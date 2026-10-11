# -*- coding: utf-8 -*-
"""
core/admin_resolver.py
Module quản lý và giải mã địa giới hành chính TP. Hồ Chí Minh
theo Nghị quyết 1685/NQ-UBTVQH15 (hiệu lực 01/07/2025).

Đóng vai trò là "Single Source of Truth (SSOT)" cho toàn bộ hệ thống:
1. Tra cứu thông tin chi tiết 168 đơn vị hành chính mới.
2. Quy đổi 2 chiều: Tên cũ (trước sáp nhập) -> Tên mới chính thức (sau sáp nhập).
3. Kiểm tra tính hợp lệ của trường `ward` trong các tập dữ liệu điểm ngập (CSGT, crawler).
"""

import json
import os
import re
import unicodedata
from typing import Any, Dict, List, Optional, Set

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ADMIN_UNITS_FILE = os.path.join(BASE_DIR, "data", "hcmc_168_administrative_units.json")

def _normalize_str(s: str) -> str:
    if not s:
        return ""
    nfkd = unicodedata.normalize('NFKD', s)
    no_acc = ''.join([c for c in nfkd if not unicodedata.combining(c)]).replace('đ', 'd').replace('Đ', 'D')
    return re.sub(r'\s+', ' ', no_acc.strip().lower())

# BẢNG ÁNH XẠ CHÍNH THỨC CẤP QUẬN CŨ -> PHƯỜNG MỚI THEO NQ 1685
DISTRICT_OLD_TO_NEW = {
    # Quận 1
    "quan 1": {
        "ben nghe": "Phường Sài Gòn", "da kao": "Phường Tân Định", "tan dinh": "Phường Tân Định",
        "ben thanh": "Phường Bến Thành", "pham ngu lao": "Phường Bến Thành",
        "nguyen thai binh": "Phường Sài Gòn", "cau ong lanh": "Phường Cầu Ông Lãnh",
        "nguyen cu trinh": "Phường Cầu Ông Lãnh", "cau kho": "Phường Cầu Ông Lãnh", "co giang": "Phường Cầu Ông Lãnh"
    },
    # Quận 3
    "quan 3": {
        "1": "Phường Bàn Cờ", "2": "Phường Bàn Cờ", "3": "Phường Bàn Cờ", "5": "Phường Bàn Cờ",
        "vo thi sau": "Phường Xuân Hòa", "4": "Phường Bàn Cờ",
        "9": "Phường Nhiêu Lộc", "11": "Phường Nhiêu Lộc", "12": "Phường Nhiêu Lộc", "14": "Phường Nhiêu Lộc"
    },
    # Quận 4
    "quan 4": {
        "13": "Phường Xóm Chiếu", "14": "Phường Xóm Chiếu", "12": "Phường Xóm Chiếu", "16": "Phường Xóm Chiếu", "18": "Phường Xóm Chiếu", "10": "Phường Khánh Hội", "6": "Phường Khánh Hội",
        "8": "Phường Khánh Hội", "9": "Phường Khánh Hội", "15": "Phường Khánh Hội",
        "1": "Phường Vĩnh Hội", "3": "Phường Vĩnh Hội", "2": "Phường Vĩnh Hội", "4": "Phường Vĩnh Hội"
    },
    # Quận 5
    "quan 5": {
        "1": "Phường Chợ Quán", "2": "Phường Chợ Quán", "4": "Phường Chợ Quán",
        "5": "Phường An Đông", "7": "Phường An Đông", "9": "Phường An Đông",
        "11": "Phường Chợ Lớn", "12": "Phường Chợ Lớn", "13": "Phường Chợ Lớn", "14": "Phường Chợ Lớn"
    },
    # Quận 6
    "quan 6": {
        "2": "Phường Bình Tây", "9": "Phường Bình Tây",
        "1": "Phường Bình Tiên", "7": "Phường Bình Tiên", "8": "Phường Bình Tiên",
        "10": "Phường Bình Phú", "11": "Phường Bình Phú",
        "12": "Phường Phú Lâm", "13": "Phường Phú Lâm", "14": "Phường Phú Lâm"
    },
    # Quận 7
    "quan 7": {
        "binh thuan": "Phường Tân Thuận", "tan thuan dong": "Phường Tân Thuận", "tan thuan tay": "Phường Tân Thuận",
        "phu thuan": "Phường Phú Thuận", "phu my": "Phường Phú Thuận",
        "tan phu": "Phường Tân Mỹ",
        "tan phong": "Phường Tân Hưng", "tan quy": "Phường Tân Hưng", "tan kieng": "Phường Tân Hưng", "tan hung": "Phường Tân Hưng"
    },
    # Quận 8
    "quan 8": {
        "1": "Phường Chánh Hưng", "2": "Phường Chánh Hưng", "3": "Phường Chánh Hưng", "4": "Phường Chánh Hưng",
        "rach ong": "Phường Chánh Hưng", "hung phu": "Phường Chánh Hưng", "8": "Phường Chánh Hưng", "9": "Phường Chánh Hưng", "10": "Phường Chánh Hưng",
        "5": "Phường Chánh Hưng",
        "14": "Phường Phú Định", "15": "Phường Phú Định", "16": "Phường Phú Định", "xom cui": "Phường Phú Định", "11": "Phường Phú Định", "12": "Phường Phú Định", "13": "Phường Phú Định",
        "6": "Phường Bình Đông", "7": "Phường Bình Đông", "binh dong": "Phường Bình Đông"
    },
    # Quận 10
    "quan 10": {
        "6": "Phường Diên Hồng", "8": "Phường Diên Hồng", "14": "Phường Diên Hồng",
        "1": "Phường Vườn Lài", "2": "Phường Vườn Lài", "4": "Phường Vườn Lài", "9": "Phường Vườn Lài", "10": "Phường Vườn Lài",
        "12": "Phường Hòa Hưng", "13": "Phường Hòa Hưng", "15": "Phường Hòa Hưng"
    },
    # Quận 11
    "quan 11": {
        "1": "Phường Minh Phụng", "7": "Phường Minh Phụng", "16": "Phường Minh Phụng",
        "3": "Phường Bình Thới", "10": "Phường Bình Thới", "8": "Phường Bình Thới",
        "5": "Phường Hòa Bình", "14": "Phường Hòa Bình",
        "11": "Phường Phú Thọ", "15": "Phường Phú Thọ"
    },
    # Quận 12
    "quan 12": {
        "tan thoi nhat": "Phường Đông Hưng Thuận", "tan hung thuan": "Phường Đông Hưng Thuận", "dong hung thuan": "Phường Đông Hưng Thuận",
        "tan chanh hiep": "Phường Trung Mỹ Tây", "trung my tay": "Phường Trung Mỹ Tây",
        "hiep thanh": "Phường Tân Thới Hiệp", "tan thoi hiep": "Phường Tân Thới Hiệp",
        "thanh xuan": "Phường Thới An", "thoi an": "Phường Thới An",
        "thanh loc": "Phường An Phú Đông", "an phu dong": "Phường An Phú Đông"
    },
    # Quận Bình Tân
    "binh tan": {
        "binh tri dong b": "Phường An Lạc", "an lac a": "Phường An Lạc", "an lac": "Phường An Lạc",
        "binh hung hoa b": "Phường Bình Tân", "tan tao": "Phường Tân Tạo", "tan tao a": "Phường Tân Tạo",
        "binh tri dong": "Phường Bình Trị Đông", "binh tri dong a": "Phường Bình Trị Đông",
        "binh hung hoa": "Phường Bình Hưng Hòa", "binh hung hoa a": "Phường Bình Hưng Hòa"
    },
    # Quận Bình Thạnh (Chuẩn hóa ĐVHC mới theo NQ 1685 & NQ 1278)
    "binh thanh": {
        "1": "Phường Gia Định", "2": "Phường Gia Định", "3": "Phường Gia Định", "7": "Phường Gia Định", "17": "Phường Gia Định",
        "12": "Phường Bình Thạnh", "14": "Phường Bình Thạnh", "15": "Phường Bình Thạnh", "24": "Phường Bình Thạnh", "26": "Phường Bình Thạnh",
        "5": "Phường Bình Lợi Trung", "6": "Phường Bình Lợi Trung", "11": "Phường Bình Lợi Trung", "13": "Phường Bình Lợi Trung",
        "19": "Phường Thạnh Mỹ Tây", "21": "Phường Thạnh Mỹ Tây", "22": "Phường Thạnh Mỹ Tây", "25": "Phường Thạnh Mỹ Tây",
        "27": "Phường Bình Quới", "28": "Phường Bình Quới",
        "binh thanh": "Phường Bình Thạnh", "gia dinh": "Phường Gia Định", "bach dang": "Phường Bình Thạnh"
    },
    # Quận Gò Vấp
    "go vap": {
        "1": "Phường Hạnh Thông", "3": "Phường Hạnh Thông",
        "5": "Phường An Nhơn", "6": "Phường An Nhơn",
        "10": "Phường Gò Vấp", "17": "Phường Gò Vấp",
        "15": "Phường An Hội Đông", "16": "Phường An Hội Đông",
        "8": "Phường Thông Tây Hội", "11": "Phường Thông Tây Hội",
        "12": "Phường An Hội Tây", "14": "Phường An Hội Tây"
    },
    # Quận Phú Nhuận
    "phu nhuan": {
        "4": "Phường Đức Nhuận", "5": "Phường Đức Nhuận", "9": "Phường Đức Nhuận",
        "1": "Phường Cầu Kiệu", "2": "Phường Cầu Kiệu", "7": "Phường Cầu Kiệu",
        "8": "Phường Phú Nhuận", "10": "Phường Phú Nhuận", "11": "Phường Phú Nhuận", "13": "Phường Phú Nhuận", "15": "Phường Phú Nhuận"
    },
    # Quận Tân Bình
    "tan binh": {
        "1": "Phường Tân Sơn Hòa", "2": "Phường Tân Sơn Hòa", "3": "Phường Tân Sơn Hòa",
        "4": "Phường Tân Sơn Nhất", "5": "Phường Tân Sơn Nhất", "7": "Phường Tân Sơn Nhất",
        "6": "Phường Tân Hòa", "8": "Phường Tân Hòa", "9": "Phường Tân Hòa",
        "10": "Phường Bảy Hiền", "11": "Phường Bảy Hiền", "12": "Phường Bảy Hiền",
        "13": "Phường Tân Bình", "14": "Phường Tân Bình",
        "15": "Phường Tân Sơn"
    },
    # Quận Tân Phú
    "tan phu": {
        "tay thanh": "Phường Tây Thạnh", "son ky": "Phường Tây Thạnh",
        "tan son nhi": "Phường Tân Sơn Nhì", "tan quy": "Phường Tân Sơn Nhì", "tan thanh": "Phường Tân Sơn Nhì",
        "phu tho hoa": "Phường Phú Thọ Hòa",
        "phu trung": "Phường Tân Phú", "hoa thanh": "Phường Tân Phú",
        "hiep tan": "Phường Phú Thạnh", "phu thanh": "Phường Phú Thạnh", "tan thoi hoa": "Phường Phú Thạnh"
    },
    # TP. Thủ Đức
    "thu duc": {
        "hiep binh chanh": "Phường Hiệp Bình", "hiep binh phuoc": "Phường Hiệp Bình",
        "binh tho": "Phường Thủ Đức", "linh chieu": "Phường Thủ Đức", "truong tho": "Phường Thủ Đức", "linh dong": "Phường Thủ Đức",
        "binh chieu": "Phường Tam Bình", "tam phu": "Phường Tam Bình", "tam binh": "Phường Tam Bình",
        "linh trung": "Phường Linh Xuân", "linh xuan": "Phường Linh Xuân", "linh tay": "Phường Linh Xuân",
        "hiep phu": "Phường Tăng Nhơn Phú", "tang nhon phu a": "Phường Tăng Nhơn Phú", "tang nhon phu b": "Phường Tăng Nhơn Phú",
        "long binh": "Phường Long Bình", "long thanh my": "Phường Long Bình",
        "truong thanh": "Phường Long Phước", "long phuoc": "Phường Long Phước",
        "phu huu": "Phường Long Trường", "long truong": "Phường Long Trường",
        "thanh my loi": "Phường Cát Lái", "cat lai": "Phường Cát Lái",
        "binh trung dong": "Phường Bình Trưng", "binh trung tay": "Phường Bình Trưng",
        "phuoc binh": "Phường Phước Long", "phuoc long a": "Phường Phước Long", "phuoc long b": "Phường Phước Long",
        "thu thiem": "Phường An Khánh", "an loi dong": "Phường An Khánh", "thao dien": "Phường An Khánh", "an khanh": "Phường An Khánh", "an phu": "Phường An Khánh"
    },
    # Huyện Bình Chánh
    "binh chanh": {
        "vinh loc a": "Xã Vĩnh Lộc", "vinh loc b": "Xã Tân Vĩnh Lộc", "pham van hai": "Xã Vĩnh Lộc",
        "le minh xuan": "Xã Bình Lợi", "binh loi": "Xã Bình Lợi",
        "tan tuc": "Xã Tân Nhựt", "tan nhut": "Xã Tân Nhựt", "tan kien": "Xã Tân Nhựt",
        "tan quy tay": "Xã Bình Chánh", "binh chanh": "Xã Bình Chánh", "an phu tay": "Xã Bình Chánh",
        "da phuoc": "Xã Hưng Long", "qui duc": "Xã Hưng Long", "hung long": "Xã Hưng Long",
        "phong phu": "Xã Bình Hưng", "binh hung": "Xã Bình Hưng"
    },
    # Huyện Cần Giờ
    "can gio": {
        "tam thon hiep": "Xã Bình Khánh", "binh khanh": "Xã Bình Khánh",
        "ly nhon": "Xã An Thới Đông", "an thoi dong": "Xã An Thới Đông",
        "long hoa": "Xã Cần Giờ", "can thanh": "Xã Cần Giờ",
        "thanh an": "Xã Thạnh An"
    },
    # Huyện Củ Chi
    "cu chi": {
        "tan phu trung": "Xã Củ Chi", "tan thong hoi": "Xã Củ Chi", "phuoc vinh an": "Xã Củ Chi",
        "thi tran cu chi": "Xã Tân An Hội", "phuoc hiep": "Xã Tân An Hội", "tan an hoi": "Xã Tân An Hội",
        "trung lap thuong": "Xã Thái Mỹ", "phuoc thanh": "Xã Thái Mỹ", "thai my": "Xã Thái Mỹ",
        "phu my hung": "Xã An Nhơn Tây", "an phu": "Xã An Nhơn Tây", "an nhon tay": "Xã An Nhơn Tây",
        "pham van coi": "Xã Nhuận Đức", "trung lap ha": "Xã Nhuận Đức", "nhuan duc": "Xã Nhuận Đức",
        "tan thanh tay": "Xã Phú Hòa Đông", "tan thanh dong": "Xã Phú Hòa Đông", "phu hoa dong": "Xã Phú Hòa Đông",
        "binh my": "Xã Bình Mỹ", "hoa phu": "Xã Bình Mỹ", "trung an": "Xã Bình Mỹ"
    },
    # Huyện Hóc Môn
    "hoc mon": {
        "thoi tam thon": "Xã Đông Thạnh", "nhi binh": "Xã Đông Thạnh", "dong thanh": "Xã Đông Thạnh",
        "tan hiep": "Xã Hóc Môn", "tan xuan": "Xã Hóc Môn", "thi tran hoc mon": "Xã Hóc Môn",
        "tan thoi nhi": "Xã Xuân Thới Sơn", "xuan thoi dong": "Xã Xuân Thới Sơn", "xuan thoi son": "Xã Xuân Thới Sơn",
        "xuan thoi thuong": "Xã Bà Điểm", "trung chanh": "Xã Bà Điểm", "ba diem": "Xã Bà Điểm"
    },
    # Huyện Nhà Bè
    "nha be": {
        "thi tran nha be": "Xã Nhà Bè", "phu xuan": "Xã Nhà Bè", "phuoc kien": "Xã Nhà Bè", "phuoc loc": "Xã Nhà Bè",
        "nhon duc": "Xã Hiệp Phước", "long thoi": "Xã Hiệp Phước", "hiep phuoc": "Xã Hiệp Phước"
    },
    # TP. Vũng Tàu (Bà Rịa - Vũng Tàu cũ)
    "vung tau": {
        "1": "Phường Vũng Tàu", "2": "Phường Vũng Tàu", "3": "Phường Vũng Tàu", "4": "Phường Vũng Tàu", "5": "Phường Vũng Tàu",
        "thang nhi": "Phường Vũng Tàu", "thang tam": "Phường Vũng Tàu",
        "7": "Phường Tam Thắng", "8": "Phường Tam Thắng", "9": "Phường Tam Thắng", 
        "10": "Phường Rạch Dừa", "thang nhat": "Phường Rạch Dừa", "rach dua": "Phường Rạch Dừa",
        "11": "Phường Phước Thắng", "12": "Phường Phước Thắng",
        "long son": "Xã Long Sơn"
    },
    # TP. Dĩ An (Bình Dương cũ)
    "di an": {
        "binh an": "Phường Đông Hòa", "binh thang": "Phường Đông Hòa", "dong hoa": "Phường Đông Hòa",
        "an binh": "Phường Dĩ An", "di an": "Phường Dĩ An", "tan dong hiep": "Phường Tân Đông Hiệp",
        "tan binh": "Phường Tân Đông Hiệp"
    },
    # TP. Bến Cát (Bình Dương cũ)
    "ben cat": {
        "an tay": "Phường Tây Nam", "an dien": "Phường Long Nguyên",
        "my phuoc": "Phường Bến Cát", "lai hung": "Phường Bến Cát",
        "thoi hoa": "Phường Thới Hòa"
    }
}

class AdminResolver:
    def __init__(self, data_path: str = ADMIN_UNITS_FILE):
        self.data_path = data_path
        self.units: List[Dict[str, Any]] = []
        self.by_id: Dict[str, Dict[str, Any]] = {}
        self.by_name_norm: Dict[str, Dict[str, Any]] = {}
        self.valid_ward_names: Set[str] = set()
        self.old_to_new_map: Dict[str, str] = {}
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.data_path):
            return
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.units = json.load(f)
        except Exception:
            self.units = []
            return

        for u in self.units:
            uid = u.get("id")
            name = u.get("name", "")
            short_name = u.get("short_name", "")
            
            if uid:
                self.by_id[uid] = u
            if name:
                self.valid_ward_names.add(name)
                self.by_name_norm[_normalize_str(name)] = u
            if short_name:
                self.by_name_norm[_normalize_str(short_name)] = u

            # Xây dựng bản đồ ánh xạ tên cũ -> tên mới
            merged_from = u.get("merged_from", [])
            for old_u in merged_from:
                norm_old = _normalize_str(old_u)
                if norm_old:
                    self.old_to_new_map[norm_old] = name

        # Bổ sung các ánh xạ phường cũ đặc thù tránh sót lọt
        extra_old = {
            "24": "Phường Bình Thạnh", "phuong 24": "Phường Bình Thạnh",
            "15": "Phường Bình Thạnh", "phuong 15": "Phường Bình Thạnh",
            "21": "Phường Thạnh Mỹ Tây", "phuong 21": "Phường Thạnh Mỹ Tây",
            "binh thanh": "Phường Bình Thạnh", "quan binh thanh": "Phường Bình Thạnh",
            "bach dang": "Phường Bình Thạnh", "phuong bach dang": "Phường Bình Thạnh"
        }
        for k, v in extra_old.items():
            self.old_to_new_map[_normalize_str(k)] = v

    def get_all_units(self) -> List[Dict[str, Any]]:
        """Trả về toàn bộ 168 đơn vị hành chính."""
        return self.units

    def get_unit_by_id(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """Tra cứu theo mã ID (ví dụ: HCM_U_022)."""
        return self.by_id.get(unit_id)

    def get_unit_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Tra cứu theo tên (hỗ trợ có dấu, không dấu, viết hoa/thường)."""
        norm = _normalize_str(name)
        return self.by_name_norm.get(norm)

    def is_valid_new_ward(self, ward_name: str) -> bool:
        """Kiểm tra tên phường/xã có thuộc 168 đơn vị chính thức theo NQ 1685 hay không."""
        if not ward_name:
            return False
        if ward_name in self.valid_ward_names:
            return True
        norm = _normalize_str(ward_name)
        return norm in self.by_name_norm

    def resolve_to_official_ward(self, ward_input: str, district_context: str = "") -> Optional[str]:
        """
        Quy đổi một tên phường/xã bất kỳ (kể cả tên cũ trước sáp nhập) về tên phường mới chính thức.
        Trả về: Tên phường chính thức (ví dụ: 'Phường Chánh Hưng') hoặc None nếu không tìm thấy.
        """
        if not ward_input:
            return None
        
        # 1. Nếu đã là tên chính thức mới
        if self.is_valid_new_ward(ward_input):
            unit = self.get_unit_by_name(ward_input)
            return unit["name"] if unit else ward_input

        norm_input = _normalize_str(ward_input)
        core_input = re.sub(r'^(phuong|xa|thi tran|p\.|x\.)\s*', '', norm_input).strip()
        norm_dist = _normalize_str(district_context)
        
        # 2. Tra cứu theo ngữ cảnh quận cũ (Chính xác tuyệt đối tránh trùng lặp giữa các quận)
        for dist_key, mapping in DISTRICT_OLD_TO_NEW.items():
            if dist_key in norm_dist:
                if core_input in mapping:
                    return mapping[core_input]
                if norm_input in mapping:
                    return mapping[norm_input]

        # 3. Tra cứu chung qua từ điển ánh xạ cũ -> mới
        if norm_input in self.old_to_new_map:
            return self.old_to_new_map[norm_input]
        if core_input in self.old_to_new_map:
            return self.old_to_new_map[core_input]

        return None

    def validate_dataset(self, hotspots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Kiểm tra toàn bộ danh sách điểm ngập:
        - Đếm số điểm đã chuẩn theo NQ 1685.
        - Liệt kê các điểm còn dùng tên phường cũ hoặc tên không hợp lệ kèm gợi ý chuẩn hóa.
        """
        valid_count = 0
        invalid_items = []
        for h in hotspots:
            hid = h.get("id", "unknown")
            ward = h.get("ward", "")
            street = h.get("street", "")
            district = h.get("district", "")
            if self.is_valid_new_ward(ward):
                valid_count += 1
            else:
                suggested = self.resolve_to_official_ward(ward, district)
                invalid_items.append({
                    "id": hid,
                    "street": street,
                    "current_ward": ward,
                    "district": district,
                    "suggested_new_ward": suggested
                })
        return {
            "total": len(hotspots),
            "valid_count": valid_count,
            "invalid_count": len(invalid_items),
            "invalid_items": invalid_items
        }

# Khởi tạo singleton instance tiện dụng cho import nhanh
RESOLVER = AdminResolver()
