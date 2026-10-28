#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/evaluate_mt5.py
--------------------------------------------------------------------------------
Benchmark Evaluation for fine-tuned mT5-Base ASTE Model on test split.
Outputs academic metrics JSON report to AI/mt5/base/test/benchmark_reports/.
"""

import os
import sys
import json
import time
import argparse
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.train_mt5_aste import (
    MT5ASTEDataset,
    mt5_collate_fn,
    evaluate_val_loss_and_f1
)

DEFAULT_CHECKPOINT_DIR = os.path.join(PROJECT_ROOT, "AI", "mt5", "base", "finetune", "checkpoints", "best_aste_model")
DEFAULT_TEST_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "splits", "test.json")
DEFAULT_REPORT_FILE = os.path.join(PROJECT_ROOT, "AI", "mt5", "base", "test", "benchmark_reports", "test_report.json")


def main():
    parser = argparse.ArgumentParser(description="Evaluate fine-tuned mT5-Base on test set")
    parser.add_argument("--checkpoint_dir", type=str, default=DEFAULT_CHECKPOINT_DIR, help="Path to checkpoint directory")
    parser.add_argument("--test_file", type=str, default=DEFAULT_TEST_FILE, help="Path to test.json")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    parser.add_argument("--max_source_len", type=int, default=256, help="Max source length")
    parser.add_argument("--max_target_len", type=int, default=128, help="Max target length")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--output_report", type=str, default=DEFAULT_REPORT_FILE, help="File to save JSON benchmark report")

    args = parser.parse_args()

    if not os.path.exists(args.checkpoint_dir):
        raise FileNotFoundError(f"Missing checkpoint directory: {args.checkpoint_dir}")

    device = torch.device(args.device)

    print(f"[*] Nạp Tokenizer từ {args.checkpoint_dir}...")
    tokenizer = AutoTokenizer.from_pretrained(args.checkpoint_dir)
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0

    print(f"[*] Khởi tạo mô hình mT5 từ {args.checkpoint_dir}...")
    model = AutoModelForSeq2SeqLM.from_pretrained(args.checkpoint_dir).to(device)
    model.eval()

    print(f"[*] Nạp tập dữ liệu Test: {args.test_file}...")
    test_ds = MT5ASTEDataset(args.test_file, tokenizer, args.max_source_len, args.max_target_len)
    test_loader = DataLoader(
        test_ds,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=lambda b: mt5_collate_fn(b, pad_id),
        num_workers=0
    )

    print(f"[*] Tiến hành đánh giá trên {len(test_ds)} mẫu test...")
    start_time = time.time()
    test_loss, metrics = evaluate_val_loss_and_f1(
        model=model,
        val_loader=test_loader,
        tokenizer=tokenizer,
        val_dataset=test_ds,
        device=device,
        max_target_len=args.max_target_len
    )
    eval_time = round(time.time() - start_time, 2)

    metrics["model_name"] = "google/mt5-base"
    metrics["Evaluation_Time_Seconds"] = eval_time
    metrics["Samples_Per_Second"] = round(len(test_ds) / max(0.01, eval_time), 2)
    metrics["Test_Loss"] = test_loss

    os.makedirs(os.path.dirname(args.output_report), exist_ok=True)
    with open(args.output_report, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 75)
    print("📊 BẢNG KẾT QUẢ ĐÁNH GIÁ (mT5 BASE)")
    print("=" * 75)
    print(f"{'Task / Metric':<26} | {'Precision (%)':<15} | {'Recall (%)':<15} | {'F1-Score (%)':<15}")
    print("-" * 75)
    tm = metrics["Triplet_Strict_Match"]
    am = metrics["Aspect_Span"]
    om = metrics["Opinion_Span"]
    print(f"{'Triplet Strict Match':<26} | {tm['Precision']:<15.2f} | {tm['Recall']:<15.2f} | {tm['F1']:<15.2f}")
    print(f"{'Aspect Extraction':<26} | {am['Precision']:<15.2f} | {am['Recall']:<15.2f} | {am['F1']:<15.2f}")
    print(f"{'Opinion Extraction':<26} | {om['Precision']:<15.2f} | {om['Recall']:<15.2f} | {om['F1']:<15.2f}")
    print("-" * 75)
    for p_name in ["NEG", "POS", "NEU"]:
        p_data = metrics["Polarity_Per_Class"][p_name]
        print(f"{'Polarity [' + p_name + ']':<26} | {p_data['Precision']:<15.2f} | {p_data['Recall']:<15.2f} | {p_data['F1']:<15.2f}")
    print("-" * 75)
    print(f"{'Macro Polarity F1':<26} | {'-':<15} | {'-':<15} | {metrics['Macro_Polarity_F1']:<15.2f}")
    print("=" * 75 + "\n")
    print(f"[+] Báo cáo khoa học đã lưu vào: {args.output_report}")


if __name__ == "__main__":
    main()
