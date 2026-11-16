# -*- coding: utf-8 -*-
from analyze_batch_26_30 import records

recs_26_27 = [r for r in records if 2501 <= r['id'] <= 2700]
print(f"Tổng số reject trong Lô 26-27: {len(recs_26_27)}")

for i, r in enumerate(recs_26_27):
    print(f"\n[{i+1}] REC {r['id']}")
    print(f"  P3: {r['p3_text']}")
    print(f"  TRIP: {r['ma_triplets']}")
