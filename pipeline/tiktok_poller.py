# -*- coding: utf-8 -*-
"""
pipeline/tiktok_poller.py - Thu thập dữ liệu video TikTok thời gian thực
Hỗ trợ cả chế độ:
- LIVE: Cào TikTok thật bằng cơ chế Video Search Queries + Hashtags bản địa qua Apify.
        Tích hợp Smart Key Rotation qua ApifyPoolManager.
        Tối ưu số lượng truy vấn để cào nhanh (~60-90s), tránh nguy cơ timeout 300s.
- SIMULATION: Phát lại dữ liệu mô phỏng từ file dataset sạch (100% TP.HCM).
"""

import os
import json
import time
import requests
from typing import List, Dict, Any, Tuple, Optional

from core.config import APIFY_TOKEN, ACTOR_ID, DEFAULT_HASHTAGS, DEFAULT_SEARCH_QUERIES, DEFAULT_WINDOW_MINUTES
from pipeline.event_processor import process_tiktok_item
from pipeline.simulation_replayer import SimulationReplayer
from core.state_manager import StateManager

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
        max_items: int = 50,
        window_minutes: int = DEFAULT_WINDOW_MINUTES
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Cào TikTok thật bằng cơ chế Video Search Queries + Hashtags bản địa:
        - Tự động lấy active token từ ApifyPoolManager (với cơ chế Failover khi hết hạn mức).
        - Tối ưu 3 câu query trọng điểm + 3 hashtag thịnh hành (hoàn thành ~60-90s, an toàn dưới timeout 300s).
        - Thu thập và xử lý video về ngập lụt, mưa lớn, triều cường tại TP.HCM.
        """
        pool_mgr = None
        try:
            from core.apify_pool import ApifyPoolManager, mask_token
            pool_mgr = ApifyPoolManager.get_instance()
        except Exception:
            pool_mgr = None

        target_hashtags = hashtags or DEFAULT_HASHTAGS
        target_queries = search_queries or DEFAULT_SEARCH_QUERIES

        run_input = {
            "searchQueries": target_queries,
            "hashtags": target_hashtags,
            "resultsPerPage": 15,
            "maxItems": max_items,
        }

        # Vòng lặp Failover thông minh: Tự động đổi key và thử lại nếu gặp HTTP 401 hoặc 402 ($5 Quota Exceeded)
        max_attempts = 3
        raw_items = []
        for attempt in range(max_attempts):
            active_token = pool_mgr.get_active_token() if pool_mgr else (self.apify_token or APIFY_TOKEN)
            if not active_token:
                raise ValueError("Chưa cấu hình APIFY_TOKEN. Vui lòng cung cấp token trong core/config.py hoặc Apify Pool.")

            masked_disp = active_token[:12] + "..." + active_token[-4:] if len(active_token) >= 16 else active_token
            print(f"\n[Apify Live] Đang gửi yêu cầu cào Video TikTok qua Apify Key ({masked_disp}) [Lần thử {attempt + 1}/{max_attempts}]...")
            if attempt == 0:
                print(f"[Apify Live] Từ khóa điểm nóng TP.HCM ({len(target_queries)} queries): {target_queries}...")
                print(f"[Apify Live] Danh sách Hashtags ({len(target_hashtags)} tags): {target_hashtags}...")

            url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={active_token}"

            try:
                resp = requests.post(url, json=run_input, timeout=30)
                if resp.status_code == 429:
                    print("[Apify Live] ⚠️ Apify TikTok Actor đạt giới hạn tần suất (Rate Limit). Bỏ qua TikTok đợt này.")
                    return [], {"status": "rate_limited", "tiktok_count": 0}
                if resp.status_code in [401, 402]:
                    err_label = "Hết hạn mức $5 (HTTP 402 Quota Exceeded)" if resp.status_code == 402 else "Token không hợp lệ (HTTP 401)"
                    print(f"[Apify Live] ⚠️ Key ({masked_disp}) gặp lỗi: {err_label}!")
                    if pool_mgr:
                        pool_mgr.mark_exhausted(active_token, reason=err_label)
                        if attempt < max_attempts - 1:
                            print(f"[Apify Live] 🔄 Tự động Failover: Đã đánh dấu EXHAUSTED và xoay sang Key kế tiếp trong Pool để thử lại cào ngay...")
                            time.sleep(1.0)
                            continue
                    return [], {"status": "exhausted", "error": err_label, "tiktok_count": 0}

                resp.raise_for_status()
                run_data = resp.json().get("data", {})
                run_id = run_data.get("id")
                dataset_id = run_data.get("defaultDatasetId")
                
                print(f"[Apify Live] Actor đang chạy (Run ID: {run_id}). Đang chờ kết quả...")

                # 2. Chờ Actor hoàn thành (tối đa 360 giây)
                poll_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={active_token}"
                status = "RUNNING"
                for _ in range(180):
                    time.sleep(2.0)
                    try:
                        status_resp = requests.get(poll_url, timeout=10).json().get("data", {})
                        status = status_resp.get("status")
                        if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                            break
                    except Exception:
                        pass
                
                if status != "SUCCEEDED":
                    print(f"[Apify Live] ⚠️ TikTok Actor dừng với trạng thái: {status}.")
                    return [], {"status": status, "tiktok_count": 0}

                # 3. Lấy dữ liệu từ Dataset
                items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={active_token}"
                items_resp = requests.get(items_url, timeout=30)
                items_resp.raise_for_status()
                raw_items = items_resp.json()
                break  # Hoàn thành xuất sắc, thoát khỏi vòng lặp thử lại!
            except Exception as e:
                print(f"[Apify Live] ⚠️ Lỗi kết nối cào TikTok qua Apify: {e}")
                if attempt < max_attempts - 1 and pool_mgr:
                    print(f"[Apify Live] 🔄 Tự động thử lại với Key khác trong Pool...")
                    pool_mgr.rotate_next(reason="network_retry")
                    time.sleep(1.0)
                    continue
                return [], {"status": "error", "tiktok_count": 0}

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
            age_seconds = max(0, current_time - c_time)
            if age_seconds <= 7200:
                event["freshness"] = "strict_2h"
                event["status_tag"] = "🔴 ĐANG DIỄN RA (< 2 GIỜ)"
                event["weight"] = event.get("weight", 2.0) * 1.3
                events_window.append(event)
            elif age_seconds <= 14400:
                event["freshness"] = "recent_4h"
                event["status_tag"] = "🟠 ĐỢT MƯA VỪA DỨT (2-4 GIỜ)"
                event["weight"] = event.get("weight", 2.0) * 1.1
                events_24h.append(event)
            elif age_seconds <= 86400:
                event["freshness"] = "within_24h"
                event["status_tag"] = "🟡 CẢNH BÁO TRONG NGÀY (4-24 GIỜ)"
                event["weight"] = event.get("weight", 2.0) * 1.0
                events_24h.append(event)

            if age_seconds <= 86400 and vid_id:
                self.state_manager.mark_seen(vid_id, c_time)

        self.state_manager.save()

        # Chế độ Live Mode nghiêm ngặt: Giữ đúng cửa sổ 24 giờ qua (3 tầng cảnh báo)
        display_events = events_window + events_24h
        win_label = "24 giờ qua (3 tầng cảnh báo: <2h, 2-4h, 4-24h)"
        if not display_events:
            win_label = f"{win_label} (Không có ngập mới)"

        display_events.sort(key=lambda x: (
            3 if x.get("freshness") == "strict_2h" else (2 if x.get("freshness") == "recent_4h" else 1),
            x.get("weight", 1.0),
            x.get("create_time", 0)
        ), reverse=True)

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
