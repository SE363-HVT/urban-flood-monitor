import os
import sys
import json
import time
import urllib.request
import urllib.parse
import re

DATA_FILE = "D:/SE363_RAWDATA/data/csgt_122_flood_hotspots.json"
CACHE_FILE = "D:/SE363_RAWDATA/data/osm_geocoded_csgt.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    hotspots = json.load(f)

# Load existing progress if available
results = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            results = json.load(f)
    except Exception:
        results = {}

print(f"Loaded {len(hotspots)} hotspots. Existing cached: {len(results)}", flush=True)

def clean_street_name(street: str) -> str:
    s = street.strip()
    s = re.sub(r'\(.*?\)', '', s).strip()
    s = re.sub(r'^(đường|tuyến đường|chân cầu|cổng|hầm chui|khu vực|ngã tư|ngã ba|vòng xoay|chợ|bờ kè)\s+', '', s, flags=re.IGNORECASE).strip()
    return s

query_cache = {}

def geocode_osm(query: str):
    q_clean = query.strip().lower()
    if q_clean in query_cache:
        return query_cache[q_clean]
        
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=5"
    headers = {"User-Agent": "SE363-PrecisionGIS/4.0 (contact: student@hcmut.edu.vn)"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for item in data:
                if item.get("class") in ["highway", "junction", "place", "amenity"]:
                    query_cache[q_clean] = item
                    return item
            if data:
                query_cache[q_clean] = data[0]
                return data[0]
    except Exception as e:
        pass
    query_cache[q_clean] = None
    return None

success_cnt = 0
for i, h in enumerate(hotspots):
    hid = h["id"]
    if hid in results and results[hid] is not None:
        success_cnt += 1
        continue
        
    st = h["street"]
    dist = h.get("district", "")
    ward = h.get("ward", "")
    
    clean_st = clean_street_name(st)
    parts = [p.strip() for p in clean_st.split("-")]
    
    queries = []
    if len(parts) > 1:
        queries.append(f"Đường {parts[0]}, {dist}, Thành phố Hồ Chí Minh")
        queries.append(f"Đường {parts[1]}, {dist}, Thành phố Hồ Chí Minh")
        queries.append(f"Đường {parts[0]}, Thành phố Hồ Chí Minh")
    else:
        queries.append(f"Đường {clean_st}, {dist}, Thành phố Hồ Chí Minh")
        queries.append(f"Đường {clean_st}, Thành phố Hồ Chí Minh")
        queries.append(f"{clean_st}, Thành phố Hồ Chí Minh")

    found = None
    used_q = ""
    for q in queries:
        found = geocode_osm(q)
        if found:
            used_q = q
            break
        time.sleep(0.4)

    if found:
        lat = round(float(found["lat"]), 5)
        lon = round(float(found["lon"]), 5)
        results[hid] = {
            "lat": lat,
            "lon": lon,
            "osm_name": found.get("display_name", "")[:60],
            "query": used_q
        }
        success_cnt += 1
        print(f"[{i+1}/{len(hotspots)}] OK: {st} -> ({lat}, {lon})", flush=True)
    else:
        results[hid] = None
        print(f"[{i+1}/{len(hotspots)}] FAIL: {st}", flush=True)

    # Save progress after every 5 items
    if i % 5 == 0:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    time.sleep(0.8)

with open(CACHE_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"[Done] Geocoded successfully {success_cnt}/{len(hotspots)} hotspots!", flush=True)
