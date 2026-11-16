# -*- coding: utf-8 -*-
from analyze_batch_31_35 import records

recs_31_32 = [r for r in records if 3001 <= r['id'] <= 3200]
print(f"Tổng số reject trong Lô 31-32: {len(recs_31_32)}")

for i, r in enumerate(recs_31_32):
    print(f"\n[{i+1}] REC {r['id']}")
    print(f"  P3: {r['p3_text']}")
    print(f"  TRIP: {r['ma_triplets']}")
