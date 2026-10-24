# -*- coding: utf-8 -*-
"""
bigdata/lakehouse/backfill_episodes.py
Backfill ETL Pipeline: Đồng bộ toàn bộ dữ liệu lịch sử các đợt ngập (5 Episodes + Archive)
từ Raw / Processed Dataset vào Data Lakehouse theo chuẩn phân vùng:
data/lakehouse/flood_events/episode_id={episode_id}/date={date}/events.jsonl

Đảm bảo:
1. 100% Kế thừa Street-First GIS Matching (122 CSGT + Tim đường OSM).
2. 100% Kế thừa ĐVHC 168 Phường/Xã mới (NQ 1685).
3. Gắn nhãn ASTE, Severity và Veracity (Đã kiểm định).
4. Đồng bộ metadata.json cho từng Episode.
"""

import os
import sys
import json
import time
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, Any, List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from pipeline.simulation_replayer import SimulationReplayer
from scripts.organize_raw_episodes import determine_episode_id, extract_item_date, EPISODE_DEFINITIONS

DATA_DIR = os.path.join(ROOT_DIR, "data")
PROCESSED_V2 = os.path.join(DATA_DIR, "processed", "hcmc_flood_annotated_v2_multimodal.json")
RAW_EPISODES_DIR = os.path.join(DATA_DIR, "raw", "episodes")
LAKEHOUSE_DIR = os.path.join(DATA_DIR, "lakehouse", "flood_events")


def run_backfill():
    print("=" * 70)
    print("🚀 BẮT ĐẦU BACKFILL DỮ LIỆU LỊCH SỬ VÀO DATA LAKEHOUSE (SE363)")
    print("=" * 70)

    # 1. Nạp pool sự kiện đã chuẩn hóa từ SimulationReplayer (đầy đủ tọa độ Street-First, 168 phường, Veracity)
    t0 = time.time()
    replayer = SimulationReplayer.get_instance()
    pool = replayer._events_pool or []
    print(f"[*] Đã tải {len(pool)} sự kiện chuẩn hóa từ SimulationReplayer")

    # 2. Nạp metadata v2 để lấy mapping episode_id và published_at
    v2_map = {}
    if os.path.exists(PROCESSED_V2):
        with open(PROCESSED_V2, "r", encoding="utf-8") as f:
            v2_data = json.load(f)
            v2_map = {item["id"]: item for item in v2_data}

    os.makedirs(LAKEHOUSE_DIR, exist_ok=True)

    # 3. Đồng bộ metadata.json của từng episode từ raw sang lakehouse
    for ep in EPISODE_DEFINITIONS:
        ep_id = ep["id"]
        ep_lakehouse_dir = os.path.join(LAKEHOUSE_DIR, f"episode_id={ep_id}")
        os.makedirs(ep_lakehouse_dir, exist_ok=True)
        meta_file = os.path.join(ep_lakehouse_dir, "metadata.json")
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(ep, f, ensure_ascii=False, indent=2)

    for special_id in ["historical_archive", "sporadic_flood_events"]:
        sp_dir = os.path.join(LAKEHOUSE_DIR, f"episode_id={special_id}")
        os.makedirs(sp_dir, exist_ok=True)
        raw_meta = os.path.join(RAW_EPISODES_DIR, special_id, "metadata.json")
        if os.path.exists(raw_meta):
            with open(raw_meta, "r", encoding="utf-8") as rf:
                m_data = json.load(rf)
            with open(os.path.join(sp_dir, "metadata.json"), "w", encoding="utf-8") as wf:
                json.dump(m_data, wf, ensure_ascii=False, indent=2)

    # 4. Phân vùng dữ liệu vào Lakehouse theo episode_id và date
    partitioned_events = defaultdict(list)
    processed_count = 0

    for ev in pool:
        ev_id = ev.get("id")
        v2_item = v2_map.get(ev_id, {})

        # Trích xuất ngày
        pub_at = v2_item.get("published_at") or ev.get("created_at_iso") or ""
        date_str = None
        if len(pub_at) >= 10 and pub_at[:4].isdigit():
            date_str = pub_at[:10]
        else:
            d_s, _ = extract_item_date(v2_item) if v2_item else (None, None)
            date_str = d_s or "2026-10-12"

        # Phân định Episode ID
        ep_id = v2_item.get("episode_id")
        if not ep_id:
            ep_id = determine_episode_id(date_str)

        lakehouse_record = dict(ev)
        lakehouse_record["episode_id"] = ep_id
        lakehouse_record["partition_date"] = date_str
        lakehouse_record["published_at"] = pub_at or f"{date_str}T00:00:00Z"
        lakehouse_record["canonical_id"] = f"{ev.get('platform', 'sim')}_{ev_id}"

        partitioned_events[(ep_id, date_str)].append(lakehouse_record)
        processed_count += 1

    # 5. Ghi ra từng Partition
    print(f"[*] Đang ghi dữ liệu vào {len(partitioned_events)} partitions trong Lakehouse...")
    for (ep_id, date_str), ev_list in sorted(partitioned_events.items()):
        p_dir = os.path.join(LAKEHOUSE_DIR, f"episode_id={ep_id}", f"date={date_str}")
        os.makedirs(p_dir, exist_ok=True)
        file_path = os.path.join(p_dir, "events.jsonl")

        with open(file_path, "w", encoding="utf-8") as f:
            for item in ev_list:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    elapsed = time.time() - t0
    print("=" * 70)
    print(f"🎉 HOÀN TẤT BACKFILL DATA LAKEHOUSE THÀNH CÔNG! ({elapsed:.2f}s)")
    print(f"   - Tổng sự kiện đã xử lý: {processed_count:,}")
    print(f"   - Tổng partitions: {len(partitioned_events):,}")
    print(f"   - Vị trí Lakehouse: {LAKEHOUSE_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    run_backfill()
