import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

districts = [
    'bình thạnh', 'thủ đức', 'gò vấp', 'tân bình', 'tân phú', 'phú nhuận', 'bình tân', 'nhà bè', 'hóc môn',
    'củ chi', 'cần giờ', 'bình chánh', 'dĩ an', 'thuận an', 'thủ dầu một', 'bến cát', 'tân uyên', 'vũng tàu',
    'bà rịa', 'thảo điền', 'thanh đa', 'an phú', 'phú mỹ hưng', 'hàng xanh', 'bảy hiền', 'ba son', 'bùi viện'
]

# Roads with proper nouns: "đường [Tên Viết Hoa]"
road_named = re.compile(r'\b(đường|cầu|hẻm|phố|ngõ|quốc lộ|xa lộ|ngã tư|ngã ba|kênh|sông|rạch|chợ)\s+([A-ZÀ-Ỹ0-9][a-zà-ỹ0-9]*)', re.UNICODE)
admin_named = re.compile(r'\b(quận|huyện|phường)\s+([0-9]+|[A-ZÀ-Ỹ][a-zà-ỹ]*)', re.UNICODE)

prefix_only_with_specific = []

for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip_str = line.split('####')
    triplets = ast.literal_eval(trip_str)
    
    if not (text.startswith('Tại TP. Hồ Chí Minh , ') or text.startswith('Tại TPHCM , ')):
        continue
        
    pfx_token_count = 6 if text.startswith('Tại TP. Hồ Chí Minh , ') else 3
    
    # check if targets only prefix
    is_prefix_only = True
    for asp, opi, pol in triplets:
        if any(i >= pfx_token_count for i in asp):
            is_prefix_only = False
            break
            
    if not is_prefix_only or not triplets:
        continue
        
    # check body for specific names
    body = text.split(' , ', 1)[1] if ' , ' in text else text
    found = []
    for m in road_named.finditer(body):
        # ignore generic capitalizations at sentence start if any, but let's check
        found.append(m.group(0))
    for m in admin_named.finditer(body):
        found.append(m.group(0))
    for d in districts:
        if d in body.lower():
            found.append(d)
            
    if found:
        prefix_only_with_specific.append((rec_num, found, text, triplets))

print(f"Số records gán Fallback Prefix nhưng trong thân bài có tên địa danh cụ thể: {len(prefix_only_with_specific)}")
for r, f, t, tr in prefix_only_with_specific[:25]:
    print(f"Rec {r}: {f} -> {t[:100]}... | {tr}")
