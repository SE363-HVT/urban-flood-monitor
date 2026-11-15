import sys
import re
import json

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

# 1. Exact Double Patterns
p_double = re.compile(
    r'(tphcm\s+ở\s+tphcm|ở\s+tphcm\s+ở\s+tphcm|tp\.\s*hcm\s+ở\s+tp\.\s*hcm|tphcm\s+tphcm|tại\s+tphcm\s*,?\s*tphcm|tại\s+tp\.\s*hồ\s+chí\s+minh\s*,?\s*tp\.\s*hồ\s+chí\s+minh|tại\s+tp\.\s*hồ\s+chí\s+minh\s*,?\s*tphcm)',
    re.IGNORECASE
)

# 2. Specific entities (streets, districts, landmarks, wards)
# Regex to find specific named locations
street_p = re.compile(r'\b(đường|hẻm|phố|ngõ|cầu|hầm|quốc lộ|xa lộ|vòng xoay|ngã tư|ngã ba|ngã năm|ngã sáu|ngã bảy|chợ|kcn|khu công nghiệp|khu chế xuất|bến xe)\s+([A-ZÀ-Ỹ0-9][a-zà-ỹ0-9]*(\s+[A-ZÀ-Ỹ0-9][a-zà-ỹ0-9]*)*)', re.UNICODE)
admin_p = re.compile(r'\b(quận|huyện|phường|thị xã|tp\.|thành phố|tỉnh)\s+([A-ZÀ-Ỹ0-9][a-zà-ỹ0-9]*(\s+[A-ZÀ-Ỹ0-9][a-zà-ỹ0-9]*)*)', re.UNICODE)
landmarks_list = [
    'thảo điền', 'thanh đa', 'an phú', 'bình thạnh', 'thủ đức', 'gò vấp', 'tân bình', 'tân phú', 'phú nhuận', 'bình tân',
    'nhà bè', 'hóc môn', 'củ chi', 'cần giờ', 'bình chánh', 'dĩ an', 'thuận an', 'thủ dầu một', 'bến cát', 'tân uyên',
    'vũng tàu', 'bà rịa', 'phố tây bùi viện', 'hàng xanh', 'bảy hiền', 'ba son', 'nguyễn hữu cảnh', 'phú mỹ hưng'
]

def find_specific_places(text_body):
    places = set()
    for m in street_p.finditer(text_body):
        places.add(m.group(0))
    for m in admin_p.finditer(text_body):
        # exclude generic "thành phố" or "tỉnh" if not specific
        p_val = m.group(0).lower()
        if not re.search(r'\b(tp\.|thành phố)\s+(hồ chí minh|hcm|tphcm)\b', p_val):
            places.add(m.group(0))
    t_lower = text_body.lower()
    for lm in landmarks_list:
        if lm in t_lower:
            places.add(lm)
    return list(places)

cat1_doubles = []
cat2_multi_o_tphcm = []
cat3_has_specific_and_o_tphcm = []
cat4_has_specific_and_prefix = []

for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip = line.split('####')
    text_lower = text.lower()
    
    # Check double
    m_d = p_double.search(text)
    if m_d:
        cat1_doubles.append((rec_num, m_d.group(0), text, trip))
        
    # Check multi 'ở tphcm'
    o_matches = re.findall(r'ở\s+(tphcm|tp\.\s*hcm|tp\.\s*hồ\s+chí\s+minh)', text_lower)
    if len(o_matches) >= 2:
        cat2_multi_o_tphcm.append((rec_num, len(o_matches), text, trip))
        
    # Separate prefix if any
    prefix = ""
    body = text
    if text.startswith('Tại TP. Hồ Chí Minh , '):
        prefix = 'Tại TP. Hồ Chí Minh , '
        body = text[len('Tại TP. Hồ Chí Minh , '):]
    elif text.startswith('Tại TPHCM , '):
        prefix = 'Tại TPHCM , '
        body = text[len('Tại TPHCM , '):]
    elif text.startswith('Tại TP.HCM , '):
        prefix = 'Tại TP.HCM , '
        body = text[len('Tại TP.HCM , '):]
        
    places = find_specific_places(body)
    
    # Check if body has 'ở TPHCM'
    has_o_tphcm_in_body = bool(re.search(r'ở\s+(tphcm|tp\.\s*hcm|tp\.\s*hồ\s+chí\s+minh)', body, re.IGNORECASE))
    
    if places and has_o_tphcm_in_body:
        cat3_has_specific_and_o_tphcm.append((rec_num, places, text, trip))
        
    if places and prefix:
        cat4_has_specific_and_prefix.append((rec_num, places, prefix, text, trip))

print(f"BÁO CÁO TỔNG HỢP KIỂM KÊ:")
print(f"Tổng số records: {len(lines)}")
print(f"1. Số records bị lỗi double cụm từ (e.g. 'ở TPHCM ở TPHCM', 'TPHCM TPHCM', 'Tại TPHCM , TPHCM'): {len(cat1_doubles)}")
print(f"2. Số records bị lặp cụm 'ở TPHCM' >= 2 lần: {len(cat2_multi_o_tphcm)}")
print(f"3. Số records ĐÃ CÓ địa điểm cụ thể nhưng VẪN CÓ cụm 'ở TPHCM' trong nội dung: {len(cat3_has_specific_and_o_tphcm)}")
print(f"4. Số records ĐÃ CÓ địa điểm cụ thể nhưng VẪN BỊ BƠM tiền tố fallback ('Tại TPHCM , ' / 'Tại TP. Hồ Chí Minh , '): {len(cat4_has_specific_and_prefix)}")

# Save detailed report to json
report_data = {
    'cat1_doubles': [{'rec': r, 'match': m, 'text': t, 'trip': tr} for r, m, t, tr in cat1_doubles],
    'cat2_multi': [{'rec': r, 'count': c, 'text': t, 'trip': tr} for r, c, t, tr in cat2_multi_o_tphcm],
    'cat3_specific_plus_o_tphcm': [{'rec': r, 'places': p, 'text': t, 'trip': tr} for r, p, t, tr in cat3_has_specific_and_o_tphcm],
    'cat4_specific_plus_prefix': [{'rec': r, 'places': p, 'prefix': pf, 'text': t, 'trip': tr} for r, p, pf, t, tr in cat4_has_specific_and_prefix]
}
with open('scripts/redundant_audit_report.json', 'w', encoding='utf-8') as f:
    json.dump(report_data, f, ensure_ascii=False, indent=2)

print("\nĐã xuất chi tiết toàn bộ danh sách records ra scripts/redundant_audit_report.json")
