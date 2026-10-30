"""
AI/bartpho/syllable_base/test/inference.py
--------------------------------------------------------------------------------
Inference Module for fine-tuned BARTpho-syllable-base Generative ASTE Model.
Transforms raw input texts into structured Aspect-Sentiment-Opinion Triplets:
[{'aspect': '...', 'opinion': '...', 'polarity': 'POS|NEG|NEU'}]

Supports both SemEval v2 index format and linearized word format.
"""

import os
import sys
import json
import re
import ast
import unicodedata
from typing import List, Dict, Any, Optional, Tuple

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SEMEVAL_DIR = os.path.dirname(SCRIPT_DIR)
DEFAULT_CHECKPOINT_DIR = os.path.join(SEMEVAL_DIR, "finetune", "checkpoints", "best_aste_model")


def parse_semeval_v2_string(text: str) -> List[Tuple[Tuple[int, ...], Tuple[int, ...], str]]:
    """Parses SemEval v2 Seq2Seq output string into list of index-based triplets."""
    if not text or text.strip().lower() in ["[]", "none", ""]:
        return []
    text_clean = text.strip()
    try:
        val = ast.literal_eval(text_clean)
        if isinstance(val, list):
            res = []
            for item in val:
                if isinstance(item, (tuple, list)) and len(item) == 3:
                    a_idx, o_idx, pol = item
                    if isinstance(a_idx, (list, tuple)) and isinstance(o_idx, (list, tuple)):
                        a_clean = tuple(sorted(int(x) for x in a_idx))
                        o_clean = tuple(sorted(int(x) for x in o_idx))
                        if a_clean and o_clean:
                            res.append((a_clean, o_clean, str(pol).upper()))
            return res
    except Exception:
        pass

    triplets = []
    pattern = re.compile(r'\(\s*\[([0-9,\s]*)\]\s*,\s*\[([0-9,\s]*)\]\s*,\s*[\x27\x22](POS|NEG|NEU)[\x27\x22]\s*\)')
    for m in pattern.finditer(text_clean):
        a_raw, o_raw, pol = m.group(1), m.group(2), m.group(3)
        a_idx = [int(x.strip()) for x in a_raw.split(',') if x.strip().isdigit()]
        o_idx = [int(x.strip()) for x in o_raw.split(',') if x.strip().isdigit()]
        if a_idx and o_idx:
            triplets.append((tuple(sorted(a_idx)), tuple(sorted(o_idx)), pol.upper()))
    return triplets


def parse_triplets_from_string(text: str) -> List[Dict[str, str]]:
    """Parses linearized target text into structured triplets."""
    if not text or text.strip().lower() in ["none", ""]:
        return []

    triplets = []
    raw_items = [x.strip() for x in text.split(";") if x.strip()]
    if not raw_items:
        raw_items = re.findall(r'\((.*?)\)', text)

    seen = set()
    for raw_item in raw_items:
        clean_item = raw_item.strip()
        if clean_item.startswith("(") and clean_item.endswith(")"):
            clean_item = clean_item[1:-1].strip()

        parts = [p.strip() for p in clean_item.split("|")]
        if len(parts) >= 3:
            asp = unicodedata.normalize('NFC', parts[0]).strip()
            opi = unicodedata.normalize('NFC', parts[1]).strip()
            pol = parts[2].strip().upper()
            if pol not in ["POS", "NEG", "NEU"]:
                pol = "NEG"
            key = (asp.lower(), opi.lower(), pol)
            if asp and opi and key not in seen:
                seen.add(key)
                triplets.append({
                    "aspect": asp,
                    "opinion": opi,
                    "polarity": pol
                })
        elif len(parts) == 2:
            asp = unicodedata.normalize('NFC', parts[0]).strip()
            opi = unicodedata.normalize('NFC', parts[1]).strip()
            key = (asp.lower(), opi.lower(), "NEG")
            if asp and opi and key not in seen:
                seen.add(key)
                triplets.append({
                    "aspect": asp,
                    "opinion": opi,
                    "polarity": "NEG"
                })

    return triplets


class ASTEPredictor:
    """Predictor class wrapping fine-tuned BARTpho-syllable-base ASTE Seq2Seq model."""
    def __init__(self, checkpoint_dir: str = DEFAULT_CHECKPOINT_DIR, device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[*] Đang tải checkpoint BARTpho Syllable ASTE từ: {checkpoint_dir} (Thiết bị: {self.device})...")

        if not os.path.exists(checkpoint_dir):
            raise FileNotFoundError(f"Checkpoint không tồn tại tại: {checkpoint_dir}")

        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint_dir)
        self.model.to(self.device)
        self.model.eval()
        print("[+] Nạp mô hình BARTpho Syllable ASTE thành công!")

    def predict(self, text: str, max_length: int = 160, num_beams: int = 4) -> Dict[str, Any]:
        if not text or len(text.strip()) == 0:
            return {"input_text": "", "raw_output": "[]", "triplets": [], "semeval_triplets": []}

        clean_input = unicodedata.normalize('NFC', text).strip()
        inputs = self.tokenizer(
            clean_input,
            return_tensors="pt",
            max_length=256,
            truncation=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=num_beams,
                early_stopping=True,
                no_repeat_ngram_size=3
            )

        raw_str = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

        # Check if output is SemEval v2 index format: [([0, 1], [4], 'POS')]
        semeval_triplets = []
        if raw_str.startswith("[") or "([0" in raw_str or "([1" in raw_str or "([2" in raw_str:
            idx_triplets = parse_semeval_v2_string(raw_str)
            semeval_triplets = idx_triplets
            # Map index spans back to tokens/words
            tokens = re.findall(r'\w+|[^\w\s]', clean_input, re.UNICODE)
            triplets = []
            seen = set()
            for a_idx, o_idx, pol in idx_triplets:
                asp_toks = [tokens[i] for i in a_idx if i < len(tokens)]
                opn_toks = [tokens[i] for i in o_idx if i < len(tokens)]
                asp = " ".join(asp_toks).strip()
                opn = " ".join(opn_toks).strip()
                if asp and opn:
                    key = (asp.lower(), opn.lower(), pol.upper())
                    if key not in seen:
                        seen.add(key)
                        triplets.append({"aspect": asp, "opinion": opn, "polarity": pol.upper()})
        else:
            triplets = parse_triplets_from_string(raw_str)

        return {
            "input_text": clean_input,
            "raw_output": raw_str,
            "triplets": triplets,
            "semeval_triplets": semeval_triplets
        }


def main():
    test_cases = [
        "Đường Võ Văn Ngân nước chảy như thác đổ , nhiều xe máy chết máy dắt bộ bì bõm .",
        "Mưa lớn khiến đường Nguyễn Hữu Cảnh ngập sâu lút nửa bánh xe , giao thông tê liệt .",
        "Đến chiều tối nước đã rút hết trên đường Tân Kỳ Tân Quý , xe cộ đi lại thông thoáng .",
        "Hôm nay trời nắng đẹp , không có mưa ngập ở quận 1 ."
    ]

    predictor = ASTEPredictor()
    for tc in test_cases:
        res = predictor.predict(tc)
        print("\nInput      :", res["input_text"])
        print("Raw Output :", res["raw_output"])
        print("Triplets   :", res["triplets"])


if __name__ == "__main__":
    main()
