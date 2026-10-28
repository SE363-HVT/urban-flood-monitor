"""
AI/bartpho/word_base/test/evaluate_aste.py
--------------------------------------------------------------------------------
Comprehensive Academic Benchmark Evaluation for Generative ASTE using BARTpho.
Evaluates on independent test split (data/processed/splits/test.json or AI/bartpho/data/test.json).
Computes:
1. Strict Triplet F1 (Aspect + Opinion + Polarity exact match)
2. Aspect Extraction F1
3. Opinion Extraction F1
4. Per-Class Polarity F1 (NEG, POS, NEU) & Macro Polarity F1
"""

import os
import sys
import json
import time
import argparse
from typing import List, Set, Tuple, Dict, Any

import torch
from tqdm import tqdm

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORD_BASE_DIR = os.path.dirname(SCRIPT_DIR)
BARTPHO_DIR = os.path.dirname(WORD_BASE_DIR)

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from inference import ASTEPredictor, parse_triplets_from_string

DEFAULT_TEST_FILE = os.path.join(BARTPHO_DIR, "data", "test.json")
DEFAULT_CHECKPOINT_DIR = os.path.join(WORD_BASE_DIR, "finetune", "checkpoints", "best_aste_model")
DEFAULT_REPORT_FILE = os.path.join(WORD_BASE_DIR, "test", "benchmark_reports", "bartpho_word_test_report.json")


def tuple_from_dict(d: Dict[str, str]) -> Tuple[str, str, str]:
    """Convert triplet dict into normalized lowercased tuple for set matching."""
    asp = d.get("aspect", "").strip().lower()
    opi = d.get("opinion", "").strip().lower()
    pol = d.get("polarity", "NEG").strip().upper()
    return (asp, opi, pol)


def calculate_prf(gold_total: int, pred_total: int, correct_total: int) -> Tuple[float, float, float]:
    """Calculate Precision, Recall, and F1."""
    precision = (correct_total / pred_total * 100) if pred_total > 0 else 0.0
    recall = (correct_total / gold_total * 100) if gold_total > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return precision, recall, f1


def evaluate():
    parser = argparse.ArgumentParser(description="Evaluate BARTpho Generative ASTE Model")
    parser.add_argument("--test_file", type=str, default=DEFAULT_TEST_FILE, help="Path to test.json")
    parser.add_argument("--checkpoint_dir", type=str, default=DEFAULT_CHECKPOINT_DIR, help="Model checkpoint path")
    parser.add_argument("--output_report", type=str, default=DEFAULT_REPORT_FILE, help="Path to save output JSON benchmark report")
    parser.add_argument("--num_beams", type=int, default=4, help="Beam size for generation")
    parser.add_argument("--max_length", type=int, default=160, help="Max length for generation")

    args = parser.parse_args()

    if not os.path.exists(args.test_file):
        raise FileNotFoundError(f"Missing test dataset: {args.test_file}")

    with open(args.test_file, "r", encoding="utf-8") as f:
        test_samples = json.load(f)

    predictor = ASTEPredictor(checkpoint_dir=args.checkpoint_dir)

    print("=" * 75)
    print(f"BẮT ĐẦU ĐÁNH GIÁ MÔ HÌNH BARTPHO-WORD TRÊN TẬP TEST ({len(test_samples)} MẪU)")
    print(f"  • Checkpoint: {args.checkpoint_dir}")
    print(f"  • Test File : {args.test_file}")
    print("=" * 75)

    # Counters for Triplet Match
    n_gold_triplets = 0
    n_pred_triplets = 0
    n_correct_triplets = 0

    # Counters for Aspect Match
    n_gold_aspects = 0
    n_pred_aspects = 0
    n_correct_aspects = 0

    # Counters for Opinion Match
    n_gold_opinions = 0
    n_pred_opinions = 0
    n_correct_opinions = 0

    # Polarity per-class counters
    pol_counters = {
        "NEG": {"gold": 0, "pred": 0, "correct": 0},
        "POS": {"gold": 0, "pred": 0, "correct": 0},
        "NEU": {"gold": 0, "pred": 0, "correct": 0}
    }

    start_eval_time = time.time()

    for item in tqdm(test_samples, desc="Inference trên Test set"):
        text = item["input_text"]
        gold_raw = item.get("raw_triplets", [])

        gold_set = set(tuple_from_dict(t) for t in gold_raw)
        gold_aspects = set(t[0] for t in gold_set)
        gold_opinions = set(t[1] for t in gold_set)

        res = predictor.predict(text, max_length=args.max_length, num_beams=args.num_beams)
        pred_set = set(tuple_from_dict(t) for t in res["triplets"])
        pred_aspects = set(t[0] for t in pred_set)
        pred_opinions = set(t[1] for t in pred_set)

        # Triplets
        n_gold_triplets += len(gold_set)
        n_pred_triplets += len(pred_set)
        correct_triplets = gold_set.intersection(pred_set)
        n_correct_triplets += len(correct_triplets)

        # Aspects
        n_gold_aspects += len(gold_aspects)
        n_pred_aspects += len(pred_aspects)
        n_correct_aspects += len(gold_aspects.intersection(pred_aspects))

        # Opinions
        n_gold_opinions += len(gold_opinions)
        n_pred_opinions += len(pred_opinions)
        n_correct_opinions += len(gold_opinions.intersection(pred_opinions))

        # Polarity Breakdown
        for (g_asp, g_opi, g_pol) in gold_set:
            if g_pol in pol_counters:
                pol_counters[g_pol]["gold"] += 1
        for (p_asp, p_opi, p_pol) in pred_set:
            if p_pol in pol_counters:
                pol_counters[p_pol]["pred"] += 1
        for (c_asp, c_opi, c_pol) in correct_triplets:
            if c_pol in pol_counters:
                pol_counters[c_pol]["correct"] += 1

    eval_duration = time.time() - start_eval_time

    # Calculate Metrics
    t_p, t_r, t_f1 = calculate_prf(n_gold_triplets, n_pred_triplets, n_correct_triplets)
    a_p, a_r, a_f1 = calculate_prf(n_gold_aspects, n_pred_aspects, n_correct_aspects)
    o_p, o_r, o_f1 = calculate_prf(n_gold_opinions, n_pred_opinions, n_correct_opinions)

    polarity_results = {}
    macro_f1_sum = 0.0
    for p_name, counts in pol_counters.items():
        p, r, f = calculate_prf(counts["gold"], counts["pred"], counts["correct"])
        polarity_results[p_name] = {
            "Precision": round(p, 2),
            "Recall": round(r, 2),
            "F1": round(f, 2),
            "Gold": counts["gold"],
            "Pred": counts["pred"],
            "Correct": counts["correct"]
        }
        macro_f1_sum += f

    macro_pol_f1 = macro_f1_sum / max(1, len(pol_counters))

    report = {
        "model_name": "vinai/bartpho-word-base",
        "Triplet_Strict_Match": {
            "Precision": round(t_p, 2),
            "Recall": round(t_r, 2),
            "F1": round(t_f1, 2),
            "Gold": n_gold_triplets,
            "Pred": n_pred_triplets,
            "Correct": n_correct_triplets
        },
        "Aspect_Span": {
            "Precision": round(a_p, 2),
            "Recall": round(a_r, 2),
            "F1": round(a_f1, 2)
        },
        "Opinion_Span": {
            "Precision": round(o_p, 2),
            "Recall": round(o_r, 2),
            "F1": round(o_f1, 2)
        },
        "Polarity_Per_Class": polarity_results,
        "Macro_Polarity_F1": round(macro_pol_f1, 2),
        "Evaluation_Time_Seconds": round(eval_duration, 2),
        "Samples_Per_Second": round(len(test_samples) / max(0.001, eval_duration), 2)
    }

    os.makedirs(os.path.dirname(args.output_report), exist_ok=True)
    with open(args.output_report, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 75)
    print("📊 BẢNG KẾT QUẢ THỰC NGHIỆM ĐÁNH GIÁ (SCIENTIFIC BENCHMARK REPORT)")
    print("=" * 75)
    print(f"{'Task / Metric':<25} | {'Precision (%)':<14} | {'Recall (%)':<14} | {'F1-Score (%)':<14}")
    print("-" * 75)
    print(f"{'Triplet Strict Match':<25} | {t_p:<14.2f} | {t_r:<14.2f} | {t_f1:<14.2f}")
    print(f"{'Aspect Extraction':<25} | {a_p:<14.2f} | {a_r:<14.2f} | {a_f1:<14.2f}")
    print(f"{'Opinion Extraction':<25} | {o_p:<14.2f} | {o_r:<14.2f} | {o_f1:<14.2f}")
    print("-" * 75)
    for p_name in ["NEG", "POS", "NEU"]:
        m = polarity_results[p_name]
        print(f"{f'Polarity [{p_name}]':<25} | {m['Precision']:<14.2f} | {m['Recall']:<14.2f} | {m['F1']:<14.2f}")
    print("-" * 75)
    print(f"{'Macro Polarity F1':<25} | {'-':<14} | {'-':<14} | {macro_pol_f1:<14.2f}")
    print("=" * 75)
    print(f"[+] Báo cáo khoa học JSON đã lưu: {args.output_report}")
    print(f"[+] Tốc độ suy luận: {report['Samples_Per_Second']} mẫu/giây ({eval_duration:.1f}s)")


if __name__ == "__main__":
    evaluate()
