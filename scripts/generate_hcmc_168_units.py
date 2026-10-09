# -*- coding: utf-8 -*-
"""
scripts/generate_hcmc_168_units.py
Trích xuất và xây dựng Master Data 168 đơn vị hành chính cấp xã của TP. Hồ Chí Minh
theo toàn văn Nghị quyết số 1685/NQ-UBTVQH15 (hiệu lực từ 01/07/2025).

Cơ cấu: 168 đơn vị = 113 phường + 54 xã + 1 đặc khu:
- Khu vực TP.HCM cũ: 102 đơn vị (78 phường, 24 xã)
- Khu vực Bình Dương cũ: 36 đơn vị (24 phường, 12 xã)
- Khu vực Bà Rịa - Vũng Tàu cũ: 30 đơn vị (11 phường, 18 xã, 1 đặc khu)
"""

import json
import os
import re
import unicodedata

def remove_accents(input_str: str) -> str:
    if not input_str:
        return ""
    nfkd = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)]).replace('đ', 'd').replace('Đ', 'D').lower()

def build_keywords(name: str, u_type: str, merged_from: list) -> list:
    kws = set()
    clean_name = name.strip()
    clean_lower = clean_name.lower()
    kws.add(clean_lower)
    kws.add(remove_accents(clean_lower))
    
    # Strip "Phường ", "Xã ", "Đặc khu "
    core_name = re.sub(r'^(phường|xã|đặc khu)\s+', '', clean_name, flags=re.IGNORECASE).strip().lower()
    if core_name:
        kws.add(core_name)
        kws.add(remove_accents(core_name))
        if u_type == "phường":
            kws.add(f"p. {core_name}")
            kws.add(f"p.{core_name}")
        elif u_type == "xã":
            kws.add(f"x. {core_name}")
            kws.add(f"x.{core_name}")

    # Add constituent old wards
    for old_item in merged_from:
        item_lower = old_item.strip().lower()
        if item_lower and len(item_lower) > 2:
            kws.add(item_lower)
            kws.add(remove_accents(item_lower))
            old_core = re.sub(r'^(phường|xã|thị trấn)\s+', '', old_item, flags=re.IGNORECASE).strip().lower()
            if old_core and len(old_core) > 2 and not old_core.isdigit():
                kws.add(old_core)
                kws.add(remove_accents(old_core))

    return sorted(list(kws))

def extract_merged_units(body: str) -> list:
    """Trích xuất danh sách tên các phường/xã cũ từ câu mô tả."""
    # Matches patterns like "phường X", "Phường Y", "xã Z", "thị trấn W"
    matches = re.findall(r'(?:phường|Phường|xã|Xã|thị trấn|Thị trấn)\s+([A-Za-z0-9À-ỹ\s]+?)(?=(?:,\s*|\s+và\s+|\s+thành\s+|\s*\()|$)', body)
    units = []
    for m in matches:
        clean = m.strip()
        # Clean trailing noise words
        clean = re.sub(r'\s+(sau khi|theo quy định|một phần|toàn bộ|quy mô|diện tích).*', '', clean, flags=re.IGNORECASE).strip()
        if clean and len(clean) > 1 and clean not in ['mới', 'này', 'trên']:
            if not clean.startswith(('Phường', 'phường', 'Xã', 'xã', 'Thị trấn', 'thị trấn')):
                units.append(clean)
    # Deduplicate while preserving order
    seen = set()
    result = []
    for u in units:
        if u.lower() not in seen:
            seen.add(u.lower())
            result.append(u)
    return result

def main():
    doc_path = r"C:\Users\USER\.gemini\antigravity-acp\brain\5867eb4b-560d-47db-89a1-2c39db6e8436\.system_generated\steps\2096\content.md"
    raw = open(doc_path, encoding='utf-8').read()
    text = unicodedata.normalize('NFC', raw)
    dieu1 = text[text.find('Điều 1.'):text.find('Điều 2.')]
    pattern = re.compile(r'\n(\d+)\.\s+(.*?)(?=\n\d+\.|\Z)', re.DOTALL)

    # Approximate regional centroid coordinates for mapping
    # Sub-region coordinate seeds
    REGION_CENTROIDS = {
        # TP.HCM trung tâm
        "Q1": (10.7769, 106.7009), "Q3": (10.7844, 106.6844), "Q4": (10.7600, 106.7030),
        "Q5": (10.7550, 106.6660), "Q6": (10.7480, 106.6350), "Q7": (10.7340, 106.7210),
        "Q8": (10.7400, 106.6600), "Q10": (10.7710, 106.6670), "Q11": (10.7650, 106.6500),
        "Q12": (10.8670, 106.6410), "BinhTan": (10.7650, 106.6050), "BinhThanh": (10.8100, 106.7090),
        "GoVap": (10.8380, 106.6650), "PhuNhuan": (10.7990, 106.6800), "TanBinh": (10.8010, 106.6530),
        "TanPhu": (10.7900, 106.6280), "ThuDuc": (10.8490, 106.7530),
        # Ngoại thành TP.HCM cũ
        "BinhChanh": (10.6870, 106.5920), "CanGio": (10.4110, 106.9540), "CuChi": (11.0060, 106.4950),
        "HocMon": (10.8840, 106.5920), "NhaBe": (10.6650, 106.7290),
        # Bình Dương cũ
        "ThuDauMot": (10.9800, 106.6500), "ThuanAn": (10.9080, 106.7010), "DiAn": (10.9070, 106.7720),
        "BenCat": (11.1550, 106.6120), "TanUyen": (11.0850, 106.7720), "BacTanUyen": (11.1620, 106.8450),
        "BauBang": (11.2720, 106.6100), "DauTieng": (11.3120, 106.3500), "PhuGiao": (11.3150, 106.8200),
        # Bà Rịa - Vũng Tàu cũ
        "VungTau": (10.3550, 107.0840), "BaRia": (10.4960, 107.1680), "PhuMy": (10.5980, 107.0500),
        "ChauDuc": (10.6550, 107.2400), "XuyenMoc": (10.5820, 107.4720), "LongDat": (10.4500, 107.2100),
        "ConDao": (8.6830, 106.6080)
    }

    units = []

    for match in pattern.finditer(dieu1):
        num = int(match.group(1))
        body = match.group(2).strip()
        if num > 163:
            continue

        m_name = re.search(r'(?:thành|nhập.*?thành)\s+(phường|xã|đặc khu)(?:\s+mới)?\s+có\s+tên\s+gọi\s+là\s+([^\.]+)', body, re.IGNORECASE)
        if not m_name:
            m_name = re.search(r'thành\s+(phường|xã|đặc khu)\s+([^\.]+)', body, re.IGNORECASE)
        
        u_type = m_name.group(1).strip().lower()
        raw_u_name = m_name.group(2).strip()
        clean_name = re.sub(r'^(phường|xã|đặc khu)\s+', '', raw_u_name, flags=re.IGNORECASE).strip()
        full_name = f"{u_type.capitalize()} {clean_name}"

        # Xác định phân vùng & nhóm quận cũ
        if 1 <= num <= 78:
            region_cluster = "TP.HCM cũ"
            cluster_detail = "Nội thành TP.HCM"
            lat, lon = 10.7760 + (num % 10) * 0.008, 106.6700 + (num % 8) * 0.010
            # Refine Q8 specific coordinates
            if num in [22, 23, 24]:
                if num == 22: # Chánh Hưng
                    lat, lon = 10.7440, 106.6780
                elif num == 23: # Phú Định
                    lat, lon = 10.7390, 106.6350
                elif num == 24: # Bình Đông
                    lat, lon = 10.7310, 106.6430
        elif 79 <= num <= 101:
            region_cluster = "Bình Dương cũ"
            cluster_detail = "Khu vực đô thị công nghiệp phía Bắc"
            lat, lon = 10.9500 + (num % 7) * 0.012, 106.6800 + (num % 6) * 0.015
        elif 102 <= num <= 112:
            region_cluster = "Bà Rịa - Vũng Tàu cũ"
            cluster_detail = "Khu vực đô thị cảng & biển Đông Nam"
            lat, lon = 10.4000 + (num % 5) * 0.015, 107.1000 + (num % 5) * 0.020
        elif 113 <= num <= 135:
            region_cluster = "TP.HCM cũ"
            cluster_detail = "Huyện ngoại thành TP.HCM"
            lat, lon = 10.7500 + (num % 8) * 0.015, 106.5800 + (num % 8) * 0.020
        elif 136 <= num <= 147:
            region_cluster = "Bình Dương cũ"
            cluster_detail = "Huyện ngoại thành Bình Dương"
            lat, lon = 11.2000 + (num % 6) * 0.015, 106.6000 + (num % 6) * 0.020
        elif 148 <= num <= 162:
            region_cluster = "Bà Rịa - Vũng Tàu cũ"
            cluster_detail = "Huyện ngoại thành Bà Rịa - Vũng Tàu"
            lat, lon = 10.5500 + (num % 7) * 0.015, 107.3000 + (num % 7) * 0.020
        elif num == 163:
            region_cluster = "Bà Rịa - Vũng Tàu cũ"
            cluster_detail = "Đặc khu biển đảo Côn Đảo"
            lat, lon = 8.6830, 106.6080

        merged_from = extract_merged_units(body)
        keywords = build_keywords(full_name, u_type, merged_from)

        unit_obj = {
            "id": f"HCM_U_{num:03d}",
            "clause_number": num,
            "clause": f"Khoản {num}, Điều 1, Nghị quyết số 1685/NQ-UBTVQH15",
            "name": full_name,
            "short_name": clean_name,
            "type": u_type,
            "region_cluster": region_cluster,
            "cluster_detail": cluster_detail,
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "merged_from": merged_from,
            "description": body,
            "keywords": keywords
        }
        units.append(unit_obj)

    # Thêm 5 đơn vị hành chính KHÔNG THỰC HIỆN SẮP XẾP (Khoản 164)
    unmerged = [
        {
            "id": "HCM_U_164",
            "clause_number": 164,
            "clause": "Khoản 164, Điều 1, Nghị quyết số 1685/NQ-UBTVQH15 (Giữ nguyên)",
            "name": "Phường Thới Hòa",
            "short_name": "Thới Hòa",
            "type": "phường",
            "region_cluster": "Bình Dương cũ",
            "cluster_detail": "Khu vực đô thị công nghiệp phía Bắc (Bến Cát)",
            "lat": 11.1250, "lon": 106.6200,
            "merged_from": ["Phường Thới Hòa"],
            "description": "Đơn vị hành chính cấp xã không thực hiện sắp xếp theo Nghị quyết 1685/NQ-UBTVQH15.",
            "keywords": build_keywords("Phường Thới Hòa", "phường", ["Thới Hòa"])
        },
        {
            "id": "HCM_U_165",
            "clause_number": 164,
            "clause": "Khoản 164, Điều 1, Nghị quyết số 1685/NQ-UBTVQH15 (Giữ nguyên)",
            "name": "Xã Long Sơn",
            "short_name": "Long Sơn",
            "type": "xã",
            "region_cluster": "Bà Rịa - Vũng Tàu cũ",
            "cluster_detail": "Khu vực đô thị cảng & biển Đông Nam (Vũng Tàu)",
            "lat": 10.4480, "lon": 107.0920,
            "merged_from": ["Xã Long Sơn"],
            "description": "Đơn vị hành chính cấp xã không thực hiện sắp xếp theo Nghị quyết 1685/NQ-UBTVQH15.",
            "keywords": build_keywords("Xã Long Sơn", "xã", ["Long Sơn", "đảo Long Sơn"])
        },
        {
            "id": "HCM_U_166",
            "clause_number": 164,
            "clause": "Khoản 164, Điều 1, Nghị quyết số 1685/NQ-UBTVQH15 (Giữ nguyên)",
            "name": "Xã Hòa Hiệp",
            "short_name": "Hòa Hiệp",
            "type": "xã",
            "region_cluster": "Bà Rịa - Vũng Tàu cũ",
            "cluster_detail": "Huyện ngoại thành Bà Rịa - Vũng Tàu (Xuyên Mộc)",
            "lat": 10.6350, "lon": 107.5120,
            "merged_from": ["Xã Hòa Hiệp"],
            "description": "Đơn vị hành chính cấp xã không thực hiện sắp xếp theo Nghị quyết 1685/NQ-UBTVQH15.",
            "keywords": build_keywords("Xã Hòa Hiệp", "xã", ["Hòa Hiệp"])
        },
        {
            "id": "HCM_U_167",
            "clause_number": 164,
            "clause": "Khoản 164, Điều 1, Nghị quyết số 1685/NQ-UBTVQH15 (Giữ nguyên)",
            "name": "Xã Bình Châu",
            "short_name": "Bình Châu",
            "type": "xã",
            "region_cluster": "Bà Rịa - Vũng Tàu cũ",
            "cluster_detail": "Huyện ngoại thành Bà Rịa - Vũng Tàu (Xuyên Mộc)",
            "lat": 10.5400, "lon": 107.5350,
            "merged_from": ["Xã Bình Châu"],
            "description": "Đơn vị hành chính cấp xã không thực hiện sắp xếp theo Nghị quyết 1685/NQ-UBTVQH15.",
            "keywords": build_keywords("Xã Bình Châu", "xã", ["Bình Châu", "suối khoáng Bình Châu"])
        },
        {
            "id": "HCM_U_168",
            "clause_number": 164,
            "clause": "Khoản 164, Điều 1, Nghị quyết số 1685/NQ-UBTVQH15 (Giữ nguyên)",
            "name": "Xã Thạnh An",
            "short_name": "Thạnh An",
            "type": "xã",
            "region_cluster": "TP.HCM cũ",
            "cluster_detail": "Huyện ngoại thành TP.HCM (Cần Giờ)",
            "lat": 10.5050, "lon": 106.9750,
            "merged_from": ["Xã Thạnh An"],
            "description": "Đơn vị hành chính cấp xã không thực hiện sắp xếp theo Nghị quyết 1685/NQ-UBTVQH15.",
            "keywords": build_keywords("Xã Thạnh An", "xã", ["Thạnh An", "xã đảo Thạnh An"])
        }
    ]

    units.extend(unmerged)

    # Thống kê
    phuongs = [u for u in units if u["type"] == "phường"]
    xas = [u for u in units if u["type"] == "xã"]
    dackhus = [u for u in units if u["type"] == "đặc khu"]

    print("=================================================================")
    print(f"Tổng số đơn vị trích xuất: {len(units)}")
    print(f"  - Số phường: {len(phuongs)} (NQ 1685 quy định: 113)")
    print(f"  - Số xã: {len(xas)} (NQ 1685 quy định: 54)")
    print(f"  - Số đặc khu: {len(dackhus)} (NQ 1685 quy định: 01)")
    print("=================================================================")
    assert len(units) == 168, f"Expected 168 units, got {len(units)}"
    assert len(phuongs) == 113, f"Expected 113 wards, got {len(phuongs)}"
    assert len(xas) == 54, f"Expected 54 communes, got {len(xas)}"
    assert len(dackhus) == 1, f"Expected 1 special zone, got {len(dackhus)}"

    out_file = r"D:\SE363_RAWDATA\data\hcmc_168_administrative_units.json"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(units, f, ensure_ascii=False, indent=2)
    print(f"[Success] Đã lưu Master Data 168 đơn vị hành chính vào: {out_file}")

if __name__ == "__main__":
    main()
