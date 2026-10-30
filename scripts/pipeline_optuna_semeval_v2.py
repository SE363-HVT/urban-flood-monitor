#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/pipeline_optuna_semeval_v2.py
--------------------------------------------------------------------------------
Sequential Execution Pipeline for Optuna Tuning (3 trials x 5 epochs) & Full ASTE
Fine-Tuning on SemEval v2 Format on GPU 2 (UUID: GPU-40888ad5-fe5d-17c8-a236-4b0fd1d97e6f):
  1. PhoBERT Base v2 (vinai/phobert-base-v2)
  2. XLM-V Base (facebook/xlm-v-base)
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

PHOBERT_SCRIPT = os.path.join(PROJECT_ROOT, "AI", "phobert", "base_v2", "semeval_v2", "finetune", "tune_and_train_phobert_semeval_v2.py")
XLM_V_SCRIPT = os.path.join(PROJECT_ROOT, "AI", "xlm_v", "base", "semeval_v2", "finetune", "tune_and_train_xlm_v_semeval_v2.py")
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
    phobert_report_path = os.path.join(PROJECT_ROOT, "AI", "phobert", "base_v2", "semeval_v2", "test", "benchmark_reports", "phobert_base_v2_semeval_v2_report.json")
    xlm_v_report_path = os.path.join(PROJECT_ROOT, "AI", "xlm_v", "base", "semeval_v2", "test", "benchmark_reports", "xlm_v_base_semeval_v2_report.json")

    phobert_data = {}
    xlm_v_data = {}

    if os.path.exists(phobert_report_path):
        with open(phobert_report_path, "r", encoding="utf-8") as f:
            phobert_data = json.load(f)
    if os.path.exists(xlm_v_report_path):
        with open(xlm_v_report_path, "r", encoding="utf-8") as f:
            xlm_v_data = json.load(f)

    p_f1 = phobert_data.get("Triplet_Strict_Match", {}).get("F1", 0.0)
    p_prec = phobert_data.get("Triplet_Strict_Match", {}).get("Precision", 0.0)
    p_rec = phobert_data.get("Triplet_Strict_Match", {}).get("Recall", 0.0)
    p_asp = phobert_data.get("Aspect_Span", {}).get("F1", 0.0)
    p_opn = phobert_data.get("Opinion_Span", {}).get("F1", 0.0)
    p_pos = phobert_data.get("Polarity_Per_Class", {}).get("POS", {}).get("F1", 0.0)
    p_macro = phobert_data.get("Macro_Polarity_F1", 0.0)

    x_f1 = xlm_v_data.get("Triplet_Strict_Match", {}).get("F1", 0.0)
    x_prec = xlm_v_data.get("Triplet_Strict_Match", {}).get("Precision", 0.0)
    x_rec = xlm_v_data.get("Triplet_Strict_Match", {}).get("Recall", 0.0)
    x_asp = xlm_v_data.get("Aspect_Span", {}).get("F1", 0.0)
    x_opn = xlm_v_data.get("Opinion_Span", {}).get("F1", 0.0)
    x_pos = xlm_v_data.get("Polarity_Per_Class", {}).get("POS", {}).get("F1", 0.0)
    x_macro = xlm_v_data.get("Macro_Polarity_F1", 0.0)

    print(f"  • PhoBERT Base v2 Strict F1: {p_f1:.2f}% (P: {p_prec:.2f}%, R: {p_rec:.2f}%)")
    print(f"  • XLM-V Base Strict F1      : {x_f1:.2f}% (P: {x_prec:.2f}%, R: {x_rec:.2f}%)")

    # Read BENCHMARK_TABLE.md and replace lines
    if os.path.exists(BENCHMARK_FILE):
        with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Update lines
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            if "| **PhoBERT Base v2** |" in line and "semeval" in content.lower():
                best_tag = " 🏆" if p_f1 >= x_f1 else ""
                new_line = f"| **PhoBERT Base v2** | *Extractive Span-Pair (Base)* | {p_prec:.2f}% | {p_rec:.2f}% | **{p_f1:.2f}%**{best_tag} | {p_asp:.2f}% | {p_opn:.2f}% | {p_pos:.2f}% | {p_macro:.2f}% |"
                new_lines.append(new_line)
            elif "| **XLM-V Base** |" in line and "semeval" in content.lower():
                best_tag = " 🏆" if x_f1 > p_f1 else " 🥈"
                new_line = f"| **XLM-V Base** | *Extractive Span-Pair (1M Vocab)* | {x_prec:.2f}% | {x_rec:.2f}% | **{x_f1:.2f}%**{best_tag} | {x_asp:.2f}% | {x_opn:.2f}% | {x_pos:.2f}% | {x_macro:.2f}% |"
                new_lines.append(new_line)
            else:
                new_lines.append(line)

        with open(BENCHMARK_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
        print("  ✓ Đã cập nhật thành công AI/results/BENCHMARK_TABLE.md!")

def main():
    print("=" * 80)
    print("🌟 RADI-NET: PIPELINE OPTUNA (3 TRIALS x 5 EPOCHS) & FINE-TUNING SEMEVAL V2")
    print(f"  • Target GPU       : GPU 2 (UUID: {GPU_UUID_2})")
    print(f"  • PhoBERT Script   : {PHOBERT_SCRIPT}")
    print(f"  • XLM-V Script     : {XLM_V_SCRIPT}")
    print("=" * 80)

    # 1. Chạy PhoBERT Base v2
    run_step(
        "PhoBERT Base v2 Optuna + Fine-tuning",
        [sys.executable, "-u", PHOBERT_SCRIPT, "--n_trials", "3", "--trial_epochs", "5", "--final_epochs", "25", "--final_patience", "5"]
    )

    # 2. Chạy XLM-V Base
    run_step(
        "XLM-V Base Optuna + Fine-tuning",
        [sys.executable, "-u", XLM_V_SCRIPT, "--n_trials", "3", "--trial_epochs", "5", "--final_epochs", "25", "--final_patience", "5"]
    )

    # 3. Cập nhật bảng Benchmark
    update_benchmark_table()

    print("\n🎉 TOÀN BỘ PIPELINE ĐÃ HOÀN TẤT THÀNH CÔNG RỰC RỠ!\n")

if __name__ == "__main__":
    main()
