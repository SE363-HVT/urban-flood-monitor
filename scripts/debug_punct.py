# -*- coding: utf-8 -*-
from build_phase3_batch25 import batch25_data

targets = [2413, 2432, 2433, 2439, 2444, 2470, 2494]
for idx, (text, trips) in enumerate(batch25_data, 2401):
    if idx in targets:
        print(f"=== REC {idx} ===")
        toks = text.split()
        for i, t in enumerate(toks):
            print(f"  {i}: {t}")
        print("Triplets:", trips)
