# -*- coding: utf-8 -*-
import ast, re

with open('scratch_audit_batch_36_39.txt', 'r', encoding='utf-8') as f:
    text = f.read()

entries = text.split('=== REC ')
records = []
for entry in entries[1:]:
    lines = entry.strip().split('\n')
    rec_id = int(lines[0].split('===')[0].strip())
    p3 = ""
    ma = ""
    for l in lines[1:]:
        if l.startswith('P3:'):
            p3 = l[3:].strip()
        elif l.startswith('MA:'):
            ma = l[3:].strip()
            
    p3_parts = p3.split('####')
    p3_text = p3_parts[0].strip()
    
    ma_parts = ma.split('####')
    ma_text = ma_parts[0].strip()
    ma_triplets = []
    if len(ma_parts) > 1 and ma_parts[1].strip():
        try:
            ma_triplets = ast.literal_eval(ma_parts[1].strip())
        except:
            ma_triplets = []
            
    records.append({
        'id': rec_id,
        'p3_text': p3_text,
        'ma_text': ma_text,
        'ma_triplets': ma_triplets
    })

print(f"Loaded {len(records)} reject records in Batch 36-39.")

# Phân loại sơ bộ
out_provinces = [
    r'\bgia lai\b', r'\bquy nhơn\b', r'\bhà đông\b', r'\bhà nội\b',
    r'\bcần thơ\b', r'\bđà nẵng\b', r'\bhuế\b', r'\bthái lan\b'
]

sample_display = []
for r in records:
    t_lower = r['p3_text'].lower()
    is_out = any(re.search(p, t_lower) for p in out_provinces)
    status = "POTENTIAL_IN_SCOPE"
    if is_out:
        status = "REJECT_OUT_PROVINCE"
    elif len(r['p3_text'].split()) < 5:
        status = "REJECT_TOO_SHORT"
        
    sample_display.append((r['id'], status, r['p3_text'], r['ma_triplets']))

from collections import Counter
counts = Counter([s[1] for s in sample_display])
print("Thống kê phân loại sơ bộ Lô 36-39:")
for k, v in counts.items():
    print(f"  {k}: {v}")

with open('scratch_b36_39_analysis.txt', 'w', encoding='utf-8') as f:
    for s in sample_display:
        f.write(f"REC {s[0]} | {s[1]}\n  P3: {s[2]}\n  MA_TRIP: {s[3]}\n\n")

print("Đã xuất vào scratch_b36_39_analysis.txt")
