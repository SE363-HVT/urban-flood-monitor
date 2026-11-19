"""Build small driver-supplied DataFrames without starting Python workers."""

import json

from pyspark.sql import functions as F


def frame_from_records(spark, records, schema, *, partitions):
    literals = F.array(*(F.lit(json.dumps(record, ensure_ascii=False)) for record in records))
    encoded = F.get(literals, F.col("id").cast("int"))
    source = spark.range(len(records), numPartitions=min(partitions, len(records)))
    return source.select(F.from_json(encoded, schema, {"mode": "FAILFAST"}).alias("record")).select("record.*")
