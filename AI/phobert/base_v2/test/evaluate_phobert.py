#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI/phobert/test/evaluate_phobert.py
--------------------------------------------------------------------------------
Benchmark Evaluation for fine-tuned PhoBERT models on the independent test split.
Outputs academic metrics JSON report to AI/phobert/test/benchmark_reports/.
"""

import os
import sys
import json
import argparse
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PHOBERT_DIR = os.path.dirname(SCRIPT_DIR)
AI_DIR = os.path.dirname(PHOBERT_DIR)
PROJECT_ROOT = os.path.dirname(AI_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.train_phobert_aste import (
    ASTEJsonDataset,
    aste_collate_fn,
    PhoBertForASTE,
    evaluate_model
)


def main():
    parser = argparse.ArgumentParser(description="Evaluate PhoBERT on test set")
    parser.add_argument("--checkpoint_dir", type=str, required=True, help="Path to checkpoint directory")
    parser.add_argument("--test_file", type=str, default="data/processed/splits/test.json", help="Path to test.json")
    parser.add_argument("--model_name", type=str, default=None, help="Backbone model name (if not in checkpoint)")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--output_report", type=str, default=None, help="File to save JSON benchmark report")
    args = parser.parse_args()

    device = torch.device(args.device)
    print(f"Loading checkpoint from: {args.checkpoint_dir} on {device}...")

    ckpt_file = os.path.join(args.checkpoint_dir, "best_phobert_aste.pt")
    if not os.path.exists(ckpt_file):
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_file}")

    ckpt = torch.load(ckpt_file, map_location=device)
    model_name = args.model_name or ckpt.get("args", {}).get("model_name") or ckpt.get("params", {}).get("model_name", "vinai/phobert-base-v2")

    tokenizer = AutoTokenizer.from_pretrained(args.checkpoint_dir)
    test_path = os.path.join(PROJECT_ROOT, args.test_file) if not os.path.isabs(args.test_file) else args.test_file
    test_ds = ASTEJsonDataset(test_path, tokenizer, max_len=160, is_train=False)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False, collate_fn=aste_collate_fn)

    dropout = ckpt.get("args", {}).get("dropout", 0.15)
    model = PhoBertForASTE(model_name=model_name, dropout_rate=dropout).to(device)
    model.load_state_dict(ckpt["model_state_dict"])

    print(f"Running evaluation on {len(test_ds)} test samples...")
    metrics = evaluate_model(model, test_loader, tokenizer, device)

    out_file = args.output_report
    if not out_file:
        model_tag = "large" if "large" in model_name else "base_v2"
        out_file = os.path.join(SCRIPT_DIR, "benchmark_reports", f"phobert_{model_tag}_test_report.json")

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"🏆 BENCHMARK EVALUATION RESULTS: {model_name}")
    print("=" * 60)
    print(f"  • Triplet Strict Match F1 : {metrics['Triplet_Strict_Match']['F1']:.2f}% (P: {metrics['Triplet_Strict_Match']['Precision']}%, R: {metrics['Triplet_Strict_Match']['Recall']}%)")
    print(f"  • Aspect Entity F1        : {metrics['Aspect_Span']['F1']:.2f}% (P: {metrics['Aspect_Span']['Precision']}%, R: {metrics['Aspect_Span']['Recall']}%)")
    print(f"  • Opinion Expression F1   : {metrics['Opinion_Span']['F1']:.2f}% (P: {metrics['Opinion_Span']['Precision']}%, R: {metrics['Opinion_Span']['Recall']}%)")
    print(f"  • Macro Polarity F1       : {metrics['Macro_Polarity_F1']:.2f}%")
    for pol in ["NEG", "POS", "NEU"]:
        p = metrics["Polarity_Per_Class"][pol]
        print(f"    - [{pol}] F1: {p['F1']:.2f}% (P: {p['Precision']}%, R: {p['Recall']}%, Gold: {p['Gold']})")
    print(f"\nReport saved to: {out_file}")


if __name__ == "__main__":
    main()
