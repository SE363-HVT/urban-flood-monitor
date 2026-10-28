"""
AI/bartpho/word_base/test/inference.py
--------------------------------------------------------------------------------
Inference Module for fine-tuned BARTpho Generative ASTE Model.
Transforms raw input texts into structured Aspect-Sentiment-Opinion Triplets:
[{'aspect': '...', 'opinion': '...', 'polarity': 'POS|NEG|NEU'}]
"""

import os
import sys
import json
import re
import unicodedata
from typing import List, Dict, Any, Optional

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORD_BASE_DIR = os.path.dirname(SCRIPT_DIR)
DEFAULT_CHECKPOINT_DIR = os.path.join(WORD_BASE_DIR, "finetune", "checkpoints", "best_aste_model")


def parse_triplets_from_string(text: str) -> List[Dict[str, str]]:
    """
    Parses linearized target text into structured triplets:
    Input: "(Võ Văn Ngân | ngập lút bánh xe | NEG) ; (phương tiện | chết máy | NEG)"
    Output: [{'aspect': 'Võ Văn Ngân', 'opinion': 'ngập lút bánh xe', 'polarity': 'NEG'}, ...]
    """
    if not text or text.strip().lower() in ["none", ""]:
        return []

    triplets = []
    # Match any content within parentheses
    items = re.findall(r'\((.*?)\)', text)
    if not items:
        # Fallback if model didn't enclose with parentheses
        items = text.split(";")

    seen = set()

    for item in items:
        parts = [p.strip() for p in item.split("|")]
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
    """Predictor class wrapping fine-tuned BARTpho ASTE Seq2Seq model."""
    def __init__(self, checkpoint_dir: str = DEFAULT_CHECKPOINT_DIR, device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[*] Đang tải checkpoint BARTpho ASTE từ: {checkpoint_dir} (Thiết bị: {self.device})...")

        if not os.path.exists(checkpoint_dir):
            raise FileNotFoundError(f"Checkpoint không tồn tại tại: {checkpoint_dir}")

        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint_dir)
        self.model.to(self.device)
        self.model.eval()
        print("[+] Nạp mô hình BARTpho ASTE thành công!")

    def predict(self, text: str, max_length: int = 80, num_beams: int = 4) -> Dict[str, Any]:
        """Generate structured triplets for an input sentence."""
        if not text or len(text.strip()) == 0:
            return {"input_text": "", "raw_output": "None", "triplets": []}

        clean_input = unicodedata.normalize('NFC', text).strip()
        inputs = self.tokenizer(
            clean_input,
            return_tensors="pt",
            max_length=160,
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
        triplets = parse_triplets_from_string(raw_str)

        return {
            "input_text": clean_input,
            "raw_output": raw_str,
            "triplets": triplets
        }


def main():
    test_cases = [
        "Đường Võ Văn Ngân nước chảy như thác đổ, nhiều xe máy chết máy dắt bộ bì bõm.",
        "Mưa lớn khiến đường Nguyễn Hữu Cảnh ngập sâu lút nửa bánh xe, giao thông tê liệt.",
        "Đến chiều tối nước đã rút hết trên đường Tân Kỳ Tân Quý, xe cộ đi lại thông thoáng.",
        "Hôm nay trời nắng đẹp, không có mưa ngập ở quận 1."
    ]

    try:
        predictor = ASTEPredictor()
    except Exception as e:
        print(f"[!] Lỗi khi nạp predictor: {e}")
        return

    print("=" * 75)
    print("DEMO INFERENCE GENERATIVE ASTE (BARTPHO-WORD-BASE)")
    print("=" * 75)

    for idx, sentence in enumerate(test_cases, 1):
        res = predictor.predict(sentence)
        print(f"[{idx}] Câu gốc : \"{res['input_text']}\"")
        print(f"    Chuỗi sinh: {res['raw_output']}")
        print(f"    Triplets  : {json.dumps(res['triplets'], ensure_ascii=False)}")
        print("-" * 75)


if __name__ == "__main__":
    main()
