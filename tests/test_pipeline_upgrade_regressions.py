import io
import json
import os
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

from bigdata.lakehouse import compaction_job
from bigdata.producers import social_producer
from bigdata.streaming.stream_storage import crawler_heartbeat_path, write_json_atomic
from core import gazetteer
from dashboard import server
from pipeline.event_processor import report_url
from pipeline.spatio_temporal_clusterer import SpatioTemporalClusterer
from pipeline.veracity_checker import VeracityChecker


class WeatherTests(unittest.TestCase):
    def test_live_cache_shares_one_request_and_keeps_dry_and_tidal_distinct(self):
        checker = VeracityChecker()
        timestamp = int(datetime(2026, 11, 18, 12, tzinfo=timezone.utc).timestamp())
        series = {"hourly": {"time": ["2026-11-18T19:00"], "precipitation": [0], "rain": [None]}}

        def response(*args, **kwargs):
            time.sleep(0.05)
            return io.BytesIO(json.dumps(series).encode())

        with (
            patch("pipeline.veracity_checker.time.time", return_value=timestamp),
            patch("pipeline.veracity_checker.urllib.request.urlopen", side_effect=response) as get,
        ):
            with ThreadPoolExecutor(max_workers=4) as pool:
                results = list(pool.map(lambda tidal: checker.check_weather_plausibility(
                    10.78, 106.70, timestamp, is_tidal=tidal
                ), [False, True, False, True]))
            missing = checker.check_weather_plausibility(10.78, 106.70, timestamp - 3600)
        get.assert_called_once()
        self.assertEqual([result["score"] for result in results], [0.50, 0.90, 0.50, 0.90])
        self.assertTrue(all(result["checked"] and result["precipitation_mm"] == 0 for result in results))
        self.assertFalse(missing["checked"])
        self.assertIsNone(missing["precipitation_mm"])

    def test_archive_requests_the_local_date_after_midnight(self):
        checker = VeracityChecker()
        timestamp = int(datetime(2024, 11, 17, 18, tzinfo=timezone.utc).timestamp())
        payload = {"hourly": {"time": ["2024-11-18T01:00"], "precipitation": [8.5]}}
        with patch("pipeline.veracity_checker.urllib.request.urlopen",
                   return_value=io.BytesIO(json.dumps(payload).encode())) as get:
            result = checker.check_weather_plausibility(10.78, 106.70, timestamp)
        self.assertIn("start_date=2024-11-18&end_date=2024-11-18", get.call_args.args[0].full_url)
        self.assertEqual(result["source"], "open_meteo_archive")
        self.assertEqual(result["precipitation_mm"], 8.5)

    def test_unavailable_weather_and_ai_are_explicit_in_veracity(self):
        checker = VeracityChecker()
        now = int(time.time())
        with patch("pipeline.veracity_checker.urllib.request.urlopen", side_effect=TimeoutError) as get:
            for identity in ("a", "b", "c"):
                event = checker.verify_event({
                    "id": identity, "text": "Ngập nhiều nơi", "create_time": now,
                    "location": {"lat": 10.78, "lon": 106.70, "precision": "city"},
                })
        self.assertEqual(get.call_count, 4)
        self.assertEqual(event["veracity"]["evidence_count"], 1)
        self.assertEqual(event["veracity"]["content_check"]["fallback_reason"], "timeout")
        self.assertFalse(event["veracity"]["weather_check"]["checked"])


class IncidentTests(unittest.TestCase):
    def test_url_dedup_keeps_resource_ids(self):
        self.assertEqual(report_url("https://youtube.com/watch?v=a&utm_source=ref"), "https://youtube.com/watch?v=a")
        self.assertNotEqual(report_url("https://youtube.com/watch?v=a"), report_url("https://youtube.com/watch?v=b"))

    def test_cluster_keeps_history_and_separates_nearby_roads_and_city_reports(self):
        location = {"lat": 10.8, "lon": 106.7, "street": "Nguyễn Hữu Cảnh", "precision": "street"}
        first = {"id": "first", "create_time": 1000, "text": "Đường đang ngập", "location": location}
        recovery = {**first, "id": "recovery", "create_time": 1200, "text": "Nước đã rút"}
        unrelated = {**first, "id": "other", "location": {**location, "street": "Điện Biên Phủ"}}
        city = {**first, "id": "city", "location": {**location, "street": "", "precision": "city"}}
        forecast = {**first, "id": "forecast", "text": "Dự báo đường có thể ngập"}
        reprint = {**first, "id": "reprint", "url": "https://example.org/story?utm_source=copy"}
        first["url"] = "https://example.org/story"
        reports = [first, recovery, unrelated, city, forecast, reprint]
        clusterer = SpatioTemporalClusterer()
        clusters = clusterer.cluster_events(reports)
        self.assertEqual(clusters, clusterer.cluster_events(list(reversed(reports))))
        self.assertEqual(len(clusters), 4)
        incident = next(item for item in clusters if item["id"] == "first")
        self.assertEqual(incident["incident_status"], "receded")
        self.assertEqual(incident["report_ids"], ["first", "recovery"])

    def test_context_selects_the_correct_coordinates_for_duplicate_street_name(self):
        wards = [{
            "keywords": [gazetteer.normalize_text("Phường Xanh")], "ward": "Phường Xanh", "lat": 10.79, "lon": 106.7,
        }]
        streets = [
            {"keywords": [gazetteer.normalize_text("Đường A")], "street": "Đường A", "ward": "Phường Đỏ", "lat": 10.8, "lon": 106.7},
            {"keywords": [gazetteer.normalize_text("Đường A")], "street": "Đường A", "ward": "Phường Xanh", "lat": 10.9, "lon": 106.7},
        ]
        with (
            patch.dict(os.environ, {"RADINET_OSM_ROAD_INDEX": ""}),
            patch.object(gazetteer, "ADMIN_HOTSPOTS", wards),
            patch.object(gazetteer, "STREET_HOTSPOTS", streets),
            patch.object(gazetteer, "CSGT_HOTSPOTS", []),
            patch.object(gazetteer, "_finalize_match", side_effect=lambda item: item),
        ):
            matched = gazetteer.match_hotspot("Đường A, Phường Xanh, TP.HCM, đang bị ngập.")
            multiple = gazetteer.match_all_hotspots("Đường A, Phường Xanh, TP.HCM, đang bị ngập.")
            with patch.object(gazetteer, "STREET_HOTSPOTS", streets[:1]):
                fallback = gazetteer.match_hotspot("Đường A, Phường Xanh, TP.HCM, đang bị ngập.")
        self.assertEqual((matched["lat"], matched["precision"]), (10.9, "street"))
        self.assertEqual([(match["lat"], match["precision"]) for match in multiple], [(10.9, "street")])
        self.assertEqual((fallback["lat"], fallback["precision"], fallback["resolution_reason"]),
                         (10.79, "ward", "road_unverified"))


class ProducerAndServingTests(unittest.TestCase):
    def test_ack_or_durable_spool_precedes_deduplication(self):
        producer = social_producer.SocialKafkaProducer.__new__(social_producer.SocialKafkaProducer)
        producer.producer = Mock()
        future = producer.producer.send.return_value
        producer.seen_canonical_ids = set()
        producer.buffered_count = 0
        first = {"id": "first", "canonical_id": "first", "text": "Ngập ở đường chính"}
        second = {**first, "id": "second", "canonical_id": "second"}
        self.assertTrue(producer.publish_event("test.raw", first))
        future.get.assert_called_once_with(timeout=5)
        future.get.side_effect = TimeoutError
        with tempfile.TemporaryDirectory() as folder, patch.object(social_producer, "ROOT_DIR", folder):
            self.assertFalse(producer.publish_event("test.raw", second))
            spool = list(Path(folder).glob("data/lakehouse/_ingress_spool/test.raw/*.jsonl"))
            self.assertEqual(len(spool), 1)
            self.assertEqual(json.loads(spool[0].read_text(encoding="utf-8"))["canonical_id"], "second")
        self.assertEqual(producer.seen_canonical_ids, {"first", "second"})
        self.assertEqual(producer.buffered_count, 1)

    def test_summary_and_map_share_fallback_snapshot_and_heartbeat_expires(self):
        with (
            tempfile.TemporaryDirectory() as folder,
            patch.object(server, "ROOT_DIR", folder),
            patch.object(server, "_SNAPSHOT", None),
            patch.object(server, "get_redis_client", return_value=None),
            patch.dict(server.GLOBAL_STATE, {"mode": "live"}),
        ):
            state_file = Path(folder) / "data" / "live_stream_state.json"
            snapshot = {"mode": "live", "window": "120 phút", "updated_at": "2026-11-18T01:00:00+00:00",
                        "events": [{"id": "source"}]}
            write_json_atomic(state_file, snapshot)
            state = server.get_serving_snapshot()
            write_json_atomic(state_file, {**snapshot, "events": []})
            summary = server.compute_dashboard_summary()
            self.assertEqual(summary["events_count"], len(state["events"]))
            self.assertEqual(summary["snapshot_updated_at"], state["updated_at"])
            pulse = crawler_heartbeat_path(Path(folder) / "data", "live")
            write_json_atomic(pulse, {"status": "ONLINE", "expires_at": time.time() - 1, "phase": "idle"})
            self.assertEqual(server._probe_crawler_health("live")["status"], "STANDBY")


class CompactionTests(unittest.TestCase):
    def test_legacy_partial_line_and_bad_report_do_not_hide_valid_reports(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            base = root / "flood_events"
            partition = base / "episode_id=0" / "date=2026-11-18"
            partition.mkdir(parents=True)
            (partition / "events_bronze.jsonl").write_bytes(b'{"id":"legacy"}\n{"unfinished"')
            (partition / "report-live-test.jsonl").write_bytes(b'bad\n{"id":"new"}\n')
            parquet = root / "silver_parquet_lakehouse"
            with patch.object(compaction_job, "TARGET_PARQUET_DIR", str(parquet)):
                compaction_job.compact_standalone(str(base))
            output = next(root.glob("silver_jsonl_lakehouse/*/*/consolidated_events.jsonl"))
            ids = {json.loads(line)["id"] for line in output.read_text(encoding="utf-8").splitlines()}
            self.assertEqual(ids, {"legacy", "new"})
            self.assertFalse(parquet.exists())
            self.assertEqual(len(list(root.glob("compaction_quarantine/*/*/invalid_records.jsonl"))), 1)
