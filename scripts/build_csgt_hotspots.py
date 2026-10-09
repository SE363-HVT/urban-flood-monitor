# -*- coding: utf-8 -*-
"""
scripts/build_csgt_hotspots.py
Chuẩn hóa 122 điểm ngập nước do Phòng CSGT Công an TP.HCM (PC08) cảnh báo:
- 83 điểm ngập do Mưa lớn, nước không thoát kịp
- 39 điểm ngập do Triều cường
Đã chuẩn hóa toàn bộ Đơn vị hành chính Phường / Xã và Quận / Huyện / Thành phố
theo mô hình MỚI NHẤT SAU SÁP NHẬP tại TP.HCM (Nghị quyết của UBTVQH).
"""

import os
import sys
import json
import unicodedata
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.admin_resolver import RESOLVER

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def remove_accents(input_str: str) -> str:
    if not input_str:
        return ""
    nfkd = unicodedata.normalize('NFKD', input_str)
    res = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return res.replace('đ', 'd').replace('Đ', 'D').lower()

def make_keywords(street: str, extra: list = None) -> list:
    kws = set()
    s_lower = street.lower().strip()
    s_clean = re.sub(r'^(đường|tỉnh lộ|quốc lộ|hẻm|đoạn|ngã tư|vòng xoay|chợ|hầm chui)\s+', '', s_lower).strip()
    
    kws.add(s_lower)
    kws.add(remove_accents(s_lower))
    if s_clean and s_clean != s_lower:
        kws.add(s_clean)
        kws.add(remove_accents(s_clean))
        
    if extra:
        for ex in extra:
            ex_lower = ex.lower().strip()
            kws.add(ex_lower)
            kws.add(remove_accents(ex_lower))
            
    return sorted(list(kws))

# =============================================================================
# DANH SÁCH CHI TIẾT 122 ĐIỂM NGẬP PC08 - CHUẨN HÓA PHƯỜNG/XÃ MỚI SAU SÁP NHẬP
# =============================================================================
RAW_CSGT_DATA = [
    # =========================================================================
    # I. 83 ĐIỂM NGẬP DO MƯA LỚN, NƯỚC KHÔNG THOÁT KỊP
    # =========================================================================
    {
        "id": "csgt_rain_01",
        "cause": "rain",
        "street": "Lý Thường Kiệt",
        "segment": "Từ số 387 đến cổng trường Nguyễn Thái Bình",
        "ward": "Phường 8", "district": "Quận Tân Bình",
        "lat": 10.7852, "lon": 106.6575,
        "extra_kw": ["lý thường kiệt 387", "trường nguyễn thái bình"]
    },
    {
        "id": "csgt_rain_02",
        "cause": "rain",
        "street": "Ngã tư Bảy Hiền",
        "segment": "Khu vực giao lộ Cách Mạng Tháng 8 - Trường Chinh - Lý Thường Kiệt",
        "ward": "Phường 11", "district": "Quận Tân Bình",
        "lat": 10.7915, "lon": 106.6534,
        "extra_kw": ["ngã tư bảy hiền", "bảy hiền"]
    },
    {
        "id": "csgt_rain_03",
        "cause": "rain",
        "street": "Lê Đức Anh - Hồ Học Lãm",
        "segment": "Giao lộ Lê Đức Anh và Hồ Học Lãm",
        "ward": "Phường An Lạc", "district": "Quận Bình Tân",
        "lat": 10.7325, "lon": 106.6135,
        "extra_kw": ["lê đức anh hồ học lãm", "lê đức anh", "hồ học lãm"]
    },
    {
        "id": "csgt_rain_04",
        "cause": "rain",
        "street": "Tỉnh lộ 10",
        "segment": "Từ Tên Lửa nhỏ ra Lê Đức Anh",
        "ward": "Phường An Lạc A", "district": "Quận Bình Tân",
        "lat": 10.7570, "lon": 106.6080,
        "extra_kw": ["tỉnh lộ 10", "tl10 tên lửa"]
    },
    {
        "id": "csgt_rain_05",
        "cause": "rain",
        "street": "Trần Đại Nghĩa",
        "segment": "Nhánh từ số 4 đến giáp Lê Khả Phiêu",
        "ward": "Xã Tân Nhựt", "district": "Huyện Bình Chánh",
        "lat": 10.7350, "lon": 106.5750,
        "extra_kw": ["trần đại nghĩa", "trần đại nghĩa số 4", "xã tân nhựt"]
    },
    {
        "id": "csgt_rain_06",
        "cause": "rain",
        "street": "Trần Văn Giàu",
        "segment": "Từ số 55 đến giao lộ Vườn Thơm",
        "ward": "Xã Bình Lợi", "district": "Huyện Bình Chánh",
        "lat": 10.7680, "lon": 106.5450,
        "extra_kw": ["trần văn giàu", "trần văn giàu vườn thơm", "xã bình lợi"]
    },
    {
        "id": "csgt_rain_07",
        "cause": "rain",
        "street": "Vĩnh Lộc",
        "segment": "Từ Trần Văn Giàu đến Lại Hùng Cường (ngập nặng từ Trần Văn Giàu đến cầu Bà Tri)",
        "ward": "Xã Tân Vĩnh Lộc", "district": "Huyện Bình Chánh",
        "lat": 10.7850, "lon": 106.5650,
        "extra_kw": ["vĩnh lộc", "cầu bà tri", "lại hùng cường", "vĩnh lộc b", "tân vĩnh lộc"]
    },
    {
        "id": "csgt_rain_08",
        "cause": "rain",
        "street": "Võ Văn Vân",
        "segment": "Từ số 700 đến 730 (khu vực giao lộ đường Trục Tổ 7)",
        "ward": "Xã Tân Vĩnh Lộc", "district": "Huyện Bình Chánh",
        "lat": 10.7820, "lon": 106.5780,
        "extra_kw": ["võ văn vân", "võ văn vân 700", "vĩnh lộc b", "tân vĩnh lộc"]
    },
    {
        "id": "csgt_rain_09",
        "cause": "rain",
        "street": "Lê Quang Đạo",
        "segment": "Từ giao lộ Võ Thị Hồi đến giao lộ Nguyễn Thị Sóc",
        "ward": "Xã Bà Điểm", "district": "Huyện Hóc Môn",
        "lat": 10.8490, "lon": 106.6020,
        "extra_kw": ["lê quang đạo", "võ thị hồi", "nguyễn thị sóc", "bà điểm"]
    },
    {
        "id": "csgt_rain_10",
        "cause": "rain",
        "street": "Lê Quang Đạo - Trần Văn Mười",
        "segment": "Giao lộ Lê Quang Đạo - Trần Văn Mười",
        "ward": "Xã Bà Điểm", "district": "Huyện Hóc Môn",
        "lat": 10.8520, "lon": 106.5980,
        "extra_kw": ["lê quang đạo trần văn mười", "xuân thới thượng", "bà điểm"]
    },
    {
        "id": "csgt_rain_11",
        "cause": "rain",
        "street": "Trần Văn Mười",
        "segment": "Từ Lê Quang Đạo đến Xuân Thới 2",
        "ward": "Xã Xuân Thới Sơn", "district": "Huyện Hóc Môn",
        "lat": 10.8560, "lon": 106.5920,
        "extra_kw": ["trần văn mười", "xuân thới 2", "xuân thới đông", "xuân thới sơn"]
    },
    {
        "id": "csgt_rain_12",
        "cause": "rain",
        "street": "Nguyễn Thị Thử",
        "segment": "Từ Võ Thị Hồi đến Xuân Thới Sơn 5",
        "ward": "Xã Xuân Thới Sơn", "district": "Huyện Hóc Môn",
        "lat": 10.8650, "lon": 106.5820,
        "extra_kw": ["nguyễn thị thử", "xuân thới sơn 5", "xuân thới sơn"]
    },
    {
        "id": "csgt_rain_13",
        "cause": "rain",
        "street": "Song hành Quốc lộ 22",
        "segment": "Từ Đỗ Mười đến Bà Triệu",
        "ward": "Xã Hóc Môn", "district": "Huyện Hóc Môn",
        "lat": 10.8780, "lon": 106.5980,
        "extra_kw": ["song hành ql22", "song hành quốc lộ 22", "thị trấn hóc môn", "xã hóc môn"]
    },
    {
        "id": "csgt_rain_14",
        "cause": "rain",
        "street": "Nguyễn Ảnh Thủ",
        "segment": "Từ Lê Quang Đạo đến Đồng Tâm",
        "ward": "Xã Bà Điểm", "district": "Huyện Hóc Môn",
        "lat": 10.8620, "lon": 106.6080,
        "extra_kw": ["nguyễn ảnh thủ", "đồng tâm", "trung chánh", "bà điểm"]
    },
    {
        "id": "csgt_rain_15",
        "cause": "rain",
        "street": "Bà Triệu",
        "segment": "Từ giao lộ Quang Trung đến giao lộ Song hành",
        "ward": "Xã Hóc Môn", "district": "Huyện Hóc Môn",
        "lat": 10.8848, "lon": 106.5951,
        "extra_kw": ["bà triệu hóc môn", "bà triệu song hành", "thị trấn hóc môn", "xã hóc môn"]
    },
    {
        "id": "csgt_rain_16",
        "cause": "rain",
        "street": "Trưng Nữ Vương",
        "segment": "Từ giao lộ Quang Trung đến giao lộ Đỗ Văn Dậy",
        "ward": "Xã Hóc Môn", "district": "Huyện Hóc Môn",
        "lat": 10.8890, "lon": 106.5920,
        "extra_kw": ["trưng nữ vương", "đỗ văn dậy", "thị trấn hóc môn", "xã hóc môn"]
    },
    {
        "id": "csgt_rain_17",
        "cause": "rain",
        "street": "Đỗ Mười (QL1)",
        "segment": "Trước số 2539/3A (P. An Phú Đông)",
        "ward": "Phường An Phú Đông", "district": "Quận 12",
        "lat": 10.8480, "lon": 106.6980,
        "extra_kw": ["đỗ mười an phú đông", "đỗ mười 2539"]
    },
    {
        "id": "csgt_rain_18",
        "cause": "rain",
        "street": "Đỗ Mười (QL1)",
        "segment": "Trước số 139 (P. Tam Bình)",
        "ward": "Phường Tam Bình", "district": "TP. Thủ Đức",
        "lat": 10.8630, "lon": 106.7250,
        "extra_kw": ["đỗ mười tam bình", "đỗ mười 139"]
    },
    {
        "id": "csgt_rain_19",
        "cause": "rain",
        "street": "Cầu Bình Phước",
        "segment": "Hai bên cầu Bình Phước, trước số 2 (P. Hiệp Bình Phước)",
        "ward": "Phường Hiệp Bình Phước", "district": "TP. Thủ Đức",
        "lat": 10.8520, "lon": 106.7110,
        "extra_kw": ["cầu bình phước", "hai bên cầu bình phước", "hiệp bình phước"]
    },
    {
        "id": "csgt_rain_20",
        "cause": "rain",
        "street": "Chợ đầu mối nông sản Thủ Đức",
        "segment": "Trước chợ đầu mối nông sản Thủ Đức, đoạn số 113",
        "ward": "Phường Tam Bình", "district": "TP. Thủ Đức",
        "lat": 10.8640, "lon": 106.7280,
        "extra_kw": ["chợ đầu mối thủ đức", "chợ đầu mối nông sản thủ đức", "tam bình"]
    },
    {
        "id": "csgt_rain_21",
        "cause": "rain",
        "street": "Đỗ Mười - đường 17",
        "segment": "Giao lộ Đỗ Mười - đường 17",
        "ward": "Phường Tam Bình", "district": "TP. Thủ Đức",
        "lat": 10.8660, "lon": 106.7310,
        "extra_kw": ["đỗ mười đường 17", "tam bình"]
    },
    {
        "id": "csgt_rain_22",
        "cause": "rain",
        "street": "Hầm chui cầu Bến Cát",
        "segment": "Hầm chui cầu Bến Cát (P. Thới An)",
        "ward": "Phường Thới An", "district": "Quận 12",
        "lat": 10.8610, "lon": 106.6620,
        "extra_kw": ["hầm chui bến cát", "hầm chui cầu bến cát", "thới an"]
    },
    {
        "id": "csgt_rain_23",
        "cause": "rain",
        "street": "Vòng xoay Bình Phước",
        "segment": "Vòng xoay ngã tư Bình Phước",
        "ward": "Phường Hiệp Bình Phước", "district": "TP. Thủ Đức",
        "lat": 10.8530, "lon": 106.7120,
        "extra_kw": ["vòng xoay bình phước", "ngã tư bình phước", "hiệp bình phước"]
    },
    {
        "id": "csgt_rain_24",
        "cause": "rain",
        "street": "Ngã tư Bình Phước",
        "segment": "Hai bên ngã tư Bình Phước (dưới gầm cầu vượt)",
        "ward": "Phường Hiệp Bình Phước", "district": "TP. Thủ Đức",
        "lat": 10.8535, "lon": 106.7125,
        "extra_kw": ["dưới cầu vượt bình phước", "ngã tư bình phước", "hiệp bình phước"]
    },
    {
        "id": "csgt_rain_25",
        "cause": "rain",
        "street": "Võ Nguyên Giáp",
        "segment": "Đoạn từ Cầu Trắng đến điểm quay đầu (làn hỗn hợp)",
        "ward": "Phường An Khánh", "district": "TP. Thủ Đức",
        "lat": 10.8030, "lon": 106.7380,
        "extra_kw": ["võ nguyên giáp", "cầu trắng", "xa lộ hà nội", "an khánh"]
    },
    {
        "id": "csgt_rain_26",
        "cause": "rain",
        "street": "Võ Nguyên Giáp",
        "segment": "Đoạn từ điểm quay đầu về cầu Rạch Chiếc",
        "ward": "Phường An Phú", "district": "TP. Thủ Đức",
        "lat": 10.8120, "lon": 106.7510,
        "extra_kw": ["võ nguyên giáp cầu rạch chiếc", "an phú"]
    },
    {
        "id": "csgt_rain_27",
        "cause": "rain",
        "street": "Võ Trường Toản - Song hành Võ Nguyên Giáp",
        "segment": "Giao Võ Trường Toản với song hành Võ Nguyên Giáp",
        "ward": "Phường An Phú", "district": "TP. Thủ Đức",
        "lat": 10.8055, "lon": 106.7410,
        "extra_kw": ["võ trường toản", "song hành võ nguyên giáp", "an phú"]
    },
    {
        "id": "csgt_rain_28",
        "cause": "rain",
        "street": "Chân cầu Rạch Chiếc (Metro Rạch Chiếc)",
        "segment": "Chân cầu Rạch Chiếc, hướng ra ga Metro Rạch Chiếc (P. An Khánh)",
        "ward": "Phường An Khánh", "district": "TP. Thủ Đức",
        "lat": 10.8150, "lon": 106.7550,
        "extra_kw": ["ga metro rạch chiếc", "chân cầu rạch chiếc", "an khánh"]
    },
    {
        "id": "csgt_rain_29",
        "cause": "rain",
        "street": "Mai Chí Thọ - Tố Hữu",
        "segment": "Giao lộ Tố Hữu - Mai Chí Thọ",
        "ward": "Phường Thủ Thiêm", "district": "TP. Thủ Đức",
        "lat": 10.7780, "lon": 106.7210,
        "extra_kw": ["mai chí thọ tố hữu", "tố hữu mai chí thọ", "thủ thiêm"]
    },
    {
        "id": "csgt_rain_30",
        "cause": "rain",
        "street": "Mai Chí Thọ - Lương Định Của",
        "segment": "Giao lộ Mai Chí Thọ - Lương Định Của",
        "ward": "Phường An Phú", "district": "TP. Thủ Đức",
        "lat": 10.7920, "lon": 106.7420,
        "extra_kw": ["mai chí thọ lương định của", "lương định của", "an phú"]
    },
    {
        "id": "csgt_rain_31",
        "cause": "rain",
        "street": "Mai Chí Thọ (Cầu vượt A)",
        "segment": "Hướng từ Cầu vượt A đến giao lộ Lương Định Của",
        "ward": "Phường An Phú", "district": "TP. Thủ Đức",
        "lat": 10.7940, "lon": 106.7440,
        "extra_kw": ["cầu vượt a", "cầu vượt mai chí thọ", "an phú"]
    },
    {
        "id": "csgt_rain_32",
        "cause": "rain",
        "street": "Tô Ngọc Vân - Phạm Văn Đồng",
        "segment": "Giao lộ Tô Ngọc Vân - Phạm Văn Đồng",
        "ward": "Phường Linh Tây", "district": "TP. Thủ Đức",
        "lat": 10.8580, "lon": 106.7520,
        "extra_kw": ["tô ngọc vân phạm văn đồng", "tô ngọc vân", "linh tây"]
    },
    {
        "id": "csgt_rain_33",
        "cause": "rain",
        "street": "Tô Ngọc Vân - Linh Đông",
        "segment": "Giao lộ Tô Ngọc Vân - Linh Đông",
        "ward": "Phường Linh Đông", "district": "TP. Thủ Đức",
        "lat": 10.8525, "lon": 106.7560,
        "extra_kw": ["tô ngọc vân linh đông", "linh đông"]
    },
    {
        "id": "csgt_rain_34",
        "cause": "rain",
        "street": "Tô Ngọc Vân - Đường 35",
        "segment": "Giao lộ Tô Ngọc Vân - đường 35 (Linh Tây)",
        "ward": "Phường Linh Tây", "district": "TP. Thủ Đức",
        "lat": 10.8550, "lon": 106.7540,
        "extra_kw": ["tô ngọc vân đường 35", "linh tây"]
    },
    {
        "id": "csgt_rain_35",
        "cause": "rain",
        "street": "Phạm Văn Đồng - Linh Đông",
        "segment": "Đường Phạm Văn Đồng giao Linh Đông",
        "ward": "Phường Linh Đông", "district": "TP. Thủ Đức",
        "lat": 10.8490, "lon": 106.7480,
        "extra_kw": ["phạm văn đồng linh đông", "linh đông"]
    },
    {
        "id": "csgt_rain_36",
        "cause": "rain",
        "street": "Trịnh Thị Dối",
        "segment": "Số 69 Trịnh Thị Dối (xã Đông Thạnh)",
        "ward": "Xã Đông Thạnh", "district": "Huyện Hóc Môn",
        "lat": 10.8920, "lon": 106.6380,
        "extra_kw": ["trịnh thị dối", "69 trịnh thị dối", "đông thạnh"]
    },
    {
        "id": "csgt_rain_37",
        "cause": "rain",
        "street": "Võ Chí Công - Đường số 5",
        "segment": "Đường Võ Chí Công giao đường số 5",
        "ward": "Phường Phước Long", "district": "TP. Thủ Đức",
        "lat": 10.8010, "lon": 106.7820,
        "extra_kw": ["võ chí công đường số 5", "võ chí công", "phước long", "phước long b"]
    },
    {
        "id": "csgt_rain_38",
        "cause": "rain",
        "street": "Thảo Điền - Quốc Hương",
        "segment": "Giao lộ Thảo Điền - Quốc Hương",
        "ward": "Phường Thảo Điền", "district": "TP. Thủ Đức",
        "lat": 10.8040, "lon": 106.7320,
        "extra_kw": ["thảo điền quốc hương", "thảo điền", "quốc hương"]
    },
    {
        "id": "csgt_rain_39",
        "cause": "rain",
        "street": "Đỗ Xuân Hợp - Tây Hòa",
        "segment": "Giao lộ Đỗ Xuân Hợp - Tây Hòa",
        "ward": "Phường Phước Long", "district": "TP. Thủ Đức",
        "lat": 10.8220, "lon": 106.7680,
        "extra_kw": ["đỗ xuân hợp tây hòa", "đỗ xuân hợp", "phước long", "phước long a"]
    },
    {
        "id": "csgt_rain_40",
        "cause": "rain",
        "street": "Đường số 2 (Trường Thọ)",
        "segment": "Đường số 2 (Phường Trường Thọ, TP. Thủ Đức)",
        "ward": "Phường Trường Thọ", "district": "TP. Thủ Đức",
        "lat": 10.8380, "lon": 106.7580,
        "extra_kw": ["đường số 2 thủ đức", "đường số 2 trường thọ", "trường thọ"]
    },
    {
        "id": "csgt_rain_41",
        "cause": "rain",
        "street": "Tạ Quang Bửu",
        "segment": "Từ Võ Liêm Sơn đến Cao Lỗ",
        "ward": "Phường Chánh Hưng", "district": "Quận 8",
        "lat": 10.7380, "lon": 106.6780,
        "extra_kw": ["tạ quang bửu cao lỗ", "võ liêm sơn", "chánh hưng", "phường 4 quận 8"]
    },
    {
        "id": "csgt_rain_42",
        "cause": "rain",
        "street": "Chợ Thủ Đức",
        "segment": "Khu vực Chợ Thủ Đức (Dương Văn Cam - Đặng Thị Rành)",
        "ward": "Phường Linh Tây", "district": "TP. Thủ Đức",
        "lat": 10.8503, "lon": 106.7541,
        "extra_kw": ["chợ thủ đức", "dương văn cam", "đặng thị rành", "linh tây"]
    },
    {
        "id": "csgt_rain_43",
        "cause": "rain",
        "street": "Lý Tế Xuyên",
        "segment": "Đường Lý Tế Xuyên",
        "ward": "Phường Linh Đông", "district": "TP. Thủ Đức",
        "lat": 10.8460, "lon": 106.7520,
        "extra_kw": ["lý tế xuyên", "linh đông"]
    },
    {
        "id": "csgt_rain_44",
        "cause": "rain",
        "street": "Cổng KCN Sóng Thần",
        "segment": "Cổng KCN Sóng Thần (giáp ranh Thủ Đức)",
        "ward": "Phường Bình Chiểu", "district": "TP. Thủ Đức",
        "lat": 10.8850, "lon": 106.7450,
        "extra_kw": ["kcn sóng thần", "cổng kcn sóng thần", "bình chiểu"]
    },
    {
        "id": "csgt_rain_45",
        "cause": "rain",
        "street": "ĐT743A - Mỹ Phước Tân Vạn",
        "segment": "Đường ĐT743A giao Mỹ Phước Tân Vạn (giáp cửa ngõ Thủ Đức)",
        "ward": "Phường Bình Thắng", "district": "TP. Dĩ An (Cửa ngõ TP. Thủ Đức)",
        "lat": 10.8920, "lon": 106.7850,
        "extra_kw": ["đt743a", "mỹ phước tân vạn", "bình thắng"]
    },
    {
        "id": "csgt_rain_46",
        "cause": "rain",
        "street": "Lê Văn Việt",
        "segment": "Từ giao lộ Đình Phong Phú đến giao lộ Lã Xuân Oai",
        "ward": "Phường Tăng Nhơn Phú A", "district": "TP. Thủ Đức",
        "lat": 10.8465, "lon": 106.7860,
        "extra_kw": ["lê văn việt đình phong phú", "lã xuân oai", "tăng nhơn phú a"]
    },
    {
        "id": "csgt_rain_47",
        "cause": "rain",
        "street": "Nguyễn Xiển",
        "segment": "Từ số 581 (Vinhomes Grand Park) đến cầu Gò Công",
        "ward": "Phường Long Thạnh Mỹ", "district": "TP. Thủ Đức",
        "lat": 10.8410, "lon": 106.8320,
        "extra_kw": ["nguyễn xiển gò công", "vinhomes grand park", "cầu gò công", "long thạnh mỹ"]
    },
    {
        "id": "csgt_rain_48",
        "cause": "rain",
        "street": "Quốc lộ 50",
        "segment": "Từ Nguyễn Văn Linh về cầu Chánh Hưng",
        "ward": "Xã Bình Hưng", "district": "Huyện Bình Chánh",
        "lat": 10.7320, "lon": 106.6650,
        "extra_kw": ["quốc lộ 50 cầu chánh hưng", "ql50 chánh hưng", "bình hưng"]
    },
    {
        "id": "csgt_rain_49",
        "cause": "rain",
        "street": "Văn Tiến Dũng",
        "segment": "Đường Văn Tiến Dũng",
        "ward": "Xã Xuân Thới Sơn", "district": "Huyện Hóc Môn",
        "lat": 10.8750, "lon": 106.5820,
        "extra_kw": ["văn tiến dũng", "tân thới nhì", "xuân thới sơn"]
    },
    {
        "id": "csgt_rain_50",
        "cause": "rain",
        "street": "Nguyễn Văn Tạo",
        "segment": "Từ cầu Kênh Lộ đến cầu Rạch Chim (xã Hiệp Phước)",
        "ward": "Xã Hiệp Phước", "district": "Huyện Nhà Bè",
        "lat": 10.6380, "lon": 106.7210,
        "extra_kw": ["nguyễn văn tạo cầu kênh lộ", "cầu rạch chim", "hiệp phước"]
    },
    {
        "id": "csgt_rain_51",
        "cause": "rain",
        "street": "Nguyễn Bình - Lê Văn Lương",
        "segment": "Giao lộ Nguyễn Bình - Lê Văn Lương (xã Hiệp Phước)",
        "ward": "Xã Hiệp Phước", "district": "Huyện Nhà Bè",
        "lat": 10.6520, "lon": 106.7110,
        "extra_kw": ["nguyễn bình lê văn lương", "hiệp phước"]
    },
    {
        "id": "csgt_rain_52",
        "cause": "rain",
        "street": "Huỳnh Tấn Phát - Phú Thuận",
        "segment": "Giao lộ Huỳnh Tấn Phát - Phú Thuận",
        "ward": "Phường Phú Thuận", "district": "Quận 7",
        "lat": 10.7310, "lon": 106.7380,
        "extra_kw": ["huỳnh tấn phát phú thuận", "phú thuận"]
    },
    {
        "id": "csgt_rain_53",
        "cause": "rain",
        "street": "Nguyễn Văn Linh (Cầu Ông Lớn)",
        "segment": "Đoạn trước công trình cầu Ông Lớn, hướng từ Phạm Hùng đi Nguyễn Hữu Thọ",
        "ward": "Phường Tân Phong", "district": "Quận 7",
        "lat": 10.7320, "lon": 106.6960,
        "extra_kw": ["nguyễn văn linh cầu ông lớn", "cầu ông lớn", "tân phong"]
    },
    {
        "id": "csgt_rain_54",
        "cause": "rain",
        "street": "Nguyễn Văn Linh (Làn SF)",
        "segment": "Làn SF, từ giao lộ Phạm Văn Nghị đến cầu Cả Cấm",
        "ward": "Phường Tân Phong", "district": "Quận 7",
        "lat": 10.7280, "lon": 106.7150,
        "extra_kw": ["nguyễn văn linh phạm văn nghị", "cầu cả cấm", "tân phong"]
    },
    {
        "id": "csgt_rain_55",
        "cause": "rain",
        "street": "Đường D1 - Cầu chui RMIT",
        "segment": "Từ giao lộ D1-D6 đến điểm nối vào Nguyễn Văn Linh (gồm cầu chui RMIT)",
        "ward": "Phường Tân Phong", "district": "Quận 7",
        "lat": 10.7330, "lon": 106.6940,
        "extra_kw": ["cầu chui rmit", "đường d1 rmit", "tân phong"]
    },
    {
        "id": "csgt_rain_56",
        "cause": "rain",
        "street": "Đường D6",
        "segment": "Từ Nguyễn Hữu Thọ đến giao lộ D1–D6",
        "ward": "Phường Tân Phong", "district": "Quận 7",
        "lat": 10.7360, "lon": 106.6970,
        "extra_kw": ["đường d6 tân phong", "tân phong"]
    },
    {
        "id": "csgt_rain_57",
        "cause": "rain",
        "street": "Hoàng Trọng Mậu (Cầu D1 Him Lam)",
        "segment": "Từ giao lộ D6 đến cầu D1 Him Lam",
        "ward": "Phường Tân Hưng", "district": "Quận 7",
        "lat": 10.7450, "lon": 106.6980,
        "extra_kw": ["hoàng trọng mậu", "cầu d1 him lam", "tân hưng"]
    },
    {
        "id": "csgt_rain_58",
        "cause": "rain",
        "street": "Đặng Thùy Trâm",
        "segment": "Đường Đặng Thùy Trâm (Phường 13 / Bình Lợi Trung)",
        "ward": "Phường 13", "district": "Quận Bình Thạnh",
        "lat": 10.8280, "lon": 106.6990,
        "extra_kw": ["đặng thùy trâm", "bình lợi trung", "phường 13 bình thạnh"]
    },
    {
        "id": "csgt_rain_59",
        "cause": "rain",
        "street": "Ung Văn Khiêm",
        "segment": "Từ Nguyễn Gia Trí đến Điện Biên Phủ",
        "ward": "Phường 25", "district": "Quận Bình Thạnh",
        "lat": 10.8035, "lon": 106.7160,
        "extra_kw": ["ung văn khiêm nguyễn gia trí", "ung văn khiêm", "phường 25 bình thạnh"]
    },
    {
        "id": "csgt_rain_60",
        "cause": "rain",
        "street": "Nguyễn Văn Khối",
        "segment": "Từ Lê Văn Thọ đến trước UBND P. Thông Tây Hội",
        "ward": "Phường 8", "district": "Quận Gò Vấp",
        "lat": 10.8460, "lon": 106.6530,
        "extra_kw": ["nguyễn văn khối", "thông tây hội", "nguyễn văn khối lê văn thọ", "phường 8 gò vấp"]
    },
    {
        "id": "csgt_rain_61",
        "cause": "rain",
        "street": "Phạm Thế Hiển (Hẻm 2695 - Lê Bôi)",
        "segment": "Đoạn từ hẻm 2695 đến giao lộ Lê Bôi",
        "ward": "Phường Bình Đông", "district": "Quận 8",
        "lat": 10.7250, "lon": 106.6380,
        "extra_kw": ["phạm thế hiển lê bôi", "hẻm 2695 phạm thế hiển", "phạm thế hiển hẻm 2695", "phạm thế hiển 2695", "lê bôi", "bình đông", "phường 7 quận 8"]
    },
    {
        "id": "csgt_rain_62",
        "cause": "rain",
        "street": "Phạm Thế Hiển (Cầu Bà Tàng)",
        "segment": "Chân cầu Bà Tàng, trước số 2377",
        "ward": "Phường Bình Đông", "district": "Quận 8",
        "lat": 10.7280, "lon": 106.6430,
        "extra_kw": ["cầu bà tàng", "phạm thế hiển cầu bà tàng", "cầu bà tàng phạm thế hiển", "phạm thế hiển 2377", "2377 phạm thế hiển", "bình đông", "phường 7 quận 8"]
    },
    {
        "id": "csgt_rain_63",
        "cause": "rain",
        "street": "Phan Văn Khải",
        "segment": "Số 534 (xã Tân An Hội)",
        "ward": "Xã Tân An Hội", "district": "Huyện Củ Chi",
        "lat": 10.9780, "lon": 106.4820,
        "extra_kw": ["phan văn khải tân an hội", "phan văn khải 534", "tân an hội"]
    },
    {
        "id": "csgt_rain_64",
        "cause": "rain",
        "street": "Phan Văn Khải",
        "segment": "Số 437 (xã Tân An Hội)",
        "ward": "Xã Tân An Hội", "district": "Huyện Củ Chi",
        "lat": 10.9810, "lon": 106.4850,
        "extra_kw": ["phan văn khải 437", "tân an hội"]
    },
    {
        "id": "csgt_rain_65",
        "cause": "rain",
        "street": "Phan Văn Khải",
        "segment": "Số 124 (Thị trấn Củ Chi)",
        "ward": "Thị trấn Củ Chi", "district": "Huyện Củ Chi",
        "lat": 10.9730, "lon": 106.4950,
        "extra_kw": ["phan văn khải 124", "phan văn khải củ chi", "thị trấn củ chi"]
    },
    {
        "id": "csgt_rain_66",
        "cause": "rain",
        "street": "ĐT744",
        "segment": "Hướng từ ngã 3 trường tiểu học An Tây đến chợ An Tây",
        "ward": "Xã An Tây", "district": "TP. Bến Cát (Giáp Củ Chi)",
        "lat": 11.1250, "lon": 106.5180,
        "extra_kw": ["đt744", "chợ an tây", "an tây"]
    },
    {
        "id": "csgt_rain_67",
        "cause": "rain",
        "street": "ĐT744",
        "segment": "Hướng từ ngã 3 Rạch Bắp đến đầu chợ Bưng Còng",
        "ward": "Xã An Điền", "district": "TP. Bến Cát (Giáp Củ Chi)",
        "lat": 11.1350, "lon": 106.5050,
        "extra_kw": ["đt744 rạch bắp", "bưng còng", "an điền"]
    },
    {
        "id": "csgt_rain_68",
        "cause": "rain",
        "street": "Bùi Thanh Khiết",
        "segment": "Từ giao lộ Nguyễn Hữu Trí đến giao lộ Bình Thuận - Chợ Đệm (xã Tân Nhựt)",
        "ward": "Xã Tân Nhựt", "district": "Huyện Bình Chánh",
        "lat": 10.6950, "lon": 106.5820,
        "extra_kw": ["bùi thanh khiết", "chợ đệm tân nhựt", "xã tân nhựt"]
    },
    {
        "id": "csgt_rain_69",
        "cause": "rain",
        "street": "Trịnh Quang Nghị",
        "segment": "Từ Nguyễn Văn Linh đến cầu Ba Tơ",
        "ward": "Phường Bình Đông", "district": "Quận 8",
        "lat": 10.7180, "lon": 106.6450,
        "extra_kw": ["trịnh quang nghị", "cầu ba tơ", "bình đông", "phường 7 quận 8"]
    },
    {
        "id": "csgt_rain_70",
        "cause": "rain",
        "street": "Mã Lò",
        "segment": "Từ Mã Lò đến Hương lộ 2",
        "ward": "Phường Bình Trị Đông A", "district": "Quận Bình Tân",
        "lat": 10.7680, "lon": 106.5980,
        "extra_kw": ["mã lò hương lộ 2", "mã lò", "bình trị đông a"]
    },
    {
        "id": "csgt_rain_71",
        "cause": "rain",
        "street": "Bình Trị Đông - Chiến Lược",
        "segment": "Giao lộ Bình Trị Đông - Chiến Lược",
        "ward": "Phường Bình Trị Đông", "district": "Quận Bình Tân",
        "lat": 10.7650, "lon": 106.6120,
        "extra_kw": ["bình trị đông chiến lược", "chiến lược bình tân", "bình trị đông"]
    },
    {
        "id": "csgt_rain_72",
        "cause": "rain",
        "street": "Quốc lộ 51",
        "segment": "Km43+300 đến Km43+800 (P. Phú Mỹ, hướng Đồng Nai về Phú Mỹ)",
        "ward": "Phường Phú Mỹ", "district": "Thị xã Phú Mỹ (Cửa ngõ liên tỉnh)",
        "lat": 10.5850, "lon": 107.0520,
        "extra_kw": ["quốc lộ 51 phú mỹ", "ql51 km43"]
    },
    {
        "id": "csgt_rain_73",
        "cause": "rain",
        "street": "Quốc lộ 51",
        "segment": "Km44+300 đến Km44+600 (P. Phú Mỹ, hướng Đồng Nai về Phú Mỹ)",
        "ward": "Phường Phú Mỹ", "district": "Thị xã Phú Mỹ (Cửa ngõ liên tỉnh)",
        "lat": 10.5780, "lon": 107.0550,
        "extra_kw": ["ql51 km44"]
    },
    {
        "id": "csgt_rain_74",
        "cause": "rain",
        "street": "Quốc lộ 51",
        "segment": "Km49+100 đến Km49+700 (P. Tân Phước, hướng đi Đồng Nai)",
        "ward": "Phường Tân Phước", "district": "Thị xã Phú Mỹ (Cửa ngõ liên tỉnh)",
        "lat": 10.5420, "lon": 107.0780,
        "extra_kw": ["ql51 tân phước"]
    },
    {
        "id": "csgt_rain_75",
        "cause": "rain",
        "street": "Quốc lộ 51",
        "segment": "Km52+300 đến Km52+800 (ngã tư Hội Bài, P. Tân Hải, hướng đi Đồng Nai)",
        "ward": "Phường Tân Hải", "district": "Thị xã Phú Mỹ (Cửa ngõ liên tỉnh)",
        "lat": 10.5180, "lon": 107.0980,
        "extra_kw": ["ql51 hội bài", "ngã tư hội bài"]
    },
    {
        "id": "csgt_rain_76",
        "cause": "rain",
        "street": "Quốc lộ 51",
        "segment": "Km68+900 đến Km69+400 (P. Phước Thắng, hướng Vũng Tàu đi Bà Rịa)",
        "ward": "Phường Phước Thắng", "district": "TP. Vũng Tàu (Cửa ngõ liên tỉnh)",
        "lat": 10.4250, "lon": 107.1250,
        "extra_kw": ["ql51 phước thắng"]
    },
    {
        "id": "csgt_rain_77",
        "cause": "rain",
        "street": "Quốc lộ 51",
        "segment": "Km73+500 (ngã tư Ẹo Ông Từ, P. Phước Thắng, hướng Vũng Tàu đi Bà Rịa)",
        "ward": "Phường Phước Thắng", "district": "TP. Vũng Tàu (Cửa ngõ liên tỉnh)",
        "lat": 10.4080, "lon": 107.1380,
        "extra_kw": ["ẹo ông từ", "ngã tư ẹo ông từ"]
    },
    {
        "id": "csgt_rain_78",
        "cause": "rain",
        "street": "Lê Hồng Phong nối dài",
        "segment": "Đường Lê Hồng Phong nối dài",
        "ward": "Phường Thắng Tam", "district": "TP. Vũng Tàu (Cửa ngõ liên tỉnh)",
        "lat": 10.3550, "lon": 107.0850,
        "extra_kw": ["lê hồng phong nối dài"]
    },
    {
        "id": "csgt_rain_79",
        "cause": "rain",
        "street": "Đường 30/4",
        "segment": "Đoạn từ cảng Dầu khí đến chợ Thắng Nhất",
        "ward": "Phường Thắng Nhất", "district": "TP. Vũng Tàu (Cửa ngõ liên tỉnh)",
        "lat": 10.3820, "lon": 107.1080,
        "extra_kw": ["đường 30/4 cảng dầu khí", "chợ thắng nhất"]
    },
    {
        "id": "csgt_rain_80",
        "cause": "rain",
        "street": "Đường 2/9",
        "segment": "Đường 2/9",
        "ward": "Phường 11", "district": "TP. Vũng Tàu (Cửa ngõ liên tỉnh)",
        "lat": 10.3950, "lon": 107.1150,
        "extra_kw": ["đường 2/9"]
    },
    {
        "id": "csgt_rain_81",
        "cause": "rain",
        "street": "Nguyễn An Ninh",
        "segment": "Đường Nguyễn An Ninh",
        "ward": "Phường 7", "district": "TP. Vũng Tàu (Cửa ngõ liên tỉnh)",
        "lat": 10.3580, "lon": 107.0820,
        "extra_kw": ["nguyễn an ninh"]
    },
    {
        "id": "csgt_rain_82",
        "cause": "rain",
        "street": "Trương Công Định",
        "segment": "Đường Trương Công Định",
        "ward": "Phường 3", "district": "TP. Vũng Tàu (Cửa ngõ liên tỉnh)",
        "lat": 10.3520, "lon": 107.0780,
        "extra_kw": ["trương công định"]
    },
    {
        "id": "csgt_rain_83",
        "cause": "rain",
        "street": "Nguyễn Tất Thành",
        "segment": "Đường Nguyễn Tất Thành (xã Long Hải)",
        "ward": "Xã Long Hải", "district": "Huyện Long Điền (Cửa ngõ liên tỉnh)",
        "lat": 10.3750, "lon": 107.2420,
        "extra_kw": ["nguyễn tất thành long hải"]
    },

    # =========================================================================
    # II. 39 ĐIỂM NGẬP DO TRIỀU CƯỜNG DÂNG CAO
    # =========================================================================
    {
        "id": "csgt_tide_01",
        "cause": "tide",
        "street": "Lê Khả Phiêu (Song hành)",
        "segment": "Đoạn song hành, hướng từ Hưng Nhơn về Dương Đình Cúc",
        "ward": "Xã Tân Nhựt", "district": "Huyện Bình Chánh",
        "lat": 10.7180, "lon": 106.5820,
        "extra_kw": ["lê khả phiêu", "hưng nhơn", "dương đình cúc", "tân kiên", "tân nhựt"]
    },
    {
        "id": "csgt_tide_02",
        "cause": "tide",
        "street": "Lê Khả Phiêu - Hoàng Đạo Thúy",
        "segment": "Giao Hoàng Đạo Thúy, hướng từ Nguyễn Văn Linh đi cầu Bình Điền",
        "ward": "Xã Tân Nhựt", "district": "Huyện Bình Chánh",
        "lat": 10.7120, "lon": 106.5780,
        "extra_kw": ["hoàng đạo thúy", "cầu bình điền", "tân kiên", "tân nhựt"]
    },
    {
        "id": "csgt_tide_03",
        "cause": "tide",
        "street": "Bến Nghé",
        "segment": "Số 4 Bến Nghé (Tân Thuận)",
        "ward": "Phường Tân Thuận Đông", "district": "Quận 7",
        "lat": 10.7620, "lon": 106.7320,
        "extra_kw": ["đường bến nghé", "số 4 bến nghé", "tân thuận", "tân thuận đông"]
    },
    {
        "id": "csgt_tide_04",
        "cause": "tide",
        "street": "Trần Xuân Soạn",
        "segment": "Từ Huỳnh Tấn Phát đến Lâm Văn Bền",
        "ward": "Phường Tân Kiểng", "district": "Quận 7",
        "lat": 10.7490, "lon": 106.7150,
        "extra_kw": ["trần xuân soạn", "lâm văn bền", "tân kiểng"]
    },
    {
        "id": "csgt_tide_05",
        "cause": "tide",
        "street": "Nguyễn Thị Thập - Tân Mỹ",
        "segment": "Giao lộ Nguyễn Thị Thập - Tân Mỹ",
        "ward": "Phường Tân Phú", "district": "Quận 7",
        "lat": 10.7380, "lon": 106.7240,
        "extra_kw": ["nguyễn thị thập tân mỹ", "nguyễn thị thập", "tân phú"]
    },
    {
        "id": "csgt_tide_06",
        "cause": "tide",
        "street": "Nguyễn Thị Thập - Lê Văn Lương",
        "segment": "Giao lộ Nguyễn Thị Thập - Lê Văn Lương",
        "ward": "Phường Tân Quy", "district": "Quận 7",
        "lat": 10.7420, "lon": 106.7060,
        "extra_kw": ["nguyễn thị thập lê văn lương", "tân quy"]
    },
    {
        "id": "csgt_tide_07",
        "cause": "tide",
        "street": "Lê Văn Lương",
        "segment": "Đoạn qua xã Nhà Bè",
        "ward": "Xã Nhà Bè", "district": "Huyện Nhà Bè",
        "lat": 10.7180, "lon": 106.7020,
        "extra_kw": ["lê văn lương nhà bè", "lê văn lương", "xã nhà bè"]
    },
    {
        "id": "csgt_tide_08",
        "cause": "tide",
        "street": "Lê Văn Lương (Cầu Rạch Tôm)",
        "segment": "Khoảng 250m trước công trình cầu Rạch Tôm, hướng đi Tây Ninh/trung tâm",
        "ward": "Xã Hiệp Phước", "district": "Huyện Nhà Bè",
        "lat": 10.6780, "lon": 106.7050,
        "extra_kw": ["cầu rạch tôm", "lê văn lương rạch tôm", "nhơn đức", "hiệp phước"]
    },
    {
        "id": "csgt_tide_09",
        "cause": "tide",
        "street": "Huỳnh Tấn Phát - Phạm Hữu Lầu",
        "segment": "Giao lộ Huỳnh Tấn Phát - Phạm Hữu Lầu",
        "ward": "Phường Phú Mỹ", "district": "Quận 7",
        "lat": 10.7150, "lon": 106.7380,
        "extra_kw": ["huỳnh tấn phát phạm hữu lầu", "phạm hữu lầu", "phú mỹ"]
    },
    {
        "id": "csgt_tide_10",
        "cause": "tide",
        "street": "Huỳnh Tấn Phát - Hoàng Quốc Việt",
        "segment": "Giao lộ Huỳnh Tấn Phát - Hoàng Quốc Việt",
        "ward": "Phường Phú Thuận", "district": "Quận 7",
        "lat": 10.7250, "lon": 106.7370,
        "extra_kw": ["huỳnh tấn phát hoàng quốc việt", "hoàng quốc việt", "phú thuận"]
    },
    {
        "id": "csgt_tide_11",
        "cause": "tide",
        "street": "Nguyễn Lương Bằng - Hoàng Quốc Việt",
        "segment": "Giao Hoàng Quốc Việt, hướng từ Phạm Hữu Lầu về Nguyễn Lương Bằng",
        "ward": "Phường Phú Mỹ", "district": "Quận 7",
        "lat": 10.7220, "lon": 106.7210,
        "extra_kw": ["nguyễn lương bằng hoàng quốc việt", "phú mỹ"]
    },
    {
        "id": "csgt_tide_12",
        "cause": "tide",
        "street": "Nguyễn Lương Bằng - Phạm Hữu Lầu",
        "segment": "Giao lộ Nguyễn Lương Bằng - Phạm Hữu Lầu",
        "ward": "Phường Phú Mỹ", "district": "Quận 7",
        "lat": 10.7140, "lon": 106.7220,
        "extra_kw": ["nguyễn lương bằng phạm hữu lầu", "phú mỹ"]
    },
    {
        "id": "csgt_tide_13",
        "cause": "tide",
        "street": "Phạm Hữu Lầu",
        "segment": "Từ giao lộ Huỳnh Tấn Phát đến cầu Phước Long",
        "ward": "Phường Phú Mỹ", "district": "Quận 7",
        "lat": 10.7160, "lon": 106.7280,
        "extra_kw": ["phạm hữu lầu cầu phước long", "cầu phước long", "phú mỹ"]
    },
    {
        "id": "csgt_tide_14",
        "cause": "tide",
        "street": "Nguyễn Hữu Thọ",
        "segment": "Từ giao lộ Phạm Hữu Lầu đến cầu Rạch Đỉa 2 (hướng từ Nhà Bè vào trung tâm)",
        "ward": "Xã Nhà Bè", "district": "Huyện Nhà Bè",
        "lat": 10.7180, "lon": 106.7080,
        "extra_kw": ["nguyễn hữu thọ cầu rạch đỉa", "cầu rạch đỉa 2", "phước kiển", "xã nhà bè"]
    },
    {
        "id": "csgt_tide_15",
        "cause": "tide",
        "street": "Nguyễn Bình",
        "segment": "Từ giao lộ Huỳnh Tấn Phát đến cầu Mương Chuối",
        "ward": "Xã Nhà Bè", "district": "Huyện Nhà Bè",
        "lat": 10.6850, "lon": 106.7450,
        "extra_kw": ["nguyễn bình cầu mương chuối", "cầu mương chuối", "phú xuân", "xã nhà bè"]
    },
    {
        "id": "csgt_tide_16",
        "cause": "tide",
        "street": "Lê Thị Tám",
        "segment": "Đường Lê Thị Tám (xã Hiệp Phước)",
        "ward": "Xã Hiệp Phước", "district": "Huyện Nhà Bè",
        "lat": 10.6280, "lon": 106.7250,
        "extra_kw": ["lê thị tám", "hiệp phước"]
    },
    {
        "id": "csgt_tide_17",
        "cause": "tide",
        "street": "Nguyễn Văn Quỳ",
        "segment": "Hai bên hông cầu Phú Mỹ",
        "ward": "Phường Phú Thuận", "district": "Quận 7",
        "lat": 10.7420, "lon": 106.7380,
        "extra_kw": ["nguyễn văn quỳ", "hông cầu phú mỹ", "phú thuận"]
    },
    {
        "id": "csgt_tide_18",
        "cause": "tide",
        "street": "Gò Công",
        "segment": "Đường Gò Công (Quận 5 / Chợ Lớn)",
        "ward": "Phường 13", "district": "Quận 5",
        "lat": 10.7510, "lon": 106.6540,
        "extra_kw": ["đường gò công quận 5", "chợ lớn", "phường 13 quận 5"]
    },
    {
        "id": "csgt_tide_19",
        "cause": "tide",
        "street": "Phan Phú Tiên",
        "segment": "Đường Phan Phú Tiên (Quận 5)",
        "ward": "Phường 11", "district": "Quận 5",
        "lat": 10.7535, "lon": 106.6610,
        "extra_kw": ["phan phú tiên", "phường 10 quận 5", "phường 11 quận 5"]
    },
    {
        "id": "csgt_tide_20",
        "cause": "tide",
        "street": "Võ Văn Kiệt",
        "segment": "Từ Phạm Phú Thứ đến Bình Tiên",
        "ward": "Phường 1", "district": "Quận 6",
        "lat": 10.7430, "lon": 106.6480,
        "extra_kw": ["võ văn kiệt phạm phú thứ", "bình tiên", "phường 3 quận 6"]
    },
    {
        "id": "csgt_tide_21",
        "cause": "tide",
        "street": "Phạm Phú Thứ",
        "segment": "Từ Võ Văn Kiệt đến Phạm Văn Chí",
        "ward": "Phường 1", "district": "Quận 6",
        "lat": 10.7450, "lon": 106.6470,
        "extra_kw": ["phạm phú thứ phạm văn chí", "phường 3 quận 6"]
    },
    {
        "id": "csgt_tide_22",
        "cause": "tide",
        "street": "Song Hành Lớn",
        "segment": "Đường Song Hành Lớn (P. Bình Phú)",
        "ward": "Phường 10", "district": "Quận 6",
        "lat": 10.7460, "lon": 106.6350,
        "extra_kw": ["song hành lớn", "bình phú", "phường bình phú"]
    },
    {
        "id": "csgt_tide_23",
        "cause": "tide",
        "street": "Trần Văn Kiểu - Đường 32",
        "segment": "Giao lộ Trần Văn Kiểu - đường 32",
        "ward": "Phường 10", "district": "Quận 6",
        "lat": 10.7470, "lon": 106.6310,
        "extra_kw": ["trần văn kiểu", "đường 32", "phường 10 quận 6"]
    },
    {
        "id": "csgt_tide_24",
        "cause": "tide",
        "street": "Chân cầu Lò Gốm",
        "segment": "Chân cầu Lò Gốm (Quận 6)",
        "ward": "Phường 11", "district": "Quận 6",
        "lat": 10.7410, "lon": 106.6410,
        "extra_kw": ["chân cầu lò gốm", "cầu lò gốm", "phường 11 quận 6"]
    },
    {
        "id": "csgt_tide_25",
        "cause": "tide",
        "street": "Mai Xuân Thưởng",
        "segment": "Đường Mai Xuân Thưởng",
        "ward": "Phường 2", "district": "Quận 6",
        "lat": 10.7480, "lon": 106.6520,
        "extra_kw": ["mai xuân thưởng", "phường 2 quận 6", "phường 6 quận 6"]
    },
    {
        "id": "csgt_tide_26",
        "cause": "tide",
        "street": "Cao Đạt",
        "segment": "Đường Cao Đạt (Quận 5)",
        "ward": "Phường 1", "district": "Quận 5",
        "lat": 10.7520, "lon": 106.6820,
        "extra_kw": ["đường cao đạt", "phường 1 quận 5"]
    },
    {
        "id": "csgt_tide_27",
        "cause": "tide",
        "street": "An Bình",
        "segment": "Đường An Bình (Quận 5)",
        "ward": "Phường 5", "district": "Quận 5",
        "lat": 10.7510, "lon": 106.6710,
        "extra_kw": ["đường an bình", "phường 5 quận 5", "phường 6 quận 5"]
    },
    {
        "id": "csgt_tide_28",
        "cause": "tide",
        "street": "Nguyễn Biểu",
        "segment": "Từ Trần Hưng Đạo đến Võ Văn Kiệt (Cầu Chữ Y)",
        "ward": "Phường 1", "district": "Quận 5",
        "lat": 10.7538, "lon": 106.6830,
        "heat_points": [[10.7554, 106.6826], [10.7538, 106.6830], [10.7512, 106.6835]],
        "extra_kw": ["đường nguyễn biểu", "phường 1 quận 5"]
    },
    {
        "id": "csgt_tide_29",
        "cause": "tide",
        "street": "Trần Hưng Đạo",
        "segment": "Từ Nguyễn Biểu đến Nguyễn Tri Phương",
        "ward": "Phường 7", "district": "Quận 5",
        "lat": 10.7520, "lon": 106.6740,
        "extra_kw": ["trần hưng đạo nguyễn biểu", "nguyễn tri phương", "phường 7 quận 5", "phường 8 quận 5"]
    },
    {
        "id": "csgt_tide_30",
        "cause": "tide",
        "street": "Phạm Thế Hiển (Triều cường)",
        "segment": "Đường Phạm Thế Hiển (Đoạn ven kênh Đôi)",
        "ward": "Phường Chánh Hưng", "district": "Quận 8",
        "lat": 10.7420, "lon": 106.6720,
        "extra_kw": ["phạm thế hiển quận 8", "phạm thế hiển triều cường", "chánh hưng", "phường 4 quận 8"]
    },
    {
        "id": "csgt_tide_31",
        "cause": "tide",
        "street": "Dương Bá Trạc",
        "segment": "Đường Dương Bá Trạc (Chân cầu Kênh Xáng)",
        "ward": "Phường Chánh Hưng", "district": "Quận 8",
        "lat": 10.7460, "lon": 106.6880,
        "extra_kw": ["dương bá trạc", "cầu kênh xáng", "rạch ông", "chánh hưng", "phường 1 quận 8"]
    },
    {
        "id": "csgt_tide_32",
        "cause": "tide",
        "street": "Chân cầu Rạch Chiếc (Làn xe máy)",
        "segment": "Chân cầu Rạch Chiếc, hướng từ Võ Nguyên Giáp đi RMK (làn xe máy)",
        "ward": "Phường Phước Long", "district": "TP. Thủ Đức",
        "lat": 10.8170, "lon": 106.7580,
        "extra_kw": ["chân cầu rạch chiếc làn xe máy", "chân cầu rạch chiếc xe máy", "rmk", "phước long", "phước long a"]
    },
    {
        "id": "csgt_tide_33",
        "cause": "tide",
        "street": "Mai Chí Thọ (New City)",
        "segment": "Trước chung cư New City",
        "ward": "Phường An Khánh", "district": "TP. Thủ Đức",
        "lat": 10.7850, "lon": 106.7320,
        "extra_kw": ["mai chí thọ new city", "chung cư new city", "an khánh"]
    },
    {
        "id": "csgt_tide_34",
        "cause": "tide",
        "street": "Đường R12 - Chân cầu Ba Son",
        "segment": "Đường R12, dưới chân cầu Ba Son (Thủ Thiêm)",
        "ward": "Phường Thủ Thiêm", "district": "TP. Thủ Đức",
        "lat": 10.7760, "lon": 106.7110,
        "extra_kw": ["đường r12", "cầu ba son", "thủ thiêm"]
    },
    {
        "id": "csgt_tide_35",
        "cause": "tide",
        "street": "Nguyễn Văn Hưởng",
        "segment": "Đường Nguyễn Văn Hưởng (Thảo Điền)",
        "ward": "Phường Thảo Điền", "district": "TP. Thủ Đức",
        "lat": 10.8080, "lon": 106.7350,
        "extra_kw": ["nguyễn văn hưởng thảo điền", "nguyễn văn hưởng", "thảo điền"]
    },
    {
        "id": "csgt_tide_36",
        "cause": "tide",
        "street": "Nguyễn Duy Trinh",
        "segment": "Cây xăng Kim Long 813 (P. Long Trường)",
        "ward": "Phường Long Trường", "district": "TP. Thủ Đức",
        "lat": 10.7980, "lon": 106.8120,
        "extra_kw": ["nguyễn duy trinh", "cây xăng kim long 813", "long trường"]
    },
    {
        "id": "csgt_tide_37",
        "cause": "tide",
        "street": "Liên Phường - Bưng Ông Thoàn",
        "segment": "Giao lộ Liên Phường - Bưng Ông Thoàn",
        "ward": "Phường Phú Hữu", "district": "TP. Thủ Đức",
        "lat": 10.8020, "lon": 106.7980,
        "extra_kw": ["liên phường bưng ông thoàn", "bưng ông thoàn", "phú hữu"]
    },
    {
        "id": "csgt_tide_38",
        "cause": "tide",
        "street": "Bờ kè Lô F Cư xá Thanh Đa",
        "segment": "Bờ kè Lô F, cư xá Thanh Đa (Phường 27 / Bình Quới)",
        "ward": "Phường 27", "district": "Quận Bình Thạnh",
        "lat": 10.8220, "lon": 106.7260,
        "extra_kw": ["cư xá thanh đa", "lô f thanh đa", "bờ kè thanh đa", "bình quới", "phường 27 bình thạnh"]
    },
    {
        "id": "csgt_tide_39",
        "cause": "tide",
        "street": "Hà Huy Giáp",
        "segment": "Đường Hà Huy Giáp (P. An Phú Đông)",
        "ward": "Phường An Phú Đông", "district": "Quận 12",
        "lat": 10.8580, "lon": 106.6910,
        "extra_kw": ["hà huy giáp an phú đông", "hà huy giáp", "an phú đông"]
    }
]

def build_hotspots_dataset():
    processed = []
    for item in RAW_CSGT_DATA:
        lat = item["lat"]
        lon = item["lon"]
        street = item["street"]
        segment = item.get("segment", "")
        cause = item["cause"]
        cause_label = "Mưa lớn, nước không thoát kịp" if cause == "rain" else "Triều cường dâng cao"
        
        if segment:
            if segment.lower().startswith(street.lower()):
                display_name = segment
            else:
                display_name = f"{street} ({segment})"
        else:
            display_name = street
            
        heat_points = item.get("heat_points") or [
            [lat, lon],
            [round(lat + 0.0015, 4), round(lon + 0.0015, 4)],
            [round(lat - 0.0015, 4), round(lon - 0.0015, 4)]
        ]
        
        cur_ward = item["ward"]
        district = item.get("district", "")
        official_ward = RESOLVER.resolve_to_official_ward(cur_ward, district) or cur_ward
        
        extra_kws = list(item.get("extra_kw", []))
        if official_ward != cur_ward:
            extra_kws.append(cur_ward)
            extra_kws.append(f"{cur_ward} {district}")
            
        kws = make_keywords(street, extra_kws)
        
        processed.append({
            "id": item["id"],
            "source": "PC08_CSGT_TPHCM",
            "cause": cause,
            "cause_label": cause_label,
            "street": street,
            "segment": segment,
            "display_name": display_name,
            "ward": official_ward,
            "district": district,
            "region": "TPHCM",
            "lat": lat,
            "lon": lon,
            "heat_points": heat_points,
            "priority": 3,
            "type": f"Điểm cảnh báo CSGT ({cause_label})",
            "keywords": kws
        })

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "csgt_122_flood_hotspots.json")
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)
        
    print(f"[Success] Đã tạo thành công {len(processed)} điểm ngập chuẩn hóa CSGT tại: {out_file}")
    rain_cnt = sum(1 for p in processed if p["cause"] == "rain")
    tide_cnt = sum(1 for p in processed if p["cause"] == "tide")
    print(f"  - Mưa lớn: {rain_cnt} điểm")
    print(f"  - Triều cường: {tide_cnt} điểm")

if __name__ == "__main__":
    build_hotspots_dataset()
