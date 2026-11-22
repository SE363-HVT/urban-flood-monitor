"""Select and locate a named road using Nominatim's OSM way geometry."""

import math
import os
import re
import json
import sqlite3
import unicodedata
from contextlib import closing
from functools import lru_cache
from pathlib import Path


NON_VEHICULAR_ROADS = {"footway", "path", "steps", "cycleway", "pedestrian", "proposed", "construction"}
SERVICE_ENVELOPES = ((10.27, 11.51, 105.97, 107.64), (8.34, 8.84, 106.37, 106.85))
SERVICE_ADMIN_NAMES = {"ho chi minh", "thanh pho ho chi minh", "binh duong", "ba ria vung tau"}
# OSM locality node 13163001708 in the former Hưng Long, retained in the new commune.
WARD_LOCALITY_REFERENCES = {"xã hưng long": (10.6587154, 106.6388556)}


def in_service_envelope(lat, lon):
    return any(south <= lat <= north and west <= lon <= east
               for south, north, west, east in SERVICE_ENVELOPES)


def name_key(value):
    value = unicodedata.normalize("NFD", value.casefold().replace("đ", "d"))
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return " ".join(re.findall(r"[a-z0-9]+", value))


def ward_key(value):
    return " ".join(unicodedata.normalize("NFC", value.casefold()).split())


def road_key(value):
    key = re.sub(r"^(?:tuyen duong|duong|dai lo|pho) ", "", name_key(value))
    key = re.sub(r"^ql\s*(?=\d)", "quoc lo ", key)
    key = re.sub(r"^(?:tl|dt)\s*(?=\d)", "tinh lo ", key)
    if key in {"cmt8", "cmt 8", "cach mang thang 8"}:
        return "cach mang thang tam"
    if key in {"30 4", "30 04", "30 thang 04"}:
        return "30 thang 4"
    return key


def distance_m(a, b):
    scale = math.cos(math.radians((a[0] + b[0]) / 2))
    return 111195 * math.hypot(a[0] - b[0], (a[1] - b[1]) * scale)


def _road_segments(geometry):
    kind = geometry.get("type")
    lines = geometry.get("coordinates", [])
    if kind == "LineString":
        lines = [lines]
    elif kind != "MultiLineString":
        return []
    segments = []
    for line in lines:
        points = [(float(lat), float(lon)) for lon, lat, *_ in line]
        if not all(in_service_envelope(lat, lon) for lat, lon in points):
            continue
        for start, end in zip(points, points[1:]):
            length = distance_m(start, end)
            if length:
                segments.append((start, end, length))
    return segments


def _point_on_road(segments, anchor):
    if anchor is None:
        halfway = sum(length for _, _, length in segments) / 2
        for start, end, length in segments:
            if halfway <= length:
                fraction = halfway / length
                return tuple(a + fraction * (b - a) for a, b in zip(start, end))
            halfway -= length
        return segments[-1][1]

    scale = math.cos(math.radians(anchor[0]))
    projected = []
    for start, end, _ in segments:
        dy, dx = end[0] - start[0], (end[1] - start[1]) * scale
        offset_y, offset_x = anchor[0] - start[0], (anchor[1] - start[1]) * scale
        fraction = min(1, max(0, (offset_y * dy + offset_x * dx) / (dy * dy + dx * dx)))
        projected.append((start[0] + fraction * dy, start[1] + fraction * (end[1] - start[1])))
    return min(projected, key=lambda point: distance_m(anchor, point))


def select_road(items, query, ward, resolve_ward, anchor=None):
    candidates = []
    for item in items:
        if item.get("category", item.get("class")) != "highway" or item.get("osm_type") != "way":
            continue
        if item.get("type") in NON_VEHICULAR_ROADS:
            continue
        names = [item.get("name", "")]
        details = item.get("namedetails") or {}
        names.extend(details.get(key, "") for key in ("name", "name:vi", "official_name", "alt_name", "ref"))
        if road_key(query) not in {road_key(alias) for name in names for alias in name.split(";")}:
            continue

        parts = [part.strip() for part in item.get("display_name", "").split(",")]
        address = item.get("address") or {}
        city_names = {"ho chi minh", "tp ho chi minh", "thanh pho ho chi minh"}
        region_names = [*parts[1:], address.get("city", ""), address.get("state", "")]
        if address.get("country_code") != "vn" or not city_names.intersection(map(name_key, region_names)):
            continue
        district = next((part for part in parts if name_key(part).startswith(("quan ", "huyen "))), "")
        ward_name = next((part for part in parts if name_key(part).startswith(("phuong ", "xa ", "thi tran "))), "")
        official_ward = resolve_ward(ward_name, district) if ward_name else ""
        if ward and all(name_key(ward) != name_key(value) for value in (ward_name, official_ward or "")):
            continue
        try:
            segments = _road_segments(item.get("geojson") or {})
        except (TypeError, ValueError):
            continue
        if segments:
            point = _point_on_road(segments, anchor)
            candidates.append((point, official_ward or ward_name, district, sum(s[2] for s in segments)))
    if not candidates:
        return None
    if anchor is not None:
        index = _nearby_projection([candidate[0] for candidate in candidates], anchor)
        return candidates[index][:3] if index is not None else None
    # Results far apart can be different roads or different ends of one long road.
    # A name alone does not identify which segment the report describes.
    best = max(candidates, key=lambda candidate: candidate[3])
    if any(distance_m(best[0], candidate[0]) > 300 for candidate in candidates):
        return None
    return best[:3]


def _nearby_projection(points, anchor):
    if not points:
        return None
    distances = [distance_m(point, anchor) for point in points]
    index = min(range(len(points)), key=distances.__getitem__)
    closest = distances[index]
    if closest > 30 or any(
        distance - closest < 8 and distance_m(points[index], point) > 8
        for point, distance in zip(points, distances)
    ):
        return None
    return index


def snap_local_road(index_path, name, anchor):
    """Project a trusted gazetteer anchor onto a nearby named OSM way."""
    uri = Path(index_path).resolve().as_uri() + "?mode=ro"
    try:
        with closing(sqlite3.connect(uri, uri=True, timeout=0.2)) as connection:
            rows = connection.execute(
                """SELECT coordinates FROM named_ways
                   WHERE name = ? AND south <= ? AND north >= ? AND west <= ? AND east >= ?""",
                (road_key(name), anchor[0] + 0.0003, anchor[0] - 0.0003, anchor[1] + 0.0003, anchor[1] - 0.0003),
            ).fetchall()
        points = []
        for (coordinates,) in rows:
            segments = _road_segments({"type": "LineString", "coordinates": json.loads(coordinates)})
            if segments:
                points.append(_point_on_road(segments, anchor))
        index = _nearby_projection(points, anchor)
        return points[index] if index is not None else None
    except (sqlite3.Error, OSError, ValueError):
        return None


def _inside_ring(lat, lon, ring):
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        if (y1 > lat) != (y2 > lat) and lon < x1 + (x2 - x1) * (lat - y1) / (y2 - y1):
            inside = not inside
    return inside


def _inside_admin(connection, point, name, *, regional=False):
    lat, lon = point
    if not in_service_envelope(lat, lon):
        return False
    rows = connection.execute(
        """SELECT polygons FROM admin_areas
           WHERE name = ? AND regional = ? AND south <= ? AND north >= ? AND west <= ? AND east >= ?""",
        (name_key(name) if regional else ward_key(name), int(regional), lat, lat, lon, lon),
    )
    return any(_inside_ring(lat, lon, rings[0])
               and not any(_inside_ring(lat, lon, hole) for hole in rings[1:])
               for (polygons,) in rows for rings in _decoded_boundaries(polygons) if rings)


@lru_cache(maxsize=32)
def _decoded_boundaries(polygons):
    return json.loads(polygons)


def _eligible_point(connection, point, ward):
    return (not ward or _inside_admin(connection, point, ward)) and any(
        _inside_admin(connection, point, name, regional=True) for name in SERVICE_ADMIN_NAMES
    )


def representative_local_road(index_path, name, ward="", anchor=None):
    """Return a point on the named way inside the service area."""
    try:
        stat = os.stat(index_path)
        return _indexed_road_point(str(Path(index_path).resolve()), (stat.st_ino, stat.st_size, stat.st_mtime_ns),
                                   road_key(name), ward, anchor)
    except (sqlite3.Error, OSError, ValueError):
        return None


@lru_cache(maxsize=4096)
def _indexed_road_point(index_path, revision, key, ward, anchor):
    uri = Path(index_path).as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True, timeout=0.2)) as connection:
        if anchor:
            point = snap_local_road(index_path, key, anchor)
            if point and _eligible_point(connection, point, ward):
                return point
        keys = (key, "cach mang thang 8" if key == "cach mang thang tam" else key)
        ways = connection.execute("SELECT coordinates FROM named_ways WHERE name IN (?, ?)", keys)
        segments = [
            segment for (coordinates,) in ways
            for segment in _road_segments({"type": "LineString", "coordinates": json.loads(coordinates)})
        ]
        # A segment midpoint lies on the way and is a useful road-level pin.
        for a, b, _ in sorted(segments, key=lambda segment: (-segment[2], min(segment[:2]), max(segment[:2]))):
            point = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            if _eligible_point(connection, point, ward):
                return point
    return None


def representative_ward_point(index_path, ward, old_point):
    """Keep a valid ward reference or choose an interior point from a unique OSM boundary."""
    uri = Path(index_path).resolve().as_uri() + "?mode=ro"
    try:
        with closing(sqlite3.connect(uri, uri=True, timeout=0.2)) as connection:
            rows = connection.execute(
                "SELECT DISTINCT polygons FROM admin_areas WHERE name = ? AND regional = 0",
                (ward_key(ward),),
            ).fetchall()
            if not rows:
                point = WARD_LOCALITY_REFERENCES.get(ward_key(ward))
                return point if point and _eligible_point(connection, point, "") else None
            candidates_by_area = []
            if _eligible_point(connection, old_point, ward):
                return old_point
            for (polygons,) in rows:
                for point in _interior_candidates(json.loads(polygons)):
                    if _eligible_point(connection, point, ward):
                        candidates_by_area.append(point)
                        break
            if len(candidates_by_area) == 1:
                return candidates_by_area[0]
    except (sqlite3.Error, OSError, ValueError):
        pass
    return None


def _interior_candidates(polygons):
    candidates = []
    for rings in polygons:
        if not rings:
            continue
        latitudes = [lat for _, lat in rings[0]]
        south, north = min(latitudes), max(latitudes)
        for fraction in (0.25, 0.5, 0.75):
            lat = south + (north - south) * fraction
            edges = sorted(
                x1 + (x2 - x1) * (lat - y1) / (y2 - y1)
                for ring in rings for (x1, y1), (x2, y2) in zip(ring, ring[1:])
                if (y1 > lat) != (y2 > lat)
            )
            for left, right in zip(edges[::2], edges[1::2]):
                if right > left:
                    candidates.append((right - left, (lat, (left + right) / 2)))
    return (point for _, point in sorted(candidates, reverse=True))
