import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.rstrip('\r\n') for line in f]

for i in range(1980, len(lines)):
    line = lines[i]
    parts = line.split('####')
    text = parts[0].strip()
    trip_str = parts[1].strip() if len(parts) > 1 else '[]'
    triplets = ast.literal_eval(trip_str)
    tokens = text.split()
    print(f"\n==================== REC {i+1} (idx {i}) ====================")
    print(f"TEXT: {text}")
    print(f"TRIPLETS: {triplets}")
    for t in triplets:
        asp = " ".join(tokens[idx] for idx in t[0]) if t[0] else "NULL"
        op = " ".join(tokens[idx] for idx in t[1]) if t[1] else "NULL"
        print(f"  --> Asp [{t[0]}]: '{asp}' | Op [{t[1]}]: '{op}' | Pol: {t[2]}")
