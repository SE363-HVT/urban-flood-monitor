# -*- coding: utf-8 -*-
"""
pipeline/facebook_poller.py
Thu thập và xử lý bài đăng ngập lụt từ Facebook thông qua Apify REST API
sử dụng Actor scraper_one~facebook-posts-search (hoặc simulation dataset tĩnh).
Tối ưu hóa:
- Lọc rác quảng cáo, bất động sản, xe cộ, từ ngữ ẩn dụ ("ngập tràn", "tràn ngập").
- Lọc bài đăng chỉ giữ lại bài có thời gian thực tế <= 24 giờ (loại bỏ fallback gán thời gian hiện tại).
- Phân loại độ tươi 3 tầng: < 2h, 2-4h, 4-24h.
"""

import os
import json
import time
import requests
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from core.config import (
    APIFY_TOKEN,
    FB_ACTOR_ID,
    FB_SEARCH_QUERIES,
    FB_SEARCH_LOCATIONS,
    DEFAULT_WINDOW_MINUTES
)
from core.state_manager import StateManager
from core.gazetteer import match_hotspot
from pipeline.event_processor import clean_stream_text, analyze_severity_heuristic, format_relative_time
from pipeline.simulation_replayer import SimulationReplayer

REAL_FB_POOL_FILE = os.path.join("data", "real_facebook_flood_pool.json")
LAST_CRAWL_FB_FILE = os.path.join("data", "last_crawled_facebook.json")

DIRECT_FLOOD_TERMS = [
    "nước ngập", "ngập nước", "ngập lụt", "ngập úng", "ngập sâu", "ngập đường", "đường ngập",
    "triều cường", "nước dâng", "nước tràn", "lút bánh", "bì bõm", "lội nước", "đường thành sông",
    "chìm trong biển nước", "ngập lênh láng", "ngập nặng", "ngập nửa mét", "ngập nửa bánh",
    "ngập tới đầu gối", "mưa ngập", "ngập xe"
]

FLOOD_INTENT_KEYWORDS = [
    "ngập", "triều cường", "chết máy", "bì bõm", "lút bánh",
    "dắt bộ", "biến thành sông", "nước dâng", "mưa ngập", "thất thủ", "ngập úng", "lênh láng"
]

STRICT_SPAM_KEYWORDS = [
    "cho thuê", "phòng trọ", "mặt tiền", "diện tích", "sổ hồng", "sổ đỏ",
    "căn hộ", "vinhomes", "chuyển nhượng", "pass phòng", "bán nhà", "giá chỉ",
    "đáp án triết", "k52", "k51", "thi hộ", "học hộ", "duplex", "full nội thất",
    "chuyên cho thuê", "for rent", "bán gấp", "cắt lỗ", "ngộp", "hẻm xe hơi",
    "shophouse", "biệt thự", "đất nền", "thổ cư", "deal ngập tràn", "ưu đãi ngập tràn",
    "khuyến mãi ngập tràn", "ngập tràn ưu đãi", "ngập tràn niềm vui", "ngập tràn hạnh phúc",
    "ngập tràn bất ngờ", "ngập tràn quà", "ngập tràn quà tặng", "ngập tràn tiếng cười",
    "ngập tràn đồ ăn", "ngập tràn món ngon", "foodtour", "food tour", "ẩm thực", "ăn vặt",
    "halloween", "spooktacular", "hotel", "khách sạn", "resort", "homestay", "đặt phòng",
    "inbox ngay để", "vé máy bay", "transit tour", "quá cảnh", "visa", "đặt vé",
    "buffet", "cocktail", "quán bar", "pub", "lounge", "spa", "massage", "nối mi", "nail",
    "không ngập nước", "không đâm đụng", "odo", "xe lướt", "số tự động", "bán xe",
    "vios", "accent", "trả góp", "chính chủ bán", "ford everest", "titanium", "đổi xe",
    "hội chợ", "liveshow", "concert", "minigame", "giveaway"
]


def load_real_facebook_flood_pool() -> List[Dict[str, Any]]:
    """Tải 100% bài đăng ngập lụt thực tế cho SIMULATION MODE."""
    if os.path.exists(REAL_FB_POOL_FILE):
        try:
            with open(REAL_FB_POOL_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [it for it in data if it.get("url") and "_curated" not in it.get("url", "")]
        except Exception:
            return []
    return []


def extract_facebook_media_urls(item: Dict[str, Any]) -> List[str]:
    """Trích xuất liên kết hình ảnh hoặc video từ bài viết Facebook."""
    urls = []

    # 1. Định dạng attachments từ scraper_one
    attachments = item.get("attachments", [])
    if isinstance(attachments, list):
        for att in attachments:
            if isinstance(att, dict) and att.get("url"):
                u = att["url"]
                if u not in urls:
                    urls.append(u)

    # 2. Định dạng media list / photos
    media = item.get("media", [])
    if isinstance(media, list):
        for m in media:
            if isinstance(m, dict) and m.get("url"):
                u = m["url"]
                if u not in urls:
                    urls.append(u)
            elif isinstance(m, str) and m.startswith("http"):
                if m not in urls:
                    urls.append(m)

    # 3. Định dạng image/video trực tiếp
    for k in ["image", "imageUrl", "thumbnail", "videoUrl"]:
        val = item.get(k)
        if isinstance(val, str) and val.startswith("http") and val not in urls:
            urls.append(val)

    return urls


def parse_facebook_timestamp(raw_time: Any) -> Optional[int]:
    """
    Chuẩn hóa thời gian bài viết Facebook về Unix Timestamp (giây).
    Hỗ trợ ISO-8601, timestamp giây, millisecond.
    Tuyệt đối không fallback về thời gian hiện tại nếu bài viết không có ngày giờ rõ ràng.
    """
    if not raw_time:
        return None

    if isinstance(raw_time, (int, float)):
        ts = int(raw_time)
        if ts > 1e11:  # Milliseconds
            ts = int(ts / 1000)
        return ts

    if isinstance(raw_time, str):
        raw_str = raw_time.strip()
        if raw_str.isdigit():
            ts = int(raw_str)
            if ts > 1e11:
                ts = int(ts / 1000)
            return ts

        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d"
        ):
            try:
                dt = datetime.strptime(raw_str, fmt)
                if dt.tzinfo is None:
                    return int(dt.replace(tzinfo=timezone.utc).timestamp())
                return int(dt.timestamp())
            except Exception:
                continue

    return None


class FacebookPoller:
    """Poller thu thập bài đăng Facebook thời gian thực hoặc mô phỏng."""

    def __init__(self, apify_token: Optional[str] = None, state_manager: Optional[StateManager] = None):
        self.apify_token = apify_token or APIFY_TOKEN
        self.state_manager = state_manager or StateManager()

    def poll_live_apify(
        self,
        search_queries: Optional[List[str]] = None,
        max_posts: int = 40,
        window_minutes: int = DEFAULT_WINDOW_MINUTES
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Cào trực tiếp các bài đăng ngập lụt từ Facebook thông qua Apify REST API.
        """
        if not self.apify_token:
            raise ValueError("Chưa cấu hình APIFY_TOKEN trong core/config.py.")

        queries = search_queries or FB_SEARCH_QUERIES
        target_locations = FB_SEARCH_LOCATIONS
        print(f"\n[Facebook Live] Bắt đầu cào thời gian thực từ Facebook...")
        print(f"[Facebook Live] Truy vấn tìm kiếm ({len(queries)}): {queries[:3]}...")

        # Hỗ trợ Actor danek~facebook-search-ppr (ổn định, có recent_posts) và fallback
        query_str = " OR ".join(queries[:3]) if isinstance(queries, list) else str(queries)

        url = f"https://api.apify.com/v2/acts/{FB_ACTOR_ID}/runs?token={self.apify_token}"
        if "danek" in str(FB_ACTOR_ID):
            run_input = {
                "query": query_str,
                "search_type": "posts",
                "recent_posts": True,
                "max_posts": max_posts
            }
        else:
            run_input = {
                "query": query_str,
                "locations": target_locations,
                "maxPosts": max_posts,
                "searchType": "latest"
            }

        raw_items = []
        try:
            resp = requests.post(url, json=run_input, timeout=30)
            if resp.status_code == 429:
                print("[Facebook Live] ⚠️ Apify Facebook Actor đạt giới hạn tần suất (Rate Limit). Bỏ qua Facebook đợt này.")
                return [], {"status": "rate_limited", "facebook_count": 0}
            resp.raise_for_status()
            run_data = resp.json().get("data", {})
            run_id = run_data.get("id")
            dataset_id = run_data.get("defaultDatasetId")

            print(f"[Facebook Live] Actor đang chạy (Run ID: {run_id}). Đang chờ kết quả...")

            poll_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={self.apify_token}"
            status = "RUNNING"
            for _ in range(90):
                time.sleep(2.0)
                try:
                    status_resp = requests.get(poll_url, timeout=10).json().get("data", {})
                    status = status_resp.get("status")
                    if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                        break
                except Exception:
                    pass

            if status != "SUCCEEDED":
                print(f"[Facebook Live] ⚠️ Facebook Actor dừng với trạng thái: {status}.")
                return [], {"status": status, "facebook_count": 0}

            items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={self.apify_token}"
            items_resp = requests.get(items_url, timeout=30)
            items_resp.raise_for_status()
            raw_items = items_resp.json()
        except Exception as e:
            print(f"[Facebook Live] ⚠️ Lỗi kết nối cào Facebook qua Apify: {e}")
            return [], {"status": "error", "facebook_count": 0}

        os.makedirs("data", exist_ok=True)
        try:
            with open(LAST_CRAWL_FB_FILE, "w", encoding="utf-8") as f:
                json.dump(raw_items, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        print(f"[Facebook Live] Cào thành công! Thu được {len(raw_items)} bài đăng từ Facebook.")

        current_time = int(time.time())
        cutoff_24h = current_time - 86400

        events_window = []
        events_24h = []
        events_72h = []
        seen_texts = set()

        for raw in raw_items:
            post_id = str(raw.get("post_id") or raw.get("id") or raw.get("postId") or "")
            text = raw.get("message") or raw.get("message_rich") or raw.get("postText") or raw.get("text") or raw.get("caption") or raw.get("content") or ""
            if not text and raw.get("album_preview"):
                for alb in raw.get("album_preview", []):
                    if alb.get("caption"):
                        text += " " + alb["caption"]
            cleaned = clean_stream_text(text)
            if not cleaned or len(cleaned) < 15:
                continue

            low_text = cleaned.lower()

            # 1. Lọc tuyệt đối quảng cáo, bất động sản, vé máy bay, buffet, hotel
            if any(spam in low_text for spam in STRICT_SPAM_KEYWORDS):
                continue

            # 2. Xử lý từ ẩn dụ "ngập tràn", "tràn ngập": Chỉ hợp lệ nếu có ngữ cảnh ngập nước/mưa lụt thật
            if "ngập tràn" in low_text or "tràn ngập" in low_text:
                if not any(term in low_text for term in DIRECT_FLOOD_TERMS):
                    continue

            # 3. Phải chứa ít nhất 1 từ khóa ngập lụt
            if not any(k in low_text for k in FLOOD_INTENT_KEYWORDS):
                continue

            # 4. Trích xuất thời gian thực tế - Bắt buộc phải có ngày giờ và <= 24 giờ
            raw_time = raw.get("time") or raw.get("date") or raw.get("timestamp") or raw.get("created_time")
            created_time = parse_facebook_timestamp(raw_time)
            if not created_time:
                # Loại bỏ bài không có timestamp thực tế
                continue

            age_seconds = max(0, current_time - created_time)
            if age_seconds > 259200:
                # Loại bỏ bài cũ quá 72 giờ (3 ngày)
                continue

            # Chống trùng lặp nội dung
            text_key = cleaned[:40].strip()
            if text_key in seen_texts:
                continue
            seen_texts.add(text_key)

            # Khớp địa danh TP.HCM qua Gazetteer
            location_info = match_hotspot(cleaned)
            if not location_info:
                continue

            raw_street = location_info.get("street") or ""
            ward = location_info.get("ward") or "TP.HCM"
            district = location_info.get("district") or "TP.HCM"

            media_urls = extract_facebook_media_urls(raw)
            media_type = "video" if raw.get("videoUrl") or raw.get("isVideo") else ("image" if media_urls else "none")

            author_data = raw.get("author")
            author_name = (
                author_data.get("name") if isinstance(author_data, dict)
                else (raw.get("author_title") or raw.get("authorName") or raw.get("pageName") or "Người dân TP.HCM")
            )
            source_page = raw.get("pageName") or "Facebook Post"

            canonical_id = f"fb_{post_id}" if post_id else f"fb_{hash(cleaned)}"

            event = {
                "id": canonical_id,
                "canonical_id": canonical_id,
                "platform": "facebook",
                "create_time": created_time,
                "historical_timestamp": created_time,
                "text": cleaned,
                "clean_text": cleaned,
                "aspect": raw_street or ward,
                "opinion": "ngập nước",
                "polarity": "negative",
                "confidence": 0.88,
                "severity": analyze_severity_heuristic(cleaned),
                "location": {
                    "street": raw_street,
                    "ward": ward,
                    "district": district,
                    "lat": location_info["lat"],
                    "lon": location_info["lon"],
                    "display_name": location_info.get("display_name", f"{raw_street}, {ward}")
                },
                "media_type": media_type,
                "media_urls": media_urls,
                "author": author_name,
                "source_page": source_page,
                "likes": int(raw.get("likesCount") or raw.get("reactionsCount") or 0),
                "comments": int(raw.get("commentsCount") or 0),
                "shares": int(raw.get("sharesCount") or 0),
                "url": raw.get("url") or raw.get("postUrl") or "https://www.facebook.com",
                "weight": 2.2
            }

            # Phân tầng mức độ tươi (thêm tầng 24-72h cho đợt triều cường gần nhất)
            if age_seconds <= 7200:
                event["freshness"] = "strict_2h"
                event["status_tag"] = "🔴 ĐANG DIỄN RA (< 2 GIỜ)"
                event["weight"] *= 1.3
                events_window.append(event)
            elif age_seconds <= 14400:
                event["freshness"] = "recent_4h"
                event["status_tag"] = "🟠 ĐỢT MƯA VỪA DỨT (2-4 GIỜ)"
                event["weight"] *= 1.1
                events_24h.append(event)
            elif age_seconds <= 86400:
                event["freshness"] = "within_24h"
                event["status_tag"] = "🟡 CẢNH BÁO TRONG NGÀY (4-24 GIỜ)"
                event["weight"] *= 1.0
                events_24h.append(event)
            else:
                event["freshness"] = "recent_72h"
                event["status_tag"] = "🟣 ĐỢT TRIỀU CƯỜNG / MƯA GẦN ĐÂY (24-72 GIỜ)"
                event["weight"] *= 0.8
                events_72h.append(event)

            if post_id:
                self.state_manager.mark_seen(f"fb_{post_id}", created_time)

        self.state_manager.save()

        # Hiển thị thông minh: Ưu tiên 24h, tự động bổ sung đợt triều cường gần nhất (72h) nếu 24h qua khô ráo
        all_24h_events = events_window + events_24h
        if len(all_24h_events) < 5 and events_72h:
            display_events = all_24h_events + events_72h[:(10 - len(all_24h_events))]
            win_label = "72 giờ qua (Bao gồm đợt triều cường gần nhất)"
        else:
            display_events = all_24h_events
            win_label = "24 giờ qua (3 tầng cảnh báo: <2h, 2-4h, 4-24h)"
        if not display_events:
            win_label = f"{win_label} (Không có ngập mới)"

        display_events.sort(key=lambda x: (
            4 if x.get("freshness") == "strict_2h" else (
                3 if x.get("freshness") == "recent_4h" else (
                    2 if x.get("freshness") == "within_24h" else 1
                )
            ),
            x.get("weight", 1.0),
            x.get("create_time", 0)
        ), reverse=True)

        stats = {
            "mode": "live",
            "current_time": current_time,
            "total_crawled": len(raw_items),
            "events_window": len(events_window),
            "total_events_displayed": len(display_events),
            "active_window": win_label
        }
        return display_events, stats

    def poll_simulation(
        self,
        window_minutes: int = DEFAULT_WINDOW_MINUTES,
        batch_size: int = 15
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Phát lại dữ liệu mô phỏng bài đăng Facebook từ kho dữ liệu sạch."""
        replayer = SimulationReplayer.get_instance()
        return replayer.poll(batch_size=batch_size, platform_filter="facebook")
