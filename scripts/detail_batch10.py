import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

target_lines = [911, 912, 913, 914, 920, 921, 924, 944, 946, 951, 960, 964, 993, 997]

for line_no in target_lines:
    idx = line_no - 1
    text, trip_str = lines[idx].split('####')
    tokens = text.split()
    trips = ast.literal_eval(trip_str)
    print(f"=== Line {line_no} ===")
    print("TEXT:", text)
    for asp, opi, pol in trips:
        print("  ", asp, [tokens[i] for i in asp], "||", opi, [tokens[i] for i in opi], pol)
