from core.admin_resolver import RESOLVER
"""
core/gazetteer.py - Cơ sở tri thức địa lý ngập lụt Đại đô thị TP. Hồ Chí Minh
Hệ thống tự động phát hiện địa danh mới (Dynamic Location Discovery) & Tự động Geocoding từ OpenStreetMap:
1. Danh mục hạt nhân (Seed Curated Hotspots): Các điểm nóng trọng điểm được định vị sẵn chuẩn xác tim đường.
2. Bộ nhớ đệm tự học (Self-Learning Dynamic Cache): Tự động lưu trữ các tuyến đường mới được cào về.
3. OpenStreetMap Dynamic Geocoder: Tự động truy vấn tọa độ chuẩn tim đường cho bất kỳ tuyến đường nào
   chưa từng có trong cơ sở tri thức mà không cần thêm thủ công.
   Kiểm duyệt chất lượng nghiêm ngặt: Tuyệt đối không geocode từ vô nghĩa (tại, lội, này...) hoặc tỉnh ngoài (Thái Nguyên, Nghệ An...).
"""

import os
import re
import json
import urllib.request
import urllib.parse
import unicodedata
from typing import Optional, Dict, Any, List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CACHE_FILE = os.path.join(DATA_DIR, "gazetteer_dynamic_cache.json")
CSGT_FILE = os.path.join(DATA_DIR, "csgt_122_flood_hotspots.json")
ADMIN_UNITS_FILE = os.path.join(DATA_DIR, "hcmc_168_administrative_units.json")

def load_csgt_hotspots() -> List[Dict[str, Any]]:
    if os.path.exists(CSGT_FILE):
        try:
            with open(CSGT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

CSGT_HOTSPOTS: List[Dict[str, Any]] = load_csgt_hotspots()

def load_admin_hotspots() -> List[Dict[str, Any]]:
    """Tải động 168 đơn vị hành chính chuẩn hóa theo NQ 1685/NQ-UBTVQH15."""
    if os.path.exists(ADMIN_UNITS_FILE):
        try:
            with open(ADMIN_UNITS_FILE, "r", encoding="utf-8") as f:
                units = json.load(f)
            admin_spots = []
            for u in units:
                admin_spots.append({
                    "keywords": u.get("keywords", []),
                    "display_name": u["name"],
                    "ward": u["name"],
                    "administrative_unit": u["name"],
                    "district": u.get("region_cluster", "TP.HCM"),
                    "region": "TPHCM",
                    "lat": u["lat"],
                    "lon": u["lon"],
                    "heat_points": [[u["lat"], u["lon"]]],
                    "priority": 2,
                    "type": f"khu vực {u['name']} ({u.get('cluster_detail', 'ĐVHC mới')})",
                    "source": "admin_units_168",
                    "cause": "rain",
                    "cause_label": "Khu vực địa giới hành chính",
                    "clause": u.get("clause", "")
                })
            return admin_spots
        except Exception:
            return []
    return []

ADMIN_HOTSPOTS: List[Dict[str, Any]] = load_admin_hotspots()

DYNAMIC_CACHE: Dict[str, Dict[str, Any]] = {}
FAILED_DYNAMIC_CACHE = set()

def load_dynamic_cache():
    global DYNAMIC_CACHE
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                DYNAMIC_CACHE = json.load(f)
        except Exception:
            DYNAMIC_CACHE = {}

def save_dynamic_cache():
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(DYNAMIC_CACHE, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

load_dynamic_cache()

# =========================================================================
# DANH MỤC HẠT NHÂN (SEED HOTSPOTS) - ĐÃ ĐƯỢC ĐO CHUẨN XÁC TIM ĐƯỜNG THEO OPENSTREETMAP (HIGHWAY)
# =========================================================================
HOTSPOTS: List[Dict[str, Any]] = [
    {
        "keywords": ["nguyễn thị tuôi", "nguyen thi tuoi", "nguyenthituoi"],
        "display_name": "Đường Nguyễn Thị Tuôi",
        "street": "Đường Nguyễn Thị Tuôi",
        "ward": "Xã Vĩnh Lộc",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8232, "lon": 106.5836,
        "heat_points": [[10.8211, 106.5846], [10.8232, 106.5836], [10.8253, 106.5826]],
        "priority": 3,
        "type": "ngập sâu trục đường Nguyễn Thị Tuôi (Xã Vĩnh Lộc)"
    },
    {
        "keywords": ["phan văn hớn", "phan van hon", "phanvanhon"],
        "display_name": "Đường Phan Văn Hớn",
        "street": "Đường Phan Văn Hớn",
        "ward": "Phường Đông Hưng Thuận",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8486, "lon": 106.5892,
        "heat_points": [[10.8447, 106.6110], [10.8486, 106.5892], [10.8623, 106.5721]],
        "priority": 3,
        "type": "ngập sâu trục đường Phan Văn Hớn"
    },
    # --- CÁC TUYẾN ĐƯỜNG BỔ SUNG ĐỘC LẬP (KHÔNG GỘP CHÙM) ---
    {
        "keywords": ["lã xuân oai", "la xuan oai", "laxuanoai"],
        "display_name": "Đường Lã Xuân Oai",
        "street": "Đường Lã Xuân Oai",
        "ward": "Phường Tăng Nhơn Phú",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8415, "lon": 106.7930,
        "heat_points": [[10.8415, 106.7930], [10.8480, 106.7860]],
        "priority": 3,
        "type": "ngập sâu trục đường Lã Xuân Oai"
    },
    {
        "keywords": ["nguyễn duy trinh", "nguyen duy trinh", "nguyenduytrinh"],
        "display_name": "Đường Nguyễn Duy Trinh",
        "street": "Đường Nguyễn Duy Trinh",
        "ward": "Phường Long Trường",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7908, "lon": 106.7860,
        "heat_points": [[10.7908, 106.7860], [10.7930, 106.7920]],
        "priority": 3,
        "type": "ngập sâu trục đường Nguyễn Duy Trinh"
    },
    {
        "keywords": ["đồng đen", "dong den", "dongden"],
        "display_name": "Đường Đồng Đen",
        "street": "Đường Đồng Đen",
        "ward": "Phường Bảy Hiền",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7925, "lon": 106.6475,
        "heat_points": [[10.7925, 106.6475]],
        "priority": 3,
        "type": "ngập sâu trục đường Đồng Đen"
    },
    {
        "keywords": ["bàu cát", "bau cat", "baucat"],
        "display_name": "Đường Bàu Cát",
        "street": "Đường Bàu Cát",
        "ward": "Phường Bảy Hiền",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7910, "lon": 106.6450,
        "heat_points": [[10.7910, 106.6450]],
        "priority": 3,
        "type": "ngập sâu trục đường Bàu Cát"
    },
    {
        "keywords": ["lũy bán bích", "luy ban bich", "luybanbich"],
        "display_name": "Đường Lũy Bán Bích",
        "street": "Đường Lũy Bán Bích",
        "ward": "Phường Phú Thạnh",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7780, "lon": 106.6320,
        "heat_points": [[10.7780, 106.6320]],
        "priority": 3,
        "type": "ngập sâu trục đường Lũy Bán Bích"
    },
    {
        "keywords": ["âu cơ", "au co", "auco"],
        "display_name": "Đường Âu Cơ",
        "street": "Đường Âu Cơ",
        "ward": "Phường Phú Thạnh",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7830, "lon": 106.6450,
        "heat_points": [[10.7830, 106.6450]],
        "priority": 3,
        "type": "ngập sâu trục đường Âu Cơ"
    },
    {
        "keywords": ["nguyễn văn hưởng", "nguyen van huong", "nguyenvanhuong"],
        "display_name": "Đường Nguyễn Văn Hưởng",
        "street": "Đường Nguyễn Văn Hưởng",
        "ward": "Phường An Khánh",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8090, "lon": 106.7310,
        "heat_points": [[10.8090, 106.7310]],
        "priority": 3,
        "type": "triều cường sông Sài Gòn tràn đường Nguyễn Văn Hưởng"
    },
    {
        "keywords": ["nguyễn bình", "nguyen binh", "nguyenbinh"],
        "display_name": "Đường Nguyễn Bình",
        "street": "Đường Nguyễn Bình",
        "ward": "Xã Hiệp Phước",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.6650, "lon": 106.7220,
        "heat_points": [[10.6650, 106.7220]],
        "priority": 3,
        "type": "ngập triều dâng đường Nguyễn Bình"
    },
    {
        "keywords": ["nguyễn ảnh thủ", "nguyen anh thu", "nguyenanhthu"],
        "display_name": "Đường Nguyễn Ảnh Thủ",
        "street": "Đường Nguyễn Ảnh Thủ",
        "ward": "Xã Bà Điểm",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8614, "lon": 106.6112,
        "heat_points": [[10.8614, 106.6112], [10.8570, 106.6080], [10.8660, 106.6150]],
        "priority": 3,
        "type": "ngập sâu trục đường Nguyễn Ảnh Thủ (giao Song Hành QL22)"
    },

    # --- CÁC ĐIỂM NÓNG BỔ SUNG TĂNG ĐỘ PHỦ THEO THỰC TẾ NGẬP LỤT TP.HCM ---
    {
        "keywords": ["tân kỳ tân quý", "tan ky tan quy", "tankytanquy", "cầu xéo", "cauxeo", "ngã tư gò mây", "gò mây"],
        "display_name": "Đường Tân Kỳ Tân Quý",
        "ward": "Phường Tân Sơn Nhì",
        "district": "Quận Tân Phú",
        "region": "TPHCM",
        "lat": 10.8025, "lon": 106.6275,
        "heat_points": [[10.8025, 106.6275], [10.8010, 106.6340], [10.8080, 106.6150]],
        "priority": 3,
        "type": "ngập sâu trục Tân Kỳ Tân Quý"
    },
    {
        "keywords": ["nguyễn hữu cảnh", "nguyen huu canh", "nguyenhuucanh", "chân cầu thủ thiêm", "cầu thủ thiêm 1"],
        "display_name": "Đường Nguyễn Hữu Cảnh",
        "ward": "Phường Thạnh Mỹ Tây",
        "district": "Quận Bình Thạnh",
        "region": "TPHCM",
        "lat": 10.7930, "lon": 106.7180,
        "heat_points": [[10.7930, 106.7180], [10.7910, 106.7120]],
        "priority": 3,
        "type": "rốn ngập Nguyễn Hữu Cảnh"
    },
    {
        "keywords": ["nguyễn văn quá", "nguyen van qua", "nguyenvanqua", "cầu tham lương", "tham lương"],
        "display_name": "Đường Nguyễn Văn Quá",
        "ward": "Phường Đông Hưng Thuận",
        "district": "Quận 12",
        "region": "TPHCM",
        "lat": 10.8350, "lon": 106.6280,
        "heat_points": [[10.8350, 106.6280], [10.8400, 106.6200]],
        "priority": 3,
        "type": "rốn ngập sâu Quận 12 Nguyễn Văn Quá"
    },
    {
        "keywords": ["đỗ xuân hợp", "do xuan hop", "doxuanhop"],
        "display_name": "Đường Đỗ Xuân Hợp",
        "ward": "Phường Phước Long",
        "district": "TP. Thủ Đức",
        "region": "TPHCM",
        "lat": 10.8220, "lon": 106.7720,
        "heat_points": [[10.8220, 106.7720]],
        "priority": 3,
        "type": "ngập sâu Đỗ Xuân Hợp"
    },
    {
        "keywords": ["lê văn việt", "le van viet", "levanviet"],
        "display_name": "Đường Lê Văn Việt",
        "ward": "Phường Tăng Nhơn Phú",
        "district": "TP. Thủ Đức",
        "region": "TPHCM",
        "lat": 10.8480, "lon": 106.7860,
        "heat_points": [[10.8480, 106.7860]],
        "priority": 3,
        "type": "ngập tràn đường Lê Văn Việt"
    },
            # =========================================================================
    # CÁC ĐIỂM NÓNG BÌNH DƯƠNG (BÌNH DƯƠNG CŨ - TP.HCM MỚI NQ 1685)
    # =========================================================================
    {
        "keywords": ["đại lộ bình dương", "dai lo binh duong", "ql13 bình dương", "quốc lộ 13 bình dương"],
        "display_name": "Đại lộ Bình Dương",
        "street": "Đại lộ Bình Dương",
        "ward": "Phường Thủ Dầu Một",
        "district": "Bình Dương",
        "region": "Bình Dương cũ",
        "lat": 10.9805, "lon": 106.6745,
        "heat_points": [[10.9805, 106.6745]],
        "priority": 3,
        "type": "ngập trục huyết mạch Đại lộ Bình Dương"
    },
    {
        "keywords": ["thích quảng đức thủ dầu một", "thich quang duc", "ngã tư gò đậu", "nga tu go dau"],
        "display_name": "Khu vực Thích Quảng Đức (Thủ Dầu Một)",
        "street": "Đường Thích Quảng Đức",
        "ward": "Phường Thủ Dầu Một",
        "district": "Bình Dương",
        "region": "Bình Dương cũ",
        "lat": 10.9752, "lon": 106.6681,
        "heat_points": [[10.9752, 106.6681]],
        "priority": 3,
        "type": "rốn ngập Thủ Dầu Một"
    },
    {
        "keywords": ["ngã tư 550", "nga tu 550", "cầu ông bố", "cau ong bo", "đường 22 tháng 12", "đường 22/12", "lái thiêu", "lai thieu"],
        "display_name": "Khu vực Ngã tư 550 - Cầu Ông Bố (Thuận An)",
        "street": "Khu vực Ngã tư 550",
        "ward": "Phường Thuận An",
        "district": "Bình Dương",
        "region": "Bình Dương cũ",
        "lat": 10.9080, "lon": 106.7020,
        "heat_points": [[10.9080, 106.7020]],
        "priority": 3,
        "type": "điểm ngập sâu Thuận An"
    },
    {
        "keywords": ["sóng thần", "song than", "cầu vượt sóng thần", "quốc lộ 1k dĩ an", "ql1k dĩ an", "ngã ba cây điệp", "nga ba cay diep"],
        "display_name": "Khu vực Sóng Thần - Quốc lộ 1K (Dĩ An)",
        "street": "Khu vực Sóng Thần",
        "ward": "Phường Dĩ An",
        "district": "Bình Dương",
        "region": "Bình Dương cũ",
        "lat": 10.8920, "lon": 106.7450,
        "heat_points": [[10.8920, 106.7450]],
        "priority": 3,
        "type": "điểm ngập Dĩ An"
    },
    # =========================================================================
    # CÁC ĐIỂM NÓNG BÀ RỊA - VŨNG TÀU (BÀ RỊA - VŨNG TÀU CŨ - TP.HCM MỚI NQ 1685)
    # =========================================================================
    {
        "keywords": ["đường hạ long vũng tàu", "hạ long vũng tàu", "thùy vân", "thuy van", "bãi sau vũng tàu", "bãi trước vũng tàu"],
        "display_name": "Khu vực Bãi Sau - Thùy Vân (Vũng Tàu)",
        "street": "Đường Thùy Vân",
        "ward": "Phường Vũng Tàu",
        "district": "Bà Rịa - Vũng Tàu",
        "region": "Bà Rịa - Vũng Tàu cũ",
        "lat": 10.3450, "lon": 107.0850,
        "heat_points": [[10.3450, 107.0850]],
        "priority": 3,
        "type": "ngập triều cường ven biển Vũng Tàu"
    },
    {
        "keywords": ["lê hồng phong vũng tàu", "nguyễn an ninh vũng tàu", "bến đình", "ben dinh"],
        "display_name": "Khu vực Lê Hồng Phong - Nguyễn An Ninh (Vũng Tàu)",
        "street": "Đường Lê Hồng Phong",
        "ward": "Phường Vũng Tàu",
        "district": "Bà Rịa - Vũng Tàu",
        "region": "Bà Rịa - Vũng Tàu cũ",
        "lat": 10.3580, "lon": 107.0910,
        "heat_points": [[10.3580, 107.0910]],
        "priority": 3,
        "type": "ngập đô thị TP. Vũng Tàu"
    },
    {
        "keywords": ["quốc lộ 51 phú mỹ", "ql51 phú mỹ", "thị xã phú mỹ", "phú mỹ vũng tàu"],
        "display_name": "Khu vực Quốc lộ 51 (Phú Mỹ)",
        "street": "Quốc lộ 51",
        "ward": "Thị xã Phú Mỹ",
        "district": "Bà Rịa - Vũng Tàu",
        "region": "Bà Rịa - Vũng Tàu cũ",
        "lat": 10.5910, "lon": 107.0540,
        "heat_points": [[10.5910, 107.0540]],
        "priority": 3,
        "type": "ngập cục bộ Quốc lộ 51 Phú Mỹ"
    },
{
        "keywords": ["ga đại học quốc gia", "ga dai hoc quoc gia", "đại học quốc gia", "dai hoc quoc gia"],
        "display_name": "Ga Đại Học Quốc Gia (Thủ Đức)",
        "street": "Ga Đại Học Quốc Gia",
        "ward": "Phường Linh Trung",
        "district": "TP. Thủ Đức",
        "region": "TPHCM",
        "lat": 10.8753, "lon": 106.8007,
        "heat_points": [[10.8753, 106.8007]],
        "priority": 3,
        "type": "khu vực Ga Đại Học Quốc Gia"
    },
{
        "keywords": ["chợ thủ đức", "cho thu duc", "dương văn cam", "duong van cam", "đặng thị rành", "dang thi ranh"],
        "display_name": "Khu vực Chợ Thủ Đức (Dương Văn Cam)",
        "ward": "Phường Linh Xuân",
        "district": "TP. Thủ Đức",
        "region": "TPHCM",
        "lat": 10.8520, "lon": 106.7580,
        "heat_points": [[10.8520, 106.7580]],
        "priority": 3,
        "type": "rốn ngập Chợ Thủ Đức nước chảy xiết"
    },
    {
        "keywords": ["trần não", "tran nao", "trannao"],
        "display_name": "Đường Trần Não",
        "street": "Đường Trần Não",
        "ward": "Phường An Khánh",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7920, "lon": 106.7320,
        "heat_points": [[10.7920, 106.7320]],
        "priority": 3,
        "type": "ngập triều bờ sông Sài Gòn Đường Trần Não"
    },
    {
        "keywords": ["ngã tư hàng xanh", "nga tu hang xanh", "hàng xanh", "hang xanh"],
        "display_name": "Ngã tư Hàng Xanh",
        "street": "Ngã tư Hàng Xanh",
        "ward": "Phường Bình Thạnh",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8015, "lon": 106.7115,
        "heat_points": [[10.8015, 106.7115]],
        "priority": 3,
        "type": "ngập sâu nút giao Hàng Xanh"
    },
    {
        "keywords": ["xô viết nghệ tĩnh", "xo viet nghe tinh", "xovietnghetinh"],
        "display_name": "Đường Xô Viết Nghệ Tĩnh",
        "street": "Đường Xô Viết Nghệ Tĩnh",
        "ward": "Phường Bình Thạnh",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8038, "lon": 106.7126,
        "heat_points": [[10.8038, 106.7126], [10.8015, 106.7115]],
        "priority": 3,
        "type": "ngập sâu trục Xô Viết Nghệ Tĩnh"
    },
    {
        "keywords": ["thanh đa", "thanhda", "bình quới", "binh quoi", "bán đảo thanh đa"],
        "display_name": "Đường Bình Quới",
        "ward": "Phường Bình Quới",
        "district": "Quận Bình Thạnh",
        "region": "TPHCM",
        "lat": 10.8250, "lon": 106.7350,
        "heat_points": [[10.8250, 106.7350]],
        "priority": 3,
        "type": "triều cường vỡ bờ bao Thanh Đa"
    },
    # --- CÁC ĐIỂM NÓNG BỔ SUNG TỪ THỰC TẾ NGẬP LỤT ĐÔ THỊ ---
    {
        "keywords": ["pouyuen", "pou yuen", "pou chen", "công ty pouyuen", "cty pouyuen"],
        "display_name": "Khu vực Công ty PouYuen (Bình Tân)",
        "ward": "Phường Tân Tạo",
        "district": "Quận Bình Tân",
        "region": "TPHCM",
        "lat": 10.7490, "lon": 106.5980,
        "heat_points": [[10.7490, 106.5980], [10.7510, 106.6020]],
        "priority": 3,
        "type": "ngập sâu điểm nóng công nhân PouYuen"
    },
    {
        "keywords": ["kdc vĩnh lộc", "kdc vinh loc", "khu dân cư vĩnh lộc"],
        "display_name": "Khu dân cư Vĩnh Lộc",
        "ward": "Phường Bình Tân",
        "district": "Quận Bình Tân",
        "region": "TPHCM",
        "lat": 10.8060, "lon": 106.5890,
        "heat_points": [[10.8060, 106.5890]],
        "priority": 3,
        "type": "ngập sâu khu dân cư Vĩnh Lộc"
    },
    {
        "keywords": ["chợ bình tân", "cho binh tan"],
        "display_name": "Khu vực Chợ Bình Tân",
        "ward": "Phường An Lạc",
        "district": "Quận Bình Tân",
        "region": "TPHCM",
        "lat": 10.7520, "lon": 106.6190,
        "heat_points": [[10.7520, 106.6190]],
        "priority": 3,
        "type": "ngập úng khu thương mại Chợ Bình Tân"
    },
    {
        "keywords": ["tân cảng", "tan cang", "cầu sài gòn tân cảng"],
        "display_name": "Khu vực Tân Cảng",
        "ward": "Phường Thạnh Mỹ Tây",
        "district": "Quận Bình Thạnh",
        "region": "TPHCM",
        "lat": 10.7960, "lon": 106.7210,
        "heat_points": [[10.7960, 106.7210]],
        "priority": 3,
        "type": "triều cường sông Sài Gòn khu Tân Cảng"
    },

    # --- CÁC TUYẾN ĐƯỜNG TRỌNG ĐIỂM NGẬP TẠI TP.HCM (CHUẨN TIM ĐƯỜNG OSM) ---
    {
        "keywords": ["bùi viện", "bui vien", "buivien", "phố tây bùi viện"],
        "display_name": "Đường Bùi Viện",
        "ward": "Phường Bến Thành",
        "district": "Quận 1",
        "region": "TPHCM",
        "lat": 10.7676, "lon": 106.6944,
        "heat_points": [[10.7657, 106.6908], [10.7668, 106.6927], [10.7676, 106.6944]],
        "type": "ngập trũng đô thị trung tâm"
    },
    {
        "keywords": ["trần hưng đạo", "tran hung dao", "tranhungdao"],
        "display_name": "Đường Trần Hưng Đạo",
        "ward": "Phường Cầu Ông Lãnh",
        "district": "Quận 1",
        "region": "TPHCM",
        "lat": 10.7599, "lon": 106.6883,
        "heat_points": [[10.7599, 106.6883], [10.7628, 106.6908], [10.7662, 106.6939]],
        "type": "ngập úng giao lộ trung tâm"
    },
    {
        "keywords": ["calmette", "nguyễn thái bình", "nguyen thai binh"],
        "display_name": "Đường Calmette",
        "ward": "Phường Sài Gòn",
        "district": "Quận 1",
        "region": "TPHCM",
        "lat": 10.7689, "lon": 106.6985,
        "heat_points": [[10.7665, 106.7002], [10.7689, 106.6985]],
        "type": "ngập cục bộ ven kênh Bến Nghé"
    },
    {
        "keywords": ["phạm thế hiển", "pham the hien", "phamthehien"],
        "display_name": "Đường Phạm Thế Hiển",
        "ward": "Phường Chánh Hưng",
        "district": "Quận 8",
        "region": "TPHCM",
        "lat": 10.7480, "lon": 106.6810,
        "heat_points": [[10.7440, 106.6731], [10.7480, 106.6810], [10.7505, 106.6865]],
        "type": "triều cường bờ kè Kênh Đôi"
    },
    {
        "keywords": ["rạch cùng", "rach cung", "bến bình đông", "tuyến đường bến bình đông"],
        "display_name": "Tuyến đường Bến Bình Đông (Rạch Cùng)",
        "ward": "Phường Bình Đông",
        "district": "Quận 8",
        "region": "TPHCM",
        "lat": 10.7413, "lon": 106.6473,
        "heat_points": [[10.7380, 106.6420], [10.7413, 106.6473], [10.7460, 106.6550]],
        "type": "ngập sâu triều dâng bến Bình Đông"
    },
    {
        "keywords": ["bạch đằng", "bach dang", "bachdang"],
        "display_name": "Đường Bạch Đằng",
        "ward": "Phường Bình Thạnh",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8033, "lon": 106.7056,
        "heat_points": [[10.8015, 106.7030], [10.8033, 106.7056], [10.8055, 106.7090]],
        "type": "ngập sâu chợ Bà Chiểu"
    },
    {
        "keywords": ["thanh đa", "thanhda", "bình quới", "binh quoi", "binhquoi"],
        "display_name": "Đường Bình Quới",
        "ward": "Phường Bình Quới",
        "district": "Quận Bình Thạnh",
        "region": "TPHCM",
        "lat": 10.8234, "lon": 106.7320,
        "heat_points": [[10.8180, 106.7194], [10.8234, 106.7320]],
        "type": "triều cường sông Sài Gòn tràn bờ bao"
    },
    {
        "keywords": ["ung văn khiêm", "ung van khiem", "ungvankhiem"],
        "display_name": "Đường Ung Văn Khiêm",
        "ward": "Phường Thạnh Mỹ Tây",
        "district": "Quận Bình Thạnh",
        "region": "TPHCM",
        "lat": 10.8066, "lon": 106.7198,
        "heat_points": [[10.8029, 106.7222], [10.8066, 106.7198], [10.8096, 106.7130]],
        "type": "ngập triều rạch Văn Thánh"
    },
    {
        "keywords": ["nguyễn xí", "nguyen xi", "nguyenxi", "cầu đỏ"],
        "display_name": "Đường Nguyễn Xí",
        "ward": "Phường Bình Thạnh",
        "district": "Quận Bình Thạnh",
        "region": "TPHCM",
        "lat": 10.8150, "lon": 106.7080,
        "heat_points": [[10.8118, 106.7109], [10.8150, 106.7080]],
        "type": "ngập trũng cống rãnh"
    },
    {
        "keywords": ["đinh bộ lĩnh", "dinh bo linh", "dinhbolinh", "bx miền đông", "bến xe miền đông"],
        "display_name": "Đường Đinh Bộ Lĩnh",
        "ward": "Phường Bình Thạnh",
        "district": "Quận Bình Thạnh",
        "region": "TPHCM",
        "lat": 10.8151, "lon": 106.7104,
        "heat_points": [[10.8142, 106.7122], [10.8151, 106.7104]],
        "type": "ngập dồn nội đô kẹt xe"
    },
    {
        "keywords": ["cầu sài gòn", "cau sai gon", "causaigon"],
        "display_name": "Khu vực Cầu Sài Gòn",
        "ward": "Phường Thạnh Mỹ Tây",
        "district": "Quận Bình Thạnh",
        "region": "TPHCM",
        "lat": 10.7989, "lon": 106.7272,
        "heat_points": [[10.7989, 106.7272]],
        "type": "ngập chân cầu kẹt xe tê liệt"
    },
    {
        "keywords": ["phan huy ích", "phan huy ich", "phanhuyich"],
        "display_name": "Đường Phan Huy Ích",
        "ward": "Phường An Hội Tây",
        "district": "Quận Gò Vấp",
        "region": "TPHCM",
        "lat": 10.8372, "lon": 106.6362,
        "heat_points": [[10.8270, 106.6280], [10.8372, 106.6362], [10.8465, 106.6433]],
        "type": "ngập nước mưa kéo dài"
    },
    {
        "keywords": ["phạm văn đồng", "pham van dong", "phamvandong"],
        "display_name": "Đại lộ Phạm Văn Đồng",
        "street": "Đại lộ Phạm Văn Đồng",
        "ward": "Phường Hạnh Thông",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8208, "lon": 106.6950,
        "heat_points": [[10.8188, 106.6879], [10.8208, 106.6950], [10.8354, 106.7298]],
        "heat_points": [[10.8188, 106.6879], [10.8245, 106.6950], [10.8354, 106.7298]],
        "type": "ngập tràn làn xe máy"
    },
    {
        "keywords": ["võ văn ngân", "vo van ngan", "vovanngan"],
        "display_name": "Đường Võ Văn Ngân",
        "ward": "Phường Thủ Đức",
        "district": "TP. Thủ Đức",
        "region": "TPHCM",
        "lat": 10.8505, "lon": 106.7664,
        "heat_points": [[10.8465, 106.7580], [10.8505, 106.7664], [10.8540, 106.7725]],
        "type": "dốc nước chảy xiết"
    },
    {
        "keywords": ["chợ thủ đức", "cho thu duc", "chothuduc"],
        "display_name": "Khu vực Chợ Thủ Đức",
        "ward": "Phường Linh Xuân",
        "district": "TP. Thủ Đức",
        "region": "TPHCM",
        "lat": 10.8503, "lon": 106.7541,
        "heat_points": [[10.8503, 106.7541]],
        "type": "rốn ngập trũng thấp"
    },
    {
        "keywords": ["tô ngọc vân", "to ngoc van", "tongocvan"],
        "display_name": "Đường Tô Ngọc Vân",
        "ward": "Phường Tam Bình",
        "district": "TP. Thủ Đức",
        "region": "TPHCM",
        "lat": 10.8540, "lon": 106.7510,
        "heat_points": [[10.8540, 106.7510], [10.8610, 106.7455]],
        "type": "trũng ray xe lửa"
    },
    {
        "keywords": ["kha vạn cân", "kha van can", "khavancan"],
        "display_name": "Đường Kha Vạn Cân",
        "ward": "Phường Thủ Đức",
        "district": "TP. Thủ Đức",
        "region": "TPHCM",
        "lat": 10.8453, "lon": 106.7500,
        "heat_points": [[10.8350, 106.7380], [10.8453, 106.7500]],
        "type": "ngập cục bộ ven rạch"
    },
    {
        "keywords": ["quốc hương", "quoc huong", "quochuong"],
        "display_name": "Đường Quốc Hương",
        "ward": "Phường An Khánh",
        "district": "TP. Thủ Đức",
        "region": "TPHCM",
        "lat": 10.8028, "lon": 106.7324,
        "heat_points": [[10.8028, 106.7324], [10.8074, 106.7309]],
        "type": "triều cường sông Sài Gòn"
    },
    {
        "keywords": ["lương định của", "luong dinh cua", "luongdinhcua"],
        "display_name": "Đường Lương Định Của",
        "ward": "Phường An Khánh",
        "district": "TP. Thủ Đức",
        "region": "TPHCM",
        "lat": 10.7839, "lon": 106.7272,
        "heat_points": [[10.7839, 106.7272], [10.7880, 106.7348]],
        "type": "ngập công trình thi công"
    },
    {
        "keywords": ["hầm chui an phú", "ham chui an phu", "nút giao an phú", "nut giao an phu"],
        "display_name": "Hầm chui Nút giao An Phú",
        "ward": "Phường An Khánh",
        "district": "TP. Thủ Đức",
        "region": "TPHCM",
        "lat": 10.7910, "lon": 106.7514,
        "heat_points": [[10.7910, 106.7514]],
        "type": "ngập hầm chui ngập sâu quá tải máy bơm"
    },
    {
        "keywords": ["cầu ba son", "cau ba son", "ba son", "chân cầu ba son", "chan cau ba son", "cầu thủ thiêm 2", "cau thu thiem 2", "đường r12", "duong r12", "đường r12 - chân cầu ba son"],
        "display_name": "Cầu Ba Son",
        "street": "Cầu Ba Son",
        "ward": "Phường An Khánh",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7788, "lon": 106.7115,
        "heat_points": [[10.7788, 106.7115], [10.7775, 106.7130]],
        "priority": 3,
        "type": "ngập triều khu vực chân cầu Ba Son (Thủ Thiêm)"
    },
    {
        "keywords": ["thủ thiêm", "thu thiem", "cây bàng", "cay bang"],
        "display_name": "Đường Cây Bàng",
        "ward": "Phường An Khánh",
        "district": "TP. Thủ Đức",
        "region": "TPHCM",
        "lat": 10.7704, "lon": 106.7101,
        "heat_points": [[10.7704, 106.7101]],
        "type": "ngập triều bờ sông Sài Gòn"
    },
    {
        "keywords": ["trần xuân soạn", "tran xuan soan", "tranxuansoan"],
        "display_name": "Đường Trần Xuân Soạn",
        "ward": "Phường Tân Hưng",
        "district": "Quận 7",
        "region": "TPHCM",
        "lat": 10.7518, "lon": 106.7125,
        "heat_points": [[10.7517, 106.6985], [10.7518, 106.7125], [10.7568, 106.7217]],
        "type": "triều cường bờ kè Kênh Tẻ"
    },
    {
        "keywords": ["huỳnh tấn phát", "huynh tan phat", "huynhtanphat"],
        "display_name": "Đường Huỳnh Tấn Phát",
        "ward": "Phường Phú Thuận",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7342, "lon": 106.7305,
        "heat_points": [[10.7342, 106.7305], [10.7480, 106.7289], [10.7241, 106.7335]],
        "type": "triều cường sông Nhà Bè",
        "priority": 3,
        "street": "Đường Huỳnh Tấn Phát"
    },
    {
        "keywords": ["lê văn lương", "le van luong", "levanluong", "cầu rạch đỉa"],
        "display_name": "Đường Lê Văn Lương",
        "ward": "Phường Tân Hưng",
        "district": "Quận 7",
        "region": "TPHCM",
        "lat": 10.7350, "lon": 106.7020,
        "heat_points": [[10.7280, 106.7022], [10.7350, 106.7020]],
        "type": "ngập sâu qua các cầu sắt"
    },
    {
        "keywords": ["nguyễn thị thập", "nguyen thi thap", "nguyenthithap"],
        "display_name": "Đường Nguyễn Thị Thập",
        "ward": "Phường Tân Phú",
        "district": "Quận 7",
        "region": "TPHCM",
        "lat": 10.7383, "lon": 106.7170,
        "heat_points": [[10.7397, 106.7053], [10.7383, 106.7170]],
        "type": "ngập úng triều cường dâng cao"
    },
    {
        "keywords": ["phạm hữu lầu", "pham huu lau", "phamhuulau"],
        "display_name": "Đường Phạm Hữu Lầu",
        "street": "Đường Phạm Hữu Lầu",
        "ward": "Phường Phú Mỹ",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.70408, "lon": 106.72863,
        "heat_points": [[10.70408, 106.72863], [10.70552, 106.73766], [10.70312, 106.72573]],
        "priority": 3,
        "type": "ngập tràn tim đường Phạm Hữu Lầu (từ Huỳnh Tấn Phát đến Cầu Phước Long)"
    },
    {
        "keywords": ["tân quy", "tan quy", "lotte quận 7", "lotte quan 7"],
        "display_name": "Khu dân cư Tân Quy",
        "ward": "Phường Tân Hưng",
        "district": "Quận 7",
        "region": "TPHCM",
        "lat": 10.7420, "lon": 106.7080,
        "heat_points": [[10.7420, 106.7080]],
        "type": "ngập cục bộ khu dân cư"
    },
    {
        "keywords": ["hiệp phước", "hiep phuoc", "hiepphuoc"],
        "display_name": "Khu vực Hiệp Phước (Nhà Bè)",
        "ward": "Xã Hiệp Phước",
        "priority": 2,
        "district": "Huyện Nhà Bè",
        "region": "TPHCM",
        "lat": 10.6664, "lon": 106.7203,
        "heat_points": [[10.6664, 106.7203]],
        "type": "triều cường vùng trũng ven sông Soài Rạp"
    },
    {
        "keywords": ["liên khu 4-5", "lien khu 4-5", "lk 4-5", "lienkhu45"],
        "display_name": "Đường Liên Khu 4-5",
        "ward": "Phường Bình Tân",
        "district": "Quận Bình Tân",
        "region": "TPHCM",
        "lat": 10.7982, "lon": 106.5921,
        "heat_points": [[10.7930, 106.5890], [10.7982, 106.5921]],
        "type": "ngập sâu trũng thấp ngoại ô"
    },
    {
        "keywords": ["mã lò", "ma lo", "malo"],
        "display_name": "Đường Mã Lò",
        "ward": "Phường Bình Hưng Hòa",
        "district": "Quận Bình Tân",
        "region": "TPHCM",
        "lat": 10.7764, "lon": 106.6009,
        "heat_points": [[10.7821, 106.5993], [10.7764, 106.6009], [10.7713, 106.6022], [10.7657, 106.6041]],
        "type": "ngập sâu nước ngập tắt máy xe"
    },
    {
        "keywords": ["hương lộ 2", "huong lo 2", "hl2", "hl 2"],
        "display_name": "Đường Hương Lộ 2",
        "ward": "Phường Bình Trị Đông",
        "district": "Quận Bình Tân",
        "region": "TPHCM",
        "lat": 10.7657, "lon": 106.6012,
        "heat_points": [[10.7677, 106.5964], [10.7657, 106.6012], [10.7652, 106.6037]],
        "type": "ngập sâu xe máy không về được nhà"
    },
    {
        "keywords": ["kinh dương vương", "kinh duong vuong", "kinhduongvuong", "bến xe miền tây"],
        "display_name": "Đường Kinh Dương Vương",
        "ward": "Phường An Lạc",
        "district": "Quận Bình Tân",
        "region": "TPHCM",
        "lat": 10.7480, "lon": 106.6180,
        "heat_points": [[10.7450, 106.6210], [10.7480, 106.6180], [10.7520, 106.6140]],
        "priority": 3,
        "type": "rốn ngập cửa ngõ Tây TP.HCM"
    },
    {
        "keywords": ["tên lửa", "ten lua", "tenlua"],
        "display_name": "Đường Tên Lửa",
        "ward": "Phường An Lạc",
        "district": "Quận Bình Tân",
        "region": "TPHCM",
        "lat": 10.7550, "lon": 106.6100,
        "heat_points": [[10.7498, 106.6112], [10.7550, 106.6100]],
        "priority": 3,
        "type": "ngập cục bộ khu dân cư Tên Lửa"
    },
    {
        "keywords": ["bà triệu hóc môn", "đường bà triệu", "bà triệu", "ba trieu", "bv hóc môn"],
        "display_name": "Đường Bà Triệu",
        "ward": "Xã Hóc Môn",
        "district": "Huyện Hóc Môn",
        "region": "TPHCM",
        "lat": 10.8848, "lon": 106.5951,
        "heat_points": [[10.8810, 106.6010], [10.8848, 106.5951]],
        "type": "ngập sâu khu vực bệnh viện Hóc Môn"
    },
    {
        "keywords": ["lý thường kiệt hóc môn", "ly thuong kiet hoc mon"],
        "display_name": "Đường Lý Thường Kiệt (Hóc Môn)",
        "ward": "Xã Hóc Môn",
        "district": "Huyện Hóc Môn",
        "region": "TPHCM",
        "lat": 10.8870, "lon": 106.5906,
        "heat_points": [[10.8870, 106.5906]],
        "type": "ngập đường thị trấn Hóc Môn"
    },
    {
        "keywords": ["cộng hòa", "cong hoa", "conghoa"],
        "display_name": "Đường Cộng Hòa",
        "ward": "Phường Tân Bình",
        "district": "Quận Tân Bình",
        "region": "TPHCM",
        "lat": 10.8024, "lon": 106.6412,
        "heat_points": [[10.8024, 106.6412], [10.8050, 106.6370]],
        "type": "ngập bùn đất và nước mưa kéo dài"
    },
    {
        "keywords": ["thoại ngọc hầu", "thoai ngoc hau", "thoaingochau"],
        "display_name": "Đường Thoại Ngọc Hầu",
        "ward": "Phường Phú Thạnh",
        "district": "Quận Tân Phú",
        "region": "TPHCM",
        "lat": 10.7854, "lon": 106.6409,
        "heat_points": [[10.7763, 106.6262], [10.7854, 106.6409]],
        "type": "ngập trũng cống thoát chậm"
    },
    {
        "keywords": ["vườn lài", "vuon lai", "vuonlai"],
        "display_name": "Đường Vườn Lài",
        "ward": "Phường An Phú Đông",
        "district": "Quận 12",
        "region": "TPHCM",
        "lat": 10.8399, "lon": 106.6955,
        "heat_points": [[10.8399, 106.6955], [10.8492, 106.6912]],
        "type": "ngập bờ bao An Phú Đông"
    },
    {
        "keywords": ["quốc lộ 50", "quoc lo 50", "ql 50", "ql50"],
        "display_name": "Quốc lộ 50",
        "street": "Quốc lộ 50",
        "ward": "Xã Bình Hưng",
        "priority": 3,
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7275, "lon": 106.6560,
        "heat_points": [[10.7275, 106.6560], [10.7304, 106.6560], [10.7240, 106.6560]],
        "heat_points": [[10.7100, 106.6630], [10.7180, 106.6620]],
        "type": "ngập triều kết hợp mưa lũ"
    },

    # --- PHƯỜNG MỚI TP. THỦ ĐỨC SAU SÁP NHẬP ---
    {
        # Phường Phước Long (Sáp nhập Phước Long A + Phước Long B + Phước Bình)
        "keywords": [
            "phường phước long", "phuong phuoc long", "phước long", "phuoc long",
            "phước long a", "phuoc long a", "phước long b", "phuoc long b",
            "phước bình", "phuoc binh", "p. phước long"
        ],
        "display_name": "Khu vực Phường Phước Long",
        "ward": "Phường Phước Long",
        "priority": 2,
        "district": "TP. Thủ Đức",
        "region": "TPHCM",
        "lat": 10.8200, "lon": 106.7700,
        "heat_points": [[10.8200, 106.7700]],
        "type": "ngập diện rộng khu vực Phước Long"
    },

    # --- CÁC ĐIỂM NÓNG THEO QUẬN/HUYỆN CỤ THỂ TRONG TP.HCM ---
    {
        "keywords": ["quận 7", "quan 7", "quan7"],
        "display_name": "Khu vực Quận 7",
        "priority": 1,
        "ward": "Phường Tân Hưng",
        "district": "Quận 7",
        "region": "TPHCM",
        "lat": 10.7450, "lon": 106.7150,
        "heat_points": [[10.7450, 106.7150]],
        "type": "triều cường dâng cao Nam Sài Gòn"
    },

    {
        "keywords": ["gò vấp", "go vap", "govap"],
        "display_name": "Khu vực Quận Gò Vấp",
        "priority": 1,
        "ward": "Phường Gò Vấp",
        "district": "Quận Gò Vấp",
        "region": "TPHCM",
        "lat": 10.8385, "lon": 106.6650,
        "heat_points": [[10.8385, 106.6650]],
        "type": "ngập úng mưa to Gò Vấp"
    },
    {
        "keywords": ["thủ đức", "thu duc", "thuduc"],
        "display_name": "Khu vực TP. Thủ Đức",
        "priority": 1,
        "ward": "Phường Thủ Đức",
        "district": "TP. Thủ Đức",
        "region": "TPHCM",
        "lat": 10.8500, "lon": 106.7600,
        "heat_points": [[10.8500, 106.7600]],
        "type": "ngập diện rộng Thủ Đức"
    },
    {
        "keywords": ["bình thạnh", "binh thanh", "binhthanh"],
        "display_name": "Khu vực Phường Bình Thạnh",
        "priority": 1,
        "ward": "Phường Bình Thạnh",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8050, "lon": 106.7050,
        "heat_points": [[10.8050, 106.7050]],
        "type": "ngập triều vùng trũng kênh rạch"
    },
    {
        "keywords": ["bình tân", "binh tan", "binhtan"],
        "display_name": "Khu vực Quận Bình Tân",
        "priority": 1,
        "ward": "Phường An Lạc",
        "district": "Quận Bình Tân",
        "region": "TPHCM",
        "lat": 10.7500, "lon": 106.6000,
        "heat_points": [[10.7500, 106.6000]],
        "type": "ngập diện rộng Bình Tân"
    },
    {
        "keywords": ["tân phú", "tan phu", "tanphu"],
        "display_name": "Khu vực Quận Tân Phú",
        "priority": 1,
        "ward": "Phường Phú Thạnh",
        "district": "Quận Tân Phú",
        "region": "TPHCM",
        "lat": 10.7850, "lon": 106.6350,
        "heat_points": [[10.7850, 106.6350]],
        "type": "ngập diện rộng Tân Phú"
    },
    {
        "keywords": ["tân bình", "tan binh", "tanbinh"],
        "display_name": "Khu vực Quận Tân Bình",
        "priority": 1,
        "ward": "Phường Bảy Hiền",
        "district": "Quận Tân Bình",
        "region": "TPHCM",
        "lat": 10.7990, "lon": 106.6520,
        "heat_points": [[10.7990, 106.6520]],
        "type": "ngập đường nội đô Tân Bình"
    },
    {
        "keywords": ["quận 8", "quan 8", "quan8"],
        "display_name": "Khu vực Quận 8",
        "priority": 1,
        "ward": "Phường Chánh Hưng",
        "district": "Quận 8",
        "region": "TPHCM",
        "lat": 10.7410, "lon": 106.6690,
        "heat_points": [[10.7410, 106.6690]],
        "type": "ngập triều cường kênh Tàu Hủ - Bến Nghé"
    },

    # --- CÁC PHƯỜNG MỚI QUẬN 8 THEO NGHỊ QUYẾT 1685/NQ-UBTVQH15 ---
    {
        # Phường Chánh Hưng (Quận 8) - Hợp nhất P.4, Rạch Ông (P.1-P.3), Hưng Phú (P.8-P.10), một phần P.5
        "keywords": [
            "phường chánh hưng", "phuong chanh hung", "chánh hưng", "chanh hung",
            "rạch ông", "rach ong", "hưng phú", "hung phu", "phường 4 quận 8", "phường 5 quận 8"
        ],
        "display_name": "Khu vực Phường Chánh Hưng",
        "ward": "Phường Chánh Hưng",
        "priority": 2,
        "district": "Quận 8",
        "region": "TPHCM",
        "lat": 10.7440, "lon": 106.6780,
        "heat_points": [[10.7440, 106.6780]],
        "type": "ngập triều dâng khu vực Chánh Hưng - Rạch Ông"
    },
    {
        # Phường Phú Định (Quận 8) - Hợp nhất P.14, P.15, Xóm Củi (P.11-P.13), một phần P.16
        "keywords": [
            "phường phú định", "phuong phu dinh", "phú định", "phu dinh",
            "xóm củi", "xom cui", "phường 14 quận 8", "phường 15 quận 8"
        ],
        "display_name": "Khu vực Phường Phú Định",
        "ward": "Phường Phú Định",
        "priority": 2,
        "district": "Quận 8",
        "region": "TPHCM",
        "lat": 10.7390, "lon": 106.6350,
        "heat_points": [[10.7390, 106.6350]],
        "type": "ngập triều cường ven sông Chợ Đệm - Phú Định"
    },
    # =========================================================================
    # DANH SÁCH CÁC XÃ MỚI SAU SÁP NHẬP CHÍNH THỨC TẠI TP.HCM
    # (Đồng cấp Phường/Xã trực thuộc TP.HCM - Đã bỏ cấp Quận/Huyện)
    # =========================================================================


    # --- CÁC ĐIỂM NÓNG NGẬP NƯỚC TRỌNG ĐIỂM TẠI BÌNH TÂN (CHUẨN TIM ĐƯỜNG) ---
    {
        "keywords": ["hồ học lãm", "ho hoc lam", "hohoclam"],
        "display_name": "Đường Hồ Học Lãm",
        "ward": "Phường An Lạc",
        "district": "Quận Bình Tân",
        "region": "TPHCM",
        "lat": 10.7320, "lon": 106.6150,
        "heat_points": [[10.7320, 106.6150], [10.7280, 106.6180], [10.7360, 106.6120]],
        "priority": 3,
        "type": "ngập triều cường trục Hồ Học Lãm"
    },
    {
        "keywords": ["an dương vương", "an duong vuong", "anduongvuong"],
        "display_name": "Đường An Dương Vương",
        "ward": "Phường An Lạc",
        "district": "Quận Bình Tân",
        "region": "TPHCM",
        "lat": 10.7380, "lon": 106.6250,
        "heat_points": [[10.7380, 106.6250], [10.7420, 106.6230]],
        "priority": 3,
        "type": "ngập úng trũng thấp An Dương Vương"
    },
    {
        "keywords": ["ngã tư bốn xã", "nga tu bon xa", "bốn xã", "bon xa", "hương lộ 2", "huong lo 2"],
        "display_name": "Khu vực Ngã tư Bốn Xã (Bình Tân)",
        "ward": "Phường Bình Trị Đông",
        "district": "Quận Bình Tân",
        "region": "TPHCM",
        "lat": 10.7720, "lon": 106.6280,
        "heat_points": [[10.7720, 106.6280], [10.7700, 106.6250]],
        "priority": 3,
        "type": "ngập úng nút giao Bốn Xã - Hương Lộ 2"
    },
    {
        "keywords": ["tên lửa", "ten lua", "đường số 7 bình tân"],
        "display_name": "Đường Số 7",
        "ward": "Phường An Lạc",
        "district": "Quận Bình Tân",
        "region": "TPHCM",
        "lat": 10.7550, "lon": 106.6100,
        "heat_points": [[10.7550, 106.6100], [10.7580, 106.6080]],
        "priority": 3,
        "type": "ngập cục bộ khu dân cư Tên Lửa"
    },
    {
        "keywords": ["trần văn giàu", "tran van giau", "tranvangiau"],
        "display_name": "Đường Trần Văn Giàu",
        "ward": "Phường Tân Tạo",
        "district": "Quận Bình Tân",
        "region": "TPHCM",
        "lat": 10.7680, "lon": 106.5920,
        "heat_points": [[10.7680, 106.5920]],
        "priority": 3,
        "type": "ngập tràn tuyến Trần Văn Giàu"
    },

    # --- 07 XÃ MỚI HUYỆN BÌNH CHÁNH SAU SÁP NHẬP ---
    {
        # 1. Xã Vĩnh Lộc (Sáp nhập từ Xã Vĩnh Lộc A + một phần Xã Phạm Văn Hai)
        "keywords": [
            "vĩnh lộc", "vinh loc", "vinhloc",
            "vĩnh lộc a", "vinh loc a", "vinhloc a",
            "ngã 5 vĩnh lộc", "nga 5 vinh loc", "ngã năm vĩnh lộc", "nga nam vinh loc",
            "đường vĩnh lộc", "hương lộ 80"
        ],
        "display_name": "Khu vực Xã Vĩnh Lộc",
        "ward": "Xã Vĩnh Lộc",
        "priority": 2,
        "district": "Huyện Bình Chánh",
        "region": "TPHCM",
        "lat": 10.8126, "lon": 106.5773,
        "heat_points": [[10.8126, 106.5773], [10.8250, 106.5650], [10.8050, 106.5820]],
        "type": "ngập úng trũng thấp Xã Vĩnh Lộc mới"
    },
    {
        # 2. Xã Tân Vĩnh Lộc (Sáp nhập từ Xã Vĩnh Lộc B + phần còn lại Phạm Văn Hai + một phần P. Tân Tạo)
        "keywords": [
            "tân vĩnh lộc", "tan vinh loc", "tanvinhloc",
            "vĩnh lộc b", "vinh loc b", "vinhloc b"
        ],
        "display_name": "Khu vực Xã Tân Vĩnh Lộc",
        "ward": "Xã Tân Vĩnh Lộc",
        "priority": 2,
        "district": "Huyện Bình Chánh",
        "region": "TPHCM",
        "lat": 10.7984, "lon": 106.5607,
        "heat_points": [[10.7984, 106.5607], [10.7850, 106.5500]],
        "type": "ngập úng trũng thấp Xã Tân Vĩnh Lộc"
    },
    {
        # 3. Xã Bình Lợi (Sáp nhập từ Xã Lê Minh Xuân + Xã Bình Lợi cũ)
        "keywords": [
            "bình lợi", "binh loi", "xã bình lợi",
            "lê minh xuân", "le minh xuan", "xã lê minh xuân"
        ],
        "display_name": "Khu vực Xã Bình Lợi",
        "ward": "Xã Bình Lợi",
        "priority": 2,
        "district": "Huyện Bình Chánh",
        "region": "TPHCM",
        "lat": 10.7650, "lon": 106.5150,
        "heat_points": [[10.7650, 106.5150]],
        "type": "ngập triều dâng ven Sông Thầy Cai - Kênh An Hạ"
    },
    {
        # 4. Xã Tân Nhựt (Sáp nhập từ TT. Tân Túc + Xã Tân Nhựt + Xã Tân Kiên + phần P. Tân Tạo A + P.16 Q.8)
        "keywords": [
            "tân nhựt", "tan nhut", "xã tân nhựt",
            "tân túc", "tan tuc", "thị trấn tân túc", "tt tân túc",
            "tân kiên", "tan kien", "xã tân kiên"
        ],
        "display_name": "Khu vực Xã Tân Nhựt",
        "ward": "Xã Tân Nhựt",
        "priority": 2,
        "district": "Huyện Bình Chánh",
        "region": "TPHCM",
        "lat": 10.6950, "lon": 106.5650,
        "heat_points": [[10.6950, 106.5650], [10.6899, 106.5841], [10.7250, 106.5880]],
        "type": "ngập úng ven Sông Chợ Đệm - Tân Túc"
    },
    {
        # 5. Xã Bình Chánh (Sáp nhập từ Xã Tân Quý Tây + Xã Bình Chánh + một phần Xã An Phú Tây)
        "keywords": [
            "xã bình chánh", "xa binh chanh",
            "tân quý tây", "tan quy tay", "xã tân quý tây",
            "an phú tây", "an phu tay", "xã an phú tây"
        ],
        "display_name": "Khu vực Xã Bình Chánh",
        "ward": "Xã Bình Chánh",
        "priority": 2,
        "district": "Huyện Bình Chánh",
        "region": "TPHCM",
        "lat": 10.6720, "lon": 106.5500,
        "heat_points": [[10.6720, 106.5500], [10.6650, 106.5750], [10.6850, 106.5980]],
        "type": "ngập úng trục Quốc Lộ 1A - Đinh Đức Thiện"
    },
    {
        # 6. Xã Hưng Long (Sáp nhập từ Xã Đa Phước + Xã Qui Đức + Xã Hưng Long cũ)
        "keywords": [
            "hưng long", "hung long", "xã hưng long",
            "đa phước", "da phuoc", "daphuoc", "xã đa phước",
            "qui đức", "quy đức", "qui duc", "quy duc", "xã qui đức", "xã quy đức"
        ],
        "display_name": "Khu vực Xã Hưng Long",
        "ward": "Xã Hưng Long",
        "priority": 2,
        "district": "Huyện Bình Chánh",
        "region": "TPHCM",
        "lat": 10.6550, "lon": 106.6100,
        "heat_points": [[10.6550, 106.6100], [10.6720, 106.6350], [10.6380, 106.6200]],
        "type": "ngập tràn tuyến Quốc Lộ 50 Đa Phước - Hưng Long"
    },
    {
        # 7. Xã Bình Hưng (Sáp nhập từ Xã Phong Phú + Xã Bình Hưng cũ + một phần P.7 Q.8)
        "keywords": [
            "bình hưng", "binh hung", "binhhung", "xã bình hưng",
            "phong phú", "phong phu", "phongphu", "xã phong phú"
        ],
        "display_name": "Khu vực Xã Bình Hưng",
        "ward": "Xã Bình Hưng",
        "priority": 2,
        "district": "Huyện Bình Chánh",
        "region": "TPHCM",
        "lat": 10.7200, "lon": 106.6550,
        "heat_points": [[10.7200, 106.6550], [10.7280, 106.6620], [10.7100, 106.6450]],
        "type": "ngập triều cường trục Quốc lộ 50 - Sông Cần Giuộc"
    },

    # --- 04 XÃ MỚI HUYỆN HÓC MÔN SAU SÁP NHẬP ---
    {
        # 1. Xã Hóc Môn (Sáp nhập từ Xã Tân Xuân + Xã Tân Hiệp + Thị trấn Hóc Môn cũ)
        "keywords": [
            "hóc môn", "hoc mon", "hocmon", "xã hóc môn",
            "tân xuân", "tan xuan", "xã tân xuân",
            "tân hiệp hóc môn", "xã tân hiệp hóc môn",
            "thị trấn hóc môn", "tt hóc môn"
        ],
        "display_name": "Khu vực Xã Hóc Môn",
        "ward": "Xã Hóc Môn",
        "priority": 2,
        "district": "Huyện Hóc Môn",
        "region": "TPHCM",
        "lat": 10.8850, "lon": 106.5950,
        "heat_points": [[10.8850, 106.5950], [10.8893, 106.5954]],
        "type": "ngập tràn tuyến Song Hành Quốc Lộ 22"
    },
    {
        # 2. Xã Bà Điểm (Sáp nhập từ Xã Xuân Thới Thượng + Xã Bà Điểm + Xã Trung Chánh cũ)
        "keywords": [
            "bà điểm", "ba diem", "badiem", "ngã tư bà điểm", "xã bà điểm",
            "xuân thới thượng", "xuan thoi thuong", "xã xuân thới thượng",
            "trung chánh", "trung chanh", "xã trung chánh"
        ],
        "display_name": "Khu vực Xã Bà Điểm",
        "ward": "Xã Bà Điểm",
        "priority": 2,
        "district": "Huyện Hóc Môn",
        "region": "TPHCM",
        "lat": 10.8350, "lon": 106.6020,
        "heat_points": [[10.8350, 106.6020], [10.8400, 106.5700]],
        "type": "ngập úng cửa ngõ Phan Văn Hớn - Dương Công Khi"
    },
    {
        # 3. Xã Xuân Thới Sơn (Sáp nhập từ Xã Xuân Thới Đông + Xã Xuân Thới Sơn + Xã Tân Thới Nhì cũ)
        "keywords": [
            "xuân thới sơn", "xuan thoi son", "xã xuân thới sơn",
            "xuân thới đông", "xuan thoi dong", "xã xuân thới đông",
            "tân thới nhì", "tan thoi nhi", "xã tân thới nhì"
        ],
        "display_name": "Khu vực Xã Xuân Thới Sơn",
        "ward": "Xã Xuân Thới Sơn",
        "priority": 2,
        "district": "Huyện Hóc Môn",
        "region": "TPHCM",
        "lat": 10.8650, "lon": 106.5750,
        "heat_points": [[10.8650, 106.5750]],
        "type": "ngập úng trục Quốc Lộ 22 - Tân Thới Nhì"
    },
    {
        # 4. Xã Đông Thạnh (Sáp nhập từ Xã Đông Thạnh + Xã Nhị Bình + Xã Thới Tam Thôn cũ)
        "keywords": [
            "đông thạnh", "dong thanh", "xã đông thạnh",
            "nhị bình", "nhi binh", "xã nhị bình",
            "thới tam thôn", "thoi tam thon", "xã thới tam thôn"
        ],
        "display_name": "Khu vực Xã Đông Thạnh",
        "ward": "Xã Đông Thạnh",
        "priority": 2,
        "district": "Huyện Hóc Môn",
        "region": "TPHCM",
        "lat": 10.8950, "lon": 106.6450,
        "heat_points": [[10.8950, 106.6450], [10.9150, 106.6750], [10.8800, 106.6050]],
        "type": "ngập ven Sông Sài Gòn - Nhị Bình - Đông Thạnh"
    },

    # --- 02 XÃ MỚI HUYỆN NHÀ BÈ SAU SÁP NHẬP ---
    {
        # 1. Xã Nhà Bè (Sáp nhập từ TT. Nhà Bè + Xã Phú Xuân + Xã Phước Kiển + Xã Phước Lộc cũ)
        # Trụ sở: Số 330 đường Nguyễn Bình, xã Phú Xuân cũ
        "keywords": [
            "nhà bè", "nha be", "xã nhà bè", "thị trấn nhà bè", "tt nhà bè",
            "phú xuân", "phu xuan", "xã phú xuân",
            "phước kiển", "phuoc kien", "xã phước kiển",
            "phước lộc", "phuoc loc", "xã phước lộc"
        ],
        "display_name": "Khu vực Xã Nhà Bè",
        "ward": "Xã Nhà Bè",
        "priority": 2,
        "district": "Huyện Nhà Bè",
        "region": "TPHCM",
        "lat": 10.7020, "lon": 106.7250,
        "heat_points": [[10.7020, 106.7250], [10.7180, 106.7020], [10.6900, 106.7450]],
        "type": "ngập triều dâng trục Huỳnh Tấn Phát - Lê Văn Lương"
    },
    {
        # 2. Xã Hiệp Phước (Sáp nhập từ Xã Nhơn Đức + Xã Long Thới + Xã Hiệp Phước cũ)
        # Trụ sở: Số 209 đường Nguyễn Văn Tạo, xã Long Thới cũ
        "keywords": [
            "hiệp phước", "hiep phuoc", "xã hiệp phước",
            "nhơn đức", "nhon duc", "xã nhơn đức",
            "long thới", "long thoi", "xã long thới"
        ],
        "display_name": "Khu vực Xã Hiệp Phước",
        "ward": "Xã Hiệp Phước",
        "priority": 2,
        "district": "Huyện Nhà Bè",
        "region": "TPHCM",
        "lat": 10.6550, "lon": 106.7450,
        "heat_points": [[10.6550, 106.7450], [10.6300, 106.7550]],
        "type": "ngập triều dâng cửa sông Soài Rạp - Nguyễn Văn Tạo"
    },

    {
        "keywords": ["quận 12", "quan 12", "quan12", "an phú đông"],
        "display_name": "Khu vực Quận 12",
        "priority": 1,
        "ward": "Phường Trung Mỹ Tây",
        "district": "Quận 12",
        "region": "TPHCM",
        "lat": 10.8670, "lon": 106.6260,
        "heat_points": [[10.8670, 106.6260]],
        "type": "ngập cục bộ Quận 12"
    },
    {
        "keywords": ["quận 11", "quan 11", "quan11"],
        "display_name": "Khu vực Quận 11",
        "priority": 1,
        "ward": "Phường Nhiêu Lộc",
        "district": "Quận 11",
        "region": "TPHCM",
        "lat": 10.7670, "lon": 106.6530,
        "heat_points": [[10.7670, 106.6530]],
        "type": "ngập khu Đầm Sen"
    },
    {
        "keywords": ["quận 3", "quan 3", "quan3"],
        "display_name": "Khu vực Quận 3",
        "priority": 1,
        "ward": "Phường Xuân Hòa",
        "district": "Quận 3",
        "region": "TPHCM",
        "lat": 10.7810, "lon": 106.6800,
        "heat_points": [[10.7810, 106.6800]],
        "type": "ngập nội đô Quận 3"
    },
    {
        "keywords": ["quận 4", "quan 4", "quan4", "bến vân đồn"],
        "display_name": "Khu vực Quận 4",
        "ward": "Phường Xóm Chiếu",
        "district": "Quận 4",
        "region": "TPHCM",
        "lat": 10.7620, "lon": 106.7050,
        "heat_points": [[10.7620, 106.7050]],
        "type": "triều cường ven sông Sài Gòn"
    },
    {
        "keywords": ["quận 5", "quan 5", "quan5", "chợ lớn"],
        "display_name": "Khu vực Quận 5 (Chợ Lớn)",
        "ward": "Phường An Đông",
        "district": "Quận 5",
        "region": "TPHCM",
        "lat": 10.7540, "lon": 106.6620,
        "heat_points": [[10.7540, 106.6620]],
        "type": "ngập nước khu vực thương mại"
    },
    {
        "keywords": ["quận 6", "quan 6", "quan6"],
        "display_name": "Khu vực Quận 6",
        "ward": "Phường Bình Tiên",
        "district": "Quận 6",
        "region": "TPHCM",
        "lat": 10.7480, "lon": 106.6450,
        "heat_points": [[10.7480, 106.6450]],
        "type": "ngập úng trũng thấp Quận 6"
    },
    {
        "keywords": ["quận 10", "quan 10", "quan10"],
        "display_name": "Khu vực Quận 10",
        "priority": 1,
        "ward": "Phường Diên Hồng",
        "district": "Quận 10",
        "region": "TPHCM",
        "lat": 10.7720, "lon": 106.6650,
        "heat_points": [[10.7720, 106.6650]],
        "type": "ngập cục bộ nội đô"
    },
    {
        "keywords": ["phú nhuận", "phu nhuan", "phunhuan"],
        "display_name": "Khu vực Quận Phú Nhuận",
        "priority": 1,
        "ward": "Phường Cầu Kiệu",
        "district": "Quận Phú Nhuận",
        "region": "TPHCM",
        "lat": 10.7980, "lon": 106.6850,
        "heat_points": [[10.7980, 106.6850]],
        "type": "ngập ven kênh Nhiêu Lộc"
    },
    {
        "keywords": ["củ chi", "cu chi", "cuchi"],
        "display_name": "Khu vực Huyện Củ Chi",
        "ward": "Xã Tân An Hội",
        "district": "Huyện Củ Chi",
        "region": "TPHCM",
        "lat": 10.9750, "lon": 106.4950,
        "heat_points": [[10.9750, 106.4950]],
        "type": "ngập úng ngoại thành Tây Bắc"
    },
    {
        "keywords": ["cần giờ", "can gio", "cangio"],
        "display_name": "Khu vực Huyện Cần Giờ",
        "ward": "Xã Cần Giờ",
        "district": "Huyện Cần Giờ",
        "region": "TPHCM",
        "lat": 10.4100, "lon": 106.9600,
        "heat_points": [[10.4100, 106.9600]],
        "type": "triều cường ven biển Cần Giờ"
    },
    {
        "keywords": ["quận 1", "quan 1", "quan1"],
        "display_name": "Khu vực Quận 1",
        "ward": "Phường Sài Gòn",
        "district": "Quận 1",
        "region": "TPHCM",
        "lat": 10.7765, "lon": 106.7009,
        "heat_points": [[10.7765, 106.7009]],
        "type": "ngập cục bộ trung tâm Quận 1"
    },
    {
        "keywords": [
            "tp. hồ chí minh", "tp hồ chí minh", "thành phố hồ chí minh", "tp.hcm", "tphcm", "tp hcm",
            "sài gòn", "sai gon", "saigon", "sông sài gòn", "sg", "hcm",
            "bình dương", "binh duong", "binhduong",
            "vũng tàu", "vung tau", "vungtau", "bà rịa", "ba ria", "baria", "bà rịa vũng tàu", "ba ria vung tau"
        ],
        "display_name": "Khu vực Toàn TP. Hồ Chí Minh (Diện rộng)",
        "ward": "Toàn thành phố (Chưa rõ phường/xã)",
        "administrative_unit": "Toàn thành phố (Chưa rõ phường/xã)",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7769, "lon": 106.7009,
        "heat_points": [[10.7769, 106.7009]],
        "priority": 0,
        "type": "ngập diện rộng toàn thành phố"
    }
]

# PHÂN TÁCH 3 THỨ BẬC KHÔNG GIAN (SPATIAL ENTITY HIERARCHY):
# Cấp 3 (Cao nhất): STREET_HOTSPOTS - Các tuyến đường cụ thể chuẩn tim đường OSM (122 CSGT + Seed Streets)
# Cấp 2: ADMIN_HOTSPOTS - 168 Đơn vị hành chính Phường/Xã mới sau sáp nhập
# Cấp 1 (Fallback): CITYWIDE_HOTSPOTS - Cấp Quận/Huyện chung & Toàn thành phố
STREET_HOTSPOTS: List[Dict[str, Any]] = [
    {
        "keywords": ["nguyễn an ninh", "nguyen an ninh", "nguyenanninh"],
        "display_name": "Đường Nguyễn An Ninh",
        "street": "Đường Nguyễn An Ninh",
        "ward": "Phường Dĩ An",
        "district": "TP. Dĩ An (Cửa ngõ TP. Thủ Đức)",
        "region": "TPHCM",
        "lat": 10.91465, "lon": 106.76948,
        "heat_points": [[10.91465, 106.76948], [10.9104, 106.7698]],
        "priority": 3,
        "type": "ngập trục đường Nguyễn An Ninh (Phường Dĩ An)"
    },
    {
        "keywords": ["nguyễn thị tuôi", "nguyen thi tuoi", "nguyenthituoi"],
        "display_name": "Đường Nguyễn Thị Tuôi",
        "street": "Đường Nguyễn Thị Tuôi",
        "ward": "Xã Vĩnh Lộc",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8232, "lon": 106.5836,
        "heat_points": [[10.8211, 106.5846], [10.8232, 106.5836], [10.8253, 106.5826]],
        "priority": 3,
        "type": "ngập sâu trục đường Nguyễn Thị Tuôi (Xã Vĩnh Lộc)"
    },
    {
        "keywords": ["phan văn hớn", "phan van hon", "phanvanhon"],
        "display_name": "Đường Phan Văn Hớn",
        "street": "Đường Phan Văn Hớn",
        "ward": "Phường Đông Hưng Thuận",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8486, "lon": 106.5892,
        "heat_points": [[10.8447, 106.6110], [10.8486, 106.5892], [10.8623, 106.5721]],
        "priority": 3,
        "type": "ngập sâu trục đường Phan Văn Hớn"
    },
    {
        "keywords": ["nguyễn thị tuôi", "nguyen thi tuoi", "nguyenthituoi"],
        "display_name": "Đường Nguyễn Thị Tuôi",
        "street": "Đường Nguyễn Thị Tuôi",
        "ward": "Xã Vĩnh Lộc",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8232, "lon": 106.5836,
        "heat_points": [[10.8211, 106.5846], [10.8232, 106.5836], [10.8253, 106.5826]],
        "priority": 3,
        "type": "ngập sâu trục đường Nguyễn Thị Tuôi (Xã Vĩnh Lộc)"
    },
    {
        "keywords": ["phan văn hớn", "phan van hon", "phanvanhon"],
        "display_name": "Đường Phan Văn Hớn",
        "street": "Đường Phan Văn Hớn",
        "ward": "Phường Đông Hưng Thuận",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8486, "lon": 106.5892,
        "heat_points": [[10.8447, 106.6110], [10.8486, 106.5892], [10.8623, 106.5721]],
        "priority": 3,
        "type": "ngập sâu trục đường Phan Văn Hớn"
    },
    # --- CÁC TUYẾN ĐƯỜNG BỔ SUNG ĐỘC LẬP (KHÔNG GỘP CHÙM) ---
    {
        "keywords": ["lã xuân oai", "la xuan oai", "laxuanoai"],
        "display_name": "Đường Lã Xuân Oai",
        "street": "Đường Lã Xuân Oai",
        "ward": "Phường Tăng Nhơn Phú",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8415, "lon": 106.7930,
        "heat_points": [[10.8415, 106.7930], [10.8480, 106.7860]],
        "priority": 3,
        "type": "ngập sâu trục đường Lã Xuân Oai"
    },
    {
        "keywords": ["nguyễn duy trinh", "nguyen duy trinh", "nguyenduytrinh"],
        "display_name": "Đường Nguyễn Duy Trinh",
        "street": "Đường Nguyễn Duy Trinh",
        "ward": "Phường Long Trường",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7908, "lon": 106.7860,
        "heat_points": [[10.7908, 106.7860], [10.7930, 106.7920]],
        "priority": 3,
        "type": "ngập sâu trục đường Nguyễn Duy Trinh"
    },
    {
        "keywords": ["đồng đen", "dong den", "dongden"],
        "display_name": "Đường Đồng Đen",
        "street": "Đường Đồng Đen",
        "ward": "Phường Bảy Hiền",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7925, "lon": 106.6475,
        "heat_points": [[10.7925, 106.6475]],
        "priority": 3,
        "type": "ngập sâu trục đường Đồng Đen"
    },
    {
        "keywords": ["bàu cát", "bau cat", "baucat"],
        "display_name": "Đường Bàu Cát",
        "street": "Đường Bàu Cát",
        "ward": "Phường Bảy Hiền",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7910, "lon": 106.6450,
        "heat_points": [[10.7910, 106.6450]],
        "priority": 3,
        "type": "ngập sâu trục đường Bàu Cát"
    },
    {
        "keywords": ["lũy bán bích", "luy ban bich", "luybanbich"],
        "display_name": "Đường Lũy Bán Bích",
        "street": "Đường Lũy Bán Bích",
        "ward": "Phường Phú Thạnh",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7780, "lon": 106.6320,
        "heat_points": [[10.7780, 106.6320]],
        "priority": 3,
        "type": "ngập sâu trục đường Lũy Bán Bích"
    },
    {
        "keywords": ["âu cơ", "au co", "auco"],
        "display_name": "Đường Âu Cơ",
        "street": "Đường Âu Cơ",
        "ward": "Phường Phú Thạnh",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7830, "lon": 106.6450,
        "heat_points": [[10.7830, 106.6450]],
        "priority": 3,
        "type": "ngập sâu trục đường Âu Cơ"
    },
    {
        "keywords": ["nguyễn văn hưởng", "nguyen van huong", "nguyenvanhuong"],
        "display_name": "Đường Nguyễn Văn Hưởng",
        "street": "Đường Nguyễn Văn Hưởng",
        "ward": "Phường An Khánh",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8090, "lon": 106.7310,
        "heat_points": [[10.8090, 106.7310]],
        "priority": 3,
        "type": "triều cường sông Sài Gòn tràn đường Nguyễn Văn Hưởng"
    },
    {
        "keywords": ["nguyễn bình", "nguyen binh", "nguyenbinh"],
        "display_name": "Đường Nguyễn Bình",
        "street": "Đường Nguyễn Bình",
        "ward": "Xã Hiệp Phước",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.6650, "lon": 106.7220,
        "heat_points": [[10.6650, 106.7220]],
        "priority": 3,
        "type": "ngập triều dâng đường Nguyễn Bình"
    },
    {
        "keywords": ["nguyễn ảnh thủ", "nguyen anh thu", "nguyenanhthu"],
        "display_name": "Đường Nguyễn Ảnh Thủ",
        "street": "Đường Nguyễn Ảnh Thủ",
        "ward": "Xã Bà Điểm",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8614, "lon": 106.6112,
        "heat_points": [[10.8614, 106.6112], [10.8570, 106.6080], [10.8660, 106.6150]],
        "priority": 3,
        "type": "ngập sâu trục đường Nguyễn Ảnh Thủ (giao Song Hành QL22)"
    },
]
CITYWIDE_HOTSPOTS: List[Dict[str, Any]] = [
    {
        "keywords": ["nguyễn thị tuôi", "nguyen thi tuoi", "nguyenthituoi"],
        "display_name": "Đường Nguyễn Thị Tuôi",
        "street": "Đường Nguyễn Thị Tuôi",
        "ward": "Xã Vĩnh Lộc",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8232, "lon": 106.5836,
        "heat_points": [[10.8211, 106.5846], [10.8232, 106.5836], [10.8253, 106.5826]],
        "priority": 3,
        "type": "ngập sâu trục đường Nguyễn Thị Tuôi (Xã Vĩnh Lộc)"
    },
    {
        "keywords": ["phan văn hớn", "phan van hon", "phanvanhon"],
        "display_name": "Đường Phan Văn Hớn",
        "street": "Đường Phan Văn Hớn",
        "ward": "Phường Đông Hưng Thuận",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8486, "lon": 106.5892,
        "heat_points": [[10.8447, 106.6110], [10.8486, 106.5892], [10.8623, 106.5721]],
        "priority": 3,
        "type": "ngập sâu trục đường Phan Văn Hớn"
    },
    # --- CÁC TUYẾN ĐƯỜNG BỔ SUNG ĐỘC LẬP (KHÔNG GỘP CHÙM) ---
    {
        "keywords": ["lã xuân oai", "la xuan oai", "laxuanoai"],
        "display_name": "Đường Lã Xuân Oai",
        "street": "Đường Lã Xuân Oai",
        "ward": "Phường Tăng Nhơn Phú",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8415, "lon": 106.7930,
        "heat_points": [[10.8415, 106.7930], [10.8480, 106.7860]],
        "priority": 3,
        "type": "ngập sâu trục đường Lã Xuân Oai"
    },
    {
        "keywords": ["nguyễn duy trinh", "nguyen duy trinh", "nguyenduytrinh"],
        "display_name": "Đường Nguyễn Duy Trinh",
        "street": "Đường Nguyễn Duy Trinh",
        "ward": "Phường Long Trường",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7908, "lon": 106.7860,
        "heat_points": [[10.7908, 106.7860], [10.7930, 106.7920]],
        "priority": 3,
        "type": "ngập sâu trục đường Nguyễn Duy Trinh"
    },
    {
        "keywords": ["đồng đen", "dong den", "dongden"],
        "display_name": "Đường Đồng Đen",
        "street": "Đường Đồng Đen",
        "ward": "Phường Bảy Hiền",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7925, "lon": 106.6475,
        "heat_points": [[10.7925, 106.6475]],
        "priority": 3,
        "type": "ngập sâu trục đường Đồng Đen"
    },
    {
        "keywords": ["bàu cát", "bau cat", "baucat"],
        "display_name": "Đường Bàu Cát",
        "street": "Đường Bàu Cát",
        "ward": "Phường Bảy Hiền",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7910, "lon": 106.6450,
        "heat_points": [[10.7910, 106.6450]],
        "priority": 3,
        "type": "ngập sâu trục đường Bàu Cát"
    },
    {
        "keywords": ["lũy bán bích", "luy ban bich", "luybanbich"],
        "display_name": "Đường Lũy Bán Bích",
        "street": "Đường Lũy Bán Bích",
        "ward": "Phường Phú Thạnh",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7780, "lon": 106.6320,
        "heat_points": [[10.7780, 106.6320]],
        "priority": 3,
        "type": "ngập sâu trục đường Lũy Bán Bích"
    },
    {
        "keywords": ["âu cơ", "au co", "auco"],
        "display_name": "Đường Âu Cơ",
        "street": "Đường Âu Cơ",
        "ward": "Phường Phú Thạnh",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.7830, "lon": 106.6450,
        "heat_points": [[10.7830, 106.6450]],
        "priority": 3,
        "type": "ngập sâu trục đường Âu Cơ"
    },
    {
        "keywords": ["nguyễn văn hưởng", "nguyen van huong", "nguyenvanhuong"],
        "display_name": "Đường Nguyễn Văn Hưởng",
        "street": "Đường Nguyễn Văn Hưởng",
        "ward": "Phường An Khánh",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8090, "lon": 106.7310,
        "heat_points": [[10.8090, 106.7310]],
        "priority": 3,
        "type": "triều cường sông Sài Gòn tràn đường Nguyễn Văn Hưởng"
    },
    {
        "keywords": ["nguyễn bình", "nguyen binh", "nguyenbinh"],
        "display_name": "Đường Nguyễn Bình",
        "street": "Đường Nguyễn Bình",
        "ward": "Xã Hiệp Phước",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.6650, "lon": 106.7220,
        "heat_points": [[10.6650, 106.7220]],
        "priority": 3,
        "type": "ngập triều dâng đường Nguyễn Bình"
    },
    {
        "keywords": ["nguyễn ảnh thủ", "nguyen anh thu", "nguyenanhthu"],
        "display_name": "Đường Nguyễn Ảnh Thủ",
        "street": "Đường Nguyễn Ảnh Thủ",
        "ward": "Xã Bà Điểm",
        "district": "TP.HCM",
        "region": "TPHCM",
        "lat": 10.8614, "lon": 106.6112,
        "heat_points": [[10.8614, 106.6112], [10.8570, 106.6080], [10.8660, 106.6150]],
        "priority": 3,
        "type": "ngập sâu trục đường Nguyễn Ảnh Thủ (giao Song Hành QL22)"
    },
]

if CSGT_HOTSPOTS:
    for s in CSGT_HOTSPOTS:
        s_copy = dict(s)
        s_copy["priority"] = 3
        s_copy["street"] = s_copy.get("street") or s_copy.get("display_name", "")
        STREET_HOTSPOTS.append(s_copy)

for h in HOTSPOTS:
    h_copy = dict(h)
    disp = h_copy.get("display_name", "")
    prio = h_copy.get("priority")
    
    # Kiểm tra rõ ràng các mục cấp Quận / Huyện / Toàn thành phố -> Cấp 1
    if prio == 1 or prio == 0 or disp.startswith("Khu vực Quận") or disp.startswith("Khu vực Huyện") or disp.startswith("Khu vực TP.") or disp.startswith("Khu vực Toàn"):
        h_copy["priority"] = 1
        h_copy["street"] = ""
        CITYWIDE_HOTSPOTS.append(h_copy)
    elif prio == 2 or disp.startswith("Khu vực Phường") or disp.startswith("Khu vực Xã"):
        h_copy["priority"] = 2
        h_copy["street"] = ""
        ADMIN_HOTSPOTS.append(h_copy)
    else:
        h_copy["priority"] = 3
        h_copy["street"] = h_copy.get("street") or disp
        STREET_HOTSPOTS.append(h_copy)

# TOÀN BỘ CÁC TỈNH/THÀNH PHỐ NGOÀI TP. HỒ CHÍ MINH (LOẠI BỎ TRIỆT ĐỂ KHÔNG CHỪA SƠ HỞ)
OUT_OF_SCOPE_LOCATIONS = [
    # Miền Bắc
    "hà nội", "ha noi", "hanoi", "hà đông", "ha dong", "hadong", "cầu giấy", "cau giay", "hoàn kiếm", "hoan kiem",
    "đống đa", "dong da", "ba đình", "ba dinh", "hai bà trưng", "thanh xuân", "hoàng mai", "long biên",
    "thái nguyên", "thai nguyen", "thainguyen", "yên bái", "yen bai", "yenbai", "lào cai", "lao cai", "laocai",
    "quảng ninh", "quang ninh", "quangninh", "hạ long", "ha long", "halong", "hải phòng", "hai phong", "haiphong",
    "hải dương", "hai duong", "bắc ninh", "bac ninh", "bắc giang", "bac giang", "phú thọ", "phu tho",
    "việt trì", "viet tri", "vĩnh phúc", "vinh phuc", "vĩnh yên", "nam định", "nam dinh", "ninh bình", "ninh binh",
    "thái bình", "thai binh", "hà nam", "ha nam", "hưng yên", "hung yen", "hà giang", "ha giang", "cao bằng", "cao bang",
    "lạng sơn", "lang son", "tuyên quang", "tuyen quang", "sơn la", "son la", "điện biên", "dien bien",
    "lai châu", "lai chau", "hòa bình", "hoa binh", "miền bắc", "mien bac", "mienbac",

    # Miền Trung
    "thanh hóa", "thanh hoa", "thanhhoa", "nghệ an", "nghe an", "nghean", "tp vinh", "tp. vinh", "thành phố vinh", "tpvinh",
    "hà tĩnh", "ha tinh", "hatinh", "hatinhnho", "quảng bình", "quang binh", "quangbinh", "đồng hới",
    "quảng trị", "quang tri", "đông hà", "thừa thiên huế", "huế", "hue", "đà nẵng", "da nang", "danang",
    "quảng nam", "quang nam", "quangnam", "hội an", "tam kỳ", "quảng ngãi", "quang ngai",
    "bình định", "binh dinh", "quy nhơn", "phú yên", "phu yen", "tuy hòa", "khánh hòa", "khanh hoa", "nha trang", "nhatrang",
    "ninh thuận", "ninh thuan", "phan rang", "bình thuận", "binh thuan", "phan thiết", "phan thiet", "phanthiet",
    "miền trung", "mien trung",

    # Tây Nguyên
    "kon tum", "kontum", "gia lai", "gialai", "pleiku", "đắk lắk", "dak lak", "daklak", "đắc lắc", "buôn ma thuột", "bmt",
    "đắk nông", "dak nong", "daknong", "lâm đồng", "lam dong", "lamdong", "đà lạt", "da lat", "dalat", "bảo lộc", "tây nguyên", "tay nguyen",

    # Đông Nam Bộ & Lân cận TP.HCM (Ngoại trừ Bình Dương & Bà Rịa - Vũng Tàu đã sáp nhập vào TP.HCM theo NQ 1685)
    "đồng nai", "dong nai", "dongnai", "biên hòa", "bien hoa", "bienhoa", "trảng bom", "trang bom", "trangbom",
    "long thành", "long thanh", "nhơn trạch", "nhon trach", "vĩnh cửu", "định quán", "long khánh", "xuân lộc",
    "bình phước", "binh phuoc", "đồng xoài", "dong xoai",
    "tây ninh", "tay ninh", "tayninh",

    # Cần Thơ & Miền Tây (ĐBSCL)
    "cần thơ", "can tho", "cantho", "canthotv", "cần thơ tv", "btv", "ninh kiều", "cái răng", "bình thủy", "ô môn", "thốt nốt", "sông hậu", "song hau",
    "đèo mẹ bồng con", "deo me bong con", "mẹ bồng con", "me bong con", "dầu giây", "dau giay", "long khánh", "long khanh", "an lộc", "an loc",
    "long an", "longan", "tân an", "tan an", "bến lức", "ben luc", "đức hòa", "duc hoa", "cần giuộc", "cần đước",
    "tiền giang", "tien giang", "tiengiang", "mỹ tho", "my tho", "mytho", "gò công", "cai lậy",
    "bến tre", "ben tre", "bentre", "ba tri",
    "trà vinh", "tra vinh", "travinh",
    "vĩnh long", "vinh long", "vinhlong", "bình minh",
    "đồng tháp", "dong thap", "dongthap", "cao lãnh", "cao lanh", "sa đéc", "sa dec", "sadec", "sadect", "hồng ngự",
    "an giang", "an giang", "angiang", "long xuyên", "long xuyen", "châu đốc", "chau doc",
    "kiên giang", "kien giang", "kiengiang", "rạch giá", "rach gia", "phú quốc", "phu quoc", "phuquoc", "hà tiên",
    "cần thơ", "can tho", "cantho", "ninh kiều", "cái răng", "bình thủy", "ô môn", "thốt nốt", "sông hậu", "song hau",
    "hậu giang", "hau giang", "haugiang", "vị thanh", "ngã bảy",
    "sóc trăng", "soc trang", "soctrang",
    "bạc liêu", "bac lieu", "baclieu",
    "cà mau", "ca mau", "camau", "năm căn", "u minh",
    "miền tây", "mien tay", "mientay", "đbscl", "dbscl", "sông tiền", "nam bộ",

    # Quốc tế
    "bangkok", "thái lan", "thailand", "trung quốc", "china", "indonesia", "manila", "philippines", "nhật bản", "nhat ban", "japan", "tokyo", "hàn quốc", "han quoc", "korea", "singapore", "malaysia"
]

ROAD_PREFIXES = r'(?:\bđường(?!\s+cống|\s+hầm\s+kỹ|\s+ống|\s+dây)|\bduong|tuyến\s+đường|tuyen\s+duong|quốc\s+lộ|quoc\s+lo|ql\s+|tỉnh\s+lộ|tinh\s+lo|tl\s+|xa\s+lộ|xa\s+lo|đại\s+lộ|dai\s+lo|hầm(?:\s+chui)?(?!\s+theo|\s+phải|\s+vào)|ham(?:\s+chui)?|cầu|cau|ngã\s+(?:tư|ba)|nga\s+(?:tu|ba)|vòng\s+xoay|vong\s+xoay|nút\s+giao|hẻm(?:\s+\d+)?|hem(?:\s+\d+)?|(?<!thành\s)(?<!thanh\s)\bphố\b(?!\s+thông\s+minh))'
ROAD_STOP_LOOKAHEAD = r'(?=[,\.\n;:\(\)]|(?:\s+(?:và|va|giao|đoạn|khúc|với|quận|quan|huyện|huyen|phường|phuong|thị\s+trấn|tp|đang|dang|bị|bi|được|duoc|gồm|gom|tại|tai|cũng|cung|đều|deu|lại|lai|sẽ|se|nước|nuoc|kẹt|ket|ngập|ngap|xe|lút|chết|nguy|mọi|bà\s+con|rất|kéo\s+dài|keo\s+dai|cống|thoát|theo\s+hướng|hướng\s+từ|đê\s+bao|phong\s+tỏa|ven\s+sông|thông\s+minh))|$)'
ROAD_PATTERN = re.compile(
    rf'{ROAD_PREFIXES}\s+(?!ngập|nước|kẹt|lội|sâu|cống|thoát|thông\s+minh|ven\s+sông|theo\s+hướng)([A-ZÀ-Ỹa-zà-ỹ0-9\s\.\-]+?){ROAD_STOP_LOOKAHEAD}',
    re.IGNORECASE
)

STOP_WORDS_SUFFIX = [
    "hôm nay", "hom nay", "chiều nay", "chieu nay", "sáng nay", "sang nay",
    "tối qua", "toi qua", "ngay lúc này", "đoạn", "doan", "khúc", "khuc",
    "gần", "gan", "ngập sâu", "ngập nước", "kẹt xe"
]

STOP_CANDIDATE_WORDS = [
    "tp hcm", "tphcm", "tp.hcm", "sài gòn", "sai gon", "saigon", "ngập xá", "ngap xa", "ngập sâu", "ngap sau",
    "này", "kia", "đó", "xe", "nhà", "tại", "tai", "khu", "chỗ", "vào", "ra", "lên", "xuống", "sau", "trước",
    "lội", "loi", "thuộc", "trũng", "phố", "đường", "nào", "mới", "cũ", "qua", "lại", "đi", "na3", "mưa",
    "khu vực", "khu vuc", "trung tâm", "trung tam", "khu vực trung tâm", "khu vuc trung tam",
    "mọi người", "moi nguoi", "người né", "nguoi ne", "ai cứu", "cứu tôi", "bà con", "di chuyển", "giao thông", "hóa sông", "trở về", "về nhà", "đi lại", "ngập sâu", "lênh láng", "bì bõm", "lội nước", "ùn tắc", "kẹt xe", "tan tầm", "vắng tanh", "nước cống", "tràn vào", "vượt qua", "tê liệt"
]

def clean_road_candidate(candidate: str) -> str:
    res = candidate.strip()
    res_lower = res.lower()
    for sw in STOP_WORDS_SUFFIX:
        if res_lower.endswith(sw):
            res = res[:len(res) - len(sw)].strip()
            res_lower = res.lower()
    if any(b in res_lower for b in BOGUS_ROAD_PHRASES):
        return ""
    return res

def geocode_osm_dynamic(query: str) -> Optional[Dict[str, Any]]:
    """
    Tự động truy vấn OpenStreetMap Nominatim khi phát hiện tên đường mới chưa có trong Gazetteer.
    Chuẩn hóa lấy đúng tim đường (highway) để ghim marker không bao giờ bị lệch vào nhà dân/hẻm cụt.
    Có bộ nhớ đệm tự lưu (Self-learning Cache) để không cần gọi lại lần 2.
    """
    clean_q = query.strip().lower()
    if clean_q in DYNAMIC_CACHE:
        return DYNAMIC_CACHE[clean_q]
    if clean_q in FAILED_DYNAMIC_CACHE:
        return None

    # Kiểm duyệt chất lượng: Tên đường hợp lệ phải có ít nhất 2 từ hoặc có định danh số/chữ
    # Kiểm duyệt chất lượng: Tuyệt đối không geocode từ rác / từ không phải đường
    if any(b in clean_q for b in BOGUS_ROAD_PHRASES):
        FAILED_DYNAMIC_CACHE.add(clean_q)
        return None

    words = clean_q.split()
    if len(words) < 2 and not any(ch.isdigit() for ch in clean_q):
        return None

    # Lọc bỏ tiền tố đường/phố để tìm trên OSM
    street_clean = re.sub(r'^(đường|đại lộ|tuyến đường|phố|hẻm)\s+', '', query, flags=re.IGNORECASE).strip()
    
    headers = {"User-Agent": "SE363-PrecisionGIS/4.0 (contact: student@hcmut.edu.vn)"}
    
    # 1. Thử truy vấn cấu trúc street + city
    url_structured = f"https://nominatim.openstreetmap.org/search?street={urllib.parse.quote(street_clean)}&city={urllib.parse.quote('Thành phố Hồ Chí Minh')}&format=json&limit=5"
    req1 = urllib.request.Request(url_structured, headers=headers)
    
    item = None
    try:
        with urllib.request.urlopen(req1, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for d in data:
                if d.get("class") == "highway":
                    item = d
                    break

    except Exception:
        item = None

    # 2. Dự phòng truy vấn toàn văn nếu cấu trúc không ra
    if not item:
        url_fallback = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query + ', Hồ Chí Minh, Việt Nam')}&format=json&limit=5"
        req2 = urllib.request.Request(url_fallback, headers=headers)
        try:
            with urllib.request.urlopen(req2, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for d in data:
                    if d.get("class") == "highway":
                        item = d
                        break

        except Exception:
            item = None

    if not item:
        FAILED_DYNAMIC_CACHE.add(clean_q)
        return None

    lat = round(float(item["lat"]), 4)
    lon = round(float(item["lon"]), 4)

    # Ranh giới địa lý chuẩn xác của TP.HCM mở rộng
    if not (10.38 <= lat <= 11.15 and 106.35 <= lon <= 107.02):
        return None

    disp = item.get("display_name", "")
    parts = [p.strip() for p in disp.split(",")]
    ward = "Đô thị TP.HCM"
    district = "TP.HCM"
    for p in parts:
        if any(k in p for k in ["Phường", "Xã", "Thị trấn"]):
            ward = p
        elif any(k in p for k in ["Quận", "Huyện", "Thủ Đức"]):
            district = p

    title_name = query.title()
    if not any(title_name.lower().startswith(p) for p in ["đường", "cầu", "ngã", "vòng"]):
        title_name = f"Đường {title_name}"

    res = {
        "matched_keyword": query,
        "display_name": title_name,
        "ward": ward,
        "district": district,
        "region": "TPHCM",
        "lat": lat,
        "lon": lon,
        "heat_points": [[lat, lon]],
        "type": "ngập đô thị (OSM tim đường chính xác)"
    }
    DYNAMIC_CACHE[clean_q] = res
    save_dynamic_cache()
    return res

def _finalize_match(res: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not res:
        return None
    cur_w = res.get("ward", "")
    cur_d = res.get("district", "")
    off_w = RESOLVER.resolve_to_official_ward(cur_w, cur_d)
    if off_w:
        res["ward"] = off_w
        res["administrative_unit"] = off_w
    elif "24" in cur_w or "bình thạnh" in cur_w.lower():
        res["ward"] = "Phường Bình Thạnh"
        res["administrative_unit"] = "Phường Bình Thạnh"
    res["district"] = "TP.HCM"
    return res

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace('–', '-').replace('—', '-').replace('–', '-').replace('—', '-')
    text_nfc = unicodedata.normalize('NFC', text)
    return text_nfc.lower()

BOGUS_ROAD_PHRASES = set([
    "đoạn đường",
    "tuyến đường",
    "tân quý",
    "rạch chiếc",
    "ông lãnh",
    "tân sơn nhất",
    "tân thuận",
    # Hiện tượng & miêu tả nước
    "có nơi", "thành sông", "hóa sông", "như sông", "biến thành", "ngập sâu", "chết máy",
    "dâng cao", "rút lui", "chưa từng", "bì bõm", "lội nước", "kẹt xe", "mênh mông",
    "biển nước", "ngập tràn", "liên tục", "dồn ứ", "giá rẻ", "phố không", "vô hẻm", "và hẻm",
    "điểm trường", "trục lộ", "giao thông", "sau trận", "hơn 100", "yên xe", "chiếc xe",
    "mọi người", "người dân", "nước ngập", "nước dâng", "tới yên", "thất thủ",
    "ngập nặng", "ngập lụt", "triều cường", "mưa lớn", "mưa to", "xe máy", "nước đổ",
    "an lộc", "dầu giây", "mẹ bồng con", "đô thị", "do thi", "dự án", "vùng trũng",

    # Thoát nước & công trình kỹ thuật (TUYỆT ĐỐI KHÔNG PHẢI TÊN ĐƯỜNG)
    "cống", "cống thoát", "cống thoát nước", "đường cống", "hệ thống cống", "hệ thống thoát nước",
    "miệng cống", "hố ga", "nắp cống", "cống ngăn triều", "trạm bơm", "máy bơm",
    "đê bao", "bờ bao", "ven sông", "bờ kè", "kênh rạch", "dòng chảy", "cửa xả", "cửa cống",
    "thoát nước", "xả tràn", "ngăn triều", "tuyến đê",

    # Khái niệm & quy hoạch & từ vựng báo chí
    "thông minh", "thành phố thông minh", "đô thị thông minh", "chống ngập",
    "công trình", "quy hoạch", "nâng cấp", "xây dựng", "sửa chữa", "khởi công",
    "nghiên cứu", "đề xuất", "triển khai", "giải pháp", "tiêu chuẩn", "thiết kế",
    "tương hỗ", "cực đoan", "chu kỳ", "hiện hành", "cũ kỹ", "xuống cấp",
    "đồng nhất", "cơ sở", "khoa học", "nền tảng", "bản đồ", "dùng chung", "dữ liệu",
    "chính xác", "chất lượng", "cuộc sống", "phát triển",

    # Cụm trạng ngữ chỉ hướng, trạng thái (TUYỆT ĐỐI KHÔNG PHẢI TÊN ĐƯỜNG)
    "theo hướng", "hướng từ", "từ cao tốc", "về phía", "chiều về", "làn xe",
    "phong tỏa", "hai đầu", "bảo vệ", "phục vụ", "khiến một số", "lần lượt",
    "tình trạng", "nguyên nhân", "tổ hợp", "yếu tố", "rủi ro", "địa hình", "trũng thấp",
    "xuất phát", "thời gian", "khu nam", "ở khu nam", "khu đông", "khu tây", "khu bắc",
    "nội thành", "ngoại thành", "ven đô", "ngoại ô"
])

def match_hotspot(text: str) -> Optional[Dict[str, Any]]:
    """
    Bộ bóc tách thực thể địa lý đa tầng chuẩn mực (Strict Spatial Hierarchy):
    Quy tắc cốt lõi:
    1. Khi bài viết có TÊN ĐƯỜNG -> Ưu tiên TUYỆT ĐỐI hiển thị tên đường (Yếu tố chính).
       Phường/Xã chỉ đóng vai trò yếu tố phụ (Metadata).
    2. Khi bài viết KHÔNG CÓ TÊN ĐƯỜNG -> Mới hiển thị Phường/Xã làm yếu tố chính.
    3. Khi bài viết KHÔNG CÓ CẢ ĐƯỜNG LẪN PHƯỜNG -> Hiển thị Toàn thành phố làm yếu tố chính.
    Tuyệt đối không bịa hoặc tách câu sai kiểu ghép từ "có nơi", "thành sông".
    """
    if not text:
        return None
    
    clean_text = normalize_text(text)

    # BƯỚC 0: KIỂM SOÁT ĐỊA GIỚI NGHIÊM NGẶT - LOẠI TRỪ 100% CÁC TỈNH/THÀNH NGOÀI TP.HCM
    has_hcm_affirmation = any(k in clean_text for k in [
        "tphcm", "tp hcm", "tp.hcm", "sài gòn", "sai gon", "hồ chí minh", "ho chi minh",
        "bình dương", "binh duong", "vũng tàu", "vung tau", "bà rịa", "ba ria",
        "thủ dầu một", "dĩ an", "thuận an", "bến cát", "tân uyên", "phú mỹ", "côn đảo"
    ])
    if not has_hcm_affirmation:
        for out_loc in OUT_OF_SCOPE_LOCATIONS:
            pat = r'(?:\b|^|#)' + re.escape(out_loc) + r'(?:\b|$|[#\s.,!?])'
            if re.search(pat, clean_text):
                return None

    # =========================================================================
    # TẦNG 1: ƯU TIÊN SỐ 1 - BÓC TÁCH TUYẾN ĐƯỜNG (STREET-FIRST RESOLUTION)
    # =========================================================================
    best_street = None
    best_street_len = 0

    # 1.A: So khớp với danh mục 122 điểm CSGT & các tuyến đường hạt nhân (Priority 3)
    for spot in STREET_HOTSPOTS:
        for kw in spot.get("keywords", []):
            kw_clean = kw.strip()
            if kw_clean.isdigit() or len(kw_clean) <= 2:
                continue
            pattern = r'(?:\b|^|#)' + re.escape(kw_clean) + r'(?:\b|$|[#\s.,!?])'
            if re.search(pattern, clean_text):
                if len(kw) > best_street_len:
                    best_street_len = len(kw)
                    st_name = spot.get("street") or spot.get("display_name", "")
                    best_street = {
                        "matched_keyword": kw,
                        "street": st_name,
                        "display_name": spot.get("display_name") or st_name,
                        "ward": spot.get("ward", ""),
                        "administrative_unit": spot.get("ward", ""),
                        "district": spot.get("district", "TP.HCM"), 
                        "region": spot.get("region", "TPHCM"),
                        "lat": spot["lat"],
                        "lon": spot["lon"],
                        "heat_points": spot.get("heat_points", [[spot["lat"], spot["lon"]]]),
                        "priority": 3,
                        "type": spot.get("type", f"Điểm cảnh báo tuyến đường {st_name}"),
                        "cause": spot.get("cause", "rain"),
                        "cause_label": spot.get("cause_label", "Mưa lớn, nước không thoát kịp"),
                        "source": spot.get("source", "csgt_or_seed")
                    }

    # 1.B: So khớp với bộ nhớ đệm tự học tuyến đường (Dynamic Cache)
    if not best_street:
        for cached_kw, cached_data in DYNAMIC_CACHE.items():
            ck_clean = cached_kw.strip()
            if ck_clean.isdigit() or len(ck_clean) <= 2:
                continue
            if any(bw in ck_clean for bw in BOGUS_ROAD_PHRASES):
                continue
            pattern = r'(?:\b|^|#)' + re.escape(ck_clean) + r'(?:\b|$|[#\s.,!?])'
            if re.search(pattern, clean_text):
                c_data = dict(cached_data)
                c_data["street"] = c_data.get("display_name", cached_kw)
                c_data["priority"] = 3
                best_street = c_data
                break

    # 1.C: Nhận diện thực thể tên đường mới qua ROAD_PATTERN & OSM Geocoding (Kiểm soát nghiêm ngặt)
    if not best_street:
        matches = ROAD_PATTERN.findall(text)
        for cand in matches:
            cleaned_cand = clean_road_candidate(cand)
            cand_low = cleaned_cand.lower()
            if len(cleaned_cand) < 4 or len(cleaned_cand.split()) > 5:
                continue
            if any(bw in cand_low for bw in BOGUS_ROAD_PHRASES):
                continue
            if any(sw in cand_low for sw in ["tp hcm", "tphcm", "sài gòn", "saigon", "ngập", "ngap", "này", "kia", "đó", "xe", "nhà", "lội", "loi", "tại", "tai", "thuộc", "trũng", "na3", "mưa", "khu vực", "khu vuc", "trung tâm", "trung tam", "mọi người", "moi nguoi", "cứu", "né"]):
                continue
            if cand_low in STOP_CANDIDATE_WORDS:
                continue
            dynamic_spot = geocode_osm_dynamic(cleaned_cand)
            if dynamic_spot:
                d_copy = dict(dynamic_spot)
                disp_n = d_copy.get("display_name", cleaned_cand)
                if any(bw in disp_n.lower() for bw in BOGUS_ROAD_PHRASES):
                    continue
                d_copy["street"] = disp_n
                d_copy["priority"] = 3
                best_street = d_copy
                break

    # KẾT QUẢ TẦNG 1: Nếu đã tìm thấy TÊN ĐƯỜNG -> Tuyến đường là YẾU TỐ CHÍNH!
    if best_street:
        # Nếu điểm đường này chưa có phường xác định (ví dụ đường mới phát hiện qua OSM):
        # Mới quét tìm xem bài viết có đề cập Phường / Xã cụ thể nào không
        # Ưu tiên Phường/Xã được nhắc trực tiếp trong bài viết
        for u in ADMIN_HOTSPOTS:
            for kw in u.get("keywords", []):
                pattern = r'(?:\b|^|#)' + re.escape(kw) + r'(?:\b|$|[#\s.,!?])'
                if re.search(pattern, clean_text):
                    best_street["ward"] = u["ward"]
                    best_street["administrative_unit"] = u["ward"]
                    best_street["district"] = u.get("district", best_street.get("district", "TP.HCM"))
                    break
        return _finalize_match(best_street)

    # =========================================================================
    # TẦNG 2: NẾU KHÔNG CÓ TÊN ĐƯỜNG -> SO KHỚP ĐƠN VỊ HÀNH CHÍNH (PHƯỜNG / XÃ)
    # =========================================================================
    best_ward = None
    best_ward_len = 0
    for u in ADMIN_HOTSPOTS:
        for kw in u.get("keywords", []):
            pattern = r'(?:\b|^|#)' + re.escape(kw) + r'(?:\b|$|[#\s.,!?])'
            if re.search(pattern, clean_text):
                if len(kw) > best_ward_len:
                    best_ward_len = len(kw)
                    best_ward = {
                        "matched_keyword": kw,
                        "street": "", # KHÔNG CÓ TÊN ĐƯỜNG
                        "display_name": u["display_name"],
                        "ward": u["ward"],
                        "administrative_unit": u["ward"],
                        "district": u.get("district", "TP.HCM"),
                        "region": "TPHCM",
                        "lat": u["lat"],
                        "lon": u["lon"],
                        "heat_points": [[u["lat"], u["lon"]]],
                        "priority": 2,
                        "type": u.get("type", f"Khu vực {u['ward']}"),
                        "cause": "rain",
                        "cause_label": "Khu vực địa giới hành chính",
                        "source": "admin_units_168"
                    }

    if best_ward:
        return _finalize_match(best_ward)

    # =========================================================================
    # TẦNG 3: NẾU KHÔNG CÓ CẢ ĐƯỜNG LẪN PHƯỜNG -> TOÀN THÀNH PHỐ / CẤP QUẬN
    # =========================================================================
    for out_loc in OUT_OF_SCOPE_LOCATIONS:
        pattern = r'(?:\b|^|#)' + re.escape(out_loc) + r'(?:\b|$|[#\s.,!?])'
        if re.search(pattern, clean_text):
            return None

    for spot in CITYWIDE_HOTSPOTS:
        for kw in spot.get("keywords", []):
            pattern = r'(?:\b|^|#)' + re.escape(kw) + r'(?:\b|$|[#\s.,!?])'
            if re.search(pattern, clean_text):
                res = dict(spot)
                res["street"] = ""
                res["priority"] = 1
                return _finalize_match(res)

    return None
