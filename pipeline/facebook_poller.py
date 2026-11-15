# -*- coding: utf-8 -*-
"""
pipeline/facebook_poller.py
Thu thập và xử lý bài đăng ngập lụt từ Facebook thông qua Apify REST API
sử dụng Actor danek~facebook-search-ppr (hoặc simulation dataset tĩnh).
Tích hợp Smart Key Rotation qua ApifyPoolManager.
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
        - Tự động lấy active token từ ApifyPoolManager (với cơ chế Failover khi hết hạn mức).
        """
        pool_mgr = None
        active_token = self.apify_token
        try:
            from core.apify_pool import ApifyPoolManager, mask_token
            pool_mgr = ApifyPoolManager.get_instance()
            if not active_token or active_token == APIFY_TOKEN:
                active_token = pool_mgr.get_active_token()
        except Exception:
            pool_mgr = None

        if not active_token:
            raise ValueError("Chưa cấu hình APIFY_TOKEN trong core/config.py hoặc Apify Pool.")

        queries = search_queries or FB_SEARCH_QUERIES
        target_locations = FB_SEARCH_LOCATIONS

        masked_disp = active_token[:12] + "..." + active_token[-4:] if len(active_token) >= 16 else active_token
        print(f"\n[Facebook Live] Bắt đầu cào thời gian thực từ Facebook qua Apify Key ({masked_disp})...")
        print(f"[Facebook Live] Truy vấn tìm kiếm ({len(queries)}): {queries[:3]}...")

        # Hỗ trợ Actor danek~facebook-search-ppr (ổn định, có recent_posts) và fallback
        query_str = " OR ".join(queries[:3]) if isinstance(queries, list) else str(queries)

        url = f"https://api.apify.com/v2/acts/{FB_ACTOR_ID}/runs?token={active_token}"
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
            if resp.status_code in [401, 402]:
                err_label = "Hết hạn mức $5 (HTTP 402 Quota Exceeded)" if resp.status_code == 402 else "Token không hợp lệ (HTTP 401)"
                print(f"[Facebook Live] ⚠️ Apify Facebook gặp lỗi: {err_label} đối với key {masked_disp}!")
                if pool_mgr:
                    pool_mgr.mark_exhausted(active_token, reason=err_label)
                return [], {"status": "exhausted", "error": err_label, "facebook_count": 0}

            resp.raise_for_status()
            run_data = resp.json().get("data", {})
            run_id = run_data.get("id")
            dataset_id = run_data.get("defaultDatasetId")

            print(f"[Facebook Live] Actor đang chạy (Run ID: {run_id}). Đang chờ kết quả...")

            poll_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={active_token}"
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

            items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={active_token}"
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
            text = clean_stream_text(text)

            if not text or len(text) < 15:
                continue

            # Kiểm tra từ khóa rác & spam quảng cáo
            text_lower = text.lower()
            if any(spam_word in text_lower for spam_word in STRICT_SPAM_KEYWORDS):
                continue

            # Kiểm tra ý định ngập lụt
            has_direct_flood = any(term in text_lower for term in DIRECT_FLOOD_TERMS)
            has_intent_flood = any(term in text_lower for term in FLOOD_INTENT_KEYWORDS)
            if not has_direct_flood and not has_intent_flood:
                continue

            # Khử trùng lặp nội dung
            text_sig = text[:40].strip().lower()
            if text_sig in seen_texts:
                continue
            seen_texts.add(text_sig)

            # Chuẩn hóa thời gian thực tế của bài viết
            raw_time_field = raw.get("time") or raw.get("created_time") or raw.get("timestamp") or raw.get("date")
            post_timestamp = parse_facebook_timestamp(raw_time_field)
            if not post_timestamp:
                continue

            # Lọc nghiêm ngặt: Chỉ nhận bài đăng trong vòng 24 giờ qua
            if post_timestamp < cutoff_24h:
                continue

            # Định vị địa lý
            location = match_hotspot(text)
            if not location or not location.get("street"):
                continue

            # Phân tích mức độ nghiêm trọng
            severity, triplets = analyze_severity_heuristic(text)

            # Trích xuất hình ảnh / video
            media_urls = extract_facebook_media_urls(raw)

            author = raw.get("author") or raw.get("user") or {}
            author_name = author.get("name") if isinstance(author, dict) else str(author)
            post_url = raw.get("url") or raw.get("post_url") or f"https://www.facebook.com/{post_id}"

            event = {
                "id": f"fb_{post_id}" if post_id else f"fb_{int(post_timestamp)}",
                "platform": "facebook",
                "author": author_name or "Cộng đồng Facebook",
                "text": text,
                "create_time": post_timestamp,
                "timestamp": post_timestamp,
                "relative_time": format_relative_time(post_timestamp, current_time),
                "location": location,
                "lat": location.get("lat"),
                "lon": location.get("lon"),
                "severity": severity,
                "triplets": triplets,
                "media_urls": media_urls,
                "url": post_url,
                "crawler_source": "apify_facebook"
            }

            age_seconds = max(0, current_time - post_timestamp)
            if age_seconds <= 7200:
                event["freshness"] = "strict_2h"
                event["status_tag"] = "🔴 ĐANG DIỄN RA (< 2 GIỜ)"
                event["weight"] = 2.6
                events_window.append(event)
            elif age_seconds <= 14400:
                event["freshness"] = "recent_4h"
                event["status_tag"] = "🟠 ĐỢT MƯA VỪA DỨT (2-4 GIỜ)"
                event["weight"] = 2.2
                events_24h.append(event)
            else:
                event["freshness"] = "within_24h"
                event["status_tag"] = "🟡 CẢNH BÁO TRONG NGÀY (4-24 GIỜ)"
                event["weight"] = 2.0
                events_24h.append(event)

            if post_id:
                self.state_manager.mark_seen(f"fb_{post_id}", post_timestamp)

        self.state_manager.save()

        display_events = events_window + events_24h
        win_label = "24 giờ qua (Facebook Live Stream)"
        if not display_events:
            win_label = f"{win_label} (Không có ngập mới)"

        display_events.sort(key=lambda x: (
            3 if x.get("freshness") == "strict_2h" else (2 if x.get("freshness") == "recent_4h" else 1),
            x.get("weight", 1.0),
            x.get("create_time", 0)
        ), reverse=True)

        stats = {
            "mode": "live",
            "current_time": current_time,
            "total_crawled": len(raw_items),
            "events_window": len(events_window),
            "total_events_displayed": len(display_events),
            "facebook_count": len(display_events),
            "active_window": win_label
        }
        return display_events, stats

    def poll_simulation(
        self,
        file_path: Optional[str] = None,
        window_minutes: int = DEFAULT_WINDOW_MINUTES,
        batch_size: int = 15
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Phát lại dòng bài đăng Facebook mô phỏng từ kho dữ liệu sạch:
        data/processed/hcmc_flood_annotated_v1.json (100% trong TP.HCM).
        """
        replayer = SimulationReplayer.get_instance()
        return replayer.poll(batch_size=batch_size, platform_filter="facebook")
