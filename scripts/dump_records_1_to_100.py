import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

recs_first = [1, 2, 16, 27, 40, 41, 43, 46, 47, 49, 93, 99, 100]

for r in recs_first:
    idx = r - 1
    t, tr = lines[idx].split('####')
    toks = t.split()
    print(f"=== Record {r} ===")
    tok_str = " ".join(f"[{i}:{tk}]" for i, tk in enumerate(toks))
    print(tok_str)
    print(f"Current triplets: {tr}\n")
