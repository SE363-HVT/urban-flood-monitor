# -*- coding: utf-8 -*-
import ast, re
from span_helper import make_triplet

# Đọc scratch_audit_batch_1_12.txt
with open('scratch_audit_batch_1_12.txt', 'r', encoding='utf-8') as f:
    content = f.read()

entries = content.split('=== REC ')
records = []
for entry in entries[1:]:
    lines = entry.strip().split('\n')
    rec_id = int(lines[0].split('===')[0].strip())
    p3 = ""
    ma = ""
    trip = []
    for l in lines[1:]:
        if l.startswith('P3:'):
            p3 = l[3:].strip()
        elif l.startswith('MA:'):
            ma = l[3:].strip()
        elif l.startswith('TRIP:'):
            try:
                trip = ast.literal_eval(l[5:].strip())
            except:
                trip = []
    records.append({'id': rec_id, 'p3': p3, 'ma': ma, 'trip': trip})

print(f"Tổng số records Lô 1-12: {len(records)}")

# Phân loại sơ bộ ngữ cảnh
# Xem xét từng record
for r in records:
    text = r['p3']
    text_lower = text.lower()
    
    # Kiểm tra tỉnh ngoài
    # ...
