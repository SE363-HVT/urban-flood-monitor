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
import os
import sys
import time
import socket
import threading
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
from pipeline.veracity_checker import VeracityChecker
from pipeline.spatio_temporal_clusterer import SpatioTemporalClusterer
from pipeline.event_processor import format_relative_time
from core.config import APIFY_TOKEN, DEFAULT_PORT, DEFAULT_WINDOW_MINUTES, FB_CRAWL_STRATEGY

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(DASHBOARD_DIR, "index.html")

# Khởi tạo bộ kiểm tra độ tin cậy dữ liệu (cửa sổ trượt 60 phút, bán kính 500m)
VERACITY_CHECKER = VeracityChecker(window_minutes=60, radius_meters=500.0, enable_weather_check=True)
CLUSTERER = SpatioTemporalClusterer(radius_meters=400.0, time_window_seconds=2700)

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
    """Lấy danh sách tất cả sự kiện hiện có từ Redis hoặc buffer file hoặc memory."""
    r_client = get_redis_client()
    if r_client:
        r_events = fetch_events_from_redis(r_client)
        if r_events:
            return r_events
    stream_state_file = os.path.join(ROOT_DIR, "data", "live_stream_state.json")
    if os.path.exists(stream_state_file):
        try:
            with open(stream_state_file, "r", encoding="utf-8") as sf:
                data = json.load(sf)
                if data.get("events"):
                    return data["events"]
        except Exception:
            pass
    return list(GLOBAL_STATE.get("events", []))


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
    combined.sort(key=lambda x: (
        2 if x.get("freshness") == "strict_2h" or (current_time - x.get("create_time", 0)) <= 7200 else (
            1 if x.get("freshness") == "recent_4h" or (current_time - x.get("create_time", 0)) <= 14400 else 0
        ),
        1 if x.get("platform") in ["tiktok", "facebook"] else 0,
        x.get("weight", 1.0),
        x.get("create_time", 0)
    ), reverse=True)

    return combined

def sync_to_storage(events: List[Dict[str, Any]], mode: str, window_label: str):
    """Ghi đồng bộ tức thì vào Redis In-Memory Store (<3ms) và file JSON fallback."""
    r_client = get_redis_client()
    if r_client:
        try:
            pipe = r_client.pipeline()
            event_keys = r_client.keys("flood:event:*")
            if event_keys:
                pipe.delete(*event_keys)
            pipe.delete("flood:timeline:zset", "flood:geo:index")

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
        temp_file = f"{stream_state_file}.tmp"
        with open(temp_file, "w", encoding="utf-8") as sf:
            json.dump(out_data, sf, ensure_ascii=False, indent=2)
        os.replace(temp_file, stream_state_file)
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

        elif self.path.startswith("/api/realtime-heatmap"):
            events = GLOBAL_STATE.get("events", [])
            served_from = "memory"

            # 1. ƯU TIÊN 1: In-Memory Redis Hot Serving Store (< 3ms)
            r_client = get_redis_client()
            if r_client:
                redis_events = fetch_events_from_redis(r_client)
                if redis_events:
                    events = redis_events
                    served_from = "redis"
                    r_mode = r_client.get("flood:serving:mode")
                    if r_mode:
                        GLOBAL_STATE["mode"] = r_mode
                    r_window = r_client.get("flood:serving:window")
                    if r_window:
                        GLOBAL_STATE["active_window"] = r_window
                    GLOBAL_STATE["last_updated"] = int(time.time())

            # 2. ƯU TIÊN 2 (FALLBACK): Đọc file live_stream_state.json nếu Redis chưa có hoặc offline
            if served_from != "redis":
                stream_state_file = os.path.join(ROOT_DIR, "data", "live_stream_state.json")
                if os.path.exists(stream_state_file):
                    try:
                        with open(stream_state_file, "r", encoding="utf-8") as sf:
                            st_data = json.load(sf)
                            if st_data.get("events") is not None:
                                events = st_data.get("events", [])
                                if st_data.get("mode"):
                                    GLOBAL_STATE["mode"] = st_data["mode"]
                                if st_data.get("window"):
                                    GLOBAL_STATE["active_window"] = st_data["window"]
                                GLOBAL_STATE["last_updated"] = int(time.time())
                                served_from = "local_file_buffer"
                    except Exception:
                        pass

            ward_counts = {}
            citywide_count = 0
            for ev in events:
                loc = ev.get("location", {})
                w = loc.get("ward") or "Toàn thành phố (Chưa rõ phường/xã)"
                if "Toàn thành phố" in w or "Đô thị trung tâm" in w or w == "TP.HCM":
                    citywide_count += 1
                else:
                    ward_counts[w] = ward_counts.get(w, 0) + 1

            payload = {
                "status": "success",
                "mode": GLOBAL_STATE["mode"],
                "window": GLOBAL_STATE.get("active_window", f"{GLOBAL_STATE['window_minutes']} phút"),
                "total_events": len(events),
                "last_updated": GLOBAL_STATE["last_updated"],
                "served_from": served_from,
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
            base_events = merge_and_deduplicate_events(GLOBAL_STATE.get("events", []), fresh_storage_events)
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

        self.send_error(404, "Endpoint not found")


def start_server(port: int = DEFAULT_PORT, mode: str = "live", apify_token: str = None, window_minutes: int = DEFAULT_WINDOW_MINUTES, clean_start: bool = False):
    GLOBAL_STATE["mode"] = mode
    GLOBAL_STATE["window_minutes"] = window_minutes
    token = apify_token or APIFY_TOKEN
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
