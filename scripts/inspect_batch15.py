import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

print("=== DEEP INSPECTION FOR BATCH 15 (Lines 1401 - 1500) ===")
for i in range(1400, 1500):
    text, trip_str = lines[i].split('####')
    tokens = text.split()
    trips = ast.literal_eval(trip_str)
    
    # Check prefixes
    for asp, opi, pol in trips:
        start = asp[0]
        if start > 0 and tokens[start-1].lower() in ['đường', 'phường', 'cầu', 'hẻm', 'quận', 'kênh', 'sông', 'tuyến']:
            asp_w = ' '.join(tokens[j] for j in asp)
            print(f'Line {i+1} PREFIX: "{tokens[start-1]}" before [{asp_w}] (asp={asp})')

    # Check bare tidal
    for asp, opi, pol in trips:
        asp_w = ' '.join(tokens[j] for j in asp)
        if ('triều' in asp_w.lower() or 'đỉnh' in asp_w.lower()) and not any(loc in asp_w for loc in ['TPHCM', 'TP.HCM', 'Sài Gòn', 'SG']):
            print(f'Line {i+1} BARE TIDAL: [{asp_w}] | opi=[{" ".join(tokens[j] for j in opi)}] | pol={pol}')

    # Check out-of-scope provinces
    lower_text = text.lower()
    for prov in ['hà nội', 'cần thơ', 'đà nẵng', 'vĩnh long', 'đồng nai', 'cà mau', 'thanh hóa', 'quảng ninh', 'hải phòng', 'nha trang', 'huế', 'đà lạt']:
        if prov in lower_text:
            print(f'Line {i+1} OUT_OF_SCOPE_PROVINCE ({prov}): {text[:70]}...')

    # Check multi-level dup
    asp_list = [(asp, ' '.join(tokens[j] for j in asp), opi, pol) for asp, opi, pol in trips]
    for a1, a1_w, o1, p1 in asp_list:
        for a2, a2_w, o2, p2 in asp_list:
            if a1 != a2 and o1 == o2:
                if any(broad in a1_w.lower() for broad in ['quận', 'huyện', 'tphcm', 'tp. hcm', 'tp hồ chí minh', 'bình thạnh']) and not any(broad in a2_w.lower() for broad in ['quận', 'huyện', 'tphcm', 'tp. hcm']):
                    print(f'Line {i+1} MULTI_LEVEL_DUP: broad=[{a1_w}] vs specific=[{a2_w}]')

    # Check polarity
    for asp, opi, pol in trips:
        opi_w = ' '.join(tokens[j] for j in opi)
        if any(w in opi_w.lower() for w in ['dự báo', 'nguy cơ', 'khả năng']) and pol != 'NEU':
            print(f'Line {i+1} POL CHECK (should be NEU?): pol={pol} | asp=[{" ".join(tokens[j] for j in asp)}] | opi=[{opi_w}]')
