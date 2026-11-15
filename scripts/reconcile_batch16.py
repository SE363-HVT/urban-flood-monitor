import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# Line 1518 (idx 1517): fix 3-token drift -> triều cao ở TPHCM [11, 12, 13, 14] | mênh mông nước [37, 38, 39] NEG
updates[1517] = (
    "Tôi đi làm qua đoạn này suốt , biết hôm nay triều cao ở TPHCM nên cũng không mang giày mà mang dép , chứ mang giày chắc bỏ đôi giày luôn ” , nhìn con đường mênh mông nước , anh ngao ngán . cao an biên cao an biên",
    [([11, 12, 13, 14], [37, 38, 39], 'NEG')]
)

# Line 1567 (idx 1566): omit enclosing district quận 1
updates[1566] = (
    "Chiều 8 / 11 , nhiều tuyến đường trung tâm TPHCM như Calmette , Nguyễn Thái Bình , Nguyễn Thái Học , Bùi Viện , Ký Con . . . bất ngờ chìm trong \" biển \" nước do mưa lớn kết hợp triều cường . Đây là cảnh tượng hiếm thấy , gây bất ngờ cho cả người dân và du khách . Theo ghi nhận của Dân trí , đợt triều cường chiều 8 / 11 đã gây ngập nặng tại nhiều tuyến đường thuộc quận 1 cũ . Những đợt sóng nước lớn do ô tô tạo ra khiến nước tràn mấp mé cửa nhà dân . Người đi xe máy chao đảo tay lái , nhiều người bị nước văng ướt sũng . Một số buộc phải quay đầu tìm đường khác . Mặc dù TPHCM vừa trải qua đợt triều cường được xem là lịch sử , nhưng theo người dân địa phương , đây là lần đầu tiên khu vực trung tâm bị ngập sâu đến vậy . Đến 20h , nước tại các tuyến đường trung tâm rút chậm . Theo Đài Khí tượng Thủy văn Nam Bộ , trong 24 giờ qua , mực nước đỉnh triều cao nhất ngày tại hầu hết các trạm trên sông Sài Gòn xuống chậm và vẫn ở mức cao , trên báo động 3 khoảng 0 , 13 - 0 , 26m . Đến 7h ngày 8 / 11 , đỉnh triều cao nhất ngày thực đo tại một số trạm như Phú An ( sông Sài Gòn ) và Nhà Bè ( kênh Đồng Điền ) đạt khoảng 1 , 66m ( trên báo động 3 ) . Thực hiện : Bảo Quyên # dantrinews # LearnOnTikTok # xuhuong",
    [([12], [32], 'NEG'),
     ([14, 15, 16], [32], 'NEG'),
     ([18, 19, 20], [32], 'NEG'),
     ([22, 23], [32], 'NEG'),
     ([25, 26], [32], 'NEG')]
)

# Line 1585 (idx 1584): omit q7
updates[1584] = (
    "Nguyễn Thị Thập q7 ngập trong biển nước . # lulut # ngapnuoc # sgngaymua # q7",
    [([0, 1, 2], [4, 5, 6, 7], 'NEG')]
)

# Line 1589 (idx 1588): include sông Sài Gòn [2, 3, 4] | tràn qua bờ kè [5, 6, 7, 8], Thanh Đa [17, 18] | ngập sâu [28, 29], omit phường Bình Quới
updates[1588] = (
    "Nước từ sông Sài Gòn tràn qua bờ kè , chảy vào các con hẻm khu vực Thanh Đa , phường Bình Quới , hàng chục hộ dân ngập sâu , đồ đạc hư hỏng , tối 24 / 10 👇 👇 # saigon # ngapnuoc # honghot",
    [([2, 3, 4], [5, 6, 7, 8], 'NEG'),
     ([17, 18], [28, 29], 'NEG')]
)

# Line 1596 (idx 1595): omit Quận 7
updates[1595] = (
    "Ngập ở Sài gòn Đường Phạm Hữu Lầu , Quận 7 # nướcngậpcảđườngđi # ngậpđường",
    [([4, 5, 6, 7], [0], 'NEG')]
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

print(f"Batch 16: Successfully updated {len(updates)} records!")
