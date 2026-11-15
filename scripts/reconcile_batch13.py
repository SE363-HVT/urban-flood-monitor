import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# Line 1262 (idx 1261): concise opinion 'ngập sâu' [36, 37]
updates[1261] = (
    "Chiều 27 / 5 , mưa lớn xuất hiện ở nhiều nơi tại TPHCM như quận 1 , quận 3 , quận Bình Thạnh , TP Thủ Đức . . . khiến một số tuyến đường ngập sâu , việc đi lại của người dân gặp nhiều khó khăn .",
    [([15, 16], [36, 37], 'NEG'),
     ([18, 19], [36, 37], 'NEG'),
     ([21, 22, 23], [36, 37], 'NEG'),
     ([25, 26, 27], [36, 37], 'NEG')]
)

# Validate and apply updates
for idx, (new_text, new_trips) in updates.items():
    tokens = new_text.split()
    for asp, opi, pol in new_trips:
        for a in asp:
            assert a < len(tokens), f"Line {idx+1}: asp idx {a} out of range {len(tokens)}"
        for o in opi:
            assert o < len(tokens), f"Line {idx+1}: opi idx {o} out of range {len(tokens)}"
    lines[idx] = f"{new_text}####{new_trips}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print(f"Batch 13: Successfully updated {len(updates)} records!")
