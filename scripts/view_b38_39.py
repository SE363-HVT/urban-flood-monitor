# -*- coding: utf-8 -*-
from analyze_batch_36_39 import records

recs_38_39 = [r for r in records if 3701 <= r['id'] <= 3875]
print(f"Tổng số reject trong Lô 38-39: {len(recs_38_39)}")

for i, r in enumerate(recs_38_39):
    print(f"\n[{i+1}] REC {r['id']}")
    print(f"  P3: {r['p3_text']}")
    print(f"  TRIP: {r['ma_triplets']}")
