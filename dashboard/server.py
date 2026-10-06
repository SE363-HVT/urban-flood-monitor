"""
dashboard/server.py - Máy chủ Web phục vụ Bản Đồ Nhiệt Cảnh Báo Ngập Lụt Đa Nền Tảng (Port 8050)
Cung cấp giao diện trực quan và REST API: /api/realtime-heatmap, /api/trigger-poll, /api/toggle-mode.
Tích hợp thu thập Video TikTok + Bài đăng Facebook.
Tích hợp Module Xác thực dữ liệu & Phòng chống tin giả (VeracityChecker).
"""

import http.server
import socketserver
import json
import os
import sys
import time
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
    "active_window": "2 giờ qua",
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
            payload = {
                "status": "success",
                "mode": GLOBAL_STATE["mode"],
                "window": GLOBAL_STATE.get("active_window", f"{GLOBAL_STATE['window_minutes']} phút"),
                "total_events": len(GLOBAL_STATE["events"]),
                "last_updated": GLOBAL_STATE["last_updated"],
                "events": GLOBAL_STATE["events"]
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
    print(f"        Chiến lược Facebook: {fb_strategy.upper()} (Search PPR Chống Checkpoint)")
    print(f"        Xác thực tin giả (Veracity): BẬT (Khung 60p, Trạm khí tượng Open-Meteo)")
    print(f"        Apify Token: {token[:15]}...")
    print(f"=======================================================")

    if mode == "live":
        print(f"[Worker] Đang thu thập dữ liệu gần thời gian thực từ TikTok & Facebook...")
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

    print(f"[Worker] Đã nạp {len(events)} sự kiện ngập lụt lên bản đồ (Cửa sổ: {GLOBAL_STATE['active_window']}):")
    for ev in events[:6]:
        loc = ev["location"]
        v = ev.get("veracity", {})
        print(f"   * [{ev['platform'].upper()}] {loc['street']} ({loc['ward']}) -> {ev['opinion']} | {v.get('status_label', '')} ({int(v.get('confidence_score', 0)*100)}%)")

    server_address = ("", port)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(server_address, HeatmapRequestHandler) as httpd:
        print(f"\n>> Bản đồ nhiệt đang chạy tại: http://localhost:{port}")
        print(f"   (Mở trình duyệt vào địa chỉ trên để xem)")
        print(f"   (Nhấn Ctrl+C trong terminal để dừng server)\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Server] Đang tắt máy chủ...")

if __name__ == "__main__":
    start_server()
