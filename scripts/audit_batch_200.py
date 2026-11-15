import sys
import os
from ast import literal_eval
sys.stdout.reconfigure(encoding='utf-8')

if len(sys.argv) < 3:
    print("Usage: python audit_batch_200.py <start_idx> <end_idx>")
    sys.exit(1)

start_idx = int(sys.argv[1])
end_idx = int(sys.argv[2])

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f]

batch = lines[start_idx:end_idx]
print(f"=== DEEP AUDIT FOR BATCH ({start_idx+1} to {end_idx}) ===")

out_of_province_kws = ['hà nội', 'đà nẵng', 'hải phòng', 'cần thơ', 'nha trang', 'huế', 'quảng ninh', 'vinh', 'thanh hóa', 'nghệ an', 'quảng bình', 'quảng trị', 'quảng nam', 'quảng ngãi', 'bình định', 'phú yên', 'khánh hòa', 'ninh thuận', 'bình thuận', 'lâm đồng', 'đà lạt', 'buôn ma thuột', 'đắk lắk', 'gia lai', 'pleiku', 'kon tum', 'hà tĩnh', 'nam định', 'thái bình', 'hải dương', 'bắc ninh', 'vĩnh phúc', 'thái nguyên', 'tuyên quang', 'lào cai', 'yên bái', 'hà giang', 'cao bằng', 'lạng sơn', 'bắc kạn', 'sơn la', 'điện biên', 'lai châu', 'đồng nai', 'cà mau', 'sa đéc', 'vĩnh long', 'bến tre', 'trà vinh', 'an giang', 'kiên giang']

preps = {'ở', 'tại', 'trên', 'dưới', 'trong', 'ngoài', 'từ', 'đến', 'gần', 'cạnh', 'bên', 'phía', 'thuộc', 'của'}

flaws = []
for idx, line in enumerate(batch, start_idx + 1):
    parts = line.split('####')
    text = parts[0]
    triplets = literal_eval(parts[1]) if len(parts) > 1 else []
    tokens = text.split()
    t_lower = text.lower()
    
    # 1. Bounds
    for a_idx, o_idx, pol in triplets:
        for i in a_idx + o_idx:
            if i >= len(tokens) or i < 0:
                flaws.append((idx, f"OOB index {i} >= {len(tokens)}"))
                
    # 2. Bare tidal
    for a_idx, o_idx, pol in triplets:
        a_w = ' '.join(tokens[i] for i in a_idx).lower()
        if a_w in ['triều cường', 'đỉnh triều', 'triều cao', 'thủy triều']:
            flaws.append((idx, f"BARE_TIDAL: [{a_w}]"))
            
    # 3. Invalid non-geo aspect
    for a_idx, o_idx, pol in triplets:
        a_w = ' '.join(tokens[i] for i in a_idx).lower()
        if a_w in ['xe cộ', 'giao thông', 'ô tô', 'xe máy', 'mực nước', 'nước', 'phương tiện']:
            flaws.append((idx, f"INVALID_ASPECT: [{a_w}]"))

    # 4. Preposition leakage in Aspect
    for a_idx, o_idx, pol in triplets:
        first_a = tokens[a_idx[0]].lower()
        if first_a in preps:
            flaws.append((idx, f"PREP_LEAKAGE_ASPECT: '{first_a}' at token {a_idx[0]}"))

    # 5. Missed prefix
    for a_idx, o_idx, pol in triplets:
        a_txt = ' '.join(tokens[i] for i in a_idx)
        min_a = min(a_idx)
        if min_a > 0:
            p_tok = tokens[min_a-1].lower()
            if p_tok in ['đường', 'cầu', 'hẻm', 'ngõ', 'phố', 'đại_lộ', 'xa_lộ', 'rạch', 'kênh'] and p_tok not in a_txt.lower():
                # Ignore if p_tok is part of generic description like "tuyến đường" before city name
                if not (p_tok == 'đường' and a_txt in ['Sài Gòn', 'TP.HCM', 'TPHCM', 'Thủ Đức']):
                    flaws.append((idx, f"MISSED_PREFIX: '{tokens[min_a-1]}' before [{a_txt}]"))

    # 6. Multi-level dups
    if len(triplets) > 1:
        aspects = [' '.join(tokens[i] for i in a_idx) for a_idx, _, _ in triplets]
        has_broad = any(a in ['TP.HCM', 'TPHCM', 'TP. HCM', 'TP . HCM', 'Sài Gòn', 'Sài gòn', 'Bình Thạnh', 'Quận 7', 'Thủ Đức'] for a in aspects)
        has_specific = any(('đường' in a.lower() or 'cầu' in a.lower() or 'hẻm' in a.lower() or 'd5' in a.lower()) for a in aspects)
        if has_broad and has_specific:
            opinions = [' '.join(tokens[i] for i in o_idx) for _, o_idx, _ in triplets]
            if len(opinions) > len(set(opinions)):
                flaws.append((idx, f"MULTI_LEVEL_DUP: aspects={aspects}"))

    # 7. Edge punctuation in opinion
    for a_idx, o_idx, pol in triplets:
        first_tok = tokens[o_idx[0]]
        last_tok = tokens[o_idx[-1]]
        if first_tok in ['.', ',', ';', ':', '!', '?', '…', '-', '–'] or last_tok in ['.', ',', ';', ':', '!', '?', '…', '-', '–']:
            flaws.append((idx, f"EDGE_PUNCT: first='{first_tok}', last='{last_tok}' in opinion"))

    # 8. Out of province
    for kw in out_of_province_kws:
        if kw in t_lower and kw not in ['xa lộ hà nội'] and triplets:
            if not any(h in t_lower for h in ['tphcm', 'tp. hcm', 'tp.hcm', 'sài gòn', 'bình dương', 'thủ đức', 'thủ dầu một', 'thuận an', 'dĩ an', 'quận 1', 'quận 2', 'quận 3', 'quận 4', 'quận 5', 'quận 6', 'quận 7', 'quận 8', 'quận 9', 'quận 10', 'quận 11', 'quận 12', 'bình thạnh', 'tân bình', 'gò vấp', 'bình tân', 'nhà bè', 'hóc môn', 'củ chi', 'cần giờ']):
                flaws.append((idx, f"OUT_OF_PROVINCE_TAGGED: kw='{kw}' text='{text[:70]}'"))

print(f"Total flaws found: {len(flaws)}")
for f in flaws:
    print(f)
