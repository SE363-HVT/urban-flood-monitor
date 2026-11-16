# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn chuẩn hóa cho Phase 3 - Batch 31 (Records 3001 - 3100).
Tuân thủ 100% tài liệu BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md.
"""

batch31_data = [
    # Rec 3001: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Các tuyến đường quanh khu vực này ngập lênh láng , các phương tiện di chuyển rất khó khăn .", [
        ([1], [7, 8], 'NEG'),
        ([1], [14, 15, 16], 'NEG'),
    ]),

    # Rec 3002: Thân câu 'nước ngập sâu...', Fallback 'Tại TPHCM , '
    ("Tại TPHCM , nước ngập sâu , nhiều xe chết máy , người dân chật vật lội nước về nhà .", [
        ([1], [3, 4], 'NEG'),
        ([1], [8, 9], 'NEG'),
        ([1], [13, 14, 15], 'NEG'),
    ]),

    # Rec 3003: Đã có chợ Thủ Đức, TP Thủ Đức
    ("Tại chợ Thủ Đức ( TP Thủ Đức , TP. HCM ) , mưa lớn khiến nước ngập lút bánh xe máy .", [
        ([1, 2, 3], [14, 15, 16, 17], 'NEG'),
        ([5, 6, 7], [14, 15, 16, 17], 'NEG'),
    ]),

    # Rec 3004: Thân câu 'Đường ngập sâu...', Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Đường ngập sâu , người dân bì bõm lội nước giữa trời mưa lớn .", [
        ([1], [3, 4], 'NEG'),
        ([1], [8, 9, 10], 'NEG'),
    ]),

    # Rec 3005: Đã có đường Huỳnh Tấn Phát, quận 7
    ("Mưa lớn kết hợp triều cường khiến đường Huỳnh Tấn Phát ( quận 7 ) ngập nặng , xe cộ chết máy hàng loạt .", [
        ([7, 8, 9, 10], [15, 16], 'NEG'),
        ([7, 8, 9, 10], [20, 21], 'NEG'),
        ([12, 13], [15, 16], 'NEG'),
    ]),

    # Rec 3006: Thảo luận băn khoăn về dự án nâng đường -> REJECT
    ("⚡ Người dân băn khoăn liệu rằng việc nâng đường Trần Xuân Soạn để giải quyết vấn đề ngập nước do triều cường có khiến nhà ở bị thấp xuống , thay vì ngập đường giờ ngập vào nhà dân không ?", []),

    # Rec 3007: Toàn hashtag không có địa danh cụ thể -> REJECT
    ("Đây là con đường thường xuyên chịu cảnh ngập nặng do triều cường # phuongnamhomnay # toancanh24h # vtv9 # news # tintuc # tinnhanh24h # alov9", []),

    # Rec 3008: Đã có Trần Xuân Soạn, Huỳnh Tấn Phát
    ("⚡ ️ Trần Xuân Soạn và Huỳnh Tấn Phát tiếp tục được réo tên trong Top 6 các tuyến đường ngập do triều cường của TP HCM .", [
        ([2, 3, 4], [18], 'NEG'),
        ([6, 7, 8], [18], 'NEG'),
    ]),

    # Rec 3009: Đã có đường Lê Văn Lương, phường Tân Hưng
    ("TP. HCM mưa lớn giữa trưa 1 . 11 , đường Lê Văn Lương ngập sâu Cơn mưa lớn vào giữa trưa 1 . 11 khiến nhiều tuyến đường , trong đó có đường Lê Văn Lương ( phường Tân Hưng , TP. HCM ) ngập sâu , người dân đi lại hết sức khó khăn .", [
        ([10, 11, 12, 13], [14, 15], 'NEG'),
        ([33, 34, 35, 36], [45, 46], 'NEG'),
        ([38, 39, 40], [45, 46], 'NEG'),
    ]),

    # Rec 3010: Đã có TP. HCM
    ("Mưa lớn , triều cường gây ngập : 23 tuyến đường ở TP. HCM thường xuyên chìm trong nước Từ đầu năm 2025 , TP. HCM ghi nhận 23 tuyến đường thường xuyên bị ngập do mưa lớn và triều cường , gây nhiều khó khăn cho sinh hoạt , đi lại của người dân .", [
        ([12, 13], [16, 17, 18], 'NEG'),
        ([24, 25], [33, 34], 'NEG'),
    ]),

    # Rec 3011: Đã có hẻm 458 / 20 Huỳnh Tấn Phát, Phường Tân Thuận
    ("Tình hình nước ngập lai láng nhiều ngày tại hẻm 458 / 20 Huỳnh Tấn Phát , Phường Tân Thuận .", [
        ([9, 10, 11, 12, 13, 14, 15], [2, 3, 4], 'NEG'),
        ([17, 18, 19], [2, 3, 4], 'NEG'),
    ]),

    # Rec 3012: Thân câu 'nước ngập làm hư đồ đạc...', Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Người dân cho biết nước ngập làm hư đồ đạc , đồ điện lạnh trong nhà . . . 😓", [
        ([1], [6, 7, 8, 9, 10], 'NEG'),
    ]),

    # Rec 3013: Đã có Thảo Điền
    ("Anh Chị Em nào có ý định qua Thảo Điền thì khoan đi nha , mưa to cộng với triều cường nên đang ngập dữ nha .", [
        ([7, 8], [21, 22], 'NEG'),
    ]),

    # Rec 3014: Đã có đường Nguyễn Văn Hưởng, Quốc Hương, đường Thảo Điền
    ("😞 Có 3 điểm ngập đường Nguyễn Văn Hưởng , Quốc Hương và đường Thảo Điền nha anh em !", []),

    # Rec 3015: Đã có Thảo Điền, Đường Thảo Điền, Quốc Hương, Nguyễn Văn Hưởng
    ("⚡ ️ Thảo Điền có 3 tuyến đường bất ngờ được gọi tên vào danh sách Top 13 tuyến đường chính ngập do mưa của Thành Phố gồm : Đường Thảo Điền , Quốc Hương , Nguyễn Văn Hưởng .", [
        ([2, 3], [21], 'NEG'),
        ([29, 30, 31], [21], 'NEG'),
        ([33, 34], [21], 'NEG'),
        ([36, 37, 38], [21], 'NEG'),
    ]),

    # Rec 3016: Đuôi câu cắt cụt 'Thảo Điền . . .' -> REJECT
    ("Cứ Mưa Là ngập , gần VT lắm rồi đó tak ơi 🥲 ‼ ️ TP. HCM : Cơn mưa lớn chiều 7 / 6 khiến nhiều tuyến đường bị ngập 🌊 Một số tuyến đường tại khu Thảo Điền ( TP Thủ Đức , TP. HCM ) như Quốc Hương , Tống Hữu Định , Thái Ly , Thảo Điền . . .", []),

    # Rec 3017: Đã có TP. HCM
    ("TP. HCM MƯA TRẮNG TRỜI , ÔTÔ CHẾT MÁY TRÊN ĐƯỜNG NGẬP SÂU 🌨 ☔ ️ 13h chiều 8 / 10 , TP. HCM đổ mưa lớn , chấm dứt cơn oi nóng hồi sáng .", [
        ([0, 1], [6, 7], 'NEG'),
        ([0, 1], [10, 11], 'NEG'),
    ]),

    # Rec 3018: Đã có TP. HCM
    ("Mưa lớn giữa trưa , nhiều tuyến đường tại TP. HCM ngập sâu Cơn mưa bắt đầu nặng hạt từ 11h30 và kéo dài khoảng 1 giờ , sau đó nhỏ dần .", [
        ([9, 10], [11, 12], 'NEG'),
    ]),

    # Rec 3019: Đã có quận Bình Thạnh, cắt tiền tố thừa
    ("Mưa lớn đã khiến cho nhiều con hẻm , tuyến đường tại quận Bình Thạnh bị ngập .", [
        ([12, 13, 14], [15, 16], 'NEG'),
    ]),

    # Rec 3020: Đã có TP Thủ Đức
    ("# Bản đồ các tuyến đường hay bị ngập nước khi trời mưa tại TP Thủ Đức Mùa mưa đã bắt đầu , nhiều tuyến đường tại TP Thủ Đức tiếp tục xuất hiện tình trạng ngập nước kéo dài .", [
        ([15, 16, 17], [7, 8], 'NEG'),
        ([28, 29, 30], [35, 36], 'NEG'),
    ]),

    # Rec 3021: Cắt cụt đuôi câu 'UBND' -> REJECT
    ("Tại TP. Hồ Chí Minh , Dưới đây là chi tiết 24 điểm , tuyến đường hay bị ngập theo thống kê của UBND", []),

    # Rec 3022: Đã có ĐƯỜNG NGUYỄN VĂN QUÁ, QUẬN 12, Hẻm 1134 Nguyễn Văn Quá, quận 12
    ("Ở ĐƯỜNG NGUYỄN VĂN QUÁ , QUẬN 12 NƯỚC NGẬP DỮ VẬY TA 😱 😱 😱 Hẻm 1134 Nguyễn Văn Quá ( khu phố 1 , phường Đông Hưng Thuận , quận 12 ) bị ngập tới đầu gối do nước từ con kênh ở thượng nguồn và đường lớn đổ về .", [
        ([1, 2, 3, 4], [9, 10], 'NEG'),
        ([6, 7], [9, 10], 'NEG'),
        ([16, 17, 18, 19, 20], [34, 35, 36, 37, 38], 'NEG'),
        ([31, 32], [34, 35, 36, 37, 38], 'NEG'),
    ]),

    # Rec 3023: Đã có TPHCM
    ("XE MÁY NGÃ NHÀO GIỮA ' BIỂN NƯỚC ' , NGƯỜI DÂN TPHCM CHẬT VẬT ĐI LÀM SÁNG SỚM 🤧 Khoảng 3h sáng nay ( 21 / 8 ) , cơn mưa dồn dập trút xuống TPHCM kèm theo giông , sấm sét .", [
        ([12], [1, 2, 3], 'NEG'),
        ([12], [13, 14], 'NEG'),
    ]),

    # Rec 3024: Cắt cụt lỡ dở 'ngập sâ' -> REJECT
    ("Chỉ trong khoảng 30 phút , nhiều tuyến đường ở TPHCM đã ngập sâ", []),

    # Rec 3025: Đã có TPHCM
    ("GIÔNG LỐC MẠNH , TÔN BAY NHƯ GIẤY TRÊN ĐƯỜNG Ở TPHCM 😭 Chiều tối nay ( 11 / 9 ) , tại TPHCM xuất hiện trận mưa giông lớn kéo dài hơn 2h gây ra tình trạng ngập nghiêm trọng hàng loạt tuyến đường .", [
        ([11], [38, 39, 40], 'NEG'),
        ([23], [38, 39, 40], 'NEG'),
    ]),

    # Rec 3026: Đã có TP. HCM
    ("Do ảnh hưởng của mưa lớn sáng nay , nhiều tuyến đường tại TP. HCM ngập nặng .", [
        ([13, 14], [15, 16], 'NEG'),
    ]),

    # Rec 3027: Đã có đường Chu Văn An, quận Bình Thạnh
    ("Trong cơn mưa lớn chiều 9 . 8 . 2024 , tại đường Chu Văn An ( quận Bình Thạnh , TP. HCM ) nhiều người ngâm mình trong dòng nước ngập để moi rác từ miệng cống , khơi thông dòng chảy .", [
        ([12, 13, 14, 15], [30, 31], 'NEG'),
        ([17, 18, 19], [30, 31], 'NEG'),
    ]),

    # Rec 3028: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , ngập sâu , nước tràn vào nhà , người dân dùng xô tát ra ngoài , chiều 1 / 9 .", [
        ([1], [3, 4], 'NEG'),
        ([1], [6, 7, 8, 9], 'NEG'),
    ]),

    # Rec 3029: Đã có Bình Thạnh, TP. HCM
    ("🌧 Bình Thạnh : Mưa lớn chiều 10 / 6 , đường ngập sâu đến thắt lưng , dân vất vả khơi cống Chiều 10 / 6 , cơn mưa lớn kéo dài từ khoảng 17h khiến nhiều tuyến đường tại TP. HCM ngập nặng , trong đó khu vực quận Bình Thạnh bị ảnh hưởng nghiêm trọng .", [
        ([1, 2], [12, 13], 'NEG'),
        ([41, 42], [43, 44], 'NEG'),
        ([50, 51, 52], [53, 54, 55, 56, 57], 'NEG'),
    ]),

    # Rec 3030: Đã có TP HCM, Bình Thạnh, Thủ Đức
    ("📍 Nhiều nơi ở TP HCM ngập nặng sau cơn mưa lớn tối nay Trong ảnh là khu vực Bình Thạnh và Thủ Đức cũ .", [
        ([4, 5], [6, 7], 'NEG'),
        ([19, 20], [6, 7], 'NEG'),
        ([22, 23], [6, 7], 'NEG'),
    ]),

    # Rec 3031: Đã có TP HCM, quận Bình Thạnh, TP Thủ Đức
    ("Nước ngập sau mưa lớn ở TP HCM 🌧 ️ Nhiều tuyến đường , hẻm , nhà dân ở quận Bình Thạnh , TP Thủ Đức ngập ngang người , nước dâng cao lút bánh xe sau cơn mưa lớn kèm sấm chớp , chiều 8 / 10 .", [
        ([6, 7], [1], 'NEG'),
        ([19, 20, 21], [26, 27, 28], 'NEG'),
        ([23, 24, 25], [26, 27, 28], 'NEG'),
    ]),

    # Rec 3032: Đã có TPHCM, Bình Thạnh, Thủ Đức
    ("😥 Sau cơn mưa tối nay , nhiều nơi ở TPHCM là Bình Thạnh và Thủ Đức cũ ngập nặng .", [
        ([10], [18, 19], 'NEG'),
        ([12, 13], [18, 19], 'NEG'),
        ([15, 16], [18, 19], 'NEG'),
    ]),

    # Rec 3033: Đã có TP HCM, quận Bình Thạnh, TP Thủ Đức
    ("Nước ngập hết bánh xe , tràn vào nhà dân sau mưa lớn ở TP HCM 🌧 ️ Nhiều đường , hẻm , nhà dân ở quận Bình Thạnh , TP Thủ Đức ngập ngang người , nước dâng cao lút bánh xe sau cơn mưa lớn kèm sấm chớp , chiều 8 / 10 .", [
        ([14, 15], [1, 2, 3, 4], 'NEG'),
        ([26, 27, 28], [33, 34, 35], 'NEG'),
        ([30, 31, 32], [33, 34, 35], 'NEG'),
    ]),

    # Rec 3034: Đã có TP. HCM
    ("HCM 😢 Cơn mưa lớn kéo dài hơn hai giờ tối 8 / 10 khiến nhiều tuyến đường trung tâm TP. HCM ngập sâu , sóng đánh ngã người đi xe máy , giao thông hỗn loạn và ùn tắc kéo dài .", [
        ([18, 19], [20, 21], 'NEG'),
    ]),

    # Rec 3035: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Mưa lớn chiều 10 / 6 , có nơi ngập gần một mét .", [
        ([1], [12, 13, 14, 15], 'NEG'),
    ]),

    # Rec 3036: Không có nội dung rõ ràng / cắt cụt -> REJECT
    ("Tại TP. Hồ Chí Minh , ", []),

    # Rec 3037: Cắt cụt lỡ dở 'Tân Phú . . .' -> REJECT
    ("ĐƯỜNG TP. HCM NGẬP SAU MƯA LỚN 30 PHÚT , NGƯỜI DÂN RÙNG MÌNH LỘI NƯỚC THỐI ⛈ Chiều nay ( 7 / 5 ) , tại TP. HCM tiếp tục có mưa đầu mùa trên diện rộng như TP Thủ Đức , quận 12 , quận Gò Vấp , quận Tân Bình , Tân Phú . . .", []),

    # Rec 3038: Đã có TP. HCM
    ("\" Điệp khúc \" ngập do mưa và triều cường là nỗi ám ảnh của người dân tại TP. HCM .", [
        ([18, 19], [4], 'NEG'),
    ]),

    # Rec 3039: Xã luận than thở bỏ nghề bỏ nhà -> REJECT
    ("Tại TP. Hồ Chí Minh , Bỏ nghề , bỏ nhà là những gì người dân nghĩ đến khi liên tục chịu cảnh sống chung với ngập .", []),

    # Rec 3040: Danh sách danh mục hành chính -> REJECT
    ("🔴 Danh sách 23 tuyến đường bị ngập nước do triều cường ở TP. HCM : Sở Xây dựng TP. HCM vừa công bố danh sách 23 tuyến đường bị ngập nước do triều cường .", []),

    # Rec 3041: Giả định hễ triều cường -> REJECT
    ("Tức là , hễ triều cường vượt báo động , 23 tuyến đường này sẽ bị ngập .", []),

    # Rec 3042: Đã có đường Bùi Văn Ba, quận 7
    ("Triều cường khiến nhiều hẻm ở đường Bùi Văn Ba , quận 7 ngập nặng , ông Lê Vũ cho biết như bị \" giam lỏng \" khi nước bủa vây khắp nơi , không thể ra khỏi nhà .", [
        ([6, 7, 8, 9], [13, 14], 'NEG'),
        ([11, 12], [13, 14], 'NEG'),
    ]),

    # Rec 3043: Cắt cụt đuôi câu 'TP.' -> REJECT
    ("HỒ CHÍ MINH NGUY CƠ NGẬP NẶNG DO TRIỀU CƯỜNG VÀ MƯA LỚN Từ ngày 5 đến 7 / 11 , TP.", []),

    # Rec 3044: Cắt cụt đuôi câu 'hoàn lưu bão' -> REJECT
    ("Hồ Chí Minh được dự báo có thể ngập diện rộng khi đợt triều cường Rằm tháng 9 Âm lịch trùng thời điểm mưa lớn do dải hội tụ nhiệt đới và hoàn lưu bão", []),

    # Rec 3045: Đã có TP Thủ Đức
    ("Cơn mưa lớn kéo dài từ chiều đến tối khiến nhiều tuyến đường ở TP Thủ Đức ngập sâu , hàng loạt xe tắt máy , người dân đi lại khó khăn .", [
        ([14, 15, 16], [17, 18], 'NEG'),
        ([14, 15, 16], [23, 24], 'NEG'),
        ([14, 15, 16], [29, 30, 31], 'NEG'),
    ]),

    # Rec 3046: Đã có TP THỦ ĐỨC
    ("TP THỦ ĐỨC NGẬP NẶNG , NGƯỜI DÂN ‘ BƠI ’ TRONG BIỂN NƯỚC ĐỂ VỀ NHÀ 💥 💥 💥 💥 💥 💥 💥 💥 💥 💥 Khoảng 16h ngày 20 / 5 , nhiều khu vực ở TP. HCM bắt đầu hứng mưa lớn .", [
        ([0, 1, 2], [3, 4], 'NEG'),
    ]),

    # Rec 3047: Dính URL website -> REJECT
    ("Video : https : / / tuoitre . vn / video / giai - phap - nao - chong - ngap - dong - bo - cho - tp - thu - duc - 161577 . htm Hai trận mưa lớn ở khu vực TP Thủ Đức khiến nhiều tuyến đường xung quanh chợ Thủ Đức ngập nặng .", []),

    # Rec 3048: Đã có TP THỦ ĐỨC
    ("TP THỦ ĐỨC NGẬP NẶNG , NGƯỜI DÂN ‘ BƠI ’ TRONG BIỂN NƯỚC ĐỂ VỀ NHÀ Khoảng 16h ngày 20 / 5 , nhiều khu vực ở TP. HCM bắt đầu hứng mưa lớn .", [
        ([0, 1, 2], [3, 4], 'NEG'),
    ]),

    # Rec 3049: Đã có chợ Thủ Đức, TP. Thủ Đức
    ("Tại khu vực chợ Thủ Đức , TP. Thủ Đức , TP. HCM , người dân sống quanh khu vực đang gặp phải tình cảnh nhiều tuyến đường bị ngập sâu hơn trước khi trời mưa lớn .", [
        ([3, 4, 5], [29, 30], 'NEG'),
        ([7, 8, 9], [29, 30], 'NEG'),
    ]),

    # Rec 3050: Đã có đường Tô Ngọc Vân, chợ Thủ Đức
    ("Mưa lớn chiều 20 / 5 khiến đường Tô Ngọc Vân đoạn qua chợ Thủ Đức ngập sâu , nước chảy xiết làm nhiều xe bị chết máy .", [
        ([5, 6, 7, 8], [15, 16], 'NEG'),
        ([5, 6, 7, 8], [25, 26], 'NEG'),
        ([11, 12, 13], [15, 16], 'NEG'),
    ]),

    # Rec 3051: Cắt cụt đuôi 'người' + People role -> REJECT
    ("THỦ ĐỨC : XÚC ĐỘNG HÌNH ẢNH CHIẾN SĨ DÂN QUÂN DẦM MƯA GIÚP DÂN THOÁT NGẬP Chiều ngày 20 / 5 , cơn mưa lớn , ào ạt trút xuống khu vực chợ Thủ Đức , thành phố Thủ Đức , Thành phố Hồ Chí Minh khiến cho đường sá ngập lênh láng , người", []),

    # Rec 3052: Cắt cụt đuôi 'Tân Phú . . .' -> REJECT
    ("CƠN MƯA LỚN TRÚT XUỐNG TP. HCM KHIẾN NGƯỜI DÂN BÌ BÕM LỘI NƯỚC VỀ NHÀ 🌧 Chiều 31 / 5 , một trận mưa lớn trút xuống TPHCM khiến các địa bàn như TP Thủ Đức , quận Gò Vấp , quận Tân Bình , Tân Phú . . .", []),

    # Rec 3053: Đánh giá dự án 248 tỷ -> REJECT
    ("Dự án chống ngập 248 tỷ đồng ở đường Võ Văn Ngân , Thủ Đức chỉ giải quyết 50 - 60 % khả năng thoát nước , chưa đủ triệt để .", []),

    # Rec 3054: Đánh giá hiệu quả dự án -> REJECT
    ("Tại TP. Hồ Chí Minh , Mưa lớn vào ngày 15 / 5 khiến mặt đường bong tróc tại một số vị trí , tuy nhiên dự án giúp giảm thiểu ngập so với trước .", []),

    # Rec 3055: Đã có THỦ ĐỨC
    ("THỦ ĐỨC : “ THÀNH PHỐ KẸT XE VÀ NGẬP NƯỚC ” .", [
        ([0, 1], [8, 9], 'NEG'),
    ]),

    # Rec 3056: Đã có Thủ Đức, TP HCM
    ("Thủ Đức : Mưa lớn đường lại ngập , cống lại bung Cơn mưa trắng trời vào chiều 20 / 5 làm nhiều khu vực TP HCM bị ngập sâu , người dân như xé mưa để lưu thông trên đường .", [
        ([0, 1], [6], 'NEG'),
        ([22, 23], [25, 26], 'NEG'),
    ]),

    # Rec 3057: Cắt cụt đuôi câu -> REJECT
    ("Tại khu vực chợ Thủ Đức , TP Thủ Đức lại tái diễn tình trạng đường ngập lênh láng ,", []),

    # Rec 3058: Đã có TPHCM, Bình Tân, Tân Phú, Bình Chánh
    ("TPHCM mưa như trút gây ngập nặng , xe ch : ết máy hàng loạt ⛈ 🥹 Đầu giờ chiều 20 / 6 , mưa lớn trút xuống các quận , huyện phía tây TPHCM như Bình Tân , Tân Phú , Bình Chánh khiến nhiều tuyến đường bị ngập cục bộ .", [
        ([0], [5, 6], 'NEG'),
        ([34], [48, 49, 50], 'NEG'),
        ([36, 37], [48, 49, 50], 'NEG'),
        ([39, 40], [48, 49, 50], 'NEG'),
        ([42, 43], [48, 49, 50], 'NEG'),
    ]),

    # Rec 3059: Đã có bờ Thủ Thiêm, đầu hầm Sông Sài Gòn
    ("Nước lên ngập bờ Thủ Thiêm , đầu hầm Sông Sài Gòn .", [
        ([3, 4, 5], [2], 'NEG'),
        ([7, 8, 9, 10, 11], [2], 'NEG'),
    ]),

    # Rec 3060: Cắt cụt đuôi 'ngập c' -> REJECT
    ("Tại TP. Hồ Chí Minh , 💧 Nhưng điều đáng lo là , tình trạng ngập c", []),

    # Rec 3061: Dự báo tương lai -> NEU (Pass 8)
    ("TP HCM và nhiều tỉnh thành Nam Bộ nguy cơ sẽ xảy ra ngập úng trên diện rộng trong ngày hôm nay ( 19 / 10 ) , do dự báo hôm nay là đỉnh của đợt triều cường lần này kết hợp với mưa lớn diện rộng .", [
        ([0, 1], [8, 9, 10, 11, 12, 13], 'NEU'),
    ]),

    # Rec 3062: Câu hỏi lịch sử -> REJECT
    ("SÀI GÒN TRƯỚC KHI CÓ NGẬP LỤT NHƯ TP HỒ CHÍ MINH ?", []),

    # Rec 3063: Đã có Nguyễn Thị Thập, Q7
    ("Nguyễn Thị Thập ( Q7 cũ ) ngập quá nên bà con đi đường phải tấp lên lề đợi cho nước rút bớt , có xe còn tắt máy phải dẫn bộ trong mưa .", [
        ([0, 1, 2], [7, 8], 'NEG'),
        ([0, 1, 2], [27, 28], 'NEG'),
        ([0, 1, 2], [30, 31], 'NEG'),
        ([4], [7, 8], 'NEG'),
    ]),

    # Rec 3064: Tranh luận phát ngôn chính trị -> REJECT
    ("PHÁT NGÔN GÂY SỐC VÀ XÚC PHẠM HÀNG TRIỆU NGƯỜI DÂN SÀI GÒN Phát ngôn của Phó Chủ tịch UBND TP. HCM Võ Văn Hoan rằng : \" Ngập là một đặc điểm rất tự nhiên của thành phố .", []),

    # Rec 3065: Cắt cụt đuôi câu -> REJECT
    ("Tại TP. Hồ Chí Minh , Ngập thành phố phần nào là một hình ảnh rất đẹp \" không chỉ gây", []),

    # Rec 3066: Câu hỏi tiêu đề -> REJECT
    ("Bao giờ TP. HCM hết ngập ?", []),

    # Rec 3067: Danh sách công bố danh mục -> REJECT
    ("‼ TP. HCM vừa công bố danh sách 23 tuyến đường bị ngập nước do triều cường .", []),

    # Rec 3068: Kịch bản giả định -> REJECT
    ("Tức là , hễ triều cường vượt báo động , 23 tuyến đường này sẽ bị ngập ‼ Theo Báo Thanh Niên", []),

    # Rec 3069: Đã có phường Tam Bình, TP Thủ Đức
    ("🔴 Sau một đêm mưa lớn , khu dân cư tại phường Tam Bình ( TP Thủ Đức cũ ) vẫn ngập sâu .", [
        ([11, 12, 13], [21, 22], 'NEG'),
        ([15, 16, 17], [21, 22], 'NEG'),
    ]),

    # Rec 3070: Đã có TP. HCM
    ("Mỗi mùa mưa đến , người dân TP. HCM lại đối mặt với nỗi ám ảnh “ ngập nước ” , khi ấy phố xá hóa sông , giao thông t : ê l : iệt , sinh hoạt người dân đảo lộn .", [
        ([7, 8], [17, 18], 'NEG'),
        ([7, 8], [22, 23, 24, 25], 'NEG'),
    ]),

    # Rec 3071: Đã có thành phố Thủ Đức, TP. HCM
    ("Chỉ mới những cơn mưa đầu mùa , nhưng nhiều nơi ở thành phố Thủ Đức , TP. HCM đã xảy ra 2 đợt ngập sâu , làm thiệt hại nhiều tài sản , ảnh hưởng lớn đến hoạt động sản xuất và đời sống của người dân .", [
        ([12, 13, 14, 15], [24, 25], 'NEG'),
        ([17, 18], [24, 25], 'NEG'),
    ]),

    # Rec 3072: Cắt cụt đuôi câu 'chậ' -> REJECT
    ("Tại TP. Hồ Chí Minh , Để hạn chế tình trạng ngập nước nhanh nhưng chậ", []),

    # Rec 3073: Cắt cụt đuôi câu 'dữ d' -> REJECT
    ("Do e thi tiếng anh nên em ra tầm 4 giờ mà em đi đường khúc bên nguyễn bình đoạn qua cầu cây khô trở đi là ngập dữ d", []),

    # Rec 3074: Đã có đường Nguyễn Bình, Xã Hiệp Phước, Nhà Bè
    ("Triều cường nước lên ngập đường Nguyễn Bình , Xã Hiệp Phước , Nhà Bè .", [
        ([5, 6, 7], [4], 'NEG'),
        ([9, 10, 11], [4], 'NEG'),
        ([13, 14], [4], 'NEG'),
    ]),

    # Rec 3075: Đã có TP HCM
    ("XE CHẾT MÁY LA LIỆT TRONG NGÀY TRIỀU CƯỜNG DÂNG CAO Ở TP HCM Theo Đài khí tượng thuỷ văn khu vực Nam Bộ , TP HCM đang có đợt triều cường cao nhất từ đầu năm .", [
        ([12, 13], [0, 1, 2, 3, 4], 'NEG'),
        ([25, 26], [30, 31, 32, 33], 'NEG'),
    ]),

    # Rec 3076: Đã có Thủ Đức
    ("Thủ Đức lại phải hứng chịu cảnh ngập lụt nặng nề sau cơn mưa đầu mùa , dù hệ thống thoát nước 250 tỷ đồng mới được đưa vào hoạt động cách đây không lâu .", [
        ([0, 1], [6, 7, 8, 9], 'NEG'),
    ]),

    # Rec 3077: Hoạt động cứu nạn của lực lượng chức năng -> REJECT
    ("🛑 LỰC LƯỢNG CHỨC NĂNG XUYÊN TRƯA GIÚP DÂN TẠI ĐIỂM NGẬP Ở TP. HCM ✅ Ngày 6 / 8 , sau trận mưa lớn đêm qua , nhiều khu vực thuộc TP Thủ Đức cũ ( TP. HCM ) vẫn ngập trong nước .", []),

    # Rec 3078: Xã luận vấn nạn kéo dài -> REJECT
    ("Vấn nạn ngập lụt tại Thủ Đức đã trở thành nỗi ám ảnh kéo dài nhiều năm qua đối với người dân nơi đây .", []),

    # Rec 3079: Cắt cụt đuôi câu 'song hiệu q' -> REJECT
    ("Dù đã có những dự án chống ngập được triển khai với kinh phí lớn , song hiệu q", []),

    # Rec 3080: Văn bản chỉ đạo hành chính của lãnh đạo -> REJECT
    ("TP. HCM chỉ đạo khẩn trương giải quyết điểm ngập khu vực chợ Thủ Đức , Thảo Điền , Lê Văn Việt , Nguyễn Duy Trinh . . .", []),

    # Rec 3081: Cắt cụt đầu câu -> REJECT
    ("Tam Bình , Thủ Đức ) ngập nặng .", []),

    # Rec 3082: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Có nhà chia sẻ : \" Mưa xuống là không dám ngủ , nửa đêm phải bật dậy vì nước tràn vào nhà . \"", [
        ([1], [22, 23, 24, 25], 'NEG'),
    ]),

    # Rec 3083: Đã có Đường Đặng Thùy Trâm, Bình Thạnh
    ("Đường Đặng Thùy Trâm của người anh em hàng xóm Bình Thạnh sáng nay , triều cường ngập cao , nỗi khổ của các sinh viên đại học Văn Lang 🥲 🎥 : Thành Công", [
        ([0, 1, 2, 3], [16, 17], 'NEG'),
        ([10, 11], [16, 17], 'NEG'),
    ]),

    # Rec 3084: Đã có Thanh Đa, bán đảo Thanh Đa, Q. Bình Thạnh
    ("TP. HCM : Triều cường dâng cao , khu Thanh Đa có nơi ngập hơn 1 mét Chiều tối 24 . 10 , triều cường dâng cao khiến khu vực bán đảo Thanh Đa ( Q. Bình Thạnh , TP. HCM ) ngập nặng .", [
        ([9, 10], [13, 14, 15, 16], 'NEG'),
        ([30, 31, 32, 33], [42, 43], 'NEG'),
        ([35, 36, 37], [42, 43], 'NEG'),
    ]),

    # Rec 3085: Đã có Nguyễn Văn Khối, Phạm Văn Chiêu, Lê Đức Thọ, Lê Văn Thọ, Gò Vấp
    ("Bốn tuyến đường Nguyễn Văn Khối , Phạm Văn Chiêu , Lê Đức Thọ và Lê Văn Thọ ở Gò Vấp cũ ( TP. HCM ) , được ví là “ tứ giác ngập ” , tiếp tục chìm trong nước khi mưa .", [
        ([3, 4, 5], [36, 37, 38], 'NEG'),
        ([7, 8, 9], [36, 37, 38], 'NEG'),
        ([11, 12, 13], [36, 37, 38], 'NEG'),
        ([15, 16, 17], [36, 37, 38], 'NEG'),
        ([19, 20], [36, 37, 38], 'NEG'),
    ]),

    # Rec 3086: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Tình trạng ngập đã tồn tại từ lâu , nay phức tạp hơn , gây khó khăn cho giao thông , sinh hoạt .", [
        ([1], [4, 5], 'NEG'),
    ]),

    # Rec 3087: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , ngập nửa bánh xe , người dân vất vả đi lại , chiều 7 / 5 .", [
        ([1], [3, 4, 5, 6], 'NEG'),
        ([1], [10, 11, 12, 13], 'NEG'),
    ]),

    # Rec 3088: Phát ngôn họp báo quy hoạch tương lai -> REJECT
    ("Theo đại diện Sở Xây dựng TPHCM , hệ thống thoát nước của địa phương đang quá tải , tình trạng ngập nước có thể tiếp tục diễn ra khi xuất hiện mưa lớn trong thời gian tới .", []),

    # Rec 3089: Đã có TPHCM
    ("XE MÁY NỔI LỀNH BỀNH , ĐƯỜNG BIẾN THÀNH \" SÔNG \" TRONG CƠN MƯA LỚN Ở TPHCM Sáng 10 / 5 , cơn mưa lớn kéo dài khiến nhiều tuyến đường ở TPHCM biến thành \" sông \" , xe máy bị sóng nước đánh ngã , nổi lềnh bềnh trên đường ngập .", [
        ([17], [2, 3, 4], 'NEG'),
        ([33], [48, 49, 50], 'NEG'),
    ]),

    # Rec 3090: Đã có TPHCM
    ("Mất chỗ ngủ , đi ủng cả ngày trong nhà vì triều cường ở TPHCM Do ảnh hưởng của triều cường , nước ngập sâu cả ngày lẫn đêm , cuộc sống người dân trong nhiều hẻm sâu ở TPHCM bị đảo lộn .", [
        ([14], [23, 24], 'NEG'),
        ([39], [41, 42], 'NEG'),
    ]),

    # Rec 3091: Than thở meme admin bị ghẻ -> REJECT
    ("Tại TP. Hồ Chí Minh , P / s : Ad lội nước về dễ bị ghẻ quá , huhu .", []),

    # Rec 3092: Hỏi đường -> REJECT
    ("Anh em cho hỏi Đường đi từ Lotte Quận 7 đến KDC Đào Sư Tích , Phước Kiêng có Đoạn nào bị ngập không ?", []),

    # Rec 3093: Hỏi tư vấn xe ô tô -> REJECT
    ("Tại TP. Hồ Chí Minh , Và khi ngập thì Ô tô 7 chỗ đi qua đoạn này có ảnh hưởng gì không nhỉ ?", []),

    # Rec 3094: Danh sách điểm ngập thống kê -> REJECT
    ("Những \" điểm ngập \" trên địa bàn TP. HCM bạn nên biết khi MÙA MƯA TỚI : ( Theo thống kê , TP. HCM có 66 điểm ngập được thống kê , nhưng chỉ là các điểm ngoài đường phố , còn các điểm ngập trong con hẻm và khu dân cư vẫn chưa được liệt kê .", []),

    # Rec 3095: Đã có TP. HCM
    ("Người dân TP. HCM \" không kịp trở tay \" trong trận mưa lớn nhất kể từ đầu năm : Nước ngập gần lút bánh xe , tràn cả vào nhà 😢 Chiều 15 / 5 , trận mưa lớn nhất từ đầu năm đến nay ở TP. HCM đã khiến nhiều tuyến đường , nhà dân bị ngập nặng .", [
        ([2, 3], [21, 22, 23, 24, 25], 'NEG'),
        ([47, 48], [58, 59], 'NEG'),
    ]),

    # Rec 3096: Nhầm lẫn từ ngữ (tên người Ngập trong truyện dịch) -> REJECT
    ("Tại TP. Hồ Chí Minh , Điều ấy khiến Ngập vô cùng thán phục , và trọng dụng", []),

    # Rec 3097: Đã có TP. HCM
    ("Người dân chật vật di chuyển qua đường ngập , việc buôn bán ế ẩm sau khi nhiều tuyến đường bỗng chốc mênh mông trong ' biển nước ' sau cơn mưa lớn chiều nay ở TP. HCM .", [
        ([36, 37], [2, 3, 4, 5], 'NEG'),
        ([36, 37], [10, 11], 'NEG'),
    ]),

    # Rec 3098: Chỉ toàn hashtag và link báo -> REJECT
    ("# doisong # mưa # ngập # TPHCM https : / / thanhnien . vn / tphcm - mua - trang - troi - duong", []),

    # Rec 3099: Cắt cụt đầu câu 'HCM rơi vào...' -> REJECT
    ("Tại TP. Hồ Chí Minh , HCM rơi vào tình trạng ngập * Ảnh chụp tại quận Bình Thạnh 📸 : VTV24", []),

    # Rec 3100: Đã có TP. HCM
    ("Nhiều tuyến đường tại TP. HCM bị ngập nặng sau cơn mưa kéo dài 5 tiếng .", [
        ([4, 5], [7, 8], 'NEG'),
    ]),
]

def test_triplets():
    flaws = 0
    print(f'Kiểm tra {len(batch31_data)} records...')
    for idx, (text, triplets) in enumerate(batch31_data, 3001):
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
        print('TẤT CẢ CÁC TRIPLETS CỦA BATCH 31 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!')
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
        
        # Chỉ giữ lại đúng 3000 records đầu nếu đã có
        base_lines = lines[:3000]
        
        # Format batch 31
        new_batch_lines = []
        for text, triplets in batch31_data:
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
