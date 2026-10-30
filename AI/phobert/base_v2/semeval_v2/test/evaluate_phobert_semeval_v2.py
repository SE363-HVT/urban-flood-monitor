#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI/phobert/base_v2/test/evaluate_phobert_semeval_v2.py
--------------------------------------------------------------------------------
Comprehensive Evaluation Script for PhoBERT Base v2 on SemEval v2 Test Split.
Evaluates:
  1. Strict Triplet Exact Match (F1, Precision, Recall)
  2. Aspect Boundary Extraction (F1, Precision, Recall)
  3. Opinion Boundary Extraction (F1, Precision, Recall)
  4. Macro & Per-class Sentiment Polarity F1 (NEG, POS, NEU)
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

from train_phobert_semeval_v2 import (
    PhoBertForSemEvalASTE,
    SemEvalASTEDataset,
    semeval_collate_fn,
    ID2TAG,
    POLARITY2ID,
    ID2POLARITY
)


def compute_span_metrics(gold_spans: List[Set[Tuple[int, ...]]], pred_spans: List[Set[Tuple[int, ...]]]) -> Dict[str, float]:
    total_gold = sum(len(g) for g in gold_spans)
    total_pred = sum(len(p) for p in pred_spans)
    total_correct = sum(len(g.intersection(p)) for g, p in zip(gold_spans, pred_spans))

    p = (total_correct / total_pred * 100) if total_pred > 0 else 0.0
    r = (total_correct / total_gold * 100) if total_gold > 0 else 0.0
    f1 = (2 * p * r / (p + r)) if (p + r) > 0 else 0.0

    return {
        "Precision": round(p, 2),
        "Recall": round(r, 2),
        "F1": round(f1, 2),
        "Gold": total_gold,
        "Predicted": total_pred,
        "Correct": total_correct
    }


def evaluate_test_set(model: PhoBertForSemEvalASTE, data_loader: DataLoader, device: torch.device) -> Dict[str, any]:
    model.eval()

    all_gold_triplets = []
    all_pred_triplets = []

    all_gold_aspects = []
    all_pred_aspects = []

    all_gold_opinions = []
    all_pred_opinions = []

    polarity_stats = {
        "NEG": {"gold": 0, "pred": 0, "correct": 0},
        "POS": {"gold": 0, "pred": 0, "correct": 0},
        "NEU": {"gold": 0, "pred": 0, "correct": 0}
    }

    with torch.no_grad():
        for batch in data_loader:
            in_ids = batch["input_ids"].to(device, non_blocking=True)
            att_m = batch["attention_mask"].to(device, non_blocking=True)
            bio_tags = batch["bio_tags"].to(device, non_blocking=True)
            raw_batch = batch["raw_batch"]

            with torch.amp.autocast('cuda', enabled=device.type == "cuda"):
                outputs = model(input_ids=in_ids, attention_mask=att_m, bio_tags=bio_tags, raw_batch=raw_batch)

            bio_logits = outputs["bio_logits"]
            pred_tags_batch = torch.argmax(bio_logits, dim=-1).cpu().tolist()

            encoder_out = model.encoder(input_ids=in_ids, attention_mask=att_m).last_hidden_state
            cls_out = encoder_out[:, 0, :]

            for b_idx, sample in enumerate(raw_batch):
                seq_len = sample["seq_len"]
                predicted_tags = [ID2TAG[t] for t in pred_tags_batch[b_idx][:seq_len]]
                pred_triplets = model.predict_semeval_triplets(
                    sequence_output=encoder_out[b_idx],
                    cls_output=cls_out[b_idx],
                    predicted_tags=predicted_tags,
                    bpe2word=sample["bpe2word"]
                )

                gold_triplets = [
                    (tuple(sorted(t[0])), tuple(sorted(t[1])), t[2].upper())
                    for t in sample.get("semeval_triplets", [])
                ]

                g_trip_set = set(gold_triplets)
                p_trip_set = set(pred_triplets)

                all_gold_triplets.append(g_trip_set)
                all_pred_triplets.append(p_trip_set)

                # Aspect & Opinion span sets
                g_asp_set = {t[0] for t in g_trip_set}
                p_asp_set = {t[0] for t in p_trip_set}
                all_gold_aspects.append(g_asp_set)
                all_pred_aspects.append(p_asp_set)

                g_opn_set = {t[1] for t in g_trip_set}
                p_opn_set = {t[1] for t in p_trip_set}
                all_gold_opinions.append(g_opn_set)
                all_pred_opinions.append(p_opn_set)

                # Polarity stats
                for gt in g_trip_set:
                    pol = gt[2]
                    if pol in polarity_stats:
                        polarity_stats[pol]["gold"] += 1

                for pt in p_trip_set:
                    pol = pt[2]
                    if pol in polarity_stats:
                        polarity_stats[pol]["pred"] += 1
                    if pt in g_trip_set:
                        if pol in polarity_stats:
                            polarity_stats[pol]["correct"] += 1

    # Calculate Triplet metrics
    triplet_metrics = compute_span_metrics(all_gold_triplets, all_pred_triplets)
    aspect_metrics = compute_span_metrics(all_gold_aspects, all_pred_aspects)
    opinion_metrics = compute_span_metrics(all_gold_opinions, all_pred_opinions)

    # Polarity metrics
    pol_results = {}
    macro_f1_list = []
    for pol, stat in polarity_stats.items():
        cg = stat["gold"]
        cp = stat["pred"]
        cc = stat["correct"]
        p_c = (cc / cp * 100) if cp > 0 else 0.0
        r_c = (cc / cg * 100) if cg > 0 else 0.0
        f1_c = (2 * p_c * r_c / (p_c + r_c)) if (p_c + r_c) > 0 else 0.0
        pol_results[pol] = {
            "Precision": round(p_c, 2),
            "Recall": round(r_c, 2),
            "F1": round(f1_c, 2),
            "Gold": cg,
            "Predicted": cp,
            "Correct": cc
        }
        if cg > 0:
            macro_f1_list.append(f1_c)

    macro_f1 = sum(macro_f1_list) / len(macro_f1_list) if macro_f1_list else 0.0

    return {
        "Triplet_Strict_Match": triplet_metrics,
        "Aspect_Span": aspect_metrics,
        "Opinion_Span": opinion_metrics,
        "Macro_Polarity_F1": round(macro_f1, 2),
        "Polarity_Per_Class": pol_results
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate PhoBERT SemEval v2 Model")
    parser.add_argument("--checkpoint_dir", type=str,
                        default=os.path.join(SEMEVAL_DIR, "finetune", "checkpoints", "best_model"),
                        help="Path to checkpoint directory containing phobert_aste_weights.pt")
    parser.add_argument("--test_file", type=str,
                        default=os.path.join(PROJECT_ROOT, "data", "semeval_v2", "test.json"),
                        help="Path to test.json in SemEval v2 format")
    parser.add_argument("--model_name", type=str, default="vinai/phobert-base-v2")
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--output_report", type=str, default=None)
    args = parser.parse_args()

    device = torch.device(args.device)
    weights_path = os.path.join(args.checkpoint_dir, "phobert_aste_weights.pt")
    if not os.path.exists(weights_path):
        raise FileNotFoundError(f"Weights file not found: {weights_path}")

    print(f"Loading checkpoint from: {weights_path} on {device}...")
    tokenizer = AutoTokenizer.from_pretrained(args.checkpoint_dir if os.path.exists(os.path.join(args.checkpoint_dir, "vocab.txt")) else args.model_name)

    test_ds = SemEvalASTEDataset(args.test_file, tokenizer, max_len=160)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False, collate_fn=semeval_collate_fn)

    model = PhoBertForSemEvalASTE(model_name=args.model_name, dropout_rate=0.15).to(device)
    state_dict = torch.load(weights_path, map_location=device)
    model.load_state_dict(state_dict)

    print(f"Evaluating PhoBERT on {len(test_ds)} SemEval v2 test samples...")
    metrics = evaluate_test_set(model, test_loader, device)

    # Save benchmark report
    out_file = args.output_report
    if not out_file:
        out_file = os.path.join(SCRIPT_DIR, "benchmark_reports", "phobert_base_v2_semeval_v2_report.json")

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 68)
    print("🏆 BÁO CÁO ĐÁNH GIÁ PHOBERT-BASE-V2 TRÊN SEMEVAL V2 TEST SPLIT")
    print("=" * 68)
    print(f"  • Triplet Strict Match F1 : {metrics['Triplet_Strict_Match']['F1']:.2f}% "
          f"(P: {metrics['Triplet_Strict_Match']['Precision']}%, R: {metrics['Triplet_Strict_Match']['Recall']}%) "
          f"[{metrics['Triplet_Strict_Match']['Correct']}/{metrics['Triplet_Strict_Match']['Gold']}]")
    print(f"  • Aspect Entity F1        : {metrics['Aspect_Span']['F1']:.2f}% "
          f"(P: {metrics['Aspect_Span']['Precision']}%, R: {metrics['Aspect_Span']['Recall']}%)")
    print(f"  • Opinion Expression F1   : {metrics['Opinion_Span']['F1']:.2f}% "
          f"(P: {metrics['Opinion_Span']['Precision']}%, R: {metrics['Opinion_Span']['Recall']}%)")
    print(f"  • Macro Polarity F1       : {metrics['Macro_Polarity_F1']:.2f}%")
    for pol in ["NEG", "POS", "NEU"]:
        p = metrics["Polarity_Per_Class"][pol]
        print(f"    - [{pol}] F1: {p['F1']:.2f}% (P: {p['Precision']}%, R: {p['Recall']}%, Gold: {p['Gold']}, Pred: {p['Predicted']})")
    print(f"\nReport đã lưu tại: {out_file}")
    print("=" * 68)


if __name__ == "__main__":
    main()
