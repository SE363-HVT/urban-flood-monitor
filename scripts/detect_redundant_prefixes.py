import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

# Let's inspect which records have prefix AND have a specific location in body
records_with_injected_prefix_and_specific_location = []

# List of specific location indicators:
# Street names, bridge names, specific districts, wards, landmarks
specific_districts = [
    'bình thạnh', 'thủ đức', 'gò vấp', 'tân bình', 'tân phú', 'phú nhuận', 'bình tân', 'nhà bè', 'hóc môn',
    'củ chi', 'cần giờ', 'bình chánh', 'dĩ an', 'thuận an', 'thủ dầu một', 'bến cát', 'tân uyên', 'vũng tàu',
    'bà rịa', 'quận 1', 'quận 2', 'quận 3', 'quận 4', 'quận 5', 'quận 6', 'quận 7', 'quận 8', 'quận 9', 'quận 10', 'quận 11', 'quận 12',
    'thảo điền', 'thanh đa', 'an phú', 'phú mỹ hưng', 'hàng xanh', 'bảy hiền', 'ba son', 'bùi viện', 'miền đông', 'miền tây'
]

road_pattern = re.compile(
    r'\b(đường|phố|cầu|hẻm|hầm|ngã tư|ngã ba|ngã năm|ngã sáu|ngã bảy|quốc lộ|xa lộ|chợ|kênh|rạch|sông|bến xe)\s+([A-ZÀ-Ỹ0-9][a-zà-ỹ0-9]*)',
    re.UNICODE
)
admin_pattern = re.compile(
    r'\b(quận|huyện|phường|thị xã|kcn|khu công nghiệp)\s+([A-ZÀ-Ỹ0-9][a-zà-ỹ0-9]*)',
    re.UNICODE
)

for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip_str = line.split('####')
    triplets = ast.literal_eval(trip_str)
    
    prefix = None
    body = text
    pfx_token_len = 0
    if text.startswith('Tại TP. Hồ Chí Minh , '):
        prefix = 'Tại TP. Hồ Chí Minh , '
        body = text[len('Tại TP. Hồ Chí Minh , '):]
        pfx_token_len = 6
    elif text.startswith('Tại TPHCM , '):
        prefix = 'Tại TPHCM , '
        body = text[len('Tại TPHCM , '):]
        pfx_token_len = 3
    elif text.startswith('Tại TP.HCM , '):
        prefix = 'Tại TP.HCM , '
        body = text[len('Tại TP.HCM , '):]
        pfx_token_len = 4
        
    if not prefix:
        continue
        
    # Check if triplets target entities in body
    triplet_targets_body = False
    for asp, opi, pol in triplets:
        if any(i >= pfx_token_len for i in asp):
            triplet_targets_body = True
            break
            
    # Check text body for specific places
    body_lower = body.lower()
    places_found = []
    
    # Check named roads/places
    for m in road_pattern.finditer(body):
        # filter out false positives
        word = m.group(2).lower()
        if word not in ['này', 'đó', 'kia', 'nào', 'ngập', 'vào', 'ra', 'qua', 'lên', 'xuống', 'đến', 'về', 'đi', 'đã', 'sẽ', 'bị', 'được', 'lớn', 'nhỏ', 'nhiều']:
            places_found.append(m.group(0))
            
    for m in admin_pattern.finditer(body):
        word = m.group(2).lower()
        if word not in ['này', 'đó', 'kia', 'nào', 'ngập', 'vào', 'ra', 'qua', 'lên', 'xuống', 'đến', 'về', 'đi', 'đã', 'sẽ', 'bị', 'được', 'lớn', 'nhỏ', 'nhiều']:
            places_found.append(m.group(0))
            
    for d in specific_districts:
        if d in body_lower:
            places_found.append(d)
            
    if triplet_targets_body or places_found:
        records_with_injected_prefix_and_specific_location.append({
            'rec_num': rec_num,
            'prefix': prefix,
            'pfx_token_len': pfx_token_len,
            'body': body,
            'text': text,
            'triplets': triplets,
            'places_found': list(set(places_found)),
            'triplet_targets_body': triplet_targets_body
        })

print(f"Tổng số records có prefix VÀ có địa điểm sẵn trong body: {len(records_with_injected_prefix_and_specific_location)}")
print(f"  - Đã có triplet gán trực tiếp vào body: {len([r for r in records_with_injected_prefix_and_specific_location if r['triplet_targets_body']])}")
print(f"  - Triplet đang gán vào prefix (cần điều chỉnh gán lại vào địa điểm thực tế hoặc giữ nếu không có địa điểm ngập trực tiếp): {len([r for r in records_with_injected_prefix_and_specific_location if not r['triplet_targets_body']])}")

# Let's save this detailed list
with open('scripts/prefix_to_clean.py', 'w', encoding='utf-8') as f:
    f.write(f"# Total: {len(records_with_injected_prefix_and_specific_location)}\n")
    for r in records_with_injected_prefix_and_specific_location:
        f.write(f"# Rec {r['rec_num']}: places={r['places_found']} | targets_body={r['triplet_targets_body']}\n")
