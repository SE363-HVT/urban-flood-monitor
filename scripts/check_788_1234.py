import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

# Let's inspect Rec 788 and Rec 1234
for r in [788, 1234]:
    idx = r - 1
    t, tr = lines[idx].split('####')
    print(f"Rec {r}: {t}")
    print(f"  Triplets: {tr}")
