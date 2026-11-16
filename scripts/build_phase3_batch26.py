# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn Lô 26 (Rec 2501 - 2600) cho phase3.txt.
Tuân thủ tuyệt đối BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md
"""

batch26_data = [
    # 2501 (TP. HCM)
    (
        "‼ ️ Kiếp nạn tối qua : Trận mưa lớn khiến nhiều khu vực tại TP. HCM bị ngập sâu , nước dâng nhanh làm đảo lộn sinh hoạt của người dân .",
        [([13, 14], [16, 17], 'NEG')]
    ),
    # 2502 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Trên các tuyến đường , hàng loạt xe tắt máy buộc người dắt bộ khó khăn qua đoạn tràn .",
        [([1], [11, 12], 'NEG')]
    ),
    # 2503 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Không chỉ vậy , nước tràn vào nh",
        []
    ),
    # 2504 (Khẩu hiệu châm biếm)
    (
        "Tại TP. Hồ Chí Minh , \" CHỐNG NGẬP CHO DÂN — MÀ DÂN NGẬP TRƯỚC .",
        []
    ),
    # 2505 (Đường Phan Huy Ích)
    (
        "Đường Phan Huy Ích ngập hơn 1 mét tối 30 / 9 .",
        [([0, 1, 2, 3], [4, 5, 6, 7], 'NEG')]
    ),
    # 2506 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Xe buýt chết máy , nước tràn vào nhà , dân mắc kẹt đến nửa đêm .",
        [([1], [8, 9, 10, 11], 'NEG')]
    ),
    # 2507 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Người sống ở đây 13 năm nói : năm nào cũng ngập — nhưng CHƯA BAO GI",
        []
    ),
    # 2508 (Chuẩn hóa lặp do scraping)
    (
        "TPHCM gần như ngày nào cũng ghi nhận ngập úng do mưa lớn , triều cường hoặc cả hai .",
        [([0], [8, 9], 'NEG')]
    ),
    # 2509 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Có nơi lượng mưa lên tới 290 - 330 mm , khiến nước thoát chậm , nhiều tuyến đường ngập sâu , phương tiện chết máy và nước tràn vào nhà dâ",
        []
    ),
    # 2510 (TP. HCM)
    (
        "Khổ sở vì triều cường dâng cao ở TP. HCM , người dân chật vật chờ nước rút 🥲 # TNN",
        [([8, 9], [5, 6], 'NEG')]
    ),
    # 2511 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Hồ Chí Minh vẫn đang khắc phục ảnh hưởng của những ngày mưa ngập vừa qua , mưa vừa , mưa to đến rất to được dự báo sẽ tiếp tục xuất hiện từ chiều tối 3 / 10 và có thể kéo dài n",
        []
    ),
    # 2512 (Fallback chuẩn hóa - Dự báo tương lai NEU)
    (
        "Tại TPHCM , Các tuyến đường sẽ ngập sâu khó khăn cho việc di chuyển đi lại .",
        [([1], [6, 7], 'NEU')]
    ),
    # 2513 (Cắt cụt)
    (
        "HỒ CHÍ MINH CHIỀU TỐI NAY CÒN NGẬP NHẸ Sau hai ngày liên tiếp mưa to xối xả kết hợp với triều cường gây ngập sâu nhiều tuyến đường , dự báo hôm nay , mưa giông ở TP.",
        []
    ),
    # 2514 (Chỉ đạo hành chính ứng phó sơ tán)
    (
        "KHẨN CẤP : TP. HCM YÊU CẦU SƠ TÁN KHI VÙNG NGẬP SÂU UBND TP. HCM vừa ban hành công văn khẩn , yêu cầu các sở , ngành và địa phương theo dõi chặt diễn biến thời tiết , trực ban 24 / 24h và bố trí lực lượng cảnh báo , hướng dẫn giao thông .",
        []
    ),
    # 2515 (Lời khuyên giao thông)
    (
        "Tại TP. Hồ Chí Minh , Hồ Chí Minh khuyến cáo người dân giảm tốc độ , không cố vượt vùng ngập sâu khi mưa lớn",
        []
    ),
    # 2516 (TP HCM)
    (
        "TP HCM NGẬP NẶNG TRONG KHI SIÊU DỰ ÁN CHỐNG NGẬP 10 . 000 TỶ CHƯA VẬN HÀNH Những ngày qua , nhiều khu vực TP HCM tiếp tục ngập nặng khi mưa lớn kết hợp triều cường .",
        [([0, 1], [2, 3], 'NEG')]
    ),
    # 2517 (Phan Huy Ích)
    (
        "KỲ LẠ : MƯA TẠNH , NƯỚC VẪN DÂNG CAO TRÊN PHAN HUY ÍCH 😲 Khu vực Phan Huy Ích ( phường Tân Sơn ) sau trận mưa lớn tối 1 - 10 vẫn chìm trong ngập khoảng 1 km dù mưa đã ngớt .",
        [([17, 18, 19], [34, 35, 36], 'NEG')]
    ),
    # 2518 (phường Thủ Đức)
    (
        "MƯA XUỐNG , ĐƯỜNG THÀNH SÔNG , NHÀ DÂN MÊNH MÔNG NƯỚC Gần 12h đêm 30 / 9 / 2026 , hàng trăm hộ dân sinh sống ở phường Thủ Đức ( TP. HCM ) chạy ngập .",
        [([24, 25, 26], [32], 'NEG')]
    ),
    # 2519 (TPHCM)
    (
        "Cơn mưa chiều 4 - 10 chỉ kéo dài trong thời gian ngắn nhưng khiến nhiều tuyến đường ở TPHCM ngập nước , người dân bì bõm di chuyển .",
        [([16], [17, 18], 'NEG')]
    ),
    # 2520 (ngã tư Hàng Xanh kẹt cứng không ngập)
    (
        "Người dân dầm mưa giữa dòng xe kẹt cứng ở ngã tư Hàng Xanh Chiều tối 1 / 10 , mưa lớn trút xuống TPHCM đúng giờ tan tầm .",
        []
    ),
    # 2521 (Hàng Xanh ùn tắc không ngập)
    (
        "Khu vực Hàng Xanh ùn tắc kéo dài , dòng xe ken đặc , nhiều thời điểm gần như đứng yên .",
        []
    ),
    # 2522 (Danh sách có Bình Dương cũ, Bà Rịa Vũng Tàu cũ -> Ngoại tỉnh)
    (
        "📍 159 điểm ngập thường xuyên tại TP. HCM ( gồm TP. HCM cũ , Bình Dương cũ , Bà Rịa - Vũng Tàu cũ ) · TP. HCM cũ : 76 điểm .",
        []
    ),
    # 2523 (Bố trí máy bơm -> Kỹ thuật)
    (
        "TP. HCM bố trí máy bơm di động xử lý điểm ngập .",
        []
    ),
    # 2524 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Lại mưa to . . lại ngập .",
        [([1], [9], 'NEG')]
    ),
    # 2525 (Hỏi mua chung cư tránh ngập -> BĐS)
    (
        "Tại TP. Hồ Chí Minh , SAU TRẬN NGẬP TỐI 1 / 10 : CÓ NÊN MUA CHUNG CƯ ĐỂ TRÁNH NGẬP ?",
        []
    ),
    # 2526 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nhiều tuyến đường ngập , có chỗ nước lên quá đầu gối , xe chết máy hàng loạt .",
        [([1], [6], 'NEG')]
    ),
    # 2527 (TP. HCM)
    (
        "Ngày đầu tiên của tháng 10 với nhiều người tại TP. HCM là 1 ngày ám ảnh … mưa lớn gây ngập , nhiều tuyến đường tắc cứng … có người mất 3 , 4 tiếng mới về đến nhà , người thì chọn ở lại công ty ! ! !",
        [([10, 11], [21], 'NEG')]
    ),
    # 2528 (TP. HCM)
    (
        "☔ Mùa mưa ở TP. HCM đôi khi chỉ cần một cơn mưa lớn là một số tuyến đường đã có thể xuất hiện tình trạng ngập , ùn xe hoặc di chuyển khó khăn .",
        [([4, 5], [23], 'NEG')]
    ),
    # 2529 (đường số 11)
    (
        "\" Khoảng 19h tối 30 - 9 , nước từ rạch Thủ Đức bất ngờ dâng nhanh rồi tràn qua bờ kè , nhấn chìm hàng trăm căn nhà quanh đường số 11 ( phường Thủ Đức , TP. HCM ) , có đoạn ngập sâu hơn 1m .",
        [([25, 26, 27], [39, 40, 41, 42], 'NEG')]
    ),
    # 2530 (Tuyến đường Tô Ngọc Vân)
    (
        "Tuyến đường Tô Ngọc Vân bị ngập cục bộ 1 số đoạn làm 2 oto phải gọi cứu hộ .",
        [([0, 1, 2, 3, 4], [6, 7], 'NEG')]
    ),
    # 2531 (tuyến đường Tô Ngọc Vân)
    (
        "Cơn mưa lớn chiều nay kéo dài hơn 1h làm ngập cục bộ tại tuyến đường Tô Ngọc Vân , 2 xe Oto phải gọi cứu hộ .",
        [([12, 13, 14, 15, 16], [9, 10], 'NEG')]
    ),
    # 2532 (Thủ Đức)
    (
        "mưa lớn trút xuống khu vực Thủ Đức ( TP HCM ) khiến nhiều tuyến đường ngập sâu .",
        [([5, 6], [13, 14], 'NEG')]
    ),
    # 2533 (Cắt cụt)
    (
        "Khu vực giao với đường Linh Đông ngập nặng nhất , dòng nước cuồn c",
        []
    ),
    # 2534 (ĐƯỜNG PHAN HUY ÍCH)
    (
        "ĐƯỜNG PHAN HUY ÍCH BIẾN THÀNH SÔNG SAU MƯA LỚN Ở TP. HCM Tối 1 - 10 , sau mưa lớn tại TP. HCM , nước vẫn dâng cao trên đường Phan Huy Ích , phường Tân Sơn , kéo dài khoảng 1km đến hơn 21h .",
        [([0, 1, 2, 3], [4, 5, 6], 'NEG')]
    ),
    # 2535 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Nhiều xe máy phải dẫn bộ , ôtô gặp khó khăn , nh",
        []
    ),
    # 2536 (đường Phan Huy Ích)
    (
        "Thành phố Hồ Chí Minh ngập chấn động trên đường Phan Huy Ích",
        [([7, 8, 9, 10], [4, 5], 'NEG')]
    ),
    # 2537 (Đường Phan Huy Ích)
    (
        "Đường Phan Huy Ích , cứ mưa là ngập . . .",
        [([0, 1, 2, 3], [7], 'NEG')]
    ),
    # 2538 (Châm biếm chung)
    (
        "Tại TP. Hồ Chí Minh , năm nào cũng lấy tiền để chống ngập !",
        []
    ),
    # 2539 (Đường Phan Huy Ích)
    (
        "Đường Phan Huy Ích ở TP. HCM , ngập sâu cả mét nhiều người mắc kẹt tới nửa đêm",
        [([0, 1, 2, 3], [8, 9, 10, 11], 'NEG')]
    ),
    # 2540 (Bàn luận giải pháp CSDL)
    (
        "Tại TP. Hồ Chí Minh , Hồ Chí Minh triển khai nhiều giải pháp xử lý ngập đô thị , trong đó xây dựng cơ sở dữ liệu thoát nước , nền tảng tiếp nhận phản ánh ngập trực tuyến và hệ thống hỗ trợ ra quyết định .",
        []
    ),
    # 2541 (Fallback chuẩn hóa - Dự báo tương lai NEU)
    (
        "Tại TPHCM , Khả năng có mưa to gây ngập vào giờ tan tầm .",
        [([1], [7, 8], 'NEU')]
    ),
    # 2542 (Bàn luận Sài Gòn xưa)
    (
        "Tui nghe nói là Sài Gòn xưa chưa bị bê tông hóa , kinh rạch còn nhiều , nên đường sá hiếm khi bị ngập .",
        []
    ),
    # 2543 (Cắt cụt)
    (
        "Thiệt ra là hiếm chứ không phải không có , video này là video hiếm hoi quay lại cảnh đường trung tâm Sài Gòn ngập như sông hồi năm",
        []
    ),
    # 2544 (Sài Gòn)
    (
        "Sài Gòn mấy ngày nay mưa lớn , nhiều con đường ngập úng .",
        [([0, 1], [10, 11], 'NEG')]
    ),
    # 2545 (Người dân vất vả về nhà không ngập)
    (
        "Tại TP. Hồ Chí Minh , Người dân vất vả về nhà , nhiều người bức xúc .",
        []
    ),
    # 2546 (Kế hoạch rà soát điểm ngập)
    (
        "Sau những ngày nhiều tuyến đường tiếp tục biến thành sông , TP. HCM lại bước vào một đợt rà soát lớn để tìm nguyên nhân và xếp thứ tự ưu tiên xử lý các điểm ngập .",
        []
    ),
    # 2547 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Tối ngập nước , sáng kẹt xe .",
        [([1], [4, 5], 'NEG')]
    ),
    # 2548 (TP. HCM)
    (
        "Mưa lớn vào chiều 1 / 10 khiến nhiều tuyến đường tại TP. HCM ngập nước , giao thông di chuyển chậm và ùn ứ tại một số khu vực .",
        [([12, 13], [14, 15], 'NEG')]
    ),
    # 2549 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Trên những đoạn đường ngập , người dân phải giảm tốc , dắt xe hoặc tìm cách di chuyển qua dòng nước giữa lúc đường phố đô",
        []
    ),
    # 2550 (TP. HCM)
    (
        "TP. HCM và vùng phụ cận : Bản đồ “ điểm nóng ” ngập nặng mỗi khi mưa lớn Mùa mưa năm 2026 đang chứng kiến tình trạng ngập úng ngày càng nghiêm trọng tại TP. HCM và các khu vực giáp ranh .",
        [([0, 1], [13, 14], 'NEG')]
    ),
    # 2551 (Bình Dương cũ -> Ngoại tỉnh)
    (
        "🆘 Cảnh báo khẩn giữa đêm , nước cuồn cuồn tràn về đoạn cầu Khánh Vân ( Tân Uyên , Bình Dương cũ ) Nước từ đâu chưa rõ dồn dập đổ về đường DT747B lúc gần 00h , gây ngập , nhiều phương tiện chết máy , quay đầu .",
        []
    ),
    # 2552 (Bình Dương cũ -> Ngoại tỉnh)
    (
        "Khẩn 🆘 Cảnh báo giữa đêm , nước cuồn cuồn tràn về đoạn cầu Khánh Vân ( Tân Uyên , Bình Dương cũ ) Nước từ đâu chưa rõ dồn dập đổ về đường DT747B lúc gần 00h , gây ngập , nhiều phương tiện chết máy , quay đầu .",
        []
    ),
    # 2553 (Bình Dương cũ -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , Cập nhật ngay lúc này 🆘 2h sáng , lực lượng chức năng phường Tân Khánh ( Tân Uyên , Bình Dương cũ ) đã có mặt để hỗ đưa người người dân ra khỏi vùng ngập , đến nơi an toàn .",
        []
    ),
    # 2554 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nhìn cảnh nước ngập mà buôn bán cũng thấy khó chịu ghê luôn 😥 .",
        [([1], [5, 6], 'NEG')]
    ),
    # 2555 (Sài Gòn)
    (
        "Không phải ai cũng thua cuộc giữa dòng nước ngập ở Sài Gòn tối qua đâu = ) ) ) ( Ảnh từ : VnExpress )",
        [([9, 10], [7, 8], 'NEG')]
    ),
    # 2556 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Mưa lớn , ngập đường . . .",
        [([1], [6], 'NEG')]
    ),
    # 2557 (khu đô thị Sala)
    (
        "Gió lớn khiến cây xanh ở khu đô thị Sala chẻ đôi , nước ngập sâu ( phường An Khánh , TP. HCM ) , tối 1 / 10 .",
        [([6, 7, 8, 9], [14, 15], 'NEG')]
    ),
    # 2558 (Cắt cụt)
    (
        "TP. HCM SAU CƠN MƯA LỚN NGẬP CẢ LỐI VỀ Cơn mưa lúc hơn 16h chiều 1 / 10 / 2022 làm nhiều tuyến đường như Ung Văn Khiêm ( quận Bình Thạnh ) , đường Quốc Hương , Võ Văn Ngân , Nguyễn Duy Trinh , ( TP T",
        []
    ),
    # 2559 (TP. HCM)
    (
        "Mưa lớn xuất hiện tại nhiều khu vực TP. HCM và Nam Bộ , khiến một số tuyến đường ngập nước , giao thông gặp nhiều khó khăn .",
        [([7, 8], [16, 17], 'NEG')]
    ),
    # 2560 (Chỉ nói chung chung không địa danh)
    (
        "Hình ảnh người dân chật vật di chuyển giữa dòng nước cho thấy những ảnh hưởng rõ rệt của thời tiết đến sinh hoạt và đi lại .",
        []
    ),
    # 2561 (Dự án nâng nền)
    (
        "Nâng nền Quốc lộ 13 ở TP. HCM , chủ đầu tư lý giải và lên phương án hỗ trợ các hộ dân bị ảnh hưởng # VOVTPHCM # Quốclộ13 # nângnền # ngập # bụi",
        []
    ),
    # 2562 (Kỹ thuật máy bơm)
    (
        "TPHCM đặt máy bơm nước di động tại các điểm ngập .",
        []
    ),
    # 2563 (Kỹ thuật trạm bơm)
    (
        "5 trạm bơm đang hoạt động hết công suất , trong khi những vườn cây chuẩn bị phục vụ thị trường Tết vẫn từng giờ chờ nước rút .",
        []
    ),
    # 2564 (Nghiên cứu dự án giao thông)
    (
        "TP. HCM chuẩn bị mở rộng đường Ung Văn Khiêm và nghiên cứu dự án hơn 10 . 000 tỉ đồng với đường trên cao , nút giao đa tầng Hàng Xanh để giảm kẹt xe , ngập nước .",
        []
    ),
    # 2565 (TP. HCM)
    (
        "Mưa lớn tối 1 / 10 , nhiều tuyến đường TP. HCM ngập , xe cộ nối dài",
        [([8, 9], [10], 'NEG')]
    ),
    # 2566 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Nhiều phương tiện chết máy vì nước ngập sâu ở TP.",
        []
    ),
    # 2567 (Dự án giao thông giảm ngập)
    (
        "TPHCM sẽ mở rộng và làm đường trên cao trục Xô Viết Nghệ Tĩnh - Đinh Bộ Lĩnh , mở rộng đường Ung Văn Khiêm để giảm kẹt xe , ngập nước khu Hàng Xanh - Bình Triệu .",
        []
    ),
    # 2568 (phường Thạnh Mỹ Tây)
    (
        "Mưa lớn từ chiều 1 . 10 khiến nhiều tuyến đường ở phường Thạnh Mỹ Tây ( TP. HCM ) ngập nước kéo dài .",
        [([12, 13, 14, 15], [20, 21], 'NEG')]
    ),
    # 2569 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Qua nửa đêm , người còn mắc kẹt ngoài đường , người thức trắng chờ nước rút .",
        [([1], [7, 8], 'NEG')]
    ),
    # 2570 (Tuyến đường Phan Huy Ích)
    (
        "Tuyến đường Phan Huy Ích Gò Vấp tiếp tục là điểm ngập sâu vào tối 1 / 10 / 2026 sau trận ngập lịch sử hôm 30 / 9 / 2026 # thamtushowbiz # phanhuyich # ngaplut # ngapnuoc # ngap # TPHCM # tintuc",
        [([0, 1, 2, 3, 4], [9, 10], 'NEG')]
    ),
    # 2571 (đường Nguyễn Văn Khối)
    (
        "TP. HCM : Cơn mưa lớn chiều tối khiến đường Nguyễn Văn Khối ngập sâu hơn nửa mét , biến thành biển nước suốt hơn 2 tiếng chưa rút .",
        [([9, 10, 11, 12], [13, 14, 15, 16, 17], 'NEG')]
    ),
    # 2572 (Kiến nghị cử tri)
    (
        "Cử tri TP. HCM kiến nghị nghiên cứu giải pháp chống ngập , xử lý lấn chiếm lòng lề đường 👇",
        []
    ),
    # 2573 (Phú Mỹ Hưng)
    (
        "TP. HCM mưa lớn , cây bật gốc : CSGT chuẩn bị xe tải chở xe máy qua vùng ngập Mưa lớn ở TP. HCM kèm giông lốc làm cây xanh bật gốc , cành cây ngã xuống đường ở khu Phú Mỹ Hưng .",
        [([41, 42, 43], [19], 'NEG')]
    ),
    # 2574 (Đường Mã Lò)
    (
        "Đường Mã Lò ngập sâu sau mưa lớn , ông bà cụ U . 80 mắc kẹt hơn 2 giờ 🥹 # TNN",
        [([0, 1, 2], [3, 4], 'NEG')]
    ),
    # 2575 (đường Mã Lò)
    (
        "Hơn 2 giờ sau mưa , đường Mã Lò vẫn ngập sâu : ' Không biết làm sao về nhà '",
        [([6, 7, 8], [10, 11], 'NEG')]
    ),
    # 2576 (Kế hoạch hành chính)
    (
        "TP. HCM lên kế hoạch giải quyết 50 điểm ngập nặng",
        []
    ),
    # 2577 (TP. HCM)
    (
        "Học sinh TP. HCM lội nước bì bõm đến trường trong con hẻm 5 ngày ngập sâu",
        [([2, 3], [15, 16], 'NEG')]
    ),
    # 2578 (TPHCM)
    (
        "TPHCM sấm chớp đùng đùng , mưa lớn trút xuống khiến hàng loạt tuyến đường ngập sâu trong nước .",
        [([0], [15, 16], 'NEG')]
    ),
    # 2579 (Kỹ thuật máy bơm)
    (
        "TPHCM đặt máy bơm nước di động tại các điểm ngập",
        []
    ),
    # 2580 (TP HỒ CHÍ MINH)
    (
        "🌧 ️ MƯA LỚN , TRIỀU CƯỜNG Ở TP HỒ CHÍ MINH GÂY NGẬP NHIỀU TUYẾN ĐƯỜNG .",
        [([8, 9, 10, 11], [13], 'NEG')]
    ),
    # 2581 (TP. HCM)
    (
        "Mưa lớn chiều nay , đường TP. HCM ngập sâu : Xe chết máy , shipper phải tắt app - Báo Thanh Niên",
        [([6, 7], [8, 9], 'NEG')]
    ),
    # 2582 (Đường Phan Huy Ích)
    (
        "Đường Phan Huy Ích ngập sâu cả mét ở TP. HCM , nhiều người mắc kẹt tới nửa đêm - Báo Thanh Niên",
        [([0, 1, 2, 3], [4, 5, 6, 7], 'NEG')]
    ),
    # 2583 (đường Liên Khu 4 - 5)
    (
        "Cập nhật tình hình đường Liên Khu 4 - 5 Bình Tân trưa 13h40 … vẫn ngập chưa rút nước . .",
        [([4, 5, 6, 7, 8, 9], [16], 'NEG')]
    ),
    # 2584 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Mưa có chút mà thành sông luôn .",
        [([1], [7, 8], 'NEG')]
    ),
    # 2585 (Cắt tiền tố thừa vì thân bài có Liên Khu 4 - 5, Bình Tân)
    (
        "Mưa ngập sâu đoạn cuối Liên Khu 4 - 5 , Bình Hưng Hoà B , P Bình Tân ( giáp ranh Vĩnh Lộc ) .",
        [([6, 7, 8, 9], [1, 2], 'NEG'), ([17, 18], [1, 2], 'NEG')]
    ),
    # 2586 (Cắt cụt)
    (
        "Trước nguy cơ mưa lớn , triều cường gây ngập đường , ảnh hưởng việc đi lại và an toàn của học sinh , các trường tại TP.",
        []
    ),
    # 2587 (Huyện Bình Chánh)
    (
        "Các khu dân cư ngập nước tại Huyện Bình Chánh & các quận vùng ven ở Thành Phố Hồ Chí Minh do mưa lớn với triều cường gây ngập sâu .",
        [([7, 8, 9], [28, 29], 'NEG')]
    ),
    # 2588 (xã Tân Nhựt, Tân Kiên)
    (
        "Điển hình là các khu dân cư tại xã Tân Nhựt hoặc khu vực Tân Kiên , Tân Vĩnh Lộc bị ngập sâu liên tiếp nhiều ngày .",
        [([8, 9, 10], [19, 20], 'NEG'), ([14, 15], [19, 20], 'NEG')]
    ),
    # 2589 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nước ngập sâu biến đường sá , sân nhà thành \" sông \" , khiến người dân phải dùng xuồng ba lá , đem lưới ra giăng và bắt được nhiều loại cá nước ngọt ( cá trê , cá lau kính , cá rô ) dạt từ kênh rạch hoặc ao hồ lân cận . # viral # xuhuong # tintuc # xuhuongtiktok # tiktoknews",
        [([1], [4, 5], 'NEG')]
    ),
    # 2590 (Sài Gòn)
    (
        "Sài Gòn mùng 1 tháng 10 thất thủ : Mưa ngập , kẹt xe và cái kết bất ngờ khi chọn phương tiện giao thông văn minh là tàu Metro .",
        [([0, 1], [9, 10], 'NEG')]
    ),
    # 2591 (TPHCM)
    (
        "Giữa lúc đường bộ chôn chân chịu trận ngập lụt khốc liệt Hẻm TPHCM ngập sâu cả tuần , Metro đã thong thả đưa hành khách về đích an toàn , trả khách đúng giờ .",
        [([12], [13, 14], 'NEG')]
    ),
    # 2592 (Cắt cụt)
    (
        "Sau 10 năm triển khai , dự án chống ngập , triều cường hơn 10 . 000 tỷ đồng ở TP.",
        []
    ),
    # 2593 (Sài gòn)
    (
        "Sài gòn nước ngập luôn",
        [([0, 1], [3], 'NEG')]
    ),
    # 2594 (xã Tân Vĩnh Lộc)
    (
        "Hơn 7 ngày qua , nhiều hộ dân ở xã Tân Vĩnh Lộc , TP. HCM vẫn sống giữa những con hẻm ngập nước , phải đi xuồng , gửi xe bên ngoài và có nhà không còn chỗ khô để ngủ",
        [([9, 10, 11, 12], [22, 23], 'NEG')]
    ),
    # 2595 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nhiều đoạn đường nước ngập lênh láng , người dân di chuyển khá khó khăn .",
        [([1], [7, 8], 'NEG')]
    ),
    # 2596 (Cắt cụt không dấu câu)
    (
        "Tại TP. Hồ Chí Minh , Hơn 7 ngày qua , nhiều hộ dân ở xã Tân Vĩnh Lộc phải sống chung với cảnh ngập úng",
        []
    ),
    # 2597 (Sài Gòn)
    (
        "Sài Gòn mưa như trút nước , ngập đường sá , hàng trăm người ở TTTM không thấy lối về # vietdailylife",
        [([0, 1], [7], 'NEG')]
    ),
    # 2598 (TP. HCM - Câu hỏi tu từ NEU)
    (
        "Ngập nước : chuyện bình thường ở TP. HCM ?",
        [([7, 8], [0, 1], 'NEU')]
    ),
    # 2599 (Sài Gòn)
    (
        "\" Sài Gòn biến thành sông \" : Trận ngập lịch sử khiến cả xe buýt cũng bất lực !",
        [([1, 2], [9], 'NEG')]
    ),
    # 2600 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Mưa từ 5h chiều đến 9h tối , đường xá ngập , ùn tắc .",
        [([1], [13], 'NEG')]
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
    for idx, (text, triplets) in enumerate(batch26_data, 2501):
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
        print("TẤT CẢ CÁC TRIPLETS CỦA BATCH 26 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!")
    else:
        print(f"CÓ {errors} LỖI CẦN SỬA!")
    return errors

if __name__ == '__main__':
    assert len(batch26_data) == 100, f"Expected 100 records, got {len(batch26_data)}"
    err_cnt = test_triplets()
    if err_cnt > 0:
        import sys
        sys.exit(1)
        
    phase3_path = "data/validate_label/thuan/phase3.txt"
    with open(phase3_path, "r", encoding="utf-8") as f:
        lines = [l for l in f.readlines() if l.strip()]
    
    base_2500 = lines[:2500]
    assert len(base_2500) == 2500, f"Expected 2500 existing lines, found {len(base_2500)}"
    
    new_lines = [format_line(t, tr) for t, tr in batch26_data]
    
    all_lines = base_2500 + new_lines
    with open(phase3_path, "w", encoding="utf-8") as f:
        f.writelines(all_lines)
        
    print(f"Successfully updated {len(all_lines)} lines to {phase3_path}!")
