# -*- coding: utf-8 -*-
with open('scratch_all_859_rejected.txt', 'r', encoding='utf-8') as f:
    content = f.read()

entries = content.split('=== REC ')
print(f"Total entries: {len(entries) - 1}")
for entry in entries[1:4]:
    print("--- ENTRY ---")
    print(entry[:400])
