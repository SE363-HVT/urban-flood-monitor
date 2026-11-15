import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        text, trip_str = line.strip().split('####')
        text_lower = text.lower()
        if 'triều cường ở tphcm' in text_lower:
            trips = ast.literal_eval(trip_str)
            tokens = text.split()
            has_tc_asp = any('triều cường ở tphcm' in ' '.join(tokens[x] for x in t[0]).lower() for t in trips)
            if not has_tc_asp:
                print(f"Line {idx+1}: {text[:80]}...")
                print(f"  Current Triplets: {trips}")
                for t in trips:
                    print(f"    Asp: '{' '.join(tokens[x] for x in t[0])}' | Op: '{' '.join(tokens[x] for x in t[1])}' | {t[2]}")
