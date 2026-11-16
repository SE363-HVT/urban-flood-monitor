# -*- coding: utf-8 -*-
from analyze_all_859 import parse_859

recs = parse_859()

batch_map = {}
for r in recs:
    rec_id = r['rec_id']
    batch_idx = (rec_id - 1) // 100 + 1
    batch_map[batch_idx] = batch_map.get(batch_idx, []) + [r]

print("Phân bố 859 records reject theo 39 lô của Phase 3:")
for b in range(1, 40):
    count = len(batch_map.get(b, []))
    ids = [r['rec_id'] for r in batch_map.get(b, [])]
    if count > 0:
        print(f"Lô {b:2d} (Recs {(b-1)*100+1:4d} - {min(b*100, 3875):4d}): {count:2d} rejects -> IDs: {ids[:5]} ... {ids[-2:] if count > 5 else ''}")
    else:
        print(f"Lô {b:2d} (Recs {(b-1)*100+1:4d} - {min(b*100, 3875):4d}):  0 rejects")
