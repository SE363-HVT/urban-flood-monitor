import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

print("=== INSPECTION FOR BATCH 5 (Lines 401 - 500) ===")
for i in range(400, 500):
    text, trip_str = lines[i].split('####')
    tokens = text.split()
    trips = ast.literal_eval(trip_str)
    
    # Check prefixes
    for asp, opi, pol in trips:
        start = asp[0]
        if start > 0 and tokens[start-1].lower() in ['đường', 'phường', 'cầu', 'hẻm', 'quận', 'kênh', 'sông', 'tuyến']:
            asp_w = ' '.join(tokens[j] for j in asp)
            # check if the word before is actually part of name like "đường Trần Xuân Soạn"
            print(f'Line {i+1} PREFIX: "{tokens[start-1]}" before [{asp_w}] (asp={asp})')

    # Check bare tidal
    for asp, opi, pol in trips:
        asp_w = ' '.join(tokens[j] for j in asp)
        if ('triều' in asp_w.lower() or 'đỉnh' in asp_w.lower()) and not any(loc in asp_w for loc in ['TPHCM', 'TP.HCM', 'Sài Gòn', 'SG']):
            print(f'Line {i+1} BARE TIDAL: [{asp_w}]')

    # Check opinion boundaries
    for asp, opi, pol in trips:
        if tokens[opi[0]] in [',', '.', ';', ':', '!', '?'] or tokens[opi[-1]] in [',', '.', ';', ':', '!', '?']:
            print(f'Line {i+1} PUNCT IN OPI: "{tokens[opi[0]]}" .. "{tokens[opi[-1]]}"')
