import io
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core import gazetteer
from core.road_geometry import representative_local_road, representative_ward_point, select_road, snap_local_road
from pipeline.simulation_replayer import _resolve_replay_location


def way(name="Đường Hoa Mai", ward="Phường Một", lon=106.7):
    return {
        "name": name,
        "osm_type": "way",
        "category": "highway",
        "type": "residential",
        "address": {"country_code": "vn"},
        "display_name": f"{name}, {ward}, Thành phố Hồ Chí Minh, Việt Nam",
        "geojson": {"type": "LineString", "coordinates": [[lon, 10.8], [lon, 10.802]]},
        "lat": "10.9",
        "lon": "106.9",
    }


def official_ward(ward, district):
    return ward


class RoadGeometryTests(unittest.TestCase):
    def test_simulation_uses_shared_osm_pin_and_protects_historical_road(self):
        historical = {"street": "Đường Hoa Mai", "ward": "Phường Một", "precision": "street",
                      "lat": 10.8, "lon": 106.7, "heat_points": [[10.8, 106.7]], "source": "annotated_dataset_v1"}
        candidate = {**historical, "street": "Hoa Mai", "lat": 10.8002, "heat_points": [[10.8002, 106.7]],
                     "coordinate_kind": "osm_road_centerline", "resolution_reason": "named_road"}
        other_road = {**candidate, "street": "Hoa Lan"}
        with patch("pipeline.simulation_replayer.match_all_hotspots", return_value=[other_road, candidate]) as match:
            shared = _resolve_replay_location("Hoa Mai ngập", historical)
            self.assertEqual((shared["lat"], shared["heat_points"], shared["coordinate_source"]),
                             (10.8002, [[10.8002, 106.7]], "OpenStreetMap"))
            self.assertEqual(historical["lat"], 10.8)
            for replacement in (
                other_road,
                {**candidate, "lat": 10.85},
                {**candidate, "ward": "Phường Hai"},
                {**candidate, "precision": "ward", "coordinate_kind": "administrative_center"},
                None,
            ):
                match.return_value = [replacement] if replacement else []
                self.assertIs(_resolve_replay_location("Hoa Mai ngập", historical), historical)

            match.return_value = [other_road, candidate]
            area = {**historical, "street": "", "precision": "ward"}
            self.assertIs(_resolve_replay_location("Hoa Mai và Hoa Lan ngập", area), area)

    def test_three_levels_and_service_boundary(self):
        with tempfile.TemporaryDirectory() as folder:
            index = Path(folder) / "roads.sqlite3"
            polygon = json.dumps([[[[106.6, 10.7], [106.9, 10.7], [106.9, 11], [106.6, 11], [106.6, 10.7]]]])
            connection = sqlite3.connect(index)
            try:
                connection.executescript("""
                    CREATE TABLE named_ways (name, south, north, west, east, coordinates);
                    CREATE TABLE admin_areas (name, regional, south, north, west, east, polygons);
                    INSERT INTO named_ways VALUES
                        ('hoa mai', 10.8, 10.802, 106.7, 106.7, '[[106.7,10.8],[106.7,10.802]]'),
                        ('hoa lan', 10.8, 10.802, 107.2, 107.2, '[[107.2,10.8],[107.2,10.802]]'),
                        ('hoa hue', 10.8, 10.802, 106.7, 106.7, '[[106.7,10.8],[106.7,10.802]]'),
                        ('hoa hue', 10.8, 10.802, 106.75, 106.75, '[[106.75,10.8],[106.75,10.802]]'),
                        ('hoa mai', 10.802, 10.803, 106.7, 106.7, '[[106.7,10.802],[106.7,10.803]]');
                """)
                connection.executemany(
                    "INSERT INTO admin_areas VALUES (?, ?, 10.7, 11, 106.6, 106.9, ?)",
                    [("thanh pho ho chi minh", 1, polygon), ("phường một", 0, polygon)],
                )
                connection.commit()
            finally:
                connection.close()
            self.assertIsNone(representative_local_road(index, "Hoa Lan"))
            self.assertIsNone(representative_local_road(index, "Hoa Huệ"))
            self.assertIsNotNone(representative_local_road(index, "Hoa Mai"))
            self.assertEqual(representative_local_road(index, "Hoa Huệ", anchor=(10.801, 106.75)), (10.801, 106.75))
            self.assertIsNotNone(representative_ward_point(index, "Phường Một", (10.8, 107)))
            ward = {"keywords": ["phường một"], "display_name": "Phường Một", "ward": "Phường Một", "lat": 10.8, "lon": 107}
            with (
                patch.dict(os.environ, {"RADINET_OSM_ROAD_INDEX": str(index)}),
                patch.object(gazetteer, "STREET_HOTSPOTS", []),
                patch.object(gazetteer, "CSGT_HOTSPOTS", []),
                patch.object(gazetteer, "ADMIN_HOTSPOTS", [ward]),
            ):
                road = gazetteer.match_hotspot("Ngập nặng ở số 12 đường Hoa Mai, Phường Một, TP.HCM.")
                bare = gazetteer.match_hotspot("Hoa Mai ngập nặng, Phường Một, TP.HCM.")
                ascii_name = gazetteer.match_hotspot("Duong Hoa Mai dang ngap, phuong mot, TP.HCM.")
                area = gazetteer.match_hotspot("Ngập nhiều nơi ở Phường Một, TP.HCM.")
                city = gazetteer.match_hotspot("Ngập nhiều nơi ở TP.HCM.")
                unavailable = gazetteer.match_hotspot("Ngập ở đường Hoa Lan, Phường Một, TP.HCM.")
                self.assertEqual([road["precision"], area["precision"], city["precision"]], ["street", "ward", "city"])
                self.assertEqual(road["lon"], 106.7)
                self.assertEqual(road["coordinate_kind"], "osm_road_centerline")
                self.assertEqual(bare["heat_points"], road["heat_points"])
                self.assertEqual(ascii_name["heat_points"], road["heat_points"])
                self.assertEqual(road["resolution_reason"], "named_road")
                self.assertEqual(area["resolution_reason"], "ward_only")
                self.assertEqual(city["resolution_reason"], "city_only")
                self.assertEqual((unavailable["precision"], unavailable["resolution_reason"]), ("ward", "road_unverified"))
                self.assertEqual(city["heat_points"], [[10.7769, 106.7009]])
                self.assertEqual(gazetteer.match_all_hotspots("Đường Hoa Mai, Hà Nội, bị ngập."), [])
                mixed = "Đường Hoa Mai, Hà Nội, bị ngập; TP.HCM có mưa."
                self.assertIsNone(gazetteer.match_hotspot(mixed))
                self.assertEqual(gazetteer.match_all_hotspots(mixed), [])

    def test_local_index_requires_nearby_road_with_matching_name(self):
        with tempfile.TemporaryDirectory() as folder:
            index = Path(folder) / "roads.sqlite3"
            connection = sqlite3.connect(index)
            try:
                connection.execute(
                    "CREATE TABLE named_ways (name, south, north, west, east, coordinates)"
                )
                connection.execute(
                    "INSERT INTO named_ways VALUES (?, ?, ?, ?, ?, ?)",
                    ("hoa mai", 10.8, 10.802, 106.7, 106.7, "[[106.7, 10.8], [106.7, 10.802]]"),
                )
                connection.commit()
            finally:
                connection.close()
            self.assertEqual(snap_local_road(index, "Đường Hoa Mai", (10.801, 106.7001)), (10.801, 106.7))
            self.assertIsNone(snap_local_road(index, "Đường Hoa Mai", (10.801, 106.703)))
            self.assertIsNone(snap_local_road(index, "Đường Hoa Lan", (10.801, 106.7001)))

    def test_uses_linestring_and_rejects_wrong_name_ward_and_places(self):
        candidates = [
            way(name="Hẻm Hoa Mai"),
            way(ward="Phường Hai", lon=106.75),
            {**way(), "category": "building"},
            {**way(), "geojson": {"type": "Point", "coordinates": [106.7, 10.8]}},
            way(),
        ]
        point, ward, _ = select_road(candidates, "hoa mai", "Phường Một", official_ward)
        self.assertAlmostEqual(point[0], 10.801)
        self.assertEqual(point[1], 106.7)
        self.assertEqual(ward, "Phường Một")
        self.assertIsNone(select_road(candidates[:-1], "hoa mai", "Phường Một", official_ward))

    def test_ambiguous_names_and_distant_anchor_are_rejected(self):
        candidates = [way(), way(ward="Phường Hai", lon=106.75)]
        self.assertIsNone(select_road(candidates, "hoa mai", "", official_ward))
        self.assertIsNone(select_road(candidates, "hoa mai", "", official_ward, (10.801, 106.72)))
        point, _, _ = select_road(candidates, "hoa mai", "", official_ward, (10.8004, 106.7001))
        self.assertAlmostEqual(point[0], 10.8004)
        self.assertEqual(point[1], 106.7)

    def test_live_matcher_uses_verified_geometry_and_retries_temporary_failures(self):
        with (
            tempfile.TemporaryDirectory() as folder,
            patch.object(gazetteer, "ROAD_CACHE_FILE", str(Path(folder) / "roads.sqlite3")),
            patch.dict(os.environ, {"RADINET_OSM_ROAD_INDEX": "", "RADINET_NOMINATIM_SEARCH_URL": "http://example.test/search"}),
            patch.object(gazetteer, "STREET_HOTSPOTS", []),
            patch.object(gazetteer, "CSGT_HOTSPOTS", []),
            patch.object(gazetteer, "ADMIN_HOTSPOTS", []),
            patch("core.gazetteer.urllib.request.urlopen", side_effect=[
                TimeoutError, io.BytesIO(json.dumps([way()]).encode()),
            ]) as fetch,
        ):
            text = "Ngập ở đường Hoa Mai, TP.HCM."
            self.assertNotEqual(gazetteer.match_hotspot(text)["precision"], "street")
            match = gazetteer.match_all_hotspots(text)[0]
            self.assertEqual(match["coordinate_kind"], "osm_road_centerline")
            self.assertAlmostEqual(match["lat"], 10.801)
            self.assertEqual(gazetteer.match_hotspot(text), match)
            self.assertEqual(fetch.call_count, 2)


if __name__ == "__main__":
    unittest.main()
