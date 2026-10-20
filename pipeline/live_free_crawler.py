# -*- coding: utf-8 -*-
"""
pipeline/live_free_crawler.py
Module Cào Dữ liệu Đa Kênh Trực tiếp Hoàn Toàn Miễn Phí (Live Free Multi-Channel Crawler):
- Phục vụ riêng cho LIVE MODE Streaming Ingestion.
- 100% Zero-cost: Khai thác Google Discovery RSS kết hợp googlenewsdecoder.
- Hỗ trợ 3 luồng nguồn dữ liệu:
  1. TikTok Video Posts (ƯU TIÊN HÀNG ĐẦU)
  2. Facebook Public Posts / Pages (ƯU TIÊN HÀNG ĐẦU)
  3. Báo chí Chính thống (Nguồn bổ trợ, thứ cấp đối soát)
- Cơ chế Round-Robin Hotspot Matrix:
  * Phân bổ 87% ngân sách quét cho Mạng Xã Hội (TikTok & Facebook) và 13% cho Báo chí.
- Xử lý Đa luồng song song (ThreadPoolExecutor): Tốc độ quét nhanh < 2 giây.
- Phân rã Sự kiện Đa Điểm (Multi-Hotspot Event Fan-out):
  * Khi bài báo/post liệt kê 2-3 tuyến đường ngập, tự động tách thành các điểm ngập độc lập
    chuẩn tim đường OpenStreetMap trên Heatmap.
- Trích xuất câu ngữ cảnh trọn vẹn (Sentence-level Context Extraction):
  * Tuyệt đối không cắt cụt chữ, giữ nguyên vẹn câu văn để hiển thị chuẩn đẹp trên popup Heatmap.
- Định dạng Event chuẩn hoá 100% sẵn sàng cho Apache Kafka Topic: social.live.raw.
- GIỚI HẠN TUYỆT ĐỐI 24 GIỜ: Loại bỏ 100% bài đăng cũ quá 24h.
- 3 NHÃN PHÂN LOẠI THỜI GIAN CHUẨN XÁC:
  * < 2h: 🔴 ĐANG DIỄN RA (< 2 GIỜ)
  * 2-4h: 🟠 ĐỢT MƯA VỪA DỨT (2-4 GIỜ)
  * <= 24h: 🟡 CẢNH BÁO TRONG NGÀY (4-24 GIỜ)
"""

import os
import sys
import json
import re
import time
import calendar
import hashlib
import urllib.parse
from datetime import datetime, timezone
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

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.gazetteer import normalize_text, HOTSPOTS, CSGT_HOTSPOTS, OUT_OF_SCOPE_LOCATIONS, match_all_hotspots
from pipeline.event_processor import clean_stream_text, contains_spam_or_noise, format_relative_time

# TỪ KHÓA CHỈ DẤU NGẬP TRỰC TIẾP (Bản thân từ ngữ đã mang nghĩa ngập/nước/triều)
DIRECT_FLOOD_KEYWORDS = [
    "ngập", "ngap", "triều cường", "trieu cuong", "lội nước", "loi nuoc", "bì bõm", "bi bom",
    "lút bánh", "lut banh", "nước dâng", "nuoc dang", "ngập sâu", "ngap sau", "biển nước", "bien nuoc",
    "ngập lụt", "ngap lut", "tràn vào nhà", "tran vao nha", "mênh mông nước", "sóng đánh vào nhà",
    "ngập đường", "ngap duong", "ngập nặng", "ngap nang", "mực nước triều", "đỉnh triều",
    "ngập nửa bánh", "lút bô", "lut bo", "lút ống xả", "đường hóa sông", "duong hoa song",
    "đường thành sông", "ngập lênh láng", "chìm trong biển nước", "hộc nước",
    "nước ngập tới đầu gối", "ngập ngang xe", "dự báo triều cường", "cảnh báo ngập"
]

# TỪ KHÓA HÀNH VI ĐỜI THƯỜNG (Bắt buộc phải đi kèm bối cảnh nước/mưa và loại trừ ngữ cảnh phi ngập)
BEHAVIORAL_FLOOD_KEYWORDS = [
    "chết máy", "chet may", "dắt bộ", "dat bo", "dắt xe", "dat xe", "dẫn bộ",
    "thất thủ", "that thu", "chết bu-gi", "chet bu gi", "quay đầu xe",
    "không đi được", "khong di duoc", "té xe", "te xe", "ngã xe", "đẩy bộ", "day bo",
    "nước tràn vào nhà", "sóng đánh", "sóng tạt", "sóng dập", "sóng tràn", "hết lối đi"
]

# TỪ KHÓA BỐI CẢNH NƯỚC / MƯA BẮT BUỘC ĐI KÈM VỚI TỪ KHÓA HÀNH VI
WATER_WEATHER_CONTEXT = [
    "mưa", "mua", "nước", "nuoc", "triều", "trieu", "lụt", "lut", "lũ", "lu",
    "sông", "song", "rạch", "rach", "cống", "cong", "suối", "bão", "bao", "hầm",
    "đường", "tuyến", "lội", "ngập"
]

# TỪ KHÓA LOẠI TRỪ NGUYÊN NHÂN PHI NGẬP LỤT (Chặn đứng tin rác: xe hết xăng, quán thất thủ...)
NON_FLOOD_EXCLUSIONS = [
    "hết xăng", "het xang", "hỏng ắc quy", "ắc quy", "ac quy", "bể ống nước", "vỡ ống nước",
    "quên tắt vòi", "tiệm sửa", "tiem sua", "sửa xe", "bảo dưỡng xe", "quán ăn", "trà sữa",
    "trận đấu", "bóng đá", "hội chợ", "liveshow", "concert", "khuyến mãi", "say xỉn",
    "say rượu", "va chạm giao thông", "cướp giật", "tai nạn giao thông", "cháy xe"
]

FLOOD_INTENT_KEYWORDS = DIRECT_FLOOD_KEYWORDS + BEHAVIORAL_FLOOD_KEYWORDS

# Từ khóa khẳng định địa bàn TP.HCM
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
    "bàu cát", "đồng đen", "đào sư tích", "phạm hữu lầu", "nguyễn bình", "bùi văn ba",
    "bình dương", "binh duong", "thủ dầu một", "dĩ an", "di an", "thuận an",
    "vũng tàu", "vung tau", "bà rịa", "ba ria", "phú mỹ"
]

# Từ khóa loại trừ nội dung rác / ẩn dụ / thương mại / BĐS phòng trọ / chính trị vĩ mô
JUNK_EXCLUSIONS = [
    "deal hot", "ngập trời", "giải mật", "hồ sơ giải mật", "nhà sách", "khai trương",
    "độc quyền trên", "series tập", "cánh sóng âm", "khuyến mãi", "sale sập sàn",
    "mực tím", "truyện hạt lúa", "cia sài gòn", "bán nhà", "cho thuê", "phòng trọ",
    "căn hộ", "vinhomes", "bánh mì", "xe lướt", "odo", "thi hộ", "học hộ",
    "pha nước rút", "chạy nước rút", "giai đoạn nước rút", "nước rút thi công",
    "tay đua", "cầu đi bộ", "nhựa duy tân", "duy tân", "cải tạo diện mạo",
    "hà nội", "mcer", "marie curie", "đà lạt", "đà nẵng", "hải phòng", "cần thơ",
    "lục bình", "bãi tắm", "rác biển", "bánh khọt", "cellphones", "sắm tết",
    "chúc khách", "tiệm ăn", "mì cay", "quán chay", "sạc xanh", "ev one", "vi vu vũng tàu lễ",
    "shin-chan", "thông cống nghẹt", "hút hầm cầu", "thông nghẹt", "bảo dưỡng xe máy", "thủy kích",
    "chung cư mini", "căn duplex", "studio ban công", "pax sky", "căn góc cực thoáng", "sát vách quận 1",
    "hẻm 5m xe hơi", "chuyện lịch sử", "đinh bộ lĩnh cậy núi",
    "bảo lộc", "lâm đồng", "nghệ an", "tuyên quang", "thái nguyên", "quảng ninh", "cà mau",
    "đồng nai", "phước tân", "biên hòa", "biên hoà", "cao tốc biên hòa", "long thành", "trảng bom", "nhơn trạch", "vĩnh cửu",
    # LỌC RÁC PHÒNG TRỌ, BĐS VÀ ẨN DỤ ÁNH SÁNG
    "studio", "tách bếp", "tach bep", "ban công", "ban cong", "bếp tách biệt", "nội thất", "noi that",
    "xách vali", "xach vali", "máy giặt", "may giat", "tủ lạnh", "tu lanh", "nước nóng", "nuoc nong",
    "4k/kwh", "kwh", "điện:", "nước:", "hotline", "zalo", "cọc", "cho thuê phòng", "ở ghép", "giá rẻ",
    "ngập tràn ánh sáng", "ngap tran anh sang", "ngập tràn niềm vui", "ngập tràn hạnh phúc", "ngập tràn tiếng cười",
    "ngập tràn yêu thương", "cửa sổ ngập tràn", "ban công siêu thoáng", "hữu cảnh nhà trọ", "phòng trọ bình thạnh",
    # LỌC RÁC BÌNH LUẬN CHÍNH TRỊ, DỰ ÁN VĨ MÔ, BÀI LUẬN
    "mệnh lệnh", "mệnh lệnh không được thay đổi", "bộ đội cụ hồ", "thủ tướng", "thủ tướng chính phủ",
    "phó thủ tướng", "chính trị", "tin nội chính", "ctvn", "chinhtrivietnam", "tinnoichinh",
    "duanchongngaptphcm", "thutuongleminhhung", "kênh tham lương", "hồ điều tiết ngầm", "vì sao phải sống chung",
    "dự án chống ngập", "công trình về đích", "bàn giao", "vận hành thử", "6,5 triệu người dân", "nghị quyết"
]

# Danh sách URL cấm triệt để
BLOCKED_URLS = [
    "1290599776588076", "1560796269387953", "7651865598330277138", "7677552058366430484",
    "909275717898402", "1213187850601240", "1083969077465719", "1025438923832462",
    "1324003929930555", "1655627919262386", "814626184498303", "1342905424547961",
    "1018248260982647", "1047070484870120", "1928424957917772", "7658193771384900884",
    "2001763603775858", "1612357400408698", "954734066181198", "1679978572035782",
    "561908110048170", "1824668004742145", "1104448985347819", "7690869999593884948",
    "7556535629320883474", "7556168799162993938", "7555905500920040724", "2214370282512169",
    "27443549455269648", "CBMipwJBVV", "ebaf5b0296b9cca6", "7613569837301894421"
]

# Tên miền báo chí chính thống được kiểm chứng
TRUSTED_NEWS_DOMAINS = [
    "tuoitre.vn", "thanhnien.vn", "vnexpress.net", "dantri.com.vn",
    "plo.vn", "nld.com.vn", "vietnamnet.vn", "vtcnews.vn", "laodong.vn", "vtv.vn"
]

# MA TRẬN TRUY VẤN ĐA TẦNG CHUYÊN SÂU (TIKTOK + FACEBOOK + NEWS)
TIKTOK_QUERIES = [
    # Tier 1: Real-time hashtags & captions
    'site:tiktok.com ("#ngaplut" OR "#trieucuong") "Sài Gòn" when:4h',
    'site:tiktok.com ("ngập" OR "nước dâng") ("TPHCM" OR "Sài Gòn") when:4h',
    'site:tiktok.com ("xe chết máy" OR "lội nước") ("TPHCM" OR "Sài Gòn") when:12h',
    # Tier 2: Hotspots multi-line
    'site:tiktok.com "Trần Xuân Soạn" "ngập" when:12h',
    'site:tiktok.com "Huỳnh Tấn Phát" "ngập" when:12h',
    'site:tiktok.com "Lê Văn Lương" "ngập" when:12h',
    'site:tiktok.com "Bùi Văn Ba" "ngập" when:12h',
    'site:tiktok.com "Ung Văn Khiêm" "ngập" when:12h',
    'site:tiktok.com "Thảo Điền" "ngập" when:12h',
    'site:tiktok.com "Võ Văn Ngân" "ngập" when:12h',
    'site:tiktok.com "Nguyễn Văn Quá" "ngập" when:12h',
    'site:tiktok.com "Hồ Học Lãm" "ngập" when:12h',
    'site:tiktok.com "Mễ Cốc" "ngập" when:12h',
    'site:tiktok.com "triều cường" "ngập" "TPHCM"',
    'site:tiktok.com "mưa lớn" "ngập" "Sài Gòn"',
    'site:tiktok.com "#ngaplut" "Sài Gòn"'
]

FACEBOOK_QUERIES = [
    # Tier 1: Siêu tốc 2 Giờ (when:2h) - Cộng đồng & Giao thông tức thời
    'site:facebook.com ("ngập" OR "ngập nước" OR "nước dâng") ("TPHCM" OR "Sài Gòn") when:2h',
    'site:facebook.com ("triều cường" OR "mưa ngập") ("TP.HCM" OR "Sài Gòn") when:2h',
    'site:facebook.com ("xe chết máy" OR "lội nước" OR "bì bõm" OR "lút bánh") "ngập" when:2h',
    'site:facebook.com ("nước tràn vào nhà" OR "đường thành sông" OR "sóng đánh") ("Sài Gòn" OR "TPHCM") when:2h',
    'site:facebook.com/groups ("đường ngập" OR "kẹt xe" OR "nước ngập") "TPHCM" when:2h',
    'site:facebook.com/groups ("chết máy" OR "ngập nước" OR "triều cường") when:2h',
    'site:facebook.com ("Trần Xuân Soạn" OR "Huỳnh Tấn Phát" OR "Lê Văn Lương" OR "Bùi Văn Ba") "ngập" when:2h',
    'site:facebook.com ("Quốc Hương" OR "Thảo Điền" OR "Ung Văn Khiêm" OR "Nguyễn Xí") "ngập" when:2h',
    'site:facebook.com ("Võ Văn Ngân" OR "Kha Vạn Cân" OR "Đặng Thị Rành" OR "Chợ Thủ Đức") "ngập" when:2h',
    'site:facebook.com ("Hồ Học Lãm" OR "An Dương Vương" OR "Kinh Dương Vương" OR "Mễ Cốc") "ngập" when:2h',
    'site:facebook.com ("Nguyễn Văn Quá" OR "Phan Huy Ích" OR "Cây Trâm" OR "Lê Đức Thọ") "ngập" when:2h',
    'site:facebook.com ("Bến Bình Đông" OR "Phạm Thế Hiển" OR "Tạ Quang Bửu") "ngập" when:2h',
    'site:facebook.com ("Đinh Bộ Lĩnh" OR "Bạch Đằng" OR "Xô Viết Nghệ Tĩnh") "ngập" when:2h',
    'site:facebook.com ("Quốc Lộ 50" OR "Đào Sư Tích" OR "Nguyễn Bình") "ngập" when:2h',
    # Tier 2: Đợt ngập liền kề (when:4h / when:1d) - Giữ vững nền tảng chống đói tin khi vừa tạnh mưa
    'site:facebook.com "Trần Xuân Soạn" "ngập" when:1d',
    'site:facebook.com "Huỳnh Tấn Phát" "ngập" when:1d',
    'site:facebook.com "Lê Văn Lương" "ngập" when:1d',
    'site:facebook.com "Bùi Văn Ba" "ngập" when:1d',
    'site:facebook.com "triều cường" "ngập" "TPHCM" when:1d',
    'site:facebook.com "mưa lớn" "ngập" "Sài Gòn" when:1d',
    'site:facebook.com "Ung Văn Khiêm" "ngập" when:1d',
    'site:facebook.com "Thảo Điền" "ngập" when:1d',
    'site:facebook.com "Võ Văn Ngân" "ngập" when:1d',
    'site:facebook.com "Phan Huy Ích" "ngập" when:1d',
    'site:facebook.com "Mễ Cốc" "ngập" when:1d',
    'site:facebook.com "Kinh Dương Vương" "ngập" when:1d'
]

# Truy vấn báo chí (nguồn phụ đối soát nhanh)
NEWS_QUERIES = [
    'site:tuoitre.vn ("ngập" OR "triều cường") ("TP.HCM" OR "Sài Gòn") when:2h',
    'site:thanhnien.vn ("ngập" OR "triều cường") ("TP.HCM" OR "Sài Gòn") when:2h',
    'site:vnexpress.net ("ngập" OR "triều cường") ("TP.HCM" OR "Sài Gòn") when:2h',
    'site:plo.vn ("ngập" OR "triều cường") ("TP.HCM" OR "Sài Gòn") when:2h',
    'site:dantri.com.vn ("ngập" OR "triều cường") ("TP.HCM" OR "Sài Gòn") when:1d',
    'site:nld.com.vn ("ngập" OR "triều cường") ("TP.HCM" OR "Sài Gòn") when:1d',
    '("ngập" OR "triều cường") ("TP.HCM" OR "Sài Gòn") ("tuyến đường" OR "giao thông") when:2h'
]


class LiveFreeSocialCrawler:
    """
    Crawler thu thập thời gian thực (Live Multi-Channel Streaming Ingestion) hoàn toàn miễn phí.
    ƯU TIÊN TUYỆT ĐỐI MẠNG XÃ HỘI (TikTok & Facebook) TRÊN CẢ BÁO CHÍ.
    """
    _rr_tiktok_offset: int = 0
    _rr_fb_offset: int = 0
    _rr_news_offset: int = 0

    def __init__(self):
        self.seen_urls: Set[str] = set()
        self.seen_hashes: Set[str] = set()

    def is_valid_content(self, text: str) -> bool:
        clean = clean_stream_text(text)
        if not clean or len(clean) < 8:
            return False
        clean_low = clean.lower()

        if contains_spam_or_noise(clean):
            return False
        for junk in JUNK_EXCLUSIONS:
            if junk in clean_low:
                return False

        # PHÒNG TRÁNH TIN RÁC: Loại trừ các nguyên nhân phi ngập lụt
        for non_f in NON_FLOOD_EXCLUSIONS:
            if non_f in clean_low:
                return False

        # TUÂN THỦ 100% KIỂM SOÁT ĐỊA GIỚI NGOẠI TỈNH
        for out_loc in OUT_OF_SCOPE_LOCATIONS:
            pat = r'(?:\b|^|#)' + re.escape(out_loc) + r'(?:\b|$|[#\s.,!?])'
            if re.search(pat, clean_low):
                return False

        # RÀNG BUỘC Ý ĐỊNH NGẬP LỤT (Co-occurrence Guard cho từ khóa hành vi)
        has_direct_flood = any(k in clean_low for k in DIRECT_FLOOD_KEYWORDS)
        has_behavioral_flood = False
        if not has_direct_flood:
            matched_behavior = any(k in clean_low for k in BEHAVIORAL_FLOOD_KEYWORDS)
            if matched_behavior:
                has_water_context = any(w in clean_low for w in WATER_WEATHER_CONTEXT)
                if has_water_context:
                    has_behavioral_flood = True

        if not has_direct_flood and not has_behavioral_flood:
            return False

        has_hcmc = any(k in clean_low for k in HCMC_AFFIRMATION_KEYWORDS)
        if not has_hcmc:
            has_hotspot = any(
                any(kw in clean_low for kw in spot.get("keywords", []))
                for spot in HOTSPOTS[:80]
            )
            if not has_hotspot:
                return False

        return True

    def extract_author_and_id(self, url: str, platform: str) -> Tuple[str, str]:
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
        elif platform == "news":
            for d in TRUSTED_NEWS_DOMAINS:
                if d in url.lower():
                    author = f"Báo {d.split('.')[0].capitalize()}"
                    break
            else:
                author = "Báo Chính Thống"

        return author, item_id

    def extract_clean_quote(self, title: str, summary: str = "") -> str:
        """
        Trích xuất câu hoàn chỉnh có ngữ cảnh ngập lụt chuẩn mực.
        """
        clean_t = re.sub(r'\s*-\s*(?:TikTok|Facebook|VnExpress|Tuổi Trẻ|Thanh Niên|Dân Trí|PLO|NLD)\s*$', '', title, flags=re.IGNORECASE).strip()
        if not summary:
            return clean_t

        clean_sum = re.sub(r'<[^>]+>', ' ', summary)
        clean_sum = re.sub(r'\s+', ' ', clean_sum).strip()

        sentences = re.split(r'(?<=[.!?])\s+', clean_sum)
        for s in sentences:
            s_clean = s.strip()
            if len(s_clean) >= 15 and any(k in s_clean.lower() for k in ["ngập", "triều cường", "chết máy", "nước dâng", "lút bánh"]):
                if len(s_clean) <= 140:
                    return s_clean

        return clean_t

    def get_interleaved_queries(self, max_queries: int = 15) -> List[Tuple[str, str]]:
        """
        Phân bổ ngân sách truy vấn: ƯU TIÊN TUYỆT ĐỐI MẠNG XÃ HỘI (87% Social : 13% News)
        """
        tiktok_count = max(1, int(max_queries * 0.47))
        fb_count = max(1, int(max_queries * 0.40))
        news_count = max(1, max_queries - tiktok_count - fb_count)

        selected = []

        # 1. TikTok (Ưu tiên hàng đầu)
        for i in range(tiktok_count):
            idx = (LiveFreeSocialCrawler._rr_tiktok_offset + i) % len(TIKTOK_QUERIES)
            selected.append((TIKTOK_QUERIES[idx], "tiktok"))
        LiveFreeSocialCrawler._rr_tiktok_offset = (LiveFreeSocialCrawler._rr_tiktok_offset + tiktok_count) % len(TIKTOK_QUERIES)

        # 2. Facebook (Ưu tiên hàng đầu)
        for i in range(fb_count):
            idx = (LiveFreeSocialCrawler._rr_fb_offset + i) % len(FACEBOOK_QUERIES)
            selected.append((FACEBOOK_QUERIES[idx], "facebook"))
        LiveFreeSocialCrawler._rr_fb_offset = (LiveFreeSocialCrawler._rr_fb_offset + fb_count) % len(FACEBOOK_QUERIES)

        # 3. Báo chí Chính thống (Nguồn phụ đối soát)
        for i in range(news_count):
            idx = (LiveFreeSocialCrawler._rr_news_offset + i) % len(NEWS_QUERIES)
            selected.append((NEWS_QUERIES[idx], "news"))
        LiveFreeSocialCrawler._rr_news_offset = (LiveFreeSocialCrawler._rr_news_offset + news_count) % len(NEWS_QUERIES)

        return selected

    def _fetch_single_query(self, query: str, platform: str, max_items_per_query: int) -> List[Tuple[Any, str]]:
        enc_q = urllib.parse.quote_plus(query)
        feed_url = f"https://news.google.com/rss/search?q={enc_q}&hl=vi&gl=VN&ceid=VN:vi"
        try:
            feed = feedparser.parse(feed_url)
            return [(entry, platform) for entry in feed.entries[:max_items_per_query]]
        except Exception:
            return []

    def poll_live_stream(
        self,
        window_minutes: int = 120,
        max_queries: int = 25,
        max_items_per_query: int = 8
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Quét luồng thời gian thực cho Live Mode:
        - ƯU TIÊN MẠNG XÃ HỘI (TikTok & Facebook) TRÊN CẢ BÁO CHÍ.
        - CHẶN 100% CÁC BÀI ĐĂNG CŨ QUÁ 24 GIỜ (age_seconds > 86400s).
        - PHÂN LOẠI CHUẨN XÁC THEO 3 NHÃN THỜI GIAN:
          * < 2h: 🔴 ĐANG DIỄN RA (< 2 GIỜ)
          * 2-4h: 🟠 ĐỢT MƯA VỪA DỨT (2-4 GIỜ)
          * <= 24h: 🟡 CẢNH BÁO TRONG NGÀY (4-24 GIỜ)
        - TUYỆT ĐỐI KHÔNG GIẢ MẠO THỜI GIAN.
        """
        current_time = int(time.time())
        # Cửa sổ giới hạn nghiêm ngặt tối đa 24 giờ (86400 giây): TUYỆT ĐỐI LOẠI BỎ TIN TRÊN 24H
        cutoff_24h = current_time - 86400
        news_cutoff = current_time - (window_minutes * 60)

        events_window = []
        events_recent = []
        total_scanned = 0

        active_queries = self.get_interleaved_queries(max_queries=max_queries)

        # 1. Quét song song đa luồng các feed RSS bằng ThreadPoolExecutor
        raw_entries: List[Tuple[Any, str]] = []
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(self._fetch_single_query, q, p, max_items_per_query) for q, p in active_queries]
            for f in as_completed(futures):
                try:
                    res = f.result()
                    if res:
                        raw_entries.extend(res)
                except Exception:
                    pass

        total_scanned = len(raw_entries)

        # 2. Xử lý & Bóc tách đa điểm ngập (Fan-out Resolution)
        for entry, platform in raw_entries:
            raw_title = getattr(entry, "title", "") or ""
            clean_title = re.sub(r'\s*-\s*(?:TikTok|Facebook|VnExpress|Tuổi Trẻ|Thanh Niên|Dân Trí|PLO|NLD)\s*$', '', raw_title, flags=re.IGNORECASE).strip()

            if not self.is_valid_content(clean_title):
                continue

            c_hash = hashlib.md5(clean_title.lower().encode("utf-8")).hexdigest()
            if c_hash in self.seen_hashes:
                continue

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

            if any(b in decoded_url for b in BLOCKED_URLS):
                continue
            if decoded_url in self.seen_urls:
                continue

            dec_low = decoded_url.lower()
            if platform == "tiktok":
                if "tiktok.com" not in dec_low and not any(d in dec_low for d in TRUSTED_NEWS_DOMAINS):
                    continue
            elif platform == "facebook":
                if "facebook.com" not in dec_low and not any(d in dec_low for d in TRUSTED_NEWS_DOMAINS):
                    continue
            elif platform == "news":
                if not any(d in dec_low for d in TRUSTED_NEWS_DOMAINS):
                    continue

            # Xác định thời gian đăng bài chuẩn xác (UTC -> Unix Timestamp)
            pub_parsed = getattr(entry, "published_parsed", None)
            if pub_parsed:
                try:
                    pub_unix = calendar.timegm(pub_parsed)
                except Exception:
                    pub_unix = 0
            else:
                pub_unix = 0

            # TUYỆT ĐỐI KHÔNG GÁN BỪA THỜI GIAN NẾU KHÔNG CÓ TIMESTAMP THẬT
            if pub_unix == 0:
                continue

            # ÁP DỤNG CỬA SỔ THỜI GIAN TỐI ĐA 24 GIỜ: LOẠI BỎ TOÀN BỘ TIN TRÊN 24H
            if pub_unix < cutoff_24h:
                continue
            if platform == "news" and pub_unix < news_cutoff:
                continue

            age_seconds = current_time - pub_unix
            if age_seconds > 86400:
                continue

            pub_iso = datetime.fromtimestamp(pub_unix, timezone.utc).isoformat()
            author_name, post_id = self.extract_author_and_id(decoded_url, platform)

            raw_summary = getattr(entry, "summary", "") or ""
            quote_text = self.extract_clean_quote(clean_title, raw_summary)

            self.seen_urls.add(decoded_url)
            self.seen_hashes.add(c_hash)

            # PHÂN RÃ SỰ KIỆN ĐA ĐIỂM (MULTI-HOTSPOT EVENT FAN-OUT)
            matched_spots = match_all_hotspots(clean_title)
            if not matched_spots and quote_text != clean_title:
                matched_spots = match_all_hotspots(quote_text)

            if not matched_spots:
                continue

            # PHÂN LOẠI CHUẨN XÁC THEO 3 NHÃN THỜI GIAN:
            # 1. < 2h: 🔴 ĐANG DIỄN RA (< 2 GIỜ)
            # 2. 2-4h: 🟠 ĐỢT MƯA VỪA DỨT (2-4 GIỜ)
            # 3. <= 24h: 🟡 CẢNH BÁO TRONG NGÀY (4-24 GIỜ)
            is_social = platform in ["tiktok", "facebook"]
            if age_seconds <= 7200:
                freshness = "strict_2h"
                status_tag = "🔴 ĐANG DIỄN RA (< 2 GIỜ)"
                event_weight = 4.5 if is_social else 3.0
                event_priority = 1 if is_social else 2
            elif age_seconds <= 14400:
                freshness = "recent_4h"
                status_tag = "🟠 ĐỢT MƯA VỪA DỨT (2-4 GIỜ)"
                event_weight = 3.5 if is_social else 2.0
                event_priority = 2 if is_social else 3
            else:
                freshness = "within_24h"
                status_tag = "🟡 CẢNH BÁO TRONG NGÀY (4-24 GIỜ)"
                event_weight = 2.5 if is_social else 1.5
                event_priority = 3 if is_social else 4

            for spot_idx, spot in enumerate(matched_spots):
                st_name = spot.get("street") or spot.get("display_name", "")
                sub_id = f"{post_id}_s{spot_idx}" if len(matched_spots) > 1 else str(post_id)
                canonical_id = f"{platform}_{sub_id}"

                event = {
                    "id": str(sub_id),
                    "canonical_id": canonical_id,
                    "url": decoded_url,
                    "platform": platform,
                    "media_type": "video" if platform == "tiktok" else ("article" if platform == "news" else "post"),
                    "author": author_name,
                    "text": quote_text,
                    "title": clean_title,
                    "create_time": pub_unix,
                    "created_at_iso": pub_iso,
                    "timestamp": pub_unix,
                    "relative_time": format_relative_time(pub_unix, current_time),
                    "location": {
                        "street": st_name,
                        "display_name": st_name if st_name else (f"{spot.get('ward', '')} (TP.HCM)" if spot.get('ward') != "Toàn TP.HCM" else "Toàn TP. Hồ Chí Minh"),
                        "ward": spot.get("ward", "Toàn TP.HCM"),
                        "administrative_unit": spot.get("ward", "Toàn TP.HCM"),
                        "district": spot.get("district", "TP.HCM"),
                        "region": spot.get("region", "TPHCM"),
                        "lat": spot["lat"],
                        "lon": spot["lon"],
                        "heat_points": spot.get("heat_points", [[spot["lat"], spot["lon"]]]),
                        "priority": event_priority,
                        "type": spot.get("type", "ngập úng đô thị"),
                        "cause": spot.get("cause", "rain"),
                        "cause_label": spot.get("cause_label", "Mưa lớn, nước không thoát kịp"),
                        "source": "live_free_crawler"
                    },
                    "aspect": st_name or spot.get("ward", ""),
                    "weight": event_weight,
                    "freshness": freshness,
                    "status_tag": status_tag,
                    "crawler_source": "live_free_social_crawler"
                }

                events_window.append(event)

        # SẮP XẾP ƯU TIÊN: TIN TRONG 2 GIỜ LÊN ĐẦU TIÊN -> MẠNG XÃ HỘI (TIKTOK/FACEBOOK) -> ĐỘ NGHIÊM TRỌNG
        events_window.sort(key=lambda x: (
            2 if x.get("freshness") == "strict_2h" else (1 if x.get("freshness") == "recent_4h" else 0),
            1 if x.get("platform") in ["tiktok", "facebook"] else 0,
            x.get("weight", 1.0),
            x.get("create_time", 0)
        ), reverse=True)

        active_window_label = f"{window_minutes // 60} giờ qua" if window_minutes >= 60 else f"{window_minutes} phút"

        stats = {
            "mode": "live",
            "crawler": "live_free_multi_crawler",
            "current_time": current_time,
            "total_scanned": total_scanned,
            "events_window_count": len(events_window),
            "events_recent_count": len(events_recent),
            "social_priority_ratio": "87% Social : 13% News",
            "window_minutes": window_minutes,
            "active_window": active_window_label
        }

        return events_window, stats


if __name__ == "__main__":
    crawler = LiveFreeSocialCrawler()
    print("[*] Đang thử nghiệm quét Live Free Multi-Channel Crawler (Ưu tiên TikTok + Facebook)...")
    events, stats = crawler.poll_live_stream(window_minutes=120, max_queries=15)
    print(f"[+] Kết quả quét Live:")
    print(f"  - Tổng số ứng viên quét: {stats['total_scanned']}")
    print(f"  - Bài đăng thu nạp được: {len(events)} (Tỷ lệ: {stats['social_priority_ratio']})")
    for ev in events[:5]:
        loc = ev.get('location', {})
        print(f"    * [{ev['platform'].upper()}] Đường: {loc.get('street')} | ĐVHC: {loc.get('ward')} ({ev.get('relative_time')})")
        print(f"      Status: {ev.get('status_tag')}")
        print(f"      Text: {ev['text'][:80]}...")
        print(f"      URL: {ev['url']}")
