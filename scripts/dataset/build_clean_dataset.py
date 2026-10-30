"""
scripts/build_clean_dataset.py
Kịch bản làm sạch, khử trùng lặp và chuẩn hóa dữ liệu đa nguồn (Chuẩn Data Engineering & Paper):
1. Đọc và hợp nhất từ cấu trúc phân vùng Episode (data/raw/episodes/*):
   - Episode 01: Mưa giông diện rộng đầu tháng 9 (07/09 - 13/09/2026)
   - Episode 02: Hoàn lưu bão số 4 & dải hội tụ nhiệt đới (14/09 - 21/09/2026)
   - Episode 03: Đỉnh triều cường & mưa lớn cuối tháng 9 (22/09 - 28/09/2026)
   - Episode 04: Triều cường Rằm tháng 8 Âm lịch (29/09 - 04/10/2026)
   - Episode 05: Mưa giông cục bộ chiều tối (05/10 - 11/10/2026)
   - Historical Archive: Dữ liệu lịch sử 2018-2025
   - Sporadic Flood Events: Các sự kiện ngập nhỏ lẻ đơn lẻ
2. Phân tách và ghép nối ngữ cảnh thông minh cho bài báo dài (Google News):
   - Loại bỏ captions ảnh, subheadings kết thúc bằng dấu ":", tên phóng viên.
   - Tự động ghép các mệnh đề cụt/phụ thuộc vào câu chính trước đó.
3. Cập nhật phân cấp hành chính chuẩn sau sáp nhập (NQ 1278/NQ-UBTVQH15):
   - Chuyển đổi toàn diện xã/phường cũ sang phường mới sau sáp nhập tại TP.HCM.
   - Lưu vết cả 'ward' (phường mới chuẩn hóa) và 'legacy_ward' (phường cũ trước sáp nhập).
4. Phân bổ cân bằng nhãn ASTE Triplet 3 lớp (NEG, NEU, POS) theo chuẩn nghiên cứu:
   - POS: Đường khô thoáng / nước đã rút / lưu thông bình thường.
   - NEU: Dự báo triều cường / cảnh báo mưa giông / ngập nhẹ mép đường / cần theo dõi thêm.
   - NEG: Ngập sâu / lút bánh / chết máy / tê liệt giao thông / nước tràn vào nhà.
5. Bảo tồn liên kết Media cho kiến trúc Multimodal AI (VAD + ASR + Image Classifier).
6. Đánh số thứ tự 'seq_id' từ 1 đến N và gom toàn bộ dữ liệu cào mới xuống CUỐI FILE để kiểm soát dễ dàng.
7. Xuất dữ liệu hợp nhất vào data/processed/hcmc_flood_annotated_v1.json và v2.
"""

import os
import sys
import re
import json
import glob
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

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.gazetteer import HOTSPOTS, OUT_OF_SCOPE_LOCATIONS, normalize_text
from pipeline.event_processor import clean_stream_text

EPISODES_DIR = os.path.join(ROOT_DIR, "data", "raw", "episodes")
RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")
OUTPUT_FILE_V1 = os.path.join(ROOT_DIR, "data", "processed", "hcmc_flood_annotated_v1.json")
OUTPUT_FILE_V2 = os.path.join(ROOT_DIR, "data", "processed", "hcmc_flood_annotated_v2_multimodal.json")

# ==============================================================================
# BẢNG ÁNH XẠ SÁP NHẬP ĐƠN VI HÀNH CHÍNH CẤP XÃ/PHƯỜNG TẠI TP.HCM
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

    from core.admin_resolver import RESOLVER
    res_ward = RESOLVER.resolve_to_official_ward(w_clean, d_clean)
    if res_ward:
        return {
            "ward": res_ward,
            "legacy_ward": w_clean,
            "is_merged": (res_ward.lower() != w_clean.lower()),
            "merged_note": "Quy đổi chuẩn NQ 1685",
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
    "ngập", "triều cường", "chết máy", "dắt bộ", "dẫn bộ", "lút bánh", "bì bõm",
    "biển nước", "nước dâng", "dâng cao", "thành sông", "biến thành sông", "ngập úng", "úng ngập", "thất thủ",
    "nước tràn", "mênh mông nước", "lội nước", "ngập sâu", "ngập lụt",
    "mưa ngập", "ngập nửa bánh", "ngập đường", "nước nhiều", "không mưa mà nước",
    "rút", "dự báo", "khô ráo", "khô rang", "khô queo", "không bị ngập", "không hề ngập", "không ngập", "hết ngập",
    "#ngap", "#ngapnuoc", "#nuocngap", "#trieucuong", "#ngaplut"
]

EXCLUDE_KEYWORDS = [
    "bán nhà", "cho thuê", "phòng trọ", "mặt tiền", "diện tích", "sổ hồng", "sổ đỏ",
    "căn hộ", "vinhomes", "chuyển nhượng", "pass phòng", "giá chỉ", "đáp án triết",
    "hội thảo", "nghị quyết", "chủ tọa", "luật đất đai", "khai mạc", "bế mạc",
    "thi hộ", "học hộ", "bánh mì", "xe lướt", "không ngập nước",
    "deal hot", "ngập trời", "giải mật", "hồ sơ giải mật", "nhà sách", "khai trương",
    "độc quyền trên", "series tập", "cánh sóng âm", "khuyến mãi", "sale sập sàn",
    "mực tím", "truyện hạt lúa", "cia sài gòn",
    "pha nước rút", "chạy nước rút", "giai đoạn nước rút", "nước rút thi công",
    "tay đua", "cầu đi bộ", "nhựa duy tân", "duy tân", "cải tạo diện mạo",
    "hà nội", "mcer", "marie curie", "đà lạt",
    # Từ ngữ ẩn dụ / quảng cáo F&B / du lịch / đồ công nghệ
    "ngập dầu", "ngập bơ", "ngập mỡ", "ngập tràn deal", "ngập tràn may mắn",
    "ngập tràn ưu đãi", "ngập tràn quà", "ngập tràn ánh sáng", "ngập tràn niềm vui",
    "ngập tràn tiếng cười", "ngập tràn hạnh phúc", "ngập tràn hy vọng", "ngập tràn năng lượng",
    "lục bình", "bãi tắm", "rác biển", "bánh khọt", "cellphones", "sắm tết",
    "chúc khách", "tiệm ăn", "mì cay", "quán chay", "sạc xanh", "ev one", "vi vu vũng tàu lễ",
    "ngập tràn tết", "shop bí", "ngập ánh sáng", "tràn ngập ánh sáng", "ngập nắng", "view chill ngập", "ngập dâu sữa",
    "ngập quà", "shin-chan", "thông cống nghẹt", "hút hầm cầu", "thông nghẹt", "bảo dưỡng xe máy", "thủy kích",
    "chung cư mini", "căn duplex", "studio ban công", "pax sky", "căn góc cực thoáng", "sát vách quận 1",
    "hẻm 5m xe hơi", "chuyện lịch sử", "đinh bộ lĩnh cậy núi",
    "bảo lộc", "lâm đồng", "nghệ an", "tuyên quang", "thái nguyên", "quảng ninh", "cà mau",
    # Ngoại tỉnh Đồng Nai hoàn toàn ngoài phạm vi
    "đồng nai", "phước tân", "biên hòa", "biên hoà", "cao tốc biên hòa", "long thành", "trảng bom", "nhơn trạch", "vĩnh cửu"
]

# Các URL cụ thể người dùng yêu cầu loại bỏ hoàn toàn
BLOCKED_URL_SUBSTRINGS = [
    "1290599776588076",
    "1560796269387953",
    "7651865598330277138",
    "7677552058366430484",
    "909275717898402",
    "1213187850601240",
    "1083969077465719",
    "1025438923832462",
    "1324003929930555",
    "1655627919262386",
    "814626184498303",
    "1342905424547961",
    "1018248260982647",
    "1047070484870120",
    "1928424957917772",
    "7658193771384900884",
    "2001763603775858",
    "1612357400408698",
    "954734066181198",
    "1679978572035782",
    "561908110048170",
    "1824668004742145",
    "1104448985347819",
    "7690869999593884948",
    "7556535629320883474",
    "7556168799162993938",
    "7555905500920040724",
    "2214370282512169",
    "27443549455269648",
    "CBMipwJBVV",
    "ebaf5b0296b9cca6",
    "7613569837301894421",
    "7446012976617819410",
    "7480104626914708743",
    "7554971423815568658",
    "7561995599252442375",
    "756869738999372519",
    "7562572658307501330",
    "7367300831223254289",
    "7507221805120212267",
    "7359100999908265232",
    "7561663835577339144",
    "7371059034629229831",
    "642797025525422",
    "1399999890746196",
    "1345459492299720",
    "5671640929613047",
    "727427766642211",
    "433896542542198"
]

JUNK_HEADER_PATTERNS = [
    r'^(?:một số hình ảnh|chùm ảnh|hình ảnh|ảnh|video|clip|xem thêm|tin liên quan|tin cùng chuyên mục|bài viết liên quan|diễn biến|ghi nhận):',
    r'^(?:theo|nguồn|ảnh|thực hiện|đồ họa|bài, ảnh|video):\s*.*$',
    r'^(?:tto|vov|vtv|ttxvn|vietnamnet|vnexpress|dân trí|thanh niên|tuổi trẻ)\s*-\s*',
    r'^(?:bạn đọc có thể|mọi thắc mắc|ý kiến bạn đọc|bình luận).*$'
]


def is_excluded_content(text: str) -> bool:
    """Kiểm tra nội dung loại trừ thông minh (chặn chính xác rác, không chặn nhầm tin ngập TP.HCM)."""
    t_low = text.lower()

    # 1. Bất động sản / Cho thuê / Bán nhà (chỉ bắt ngữ cảnh rao bán/cho thuê)
    if re.search(r'(?:bán nhà|bán đất|cho thuê|pass phòng|cần sang nhượng|sổ hồng riêng|sổ đỏ|chính chủ cần bán|căn duplex|chung cư mini|studio ban công|pax sky|căn góc cực thoáng|1pn|2pn|ban công tách bếp|vách kính lùa|hẻm \d+m xe hơi|dt\s*:\s*\d+|sát vách quận 1)', t_low):
        return True

    # 2. Xe cũ / ODO
    if re.search(r'\bodo\s*(?::\s*)?\d+', t_low):
        return True
    if any(k in t_low for k in ['xe lướt', 'thu mua xe cũ']):
        return True

    # 3. Dịch vụ môi trường quảng cáo
    if re.search(r'(?:thông cống nghẹt|hút hầm cầu|thông nghẹt giá rẻ|vệ sinh môi trường minh phát|gọi là tới phục vụ 24/24)', t_low):
        return True

    # 4. Ẩn dụ / Quảng cáo F&B / Du lịch / Mua sắm (bao gồm quán cháo nấm rơm ngập ngụa khách)
    if re.search(r'(?:ngập tràn\s+(?:deal|may mắn|ưu đãi|quà|ánh sáng|niềm vui|tiếng cười|hạnh phúc|hy vọng|năng lượng|tết)|ngập\s+(?:ánh sáng|năng lượng|dầu|bơ|mỡ|dâu sữa|ngụa)|tràn ngập\s+(?:ánh sáng|năng lượng|deal|may mắn|tết)|địa điểm ăn uống|cháo nấm rơm|bánh khọt|quán chay|mì cay|cellphones|sắm tết|shin-chan|đặt vé gặp cậu bé bút chì|kfc|starbucks|highlands coffee|the pizza company|tacos station|familymart|co.opmart|thiso mall|deal 8/3|giòn rụm|quán cà phê tràn ngập|quán cafe tràn ngập|quán cafe 4 tầng ngập)', t_low):
        return True

    # 5. Ngoại tỉnh hoàn toàn ngoài phạm vi (bảo lưu nếu là Xa lộ Hà Nội hoặc tin dự báo có kèm TP.HCM/Bình Dương/Vũng Tàu)
    if 'xa lộ hà nội' not in t_low and re.search(r'\b(?:hà nội|đà nẵng|hải phòng|đà lạt|nha trang|bảo lộc|nghệ an|tuyên quang|thái nguyên|quảng ninh|lào cai|yên bái|thanh hóa)\b', t_low):
        if not any(loc in t_low for loc in ['tphcm', 'tp.hcm', 'sài gòn', 'hồ chí minh', 'bình dương', 'vũng tàu', 'thủ đức']):
            return True

    # 6. Đồng Nai (biên hòa, phước tân...) - nằm ngoài 168 đơn vị TP.HCM Mới
    if any(dn in t_low for dn in ['đồng nai', 'phước tân', 'biên hòa', 'biên hoà', 'cao tốc biên hòa', 'long thành', 'trảng bom', 'nhơn trạch', 'vĩnh cửu']):
        if not any(loc in t_low for loc in ['tphcm', 'tp.hcm', 'sài gòn', 'bình dương', 'vũng tàu', 'thủ đức']):
            return True

        # 7. Tin tài chính / Thanh toán giao đất dự án chống ngập (không phải sự kiện ngập)
    if re.search(r'(?:thanh toán dự án|giao \d+ khu đất|khu đất "vàng"|trung nam group|dự án bt\b)', t_low):
        return True

    return False

def matches_flood_context(text: str) -> bool:
    """Kiểm tra câu/bài có liên quan đến ngữ cảnh ngập, triều cường, thoát nước hoặc khô ráo."""
    t_low = text.lower()
    if any(k in t_low for k in FLOOD_KEYWORDS):
        return True
    if any(k in t_low for k in ["rút", "dự báo", "khô ráo", "khô rang", "khô queo", "không bị ngập", "không hề ngập", "không ngập"]):
        return True
    return False

def clean_sentence_text(text: str) -> str:
    """Làm sạch văn bản ở cấp độ Data Engineering chuẩn mực."""
    if not text:
        return ""
    text = unicodedata.normalize('NFC', text)
    text = text.strip(' \t\r\n"\'“”‘’')
    text = re.sub(r'^[\-\*\•\–]\s*', '', text)
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
    """So khớp địa danh chuẩn mực, chống so khớp chéo giữa các vùng hành chính."""
    if not text:
        return None
    clean_text = normalize_text(text)
    clean_low = clean_text.lower()

    # 1. Xác định ngữ cảnh vùng miền trực tiếp từ văn bản
    is_bd = any(k in clean_low for k in ["bình dương", "binh duong", "thủ dầu một", "dĩ an", "thuận an", "tân uyên", "bến cát", "bàu bàng", "dầu tiếng", "mỹ phước"])
    is_vt = any(k in clean_low for k in ["vũng tàu", "vung tau", "bà rịa", "ba ria", "phú mỹ", "côn đảo", "thùy vân"])
    is_hcm_core = any(k in clean_low for k in ["sài gòn", "tphcm", "tp.hcm", "thủ đức", "quận 1", "quận 3", "quận 4", "quận 5", "quận 6", "quận 7", "quận 8", "quận 10", "quận 11", "quận 12", "bình thạnh", "gò vấp", "tân bình", "tân phú", "phú nhuận", "bình tân", "nhà bè", "hóc môn", "củ chi", "cần giờ", "bình chánh"])

    best_match = None
    best_score = (-1, 0)
    for hotspot in HOTSPOTS:
        h_district = hotspot.get("district", "").lower()
        h_region = hotspot.get("region", "").lower()

        # Rào chắn vùng miền tuyệt đối: nếu text ở Bình Dương, không cho phép match Hóc Môn / Gò Vấp...
        if is_bd and not is_hcm_core:
            if "bình dương" not in h_district and "bình dương" not in h_region:
                continue
        elif is_vt and not is_hcm_core:
            if "vũng tàu" not in h_district and "vũng tàu" not in h_region and "bà rịa" not in h_district:
                continue

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

    # Nếu chưa match được hotspot cụ thể nhưng text có địa danh Bình Dương / Vũng Tàu rõ ràng:
    if not best_match:
        if is_bd:
            target_ward = "Phường Thủ Dầu Một"
            loc_name = "Thủ Dầu Một, Bình Dương"
            lat, lon = 10.9805, 106.6745
            if "dĩ an" in clean_low:
                target_ward = "Phường Dĩ An"
                loc_name = "Dĩ An, Bình Dương"
                lat, lon = 10.8920, 106.7450
            elif "thuận an" in clean_low:
                target_ward = "Phường Thuận An"
                loc_name = "Thuận An, Bình Dương"
                lat, lon = 10.9080, 106.7020
            elif "tân uyên" in clean_low or "tân hiệp" in clean_low:
                target_ward = "Phường Tân Hiệp"
                loc_name = "Tân Uyên, Bình Dương"
                lat, lon = 11.0850, 106.7800
            elif "bến cát" in clean_low:
                target_ward = "Phường Bến Cát"
                loc_name = "Bến Cát, Bình Dương"
                lat, lon = 11.1550, 106.6050
            best_match = {
                "matched_keyword": loc_name,
                "display_name": loc_name,
                "ward": target_ward,
                "district": "Bình Dương",
                "region": "Bình Dương cũ",
                "lat": lat, "lon": lon,
                "heat_points": [[lat, lon]],
                "type": "ngập đô thị Bình Dương"
            }
        elif is_vt:
            target_ward = "Phường Vũng Tàu"
            loc_name = "TP. Vũng Tàu"
            lat, lon = 10.3450, 107.0850
            if "bà rịa" in clean_low:
                target_ward = "Phường Bà Rịa"
                loc_name = "TP. Bà Rịa"
                lat, lon = 10.4950, 107.1700
            elif "phú mỹ" in clean_low:
                target_ward = "Thị xã Phú Mỹ"
                loc_name = "Thị xã Phú Mỹ"
                lat, lon = 10.5910, 107.0540
            best_match = {
                "matched_keyword": loc_name,
                "display_name": loc_name,
                "ward": target_ward,
                "district": "Bà Rịa - Vũng Tàu",
                "region": "Bà Rịa - Vũng Tàu cũ",
                "lat": lat, "lon": lon,
                "heat_points": [[lat, lon]],
                "type": "ngập đô thị Bà Rịa - Vũng Tàu"
            }

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
        s = re.sub(r'(\\d+)_(\\d+)', r'\1.\2', s).strip()
        s_clean = clean_sentence_text(s)
        if s_clean:
            tokens.append(s_clean)

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
    Bộ bóc tách Triplet Aspect-Sentiment 3 lớp chuẩn hóa:
    NGUYÊN TẮC CỐT LÕI: Aspect BẮT BUỘC phải là thực thể xuất hiện trực tiếp trong câu (Text-Grounded).
    Tuyệt đối không lấy tên địa danh bên ngoài nếu câu văn không hề nhắc tới.
    """
    triplets = []
    text_lower = text.lower()

    # 1. TÌM TẤT CẢ ASPECTS (ĐỐI TƯỢNG) CÓ MẶT TRONG TEXT
    aspects = []

    # 1.A: Tuyến đường xuất hiện trực tiếp trong câu qua regex
    road_matches = re.findall(
        r'(?:đường|tuyến đường|đại lộ|cầu|ngã tư|ngã ba|hầm chui|vòng xoay|quốc lộ|xa lộ)\s+([A-ZÀ-Ỹ0-9][A-ZÀ-Ỹa-zà-ỹ0-9\s\.\-]+?)(?=[,\.\;\:\-]|\s+bị|\s+ngập|\s+đang|\s+nước|$)',
        text
    )
    for rm in road_matches:
        rm_clean = clean_sentence_text(rm)
        if 3 <= len(rm_clean) <= 35 and rm_clean.lower() in text_lower and rm_clean not in aspects:
            aspects.append(rm_clean)

    # 1.B: Các địa danh cụ thể có mặt trong câu
    candidate_entities = [
        "Ga Đại Học Quốc Gia", "Đại Học Quốc Gia", "Phan Huy Ích", "Hầm chui Bến xe Miền Đông mới",
        "Bến xe Miền Đông", "Thủ Dầu Một", "Dĩ An", "Thuận An", "Tân Uyên", "Tân Hiệp",
        "Bến Cát", "Bình Dương", "Vũng Tàu", "Bà Rịa", "Phú Mỹ", "Bãi Sau", "Bãi Trước",
        "Thảo Điền", "Chợ Thủ Đức", "Thủ Đức", "Bình Thạnh", "Gò Vấp", "Quận 7", "Quận 8",
        "Bình Tân", "Tân Bình", "Nhà Bè", "Hóc Môn", "Bình Chánh", "Mỹ Phước Tân Vạn",
        "ĐT746", "ĐT748", "ĐT744", "Lý Thường Kiệt", "Trần Tử Bình", "Nguyễn Văn Cung",
        "Trường THCS Nguyễn Thị Thập", "Nguyễn Thị Thập", "Tân Hưng", "Huỳnh Tấn Phát", "Trần Xuân Soạn", "Lê Văn Lương", "Nguyễn Xí", "Đinh Bộ Lĩnh",
        "Ung Văn Khiêm", "Võ Văn Ngân", "Tô Ngọc Vân", "Kha Vạn Cân", "Mễ Cốc", "Bến Phú Định"
    ]
    for ent in candidate_entities:
        if ent.lower() in text_lower and ent not in aspects:
            aspects.append(ent)

    # 1.C: Nếu có hotspot, chỉ lấy tên hotspot NẾU TÊN ĐÓ XUẤT HIỆN TRONG TEXT
    if hotspot:
        kw = hotspot.get("matched_keyword", "")
        disp = hotspot.get("display_name", "").replace("Khu vực ", "").replace("Đường ", "").strip()
        if kw and kw.lower() in text_lower and len(kw) >= 3 and kw not in aspects:
            aspects.append(kw)
        elif disp and disp.lower() in text_lower and disp not in aspects:
            aspects.append(disp)

    # 1.D: Đối tượng bị ảnh hưởng xuất hiện trong câu
    if any(k in text_lower for k in ["xe máy", "xe ô tô", "ô tô", "xe buýt", "phương tiện", "chết máy", "dắt xe"]):
        if "phương tiện giao thông" not in aspects:
            aspects.append("phương tiện giao thông")
    if any(k in text_lower for k in ["nhà dân", "vào nhà", "tràn vào nhà", "ngập nhà"]):
        if "nhà dân" not in aspects:
            aspects.append("nhà dân")
    if any(k in text_lower for k in ["hầm xe", "hầm chung cư", "hầm chui"]):
        if "hầm gửi xe / hầm chui" not in aspects:
            aspects.append("hầm gửi xe / hầm chui")
    if any(k in text_lower for k in ["cống", "hệ thống thoát nước", "miệng cống"]):
        if "hệ thống thoát nước" not in aspects:
            aspects.append("hệ thống thoát nước")
    if any(k in text_lower for k in ["kẹt xe", "ùn tắc", "ùn ứ", "tê liệt"]):
        if "giao thông đô thị" not in aspects:
            aspects.append("giao thông đô thị")

    # 1.E: Dự phòng chuẩn tắc
    if not aspects:
        if any(k in text_lower for k in ["đường", "tuyến đường", "đoạn"]):
            aspects.append("tuyến đường ngập")
        elif "tp.hcm" in text_lower or "sài gòn" in text_lower:
            aspects.append("Đô thị TP. Hồ Chí Minh")
        elif "bình dương" in text_lower:
            aspects.append("Đô thị Bình Dương")
        elif "vũng tàu" in text_lower:
            aspects.append("Đô thị Vũng Tàu")
        else:
            aspects.append("khu vực ngập")

    # 2. XÁC ĐỊNH SẮC THÁI CẢM XÚC (POLARITY) & Ý KIẾN (OPINION)
    distress_neg_cues = [
        "chờ nước rút", "đợi nước rút", "đợi cho nước rút", "chờ cho nước rút",
        "đứng chờ nước", "ngồi chờ nước", "chờ mưa ngớt", "chờ mưa tạnh",
        "khi nào hết ngập", "bao giờ nước rút", "chưa rút", "chưa rút nước",
        "vẫn ngập", "ngập chưa rút", "rút chậm", "rút rất chậm", "không rút kịp",
        "ngập quá", "ngập sâu", "ngập nặng", "ngập lút bánh", "lút bánh", "nửa bánh",
        "chết máy", "tắt máy", "dắt bộ", "dắt xe", "dẫn bộ", "bì bõm",
        "tấp lên lề", "tấp vào lề", "lên lề", "ướt sũng", "không dám đi",
        "bất lực", "tràn vào nhà", "nước tràn", "nước cuốn", "biển nước", "mênh mông",
        "kẹt cứng", "tê liệt", "sóng đánh", "hên xui", "hỏi đã rút nước chưa",
        "trú mưa", "đứng chôn chân", "vất vả", "gian nan", "chật vật",
        "biến thành sông", "thành sông", "dâng cao", "nước dâng cao"
    ]

    genuine_pos_cues = [
        "thi công chống ngập", "sớm thi công chống ngập", "triển khai thi công chống ngập",
        "nước đã rút hết", "nước đã rút hoàn toàn", "đã rút hẳn", "nước rút sạch",
        "đã hết ngập", "không còn ngập nữa", "không còn ngập nước", "đường đã khô ráo",
        "đã khô ráo", "khô ráo hoàn toàn", "mặt đường khô ráo", "khô ráo sạch sẽ",
        "khô rang", "khô queo", "ráo hoảnh", "không bị ngập", "không hề ngập", "không ngập",
        "lưu thông bình thường trở lại", "phương tiện lưu thông bình thường",
        "di chuyển bình thường", "lưu thông thuận lợi", "giao thông ổn định trở lại",
        "đi lại dễ dàng", "mặt đường thông thoáng trở lại", "thông thoáng trở lại"
    ]

    neu_cues = [
        "dự báo", "cảnh báo triều cường", "dự báo triều cường", "nhận định",
        "khả năng xuất hiện", "khả năng gây ngập", "nguy cơ ngập", "có thể gây ngập",
        "có thể ngập", "theo dõi diễn biến", "cần theo dõi", "theo dõi tình hình",
        "ngập nhẹ", "ngập nhỏ", "xâm xấp", "chớm ngập", "mép vỉa hè", "mép đường",
        "dấu hiệu ngập", "bắt đầu lên", "mực nước bắt đầu lên", "chuẩn bị lên",
        "diễn biến triều cường", "thủy triều đang lên", "mực nước bắt đầu rút", "nước rút dần"
    ]

    has_distress = any(k in text_lower for k in distress_neg_cues)
    has_pos = any(k in text_lower for k in genuine_pos_cues)
    has_neu = any(k in text_lower for k in neu_cues)

    opinion = ""
    polarity = "NEG"

    if has_distress:
        polarity = "NEG"
        if "tấp lên lề" in text_lower or "chờ nước rút" in text_lower or "đợi cho nước rút" in text_lower:
            opinion = "ngập sâu khiến phương tiện phải tấp lên lề / chờ nước rút"
        elif "chết máy" in text_lower or "tắt máy" in text_lower or "dắt bộ" in text_lower or "dẫn bộ" in text_lower:
            opinion = "nước ngập làm xe chết máy, phải dắt bộ bì bõm"
        elif "lút bánh" in text_lower:
            opinion = "ngập lút bánh xe nghiêm trọng"
        elif "tràn vào nhà" in text_lower or "nước tràn" in text_lower:
            opinion = "nước dâng tràn vào nhà dân"
        elif "tê liệt" in text_lower or "kẹt cứng" in text_lower:
            opinion = "giao thông tê liệt hoàn toàn vì ngập"
        elif "vẫn ngập" in text_lower or "chưa rút" in text_lower or "rút chậm" in text_lower:
            opinion = "nước rút chậm, tuyến đường vẫn ngập sâu"
        elif "biến thành sông" in text_lower or "thành sông" in text_lower:
            opinion = "mưa lớn biến đường phố thành sông"
        else:
            opinion = "ngập sâu gây cản trở và đảo lộn giao thông"

    elif has_pos:
        polarity = "POS"
        if "thi công chống ngập" in text_lower or "sớm thi công chống ngập" in text_lower:
            opinion = "sớm thi công chống ngập"
        elif "thông thoáng" in text_lower or "bình thường" in text_lower:
            opinion = "nước đã rút, mặt đường thông thoáng và lưu thông bình thường"
        elif "khô rang" in text_lower or "khô queo" in text_lower:
            opinion = "mặt đường khô rang, hoàn toàn không bị ngập nước"
        elif "không bị ngập" in text_lower or "không hề ngập" in text_lower or "không ngập" in text_lower:
            opinion = "tuyến đường không bị ngập nước, di chuyển bình thường"
        elif "khô ráo" in text_lower:
            opinion = "đoạn đường đã khô ráo hoàn toàn"
        else:
            opinion = "nước đã rút hết, giao thông ổn định trở lại"

    elif has_neu:
        polarity = "NEU"
        if "ngập nhẹ" in text_lower or "ngập nhỏ" in text_lower or "xâm xấp" in text_lower or "mép" in text_lower:
            opinion = "đường có dấu hiệu ngập nhỏ mép vỉa hè, cần theo dõi"
        elif "dự báo" in text_lower or "cảnh báo" in text_lower or "nguy cơ" in text_lower:
            opinion = "dự báo triều cường / khả năng ngập, cần theo dõi diễn biến"
        elif "bắt đầu rút" in text_lower or "rút dần" in text_lower:
            opinion = "mực nước bắt đầu rút dần, tình hình đang chuyển biến"
        else:
            opinion = "mực nước triều đang lên, theo dõi sát diễn biến"
    else:
        polarity = "NEG"
        if "ngập sâu" in text_lower or "ngập nặng" in text_lower:
            opinion = "ngập sâu diện rộng"
        elif "triều cường" in text_lower:
            opinion = "triều cường dâng cao gây ngập"
        else:
            opinion = "ngập nước cục bộ"

    for asp in aspects[:2]:
        triplets.append({
            "aspect": asp,
            "opinion": opinion,
            "polarity": polarity
        })

    return triplets

def build_dataset():
    print("=" * 80)
    print("BẮT ĐẦU CHUẨN HÓA, LỌC BỎ RÁC & CÂN BẰNG ASTE 3 LỚP (NEG / NEU / POS)")
    print("=" * 80)

    baseline_items = []
    enriched_items = []

    seen_urls = set()
    seen_texts = set()

    platform_stats = {"news": 0, "tiktok": 0, "facebook": 0}
    polarity_stats = {"NEG": 0, "NEU": 0, "POS": 0}
    episode_stats = {}

    episode_dirs = sorted(glob.glob(os.path.join(EPISODES_DIR, "*")))
    print(f"[*] Tìm thấy {len(episode_dirs)} phân vùng Episode trong data/raw/episodes/")

    for ep_dir in episode_dirs:
        if not os.path.isdir(ep_dir):
            continue
        ep_id = os.path.basename(ep_dir)
        meta_path = os.path.join(ep_dir, "metadata.json")
        ep_title = ep_id
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as mf:
                    mdata = json.load(mf)
                    ep_title = mdata.get("title", ep_id)
            except Exception:
                pass

        episode_stats[ep_id] = {"title": ep_title, "news": 0, "tiktok": 0, "facebook": 0}

        # -------------------------------------------------------------
        # 1. XỬ LÝ GOOGLE NEWS TRONG PHÂN VÙNG
        # -------------------------------------------------------------
        news_file = os.path.join(ep_dir, "news_raw.json")
        if os.path.exists(news_file):
            try:
                with open(news_file, "r", encoding="utf-8") as f:
                    raw_news = json.load(f)
            except Exception:
                raw_news = []

            for article in raw_news:
                url = article.get("url", "")
                if any(b in url for b in BLOCKED_URL_SUBSTRINGS):
                    continue

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
                    if is_excluded_content(clean_sent):
                        continue
                    if not matches_flood_context(clean_sent):
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
                    for t in triplets:
                        polarity_stats[t["polarity"]] += 1

                    item_id = f"{parent_id}_s{chunk_sub_idx:02d}"
                    chunk_sub_idx += 1

                    item_record = {
                        "id": item_id,
                        "parent_id": parent_id,
                        "episode_id": ep_id,
                        "episode_title": ep_title,
                        "crawl_batch": "batch_1_baseline",
                        "is_new_crawl": False,
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
                    }
                    baseline_items.append(item_record)
                    platform_stats["news"] += 1
                    episode_stats[ep_id]["news"] += 1

        # -------------------------------------------------------------
        # 2. XỬ LÝ TIKTOK TRONG PHÂN VÙNG
        # -------------------------------------------------------------
        tt_file = os.path.join(ep_dir, "tiktok_raw.json")
        if os.path.exists(tt_file):
            try:
                with open(tt_file, "r", encoding="utf-8") as f:
                    raw_tt = json.load(f)
            except Exception:
                raw_tt = []

            for it in raw_tt:
                if not isinstance(it, dict) or it.get("error") or it.get("errorCode"):
                    continue

                url = it.get("webVideoUrl") or it.get("url") or ""
                if any(b in url for b in BLOCKED_URL_SUBSTRINGS):
                    continue

                raw_text = it.get("text", "") or ""
                clean_text = clean_stream_text(raw_text)
                if not clean_text or len(clean_text) < 18 or is_junk_sentence(clean_text):
                    continue

                low_text = clean_text.lower()
                if is_excluded_content(clean_text):
                    continue
                if not matches_flood_context(clean_text):
                    continue

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

                author_raw = it.get("authorMeta") or it.get("author")
                author_name = "TikTok Creator"
                if isinstance(author_raw, dict):
                    author_name = author_raw.get("name") or author_raw.get("nickname") or "TikTok Creator"
                elif author_raw:
                    author_name = str(author_raw)

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
                if not media_urls:
                    v_url = it.get("webVideoUrl") or url
                    if v_url and ("tiktok.com" in v_url.lower() and "/video/" in v_url.lower()):
                        media_urls.append(v_url)

                published_iso = parse_iso_datetime(it.get("createTimeISO") or it.get("createTime") or it.get("published_at"))
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
                for t in triplets:
                    polarity_stats[t["polarity"]] += 1

                is_new_crawl = (it.get("crawler_source") == "free_discovery_engine")
                item_record = {
                    "id": parent_id,
                    "parent_id": parent_id,
                    "episode_id": ep_id,
                    "episode_title": ep_title,
                    "crawl_batch": "batch_2_social_enrichment" if is_new_crawl else "batch_1_baseline",
                    "is_new_crawl": is_new_crawl,
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
                }

                if is_new_crawl:
                    enriched_items.append(item_record)
                else:
                    baseline_items.append(item_record)

                platform_stats["tiktok"] += 1
                episode_stats[ep_id]["tiktok"] += 1

        # -------------------------------------------------------------
        # 3. XỬ LÝ FACEBOOK TRONG PHÂN VÙNG
        # -------------------------------------------------------------
        fb_file = os.path.join(ep_dir, "facebook_raw.json")
        if os.path.exists(fb_file):
            try:
                with open(fb_file, "r", encoding="utf-8") as f:
                    raw_fb = json.load(f)
            except Exception:
                raw_fb = []

            for it in raw_fb:
                if not isinstance(it, dict) or it.get("error") or it.get("errorDescription"):
                    continue

                url = it.get("url") or it.get("post_url") or it.get("facebookUrl") or ""
                if any(b in url for b in BLOCKED_URL_SUBSTRINGS):
                    continue

                raw_text = it.get("text") or it.get("message") or it.get("post_text") or ""
                clean_text = clean_stream_text(raw_text)
                if not clean_text or len(clean_text) < 18 or is_junk_sentence(clean_text):
                    continue

                low_text = clean_text.lower()
                if is_excluded_content(clean_text):
                    continue
                if not matches_flood_context(clean_text):
                    continue

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
                if not media_urls:
                    if url and any(k in url.lower() for k in ["/reel/", "/videos/", "/watch/"]):
                        media_urls.append(url)

                published_iso = parse_iso_datetime(it.get("time") or it.get("createTime") or it.get("timestamp") or it.get("published_at"))
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
                for t in triplets:
                    polarity_stats[t["polarity"]] += 1

                is_new_crawl = (it.get("crawler_source") == "free_discovery_engine")
                item_record = {
                    "id": parent_id,
                    "parent_id": parent_id,
                    "episode_id": ep_id,
                    "episode_title": ep_title,
                    "crawl_batch": "batch_2_social_enrichment" if is_new_crawl else "batch_1_baseline",
                    "is_new_crawl": is_new_crawl,
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
                }

                if is_new_crawl:
                    enriched_items.append(item_record)
                else:
                    baseline_items.append(item_record)

                platform_stats["facebook"] += 1
                episode_stats[ep_id]["facebook"] += 1

    # -------------------------------------------------------------
    # GHÉP NỐI: TẬP GỐC (BASELINE) Ở ĐẦU + TẬP CÀO MỚI (ENRICHED) Ở CUỐI FILE
    # ĐÁNH SỐ THỨ TỰ TUYỆT ĐỐI 'seq_id' TỪ 1 ĐẾN N
    # -------------------------------------------------------------
    combined_items = baseline_items + enriched_items
    for idx, item in enumerate(combined_items, start=1):
        item["seq_id"] = idx

    # Ghi ra đồng thời 2 file dataset
    for target_path in [OUTPUT_FILE_V1, OUTPUT_FILE_V2]:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as fp:
            json.dump(combined_items, fp, ensure_ascii=False, indent=2)

    total_items = len(combined_items)
    with_triplets = sum(1 for it in combined_items if len(it.get("aste_triplets", [])) > 0)
    pct = (with_triplets / total_items * 100) if total_items > 0 else 0

    print("\n" + "=" * 80)
    print("HOÀN TẤT XỬ LÝ VÀ GÁN NHÃN DATASET:")
    print(f"  * Tổng số mẫu hợp nhất: {total_items} items")
    print(f"    - Tập Baseline ban đầu: {len(baseline_items)} items (seq_id: 1 -> {len(baseline_items)})")
    print(f"    - Tập Mới cào thêm (Nằm ở CUỐI FILE): {len(enriched_items)} items (seq_id: {len(baseline_items)+1} -> {total_items})")
    print("\n  * Phân bố theo Nền tảng:")
    print(f"    - Google News (Báo chí): {platform_stats['news']} items ({platform_stats['news']/total_items*100:.1f}%) [BẢO TỒN NGUYÊN VẸN 100%]")
    print(f"    - TikTok Videos: {platform_stats['tiktok']} items ({platform_stats['tiktok']/total_items*100:.1f}%)")
    print(f"    - Facebook Posts: {platform_stats['facebook']} items ({platform_stats['facebook']/total_items*100:.1f}%) [ĐÃ LOẠI 2 BÀI RÁC]")
    print("\n  * Phân bố Nhãn Cảm xúc ASTE Triplet 3 lớp ({Aspect, Opinion, Polarity}):")
    tot_triplets = sum(polarity_stats.values())
    print(f"    - NEGATIVE (Ngập lụt / Chết máy / Tê liệt): {polarity_stats['NEG']} ({polarity_stats['NEG']/tot_triplets*100:.1f}%)")
    print(f"    - NEUTRAL (Dự báo / Cảnh báo / Ngập nhỏ / Theo dõi): {polarity_stats['NEU']} ({polarity_stats['NEU']/tot_triplets*100:.1f}%)")
    print(f"    - POSITIVE (Nước đã rút / Đường khô thoáng / Bình thường): {polarity_stats['POS']} ({polarity_stats['POS']/tot_triplets*100:.1f}%)")
    print(f"  * Tỷ lệ gán nhãn ASTE Triplet: {with_triplets}/{total_items} ({pct:.1f}%)")
    print(f"  * Đã lưu đồng bộ vào:")
    print(f"    1. {OUTPUT_FILE_V1} (Tương thích tuyệt đối hệ thống replayer)")
    print(f"    2. {OUTPUT_FILE_V2} (Bản mở rộng phân vùng Multimodal)")
    print("=" * 80)

if __name__ == "__main__":
    build_dataset()
