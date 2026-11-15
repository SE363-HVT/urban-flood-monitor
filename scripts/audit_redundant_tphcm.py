import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Tổng số records kiểm tra: {len(lines)}")

# Pattern 1: Double / Repeated TPHCM clusters (e.g. "TPHCM ở TPHCM", "ở TPHCM ở TPHCM", "TP. HCM ở TP. HCM", "TPHCM TPHCM", etc.)
double_pattern = re.compile(
    r'(tphcm\s+ở\s+tphcm|ở\s+tphcm\s+ở\s+tphcm|tp\.\s*hcm\s+ở\s+tp\.\s*hcm|tphcm\s+tphcm|tại\s+tphcm\s*,?\s*tphcm|tại\s+tp\.\s*hồ\s+chí\s+minh\s*,?\s*tp\.\s*hồ\s+chí\s+minh)',
    re.IGNORECASE
)

# Pattern 2: Multiple occurrences of TPHCM / TP. HCM / Sài Gòn in the text
# Pattern 3: Specific local entities existing in text (streets, wards, districts, landmarks) while "ở TPHCM" or "Tại TPHCM" / "Tại TP. Hồ Chí Minh" was injected
specific_location_indicators = [
    r'\bđường\s+[A-ZÀ-Ỹa-zà-ỹ0-9\s]+',
    r'\bhẻm\s+[A-ZÀ-Ỹa-zà-ỹ0-9\s]+',
    r'\bcầu\s+[A-ZÀ-Ỹa-zà-ỹ0-9\s]+',
    r'\bhầm\s+(chui\s+)?[A-ZÀ-Ỹa-zà-ỹ0-9\s]+',
    r'\bngã\s+(tư|ba|năm|sáu|bảy)\s+[A-ZÀ-Ỹa-zà-ỹ0-9\s]+',
    r'\bphường\s+[A-ZÀ-Ỹa-zà-ỹ0-9\s]+',
    r'\bquận\s+[0-9A-ZÀ-Ỹa-zà-ỹ]+',
    r'\bhuyện\s+[A-ZÀ-Ỹa-zà-ỹ]+',
    r'\bchợ\s+[A-ZÀ-Ỹa-zà-ỹ]+',
    r'\bkênh\s+[A-ZÀ-Ỹa-zà-ỹ]+',
    r'\brạch\s+[A-ZÀ-Ỹa-zà-ỹ]+',
    r'\bxã\s+[A-ZÀ-Ỹa-zà-ỹ]+'
]
spec_regex = re.compile('|'.join(specific_location_indicators), re.IGNORECASE)

records_with_double = []
records_with_redundant_fallback = []

for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip_str = line.split('####')
    text_lower = text.lower()
    
    # 1. Check double patterns
    m_double = double_pattern.search(text)
    if m_double:
        records_with_double.append((rec_num, m_double.group(0), text, trip_str))
        
    # Check general repeating phrase "ở TPHCM" appearing 2+ times
    tc_count = len(re.findall(r'ở\s+tphcm', text_lower))
    tphcm_count = len(re.findall(r'\btphcm\b|\btp\.\s*hcm\b', text_lower))
    if tc_count >= 2:
        records_with_double.append((rec_num, f"'ở TPHCM' xuất hiện {tc_count} lần", text, trip_str))

print("=" * 80)
print(f"1. KẾT QUẢ RÀ SOÁT CỤM DOUBLE / LẶP TỪ (VD: 'TPHCM ở TPHCM', 'ở TPHCM ở TPHCM'):")
print(f"Tổng số phát hiện: {len(records_with_double)} trường hợp")
print("=" * 80)
seen_recs = set()
for rec_num, match_str, text, trip_str in records_with_double:
    if rec_num not in seen_recs:
        seen_recs.add(rec_num)
        print(f"Record {rec_num}: [Trùng khớp: {match_str}]")
        print(f"  TEXT: {text}")
        print(f"  TRIP: {trip_str}\n")
