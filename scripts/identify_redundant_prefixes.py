import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

# Let's check prefixes
prefixes = ['Tại TP. Hồ Chí Minh , ', 'Tại TPHCM , ', 'Tại TP.HCM , ']

# Specific locations:
# 1. Road, street, bridge, tunnel, alley, highway, circle, intersection, market, bus station, canal, river
spec_place_regex = re.compile(
    r'\b(đường|hẻm|phố|ngõ|cầu|hầm|quốc lộ|xa lộ|vòng xoay|ngã tư|ngã ba|ngã năm|ngã sáu|ngã bảy|chợ|kcn|khu công nghiệp|khu chế xuất|bến xe|kênh|sông|rạch|bán đảo)\s+([A-ZÀ-Ỹ0-9][a-zà-ỹ0-9]*(\s+[A-ZÀ-Ỹ0-9][a-zà-ỹ0-9]*)*)',
    re.UNICODE
)
admin_regex = re.compile(
    r'\b(quận|huyện|phường|thị xã)\s+([A-ZÀ-Ỹ0-9][a-zà-ỹ0-9]*(\s+[A-ZÀ-Ỹ0-9][a-zà-ỹ0-9]*)*)',
    re.UNICODE
)
specific_named_entities = [
    'bình thạnh', 'thủ đức', 'gò vấp', 'tân bình', 'tân phú', 'phú nhuận', 'bình tân', 'nhà bè', 'hóc môn',
    'củ chi', 'cần giờ', 'bình chánh', 'dĩ an', 'thuận an', 'thủ dầu một', 'bến cát', 'tân uyên', 'vũng tàu',
    'bà rịa', 'thảo điền', 'thanh đa', 'an phú', 'phú mỹ hưng', 'hàng xanh', 'bảy hiền', 'ba son', 'phố tây bùi viện'
]

records_to_clean = []

for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip_str = line.split('####')
    triplets = ast.literal_eval(trip_str)
    
    # check if text starts with our injected prefix
    pfx_matched = None
    body = text
    for pfx in prefixes:
        if text.startswith(pfx):
            pfx_matched = pfx
            body = text[len(pfx):]
            break
            
    if not pfx_matched:
        continue
        
    # Check if body has specific location
    found_specs = []
    for m in spec_place_regex.finditer(body):
        # filter out generic terms like "con đường ngập", "tuyến đường này", etc.
        val = m.group(0).strip()
        val_lower = val.lower()
        if any(val_lower.startswith(x) for x in ['đường đi', 'đường về', 'đường ngập', 'đường vào', 'đường đến', 'đường lên', 'đường này', 'đường nước', 'đường nhớ', 'đường xe']):
            continue
        found_specs.append(val)
        
    for m in admin_regex.finditer(body):
        found_specs.append(m.group(0).strip())
        
    body_lower = body.lower()
    for ne in specific_named_entities:
        if ne in body_lower:
            found_specs.append(ne)
            
    # Also check: did the existing triplets ALREADY target specific entities in body (aspect index > len(pfx.split()))?
    pfx_tokens = pfx.strip().split()
    pfx_len = len(pfx_tokens)
    targets_body = False
    targets_prefix = False
    for asp, opi, pol in triplets:
        if asp == [1] or asp == [1, 2, 3, 4]:
            targets_prefix = True
        elif any(i >= pfx_len for i in asp):
            targets_body = True
            
    # If it has specific location in body OR triplets target specific entities in body,
    # then prefix was injected redundantly!
    if found_specs or targets_body:
        records_to_clean.append({
            'rec_num': rec_num,
            'pfx': pfx_matched,
            'pfx_len': pfx_len,
            'text': text,
            'body': body,
            'triplets': triplets,
            'specs': list(set(found_specs)),
            'targets_prefix': targets_prefix,
            'targets_body': targets_body
        })

print(f"Tổng số records có prefix: {len([l for l in lines if any(l.startswith(p) for p in prefixes)])}")
print(f"Số records có địa điểm cụ thể trong thân bài bị bơm tiền tố thừa: {len(records_to_clean)}")
print(f"  - Trong đó có gán vào body (địa điểm cụ thể): {len([r for r in records_to_clean if r['targets_body']])}")
print(f"  - Trong đó có gán vào prefix (cần chuyển aspect sang địa điểm thật): {len([r for r in records_to_clean if r['targets_prefix']])}")

