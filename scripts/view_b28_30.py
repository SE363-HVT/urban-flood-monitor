# -*- coding: utf-8 -*-
from analyze_batch_26_30 import records

recs_28_30 = [r for r in records if 2701 <= r['id'] <= 3000]
print(f"Tổng số reject trong Lô 28-30: {len(recs_28_30)}")

for i, r in enumerate(recs_28_30):
    print(f"\n[{i+1}] REC {r['id']}")
    print(f"  P3: {r['p3_text']}")
    print(f"  TRIP: {r['ma_triplets']}")
