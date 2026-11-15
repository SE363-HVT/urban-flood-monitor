import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

# Let's import the detected list
import detect_redundant_prefixes as drp
from detect_redundant_prefixes import records_with_injected_prefix_and_specific_location

print("=== 22 RECORDS TARGETING PREFIX WITH PLACES IN BODY ===")
for r in records_with_injected_prefix_and_specific_location:
    if not r['triplet_targets_body']:
        print(f"Rec {r['rec_num']}: places={r['places_found']}")
        print(f"  TEXT: {r['text']}")
        print(f"  TRIP: {r['triplets']}\n")
