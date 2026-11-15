import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt.bak_before_redundant_clean'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

spec_patterns = [
    r'\bđường\s+[^,.;#!\?]+',
    r'\bphố\s+[^,.;#!\?]+',
    r'\bcầu\s+[^,.;#!\?]+',
    r'\bhẻm\s+[^,.;#!\?]+',
    r'\bhầm\s+[^,.;#!\?]+',
    r'\bngã\s+(tư|ba|năm|sáu|bảy)\s+[^,.;#!\?]+',
    r'\bquốc\s+lộ\s+[0-9A-Za-z]+',
    r'\bxa\s+lộ\s+[^,.;#!\?]+',
    r'\bchợ\s+[^,.;#!\?]+',
    r'\bkcn\s+[^,.;#!\?]+',
    r'\bkhu\s+chế\s+xuất\s+[^,.;#!\?]+',
    r'\bquận\s+[0-9A-Za-zÀ-ỹ]+',
    r'\bhuyện\s+[A-Za-zÀ-ỹ]+',
    r'\bphường\s+[0-9A-Za-zÀ-ỹ]+',
    r'\bbình\s+thạnh\b',
    r'\bthủ\s+đức\b',
    r'\bgò\s+vấp\b',
    r'\btân\s+bình\b',
    r'\btân\s+phú\b',
    r'\bphú\s+nhuận\b',
    r'\bbình\s+tân\b',
    r'\bnhà\s+bè\b',
    r'\bhóc\s+môn\b',
    r'\bcủ\s+chi\b',
    r'\bcần\s+giờ\b',
    r'\bbình\s+chánh\b',
    r'\bdĩ\s+an\b',
    r'\bthuận\s+an\b',
    r'\bthủ\s+dầu\s+một\b',
    r'\bbến\s+cát\b',
    r'\btân\s+uyên\b',
    r'\bvũng\s+tàu\b',
    r'\bbà\s+rịa\b',
    r'\bthảo\s+điền\b',
    r'\bthanh\s+đa\b',
    r'\ban\s+phú\b'
]
spec_regex = re.compile('|'.join(spec_patterns), re.IGNORECASE)

records_prefix_and_specific = []

for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip = line.split('####')
    
    prefix = None
    body = text
    for pfx in ['Tại TP. Hồ Chí Minh , ', 'Tại TPHCM , ', 'Tại TP.HCM , ']:
        if text.startswith(pfx):
            prefix = pfx
            body = text[len(pfx):]
            break
            
    if not prefix:
        continue
        
    body_specs = list(set([m.group(0).strip() for m in spec_regex.finditer(body)]))
    cleaned_specs = []
    for s in body_specs:
        s_low = s.lower()
        if s_low in ['đường đi', 'đường về', 'đường ngập', 'đường vào', 'đường đến', 'con đường', 'tuyến đường', 'đường phố']:
            continue
        cleaned_specs.append(s)
        
    if cleaned_specs:
        records_prefix_and_specific.append((rec_num, prefix, cleaned_specs, text, trip))

print(f"Tổng số tìm thấy: {len(records_prefix_and_specific)}")
# Let's inspect some of them
for r, pfx, cs, t, tr in records_prefix_and_specific[:30]:
    print(f"Rec {r}: {cs} | {tr}")
    print(f"   {t[:100]}...\n")
