import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/redundant_audit_report.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("CAT 1 (Double phrases):", len(d['cat1_doubles']))
for item in d['cat1_doubles']:
    print(f"Rec {item['rec']}: [{item['match']}] -> {item['text'][:100]}")

print("\nCAT 2 (Multi 'ở TPHCM'):", len(d['cat2_multi']))
for item in d['cat2_multi']:
    print(f"Rec {item['rec']}: ({item['count']} times) -> {item['text'][:100]}")
