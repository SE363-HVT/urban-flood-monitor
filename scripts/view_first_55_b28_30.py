# -*- coding: utf-8 -*-
from view_b28_30 import recs_28_30

for i, r in enumerate(recs_28_30[:55]):
    print(f"\n[{i+1}] REC {r['id']}")
    print(f"  P3: {r['p3_text']}")
    print(f"  TRIP: {r['ma_triplets']}")
