# -*- coding: utf-8 -*-
from view_all_batch_5_8 import records

for i, r in enumerate(records[:26]):
    print(f"[{i+1}] REC {r['id']}")
    print(f"  P3:   {r['p3']}")
    print(f"  TRIP: {r['trip']}\n")
