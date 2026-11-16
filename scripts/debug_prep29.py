# -*- coding: utf-8 -*-
from build_phase3_batch29 import batch29_data

targets = [2814, 2816, 2825]
for idx, (text, trips) in enumerate(batch29_data, 2801):
    if idx in targets:
        print(f"=== REC {idx} ===")
        toks = text.split()
        for i, t in enumerate(toks):
            print(f"  {i}: {t}")
        print("Triplets:", trips)
