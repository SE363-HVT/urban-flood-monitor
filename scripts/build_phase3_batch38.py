# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn chuẩn hóa cho Phase 3 - Batch 38 (Records 3701 - 3800).
Tuân thủ 100% tài liệu BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md.
"""

batch38_data = [
    # Rec 3701: Tản mạn cá nhân nâng nền -> REJECT
    ("Bà Tư ( SN 1961 ) chia sẻ trong sự ngao ngán : \" Tôi đã nâng nền nhà thêm nửa mét nhưng nước vẫn tràn vào .", []),

    # Rec 3702: Quyết định chủ trương đầu tư dự án -> REJECT
    ("Sáng 27 - 9 , kỳ họp thứ 18 , HĐND TP. HCM khóa X đã thông qua quyết định chủ trương đầu tư dự án nâng cấp , cải tạo chống ngập đường Trần Xuân Soạn ( từ đường Huỳnh Tấn Phát đến cầu Rạch Ông , quận 7 ) với 245 tỉ đồng từ ngân sách TP.", []),

    # Rec 3703: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Đồng thời kéo theo đó các con đường nhánh cũng bị ngập .", [
        ([1], [14], 'NEG'),
    ]),

    # Rec 3704: Đã có đường Quốc Hương (cắt 'trên')
    ("Đoạn ngập trên đường Quốc Hương này kéo dài khoảng 300 m , từ giao lộ Quốc Hương – Xuân Thủy đến đường Thái Lý .", [
        ([3, 4, 5], [1], 'NEG'),
    ]),

    # Rec 3705: Phê duyệt chủ trương đầu tư -> REJECT
    ("Sáng 27 . 9 , tại kỳ họp chuyên đề , HĐND TP. HCM đã phê duyệt chủ trương đầu tư dự án nâng cấp và cải tạo chống ngập cho đường Trần Xuân Soạn ( đoạn từ đường Huỳnh Tấn Phát đến cầu Rạch Ông ) tại Q. 7 .", []),

    # Rec 3706: Đã có tuyến Trần Xuân Soạn (cắt 'tại')
    ("Khoảng 17 giờ , tại tuyến Trần Xuân Soạn ( phường Tân Thuận , TP. HCM ) nước từ kênh Tẻ theo miệng cống tràn vào đường .", [
        ([5, 6, 7, 8], [24, 25], 'NEG'),
    ]),

    # Rec 3707: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Ghi nhận nước ngập sâu , có đoạn ngập hơn nửa xe máy , nước chảy như thác đổ khiến nhiều người dắt xe máy loạn choạng suýt té ngã .", [
        ([1], [6, 7], 'NEG'),
        ([1], [11, 12, 13, 14, 15], 'NEG'),
    ]),

    # Rec 3708: Đã có đường Tô Ngọc Vân
    ("Sau cơn mưa lớn , nước từ 1 con kênh bắc qua đường Tô Ngọc Vân dâng cao và tuôn trào ra đường khiến khu vực bị ngập sâu .", [
        ([12, 13, 14, 15], [16, 17], 'NEG'),
        ([12, 13, 14, 15], [27, 28], 'NEG'),
    ]),

    # Rec 3709: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Đây cũng là lần ngập nhiều lần sau mưa ở con đường này .", [
        ([1], [7], 'NEG'),
    ]),

    # Rec 3710: Đã có đường Quốc Hương (cắt 'ở')
    ("Đoạn ngập ở đường Quốc Hương này kéo dài khoảng 300 m , từ giao lộ Quốc Hương – Xuân Thủy đến đường Thái Lý .", [
        ([3, 4, 5], [1], 'NEG'),
    ]),

    # Rec 3711: Tin tức tương lai kết thúc bằng hai chấm -> REJECT
    ("Khi biết thông tin , nhiều người dân phấn khởi vì tới đây sẽ không còn cảnh lội nước mỗi khi triều cường dân cao :", []),

    # Rec 3712: Câu trích dẫn cụt -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Chưa nâng lên thì nước đã ngập rồi .", []),

    # Rec 3713: Bàn luận chuyên gia -> REJECT
    ("Tại TP. Hồ Chí Minh , Thế nhưng theo PGS . TS Phùng Chí Sỹ - Phó Chủ tịch Hội Thiên nhiên và Bảo vệ Môi trường Việt Nam cho rằng việc nâng đường chống ngập chỉ là giải pháp tạm thời .", []),

    # Rec 3714: Tin tức dự án trễ hẹn -> REJECT
    ("trong khi đó đại dự án chống ngập do triều ở TP HCM tổng đầu tư 10 . 000 tỷ đồng đã trễ hẹn 6 năm qua vẫn chưa biết ngày hoàn thành .", []),

    # Rec 3715: Trích dẫn phê phán dự án -> REJECT
    ("\" Giờ bỏ tiền ra nâng đường mà trong khi đó công trình chống ngập thì nằm trơ trơ ra , không biết khi nào mới hoàn thành \" .", []),

    # Rec 3716: Trích dẫn phê phán dự án -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Cống này làm xong lâu rồi mà giờ chưa thấy hoạt động gì hết , nằm ì đó hoài , trong khi đường xá , nhà cửa thì ngập lênh láng .", []),

    # Rec 3717: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Người dân di chuyên khó khăn , xe chết máy suốt , phải dắt bộ , buôn bán phải đóng cửa .", [
        ([1], [11, 12], 'NEG'),
        ([1], [16, 17], 'NEG'),
    ]),

    # Rec 3718: Trích dẫn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Nước lên như này khổ sở lắm .", []),

    # Rec 3719: Đã có đường Trần Xuân Soạn (cắt 'trên')
    ("Một số hình ảnh ngập nước do triều cường trên đường Trần Xuân Soạn , quận 7 ( TP HCM ) :", [
        ([10, 11, 12, 13], [4], 'NEG'),
    ]),

    # Rec 3720: Đã có đường Trần Xuân Soạn
    ("Chiều 27 . 9 , TP. HCM bất ngờ đổ cơn mưa lớn , kết hợp triều cường làm cho tuyến đường Trần Xuân Soạn ( đoạn thuộc P. Tân Thuận Tây , Q. 7 , TP. HCM ) dọc theo sông Sài Gòn ngập sâu .", [
        ([21, 22, 23, 24], [44, 45], 'NEG'),
    ]),

    # Rec 3721: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Cũng tại đoạn này , phương tiện chen nhau dưới trời mưa , ngập nước .", [
        ([1], [16, 17], 'NEG'),
    ]),

    # Rec 3722: Câu cụt mất chủ ngữ -> REJECT
    ("Tại TP. Hồ Chí Minh , đều bị ngập sâu sau mưa lớn .", []),

    # Rec 3723: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhiều xe chết máy , nhiều người tay lái không vững phải xuống lội nước dắt xe qua đoạn ngập .", [
        ([1], [5, 6], 'NEG'),
        ([1], [16, 17], 'NEG'),
        ([1], [22], 'NEG'),
    ]),

    # Rec 3724: Trích dẫn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , “ Bình thường tay lái tôi cũng vững , nên nước ngập vậy cũng chạy qua được .", []),

    # Rec 3725: Tản mạn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , Tôi đi làm qua đoạn này suốt , biết hôm nay triều cao nên cũng không mang giày mà mang dép , chứ mang giày chắc bỏ đôi giày luôn ” , nhìn con đường mênh mông nước , anh ngao ngán .", []),

    # Rec 3726: Đã có TP HCM -> Cắt bỏ tiền tố nhân tạo
    ("CLIP : TP HCM ngập nước khắp nơi , xe chết máy hàng loạt - Tuổi Trẻ", [
        ([2, 3], [4, 5], 'NEG'),
        ([2, 3], [10, 11], 'NEG'),
    ]),

    # Rec 3727: Đã có TP HCM -> Cắt bỏ tiền tố nhân tạo
    ("TP HCM : Mưa như trút nước , đường ngập sâu , xe chết máy la liệt - Tuổi Trẻ", [
        ([0, 1], [8, 9], 'NEG'),
        ([0, 1], [12, 13, 14, 15], 'NEG'),
    ]),

    # Rec 3728: Đã có TP HCM -> Cắt bỏ tiền tố nhân tạo
    ("Bì bõm trên nhiều tuyến đường trung tâm TP HCM tối cuối tuần , xe chết máy , nước tràn vào quán - Báo Tuổi Trẻ", [
        ([7, 8], [0, 1], 'NEG'),
        ([7, 8], [14, 15], 'NEG'),
        ([7, 8], [18, 19], 'NEG'),
    ]),

    # Rec 3729: Đã có Đường Trần Xuân Soạn
    ("Đường Trần Xuân Soạn thành sông , loạt xe chết máy , nhiều người chỉ biết chịu trận - Tuổi Trẻ", [
        ([0, 1, 2, 3], [4, 5], 'NEG'),
        ([0, 1, 2, 3], [9, 10], 'NEG'),
    ]),

    # Rec 3730: Đã có TP HCM -> Cắt bỏ tiền tố nhân tạo
    ("Mưa lớn bất ngờ đổ xuống TP HCM , nhiều tuyến đường đang ngập sâu , xe chết máy - Báo Tuổi Trẻ", [
        ([6, 7], [13, 14], 'NEG'),
        ([6, 7], [17, 18], 'NEG'),
    ]),

    # Rec 3731: Đã có TP HCM -> Cắt bỏ tiền tố nhân tạo
    ("Vạn người khốn khổ trong kẹt xe , ngập nước ở TP HCM - Tuổi Trẻ", [
        ([11, 12], [8, 9], 'NEG'),
    ]),

    # Rec 3732: Đã có TP HCM -> Cắt bỏ tiền tố nhân tạo
    ("TP HCM : Mưa lớn kéo dài trong đêm , ngập nặng , xe cộ “ chết đứng ” - Tuổi Trẻ", [
        ([0, 1], [10, 11], 'NEG'),
    ]),

    # Rec 3733: Đã có triều cường, TP HCM
    ("Triều cường dâng cao , nhiều tuyến đường TP HCM ngập sâu - Báo Tuổi Trẻ", [
        ([0, 1], [2, 3], 'NEG'),
        ([8, 9], [10, 11], 'NEG'),
    ]),

    # Rec 3734: Đã có TPHCM
    ("TPHCM : Mưa lớn , người dân bì bõm trong biển nước - Tuổi Trẻ", [
        ([0], [10, 11], 'NEG'),
    ]),

    # Rec 3735: Đã có Đường Hồ Học Lãm
    ("TPHCM : Đường Hồ Học Lãm ngập sâu sau mưa lớn - Tuổi Trẻ", [
        ([2, 3, 4, 5], [6, 7], 'NEG'),
    ]),

    # Rec 3736: Đã có TP. HCM, triều cường
    ("Cảnh khu nam TP. HCM ngập sâu , triều cường vượt lịch sử nhìn từ trên cao - Thanh Niên", [
        ([3, 4], [5, 6], 'NEG'),
        ([8, 9], [10, 11, 12], 'NEG'),
    ]),

    # Rec 3737: Đã có đường Lê Văn Lương
    ("TP. HCM mưa lớn giữa trưa 1 . 11 , đường Lê Văn Lương ngập sâu - Báo Thanh Niên", [
        ([10, 11, 12, 13], [14, 15], 'NEG'),
    ]),

    # Rec 3738: Đã có TP. HCM
    ("Đường ở trung tâm TP. HCM ngập sâu trong cơn mưa giông cực lớn - Báo Thanh Niên", [
        ([4, 5], [6, 7], 'NEG'),
    ]),

    # Rec 3739: Tiêu đề chất vấn dự án -> REJECT
    ("Dự án chống ngập 10 . 000 tỉ đồng ở TPHCM – chờ đến bao giờ ?", []),

    # Rec 3740: Tiêu đề chậm triển khai dự án -> REJECT
    ("Mùa mưa đến sớm , các dự án chống ngập tại TPHCM vẫn chậm triển khai - Tuổi Trẻ", []),

    # Rec 3741: Tiêu đề thi công dự án -> REJECT
    ("Gấp rút thi công dự án chống ngập tại TPHCM - Báo Tuổi Trẻ", []),

    # Rec 3742: Tiêu đề quỹ đất thanh toán dự án -> REJECT
    ("Tin nóng hôm nay : TPHCM được dùng quỹ đất thanh toán dự án chống ngập 10 . 000 tỉ đồng | Bổ sung gần 34 . 000 tỉ đồng cho dự toán đầu tư công 2025 - Tuổi Trẻ", []),

    # Rec 3743: Tiêu đề siêu dự án tiêu điều -> REJECT
    ("Cảnh tiêu điều tại siêu dự án chống ngập 10 . 000 tỷ đồng ở TPHCM - Tuổi Trẻ", []),

    # Rec 3744: Tiêu đề chất vấn dự án -> REJECT
    ("Vì sao dự án chống ngập 10 . 000 tỉ đồng ở TP. HCM vẫn ' đứng bánh ' ?", []),

    # Rec 3745: Tiêu đề chất vấn dự án -> REJECT
    ("Vì sao dự án chống ngập 10 . 000 tỉ đồng ở TP. HCM chưa hoạt động ?", []),

    # Rec 3746: Chỉ đạo xử lý dự án -> REJECT
    ("Tổng Bí thư Tô Lâm yêu cầu xử lý dứt điểm dự án chống ngập 10 . 000 tỉ của TP. HCM - Báo Thanh Niên", []),

    # Rec 3747: Bài phóng sự dự án nghìn tỉ -> REJECT
    ("Ngập ở TP. HCM - Kỳ 2 : Những dự án chống ngập nghìn tỉ và câu hỏi bỏ ngỏ - Báo Thanh Niên", []),

    # Rec 3748: Tin tức gỡ vướng dự án -> REJECT
    ("TP. HCM lại ' cầu cứu ' Chính phủ gỡ vướng dự án chống ngập 10 . 000 tỉ - Thanh Niên", []),

    # Rec 3749: Tin chốt thời điểm dự án -> REJECT
    ("TP. HCM chốt thời điểm hoàn thành dự án chống ngập 10 . 000 tỉ đồng - Thanh Niên", []),

    # Rec 3750: Chỉ đạo đôn đốc dự án -> REJECT
    ("Chính phủ lại thúc TP. HCM khẩn trương giải quyết dứt điểm dự án chống ngập 10 . 000 tỉ - Báo Thanh Niên", []),

    # Rec 3751: Đã có TP. HCM
    ("Nhiều tuyến đường tại TP. HCM ngập sau cơn mưa lớn - VTV . vn", [
        ([4, 5], [6], 'NEG'),
    ]),

    # Rec 3752: Diên Khánh (Khánh Hòa - Tỉnh ngoài) -> REJECT
    ("Tại TP. Hồ Chí Minh , Chị mối bình thường mình hay lấy rau nhà trên Diên Khánh bị ngập ko bỏ rau được .", []),

    # Rec 3753: Hashtag meme -> REJECT
    ("Tại TP. Hồ Chí Minh , Bao ngập tắt máy xe nha 😂 😂 😂 # mua # ngap # saigon", []),

    # Rec 3754: Hashtag meme -> REJECT
    ("mỗi lần ngập vì triều cường 😢 🫣 😢 # quận7 # Ngập # saigon # cuocsongmuusinh", []),

    # Rec 3755: Đã có thành phố Thủ Đức
    ("Hồ Chí Minh xảy ra mưa lớn kèm sấm chớp liên tục khiến nhiều tuyến đường tại các quận , huyện và thành phố Thủ Đức ngập nước , tắc đường , người dân vất vả di chuyển .", [
        ([22, 23, 24, 25], [26, 27], 'NEG'),
        ([22, 23, 24, 25], [29, 30], 'NEG'),
    ]),

    # Rec 3756: Đã có TPHCM
    ("Cơn mưa lớn , kéo dài chiều 15 / 5 khiến nhiều tuyến đường ở TPHCM biến thành sông , hàng loạt xe chết máy , người dân ngã nhào trên đường ngập .", [
        ([15], [16, 17, 18], 'NEG'),
        ([15], [23, 24], 'NEG'),
        ([15], [32], 'NEG'),
    ]),

    # Rec 3757: Hashtag tiktok -> REJECT
    ("Tại TP. Hồ Chí Minh , # tiktoklive # livehighlights nước ngập nhà", []),

    # Rec 3758: Trò chuyện cảm thán -> REJECT
    ("Tại TP. Hồ Chí Minh , đền cô ngập rồi các cậu ơi . . .", []),

    # Rec 3759: Câu cụt kết thúc bằng 'tại TP.' -> REJECT
    ("Tại TP. Hồ Chí Minh , Sáng nay xem live cập nhật thông tin nước ngập cao tại TP.", []),

    # Rec 3760: Trò chuyện cảm thán emoji -> REJECT
    ("Tại TP. Hồ Chí Minh , Bà nào ở quận 7 mới thấu hiểu nỗi lòng tui 🥹 🥹 tui lội nước bữa giờ 🥲 🥲", []),

    # Rec 3761: Đã có TPHCM
    ("Tối 5 / 8 , một trận mưa lớn kéo dài hơn 2 tiếng đồng hồ đã biến nhiều tuyến đường tại TPHCM thành sông , gây khó khăn nghiêm trọng cho người dân trong giờ tan tầm .", [
        ([22], [23, 24], 'NEG'),
        ([22], [27, 28], 'NEG'),
    ]),

    # Rec 3762: Đã có phường Thủ Đức (cắt 'tại')
    ("Đặc biệt , tại phường Thủ Đức , tình hình ngập lụt trở nên nghiêm trọng hơn bao giờ hết .", [
        ([4, 5, 6], [10, 11], 'NEG'),
        ([4, 5, 6], [14, 15], 'NEG'),
    ]),

    # Rec 3763: Đã có đường Dương Văn Cam
    ("Theo ghi nhận của phóng viên Dân trí , đường Dương Văn Cam ( phường Thủ Đức ) ngập sâu hơn 1m , khiến giao thông hoàn toàn tê liệt .", [
        ([9, 10, 11, 12], [18, 19], 'NEG'),
        ([9, 10, 11, 12], [28, 29], 'NEG'),
    ]),

    # Rec 3764: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Hàng loạt xe máy nằm ngổn ngang trên vỉa hè , nhiều ô tô chết máy giữa dòng nước , gây ách tắc nghiêm trọng .", [
        ([1], [17, 18], 'NEG'),
        ([1], [23, 24], 'NEG'),
    ]),

    # Rec 3765: Đã có đường Dương Văn Cam
    ("Để đối phó với tình trạng ngập lụt thường xuyên , một số gia đình trên đường Dương Văn Cam đã tự chế máy bơm nước , tìm cách \" sống chung \" với mưa ngập .", [
        ([16, 17, 18, 19], [6, 7], 'NEG'),
        ([16, 17, 18, 19], [34, 35], 'NEG'),
    ]),

    # Rec 3766: Đã có đường Mã Lò
    ("Buổi chiều mưa nặng hạt , và đoàn xe chết máy trên đường Mã Lò - Bình Tân - TP. HCM", [
        ([12, 13, 14], [9, 10], 'NEG'),
    ]),

    # Rec 3767: Phương tiện ngập chung chung -> REJECT
    ("Tại TP. Hồ Chí Minh , Xe ngập thật sự rất nặng và kinh khủng", []),

    # Rec 3768: Tân Kỳ (Nghệ An - Tỉnh ngoài) -> REJECT
    ("Tại TP. Hồ Chí Minh , Ngày thứ 2 ở Tân Kỳ , chúng tôi thấy cảnh bà con dắt xe mà thương đứt ruột .", []),

    # Rec 3769: Kỹ thuật xe hỏng máy phanh -> REJECT
    ("Tại TP. Hồ Chí Minh , Xe ngập sâu , nước tràn cả vào máy – nhớt đục như nước gạo , má phanh ướt nhẹp , dây điện chập hết .", []),

    # Rec 3770: Đã có Thủ Đức
    ("Thủ Đức ngập sau cơn mưa chiều 13 / 10 .", [
        ([0, 1], [2], 'NEG'),
    ]),

    # Rec 3771: Meme mạng xã hội -> REJECT
    ("“ Thành phố biển ” Thủ Đức xin kính chào quý khách 🥺 Hiện tại em cần xuồng hay thuyền để bơi dìa chứ nước giữa đường chảy xiết , ngập tới yên xe em khum lội được nữa rồi 🥲 # mua # muangapduong # thuduc # nuocngap # xuhuong # trending # viral", []),

    # Rec 3772: Đã có triều cường, đường Nguyễn Văn Cung
    ("TPHCM - Chiều tối 16 . 11 , triều cường dâng cao khiến nhiều hộ dân đường Nguyễn Văn Cung ( Quận 8 ) phải dựng vách ngăn , đắp bao cát để chống ngập .", [
        ([8, 9], [10, 11], 'NEG'),
        ([16, 17, 18, 19], [33, 34], 'NEG'),
    ]),

    # Rec 3773: PR xe hơi hashtag TikTok -> REJECT
    ("Về TP HCM chẳng lo ngập nước Nguyễn Hữu Cảnh 😂 # oto # yêuxe # mebonbanh # sieuxe # mêxe # g63 # tank300 # chinacar # noidiatrung # xehay", []),

    # Rec 3774: Tư vấn bất động sản -> REJECT
    ("Nhiều người đi mua nhà rất quan tâm đến vấn đề nước ngập tại TP. HCM .", []),

    # Rec 3775: Tư vấn bất động sản -> REJECT
    ("Hôm nay , chúng ta sẽ bàn về tình trạng ngập nước tại TP. HCM và những điều cần lưu ý khi mua nhà trong khu vực này .", []),

    # Rec 3776: Cảnh báo khí tượng ven sông Sài Gòn -> NEU
    ("Cơ quan khí tượng cảnh báo nguy cơ ngập úng nghiêm trọng nếu triều cường trùng với mưa lớn , đặc biệt tại các khu vực thấp trũng ven sông Sài Gòn , ảnh hưởng đến giao thông và sinh hoạt người dân .", [
        ([28, 29, 30, 31], [6, 7, 8, 9], 'NEU'),
    ]),

    # Rec 3777: Khuyến cáo cấp độ rủi ro thiên tai -> REJECT
    ("Tại TP. Hồ Chí Minh , Cấp độ rủi ro thiên tai được nâng lên mức 2 , các địa phương được khuyến cáo chủ động gia cố bờ bao , hạn chế đi lại vùng ngập sâu để đảm bảo an toàn .", []),

    # Rec 3778: Hướng dẫn kỹ thuật lái xe -> REJECT
    ("Tại TP. Hồ Chí Minh , 1 ️ ⃣ Khi đang đi mà gặp nước ngập", []),

    # Rec 3779: Hướng dẫn kỹ thuật lái xe -> REJECT
    ("Tại TP. Hồ Chí Minh , Giữ khoảng cách với xe trước để tránh sóng nước tràn vào khoang máy .", []),

    # Rec 3780: Hướng dẫn kỹ thuật lái xe -> REJECT
    ("Tại TP. Hồ Chí Minh , 2 ️ ⃣ Nếu xe bị chết máy trong nước", []),

    # Rec 3781: Hướng dẫn kỹ thuật lái xe -> REJECT
    ("Tại TP. Hồ Chí Minh , Tắt máy , bật đèn cảnh báo .", []),

    # Rec 3782: Hướng dẫn kỹ thuật lái xe -> REJECT
    ("Tại TP. Hồ Chí Minh , Gọi cứu hộ kéo xe lên chỗ khô ráo .", []),

    # Rec 3783: Hướng dẫn kỹ thuật lái xe -> REJECT
    ("Tại TP. Hồ Chí Minh , 3 ️ ⃣ Sau khi xe ra khỏi vùng ngập", []),

    # Rec 3784: Hướng dẫn kỹ thuật lái xe -> REJECT
    ("Tại TP. Hồ Chí Minh , Cố nổ máy lại khi xe chết máy .", []),

    # Rec 3785: Hướng dẫn kỹ thuật lái xe -> REJECT
    ("Tại TP. Hồ Chí Minh , Tránh đi vào điểm ngập quen thuộc .", []),

    # Rec 3786: Đã có triều cường, TPHCM
    ("hôm nay triều cường dâng cao , TPHCM đâu đâu cũng ngập .", [
        ([2, 3], [4, 5], 'NEG'),
        ([7], [11], 'NEG'),
    ]),

    # Rec 3787: Tiêu đề lửng lơ không vế câu -> REJECT
    ("Nhân một ngày mưa tầm tã và ngập nước tại Sài Gòn", []),

    # Rec 3788: Tiêu đề danh sách -> REJECT
    ("🌊 DANH SÁCH CHUẨN – CÁC TUYẾN NGẬP KHI TRIỀU CƯỜNG trong đợt xã lũ này", []),

    # Rec 3789: Chú thích trong ngoặc -> REJECT
    ("Tại TP. Hồ Chí Minh , ( Chỉ giữ lại những đoạn chắc chắn ngập do triều lớn )", []),

    # Rec 3790: Đã có QUẬN 7 -> Cắt bỏ tiền tố nhân tạo
    ("📍 QUẬN 7 – NGẬP TRIỀU NẶNG NHẤT TP. HCM", [
        ([1, 2], [4], 'NEG'),
    ]),

    # Rec 3791: Câu cụt kết thúc bằng hai chấm -> REJECT
    ("Tại TP. Hồ Chí Minh , → Ngập triều nặng tại đoạn :", []),

    # Rec 3792: Đã có kênh Tẻ (cắt 'Dọc')
    ("→ Dọc kênh Tẻ – ngập ngay cả khi không mưa .", [
        ([2, 3], [5], 'NEG'),
    ]),

    # Rec 3793: Gạch đầu dòng lửng lơ không địa danh -> REJECT
    ("Tại TP. Hồ Chí Minh , → Một trong những tuyến ngập triều sâu nhất thành phố .", []),

    # Rec 3794: Đã có QUẬN 8 -> Cắt bỏ tiền tố nhân tạo
    ("📍 QUẬN 8 – NGẬP TRIỀU KINH NIÊN", [
        ([1, 2], [4], 'NEG'),
    ]),

    # Rec 3795: Gạch đầu dòng lửng lơ -> REJECT
    ("Tại TP. Hồ Chí Minh , → Ngập triều nặng , “ rốn ngập ” quận 8 .", []),

    # Rec 3796: Đã có kênh Đôi
    ("→ Ngập do triều đẩy từ kênh Đôi lên .", [
        ([6, 7], [1], 'NEG'),
    ]),

    # Rec 3797: Gạch đầu dòng không tên đường cụ thể -> REJECT
    ("Tại TP. Hồ Chí Minh , → Các tuyến nhỏ ven bờ kênh ngập sớm hơn 20 – 40 phút .", []),

    # Rec 3798: Đã có QUẬN 4 -> Cắt bỏ tiền tố nhân tạo
    ("📍 QUẬN 4 – NGẬP KHI TRIỀU MẠNH", [
        ([1, 2], [4], 'NEG'),
    ]),

    # Rec 3799: Gạch đầu dòng không có địa danh -> REJECT
    ("Tại TP. Hồ Chí Minh , → Dù có máy bơm vẫn ngập khi triều cực lớn .", []),

    # Rec 3800: Gạch đầu dòng không có địa danh -> REJECT
    ("Tại TP. Hồ Chí Minh , → Ngập triều do vùng trũng – bán đảo .", []),
]

def test_triplets():
    flaws = 0
    print(f"Tổng số records kiểm tra: {len(batch38_data)}")
    for idx, (text, triplets) in enumerate(batch38_data, 3701):
        tokens = text.split()
        for a_idx, o_idx, s in triplets:
            try:
                asp_tokens = [tokens[i] for i in a_idx]
                op_tokens = [tokens[i] for i in o_idx]
                asp_str = " ".join(asp_tokens)
                op_str = " ".join(op_tokens)
                
                # Check contiguous
                if a_idx != list(range(a_idx[0], a_idx[-1] + 1)):
                    print(f"LỖI KHÔNG LIÊN TỤC ASPECT Rec {idx}: {a_idx}")
                    flaws += 1
                if o_idx != list(range(o_idx[0], o_idx[-1] + 1)):
                    print(f"LỖI KHÔNG LIÊN TỤC OPINION Rec {idx}: {o_idx}")
                    flaws += 1
                    
                # Check overlap
                if set(a_idx).intersection(set(o_idx)):
                    print(f"LỖI TRÙNG LẶP INDEX Rec {idx}: {a_idx} vs {o_idx}")
                    flaws += 1
                    
                # Check punctuation at edges
                bad_puncts = [',', '.', ':', '!', '?', ';', '(', ')', '"', '“', '”', '…', '‘', '’', '\'', '[', ']', '—', '-', '📍', '→']
                if asp_tokens[0] in bad_puncts or asp_tokens[-1] in bad_puncts:
                    print(f"LỖI DẤU CÂU ASPECT Rec {idx}: \"{asp_str}\"")
                    flaws += 1
                if op_tokens[0] in bad_puncts or op_tokens[-1] in bad_puncts:
                    print(f"LỖI DẤU CÂU OPINION Rec {idx}: \"{op_str}\"")
                    flaws += 1
                    
                # Check prepositions
                bad_preps = ['ở', 'tại', 'trên', 'trong', 'tới', 'vào', 'bởi', 'do', 'đến', 'thuộc', 'gần', 'của', 'dọc']
                if asp_tokens[0].lower() in bad_preps:
                    print(f"LỖI GIỚI TỪ ĐẦU ASPECT Rec {idx}: \"{asp_str}\"")
                    flaws += 1
            except Exception as e:
                print(f"LỖI INDEX NGOÀI RANGE Rec {idx}: {e}")
                flaws += 1
    if flaws == 0:
        print("TẤT CẢ CÁC TRIPLETS CỦA BATCH 38 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!")
    else:
        print(f"TỔNG CỘNG PHÁT HIỆN {flaws} LỖI!")
    return flaws

if __name__ == '__main__':
    flaws = test_triplets()
    if flaws == 0:
        phase3_path = 'data/validate_label/thuan/phase3.txt'
        with open(phase3_path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        base_lines = lines[:3700]
        
        new_batch_lines = []
        for text, triplets in batch38_data:
            trip_strs = []
            for a, o, s in triplets:
                trip_strs.append(f"({a}, {o}, '{s}')")
            formatted_trips = '[' + ', '.join(trip_strs) + ']'
            new_batch_lines.append(f"{text}####{formatted_trips}")
            
        full_lines = base_lines + new_batch_lines
        with open(phase3_path, 'w', encoding='utf-8') as f:
            for l in full_lines:
                f.write(l + '\n')
        print(f"Successfully updated {len(full_lines)} lines to {phase3_path}!")
