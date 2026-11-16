# -*- coding: utf-8 -*-
from inspect_batch_1_4 import batch_1_4

for i, r in enumerate(batch_1_4[:12]):
    print(f"\n[{i+1}] REC {r['rec_id']}")
    print(f"P3: {r['p3_text']}")
    print(f"TRIP: {r['master_triplets']}")
