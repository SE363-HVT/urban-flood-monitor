import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

# 1. Double / Duplicate TPHCM patterns
p_double_explicit = re.compile(
    r'(tphcm\s+ở\s+tphcm|ở\s+tphcm\s+ở\s+tphcm|tp\.\s*hcm\s+ở\s+tp\.\s*hcm|tphcm\s+tphcm|tại\s+tphcm\s*,?\s*tphcm|tại\s+tp\.\s*hồ\s+chí\s+minh\s*,?\s*tp\.\s*hồ\s+chí\s+minh|tại\s+tp\.\s*hồ\s+chí\s+minh\s*,?\s*tphcm)',
    re.IGNORECASE
)

districts = [
    'quận 1', 'quận 2', 'quận 3', 'quận 4', 'quận 5', 'quận 6', 'quận 7', 'quận 8', 'quận 9', 'quận 10', 'quận 11', 'quận 12',
    'bình thạnh', 'thủ đức', 'gò vấp', 'tân bình', 'tân phú', 'phú nhuận', 'bình tân', 'nhà bè', 'hóc môn', 'củ chi', 'cần giờ', 'bình chánh',
    'dĩ an', 'thuận an', 'thủ dầu một', 'bến cát', 'tân uyên', 'vũng tàu', 'bà rịa'
]
spec_indicators = [
    r'\bđường\s+[^\s,.;]+',
    r'\bphố\s+[^\s,.;]+',
    r'\bcầu\s+[^\s,.;]+',
    r'\bhẻm\s+[^\s,.;]+',
    r'\bhầm\s+[^\s,.;]+',
    r'\bngã\s+(tư|ba|năm|sáu|bảy)\s+[^\s,.;]+',
    r'\bquốc\s+lộ\s+[0-9A-Za-z]+',
    r'\bxa\s+lộ\s+[A-Za-zÀ-ỹ]+',
    r'\bchợ\s+[A-Za-zÀ-ỹ]+',
    r'\bkcn\s+[A-Za-zÀ-ỹ0-9]+',
    r'\bkhu\s+chế\s+xuất\s+[A-Za-zÀ-ỹ]+',
    r'\bthảo\s+điền\b',
    r'\ban\s+phú\b',
    r'\bthanh\s+đa\b'
]
spec_regex = re.compile('|'.join(spec_indicators), re.IGNORECASE)

records_double = []
records_o_tphcm_multiple = []
records_has_specific_and_has_o_tphcm = []
records_has_specific_and_has_prefix = []

for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip_str = line.split('####')
    text_lower = text.lower()
    
    # Check explicit double
    m = p_double_explicit.search(text)
    if m:
        records_double.append((rec_num, m.group(0), text, trip_str))
        
    # Check multiple 'ở tphcm'
    o_tphcm_matches = re.findall(r'ở\s+(tphcm|tp\.\s*hcm|tp\.\s*hồ\s+chí\s+minh)', text_lower)
    if len(o_tphcm_matches) >= 2:
        records_o_tphcm_multiple.append((rec_num, len(o_tphcm_matches), text, trip_str))
        
    # Check if text has specific location
    body_text = text
    has_prefix = False
    if text.startswith('Tại TP. Hồ Chí Minh , ') or text.startswith('Tại TPHCM , ') or text.startswith('Tại TP.HCM , '):
        has_prefix = True
        body_text = text.split(' , ', 1)[1] if ' , ' in text else text
        
    body_lower = body_text.lower()
    spec_matches = []
    
    for rm in spec_regex.finditer(body_lower):
        spec_matches.append(rm.group(0))
    for d in districts:
        if d in body_lower:
            spec_matches.append(d)
            
    # Check if text contains 'ở TPHCM'
    has_o_tphcm = bool(re.search(r'ở\s+(tphcm|tp\.\s*hcm|tp\.\s*hồ\s+chí\s+minh)', body_lower))
    
    if spec_matches and has_o_tphcm:
        records_has_specific_and_has_o_tphcm.append((rec_num, spec_matches, text, trip_str))
        
    if spec_matches and has_prefix:
        records_has_specific_and_has_prefix.append((rec_num, spec_matches, text, trip_str))

print(f"Tổng số records kiểm tra: {len(lines)}")
print("=" * 80)
print(f"NHÓM 1: CÁC RECORD BỊ DƯ / DOUBLE CỤM 'TPHCM ở TPHCM', 'ở TPHCM ở TPHCM', 'TPHCM TPHCM'...")
print(f"Tổng số phát hiện: {len(records_double)} records")
print("-" * 80)
for r, m, t, tr in records_double:
    print(f"Record {r}: [Cụm trùng: '{m}']")
    print(f"  TEXT: {t}")
    print(f"  TRIP: {tr}\n")

print("=" * 80)
print(f"NHÓM 2: CÁC RECORD XUẤT HIỆN 'ở TPHCM' TỪ 2 LẦN TRỞ LÊN TRONG CÂU:")
print(f"Tổng số phát hiện: {len(records_o_tphcm_multiple)} records")
print("-" * 80)
for r, c, t, tr in records_o_tphcm_multiple:
    print(f"Record {r} ({c} lần 'ở TPHCM'):")
    print(f"  TEXT: {t}")
    print(f"  TRIP: {tr}\n")

print("=" * 80)
print(f"NHÓM 3: CÁC RECORD ĐÃ CÓ ĐỊA ĐIỂM CỤ THỂ (đường, cầu, quận, phường, chợ...) NHƯNG VẪN CÓ CỤM 'ở TPHCM' TRONG NỘI DUNG:")
print(f"Tổng số phát hiện: {len(records_has_specific_and_has_o_tphcm)} records")
print("-" * 80)
print("Danh sách toàn bộ số thứ tự record:")
rec_ids_3 = [r[0] for r in records_has_specific_and_has_o_tphcm]
print(rec_ids_3)
print(f"\n10 ví dụ tiêu biểu:")
for r, sm, t, tr in records_has_specific_and_has_o_tphcm[:10]:
    print(f"Record {r} [Địa điểm phát hiện: {sm[:4]}]:")
    print(f"  TEXT: {t}")
    print(f"  TRIP: {tr}\n")

print("=" * 80)
print(f"NHÓM 4: CÁC RECORD ĐÃ CÓ ĐỊA ĐIỂM CỤ THỂ NHƯNG VẪN BỊ BƠM TIỀN TỐ FALLBACK ĐẦU CÂU ('Tại TPHCM , ' / 'Tại TP. Hồ Chí Minh , '):")
print(f"Tổng số phát hiện: {len(records_has_specific_and_has_prefix)} records")
print("-" * 80)
rec_ids_4 = [r[0] for r in records_has_specific_and_has_prefix]
print(f"Số lượng: {len(rec_ids_4)} records")
print(f"Danh sách ID: {rec_ids_4[:50]}... (tổng cộng {len(rec_ids_4)})")
print(f"\n10 ví dụ tiêu biểu:")
for r, sm, t, tr in records_has_specific_and_has_prefix[:10]:
    print(f"Record {r} [Địa điểm phát hiện: {sm[:4]}]:")
    print(f"  TEXT: {t}")
    print(f"  TRIP: {tr}\n")

