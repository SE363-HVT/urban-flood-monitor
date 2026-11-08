import sys, os, ast, re

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase1.txt', 'r', encoding='utf-8') as f:
    thuan_lines = [l.strip() for l in f if l.strip()]

with open('data/validate_label/hung/phase1.txt', 'r', encoding='utf-8') as f:
    hung_lines = [l.strip() for l in f if l.strip()]

# 25 confirmed reject records
REJECT_RECORDS = {
    68, 145, 148, 150, 155, 157, 172, 178, 179, 184, 187, 194, 203,
    215, 229, 315, 316, 326, 393, 452, 481, 482, 486, 490, 491
}

# Add pre-existing rejects from Thuan
for i, line in enumerate(thuan_lines, 1):
    _, trips_str = line.split('####')
    if trips_str == '[]':
        REJECT_RECORDS.add(i)

print(f"Total reject records: {len(REJECT_RECORDS)}")
