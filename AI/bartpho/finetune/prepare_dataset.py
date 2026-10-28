"""
AI/bartpho/finetune/prepare_dataset.py
--------------------------------------------------------------------------------
Generative ASTE Dataset Preparation for BARTpho Models:
1. Reads canonical splits from data/processed/splits/ (train.json, dev.json, test.json).
2. Normalizes input and generates linearized target strings:
   Target: (Aspect | Opinion | Polarity) ; (Aspect | Opinion | Polarity) ...
   or "None" if no triplets exist in the sample.
3. Saves output to AI/bartpho/data/{train.json, val.json, test.json}.
"""

import os
import sys
import json
import unicodedata
from typing import List, Dict, Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Locate RadiNet project root
BARTPHO_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) in ["finetune", "word_base"] else SCRIPT_DIR
if os.path.basename(BARTPHO_DIR) == "word_base":
    BARTPHO_DIR = os.path.dirname(BARTPHO_DIR)
AI_DIR = os.path.dirname(BARTPHO_DIR)
PROJECT_ROOT = os.path.dirname(AI_DIR)

DATA_SPLITS_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "splits")
OUTPUT_DIR = os.path.join(BARTPHO_DIR, "data")


def format_triplets_to_target(triplets: List[Dict[str, Any]]) -> str:
    """
    Linearize a list of ASTE triplets into a structured sequence string:
    (Aspect | Opinion | Polarity) ; (Aspect | Opinion | Polarity)
    """
    if not triplets:
        return "None"

    formatted_items = []
    seen = set()

    for t in triplets:
        asp = unicodedata.normalize('NFC', t.get("aspect", "")).strip()
        opi = unicodedata.normalize('NFC', t.get("opinion", "")).strip()
        pol = t.get("polarity", "NEG").strip().upper()
        if pol not in ["POS", "NEG", "NEU"]:
            pol = "NEG"

        if asp and opi:
            key = (asp.lower(), opi.lower(), pol)
            if key not in seen:
                seen.add(key)
                formatted_items.append(f"({asp} | {opi} | {pol})")

    if not formatted_items:
        return "None"
    return " ; ".join(formatted_items)


def process_split_file(input_path: str, output_path: str, split_name: str) -> Dict[str, Any]:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Missing split file: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    processed_samples = []
    total_triplets = 0
    empty_samples = 0

    for idx, item in enumerate(raw_items):
        text = unicodedata.normalize('NFC', item.get("content", {}).get("text", "")).strip()
        triplets = item.get("aste_triplets", [])

        target_str = format_triplets_to_target(triplets)
        if target_str == "None":
            empty_samples += 1

        seq_id = item.get("seq_id", idx + 1)
        clean_raw_triplets = []
        for t in triplets:
            clean_raw_triplets.append({
                "aspect": unicodedata.normalize('NFC', t.get("aspect", "")).strip(),
                "opinion": unicodedata.normalize('NFC', t.get("opinion", "")).strip(),
                "polarity": t.get("polarity", "NEG").strip().upper()
            })

        processed_samples.append({
            "id": item.get("id", f"sample_{seq_id:04d}"),
            "seq_id": seq_id,
            "original_id": item.get("id"),
            "platform": item.get("source", {}).get("platform", "unknown"),
            "input_text": text,
            "target_text": target_str,
            "raw_triplets": clean_raw_triplets
        })
        total_triplets += len(clean_raw_triplets)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed_samples, f, ensure_ascii=False, indent=2)

    stats = {
        "split": split_name,
        "total_samples": len(processed_samples),
        "total_triplets": total_triplets,
        "empty_triplet_samples": empty_samples,
        "avg_triplets_per_sample": round(total_triplets / max(1, len(processed_samples)), 2),
        "output_file": output_path
    }
    return stats


def main():
    print("=" * 70)
    print("CHUẨN BỊ DỮ LIỆU HUẤN LUYỆN GENERATIVE ASTE CHO BARTPHO")
    print(f"[*] Thư mục nguồn (splits chuẩn V3): {DATA_SPLITS_DIR}")
    print(f"[*] Thư mục đích                     : {OUTPUT_DIR}")
    print("=" * 70)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    mappings = [
        ("train.json", "train.json", "train"),
        ("dev.json", "val.json", "val"),
        ("test.json", "test.json", "test")
    ]

    for in_file, out_file, split_name in mappings:
        in_path = os.path.join(DATA_SPLITS_DIR, in_file)
        out_path = os.path.join(OUTPUT_DIR, out_file)
        stats = process_split_file(in_path, out_path, split_name)
        print(f"[+] Tập {stats['split'].upper():<6}: {stats['total_samples']:,} mẫu | "
              f"{stats['total_triplets']:,} bộ ba triplets | "
              f"{stats['empty_triplet_samples']} mẫu không có triplet | "
              f"Lưu vào -> {out_file}")

    print("=" * 70)
    print("Hoàn tất chuẩn bị dữ liệu Generative ASTE cho BARTpho!")


if __name__ == "__main__":
    main()
