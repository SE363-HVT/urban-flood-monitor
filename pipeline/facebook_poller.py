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
    if item.get("video") and item["video"] not in urls:
        urls.append(item["video"])
    return urls


def process_facebook_item(
    item: Dict[str, Any],
    reference_time: Optional[int] = None,
    max_age_seconds: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Chuẩn hóa bài viết Facebook sang sự kiện ngập lụt tiêu chuẩn.
    Chỉ chấp nhận bài viết có URL thật từ Facebook, tuyệt đối không tạo URL ảo.
    Nhận diện Fanpage chính thống (Báo Thanh Niên, Báo Người Lao Động, Báo Pháp Luật TP.HCM, VnExpress, Sài Gòn Của Tôi).
    """
    raw_text = item.get("postText", "") or item.get("text", "") or item.get("message", "")
    if not raw_text and isinstance(item.get("sharedPost"), dict):
        raw_text = item["sharedPost"].get("postText", "") or item["sharedPost"].get("text", "")

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

    # Thời gian đăng bài (Epoch seconds)
    create_time = item.get("timestamp") or item.get("createTime")
    if create_time:
        try:
            val = int(create_time)
            # Nếu timestamp ở dạng milliseconds (13 chữ số)
            if val > 100000000000:
                val = int(val / 1000)
            create_time = val
        except Exception:
            create_time = None

    if not create_time and item.get("time"):
        try:
            time_str = str(item["time"]).replace("Z", "+00:00")
            dt = datetime.fromisoformat(time_str)
            create_time = int(dt.timestamp())
        except Exception:
            create_time = None

    # KIỂM SOÁT THỜI GIAN NGHIÊM NGẶT
    if reference_time is not None:
        cutoff = max_age_seconds if max_age_seconds is not None else 14400
        if not create_time or (reference_time - create_time) > cutoff:
            return None

    # Thông tin tác giả
    author_name = "Facebook Community"
    author_url = ""
    author_raw = item.get("author") or item.get("user") or item.get("pageName")
    if isinstance(author_raw, dict):
        author_name = author_raw.get("name") or author_raw.get("username") or "Facebook User"
        author_url = author_raw.get("profileUrl") or ""
    elif author_raw:
        author_name = str(author_raw)

    post_id = item.get("postId") or item.get("post_id") or item.get("id") or create_time or int(time.time())

    media_urls = extract_facebook_media_urls(item)
    likes = item.get("reactionsCount") or item.get("likes") or item.get("reactionLikeCount", 0) or 0
    comments = item.get("commentsCount") or item.get("comments", 0) or 0
    shares = item.get("sharesCount") or item.get("shares", 0) or 0

    weight = analysis["weight"]
    if media_urls:
        weight += 0.15
    if likes > 50 or comments > 20:
        weight += 0.1

    # Kiểm tra xem có thuộc 5 Fanpage trọng điểm TP.HCM hay không
    is_verified_fanpage = False
    source_check_str = f"{author_name.lower()} {author_url.lower()} {str(post_url).lower()}"
    for ident in FB_TARGET_PAGE_IDENTIFIERS:
        if ident in source_check_str:
            is_verified_fanpage = True
            break

    if is_verified_fanpage:
        weight += 0.25  # Tăng mạnh trọng số cho nguồn báo chí / fanpage lớn uy tín

    event = {
        "id": f"fb_{post_id}",
        "platform": "facebook",
        "media_type": "post" if not media_urls else ("video" if any("mp4" in u or "video" in u or "reel" in str(post_url) for u in media_urls) else "image_post"),
        "author": author_name,
        "is_verified_source": is_verified_fanpage,
        "source_badge": "Báo chí / Fanpage uy tín TP.HCM" if is_verified_fanpage else "Cộng đồng mạng xã hội",
        "text": cleaned_text,
        "create_time": create_time or int(time.time()),
        "created_at_iso": datetime.fromtimestamp(create_time, timezone.utc).isoformat() if create_time else "",
        "relative_time": format_relative_time(create_time, reference_time) if create_time else "Gần đây",
        "location": {
            "street": hotspot.get("street") or (hotspot["display_name"] if hotspot.get("priority", 3) >= 3 else ""),
            "display_name": hotspot.get("display_name", ""),
            "ward": hotspot["ward"],
            "administrative_unit": hotspot.get("ward", ""),
            "district": hotspot.get("district", ""),
            "region": hotspot.get("region", "TPHCM"),
            "lat": hotspot["lat"],
            "lon": hotspot["lon"],
            "heat_points": hotspot.get("heat_points", [[hotspot["lat"], hotspot["lon"]]]),
            "priority": hotspot.get("priority", 3),
            "type": hotspot["type"],
            "cause": hotspot.get("cause", "rain"),
            "cause_label": hotspot.get("cause_label", "Mưa lớn, nước không thoát kịp"),
            "source": hotspot.get("source", "seed")
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
    - Thu thập bài đăng người dùng & Fanpage qua scraper_one/facebook-posts-search (chuyên sâu, siêu tiết kiệm).
    - Hỗ trợ tìm kiếm theo từ khóa mưa ngập kết hợp nhắm mục tiêu địa bàn TP.HCM (location='Ho Chi Minh City').
    - Ưu tiên và nhận diện 5 Fanpage trọng điểm (Pháp Luật TP.HCM, Thanh Niên, Người Lao Động, VnExpress, Sài Gòn Của Tôi).
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

    def poll_search_posts(
        self,
        query: str = "mưa ngập TP.HCM",
        max_posts: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Cào tìm kiếm bài đăng Facebook thời gian thực qua scraper_one/facebook-posts-search.
        Tối ưu tuyệt đối: location='Ho Chi Minh City', searchType='latest'.
        Chi phí: ~$0.04/lần chạy (siêu tiết kiệm).
        """
        if not self.apify_token:
            return []

        url = f"https://api.apify.com/v2/acts/{FB_ACTOR_ID}/runs?token={self.apify_token}"
        run_input = {
            "query": query,
            "resultsCount": max_posts,
            "searchType": "latest",
            "location": "Ho Chi Minh City"
        }

        try:
            resp = requests.post(url, json=run_input, timeout=30)
            resp.raise_for_status()
            run_data = resp.json().get("data", {})
            run_id = run_data.get("id")
            dataset_id = run_data.get("defaultDatasetId")
            print(f"[Facebook Search] Actor đang chạy cho '{query}' (Run ID: {run_id})...")

            status = self._wait_for_run(run_id, timeout_sec=80)
            if status != "SUCCEEDED":
                print(f"[Facebook Search] Run {run_id} kết thúc với trạng thái: {status}")
                return []

            raw = self._fetch_dataset_items(dataset_id)
            print(f"[Facebook Search] Đã thu thập {len(raw)} kết quả cho '{query}'.")
            return raw
        except Exception as e:
            print(f"[Facebook Search] Lỗi khi cào query '{query}': {e}")
            return []

    def poll_live_apify(
        self,
        search_queries: Optional[List[str]] = None,
        max_posts: int = 12,
        window_minutes: int = DEFAULT_WINDOW_MINUTES
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Cào Facebook thời gian thực chuẩn LIVE MODE:
        - Quét bài đăng mới nhất có liên quan đến ngập lụt, triều cường tại TP.HCM.
        - Khớp địa danh chuẩn mực qua Gazetteer và OSM Geocoder để đưa lên Heatmap.
        - Tự động nhận diện và gia tăng trọng số uy tín cho 5 Fanpage lớn.
        - Tuân thủ chặt chẽ cửa sổ thời gian window_minutes.
        """
        print(f"\n[Facebook Live] Bắt đầu cào bài đăng Facebook thời gian thực qua '{FB_ACTOR_ID}'...")
        raw_items = []
        queries = search_queries or FB_SEARCH_QUERIES

        # Chạy 1 truy vấn kết hợp thông minh duy nhất để kiểm soát chặt chẽ ngân sách
        primary_query = queries[0] if queries else "mưa ngập TP.HCM"
        print(f"[Facebook Live] Thực thi truy vấn trọng tâm: '{primary_query}' (Dung lượng: {max_posts} bài)...")
        try:
            items = self.poll_search_posts(query=primary_query, max_posts=max_posts)
            raw_items.extend(items)
        except Exception as eq:
            print(f"[Facebook Live] Lỗi query '{primary_query}': {eq}")

        now = int(time.time())
        # Cửa sổ lọc thời gian nghiêm ngặt theo yêu cầu:
        # Nếu window=120 phút -> tối đa ~2 tiếng (dung sai tối đa 15% hoặc 20p bù trễ mạng, dưới 3 tiếng)
        # Nếu window=180 phút -> tối đa ~3 tiếng (hơn 3 tiếng một chút nhưng tuyệt đối dưới 4 tiếng)
        tolerance_minutes = min(int(window_minutes * 0.15), 25)
        max_age_sec = (window_minutes + tolerance_minutes) * 60
        events = []
        seen = set()

        for it in raw_items:
            ev = process_facebook_item(it, reference_time=now, max_age_seconds=max_age_sec)
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

        win_label = f"{window_minutes // 60} giờ qua" if (window_minutes >= 60 and window_minutes % 60 == 0) else f"{window_minutes} phút qua"
        if not events:
            win_label = f"{win_label} (Không có ngập mới)"

        stats = {
            "platform": "facebook",
            "mode": "live",
            "raw_count": len(raw_items),
            "events_matched": len(events),
            "active_window": win_label
        }
        print(f"[Facebook Live] Hoàn tất cào Live: {len(raw_items)} bài thô, {len(events)} sự kiện khớp trong cửa sổ ({win_label}).")
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
