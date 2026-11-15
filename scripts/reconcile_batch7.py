import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# Line 632 (idx 631): omit phường Tăng Nhơn Phú A and TP. Thủ Đức (multi-level dup with đường Lã Xuân Oai)
updates[631] = (
    "Ghi nhận trên đường Lã Xuân Oai , phường Tăng Nhơn Phú A ( TP. Thủ Đức , quận 9 cũ ) bị ngập rất nặng .",
    [([3, 4, 5, 6], [22, 23, 24, 25], 'NEG')]
)

# Line 637 (idx 636): omit TP. Thủ Đức (multi-level dup with đường Lê Văn Việt)
updates[636] = (
    "Mưa lớn cũng khiến đường Lê Văn Việt ( TP. Thủ Đức ) biến thành sông một đoạn dài .",
    [([4, 5, 6, 7], [13, 14, 15, 16, 17, 18], 'NEG')]
)

# Line 661 (idx 660): omit Q. Bình Thạnh (multi-level dup with đường Nguyễn Hữu Cảnh)
updates[660] = (
    "Còn mưa trong 2 ngày tới Nhiều xe chết máy trên đường Nguyễn Hữu Cảnh ( Q. Bình Thạnh , TP. HCM ) sau cơn mưa lớn kéo dài trong đêm .",
    [([11, 12, 13, 14], [6, 7, 8, 9], 'NEG')]
)

# Line 664 (idx 663): omit generic phrase 'nhiều khu vực trũng thấp', keep TP. HCM
updates[663] = (
    "Mưa lớn kéo dài từ khuya đến sáng 14_9 khiến nhiều khu vực trũng thấp tại cửa ngõ phía đông TP. HCM ngập nặng .",
    [([20, 21], [22, 23], 'NEG')]
)

# Line 676 (idx 675): omit enclosing entity TP. HCM, keep individual streets
updates[675] = (
    "Nhiều tuyến đường trên địa bàn khu vực Tây Bắc TP. HCM như : Nguyễn Văn Quá , Phan Huy Ích , Phạm Đăng Giảng … , ngập sâu , nhiều đoạn nước ngập lút hơn nửa bánh xe máy .",
    [([14, 15, 16], [27, 28], 'NEG'),
     ([18, 19, 20], [27, 28], 'NEG'),
     ([22, 23, 24], [27, 28], 'NEG')]
)

# Line 677 (idx 676): omit bounding intersections/wards/districts, keep main flooded street đường Phan Văn Hớn
updates[676] = (
    "Đặc biệt , trên đường Phan Văn Hớn , ( đoạn QL1 - Tân Thới Nhất 8 , P. Tân Thới Nhất , Q. 12 ) nước ngập dâng cao gần lút bánh xe máy kéo dài trên đoạn đường hơn 1km khiến nhiều người dân trên đường đi làm về trong đêm xe bị chết máy , phải vất vả đẩy bộ tìm nơi sửa .",
    [([4, 5, 6, 7], [26, 27, 28, 29], 'NEG')]
)

# Line 681 (idx 680): in-place expansion of triều cường -> triều cường ở TPHCM
updates[680] = (
    "Những ngày qua , khi mực nước triều cường ở TPHCM dâng cao vượt mức báo động 3 ( trên 1 , 5 mét ) khiến nhiều tuyến đường ở TPHCM bị ngập sâu .",
    [([7, 8, 9, 10], [11, 12], 'NEG'),
     ([30], [32, 33], 'NEG')]
)

# Line 684 (idx 683): omit Q. Thủ Đức (multi-level dup with đường Lê Thị Hoa)
updates[683] = (
    "Hễ trời bắt đầu chuyển mưa là những người dân sinh sống tại đường Lê Thị Hoa ( Q. Thủ Đức , TP. HCM ) lại loay hoay tranh thủ dọn đồ kê lên cao , rút điện tủ lạnh để tránh bị nước ngập . Kê cao đồ đạc , nước vào là quét ra",
    [([13, 14, 15, 16], [43, 44], 'NEG')]
)

# Line 685 (idx 684): omit Q. Thủ Đức (multi-level dup with Tỉnh lộ 43)
updates[684] = (
    "Những ngày qua hình ảnh về việc những người dân sống ở Tỉnh lộ 43 ( Q. Thủ Đức , TP. HCM ) phải kê hết đồ đạc trong nhà , có nơi nước ngập ngang cổ được chia sẻ rộng rãi trên mạng xã hội .",
    [([12, 13, 14], [33, 34, 35, 36], 'NEG')]
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

print(f"Batch 7: Successfully updated {len(updates)} records!")
