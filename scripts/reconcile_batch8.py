import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# Line 718 (idx 717): omit quận 12
updates[717] = (
    "Ghi nhận trên đường Phan Văn Hớn ( quận 12 ) nước ngập gần nửa mét khiến nhiều phương tiện chết máy . Đoạn ngập kéo dài khoảng 1km , có đoạn ngập sâu hơn nửa mét khiến không chỉ xe máy mà ô tô cũng chết máy .",
    [([3, 4, 5, 6], [12, 13, 14, 15], 'NEG')]
)

# Line 719 (idx 718): omit quận Bình Thạnh
updates[718] = (
    "Ghi nhận tại đường Bình Lợi ( quận Bình Thạnh ) , đoạn ngập dài hơn 1km .",
    [([3, 4, 5], [13, 14, 15, 16], 'NEG')]
)

# Line 722 (idx 721): omit phường 26, quận Bình Thạnh
updates[721] = (
    "Tương tự tại đường Ung Văn Khiêm , nhiều đoạn ngập sâu , một con hẻm đường Xô Viết Nghệ Tĩnh ( phường 26 , quận Bình Thạnh ) cũng bị ngập .",
    [([3, 4, 5, 6], [10, 11], 'NEG'),
     ([16, 17, 18, 19, 20], [30, 31], 'NEG')]
)

# Line 723 (idx 722): omit quận Gò Vấp
updates[722] = (
    "Còn tại đường Nguyễn Văn Khối ( Cây Trâm cũ , quận Gò Vấp ) , đoạn ngập dài hơn 200m khiến nhiều phương tiện bị chết máy phải đẩy bộ .",
    [([2, 3, 4, 5], [17, 18, 19, 20], 'NEG')]
)

# Line 734 (idx 733): omit enclosing districts Q. Bình Thạnh, Q. Tân Bình, Q. 7
updates[733] = (
    "Theo ghi nhận của PV Báo Thanh Niên , các tuyến đường như D5 , D1 ( Q. Bình Thạnh ) , Phan Huy Ích ( Q. Tân Bình ) , Nguyễn Thị Thập ( Q. 7 ) và nhiều tuyến đường khác tại Q. 4 , Q. 5 … ngập sâu trong nước .",
    [([13], [50, 51, 52, 53], 'NEG'),
     ([15], [50, 51, 52, 53], 'NEG'),
     ([22, 23, 24], [50, 51, 52, 53], 'NEG'),
     ([31, 32, 33], [50, 51, 52, 53], 'NEG'),
     ([44, 45], [50, 51, 52, 53], 'NEG'),
     ([47, 48], [50, 51, 52, 53], 'NEG')]
)

# Line 737 (idx 736): omit Q. Bình Thạnh
updates[736] = (
    "Tại giao lộ D1 - Điện Biên Phủ ( P. 25 , Q. Bình Thạnh ) , giao thông náo loạn vì một chiếc ô tô chết máy từ đêm 25_11 .",
    [([1, 2, 3, 4, 5, 6, 7], [19, 20], 'NEG')]
)

# Line 742 (idx 741): omit phường 26, quận Bình Thạnh
updates[741] = (
    "Đến 22h ngày 26 / 9 , nhiều ngôi nhà trong ngõ 13 , đường Đinh Bộ Lĩnh , phường 26 , quận Bình Thạnh , TP. HCM ( đoạn gần bến xe miền Đông ) vẫn bị nước bủa vây , ngập gần tới đầu gối .",
    [([14, 15, 16, 17], [42, 43, 44, 45, 46], 'NEG')]
)

# Line 748 (idx 747): omit P. 15, quận Tân Bình
updates[747] = (
    "Một khách sạn trên đường Cộng Hòa ( P. 15 , quận Tân Bình ) cũng bị nước ngoài đường tràn vào nhà gây ngập tầng hầm",
    [([4, 5, 6], [24, 25, 26], 'NEG')]
)

# Line 749 (idx 748): in-place expansion of triều cường -> triều cường ở TPHCM
updates[748] = (
    "Chiều 8 / 10 , triều cường ở TPHCM dâng cao khiến nhiều tuyến đường tại các quận 7 , Bình Tân và huyện Nhà Bè ngập nặng , xe chết máy , giao thông rối loạn trong nhiều giờ .",
    [([5, 6, 7, 8], [9, 10], 'NEG'),
     ([17, 18], [26, 27], 'NEG'),
     ([20, 21], [26, 27], 'NEG'),
     ([23, 24, 25], [26, 27], 'NEG')]
)

# Line 751 (idx 750): omit huyện Nhà Bè
updates[750] = (
    "Phụ huynh chở con loay hoay khi xe bị chết máy trên đường Nguyễn Bình ( huyện Nhà Bè ) .",
    [([12, 13, 14], [9, 10], 'NEG')]
)

# Line 752 (idx 751): omit quận Bình Thạnh
updates[751] = (
    "Theo đó , mưa lớn xảy ra đã làm các tuyến đường như : Điện Biên Phủ , Nguyễn Hữu Cảnh , Ung Văn Khiêm , quận Bình Thạnh bị ngập nước .",
    [([14, 15, 16], [30, 31], 'NEG'),
     ([18, 19, 20], [30, 31], 'NEG'),
     ([22, 23, 24], [30, 31], 'NEG')]
)

# Line 756 (idx 755): omit quận Bình Thạnh
updates[755] = (
    "Đồng thời , mưa lớn cũng làm tuyến đường Điện Biên Phủ nối ra đường Nguyễn Hữu Cảnh , quận Bình Thạnh cũng bị ngập sâu khiến nhiều xe gắn máy lưu thông bị chết máy phải dắt bộ trên đường ; nước tràn vào nhà dân gây ảnh hưởng đến đời sống sinh hoạt và kinh doanh buôn bán .",
    [([8, 9, 10, 11], [24, 25], 'NEG'),
     ([14, 15, 16, 17], [24, 25], 'NEG')]
)

# Line 762 (idx 761): omit phường Bình Thạnh
updates[761] = (
    "Tại phường Bình Thạnh , đường Ung Văn Khiêm đoạn gần cầu Sài Gòn , nước ngập sâu tới nửa mét , khiến giao thông tắc nghẽn cả đoạn dài .",
    [([5, 6, 7, 8], [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29], 'NEG')]
)

# Line 779 (idx 778): omit quận 6
updates[778] = (
    "Điển hình như đường Hồng Bàng , đoạn từ khu vực tòa nhà Thuận Kiều đến cầu vượt Cây Gõ ( quận 6 ) , cả đoạn đường ngập sâu đến nửa xe máy khiến hàng loạt phương tiện di chuyển qua đây bị chết máy .",
    [([3, 4, 5], [28, 29, 30, 31, 32, 33], 'NEG')]
)

# Line 783 (idx 782): omit quận 6
updates[782] = (
    "Tương tự , mưa lớn cũng khiến tuyến đường Lê Quang Sung ( quận 6 ) bị ngập nặng , gần như các phương tiện di chuyển vào đoạn đường này đều bị chết máy .",
    [([8, 9, 10, 11], [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34], 'NEG')]
)

# Line 784 (idx 783): omit quận 5 and quận 6
updates[783] = (
    "Trận mưa lớn chiều 8 / 9 cũng khiến nhiều tuyến đường khác như Tân Hưng , Phạm Hữu Chí , Thuận Kiều , Châu Văn Liêm ( quận 5 ) , Minh Phụng , khu Bình Phú ( quận 6 ) … bị ngập lênh láng .",
    [([14, 15], [44, 45, 46], 'NEG'),
     ([17, 18, 19], [44, 45, 46], 'NEG'),
     ([21, 22], [44, 45, 46], 'NEG'),
     ([24, 25, 26], [44, 45, 46], 'NEG'),
     ([32, 33], [44, 45, 46], 'NEG'),
     ([35, 36, 37], [44, 45, 46], 'NEG')]
)

# Line 786 (idx 785): omit quận Bình Thạnh, quận 2, quận Thủ Đức
updates[785] = (
    "Khoảng 30 phút sau , hàng loạt đường như Nguyễn Hữu Cảnh , Nguyễn Xí , Ung Văn Khiêm ( quận Bình Thạnh ) , Quốc Hương ( quận 2 ) , Hiệp Bình ( quận Thủ Đức ) . . . ngập nặng .",
    [([9, 10, 11], [42, 43], 'NEG'),
     ([13, 14], [42, 43], 'NEG'),
     ([16, 17, 18], [42, 43], 'NEG'),
     ([25, 26], [42, 43], 'NEG'),
     ([32, 33], [42, 43], 'NEG')]
)

# Line 788 (idx 787): include prefix 'cầu' -> cầu Sài Gòn is [4, 5, 6]
updates[787] = (
    "Đoạn từ gần châu cầu Sài Gòn đến đến gần tòa nhà The Marnor khoảng 300 m có nhiều lô cốt công trình , mặt đường bị thu hẹp khiến người dân khó khăn hơn khi vượt qua \" rốn ngập \" .",
    [([4, 5, 6], [40], 'NEG')]
)

# Line 798 (idx 797): omit quận 2
updates[797] = (
    "Đợt triều cường giữa tháng 5 đạt đỉnh khiến đường ở khu Thảo Điền ( quận 2 , TP. HCM ) ngập kéo dài , nhiều phương tiện chết máy khi đi qua khúc ngập cuối giờ chiều .",
    [([11, 12, 13], [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37], 'NEG')]
)

# Line 799 (idx 798): omit phường Thảo Điền and quận 2
updates[798] = (
    "Chiều 8 / 5 , đợt triều cường giữa tháng 5 đạt đỉnh điểm khiến một đoạn dài trên đường Nguyễn Văn Hưởng ( phường Thảo Điền , quận 2 , TP. HCM ) bị ngập sâu .",
    [([19, 20, 21, 22], [35, 36], 'NEG')]
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

print(f"Batch 8: Successfully updated {len(updates)} records!")
