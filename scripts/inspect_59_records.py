import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

recs_to_test = [
    1, 2, 16, 27, 40, 41, 43, 46, 47, 49, 93, 99, 100, 124, 139, 144, 359, 375, 393, 460,
    513, 521, 851, 862, 880, 897, 917, 1000, 1017, 1019, 1040, 1099, 1109, 1129, 1150, 1160,
    1166, 1218, 1227, 1256, 1277, 1349, 1387, 1430, 1432, 1445, 1459, 1527, 1568, 1570, 1594,
    1626, 1648, 1812, 1851, 1889, 1892, 1944, 1966
]

for r in recs_to_test:
    idx = r - 1
    text, trip = lines[idx].split('####')
    triplets = ast.literal_eval(trip)
    tokens = text.split()
    asps = [" ".join(tokens[i] for i in a) for a, o, p in triplets]
    print(f"Rec {r:4d}: Asps={asps} | TEXT={text[:90]}...")
