# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn Lô 28 (Rec 2701 - 2800) cho phase3.txt.
Tuân thủ tuyệt đối BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md
"""

batch28_data = [
    # 2701 (TP HCM)
    (
        "MƯA LỚN GÂY NGẬP NẶNG NHIỀU TUYẾN ĐƯỜNG Ở TP HCM Cơn mưa lớn chiều 7 / 10 khiến nhiều con đường ở TP. HCM ngập nặng .",
        [([9, 10], [3, 4], 'NEG')]
    ),
    # 2702 (quận Gò Vấp)
    (
        "Đặc biệt khu vực quận Gò Vấp cũ xảy ra ngập cục bộ .",
        [([4, 5, 6], [9, 10], 'NEG')]
    ),
    # 2703 (Nguyễn Văn Khối, Lê Văn Thọ)
    (
        "Các tuyến đường ngập nặng như : Nguyễn Văn Khối , Lê Văn Thọ",
        [([7, 8, 9], [3, 4], 'NEG'), ([11, 12, 13], [3, 4], 'NEG')]
    ),
    # 2704 (Bài phân tích nguyên nhân)
    (
        "Vì sao TP. HCM ngập nặng sau mưa lớn ?",
        []
    ),
    # 2705 (Dự án quy hoạch)
    (
        "Tại TP. Hồ Chí Minh , Kế hoạch : Chi 142 . 000 tỷ , làm 87 dự án từ 2026 - 2030 để xóa 50 điểm ngập .",
        []
    ),
    # 2706 (Cắt cụt)
    (
        "THƯƠNG TÂM QUÁ - SỰ CỐ ĐIỆN ĐAU LÒNG TRONG ĐÊM MƯA NGẬP TẠI TP. THỦ ĐỨC Trận mưa lớn rạng sáng ngày 8 / 10 đã làm ngập sâu nhiều tuyến hẻm và nhà dân tại khu vực TP.",
        []
    ),
    # 2707 (Thống kê danh sách)
    (
        "TP. HCM hiện có 159 điểm ngập thường xuyên , trong đó khu vực trung tâm có 24 tuyến được xếp vào nhóm ngập nặng .",
        []
    ),
    # 2708 (thành phố Thủ Đức)
    (
        "Đáng chú ý , 10 tuyến tập trung tại khu vực thành phố Thủ Đức ( cũ ) , thường xảy ra ngập khi mưa lớn kết hợp triều cường .",
        [([11, 12, 13, 14], [22], 'NEG')]
    ),
    # 2709 (phường Thủ Đức)
    (
        "Người thân bàng hoàng khi người đàn ông bị đɪệɴ ɢɪậᴛ тử ᴠᴏɴɢ ở TPHCM 😢 Sau nhiều giờ nước ngập do mưa lớn , người đàn ông ở phường Thủ Đức , TPHCM dọn dẹp căn nhà thì gặp nạn .",
        [([25, 26, 27], [18, 19], 'NEG')]
    ),
    # 2710 (Sài Gòn)
    (
        "Sài Gòn \" thất thủ \" sau cơn mưa lớn , phương tiện trục trặc , nước tràn vào nhà dân # POPSTV # TruyenHinhDongThap # Joey videoid : rFsZ4jTi8X0 - - - © Bản quyền của video này thuộc về Truyền Hình Đồng Tháp - đối tác POPS .",
        [([0, 1], [3, 4], 'NEG')]
    ),
    # 2711 (Sài Gòn)
    (
        "Sài Gòn ngập trong nước",
        [([0, 1], [2], 'NEG')]
    ),
    # 2712 (Nâng đường chống ngập)
    (
        "Người dân TPHCM khổ sở vì nhà thấp hơn đường gần 2m 😥 Đường Đặng Thùy Trâm , TPHCM đang được nâng nền hơn 1m để chống ngập , khiến nhiều nhà dân thấp hơn mặt đường 1 - 1 , 5m .",
        []
    ),
    # 2713 (Tranh luận nâng đường)
    (
        "Tại TP. Hồ Chí Minh , NÂNG ĐƯỜNG GẦN 2 MÉT : CHỐNG NGẬP HAY “ ĐUỔI ” NGẬP ?",
        []
    ),
    # 2714 (Thi công nâng nền)
    (
        "Đường Đặng Thùy Trâm , TP. HCM đang được nâng nền gần 2 mét để chống ngập .",
        []
    ),
    # 2715 (Cắt cụt)
    (
        "PHÒNG CSGT CÔNG AN TPHCM CẢNH BÁO 122 ĐIỂM NGẬP NƯỚC TRÊN ĐỊA BÀN TP.",
        []
    ),
    # 2716 (Hồ Chí Minh - Dự báo NEU)
    (
        "Hồ Chí Minh có thể ngập sâu hơn nửa mét",
        [([0, 1, 2], [3, 4, 5, 6, 7], 'NEU')]
    ),
    # 2717 (Fallback chuẩn hóa - Dự báo NEU)
    (
        "Tại TPHCM , Chủ động đề phòng ngập khu vực trũng thấp và ven sông .",
        [([1], [5, 6, 7], 'NEU')]
    ),
    # 2718 (Cảnh báo thủy kích)
    (
        "Tại TP. Hồ Chí Minh , Khách hàng lưu thông về phía Nhà Bè cũ , quận 7 , 4 , 8 cũ hết sức cẩn trọng , nếu nước ngập cao thì đừng cố di chuyển , tránh để xe gặp tình trạng thủy kích nhé !",
        []
    ),
    # 2719 (Hồ Chí Minh)
    (
        "Hồ Chí Minh ngập nhanh",
        [([0, 1, 2], [3, 4], 'NEG')]
    ),
    # 2720 (Fallback chuẩn hóa - Cảnh báo NEU)
    (
        "Tại TPHCM , Cảnh báo tiếp tục ngập sâu và rộng",
        [([1], [5, 6, 7], 'NEU')]
    ),
    # 2721 (đường Nguyễn Bình)
    (
        "Triều cường ngập gần nửa mét , người dân chèo xuồng đón con Chiều tối 10 / 10 , triều cường khiến đường Nguyễn Bình ( TP. HCM ) ngập khoảng 1 km , có nơi sâu gần nửa mét .",
        [([21, 22, 23], [27], 'NEG')]
    ),
    # 2722 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Hàng giờ liền , người dân phải canh con nước , chắn nước tràn vào",
        []
    ),
    # 2723 (TP. HCM - Câu hỏi tu từ NEU)
    (
        "Khi nào TP. HCM hết ngập ?",
        [([2, 3], [4, 5], 'NEU')]
    ),
    # 2724 (TP. HCM)
    (
        "🛑 CẢNH BÁO 122 ĐIỂM NGẬP NƯỚC TRÊN ĐỊA BÀN TP. HCM Thành phố Hồ Chí Minh đang có những đợt mưa lớn , triều cường dâng cao , nhiều tuyến đường bị ngập sâu , gây ùn ứ , xe chết máy và tiềm ẩn nguy cơ mất an toàn .",
        [([10, 11], [33, 34], 'NEG')]
    ),
    # 2725 (TP. HCM)
    (
        "🚨 TRIỀU CƯỜNG TP. HCM LÊN CAO , NGƯỜI DÂN CHẬT VẬT LỘI NƯỚC CHIỀU CUỐI TUẦN !",
        [([3, 4], [9, 10], 'NEG')]
    ),
    # 2726 (TPHCM)
    (
        "CẢNH BÁO 122 ĐIỂM NGẬP NƯỚC TRÊN ĐỊA BÀN TPHCM Thành phố Hồ Chí Minh đang có những đợt mưa lớn , triều cường dâng cao , nhiều tuyến đường bị ngập sâu , gây ùn ứ , xe chết máy và tiềm ẩn nguy cơ mất an toàn .",
        [([9], [31, 32], 'NEG')]
    ),
    # 2727 (Vũng Tàu, Bình Dương cũ -> Ngoại tỉnh)
    (
        "😵 Ngay lúc này 7 / 10 , Bình Dương tiếp tục giữ chuỗi \" hồi chiều trời mưa \" CSGT cảnh báo 122 điểm ngập ở TPHCM bao gồm khu vực Vũng Tàu và Bình Dương cũ .",
        []
    ),
    # 2728 (Phòng tránh ngập chung)
    (
        "Tại TP. Hồ Chí Minh , Mọi người xem để phòng tránh ngập nhé .",
        []
    ),
    # 2729 (Sài Gòn)
    (
        "🌊 Sài Gòn hôm nay không mưa mà vẫn ngập .",
        [([1, 2], [8], 'NEG')]
    ),
    # 2730 (Cắt cụt)
    (
        "🌊 Đợt triều cường cao nhất năm đã làm ngập nhi",
        []
    ),
    # 2731 (Hồ Chí Minh)
    (
        "Hồ Chí Minh bị ngập hơn 1 mét , khiến nhiều tài sản của người dân bị thiệt hại .",
        [([0, 1, 2], [4, 5, 6, 7], 'NEG')]
    ),
    # 2732 (Công Viên Nước Gò Vấp)
    (
        "❌ CV Làng Hoa Gò Vấp ✅ Công Viên Nước Gò Vấp 👉 Ơn đảng ơn nhà nước đã quy hoạch công viên công viên 2 trong 1 : mùa tết chơi hoa , mùa ngập chơi nước mưa nước cống .",
        [([7, 8, 9, 10, 11], [31], 'NEG')]
    ),
    # 2733 (Công viên Làng Hoa , Gò Vấp)
    (
        "⛈ Sau trận mưa tối qua : Công viên Làng Hoa sáng nay ở Gò Vấp vẫn ngập nước , giờ thành ' biển hoa ' luôn 😅 , có ai sáng này đi làm trễ nữa không ?",
        [([7, 8, 9, 10], [17, 18], 'NEG'), ([14, 15], [17, 18], 'NEG')]
    ),
    # 2734 (phường Gò Vấp)
    (
        "Cảnh xe máy để trong hầm 1 chung cư tại phường Gò Vấp , TP. HCM sáng nay ( 8 / 10 ) , nước ngập hơn 1m , nhiều xe máy , máy móc và thiết bị bị hư hỏng .",
        [([10, 11, 12], [24, 25, 26], 'NEG')]
    ),
    # 2735 (Gò Vấp)
    (
        "Vì sao Gò Vấp địa hình cao vẫn ngập nặng ?",
        [([2, 3], [7, 8], 'NEG')]
    ),
    # 2736 (Gò Vấp)
    (
        "Có địa hình tương đối cao , Gò Vấp vẫn ngập sâu bởi nhiều điểm trũng , cống quá tải và nước khó thoát ra kênh khi mưa lớn gặp triều cường .",
        [([7, 8], [10, 11], 'NEG')]
    ),
    # 2737 (Cityland Park Hills , Gò Vấp)
    (
        "Ghi nhận sáng 8 / 10 tại KDC Cityland Park Hills , Gò Vấp : nhiều hầm vẫn ngập 1 - 1 , 5m .",
        [([7, 8, 9, 10], [17], 'NEG'), ([12, 13], [17], 'NEG')]
    ),
    # 2738 (Gò Vấp)
    (
        "🌧 ️ GÒ VẤP MƯA LỚN , HẦM XE NGẬP NƯỚC – NGOÀI ĐƯỜNG THÀNH “ SÔNG ” Cơn mưa lớn khiến nhiều khu vực ở Gò Vấp ngập nhanh .",
        [([2, 3], [9, 10], 'NEG'), ([26, 27], [28, 29], 'NEG')]
    ),
    # 2739 (khu nam TP. HCM)
    (
        "Chiều 10 . 10 , triều cường dâng cao khiến nhiều tuyến đường khu nam TP. HCM ngập sâu .",
        [([11, 12, 13, 14], [15, 16], 'NEG')]
    ),
    # 2740 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Xe máy chết máy , người dân phải dắt bộ , có người đứng chờ vì không dám qua đoạn ngập .",
        [([1], [22], 'NEG')]
    ),
    # 2741 (TP HCM)
    (
        "TRIỀU CƯỜNG NHẤN CHÌM NHIỀU TUYẾN ĐƯỜNG Ở TPHCM 😭 Triều cường dâng cao chiều 10 / 10 khiến nhiều tuyến đường ở TP HCM ngập sâu , người dân chật vật dắt xe ch * t máy , hàng quán bị nước tràn vào .",
        [([23, 24], [25, 26], 'NEG')]
    ),
    # 2742 (Bài xã luận 159 điểm ngập)
    (
        "Tại TP. Hồ Chí Minh , TP HCM SAU MỖI TRẬN MƯA LỚN : 159 ĐIỂM NGẬP VÀ MỘT BÀI TOÁN CHƯA THỂ GIẢI QUYẾT DỨT ĐIỂM Những trận mưa lớn cuối tháng 9 , đầu tháng 10 tiếp tục cho thấy áp lực ngập nước tại TP HCM .",
        []
    ),
    # 2743 (Cắt cụt)
    (
        "Riêng ngày 30 / 9 , đường Phan Huy Ích ngập trên đ",
        []
    ),
    # 2744 (Sài Gòn)
    (
        "Tình hình mấy địa bàn ngập nước ở Sài Gòn còn ngập k ACE ?",
        [([8, 9], [5, 6], 'NEG')]
    ),
    # 2745 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Hôm qua k mưa mà triều cường ngập ghê quá",
        [([1], [8, 9, 10], 'NEG')]
    ),
    # 2746 (Bàn luận chính sách)
    (
        "NGẬP NGỤA VÌ MƯA VÀ TRIỀU , TP. HCM RÚT NGẮN THỜI GIAN GIẢI QUYẾT Sở Xây dựng TP. HCM cho biết trận mưa cuối tháng 9 và đầu tháng 10 vượt tần suất thiết kế của hệ thống thoát nước , khiến nhiều kênh rạch dâng cao và rút chậm .",
        []
    ),
    # 2747 (Ngân sách)
    (
        "Tại TP. Hồ Chí Minh , Hồ Chí Minh dành 142 . 000 tỷ đồng xử lý 50 điểm ngập",
        []
    ),
    # 2748 (HÓC MÔN , Đường Lê Quang Đạo)
    (
        "NHỮNG ĐIỂM NGẬP DO MƯA LỚN , NƯỚC KHÔNG THOÁT KỊP TẠI HÓC MÔN : − Đường Lê Quang Đạo : + Từ giao lộ Võ Thị Hồi đến giao lộ Nguyễn Thị Sóc .",
        [([16, 17, 18, 19], [2], 'NEG')]
    ),
    # 2749 (Kỹ thuật xe thủy kích)
    (
        "Tại TP. Hồ Chí Minh , 🌊 ĐIỀU ĐÁNG SỢ KHÔNG CHỈ LÀ NƯỚC NGẬP — MÀ LÀ \" THỦY KÍCH \" .",
        []
    ),
    # 2750 (TP. HCM)
    (
        "Mưa lớn kết hợp triều cường khiến nhiều khu vực tại TP. HCM ngập sâu .",
        [([8, 9], [10, 11], 'NEG')]
    ),
    # 2751 (Rao vặt phòng trọ)
    (
        "Tìm phòng Q2 Ko ngập ~ 6Tr Mình cần tìm 1 phòng studio cho 1 người ở khu vực Trần Não , Lương Định Của , . .",
        []
    ),
    # 2752 (Rao vặt phòng trọ)
    (
        "Tại TP. Hồ Chí Minh , khu vực An Khánh , ko ngập , giá tầm 6Tr .",
        []
    ),
    # 2753 (Cắt cụt lửng lơ)
    (
        "Tại TP. Hồ Chí Minh , Hồ Chí Minh ) sáng nay vẫn còn ngập sâu .",
        []
    ),
    # 2754 (Gò Vấp)
    (
        "Gò Vấp đã ngập , đường giờ như biển mấy quận khác sao rồi .",
        [([0, 1], [3], 'NEG')]
    ),
    # 2755 (đường Nguyễn Văn Khối , Lê Văn Thọ)
    (
        "Các chiến sĩ PCCC & CHCN TP. HCM cứu chú chó nhỏ giữa dòng nước ngập ở TP. HCM Khoảng 21h ngày 7 / 10 , vài giờ sau trận mưa lớn tại TP. HCM , đường Nguyễn Văn Khối , Lê Văn Thọ ( phường Thông Tây Hội ) vẫn ngập sâu .",
        [([36, 37, 38, 39], [51, 52], 'NEG'), ([41, 42, 43], [51, 52], 'NEG')]
    ),
    # 2756 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Đoạn ngập kéo dài 400 - 500",
        []
    ),
    # 2757 (TP. HCM)
    (
        "Đường ngập từ chiều qua tới sáng nay ở TP. HCM Anh em sáng nay đi làm có ổn không ?",
        [([9, 10], [1], 'NEG')]
    ),
    # 2758 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Để người từ nơi khác đến chủ động tránh điểm ngập , phường Tam Bình , TP.",
        []
    ),
    # 2759 (Giới thiệu app)
    (
        "Tại TP. Hồ Chí Minh , Vị trí , mức độ ngập và hình ảnh thực tế có thể được gửi trực tiếp , giúp lựa chọn lộ trình phù hợp .",
        []
    ),
    # 2760 (Giới thiệu app)
    (
        "Tại TP. Hồ Chí Minh , Hồ Chí Minh ) , người dân có thể gửi vị trí , mức độ ngập và hình ảnh thực tế qua ứng dụng “ Tam Bình kết nối ” .",
        []
    ),
    # 2761 (TPHCM)
    (
        "TPHCM LẠI MƯA LỚN KÈM SẤM SÉT , NGHÌN NGƯỜI CHẬT VẬT VÌ NGẬP VÀ KẸT XE 😭 Mưa trắng trời kèm sấm chớp trút xuống trung tâm TPHCM trong chiều tối 7 / 10 , khiến nhiều tuyến đường ngập nặng , giao thông rối loạn .",
        [([0], [13], 'NEG')]
    ),
    # 2762 (TPHCM)
    (
        "Mưa như trút nước , người dân TPHCM bì bõm về nhà sau giờ làm",
        [([7], [8, 9], 'NEG')]
    ),
    # 2763 (TP HCM)
    (
        "một ngày trời mưa ngập nước xe chết máy ở TP HCM",
        [([10, 11], [4, 5], 'NEG')]
    ),
    # 2764 (Nam bộ - Cảnh báo NEU)
    (
        "Nam bộ tiếp tục mưa lớn , cảnh báo ngập do triều cường dâng cao # nambo # dubaothoitiet # trieucuong # muadong",
        [([0, 1], [7, 8, 9], 'NEU')]
    ),
    # 2765 (Fallback chuẩn hóa - Dự báo NEU)
    (
        "Tại TPHCM , Tình trạng ngập có thể nghiêm trọng hơn khi kết hợp với mưa lớn .",
        [([1], [6, 7, 8, 9, 10], 'NEU')]
    ),
    # 2766 (HCM)
    (
        "HCM ngập chìm trong nước .",
        [([0], [1, 2, 3, 4], 'NEG')]
    ),
    # 2767 (Đoạn đường Phạm Hữu Lầu)
    (
        "Đoạn đường Phạm Hữu Lầu , phường Tân Mỹ nước dâng cao tràn vào nhà dân , trôi cả giày dép khiến sinh hoạt khó khăn .",
        [([0, 1, 2, 3, 4], [8, 9, 10, 11, 12, 13], 'NEG')]
    ),
    # 2768 (Hồ Chí Minh - Dự báo NEU)
    (
        "Hồ Chí Minh có nơi có thể ngập sâu hơn nửa mét ‼",
        [([0, 1, 2], [5, 6, 7, 8, 9, 10], 'NEU')]
    ),
    # 2769 (TPHCM)
    (
        "Chiều 11 - 10 , triều cường trên sông Sài Gòn dâng nhanh , vượt mức báo động 3 , khiến nhiều tuyến đường trũng thấp tại TPHCM bị ngập cục bộ , ảnh hưởng đến sinh hoạt và di chuyển của người dân .",
        [([26], [28, 29, 30], 'NEG')]
    ),
    # 2770 (Thủ Dầu Một - Bình Dương -> Ngoại tỉnh)
    (
        "😳 Mọi năm cứ triều cường lên rồi rút nhanh , còn năm nay thì lên ối giời ơi luôn . nào là chợ BD , nào là c ôbg đành , Ngô Quyền . . khócc Khung cảnh nhiều nơi ở khu vực Thủ Dầu Một ngập nước , nhìn mà cứ ngỡ đ",
        []
    ),
    # 2771 (Bình Dương -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , Bình Dương lại mưa ngập nữa rồi",
        []
    ),
    # 2772 (Xã luận sống chung với ngập)
    (
        "Tại TP. Hồ Chí Minh , TP HCM định sống chung với ngập thế nào ?",
        []
    ),
    # 2773 (Sài Gòn sống chung với ngập)
    (
        "October 8 , 2026 Phạm Thu Hương Sài Gòn mấy chục năm chống ngập , giờ chuyển sang sống chung với ngập .",
        []
    ),
    # 2774 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Phạm Thu Hương Người dân dắt xe",
        []
    ),
    # 2775 (đường Trần Xuân Soạn , Quận 7)
    (
        "🐉 Triều cường dân cao ngập đường Trần Xuân Soạn Quận 7 chiều ngày 10 / 11 .",
        [([6, 7, 8, 9], [5], 'NEG'), ([10, 11], [5], 'NEG')]
    ),
    # 2776 (Sài Gòn)
    (
        "TIN NÓNG 🔥 🔥 🔥 🔥 🔥 🔥 Sài Gòn ngập nặng !",
        [([8, 9], [10, 11], 'NEG')]
    ),
    # 2777 (TP. HCM)
    (
        "Tình trạng ngập lụt nghiêm trọng tại TP. HCM ( Sài Gòn ) đang là vấn đề vô cùng cấp bách , đặc biệt trong các đợt mưa lớn dồn dập vào giờ cao điểm kết hợp với đỉnh triều cường dâng cao .",
        [([7, 8], [2, 3, 4, 5], 'NEG')]
    ),
    # 2778 (Thủ Dầu Một - Bình Dương -> Ngoại tỉnh)
    (
        "Đài KTTV Nam bộ dự báo triều cường có thể đạt 1 , 9 – 1 , 95m Thủ Dầu Một , vượt báo động 3 30 – 35cm , ngập .",
        []
    ),
    # 2779 (TP. HCM - Dự báo NEU)
    (
        "TP. HCM dự báo đỉnh triều chiều tối nay 12 / 10 , ae đi làm về lưu ý mấy tuyến đường bên khu Q7 , Nhà bè ! .",
        [([0, 1], [2, 3, 4, 5], 'NEU')]
    ),
    # 2780 (Nam Bộ - Dự báo NEU)
    (
        "Hôm nay ( 12 / 10 ) và ngày mai ( 13 / 10 ) là giai đoạn đỉnh triều cường tại Nam Bộ , nhiều nơi được cảnh báo ngập sâu . .",
        [([22, 23], [28, 29, 30, 31], 'NEU')]
    ),
    # 2781 (Cắt cụt)
    (
        "🌊 TRIỀU CƯỜNG NAM BỘ DÂNG CAO , CẢNH BÁO NGẬP NHIỀU KHU VỰC Tại TP.",
        []
    ),
    # 2782 (Tự nâng nền nhà)
    (
        "Nâng nền nhà 3 lần , tốn hơn 100 triệu đồng vẫn loay hoay chống ngập ở TP. HCM",
        []
    ),
    # 2783 (Tam Kỳ - Quảng Nam -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , Tam Kỳ ngớt mưa , loạt tuyến đường ngập úng chiều nay nước đã rút hết , cuộc sống trở lại bình thường , mong tất cả bình an 💚 .",
        []
    ),
    # 2784 (Cẩm nang an toàn)
    (
        "🌧 ️ HƯỚNG DẪN ĐẢM BẢO AN TOÀN KHI CÓ NGẬP LỤT TẠI ĐÔ THỊ Theo Đài Khí tượng Thủy văn Nam Bộ , đỉnh triều cường tại Thành phố Hồ Chí Minh dự báo vượt báo động 3 từ ngày 28 / 9 đến 30 / 9 / 2026 .",
        []
    ),
    # 2785 (đường Trần Xuân Soạn)
    (
        "Triều cường dâng cao làm ngập đường Trần Xuân Soạn # VnExpress",
        [([6, 7, 8, 9], [5], 'NEG')]
    ),
    # 2786 (đường Trần Xuân Soạn , Quận 7)
    (
        "🐉 Triều cường dân cao ngập đường Trần Xuân Soạn Quận 7 chiều ngày 11 / 10 / 2026 .",
        [([6, 7, 8, 9], [5], 'NEG'), ([10, 11], [5], 'NEG')]
    ),
    # 2787 (Đoạn đường Nguyễn Bình)
    (
        "Tuyến đường ngập 1 : Đoạn đường Nguyễn Bình từ ngã tư Lê Văn Lương - Nguyễn Bình đến khu vực dưới chân cầu Bà Sáu",
        [([5, 6, 7, 8], [2], 'NEG')]
    ),
    # 2788 (Hồ Chí Minh)
    (
        "Hồ Chí Minh đang diễn biến phức tạp , khiến nhiều tuyến đường thấp ven sông ngập sâu , giao thông ùn tắc vào giờ tan tầm .",
        [([0, 1, 2], [14, 15], 'NEG')]
    ),
    # 2789 (Phan Văn Trị , TP. HCM)
    (
        "Phan Văn Trị ngập nặng ⛈ ️ ⛈ ️ Cơn mưa lớn chiều 7 / 10 khiến nhiều con đường ở TP. HCM ngập nặng .",
        [([0, 1, 2], [3, 4], 'NEG'), ([21, 22], [23, 24], 'NEG')]
    ),
    # 2790 (Nguyễn Văn Khối , Lê Văn Thọ , Nguyễn Oanh)
    (
        "Các tuyến đường ngập nặng như : Nguyễn Văn Khối , Lê Văn Thọ , Nguyễn Oanh . . .",
        [([7, 8, 9], [3, 4], 'NEG'), ([11, 12, 13], [3, 4], 'NEG'), ([15, 16], [3, 4], 'NEG')]
    ),
    # 2791 (Hồ Chí Minh)
    (
        "Hồ Chí Minh ngập gần nửa mét , khiến hành trình đến trường của nhiều gia đình trở nên chật vật .",
        [([0, 1, 2], [3, 4, 5, 6], 'NEG')]
    ),
    # 2792 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Có phụ huynh phải cõng con lội nước , người dắt xe chết máy giữa đường , một số học sinh phải",
        []
    ),
    # 2793 (đường Đào Sư Tích)
    (
        "Triều cường dâng cao sáng 12 . 10 khiến đường Đào Sư Tích , xã Nhà Bè , TP. HCM ngập gần nửa mét .",
        [([8, 9, 10, 11], [18, 19, 20, 21], 'NEG')]
    ),
    # 2794 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nhiều học sinh phải xắn quần lội nước đến trường , phụ huynh cõng con , dắt xe chết máy hoặc đứng chờ nước rút , khiến buổi đi học đầu tuần thêm vất vả .",
        [([1], [7, 8], 'NEG')]
    ),
    # 2795 (TP. HCM)
    (
        "Triều cường gây ngập gần nửa mét ở TP. HCM , phụ huynh lội nước cõng con đến trường 🥹 # TNN",
        [([8, 9], [3, 4, 5, 6], 'NEG')]
    ),
    # 2796 (đường Lương Định Của)
    (
        "Block đường Lương Định Của đoạn ngập nước rồi ae",
        [([1, 2, 3, 4], [6, 7], 'NEG')]
    ),
    # 2797 (Gò Vấp)
    (
        "Cả Gò Vấp đã ngập , đường giờ như biển mấy quận khác sao rồi .",
        [([1, 2], [4], 'NEG')]
    ),
    # 2798 (Tranh luận nâng đường)
    (
        "Tại TP. Hồ Chí Minh , NÂNG ĐƯỜNG GẦN 2 MÉT : CHỐNG NGẬP HAY “ ĐUỔI ” NƯỚC VÀO NHÀ DÂN ?",
        []
    ),
    # 2799 (TPHCM)
    (
        "Đường ở TPHCM vẫn ngập nước giữa trời nắng .",
        [([2], [4, 5], 'NEG')]
    ),
    # 2800 (Tiêu đề bài phân tích)
    (
        "TP. HCM liên tục có mưa lớn , đường ngập sâu : Vì sao thời tiết ngày càng bất thường ?",
        []
    )
]

def format_line(text, triplets):
    formatted_triplets = []
    for asp, opn, pol in triplets:
        formatted_triplets.append(f"({asp}, {opn}, '{pol}')")
    triplets_str = "[" + ", ".join(formatted_triplets) + "]"
    return f"{text}####{triplets_str}\n"

def test_triplets():
    errors = 0
    punct = set(".,;:!?\"'“”‘’()[]{}#~-_/\\")
    for idx, (text, triplets) in enumerate(batch28_data, 2701):
        tokens = text.split()
        for asp, opn, pol in triplets:
            # Check aspect bounds
            for a in asp:
                if a < 0 or a >= len(tokens):
                    print(f"LỖI REC {idx}: Aspect index {a} out of range (len {len(tokens)})")
                    errors += 1
            # Check opinion bounds
            for o in opn:
                if o < 0 or o >= len(tokens):
                    print(f"LỖI REC {idx}: Opinion index {o} out of range (len {len(tokens)})")
                    errors += 1
            asp_str = " ".join([tokens[a] for a in asp])
            opn_str = " ".join([tokens[o] for o in opn])
            # Check punctuation edge
            if tokens[opn[0]] in punct or tokens[opn[-1]] in punct:
                print(f"CẢNH BÁO REC {idx}: Opinion dính dấu câu: '{opn_str}'")
                errors += 1
            if tokens[asp[0]] in punct or tokens[asp[-1]] in punct:
                print(f"CẢNH BÁO REC {idx}: Aspect dính dấu câu: '{asp_str}'")
                errors += 1
            # Check empty
            if not asp_str.strip() or not opn_str.strip():
                print(f"LỖI REC {idx}: Aspect hoặc Opinion rỗng")
                errors += 1
    if errors == 0:
        print("TẤT CẢ CÁC TRIPLETS CỦA BATCH 28 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!")
    else:
        print(f"CÓ {errors} LỖI CẦN SỬA!")
    return errors

if __name__ == '__main__':
    assert len(batch28_data) == 100, f"Expected 100 records, got {len(batch28_data)}"
    err_cnt = test_triplets()
    if err_cnt > 0:
        import sys
        sys.exit(1)
        
    phase3_path = "data/validate_label/thuan/phase3.txt"
    with open(phase3_path, "r", encoding="utf-8") as f:
        lines = [l for l in f.readlines() if l.strip()]
    
    base_2700 = lines[:2700]
    assert len(base_2700) == 2700, f"Expected 2700 existing lines, found {len(base_2700)}"
    
    new_lines = [format_line(t, tr) for t, tr in batch28_data]
    
    all_lines = base_2700 + new_lines
    with open(phase3_path, "w", encoding="utf-8") as f:
        f.writelines(all_lines)
        
    print(f"Successfully updated {len(all_lines)} lines to {phase3_path}!")
