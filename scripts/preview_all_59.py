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
    
    if text.startswith('Tại TP. Hồ Chí Minh , '):
        pfx = 'Tại TP. Hồ Chí Minh , '
        shift = 6
    elif text.startswith('Tại TPHCM , '):
        pfx = 'Tại TPHCM , '
        shift = 3
    else:
        continue
        
    new_text = text[len(pfx):]
    new_tokens = new_text.split()
    
    new_triplets = []
    for asp, opi, pol in triplets:
        if all(i < shift for i in asp):
            # aspect was on prefix
            # check if there's an aspect to keep
            continue
        new_asp = [i - shift for i in asp]
        new_opi = [i - shift for i in opi]
        new_triplets.append((new_asp, new_opi, pol))
        
    # print decoded
    decoded = []
    for a, o, p in new_triplets:
        a_txt = " ".join(new_tokens[i] for i in a)
        o_txt = " ".join(new_tokens[i] for i in o)
        decoded.append((a_txt, o_txt, p))
        
    print(f"Rec {r:4d}:")
    print(f"  NEW TEXT: {new_text[:80]}...")
    print(f"  DECODED : {decoded}\n")
