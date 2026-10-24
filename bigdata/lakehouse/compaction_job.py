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

import glob
import json
import argparse
from typing import List, Dict, Any

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

DEFAULT_LAKEHOUSE_DIR = os.path.join(ROOT_DIR, "data", "lakehouse", "flood_events")
TARGET_PARQUET_DIR = os.path.join(ROOT_DIR, "data", "lakehouse", "silver_parquet_lakehouse")


def compact_with_spark(base_dir: str, min_files_threshold: int = 1, force: bool = False):
    """Sử dụng PySpark để đọc, nén và coalesce(1) xuất bản Parquet."""
    try:
        from pyspark.sql import SparkSession
    except ImportError:
        print("[!] PySpark chưa sẵn sàng, chuyển sang chế độ Compact Standalone.")
        compact_standalone(base_dir, min_files_threshold)
        return

    print("[*] Khởi tạo Spark Session cho Lakehouse Compaction Job...")
    spark = SparkSession.builder \
        .appName("SE363-Lakehouse-Compaction-Job") \
        .master("local[*]") \
        .config("spark.ui.showConsoleProgress", "false") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    partition_folders = glob.glob(os.path.join(base_dir, "episode_id=*", "date=*"))
    print(f"[*] Tìm thấy {len(partition_folders)} phân vùng trong Lakehouse ({base_dir})...")

    compacted_count = 0
    for folder in partition_folders:
        jsonl_files = glob.glob(os.path.join(folder, "*.jsonl"))
        if len(jsonl_files) >= min_files_threshold or force:
            print(f"[*] Đang nén gộp {len(jsonl_files)} tệp vụn tại: {folder}")
            rel_path = os.path.relpath(folder, base_dir)
            target_folder = os.path.join(TARGET_PARQUET_DIR, rel_path)
            os.makedirs(target_folder, exist_ok=True)

            try:
                df = spark.read.json(folder)
                count = df.count()
                df.coalesce(1).write.mode("overwrite").parquet(target_folder)
                print(f"   [+] Đã tối ưu hóa xong {count} bản ghi -> {target_folder}")
                compacted_count += 1
            except Exception as e:
                print(f"   [!] Lỗi khi nén phân vùng {folder} với Spark: {e}")
                compact_single_folder_standalone(folder, target_folder)

    spark.stop()
    print(f"\n[+] Hoàn tất Lakehouse Compaction Job! Đã tối ưu {compacted_count} phân vùng.")


def compact_single_folder_standalone(folder: str, target_folder: str):
    """Nén gộp thủ công khi Spark IO gặp giới hạn."""
    jsonl_files = glob.glob(os.path.join(folder, "*.jsonl"))
    all_records = []
    for jf in jsonl_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        all_records.append(json.loads(line))
        except Exception:
            pass

    if not all_records:
        return

    os.makedirs(target_folder, exist_ok=True)
    out_file = os.path.join(target_folder, "consolidated_events.jsonl")
    with open(out_file, "w", encoding="utf-8") as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"   [+] Standalone Compact: {len(all_records)} bản ghi -> {out_file}")


def compact_standalone(base_dir: str, min_files_threshold: int = 1):
    partition_folders = glob.glob(os.path.join(base_dir, "episode_id=*", "date=*"))
    print(f"[*] [Standalone Mode] Tìm thấy {len(partition_folders)} phân vùng...")
    for folder in partition_folders:
        jsonl_files = glob.glob(os.path.join(folder, "*.jsonl"))
        if len(jsonl_files) >= min_files_threshold:
            rel_path = os.path.relpath(folder, base_dir)
            target_folder = os.path.join(TARGET_PARQUET_DIR, rel_path)
            compact_single_folder_standalone(folder, target_folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SE363 - Lakehouse Compaction & Parquet Optimizer")
    parser.add_argument("--base-dir", default=DEFAULT_LAKEHOUSE_DIR, help="Thư mục gốc của flood_events lakehouse")
    parser.add_argument("--threshold", type=int, default=2, help="Số lượng file vụn tối thiểu để kích hoạt compaction")
    parser.add_argument("--force", action="store_true", help="Cưỡng chế nén tất cả phân vùng")
    parser.add_argument("--standalone", action="store_true", help="Chạy chế độ Standalone không cần Spark")

    args = parser.parse_args()
    if args.standalone:
        compact_standalone(args.base_dir, args.threshold)
    else:
        compact_with_spark(args.base_dir, args.threshold, force=args.force)
