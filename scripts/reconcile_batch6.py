import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# Line 503 (idx 502): triều cường -> triều cường ở TPHCM
updates[502] = (
    "Theo đó , triều cường ở TPHCM dâng cao đã khiến đường Trần Xuân Soạn ( quận 7 ) ngập sâu từ 0 , 3 đến 0 , 5m , nước từ kênh Tẻ tràn qua bờ kè đổ vào nhà dân .",
    [([3, 4, 5, 6], [7, 8], 'NEG'),
     ([12, 13, 14, 15], [20, 21], 'NEG'),
     ([31, 32], [33, 34, 35, 36, 37, 38, 39, 40], 'NEG')]
)

# Line 507 (idx 506): Triều cường -> Triều cường ở TPHCM, omit 'mực nước' attribute
updates[506] = (
    "VOV . VN - Triều cường ở TPHCM đạt đỉnh vào đầu tháng 11 khiến mực nước các sông , kênh , rạch tại TPHCM dâng cao .",
    [([4, 5, 6, 7], [8, 9], 'NEU'),
     ([23], [24, 25], 'NEG')]
)

# Line 511 (idx 510): triều cường tại TP. HCM is [5, 6, 7, 8, 9] (no text change needed)
updates[510] = (
    "Sáng 18 - 10 , triều cường tại TP. HCM dâng cao , một số nơi tại quận 7 ngập chưa kịp rút do mưa chiều qua thì hứng thêm đợt triều đầu sáng nay . Tin nóng 20 / 09 / 2024",
    [([5, 6, 7, 8, 9], [10, 11], 'NEG'),
     ([16, 17], [18, 19, 20, 21], 'NEG')]
)

# Line 512 (idx 511): omit quận 7 (multi-level dup with đường Trần Xuân Soạn)
updates[511] = (
    "Triều cường vượt 1 , 65m cộng thêm mưa lớn khiến đường Trần Xuân Soạn ( quận 7 , TP. HCM ) ngập nhiều đoạn .",
    [([9, 10, 11, 12], [19, 20, 21], 'NEG')]
)

# Line 541 (idx 540): triều cường -> triều cường ở TPHCM, omit phường Tân Thuận
updates[540] = (
    "Có mặt tại đường Trần Xuân Soạn ( phường Tân Thuận , TP HCM ) , từ khoảng 17 giờ , triều cường ở TPHCM bắt đầu tràn bờ , nhanh chóng gây ngập sâu ở nhiều khu vực .",
    [([3, 4, 5, 6], [28, 29], 'NEG'),
     ([18, 19, 20, 21], [22, 23, 24, 25], 'NEG')]
)

# Line 545 (idx 544): triều cường -> triều cường ở TPHCM
updates[544] = (
    "Sống trên đường Trần Xuân Soạn , bà Đinh Thị Phương ( SN 1971 ) cho biết , cứ mỗi lần triều cường ở TPHCM dâng là nước lại tràn vào nhà .",
    [([2, 3, 4, 5], [23, 24, 25, 26, 27], 'NEG'),
     ([17, 18, 19, 20], [21], 'NEG')]
)

# Line 552 (idx 551): omit phường Tân Thuận (multi-level dup with đường Huỳnh Tấn Phát)
updates[551] = (
    "Trong khi đó , đường Huỳnh Tấn Phát ( phường Tân Thuận , TP HCM ) , nước tràn vào đường từ sớm ( khoảng 16 giờ ) , ngập sâu khoảng nửa bánh xe từ hơn từ 18 giờ , sau nước cũng xuống nhanh .",
    [([4, 5, 6, 7], [29, 30, 31, 32, 33, 34], 'NEG')]
)

# Line 560 (idx 559): omit xã Nhà Bè (multi-level dup with đường Lê Văn Lương)
updates[559] = (
    "Còn anh Lê Nguyên Tú , tiểu thương trên đường Lê Văn Lương ( xã Nhà Bè ) , chia sẻ : \" Con đường Lê Văn Lương năm nào cũng ngập mỗi khi rằm hoặc có mưa lớn , nhưng năm nay tình hình nặng hơn nhiều .",
    [([9, 10, 11, 12], [31], 'NEG')]
)

# Line 568 (idx 567): triều cường -> triều cường ở TPHCM
updates[567] = (
    "Cơ quan chuyên môn cảnh báo , đây là kỳ triều cường ở TPHCM cao trong năm , mức độ rủi ro thiên tai khu vực hạ lưu sông Sài Gòn được xác định ở cấp độ 2 .",
    [([10, 11, 12, 13], [14, 15, 16], 'NEU'),
     ([28, 29, 30], [34, 35, 36, 37], 'NEU')]
)

# Line 570 (idx 569): triều cường -> triều cường ở TPHCM
updates[569] = (
    "Chiều tối nay , đợt triều cường ở TPHCM lên đỉnh kết hợp với hoàn lưu bão đã khiến mực nước trên hệ thống sông Sài Gòn và kênh rạch dâng rất cao , nhiều trạm đo ghi nhận mực nước vượt báo động 3 , gây ngập sâu diện rộng tại các khu ven sông và nhiều hẻm trũng .",
    [([5, 6, 7, 8], [9, 10], 'NEU'),
     ([24, 25, 26], [30, 31, 32], 'NEG'),
     ([24, 25, 26], [47, 48, 49, 50], 'NEG')]
)

# Line 578 (idx 577): triều cường -> triều cường ở TPHCM
updates[577] = (
    "Đài Khí tượng – Thủy văn Nam Bộ và các cơ quan chức năng tiếp tục cảnh báo triều cường ở TPHCM có khả năng duy trì ở mức cao trong 24 – 48 giờ tới , đề nghị người dân chủ động di chuyển sớm , tránh các vùng trũng thấp và tuân thủ hướng dẫn của lực lượng chức năng .",
    [([18, 19, 20, 21], [25, 26, 27, 28, 29], 'NEU')]
)

# Line 583 (idx 582): omit Bình Tân (multi-level dup with đường Tên Lửa)
updates[582] = (
    "Dù ở khu vực trung tâm Bình Tân nhưng cứ mưa lớn là đường lại thành sông ” , anh Vương , một hộ kinh doanh trên đường Tên Lửa , chia sẻ .",
    [([27, 28, 29], [15, 16], 'NEG')]
)

# Line 588 (idx 587): omit TP. HCM (enclosing city), keep individual districts
updates[587] = (
    "Khoảng 15h hôm nay ( Chủ nhật ) , trên địa bàn TP. HCM xuất hiện mưa lớn kéo dài khiến nhiều tuyến đường ở TP Thủ Đức , Bình Thạnh , Gò Vấp , quận 12 … bị ngập nặng .",
    [([25, 26, 27], [38, 39, 40], 'NEG'),
     ([29, 30], [38, 39, 40], 'NEG'),
     ([32, 33], [38, 39, 40], 'NEG'),
     ([35, 36], [38, 39, 40], 'NEG')]
)

# Line 599 (idx 598): omit TP Thủ Đức (multi-level dup with đường Dương Văn Cam)
updates[598] = (
    "Cách đó không xa , tại đường Dương Văn Cam , TP Thủ Đức nước ngập gần lút bánh xe máy .",
    [([6, 7, 8, 9], [15, 16, 17, 18, 19, 20], 'NEG')]
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

print(f"Batch 6: Successfully updated {len(updates)} records!")
