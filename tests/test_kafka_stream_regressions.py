import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from bigdata.streaming import spark_flood_processor as streaming
from bigdata.streaming.stream_storage import spool_record


class KafkaStreamRegressionTests(unittest.TestCase):
    def setUp(self):
        data = self.enterContext(tempfile.TemporaryDirectory())
        self.enterContext(patch.object(streaming, "DATA_DIR", data))
        self.enterContext(patch.object(streaming, "LAKEHOUSE_DIR", str(Path(data) / "lakehouse" / "flood_events")))
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
        return consumer

    def submitted_batches(self):
        return [call.kwargs["raw_records"] for call in self.processor.process_micro_batch.call_args_list]

    def test_drains_records_from_every_partition_in_bounded_batches(self):
        records = [{"canonical_id": f"live_{i}"} for i in range(34)]
        consumer = self.run_stream({
            0: [self.message(0, i, record) for i, record in enumerate(records[:17])],
            1: [self.message(1, i, record) for i, record in enumerate(records[17:])],
        })
        self.assertEqual(self.submitted_batches(), [records[:15], records[15:30], records[30:]])
        self.assertEqual({p: offset.offset for p, offset in consumer.commit.call_args.args[0].items()},
                         {0: 17, 1: 17})

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

    def test_avoids_commit_if_durable_storage_fails(self):
        consumer = Mock()
        consumer.poll.return_value = {0: [self.message(0, 13, {"canonical_id": "live_1"})]}
        self.processor.process_micro_batch.side_effect = OSError("disk unavailable")
        with patch.object(streaming, "KAFKA_AVAILABLE", True), patch.object(streaming, "KafkaConsumer", return_value=consumer):
            with self.assertRaisesRegex(OSError, "disk unavailable"):
                self.processor.start_kafka_streaming()
        consumer.commit.assert_not_called()
        consumer.close.assert_called_once()

    def test_keeps_spool_file_on_processing_failure_then_retries(self):
        topic = "social.live.raw"
        record = {"canonical_id": "live_buffered"}
        spool_record(streaming.DATA_DIR, topic, record)
        folder = Path(streaming.DATA_DIR) / "lakehouse" / "_ingress_spool" / topic
        self.processor.process_micro_batch.side_effect = OSError("disk unavailable")
        with self.assertRaises(OSError):
            self.processor._drain_buffer([topic], 0, 15)
        self.assertEqual(len(list(folder.glob("*.jsonl"))), 1)
        self.processor.process_micro_batch.side_effect = None
        self.assertEqual(self.processor._drain_buffer([topic], 0, 15), 1)
        self.assertEqual(list(folder.glob("*.jsonl")), [])
        self.assertEqual(self.submitted_batches(), [[record], [record]])

    def test_reuses_durable_normalized_report_on_replay(self):
        record = {"canonical_id": "live_saved", "create_time": int(streaming.time.time())}
        saved = {**record, "report_version": self.processor._fingerprint(record)}
        self.processor._append_cold_lakehouse([saved])
        with patch.object(self.processor, "_publish_verified_batch") as publish:
            self.processor._process_ingress_batch([record], batch_id=2)
        self.processor.spark.createDataFrame.assert_not_called()
        publish.assert_called_once_with([saved], 2)
