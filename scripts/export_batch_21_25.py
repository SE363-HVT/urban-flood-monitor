# -*- coding: utf-8 -*-
with open('data/validate_label/thuan/phase3.txt', 'r', encoding='utf-8') as f:
    p3_lines = [l.strip() for l in f]

with open('data/processed/aste_v2_format/master_10k_triplets.txt', 'r', encoding='utf-8') as f:
    master_all = [l.strip() for l in f]

# Phase 3 là lines 2501 - 6375 (0-indexed: 2500 - 6375)
p3_master = master_all[2500:6375]

# Lọc các reject trong Lô 21 - 25 (Recs 2001 - 2500)
batch_21_25_rejects = []
for i in range(2000, 2500):
    line = p3_lines[i]
    if line.endswith('####[]'):
        rec_id = i + 1
        batch_21_25_rejects.append({
            'rec_id': rec_id,
            'p3_line': line,
            'master_line': p3_master[i]
        })

print(f"Tổng số reject trong Lô 21-25 (Recs 2001-2500): {len(batch_21_25_rejects)}")

with open('scratch_audit_batch_21_25.txt', 'w', encoding='utf-8') as f:
    for r in batch_21_25_rejects:
        f.write(f"=== REC {r['rec_id']} ===\n")
        f.write(f"P3:  {r['p3_line']}\n")
        f.write(f"MA:  {r['master_line']}\n\n")

print("Đã xuất vào scratch_audit_batch_21_25.txt")
