"""Exercise crash/replay and dashboard fallback using disposable Kafka and Redis state."""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from socketserver import ThreadingTCPServer
from threading import Thread
from unittest.mock import patch
from urllib.request import urlopen
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import redis
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic


def wait_for(description, check, timeout=120):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if result := check():
            return result
        time.sleep(0.5)
    raise TimeoutError(description)


def worker(root, topic, bootstrap, phase):
    from bigdata.lakehouse.delta_reports import DeltaReportHistory
    from bigdata.streaming import spark_flood_processor as processing
    from bigdata.streaming.structured_flood_stream import StructuredFloodStream

    processing.DATA_DIR = str(root / "data")
    processing.LAKEHOUSE_DIR = str(root / "data" / "lakehouse" / "flood_events")
    processing.STREAM_STATE_FILE = str(root / "data" / "live_stream_state.json")
    processing.DLQ_FILE = str(root / "data" / "dlq.jsonl")
    with (
        patch.object(StructuredFloodStream, "_init_dlq_producer", return_value=None),
        patch("pipeline.veracity_checker.urllib.request.urlopen", side_effect=TimeoutError("recovery fixture")),
    ):
        stream = StructuredFloodStream(mode="live")
        gateway = stream.spark.sparkContext._gateway.proc
        if gateway is not None:
            (root / f"{phase}.gateway").write_text(str(gateway.pid))
        stream.spark.sparkContext.setLogLevel("ERROR")
        if phase == "before-delta":
            # The override runs immediately after the real normalized JSONL write.
            def before_delta(*args):
                os._exit(71)

            DeltaReportHistory.write = before_delta
        elif phase == "before-file":
            original = processing.write_json_atomic

            def before_file(path, *args, **kwargs):
                if str(path) == processing.STREAM_STATE_FILE:
                    os._exit(72)
                return original(path, *args, **kwargs)

            processing.write_json_atomic = before_file

        query = stream.start_query(bootstrap, [topic], topic)
        try:
            while not query.awaitTermination(1):
                with stream.processing_lock:
                    stream._recover_hot_snapshot()
                    if (root / "finish").exists():
                        rows = stream.spark.read.format("delta").load(stream.delta_path.as_uri()).select(
                            "canonical_id", "report_version"
                        ).collect()
                        (root / "delta-rows.json").write_text(json.dumps([row.asDict() for row in rows]))
                        return
        finally:
            query.stop()
            stream.spark.stop()


def check_recovery(root, bootstrap, redis_port, redis_container):
    from dashboard import server as dashboard

    published_port = subprocess.check_output(
        ["docker", "port", redis_container, "6379/tcp"], text=True
    ).strip()
    if published_port != f"127.0.0.1:{redis_port}":
        raise RuntimeError("Disposable Redis must publish its configured port on 127.0.0.1")
    topic = "se363-recovery-" + uuid4().hex
    client = redis.Redis(host="127.0.0.1", port=redis_port, decode_responses=True,
                         socket_connect_timeout=0.2, socket_timeout=0.2)
    if client.dbsize():
        raise RuntimeError("Recovery requires an empty disposable Redis instance")
    (root / "data").mkdir()
    stamp = int(time.time()) - 60
    fixtures = [
        {"id": str(i), "canonical_id": f"recovery-{i}", "platform": platform, "create_time": stamp + i,
         "text": message, "ingested_at_iso": datetime.now(timezone.utc).isoformat(),
         "location": {"street": "Nguyễn Hữu Cảnh", "ward": "Phường Thạnh Mỹ Tây",
                      "lat": 10.793, "lon": 106.719, "precision": "street"}}
        for i, (platform, message) in enumerate((
            ("youtube", "Đường Nguyễn Hữu Cảnh TP.HCM ngập sâu, xe chết máy."),
            ("facebook", "Nước ngập tràn đường Nguyễn Hữu Cảnh ở TP.HCM, xe phải dắt bộ."),
            ("citizen_report", "Mưa lớn làm ngập đường Nguyễn Hữu Cảnh, TP.HCM, nước dâng qua bánh xe."),
        ), start=1)
    ]
    checkpoints = root / "data" / "lakehouse" / "_checkpoints" / "structured_flood" / "live" / "query"
    cold = root / "data" / "lakehouse" / "flood_events"
    delta = cold.parent / "delta" / "verified_reports" / "live"

    def start(phase):
        log = root / f"{phase}.log"
        env = dict(os.environ, REDIS_PORT=str(redis_port), REDIS_HOST="127.0.0.1",
                   SE363_SPARK_MASTER="local[4]", PYTHONIOENCODING="utf-8")
        with log.open("w", encoding="utf-8") as out:
            child = subprocess.Popen([sys.executable, "-u", __file__, str(root), topic, bootstrap, phase],
                                     cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT)
        return child, log

    def check_exit(child, log, expected):
        if child.wait(timeout=150) != expected:
            raise RuntimeError(log.read_text(encoding="utf-8", errors="replace"))

    def cleanup_worker(child, phase):
        gateway = root / f"{phase}.gateway"
        if os.name == "nt" and gateway.exists():
            subprocess.run(["taskkill", "/PID", gateway.read_text(), "/T", "/F"], capture_output=True)
        if child.poll() is None:
            child.kill()
            child.wait(timeout=15)

    def commits():
        return {int(p.name) for p in (checkpoints / "commits").glob("*") if p.name.isdecimal()}

    class Handler(dashboard.HeatmapRequestHandler):
        def log_message(self, *args):
            pass

    with KafkaAdminClient(bootstrap_servers=bootstrap, request_timeout_ms=10000) as admin:
        admin.create_topics([NewTopic(topic, 2, 1)])
        try:
            with KafkaProducer(bootstrap_servers=bootstrap, acks="all") as producer:
                def send(record, partition):
                    producer.send(topic, partition=partition, value=json.dumps(record).encode()).get(timeout=15)

                send(fixtures[0], 0)
                for phase, expected in (("before-delta", 71), ("before-file", 72)):
                    child, log = start(phase)
                    try:
                        check_exit(child, log, expected)
                        assert len(list(cold.rglob("report-*.jsonl"))) == 1
                        assert not commits(), "Kafka checkpoint advanced during interrupted batch"
                        if phase == "before-delta":
                            assert not (delta / "_delta_log").exists()
                            assert client.zcard("flood:timeline:zset") == 0
                        else:
                            assert list((delta / "_delta_log").glob("*.json"))
                            assert client.zcard("flood:timeline:zset") == 1
                        print(f"{phase}: interrupted at expected sink, checkpoint uncommitted", flush=True)
                    finally:
                        cleanup_worker(child, phase)

                child, log = start("recover")
                try:
                    with (
                        patch.object(dashboard, "ROOT_DIR", str(root)),
                        patch.object(dashboard, "REDIS_HOST", "127.0.0.1"),
                        patch.object(dashboard, "REDIS_PORT", redis_port),
                        patch.dict(dashboard.GLOBAL_STATE, {"mode": "live", "events": []}),
                        ThreadingTCPServer(("127.0.0.1", 0), Handler) as server,
                    ):
                        thread = Thread(target=server.serve_forever, daemon=True)
                        thread.start()
                        base = f"http://127.0.0.1:{server.server_address[1]}"

                        def check_dashboard(source, count):
                            if child.poll() is not None:
                                raise RuntimeError(log.read_text(encoding="utf-8", errors="replace"))
                            with urlopen(base + "/api/realtime-heatmap", timeout=5) as response:
                                payload = json.load(response)
                            if payload["served_from"] != source or len(payload["events"]) != 1:
                                return None
                            incident = payload["events"][0]
                            expected_ids = {item["canonical_id"] for item in fixtures[:count]}
                            if (set(incident["report_ids"]) == expected_ids and
                                    incident["report_count"] == len(expected_ids) and
                                    incident["location"]["street"] == "Nguyễn Hữu Cảnh"):
                                return incident
                            return None

                        try:
                            wait_for("Original report did not recover through Redis", lambda: commits() and check_dashboard("redis", 1))
                            send(fixtures[0], 1)
                            send(fixtures[1], 1)
                            wait_for("Replay or second partition did not reach dashboard", lambda: check_dashboard("redis", 2))
                            print("Restart/replay: Redis heatmap serves exactly 2 unique report IDs", flush=True)

                            subprocess.run(["docker", "stop", redis_container], check=True, capture_output=True)
                            try:
                                send(fixtures[2], 0)
                                wait_for("Dashboard file fallback missing the third report",
                                         lambda: check_dashboard("local_file_buffer", 3))
                                print("Redis unavailable: dashboard serves 3 reports from file", flush=True)
                            finally:
                                subprocess.run(["docker", "start", redis_container], check=True, capture_output=True)
                            wait_for("Redis did not recover without a fresh report", lambda: check_dashboard("redis", 3))
                            print("Redis restarted: dashboard serves the same 3 reports from Redis", flush=True)
                            (root / "finish").touch()
                            check_exit(child, log, 0)
                        finally:
                            server.shutdown()
                            thread.join(timeout=5)
                    rows = json.loads((root / "delta-rows.json").read_text())
                    assert sorted(row["canonical_id"] for row in rows) == sorted(event["canonical_id"] for event in fixtures)
                    assert len({row["report_version"] for row in rows}) == 3
                    assert len(list(cold.rglob("report-*.jsonl"))) == 3
                    assert len(list((cold.parent / "raw_reports").rglob("*.jsonl"))) == 3
                    print("Verified: 3 unique reports in raw JSONL, normalized JSONL, Delta and heatmap.", flush=True)
                finally:
                    cleanup_worker(child, "recover")
        finally:
            admin.delete_topics([topic])


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[4] in {"before-delta", "before-file", "recover"}:
        worker(Path(sys.argv[1]), *sys.argv[2:])
    else:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--bootstrap", default="localhost:9092")
        parser.add_argument("--redis-container", required=True, help="Dedicated disposable Docker container")
        parser.add_argument("--redis-port", type=int, required=True)
        args = parser.parse_args()
        if args.redis_port == 6379 or args.redis_container == "se363-redis-serving":
            parser.error("Use an isolated Redis container and a non-production port")
        with tempfile.TemporaryDirectory(prefix="se363-recovery-") as directory:
            check_recovery(Path(directory), args.bootstrap, args.redis_port, args.redis_container)
