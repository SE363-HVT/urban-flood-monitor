"""
pipeline/threads_poller.py - Module Thu Thập Dữ Liệu Ngập Lụt Từ Nền Tảng Threads (Meta Threads)
Tối ưu hóa chi phí & hiệu suất tìm kiếm:
1. Chuyển đổi Actor sang futurizerush/meta-threads-scraper:
   - Chi phí siêu tiết kiệm: chỉ $0.0025/kết quả (rẻ hơn 8 lần so với $0.02 của actor cũ).
   - Hỗ trợ chế độ tìm kiếm đồng thời danh sách từ khóa & hashtag (#ngaplut, #muangap, #ngapsaigon).
   - Lọc theo 'recent' (bài đăng mới nhất), không yêu cầu thông tin đăng nhập.
2. Cam kết Chuẩn Live Mode 100% Thực Tế:
   - Trong chế độ LIVE, chỉ xử lý và trả về bài đăng thật từ người dùng Threads vừa cào được.
   - Tuyệt đối KHÔNG giả lập dữ liệu, không chèn bài cũ vào Live Mode.
   - Kho bài đăng lịch sử chỉ dùng cho chế độ SIMULATION MODE.
3. Chuẩn hóa sự kiện ngập lụt tiêu chuẩn (SE363 Flood Event) tích hợp tọa độ địa lý TP.HCM.
"""

import os
import glob
import json
import time
import requests
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from core.config import APIFY_TOKEN, THREADS_ACTOR_ID, THREADS_SEARCH_QUERIES, DEFAULT_WINDOW_MINUTES
from core.state_manager import StateManager
from core.gazetteer import match_hotspot
from pipeline.event_processor import clean_stream_text, analyze_severity_heuristic, format_relative_time

# Danh sách từ khóa ngập lụt bắt buộc trên Threads
THREADS_FLOOD_KEYWORDS = [
    "ngập", "triều cường", "chết máy", "bì bõm", "lút bánh",
    "dắt bộ", "biến thành sông", "nước dâng", "mưa to", "mưa ngập", "thất thủ", "ngập úng"
]

# Chặn tin rác, BĐS, bán hàng
THREADS_SPAM_KEYWORDS = [
    "cho thuê", "bán nhà", "phòng trọ", "mặt tiền", "diện tích", "sổ hồng",
    "sổ đỏ", "căn hộ", "vinhomes", "chuyển nhượng", "pass phòng", "giá chỉ",
    "đáp án triết", "học hộ", "thi hộ", "bánh mì", "đồ chua", "pa tê"
]


def process_threads_item(item: Dict[str, Any], reference_time: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Chuẩn hóa một bài đăng Threads sang sự kiện ngập lụt tiêu chuẩn.
    Bắt buộc phải có postUrl thật từ threads.net / threads.com.
    """
    raw_text = (
        item.get("text_content")
        or item.get("text")
        or item.get("captionText")
        or item.get("caption")
        or ""
    )

    # Bổ sung hashtag vào nội dung nếu có trường hashtags riêng
    hashtags = item.get("hashtags", [])
    if isinstance(hashtags, list) and hashtags:
        raw_text += " " + " ".join([f"#{h}" if not str(h).startswith("#") else str(h) for h in hashtags])

    if not raw_text or len(raw_text.strip()) < 10:
        return None

    raw_lower = raw_text.lower()

    # Chặn tin rác
    for spam_kw in THREADS_SPAM_KEYWORDS:
        if spam_kw in raw_lower:
            return None

    # Bắt buộc có biểu hiện ngập hoặc mưa to
    if not any(kw in raw_lower for kw in THREADS_FLOOD_KEYWORDS):
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

    # BẮT BUỘC CÓ URL THỰC TẾ
    post_url = item.get("post_url") or item.get("postUrl") or item.get("url")
    if not post_url or not (str(post_url).startswith("https://www.threads.") or str(post_url).startswith("https://threads.")):
        return None
    if "th_tanky" in str(post_url) or "_curated" in str(post_url):
        return None

    # Trích xuất thời gian
    create_time = item.get("timestamp") or item.get("takenAt")
    if not create_time:
        pub = item.get("created_at") or item.get("published_at") or item.get("takenAtISO")
        if pub:
            try:
                dt = datetime.fromisoformat(str(pub).replace("Z", "+00:00"))
                create_time = int(dt.timestamp())
            except Exception:
                create_time = None

    if reference_time is not None:
        if not create_time or (reference_time - create_time) > 432000:
            return None

    author_name = item.get("username") or item.get("display_name")
    if not author_name and str(post_url).startswith("https://www.threads."):
        # Trích xuất username từ URL: https://www.threads.com/@username/post/...
        parts = str(post_url).split("/")
        for p in parts:
            if p.startswith("@"):
                author_name = p
                break
    author_name = author_name or "Threads User"

    post_id = item.get("post_code") or item.get("postId") or item.get("postCode") or create_time or int(time.time())

    # Trích xuất media
    media_urls = []
    if item.get("media_urls") and isinstance(item.get("media_urls"), list):
        media_urls.extend(item.get("media_urls"))
    if item.get("imageUrl") and item["imageUrl"] not in media_urls:
        media_urls.append(item["imageUrl"])
    if item.get("videoUrl") and item["videoUrl"] not in media_urls:
        media_urls.append(item["videoUrl"])
    for m in item.get("allImages", []):
        if m and m not in media_urls:
            media_urls.append(m)

    likes = item.get("like_count") or item.get("likeCount", 0) or 0
    replies = item.get("reply_count") or item.get("directReplyCount", 0) or 0
    reposts = item.get("repost_count") or item.get("repostCount", 0) or 0

    weight = analysis["weight"]
    if media_urls:
        weight += 0.2
    if likes > 20:
        weight += 0.1

    event = {
        "id": f"th_{post_id}",
        "platform": "threads",
        "media_type": "post" if not media_urls else ("video" if any("mp4" in str(u) for u in media_urls) else "image_post"),
        "author": f"@{author_name}" if not str(author_name).startswith("@") else str(author_name),
        "text": cleaned_text,
        "create_time": create_time or int(time.time()),
        "created_at_iso": datetime.fromtimestamp(create_time, timezone.utc).isoformat() if create_time else "",
        "relative_time": format_relative_time(create_time, reference_time) if create_time else "Vừa xong",
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
            "comments": replies,
            "shares": reposts
        }
    }
    return event


class ThreadsPoller:
    """Bộ thu thập dữ liệu ngập lụt từ mạng xã hội Threads (Meta) qua Apify với chi phí tối ưu."""
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

    def poll_live_apify(
        self,
        search_queries: Optional[List[str]] = None,
        max_posts: int = 25,
        window_minutes: int = DEFAULT_WINDOW_MINUTES
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Cào Threads thời gian thực qua Apify:
        - Sử dụng futurizerush/meta-threads-scraper (rẻ gấp 8 lần, $0.0025/kết quả).
        - Hỗ trợ gửi danh sách từ khóa ngập lụt và hashtag cùng lúc.
        - Chế độ LIVE Mode chuẩn: Chỉ trả về bài đăng thật được cào, không chèn dataset giả lập.
        """
        if not self.apify_token:
            return [], {"platform": "threads", "mode": "live", "matched_count": 0}

        keywords = search_queries or THREADS_SEARCH_QUERIES[:6]
        print(f"\n[Threads Live] Bắt đầu cào bài đăng Threads thời gian thực qua '{THREADS_ACTOR_ID}'...")
        print(f"[Threads Live] Danh sách truy vấn & Hashtags: {keywords}")

        url = f"https://api.apify.com/v2/acts/{THREADS_ACTOR_ID}/runs?token={self.apify_token}"

        # Cấu hình linh hoạt theo loại Actor (futurizerush vs igview)
        if "futurizerush" in THREADS_ACTOR_ID:
            run_input = {
                "mode": "search",
                "keywords": keywords,
                "search_filter": "recent",
                "max_posts": max(20, max_posts)
            }
        else:
            run_input = {
                "searchQuery": keywords[0] if keywords else "ngập Sài Gòn",
                "sort": "recent",
                "maxPosts": max(20, max_posts)
            }

        try:
            resp = requests.post(url, json=run_input, timeout=30)
            resp.raise_for_status()
            run_data = resp.json().get("data", {})
            run_id = run_data.get("id")
            dataset_id = run_data.get("defaultDatasetId")
            print(f"[Threads Live] Actor đang chạy (Run ID: {run_id})...")

            status = self._wait_for_run(run_id, timeout_sec=90)
            if status != "SUCCEEDED":
                print(f"[Threads Live] Actor kết thúc với trạng thái: {status}.")
                return [], {"platform": "threads", "mode": "live", "matched_count": 0}

            items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={self.apify_token}"
            raw_items = requests.get(items_url, timeout=30).json()
            if not isinstance(raw_items, list):
                raw_items = []
            print(f"[Threads Live] Đã thu thập {len(raw_items)} bài viết thô từ Threads.")

            # Lưu lại dữ liệu thô gần nhất để kiểm tra
            try:
                os.makedirs("data/raw", exist_ok=True)
                with open("data/raw/dataset_threads_live.json", "w", encoding="utf-8") as f:
                    json.dump(raw_items, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

            now = int(time.time())
            max_age_sec = max(259200, window_minutes * 60)
            events = []
            seen = set()

            for it in raw_items:
                ev = process_threads_item(it, reference_time=now)
                if not ev:
                    continue
                if (now - ev["create_time"]) > max_age_sec:
                    continue
                k = (ev["location"]["street"], ev["opinion"], ev["text"][:30].lower())
                if k in seen:
                    continue
                seen.add(k)
                events.append(ev)

            stats = {
                "platform": "threads",
                "mode": "live",
                "raw_count": len(raw_items),
                "matched_count": len(events),
                "active_window": f"{window_minutes // 60} giờ qua" if window_minutes >= 60 else f"{window_minutes} phút qua"
            }
            print(f"[Threads Live] Hoàn tất cào Threads: {len(raw_items)} bài thô, {len(events)} sự kiện khớp ngập lụt.")
            return events, stats

        except Exception as e:
            print(f"[Threads Live] Lỗi: {e}")
            return [], {"platform": "threads", "mode": "live", "matched_count": 0}

    def poll_simulation(
        self,
        window_minutes: int = DEFAULT_WINDOW_MINUTES,
        batch_size: int = 8
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Mô phỏng bài viết ngập lụt cho SIMULATION MODE:
        Nạp các bài viết thực tế đã thu thập từ Threads có trong data/raw/*threads*.json.
        """
        raw_files = glob.glob("data/raw/*threads*.json")
        events = []
        seen = set()

        for rf in raw_files:
            try:
                with open(rf, "r", encoding="utf-8-sig") as fp:
                    data = json.load(fp)
                    if not isinstance(data, list):
                        continue
                    for it in data:
                        ev = process_threads_item(it)
                        if ev:
                            k = (ev["location"]["street"], ev["opinion"], ev["text"][:30].lower())
                            if k not in seen:
                                seen.add(k)
                                events.append(ev)
            except Exception:
                pass

        matched = events[:batch_size] if events else []
        stats = {
            "platform": "threads",
            "mode": "simulation",
            "raw_count": len(events),
            "matched_count": len(matched),
            "active_window": f"{window_minutes // 60} giờ qua (Mô phỏng)"
        }
        return matched, stats
