# -*- coding: utf-8 -*-
"""
scripts/free_social_crawler.py
Công cụ cào dữ liệu mạng xã hội đa kênh (TikTok, Facebook, Threads, YouTube Shorts, News) hoàn toàn MIỄN PHÍ:
- 100% Zero-cost: Khai thác Google Discovery RSS Indexer kết hợp googlenewsdecoder.
- Hỗ trợ 5 nền tảng:
  1. TikTok Video Posts (site:tiktok.com)
  2. Facebook Public Posts / Pages / Groups (site:facebook.com)
  3. Threads Posts (site:threads.net - Radar cảm xúc & đời thường)
  4. YouTube Shorts Video Clip (site:youtube.com/shorts - Clip dọc hiện trường)
  5. Báo chí Chính thống (News)
- Mở rộng quy mô lớn không giới hạn thời gian (Historical Multi-Year Coverage 2018-2025).
- Ma trận truy vấn đa tầng quét toàn diện 168 phường xã và 40 điểm nóng ngập lụt TP.HCM.
- Bộ lọc đồng xuất hiện bắt buộc (Điểm nóng + Hành vi ngập lụt thực tế).
- Bộ lọc chặn rác triệt để (không dính thể thao 'nước rút', PR doanh nghiệp, bất động sản, F&B, ngoại tỉnh).
- Tự động phân luồng vào từng thư mục Episode tương ứng trong data/raw/episodes/.
- Xử lý đa luồng ThreadPoolExecutor tăng tốc cào dữ liệu.
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
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Set, Optional, Tuple

import feedparser
from googlenewsdecoder import gnewsdecoder

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
EPISODES_DIR = os.path.join(DATA_DIR, "raw", "episodes")

from core.gazetteer import normalize_text, HOTSPOTS, CSGT_HOTSPOTS, OUT_OF_SCOPE_LOCATIONS
from pipeline.event_processor import clean_stream_text, contains_spam_or_noise
from scripts.crawlers.organize_raw_episodes import determine_episode_id, EPISODE_DEFINITIONS

# Danh sách từ khóa ngập lụt thực tế bắt buộc
DIRECT_FLOOD_KEYWORDS = [
    "ngập", "ngap", "triều cường", "trieu cuong", "lội nước", "loi nuoc", "bì bõm", "bi bom",
    "lút bánh", "lut banh", "nước dâng", "nuoc dang", "ngập sâu", "ngap sau", "biển nước", "bien nuoc",
    "ngập lụt", "ngap lut", "tràn vào nhà", "tran vao nha", "mênh mông nước", "sóng đánh vào nhà",
    "ngập đường", "ngap duong", "ngập nặng", "ngap nang", "mực nước triều", "đỉnh triều",
    "ngập nửa bánh", "lút bô", "lut bo", "lút ống xả", "đường hóa sông", "duong hoa song",
    "đường thành sông", "ngập lênh láng", "chìm trong biển nước", "hộc nước",
    "nước ngập tới đầu gối", "ngập ngang xe", "dự báo triều cường", "cảnh báo ngập",
    "nước đã rút", "nước rút hết", "hết ngập", "đường khô ráo", "nước rút nhanh"
]

BEHAVIORAL_FLOOD_KEYWORDS = [
    "chết máy", "chet may", "dắt bộ", "dat bo", "dắt xe", "dat xe", "dẫn bộ",
    "thất thủ", "that thu", "chết bu-gi", "chet bu gi", "quay đầu xe",
    "không đi được", "khong di duoc", "té xe", "te xe", "ngã xe", "đẩy bộ", "day bo",
    "nước tràn vào nhà", "sóng đánh", "sóng tạt", "sóng dập", "sóng tràn", "hết lối đi",
    "bơi về nhà", "boi ve nha", "lội bì bõm", "xe tắt máy", "xe tat may"
]

FLOOD_INTENT_KEYWORDS = DIRECT_FLOOD_KEYWORDS + BEHAVIORAL_FLOOD_KEYWORDS

# Các từ khóa xác nhận địa bàn TP.HCM
HCMC_AFFIRMATION_KEYWORDS = [
    "tphcm", "tp.hcm", "tp hcm", "sài gòn", "sai gon", "hồ chí minh", "ho chi minh",
    "thủ đức", "thu duc", "bình thạnh", "binh thanh", "quận 7", "quan 7",
    "bình tân", "binh tan", "tân bình", "tan binh", "quận 8", "quan 8",
    "gò vấp", "go vap", "nhà bè", "nha be", "hóc môn", "hoc mon", "bình chánh",
    "quận 12", "quan 12", "quận 4", "quan 4", "quận 6", "quan 6", "tân phú",
    "trần xuân soạn", "huỳnh tấn phát", "quốc hương", "ung văn khiêm", "nguyễn văn quá",
    "nguyễn hữu cảnh", "phan huy ích", "lê văn lương", "tân hòa đông", "mễ cốc",
    "bến bình đông", "bến phú định", "võ văn ngân", "kha vạn cân", "an phú", "thảo điền",
    "nguyễn xí", "đinh bộ lĩnh", "bạch đằng", "lương định của", "hồ học lãm",
    "bàu cát", "đồng đen", "đào sư tích", "phạm hữu lầu", "nguyễn bình", "mã lò", "lê lai",
    "bình dương", "dĩ an", "thuận an", "thủ dầu một", "vũng tàu", "bà rịa"
]

# Danh mục từ khóa rác / quảng cáo / thể thao / F&B / bất động sản cần loại trừ TUYỆT ĐỐI
JUNK_EXCLUSIONS = [
    "deal hot", "ngập trời", "giải mật", "hồ sơ giải mật", "nhà sách", "khai trương",
    "độc quyền trên", "series tập", "cánh sóng âm", "khuyến mãi", "sale sập sàn",
    "mực tím", "truyện hạt lúa", "cia sài gòn", "bán nhà", "cho thuê", "phòng trọ",
    "căn hộ", "vinhomes", "bánh mì", "xe lướt", "odo", "thi hộ", "học hộ",
    "pha nước rút", "chạy nước rút", "giai đoạn nước rút", "nước rút thi công",
    "tay đua", "cầu đi bộ", "nhựa duy tân", "duy tân", "cải tạo diện mạo",
    "hà nội", "mcer", "marie curie", "đà lạt", "đà nẵng", "hải phòng", "cần thơ",
    "ngập dầu", "ngập bơ", "ngập mỡ", "ngập tràn deal", "ngập tràn may mắn",
    "ngập tràn ưu đãi", "ngập tràn quà", "ngập tràn ánh sáng", "ngập tràn niềm vui",
    "ngập tràn tiếng cười", "ngập tràn hạnh phúc", "ngập tràn hy vọng", "ngập tràn năng lượng",
    "lục bình", "bãi tắm", "rác biển", "bánh khọt", "cellphones", "sắm tết",
    "chúc khách", "tiệm ăn", "mì cay", "quán chay", "sạc xanh", "ev one", "vi vu vũng tàu lễ",
    "ngập tràn tết", "shop bí", "ngập ánh sáng", "tràn ngập ánh sáng", "ngập nắng", "view chill ngập",
    "ngập dâu sữa", "ngập quà", "shin-chan", "thông cống nghẹt", "hút hầm cầu", "thông nghẹt",
    "bảo dưỡng xe máy", "thủy kích", "chung cư mini", "căn duplex", "studio ban công",
    "hết xăng", "hỏng ắc quy", "ắc quy", "bóng đá", "tuyển dụng", "tử vi", "giá vàng"
]

BLOCKED_URLS = [
    "vovgiaothong.vn", "plo.vn/thoi-tiet", "accuweather.com", "weather.com",
    "tinhte.vn", "kenh14.vn/fashion", "webtretho.com", "batdongsan.com.vn",
    "chotot.com", "nhatot.com"
]

# ==============================================================================
# MA TRẬN TRUY VẤN MỞ RỘNG ĐA NỀN TẢNG (TIKTOK, FACEBOOK, THREADS, YOUTUBE SHORTS, NEWS)
# KHÔNG GIỚI HẠN THỜI GIAN ĐỂ THU THẬP TỐI ĐA DỮ LIỆU LỊCH SỬ VÀ HIỆN TẠI (2018-2025)
# ==============================================================================

def generate_expanded_crawl_queries() -> List[Tuple[str, str]]:
    queries = []

    # 1. TIKTOK QUERIES (Video ngắn, phản ánh thực địa)
    tiktok_hotspots = [
        "Trần Xuân Soạn", "Huỳnh Tấn Phát", "Lê Văn Lương", "Đào Sư Tích", "Nguyễn Bình",
        "Ung Văn Khiêm", "Nguyễn Xí", "Đinh Bộ Lĩnh", "Bạch Đằng", "Nguyễn Hữu Cảnh",
        "Quốc Hương", "Nguyễn Văn Hưởng", "Thảo Điền", "Võ Văn Ngân", "Kha Vạn Cân",
        "Tô Ngọc Vân", "Đặng Thị Rành", "Lương Định Của", "Hồ Học Lãm", "An Dương Vương",
        "Kinh Dương Vương", "Phan Huy Ích", "Nguyễn Văn Khối", "Lê Đức Thọ", "Cây Trâm",
        "Phạm Văn Chiêu", "Đỗ Xuân Hợp", "Dương Văn Cam", "Lê Thị Hoa", "Phạm Văn Đồng",
        "Bến Phú Định", "Mễ Cốc", "Nguyễn Duy", "Phạm Thế Hiển", "Lê Lai", "Mã Lò",
        "Tân Hòa Đông", "Bình Quới", "Quốc lộ 13", "Quốc lộ 50"
    ]
    for spot in tiktok_hotspots:
        queries.append((f'site:tiktok.com "{spot}" "ngập"', "tiktok"))
        queries.append((f'site:tiktok.com "{spot}" "triều cường"', "tiktok"))
    
    # TikTok Tổng quát & Đa năm (2021-2025)
    queries.extend([
        ('site:tiktok.com ("ngập" OR "ngập lụt") ("Sài Gòn" OR "TPHCM")', "tiktok"),
        ('site:tiktok.com ("triều cường" OR "mưa lớn ngập") "TPHCM"', "tiktok"),
        ('site:tiktok.com ("xe chết máy" OR "lội nước" OR "bì bõm") "ngập"', "tiktok"),
        ('site:tiktok.com ("Sài Gòn thất thủ" OR "đường thành sông")', "tiktok"),
        ('site:tiktok.com ("nước tràn vào nhà" OR "sóng đánh") ("Sài Gòn" OR "TP.HCM")', "tiktok"),
        ('site:tiktok.com "chợ Thủ Đức" "ngập sâu"', "tiktok"),
        ('site:tiktok.com "nước rút nhanh" ("Sài Gòn" OR "TPHCM")', "tiktok"),
        ('site:tiktok.com ("hết ngập" OR "đường khô ráo") "TPHCM"', "tiktok")
    ])
    for yr in [2021, 2022, 2023, 2024, 2025]:
        queries.append((f'site:tiktok.com "ngập" "Sài Gòn" {yr}', "tiktok"))
        queries.append((f'site:tiktok.com "ngập" "TPHCM" {yr}', "tiktok"))
        queries.append((f'site:tiktok.com "triều cường" "Sài Gòn" {yr}', "tiktok"))
        queries.append((f'site:tiktok.com "xe chết máy" "ngập" {yr}', "tiktok"))
        queries.append((f'site:tiktok.com "Trần Xuân Soạn" "ngập" {yr}', "tiktok"))
        queries.append((f'site:tiktok.com "Thảo Điền" "ngập" {yr}', "tiktok"))

    # 2. FACEBOOK QUERIES (Bài đăng, trang cộng đồng, nhóm cư dân) - Multi-Year 2018-2025
    for spot in tiktok_hotspots:
        queries.append((f'site:facebook.com "{spot}" "ngập"', "facebook"))
    queries.extend([
        ('site:facebook.com ("ngập" OR "ngập nước") ("TPHCM" OR "Sài Gòn")', "facebook"),
        ('site:facebook.com ("triều cường" OR "mưa ngập") ("TP.HCM" OR "Sài Gòn")', "facebook"),
        ('site:facebook.com ("xe chết máy" OR "lội nước" OR "bì bõm" OR "lút bánh") "ngập"', "facebook"),
        ('site:facebook.com ("nước tràn vào nhà" OR "đường thành sông" OR "sóng đánh") ("Sài Gòn" OR "TPHCM")', "facebook"),
        ('site:facebook.com/groups ("đường ngập" OR "kẹt xe" OR "nước ngập") "TPHCM"', "facebook"),
        ('site:facebook.com/groups ("chết máy" OR "ngập nước" OR "triều cường")', "facebook"),
        ('site:facebook.com ("Sài Gòn thất thủ" OR "TPHCM ngập")', "facebook"),
        ('site:facebook.com ("dắt bộ" OR "xe tắt máy") ("đường ngập" OR "nước ngập")', "facebook"),
        ('site:facebook.com ("đỉnh triều" OR "triều cường đạt đỉnh") "TPHCM"', "facebook"),
        ('site:facebook.com ("công trình chống ngập" OR "trạm bơm" OR "thoát nước tốt") "TPHCM"', "facebook")
    ])
    years = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
    for yr in years:
        queries.append((f'site:facebook.com "ngập" "Sài Gòn" {yr}', "facebook"))
        queries.append((f'site:facebook.com "ngập" "TPHCM" {yr}', "facebook"))
        queries.append((f'site:facebook.com "triều cường" "Sài Gòn" {yr}', "facebook"))
        queries.append((f'site:facebook.com "xe chết máy" "ngập" {yr}', "facebook"))
        queries.append((f'site:facebook.com "nước tràn vào nhà" {yr}', "facebook"))
        queries.append((f'site:facebook.com "Sài Gòn thất thủ" {yr}', "facebook"))
        queries.append((f'site:facebook.com "Trần Xuân Soạn" "ngập" {yr}', "facebook"))
        queries.append((f'site:facebook.com "Huỳnh Tấn Phát" "ngập" {yr}', "facebook"))
        queries.append((f'site:facebook.com "Nguyễn Văn Quá" "ngập" {yr}', "facebook"))
        queries.append((f'site:facebook.com "Võ Văn Ngân" "ngập" {yr}', "facebook"))
        queries.append((f'site:facebook.com "Thảo Điền" "ngập" {yr}', "facebook"))

    # 3. THREADS QUERIES (Radar cảm xúc, than vãn giờ tan tầm, ngôn ngữ đời thường)
    threads_topics = [
        'site:threads.net ("ngập" OR "ngập lụt") ("Sài Gòn" OR "TPHCM")',
        'site:threads.net ("bơi về nhà" OR "xe chết máy") ("Sài Gòn" OR "TPHCM")',
        'site:threads.net ("mưa to" AND "ngập") ("Sài Gòn" OR "TPHCM")',
        'site:threads.net ("lội nước" OR "bì bõm" OR "lút bánh") ("Sài Gòn" OR "TP.HCM")',
        'site:threads.net ("combo mưa ngập" OR "Sài Gòn thất thủ")',
        'site:threads.net ("triều cường" AND "ngập") "TPHCM"',
        'site:threads.net "Thảo Điền" "ngập"',
        'site:threads.net ("Trần Xuân Soạn" OR "Huỳnh Tấn Phát") "ngập"',
        'site:threads.net ("Ung Văn Khiêm" OR "D2" OR "Nguyễn Xí") "ngập"',
        'site:threads.net ("Nguyễn Văn Quá" OR "Phan Huy Ích") "ngập"',
        'site:threads.net ("Võ Văn Ngân" OR "Thủ Đức") "ngập"',
        'site:threads.net ("Kinh Dương Vương" OR "Hồ Học Lãm") "ngập"',
        'site:threads.net ("nước rút lẹ" OR "không còn ngập" OR "thoát nước tốt") "Sài Gòn"',
        'site:threads.net ("dắt bộ cả cây số" OR "xe chết máy hàng loạt")',
        'site:threads.net ("sóng tạt vào nhà" OR "nước ngập tới đùi") "Sài Gòn"'
    ]
    for q in threads_topics:
        queries.append((q, "threads"))

    # 4. YOUTUBE SHORTS QUERIES (Video dọc hiện trường) - Multi-Year 2021-2025
    youtube_topics = [
        'site:youtube.com/shorts ("ngập" OR "ngập lụt") ("Sài Gòn" OR "TPHCM")',
        'site:youtube.com/shorts ("triều cường" OR "nước dâng") "TPHCM"',
        'site:youtube.com/shorts ("xe chết máy" OR "lội nước") "ngập"',
        'site:youtube.com/shorts ("đường ngập" OR "nước tràn vào nhà") "Sài Gòn"',
        'site:youtube.com/shorts "Trần Xuân Soạn" "ngập"',
        'site:youtube.com/shorts "Thảo Điền" "ngập"',
        'site:youtube.com/shorts "Nguyễn Văn Quá" "ngập"',
        'site:youtube.com/shorts "Võ Văn Ngân" "ngập"',
        'site:youtube.com/shorts "chợ Thủ Đức" "ngập"',
        'site:youtube.com/shorts "Huỳnh Tấn Phát" "triều cường"',
        'site:youtube.com ("mưa lớn gây ngập" OR "triều cường dâng cao") "TPHCM"',
        'site:youtube.com ("đường thành sông" OR "hàng loạt xe chết máy") "TPHCM"'
    ]
    for q in youtube_topics:
        queries.append((q, "youtube"))
    for yr in [2021, 2022, 2023, 2024, 2025]:
        queries.append((f'site:youtube.com/shorts "ngập" "Sài Gòn" {yr}', "youtube"))
        queries.append((f'site:youtube.com/shorts "triều cường" "TPHCM" {yr}', "youtube"))
        queries.append((f'site:youtube.com/shorts "xe chết máy" "ngập" {yr}', "youtube"))
        queries.append((f'site:youtube.com/shorts "Trần Xuân Soạn" "ngập" {yr}', "youtube"))

    # 5. NEWS QUERIES (Báo chí chính thống)
    news_topics = [
        '("ngập sâu" OR "triều cường đạt đỉnh") "TPHCM" (site:tuoitre.vn OR site:thanhnien.vn OR site:vnexpress.net)',
        '("xe chết máy" OR "đường biến thành sông") "TP.HCM" (site:dantri.com.vn OR site:plo.vn OR site:nld.com.vn)',
        '("dự án chống ngập" OR "nâng nền thoát nước") "TPHCM" (site:tuoitre.vn OR site:thanhnien.vn)',
        '("cảnh báo triều cường" OR "mưa ngập diện rộng") "TP.HCM" (site:laodong.vn OR site:vtv.vn)'
    ]
    for q in news_topics:
        queries.append((q, "news"))

    return queries


def load_existing_identifiers() -> Tuple[Set[str], Set[str]]:
    """Tải toàn bộ URL và MD5 hash hiện có để chống trùng lặp tuyệt đối."""
    seen_urls: Set[str] = set()
    seen_hashes: Set[str] = set()

    # 1. Từ thư mục raw episodes
    if os.path.exists(EPISODES_DIR):
        for root, _, files in os.walk(EPISODES_DIR):
            for fname in files:
                if fname.endswith(".json"):
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8-sig") as fp:
                            data = json.load(fp)
                            if isinstance(data, list):
                                for item in data:
                                    u = item.get("url") or item.get("webVideoUrl")
                                    if u:
                                        seen_urls.add(u)
                                    t = item.get("text") or item.get("title")
                                    if t:
                                        c_hash = hashlib.md5(t.strip().lower().encode("utf-8")).hexdigest()
                                        seen_hashes.add(c_hash)
                    except Exception:
                        pass

    # 2. Từ dataset master v3
    v3_path = os.path.join(DATA_DIR, "processed", "hcmc_flood_annotated_v3_multimodal.json")
    if os.path.exists(v3_path):
        try:
            with open(v3_path, "r", encoding="utf-8") as fp:
                v3_data = json.load(fp)
                for item in v3_data:
                    u = item.get("source", {}).get("url")
                    if u:
                        seen_urls.add(u)
                    t = item.get("content", {}).get("text")
                    if t:
                        seen_hashes.add(hashlib.md5(t.strip().lower().encode("utf-8")).hexdigest())
        except Exception:
            pass

    return seen_urls, seen_hashes


def is_valid_hcmc_flood_content(text: str) -> bool:
    """Kiểm tra nội dung hợp lệ theo chủ đề ngập lụt TP.HCM và loại bỏ rác."""
    if not text or len(text.strip()) < 15:
        return False

    clean_low = text.lower()

    # 1. Loại trừ rác tuyệt đối
    for junk in JUNK_EXCLUSIONS:
        if junk in clean_low:
            return False

    # 2. Loại trừ tỉnh ngoài rõ rệt
    for out_loc in OUT_OF_SCOPE_LOCATIONS:
        pat = r'(?:\b|^|#)' + re.escape(out_loc) + r'(?:\b|$|[#\s.,!?])'
        if re.search(pat, clean_low):
            if not any(k in clean_low for k in ["tphcm", "tp hcm", "sài gòn", "sai gon", "bình dương", "vũng tàu"]):
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
    """Trích xuất username và ID bài viết cho từng nền tảng."""
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

    elif platform == "threads":
        m_user = re.search(r'threads\.net/@([a-zA-Z0-9_.-]+)', url)
        if m_user:
            author = m_user.group(1)
        m_post = re.search(r'/post/([a-zA-Z0-9_.-]+)', url)
        if m_post:
            item_id = m_post.group(1)

    elif platform == "youtube":
        m_vid = re.search(r'(?:shorts/|watch\?v=)([a-zA-Z0-9_-]{11})', url)
        if m_vid:
            item_id = m_vid.group(1)
        m_user = re.search(r'@([a-zA-Z0-9_.-]+)', url)
        if m_user:
            author = m_user.group(1)

    return author, item_id


def crawl_single_query(query: str, platform: str, max_entries: int = 50) -> List[Dict[str, Any]]:
    """Cào và giải mã một câu truy vấn qua Google Discovery RSS."""
    encoded_q = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=vi&gl=VN&ceid=VN:vi"
    feed = feedparser.parse(rss_url)

    results = []
    for entry in feed.entries[:max_entries]:
        raw_title = getattr(entry, "title", "").strip()
        raw_summary = getattr(entry, "summary", "").strip()
        rss_link = getattr(entry, "link", "")
        pub_raw = getattr(entry, "published", "")

        if not raw_title or not rss_link:
            continue

        results.append({
            "raw_title": raw_title,
            "raw_summary": raw_summary,
            "rss_link": rss_link,
            "published": pub_raw,
            "platform": platform,
            "query": query
        })
    return results


def run_free_social_crawler(max_per_query: int = 50, num_workers: int = 15):
    queries = generate_expanded_crawl_queries()
    print("=" * 80)
    print("🚀 KHỞI ĐỘNG CÔNG CỤ FREE SOCIAL CRAWLER ĐA KÊNH MỞ RỘNG (100% ZERO-COST)")
    print(f"📌 Tổng số câu truy vấn mở rộng: {len(queries)}")
    print(f"📌 Số luồng song song: {num_workers}")
    print("=" * 80)

    seen_urls, seen_hashes = load_existing_identifiers()
    print(f"-> Đã nạp {len(seen_urls)} URLs và {len(seen_hashes)} content hashes hiện có để chống trùng lặp.")

    new_items_by_episode = defaultdict(lambda: defaultdict(list))
    total_found = 0
    total_added = 0
    duplicate_count = 0
    filtered_count = 0

    # Bước 1: Quét RSS song song
    raw_candidates = []
    print("\n[*] Giai đoạn 1: Quét song song Google Discovery RSS cho toàn bộ ma trận truy vấn...")
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_query = {
            executor.submit(crawl_single_query, q, plat, max_per_query): (q, plat)
            for q, plat in queries
        }
        for future in as_completed(future_to_query):
            try:
                items = future.result()
                raw_candidates.extend(items)
            except Exception:
                pass

    print(f"-> Đã tìm thấy {len(raw_candidates)} ứng viên ban đầu. Bắt đầu giải mã URL và kiểm duyệt...")

    # Bước 2: Giải mã và kiểm duyệt
    for cand in raw_candidates:
        total_found += 1
        raw_title = cand["raw_title"]
        raw_summary = cand["raw_summary"]
        platform = cand["platform"]
        full_snippet = f"{raw_title}. {raw_summary}".strip()

        clean_title = re.sub(r'\s*-\s*(?:TikTok|Facebook|Threads|YouTube)\s*$', '', raw_title, flags=re.IGNORECASE).strip()

        if not is_valid_hcmc_flood_content(clean_title) and not is_valid_hcmc_flood_content(full_snippet):
            filtered_count += 1
            continue

        c_hash = hashlib.md5(clean_title.lower().encode("utf-8")).hexdigest()
        if c_hash in seen_hashes:
            duplicate_count += 1
            continue

        try:
            decoded = gnewsdecoder(cand["rss_link"])
            decoded_url = decoded.get("decoded_url") if isinstance(decoded, dict) else decoded
        except Exception:
            decoded_url = ""

        if not decoded_url or not isinstance(decoded_url, str):
            continue

        if any(b in decoded_url for b in BLOCKED_URLS):
            continue
        if decoded_url in seen_urls:
            duplicate_count += 1
            continue

        # Kiểm tra đúng domain theo nền tảng
        dec_lower = decoded_url.lower()
        if platform == "tiktok" and "tiktok.com" not in dec_lower:
            continue
        elif platform == "facebook" and "facebook.com" not in dec_lower:
            continue
        elif platform == "threads" and "threads.net" not in dec_lower:
            continue
        elif platform == "youtube" and ("youtube.com" not in dec_lower and "youtu.be" not in dec_lower):
            continue

        seen_urls.add(decoded_url)
        seen_hashes.add(c_hash)

        d_str, iso_str = parse_rfc822_date(cand["published"])
        if not d_str:
            d_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            iso_str = datetime.now(timezone.utc).isoformat()

        ep_id = determine_episode_id(d_str)
        author_name, post_id = extract_author_and_id_from_url(decoded_url, platform)

        raw_record = {
            "id": post_id,
            "url": decoded_url,
            "webVideoUrl": decoded_url if platform in ["tiktok", "youtube"] else "",
            "mediaUrls": [decoded_url] if platform in ["tiktok", "youtube"] else [],
            "text": clean_title,
            "title": clean_title,
            "author": author_name,
            "authorMeta": {"name": author_name},
            "createTimeISO": iso_str,
            "published": cand["published"],
            "extracted_date": d_str,
            "platform": platform,
            "crawled_at": datetime.now(timezone.utc).isoformat(),
            "crawler_source": "free_discovery_engine_multichannel"
        }

        new_items_by_episode[ep_id][platform].append(raw_record)
        total_added += 1

    print("\n" + "=" * 80)
    print("HOÀN TẤT THU THẬP TỰ ĐỘNG. ĐANG LƯU VÀO CÁC PHÂN VÙNG EPISODE:")
    print(f"  * Tổng số ứng viên quét: {total_found}")
    print(f"  * Bị loại bỏ do không hợp lệ/ngoại tỉnh/rác: {filtered_count}")
    print(f"  * Bị loại bỏ do trùng lặp (URL hoặc nội dung): {duplicate_count}")
    print(f"  * SỐ BÀI ĐĂNG MỚI ĐẠT CHUẨN THÊM VÀO: {total_added}")
    print("=" * 80)

    # Bước 3: Lưu vào data/raw/episodes/
    for ep_id, platforms in new_items_by_episode.items():
        ep_dir = os.path.join(EPISODES_DIR, ep_id)
        os.makedirs(ep_dir, exist_ok=True)

        for plat, items in platforms.items():
            raw_fname = f"{plat}_raw.json"
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

            print(f"  + [{ep_id}] {plat.upper()}: Thêm {len(items)} bài -> Tổng cộng: {len(final_list)} bài ({raw_fname})")

    print("\n-> Đã cập nhật toàn bộ vào cấu trúc phân vùng Episode!")


if __name__ == "__main__":
    run_free_social_crawler(max_per_query=30, num_workers=15)
