# -*- coding: utf-8 -*-
from analyze_all_859 import parse_859

recs = parse_859()
batch_5_8 = [r for r in recs if 401 <= r['rec_id'] <= 800]
print(f"Tổng số reject trong Lô 5-8 (Recs 401-800): {len(batch_5_8)}")

with open('scratch_audit_batch_5_8.txt', 'w', encoding='utf-8') as f:
    for r in batch_5_8:
        f.write(f"=== REC {r['rec_id']} ===\n")
        f.write(f"P3:  {r['p3_text']}\n")
        f.write(f"MA:  {r['master_text']}\n")
        f.write(f"TRIP:{r['master_triplets']}\n\n")

print("Đã xuất vào scratch_audit_batch_5_8.txt")
