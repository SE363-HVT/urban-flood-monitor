import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

keywords = ['bình dương', 'dĩ an', 'thuận an', 'thủ dầu một', 'tân uyên', 'bến cát', 'vsip', 'vũng tàu', 'bà rịa']

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        text, trip_str = line.strip().split('####')
        text_lower = text.lower()
        if any(kw in text_lower for kw in keywords):
            trips = ast.literal_eval(trip_str)
            tokens = text.split()
            print(f"Line {idx+1}: {text[:80]}...")
            print(f"  Triplets: {trips}")
            for t in trips:
                print(f"    Asp: '{' '.join(tokens[x] for x in t[0])}' | Op: '{' '.join(tokens[x] for x in t[1])}' | Pol: {t[2]}")
