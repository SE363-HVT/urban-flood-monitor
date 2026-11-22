"""Evaluate a location index on independent georeferenced flood reports."""

import argparse
import json
import math
import os
import sqlite3
from collections import Counter
from contextlib import closing, nullcontext
from pathlib import Path
from statistics import median

from core.gazetteer import match_all_hotspots
from core.road_geometry import _point_on_road, _road_segments, distance_m, name_key, road_key


def review_rows(rows):
    sources = {}
    for row in rows:
        if "source_file" in row:
            source = row["source_file"]
            if source not in sources:
                sources[source] = json.loads(Path(source).read_text(encoding="utf-8-sig"))
            record = sources[source][row["record_index"]]
            yield {**row, "text": record[row.get("text_field", "text")]}
        else:
            yield row


def _centerline_error(connection, street, point):
    if not connection:
        return None
    key = road_key(street)
    legacy_key = "cach mang thang 8" if key == "cach mang thang tam" else key
    ways = connection.execute("SELECT coordinates FROM named_ways WHERE name IN (?, ?)", (key, legacy_key))
    errors = []
    for (coordinates,) in ways:
        segments = _road_segments({"type": "LineString", "coordinates": json.loads(coordinates)})
        if segments:
            errors.append(distance_m(point, _point_on_road(segments, point)))
    return min(errors, default=None)


def evaluate(rows, index):
    os.environ["RADINET_OSM_ROAD_INDEX"] = str(index) if index else ""
    os.environ["RADINET_NOMINATIM_SEARCH_URL"] = ""
    counts = Counter()
    errors, centerline_errors, predictions = [], [], []
    opened = closing(sqlite3.connect(index.resolve().as_uri() + "?mode=ro", uri=True)) if index else nullcontext()
    with opened as connection:
        for row in rows:
            counts["reports"] += 1
            matches = match_all_hotspots(row["text"], max_spots=1)
            match = matches[0] if matches else {}
            kind = match.get("coordinate_kind", "unresolved")
            counts[kind] += 1
            level = match.get("precision", "unresolved")
            expected_level = row.get("level")
            if expected_level:
                counts["level_labels"] += 1
                counts["correct_level"] += expected_level == level
            road = row.get("road")
            if road:
                counts["road_labels"] += 1
                road_correct = road_key(road) == road_key(match.get("street", ""))
                counts["correct_road"] += road_correct
                if not road_correct:
                    counts["wrong_road" if level == "street" else "missed_road"] += 1
            if row.get("ward"):
                counts["ward_labels"] += 1
                counts["correct_ward"] += name_key(match.get("ward", "")) == name_key(row["ward"])
            pin = (match["lat"], match["lon"]) if match else None
            if level == "street":
                centerline = _centerline_error(connection, match.get("street", ""), pin)
                if centerline is not None:
                    centerline_errors.append(centerline)
                    counts["on_centerline"] += centerline <= 1
                if "lat" in row or "lon" in row:
                    point = (float(row["lat"]), float(row["lon"]))
                    if not (-90 <= point[0] <= 90 and -180 <= point[1] <= 180):
                        raise ValueError("Reference point must be a valid latitude and longitude")
                    error = distance_m(point, pin)
                    errors.append(error)
                    counts["within_25m"] += error <= 25
                    counts["within_50m"] += error <= 50
            predictions.append({
                "id": row.get("id", counts["reports"]), "level": level,
                "street": match.get("street", ""), "ward": match.get("ward", ""),
                "pin": pin, "reason": match.get("resolution_reason"),
            })

    errors.sort()
    return {
        "counts": dict(counts),
        "point_predictions": len(errors),
        "median_error_m": round(median(errors), 2) if errors else None,
        "p90_error_m": round(errors[math.ceil(0.9 * len(errors)) - 1], 2) if errors else None,
        "centerline_checks": len(centerline_errors),
        "max_centerline_error_m": round(max(centerline_errors), 3) if centerline_errors else None,
        "predictions": predictions,
    }


def compare(baseline, candidate, threshold):
    levels = {"unresolved": 0, "city": 1, "ward": 2, "street": 3}
    changes = []
    for old, new in zip(baseline["predictions"], candidate["predictions"], strict=True):
        shift = distance_m(old["pin"], new["pin"]) if old["pin"] and new["pin"] else None
        downgraded = levels[new["level"]] < levels[old["level"]]
        changed_road = old["level"] == new["level"] == "street" and road_key(old["street"]) != road_key(new["street"])
        changed_ward = bool(old["ward"] and new["ward"] and name_key(old["ward"]) != name_key(new["ward"]))
        if downgraded or changed_road or changed_ward or (shift is not None and shift > threshold):
            changes.append({"id": new["id"], "shift_m": round(shift, 2) if shift is not None else None,
                            "downgraded": downgraded, "changed_road": changed_road, "changed_ward": changed_ward})
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", type=Path, help="JSONL with text or a source record, and optional level, road, ward, lat/lon")
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--baseline-index", type=Path)
    parser.add_argument("--baseline-results", type=Path, help="Candidate report saved from an earlier code version")
    parser.add_argument("--review-shift-m", type=float, default=100)
    args = parser.parse_args()
    with args.reports.open(encoding="utf-8") as stream:
        rows = list(review_rows(json.loads(line) for line in stream if line.strip()))
    if not rows:
        parser.error("At least one independently georeferenced report is required")
    for index in (args.index, args.baseline_index):
        if index is not None and not index.is_file():
            parser.error(f"Index does not exist: {index}")
    baseline = evaluate(rows, args.baseline_index) if not args.baseline_results else json.loads(
        args.baseline_results.read_text(encoding="utf-8-sig")
    )["candidate"]
    candidate = evaluate(rows, args.index)
    if [p["id"] for p in baseline["predictions"]] != [p["id"] for p in candidate["predictions"]]:
        parser.error("Baseline and candidate must use the same sample IDs in the same order")
    result = {"baseline": baseline, "candidate": candidate,
              "review": compare(baseline, candidate, args.review_shift_m)}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
