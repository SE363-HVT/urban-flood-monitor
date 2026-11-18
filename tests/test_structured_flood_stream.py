import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from kafka.structs import OffsetAndMetadata, TopicPartition

from bigdata.lakehouse.delta_reports import record_row
from bigdata.streaming.structured_flood_stream import StructuredFloodStream, legacy_starting_offsets


class StructuredFloodTests(unittest.TestCase):
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
