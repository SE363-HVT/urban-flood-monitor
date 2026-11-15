import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

for i in range(330, 358):
    rec = i + 1
    line = lines[i]
    if '####' not in line:
        continue
    text, trips = line.split('####')
    triplets = ast.literal_eval(trips)
    tokens = text.split()
    print(f"=== REC {rec} (idx {i}) ===")
    print(f"TEXT: {text}")
    if not triplets:
        print("   REJECT (####[])")
    for asp, opi, pol in triplets:
        a_words = [tokens[k] for k in asp] if asp else []
        o_words = [tokens[k] for k in opi] if opi else []
        print(f"   Asp: '{' '.join(a_words)}' ({asp}) | Opi: '{' '.join(o_words)}' ({opi}) | Pol: {pol}")
