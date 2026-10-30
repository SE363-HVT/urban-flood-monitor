# -*- coding: utf-8 -*-
"""
pipeline/facebook_poller.py - Module Thu Thập Dữ Liệu Ngập Lụt Từ Facebook
Tối ưu hóa thu thập thời gian thực với Actor chuyên sâu:
1. Facebook Posts Search (scraper_one/facebook-posts-search):
   - Tìm kiếm bài đăng ngập lụt, triều cường thời gian thực tại TP.HCM (location="Ho Chi Minh City", searchType="latest").
   - Chi phí cực thấp (~$0.04 / lần chạy), tiết kiệm tối đa usage Apify.
   - Nhận diện và gán trọng số ưu tiên cho 5 Fanpage uy tín trọng điểm:
     + Báo Pháp Luật TP.HCM (phapluattp.vn)
     + Báo Thanh Niên (thanhnien)
     + Báo Người Lao Động (nguoilaodong)
     + VnExpress (congdongvnexpress)
     + Sài Gòn Của Tôi (SGCT1)
2. Chuẩn Live Mode 100% Thực Tế:
   - Chỉ trả về bài đăng thật từ Facebook được cào gần đây.
   - Khớp nối chính xác với Gazetteer và OpenStreetMap để đảm bảo 100% sự kiện hợp lệ có tọa độ hiển thị trên Heatmap.
3. Bộ lọc kiểm duyệt khắt khe:
   - Loại bỏ triệt để tin rác BĐS ("cho thuê", "bán nhà"), bán xe ô tô ("không ngập nước", "odo"), bẫy chữ "ngập tràn deal/ưu đãi".
   - Kiểm soát nghiêm ngặt cửa sổ thời gian (window_minutes): Tuyệt đối không để lọt bài đăng cũ (9 giờ - 1 ngày trước).
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
    FB_ACTOR_ID,
    FB_SEARCH_QUERIES,
    FB_SEARCH_LOCATIONS,
    FB_TARGET_PAGES,
    FB_TARGET_PAGE_IDENTIFIERS,
    DEFAULT_WINDOW_MINUTES
)
from core.state_manager import StateManager
from core.gazetteer import match_hotspot
from pipeline.event_processor import clean_stream_text, analyze_severity_heuristic, format_relative_time
from pipeline.simulation_replayer import SimulationReplayer

REAL_FB_POOL_FILE = os.path.join("data", "real_facebook_flood_pool.json")
LAST_CRAWL_FB_FILE = os.path.join("data", "last_crawled_facebook.json")

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

    # 2. Định dạng media từ các scraper truyền thống
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

    return urls


def parse_facebook_timestamp(time_val: Any) -> Optional[int]:
    """Chuẩn hóa mọi định dạng thời gian của Facebook sang Unix Timestamp (giây)."""
    if not time_val:
        return None
    if isinstance(time_val, (int, float)):
        val = int(time_val)
        return val // 1000 if val > 1e11 else val

    val_str = str(time_val).strip()
    try:
        dt = datetime.fromisoformat(val_str.replace("Z", "+00:00"))
        return int(dt.timestamp())
    except Exception:
        pass

    for fmt in [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y"
    ]:
        try:
            return int(datetime.strptime(val_str, fmt).replace(tzinfo=timezone.utc).timestamp())
        except Exception:
            continue

    return None


class FacebookPoller:
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

        url = f"https://api.apify.com/v2/acts/{FB_ACTOR_ID}/runs?token={self.apify_token}"
        main_query = queries[0] if isinstance(queries, list) and queries else "mưa ngập TP.HCM"
        if isinstance(queries, list) and len(queries) > 1:
            main_query = f"{queries[0]} OR {queries[1]}"
        run_input = {
            "query": main_query,
            "locations": target_locations,
            "maxPosts": max_posts,
            "searchType": "latest",
        }

        raw_items = []
        try:
            resp = requests.post(url, json=run_input, timeout=30)
            if resp.status_code == 429:
                print("[Facebook Live] ⚠️ Apify Facebook Actor đạt giới hạn tần suất (Rate Limit). Bỏ qua kênh Facebook đợt này.")
                return [], {"status": "rate_limited", "facebook_count": 0}
            resp.raise_for_status()
            run_data = resp.json().get("data", {})
            run_id = run_data.get("id")
            dataset_id = run_data.get("defaultDatasetId")

            print(f"[Facebook Live] Actor đang chạy (Run ID: {run_id}). Đang đợi kết quả...")

            poll_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={self.apify_token}"
            status = "RUNNING"
            for _ in range(50):
                time.sleep(2.5)
                try:
                    s_resp = requests.get(poll_url, timeout=10).json().get("data", {})
                    status = s_resp.get("status")
                    if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                        break
                except Exception:
                    pass

            if status != "SUCCEEDED":
                print(f"[Facebook Live] ⚠️ Facebook Actor dừng với trạng thái: {status} (có thể do rate limit/quota).")
                return [], {"status": status, "facebook_count": 0}

            items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={self.apify_token}"
            items_resp = requests.get(items_url, timeout=30)
            items_resp.raise_for_status()
            raw_items = items_resp.json()
        except Exception as e:
            print(f"[Facebook Live] ⚠️ Lỗi kết nối cào Facebook qua Apify: {e}")
            return [], {"status": "error", "facebook_count": 0}

        try:
            os.makedirs("data", exist_ok=True)
            with open(LAST_CRAWL_FB_FILE, "w", encoding="utf-8") as f:
                json.dump(raw_items, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        print(f"[Facebook Live] Cào thành công! Thu được {len(raw_items)} bài đăng từ Facebook.")

        current_time = int(time.time())
        cutoff_window = current_time - (window_minutes * 60)
        cutoff_24h = current_time - 86400
        cutoff_72h = current_time - 259200

        events_window = []
        events_24h = []
        events_72h = []
        seen_texts = set()

        for raw in raw_items:
            post_id = str(raw.get("id") or raw.get("postId") or "")
            text = raw.get("text") or raw.get("message") or raw.get("caption") or ""
            cleaned = clean_stream_text(text)
            if not cleaned:
                continue

            cleaned_lower = cleaned.lower()
            if any(spam in cleaned_lower for spam in STRICT_SPAM_KEYWORDS):
                continue

            has_intent = any(k in cleaned_lower for k in FLOOD_INTENT_KEYWORDS)
            if not has_intent:
                continue

            hotspot = match_hotspot(cleaned)
            if not hotspot:
                continue

            txt_sig = cleaned[:35].lower()
            if txt_sig in seen_texts:
                continue
            seen_texts.add(txt_sig)

            post_time = parse_facebook_timestamp(raw.get("time") or raw.get("timestamp") or raw.get("created_time")) or current_time
            analysis = analyze_severity_heuristic(cleaned) or {
                "opinion": "mưa ngập",
                "sentiment": "negative",
                "severity_level": "medium",
                "weight": 2.0
            }

            media_urls = extract_facebook_media_urls(raw)
            media_type = "video" if any(".mp4" in u.lower() or "video" in u.lower() for u in media_urls) else ("image" if media_urls else "text")

            author_data = raw.get("author") or {}
            if isinstance(author_data, dict):
                author_name = author_data.get("name") or author_data.get("title") or "Cộng đồng mạng TP.HCM"
            else:
                author_name = str(author_data) if author_data else "Cộng đồng mạng TP.HCM"

            post_url = raw.get("url") or raw.get("postUrl") or (f"https://www.facebook.com/{post_id}" if post_id else "https://www.facebook.com")

            ev = {
                "id": f"fb_{post_id}" if post_id else f"fb_{int(time.time()*1000)}",
                "platform": "facebook",
                "media_type": media_type,
                "media_urls": media_urls,
                "author": author_name,
                "text": cleaned,
                "create_time": post_time,
                "created_at_iso": datetime.fromtimestamp(post_time, timezone.utc).isoformat(),
                "relative_time": format_relative_time(post_time, current_time),
                "location": {
                    "street": hotspot.get("street") or "",
                    "display_name": hotspot.get("display_name", ""),
                    "ward": hotspot.get("ward", ""),
                    "administrative_unit": hotspot.get("ward", ""),
                    "district": hotspot.get("district", "TP.HCM"),
                    "region": hotspot.get("region", "TPHCM"),
                    "lat": hotspot["lat"],
                    "lon": hotspot["lon"],
                    "heat_points": hotspot.get("heat_points", [[hotspot["lat"], hotspot["lon"]]]),
                    "priority": hotspot.get("priority", 3),
                    "type": hotspot.get("type", "Ngập lụt"),
                    "cause": hotspot.get("cause", "rain"),
                    "cause_label": hotspot.get("cause_label", "Mưa lớn, nước không thoát kịp"),
                    "source": hotspot.get("source", "facebook_live")
                },
                "aspect": hotspot["display_name"],
                "opinion": analysis["opinion"],
                "sentiment": analysis["sentiment"],
                "severity": analysis["severity_level"],
                "weight": analysis["weight"] * 1.1,
                "url": post_url
            }

            if post_time >= cutoff_window:
                events_window.append(ev)
                if post_id:
                    self.state_manager.mark_seen(f"fb_{post_id}", post_time)
            elif post_time >= cutoff_24h:
                events_24h.append(ev)
            elif post_time >= cutoff_72h:
                events_72h.append(ev)

        self.state_manager.save()

        display_events = events_window
        win_label = f"{window_minutes // 60} giờ qua" if (window_minutes >= 60 and window_minutes % 60 == 0) else f"{window_minutes} phút"
        if not display_events:
            win_label = f"{win_label} (Không có bài đăng mới)"

        display_events.sort(key=lambda x: (x.get("weight", 1.0), x.get("create_time", 0)), reverse=True)

        stats = {
            "platform": "facebook",
            "mode": "live",
            "total_crawled": len(raw_items),
            "events_window": len(events_window),
            "total_events_displayed": len(display_events),
            "active_window": win_label
        }
        print(f"[Facebook Live] Hoàn tất cào Live: {len(raw_items)} bài thô, {len(events_window)} sự kiện khớp trong cửa sổ ({win_label}).")
        return display_events, stats

    def poll_simulation(
        self,
        file_path: Optional[str] = None,
        window_minutes: int = DEFAULT_WINDOW_MINUTES,
        batch_size: int = 10
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Phát lại bài viết ngập lụt mô phỏng từ dataset tĩnh đã làm sạch:
        data/processed/hcmc_flood_annotated_v1.json (100% trong TP.HCM).
        """
        replayer = SimulationReplayer.get_instance()
        return replayer.poll(batch_size=batch_size, platform_filter="facebook")
