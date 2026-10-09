"""
pipeline/veracity_checker.py
Module Xác Thực Dữ Liệu & Phòng Chống Báo Cáo Sai Lệch / Tin Giả (Data Veracity & Fake Report Mitigation).

Cơ chế hoạt động (Multi-tier Defense):
1. Tầng 1: Đánh giá độ tin cậy nội dung & hình ảnh (Content/Visual Verification).
   - [BASELINE HIỆN TẠI]: Dùng luật heuristic kiểm tra link media và từ khóa.
   - [ĐIỂM CẮM CHO BẠN BẠN]: Sẵn sàng kết nối mô hình Image Classifier + Whisper ASR + ASTE.
2. Tầng 2: Đối soát Khí tượng thực tế (Weather Cross-Check).
   - Live Mode: Truy vấn lượng mưa thời gian thực từ Open-Meteo Forecast API tại tọa độ cụ thể của điểm ngập.
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
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple

import os
# Bán kính trái đất (mét) phục vụ tính khoảng cách Haversine
EARTH_RADIUS_METERS = 6371000.0

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CSGT_FILE = os.path.join(DATA_DIR, "csgt_122_flood_hotspots.json")

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
    # ĐIỂM CẮM TÍCH HỢP (EXTENSION POINT) CHO MÔ HÌNH AI CỦA BẠN BẠN
    # =========================================================================
    def evaluate_content_ai(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Đánh giá độ tin cậy từ nội dung đa phương thái (Chữ, Âm thanh, Hình ảnh).
        
        >>> ĐÂY CHÍNH LÀ NƠI BẠN BẠN SẼ CẮM MÔ HÌNH VÀO SAU NÀY <<<
        Ví dụ khi có mô hình:
            from models.multimodal_detector import predict_flood_multimodal
            res = predict_flood_multimodal(text=event['text'], media_urls=event.get('media_urls', []))
            return {
                "source": "friend_multimodal_ai",
                "visual_verified": res['has_water'],
                "content_score": res['confidence'],
                "triplets": res['triplets']
            }
        """
        # [CƠ CHẾ DỰ PHÒNG HIỆN TẠI - HEURISTIC BASELINE]:
        media_val = event.get("media")
        has_media = False
        if (
            event.get("media_urls") or
            event.get("video_url") or
            event.get("media_type") == "video" or
            bool(event.get("url")) or
            (isinstance(media_val, dict) and media_val.get("has_media")) or
            (isinstance(media_val, list) and len(media_val) > 0)
        ):
            has_media = True

        text = str(event.get("text", "")).lower()

        # Nếu có video/ảnh thật từ mạng xã hội
        if has_media:
            visual_verified = True
            content_score = 0.75
        else:
            visual_verified = False
            content_score = 0.50

        # Nếu text có từ khóa khẳng định mạnh (chết máy, ngập lút bánh, ngập sâu, thất thủ...)
        if any(k in text for k in ["chết máy", "lút bánh", "dắt bộ", "bì bõm", "ngập sâu", "thất thủ", "ngập lụt", "biển nước"]):
            content_score = min(1.0, content_score + 0.15)

        return {
            "source": "heuristic_baseline",  # Sau này đổi thành "friend_multimodal_ai"
            "visual_verified": visual_verified,
            "content_score": round(content_score, 2),
            "triplets": event.get("aste_triplets", [])
        }

    # =========================================================================
    # TẦNG 2: ĐỐI SOÁT KHÍ TƯỢNG (THEO TỌA ĐỘ ĐỊA ĐIỂM & KHUNG GIỜ ĐĂNG TẢI)
    # =========================================================================
    def check_weather_plausibility(self, lat: float, lon: float, timestamp: int, is_tidal: bool = False) -> Dict[str, Any]:
        """
        Kiểm tra thời tiết thực tế tại tọa độ sự kiện.
        - Tọa độ: Lấy chính xác tọa độ GPS của điểm ngập (hoặc lưới 1km lân cận).
        - Thời gian: Lấy theo khung giờ bài viết được đăng tải (cửa sổ ±2 giờ).
        """
        if not self.enable_weather or not lat or not lon:
            return {"checked": False, "score": 0.60, "plausible": True, "reason": "Weather check bypassed"}

        now = int(time.time())
        is_historical = (abs(now - timestamp) > 86400)
        lat_grid = round(lat, 2)
        lon_grid = round(lon, 2)

        if is_historical:
            # 1. ĐỐI SOÁT LỊCH SỬ: Theo tọa độ điểm ngập và giờ đăng bài gốc
            hour = datetime.fromtimestamp(timestamp, timezone.utc).hour
            cache_key = f"hist_{lat_grid}_{lon_grid}_{timestamp // 86400}_{hour // 2}"
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
                    # Lấy lượng mưa trong khung ±2 tiếng xung quanh giờ đăng tải
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
                    "reason": f"Không có dữ liệu trạm khí tượng lưu trữ lúc {hour}h ngày {date_str}"
                }
                self.weather_cache[cache_key] = res
                return res

        else:
            # 2. LIVE MODE: Thời gian thực theo đúng tọa độ điểm ngập
            cache_key = f"live_{lat_grid}_{lon_grid}_{now // 1800}"
            if cache_key in self.weather_cache:
                return self.weather_cache[cache_key]

            try:
                url = (
                    f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={lat}&longitude={lon}&current=precipitation,rain&timezone=Asia%2FBangkok"
                )
                req = urllib.request.Request(url, headers={"User-Agent": "SE363-UrbanFlood-Monitor/1.0"})
                with urllib.request.urlopen(req, timeout=6) as response:
                    payload = json.loads(response.read().decode("utf-8"))

                current = payload.get("current", {})
                precip = float(current.get("precipitation", 0.0))
                rain = float(current.get("rain", 0.0))
                val = max(precip, rain)

                if val >= 5.0:
                    score = 1.0
                    plausible = True
                    desc = f"Trạm khí tượng thời gian thực: Mưa lớn ({val} mm/h)"
                elif val > 0.0:
                    score = 0.85
                    plausible = True
                    desc = f"Trạm khí tượng thời gian thực: Có mưa rào ({val} mm/h)"
                else:
                    if is_tidal:
                        score = 0.90
                        plausible = True
                        desc = "Điểm ngập triều cường đặc trưng (PC08 CSGT) - Triều dâng ven sông/kênh rạch (không phụ thuộc mưa)"
                    else:
                        score = 0.45
                        plausible = True
                        desc = "Không ghi nhận mưa tại thời điểm này (có thể do triều cường)"

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

        # Dọn dẹp các sự kiện đã quá 2 tiếng để giữ bộ nhớ nhẹ
        cutoff_time = event_time - (self.window_seconds * 2)
        self.recent_events = [e for e in self.recent_events if e.get("timestamp", 0) >= cutoff_time or is_cur_sim]

        for past in self.recent_events:
            p_lat = past.get("lat")
            p_lon = past.get("lon")
            p_time = past.get("timestamp", 0)

            if not p_lat or not p_lon:
                continue

            time_diff = abs(event_time - p_time)
            is_past_sim = (abs(now - p_time) > 86400)

            # Nếu trong Live mode: Phải trong khung 60 phút
            # Nếu trong Simulation mode: Cùng đợt ngập mô phỏng hoặc trong khung 60 phút
            if time_diff > self.window_seconds and not (is_cur_sim and is_past_sim):
                continue

            dist = haversine_distance_meters(lat, lon, p_lat, p_lon)
            if dist <= self.radius_meters:
                evidence_ids.append(str(past.get("id")))

        evidence_count = len(evidence_ids) + 1  # Tính cả sự kiện hiện tại

        # Thang điểm đồng thuận mềm:
        if evidence_count >= 3:
            consensus_score = 1.0   # Từ 3 người trở lên: Đồng thuận tuyệt đối
        elif evidence_count == 2:
            consensus_score = 0.75  # 2 người cùng báo: Độ tin cậy cao
        else:
            consensus_score = 0.40  # 1 người duy nhất: Điểm thăm dò

        return consensus_score, evidence_count, evidence_ids

    # =========================================================================
    # HÀM XÁC THỰC SỰ KIỆN TỔNG THỂ (MAIN VERIFY FUNCTION)
    # =========================================================================
    def verify_event(self, event: Dict[str, Any], reference_time: Optional[int] = None) -> Dict[str, Any]:
        """
        Xác thực độ tin cậy của sự kiện, gắn thêm trường 'veracity' mà không sửa đổi dữ liệu gốc.
        Hỗ trợ cả Live Mode (reference_time = None) và Simulation Mode (truyền mốc thời gian ảo).
        """
        try:
            event_time = event.get("timestamp") or reference_time or int(time.time())
            loc = event.get("location")
            loc_dict = loc if isinstance(loc, dict) else {}
            lat = event.get("lat") or loc_dict.get("lat")
            lon = event.get("lon") or loc_dict.get("lon")

            # 1. Đánh giá nội dung / thị giác
            content_eval = self.evaluate_content_ai(event)
            content_score = content_eval["content_score"]

            # Xác định xem sự kiện có thuộc nhóm ngập do triều cường hay không
            is_tidal = is_tidal_flood_event(event, lat, lon)

            # 2. Đối soát thời tiết (theo tọa độ cụ thể & khung giờ đăng tải)
            weather_eval = self.check_weather_plausibility(lat, lon, event_time, is_tidal=is_tidal) if (lat and lon) else {
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
