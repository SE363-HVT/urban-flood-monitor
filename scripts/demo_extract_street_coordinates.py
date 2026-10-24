#!/usr/bin/env python3
"""
RadiNet/scripts/demo_extract_street_coordinates.py
Interactive CLI demonstration of street entity extraction and GPS coordinate resolution (lat, lon)
using RadiNet's core gazetteer, curated CSGT hotspots, and OpenStreetMap (OSM) dynamic geocoder.
"""

import os
import sys

# Ensure repository root is in python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.gazetteer import match_hotspot, geocode_osm_dynamic


def display_street_coordinates(query_or_sentence: str):
    print("\n" + "=" * 75)
    print(f"INPUT TEXT: \"{query_or_sentence}\"")
    print("-" * 75)

    # 1. Try full hierarchical hotspot matching (Street-first)
    res = match_hotspot(query_or_sentence)

    if not res:
        # 2. Fallback: Direct dynamic OSM geocoding query
        res = geocode_osm_dynamic(query_or_sentence)

    if not res:
        print("[-] Result: No valid street or coordinate could be extracted.")
        print("    (Reason: No recognized street entity, or location falls outside HCMC bounds).")
        print("=" * 75)
        return

    name = res.get("display_name") or res.get("street") or "Unknown"
    kw = res.get("matched_keyword", "N/A")
    lat = res.get("lat")
    lon = res.get("lon")
    ward = res.get("ward", "N/A")
    district = res.get("district", "N/A")
    source = res.get("source", "OpenStreetMap Nominatim Dynamic Geocoder")
    priority = res.get("priority", "N/A")

    print(f"[+] Extracted Street   : {name}")
    print(f"    • Matched Keyword  : {kw}")
    print(f"    • GPS Coordinates  : Latitude = {lat}, Longitude = {lon}")
    print(f"    • Admin Unit (Ward): {ward}")
    print(f"    • District / City  : {district}")
    print(f"    • Data Source      : {source} (Priority: {priority})")
    print(f"    • Google Maps Link : https://www.google.com/maps?q={lat},{lon}")
    print("=" * 75)


def run_predefined_demos():
    print("=" * 75)
    print("      RADINET: STREET ENTITY & GPS COORDINATE EXTRACTION DEMO           ")
    print("=" * 75)

    test_cases = [
        # 1. Curated CSGT Hotspot with street segment
        "Đường Trần Xuân Soạn Quận 7 ngập sâu nửa mét do triều cường dâng cao",
        
        # 2. Major intersection
        "Ngã tư Bảy Hiền nước ngập mênh mông, nhiều xe máy chết máy",
        
        # 3. Known chronic flood road
        "Đường Phan Huy Ích Gò Vấp đang ngập nặng sau mưa",
        
        # 4. Critical flood road in Binh Thanh
        "Đường Nguyễn Hữu Cảnh sau cơn mưa lớn nước rút rất chậm",
        
        # 5. Dynamic street discovered via OpenStreetMap (Zero-Shot Geocoding)
        "Đường Lê Văn Việt hiện tại đang đông đúc và có dấu hiệu ngập nhẹ",
        
        # 6. Specific road in Thu Duc
        "Đường Tô Ngọc Vân đoạn gần ray xe lửa nước dâng cao"
    ]

    for sentence in test_cases:
        display_street_coordinates(sentence)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run custom input from command line argument
        custom_input = " ".join(sys.argv[1:])
        display_street_coordinates(custom_input)
    else:
        # Run standard test cases
        run_predefined_demos()
        print("\nTip: You can test any custom sentence by running:")
        print("  python RadiNet/scripts/demo_extract_street_coordinates.py \"Đường Võ Văn Ngân Thủ Đức ngập sâu\"")
