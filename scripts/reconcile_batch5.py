import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

# Dictionary of updates for 0-indexed positions 400 to 499 (Lines 401 - 500)
updates = {}

# Line 401 (idx 400): triều cường tại TP. HCM is [9, 10, 11, 12, 13]
updates[400] = (
    "Chiều tối nay ( 7 / 11 ) , triều cường tại TP. HCM được dự báo tiếp tục đạt đỉnh trên các sông , kênh rạch hạ lưu , với mực nước tại trạm Phú An và Nhà Bè lên khoảng 1 , 77 - 1 , 80 m , vượt báo động III từ 0 , 17 - 0 , 20 m .",
    [([9, 10, 11, 12, 13], [19, 20], 'NEU'), ([34, 35, 36], [51, 52, 53, 54], 'NEU'), ([38, 39], [51, 52, 53, 54], 'NEU')]
)

# Line 402 (idx 401): omit Bình Thạnh (multi-level dup with bán đảo Thanh Đa)
updates[401] = (
    "Đợt triều cường tối 6 / 11 đã khiến nhiều tuyến đường ở quận 7 , Nhà Bè và các khu dân cư ven sông như bán đảo Thanh Đa ( Bình Thạnh ) bị ngập sâu , buộc người dân phải dùng bao cát và máy bơm để hạn chế nước tràn vào nhà .",
    [([13, 14], [35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54], 'NEG'), ([16, 17], [35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54], 'NEG'), ([26, 27, 28, 29], [35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54], 'NEG')]
)

# Line 403 (idx 402): opinion concise: không phải là tâm điểm ngập nặng
updates[402] = (
    "Đối với hành khách di chuyển đến sân bay Tân Sơn Nhất , các tuyến đường trục chính như Trường Sơn , Hoàng Văn Thụ , Cộng Hòa và Phan Đăng Lưu hiện không phải là tâm điểm ngập nặng , song vẫn có nguy cơ ùn tắc kéo dài vào giờ cao điểm do lưu lượng phương tiện dồn sang từ các tuyến ngập .",
    [([19, 20], [33, 34, 35, 36, 37, 38, 39], 'POS'), ([22, 23, 24], [33, 34, 35, 36, 37, 38, 39], 'POS'), ([26, 27], [33, 34, 35, 36, 37, 38, 39], 'POS'), ([29, 30, 31], [33, 34, 35, 36, 37, 38, 39], 'POS')]
)

# Line 405 (idx 404): tăng nguy cơ ngập is NEU
updates[404] = (
    "Điều này đồng nghĩa triều cường ở TPHCM và mưa có thể xảy ra cùng lúc , tăng nguy cơ ngập cục bộ và ùn tắc giao thông .",
    [([4, 5, 6, 7], [17, 18, 19, 20], 'NEU')]
)

# Line 409 (idx 408): omit phường Thủ Dầu Một (enclosing ward), keep specific khu phố Chánh Nghĩa and khu phố Phú Thọ
updates[408] = (
    "Tại phường Thủ Dầu Một , nước từ các con rạch tràn vào khu dân cư , gây ngập khu phố Chánh Nghĩa 6 , 7 , 8 , 9 ; khu phố Phú Thọ 4 , 5 , 6 với độ sâu 0 , 8 - 1 , 2m , ảnh hưởng khoảng 500 hộ dân .",
    [([19, 20, 21, 22], [17, 18], 'NEG'), ([31, 32, 33, 34], [44, 45, 46, 47, 48, 49], 'NEG')]
)

# Line 421 (idx 420): triều cường -> triều cường ở TPHCM
updates[420] = (
    "Khoảng 18h cùng ngày , triều cường ở TPHCM tiếp tục dâng cao , nước từ sông Sài Gòn tràn qua đê khiến khu vực bán đảo Thanh Đa ngập sâu , có nơi hơn 1m .",
    [([5, 6, 7, 8], [9, 10, 11, 12], 'NEG'), ([16, 17, 18], [19, 20, 21], 'NEG'), ([25, 26, 27, 28], [29, 30], 'NEG')]
)

# Line 424 (idx 423): triều cường -> triều cường ở TPHCM
updates[423] = (
    "Lực lượng chức năng túc trực hỗ trợ di dời tài sản , kê cao đồ đạc , đảm bảo an toàn cho người dân . Đến 19h , triều cường ở TPHCM đạt đỉnh .",
    [([29, 30, 31, 32], [33, 34], 'NEU')]
)

# Line 425 (idx 424): triều cường -> triều cường ở TPHCM
updates[424] = (
    "Kết hợp với triều cường ở TPHCM đạt mức lịch sử , nhiều khu vực sẽ ngập nặng .",
    [([3, 4, 5, 6], [7, 8, 9, 10], 'NEU')]
)

# Line 426 (idx 425): triều cường -> triều cường ở TPHCM
updates[425] = (
    "UBND TPHCM yêu cầu các sở , ngành , địa phương và đặc khu Côn Đảo kích hoạt cao điểm phòng chống thiên tai , trực ban 24 / 24 , triển khai các biện pháp đảm bảo an toàn cho người dân và công trình trước \" nguy cơ kép \" triều cường ở TPHCM đạt đỉnh đúng thời điểm bão số 13 Kalmaegi đổ bộ .",
    [([52, 53, 54, 55], [56, 57], 'NEU')]
)

# Line 430 (idx 429): sông Sài Gòn | cảnh báo ở cấp độ 2
updates[429] = (
    "Nguy cơ rủi ro thiên tai do triều cường tại hạ lưu sông Sài Gòn được cảnh báo ở cấp độ 2 .",
    [([12, 13, 14], [16, 17, 18, 19, 20, 21], 'NEU')]
)

# Line 431 (idx 430): omit TP. HCM (broad entity), keep TP Thủ Đức
updates[430] = (
    "Vào giờ tan tầm , hàng ngàn xe máy từ trung tâm TP. HCM về TP Thủ Đức ( cũ ) buộc phải đi chậm qua đoạn ngập .",
    [([15, 16, 17], [21, 22, 23, 24, 25, 26, 27], 'NEG')]
)

# Line 433 (idx 432): triều cường -> triều cường ở TPHCM
updates[432] = (
    "Đây là đợt triều cường ở TPHCM cao nhất trong năm và cũng được dự báo vượt mốc lịch sử nhiều năm trở lại đây , cho thấy ngập lụt đang là một thách thức không nhỏ của những đô thị như TP. HCM .",
    [([3, 4, 5, 6], [7, 8, 9, 10], 'NEU'), ([42, 43], [33, 34, 35, 36], 'NEG')]
)

# Line 445 (idx 444): triều cường -> triều cường ở TPHCM
updates[444] = (
    "Vất vả nhất là người dân tại khu vực bán đảo Bình Quới - Thanh Đa , trong những ngày triều cường ở TPHCM đạt đỉnh , lúc nào cũng thấp thỏm không yên , sợ nước tràn vào nhà bất cứ lúc nào .",
    [([11, 12], [30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43], 'NEG'),
     ([14, 15], [30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43], 'NEG'),
     ([20, 21, 22, 23], [24, 25], 'NEU')]
)

# Line 450 (idx 449): triều cường -> triều cường ở TPHCM
updates[449] = (
    "Theo dự báo , đợt triều cường ở TPHCM này còn duy trì ở mức rất cao trong 2 - 3 ngày tới , đặc biệt nguy cơ ngập sâu hơn nếu kết hợp với mưa lớn do hoàn lưu bão số 13 .",
    [([5, 6, 7, 8], [13, 14, 15, 16], 'NEU')]
)

# Line 453 (idx 452): Triều cường -> Triều cường ở TPHCM
updates[452] = (
    "Triều cường ở TPHCM đạt đỉnh gây ra ngập nặng , dẫn đến cảnh kẹt xe kéo dài nhiều tiếng trên nhiều trục đường Calmette .",
    [([0, 1, 2, 3], [4, 5], 'NEU'), ([23, 24], [8, 9], 'NEG')]
)

# Line 457 (idx 456): triều cường -> triều cường ở TPHCM
updates[456] = (
    "Nhiều ngày qua , triều cường ở TPHCM kết hợp với mưa lớn khiến nhiều tuyến đường ở TP. HCM bị ngập .",
    [([4, 5, 6, 7], [8, 9, 10, 11, 12], 'NEU'), ([18, 19], [20, 21], 'NEG')]
)

# Line 464 (idx 463): triều cường tại TP. HCM is [14, 15, 16, 17, 18]
updates[463] = (
    "Hôm nay , Đài Khí tượng thủy văn khu vực Nam Bộ dự báo triều cường tại TP. HCM có thể đạt đỉnh 1 , 8 m .",
    [([14, 15, 16, 17, 18], [21, 22, 23, 24, 25, 26], 'NEU')]
)

# Line 475 (idx 474): triều cường -> triều cường ở TPHCM
updates[474] = (
    "Mỗi khi triều cường ở TPHCM đạt đỉnh , tình trạng nước ngập kéo dài từ 30 phút đến 120 phút .",
    [([2, 3, 4, 5], [6, 7], 'NEU')]
)

# Line 476 (idx 475): omit quận 7 (multi-level dup with đường Trần Xuân Soạn)
updates[475] = (
    "Triều cường dâng cao gây ngập trên đường Trần Xuân Soạn ( quận 7 , TPHCM ) khiến việc đi lại của người dân gặp rất nhiều khó khăn ( Ảnh : Nam Anh ) .",
    [([7, 8, 9, 10], [5], 'NEG')]
)

# Line 479 (idx 478): triều cường -> triều cường ở TPHCM, omit quận 7
updates[478] = (
    "Anh Nguyễn Văn Thái ( quận 7 ) cho biết : \" Năm nào cũng vậy , cứ có triều cường ở TPHCM là tuyến đường này ngập sâu , nước tràn hết vào nhà , có hôm mấy chị phụ nữ đi té ngã ướt hết quần áo \" ( Ảnh : Thúy Hường ) .",
    [([19, 20, 21, 22], [27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48], 'NEG')]
)

# Line 480 (idx 479): triều cường -> triều cường ở TPHCM, omit quận 7
updates[479] = (
    "Tình trạng ngập nước do triều cường ở TPHCM kéo dài nhiều năm nay trên tuyến đường này nhưng không được các cơ quan chức năng giải quyết triệt để , bà con chúng tôi gặp nhiều bất tiện \" , chị Lý Thị Hoa ( quận 7 ) nói ( Ảnh : Thúy Hường ) .",
    [([4, 5, 6, 7], [2, 3], 'NEG')]
)

# Line 484 (idx 483): clean fallback, Triều cường ở TPHCM gây ngập
updates[483] = (
    "Triều cường ở TPHCM gây ngập khiến nhiều xe máy của người dân bị chết máy ( Ảnh : Nam Anh ) .",
    [([0, 1, 2, 3], [5], 'NEG'), ([0, 1, 2, 3], [13, 14, 15], 'NEG')]
)

# Line 485 (idx 484): triều cường -> triều cường ở TPHCM, omit quận 7 and quận Bình Thạnh
updates[484] = (
    "Tương tự , triều cường ở TPHCM còn gây ngập ở một số tuyến đường như Huỳnh Tấn Phát , đường số 20 ( quận 7 ) và khu dân cư Thanh Đa ( quận Bình Thạnh ) . . . khiến cuộc sống người dân bị đảo lộn ( Ảnh : Khoa Nguyễn ) .",
    [([3, 4, 5, 6], [9], 'NEG'), ([16, 17, 18], [9], 'NEG'), ([20, 21, 22], [9], 'NEG'), ([28, 29, 30, 31, 32], [9], 'NEG')]
)

# Line 489 (idx 488): omit huyện Bình Chánh (multi-level dup with đường quốc lộ 50)
updates[488] = (
    "Khoảng 20h , đường quốc lộ 50 ( huyện Bình Chánh ) vẫn còn ngập nước .",
    [([3, 4, 5, 6], [12, 13, 14, 15], 'NEG')]
)

# Line 491 (idx 490): triều cường tại TPHCM is [21, 22, 23, 24]
updates[490] = (
    "Theo thông tin từ Đài khí tượng thủy văn khu vực Nam Bộ , hôm nay , 18 / 10 , triều cường tại TPHCM dự kiến có thể đạt đỉnh 1 , 8m .",
    [([21, 22, 23, 24], [29, 30, 31, 32, 33], 'NEU')]
)

# Line 492 (idx 491): triều cường tại TP. HCM is [5, 6, 7, 8, 9]
updates[491] = (
    "Chiều 6 - 11 , triều cường tại TP. HCM đạt mức cao nhất từ đầu năm đến nay và vượt mốc lịch sử khiến nhiều khu vực lại chìm sâu trong biển nước .",
    [([5, 6, 7, 8, 9], [10, 11, 12, 13], 'NEU'), ([5, 6, 7, 8, 9], [29, 30, 31, 32, 33], 'NEG')]
)

# Apply updates
for idx, (new_text, new_trips) in updates.items():
    tokens = new_text.split()
    # verify triplets validity before applying
    for asp, opi, pol in new_trips:
        for a in asp:
            assert a < len(tokens), f"Idx {idx+1}: asp idx {a} out of range {len(tokens)}"
        for o in opi:
            assert o < len(tokens), f"Idx {idx+1}: opi idx {o} out of range {len(tokens)}"
    lines[idx] = f"{new_text}####{new_trips}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print(f"Batch 5: Successfully updated {len(updates)} records!")
