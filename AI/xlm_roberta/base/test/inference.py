#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI/xlm_roberta/base/test/inference.py
--------------------------------------------------------------------------------
Inference Module for fine-tuned XLM-RoBERTa ASTE Model.
Extracts structured triplets: [{'aspect': '...', 'opinion': '...', 'polarity': '...'}]
"""

import os
import sys
import json
import torch
from transformers import AutoTokenizer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
XLM_DIR = os.path.dirname(BASE_DIR)
AI_DIR = os.path.dirname(XLM_DIR)
PROJECT_ROOT = os.path.dirname(AI_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.train_xlm_roberta_aste import (
    XLMRobertaForASTE,
    extract_spans_from_bio
)


class XLMRobertaASTEPredictor:
    def __init__(self, checkpoint_dir: str = None, device: str = None):
        self.device = torch.device(device if device else ("cuda" if torch.cuda.is_available() else "cpu"))
        if checkpoint_dir is None:
            checkpoint_dir = os.path.join(BASE_DIR, "finetune", "checkpoints")

        ckpt_path = os.path.join(checkpoint_dir, "best_xlm_roberta_aste.pt")
        if not os.path.exists(ckpt_path):
            raise FileNotFoundError(f"Missing checkpoint: {ckpt_path}")

        checkpoint = torch.load(ckpt_path, map_location=self.device, weights_only=False)
        model_name = checkpoint.get("model_name", "xlm-roberta-base")
        params = checkpoint.get("params", {})
        dropout = params.get("dropout", 0.15)

        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir if os.path.exists(os.path.join(checkpoint_dir, "tokenizer_config.json")) else model_name)
        self.model = XLMRobertaForASTE(model_name=model_name, dropout_rate=dropout).to(self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()

    def predict(self, text: str) -> dict:
        if not text or not text.strip():
            return {"input_text": "", "triplets": []}

        encoding = self.tokenizer(text, return_offsets_mapping=True, truncation=True, max_length=160, return_tensors="pt")
        input_ids = encoding["input_ids"].to(self.device)
        attention_mask = encoding["attention_mask"].to(self.device)
        offsets = encoding["offset_mapping"][0].cpu().tolist()

        with torch.no_grad():
            outputs = self.model.encoder(input_ids=input_ids, attention_mask=attention_mask)
            seq_out = outputs.last_hidden_state
            cls_out = seq_out[:, 0, :]
            bio_logits = self.model.tag_classifier(seq_out)
            bio_preds = torch.argmax(bio_logits, dim=-1)[0].cpu().tolist()

            pred_asps, pred_opns = extract_spans_from_bio(bio_preds)
            pred_triplets = self.model.predict_spans_and_pairs(seq_out[0], cls_out[0], pred_asps, pred_opns)

        triplets = []
        for t in pred_triplets:
            as_idx, ae_idx = t["aspect_span"]
            os_idx, oe_idx = t["opinion_span"]

            if as_idx == 0 and ae_idx == 0:
                asp_str = "TP. Hồ Chí Minh"
            else:
                s_char = offsets[as_idx][0]
                e_char = offsets[ae_idx][1]
                asp_str = text[s_char:e_char].strip()

            s_char = offsets[os_idx][0]
            e_char = offsets[oe_idx][1]
            opn_str = text[s_char:e_char].strip()

            triplets.append({
                "aspect": asp_str,
                "opinion": opn_str,
                "polarity": t["polarity"]
            })

        return {"input_text": text, "triplets": triplets}


def main():
    test_cases = [
        "Đường Võ Văn Ngân nước chảy như thác đổ, nhiều xe máy chết máy dắt bộ bì bõm.",
        "Mưa lớn khiến đường Nguyễn Hữu Cảnh ngập sâu lút nửa bánh xe, giao thông tê liệt.",
        "Đến chiều tối nước đã rút hết trên đường Tân Kỳ Tân Quý, xe cộ đi lại thông thoáng.",
        "Hôm nay trời nắng đẹp, không có mưa ngập ở quận 1."
    ]

    try:
        predictor = XLMRobertaASTEPredictor()
    except Exception as e:
        print(f"[!] Lỗi khi nạp predictor: {e}")
        return

    print("=" * 70)
    print("DEMO INFERENCE ASTE TRÊN CÂU MẪU MẠNG XÃ HỘI (XLM-ROBERTA)")
    print("=" * 70)
    for idx, sentence in enumerate(test_cases, 1):
        res = predictor.predict(sentence)
        print(f"\n[{idx}] Câu gốc : \"{res['input_text']}\"")
        print(f"    Triplets  : {json.dumps(res['triplets'], ensure_ascii=False)}")


if __name__ == "__main__":
    main()
