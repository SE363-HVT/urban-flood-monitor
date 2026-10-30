# -*- coding: utf-8 -*-
"""
pipeline/tiktok_poller.py - Module Thu Thập Dữ Liệu Video TikTok Đô Thị
Thuần túy phục vụ Video bài đăng (đã loại bỏ hoàn toàn các chức năng Livestream/Live Chat).
Hỗ trợ:
- Live Mode: Gọi trực tiếp Apify REST API với bộ Hashtag + Query tiếng Việt tối ưu cho Video ngập lụt.
  Cơ chế Smart Adaptive Window: Ưu tiên cửa sổ 2 giờ; nếu thời điểm demo trời tạnh ráo,
  tự động mở rộng hiển thị đợt mưa bão gần nhất (24h - 72h) kèm mốc thời gian minh bạch.
- Simulation Mode: Phát lại dòng dữ liệu trôi động (Sliding Stream) video ngập lụt từ dataset
  đã làm sạch: data/processed/hcmc_flood_annotated_v1.json (100% trong TP.HCM).
"""

import json
import os
import time
import requests
from typing import List, Dict, Any, Optional, Tuple

from core.state_manager import StateManager
from core.config import APIFY_TOKEN, ACTOR_ID, DEFAULT_SEARCH_QUERIES, DEFAULT_HASHTAGS, DEFAULT_WINDOW_MINUTES
from pipeline.event_processor import process_tiktok_item
from pipeline.simulation_replayer import SimulationReplayer

DEFAULT_RAW_FILE = os.path.join("data", "raw", "dataset_tiktok-scraper-urban_2026-09-29_10-39-28-832.json")
LAST_CRAWL_DEBUG_FILE = os.path.join("data", "last_crawled_tiktok.json")

class TikTokPoller:
    _sim_offset: int = 0
    _cached_sim_events: Optional[List[Dict[str, Any]]] = None

    def __init__(self, apify_token: Optional[str] = None, state_manager: Optional[StateManager] = None):
        self.apify_token = apify_token or APIFY_TOKEN
        self.state_manager = state_manager or StateManager()

    def poll_live_apify(
        self,
        hashtags: Optional[List[str]] = None,
        search_queries: Optional[List[str]] = None,
        max_items: int = 35,
        window_minutes: int = DEFAULT_WINDOW_MINUTES
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Cào TikTok thật bằng cơ chế Video Search Queries + Hashtags bản địa:
        - Bỏ hoàn toàn các từ khóa livestream gây sai lệch chủ đề.
        - Thu thập và xử lý video về ngập lụt, mưa lớn, triều cường tại TP.HCM.
        """
        if not self.apify_token:
            raise ValueError("Chưa cấu hình APIFY_TOKEN. Vui lòng cung cấp token trong core/config.py.")

        target_hashtags = hashtags or DEFAULT_HASHTAGS
        target_queries = search_queries or DEFAULT_SEARCH_QUERIES

        print(f"\n[Apify Live] Đang gửi yêu cầu cào Video TikTok (Hybrid: Search Queries + Hashtags)...")
        print(f"[Apify Live] Từ khóa điểm nóng TP.HCM ({len(target_queries)} queries): {target_queries[:4]}...")
        print(f"[Apify Live] Danh sách Hashtags ({len(target_hashtags)} tags): {target_hashtags[:4]}...")

        url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={self.apify_token}"
        run_input = {
            "searchQueries": target_queries[:5],
            "hashtags": target_hashtags[:4],
            "resultsPerPage": 5,
            "maxItems": max_items,
        }

        # 1. Khởi chạy Actor
        resp = requests.post(url, json=run_input, timeout=30)
        resp.raise_for_status()
        run_data = resp.json().get("data", {})
        run_id = run_data.get("id")
        dataset_id = run_data.get("defaultDatasetId")
        
        print(f"[Apify Live] Actor đang chạy (Run ID: {run_id}). Đang chờ kết quả...")

        # 2. Chờ Actor hoàn thành
        poll_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={self.apify_token}"
        status = "RUNNING"
        for _ in range(50):
            time.sleep(2.5)
            try:
                status_resp = requests.get(poll_url, timeout=10).json().get("data", {})
                status = status_resp.get("status")
                if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                    break
            except Exception:
                pass
        
        if status != "SUCCEEDED":
            raise RuntimeError(f"Actor Apify kết thúc với trạng thái: {status}")

        # 3. Lấy dữ liệu từ Dataset
        items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={self.apify_token}"
        items_resp = requests.get(items_url, timeout=30)
        items_resp.raise_for_status()
        raw_items = items_resp.json()

        # Lưu bản sao raw debug
        os.makedirs("data", exist_ok=True)
        try:
            with open(LAST_CRAWL_DEBUG_FILE, "w", encoding="utf-8") as f:
                json.dump(raw_items, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        print(f"[Apify Live] Cào thành công! Nhận được {len(raw_items)} bài đăng từ TikTok.")

        # 4. Xử lý & Phân tầng thời gian thông minh (Smart Adaptive Window)
        current_time = int(time.time())
        cutoff_window = current_time - (window_minutes * 60)  # Cửa sổ chính (e.g. 120 phút = 2 giờ)
        cutoff_24h = current_time - 86400                    # 24 giờ qua
        cutoff_72h = current_time - 259200                   # 72 giờ qua (3 ngày)

        events_window = []
        events_24h = []
        events_72h = []
        events_all_matched = []

        seen_ids = set()

        for raw in raw_items:
            vid_id = str(raw.get("id"))
            if vid_id in seen_ids:
                continue
            seen_ids.add(vid_id)

            c_time = raw.get("createTime", 0)
            event = process_tiktok_item(raw, reference_time=current_time)
            if not event:
                continue

            events_all_matched.append(event)
            if c_time >= cutoff_window:
                events_window.append(event)
                self.state_manager.mark_seen(vid_id, c_time)
            elif c_time >= cutoff_24h:
                events_24h.append(event)
            elif c_time >= cutoff_72h:
                events_72h.append(event)

        self.state_manager.save()

        display_events = events_window
        win_label = f"{window_minutes // 60} giờ qua" if (window_minutes >= 60 and window_minutes % 60 == 0) else f"{window_minutes} phút"
        if not display_events:
            win_label = f"{win_label} (Không có ngập mới)"

        # Sắp xếp theo mức độ nghiêm trọng và thời gian mới nhất
        display_events.sort(key=lambda x: (x.get("weight", 1.0), x.get("create_time", 0)), reverse=True)

        stats = {
            "mode": "live",
            "current_time": current_time,
            "total_crawled": len(raw_items),
            "events_window": len(events_window),
            "total_events_displayed": len(display_events),
            "videos_count": len(display_events),
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
        Phát lại dòng dữ liệu mô phỏng từ dataset tĩnh đã làm sạch:
        data/processed/hcmc_flood_annotated_v1.json (100% trong TP.HCM).
        """
        replayer = SimulationReplayer.get_instance()
        return replayer.poll(batch_size=batch_size, platform_filter="tiktok")
