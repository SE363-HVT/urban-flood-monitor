#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/run_xlm_roberta_semeval_v2.py
--------------------------------------------------------------------------------
Full Pipeline for XLM-RoBERTa Base on SemEval v2:
  1. Train XLM-RoBERTa Base (Early Stopping Patience = 5) on GPU 2.
  2. Evaluate on Test Split (data/semeval_v2/test.json).
  3. Sync results directly into AI/results/BENCHMARK_TABLE.md.
"""

import os
import sys
import json
import time
import subprocess

try:
    import setproctitle
    setproctitle.setproctitle("python")
except Exception:
    pass

GPU_UUID_2 = "GPU-40888ad5-fe5d-17c8-a236-4b0fd1d97e6f"
os.environ["CUDA_VISIBLE_DEVICES"] = GPU_UUID_2
os.environ["TOKENIZERS_PARALLELISM"] = "false"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

TRAIN_SCRIPT = os.path.join(PROJECT_ROOT, "AI", "xlm_roberta", "base", "semeval_v2", "finetune", "train_xlm_roberta_semeval_v2.py")
EVAL_SCRIPT = os.path.join(PROJECT_ROOT, "AI", "xlm_roberta", "base", "semeval_v2", "test", "evaluate_xlm_roberta_semeval_v2.py")
REPORT_FILE = os.path.join(PROJECT_ROOT, "AI", "xlm_roberta", "base", "semeval_v2", "test", "benchmark_reports", "xlm_roberta_base_semeval_v2_report.json")
BENCHMARK_FILE = os.path.join(PROJECT_ROOT, "AI", "results", "BENCHMARK_TABLE.md")
CHECKPOINT_DIR = os.path.join(PROJECT_ROOT, "AI", "xlm_roberta", "base", "semeval_v2", "finetune", "checkpoints", "best_model")
TEST_FILE = os.path.join(PROJECT_ROOT, "data", "semeval_v2", "test.json")


def update_benchmark_table():
    if not os.path.exists(REPORT_FILE):
        print(f"⚠️ Không tìm thấy báo cáo tại {REPORT_FILE}")
        return

    with open(REPORT_FILE, "r", encoding="utf-8") as f:
        rep = json.load(f)

    tm = rep.get("Triplet_Strict_Match", {})
    am = rep.get("Aspect_Span", {})
    om = rep.get("Opinion_Span", {})
    pos = rep.get("Polarity_Per_Class", {}).get("POS", {})
    macro = rep.get("Macro_Polarity_F1", 0.0)

    p_f1 = tm.get("F1", 0.0)
    p_prec = tm.get("Precision", 0.0)
    p_rec = tm.get("Recall", 0.0)
    a_f1 = am.get("F1", 0.0)
    o_f1 = om.get("F1", 0.0)
    pos_f1 = pos.get("F1", 0.0)

    print(f"\n📊 Kết quả XLM-RoBERTa Base SemEval v2: Strict F1 = {p_f1:.2f}% (P: {p_prec:.2f}%, R: {p_rec:.2f}%)")

    if os.path.exists(BENCHMARK_FILE):
        with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        new_lines = []
        in_part1 = False

        for line in lines:
            if "### PHẦN 1: BẢNG BENCHMARK TRÊN ĐỊNH DẠNG MỚI" in line:
                in_part1 = True
            elif "### PHẦN 2:" in line:
                in_part1 = False

            if in_part1 and "| **XLM-RoBERTa Base** |" in line:
                new_line = f"| **XLM-RoBERTa Base** | *Extractive Span-Pair Multilingual* | {p_prec:.2f}% | {p_rec:.2f}% | **{p_f1:.2f}%** | {a_f1:.2f}% | {o_f1:.2f}% | {pos_f1:.2f}% | {macro:.2f}% |"
                new_lines.append(new_line)
            else:
                new_lines.append(line)

        with open(BENCHMARK_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
        print(f"  ✓ Đã cập nhật thành công {BENCHMARK_FILE}!\n")


def main():
    print("=" * 80)
    print("🚀 PIPELINE HUẤN LUYỆN & ĐÁNH GIÁ: XLM-ROBERTA BASE (SEMEVAL V2)")
    print(f"  • GPU Target   : GPU 2 (UUID: {GPU_UUID_2})")
    print(f"  • Train Script : {TRAIN_SCRIPT}")
    print(f"  • Eval Script  : {EVAL_SCRIPT}")
    print("=" * 80 + "\n")

    # 1. Huấn luyện
    train_cmd = [
        sys.executable, "-u", TRAIN_SCRIPT,
        "--learning_rate", "2.5e-5",
        "--batch_size", "16",
        "--epochs", "25",
        "--patience", "5",
        "--dropout", "0.15",
        "--weight_decay", "0.01"
    ]
    t0 = time.time()
    res = subprocess.run(train_cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=GPU_UUID_2))
    if res.returncode != 0:
        print(f"❌ Huấn luyện thất bại với mã lỗi {res.returncode}")
        sys.exit(res.returncode)

    train_dur = time.time() - t0
    print(f"\n✅ Hoàn tất huấn luyện sau {train_dur:.1f}s!\n")

    # 2. Đánh giá
    eval_cmd = [
        sys.executable, "-u", EVAL_SCRIPT,
        "--checkpoint_dir", CHECKPOINT_DIR,
        "--test_file", TEST_FILE
    ]
    res_eval = subprocess.run(eval_cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=GPU_UUID_2))
    if res_eval.returncode != 0:
        print(f"❌ Đánh giá thất bại với mã lỗi {res_eval.returncode}")
        sys.exit(res_eval.returncode)

    # 3. Đồng bộ hóa Benchmark Table
    update_benchmark_table()

    print("🎉 HOÀN TẤT TOÀN DIỆN XLM-ROBERTA BASE TRÊN SEMEVAL V2!")


if __name__ == "__main__":
    main()
