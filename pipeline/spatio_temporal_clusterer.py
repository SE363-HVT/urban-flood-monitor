# -*- coding: utf-8 -*-
"""
pipeline/spatio_temporal_clusterer.py
Gom cụm Sự kiện Đa nguồn Không gian - Thời gian (Spatio-Temporal Flood Clustering).

Mục tiêu:
Gom cụm các bài đăng mạng xã hội trùng khớp về không gian (< 400m)
và thời gian (< 45 phút) thành một 'Sự kiện Ngập Thống Nhất' (Unified Incident / Master Incident).
Loại bỏ hiện tượng 20 bài viết cùng nói về 1 điểm ngập gây nhiễu quầng nhiệt,
hợp nhất thành 1 marker lớn với nhãn "Được báo cáo bởi 20 người".
"""

import math
import time
from typing import List, Dict, Any

try:
    from pipeline.veracity_checker import haversine_distance_meters
except ImportError:
    EARTH_RADIUS_METERS = 6371000.0
    def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi / 2.0) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return EARTH_RADIUS_METERS * c


class SpatioTemporalClusterer:
    """
    Gom cụm các bài đăng mạng xã hội trùng khớp về không gian (< 400m)
    và thời gian (< 45 phút) thành một 'Sự kiện Ngập Thống Nhất' (Unified Incident).
    """
    def __init__(self, radius_meters: float = 400.0, time_window_seconds: int = 2700):
        self.radius = radius_meters
        self.window = time_window_seconds

    def cluster_events(self, raw_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Gom cụm danh sách sự kiện ngập lụt.
        Các sự kiện gần nhau (< radius_meters) và diễn ra trong cùng khoảng thời gian (< time_window_seconds)
        sẽ được gộp lại thành 1 sự kiện trọng điểm.
        """
        clusters: List[Dict[str, Any]] = []

        for ev in raw_events:
            loc = ev.get("location", {})
            lat = loc.get("lat") or ev.get("lat")
            lon = loc.get("lon") or ev.get("lon")
            ev_time = ev.get("create_time") or ev.get("timestamp") or int(time.time())

            if not lat or not lon:
                clusters.append(ev)
                continue

            merged = False
            for c in clusters:
                c_loc = c.get("location", {})
                c_lat = c_loc.get("lat") or c.get("lat")
                c_lon = c_loc.get("lon") or c.get("lon")
                c_time = c.get("create_time") or c.get("timestamp") or int(time.time())

                if not c_lat or not c_lon:
                    continue

                dist = haversine_distance_meters(lat, lon, c_lat, c_lon)
                time_diff = abs(ev_time - c_time)

                if dist <= self.radius and time_diff <= self.window:
                    # Tăng số lượng người báo cáo
                    current_count = c.get("report_count", 1) + 1
                    c["report_count"] = current_count

                    # Hợp nhất các nguồn (TikTok, Facebook, RSS,...)
                    cur_sources = c.get("sources", [c.get("platform", "social")])
                    new_src = ev.get("platform", "social")
                    if new_src not in cur_sources:
                        cur_sources.append(new_src)
                    c["sources"] = cur_sources

                    # Tăng trọng số hiển thị do có nhiều nguồn xác nhận
                    c["weight"] = max(c.get("weight", 1.0), ev.get("weight", 1.0)) + 0.5

                    # Ghi nhãn Master Incident
                    c["cluster_label"] = f"Được báo cáo bởi {current_count} người"
                    c["is_cluster"] = True

                    # Tăng bằng chứng Veracity nếu có
                    if "veracity" in c and isinstance(c["veracity"], dict):
                        c["veracity"]["evidence_count"] = max(
                            c["veracity"].get("evidence_count", 1),
                            current_count
                        )
                        c["veracity"]["spatial_consensus_count"] = current_count
                        c["veracity"]["confidence_score"] = min(
                            0.98,
                            c["veracity"].get("confidence_score", 0.75) + 0.05
                        )
                        c["veracity"]["status"] = "confirmed"
                        c["veracity"]["status_label"] = "Đã xác thực (Đồng thuận cao)"

                    # Tổng hợp tóm tắt các bài viết
                    cur_posts = c.get("posts_summary", [])
                    cur_posts.append({
                        "author": ev.get("author", "Người dân"),
                        "text": ev.get("text") or ev.get("title", ""),
                        "url": ev.get("url", ""),
                        "platform": ev.get("platform", "social"),
                        "create_time": ev_time
                    })
                    c["posts_summary"] = cur_posts

                    # Mở rộng quầng nhiệt nếu có nhiều điểm xung quanh
                    if "heat_points" in c_loc and isinstance(c_loc["heat_points"], list):
                        new_pts = loc.get("heat_points", [[lat, lon]])
                        for pt in new_pts:
                            if pt not in c_loc["heat_points"]:
                                c_loc["heat_points"].append(pt)

                    merged = True
                    break

            if not merged:
                ev_copy = dict(ev)
                ev_copy["report_count"] = 1
                ev_copy["sources"] = [ev.get("platform", "social")]
                ev_copy["cluster_label"] = "Báo cáo đơn lẻ"
                ev_copy["is_cluster"] = False
                ev_copy["posts_summary"] = [{
                    "author": ev.get("author", "Người dân"),
                    "text": ev.get("text") or ev.get("title", ""),
                    "url": ev.get("url", ""),
                    "platform": ev.get("platform", "social"),
                    "create_time": ev_time
                }]
                clusters.append(ev_copy)

        return clusters
