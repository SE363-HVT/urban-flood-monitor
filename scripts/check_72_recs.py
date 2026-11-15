import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip = line.split('####')
    matches = list(re.finditer(r'ở\s+(TPHCM|TP\.\s*HCM|TP\.\s*Hồ\s+Chí\s+Minh)', text, re.IGNORECASE))
    if matches:
        t_clean = text.lower()
        tc_matches = re.findall(r'(triều\s+cường|đỉnh\s+triều|mực\s+nước\s+triều\s+cường)\s+ở\s+tphcm', t_clean)
        if len(tc_matches) != len(matches):
            print(f"Rec {rec_num}:")
            print(f"  TEXT: {text}")
            print(f"  TRIP: {trip}\n")
