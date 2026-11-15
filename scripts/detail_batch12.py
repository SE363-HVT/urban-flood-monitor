import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

for line_no in [1108, 1154, 1155, 1166]:
    idx = line_no - 1
    text, trip_str = lines[idx].split('####')
    tokens = text.split()
    trips = ast.literal_eval(trip_str)
    print(f"=== Line {line_no} ===")
    print("TEXT:", text)
    for asp, opi, pol in trips:
        print("  ", asp, [tokens[i] for i in asp], "||", opi, [tokens[i] for i in opi], pol)
