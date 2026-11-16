# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn chuẩn hóa cho Phase 3 - Batch 37 (Records 3601 - 3700).
Tuân thủ 100% tài liệu BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md.
"""

batch37_data = [
    # Rec 3601: Ùn ứ phương tiện, không ngập -> REJECT
    ("Tại TP. Hồ Chí Minh , Phương tiện giao thông ùn ứ nhiều gây tắc nghẽn cả đoạn đường .", []),

    # Rec 3602: Đã có đường Lê Thánh Tôn -> Cắt bỏ tiền tố nhân tạo
    ("Từ Gò Vấp , Bình Thạnh , đến Hóc Môn , thậm chí cả khu trung tâm thành phố như đoạn Lê Thánh Tôn ( Q. 1 ) nước ngập xấp xỉ mặt đường như muốn tràn vào các khách sạn nơi đây .", [
        ([21, 22, 23], [29], 'NEG'),
    ]),

    # Rec 3603: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , “ Đường thì hẹp lại mưa ngập khung giờ tan tầm , nếu cố chạy xe sẽ nguy hiểm , phải dừng vào vỉa hè trú cho chắc ” , chị nói .", [
        ([1], [8, 9], 'NEG'),
    ]),

    # Rec 3604: Đã có đường Phan Huy Ích
    ("Trận mưa như trút nước xảy ra hơn 3 giờ , tối 19 . 5 biến đường Phan Huy Ích ( Q. Tân Bình , Q. Gò Vấp ) ngập như sông , đến nỗi người dân đẩy bộ xe máy bị nước lút đến yên xe , vật vã tìm đường về nhà .", [
        ([16, 17, 18, 19], [29, 30, 31], 'NEG'),
        ([16, 17, 18, 19], [48, 49], 'NEG'),
    ]),

    # Rec 3605: Đã có đường Phan Huy Ích
    ("Sau cơn mưa lớn nhất kể từ đầu năm 2018 đến nay , tuyến đường Phan Huy Ích ( Q. Gò Vấp , Q. Tân Bình ) được xem là rốn ngập lâu năm trên địa bàn TP. HCM lại tiếp tục ngập kinh hoàng .", [
        ([14, 15, 16, 17], [30, 31], 'NEG'),
        ([14, 15, 16, 17], [42, 43, 44], 'NEG'),
    ]),

    # Rec 3606: Đã có Sài Gòn
    ("VIDEO : Đường phố Sài Gòn ngập sâu tối 19 . 5", [
        ([4, 5], [6, 7], 'NEG'),
    ]),

    # Rec 3607: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Cả tuyến đường hầu như đều bị ngập nặng , có đoạn lút khỏi yên xe máy .", [
        ([1], [10, 11], 'NEG'),
        ([1], [15, 16, 17, 18, 19], 'NEG'),
    ]),

    # Rec 3608: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , “ Dắt bộ xe máy đã hơn 30 phút rồi , mỏi chân kinh khủng nhưng phải đi , chờ nước rút thì biết bao giờ mới về được đến nhà .", [
        ([1], [4, 5], 'NEG'),
    ]),

    # Rec 3609: Đã có TP. HCM
    ("Trận mưa siêu lớn tối 12 . 10 khiến hàng loạt tuyến đường trên địa bàn TP. HCM ngập nặng , nhiều người phải vật vã dắt xe chết máy qua nước ngập đi sửa .", [
        ([16, 17], [18, 19], 'NEG'),
        ([16, 17], [28, 29], 'NEG'),
    ]),

    # Rec 3610: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Chưa đến 1 giờ sau , trận mưa như trút nước khiến hàng loạt tuyến đường ngập sâu .", [
        ([1], [19, 20], 'NEG'),
    ]),

    # Rec 3611: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Người Sài thành nơi cứ mưa là lội nước : ' Ngập hết mùa mưa chắc đổ nợ quá '", [
        ([1], [10, 11], 'NEG'),
        ([1], [14], 'NEG'),
    ]),

    # Rec 3612: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , ' Cứ mưa xuống là ngập , mưa nhỏ cũng ngập .", [
        ([1], [8], 'NEG'),
        ([1], [13], 'NEG'),
    ]),

    # Rec 3613: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Một số hộ dân cũng chống ngập bằng cách căng bạt , đắp bao cát , ván gỗ . . .", [
        ([1], [8, 9], 'NEG'),
    ]),

    # Rec 3614: Câu cụt lở dở -> REJECT
    ("Tại TP. Hồ Chí Minh , trước nhà tránh nước tràn vào .", []),

    # Rec 3615: Ùn ứ giao thông không ngập -> REJECT
    ("Tại TP. Hồ Chí Minh , Đến 19 giờ 30 , lượng phương tiện lưu thông qua khu vực tăng cao , xảy ra ùn ứ cục bộ .", []),

    # Rec 3616: Đã có TP. HCM
    ("Khoảng 13 giờ chiều 15 . 5 , TP. HCM xuất hiện cơn mưa lớn trên hầu hết các quận , huyện của thành phố , khiến nhiều tuyến đường ngập nặng .", [
        ([8, 9], [30, 31], 'NEG'),
    ]),

    # Rec 3617: Đã có TP. HCM
    ("VIDEO : Cơn mưa to ở TP. HCM vào trưa 15 . 5 đã làm nhiều tuyến đường ngập nặng", [
        ([6, 7], [18, 19], 'NEG'),
    ]),

    # Rec 3618: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Khoảng 30 phút sau cơn mưa , một số tuyến đường đã ngập nước khiến nhiều người điều khiển phương tiện khó khăn .", [
        ([1], [15, 16], 'NEG'),
        ([1], [24, 25], 'NEG'),
    ]),

    # Rec 3619: Mưa kẹt xe/sân bay, không ngập -> REJECT
    ("Tại TP. Hồ Chí Minh , Trận mưa trắng trời kéo dài từ trưa đến tối 1 . 4 , hiện vẫn tiếp diễn khiến cho cả trên trời lẫn dưới đất đều ' kẹt cứng ' .", []),

    # Rec 3620: Đã có danh sách đường Hồng Bàng, Phú Hữu, Dương Tử Giang -> Cắt bỏ tiền tố nhân tạo
    ("Các con đường ngập kéo dài như Hồng Bàng , Phú Hữu , Dương Tử Giang . . .", [
        ([7, 8], [3], 'NEG'),
        ([10, 11], [3], 'NEG'),
        ([13, 14, 15], [3], 'NEG'),
    ]),

    # Rec 3621: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhưng nhiều chỗ vẫn chưa thể dọn vì nước vẫn còn ngập , muốn dọn dẹp cho sạch sẽ cũng chẳng được .", [
        ([1], [14], 'NEG'),
    ]),

    # Rec 3622: Câu cụt lở dở -> REJECT
    ("Tại TP. Hồ Chí Minh , cho biết cứ mưa là ngập , mưa nhỏ cũng ngập mà mưa lớn cũng ngập .", []),

    # Rec 3623: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Cứ trời đổ mưa là phải lo đi kê đồ đạc lên cao vì biết kiểu gì nước cũng sẽ tràn vào nhà .", [
        ([1], [23, 24, 25], 'NEG'),
    ]),

    # Rec 3624: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , “ Nhà này đêm hôm qua là ngập nguyên một đêm không có rút được , không có chỗ ngủ luôn .", [
        ([1], [10], 'NEG'),
    ]),

    # Rec 3625: Trích dẫn cụt -> REJECT
    ("Tại TP. Hồ Chí Minh , Ngập quá nhiều ” , anh V .", []),

    # Rec 3626: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , “ Nước vô đột xuất nên trở tay không kịp , gạo , bia ướt hết vậy đó , nước tràn vào nhà ngập hư hết tủ , buôn bán thất thu ” , chị Phượng nói .", [
        ([1], [22, 23, 24], 'NEG'),
        ([1], [25], 'NEG'),
    ]),

    # Rec 3627: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , “ Nước ngập vậy đó , đi ra là xe chết máy ướt hết đồ vậy sao đi làm được , sáng giờ phải ở nhà dọn dẹp , tốn thời gian lại vừa không làm ra tiền được , mà cuộc sống thì khó khăn ” , anh Hải tâm sự .", [
        ([1], [5], 'NEG'),
        ([1], [13, 14], 'NEG'),
    ]),

    # Rec 3628: Đã có đường Phan Huy Ích
    ("Con đường \" siêu ngập \" Phan Huy Ích mênh mông nước sau cơn mưa lớn kéo dài hơn 1 giờ .", [
        ([6, 7, 8], [3, 4], 'NEG'),
        ([6, 7, 8], [9, 10, 11], 'NEG'),
    ]),

    # Rec 3629: Câu trích dẫn cụt -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Đường này cứ mưa là ngập .", []),

    # Rec 3630: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhiều người rơi vào tình trạng \" tiến thoái lưỡng nan \" khi nước mênh mông trên đường .", [
        ([1], [17, 18], 'NEG'),
    ]),

    # Rec 3631: Đã có quận Bình Thạnh, quận 7, huyện Nhà Bè -> Cắt bỏ tiền tố nhân tạo
    ("Các quận Bình Thạnh , quận 7 , huyện Nhà Bè … bị ngập , người đi đường ướt sũng , nhiều xe chết máy phải đẩy bộ .", [
        ([1, 2, 3], [13], 'NEG'),
        ([5, 6], [13], 'NEG'),
        ([8, 9, 10], [13], 'NEG'),
        ([1, 2, 3], [23, 24], 'NEG'),
        ([5, 6], [23, 24], 'NEG'),
        ([8, 9, 10], [23, 24], 'NEG'),
    ]),

    # Rec 3632: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhiều hộ kinh doanh dùng bao cát chắn trước cửa hàng để nước khỏi tràn vào nhưng cũng không thoát .", [
        ([1], [17, 18], 'NEG'),
    ]),

    # Rec 3633: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , \" Vừa thấy mưa lớn , sợ về giờ cao điểm kẹt xe nên tôi xin phép công ty về sớm nhưng không ngờ ra đây lại dính nước ngập , xe chết máy .", [
        ([1], [31, 32], 'NEG'),
        ([1], [35, 36], 'NEG'),
    ]),

    # Rec 3634: Trích dẫn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Chỗ này cứ mưa lớn là nước lên lênh láng , ảnh hưởng buôn bán , du khách , nhưng việc chống ngập chưa được cải thiện \" , chị Thuỳ , bán quán ăn ở khu vực nói .", []),

    # Rec 3635: Trích dẫn cụt -> REJECT
    ("Tại TP. Hồ Chí Minh , “ Có thể hôm nay là trận ngập lịch sử .", []),

    # Rec 3636: Tản mạn chờ nước rút -> REJECT
    ("Tại TP. Hồ Chí Minh , Một số tiểu thương khác chỉ biết đứng nhìn , chờ nước rút mới có thể buôn bán tiếp .", []),

    # Rec 3637: Tản mạn ăn tối -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Cả nhà đang chuẩn bị ăn tối , nước tràn vô , giờ phải vừa chống ngập trong nhà , vừa ra đường vớt rác để nước thoát nhanh \" , ông Hòa nói .", []),

    # Rec 3638: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , \" Nhiều người không biết cứ chạy vào mấy đường ngập cao , xe chết máy , dắt bộ rất vất vả \" , anh nói .", [
        ([1], [13, 14], 'NEG'),
        ([1], [17, 18], 'NEG'),
        ([1], [20, 21], 'NEG'),
    ]),

    # Rec 3639: Đã có TP Thủ Đức
    ("Hình ảnh ngập đường ở TP Thủ Đức :", [
        ([5, 6, 7], [2], 'NEG'),
    ]),

    # Rec 3640: Đã có TP. Thủ Đức
    ("Chiều 30 . 6 , cơn mưa to trên diện rộng , kéo dài nhiều giờ liền làm nhiều tuyến đường ở TP. Thủ Đức ( TP. HCM ) ngập sâu , có nơi ngập nửa bánh xe máy .", [
        ([22, 23, 24], [29, 30], 'NEG'),
        ([22, 23, 24], [34, 35, 36, 37, 38], 'NEG'),
    ]),

    # Rec 3641: Đã có đường Phạm Văn Đồng (cắt 'tại')
    ("Trong khi đó , tại đường Phạm Văn Đồng cũng trong tình trạng kẹt xe nước ngập nghiêm trọng .", [
        ([5, 6, 7, 8], [13, 14], 'NEG'),
        ([5, 6, 7, 8], [16, 17, 18], 'NEG'),
    ]),

    # Rec 3642: Đã có giao lộ Kha Vạn Cân - Phạm Văn Đồng
    ("Đoạn ngập kéo dài khoảng 200 m trên đường này nằm gần giao lộ Kha Vạn Cân - Phạm Văn Đồng làm tình trạng kẹt xe kéo dài đến hơn 1 km khiến giao thông gần như tê liệt .", [
        ([14, 15, 16], [1], 'NEG'),
        ([18, 19, 20], [1], 'NEG'),
        ([14, 15, 16], [24, 25], 'NEG'),
        ([18, 19, 20], [24, 25], 'NEG'),
    ]),

    # Rec 3643: Đã có TP. HCM
    ("Chiều tối 5 . 8 , một cơn mưa lớn bất ngờ trút xuống trên địa bàn TP. HCM khiến nhiều tuyến đường bị ngập sâu , phương tiện chết máy , giao thông gặp khó khăn .", [
        ([17, 18], [24, 25], 'NEG'),
        ([17, 18], [29, 30], 'NEG'),
    ]),

    # Rec 3644: Trích dẫn cá nhân metadata ảnh -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Khu vực này trũng , miệng cống thường xuyên ứ rác khiến tình trạng ngập nặng mỗi khi trời mưa , ngập mãi cũng thấy quen \" , em Kim Long nói ( Ảnh : Hải Long ) .", []),

    # Rec 3645: Người dân vớt rác -> REJECT
    ("Người dân cố gắng vớt rác ùn ứ từ các miệng cống để lưu thông dòng chảy ( Ảnh : Hải Long ) .", []),

    # Rec 3646: Tin dự án chống ngập không ngập -> REJECT
    ("Đáng chú ý , một dự án chống ngập quy mô lớn với tổng mức đầu tư dự kiến lên đến hơn 5 . 000 tỉ đồng đang được đề xuất và trong quá trình triển khai các thủ tục cần thiết .", []),

    # Rec 3647: Tin danh sách dự án chống ngập -> REJECT
    ("Các dự án chống ngập gần hoàn thiện gồm : dự án xây hệ thống thoát nước dọc đường ray xe lửa ( hoàn thành tháng 7 . 2025 ) ; dự án cải tạo rạch Cầu Ngang ( hoàn thành tháng 7 . 2025 ) .", []),

    # Rec 3648: Câu cụt mất chủ ngữ -> REJECT
    ("cũng trong tình trạng ngập nặng , kéo dài hơn do hệ thống cống thoát nước rút chậm .", []),

    # Rec 3649: Tản mạn con cháu đi học -> REJECT
    ("Tại TP. Hồ Chí Minh , “ Con cháu mà đi học là nó hay bị chết máy rồi té xe ngã xe đồ , sụp vào cống thì cũng rất là nguy hiểm . ”", []),

    # Rec 3650: Trích dẫn cụt -> REJECT
    ("Tại TP. Hồ Chí Minh , “ Đường thì nhỏ mà nước nó lên ngập như thế này thì quá khủng khiếp ”", []),

    # Rec 3651: Kế hoạch tương lai -> REJECT
    ("Tại TP. Hồ Chí Minh , Khi hoàn thành , hệ thống này sẽ như một tấm lá chắn khổng lồ , ngăn triều từ các con sông lớn tràn vào nội đô , bảo vệ diện tích 570km² với khoảng 6 , 5 triệu dân .", []),

    # Rec 3652: Bàn luận chuyên gia -> REJECT
    ("Kiến trúc sư Khương Văn Mười Nguyên Phó Chủ tịch Hội KTS Việt Nam cho biết : “ Khi triều cường mưa lớn , nước sông dâng cao hơn miệng cống thoát nước nên lượng nước trong thành phố sẽ không thoát ra được , hay thoát chậm sẽ gây tình trạng ngập .", []),

    # Rec 3653: Bàn luận chuyên gia -> REJECT
    ("Tại TP. Hồ Chí Minh , Mực nước ngoài sông lớn có thể cao nhưng trong kênh rạch của mình ở mức thấp , lúc này chúng như những cái hồ chứa nước , nước sẽ rút nhanh từ đó làm giảm ngập cho thành phố . ”", []),

    # Rec 3654: Bàn luận chính sách -> REJECT
    ("Giờ đây , với sự vào cuộc quyết liệt của Chính phủ và TP. HCM , hy vọng về một ngày công trình chống ngập 10 . 000 tỷ đồng về đích đang lớn hơn bao giờ hết .", []),

    # Rec 3655: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Bị ngập sâu , nhiều phương tiện chết máy .", [
        ([1], [4, 5], 'NEG'),
        ([1], [10, 11], 'NEG'),
    ]),

    # Rec 3656: Nguyện vọng người dân -> REJECT
    ("Tại TP. Hồ Chí Minh , “ Tôi mong các ngành chức năng sớm có biện pháp khắc phục chứ mưa ngập từ năm này sang năm khác , rất khổ ” , ông Mạnh nói .", []),

    # Rec 3657: Nhắc tỉnh Bình Dương -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Tôi vừa tan ca làm trong công trình xây dựng dưới Bình Dương chạy về đến đây thì gặp nước ngập , xe tôi bị chết máy nhiều lần rồi nên không dám chạy qua .", []),

    # Rec 3658: Đã có TP Thủ Đức
    ("Hình ảnh nước ngập ở TP Thủ Đức chiều tối 1 - 9 :", [
        ([5, 6, 7], [3], 'NEG'),
    ]),

    # Rec 3659: Chỉ đạo hành chính -> REJECT
    ("Để giảm ngập trước mắt , Sở Xây dựng TP. HCM yêu cầu đơn vị thuộc thẩm quyền nhanh chóng nạo vét các tuyến cống , cửa xả , kênh rạch bị bồi lắng , đặc biệt ưu tiên các nơi thường xuyên bị ngập và sửa chữa cống bị tắc nghẽn . . .", []),

    # Rec 3660: Đã có TP. HCM
    ("Cơn mưa lớn vào chiều tối 15 . 5 . 2024 đã khiến nhiều tuyến đường ở TP. HCM ngập nặng .", [
        ([17, 18], [19, 20], 'NEG'),
    ]),

    # Rec 3661: Giờ tan tầm chật vật không ngập -> REJECT
    ("Tại TP. Hồ Chí Minh , Thời điểm mưa lớn trùng với giờ tan tầm khiến nhiều người dân chật vật trên đường trở về nhà .", []),

    # Rec 3662: Đã có TP Thủ Đức
    ("24 điểm ngập tại TP Thủ Đức người dân cần lưu ý :", [
        ([4, 5, 6], [2], 'NEG'),
    ]),

    # Rec 3663: Đã có Quốc lộ 1, tỉnh lộ 43, Lê Thị Hoa
    ("Quốc lộ 1 - tỉnh lộ 43 - Lê Thị Hoa ( Bình Chiểu ) : từ cầu vượt Linh Xuân đến giao lộ tỉnh lộ 43 và quốc lộ 1 ngập diện rộng , 1 . 500m .", [
        ([0, 1, 2], [31, 32, 33], 'NEG'),
        ([4, 5, 6], [31, 32, 33], 'NEG'),
        ([8, 9, 10], [31, 32, 33], 'NEG'),
    ]),

    # Rec 3664: Đã có TP. Thủ Đức
    ("Trong trận mưa chiều tối qua ( 15 . 5 ) , nhiều tuyến đường tại TP. Thủ Đức ngập nước nghiêm trọng .", [
        ([16, 17, 18], [19, 20], 'NEG'),
    ]),

    # Rec 3665: Xe cộ ùn ứ không ngập -> REJECT
    ("Tại TP. Hồ Chí Minh , Xe cộ bị ùn ứ , nối đuôi nhau di chuyển .", []),

    # Rec 3666: Tản mạn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Tôi ở đây cả mấy chục năm rồi , khu vực này cứ mưa là sẽ ngập .", []),

    # Rec 3667: Trích dẫn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Tôi chở hàng ở trong hẻm ra thì không may xe chết máy , bây giờ phải đợi nước rút mới kiểm tra được \" , tài xế xe tải chia sẻ .", []),

    # Rec 3668: Đã có TP. HCM
    ("Sáng 10 . 5 , cơn mưa bất ngờ đổ xuống hầu như toàn bộ khu vực TP. HCM khiến nhiều tuyến đường bị ngập sâu .", [
        ([17, 18], [24, 25], 'NEG'),
    ]),

    # Rec 3669: Đã có đường Lê Văn Ninh (cắt 'Trên')
    ("Trên đường Lê Văn Ninh , nước ngập sâu khiến nắp cống bung phun nước như \" vòi rồng \" .", [
        ([1, 2, 3, 4], [7, 8], 'NEG'),
    ]),

    # Rec 3670: Tản mạn che chắn -> REJECT
    ("Tại TP. Hồ Chí Minh , Mặc dù bà đã dùng tấm gỗ che lại nhưng vẫn \" không ăn thua \" , nước vẫn tràn vào nhà .", []),

    # Rec 3671: Tin quy hoạch hồ điều tiết -> REJECT
    ("Thực tế , TP HCM từng đặt mục tiêu xây bảy hồ điều tiết ( một hồ hở , sáu hồ ngầm ) thuộc kế hoạch chống ngập từ năm 2021 , trong đó dự án hồ Gò Dưa rộng 20 ha tại Thủ Đức với tổng vốn hơn 1 . 000 tỷ đồng .", []),

    # Rec 3672: Đã có đường Võ Văn Ngân, đường Dương Văn Cam
    ("Theo ông Mai Hữu Quyết ( Phó chủ tịch UBND thành phố Thủ Đức ) cơn mưa chiều 15 . 5 khiến nhiều tuyến đường trên địa bàn bị ngập , trong đó có tuyến đường Võ Văn Ngân , nặng nhất là đường Dương Văn Cam ngập sâu hơn nửa mét .", [
        ([35, 36, 37, 38], [29], 'NEG'),
        ([43, 44, 45, 46], [47, 48], 'NEG'),
    ]),

    # Rec 3673: Trích dẫn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , “ Nhiều phương tiện bị chết máy phải đẩy bộ về nhà ” , ông Thành , ngụ tại con hẻm trên nói .", []),

    # Rec 3674: Nguyện vọng người dân -> REJECT
    ("\" Mong cải thiện , đường được nâng lên cho người dân đi được thoải mái , không có ngập \"", []),

    # Rec 3675: Nguyện vọng người dân -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Thì đường này thường xuyên ngập nên chỉ mong làm sao cho đường này đỡ ngập để người dân đỡ khổ \"", []),

    # Rec 3676: Câu cụt lở dở -> REJECT
    ("Tại TP. Hồ Chí Minh , Để giải quyết tình trạng ngập đường 38 , UBND TP.", []),

    # Rec 3677: Phê duyệt dự án -> REJECT
    ("Thủ Đức đã phê duyệt dự án nâng cấp đường và hệ thống thoát nước , giúp người dân thoát cảnh bì bõm mỗi khi trời mưa .", []),

    # Rec 3678: Thông tin dự án -> REJECT
    ("\" Tuy nhiên , dự án chỉ đầu tư lắp đặt hệ thống thoát nước , nạo vét mương nước hiện hữu và nâng cấp tuyến hẻm theo hiện trạng trên phần đường , đất do Nhà nước quản lý , vì vậy chỉ giải quyết được một phần ngập nước khu vực .", []),

    # Rec 3679: Đã có chợ Thủ Đức
    ("Sau trận mưa vào chiều ngày 15 . 5 . 2024 , nhiều tiểu thương tại chợ Thủ Đức , TP. HCM bất lực nhìn đồ đạc bị nhấn chìm trong “ biển nước ” .", [
        ([16, 17, 18], [32, 33], 'NEG'),
    ]),

    # Rec 3680: Đã có chợ Thủ Đức
    ("Trong buổi họp báo kinh tế - xã hội định kỳ của TP. HCM diễn ra vào chiều 16 . 5 , vấn đề khu vực chợ Thủ Đức ngập nặng sau cơn mưa cũng được ra trao đổi .", [
        ([26, 27, 28], [29, 30], 'NEG'),
    ]),

    # Rec 3681: Đã có đường Dương Văn Cam
    ("Ông Mai Hữu Quyết , Phó chủ tịch UBND TP. Thủ Đức cho biết cơn mưa chiều ngày 15 . 5 đã khiến nhiều tuyến đường trên địa bàn bị ngập , nặng nhất là đường Dương Văn Cam ngập sâu 0 , 6 mét .", [
        ([35, 36, 37, 38], [39, 40], 'NEG'),
    ]),

    # Rec 3682: Câu cụt mất chủ ngữ -> REJECT
    ("Tại TP. Hồ Chí Minh , khiến một số tuyến đường ngập sâu , việc đi lại của người dân gặp nhiều khó khăn .", []),

    # Rec 3683: Mưa lớn tan tầm không ngập -> REJECT
    ("Tại TP. Hồ Chí Minh , Cơn mưa lớn kéo dài gần một giờ đúng trong khung thời gian tan tầm khiến nhiều người vất vả trên đường đi làm về .", []),

    # Rec 3684: Trích dẫn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , “ Mỗi lần nước ngập là tôi và vợ phải bỏ hết công việc buôn bán để dựng ván che chắn , hôm nay mưa lớn khiến nước tràn vào , chúng tôi phải liên tục tát nước gần cả tiếng đồng hồ .", []),

    # Rec 3685: Đã có Nhà thiếu nhi TP. Thủ Đức, đường Nguyễn Tuyến
    ("Đoạn ngập này kéo dài khoảng 300 m , xung quanh Nhà thiếu nhi TP. Thủ Đức ( cơ sở 1 ) và kéo dài đến đường Nguyễn Tuyến .", [
        ([11, 12, 13, 14, 15, 16], [1], 'NEG'),
        ([26, 27, 28], [1], 'NEG'),
    ]),

    # Rec 3686: Đã có TPHCM
    ("Sau đây là một số hình ảnh nhiều tuyến đường ở TPHCM ngập sâu do mưa cực lớn :", [
        ([11], [12, 13], 'NEG'),
    ]),

    # Rec 3687: Tản mạn che chắn -> REJECT
    ("Tại TP. Hồ Chí Minh , Nhiều tiểu thương phải vất vả che chắn gian hàng , di dời phương tiện để tránh bị nước làm hỏng .", []),

    # Rec 3688: Đã có đường Trần Xuân Soạn
    ("Theo anh Nguyễn Ngọc Hoàng , nhân viên kỹ thuật thuộc Công ty Thoát nước đô thị TP. HCM , phải cần 60 - 70 mét khối cát , với khoảng 2 . 000 bao cát để có thể chặn quanh bờ kênh Tẻ , hạn chế nước tràn vào đường Trần Xuân Soạn , P. Tân Thuận , TP. HCM .", [
        ([50, 51, 52, 53], [48], 'NEG'),
    ]),

    # Rec 3689: Đã có triều cường ở TP. HCM, đường Trần Xuân Soạn, đường Đào Trí, Gò Ô Môi
    ("Ghi nhận của Thanh Niên tối 7 . 11 , triều cường ở TP. HCM dâng cao khiến nhiều tuyến đường ngập sâu trong nước , đặc biệt tại khu vực đường Trần Xuân Soạn ( phường Tân Thuận ) , đường Đào Trí , Gò Ô Môi ( phường Phú Thuận ) . . .", [
        ([10, 11, 12, 13, 14], [15, 16], 'NEG'),
        ([31, 32, 33, 34], [21, 22], 'NEG'),
        ([41, 42, 43], [21, 22], 'NEG'),
        ([45, 46, 47], [21, 22], 'NEG'),
    ]),

    # Rec 3690: Đã có đường Quốc Hương
    ("Tối nay , đường Quốc Hương lại ngập sâu , kéo dài gần như suốt tuyến .", [
        ([3, 4, 5], [7, 8], 'NEG'),
    ]),

    # Rec 3691: Đã có Trường đại học Văn hóa TP. HCM
    ("Đoạn ngập sâu nhất phải kể đến là khu vực trước Trường đại học Văn hóa TP. HCM .", [
        ([11, 12, 13, 14, 15, 16, 17], [1, 2], 'NEG'),
    ]),

    # Rec 3692: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nơi đây nước ngập lên đến hơn bánh xe máy .", [
        ([1], [6], 'NEG'),
    ]),

    # Rec 3693: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Có nơi nước ngập đến gần 1 m .", [
        ([1], [6], 'NEG'),
    ]),

    # Rec 3694: Họp báo dự án chống ngập -> REJECT
    ("Trong cuộc họp báo kinh tế - xã hội định kỳ do Sở VH - TT cùng Ban Tuyên giáo và Dân vận Thành ủy TP. HCM tổ chức chiều 30 . 10 , đại diện Sở Xây dựng thông tin về các dự án chống ngập do triều cường trên địa bàn .", []),

    # Rec 3695: Phát biểu họp báo kết thúc bằng dấu hai chấm -> REJECT
    ("Ông Hoàng Phúc Dũng , Phó trưởng phòng Hạ tầng Kỹ thuật , Sở Xây dựng TP. HCM cho biết , để giải quyết tình hình ngập nước do triều , TP. HCM đã hoàn thành các dự án và đưa vào vận hành các cống kiểm soát triều như :", []),

    # Rec 3696: Phát biểu dự án giảm ngập -> REJECT
    ("\" Một số dự án giải quyết ngập trên địa bàn Gò Vấp , Thảo Điền - Quốc Hương và chợ Thủ Đức đang và sẽ triển khai cũng sẽ góp phần giảm ngập cho các khu vực \" nóng \" hiện nay trên địa bàn \" , ông Hoàng Phúc Dũng nói .", []),

    # Rec 3697: Câu cụt kết thúc bằng hai chấm -> REJECT
    ("Hiện TP. HCM đang tập trung đẩy nhanh thực hiện các công trình trọng điểm chống ngập như :", []),

    # Rec 3698: Đã có đường Tô Ngọc Vân
    ("“ Hôm nay , mưa lâu nên tuyến đường này ngập sâu , nước tràn vào hàng quán nên tôi đóng cửa sớm ” , một tiểu thương trên đường Tô Ngọc Vân nói .", [
        ([29, 30, 31, 32], [10, 11], 'NEG'),
        ([29, 30, 31, 32], [14, 15], 'NEG'),
    ]),

    # Rec 3699: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Một số người dân dùng đến 2 lớp ván chắn nước , nhưng nước vẫn tràn vào nhà .", [
        ([1], [18, 19, 20], 'NEG'),
    ]),

    # Rec 3700: Đã có hẻm 181 (cắt 'Tại')
    ("Tại hẻm 181 , nhiều hộ dân dù đã chủ động nâng nền nhưng vẫn bất lực trước sức nước .", [
        ([1, 2], [15, 16], 'NEG'),
    ]),
]

def test_triplets():
    flaws = 0
    print(f"Tổng số records kiểm tra: {len(batch37_data)}")
    for idx, (text, triplets) in enumerate(batch37_data, 3601):
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
                bad_puncts = [',', '.', ':', '!', '?', ';', '(', ')', '"', '“', '”', '…', '‘', '’', '\'', '[', ']', '—', '-']
                if asp_tokens[0] in bad_puncts or asp_tokens[-1] in bad_puncts:
                    print(f"LỖI DẤU CÂU ASPECT Rec {idx}: \"{asp_str}\"")
                    flaws += 1
                if op_tokens[0] in bad_puncts or op_tokens[-1] in bad_puncts:
                    print(f"LỖI DẤU CÂU OPINION Rec {idx}: \"{op_str}\"")
                    flaws += 1
                    
                # Check prepositions
                bad_preps = ['ở', 'tại', 'trên', 'trong', 'tới', 'vào', 'bởi', 'do', 'đến', 'thuộc', 'gần', 'của']
                if asp_tokens[0].lower() in bad_preps:
                    print(f"LỖI GIỚI TỪ ĐẦU ASPECT Rec {idx}: \"{asp_str}\"")
                    flaws += 1
            except Exception as e:
                print(f"LỖI INDEX NGOÀI RANGE Rec {idx}: {e}")
                flaws += 1
    if flaws == 0:
        print("TẤT CẢ CÁC TRIPLETS CỦA BATCH 37 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!")
    else:
        print(f"TỔNG CỘNG PHÁT HIỆN {flaws} LỖI!")
    return flaws

if __name__ == '__main__':
    flaws = test_triplets()
    if flaws == 0:
        phase3_path = 'data/validate_label/thuan/phase3.txt'
        with open(phase3_path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        base_lines = lines[:3600]
        
        new_batch_lines = []
        for text, triplets in batch37_data:
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
