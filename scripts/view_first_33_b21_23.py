# -*- coding: utf-8 -*-
from view_b21_23 import recs_21_23

for i, r in enumerate(recs_21_23[:33]):
    print(f"\n[{i+1}] REC {r['id']}")
    print(f"  P3: {r['p3_text']}")
    print(f"  TRIP: {r['ma_triplets']}")
