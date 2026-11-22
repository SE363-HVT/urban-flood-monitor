"""Build the live centerline index from a local OpenStreetMap .osm.pbf extract."""

import argparse
import hashlib
import json
import os
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

import osmium

from core.road_geometry import (
    NON_VEHICULAR_ROADS, SERVICE_ADMIN_NAMES, SERVICE_ENVELOPES,
    name_key, road_key, ward_key,
)


class NamedWays(osmium.SimpleHandler):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.count = 0
        self.geometry = osmium.geom.GeoJSONFactory()

    def area(self, area):
        if area.from_way() or area.tags.get("boundary") != "administrative":
            return
        label = area.tags.get("name", "")
        name = name_key(label)
        level = area.tags.get("admin_level")
        regional = level == "4" and name in SERVICE_ADMIN_NAMES
        if not regional and (level not in {"6", "7", "8", "9", "10"} or not name.startswith(("phuong ", "xa ", "dac khu "))):
            return
        try:
            polygons = json.loads(self.geometry.create_multipolygon(area))["coordinates"]
        except osmium.InvalidLocationError:
            return
        exterior = [point for rings in polygons for point in rings[0]]
        if not exterior:
            return
        lon, lat = zip(*exterior)
        bounds = min(lat), max(lat), min(lon), max(lon)
        south, north, west, east = bounds
        if not any(south <= n and north >= s and west <= e and east >= w
                   for s, n, w, e in SERVICE_ENVELOPES):
            return
        key = name if regional else ward_key(label)
        self.connection.execute("INSERT INTO admin_areas VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (key, int(regional), *bounds, json.dumps(polygons, separators=(",", ":"))))

    def way(self, way):
        highway = way.tags.get("highway")
        if not highway or highway in NON_VEHICULAR_ROADS:
            return
        names = {
            road_key(name) for tag in ("name", "name:vi", "official_name", "alt_name", "ref")
            for name in way.tags.get(tag, "").split(";") if road_key(name)
        }
        if not names or len(way.nodes) < 2 or any(not node.location.valid() for node in way.nodes):
            return
        points = [(node.lon, node.lat) for node in way.nodes]
        longitudes, latitudes = zip(*points)
        if not any(s <= min(latitudes) <= max(latitudes) <= n and w <= min(longitudes) <= max(longitudes) <= e
                   for s, n, w, e in SERVICE_ENVELOPES):
            return
        coordinates = json.dumps(points, separators=(",", ":"))
        self.connection.executemany(
            "INSERT INTO named_ways VALUES (?, ?, ?, ?, ?, ?, ?)",
            [(name, way.id, min(latitudes), max(latitudes), min(longitudes), max(longitudes), coordinates)
             for name in names],
        )
        self.count += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("extract", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/osm_named_roads.sqlite3"))
    args = parser.parse_args()
    with args.extract.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fd, filename = tempfile.mkstemp(suffix=".sqlite3", dir=args.output.parent)
    os.close(fd)
    try:
        with closing(sqlite3.connect(filename)) as connection, connection:
            connection.execute(
                """CREATE TABLE named_ways (
                       name TEXT, osm_id INTEGER, south REAL, north REAL, west REAL, east REAL,
                       coordinates TEXT, PRIMARY KEY(name, osm_id)
                   ) WITHOUT ROWID"""
            )
            connection.execute("CREATE TABLE extract (filename TEXT, sha256 TEXT)")
            connection.execute("""CREATE TABLE admin_areas (
                name TEXT, regional INTEGER, south REAL, north REAL, west REAL, east REAL, polygons TEXT
            )""")
            connection.execute("INSERT INTO extract VALUES (?, ?)", (args.extract.name, digest))
            handler = NamedWays(connection)
            handler.apply_file(str(args.extract), locations=True, idx="flex_mem")
            if not handler.count:
                raise ValueError("The extract has no named roads in the supported area")
            connection.execute("CREATE INDEX admin_lookup ON admin_areas (name, regional)")
        os.replace(filename, args.output)
    finally:
        Path(filename).unlink(missing_ok=True)
    print(f"{handler.count} named OSM ways indexed. Source SHA-256 {digest}.")


if __name__ == "__main__":
    main()
