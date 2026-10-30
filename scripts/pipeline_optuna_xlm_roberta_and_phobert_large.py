#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/pipeline_optuna_xlm_roberta_and_phobert_large.py
--------------------------------------------------------------------------------
Sequential Execution Pipeline for Optuna Tuning (3 trials x 5 epochs) & Full ASTE
Fine-Tuning on SemEval v2 Format strictly on GPU 2 (UUID: GPU-40888ad5-fe5d-17c8-a236-4b0fd1d97e6f):
  1. XLM-RoBERTa Base (xlm-roberta-base) -> Optuna -> Fine-tune -> Test Split Eval
  2. PhoBERT Large (vinai/phobert-large) -> Optuna -> Fine-tune -> Test Split Eval
Followed by Benchmark Report Extraction and Benchmark Table Update.
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

XLM_ROBERTA_SCRIPT = os.path.join(PROJECT_ROOT, "AI", "xlm_roberta", "base", "semeval_v2", "finetune", "tune_and_train_xlm_roberta_semeval_v2.py")
PHOBERT_LARGE_SCRIPT = os.path.join(PROJECT_ROOT, "AI", "phobert", "large", "semeval_v2", "finetune", "tune_and_train_phobert_large_semeval_v2.py")
BENCHMARK_FILE = os.path.join(PROJECT_ROOT, "AI", "results", "BENCHMARK_TABLE.md")

def run_step(step_name: str, cmd: list):
    print("\n" + "=" * 80)
    print(f"⏩ BẮT ĐẦU: {step_name}")
    print(f"   Command: {' '.join(cmd)}")
    print("=" * 80 + "\n", flush=True)
    t0 = time.time()
    res = subprocess.run(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=GPU_UUID_2))
    dur = time.time() - t0
    if res.returncode != 0:
        print(f"\n❌ LỖI tại {step_name} (mã thoát {res.returncode}, thời gian: {dur:.1f}s)", flush=True)
        sys.exit(res.returncode)
    print(f"\n✅ HOÀN TẤT: {step_name} (thời gian: {dur:.1f}s)\n", flush=True)

def update_benchmark_table():
    print("\n📊 Đang đồng bộ hóa kết quả vào AI/results/BENCHMARK_TABLE.md...")
    xlm_r_report_path = os.path.join(PROJECT_ROOT, "AI", "xlm_roberta", "base", "semeval_v2", "test", "benchmark_reports", "xlm_roberta_base_semeval_v2_report.json")
    phobert_lg_report_path = os.path.join(PROJECT_ROOT, "AI", "phobert", "large", "semeval_v2", "test", "benchmark_reports", "phobert_large_semeval_v2_report.json")

    xlm_r_data = {}
    phobert_lg_data = {}

    if os.path.exists(xlm_r_report_path):
        with open(xlm_r_report_path, "r", encoding="utf-8") as f:
            xlm_r_data = json.load(f)
    if os.path.exists(phobert_lg_report_path):
        with open(phobert_lg_report_path, "r", encoding="utf-8") as f:
            phobert_lg_data = json.load(f)

    # XLM-RoBERTa Base metrics
    xr_f1 = xlm_r_data.get("Triplet_Strict_Match", {}).get("F1", 0.0)
    xr_prec = xlm_r_data.get("Triplet_Strict_Match", {}).get("Precision", 0.0)
    xr_rec = xlm_r_data.get("Triplet_Strict_Match", {}).get("Recall", 0.0)
    xr_asp = xlm_r_data.get("Aspect_Span", {}).get("F1", 0.0)
    xr_opn = xlm_r_data.get("Opinion_Span", {}).get("F1", 0.0)
    xr_pos = xlm_r_data.get("Polarity_Per_Class", {}).get("POS", {}).get("F1", 0.0)
    xr_macro = xlm_r_data.get("Macro_Polarity_F1", 0.0)

    # PhoBERT Large metrics
    pl_f1 = phobert_lg_data.get("Triplet_Strict_Match", {}).get("F1", 0.0)
    pl_prec = phobert_lg_data.get("Triplet_Strict_Match", {}).get("Precision", 0.0)
    pl_rec = phobert_lg_data.get("Triplet_Strict_Match", {}).get("Recall", 0.0)
    pl_asp = phobert_lg_data.get("Aspect_Span", {}).get("F1", 0.0)
    pl_opn = phobert_lg_data.get("Opinion_Span", {}).get("F1", 0.0)
    pl_pos = phobert_lg_data.get("Polarity_Per_Class", {}).get("POS", {}).get("F1", 0.0)
    pl_macro = phobert_lg_data.get("Macro_Polarity_F1", 0.0)

    print(f"  • XLM-RoBERTa Base Strict F1 : {xr_f1:.2f}% (P: {xr_prec:.2f}%, R: {xr_rec:.2f}%)")
    print(f"  • PhoBERT Large Strict F1    : {pl_f1:.2f}% (P: {pl_prec:.2f}%, R: {pl_rec:.2f}%)")

    # Read BENCHMARK_TABLE.md and replace lines
    if os.path.exists(BENCHMARK_FILE):
        with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        new_lines = []
        in_semeval_part = False

        for line in lines:
            if "PHẦN 1: BẢNG BENCHMARK TRÊN ĐỊNH DẠNG MỚI" in line:
                in_semeval_part = True
            elif "PHẦN 2:" in line:
                in_semeval_part = False

            if in_semeval_part and "| **XLM-RoBERTa Base** |" in line:
                new_line = f"| **XLM-RoBERTa Base** | *Extractive Span-Pair Multilingual* | {xr_prec:.2f}% | {xr_rec:.2f}% | **{xr_f1:.2f}%** | {xr_asp:.2f}% | {xr_opn:.2f}% | {xr_pos:.2f}% | {xr_macro:.2f}% |"
                new_lines.append(new_line)
            elif in_semeval_part and "| **PhoBERT Large** |" in line:
                new_line = f"| **PhoBERT Large** | *Extractive Span-Pair (Large)* | {pl_prec:.2f}% | {pl_rec:.2f}% | **{pl_f1:.2f}%** | {pl_asp:.2f}% | {pl_opn:.2f}% | {pl_pos:.2f}% | {pl_macro:.2f}% |"
                new_lines.append(new_line)
            else:
                new_lines.append(line)

        with open(BENCHMARK_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
        print("  ✓ Đã cập nhật thành công AI/results/BENCHMARK_TABLE.md!\n")

def main():
    print("=" * 80)
    print("🚀 PIPELINE CHẠY TUẦN TỰ: OPTUNA & HUẤN LUYỆN XLM-ROBERTA VÀ PHOBERT LARGE")
    print(f"  • Target GPU UUID  : {GPU_UUID_2} (RTX 2080 Ti #2)")
    print(f"  • Step 1           : XLM-RoBERTa Base (Optuna 3 trials x 5 ep -> Full fine-tuning -> Test)")
    print(f"  • Step 2           : PhoBERT Large (Optuna 3 trials x 5 ep -> Full fine-tuning -> Test)")
    print(f"  • Step 3           : Tự động cập nhật AI/results/BENCHMARK_TABLE.md")
    print("=" * 80 + "\n", flush=True)

    py_exe = sys.executable

    # BƯỚC 1: XLM-RoBERTa Base
    run_step(
        "GIAI ĐOẠN 1: XLM-RoBERTa Base Optuna & Huấn luyện SemEval v2",
        [py_exe, XLM_ROBERTA_SCRIPT, "--n_trials", "3", "--trial_epochs", "5", "--final_epochs", "25", "--final_patience", "5"]
    )

    # BƯỚC 2: PhoBERT Large
    run_step(
        "GIAI ĐOẠN 2: PhoBERT Large Optuna & Huấn luyện SemEval v2",
        [py_exe, PHOBERT_LARGE_SCRIPT, "--n_trials", "3", "--trial_epochs", "5", "--final_epochs", "25", "--final_patience", "5"]
    )

    # BƯỚC 3: Cập nhật Benchmark Table
    update_benchmark_table()

    print("\n" + "=" * 80)
    print("🎉 TẤT CẢ GIAI ĐOẠN HUẤN LUYỆN & ĐÁNH GIÁ ĐÃ HOÀN TẤT THÀNH CÔNG!")
    print("=" * 80 + "\n", flush=True)

if __name__ == "__main__":
    main()
