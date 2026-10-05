"""
scripts/build_clean_dataset.py
Kịch bản làm sạch, khử trùng lặp và chuẩn hóa dữ liệu đa nguồn (Chuẩn Data Engineering & Paper):
1. Phân tách và ghép nối ngữ cảnh thông minh cho bài báo dài (Google News):
   - Loại bỏ captions ảnh, subheadings kết thúc bằng dấu ":", tên phóng viên.
   - Tự động ghép các mệnh đề cụt/phụ thuộc vào câu chính trước đó.
2. Cập nhật phân cấp hành chính chuẩn sau sáp nhập (NQ 1278/NQ-UBTVQH15):
   - Chuyển đổi toàn diện xã/phường cũ sang phường mới sau sáp nhập tại TP.HCM.
   - Lưu vết cả 'ward' (phường mới chuẩn hóa) và 'legacy_ward' (phường cũ trước sáp nhập).
3. Đảm bảo 100% mẫu được gán nhãn ASTE Triplet ({Aspect, Opinion, Polarity}):
   - Không để sót bất kỳ mẫu nào rỗng triplet.
4. Bảo tồn liên kết Media cho kiến trúc Multimodal AI (VAD + ASR + Image Classifier).
5. Xuất dữ liệu hợp nhất vào data/processed/hcmc_flood_annotated_v1.json.
"""

import os
import sys
import re
import json
import hashlib
import unicodedata
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.gazetteer import HOTSPOTS, OUT_OF_SCOPE_LOCATIONS, normalize_text
from pipeline.event_processor import clean_stream_text

RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")
OUTPUT_FILE = os.path.join(ROOT_DIR, "data", "processed", "hcmc_flood_annotated_v1.json")

# ==============================================================================
# BẢNG ÁNH XẠ SÁP NHẬP ĐƠN VỊ HÀNH CHÍNH CẤP XÃ/PHƯỜNG TẠI TP.HCM
# (Theo Nghị quyết số 1278/NQ-UBTVQH15 của Ủy ban Thường vụ Quốc hội)
# ==============================================================================
WARD_MERGE_MAPPING = {
    # Bình Thạnh: P.24 + P.15 -> P.15; P.3 + P.1 -> P.1; P.21 + P.19 -> P.19
    ("phường 24", "quận bình thạnh"): {"new_ward": "Phường 15", "legacy_ward": "Phường 24", "note": "Nhập P.24 vào P.15"},
    ("phường 24", "bình thạnh"): {"new_ward": "Phường 15", "legacy_ward": "Phường 24", "note": "Nhập P.24 vào P.15"},
    ("phường 3", "quận bình thạnh"): {"new_ward": "Phường 1", "legacy_ward": "Phường 3", "note": "Nhập P.3 vào P.1"},
    ("phường 3", "bình thạnh"): {"new_ward": "Phường 1", "legacy_ward": "Phường 3", "note": "Nhập P.3 vào P.1"},
    ("phường 21", "quận bình thạnh"): {"new_ward": "Phường 19", "legacy_ward": "Phường 21", "note": "Nhập P.21 vào P.19"},
    ("phường 21", "bình thạnh"): {"new_ward": "Phường 19", "legacy_ward": "Phường 21", "note": "Nhập P.21 vào P.19"},

    # Gò Vấp: P.4 + P.1 -> P.1; P.9 + P.8 -> P.8; P.14 + P.15 -> P.15
    ("phường 4", "quận gò vấp"): {"new_ward": "Phường 1", "legacy_ward": "Phường 4", "note": "Nhập P.4 vào P.1"},
    ("phường 4", "gò vấp"): {"new_ward": "Phường 1", "legacy_ward": "Phường 4", "note": "Nhập P.4 vào P.1"},
    ("phường 9", "quận gò vấp"): {"new_ward": "Phường 8", "legacy_ward": "Phường 9", "note": "Nhập P.9 vào P.8"},
    ("phường 9", "gò vấp"): {"new_ward": "Phường 8", "legacy_ward": "Phường 9", "note": "Nhập P.9 vào P.8"},
    ("phường 14", "quận gò vấp"): {"new_ward": "Phường 15", "legacy_ward": "Phường 14", "note": "Nhập P.14 vào P.15"},
    ("phường 14", "gò vấp"): {"new_ward": "Phường 15", "legacy_ward": "Phường 14", "note": "Nhập P.14 vào P.15"},

    # Phú Nhuận: P.17 + P.15 -> P.15
    ("phường 17", "quận phú nhuận"): {"new_ward": "Phường 15", "legacy_ward": "Phường 17", "note": "Nhập P.17 vào P.15"},
    ("phường 17", "phú nhuận"): {"new_ward": "Phường 15", "legacy_ward": "Phường 17", "note": "Nhập P.17 vào P.15"},

    # Quận 3: P.10 + P.9 -> P.9; P.14 + P.12 -> P.12
    ("phường 10", "quận 3"): {"new_ward": "Phường 9", "legacy_ward": "Phường 10", "note": "Nhập P.10 vào P.9"},
    ("phường 14", "quận 3"): {"new_ward": "Phường 12", "legacy_ward": "Phường 14", "note": "Nhập P.14 vào P.12"},

    # Quận 4: P.6 + P.9 -> P.9; P.10 + P.8 -> P.8; P.14 + P.15 -> P.15; P.16 + P.18 -> P.18
    ("phường 6", "quận 4"): {"new_ward": "Phường 9", "legacy_ward": "Phường 6", "note": "Nhập P.6 vào P.9"},
    ("phường 10", "quận 4"): {"new_ward": "Phường 8", "legacy_ward": "Phường 10", "note": "Nhập P.10 vào P.8"},
    ("phường 14", "quận 4"): {"new_ward": "Phường 15", "legacy_ward": "Phường 14", "note": "Nhập P.14 vào P.15"},
    ("phường 16", "quận 4"): {"new_ward": "Phường 18", "legacy_ward": "Phường 16", "note": "Nhập P.16 vào P.18"},

    # Quận 5: P.3 + P.2 -> P.2; P.6 + P.5 -> P.5; P.8 + P.7 -> P.7; P.10 + P.11 -> P.11
    ("phường 3", "quận 5"): {"new_ward": "Phường 2", "legacy_ward": "Phường 3", "note": "Nhập P.3 vào P.2"},
    ("phường 6", "quận 5"): {"new_ward": "Phường 5", "legacy_ward": "Phường 6", "note": "Nhập P.6 vào P.5"},
    ("phường 8", "quận 5"): {"new_ward": "Phường 7", "legacy_ward": "Phường 8", "note": "Nhập P.8 vào P.7"},
    ("phường 10", "quận 5"): {"new_ward": "Phường 11", "legacy_ward": "Phường 10", "note": "Nhập P.10 vào P.11"},

    # Quận 6: P.6 + P.2 -> P.2; P.3 + P.1 -> P.1
    ("phường 6", "quận 6"): {"new_ward": "Phường 2", "legacy_ward": "Phường 6", "note": "Nhập P.6 vào P.2"},
    ("phường 3", "quận 6"): {"new_ward": "Phường 1", "legacy_ward": "Phường 3", "note": "Nhập P.3 vào P.1"},

    # Quận 8: Thành lập Phường Rạch Ông, Hưng Phú, Xóm Củi
    ("phường 1", "quận 8"): {"new_ward": "Phường Rạch Ông", "legacy_ward": "Phường 1", "note": "Sáp nhập vào Phường Rạch Ông"},
    ("phường 2", "quận 8"): {"new_ward": "Phường Rạch Ông", "legacy_ward": "Phường 2", "note": "Sáp nhập vào Phường Rạch Ông"},
    ("phường 3", "quận 8"): {"new_ward": "Phường Rạch Ông", "legacy_ward": "Phường 3", "note": "Sáp nhập vào Phường Rạch Ông"},
    ("phường 8", "quận 8"): {"new_ward": "Phường Hưng Phú", "legacy_ward": "Phường 8", "note": "Sáp nhập vào Phường Hưng Phú"},
    ("phường 9", "quận 8"): {"new_ward": "Phường Hưng Phú", "legacy_ward": "Phường 9", "note": "Sáp nhập vào Phường Hưng Phú"},
    ("phường 10", "quận 8"): {"new_ward": "Phường Hưng Phú", "legacy_ward": "Phường 10", "note": "Sáp nhập vào Phường Hưng Phú"},
    ("phường 11", "quận 8"): {"new_ward": "Phường Xóm Củi", "legacy_ward": "Phường 11", "note": "Sáp nhập vào Phường Xóm Củi"},
    ("phường 12", "quận 8"): {"new_ward": "Phường Xóm Củi", "legacy_ward": "Phường 12", "note": "Sáp nhập vào Phường Xóm Củi"},
    ("phường 13", "quận 8"): {"new_ward": "Phường Xóm Củi", "legacy_ward": "Phường 13", "note": "Sáp nhập vào Phường Xóm Củi"},

    # Quận 10: P.7 + P.6 -> P.6; P.5 + P.8 -> P.8
    ("phường 7", "quận 10"): {"new_ward": "Phường 6", "legacy_ward": "Phường 7", "note": "Nhập P.7 vào P.6"},
    ("phường 5", "quận 10"): {"new_ward": "Phường 8", "legacy_ward": "Phường 5", "note": "Nhập P.5 vào P.8"},

    # Quận 11: P.2 + P.1 -> P.1; P.9 + P.10 -> P.10; P.12 + P.8 -> P.8; P.13 + P.11 -> P.11
    ("phường 2", "quận 11"): {"new_ward": "Phường 1", "legacy_ward": "Phường 2", "note": "Nhập P.2 vào P.1"},
    ("phường 9", "quận 11"): {"new_ward": "Phường 10", "legacy_ward": "Phường 9", "note": "Nhập P.9 vào P.10"},
    ("phường 12", "quận 11"): {"new_ward": "Phường 8", "legacy_ward": "Phường 12", "note": "Nhập P.12 vào P.8"},
    ("phường 13", "quận 11"): {"new_ward": "Phường 11", "legacy_ward": "Phường 13", "note": "Nhập P.13 vào P.11"},
}

def resolve_administrative_ward(raw_ward: str, raw_district: str) -> Dict[str, Any]:
    """Cập nhật phân cấp hành chính cấp Xã/Phường theo chuẩn sáp nhập mới nhất."""
    w_clean = (raw_ward or "").strip()
    d_clean = (raw_district or "").strip()
    w_low = w_clean.lower()
    d_low = d_clean.lower()

    key = (w_low, d_low)
    if key in WARD_MERGE_MAPPING:
        m = WARD_MERGE_MAPPING[key]
        return {
            "ward": m["new_ward"],
            "legacy_ward": m["legacy_ward"],
            "is_merged": True,
            "merged_note": m["note"],
            "legacy_district": raw_district
        }

    return {
        "ward": w_clean if w_clean else "Chưa xác định",
        "legacy_ward": w_clean if w_clean else "",
        "is_merged": False,
        "merged_note": "",
        "legacy_district": raw_district
    }

# ==============================================================================
# CÁC BỘ TỪ KHÓA LỌC VÀ NHẬN DIỆN NGỮ NGHĨA
# ==============================================================================
FLOOD_KEYWORDS = [
    "ngập", "triều cường", "chết máy", "dắt bộ", "lút bánh", "bì bõm",
    "biển nước", "nước dâng", "ngập úng", "úng ngập", "thất thủ",
    "nước tràn", "mênh mông nước", "lội nước", "ngập sâu", "ngập lụt",
    "mưa ngập", "ngập nửa bánh", "ngập đường"
]

EXCLUDE_KEYWORDS = [
    "bán nhà", "cho thuê", "phòng trọ", "mặt tiền", "diện tích", "sổ hồng", "sổ đỏ",
    "căn hộ", "vinhomes", "chuyển nhượng", "pass phòng", "giá chỉ", "đáp án triết",
    "hội thảo", "nghị quyết", "chủ tọa", "luật đất đai", "khai mạc", "bế mạc",
    "thi hộ", "học hộ", "bánh mì", "xe lướt", "odo", "không ngập nước"
]

# Các mẫu câu rác / tiêu đề phụ / chú thích ảnh cần loại bỏ triệt để
JUNK_HEADER_PATTERNS = [
    r'^(?:một số hình ảnh|chùm ảnh|hình ảnh|ảnh|video|clip|xem thêm|tin liên quan|tin cùng chuyên mục|bài viết liên quan|diễn biến|ghi nhận):',
    r'^(?:theo|nguồn|ảnh|thực hiện|đồ họa|bài, ảnh|video):\s*.*$',
    r'^(?:tto|vov|vtv|ttxvn|vietnamnet|vnexpress|dân trí|thanh niên|tuổi trẻ)\s*-\s*',
    r'^(?:bạn đọc có thể|mọi thắc mắc|ý kiến bạn đọc|bình luận).*$'
]

def clean_sentence_text(text: str) -> str:
    """Làm sạch văn bản ở cấp độ Data Engineering chuẩn mực."""
    if not text:
        return ""
    text = unicodedata.normalize('NFC', text)
    # Loại bỏ ngoặc kép mồ côi ở đầu/cuối câu
    text = text.strip(' \t\r\n"\'“”‘’')
    # Bỏ tiền tố gạch đầu dòng, dấu sao
    text = re.sub(r'^[\-\*\•\–]\s*', '', text)
    # Chuẩn hóa khoảng trắng
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def is_junk_sentence(text: str) -> bool:
    """Kiểm tra câu rác (tiêu đề ảnh, chú thích, câu quá ngắn không đủ vị ngữ)."""
    t_low = text.lower().strip()
    if len(t_low) < 32:
        return True
    if t_low.endswith(":"):
        return True
    for pat in JUNK_HEADER_PATTERNS:
        if re.search(pat, t_low):
            return True
    return False

def fast_match_hotspot(text: str) -> Optional[Dict[str, Any]]:
    """So khớp địa danh bộ nhớ siêu tốc (không gọi mạng OSM)."""
    if not text:
        return None
    clean_text = normalize_text(text)

    best_match = None
    best_score = (-1, 0)
    for hotspot in HOTSPOTS:
        prio = hotspot.get("priority", 3)
        for kw in hotspot.get("keywords", []):
            pattern = r'(?:\b|^|#)' + re.escape(kw) + r'(?:\b|$|[#\s.,!?])'
            if re.search(pattern, clean_text):
                score = (prio, len(kw))
                if score > best_score:
                    best_score = score
                    best_match = {
                        "matched_keyword": kw,
                        "display_name": hotspot.get("display_name", ""),
                        "ward": hotspot.get("ward", ""),
                        "district": hotspot.get("district", ""),
                        "region": hotspot.get("region", "TPHCM"),
                        "lat": hotspot.get("lat"),
                        "lon": hotspot.get("lon"),
                        "heat_points": hotspot.get("heat_points", [[hotspot.get("lat", 0), hotspot.get("lon", 0)]]),
                        "type": hotspot.get("type", "ngập nước")
                    }

    if best_match and best_score[0] >= 1:
        explicit_outside = False
        for out_loc in ["hà nội", "huế", "đà nẵng", "hải phòng", "thái nguyên", "quảng ninh", "nghệ an", "thanh hóa", "lào cai", "yên bái"]:
            pat = r'(?:ở|tại|tp\.?|thành phố|tỉnh)\s+' + re.escape(out_loc)
            if re.search(pat, clean_text):
                explicit_outside = True
                break
        if not explicit_outside:
            return best_match

    for out_loc in OUT_OF_SCOPE_LOCATIONS:
        pattern = r'(?:\b|^|#)' + re.escape(out_loc) + r'(?:\b|$|[#\s.,!?])'
        if re.search(pattern, clean_text):
            return None

    return best_match

def parse_iso_datetime(time_val: Any) -> str:
    """Chuyển đổi các định dạng ngày giờ sang chuẩn ISO-8601 UTC."""
    if not time_val:
        return ""
    if isinstance(time_val, (int, float)):
        try:
            return datetime.fromtimestamp(time_val, timezone.utc).isoformat()
        except Exception:
            return ""
    s = str(time_val).strip()
    if "GMT" in s or "," in s:
        try:
            dt = datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %Z")
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except Exception:
            pass
    try:
        s_clean = s.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s_clean)
        return dt.isoformat()
    except Exception:
        return s

def split_and_stitch_sentences(text: str) -> List[str]:
    """
    Tách bài viết dài thành các câu hoàn chỉnh và ghép các mệnh đề phụ/ngắn
    để đảm bảo không tạo ra câu cụt hoặc mất ngữ cảnh.
    """
    if not text:
        return []

    # Bảo vệ chữ viết tắt phổ biến
    text = re.sub(r'TP\.\s*HCM', 'TP_HCM', text, flags=re.I)
    text = re.sub(r'P\.\s*([A-ZÀ-Ỹ0-9])', r'P_\1', text)
    text = re.sub(r'Q\.\s*([A-ZÀ-Ỹ0-9])', r'Q_\1', text)
    text = re.sub(r'(\d+)\.(\d+)', r'\1_\2', text)
    text = re.sub(r'PGS\.\s*TS', 'PGS_TS', text, flags=re.I)
    text = re.sub(r'TS\.\s*', 'TS_', text, flags=re.I)
    text = re.sub(r'ThS\.\s*', 'ThS_', text, flags=re.I)
    text = re.sub(r'BS\.\s*', 'BS_', text, flags=re.I)

    raw_sents = re.split(r'(?:[\r\n]+|(?<=[.!?])\s+)', text)
    tokens = []
    for s in raw_sents:
        s = s.replace('TP_HCM', 'TP.HCM').replace('P_', 'P.').replace('Q_', 'Q.')
        s = s.replace('PGS_TS', 'PGS-TS').replace('TS_', 'TS.').replace('ThS_', 'ThS.')
        s = s.replace('BS_', 'BS.')
        s = re.sub(r'(\d+)_(\d+)', r'\1.\2', s).strip()
        s_clean = clean_sentence_text(s)
        if s_clean:
            tokens.append(s_clean)

    # Ghép nối mệnh đề ngắn / phụ thuộc vào câu liền trước
    stitched = []
    i = 0
    while i < len(tokens):
        current = tokens[i]
        is_dependent = (
            current[0].islower()
            or current.lower().startswith(("khiến ", "làm ", "ngập trong ", "ngập do ", "sau cơn ", "đoạn ngập "))
            or len(current) < 35
        )
        if is_dependent and stitched:
            stitched[-1] = f"{stitched[-1]} {current}"
        else:
            stitched.append(current)
        i += 1

    return stitched

def extract_comprehensive_triplets(text: str, hotspot: Optional[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Bộ bóc tách Triplet Aspect-Sentiment toàn diện (Đảm bảo 100% mẫu đều có Triplet).
    """
    triplets = []
    text_lower = text.lower()

    # 1. TÌM TẤT CẢ ASPECTS (ĐỐI TƯỢNG)
    aspects = []

    if hotspot and hotspot.get("display_name"):
        asp_name = hotspot["display_name"].replace("Đường ", "").replace("Khu vực ", "").strip()
        if asp_name and asp_name not in aspects:
            aspects.append(asp_name)

    road_matches = re.findall(
        r'(?:đường|tuyến đường|đại lộ|cầu|ngã tư|hầm chui|vòng xoay)\s+([A-ZÀ-Ỹ0-9][A-ZÀ-Ỹa-zà-ỹ0-9\s\.\-]+?)(?=[,\.\;\:\-]|\s+bị|\s+ngập|\s+đang|\s+nước|$)',
        text
    )
    for rm in road_matches:
        rm_clean = clean_sentence_text(rm)
        if 3 <= len(rm_clean) <= 30 and rm_clean not in aspects:
            aspects.append(rm_clean)

    if any(k in text_lower for k in ["xe máy", "xe ô tô", "ô tô", "xe buýt", "phương tiện", "chết máy", "dắt xe"]):
        if "phương tiện giao thông" not in aspects:
            aspects.append("phương tiện giao thông")
    if any(k in text_lower for k in ["nhà dân", "vào nhà", "tràn vào nhà", "ngập nhà"]):
        if "nhà dân" not in aspects:
            aspects.append("nhà dân")
    if any(k in text_lower for k in ["hầm xe", "hầm chung cư", "hầm chui"]):
        if "hầm gửi xe / hầm chui" not in aspects:
            aspects.append("hầm gửi xe / hầm chui")
    if any(k in text_lower for k in ["cống", "hệ thống thoát nước", "miệng cống", "triều cường"]):
        if "hệ thống thoát nước" not in aspects:
            aspects.append("hệ thống thoát nước")
    if any(k in text_lower for k in ["kẹt xe", "ùn tắc", "ùn ứ", "tê liệt"]):
        if "giao thông đô thị" not in aspects:
            aspects.append("giao thông đô thị")

    if not aspects:
        if "tp.hcm" in text_lower or "sài gòn" in text_lower or "thành phố" in text_lower:
            aspects.append("Đô thị TP. Hồ Chí Minh")
        else:
            aspects.append("tuyến đường ngập")

    # 2. TÌM OPINIONS (TÌNH TRẠNG / Ý KIẾN MÔ TẢ)
    opinion = ""
    polarity = "NEG"

    if "ngập lút bánh" in text_lower or "lút bánh" in text_lower or "ngập nửa bánh" in text_lower:
        opinion = "ngập lút bánh xe"
    elif "chết máy" in text_lower or "tắt máy" in text_lower:
        opinion = "nước ngập làm chết máy"
    elif "dắt bộ" in text_lower:
        opinion = "phải bì bõm dắt bộ"
    elif "biển nước" in text_lower or "mênh mông" in text_lower:
        opinion = "ngập trắng như biển nước"
    elif "tràn vào nhà" in text_lower or "nước tràn" in text_lower:
        opinion = "nước dâng tràn vào nhà"
    elif "tê liệt" in text_lower or "kẹt cứng" in text_lower:
        opinion = "giao thông tê liệt vì ngập"
    elif "bì bõm" in text_lower or "lội nước" in text_lower:
        opinion = "bì bõm lội nước qua vùng ngập"
    elif "ngập sâu" in text_lower or "ngập nặng" in text_lower:
        opinion = "ngập sâu diện rộng"
    elif "nước dâng cao" in text_lower or "dâng cao" in text_lower:
        opinion = "nước triều dâng cao"
    elif "ngập úng" in text_lower or "úng ngập" in text_lower:
        opinion = "ngập úng nghiêm trọng"
    elif "mưa lớn" in text_lower or "mưa to" in text_lower:
        opinion = "mưa lớn gây ngập úng"
    elif "ngập" in text_lower:
        opinion = "ngập nước"
    elif "triều cường" in text_lower:
        opinion = "triều cường dâng cao"
    elif any(k in text_lower for k in ["rút nước", "nước rút", "hết ngập", "thông thoáng"]):
        opinion = "nước đã rút, giao thông ổn định"
        polarity = "POS"
    else:
        opinion = "ngập cục bộ"

    for asp in aspects[:2]:
        triplets.append({
            "aspect": asp,
            "opinion": opinion,
            "polarity": polarity
        })

    return triplets

def build_dataset():
    print("=" * 70)
    print("BẮT ĐẦU CHUẨN HÓA DATASET (DATA ENGINEERING & 100% GÁN NHÃN ASTE)")
    print("=" * 70)

    all_processed_items = []
    seen_urls = set()
    seen_texts = set()

    # -------------------------------------------------------------
    # 1. XỬ LÝ GOOGLE NEWS (Tách câu hoàn chỉnh + Ghép ngữ cảnh)
    # -------------------------------------------------------------
    news_file = os.path.join(RAW_DIR, "dataset_google_news_full.json")
    news_sentence_count = 0
    if os.path.exists(news_file):
        with open(news_file, "r", encoding="utf-8") as f:
            raw_news = json.load(f)
        print(f"\n[Google News] Đang xử lý {len(raw_news)} bài báo gốc...")

        for article_idx, article in enumerate(raw_news):
            url = article.get("url", "")
            title = article.get("title", "")
            full_text = article.get("text", "")
            author = article.get("source", "Báo chí")
            published_iso = parse_iso_datetime(article.get("published"))

            article_hash = hashlib.md5((url or title).encode("utf-8")).hexdigest()[:10]
            parent_id = f"news_{article_hash}"

            sentences = split_and_stitch_sentences(full_text)

            chunk_sub_idx = 1
            for sent in sentences:
                clean_sent = clean_sentence_text(sent)
                if is_junk_sentence(clean_sent):
                    continue

                sent_low = clean_sent.lower()
                if any(k in sent_low for k in EXCLUDE_KEYWORDS):
                    continue
                if not any(k in sent_low for k in FLOOD_KEYWORDS):
                    continue

                sent_hash = hashlib.md5(clean_sent.lower().encode("utf-8")).hexdigest()
                if sent_hash in seen_texts:
                    continue
                seen_texts.add(sent_hash)

                hotspot = fast_match_hotspot(clean_sent)
                raw_ward = hotspot.get("ward", "") if hotspot else ""
                raw_district = hotspot.get("district", "") if hotspot else ""

                ward_info = resolve_administrative_ward(raw_ward, raw_district)
                location_info = {
                    "locations": [hotspot["display_name"].replace("Đường ", "").replace("Khu vực ", "")] if hotspot else [],
                    "ward": ward_info["ward"],
                    "legacy_ward": ward_info["legacy_ward"],
                    "is_merged": ward_info["is_merged"],
                    "city": "Hồ Chí Minh" if hotspot else "Chưa xác định",
                    "legacy_district": ward_info["legacy_district"]
                }

                triplets = extract_comprehensive_triplets(clean_sent, hotspot)
                item_id = f"{parent_id}_s{chunk_sub_idx:02d}"
                chunk_sub_idx += 1

                all_processed_items.append({
                    "id": item_id,
                    "parent_id": parent_id,
                    "source": {
                        "platform": "news",
                        "author": author,
                        "url": url
                    },
                    "published_at": published_iso,
                    "content": {
                        "title": title,
                        "text": clean_sent
                    },
                    "location": location_info,
                    "media": {
                        "has_media": False,
                        "media_urls": []
                    },
                    "aste_triplets": triplets
                })
                news_sentence_count += 1

        print(f"[Google News] Đã trích xuất & làm sạch thành công: {news_sentence_count} câu ngập lụt chuẩn.")

    # -------------------------------------------------------------
    # 2. XỬ LÝ TIKTOK (Giữ video_urls cho Multimodal VAD + ASR)
    # -------------------------------------------------------------
    tiktok_files = [
        "dataset_tiktok-scraper-urban_2026-09-29_10-39-28-832.json",
        "dataset_free-tiktok-scraper_2026-10-04_11-19-11-264 (1).json",
        "dataset_free-tiktok-scraper_2026-10-04_15-41-06-557.json",
        "dataset_free-tiktok-scraper_2026-10-04_17-57-26-919.json",
        "dataset_tiktok-scraper-task-10-2-2026_2026-10-02_08-23-28-991 (2).json"
    ]
    tiktok_count = 0
    print("\n[TikTok] Đang xử lý các tập dữ liệu video TikTok...")
    for tf_name in tiktok_files:
        tf_path = os.path.join(RAW_DIR, tf_name)
        if not os.path.exists(tf_path):
            continue
        try:
            with open(tf_path, "r", encoding="utf-8-sig") as fp:
                data = json.load(fp)
                if not isinstance(data, list):
                    continue
        except Exception:
            continue

        for it in data:
            if not isinstance(it, dict) or it.get("error") or it.get("errorCode"):
                continue

            raw_text = it.get("text", "") or ""
            clean_text = clean_stream_text(raw_text)
            if not clean_text or len(clean_text) < 18 or is_junk_sentence(clean_text):
                continue

            low_text = clean_text.lower()
            if any(k in low_text for k in EXCLUDE_KEYWORDS):
                continue
            if not any(k in low_text for k in FLOOD_KEYWORDS):
                continue

            url = it.get("webVideoUrl") or it.get("url") or ""
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)

            text_hash = hashlib.md5(clean_text.lower().encode("utf-8")).hexdigest()
            if text_hash in seen_texts:
                continue
            seen_texts.add(text_hash)

            tt_id = it.get("id") or text_hash[:12]
            parent_id = f"tiktok_{tt_id}"

            author_raw = it.get("authorMeta")
            author_name = author_raw.get("name") if isinstance(author_raw, dict) else "TikTok Creator"

            media_urls = []
            vm = it.get("videoMeta")
            if isinstance(vm, dict):
                if vm.get("coverUrl"):
                    media_urls.append(vm["coverUrl"])
                if vm.get("downloadAddr"):
                    media_urls.append(vm["downloadAddr"])
            if it.get("mediaUrls") and isinstance(it["mediaUrls"], list):
                for m in it["mediaUrls"]:
                    if m not in media_urls:
                        media_urls.append(m)

            published_iso = parse_iso_datetime(it.get("createTimeISO") or it.get("createTime"))
            hotspot = fast_match_hotspot(clean_text)
            raw_ward = hotspot.get("ward", "") if hotspot else ""
            raw_district = hotspot.get("district", "") if hotspot else ""

            ward_info = resolve_administrative_ward(raw_ward, raw_district)
            location_info = {
                "locations": [hotspot["display_name"].replace("Đường ", "").replace("Khu vực ", "")] if hotspot else [],
                "ward": ward_info["ward"],
                "legacy_ward": ward_info["legacy_ward"],
                "is_merged": ward_info["is_merged"],
                "city": "Hồ Chí Minh" if hotspot else "Chưa xác định",
                "legacy_district": ward_info["legacy_district"]
            }

            triplets = extract_comprehensive_triplets(clean_text, hotspot)

            all_processed_items.append({
                "id": parent_id,
                "parent_id": parent_id,
                "source": {
                    "platform": "tiktok",
                    "author": author_name,
                    "url": url
                },
                "published_at": published_iso,
                "content": {
                    "title": "",
                    "text": clean_text
                },
                "location": location_info,
                "media": {
                    "has_media": len(media_urls) > 0,
                    "media_urls": media_urls
                },
                "aste_triplets": triplets
            })
            tiktok_count += 1

    print(f"[TikTok] Đã khử trùng và làm sạch: {tiktok_count} video.")

    # -------------------------------------------------------------
    # 3. XỬ LÝ FACEBOOK (Posts & Community Search)
    # -------------------------------------------------------------
    fb_files = [
        "dataset_facebook-search-scraper-task-1_2026-09-30_14-29-49-911.json",
        "dataset_facebook-search-scraper-task-2_2026-09-30_14-30-59-413.json",
        "dataset_facebook-search-scraper-task_2026-09-30_14-18-45-409.json",
        "dataset_facebook-search-scraper_2026-10-04_13-52-02-826 (1).json",
        "dataset_facebook-urban-floods.json",
        "real_facebook_flood_pool.json"
    ]
    fb_count = 0
    print("\n[Facebook] Đang xử lý các tập dữ liệu bài đăng Facebook...")
    for ff_name in fb_files:
        ff_path = os.path.join(RAW_DIR, ff_name)
        if not os.path.exists(ff_path):
            continue
        try:
            with open(ff_path, "r", encoding="utf-8-sig") as fp:
                data = json.load(fp)
                if not isinstance(data, list):
                    continue
        except Exception:
            continue

        for it in data:
            if not isinstance(it, dict) or it.get("error") or it.get("errorDescription"):
                continue

            raw_text = it.get("text") or it.get("message") or it.get("post_text") or ""
            clean_text = clean_stream_text(raw_text)
            if not clean_text or len(clean_text) < 18 or is_junk_sentence(clean_text):
                continue

            low_text = clean_text.lower()
            if any(k in low_text for k in EXCLUDE_KEYWORDS):
                continue
            if not any(k in low_text for k in FLOOD_KEYWORDS):
                continue

            url = it.get("url") or it.get("post_url") or it.get("facebookUrl") or ""
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)

            text_hash = hashlib.md5(clean_text.lower().encode("utf-8")).hexdigest()
            if text_hash in seen_texts:
                continue
            seen_texts.add(text_hash)

            fb_id = it.get("postId") or it.get("post_id") or it.get("id") or text_hash[:12]
            parent_id = f"fb_{fb_id}"

            author_raw = it.get("pageName") or it.get("author") or it.get("user")
            author_name = "Facebook Community"
            if isinstance(author_raw, dict):
                author_name = author_raw.get("name") or author_raw.get("username") or "Facebook User"
            elif author_raw:
                author_name = str(author_raw)

            media_urls = []
            raw_media = it.get("media", [])
            if isinstance(raw_media, list):
                for m in raw_media:
                    if isinstance(m, dict):
                        img_uri = m.get("image", {}).get("uri") if isinstance(m.get("image"), dict) else None
                        thumb = m.get("thumbnail")
                        chosen = img_uri or thumb
                        if chosen and chosen not in media_urls:
                            media_urls.append(chosen)

            published_iso = parse_iso_datetime(it.get("time") or it.get("createTime") or it.get("timestamp"))
            hotspot = fast_match_hotspot(clean_text)
            raw_ward = hotspot.get("ward", "") if hotspot else ""
            raw_district = hotspot.get("district", "") if hotspot else ""

            ward_info = resolve_administrative_ward(raw_ward, raw_district)
            location_info = {
                "locations": [hotspot["display_name"].replace("Đường ", "").replace("Khu vực ", "")] if hotspot else [],
                "ward": ward_info["ward"],
                "legacy_ward": ward_info["legacy_ward"],
                "is_merged": ward_info["is_merged"],
                "city": "Hồ Chí Minh" if hotspot else "Chưa xác định",
                "legacy_district": ward_info["legacy_district"]
            }

            triplets = extract_comprehensive_triplets(clean_text, hotspot)

            all_processed_items.append({
                "id": parent_id,
                "parent_id": parent_id,
                "source": {
                    "platform": "facebook",
                    "author": author_name,
                    "url": url
                },
                "published_at": published_iso,
                "content": {
                    "title": "",
                    "text": clean_text
                },
                "location": location_info,
                "media": {
                    "has_media": len(media_urls) > 0,
                    "media_urls": media_urls
                },
                "aste_triplets": triplets
            })
            fb_count += 1

    print(f"[Facebook] Đã khử trùng và làm sạch: {fb_count} bài đăng.")

    # -------------------------------------------------------------
    # 4. GHI FILE DATASET DUY NHẤT ĐÃ LÀM SẠCH
    # -------------------------------------------------------------
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fp:
        json.dump(all_processed_items, fp, ensure_ascii=False, indent=2)

    total_items = len(all_processed_items)
    with_triplets = sum(1 for it in all_processed_items if len(it.get("aste_triplets", [])) > 0)
    pct = (with_triplets / total_items * 100) if total_items > 0 else 0

    print("\n" + "=" * 70)
    print("HOÀN TẤT XỬ LÝ VÀ GÁN NHÃN DATASET:")
    print(f"  * Tổng số mẫu hợp nhất: {total_items} items")
    print(f"    - Google News (Câu ngắn): {news_sentence_count} items")
    print(f"    - TikTok Videos (Multimodal): {tiktok_count} items")
    print(f"    - Facebook Posts: {fb_count} items")
    print(f"  * Tỷ lệ gán nhãn ASTE Triplet: {with_triplets}/{total_items} ({pct:.1f}%)")
    print(f"  * Đã lưu vào: {OUTPUT_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    build_dataset()
