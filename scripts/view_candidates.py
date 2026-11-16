# -*- coding: utf-8 -*-
from classify_859_detailed import candidate_recs

print(f"Viewing first 25 candidate records:")
for i, r in enumerate(candidate_recs[:25]):
    print(f"\n--- [{i+1}] REC {r['rec_id']} ---")
    print(f"P3:     {r['p3_text']}")
    print(f"MASTER: {r['master_text']}")
    print(f"TRIP:   {r['master_triplets']}")
