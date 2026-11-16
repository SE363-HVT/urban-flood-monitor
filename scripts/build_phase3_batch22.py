# -*- coding: utf-8 -*-
"""
Build Phase 3 Batch 22 (Records 2101 - 2200).
Tuân thủ 100% BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md.
"""

batch22_data = [
    # 2101 (Câu hỏi thăm dò điều kiện thời tiết -> NEU)
    (
        "Mưa bao nhiêu mm thì thành phố Hồ Chí Minh sẽ ngập nặng ?",
        [([5, 6, 7, 8, 9], [10, 11, 12], 'NEU')]
    ),
    # 2102
    (
        "* * Không có một con số cố định * * , nhưng thường mưa khoảng * * trên 80 – 100 mm trong vài giờ * * là TP. HCM bắt đầu ngập nặng diện rộng .",
        [([29, 30], [33, 34, 35, 36], 'NEG')]
    ),
    # 2103 (Thủy văn: Triều cường trơ trọi mở rộng in-place triều cường ở TPHCM)
    (
        "Mức ngập còn phụ thuộc nhiều vào triều cường ở TPHCM .",
        [([7, 8, 9, 10], [0, 1], 'NEG')]
    ),
    # 2104
    (
        "- * * Khoảng 40 – 60 mm trong 1 – 2 giờ : * * ngập cục bộ ở các \" điểm đen \" quen thuộc như Nguyễn Hữu Cảnh , Phan Anh , Kinh Dương Vương , khu Thủ Đức cũ .",
        [
            ([28, 29, 30], [16, 17, 18], 'NEG'),
            ([32, 33], [16, 17, 18], 'NEG'),
            ([35, 36, 37], [16, 17, 18], 'NEG'),
            ([39, 40, 41, 42], [16, 17, 18], 'NEG')
        ]
    ),
    # 2105 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nước rút chậm , ngập lan rộng nhiều quận .",
        [([1], [7, 8, 9], 'NEG')]
    ),
    # 2106 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , - * * Trên 150 mm : * * ngập rất nặng , nước sâu 0 , 5 m trở lên ở nhiều nơi .",
        [([1], [12, 13, 14], 'NEG')]
    ),
    # 2107 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Ngoài lượng mưa , còn ba yếu tố làm ngập nặng hơn :",
        [([1], [12, 13, 14], 'NEG')]
    ),
    # 2108 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , - * * Mưa lớn tập trung trong thời gian ngắn * * gây ngập nặng hơn so với cùng lượng mưa rải rác cả ngày .",
        [([1], [17, 18, 19], 'NEG')]
    ),
    # 2109 (Fallback)
    (
        "Tại TPHCM , Vì vậy , khi mưa to trùng giờ triều cường ( thường vào chiều tối các tháng 9 – 12 ) , chỉ khoảng 50 – 60 mm cũng có thể gây ngập nặng .",
        [([1], [35, 36], 'NEG')]
    ),
    # 2110 (Strip giới từ 'tại' theo Pass 5)
    (
        "Ghi nhận đến 20 giờ , tại đường Hồ Học Lãm ( phường An Lạc , TPHCM ) vẫn còn ngập sâu , có nơi hơn 0 , 5m , nhiều người phải dắt bộ vì xe chết máy .",
        [
            ([7, 8, 9, 10], [20, 21], 'NEG'),
            ([7, 8, 9, 10], [36, 37, 38], 'NEG')
        ]
    ),
    # 2111
    (
        "🚨 SÀI GÒN NGẬP LỤT MẤY HÔM NAY CHƯA DỪNG LẠI , SẮP TỚI ĐÓN ĐỢT BÃO TRIỀU CƯỜNG NGẬP DÂNG CAO Ở SÀI GÒN Mưa lớn gặp đúng lúc triều cường , có chỗ nước lên nhanh .",
        [([1, 2], [3, 4], 'NEG')]
    ),
    # 2112 (Strip giới từ 'ở' theo Pass 5)
    (
        "Cơn mưa lớn vào đầu giờ chiều nay khiến nhiều tuyến đường ở TPHCM bị ngập , gây khó khăn cho việc đi lại .",
        [([13], [14, 15], 'NEG')]
    ),
    # 2113 (Strip giới từ 'ở' theo Pass 5)
    (
        "🥺 Ngập lụt ở Sài Gòn những ngày này có lẽ là điều chẳng còn xa lạ .",
        [([4, 5], [1, 2], 'NEG')]
    ),
    # 2114 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Giờ tan tầm , chỉ một cơn mưa lớn cũng đủ khiến nhiều tuyến đường ngập nước .",
        [([1], [18, 19], 'NEG')]
    ),
    # 2115 (Câu bị cắt cụt giữa chừng -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Những trận ngập đến từ nhiều yếu tố , từ mưa lớn , biến đổi khí hậu , triều cư",
        []
    ),
    # 2116 (Bài thơ vè chế nhảm nhí -> REJECT)
    (
        "Dự đoán tình hình mưa Sài Gòn hôm nay : Huỳnh Thúc Kháng ngập tới háng , Trần Đình xu ngập tới khu , Tân Phú ngập tới dzú , Củ Chi ngập tới ti , Vân Đồn , Cát Lái ngập tới . . .",
        []
    ),
    # 2117
    (
        "⛔ ️ Mưa lớn kéo dài ở TPHCM tối 18 . 9 , nhiều đường ngập sâu , nước tràn vào nhà dân Ghi nhận tối 18 . 9 , nhiều tuyến đường ở TPHCM như Lê Văn Việt , Nguyễn Văn Hưởng , Linh Đông , Lý Tế Xuyên , Tô Ngọc Vân . . .",
        [
            ([36, 37, 38], [15, 16], 'NEG'),
            ([40, 41, 42], [15, 16], 'NEG'),
            ([44, 45], [15, 16], 'NEG'),
            ([47, 48, 49], [15, 16], 'NEG'),
            ([51, 52, 53], [15, 16], 'NEG')
        ]
    ),
    # 2118 (Mẩu câu rời rạc cắt cụt -> REJECT)
    (
        "( thuộc khu vực quận Thủ Đức cũ ) bị ngập",
        []
    ),
    # 2119
    (
        "TPHCM : ĐƯỜNG ‘ NGẬP NHƯ SÔNG ’ , Ô TÔ BẤT ĐỘNG , XE MÁY BỊ NƯỚC XÔ NGÃ Tối 18 / 9 , mưa giông xảy ra trên diện rộng tại TPHCM khiến nhiều tuyến đường ngập sâu , giao thông đi lại khó khăn , hàng loạt phương tiện ch * t máy .",
        [([0], [38, 39], 'NEG')]
    ),
    # 2120 (Strip giới từ 'ở' theo Pass 5)
    (
        "Người dân TPHCM bì bõm trên đường ngập trong đêm để về nhà Mưa lớn kéo dài tối 18 / 9 khiến nhiều tuyến đường ở TPHCM ngập sâu , có nơi nước dâng hơn nửa mét , chảy xiết .",
        [([26], [27, 28], 'NEG')]
    ),
    # 2121 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Xíu tan làm xác định ăn trọn combo ướt + kẹt xe , xui xui thì có thêm quả ngập nước 🫠 # Hongsaigon # News",
        [([1], [22, 23], 'NEG')]
    ),
    # 2122
    (
        "Hồ Chí Minh ngập nước , nhiều tuyến đường đi lại khó khăn .",
        [([0, 1, 2], [3, 4], 'NEG')]
    ),
    # 2123 (Strip giới từ 'ở khu vục' theo Pass 5)
    (
        "Kinh hoàng với tình trạng ngập lụt ở khu vục Sài Gòn . . .",
        [([10, 11], [5, 6], 'NEG')]
    ),
    # 2124 (Ý kiến chê bai mỉa mai chung chung -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , vậy mà năm nào cũng tiêu một đống tiền \" chống ngập \"",
        []
    ),
    # 2125
    (
        "🚨 SÀI GÒN TỐI QUA , CON ĐƯỜNG “ HUYẾT MẠCH ” CỦA SÀI GÒN CŨNG HÓA THÀNH SÔNG !",
        [([1, 2], [16, 17, 18], 'NEG')]
    ),
    # 2126
    (
        "🌧 ️ Mưa Sài Gòn một trận là loạt khu vực ngập lụt thấy mà choáng 😭 Dân TP.",
        [([3, 4], [11, 12], 'NEG')]
    ),
    # 2127 (Cắt bỏ tiền tố thừa vì thân bài có Tân Bình)
    (
        "Tình hình hiện tại Tân Bình , … ngập cỡ này , chỗ mấy ní ổn không ?",
        [([4, 5], [8, 9, 10], 'NEG')]
    ),
    # 2128 (Đô thị không ngập -> POS, TPHCM ngập nặng -> NEG)
    (
        "LÝ DO VÌ SAO THE GLOBAL CITY KO NGẬP ❓ Mấy hôm nay mưa lớn + triều cường lên , nhiều địa bàn tại TPHCM ngập nặng .",
        [
            ([4, 5, 6], [7, 8], 'POS'),
            ([24], [25, 26], 'NEG')
        ]
    ),
    # 2129 (Rao vặt tìm người ở ghép -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Thoáng ko ngập , yên tĩnh an ninh , share cc cũng được ạ",
        []
    ),
    # 2130 (Strip giới từ 'ở' theo Pass 5)
    (
        "Sau cơn mưa lớn chiều 23 / 9 , đường ở Thủ Thiêm ngập hơn một ngày , xe chết máy , người ngã nhào Chiều 24 / 9 , đường Lương Định Của ( phường An Khánh ) vẫn ngập sâu , kéo dài hơn 400 m từ vòng xoay Trần Não đến đoạn giao với đường Tố Hữu .",
        [
            ([11, 12], [13], 'NEG'),
            ([30, 31, 32, 33], [40, 41], 'NEG')
        ]
    ),
    # 2131
    (
        "Mưa lớn giờ tan tầm , nhiều tuyến đường TPHCM chìm trong nước Mưa lớn kèm sấm chớp trút xuống nhiều khu vực TPHCM vào giờ tan tầm , khiến nhiều tuyến đường ngập sâu .",
        [([23], [33, 34], 'NEG')]
    ),
    # 2132 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Người dân chật vật về nhà , một số phương tiện chết máy giữa dòng nước .",
        [([1], [14, 15], 'NEG')]
    ),
    # 2133 (Strip giới từ 'tại' theo Pass 5)
    (
        "Cơn mưa lớn kéo dài tại TP. HCM khiến nhiều tuyến đường ngập sâu , giao thông ùn tắc trong giờ tan tầm .",
        [([6, 7], [12, 13], 'NEG')]
    ),
    # 2134 (Strip giới từ 'tại' theo Pass 5)
    (
        "Ghi nhận tại đường D5 ( phường Thạnh Mỹ Tây , TP. HCM ) nước ngập sâu khiến nhiều phương tiện lư",
        [([3, 4], [15, 16], 'NEG')]
    ),
    # 2135 (Strip giới từ 'tại' theo Pass 5)
    (
        "🌧 ️ Chiều ngày 22 / 9 , mưa lớn kéo dài khiến nước dâng nhanh trên nhiều tuyến đường tại TP. HCM , có nơi ngập qua đầu gối người lớn .",
        [([21, 22], [26, 27, 28, 29], 'NEG')]
    ),
    # 2136 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Việc đi lại trong giờ tan tầm gặp nhiều khó khăn , một số xe máy chết máy giữa đường .",
        [([1], [19, 20], 'NEG')]
    ),
    # 2137 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Sau trận mưa lớn , nước ngập , xe di chuyển chậm lúc tan tầm .",
        [([1], [8, 9], 'NEG')]
    ),
    # 2138 (Strip giới từ 'ở' theo Pass 5)
    (
        "Ghi nhận trong cơn mưa chiều tối 22 - 9 , nước thoát không kịp khiến nhiều tuyến đường ở TP. HCM ngập nặng .",
        [([20, 21], [22, 23], 'NEG')]
    ),
    # 2139 (Bà Rịa tỉnh ngoài -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , PHƯỜNG BÀ RỊA ĐẨY MẠNH TUYÊN TRUYỀN CÔNG TÁC PHÒNG , CHỐNG DỊCH BỆNH TRONG MÙA MƯA LŨ , NGẬP LỤT 👉 Mùa mưa bão là điều kiện thuận cho các dịch bệnh bùng phát .",
        []
    ),
    # 2140 (Strip giới từ 'ở' theo Pass 5)
    (
        "Hồ Chí Minh , khiến một số tuyến đường ở phường Hiệp Bình ngập sâu .",
        [([10, 11, 12], [13, 14], 'NEG')]
    ),
    # 2141 (Cắt bỏ tiền tố thừa vì thân bài có giao lộ Linh Đông – Lý Tế Xuyên)
    (
        "Nước từ các tuyến đường dồn về giao lộ Linh Đông – Lý Tế Xuyên chảy mạnh như thác , khiến nhiều người phải dừng xe , chờ nước rút mới có th",
        [([7, 8, 9, 10, 11, 12, 13, 14], [15, 16, 17, 18], 'NEG')]
    ),
    # 2142 (Lái Thiêu, Bình Dương tỉnh ngoài -> REJECT)
    (
        "CHỐNG NGẬP KIỂU MỚI , ĐƯA NƯỚC VÀO NHÀ DÂN LÀ MẶT ĐƯỜNG SẼ HẾT NGẬP Theo thông tin từ Báo Tiền Phong ngày 10 / 09 / 2026 , dự án nâng cấp Quốc lộ 13 qua phường Lái Thiêu và Bình Hòa tại TP. HCM đang tiến hành nâng nền đường cao hơ",
        []
    ),
    # 2143 (Dính HTML rác -> REJECT)
    (
        "Hàng loạt điểm ngập xuất hiện , nhiều trạm bơm được vận hành < / a > & nbsp ; & nbsp ; < font color = \" # 6f6f6f \" > Facebook < / font >",
        []
    ),
    # 2144
    (
        "TP. HCM mưa lớn đúng giờ tan tầm khiến nhiều tuyến đường ngập sâu Đoạn Ung Văn Khiêm - Tân Cảng ngập hơn 30 phút .",
        [
            ([0, 1], [12, 13], 'NEG'),
            ([15, 16, 17, 18, 19, 20], [21, 22, 23, 24], 'NEG')
        ]
    ),
    # 2145 (Fallback chuẩn hóa - Opinion là 'ngập')
    (
        "Tại TPHCM , Hiện tại vẫn mưa lớn và đoạn ngập chưa có dấu hiệu rút # znews",
        [([1], [10], 'NEG')]
    ),
    # 2146 (Tiêu đề bài viết hỏi thăm dò chung không có ngập cụ thể -> REJECT)
    (
        "CHIỀU NAY NẾU MƯA LỚN , NGƯỜI DÂN TP. HCM CẦN LƯU Ý NHỮNG ĐOẠN ĐƯỜNG DỄ NGẬP NƯỚC NÀO ?",
        []
    ),
    # 2147 (Strip giới từ 'Tại' theo Pass 5)
    (
        "Tại TP. HCM còn 50 điểm ngập nặng từ 30cm trở lên và kéo dài trong 30 phút khi mưa lớn , bên cạnh đó còn rất nhiều điểm ngập khác với tình tr",
        [([1, 2], [6, 7], 'NEG')]
    ),
    # 2148 (Có tên đường cụ thể nên không gán Fallback TP.HCM theo Pass 9)
    (
        "Đường Bùi Viện , D5 , TP. HCM ngập nước mênh mông sau 1 giờ mưa lớn",
        [
            ([0, 1, 2], [8, 9, 10, 11], 'NEG'),
            ([4], [8, 9, 10, 11], 'NEG')
        ]
    ),
    # 2149
    (
        "Mưa lớn giờ cao điểm tại TP. HCM : Nhiều tuyến đường ngập sâu , giao thông cầu vượt Hàng Xanh ùn ứ Các con đường ngập kinh điển như Đường ngập nặng như đường Quốc Hương , Xuân Thủy ( phường An Khánh ) , đường R12 ( phường Sài Gòn ) , đường",
        [
            ([34, 35, 36], [31, 32], 'NEG'),
            ([38, 39], [31, 32], 'NEG'),
            ([46, 47], [31, 32], 'NEG')
        ]
    ),
    # 2150 (Rạch Dừa thuộc TP Vũng Tàu, tỉnh Bà Rịa Vũng Tàu -> REJECT)
    (
        "Ba thập kỷ qua , hơn 300 hộ dân tại hẻm 290 Nguyễn Hữu Cảnh , phường Rạch Dừa , TPHCM phải sống chung với cảnh ngập úng mỗi khi mùa mưa đến .",
        []
    ),
    # 2151 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nước tràn vào nhà , đường sá biến thành sông , việc đi lại , sinh hoạt của người dân bị đảo lộn .",
        [
            ([1], [3, 4, 5, 6], 'NEG'),
            ([1], [10, 11, 12], 'NEG')
        ]
    ),
    # 2152
    (
        "TP. HCM : ĐƯỜNG PHAN HUY ÍCH NGẬP SÂU KHIẾN XE C . H . Ế . T MÁY LÚC NỬA ĐÊM Chi tiết vụ việc 👇 • Mưa lớn suốt chiều tối 22 - 9 kết hợp triều cường khiến đường Phan Huy Ích ngập sâu hơn nửa bánh xe .",
        [([41, 42, 43, 44], [45, 46], 'NEG')]
    ),
    # 2153 (Cao lỗ hay ngập -> NEG, Phạm Thế Hiển câu hỏi thăm dò -> NEU)
    (
        "Dạ mn cho e hỏi bthg e đi Tạ Quang Bửu qua Cao lỗ nma mưa hay ngập chỗ Aeon vậy e đi vòng qua Phạm Thế Hiển đỡ ngập ko ạ .",
        [
            ([12, 13], [16, 17], 'NEG'),
            ([25, 26, 27], [28, 29, 30], 'NEU')
        ]
    ),
    # 2154
    (
        "TP. Hcm Mưa Trắng Trời : Quốc Lộ 50 Ngập Nặng , Nhiều Tuyến Đường Chìm Trong Nước !",
        [([6, 7, 8], [9, 10], 'NEG')]
    ),
    # 2155
    (
        "Mưa lớn tại TP. HCM tối 21 / 9 khiến một số khu vực Bình Hưng , Bình Chánh cũ , Quận 8 cũ và Quốc lộ 50 xuất hiện ngập , gây khó khăn cho người tham gia giao thông .",
        [
            ([14, 15], [28, 29, 30], 'NEG'),
            ([25, 26, 27], [28, 29, 30], 'NEG')
        ]
    ),
    # 2156
    (
        "SỐC : ĐƯỜNG PHỐ TPHCM NHƯ THÁC NƯỚC SAU MƯA LỚN Mưa lớn và sấm sét đổ bộ khắp TPHCM khiến nhiều tuyến đường ngập sâu , nước chảy xiết như thác , xe máy chế . t máy phải dắt bộ .",
        [([19], [24, 25], 'NEG')]
    ),
    # 2157 (Câu bị cắt cụt lỡ dở -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Đường Linh Đông – Lý Tế Xuyên ngập nặng buộc người dâ",
        []
    ),
    # 2158 (Hashtag meme chung chung -> REJECT)
    (
        "Anh em chọn hướng tránh ngập TPHCM # canhbaongaplut # canhbaoketxengaymua # ngapquan2 # ngapduongtrannao # canhbaogiaothong # giaothongantoan",
        []
    ),
    # 2159 (Lái Thiêu, Bình Dương tỉnh ngoài -> REJECT)
    (
        "Nâng nền Quốc lộ 13 , nhà dân thấp gần 1m , nắng bụi mưa ngập Đoạn Quốc lộ 13 từ trạm thu phí Lái Thiêu đến cầu Vĩnh Bình đang được nâng nền , có nơi cao hơn nhà dân gần 1m .",
        []
    ),
    # 2160 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Trời nắng thì bụi mù , mưa xuống bùn đất và nước tràn vào nhà dân",
        [([1], [14, 15, 16, 17, 18], 'NEG')]
    ),
    # 2161
    (
        "TP. HCM Mưa Lớn : Nhà Bè , Bình Tân Ngập Nước , Tỉnh Lộ 10 Ùn Ứ Mưa lớn tại TP. HCM chiều 22 / 9 khiến nhiều tuyến đường ngập nước , giao thông ùn ứ .",
        [
            ([5, 6], [10, 11], 'NEG'),
            ([8, 9], [10, 11], 'NEG')
        ]
    ),
    # 2162 (Strip giới từ 'trên' theo Pass 5)
    (
        "Xem clip mưa ngập trên đường Mã Lò , phường Bình Trị Đông :",
        [([5, 6, 7], [2, 3], 'NEG')]
    ),
    # 2163 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , “ Nước dâng ngập bánh xe khiến xe chết máy .",
        [([1], [4, 5, 6, 7, 8], 'NEG')]
    ),
    # 2164 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Hàng loạt xe chết máy phải dắt bộ .",
        [([1], [5, 6, 7, 8, 9, 10], 'NEG')]
    ),
    # 2165 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , “ Mưa nhỏ thì ngập nửa bánh xe , mưa lớn thì hơn cả bánh xe , nhiều người phải dắt bộ chứ không dám chạy xe qua đây .",
        [([1], [7, 8, 9, 10], 'NEG')]
    ),
    # 2166 (Chỉ kẹt xe ùn ứ, không nhắc ngập -> REJECT)
    (
        "Mưa đúng thời điểm giờ tan tầm , người dân phải chịu cảnh ùn ứ do kẹt xe tại khu vực cầu vượt Hàng Xanh .",
        []
    ),
    # 2167 (Fallback chuẩn hóa - Chống ngập triệt để -> POS)
    (
        "Tại TPHCM , Công trình có tổng mức đầu tư gần 7 . 800 tỷ đồng từ nguồn vốn ngân sách thành phố , giúp giải quyết tình trạng ô nhiễm , sạt lở và chống ngập triệt để cho khu vực phía Nam .",
        [([1], [35, 36, 37, 38], 'POS')]
    ),
    # 2168
    (
        "Tại phường An Lạc ( TPHCM ) mưa lớn xuất hiện từ 15 giờ 30 , ghi nhận đến 20 giờ cùng ngày , một số vị trí trên đường Hồ Học Lãm , An Dương Vương vẫn còn ngập sâu , có nơi trên 0 , 5m , nhiều người dắt bộ vì xe chết máy .",
        [
            ([29, 30, 31, 32], [39, 40], 'NEG'),
            ([34, 35, 36], [39, 40], 'NEG')
        ]
    ),
    # 2169
    (
        "22h đêm , xe chết máy la liệt trên đường Phan Huy Ích , người dân mệt mỏi dắt xe lội nước về nhà - Tuổi Trẻ",
        [([9, 10, 11, 12], [3, 4, 5, 6, 7], 'NEG')]
    ),
    # 2170 (Dự án chống ngập -> POS)
    (
        "TP. HCM duyệt dự án chống ngập gần 7 . 700 tỉ đồng khu vực phía tây - Báo Thanh Niên",
        [([0, 1], [5, 6], 'POS')]
    ),
    # 2171
    (
        "Mưa lớn kéo dài vào giờ tan tầm khiến nhiều tuyến đường TP HCM ngập sâu , người dân phải lội giữa dòng nước đổ như thác để về nhà , tối 22 / 9 .",
        [([12, 13], [14, 15], 'NEG')]
    ),
    # 2172 (Cắt bỏ tiền tố thừa vì thân bài có khu đô thị An Khánh)
    (
        "Nhiều ô tô , xe máy chết máy , mắc kẹt giữa những đoạn đường ngập sâu tại khu đô thị An Khánh",
        [([18, 19, 20, 21, 22], [15, 16], 'NEG')]
    ),
    # 2173 (Caption ngắn chung chung -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Hành trình đi làm mùa ngập ngày 3 .",
        []
    ),
    # 2174 (Hashtag chứa Hà Nội mưa tỉnh ngoài -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Qua được kiếp nạn ngập để đến với kiếp nạn tắc đường 😭 # minhthuynt # muangap # hanoimua # ngaplut # viral",
        []
    ),
    # 2175 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Anh em nào có đi ngang những đoạn hay ngập chiều nay lưu ý nha",
        [([1], [11, 12], 'NEG')]
    ),
    # 2176 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Xe Ngập Nước Rồi Bà Con Ạ .",
        [([1], [4, 5], 'NEG')]
    ),
    # 2177 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Mùa ngập lụt tới rồi , các bác lưu ý kẻo lại hỏi sao nước biển lại mặn 🥲 🥲",
        [([1], [4, 5], 'NEG')]
    ),
    # 2178 (Đèo Mẹ Bồng Con thuộc Đồng Nai tỉnh ngoài -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , QUỐC LỘ 1A - KHU VỰC ĐÈO MẸ BỒNG CON ĐANG NGẬP SÂU TRONG BIỂN NƯỚC !",
        []
    ),
    # 2179 (Đèo Mẹ Bồng Con, Dầu Giây thuộc Đồng Nai tỉnh ngoài -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Mưa lớn liên tục làm nước đổ về như trút nước , biến đoạn đường ngay khu vực đèo Mẹ Bồng Con ( An Lộc - Dầu Giây ) thành sông rồi mọi người ơi !",
        []
    ),
    # 2180 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nước ngập sâu , đục ngầu , dòng chảy lại xiết khiến các phương tiện di chuyển qua đây cực kỳ khó khăn và nguy hiểm .",
        [([1], [3, 4, 5], 'NEG')]
    ),
    # 2181 (Không có vị ngữ ngập nước -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Nhìn mấy chiếc xe máy phải chật vật dắt bộ mà thấy thương quá .",
        []
    ),
    # 2182 (Fallback chuẩn hóa - Câu hỏi thăm dò -> NEU)
    (
        "Tại TPHCM , Có bị ngập úng hay gặp khó khăn gì không ?",
        [([1], [3, 4, 5, 6], 'NEU')]
    ),
    # 2183 (Thủy văn: Triều cường trơ trọi mở rộng in-place triều cường ở TPHCM)
    (
        "Mấy ngày mưa triều cường ở TPHCM ngập nước .",
        [([3, 4, 5, 6], [7, 8], 'NEG')]
    ),
    # 2184
    (
        "Sài Gòn dạo này mưa nhiều đến mức ngập lụt hết toàn thành phố .",
        [([0, 1], [8, 9], 'NEG')]
    ),
    # 2185 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nhiều nơi hôm nay lại ngập nặng , xe chết máy hàng loạt cho coi 😭",
        [
            ([1], [8, 9], 'NEG'),
            ([1], [11, 12, 13, 14, 15], 'NEG')
        ]
    ),
    # 2186 (Cắt bỏ tiền tố thừa vì thân bài có Hồ Chí Minh)
    (
        "Hồ Chí Minh ngập cục bộ , các phương tiện di chuyển khó khăn .",
        [([0, 1, 2], [3, 4, 5], 'NEG')]
    ),
    # 2187 (ĐBSCL tỉnh ngoài -> REJECT)
    (
        "🌊 TRIỀU CƯỜNG DÂNG CAO , NGUY CƠ NGẬP LỤT ĐBSCL",
        []
    ),
    # 2188 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , NGẬP CỠ NÀY THÌ KHACH KHỨA GÌ NỮA CHỊ EM ƠI 🥲 🥲 🥲 thôi off sớm đóng cửa ngủ bớt đau lòng # nuocngap # ngapnuoc",
        [([1], [3, 4, 5], 'NEG')]
    ),
    # 2189 (Đường 25c Vĩnh Thanh thuộc Nhơn Trạch, Đồng Nai tỉnh ngoài -> REJECT)
    (
        "Những vị khách đến nhà tiếp tế nước ngập đường 25c Vĩnh thanh .",
        []
    ),
    # 2190
    (
        "Mưa lớn kéo dài những ngày qua khiến nhiều tuyến đường TP. HCM ngập sâu , người dân chật vật di chuyển",
        [([11, 12], [13, 14], 'NEG')]
    ),
    # 2191 (Caption meme khoe xe Jeep -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , ngập nhưng Jeep lại rất thích ngập 🤣",
        []
    ),
    # 2192 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Hồ điều hòa gần 12ha ngay cạnh làm xong vẫn bị ngập 🤔",
        [([1], [12, 13, 14], 'NEG')]
    ),
    # 2193 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , mưa gió ngập lụt mà cũng đòi đi cho bằng được",
        [([1], [5, 6], 'NEG')]
    ),
    # 2194 (Fallback chuẩn hóa - Câu hỏi thăm dò -> NEU)
    (
        "Tại TPHCM , Tình hình ngập lụt chỗ các bác sao rồi ạ 🥹",
        [([1], [3, 4, 5, 6], 'NEU')]
    ),
    # 2195
    (
        "Khi Sài Gòn mất điện kèm luôn combo ngập k lối thoát … .",
        [([1, 2], [8, 9, 10, 11], 'NEG')]
    ),
    # 2196 (Cắt bỏ tiền tố thừa vì thân bài có SG)
    (
        "SG mưa lớn ngập đường - xe máy đi qua làn ô tô kẹt lại thêm kẹt",
        [([0], [3, 4], 'NEG')]
    ),
    # 2197
    (
        "Mưa lớn trưa 23 / 9 khiến phố Tây Bùi Viện cùng nhiều tuyến đường trung tâm TP. HCM ngập sâu .",
        [
            ([7, 8, 9, 10], [19, 20], 'NEG'),
            ([17, 18], [19, 20], 'NEG')
        ]
    ),
    # 2198 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Du khách tháo giày lội nước , hàng quán tất bật chống ngập giữa khu phố du lịch nổi tiếng .",
        [([1], [7, 8], 'NEG')]
    ),
    # 2199 (Bãi giữa sông Hồng thuộc Hà Nội tỉnh ngoài -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Bãi giữa HCM ngập rồi ae ơi",
        []
    ),
    # 2200
    (
        "Sài Gòn Nước ngập mênh mông",
        [([0, 1], [2, 3, 4, 5], 'NEG')]
    ),
]

def format_line(text, triplets):
    formatted_triplets = []
    for asp, opn, pol in triplets:
        formatted_triplets.append(f"({asp}, {opn}, '{pol}')")
    triplets_str = "[" + ", ".join(formatted_triplets) + "]"
    return f"{text}####{triplets_str}\n"

if __name__ == '__main__':
    assert len(batch22_data) == 100, f"Expected 100 records, got {len(batch22_data)}"
    
    phase3_path = "data/validate_label/thuan/phase3.txt"
    with open(phase3_path, "r", encoding="utf-8") as f:
        lines = [l for l in f.readlines() if l.strip()]
    
    base_2100 = lines[:2100]
    assert len(base_2100) == 2100, f"Expected 2100 existing lines, found {len(base_2100)}"
    
    new_lines = [format_line(t, tr) for t, tr in batch22_data]
    
    all_lines = base_2100 + new_lines
    with open(phase3_path, "w", encoding="utf-8") as f:
        f.writelines(all_lines)
        
    print(f"Successfully updated {len(all_lines)} lines to {phase3_path}!")
