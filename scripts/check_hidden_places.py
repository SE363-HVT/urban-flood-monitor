import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

prefixes = ['Tại TP. Hồ Chí Minh , ', 'Tại TPHCM , ', 'Tại TP.HCM , ']

# Explicit list of road names or districts or wards
districts = [
    'quận 1', 'quận 2', 'quận 3', 'quận 4', 'quận 5', 'quận 6', 'quận 7', 'quận 8', 'quận 9', 'quận 10', 'quận 11', 'quận 12',
    'bình thạnh', 'thủ đức', 'gò vấp', 'tân bình', 'tân phú', 'phú nhuận', 'bình tân', 'nhà bè', 'hóc môn',
    'củ chi', 'cần giờ', 'bình chánh', 'dĩ an', 'thuận an', 'thủ dầu một', 'bến cát', 'tân uyên', 'vũng tàu',
    'bà rịa', 'thảo điền', 'thanh đa', 'an phú', 'phú mỹ hưng', 'hàng xanh', 'bảy hiền', 'ba son', 'bùi viện'
]

# Pattern for named roads/bridges/markets/etc.
road_pattern = re.compile(
    r'\b(đường|phố|cầu|hẻm|hầm|quốc lộ|xa lộ|ngã tư|ngã ba|chợ|kênh|rạch|sông)\s+([A-ZÀ-Ỹ0-9][a-zà-ỹ0-9]*)',
    re.UNICODE
)

has_real_place = []

for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip_str = line.split('####')
    triplets = ast.literal_eval(trip_str)
    
    pfx = None
    shift = 0
    if text.startswith('Tại TP. Hồ Chí Minh , '):
        pfx = 'Tại TP. Hồ Chí Minh , '
        shift = 6
    elif text.startswith('Tại TPHCM , '):
        pfx = 'Tại TPHCM , '
        shift = 3
    elif text.startswith('Tại TP.HCM , '):
        pfx = 'Tại TP.HCM , '
        shift = 4
        
    if not pfx:
        continue
        
    # Skip if already targets body (those 59 records are already confirmed)
    if any(any(i >= shift for i in asp) for asp, opi, pol in triplets):
        continue
        
    body = text[len(pfx):]
    body_lower = body.lower()
    
    # check if body has real location
    found_dist = [d for d in districts if d in body_lower]
    found_roads = []
    for m in road_pattern.finditer(body):
        w = m.group(2).lower()
        if w not in ['này', 'đó', 'kia', 'nào', 'ngập', 'vào', 'ra', 'qua', 'lên', 'xuống', 'đến', 'về', 'đi', 'đã', 'sẽ', 'bị', 'được', 'lớn', 'nhỏ', 'nhiều', 'rộng', 'hẹp']:
            found_roads.append(m.group(0))
            
    if found_dist or found_roads:
        has_real_place.append((rec_num, pfx, found_dist, found_roads, body, triplets))

print(f"Số records gán prefix nhưng trong body có địa danh thực tế: {len(has_real_place)}")
for r, p, fd, fr, b, tr in has_real_place:
    print(f"Rec {r}: dist={fd}, roads={fr}")
    print(f"  BODY: {b[:120]}")
    print(f"  TRIP: {tr}\n")
