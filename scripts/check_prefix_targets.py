import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

prefixes = ['Tại TP. Hồ Chí Minh , ', 'Tại TPHCM , ', 'Tại TP.HCM , ']

body_targets = []
prefix_targets = []
both = []
neither = []

for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip_str = line.split('####')
    triplets = ast.literal_eval(trip_str)
    
    pfx_len = 0
    if text.startswith('Tại TP. Hồ Chí Minh , '):
        pfx_len = 5 # ['Tại', 'TP.', 'Hồ', 'Chí', 'Minh', ','] -> 6 tokens! Wait!
    elif text.startswith('Tại TPHCM , '):
        pfx_len = 3 # ['Tại', 'TPHCM', ','] -> 3 tokens!
    else:
        continue
        
    tokens = text.split()
    # Check how many tokens the prefix actually has:
    # "Tại TP. Hồ Chí Minh ," -> tokens are:
    # 'Tại', 'TP.', 'Hồ', 'Chí', 'Minh', ',' -> 6 tokens!
    # "Tại TPHCM ," -> tokens are:
    # 'Tại', 'TPHCM', ',' -> 3 tokens!
    if text.startswith('Tại TP. Hồ Chí Minh , '):
        pfx_token_count = 6
    else:
        pfx_token_count = 3
        
    has_body = False
    has_pfx = False
    for asp, opi, pol in triplets:
        if all(i < pfx_token_count for i in asp):
            has_pfx = True
        else:
            has_body = True
            
    if has_body and has_pfx:
        both.append((rec_num, text, triplets))
    elif has_body:
        body_targets.append((rec_num, text, triplets))
    elif has_pfx:
        prefix_targets.append((rec_num, text, triplets))
    else:
        neither.append((rec_num, text, triplets))

print(f"Prefix records targeting ONLY body entities: {len(body_targets)}")
print(f"Prefix records targeting ONLY prefix: {len(prefix_targets)}")
print(f"Prefix records targeting BOTH prefix and body: {len(both)}")
print(f"Neither (empty/rejected): {len(neither)}")
