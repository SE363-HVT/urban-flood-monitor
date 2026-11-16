# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn chuẩn hóa cho Phase 3 - Batch 30 (Records 2901 - 3000).
Tuân thủ 100% tài liệu BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md.
"""

batch30_data = [
    # Rec 2901: Thân câu 'cũng bị ngập sâu...' mồ côi cắt cụt đầu câu -> REJECT
    ("Tại TP. Hồ Chí Minh , cũng bị ngập sâu do trời mưa khiến nhiều phương tiện phải chật vật di chuyển .", []),

    # Rec 2902: Thân câu 'ngập như sông...', Fallback 'Tại TPHCM , '
    ("Tại TPHCM , ngập như sông , xe cộ qua đây bị chết máy phải dắt bộ .", [
        ([1], [3, 4, 5], 'NEG'),
        ([1], [12, 13], 'NEG'),
        ([1], [15, 16], 'NEG'),
    ]),

    # Rec 2903: Đã có PHƯỜNG TÂN MỸ
    ("HỒ CHÍ MINH : TRIỀU CƯỜNG DÂNG CAO GÂY NGẬP SÂU Ở PHƯỜNG TÂN MỸ", [
        ([12, 13, 14], [9, 10], 'NEG'),
    ]),

    # Rec 2904: Thân câu 'Hồ Chí Minh lên vượt báo động 3...', cắt tiền tố thừa
    ("Hồ Chí Minh lên vượt báo động 3 , các vùng trũng thấp đã bị ngập .", [
        ([0, 1, 2], [14], 'NEG'),
    ]),

    # Rec 2905: Đã có đường Nguyễn Lương Bằng, Phường Tân Mỹ
    ("Ghi nhận tại đường Nguyễn Lương Bằng , Phường Tân Mỹ , nước triều dâng gây ngập gần đến đầu gối người lớn khiến nhiều xe chết máy .", [
        ([3, 4, 5, 6], [16, 17, 18, 19, 20, 21, 22], 'NEG'),
        ([3, 4, 5, 6], [26, 27], 'NEG'),
        ([8, 9, 10], [16, 17, 18, 19, 20, 21, 22], 'NEG'),
    ]),

    # Rec 2906: Triều cường mồ côi -> Quy tắc 6 mở rộng in-place 'Triều cường ở TPHCM'
    ("Triều cường ở TPHCM cũng khiến hàng quán bị nước tràn vào , kinh doanh ế ẩm , ảnh hưởng đến đời sống người dân .", [
        ([0, 1, 2, 3], [9, 10, 11], 'NEG'),
        ([0, 1, 2, 3], [13, 14, 15, 16], 'NEG'),
    ]),

    # Rec 2907: Nhận định dự báo tương lai -> NEU (Pass 8)
    ("Tại TPHCM , Như vậy , mức độ ngập có thể còn sâu hơn hôm nay .", [
        ([1], [9, 10, 11, 12, 13], 'NEU'),
    ]),

    # Rec 2908: Đã có cửa ngõ TP. HCM
    ("❌ Hầm chui 75 tỷ ở cửa ngõ TP. HCM bị ngập sau cơn mưa 30 phút chiều qua", [
        ([8, 9], [10, 11], 'NEG'),
    ]),

    # Rec 2909: Giải trình kỹ thuật hỏng máy bơm -> REJECT
    ("Tại TP. Hồ Chí Minh , Lý giải nguyên nhân hầm bị ngập nước thời điểm đó , chủ đầu tư cho biết do máy máy bơm tự động của công trình bị hỏng , không thể bơm thoát nước nên hầm bị ngập .", []),

    # Rec 2910: Đã có TPHCM
    ("Chiều 19 / 6 , TPHCM xuất hiện mưa lớn kéo dài hàng giờ khiến nhiều tuyến đường bị ngập nặng .", [
        ([5], [19, 20], 'NEG'),
    ]),

    # Rec 2911: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhiều tuyến đường nước ngập lênh láng , hàng chục xe bị chết máy , người dân dẫn bộ về nhà trong đêm .", [
        ([1], [7, 8, 9], 'NEG'),
        ([1], [15, 16], 'NEG'),
        ([1], [20, 21], 'NEG'),
    ]),

    # Rec 2912: Đã có TPHCM
    ("TPHCM MƯA LỚN TRÁI MÙA , ĐƯỜNG NGẬP SÂU KHIẾN NGƯỜI NGÃ , XE BỊ TẮT MÁY", [
        ([0], [6, 7], 'NEG'),
        ([0], [14, 15], 'NEG'),
    ]),

    # Rec 2913: Đã có trung tâm TPHCM
    ("Chiều nay ( 27 / 12 ) , cơn mưa lớn trái mùa nặng hạt và kéo dài đổ xuống trung tâm TPHCM khiến nhiều tuyến đường ngập lênh láng , người dân di chuyển khó khăn .", [
        ([18, 19, 20], [25, 26, 27], 'NEG'),
        ([18, 19, 20], [31, 32, 33, 34], 'NEG'),
    ]),

    # Rec 2914: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Đến 18h , mưa giảm nhưng nước vẫn chưa rút , nhiều người bì bõm lội nước về nhà .", [
        ([1], [9, 10, 11, 12], 'NEG'),
        ([1], [16, 17, 18, 19], 'NEG'),
    ]),

    # Rec 2915: Đã có TP HCM
    ("Mưa lớn khiến hàng loạt tuyến đường TP HCM ngập sâu , nhiều xe chết máy , người dân lội nước về nhà , chiều 15 / 5 .", [
        ([6, 7], [8, 9], 'NEG'),
        ([6, 7], [13, 14], 'NEG'),
        ([6, 7], [18, 19], 'NEG'),
    ]),

    # Rec 2916: Bài viết đùa vui/máy lạnh xe -> REJECT
    ("Tại TP. Hồ Chí Minh , Máy lạnh phà , ngập không sợ chết máy", []),

    # Rec 2917: Đã có Hồ Chí Minh
    ("Hồ Chí Minh ngập sâu trong triều cường , người dân vất vả trở về nhà", [
        ([0, 1, 2], [3, 4], 'NEG'),
        ([0, 1, 2], [9, 10, 11, 12, 13], 'NEG'),
    ]),

    # Rec 2918: Thân câu có Hồ Chí Minh, cắt tiền tố thừa
    ("Hồ Chí Minh đã bất ngờ ngập sâu , gây khó khăn trong di chuyển của người dân .", [
        ([0, 1, 2], [5, 6], 'NEG'),
        ([0, 1, 2], [9, 10, 11, 12], 'NEG'),
    ]),

    # Rec 2919: Đã có TP. HCM
    ("Cơn mưa lớn tối 27 - 5 khiến một số tuyến đường ở TP. HCM bị ngập , người dân bì bõm lội nước về nhà .", [
        ([13, 14], [15, 16], 'NEG'),
        ([13, 14], [20, 21, 22, 23], 'NEG'),
    ]),

    # Rec 2920: Đã có đường Nguyễn Văn Quá, quận 12
    ("Theo ghi nhận , trên đường Nguyễn Văn Quá quận 12 , mưa gây ngập hơn nửa bánh xe máy .", [
        ([5, 6, 7, 8], [14, 15, 16, 17, 18, 19], 'NEG'),
        ([9, 10], [14, 15, 16, 17, 18, 19], 'NEG'),
    ]),

    # Rec 2921: Tản văn ví von không có sự kiện ngập cụ thể -> REJECT
    ("Tại TP. Hồ Chí Minh , Như thông lệ , cư dân của thành phố sôi động nhất cả nước phải hứng chịu cảnh bì bõm lội qua những vũng nước giữa đô thị giờ tan tầm .", []),

    # Rec 2922: Đã có TPHCM
    ("NGƯỜI DÂN TPHCM XẮN QUẦN , CO CHÂN VƯỢT ĐƯỜNG NGẬP LÊNH LÁNG VÀO GIỜ CAO ĐIỂM 🤧", [
        ([2], [9, 10, 11], 'NEG'),
    ]),

    # Rec 2923: Đã có TPHCM
    ("Cơn mưa lớn kéo dài từ đêm qua đến rạng sáng nay ( 5 / 11 ) trút xuống hầu hết các phường , xã trên địa bàn TPHCM , khiến nhiều tuyến đường bị ngập nặng .", [
        ([27], [34, 35], 'NEG'),
    ]),

    # Rec 2924: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Đến 7h , dù trời đã tạnh , nhiều tuyến phố vẫn ngập cục bộ , gây khó khăn cho giao thông và sinh hoạt của người dân .", [
        ([1], [13, 14, 15], 'NEG'),
    ]),

    # Rec 2925: Trích dẫn nhân chứng, Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Khi đi qua đoạn đường này , nước vẫn còn ngập rất sâu , nhiều xe mô tô bị ch * t máy \" , anh Minh nói .", [
        ([1], [12, 13, 14], 'NEG'),
        ([1], [20, 21, 22], 'NEG'),
    ]),

    # Rec 2926: Đã có chợ Thủ Đức, TP Thủ Đức, TP. HCM
    ("Gần đây khi những cơn mưa lớn xuất hiện trở lại , các tuyến đường xung quanh khu vực chợ Thủ Đức ( TP Thủ Đức , TP. HCM ) tái diễn cảnh nước chảy cuồn cuộn , người dân bì bõm giữa dòng nước ngập .", [
        ([19, 20, 21], [33, 34, 35, 36], 'NEG'),
        ([19, 20, 21], [44, 45], 'NEG'),
        ([23, 24, 25], [44, 45], 'NEG'),
        ([27, 28], [44, 45], 'NEG'),
    ]),

    # Rec 2927: Đã có Đặng Thị Rành, Hồ Văn Tư, Kha Vạn Cân
    ("Tình trạng ngập xảy ra nặng nhất tại các tuyến đường như Đặng Thị Rành , Hồ Văn Tư , Kha Vạn Cân .", [
        ([12, 13, 14], [2, 3, 4, 5, 6], 'NEG'),
        ([16, 17, 18], [2, 3, 4, 5, 6], 'NEG'),
        ([20, 21, 22], [2, 3, 4, 5, 6], 'NEG'),
    ]),

    # Rec 2928: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Do nằm ngay vùng trũng của khu vực nên nước từ các khu vực cao hơn chảy về ồ ạt gây ngập nặng .", [
        ([1], [24, 25], 'NEG'),
    ]),

    # Rec 2929: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Qua khu vực này , nếu người đi xe máy cố gắng vượt qua thì đến 7 / 10 xe bị chết máy phải dắt bộ .", [
        ([1], [24, 25], 'NEG'),
        ([1], [27, 28], 'NEG'),
    ]),

    # Rec 2930: Miêu tả thi công đào xới không có sự kiện ngập -> REJECT
    ("Một số điểm đang thi công , mặt đường bị đào xới tạo ra nhiều chướng ngại vật bị nước che khuất , càng khiến việc di chuyển khó khăn hơn , dễ sa xuống phần đường bị trũng nằm ẩn dưới dòng nước .", []),

    # Rec 2931: Đã có đường Tô Ngọc Vân
    ("Tương tự tại đường Tô Ngọc Vân đoạn giao với đường sắt Bắc - Nam , nước cũng ngập không thấy phần mặt đường .", [
        ([4, 5, 6, 7], [17, 18, 19, 20, 21, 22], 'NEG'),
    ]),

    # Rec 2932: Miêu tả chờ đợi nước rút -> REJECT
    ("Tại TP. Hồ Chí Minh , Có thời điểm hàng trăm xe phải dừng lại đợi nước rút bớt mới đi qua được .", []),

    # Rec 2933: Tuyến đường sắt nước tràn qua đường ray
    ("Tại TPHCM , Tuyến đường sắt thì chịu cảnh nước chảy tràn qua đường ray , đất đá nền bị cuốn trôi , nhân viên đường sắt phải túc trực để kiểm tra , đợi nước rút để kịp thời phát hiện các sự cố .", [
        ([1], [9, 10, 11, 12, 13, 14], 'NEG'),
    ]),

    # Rec 2934: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Mưa gây ngập dẫn đến hệ lụy kẹt xe kéo dài do người dân đứng đợi nước rút .", [
        ([1], [5], 'NEG'),
        ([1], [8, 9, 10, 11], 'NEG'),
    ]),

    # Rec 2935: Xã luận tìm cách chống ngập -> REJECT
    ("Tại TP. Hồ Chí Minh , Mỗi khi có cơn mưa lớn xảy ra cả khu vực này náo loạn tìm cách chống ngập , chống kẹt .", []),

    # Rec 2936: Đã có chợ Thủ Đức
    ("May đường cấm xe lớn chứ cho vô nữa thì sóng nước đánh tràn vào nhà ướt hết đồ đạc , hàng hóa \" , ông Huấn , sống tại đường dọc bên chợ Thủ Đức , bày tỏ .", [
        ([33, 34, 35], [10, 11, 12, 13, 14, 15], 'NEG'),
        ([33, 34, 35], [16, 17, 18, 19], 'NEG'),
    ]),

    # Rec 2937: Đã có TPHCM
    ("NƯỚC NGẬP SÂU , NGƯỜI DÂN TPHCM VÁC VALI LỘI BÌ BÕM ĐI NGỦ NHỜ 🤧", [
        ([6], [1, 2], 'NEG'),
        ([6], [9, 10, 11], 'NEG'),
    ]),

    # Rec 2938: Đã có đường Bình Quới, quận Bình Thạnh
    ("Tối 24 / 10 , triều cường trên sông Sài Gòn dâng cao , vượt mức báo động , nước tràn qua bờ kè đổ vào nhiều khu dân cư , làm ngập sâu đường Bình Quới ( quận Bình Thạnh ) .", [
        ([34, 35, 36], [32, 33], 'NEG'),
        ([38, 39, 40], [32, 33], 'NEG'),
    ]),

    # Rec 2939: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhiều khu vực ven sông ngập sâu tới cả mét .", [
        ([1], [8, 9, 10, 11, 12], 'NEG'),
    ]),

    # Rec 2940: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Em Nguyễn Trọng Thắng cùng người thân lội nước , vác vali và đồ đạc sang nhà người quen để ngủ nhờ .", [
        ([1], [10, 11], 'NEG'),
    ]),

    # Rec 2941: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Tối về chúng tôi lại phải bì bõm lội nước , cực lắm ” .", [
        ([1], [9, 10, 11, 12], 'NEG'),
        ([1], [14, 15], 'NEG'),
    ]),

    # Rec 2942: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Cả tuyến đường trục chính bị ngập kéo dài hơn 5km , nhiều xe ch * t máy nằm la liệt .", [
        ([1], [8, 9, 10, 11, 12, 13], 'NEG'),
        ([1], [17, 18, 19, 20, 21, 22], 'NEG'),
    ]),

    # Rec 2943: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Người dân phải dắt bộ , nhiều người thốt lên vì mỏi tay sau quãng đường dài giữa dòng nước .", [
        ([1], [5, 6], 'NEG'),
    ]),

    # Rec 2944: Đã có TP. HCM
    ("✅ Chiều 22 / 10 , triều cường trên sông Sài Gòn bắt đầu dâng cao khiến một số khu vực thấp trũng trên địa bàn TP. HCM ngập .", [
        ([26, 27], [28], 'NEG'),
    ]),

    # Rec 2945: Câu bị cắt cụt đầu lỡ dở 'HCM ) bị ngập sâu...' -> REJECT
    ("Tại TP. Hồ Chí Minh , HCM ) bị ngập sâu , khiến nhiều người tham gia giao thông gặp nhiều khó khăn , một số người té ngã sõng soài xuống nước , một số người phải phải dắt bộ vì xe chết máy giữa đường .", []),

    # Rec 2946: Đã có SÀI GÒN
    ("DÂN SÀI GÒN NỐI ĐUÔI NHAU DẮT XE ĐI NHƯ KIẾN VÌ TRIỀU CƯỜNG 🥴", [
        ([1, 2], [5, 6], 'NEG'),
    ]),

    # Rec 2947: Đã có đường Lương Định Của, TP Thủ Đức, Trần Xuân Soạn, Nguyễn Thị Thập, quận 7, TP. HCM
    ("Tối 7 - 11 , nhiều người dân TP. HCM vất vả khi đi qua các tuyến đường bị ngập nặng do triều cường dâng cao , như đường Lương Định Của ( TP Thủ Đức ) , Trần Xuân Soạn , Nguyễn Thị Thập ( quận 7 ) .", [
        ([28, 29, 30, 31], [19, 20], 'NEG'),
        ([33, 34, 35], [19, 20], 'NEG'),
        ([38, 39, 40], [19, 20], 'NEG'),
        ([42, 43, 44], [19, 20], 'NEG'),
        ([46, 47], [19, 20], 'NEG'),
    ]),

    # Rec 2948: Đã có đường Lương Định Của, TP Thủ Đức
    ("Có mặt tại đường Lương Định Của ( TP Thủ Đức ) lúc 18h30 , phóng viên ghi nhận tuyến đường này bị ngập một đoạn dài khoảng 200m , trong đó có những đoạn ngập nặng khoảng 0 , 5m khiến hàng loạt phương tiện chớt máy phải dẫn bộ .", [
        ([3, 4, 5, 6], [22, 23], 'NEG'),
        ([3, 4, 5, 6], [35, 36], 'NEG'),
        ([3, 4, 5, 6], [46, 47], 'NEG'),
        ([3, 4, 5, 6], [49, 50], 'NEG'),
        ([8, 9, 10], [22, 23], 'NEG'),
    ]),

    # Rec 2949: Đã có đường Trần Xuân Soạn, quận 7
    ("Còn tại đường Trần Xuân Soạn ( quận 7 ) trong những ngày này , các hàng quán , các nhà ven kênh Tẻ luôn trong tình trạng tất bật chống ngập bằng cách chắn những bao cát , kê đồ đạc lên cao . . .", [
        ([2, 3, 4, 5], [28, 29, 30, 31], 'NEG'),
        ([7, 8], [28, 29, 30, 31], 'NEG'),
    ]),

    # Rec 2950: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Việc buôn bán mùa này cũng ế ẩm do khách ngại dừng xe mua hàng khi mặt đường mênh mông nước .", [
        ([1], [8, 9], 'NEG'),
        ([1], [20, 21, 22, 23], 'NEG'),
    ]),

    # Rec 2951: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Chứ ngập thế này không ai dám dừng lại mua \" , chị Mai chia sẻ .", [
        ([1], [4], 'NEG'),
    ]),

    # Rec 2952: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Các con hẻm trũng , nước tràn vào nhà , người dân phải dùng tôn , bao cát để chặn dòng nước .", [
        ([1], [8, 9, 10, 11], 'NEG'),
    ]),

    # Rec 2953: Triều cường mồ côi -> Quy tắc 6 mở rộng in-place 'triều cường ở TPHCM'
    ("Cũng chính vì triều cường ở TPHCM gây ngập sâu mà nhiều tuyến xe buýt đi qua khu vực bị ảnh hưởng nghiêm trọng .", [
        ([3, 4, 5, 6], [7, 8, 9], 'NEG'),
    ]),

    # Rec 2954: Xã luận triết lý ví von -> REJECT
    ("Tại TP. Hồ Chí Minh , Thế nhưng dường như “ càng chống thì thành phố càng ngập ” .", []),

    # Rec 2955: Đã có Thủ Đức
    ("Thủ Đức sau 30 phút mưa lớn , nước đã ngập lút hơn nửa bánh xe !", [
        ([0, 1], [9, 10, 11, 12, 13, 14], 'NEG'),
    ]),

    # Rec 2956: Cắt cụt lỡ dở 'Ở TP.' -> REJECT
    ("Tại TP. Hồ Chí Minh , HÀNG LOẠT XE BỊ CHẾT MÁY SAU MƯA LỚN Ở TP.", []),

    # Rec 2957: Đã có TP HCM, cắt tiền tố thừa
    ("Chiều 7 / 5 , cơn mưa lớn trên diện rộng ở nhiều quận tại TP HCM khiến nhiều tuyến đường ngập sâu .", [
        ([15, 16], [21, 22], 'NEG'),
    ]),

    # Rec 2958: Đã có đường Nguyễn Hữu Cảnh, quận Bình Thạnh
    ("Tại đường Nguyễn Hữu Cảnh ( quận Bình Thạnh ) , nước ngập nửa bánh xe khiến hàng loạt xe máy , ôtô chết máy .", [
        ([1, 2, 3, 4], [12, 13, 14, 15], 'NEG'),
        ([1, 2, 3, 4], [23, 24], 'NEG'),
        ([6, 7, 8], [12, 13, 14, 15], 'NEG'),
    ]),

    # Rec 2959: Đã có cầu Sài Gòn
    ("Trong đó , ngập nặng nhất là đoạn dưới chân cầu Sài Gòn , gần 2 km đoạn đường lênh láng nước .", [
        ([9, 10, 11], [3, 4, 5], 'NEG'),
        ([9, 10, 11], [18, 19, 20], 'NEG'),
    ]),

    # Rec 2960: Cảnh sát PCCC cứu nạn (People Role / Hoạt động chức năng) -> REJECT
    ("Ngay sau khi nhận tin , Phòng Cảnh sát PCCC & CNCH – Công an TP. HCM đã huy động hàng chục cán bộ , chiến sĩ chia nhiều hướng vào vùng ngập sâu gần 2m để cứu người trong đêm tối .", []),

    # Rec 2961: Đã có hầm chui trước Bến xe Miền Đông mới, phường Long Bình, TPHCM
    ("Chiều 28 / 10 , hầm chui trước Bến xe Miền Đông mới ( phường Long Bình , TPHCM ) , tổng mức đầu tư hơn 75 tỷ đồng , tiếp tục ngập sau mưa lớn .", [
        ([5, 6, 7, 8, 9, 10, 11, 12], [30, 31, 32], 'NEG'),
        ([14, 15, 16], [30, 31, 32], 'NEG'),
        ([18], [30, 31, 32], 'NEG'),
    ]),

    # Rec 2962: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Dù chủ đầu tư đã lắp camera giám sát và bố trí lực lượng túc trực bơm thoát nước , tình trạng ngập vẫn tái diễn , gây gián đoạn giao thông và bức xúc cho người dân .", [
        ([1], [20, 21, 22, 23], 'NEG'),
    ]),

    # Rec 2963: Mỉa mai châm biếm công trình 75 tỷ -> REJECT
    ("Nực cười ở chỗ , cả một công trình hầm chui 75 tỷ , nhưng đầu tư cả camera giám sát , lực lượng túc trực và máy bơm chỉ để . . . chống ngập .", []),

    # Rec 2964: Mỉa mai rút kinh nghiệm sâu sắc -> REJECT
    ("Tại TP. Hồ Chí Minh , Chỉ có điều , nước vẫn ngập rất sau và có lẽ camera được dùng để quay lại cảnh ngập nhằm “ rút kinh nghiệm sâu sắc ” cho những mùa mưa sau .", []),

    # Rec 2965: Xã luận trách ông trời -> REJECT
    ("Tại TP. Hồ Chí Minh , Thế nên dân có bức xúc , khó chịu và khổ sở thế nào mỗi lần mưa xuống , thì chỉ nên trách ông trời vì sao mưa lắm vậy thôi ; chứ nếu không mưa thì lãnh đạo lại được dịp tự tin vỗ ngực \" công trình đang hoạt động dưới trời nắng rất tốt \" đấy thôi .", []),

    # Rec 2966: Đã có TPHCM
    ("TRIỀU CƯỜNG BẤT NGỜ , NHIỀU TUYẾN ĐƯỜNG , NHÀ DÂN Ở TPHCM NGẬP SÂU ‼ ️", [
        ([10], [11, 12], 'NEG'),
    ]),

    # Rec 2967: Thủ Dầu Một (tỉnh Bình Dương) -> REJECT tỉnh ngoài
    ("Tối nay ( 23 / 10 ) , nhiều tuyến đường gần sông Sài Gòn , thuộc phường Thủ Dầu Một ( TPHCM ) , bất ngờ bị ngập sâu , khiến phương tiện và người dân không thể lưu thông .", []),

    # Rec 2968: Đã có Thành phố Thủ Đức, TPHCM, Tô Ngọc Vân, Võ Văn Ngân, Đăng Văn Bi
    ("Từ đầu tháng 5 , nhiều cơn mưa lớn xuất hiện liên tiếp và gây ngập lụt nhiều tuyến đường chính ở Thành phố Thủ Đức ( TPHCM ) như Tô Ngọc Vân , Võ Văn Ngân , Đăng Văn Bi … Nhiều người dân không hiểu vì sao Thành phố Thủ Đức – một trong những nơi có địa hình thuộc cao nhất thành phố lại thành “ rốn ngập ” .", [
        ([22, 23, 24, 25], [14, 15, 16], 'NEG'),
        ([27], [14, 15, 16], 'NEG'),
        ([30, 31, 32], [14, 15, 16], 'NEG'),
        ([34, 35, 36], [14, 15, 16], 'NEG'),
        ([38, 39, 40], [14, 15, 16], 'NEG'),
    ]),

    # Rec 2969: Dự án tương lai / giải pháp của lãnh đạo -> REJECT
    ("Theo ông Vũ Văn Điệp , để giải bài toán thoát nước , chống ngập ở khu vực này , việc nên làm trước hết là đẩy nhanh tiến độ thực hiện các dự án nâng cấp , cải tạo hệ thống thoát nước để giảm tình trạng ngập .", []),

    # Rec 2970: Câu mồ côi cắt cụt đầu câu 'cũng sẽ góp phần...' -> REJECT
    ("Tại TP. Hồ Chí Minh , cũng sẽ góp phần giải quyết ngập cho khu vực này .", []),

    # Rec 2971: Đã có TP. HCM
    ("🌧 TP. HCM TỐI QUA : MƯA LỚN GÂY NGẬP , GIAO THÔNG HỖN LOẠN 🚧", [
        ([1, 2], [7, 8], 'NEG'),
    ]),

    # Rec 2972: Đã có TP. HCM
    ("Tối 8 / 10 , một cơn mưa lớn kéo dài hơn 2 giờ đã khiến nhiều tuyến đường trung tâm TP. HCM ngập sâu , gây ùn tắc nghiêm trọng .", [
        ([20, 21], [22, 23], 'NEG'),
    ]),

    # Rec 2973: Đã có các tuyến đường
    ("🌊 Nước ngập sâu tại các tuyến Nguyễn Thị Minh Khai , 3 Tháng 2 , Lý Thái Tổ , Nguyễn Hữu Cảnh . . .", [
        ([7, 8, 9, 10], [1, 2, 3], 'NEG'),
        ([12, 13, 14], [1, 2, 3], 'NEG'),
        ([16, 17, 18], [1, 2, 3], 'NEG'),
        ([20, 21, 22], [1, 2, 3], 'NEG'),
    ]),

    # Rec 2974: Đã có Điện Biên Phủ, TP Thủ Đức
    ("👉 Trên trục Điện Biên Phủ hướng từ Q. 1 về TP Thủ Đức , hàng nghìn phương tiện “ chôn chân ” giữa mưa lớn và nước ngập .", [
        ([3, 4, 5], [17, 18], 'NEG'),
        ([3, 4, 5], [23, 24], 'NEG'),
        ([10, 11, 12], [23, 24], 'NEG'),
    ]),

    # Rec 2975: Lời khuyên theo dõi thời tiết -> REJECT
    ("Tại TP. Hồ Chí Minh , Người dân cần theo dõi thời tiết để chủ động lịch trình và đảm bảo an toàn !", []),

    # Rec 2976: Bị cắt cụt đuôi câu 'Ở TP.' -> REJECT
    ("TP. HCM TỐI NAY : ÙN TẮC GIAO THÔNG DO MƯA NGẬP Ở TP.", []),

    # Rec 2977: Đã có TP. HCM
    ("Cơn mưa lớn kéo dài hơn hai giờ tối 8 / 10 khiến nhiều tuyến đường trung tâm TP. HCM ngập sâu , sóng đánh ngã người đi xe máy , giao thông hỗn loạn và ùn tắc kéo dài .", [
        ([17, 18], [19, 20], 'NEG'),
    ]),

    # Rec 2978: Đã có các tuyến đường
    ("Các tuyến Nguyễn Thị Minh Khai , Lý Thái Tổ , 3 Tháng 2 , Nguyễn Hữu Cảnh … bị ngập nặng , dòng xe di chuyển chậm , nhích từng chút một .", [
        ([2, 3, 4, 5], [19, 20, 21], 'NEG'),
        ([7, 8, 9], [19, 20, 21], 'NEG'),
        ([11, 12, 13], [19, 20, 21], 'NEG'),
        ([15, 16, 17], [19, 20, 21], 'NEG'),
    ]),

    # Rec 2979: Đã có Điện Biên Phủ, TP Thủ Đức
    ("Riêng trên trục Điện Biên Phủ hướng từ quận 1 về TP Thủ Đức , hàng nghìn phương tiện xếp hàng dài , di chuyển khó khăn giữa mưa lớn và nước ngập .", [
        ([3, 4, 5], [20, 21, 22, 23], 'NEG'),
        ([3, 4, 5], [27, 28], 'NEG'),
        ([10, 11, 12], [27, 28], 'NEG'),
    ]),

    # Rec 2980: Đã có TP. HCM, Nguyễn Hữu Cảnh
    ("Mưa lớn từ chiều tối 6 - 8 khiến nhiều tuyến đường trung tâm TP. HCM ngập nặng , trong đó \" rốn ngập \" Nguyễn Hữu Cảnh tê liệt xe cộ qua lại trong luồng nước nửa mét .", [
        ([14, 15], [16, 17], 'NEG'),
        ([25, 26, 27], [28, 29], 'NEG'),
    ]),

    # Rec 2981: Đàm phán hợp đồng thuê máy bơm -> REJECT
    ("Cần đàm phán , trường hợp dừng thuê máy bơm chống ngập đường Nguyễn Hữu Cảnh trước thời hạn , TP. HCM sẽ phải bồi thường thiệt hại hợp đồng cho Công ty cổ phần tập đoàn công nghiệp Quang Trung .", []),

    # Rec 2982: Đã có TP. HCM
    ("Trưa nay 3 . 8 , mưa đổ xuống nhiều khu vực ở TP. HCM khiến một số tuyến đường mênh mông nước , người dân vất vả di chuyển qua đoạn ngập .", [
        ([13, 14], [20, 21, 22], 'NEG'),
        ([13, 14], [26, 27, 28, 29], 'NEG'),
    ]),

    # Rec 2983: Đã có TPHCM
    ("TPHCM thường xuyên ngập sâu do mưa và triều cường , người dân mong sớm hoàn thiện các dự án chống ngập để thoát cảnh sống chung với nước .", [
        ([0], [1, 2, 3, 4], 'NEG'),
    ]),

    # Rec 2984: Đã có TP. HCM, Dự báo giờ đi làm -> NEU (Pass 8)
    ("Thông tin quan trọng : Hôm nay bắt đầu vào đỉnh triều cường , TP. HCM nhiều nơi lại ngập nặng vào giờ đi làm và tan ca .", [
        ([11, 12], [16, 17], 'NEU'),
    ]),

    # Rec 2985: Đã có sông Sài Gòn, Thanh Đa, phường Bình Quới
    ("Nước từ sông Sài Gòn tràn qua bờ kè , chảy vào các con hẻm khu vực Thanh Đa , phường Bình Quới , hàng chục hộ dân ngập sâu , đồ đạc hư hỏng , tối 24 / 10 .", [
        ([2, 3, 4], [5, 6, 7, 8], 'NEG'),
        ([17, 18], [28, 29], 'NEG'),
        ([17, 18], [31, 32, 33, 34], 'NEG'),
        ([20, 21, 22], [28, 29], 'NEG'),
    ]),

    # Rec 2986: Cắt cụt lỡ dở 'khiến n' -> REJECT
    ("Tại TP. Hồ Chí Minh , Nước ngập sâu , tràn vào nhà khiến n", []),

    # Rec 2987: Đã có Quận 7, TP. HCM
    ("🛑 Triều cường biến đường thành sông , dân Quận 7 ( cũ ) sáng nay phải khổ sở đi làm , có người chở con đi học ngã sõng soài 🥲 Thời tiết TP. HCM hôm nay dự báo triều cường tiếp tục vượt báo động 3 vào giờ tan tầm chiều .", [
        ([8, 9], [3, 4, 5, 6], 'NEG'),
        ([8, 9], [14, 15], 'NEG'),
        ([30, 31], [37, 38, 39, 40], 'NEU'),
    ]),

    # Rec 2988: Bình Dương (Thủ Dầu Một) + cắt cụt '( n' -> REJECT
    ("Hiện mực nước sông Sài Gòn đang dâng cao , gây ngập 1 số nơi như Chánh Mỹ , chợ Thủ Dầu Một , bờ kè Bưng Cải , An Sơn , Quốc Lộ 13 ( n", []),

    # Rec 2989: Dự báo triều cường sông Sài Gòn -> NEU (Pass 8)
    ("Theo dự báo , mưa kết hợp với triều cường có thể gây ngập úng tại các vùng hạ du ven sông Sài Gòn .", [
        ([18, 19, 20], [9, 10, 11, 12, 13], 'NEU'),
    ]),

    # Rec 2990: Meme / bí kíp cắt cụt 'Luôn c' -> REJECT
    ("Tại TP. Hồ Chí Minh , Những cơn mưa bất chợt , ào đến rồi đi để lại những \" con sông \" ngập bất thình lình : ) : ) ⛈ ️ Để đối phó với những cơn mưa hãy : 🌩 ️ Luôn c", []),

    # Rec 2991: Đã có TP. HCM, Gò Vấp, Tân Bình
    ("⛈ ️ TP. HCM : Mưa lớn kéo dài từ rạng sáng , đường ngập sâu đến nửa bánh xe 🥹 Trận mưa to kéo dài đến giờ cao điểm khiến giao thông sáng nay ( 21 / 8 ) bị tắc nghẽn ở các tuyến đường phường Gò Vấp , 12 , Tân Bình . . .", [
        ([2, 3], [13, 14, 15, 16, 17, 18], 'NEG'),
        ([36, 37], [13, 14, 15, 16, 17, 18], 'NEG'),
        ([41, 42], [13, 14, 15, 16, 17, 18], 'NEG'),
    ]),

    # Rec 2992: Cắt cụt mất chủ ngữ 'đã chìm trong...' -> REJECT
    ("Tại TP. Hồ Chí Minh , đã chìm trong biển nước .", []),

    # Rec 2993: Mẹo vặt sinh tồn -> REJECT
    ("10 BÍ KÍP SINH TỒN MÙA MƯA Ở SÀI GÒN Sài Gòn hổm rày bắt đầu có mấy cơn mưa lớn , báo hiệu mùa mưa ngập đường sắp về , nhớ kỹ mấy điều sau để yên ổn qua mùa mưa ở Sài Gòn nha .", []),

    # Rec 2994: Đã có Sài Gòn
    ("Mưa lớn khiến hàng loạt tuyến đường Sài Gòn ngập sâu , nhiều xe chết máy , người dân lội nước về nhà , chiều 15 / 5 .", [
        ([7, 8], [9, 10], 'NEG'),
        ([7, 8], [14, 15], 'NEG'),
        ([7, 8], [19, 20], 'NEG'),
    ]),

    # Rec 2995: Đã có TP. HCM
    ("🛑 ĐƯỜNG TP. HCM NGẬP SÂU SAU TRẬN MƯA LỚN ✅ Cơn mưa lớn tối 10 / 8 khiến nhiều tuyến đường ở TP. HCM ngập sâu , hàng loạt xe chết máy , giao thông ùn tắc , người dân di chuyển khó khăn .", [
        ([2, 3], [4, 5], 'NEG'),
        ([18, 19], [20, 21], 'NEG'),
        ([18, 19], [25, 26], 'NEG'),
        ([18, 19], [30, 31], 'NEG'),
        ([18, 19], [36, 37, 38, 39], 'NEG'),
    ]),

    # Rec 2996: Đã có đường Nguyễn Duy Trinh, TP. HCM
    ("HCM : NGẬP NƯỚC HƠN 1M SUỐT 2 TIẾNG , Ô TÔ CHẾT MÁY LA LIỆT … Mưa lớn chiều 10 . 8 khiến đường Nguyễn Duy Trinh ( TP. HCM ) bị ngập nước hơn 1 m suốt 2 tiếng , nhiều ô tô chết máy , người dân phải lội nước về nhà .", [
        ([24, 25, 26, 27], [32, 33, 34, 35, 36, 37, 38, 39, 40], 'NEG'),
        ([24, 25, 26, 27], [45, 46], 'NEG'),
        ([24, 25, 26, 27], [51, 52], 'NEG'),
    ]),

    # Rec 2997: Đã có TPHCM
    ("MƯA NGẬP LÚT BÁNH XE , NGƯỜI DÂN TPHCM VẬT LỘN GIỮA DÒNG NƯỚC Sau chuỗi ngày nắng nóng oi bức , TPHCM xuất hiện mưa lớn làm loạt tuyến đường ngập sâu khiến xe chết máy hàng loạt , giao thông rối loạn .", [
        ([8], [1, 2, 3, 4], 'NEG'),
        ([20], [27, 28], 'NEG'),
        ([20], [31, 32], 'NEG'),
    ]),

    # Rec 2998: Đã có TP. HCM, Sài Gòn
    ("TP. HCM KẸT CỨNG GIỮA MƯA NGẬP TỐI 8 / 10 : “ ĐI 2KM MẤT GẦN 2 TIẾNG ! ” Tối 8 / 10 , Sài Gòn như “ vỡ trận ” vì mưa lớn kéo dài suốt hơn hai giờ .", [
        ([0, 1], [2, 3], 'NEG'),
        ([23, 24], [26, 27], 'NEG'),
    ]),

    # Rec 2999: Cắt cụt đuôi 'một hô' -> REJECT
    ("Tại TP. Hồ Chí Minh , Nước ngập dâng lên nhanh , xe chết máy xếp hàng , hàng nghìn người mắc kẹt giữa biển xe bất động — một hô", []),

    # Rec 3000: Đã có TPHCM, Bình Tân, Tân Phú, Bình Chánh
    ("‼ ️ TPHCM : Mưa như trút gây ngập nặng , xe ch : ết máy hàng loạt ⛈ 🫨 Đầu giờ chiều 20 / 6 , mưa lớn trút xuống các quận , huyện phía tây TPHCM như Bình Tân , Tân Phú , Bình Chánh khiến nhiều tuyến đường bị ngập cục bộ .", [
        ([2], [7, 8, 9], 'NEG'),
        ([37], [51, 52, 53, 54], 'NEG'),
        ([39, 40], [51, 52, 53, 54], 'NEG'),
        ([42, 43], [51, 52, 53, 54], 'NEG'),
        ([45, 46], [51, 52, 53, 54], 'NEG'),
    ]),
]

def test_triplets():
    flaws = 0
    print(f'Kiểm tra {len(batch30_data)} records...')
    for idx, (text, triplets) in enumerate(batch30_data, 2901):
        tokens = text.split()
        for asp_idx, op_idx, pol in triplets:
            try:
                asp_tokens = [tokens[i] for i in asp_idx]
                op_tokens = [tokens[i] for i in op_idx]
                asp_str = ' '.join(asp_tokens)
                op_str = ' '.join(op_tokens)
                
                # Check punctuation at edges
                bad_puncts = [',', '.', ':', '!', '?', ';', '(', ')', '"', '“', '”', '…']
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
        print('TẤT CẢ CÁC TRIPLETS CỦA BATCH 30 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!')
    else:
        print(f'TỔNG CỘNG PHÁT HIỆN {flaws} LỖI!')
    return flaws

if __name__ == '__main__':
    flaws = test_triplets()
    if flaws == 0:
        # Đọc phase3.txt hiện có
        phase3_path = 'data/validate_label/thuan/phase3.txt'
        with open(phase3_path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        # Chỉ giữ lại đúng 2900 records đầu nếu đã có
        base_lines = lines[:2900]
        
        # Format batch 30
        new_batch_lines = []
        for text, triplets in batch30_data:
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
