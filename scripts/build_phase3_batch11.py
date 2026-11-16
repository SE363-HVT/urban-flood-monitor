import ast, sys, re

sys.stdout.reconfigure(encoding='utf-8')

# Read raw batch 11
with open('scratch_batch11_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

assert len(blocks) == 100, f"Expected 100 blocks, got {len(blocks)}"

curated_lines = []

for idx, b in enumerate(blocks):
    rec_num = 1001 + idx
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
    
    # --- R1001 to R1010 ---
    if rec_num == 1001:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        c_trips = [([1], [10, 11, 12], 'NEU')]
    elif rec_num == 1002:
        # Tâm sự nâng đường nhà thành hầm -> REJECT
        c_trips = []
    elif rec_num == 1003:
        # Tâm sự nâng đường -> REJECT
        c_trips = []
    elif rec_num == 1004:
        # TP. HCM -> Triều cường đạt đỉnh (NEU), dâng cao (NEG)
        c_trips = [
            ([13, 14], [6, 7, 8, 9], 'NEU'),
            ([13, 14], [26, 27], 'NEG')
        ]
    elif rec_num == 1005:
        # TP. HCM -> đạt đỉnh (NEU), trạm Phú An/Nhà Bè -> cao hơn báo động 3 (NEU)
        c_trips = [
            ([12, 13], [15, 16], 'NEU'),
            ([39, 40, 41], [57, 58, 59, 60, 61], 'NEU'),
            ([43, 44], [57, 58, 59, 60, 61], 'NEU')
        ]
    elif rec_num == 1006:
        # HCM -> nguy cơ ngập nước (NEU), đỉnh triều cường (NEU), mưa lớn (NEG)
        c_trips = [
            ([0], [3, 4, 5, 6], 'NEU'),
            ([0], [8, 9, 10], 'NEU'),
            ([0], [13, 14], 'NEG')
        ]
    elif rec_num == 1007:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        c_trips = [([1], [4, 5], 'NEU')]
    elif rec_num == 1008:
        # TP HCM -> sắp đạt đỉnh (NEU)
        c_trips = [([9, 10], [2, 3, 4], 'NEU')]
    elif rec_num == 1009:
        # sông Sài Gòn -> vẫn ở mức cao (NEU), trên báo động 3 (NEU)
        c_trips = [
            ([28, 29], [33, 34, 35, 36], 'NEU'),
            ([28, 29], [38, 39, 40, 41], 'NEU')
        ]
    elif rec_num == 1010:
        # TpHCM -> triều cường đạt đỉnh (NEU)
        c_trips = [([8], [12, 13, 14, 15], 'NEU')]

    # --- R1011 to R1020 ---
    elif rec_num == 1011:
        # Giới thiệu 6 cống của dự án chống ngập 10k tỷ -> REJECT
        c_trips = []
    elif rec_num == 1012:
        # Meme hashtag -> REJECT
        c_trips = []
    elif rec_num == 1013:
        # TP. Hồ Chí Minh -> Triều cường đạt đỉnh lịch sử (NEU), thất thủ (NEG)
        c_trips = [
            ([7, 8, 9, 10], [0, 1, 2, 3, 4, 5], 'NEU'),
            ([7, 8, 9, 10], [11, 12], 'NEG')
        ]
    elif rec_num == 1014:
        # khu nam TP. HCM -> triều cường đạt đỉnh (NEU), ngập sâu (NEG)
        c_trips = [
            ([22, 23, 24, 25], [6, 7, 8, 9], 'NEU'),
            ([22, 23, 24, 25], [26, 27], 'NEG')
        ]
    elif rec_num == 1015:
        # TP. HCM -> triều cường cao (NEU), tăng nguy cơ ngập diện rộng (NEU)
        c_trips = [
            ([5, 6], [11, 12, 13], 'NEU'),
            ([5, 6], [28, 29, 30, 31, 32, 33], 'NEU')
        ]
    elif rec_num == 1016:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        c_trips = [
            ([1], [11, 12, 13, 14], 'NEG'),
            ([1], [15, 16, 17, 18, 19], 'NEG')
        ]
    elif rec_num == 1017:
        # TP. HCM -> sắp đạt đỉnh (NEU), dễ ngập (NEU)
        c_trips = [
            ([6, 7], [2, 3, 4], 'NEU'),
            ([6, 7], [12, 13], 'NEU')
        ]
    elif rec_num == 1018:
        # TPHCM -> đạt đỉnh (NEU)
        c_trips = [([2], [6, 7], 'NEU')]
    elif rec_num == 1019:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        c_trips = [([1], [3, 4, 5, 6], 'NEU')]
    elif rec_num == 1020:
        # Khuyến cáo chung không có địa điểm -> REJECT
        c_trips = []

    # --- R1021 to R1030 ---
    elif rec_num == 1021:
        # TPHCM -> triều cường đạt đỉnh (NEU)
        c_trips = [([1], [11, 12, 13, 14], 'NEU')]
    elif rec_num == 1022:
        # Quận 7, Nhà Bè -> Triều cường đạt đỉnh (NEU), chuẩn bị ngập nặng (NEG)
        c_trips = [
            ([6, 7], [2, 3, 4, 5], 'NEU'),
            ([6, 7], [11, 12, 13, 14], 'NEG'),
            ([9, 10], [2, 3, 4, 5], 'NEU'),
            ([9, 10], [11, 12, 13, 14], 'NEG')
        ]
    elif rec_num == 1023:
        # Trường THCS Nguyễn Thị Thập -> thi công chống ngập (POS)
        c_trips = [([26, 27, 28, 29, 30], [21, 22, 23, 24], 'POS')]
    elif rec_num == 1024:
        # sông Sài Gòn -> tăng nhanh (NEU), đạt đỉnh (NEU)
        c_trips = [
            ([7, 8], [9, 10], 'NEU'),
            ([7, 8], [18, 19], 'NEU')
        ]
    elif rec_num == 1025:
        # Lý thuyết điều kiện không địa danh -> REJECT
        c_trips = []
    elif rec_num == 1026:
        # Khuyến cáo chung -> REJECT
        c_trips = []
    elif rec_num == 1027:
        # Cụt dở dang không địa danh -> REJECT
        c_trips = []
    elif rec_num == 1028:
        # Cụt chữ cuối câu "TP." -> REJECT
        c_trips = []
    elif rec_num == 1029:
        # sông Sài Gòn -> triều cường (NEU)
        c_trips = [([19, 20], [13, 14], 'NEU')]
    elif rec_num == 1030:
        # TP HỒ CHÍ MINH -> NGUY CƠ NGẬP (NEU)
        c_trips = [([11, 12, 13, 14], [7, 8, 9], 'NEU')]

    # --- R1031 to R1040 ---
    elif rec_num == 1031:
        # Cụt chữ cuối câu -> REJECT
        c_trips = []
    elif rec_num == 1032:
        # Cụt chữ cuối câu -> REJECT
        c_trips = []
    elif rec_num == 1033:
        # Quận 7 -> hết ngập (POS), Huỳnh Tấn Phát -> khô queo (POS), Gò Ô Môi -> khô queo (POS)
        c_trips = [
            ([0, 1], [3, 4], 'POS'),
            ([8, 9, 10], [22, 23], 'POS'),
            ([12, 13, 14], [22, 23], 'POS')
        ]
    elif rec_num == 1034:
        # Cống ngăn triều Bến Nghé -> vận hành thử (POS)
        c_trips = [([1, 2, 3, 4, 5], [9, 10, 11], 'POS')]
    elif rec_num == 1035:
        # Cụt chữ cuối câu -> REJECT
        c_trips = []
    elif rec_num == 1036:
        # rạch Văn Thánh -> cải tạo (POS)
        c_trips = [([10, 11, 12], [8, 9], 'POS')]
    elif rec_num == 1037:
        # sông Sài Gòn -> còn ở mức cao (NEU)
        c_trips = [([48, 49], [53, 54, 55, 56], 'NEU')]
    elif rec_num == 1038:
        # sông Sài Gòn -> biến đổi chậm (NEU)
        c_trips = [([48, 49], [50, 51, 52], 'NEU')]
    elif rec_num == 1039:
        # sông Sài Gòn -> còn ở mức cao (NEU)
        c_trips = [([48, 49], [53, 54, 55, 56], 'NEU')]
    elif rec_num == 1040:
        # Thủ Thiêm -> rào chắn thi công (POS)
        c_trips = [([2, 3], [6, 7, 8, 9], 'POS')]

    # --- R1041 to R1050 ---
    elif rec_num == 1041:
        # Câu hỏi tu từ -> REJECT
        c_trips = []
    elif rec_num == 1042:
        # Cụt chữ cuối câu -> REJECT
        c_trips = []
    elif rec_num == 1043:
        # rạch Văn Thánh -> cải tạo (POS)
        c_trips = [([10, 11, 12], [8, 9], 'POS')]
    elif rec_num == 1044:
        # Nam Bộ đa tỉnh -> REJECT
        c_trips = []
    elif rec_num == 1045:
        # sông Sài Gòn -> còn duy trì ở mức cao (NEU)
        c_trips = [([50, 51], [56, 57, 58, 59, 60, 61], 'NEU')]
    elif rec_num == 1046:
        # Không có địa danh cụ thể -> REJECT
        c_trips = []
    elif rec_num == 1047:
        # Chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        c_trips = [([1], [3, 4, 5, 6], 'NEU')]
    elif rec_num == 1048:
        # đường Trần Xuân Soạn -> xây dựng bờ kè (POS)
        c_trips = [([33, 34, 35, 36], [29, 30, 31, 32], 'POS')]
    elif rec_num == 1049:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        c_trips = [([1], [16, 17, 18, 19], 'NEU')]
    elif rec_num == 1050:
        # Quan điểm chính trị xã hội -> REJECT
        c_trips = []

    # --- R1051 to R1060 ---
    elif rec_num == 1051:
        # Khu Nam Sài Gòn -> chuẩn bị hết ngập (POS)
        c_trips = [([0, 1, 2, 3], [4, 5, 6, 7], 'POS')]
    elif rec_num == 1052:
        # Thủ Thiêm, Q2 -> mưa lớn là ngập (NEG)
        c_trips = [
            ([28, 29], [32, 33, 34, 35], 'NEG'),
            ([30], [32, 33, 34, 35], 'NEG')
        ]
    elif rec_num == 1053:
        # Tphcm -> vẫn ở mức cao (NEU), ngập úng (NEG)
        c_trips = [
            ([2], [12, 13, 14, 15], 'NEU'),
            ([2], [19, 20], 'NEG')
        ]
    elif rec_num == 1054:
        # Viral tiktok quán bánh canh -> REJECT
        c_trips = []
    elif rec_num == 1055:
        # TPHCM -> Triều cường lên rất cao (NEU), có nguy cơ ngập (NEU)
        c_trips = [
            ([0], [7, 8, 9, 10, 11], 'NEU'),
            ([0], [21, 22, 23, 24], 'NEU')
        ]
    elif rec_num == 1056:
        # TPHCM -> đạt đỉnh (NEU)
        c_trips = [([3], [6, 7], 'NEU')]
    elif rec_num == 1057:
        # TPHCM -> mênh mông nước (NEG), triều cường đạt đỉnh (NEU)
        c_trips = [
            ([2], [3, 4, 5], 'NEG'),
            ([2], [8, 9, 10, 11], 'NEU')
        ]
    elif rec_num == 1058:
        # TP. HCM -> Triều cường đạt đỉnh (NEU), đi lại khó khăn (NEG)
        c_trips = [
            ([8, 9], [0, 1, 2, 3], 'NEU'),
            ([8, 9], [12, 13, 14, 15], 'NEG')
        ]
    elif rec_num == 1059:
        # TP. HCM -> triều cường đạt đỉnh (NEU)
        c_trips = [([13, 14], [15, 16, 17, 18], 'NEU')]
    elif rec_num == 1060:
        # TP. HCM -> Triều cường đạt đỉnh (NEU)
        c_trips = [([10, 11], [0, 1, 2, 3], 'NEU')]

    # --- R1061 to R1070 ---
    elif rec_num == 1061:
        # TP. HCM -> Triều cường đạt đỉnh (NEU), biển nước (NEG)
        c_trips = [
            ([7, 8], [0, 1, 2, 3], 'NEU'),
            ([7, 8], [12, 13], 'NEG')
        ]
    elif rec_num == 1062:
        # TP. HCM -> Triều cường đạt đỉnh (NEU), biển nước (NEG)
        c_trips = [
            ([7, 8], [0, 1, 2, 3], 'NEU'),
            ([7, 8], [14, 15], 'NEG')
        ]
    elif rec_num == 1063:
        # TP. HCM -> Triều cường dâng cao (NEU), nhiều đường ngập (NEG)
        c_trips = [
            ([7, 8], [0, 1, 2, 3], 'NEU'),
            ([7, 8], [10, 11, 12], 'NEG')
        ]
    elif rec_num == 1064:
        # Hồ Chí Minh -> Triều cường đạt đỉnh (NEU)
        c_trips = [([0, 1, 2], [4, 5, 6, 7], 'NEU')]
    elif rec_num == 1065:
        # TP. HCM -> Triều cường đạt đỉnh (NEU), bì bõm lội nước (NEG)
        c_trips = [
            ([11, 12], [0, 1, 2, 3], 'NEU'),
            ([11, 12], [13, 14, 15, 16], 'NEG')
        ]
    elif rec_num == 1066:
        # TPHCM -> đạt đỉnh (NEU)
        c_trips = [([3], [6, 7], 'NEU')]
    elif rec_num == 1067:
        # khu nam TP. HCM -> Triều cường đạt đỉnh (NEU), lại ngập (NEG)
        c_trips = [
            ([10, 11, 12, 13], [0, 1, 2, 3], 'NEU'),
            ([10, 11, 12, 13], [14, 15], 'NEG')
        ]
    elif rec_num == 1068:
        # Câu hỏi tu từ giật tít -> REJECT
        c_trips = []
    elif rec_num == 1069:
        # TPHCM -> ngập sâu (NEG), triều cường đạt đỉnh (NEU)
        c_trips = [
            ([3], [4, 5], 'NEG'),
            ([3], [8, 9, 10, 11], 'NEU')
        ]
    elif rec_num == 1070:
        # TP. HCM -> sắp đạt đỉnh (NEU), dễ ngập (NEU)
        c_trips = [
            ([6, 7], [2, 3, 4], 'NEU'),
            ([6, 7], [12, 13], 'NEU')
        ]

    # --- R1071 to R1080 ---
    elif rec_num == 1071:
        # khu nam TP. HCM -> Triều cường đạt đỉnh (NEU), ngập như sông (NEG)
        c_trips = [
            ([13, 14, 15, 16], [0, 1, 2, 3], 'NEU'),
            ([13, 14, 15, 16], [17, 18, 19], 'NEG')
        ]
    elif rec_num == 1072:
        # TPHCM -> Triều cường đạt đỉnh (NEU), vật lộn chống ngập (NEG)
        c_trips = [
            ([7], [0, 1, 2, 3], 'NEU'),
            ([7], [8, 9, 10, 11], 'NEG')
        ]
    elif rec_num == 1073:
        # TPHCM -> triều cường đạt đỉnh (NEU), tất tả chặn cửa , bơm nước (NEG)
        c_trips = [
            ([13], [6, 7, 8, 9], 'NEU'),
            ([13], [14, 15, 16, 17, 18, 19, 20], 'NEG')
        ]
    elif rec_num == 1074:
        # TPHCM -> Triều cường đạt đỉnh (NEU), ngập nước (NEG)
        c_trips = [
            ([5], [0, 1, 2, 3], 'NEU'),
            ([5], [9, 10], 'NEG')
        ]
    elif rec_num == 1075:
        # sông Sài Gòn -> Cảnh báo triều cường (NEU)
        c_trips = [([7, 8, 9], [2, 3, 4, 5], 'NEU')]
    elif rec_num == 1076:
        # Nam Bộ đa tỉnh -> REJECT
        c_trips = []
    elif rec_num == 1077:
        # TPHCM -> ngập (NEG), triều cường đạt đỉnh (NEU)
        c_trips = [
            ([0], [1], 'NEG'),
            ([0], [10, 11, 12, 13], 'NEU')
        ]
    elif rec_num == 1078:
        # TPHCM -> đạt đỉnh (NEU), chết máy (NEG)
        c_trips = [
            ([5], [6, 7], 'NEU'),
            ([5], [17, 18], 'NEG')
        ]
    elif rec_num == 1079:
        # TPHCM -> vật vã lội nước (NEG), triều cường đạt đỉnh (NEU)
        c_trips = [
            ([2], [3, 4, 5, 6], 'NEG'),
            ([2], [11, 12, 13, 14], 'NEU')
        ]
    elif rec_num == 1080:
        # TPHCM -> Triều cường hơn 1 , 7m (NEU), nguy cơ ngập (NEU)
        c_trips = [
            ([13], [0, 1, 2, 3, 4, 5], 'NEU'),
            ([13], [7, 8, 9], 'NEU')
        ]

    # --- R1081 to R1090 ---
    elif rec_num == 1081:
        # TPHCM -> Mưa lớn kéo dài (NEG), triều cường đạt đỉnh (NEU), nguy cơ ngập úng diện rộng (NEU)
        c_trips = [
            ([0], [2, 3, 4, 5], 'NEG'),
            ([0], [8, 9, 10, 11], 'NEU'),
            ([0], [13, 14, 15, 16, 17, 18], 'NEU')
        ]
    elif rec_num == 1082:
        # TPHCM -> đạt đỉnh (NEU), thành sông (NEG)
        c_trips = [
            ([3], [4, 5], 'NEU'),
            ([3], [11, 12], 'NEG')
        ]
    elif rec_num == 1083:
        # TP. HCM -> đạt đỉnh (NEU)
        c_trips = [([3, 4], [5, 6], 'NEU')]
    elif rec_num == 1084:
        # TP. HCM -> Triều cường đạt đỉnh kỷ lục (NEU)
        c_trips = [([14, 15], [0, 1, 2, 3, 4, 5], 'NEU')]
    elif rec_num == 1085:
        # TP. HCM -> Triều cường đạt đỉnh (NEU), ngập sâu (NEG)
        c_trips = [
            ([0, 1], [3, 4, 5, 6], 'NEU'),
            ([0, 1], [15, 16], 'NEG')
        ]
    elif rec_num == 1086:
        # TP. HCM -> Triều cường đạt đỉnh (NEU)
        c_trips = [([5, 6], [0, 1, 2, 3], 'NEU')]
    elif rec_num == 1087:
        # TPHCM -> triều cường đạt đỉnh (NEU)
        c_trips = [([15], [10, 11, 12, 13], 'NEU')]
    elif rec_num == 1088:
        # TP. HCM -> Triều cường đạt đỉnh (NEU), ngập sâu (NEG)
        c_trips = [
            ([0, 1], [3, 4, 5, 6], 'NEU'),
            ([0, 1], [15, 16], 'NEG')
        ]
    elif rec_num == 1089:
        # TP. HCM -> triều cường đạt đỉnh (NEU), vật vã (NEG)
        c_trips = [
            ([2, 3], [7, 8, 9, 10], 'NEU'),
            ([2, 3], [4, 5], 'NEG')
        ]
    elif rec_num == 1090:
        # TP. HCM -> Triều cường đạt đỉnh (NEU), lại thành sông (NEG)
        c_trips = [
            ([9, 10], [0, 1, 2, 3], 'NEU'),
            ([9, 10], [11, 12, 13], 'NEG')
        ]

    # --- R1091 to R1100 ---
    elif rec_num == 1091:
        # TPHCM -> như miền Tây mùa nước nổi (NEG), triều cường đạt đỉnh lịch sử (NEU)
        c_trips = [
            ([0], [1, 2, 3, 4, 5, 6], 'NEG'),
            ([0], [8, 9, 10, 11, 12, 13], 'NEU')
        ]
    elif rec_num == 1092:
        # TPHCM -> triều cường đạt đỉnh (NEU), Cảnh báo ngập (NEU)
        c_trips = [
            ([9], [4, 5, 6, 7], 'NEU'),
            ([9], [0, 1, 2], 'NEU')
        ]
    elif rec_num == 1093:
        # TP. HCM -> Triều cường đạt đỉnh (NEU), chống ngập (POS)
        c_trips = [
            ([5, 6], [0, 1, 2, 3], 'NEU'),
            ([5, 6], [16, 17], 'POS')
        ]
    elif rec_num == 1094:
        # TP. HCM -> Triều cường đạt đỉnh (NEU), gây ngập (NEG)
        c_trips = [
            ([10, 11], [0, 1, 2, 3], 'NEU'),
            ([10, 11], [4, 5], 'NEG')
        ]
    elif rec_num == 1095:
        # đường Trần Xuân Soạn -> Triều cường đạt đỉnh (NEU), ngập nửa bánh xe (NEG)
        c_trips = [
            ([10, 11, 12, 13], [0, 1, 2, 3], 'NEU'),
            ([10, 11, 12, 13], [5, 6, 7, 8], 'NEG')
        ]
    elif rec_num == 1096:
        # Trung tâm Sài Gòn -> ngập nước (NEG), triều cường đạt đỉnh (NEU)
        c_trips = [
            ([2, 3, 4, 5], [6, 7], 'NEG'),
            ([2, 3, 4, 5], [10, 11, 12, 13], 'NEU')
        ]
    elif rec_num == 1097:
        # Câu hỏi tu từ than thở -> REJECT
        c_trips = []
    elif rec_num == 1098:
        # Câu hỏi giật tít hoài nghi -> REJECT
        c_trips = []
    elif rec_num == 1099:
        # đường Trần Xuân Soạn -> Triều cường đạt đỉnh (NEU), không còn bến bờ (NEG)
        c_trips = [
            ([5, 6, 7, 8], [0, 1, 2, 3], 'NEU'),
            ([5, 6, 7, 8], [9, 10, 11, 12], 'NEG')
        ]
    elif rec_num == 1100:
        # Chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        c_trips = [([1], [27, 28, 29, 30, 31, 32], 'NEU')]

    curated_lines.append(f"{c_text}####{c_trips}")

assert len(curated_lines) == 100, f"Expected 100 lines, got {len(curated_lines)}"

# Read existing lines from phase3.txt
with open('data/validate_label/thuan/phase3.txt', 'r', encoding='utf-8') as f:
    existing_lines = [l.strip() for l in f if l.strip()]

existing_lines = existing_lines[:1000]
assert len(existing_lines) == 1000, f"Expected 1000 existing lines, got {len(existing_lines)}"

total_lines = existing_lines + curated_lines
assert len(total_lines) == 1100, f"Expected 1100 lines, got {len(total_lines)}"

with open('data/validate_label/thuan/phase3.txt', 'w', encoding='utf-8') as f:
    for line in total_lines:
        f.write(line + '\n')

print(f"Successfully updated phase3.txt with batch 11! Total records: {len(total_lines)}")
