# -*- coding: utf-8 -*-
"""
pipeline/threads_crawler.py
Module Khai Thác Kho Dữ Liệu Mạng Xã Hội Threads (Instagram Threads) Chuyên Sâu:
Kiến trúc 4 Trụ Cột Cho Heatmap Đa Luồng:
1. Trụ cột 1: Phân loại theo Cụm Mục / Topics & Ngữ cảnh đời thường (Spoken natural language)
   - Bỏ hoàn toàn phụ thuộc vào hashtag (do Threads giới hạn tối đa 1 thẻ chủ đề).
   - Quét theo 3 cụm mục tiêu: Cảm thán đời thường tan tầm, Hotspots sinh viên/văn phòng, Topic slugs.
2. Trụ cột 2: Cơ chế Bóc tách Đa tầng (DuckDuckGo Lite Discovery + Headless Reader)
   - Bóc tách Markdown DOM, lấy trọn vẹn văn bản, tác giả, ngày giờ thực tế và ảnh hiện trường.
3. Trụ cột 3: Radar Tài Khoản Thực Địa TP.HCM (Targeted Account Radar)
   - Giám sát danh sách 35+ tài khoản cộng đồng, sinh viên, đời sống tại các "rốn ngập" (Thủ Đức, D2 Bình Thạnh, Q7).
4. Trụ cột 4: Chuẩn hóa Luồng Sự Kiện GIS Đa luồng cho Heatmap & Apache Kafka
   - Phân giải tọa độ tự động qua Gazetteer chuẩn NQ 1685.
   - Chuẩn hóa schema đồng bộ 100% với TikTok, Facebook và YouTube.
"""

import os
import sys
import re
import json
import time
import base64
import hashlib
import calendar
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Set, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import requests
from bs4 import BeautifulSoup

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.gazetteer import match_all_hotspots, HOTSPOTS
from pipeline.event_processor import clean_stream_text, format_relative_time

# =============================================================================
# TRỤ CỘT 1: MA TRẬN CỤM MỤC / CHỦ ĐỀ & TỪ NGỮ ĐỜI THƯỜNG (KHÔNG DÙNG HASHTAG)
# =============================================================================

# Cụm 1: Cảm thán đời thường & tình huống ngập nước lúc tan tầm của giới trẻ TP.HCM
SPOKEN_FLOOD_QUERIES = [
    "bơi về nhà Sài Gòn",
    "xe chết máy ngập",
    "lội nước bì bõm Sài Gòn",
    "ngập lút bánh xe TPHCM",
    "Sài Gòn thất thủ ngập",
    "dắt bộ ngập nước",
    "nước tràn vào phòng trọ",
    "ngập quá trời Sài Gòn",
    "đường thành sông Sài Gòn",
    "ướt như chuột lội nước",
    "triều cường dâng cao TPHCM",
    "mưa to ngập nặng Sài Gòn",
    "kẹt xe ngập nước tan tầm",
    "lội nước về nhà TPHCM",
    "nước ngập tới đầu gối",
    "đẩy xe chết máy ngập"
]

# Cụm 2: Tọa độ Hotspots văn phòng / trường đại học / sinh viên check-in
HOTSPOT_THREAD_QUERIES = [
    "Thảo Điền ngập",
    "Ung Văn Khiêm ngập",
    "D2 Nguyễn Gia Trí ngập",
    "Võ Văn Ngân ngập",
    "Chợ Thủ Đức ngập",
    "Kha Vạn Cân ngập",
    "Trần Xuân Soạn ngập",
    "Huỳnh Tấn Phát ngập",
    "Lê Văn Lương ngập",
    "Nguyễn Văn Quá ngập",
    "Phan Huy Ích ngập",
    "Kinh Dương Vương ngập",
    "Hồ Học Lãm ngập",
    "Bến Phú Định ngập",
    "Bình Quới ngập",
    "Thanh Đa ngập",
    "Cầu Bình Triệu ngập",
    "Đỗ Xuân Hợp ngập",
    "Tô Ngọc Vân ngập",
    "Lương Định Của ngập"
]

# Cụm 3: Các Topic Slugs chính thức trên Threads
THREADS_OFFICIAL_TOPICS = [
    "sài-gòn",
    "mưa-sài-gòn",
    "ngập-nước",
    "triều-cường",
    "giao-thông-tphcm",
    "thời-tiết-sài-gòn"
]

# =============================================================================
# TRỤ CỘT 3: RADAR CÁC TÀI KHOẢN CỘNG ĐỒNG & SINH VIÊN RỐN NGẬP TP.HCM
# =============================================================================
TARGET_RADAR_ACCOUNTS = [
    # Cộng đồng đời sống TP.HCM
    "saigon.ngaynay",
    "yeusaigon",
    "chuyencuasaigon",
    "checkinsaigon",
    "tphcm24h",
    "nguoisaigon",
    "saigondauthe",
    "saigon_traffic",
    "saigon_weather_vibes",
    # Sinh viên & Trường học tại các khu vực rốn ngập (Thủ Đức, Bình Thạnh, Q7)
    "sinhvien.hutech",       # D2 Ung Văn Khiêm
    "hutech_confessions",
    "hutech_memes",
    "sinhvien_vanlang",      # Bình Thạnh / Gò Vấp
    "vlu_confessions",
    "sinhvien_uit",          # Thủ Đức
    "uit_confessions",
    "bachkhoa_hcmut",        # Q10 / Thủ Đức
    "ueh_confessions",       # Q5 / Nam Sài Gòn
    "kinhteluat_uel",        # Thủ Đức
    "langdaithuduc",
    # Khu vực dân cư trũng thấp
    "thaodien_community",    # Thảo Điền Q2
    "quan7_saigon",          # Trần Xuân Soạn / Huỳnh Tấn Phát
    "binhthanh_review"       # Thanh Đa / Bình Quới
]


# =============================================================================
# TRỤ CỘT 2: CƠ CHẾ DISCOVERY (WEB DISCOVERY + HEADLESS READER)
# =============================================================================

def find_threads_via_ddg_lite(query: str, max_results: int = 5) -> Set[str]:
    """Tìm link Threads qua DuckDuckGo Lite không cần API key."""
    url = "https://lite.duckduckgo.com/lite/"
    data = {"q": f"site:threads.net {query}"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    found = set()
    try:
        resp = requests.post(url, data=data, headers=headers, timeout=6)
        pattern = r"https?://(?:www\.)?threads\.net/@([a-zA-Z0-9_.-]+)/post/([a-zA-Z0-9_.-]+)"
        for m in re.finditer(pattern, resp.text):
            found.add(f"https://www.threads.net/@{m.group(1)}/post/{m.group(2)}")
            if len(found) >= max_results:
                break
    except Exception:
        pass
    return found


def fetch_threads_post_via_jina(post_url: str) -> Optional[Dict[str, Any]]:
    """Bóc tách chi tiết bài viết Threads bằng Jina Reader."""
    jina_url = f"https://r.jina.ai/{post_url}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/plain"
    }

    try:
        resp = requests.get(jina_url, headers=headers, timeout=4)
        if resp.status_code != 200:
            return None
        md_text = resp.text
    except Exception:
        return None

    # Trích xuất tác giả
    author_m = re.search(r'Title:.*?\(@([a-zA-Z0-9_.-]+)\)', md_text)
    if not author_m:
        author_m = re.search(r'threads\.net/@([a-zA-Z0-9_.-]+)', post_url)
    author = author_m.group(1) if author_m else "threads_user"

    # Trích xuất ID bài viết
    id_m = re.search(r'/post/([a-zA-Z0-9_.-]+)', post_url)
    post_id = id_m.group(1) if id_m else hashlib.md5(post_url.encode("utf-8")).hexdigest()[:16]

    # Trích xuất thời gian đăng bài
    now_ts = int(time.time())
    pub_ts = now_ts
    date_m = re.search(r'\[(\d{1,2}/\d{1,2}/\d{2,4})\]', md_text)
    if date_m:
        raw_d = date_m.group(1)
        try:
            parts = raw_d.split("/")
            year = int(parts[2])
            if year < 100: year += 2000
            month = int(parts[0])
            day = int(parts[1])
            dt = datetime(year, month, day, 12, 0, 0, tzinfo=timezone.utc)
            pub_ts = int(dt.timestamp())
        except Exception:
            pass
    else:
        # Nhận diện relative time (ví dụ: 1h, 2h, 30m)
        rel_m = re.search(r'\b(\d+)\s*(h|m|d|giờ|phút|ngày)\s*ago\b', md_text, re.IGNORECASE)
        if rel_m:
            val = int(rel_m.group(1))
            unit = rel_m.group(2).lower()
            if unit in ["m", "phút"]:
                pub_ts = now_ts - val * 60
            elif unit in ["h", "giờ"]:
                pub_ts = now_ts - val * 3600
            elif unit in ["d", "ngày"]:
                pub_ts = now_ts - val * 86400

    # Trích xuất media URLs (ảnh hiện trường cdn)
    media_urls = re.findall(r'!\[.*?\]\((https://[^\s)]+(?:cdninstagram|scontent|fbcdn)[^\s)]+)\)', md_text)

    # Trích xuất thân bài viết
    lines = [l.strip() for l in md_text.split("\n") if l.strip()]
    content_lines = []
    capture = False

    for l in lines:
        if "[Thread](" in l or "views" in l or "Markdown Content:" in l:
            capture = True
            continue
        if capture:
            if any(term in l for term in ["Related threads", "Log in to like", "Reply to", "Report a problem", "Translate post"]):
                break
            if l.startswith("![") or l.startswith("[Log in") or l.startswith("[Translate"):
                continue
            if l.startswith("[") and l.endswith(")") and len(l) < 50:
                continue
            if len(l) > 6:
                content_lines.append(l)

    text = " ".join(content_lines).strip()
    if not text or len(text) < 10:
        desc_m = re.search(r'Description:\s*(.*?)(?:\n\n|\Z)', md_text, re.DOTALL)
        if desc_m:
            text = desc_m.group(1).strip()
        else:
            text = f"Phản ánh ngập nước thực địa từ @{author} trên Threads"

    return {
        "post_id": post_id,
        "author": author,
        "url": post_url,
        "text": text,
        "pub_timestamp": pub_ts,
        "media_urls": media_urls
    }


# =============================================================================
# TRỤ CỘT 4: ENGINE KHAI THÁC THREADS ĐA LUỒNG CHO STREAMING HEATMAP
# =============================================================================

class ThreadsMultiStreamCrawler:
    """
    Crawler Chuyên Sâu Threads Khai Thác Đa Nguồn:
    - Quét song song đa luồng
    - Hợp nhất Topic Queries, Spoken Queries và Account Radar
    - Tự động map tọa độ GIS với Gazetteer TP.HCM (NQ 1685)
    - Tương thích 100% với Kafka Topic social.live.raw & Leaflet Heatmap
    """

    def __init__(self, max_workers: int = 6):
        self.max_workers = max_workers
        self.seen_urls: Set[str] = set()
        self.seen_hashes: Set[str] = set()

    def discover_urls_for_queries(self, queries: List[str], max_per_query: int = 3) -> Set[str]:
        """Quét song song lấy danh sách URLs bài viết Threads."""
        urls = set()
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(queries) or 1)) as pool:
            futures = [pool.submit(find_threads_via_ddg_lite, q, max_per_query) for q in queries]
            for f in as_completed(futures):
                try:
                    res = f.result()
                    if res:
                        urls.update(res)
                except Exception:
                    pass
        return urls

    def scan_account_radar_urls(self, accounts: List[str], max_per_acc: int = 2) -> Set[str]:
        """Quét các bài đăng gần nhất từ Radar tài khoản cộng đồng TP.HCM."""
        radar_queries = [f"site:threads.net/@{acc} (ngập OR mưa OR triều cường OR kẹt xe)" for acc in accounts[:8]]
        return self.discover_urls_for_queries(radar_queries, max_per_query=max_per_acc)

    def is_valid_flood_post(self, text: str) -> bool:
        """Kiểm tra bài đăng có mang ngữ cảnh ngập lụt thực tế TP.HCM."""
        low = text.lower()
        # Loại trừ rác & F&B
        junk_terms = [
            "khuyến mãi", "ưu đãi", "giảm giá", "voucher", "bất động sản", "cho thuê",
            "bán nhà", "sushi", "pizza", "tacos", "buffet", "tràn ngập quà", "ngập tràn niềm vui"
        ]
        if any(j in low for j in junk_terms):
            return False

        flood_signals = [
            "ngập", "lụt", "triều cường", "chết máy", "lút bánh", "dắt bộ", "bì bõm",
            "thất thủ", "biển nước", "nước dâng", "nước tràn", "đường thành sông", "bơi về"
        ]
        has_flood = any(s in low for s in flood_signals)
        if not has_flood:
            return False

        hcm_signals = [
            "sài gòn", "tphcm", "tp.hcm", "hồ chí minh", "thủ đức", "bình thạnh", "quận 7",
            "thảo điền", "ung văn khiêm", "trần xuân soạn", "huỳnh tấn phát", "nguyễn văn quá",
            "d2", "nguyễn gia trí", "võ văn ngân", "quốc hương", "hồ học lãm", "bình quới"
        ]
        has_hcm = any(h in low for h in hcm_signals)
        return has_hcm

    def extract_gis_location(self, text: str) -> Dict[str, Any]:
        """Tự động phân giải vị trí GIS từ văn bản bài đăng Threads."""
        matches = match_all_hotspots(text)
        if matches:
            top_m = matches[0]
            lat = top_m.get("lat", 10.7769)
            lon = top_m.get("lon", 106.7009)
            street = top_m.get("street") or top_m.get("matched_name", "Điểm ngập TP.HCM")
            ward = top_m.get("ward", "Phường Bến Nghé")
            return {
                "street": street,
                "display_name": street,
                "ward": ward,
                "administrative_unit": ward,
                "district": "TP.HCM",
                "lat": lat,
                "lon": lon,
                "heat_points": [[lat, lon]],
                "cause": "rain",
                "cause_label": "Mưa lớn gây ngập đô thị",
                "source": "threads_nlp_gazetteer"
            }

        # Fallback tọa độ trung tâm TP.HCM nếu là tin diện rộng
        return {
            "street": "Khu vực TP. Hồ Chí Minh",
            "display_name": "Toàn thành phố Hồ Chí Minh (Diện rộng)",
            "ward": "Toàn TP.HCM",
            "administrative_unit": "Toàn TP.HCM",
            "district": "TP.HCM",
            "lat": 10.7769,
            "lon": 106.7009,
            "heat_points": [[10.7769, 106.7009]],
            "cause": "rain",
            "cause_label": "Phản ánh ngập diện rộng",
            "source": "threads_nlp_fallback"
        }

    def poll_threads_live(
        self,
        window_minutes: int = 120,
        max_items: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Thu thập các bài đăng Threads thời gian thực:
        1. Kết hợp Spoken Queries + Hotspot Queries + Account Radar
        2. Tải bài viết và lọc rác
        3. Gán nhãn GIS và tạo event chuẩn
        """
        now_ts = int(time.time())
        cutoff_ts = now_ts - (window_minutes * 60)

        # 1. Hợp nhất truy vấn theo Trụ cột 1 & 3
        active_queries = SPOKEN_FLOOD_QUERIES[:4] + HOTSPOT_THREAD_QUERIES[:4]
        discovered_urls = self.discover_urls_for_queries(active_queries, max_per_query=2)
        radar_urls = self.scan_account_radar_urls(TARGET_RADAR_ACCOUNTS[:5], max_per_acc=1)
        all_candidate_urls = (discovered_urls | radar_urls) - self.seen_urls

        events = []
        if not all_candidate_urls:
            return events

        # 2. Bóc tách nội dung song song (Trụ cột 2)
        with ThreadPoolExecutor(max_workers=min(6, len(all_candidate_urls))) as pool:
            futures = {pool.submit(fetch_threads_post_via_jina, u): u for u in list(all_candidate_urls)[:max_items]}
            for f in as_completed(futures):
                try:
                    post = f.result()
                    if not post:
                        continue

                    raw_text = post.get("text", "")
                    if not self.is_valid_flood_post(raw_text):
                        continue

                    text_hash = hashlib.md5(raw_text.strip().lower().encode("utf-8")).hexdigest()
                    if text_hash in self.seen_hashes:
                        continue
                    self.seen_hashes.add(text_hash)
                    self.seen_urls.add(post["url"])

                    pub_ts = post.get("pub_timestamp", now_ts)
                    # Giới hạn 24h
                    if now_ts - pub_ts > 86400:
                        continue

                    loc = self.extract_gis_location(raw_text)

                    # Bóc tách Aspect / Opinion sơ bộ (sẽ được PhoBERT tinh chỉnh)
                    opinion_candidate = "ngập sâu"
                    for op in ["ngập sâu", "chết máy", "bì bõm", "lút bánh", "dắt bộ", "thất thủ", "ngập nước", "sóng đánh"]:
                        if op in raw_text.lower():
                            opinion_candidate = op
                            break

                    severity = "high" if any(w in raw_text.lower() for w in ["chết máy", "lút bánh", "thất thủ", "biển nước", "ngập sâu"]) else "medium"

                    event = {
                        "id": post["post_id"],
                        "canonical_id": f"threads_{post['post_id']}",
                        "platform": "threads",
                        "media_type": "image" if post.get("media_urls") else "post",
                        "author": post["author"],
                        "text": raw_text,
                        "title": raw_text[:90],
                        "url": post["url"],
                        "media_urls": post.get("media_urls", []),
                        "video_url": None,
                        "create_time": pub_ts,
                        "timestamp": pub_ts,
                        "relative_time": format_relative_time(pub_ts, now_ts),
                        "location": loc,
                        "aspect": loc.get("street", "Điểm ngập TP.HCM"),
                        "opinion": opinion_candidate,
                        "severity": severity,
                        "weight": 1.4, # Ưu tiên mạng xã hội Threads
                        "report_count": 1,
                        "source": "threads_multi_stream_crawler"
                    }
                    events.append(event)
                    if len(events) >= max_items:
                        break
                except Exception:
                    pass

        return events


# Thử nghiệm chạy độc lập
if __name__ == "__main__":
    print("=" * 80)
    print("KIỂM THỬ MODULE THREADS MULTI-STREAM CRAWLER")
    print("=" * 80)
    crawler = ThreadsMultiStreamCrawler(max_workers=6)
    print("[*] Đang chạy quét Threads thời gian thực theo Cụm Mục & Radar...")
    t0 = time.time()
    res_events = crawler.poll_threads_live(window_minutes=240, max_items=5)
    print(f"[+] Hoàn tất quét sau {time.time() - t0:.2f}s! Tìm thấy: {len(res_events)} bài đăng ngập lụt.")
    for ev in res_events:
        print(f"  * [@{ev['author']}] {ev['aspect']} -> {ev['opinion']} ({ev['severity'].upper()}): {ev['title'][:60]}...")
        print(f"    URL: {ev['url']}")
