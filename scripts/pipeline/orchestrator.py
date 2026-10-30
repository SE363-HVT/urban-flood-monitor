# -*- coding: utf-8 -*-
"""
scripts/orchestrator.py
Bộ điều phối và Tự động hóa Pipeline (Pipeline Orchestrator & Workflow DAG).

Mục tiêu (Phase 4):
- Quản lý lịch chạy các tác vụ:
  1. Task 1: Thu nạp dữ liệu mạng xã hội (Ingestion Task).
  2. Task 2: Nén gộp và tối ưu hóa Lakehouse (Compaction Job).
  3. Task 3: Kiểm tra sức khỏe toàn trình (End-to-End Health Check).
  4. Task 4: Sao lưu snapshot hồ dữ liệu (Backup Lakehouse).
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import time
import argparse
import subprocess
from typing import Dict, Any, List

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

PYTHON_EXE = sys.executable


class PipelineOrchestrator:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def run_task(self, name: str, command: List[str]) -> bool:
        start_time = time.time()
        print(f"\n[DAG Orchestrator] >>> Bắt đầu Task: [{name}]...")
        try:
            res = subprocess.run(command, cwd=ROOT_DIR, check=False)
            duration = round(time.time() - start_time, 2)
            success = (res.returncode == 0)
            status_str = "THÀNH CÔNG" if success else f"LỖI (Exit {res.returncode})"
            print(f"[DAG Orchestrator] <<< Hoàn tất [{name}]: {status_str} trong {duration}s")
            self.history.append({
                "task": name,
                "status": status_str,
                "duration_seconds": duration,
                "timestamp": int(time.time())
            })
            return success
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            print(f"[DAG Orchestrator] <<< Lỗi ngoại lệ trong [{name}]: {e}")
            self.history.append({
                "task": name,
                "status": f"FAILED ({e})",
                "duration_seconds": duration,
                "timestamp": int(time.time())
            })
            return False

    def run_daily_pipeline(self):
        """Chạy chuỗi DAG toàn diện hàng ngày."""
        print("=" * 70)
        print("[*] KHOI CHAY PIPELINE ORCHESTRATION DAG (DAILY BATCH)")
        print("=" * 70)

        # 1. Thu nạp dữ liệu nhanh
        self.run_task(
            "Social Data Ingestion Cycle",
            [PYTHON_EXE, "-c", "from bigdata.producers.social_producer import SocialKafkaProducer; p = SocialKafkaProducer(); print(p.run_live_cycle(enable_free_crawler=True))"]
        )

        # 2. Nén gộp Lakehouse Parquet
        self.run_task(
            "Lakehouse Compaction Job",
            [PYTHON_EXE, os.path.join(ROOT_DIR, "bigdata", "lakehouse", "compaction_job.py"), "--threshold", "1", "--standalone"]
        )

        # 3. Chạy Automated Smoke Test kiểm tra chất lượng
        self.run_task(
            "Smoke Test Validation",
            [PYTHON_EXE, os.path.join(ROOT_DIR, "tests", "smoke_test_pipeline.py")]
        )

        print("\n" + "=" * 70)
        print("[*] BAO CAO KET QUA THUC THI DAG:")
        for h in self.history:
            print(f" - {h['task']}: {h['status']} ({h['duration_seconds']}s)")
        print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SE363 - Data Pipeline Orchestrator")
    parser.add_argument("--mode", default="daily", choices=["daily", "compact", "test"], help="Chế độ chạy DAG")
    parser.add_argument("--run-all", action="store_true", help="Chạy toàn bộ các tasks trong DAG (tương đương --mode daily)")
    args = parser.parse_args()

    orchestrator = PipelineOrchestrator()
    if args.run_all or args.mode == "daily":
        orchestrator.run_daily_pipeline()
    elif args.mode == "compact":
        orchestrator.run_task(
            "Lakehouse Compaction",
            [PYTHON_EXE, os.path.join(ROOT_DIR, "bigdata", "lakehouse", "compaction_job.py"), "--threshold", "1", "--standalone"]
        )
    elif args.mode == "test":
        orchestrator.run_task(
            "Smoke Test",
            [PYTHON_EXE, os.path.join(ROOT_DIR, "tests", "smoke_test_pipeline.py")]
        )
