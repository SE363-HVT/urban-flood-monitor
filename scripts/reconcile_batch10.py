import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# Line 911 (idx 910): omit Q. Bình Thạnh
updates[910] = (
    "Đường Nguyễn Hữu Cảnh ( Q. Bình Thạnh ) ngập nặng nhất - Ảnh : Thuận Thắng",
    [([0, 1, 2, 3], [7, 8, 9], 'NEG')]
)

# Line 912 (idx 911): omit Q. Bình Thạnh
updates[911] = (
    "Nước ngập tới yên xe trên đường Nguyễn Hữu Cảnh ( Q. Bình Thạnh ) - Ảnh : Thuận Thắng",
    [([6, 7, 8, 9], [1, 2, 3, 4], 'NEG')]
)

# Line 913 (idx 912): omit Q. Bình Thạnh
updates[912] = (
    "Xe chết máy hàng loạt trên đường Nguyễn Hữu Cảnh ( Q. Bình Thạnh ) - Ảnh : Thuận Thắng",
    [([6, 7, 8, 9], [1, 2, 3, 4], 'NEG')]
)

# Line 914 (idx 913): omit Q. Bình Thạnh
updates[913] = (
    "Nước tràn vào nhà dân ở đường Nguyễn Hữu Cảnh ( Q. Bình Thạnh ) - Ảnh : Thuận Thắng",
    [([6, 7, 8, 9], [1, 2, 3], 'NEG')]
)

# Line 920 (idx 919): omit Q. Bình Thạnh
updates[919] = (
    "Trước đó , từ chiều 15 - 9 , theo ghi nhận của PV Tuổi Trẻ , nước mưa ngập mênh mông các tuyến đường xung quanh bến xe miền Đông ( Q. Bình Thạnh ) như Đinh Bộ Lĩnh , Xô Viết Nghệ Tĩnh , quốc lộ 13 , Ung Văn Khiêm . . .",
    [([27, 28, 29, 30], [19, 20, 21], 'NEG'),
     ([37, 38, 39], [19, 20, 21], 'NEG'),
     ([41, 42, 43, 44], [19, 20, 21], 'NEG'),
     ([46, 47, 48], [19, 20, 21], 'NEG'),
     ([50, 51, 52], [19, 20, 21], 'NEG')]
)

# Line 921 (idx 920): omit Q. Bình Thạnh
updates[920] = (
    "Tại đường Nguyễn Xí ( Q. Bình Thạnh ) , nước ngập quá đầu gối khiến hàng trăm xe chết máy .",
    [([1, 2, 3], [11, 12, 13, 14], 'NEG')]
)

# Line 924 (idx 923): omit Q. Thủ Đức, Hóc Môn, Q. Bình Tân, Q. Bình Thạnh, Q. 2
updates[923] = (
    "Nhiều tuyến đường khác như Kha Vạn Cân , quốc lộ 13 , Linh Đông ( Q. Thủ Đức ) , Phan Văn Hớn ( Hóc Môn ) , đường Ấp Chiến Lược ( Q. Bình Tân ) , Bạch Đằng , Xô Viết Nghệ Tĩnh , Nguyễn Hữu Cảnh , Chu Văn An ( Q. Bình Thạnh ) , xa lộ Hà Nội đoạn ở cầu Rạch Chiếc ( Q. 2 ) . . . ngập nặng .",
    [([5, 6, 7], [76, 77], 'NEG'),
     ([9, 10, 11], [76, 77], 'NEG'),
     ([13, 14], [76, 77], 'NEG'),
     ([21, 22, 23], [76, 77], 'NEG'),
     ([29, 30, 31, 32], [76, 77], 'NEG'),
     ([39, 40], [76, 77], 'NEG'),
     ([42, 43, 44, 45], [76, 77], 'NEG'),
     ([47, 48, 49], [76, 77], 'NEG'),
     ([51, 52, 53], [76, 77], 'NEG'),
     ([60, 61, 62, 63], [76, 77], 'NEG'),
     ([66, 67, 68], [76, 77], 'NEG')]
)

# Line 944 (idx 943): omit quận 12, quận Gò Vấp, quận Bình Tân, quận Tân Phú
updates[943] = (
    "Ngoài ra , cơn mưa tối 17 / 9 cũng khiến các tuyến đường như : Nguyễn Văn Quá , Song Hành ( quận 12 ) ; Nguyễn Văn Khối , Thống Nhất ( quận Gò Vấp ) ; Phan Anh ( quận Bình Tân ) , Tô Hiệu ( quận Tân Phú ) ngập sâu .",
    [([16, 17, 18], [54, 55], 'NEG'),
     ([20, 21], [54, 55], 'NEG'),
     ([27, 28, 29], [54, 55], 'NEG'),
     ([31, 32], [54, 55], 'NEG'),
     ([39, 40], [54, 55], 'NEG'),
     ([47, 48], [54, 55], 'NEG')]
)

# Line 946 (idx 945): omit quận 1
updates[945] = (
    "Tối 25 / 11 , nước ngập rất cao tại giao lộ Trần Hưng Đạo - Nguyễn Khắc Nhu ( quận 1 , TPHCM ) khiến nhiều xe máy của người dân bị chết .",
    [([10, 11, 12, 13, 14, 15, 16, 17, 18], [6, 7, 8], 'NEG')]
)

# Line 951 (idx 950): omit quận 7
updates[950] = (
    "Cụ thể , tại đường Huỳnh Tấn Phát ( quận 7 ) bị ngập sâu khoảng nửa bánh xe từ sáng sớm .",
    [([4, 5, 6, 7], [13, 14, 15, 16, 17, 18], 'NEG')]
)

# Line 960 (idx 959): omit quận 12
updates[959] = (
    "Cơn mưa chiều nay cũng gây ngập nặng đường Nguyễn Văn Quá , Song Hành ( quận 12 ) khiến giao thông chiều đầu tuần hỗn loạn .",
    [([8, 9, 10, 11], [6, 7], 'NEG'),
     ([13, 14], [6, 7], 'NEG')]
)

# Line 993 (idx 992): omit phường 13, quận Bình Thạnh
updates[992] = (
    "Anh Tô Văn Nam đẩy xe giúp người dân thoát qua đoạn ngập đường Đặng Thuỳ Trâm ( phường 13 , quận Bình Thạnh cũ ) .",
    [([13, 14, 15, 16], [12], 'NEG')]
)

# Line 997 (idx 996): include prefix 'hẻm' -> hẻm quốc lộ 13 [36, 37, 38, 39], omit TP Thủ Đức, concise opinion 'ngập nước' [46, 47]
updates[996] = (
    "Theo ghi nhận của Tuổi Trẻ Online chiều 2 - 9 , một số đoạn thuộc các tuyến đường ở TP Thủ Đức như : đường 38 , số 6 , Tam Bình , một số hẻm quốc lộ 13 và Phạm Văn Đồng … vẫn ngập nước , người dân phải lội bì bõm .",
    [([25, 26], [46, 47], 'NEG'),
     ([28, 29], [46, 47], 'NEG'),
     ([31, 32], [46, 47], 'NEG'),
     ([36, 37, 38, 39], [46, 47], 'NEG'),
     ([41, 42, 43], [46, 47], 'NEG')]
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

print(f"Batch 10: Successfully updated {len(updates)} records!")
