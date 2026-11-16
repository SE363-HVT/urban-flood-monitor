# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn chuẩn hóa cho Phase 3 - Batch 34 (Records 3301 - 3400).
Tuân thủ 100% tài liệu BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md.
"""

batch34_data = [
    # Rec 3301: Đã có Thảo Điền
    ("Lý do nào mà Thảo Điền nơi được xem và vùng trũng thường xuyên xảy ra NGẬP LỤT và KẸT XE mà vẫn thu hút được giới nhà giàu đến ở ? 🤔 🤔", [
        ([4, 5], [16, 17], 'NEG'),
    ]),

    # Rec 3302: Chỉ đạo hành chính ra hạn chót -> REJECT
    ("TP. HCM ra hạn chót đến 15 - 9 phải xử lý điểm ngập chợ Thủ Đức , Thảo Điền , Lê Văn Việt . . . . .", []),

    # Rec 3303: Cắt cụt đuôi câu 'sống trong cả' -> REJECT
    ("🌧 😔 NGƯỜI DÂN KHU NHÀ GIÀU THẢO ĐIỀN KHỐN KHỔ VÌ CỨ MƯA LÀ NGẬP Được mệnh danh là “ khu nhà giàu ” với hàng loạt biệt thự , chung cư cao cấp , nhưng cả chục năm nay , người dân ở phường Thảo Điền , TP Thủ Đức ( TPHCM ) phải sống trong cả", []),

    # Rec 3304: Cảnh báo ngập tương lai -> NEU (Pass 8)
    ("Cảnh báo ngập tại Thảo Điền 🥹 Tối nay mưa lớn , kèm triều cường cả nhà chú ý những tuyến đường dễ ngập .", [
        ([4, 5], [0, 1, 2], 'NEU'),
    ]),

    # Rec 3305: Đã có khu Thảo Điền, TP Thủ Đức
    ("Cơn mưa lớn chiều 4 / 6 khiến các tuyến đường tại khu Thảo Điền ( TP Thủ Đức ) ngập nặng , nhiều xe máy té ngã trong \" biển nước \" 🥹 Ảnh : ZNews", [
        ([13, 14], [20, 21], 'NEG'),
        ([13, 14], [26, 27], 'NEG'),
        ([16, 17, 18], [20, 21], 'NEG'),
    ]),

    # Rec 3306: Đã có Thủ Đức, Thảo Điền
    ("Thành Phố Biển Thủ Đức , khu vực Thảo Điền lại ngập nước tràn trề lai láng sau mưa lớn .", [
        ([3, 4], [11, 12, 13, 14, 15, 16], 'NEG'),
        ([8, 9], [11, 12, 13, 14, 15, 16], 'NEG'),
    ]),

    # Rec 3307: Ẩn dụ sóng dữ / cắt cụt -> REJECT
    ("Tại TP. Hồ Chí Minh , Dòng xe máy chật vật trước những cơn sóng dữ được tạo bởi ô tô . . .", []),

    # Rec 3308: Câu hỏi hỏi đường -> REJECT
    ("Ae cho hỏi đường Nguyễn Văn Hưởng sáng nay có ngập k ?", []),

    # Rec 3309: Cắt cụt đuôi câu 'trên địa' -> REJECT
    ("BÍ THƯ THÀNH UỶ TPHCM NGUYỄN VĂN NÊN : CHỐNG NGẬP CẦN PHẢI LÀM ĐỒNG BỘ ________________________ Ngày 25 - 10 , Đoàn lãnh đạo Thành ủy , UBND TPHCM đã làm việc với Sở Xây dựng về tình hình thực hiện công tác giảm ngập trên địa", []),

    # Rec 3310: Đã có TP. HCM
    ("Tại TP. HCM , mực nước tại các kênh , rạch lên nhanh theo đỉnh triều cường tháng 8 âm lịch đã gây ngập nhiều tuyến đường khu vực trũng , thấp trong hai ngày qua .", [
        ([1, 2], [23, 24], 'NEG'),
    ]),

    # Rec 3311: Đã có Võ Văn Ngân, Tô Ngọc Vân, Thủ Đức
    ("Đây là cảnh ngập nước tại Võ Văn Ngân và Tô Ngọc Vân Thủ Đức .", [
        ([6, 7, 8], [3, 4], 'NEG'),
        ([10, 11, 12], [3, 4], 'NEG'),
        ([13, 14], [3, 4], 'NEG'),
    ]),

    # Rec 3312: Review mạng xã hội -> REJECT
    ("Tại TP. Hồ Chí Minh , Kiểu đi xuồng được luôn Review nhẹ khoe tình hình ngập nước nơi bạn sống đi Ảnh : Trương Huy ( Via : thánh riviu ) # toilanguoisaigon", []),

    # Rec 3313: Đã có đường Tô Ngọc Vân, quận Thủ Đức
    ("Hình ảnh ngập toe tua trên đường Tô Ngọc Vân ( quận Thủ Đức ) vào chiều tối nay , khiếp quá .", [
        ([6, 7, 8, 9], [2, 3, 4], 'NEG'),
        ([6, 7, 8, 9], [20, 21], 'NEG'),
        ([11, 12, 13], [2, 3, 4], 'NEG'),
    ]),

    # Rec 3314: Câu hỏi tương lai -> REJECT
    ("Không biết mai mốt lên thành phố Thủ Đức rồi có hết ngập không ? ? ?", []),

    # Rec 3315: Ngập rác -> REJECT
    ("Đường ở TP Thủ Đức ngập rác sau mưa lớn Sau cơn mưa lớn chiều 13 / 5 , đường Tô Ngọc Vân ( đoạn qua phường Linh Đông , TP Thủ Đức ) ngập trong rác .", []),

    # Rec 3316: Không có từ ngập lụt -> REJECT
    ("Tại TP. Hồ Chí Minh , Người dân phải đội mưa khơi thông dòng chảy để tránh rác tràn vào nhà .", []),

    # Rec 3317: Đã có TÔ NGỌC VÂN, đường Tô Ngọc Vân
    ("NGAY LÚC NÀY TẠI TÔ NGỌC VÂN 🥲 Lúc này tại đường Tô Ngọc Vân , TP. HCM , nước đã ngập quá nửa bánh xe , người dân lội nước đi học , đi làm 🌊", [
        ([4, 5, 6], [21, 22, 23, 24, 25], 'NEG'),
        ([11, 12, 13, 14], [21, 22, 23, 24, 25], 'NEG'),
        ([11, 12, 13, 14], [29, 30], 'NEG'),
    ]),

    # Rec 3318: Cắt cụt đuôi câu 'tại TP.' -> REJECT
    ("Tại TP. Hồ Chí Minh , HCM ĐANG NGẬP SÂU Cơn mưa sáng nay ( 25 / 5 ) khiến không ít con đường tại TP.", []),

    # Rec 3319: Cắt cụt đuôi câu 'người dâ' -> REJECT
    ("Thủ Đức bị ngập sâu , mực nước dâng cao khoảng 0 , 5m 😱 Nơi được khuyến cáo người dâ", []),

    # Rec 3320: Bàn luận dự án kỳ vọng tương lai -> REJECT
    ("Dự án thoát nước đường Võ Văn Ngân , TP. Thủ Đức được kỳ vọng sẽ giải quyết tình trạng ngập úng dai dẳng tại khu vực này .", []),

    # Rec 3321: Đã có Đường Võ Văn Ngân
    ("Đường Võ Văn Ngân mới làm đã ngập , lãnh đạo thành phố Thủ Đức nói gì ?", [
        ([0, 1, 2, 3], [4, 5, 6, 7], 'NEG'),
    ]),

    # Rec 3322: Đã có Lã Xuân Oai, Lê Văn Việt, Tô Ngọc Vân, Võ Văn Ngân
    ("Cơn mưa chiều 5 - 6 trên địa bàn TP Thủ Đức làm nhiều tuyến đường như Lã Xuân Oai , Lê Văn Việt , Tô Ngọc Vân , Võ Văn Ngân … bị ngập nước , nhiều xe chết máy .", [
        ([17, 18, 19], [34, 35], 'NEG'),
        ([17, 18, 19], [39, 40], 'NEG'),
        ([21, 22, 23], [34, 35], 'NEG'),
        ([21, 22, 23], [39, 40], 'NEG'),
        ([25, 26, 27], [34, 35], 'NEG'),
        ([25, 26, 27], [39, 40], 'NEG'),
        ([29, 30, 31], [34, 35], 'NEG'),
        ([29, 30, 31], [39, 40], 'NEG'),
    ]),

    # Rec 3323: Đã có chợ Thủ Đức, Đường Võ Văn Ngân
    ("‼ ️ Rồi xong phim , chợ Thủ Đức thất thủ rồi , toàn là nước ei Đường Võ Văn Ngân ngay ngã 3 Đặng Văn Bi , dốc nhà thờ không còn ngập như xưa nữa nhưng nước dồn hết về xung quanh chợ Thủ Đức thành chợ nổi luôn rồi .", [
        ([6, 7, 8], [9, 10], 'NEG'),
        ([17, 18, 19, 20], [31, 32, 33, 34, 35, 36], 'POS'),
        ([44, 45, 46], [47, 48, 49], 'NEG'),
    ]),

    # Rec 3324: Cắt cụt đuôi câu 'từ đườ' -> REJECT
    ("TPHCM chuẩn bị khởi công 3 dự án chống ngập trên địa bàn quận Gò Vấp , gồm : Cải tạo hệ thống thoát nước đường Quang Trung ( từ đường Phạm Văn Chiêu đến Cầu Chợ Cầu - tổng vốn 120 tỉ đồng ) ; cải tạo hệ thống thoát nước đường Lê Đức Thọ ( từ đườ", []),

    # Rec 3325: Đã có Kha Vạn Cân, phường Hiệp Bình Chánh
    ("Hiện đường ống nước đang bị bể ở trước số nhà 407A Kha Vạn Cân , phường Hiệp Bình Chánh , TP Thủ Đức khiến cả khu vực ngập nặng .", [
        ([12, 13, 14], [28, 29], 'NEG'),
        ([16, 17, 18, 19], [28, 29], 'NEG'),
    ]),

    # Rec 3326: Đã có TP. HCM, thành phố Thủ Đức
    ("TP. HCM : Mưa xối xả , nhiều tuyến đường ngập sâu Cơn mưa lớn trút xuống thành phố Thủ Đức ( TP HCM ) chiều 6 - 9 khiến nhiều đoạn đường trước đây rất ít ngập giờ cũng bị ngập nước .", [
        ([0, 1], [10, 11], 'NEG'),
        ([17, 18, 19, 20], [40, 41, 42], 'NEG'),
    ]),

    # Rec 3327: Cắt cụt đuôi câu 'Chìa khóa' -> REJECT
    ("💥 BẢN TIN NỔI BẬT TỔNG HỢP SÁNG NGÀY 21 / 5 💥 ✦ Chống ngập nước cho TP. HCM : cần giải pháp hạ tầng đồng bộ và lâu dài ✦ TP. HCM : Ô nhiễm môi trường Kênh Nước Đen - Cần giải pháp bền vững ✦ Khai thác nguồn lực đất đai hiệu quả - Chìa khóa", []),

    # Rec 3328: Cắt cụt đuôi câu '. . .' -> REJECT
    ("MƯA LỚN KÉO DÀI , HÀNG LOẠT TUYẾN ĐƯỜNG Ở TP. HCM NGẬP SÂU ⛈ Hơn 19h30 tối 23 / 10 , hàng loạt tuyến đường ở quận Bình Tân ( TP. HCM ) như An Dương Vương , Nguyễn Thức Đường , Kênh Nước Đen , Hồ Học Lãm , . . .", []),

    # Rec 3329: Cắt cụt đuôi câu '. . .' -> REJECT
    ("Nhiều đường ở TP HCM ngập sâu trong mưa đầu mùa Mưa lớn kéo dài khoảng một giờ khiến nhiều tuyến đường ở quận Gò Vấp , quận 12 . . .", []),

    # Rec 3330: Cắt cụt đuôi câu ',' -> REJECT
    ("Theo Trung tâm quản lý hạ tầng kỹ thuật - Sở Xây dựng TPHCM , nơi ngập nhiều nhất là thành phố Thủ Đức với 11 tuyến đường , gồm : Quốc Hương , Nguyễn Duy Trinh , Tô Ngọc Vân , Đặng Thị Rành , Hồ Văn Tư , Kha Vạn Cân , Dương Văn Cam , Võ Văn Ngân ,", []),

    # Rec 3331: Đã có TP Thủ Đức
    ("TP Thủ Đức : Hẻm ngập triền miên , người dân bỏ nhà đi thuê trọ 👇", [
        ([0, 1, 2], [5, 6, 7], 'NEG'),
    ]),

    # Rec 3332: Đã có chợ Thủ Đức
    ("Nước ngập nửa mét bao vây chợ Thủ Đức Sáng 6 / 8 , trận mưa như trút nước khiến tuyến đường xung quanh chợ Thủ Đức ngập nửa mét , hoạt động kinh doanh bị ngưng trệ .", [
        ([6, 7, 8], [1, 2, 3], 'NEG'),
        ([6, 7, 8], [4, 5], 'NEG'),
        ([24, 25, 26], [27, 28, 29], 'NEG'),
        ([24, 25, 26], [35, 36, 37], 'NEG'),
    ]),

    # Rec 3333: Đã cắt bỏ tiền tố thừa, giữ TP HCM
    ("Trận mưa lớn vào ngày hôm qua 27 . 5 , làm nhiều tuyến đường tại TP HCM ngập cục bộ .", [
        ([16, 17], [18, 19, 20], 'NEG'),
    ]),

    # Rec 3334: Đã có TP Thủ Đức
    ("Chiều 20 / 5 , cơn mưa lớn khiến nhiều tuyến đường ở TP Thủ Đức ngập nặng .", [
        ([13, 14, 15], [16, 17], 'NEG'),
    ]),

    # Rec 3335: Đã có Chợ Thủ Đức
    ("Chợ Thủ Đức biến thành biển nước , nắp cống bung lên khiến nước phun ồ ạt .", [
        ([0, 1, 2], [3, 4, 5, 6], 'NEG'),
    ]),

    # Rec 3336: Đã có TP Thủ Đức
    ("Đến hẹn lại lên , những con phố trung tâm TP Thủ Đức lại trở nên mênh mông nước sau những cơn mưa nặng hạt .", [
        ([10, 11, 12], [16, 17, 18], 'NEG'),
    ]),

    # Rec 3337: Câu hỏi tương lai -> REJECT
    ("🌊 🚫 TP. HCM “ Rốn ngập ” Gò Vấp cũ có phải chờ ít nhất đến 2027 mới mong hết ngập ?", []),

    # Rec 3338: Dính ngoặc đơn thừa ')' + thống kê -> REJECT
    ("Các đường Nguyễn Văn Khối , Lê Văn Thọ , Lê Đức Thọ , Phạm Văn Chiêu ) hễ mưa là ngập sâu 0 , 11 – 0 , 15 m , năm 2025 mỗi tuyến đã ngập 4 – 8 lần .", []),

    # Rec 3339: Đề tài khoa học -> REJECT
    ("[ KHOA HỌC CÔNG NGHỆ ] NHẬN THỨC VÀ THÍCH ỨNG VỀ NGUY CƠ NGẬP NƯỚC CỦA NGƯỜI DÂN THÀNH PHỐ HỒ CHÍ MINH .", []),

    # Rec 3340: Cắt cụt đuôi câu 'Dưới tá' -> REJECT
    ("ĐIỂN CỨU : ĐIỂM NGẬP ĐƯỜNG KINH DƯƠNG VƯƠNG ( TP. HCM ) * Nghiên cứu được thực hiện trước 01 / 7 / 2025 Dưới tá", []),

    # Rec 3341: Cẩm nang tổng hợp danh sách -> REJECT
    ("TỔNG HỢP CÁC ĐOẠN ĐƯỜNG LÀ ĐIỂM NGẬP TẠI TP. THỦ ĐỨC VÀ HCM KHI MƯA LỚN - - - - DANH SÁCH CÁC ĐOẠN ĐƯỜNG BỊ NGẬP Ở TP HCM : Những tuyến đường hay ngập ở Quận 1 : ➤ Đường Calmette ( Từ Lê Thị Hồng Gấm – Nguyễn Công Trứ ) .", []),

    # Rec 3342: Kêu cứu lũ lụt -> REJECT
    ("Tại TP. Hồ Chí Minh , nhà nước ngập tới ngực rồi ạ , không leo lên mái được tại bé đang giữ giường bệnh cho ÔNG của bé đang bị tai biến bé sắp chịu hết nổi rồi ạ mong ĐỘI CỨU HỘ dùm em ạ sđt của người bị nạn : 033 3507414", []),

    # Rec 3343: Kêu cứu lũ lụt -> REJECT
    ("Sos cứu cứu em gái của em giúp em với 1 người già , 1 trẻ em , 2 người lớn , nước ngập lên tầng 1 rồi 305 / 62 lương định của , chợ chiều , khúc cua nghĩa trang 0819733971", []),

    # Rec 3344: Cắt cụt đuôi câu 'Thập (' -> REJECT
    ("Xe cộ ' bơi ' giữa đường trong mùa triều cường dâng cao tại TP. HCM Tối 7 - 11 , nhiều người dân TP. HCM vất vả khi đi qua các tuyến đường bị ngập nặng do triều cường dâng cao , như đường Lương Định Của ( TP Thủ Đức ) , Trần Xuân Soạn , Nguyễn Thị Thập (", []),

    # Rec 3345: Kêu cứu lũ lụt -> REJECT
    ("Tại TP. Hồ Chí Minh , Nhiều hộ đang cần cứu vì nước ngập kẹt ko ra được ạh", []),

    # Rec 3346: Đã có Sài Gòn, TP HCM
    ("Nhà ngập , ôtô chết máy trong triều cường ở Sài Gòn Triều cường khiến nhiều tuyến đường ở TP HCM ngập sâu , hàng loạt xe chết máy , nhà dân bị nước tràn vào , chiều 5 / 11 .", [
        ([10, 11], [1], 'NEG'),
        ([10, 11], [4, 5], 'NEG'),
        ([19, 20], [21, 22], 'NEG'),
        ([19, 20], [27, 28], 'NEG'),
        ([19, 20], [32, 33, 34, 35], 'NEG'),
    ]),

    # Rec 3347: Đã có TP HCM
    ("Lúc 17h , triều cường gây ngập nhiều tuyến đường ở khu vực trũng thấp tại TP HCM", [
        ([16, 17], [5, 6], 'NEG'),
    ]),

    # Rec 3348: Tản văn đùa cợt cắt cụt đuôi câu -> REJECT
    ("PHAN HUY ÍCH VÀ NHỮNG \" ĐẶC SẢN \" HỔNG CÓ DZUI Dài không dài , ngắn không ngắn , đủ dùng , đủ kẹt xe , đủ ngập nước , đủ đua xe lạng lách tranh cúp lư hương các kiểu Thử , à không , có thiệt , một chiều nắng đẹp , bạn ăn mặc đẹp đẽ , dắt xe ra khỏi nhà", []),

    # Rec 3349: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Bữa nay là NGẬP BẤT KỂ mưa TO mưa NHỎ nha ! .", [
        ([1], [6, 7, 8], 'NEG'),
    ]),

    # Rec 3350: Đã có GÒ VẤP, Gò Vấp, đường Nguyễn Văn Khối
    ("MƯA LỚN HƠN 1 GIỜ , NHIỀU TUYẾN ĐƯỜNG Ở VÙNG DỊCH GÒ VẤP NGẬP SÂU Sau cơn mưa lớn kéo dài hơn 1 giờ nhiều tuyến đường tại vùng dịch Gò Vấp ngập sâu , nhiều phương tiện lưu thông qua đường Nguyễn Văn Khối chết máy phải dẫn bộ .", [
        ([12, 13], [14, 15], 'NEG'),
        ([31, 32], [33, 34], 'NEG'),
        ([42, 43, 44, 45], [46, 47], 'NEG'),
        ([42, 43, 44, 45], [48, 49, 50], 'NEG'),
    ]),

    # Rec 3351: Đã có đường Nguyễn Văn Khối, quận Gò Vấp
    ("Toàn bộ đường Nguyễn Văn Khối ( quận Gò Vấp ) ngập sâu đến 0 , 5m , xe cộ di chuyển khó khăn - Ảnh : CHÂU TUẤN", [
        ([2, 3, 4, 5], [11, 12], 'NEG'),
        ([2, 3, 4, 5], [20, 21, 22, 23], 'NEG'),
        ([7, 8, 9], [11, 12], 'NEG'),
    ]),

    # Rec 3352: Cải tạo rạch thành đường -> REJECT
    ("Tại TP. Hồ Chí Minh , Rạch chống ngập thành đường sau 4 năm cải tạo ở TP HCM .", []),

    # Rec 3353: Cắt cụt đuôi câu '. . .' -> REJECT
    ("🛑 MƯA LỚN GẦN 2 TIẾNG , NHIỀU TUYẾN ĐƯỜNG TÂY TPHCM NGẬP SÂU , XE CHẾT MÁY HÀNG LOẠT ✅ Khoảng 17h ngày 18 - 9 , mưa lớn bắt đầu đổ xuống khu vực phía tây TP. HCM , khiến nhiều tuyến đường như Tên Lửa , Sinco , Hồ Học Lãm . . .", []),

    # Rec 3354: Đã có TP. HCM
    ("🛑 Phường lún nhanh nhất TP. HCM : Chỉ sau 1 cơn mưa , nước “ đen ngòm ” ngập lênh láng nhiều tuyến đường khiến người dân chật vật di chuyển 🌊", [
        ([5, 6], [19, 20, 21], 'NEG'),
        ([5, 6], [28, 29, 30, 31], 'NEG'),
    ]),

    # Rec 3355: Cắt cụt đuôi câu '. . .' -> REJECT
    ("Trụ sở ủy ban quận , hầm chui ở TP HCM ngập do mưa lớn Mưa lớn hơn một giờ khiến trụ sở UBND quận Bình Tân , hầm chui Tân Tạo , quốc lộ 1 . . .", []),

    # Rec 3356: Cắt cụt đuôi câu 'quận B' -> REJECT
    ("Tại TP. Hồ Chí Minh , Khoảng 16h30 , sau nửa tiếng mưa trút xuống , nước ngập tràn vào trụ sở UBND quận B", []),

    # Rec 3357: Cắt cụt đuôi câu 'Hồ H' -> REJECT
    ("MƯA LỚN KÉO DÀI NHIỀU GIỜ KHIẾN HÀNG LOẠT TUYẾN ĐƯỜNG KHU VỰC PHÍA TÂY TP. HCM NGẬP SÂU 😰 Hơn 19h30 tối 23 / 10 , hàng loạt tuyến đường ở quận Bình Tân ( TP. HCM ) như An Dương Vương , Nguyễn Thức Đường , Kênh Nước Đen , Hồ H", []),

    # Rec 3358: Đã có TP. HCM
    ("CƠN MƯA CHIỀU Ở TP. HCM CÓ ĐƯỜNG NƯỚC NGẬP GẦN TỚI YÊN XE , NHIỀU NGƯỜI NGỠ NGÀNG Trong cơn mưa chiều nay 25 . 9 , một số tuyến đường ở TP. HCM nước ngập gần tới … yên xe máy .", [
        ([4, 5], [8, 9, 10, 11, 12, 13], 'NEG'),
        ([33, 34], [35, 36], 'NEG'),
    ]),

    # Rec 3359: Cắt cụt đuôi câu 'nhiề' -> REJECT
    ("Tại TP. Hồ Chí Minh , Giữa ' biển nước ' mênh mông , xe chết máy la liệt , nhiề", []),

    # Rec 3360: Đã có quận Bình Tân, TP. HCM
    ("Cơn mưa lớn chừng 20 phút vào chiều nay 25 - 9 khiến nhiều tuyến đường ở quận Bình Tân , TP. HCM nước ngập lênh láng như ' ao cá ' .", [
        ([17, 18, 19], [24, 25, 26], 'NEG'),
        ([21, 22], [24, 25, 26], 'NEG'),
    ]),

    # Rec 3361: Đã có quận Bình Tân, TP. HCM
    ("Cơn mưa lớn chừng 20 phút vào chiều nay 25 - 9 khiến nhiều tuyến đường ở quận Bình Tân , TP. HCM nước ngập lênh lang như ' ao cá ' .", [
        ([17, 18, 19], [24, 25, 26], 'NEG'),
        ([21, 22], [24, 25, 26], 'NEG'),
    ]),

    # Rec 3362: Đã có TP. HCM
    ("🆘 Phường lún nhanh nhất TP. HCM : Ngập trong biển nước “ đen ngòm ” lênh láng ở nhiều tuyến đường sau cơn mưa sáng nay 🤧 Ảnh : Cao An Biên Theo : Thanh Niên", [
        ([5, 6], [8, 9, 10, 11], 'NEG'),
    ]),

    # Rec 3363: Kiến nghị dự án tương lai -> REJECT
    ("Tại TP. Hồ Chí Minh , Quận Gò Vấp kiến nghị UBND thành phố chi gần 5 . 900 tỷ đồng cho 4 dự án mở rộng đường huyết mạch đang xuống cấp , ùn tắc và hay ngập nước .", []),

    # Rec 3364: Đã cắt tiền tố thừa, giữ Gò Vấp
    ("Đến 11h cùng ngày , Gò Vấp một số tuyến đường vẫn còn ngập nặng .", [
        ([5, 6], [11, 12, 13, 14], 'NEG'),
    ]),

    # Rec 3365: Cắt cụt đầu câu 'HCM )' -> REJECT
    ("Tại TP. Hồ Chí Minh , HCM ) phải huy động toàn bộ nhân viên xuống đường xử lý cống , chống ngập .", []),

    # Rec 3366: Đã có trạm điện quận Gò Vấp, đường Cây Trâm
    ("Tối 14 - 9 , trên địa bàn TP. HCM xuất hiện mưa lớn khiến nhiều tuyến đường ngập , trong đó trạm điện quận Gò Vấp trên đường Cây Trâm bị nước tràn vào , lực lượng PCCC đã ứng cứu khẩn cấp đến hút nước ra ngoài .", [
        ([23, 24, 25, 26, 27], [32, 33, 34], 'NEG'),
        ([29, 30, 31], [32, 33, 34], 'NEG'),
    ]),

    # Rec 3367: Đã có SÀI GÒN
    ("HÀNG LOẠT TUYẾN ĐƯỜNG TẠI SÀI GÒN LẠI CHÌM TRONG BIỂN NƯỚC ! ! !", [
        ([5, 6], [8, 9, 10, 11], 'NEG'),
    ]),

    # Rec 3368: Báo cáo hành chính Sở Xây dựng -> REJECT
    ("TẠM BIỆT NẮNG NÓNG , TP. HCM CHUẨN BỊ TRƯỚC ' MÙA NGẬP ' ☔ ️ ☔ ️ Mới đây , Sở Xây dựng TP. HCM có báo cáo về tình hình ngập do mưa và triều cường tại thành phố .", []),

    # Rec 3369: Cắt cụt đuôi câu 'tuyến đườn' -> REJECT
    ("Theo đó , TP. HCM có 18 điểm ngập ( 13 tuyến đường ngập do mưa và 5 tuyến đườn", []),

    # Rec 3370: Cẩm nang 18 tuyến đường -> REJECT
    ("18 tuyến đường ở TP. HCM thường xuyên bị ngập nước mà người dân cần biết", []),

    # Rec 3371: Đã có TP. HCM
    ("Vào mùa mưa , nhiều tuyến đường ở TP. HCM liên tục bị ngập nước điều này kéo theo những ngôi nhà của người dân cũng trong tình cảnh tương tự .", [
        ([8, 9], [10, 11, 12, 13, 14], 'NEG'),
    ]),

    # Rec 3372: Câu điều kiện giả định -> REJECT
    ("Tại TP. Hồ Chí Minh , Nếu nhà thường xuyên bị ngập nước sẽ ảnh hưởng đến chất lượng công trình .", []),

    # Rec 3373: Quảng cáo bán phụ tùng xe -> REJECT
    ("Chủ nhật ngập kèo ae ơi 😝 😝 Anchor mod excel rim 2 lỗ van luôn , tới cục cutt Ae có nhu cầu alo em nha , rút căm vô vỏ sẵn , ae mua lẻ đều có đủ 😋 ☎ ️ 0783255268 Thanh m5 ( có zalo ạ ) 250 Lê Thị Hoa , Bình Chiểu , Thủ Đức", []),

    # Rec 3374: Hà Nội (Đại lộ Thăng Long) + Cắt cụt đuôi câu -> REJECT
    ("ĐẾN ĐẠI LỘ CŨNG HOÁ THÀNH SÔNG Cơn mưa lớn chiều nay không chỉ khiến các con phố trong nội thành ngập nặng , mà cả những con đường lớn ở ngoại thành như Lê Văn Lương kéo dài , vành đai 3 , Đại lộ Thăng Long cũng hoá sông … Hiện tại mưa đ", []),

    # Rec 3375: Đã cắt tiền tố thừa, giữ Đường Lã Xuân Oai
    ("Đường Lã Xuân Oai mênh mông nước , đoạn ngập nặng nhất dài khoảng 300 m .", [
        ([0, 1, 2, 3], [4, 5, 6], 'NEG'),
        ([0, 1, 2, 3], [9, 10, 11], 'NEG'),
    ]),

    # Rec 3376: Đã có thành phố Thủ Đức, TP HCM
    ("Cơn mưa lớn trút xuống thành phố Thủ Đức ( TP HCM ) chiều 6 - 9 khiến nhiều đoạn đường trước đây rất ít ngập giờ cũng bị ngập nước .", [
        ([5, 6, 7, 8], [28, 29, 30], 'NEG'),
        ([10, 11], [28, 29, 30], 'NEG'),
    ]),

    # Rec 3377: Đã có TPHCM
    ("Cơn mưa kéo dài và trải rộng chiều qua trên địa bàn TPHCM khiến cho nhiều nơi bị ngập nặng , giao thông hỗn độn , ảnh hưởng không nhỏ đến sinh hoạt của người dân .", [
        ([12], [17, 18, 19], 'NEG'),
        ([12], [21, 22, 23, 24], 'NEG'),
    ]),

    # Rec 3378: Đã có TP HCM
    ("Đường ngập lút bánh xe trong mưa lớn ở TP HCM Mưa lớn khiến hàng loạt tuyến đường TP HCM ngập sâu , nhiều xe chết máy , người dân lội nước về nhà , chiều 15 / 5 .", [
        ([9, 10], [1, 2, 3, 4], 'NEG'),
        ([18, 19], [20, 21], 'NEG'),
        ([18, 19], [25, 26], 'NEG'),
        ([18, 19], [30, 31], 'NEG'),
    ]),

    # Rec 3379: Đã có TP. HCM, chợ Thủ Đức, TP Thủ Đức
    ("Chiều 19 - 5 , cơn mưa xảy ra trên diện rộng trút xuống khu vực TP. HCM trong gần 1 tiếng khiến nhiều tuyến đường bị ngập , trong đó có có ' rốn ngập ' quanh chợ Thủ Đức ( TP Thủ Đức ) , nơi đang có dự án chống ngập vừa được khởi công năm 2020 .", [
        ([16, 17], [26, 27], 'NEG'),
        ([38, 39, 40], [26, 27], 'NEG'),
        ([42, 43, 44], [26, 27], 'NEG'),
    ]),

    # Rec 3380: Đã có TP Thủ Đức, đường Phạm Văn Đồng
    ("Mưa lớn gây ngập đường , kẹt xe ở TP HCM Mưa lớn khiến nhiều nơi ở TP Thủ Đức ngập sâu , nắp hố ga trên đường Phạm Văn Đồng bị bung tạo thành cột nước cao , gây ùn tắc khoảng 4 km , chiều 6 / 9 .", [
        ([17, 18, 19], [20, 21], 'NEG'),
        ([27, 28, 29, 30], [39, 40, 41], 'NEG'),
    ]),

    # Rec 3381: Đã có TP. HCM, GÒ VẤP, Gò Vấp
    ("🌧 TP. HCM MƯA LỚN , GÒ VẤP CŨ NGẬP LÊNH LÁNG – DÂN PHẢI KHIÊNG XE THOÁT NƯỚC Tối 26 - 10 , mưa lớn kéo dài khiến nhiều khu vực ở Gò Vấp cũ ( TP. HCM ) rơi vào cảnh ngập nặng .", [
        ([1, 2], [9, 10, 11], 'NEG'),
        ([6, 7], [9, 10, 11], 'NEG'),
        ([33, 34], [42, 43, 44], 'NEG'),
    ]),

    # Rec 3382: Đã có Gò Vấp, TPHCM
    ("Gò Vấp TPHCM Ngập Ngay Lúc Này", [
        ([0, 1], [3], 'NEG'),
        ([2], [3], 'NEG'),
    ]),

    # Rec 3383: Đã có TPHCM
    ("TPHCM BẤT NGỜ MƯA LỚN KÈM SẤM SÉT VÀO SÁNG SỚM , ĐƯỜNG NGẬP NHƯ SÔNG 💦 6h sáng , khắp nơi trên địa bàn TPHCM xuất hiện mưa lớn kèm theo hiện tượng sấm chớp , gió giật mạnh .", [
        ([0], [13, 14, 15], 'NEG'),
    ]),

    # Rec 3384: Cắt cụt đuôi câu 'như So' -> REJECT
    ("Tại TP. Hồ Chí Minh , Mưa lớn cũng gây ngập nặng nhiều tuyến đường như So", []),

    # Rec 3385: Đã có TP. HCM, TP Thủ Đức
    ("🌧 🌧 🌧 TP. HCM : ĐƯỜNG NGẬP SÂU , KẸT XE KHÔNG LỐI THOÁT SAU TRẬN MƯA LỚN Chiều 12 / 9 , cơn mưa lớn kéo dài trên địa bàn TP Thủ Đức ( TP. HCM ) khiến nhiều tuyến đường bị ngập sâu .", [
        ([3, 4], [7, 8], 'NEG'),
        ([3, 4], [10, 11, 12, 13, 14], 'NEG'),
        ([32, 33, 34], [43, 44, 45], 'NEG'),
    ]),

    # Rec 3386: Đã có quận 9, Đỗ Xuân Hợp, Dương Đình Hội, Lê Văn Việt
    ("Rất nhiều nơi ở quận 9 đang bị ngập khá nặng , như Đỗ Xuân Hợp , Dương Đình Hội , Lê Văn Việt . . .", [
        ([4, 5], [7, 8, 9, 10], 'NEG'),
        ([13, 14, 15], [7, 8, 9, 10], 'NEG'),
        ([17, 18, 19], [7, 8, 9, 10], 'NEG'),
        ([21, 22, 23], [7, 8, 9, 10], 'NEG'),
    ]),

    # Rec 3387: Đã có đường Dương Đình Hội, Đỗ Xuân Hợp
    ("Trên đường Dương Đình Hội , đoạn từ đường 359 về chỗ giao với Đỗ Xuân Hợp , hàng loạt xe chết máy vì ngập , mong bà con chú ý .", [
        ([1, 2, 3, 4], [21, 22], 'NEG'),
        ([1, 2, 3, 4], [24], 'NEG'),
        ([14, 15, 16], [21, 22], 'NEG'),
        ([14, 15, 16], [24], 'NEG'),
    ]),

    # Rec 3388: Tiêu đề câu hỏi -> REJECT
    ("TP. HCM THƯỜNG XUYÊN NGẬP SAU MƯA CƠ QUAN CHỨC NĂNG NÓI GÌ ?", []),

    # Rec 3389: Đã có TP. HCM
    ("Sau những cơn mưa lớn , nhiều con đường tại TP. HCM rơi vào cảnh ngập úng , nhiều phương tiện chết máy .", [
        ([10, 11], [14, 15, 16], 'NEG'),
        ([10, 11], [21, 22], 'NEG'),
    ]),

    # Rec 3390: Cắt cụt đầu câu 'Thủ Đức )' -> REJECT
    ("Thủ Đức ) đã bị ngập nước .", []),

    # Rec 3391: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Đoạn này đang ngập nước khá sâu , bà con qua đây cần lưu ý .", [
        ([1], [5, 6, 7, 8, 9], 'NEG'),
    ]),

    # Rec 3392: Cắt cụt đuôi câu 'NGẬP . . .' -> REJECT
    ("Tại TP. Hồ Chí Minh , ĐÓN TẾT RỘN RÀNG - NGẬP . . .", []),

    # Rec 3393: Đã có TPHCM, hầm chui trước cổng Bến xe Miền Đông mới
    ("HẦM CHUI 75 TỶ ĐỒNG Ở CỬA NGÕ TPHCM LẠI NGẬP NẶNG SAU MƯA ☔ ️ 🌧 ️ Hơn 20h tối nay ( 4 / 7 ) , hầm chui trước cổng Bến xe Miền Đông mới , theo hướng TP. HCM đi TP Biên Hoà ( Đồng Nai ) vẫn còn ngập lênh láng .", [
        ([8], [10, 11], 'NEG'),
        ([28, 29, 30, 31, 32, 33, 34, 35, 36], [52, 53, 54], 'NEG'),
    ]),

    # Rec 3394: Cắt cụt đuôi câu 'từ 30 -' -> REJECT
    ("Tại TP. Hồ Chí Minh , Theo ghi nhận , nước ngập từ 30 -", []),

    # Rec 3395: Đã có Hầm chui trước Bến xe Miền Đông, TP Thủ Đức
    ("Hầm chui trước Bến xe Miền Đông ( TP Thủ Đức ) mưa cũng ngập , không mưa cũng ngập .", [
        ([0, 1, 2, 3, 4, 5, 6], [12, 13, 14], 'NEG'),
        ([0, 1, 2, 3, 4, 5, 6], [16, 17, 18, 19], 'NEG'),
        ([8, 9, 10], [12, 13, 14], 'NEG'),
        ([8, 9, 10], [16, 17, 18, 19], 'NEG'),
    ]),

    # Rec 3396: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Người dân khổ sở “ đạp gió rẽ sóng ” đi qua , nhiều xe tắt máy 🥲 Theo Báo Công An TPHCM", [
        ([1], [5, 6], 'NEG'),
        ([1], [18, 19], 'NEG'),
    ]),

    # Rec 3397: Đã có SÀI GÒN
    ("🛑 TRIỀU CƯỜNG VƯỢT ĐỈNH NĂM 2020 , NGƯỜI DÂN SÀI GÒN LỘI NƯỚC NẤU CƠM TỐI Theo dự báo , đỉnh triều ngày 6 - 11 tại trạm Phú An trên sông Sài Gòn là 1 , 68m vào 18h , và trạm Nhà Bè trên kênh Đồng Điền là 1 , 72m lúc 17h .", [
        ([10, 11], [12, 13], 'NEG'),
    ]),

    # Rec 3398: Đã có Đường Lê Văn Việt, quận 9
    ("Đường Lê Văn Việt đoạn từ Lã Xuân Oai đến Đình Phong Phú ( quận 9 ) đang ngập sâu nha bà con .", [
        ([0, 1, 2, 3], [18, 19, 20], 'NEG'),
        ([14, 15], [18, 19, 20], 'NEG'),
    ]),

    # Rec 3399: CSGT (People Role) + Cắt cụt đuôi câu -> REJECT
    ("Tại TP. Hồ Chí Minh , HÌNH ẢNH ĐẸP VỀ CSGT GIÚP DÂN RA KHỎI TUYẾN ĐƯỜNG NGẬP Hình ảnh những cán bộ chiến sĩ CSGT dầm mưa điều hòa giao thông , di chuyển phương tiện bị chết máy của người dân lên khu vực an toàn trong những ngày qua tại TP Hồ Chí Minh đa", []),

    # Rec 3400: Đã có QL13, Hiệp Bình, Tô Ngọc Vân, Phạm Văn Đồng
    ("Một số tuyến đường tại Thủ Đức như QL13 , Hiệp Bình , Tô Ngọc Vân , Phạm Văn Đồng ngập sâu .", [
        ([8], [20, 21], 'NEG'),
        ([10, 11], [20, 21], 'NEG'),
        ([13, 14, 15], [20, 21], 'NEG'),
        ([17, 18, 19], [20, 21], 'NEG'),
    ]),
]

def test_triplets():
    flaws = 0
    print(f'Kiểm tra {len(batch34_data)} records...')
    for idx, (text, triplets) in enumerate(batch34_data, 3301):
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
        print('TẤT CẢ CÁC TRIPLETS CỦA BATCH 34 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!')
    else:
        print(f'TỔNG CỘNG PHÁT HIỆN {flaws} LỖI!')
    return flaws

if __name__ == '__main__':
    flaws = test_triplets()
    if flaws == 0:
        phase3_path = 'data/validate_label/thuan/phase3.txt'
        with open(phase3_path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        base_lines = lines[:3300]
        
        new_batch_lines = []
        for text, triplets in batch34_data:
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
