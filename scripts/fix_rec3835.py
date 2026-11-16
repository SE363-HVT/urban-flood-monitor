# -*- coding: utf-8 -*-
from span_helper import make_triplet
import json

with open('data/validate_label/thuan/phase3.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

# REC 3835 (0-indexed: 3834)
rec_id = 3835
idx = rec_id - 1
text = "Tại TP. Hồ Chí Minh , Đến 20h , nước tại các tuyến đường trung tâm rút chậm ."
t = make_triplet(text, "TP. Hồ Chí Minh", "rút chậm", "POS")

lines[idx] = f"{text}####{json.dumps([t])}"

with open('data/validate_label/thuan/phase3.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print("Fixed REC 3835 Polarity to POS")
