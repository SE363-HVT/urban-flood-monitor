# -*- coding: utf-8 -*-
from analyze_batch_21_25 import records

recs_24 = [r for r in records if 2301 <= r['id'] <= 2400]
print(f"Tổng số reject trong Lô 24: {len(recs_24)}")

for i, r in enumerate(recs_24):
    print(f"\n[{i+1}] REC {r['id']}")
    print(f"  P3: {r['p3_text']}")
    print(f"  TRIP: {r['ma_triplets']}")
