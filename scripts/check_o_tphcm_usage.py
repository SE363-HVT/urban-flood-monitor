import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

# Let's inspect all records containing "ở TPHCM" or "ở TP. HCM" or "ở TP. Hồ Chí Minh"
o_tphcm_recs = []
for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip = line.split('####')
    matches = list(re.finditer(r'ở\s+(TPHCM|TP\.\s*HCM|TP\.\s*Hồ\s+Chí\s+Minh)', text, re.IGNORECASE))
    if matches:
        o_tphcm_recs.append((rec_num, text, trip, [m.group(0) for m in matches]))

print(f"Tổng số records có chứa cụm 'ở TPHCM / ở TP.HCM / ở TP. Hồ Chí Minh': {len(o_tphcm_recs)}")

# How many of these are inside "triều cường ở TPHCM" / "đỉnh triều ở TPHCM"?
trieu_cuong_count = 0
standalone_count = 0
for r, t, tr, ms in o_tphcm_recs:
    # check if all occurrences are part of trieu cuong / dinh trieu
    t_clean = t.lower()
    tc_matches = re.findall(r'(triều\s+cường|đỉnh\s+triều|mực\s+nước\s+triều\s+cường)\s+ở\s+tphcm', t_clean)
    if len(tc_matches) == len(ms):
        trieu_cuong_count += 1
    else:
        standalone_count += 1

print(f"  - Chỉ xuất hiện trong cụm chuẩn 'triều cường ở TPHCM' / 'đỉnh triều ở TPHCM': {trieu_cuong_count}")
print(f"  - Xuất hiện ở vị trí khác (hoặc vừa có triều cường vừa có ở vị trí khác): {standalone_count}")
