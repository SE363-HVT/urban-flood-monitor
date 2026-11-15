import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.rstrip('\r\n') for line in f]

for i in range(1880, 1930):
    line = lines[i]
    parts = line.split('####')
    text = parts[0].strip()
    triplets = ast.literal_eval(parts[1].strip()) if len(parts) > 1 and parts[1].strip() else []
    tokens = text.split()
    print(f"=== REC {i+1} (idx {i}) ===")
    token_str = " ".join([f"{idx}:{t}" for idx, t in enumerate(tokens)])
    print(f"TOKENS: {token_str}")
    print(f"CURRENT TRIPLETS: {triplets}")
    for t in triplets:
        asp = " ".join(tokens[idx] for idx in t[0]) if t[0] else ""
        op = " ".join(tokens[idx] for idx in t[1]) if t[1] else ""
        print(f"  [{t[0]}] '{asp}' | [{t[1]}] '{op}' | {t[2]}")
