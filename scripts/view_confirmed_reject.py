# -*- coding: utf-8 -*-
from categorize_strict import confirmed_reject

print(f"Danh sách {len(confirmed_reject)} records Confirmed REJECT:")
for i, (r, reason, detail) in enumerate(confirmed_reject):
    print(f"\n[{i+1}] REC {r['rec_id']} | Reason: {reason} | Detail: {detail}")
    print(f"  P3: {r['p3_text'][:120]}")
    print(f"  MA: {r['master_text'][:120]}")
