import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# Line 1166 (idx 1165): concise opinion 'ngập sâu' [35, 36]
updates[1165] = (
    "Tại TP. Hồ Chí Minh , Trưa 10 / 10 , cơn mưa lớn kéo dài gần một tiếng đồng hồ khiến nhiều tuyến đường ở quận 1 , quận 12 và TP Thủ Đức ngập sâu , ảnh hưởng đến đời sống của người dân .",
    [([26, 27], [35, 36], 'NEG'),
     ([29, 30], [35, 36], 'NEG'),
     ([32, 33, 34], [35, 36], 'NEG')]
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

print(f"Batch 12: Successfully updated {len(updates)} records!")
