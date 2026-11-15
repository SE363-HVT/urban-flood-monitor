import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

# Let's inspect specific lines:
target_indices = [400, 401, 402, 404, 408, 409, 420, 423, 424, 425, 429, 430, 432, 444, 449, 452, 456, 463, 474, 475, 478, 479, 483, 484, 488, 490, 491]
for i in target_indices:
    text, trip_str = lines[i].split('####')
    tokens = text.split()
    trips = ast.literal_eval(trip_str)
    print(f"=== Line {i+1} ===")
    print("TEXT:", text)
    for asp, opi, pol in trips:
        asp_w = ' '.join(tokens[j] for j in asp)
        opi_w = ' '.join(tokens[j] for j in opi)
        print(f"  [{asp_w}] ({asp}) | [{opi_w}] ({opi}) | {pol}")
