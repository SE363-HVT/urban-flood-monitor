#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/evaluate_xlm_v.py
--------------------------------------------------------------------------------
Benchmark Evaluation for fine-tuned XLM-V model on independent test split.
Outputs academic metrics JSON report to AI/xlm_v/base/test/benchmark_reports/.
"""

import os
import sys
import json
import argparse
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.train_xlm_v_aste import (
    XLMVJsonDataset,
    aste_collate_fn,
    XLMVForASTE,
    evaluate_model
)

DEFAULT_CHECKPOINT_DIR = os.path.join(PROJECT_ROOT, "AI", "xlm_v", "base", "finetune", "checkpoints")
DEFAULT_TEST_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "splits", "test.json")
DEFAULT_REPORT_FILE = os.path.join(PROJECT_ROOT, "AI", "xlm_v", "base", "test", "benchmark_reports", "test_report.json")


def main():
    parser = argparse.ArgumentParser(description="Evaluate fine-tuned XLM-V model on test set")
    parser.add_argument("--checkpoint_dir", type=str, default=DEFAULT_CHECKPOINT_DIR, help="Path to checkpoint directory")
    parser.add_argument("--test_file", type=str, default=DEFAULT_TEST_FILE, help="Path to test.json")
    parser.add_argument("--model_name", type=str, default="facebook/xlm-v-base", help="Backbone model name")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    parser.add_argument("--max_len", type=int, default=256, help="Max sequence length")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--output_report", type=str, default=DEFAULT_REPORT_FILE, help="File to save JSON benchmark report")

    args = parser.parse_args()

    ckpt_path = os.path.join(args.checkpoint_dir, "best_xlm_v_aste.pt")
    if not os.path.exists(ckpt_path):
        raise FileNotFoundError(f"Missing checkpoint file: {ckpt_path}")

    device = torch.device(args.device)
    checkpoint = torch.load(ckpt_path, map_location=device, weights_only=False)

    model_name = checkpoint.get("model_name", args.model_name)
    params = checkpoint.get("params", {})
    dropout = params.get("dropout", 0.15)

    print(f"[*] Nạp Tokenizer: {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(args.checkpoint_dir if os.path.exists(os.path.join(args.checkpoint_dir, "tokenizer_config.json")) else model_name)

    print(f"[*] Khởi tạo mô hình XLM-V và nạp trọng số đã lưu...")
    model = XLMVForASTE(model_name=model_name, dropout_rate=dropout).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    print(f"[*] Nạp tập dữ liệu Test: {args.test_file}...")
    test_dataset = XLMVJsonDataset(args.test_file, tokenizer, max_len=args.max_len, is_train=False)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, collate_fn=aste_collate_fn)

    print(f"[*] Tiến hành đánh giá trên {len(test_dataset)} mẫu...")
    metrics = evaluate_model(model, test_loader, device)
    metrics["model_name"] = model_name

    os.makedirs(os.path.dirname(args.output_report), exist_ok=True)
    with open(args.output_report, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 75)
    print("📊 BẢNG KẾT QUẢ ĐÁNH GIÁ (XLM-V BASE)")
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
    print(f"[+] Báo cáo đã lưu vào: {args.output_report}")


if __name__ == "__main__":
    main()
