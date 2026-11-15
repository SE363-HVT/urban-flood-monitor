import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

recs_body_target = []
for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip_str = line.split('####')
    triplets = ast.literal_eval(trip_str)
    
    if not (text.startswith('Tại TP. Hồ Chí Minh , ') or text.startswith('Tại TPHCM , ')):
        continue
        
    pfx_len = 6 if text.startswith('Tại TP. Hồ Chí Minh , ') else 3
    targets_body = any(any(i >= pfx_len for i in asp) for asp, opi, pol in triplets)
    if targets_body:
        recs_body_target.append((rec_num, text, triplets))

print(f"Tổng cộng có {len(recs_body_target)} records có prefix nhưng triplets trỏ vào thực thể trong body:")
for r, t, tr in recs_body_target:
    tokens = t.split()
    asp_texts = [" ".join(tokens[i] for i in asp) for asp, opi, pol in tr]
    print(f"Rec {r}: Aspects={asp_texts}")
    print(f"  TEXT: {t[:110]}...")
