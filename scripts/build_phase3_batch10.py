import ast, sys, re

sys.stdout.reconfigure(encoding='utf-8')

# Read raw batch 10
with open('scratch_batch10_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

assert len(blocks) == 100, f"Expected 100 blocks, got {len(blocks)}"

curated_lines = []

for idx, b in enumerate(blocks):
    rec_num = 901 + idx
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
    
    # --- R901 to R910 ---
    if rec_num == 901:
        # Lào Cai (phường Cam Đường, cầu Kim Tân, đường Châu Úy) -> REJECT
        c_trips = []
    elif rec_num == 902:
        # TPHCM -> tiếp tục mưa lớn (NEG), triều cường đạt đỉnh (NEU)
        c_trips = [
            ([13], [19, 20], 'NEG'),
            ([13], [24, 25, 26, 27], 'NEU')
        ]
    elif rec_num == 903:
        # TP. HCM -> mưa to (NEG), triều cường đạt đỉnh (NEU), Phú An/Nhà Bè -> vượt báo động 3 (NEU)
        c_trips = [
            ([0, 1], [2, 3], 'NEG'),
            ([0, 1], [11, 12, 13, 14], 'NEU'),
            ([27, 28], [22, 23, 24, 25], 'NEU'),
            ([30, 31], [22, 23, 24, 25], 'NEU')
        ]
    elif rec_num == 904:
        # Hồ Chí Minh -> nguy cơ ngập (NEU)
        c_trips = [([0, 1, 2], [9, 10, 11], 'NEU')]
    elif rec_num == 905:
        # Câu hỏi tu từ cảm thán -> REJECT
        c_trips = []
    elif rec_num == 906:
        # Bàn luận chính sách nâng đường -> REJECT
        c_trips = []
    elif rec_num == 907:
        # Chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        c_trips = [
            ([1], [3, 4, 5], 'NEG'),
            ([1], [13, 14, 15, 16], 'NEU')
        ]
    elif rec_num == 908:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        c_trips = [([1], [9, 10, 11, 12], 'NEU')]
    elif rec_num == 909:
        # TPHCM -> đạt đỉnh (NEU), gây ngập (NEG)
        c_trips = [
            ([3], [6, 7], 'NEU'),
            ([3], [18, 19], 'NEG')
        ]
    elif rec_num == 910:
        # Quảng cáo BĐS T&T City Millennia -> REJECT
        c_trips = []

    # --- R911 to R920 ---
    elif rec_num == 911:
        # Cụt dở dang cuối câu "tại TP." -> REJECT
        c_trips = []
    elif rec_num == 912:
        # TPHCM -> sắp đạt đỉnh (NEU), lại ngập nặng (NEG)
        c_trips = [
            ([10], [6, 7, 8], 'NEU'),
            ([10], [18, 19, 20], 'NEG')
        ]
    elif rec_num == 913:
        # TPHCM -> triều cường đạt đỉnh (NEU), đe dọa gây ngập (NEG)
        c_trips = [
            ([22], [8, 9, 10, 11], 'NEU'),
            ([22], [17, 18, 19, 20], 'NEG')
        ]
    elif rec_num == 914:
        # Than thở mơ hồ công trình chống ngập tại đây -> REJECT
        c_trips = []
    elif rec_num == 915:
        # Hệ thống cống tại đây quá tải -> REJECT
        c_trips = []
    elif rec_num == 916:
        # Tâm sự bán cá viên chiên -> REJECT
        c_trips = []
    elif rec_num == 917:
        # đường Trần Xuân Soạn -> Triều cường đạt đỉnh (NEU), gây ngập sâu (NEG)
        c_trips = [
            ([6, 7, 8, 9], [0, 1, 2, 3], 'NEU'),
            ([6, 7, 8, 9], [17, 18, 19], 'NEG')
        ]
    elif rec_num == 918:
        # trạm Cát Lái -> 103 , 6mm (NEU), trạm Hóc Môn -> 42 , 2m (NEU)
        c_trips = [
            ([8, 9, 10], [12, 13, 14], 'NEU'),
            ([16, 17, 18], [19, 20, 21], 'NEU')
        ]
    elif rec_num == 919:
        # sông Sài Gòn -> DỰ BÁO TRIỀU CƯỜNG (NEU), TP. HCM -> đường ngập nhiều hơn (NEG)
        c_trips = [
            ([8, 9], [1, 2, 3, 4], 'NEU'),
            ([22, 23], [38, 39, 40, 41], 'NEG')
        ]
    elif rec_num == 920:
        # sông Sài Gòn -> triều cường (NEU), vẫn duy trì ở mức cao (NEU)
        c_trips = [
            ([9, 10, 11], [6, 7], 'NEU'),
            ([30, 31, 32], [37, 38, 39, 40, 41, 42], 'NEU')
        ]

    # --- R921 to R930 ---
    elif rec_num == 921:
        # Mưa Bình Dương (tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 922:
        # TP. HCM -> Triều cường đạt đỉnh (NEU), lại ngập (NEG)
        c_trips = [
            ([13, 14], [1, 2, 3, 4], 'NEU'),
            ([13, 14], [15, 16], 'NEG')
        ]
    elif rec_num == 923:
        # Cụt dở dang "tại tuyế" -> REJECT
        c_trips = []
    elif rec_num == 924:
        # TP. HCM -> ĐẠT ĐỈNH TRIỀU CỰC ĐẠI (NEU), gây ngập (NEG)
        c_trips = [
            ([0, 1], [2, 3, 4, 5, 6], 'NEU'),
            ([21, 22], [38, 39], 'NEG')
        ]
    elif rec_num == 925:
        # Cắt tiền tố thừa "Tại TP. Hồ Chí Minh , " vì đã có BÌNH THẠNH CŨ
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):].strip()
        c_trips = [([0, 1, 2], [4, 5, 6, 7, 8, 9, 10], 'NEG')]
    elif rec_num == 926:
        # Nam Bộ đa tỉnh -> REJECT
        c_trips = []
    elif rec_num == 927:
        # SÔNG SÀI GÒN -> NGUY CƠ NGẬP (NEU)
        c_trips = [([16, 17, 18], [11, 12, 13], 'NEU')]
    elif rec_num == 928:
        # TPHCM -> nguy cơ ngập nước rất cao (NEU)
        c_trips = [([24], [30, 31, 32, 33, 34, 35], 'NEU')]
    elif rec_num == 929:
        # Sài Gòn trước 1975 -> REJECT
        c_trips = []
    elif rec_num == 930:
        # Phóng sự dự án chết chìm 10.000 tỷ -> REJECT
        c_trips = []

    # --- R931 to R940 ---
    elif rec_num == 931:
        # Đường Nguyễn Hữu Thọ -> ngập nhẹ (NEG), đường Long Hậu -> nặng (NEG)
        c_trips = [
            ([24, 25, 26, 27], [28, 29], 'NEG'),
            ([36, 37, 38], [32], 'NEG')
        ]
    elif rec_num == 932:
        # Tít châm biếm chính sách -> REJECT
        c_trips = []
    elif rec_num == 933:
        # TPHCM -> triều cường đạt đỉnh (NEU), ngập sâu (NEG), sông Sài Gòn -> vượt mốc lịch sử (NEU)
        c_trips = [
            ([13], [8, 9, 10, 11], 'NEU'),
            ([23, 24], [25, 26, 27, 28], 'NEU'),
            ([33], [34, 35], 'NEG')
        ]
    elif rec_num == 934:
        # HẦM CHUI NGUYỄN VĂN LINH -> NGẬP NẶNG (NEG), đại lộ Nguyễn Văn Linh -> ngập nặng (NEG)
        c_trips = [
            ([2, 3, 4, 5, 6], [7, 8], 'NEG'),
            ([17, 18, 19, 20, 21], [39, 40], 'NEG')
        ]
    elif rec_num == 935:
        # CHỢ THỦ ĐỨC -> THẤT THỦ (NEG)
        c_trips = [([0, 1, 2], [4, 5], 'NEG')]
    elif rec_num == 936:
        # TP HCM -> TRIỀU CƯỜNG ĐẠT ĐỈNH (NEU), TPHCM -> dâng cao (NEG)
        c_trips = [
            ([6, 7], [1, 2, 3, 4], 'NEU'),
            ([27], [30, 31], 'NEG')
        ]
    elif rec_num == 937:
        # đường Võ Văn Ngân -> hoạt động hiệu quả (POS)
        c_trips = [([41, 42, 43, 44], [54, 55, 56, 57], 'POS')]
    elif rec_num == 938:
        # rạch Xuyên Tâm -> nạo vét (POS), cải tạo (POS)
        c_trips = [
            ([16, 17, 18], [4, 5], 'POS'),
            ([16, 17, 18], [7, 8], 'POS')
        ]
    elif rec_num == 939:
        # RẠCH XUYÊN TÂM -> CẢI TẠO (POS)
        c_trips = [([7, 8, 9], [5, 6], 'POS')]
    elif rec_num == 940:
        # rạch Xuyên Tâm -> cải tạo (POS)
        c_trips = [([31, 32, 33], [29, 30], 'POS')]

    # --- R941 to R950 ---
    elif rec_num == 941:
        # quận Gò Vấp -> cải tạo hệ thống thoát nước (POS)
        c_trips = [([42, 43, 44], [34, 35, 36, 37, 38, 39], 'POS')]
    elif rec_num == 942:
        # đường Nguyễn Văn Khối -> cải tạo hệ thống thoát nước (POS), Lê Văn Thọ -> cải tạo hệ thống thoát nước (POS)
        c_trips = [
            ([10, 11, 12, 13], [4, 5, 6, 7, 8, 9], 'POS'),
            ([15, 16, 17], [4, 5, 6, 7, 8, 9], 'POS')
        ]
    elif rec_num == 943:
        # rạch Xuyên Tâm -> nạo vét (POS), cải tạo (POS)
        c_trips = [
            ([26, 27, 28], [14, 15], 'POS'),
            ([26, 27, 28], [17, 18], 'POS')
        ]
    elif rec_num == 944:
        # Rạch Dừa -> nạo vét (POS), Rạch Ông Hóa -> nạo vét (POS), phường Thảo Điền -> nạo vét (POS)
        c_trips = [
            ([12, 13], [10, 11], 'POS'),
            ([15, 16, 17], [10, 11], 'POS'),
            ([22, 23], [10, 11], 'POS')
        ]
    elif rec_num == 945:
        # sông Sài Gòn -> đã đạt đỉnh (NEU)
        c_trips = [([28, 29, 30], [31, 32, 33], 'NEU')]
    elif rec_num == 946:
        # TP. HCM -> ĐẠT ĐỈNH (NEU)
        c_trips = [([15, 16], [18, 19], 'NEU')]
    elif rec_num == 947:
        # TPHCM -> trên báo động 3 (NEU), nguy cơ ngập cao (NEU)
        c_trips = [
            ([7], [8, 9, 10, 11], 'NEU'),
            ([7], [13, 14, 15, 16], 'NEU')
        ]
    elif rec_num == 948:
        # TP. HCM -> đạt đỉnh (NEU), nguy cơ ngập (NEU)
        c_trips = [
            ([5, 6], [10, 11], 'NEU'),
            ([5, 6], [17, 18, 19], 'NEU')
        ]
    elif rec_num == 949:
        # Câu hỏi tu từ -> REJECT
        c_trips = []
    elif rec_num == 950:
        # Hội đồng nghiệm thu đề tài KHCN -> REJECT
        c_trips = []

    # --- R951 to R960 ---
    elif rec_num == 951:
        # rạch Xuyên Tâm -> nạo vét (POS), cải tạo (POS)
        c_trips = [
            ([16, 17, 18], [4, 5], 'POS'),
            ([16, 17, 18], [7, 8], 'POS')
        ]
    elif rec_num == 952:
        # THỦ ĐỨC -> THẤT THỦ (NEG)
        c_trips = [([12, 13], [14, 15], 'NEG')]
    elif rec_num == 953:
        # TP. HCM -> ĐẠT ĐỈNH (NEU)
        c_trips = [([15, 16], [18, 19], 'NEU')]
    elif rec_num == 954:
        # TP. HCM -> đạt đỉnh (NEU), nguy cơ ngập (NEU)
        c_trips = [
            ([5, 6], [10, 11], 'NEU'),
            ([5, 6], [17, 18, 19], 'NEU')
        ]
    elif rec_num == 955:
        # sông Sài Gòn -> lên cao (NEU), đạt đỉnh (NEU)
        c_trips = [
            ([20, 21], [23, 24], 'NEU'),
            ([20, 21], [26, 27], 'NEU')
        ]
    elif rec_num == 956:
        # đường Trần Xuân Soạn -> chỉ ngập nhẹ (NEU)
        c_trips = [([2, 3, 4, 5], [22, 23, 24], 'NEU')]
    elif rec_num == 957:
        # trạm Phú An -> trên báo động 3 (NEU), Nhà Bè -> trên báo động 3 (NEU)
        c_trips = [
            ([29, 30, 31], [49, 50, 51, 52], 'NEU'),
            ([33, 34], [49, 50, 51, 52], 'NEU')
        ]
    elif rec_num == 958:
        # hạ lưu sông Sài Gòn -> ở cấp độ 2 (NEU)
        c_trips = [([8, 9, 10, 11, 12], [13, 14, 15, 16], 'NEU')]
    elif rec_num == 959:
        # sông Sài Gòn -> vẫn duy trì ở mức cao (NEU)
        c_trips = [([21, 22, 23], [33, 34, 35, 36, 37, 38], 'NEU')]
    elif rec_num == 960:
        # trạm Phú An -> vượt trên báo động 3 (NEU), Nhà Bè -> vượt trên báo động 3 (NEU)
        c_trips = [
            ([10, 11, 12], [26, 27, 28, 29, 30], 'NEU'),
            ([14, 15], [26, 27, 28, 29, 30], 'NEU')
        ]

    # --- R961 to R970 ---
    elif rec_num == 961:
        # hạ lưu sông Sài Gòn -> ở cấp độ 2 (NEU)
        c_trips = [([8, 9, 10, 11, 12], [16, 17, 18], 'NEU')]
    elif rec_num == 962:
        # sông Sài Gòn -> vẫn duy trì ở mức cao (NEU), trạm Phú An -> 1 , 53m (NEU), Nhà Bè -> xấp xỉ báo động II (NEU)
        c_trips = [
            ([16, 17], [21, 22, 23, 24, 25, 26], 'NEU'),
            ([35, 36, 37], [40, 41, 42], 'NEU'),
            ([44, 45], [50, 51, 52, 53, 54], 'NEU')
        ]
    elif rec_num == 963:
        # Chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        c_trips = [
            ([1], [9, 10, 11, 12], 'NEU'),
            ([1], [19, 20], 'NEG')
        ]
    elif rec_num == 964:
        # trạm Phú An -> đạt mức + 1 , 78m (NEU)
        c_trips = [([11, 12, 13], [21, 22, 23, 24, 25, 26], 'NEU')]
    elif rec_num == 965:
        # Khuyến nghị môi trường chung chung -> REJECT
        c_trips = []
    elif rec_num == 966:
        # Chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        c_trips = [([1], [6, 7, 8, 9], 'NEU')]
    elif rec_num == 967:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        c_trips = [([1], [15, 16], 'NEU')]
    elif rec_num == 968:
        # trạm Nhà Bè -> đạt mức 1 , 8m (NEU)
        c_trips = [([4, 5, 6], [13, 14, 15, 16, 17], 'NEU')]
    elif rec_num == 969:
        # Câu hỏi tu từ cảm thán -> REJECT
        c_trips = []
    elif rec_num == 970:
        # đường Cao Thị Chính -> nước ngập lênh láng (NEG), bắt đầu rút dần (POS), phường Phú Thuận -> nước ngập lênh láng (NEG)
        c_trips = [
            ([1, 2, 3, 4], [18, 19, 20, 21], 'NEG'),
            ([1, 2, 3, 4], [35, 36, 37, 38], 'POS'),
            ([6, 7, 8], [18, 19, 20, 21], 'NEG')
        ]

    # --- R971 to R980 ---
    elif rec_num == 971:
        # sông Sài Gòn -> đạt mức cao (NEU)
        c_trips = [([25, 26, 27], [31, 32, 33], 'NEU')]
    elif rec_num == 972:
        # Chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        c_trips = [([1], [5, 6], 'NEU')]
    elif rec_num == 973:
        # trạm Phú Lâm -> 127 . 8mm (NEU), trạm An Lạc -> 102 . 8mm (NEU)
        c_trips = [
            ([5, 6, 7], [9, 10, 11], 'NEU'),
            ([13, 14, 15], [17, 18, 19], 'NEU')
        ]
    elif rec_num == 974:
        # trạm Cát Lái -> lượng mưa 110 m (NEU)
        c_trips = [([9, 10, 11], [2, 3, 4, 5], 'NEU')]
    elif rec_num == 975:
        # Chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        c_trips = [([1], [13, 14], 'POS')]
    elif rec_num == 976:
        # TP Thủ Đức, Bình Thạnh, Gò Vấp -> gần 70 mm (NEU); quận 1 -> 50 mm (NEU)
        c_trips = [
            ([5, 6, 7], [17, 18, 19], 'NEU'),
            ([12, 13], [17, 18, 19], 'NEU'),
            ([15, 16], [17, 18, 19], 'NEU'),
            ([22, 23], [25, 26], 'NEU')
        ]
    elif rec_num == 977:
        # Võ Văn Ngân -> vẫn còn ngập (NEG)
        c_trips = [([11, 12, 13], [24, 25, 26], 'NEG')]
    elif rec_num == 978:
        # Chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        c_trips = [
            ([1], [21, 22, 23, 24], 'POS'),
            ([1], [29, 30, 31, 32], 'POS')
        ]
    elif rec_num == 979:
        # Câu hỏi tu từ giật tít -> REJECT
        c_trips = []
    elif rec_num == 980:
        # TP. HCM -> Giải quyết ngập do triều (POS)
        c_trips = [([16, 17], [8, 9, 10, 11, 12], 'POS')]

    # --- R981 to R990 ---
    elif rec_num == 981:
        # Đường Kha Vạn Cân -> ngập nhẹ (NEG), Hiệp Bình Chánh -> ngập nhẹ (NEG)
        c_trips = [
            ([0, 1, 2, 3], [18, 19], 'NEG'),
            ([5, 6, 7], [18, 19], 'NEG')
        ]
    elif rec_num == 982:
        # Quốc lộ 13 -> ngập nhẹ (NEG), Hiệp Bình Phước -> ngập nhẹ (NEG)
        c_trips = [
            ([0, 1, 2], [23, 24], 'NEG'),
            ([10, 11, 12], [23, 24], 'NEG')
        ]
    elif rec_num == 983:
        # trạm Dương Văn Cam -> 122 , 8 mm (NEU)
        c_trips = [([33, 34, 35, 36], [27, 28, 29, 30], 'NEU')]
    elif rec_num == 984:
        # đường Dương Văn Cam -> 122 , 6mm (NEU), chợ Thủ Đức -> 122 , 6mm (NEU)
        c_trips = [
            ([11, 12, 13, 14], [25, 26, 27], 'NEU'),
            ([18, 19, 20], [25, 26, 27], 'NEU')
        ]
    elif rec_num == 985:
        # Giải thích kỹ thuật không địa điểm -> REJECT
        c_trips = []
    elif rec_num == 986:
        # Không có địa điểm cụ thể -> REJECT
        c_trips = []
    elif rec_num == 987:
        # TPHCM -> khoảng 10 - 30mm (NEU)
        c_trips = [([19], [34, 35, 36, 37], 'NEU')]
    elif rec_num == 988:
        # Tâm sự phỏng vấn không địa chỉ cụ thể -> REJECT
        c_trips = []
    elif rec_num == 989:
        # Giải thích kỹ thuật cống bung nắp -> REJECT
        c_trips = []
    elif rec_num == 990:
        # đường Dương Văn Cam -> 126 mm (NEU)
        c_trips = [([6, 7, 8, 9], [15, 16], 'NEU')]

    # --- R991 to R1000 ---
    elif rec_num == 991:
        # Bàn vu vơ về làm cống -> REJECT
        c_trips = []
    elif rec_num == 992:
        # TP Thủ Đức -> khởi công xây dựng đường số 38 (POS), đường số 38 -> khởi công xây dựng (POS)
        c_trips = [
            ([6, 7, 8], [10, 11, 12, 13], 'POS'),
            ([14, 15, 16], [10, 11, 12, 13], 'POS')
        ]
    elif rec_num == 993:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        c_trips = [([1], [35, 36, 37], 'POS')]
    elif rec_num == 994:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        c_trips = [([1], [26, 27, 28], 'POS')]
    elif rec_num == 995:
        # Đoạn này... cống đầy rác, không địa điểm cụ thể -> REJECT
        c_trips = []
    elif rec_num == 996:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        c_trips = [([1], [18, 19, 20, 21, 22, 23], 'NEG')]
    elif rec_num == 997:
        # Chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        c_trips = [([1], [28, 29, 30], 'POS')]
    elif rec_num == 998:
        # Mong ước dự án 10.000 tỷ -> REJECT
        c_trips = []
    elif rec_num == 999:
        # Mong ước bà Lĩnh -> REJECT
        c_trips = []
    elif rec_num == 1000:
        # cống ngăn triều Tân Thuận -> đang thi công (NEU)
        c_trips = [([8, 9, 10, 11, 12], [22, 23, 24], 'NEU')]

    curated_lines.append(f"{c_text}####{c_trips}")

assert len(curated_lines) == 100, f"Expected 100 lines, got {len(curated_lines)}"

# Read existing lines from phase3.txt
with open('data/validate_label/thuan/phase3.txt', 'r', encoding='utf-8') as f:
    existing_lines = [l.strip() for l in f if l.strip()]

existing_lines = existing_lines[:900]
assert len(existing_lines) == 900, f"Expected 900 existing lines, got {len(existing_lines)}"

total_lines = existing_lines + curated_lines
assert len(total_lines) == 1000, f"Expected 1000 lines, got {len(total_lines)}"

with open('data/validate_label/thuan/phase3.txt', 'w', encoding='utf-8') as f:
    for line in total_lines:
        f.write(line + '\n')

print(f"Successfully updated phase3.txt with batch 10! Total records: {len(total_lines)}")
