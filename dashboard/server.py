# -*- coding: utf-8 -*-
"""
dashboard/server.py - Máy chủ Web phục vụ Bản Đồ Nhiệt Cảnh Báo Ngập Lụt Đa Nền Tảng (Port 8050)
Cung cấp giao diện trực quan và REST API: /api/realtime-heatmap, /api/trigger-poll, /api/toggle-mode.
Tích hợp thu thập Video TikTok + Bài đăng Facebook.
Tích hợp Module Xác thực dữ liệu & Phòng chống tin giả (VeracityChecker).
Tích hợp Cầu nối PySpark Streaming (Hot State Bridge từ live_stream_state.json).
"""

import http.server
import socketserver
import json
import os
import sys
import time
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

from pipeline.multi_poller import MultiPlatformPoller
from pipeline.veracity_checker import VeracityChecker
from core.config import APIFY_TOKEN, DEFAULT_PORT, DEFAULT_WINDOW_MINUTES, FB_CRAWL_STRATEGY

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(DASHBOARD_DIR, "index.html")

# Khởi tạo bộ kiểm tra độ tin cậy dữ liệu (cửa sổ trượt 60 phút, bán kính 500m)
VERACITY_CHECKER = VeracityChecker(window_minutes=60, radius_meters=500.0, enable_weather_check=True)

GLOBAL_STATE = {
    "mode": "live",
    "window_minutes": DEFAULT_WINDOW_MINUTES,
    "active_window": "Đang kết nối dữ liệu...",
    "events": [],
    "last_updated": None,
    "poller": None
}

def enrich_events_with_veracity(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Gắn thông tin xác thực dữ liệu, đối soát thời tiết và đồng thuận 60 phút vào từng sự kiện."""
    enriched = []
    for ev in events:
        loc = ev.get("location", {})
        ev["lat"] = loc.get("lat")
        ev["lon"] = loc.get("lon")
        ev["timestamp"] = ev.get("create_time") or int(time.time())
        verified = VERACITY_CHECKER.verify_event(ev, reference_time=ev.get("create_time"))
        enriched.append(verified)
    return enriched

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
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(content)
            return

        elif self.path.startswith("/api/realtime-heatmap"):
            events = GLOBAL_STATE.get("events", [])

            # CẦU NỐI PYSPARK STREAMING: Ưu tiên dữ liệu nóng từ Spark nếu có
            stream_state_file = os.path.join(ROOT_DIR, "data", "live_stream_state.json")
            if os.path.exists(stream_state_file):
                try:
                    with open(stream_state_file, "r", encoding="utf-8") as sf:
                        st_data = json.load(sf)
                        if st_data.get("events"):
                            events = st_data["events"]
                            if st_data.get("mode"):
                                GLOBAL_STATE["mode"] = st_data["mode"]
                            if st_data.get("window"):
                                GLOBAL_STATE["active_window"] = st_data["window"]
                            GLOBAL_STATE["last_updated"] = int(time.time())
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
                "events": events,
                "ward_stats": ward_counts,
                "citywide_count": citywide_count
            }
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

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
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return

        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/trigger-poll":
            print(f"\n[API Trigger] Nhận yêu cầu quét mới ({GLOBAL_STATE['mode'].upper()}) từ giao diện...")
            poller = GLOBAL_STATE["poller"]
            if poller:
                try:
                    if GLOBAL_STATE["mode"] == "live":
                        raw_events, stats = poller.poll_live(window_minutes=GLOBAL_STATE["window_minutes"])
                    else:
                        raw_events, stats = poller.poll_simulation(window_minutes=GLOBAL_STATE["window_minutes"])
                    
                    events = enrich_events_with_veracity(raw_events)
                    GLOBAL_STATE["events"] = events
                    GLOBAL_STATE["active_window"] = stats.get("active_window", "2 giờ qua")
                    GLOBAL_STATE["last_updated"] = int(time.time())
                    print(f"[API Trigger] Quét hoàn tất! Có {len(events)} sự kiện ngập. Cửa sổ: {GLOBAL_STATE['active_window']}")
                except Exception as e:
                    print(f"[API Trigger] Lỗi khi quét: {e}")
                    if GLOBAL_STATE["mode"] == "live":
                        GLOBAL_STATE["events"] = []
                        GLOBAL_STATE["active_window"] = f"{GLOBAL_STATE['window_minutes'] // 60} giờ qua (0 sự kiện)"

            res = json.dumps({"status": "polled", "mode": GLOBAL_STATE["mode"], "count": len(GLOBAL_STATE["events"])}).encode("utf-8")
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
            poller = GLOBAL_STATE["poller"]
            if poller:
                try:
                    if new_mode == "live":
                        raw_events, stats = poller.poll_live(window_minutes=GLOBAL_STATE["window_minutes"])
                    else:
                        raw_events, stats = poller.poll_simulation(window_minutes=GLOBAL_STATE["window_minutes"])
                    
                    events = enrich_events_with_veracity(raw_events)
                    GLOBAL_STATE["events"] = events
                    GLOBAL_STATE["active_window"] = stats.get("active_window", "2 giờ qua")
                    GLOBAL_STATE["last_updated"] = int(time.time())
                    print(f"[API Mode] Đã tải dữ liệu chế độ {new_mode.upper()}: {len(events)} sự kiện (đã xác thực).")
                except Exception as e:
                    print(f"[API Mode] Lỗi khi chuyển chế độ: {e}")
                    if new_mode == "live":
                        GLOBAL_STATE["events"] = []
                        GLOBAL_STATE["active_window"] = f"{GLOBAL_STATE['window_minutes'] // 60} giờ qua (0 sự kiện)"

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

def start_server(port: int = DEFAULT_PORT, mode: str = "live", apify_token: str = None, window_minutes: int = DEFAULT_WINDOW_MINUTES):
    GLOBAL_STATE["mode"] = mode
    GLOBAL_STATE["window_minutes"] = window_minutes
    token = apify_token or APIFY_TOKEN
    poller = MultiPlatformPoller(apify_token=token)
    GLOBAL_STATE["poller"] = poller
    fb_strategy = os.environ.get("FB_CRAWL_STRATEGY", FB_CRAWL_STRATEGY)

    print(f"\n=======================================================")
    print(f"[SE363] HỆ THỐNG CẢNH BÁO NGẬP LỤT ĐA NỀN TẢNG (TIKTOK + FACEBOOK)")
    print(f"        Chế độ (Mode): {mode.upper()}")
    print(f"        Cửa sổ lọc (Window): {window_minutes // 60} giờ ({window_minutes} phút)")
    print(f"        Chiến lược Facebook: {fb_strategy.upper()} (Chuyên sâu TP.HCM)")
    print(f"        Xác thực tin giả (Veracity): BẬT (Khung 60p, Trạm khí tượng Open-Meteo)")
    print(f"        Apify Token: {token[:15]}...")
    print(f"=======================================================")

    def run_initial_ingest():
        if mode == "live":
            print(f"[Worker] Đang thu thập dữ liệu gần thời gian thực từ TikTok & Facebook qua Apify...")
            try:
                raw_events, stats = poller.poll_live(window_minutes=window_minutes)
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
        GLOBAL_STATE["events"] = events
        GLOBAL_STATE["active_window"] = stats.get("active_window", f"{window_minutes // 60} giờ qua")
        GLOBAL_STATE["last_updated"] = int(time.time())

        print(f"\n[Worker] Đã nạp thành công {len(events)} sự kiện ngập lụt lên bản đồ (Cửa sổ: {GLOBAL_STATE['active_window']}):")
        for ev in events[:6]:
            loc = ev.get("location", {})
            v = ev.get("veracity", {})
            print(f"   * [{ev.get('platform', '').upper()}] {loc.get('street', '')} ({loc.get('ward', '')}) -> {ev.get('opinion', '')} | {v.get('status_label', '')} ({int(v.get('confidence_score', 0)*100)}%)")

    # Khởi động luồng thu thập dữ liệu ngầm để Web Server phản hồi ngay lập tức (không chặn cổng 8050)
    ingest_thread = threading.Thread(target=run_initial_ingest, daemon=True)
    ingest_thread.start()

    server_address = ("", port)
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

    args = parser.parse_args()
    start_server(port=args.port, mode=args.mode, apify_token=args.token, window_minutes=args.window)
