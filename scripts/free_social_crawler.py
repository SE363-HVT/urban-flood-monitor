"""
scripts/free_social_crawler.py
Công cụ cào dữ liệu mạng xã hội (TikTok & Facebook) hoàn toàn MIỄN PHÍ:
- 100% Zero-cost: Khai thác Google Discovery RSS Indexer kết hợp googlenewsdecoder.
- Chiến dịch mở rộng 50% Social Media:
  * Ma trận 40 Điểm nóng Ngập lụt biểu tượng của 24 quận huyện TP.HCM.
  * Bộ lọc đồng xuất hiện bắt buộc (Điểm nóng + Hành vi ngập lụt thực tế).
  * Bộ lọc chặn rác triệt để (không dính thể thao 'nước rút', PR doanh nghiệp, xây dựng, ngoại tỉnh).
- Tự động phân luồng vào từng thư mục Episode tương ứng trong data/raw/episodes/.
"""

import os
import sys
import json
import re
import time
import hashlib
import urllib.parse
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, Any, List, Set, Optional, Tuple

import feedparser
from googlenewsdecoder import gnewsdecoder

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
EPISODES_DIR = os.path.join(DATA_DIR, "raw", "episodes")

from core.gazetteer import normalize_text, HOTSPOTS, CSGT_HOTSPOTS, OUT_OF_SCOPE_LOCATIONS
from pipeline.event_processor import clean_stream_text, contains_spam_or_noise
from scripts.organize_raw_episodes import determine_episode_id, EPISODE_DEFINITIONS

# Danh sách từ khóa ngập lụt thực tế bắt buộc
FLOOD_INTENT_KEYWORDS = [
    "ngập", "ngap", "triều cường", "trieu cuong", "chết máy", "chet may",
    "bì bõm", "bi bom", "lội nước", "loi nuoc", "lút bánh", "lut banh",
    "nước dâng", "nuoc dang", "ngập sâu", "ngap sau", "biển nước", "bien nuoc",
    "thất thủ", "that thu", "ngập lụt", "ngap lut", "tràn vào nhà", "tran vao nha",
    "mênh mông nước", "sóng đánh", "ngập đường", "ngap duong", "dắt bộ", "dắt xe",
    "dẫn bộ", "xe chết máy", "ùn tắc do ngập", "ngập nặng", "ngap nang",
    "dự báo triều cường", "cảnh báo ngập", "mực nước triều", "đỉnh triều",
    "nước đã rút", "nước rút hết", "hết ngập", "đường khô ráo"
]

# Các từ khóa xác nhận địa bàn TP.HCM
HCMC_AFFIRMATION_KEYWORDS = [
    "tphcm", "tp.hcm", "tp hcm", "sài gòn", "sai gon", "hồ chí minh", "ho chi minh",
    "thủ đức", "thu duc", "bình thạnh", "binh thanh", "quận 7", "quan 7",
    "bình tân", "binh tan", "tân bình", "tan binh", "quận 8", "quan 8",
    "gò vấp", "go vap", "nhà bè", "nha be", "hóc môn", "hoc mon", "bình chánh",
    "quận 12", "quan 12", "quận 4", "quan 4", "quận 6", "quan 6", "tân phú",
    "trần xuân soạn", "huỳnh tấn phát", "quốc hương", "ung văn khiêm", "nguyễn văn quá",
    "nguyễn hữu cảnh", "phan huy ích", "lê văn lương", "tân hòa đông", "mễ cốc",
    "bến bình đông", "võ văn ngân", "kha vạn cân", "an phú", "thảo điền",
    "nguyễn xí", "đinh bộ lĩnh", "bạch đằng", "lương định của", "hồ học lãm",
    "bàu cát", "đồng đen", "đào sư tích", "phạm hữu lầu", "nguyễn bình",
    # Mở rộng TP.HCM mới (Bình Dương cũ & Bà Rịa - Vũng Tàu cũ)
    "bình dương", "binh duong", "thủ dầu một", "thu dau mot", "dĩ an", "di an", "thuận an", "thuan an",
    "bến cát", "ben cat", "tân uyên", "tan uyen", "đại lộ bình dương", "ngã tư 550", "cầu ông bố", "sóng thần",
    "vũng tàu", "vung tau", "bà rịa", "ba ria", "phú mỹ", "phu my", "côn đảo", "con dao", "thùy vân", "hạ long vũng tàu"
]

# Danh mục từ khóa rác / quảng cáo / thể thao / xây dựng cần loại trừ TUYỆT ĐỐI
JUNK_EXCLUSIONS = [
    "deal hot", "ngập trời", "giải mật", "hồ sơ giải mật", "nhà sách", "khai trương",
    "độc quyền trên", "series tập", "cánh sóng âm", "khuyến mãi", "sale sập sàn",
    "mực tím", "truyện hạt lúa", "cia sài gòn", "bán nhà", "cho thuê", "phòng trọ",
    "căn hộ", "vinhomes", "bánh mì", "xe lướt", "odo", "thi hộ", "học hộ",
    "pha nước rút", "chạy nước rút", "giai đoạn nước rút", "nước rút thi công",
    "tay đua", "cầu đi bộ", "nhựa duy tân", "duy tân", "cải tạo diện mạo",
    "hà nội", "mcer", "marie curie", "đà lạt", "đà nẵng", "hải phòng", "cần thơ",
    # Từ ngữ ẩn dụ / F&B / du lịch / đồ công nghệ
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
    # Ngoại tỉnh Đồng Nai
    "đồng nai", "phước tân", "biên hòa", "biên hoà", "cao tốc biên hòa", "long thành", "trảng bom", "nhơn trạch", "vĩnh cửu"
]

# Danh sách URL cần chặn triệt để
BLOCKED_URLS = [
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

# MA TRẬN TRUY VẤN MỞ RỘNG (40 ĐIỂM NÓNG NGẬP LỤT BIỂU TƯỢNG TP.HCM)
HOTSPOT_CRAWL_QUERIES = [
    # 1. Khu vực Quận 7 & Nhà Bè (Rốn triều cường)
    ('site:tiktok.com "Trần Xuân Soạn" "ngập"', "tiktok"),
    ('site:tiktok.com "Trần Xuân Soạn" "triều cường"', "tiktok"),
    ('site:tiktok.com "Huỳnh Tấn Phát" "ngập"', "tiktok"),
    ('site:tiktok.com "Huỳnh Tấn Phát" "triều cường"', "tiktok"),
    ('site:tiktok.com "Lê Văn Lương" "ngập"', "tiktok"),
    ('site:tiktok.com "Lê Văn Lương" "triều cường"', "tiktok"),
    ('site:tiktok.com "Đào Sư Tích" "ngập"', "tiktok"),
    ('site:tiktok.com "Phạm Hữu Lầu" "ngập"', "tiktok"),
    ('site:tiktok.com "Nguyễn Bình" "Nhà Bè" "ngập"', "tiktok"),
    ('site:tiktok.com "Quận 7" "triều cường" "ngập"', "tiktok"),
    ('site:tiktok.com "Nhà Bè" "triều cường" "ngập"', "tiktok"),

    ('site:facebook.com "Trần Xuân Soạn" "ngập"', "facebook"),
    ('site:facebook.com "Trần Xuân Soạn" "triều cường"', "facebook"),
    ('site:facebook.com "Huỳnh Tấn Phát" "ngập"', "facebook"),
    ('site:facebook.com "Huỳnh Tấn Phát" "triều cường"', "facebook"),
    ('site:facebook.com "Lê Văn Lương" "ngập"', "facebook"),
    ('site:facebook.com "Lê Văn Lương" "triều cường"', "facebook"),
    ('site:facebook.com "Đào Sư Tích" "ngập"', "facebook"),
    ('site:facebook.com "Phạm Hữu Lầu" "ngập"', "facebook"),
    ('site:facebook.com "Quận 7" "triều cường" "ngập nặng"', "facebook"),
    ('site:facebook.com "Nhà Bè" "triều cường dâng cao"', "facebook"),

    # 2. Khu vực Bình Thạnh (Rốn mưa & triều)
    ('site:tiktok.com "Ung Văn Khiêm" "ngập"', "tiktok"),
    ('site:tiktok.com "Nguyễn Xí" "ngập"', "tiktok"),
    ('site:tiktok.com "Đinh Bộ Lĩnh" "ngập"', "tiktok"),
    ('site:tiktok.com "Bạch Đằng" "Bình Thạnh" "ngập"', "tiktok"),
    ('site:tiktok.com "Nguyễn Hữu Cảnh" "ngập"', "tiktok"),
    ('site:tiktok.com "Hàng Xanh" "ngập"', "tiktok"),
    ('site:tiktok.com "Quốc lộ 13" "Bình Thạnh" "ngập"', "tiktok"),

    ('site:facebook.com "Ung Văn Khiêm" "ngập"', "facebook"),
    ('site:facebook.com "Nguyễn Xí" "ngập"', "facebook"),
    ('site:facebook.com "Đinh Bộ Lĩnh" "ngập"', "facebook"),
    ('site:facebook.com "Bạch Đằng" "Bình Thạnh" "ngập"', "facebook"),
    ('site:facebook.com "Nguyễn Hữu Cảnh" "ngập"', "facebook"),
    ('site:facebook.com "Bình Thạnh" "mưa ngập sâu"', "facebook"),

    # 3. Khu vực TP. Thủ Đức (Thảo Điền & Chợ Thủ Đức)
    ('site:tiktok.com "Quốc Hương" "ngập"', "tiktok"),
    ('site:tiktok.com "Nguyễn Văn Hưởng" "ngập"', "tiktok"),
    ('site:tiktok.com "Thảo Điền" "ngập"', "tiktok"),
    ('site:tiktok.com "Võ Văn Ngân" "ngập"', "tiktok"),
    ('site:tiktok.com "Kha Vạn Cân" "ngập"', "tiktok"),
    ('site:tiktok.com "Tô Ngọc Vân" "ngập"', "tiktok"),
    ('site:tiktok.com "Đặng Thị Rành" "ngập"', "tiktok"),
    ('site:tiktok.com "Lương Định Của" "ngập"', "tiktok"),
    ('site:tiktok.com "Trần Não" "ngập"', "tiktok"),
    ('site:tiktok.com "Chợ Thủ Đức" "ngập"', "tiktok"),

    ('site:facebook.com "Quốc Hương" "ngập"', "facebook"),
    ('site:facebook.com "Nguyễn Văn Hưởng" "ngập"', "facebook"),
    ('site:facebook.com "Thảo Điền" "ngập"', "facebook"),
    ('site:facebook.com "Võ Văn Ngân" "ngập"', "facebook"),
    ('site:facebook.com "Kha Vạn Cân" "ngập"', "facebook"),
    ('site:facebook.com "Tô Ngọc Vân" "ngập"', "facebook"),
    ('site:facebook.com "Lương Định Của" "ngập"', "facebook"),
    ('site:facebook.com "Chợ Thủ Đức" "ngập nước"', "facebook"),

    # 4. Khu vực Gò Vấp & Quận 12
    ('site:tiktok.com "Phan Huy Ích" "ngập"', "tiktok"),
    ('site:tiktok.com "Nguyễn Văn Khối" "ngập"', "tiktok"),
    ('site:tiktok.com "Cây Trâm" "ngập"', "tiktok"),
    ('site:tiktok.com "Lê Đức Thọ" "Gò Vấp" "ngập"', "tiktok"),
    ('site:tiktok.com "Phạm Văn Chiêu" "ngập"', "tiktok"),
    ('site:tiktok.com "Nguyễn Văn Quá" "ngập"', "tiktok"),
    ('site:tiktok.com "Song Hành" "Quận 12" "ngập"', "tiktok"),

    ('site:facebook.com "Phan Huy Ích" "ngập"', "facebook"),
    ('site:facebook.com "Nguyễn Văn Khối" "ngập"', "facebook"),
    ('site:facebook.com "Cây Trâm" "ngập"', "facebook"),
    ('site:facebook.com "Lê Đức Thọ" "Gò Vấp" "ngập"', "facebook"),
    ('site:facebook.com "Phạm Văn Chiêu" "ngập"', "facebook"),
    ('site:facebook.com "Nguyễn Văn Quá" "ngập"', "facebook"),
    ('site:facebook.com "Quận 12" "mưa ngập nặng"', "facebook"),

    # 5. Khu vực Quận 8 & Bình Tân & Tân Bình
    ('site:tiktok.com "Mễ Cốc" "ngập"', "tiktok"),
    ('site:tiktok.com "Bến Bình Đông" "ngập"', "tiktok"),
    ('site:tiktok.com "Bến Phú Định" "ngập"', "tiktok"),
    ('site:tiktok.com "Tân Hòa Đông" "ngập"', "tiktok"),
    ('site:tiktok.com "Kinh Dương Vương" "ngập"', "tiktok"),
    ('site:tiktok.com "Hồ Học Lãm" "ngập"', "tiktok"),
    ('site:tiktok.com "An Dương Vương" "ngập"', "tiktok"),
    ('site:tiktok.com "Đồng Đen" "ngập"', "tiktok"),
    ('site:tiktok.com "Bàu Cát" "ngập"', "tiktok"),
    ('site:tiktok.com "Phan Anh" "Bình Tân" "ngập"', "tiktok"),

    ('site:facebook.com "Mễ Cốc" "ngập"', "facebook"),
    ('site:facebook.com "Bến Bình Đông" "ngập"', "facebook"),
    ('site:facebook.com "Bến Phú Định" "ngập"', "facebook"),
    ('site:facebook.com "Tân Hòa Đông" "ngập"', "facebook"),
    ('site:facebook.com "Kinh Dương Vương" "ngập"', "facebook"),
    ('site:facebook.com "Hồ Học Lãm" "ngập"', "facebook"),
    ('site:facebook.com "An Dương Vương" "ngập"', "facebook"),
    ('site:facebook.com "Đồng Đen" "ngập"', "facebook"),
    ('site:facebook.com "Bàu Cát" "ngập"', "facebook"),
    ('site:facebook.com "Phan Anh" "ngập"', "facebook"),

    # 6. Truy vấn cộng đồng & tình huống hiện trường
    ('site:tiktok.com "mưa ngập" "Sài Gòn"', "tiktok"),
    ('site:tiktok.com "triều cường" "Sài Gòn"', "tiktok"),
    ('site:tiktok.com "xe chết máy" "ngập" "TPHCM"', "tiktok"),
    ('site:tiktok.com "ngập lút bánh" "TPHCM"', "tiktok"),
    ('site:tiktok.com "bì bõm" "lội nước" "Sài Gòn"', "tiktok"),
    ('site:tiktok.com "nước tràn vào nhà" "TPHCM"', "tiktok"),

    ('site:facebook.com "triều cường đạt đỉnh" "TPHCM"', "facebook"),
    ('site:facebook.com "mưa lớn gây ngập" "Sài Gòn"', "facebook"),
    ('site:facebook.com "đường ngập" "chết máy" "TPHCM"', "facebook"),
    ('site:facebook.com "triều cường dâng cao" "Sài Gòn"', "facebook"),
    ('site:facebook.com "dắt bộ bì bõm" "Sài Gòn"', "facebook"),
    ('site:facebook.com "Sài Gòn ngập như sông"', "facebook"),
    # 7. Mở rộng Bình Dương (Bình Dương cũ - TP.HCM Mới)
    ('site:tiktok.com "Dĩ An" "ngập"', "tiktok"),
    ('site:tiktok.com "Thuận An" "ngập"', "tiktok"),
    ('site:tiktok.com "Thủ Dầu Một" "ngập"', "tiktok"),
    ('site:tiktok.com "Đại lộ Bình Dương" "ngập"', "tiktok"),
    ('site:tiktok.com "Bình Dương" "mưa ngập"', "tiktok"),
    ('site:tiktok.com "Bình Dương" "ngập sâu"', "tiktok"),
    ('site:facebook.com "Dĩ An" "ngập"', "facebook"),
    ('site:facebook.com "Thuận An" "ngập"', "facebook"),
    ('site:facebook.com "Thủ Dầu Một" "ngập"', "facebook"),
    ('site:facebook.com "Đại lộ Bình Dương" "ngập"', "facebook"),
    ('site:facebook.com "Bình Dương" "mưa ngập"', "facebook"),

    # 8. Mở rộng Bà Rịa - Vũng Tàu (Bà Rịa - Vũng Tàu cũ - TP.HCM Mới)
    ('site:tiktok.com "Vũng Tàu" "ngập"', "tiktok"),
    ('site:tiktok.com "Vũng Tàu" "triều cường"', "tiktok"),
    ('site:tiktok.com "Vũng Tàu" "mưa ngập"', "tiktok"),
    ('site:tiktok.com "Bà Rịa" "ngập"', "tiktok"),
    ('site:tiktok.com "Phú Mỹ" "ngập"', "tiktok"),
    ('site:facebook.com "Vũng Tàu" "ngập"', "facebook"),
    ('site:facebook.com "Vũng Tàu" "triều cường"', "facebook"),
    ('site:facebook.com "Vũng Tàu" "mưa lớn ngập"', "facebook"),
    ('site:facebook.com "Bà Rịa" "ngập"', "facebook"),
]


def load_existing_identifiers() -> Tuple[Set[str], Set[str]]:
    """Tải toàn bộ URL và MD5 hash đã tồn tại trong toàn bộ hệ thống để chống trùng lặp."""
    seen_urls = set()
    seen_hashes = set()

    # Quét trong data/raw/episodes/
    if os.path.exists(EPISODES_DIR):
        for root, _, files in os.walk(EPISODES_DIR):
            for f in files:
                if f.endswith("_raw.json"):
                    fpath = os.path.join(root, f)
                    try:
                        with open(fpath, "r", encoding="utf-8-sig") as fp:
                            items = json.load(fp)
                            if isinstance(items, list):
                                for it in items:
                                    u = it.get("url") or it.get("webVideoUrl") or it.get("link") or ""
                                    if u:
                                        seen_urls.add(u)
                                    t = it.get("text") or it.get("caption") or it.get("title") or ""
                                    if t:
                                        seen_hashes.add(hashlib.md5(t.strip().lower().encode("utf-8")).hexdigest())
                    except Exception:
                        pass

    # Quét trong dataset v1 và v2
    for vf in ["hcmc_flood_annotated_v1.json", "hcmc_flood_annotated_v2_multimodal.json"]:
        v_file = os.path.join(DATA_DIR, "processed", vf)
        if os.path.exists(v_file):
            try:
                with open(v_file, "r", encoding="utf-8") as fp:
                    v_items = json.load(fp)
                    for it in v_items:
                        src_url = it.get("source", {}).get("url") or ""
                        if src_url:
                            seen_urls.add(src_url)
                        txt = it.get("content", {}).get("text") or ""
                        if txt:
                            seen_hashes.add(hashlib.md5(txt.strip().lower().encode("utf-8")).hexdigest())
            except Exception:
                pass

    return seen_urls, seen_hashes


def is_valid_hcmc_flood_content(title_or_snippet: str) -> bool:
    """Kiểm tra nghiêm ngặt tính hợp lệ của nội dung ngập lụt TP.HCM."""
    clean = clean_stream_text(title_or_snippet)
    if not clean or len(clean) < 15:
        return False

    clean_low = clean.lower()

    # 1. Loại trừ tin rác bất động sản / quảng cáo / giải mật / thể thao / thi công
    if contains_spam_or_noise(clean):
        return False
    for junk in JUNK_EXCLUSIONS:
        if junk in clean_low:
            return False

    # 2. Loại trừ tỉnh ngoài rõ rệt
    for out_loc in OUT_OF_SCOPE_LOCATIONS:
        pat = r'(?:\b|^|#)' + re.escape(out_loc) + r'(?:\b|$|[#\s.,!?])'
        if re.search(pat, clean_low):
            if not any(k in clean_low for k in ["tphcm", "tp hcm", "sài gòn", "sai gon", "bình dương", "binh duong", "vũng tàu", "vung tau", "bà rịa"]):
                return False

    # 3. Phải có từ khóa ngập lụt thực tế
    has_flood = any(k in clean_low for k in FLOOD_INTENT_KEYWORDS)
    if not has_flood:
        return False

    # 4. Phải có từ khóa khẳng định địa bàn TP.HCM hoặc điểm nóng TP.HCM
    has_hcmc = any(k in clean_low for k in HCMC_AFFIRMATION_KEYWORDS)
    if not has_hcmc:
        has_hotspot = any(
            any(kw in clean_low for kw in spot.get("keywords", []))
            for spot in HOTSPOTS[:80]
        )
        if not has_hotspot:
            return False

    return True


def parse_rfc822_date(date_str: str) -> Tuple[Optional[str], Optional[str]]:
    """Chuyển đổi ngày định dạng RSS sang YYYY-MM-DD và ISO-8601."""
    if not date_str:
        return None, None
    try:
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%d"), dt.isoformat()
    except Exception:
        pass
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d"), dt.isoformat()
    except Exception:
        return None, None


def extract_author_and_id_from_url(url: str, platform: str) -> Tuple[str, str]:
    """Trích xuất username và post/video ID từ URL TikTok/Facebook."""
    author = f"{platform.capitalize()} Creator"
    item_id = hashlib.md5(url.encode("utf-8")).hexdigest()[:16]

    if platform == "tiktok":
        m_user = re.search(r'@([a-zA-Z0-9_.-]+)', url)
        if m_user:
            author = m_user.group(1)
        m_vid = re.search(r'/video/(\d+)', url)
        if m_vid:
            item_id = m_vid.group(1)

    elif platform == "facebook":
        m_page = re.search(r'facebook\.com/([^/?#]+)', url)
        if m_page and m_page.group(1) not in ["groups", "watch", "reel", "story.php", "permalink.php"]:
            author = m_page.group(1)
        m_post = re.search(r'/(?:posts|videos|reel)/([a-zA-Z0-9_.-]+)', url)
        if m_post:
            item_id = m_post.group(1)

    return author, item_id


def run_free_social_crawler(max_per_query: int = 50):
    print("=" * 80)
    print("KHỞI ĐỘNG CÀO DỮ LIỆU TIKTOK & FACEBOOK ĐẨY SOCIAL LÊN 50% (CHUẨN 40 ĐIỂM NÓNG)")
    print("=" * 80)

    seen_urls, seen_hashes = load_existing_identifiers()
    print(f"-> Đã nạp {len(seen_urls)} URLs và {len(seen_hashes)} content hashes hiện có để chống trùng lặp.")

    new_items_by_episode = defaultdict(lambda: defaultdict(list))
    total_found = 0
    total_added = 0
    duplicate_count = 0
    filtered_count = 0

    for q_idx, (query, platform) in enumerate(HOTSPOT_CRAWL_QUERIES, start=1):
        print(f"\n[{q_idx}/{len(HOTSPOT_CRAWL_QUERIES)}] Truy vấn: {query} ({platform.upper()})...")
        enc_q = urllib.parse.quote_plus(query)
        feed_url = f"https://news.google.com/rss/search?q={enc_q}&hl=vi&gl=VN&ceid=VN:vi"

        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"  Lỗi khi gọi RSS feed: {e}")
            continue

        entries = feed.entries[:max_per_query]
        print(f"  -> Nhận được {len(entries)} kết quả từ công cụ tìm kiếm.")

        for entry in entries:
            total_found += 1
            raw_title = getattr(entry, "title", "") or ""
            raw_summary = getattr(entry, "summary", "") or ""
            full_snippet = f"{raw_title}. {raw_summary}".strip()

            clean_title = re.sub(r'\s*-\s*(?:TikTok|Facebook)\s*$', '', raw_title, flags=re.IGNORECASE).strip()

            # 1. Kiểm duyệt nội dung nghiêm ngặt
            if not is_valid_hcmc_flood_content(clean_title) and not is_valid_hcmc_flood_content(full_snippet):
                filtered_count += 1
                continue

            # 2. Khử trùng lặp qua văn bản
            c_hash = hashlib.md5(clean_title.lower().encode("utf-8")).hexdigest()
            if c_hash in seen_hashes:
                duplicate_count += 1
                continue

            # 3. Giải mã liên kết gốc sang TikTok / Facebook
            rss_link = getattr(entry, "link", "")
            if not rss_link:
                continue

            try:
                decoded = gnewsdecoder(rss_link)
                decoded_url = decoded.get("decoded_url") if isinstance(decoded, dict) else decoded
            except Exception:
                decoded_url = ""

            if not decoded_url or not isinstance(decoded_url, str):
                continue

            # Kiểm tra URL bị chặn hoặc trùng lặp
            if any(b in decoded_url for b in BLOCKED_URLS):
                continue
            if decoded_url in seen_urls:
                duplicate_count += 1
                continue

            # Chỉ giữ URL thuộc đúng nền tảng
            if platform == "tiktok" and "tiktok.com" not in decoded_url.lower():
                continue
            if platform == "facebook" and "facebook.com" not in decoded_url.lower():
                continue

            # Đánh dấu đã thấy
            seen_urls.add(decoded_url)
            seen_hashes.add(c_hash)

            # 4. Trích xuất thời gian và xác định Episode
            pub_date_raw = getattr(entry, "published", "")
            d_str, iso_str = parse_rfc822_date(pub_date_raw)
            if not d_str:
                d_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                iso_str = datetime.now(timezone.utc).isoformat()

            ep_id = determine_episode_id(d_str)

            # 5. Bóc tách Author & ID
            author_name, post_id = extract_author_and_id_from_url(decoded_url, platform)

            # Cấu trúc bản ghi thô chuẩn mực
            raw_record = {
                "id": post_id,
                "url": decoded_url,
                "webVideoUrl": decoded_url if platform == "tiktok" else "",
                "mediaUrls": [decoded_url] if platform == "tiktok" else [],
                "text": clean_title,
                "title": clean_title,
                "author": author_name,
                "authorMeta": {"name": author_name},
                "createTimeISO": iso_str,
                "published": pub_date_raw,
                "extracted_date": d_str,
                "platform": platform,
                "crawled_at": datetime.now(timezone.utc).isoformat(),
                "crawler_source": "free_discovery_engine"
            }

            new_items_by_episode[ep_id][platform].append(raw_record)
            total_added += 1

        time.sleep(0.4)

    print("\n" + "=" * 80)
    print("HOÀN TẤT THU THẬP TỰ ĐỘNG. ĐANG LƯU VÀO CÁC PHÂN VÙNG EPISODE:")
    print(f"  * Tổng số ứng viên quét: {total_found}")
    print(f"  * Bị loại bỏ do không hợp lệ/ngoại tỉnh/rác: {filtered_count}")
    print(f"  * Bị loại bỏ do trùng lặp (URL hoặc nội dung): {duplicate_count}")
    print(f"  * SỐ BÀI ĐĂNG MỚI ĐẠT CHUẨN THÊM VÀO: {total_added}")
    print("=" * 80)

    # 6. Ghi nối tiếp vào các file tương ứng trong data/raw/episodes/
    for ep_id, platforms in new_items_by_episode.items():
        ep_dir = os.path.join(EPISODES_DIR, ep_id)
        os.makedirs(ep_dir, exist_ok=True)

        for platform, items in platforms.items():
            raw_fname = f"{platform}_raw.json"
            target_path = os.path.join(ep_dir, raw_fname)

            existing_items = []
            if os.path.exists(target_path):
                try:
                    with open(target_path, "r", encoding="utf-8-sig") as fp:
                        existing_items = json.load(fp)
                        if not isinstance(existing_items, list):
                            existing_items = []
                except Exception:
                    existing_items = []

            # Hợp nhất và chống trùng lặp theo ID/URL
            merged_dict = {}
            for it in existing_items:
                uid = it.get("url") or it.get("id")
                if uid:
                    merged_dict[uid] = it
            for it in items:
                uid = it.get("url") or it.get("id")
                if uid:
                    merged_dict[uid] = it

            final_list = list(merged_dict.values())
            with open(target_path, "w", encoding="utf-8") as fp:
                json.dump(final_list, fp, ensure_ascii=False, indent=2)

            print(f"  + [{ep_id}] {platform.upper()}: Thêm {len(items)} bài -> Tổng cộng: {len(final_list)} bài ({raw_fname})")

    print("\n-> Đã cập nhật toàn bộ vào cấu trúc phân vùng Episode!")


if __name__ == "__main__":
    run_free_social_crawler(max_per_query=50)
