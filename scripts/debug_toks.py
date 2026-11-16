# -*- coding: utf-8 -*-
with open('scripts/build_phase3_batch25.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '# 2412' in l:
        text_line = lines[i+2]
        print("Line:", text_line)
        toks = text_line.strip().strip('",').split()
        for idx, t in enumerate(toks):
            print(f'{idx}: {t}')
