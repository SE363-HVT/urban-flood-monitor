import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

recs = [359, 375, 393, 460, 513, 521, 788, 851, 862, 880, 897, 917, 1000, 1017, 1019, 1040]

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
