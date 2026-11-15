import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

target_lines = [718, 719, 722, 723, 734, 737, 742, 748, 749, 751, 752, 753, 756, 762, 769, 778, 779, 783, 784, 786, 788, 797, 798, 799]

for line_no in target_lines:
    idx = line_no - 1
    text, trip_str = lines[idx].split('####')
    tokens = text.split()
    trips = ast.literal_eval(trip_str)
    print(f"=== Line {line_no} ===")
    print("TEXT:", text)
    for asp, opi, pol in trips:
        print("  ", asp, [tokens[i] for i in asp], "||", opi, [tokens[i] for i in opi], pol)
