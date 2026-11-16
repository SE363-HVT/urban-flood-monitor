import ast, sys, re

sys.stdout.reconfigure(encoding='utf-8')

# Read raw batch 12
with open('scratch_batch12_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

assert len(blocks) == 100, f"Expected 100 blocks, got {len(blocks)}"

curated_lines = []

for idx, b in enumerate(blocks):
    rec_num = 1101 + idx
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
    
    # --- R1101 to R1110 ---
    if rec_num == 1101:
        # đường Lương Định Của -> nước rút dần (POS), Trần Xuân Soạn -> nước rút dần (POS)
        c_trips = [
            ([11, 12, 13, 14], [3, 4, 5], 'POS'),
            ([16, 17, 18], [3, 4, 5], 'POS')
        ]
    elif rec_num == 1102:
        # Chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        c_trips = [([1], [20, 21, 22, 23, 24], 'NEU')]
    elif rec_num == 1103:
        # trạm Phú An -> đạt mức 1 , 69 - 1 , 7 m (NEU), Nhà Bè -> đạt mức 1 , 69 - 1 , 7 m (NEU)
        c_trips = [
            ([19, 20, 21], [8, 9, 10, 11, 12, 13, 14, 15, 16, 17], 'NEU'),
            ([23, 24], [8, 9, 10, 11, 12, 13, 14, 15, 16, 17], 'NEU')
        ]
    elif rec_num == 1104:
        # Cầu Kinh Dương Vương Bắc Ninh (tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 1105:
        # đường Lê Hồng Phong -> nước ngập (NEG), xe chết máy (NEG)
        c_trips = [
            ([2, 3, 4, 5], [7, 8], 'NEG'),
            ([2, 3, 4, 5], [33, 34, 35], 'NEG')
        ]
    elif rec_num == 1106:
        # Cụt dở dang cuối câu "ở TP." -> REJECT
        c_trips = []
    elif rec_num == 1107:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        c_trips = [
            ([1], [15, 16, 17, 18, 19], 'NEG'),
            ([1], [25, 26, 27], 'NEU'),
            ([1], [30, 31, 32, 33, 34], 'NEU')
        ]
    elif rec_num == 1108:
        # Cần Thơ, Hậu Giang, Vĩnh Long (tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 1109:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        c_trips = [
            ([1], [14, 15, 16, 17, 18], 'NEU'),
            ([1], [20, 21, 22, 23, 24], 'NEU')
        ]
    elif rec_num == 1110:
        # Nam Bộ đa tỉnh -> REJECT
        c_trips = []

    # --- R1111 to R1120 ---
    elif rec_num == 1111:
        # Phường Bình Thủy ở Cần Thơ (tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 1112:
        # Chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        c_trips = [([1], [17, 18, 19, 20, 21, 22], 'NEU')]
    elif rec_num == 1113:
        # Cảnh báo chung không có địa điểm cụ thể -> REJECT
        c_trips = []
    elif rec_num == 1114:
        # Lý thuyết chung -> REJECT
        c_trips = []
    elif rec_num == 1115:
        # Chuẩn hóa tiền tố "Tại TPHCM , "
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = "Tại TPHCM , " + c_text[len(prefix):].strip()
        c_trips = [
            ([1], [14, 15, 16, 17, 18], 'NEU'),
            ([1], [39, 40, 41], 'NEU')
        ]
    elif rec_num == 1116:
        # Khuyến cáo chung -> REJECT
        c_trips = []
    elif rec_num == 1117:
        # sông Sài Gòn -> vượt mức báo động 3 (NEU), đạt đỉnh (NEU)
        c_trips = [
            ([12, 13, 14], [17, 18, 19, 20, 21], 'NEU'),
            ([12, 13, 14], [31, 32], 'NEU')
        ]
    elif rec_num == 1118:
        # trạm Phú An -> vượt báo động 3 (NEU), Nhà Bè -> vượt báo động 3 (NEU)
        c_trips = [
            ([20, 21, 22], [39, 40, 41, 42], 'NEU'),
            ([24, 25], [39, 40, 41, 42], 'NEU')
        ]
    elif rec_num == 1119:
        # Hầm chui này không rõ -> REJECT
        c_trips = []
    elif rec_num == 1120:
        # TPHCM -> đạt đỉnh (NEU), gây ngập (NEG)
        c_trips = [
            ([17], [20, 21], 'NEU'),
            ([17], [32, 33], 'NEG')
        ]

    # --- R1121 to R1130 ---
    elif rec_num == 1121:
        # Hashtag meme -> REJECT
        c_trips = []
    elif rec_num == 1122:
        # ĐBSCL (miền Tây) -> REJECT
        c_trips = []
    elif rec_num == 1123:
        # TP. HCM -> lên đỉnh (NEU), ngập (NEU), đạt đỉnh (NEU)
        c_trips = [
            ([2, 3], [4, 5], 'NEU'),
            ([2, 3], [13], 'NEU'),
            ([21, 22], [26, 27], 'NEU')
        ]
    elif rec_num == 1124:
        # Chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        c_trips = [
            ([1], [3, 4, 5, 6], 'NEU'),
            ([1], [8, 9, 10, 11, 12, 13, 14], 'NEU')
        ]
    elif rec_num == 1125:
        # TPHCM -> Mưa lớn (NEG), triều cường vượt báo động 3 (NEU), nguy cơ ngập sâu (NEU)
        c_trips = [
            ([11], [0, 1], 'NEG'),
            ([11], [4, 5, 6, 7, 8, 9], 'NEU'),
            ([11], [14, 15, 16, 17], 'NEU')
        ]
    elif rec_num == 1126:
        # TPHCM -> LÊN NHANH (NEU), NGUY CƠ NGẬP SÂU (NEU), sông Sài Gòn -> vượt báo động 3 (NEU)
        c_trips = [
            ([2], [3, 4], 'NEU'),
            ([2], [6, 7, 8, 9], 'NEU'),
            ([34, 35], [36, 37, 38, 39], 'NEU')
        ]
    elif rec_num == 1127:
        # TPHCM -> nguy cơ ngập (NEU)
        c_trips = [([15], [18, 19], 'NEU')]
    elif rec_num == 1128:
        # HCM -> nguy cơ ngập nước (NEU), mưa lớn (NEG)
        c_trips = [
            ([0], [3, 4, 5, 6], 'NEU'),
            ([0], [13, 14], 'NEG')
        ]
    elif rec_num == 1129:
        # TP. HCM -> triều cường cao (NEU), tăng nguy cơ ngập diện rộng (NEU)
        c_trips = [
            ([5, 6], [11, 12, 13], 'NEU'),
            ([5, 6], [28, 29, 30, 31, 32, 33], 'NEU')
        ]
    elif rec_num == 1130:
        # TPHCM -> sắp đạt đỉnh (NEU), lại ngập nặng (NEG), đe dọa gây ngập (NEG)
        c_trips = [
            ([10], [6, 7, 8], 'NEU'),
            ([10], [18, 19, 20], 'NEG'),
            ([46], [41, 42, 43, 44], 'NEG')
        ]

    # --- R1131 to R1140 ---
    elif rec_num == 1131:
        # tuyến đường Đặng Thùy Trâm -> mưa lớn là ngập (NEG)
        c_trips = [([18, 19, 20, 21, 22], [27, 28, 29, 30], 'NEG')]
    elif rec_num == 1132:
        # ĐƯỜNG LƯƠNG ĐỊNH CỦA -> NGẬP NƯỚC (NEG), Thủ Thiêm -> mưa lớn là ngập (NEG), Q2 -> mưa lớn là ngập (NEG)
        c_trips = [
            ([2, 3, 4, 5], [0, 1], 'NEG'),
            ([45, 46], [49, 50, 51, 52], 'NEG'),
            ([47], [49, 50, 51, 52], 'NEG')
        ]
    elif rec_num == 1133:
        # Kha Vạn Cân -> khô ráo (POS)
        c_trips = [([9, 10, 11], [14, 15], 'POS')]
    elif rec_num == 1134:
        # Phạm Thế Hiển -> thông suốt (POS)
        c_trips = [([6, 7, 8], [9, 10], 'POS')]
    elif rec_num == 1135:
        # Quốc lộ 13 -> thông xe (POS), đi lại dễ dàng (POS)
        c_trips = [
            ([3, 4, 5], [10, 11], 'POS'),
            ([3, 4, 5], [15, 16, 17, 18], 'POS')
        ]
    elif rec_num == 1136:
        # Đỗ Xuân Hợp -> đi lại bình thường (POS)
        c_trips = [([4, 5, 6], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1137:
        # Đoạn đường Nguyễn Duy -> thông thoáng (POS)
        c_trips = [([0, 1, 2, 3], [11, 12], 'POS')]
    elif rec_num == 1138:
        # Nguyễn Duy -> hết ngập hoàn toàn (POS)
        c_trips = [([6, 7], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1139:
        # Kinh Dương Vương -> khô ráo (POS)
        c_trips = [([5, 6, 7], [16, 17], 'POS')]
    elif rec_num == 1140:
        # Lương Định Của -> nước rút sạch (POS)
        c_trips = [([3, 4, 5], [10, 11, 12], 'POS')]

    # --- R1141 to R1150 ---
    elif rec_num == 1141:
        # Đoạn đường Dương Văn Cam -> thông thoáng (POS)
        c_trips = [([0, 1, 2, 3, 4], [12, 13], 'POS')]
    elif rec_num == 1142:
        # Đoạn đường Trần Hưng Đạo -> thông thoáng (POS)
        c_trips = [([0, 1, 2, 3, 4], [12, 13], 'POS')]
    elif rec_num == 1143:
        # Kha Vạn Cân -> hết ngập hẳn (POS)
        c_trips = [([5, 6, 7], [15, 16, 17], 'POS')]
    elif rec_num == 1144:
        # Đường Lương Định Của -> lưu thông bình thường (POS)
        c_trips = [([0, 1, 2, 3], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1145:
        # Tô Ngọc Vân -> hết ngập hẳn (POS)
        c_trips = [([5, 6, 7], [15, 16, 17], 'POS')]
    elif rec_num == 1146:
        # Bạch Đằng -> khô ráo (POS)
        c_trips = [([3, 4], [7, 8], 'POS')]
    elif rec_num == 1147:
        # Tuyến đường Nguyễn Văn Hưởng -> nước rút sạch (POS)
        c_trips = [([0, 1, 2, 3, 4], [7, 8, 9], 'POS')]
    elif rec_num == 1148:
        # đường Nguyễn Biểu -> khô ráo sạch sẽ (POS)
        c_trips = [([6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1149:
        # Bến Phú Định -> hết ngập hoàn toàn (POS)
        c_trips = [([6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1150:
        # Thảo Điền -> thông suốt (POS)
        c_trips = [([6, 7], [8, 9], 'POS')]

    # --- R1151 to R1160 ---
    elif rec_num == 1151:
        # đường Đoàn Văn Bơ -> nước đã rút (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11], 'POS')]
    elif rec_num == 1152:
        # Đoạn đường Nguyễn Hữu Cảnh -> thông suốt (POS)
        c_trips = [([0, 1, 2, 3, 4], [10, 11], 'POS')]
    elif rec_num == 1153:
        # An Dương Vương -> hết ngập hẳn (POS)
        c_trips = [([5, 6, 7], [15, 16, 17], 'POS')]
    elif rec_num == 1154:
        # đường Đặng Thị Rành -> khô ráo sạch sẽ (POS)
        c_trips = [([6, 7, 8, 9], [10, 11, 12, 13], 'POS')]
    elif rec_num == 1155:
        # Trần Hưng Đạo -> khô ráo (POS)
        c_trips = [([5, 6, 7], [16, 17], 'POS')]
    elif rec_num == 1156:
        # Quốc Hương -> hết ngập hoàn toàn (POS)
        c_trips = [([6, 7], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1157:
        # Kinh Dương Vương -> hết ngập hẳn (POS)
        c_trips = [([5, 6, 7], [15, 16, 17], 'POS')]
    elif rec_num == 1158:
        # Lương Định Của -> nước rút sạch (POS)
        c_trips = [([3, 4, 5], [8, 9, 10], 'POS')]
    elif rec_num == 1159:
        # Đặng Thị Rành -> thông xe (POS), đi lại dễ dàng (POS)
        c_trips = [
            ([3, 4, 5], [10, 11], 'POS'),
            ([3, 4, 5], [15, 16, 17, 18], 'POS')
        ]
    elif rec_num == 1160:
        # đường Lương Định Của -> lưu thông bình thường (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]

    # --- R1161 to R1170 ---
    elif rec_num == 1161:
        # Trần Xuân Soạn -> nước đã rút (POS)
        c_trips = [([4, 5, 6], [8, 9, 10], 'POS')]
    elif rec_num == 1162:
        # Lê Văn Việt -> nước đã rút sạch (POS)
        c_trips = [([6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1163:
        # Đoạn đường Quốc Hương -> thông thoáng (POS)
        c_trips = [([0, 1, 2, 3], [11, 12], 'POS')]
    elif rec_num == 1164:
        # Hồ Học Lãm -> thông thoáng (POS)
        c_trips = [([4, 5, 6], [8, 9], 'POS')]
    elif rec_num == 1165:
        # đường Nguyễn Xí -> thông thoáng (POS)
        c_trips = [([6, 7, 8], [9, 10], 'POS')]
    elif rec_num == 1166:
        # Đoàn Văn Bơ -> khô queo (POS)
        c_trips = [([9, 10, 11], [12, 13], 'POS')]
    elif rec_num == 1167:
        # đường Nguyễn Văn Hưởng -> đã khô ráo (POS)
        c_trips = [([6, 7, 8, 9], [10, 11, 12], 'POS')]
    elif rec_num == 1168:
        # đường Lê Đức Thọ -> khô ráo hoàn toàn (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1169:
        # Tuyến đường Dương Văn Cam -> không còn ngập nữa (POS)
        c_trips = [([0, 1, 2, 3, 4], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1170:
        # Trần Xuân Soạn -> khô ráo (POS)
        c_trips = [([3, 4, 5], [8, 9], 'POS')]

    # --- R1171 to R1180 ---
    elif rec_num == 1171:
        # Đoạn đường Phan Huy Ích -> khô ráo sạch sẽ (POS)
        c_trips = [([0, 1, 2, 3, 4], [10, 11, 12, 13], 'POS')]
    elif rec_num == 1172:
        # đường Nguyễn Văn Khối -> đã khô ráo (POS)
        c_trips = [([6, 7, 8, 9], [10, 11, 12], 'POS')]
    elif rec_num == 1173:
        # Đặng Thị Rành -> thông thoáng (POS)
        c_trips = [([4, 5, 6], [8, 9], 'POS')]
    elif rec_num == 1174:
        # Phạm Thế Hiển -> thông thoáng trở lại (POS)
        c_trips = [([3, 4, 5], [6, 7, 8, 9], 'POS')]
    elif rec_num == 1175:
        # Dương Văn Cam -> hết ngập hẳn (POS)
        c_trips = [([5, 6, 7], [15, 16, 17], 'POS')]
    elif rec_num == 1176:
        # Đường Võ Văn Ngân -> nước rút rất nhanh (POS)
        c_trips = [([0, 1, 2, 3], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1177:
        # Trần Hưng Đạo -> thông thoáng (POS)
        c_trips = [([4, 5, 6], [8, 9], 'POS')]
    elif rec_num == 1178:
        # Lê Văn Việt -> thông thoáng (POS)
        c_trips = [([4, 5, 6], [8, 9], 'POS')]
    elif rec_num == 1179:
        # Tuyến đường Nguyễn Văn Hưởng -> không ngập (POS)
        c_trips = [([0, 1, 2, 3, 4], [7, 8], 'POS')]
    elif rec_num == 1180:
        # Hồ Học Lãm -> hết ngập hẳn (POS)
        c_trips = [([3, 4, 5], [6, 7, 8], 'POS')]

    # --- R1181 to R1190 ---
    elif rec_num == 1181:
        # đường Trần Xuân Soạn -> không còn ngập nước (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1182:
        # Đoạn đường Nguyễn Biểu -> thông suốt (POS)
        c_trips = [([0, 1, 2, 3], [9, 10], 'POS')]
    elif rec_num == 1183:
        # Ung Văn Khiêm -> khô ráo (POS)
        c_trips = [([6, 7, 8], [9, 10], 'POS')]
    elif rec_num == 1184:
        # đường Dương Văn Cam -> thông thoáng (POS)
        c_trips = [([6, 7, 8, 9], [10, 11], 'POS')]
    elif rec_num == 1185:
        # Tô Ngọc Vân -> khô queo (POS), đi lại dễ dàng (POS)
        c_trips = [
            ([3, 4, 5], [10, 11], 'POS'),
            ([3, 4, 5], [14, 15, 16, 17], 'POS')
        ]
    elif rec_num == 1186:
        # Lê Văn Việt -> thông xe (POS)
        c_trips = [([5, 6, 7], [15, 16], 'POS')]
    elif rec_num == 1187:
        # Ung Văn Khiêm -> nước đã rút (POS)
        c_trips = [([5, 6, 7], [15, 16, 17], 'POS')]
    elif rec_num == 1188:
        # Đặng Thị Rành -> đã khô ráo (POS)
        c_trips = [([5, 6, 7], [15, 16, 17], 'POS')]
    elif rec_num == 1189:
        # Đỗ Xuân Hợp -> nước đã rút (POS)
        c_trips = [([9, 10, 11], [12, 13, 14], 'POS')]
    elif rec_num == 1190:
        # Lê Đức Thọ -> nước đã rút sạch (POS)
        c_trips = [([6, 7, 8], [9, 10, 11, 12], 'POS')]

    # --- R1191 to R1200 ---
    elif rec_num == 1191:
        # Tô Ngọc Vân -> thông thoáng (POS)
        c_trips = [([3, 4, 5], [8, 9], 'POS')]
    elif rec_num == 1192:
        # Bến Phú Định -> khô ráo (POS)
        c_trips = [([3, 4, 5], [8, 9], 'POS')]
    elif rec_num == 1193:
        # Bình Quới -> khô queo (POS), đi lại dễ dàng (POS)
        c_trips = [
            ([3, 4], [9, 10], 'POS'),
            ([3, 4], [13, 14, 15, 16], 'POS')
        ]
    elif rec_num == 1194:
        # đường Thảo Điền -> đã khô ráo (POS)
        c_trips = [([6, 7, 8], [9, 10, 11], 'POS')]
    elif rec_num == 1195:
        # Đoạn đường Nguyễn Duy -> nước rút hết (POS)
        c_trips = [([0, 1, 2, 3], [9, 10, 11], 'POS')]
    elif rec_num == 1196:
        # Đinh Bộ Lĩnh -> khô queo (POS)
        c_trips = [([9, 10, 11], [12, 13], 'POS')]
    elif rec_num == 1197:
        # Tuyến đường Hồ Học Lãm -> không còn ngập nữa (POS)
        c_trips = [([0, 1, 2, 3, 4], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1198:
        # Đào Trí -> khô ráo (POS)
        c_trips = [([9, 10], [13, 14], 'POS')]
    elif rec_num == 1199:
        # đường Đỗ Xuân Hợp -> nước đã rút hết (POS)
        c_trips = [([6, 7, 8, 9], [10, 11, 12, 13], 'POS')]
    elif rec_num == 1200:
        # Đường Đào Trí -> thông thoáng trở lại (POS)
        c_trips = [([0, 1, 2], [6, 7, 8, 9], 'POS')]

    curated_lines.append(f"{c_text}####{c_trips}")

assert len(curated_lines) == 100, f"Expected 100 lines, got {len(curated_lines)}"

# Read existing lines from phase3.txt
with open('data/validate_label/thuan/phase3.txt', 'r', encoding='utf-8') as f:
    existing_lines = [l.strip() for l in f if l.strip()]

existing_lines = existing_lines[:1100]
assert len(existing_lines) == 1100, f"Expected 1100 existing lines, got {len(existing_lines)}"

total_lines = existing_lines + curated_lines
assert len(total_lines) == 1200, f"Expected 1200 lines, got {len(total_lines)}"

with open('data/validate_label/thuan/phase3.txt', 'w', encoding='utf-8') as f:
    for line in total_lines:
        f.write(line + '\n')

print(f"Successfully updated phase3.txt with batch 12! Total records: {len(total_lines)}")
