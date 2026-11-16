# -*- coding: utf-8 -*-
from view_b24 import recs_24

for i, r in enumerate(recs_24[:15]):
    print(f"\n[{i+1}] REC {r['id']}")
    print(f"  P3: {r['p3_text']}")
    print(f"  TRIP: {r['ma_triplets']}")
