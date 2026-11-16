# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn chuẩn hóa cho Phase 3 - Batch 32 (Records 3101 - 3200).
Tuân thủ 100% tài liệu BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md.
"""

batch32_data = [
    # Rec 3101: Đã có TP. HCM
    ("Nhiều tuyến đường tại TP. HCM bị ngập sâu sau cơn mưa lớn .", [
        ([4, 5], [7, 8], 'NEG'),
    ]),

    # Rec 3102: Đã có TP Thủ Đức
    ("Mưa lớn kèm theo triều cường dâng cao khiến nhiều tuyến đường ở khu vực TP Thủ Đức ngập nặng .", [
        ([14, 15, 16], [17, 18], 'NEG'),
    ]),

    # Rec 3103: PR khu nhà giàu + cắt cụt đuôi câu -> REJECT
    ("🏙 ️ THẢO ĐIỀN - “ KHU NHÀ GIÀU ” VẪN ĐẮT ĐỎ DÙ NGẬP NƯỚC 🔸 Thảo Điền ( TP Thủ Đức ) là khu dân cư cao cấp được mệnh danh “ khu nhà giàu ” nhờ hệ thống tiện ích đầy đủ , không gian sống yên tĩnh , nhiều trường quốc tế và cộng đồng cư dân thu nhậ", []),

    # Rec 3104: Đã có Thảo Điền, quận 2
    ("Đây là khu vực Thảo Điền , quận 2 - nơi được cho là phố nhà giàu nhưng vẫn không thể tránh khỏi chuyện ngập lụt .", [
        ([4, 5], [24, 25], 'NEG'),
        ([7, 8], [24, 25], 'NEG'),
    ]),

    # Rec 3105: Hồ sơ thiết kế kiến trúc cắt cụt đuôi -> REJECT
    ("HCM Chủ trì thiết kế : Nguyễn Hoàng Mạnh Thiết kế ý tưởng : Nguyễn Quốc Long , Trần Hữu Dũng Thiết kế kỹ thuật : Bùi Hoàng Bảo , Lê Hồ Ngọc Thảo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - Chúng tôi gặp nhau vào một buổi chiều Sài Gòn ngập", []),

    # Rec 3106: Đã có THỦ ĐỨC, Đường 11, phường Linh Xuân
    ("‼ ️ THỦ ĐỨC - Đường 11 , phường Linh Xuân ( Truông Tre ) ngập sâu rồi .", [
        ([2, 3], [15, 16], 'NEG'),
        ([5, 6], [15, 16], 'NEG'),
        ([8, 9, 10], [15, 16], 'NEG'),
    ]),

    # Rec 3107: Miêu tả đợi nước rút -> REJECT
    ("Tại TP. Hồ Chí Minh , Hiện người dân đã dạt ra 2 bên vỉa hè đứng đợi nước rút .", []),

    # Rec 3108: Đã có CHỢ THỦ ĐỨC, TPHCM, đường Phạm Văn Đồng, TP Thủ Đức
    ("MƯA LỚN TRÚT XUỐNG KHU VỰC CHỢ THỦ ĐỨC TPHCM KHIẾN ĐƯỜNG NGẬP LÊNH LÁNG ⛈ ️ Chiều 20 / 5 , cơn mưa trắng trời trên đường Phạm Văn Đồng ( TP Thủ Đức ) khiến nhiều phương tiện giao thông di chuyển gặp khó khăn .", [
        ([6, 7, 8], [12, 13, 14], 'NEG'),
        ([27, 28, 29, 30], [42, 43, 44, 45, 46], 'NEG'),
        ([32, 33, 34], [42, 43, 44, 45, 46], 'NEG'),
    ]),

    # Rec 3109: Video URL + cắt cụt đuôi câu -> REJECT
    ("Video : https : / / tuoitre . vn / video / xem - nuoc - phun - nhu - voi - rong - o - khu - cho - thu - duc - khi - mua - lon - ma - khong - khoi - nhoi - long - 161443 . htm Chiều 20 - 5 , mưa lớn như trút xuống khu vực chợ Thủ Đức , TP Thủ Đức , TP. HCM khiến đường sá ngập lênh láng , cống thoát nư", []),

    # Rec 3110: Đã có Thạnh Xuân 21, Tô Ngọc Vân
    ("Ngập nước sâu tại đầu Thạnh Xuân 21 , giáp Tô Ngọc Vân nè .", [
        ([5, 6, 7], [0, 1, 2], 'NEG'),
        ([10, 11, 12], [0, 1, 2], 'NEG'),
    ]),

    # Rec 3111: Đã có Tô Ngọc Vân, chợ Thạnh Xuân
    ("Đoạn Tô Ngọc Vân ra chợ Thạnh Xuân cũng có 2 điểm ngập sâu , nhiều xe chết máy .", [
        ([1, 2, 3], [12, 13], 'NEG'),
        ([1, 2, 3], [17, 18], 'NEG'),
        ([5, 6, 7], [12, 13], 'NEG'),
        ([5, 6, 7], [17, 18], 'NEG'),
    ]),

    # Rec 3112: Đã có đường Linh Đông, Tô Ngọc Vân, Thủ Đức
    ("‼ ️ Ngập nặng , nước chảy như thác trên đường Linh Đông , đoạn giao Tô Ngọc Vân , Thủ Đức cũ 😢 Mong mọi người về nhà bình an 🍀", [
        ([10, 11, 12], [2, 3], 'NEG'),
        ([10, 11, 12], [5, 6, 7, 8], 'NEG'),
        ([16, 17, 18], [2, 3], 'NEG'),
        ([20, 21], [2, 3], 'NEG'),
    ]),

    # Rec 3113: Quảng cáo Buffet hải sản -> REJECT
    ("BUFFET NGẬP HẢI SẢN CUA , GHẸ , BỀ BỀ TƯƠI CHỈ hơn 400K - đông chấn động khu Lương Định Của Quầy line nóng hổi đủ Hải Sản - Các món Âu - Á hơn 200 món cơ , tui không đếm hết mời bác nào qua kiểm chứng nhé nhưng signature ở đây là buffet hả", []),

    # Rec 3114: Đã có Lê Văn Thọ, cắt tiền tố thừa
    ("Lê Văn Thọ đang ngập như thế nào rồi hen 😌 - - - - - - # ToiladanGoVap", [
        ([0, 1, 2], [4], 'NEG'),
    ]),

    # Rec 3115: Chậu cây cảnh ngập kho -> REJECT
    ("Tại TP. Hồ Chí Minh , 👩 Chậu về ngập kho rồi các bác ơi !", []),

    # Rec 3116: Đã có Lê Đức Thọ, Lê Văn Thọ
    ("Mình chỉ biết Lê Đức Thọ ngập nguyên bánh xe , Lê Văn Thọ ngập nửa bánh xe .", [
        ([3, 4, 5], [6, 7, 8, 9], 'NEG'),
        ([11, 12, 13], [14, 15, 16, 17], 'NEG'),
    ]),

    # Rec 3117: Đã có Đường Lê Đức Thọ
    ("Đường Lê Đức Thọ xe chết máy cỡ này .", [
        ([0, 1, 2, 3], [5, 6], 'NEG'),
    ]),

    # Rec 3118: Đã có Gò Vấp, cắt tiền tố thừa
    ("Bão số 9 suy yếu thành áp thấp , Gò Vấp hiện đang mưa rất to và ngập lụt nhiều nơi .", [
        ([9, 10], [17, 18], 'NEG'),
    ]),

    # Rec 3119: Đã có TPHCM
    ("ĐƯỜNG PHỐ TPHCM MÊNH MÔNG NƯỚC SAU TRẬN MƯA LỚN KÈM DÔNG SÉT MẠNH 🌧 ️ Chiều tối 7 / 5 , nhiều nơi ở TPHCM xuất hiện mưa lớn trái mùa kèm hiện tượng dông sét mạnh .", [
        ([2], [3, 4, 5], 'NEG'),
        ([23], [3, 4, 5], 'NEG'),
    ]),

    # Rec 3120: Cắt cụt đuôi câu không có dấu chấm -> REJECT
    ("Tại TP. Hồ Chí Minh , Mưa kéo dài hơn 1 giờ khiến nước thoát không kịp gây ngập nặng", []),

    # Rec 3121: Đã có chợ An Nhơn
    ("Khúc chợ An Nhơn ngập dữ lắm , xe tắt máy nhiều , mọi người né đường này nhé .", [
        ([1, 2, 3], [4, 5, 6], 'NEG'),
        ([1, 2, 3], [9, 10], 'NEG'),
    ]),

    # Rec 3122: Bóc phốt ô tô cũ thủy kích -> REJECT
    ("PHỐT : Lắm Ô TÔ Cũ Sài Gòn Bán Xe NGẬP NƯỚC !", []),

    # Rec 3123: Kế hoạch giải pháp tương lai của thành phố -> REJECT
    ("TP. HCM CHỦ ĐỘNG TRIỂN KHAI NHIỀU PHƯƠNG ÁN , GIẢI PHÁP CHỐNG NGẬP TPHCM và cả khu vực Nam bộ đã bước vào mùa mưa .", []),

    # Rec 3124: Tuyến đường Hà Nội (Võ Chí Công, Nhật Tân) -> REJECT tỉnh ngoài
    ("Đường Võ Chí Công từ cầu Nhật Tân đến ngã tư Nguyễn Hoàng Tôn hiện tại giao thông thưa vắng , rất ít phương tiện di chuyển qua do đoạn qua Lotte cả 2 chiều vẫn ngập sâu .", []),

    # Rec 3125: Tranh chấp nước thải chung cư Thạnh Lộc -> REJECT
    ("Tại TP. Hồ Chí Minh , 🚨 QUẬN 12 : HẺM NGẬP QUANH NĂM DO NƯỚC THẢI CỦA CHUNG CƯ 👇 Nước thải sinh hoạt từ chung cư Thạnh Lộc phía trước hẻm xả thẳng xuống kênh , làm cho nước kênh tràn vào hẻm , có khi tràn vào nhà dân .", []),

    # Rec 3126: Đã có phường Tam Bình, TP Thủ Đức, TPHCM
    ("Người dân ở khu phố 5 , phường Tam Bình , TP Thủ Đức ( TPHCM ) phản ánh về việc ngập sâu kéo dài gần một năm nay # phuongnamhomnay # toancanh24h # vtv9 # news # tintuc", [
        ([7, 8, 9], [21, 22], 'NEG'),
        ([11, 12, 13], [21, 22], 'NEG'),
        ([15], [21, 22], 'NEG'),
    ]),

    # Rec 3127: Bình Dương (Thủ Dầu Một) -> REJECT tỉnh ngoài
    ("Trung tâm Bình Dương ngay lúc này 😟 Triều cường dâng cao , loạt tuyến đường như Cách Mạng Tháng Tám ( cầu ông Đành ) , Ngô Quyền ( xuống Bạch Đằng ) và chợ Thủ Dầu Một ngập nặng nhiều nơi .", []),

    # Rec 3128: Cắt cụt đuôi câu 'cho an toàn ,' -> REJECT
    ("Tại TP. Hồ Chí Minh , Mọi người hạn chế lưu thông qua vùng ngập cho an toàn ,", []),

    # Rec 3129: Đã có TPHCM
    ("NHIỀU TUYẾN ĐƯỜNG Ở TPHCM LẠI NGẬP NHƯ SÔNG SAU TRẬN MƯA KÉO DÀI 1 GIỜ 😰 Lúc 16h ngày 19 / 10 , mưa giông lớn trút xuống khu vực phía Tây Bắc TPHCM .", [
        ([4], [6, 7, 8], 'NEG'),
        ([28], [6, 7, 8], 'NEG'),
    ]),

    # Rec 3130: Đã có TPHCM
    ("Sau cơn mưa lớn kéo dài gần 1 giờ đồng hồ vào chiều 13 / 7 , nhiều tuyến đường trung tâm của TPHCM đã bị ngập nặng .", [
        ([21], [23, 24, 25], 'NEG'),
    ]),

    # Rec 3131: Dự báo đỉnh triều tương lai -> NEU (Pass 8)
    ("Theo Đài Khí tượng Thủy văn khu vực Nam bộ , đỉnh triều cao nhất đợt này tại TPHCM có khả năng xuất hiện vào ngày 19 - 21 / 10 ( tức 17 - 19 tháng Chín Âm lịch ) .", [
        ([15], [16, 17, 18, 19, 20], 'NEU'),
    ]),

    # Rec 3132: Dĩ An (Bình Dương) -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Nhiều nhà dân đã bị ngập nặng sau cơn mưa lớn sáng nay ở TP Dĩ An .", []),

    # Rec 3133: Dĩ An (Bình Dương) -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , quốc lộ 1K , khu vực Châu Thới tối nay Ngập mênh mông luôn , hiện CSGT đang điều tiết Tôi là dân Dĩ An TÔI LÀ DÂN DĨ AN ✔ ️", []),

    # Rec 3134: Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Bình Dương ❌ Khẩn trương đưa người dân ra khỏi nơi bị ngập sâu , nguy hiểm Sáng nay ngày 10 / 5 , trận mưa lớn kéo dài đã gây ngập cục bộ tại nhiều khu vực trên địa bàn Tp Dĩ An .", []),

    # Rec 3135: Châu Thới, Dĩ An + cắt cụt đuôi 'và' -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Một số khu vực bị ngập nặng , đặc biệt là khu vực Châu Thới , suối Lồ Ồ , và", []),

    # Rec 3136: Dĩ An (Bình Dương) -> REJECT tỉnh ngoài
    ("‼ ️ DĨ AN - Nhiều tuyến đường đã ngập Hiện tại đường Nguyễn Tri Phương đang ngập sâu , có đoạn nước chảy như thác , bà con hạn chế đi vào đây .", []),

    # Rec 3137: Chờ nước rút -> REJECT
    ("Tại TP. Hồ Chí Minh , Các xe đã dạt hết lên vỉa hè đứng đợi nước rút .", []),

    # Rec 3138: Thân câu 'nước ngập vô nhà...', Fallback 'Tại TPHCM , '
    ("Tại TPHCM , nước ngập vô nhà luôn rồi nha Báo cáo tình hình chỗ mọi người sao rồi Cảm ơn bạn Võ H . Nam đã gửi tin", [
        ([1], [3, 4, 5, 6], 'NEG'),
    ]),

    # Rec 3139: Hoa bằng lăng tím (ẩn dụ) -> REJECT
    ("Tại TP. Hồ Chí Minh , con đường ngập hoa bằng lăng tím > > > đố bà con biết đường nào nha .", []),

    # Rec 3140: Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , BÌNH DƯƠNG : CÁC CHIẾN SĨ KHẨN TRƯƠNG DI DỜI NGƯỜI DÂN RA KHỎI NHỮNG NƠI NGẬP SÂU ‼ ️ Sáng nay ngày 10 / 5 , trận mưa lớn kéo dài đã gây ngập cục bộ tại nhiều khu vực trên địa bàn Tp Dĩ An .", []),

    # Rec 3141: Cắt cụt đuôi câu 'khu v' -> REJECT
    ("Tại TP. Hồ Chí Minh , Một số khu vực bị ngập nặng , đặc biệt là khu v", []),

    # Rec 3142: Bình Dương -> REJECT tỉnh ngoài
    ("🔥 Bình Dương : Mưa lớn cuốn trôi xe bán tải , nữ tài xế ra đi trong cống thoát nước 😥 😥 😥 Tối 13 / 9 , một phụ nữ điều khiển xe ô tô trên đường đang bị ngập nước trong cơn mưa lớn ở Bình Dương và bị nước cuốn trôi .", []),

    # Rec 3143: Bình Dương -> REJECT tỉnh ngoài
    ("Cơn mưa lớn đổ xuống cuối chiều nay khiến nhiều tuyến đường ở Bình Dương ngập sâu , xe máy bị nước cuốn , cây xanh gãy đổ . . .", []),

    # Rec 3144: Xưởng phế liệu ngập biển lửa ở Bình Dương -> REJECT
    ("❌ Xưởng phế liệu ngập trong biển lửa ở Dĩ An , Bình Dương Tối nay 27 / 3 , xưởng phế liệu trên đường Nguyễn Thị Tươi , Tân Bình , TP.", []),

    # Rec 3145: Ngập biển lửa ở Bình Dương -> REJECT
    ("Tại TP. Hồ Chí Minh , Dĩ An , tỉnh Bình Dương bỗng bốt cháy và nhanh chóng ngập trong biển lửa .", []),

    # Rec 3146: Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Cơn mưa lớn khiến nhiều tuyến đường tại Bình Dương ngập sâu .", []),

    # Rec 3147: Chờ nước rút -> REJECT
    ("Tại TP. Hồ Chí Minh , phương tiện lưu thông chết máy , người dân chờ nước rút mới về nhà .", []),

    # Rec 3148: Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Tối 13 / 9 , một phụ nữ điều khiển xe ô tô trên đường đang bị ngập nước trong cơn mưa lớn ở Bình Dương và bị nước cuốn trôi .", []),

    # Rec 3149: Thuận An, Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Thuận An , Bình Dương cứ tưởng Vũng Tàu 😟 😟 Ngay lúc này , đêm 7 / 11 , thuỷ triều dâng làm ngập 1 đoạn Cách Mạng Tháng Tám ( đoạn Cầu Ngang , Hưng Định cũ ) Bà con tay ga , gầm thấp lưu ý không cố đi qua vùng ngập , các phương tiện muốn an toàn có t", []),

    # Rec 3150: Thuận An, Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , ❌ Đoạn Lotte và Cầu Ông Bố ( QL13 , Thuận An , Bình Dương ) nước vẫn còn ngập khá cao , kẹt xe kéo dài .", []),

    # Rec 3151: Thuận An, Thủ Dầu Một (Bình Dương) -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Bà con hạ du Thuận An , Thủ Dầu Một ( Bình Dương cũ ) hay ven sông SG đề phòng ngập ❗", []),

    # Rec 3152: Thuận An, Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Thuận An , Bình Dương , khổ sở với ngập úng kéo dài 4 năm .", []),

    # Rec 3153: Câu chung chung không có địa danh cụ thể -> REJECT
    ("Tại TP. Hồ Chí Minh , Tình trạng ngập úng diễn ra thường xuyên , kéo dài nhiều ngày .", []),

    # Rec 3154: Thuận An, Bình Dương -> REJECT tỉnh ngoài
    ("Ngay lúc này 🆘 Thuỷ triều dâng , làm nước ngập trên đường CMT8 , đoạn Cầu Ngang , Hưng định , Thuận An , Bình Dương cũ .", []),

    # Rec 3155: Câu mồ côi -> REJECT
    ("Tại TP. Hồ Chí Minh , Nước ngập dâng lên khá cao .", []),

    # Rec 3156: Thủ Dầu Một, Bình Dương + cắt cụt đuôi câu -> REJECT tỉnh ngoài
    ("Đường Trần Tử Bình x Lý Thường Kiệt , Thủ Dầu Một , Bình Dương ngay lúc này 😥 😥 😥 - - - - Đợt triều cường dâng vào giữa tháng 10 , mực nước dâng ở khu vực Thủ Dầu Một đo được khoảng gần 1m9 ( kỷ lục ) Nhưng theo chuyên gia dự báo , đợt triều cường tron", []),

    # Rec 3157: Bến Cát, Bình Dương -> REJECT tỉnh ngoài
    ("📍 Cảnh người dân đi học , đi làm trễ sáng nay vì không qua được vùng ngập ở đoạn cầu Quan - Bến Cát , Bình Dương .", []),

    # Rec 3158: Cắt cụt đuôi câu 'và con' + Bình Dương -> REJECT
    ("Tại TP. Hồ Chí Minh , Bà con ven kênh , sông SG như Thuận An , Thủ Dầu Một đề phòng ngập úng , chủ động bảo vệ tài sản và con", []),

    # Rec 3159: Trung tâm Bình Dương -> REJECT tỉnh ngoài
    ("Ngập ở khu vực trung tâm Bình Dương ngay lúc này 😟 Triều cường dâng , loạt tuyến đường như Cách Mạng Tháng Tám ( cầu ông Đành ) , Ngô Quyền ( xuống Bạch Đằng ) và chợ Thủ Dầu Một ngập nặng nhiều nơi .", []),

    # Rec 3160: Cắt cụt đuôi câu 'vùng ngập' -> REJECT
    ("Tại TP. Hồ Chí Minh , Mọi người hạn chế lưu thông qua vùng ngập", []),

    # Rec 3161: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Sau cơn mưa đường ngập nửa bánh xe , ai đi qua chú ý nhé .", [
        ([1], [6, 7, 8, 9], 'NEG'),
    ]),

    # Rec 3162: Phú Hòa, Thủ Dầu Một, Bình Dương + cắt cụt đuôi câu -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , 🌧 🌧 🌧 BAN CHQS PHƯỜNG PHÚ HÒA , TP THỦ DẦU MỘT , BÌNH DƯƠNG ỨNG CỨU NGẬP CỤC BỘ DO TRỜI MƯA BÃO \" 🌧 🌧 🌧 💯 Để chủ động , kịp thời ứng phó với diễn biến phức tạp của thiên tai , bão lũ , thời gian vừa qua Ban CHQS phường Phú Hoà đã ch", []),

    # Rec 3163: Thủ Dầu Một, Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Thủ Dầu Một , Mưa ngập ❌ ngay lúc này ở ngã 3 Cống Thích Quảng Đức , Thủ Dầu Một , Bình Dương .", []),

    # Rec 3164: Cảnh báo qua vùng ngập -> REJECT
    ("Tại TP. Hồ Chí Minh , Hiện lượng chức năng đã giăng dây cảnh báo bên đầu ngập , mọi người không nên cố vượt qua nhé .", []),

    # Rec 3165: Chợ Bình Dương -> REJECT tỉnh ngoài
    ("Tối nay ⛔ Thủy Triều dâng cao gây ngập chợ Bình Dương và ngã 6 đến cầu Ông Đành .", []),

    # Rec 3166: Đo mực nước trạm Thủ Dầu Một -> REJECT tỉnh ngoài
    ("Mực nước đo được là 1 , 85m tại trạm Thủ Dầu Một , cao hơn báo động 3 .", []),

    # Rec 3167: Chợ Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Chợ Bình Dương tối nay và những ngày gần đây nước ngập khiến nhiều xe chết máy .", []),

    # Rec 3168: Cảnh báo chung -> REJECT
    ("Tại TP. Hồ Chí Minh , Bà con lưu ý khi qua vùng ngập .", []),

    # Rec 3169: Cảnh báo xả lũ Dầu Tiếng -> REJECT
    ("THÔNG BÁO KHẨN : TỪ 7H SÁNG 25 / 11 ĐẾN 7H NGÀY 2 / 12 / 2025 , HỒ DẦU TIẾNG XẢ LŨ – NGƯỜI DÂN KHU VỰC HẠ DU THUẬN AN , THỦ DẦU MỘT VÀ VEN SÔNG SÀI GÒN CẦN CHỦ ĐỘNG ỨNG PHÓ NGUY CƠ NGẬP ⁉ ️", []),

    # Rec 3170: Cắt cụt đuôi 'ngập ú' + Bình Dương -> REJECT
    ("Tại TP. Hồ Chí Minh , Bà con ven kênh , sông SG như Thuận An , Thủ Dầu Một hết sức lưu ý , đề phòng ngập ú", []),

    # Rec 3171: Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , BÌNH DƯƠNG CHIỀU NAY PHỐ CŨNG NHƯ SÔNG 😢 Khoảng 17h chiều nay ( 13 / 10 ) , cơn mưa lớn bất ngờ đổ xuống nhiều khu vực tại tỉnh Bình Dương khiến không ít tuyến đường bị ngập sâu .", []),

    # Rec 3172: Thủ Dầu Một, Tân Uyên, Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Cảnh này thật quen thuộc 🥹 , Thủ Dầu Một ❌ Đoạn Đường Huỳnh Văn lũy ngay lúc này , Sau trận mưa lớn nước đã tràn vào nhà dân , và một số hình ảnh xe chết máy dắt bộ tại khu vực lân Cận Tân Uyên , Bình Dương Chiều Nay .", []),

    # Rec 3173: Bình Dương -> REJECT tỉnh ngoài
    ("Mưa như trút , nước chảy như thác cuốn trôi xe máy ở Bình Dương TPO - Cơn mưa lớn kèm sấm sét chiều nay ( 24 / 5 ) khiến nhiều tuyến đường ở Bình Dương bị ngập nặng .", []),

    # Rec 3174: Bến Cát, Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Cập nhật ❌ Sau loạt ôtô trôi lềnh đềnh , thì xe máy đậu trên lề cũng bị ngập nặng trong cơn mưa ở Mỹ Phước 2 , thành phố Bến Cát , tỉnh Bình Dương vào chiều nay ( ngày 26 / 8 ) # binhduong24h", []),

    # Rec 3175: Thủ Dầu Một, Thuận An, Bình Dương + cắt cụt đuôi câu -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Bình Dương : Mưa ngập ở 2 thành phố , giao thông tắc nghẽn Đến 19 giờ ngày 1 . 9 . 2024 , nhiều điểm ngập ở thành phố Thủ Dầu Một , thành phố Thuận An ( tỉnh Bình Dương ) vì mưa lớn vẫn chưa có dấu hiệu rút nước , nhiều điểm ngập xuất hiện khiến ô tô khôn", []),

    # Rec 3176: Quốc lộ 13 Suối Giữa (Bình Dương) -> REJECT tỉnh ngoài
    ("Trạm Thu Phí Suối Giữa ( Quốc lộ 13 ) ngay lúc này , mưa khá lớn , dự là sẽ ngập .", []),

    # Rec 3177: Vũng Tàu -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Cơn mưa ngang qua VŨNG TÀU NGẬP BANH CHÀNH / BANH TA LÔNG Chỗ bạn sao rồi", []),

    # Rec 3178: Vũng Tàu -> REJECT tỉnh ngoài
    ("Mưa lớn đầu mùa , nhiều tuyến đường Vũng Tàu ngập sâu Ảnh : Kha Lu", []),

    # Rec 3179: Vũng Tàu -> REJECT tỉnh ngoài
    ("Mưa lớn đầu mùa , nhiều tuyến đường Vũng Tàu ngập sâu", []),

    # Rec 3180: Đường 30 tháng 4 Vũng Tàu -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Ngập ngập & ngập … Đường 30 tháng 4 hôm nay .", []),

    # Rec 3181: Vũng Tàu -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Ngập nặng ở Thi Sách - Vũng Tàu Video : Trần Phúc Hậu", []),

    # Rec 3182: Vũng Tàu + cắt cụt đuôi câu -> REJECT tỉnh ngoài
    ("Hàng loạt phương tiện chết máy trong cơn mưa lớn ở Vũng Tàu tối 22 / 5 Tối 22 / 5 , cơn mưa lớn kéo dài khoảng 2 tiếng đồng hồ ( từ 19 giờ đến 21 giờ ) khiến nhiều tuyến đường trên địa bàn TP. Vũng Tàu ngập sâu Cơn mưa tối 22 / 5 , các tuyến đường Lê Hồng", []),

    # Rec 3183: Vũng Tàu -> REJECT tỉnh ngoài
    ("Mưa lớn đầu mùa , nhiều tuyến đường Vũng Tàu ngập sâu Ngày 7 / 6 , trận mưa lớn kéo dài khoảng 3 giờ đồng hồ ( từ 8 - 11 giờ ) khiến nhiều tuyến đường và nhiều khu vực trên địa bàn TP. Vũng Tàu ngập sâu .", []),

    # Rec 3184: Vũng Tàu -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , 💦 NHIỀU TUYẾN ĐƯỜNG TRUNG TÂM KHU VỰC VŨNG TÀU NGẬP SAU MƯA !", []),

    # Rec 3185: Cắt cụt đuôi câu 'xe cộ di ch' -> REJECT
    ("Tại TP. Hồ Chí Minh , Hồ Chí Minh ) ngập sâu , xe cộ di ch", []),

    # Rec 3186: Vũng Tàu -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , 📍 14 TUYẾN ĐƯỜNG NGẬP SÂU KHI MƯA LỚN TẠI VŨNG TÀU .", []),

    # Rec 3187: Bà Rịa -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , TÌNH HÌNH NGẬP LỤT SẮP TỚI TẠI BÀ RỊA .", []),

    # Rec 3188: Bà Rịa - Vũng Tàu + cắt cụt đuôi -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , KHÔNG HOANG MANG VỀ TIN ĐỒN : Trong hai ngày gần đây , trên không gian mạng có lan truyền thông tin đồn đoán rằng địa bàn Bà Rịa - Vũng Tàu ( cũ ) sắp xảy ra ngập lụt nghiêm trọng , dẫn đến việc nhiều ngư", []),

    # Rec 3189: Bà Rịa -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , KHÔNG HOANG MANG VỀ TIN ĐỒN : TÌNH HÌNH NGẬP LỤT SẮP TỚI TẠI BÀ RỊA", []),

    # Rec 3190: Tin đồn thất thiệt -> REJECT
    ("Tại TP. Hồ Chí Minh , 4 PHÍA ĐỀU LÀ BIỂN ĐẢO ĐỪNG NGHE AI ĐÓ NÓI NGẬP ĐẾN NÓC NHÀ TRỪ TRƯỜNG HỢP NƯỚC BIỂN DÂNG LÊN HOẶC SÓNG THẦN THÔI", []),

    # Rec 3191: Chợ Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Đường ở chợ Bình Dương gần đây cứ như ' Vũng Tàu ' 🫣 Đường ngập bà con xin đừng cố chạy qua .", []),

    # Rec 3192: Bà Rịa - Vũng Tàu + cắt cụt đuôi -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , ⚠ ️ CẢNH BÁO NGƯỜI DÂN KHÔNG NGHE THEO TIN ĐỒN THẤT THIỆT VỀ NGUY CƠ NGẬP LỤT TẠI BÀ RỊA – VŨNG TÀU Những ngày gần đây , trên mạng xã hội xuất hiện nhiều thông tin đồn đoán về việc khu vực Bà Rịa – Vũng Tàu ( cũ ) thuộc Thành phố", []),

    # Rec 3193: Hồ Tràm - Xuyên Mộc - BRVT -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , HỒ TRÀM - XUYÊN MỘC - BRVT CŨ NGẬP NẶNG - NƯỚC CHẢY RA BIỂN KO KỊP", []),

    # Rec 3194: Vũng Tàu -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Không ngờ có ngày Vũng Tàu gặp cảnh này . Ngập ngang bụng luôn 🥲 🥲 Note : đoạn ngã tư Vietso Petro đường 30 / 04 hướng vô trung tâm và ngược lại Cre : Ngoan Đặng", []),

    # Rec 3195: Vũng Tàu -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Đường 30 / 4 khu vực cảng Vietso ngập nặng , mọi người nên chọn hướng đi khác Ảnh : SOS Vũng Tàu Share by Tin Tức Bà Rịa - Vũng Tàu", []),

    # Rec 3196: Mỹ Xuân, thị xã Phú Mỹ (Bà Rịa) -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Sớm xử lý tình trạng ngập tại phường Mỹ Xuân , thị xã Phú Mỹ", []),

    # Rec 3197: Bến Cát, Bình Dương -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Mưa lớn ngập sâu ở Bến Cát , Bình Dương Không cần đi chữa lành , ở đây vừa lành và lạnh luôn 🐧", []),

    # Rec 3198: Bà Rịa – Châu Pha -> REJECT tỉnh ngoài
    ("Tại TP. Hồ Chí Minh , Đường Bà Rịa – Châu Pha đoạn thi công cầu vượt km 49 + 900 ngập nước vì trời mưa", []),

    # Rec 3199: Đồ án sinh viên kiến trúc cảnh quan công viên rừng ngập mặn -> REJECT
    ("Tại TP. Hồ Chí Minh , ĐỒ ÁN SINH VIÊN TIÊU BIỂU : THIẾT KẾ KIẾN TRÚC CẢNH QUAN CÔNG VIÊN RỪNG NGẬP MẶN TỈNH BÀ RỊA - VŨNG TÀU Với định hướng trở thành một “ Công viên rừng ngập mặn ” trong tương lai , đồ án “ Thiết kế kiến trúc cảnh quan công viên rừng ngậ", []),

    # Rec 3200: Ăn uống hải sản ngập mặt -> REJECT
    ("Tăng 2 hải sản ngập mặt ngay tại Sài Gòn chứ không phải Bà Rịa .", []),
]

def test_triplets():
    flaws = 0
    print(f'Kiểm tra {len(batch32_data)} records...')
    for idx, (text, triplets) in enumerate(batch32_data, 3101):
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
        print('TẤT CẢ CÁC TRIPLETS CỦA BATCH 32 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!')
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
        
        # Chỉ giữ lại đúng 3100 records đầu nếu đã có
        base_lines = lines[:3100]
        
        # Format batch 32
        new_batch_lines = []
        for text, triplets in batch32_data:
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
