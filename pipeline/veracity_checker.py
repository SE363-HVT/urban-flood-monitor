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
from collections import OrderedDict
from concurrent.futures import Future
from threading import BoundedSemaphore, Lock

from pipeline.event_processor import analyze_severity_heuristic, report_url
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
        self.weather_cache = OrderedDict()
        self._weather_inflight = {}
        self._weather_lock = Lock()
        self._consensus_lock = Lock()
        self._media_slots = BoundedSemaphore(2)

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

        is_video_link = any(v in raw_url.lower() for v in ["tiktok.com", "youtube.com", "youtu.be", "/reel/", "/videos/", "/video"]) or ("video" in raw_url.lower())

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
        started = time.monotonic()
        acquired = has_media and self._media_slots.acquire(blocking=False)
        fallback_reason = "inference_unavailable"
        try:
            if has_media and not acquired:
                raise BlockingIOError("media_capacity")
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
                            "timeout_used": ai_timeout,
                            "elapsed_ms": round((time.monotonic() - started) * 1000, 1),
                        }
        except BlockingIOError:
            fallback_reason = "media_capacity"
        except TimeoutError:
            fallback_reason = "timeout"
        except urllib.error.URLError as error:
            fallback_reason = "timeout" if isinstance(error.reason, TimeoutError) else "ai_unreachable"
        except (ValueError, TypeError, AttributeError, OSError):
            fallback_reason = "invalid_or_unavailable_response"
        finally:
            if acquired:
                self._media_slots.release()

        # 2. CƠ CHẾ DỰ PHÒNG (HEURISTIC BASELINE):
        text = str(event.get("text", "")).lower()

        if has_media:
            visual_verified = False
            content_score = 0.75
        else:
            visual_verified = False
            content_score = 0.55

        if any(k in text for k in ["chết máy", "lút bánh", "dắt bộ", "bì bõm", "ngập sâu", "thất thủ", "ngập lụt", "biển nước"]):
            content_score = min(1.0, content_score + 0.20)

        # Trích xuất ASTE triplets động theo ngữ cảnh bài đăng (Đề xuất 3)
        triplets = event.get("aste_triplets", []) or event.get("triplets", [])
        if not triplets:
            analysis = analyze_severity_heuristic(event.get("text", "") or event.get("title", ""))
            aspect_name = (
                event.get("aspect") or
                (event.get("location", {}).get("display_name") if isinstance(event.get("location"), dict) else "") or
                event.get("street") or
                "Điểm ngập TP.HCM"
            )
            if analysis:
                triplets = [{
                    "aspect": aspect_name,
                    "opinion": analysis.get("opinion", "ngập nước"),
                    "polarity": analysis.get("polarity", "NEG"),
                    "confidence": 0.88
                }]
            else:
                triplets = [{
                    "aspect": aspect_name,
                    "opinion": "ngập nước",
                    "polarity": "NEG",
                    "confidence": 0.70
                }]

        return {
            "source": "heuristic_baseline",
            "branch": "heuristic",
            "visual_verified": visual_verified,
            "content_score": round(content_score, 2),
            "triplets": triplets,
            "fallback_reason": fallback_reason,
            "elapsed_ms": round((time.monotonic() - started) * 1000, 1),
        }

    # =========================================================================
    # TẦNG 2: ĐỐI SOÁT KHÍ TƯỢNG (THEO TỌA ĐỘ ĐỊA ĐIỂM & KHUNG GIỜ ĐĂNG TẢI)
    # =========================================================================
    def _weather_series(self, lat, lon, local_day, historical):
        lat, lon = round(lat, 2), round(lon, 2)
        key = (lat, lon, local_day if historical else None)
        with self._weather_lock:
            cached = self.weather_cache.get(key)
            if cached and cached[0] > time.monotonic():
                self.weather_cache.move_to_end(key)
                return cached[1]
            pending = self._weather_inflight.get(key)
            if pending is None:
                pending = self._weather_inflight[key] = Future()
                fetch = True
            else:
                fetch = False
        if not fetch:
            return pending.result()

        try:
            if historical:
                endpoint = "https://archive-api.open-meteo.com/v1/archive"
                dates = f"start_date={local_day}&end_date={local_day}"
            else:
                endpoint = "https://api.open-meteo.com/v1/forecast"
                dates = "past_days=1&forecast_days=1"
            url = f"{endpoint}?latitude={lat}&longitude={lon}&{dates}&hourly=precipitation,rain&timezone=Asia%2FBangkok"
            req = urllib.request.Request(url, headers={"User-Agent": "SE363-UrbanFlood-Monitor/1.0"})
            with urllib.request.urlopen(req, timeout=6) as response:
                hourly = json.load(response)["hourly"]
            series = {}
            for field in ("precipitation", "rain"):
                for hour, value in zip(hourly["time"], hourly.get(field, [])):
                    if isinstance(value, (int, float)) and math.isfinite(value) and value >= 0:
                        series[hour] = max(value, series.get(hour, 0))
            if not series:
                raise ValueError("Open-Meteo hourly precipitation is missing")
            result = series, None
            ttl = 86400 if historical else 300
        except (OSError, TypeError, ValueError, KeyError) as error:
            result = {}, type(error).__name__
            ttl = 30
        finally:
            with self._weather_lock:
                self._weather_inflight.pop(key, None)
                if "result" in locals():
                    self.weather_cache[key] = (time.monotonic() + ttl, result)
                    self.weather_cache.move_to_end(key)
                    if len(self.weather_cache) > 512:
                        self.weather_cache.popitem(last=False)
                    pending.set_result(result)
                else:
                    pending.cancel()
        return result

    def check_weather_plausibility(self, lat: float, lon: float, timestamp: int, is_tidal: bool = False) -> Dict[str, Any]:
        """Score rainfall near the original posting time using Open-Meteo."""
        if not self.enable_weather or not lat or not lon:
            return {"checked": False, "score": 0.60, "plausible": True, "reason": "Weather check bypassed"}
        started = time.monotonic()
        local_time = datetime.fromtimestamp(timestamp, timezone(timedelta(hours=7)))
        historical = timestamp < time.time() - 86400
        series, error = self._weather_series(lat, lon, local_time.date().isoformat(), historical)
        target = local_time.strftime("%Y-%m-%dT%H:00")
        value = None
        if target in series:
            window = 2 if historical else 1
            hours = [(local_time + timedelta(hours=i)).strftime("%Y-%m-%dT%H:00")
                     for i in range(-window, window + 1)]
            value = max(series[hour] for hour in hours if hour in series)

        if value is None:
            score = 0.90 if is_tidal and not historical else 0.60
            reason = f"Open-Meteo thiếu dữ liệu giờ đăng ({error or 'missing_hour'})"
            if is_tidal and not historical:
                reason += ". Có bằng chứng điểm triều cường"
        elif value >= 5.0:
            score, reason = 1.0, f"Open-Meteo ghi nhận mưa lớn ({value} mm/h)"
        elif value > 0:
            score, reason = 0.85, f"Open-Meteo ghi nhận có mưa ({value} mm/h)"
        elif is_tidal and not historical:
            score, reason = 0.90, "Open-Meteo ghi nhận không mưa. Đây là điểm có bằng chứng triều cường"
        else:
            score, reason = 0.50, "Open-Meteo ghi nhận không mưa (0 mm/h)"
        return {
            "checked": value is not None,
            "precipitation_mm": value,
            "score": score,
            "plausible": True,
            "reason": reason,
            "source": "open_meteo_archive" if historical else "open_meteo_forecast",
            "elapsed_ms": round((time.monotonic() - started) * 1000, 1),
        }

    # =========================================================================
    # TẦNG 3: ĐỒNG THUẬN KHÔNG - THỜI GIAN (60 PHÚT & BÁN KÍNH 500M)
    # =========================================================================
    def calculate_consensus(self, lat: float, lon: float, event_time: int, identity=None, url="") -> Tuple[float, int, List[str]]:
        """
        Tìm kiếm các sự kiện lân cận trong bán kính 500m và thời gian 60 phút.
        Trả về: (Điểm đồng thuận, Số lượng bằng chứng, Danh sách ID bằng chứng).
        """
        evidence_ids = []
        seen_ids = {identity} if identity else set()
        seen_urls = {url} if url else set()
        now = int(time.time())
        is_cur_sim = (abs(now - event_time) > 86400)

        cutoff_time = event_time - (self.window_seconds * 2)
        self.recent_events = [e for e in self.recent_events[-2048:] if e.get("timestamp", 0) >= cutoff_time or is_cur_sim]

        for past in self.recent_events:
            p_lat = past.get("lat")
            p_lon = past.get("lon")
            p_time = past.get("timestamp", 0)

            if not p_lat or not p_lon:
                continue

            dist = haversine_distance_meters(lat, lon, p_lat, p_lon)
            time_diff = abs(event_time - p_time)

            if dist <= self.radius_meters and time_diff <= self.window_seconds:
                previous_id, previous_url = past.get("id"), past.get("url")
                if not previous_id or previous_id in seen_ids or (previous_url and previous_url in seen_urls):
                    continue
                evidence_ids.append(str(previous_id))
                seen_ids.add(previous_id)
                if previous_url:
                    seen_urls.add(previous_url)

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
            if lat and lon and loc_dict.get("precision") not in ("ward", "city"):
                raw_identity = event.get("canonical_id") or event.get("id")
                identity = str(raw_identity) if raw_identity else None
                url = report_url(event.get("url"))
                with self._consensus_lock:
                    consensus_score, evidence_count, evidence_ids = self.calculate_consensus(
                        lat, lon, event_time, identity, url
                    )
                    if identity:
                        self.recent_events.append({
                            "id": identity, "url": url, "lat": lat, "lon": lon, "timestamp": event_time,
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
            if content_eval.get("triplets"):
                prim = content_eval["triplets"][0]
                if not event_copy.get("opinion"):
                    event_copy["opinion"] = prim.get("opinion")
                if not event_copy.get("polarity"):
                    event_copy["polarity"] = prim.get("polarity")
                if not event_copy.get("sentiment"):
                    pol = str(prim.get("polarity", "NEG")).upper()
                    event_copy["sentiment"] = "positive" if pol == "POS" else ("neutral" if pol == "NEU" else "negative")
                if not event_copy.get("triplets"):
                    event_copy["triplets"] = content_eval["triplets"]

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
