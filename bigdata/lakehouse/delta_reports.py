"""Versioned analytical history for normalized flood reports."""

import json
from pathlib import Path

from pyspark.sql.types import (
    DoubleType, LongType, StringType, StructField, StructType,
)

from scripts.crawlers.organize_raw_episodes import determine_episode_id
from bigdata.streaming.spark_records import frame_from_records


REPORT_SCHEMA = StructType([
    StructField("report_version", StringType(), False),
    StructField("canonical_id", StringType(), False),
    StructField("event_time", LongType()),
    StructField("historical_timestamp", LongType()),
    StructField("episode_id", StringType()),
    StructField("platform", StringType()),
    StructField("street", StringType()),
    StructField("ward", StringType()),
    StructField("location_precision", StringType()),
    StructField("polarity", StringType()),
    StructField("precipitation_mm", DoubleType()),
    StructField("report_json", StringType(), False),
])


def record_row(event):
    event_time = event.get("create_time") or event.get("timestamp")
    location = event.get("location") or {}
    weather = (event.get("veracity") or {}).get("weather_check") or {}
    rain = weather.get("precipitation_mm")
    return (
        event["report_version"],
        str(event.get("canonical_id") or event["id"]),
        event_time,
        event.get("historical_timestamp"),
        determine_episode_id(event_time) if event_time else None,
        event.get("platform"),
        location.get("street"),
        location.get("ward"),
        location.get("precision"),
        event.get("polarity"),
        float(rain) if isinstance(rain, (int, float)) else None,
        json.dumps(event, ensure_ascii=False),
    )


class DeltaReportHistory:
    def __init__(self, spark, directory):
        self.spark = spark
        self.path = Path(directory).resolve()

    def write(self, reports):
        if not reports:
            return
        from delta.tables import DeltaTable

        rows = {event["report_version"]: record_row(event) for event in reports}
        if len(rows) <= 120:
            fields = REPORT_SCHEMA.fieldNames()
            data = frame_from_records(
                self.spark, [dict(zip(fields, row)) for row in rows.values()], REPORT_SCHEMA, partitions=1
            )
        else:
            data = self.spark.createDataFrame(list(rows.values()), schema=REPORT_SCHEMA)
        uri = self.path.as_uri()
        if not (self.path / "_delta_log").exists():
            data.write.format("delta").mode("errorifexists").save(uri)
            return
        (DeltaTable.forPath(self.spark, uri).alias("stored")
         .merge(data.alias("incoming"), "stored.report_version = incoming.report_version")
         .whenNotMatchedInsertAll()
         .execute())
