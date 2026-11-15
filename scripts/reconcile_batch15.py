import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# Line 1443 (idx 1442): fix aspect boundary -> đường Tô Ngọc Vân [24, 25, 26, 27] | opinion ngập [22]
updates[1442] = (
    "Rạng sáng 25 / 10 , nhiều người dân ở TPHCM vẫn còn vật vã dắt xe máy di chuyển qua đoạn ngập trên đường Tô Ngọc Vân đoạn gần giao lộ Linh Đông , phường Linh Đông , thành phố Thủ Đức .",
    [([24, 25, 26, 27], [22], 'NEG')]
)

# Line 1460 (idx 1459): concise opinion 'ngập sâu' [23, 24]
updates[1459] = (
    "Các tuyến đường như Đặng Thị Rành , Nguyễn Duy Trinh , Linh Đông , Tô Ngọc Vân … đều trong tình trạng ngập sâu , có nơi nước ngập hơn nửa bánh xe , khiến nhiều phương tiện bị chết máy , người dân phải bì bõm dắt bộ .",
    [([4, 5, 6], [23, 24], 'NEG'),
     ([8, 9, 10], [23, 24], 'NEG'),
     ([12, 13], [23, 24], 'NEG'),
     ([15, 16, 17], [23, 24], 'NEG')]
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

print(f"Batch 15: Successfully updated {len(updates)} records!")
