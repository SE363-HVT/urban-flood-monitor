# -*- coding: utf-8 -*-
"""
pipeline/veracity_checker.py
Module Xác Thực Dữ Liệu & Phòng Chống Báo Cáo Sai Lệch / Tin Giả (Data Veracity & Fake Report Mitigation).

Cơ chế hoạt động (Multi-tier Defense):
1. Tầng 1: Đánh giá độ tin cậy nội dung & hình ảnh (Content/Visual Verification).
   - Kết nối Multimodal AI Microservice (Port 8001) qua HTTP REST API với Dynamic Adaptive Timeout:
     * has_media == False (Văn bản thuần): timeout = 0.5s (Fast Path PhoBERT <= 35ms)
     * has_media == True (Video/ảnh): timeout = 3.5s (Slow Path CLIP + PhoWhisper + BARTpho)
   - Graceful fallback: Dùng luật heuristic kiểm tra link media và từ khóa nếu microservice offline.
2. Tầng 2: Đối soát Khí tượng thực tế (Weather Cross-Check).
   - Live Mode: Truy vấn lượng mưa Open-Meteo Forecast API theo đúng tọa độ điểm ngập VÀ KHUNG GIỜ ĐĂNG BÀI (Asia/Bangkok).
   - Simulation / Historical Mode: Tự động đối soát lượng mưa lịch sử vào đúng thời điểm đăng tải bài viết tại tọa độ điểm ngập.
3. Tầng 3: Đồng thuận Không - Thời gian (Spatio-Temporal Consensus).
   - Gom cụm bài đăng trong khung trượt 60 phút (1 tiếng) và bán kính 500m.
4. Tầng 4: Tổng hợp Điểm Tin Cậy (Confidence Score) & Phân loại:
   - >= 0.75: Confirmed (🔴 Đã xác thực - Kích hoạt cảnh báo đỏ)
   - 0.50 - 0.74: Suspect (🟡 Nghi vấn - Cảnh báo thăm dò / chờ thêm tin)
   - 0.35 - 0.49: Unverified (⚪ Chưa kiểm chứng)
   - < 0.35: Rejected (🚫 Bác bỏ - Chặn tin rác / clip cũ không có mưa)

Hỗ trợ đồng nhất cả Live Mode (thời gian thực) và Simulation Mode (đồng hồ ảo).
"""

import math
import time
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
import os

# Bán kính trái đất (mét) phục vụ tính khoảng cách Haversine
EARTH_RADIUS_METERS = 6371000.0

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CSGT_FILE = os.path.join(DATA_DIR, "csgt_122_flood_hotspots.json")
AI_MICROSERVICE_URL = os.environ.get("AI_MICROSERVICE_URL", "http://localhost:8001/api/v1/predict-multimodal")

def load_tidal_hotspots() -> List[Dict[str, Any]]:
    if os.path.exists(CSGT_FILE):
        try:
            with open(CSGT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [item for item in data if item.get("cause") == "tide"]
        except Exception:
            return []
    return []

TIDAL_HOTSPOTS = load_tidal_hotspots()

def is_tidal_flood_event(event: Dict[str, Any], lat: Optional[float] = None, lon: Optional[float] = None) -> bool:
    """Xác định sự kiện có thuộc nhóm ngập do triều cường hay không."""
    loc = event.get("location")
    if isinstance(loc, dict):
        if loc.get("cause") == "tide":
            return True
        type_str = str(loc.get("type", "")).lower()
        if "triều cường" in type_str or "trieu cuong" in type_str:
            return True

    text = str(event.get("text", "")).lower()
    if any(k in text for k in ["triều cường", "trieu cuong", "nước dâng", "nuoc dang", "tràn bờ", "tran bo"]):
        return True

    if lat is not None and lon is not None:
        for t in TIDAL_HOTSPOTS:
            if haversine_distance_meters(lat, lon, t["lat"], t["lon"]) <= 800:
                return True
    return False


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Tính khoảng cách đường chim bay giữa 2 tọa độ GPS theo mét."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_METERS * c


class VeracityChecker:
    def __init__(
        self,
        window_minutes: int = 60,       # Cửa sổ thời gian đồng thuận: 60 phút (1 tiếng)
        radius_meters: float = 500.0,    # Bán kính đồng thuận không gian: 500m
        enable_weather_check: bool = True
    ):
        self.window_seconds = window_minutes * 60
        self.radius_meters = radius_meters
        self.enable_weather = enable_weather_check

        # Bộ nhớ lưu các sự kiện gần đây để tính đồng thuận: List[Dict[str, Any]]
        self.recent_events: List[Dict[str, Any]] = []

        # Cache kết quả thời tiết theo tọa độ và thời gian
        self.weather_cache: Dict[str, Dict[str, Any]] = {}

    # =========================================================================
    # ĐIỂM CẮM TÍCH HỢP (EXTENSION POINT) CHO MÔ HÌNH AI VỚI DYNAMIC TIMEOUT
    # =========================================================================
    def evaluate_content_ai(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Đánh giá độ tin cậy từ nội dung đa phương thái (Chữ, Âm thanh, Hình ảnh).
        Ưu tiên gọi Multimodal AI Microservice (Port 8001).
        Áp dụng Dynamic Timeout:
          - has_media == False (Văn bản): timeout = 0.5s (Fast Path)
          - has_media == True (Video/Ảnh): timeout = 3.5s (Slow Path)
        Nếu microservice offline hoặc timeout -> Fallback an toàn sang Heuristic Baseline.
        """
        media_val = event.get("media")
        raw_url = str(event.get("url") or "")
        media_urls = list(event.get("media_urls") or [])
        video_url = event.get("video_url")

        is_video_link = any(v in raw_url.lower() for v in ["tiktok.com", "youtube.com", "youtu.be", "/reel/", "/videos/"])

        has_media = bool(
            media_urls or
            video_url or
            is_video_link or
            event.get("media_type") == "video" or
            (isinstance(media_val, dict) and media_val.get("has_media")) or
            (isinstance(media_val, list) and len(media_val) > 0)
        )

        # Dynamic Adaptive Timeout theo Đề xuất Chiến lược 1
        ai_timeout = 3.5 if has_media else 0.5

        # 1. Thử kết nối Microservice AI với Dynamic Timeout
        try:
            effective_media = media_urls
            if not effective_media and is_video_link:
                effective_media = [raw_url]

            payload = {
                "post_id": str(event.get("id") or event.get("canonical_id") or "event_raw"),
                "text": event.get("text") or event.get("title", ""),
                "media_urls": effective_media,
                "video_url": video_url or (raw_url if is_video_link else None)
            }
            req_data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(
                AI_MICROSERVICE_URL,
                data=req_data,
                headers={"Content-Type": "application/json", "User-Agent": "SE363-Veracity/2.5"}
            )
            with urllib.request.urlopen(req, timeout=ai_timeout) as resp:
                if resp.status == 200:
                    ai_resp = json.loads(resp.read().decode("utf-8"))
                    if ai_resp.get("status") == "success":
                        v_pred = ai_resp.get("visual_prediction", {})
                        triplets = ai_resp.get("aste_triplets") or ai_resp.get("triplets") or []
                        branch = ai_resp.get("branch", "slow_path" if has_media else "fast_path")
                        return {
                            "source": "friend_multimodal_ai",
                            "branch": branch,
                            "visual_verified": v_pred.get("is_flood", False) if has_media else False,
                            "content_score": round(float(ai_resp.get("content_confidence_score", 0.85)), 2),
                            "triplets": triplets,
                            "audio_transcript": ai_resp.get("audio_transcript", ""),
                            "timeout_used": ai_timeout
                        }
        except Exception:
            pass

        # 2. CƠ CHẾ DỰ PHÒNG (HEURISTIC BASELINE):
        text = str(event.get("text", "")).lower()

        if has_media:
            visual_verified = True
            content_score = 0.75
        else:
            visual_verified = False
            content_score = 0.50

        if any(k in text for k in ["chết máy", "lút bánh", "dắt bộ", "bì bõm", "ngập sâu", "thất thủ", "ngập lụt", "biển nước"]):
            content_score = min(1.0, content_score + 0.15)

        return {
            "source": "heuristic_baseline",
            "branch": "heuristic",
            "visual_verified": visual_verified,
            "content_score": round(content_score, 2),
            "triplets": event.get("aste_triplets", []) or event.get("triplets", [])
        }

    # =========================================================================
    # TẦNG 2: ĐỐI SOÁT KHÍ TƯỢNG (THEO TỌA ĐỘ ĐỊA ĐIỂM & KHUNG GIỜ ĐĂNG TẢI)
    # =========================================================================
    def check_weather_plausibility(self, lat: float, lon: float, timestamp: int, is_tidal: bool = False) -> Dict[str, Any]:
        """
        Kiểm tra thời tiết thực tế tại tọa độ sự kiện.
        - Tọa độ: Lấy chính xác tọa độ GPS của điểm ngập.
        - Thời gian: Lấy theo khung giờ bài viết được đăng tải (Asia/Bangkok +7).
        """
        if not self.enable_weather or not lat or not lon:
            return {"checked": False, "score": 0.60, "plausible": True, "reason": "Weather check bypassed"}

        now = int(time.time())
        # Nếu mốc thời gian khác biệt quá 24h so với thời điểm chạy máy -> Bắt buộc gọi Archive API
        is_historical = (abs(now - timestamp) > 86400) or (timestamp < now - 3600*24)
        lat_grid = round(lat, 2)
        lon_grid = round(lon, 2)

        if is_historical:
            # 1. ĐỐI SOÁT LỊCH SỬ: Theo tọa độ điểm ngập và giờ đăng bài gốc theo múi giờ Việt Nam (Archive API)
            tz_vn = timezone(timedelta(hours=7))
            post_dt = datetime.fromtimestamp(timestamp, tz_vn)
            hour = post_dt.hour
            date_str = post_dt.strftime("%Y-%m-%d")
            cache_key = f"hist_{lat_grid}_{lon_grid}_{date_str}_{hour // 2}"
            if cache_key in self.weather_cache:
                return self.weather_cache[cache_key]

            try:
                date_str = datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y-%m-%d")
                url = (
                    f"https://archive-api.open-meteo.com/v1/archive?"
                    f"latitude={lat}&longitude={lon}&start_date={date_str}&end_date={date_str}&hourly=precipitation,rain&timezone=Asia%2FBangkok"
                )
                req = urllib.request.Request(url, headers={"User-Agent": "SE363-UrbanFlood-Monitor/1.0"})
                with urllib.request.urlopen(req, timeout=6) as response:
                    payload = json.loads(response.read().decode("utf-8"))

                hourly_precip = payload.get("hourly", {}).get("precipitation", [])
                val = 0.0
                if hourly_precip and len(hourly_precip) > hour:
                    start_h = max(0, hour - 2)
                    end_h = min(len(hourly_precip), hour + 3)
                    val = max(hourly_precip[start_h:end_h]) if hourly_precip[start_h:end_h] else 0.0

                if val >= 5.0:
                    score = 1.0
                    plausible = True
                    desc = f"Trạm khí tượng lịch sử đối soát: Mưa lớn ({val} mm/h lúc {hour}h ngày {date_str})"
                elif val > 0.0:
                    score = 0.85
                    plausible = True
                    desc = f"Trạm khí tượng lịch sử đối soát: Có mưa ({val} mm/h lúc {hour}h ngày {date_str})"
                else:
                    score = 0.50
                    plausible = True
                    desc = f"Trạm khí tượng lịch sử ghi nhận không mưa (0.0 mm/h lúc {hour}h ngày {date_str})"

                res = {
                    "checked": True,
                    "precipitation_mm": val,
                    "score": score,
                    "plausible": plausible,
                    "reason": desc
                }
                self.weather_cache[cache_key] = res
                return res

            except Exception as e:
                date_str = datetime.fromtimestamp(timestamp, timezone.utc).strftime("%d/%m/%Y")
                hour = datetime.fromtimestamp(timestamp, timezone.utc).hour
                res = {
                    "checked": False,
                    "precipitation_mm": 0.0,
                    "score": 0.60,
                    "plausible": True,
                    "reason": f"Không có dữ liệu trạm khí tượng lưu trữ lúc {hour}h ngày {date_str} ({e})"
                }
                self.weather_cache[cache_key] = res
                return res

        else:
            # 2. LIVE MODE: Thời gian thực theo đúng tọa độ điểm ngập VÀ KHUNG GIỜ ĐĂNG BÀI
            # Open-Meteo Forecast endpoint trả về 48h (hôm qua + hôm nay)
            tz_vn = timezone(timedelta(hours=7))
            post_dt = datetime.fromtimestamp(timestamp, tz_vn)
            target_hour_str = post_dt.strftime("%Y-%m-%dT%H:00")
            cache_key = f"live_{lat_grid}_{lon_grid}_{target_hour_str}"
            if cache_key in self.weather_cache:
                return self.weather_cache[cache_key]

            try:
                url = (
                    f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={lat}&longitude={lon}&hourly=precipitation,rain&past_days=1&forecast_days=1&timezone=Asia%2FBangkok"
                )
                req = urllib.request.Request(url, headers={"User-Agent": "SE363-UrbanFlood-Monitor/1.0"})
                with urllib.request.urlopen(req, timeout=6) as response:
                    payload = json.loads(response.read().decode("utf-8"))

                hourly = payload.get("hourly", {})
                times = hourly.get("time", [])
                precips = hourly.get("precipitation", [])
                rains = hourly.get("rain", [])

                val = 0.0
                if target_hour_str in times:
                    idx = times.index(target_hour_str)
                    start_i = max(0, idx - 1)
                    end_i = min(len(times), idx + 2)
                    for i in range(start_i, end_i):
                        p = float(precips[i]) if i < len(precips) else 0.0
                        r = float(rains[i]) if i < len(rains) else 0.0
                        val = max(val, p, r)

                if val >= 5.0:
                    score = 1.0
                    plausible = True
                    desc = f"Trạm khí tượng thời gian thực: Mưa lớn ({val} mm/h lúc {post_dt.hour}h)"
                elif val > 0.0:
                    score = 0.85
                    plausible = True
                    desc = f"Trạm khí tượng thời gian thực: Có mưa ({val} mm/h lúc {post_dt.hour}h)"
                else:
                    if is_tidal:
                        score = 0.90
                        plausible = True
                        desc = "Điểm ngập triều cường đặc trưng (PC08 CSGT) - Triều dâng ven sông/kênh rạch (không phụ thuộc mưa)"
                    else:
                        score = 0.50
                        plausible = True
                        desc = f"Không ghi nhận mưa lúc {post_dt.hour}h (ngập do triều cường hoặc đọng nước)"

                res = {
                    "checked": True,
                    "precipitation_mm": val,
                    "score": score,
                    "plausible": plausible,
                    "reason": desc
                }
                self.weather_cache[cache_key] = res
                return res

            except Exception as e:
                if is_tidal:
                    fallback_res = {
                        "checked": True,
                        "precipitation_mm": 0.0,
                        "score": 0.90,
                        "plausible": True,
                        "reason": f"Điểm ngập triều cường đặc trưng (PC08 CSGT) - Triều dâng ven sông/kênh rạch (Open-Meteo fallback: {e})"
                    }
                else:
                    fallback_res = {
                        "checked": False,
                        "score": 0.60,
                        "plausible": True,
                        "reason": f"Weather API offline fallback ({e})"
                    }
                return fallback_res

    # =========================================================================
    # TẦNG 3: ĐỒNG THUẬN KHÔNG - THỜI GIAN (60 PHÚT & BÁN KÍNH 500M)
    # =========================================================================
    def calculate_consensus(self, lat: float, lon: float, event_time: int) -> Tuple[float, int, List[str]]:
        """
        Tìm kiếm các sự kiện lân cận trong bán kính 500m và thời gian 60 phút.
        Trả về: (Điểm đồng thuận, Số lượng bằng chứng, Danh sách ID bằng chứng).
        """
        evidence_ids = []
        now = int(time.time())
        is_cur_sim = (abs(now - event_time) > 86400)

        cutoff_time = event_time - (self.window_seconds * 2)
        self.recent_events = [e for e in self.recent_events if e.get("timestamp", 0) >= cutoff_time or is_cur_sim]

        for past in self.recent_events:
            p_lat = past.get("lat")
            p_lon = past.get("lon")
            p_time = past.get("timestamp", 0)

            if not p_lat or not p_lon:
                continue

            dist = haversine_distance_meters(lat, lon, p_lat, p_lon)
            time_diff = abs(event_time - p_time)

            if dist <= self.radius_meters and time_diff <= self.window_seconds:
                if past.get("id"):
                    evidence_ids.append(str(past["id"]))

        evidence_count = len(evidence_ids) + 1
        if evidence_count >= 3:
            consensus_score = 1.0
        elif evidence_count == 2:
            consensus_score = 0.80
        else:
            consensus_score = 0.50

        return consensus_score, evidence_count, evidence_ids

    # =========================================================================
    # TẦNG 4: TỔNG HỢP XÁC THỰC TOÀN TRÌNH (TÍCH HỢP 4 TẦNG PHÒNG THỦ)
    # =========================================================================
    def verify_event(self, event: Dict[str, Any], reference_time: Optional[int] = None) -> Dict[str, Any]:
        """
        Xác thực độ tin cậy của sự kiện, gắn thêm trường 'veracity' mà không sửa đổi dữ liệu gốc.
        Hỗ trợ cả Live Mode (reference_time = None) và Simulation Mode (truyền mốc thời gian ảo).
        """
        try:
            post_time = (
                event.get("create_time") or 
                event.get("timestamp") or 
                event.get("published_time") or 
                event.get("publish_time") or 
                event.get("historical_timestamp")
            )
            event_time = post_time or reference_time or int(time.time())
            weather_time = event.get("historical_timestamp") or post_time or reference_time or event_time
            loc = event.get("location")
            loc_dict = loc if isinstance(loc, dict) else {}
            lat = event.get("lat") or loc_dict.get("lat")
            lon = event.get("lon") or loc_dict.get("lon")

            # 1. Đánh giá nội dung / thị giác
            content_eval = self.evaluate_content_ai(event)
            content_score = content_eval["content_score"]

            # Xác định xem sự kiện có thuộc nhóm ngập do triều cường hay không
            is_tidal = is_tidal_flood_event(event, lat, lon)

            # 2. Đối soát thời tiết (theo tọa độ cụ thể & khung giờ đăng tải lịch sử hoặc thời gian thực)
            weather_eval = self.check_weather_plausibility(lat, lon, weather_time, is_tidal=is_tidal) if (lat and lon) else {
                "checked": False, "score": 0.60, "plausible": True, "reason": "No coordinates for weather"
            }
            weather_score = weather_eval["score"]

            # 3. Tính điểm đồng thuận không gian - thời gian (60 phút / 500m)
            if lat and lon:
                consensus_score, evidence_count, evidence_ids = self.calculate_consensus(lat, lon, event_time)
                self.recent_events.append({
                    "id": event.get("id"),
                    "lat": lat,
                    "lon": lon,
                    "timestamp": event_time
                })
            else:
                consensus_score = 0.40
                evidence_count = 1
                evidence_ids = []

            # 4. Công thức tính điểm tin cậy tổng thể
            total_confidence = (
                0.40 * content_score +
                0.35 * weather_score +
                0.25 * consensus_score
            )
            total_confidence = round(min(1.0, max(0.0, total_confidence)), 2)

            # 5. Phân loại trạng thái
            if total_confidence >= 0.75 or evidence_count >= 3:
                status = "confirmed"
                label = "Đã xác thực"
            elif total_confidence >= 0.50:
                status = "suspect"
                label = "Nghi vấn (Chờ kiểm chứng)"
            elif total_confidence >= 0.35:
                status = "unverified"
                label = "Chưa kiểm chứng"
            else:
                status = "rejected"
                label = "Cảnh báo tin không xác thực"

            event_copy = dict(event)
            event_copy["veracity"] = {
                "confidence_score": total_confidence,
                "status": status,
                "status_label": label,
                "evidence_count": evidence_count,
                "correlated_event_ids": evidence_ids,
                "content_check": content_eval,
                "weather_check": weather_eval,
                "is_tidal_point": is_tidal,
                "consensus_window_minutes": 60,
                "evaluated_at": datetime.now(timezone.utc).isoformat()
            }
            return event_copy
        except Exception as e:
            event_copy = dict(event)
            event_copy["veracity"] = {
                "confidence_score": 0.60,
                "status": "unverified",
                "status_label": "Chưa kiểm chứng",
                "evidence_count": 1,
                "correlated_event_ids": [],
                "content_check": {"source": "fallback", "visual_verified": False, "content_score": 0.5},
                "weather_check": {"checked": False, "reason": f"Fallback ({e})"},
                "consensus_window_minutes": 60,
                "evaluated_at": datetime.now(timezone.utc).isoformat()
            }
            return event_copy
