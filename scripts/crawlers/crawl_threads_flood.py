#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/crawl_threads_flood.py
--------------------------------------------------------------------------------
Module cào dữ liệu mạng xã hội Threads (threads.net) hoàn toàn MIỄN PHÍ:
- 100% Zero-cost & No API key needed.
- Kết hợp Discovery Search (DuckDuckGo Lite & Bing Search Decoded) để tìm URL bài đăng thực tế.
- Khai thác công nghệ Render Headless Parser (Jina Reader) để vượt qua SPA JavaScript
  và cơ chế chặn bot của Meta mà không vi phạm bảo mật.
- Chuẩn hóa đầu ra 100% đồng bộ với schema raw của dự án (TikTok, Facebook, YouTube).
- Tự động phân luồng bài viết vào từng thư mục Episode tương ứng:
  data/raw/episodes/{episode_id}/threads_raw.json
- Tích hợp bộ lọc ngữ cảnh ngập lụt thực tế TP.HCM và loại bỏ rác/F&B/quảng cáo.
"""

import os
import sys
import re
import json
import time
import base64
import hashlib
import urllib.parse
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, Any, List, Set, Optional, Tuple

import requests
from bs4 import BeautifulSoup

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

DATA_DIR = os.path.join(ROOT_DIR, "data")
EPISODES_DIR = os.path.join(DATA_DIR, "raw", "episodes")

from scripts.crawlers.organize_raw_episodes import determine_episode_id
from scripts.crawlers.free_social_crawler import (
    FLOOD_INTENT_KEYWORDS,
    HCMC_AFFIRMATION_KEYWORDS,
    JUNK_EXCLUSIONS,
    OUT_OF_SCOPE_LOCATIONS,
    is_valid_hcmc_flood_content
)

# Danh sách truy vấn chủ đề ngập lụt thực tế trên Threads
THREADS_SEARCH_QUERIES = [
    # Cụm 1: Cảm thán đời thường & giờ tan tầm của giới trẻ TP.HCM (Spoken natural language)
    "bơi về nhà Sài Gòn",
    "xe chết máy ngập",
    "lội nước bì bõm Sài Gòn",
    "lút bánh xe TPHCM",
    "Sài Gòn thất thủ ngập",
    "dắt bộ ngập nước",
    "nước tràn vào nhà TPHCM",
    "nước tràn vào phòng trọ",
    "ngập quá trời Sài Gòn",
    "đường thành sông Sài Gòn",
    "ướt như chuột lội nước",
    "kẹt xe ngập nước tan tầm",
    "lội nước về nhà TPHCM",
    "nước ngập tới đầu gối",
    "đẩy xe chết máy ngập",
    "mưa to ngập nặng Sài Gòn",
    "triều cường dâng cao TPHCM",
    
    # Cụm 2: Tọa độ Hotspots sinh viên/dân văn phòng hay check-in (Trọng điểm)
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
    "Lương Định Của ngập",
    
    # Cụm 3: Radar tài khoản sinh viên & cộng đồng TP.HCM
    "site:threads.net/@sinhvien.hutech ngập",
    "site:threads.net/@hutech_confessions ngập",
    "site:threads.net/@sinhvien_vanlang ngập",
    "site:threads.net/@sinhvien_uit ngập",
    "site:threads.net/@saigon.ngaynay ngập",
    "site:threads.net/@yeusaigon ngập",
    "site:threads.net/@chuyencuasaigon ngập",
    "site:threads.net/@checkinsaigon ngập"
]


def find_threads_urls_ddg(query: str) -> Set[str]:
    """Tìm link Threads qua DuckDuckGo Lite mà không cần API key."""
    url = "https://lite.duckduckgo.com/lite/"
    data = {"q": f"site:threads.net {query}"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    found = set()
    try:
        resp = requests.post(url, data=data, headers=headers, timeout=12)
        pattern = r"https?://(?:www\.)?threads\.net/@([a-zA-Z0-9_.-]+)/post/([a-zA-Z0-9_.-]+)"
        for m in re.finditer(pattern, resp.text):
            found.add(f"https://www.threads.net/@{m.group(1)}/post/{m.group(2)}")
    except Exception:
        pass
    return found


def find_threads_urls_bing(query: str) -> Set[str]:
    """Tìm link Threads qua Bing Search và giải mã Base64 URL chuyển hướng."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "vi,en;q=0.9",
    }
    found = set()
    url = f"https://www.bing.com/search?q={urllib.parse.quote('site:threads.net ' + query)}"
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if "/ck/a?" in href:
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                u = parsed.get("u", [""])[0]
                if u.startswith("a1"):
                    try:
                        raw_b64 = u[2:]
                        raw_b64 += "=" * ((4 - len(raw_b64) % 4) % 4)
                        decoded = base64.b64decode(raw_b64).decode("utf-8", errors="ignore")
                        m = re.search(r"https?://(?:www\.)?threads\.net/@([a-zA-Z0-9_.-]+)/post/([a-zA-Z0-9_.-]+)", decoded)
                        if m:
                            found.add(f"https://www.threads.net/@{m.group(1)}/post/{m.group(2)}")
                    except Exception:
                        pass
    except Exception:
        pass
    return found


def fetch_threads_post_via_jina(post_url: str) -> Optional[Dict[str, Any]]:
    """Bóc tách bài đăng Threads bằng Jina Reader."""
    jina_url = f"https://r.jina.ai/{post_url}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/plain"
    }

    try:
        resp = requests.get(jina_url, headers=headers, timeout=18)
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

    # Trích xuất ngày đăng
    date_m = re.search(r'\[(\d{2}/\d{2}/\d{2,4})\]', md_text)
    pub_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if date_m:
        raw_d = date_m.group(1)
        try:
            parts = raw_d.split("/")
            if len(parts[2]) == 2:
                year = f"20{parts[2]}"
            else:
                year = parts[2]
            pub_date_str = f"{year}-{parts[0]}-{parts[1]}"
        except Exception:
            pass

    # Trích xuất media URLs (nếu có ảnh đính kèm)
    media_urls = re.findall(r'!\[.*?\]\((https://scontent[^\s)]+)\)', md_text)

    # Trích xuất thân bài đăng
    lines = [l.strip() for l in md_text.split("\n") if l.strip()]
    content_lines = []
    capture = False

    for l in lines:
        if "[Thread](" in l or "views" in l:
            capture = True
            continue
        if capture:
            if any(term in l for term in ["Related threads", "Log in to like", "Reply to", "Report a problem"]):
                break
            if l.startswith("![") or l.startswith("[Log in") or l.startswith("[Translate"):
                continue
            if l.startswith("[") and l.endswith(")") and len(l) < 50:
                continue
            if len(l) > 10:
                content_lines.append(l)

    text = " ".join(content_lines).strip()
    if not text:
        # Fallback từ meta tag description nếu có
        desc_m = re.search(r'Markdown Content:\s*(.*?)(?:\n\n|\Z)', md_text, re.DOTALL)
        if desc_m:
            text = desc_m.group(1).strip()
        else:
            text = f"Cập nhật ngập lụt thực địa từ @{author} trên Threads"

    return {
        "post_id": post_id,
        "author": author,
        "url": post_url,
        "text": text,
        "pub_date": pub_date_str,
        "media_urls": media_urls
    }


def run_threads_crawler():
    print("=" * 80)
    print("🚀 KHỞI ĐỘNG CÔNG CỤ CÀO THREADS MIỄN PHÍ ĐỒNG BỘ SCHEMA EPISODE")
    print(f"📌 Tổng số câu truy vấn: {len(THREADS_SEARCH_QUERIES)}")
    print("=" * 80)

    # Đọc URL và content hash đã có để chống trùng lặp
    existing_urls = set()
    if os.path.exists(EPISODES_DIR):
        for root, _, files in os.walk(EPISODES_DIR):
            for fname in files:
                if fname.endswith(".json"):
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8-sig") as fp:
                            items = json.load(fp)
                            if isinstance(items, list):
                                for it in items:
                                    u = it.get("url")
                                    if u: existing_urls.add(u)
                    except Exception:
                        pass

    new_items_by_episode = defaultdict(list)
    total_found = 0
    total_added = 0
    filtered_count = 0
    discovered_urls = set()

    # Bước 1: Thu thập URL ứng viên qua DDG Lite & Bing
    for q in THREADS_SEARCH_QUERIES:
        ddg_urls = find_threads_urls_ddg(q)
        bing_urls = find_threads_urls_bing(q)
        combined = ddg_urls | bing_urls
        for u in combined:
            if u not in existing_urls and u not in discovered_urls:
                discovered_urls.add(u)
        time.sleep(0.3)

    print(f"[*] Tổng số URL bài đăng Threads độc nhất phát hiện: {len(discovered_urls)}")

    # Bước 2: Bóc tách nội dung từng bài qua Jina Reader
    for u in discovered_urls:
        total_found += 1
        post_data = fetch_threads_post_via_jina(u)
        if not post_data:
            continue

        text = post_data["text"]

        # Lọc sạch nội dung rác và kiểm tra hợp lệ ngập lụt TP.HCM
        if not is_valid_hcmc_flood_content(text):
            filtered_count += 1
            continue

        pub_date = post_data["pub_date"]
        iso_str = datetime.now(timezone.utc).isoformat()
        ep_id = determine_episode_id(pub_date)

        # Chuẩn hóa 100% theo đúng Schema Raw của dự án
        raw_record = {
            "id": post_data["post_id"],
            "url": u,
            "webVideoUrl": "",
            "mediaUrls": post_data["media_urls"],
            "text": text,
            "title": text[:80],
            "author": post_data["author"],
            "authorMeta": {"name": post_data["author"]},
            "createTimeISO": iso_str,
            "published": pub_date,
            "extracted_date": pub_date,
            "platform": "threads",
            "crawled_at": iso_str,
            "crawler_source": "free_threads_engine"
        }

        new_items_by_episode[ep_id].append(raw_record)
        total_added += 1
        time.sleep(1.0)

    print("\n" + "=" * 80)
    print("KẾT QUẢ THU THẬP THREADS:")
    print(f"  * Tổng số URL ứng viên: {total_found}")
    print(f"  * Bị loại do không hợp lệ/rác: {filtered_count}")
    print(f"  * SỐ BÀI ĐĂNG THREADS ĐẠT CHUẨN THÊM VÀO: {total_added}")
    print("=" * 80)

    # Bước 3: Lưu vào data/raw/episodes/{episode_id}/threads_raw.json
    for ep_id, items in new_items_by_episode.items():
        ep_dir = os.path.join(EPISODES_DIR, ep_id)
        os.makedirs(ep_dir, exist_ok=True)
        target_path = os.path.join(ep_dir, "threads_raw.json")

        existing_items = []
        if os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8-sig") as fp:
                    existing_items = json.load(fp)
                    if not isinstance(existing_items, list):
                        existing_items = []
            except Exception:
                existing_items = []

        # Hợp nhất chống trùng lặp theo ID/URL
        merged_dict = {}
        for it in existing_items:
            uid = it.get("url") or it.get("id")
            if uid: merged_dict[uid] = it
        for it in items:
            uid = it.get("url") or it.get("id")
            if uid: merged_dict[uid] = it

        final_list = list(merged_dict.values())
        with open(target_path, "w", encoding="utf-8") as fp:
            json.dump(final_list, fp, ensure_ascii=False, indent=2)

        print(f"  + [{ep_id}] THREADS: Thêm {len(items)} bài -> Tổng cộng: {len(final_list)} bài (threads_raw.json)")

    print("\n-> Đã lưu trữ hoàn tất các bài đăng Threads theo chuẩn schema Episode!")


if __name__ == "__main__":
    run_threads_crawler()
