# -*- coding: utf-8 -*-
from analyze_all_859 import parse_859

recs = parse_859()
batch_1_4 = [r for r in recs if 1 <= r['rec_id'] <= 400]
print(f"Tổng số reject trong Lô 1-4 (Recs 1-400): {len(batch_1_4)}")

for i, r in enumerate(batch_1_4):
    print(f"\n--- [{i+1}] REC {r['rec_id']} ---")
    print(f"P3:  {r['p3_text']}")
    print(f"MA:  {r['master_text']}")
    print(f"TRIP:{r['master_triplets']}")
