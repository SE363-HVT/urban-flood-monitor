# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn Lô 27 (Rec 2601 - 2700) cho phase3.txt.
Tuân thủ tuyệt đối BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md
"""

batch27_data = [
    # 2601 (TP. HCM)
    (
        "Thêm một buổi tối người dân TP. HCM rồng rắn lội nước dắt xe về nhà",
        [([6, 7], [10, 11], 'NEG')]
    ),
    # 2602 (Thái Lan -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , NGẬP LỤT DIỆN RỘNG TẠI THÁI LAN",
        []
    ),
    # 2603 (SÀI GÒN)
    (
        "# CapCut SÀI GÒN NHỮNG NGÀY MƯA - GIÓ - NGẬP . .",
        [([1, 2], [8], 'NEG')]
    ),
    # 2604 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Mưa ngập hết cả rồi các bác ơi !",
        [([1], [4], 'NEG')]
    ),
    # 2605 (quận Bình Thạnh)
    (
        "Chiều ngày 1 / 10 sau cơn mưa 2 tiếng ở Sài Gòn quận Bình Thạnh ngập nước # saigon # mưa # tiktok # binhthanh # ngapnuoc",
        [([12, 13, 14], [15, 16], 'NEG')]
    ),
    # 2606 (chợ Tân Sơn Nhất)
    (
        "Mưa lớn tối 1 / 10 khiến nhiều nơi ở TP HCM ngập nặng , tại chợ Tân Sơn Nhất nước ngập hơn nửa mét .",
        [([16, 17, 18, 19], [21, 22, 23, 24], 'NEG')]
    ),
    # 2607 (đường Tam Bình)
    (
        "Sau 19 năm với hai lần tự bỏ tiền nâng nền nhà , người dân tại con hẻm trên đường Tam Bình vẫn phải sống chung với cảnh ngập úng vì hạ tầng thoát nước chỉ được làm dở dang ở đầu hẻm # f247 # tphcm # ngapung # hatang # duongtambinh",
        [([18, 19, 20], [28, 29], 'NEG')]
    ),
    # 2608 (Fallback chuẩn hóa - POS)
    (
        "Tại TPHCM , Lưu ý , hẻm nhà khu tôi ở ít khi ngập nước lắm .",
        [([1], [9, 10, 11, 12], 'POS')]
    ),
    # 2609 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Chở khách ra sân bay nhưng tài xế mắc kẹt 6 – 7 tiếng giữa đường ngập gần 1 mét .",
        [([1], [17, 18, 19, 20], 'NEG')]
    ),
    # 2610 (Khu Nam)
    (
        "Mưa lớn cộng triều cường , Khu Nam ngập triền miên .",
        [([6, 7], [8, 9, 10], 'NEG')]
    ),
    # 2611 (Hỏi chung chung)
    (
        "Tại TP. Hồ Chí Minh , Vậy có cách nào chống ngập không ?",
        []
    ),
    # 2612 (Thống kê 6 cống dự án)
    (
        "Dự án chống ngập 10 . 000 tỷ đồng với 6 cống ngăn triều : Bến Nghé , Tân Thuận , Phú Xuân , Mương Chuối , Cây Khô , Phú Định , vận hành thông minh bằng SCADA .",
        []
    ),
    # 2613 (Hỏi thăm tình hình Khu Nam)
    (
        "Tại TP. Hồ Chí Minh , Anh chị ở Khu Nam thấy tình hình ngập dạo này thế nào ?",
        []
    ),
    # 2614 (đường Phan Huy Ích)
    (
        "Sau trận mưa lớn chiều tối 30 / 9 , đường Phan Huy Ích và phường Thủ Đức ở TP. HCM ngập sâu , ảnh hưởng nghiêm trọng đến việc đi lại và sinh hoạt của người dân .",
        [([10, 11, 12, 13], [21, 22], 'NEG'), ([15, 16, 17], [21, 22], 'NEG')]
    ),
    # 2615 (đường Phan Huy Ích)
    (
        "Tối 30 / 9 , đường Phan Huy Ích , đoạn qua phường Tân Sơn , có nơi ngập khoảng 1 m , nước ngang yên xe máy và tràn vào nhà dân , xe buýt .",
        [([5, 6, 7, 8], [18, 19, 20, 21], 'NEG')]
    ),
    # 2616 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nhiều ô tô , xe máy và xe buýt chết máy giữa đường .",
        [([1], [11, 12], 'NEG')]
    ),
    # 2617 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Sau hơn 5 giờ , đến khoảng 22h30 , nước vẫn dâng cao , khiến giao thông qua khu vực gặp nhiều khó khăn .",
        [([1], [14, 15], 'NEG')]
    ),
    # 2618 (đường số 11 , phường Thủ Đức)
    (
        "Đến sáng 1 / 10 , nhiều nhà dân trên đường số 11 , phường Thủ Đức vẫn ngập sâu .",
        [([8, 9, 10], [17, 18], 'NEG')]
    ),
    # 2619 (hẻm 114)
    (
        "Tại TP. Hồ Chí Minh , Một số hẻm nhánh như hẻm 114 cũng ngập kéo dài từ tối hôm trước .",
        [([11, 12], [14, 15], 'NEG')]
    ),
    # 2620 (Hẻm 84)
    (
        "Tại TP. Hồ Chí Minh , Hẻm 84 được ghi nhận là một trong những khu vực ngập nặng nhất , với mực nước hơn nửa mét và nhiều nhà bị nước tràn vào .",
        [([6, 7], [17, 18, 19], 'NEG')]
    ),
    # 2621 (Mã lò, Phan Huy ích)
    (
        "Phan Huy ích nước ngập tới đích . . . Mã lò nước ngập tới . . . . . 🤣 # binhtan # muamua # nuocngap # malo # xuhuong",
        [([0, 1, 2], [3, 4], 'NEG'), ([11, 12], [13, 14], 'NEG')]
    ),
    # 2622 (Meme câu like)
    (
        "5 CON ĐƯỜNG HUYỀN THOẠI chuyên gia ngập lụt mùa mưa bão mà con dân Sài Gòn nào nghe tới cũng thấy sợ 🤣 🤣 🤣",
        []
    ),
    # 2623 (ngã tư hàng xanh, Nguyễn Hữu Cảnh)
    (
        "NGÃ TƯ HÀNG XANH HOT NHẤT LÚC NÀY 🥵 : kẹt xe , mưa ngập ở ngã tư hàng xanh , Nguyễn Hữu Cảnh , Võ Nguyên Giáp , chặn đường quanh BX Miền Đông cũ , hàng chục xe buýt đổi lộ trình , xếp hàng , đồng thời tắt GPS hàng loạt trên app Multigo 😭 🙏",
        [([16, 17, 18, 19], [13, 14], 'NEG'), ([21, 22, 23], [13, 14], 'NEG')]
    ),
    # 2624 (Mã Lò)
    (
        "Mã Lò 😆 # 2026 # saigon # mưa # ngập",
        [([0, 1], [10], 'NEG')]
    ),
    # 2625 (Quảng cáo BĐS)
    (
        "Ngập lụt tại TPHCM và câu chuyện Khu đô thị Vinhomes Sài Gòn Park Hóc môn",
        []
    ),
    # 2626 (Bến Tre -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , 😳 😳 😳 Ngập hơn nữa banh xe luôn rồi 🤣 🤣 🤣 # xuhuong # bentre71 🌴 🥥 # kcngiaolong # tiktok",
        []
    ),
    # 2627 (Đường Phan Huy Ích)
    (
        "Đường Phan Huy Ích lại hóa biển , nước lút yên xe , tràn vào cả xe buýt .",
        [([0, 1, 2, 3], [4, 5, 6], 'NEG')]
    ),
    # 2628 (Eco - POS)
    (
        "Nhưng ở Eco mưa xong ko ngập mà đẹp lắm ạ",
        [([2], [5, 6], 'POS')]
    ),
    # 2629 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Xe thì chết máy , nước thì ngập tới chân … nhưng đơn hàng vẫn phải giao !",
        [([1], [10, 11, 12], 'NEG')]
    ),
    # 2630 (Giới thiệu app)
    (
        "Tại TP. Hồ Chí Minh , Giải pháp mình làm free no ads cho cộng đồng cùng nhau chống ngập an toàn nhé 🙏",
        []
    ),
    # 2631 (Tản văn gia đình)
    (
        "Tại TP. Hồ Chí Minh , Tsv lần đầu thấy ngập nên quay cho bố và mẹ coi 😌 # tsv # ngaplut # giadinh",
        []
    ),
    # 2632 (Đường Mã Lò , Bình Tân)
    (
        "TP. HCM : Đường Mã Lò , Bình Tân ngập sau mưa lớn , nhiều xe chết máy",
        [([3, 4, 5], [8], 'NEG'), ([7, 8], [8], 'NEG')]
    ),
    # 2633 (đường Mã Lò , Bình Tân)
    (
        "Ngay lúc này , đường Mã Lò , Bình Tân , TP. HCM ngập nước sau mưa lớn .",
        [([4, 5, 6], [12, 13], 'NEG'), ([8, 9], [12, 13], 'NEG')]
    ),
    # 2634 (Người dân chật vật không ngập)
    (
        "Tại TP. Hồ Chí Minh , Hình ảnh hiện trường ghi nhận cảnh người dân chật vật qua khu vực .",
        []
    ),
    # 2635 (TP. HCM)
    (
        "TP. HCM ngập sâu sau mưa lớn , nước tràn vào xe buýt , hàng loạt phương tiện chết máy giữa đường",
        [([0, 1], [2, 3], 'NEG')]
    ),
    # 2636 (TP. HCM)
    (
        "TP. HCM ngập nặng sau mưa lớn trùng thời điểm triều cường tối 30 / 9 .",
        [([0, 1], [2, 3], 'NEG')]
    ),
    # 2637 (đường Phan Huy Ích)
    (
        "Cơ quan quản lý ghi nhận 12 tuyến đường bị ngập , trong đó đường Phan Huy Ích có nơi nước sâu khoảng 1 mét , nhiều xe máy , ô tô và xe buýt chết máy .",
        [([12, 13, 14, 15], [8], 'NEG')]
    ),
    # 2638 (Meme Diêm la)
    (
        "Tại TP. Hồ Chí Minh , CÁC VUA DIÊM LA KHEN NGỢI",
        []
    ),
    # 2639 (Gò Vấp, thành phố - Dự báo NEU)
    (
        "Nếu 04 / 10 chỉ ngập nặng ở Gò Vấp và vai khu vực thì mai khả năng sẽ ngập hầu hết thành phố .",
        [([6, 7], [4, 5], 'NEG'), ([19, 20], [15, 16], 'NEU')]
    ),
    # 2640 (Ung Văn Khiêm , Bình Thạnh)
    (
        "Kinh hoàng kẹt xe cầu Sài Gòn và ngập nước Ung Văn Khiêm , Bình Thạnh tối qua .",
        [([10, 11, 12], [8, 9], 'NEG'), ([14, 15], [8, 9], 'NEG')]
    ),
    # 2641 (Sài Gòn)
    (
        "Combo mưa lớn làm Sài Gòn thất thủ , dầm mưa dắt bộ quá cực .",
        [([4, 5], [6, 7], 'NEG')]
    ),
    # 2642 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Người dân : ' Ba lần nâng nhà nhưng vẫn ngập '",
        [([1], [13], 'NEG')]
    ),
    # 2643 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Đường phố ngập trong ánh đèn , người người vẫn phải vội vã len qua từng con đường ngập nước để trở về nhà .",
        [([1], [20, 21], 'NEG')]
    ),
    # 2644 (Sài Gòn)
    (
        "Cứ mưa như này thì đường nào ở Sài Gòn cũng ngập hết thôi kkk",
        [([8, 9], [11], 'NEG')]
    ),
    # 2645 (Trường Chinh, Phan Huy Ích)
    (
        "Cái đường từ KCN Tân Bình dưới cầu Tham Lương về Trường Chinh và Phan Huy Ích này mưa là ngập dữ lắm mọi người ơi , có khi đuối nước luôn đó .",
        [([11, 12], [18, 19], 'NEG'), ([14, 15, 16], [18, 19], 'NEG')]
    ),
    # 2646 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Bữa mình đi cố xong muốn tắt máy xe cũng phải quay đầu .",
        [([1], [10, 11], 'NEG')]
    ),
    # 2647 (Tiêu đề bài phân tích)
    (
        "Đã tìm ra nguyên nhân đường Phan Huy Ích ngập hơn 1 mét tối qua",
        []
    ),
    # 2648 (phường Bình Tân)
    (
        "Ai ở phường Bình Tân chịu cảnh này cho xin review với chứ ở SG bao năm lần đầu thấy ngập như vậy 🥲 Đường có ổ gà 3 cha con đi trên đường té ướt hết .",
        [([2, 3, 4], [21], 'NEG')]
    ),
    # 2649 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Đg ngồi lướt tik tok thấy nhà ngta nước ngập vô nhà các kiểu .",
        [([1], [10, 11], 'NEG')]
    ),
    # 2650 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , trận mưa hôm qua làm ngập rau hết trơn .",
        [([1], [7], 'NEG')]
    ),
    # 2651 (Yêu cầu hành chính)
    (
        "🚧 Các đơn vị quản lý được yêu cầu vận hành hiệu quả cống kiểm soát triều , cửa xả , trạm bơm , khơi thông dòng chảy và bố trí máy bơm di động tại các điểm ngập .",
        []
    ),
    # 2652 (Câu hỏi dự án)
    (
        "Gần 10 . 000 tỉ đồng được đầu tư , dự án chống ngập này sẽ vận hành ra sao ?",
        []
    ),
    # 2653 (TPHCM - Cảnh báo tương lai NEU)
    (
        "TPHCM mưa lớn dồn dập 3 ngày đầu tuần , cảnh báo ngập giờ tan tầm .",
        [([0], [10, 11, 12], 'NEU')]
    ),
    # 2654 (Dự án tương lai)
    (
        "Dự án chống ngập quy mô lớn nhất TP. HCM sẽ vận hành chính thức vào tháng 11 - 2026 .",
        []
    ),
    # 2655 (Ngân sách chống ngập)
    (
        "TP. HCM chi hơn 142 . 000 tỷ đồng cho bài toán chống ngập , đặt mục tiêu đến năm 2030 cơ bản xử lý ngập do mưa .",
        []
    ),
    # 2656 (Cắt cụt)
    (
        "Từ cống , kênh rạch , trạm bơm đến hệ thống thoát nước thông minh , mục tiêu cuối cùng vẫn là để người dân bớt cảnh kẹt xe , chết máy và nước",
        []
    ),
    # 2657 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Khi một số nơi chuẩn bị mưa thì Bình Tân đã ngập nữa bánh xe 🏊 🏊 ‍ ♂ ️ 📸 :",
        []
    ),
    # 2658 (TP. HCM)
    (
        "TP. HCM ngập sâu sau mưa lớn và triều cường Hello from Vietnam !",
        [([0, 1], [2, 3], 'NEG')]
    ),
    # 2659 (TP. HCM)
    (
        "Một thế giới , một gia đình ❤ ️ 🇻 🇳 Mưa lớn kết hợp triều cường khiến nhiều khu vực tại TP. HCM ngập sâu , có nơi nước dâng hơn một mét .",
        [([22, 23], [24, 25], 'NEG')]
    ),
    # 2660 (Dự kiến ngân sách)
    (
        "Tại TP. Hồ Chí Minh , Hồ Chí Minh dự kiến chi hơn 142 . 000 tỷ đồng cho các dự án giao thông , thủy lợi , thoát nước và chỉnh trang đô thị , tập trung xử lý 50 vị trí ngập nặng .",
        []
    ),
    # 2661 (Hồ Chí Minh lặp do scraping)
    (
        "Hồ Chí Minh lại ngập sâu như vậy ?",
        [([0, 1, 2], [4, 5], 'NEG')]
    ),
    # 2662 (Đánh giá dự án)
    (
        "Đầu tư hơn 7 . 000 tỷ cho các dự án chống ngập nhưng TP. HCM chỉ mới giải quyết được 3 / 50 điểm ngập .",
        []
    ),
    # 2663 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nhiều tuyến đường chính vẫn thành \" biển nước \" sau cơn mưa lớn # topcomments # mualon # denhnuoc # ngaplut # chongngap",
        [([1], [10, 11], 'NEG')]
    ),
    # 2664 (Sài Gòn)
    (
        "Sài Gòn ngập nước sau mưa",
        [([0, 1], [2, 3], 'NEG')]
    ),
    # 2665 (Trần Não , Quận 2)
    (
        "Trần Não Quận 2 Bị Ngập",
        [([0, 1], [4], 'NEG'), ([2, 3], [4], 'NEG')]
    ),
    # 2666 (Quận 12)
    (
        "Mưa ngập lũ tại Quận 12",
        [([4, 5], [1, 2], 'NEG')]
    ),
    # 2667 (Dĩ An Bình Dương -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , mưa ngập kiểu này chỉ có dĩ an bình dương thôi kk 🤣 giờ làm mòi gì nhậu anh em 🤣",
        []
    ),
    # 2668 (Hồ Chí Minh)
    (
        "Hồ Chí Minh 3 ngày liên tiếp ngập , ùn tắc | VTVWDB",
        [([0, 1, 2], [6], 'NEG')]
    ),
    # 2669 (Đinh Bộ Lĩnh , Bình Thạnh)
    (
        "Đường Đinh Bộ Lĩnh Bình Thạnh Ngập Lụt Hôm Nay : Thất Thủ Vì Mưa",
        [([1, 2, 3], [6, 7], 'NEG'), ([4, 5], [6, 7], 'NEG')]
    ),
    # 2670 (đường Nguyễn Văn Khối)
    (
        "Mưa lớn ở TP. HCM , đường Nguyễn Văn Khối ngập hơn nửa mét suốt 2 tiếng chưa rút # tiktoknews # tiktokthanhnien # thờitiết # mưalớn",
        [([6, 7, 8, 9], [10, 11, 12, 13], 'NEG')]
    ),
    # 2671 (TPHCM)
    (
        "Ngập sâu sau mưa lớn , người dân TPHCM dắt xe lội nước về nhà | Báo Lao Động",
        [([8], [0, 1], 'NEG')]
    ),
    # 2672 (TP. HCM)
    (
        "Cảnh khổ ở hẻm TP. HCM : Gần 1 tuần ngập nước , học sinh lội nước đi học # shorts",
        [([4, 5], [10, 11], 'NEG')]
    ),
    # 2673 (TPHCM)
    (
        "Tối 1 - 10 , đường ngập , kẹt xe , người dân TPHCM vất vả tan làm",
        [([13], [6], 'NEG')]
    ),
    # 2674 (Sài Gòn)
    (
        "Từ Đồng Nai Đến Sài Gòn Giờ NGẬP Thành Sông ! ! ! 😩",
        [([4, 5], [7, 8, 9], 'NEG')]
    ),
    # 2675 (Hướng dẫn app)
    (
        "Mưa lớn ở TPHCM , đây là cách kiểm tra đường ngập , kẹt xe ngay trên điện thoại !",
        []
    ),
    # 2676 (TP. HCM)
    (
        "Mưa lớn đúng giờ tan tầm chiều 7 . 10 khiến nhiều tuyến đường TP. HCM ngập nặng .",
        [([14, 15], [16, 17], 'NEG')]
    ),
    # 2677 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Đến hơn 19 giờ 30 , có nơi nước vẫn dâng sát yên xe máy , hàng loạt phương tiện chết máy .",
        [([1], [22, 23], 'NEG')]
    ),
    # 2678 (Chỉ đạo công văn)
    (
        "Sở NN - MT TPHCM đề nghị các đơn vị , địa phương kiểm tra đê bao , bờ kè , cửa van ngăn triều ; chuẩn bị lực lượng , phương tiện xử lý ngập úng và bảo đảm an toàn hồ chứa trước đợt triều cường , mưa lớn đầu tháng 10 .",
        []
    ),
    # 2679 (Fallback chuẩn hóa - Cảnh báo tương lai NEU)
    (
        "Tại TPHCM , Cảnh báo nhiều nơi ngập sâu do mưa lớn kết hợp triều cường cao .",
        [([1], [6, 7], 'NEU')]
    ),
    # 2680 (TPHCM - Cảnh báo tương lai NEU)
    (
        "TPHCM chiều tối nay tiếp tục mưa dông , đề phòng ngập # thoitiet # TPHCM # SGGP",
        [([0], [7, 8, 9], 'NEU')]
    ),
    # 2681 (TP HCM)
    (
        "🔴 NHIỀU ĐƯỜNG TP HCM NGẬP SÂU DO TRIỀU CƯỜNG CAO NHẤT TỪ ĐẦU NĂM Triều cường hơn 1 , 7 m - cao nhất từ đầu năm khiến nhiều tuyến đường TP HCM ngập sâu , xe chết máy , người dân đi lại khó khăn , chiều 10 / 10 .",
        [([3, 4], [5, 6], 'NEG')]
    ),
    # 2682 (Sài Gòn)
    (
        "🌧 ️ Ở ĐÂU CŨNG CÓ THỂ NGẬP , TRỪ VĂN PHÒNG VNO Sài Gòn mưa : đường ngập , xe lội nước , giày dép “ đi du lịch ” .",
        [([13, 14], [18], 'NEG')]
    ),
    # 2683 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , HỒ CHÍ MINH CÓ THỂ NGẬP SÂU HƠN NỬA MÉT Tại TP.",
        []
    ),
    # 2684 (Than thở chính sách)
    (
        "Tại TP. Hồ Chí Minh , dân chỉ biết chép miệng \" năm nào cũng xài tiền tỷ chống ngập \" . . .",
        []
    ),
    # 2685 (Lời khuyên kỹ thuật)
    (
        "Tại TP. Hồ Chí Minh , 🌧 ️ MƯA LỚN , NGẬP SÂU NGƯỜI ĐI XE MÁY CẦN LƯU Ý GÌ ?",
        []
    ),
    # 2686 (Sài Gòn)
    (
        "💦 Dạo này chiều nào Sài Gòn cũng đổ mưa lớn , phố xá biến thành sông , khiến bao chiến mã rơi vào cảnh chết máy giữa đường nếu không biết cách xử lý đúng .",
        [([5, 6], [14, 15, 16], 'NEG')]
    ),
    # 2687 (TPHCM)
    (
        "TPHCM mưa lớn , nhiều nơi vẫn ngập nặng sau một ngày # mualon # ngapsau # trieucuong",
        [([0], [7, 8], 'NEG')]
    ),
    # 2688 (TPHCM - Dự báo tương lai NEU)
    (
        "🌧 ️ 📢 Từ ngày 09 đến 12 / 10 / 2026 , triều cường tại TPHCM dự báo dâng cao , kết hợp mưa lớn có thể gây ngập úng .",
        [([13], [22, 23, 24, 25, 26], 'NEU')]
    ),
    # 2689 (TPHCM)
    (
        "🛑 🌊 CẢNH BÁO 122 ĐIỂM NGẬP NƯỚC TRÊN ĐỊA BÀN TPHCM Thành phố Hồ Chí Minh đang có những đợt mưa lớn , triều cường dâng cao , nhiều tuyến đường bị ngập sâu , gây ùn ứ , xe chết máy và tiềm ẩn nguy cơ mất an toàn .",
        [([11], [6, 7], 'NEG')]
    ),
    # 2690 (TP HCM)
    (
        "TRIỀU CƯỜNG NHẤN CHÌM NHIỀU TUYẾN ĐƯỜNG Ở TPHCM ‼ ️ Triều cường dâng cao chiều 10 / 10 khiến nhiều tuyến đường ở TP HCM ngập sâu , người dân chật vật dắt xe ch * t máy , hàng quán bị nước tràn vào .",
        [([24, 25], [26, 27], 'NEG')]
    ),
    # 2691 (sông Sài Gòn - NEU)
    (
        "📣 TIN TRIỀU CƯỜNG KHU VỰC SÔNG SÀI GÒN ⏰ Tin phát lúc 09 giờ , ngày 10 / 10 / 2026 ✅ Tình hình thủy văn đã qua 👉 Trong 24h qua , mực nước đỉnh triều cao nhất ngày tại hầu hết các trạm trên sông Sài Gòn lên nhanh và ở mức cao .",
        [([47, 48, 49], [53, 54, 55], 'NEU')]
    ),
    # 2692 (TP. HCM)
    (
        "Triều cường ở TP. HCM lên cao 1 , 86 m , nhiều tuyến đường ngập nặng Theo Đài Khí tượng Thủy văn Nam Bộ , triều cường đầu tháng 9 Âm lịch trên sông Sài Gòn đang lên nhanh .",
        [([3, 4], [15, 16], 'NEG')]
    ),
    # 2693 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , 😂 Người đi ô tô thì lo chết máy , người đi xe máy thì lo … mất dép .",
        [([1], [9, 10], 'NEG')]
    ),
    # 2694 (đường Trần Xuân Soạn)
    (
        "Triều cường ở TP. HCM lên cao 1 , 86 m , nhiều tuyến đường ngập nặng Theo ghi nhận của Tri Thức - Znews lúc 16h ngày 10 / 10 , triều cường dâng khiến đường Trần Xuân Soạn ( phường Tân Hưng ) xảy ra tình trạng ngập , người dân chật vật di chuyển .",
        [([37, 38, 39], [49], 'NEG')]
    ),
    # 2695 (TP HCM)
    (
        "Nhiều đường TP HCM ngập sâu do triều cường cao nhất từ đầu năm Triều cường hơn 1 , 7 m - cao nhất từ đầu năm khiến nhiều tuyến đường TP HCM ngập sâu , xe chếtmáy , người dân đi lại khó khăn , chiều 10 / 10 .",
        [([2, 3], [4, 5], 'NEG')]
    ),
    # 2696 (Bài phân tích nguyên nhân)
    (
        "Vì sao nhiều điểm ngập ở TP. HCM nay ngập lâu , nước rút chậm ?",
        []
    ),
    # 2697 (TP. HCM)
    (
        "Sau các đợt mưa lớn những ngày qua , một số khu vực tại TP. HCM ngập sâu , nước rút chậm .",
        [([14, 15], [16, 17], 'NEG')]
    ),
    # 2698 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Sở Xây dựng cho biết các vị trí ngập đều từng xuất hiện trong những năm qua , nhưng một số tuyến",
        []
    ),
    # 2699 (Thống kê danh sách)
    (
        "Tại TP. Hồ Chí Minh , Hồ Chí Minh hiện ghi nhận 159 điểm ngập , trong đó có 24 tuyến đường thường xuyên ngập nặng .",
        []
    ),
    # 2700 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Tình trạng ngập có nguy cơ nghiêm trọng hơn khi mưa lớn tr",
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
    for idx, (text, triplets) in enumerate(batch27_data, 2601):
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
        print("TẤT CẢ CÁC TRIPLETS CỦA BATCH 27 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!")
    else:
        print(f"CÓ {errors} LỖI CẦN SỬA!")
    return errors

if __name__ == '__main__':
    assert len(batch27_data) == 100, f"Expected 100 records, got {len(batch27_data)}"
    err_cnt = test_triplets()
    if err_cnt > 0:
        import sys
        sys.exit(1)
        
    phase3_path = "data/validate_label/thuan/phase3.txt"
    with open(phase3_path, "r", encoding="utf-8") as f:
        lines = [l for l in f.readlines() if l.strip()]
    
    base_2600 = lines[:2600]
    assert len(base_2600) == 2600, f"Expected 2600 existing lines, found {len(base_2600)}"
    
    new_lines = [format_line(t, tr) for t, tr in batch27_data]
    
    all_lines = base_2600 + new_lines
    with open(phase3_path, "w", encoding="utf-8") as f:
        f.writelines(all_lines)
        
    print(f"Successfully updated {len(all_lines)} lines to {phase3_path}!")
