import ast, sys, re

sys.stdout.reconfigure(encoding='utf-8')

# Read raw batch 13
with open('scratch_batch13_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

assert len(blocks) == 100, f"Expected 100 blocks, got {len(blocks)}"

curated_lines = []

for idx, b in enumerate(blocks):
    rec_num = 1201 + idx
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
    
    # --- R1201 to R1210 ---
    if rec_num == 1201:
        # Đỗ Xuân Hợp -> nước rút sạch (POS)
        c_trips = [([3, 4, 5], [10, 11, 12], 'POS')]
    elif rec_num == 1202:
        # Phạm Văn Đồng -> khô ráo (POS)
        c_trips = [([3, 4, 5], [8, 9], 'POS')]
    elif rec_num == 1203:
        # Hồ Học Lãm -> hết ngập (POS)
        c_trips = [([3, 4, 5], [8, 9], 'POS')]
    elif rec_num == 1204:
        # đường Đặng Thị Rành -> khô ráo (POS)
        c_trips = [([1, 2, 3, 4], [7, 8], 'POS')]
    elif rec_num == 1205:
        # đường Phạm Thế Hiển -> không còn ngập nữa (POS)
        c_trips = [([1, 2, 3, 4], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1206:
        # Bến Phú Định -> hết ngập hẳn (POS)
        c_trips = [([3, 4, 5], [6, 7, 8], 'POS')]
    elif rec_num == 1207:
        # Quốc lộ 13 -> thông thoáng (POS)
        c_trips = [([6, 7, 8], [11, 12], 'POS')]
    elif rec_num == 1208:
        # Bến Phú Định -> khô rang (POS)
        c_trips = [([5, 6, 7], [15, 16], 'POS')]
    elif rec_num == 1209:
        # đường Nguyễn Biểu -> nước rút sạch (POS)
        c_trips = [([1, 2, 3], [6, 7, 8], 'POS')]
    elif rec_num == 1210:
        # Tô Ngọc Vân -> thông xe (POS), đi lại dễ dàng (POS)
        c_trips = [
            ([3, 4, 5], [10, 11], 'POS'),
            ([3, 4, 5], [15, 16, 17, 18], 'POS')
        ]

    # --- R1211 to R1220 ---
    elif rec_num == 1211:
        # Dương Văn Cam -> thông thoáng (POS)
        c_trips = [([4, 5, 6], [8, 9], 'POS')]
    elif rec_num == 1212:
        # Đường Nguyễn Văn Khối -> lưu thông bình thường (POS)
        c_trips = [([0, 1, 2, 3], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1213:
        # đường Huỳnh Tấn Phát -> không ngập (POS)
        c_trips = [([1, 2, 3, 4], [7, 8], 'POS')]
    elif rec_num == 1214:
        # Quốc lộ 13 -> nước rút sạch (POS)
        c_trips = [([3, 4, 5], [8, 9, 10], 'POS')]
    elif rec_num == 1215:
        # đường Đoàn Văn Bơ -> khô ráo sạch sẽ (POS)
        c_trips = [([6, 7, 8, 9], [10, 11, 12, 13], 'POS')]
    elif rec_num == 1216:
        # đường Hồ Học Lãm -> nước rút sạch (POS)
        c_trips = [([1, 2, 3, 4], [7, 8, 9], 'POS')]
    elif rec_num == 1217:
        # đường Bạch Đằng -> khô ráo (POS)
        c_trips = [([1, 2, 3], [6, 7], 'POS')]
    elif rec_num == 1218:
        # đường Đinh Bộ Lĩnh -> đã khô ráo (POS)
        c_trips = [([6, 7, 8, 9], [10, 11, 12], 'POS')]
    elif rec_num == 1219:
        # Đường Quốc Hương -> nước đã rút hoàn toàn (POS)
        c_trips = [([0, 1, 2], [6, 7, 8, 9, 10], 'POS')]
    elif rec_num == 1220:
        # Mễ Cốc -> khô ráo (POS)
        c_trips = [([9, 10], [13, 14], 'POS')]

    # --- R1221 to R1230 ---
    elif rec_num == 1221:
        # Trần Xuân Soạn -> ổn định trở lại (POS)
        c_trips = [([3, 4, 5], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1222:
        # Huỳnh Tấn Phát -> khô rang (POS)
        c_trips = [([5, 6, 7], [15, 16], 'POS')]
    elif rec_num == 1223:
        # Nguyễn Văn Hưởng -> khô ráo (POS)
        c_trips = [([6, 7, 8], [9, 10], 'POS')]
    elif rec_num == 1224:
        # đường Lê Văn Lương -> khô ráo sạch sẽ (POS)
        c_trips = [([1, 2, 3, 4], [10, 11, 12, 13], 'POS')]
    elif rec_num == 1225:
        # Trần Xuân Soạn -> nước đã rút sạch (POS)
        c_trips = [([3, 4, 5], [6, 7, 8, 9], 'POS')]
    elif rec_num == 1226:
        # đường Đinh Bộ Lĩnh -> khô ráo sạch sẽ (POS)
        c_trips = [([1, 2, 3, 4], [10, 11, 12, 13], 'POS')]
    elif rec_num == 1227:
        # đường Lê Văn Lương -> không còn ngập nữa (POS)
        c_trips = [([1, 2, 3, 4], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1228:
        # Dương Văn Cam -> khô rang (POS)
        c_trips = [([5, 6, 7], [15, 16], 'POS')]
    elif rec_num == 1229:
        # Nguyễn Biểu -> thông thoáng (POS)
        c_trips = [([4, 5], [7, 8], 'POS')]
    elif rec_num == 1230:
        # An Dương Vương -> nước đã rút sạch (POS)
        c_trips = [([6, 7, 8], [9, 10, 11, 12], 'POS')]

    # --- R1231 to R1240 ---
    elif rec_num == 1231:
        # Đường Trần Xuân Soạn -> thông thoáng trở lại (POS)
        c_trips = [([0, 1, 2, 3], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1232:
        # Bến Phú Định -> hết ngập (POS)
        c_trips = [([3, 4, 5], [8, 9], 'POS')]
    elif rec_num == 1233:
        # Tô Ngọc Vân -> đi lại bình thường (POS)
        c_trips = [([4, 5, 6], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1234:
        # Đường Lương Định Của -> nước rút rất nhanh (POS)
        c_trips = [([0, 1, 2, 3], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1235:
        # đường Calmette -> không ngập (POS)
        c_trips = [([1, 2, 3], [5, 6], 'POS')]
    elif rec_num == 1236:
        # Đường Nguyễn Văn Khối -> nước rút rất nhanh (POS)
        c_trips = [([0, 1, 2, 3], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1237:
        # đường Quốc lộ 13 -> thông suốt (POS)
        c_trips = [([1, 2, 3, 4], [10, 11], 'POS')]
    elif rec_num == 1238:
        # đường Thảo Điền -> không còn ngập nữa (POS)
        c_trips = [([1, 2, 3, 4], [6, 7, 8, 9], 'POS')]
    elif rec_num == 1239:
        # đường Hoàng Diệu -> nước đã rút sạch sẽ (POS)
        c_trips = [([1, 2, 3], [9, 10, 11, 12, 13], 'POS')]
    elif rec_num == 1240:
        # Đường Quốc lộ 13 -> nước rút rất nhanh (POS)
        c_trips = [([0, 1, 2, 3], [7, 8, 9, 10], 'POS')]

    # --- R1241 to R1250 ---
    elif rec_num == 1241:
        # Tô Ngọc Vân -> hết ngập hẳn (POS)
        c_trips = [([9, 10, 11], [12, 13, 14], 'POS')]
    elif rec_num == 1242:
        # đường Đào Trí -> khô ráo hoàn toàn (POS)
        c_trips = [([5, 6, 7], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1243:
        # đường Phạm Văn Đồng -> khô ráo (POS)
        c_trips = [([1, 2, 3, 4], [7, 8], 'POS')]
    elif rec_num == 1244:
        # Phạm Thế Hiển -> khô ráo (POS)
        c_trips = [([9, 10, 11], [14, 15], 'POS')]
    elif rec_num == 1245:
        # đường Ung Văn Khiêm -> khô ráo sạch sẽ (POS)
        c_trips = [([1, 2, 3, 4], [10, 11, 12, 13], 'POS')]
    elif rec_num == 1246:
        # Kha Vạn Cân -> hết ngập hẳn (POS)
        c_trips = [([9, 10, 11], [12, 13, 14], 'POS')]
    elif rec_num == 1247:
        # đường Phạm Thế Hiển -> không ngập (POS)
        c_trips = [([1, 2, 3, 4], [7, 8], 'POS')]
    elif rec_num == 1248:
        # Đỗ Xuân Hợp -> thông thoáng trở lại (POS)
        c_trips = [([3, 4, 5], [6, 7, 8, 9], 'POS')]
    elif rec_num == 1249:
        # Phạm Thế Hiển -> đã khô ráo (POS)
        c_trips = [([3, 4, 5], [10, 11, 12], 'POS')]
    elif rec_num == 1250:
        # Calmette -> hết ngập hẳn (POS)
        c_trips = [([5], [13, 14, 15], 'POS')]

    # --- R1251 to R1260 ---
    elif rec_num == 1251:
        # Lê Văn Việt -> hết ngập (POS)
        c_trips = [([4, 5, 6], [8, 9], 'POS')]
    elif rec_num == 1252:
        # Hoàng Diệu -> nước đã rút sạch (POS)
        c_trips = [([6, 7], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1253:
        # Nguyễn Hữu Cảnh -> hết ngập hoàn toàn (POS)
        c_trips = [([6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1254:
        # Đường Quốc lộ 13 -> khô ráo (POS)
        c_trips = [([0, 1, 2, 3], [9, 10], 'POS')]
    elif rec_num == 1255:
        # Trần Hưng Đạo -> nước rút sạch (POS)
        c_trips = [([3, 4, 5], [8, 9, 10], 'POS')]
    elif rec_num == 1256:
        # Dương Văn Cam -> đi lại bình thường (POS)
        c_trips = [([4, 5, 6], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1257:
        # Đinh Bộ Lĩnh -> đã khô ráo (POS)
        c_trips = [([3, 4, 5], [10, 11, 12], 'POS')]
    elif rec_num == 1258:
        # Đường Quốc Hương -> nước rút rất nhanh (POS)
        c_trips = [([0, 1, 2], [6, 7, 8, 9], 'POS')]
    elif rec_num == 1259:
        # đường Phan Huy Ích -> khô ráo hoàn toàn (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1260:
        # đường Đặng Thị Rành -> thông thoáng (POS)
        c_trips = [([1, 2, 3, 4], [12, 13], 'POS')]

    # --- R1261 to R1270 ---
    elif rec_num == 1261:
        # Lê Đức Thọ -> khô queo (POS)
        c_trips = [([9, 10, 11], [12, 13], 'POS')]
    elif rec_num == 1262:
        # Nguyễn Hữu Cảnh -> khô queo (POS), đi lại dễ dàng (POS)
        c_trips = [
            ([3, 4, 5], [10, 11], 'POS'),
            ([3, 4, 5], [15, 16, 17, 18], 'POS')
        ]
    elif rec_num == 1263:
        # Lê Văn Việt -> thông thoáng trở lại (POS)
        c_trips = [([3, 4, 5], [6, 7, 8, 9], 'POS')]
    elif rec_num == 1264:
        # Lương Định Của -> thông thoáng (POS)
        c_trips = [([3, 4, 5], [8, 9], 'POS')]
    elif rec_num == 1265:
        # đường Nguyễn Văn Hưởng -> nước rút nhanh chóng (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1266:
        # Đường Lê Văn Lương -> nước rút rất nhanh (POS)
        c_trips = [([0, 1, 2, 3], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1267:
        # Nguyễn Văn Khối -> thông suốt (POS)
        c_trips = [([6, 7, 8], [9, 10], 'POS')]
    elif rec_num == 1268:
        # Bến Phú Định -> khô queo (POS)
        c_trips = [([9, 10, 11], [12, 13], 'POS')]
    elif rec_num == 1269:
        # Phan Huy Ích -> hết ngập (POS)
        c_trips = [([3, 4, 5], [8, 9], 'POS')]
    elif rec_num == 1270:
        # Đinh Bộ Lĩnh -> hết ngập hẳn (POS)
        c_trips = [([3, 4, 5], [6, 7, 8], 'POS')]

    # --- R1271 to R1280 ---
    elif rec_num == 1271:
        # Đoàn Văn Bơ -> nước đã rút sạch (POS)
        c_trips = [([6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1272:
        # Trần Xuân Soạn -> thông xe (POS), đi lại dễ dàng (POS)
        c_trips = [
            ([3, 4, 5], [10, 11], 'POS'),
            ([3, 4, 5], [15, 16, 17, 18], 'POS')
        ]
    elif rec_num == 1273:
        # Đường Hồ Học Lãm -> thông thoáng trở lại (POS)
        c_trips = [([0, 1, 2, 3], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1274:
        # Trần Xuân Soạn -> nước đã rút hoàn toàn (POS)
        c_trips = [([3, 4, 5], [6, 7, 8, 9, 10], 'POS')]
    elif rec_num == 1275:
        # đường Nguyễn Xí -> nước đã rút hết (POS)
        c_trips = [([6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1276:
        # đường Hoàng Diệu -> khô ráo (POS)
        c_trips = [([1, 2, 3], [6, 7], 'POS')]
    elif rec_num == 1277:
        # Lê Đức Thọ -> thông thoáng (POS)
        c_trips = [([3, 4, 5], [8, 9], 'POS')]
    elif rec_num == 1278:
        # An Dương Vương -> không bị ngập (POS)
        c_trips = [([3, 4, 5], [10, 11, 12], 'POS')]
    elif rec_num == 1279:
        # đường Phạm Văn Đồng -> khô ráo sạch sẽ (POS)
        c_trips = [([1, 2, 3, 4], [10, 11, 12, 13], 'POS')]
    elif rec_num == 1280:
        # Nguyễn Văn Khối -> thông thoáng (POS)
        c_trips = [([3, 4, 5], [7, 8], 'POS')]

    # --- R1281 to R1290 ---
    elif rec_num == 1281:
        # đường Hoàng Diệu -> thông thoáng (POS)
        c_trips = [([6, 7, 8], [9, 10], 'POS')]
    elif rec_num == 1282:
        # An Dương Vương -> khô ráo (POS)
        c_trips = [([4, 5, 6], [8, 9], 'POS')]
    elif rec_num == 1283:
        # Đường Mễ Cốc -> nước đã rút hoàn toàn (POS)
        c_trips = [([0, 1, 2], [6, 7, 8, 9, 10], 'POS')]
    elif rec_num == 1284:
        # Nguyễn Xí -> khô rang (POS)
        c_trips = [([5, 6], [14, 15], 'POS')]
    elif rec_num == 1285:
        # Trần Hưng Đạo -> khô ráo (POS)
        c_trips = [([4, 5, 6], [8, 9], 'POS')]
    elif rec_num == 1286:
        # An Dương Vương -> thông thoáng (POS)
        c_trips = [([4, 5, 6], [8, 9], 'POS')]
    elif rec_num == 1287:
        # Tô Ngọc Vân -> nước đã rút (POS)
        c_trips = [([5, 6, 7], [15, 16, 17], 'POS')]
    elif rec_num == 1288:
        # Quốc Hương -> đã khô ráo (POS)
        c_trips = [([3, 4], [9, 10, 11], 'POS')]
    elif rec_num == 1289:
        # Quốc Hương -> thông thoáng (POS)
        c_trips = [([4, 5], [7, 8], 'POS')]
    elif rec_num == 1290:
        # đường Nguyễn Biểu -> đã khô ráo (POS)
        c_trips = [([6, 7, 8], [9, 10, 11], 'POS')]

    # --- R1291 to R1300 ---
    elif rec_num == 1291:
        # Kinh Dương Vương -> nước rút sạch (POS)
        c_trips = [([3, 4, 5], [8, 9, 10], 'POS')]
    elif rec_num == 1292:
        # đường Trần Xuân Soạn -> khô ráo (POS)
        c_trips = [([1, 2, 3, 4], [7, 8], 'POS')]
    elif rec_num == 1293:
        # Lê Văn Lương -> hết ngập hẳn (POS)
        c_trips = [([5, 6, 7], [15, 16, 17], 'POS')]
    elif rec_num == 1294:
        # Phạm Văn Đồng -> nước rút sạch (POS)
        c_trips = [([3, 4, 5], [10, 11, 12], 'POS')]
    elif rec_num == 1295:
        # Nguyễn Hữu Cảnh -> thông thoáng (POS)
        c_trips = [([6, 7, 8], [11, 12], 'POS')]
    elif rec_num == 1296:
        # đường Lê Văn Lương -> không ngập (POS)
        c_trips = [([1, 2, 3, 4], [7, 8], 'POS')]
    elif rec_num == 1297:
        # Đường Lương Định Của -> thông thoáng trở lại (POS)
        c_trips = [([0, 1, 2, 3], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1298:
        # Phạm Thế Hiển -> hết ngập (POS)
        c_trips = [([4, 5, 6], [8, 9], 'POS')]
    elif rec_num == 1299:
        # đường Dương Văn Cam -> lưu thông bình thường (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1300:
        # Ung Văn Khiêm -> hết ngập (POS)
        c_trips = [([3, 4, 5], [8, 9], 'POS')]

    curated_lines.append(f"{c_text}####{c_trips}")

assert len(curated_lines) == 100, f"Expected 100 lines, got {len(curated_lines)}"

# Read existing lines from phase3.txt
with open('data/validate_label/thuan/phase3.txt', 'r', encoding='utf-8') as f:
    existing_lines = [l.strip() for l in f if l.strip()]

existing_lines = existing_lines[:1200]
assert len(existing_lines) == 1200, f"Expected 1200 existing lines, got {len(existing_lines)}"

total_lines = existing_lines + curated_lines
assert len(total_lines) == 1300, f"Expected 1300 lines, got {len(total_lines)}"

with open('data/validate_label/thuan/phase3.txt', 'w', encoding='utf-8') as f:
    for line in total_lines:
        f.write(line + '\n')

print(f"Successfully updated phase3.txt with batch 13! Total records: {len(total_lines)}")
