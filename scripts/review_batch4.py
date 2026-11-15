import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

recs = [1459, 1527, 1568, 1570, 1594, 1616, 1626, 1648, 1669, 1812, 1851, 1889, 1892, 1944, 1961, 1966]

for r in recs:
    idx = r - 1
    t, tr = lines[idx].split('####')
    toks = t.split()
    triplets = ast.literal_eval(tr)
    print(f"=== Record {r} ===")
    print("TEXT:", t)
    print("TOKENS:", " ".join(f"[{i}:{tk}]" for i, tk in enumerate(toks)))
    print("TRIPLETS:", triplets)
    decoded = []
    for a, o, p in triplets:
        decoded.append((" ".join(toks[i] for i in a), " ".join(toks[i] for i in o), p))
    print("DECODED:", decoded)
    print()
