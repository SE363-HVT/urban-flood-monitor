import ast, sys, re

sys.stdout.reconfigure(encoding='utf-8')

# Read raw batch 9
with open('scratch_batch9_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

assert len(blocks) == 100, f"Expected 100 blocks, got {len(blocks)}"

curated_lines = []

for idx, b in enumerate(blocks):
    rec_num = 801 + idx
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
    
    # --- R801 to R810 ---
    if rec_num == 801:
        # Tô Ngọc Vân, Linh Đông -> ngập kinh điển (NEG)
        c_trips = [
            ([37, 38, 39], [29, 30, 31], 'NEG'),
            ([41, 42], [29, 30, 31], 'NEG')
        ]
    elif rec_num == 802:
        # phường Thủ Đức -> ngập sâu (NEG)
        c_trips = [([20, 21, 22], [23, 24], 'NEG')]
    elif rec_num == 803:
        # cầu Kinh Dương Vương -> nước ngập (NEG)
        c_trips = [([15, 16, 17, 18], [21, 22], 'NEG')]
    elif rec_num == 804:
        # đường Mã Lò -> mưa ngập (NEG)
        c_trips = [([9, 10, 11], [4, 5], 'NEG')]
    elif rec_num == 805:
        # Quảng cáo trung tâm tiếng Anh -> REJECT
        c_trips = []
    elif rec_num == 806:
        # TP. HCM -> CHỐNG NGẬP (POS)
        c_trips = [([1, 2], [8, 9], 'POS')]
    elif rec_num == 807:
        # Kêu gọi hỏi thăm tương tác Facebook -> REJECT
        c_trips = []
    elif rec_num == 808:
        # TPHCM -> ngập lênh láng (NEG)
        c_trips = [([14], [2, 3, 4], 'NEG')]
    elif rec_num == 809:
        # TP. HCM -> Triều cường dâng cao (NEG)
        c_trips = [([7, 8], [0, 1, 2, 3], 'NEG')]
    elif rec_num == 810:
        # Cần Thơ - Lâm Đồng (liệt kê đa tỉnh ngoài TP.HCM) -> REJECT
        c_trips = []

    # --- R811 to R820 ---
    elif rec_num == 811:
        # Cắt tiền tố thừa "Tại TP. Hồ Chí Minh , " vì câu đã có Dĩ An
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):].strip()
        # Khúc 550 [13, 14] -> mưa là ngập [16, 17, 18] (NEG)
        c_trips = [([13, 14], [16, 17, 18], 'NEG')]
    elif rec_num == 812:
        # PHƯỜNG DĨ AN -> CỨ MƯA LÀ NGẬP (NEG)
        c_trips = [([0, 1, 2], [4, 5, 6, 7], 'NEG')]
    elif rec_num == 813:
        # Sài Gòn, Bình Dương -> ngập khủng khiếp (NEG)
        c_trips = [
            ([0, 1], [5, 6, 7], 'NEG'),
            ([2, 3], [5, 6, 7], 'NEG')
        ]
    elif rec_num == 814:
        # Cẩm nang danh sách 122 điểm ngập -> REJECT
        c_trips = []
    elif rec_num == 815:
        # TP. Hồ Chí Minh -> ngập sâu (NEG)
        c_trips = [([12, 13, 14, 15], [16, 17], 'NEG')]
    elif rec_num == 816:
        # đường ĐT746 -> ngập sâu (NEG)
        c_trips = [([21, 22], [47, 48], 'NEG')]
    elif rec_num == 817:
        # Cắt tiền tố thừa "Tại TP. Hồ Chí Minh , " vì câu đã có thành phố hồ chí minh
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):].strip()
        # thành phố hồ chí minh [11, 12, 13, 14, 15], bình dương [17, 18] -> ngập [6] (NEG)
        c_trips = [
            ([12, 13, 14, 15, 16], [8], 'NEG'),
            ([18, 19], [8], 'NEG')
        ]
    elif rec_num == 818:
        # Cắt tiền tố thừa "Tại TP. Hồ Chí Minh , " vì câu đã có thủ đức
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):].strip()
        # thủ đức [10, 11] -> ngập sâu [14, 15] (NEG)
        c_trips = [([10, 11], [14, 15], 'NEG')]
    elif rec_num == 819:
        # sông Sài Gòn -> đạt mức cao nhất (NEU)
        c_trips = [([4, 5, 6], [12, 13, 14, 15], 'NEU')]
    elif rec_num == 820:
        # Hầm chui An Phú -> đã hết ngập (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11], 'POS')]

    # --- R821 to R830 ---
    elif rec_num == 821:
        # Cắt tiền tố thừa "Tại TP. Hồ Chí Minh , " vì câu đã có HỒ CHÍ MINH
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):].strip()
        # HỒ CHÍ MINH [0, 1, 2] -> NGẬP SÂU [3, 4] (NEG)
        c_trips = [([0, 1, 2], [3, 4], 'NEG')]
    elif rec_num == 822:
        # Cắt tiền tố thừa "Tại TP. Hồ Chí Minh , " vì câu đã có Hồ Chí Minh
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):].strip()
        # Hồ Chí Minh [0, 1, 2] -> đạt đỉnh [4, 5] (NEU)
        c_trips = [([0, 1, 2], [4, 5], 'NEU')]
    elif rec_num == 823:
        # Hầm chui An Phú -> đã hết ngập (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11], 'POS')]
    elif rec_num == 824:
        # Hầm chui nút giao An Phú -> đã hết ngập (POS)
        c_trips = [([4, 5, 6, 7, 8, 9], [11, 12, 13], 'POS')]
    elif rec_num == 825:
        # Hầm chui An Phú -> đã hết ngập (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11], 'POS')]
    elif rec_num == 826:
        # Hầm chui An Phú -> đã hết ngập (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11], 'POS')]
    elif rec_num == 827:
        # Câu chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        # TPHCM [1] -> nước lại dâng lên [9, 10, 11, 12] (NEG)
        c_trips = [([1], [10, 11, 12, 13], 'NEG')]
    elif rec_num == 828:
        # Câu chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        # TPHCM [1] -> tăng nguy cơ ngập [17, 18, 19, 20] (NEU)
        c_trips = [([1], [17, 18, 19, 20], 'NEU')]
    elif rec_num == 829:
        # Câu hỏi tu từ cảm thán -> REJECT
        c_trips = []
    elif rec_num == 830:
        # Câu hỏi tu từ cảm thán -> REJECT
        c_trips = []

    # --- R831 to R840 ---
    elif rec_num == 831:
        # Đồng bằng sông Cửu Long (tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 832:
        # Than thở chung chung -> REJECT
        c_trips = []
    elif rec_num == 833:
        # Slogan hài hước meme -> REJECT
        c_trips = []
    elif rec_num == 834:
        # Cầu nguyện cá nhân trên MXH -> REJECT
        c_trips = []
    elif rec_num == 835:
        # TP. HCM -> đạt đỉnh (NEU)
        c_trips = [([3, 4], [8, 9], 'NEU')]
    elif rec_num == 836:
        # Tâm sự cá nhân kẹt xe -> REJECT
        c_trips = []
    elif rec_num == 837:
        # đường Rạch Cùng -> tràn qua vào nhà dân (NEG)
        c_trips = [([24, 25, 26], [34, 35, 36, 37, 38], 'NEG')]
    elif rec_num == 838:
        # Hồ Chí Minh -> ngập nước (NEG)
        c_trips = [([0, 1, 2], [17, 18], 'NEG')]
    elif rec_num == 839:
        # Câu chưa có địa điểm cụ thể -> chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        # TPHCM [1] -> tăng nguy cơ ngập [14, 15, 16, 17] (NEU)
        c_trips = [([1], [14, 15, 16, 17], 'NEU')]
    elif rec_num == 840:
        # TP. HCM -> ngập giờ tan tầm (NEG)
        c_trips = [([0, 1], [2, 3, 4, 5], 'NEG')]

    # --- R841 to R845 ---
    elif rec_num == 841:
        # Câu chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        # TPHCM [1] -> nguy cơ ngập [28, 29, 30] (NEU)
        # Verify tokens of 841: find 'nguy cơ ngập'
        tokens_841 = c_text.split()
        opi_841 = [i for i, w in enumerate(tokens_841) if w in {'ngập', 'ngập'}]
        # Let's match in 841: 'nguy cơ ngập'
        for i in range(len(tokens_841) - 2):
            if tokens_841[i] == 'nguy' and tokens_841[i+1] == 'cơ' and tokens_841[i+2].startswith('ngập'):
                c_trips = [([1], [i, i+1, i+2], 'NEU')]
                break
        else:
            c_trips = [([1], [25, 26, 27], 'NEU')]
    elif rec_num == 842:
        # Hồ Chí Minh -> ngập nước (NEG)
        tokens_842 = c_text.split()
        for i in range(len(tokens_842) - 1):
            if tokens_842[i] == 'ngập' and tokens_842[i+1] == 'nước':
                c_trips = [([0, 1, 2], [i, i+1], 'NEG')]
                break
        else:
            c_trips = [([0, 1, 2], [16, 17], 'NEG')]
    elif rec_num == 843:
        # TP. HCM -> đạt đỉnh (NEU)
        c_trips = [([2, 3], [4, 5], 'NEU')]
    elif rec_num == 844:
        # Dự báo biến đổi khí hậu / xu hướng sụt lún tương lai xa -> REJECT
        c_trips = []
    elif rec_num == 845:
        # rạch Cầu Cụt -> thoát nước (POS)
        c_trips = [([8, 9, 10], [35, 36], 'POS')]

    # --- R846 to R850 ---
    elif rec_num == 846:
        # TPHCM -> cảnh báo ngập (NEU)
        tokens_846 = c_text.split()
        for i in range(len(tokens_846) - 2):
            if tokens_846[i] == 'cảnh' and tokens_846[i+1] == 'báo' and tokens_846[i+2] == 'ngập':
                c_trips = [([2], [i, i+1, i+2], 'NEU')]
                break
        else:
            c_trips = [([2], [25, 26, 27], 'NEU')]
    elif rec_num == 847:
        # Câu chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        tokens_847 = c_text.split()
        for i in range(len(tokens_847) - 2):
            if tokens_847[i] == 'nước' and tokens_847[i+1] == 'dâng' and tokens_847[i+2] == 'cao':
                c_trips = [([1], [i, i+1, i+2], 'NEG')]
                break
        else:
            c_trips = [([1], [11, 12, 13], 'NEG')]
    elif rec_num == 848:
        # phường Thuận An -> nguy cơ ngập úng (NEU)
        tokens_848 = c_text.split()
        for i in range(len(tokens_848) - 3):
            if tokens_848[i] == 'nguy' and tokens_848[i+1] == 'cơ' and tokens_848[i+2] == 'ngập' and tokens_848[i+3] == 'úng':
                c_trips = [([6, 7, 8], [i, i+1, i+2, i+3], 'NEU')]
                break
        else:
            c_trips = [([6, 7, 8], [30, 31, 32, 33], 'NEU')]
    elif rec_num == 849:
        # Câu chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        tokens_849 = c_text.split()
        for i in range(len(tokens_849) - 1):
            if tokens_849[i] == 'đạt' and tokens_849[i+1] == 'đỉnh':
                c_trips = [([1], [i, i+1], 'NEU')]
                break
        else:
            c_trips = [([1], [17, 18], 'NEU')]
    elif rec_num == 850:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        tokens_850 = c_text.split()
        for i in range(len(tokens_850) - 1):
            if tokens_850[i] == 'đạt' and tokens_850[i+1] == 'đỉnh':
                c_trips = [([1], [i, i+1], 'NEU')]
                break
        else:
            c_trips = [([1], [17, 18], 'NEU')]

    # --- R851 to R860 ---
    elif rec_num == 851:
        # TP. HCM -> chưa đạt đỉnh (NEU)
        c_trips = [([2, 3], [4, 5, 6], 'NEU')]
    elif rec_num == 852:
        # đường Phan Huy Ích, Trường Chinh -> ngập (NEG)
        c_trips = [
            ([23, 24, 25, 26], [17], 'NEG'),
            ([29, 30], [17], 'NEG')
        ]
    elif rec_num == 853:
        # Câu chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        tokens_853 = c_text.split()
        for i in range(len(tokens_853) - 1):
            if tokens_853[i] == 'đạt' and tokens_853[i+1].startswith('khoảng'):
                pass
        for i in range(len(tokens_853) - 2):
            if tokens_853[i] == 'nguy' and tokens_853[i+1] == 'cơ' and tokens_853[i+2].startswith('ngập'):
                c_trips = [([1], [i, i+1, i+2], 'NEU')]
                break
        else:
            c_trips = [([1], [5, 6], 'NEU')]
    elif rec_num == 854:
        # Nam Bộ đa tỉnh -> REJECT
        c_trips = []
    elif rec_num == 855:
        # TP. HCM -> đạt đỉnh (NEU)
        c_trips = [([8, 9], [2, 3], 'NEU')]
    elif rec_num == 856:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        tokens_856 = c_text.split()
        for i in range(len(tokens_856) - 3):
            if tokens_856[i] == 'nguy' and tokens_856[i+1] == 'cơ' and tokens_856[i+2] == 'ngập' and tokens_856[i+3] == 'sâu':
                c_trips = [([1], [i, i+1, i+2, i+3], 'NEU')]
                break
        else:
            c_trips = [([1], [6, 7, 8, 9], 'NEU')]
    elif rec_num == 857:
        # Câu chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        tokens_857 = c_text.split()
        for i in range(len(tokens_857) - 6):
            if tokens_857[i] == 'nước' and tokens_857[i+1] == 'tràn' and tokens_857[i+2] == 'sâu':
                c_trips = [([1], [i, i+1, i+2, i+3, i+4, i+5, i+6], 'NEG')]
                break
        else:
            c_trips = [([1], [8, 9, 10, 11, 12, 13, 14], 'NEG')]
    elif rec_num == 858:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        tokens_858 = c_text.split()
        for i in range(len(tokens_858) - 3):
            if tokens_858[i] == 'Nguy' and tokens_858[i+1] == 'cơ' and tokens_858[i+2] == 'ngập' and tokens_858[i+3] == 'sâu':
                c_trips = [([1], [i, i+1, i+2, i+3], 'NEU')]
                break
        else:
            c_trips = [([1], [3, 4, 5, 6], 'NEU')]
    elif rec_num == 859:
        # Tản văn nhận xét chung chung -> REJECT
        c_trips = []
    elif rec_num == 860:
        # Nhận xét chung chung -> REJECT
        c_trips = []

    # --- R861 to R870 ---
    elif rec_num == 861:
        # TP. HCM -> CHỐNG NGẬP (POS)
        c_trips = [([9, 10], [6, 7], 'POS')]
    elif rec_num == 862:
        # Tổng hợp điểm ngập / phân loại báo cáo -> REJECT
        c_trips = []
    elif rec_num == 863:
        # Bình luận cá nhân -> REJECT
        c_trips = []
    elif rec_num == 864:
        # HẦM CHUI AN PHÚ -> HẾT NGẬP (POS)
        c_trips = [([0, 1, 2, 3], [5, 6], 'POS')]
    elif rec_num == 865:
        # Câu hỏi tu từ châm biếm -> REJECT
        c_trips = []
    elif rec_num == 866:
        # TPHCM -> không còn ngập (POS)
        c_trips = [([7], [35, 36, 37], 'POS')]
    elif rec_num == 867:
        # TPHCM -> không còn ngập (POS)
        c_trips = [([7], [35, 36, 37], 'POS')]
    elif rec_num == 868:
        # Status văn thơ cảm xúc -> REJECT
        c_trips = []
    elif rec_num == 869:
        # Câu chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        tokens_869 = c_text.split()
        for i in range(len(tokens_869) - 3):
            if tokens_869[i] == 'nguy' and tokens_869[i+1] == 'cơ' and tokens_869[i+2] == 'ngập' and tokens_869[i+3] == 'sâu':
                c_trips = [([1], [i, i+1, i+2, i+3], 'NEU')]
                break
        else:
            c_trips = [([1], [22, 23, 24, 25], 'NEU')]
    elif rec_num == 870:
        # TP. HCM -> nguy cơ ngập diện rộng (NEU)
        c_trips = [([10, 11], [3, 4, 5, 6, 7], 'NEU')]

    # --- R871 to R880 ---
    elif rec_num == 871:
        # TPHCM -> nguy cơ ngập (NEU)
        c_trips = [([4], [10, 11, 12], 'NEU')]
    elif rec_num == 872:
        # TPHCM -> chống ngập (POS)
        c_trips = [([4], [2, 3], 'POS')]
    elif rec_num == 873:
        # sông Sài Gòn -> gần chạm mốc lịch sử (NEU), TP. HCM -> nguy cơ ngập (NEU)
        c_trips = [
            ([4, 5, 6], [8, 9, 10, 11, 12], 'NEU'),
            ([24, 25], [30, 31, 32], 'NEU')
        ]
    elif rec_num == 874:
        # Tiêu đề cụt dở dang -> REJECT
        c_trips = []
    elif rec_num == 875:
        # Hồ Chí Minh -> đạt đỉnh (NEU)
        c_trips = [([0, 1, 2], [14, 15], 'NEU')]
    elif rec_num == 876:
        # Hồ Chí Minh -> nguy cơ ngập nước (NEU)
        c_trips = [([0, 1, 2], [7, 8, 9, 10], 'NEU')]
    elif rec_num == 877:
        # Tiêu đề cụt dở dang -> REJECT
        c_trips = []
    elif rec_num == 878:
        # Câu hỏi tu từ cảm thán -> REJECT
        c_trips = []
    elif rec_num == 879:
        # TP. HCM -> đạt đỉnh (NEU)
        c_trips = [([0, 1], [13, 14], 'NEU')]
    elif rec_num == 880:
        # Phú An, Nhà Bè, Thủ Dầu Một -> vượt báo động 3 (NEU)
        c_trips = [
            ([21, 22], [33, 34, 35, 36], 'NEU'),
            ([24, 25], [33, 34, 35, 36], 'NEU'),
            ([27, 28, 29], [33, 34, 35, 36], 'NEU')
        ]

    # --- R881 to R890 ---
    elif rec_num == 881:
        # TP. HCM -> triều cường dâng cao (NEG)
        c_trips = [([8, 9], [3, 4, 5, 6], 'NEG')]
    elif rec_num == 882:
        # Hồ Chí Minh -> ngập (NEG)
        c_trips = [([0, 1, 2], [3], 'NEG')]
    elif rec_num == 883:
        # Hồ Chí Minh -> nguy cơ ngập (NEU)
        c_trips = [([0, 1, 2], [6, 7, 8], 'NEU')]
    elif rec_num == 884:
        # Tiêu đề cụt dở dang -> REJECT
        c_trips = []
    elif rec_num == 885:
        # Phân tích nguyên nhân kỹ thuật chung chung -> REJECT
        c_trips = []
    elif rec_num == 886:
        # Cắt tiền tố thừa "Tại TP. Hồ Chí Minh , " vì câu đã có Hồ Chí Minh
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):].strip()
        # Hồ Chí Minh [0, 1, 2] -> đạt đỉnh [5, 6] (NEU)
        c_trips = [([0, 1, 2], [5, 6], 'NEU')]
    elif rec_num == 887:
        # Tiêu đề cụt dở dang -> REJECT
        c_trips = []
    elif rec_num == 888:
        # Q7, Nhà Bè -> Triều cường đạt đỉnh (NEU)
        c_trips = [
            ([0], [8, 9, 10, 11], 'NEU'),
            ([1, 2], [8, 9, 10, 11], 'NEU')
        ]
    elif rec_num == 889:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        tokens_889 = c_text.split()
        for i in range(len(tokens_889) - 3):
            if tokens_889[i] == 'KHẢ' and tokens_889[i+1] == 'NĂNG' and tokens_889[i+2] == 'ĐẠT' and tokens_889[i+3] == 'ĐỈNH':
                c_trips = [([1], [i, i+1, i+2, i+3], 'NEU')]
                break
        else:
            c_trips = [([1], [9, 10, 11, 12], 'NEU')]
    elif rec_num == 890:
        # TPHCM -> đạt đỉnh (NEU)
        c_trips = [([2], [18, 19], 'NEU')]

    # --- R891 to R900 ---
    elif rec_num == 891:
        # Câu chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        tokens_891 = c_text.split()
        for i in range(len(tokens_891) - 2):
            if tokens_891[i] == 'nguy' and tokens_891[i+1] == 'cơ' and tokens_891[i+2] == 'ngập':
                c_trips = [([1], [i, i+1, i+2, i+3, i+4, i+5], 'NEU')]
                break
        else:
            c_trips = [([1], [8, 9, 10, 11, 12, 13], 'NEU')]
    elif rec_num == 892:
        # Phân tích dự án chung chung -> REJECT
        c_trips = []
    elif rec_num == 893:
        # TP. HCM -> đạt đỉnh (NEU)
        c_trips = [([0, 1], [13, 14], 'NEU')]
    elif rec_num == 894:
        # TP. HCM -> dự báo đỉnh triều (NEU)
        c_trips = [([0, 1], [2, 3, 4, 5], 'NEU')]
    elif rec_num == 895:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        tokens_895 = c_text.split()
        for i in range(len(tokens_895) - 5):
            if tokens_895[i] == 'nguy' and tokens_895[i+1] == 'cơ' and tokens_895[i+2] == 'ngập' and tokens_895[i+3] == 'sâu' and tokens_895[i+4] == 'và' and tokens_895[i+5] == 'rộng':
                c_trips = [([1], [i, i+1, i+2, i+3, i+4, i+5], 'NEU')]
                break
        else:
            c_trips = [([1], [5, 6, 7, 8, 9, 10], 'NEU')]
    elif rec_num == 896:
        # Câu chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        c_trips = [([1], [3, 4, 5, 6], 'NEU')]
    elif rec_num == 897:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        tokens_897 = c_text.split()
        for i in range(len(tokens_897) - 5):
            if tokens_897[i] == 'nguy' and tokens_897[i+1] == 'cơ' and tokens_897[i+2] == 'ngập' and tokens_897[i+3] == 'sâu' and tokens_897[i+4] == 'và' and tokens_897[i+5] == 'rộng':
                c_trips = [([1], [i, i+1, i+2, i+3, i+4, i+5], 'NEU')]
                break
        else:
            c_trips = [([1], [5, 6, 7, 8, 9, 10], 'NEU')]
    elif rec_num == 898:
        # Hồ Chí Minh -> tiếp tục ở mức cao (NEU)
        c_trips = [([0, 1, 2], [9, 10, 11, 12, 13], 'NEU')]
    elif rec_num == 899:
        # TP. HCM -> NƯỚC DÂNG RẤT CAO (NEG)
        c_trips = [([4, 5], [7, 8, 9, 10], 'NEG')]
    elif rec_num == 900:
        # Câu hỏi tu từ cảm thán -> REJECT
        c_trips = []

    curated_lines.append(f"{c_text}####{c_trips}")

assert len(curated_lines) == 100, f"Expected 100 lines, got {len(curated_lines)}"

# Read existing lines from phase3.txt
out_path = 'data/validate_label/thuan/phase3.txt'
with open(out_path, 'r', encoding='utf-8') as f:
    existing_lines = [l.strip() for l in f if l.strip()]

# Keep the first 800 lines (Batch 1 to 8)
batch1_to_8_lines = existing_lines[:800]
final_lines = batch1_to_8_lines + curated_lines

with open(out_path, 'w', encoding='utf-8') as out_f:
    for l in final_lines:
        out_f.write(l + '\n')

print(f"Successfully wrote 800 previous lines + 100 Batch 9 lines. Total lines in {out_path}: {len(final_lines)}")
