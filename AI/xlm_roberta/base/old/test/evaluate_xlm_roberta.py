#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI/xlm_roberta/base/test/evaluate_xlm_roberta.py
--------------------------------------------------------------------------------
Benchmark Evaluation for fine-tuned XLM-RoBERTa model on independent test split.
Outputs academic metrics JSON report to AI/xlm_roberta/base/test/benchmark_reports/.
"""

import os
import sys
import json
import argparse
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.train_xlm_roberta_aste import (
    XLMRobertaJsonDataset,
    aste_collate_fn,
    XLMRobertaForASTE,
    evaluate_model
)


def main():
    parser = argparse.ArgumentParser(description="Evaluate XLM-RoBERTa on test set")
    parser.add_argument("--checkpoint_dir", type=str, default=os.path.join(BASE_DIR, "finetune", "checkpoints"), help="Path to checkpoint directory")
    parser.add_argument("--test_file", type=str, default=os.path.join(PROJECT_ROOT, "data", "processed", "splits", "test.json"), help="Path to test.json")
    parser.add_argument("--model_name", type=str, default="xlm-roberta-base", help="Backbone model name")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--output_report", type=str, default=os.path.join(SCRIPT_DIR, "benchmark_reports", "test_report.json"), help="File to save JSON benchmark report")

    args = parser.parse_args()

    ckpt_path = os.path.join(args.checkpoint_dir, "best_xlm_roberta_aste.pt")
    if not os.path.exists(ckpt_path):
        raise FileNotFoundError(f"Missing checkpoint file: {ckpt_path}")

    device = torch.device(args.device)
    checkpoint = torch.load(ckpt_path, map_location=device, weights_only=False)

    model_name = checkpoint.get("model_name", args.model_name)
    params = checkpoint.get("params", {})
    dropout = params.get("dropout", 0.15)

    print(f"[*] Nạp Tokenizer: {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(args.checkpoint_dir if os.path.exists(os.path.join(args.checkpoint_dir, "tokenizer_config.json")) else model_name)

    print(f"[*] Khởi tạo mô hình và nạp trọng số...")
    model = XLMRobertaForASTE(model_name=model_name, dropout_rate=dropout).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    print(f"[*] Đang tải dữ liệu test từ {args.test_file}...")
    test_ds = XLMRobertaJsonDataset(args.test_file, tokenizer, max_len=160, is_train=False)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False, collate_fn=aste_collate_fn)

    print(f"[*] Bắt đầu đánh giá trên {len(test_ds)} mẫu...")
    metrics = evaluate_model(model, test_loader, device)

    os.makedirs(os.path.dirname(args.output_report), exist_ok=True)
    with open(args.output_report, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("📊 BÁO CÁO THỰC NGHIỆM ĐỘC LẬP TRÊN TẬP TEST (XLM-ROBERTA)")
    print("=" * 70)
    tm = metrics["Triplet_Strict_Match"]
    am = metrics["Aspect_Span"]
    om = metrics["Opinion_Span"]
    print(f"{'Task / Metric':<25} | {'Precision (%)':<14} | {'Recall (%)':<14} | {'F1-Score (%)':<14}")
    print("-" * 75)
    print(f"{'Triplet Strict Match':<25} | {tm['Precision']:<14.2f} | {tm['Recall']:<14.2f} | {tm['F1']:<14.2f}")
    print(f"{'Aspect Extraction':<25} | {am['Precision']:<14.2f} | {am['Recall']:<14.2f} | {am['F1']:<14.2f}")
    print(f"{'Opinion Extraction':<25} | {om['Precision']:<14.2f} | {om['Recall']:<14.2f} | {om['F1']:<14.2f}")
    print("-" * 75)
    for p_name in ["NEG", "POS", "NEU"]:
        pm = metrics["Polarity_Per_Class"][p_name]
        print(f"{f'Polarity [{p_name}]':<25} | {pm['Precision']:<14.2f} | {pm['Recall']:<14.2f} | {pm['F1']:<14.2f}")
    print("-" * 75)
    print(f"{'Macro Polarity F1':<25} | {'-':<14} | {'-':<14} | {metrics['Macro_Polarity_F1']:<14.2f}")
    print("=" * 70)
    print(f"[+] Báo cáo khoa học đã lưu tại: {args.output_report}")


if __name__ == "__main__":
    main()
