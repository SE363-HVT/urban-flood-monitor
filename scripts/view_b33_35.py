# -*- coding: utf-8 -*-
from analyze_batch_31_35 import records

recs_33_35 = [r for r in records if 3201 <= r['id'] <= 3500]
print(f"Tổng số reject trong Lô 33-35: {len(recs_33_35)}")

for i, r in enumerate(recs_33_35):
    print(f"\n[{i+1}] REC {r['id']}")
    print(f"  P3: {r['p3_text']}")
    print(f"  TRIP: {r['ma_triplets']}")
