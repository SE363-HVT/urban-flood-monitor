# -*- coding: utf-8 -*-
from build_phase3_batch28 import batch28_data

targets = [2701, 2724, 2726, 2738, 2744, 2748, 2757, 2763, 2777, 2795]
for idx, (text, trips) in enumerate(batch28_data, 2701):
    if idx in targets:
        print(f"=== REC {idx} ===")
        toks = text.split()
        for i, t in enumerate(toks):
            print(f"  {i}: {t}")
        print("Triplets:", trips)
