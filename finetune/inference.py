"""
finetune/inference.py
Kịch bản kiểm thử dự đoán mô hình Generative ASTE trên văn bản ngập lụt mới:
- Tự động nạp checkpoint đã huấn luyện từ finetune/checkpoints/best_aste_model.
- Giải mã chuỗi sinh ra thành danh sách các bộ ba có cấu trúc:
  [{'aspect': '...', 'opinion': '...', 'polarity': '...'}]
- Sẵn sàng dùng trực tiếp trong pipeline RadiNet.
"""

import os
import sys
import json
import re
import unicodedata
from typing import List, Dict, Any, Optional

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CHECKPOINT_DIR = os.path.join(CURRENT_DIR, "checkpoints", "best_aste_model")


def parse_triplets_from_string(text: str) -> List[Dict[str, str]]:
    """
    Phân giải chuỗi văn bản mục tiêu thành danh sách bộ ba có cấu trúc:
    Input: "(Võ Văn Ngân | ngập lút bánh xe | NEG) ; (phương tiện giao thông | chết máy | NEG)"
    Output: [{'aspect': 'Võ Văn Ngân', 'opinion': 'ngập lút bánh xe', 'polarity': 'NEG'}, ...]
    """
    if not text or text.strip().lower() == "none":
        return []

    triplets = []
    # Tách các bộ ba ngăn cách bởi dấu chấm phẩy hoặc dấu ngoặc đóng
    items = re.findall(r'\((.*?)\)', text)
    if not items:
        # Dự phòng trường hợp không có ngoặc đơn
        items = text.split(";")

    for item in items:
        parts = [p.strip() for p in item.split("|")]
        if len(parts) >= 3:
            asp = unicodedata.normalize('NFC', parts[0])
            opi = unicodedata.normalize('NFC', parts[1])
            pol = parts[2].upper()
            if pol not in ["POS", "NEG", "NEU"]:
                pol = "NEG"
            triplets.append({
                "aspect": asp,
                "opinion": opi,
                "polarity": pol
            })
        elif len(parts) == 2:
            # Fallback nếu thiếu polarity
            asp = unicodedata.normalize('NFC', parts[0])
            opi = unicodedata.normalize('NFC', parts[1])
            triplets.append({
                "aspect": asp,
                "opinion": opi,
                "polarity": "NEG"
            })

    return triplets


class ASTEPredictor:
    """Class bọc mô hình phục vụ suy luận thời gian thực cho Pipeline RadiNet."""
    def __init__(self, checkpoint_dir: str = DEFAULT_CHECKPOINT_DIR, device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[*] Đang nạp mô hình Generative ASTE từ: {checkpoint_dir} (Thiết bị: {self.device})...")

        if not os.path.exists(checkpoint_dir):
            raise FileNotFoundError(
                f"Chưa tìm thấy checkpoint tại {checkpoint_dir}! "
                f"Vui lòng chạy 'python finetune/train_generative_aste.py' để huấn luyện trước."
            )

        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint_dir)
        self.model.to(self.device)
        self.model.eval()
        print("[+] Nạp mô hình ASTE thành công!")

    def predict(self, text: str, max_length: int = 128, num_beams: int = 4) -> Dict[str, Any]:
        """
        Dự đoán bộ ba cho một câu văn bản đầu vào.
        Trả về dictionary chứa chuỗi raw và danh sách triplets có cấu trúc.
        """
        if not text or len(text.strip()) == 0:
            return {"raw_output": "None", "triplets": []}

        clean_input = unicodedata.normalize('NFC', text).strip()
        inputs = self.tokenizer(clean_input, return_tensors="pt", max_length=256, truncation=True)
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


def demo_interactive():
    test_cases = [
        "Đường Võ Văn Ngân nước chảy như thác đổ, nhiều xe máy chết máy dắt bộ bì bõm.",
        "Mưa lớn khiến đường Nguyễn Hữu Cảnh ngập sâu lút nửa bánh xe, giao thông tê liệt.",
        "Đến chiều tối nước đã rút hết trên đường Tân Kỳ Tân Quý, xe cộ đi lại thông thoáng.",
        "Hôm nay trời nắng đẹp, không có mưa ngập ở quận 1."
    ]

    try:
        predictor = ASTEPredictor()
    except Exception as e:
        print(f"\n[!] Lưu ý: {e}")
        print("Kịch bản suy luận mẫu sẽ sẵn sàng sau khi bạn chạy xong train_generative_aste.py.")
        return

    print("\n" + "=" * 70)
    print("CHẠY THỬ NGHIỆM INFERENCE TRÊN CÁC CÂU MẪU MẠNG XÃ HỘI")
    print("=" * 70)

    for idx, sentence in enumerate(test_cases, 1):
        res = predictor.predict(sentence)
        print(f"\n[{idx}] Câu gốc : \"{res['input_text']}\"")
        print(f"    Chuỗi sinh: {res['raw_output']}")
        print(f"    Triplets  : {json.dumps(res['triplets'], ensure_ascii=False)}")


if __name__ == "__main__":
    demo_interactive()
