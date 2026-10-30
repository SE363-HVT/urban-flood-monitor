#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/append_new_social_crawl.py
--------------------------------------------------------------------------------
Bổ sung các bài đăng mạng xã hội thực tế vừa cào (Facebook, TikTok, YouTube 2018-2025)
vào tập Master Dataset để vượt mốc 10,000 bản ghi:
- Áp dụng chuẩn gán nhãn chuyên gia CAM_NANG_BI_QUYET_GAN_NHAN_ASTE_CHUAN_EXPERT.md
- Giữ nguyên vẹn 100% các bản ghi trước đây.
- Đánh số seq_id liên tục.
"""

import os
import sys
import glob
import json
import re
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Set

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.reannotate_expert_batches import extract_expert_triplets, clean_aspect_text
from scripts.cleanse_and_resolve_gazetteer import resolve_ward_for_record

V3_PATH = os.path.join(ROOT_DIR, "data", "processed", "hcmc_flood_annotated_v3_multimodal.json")

def append_social_records():
    print("=" * 80)
    print("🚀 BỔ SUNG BÀI ĐĂNG MẠNG XÃ HỘI MỚI CÀO ĐỂ VƯỢT MỐC 10,000 BẢN GHI")
    print("=" * 80)

    with open(V3_PATH, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    initial_len = len(master_data)
    print(f"[*] Số bản ghi hiện tại trong Master: {initial_len}")

    existing_hashes: Set[str] = set()
    for item in master_data:
        t = (item.get("content", {}).get("text") or "").strip().lower()
        if t:
            existing_hashes.add(hashlib.md5(t.encode("utf-8")).hexdigest())

    raw_files = glob.glob(os.path.join(ROOT_DIR, "data", "raw", "episodes", "*", "*_raw.json"))
    new_records = []

    for fpath in sorted(raw_files):
        ep_id = os.path.basename(os.path.dirname(fpath))
        platform = "facebook"
        fname_low = os.path.basename(fpath).lower()
        for p in ["tiktok", "facebook", "youtube", "threads", "news"]:
            if p in fname_low:
                platform = p
                break

        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                items = json.load(fp)
                if not isinstance(items, list): continue
        except Exception:
            continue

        for it in items:
            raw_text = (it.get("text") or it.get("title") or "").strip()
            if len(raw_text) < 15: continue

            sentences = re.split(r'(?:[\r\n]+|(?<=[.!?])\s+)', raw_text)
            for s_idx, s in enumerate(sentences, start=1):
                s_clean = s.strip()
                if len(s_clean) < 18 or len(s_clean) > 300: continue

                c_hash = hashlib.md5(s_clean.lower().encode("utf-8")).hexdigest()
                if c_hash in existing_hashes: continue

                loc = it.get("location") or {}
                triplets = extract_expert_triplets(s_clean, loc)
                if not triplets: continue

                existing_hashes.add(c_hash)
                url = it.get("url") or it.get("webVideoUrl") or ""
                pid = it.get("id") or hashlib.md5((url or s_clean).encode("utf-8")).hexdigest()[:12]
                sub_id = f"{platform}_{pid}_s{s_idx:02d}_{len(master_data) + len(new_records) + 1}"
                pub_time = it.get("createTimeISO") or it.get("published") or datetime.now(timezone.utc).isoformat()
                author_name = it.get("author") or (it.get("authorMeta") or {}).get("name") or f"{platform.capitalize()} Creator"

                loc_info = {
                    "locations": [],
                    "ward": "Chưa xác định",
                    "city": "Hồ Chí Minh",
                    "legacy_district": "TP.HCM"
                }

                rec = {
                    "seq_id": initial_len + len(new_records),
                    "id": sub_id,
                    "parent_id": pid,
                    "episode_id": ep_id,
                    "episode_title": ep_id,
                    "crawl_batch": "batch_5_social_multiyear_exceed_10k",
                    "is_new_crawl": True,
                    "source": {
                        "platform": platform,
                        "author": author_name,
                        "url": url
                    },
                    "published_at": pub_time,
                    "content": {
                        "title": s_clean[:80],
                        "text": s_clean
                    },
                    "location": loc_info,
                    "media": {
                        "has_media": bool(it.get("webVideoUrl") or it.get("mediaUrls")),
                        "media_urls": it.get("mediaUrls") or ([it["webVideoUrl"]] if it.get("webVideoUrl") else [])
                    },
                    "aste_triplets": triplets
                }
                resolve_ward_for_record(rec)
                new_records.append(rec)

    print(f"[*] Đã khai thác thêm từ Social Episodes: {len(new_records)} bản ghi thực tế.")
    final_dataset = master_data + new_records

    # Cập nhật seq_id liên tục 0 -> N-1
    for idx in range(len(final_dataset)):
        final_dataset[idx]["seq_id"] = idx

    print(f"[+] TỔNG SỐ BẢN GHI MỚI SAU KHI VƯỢT MỐC 10K: {len(final_dataset)}")

    with open(V3_PATH, "w", encoding="utf-8") as fp:
        json.dump(final_dataset, fp, ensure_ascii=False, indent=2)

    print(f"✅ Đã ghi đè thành công tập dữ liệu Master: {V3_PATH}")

if __name__ == "__main__":
    append_social_records()
