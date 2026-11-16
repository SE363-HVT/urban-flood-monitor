# -*- coding: utf-8 -*-
with open('data/validate_label/thuan/phase3.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

# REC 2146 (0-indexed: 2145)
rec_2146_text = lines[2145].split('####')[0].strip()
lines[2145] = f"{rec_2146_text}####[]"

with open('data/validate_label/thuan/phase3.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print("Reset REC 2146 to ####[]")
