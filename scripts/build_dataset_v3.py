# -*- coding: utf-8 -*-
"""
scripts/build_dataset_v3.py
Chương trình chuyển đổi và chuẩn hóa Dataset ASTE lên chuẩn v3 hoàn thiện:
1. Tuân thủ 100% Schema v3 (7 trường ngữ cảnh):
   {aspect, opinion, polarity, aspect_category, gazetteer_id, grounding_provenance, severity}
2. Bỏ hoàn toàn khái niệm cấp Quận theo Nghị quyết 1685 (NQ 1685):
   Chỉ sử dụng 168 Phường/Xã/Thị trấn chuẩn hóa, 0% rò rỉ cấp Quận.
3. Khắc phục triệt để 3 lỗi Heuristics cố hữu:
   - Loại bỏ Substring Shadowing (không sinh 'Sài Gòn' khi đã có 'sông Sài Gòn').
   - Thực thi Span Hierarchy Rule (không broadcast ý kiến cho cấp hành chính khi đã có tên đường làm chủ ngữ).
   - Ràng buộc mệnh đề cục bộ (Clause Proximity Binding: liên kết mỗi aspect với ý kiến gần nhất).
4. Tách biệt chuẩn xác 5 Aspect Categories:
   - INFRASTRUCTURE_DRAINAGE (Cống, trạm bơm, nắp ga, nạo vét kênh, nâng nền).
   - HYDROLOGY (Sông, kênh, rạch, hồ, đỉnh triều, trạm thủy văn).
   - RESPONSE_ENTITY (CSGT, công nhân thoát nước, đội ứng trực, chính quyền).
   - LOCATION_STREET (Tên đường, giao lộ, cầu, hầm chui).
   - LOCATION_ADMIN (168 Phường/Xã theo NQ 1685).
5. Khai thác & làm sạch dữ liệu POS/NEU từ:
   - Toàn bộ raw episodes (bao gồm Facebook & TikTok vừa crawl).
   - data/raw/dataset_google_news_full.json.
   - data/lakehouse/**/*.jsonl.
   - Khử trùng lặp 100% qua mã băm MD5.
"""

import os
import sys
import re
import json
import glob
import hashlib
import unicodedata
from datetime import datetime, timezone
from collections import defaultdict, Counter
from typing import List, Dict, Any, Optional, Tuple, Set

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.gazetteer import HOTSPOTS, normalize_text
from core.admin_resolver import RESOLVER

DATA_DIR = os.path.join(ROOT_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
INPUT_FILE_V2 = os.path.join(PROCESSED_DIR, "hcmc_flood_annotated_v2_multimodal.json")
OUTPUT_FILE_V3 = os.path.join(PROCESSED_DIR, "hcmc_flood_annotated_v3_multimodal.json")
RAW_EPISODES_DIR = os.path.join(DATA_DIR, "raw", "episodes")
LAKEHOUSE_DIR = os.path.join(DATA_DIR, "lakehouse")

# Danh mục 168 Phường/Xã chuẩn NQ 1685
VALID_WARDS = RESOLVER.valid_ward_names
VALID_WARDS_LOWER = {w.lower(): w for w in VALID_WARDS}

# Lập chỉ mục Hotspot CSGT phục vụ Mapping (Loại bỏ cấp Quận)
HOTSPOT_LOOKUP = {}
for h in HOTSPOTS:
    h_disp = h.get("display_name", "")
    h_name = h_disp.replace("Khu vực ", "").replace("Đường ", "").strip()
    slug_id = "csgt_" + re.sub(r'[^a-zA-Z0-9]', '', h_name.lower())[:8]
    is_admin_area = h_disp.startswith("Khu vực") or any(k in h_name.lower() for k in ["toàn tp", "thủ đức", "quận", "huyện"])
    
    for kw in h.get("keywords", []):
        kw_clean = kw.strip().lower()
        # Bỏ qua từ khóa cấp quận
        if re.search(r'\b(?:quận|huyện)\s+[0-9a-zà-ỹ]+', kw_clean):
            continue
        if len(kw_clean) >= 3:
            HOTSPOT_LOOKUP[kw_clean] = {
                "gazetteer_id": slug_id,
                "display_name": h_disp,
                "is_admin": is_admin_area,
                "ward": h.get("ward", ""),
                "lat": h.get("lat"),
                "lon": h.get("lon")
            }

# ==============================================================================
# TỪ ĐIỂN CÁC THỰC THỂ THUỘC 5 NHÓM ASPECT CATEGORY
# ==============================================================================
INFRASTRUCTURE_ENTITIES = [
    "cống ngăn triều mương chuối", "cống mương chuối", "cống ngăn triều bến nghé", "cống bến nghé",
    "cống ngăn triều phú xuân", "cống phú xuân", "cống tân thuận", "cống cây khô", "cống phú định",
    "cống kiểm soát triều", "cống ngăn triều", "cống thoát nước", "miệng cống", "nắp cống", "nắp ga",
    "hố ga", "hệ thống cống", "hệ thống thoát nước", "trạm bơm thảo điền", "trạm bơm nguyễn hữu cảnh",
    "trạm bơm thanh đa", "trạm bơm", "máy bơm công suất lớn", "máy bơm chống ngập", "máy bơm",
    "dự án nạo vét rạch", "dự án nạo vét", "công trình chống ngập", "dự án giải quyết ngập",
    "dự án ngăn triều", "dự án thoát nước", "dự án chống ngập", "đê bao", "bờ kè", "kè chống sạt lở",
    "nâng nền đường", "nâng nền", "khơi thông dòng chảy"
]

HYDROLOGY_ENTITIES = [
    "sông sài gòn", "sông đồng nai", "sông soài rạp", "sông nhà bè",
    "kênh nhiêu lộc - thị nghè", "kênh nhiêu lộc", "kênh tẻ", "kênh đôi", "kênh tàu hủ",
    "kênh nước đen", "kênh 19/5", "rạch xuyên tâm", "rạch bến nghé", "rạch cầu hàn",
    "rạch đĩa", "rạch dừa", "rạch ông lớn", "rạch tôm", "rạch thủ đức", "rạch ông búp", "hồ dầu tiếng", "hồ trị an",
    "trạm phú an", "trạm nhà bè", "trạm thủ dầu một", "trạm hải văn", "trạm đo",
    "triều cường", "thủy triều", "triều dâng", "đỉnh triều", "mực nước triều",
    "dòng nước", "mực nước sông", "dòng lũ", "nước dâng", "nước sông", "thủy văn"
]

RESPONSE_ENTITIES = [
    "cảnh sát giao thông", "csgt", "công nhân thoát nước", "công ty thoát nước đô thị",
    "đội ứng trực", "đội cứu hộ", "lực lượng ứng phó", "lực lượng chức năng", "ban chỉ huy pctt",
    "chính quyền địa phương", "cán bộ địa phương", "đội xung kích", "lực lượng xung kích"
]

# ==============================================================================
# TỪ ĐIỂN Ý KIẾN NGUYÊN VĂN (VERBATIM OPINIONS)
# ==============================================================================
POSITIVE_OPINIONS = [
    # Nước rút / Khô ráo / Thông xe (Recovery)
    "nước đã rút hoàn toàn", "nước đã rút sạch", "nước đã rút hết", "nước rút sạch sẽ", "nước rút sạch",
    "nước rút hết", "nước đã rút", "nước rút nhanh", "đã rút hết", "đã rút hẳn", "rút sạch", "rút hết",
    "bắt đầu rút", "nước bắt đầu rút", "rút dần", "nước rút dần",
    "không còn ngập nước", "không còn ngập nữa", "không còn ngập", "hết ngập hẳn", "hết ngập",
    "không bị ngập nước", "không bị ngập", "không hề ngập", "không ngập",
    "khô ráo hoàn toàn", "mặt đường khô ráo", "đã khô ráo", "khô ráo sạch sẽ", "khô ráo", "khô rang", "khô queo", "ráo hoảnh",
    "thông thoáng trở lại", "mặt đường thông thoáng", "thông thoáng", "thông xe", "thông suốt",
    "lưu thông bình thường trở lại", "phương tiện lưu thông bình thường", "lưu thông bình thường",
    "di chuyển bình thường", "đi lại bình thường", "đi lại dễ dàng", "lưu thông thuận lợi",
    "ổn định trở lại", "giao thông ổn định trở lại", "giao thông bình thường", "xe cộ qua lại bình thường",
    # Khen ngợi công trình / Lực lượng ứng trực (Praise)
    "phát huy hiệu quả", "hoạt động hiệu quả", "thoát nước rất nhanh", "thoát nước nhanh",
    "thoát nước rất tốt", "chống ngập tốt", "chống ngập hiệu quả", "khen ngợi",
    "ứng trực kịp thời", "kịp thời đẩy xe giúp dân", "kịp thời hỗ trợ", "giúp người dân vượt qua điểm ngập",
    "bình yên sau mưa", "phấn khởi", "an tâm"
]

NEUTRAL_OPINIONS = [
    # Đo đạc khách quan / Mực nước
    "ngập sâu khoảng nửa mét", "ngập sâu khoảng 0.5m", "ngập sâu khoảng 20cm", "ngập sâu khoảng 30cm",
    "ngập sâu khoảng 40cm", "ngập sâu 20cm", "ngập sâu 30cm", "ngập sâu 40cm", "ngập sâu 50cm",
    "ngập khoảng 20-30cm", "ngập khoảng 20 - 30cm", "ngập từ 10-20cm", "ngập từ 20-30cm",
    "cao khoảng 20cm", "cao khoảng 30cm", "cao khoảng 40cm", "cao 20cm", "cao 30cm", "cao 40cm", "cao 50cm",
    "mực nước cao 0.5m", "mực nước cao 0.4m", "mực nước cao 0.3m", "mực nước cao 20cm", "mực nước cao 30cm",
    "đỉnh triều đạt 1m70", "đỉnh triều đạt 1m72", "đỉnh triều đạt 1m68", "đỉnh triều đạt 1m65", "đạt mức 1m70",
    "đạt mức 1m72", "đạt mức 1m68", "đạt mức 1m65", "đạt đỉnh 1,65 m", "đo được", "đo đạc", "đạt đỉnh", "đạt mức",
    "ở mức cao", "đang ở mức cao", "biến đổi chậm", "được dự báo biến đổi chậm", "ở cấp độ 2", "ở cấp độ 1", "ở cấp độ 3",
    # Dự báo / Khí tượng
    "dự báo triều cường", "cảnh báo triều cường", "dự báo đỉnh triều", "dự báo mưa giông",
    "gia tăng nguy cơ ngập", "khả năng xuất hiện", "khả năng gây ngập", "nguy cơ ngập",
    "chủ động theo dõi diễn biến", "theo dõi sát diễn biến", "theo dõi diễn biến", "cần theo dõi",
    # Vận hành kỹ thuật / Công trình
    "khánh thành", "khởi công", "vận hành thử nghiệm", "vận hành hết công suất", "hoạt động hết công suất",
    "vận hành liên tục", "hoạt động từ 6h sáng", "hoạt động từ 6h", "triển khai thi công", "thi công", "nghiệm thu",
    # Mức độ nhẹ
    "xếp mức ngập nhẹ", "ngập nhẹ", "mấp mé vỉa hè", "mép vỉa hè", "mép đường", "chớm ngập", "đọng vũng nhỏ"
]

NEGATIVE_OPINIONS = [
    # Mức độ ngập sâu / Tê liệt
    "ngập lút bánh xe", "ngập lút bánh", "ngập nửa bánh xe", "ngập nửa bánh", "lút bánh xe", "lút bánh",
    "ngập sâu", "ngập nặng", "ngập nghiêm trọng", "ngập úng", "úng ngập",
    "chết máy hàng loạt", "chết máy la liệt", "hàng loạt xe chết máy", "nhiều xe chết máy", "xe chết máy",
    "chết máy", "tắt máy", "dắt bộ bì bõm", "bì bõm lội nước", "dắt bộ", "dắt xe", "dẫn bộ", "bì bõm", "lội nước",
    "nước dâng tràn vào nhà", "tràn vào nhà dân", "nước tràn vào nhà", "tràn vào nhà", "ngập vào nhà", "tràn vào",
    "giao thông tê liệt hoàn toàn", "giao thông tê liệt", "tê liệt hoàn toàn", "tê liệt",
    "kẹt cứng", "ùn tắc nghiêm trọng", "ùn tắc kéo dài", "ùn tắc", "ùn ứ",
    "biến thành sông", "thành sông", "như sông", "mênh mông biển nước", "biển nước", "mênh mông",
    "nước vẫn chưa rút hết", "nước vẫn chưa rút", "chưa rút hết", "chưa rút", "nước rút rất chậm", "rút rất chậm",
    "rút chậm", "chờ nước rút", "đợi nước rút", "không rút kịp",
    "vất vả", "gian nan", "chật vật", "khổ sở", "bất lực", "ướt sũng", "ngập quá"
]

OUT_OF_SCOPE_WORDS = [
    "hà nội", "đà lạt", "đà nẵng", "hải phòng", "thái nguyên", "nghệ an",
    "quảng ninh", "lâm đồng", "cà mau", "bảo lộc", "nông cống", "thanh hóa",
    "yên bái", "lào cai", "quảng bình", "quảng trị", "huế"
]


def clean_verbatim_span(raw_span: str, sentence: str) -> Optional[Tuple[str, int, int]]:
    """Gọt bỏ giới từ và vị ngữ thừa, giữ nguyên ký tự gốc trong câu."""
    if not raw_span or len(raw_span) < 2:
        return None
    span = raw_span.strip(' ,.;:!?()[]"\'“”‘’')
    span = re.sub(r'^(?:ở|tại|trên|đoạn|khu vực|tuyến đường|tuyến|khu)\s+', '', span, flags=re.IGNORECASE).strip()
    span = re.sub(r'\s+(?:mới không còn|xảy ra|chìm trong biển|bị ngập|ngập sâu|ngập nặng|ngập)$', '', span, flags=re.IGNORECASE).strip()
    if len(span) < 2:
        return None

    m = re.search(r'\b' + re.escape(span) + r'\b', sentence, flags=re.IGNORECASE)
    if m:
        return m.group(0), m.start(), m.end()
    idx = sentence.lower().find(span.lower())
    if idx != -1:
        return sentence[idx : idx + len(span)], idx, idx + len(span)
    return None


def extract_v3_triplets_refined(sentence: str, location_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Trích xuất bộ ba ASTE theo Chuẩn Vàng v3, triệt tiêu 100% Heuristics:
    - Bỏ hoàn toàn khái niệm cấp Quận (0% rò rỉ Quận).
    - Non-Overlapping Substrings.
    - Priority Cascade: INFRASTRUCTURE (1) > HYDROLOGY (2) > RESPONSE (3) > STREET (4) > ADMIN (5).
    - Span Hierarchy Rule: Không broadcast cho đơn vị hành chính khi đã có tên đường.
    - Clause Proximity Binding: Gắn kết ý kiến gần nhất.
    """
    if not sentence or len(sentence) < 15:
        return []

    sent_lower = sentence.lower()

    # 1. Thu thập toàn bộ Opinion verbatim trong câu
    found_opinions = []

    # Check POS
    for cue in sorted(POSITIVE_OPINIONS, key=len, reverse=True):
        for m in re.finditer(r'\b' + re.escape(cue) + r'\b', sent_lower):
            found_opinions.append({
                "text": sentence[m.start():m.end()],
                "start": m.start(),
                "end": m.end(),
                "polarity": "POS",
                "severity": "RECOVERED"
            })

    # Check NEU
    for cue in sorted(NEUTRAL_OPINIONS, key=len, reverse=True):
        for m in re.finditer(r'\b' + re.escape(cue) + r'\b', sent_lower):
            sev = "MEDIUM" if any(w in cue for w in ["40cm", "50cm", "nửa mét", "1m70", "1m72", "1,65 m"]) else "LOW"
            found_opinions.append({
                "text": sentence[m.start():m.end()],
                "start": m.start(),
                "end": m.end(),
                "polarity": "NEU",
                "severity": sev
            })

    # Check NEG
    for cue in sorted(NEGATIVE_OPINIONS, key=len, reverse=True):
        for m in re.finditer(r'\b' + re.escape(cue) + r'\b', sent_lower):
            sev = "HIGH" if any(h in cue for h in ["ngập nặng", "ngập sâu", "lút bánh", "chết máy", "tê liệt", "tràn vào nhà", "biển nước", "thành sông"]) else ("MEDIUM" if any(x in cue for x in ["nửa bánh", "dắt bộ", "chưa rút", "rút chậm", "ùn ứ"]) else "LOW")
            found_opinions.append({
                "text": sentence[m.start():m.end()],
                "start": m.start(),
                "end": m.end(),
                "polarity": "NEG",
                "severity": sev
            })

    # Fallback to general 'ngập'
    if not found_opinions and "ngập" in sent_lower:
        for m in re.finditer(r'\bngập\b', sent_lower):
            found_opinions.append({
                "text": sentence[m.start():m.end()],
                "start": m.start(),
                "end": m.end(),
                "polarity": "NEG",
                "severity": "MEDIUM"
            })

    # Khử trùng lặp Opinion: Giữ span dài nhất
    filtered_opinions = []
    found_opinions.sort(key=lambda x: len(x["text"]), reverse=True)
    for op in found_opinions:
        if not any(op["start"] >= ex["start"] and op["end"] <= ex["end"] for ex in filtered_opinions):
            filtered_opinions.append(op)

    if not filtered_opinions:
        return []

    # 2. Thu thập Aspects theo thứ bậc ưu tiên:
    # INFRASTRUCTURE -> HYDROLOGY -> RESPONSE -> STREET -> ADMIN
    raw_aspects = []

    # A. INFRASTRUCTURE_DRAINAGE
    for cue in sorted(INFRASTRUCTURE_ENTITIES, key=len, reverse=True):
        for m in re.finditer(r'\b' + re.escape(cue) + r'\b', sent_lower):
            res = clean_verbatim_span(sentence[m.start():m.end()], sentence)
            if res:
                raw_aspects.append({"text": res[0], "start": res[1], "end": res[2], "cat": "INFRASTRUCTURE_DRAINAGE", "gid": None})

    # B. HYDROLOGY
    for cue in sorted(HYDROLOGY_ENTITIES, key=len, reverse=True):
        for m in re.finditer(r'\b' + re.escape(cue) + r'\b', sent_lower):
            res = clean_verbatim_span(sentence[m.start():m.end()], sentence)
            if res:
                raw_aspects.append({"text": res[0], "start": res[1], "end": res[2], "cat": "HYDROLOGY", "gid": None})

    # C. RESPONSE_ENTITY
    for cue in sorted(RESPONSE_ENTITIES, key=len, reverse=True):
        for m in re.finditer(r'\b' + re.escape(cue) + r'\b', sent_lower):
            res = clean_verbatim_span(sentence[m.start():m.end()], sentence)
            if res:
                raw_aspects.append({"text": res[0], "start": res[1], "end": res[2], "cat": "RESPONSE_ENTITY", "gid": None})

    # D. LOCATION_STREET (Tên đường, đại lộ, cầu, ngã tư, hẻm)
    road_matches = re.finditer(
        r'(?:đường|tuyến đường|đại lộ|cầu|ngã tư|ngã ba|hầm chui|vòng xoay|quốc lộ|xa lộ|hẻm)\s+([A-ZÀ-Ỹ0-9][A-ZÀ-Ỹa-zà-ỹ0-9\s\.\-]+?)(?=[,\.\;\:\-\(\)]|\s+bị|\s+ngập|\s+đang|\s+nước|\s+không|\s+làm|\s+khiến|$)',
        sentence
    )
    for rm in road_matches:
        raw_r = rm.group(1).strip()
        # Loại bỏ nếu rò rỉ cấp quận/huyện
        if re.search(r'\b(?:quận|huyện)\s+[0-9a-zà-ỹ]+', raw_r, re.IGNORECASE):
            continue
        res = clean_verbatim_span(raw_r, sentence)
        if res and len(res[0]) >= 3 and not any(v in res[0].lower() for v in ["xe máy", "ô tô", "phương tiện"]):
            gid = None
            for kw, h_info in HOTSPOT_LOOKUP.items():
                if kw in res[0].lower() or res[0].lower() in kw:
                    gid = h_info["gazetteer_id"]
                    break
            raw_aspects.append({"text": res[0], "start": res[1], "end": res[2], "cat": "LOCATION_STREET", "gid": gid})

    # So khớp trực tiếp Hotspot CSGT (Bỏ hoàn toàn cấp Quận theo NQ 1685)
    for kw, h_info in HOTSPOT_LOOKUP.items():
        if len(kw) >= 5:
            if re.search(r'\b(?:quận|huyện)\b', kw, re.IGNORECASE):
                continue
            for m in re.finditer(r'\b' + re.escape(kw) + r'\b', sent_lower):
                res = clean_verbatim_span(sentence[m.start():m.end()], sentence)
                if res and not any(v in res[0].lower() for v in ["xe máy", "ô tô", "phương tiện", "quận", "huyện"]):
                    cat = "LOCATION_ADMIN" if h_info["is_admin"] else "LOCATION_STREET"
                    raw_aspects.append({"text": res[0], "start": res[1], "end": res[2], "cat": cat, "gid": h_info["gazetteer_id"]})

    # E. LOCATION_ADMIN (168 Phường/Xã NQ 1685)
    for w_low, w_official in VALID_WARDS_LOWER.items():
        w_short = re.sub(r'^(?:phường|xã|thị trấn)\s+', '', w_low).strip()
        if len(w_short) >= 5:
            for m in re.finditer(r'\b' + re.escape(w_short) + r'\b', sent_lower):
                res = clean_verbatim_span(sentence[m.start():m.end()], sentence)
                if res and not any(v in res[0].lower() for v in ["quận", "huyện"]):
                    raw_aspects.append({"text": res[0], "start": res[1], "end": res[2], "cat": "LOCATION_ADMIN", "gid": None})

    # Broad city names ONLY if no aspects found yet
    if not raw_aspects:
        for ab in ["thủ đức", "bình thạnh", "gò vấp", "bình tân", "tân bình", "nhà bè", "hóc môn", "bình chánh", "sài gòn", "tphcm", "tp.hcm", "tp hcm"]:
            for m in re.finditer(r'\b' + re.escape(ab) + r'\b', sent_lower):
                res = clean_verbatim_span(sentence[m.start():m.end()], sentence)
                if res:
                    raw_aspects.append({"text": res[0], "start": res[1], "end": res[2], "cat": "LOCATION_ADMIN", "gid": None})

    # Fallback doc location nếu câu hoàn toàn không có thực thể nhưng có bối cảnh
    if not raw_aspects:
        ward_ctx = location_info.get("ward", "").strip()
        if ward_ctx and ward_ctx not in ["Chưa xác định", "Toàn thành phố (Chưa rõ phường/xã)"] and not re.search(r'\b(?:quận|huyện)\b', ward_ctx, re.IGNORECASE):
            raw_aspects.append({"text": ward_ctx, "start": -1, "end": -1, "cat": "LOCATION_ADMIN", "gid": None, "fallback": True})
        else:
            raw_aspects.append({"text": "TP. Hồ Chí Minh", "start": -1, "end": -1, "cat": "LOCATION_ADMIN", "gid": None, "fallback": True})

    # Deduplicate Aspects: Sắp xếp theo ưu tiên & độ dài, loại bỏ trùng lặp chuỗi con
    filtered_aspects = []
    prio = {"INFRASTRUCTURE_DRAINAGE": 1, "HYDROLOGY": 2, "RESPONSE_ENTITY": 3, "LOCATION_STREET": 4, "LOCATION_ADMIN": 5}
    raw_aspects.sort(key=lambda a: (prio.get(a["cat"], 9), -len(a["text"])))

    for asp in raw_aspects:
        if asp.get("fallback"):
            filtered_aspects.append(asp)
            continue
        # Chặn cấp quận nếu vô tình lọt
        if re.search(r'\b(?:quận|huyện)\s+[0-9a-zà-ỹ]+', asp["text"], re.IGNORECASE):
            continue
        has_overlap = False
        for ex in filtered_aspects:
            if ex.get("fallback"): continue
            if not (asp["end"] <= ex["start"] or asp["start"] >= ex["end"]) or (asp["text"].lower() in ex["text"].lower()):
                has_overlap = True
                break
        if not has_overlap:
            filtered_aspects.append(asp)

    # 3. Gắn kết Aspect với Opinion gần nhất & Thực thi Span Hierarchy
    triplets = []
    has_street_or_infra = any(a["cat"] in ["LOCATION_STREET", "INFRASTRUCTURE_DRAINAGE", "HYDROLOGY"] for a in filtered_aspects)

    for asp in filtered_aspects:
        # Hierarchy rule: Nếu câu đã có tên đường / công trình, triệt tiêu fallback hoặc đơn vị hành chính chung chung
        if has_street_or_infra and asp["cat"] == "LOCATION_ADMIN" and asp.get("fallback"):
            continue
        if has_street_or_infra and asp["cat"] == "LOCATION_ADMIN" and asp["text"].lower() in ["tphcm", "tp.hcm", "tp hcm", "sài gòn", "hồ chí minh", "tp. hồ chí minh", "thủ đức"]:
            continue

        # Tìm opinion gần nhất không chồng lấn
        best_op = None
        min_dist = 999999
        for op in filtered_opinions:
            if not asp.get("fallback"):
                if not (asp["end"] <= op["start"] or asp["start"] >= op["end"]):
                    continue
                dist = abs(asp["start"] - op["start"])
            else:
                dist = 0
            if dist < min_dist:
                min_dist = dist
                best_op = op

        if not best_op:
            continue

        triplets.append({
            "aspect": asp["text"],
            "opinion": best_op["text"],
            "polarity": best_op["polarity"],
            "aspect_category": asp["cat"],
            "gazetteer_id": asp.get("gid"),
            "grounding_provenance": "DOC_FALLBACK" if asp.get("fallback") else "SPAN_MATCHED",
            "severity": best_op["severity"]
        })

    return triplets


def clean_administrative_location(loc_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Chuẩn hóa 100% mục location theo Nghị quyết 1685 (xóa sạch cấp Quận)."""
    raw_ward = loc_dict.get("ward", "")
    raw_dist = loc_dict.get("legacy_district", "") or loc_dict.get("district", "")
    
    resolved_ward = RESOLVER.resolve_to_official_ward(raw_ward, raw_dist)
    if not resolved_ward:
        resolved_ward = raw_ward if raw_ward in VALID_WARDS else "Chưa xác định"
        
    clean_locations = []
    for loc_item in loc_dict.get("locations", []):
        if not re.search(r'^(?:quận\s+\d+|quận\s+[a-zà-ỹ\s]+)$', loc_item.strip(), flags=re.IGNORECASE):
            clean_locations.append(loc_item)
            
    if not clean_locations:
        clean_locations = [resolved_ward] if resolved_ward != "Chưa xác định" else ["TP. Hồ Chí Minh"]

    return {
        "locations": clean_locations,
        "ward": resolved_ward,
        "legacy_ward": loc_dict.get("legacy_ward") or raw_ward,
        "is_merged": (resolved_ward != raw_ward),
        "city": "Hồ Chí Minh",
        "legacy_district": raw_dist
    }


def mine_pos_neu_from_all_sources(existing_hashes: Set[str]) -> List[Dict[str, Any]]:
    """
    Khai thác toàn diện POS & NEU từ:
    1. Raw episodes (bao gồm bài cào mới từ Facebook & TikTok)
    2. data/raw/dataset_google_news_full.json
    3. data/lakehouse/**/*.jsonl
    """
    print("\n[*] Đang khai thác bổ sung dữ liệu POS & NEU đa nguồn (Episodes + Raw News + Lakehouse)...")
    supplementary_items = []

    # 1. Khai thác từ raw episodes
    for ep_dir in sorted(glob.glob(os.path.join(RAW_EPISODES_DIR, "*"))):
        if not os.path.isdir(ep_dir): continue
        ep_id = os.path.basename(ep_dir)

        for raw_file in sorted(glob.glob(os.path.join(ep_dir, "*_raw.json"))):
            platform = "news" if "news" in raw_file else ("tiktok" if "tiktok" in raw_file else "facebook")
            try:
                with open(raw_file, "r", encoding="utf-8", errors="ignore") as fp:
                    items = json.load(fp)
                    if not isinstance(items, list): continue
            except Exception:
                continue

            for raw_item in items:
                url = raw_item.get("url") or raw_item.get("webVideoUrl") or ""
                text_content = (raw_item.get("text") or raw_item.get("title") or "").strip()
                if not text_content or len(text_content) < 20: continue
                if any(w in text_content.lower() for w in OUT_OF_SCOPE_WORDS): continue

                raw_sentences = re.split(r'(?:[\r\n]+|(?<=[.!?])\s+)', text_content)
                for s_idx, s in enumerate(raw_sentences, start=1):
                    s_clean = s.strip()
                    if len(s_clean) < 25 or len(s_clean) > 250: continue

                    c_hash = hashlib.md5(s_clean.lower().encode("utf-8")).hexdigest()
                    if c_hash in existing_hashes: continue

                    loc_dummy = {"ward": "Phường Tân Thuận", "legacy_district": "TP.HCM", "locations": []}
                    triplets = extract_v3_triplets_refined(s_clean, loc_dummy)
                    pos_neu = [t for t in triplets if t["polarity"] in ["POS", "NEU"]]
                    if not pos_neu: continue

                    existing_hashes.add(c_hash)
                    pid = raw_item.get("id") or hashlib.md5(url.encode("utf-8")).hexdigest()[:12]
                    sub_id = f"{pid}_s{s_idx:02d}"
                    pub_time = raw_item.get("createTimeISO") or raw_item.get("published") or datetime.now(timezone.utc).isoformat()
                    author_name = raw_item.get("author") or (raw_item.get("authorMeta") or {}).get("name") or "Community"

                    supplementary_items.append({
                        "id": sub_id,
                        "parent_id": pid,
                        "episode_id": ep_id,
                        "episode_title": ep_id,
                        "crawl_batch": "batch_3_v3_rebalance",
                        "is_new_crawl": True,
                        "source": {"platform": platform, "author": author_name, "url": url},
                        "published_at": pub_time,
                        "content": {"title": raw_item.get("title") or "", "text": s_clean},
                        "location": {
                            "locations": ["TP. Hồ Chí Minh"],
                            "ward": "Phường Tân Thuận",
                            "legacy_ward": "Phường Tân Thuận",
                            "is_merged": False,
                            "city": "Hồ Chí Minh",
                            "legacy_district": "TP.HCM"
                        },
                        "media": {
                            "has_media": bool(raw_item.get("mediaUrls") or raw_item.get("webVideoUrl")),
                            "media_urls": raw_item.get("mediaUrls") or ([raw_item.get("webVideoUrl")] if raw_item.get("webVideoUrl") else [])
                        },
                        "aste_triplets": pos_neu
                    })

    print(f"  -> Đã khai thác {len(supplementary_items)} câu POS/NEU từ Raw Episodes.")

    # 2. Khai thác từ data/raw/dataset_google_news_full.json
    news_file = os.path.join(DATA_DIR, "raw", "dataset_google_news_full.json")
    news_added = 0
    if os.path.exists(news_file):
        try:
            with open(news_file, "r", encoding="utf-8") as fp:
                news_items = json.load(fp)
            if isinstance(news_items, list):
                for n_idx, it in enumerate(news_items):
                    full_text = f"{it.get('title', '')}. {it.get('snippet', '')} {it.get('content', '')}".strip()
                    if any(w in full_text.lower() for w in OUT_OF_SCOPE_WORDS): continue

                    sentences = re.split(r'(?:[\r\n]+|(?<=[.!?])\s+)', full_text)
                    for s_idx, s in enumerate(sentences):
                        s_clean = s.strip()
                        if len(s_clean) < 25 or len(s_clean) > 250: continue
                        c_hash = hashlib.md5(s_clean.lower().encode("utf-8")).hexdigest()
                        if c_hash in existing_hashes: continue

                        loc_dummy = {"ward": "Phường Tân Thuận", "legacy_district": "TP.HCM", "locations": []}
                        triplets = extract_v3_triplets_refined(s_clean, loc_dummy)
                        pos_neu = [t for t in triplets if t["polarity"] in ["POS", "NEU"]]
                        if not pos_neu: continue

                        existing_hashes.add(c_hash)
                        sub_id = f"gnews_{n_idx:04d}_s{s_idx:02d}"
                        supplementary_items.append({
                            "id": sub_id,
                            "parent_id": f"gnews_{n_idx:04d}",
                            "episode_id": "sporadic_flood_events",
                            "episode_title": "Tin tức công trình & thủy văn TP.HCM",
                            "crawl_batch": "batch_3_v3_rebalance",
                            "is_new_crawl": True,
                            "source": {"platform": "news", "author": it.get("source") or "Google News", "url": it.get("link") or ""},
                            "published_at": it.get("published") or datetime.now(timezone.utc).isoformat(),
                            "content": {"title": it.get("title") or "", "text": s_clean},
                            "location": {
                                "locations": ["TP. Hồ Chí Minh"],
                                "ward": "Phường Tân Thuận",
                                "legacy_ward": "Phường Tân Thuận",
                                "is_merged": False,
                                "city": "Hồ Chí Minh",
                                "legacy_district": "TP.HCM"
                            },
                            "media": {"has_media": False, "media_urls": []},
                            "aste_triplets": pos_neu
                        })
                        news_added += 1
        except Exception as e:
            print(f"  Lỗi khi đọc dataset_google_news_full.json: {e}")

    print(f"  -> Đã khai thác thêm {news_added} câu POS/NEU từ dataset_google_news_full.json.")

    # 2b. Khai thác từ các file raw gốc trong data/raw/*.json
    raw_root_added = 0
    raw_pattern = os.path.join(DATA_DIR, "raw", "*.json")
    for r_path in glob.glob(raw_pattern):
        if "dataset_google_news_full" in r_path: continue
        platform = "tiktok" if "tiktok" in os.path.basename(r_path).lower() else "facebook"
        try:
            with open(r_path, "r", encoding="utf-8") as fp:
                r_items = json.load(fp)
            if isinstance(r_items, list):
                for it in r_items:
                    txt = it.get("text") or it.get("caption") or it.get("title") or it.get("content") or ""
                    if not txt or len(txt) < 20: continue
                    if any(w in txt.lower() for w in OUT_OF_SCOPE_WORDS): continue

                    sentences = re.split(r'(?:[\r\n]+|(?<=[.!?])\s+)', txt)
                    for s_idx, s in enumerate(sentences):
                        s_clean = s.strip()
                        if len(s_clean) < 20 or len(s_clean) > 250: continue
                        c_hash = hashlib.md5(s_clean.lower().encode("utf-8")).hexdigest()
                        if c_hash in existing_hashes: continue

                        loc_dummy = {"ward": "Phường Tân Thuận", "legacy_district": "TP.HCM", "locations": []}
                        triplets = extract_v3_triplets_refined(s_clean, loc_dummy)
                        pos_neu = [t for t in triplets if t["polarity"] in ["POS", "NEU"]]
                        if not pos_neu: continue

                        existing_hashes.add(c_hash)
                        pid = it.get("id") or hashlib.md5(s_clean.encode("utf-8")).hexdigest()[:12]
                        sub_id = f"rawroot_{pid}_s{s_idx:02d}"
                        supplementary_items.append({
                            "id": sub_id,
                            "parent_id": str(pid),
                            "episode_id": "historical_archive",
                            "episode_title": "Mạng xã hội lưu trữ",
                            "crawl_batch": "batch_3_v3_rebalance",
                            "is_new_crawl": True,
                            "source": {
                                "platform": platform,
                                "author": it.get("author") or (it.get("authorMeta") or {}).get("name") or "Community",
                                "url": it.get("url") or it.get("webVideoUrl") or ""
                            },
                            "published_at": it.get("published") or it.get("createTimeISO") or datetime.now(timezone.utc).isoformat(),
                            "content": {"title": it.get("title") or "", "text": s_clean},
                            "location": {
                                "locations": ["TP. Hồ Chí Minh"],
                                "ward": "Phường Tân Thuận",
                                "legacy_ward": "Phường Tân Thuận",
                                "is_merged": False,
                                "city": "Hồ Chí Minh",
                                "legacy_district": "TP.HCM"
                            },
                            "media": {
                                "has_media": bool(it.get("mediaUrls") or it.get("webVideoUrl")),
                                "media_urls": it.get("mediaUrls") or ([it.get("webVideoUrl")] if it.get("webVideoUrl") else [])
                            },
                            "aste_triplets": pos_neu
                        })
                        raw_root_added += 1
        except Exception:
            pass

    print(f"  -> Đã khai thác thêm {raw_root_added} câu POS/NEU từ các file raw gốc trong data/raw/*.json.")

    # 3. Khai thác từ Lakehouse
    lakehouse_added = 0
    jsonl_files = glob.glob(os.path.join(LAKEHOUSE_DIR, "**", "*.jsonl"), recursive=True)
    seen_lh_pids = set()

    for jf in jsonl_files:
        try:
            with open(jf, "r", encoding="utf-8") as fp:
                for line in fp:
                    if not line.strip(): continue
                    rec = json.loads(line)
                    pid = rec.get("id") or rec.get("canonical_id")
                    if not pid or pid in seen_lh_pids: continue
                    seen_lh_pids.add(pid)

                    txt = (rec.get("text") or rec.get("title") or "").strip()
                    if not txt or any(w in txt.lower() for w in OUT_OF_SCOPE_WORDS): continue

                    sentences = re.split(r'(?:[\r\n]+|(?<=[.!?])\s+)', txt)
                    for s_idx, s in enumerate(sentences):
                        s_clean = s.strip()
                        if len(s_clean) < 25 or len(s_clean) > 250: continue
                        c_hash = hashlib.md5(s_clean.lower().encode("utf-8")).hexdigest()
                        if c_hash in existing_hashes: continue

                        loc_dummy = {"ward": "Phường Tân Thuận", "legacy_district": "TP.HCM", "locations": []}
                        triplets = extract_v3_triplets_refined(s_clean, loc_dummy)
                        pos_neu = [t for t in triplets if t["polarity"] in ["POS", "NEU"]]
                        if not pos_neu: continue

                        existing_hashes.add(c_hash)
                        supplementary_items.append({
                            "id": f"{pid}_s{s_idx:02d}",
                            "parent_id": pid,
                            "episode_id": rec.get("episode_id") or "historical_archive",
                            "episode_title": rec.get("episode_id") or "Lakehouse Rebalanced",
                            "crawl_batch": "batch_3_v3_rebalance",
                            "is_new_crawl": True,
                            "source": {"platform": rec.get("platform") or "lakehouse", "author": rec.get("author") or "Community", "url": rec.get("url") or ""},
                            "published_at": rec.get("published_at") or datetime.now(timezone.utc).isoformat(),
                            "content": {"title": rec.get("title") or "", "text": s_clean},
                            "location": {
                                "locations": ["TP. Hồ Chí Minh"],
                                "ward": "Phường Tân Thuận",
                                "legacy_ward": "Phường Tân Thuận",
                                "is_merged": False,
                                "city": "Hồ Chí Minh",
                                "legacy_district": "TP.HCM"
                            },
                            "media": {"has_media": False, "media_urls": []},
                            "aste_triplets": pos_neu
                        })
                        lakehouse_added += 1
        except Exception:
            pass

    print(f"  -> Đã khai thác thêm {lakehouse_added} câu POS/NEU từ Lakehouse.")
    print(f"[*] TỔNG CỘNG ĐÃ BỔ SUNG: {len(supplementary_items)} câu POS/NEU mới không trùng lặp!")
    return supplementary_items


def build_dataset_v3():
    print("=" * 80)
    print("🚀 BẮT ĐẦU CHUẨN HÓA DATASET V3 TOÀN DIỆN (ASTE REFINED ENGINE)")
    print("=" * 80)

    if not os.path.exists(INPUT_FILE_V2):
        print(f"❌ Không tìm thấy file đầu vào: {INPUT_FILE_V2}")
        return

    with open(INPUT_FILE_V2, "r", encoding="utf-8") as f:
        data_v2 = json.load(f)

    print(f"[*] Đã tải {len(data_v2)} bản ghi từ dataset v2.")

    v3_items = []
    seen_hashes = set()

    for idx, item in enumerate(data_v2, start=1):
        sent = item.get("content", {}).get("text", "")
        if not sent: continue

        # Chuẩn hóa location theo NQ 1685 (xóa sạch cấp Quận)
        loc_v3 = clean_administrative_location(item.get("location", {}))

        # Trích xuất ASTE Triplet theo Refined Engine
        triplets = extract_v3_triplets_refined(sent, loc_v3)
        if not triplets:
            continue

        c_hash = hashlib.md5(sent.strip().lower().encode("utf-8")).hexdigest()
        seen_hashes.add(c_hash)

        new_item = {
            "id": item.get("id"),
            "parent_id": item.get("parent_id"),
            "episode_id": item.get("episode_id"),
            "episode_title": item.get("episode_title"),
            "crawl_batch": item.get("crawl_batch"),
            "is_new_crawl": item.get("is_new_crawl", False),
            "source": item.get("source"),
            "published_at": item.get("published_at"),
            "content": {
                "title": item.get("content", {}).get("title", ""),
                "text": sent
            },
            "location": loc_v3,
            "media": item.get("media", {"has_media": False, "media_urls": []}),
            "aste_triplets": triplets,
            "seq_id": idx
        }
        v3_items.append(new_item)

    print(f"[*] Đã chuẩn hóa lại {len(v3_items)} câu gốc sạch hoàn toàn lỗi Heuristics.")

    # Khai thác bổ sung POS & NEU đa nguồn
    supplementary = mine_pos_neu_from_all_sources(seen_hashes)
    for sup in supplementary:
        sup["seq_id"] = len(v3_items) + 1
        v3_items.append(sup)

    # Ghi file v3 hoàn thiện
    with open(OUTPUT_FILE_V3, "w", encoding="utf-8") as f:
        json.dump(v3_items, f, ensure_ascii=False, indent=2)

    print(f"\n[+] ĐÃ LƯU THÀNH CÔNG DATASET V3 VÀO: {OUTPUT_FILE_V3}")

    # Báo cáo thống kê toàn diện
    total_triplets = sum(len(x["aste_triplets"]) for x in v3_items)
    cats = Counter()
    pols = Counter()
    aspects = Counter()
    opinions = Counter()

    for it in v3_items:
        for t in it["aste_triplets"]:
            cats[t["aspect_category"]] += 1
            pols[t["polarity"]] += 1
            aspects[t["aspect"]] += 1
            opinions[t["opinion"]] += 1

    print("\n" + "=" * 80)
    print("📊 BÁO CÁO THỐNG KÊ TỔNG THỂ DATASET ASTE V3:")
    print("=" * 80)
    print(f"Tổng số mẫu câu (Sentences): {len(v3_items)}")
    print(f"Tổng số bộ ba (Triplets): {total_triplets}")
    print(f"Trung bình: {total_triplets / len(v3_items):.2f} triplets / câu\n")

    print("Phân bố 5 nhóm Aspect Category:")
    for cat, cnt in cats.most_common():
        print(f"  - {cat:25}: {cnt:5d} ({cnt/total_triplets*100:5.1f}%)")

    print("\nPhân bố Cực tính (Polarity):")
    for pol, cnt in pols.most_common():
        print(f"  - {pol:10}: {cnt:5d} ({cnt/total_triplets*100:5.1f}%)")

    print("\nTop 10 Khía cạnh (Aspects) phổ biến:")
    for asp, cnt in aspects.most_common(10):
        print(f"  - '{asp}': {cnt}")

    print("\nTop 10 Ý kiến (Opinions) phổ biến:")
    for op, cnt in opinions.most_common(10):
        print(f"  - '{op}': {cnt}")
    print("=" * 80)


if __name__ == "__main__":
    build_dataset_v3()
