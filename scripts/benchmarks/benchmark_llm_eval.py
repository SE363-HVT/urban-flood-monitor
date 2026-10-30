#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/benchmark_llm_eval.py
--------------------------------------------------------------------------------
Independent Academic Benchmark Evaluation for Large Language Models (LLMs):
  1. Google Gemma-4-26B-A4B (MoE 26B, id: gemma-4-26b)
  2. Qwen3.8-27B (Dense Reasoning 27B, id: qwen3.8-27b)

Evaluates on the official Test Split:
  data/processed/splits/test.json (462 samples, 636 gold triplets)

Metrics computed:
  • Triplet Strict Match (Precision, Recall, F1)
  • Aspect Span Match (Precision, Recall, F1)
  • Opinion Span Match (Precision, Recall, F1)
  • Polarity Per Class (NEG, POS, NEU)
  • Macro Polarity F1

Outputs:
  • AI/llm/gemma_26b/test/benchmark_reports/test_report.json
  • AI/llm/gemma_26b/test/predictions.json
  • AI/llm/qwen_27b/test/benchmark_reports/test_report.json
  • AI/llm/qwen_27b/test/predictions.json
"""

import os
import sys
import re
import json
import time
import socket
import argparse
import requests
import urllib3
import concurrent.futures
from typing import Dict, Any, List, Tuple

urllib3.disable_warnings()

# ---------------------------------------------------------------------------
# DNS MONKEY-PATCH FOR UIT INTERNAL LLM GATEWAY (10.204.2.6)
# ---------------------------------------------------------------------------
_orig_getaddrinfo = socket.getaddrinfo

def _custom_getaddrinfo(host, port, *args, **kwargs):
    if host == "llm.uit.edu.vn":
        return _orig_getaddrinfo("10.204.2.6", port, *args, **kwargs)
    return _orig_getaddrinfo(host, port, *args, **kwargs)

socket.getaddrinfo = _custom_getaddrinfo

# ---------------------------------------------------------------------------
# CONSTANTS & CONFIGURATION
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
TEST_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "splits", "test.json")

API_KEY = "sk-uit-V1sRLf30CZhDl4b0ryimuxL8DHGf8HuN"

LLM_CONFIGS = {
    "gemma": {
        "display_name": "Gemma-4-26B",
        "model_id": "gemma-4-26b",
        "url": "https://llm.uit.edu.vn/gemma/v1/chat/completions",
        "max_tokens": 300,
        "temperature": 0.0,
        "output_dir": os.path.join(PROJECT_ROOT, "AI", "llm", "gemma_26b"),
        "timeout": 30
    },
    "qwen": {
        "display_name": "Qwen3.8-27B",
        "model_id": "qwen3.8-27b",
        "url": "https://llm.uit.edu.vn/qwen/v1/chat/completions",
        "max_tokens": 900,
        "temperature": 0.0,
        "output_dir": os.path.join(PROJECT_ROOT, "AI", "llm", "qwen_27b"),
        "timeout": 60
    }
}

# ---------------------------------------------------------------------------
# SYSTEM PROMPT FOR ASTE
# ---------------------------------------------------------------------------
ASTE_SYSTEM_PROMPT = """Bạn là chuyên gia trích xuất bộ ba ASTE (Aspect–Opinion–Polarity Triplet Extraction) trong lĩnh vực ngập lụt đô thị TP.HCM.

NHIỆM VỤ: Phân tích câu đầu vào và trích xuất TẤT CẢ bộ ba {"aspect", "opinion", "polarity"}.

1. "aspect" — thực thể được nhắc đến, thuộc 1 trong 5 nhóm:
   • Địa điểm: đường, hầm chui, cầu, giao lộ ("Trần Xuân Soạn", "hầm chui An Phú")
   • Hành chính: phường, quận, thành phố ("Phường Linh Đông", "Q7", "TP. Thủ Đức")
   • Thủy văn: sông, kênh, rạch, triều, mưa ("Kênh Nhiêu Lộc", "triều cường")
   • Hạ tầng thoát nước: cống, nắp ga, trạm bơm, hệ thống thoát nước, nạo vét
   • Đơn vị ứng phó: đội ứng phó, công nhân thoát nước, CSGT, chính quyền

2. "opinion" — cụm từ mô tả trạng thái hoặc đánh giá về aspect ("ngập sâu", "bì bõm lội qua", "chết máy hàng loạt", "nước đã rút hết", "thông thoáng", "làm việc rất nhanh").

3. "polarity" — thái độ của NGƯỜI VIẾT đối với aspect, CHỈ CHỌN 1 nhãn:
   • "NEG": phàn nàn, khó chịu, lo lắng, chỉ trích
   • "POS": khen ngợi, hài lòng, hoặc tả tình trạng đã khắc phục (hết ngập, nước rút, khô ráo)
   • "NEU": tường thuật khách quan, số liệu đo đạc, câu hỏi, dự báo — không khen không chê
   QUYẾT ĐỊNH: câu có đánh giá/cảm xúc rõ ràng → chọn theo sắc thái; câu chỉ tường thuật hoặc nêu số liệu → NEU. Polarity KHÔNG phụ thuộc việc có ngập hay không: "ngập khoảng 30cm" là NEU; "ngập kinh khủng chưa từng thấy" là NEG.

QUY TẮC BẮT BUỘC:
• aspect và opinion PHẢI là chuỗi nguyên văn sao chép từ câu đầu vào. TUYỆT ĐỐI KHÔNG sửa chính tả, KHÔNG bỏ dấu, KHÔNG chuẩn hóa teencode ("hẩm chui" giữ nguyên, "Q7" giữ nguyên, "kinh khũng" giữ nguyên).
• Cắt giới từ thừa ở đầu span ("ở", "tại", "đoạn") và vị từ thừa ở đuôi ("xảy ra", "mới không còn").
• KHÔNG gán xe cộ/phương tiện làm aspect — quy về tên đường nơi xe gặp nạn.
• Nếu cả câu chỉ có emoji biểu thị thái độ ("Hầm An Phú 😭😭"), emoji đó chính là opinion.
• Trả về ĐÚNG MỘT MẢNG JSON, không bọc khung ```json```, không giải thích:
  [{"aspect": "...", "opinion": "...", "polarity": "NEG"|"POS"|"NEU"}]
• Không tìm thấy bộ ba hợp lệ nào → trả về: []"""

# ---------------------------------------------------------------------------
# OUTPUT PARSER
# ---------------------------------------------------------------------------
def parse_llm_triplets(raw_text: str) -> List[Tuple[str, str, str]]:
    triplets = []
    if not raw_text or not raw_text.strip():
        return triplets

    cleaned = raw_text.strip()
    # Remove markdown code block markers
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE).strip()

    # 1. Try JSON Array parsing
    json_match = re.search(r"\[\s*\{.*?\}\s*\]", cleaned, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(0))
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict):
                        asp = str(item.get("aspect", "")).strip()
                        opi = str(item.get("opinion", "")).strip()
                        pol = str(item.get("polarity", "NEG")).strip().upper()
                        if pol not in ["POS", "NEG", "NEU"]:
                            pol = "NEG"
                        if asp and opi:
                            triplets.append((asp, opi, pol))
                return triplets
        except Exception:
            pass

    # 2. Fallback: Parse line-by-line objects
    obj_matches = re.findall(r"\{\s*\"aspect\"\s*:\s*\"(.*?)\"\s*,\s*\"opinion\"\s*:\s*\"(.*?)\"\s*,\s*\"polarity\"\s*:\s*\"(.*?)\"\s*\}", cleaned, re.DOTALL)
    if obj_matches:
        for asp, opi, pol in obj_matches:
            pol_clean = pol.strip().upper()
            if pol_clean not in ["POS", "NEG", "NEU"]:
                pol_clean = "NEG"
            if asp.strip() and opi.strip():
                triplets.append((asp.strip(), opi.strip(), pol_clean))
        if triplets:
            return triplets

    # 3. Fallback: Tuple regex format: (aspect | opinion | polarity)
    tuple_matches = re.findall(r"\(\s*([^|,\)]+?)\s*[|,]\s*([^|,\)]+?)\s*[|,]\s*(POS|NEG|NEU)\s*\)", cleaned, re.IGNORECASE)
    for asp, opi, pol in tuple_matches:
        if asp.strip() and opi.strip():
            triplets.append((asp.strip(), opi.strip(), pol.strip().upper()))
    if triplets:
        return triplets

    # 4. Fallback: Tolerant regex (even if trailing brace or bracket is truncated)
    tolerant_matches = re.findall(r"\"aspect\"\s*:\s*\"(.*?)\"\s*,\s*\"opinion\"\s*:\s*\"(.*?)\"\s*,\s*\"polarity\"\s*:\s*\"(.*?)\"", cleaned, re.DOTALL)
    for asp, opi, pol in tolerant_matches:
        pol_clean = pol.strip().upper()
        if pol_clean not in ["POS", "NEG", "NEU"]:
            pol_clean = "NEG"
        if asp.strip() and opi.strip():
            triplets.append((asp.strip(), opi.strip(), pol_clean))

    return triplets


# ---------------------------------------------------------------------------
# METRICS COMPUTATION (ACADEMIC STANDARD MATCHING REPO BENCHMARK)
# ---------------------------------------------------------------------------
def prf(gold: int, pred: int, correct: int) -> Tuple[float, float, float]:
    p = (correct / pred * 100) if pred > 0 else 0.0
    r = (correct / gold * 100) if gold > 0 else 0.0
    f = (2 * p * r / (p + r)) if (p + r) > 0 else 0.0
    return round(p, 2), round(r, 2), round(f, 2)


def evaluate_predictions(gold_items: List[Dict[str, Any]], predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
    n_gold_triplets, n_pred_triplets, n_correct_triplets = 0, 0, 0
    n_gold_aspects, n_pred_aspects, n_correct_aspects = 0, 0, 0
    n_gold_opinions, n_pred_opinions, n_correct_opinions = 0, 0, 0

    pol_stats = {
        "NEG": {"gold": 0, "pred": 0, "correct": 0},
        "POS": {"gold": 0, "pred": 0, "correct": 0},
        "NEU": {"gold": 0, "pred": 0, "correct": 0}
    }

    pred_map = {p["id"]: p for p in predictions}

    for item in gold_items:
        gold_triplets = set(
            (t["aspect"].strip().lower(), t["opinion"].strip().lower(), t["polarity"].strip().upper())
            for t in item.get("aste_triplets", [])
        )
        gold_aspects = set(t[0] for t in gold_triplets)
        gold_opinions = set(t[1] for t in gold_triplets)

        pred_entry = pred_map.get(item["id"], {})
        pred_triplets_raw = pred_entry.get("predicted_triplets", [])
        pred_triplets = set(
            (t[0].strip().lower(), t[1].strip().lower(), t[2].strip().upper())
            for t in pred_triplets_raw
        )
        pred_aspects = set(t[0] for t in pred_triplets)
        pred_opinions = set(t[1] for t in pred_triplets)

        n_gold_triplets += len(gold_triplets)
        n_pred_triplets += len(pred_triplets)
        correct_triplets = gold_triplets & pred_triplets
        n_correct_triplets += len(correct_triplets)

        n_gold_aspects += len(gold_aspects)
        n_pred_aspects += len(pred_aspects)
        n_correct_aspects += len(gold_aspects & pred_aspects)

        n_gold_opinions += len(gold_opinions)
        n_pred_opinions += len(pred_opinions)
        n_correct_opinions += len(gold_opinions & pred_opinions)

        for g in gold_triplets:
            if g[2] in pol_stats:
                pol_stats[g[2]]["gold"] += 1
        for p in pred_triplets:
            if p[2] in pol_stats:
                pol_stats[p[2]]["pred"] += 1
        for c in correct_triplets:
            if c[2] in pol_stats:
                pol_stats[c[2]]["correct"] += 1

    t_p, t_r, t_f1 = prf(n_gold_triplets, n_pred_triplets, n_correct_triplets)
    a_p, a_r, a_f1 = prf(n_gold_aspects, n_pred_aspects, n_correct_aspects)
    o_p, o_r, o_f1 = prf(n_gold_opinions, n_pred_opinions, n_correct_opinions)

    polarity_results = {}
    macro_f1_sum = 0.0
    for p_name, counts in pol_stats.items():
        p, r, f = prf(counts["gold"], counts["pred"], counts["correct"])
        polarity_results[p_name] = {
            "Precision": p,
            "Recall": r,
            "F1": f,
            "Gold": counts["gold"],
            "Pred": counts["pred"],
            "Correct": counts["correct"]
        }
        macro_f1_sum += f

    macro_pol_f1 = round(macro_f1_sum / len(pol_stats), 2)

    return {
        "Triplet_Strict_Match": {
            "Precision": t_p,
            "Recall": t_r,
            "F1": t_f1,
            "Gold": n_gold_triplets,
            "Pred": n_pred_triplets,
            "Correct": n_correct_triplets
        },
        "Aspect_Span": {
            "Precision": a_p,
            "Recall": a_r,
            "F1": a_f1
        },
        "Opinion_Span": {
            "Precision": o_p,
            "Recall": o_r,
            "F1": o_f1
        },
        "Polarity_Per_Class": polarity_results,
        "Macro_Polarity_F1": macro_pol_f1
    }


# ---------------------------------------------------------------------------
# API WORKER
# ---------------------------------------------------------------------------
def call_llm_single(cfg: Dict[str, Any], item: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
    text = item["content"]["text"]
    item_id = item["id"]

    prompt_to_use = ASTE_SYSTEM_PROMPT
    if "qwen" in cfg["model_id"]:
        prompt_to_use += "\n\nLƯU Ý: Suy nghĩ cực kỳ ngắn gọn (dưới 15 từ) rồi xuất ngay mảng JSON kết quả."

    payload = {
        "model": cfg["model_id"],
        "messages": [
            {"role": "system", "content": prompt_to_use},
            {"role": "user", "content": text}
        ],
        "temperature": cfg["temperature"],
        "max_tokens": cfg["max_tokens"]
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    raw_response = ""
    reasoning_text = ""
    duration = 0.0

    for attempt in range(max_retries):
        t0 = time.time()
        try:
            resp = requests.post(
                cfg["url"],
                json=payload,
                headers=headers,
                verify=False,
                timeout=cfg["timeout"]
            )
            duration = time.time() - t0
            if resp.status_code == 200:
                data = resp.json()
                msg = data["choices"][0]["message"]
                raw_response = msg.get("content") or ""
                reasoning_text = msg.get("reasoning") or ""
                break
            else:
                time.sleep(1.0 * (attempt + 1))
        except Exception as e:
            duration = time.time() - t0
            time.sleep(1.0 * (attempt + 1))

    if not raw_response.strip() and reasoning_text:
        raw_response = reasoning_text

    predicted_triplets = parse_llm_triplets(raw_response)
    if not predicted_triplets and reasoning_text:
        predicted_triplets = parse_llm_triplets(reasoning_text)

    return {
        "id": item_id,
        "input_text": text,
        "raw_response": raw_response,
        "reasoning": reasoning_text,
        "predicted_triplets": predicted_triplets,
        "duration_sec": round(duration, 3)
    }


# ---------------------------------------------------------------------------
# BENCHMARK RUNNER
# ---------------------------------------------------------------------------
def run_llm_benchmark(model_key: str, workers: int = 8, force: bool = False):
    cfg = LLM_CONFIGS[model_key]
    print("=" * 80)
    print(f"🚀 BẮT ĐẦU BENCHMARK LLM: {cfg['display_name']} ({cfg['model_id']})")
    print(f"  • Endpoint URL : {cfg['url']}")
    print(f"  • Test Dataset : {TEST_FILE}")
    print(f"  • Concurrency  : {workers} workers")
    print(f"  • Force Re-run : {force}")
    print("=" * 80)

    with open(TEST_FILE, "r", encoding="utf-8") as f:
        test_items = json.load(f)

    report_dir = os.path.join(cfg["output_dir"], "test", "benchmark_reports")
    pred_dir = os.path.join(cfg["output_dir"], "test")
    os.makedirs(report_dir, exist_ok=True)
    os.makedirs(pred_dir, exist_ok=True)

    cache_file = os.path.join(pred_dir, "predictions.json")
    predictions = []
    cached_ids = set()

    # Load cache if available and not forced
    if force and os.path.exists(cache_file):
        print(f"[*] Force re-run được kích hoạt: Xóa bộ nhớ đệm cũ {cache_file} để đánh giá lại toàn bộ với System Prompt mới.")
        os.remove(cache_file)
    elif os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                predictions = json.load(f)
            cached_ids = set(p["id"] for p in predictions)
            print(f"[i] Đã nạp {len(cached_ids)} kết quả từ bộ nhớ đệm cache ({cache_file}).")
        except Exception:
            predictions = []

    remaining_items = [item for item in test_items if item["id"] not in cached_ids]
    print(f"[*] Cần xử lý mới: {len(remaining_items)} / {len(test_items)} mẫu.")

    t_start = time.time()
    if remaining_items:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_item = {
                executor.submit(call_llm_single, cfg, item): item
                for item in remaining_items
            }

            done_count = 0
            for future in concurrent.futures.as_completed(future_to_item):
                res = future.result()
                predictions.append(res)
                done_count += 1
                if done_count % 25 == 0 or done_count == len(remaining_items):
                    elapsed = time.time() - t_start
                    speed = done_count / elapsed if elapsed > 0 else 0
                    print(f"  • Tiến độ: {done_count}/{len(remaining_items)} ({done_count/len(remaining_items)*100:.1f}%) | Tốc độ: {speed:.2f} mẫu/s")

                    # Periodically save cache
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(predictions, f, indent=2, ensure_ascii=False)

    total_eval_time = round(time.time() - t_start, 2)
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=2, ensure_ascii=False)
    print(f"[+] Toàn bộ {len(predictions)} dự đoán đã được lưu tại: {cache_file}")

    # Compute academic benchmark metrics
    metrics = evaluate_predictions(test_items, predictions)
    metrics["model_name"] = cfg["display_name"]
    metrics["model_id"] = cfg["model_id"]
    metrics["Evaluation_Time_Seconds"] = total_eval_time
    metrics["Samples_Per_Second"] = round(len(test_items) / total_eval_time, 2) if total_eval_time > 0 else 0.0

    report_file = os.path.join(report_dir, "test_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"[+] Báo cáo khoa học JSON đã lưu: {report_file}")

    print("\n" + "=" * 75)
    print(f"📊 BẢNG KẾT QUẢ THỰC NGHIỆM ĐÁNH GIÁ ({cfg['display_name']})")
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate LLMs on ASTE Test Split")
    parser.add_argument("--model", type=str, choices=["gemma", "qwen", "all"], default="all",
                        help="Which LLM to benchmark ('gemma', 'qwen', or 'all')")
    parser.add_argument("--workers", type=int, default=8, help="Number of concurrent workers")
    parser.add_argument("--force", action="store_true", help="Force re-evaluation and overwrite old cache")
    args = parser.parse_args()

    if args.model in ["gemma", "all"]:
        run_llm_benchmark("gemma", workers=args.workers, force=args.force)
    if args.model in ["qwen", "all"]:
        run_llm_benchmark("qwen", workers=args.workers, force=args.force)
