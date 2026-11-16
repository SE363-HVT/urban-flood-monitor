# -*- coding: utf-8 -*-
from view_all_batch_9_12 import records

for i, r in enumerate(records[:46]):
    print(f"[{i+1}] REC {r['id']}")
    print(f"  P3:   {r['p3']}")
    print(f"  TRIP: {r['trip']}\n")
