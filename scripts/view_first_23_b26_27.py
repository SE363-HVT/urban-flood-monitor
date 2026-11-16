# -*- coding: utf-8 -*-
from view_b26_27 import recs_26_27

for i, r in enumerate(recs_26_27[:23]):
    print(f"\n[{i+1}] REC {r['id']}")
    print(f"  P3: {r['p3_text']}")
    print(f"  TRIP: {r['ma_triplets']}")
