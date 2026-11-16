# -*- coding: utf-8 -*-
from build_phase3_batch27 import batch27_data

targets = [2644, 2659, 2691]
for idx, (text, trips) in enumerate(batch27_data, 2601):
    if idx in targets:
        print(f"=== REC {idx} ===")
        toks = text.split()
        for i, t in enumerate(toks):
            print(f"  {i}: {t}")
        print("Triplets:", trips)
