# -*- coding: utf-8 -*-
"""
pipeline/live_free_crawler.py
Module Cào Dữ liệu Mạng Xã hội Trực tiếp Hoàn Toàn Miễn Phí (Live Free Social Crawler):
- Phục vụ riêng cho LIVE MODE Streaming Ingestion (không đụng tới scripts/free_social_crawler.py của tập tĩnh).
- 100% Zero-cost: Khai thác Google Discovery RSS kết hợp googlenewsdecoder.
- Cơ chế Smart Adaptive Window:
  * Mặc định lọc các bài đăng trong 60 - 120 phút vừa qua (thời điểm đang diễn ra mưa).
  * Nếu thời điểm quét chưa có mưa mới (trời nắng), tự động báo cáo trạng thái an toàn
    hoặc mở rộng hiển thị đợt mưa gần nhất (24h - 48h) minh bạch.
- Tích hợp sẵn cơ chế Deduplication cấp độ Ingestion (seen_urls & hash MD5).
- Định dạng Event chuẩn hoá sẵn sàng bắn vào Apache Kafka Topic: social.live.raw.
"""

import os
import sys
import json
import re
import time
import hashlib
import urllib.parse
from datetime import datetime, timezone
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

from core.gazetteer import normalize_text, HOTSPOTS, CSGT_HOTSPOTS, OUT_OF_SCOPE_LOCATIONS
from pipeline.event_processor import clean_stream_text, contains_spam_or_noise

# Danh mục từ khóa phản ánh ngập lụt thực tế
FLOOD_INTENT_KEYWORDS = [
    "ngập", "ngap", "triều cường", "trieu cuong", "chết máy", "chet may",
    "bì bõm", "bi bom", "lội nước", "loi nuoc", "lút bánh", "lut banh",
    "nước dâng", "nuoc dang", "ngập sâu", "ngap sau", "biển nước", "bien nuoc",
    "thất thủ", "that thu", "ngập lụt", "ngap lut", "tràn vào nhà", "tran vao nha",
    "mênh mông nước", "sóng đánh", "ngập đường", "ngap duong", "dắt bộ", "dắt xe",
    "dẫn bộ", "xe chết máy", "ùn tắc do ngập", "ngập nặng", "ngap nang",
    "dự báo triều cường", "cảnh báo ngập", "mực nước triều", "đỉnh triều",
    "nước đã rút", "nước rút hết", "hết ngập", "đường khô ráo", "sớm thi công chống ngập", "thi công chống ngập"
]

# Từ khóa khẳng định địa bàn TP.HCM (bao gồm các khu vực liên kết)
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
    # Mở rộng TP.HCM
    "bình dương", "binh duong", "thủ dầu một", "thu dau mot", "dĩ an", "di an", "thuận an", "thuan an",
    "bến cát", "ben cat", "tân uyên", "tan uyen", "đại lộ bình dương", "ngã tư 550", "cầu ông bố", "sóng thần",
    "vũng tàu", "vung tau", "bà rịa", "ba ria", "phú mỹ", "phu my", "côn đảo", "con dao", "thùy vân", "hạ long vũng tàu"
]

# Từ khóa loại trừ nội dung rác / ẩn dụ / thương mại
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
    "ngập tràn tết", "shop bí", "ngập ánh sáng", "tràn ngập ánh sáng", "ngập nắng", "view chill ngập", "ngập dâu sữa",
    "ngập quà", "shin-chan", "thông cống nghẹt", "hút hầm cầu", "thông nghẹt", "bảo dưỡng xe máy", "thủy kích",
    "chung cư mini", "căn duplex", "studio ban công", "pax sky", "căn góc cực thoáng", "sát vách quận 1",
    "hẻm 5m xe hơi", "chuyện lịch sử", "đinh bộ lĩnh cậy núi",
    "bảo lộc", "lâm đồng", "nghệ an", "tuyên quang", "thái nguyên", "quảng ninh", "cà mau",
    "đồng nai", "phước tân", "biên hòa", "biên hoà", "cao tốc biên hòa", "long thành", "trảng bom", "nhơn trạch", "vĩnh cửu"
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
    "27443549455269648", "CBMipwJBVV", "ebaf5b0296b9cca6", "7613569837301894421",
    "7446012976617819410", "7480104626914708743", "7554971423815568658", "7561995599252442375",
    "756869738999372519", "7562572658307501330", "7367300831223254289", "7507221805120212267",
    "7359100999908265232", "7561663835577339144", "7371059034629229831", "642797025525422",
    "1399999890746196", "1345459492299720", "5671640929613047", "727427766642211",
    "433896542542198"
]

# Ma trận truy vấn nhanh tập trung vào các điểm ngập nhạy cảm nhất TP.HCM
LIVE_HOTSPOT_QUERIES = [
    # Nhóm 1: Rốn triều cường & mưa lớn Q7, Nhà Bè, Bình Thạnh
    ('site:tiktok.com "Trần Xuân Soạn" "ngập"', "tiktok"),
    ('site:tiktok.com "Huỳnh Tấn Phát" "ngập"', "tiktok"),
    ('site:tiktok.com "Lê Văn Lương" "ngập"', "tiktok"),
    ('site:tiktok.com "Ung Văn Khiêm" "ngập"', "tiktok"),
    ('site:tiktok.com "Nguyễn Xí" "ngập"', "tiktok"),
    ('site:tiktok.com "Đinh Bộ Lĩnh" "ngập"', "tiktok"),
    ('site:tiktok.com "Thảo Điền" "ngập"', "tiktok"),
    ('site:tiktok.com "Võ Văn Ngân" "ngập"', "tiktok"),
    ('site:tiktok.com "Phan Huy Ích" "ngập"', "tiktok"),
    ('site:tiktok.com "Nguyễn Văn Quá" "ngập"', "tiktok"),
    ('site:tiktok.com "Mễ Cốc" "ngập"', "tiktok"),
    ('site:tiktok.com "Hồ Học Lãm" "ngập"', "tiktok"),
    ('site:tiktok.com "mưa ngập" "Sài Gòn"', "tiktok"),
    ('site:tiktok.com "ngập lụt" "TPHCM"', "tiktok"),
    ('site:tiktok.com "xe chết máy" "TPHCM"', "tiktok"),

    ('site:facebook.com "Trần Xuân Soạn" "ngập"', "facebook"),
    ('site:facebook.com "Huỳnh Tấn Phát" "ngập"', "facebook"),
    ('site:facebook.com "Lê Văn Lương" "ngập"', "facebook"),
    ('site:facebook.com "Ung Văn Khiêm" "ngập"', "facebook"),
    ('site:facebook.com "Nguyễn Xí" "ngập"', "facebook"),
    ('site:facebook.com "Thảo Điền" "ngập"', "facebook"),
    ('site:facebook.com "Võ Văn Ngân" "ngập"', "facebook"),
    ('site:facebook.com "Phan Huy Ích" "ngập"', "facebook"),
    ('site:facebook.com "Mễ Cốc" "ngập"', "facebook"),
    ('site:facebook.com "mưa lớn gây ngập" "Sài Gòn"', "facebook"),
    ('site:facebook.com "triều cường" "Sài Gòn" "ngập"', "facebook"),
    ('site:facebook.com "đường ngập" "chết máy" "TPHCM"', "facebook"),
    ('site:facebook.com "Dĩ An" "ngập"', "facebook"),
    ('site:facebook.com "Vũng Tàu" "ngập"', "facebook"),
]


class LiveFreeSocialCrawler:
    """
    Crawler thu thập thời gian thực (Live Stream Ingestion) hoàn toàn miễn phí.
    """
    def __init__(self):
        self.seen_urls: Set[str] = set()
        self.seen_hashes: Set[str] = set()

    def is_valid_content(self, text: str) -> bool:
        clean = clean_stream_text(text)
        if not clean or len(clean) < 15:
            return False
        clean_low = clean.lower()

        if contains_spam_or_noise(clean):
            return False
        for junk in JUNK_EXCLUSIONS:
            if junk in clean_low:
                return False

        for out_loc in OUT_OF_SCOPE_LOCATIONS:
            pat = r'(?:\\b|^|#)' + re.escape(out_loc) + r'(?:\\b|$|[#\\s.,!?])'
            if re.search(pat, clean_low):
                if not any(k in clean_low for k in ["tphcm", "tp.hcm", "sài gòn", "bình dương", "vũng tàu"]):
                    return False

        has_flood = any(k in clean_low for k in FLOOD_INTENT_KEYWORDS)
        if not has_flood:
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
            m_vid = re.search(r'/video/(\\d+)', url)
            if m_vid:
                item_id = m_vid.group(1)
        elif platform == "facebook":
            m_page = re.search(r'facebook\\.com/([^/?#]+)', url)
            if m_page and m_page.group(1) not in ["groups", "watch", "reel", "story.php", "permalink.php"]:
                author = m_page.group(1)
            m_post = re.search(r'/(?:posts|videos|reel)/([a-zA-Z0-9_.-]+)', url)
            if m_post:
                item_id = m_post.group(1)

        return author, item_id

    def poll_live_stream(
        self,
        window_minutes: int = 120,
        max_queries: int = 12,
        max_items_per_query: int = 10
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Quét luồng thời gian thực cho Live Mode:
        - Lọc các bài đăng trong cửa sổ window_minutes (mặc định 120 phút).
        - Trả về danh sách standardized live events sẵn sàng cho Kafka Producer hoặc PySpark.
        """
        current_time = int(time.time())
        cutoff_time = current_time - (window_minutes * 60)

        events_window = []
        events_recent = []
        total_scanned = 0

        # Lấy tập truy vấn trọng điểm
        active_queries = LIVE_HOTSPOT_QUERIES[:max_queries]

        for query, platform in active_queries:
            enc_q = urllib.parse.quote_plus(query)
            feed_url = f"https://news.google.com/rss/search?q={enc_q}&hl=vi&gl=VN&ceid=VN:vi"

            try:
                feed = feedparser.parse(feed_url)
            except Exception:
                continue

            entries = feed.entries[:max_items_per_query]
            for entry in entries:
                total_scanned += 1
                raw_title = getattr(entry, "title", "") or ""
                clean_title = re.sub(r'\\s*-\\s*(?:TikTok|Facebook)\\s*$', '', raw_title, flags=re.IGNORECASE).strip()

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

                # Kiểm tra đúng domain nền tảng
                if platform == "tiktok" and "tiktok.com" not in decoded_url.lower():
                    continue
                if platform == "facebook" and "facebook.com" not in decoded_url.lower():
                    continue

                # Xác định thời gian đăng bài
                pub_parsed = getattr(entry, "published_parsed", None)
                if pub_parsed:
                    pub_unix = int(time.mktime(pub_parsed))
                else:
                    pub_unix = current_time

                pub_iso = datetime.fromtimestamp(pub_unix, timezone.utc).isoformat()
                author_name, post_id = self.extract_author_and_id(decoded_url, platform)

                canonical_id = f"{platform}_{post_id}"

                self.seen_urls.add(decoded_url)
                self.seen_hashes.add(c_hash)

                event = {
                    "id": str(post_id),
                    "canonical_id": canonical_id,
                    "url": decoded_url,
                    "platform": platform,
                    "media_type": "video" if platform == "tiktok" else "post",
                    "author": author_name,
                    "text": clean_title,
                    "title": clean_title,
                    "create_time": pub_unix,
                    "created_at_iso": pub_iso,
                    "timestamp": pub_unix,
                    "crawler_source": "live_free_social_crawler"
                }

                if pub_unix >= cutoff_time:
                    events_window.append(event)
                else:
                    events_recent.append(event)

            time.sleep(0.15)

        # Sắp xếp bài mới nhất lên đầu
        events_window.sort(key=lambda x: x.get("create_time", 0), reverse=True)

        stats = {
            "mode": "live",
            "crawler": "live_free_social_crawler",
            "current_time": current_time,
            "total_scanned": total_scanned,
            "events_window_count": len(events_window),
            "events_recent_count": len(events_recent),
            "window_minutes": window_minutes,
            "active_window": f"{window_minutes // 60} giờ qua" if window_minutes >= 60 else f"{window_minutes} phút"
        }

        return events_window, stats


if __name__ == "__main__":
    crawler = LiveFreeSocialCrawler()
    print("[*] Đang thử nghiệm quét Live Free Social Crawler (Cửa sổ 120 phút)...")
    events, stats = crawler.poll_live_stream(window_minutes=120, max_queries=6)
    print(f"[+] Kết quả quét Live:")
    print(f"  - Tổng số ứng viên quét: {stats['total_scanned']}")
    print(f"  - Bài đăng trong cửa sổ {stats['active_window']}: {len(events)}")
    for ev in events[:5]:
        print(f"    * [{ev['platform'].upper()}] {ev['text'][:70]}... ({ev['url']})")
