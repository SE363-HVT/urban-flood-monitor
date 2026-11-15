import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.rstrip('\r\n') for line in f]

for i in range(1880, 1890):
    line = lines[i]
    parts = line.split('####')
    text = parts[0].strip()
    triplets = ast.literal_eval(parts[1].strip())
    tokens = text.split()
    print(f"REC {i+1} (idx {i}):")
    print(f"  TEXT: {text}")
    print(f"  TOKENS: {list(enumerate(tokens))}")
    print(f"  TRIPLETS: {triplets}")
    for t in triplets:
        print(f"    {' '.join(tokens[x] for x in t[0])} | {' '.join(tokens[x] for x in t[1])} | {t[2]}")
