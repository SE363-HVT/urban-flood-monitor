import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

# Test shifting for the 59 records
recs_to_test = [
    1, 2, 16, 27, 40, 41, 43, 46, 47, 49, 93, 99, 100, 124, 139, 144, 359, 375, 393, 460,
    513, 521, 851, 862, 880, 897, 917, 1000, 1017, 1019, 1040, 1099, 1109, 1129, 1150, 1160,
    1166, 1218, 1227, 1256, 1277, 1349, 1387, 1430, 1432, 1445, 1459, 1527, 1568, 1570, 1594,
    1626, 1648, 1812, 1851, 1889, 1892, 1944, 1966
]

for rec_num in recs_to_test:
    idx = rec_num - 1
    line = lines[idx]
    text, trip_str = line.split('####')
    triplets = ast.literal_eval(trip_str)
    
    orig_tokens = text.split()
    shift = 0
    if text.startswith('Tại TP. Hồ Chí Minh , '):
        pfx = 'Tại TP. Hồ Chí Minh , '
        shift = 6
    elif text.startswith('Tại TPHCM , '):
        pfx = 'Tại TPHCM , '
        shift = 3
    else:
        print(f"Rec {rec_num}: Unknown prefix!")
        continue
        
    new_text = text[len(pfx):]
    new_tokens = new_text.split()
    
    # Check that new_tokens == orig_tokens[shift:]
    assert new_tokens == orig_tokens[shift:], f"Token mismatch at Rec {rec_num}!"
    
    # Shift triplets
    new_triplets = []
    for asp, opi, pol in triplets:
        # If aspect was on prefix itself:
        if all(i < shift for i in asp):
            # Check what this aspect was
            # e.g. at Rec 375, 393, 513
            pass
        else:
            new_asp = [i - shift for i in asp]
            new_opi = [i - shift for i in opi]
            new_triplets.append((new_asp, new_opi, pol))
            
            # verify text matches
            orig_asp_text = " ".join(orig_tokens[i] for i in asp)
            new_asp_text = " ".join(new_tokens[i] for i in new_asp)
            orig_opi_text = " ".join(orig_tokens[i] for i in opi)
            new_opi_text = " ".join(new_tokens[i] for i in new_opi)
            
            assert orig_asp_text == new_asp_text, f"Aspect text mismatch at Rec {rec_num}!"
            assert orig_opi_text == new_opi_text, f"Opinion text mismatch at Rec {rec_num}!"

print("ALL 59 records shifted perfectly with 100% text match for body triplets!")
