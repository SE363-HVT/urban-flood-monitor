import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# Line 1738 (idx 1737): omit phường An Khánh, quận 2; concise opinion 'ngập sâu' [37, 38]
updates[1737] = (
    "Chiều 16 / 6 , cơn mưa lớn kèm dông gió kéo dài hơn một giờ khiến nhiều tuyến đường tại khu vực Thảo Điền ( phường An Khánh , quận 2 cũ , TP. HCM ) ngập sâu , gây khó khăn cho việc đi lại của người dân .",
    [([23, 24], [37, 38], 'NEG')]
)

# Line 1740 (idx 1739): omit phường An Khánh, concise opinion 'nước dâng cao phủ kín mặt đường' [14..20]
updates[1739] = (
    "Tại khu vực chân cầu Ba Son ( phía phường An Khánh ) , nước dâng cao phủ kín mặt đường , hàng loạt xe máy và ô tô bị chết máy khi cố gắng đi qua đoạn ngập .",
    [([4, 5, 6], [14, 15, 16, 17, 18, 19, 20], 'NEG')]
)

# Line 1748 (idx 1747): omit phường An Khánh, quận 2; concise opinion 'ngập sâu' [23, 24]
updates[1747] = (
    "Khoảng 17h30 , mưa lớn khiến hàng loạt tuyến đường quanh khu Thảo Điền ( phường An Khánh , quận 2 cũ ) ngập sâu , có đoạn gần ngang người khiến xe chết máy , người dân phải dắt bộ xe về nhà .",
    [([12, 13], [23, 24], 'NEG')]
)

# Line 1753 (idx 1752): concise opinion 'ngập nặng' [27, 28]
updates[1752] = (
    "Cách xa lộ Hà Nội gần 15 km , mưa giông cũng khiến hai đầu cầu Phú Mỹ ( nối quận 2 và quận 7 cũ ) ngập nặng , dòng xe ùn ứ kéo dài .",
    [([13, 14, 15, 16, 17], [27, 28], 'NEG')]
)

# Line 1767 (idx 1766): include prefix 'đường' for đường Linh Đông [29, 30, 31], add giao lộ Tô Ngọc Vân – Linh Đông [1..8]
updates[1766] = (
    "Ở giao lộ Tô Ngọc Vân – Linh Đông , nước ngập lên đến yên xe máy ( khoảng 1 m ) và chảy cuồn cuộn đổ thẳng vào đường Linh Đông .",
    [([1, 2, 3, 4, 5, 6, 7, 8], [10, 11, 12, 13, 14, 15, 16], 'NEG'),
     ([29, 30, 31], [10, 11, 12, 13, 14, 15, 16], 'NEG')]
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

print(f"Batch 18: Successfully updated {len(updates)} records!")
