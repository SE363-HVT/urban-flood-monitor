import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

# Check if any triplet actually targeted [1, 2, 3, 4] or [1] when a specific street was present
true_fallback_misuse = []
for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip_str = line.split('####')
    triplets = ast.literal_eval(trip_str)
    
    # check if prefix aspect is in triplets
    has_fallback_aspect = False
    for asp, opi, pol in triplets:
        if text.startswith('Tại TP. Hồ Chí Minh , ') and asp == [1, 2, 3, 4]:
            has_fallback_aspect = True
        elif text.startswith('Tại TPHCM , ') and asp == [1]:
            has_fallback_aspect = True
            
    if has_fallback_aspect:
        # check if there's a specific street/bridge/district in the body
        body = text.split(' , ', 1)[1] if ' , ' in text else text
        # check if body has street/bridge
        if re.search(r'\b(đường|cầu|hẻm|quốc lộ|ngã tư|chợ)\s+[A-ZÀ-Ỹ0-9]', body):
            true_fallback_misuse.append((rec_num, text, triplets))

print(f"Số records có gán nhãn fallback [1] hoặc [1, 2, 3, 4] dù trong câu có tên đường cụ thể: {len(true_fallback_misuse)}")
for r, t, tr in true_fallback_misuse:
    print(f"Rec {r}: {t}")
    print(f"  Triplets: {tr}\n")
