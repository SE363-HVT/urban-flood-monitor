"""
pipeline/facebook_poller.py - Module Thu Thập Dữ Liệu Ngập Lụt Từ Facebook
Tối ưu hóa tập trung duy nhất 1 Actor Search tối ưu chống checkpoint & bypass block:
1. Facebook Search Scraper (danek/facebook-search-ppr):
   - Chuyên tìm kiếm bài đăng người dùng & cộng đồng gần thời gian thực.
   - Sử dụng 1 truy vấn hợp nhất duy nhất (Consolidated Search): Gom chung cả hiện tượng ngập lụt & địa bàn TP.HCM (ví dụ: 'mưa ngập Sài Gòn').
   - Tăng quy mô thu thập trong 1 lần cào (max_posts=40..50) để tối đa hóa xác suất lấy bài chuẩn xác.
   - Không chạy quét lần 2 gây phân mảnh và tốn thời gian.
2. Chuẩn Live Mode 100% Thực Tế:
   - Trong chế độ LIVE, chỉ trả về bài đăng thật do người dùng đăng gần đây được cào từ Facebook.
   - Tuyệt đối KHÔNG fallback về kho dữ liệu có sẵn hay giả lập.
   - Kho bài đăng dataset có sẵn chỉ được dùng cho chế độ SIMULATION MODE.
3. Bộ lọc kiểm duyệt khắt khe:
   - Chặn đứng 100% bẫy chữ "deal ngập tràn", "ưu đãi ngập tràn", "pass phòng", "cho thuê phòng", "xe lướt không ngập nước".
"""

import os
import glob
import json
import time
import requests
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from core.config import (
    APIFY_TOKEN,
    FB_SEARCH_PPR_ACTOR_ID,
    FB_SEARCH_QUERIES,
    FB_SEARCH_LOCATIONS,
    DEFAULT_WINDOW_MINUTES
)
from core.state_manager import StateManager
from core.gazetteer import match_hotspot
from pipeline.event_processor import clean_stream_text, analyze_severity_heuristic, format_relative_time

REAL_FB_POOL_FILE = os.path.join("data", "real_facebook_flood_pool.json")
LAST_CRAWL_FB_FILE = os.path.join("data", "last_crawled_facebook.json")

FLOOD_INTENT_KEYWORDS = [
    "ngập", "triều cường", "chết máy", "bì bõm", "lút bánh",
    "dắt bộ", "biến thành sông", "nước dâng", "mưa ngập", "thất thủ", "ngập úng"
]

STRICT_SPAM_KEYWORDS = [
    "cho thuê", "phòng trọ", "mặt tiền", "diện tích", "sổ hồng", "sổ đỏ",
    "căn hộ", "vinhomes", "chuyển nhượng", "pass phòng", "bán nhà", "giá chỉ",
    "đáp án triết", "k52", "k51", "thi hộ", "học hộ", "duplex", "full nội thất",
    "chuyên cho thuê", "for rent", "bán gấp", "cắt lỗ", "ngộp", "hẻm xe hơi",
    "shophouse", "biệt thự", "đất nền", "thổ cư", "deal ngập tràn", "ưu đãi ngập tràn",
    "khuyến mãi ngập tràn", "ngập tràn ưu đãi",
    "không ngập nước", "không đâm đụng", "odo", "xe lướt", "số tự động",
    "số sàn", "bán xe", "vios", "accent", "trả góp", "chính chủ bán"
]


def load_real_facebook_flood_pool() -> List[Dict[str, Any]]:
    """Tải 100% bài đăng ngập lụt thực tế cho SIMULATION MODE."""
    if os.path.exists(REAL_FB_POOL_FILE):
        try:
            with open(REAL_FB_POOL_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [it for it in data if it.get("url") and "curated" not in it.get("url", "")]
        except Exception:
            return []
    return []


def extract_facebook_media_urls(item: Dict[str, Any]) -> List[str]:
    """Trích xuất liên kết hình ảnh hoặc video từ bài viết Facebook."""
    urls = []
    media_list = item.get("media", [])
    if isinstance(media_list, list):
        for m in media_list:
            if not isinstance(m, dict):
                continue
            img_uri = m.get("image", {}).get("uri") if isinstance(m.get("image"), dict) else None
            thumb = m.get("thumbnail") or (m.get("thumbnailImage", {}).get("uri") if isinstance(m.get("thumbnailImage"), dict) else None)
            video_url = m.get("browser_native_hd_url") or m.get("browser_native_sd_url") or m.get("video_url")
            chosen = img_uri or thumb or video_url
            if chosen and chosen not in urls:
                urls.append(chosen)

    if item.get("image") and item["image"] not in urls:
        urls.append(item["image"])
    if item.get("video") and item["video"] not in urls:
        urls.append(item["video"])
    return urls


def process_facebook_item(item: Dict[str, Any], reference_time: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Chuẩn hóa bài viết Facebook sang sự kiện ngập lụt tiêu chuẩn.
    Chỉ chấp nhận bài viết có URL thật từ Facebook, tuyệt đối không tạo URL ảo.
    """
    raw_text = item.get("text", "") or item.get("post_text", "") or item.get("message", "")
    if not raw_text and isinstance(item.get("sharedPost"), dict):
        raw_text = item["sharedPost"].get("text", "")

    if not raw_text or len(raw_text.strip()) < 15:
        return None

    raw_lower = raw_text.lower()

    # Chặn triệt để tin rác BĐS, cho thuê, bẫy chữ "ngập tràn", bán xe
    for spam_kw in STRICT_SPAM_KEYWORDS:
        if spam_kw in raw_lower:
            return None

    # Bắt buộc phải có ít nhất 1 từ phản ánh ngập lụt thực tế
    if not any(kw in raw_lower for kw in FLOOD_INTENT_KEYWORDS):
        return None

    cleaned_text = clean_stream_text(raw_text)
    if not cleaned_text:
        return None

    analysis = analyze_severity_heuristic(cleaned_text)
    if not analysis:
        return None

    hotspot = match_hotspot(cleaned_text)
    if not hotspot:
        return None

    # URL bài viết - BẮT BUỘC PHẢI LÀ URL THẬT
    post_url = item.get("url") or item.get("post_url")
    if not post_url or not str(post_url).startswith("https://www.facebook.com/"):
        return None
    if "_curated" in str(post_url):
        return None

    create_time = item.get("createTime") or item.get("timestamp")
    if not create_time and item.get("time"):
        try:
            time_str = str(item["time"]).replace("Z", "+00:00")
            dt = datetime.fromisoformat(time_str)
            create_time = int(dt.timestamp())
        except Exception:
            create_time = None

    if reference_time is not None:
        if not create_time or (reference_time - create_time) > 432000: # 5 ngày bao quát đợt ngập gần nhất
            return None

    author_name = "Facebook Community"
    author_raw = item.get("user") or item.get("author") or item.get("pageName")
    if isinstance(author_raw, dict):
        author_name = author_raw.get("name") or author_raw.get("username") or "Facebook User"
    elif author_raw:
        author_name = str(author_raw)

    post_id = item.get("postId") or item.get("post_id") or item.get("id") or create_time or int(time.time())

    media_urls = extract_facebook_media_urls(item)
    likes = item.get("likes") or item.get("reactionLikeCount", 0) or item.get("reactions_count", 0) or 0
    comments = item.get("comments") or item.get("comments_count", 0) or 0
    shares = item.get("shares") or item.get("reshare_count", 0) or 0

    weight = analysis["weight"]
    if media_urls:
        weight += 0.15
    if likes > 50 or comments > 20:
        weight += 0.1

    event = {
        "id": f"fb_{post_id}",
        "platform": "facebook",
        "media_type": "post" if not media_urls else ("video" if any("mp4" in u or "video" in u for u in media_urls) else "image_post"),
        "author": author_name,
        "text": cleaned_text,
        "create_time": create_time or int(time.time()),
        "created_at_iso": datetime.fromtimestamp(create_time, timezone.utc).isoformat() if create_time else "",
        "relative_time": format_relative_time(create_time, reference_time) if create_time else "Gần đây",
        "location": {
            "street": hotspot["display_name"],
            "ward": hotspot["ward"],
            "administrative_unit": hotspot.get("ward", ""),
            "district": hotspot.get("district", ""),
            "region": hotspot.get("region", "TPHCM"),
            "lat": hotspot["lat"],
            "lon": hotspot["lon"],
            "heat_points": hotspot.get("heat_points", [[hotspot["lat"], hotspot["lon"]]]),
            "type": hotspot["type"]
        },
        "aspect": hotspot["display_name"],
        "opinion": analysis["opinion"],
        "sentiment": analysis["sentiment"],
        "severity": analysis["severity_level"],
        "weight": round(min(weight, 2.0), 2),
        "url": post_url,
        "media_urls": media_urls[:3],
        "engagement": {
            "likes": likes,
            "comments": comments,
            "shares": shares
        }
    }
    return event


class FacebookPoller:
    """
    Bộ thu thập dữ liệu ngập lụt từ Facebook:
    - Thu thập 100% bài đăng thực tế của người dùng & cộng đồng qua Facebook Search Scraper.
    - Truy vấn hợp nhất duy nhất (Single Consolidated Search) kết hợp hiện tượng ngập lụt + Sài Gòn.
    - Không fallback vào dữ liệu giả lập trong chế độ Live Mode.
    """
    def __init__(self, apify_token: Optional[str] = None, state_manager: Optional[StateManager] = None):
        self.apify_token = apify_token or APIFY_TOKEN
        self.state_manager = state_manager or StateManager()

    def _wait_for_run(self, run_id: str, timeout_sec: int = 100, check_interval: int = 3) -> str:
        poll_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={self.apify_token}"
        status = "RUNNING"
        start_time = time.time()
        while time.time() - start_time < timeout_sec:
            time.sleep(check_interval)
            try:
                s_resp = requests.get(poll_url, timeout=10)
                if s_resp.status_code == 200:
                    status = s_resp.json().get("data", {}).get("status", "UNKNOWN")
                    if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                        break
            except Exception:
                pass
        return status

    def _fetch_dataset_items(self, dataset_id: str) -> List[Dict[str, Any]]:
        items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={self.apify_token}"
        resp = requests.get(items_url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def poll_search_posts_ppr(
        self,
        query: str = "mưa ngập Sài Gòn",
        max_posts: int = 40
    ) -> List[Dict[str, Any]]:
        """
        Cào tìm kiếm bài đăng người dùng qua danek/facebook-search-ppr
        (Actor chạy ổn định, bypass login checkpoint, hỗ trợ lọc bài mới).
        """
        if not self.apify_token:
            return []

        url = f"https://api.apify.com/v2/acts/{FB_SEARCH_PPR_ACTOR_ID}/runs?token={self.apify_token}"
        run_input = {
            "query": query,
            "search_type": "posts",
            "recent_posts": True,
            "max_posts": max_posts
        }

        try:
            resp = requests.post(url, json=run_input, timeout=30)
            resp.raise_for_status()
            run_data = resp.json().get("data", {})
            run_id = run_data.get("id")
            dataset_id = run_data.get("defaultDatasetId")
            print(f"[Facebook Search PPR] Actor đang chạy cho '{query}' (Run ID: {run_id})...")

            status = self._wait_for_run(run_id, timeout_sec=80)
            if status != "SUCCEEDED":
                print(f"[Facebook Search PPR] Run {run_id} kết thúc với trạng thái: {status}")
                return []

            raw = self._fetch_dataset_items(dataset_id)
            print(f"[Facebook Search PPR] Đã thu thập {len(raw)} kết quả cho '{query}'.")
            return raw
        except Exception as e:
            print(f"[Facebook Search PPR] Lỗi khi cào query '{query}': {e}")
            return []

    def poll_live_apify(
        self,
        search_queries: Optional[List[str]] = None,
        max_posts: int = 40,
        window_minutes: int = DEFAULT_WINDOW_MINUTES
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Cào Facebook thời gian thực chuẩn LIVE MODE:
        - Sử dụng duy nhất 1 lần cào hợp nhất (Single Consolidated Search) cho 'mưa ngập Sài Gòn'.
        - Không chia nhỏ 2 lần quét gây phân mảnh.
        - Tự động bao quát đợt ngập gần nhất (trong vòng 72h-96h).
        - Tuyệt đối KHÔNG fallback sang kho dataset cũ trong LIVE MODE.
        """
        print(f"\n[Facebook Live] Bắt đầu cào bài đăng người dùng Facebook thời gian thực qua Search Actor...")
        raw_items = []
        queries = search_queries or FB_SEARCH_QUERIES

        # Chạy cào tập trung DUY NHẤT 1 lần cho truy vấn hợp nhất hàng đầu
        primary_query = queries[0] if queries else "mưa ngập Sài Gòn"
        print(f"[Facebook Live] Thực thi 1 truy vấn hợp nhất duy nhất: '{primary_query}' (Dung lượng: {max_posts} bài)...")
        try:
            items = self.poll_search_posts_ppr(query=primary_query, max_posts=max_posts)
            raw_items.extend(items)
        except Exception as eq:
            print(f"[Facebook Live] Lỗi query '{primary_query}': {eq}")

        now = int(time.time())
        # Cửa sổ thời gian thích ứng: ít nhất 72h (3 ngày) để đảm bảo không bỏ sót đợt ngập vừa qua
        max_age_sec = max(259200, window_minutes * 60)
        events = []
        seen = set()

        for it in raw_items:
            ev = process_facebook_item(it, reference_time=now)
            if not ev:
                continue
            if (now - ev["create_time"]) > max_age_sec:
                continue
            k = (ev["location"]["street"], ev["opinion"], ev["text"][:30].lower())
            if k in seen:
                continue
            seen.add(k)
            events.append(ev)

        # Lưu lại bản thô vừa cào để audit
        if raw_items:
            try:
                with open(LAST_CRAWL_FB_FILE, "w", encoding="utf-8") as f:
                    json.dump(raw_items, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

        stats = {
            "platform": "facebook",
            "mode": "live",
            "raw_count": len(raw_items),
            "events_matched": len(events),
            "active_window": f"{window_minutes // 60} giờ qua" if window_minutes >= 60 else f"{window_minutes} phút qua"
        }
        print(f"[Facebook Live] Hoàn tất cào Live: {len(raw_items)} bài thô, {len(events)} sự kiện khớp điểm ngập.")
        return events, stats

    def poll_simulation(
        self,
        file_path: Optional[str] = None,
        window_minutes: int = DEFAULT_WINDOW_MINUTES,
        batch_size: int = 10
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Mô phỏng bài viết ngập lụt cho SIMULATION MODE:
        Sử dụng kho dữ liệu bài đăng ngập lụt thực tế đã được kiểm chứng.
        """
        real_pool = load_real_facebook_flood_pool()
        events = real_pool[:batch_size] if real_pool else []
        stats = {
            "platform": "facebook",
            "mode": "simulation",
            "events_matched": len(events),
            "active_window": f"{window_minutes // 60} giờ qua (Mô phỏng thực tế)"
        }
        return events, stats
