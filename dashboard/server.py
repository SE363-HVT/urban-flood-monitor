# -*- coding: utf-8 -*-
"""
dashboard/server.py - Máy chủ Web phục vụ Bản Đồ Nhiệt Cảnh Báo Ngập Lụt Đa Nền Tảng (Port 8050)
Cung cấp giao diện trực quan và REST API: /api/realtime-heatmap, /api/trigger-poll, /api/toggle-mode, /api/metrics.
Tích hợp thu thập Video TikTok + Bài đăng Facebook.
Tích hợp Module Xác thực dữ liệu & Phòng chống tin giả (VeracityChecker).
Tích hợp Cầu nối PySpark Streaming & In-Memory Redis Hot Serving Store (GEO + ZSET) với Fallback không khóa file.
"""

import http.server
import socketserver
import json
import math
import os
import sys
import time
import socket
import threading
from urllib.parse import urlsplit
from urllib.request import urlopen
from typing import List, Dict, Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from datetime import datetime, timezone
from pipeline.multi_poller import MultiPlatformPoller
from pipeline.live_free_crawler import LiveFreeSocialCrawler
from pipeline.veracity_checker import AI_MICROSERVICE_URL, VeracityChecker
from pipeline.spatio_temporal_clusterer import SpatioTemporalClusterer
from pipeline.event_processor import format_relative_time
from bigdata.streaming.stream_storage import crawler_heartbeat_path, write_json_atomic
from core.config import APIFY_TOKEN, DEFAULT_PORT, DEFAULT_WINDOW_MINUTES, FB_CRAWL_STRATEGY

try:
    import redis
    from redis.backoff import NoBackoff
    from redis.retry import Retry
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(DASHBOARD_DIR, "index.html")
INDEX_V3_FILE = os.path.join(DASHBOARD_DIR, "index_v3.html")

# Khởi tạo bộ kiểm tra độ tin cậy dữ liệu (cửa sổ trượt 60 phút, bán kính 500m)
VERACITY_CHECKER = VeracityChecker(window_minutes=60, radius_meters=500.0, enable_weather_check=True)
CLUSTERER = SpatioTemporalClusterer(radius_meters=400.0, time_window_seconds=2700)


# =============================================================================
# MODULAR MULTI-PANEL OPERATIONS METRICS & BACKGROUND HEARTBEAT WORKER
# =============================================================================

_SERVER_START_TIME = time.time()
_AI_ENDPOINT = urlsplit(AI_MICROSERVICE_URL)
_AI_PORT = _AI_ENDPOINT.port or (443 if _AI_ENDPOINT.scheme == "https" else 80)
_KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
SYSTEM_HEALTH_CACHE = {
    "ai_service": {"status": "UNKNOWN", "latency_ms": -1.0, "port": _AI_PORT},
    "redis": {"status": "UNKNOWN", "latency_ms": -1.0, "port": REDIS_PORT},
    "kafka": {"status": "UNKNOWN", "latency_ms": -1.0, "port": 9092},
    "crawler": {"status": "UNKNOWN", "active_poller": False},
    "last_checked": 0,
    "uptime_seconds": 0
}
_HEALTH_WORKER_STARTED = False


def _ping_service_socket(host: str, port: int, timeout_sec: float = 0.8) -> tuple:
    """Ping socket voi timeout an toan 0.8s trong luong ngam doc lap, do dac do tre ms."""
    t0 = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout_sec):
            latency = round((time.monotonic() - t0) * 1000, 1)
            return True, latency
    except Exception:
        return False, -1.0


def _probe_ai_health():
    result = {"status": "STANDBY", "latency_ms": -1.0, "port": _AI_PORT}
    started = time.monotonic()
    try:
        with urlopen(f"{_AI_ENDPOINT.scheme}://{_AI_ENDPOINT.netloc}/health", timeout=0.8) as response:
            payload = json.load(response)
        if payload.get("status") == "healthy":
            models = payload.get("models") or {}
            ready = models.get("branch_1_phobert_fast") == "active" and all(
                state == "active" for state in models.values()
            )
            result.update(
                status="ONLINE" if ready else "DEGRADED",
                latency_ms=round((time.monotonic() - started) * 1000, 1),
                models=models,
            )
    except (OSError, ValueError, AttributeError):
        pass
    return result


def _probe_kafka_health():
    result = {"status": "STANDBY", "latency_ms": -1.0, "port": 9092, "check": "tcp"}
    for endpoint in _KAFKA_BOOTSTRAP.split(","):
        try:
            address = urlsplit("//" + endpoint.strip())
            host, port = address.hostname, address.port or 9092
        except ValueError:
            continue
        if not host:
            continue
        reachable, latency = _ping_service_socket(host, port)
        result.update(port=port, latency_ms=latency)
        if reachable:
            result["status"] = "ONLINE"
            break
    return result


def _probe_redis_health():
    result = {"status": "STANDBY", "latency_ms": -1.0, "port": REDIS_PORT}
    if not REDIS_AVAILABLE:
        return result
    started = time.monotonic()
    try:
        with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_connect_timeout=0.2,
                         socket_timeout=0.2, retry=Retry(NoBackoff(), 0)) as client:
            if client.ping():
                result.update(status="ONLINE", latency_ms=round((time.monotonic() - started) * 1000, 1))
    except (OSError, redis.RedisError):
        pass
    return result


def start_background_health_worker(interval_seconds: int = 10):
    """Worker chay ngam doc lap, dinh ky cap nhat trang thai cac vi dich vu vao RAM cache."""
    global _HEALTH_WORKER_STARTED
    if _HEALTH_WORKER_STARTED:
        return
    _HEALTH_WORKER_STARTED = True

    def _worker_loop():
        global SYSTEM_HEALTH_CACHE
        while True:
            SYSTEM_HEALTH_CACHE = {
                "ai_service": _probe_ai_health(),
                "redis": _probe_redis_health(),
                "kafka": _probe_kafka_health(),
                "crawler": _probe_crawler_health(GLOBAL_STATE["mode"]),
                "last_checked": int(time.time()),
                "uptime_seconds": int(time.time() - _SERVER_START_TIME),
            }
            time.sleep(interval_seconds)

    t = threading.Thread(target=_worker_loop, daemon=True, name="DashboardHealthWorker")
    t.start()


_SNAPSHOT_LOCK = threading.Lock()
_SNAPSHOT = None


def _probe_crawler_health(mode):
    if mode.endswith("simulation"):
        return {"status": "STANDBY", "active_poller": False}
    try:
        with crawler_heartbeat_path(os.path.join(ROOT_DIR, "data"), "live").open(encoding="utf-8") as stream:
            heartbeat = json.load(stream)
        active = time.time() < heartbeat["expires_at"]
        return {**heartbeat, "status": heartbeat["status"] if active else "STANDBY", "active_poller": active}
    except (OSError, ValueError, KeyError, TypeError):
        return {"status": "UNKNOWN", "active_poller": False}


def get_serving_snapshot():
    """Use one short-lived snapshot for both metrics and the heatmap."""
    global _SNAPSHOT
    requested_mode = GLOBAL_STATE["mode"]
    mode = "simulation" if requested_mode.endswith("simulation") else "live"
    with _SNAPSHOT_LOCK:
        now = time.monotonic()
        if _SNAPSHOT and _SNAPSHOT["mode"] == mode and now < _SNAPSHOT["expires"]:
            return _SNAPSHOT
        snapshot = {
            "mode": mode, "events": GLOBAL_STATE.get("events", []),
            "window": GLOBAL_STATE.get("active_window"), "served_from": "memory",
            "updated_at": GLOBAL_STATE.get("last_updated"), "expires": now + 2,
        }
        client = get_redis_client()
        if client:
            try:
                redis_mode, window, updated_at = client.mget(
                    "flood:serving:mode", "flood:serving:window", "flood:serving:updated_at"
                )
                if redis_mode == mode:
                    events = fetch_events_from_redis(client)
                    if events:
                        snapshot.update(events=events, window=window or snapshot["window"],
                                        updated_at=int(updated_at) if updated_at else snapshot["updated_at"],
                                        served_from="redis")
            except (OSError, ValueError, redis.RedisError):
                pass
        if snapshot["served_from"] != "redis":
            try:
                with open(os.path.join(ROOT_DIR, "data", "live_stream_state.json"), encoding="utf-8") as stream:
                    data = json.load(stream)
                if str(data.get("mode") or "").endswith(mode) and isinstance(data.get("events"), list):
                    updated_at = data.get("updated_at")
                    snapshot.update(events=data["events"], window=data.get("window") or snapshot["window"],
                                    updated_at=int(datetime.fromisoformat(updated_at).timestamp()) if updated_at else None,
                                    served_from="local_file_buffer")
            except (OSError, ValueError, TypeError):
                pass
        _SNAPSHOT = snapshot
        return snapshot


def get_current_active_events() -> List[Dict[str, Any]]:
    return get_serving_snapshot()["events"]


WARD_TO_CLUSTER_MAP = {}

def get_ward_cluster_map() -> Dict[str, str]:
    """Tra cuu nhanh phan vung do thi (TP.HCM cu, Binh Duong cu, Ba Ria - Vung Tau cu) tu 168 DVHC."""
    global WARD_TO_CLUSTER_MAP
    if not WARD_TO_CLUSTER_MAP:
        units_path = os.path.join(ROOT_DIR, "data", "hcmc_168_administrative_units.json")
        if os.path.exists(units_path):
            try:
                with open(units_path, "r", encoding="utf-8") as f:
                    units_data = json.load(f)
                    for item in units_data:
                        w_name = item.get("name")
                        cluster = item.get("region_cluster", "")
                        if w_name:
                            WARD_TO_CLUSTER_MAP[w_name.strip()] = cluster
            except Exception as e:
                logger.warning(f"Could not load administrative units mapping: {e}")
    return WARD_TO_CLUSTER_MAP


def compute_admin_ward_metrics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Phan tich va tong hop so luong diem ngap theo 168 Phuong/Xa moi NQ 1685 va 4 Megacity Zones."""
    ward_counts = {}
    citywide_count = 0
    zone_counts = {
        "TPHCM_Core": 0,
        "ThuDuc": 0,
        "BinhDuong": 0,
        "VungTau": 0
    }
    cluster_map = get_ward_cluster_map()

    for ev in events:
        loc = ev.get("location") or {}
        w = loc.get("ward") or "Toàn thành phố (Chưa rõ phường/xã)"
        reg = (loc.get("region") or "").lower()
        dist = (loc.get("district") or "").lower()
        w_low = w.lower()

        if any(cw in w.lower() for cw in ["toàn thành phố", "chưa rõ", "diện rộng"]):
            citywide_count += 1
        else:
            ward_counts[w] = ward_counts.get(w, 0) + 1

        c_cluster = cluster_map.get(w.strip(), "")
        if c_cluster == "Bình Dương cũ" or any(bd in w_low or bd in dist or bd in reg for bd in ["bình dương", "binh duong", "dĩ an", "thuận an", "thủ dầu một", "bến cát", "tân uyên"]):
            zone_counts["BinhDuong"] += 1
        elif c_cluster == "Bà Rịa - Vũng Tàu cũ" or any(vt in w_low or vt in dist or vt in reg for vt in ["vũng tàu", "vung tau", "bà rịa", "ba ria", "phú mỹ", "côn đảo"]):
            zone_counts["VungTau"] += 1
        elif "thủ đức" in w_low or "thu duc" in dist or "thủ đức" in dist:
            zone_counts["ThuDuc"] += 1
        else:
            zone_counts["TPHCM_Core"] += 1

    sorted_wards = sorted(ward_counts.items(), key=lambda x: x[1], reverse=True)
    top_wards = [{"ward": k, "count": v} for k, v in sorted_wards[:10]]

    return {
        "top_wards": top_wards,
        "ward_counts": ward_counts,
        "citywide_count": citywide_count,
        "zones": zone_counts,
        "total_wards_affected": len(ward_counts)
    }


def _event_timestamp(event):
    for key in ("create_time", "timestamp"):
        value = event.get(key)
        if isinstance(value, bool):
            continue
        try:
            timestamp = float(value)
        except (TypeError, ValueError, OverflowError):
            continue
        if math.isfinite(timestamp) and timestamp > 0:
            return timestamp
    return None


def _normalized_polarity(value):
    value = str(value or "").strip().upper()
    return {"POSITIVE": "POS", "NEGATIVE": "NEG", "NEUTRAL": "NEU"}.get(value, value)


def _event_polarity(event):
    candidates = [event.get("polarity")]
    content = (event.get("veracity") or {}).get("content_check") or {}
    for triplets in (content.get("triplets"), event.get("triplets"), event.get("aste_triplets")):
        if isinstance(triplets, list) and triplets and isinstance(triplets[0], dict):
            candidates.append(triplets[0].get("polarity"))
            break
    candidates.extend((event.get("sentiment"), event.get("status_tag")))
    for value in candidates:
        polarity = _normalized_polarity(value)
        if polarity in {"NEG", "NEU", "POS"}:
            return polarity

    severity = str(event.get("severity") or "").casefold()
    if severity == "recovered" or any(s in severity for s in ("an toàn", "nước rút")):
        return "POS"
    if "dự báo" in severity:
        return "NEU"
    return "NEG"


def compute_time_series_metrics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Đếm theo giờ hiện tại và năm giờ liền trước, dùng thời gian sự kiện."""
    now = time.time()
    local_now = time.localtime(now)
    hour_start = int(now) - local_now.tm_min * 60 - local_now.tm_sec
    first_slot = hour_start - 5 * 3600
    hours = [time.strftime("%H:00", time.localtime(first_slot + i * 3600)) for i in range(6)]
    counts = {"NEG": [0] * 6, "NEU": [0] * 6, "POS": [0] * 6}

    for ev in events:
        timestamp = _event_timestamp(ev)
        if timestamp is not None and first_slot <= timestamp <= now:
            slot = int((timestamp - first_slot) // 3600)
            counts[_event_polarity(ev)][slot] += 1

    return {"hours": hours, "neg": counts["NEG"], "neu": counts["NEU"], "pos": counts["POS"]}


def compute_throughput_metrics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Thong ke toc do cao va phan bo nguon du lieu thuc te: TikTok, Facebook, YouTube, Cong 1022 TP.HCM, Bao chi RSS."""
    platforms = {
        "tiktok": 0,
        "facebook": 0,
        "youtube": 0,
        "citizen_report": 0,
        "news_rss": 0
    }
    veracity_passed = 0
    total = len(events)
    now = time.time()
    recent = 0

    for ev in events:
        timestamp = _event_timestamp(ev)
        if timestamp is not None and now - 60 < timestamp <= now:
            recent += 1
        p = (ev.get("platform") or "").lower()
        src = (ev.get("source") or "").lower()
        txt = (ev.get("text") or "").lower()

        if "tiktok" in p or "tiktok" in src:
            platforms["tiktok"] += 1
        elif "facebook" in p or "facebook" in src:
            platforms["facebook"] += 1
        elif "youtube" in p or "youtube" in src:
            platforms["youtube"] += 1
        elif "1022" in txt or "citizen" in p or "1022" in src:
            platforms["citizen_report"] += 1
        else:
            platforms["news_rss"] += 1

        ver = ev.get("veracity") or {}
        status = str(ver.get("status") or "").strip().lower()
        if status in {"confirmed", "verified", "passed", "cluster_confirmed"}:
            veracity_passed += 1
        elif not status:
            score = ver.get("confidence_score")
            if isinstance(score, (int, float)) and score >= 0.75:
                veracity_passed += 1
            elif score is None:
                legacy_score = ver.get("confidence")
                if isinstance(legacy_score, (int, float)) and legacy_score >= 0.7:
                    veracity_passed += 1

    pass_rate = round((veracity_passed / total * 100), 1) if total else 0.0

    return {
        "current_rpm": recent,
        "platforms": platforms,
        "total_posts": total,
        "veracity_pass_rate": pass_rate
    }


def compute_dashboard_summary() -> Dict[str, Any]:
    """Gom toan bo so lieu 6 Panels vao mot payload JSON duy nhat phuc vu Client (< 10 KB)."""
    snapshot = get_serving_snapshot()
    events = snapshot["events"]
    admin_wards = compute_admin_ward_metrics(events)
    time_series = compute_time_series_metrics(events)
    throughput = compute_throughput_metrics(events)

    # Format live feed items
    formatted_feed = []
    for ev in events[:20]:
        loc = ev.get("location") or {}
        formatted_feed.append({
            "id": ev.get("id"),
            "platform": ev.get("platform", "other"),
            "author": ev.get("author", "Cộng đồng"),
            "road": loc.get("street") or loc.get("display_name") or "Tuyến đường trung tâm",
            "ward": loc.get("ward") or "TP.HCM",
            "relative_time": ev.get("relative_time") or "Gần đây",
            "severity": ev.get("severity", "medium"),
            "text": (ev.get("text") or "")[:120],
            "url": ev.get("url") or "#"
        })

    return {
        "status": "ok",
        "timestamp": int(time.time()),
        "mode": snapshot["mode"],
        "active_window": snapshot["window"],
        "snapshot_updated_at": snapshot["updated_at"],
        "events_count": len(events),
        "system_health": SYSTEM_HEALTH_CACHE,
        "admin_wards": admin_wards,
        "time_series": time_series,
        "throughput": throughput,
        "live_feed": formatted_feed
    }

GLOBAL_STATE = {
    "mode": "live",
    "window_minutes": DEFAULT_WINDOW_MINUTES,
    "active_window": "Đang kết nối dữ liệu...",
    "events": [],
    "last_updated": None,
    "poller": None
}

_REDIS_LAST_CHECK = 0.0
_REDIS_IS_ALIVE = False
_REDIS_CLIENT = None


def get_redis_client():
    """Khởi tạo kết nối Redis an toàn với fast socket check, không làm nghẽn server nếu Redis tắt."""
    global _REDIS_LAST_CHECK, _REDIS_IS_ALIVE, _REDIS_CLIENT
    if not REDIS_AVAILABLE:
        return None
    now = time.time()
    # Nếu kiểm tra gần đây (< 5s) đã biết Redis offline thì bỏ qua ngay lập tức
    if not _REDIS_IS_ALIVE and (now - _REDIS_LAST_CHECK < 5.0):
        return None
    _REDIS_LAST_CHECK = now

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.08)
        res = sock.connect_ex((REDIS_HOST, REDIS_PORT))
        sock.close()
        if res != 0:
            _REDIS_IS_ALIVE = False
            _REDIS_CLIENT = None
            return None
    except Exception:
        _REDIS_IS_ALIVE = False
        _REDIS_CLIENT = None
        return None

    try:
        if _REDIS_CLIENT is None:
            _REDIS_CLIENT = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=0,
                socket_connect_timeout=0.2,
                socket_timeout=0.2,
                retry=Retry(NoBackoff(), 0),
                decode_responses=True
            )
        _REDIS_CLIENT.ping()
        _REDIS_IS_ALIVE = True
        return _REDIS_CLIENT
    except Exception:
        _REDIS_IS_ALIVE = False
        _REDIS_CLIENT = None
        return None


def fetch_events_from_redis(client) -> List[Dict[str, Any]]:
    """Đọc hot state phục vụ Leaflet từ Redis GEO & Timeline Sorted Set (< 3ms)."""
    if not client:
        return []
    try:
        event_ids = client.zrevrange("flood:timeline:zset", 0, 300)
        if not event_ids:
            return []
        pipe = client.pipeline()
        for eid in event_ids:
            pipe.get(f"flood:event:{eid}")
        raw_list = pipe.execute()
        events = []
        for raw in raw_list:
            if raw:
                try:
                    events.append(json.loads(raw))
                except Exception:
                    pass
        return events
    except Exception as e:
        print(f"[Redis Warning] Lỗi đọc dữ liệu Redis: {e}")
        return []


def enrich_events_with_veracity(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Gắn thông tin xác thực dữ liệu, đối soát thời tiết và gom cụm không - thời gian."""
    now_ts = int(time.time())
    enriched = []
    for ev in events:
        loc = ev.get("location", {})
        ev["lat"] = loc.get("lat") or ev.get("lat")
        ev["lon"] = loc.get("lon") or ev.get("lon")
        ctime = ev.get("create_time") or ev.get("timestamp") or now_ts
        ev["timestamp"] = ctime
        ev["create_time"] = ctime
        ref_t = ev.get("historical_timestamp") or ctime
        verified = VERACITY_CHECKER.verify_event(ev, reference_time=ref_t)
        verified["relative_time"] = format_relative_time(ctime, now_ts)
        age = max(0, now_ts - ctime)
        if age <= 7200:
            verified["freshness"] = "strict_2h"
            verified["status_tag"] = "🔴 ĐANG DIỄN RA (< 2 GIỜ)"
        elif age <= 14400:
            verified["freshness"] = "recent_4h"
            verified["status_tag"] = "🟠 ĐỢT MƯA VỪA DỨT (2-4 GIỜ)"
        else:
            verified["freshness"] = "within_24h"
            verified["status_tag"] = "🟡 CẢNH BÁO TRONG NGÀY (4-24 GIỜ)"
        enriched.append(verified)

    # Gom cụm các điểm ngập trùng không gian (<400m) và thời gian (<45p)
    clustered = CLUSTERER.cluster_events(enriched)
    return clustered



def fetch_current_all_events() -> List[Dict[str, Any]]:
    """Lấy danh sách tất cả sự kiện hiện có hợp nhất từ cả Redis, buffer file và memory."""
    all_events_map = {}

    # 1. Từ file buffer live_stream_state.json
    stream_state_file = os.path.join(ROOT_DIR, "data", "live_stream_state.json")
    if os.path.exists(stream_state_file):
        try:
            with open(stream_state_file, "r", encoding="utf-8") as sf:
                data = json.load(sf)
                for ev in data.get("events", []):
                    cid = ev.get("canonical_id") or ev.get("id")
                    if cid:
                        all_events_map[cid] = ev
        except Exception:
            pass

    # 2. Từ Redis In-Memory Serving Store
    r_client = get_redis_client()
    if r_client:
        r_events = fetch_events_from_redis(r_client)
        for ev in r_events:
            cid = ev.get("canonical_id") or ev.get("id")
            if cid:
                all_events_map[cid] = ev

    # 3. Từ memory GLOBAL_STATE
    for ev in GLOBAL_STATE.get("events", []):
        cid = ev.get("canonical_id") or ev.get("id")
        if cid and cid not in all_events_map:
            all_events_map[cid] = ev

    return list(all_events_map.values())


def merge_and_deduplicate_events(base_events: List[Dict[str, Any]], new_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Hòa trộn (merge) danh sách sự kiện mới vào danh sách hiện tại theo cơ chế cộng dồn (Cumulative Ingestion):
    - Đảm bảo: 8 tin Freecrawl + N tin Apify = 8 + N tin trên Heatmap (tuyệt đối không ghi đè mất tin).
    - Khử trùng lặp thông minh theo canonical_id / id và chữ ký ngữ nghĩa (street + opinion + text[:35]).
    """
    combined = []
    seen_ids = set()
    seen_semantics = set()

    # 1. Nạp sự kiện mới (ưu tiên cao)
    for ev in (new_events or []):
        cid = str(ev.get("canonical_id") or ev.get("id") or "")
        loc = ev.get("location", {}) or {}
        street = str(loc.get("street") or "")
        opinion = str(ev.get("opinion") or "")
        txt = str(ev.get("text") or ev.get("title") or "")[:35].strip().lower()
        sem_sig = (street.lower(), opinion.lower(), txt)

        if cid and cid in seen_ids:
            continue
        if street and sem_sig in seen_semantics:
            continue

        if cid:
            seen_ids.add(cid)
        if street:
            seen_semantics.add(sem_sig)
        combined.append(ev)

    # 2. Nạp sự kiện hiện tại (Freecrawl / hệ thống)
    for ev in (base_events or []):
        cid = str(ev.get("canonical_id") or ev.get("id") or "")
        loc = ev.get("location", {}) or {}
        street = str(loc.get("street") or "")
        opinion = str(ev.get("opinion") or "")
        txt = str(ev.get("text") or ev.get("title") or "")[:35].strip().lower()
        sem_sig = (street.lower(), opinion.lower(), txt)

        if cid and cid in seen_ids:
            continue
        if street and sem_sig in seen_semantics:
            continue

        if cid:
            seen_ids.add(cid)
        if street:
            seen_semantics.add(sem_sig)
        combined.append(ev)

    current_time = int(time.time())
    for ev in combined:
        ctime = ev.get("create_time", 0) or ev.get("timestamp", 0)
        age = max(0, current_time - ctime) if ctime > 0 else 0
        if not ev.get("freshness") or not ev.get("status_tag"):
            if age <= 7200:
                ev["freshness"] = "strict_2h"
                ev["status_tag"] = "🔴 ĐANG DIỄN RA (< 2 GIỜ)"
            elif age <= 14400:
                ev["freshness"] = "recent_4h"
                ev["status_tag"] = "🟠 ĐỢT MƯA VỪA DỨT (2-4 GIỜ)"
            else:
                ev["freshness"] = "within_24h"
                ev["status_tag"] = "🟡 CẢNH BÁO TRONG NGÀY (4-24 GIỜ)"
        if not ev.get("relative_time"):
            ev["relative_time"] = format_relative_time(ctime, current_time)

    combined.sort(key=lambda x: (
        2 if x.get("freshness") == "strict_2h" or (current_time - (x.get("create_time", 0) or x.get("timestamp", 0))) <= 7200 else (
            1 if x.get("freshness") == "recent_4h" or (current_time - (x.get("create_time", 0) or x.get("timestamp", 0))) <= 14400 else 0
        ),
        1 if x.get("platform") in ["tiktok", "facebook", "threads", "youtube"] else 0,
        x.get("weight", 1.0),
        x.get("create_time", 0) or x.get("timestamp", 0)
    ), reverse=True)

    return combined

def sync_to_storage(events: List[Dict[str, Any]], mode: str, window_label: str):
    """Ghi đồng bộ tức thì vào Redis In-Memory Store (<3ms) và file JSON fallback."""
    r_client = get_redis_client()
    if r_client:
        try:
            pipe = r_client.pipeline()
            # Cơ chế Upsert liên tục: Giữ nguyên các key còn hạn, không xóa trắng gây mất dữ liệu song song
            for ev in events:
                cid = ev.get("canonical_id") or ev.get("id")
                loc = ev.get("location", {})
                lat = loc.get("lat") or ev.get("lat")
                lon = loc.get("lon") or ev.get("lon")
                ctime = ev.get("create_time", int(time.time()))

                if lat and lon:
                    pipe.geoadd("flood:geo:index", (lon, lat, cid))
                pipe.zadd("flood:timeline:zset", {cid: ctime})
                pipe.set(f"flood:event:{cid}", json.dumps(ev, ensure_ascii=False), ex=86400)

            pipe.set("flood:serving:mode", mode)
            pipe.set("flood:serving:window", window_label)
            pipe.set("flood:serving:updated_at", int(time.time()))
            pipe.execute()
        except Exception as e:
            print(f"[Dashboard Server] Lỗi đồng bộ Redis: {e}")

    # Ghi file fallback
    stream_state_file = os.path.join(ROOT_DIR, "data", "live_stream_state.json")
    try:
        out_data = {
            "mode": f"live_streaming_spark_{mode}",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "window": window_label,
            "events_count": len(events),
            "events": events
        }
        write_json_atomic(stream_state_file, out_data)
    except Exception as e:
        print(f"[Dashboard Server] Lỗi ghi file fallback: {e}")


class HeatmapRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index.html") or self.path.startswith("/?"):
            if not os.path.exists(INDEX_FILE):
                self.send_error(404, "Index file not found")
                return
            with open(INDEX_FILE, "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(content)
            return

        
        elif self.path in ["/index_v3.html", "/v3", "/index_v3"]:
            target_file = INDEX_V3_FILE if os.path.exists(INDEX_V3_FILE) else INDEX_FILE
            with open(target_file, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(content)
            return

        elif self.path.startswith("/api/metrics/dashboard-summary"):
            data = compute_dashboard_summary()
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return

        elif self.path.startswith("/api/metrics/admin-wards"):
            events = get_current_active_events()
            data = compute_admin_ward_metrics(events)
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return

        elif self.path.startswith("/api/metrics/system-health"):
            data = SYSTEM_HEALTH_CACHE
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return

        elif self.path.startswith("/api/metrics/time-series"):
            events = get_current_active_events()
            data = compute_time_series_metrics(events)
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return

        elif self.path.startswith("/api/metrics/throughput"):
            events = get_current_active_events()
            data = compute_throughput_metrics(events)
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return

        elif self.path.startswith("/api/live-feed"):
            summary = compute_dashboard_summary()
            body = json.dumps({"status": "ok", "feed": summary["live_feed"]}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return

        elif self.path.startswith("/api/realtime-heatmap"):
            snapshot = get_serving_snapshot()
            events = snapshot["events"]

            ward_counts = {}
            citywide_count = 0
            for ev in events:
                loc = ev.get("location", {})
                w = loc.get("ward") or "Toàn thành phố (Chưa rõ phường/xã)"
                if loc.get("precision") == "city" or "Toàn thành phố" in w or "Đô thị trung tâm" in w or w == "TP.HCM":
                    citywide_count += 1
                else:
                    ward_counts[w] = ward_counts.get(w, 0) + 1

            payload = {
                "status": "success",
                "mode": snapshot["mode"],
                "window": snapshot["window"] or f"{GLOBAL_STATE['window_minutes']} phút",
                "total_events": len(events),
                "last_updated": snapshot["updated_at"],
                "served_from": snapshot["served_from"],
                "events": events,
                "ward_stats": ward_counts,
                "citywide_count": citywide_count
            }
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return

        elif self.path.startswith("/api/metrics"):
            # Endpoint quan sát (Observability Endpoint) theo chuẩn Phase 4
            r_client = get_redis_client()
            redis_online = r_client is not None
            cached_count = 0
            if r_client:
                try:
                    cached_count = r_client.zcard("flood:timeline:zset") or 0
                except Exception:
                    pass

            metrics = {
                "status": "healthy",
                "timestamp": int(time.time()),
                "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "mode": GLOBAL_STATE["mode"],
                "active_window": GLOBAL_STATE.get("active_window"),
                "current_events_count": len(GLOBAL_STATE.get("events", [])),
                "serving_store": {
                    "redis_available": redis_online,
                    "redis_host": REDIS_HOST,
                    "redis_port": REDIS_PORT,
                    "redis_cached_events": cached_count,
                    "fallback_file": "data/live_stream_state.json"
                },
                "veracity_status": {
                    "weather_checker_enabled": True,
                    "consensus_radius_m": 500,
                    "consensus_window_min": 60
                }
            }
            body = json.dumps(metrics, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return

        elif self.path.startswith("/api/csgt-hotspots"):
            csgt_file = os.path.join(ROOT_DIR, "data", "csgt_122_flood_hotspots.json")
            data = []
            if os.path.exists(csgt_file):
                try:
                    with open(csgt_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = []
            body = json.dumps({"status": "success", "count": len(data), "hotspots": data}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return

        elif self.path.startswith("/api/admin-units"):
            admin_file = os.path.join(ROOT_DIR, "data", "hcmc_168_administrative_units.json")
            data = []
            if os.path.exists(admin_file):
                try:
                    with open(admin_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = []
            body = json.dumps({"status": "success", "count": len(data), "units": data}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return

        elif self.path.startswith("/api/apify-pool/status") or self.path == "/api/apify-pool":
            from core.apify_pool import ApifyPoolManager
            pool_mgr = ApifyPoolManager.get_instance()
            data = pool_mgr.get_pool_status(mask_tokens=True)
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return

        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/reset-state":
            print("\n[API Reset] Nhận yêu cầu làm mới dòng sự kiện (Bắt đầu từ 0)...")
            GLOBAL_STATE["events"] = []
            GLOBAL_STATE["active_window"] = "Bắt đầu từ 0 (Chờ nạp...)"
            GLOBAL_STATE["last_updated"] = int(time.time())

            # 1. Dọn dẹp Redis nếu đang kết nối
            r_client = get_redis_client()
            if r_client:
                try:
                    event_keys = r_client.keys("flood:event:*")
                    if event_keys:
                        r_client.delete(*event_keys)
                    r_client.delete("flood:timeline:zset", "flood:geo:index", "flood:serving:mode")
                    r_client.set("flood:serving:window", "Bắt đầu từ 0 (Chờ nạp...)")
                    print("   ✓ Đã dọn sạch bộ nhớ đệm Redis Serving Store")
                except Exception as e:
                    print(f"   ! Lỗi dọn Redis: {e}")

            # 2. Dọn dẹp File đệm cục bộ
            stream_state_file = os.path.join(ROOT_DIR, "data", "live_stream_state.json")
            try:
                with open(stream_state_file, "w", encoding="utf-8") as sf:
                    json.dump({"mode": GLOBAL_STATE["mode"], "window": "Bắt đầu từ 0 (Chờ nạp...)", "events_count": 0, "events": []}, sf, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[API Reset] Lỗi: {e}")

            res = json.dumps({"status": "reset", "count": 0}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(res)
            return

        elif self.path == "/api/trigger-poll":
            print(f"\n[API Trigger] Nhận yêu cầu quét FREE mới ({GLOBAL_STATE['mode'].upper()}) từ giao diện...")
            events = []
            if GLOBAL_STATE["mode"] == "live":
                try:
                    free_crawler = LiveFreeSocialCrawler()
                    raw_events, stats = free_crawler.poll_live_stream(window_minutes=GLOBAL_STATE["window_minutes"])
                    print(f"   ✓ LiveFreeSocialCrawler quét được {len(raw_events)} sự kiện (Ưu tiên TikTok + Facebook).")
                    events = enrich_events_with_veracity(raw_events)
                    events.sort(key=lambda x: (
                        2 if x.get("freshness") == "strict_2h" else (1 if x.get("freshness") == "recent_4h" else 0),
                        1 if x.get("platform") in ["tiktok", "facebook"] else 0,
                        x.get("weight", 1.0),
                        x.get("create_time", 0)
                    ), reverse=True)
                    window_label = stats.get("active_window", f"{GLOBAL_STATE['window_minutes']} phút")
                    GLOBAL_STATE["events"] = events
                    GLOBAL_STATE["active_window"] = window_label
                    GLOBAL_STATE["last_updated"] = int(time.time())
                    sync_to_storage(events, "live", window_label)
                except Exception as e:
                    print(f"[API Trigger] Lỗi khi quét Live Free: {e}")
            else:
                poller = GLOBAL_STATE["poller"]
                if poller:
                    try:
                        raw_events, stats = poller.poll_simulation(window_minutes=GLOBAL_STATE["window_minutes"])
                        events = enrich_events_with_veracity(raw_events)
                        events.sort(key=lambda x: (
                            1 if x.get("platform") in ["tiktok", "facebook"] else 0,
                            x.get("weight", 1.0),
                            x.get("create_time", 0)
                        ), reverse=True)
                        window_label = stats.get("active_window", "Mô phỏng TP.HCM")
                        GLOBAL_STATE["events"] = events
                        GLOBAL_STATE["active_window"] = window_label
                        GLOBAL_STATE["last_updated"] = int(time.time())
                        sync_to_storage(events, "simulation", window_label)
                    except Exception as e:
                        print(f"[API Trigger] Lỗi khi quét Simulation: {e}")

            res = json.dumps({"status": "polled", "mode": GLOBAL_STATE["mode"], "count": len(GLOBAL_STATE["events"])}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(res)
            return

        elif self.path == "/api/trigger-apify":
            print(f"\n[API Apify] Nhận yêu cầu cào sâu Apify ({GLOBAL_STATE['mode'].upper()}) từ giao diện...")
            new_events = []
            poller = GLOBAL_STATE.get("poller")
            if poller:
                try:
                    if GLOBAL_STATE["mode"] == "live":
                        raw_events, stats = poller.poll_live(window_minutes=GLOBAL_STATE["window_minutes"])
                    else:
                        raw_events, stats = poller.poll_simulation(window_minutes=GLOBAL_STATE["window_minutes"])

                    if raw_events:
                        new_events = enrich_events_with_veracity(raw_events)
                        print(f"   ✓ [Apify Raw Ingestion] Nhận được {len(raw_events)} tin thô -> {len(new_events)} sự kiện sau bóc tách & xác thực (lọc <= 24h, 3 tầng độ tươi).")
                    else:
                        print("   ⚠️ [Apify Live] Không thu được tin mới từ đợt cào này (giữ nguyên sự kiện hiện có).")
                except Exception as e:
                    print(f"   ❌ [API Apify] Lỗi khi cào Apify: {e}")

            # HÒA TRỘN CỘNG DỒN CHỐNG RACE CONDITION (CUMULATIVE MERGE):
            # Truy vấn lại trạng thái sự kiện mới nhất ngay tại thời điểm hoàn thành cào Apify
            # để không bao giờ ghi đè hoặc quay lui (rollback) các tin do Freecrawl streaming vừa đẩy vào Redis
            fresh_storage_events = fetch_current_all_events()
            base_events = fresh_storage_events
            merged_events = merge_and_deduplicate_events(base_events, new_events)
            
            window_label = GLOBAL_STATE.get("active_window", "120 phút")
            if new_events:
                window_label = "Freecrawl + Apify Deep Crawl (24h)"

            GLOBAL_STATE["events"] = merged_events
            GLOBAL_STATE["active_window"] = window_label
            GLOBAL_STATE["last_updated"] = int(time.time())

            # Đồng bộ danh sách đã gộp vào Redis và file đệm
            sync_to_storage(merged_events, GLOBAL_STATE["mode"], window_label)
            print(f"   ✅ [Heatmap Updated] Tổng số sự kiện hiển thị trên bản đồ: {len(merged_events)} điểm ngập (gồm {len(base_events)} tin sẵn có + {len(new_events)} tin Apify mới).\n")

            res = json.dumps({"status": "apify_polled", "new_count": len(new_events), "total_count": len(merged_events)}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(res)
            return

        elif self.path == "/api/toggle-mode":
            new_mode = "live" if GLOBAL_STATE["mode"] == "simulation" else "simulation"
            GLOBAL_STATE["mode"] = new_mode
            print(f"\n[API Mode] Chuyển chế độ sang: {new_mode.upper()}...")
            events = []
            if new_mode == "live":
                try:
                    free_crawler = LiveFreeSocialCrawler()
                    raw_events, stats = free_crawler.poll_live_stream(window_minutes=GLOBAL_STATE["window_minutes"])
                    events = enrich_events_with_veracity(raw_events)
                    events.sort(key=lambda x: (
                        1 if x.get("platform") in ["tiktok", "facebook"] else 0,
                        x.get("weight", 1.0),
                        x.get("create_time", 0)
                    ), reverse=True)
                    window_label = stats.get("active_window", f"{GLOBAL_STATE['window_minutes']} phút")
                    GLOBAL_STATE["events"] = events
                    GLOBAL_STATE["active_window"] = window_label
                    GLOBAL_STATE["last_updated"] = int(time.time())
                    sync_to_storage(events, "live", window_label)
                except Exception as e:
                    print(f"[API Mode] Lỗi khi tải dữ liệu Live: {e}")
                    GLOBAL_STATE["events"] = []
                    GLOBAL_STATE["active_window"] = f"{GLOBAL_STATE['window_minutes'] // 60} giờ qua (0 sự kiện)"
            else:
                poller = GLOBAL_STATE["poller"]
                if poller:
                    try:
                        raw_events, stats = poller.poll_simulation(window_minutes=GLOBAL_STATE["window_minutes"])
                        events = enrich_events_with_veracity(raw_events)
                        events.sort(key=lambda x: (
                            1 if x.get("platform") in ["tiktok", "facebook"] else 0,
                            x.get("weight", 1.0),
                            x.get("create_time", 0)
                        ), reverse=True)
                        window_label = stats.get("active_window", "Mô phỏng TP.HCM")
                        GLOBAL_STATE["events"] = events
                        GLOBAL_STATE["active_window"] = window_label
                        GLOBAL_STATE["last_updated"] = int(time.time())
                        sync_to_storage(events, "simulation", window_label)
                    except Exception as e:
                        print(f"[API Mode] Lỗi khi tải dữ liệu Simulation: {e}")

            res = json.dumps({"status": "mode_changed", "mode": GLOBAL_STATE["mode"], "count": len(GLOBAL_STATE["events"])}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(res)
            return

        elif self.path.startswith("/api/apify-pool/"):
            action = self.path.replace("/api/apify-pool/", "").split("?")[0].strip().lower()
            from core.apify_pool import ApifyPoolManager
            pool_mgr = ApifyPoolManager.get_instance()

            payload = {}
            try:
                length = int(self.headers.get('Content-Length', 0))
                if length > 0:
                    raw_body = self.rfile.read(length).decode('utf-8')
                    payload = json.loads(raw_body)
            except Exception:
                payload = {}

            resp_data = {"status": "error", "message": "Yêu cầu không hợp lệ"}

            if action == "add":
                token = (payload.get("token") or "").strip()
                label = (payload.get("label") or "").strip()
                resp_data = pool_mgr.add_token(token, label=label, check_now=True)
            elif action in ["remove", "delete"]:
                tok_id = (payload.get("token_id") or payload.get("token") or "").strip()
                target_token = None
                for acc in pool_mgr.tokens:
                    t = acc.get("token", "")
                    if t == tok_id or (len(t) >= 14 and (t[:10] + t[-4:]) == tok_id):
                        target_token = t
                        break
                if target_token and pool_mgr.remove_token(target_token):
                    resp_data = {"status": "success", "message": "Đã xóa tài khoản khỏi Pool thành công", "pool": pool_mgr.get_pool_status()}
                else:
                    resp_data = {"status": "error", "message": "Không tìm thấy token trong Pool"}
            elif action == "set-active":
                tok_id = (payload.get("token_id") or payload.get("token") or "").strip()
                target_token = None
                for acc in pool_mgr.tokens:
                    t = acc.get("token", "")
                    if t == tok_id or (len(t) >= 14 and (t[:10] + t[-4:]) == tok_id):
                        target_token = t
                        break
                if target_token and pool_mgr.set_manual_active(target_token):
                    resp_data = {"status": "success", "message": "Đã ghim thủ công tài khoản thành công", "pool": pool_mgr.get_pool_status()}
                else:
                    resp_data = {"status": "error", "message": "Không tìm thấy token cần ghim"}
            elif action == "rotate":
                new_tok, msg = pool_mgr.rotate_next(reason="admin_manual_rotate")
                resp_data = {"status": "success", "message": msg, "pool": pool_mgr.get_pool_status()}
            elif action == "toggle-mode":
                new_mode = payload.get("mode")
                if not new_mode:
                    new_mode = "manual" if pool_mgr.mode == "auto" else "auto"
                pool_mgr.set_mode(new_mode)
                resp_data = {"status": "success", "mode": pool_mgr.mode, "pool": pool_mgr.get_pool_status()}
            elif action == "refresh":
                pool_data = pool_mgr.refresh_all(timeout_sec=3.5)
                resp_data = {"status": "success", "message": "Đã cập nhật số dư tất cả tài khoản", "pool": pool_data}

            res = json.dumps(resp_data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(res)
            return

        self.send_error(404, "Endpoint not found")


def start_server(port: int = DEFAULT_PORT, mode: str = "live", apify_token: str = None, window_minutes: int = DEFAULT_WINDOW_MINUTES, clean_start: bool = False):
    GLOBAL_STATE["mode"] = mode
    GLOBAL_STATE["window_minutes"] = window_minutes
    from core.apify_pool import ApifyPoolManager
    pool_mgr = ApifyPoolManager.get_instance()
    token = apify_token or pool_mgr.get_active_token()
    poller = MultiPlatformPoller(apify_token=token)
    GLOBAL_STATE["poller"] = poller
    fb_strategy = os.environ.get("FB_CRAWL_STRATEGY", FB_CRAWL_STRATEGY)

    # Khởi tạo trạng thái ban đầu
    stream_state_file = os.path.join(ROOT_DIR, "data", "live_stream_state.json")
    if os.path.exists(stream_state_file):
        try:
            with open(stream_state_file, "r", encoding="utf-8") as sf:
                st_data = json.load(sf)
                if st_data.get("events"):
                    GLOBAL_STATE["events"] = st_data["events"]
                    GLOBAL_STATE["active_window"] = st_data.get("window", "120 phút (Mô phỏng TP.HCM)")
                    GLOBAL_STATE["last_updated"] = int(time.time())
                    print(f"   ✓ [Heatmap Ready] Đã nạp sẵn {len(st_data['events'])} sự kiện lên bản đồ ngay khi mở web.")
        except Exception:
            pass
    if not GLOBAL_STATE.get("events"):
        GLOBAL_STATE["events"] = []
        GLOBAL_STATE["active_window"] = "120 phút"
        GLOBAL_STATE["last_updated"] = int(time.time())

    print(f"\n=======================================================")
    print(f"[SE363] HỆ THỐNG CẢNH BÁO NGẬP LỤT ĐA NỀN TẢNG (TIKTOK + FACEBOOK)")
    print(f"        Chế độ (Mode): {mode.upper()}")
    print(f"        Cửa sổ lọc (Window): {window_minutes // 60} giờ ({window_minutes} phút)")
    print(f"        Chiến lược Facebook: {fb_strategy.upper()} (Chuyên sâu TP.HCM)")
    print(f"        Xác thực tin giả (Veracity): BẬT (Khung 60p, Trạm khí tượng Open-Meteo)")
    print(f"        Serving Store: Redis ({'Sẵn sàng' if REDIS_AVAILABLE else 'Chưa có'}) + Local File Fallback")
    print(f"        Apify Token: {token[:15]}...")
    print(f"=======================================================")

    def run_initial_ingest():
        if clean_start:
            return
        if mode == "live":
            print(f"[Worker] Đang thu thập dữ liệu gần thời gian thực từ TikTok & Facebook (Ưu tiên MXH)...")
            try:
                free_crawler = LiveFreeSocialCrawler()
                raw_events, stats = free_crawler.poll_live_stream(window_minutes=window_minutes)
            except Exception as e:
                print(f"[Worker] Lỗi cào trực tiếp: {e}")
                raw_events = []
                stats = {
                    "mode": "live",
                    "total_events": 0,
                    "active_window": f"{window_minutes // 60} giờ qua (0 sự kiện)"
                }
        else:
            print(f"[Worker] Đang mô phỏng dòng dữ liệu trôi động đa nền tảng...")
            raw_events, stats = poller.poll_simulation(window_minutes=window_minutes, batch_size=15)

        events = enrich_events_with_veracity(raw_events)
        events.sort(key=lambda x: (
            1 if x.get("platform") in ["tiktok", "facebook"] else 0,
            x.get("weight", 1.0),
            x.get("create_time", 0)
        ), reverse=True)
        GLOBAL_STATE["events"] = events
        GLOBAL_STATE["active_window"] = stats.get("active_window", f"{window_minutes // 60} giờ qua")
        GLOBAL_STATE["last_updated"] = int(time.time())
        sync_to_storage(events, mode, GLOBAL_STATE["active_window"])

        print(f"\n[Worker] Đã nạp thành công {len(events)} sự kiện ngập lụt lên bản đồ (Cửa sổ: {GLOBAL_STATE['active_window']}):")
        for ev in events[:6]:
            loc = ev.get("location", {})
            v = ev.get("veracity", {})
            print(f"   * [{ev.get('platform', '').upper()}] {loc.get('street', '')} ({loc.get('ward', '')}) -> {ev.get('opinion', '')} | {v.get('status_label', '')} ({int(v.get('confidence_score', 0)*100)}%)")

    ingest_thread = threading.Thread(target=run_initial_ingest, daemon=True)
    ingest_thread.start()

    server_address = ("127.0.0.1", port)
    socketserver.TCPServer.allow_reuse_address = True
    try:
        httpd = socketserver.ThreadingTCPServer(server_address, HeatmapRequestHandler)
    except OSError as err:
        print(f"\n[Cảnh báo] Cổng {port} đang bận ({err}). Đang tự động thử lại sau 1.5 giây...")
        time.sleep(1.5)
        httpd = socketserver.ThreadingTCPServer(server_address, HeatmapRequestHandler)

    with httpd:
        start_background_health_worker()
        print(f"\n>> Bản đồ nhiệt đang hoạt động tại: http://localhost:{port}")
        print(f"   (Mở trình duyệt vào địa chỉ trên để xem)")
        print(f"   (Nhấn Ctrl+C trong terminal để dừng server)\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Server] Đang tắt máy chủ...")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="SE363 - Máy chủ Web Bản đồ Nhiệt Cảnh báo Ngập lụt (Heatmap Dashboard)"
    )
    parser.add_argument(
        "--mode",
        choices=["simulation", "live"],
        default="live",
        help="Chế độ chạy: 'live' (mặc định) hoặc 'simulation'"
    )
    parser.add_argument(
        "--window",
        type=int,
        default=DEFAULT_WINDOW_MINUTES,
        help="Cửa sổ thời gian lọc dữ liệu (phút) - Mặc định: 120 phút (2 giờ)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Cổng mở giao diện Web (Mặc định: 8050)"
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="Apify API Token (Mặc định tự động lấy từ core/config.py)"
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        default=True,
        help="Tự động làm sạch cache khi khởi động để nạp từ từ từ 0 (Mặc định: BẬT)"
    )
    parser.add_argument(
        "--no-clean",
        dest="clean",
        action="store_false",
        help="Giữ lại snapshot cũ từ lần chạy trước"
    )

    args = parser.parse_args()
    start_server(port=args.port, mode=args.mode, apify_token=args.token, window_minutes=args.window, clean_start=args.clean)
