# -*- coding: utf-8 -*-
from build_phase3_batch27 import batch27_data

targets = [2606, 2610, 2614, 2615, 2620, 2623, 2624, 2640, 2653, 2663, 2686, 2694]
for idx, (text, trips) in enumerate(batch27_data, 2601):
    if idx in targets:
        print(f"=== REC {idx} ===")
        toks = text.split()
        for i, t in enumerate(toks):
            print(f"  {i}: {t}")
        print("Triplets:", trips)
