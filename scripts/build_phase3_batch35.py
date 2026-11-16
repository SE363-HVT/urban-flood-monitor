# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn chuẩn hóa cho Phase 3 - Batch 35 (Records 3401 - 3500).
Tuân thủ 100% tài liệu BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md.
"""

batch35_data = [
    # Rec 3401: Đã có đường Phạm Văn Đồng
    ("Cơn mưa lớn khiến đường Phạm Văn Đồng - con đường nội đô đẹp nhất TPHCM có đoạn ngập sâu lút bánh xe máy , giao thông tê liệt .", [
        ([4, 5, 6, 7], [18, 19, 20, 21, 22, 23], 'NEG'),
        ([4, 5, 6, 7], [25, 26, 27, 28], 'NEG'),
    ]),

    # Rec 3402: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhiều người di chuyển xe máy qua đây bị chết máy , xe chao đảo .", [
        ([1], [12, 13], 'NEG'),
        ([1], [16, 17], 'NEG'),
    ]),

    # Rec 3403: Đã có đường Phạm Văn Đồng, TP Thủ Đức
    ("Đến 19h tối 20 - 5 , tình hình giao thông trên đường Phạm Văn Đồng đoạn qua TP Thủ Đức vẫn hết sức căng thẳng vì một đoạn bị ngập .", [
        ([12, 13, 14, 15], [22, 23, 24, 25], 'NEG'),
        ([12, 13, 14, 15], [29, 30], 'NEG'),
        ([18, 19, 20], [29, 30], 'NEG'),
    ]),

    # Rec 3404: Đã có đường Phạm Văn Đồng, TP Thủ Đức
    ("Đến 19h ngày 20 - 5 , tình hình giao thông trên đường Phạm Văn Đồng ( TP Thủ Đức , TP. HCM ) vẫn ùn ứ vì một đoạn bị ngập .", [
        ([12, 13, 14, 15], [25, 26], 'NEG'),
        ([12, 13, 14, 15], [30, 31], 'NEG'),
        ([17, 18, 19], [30, 31], 'NEG'),
    ]),

    # Rec 3405: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Một số xe máy cố gắng chạy qua bị nước vào động cơ , tắt máy phải dẫn bộ .", [
        ([1], [17, 18], 'NEG'),
        ([1], [19, 20, 21], 'NEG'),
    ]),

    # Rec 3406: Đã có Vành đai 3, Phạm Văn Đồng
    ("‼ ️ CHẢ HIỂU KIỂU GÌ : Vành đai 3 trên cao quãng Phạm Văn Đồng đang bị ngập nước .", [
        ([7, 8, 9], [17, 18, 19], 'NEG'),
        ([13, 14, 15], [17, 18, 19], 'NEG'),
    ]),

    # Rec 3407: Đã có TP. HCM, TP Thủ Đức
    ("NHIỀU TUYẾN ĐƯỜNG Ở TP. HCM ĐANG NGẬP SÂU Cơn mưa sáng 25 - 5 , khiến không ít con đường tại TP HCM , trong đó đáng nói nhất là TP Thủ Đức , ngập sâu vào giờ cao điểm khiến nhiều người vất vả khi đi làm .", [
        ([4, 5], [7, 8], 'NEG'),
        ([31, 32, 33], [35, 36], 'NEG'),
        ([31, 32, 33], [44, 45], 'NEG'),
    ]),

    # Rec 3408: Cắt cụt đuôi câu 'ngập U' -> REJECT
    ("Tại TP. Hồ Chí Minh , Sáng 25 - 5 , Ứng dụng cảnh báo ngập U", []),

    # Rec 3409: Đoạn trích ngắn so sánh -> REJECT
    ("Tại TP. Hồ Chí Minh , So với đường thì nước ngập khoảng 1 , 2m .", []),

    # Rec 3410: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Hậu quả là hàng chục nhà dân sống xung quanh khu vực này bị nước tràn vào nhà không chỉ thiệt hại về tài sản mà còn ảnh hưởng nghiêm trọng đến sinh hoạt .", [
        ([1], [17, 18, 19, 20, 21], 'NEG'),
        ([1], [25, 26], 'NEG'),
        ([1], [32, 33, 34, 35], 'NEG'),
    ]),

    # Rec 3411: Đã có D2 NỐI DÀI, CẦU THANH ĐA, công viên Tầm Vu
    ("TRIỀU CƯỜNG DÂNG CAO GÂY NGẬP ĐOẠN ĐƯỜNG TỪ D2 NỐI DÀI TỚI CẦU THANH ĐA Triều cường dâng cao sát mép bờ chắn tại công viên Tầm Vu , nước tràn nhiều ra đường gây ngập một đoạn đường dài .", [
        ([9, 10, 11], [4, 5], 'NEG'),
        ([13, 14, 15], [4, 5], 'NEG'),
        ([25, 26, 27, 28], [35, 36], 'NEG'),
    ]),

    # Rec 3412: Đã có TP Hồ Chí Minh
    ("TP Hồ Chí Minh ngập sâu do triều cường", [
        ([0, 1, 2, 3], [4, 5], 'NEG'),
    ]),

    # Rec 3413: Đã có TP. HCM
    ("Liên tiếp té ngã do triều cường dâng cao Triều cường trên sông Sài Gòn dâng cao khiến một số khu vực thấp trũng trên địa bàn TP. HCM bị ngập .", [
        ([27, 28], [29, 30], 'NEG'),
    ]),

    # Rec 3414: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhất là một số tuyến đường ven sông bị ngập sâu khiến nhiều người tham gia giao thông gặp nhiều khó khăn .", [
        ([1], [12, 13], 'NEG'),
        ([1], [21, 22, 23, 24], 'NEG'),
    ]),

    # Rec 3415: Cắt cụt đuôi câu 'TP. HCM n' -> REJECT
    ("🛑 TRUNG TÂM TP. HCM MÊNH MÔNG NƯỚC SAU CƠN MƯA LỚN TỐI 4 . 11 ‼ ️ Mưa lớn tối hôm qua ( 4 . 11 ) : Nhiều tuyến đường ở trung tâm TP. HCM mênh mông nước ‼ Cơn mưa lớn kéo dài nhiều giờ tối 4 . 11 khiến một số con đường ở trung tâm TP. HCM n", []),

    # Rec 3416: Bình luận từ ngữ -> REJECT
    ("Nam bộ đang bước vào mùa mưa & \" ngập \" là từ được nhiều người dân tại TPHCM nhắc đến lúc này .", []),

    # Rec 3417: Cắt cụt đuôi câu 'căn n' -> REJECT
    ("Tại TP. Hồ Chí Minh , Cũng vì sống chung với ngập quá lâu , mà ở những nơi được coi rốn ngập của TP , xuất hiện con đường lạ , căn n", []),

    # Rec 3418: Cắt cụt đuôi câu ', T' -> REJECT
    ("⛈ ÍT NHẤT 18 TUYẾN ĐƯỜNG Ở TP. HCM BỊ NGẬP TRONG CƠN MƯA CHIỀU 2 / 6 Cơn mưa chiều hôm qua 2 / 6 khiến nhiều điểm ngập ở TPHCM như : đường Phan Văn Hớn , Song Hành Quốc lộ 22 ( Quận 12 ) , Quốc Hương , Nguyễn Văn Hưởng , Thảo Điền , T", []),

    # Rec 3419: Nhận định chung chung -> REJECT
    ("Tại TP. Hồ Chí Minh , Sau cơn mưa , đường sẽ ngập .", []),

    # Rec 3420: Đã có đường số 5, khu dân cư Intresco 13E
    ("Những ngày qua , phụ huynh , học sinh Trường tiểu học Lê Quý Đôn ( đường số 5 , khu dân cư Intresco 13E , ấp 5 , xã Phong Phú , huyện Bình Chánh , TP. HCM ) và cư dân ở khu vực này rất vất vả khi đi lại , bởi các con đường bị ngập sâu do triều cường .", [
        ([16, 17, 18], [47, 48, 49], 'NEG'),
        ([16, 17, 18], [58, 59, 60], 'NEG'),
        ([20, 21, 22, 23, 24], [58, 59, 60], 'NEG'),
    ]),

    # Rec 3421: Cắt cụt đuôi câu 'mức ngậ' -> REJECT
    ("DANH SÁCH CHI TIẾT 38 TUYẾN ĐƯỜNG BỊ NGẬP NẶNG KHI MƯA LỚN TẠI TP. HCM Theo báo cáo của Trung tâm Quản lý hạ tầng kỹ thuật TP ( thuộc Sở Xây dựng TP. HCM ) , cơn mưa chiều tối 6 - 8 đã gây ngập 38 tuyến đường trên địa bàn TP với mức ngậ", []),

    # Rec 3422: Đã có Quốc lộ 50
    ("Quốc lộ 50 hiện tại nước ngập qua bánh xe .", [
        ([0, 1, 2], [5, 6, 7, 8, 9], 'NEG'),
    ]),

    # Rec 3423: Đã có Quốc Lộ 50, Bình Hưng, Bình Chánh
    ("Ngay Lúc Này Mưa Ngập Ở Quốc Lộ 50 Bình Hưng Bình Chánh TPHCM", [
        ([6, 7, 8], [3, 4], 'NEG'),
        ([9, 10], [3, 4], 'NEG'),
        ([11, 12], [3, 4], 'NEG'),
    ]),

    # Rec 3424: Đã cắt bỏ tiền tố thừa, giữ QL50
    ("QL50 ngập hơn nửa bánh xe , bà con chú ý lộ trình di chuyển 🥹", [
        ([0], [1, 2, 3, 4, 5], 'NEG'),
    ]),

    # Rec 3425: Đã có Quốc lộ 50
    ("Mưa to và triều cường gây ngập , ùn tắc kéo dài ở Quốc lộ 50 Ảnh Lao Động", [
        ([13, 14, 15], [5, 6], 'NEG'),
        ([13, 14, 15], [8, 9, 10, 11], 'NEG'),
    ]),

    # Rec 3426: Đã có quốc lộ 50, xã Bình Hưng, huyện Bình Chánh
    ("Người dân TP. HCM than trời vì triều cường ngập nhà hơn 10 năm Những tháng cuối năm , hàng chục hộ dân sống trên quốc lộ 50 , đoạn qua xã Bình Hưng , huyện Bình Chánh ( TP. HCM ) , phải khốn khổ trăm bề vì ngập nước do triều cường .", [
        ([25, 26, 27], [44, 45, 46, 47], 'NEG'),
        ([25, 26, 27], [49, 50], 'NEG'),
        ([31, 32, 33], [49, 50], 'NEG'),
        ([35, 36, 37], [49, 50], 'NEG'),
    ]),

    # Rec 3427: Đã có Quốc lộ 50
    ("Quốc lộ 50 ngập kẹt xe lên đến nguyên văn linh ae đi đường khác nha", [
        ([0, 1, 2], [3], 'NEG'),
        ([0, 1, 2], [4, 5], 'NEG'),
    ]),

    # Rec 3428: Đã có Mã Lò, Tân Hoà Đông
    ("Ngập Mã Lò , Ngập Tân Hoà Đông . . . .", [
        ([1, 2], [0], 'NEG'),
        ([5, 6, 7], [4], 'NEG'),
    ]),

    # Rec 3429: Không có ngập lụt -> REJECT
    ("Tại TP. Hồ Chí Minh , Xe khác ngta chết máy hết .", []),

    # Rec 3430: Đã có đường Mã Lò
    ("Trận mưa to khiến trước cổng UBND phường và đoạn đường Mã Lò ngập nặng .", [
        ([10, 11, 12], [13, 14], 'NEG'),
    ]),

    # Rec 3431: Không có ngập lụt (chỉ có ùn tắc) -> REJECT
    ("Đoạn giao lộ Mã Lò - Hương Lộ 2 bị ùn tắc nghiêm trọng .", []),

    # Rec 3432: Dân quân hỗ trợ (People role) -> REJECT
    ("Tại TP. Hồ Chí Minh , Chi đoàn Dân Quân phường Bình Trị Đông A đã cùng nhau hỗ trợ dắt phụ các xe bị chết máy .", []),

    # Rec 3433: Khắc phục hành chính -> REJECT
    ("Các vị trí xung yếu ở Bình Quới được khắc phục để hạn chế ngập nước triều cường", []),

    # Rec 3434: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , 👉 Hàng chục hộ dân bị ngập sâu , nhiều tài sản hư hỏng nặng .", [
        ([1], [9, 10], 'NEG'),
        ([1], [15, 16, 17], 'NEG'),
    ]),

    # Rec 3435: Đã có Thanh Đa, phường Bình Quới
    ("Nước từ sông Sài Gòn tràn qua bờ kè , chảy vào các con hẻm khu vực Thanh Đa , phường Bình Quới , hàng chục hộ dân ngập sâu , đồ đạc hư hỏng , tối 24 / 10 👇 👇 # VnExpress", [
        ([17, 18], [28, 29], 'NEG'),
        ([17, 18], [33, 34], 'NEG'),
        ([20, 21, 22], [28, 29], 'NEG'),
        ([20, 21, 22], [33, 34], 'NEG'),
    ]),

    # Rec 3436: Đã có đường Bình Quới
    ("🤷 Triều cường dâng cao ở TP. HCM : Nhà ngập đến nửa đêm , người dân hì hục tát nước Đến 0 giờ ngày 24 . 10 , nhiều hộ dân ở đường Bình Quới ( TP. HCM ) vẫn hì hục tát nước vì triều cường dâng cao tràn vào nhà , gây ngập nặng kéo dài suốt nhiều giờ .", [
        ([33, 34, 35], [50, 51, 52], 'NEG'),
        ([33, 34, 35], [54, 55, 56], 'NEG'),
    ]),

    # Rec 3437: Đã có Thanh Đa, phường Bình Quới
    ("' Chưa thấy triều cường nào lớn như năm nay ' , người dân Thanh Đa trắng đêm giữ bờ kè Tối 24 / 10 , triều cường vượt đỉnh khiến khu bán đảo Thanh Đa ( phường Bình Quới , TP. HCM ) ngập sâu .", [
        ([34, 35], [44, 45], 'NEG'),
        ([37, 38, 39], [44, 45], 'NEG'),
    ]),

    # Rec 3438: Đã có Bình Quới, phường Bình Quới
    ("Người dân rốn ngập Bình Quới ( TP. HCM ) vẫn còn khổ với con nước Đến chiều 25 / 10 , nhiều nơi tại phường Bình Quới , TP. HCM vẫn còn đang ngập sâu , ảnh hưởng đến sinh hoạt .", [
        ([4, 5], [33, 34, 35], 'NEG'),
        ([25, 26, 27], [33, 34, 35], 'NEG'),
        ([25, 26, 27], [37, 38, 39, 40, 41], 'NEG'),
    ]),

    # Rec 3439: Đã có TP. HCM
    ("⛈ NGƯỜI DÂN TP. HCM THỨC TRẮNG ĐÊM CHẠY TRIỀU CƯỜNG ☔ ️ Chiều 23 / 10 , triều cường đầu tháng 9 Âm lịch dâng cao , khiến nhiều tuyến đường trũng ở TP. HCM ngập nặng , cuộc sống người dân đảo lộn .", [
        ([3, 4], [36, 37], 'NEG'),
        ([34, 35], [36, 37], 'NEG'),
        ([34, 35], [43, 44], 'NEG'),
    ]),

    # Rec 3440: Cắt cụt đuôi câu 'đường Bìn' -> REJECT
    ("Người dân vất vả di chuyển trên đường Bìn", []),

    # Rec 3441: Quy hoạch tương lai + cắt cụt -> REJECT
    ("BÁN ĐẢO THANH ĐA SẼ TRỞ THÀNH KHU ĐÔ THỊ VÀ CÔNG VIÊN NGẬP NƯỚC GIỮA TPHCM Theo quy hoạch được duyệt , trung tâm bán đảo Thanh Đa sẽ có tòa tháp cao 70 tầng , các khu vực khác sẽ trở thành khu đô thị , bến du thuyền , tổ hợp vui chơi ,", []),

    # Rec 3442: Đã có Khu du lịch Bình Quới
    ("Khu du lịch Bình Quới ở TP HCM ngập một mét !", [
        ([0, 1, 2, 3, 4], [8, 9, 10], 'NEG'),
    ]),

    # Rec 3443: Đã có Khu du lịch Bình Quới
    ("Nước sông Sài Gòn dâng cao làm vỡ tường chắn khiến Khu du lịch Bình Quới rộng 3 . 500 m2 ngập sâu , gần 40 phòng nghỉ , khu chức năng bị hư hại .", [
        ([11, 12, 13, 14, 15], [21, 22], 'NEG'),
        ([11, 12, 13, 14, 15], [32, 33, 34], 'NEG'),
    ]),

    # Rec 3444: Đã có phường Bình Quới, TP. HCM
    ("Tối 24 . 10 . 2025 , triều cường dâng cao khiến nhiều tuyến hẻm tại phường Bình Quới , TP. HCM ngập nặng .", [
        ([16, 17, 18], [22, 23], 'NEG'),
        ([20, 21], [22, 23], 'NEG'),
    ]),

    # Rec 3445: Cắt cụt đuôi câu '. . .' -> REJECT
    ("Nhật ký ngập Bình Quới . . .", []),

    # Rec 3446: Triều cường mồ côi -> Quy tắc 6 mở rộng in-place
    ("Bữa đầu tiên triều cường ở TPHCM thì tràn đê , trước nhà ngập cao .", [
        ([3, 4, 5, 6], [13, 14], 'NEG'),
    ]),

    # Rec 3447: Chuyện gia đình tản mạn -> REJECT
    ("Tại TP. Hồ Chí Minh , Bữa đó trước nhà ngập xong ngập kế bên , tràn vòng phía sau nhà bếp lên .", []),

    # Rec 3448: Thuận An, Bình Dương -> REJECT tỉnh ngoài
    ("Cơn mưa như trút từ trưa đến chiều nay 16 - 4 khiến tuyến đường Quốc lộ 13 , Tp Thuận An , Bình Dương ( giáp phường Hiệp Bình Phước , Thủ Đức ) ngập nặng .", []),

    # Rec 3449: Không có từ ngập lụt -> REJECT
    ("Tại TP. Hồ Chí Minh , Nhiều xe chết máy phải đẩy bộ , giao thông hỗn loạn .", []),

    # Rec 3450: Thuận An -> REJECT tỉnh ngoài
    ("Quốc lộ 13 đoạn qua thị xã Thuận An ngập nặng , hàng ngàn phương tiện \" chìm sâu \" trong nước .", []),

    # Rec 3451: Bến Cát Bình Dương -> REJECT tỉnh ngoài
    ("📍 Trạm CSGT Quốc Lộ 13 phát hiện dùng xe thùng chở người dân qua vùng ngập nước ở cầu Quan , Bến Cát Bình Dương sáng nay .", []),

    # Rec 3452: Lotte Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Thông tin tại hiện trường Hiện tại QL13 hướng 2 chiều từ cây Xăng số 4 đến Lotte Bình Dương đang ùn tắc giao thông , lượng xe duy chuyển chậm và nhiều xe bị chết máy vì ngập lụt .", []),

    # Rec 3453: Lái Thiêu (Bình Dương) + cắt cụt -> REJECT tỉnh ngoài
    ("Tại trung tâm phường Lái Thiêu lượng xe đổ về đông do QL13 bị ùn tắc ch", []),

    # Rec 3454: Cắt cụt đuôi câu 'quá trình di' -> REJECT
    ("Tại TP. Hồ Chí Minh , Tình trạng “ cứ trời mưa , đường thành sông ” khiến người dân lo lắng trong quá trình di", []),

    # Rec 3455: Đã có TPHCM
    ("NHIỀU KHU VỰC Ở TPHCM NGẬP NẶNG SAU CƠN MƯA KÉO DÀI 5 TIẾNG 💦 Cụ thể , trận mưa bắt đầu từ 13h55 và kết thúc lúc 18h55 ngày 8 / 10 , cao điểm mưa là từ 14h30 đến 15h30 .", [
        ([4], [5, 6], 'NEG'),
    ]),

    # Rec 3456: Cắt cụt đuôi câu '1 , 36' -> REJECT
    ("Vũ lượng mưa lớn nhất đo được là 116mm , đỉnh triều cao nhất là 1 , 36", []),

    # Rec 3457: Đã có Sài Gòn
    ("Tyler chứng kiến đường phố Sài Gòn \" thất thủ \" vì nước ngập .", [
        ([5, 6], [8, 9], 'NEG'),
        ([5, 6], [12, 13], 'NEG'),
    ]),

    # Rec 3458: Cắt cụt đuôi câu 'tát nước ra k' -> REJECT
    ("Tại TP. Hồ Chí Minh , Anh không thể nào chạy được xe máy về nhà , nên phải chấp nhận đi bộ 4 - 5 km , vượt qua một số nơi nước ngập đến đầu gối , trong khi người dân hai bên đường cuống cuồng dùng xô tát nước ra k", []),

    # Rec 3459: Đã có TPHCM
    ("‼ ️ Nhiều tuyến đường ở TPHCM ngập nặng sau cơn mưa lúc trưa nay ‼ ️ 📷 : Tiền Phong , Dân Trí", [
        ([6], [7, 8], 'NEG'),
    ]),

    # Rec 3460: Đã có TPHCM
    ("NHIỀU TUYẾN ĐƯỜNG Ở TPHCM NGẬP SÂU SAU TRẬN “ MƯA VÀNG ” Cơn mưa lớn kéo dài khiến nhiều tuyến đường ở TPHCM ngập sâu .", [
        ([4], [5, 6], 'NEG'),
        ([23], [24, 25], 'NEG'),
    ]),

    # Rec 3461: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Người dân lội bì bõm , đẩy xe chết máy về nhà trong đêm muộn .", [
        ([1], [5, 6, 7], 'NEG'),
        ([1], [11, 12], 'NEG'),
    ]),

    # Rec 3462: Đã có TPHCM
    ("Mưa lớn , loạt tuyến đường ở TPHCM ngập như sông", [
        ([7], [8, 9, 10], 'NEG'),
    ]),

    # Rec 3463: Đã có TP. HCM, quận 12, quận Gò Vấp
    ("🛑 TP. HCM : HÀNG LOẠT TUYẾN ĐƯỜNG NGẬP ĐẾN YÊN XE SAU TRẬN MƯA HƠN 2 TIẾNG 🌊 Trọng tâm của trận mưa đổ xuống các khu vực vốn là “ rốn ngập ” của thành phố như quận 12 và quận Gò Vấp ( cũ ) .", [
        ([1, 2], [8, 9, 10, 11], 'NEG'),
        ([39, 40], [8, 9, 10, 11], 'NEG'),
        ([42, 43, 44], [8, 9, 10, 11], 'NEG'),
    ]),

    # Rec 3464: Cắt cụt đuôi câu 'ngập nặng' -> REJECT
    ("Tại TP. Hồ Chí Minh , Theo ghi nhận , các tuyến đường ngập nặng", []),

    # Rec 3465: Cắt cụt đầu câu 'HCM phải cõng con' -> REJECT
    ("HCM phải cõng con qua đường ngập sau trận mưa xối xả chiều 24 / 6 Mưa lớn chiều 24 / 6 làm ngập nhiều tuyến đường ở quận Gò Gấp , TP. HCM .", []),

    # Rec 3466: Văn cảnh cụt lửng -> REJECT
    ("Tại TP. Hồ Chí Minh , Nhiều người cõng con qua đường ngập .", []),

    # Rec 3467: Đã có TP. HCM
    ("Cơn mưa lớn kéo dài hơn một giờ đồng hồ khiến nhiều tuyến đường ở TP. HCM “ thành sông ” , người dân dắt bộ xe máy Sau hơn một giờ mưa lớn , nhiều tuyến đường ở TP. HCM đã “ biến thành sông ” .", [
        ([15, 16], [18, 19], 'NEG'),
        ([15, 16], [24, 25, 26, 27], 'NEG'),
        ([39, 40], [43, 44, 45], 'NEG'),
    ]),

    # Rec 3468: Cắt cụt đuôi câu 'để di' -> REJECT
    ("Tại TP. Hồ Chí Minh , Nước ngập cao ngừi dân phải chật vật dắt bộ xe máy để di", []),

    # Rec 3469: Đã có TP HCM
    ("Tối 5 - 12 , tại TP HCM , hàng trăm xe máy bị hư tắt máy phải dắt bộ khi đi qua các tuyến đường ngập nặng do triều cường dâng cao . 🙁 Theo Tuổi trẻ", [
        ([6, 7], [14, 15], 'NEG'),
        ([6, 7], [17, 18, 19], 'NEG'),
        ([6, 7], [26, 27], 'NEG'),
    ]),

    # Rec 3470: Đã có TP. HCM
    ("Từ khoảng 18 giờ chiều 6 . 8 , một cơn mưa cực to tại TP. HCM đã khiến hàng ngàn người phải lội giữa \" biển nước \" khi nhiều tuyến đường ngập nặng .", [
        ([15, 16], [23], 'NEG'),
        ([15, 16], [33, 34], 'NEG'),
    ]),

    # Rec 3471: Cắt cụt đuôi câu 'người dân ph' -> REJECT
    ("Tại TP. Hồ Chí Minh , Hàng trăm xe chết máy , người dân ph", []),

    # Rec 3472: Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Bình Dương mưa lớn ngay lúc này ❌ ghi nhận mưa lớn khiến đường ngập nhiều nơi , đúng lúc mọi người tan ca về qua đường ngập , xe ch / ết máy khiến bà con phải dắt bộ dưới mưa .", []),

    # Rec 3473: Đề xuất giải pháp dự án tương lai -> REJECT
    ("CHUYÊN GIA HÀ LAN ĐỀ XUẤT GIẢI PHÁP CHỐNG NGẬP ĐỘC ĐÁO CHO TPHCM - - - - - - - - - - - - - - - - - - - - - - - - - - - - Các chuyên gia Hà Lan đề xuất xây dựng hệ thống công trình chống ngập cho quận 2 và quận 9 .", []),

    # Rec 3474: Cắt cụt đuôi câu 'vừa là' -> REJECT
    ("Tại TP. Hồ Chí Minh , Đây là công trình đa mục tiêu , vừa chống ngập , vừa là", []),

    # Rec 3475: Đã có TP. HCM, Phú Định
    ("TP. HCM : Ngập triền miên cạnh công trình ‘ chống ngập ’ Phú Định !", [
        ([0, 1], [3, 4, 5], 'NEG'),
        ([13, 14], [3, 4, 5], 'NEG'),
    ]),

    # Rec 3476: Đã có TP. HCM
    ("Người dân bì bõm , tát nước cạnh công trình chống ngập 10 . 000 tỷ ở TP. HCM", [
        ([17, 18], [2, 3], 'NEG'),
        ([17, 18], [5, 6], 'NEG'),
    ]),

    # Rec 3477: Bài toán dự án tương lai -> REJECT
    ("TPO - Theo cơ quan chức năng TP. Thủ Đức ( TPHCM ) , để giải quyết bài toán thoát nước , chống ngập cho khu vực “ lòng chảo ” chợ Thủ Đức cần phải thực hiện thêm các dự án trên các tuyến đường khác quanh chợ .", []),

    # Rec 3478: Đã có Thủ Đức
    ("Thủ Đức đường thành sông nước chảy rất mạnh # HoàngVũOfficial", [
        ([0, 1], [2, 3, 4], 'NEG'),
        ([0, 1], [6, 7, 8], 'NEG'),
    ]),

    # Rec 3479: Đã có TP. HCM
    ("Chiều nay 2 . 7 , mưa lớn tiếp tục xuất hiện ở TP. HCM khiến cho nhiều tuyến đường ngập nặng , rác trôi lềnh bềnh .", [
        ([13, 14], [20, 21], 'NEG'),
    ]),

    # Rec 3480: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Người dân ở các khu dân cư cũng không thoát cảnh nước tràn vào nhà .", [
        ([1], [14, 15, 16, 17], 'NEG'),
    ]),

    # Rec 3481: Đã có Sài Gòn
    ("TRIỀU CƯỜNG LẬP KỶ LỤC MỚI 1M8 😰 Câu chuyện cũ lại lặp lại - đường thành sông , nhà thành ao , người dân Sài Gòn lại bì bõm trong nước .", [
        ([25, 26], [15, 16, 17], 'NEG'),
        ([25, 26], [28, 29], 'NEG'),
    ]),

    # Rec 3482: Đã có TPHCM
    ("TRIỀU CƯỜNG DÂNG CAO , NGƯỜI DÂN TPHCM CHẬT VẬT LỘI NƯỚC VỀ NHÀ _______________________ TPO - Chiều 18 / 10 , triều cường dâng cao , nhiều tuyến đường ở TPHCM ngập nặng , người dân phải vất vả di chuyển về nhà .", [
        ([7], [8, 9, 10, 11], 'NEG'),
        ([31], [32, 33], 'NEG'),
        ([31], [38, 39], 'NEG'),
    ]),

    # Rec 3483: Đã có Sài Gòn
    ("Mưa lớn kéo dài khiến hàng loạt tuyến đường Sài Gòn ngập nặng .", [
        ([9, 10], [11, 12], 'NEG'),
    ]),

    # Rec 3484: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Người dân oằn mình đón đêm Trung thu trong cảnh kẹt xe , tắc đường , mưa ngập .", [
        ([1], [13, 14], 'NEG'),
        ([1], [16, 17], 'NEG'),
        ([1], [19, 20], 'NEG'),
    ]),

    # Rec 3485: Đã có sông Sài Gòn
    ("Triều cường trên sông Sài Gòn vượt báo động III gây ngập nhiều tuyến đường", [
        ([3, 4, 5], [11, 12], 'NEG'),
    ]),

    # Rec 3486: Cắt cụt đuôi câu 'trong đ' -> REJECT
    ("THÀNH PHỐ HỒ CHÍ MINH CHI 350 TỶ ĐỒNG XÓA ‘ RỐN NGẬP ’ NHẤT Ở QUẬN GÒ VẤP - - - - - - - - - - - - - - - - - - - - - - - - - - - - TPHCM kỳ vọng dự án cải tạo hệ thống thoát nước hơn 350 tỷ đồng để giải quyết tình trạng ngập lụt cho nhiều tuyến đường quận Gò Vấp , trong đ", []),

    # Rec 3487: Bình Dương -> REJECT tỉnh ngoài
    ("🛑 Triều cường trên sông Sài Gòn vượt báo động III gây ngập nhiều tuyến đường ở Bình Dương tối nay 18 / 10 Ảnh : Minh Duy / Báo Bình Dương # kinhtedothivietnam # hochiminh # saigon", []),

    # Rec 3488: Đã có Sài Gòn, TP. HCM
    ("Vừa mưa ' giải nhiệt ' , nhiều đường Sài Gòn đã ngập sâu Chiều 30 - 4 , cơn mưa kéo dài khoảng một giờ đồng hồ làm giảm nắng nóng oi bức nhưng khiến nhiều tuyến đường trên địa bàn TP. HCM bị ngập nước .", [
        ([9, 10], [12, 13], 'NEG'),
        ([42, 43], [44, 45, 46], 'NEG'),
    ]),

    # Rec 3489: Meme OT -> REJECT
    ("Sài Gòn mưa ngập đường thế này , quả là một cơ hội tuyệt vời để OT 🥰", []),

    # Rec 3490: Tam Kỳ -> REJECT
    ("4 . 000 tỉ chống ngập cho Tam Kỳ , đừng như 10 . 000 tỉ ở TPHCM", []),

    # Rec 3491: Cắt cụt đuôi câu 'chống ngập tr' -> REJECT
    ("TPHCM QUYẾT HOÀN THÀNH DỰ ÁN CHỐNG NGẬP 10 . 000 TỶ TRONG NĂM NAY 🇻 🇳 🇻 🇳 🇻 🇳 Trong chỉ tiêu năm 2022 , Sở Xây dựng TP. HCM nêu : Cơ bản hoàn thành dự án Giải quyết ngập do triều có xét đến biến đổi khí hậu ( giai đoạn 1 ) để chống ngập tr", []),

    # Rec 3492: Đã có TPHCM
    ("TPHCM NHƯ MIỀN TÂY MÙA NƯỚC NỔI KHI TRIỀU CƯỜNG ĐẠT ĐỈNH LỊCH SỬ Cuộc sống người dân bị đảo lộn khi nhiều tuyến đường , nhà ven kênh ở TPHCM mênh mông biển nước khi triều cường đạt đỉnh lịch sử 1 , 8m vào chiều 18 / 10 .", [
        ([0], [1, 2, 3, 4, 5, 6], 'NEG'),
        ([30], [18, 19, 20], 'NEG'),
        ([30], [31, 32, 33, 34], 'NEG'),
    ]),

    # Rec 3493: Dự báo tương lai -> NEU (Pass 8)
    ("ĐỈNH TRIỀU CƯỜNG VƯỢT BÁO ĐỘNG 3 , TPHCM NGUY CƠ NGẬP SÂU NHIỀU NƠI ‼ Sáng 16 / 11 , Đài Khí tượng thủy văn khu vực Nam Bộ cho biết , khu vực Nam bộ đang bước vào giai đoạn triều cường rằm tháng 10 âm lịch đạt đỉnh .", [
        ([8], [9, 10, 11, 12], 'NEU'),
    ]),

    # Rec 3494: Đã có TPHCM
    ("Triều cường đạt đỉnh khiến nhiều khu vực trũng , thấp và ven sông ở TPHCM bị ngập úng .", [
        ([15], [16, 17, 18], 'NEG'),
    ]),

    # Rec 3495: Đã có đường Huỳnh Tấn Phát, quận 7
    ("Người dân tại khu dân cư trên đường Huỳnh Tấn Phát , quận 7 phải bì bõm lội nước về nhà .", [
        ([7, 8, 9, 10], [15, 16, 17, 18], 'NEG'),
        ([12, 13], [15, 16, 17, 18], 'NEG'),
    ]),

    # Rec 3496: Ngăn nước thành công -> REJECT
    ("Người dân sống tại đường Trần Xuân Soạn cho biết nhờ các bao cát này nên chiều hôm nay đã ngăn được lượng nước lớn tràn vào trong .", []),

    # Rec 3497: Lo ngại tương lai -> REJECT
    ("Tuy nhiên , người dân này cũng lo ngại đến ngày mai ( 20 . 11 ) triều cường dâng cao hơn lại tiếp tục tràn vào bên trong .", []),

    # Rec 3498: Không có ngập lụt -> REJECT
    ("Tại TP. Hồ Chí Minh , Nhiều ô tô , xe máy phải nhích từng chút qua khu vực này khiến giao thông ùn ứ .", []),

    # Rec 3499: Báo cáo thống kê -> REJECT
    ("Theo đó , từ đợt triều cường trong thời gian các ngày 20 - 25 . 10 ( từ 29 . 8 - 4 . 9 âm lịch ) , Phòng Hạ tầng kỹ thuật Sở Xây dựng TP. HCM cho biết trên địa bàn TP. HCM xảy ra các đợt ngập do triều cường tại nhiều khu vực .", []),

    # Rec 3500: Đoạn ngập trần trụi -> REJECT
    ("Tại TP. Hồ Chí Minh , Đoạn ngập kéo dài không đáng kể .", []),
]

def test_triplets():
    flaws = 0
    print(f'Kiểm tra {len(batch35_data)} records...')
    for idx, (text, triplets) in enumerate(batch35_data, 3401):
        tokens = text.split()
        for asp_idx, op_idx, pol in triplets:
            try:
                asp_tokens = [tokens[i] for i in asp_idx]
                op_tokens = [tokens[i] for i in op_idx]
                asp_str = ' '.join(asp_tokens)
                op_str = ' '.join(op_tokens)
                
                # Check punctuation at edges
                bad_puncts = [',', '.', ':', '!', '?', ';', '(', ')', '"', '“', '”', '…', '‘', '’', '\'']
                if asp_tokens[0] in bad_puncts or asp_tokens[-1] in bad_puncts:
                    print(f'LỖI DẤU CÂU ASPECT Rec {idx}: "{asp_str}"')
                    flaws += 1
                if op_tokens[0] in bad_puncts or op_tokens[-1] in bad_puncts:
                    print(f'LỖI DẤU CÂU OPINION Rec {idx}: "{op_str}"')
                    flaws += 1
                    
                # Check prepositions
                bad_preps = ['ở', 'tại', 'trên', 'trong', 'tới', 'vào', 'bởi', 'do', 'đến', 'thuộc']
                if asp_tokens[0].lower() in bad_preps:
                    print(f'LỖI GIỚI TỪ ĐẦU ASPECT Rec {idx}: "{asp_str}"')
                    flaws += 1
            except Exception as e:
                print(f'LỖI INDEX NGOÀI RANGE Rec {idx}: {e}')
                flaws += 1
    if flaws == 0:
        print('TẤT CẢ CÁC TRIPLETS CỦA BATCH 35 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!')
    else:
        print(f'TỔNG CỘNG PHÁT HIỆN {flaws} LỖI!')
    return flaws

if __name__ == '__main__':
    flaws = test_triplets()
    if flaws == 0:
        phase3_path = 'data/validate_label/thuan/phase3.txt'
        with open(phase3_path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        base_lines = lines[:3400]
        
        new_batch_lines = []
        for text, triplets in batch35_data:
            trip_strs = []
            for a, o, s in triplets:
                trip_strs.append(f'({a}, {o}, \'{s}\')')
            formatted_trips = '[' + ', '.join(trip_strs) + ']'
            new_batch_lines.append(f'{text}####{formatted_trips}')
            
        full_lines = base_lines + new_batch_lines
        with open(phase3_path, 'w', encoding='utf-8') as f:
            for l in full_lines:
                f.write(l + '\n')
        print(f'Successfully updated {len(full_lines)} lines to {phase3_path}!')
