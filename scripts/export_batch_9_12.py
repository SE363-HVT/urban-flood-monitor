# -*- coding: utf-8 -*-
from analyze_all_859 import parse_859

recs = parse_859()
batch_9_12 = [r for r in recs if 801 <= r['rec_id'] <= 1200]
print(f"Tổng số reject trong Lô 9-12 (Recs 801-1200): {len(batch_9_12)}")

with open('scratch_audit_batch_9_12.txt', 'w', encoding='utf-8') as f:
    for r in batch_9_12:
        f.write(f"=== REC {r['rec_id']} ===\n")
        f.write(f"P3:  {r['p3_text']}\n")
        f.write(f"MA:  {r['master_text']}\n")
        f.write(f"TRIP:{r['master_triplets']}\n\n")

print("Đã xuất vào scratch_audit_batch_9_12.txt")
