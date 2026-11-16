# -*- coding: utf-8 -*-
from analyze_batch_21_25 import records

recs_21_23 = [r for r in records if 2001 <= r['id'] <= 2300]
print(f"Tổng số reject trong Lô 21-23: {len(recs_21_23)}")

for i, r in enumerate(recs_21_23):
    print(f"\n[{i+1}] REC {r['id']}")
    print(f"  P3: {r['p3_text']}")
    print(f"  MA: {r['ma_text']}")
    print(f"  TRIP: {r['ma_triplets']}")
