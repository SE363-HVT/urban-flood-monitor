#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/cleanse_and_resolve_gazetteer.py
--------------------------------------------------------------------------------
Script thanh lọc triệt để các bản ghi rác/ẩn dụ/câu cụt khỏi tập 10,000 bản ghi,
đồng thời chuẩn hóa địa giới hành chính theo Nghị quyết 1685 (168 phường mới)
thông qua Gazetteer Mapping từ tên đường sang phường chính thức.
"""

import os
import sys
import json
import re
from typing import List, Dict, Any, Set

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.admin_resolver import RESOLVER

V3_PATH = os.path.join(ROOT_DIR, "data", "processed", "hcmc_flood_annotated_v3_multimodal.json")

# Danh mục từ khóa rác & ẩn dụ cần loại bỏ triệt để
JUNK_PATTERNS = [
    r"bánh mì.*ngập",
    r"ngập.*(nhân|phô mai|sốt|topping|thịt|kem|trân châu)",
    r"ngập tràn.*(ưu đãi|ánh sáng|quà|tiếng cười|hạnh phúc|khuyến mãi|tiện ích)",
    r"tuyển dụng",
    r"lương.*triệu",
    r"bóng đá",
    r"đội tuyển.*nước rút",
    r"về đích.*nước rút",
    r"giai đoạn.*nước rút",
    r"nước rút.*(ôn thi|kỳ thi|tốt nghiệp)",
    r"ngập trong nợ",
    r"chìm trong nợ",
]

# Ánh xạ tên đường sang Phường mới theo NQ 1685
STREET_TO_OFFICIAL_WARD = {
    "trần xuân soạn": "Phường Tân Thuận",
    "huỳnh tấn phát": "Phường Phú Thuận",
    "nguyễn thị thập": "Phường Tân Hưng",
    "lê văn lương": "Phường Tân Hưng",
    "nguyễn văn linh": "Phường Tân Hưng",
    "võ văn ngân": "Phường Linh Chiểu",
    "đặng thị rành": "Phường Thủ Đức",
    "tô ngọc vân": "Phường Linh Tây",
    "kha vạn cân": "Phường Linh Xuân",
    "quốc lộ 13": "Phường Hiệp Bình",
    "ung văn khiêm": "Phường Thạnh Mỹ Tây",
    "nguyễn xí": "Phường Bình Thạnh",
    "đinh bộ lĩnh": "Phường Bình Thạnh",
    "bạch đằng": "Phường Bình Thạnh",
    "nguyễn văn quá": "Phường Đông Hưng Thuận",
    "phan huy ích": "Phường Tân Trụ",
    "cây trâm": "Phường Thông Tây Hội",
    "nguyễn văn khối": "Phường Thông Tây Hội",
    "lê đức thọ": "Phường An Nhơn",
    "quốc hương": "Phường An Khánh",
    "thảo điền": "Phường An Khánh",
    "nguyễn văn hưởng": "Phường An Khánh",
    "kinh dương vương": "Phường An Lạc",
    "hồ học lãm": "Phường An Lạc",
    "an dương vương": "Phường Phú Lâm",
    "hùng vương": "Phường Chợ Lớn",
    "trần hưng đạo": "Phường Bến Thành",
    "nguyễn thái bình": "Phường Sài Gòn",
    "cô giang": "Phường Cầu Ông Lãnh",
    "cô bắc": "Phường Cầu Ông Lãnh",
    "calmette": "Phường Cầu Ông Lãnh",
    "đoàn văn bơ": "Phường Xóm Chiếu",
    "hoàng diệu": "Phường Vĩnh Hội",
    "bến vân đồn": "Phường Khánh Hội",
}

def is_noise_item(text: str) -> bool:
    txt_lower = text.lower().strip()
    for pat in JUNK_PATTERNS:
        if re.search(pat, txt_lower):
            return True
    if len(txt_lower.split()) < 5:
        return True
    return False

def resolve_ward_for_record(rec: Dict[str, Any]) -> None:
    loc = rec.get("location")
    if not isinstance(loc, dict):
        loc = {"ward": "Chưa xác định", "city": "Hồ Chí Minh", "legacy_district": "TP.HCM", "locations": []}
        rec["location"] = loc

    current_ward = loc.get("ward")
    district = loc.get("legacy_district", "")
    text = (rec.get("content", {}).get("text") or "").lower()

    if not current_ward or current_ward in ["Chưa xác định", "None", "TP. Hồ Chí Minh", ""]:
        for street, official_ward in STREET_TO_OFFICIAL_WARD.items():
            if street in text:
                loc["ward"] = official_ward
                loc["city"] = "Hồ Chí Minh"
                if street.title() not in loc.get("locations", []):
                    loc.setdefault("locations", []).append(street.title())
                break
    else:
        resolved = RESOLVER.resolve_to_official_ward(current_ward, district)
        if resolved:
            loc["ward"] = resolved

def main():
    with open(V3_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Tổng số bản ghi ban đầu: {len(data)}")
    
    clean_data = []
    removed_count = 0
    resolved_wards_count = 0

    for item in data:
        text = item.get("content", {}).get("text", "")
        if is_noise_item(text):
            removed_count += 1
            continue

        old_ward = (item.get("location") or {}).get("ward")
        resolve_ward_for_record(item)
        new_ward = (item.get("location") or {}).get("ward")
        if old_ward != new_ward and new_ward != "Chưa xác định":
            resolved_wards_count += 1

        clean_data.append(item)

    print(f"Đã loại bỏ {removed_count} bản ghi rác/ẩn dụ.")
    print(f"Đã chuẩn hóa/bổ sung địa giới 168 phường mới cho {resolved_wards_count} bản ghi.")
    print(f"Số bản ghi sạch còn lại: {len(clean_data)}")

    with open(V3_PATH, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

    print("✅ Đã cập nhật tệp dataset sạch!")

if __name__ == "__main__":
    main()
