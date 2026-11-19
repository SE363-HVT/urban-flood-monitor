"""Run an isolated Kafka → Spark → Delta load test on the local broker."""

import argparse
import json
import math
import os
import statistics
import sys
import tempfile
import time
from bisect import bisect_left
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from threading import Event, Thread
from unittest.mock import patch
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from pyspark.sql import functions as F

from bigdata.streaming import spark_flood_processor as processing
from bigdata.streaming.hourly_report_counts import HourlyReportCounts
from bigdata.streaming.structured_flood_stream import StructuredFloodStream


def checkpoint_latencies(progress, sent, topic):
    offsets = defaultdict(list)
    completed_at = defaultdict(list)
    for batch in sorted(progress.values(), key=lambda item: item["batchId"]):
        end_offset = batch["sources"][0]["endOffset"]
        if isinstance(end_offset, str):
            end_offset = json.loads(end_offset)
        completed = datetime.fromisoformat(batch["timestamp"]).timestamp() + batch["batchDuration"] / 1000
        for partition, position in end_offset[topic].items():
            offsets[int(partition)].append(position)
            completed_at[int(partition)].append(completed)
    return sorted(
        completed_at[partition][bisect_left(offsets[partition], offset + 1)] - created
        for created, partition, offset in sent
    )


def benchmark(seconds, rate, burst, bootstrap, *, with_history=False):
    run_id = uuid4().hex
    topic = f"se363-load-{run_id}"
    report_prefix = f"sim_load_{run_id}_"
    existing_delta = ROOT / "data" / "lakehouse" / "delta" / "verified_reports" / "simulation"
    expected = int(seconds * rate) + burst
    sent = []
    errors = []
    stop = Event()

    def publish():
        try:
            with KafkaProducer(bootstrap_servers=bootstrap, acks="all") as producer:
                started = time.monotonic()
                for number in range(expected):
                    if number < expected - burst:
                        deadline = started + number / rate
                        if stop.wait(max(0, deadline - time.monotonic())):
                            break
                    elif stop.is_set():
                        break
                    now = datetime.now(timezone.utc)
                    report = {
                        "id": str(number), "canonical_id": f"{report_prefix}{number}", "platform": "simulation",
                        "create_time": int(now.timestamp()), "ingested_at_iso": now.isoformat(),
                        "text": "TP.HCM ngập nhiều nơi, cảnh báo giao thông.",
                    }
                    receipt = producer.send(topic, partition=number % 3, value=json.dumps(report).encode()).get(timeout=10)
                    sent.append((now.timestamp(), receipt.partition, receipt.offset))
        except Exception as error:
            errors.append(error)

    with KafkaAdminClient(bootstrap_servers=bootstrap, request_timeout_ms=10000) as admin:
        admin.create_topics([NewTopic(topic, 3, 1)])
        try:
            with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"SE363_SPARK_MASTER": "local[4]"}):
                root = Path(directory)
                history = root / "lakehouse" / "flood_events"
                with (
                    patch.object(processing, "DATA_DIR", str(root)),
                    patch.object(processing, "LAKEHOUSE_DIR", str(history)),
                    patch.object(processing, "STREAM_STATE_FILE", str(root / "state.json")),
                    patch.object(processing, "DLQ_FILE", str(root / "dlq.jsonl")),
                    patch.object(StructuredFloodStream, "_init_redis", return_value=None),
                    patch.object(StructuredFloodStream, "_init_dlq_producer", return_value=None),
                    patch("pipeline.veracity_checker.urllib.request.urlopen", side_effect=TimeoutError("load fixture")),
                ):
                    worker = StructuredFloodStream(mode="simulation")
                    worker.spark.sparkContext.setLogLevel("ERROR")
                    publisher = Thread(target=publish)
                    query = hourly = None
                    try:
                        seeded = 0
                        if with_history:
                            history_frame = worker.spark.read.format("delta").load(existing_delta.as_uri())
                            history_frame.write.format("delta").save(worker.delta_path.as_uri())
                            seeded = worker.spark.read.format("delta").load(worker.delta_path.as_uri()).count()
                        rollup = HourlyReportCounts(worker.spark, worker.delta_path, root / "hourly", root / "hourly-checkpoint")
                        rollup.prepare()
                        query = worker.start_query(bootstrap, [topic], topic)
                        publisher.start()
                        seen, progress, paths = {}, {}, set()
                        deadline = time.monotonic() + seconds + 180
                        while time.monotonic() < deadline:
                            if errors:
                                raise errors[0]
                            if not query.isActive:
                                raise RuntimeError(f"Kafka query stopped: {query.exception()}")
                            if hourly is not None and not hourly.isActive:
                                raise RuntimeError(f"Hourly query stopped: {hourly.exception()}")
                            for path in history.glob("*/*/report-*.jsonl"):
                                if path not in paths:
                                    record = json.loads(path.read_text(encoding="utf-8"))
                                    seen[int(record["id"])] = path.stat().st_mtime
                                    paths.add(path)
                            for batch in query.recentProgress:
                                if batch["numInputRows"]:
                                    progress[batch["batchId"]] = batch
                            if hourly is None and progress:
                                hourly = rollup.start()
                            checkpointed = sum(batch["numInputRows"] for batch in progress.values())
                            if len(sent) == len(seen) == expected and checkpointed == expected:
                                break
                            time.sleep(1)
                        if len(sent) != expected or len(seen) != expected or checkpointed != expected:
                            raise TimeoutError(f"sent={len(sent)}, saved={len(seen)}, checkpointed={checkpointed}, expected={expected}")
                        drain_seconds = time.time() - sent[-1][0]
                        reports = worker.spark.read.format("delta").load(worker.delta_path.resolve().as_uri())
                        totals = (reports.where(F.col("canonical_id").startswith(report_prefix))
                                  .agg(F.count("*"), F.countDistinct("canonical_id"), F.countDistinct("report_version"))
                                  .first())
                        if list(totals) != [expected] * 3:
                            raise AssertionError(f"Missing or duplicate Delta reports: {totals}")
                        jsonl_delays = sorted(seen[number] - receipt[0] for number, receipt in enumerate(sent))
                        checkpoint_delays = checkpoint_latencies(progress, sent, topic)
                        p95 = math.ceil(expected * 0.95) - 1
                        return {
                            "seconds": seconds, "offered_rows_per_second": rate, "burst": burst, "partitions": 3,
                            "delta_rows": expected, "seeded_history_rows": seeded, "batches": len(progress),
                            "jsonl_delay_p95_seconds": round(jsonl_delays[p95], 2),
                            "checkpoint_delay_p95_seconds": round(checkpoint_delays[p95], 2),
                            "checkpoint_drain_seconds": round(drain_seconds, 2),
                            "median_batch_ms": round(statistics.median(batch["batchDuration"] for batch in progress.values())),
                        }
                    finally:
                        stop.set()
                        if publisher.ident is not None:
                            publisher.join(timeout=15)
                        for active in (hourly, query):
                            if active is not None and active.isActive:
                                active.stop()
                        worker.stop()
        finally:
            admin.delete_topics([topic])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=180)
    parser.add_argument("--rate", type=float, default=5)
    parser.add_argument("--burst", type=int, default=30)
    parser.add_argument("--bootstrap", default="localhost:9092")
    parser.add_argument("--with-history", action="store_true",
                        help="Copy the current simulation Delta snapshot into the isolated test table")
    args = parser.parse_args()
    if args.seconds <= 0 or not math.isfinite(args.rate) or args.rate <= 0 or args.burst < 0 or int(args.seconds * args.rate) < 1:
        parser.error("The load must contain at least one report and use a positive duration and rate.")
    print(json.dumps(benchmark(
        args.seconds, args.rate, args.burst, args.bootstrap, with_history=args.with_history
    ), indent=2))
