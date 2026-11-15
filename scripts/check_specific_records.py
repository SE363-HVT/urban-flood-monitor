import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

for r in [16, 43, 93, 897, 1040, 1616, 1659, 1669, 1671]:
    idx = r - 1
    t, tr = lines[idx].split('####')
    toks = t.split()
    triplets = ast.literal_eval(tr)
    print(f"=== Record {r} ===")
    print("TEXT:", t)
    print("TOKENS:", " ".join(f"[{i}:{tk}]" for i, tk in enumerate(toks)))
    print("TRIPLETS:", triplets)
    decoded = [(" ".join(toks[i] for i in a), " ".join(toks[i] for i in o), p) for a, o, p in triplets]
    print("DECODED:", decoded)
    print()
