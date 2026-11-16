# -*- coding: utf-8 -*-
from analyze_all_859 import parse_859

recs = parse_859()

# Lọc các records thuộc Lô 1 đến Lô 12 (rec_id <= 1200)
batch_1_12_recs = [r for r in recs if r['rec_id'] <= 1200]
print(f"Tổng số reject trong Lô 1 - 12: {len(batch_1_12_recs)}")

with open('scratch_audit_batch_1_12.txt', 'w', encoding='utf-8') as f:
    for r in batch_1_12_recs:
        f.write(f"=== REC {r['rec_id']} ===\n")
        f.write(f"P3:  {r['p3_text']}\n")
        f.write(f"MA:  {r['master_text']}\n")
        f.write(f"TRIP:{r['master_triplets']}\n\n")

print("Đã xuất vào scratch_audit_batch_1_12.txt")
