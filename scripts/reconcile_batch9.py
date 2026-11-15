import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# Line 814 (idx 813): omit Q. Bình Thạnh
updates[813] = (
    "Đến 19h , tuyến đường Nguyễn Hữu Cảnh ( Q. Bình Thạnh ) còn bị ngập sâu hơn nửa bánh xe khiến nhiều người phải bì bõm lội nước vì xe chết máy .",
    [([4, 5, 6, 7], [15, 16, 17, 18, 19, 20], 'NEG')]
)

# Line 821 (idx 820): omit Q. Bình Thạnh and Q. 9
updates[820] = (
    "Công ty TNHH một thành viên thoát nước đô thị cho biết có hơn 43 điểm ngập trong mưa rải điều trên địa bàn TP. Trong đó ngập nặng nhất là tuyến Nguyễn Hữu Cảnh ( Q. Bình Thạnh ) và Lã Xuân Oai ( Q. 9 ) ngập từ 0 , 4 - 0 , 7 mét .",
    [([32, 33, 34], [27, 28, 29], 'NEG'),
     ([41, 42, 43], [27, 28, 29], 'NEG')]
)

# Line 827 (idx 826): omit quận Bình Thạnh
updates[826] = (
    "11h đêm , những chiếc xe hơi vẫn nằm im lìm trên đường Nguyễn Hữu Cảnh , quận Bình Thạnh - nơi được coi là \" rốn ngập \" của TP",
    [([12, 13, 14, 15], [8, 9, 10], 'NEG')]
)

# Line 831 (idx 830): omit quận Phú Nhuận
updates[830] = (
    "Đến 23h , tầng hầm của một nhà hàng trên đường Phan Xích Long ( quận Phú Nhuận ) vẫn ngập nước .",
    [([10, 11, 12, 13], [20, 21], 'NEG')]
)

# Line 836 (idx 835): omit Q. Bình Thạnh
updates[835] = (
    "Còn tại đường Nguyễn Xí ( Q. Bình Thạnh , TP. HCM ) , đoạn giao với đường Đinh Bộ Lĩnh đến Quốc lộ 13 , nước mưa dâng cao khiến nhiều xe đi qua đoạn đường này bị chết máy .",
    [([2, 3, 4], [28, 29], 'NEG')]
)

# Line 842 (idx 841): include prefix 'đường' for đường Ung Văn Khiêm [8, 9, 10, 11], omit quận Bình Thạnh, TP Thủ Đức
updates[841] = (
    "Mưa lớn kéo dài gây ngập các tuyến đường Ung Văn Khiêm ( quận Bình Thạnh ) , đường Hiệp Bình , Lê Văn Việt ( TP Thủ Đức ) . . .",
    [([8, 9, 10, 11], [5], 'NEG'),
     ([18, 19, 20], [5], 'NEG'),
     ([22, 23, 24], [5], 'NEG')]
)

# Line 883 (idx 882): omit P. 19, Q. Bình Thạnh
updates[882] = (
    "Dù nhiều tuyến đường trên địa bàn TP. HCM ngập sâu , nhưng đường Nguyễn Hữu Cảnh ( P. 19 , Q. Bình Thạnh ) tối cùng ngày sạch ráo nước .",
    [([13, 14, 15, 16], [28, 29, 30], 'POS')]
)

# Line 888 (idx 887): omit P. 14, quận Gò Vấp
updates[887] = (
    "Trên đường Phan Huy Ích đoạn qua P. 14 ( quận Gò Vấp ) , nước ngập một đoạn kéo dài hơn 1km , phương tiện qua lại gặp nhiều khó khăn .",
    [([1, 2, 3, 4], [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], 'NEG')]
)

# Line 891 (idx 890): omit quận 6
updates[890] = (
    "Đặc biệt , đoạn dưới chân cầu Rạch Cây ( thuộc quận 6 ) , nước mưa ngập nửa bánh xe .",
    [([6, 7, 8], [17, 18, 19, 20], 'NEG')]
)

# Line 892 (idx 891): omit quận 5
updates[891] = (
    "Phương tiện lưu thông cũng phải chạy với tốc độ chậm một đoạn dài trên đường Châu Văn Liêm ( quận 5 ) , do ngập nước khá cao .",
    [([15, 16, 17, 18], [25, 26, 27, 28], 'NEG')]
)

# Line 900 (idx 899): omit enclosing districts quận Gò Vấp, quận Tân Bình, quận Bình Thạnh, quận Bình Tân
updates[899] = (
    "Theo ghi nhận , tình trạng ngập nặng đã xảy ra tại đường Cây Trâm , Công viên Làng Hoa ( quận Gò Vấp ) , Phan Huy Ích ( quận Tân Bình ) , Nguyễn Xí , Đinh Bộ Lĩnh , D2 , Ung Văn Khiêm ( quận Bình Thạnh ) , An Dương Vương , Phan Anh ( quận Bình Tân ) , . . .",
    [([12, 13, 14], [6, 7], 'NEG'),
     ([16, 17, 18, 19], [6, 7], 'NEG'),
     ([26, 27, 28], [6, 7], 'NEG'),
     ([35, 36], [6, 7], 'NEG'),
     ([38, 39, 40], [6, 7], 'NEG'),
     ([42], [6, 7], 'NEG'),
     ([44, 45, 46], [6, 7], 'NEG'),
     ([53, 54, 55], [6, 7], 'NEG'),
     ([57, 58], [6, 7], 'NEG')]
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

print(f"Batch 9: Successfully updated {len(updates)} records!")
