"""
finetune/evaluate_aste.py
Kịch bản đánh giá mô hình Generative ASTE trên tập kiểm thử độc lập (Test Set):
- Đọc 286 mẫu từ finetune/data/test.json.
- Đo lường các chỉ số chuẩn của các bài báo khoa học hàng đầu (ACL/EMNLP):
  + Triplet F1 (Khớp chính xác cả Aspect + Opinion + Polarity)
  + Aspect F1 (Khớp đúng tên đường / đối tượng)
  + Opinion F1 (Khớp đúng mức độ nghiêm trọng)
- Xuất bảng kết quả thực nghiệm hoàn chỉnh để trích dẫn vào bài báo.
"""

import os
import sys
import json
import argparse
from typing import List, Set, Tuple, Dict, Any

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tqdm import tqdm
from finetune.inference import ASTEPredictor, parse_triplets_from_string

TEST_FILE = os.path.join(CURRENT_DIR, "data", "test.json")


def tuple_from_dict(d: Dict[str, str]) -> Tuple[str, str, str]:
    """Chuẩn hóa bộ ba thành tuple để so khớp tập hợp (Set Matching)."""
    asp = d.get("aspect", "").strip().lower()
    opi = d.get("opinion", "").strip().lower()
    pol = d.get("polarity", "NEG").strip().upper()
    return (asp, opi, pol)


def calculate_prf(gold_total: int, pred_total: int, correct_total: int) -> Tuple[float, float, float]:
    """Tính Precision, Recall, F1-Score."""
    precision = correct_total / pred_total if pred_total > 0 else 0.0
    recall = correct_total / gold_total if gold_total > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision * 100, recall * 100, f1 * 100


def evaluate():
    parser = argparse.ArgumentParser(description="Đánh giá mô hình ASTE trên tập Test độc lập")
    parser.add_argument("--test_file", type=str, default=TEST_FILE, help="Đường dẫn file test.json")
    parser.add_argument("--checkpoint_dir", type=str, default=os.path.join(CURRENT_DIR, "checkpoints", "best_aste_model"), help="Thư mục checkpoint mô hình")
    parser.add_argument("--output_report", type=str, default=os.path.join(CURRENT_DIR, "benchmark_report.json"), help="File lưu kết quả chi tiết")

    args = parser.parse_args()

    if not os.path.exists(args.test_file):
        print(f"[!] Lỗi: Không tìm thấy file {args.test_file}. Vui lòng chạy 'prepare_dataset.py' trước!")
        sys.exit(1)

    with open(args.test_file, "r", encoding="utf-8") as f:
        test_samples = json.load(f)

    predictor = ASTEPredictor(checkpoint_dir=args.checkpoint_dir)

    print("\n" + "=" * 70)
    print(f"BẮT ĐẦU ĐÁNH GIÁ MÔ HÌNH TRÊN TẬP TEST ({len(test_samples)} MẪU)")
    print("=" * 70)

    # Các biến đếm cho Triplet Exact Match
    n_gold_triplets = 0
    n_pred_triplets = 0
    n_correct_triplets = 0

    # Các biến đếm cho Aspect Match
    n_gold_aspects = 0
    n_pred_aspects = 0
    n_correct_aspects = 0

    # Các biến đếm cho Opinion Match
    n_gold_opinions = 0
    n_pred_opinions = 0
    n_correct_opinions = 0

    detailed_results = []

    for item in tqdm(test_samples, desc="Đang suy luận tập Test"):
        text = item["input_text"]
        gold_triplets_raw = item.get("raw_triplets", [])

        # Chuyển đổi nhãn thực tế sang set
        gold_triplets_set = set(tuple_from_dict(t) for t in gold_triplets_raw)
        gold_aspects_set = set(t[0] for t in gold_triplets_set)
        gold_opinions_set = set(t[1] for t in gold_triplets_set)

        # Mô hình dự đoán
        pred_res = predictor.predict(text)
        pred_triplets_set = set(tuple_from_dict(t) for t in pred_res["triplets"])
        pred_aspects_set = set(t[0] for t in pred_triplets_set)
        pred_opinions_set = set(t[1] for t in pred_triplets_set)

        # Đếm Triplet
        n_gold_triplets += len(gold_triplets_set)
        n_pred_triplets += len(pred_triplets_set)
        n_correct_triplets += len(gold_triplets_set.intersection(pred_triplets_set))

        # Đếm Aspect
        n_gold_aspects += len(gold_aspects_set)
        n_pred_aspects += len(pred_aspects_set)
        n_correct_aspects += len(gold_aspects_set.intersection(pred_aspects_set))

        # Đếm Opinion
        n_gold_opinions += len(gold_opinions_set)
        n_pred_opinions += len(pred_opinions_set)
        n_correct_opinions += len(gold_opinions_set.intersection(pred_opinions_set))

        detailed_results.append({
            "id": item.get("id"),
            "input_text": text,
            "gold_triplets": [list(t) for t in gold_triplets_set],
            "pred_triplets": [list(t) for t in pred_triplets_set],
            "is_exact_match": gold_triplets_set == pred_triplets_set
        })

    # Tính toán chỉ số P, R, F1
    t_p, t_r, t_f1 = calculate_prf(n_gold_triplets, n_pred_triplets, n_correct_triplets)
    a_p, a_r, a_f1 = calculate_prf(n_gold_aspects, n_pred_aspects, n_correct_aspects)
    o_p, o_r, o_f1 = calculate_prf(n_gold_opinions, n_pred_opinions, n_correct_opinions)

    report = {
        "triplet_metrics": {"precision": round(t_p, 2), "recall": round(t_r, 2), "f1": round(t_f1, 2)},
        "aspect_metrics": {"precision": round(a_p, 2), "recall": round(a_r, 2), "f1": round(a_f1, 2)},
        "opinion_metrics": {"precision": round(o_p, 2), "recall": round(o_r, 2), "f1": round(o_f1, 2)},
        "total_test_samples": len(test_samples),
        "total_gold_triplets": n_gold_triplets,
        "total_pred_triplets": n_pred_triplets
    }

    with open(args.output_report, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("📊 BẢNG KẾT QUẢ THỰC NGHIỆM ĐÁNH GIÁ (SCIENTIFIC BENCHMARK TABLE)")
    print("=" * 70)
    print(f"{'Metric / Task':<25} | {'Precision (%)':<14} | {'Recall (%)':<14} | {'F1-Score (%)':<14}")
    print("-" * 75)
    print(f"{'Triplet (Exact ASTE)':<25} | {t_p:<14.2f} | {t_r:<14.2f} | {t_f1:<14.2f}")
    print(f"{'Aspect Extraction':<25} | {a_p:<14.2f} | {a_r:<14.2f} | {a_f1:<14.2f}")
    print(f"{'Opinion Extraction':<25} | {o_p:<14.2f} | {o_r:<14.2f} | {o_f1:<14.2f}")
    print("=" * 70)
    print(f"[+] Báo cáo chi tiết đã được lưu vào: {args.output_report}")


if __name__ == "__main__":
    evaluate()
