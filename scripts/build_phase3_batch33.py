# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn chuẩn hóa cho Phase 3 - Batch 33 (Records 3201 - 3300).
Tuân thủ 100% tài liệu BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md.
"""

batch33_data = [
    # Rec 3201: Cắt cụt đuôi câu 'theo' -> REJECT
    ("Tại TP. Hồ Chí Minh , Đợt xả dự kiến kéo dài đến ngày 7 / 12 và có thể gây ngập nhiều vùng hạ lưu , theo", []),

    # Rec 3202: Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Bình Dương : Mưa lớn gây ngập ở 2 thành phố , giao thông ùn tắc ⛈ ⛈ ⛈", []),

    # Rec 3203: Đã có CHỢ THỦ ĐỨC
    ("TP. HCM MƯA TRẮNG TRỜI , CHỢ THỦ ĐỨC LẠI NGẬP NẶNG Chiều 31 / 5 , Đài khí tượng thủy văn khu vực Nam Bộ thông tin , do hội tụ gió hoạt động mạnh kết hợp gió Tây Nam bị cơn bão số 1 hút khiến thời tiết miền Nam chuyển xấu , nhiều nơi mưa to .", [
        ([6, 7, 8], [10, 11], 'NEG'),
    ]),

    # Rec 3204: Cắt cụt đuôi câu 'nguyên bán' -> REJECT
    ("Nếu là Lê Văn Thọ thì bạn sẽ bị ngập nửa bánh xe , còn Lê Đức Thọ thì nguyên bán", []),

    # Rec 3205: Dự án tương lai 2.700 tỷ -> REJECT
    ("🔥 Tin vui cho Thủ Đức 🔥 TPHCM dự chi 2 . 700 tỷ làm cống , mương và nạo vét để giảm ngập sau khi rác từ suối Linh Tây tràn ra đường Tô Ngọc Vân 👇 .", []),

    # Rec 3206: Dính markdown / cắt cụt -> REJECT
    ("Tại TP. Hồ Chí Minh , ![image](file:///D:/SE363_RAWDATA/data/processed/aste_v2_format/master_10k_triplets.txt) ngập", []),

    # Rec 3207: Đã có QUẬN 7, ĐƯỜNG TRẦN XUÂN SOẠN
    ("‼ ️ QUẬN 7 : TRIỀU CƯỜNG DÂN CAO , NƯỚC NGẬP ĐƯỜNG TRẦN XUÂN SOẠN ‼ ️ Người dân cho biết vào những năm trước , nước chỉ ngập nặng vào các tháng 8 , 9 , 10 nhưng năm nay , dù mới tháng 4 , triều cường đã lên rất cao .", [
        ([2, 3], [11], 'NEG'),
        ([12, 13, 14, 15], [11], 'NEG'),
        ([12, 13, 14, 15], [28, 29], 'NEG'),
    ]),

    # Rec 3208: Đã có đường Trần Xuân Soạn, quận 7
    ("Chiều 18 - 10 , triều cường dâng cao và đạt đỉnh , tuyến đường Trần Xuân Soạn , quận 7 , TP. HCM ngập nặng gây khó khăn cho người dân qua lại .", [
        ([13, 14, 15, 16, 17], [24, 25], 'NEG'),
        ([13, 14, 15, 16, 17], [26, 27, 28], 'NEG'),
        ([19, 20], [24, 25], 'NEG'),
    ]),

    # Rec 3209: Đã có TP. HCM
    ("Đây là 1 trong 8 tuyến đường thường xuyên ngập nặng do triều cường ở TP. HCM .", [
        ([15, 16], [9, 10], 'NEG'),
    ]),

    # Rec 3210: Đã có đường Trần Xuân Soạn, quận 7
    ("Triều cường khiến đường Trần Xuân Soạn ( quận 7 ) ngập cục bộ .", [
        ([3, 4, 5, 6], [11, 12, 13], 'NEG'),
        ([8, 9], [11, 12, 13], 'NEG'),
    ]),

    # Rec 3211: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhiều xe bị chết máy , người dân bì bõm dắt xe qua khu vực ngập .", [
        ([1], [6, 7], 'NEG'),
        ([1], [11, 12, 13, 14], 'NEG'),
    ]),

    # Rec 3212: Đã có đường Trần Xuân Soạn
    ("Triều cường ‘ nuốt ’ đường Trần Xuân Soạn , người dân TP. HCM bì bõm giờ tan tầm 😟 # TNN # YeaH1", [
        ([5, 6, 7, 8], [15, 16], 'NEG'),
    ]),

    # Rec 3213: Đã có QUẬN 7, đường Trần Xuân Soạn, quận 7
    ("QUẬN 7 QUÁ QUEN : TRIỀU CƯỜNG LÊN ĐỈNH , NGƯỜI DÂN CHẬT VẬT LỘI NƯỚC VỀ NHÀ Chiều nay ( 18 / 10 ) , triều cường xuất hiện gây ngập đường Trần Xuân Soạn ( quận 7 ) đã khiến việc đi lại của người dân gặp nhiều trở ngại .", [
        ([0, 1], [12, 13, 14, 15], 'NEG'),
        ([32, 33, 34, 35], [31], 'NEG'),
        ([37, 38], [31], 'NEG'),
    ]),

    # Rec 3214: Bàn luận dự án tương lai 375 tỷ -> REJECT
    ("Với vốn đầu tư 375 tỉ đồng để cải tạo đường và làm kè chống ngập , kết hợp với hạng mục cống Tân Thuận của dự án ngăn triều 10 . 000 tỉ , đường Trần Xuân Soạn , quận 7 , TP. HCM được kỳ vọng hết ngập .", []),

    # Rec 3215: Đã có TP. HCM
    ("🛑 Triều cường liên tục nhiều ngày , người dân TP. HCM mệt mỏi lội nước .", [
        ([10, 11], [12, 13, 14, 15], 'NEG'),
    ]),

    # Rec 3216: Đã có TP. HCM
    ("Chiều 24 - 10 , triều cường tiếp tục dâng cao , khiến nhiều khu vực ở TP. HCM bị ngập .", [
        ([17, 18], [20], 'NEG'),
    ]),

    # Rec 3217: Dự án nâng cấp bờ kè -> REJECT
    ("# KTSGOnline - Đường Trần Xuân Soạn , quận 7 , TPHCM sẽ được chính quyền thành phố nâng cấp mặt đường , bờ kè để chống ngập .", []),

    # Rec 3218: Đã có TP. HCM
    ("Triều cường dâng khiến một số tuyến đường ở TP. HCM ngập nước giờ tan tầm , người dân vất vả lội nước .", [
        ([10, 11], [12, 13], 'NEG'),
        ([10, 11], [19, 20, 21, 22], 'NEG'),
    ]),

    # Rec 3219: Đã có đường Trần Xuân Soạn, quận 7
    ("Triều cường dâng cao 1 , 68 m khiến đường Trần Xuân Soạn , quận 7 ( TP. HCM ) , ngập nặng nhất , hàng loạt xe chết máy , người đi đường lội bì bõm , sinh hoạt bị đảo lộn", [
        ([9, 10, 11, 12], [21, 22, 23], 'NEG'),
        ([9, 10, 11, 12], [28, 29], 'NEG'),
        ([9, 10, 11, 12], [34, 35, 36], 'NEG'),
        ([9, 10, 11, 12], [40, 41, 42], 'NEG'),
        ([14, 15], [21, 22, 23], 'NEG'),
    ]),

    # Rec 3220: Bàn luận hạ tầng chưa đầu tư -> REJECT
    ("Đây là một đoạn từ 1135 / 83 đến Đào Trí , trước đây chỉ là đường đất chưa được đầu tư hệ thống cống thoát nước , dẫn đến gây ngập úng", []),

    # Rec 3221: Đã có Huỳnh Tấn Phát, Trần Xuân Soạn
    ("Triều cường sẽ đạt đỉnh đến ngày 26 / 10 Các tuyến đường Huỳnh Tấn Phát , Trần Xuân Soạn bị ngập do triều cường .", [
        ([13, 14, 15], [20, 21], 'NEG'),
        ([17, 18, 19], [20, 21], 'NEG'),
    ]),

    # Rec 3222: Triều cường mồ côi -> Quy tắc 6 mở rộng in-place
    ("Mỗi khi triều cường ở TPHCM đạt đỉnh , nước có thể ngập từ 30 phút đến 120 phút .", [
        ([2, 3, 4, 5], [10, 11, 12], 'NEU'),
    ]),

    # Rec 3223: Tản văn so sánh thơ + cắt cụt đuôi câu -> REJECT
    ("Tại TP. Hồ Chí Minh , Trời nắng thì bụi mù đường , tưởng đâu lại lạc vô thơ Hàn Mạc Tử ; trời mưa thì ngập hơn nửa bánh xe , sóng đánh như biể", []),

    # Rec 3224: Đã có Hẻm 719 đường Huỳnh Tấn Phát, Q. 7
    ("Hẻm 719 đường Huỳnh Tấn Phát ( Q. 7 , TP. HCM ) những ngày qua giống như một con sông mênh mông nước , người dân trong hẻm phải chèo xuồng đưa con đi học giữa phố vì nước ngập sâu , nhiều ngày không rút .", [
        ([0, 1, 2, 3, 4, 5], [18, 19, 20], 'NEG'),
        ([0, 1, 2, 3, 4, 5], [39, 40, 41], 'NEG'),
        ([7, 8], [18, 19, 20], 'NEG'),
    ]),

    # Rec 3225: Cắt cụt đuôi câu 'ngày thứ' -> REJECT
    ("🚣 TP HỒ CHÍ MINH : TRIỀU CƯỜNG VƯỢT MỨC BÁO ĐỘNG 3 , NGƯỜI DÂN BÌ BÕM LỘI NƯỚC VỀ NHÀ 🚣 Chiều 26 / 10 , nhiều khu vực trũng , thấp và ven sông lại bị ngập úng do đỉnh triều cường đạt mức hơn 1 , 73m , tiếp tục vượt mức báo động III ngày thứ", []),

    # Rec 3226: Đã có hẻm 719 đường Huỳnh Tấn Phát, quận 7
    ("KHU DÂN CƯ Ở TPHCM NGẬP NƯỚC QUANH NĂM DO TRIỀU CƯỜNG Khu dân cư trong hẻm 719 đường Huỳnh Tấn Phát ( quận 7 , TPHCM ) ngập nước quanh năm do triều cường khiến cuộc sống người dân nơi đây đảo lộn .", [
        ([16, 17, 18, 19, 20, 21], [28, 29, 30, 31], 'NEG'),
        ([23, 24], [28, 29, 30, 31], 'NEG'),
    ]),

    # Rec 3227: Đã có Trần Xuân Soạn, Trần Trọng Cung, Nguyễn Thị Thập, Phạm Hữu Lầu, Quận 7
    ("Trần Xuân Soạn , Trần Trọng Cung , Nguyễn Thị Thập , Phạm Hữu Lầu . . . nói chung Quận 7 ngập ' từa lưa hột dưa ' ae lưu ý !", [
        ([0, 1, 2], [22], 'NEG'),
        ([4, 5, 6], [22], 'NEG'),
        ([8, 9, 10], [22], 'NEG'),
        ([12, 13, 14], [22], 'NEG'),
        ([20, 21], [22], 'NEG'),
    ]),

    # Rec 3228: Khẩu hiệu nhắc nhở -> REJECT
    ("Tại TP. Hồ Chí Minh , BÀ CON NƠI BỊ NGẬP HẾT SỨC LƯU Ý NHÉ !", []),

    # Rec 3229: Đã có TP. HCM, Dự báo tương lai -> NEU (Pass 8)
    ("_______________ Trong hai ngày 15 / 11 và 16 / 11 , TP. HCM có nguy cơ bị ngập nặng do triều cường đạt đỉnh với mức nước cao 1 , 76m , cao nhất từ đầu năm đến nay .", [
        ([12, 13], [14, 15, 16, 17, 18, 19], 'NEU'),
    ]),

    # Rec 3230: Đã có TP. HCM
    ("ĐƯỜNG PHỐ TP. HCM NGẬP LÊNH LÁNG SAU MƯA LỚN , NHIỀU XE CHẾT MÁY TRONG BIỂN NƯỚC Chiều tối 6 / 10 , cơn mưa lớn trút xuống một số nơi tại TP. HCM khiến nhiều tuyến đường ngập sâu .", [
        ([2, 3], [4, 5, 6], 'NEG'),
        ([2, 3], [13, 14], 'NEG'),
        ([33, 34], [39, 40], 'NEG'),
    ]),

    # Rec 3231: Đã có TP. HCM
    ("🌧 Các ngả đường TP. HCM thành ' sông ' sau trận mưa lớn Chiều tối 19 / 9 , TP. HCM có mưa lớn kèm theo giông khiến đường sá ở hầu hết quận trên địa bàn bị ngập .", [
        ([4, 5], [38, 39], 'NEG'),
        ([20, 21], [38, 39], 'NEG'),
    ]),

    # Rec 3232: Đã có TP. HCM
    ("Chiều và tối vài ngày vừa qua , người dân TP. HCM rất khổ sở trên đường về nhà sau giờ tan tầm , vì triều cường trên các sông dâng cao .", [
        ([10, 11], [12, 13], 'NEG'),
    ]),

    # Rec 3233: Đã có Nguyễn Bình, Mương Chuối
    ("— Nguyễn Bình ( Mương Chuối ) thất thủ nước ngập cao hơn hôm qua hơn 40t mới thấy 😂 😂", [
        ([1, 2], [7, 8], 'NEG'),
        ([1, 2], [9, 10, 11], 'NEG'),
        ([4, 5], [7, 8], 'NEG'),
    ]),

    # Rec 3234: Đã có đường Nguyễn Bình - Lê Văn Lương, huyện Nhà Bè
    ("Người dân đi trên tuyến đường Nguyễn Bình - Lê Văn Lương , huyện Nhà Bè , đã được cảnh sát dùng xe chuyên dụng chở qua đoạn ngập nặng bởi triều cường .", [
        ([5, 6, 7, 8, 9, 10, 11], [28, 29], 'NEG'),
        ([13, 14, 15], [28, 29], 'NEG'),
    ]),

    # Rec 3235: Cắt cụt đuôi câu 'khiến các' -> REJECT
    ("Bốn ngày qua , triều cường lên cao vượt mức báo động 3 , huyện Nhà Bè đạt đỉnh 1 , 7 m khiến các", []),

    # Rec 3236: Đã có TPHCM
    ("NHIỀU TUYẾN ĐƯỜNG Ở TPHCM LẠI NGẬP NHƯ SÔNG , NGƯỜI DÂN BẤT LỰC NHÌN NƯỚC BẨN TRÀN VÀO NHÀ 😰 Lúc 16h ngày 19 / 10 , mưa giông lớn trút xuống khu vực phía Tây Bắc TPHCM .", [
        ([4], [6, 7, 8], 'NEG'),
        ([4], [16, 17, 18, 19, 20], 'NEG'),
        ([35], [6, 7, 8], 'NEG'),
    ]),

    # Rec 3237: Dự báo sắp ngập nặng -> NEU (Pass 8)
    ("THÀNH PHỐ HỒ CHÍ MINH SẮP NGẬP NẶNG VÌ TRIỀU CƯỜNG CAO NHẤT NĂM Dự báo , từ ngày 15 / 11 , mực nước tại trạm Phú An - sông Sài Gòn lên nhanh , đỉnh triều sẽ xuất hiện ở 2 khung 16 - 18h và 17 - 19h .", [
        ([0, 1, 2, 3, 4], [5, 6, 7], 'NEU'),
    ]),

    # Rec 3238: Đã có đường Lê Văn Việt
    ("Mưa lớn kéo dài 30 phút khiến đường Lê Văn Việt nước ngập sâu kéo dài gần 1km khiến người dân đi lại khó khăn .", [
        ([7, 8, 9, 10], [12, 13], 'NEG'),
        ([7, 8, 9, 10], [21, 22, 23, 24], 'NEG'),
    ]),

    # Rec 3239: Hải Phòng -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , 🤔 Ngập lụt rõ luôn # haiphongnews", []),

    # Rec 3240: Đà Nẵng / Kiệt Bạch Đằng -> REJECT tỉnh ngoài
    ("Khẩn cấp cứu người 🆘 2 / 1 kiệt 290 bạch đằng , 4 ng ở trên 1 cái gác nhỏ gần ngập rồi ạ . . nhiều ngày chưa ăn uống cần trợ giúp 🙏 🙏", []),

    # Rec 3241: Đã có TP. HCM
    ("❗ ️ TP. HCM TỐI NAY : ÙN TẮC GIAO THÔNG DO MƯA NGẬP HƠN 2 GIỜ 😢 Cơn mưa lớn kéo dài hơn hai giờ tối 8 / 10 khiến nhiều tuyến đường trung tâm TP. HCM ngập sâu , sóng đánh ngã người đi xe máy , giao thông hỗn loạn và ùn tắc kéo dài .", [
        ([2, 3], [38, 39], 'NEG'),
        ([36, 37], [38, 39], 'NEG'),
    ]),

    # Rec 3242: Quảng cáo bán hàng ngập shop -> REJECT
    ("❣ Hàng về ngập shop nha khách yêu ! ❣ 🏠 * 424A Nguyễn Xí , P. 13 , Q. Bình Thạnh * 71 Nguyễn Gia Trí ( đường D2 cũ ) , P. 25 , Q. Bình Thạnh", []),

    # Rec 3243: Đã có TP. HCM, quận Bình Thạnh
    ("Người dân TP. HCM dắt bộ xe máy đi làm trong mưa lớn Sáng 25 / 5 , mưa lớn khiến nhiều khu vực tại quận Bình Thạnh ( TP. HCM ) ngập nặng .", [
        ([2, 3], [4, 5, 6, 7], 'NEG'),
        ([25, 26, 27], [32, 33], 'NEG'),
    ]),

    # Rec 3244: Cắt cụt đuôi câu 'Mưa lớn kéo' -> REJECT
    ("Hẻm ở TP. HCM ngập như cống thoát nước sau mưa lớn Mưa lớn kéo", []),

    # Rec 3245: Đã có TP. HCM, quận Bình Thạnh, TP Thủ Đức
    ("Nhiều tuyến đường ở TP. HCM thành biển nước trong mưa lớn Cơn mưa đổ xuống chưa đầy một giờ nhưng làm nhiều tuyến đường tại quận Bình Thạnh , TP Thủ Đức ngập nặng .", [
        ([4, 5], [6, 7, 8], 'NEG'),
        ([24, 25, 26], [31, 32], 'NEG'),
        ([28, 29, 30], [31, 32], 'NEG'),
    ]),

    # Rec 3246: Vincom Trần Phú -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Mới được đoạn Vincom - Trần Phú Vietcombank chứ còn lại đang ngập .", []),

    # Rec 3247: Cảnh báo triều cường tương lai -> NEU (Pass 8)
    ("🛑 Có thể là bơi luôn : Nhà Bè , Quận 7 cảnh báo triều cường đạt đỉnh trong 2 ngày tới , vượt mức báo động III", [
        ([7, 8], [12, 13, 14, 15, 16], 'NEU'),
        ([10, 11], [12, 13, 14, 15, 16], 'NEU'),
    ]),

    # Rec 3248: Dự báo đỉnh triều tương lai -> NEU (Pass 8)
    ("TP. HCM sắp đón đỉnh triều cường cao nhất năm Dự báo đỉnh triều cường đợt rằm tháng 10 âm lịch tại TP. HCM có khả năng cao nhất năm , xuất hiện vào ngày 27 - 29 / 11 ở mức từ 1 , 7 - 1 , 75m gây ngập úng vùng trũng thấp , ven sông .", [
        ([0, 1], [50, 51, 52], 'NEU'),
        ([22, 23], [50, 51, 52], 'NEU'),
    ]),

    # Rec 3249: Khuyên đề phòng ngập úng, Fallback 'Tại TPHCM , ' -> NEU (Pass 8)
    ("Tại TPHCM , “ Đây là kỳ triều cường cao , cần đề phòng ngập úng những vùng trũng thấp và ven sông .", [
        ([1], [11, 12, 13, 14, 15], 'NEU'),
    ]),

    # Rec 3250: Dự báo các tuyến đường có khả năng bị ngập -> NEU (Pass 8)
    ("Một vài tuyến đường có khả năng bị ngập , như : đường Trần Xuân Soạn , Đào Sư Tích , Huỳnh Tấn Phát , Nguyễn Bình , Lê Văn Lương , Quốc lộ 50 , Phạm Hữu Lầu .", [
        ([12, 13, 14, 15], [4, 5, 6, 7, 8], 'NEU'),
        ([17, 18, 19], [4, 5, 6, 7, 8], 'NEU'),
        ([21, 22, 23], [4, 5, 6, 7, 8], 'NEU'),
        ([25, 26], [4, 5, 6, 7, 8], 'NEU'),
        ([28, 29, 30], [4, 5, 6, 7, 8], 'NEU'),
        ([32, 33, 34], [4, 5, 6, 7, 8], 'NEU'),
        ([36, 37, 38], [4, 5, 6, 7, 8], 'NEU'),
    ]),

    # Rec 3251: CSGT giúp dân (People role) + cắt cụt đuôi câu -> REJECT
    ("📸 📸 📸 GÓC ẢNH ĐẸP : CẢNH SÁT GIAO THÔNG CÔNG AN HUYỆN NHÀ BÈ HỖ TRỢ NGƯỜI DÂN LƯU THÔNG QUA CÁC ĐIỂM NGẬP SÂU DO TRIỀU CƯỜNG — — — — — — — — — — — — — — — Chiều ngày 25 / 10 / 2022 , triều cường tại trạm Phú An , Sông Sà", []),

    # Rec 3252: Đã có Đường Kha Vạn Cân, TP Thủ Đức
    ("Đường Kha Vạn Cân , TP Thủ Đức ngập nửa bánh xe do mưa lớn 🥹", [
        ([0, 1, 2, 3], [8, 9, 10, 11], 'NEG'),
        ([5, 6, 7], [8, 9, 10, 11], 'NEG'),
    ]),

    # Rec 3253: Đã có Đường Kha Vạn Cân, TP Thủ Đức
    ("( PLO ) - Đường Kha Vạn Cân ( TP Thủ Đức , TP. HCM ) ngập mênh mông trong cơn mưa lớn , khiến nhiều phương tiện di chuyển khó khăn .", [
        ([4, 5, 6, 7], [16, 17], 'NEG'),
        ([4, 5, 6, 7], [27, 28, 29, 30], 'NEG'),
        ([9, 10, 11], [16, 17], 'NEG'),
    ]),

    # Rec 3254: Thống kê danh mục hành chính -> REJECT
    ("Tính đến tháng 10 / 2023 , trên địa bàn TP. HCM còn 13 tuyến đường trục chính ngập nước do mưa .", []),

    # Rec 3255: Đã có Phạm văn đồng, kha vạn cân, tô ngọc vân
    ("Phạm văn đồng đoạn giữ ngã tư kha vạn cân với tô ngọc vân bị ngập nặng .", [
        ([0, 1, 2], [14, 15, 16], 'NEG'),
        ([7, 8, 9], [14, 15, 16], 'NEG'),
        ([11, 12, 13], [14, 15, 16], 'NEG'),
    ]),

    # Rec 3256: Đã có THỦ ĐỨC, Thủ Đức
    ("NHỮNG TUYẾN ĐƯỜNG CẦN TRÁNH Ở THỦ ĐỨC KHI MƯA LỚN 🌧 Vào mùa mưa , tình trạng ngập nước ở Thủ Đức là điều không thể tránh khỏi .", [
        ([6, 7], [16, 17, 18, 19], 'NEG'),
        ([21, 22], [16, 17, 18, 19], 'NEG'),
    ]),

    # Rec 3257: Triển khai 18 công trình chống ngập -> REJECT
    ("QUẬN THỦ ĐỨC Triển khai 18 công trình chống ngập úng .", []),

    # Rec 3258: Chủ trương hành chính dự án -> REJECT
    ("Ngày 4 / 7 , UBND TP đã chấp thuận cho UBND quận Thủ Đức làm chủ đầu tư thực hiện 18 công trình bờ bao phòng , chống triều cường , ngập úng , bảo vệ an toàn khu dân cư trên địa bàn quận .", []),

    # Rec 3259: Đề tài khoa học + cắt cụt đuôi câu 'trong tương l' -> REJECT
    ("Nhóm thực hiện đề xuất giải pháp nâng cấp cải tạo hệ thống thoát nước ngắn hạn nhằm giải quyết cấp bách điểm ngập nghiêm trọng tại giao lộ đường Phạm Văn Đồng - Tô Ngọc Vân ( thành phố Thủ Đức ) và ứng phó với sự gia tăng lượng mưa trong tương l", []),

    # Rec 3260: Đã có quận 1, 12, TP Thủ Đức
    ("Mưa lớn hơn hai giờ , một số đường ở quận 1 , 12 và TP Thủ Đức ngập nặng , nước cuồn cuộn vào nhà dân , nhiều người không kịp trở tay , chiều 5 / 7 .", [
        ([10, 11], [18, 19], 'NEG'),
        ([13], [18, 19], 'NEG'),
        ([15, 16, 17], [18, 19], 'NEG'),
        ([15, 16, 17], [21, 22, 23, 24, 25, 26], 'NEG'),
    ]),

    # Rec 3261: Đã có TP. HCM
    ("Những ngày qua , mưa lớn kéo dài khiến nhiều khu vực trên địa bàn TP. HCM ngập sâu .", [
        ([15, 16], [17, 18], 'NEG'),
    ]),

    # Rec 3262: Cắt cụt đuôi câu 'DƯỚI LÀN MƯA...' -> REJECT
    ("NGƯỜI DÂN TP. HCM BÌ BÕM DƯỚI LÀN MƯA GIỜ TAN TẦM . . .", []),

    # Rec 3263: Đã có TP. HCM
    ("MỘT CƠN MƯA TRÁI MÙA ĐI QUA KHIẾN TP. HCM NGẬP ÚNG 🌧 Chiều 28 / 12 , nhiều khu vực ở TP. HCM xuất hiện trận mưa lớn trái mùa gây ngập đường , khiến người dân di chuyển vất vả .", [
        ([8, 9], [10, 11], 'NEG'),
        ([22, 23], [31, 32], 'NEG'),
        ([22, 23], [39, 40], 'NEG'),
    ]),

    # Rec 3264: Đã có TPHCM
    ("‼ ️ TPHCM : ĐƯỜNG LẠI BIẾN THÀNH SÔNG SAU MƯA 🌧 Trưa 12 / 5 , tại một số quận , huyện của TPHCM tiếp tục có mưa to , nhiều điểm ngập do nước không rút kịp , gây ách tắc giao thông .", [
        ([2], [4, 5, 6, 7, 8], 'NEG'),
        ([24], [40, 41, 42, 43, 44], 'NEG'),
    ]),

    # Rec 3265: Thống kê xã hội học -> REJECT
    ("Theo thống kê , 54 % dân số ở TP. HCM thường xuyên trải nghiệm ngập lụt đô thị , triều cường , kẹt xe , gây thiệt hại hơn 3 tỉ USD mỗi năm .", []),

    # Rec 3266: Đã có TP HCM
    ("Cơn mưa lớn kéo dài hơn một giờ khiến nhiều tuyến đường ở TP HCM ngập sâu , nước tràn vào nhà khiến sinh hoạt của người dân bị đảo lộn , chiều 22 / 6 .", [
        ([13, 14], [15, 16], 'NEG'),
        ([13, 14], [18, 19, 20, 21], 'NEG'),
        ([13, 14], [28, 29, 30], 'NEG'),
    ]),

    # Rec 3267: Đã có Thảo Điền, TPHCM
    ("Phố \" nhà giàu \" Thảo Điền ngập sâu , người dân bì bõm lội nước - - - - Chiều ngày 2 . 6 , mưa rào xuất hiện ở TPHCM gây ngập nhiều tuyến đường .", [
        ([5, 6], [7, 8], 'NEG'),
        ([5, 6], [12, 13, 14, 15], 'NEG'),
        ([31], [32, 33], 'NEG'),
    ]),

    # Rec 3268: Đã có Đường Quốc Hương, phường Thảo Điền, Quận 2
    ("Đường Quốc Hương , phường Thảo Điền , Quận 2 đoạn trước Trường Đại học Văn hóa ) là khu vực ngập sâu nhất .", [
        ([0, 1, 2], [20, 21, 22], 'NEG'),
        ([4, 5, 6], [20, 21, 22], 'NEG'),
        ([8, 9], [20, 21, 22], 'NEG'),
    ]),

    # Rec 3269: Cắt cụt đuôi câu 'TP.' -> REJECT
    ("Mưa lớn , xe máy ngã nhào khi qua ' rốn ngập ' khu nhà giàu ở TPHCM Mưa lớn khiến đường Quốc Hương ( phường Thảo Điền , TP.", []),

    # Rec 3270: Cắt cụt đầu câu 'Thủ Đức , TPHCM )' -> REJECT
    ("Thủ Đức , TPHCM ) ngập nặng .", []),

    # Rec 3271: Không có từ ngập -> REJECT
    ("Tại TP. Hồ Chí Minh , Nhiều xe máy qua đây bị chết máy , ngã nhào .", []),

    # Rec 3272: Cắt cụt đầu câu 'Thủ Đức ) như chìm...' -> REJECT
    ("Thủ Đức ) như chìm trong biển nước , đặc biệt tại đường Quốc Hương nước ngập sâu hơn nửa mét , xe cộ chết máy hàng loạt khi qua đây .", []),

    # Rec 3273: Đã có TP Thủ Đức, quận Bình Thạnh
    ("Đường TP HCM ngập nửa mét sau mưa lớn Cơn mưa kéo dài khiến nhiều đường ở TP Thủ Đức , quận Bình Thạnh , ngập sâu nửa mét , người dân bì bõm đẩy , dắt xe chết máy về nhà , chiều 1 / 10 .", [
        ([17, 18, 19], [25, 26, 27, 28], 'NEG'),
        ([17, 18, 19], [38, 39], 'NEG'),
        ([21, 22, 23], [25, 26, 27, 28], 'NEG'),
    ]),

    # Rec 3274: Cắt cụt đuôi câu 'Ở TP.' -> REJECT
    ("Tại TP. Hồ Chí Minh , NHIỀU NGƯỜI NGÃ NHÀO TRÊN ĐƯỜNG NGẬP TRONG CƠN MƯA LỚN KÉO DÀI Ở TP.", []),

    # Rec 3275: Cắt cụt đuôi câu 'trẻ n' -> REJECT
    ("HỒ CHÍ MINH Cơn mưa lớn kéo dài hơn 3 giờ khiến một số tuyến đường ở TPHCM bị ngập sâu , nhiều người dân bị ngã nhào cả người lẫn xe trên đường ngập , trẻ n", []),

    # Rec 3276: Đã có đường Bùi Bằng Đoàn, Phú Mỹ Hưng, quận 7
    ("Cơn mưa lớn chiều tối ngày 27 / 5 tại TPHCM đã gây ra tình trạng ngập úng trên tuyến đường Bùi Bằng Đoàn , khu đô thị Phú Mỹ Hưng , quận 7 .", [
        ([20, 21, 22, 23], [14, 15, 16, 17], 'NEG'),
        ([25, 26, 27, 28, 29, 30], [14, 15, 16, 17], 'NEG'),
        ([32, 33], [14, 15, 16, 17], 'NEG'),
    ]),

    # Rec 3277: Cắt cụt đuôi câu 'đều tỏ ra k' -> REJECT
    ("Tại TP. Hồ Chí Minh , Theo một cư dân ngụ tại đây chia sẻ , đây là lần đầu tiên khu vực này bị ngập nặng nên đa số người dân đều tỏ ra k", []),

    # Rec 3278: Cắt cụt đuôi câu 'phường 9 , q' -> REJECT
    ("CỨ ĐẾN MÙA MƯA LÀ NGƯỜI DÂN TP. HCM PHẢI CHỊU CẢNH NGẬP NƯỚC THƯỜNG XUYÊN KỂ CẢ TẠI NHỮNG TUYẾN ĐƯỜNG CAO RÁO CÓ ĐỘ DỐC LỚN 🌊 Khi TP. HCM vào mùa mưa , nhiều hộ dân sống bên đường Nguyễn Văn Khối , phường 9 , q", []),

    # Rec 3279: Đã có Nguyễn Hữu Cảnh, Q. Bình Thạnh
    ("Rốn ngập ” Nguyễn Hữu Cảnh ở Q. Bình Thạnh ( TP. HCM ) đã được đầu tư máy bơm , triển khai dự án nâng đường nhưng mưa xuống vẫn ngập sâu .", [
        ([3, 4, 5], [31, 32], 'NEG'),
        ([7, 8, 9], [31, 32], 'NEG'),
    ]),

    # Rec 3280: Đã có Đường Nguyễn Hữu Cảnh, quận Bình Thạnh
    ("Khiếp quá 😥 Đường Nguyễn Hữu Cảnh ( quận Bình Thạnh ) mưa lớn gây ngập lút yên xe .", [
        ([3, 4, 5, 6], [14, 15, 16, 17], 'NEG'),
        ([8, 9, 10], [14, 15, 16, 17], 'NEG'),
    ]),

    # Rec 3281: Hỏi đường -> REJECT
    ("Đường Lê Văn Việt gần cầu Bến Nọc ngập không bà con .", []),

    # Rec 3282: Tiêu đề câu hỏi -> REJECT
    ("Khi nào “ rốn ngập ” Nguyễn Hữu Cảnh sẽ hết ngập ?", []),

    # Rec 3283: Đã có TP. HCM
    ("Chiều 3 / 6 , cơn mưa như trút nước xảy ra trên diện rộng ở TP. HCM khiến hàng loạt tuyến đường ngập như sông .", [
        ([16, 17], [23, 24, 25], 'NEG'),
    ]),

    # Rec 3284: Đã có đường Nguyễn Hữu Cảnh, quận Bình Thạnh
    ("Tại khu vực “ rốn ngập ” đường Nguyễn Hữu Cảnh ( quận Bình Thạnh ) nước cũng ngập lênh láng .", [
        ([7, 8, 9, 10], [18, 19, 20], 'NEG'),
        ([12, 13, 14], [18, 19, 20], 'NEG'),
    ]),

    # Rec 3285: Chỉ đạo hành chính xử lý máy bơm -> REJECT
    ("UBND TP. HCM yêu cầu Sở Xây dựng có chính kiến cụ thể về phương án xử lý máy bơm chống ngập đường Nguyễn Hữu Cảnh , sau khi tuyến đường này được cải tạo và trải qua mùa mưa năm 2021 không còn ngập .", []),

    # Rec 3286: Cắt cụt đuôi câu 'TP.' -> REJECT
    ("Chống ngập đường Nguyễn Hữu Cảnh , TP.", []),

    # Rec 3287: Cắt cụt đuôi câu 'đến cu' -> REJECT
    ("Đường Nguyễn Hữu Cảnh sẽ hết ngập , lún Ông Nguyễn Vĩnh Ninh , giám đốc Khu quản lý giao thông đô thị số 1 ( Sở GTVT TP. HCM ) cho biết : dự kiến trong tháng 10 sẽ tổ chức đấu thầu chọn đơn vị thi công dự án sửa chữa đường Nguyễn Hữu Cảnh , đến cu", []),

    # Rec 3288: Đã có đường Nguyễn Hữu Cảnh
    ("Cơm mưa lớn chiều 16 . 6 làm tái diễn cảnh ngập nặng trên đường Nguyễn Hữu Cảnh - bị xem là \" rốn ngập \" ở TPHCM nhiều năm nay .", [
        ([15, 16, 17, 18], [13, 14], 'NEG'),
    ]),

    # Rec 3289: Tranh cãi dự án 10 ngàn tỷ -> REJECT
    ("Nguyễn Hữu Cảnh , quận Bình Thạnh \" thất thủ \" dự án 10 ngàn tỷ chống ngập ở đâu . . .", []),

    # Rec 3290: Tranh cãi hợp đồng thuê máy bơm -> REJECT
    ("Tuyến đường Nguyễn Hữu Cảnh vừa được đầu tư gần 500 tỷ đồng để nâng cấp hệ thống thoát nước để chống ngập nhưng có vẻ vẫn còn chật vật quá !", []),

    # Rec 3291: Hợp đồng kinh tế thuê máy bơm -> REJECT
    ("Nếu tiến độ sửa chữa đường Nguyễn Hữu Cảnh chậm trễ do lỗi chủ quan từ phía chủ đầu tư và nhà thầu , chủ đầu tư sẽ phải trả tiền thuê máy bơm chống ngập cho \" rốn ngập \" này .", []),

    # Rec 3292: Giải trình kỹ thuật máy bơm bất lực -> REJECT
    ("Chủ siêu máy bơm đã lý giải nguyên nhân khiến máy bơm bất lực trong việc giải cứu đường Nguyễn Hữu Cảnh trong trận mưa ngập vào trưa nay ( 17 / 10 ) .", []),

    # Rec 3293: Cắt cụt đuôi câu 'nâng c' -> REJECT
    ("TP. HCM : Hoàn thành nâng cấp , giải quyết điểm ngập Nguyễn Hữu Cảnh Sáng 30 / 4 , Ban Quản lý dự án đầu tư xây dựng các công trình giao thông Thành phố Hồ Chí Minh ( Ban Giao thông ) đã chính thức thông xe và đưa vào khai thác dự án sửa chữa , nâng c", []),

    # Rec 3294: Đã có TP. HCM
    ("Nửa đêm , nhiều tuyến đường vẫn ngập sâu , người dân TP. HCM vất vả tìm đường về nhà .", [
        ([12, 13], [7, 8], 'NEG'),
        ([12, 13], [14, 15], 'NEG'),
    ]),

    # Rec 3295: Cắt cụt đuôi câu 'dự án n' -> REJECT
    ("Khi cơ quan chức năng công bố thông tin đầu tư gần 500 tỉ đồng nâng đường Nguyễn Hữu Cảnh , quận Bình Thạnh , TPHCM , rất nhiều hộ dân ở đây lo lắng nước ngập sẽ dồn vào các con hẻm và tái diễn tình trạng nhà biến hành hầm chứa nước như dự án n", []),

    # Rec 3296: Hợp đồng thuê máy bơm -> REJECT
    ("Đường Nguyễn Hữu Cảnh sau khi cải tạo bằng vốn ngân sách đã không còn ngập khi mưa , nên TP. HCM không còn nhu cầu thuê máy bơm chống ngập của Công ty Quang Trung .", []),

    # Rec 3297: Tản văn so sánh Venice -> REJECT
    ("Thành phố mang tên Bác sau một cơn mưa tầm tã , nghe đâu đường Nguyễn Hữu Cảnh hiện nay nước ngập đến capo xe và gây kẹt xe do xe bị chết máy . . . Ngày nào cũng mưa kiểu này có khi đặt tên thành phố thành Saigon Water Park City - một Venice mới", []),

    # Rec 3298: Đã có Thảo Điền
    ("Chỗ mọi người thế nào khu Thảo Điền ngập lút sau cơn mưa chiều nay 10 / 4 .", [
        ([6, 7], [8, 9], 'NEG'),
    ]),

    # Rec 3299: Cắt cụt đuôi câu '( TP.' -> REJECT
    ("Nước ngập hơn nửa mét ở phố ' nhà giàu ' Thảo Điền sau mưa : Tây , ta cùng lội nước Trưa 7 . 6 , sau cơn mưa lớn kéo dài hơn 1 giờ đồng hồ , khu phố ' nhà giàu ' Thảo Điền ( TP.", []),

    # Rec 3300: Cắt cụt đầu và đuôi câu -> REJECT
    ("Thủ Đức ) như chìm trong biển nước , đặc biệt tại đường Quốc Hương nước ngập sâ", []),
]

def test_triplets():
    flaws = 0
    print(f'Kiểm tra {len(batch33_data)} records...')
    for idx, (text, triplets) in enumerate(batch33_data, 3201):
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
        print('TẤT CẢ CÁC TRIPLETS CỦA BATCH 33 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!')
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
        
        # Chỉ giữ lại đúng 3200 records đầu nếu đã có
        base_lines = lines[:3200]
        
        # Format batch 33
        new_batch_lines = []
        for text, triplets in batch33_data:
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
