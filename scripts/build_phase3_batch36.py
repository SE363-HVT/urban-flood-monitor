# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn chuẩn hóa cho Phase 3 - Batch 36 (Records 3501 - 3600).
Tuân thủ 100% tài liệu BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md.
"""

batch36_data = [
    # Rec 3501: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , “ Sáng triều lên , tối cũng ngập ” , anh chia sẻ .", [
        ([1], [10], 'NEG'),
    ]),

    # Rec 3502: Caption fragment -> REJECT
    ("Tại TP. Hồ Chí Minh , để tránh nước tràn vào nhà ( Ảnh : Bảo Quyên ) .", []),

    # Rec 3503: Triều cường in-place expansion -> 'triều cường ở TPHCM'
    ("\" Lần đầu tiên tôi thấy triều cường ở TPHCM dâng cao đến mức này , nước ngập khiến khu vực chân cầu kẹt cứng .", [
        ([6, 7, 8, 9], [10, 11], 'NEG'),
        ([6, 7, 8, 9], [17], 'NEG'),
    ]),

    # Rec 3504: Caption fragment, no flood -> REJECT
    ("Tại TP. Hồ Chí Minh , Giao thông qua khu vực này gần như tê liệt , xe cộ di chuyển chậm chạp dưới cơn mưa nặng hạt ( Ảnh : Khoa Nguyễn ) .", []),

    # Rec 3505: Trạm Thủ Dầu Một (Bình Dương) -> REJECT
    ("Đỉnh triều cao nhất ngày ở mức xấp xỉ hoặc trên báo động 2 sẽ duy trì đến hết ngày 26 và 27 - 11 , riêng trạm Thủ Dầu Một ở mức cao trên báo động 3 trong 5 ngày tới .", []),

    # Rec 3506: Hồ Dầu Tiếng, trạm Dầu Tiếng (Tây Ninh/Bình Dương) -> REJECT
    ("Do ảnh hưởng xả của hồ Dầu Tiếng , mực nước tại trạm Dầu Tiếng lên nhanh trong 1 - 2 ngày đầu , sau biến đổi chậm và duy trì ở mức cao trên báo động 2 .", []),

    # Rec 3507: Triều cường in-place expansion -> 'triều cường ở TPHCM'
    ("Chị Huyền Trang , một người dân địa phương , bày tỏ sự ngán ngẩm : \" Thấy thông tin triều cường ở TPHCM dâng cao nhưng không nghĩ tuyến đường này lại ngập sâu đến vậy .", [
        ([20, 21, 22, 23], [24, 25], 'NEG'),
    ]),

    # Rec 3508: Đã có đường Hoàng Quốc Việt, Phạm Hữu Lầu
    ("Từ trên cao , giao lộ Hoàng Quốc Việt – Phạm Hữu Lầu ( phường Tân Mỹ ) trông như một dòng sông mênh mông .", [
        ([6, 7, 8], [23, 24], 'NEG'),
        ([10, 11, 12], [23, 24], 'NEG'),
    ]),

    # Rec 3509: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Tuy nhiên ở các khu vực chưa có kè , nước vẫn dâng mạnh , tràn vào nhà và đường nội bộ .", [
        ([1], [15, 16], 'NEG'),
        ([1], [18, 19, 20], 'NEG'),
    ]),

    # Rec 3510: CSGT hướng dẫn, không ngập -> REJECT
    ("Trên các tuyến đường thủy , CSGT bố trí lực lượng trực 24 / 24 giờ , chuẩn bị xuồng , phao cứu sinh , tổ chức tuần tra tại các điểm có nguy cơ lốc xoáy , nước chảy xiết , khu vực thi công , cầu yếu , vùng có nguy cơ sạt lở … nhằm cảnh báo và hướng dẫn người dân đảm bảo an toàn .", []),

    # Rec 3511: Sở NN-MT cảnh báo hành chính chung chung -> REJECT
    ("Đối với các tuyến đường ngập do triều cường , Sở NN - MT đề nghị các đơn vị có biện pháp đảm bảo an toàn nhằm tránh xảy ra tai nạn khi ngập úng .", []),

    # Rec 3512: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nước cũng tràn vào nhà khiến sinh hoạt của người dân bị đảo lộn .", [
        ([1], [5, 6, 7], 'NEG'),
    ]),

    # Rec 3513: Dự báo điều kiện "Nếu hiện tượng này..." -> REJECT
    ("\" Nếu hiện tượng này cộng hưởng với các yếu tố như triều cường , mưa lớn hay gió mùa , mức độ ngập sẽ nghiêm trọng hơn trước đây \" , ông Quyết lưu ý thêm .", []),

    # Rec 3514: Đã có đường Nguyễn Xuân Soạn
    ("Đoạn ngập đường Nguyễn Xuân Soạn nằm dưới cầu Tân Thuận , kéo dài khoảng 400 m , có nơi ngập lút bánh xe máy .", [
        ([2, 3, 4, 5], [1], 'NEG'),
        ([2, 3, 4, 5], [20, 21, 22, 23, 24], 'NEG'),
    ]),

    # Rec 3515: Đã có cầu Phú Mỹ, Phú Thuận, Huỳnh Tấn Phát
    ("Đoạn ngập nặng là từ chân cầu Phú Mỹ đến giao lộ Phú Thuận - Huỳnh Tấn Phát .", [
        ([6, 7, 8], [1, 2], 'NEG'),
        ([12, 13], [1, 2], 'NEG'),
        ([15, 16, 17], [1, 2], 'NEG'),
    ]),

    # Rec 3516: Đã có bán đảo Thanh Đa, đường Bình Quới
    ("Đặc biệt , tại khu bán đảo Thanh Đa — nơi được bao quanh bởi sông Sài Gòn — mực nước dâng cao , nhiều đoạn trên đường Bình Quới ngập lút bánh xe .", [
        ([4, 5, 6, 7, 8], [21, 22], 'NEG'),
        ([27, 28, 29], [30, 31, 32, 33], 'NEG'),
    ]),

    # Rec 3517: Tản mạn cá nhân dọn nhà -> REJECT
    ("Tại TP. Hồ Chí Minh , Bà cho biết , chưa kịp lau dọn hết nước hôm qua thì nay nước lại tràn vào .", []),

    # Rec 3518: Tản mạn ô tô chạy tạo sóng -> REJECT
    ("Tại TP. Hồ Chí Minh , Bà con nơi đây vất vả nhất là khi ô tô chạy qua , tạo sóng mạnh khiến nước vượt qua các lớp chặn và tràn vào nhà .", []),

    # Rec 3519: Đi lại giờ tan tầm, không ngập -> REJECT
    ("Ông Nguyễn Thanh Nhã ( ở khu vực đường Phạm Hữu Lầu ) cho biết , những ngày qua rất vất vả để đi lại vào giờ tan tầm .", []),

    # Rec 3520: Đã có Đường Trần Xuân Soạn
    ("Đường Trần Xuân Soạn , phường Tân Thuận thường xuyên ngập do triều cường .", [
        ([0, 1, 2, 3], [8, 9, 10], 'NEG'),
    ]),

    # Rec 3521: Đã có TP. HCM, triều cường
    ("Chiều 23 . 10 , triều cường dâng cao ở TP. HCM khiến nhiều con đường trở nên ngập nặng .", [
        ([5, 6], [7, 8], 'NEG'),
        ([10, 11], [18, 19], 'NEG'),
    ]),

    # Rec 3522: Đã có đường Bình Quới
    ("Bình thường người dân vẫn đi lại được trên đường Bình Quới , nhưng hôm nay hầu hết xe đều phải dắt bộ , rất khổ sở . ”", [
        ([9, 10, 11], [20, 21, 22], 'NEG'),
    ]),

    # Rec 3523: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Dòng nước đục ngầu cuồn cuộn tràn vào nhà người dân , các con hẻm và tầng trệt chung cư , khiến người dân phải kê cao đồ đạc , dọn dẹp để chạy . . .", [
        ([1], [9, 10, 11], 'NEG'),
    ]),

    # Rec 3524: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Chỉ ít phút sau , một đoạn đường này trở nên ngập nặng .", [
        ([1], [14, 15], 'NEG'),
    ]),

    # Rec 3525: Cầu Tân Thuận
    ("Đoạn ngập này nằm phía dưới cầu Tân Thuận , kéo dài khoảng 400 m .", [
        ([6, 7, 8], [1], 'NEG'),
    ]),

    # Rec 3526: An toàn giàn giáo, không ngập -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Các công trình đang thi công phải khẩn trương tháo dỡ hoặc chằng chống an toàn giàn giáo , cần cẩu , vật liệu xây dựng để tránh gây nguy hiểm .", []),

    # Rec 3527: Ùn ứ xe cộ, không ngập -> REJECT
    ("Tại TP. Hồ Chí Minh , Dòng xe ùn ứ kéo dài , nối đuôi nhau nhích từng chút một .", []),

    # Rec 3528: Ùn ứ xe cộ, không ngập -> REJECT
    ("Dòng xe ùn ứ hơn 1km , kéo dài lên đến cầu Rạch Chiếc .", []),

    # Rec 3529: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Bị ngập từ 30 tới 60 cm , nhiều đoạn nước chảy xiết khiến xe máy chết máy hàng loạt , người dân phải dắt bộ qua vùng ngập .", [
        ([1], [4], 'NEG'),
        ([1], [19, 20], 'NEG'),
        ([1], [27, 28], 'NEG'),
    ]),

    # Rec 3530: Buôn bán ế ẩm -> REJECT
    ("Tại TP. Hồ Chí Minh , “ Mỗi lần nước ngập là buôn bán ế ẩm , bán từ 5h chiều đến 5h sáng được 40 . 000 đồng ” , cô Kim Hà nói .", []),

    # Rec 3531: Đã có P. Tân Phú, Phú Thuận, cầu Phú Mỹ, Huỳnh Tấn Phát
    ("Đoạn ngập nặng nhất phải kể đến khu vực P. Tân Phú và Phú Thuận , đoạn từ cầu Phú Mỹ đến giao lộ Phú Thuận - Huỳnh Tấn Phát .", [
        ([9, 10, 11], [1, 2], 'NEG'),
        ([13, 14], [1, 2], 'NEG'),
        ([18, 19, 20], [1, 2], 'NEG'),
        ([27, 28, 29], [1, 2], 'NEG'),
    ]),

    # Rec 3532: Đã có Phú Thuận, Huỳnh Tấn Phát
    ("Điểm ngập nặng nhất kể đến là khu vực giao lộ Phú Thuận - Huỳnh Tấn Phát .", [
        ([11, 12], [1, 2], 'NEG'),
        ([14, 15, 16], [1, 2], 'NEG'),
    ]),

    # Rec 3533: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhiều nhà dân bị nước tràn vào .", [
        ([1], [8, 9], 'NEG'),
    ]),

    # Rec 3534: Đã có quận 7
    ("\" Tình trạng ngập nước do triều cường kéo dài nhiều năm nay trên tuyến đường này nhưng không được các cơ quan chức năng giải quyết triệt để , bà con chúng tôi gặp nhiều bất tiện \" , chị Lý Thị Hoa ( quận 7 ) nói ( Ảnh : Thúy Hường ) .", [
        ([45, 46], [3, 4], 'NEG'),
    ]),

    # Rec 3535: Đã có Huỳnh Tấn Phát, đường số 20, khu dân cư Thanh Đa
    ("Tương tự , triều cường còn gây ngập ở một số tuyến đường như Huỳnh Tấn Phát , đường số 20 ( quận 7 ) và khu dân cư Thanh Đa ( quận Bình Thạnh ) . . .", [
        ([14, 15, 16], [7], 'NEG'),
        ([18, 19, 20], [7], 'NEG'),
        ([26, 27, 28, 29, 30], [7], 'NEG'),
    ]),

    # Rec 3536: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Hàng loạt xe chết máy .", [
        ([1], [6, 7], 'NEG'),
    ]),

    # Rec 3537: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , “ Tháng này ngập hoài , nước ngập hơn nửa bánh xe khiến tôi không thể chạy được , bất lực lắm \" - chị nói , giọng đầy mệt mỏi .", [
        ([1], [6, 7], 'NEG'),
        ([1], [10, 11, 12, 13, 14], 'NEG'),
    ]),

    # Rec 3538: Cảnh báo / Dự báo -> NEU
    ("Người dân cần tránh đi lại những tuyến đường có khả năng bị ngập ở TP. HCM trong đợt triều cường này .", [
        ([15, 16], [10, 11, 12, 13], 'NEU'),
    ]),

    # Rec 3539: Đã có TP. HCM, quận 7
    ("Sáng 18 - 10 , triều cường tại TP. HCM dâng cao , một số nơi tại quận 7 ngập chưa kịp rút do mưa chiều qua thì hứng thêm đợt triều đầu sáng nay .", [
        ([5, 6], [10, 11], 'NEG'),
        ([17, 18], [19], 'NEG'),
    ]),

    # Rec 3540: Đã có kênh Đôi
    ("Từ khoảng 16 giờ ngày 22 . 10 . 2025 , sau trận mưa lớn , nước từ kênh Đôi bắt đầu dâng cao , chỉ sau nửa giờ , mặt đường đã ngập sâu hơn nửa bánh xe .", [
        ([18, 19], [22, 23], 'NEG'),
        ([18, 19], [33, 34, 35, 36, 37, 38], 'NEG'),
    ]),

    # Rec 3541: Tản mạn xắn quần lội nước -> REJECT
    ("Điều đáng buồn là dù người dân đã quen với việc phải xắn quần lội nước , kê đồ đạc , mua máy bơm , đắp nền cao . . .", []),

    # Rec 3542: Câu cụt lở dở -> REJECT
    ("Tại TP. Hồ Chí Minh , lại được \" lên sóng \" vì ngập nặng .", []),

    # Rec 3543: Dự báo trạm Thủ Dầu Một (Bình Dương) -> REJECT
    ("Đỉnh triều cao nhất trong đợt này có khả năng xuất hiện vào ngày 21 đến 23 . 10 và đạt ở mức sau : tại trạm Phú An , Nhà Bè có khả năng lên mức 1 , 60 - 1 , 65m , xấp xỉ hoặc trên mức báo động 3 từ 0 , 05m ; trạm Thủ Dầu Một lên mức 1 , 68 - 1 , 72m , trên báo động 3 từ 0 , 08 - 0 , 12m .", []),

    # Rec 3544: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nước đọng thành từng vũng lớn giữa lòng đường , tràn vào trước cửa nhiều quán bar , nhà hàng .", [
        ([1], [13, 14], 'NEG'),
    ]),

    # Rec 3545: Đã có đường 3 Tháng 2, Lạc Long Quân, Bình Thới, Lê Hồng Phong
    ("Cùng thời điểm , đường 3 Tháng 2 , Lạc Long Quân , Bình Thới ( phường Hòa Bình ) , Lê Hồng Phong ( phường Vườn Lài ) và một số tuyến khác cũng xuất hiện tình trạng ngập úng .", [
        ([4, 5, 6, 7], [39, 40], 'NEG'),
        ([9, 10, 11], [39, 40], 'NEG'),
        ([13, 14], [39, 40], 'NEG'),
        ([21, 22, 23], [39, 40], 'NEG'),
    ]),

    # Rec 3546: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhiều bao cát được kê sẵn , nhưng nước vẫn tràn vào nhà và đường .", [
        ([1], [13, 14, 15], 'NEG'),
    ]),

    # Rec 3547: Tản mạn khu trũng thấp -> REJECT
    ("Tại TP. Hồ Chí Minh , Những hộ ở trong hẻm nhỏ hay khu vực trũng thấp càng vất vả hơn .", []),

    # Rec 3548: Tản mạn việc đi lại -> REJECT
    ("Tại TP. Hồ Chí Minh , Việc đi lại rất khổ sở , nhất là mấy em học sinh tan trường về trễ .", []),

    # Rec 3549: Trích dẫn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , “ Tôi đứng đợi 30 phút rồi mà nước vẫn chưa rút ” , chị Thảo - một người đi đường - chia sẻ .", []),

    # Rec 3550: Trích dẫn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , Còn bà Hoa , sống ngay mặt tiền tuyến đường này , cho biết thời gian qua , hễ mưa là đường ngập .", []),

    # Rec 3551: Nguyện vọng người dân -> REJECT
    ("Chúng tôi mong hệ thống thoát nước sớm được nâng cấp để việc đi lại đỡ vất vả \" , bà nói .", []),

    # Rec 3552: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , “ Nước ngập đến đầu gối , đi lại rất vất vả .", [
        ([1], [5, 6, 7, 8], 'NEG'),
        ([1], [12, 13, 14], 'NEG'),
    ]),

    # Rec 3553: Đã có đường Võ Văn Ngân, chợ Thủ Đức
    ("Ghi nhận trên đường Võ Văn Ngân , đoạn chợ Thủ Đức , mưa lớn giờ tan tầm khiến ùn ứ giao thông .", [
        ([3, 4, 5, 6], [19, 20], 'NEG'),
        ([9, 10, 11], [19, 20], 'NEG'),
    ]),

    # Rec 3554: Xe buýt kẹt xe, không ngập -> REJECT
    ("Tại TP. Hồ Chí Minh , Nhiều xe buýt đi từ hai phía cũng kẹt cứng , tìm cách lách qua khu vực kẹt .", []),

    # Rec 3555: Mưa lớn ùn ứ cục bộ, không ngập -> REJECT
    ("Tại TP. Hồ Chí Minh , Cùng thời điểm , mưa lớn cũng xảy ra tại nhiều tuyến khác ở khu vực tây thành phố , khiến giao thông ùn ứ cục bộ .", []),

    # Rec 3556: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Bị ngập sâu khiến việc lưu thông của người dân khó khăn .", [
        ([1], [4, 5], 'NEG'),
        ([1], [13, 14], 'NEG'),
    ]),

    # Rec 3557: Đã có đường Lê Văn Việt (cắt 'Tại' ở đầu)
    ("Tại đường Lê Văn Việt , nước mênh mông .", [
        ([1, 2, 3, 4], [7, 8], 'NEG'),
    ]),

    # Rec 3558: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Đoạn ngập nặng khoảng nửa mét , xe chết máy la liệt .", [
        ([1], [4, 5], 'NEG'),
        ([1], [11, 12, 13, 14], 'NEG'),
    ]),

    # Rec 3559: Tản mạn cá nhân dắt xe -> REJECT
    ("Vừa hì hục dắt xe máy lên vỉa hỉa , anh Hoàng Tư ( 34 tuổi ) cho biết đang đi làm từ Thủ Đức về quận 10 thì gặp mưa .", []),

    # Rec 3560: Tản mạn túi nylon -> REJECT
    ("Tại TP. Hồ Chí Minh , “ Tôi lấy túi nylon đựng đôi giày để vượt qua đoạn ngập nước nhưng chỉ chạy được vài chục mét thì xe chết máy , đứng im .", []),

    # Rec 3561: Tản mạn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , “ Tôi vừa vào khu vực bên trong phường giao được một số chỗ , khi quay lại thì đường mênh mông nước , chay được một đoạn thì chết máy .", []),

    # Rec 3562: Câu cụt mất dấu mở ngoặc -> REJECT
    ("Thủ Đức , quận 9 cũ ) bị ngập rất nặng .", []),

    # Rec 3563: Câu cụt mất dấu mở ngoặc -> REJECT
    ("Thủ Đức ) biến thành sông một đoạn dài .", []),

    # Rec 3564: Báo cáo lượng mưa không ngập -> REJECT
    ("Theo bản tin phát đi lúc 21h50 của Đài Khí tượng thủy văn khu vực Nam Bộ , tính đến thời điểm này thì trận mưa đã kéo dài 6 giờ đồng hồ , có nhiều nơi mưa đặc biệt to , vũ lượng đo được tại quận 2 là 149 , 6mm ; tại huyện Hóc Môn là 102 , 4mm ; tại quận Thủ Đức là 193 , 8mm …", []),

    # Rec 3565: Đã có TP. HCM
    ("Cơn mưa cực lớn tối 18 . 5 khiến nhiều tuyến đường khu vực phía Tây Bắc TP. HCM ngập sâu , người dân phải lội nước ngập dắt xe chết máy tìm nơi sửa giữa đêm khuya .", [
        ([17, 18], [19, 20], 'NEG'),
        ([17, 18], [30, 31], 'NEG'),
    ]),

    # Rec 3566: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Dù đã qua ngày mới ( 19 . 5 ) , nhưng nhiều người vẫn còn dắt xe chết máy lang thang trên đường giữa đêm khuya tìm nơi sửa .", [
        ([1], [21, 22], 'NEG'),
    ]),

    # Rec 3567: Đã có TP. HCM
    ("[ VIDEO ] Đêm chật vật khi nhiều tuyến đường TP. HCM giống miền Tây mùa nước nổi", [
        ([10, 11], [4, 5], 'NEG'),
        ([10, 11], [12, 13, 14, 15, 16, 17], 'NEG'),
    ]),

    # Rec 3568: Đã có đường Lê Thị Hoa (cắt 'tại')
    ("Hễ trời bắt đầu chuyển mưa là những người dân sinh sống tại đường Lê Thị Hoa ( Q. Thủ Đức , TP. HCM ) lại loay hoay tranh thủ dọn đồ kê lên cao , rút điện tủ lạnh để tránh bị nước ngập .", [
        ([13, 14, 15, 16], [43, 44], 'NEG'),
    ]),

    # Rec 3569: Đã có Tỉnh lộ 43 -> Cắt bỏ tiền tố nhân tạo
    ("“ Trời mưa lớn những người đi từ đầu đường từ Tỉnh lộ 43 rẽ vào không biết dính nước ngập chết máy xe nhiều lắm , người dân ở đây thấy xe chết máy thì thường đẩy phụ .", [
        ([11, 12, 13], [19, 20], 'NEG'),
        ([11, 12, 13], [21, 22], 'NEG'),
    ]),

    # Rec 3570: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , “ Giờ thì phải chịu thôi chứ không biết làm sao , suốt mùa mưa là cứ mưa là ngập , ở đây mưa lớn chỉ tầm 10 phút là đường ngập rồi .", [
        ([1], [22], 'NEG'),
        ([1], [34, 35], 'NEG'),
    ]),

    # Rec 3571: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Clip : Nước ngập như sông sau mưa , xe chết máy la liệt", [
        ([1], [6, 7, 8], 'NEG'),
        ([1], [13, 14, 15, 16], 'NEG'),
    ]),

    # Rec 3572: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Xe chết máy la liệt , người dân gồng mình “ bơi ” về nhà chiều cuối tuần .", [
        ([1], [4, 5, 6, 7], 'NEG'),
    ]),

    # Rec 3573: Câu hỏi cảm thán tu từ -> REJECT
    ("Tại TP. Hồ Chí Minh , “ Tại sao cứ mưa là đường ngập ? .", []),

    # Rec 3574: Câu hỏi cảm thán tu từ -> REJECT
    ("Tại TP. Hồ Chí Minh , Tại ai mà sao đường ngập .", []),

    # Rec 3575: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , “ Cuối tuần dính phát mưa đường ngập như này thật khổ quá mà .", [
        ([1], [9, 10], 'NEG'),
        ([1], [13, 14], 'NEG'),
    ]),

    # Rec 3576: Đã có đường Phan Văn Hớn
    ("Ghi nhận trên đường Phan Văn Hớn ( quận 12 ) nước ngập gần nửa mét khiến nhiều phương tiện chết máy .", [
        ([3, 4, 5, 6], [12, 13, 14, 15], 'NEG'),
        ([3, 4, 5, 6], [20, 21], 'NEG'),
    ]),

    # Rec 3577: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Đoạn ngập kéo dài khoảng 1km , có đoạn ngập sâu hơn nửa mét khiến không chỉ xe máy mà ô tô cũng chết máy .", [
        ([1], [4], 'NEG'),
        ([1], [12, 13, 14, 15, 16], 'NEG'),
        ([1], [26, 27], 'NEG'),
    ]),

    # Rec 3578: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Các phương tiện di chuyển khó khăn trên đường ngập", [
        ([1], [8, 9], 'NEG'),
        ([1], [12], 'NEG'),
    ]),

    # Rec 3579: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Ô tô lưu thông tạo sóng mạnh trên đường ngập", [
        ([1], [12], 'NEG'),
    ]),

    # Rec 3580: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Tuyến đường mênh mông nước .", [
        ([1], [5, 6, 7], 'NEG'),
    ]),

    # Rec 3581: Đã có TP. HCM
    ("Sáng 26 . 11 , nhiều tuyến đường tại TP. HCM ngập nặng do mưa lớn từ cơn bão số 9 .", [
        ([9, 10], [11, 12], 'NEG'),
    ]),

    # Rec 3582: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhiều người bất chấp cho xe máy , ô tô lội qua đoạn ngập sâu để đến chỗ làm việc .", [
        ([1], [16, 17], 'NEG'),
    ]),

    # Rec 3583: Đã có giao lộ D1 - Điện Biên Phủ -> Cắt bỏ tiền tố nhân tạo
    ("Tại giao lộ D1 - Điện Biên Phủ ( P. 25 , Q. Bình Thạnh ) , giao thông náo loạn vì một chiếc ô tô chết máy từ đêm 25 . 11 .", [
        ([3], [19, 20], 'NEG'),
        ([5, 6, 7], [19, 20], 'NEG'),
        ([3], [26, 27], 'NEG'),
        ([5, 6, 7], [26, 27], 'NEG'),
    ]),

    # Rec 3584: Đã có D1 - Điện Biên Phủ, đường D1
    ("Trao đổi với PV Thanh Niên , chủ xe ô tô bị chết máy tại giao lộ D1 - Điện Biên Phủ cho biết , tối 25 . 11 , xe anh trên đường đi công việc về nhà khi qua đường D1 thì gặp nước ngập nặng .", [
        ([17], [12, 13], 'NEG'),
        ([19, 20, 21], [12, 13], 'NEG'),
        ([41, 42], [46, 47], 'NEG'),
    ]),

    # Rec 3585: Tản mạn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , Anh cố đi qua thì xe bị chết máy .", []),

    # Rec 3586: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Dòng nước hôi thối từ ngoài tràn vào .", [
        ([1], [5, 6], 'NEG'),
        ([1], [9, 10], 'NEG'),
    ]),

    # Rec 3587: Tản mạn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Từ đầu năm tới nay , nhà tôi bị ngập khoảng 4 – 5 lần , nhưng hôm nay là nghiêm trọng nhất .", []),

    # Rec 3588: Triều cường in-place expansion -> 'triều cường ở TPHCM'
    ("\" Suốt hai hôm nay triều cường ở TPHCM dâng , nước ngập lênh láng , nhiều người té trên đường lắm rồi .", [
        ([5, 6, 7, 8], [9], 'NEG'),
        ([5, 6, 7, 8], [12, 13, 14], 'NEG'),
    ]),

    # Rec 3589: Mưa lớn ùn tắc không ngập -> REJECT
    ("Ngoài ra , mưa lớn xảy ra vào giờ tan tầm người dân đi làm về nên gây ra tình trạng ùn tắc giao thông trên một số tuyến đường Điện Biên Phủ , Xô Viết Nghệ Tĩnh , Ung Văn Khiêm khiến người dân vất vả lưu thông về nhà .", []),

    # Rec 3590: Đã có phường Thủ Đức (cắt 'ở')
    ("Tại một số tuyến đường ở phường Thủ Đức ngập nặng trong mưa , người dân phải dắt bộ xe máy .", [
        ([6, 7, 8], [9, 10], 'NEG'),
        ([6, 7, 8], [17, 18], 'NEG'),
    ]),

    # Rec 3591: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , tình trạng ngập nghiêm trọng còn xảy ra ở nhiều khu vực khác .", [
        ([1], [5, 6], 'NEG'),
    ]),

    # Rec 3592: Đã có phường Gò Vấp -> Cắt bỏ tiền tố nhân tạo
    ("Một số hình ảnh nước ngập nặng ở phường Gò Vấp .", [
        ([8, 9, 10], [5, 6], 'NEG'),
    ]),

    # Rec 3593: Tản mạn quần áo ướt sũng -> REJECT
    ("Tại TP. Hồ Chí Minh , Quần áo ướt sũng , xe thì chết máy .", []),

    # Rec 3594: Trích dẫn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Đi tiếp thì sợ xe chết máy , nhưng không đi thì biết đi đường nào về nhà đây \" , anh Vũ Hoàng Quân , 34 tuổi , nói .", []),

    # Rec 3595: Trích dẫn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Phải chấp nhận chờ nước rút thôi .", []),

    # Rec 3596: Trích dẫn cá nhân -> REJECT
    ("Tại TP. Hồ Chí Minh , \" Đi có công chuyện ngang qua đây , thấy nước lên tưởng là không sâu lắm nên chạy qua , ai ngờ nước ngập vào khiến xe chết máy , đành phải đẩy bộ \" - ông Hồ nói .", []),

    # Rec 3597: Máy bơm chống ngập -> REJECT
    ("Tại TP. Hồ Chí Minh , Đây là tuyến đường trước đó được Công ty cổ phần Tập đoàn công nghiệp Quang Trung lắp đặt \" siêu máy bơm \" hút nước chống ngập công suất bơm lên tới 90 . 000m3 / giờ .", []),

    # Rec 3598: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Công ty TNHH một thành viên thoát nước đô thị cho biết có hơn 43 điểm ngập trong mưa rải điều trên địa bàn TP.", [
        ([1], [19], 'NEG'),
    ]),

    # Rec 3599: Đã có Nguyễn Hữu Cảnh, Lã Xuân Oai
    ("Trong đó ngập nặng nhất là tuyến Nguyễn Hữu Cảnh ( Q. Bình Thạnh ) và Lã Xuân Oai ( Q. 9 ) ngập từ 0 , 4 - 0 , 7 mét .", [
        ([7, 8, 9], [2, 3], 'NEG'),
        ([7, 8, 9], [23], 'NEG'),
        ([16, 17, 18], [2, 3], 'NEG'),
        ([16, 17, 18], [23], 'NEG'),
    ]),

    # Rec 3600: Đã có TP. HCM
    ("Từ khoảng 18 giờ chiều 6 . 8 , một cơn mưa cực to tại TP. HCM đã khiến hàng ngàn người Sài Gòn phải lội giữa \" biển nước \" khi nhiều tuyến đường ngập nặng .", [
        ([15, 16], [28, 29], 'NEG'),
        ([15, 16], [35, 36], 'NEG'),
    ]),
]

def test_triplets():
    flaws = 0
    print(f"Tổng số records kiểm tra: {len(batch36_data)}")
    for idx, (text, triplets) in enumerate(batch36_data, 3501):
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
        print("TẤT CẢ CÁC TRIPLETS CỦA BATCH 36 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!")
    else:
        print(f"TỔNG CỘNG PHÁT HIỆN {flaws} LỖI!")
    return flaws

if __name__ == '__main__':
    flaws = test_triplets()
    if flaws == 0:
        phase3_path = 'data/validate_label/thuan/phase3.txt'
        with open(phase3_path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        base_lines = lines[:3500]
        
        new_batch_lines = []
        for text, triplets in batch36_data:
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
