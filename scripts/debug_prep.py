# -*- coding: utf-8 -*-
from build_phase3_batch26 import batch26_data

targets = [2510, 2527, 2580, 2594]
for idx, (text, trips) in enumerate(batch26_data, 2501):
    if idx in targets:
        print(f"=== REC {idx} ===")
        toks = text.split()
        for i, t in enumerate(toks):
            print(f"  {i}: {t}")
        print("Triplets:", trips)
