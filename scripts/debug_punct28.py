# -*- coding: utf-8 -*-
from build_phase3_batch28 import batch28_data

targets = [2703, 2708, 2733, 2736, 2755, 2764, 2780, 2790]
for idx, (text, trips) in enumerate(batch28_data, 2701):
    if idx in targets:
        print(f"=== REC {idx} ===")
        toks = text.split()
        for i, t in enumerate(toks):
            print(f"  {i}: {t}")
        print("Triplets:", trips)
