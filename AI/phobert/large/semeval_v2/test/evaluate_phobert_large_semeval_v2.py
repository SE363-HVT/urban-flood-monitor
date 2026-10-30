#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI/phobert/large/semeval_v2/test/evaluate_phobert_large_semeval_v2.py
--------------------------------------------------------------------------------
Comprehensive Evaluation Script for PhoBERT Large on SemEval v2 Test Split.
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Tuple, Set

try:
    import setproctitle
    setproctitle.setproctitle("python")
except Exception:
    pass

import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DIR = SCRIPT_DIR
SEMEVAL_DIR = os.path.dirname(TEST_DIR)

def get_project_root():
    curr = os.path.abspath(SCRIPT_DIR)
    while curr != os.path.dirname(curr):
        if os.path.exists(os.path.join(curr, ".git")) or os.path.exists(os.path.join(curr, "data")):
            return curr
        curr = os.path.dirname(curr)
    return "/home/counting/Workspaces/ryan/RadiNet"

PROJECT_ROOT = get_project_root()
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

FINETUNE_DIR = os.path.join(SEMEVAL_DIR, "finetune")
if FINETUNE_DIR not in sys.path:
    sys.path.insert(0, FINETUNE_DIR)

from train_phobert_large_semeval_v2 import (
    PhoBertLargeForSemEvalASTE,
    SemEvalASTEDataset,
    semeval_collate_fn,
    ID2TAG,
    POLARITY2ID,
    ID2POLARITY
)


def compute_span_metrics(gold_spans: List[Set[Tuple[int, ...]]], pred_spans: List[Set[Tuple[int, ...]]]) -> Dict[str, float]:
    n_gold = sum(len(s) for s in gold_spans)
    n_pred = sum(len(s) for s in pred_spans)
    n_corr = sum(len(g & p) for g, p in zip(gold_spans, pred_spans))

    p = (n_corr / n_pred * 100) if n_pred > 0 else 0.0
    r = (n_corr / n_gold * 100) if n_gold > 0 else 0.0
    f1 = (2 * p * r / (p + r)) if (p + r) > 0 else 0.0
    return {
        "Precision": round(p, 2),
        "Recall": round(r, 2),
        "F1": round(f1, 2),
        "Gold": n_gold,
        "Predicted": n_pred,
        "Correct": n_corr
    }


def evaluate(checkpoint_dir: str, test_file: str, device_str: str = "cuda", max_len: int = 160):
    device = torch.device(device_str if torch.cuda.is_available() and "cuda" in device_str else "cpu")
    weights_path = os.path.join(checkpoint_dir, "phobert_large_aste_weights.pt")

    if not os.path.exists(weights_path):
        raise FileNotFoundError(f"Missing weights checkpoint at: {weights_path}")

    print(f"Loading checkpoint from: {weights_path} on {device}...")
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir)
    model = PhoBertLargeForSemEvalASTE(model_name="vinai/phobert-large")
    model.load_state_dict(torch.load(weights_path, map_location=device, weights_only=False))
    model.to(device)
    model.eval()

    test_ds = SemEvalASTEDataset(test_file, tokenizer, max_len=max_len)
    test_loader = DataLoader(
        test_ds,
        batch_size=16,
        shuffle=False,
        num_workers=2,
        pin_memory=True,
        collate_fn=semeval_collate_fn
    )

    print(f"Evaluating PhoBERT Large on {len(test_ds)} SemEval v2 test samples...")

    all_gold_triplets = []
    all_pred_triplets = []

    all_gold_aspects = []
    all_pred_aspects = []

    all_gold_opinions = []
    all_pred_opinions = []

    polarity_stats = {
        "NEG": {"correct": 0, "gold": 0, "pred": 0},
        "POS": {"correct": 0, "gold": 0, "pred": 0},
        "NEU": {"correct": 0, "gold": 0, "pred": 0}
    }

    with torch.no_grad():
        for batch in test_loader:
            in_ids = batch["input_ids"].to(device, non_blocking=True)
            att_m = batch["attention_mask"].to(device, non_blocking=True)
            raw_batch = batch["raw_batch"]

            outputs = model(input_ids=in_ids, attention_mask=att_m)
            bio_logits = outputs["bio_logits"]
            pred_tags_batch = torch.argmax(bio_logits, dim=-1).cpu().tolist()

            encoder_out = model.encoder(input_ids=in_ids, attention_mask=att_m).last_hidden_state
            cls_out = encoder_out[:, 0, :]

            for b_idx, sample in enumerate(raw_batch):
                seq_len = sample["seq_len"]
                pred_tags = [ID2TAG[t] for t in pred_tags_batch[b_idx][:seq_len]]

                pred_triplets = model.predict_semeval_triplets(
                    sequence_output=encoder_out[b_idx],
                    cls_output=cls_out[b_idx],
                    predicted_tags=pred_tags,
                    bpe2word=sample["bpe2word"]
                )

                gold_triplets = [
                    (tuple(sorted(t[0])), tuple(sorted(t[1])), t[2].upper())
                    for t in sample.get("semeval_triplets", [])
                ]

                g_set = set(gold_triplets)
                p_set = set(pred_triplets)

                all_gold_triplets.append(g_set)
                all_pred_triplets.append(p_set)

                g_asp = {t[0] for t in g_set}
                p_asp = {t[0] for t in p_set}
                all_gold_aspects.append(g_asp)
                all_pred_aspects.append(p_asp)

                g_opn = {t[1] for t in g_set}
                p_opn = {t[1] for t in p_set}
                all_gold_opinions.append(g_opn)
                all_pred_opinions.append(p_opn)

                for gt in g_set:
                    pol = gt[2]
                    if pol in polarity_stats:
                        polarity_stats[pol]["gold"] += 1

                for pt in p_set:
                    pol = pt[2]
                    if pol in polarity_stats:
                        polarity_stats[pol]["pred"] += 1

                for ct in (g_set & p_set):
                    pol = ct[2]
                    if pol in polarity_stats:
                        polarity_stats[pol]["correct"] += 1

    triplet_metrics = compute_span_metrics(all_gold_triplets, all_pred_triplets)
    aspect_metrics = compute_span_metrics(all_gold_aspects, all_pred_aspects)
    opinion_metrics = compute_span_metrics(all_gold_opinions, all_pred_opinions)

    pol_results = {}
    macro_f1_sum = 0.0
    for pol_name, stats in polarity_stats.items():
        c = stats["correct"]
        g = stats["gold"]
        p = stats["pred"]
        prec = (c / p * 100) if p > 0 else 0.0
        rec = (c / g * 100) if g > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        pol_results[pol_name] = {
            "Precision": round(prec, 2),
            "Recall": round(rec, 2),
            "F1": round(f1, 2),
            "Gold": g,
            "Predicted": p,
            "Correct": c
        }
        macro_f1_sum += f1

    macro_polarity_f1 = round(macro_f1_sum / len(polarity_stats), 2)

    report = {
        "Triplet_Strict_Match": triplet_metrics,
        "Aspect_Span": aspect_metrics,
        "Opinion_Span": opinion_metrics,
        "Macro_Polarity_F1": macro_polarity_f1,
        "Polarity_Per_Class": pol_results
    }

    report_dir = os.path.join(TEST_DIR, "benchmark_reports")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, "phobert_large_semeval_v2_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 68)
    print("🏆 BÁO CÁO ĐÁNH GIÁ PHOBERT LARGE TRÊN SEMEVAL V2 TEST SPLIT")
    print("=" * 68)
    print(f"  • Triplet Strict Match F1 : {triplet_metrics['F1']:.2f}% (P: {triplet_metrics['Precision']:.2f}%, R: {triplet_metrics['Recall']:.2f}%) [{triplet_metrics['Correct']}/{triplet_metrics['Gold']}]")
    print(f"  • Aspect Entity F1        : {aspect_metrics['F1']:.2f}% (P: {aspect_metrics['Precision']:.2f}%, R: {aspect_metrics['Recall']:.2f}%)")
    print(f"  • Opinion Expression F1   : {opinion_metrics['F1']:.2f}% (P: {opinion_metrics['Precision']:.2f}%, R: {opinion_metrics['Recall']:.2f}%)")
    print(f"  • Macro Polarity F1       : {macro_polarity_f1:.2f}%")
    for pol_name in ["NEG", "POS", "NEU"]:
        ps = pol_results[pol_name]
        print(f"    - [{pol_name}] F1: {ps['F1']:.2f}% (P: {ps['Precision']:.2f}%, R: {ps['Recall']:.2f}%, Gold: {ps['Gold']}, Pred: {ps['Predicted']})")
    print(f"\nReport đã lưu tại: {report_file}")
    print("=" * 68 + "\n")

    return report


def main():
    parser = argparse.ArgumentParser(description="Evaluate PhoBERT Large on SemEval v2 Test Set")
    parser.add_argument("--checkpoint_dir", type=str, default=os.path.join(SEMEVAL_DIR, "finetune", "checkpoints", "best_model"))
    parser.add_argument("--test_file", type=str, default=os.path.join(PROJECT_ROOT, "data", "semeval_v2", "test.json"))
    parser.add_argument("--device", type=str, default="cuda")
    args = parser.parse_args()

    evaluate(checkpoint_dir=args.checkpoint_dir, test_file=args.test_file, device_str=args.device)


if __name__ == "__main__":
    main()
