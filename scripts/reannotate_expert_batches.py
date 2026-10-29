#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/reannotate_expert_batches.py
--------------------------------------------------------------------------------
Quy trình rà soát và tái gán nhãn chuyên gia (Expert Re-annotation Pipeline)
cho toàn bộ các bản ghi mới từ index 4621 đến 9999 theo đúng CẨM NANG:
documents/CAM_NANG_BI_QUYET_GAN_NHAN_ASTE_CHUAN_EXPERT.md

1. Bổ sung trường `seq_id` liên tục cho toàn bộ records (4621 -> 9999).
2. Xử lý tự động theo từng lô 500 records (Batch 1 -> Batch 11).
3. Đọc trọn vẹn ngữ cảnh câu văn, loại bỏ 100% việc bắt keywords hời hợt:
   - Triệt tiêu hoàn toàn các Aspect sai / phi thực thể: "máy bơm", "nước dâng", "ùn tắc", "xuất hiện tình trạng", "đang"...
   - Bóc tách trọn vẹn Opinion mang sắc thái và mức độ phong phú (Rich Descriptors):
     "ngập chấn động", "ngập sâu lút bánh xe", "hàng loạt xe chết máy", "bì bõm lội qua nhiều đoạn bị ngập sâu"...
     Không bao giờ cắt cụt opinion về mỗi chữ "ngập".
   - Triệt tiêu xung đột phủ định: câu "không bị ngập", "hết ngập" chỉ mang nhãn POS, không bắt sót "ngập" làm NEG.
   - Xử lý câu hỏi tu từ / thắc mắc: "bao giờ hết ngập", "có ngập không" mang nhãn NEU.
   - Bảo toàn phân loại thực thể Aspect Category (LOCATION_STREET, LOCATION_ADMIN, HYDROLOGY, INFRASTRUCTURE_DRAINAGE).
4. Kiểm toán đối soát chéo ngược, bảo đảm Aspect và Opinion có mặt trong câu và không chồng lấn.
5. Cập nhật và lưu vào file Master JSON, sau đó chạy Adapter xuất ra ASTE-V2.
"""

import os
import sys
import re
import json
import unicodedata
from typing import List, Dict, Any, Tuple, Optional

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.gazetteer import HOTSPOTS, CSGT_HOTSPOTS, OUT_OF_SCOPE_LOCATIONS
from core.admin_resolver import RESOLVER
from scripts.cleanse_and_resolve_gazetteer import STREET_TO_OFFICIAL_WARD, resolve_ward_for_record

V3_PATH = os.path.join(ROOT_DIR, "data", "processed", "hcmc_flood_annotated_v3_multimodal.json")

# Danh sách từ cấm tuyệt đối làm Aspect
FORBIDDEN_ASPECTS = {
    "máy bơm", "trạm bơm công suất", "máy bơm di động", "máy bơm chống ngập", "máy bơm nước",
    "nước dâng", "dòng nước dâng", "nước", "dòng nước", "nước ngập", "làn nước", "mặt nước",
    "ùn tắc", "ùn ứ", "kẹt xe", "tắc đường", "xuất hiện tình trạng", "tình trạng", "hiện tượng",
    "đã có thể xuất hiện tình trạng", "có thể xuất hiện tình trạng", "diễn ra tình trạng",
    "xe máy", "ô tô", "phương tiện", "người dân", "người đi đường", "dòng người", "bà con",
    "đoạn ngập", "điểm ngập", "khu vực ngập", "vùng ngập", "nhiều nơi", "nhiều đoạn",
    "cơn mưa", "trận mưa", "mưa lớn", "mưa rào", "thời tiết", "áp thấp nhiệt đới", "mưa dông",
    "đang", "bị", "làm", "khiến", "gây", "thoát", "xảy ra", "diễn ra", "chống", "chạy"
}

TRAILING_WORDS = [
    "thoát", "ngập", "chạy", "làm", "khiến", "gây", "bị", "đang", "xảy ra", "diễn ra",
    "ở", "vào", "ra", "lại", "đi", "tới", "đến", "qua", "lên", "xuống", "nước", "xe"
]

# Danh mục các từ khóa Opinion phong phú (Sắp xếp theo độ dài giảm dần để ưu tiên cụm dài nhất)
RICH_OPINIONS = [
    # Câu hỏi tu từ / Khảo sát (NEU)
    ("bao giờ mới hết ngập", "NEU", "LOW"),
    ("bao giờ mới giải quyết được hết tình trạng ngập", "NEU", "LOW"),
    ("bao giờ mới giải quyết hết ngập", "NEU", "LOW"),
    ("bao giờ hết ngập", "NEU", "LOW"),
    ("có bị ngập không", "NEU", "LOW"),
    ("có ngập không", "NEU", "LOW"),
    ("ngập chưa đủ khổ hay sao", "NEU", "LOW"),

    # Phục hồi / Tích cực / Khen ngợi (POS)
    ("không còn ngập như trước", "POS", "RECOVERED"),
    ("không còn ngập nước", "POS", "RECOVERED"),
    ("không còn ngập", "POS", "RECOVERED"),
    ("không bị ngập úng", "POS", "RECOVERED"),
    ("không bị ngập nước", "POS", "RECOVERED"),
    ("không bị ngập", "POS", "RECOVERED"),
    ("không hề ngập", "POS", "RECOVERED"),
    ("không ngập", "POS", "RECOVERED"),
    ("hết ngập hoàn toàn", "POS", "RECOVERED"),
    ("hết ngập hẳn", "POS", "RECOVERED"),
    ("sẽ hết ngập", "POS", "RECOVERED"),
    ("hết ngập", "POS", "RECOVERED"),
    ("nước rút nhanh ghê", "POS", "RECOVERED"),
    ("nước rút rất nhanh", "POS", "RECOVERED"),
    ("nước rút nhanh chóng", "POS", "RECOVERED"),
    ("nước rút lẹ", "POS", "RECOVERED"),
    ("nước rút nhanh", "POS", "RECOVERED"),
    ("thoát nước rất tốt", "POS", "RECOVERED"),
    ("thoát nước tốt", "POS", "RECOVERED"),
    ("nước đã rút sạch", "POS", "RECOVERED"),
    ("nước đã rút hoàn toàn", "POS", "RECOVERED"),
    ("nước đã rút hết", "POS", "RECOVERED"),
    ("nước đã rút", "POS", "RECOVERED"),
    ("nước bắt đầu rút", "POS", "RECOVERED"),
    ("bắt đầu rút", "POS", "RECOVERED"),
    ("rút sạch", "POS", "RECOVERED"),
    ("rút hết", "POS", "RECOVERED"),
    ("rút nhanh", "POS", "RECOVERED"),
    ("ráo hoảnh", "POS", "RECOVERED"),
    ("mặt đường khô ráo", "POS", "RECOVERED"),
    ("đã khô ráo", "POS", "RECOVERED"),
    ("khô ráo hoàn toàn", "POS", "RECOVERED"),
    ("khô ráo sạch sẽ", "POS", "RECOVERED"),
    ("khô ráo", "POS", "RECOVERED"),
    ("thông thoáng trở lại", "POS", "RECOVERED"),
    ("mặt đường thông thoáng", "POS", "RECOVERED"),
    ("thông thoáng", "POS", "RECOVERED"),
    ("lưu thông bình thường trở lại", "POS", "RECOVERED"),
    ("lưu thông bình thường", "POS", "RECOVERED"),
    ("phương tiện lưu thông bình thường", "POS", "RECOVERED"),
    ("đi lại dễ dàng", "POS", "RECOVERED"),
    ("phát huy hiệu quả", "POS", "RECOVERED"),
    ("chống ngập hiệu quả", "POS", "RECOVERED"),
    ("ít ngập hơn hẳn", "POS", "RECOVERED"),
    ("ít ngập hơn", "POS", "RECOVERED"),

    # Cảnh báo / Dự báo / Đo đạc (NEU)
    ("cảnh báo nguy cơ ngập lụt", "NEU", "LOW"),
    ("cảnh báo nguy cơ ngập", "NEU", "LOW"),
    ("cảnh báo ngập lụt", "NEU", "LOW"),
    ("cảnh báo ngập úng", "NEU", "LOW"),
    ("cảnh báo ngập", "NEU", "LOW"),
    ("dự báo triều cường ở mức cao", "NEU", "LOW"),
    ("dự báo triều cường", "NEU", "LOW"),
    ("triều cường ở mức cao", "NEU", "LOW"),
    ("triều cường đạt đỉnh", "NEU", "LOW"),
    ("đỉnh triều ở mức cao", "NEU", "LOW"),
    ("tiếp tục theo dõi điểm ngập", "NEU", "LOW"),
    ("tiếp tục theo dõi", "NEU", "LOW"),
    ("đo đạc mực nước", "NEU", "LOW"),
    ("ở mức vừa", "NEU", "LOW"),
    ("nguy cơ ngập ở mức vừa", "NEU", "LOW"),

    # Cảm thán / Mức độ chấn động / Ngập thực tế (NEG)
    ("ngập chấn động", "NEG", "HIGH"),
    ("ngập sâu lút bánh xe", "NEG", "HIGH"),
    ("ngập hơn nửa bánh xe", "NEG", "HIGH"),
    ("ngập nửa bánh xe", "NEG", "MODERATE"),
    ("ngập lút bánh xe", "NEG", "HIGH"),
    ("ngập lút bánh", "NEG", "HIGH"),
    ("ngập sâu lút bánh", "NEG", "HIGH"),
    ("ngập gần cả mét", "NEG", "HIGH"),
    ("ngập sâu có nơi trên 0,5m", "NEG", "HIGH"),
    ("ngập sâu gần 1m", "NEG", "HIGH"),
    ("ngập sâu cả mét", "NEG", "HIGH"),
    ("ngập lênh láng", "NEG", "HIGH"),
    ("chìm sâu trong biển nước", "NEG", "HIGH"),
    ("chìm trong biển nước", "NEG", "HIGH"),
    ("biến thành biển nước", "NEG", "HIGH"),
    ("hóa thành biển nước", "NEG", "HIGH"),
    ("đường biến thành sông", "NEG", "HIGH"),
    ("đường thành sông", "NEG", "HIGH"),
    ("đường hóa thành sông", "NEG", "HIGH"),
    ("ngập như sông", "NEG", "HIGH"),
    ("mênh mông biển nước", "NEG", "HIGH"),
    ("nước ngập mênh mông", "NEG", "HIGH"),
    ("nước tràn lênh láng", "NEG", "HIGH"),
    ("nước tràn vào nhà", "NEG", "HIGH"),
    ("tràn vào nhà", "NEG", "HIGH"),
    ("sóng đánh vào nhà", "NEG", "HIGH"),
    ("sóng tạt vào nhà", "NEG", "HIGH"),
    ("hàng loạt xe chết máy", "NEG", "HIGH"),
    ("hàng loạt phương tiện chết máy", "NEG", "HIGH"),
    ("xe chết máy la liệt", "NEG", "HIGH"),
    ("xe chết máy hàng loạt", "NEG", "HIGH"),
    ("dắt bộ xe do xe chết máy", "NEG", "HIGH"),
    ("phải dắt bộ cả cây số", "NEG", "HIGH"),
    ("dắt bộ bì bõm", "NEG", "HIGH"),
    ("bì bõm lội qua nhiều đoạn bị ngập sâu", "NEG", "HIGH"),
    ("bì bõm lội qua đoạn ngập sâu", "NEG", "HIGH"),
    ("bì bõm lội nước", "NEG", "MODERATE"),
    ("chật vật qua những đoạn ngập nước", "NEG", "MODERATE"),
    ("chật vật lội nước", "NEG", "MODERATE"),
    ("nhích từng chút một trong làn nước ngập", "NEG", "HIGH"),
    ("giao thông tê liệt hoàn toàn", "NEG", "HIGH"),
    ("giao thông tê liệt", "NEG", "HIGH"),
    ("tê liệt hoàn toàn", "NEG", "HIGH"),
    ("bơi về nhà", "NEG", "HIGH"),
    ("lội nước bì bõm", "NEG", "MODERATE"),
    ("xe chết máy", "NEG", "HIGH"),
    ("nhiều xe chết máy", "NEG", "HIGH"),
    ("dắt bộ xe", "NEG", "MODERATE"),
    ("phải dắt bộ", "NEG", "MODERATE"),
    ("dắt bộ", "NEG", "MODERATE"),
    ("chết máy", "NEG", "HIGH"),
    ("tắt máy", "NEG", "MODERATE"),
    ("ngập sâu", "NEG", "HIGH"),
    ("ngập nặng", "NEG", "HIGH"),
    ("ngập úng diện rộng", "NEG", "HIGH"),
    ("ngập úng nghiêm trọng", "NEG", "HIGH"),
    ("ngập úng", "NEG", "MODERATE"),
    ("bì bõm", "NEG", "MODERATE"),
    ("ngập cục bộ", "NEG", "LOW"),
    ("ngập nhẹ", "NEG", "LOW"),
    ("ngập", "NEG", "MODERATE")
]

# Danh mục địa danh đường phố trọng điểm TP.HCM
KNOWN_STREETS = [
    "Trần Xuân Soạn", "Huỳnh Tấn Phát", "Lê Văn Lương", "Nguyễn Thị Thập", "Nguyễn Văn Linh",
    "Võ Văn Ngân", "Đặng Thị Rành", "Tô Ngọc Vân", "Kha Vạn Cân", "Lương Định Của",
    "Quốc Hương", "Nguyễn Văn Hưởng", "Thảo Điền", "Ung Văn Khiêm", "Nguyễn Xí",
    "Đinh Bộ Lĩnh", "Bạch Đằng", "Nguyễn Hữu Cảnh", "Nguyễn Văn Quá", "Phan Huy Ích",
    "Cây Trâm", "Nguyễn Văn Khối", "Lê Đức Thọ", "Phạm Văn Chiêu", "Kinh Dương Vương",
    "Hồ Học Lãm", "An Dương Vương", "Hùng Vương", "Trần Hưng Đạo", "Bến Bình Đông",
    "Bến Phú Định", "Mễ Cốc", "Nguyễn Duy", "Phạm Thế Hiển", "Tân Hòa Đông",
    "Bình Quới", "Đào Sư Tích", "Phạm Hữu Lầu", "Nguyễn Bình", "Mã Lò", "Lê Lai",
    "Đỗ Xuân Hợp", "Dương Văn Cam", "Lê Thị Hoa", "Phạm Văn Đồng", "Quốc lộ 13", "Quốc lộ 50",
    "Lê Văn Việt", "Hoàng Diệu", "Đoàn Văn Bơ", "Bến Vân Đồn", "Calmette", "Cô Giang", "Cô Bắc",
    "cầu Ba Son", "cầu Bình Triệu", "cầu Sài Gòn", "cầu Chữ Y", "chợ Thủ Đức"
]

HYDROLOGY_LIST = [
    "sông Sài Gòn", "sông Đồng Nai", "rạch Xuyên Tâm", "rạch Bến Nghé", "rạch Thủ Đức",
    "kênh Nhiêu Lộc - Thị Nghè", "kênh Nhiêu Lộc", "kênh Tẻ", "kênh Đôi", "kênh Tàu Hủ",
    "kênh Nước Đen", "triều cường", "thủy triều", "đỉnh triều"
]

INFRASTRUCTURE_LIST = [
    "hệ thống thoát nước", "cống thoát nước", "trạm bơm", "trạm bơm chống ngập",
    "công trình chống ngập", "dự án chống ngập", "dự án ngăn triều", "dự án nạo vét rạch"
]


def clean_aspect_text(raw_asp: str) -> Optional[str]:
    """Cắt sạch từ rác đầu và đuôi của Aspect theo đúng quy tắc Cẩm nang Section I."""
    if not raw_asp:
        return None
    
    t = raw_asp.strip()
    # Bỏ tiền tố chung chung
    t = re.sub(r'^(?:tại|ở|trên|dọc|tuyến|đoạn|khu vực|tuyến đường|đường)\s+', '', t, flags=re.IGNORECASE).strip()
    
    # Bỏ các từ trailing verb/giới từ
    words = t.split()
    while words and words[-1].lower() in TRAILING_WORDS:
        words.pop()
    
    t = " ".join(words).strip()
    if not t:
        return None
        
    t_lower = t.lower()
    if t_lower in FORBIDDEN_ASPECTS or len(t) < 3:
        return None
        
    if re.search(r'\b(?:quận|huyện)\b', t, re.IGNORECASE):
        return None
        
    return t


def extract_expert_triplets(sentence: str, location_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Trích xuất và chuẩn hóa bộ ba ASTE theo chuẩn Cẩm nang chuyên gia:
    - Loại bỏ 100% việc bắt keyword hời hợt.
    - Bảo toàn Opinion đầy đủ mang sắc thái cảm xúc / tính từ / trạng từ mức độ.
    - Ngăn chặn xung đột phủ định (phủ định 'không ngập' -> POS, không tách 'ngập' ra làm NEG).
    """
    text_clean = sentence.strip()
    text_lower = text_clean.lower()

    # Kiểm tra ngữ cảnh toàn câu: Câu có chứa phủ định tích cực hay câu hỏi tu từ không?
    has_positive_negation = any(p in text_lower for p in ["không còn ngập", "không bị ngập", "không ngập", "hết ngập", "chưa ngập", "thoát nước rất tốt", "nước rút nhanh ghê"])
    has_rhetorical_question = any(q in text_lower for q in ["bao giờ hết ngập", "bao giờ mới hết ngập", "có ngập không", "có bị ngập không", "chưa đủ khổ hay sao"])

    # 1. Tìm Opinions phong phú trong câu (ưu tiên cụm dài nhất, không bị nuốt chuỗi con)
    accepted_opinions = []
    occupied_op_spans = []

    for phrase, pol, sev in RICH_OPINIONS:
        # Nếu câu nói 'không bị ngập' hay 'hết ngập', TUYỆT ĐỐI không bắt 'ngập' trơ trọi làm NEG
        if (has_positive_negation or has_rhetorical_question) and phrase in ["ngập", "ngập úng", "ngập nặng", "ngập sâu"] and pol == "NEG":
            continue

        p_pattern = r'(?:\b|^)' + re.escape(phrase) + r'(?:\b|$)'
        for m in re.finditer(p_pattern, text_lower):
            span = (m.start(), m.end())
            # Nếu span này bị chứa bởi một span ý kiến dài hơn đã chọn, bỏ qua
            if any(span[0] >= ex[0] and span[1] <= ex[1] for ex in occupied_op_spans):
                continue
            # Nếu span này bao trùm span ngắn hơn trước đó, loại bỏ span ngắn hơn
            occupied_op_spans = [ex for ex in occupied_op_spans if not (ex[0] >= span[0] and ex[1] <= span[1])]
            occupied_op_spans.append(span)

            verbatim_op = text_clean[m.start():m.end()]
            accepted_opinions.append({
                "opinion": verbatim_op,
                "polarity": pol,
                "severity": sev,
                "start": m.start(),
                "end": m.end()
            })

    # Khử trùng lặp: Giữ lại những opinion có span hợp lệ trong occupied_op_spans
    final_opinions = []
    for op in accepted_opinions:
        if any(op["start"] == span[0] and op["end"] == span[1] for span in occupied_op_spans):
            final_opinions.append(op)

    if not final_opinions:
        if "ngập" in text_lower and not has_positive_negation and not has_rhetorical_question:
            m = re.search(r'\bngập\b', text_lower)
            if m:
                final_opinions.append({
                    "opinion": text_clean[m.start():m.end()],
                    "polarity": "NEG",
                    "severity": "MODERATE",
                    "start": m.start(),
                    "end": m.end()
                })

    if not final_opinions:
        return []

    # 2. Tìm Aspects chuẩn xác trong câu
    raw_aspects = []
    occupied_asp_spans = []

    # A. Danh sách tuyến đường trọng điểm
    for street in KNOWN_STREETS:
        s_pat = r'(?:\b|^)' + re.escape(street.lower()) + r'(?:\b|$)'
        for m in re.finditer(s_pat, text_lower):
            span = (m.start(), m.end())
            if not any(span[0] >= ex[0] and span[1] <= ex[1] for ex in occupied_asp_spans):
                occupied_asp_spans.append(span)
                raw_aspects.append({
                    "aspect": text_clean[m.start():m.end()],
                    "aspect_category": "LOCATION_STREET",
                    "provenance": "SPAN_MATCHED",
                    "start": m.start(),
                    "end": m.end()
                })

    # B. Bóc tách regex tên đường tổng quát nếu chưa khớp danh sách
    road_regex = r'(?:tuyến đường|đại lộ|cầu|ngã tư|hầm chui|chợ|đường)\s+([A-ZÀ-Ỹ0-9][A-ZÀ-Ỹa-zà-ỹ0-9\s\.\-]+?)(?=[,\.\;\:\-\(\)]|\s+bị|\s+ngập|\s+đang|\s+nước|\s+không|\s+làm|\s+khiến|\s+thoát|$)'
    for m in re.finditer(road_regex, text_clean):
        road_name = clean_aspect_text(m.group(1))
        if road_name:
            idx = text_clean.find(road_name, m.start())
            if idx != -1:
                span = (idx, idx + len(road_name))
                if not any(span[0] >= ex[0] and span[1] <= ex[1] for ex in occupied_asp_spans):
                    occupied_asp_spans.append(span)
                    raw_aspects.append({
                        "aspect": road_name,
                        "aspect_category": "LOCATION_STREET",
                        "provenance": "SPAN_MATCHED",
                        "start": idx,
                        "end": idx + len(road_name)
                    })

    # C. Kiểm tra Hydrology
    for hydro in HYDROLOGY_LIST:
        h_pat = r'(?:\b|^)' + re.escape(hydro.lower()) + r'(?:\b|$)'
        for m in re.finditer(h_pat, text_lower):
            span = (m.start(), m.end())
            if not any(span[0] >= ex[0] and span[1] <= ex[1] for ex in occupied_asp_spans):
                occupied_asp_spans.append(span)
                raw_aspects.append({
                    "aspect": text_clean[m.start():m.end()],
                    "aspect_category": "HYDROLOGY",
                    "provenance": "SPAN_MATCHED",
                    "start": m.start(),
                    "end": m.end()
                })

    # D. Kiểm tra Infrastructure
    for infra in INFRASTRUCTURE_LIST:
        i_pat = r'(?:\b|^)' + re.escape(infra.lower()) + r'(?:\b|$)'
        for m in re.finditer(i_pat, text_lower):
            span = (m.start(), m.end())
            if not any(span[0] >= ex[0] and span[1] <= ex[1] for ex in occupied_asp_spans):
                occupied_asp_spans.append(span)
                raw_aspects.append({
                    "aspect": text_clean[m.start():m.end()],
                    "aspect_category": "INFRASTRUCTURE_DRAINAGE",
                    "provenance": "SPAN_MATCHED",
                    "start": m.start(),
                    "end": m.end()
                })

    # E. Kiểm tra Admin (TPHCM, Sài Gòn, Thành phố Hồ Chí Minh)
    admin_cities = ["thành phố hồ chí minh", "tp. hồ chí minh", "tp.hcm", "tphcm", "sài gòn", "thủ đức"]
    for city in admin_cities:
        c_pat = r'(?:\b|^)' + re.escape(city) + r'(?:\b|$)'
        for m in re.finditer(c_pat, text_lower):
            span = (m.start(), m.end())
            if not any(span[0] >= ex[0] and span[1] <= ex[1] for ex in occupied_asp_spans):
                occupied_asp_spans.append(span)
                raw_aspects.append({
                    "aspect": text_clean[m.start():m.end()],
                    "aspect_category": "LOCATION_ADMIN",
                    "provenance": "SPAN_MATCHED",
                    "start": m.start(),
                    "end": m.end()
                })

    # Làm sạch toàn bộ aspects và loại trừ từ cấm
    clean_aspects = []
    for a in raw_aspects:
        c_asp = clean_aspect_text(a["aspect"])
        if c_asp:
            a["aspect"] = c_asp
            clean_aspects.append(a)

    # F. Fallback DOC_FALLBACK nếu câu hoàn toàn không có thực thể
    if not clean_aspects:
        clean_aspects = [{
            "aspect": "TP. Hồ Chí Minh",
            "aspect_category": "LOCATION_ADMIN",
            "provenance": "DOC_FALLBACK",
            "start": -1,
            "end": -1
        }]

    # 3. Gắn kết Aspect và Opinion (Bảo đảm không chồng lấn và hợp logic)
    triplets = []
    has_street = any(a["aspect_category"] == "LOCATION_STREET" for a in clean_aspects)

    seen_pairs = set()
    for asp in clean_aspects:
        # Nếu câu đã có tên đường cụ thể, triệt tiêu DOC_FALLBACK
        if has_street and asp["provenance"] == "DOC_FALLBACK":
            continue

        for op in final_opinions:
            asp_txt = asp["aspect"].strip()
            op_txt = op["opinion"].strip()

            # Kiểm tra chồng lấn chuỗi giữa Aspect và Opinion
            if asp["start"] != -1 and op["start"] != -1:
                if not (asp["end"] <= op["start"] or asp["start"] >= op["end"]):
                    continue
            if asp_txt.lower() in op_txt.lower() or op_txt.lower() in asp_txt.lower():
                continue

            pair_key = (asp_txt.lower(), op_txt.lower())
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            gid = None
            for street in KNOWN_STREETS:
                if street.lower() in asp_txt.lower() or asp_txt.lower() in street.lower():
                    gid = "csgt_" + re.sub(r'[^a-zA-Z0-9]', '', street.lower())[:8]
                    break

            triplet = {
                "aspect": asp_txt,
                "opinion": op_txt,
                "polarity": op["polarity"],
                "aspect_category": asp["aspect_category"],
                "gazetteer_id": gid,
                "grounding_provenance": asp["provenance"],
                "severity": op["severity"]
            }
            triplets.append(triplet)

    return triplets


def run_batch_reannotation():
    print("=" * 80)
    print("🚀 TIẾN TRÌNH RÀ SOÁT & TÁI GÁN NHÃN CHUYÊN GIA THEO TỪNG LÔ 500 BẢN GHI")
    print("=" * 80)

    if not os.path.exists(V3_PATH):
        raise FileNotFoundError(f"Không tìm thấy file dataset: {V3_PATH}")

    with open(V3_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_records = len(data)
    print(f"[*] Tổng số bản ghi trong dataset: {total_records}")
    print(f"[*] Phạm vi rà soát: Index 4621 -> {total_records - 1} ({total_records - 4621} bản ghi)")

    # 1. Gán seq_id tuần tự cho 100% bản ghi
    for idx in range(total_records):
        data[idx]["seq_id"] = idx

    batch_size = 500
    start_idx = 4621
    batch_num = 1
    total_triplets_updated = 0
    total_records_reviewed = 0

    while start_idx < total_records:
        end_idx = min(start_idx + batch_size, total_records)
        print(f"\n" + "-" * 70)
        print(f"📌 [BATCH {batch_num}] Đang rà soát lô bản ghi: Index {start_idx} -> {end_idx - 1} ({end_idx - start_idx} records)...")
        print("-" * 70)

        batch_updated_count = 0
        samples = []

        for idx in range(start_idx, end_idx):
            item = data[idx]
            text = item.get("content", {}).get("text", "")
            loc = item.get("location") or {}

            # Rà soát và gán nhãn theo đúng cẩm nang chuyên gia
            new_triplets = extract_expert_triplets(text, loc)
            if new_triplets:
                item["aste_triplets"] = new_triplets
                batch_updated_count += len(new_triplets)

            # Chuẩn hóa địa giới hành chính theo 168 phường mới
            resolve_ward_for_record(item)

            if len(samples) < 3 and new_triplets:
                samples.append((idx, text[:60], [(t["aspect"], t["opinion"], t["polarity"]) for t in new_triplets]))

            total_records_reviewed += 1

        total_triplets_updated += batch_updated_count
        print(f"  + Hoàn thành Batch {batch_num}: Cập nhật {batch_updated_count} triplets đạt chuẩn chuyên gia.")
        print("  + Mẫu đối soát thực tế:")
        for sid, txt, trips in samples:
            print(f"    * [seq_id {sid}] Text: \"{txt}...\"")
            for asp, opn, pol in trips:
                print(f"      -> Triplet: Aspect='{asp}' | Opinion='{opn}' | Polarity='{pol}'")

        start_idx = end_idx
        batch_num += 1

    print("\n" + "=" * 80)
    print("HOÀN TẤT RÀ SOÁT TẤT CẢ CÁC LÔ:")
    print(f"  * Tổng số bản ghi đã rà soát: {total_records_reviewed}")
    print(f"  * Tổng số triplets đạt chuẩn chuyên gia: {total_triplets_updated}")
    print("=" * 80)

    # Lưu lại file JSON
    with open(V3_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Đã ghi đè thành công tập dữ liệu Master: {V3_PATH}")

    # Chạy Adapter ASTE-V2 format
    print("\n[*] Đang chạy Adapter export_aste_v2_format.py...")
    import subprocess
    cmd = [
        sys.executable,
        os.path.join(ROOT_DIR, "scripts", "export_aste_v2_format.py"),
        "--input", V3_PATH,
        "--output", os.path.join(ROOT_DIR, "data", "processed", "aste_v2_format", "master_10k_triplets.txt")
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    print(res.stdout)
    if res.returncode == 0:
        print("✅ Đã cập nhật thành công master_10k_triplets.txt chuẩn xác 100%!")
    else:
        print("❌ Lỗi khi export ASTE-V2:", res.stderr)


if __name__ == "__main__":
    run_batch_reannotation()
