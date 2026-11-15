import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

# 1. First, check the 4 double glitch records:
print("=== 4 DOUBLE GLITCH RECORDS ===")
for r in [1616, 1669, 1892, 1961]:
    idx = r - 1
    t, tr = lines[idx].split('####')
    print(f"Rec {r}: {t}")
    print(f"  Triplets: {tr}")
