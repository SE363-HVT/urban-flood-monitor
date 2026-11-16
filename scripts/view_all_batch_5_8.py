# -*- coding: utf-8 -*-
import ast

with open('scratch_audit_batch_5_8.txt', 'r', encoding='utf-8') as f:
    text = f.read()

entries = text.split('=== REC ')
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

print(f"Tổng số records Lô 5-8: {len(records)}")

for i, r in enumerate(records):
    print(f"\n[{i+1}] REC {r['id']}")
    print(f"  P3:   {r['p3']}")
    print(f"  TRIP: {r['trip']}")
