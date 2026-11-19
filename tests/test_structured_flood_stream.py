import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from threading import Lock

from kafka.structs import OffsetAndMetadata, TopicPartition

from bigdata.lakehouse.delta_reports import record_row
from bigdata.streaming.structured_flood_stream import StructuredFloodStream, legacy_starting_offsets


class StructuredFloodTests(unittest.TestCase):
    def test_hourly_failure_is_reported_without_stopping_ingestion(self):
        with tempfile.TemporaryDirectory() as folder:
            lakehouse = Path(folder)
            stream = StructuredFloodStream.__new__(StructuredFloodStream)
            stream.mode = "live"
            stream.delta_path = lakehouse / "delta" / "verified_reports" / "live"
            stream.checkpoint = lakehouse / "checkpoint"
            stream.processing_lock = Lock()
            stream.spark = Mock()
            ingestion = Mock(isActive=True, lastProgress={"batchId": 1})
            ingestion.awaitTermination.side_effect = [False, True]
            stream.start_query = Mock(return_value=ingestion)
            stream._drain_buffer = Mock(return_value=0)
            stream._recover_hot_snapshot = Mock()
            with patch("bigdata.streaming.structured_flood_stream.HourlyReportCounts") as rollup:
                rollup.return_value.start.side_effect = RuntimeError("unavailable analytics")
                stream.run("local:9092")
            status = json.loads(
                (lakehouse / "_operations" / "structured_live.json").read_text(encoding="utf-8")
            )
        self.assertEqual(status["hourly_status"], "failed")
        self.assertEqual(status["ingestion_batch_id"], 1)
        self.assertEqual(ingestion.awaitTermination.call_count, 2)
        ingestion.stop.assert_called_once()

    def test_operational_snapshot_reports_actual_watermark_and_late_counts(self):
        stream = StructuredFloodStream.__new__(StructuredFloodStream)
        stream.mode = "live"
        ingestion = Mock(lastProgress={"batchId": 11, "batchDuration": 1000})
        hourly = Mock(isActive=True, lastProgress={
            "eventTime": {"watermark": "2026-11-18T00:00:00Z"},
            "stateOperators": [{"numRowsDroppedByWatermark": 2, "numRowsTotal": 5}],
        })
        with tempfile.TemporaryDirectory() as folder:
            stream._write_stream_progress(ingestion, hourly, Path(folder), None)
            state_file = Path(folder) / "_operations" / "structured_live.json"
            state = json.loads(state_file.read_text(encoding="utf-8"))
        self.assertEqual(state["hourly_status"], "active")
        self.assertEqual(state["hourly_watermark"], "2026-11-18T00:00:00Z")
        self.assertEqual(state["hourly_rows_dropped_last_batch"], 2)
        self.assertEqual(state["hourly_state_rows"], 5)

    def test_cutover_uses_next_committed_offset_and_earliest_for_new_partitions(self):
        admin = Mock()
        admin.describe_topics.return_value = [{
            "name": "test.raw", "error_code": 0,
            "partitions": [{"partition_index": index, "error_code": 0} for index in (0, 1)],
        }]
        admin.list_group_offsets.return_value = {
            "old": {TopicPartition("test.raw", 0): OffsetAndMetadata(18, "")},
        }
        with patch("bigdata.streaming.structured_flood_stream.KafkaAdminClient") as client:
            client.return_value.__enter__.return_value = admin
            offsets = legacy_starting_offsets("localhost:9092", ["test.raw"], "old")
        self.assertEqual(offsets, {"test.raw": {"0": 18, "1": -2}})

    def test_bootstrap_plan_is_reused_after_a_restart(self):
        with tempfile.TemporaryDirectory() as temporary:
            stream = StructuredFloodStream.__new__(StructuredFloodStream)
            stream.checkpoint = Path(temporary)
            saved = {"test.raw": {"0": 18}}
            with patch("bigdata.streaming.structured_flood_stream.legacy_starting_offsets", return_value=saved) as fetch:
                self.assertEqual(stream._get_starting_offsets("local:9092", ["test.raw"], "old"), saved)
                self.assertEqual(stream._get_starting_offsets("local:9092", ["test.raw"], "old"), saved)
                with self.assertRaises(ValueError):
                    stream._get_starting_offsets("different:9092", ["test.raw"], "old")
            fetch.assert_called_once()

    def test_delta_preserves_astespans_and_distinguishes_dry_from_missing_rain(self):
        report = {
            "report_version": "v1",
            "canonical_id": "source_42",
            "create_time": 1795000000,
            "aste_triplets": [{"aspect": "Đường A", "opinion": "ngập sâu", "polarity": "NEG"}],
            "veracity": {"weather_check": {"precipitation_mm": 0}},
        }
        row = record_row(report)
        self.assertEqual(row[-2], 0.0)
        self.assertEqual(json.loads(row[-1]), report)
        self.assertIsNone(record_row({**report, "veracity": {}})[-2])
