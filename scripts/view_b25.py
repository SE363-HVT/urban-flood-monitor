# -*- coding: utf-8 -*-
from analyze_batch_21_25 import records

recs_25 = [r for r in records if 2401 <= r['id'] <= 2500]
print(f"Tổng số reject trong Lô 25: {len(recs_25)}")

for i, r in enumerate(recs_25):
    print(f"\n[{i+1}] REC {r['id']}")
    print(f"  P3: {r['p3_text']}")
    print(f"  TRIP: {r['ma_triplets']}")
