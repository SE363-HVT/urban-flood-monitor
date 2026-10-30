#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI/adapters/convert_to_semeval_v2.py
--------------------------------------------------------------------------------
Dataset Adapter: Converts canonical HCMC Flood ASTE v3 dataset splits
(data/processed/splits/{train,dev,test}.json) into standard SemEval v2 ASTE format:

Format:
  <sentence_tokens>####[([aspect_indices], [opinion_indices], 'POLARITY'), ...]

Example:
  Boot time is super fast , around anywhere from 35 seconds to 1 minute .####[([0, 1], [4], 'POS')]
  Đáng chú ý , triều cường trên sông Sài Gòn đang ở mức cao .####[([7, 8, 9], [10, 11, 12, 13], 'NEU'), ([4, 5], [10, 11, 12, 13], 'NEU')]

Outputs:
  - Text files: data/semeval_v2/{train.txt, dev.txt, test.txt}
  - JSON files: data/semeval_v2/{train.json, dev.json, test.json}
"""

import os
import sys
import json
import re
import unicodedata
from typing import List, Tuple, Dict, Any, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(AI_DIR)

DEFAULT_INPUT_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "splits")
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "semeval_v2")


def char_span_tokenize(text: str) -> Tuple[List[str], List[Tuple[int, int]], str]:
    """
    Tokenizes text separating punctuation into individual tokens while preserving words.
    Returns:
      tokens: List of token strings
      spans: List of (char_start, char_end) tuples in text_nfc
      text_nfc: NFC-normalized text string
    """
    text_nfc = unicodedata.normalize('NFC', text)
    # Match alphanumeric words or single punctuation/special characters
    pattern = re.compile(r'\w+|[^\w\s]', re.UNICODE)
    tokens = []
    spans = []
    for m in pattern.finditer(text_nfc):
        tokens.append(m.group())
        spans.append((m.start(), m.end()))
    return tokens, spans, text_nfc


def align_phrase_to_tokens(
    text_nfc: str,
    phrase: str,
    token_spans: List[Tuple[int, int]],
    tokens: List[str]
) -> Optional[List[int]]:
    """
    Finds exact list of token indices for a subphrase in the sentence.
    Uses character-level overlap for 100% precision.
    """
    if not phrase:
        return None
    phrase_nfc = unicodedata.normalize('NFC', phrase).strip()
    if not phrase_nfc:
        return None

    idx = text_nfc.lower().find(phrase_nfc.lower())
    if idx == -1:
        return None
    c_start = idx
    c_end = idx + len(phrase_nfc)

    matched = []
    for i, (ts, te) in enumerate(token_spans):
        if max(ts, c_start) < min(te, c_end):
            matched.append(i)
    return matched if matched else None


def convert_split(
    input_json_path: str,
    output_txt_path: str,
    output_json_path: str
) -> Dict[str, Any]:
    """Converts a single split file into SemEval v2 .txt and .json formats."""
    with open(input_json_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    txt_lines = []
    json_records = []
    total_triplets = 0
    aligned_triplets = 0

    for idx, item in enumerate(samples):
        text = item.get("content", {}).get("text", "").strip()
        tokens, spans, text_nfc = char_span_tokenize(text)
        sentence_str = " ".join(tokens)

        gold_triplets = item.get("aste_triplets", [])
        semeval_triplets = []
        structured_triplets = []

        for t in gold_triplets:
            total_triplets += 1
            asp = t.get("aspect", "")
            opn = t.get("opinion", "")
            pol = t.get("polarity", "NEG").strip().upper()
            if pol not in ["POS", "NEG", "NEU"]:
                pol = "NEG"

            a_indices = align_phrase_to_tokens(text_nfc, asp, spans, tokens)
            o_indices = align_phrase_to_tokens(text_nfc, opn, spans, tokens)

            if a_indices and o_indices:
                aligned_triplets += 1
                semeval_triplets.append((a_indices, o_indices, pol))
                structured_triplets.append({
                    "aspect_indices": a_indices,
                    "opinion_indices": o_indices,
                    "aspect_text": " ".join([tokens[i] for i in a_indices]),
                    "opinion_text": " ".join([tokens[i] for i in o_indices]),
                    "polarity": pol
                })

        # SemEval v2 line representation: sentence####[([a_idxs], [o_idxs], 'POL'), ...]
        target_str = str(semeval_triplets)
        txt_line = f"{sentence_str}####{target_str}"
        txt_lines.append(txt_line)

        json_records.append({
            "id": item.get("id", f"sample_{idx:05d}"),
            "seq_id": item.get("seq_id", idx + 1),
            "tokens": tokens,
            "sentence": sentence_str,
            "target_text": target_str,
            "semeval_triplets": semeval_triplets,
            "structured_triplets": structured_triplets,
            "raw_gold_triplets": gold_triplets
        })

    os.makedirs(os.path.dirname(output_txt_path), exist_ok=True)
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines) + "\n")

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(json_records, f, ensure_ascii=False, indent=2)

    stats = {
        "total_samples": len(samples),
        "total_gold_triplets": total_triplets,
        "aligned_triplets": aligned_triplets,
        "alignment_rate_pct": round(aligned_triplets / max(1, total_triplets) * 100, 2),
        "txt_output": output_txt_path,
        "json_output": output_json_path
    }
    return stats


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Convert HCMC Flood ASTE splits to SemEval v2 format")
    parser.add_argument("--input_dir", type=str, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output_dir", type=str, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    splits = [
        ("train", "train.json", "train.txt", "train.json"),
        ("dev", "dev.json", "dev.txt", "dev.json"),
        ("test", "test.json", "test.txt", "test.json")
    ]

    print("=" * 75)
    print("🔄 BẮT ĐẦU CHUYỂN ĐỔI DATASET SANG CHUẨN SEMEVAL V2")
    print(f"  • Thư mục nguồn: {args.input_dir}")
    print(f"  • Thư mục đích  : {args.output_dir}")
    print("=" * 75)

    summary = {}
    for split_name, in_file, out_txt, out_json in splits:
        in_p = os.path.join(args.input_dir, in_file)
        out_t = os.path.join(args.output_dir, out_txt)
        out_j = os.path.join(args.output_dir, out_json)

        res = convert_split(in_p, out_t, out_j)
        summary[split_name] = res
        print(f"  • [{split_name.upper():<5}] Mẫu: {res['total_samples']:>4} | "
              f"Triplets: {res['aligned_triplets']:>4}/{res['total_gold_triplets']:>4} "
              f"({res['alignment_rate_pct']:>5.2f}%) -> {out_txt}")

    with open(os.path.join(args.output_dir, "conversion_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("=" * 75)
    print("✅ HOÀN TẤT CHUYỂN ĐỔI CHUẨN SEMEVAL V2!")
    print("=" * 75)


if __name__ == "__main__":
    main()
