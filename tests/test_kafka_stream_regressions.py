import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from bigdata.streaming import spark_flood_processor as streaming


class KafkaStreamRegressionTests(unittest.TestCase):
    def setUp(self):
        self.processor = streaming.SparkFloodProcessor.__new__(streaming.SparkFloodProcessor)
        self.processor.mode = "live"
        self.processor.spark = Mock()
        self.processor.process_micro_batch = Mock()
        self.processor._fallback_process_records = Mock()
        self.processor.send_dlq = Mock()

    def message(self, partition, offset, value):
        if isinstance(value, dict):
            value = json.dumps(value).encode("utf-8")
        return SimpleNamespace(topic="social.live.raw", partition=partition, offset=offset, value=value)

    def run_stream(self, *poll_results):
        consumer = Mock()
        consumer.poll.side_effect = [*poll_results, KeyboardInterrupt()]
        with patch.object(streaming, "KAFKA_AVAILABLE", True), patch.object(streaming, "KafkaConsumer", return_value=consumer):
            self.processor.start_kafka_streaming()
        consumer.close.assert_called_once()

    def submitted_batches(self):
        return [call.kwargs["raw_records"] for call in self.processor.process_micro_batch.call_args_list]

    def test_drains_records_from_every_partition_in_bounded_batches(self):
        records = [{"canonical_id": f"live_{i}"} for i in range(34)]
        self.run_stream({
            0: [self.message(0, i, record) for i, record in enumerate(records[:17])],
            1: [self.message(1, i, record) for i, record in enumerate(records[17:])],
        })
        self.assertEqual(self.submitted_batches(), [records[:15], records[15:30], records[30:]])

    def test_quarantines_invalid_payloads_and_keeps_valid_live_records(self):
        first = {"canonical_id": "live_1", "text": "Đường Nguyễn Hữu Cảnh bị ngập"}
        second = {"canonical_id": "live_2"}
        self.run_stream({0: [
            self.message(0, 0, first),
            self.message(0, 1, b"{"),
            self.message(0, 2, b"\xff"),
            self.message(0, 3, b"[]"),
            self.message(0, 4, None),
            self.message(0, 5, {"platform": "simulation"}),
            self.message(0, 6, {"canonical_id": "sim_1"}),
            self.message(0, 7, second),
        ]})
        self.assertEqual(self.submitted_batches(), [[first, second]])
        errors = self.processor.send_dlq.call_args_list
        self.assertEqual([call.args[0] for call in errors], ["KafkaPayloadError"] * 4)
        self.assertEqual([call.args[2]["offset"] for call in errors], [1, 2, 3, 4])
        self.assertEqual(errors[1].args[2], {
            "topic": "social.live.raw", "partition": 0, "offset": 2, "value": "\\xff",
        })

    def test_falls_back_on_spark_error_and_processes_next_batch(self):
        first = [{"canonical_id": f"live_{i}"} for i in range(15)]
        second = {"canonical_id": "live_next"}
        self.processor.spark.createDataFrame.side_effect = [RuntimeError("Spark error"), Mock()]
        self.run_stream({0: [self.message(0, i, record) for i, record in enumerate([*first, second])]})
        self.processor._fallback_process_records.assert_called_once_with(first, batch_id=1)
        self.assertEqual(self.submitted_batches(), [[second]])
        self.assertEqual(self.processor.process_micro_batch.call_args.kwargs["batch_id"], 2)
