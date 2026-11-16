# -*- coding: utf-8 -*-
from analyze_batch_36_39 import records

recs_36_37 = [r for r in records if 3501 <= r['id'] <= 3700]
print(f"Tổng số reject trong Lô 36-37: {len(recs_36_37)}")

for i, r in enumerate(recs_36_37):
    print(f"\n[{i+1}] REC {r['id']}")
    print(f"  P3: {r['p3_text']}")
    print(f"  TRIP: {r['ma_triplets']}")
