import sys
from ast import literal_eval
sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f]

batch = lines[1900:2000]
print(f"Total lines in Batch 20: {len(batch)}")

out_of_province_kws = ['hà nội', 'đà nẵng', 'hải phòng', 'cần thơ', 'nha trang', 'huế', 'quảng ninh', 'vinh', 'thanh hóa', 'nghệ an', 'quảng bình', 'quảng trị', 'quảng nam', 'quảng ngãi', 'bình định', 'phú yên', 'khánh hòa', 'ninh thuận', 'bình thuận', 'lâm đồng', 'đà lạt', 'buôn ma thuột', 'đắk lắk', 'gia lai', 'pleiku', 'kon tum', 'hà tĩnh', 'nam định', 'thái bình', 'hải dương', 'bắc ninh', 'vĩnh phúc', 'phú thọ', 'thái nguyên', 'tuyên quang', 'lào cai', 'yên bái', 'hà giang', 'cao bằng', 'lạng sơn', 'bắc kạn', 'hòa bình', 'sơn la', 'điện biên', 'lai châu']

for idx, line in enumerate(batch, 1901):
    parts = line.split('####')
    text = parts[0]
    triplets = literal_eval(parts[1]) if len(parts) > 1 else []
    tokens = text.split()
    t_lower = text.lower()
    
    # 1. Out of province
    for kw in out_of_province_kws:
        if kw in t_lower and kw not in ['xa lộ hà nội']:
            print(f"L{idx} OUT_OF_PROVINCE KW: '{kw}' | triplets={triplets}")

    # 2. Standalone bare tidal
    for a_idx, o_idx, pol in triplets:
        a_words = ' '.join(tokens[i] for i in a_idx).lower()
        if a_words in ['triều cường', 'đỉnh triều', 'triều cao', 'thủy triều']:
            print(f"L{idx} BARE_TIDAL: [{a_words}]")

    # 3. Non-geographic aspects
    for a_idx, o_idx, pol in triplets:
        a_words = ' '.join(tokens[i] for i in a_idx).lower()
        if a_words in ['xe cộ', 'giao thông', 'ô tô', 'xe máy', 'mực nước', 'nước']:
            print(f"L{idx} INVALID_ASPECT: [{a_words}]")

    # 4. Long opinions
    for a_idx, o_idx, pol in triplets:
        if len(o_idx) > 8:
            o_words = ' '.join(tokens[i] for i in o_idx)
            print(f"L{idx} LONG_OPINION ({len(o_idx)}): {o_words}")

    # 5. Missed prefix
    for a_idx, o_idx, pol in triplets:
        a_txt = ' '.join(tokens[i] for i in a_idx)
        min_a = min(a_idx)
        if min_a > 0:
            prev_tok = tokens[min_a - 1].lower()
            if prev_tok in ['đường', 'cầu', 'hẻm', 'ngõ', 'phố', 'đại_lộ', 'xa_lộ', 'rạch', 'kênh'] and prev_tok not in a_txt.lower():
                print(f"L{idx} MISSED_PREFIX: '{tokens[min_a-1]}' before [{a_txt}]")

    # 6. Multi-level dups
    if len(triplets) > 1:
        aspects = [' '.join(tokens[i] for i in a_idx) for a_idx, _, _ in triplets]
        has_broad = any(a in ['TP.HCM', 'TPHCM', 'TP. HCM', 'TP . HCM', 'Sài Gòn', 'Sài gòn', 'Bình Thạnh', 'Quận 7', 'Thủ Đức'] for a in aspects)
        has_specific = any(('đường' in a.lower() or 'cầu' in a.lower() or 'hẻm' in a.lower() or 'ngã' in a.lower()) for a in aspects)
        if has_broad and has_specific:
            print(f"L{idx} MULTI_LEVEL_DUP: {aspects}")

    # 7. Empty triplets check
    if not triplets:
        if any(w in t_lower for w in ['ngập', 'triều cường', 'đỉnh triều']):
            print(f"L{idx} EMPTY_TRIPLETS: {text[:90]}...")
