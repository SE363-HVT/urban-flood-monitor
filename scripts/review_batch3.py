import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

recs = [1099, 1109, 1129, 1150, 1160, 1166, 1218, 1227, 1234, 1256, 1277, 1349, 1387, 1430, 1432, 1445]

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
