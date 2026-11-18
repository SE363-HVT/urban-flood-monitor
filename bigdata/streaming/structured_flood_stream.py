"""Official Kafka Structured Streaming entrypoint and Delta history writer."""

import argparse
import json
import os
import subprocess
import sys
import time
from functools import lru_cache
from importlib.metadata import version
from pathlib import Path
from threading import Lock

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from kafka.admin import KafkaAdminClient
from kafka.errors import GroupIdNotFoundError, KafkaError
from kafka.structs import TopicPartition
import pyspark
from pyspark.sql import SparkSession

from bigdata.lakehouse.delta_reports import DeltaReportHistory
from bigdata.streaming import spark_flood_processor as processing
from bigdata.streaming.stream_storage import write_json_atomic


MAX_OFFSETS = 15
TOPICS = {"live": "social.live.raw", "simulation": "social.sim.raw"}


@lru_cache(maxsize=2)
def _resolve_local_jars(packages, exclusions, ivy_settings):
    spark_jars = Path(pyspark.__file__).parent / "jars" / "*"
    java_home = os.environ.get("JAVA_HOME")
    java = str(Path(java_home) / "bin" / "java.exe") if java_home else "java"
    resolver = Path(__file__).with_name("ResolveSparkPackages.java")
    result = subprocess.run(
        [java, "-classpath", str(spark_jars), str(resolver), packages, exclusions, ivy_settings],
        stdout=subprocess.PIPE, text=True, check=True, timeout=1800,
    )
    jars = [Path(line.removeprefix("jar=")).resolve() for line in result.stdout.splitlines()
            if line.startswith("jar=")]
    if not jars or any(not jar.is_file() for jar in jars):
        raise RuntimeError("Could not resolve the local Spark connectors")
    return ",".join(jar.as_uri().replace("file:", "local:", 1) for jar in jars)


def structured_builder(builder, *, kafka=True, local=False):
    from delta import configure_spark_with_delta_pip

    packages = [f"org.apache.spark:spark-sql-kafka-0-10_2.13:{pyspark.__version__}"] if kafka else []
    # PySpark already ships these. Keep one Hadoop/Parquet classpath for Spark and Delta.
    bundled = [
        "org.apache.hadoop:hadoop-client-api", "org.apache.hadoop:hadoop-client-runtime",
        "org.apache.parquet:parquet-hadoop", "org.apache.parquet:parquet-column",
        "org.apache.parquet:parquet-common", "org.apache.parquet:parquet-encoding",
        "org.apache.parquet:parquet-format-structures", "org.apache.parquet:parquet-jackson",
    ]
    exclusions = ",".join(bundled)
    settings = Path(__file__).with_name("ivysettings.xml").resolve().as_uri()
    builder.config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    builder.config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    if local and os.name == "nt":
        # Load from the Ivy cache so a Windows executor does not fetch JARs from its own driver.
        spark_minor = ".".join(pyspark.__version__.split(".")[:2])
        delta_package = f"io.delta:delta-spark_{spark_minor}_2.13:{version('delta-spark')}"
        jars = _resolve_local_jars(",".join([delta_package, *packages]), exclusions, settings)
        return builder.config("spark.jars", jars)
    builder.config("spark.jars.excludes", exclusions).config("spark.jars.ivySettings", settings)
    return configure_spark_with_delta_pip(builder, extra_packages=packages)


def legacy_starting_offsets(bootstrap_servers, topics, group_id):
    with KafkaAdminClient(bootstrap_servers=bootstrap_servers, request_timeout_ms=5000) as admin:
        metadata = admin.describe_topics(list(topics))
        try:
            committed = admin.list_group_offsets(group_id).get(group_id, {})
        except GroupIdNotFoundError:
            committed = {}
    offsets = {}
    for topic in metadata:
        if topic["error_code"] or not topic["partitions"]:
            raise KafkaError(f"Kafka metadata unavailable for {topic['name']}: {topic['error_code']}")
        partitions = {}
        for partition in topic["partitions"]:
            index = partition["partition_index"]
            if partition["error_code"]:
                raise KafkaError(f"Kafka metadata unavailable for {topic['name']} partition {index}")
            old = committed.get(TopicPartition(topic["name"], index))
            partitions[str(index)] = old.offset if old is not None and old.offset >= 0 else -2
        offsets[topic["name"]] = partitions
    if set(offsets) != set(topics):
        raise KafkaError("Kafka metadata did not return every requested topic")
    return offsets


class StructuredFloodStream(processing.SparkFloodProcessor):
    def __init__(self, mode="live", *, history_only=False):
        lakehouse = Path(processing.LAKEHOUSE_DIR).parent
        self.delta_path = lakehouse / "delta" / "verified_reports" / mode
        self.checkpoint = lakehouse / "_checkpoints" / "structured_flood" / mode
        self.processing_lock = Lock()
        self.history_only = history_only
        super().__init__(mode=mode, app_name="SE363-Structured-Flood-Streaming",
                         restore_serving=not history_only)

    def _create_spark_session(self):
        master = os.environ.get("SE363_SPARK_MASTER", "local[*]")
        builder = (SparkSession.builder.appName(self.app_name)
                   .master(master)
                   .config("spark.driver.memory", "2g")
                   .config("spark.sql.shuffle.partitions", "4")
                   .config("spark.default.parallelism", "4")
                   .config("spark.sql.ui.retainedStreamingQueries", "10")
                   .config("spark.ui.showConsoleProgress", "false"))
        if master.startswith("local"):
            builder.config("spark.driver.host", "127.0.0.1").config("spark.driver.bindAddress", "127.0.0.1")
        spark = structured_builder(builder, kafka=not self.history_only, local=master.startswith("local")).getOrCreate()
        spark.sparkContext.setLogLevel("WARN")
        return spark

    def _append_cold_lakehouse(self, events):
        super()._append_cold_lakehouse(events)
        try:
            DeltaReportHistory(self.spark, self.delta_path).write(events)
        except Exception as error:
            raise OSError(f"Delta commit failed for {self.delta_path}") from error

    def backfill_history(self):
        """Import completed normalized JSONL files without changing the serving snapshot."""
        history = DeltaReportHistory(self.spark, self.delta_path)
        total = 0
        batch = []
        for path in sorted(Path(processing.LAKEHOUSE_DIR).glob("episode_id=*/date=*/*.jsonl")):
            with path.open("rb") as source:
                remaining = os.fstat(source.fileno()).st_size
                for line_number, line in enumerate(iter(lambda: source.readline(remaining), b""), start=1):
                    remaining -= len(line)
                    if not line.endswith(b"\n") and path.name == "events_bronze.jsonl":
                        break
                    if not line.strip():
                        continue
                    try:
                        event = json.loads(line)
                        if not isinstance(event, dict) or not (event.get("canonical_id") or event.get("id")):
                            raise ValueError("Expected a normalized report with an ID")
                    except ValueError as error:
                        raise ValueError(f"Invalid normalized report in {path}:{line_number}") from error
                    platform = str(event.get("platform") or "").lower()
                    canonical_id = str(event.get("canonical_id") or "")
                    mode = event.get("stream_mode") or (
                        "simulation" if platform in ("simulation", "sim") or canonical_id.startswith("sim_")
                        else "live"
                    )
                    if mode != self.mode:
                        continue
                    if not event.get("report_version"):
                        event["report_version"] = self._fingerprint(event)
                    batch.append(event)
                    total += 1
                    if len(batch) == 2000:
                        history.write(batch)
                        batch.clear()
        history.write(batch)
        return total

    def _get_starting_offsets(self, bootstrap_servers, topics, legacy_group):
        plan_path = self.checkpoint / "bootstrap.json"
        if plan_path.exists():
            with plan_path.open(encoding="utf-8") as source:
                plan = json.load(source)
            if (plan["topics"] != list(topics) or plan["legacy_group"] != legacy_group
                    or plan["bootstrap_servers"] != bootstrap_servers):
                raise ValueError(f"Checkpoint bootstrap does not match this stream: {plan_path}")
            return plan["offsets"]
        offsets = legacy_starting_offsets(bootstrap_servers, topics, legacy_group)
        write_json_atomic(plan_path, {
            "topics": list(topics), "legacy_group": legacy_group, "offsets": offsets,
            "bootstrap_servers": bootstrap_servers,
        }, durable=True)
        return offsets

    def _consume_batch(self, frame, batch_id):
        with self.processing_lock:
            records = []
            for row in frame.toLocalIterator():
                value = self._decode_ingress_record(row.value, row.topic, row.partition, row.offset)
                if value is not None:
                    records.append(value)
                    if len(records) == MAX_OFFSETS:
                        self._process_ingress_batch(records, batch_id)
                        records = []
            if records:
                self._process_ingress_batch(records, batch_id)

    def start_query(self, bootstrap_servers, topics, legacy_group, *, available_now=False):
        offsets = self._get_starting_offsets(bootstrap_servers, topics, legacy_group)
        source = (self.spark.readStream.format("kafka")
                  .option("kafka.bootstrap.servers", bootstrap_servers)
                  .option("subscribe", ",".join(topics))
                  .option("startingOffsets", json.dumps(offsets))
                  .option("maxOffsetsPerTrigger", MAX_OFFSETS)
                  .option("failOnDataLoss", "true")
                  .load())
        writer = (source.select("topic", "partition", "offset", "value").writeStream
                  .option("checkpointLocation", (self.checkpoint / "query").resolve().as_uri())
                  .foreachBatch(self._consume_batch))
        return (writer.trigger(availableNow=True) if available_now
                else writer.trigger(processingTime="1 second")).start()

    def run(self, bootstrap_servers):
        topics = [TOPICS[self.mode]]
        group = f"pyspark-flood-{self.mode}-streaming-group"
        spool_batch = 0
        while True:
            try:
                query = self.start_query(bootstrap_servers, topics, group)
                break
            except KafkaError as error:
                print(f"[Structured Streaming] Kafka chưa sẵn sàng, đang xử lý file đệm: {error}")
                spool_batch = self._drain_buffer(topics, spool_batch, MAX_OFFSETS)
                self._recover_hot_snapshot()
                time.sleep(2)
        try:
            print(f"[Structured Streaming] {self.mode}: {query.id}")
            while not query.awaitTermination(1):
                with self.processing_lock:
                    spool_batch = self._drain_buffer(topics, spool_batch, MAX_OFFSETS)
                    self._recover_hot_snapshot()
        finally:
            if query.isActive:
                query.stop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=TOPICS, default="live")
    parser.add_argument("--backfill-delta", action="store_true",
                        help="Import normalized historical JSONL into Delta and exit")
    args = parser.parse_args()
    stream = StructuredFloodStream(mode=args.mode, history_only=args.backfill_delta)
    try:
        if args.backfill_delta:
            print(f"[Delta Lake] {stream.backfill_history()} reports checked for import into {stream.delta_path}")
        else:
            stream.run(os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
    except KeyboardInterrupt:
        print("[Structured Streaming] Đã dừng.")
    finally:
        stream.stop()


if __name__ == "__main__":
    main()
