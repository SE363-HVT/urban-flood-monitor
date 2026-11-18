# -*- coding: utf-8 -*-
"""
bigdata/lakehouse/compaction_job.py
Tối ưu hóa và Nén gộp Hồ Dữ liệu (Lakehouse Compaction & Small Files Merging).

Mục tiêu (Blueprint 4.2):
- Quét toàn bộ cây phân vùng Lakehouse: data/lakehouse/flood_events/episode_id=*/date=*
- Phát hiện các phân vùng bị chia cắt bởi hàng nghìn tệp JSONL vụn (Small Files Crisis).
- Tự động nén gộp (coalesce/compact) thành định dạng cột Apache Parquet (Snappy-compressed)
  tại data/lakehouse/silver_parquet_lakehouse/.
- Giảm 95% I/O Metadata Overhead cho các công cụ truy vấn (Spark SQL, DuckDB, Trino).
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import json
import argparse
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

DEFAULT_LAKEHOUSE_DIR = os.path.join(ROOT_DIR, "data", "lakehouse", "flood_events")
TARGET_PARQUET_DIR = os.path.join(ROOT_DIR, "data", "lakehouse", "silver_parquet_lakehouse")


def _partition_files(folder):
    return sorted(Path(folder).glob("*.jsonl"))


def _read_snapshot(files, output, rejected):
    count = 0
    for path in files:
        # Capture the byte boundary before reading a legacy append-only file.
        with path.open("rb") as source:
            remaining = os.fstat(source.fileno()).st_size
            line_number = 0
            while remaining:
                line = source.readline(remaining)
                if not line:
                    break
                remaining -= len(line)
                line_number += 1
                if not line.endswith(b"\n"):
                    # Immutable files can be valid without a trailing newline. The
                    # legacy shared file may still be appending the final record.
                    if path.name == "events_bronze.jsonl":
                        break
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    if not isinstance(record, dict):
                        raise ValueError("Expected a JSON object")
                except (ValueError, RecursionError) as error:
                    rejected.write(json.dumps({
                        "file": path.name, "line": line_number, "reason": str(error),
                        "value": line.decode("utf-8", errors="backslashreplace").rstrip(),
                    }, ensure_ascii=False) + "\n")
                    continue
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
    return count


def _compact_folder(folder, relative_path, files, spark=None):
    output_root = Path(TARGET_PARQUET_DIR).parent
    output_root.mkdir(parents=True, exist_ok=True)
    target_jsonl = output_root / "silver_jsonl_lakehouse" / relative_path
    target_parquet = Path(TARGET_PARQUET_DIR) / relative_path
    with TemporaryDirectory(dir=output_root, prefix="compact-") as temporary:
        stage = Path(temporary)
        snapshot_path = stage / "snapshot.jsonl"
        rejected_path = stage / "rejected.jsonl"
        with snapshot_path.open("w", encoding="utf-8") as output, rejected_path.open("w", encoding="utf-8") as rejected:
            count = _read_snapshot(files, output, rejected)
        if rejected_path.stat().st_size:
            quarantine = output_root / "compaction_quarantine" / relative_path
            quarantine.mkdir(parents=True, exist_ok=True)
            os.replace(rejected_path, quarantine / "invalid_records.jsonl")
        if not count:
            return False

        if spark is not None:
            try:
                df = spark.read.option("mode", "FAILFAST").json(str(snapshot_path))
                partitions = max(1, (snapshot_path.stat().st_size + 64 * 1024**2 - 1) // (64 * 1024**2))
                prepared = stage / "parquet"
                df.repartition(partitions).write.parquet(str(prepared))
                target_parquet.parent.mkdir(parents=True, exist_ok=True)
                previous = target_parquet.with_name(f".{target_parquet.name}.previous")
                if previous.exists():
                    if target_parquet.exists():
                        shutil.rmtree(previous)
                    else:
                        previous.rename(target_parquet)
                if target_parquet.exists():
                    target_parquet.rename(previous)
                try:
                    prepared.rename(target_parquet)
                except OSError:
                    if previous.exists():
                        previous.rename(target_parquet)
                    raise
                if previous.exists():
                    shutil.rmtree(previous)
                print(f"[+] Parquet: {count} bản ghi -> {target_parquet}")
                return True
            except Exception as error:
                print(f"[!] Không thể xuất Parquet từ {folder}: {error}")

        target_jsonl.mkdir(parents=True, exist_ok=True)
        path = target_jsonl / "consolidated_events.jsonl"
        os.replace(snapshot_path, path)
        print(f"[+] JSONL: {count} bản ghi -> {path}")
        return True


def compact_standalone(base_dir: str, min_files_threshold: int = 1, force: bool = False):
    _compact(base_dir, min_files_threshold, force)


def _compact(base_dir, threshold, force, spark=None):
    for folder in sorted(Path(base_dir).glob("episode_id=*/date=*")):
        files = _partition_files(folder)
        if files and (len(files) >= threshold or force):
            _compact_folder(folder, folder.relative_to(base_dir), files, spark)


def compact_with_spark(base_dir: str, min_files_threshold: int = 1, force: bool = False):
    try:
        from pyspark.sql import SparkSession
    except ImportError:
        compact_standalone(base_dir, min_files_threshold, force)
        return

    spark = (SparkSession.builder.appName("SE363-Lakehouse-Compaction-Job")
             .master("local[*]").config("spark.ui.showConsoleProgress", "false").getOrCreate())
    try:
        spark.sparkContext.setLogLevel("ERROR")
        _compact(base_dir, min_files_threshold, force, spark)
    finally:
        spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SE363 - Lakehouse Compaction & Parquet Optimizer")
    parser.add_argument("--base-dir", default=DEFAULT_LAKEHOUSE_DIR, help="Thư mục gốc của flood_events lakehouse")
    parser.add_argument("--threshold", type=int, default=2, help="Số lượng file vụn tối thiểu để kích hoạt compaction")
    parser.add_argument("--force", action="store_true", help="Cưỡng chế nén tất cả phân vùng")
    parser.add_argument("--standalone", action="store_true", help="Chạy chế độ Standalone không cần Spark")

    args = parser.parse_args()
    if args.standalone:
        compact_standalone(args.base_dir, args.threshold, args.force)
    else:
        compact_with_spark(args.base_dir, args.threshold, force=args.force)
