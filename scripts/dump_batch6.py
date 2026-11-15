import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

for i in range(500, 600):
    text, trip_str = lines[i].split('####')
    tokens = text.split()
    trips = ast.literal_eval(trip_str)
    print(f"Line {i+1}: {text}")
    for asp, opi, pol in trips:
        asp_w = ' '.join(tokens[j] for j in asp)
        opi_w = ' '.join(tokens[j] for j in opi)
        print(f"    [{asp_w}] ({asp}) | [{opi_w}] ({opi}) | {pol}")
