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
from copy import deepcopy
from typing import List, Dict, Any
from pipeline.event_processor import report_url

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
        """Group unique reports in a deterministic order and retain incident history."""
        def event_time(event):
            return event.get("create_time") or event.get("timestamp") or 0

        def report_id(event):
            return str(event.get("canonical_id") or event.get("id") or "")

        def place(event):
            location = event.get("location") or {}
            return (
                str(location.get("street") or "").strip().casefold(),
                str(location.get("ward") or "").strip().casefold(),
                location.get("precision"),
            )

        def status(event):
            text = str(event.get("text") or event.get("title") or "").casefold()
            no_recovery = any(phrase in text for phrase in ("chưa rút", "chưa hết ngập", "chờ nước rút"))
            if not no_recovery and any(phrase in text for phrase in ("nước đã rút", "nước rút hết", "hết ngập")):
                return "receded"
            if "ngập" in text and any(phrase in text for phrase in ("dự báo", "nguy cơ ngập", "có thể ngập")):
                return "forecast"
            if str(event.get("polarity") or "").upper() == "POS" and any(
                phrase in text for phrase in ("cảm ơn", "cứu hộ", "hỗ trợ")
            ):
                return "response"
            return "reported"

        clusters = []
        seen = set()
        for event in sorted(raw_events, key=lambda e: (event_time(e), report_id(e), str(e.get("text") or ""))):
            identity = report_id(event)
            url = report_url(event.get("url"))
            tokens = {("id", identity)} if identity else set()
            if url:
                tokens.add(("url", url))
            if tokens & seen:
                continue
            seen.update(tokens)

            loc = event.get("location") or {}
            lat, lon = loc.get("lat") or event.get("lat"), loc.get("lon") or event.get("lon")
            timestamp = event_time(event)
            street, ward, precision = place(event)
            condition = status(event)
            candidates = []
            if lat and lon and timestamp and precision not in ("ward", "city"):
                for candidate in reversed(clusters):
                    difference = timestamp - event_time(candidate)
                    if difference > self.window:
                        break
                    other = candidate.get("location") or {}
                    other_lat = other.get("lat") or candidate.get("lat")
                    other_lon = other.get("lon") or candidate.get("lon")
                    other_street, other_ward, other_precision = place(candidate)
                    if not other_lat or not other_lon or other_precision in ("ward", "city"):
                        continue
                    if street != other_street or (ward and other_ward and ward != other_ward):
                        continue
                    if condition in ("forecast", "response") or candidate["incident_status"] in ("forecast", "response"):
                        continue
                    distance = haversine_distance_meters(lat, lon, other_lat, other_lon)
                    if distance <= self.radius:
                        candidates.append((distance, difference, report_id(candidate), candidate))

            if candidates:
                cluster = min(candidates, key=lambda item: item[:3])[3]
                cluster["incident_status"] = condition
                cluster["incident_updated_at"] = timestamp
                if condition == "reported":
                    cluster.pop("recovery_report", None)
                if condition == "receded":
                    cluster["recovery_report"] = identity
                cluster["weight"] = max(cluster.get("weight", 1.0), event.get("weight", 1.0))
                anchor = cluster.get("location") or {}
                points = anchor.get("heat_points")
                if isinstance(points, list):
                    for point in loc.get("heat_points") or [[lat, lon]]:
                        if point not in points:
                            points.append(deepcopy(point))
            else:
                cluster = deepcopy(event)
                cluster.update(report_count=0, report_ids=[], sources=[], posts_summary=[],
                               incident_status=condition, incident_updated_at=timestamp)
                clusters.append(cluster)

            cluster["report_count"] += 1
            if identity:
                cluster["report_ids"].append(identity)
            platform = event.get("platform", "social")
            if platform not in cluster["sources"]:
                cluster["sources"].append(platform)
            count = cluster["report_count"]
            cluster["is_cluster"] = count > 1
            cluster["cluster_label"] = f"{count} báo cáo" if count > 1 else "Báo cáo đơn lẻ"
            cluster["posts_summary"].append({
                "author": event.get("author", "Người dân"),
                "text": event.get("text") or event.get("title", ""),
                "url": event.get("url", ""),
                "platform": platform,
                "create_time": timestamp,
            })

        return clusters
