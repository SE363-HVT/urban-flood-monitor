# -*- coding: utf-8 -*-
with open('scratch_audit_batch_1_12.txt', 'r', encoding='utf-8') as f:
    text = f.read()

entries = text.split('=== REC ')
for i in range(1, min(31, len(entries))):
    print(f"=== {entries[i].strip()}")
