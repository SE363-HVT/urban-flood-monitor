import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.test_purging_filter import to_remove_indices

input_file = Path('data/processed/hcmc_flood_annotated_v3_multimodal.json')
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Loaded {len(data)} records from {input_file}")

# 1. Filter out all 108 junk records
cleaned = [item for idx, item in enumerate(data) if idx not in to_remove_indices]
print(f"After removing {len(to_remove_indices)} off-topic/ads/BDS records: {len(cleaned)} records")

# 2. Context-aware semantic adjustments per User Instruction and Expert Guidelines
# Specifically:
# - seq_id 10349: "Trong lúc chờ dự án chống ngập 10.000 tỷ về đích, thành phố Hồ Chí Minh ngập nặng sau mưa lớn."
# - seq_id 10100: "HIỆN TRẠNG CỐNG CHỐNG NGẬP 10.000 TỶ CỦA TP.HCM 'ĐỨNG HÌNH' SUỐT 5 NĂM"
# - seq_id 10118: "BẤT CHẤP CHỈ ĐẠO CỦA THỦ TƯỚNG, DỰ ÁN CHỐNG NGẬP 10.000 TỶ CỦA TP.HCM VẪN TIẾP TỤC DẬM CHÂN TẠI CHỖ"
# - seq_id 10160: "NGƯỜI DÂN TP HCM GỒNG MÌNH CHỐNG NGẬP... ngập úng nghiêm trọng"
# - seq_id 10185: "‼️Triều cường đạt đỉnh, người dân TP.HCM lại bì bõm lội nước, loay hoay chống ngập"
# - seq_id 10229: "[ TP.HCM: Bài toán chống ngập do mưa còn gặp khó ]"
# - seq_id 10353: "Tình trạng này diễn ra trong lúc TP.HCM đang chờ dự án chống ngập..."

modified_count = 0
for item in cleaned:
    text = (item.get('content', {}).get('text', '') or '') + ' ' + (item.get('content', {}).get('title', '') or '')
    
    # 1. User Image 3 & 5: tiktok_7689647759468825863_s01_10419
    if 'Trong lúc chờ dự án chống ngập 10.000 tỷ về đích, thành phố Hồ Chí Minh ngập nặng' in text:
        item['aste_triplets'] = [{
            "aspect": "thành phố Hồ Chí Minh",
            "opinion": "ngập nặng sau mưa lớn",
            "polarity": "NEG",
            "aspect_category": "LOCATION_ADMIN",
            "gazetteer_id": None,
            "grounding_provenance": "SPAN_MATCHED",
            "severity": "HIGH"
        }]
        modified_count += 1
        
    # 2. Cống chống ngập 10.000 tỷ đứng hình
    elif 'HIỆN TRẠNG CỐNG CHỐNG NGẬP 10.000 TỶ' in text and 'ĐỨNG HÌNH' in text:
        item['aste_triplets'] = [{
            "aspect": "cống chống ngập",
            "opinion": "ĐỨNG HÌNH",
            "polarity": "NEG",
            "aspect_category": "INFRASTRUCTURE_DRAINAGE",
            "gazetteer_id": None,
            "grounding_provenance": "SPAN_MATCHED",
            "severity": "MEDIUM"
        }]
        modified_count += 1
        
    # 3. Tiếp tục dậm chân tại chỗ
    elif 'DỰ ÁN CHỐNG NGẬP 10.000 TỶ' in text and 'DẬM CHÂN TẠI CHỖ' in text:
        item['aste_triplets'] = [{
            "aspect": "DỰ ÁN CHỐNG NGẬP 10.000 TỶ",
            "opinion": "DẬM CHÂN TẠI CHỖ",
            "polarity": "NEG",
            "aspect_category": "INFRASTRUCTURE_DRAINAGE",
            "gazetteer_id": None,
            "grounding_provenance": "SPAN_MATCHED",
            "severity": "MEDIUM"
        }]
        modified_count += 1
        
    # 4. Gồng mình chống ngập
    elif 'NGƯỜI DÂN TP HCM GỒNG MÌNH CHỐNG NGẬP' in text:
        item['aste_triplets'] = [{
            "aspect": "TP HCM",
            "opinion": "ngập úng nghiêm trọng",
            "polarity": "NEG",
            "aspect_category": "LOCATION_ADMIN",
            "gazetteer_id": None,
            "grounding_provenance": "SPAN_MATCHED",
            "severity": "CRITICAL"
        }]
        modified_count += 1
        
    # 5. Bì bõm lội nước, loay hoay chống ngập
    elif 'người dân TP.HCM lại bì bõm lội nước, loay hoay chống ngập' in text:
        item['aste_triplets'] = [{
            "aspect": "TP.HCM",
            "opinion": "bì bõm lội nước",
            "polarity": "NEG",
            "aspect_category": "LOCATION_ADMIN",
            "gazetteer_id": None,
            "grounding_provenance": "SPAN_MATCHED",
            "severity": "HIGH"
        }]
        modified_count += 1
        
    # 6. Bài toán chống ngập do mưa còn gặp khó
    elif '[ TP.HCM: Bài toán chống ngập do mưa còn gặp khó ]' in text:
        item['aste_triplets'] = [{
            "aspect": "TP.HCM",
            "opinion": "gặp khó",
            "polarity": "NEG",
            "aspect_category": "LOCATION_ADMIN",
            "gazetteer_id": None,
            "grounding_provenance": "SPAN_MATCHED",
            "severity": "LOW"
        }]
        modified_count += 1

    # 7. Đang chờ dự án hoàn thành
    elif 'Tình trạng này diễn ra trong lúc TP.HCM đang chờ dự án chống ngập' in text:
        item['aste_triplets'] = [{
            "aspect": "TP.HCM",
            "opinion": "đang chờ dự án chống ngập",
            "polarity": "NEU",
            "aspect_category": "LOCATION_ADMIN",
            "gazetteer_id": None,
            "grounding_provenance": "SPAN_MATCHED",
            "severity": "LOW"
        }]
        modified_count += 1

    # 8. Sarcastic post 'HẾT NGẬP' 😁
    elif "HCM sẽ 'HẾT NGẬP' - CSVN cho người dân Sài Gòn biết 😁" in text:
        item['aste_triplets'] = [{
            "aspect": "Sài Gòn",
            "opinion": "HẾT NGẬP",
            "polarity": "NEU",
            "aspect_category": "LOCATION_ADMIN",
            "gazetteer_id": None,
            "grounding_provenance": "SPAN_MATCHED",
            "severity": "LOW"
        }]
        modified_count += 1

    # 9. Đề xuất cái lu hứng nước mưa chống ngập
    elif "trang bị cho mỗi nhà một lu nước to để hứng nước mưa để chống ngập" in text:
        item['aste_triplets'] = [{
            "aspect": "TP.HCM",
            "opinion": "để chống ngập",
            "polarity": "NEU",
            "aspect_category": "LOCATION_ADMIN",
            "gazetteer_id": None,
            "grounding_provenance": "SPAN_MATCHED",
            "severity": "LOW"
        }]
        modified_count += 1

print(f"Applied semantic polarity/opinion corrections to {modified_count} records.")

# 3. Clean Re-indexing & seq_id position enforcement at the VERY END of each record dict
final_dataset = []
for new_sid, record in enumerate(cleaned):
    # Construct ordered dict with all existing keys except seq_id
    ordered = OrderedDict()
    for k, v in record.items():
        if k != 'seq_id':
            ordered[k] = v
    # Place seq_id as the ABSOLUTE LAST key
    ordered['seq_id'] = new_sid
    final_dataset.append(ordered)

print(f"Total clean records in final dataset: {len(final_dataset)} (seq_id: 0 to {len(final_dataset)-1})")

# Verify seq_id order
for i, item in enumerate(final_dataset):
    keys = list(item.keys())
    assert keys[-1] == 'seq_id', f"seq_id not last in record {i}: keys are {keys}"
    assert item['seq_id'] == i, f"seq_id mismatch in record {i}: {item['seq_id']}"

# Save to master dataset file
with open(input_file, 'w', encoding='utf-8') as f:
    json.dump(final_dataset, f, ensure_ascii=False, indent=2)

print(f"Successfully saved {len(final_dataset)} records to {input_file}")
