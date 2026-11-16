# -*- coding: utf-8 -*-
from build_phase3_batch29 import batch29_data

targets = [2826, 2855, 2880, 2881, 2885]
for idx, (text, trips) in enumerate(batch29_data, 2801):
    if idx in targets:
        print(f"=== REC {idx} ===")
        toks = text.split()
        for i, t in enumerate(toks):
            print(f"  {i}: {t}")
        print("Triplets:", trips)
