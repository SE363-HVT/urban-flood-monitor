"""Run with SE363_RUN_SPARK_INTEGRATION=1 to verify the real Delta watermark."""

import os
import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from bigdata.lakehouse.delta_reports import DeltaReportHistory
from bigdata.streaming.hourly_report_counts import HourlyReportCounts
from bigdata.streaming.structured_flood_stream import StructuredFloodStream


@unittest.skipUnless(os.environ.get("SE363_RUN_SPARK_INTEGRATION") == "1", "requires a local Spark runtime")
class HourlyRollupIntegrationTests(unittest.TestCase):
    def test_in_order_late_and_future_records_with_checkpoint(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"SE363_SPARK_MASTER": "local[2]"}):
            root = Path(folder)
            stream = StructuredFloodStream(history_only=True)
            self.addCleanup(stream.stop)
            spark = stream.spark
            reports = DeltaReportHistory(spark, root / "reports")
            rollup = HourlyReportCounts(spark, reports.path, root / "hourly", root / "checkpoint")
            rollup.prepare()
            now = int(time.time())
            first_hour = (now // 3600 - 30) * 3600

            def saved_report(identity, timestamp):
                return {
                    "canonical_id": identity, "report_version": identity, "create_time": timestamp,
                    "ingested_at_iso": datetime.now(timezone.utc).isoformat(),
                }

            def drain():
                query = rollup.start(available_now=True)
                try:
                    self.assertTrue(query.awaitTermination(120))
                    return query.recentProgress
                finally:
                    if query.isActive:
                        query.stop()

            reports.write([saved_report("a", first_hour + 30), saved_report("future", now + 86400)])
            drain()
            reports.write([saved_report("b", first_hour + 60)])
            drain()
            reports.write([saved_report("advance", now - 10)])
            drain()
            reports.write([saved_report("late", first_hour + 120)])
            progress = drain()

            def counts():
                return (spark.read.format("delta").load(rollup.target.as_uri())
                        .selectExpr("cast(window_start_utc as bigint) as epoch", "report_version_count")
                        .collect())

            self.assertEqual([tuple(row) for row in counts()], [(first_hour, 2)])
            self.assertEqual(sum(
                operator.get("numRowsDroppedByWatermark", 0)
                for batch in progress for operator in batch.get("stateOperators", [])
            ), 1)
            self.assertEqual(spark.read.format("delta").load(reports.path.as_uri()).count(), 5)
            drain()
            self.assertEqual([tuple(row) for row in counts()], [(first_hour, 2)])
