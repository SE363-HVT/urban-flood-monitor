import ast, sys, re

sys.stdout.reconfigure(encoding='utf-8')

# Read raw batch 7
with open('scratch_batch7_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

assert len(blocks) == 100, f"Expected 100 blocks, got {len(blocks)}"

curated_lines = []

for idx, b in enumerate(blocks):
    rec_num = 601 + idx
    header, line = b.split('\n', 1)
    
    # Handle possible ##### or ####
    if '#####' in line:
        text, trip_str = line.split('#####', 1)
    elif '####' in line:
        text, trip_str = line.split('####', 1)
    else:
        text, trip_str = line, "[]"
        
    trip_str = trip_str.lstrip('#').strip()
    try:
        trips = ast.literal_eval(trip_str)
    except:
        trips = []
        
    c_text = text
    c_trips = trips
    
    # --- R601 to R610 ---
    if rec_num == 601:
        # TP. Hồ Chí Minh -> ngập sâu (NEG)
        c_trips = [([10, 11, 12, 13], [14, 15], 'NEG')]
    elif rec_num == 602:
        # Sài Gòn trước 1975 hoài niệm -> REJECT
        c_trips = []
    elif rec_num == 603:
        # Nguyễn Thị Thập -> ngập quá (NEG)
        c_trips = [([0, 1, 2], [7, 8], 'NEG')]
    elif rec_num == 604:
        # Bình luận chính trị/phát ngôn -> REJECT
        c_trips = []
    elif rec_num == 605:
        # Câu hỏi tu từ cảm thán -> REJECT
        c_trips = []
    elif rec_num == 606:
        # Câu hỏi tu từ / xã luận -> REJECT
        c_trips = []
    elif rec_num == 607:
        # Phóng sự siêu dự án 10.000 tỷ đình trệ -> REJECT
        c_trips = []
    elif rec_num == 608:
        # Châm biếm mạng xã hội -> REJECT
        c_trips = []
    elif rec_num == 609:
        # TP. HCM -> bị ngập nước do triều cường (NEG)
        c_trips = [([1, 2], [11, 12, 13, 14, 15, 16], 'NEG')]
    elif rec_num == 610:
        # Ý kiến đạo đức / ý thức người dân -> REJECT
        c_trips = []

    # --- R611 to R620 ---
    elif rec_num == 611:
        # phường Tam Bình -> vẫn ngập sâu (NEG)
        c_trips = [([11, 12, 13], [20, 21, 22], 'NEG')]
    elif rec_num == 612:
        # thành phố Thủ Đức -> ngập sâu (NEG)
        c_trips = [([12, 13, 14, 15], [24, 25], 'NEG')]
    elif rec_num == 613:
        # chợ Thủ Đức -> chống ngập (POS)
        c_trips = [([16, 17, 18], [13, 14], 'POS')]
    elif rec_num == 614:
        # đường Trần Xuân Soạn -> ngập (NEG)
        c_trips = [([39, 40, 41, 42], [38], 'NEG')]
    elif rec_num == 615:
        # TP. HCM -> bị ngập nước do triều cường (NEG)
        c_trips = [([12, 13], [5, 6, 7, 8, 9, 10], 'NEG')]
    elif rec_num == 616:
        # TPHCM -> CHẬT VẬT DI CHUYỂN GIỮA MÊNH MÔNG NƯỚC (NEG)
        c_trips = [([7], [8, 9, 10, 11, 12, 13, 14, 15], 'NEG')]
    elif rec_num == 617:
        # Đường Nguyễn Hữu Thọ -> ngập nhẹ (NEG), đường Long Hậu -> nặng (NEG)
        c_trips = [
            ([24, 25, 26, 27], [28, 29], 'NEG'),
            ([36, 37, 38], [32], 'NEG')
        ]
    elif rec_num == 618:
        # nguyễn bình -> ngập dữ (NEG), cầu cây khô -> ngập dữ (NEG)
        c_trips = [
            ([49, 50], [59, 60], 'NEG'),
            ([53, 54, 55], [59, 60], 'NEG')
        ]
    elif rec_num == 619:
        # đường Nguyễn Bình -> nước lên ngập (NEG)
        c_trips = [([5, 6, 7], [2, 3, 4], 'NEG')]
    elif rec_num == 620:
        # TP HCM -> XE CHẾT MÁY LA LIỆT (NEG)
        c_trips = [([12, 13], [0, 1, 2, 3, 4], 'NEG')]

    # --- R621 to R630 ---
    elif rec_num == 621:
        # đường Võ Văn Ngân -> ngập lụt nặng nề (NEG)
        c_trips = [([7, 8, 9, 10], [20, 21, 22, 23], 'NEG')]
    elif rec_num == 622:
        # đường Võ Văn Ngân -> chống ngập (POS), Tô Ngọc Vân -> chống ngập (POS)
        c_trips = [
            ([23, 24, 25, 26], [21, 22], 'POS'),
            ([28, 29, 30], [21, 22], 'POS')
        ]
    elif rec_num == 623:
        # TP Thủ Đức -> vẫn ngập trong nước (NEG)
        c_trips = [([32, 33, 34], [40, 41, 42, 43], 'NEG')]
    elif rec_num == 624:
        # TP Thủ Đức -> hay bị ngập nước (NEG)
        c_trips = [([13, 14, 15], [5, 6, 7, 8], 'NEG')]
    elif rec_num == 625:
        # đường Linh Đông -> Ngập nặng (NEG), Tô Ngọc Vân -> Ngập nặng (NEG)
        c_trips = [
            ([8, 9, 10], [0, 1], 'NEG'),
            ([14, 15, 16], [0, 1], 'NEG')
        ]
    elif rec_num == 626:
        # Thủ Đức -> chống ngập (POS), Thủ Đức -> ngập lụt (NEG)
        c_trips = [
            ([7, 8], [4, 5], 'POS'),
            ([24, 25], [21, 22], 'NEG')
        ]
    elif rec_num == 627:
        # Đồ án tốt nghiệp sinh viên -> REJECT
        c_trips = []
    elif rec_num == 628:
        # chợ Thủ Đức, Thảo Điền, Lê Văn Việt, Nguyễn Duy Trinh -> giải quyết điểm ngập (POS)
        c_trips = [
            ([12, 13, 14], [6, 7, 8, 9], 'POS'),
            ([16, 17], [6, 7, 8, 9], 'POS'),
            ([19, 20, 21], [6, 7, 8, 9], 'POS'),
            ([23, 24, 25], [6, 7, 8, 9], 'POS')
        ]
    elif rec_num == 629:
        # Tỉnh lộ 43 -> ngập nặng (NEG)
        c_trips = [([9, 10, 11], [20, 21], 'NEG')]
    elif rec_num == 630:
        # Cắt tiền tố thừa "Tại TP. Hồ Chí Minh , " vì câu đã có Bình Thạnh
        # "🌊 Triều cường lên đỉnh , nhiều tuyến đường Bình Thạnh biến thành “ biển nước ”..."
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):].strip()
        # Bình Thạnh [9, 10] -> biển nước [14, 15] (NEG)
        c_trips = [([9, 10], [14, 15], 'NEG')]

    # --- R631 to R640 ---
    elif rec_num == 631:
        # Đường Đặng Thùy Trâm -> triều cường ngập cao (NEG)
        c_trips = [([6, 7, 8, 9], [21, 22, 23, 24], 'NEG')]
    elif rec_num == 632:
        # Thanh Đa -> ngập hơn 1 mét (NEG)
        c_trips = [([9, 10], [13, 14, 15, 16], 'NEG')]
    elif rec_num == 633:
        # Nguyễn Văn Khối, Phạm Văn Chiêu, Lê Đức Thọ, Lê Văn Thọ -> chìm trong nước (NEG)
        c_trips = [
            ([3, 4, 5], [38, 39, 40], 'NEG'),
            ([7, 8, 9], [38, 39, 40], 'NEG'),
            ([11, 12, 13], [38, 39, 40], 'NEG'),
            ([15, 16, 17], [38, 39, 40], 'NEG')
        ]
    elif rec_num == 634:
        # Kêu gọi cập nhật tình hình -> REJECT
        c_trips = []
    elif rec_num == 635:
        # Cắt tiền tố thừa "Tại TP. Hồ Chí Minh , " vì câu đã có Gò Vấp
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):].strip()
        # Gò Vấp [11, 12] -> ngập khủng [8, 9] (NEG)
        c_trips = [([11, 12], [8, 9], 'NEG')]
    elif rec_num == 636:
        # Đường Phạm Văn Chiêu, Lê Đức Thọ, Lê Văn Thọ -> nước ngập hơn nửa bánh xe (NEG)
        c_trips = [
            ([0, 1, 2, 3], [24, 25, 26, 27, 28, 29], 'NEG'),
            ([5, 6, 7], [24, 25, 26, 27, 28, 29], 'NEG'),
            ([9, 10, 11], [24, 25, 26, 27, 28, 29], 'NEG')
        ]
    elif rec_num == 637:
        # quận Gò Vấp, quận 12 -> ngập nửa bánh xe (NEG)
        c_trips = [
            ([12, 13, 14], [21, 22, 23, 24], 'NEG'),
            ([16, 17], [21, 22, 23, 24], 'NEG')
        ]
    elif rec_num == 638:
        # đường Mã Lò -> đã ngập sâu (NEG)
        c_trips = [([1, 2, 3], [4, 5, 6], 'NEG')]
    elif rec_num == 639:
        # Phát ngôn chung của Sở Xây dựng TPHCM không có điểm ngập cụ thể -> REJECT
        c_trips = []
    elif rec_num == 640:
        # TP. HCM -> đường hóa sông (NEG)
        c_trips = [([0, 1], [9, 10, 11], 'NEG')]

    # --- R641 to R650 ---
    elif rec_num == 641:
        # TPHCM -> XE MÁY NỔI LỀNH BỀNH (NEG)
        c_trips = [([17], [0, 1, 2, 3, 4], 'NEG')]
    elif rec_num == 642:
        # TPHCM -> ngập sâu cả ngày lẫn đêm (NEG)
        c_trips = [([14], [23, 24, 25, 26, 27, 28], 'NEG')]
    elif rec_num == 643:
        # đường Lê Văn Lương - Tố Hữu (Hà Nội - tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 644:
        # ĐƯỜNG LÊ VĂN LƯƠNG -> NGẬP SÂU (NEG)
        c_trips = [([11, 12, 13, 14], [15, 16], 'NEG')]
    elif rec_num == 645:
        # Người đi đường hỏi thăm đường tránh ngập -> REJECT
        c_trips = []
    elif rec_num == 646:
        # Chuẩn hóa bỏ ngoặc kép "“ sông ”" -> "sông" để Opinion liền mạch "biến thành sông"
        c_text = c_text.replace('“ sông ”', 'sông')
        # Đường Lê Văn Việt [0, 1, 2, 3] -> biến thành sông [15, 16, 17] (NEG)
        c_trips = [([0, 1, 2, 3], [15, 16, 17], 'NEG')]
    elif rec_num == 647:
        # Hỏi thăm đường tránh ngập -> REJECT
        c_trips = []
    elif rec_num == 648:
        # Hỏi thăm đường tránh ngập -> REJECT
        c_trips = []
    elif rec_num == 649:
        # sông Sài Gòn -> vượt mốc lịch sử (NEU), đường Phạm Hữu Lầu -> tạo sóng quật ngã xe máy (NEG)
        c_trips = [
            ([26, 27, 28], [29, 30, 31, 32], 'NEU'),
            ([42, 43, 44, 45], [54, 55, 56, 57], 'NEG')
        ]
    elif rec_num == 650:
        # Cẩm nang danh sách 66 điểm ngập mùa mưa -> REJECT
        c_trips = []

    # --- R651 to R660 ---
    elif rec_num == 651:
        # TP. HCM -> Nước ngập gần lút bánh xe , tràn cả vào nhà (NEG)
        c_trips = [([2, 3], [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30], 'NEG')]
    elif rec_num == 652:
        # TP. HCM -> chật vật di chuyển qua đường ngập (NEG)
        c_trips = [([36, 37], [2, 3, 4, 5, 6, 7, 8], 'NEG')]
    elif rec_num == 653:
        # TP. HCM -> rơi vào tình trạng ngập (NEG)
        c_trips = [([11, 12], [13, 14, 15, 16, 17], 'NEG')]
    elif rec_num == 654:
        # TP. HCM -> ngập nặng (NEG)
        c_trips = [([4, 5], [7, 8], 'NEG')]
    elif rec_num == 655:
        # hầm chui HC1, Nguyễn Văn Linh, Nguyễn Hữu Thọ -> ngập sâu (NEG)
        c_trips = [
            ([20, 21, 22], [43, 44], 'NEG'),
            ([26, 27, 28], [43, 44], 'NEG'),
            ([30, 31, 32], [43, 44], 'NEG')
        ]
    elif rec_num == 656:
        # HẦM CHUI NGUYỄN VĂN LINH -> NGẬP NẶNG (NEG)
        c_trips = [([2, 3, 4, 5, 6], [7, 8], 'NEG')]
    elif rec_num == 657:
        # TP. HCM -> ngập như sông (NEG)
        c_trips = [([32, 33], [3, 4, 5], 'NEG')]
    elif rec_num == 658:
        # đường Nguyễn Văn Khối -> cải tạo hệ thống thoát nước (POS), Lê Văn Thọ -> cải tạo hệ thống thoát nước (POS)
        c_trips = [
            ([42, 43, 44, 45], [36, 37, 38, 39, 40, 41], 'POS'),
            ([47, 48, 49], [36, 37, 38, 39, 40, 41], 'POS')
        ]
    elif rec_num == 659:
        # Thảo Điền -> Nước ngập hơn nửa mét (NEG)
        c_trips = [([11, 12], [0, 1, 2, 3, 4], 'NEG')]
    elif rec_num == 660:
        # Thảo Điền -> ngập lụt (NEG)
        c_trips = [([8, 9], [28, 29], 'NEG')]

    # --- R661 to R670 ---
    elif rec_num == 661:
        # CHỢ THỦ ĐỨC -> THẤT THỦ (NEG)
        c_trips = [([0, 1, 2], [4, 5], 'NEG')]
    elif rec_num == 662:
        # Đường Linh Đông, Tô Ngọc Vân -> nước ngập như sông (NEG)
        c_trips = [
            ([0, 1, 2], [11, 12, 13, 14], 'NEG'),
            ([4, 5, 6], [11, 12, 13, 14], 'NEG')
        ]
    elif rec_num == 663:
        # Đường 11 -> ngập sâu (NEG)
        c_trips = [([5, 6], [15, 16], 'NEG')]
    elif rec_num == 664:
        # Đường Đặng Thị Rành, Đường Phạm Văn Đồng, Đường Tô Ngọc Vân -> ngập nước (NEG)
        c_trips = [
            ([23, 24, 25, 26], [5, 6], 'NEG'),
            ([33, 34, 35, 36], [5, 6], 'NEG'),
            ([47, 48, 49, 50], [5, 6], 'NEG')
        ]
    elif rec_num == 665:
        # CHỢ THỦ ĐỨC -> NGẬP LÊNH LÁNG (NEG)
        c_trips = [([6, 7, 8], [12, 13, 14], 'NEG')]
    elif rec_num == 666:
        # Thạnh Xuân 21, Tô Ngọc Vân -> Ngập nước sâu (NEG), chợ Thạnh Xuân -> ngập sâu (NEG)
        c_trips = [
            ([5, 6, 7], [0, 1, 2], 'NEG'),
            ([10, 11, 12], [0, 1, 2], 'NEG'),
            ([20, 21, 22], [27, 28], 'NEG')
        ]
    elif rec_num == 667:
        # đường Linh Đông, Tô Ngọc Vân -> Ngập nặng (NEG)
        c_trips = [
            ([16, 17, 18], [8, 9], 'NEG'),
            ([22, 23, 24], [8, 9], 'NEG')
        ]
    elif rec_num == 668:
        # cầu Ba Thôn 2 -> Vỡ đê bao (NEG)
        c_trips = [([8, 9, 10, 11], [4, 5, 6], 'NEG')]
    elif rec_num == 669:
        # đường Tô Ngọc Vân, đường Linh Đông, đường An Bình -> nước ngập lênh láng (NEG)
        c_trips = [
            ([30, 31, 32, 33], [56, 57, 58, 59], 'NEG'),
            ([35, 36, 37], [56, 57, 58, 59], 'NEG'),
            ([47, 48, 49], [56, 57, 58, 59], 'NEG')
        ]
    elif rec_num == 670:
        # chợ Thủ Đức -> chống ngập (POS)
        c_trips = [([13, 14, 15], [10, 11], 'POS')]

    # --- R671 to R680 ---
    elif rec_num == 671:
        # Chợ Thủ Đức -> chống ngập (POS)
        c_trips = [([0, 1, 2], [13, 14], 'POS')]
    elif rec_num == 672:
        # Đường Nguyễn Văn Khối -> hay ngập (NEG)
        c_trips = [([0, 1, 2, 3], [33, 34], 'NEG')]
    elif rec_num == 673:
        # Gò Vấp -> ngập lênh láng (NEG)
        c_trips = [([6, 7], [9, 10, 11], 'NEG')]
    elif rec_num == 674:
        # Phan Văn Trị -> ngập (NEG)
        c_trips = [([19, 20, 21], [22], 'NEG')]
    elif rec_num == 675:
        # Lê Văn Thọ -> đang ngập (NEG)
        c_trips = [([13, 14, 15], [16, 17], 'NEG')]
    elif rec_num == 676:
        # Rao bán chậu cây Vườn Sài Gòn -> REJECT
        c_trips = []
    elif rec_num == 677:
        # Lê Đức Thọ -> ngập nguyên bánh xe (NEG), Lê Văn Thọ -> ngập nửa bánh xe (NEG)
        c_trips = [
            ([3, 4, 5], [6, 7, 8, 9], 'NEG'),
            ([11, 12, 13], [14, 15, 16, 17], 'NEG')
        ]
    elif rec_num == 678:
        # Đường Lê Đức Thọ -> xe chết máy (NEG)
        c_trips = [([0, 1, 2, 3], [4, 5, 6], 'NEG')]
    elif rec_num == 679:
        # Gò Vấp -> ngập lụt nhiều nơi (NEG)
        c_trips = [([23, 24], [31, 32, 33, 34], 'NEG')]
    elif rec_num == 680:
        # Đường Phạm Văn Chiêu, Lê Đức Thọ, Lê Văn Thọ -> nước ngập hơn nửa bánh xe (NEG)
        c_trips = [
            ([0, 1, 2, 3], [24, 25, 26, 27, 28, 29], 'NEG'),
            ([5, 6, 7], [24, 25, 26, 27, 28, 29], 'NEG'),
            ([9, 10, 11], [24, 25, 26, 27, 28, 29], 'NEG')
        ]

    # --- R681 to R690 ---
    elif rec_num == 681:
        # Đường Phạm Văn Chiêu, Lê Đức Thọ, Lê Văn Thọ -> nước ngập hơn nửa bánh xe (NEG)
        c_trips = [
            ([2, 3, 4, 5], [26, 27, 28, 29, 30, 31], 'NEG'),
            ([7, 8, 9], [26, 27, 28, 29, 30, 31], 'NEG'),
            ([11, 12, 13], [26, 27, 28, 29, 30, 31], 'NEG')
        ]
    elif rec_num == 682:
        # Phan Văn Hớn, Phan Huy Ích, Phạm Văn Chiêu, Lê Đức Thọ, đường Song Hành -> MÊNH MÔNG NƯỚC (NEG)
        c_trips = [
            ([25, 26, 27], [3, 4, 5], 'NEG'),
            ([33, 34, 35], [3, 4, 5], 'NEG'),
            ([37, 38, 39], [3, 4, 5], 'NEG'),
            ([41, 42, 43], [3, 4, 5], 'NEG'),
            ([50, 51, 52], [3, 4, 5], 'NEG')
        ]
    elif rec_num == 683:
        # Tản văn hài hước phân biệt tên đường -> REJECT
        c_trips = []
    elif rec_num == 684:
        # TPHCM -> MÊNH MÔNG NƯỚC (NEG)
        c_trips = [([2], [3, 4, 5], 'NEG')]
    elif rec_num == 685:
        # chợ An Nhơn -> ngập dữ lắm (NEG)
        c_trips = [([1, 2, 3], [4, 5, 6], 'NEG')]
    elif rec_num == 686:
        # RẠCH XÓM CỦI -> GIẢI QUYẾT NGẬP (POS)
        c_trips = [([7, 8, 9], [11, 12, 13], 'POS')]
    elif rec_num == 687:
        # Phạm Thế Hiển, Cầu Bà Tàng -> nước ngập (NEG)
        c_trips = [
            ([7, 8, 9], [4, 5], 'NEG'),
            ([11, 12, 13], [4, 5], 'NEG')
        ]
    elif rec_num == 688:
        # đường Chu Văn An -> chống ngập (POS)
        c_trips = [([12, 13, 14, 15], [6, 7], 'POS')]
    elif rec_num == 689:
        # TP. HCM -> CHỐNG NGẬP (POS)
        c_trips = [([0, 1], [12, 13], 'POS')]
    elif rec_num == 690:
        # TP. HCM -> ngập nghiêm trọng (NEG)
        c_trips = [([10, 11], [26, 27, 28], 'NEG')]

    # --- R691 to R700 ---
    elif rec_num == 691:
        # TPHCM -> đề phòng ngập úng (NEU) - token 7 là dấu phẩy nên lấy 8..11
        c_trips = [([0], [8, 9, 10, 11], 'NEU')]
    elif rec_num == 692:
        # Kiệt 59 An Dương Vương (Huế - tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 693:
        # cầu Nhật Tân, Nguyễn Hoàng Tôn (Hà Nội - tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 694:
        # QUẬN 12 -> NGẬP QUANH NĂM (NEG)
        c_trips = [([1, 2], [5, 6, 7], 'NEG')]
    elif rec_num == 695:
        # phường Tam Bình -> ngập sâu (NEG)
        c_trips = [([11, 12, 13], [25, 26], 'NEG')]
    elif rec_num == 696:
        # TP HCM -> NGẬP NƯỚC (NEG)
        c_trips = [([6, 7], [11, 12], 'NEG')]
    elif rec_num == 697:
        # TP. HCM -> đạt đỉnh lịch sử (NEU)
        c_trips = [([4, 5], [6, 7, 8, 9], 'NEU')]
    elif rec_num == 698:
        # TP Hồ Chí Minh -> ngập lụt (NEG)
        c_trips = [([0, 1, 2, 3], [8, 9], 'NEG')]
    elif rec_num == 699:
        # sông Sài Gòn -> cảnh báo ngập (NEU)
        c_trips = [([12, 13, 14], [6, 7, 8], 'NEU')]
    elif rec_num == 700:
        # Thanh Đa, Bình Quới -> Bị ngập sâu (NEG)
        c_trips = [
            ([1, 2], [13, 14, 15], 'NEG'),
            ([4, 5], [13, 14, 15], 'NEG')
        ]

    curated_lines.append(f"{c_text}####{c_trips}")

assert len(curated_lines) == 100, f"Expected 100 lines, got {len(curated_lines)}"

# Read existing lines from phase3.txt
out_path = 'data/validate_label/thuan/phase3.txt'
with open(out_path, 'r', encoding='utf-8') as f:
    existing_lines = [l.strip() for l in f if l.strip()]

# Keep the first 600 lines (Batch 1 to 6)
batch1_to_6_lines = existing_lines[:600]
final_lines = batch1_to_6_lines + curated_lines

with open(out_path, 'w', encoding='utf-8') as out_f:
    for l in final_lines:
        out_f.write(l + '\n')

print(f"Successfully wrote 600 previous lines + 100 Batch 7 lines. Total lines in {out_path}: {len(final_lines)}")
