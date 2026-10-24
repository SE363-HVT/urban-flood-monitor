"""
finetune/prepare_dataset.py
Kịch bản tiền xử lý và phân tách dữ liệu cho bài toán Generative ASTE:
1. Đọc dữ liệu từ data/processed/hcmc_flood_annotated_v1.json (2,854 mẫu).
2. Chuẩn hóa cặp văn bản:
   - Input: content.text
   - Target: Chuỗi tuyến tính hóa các bộ ba: (Aspect | Opinion | Polarity) ; ...
3. Phân tách tập dữ liệu thành Train (80%), Val (10%), Test (10%).
4. Xuất các file JSON vào finetune/data/.
"""

import os
import sys
import re
import json
import random
import unicodedata
from typing import List, Dict, Any

# Cố định seed ngẫu nhiên để tái lập kết quả thực nghiệm chuẩn học thuật
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATA_SOURCE_V2 = os.path.join(PROJECT_ROOT, "data", "processed", "hcmc_flood_annotated_v2_multimodal.json")
DATA_SOURCE_V1 = os.path.join(PROJECT_ROOT, "data", "processed", "hcmc_flood_annotated_v1.json")
DATA_SOURCE = DATA_SOURCE_V2 if os.path.exists(DATA_SOURCE_V2) else DATA_SOURCE_V1
OUTPUT_DIR = os.path.join(CURRENT_DIR, "data")


def sanitize_aspect_span(raw_aspect: str) -> str:
    """
    Cleans leading prepositional noise and trailing clausal bleeding from aspect spans.
    Examples:
      'ở Sài Gòn hở mưa là' -> 'Sài Gòn'
      'Nguyễn Hữu Cảnh mới không còn' -> 'Nguyễn Hữu Cảnh'
      'ở khu Nam TPHCM xảy ra' -> 'khu Nam TPHCM'
    """
    aspect = raw_aspect.strip()
    # Strip leading prepositions
    noise_prefixes = r"^(ở|tại|trong|trên|vào)\s+"
    aspect = re.sub(noise_prefixes, "", aspect, flags=re.IGNORECASE)
    # Strip trailing noisy verbal/clausal remnants
    noise_suffixes = (
        r"\s+(mới không còn|xảy ra|chìm trong biển|mênh mông|"
        r"hở mưa là|mới hết ngập|bị ngập nặng)$"
    )
    aspect = re.sub(noise_suffixes, "", aspect, flags=re.IGNORECASE)
    return aspect.strip()


def format_triplets_to_target(triplets: List[Dict[str, str]]) -> str:
    """
    Tuyến tính hóa danh sách bộ ba thành chuỗi mục tiêu cho mô hình Seq2Seq.
    Định dạng: (Aspect | Opinion | Polarity) ; (Aspect | Opinion | Polarity)
    """
    if not triplets:
        return "None"
    
    formatted_items = []
    for t in triplets:
        raw_asp = unicodedata.normalize('NFC', t.get("aspect", "").strip())
        asp = sanitize_aspect_span(raw_asp)
        opi = unicodedata.normalize('NFC', t.get("opinion", "").strip())
        pol = t.get("polarity", "NEG").strip().upper()
        if asp and opi:
            formatted_items.append(f"({asp} | {opi} | {pol})")
    
    if not formatted_items:
        return "None"
    return " ; ".join(formatted_items)


def prepare_data():
    print("=" * 65)
    print("CHUẨN BỊ DỮ LIỆU HUẤN LUYỆN GENERATIVE ASTE (TEXT-TO-TRIPLET)")
    print("=" * 65)
    print(f"[*] Nguồn dữ liệu: {DATA_SOURCE}")
    
    if not os.path.exists(DATA_SOURCE):
        print(f"[!] Lỗi: Không tìm thấy file dữ liệu tại: {DATA_SOURCE}")
        sys.exit(1)
        
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(DATA_SOURCE, "r", encoding="utf-8") as f:
        raw_items = json.load(f)
        
    print(f"[*] Tổng số mẫu nạp từ processed dataset: {len(raw_items):,}")
    
    processed_samples = []
    total_triplets_count = 0
    
    for item in raw_items:
        text = item.get("content", {}).get("text", "").strip()
        triplets = item.get("aste_triplets", [])
        
        if not text or not triplets:
            continue
            
        target_str = format_triplets_to_target(triplets)
        if target_str == "None":
            continue
            
        seq_id = item.get("seq_id", len(processed_samples) + 1)
        processed_samples.append({
            "seq_id": seq_id,
            "id": f"sample_{seq_id:04d}",
            "original_id": item.get("id"),
            "platform": item.get("source", {}).get("platform", "unknown"),
            "input_text": text,
            "target_text": target_str,
            "raw_triplets": triplets
        })
        total_triplets_count += len(triplets)
        
    print(f"[*] Số mẫu hợp lệ phục vụ huấn luyện: {len(processed_samples):,}")
    print(f"[*] Tổng số bộ ba Triplet: {total_triplets_count:,} (Trung bình {total_triplets_count / len(processed_samples):.2f} triplet/câu)")
    
    # Stratified Split by Sentiment Polarity Groups (Bảo toàn lớp hiếm POS và NEU)
    groups: Dict[str, List[Dict[str, Any]]] = {"POS": [], "NEU": [], "NEG": []}
    for item in processed_samples:
        pols = {t["polarity"].upper() for t in item["raw_triplets"]}
        if "POS" in pols:
            groups["POS"].append(item)
        elif "NEU" in pols:
            groups["NEU"].append(item)
        else:
            groups["NEG"].append(item)
            
    train_data, val_data, test_data = [], [], []
    for g_name, items in groups.items():
        random.shuffle(items)
        n = len(items)
        n_train = int(n * 0.80)
        n_val = int(n * 0.10)
        train_data.extend(items[:n_train])
        val_data.extend(items[n_train:n_train + n_val])
        test_data.extend(items[n_train + n_val:])
        
    random.shuffle(train_data)
    random.shuffle(val_data)
    random.shuffle(test_data)
    
    splits = {
        "train": train_data,
        "val": val_data,
        "test": test_data
    }
    
    print("\n" + "-" * 65)
    print(f"PHÂN CHIA TẬP DỮ LIỆU CÓ PHÂN TẦNG (STRATIFIED SPLIT):")
    for s_name, s_list in splits.items():
        pos_c = sum(1 for it in s_list if any(t["polarity"].upper() == "POS" for t in it["raw_triplets"]))
        neu_c = sum(1 for it in s_list if any(t["polarity"].upper() == "NEU" for t in it["raw_triplets"]))
        print(f"  • Tập {s_name.upper():<5} : {len(s_list):,} mẫu (POS: {pos_c}, NEU: {neu_c})")
    print("-" * 65)
    
    for split_name, data in splits.items():
        out_file = os.path.join(OUTPUT_DIR, f"{split_name}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[+] Đã lưu {split_name.upper()} vào: {out_file}")
        
    print("\n[MẪU DỮ LIỆU ĐẦU TIÊN TRONG TẬP TRAIN]:")
    sample = train_data[0]
    print(f"  ID          : {sample['id']} (seq_id={sample['seq_id']})")
    print(f"  Input Text  : {sample['input_text']}")
    print(f"  Target Text : {sample['target_text']}")
    print("=" * 65)
    print("HOÀN TẤT CHUẨN BỊ DỮ LIỆU! SẴN SÀNG CHO BƯỚC HUẤN LUYỆN.")


if __name__ == "__main__":
    prepare_data()
