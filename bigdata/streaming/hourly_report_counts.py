"""Finalized event-time counts over the durable report history."""

import json
import time
from pathlib import Path

from pyspark.sql import functions as F

from bigdata.streaming.stream_storage import write_json_atomic


REPORT_WATERMARK = "24 hours"


def hourly_counts(reports, activated_at):
    report = F.col("report_json")
    received_at = F.coalesce(
        F.try_to_timestamp(F.get_json_object(report, "$.ingested_at_iso")),
        F.try_to_timestamp(F.get_json_object(report, "$.veracity.evaluated_at")),
    )
    observed = reports.where(F.col("event_time") > 0).select(
        F.timestamp_seconds("event_time").alias("posted_at"), received_at.alias("received_at"),
    ).where(
        (F.col("received_at") >= F.timestamp_seconds(F.lit(activated_at)))
        & (F.col("posted_at") <= F.col("received_at"))
    )
    grouped = (
        observed.withWatermark("posted_at", REPORT_WATERMARK)
        .groupBy(F.window("posted_at", "1 hour"))
        .agg(F.count("*").alias("report_version_count"))
    )
    return grouped.select(
        F.col("window.start").alias("window_start_utc"),
        F.col("window.end").alias("window_end_utc"),
        "report_version_count",
    )


class HourlyReportCounts:
    def __init__(self, spark, source, target, checkpoint):
        self.spark = spark.newSession()
        self.spark.conf.set("spark.sql.session.timeZone", "UTC")
        self.source = Path(source).resolve()
        self.target = Path(target).resolve()
        self.checkpoint = Path(checkpoint).resolve()

    def prepare(self):
        plan_path = self.checkpoint / "bootstrap.json"
        if plan_path.exists():
            return
        version = 0
        if (self.source / "_delta_log").is_dir():
            from delta.tables import DeltaTable

            version = DeltaTable.forPath(self.spark, self.source.as_uri()).history(1).first()["version"]
        write_json_atomic(plan_path, {"activated_at": int(time.time()), "starting_version": version}, durable=True)

    def start(self, *, available_now=False):
        if not (self.source / "_delta_log").is_dir():
            return None
        with (self.checkpoint / "bootstrap.json").open(encoding="utf-8") as source:
            plan = json.load(source)
        reports = (
            self.spark.readStream.format("delta")
            .option("startingVersion", str(plan["starting_version"]))
            .option("maxFilesPerTrigger", 20)
            .load(self.source.as_uri())
        )
        writer = (
            hourly_counts(reports, plan["activated_at"]).writeStream.format("delta")
            .outputMode("append")
            .option("checkpointLocation", (self.checkpoint / "query").as_uri())
        )
        return (writer.trigger(availableNow=True) if available_now
                else writer.trigger(processingTime="30 seconds")).start(self.target.as_uri())
