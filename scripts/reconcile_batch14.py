import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# Line 1326 (idx 1325): include triều cường ở TP. HCM [8, 9, 10, 11, 12] | dâng cao [13, 14] NEG
updates[1325] = (
    "Ghi nhận của Thanh Niên tối 7_11 , triều cường ở TP. HCM dâng cao khiến nhiều tuyến đường ngập sâu trong nước , đặc biệt tại khu vực đường Trần Xuân Soạn ( phường Tân Thuận ) , đường Đào Trí , Gò Ô Môi ( phường Phú Thuận ) . . .",
    [([8, 9, 10, 11, 12], [13, 14], 'NEG'),
     ([29, 30, 31, 32], [19, 20, 21, 22], 'NEG'),
     ([39, 40, 41], [19, 20, 21, 22], 'NEG'),
     ([43, 44, 45], [19, 20, 21, 22], 'NEG')]
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

print(f"Batch 14: Successfully updated {len(updates)} records!")
