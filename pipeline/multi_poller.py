"""
pipeline/multi_poller.py - Bộ Thu Thập Dữ Liệu Song Song Đa Nền Tảng Toàn Diện (TikTok + Facebook + Threads)
Chế độ LIVE chạy đồng thời cả 3 nguồn bằng đa luồng (concurrent.futures.ThreadPoolExecutor):
1. TikTok Video Scraper (Tìm kiếm video & Hashtag ngập lụt TP.HCM - Giữ nguyên ổn định)
2. Facebook Poller (Cào bài đăng người dùng + Fanpage với dữ liệu 100% thật từ báo chí & cộng đồng)
3. Threads Scraper (Meta Threads - Cập nhật tức thời từ cộng đồng người dùng trẻ)
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple, Optional

from pipeline.tiktok_poller import TikTokPoller
from pipeline.facebook_poller import FacebookPoller
from pipeline.threads_poller import ThreadsPoller
from core.config import DEFAULT_WINDOW_MINUTES

class MultiPlatformPoller:
    def __init__(self, apify_token: Optional[str] = None):
        self.tiktok_poller = TikTokPoller(apify_token=apify_token)
        self.facebook_poller = FacebookPoller(apify_token=apify_token)
        self.threads_poller = ThreadsPoller(apify_token=apify_token)

    def poll_live(self, window_minutes: int = DEFAULT_WINDOW_MINUTES) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Cào toàn diện đồng thời tất cả các nguồn trong luồng Real-Time:
        - TikTok Video (Ổn định)
        - Facebook Bài đăng người dùng & Fanpages
        - Threads (Meta Threads)
        """
        combined_events = []
        stats = {
            "mode": "live",
            "tiktok_count": 0,
            "facebook_count": 0,
            "threads_count": 0,
            "total_events": 0,
            "active_window": f"{window_minutes // 60} giờ qua" if window_minutes >= 60 else f"{window_minutes} phút"
        }

        print("\n=======================================================")
        print("[MultiPoller] BẮT ĐẦU CÀO TOÀN DIỆN THỜI GIAN THỰC (TIKTOK + FACEBOOK + THREADS):")
        print("  1. [TikTok Live] Quét video mưa ngập & triều cường đô thị (Giữ nguyên)")
        print("  2. [Facebook Live] Quét bài đăng người dùng & Fanpage giao thông (Dữ liệu thật 100%)")
        print("  3. [Threads Live] Quét cập nhật mưa ngập từ giới trẻ trên Meta Threads")
        print("=======================================================\n")

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_tt = executor.submit(self.tiktok_poller.poll_live_apify, window_minutes=window_minutes)
            future_fb = executor.submit(self.facebook_poller.poll_live_apify, window_minutes=window_minutes)
            future_th = executor.submit(self.threads_poller.poll_live_apify, window_minutes=window_minutes)

            try:
                tt_events, tt_stats = future_tt.result(timeout=140)
                stats["tiktok_count"] = len(tt_events)
                stats["active_window"] = tt_stats.get("active_window", stats["active_window"])
                combined_events.extend(tt_events)
                print(f"[MultiPoller] TikTok hoàn thành: {len(tt_events)} sự kiện.")
            except Exception as e:
                print(f"[MultiPoller] TikTok error: {e}")

            try:
                fb_events, fb_stats = future_fb.result(timeout=140)
                stats["facebook_count"] = len(fb_events)
                combined_events.extend(fb_events)
                print(f"[MultiPoller] Facebook hoàn thành: {len(fb_events)} sự kiện ngập lụt.")
            except Exception as e:
                print(f"[MultiPoller] Facebook error: {e}")

            try:
                th_events, th_stats = future_th.result(timeout=140)
                stats["threads_count"] = len(th_events)
                combined_events.extend(th_events)
                print(f"[MultiPoller] Threads hoàn thành: {len(th_events)} sự kiện ngập lụt.")
            except Exception as e:
                print(f"[MultiPoller] Threads error: {e}")

        # Khử trùng lặp nội dung giữa tất cả các nguồn
        deduped = []
        seen = set()

        for ev in combined_events:
            k = (ev["location"]["street"], ev["opinion"], ev["text"][:30].lower())
            if k in seen:
                continue
            seen.add(k)
            deduped.append(ev)

        deduped.sort(key=lambda x: (x.get("weight", 1.0), x.get("create_time", 0)), reverse=True)
        stats["total_events"] = len(deduped)

        print("\n[MultiPoller] TỔNG HỢP KẾT QUẢ CÀO TOÀN DIỆN THỜI GIAN THỰC:")
        print(f"  - TikTok: {stats['tiktok_count']} bài")
        print(f"  - Facebook: {stats['facebook_count']} bài")
        print(f"  - Threads: {stats['threads_count']} bài")
        print(f"  -> Tổng sự kiện hợp nhất: {len(deduped)} điểm ngập trên bản đồ.\n")

        return deduped, stats

    def poll_simulation(self, window_minutes: int = DEFAULT_WINDOW_MINUTES, batch_size: int = 15) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Phát lại dữ liệu đa nền tảng mô phỏng: 100% dữ liệu thật, không có bài viết hay liên kết bịa đặt.
        """
        tt_events, tt_stats = self.tiktok_poller.poll_simulation(window_minutes=window_minutes, batch_size=batch_size)
        fb_events, fb_stats = self.facebook_poller.poll_simulation(window_minutes=window_minutes, batch_size=10)
        th_events, th_stats = self.threads_poller.poll_simulation(window_minutes=window_minutes, batch_size=6)

        combined = list(tt_events) + list(fb_events) + list(th_events)
        combined.sort(key=lambda x: (x.get("weight", 1.0), x.get("create_time", 0)), reverse=True)

        stats = {
            "mode": "simulation",
            "tiktok_count": len(tt_events),
            "facebook_count": len(fb_events),
            "threads_count": len(th_events),
            "total_events": len(combined),
            "active_window": f"{window_minutes // 60} giờ qua (Mô phỏng dữ liệu thật)"
        }
        return combined, stats
