import copy
import io
import json
import time
import unittest
from unittest.mock import patch

from dashboard import server
from pipeline.spatio_temporal_clusterer import SpatioTemporalClusterer


class DashboardMetricsTests(unittest.TestCase):
    def test_calendar_buckets_use_polarity_and_skip_invalid_times(self):
        current_hour = time.mktime((2026, 10, 12, 18, 0, 0, 0, 0, -1))
        with patch.object(server.time, "time", return_value=current_hour + 1200):
            stats = server.compute_time_series_metrics([
                {"create_time": current_hour, "polarity": "pos", "sentiment": "NEG"},
                {"create_time": current_hour - 1, "sentiment": "NeU"},
                {"timestamp": str(current_hour - 5 * 3600), "status_tag": "negative"},
                {"create_time": current_hour + 60, "aste_triplets": [{"polarity": "POS"}]},
                {"create_time": current_hour - 5 * 3600 - 1, "polarity": "NEG"},
                {"create_time": current_hour + 1201, "polarity": "NEG"},
                {"create_time": "invalid", "polarity": "NEG"},
                {"polarity": "NEG"},
            ])
        self.assertEqual(stats, {
            "hours": ["13:00", "14:00", "15:00", "16:00", "17:00", "18:00"],
            "neg": [1, 0, 0, 0, 0, 0],
            "neu": [0, 0, 0, 0, 1, 0],
            "pos": [0, 0, 0, 0, 0, 2],
        })

    def test_throughput_and_veracity_use_the_serving_snapshot(self):
        with patch.object(server.time, "time", return_value=1500):
            stats = server.compute_throughput_metrics([
                {"create_time": 1499, "veracity": {"status": "confirmed"}},
                {"create_time": 1440, "veracity": {"status": "rejected", "confidence": 0.99}},
                {"create_time": 1501},
                {"timestamp": 1450, "veracity": {"confidence": 0.71}},
            ])
        self.assertEqual(stats["current_rpm"], 2)
        self.assertEqual(stats["total_posts"], 4)
        self.assertEqual(stats["veracity_pass_rate"], 50.0)
        self.assertEqual(server.compute_throughput_metrics([])["veracity_pass_rate"], 0.0)

    def test_ai_health_distinguishes_model_ready_from_heuristic_fallback(self):
        for model, expected in (("active", "ONLINE"), ("mock_fallback", "DEGRADED")):
            payload = {"status": "healthy", "models": {"branch_1_phobert_fast": model}}
            with patch.object(server, "urlopen", return_value=io.BytesIO(json.dumps(payload).encode())) as request:
                result = server._probe_ai_health()
            self.assertEqual(result["status"], expected)
            self.assertTrue(request.call_args.args[0].endswith("/health"))
        with patch.object(server, "urlopen", side_effect=OSError):
            self.assertEqual(server._probe_ai_health()["status"], "STANDBY")


class ClusterRegressionTests(unittest.TestCase):
    def test_duplicates_do_not_inflate_counts_or_mutate_source_reports(self):
        first = {
            "canonical_id": "report-1", "create_time": 1500, "platform": "tiktok",
            "location": {"lat": 10.85, "lon": 106.75, "heat_points": [[10.85, 106.75]]},
            "veracity": {"status": "unverified", "confidence_score": 0.4},
        }
        duplicate = copy.deepcopy(first)
        second = {
            "canonical_id": "report-2", "create_time": 1510, "platform": "facebook",
            "location": {"lat": 10.851, "lon": 106.75, "heat_points": [[10.851, 106.75]]},
        }
        events = [first, duplicate, second]
        original = copy.deepcopy(events)
        clusters = SpatioTemporalClusterer().cluster_events(events)
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0]["report_count"], 2)
        self.assertEqual(len(clusters[0]["posts_summary"]), 2)
        clusters[0]["location"]["heat_points"][1][0] = 0
        self.assertEqual(events, original)


if __name__ == "__main__":
    unittest.main()
