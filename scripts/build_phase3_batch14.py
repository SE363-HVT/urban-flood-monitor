import ast, sys, re

sys.stdout.reconfigure(encoding='utf-8')

# Read raw batch 14
with open('scratch_batch14_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

assert len(blocks) == 100, f"Expected 100 blocks, got {len(blocks)}"

curated_lines = []

for idx, b in enumerate(blocks):
    rec_num = 1301 + idx
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
    
    # --- R1301 to R1310 ---
    if rec_num == 1301:
        # Đường Lê Văn Việt -> nước đã rút hoàn toàn (POS)
        c_trips = [([0, 1, 2, 3], [7, 8, 9, 10, 11], 'POS')]
    elif rec_num == 1302:
        # Thảo Điền -> thông thoáng (POS)
        c_trips = [([6, 7], [10, 11], 'POS')]
    elif rec_num == 1303:
        # đường Kinh Dương Vương -> không còn ngập nữa (POS)
        c_trips = [([1, 2, 3, 4], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1304:
        # đường Đặng Thị Rành -> lưu thông thuận lợi (POS)
        c_trips = [([1, 2, 3, 4], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1305:
        # đường Calmette -> nước rút sạch (POS)
        c_trips = [([1, 2, 3], [5, 6, 7], 'POS')]
    elif rec_num == 1306:
        # Trần Hưng Đạo -> nước đã rút (POS)
        c_trips = [([4, 5, 6], [8, 9, 10], 'POS')]
    elif rec_num == 1307:
        # Kinh Dương Vương -> hết ngập (POS)
        c_trips = [([4, 5, 6], [8, 9], 'POS')]
    elif rec_num == 1308:
        # Quốc Hương -> không bị ngập (POS), đi lại dễ dàng (POS)
        c_trips = [
            ([3, 4], [9, 10, 11], 'POS'),
            ([3, 4], [15, 16, 17, 18], 'POS')
        ]
    elif rec_num == 1309:
        # Đường An Dương Vương -> lưu thông bình thường (POS)
        c_trips = [([0, 1, 2, 3], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1310:
        # đường Nguyễn Văn Khối -> nước rút nhanh chóng (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]

    # --- R1311 to R1320 ---
    elif rec_num == 1311:
        # đường An Dương Vương -> nước đã rút hết (POS)
        c_trips = [([6, 7, 8, 9], [10, 11, 12, 13], 'POS')]
    elif rec_num == 1312:
        # Đào Trí -> nước đã rút hoàn toàn (POS)
        c_trips = [([3, 4], [5, 6, 7, 8, 9], 'POS')]
    elif rec_num == 1313:
        # Đoàn Văn Bơ -> nước đã rút (POS)
        c_trips = [([5, 6, 7], [15, 16, 17], 'POS')]
    elif rec_num == 1314:
        # đường Bạch Đằng -> thông thoáng (POS)
        c_trips = [([1, 2, 3], [11, 12], 'POS')]
    elif rec_num == 1315:
        # đường Trần Hưng Đạo -> khô ráo sạch sẽ (POS)
        c_trips = [([1, 2, 3, 4], [10, 11, 12, 13], 'POS')]
    elif rec_num == 1316:
        # Võ Văn Ngân -> không bị ngập (POS), đi lại dễ dàng (POS)
        c_trips = [
            ([3, 4, 5], [10, 11, 12], 'POS'),
            ([3, 4, 5], [16, 17, 18, 19], 'POS')
        ]
    elif rec_num == 1317:
        # Đặng Thị Rành -> nước đã rút (POS)
        c_trips = [([9, 10, 11], [12, 13, 14], 'POS')]
    elif rec_num == 1318:
        # Đường Đào Trí -> nước đã rút hoàn toàn (POS)
        c_trips = [([0, 1, 2], [6, 7, 8, 9, 10], 'POS')]
    elif rec_num == 1319:
        # Dương Văn Cam -> nước đã rút hoàn toàn (POS)
        c_trips = [([3, 4, 5], [6, 7, 8, 9, 10], 'POS')]
    elif rec_num == 1320:
        # Lê Văn Việt -> thông xe (POS), đi lại dễ dàng (POS)
        c_trips = [
            ([3, 4, 5], [10, 11], 'POS'),
            ([3, 4, 5], [15, 16, 17, 18], 'POS')
        ]

    # --- R1321 to R1330 ---
    elif rec_num == 1321:
        # Đường Cây Trâm -> thông thoáng trở lại (POS)
        c_trips = [([0, 1, 2], [6, 7, 8, 9], 'POS')]
    elif rec_num == 1322:
        # Calmette -> thông thoáng (POS)
        c_trips = [([5], [9, 10], 'POS')]
    elif rec_num == 1323:
        # Phan Huy Ích -> khô ráo (POS)
        c_trips = [([4, 5, 6], [8, 9], 'POS')]
    elif rec_num == 1324:
        # Nguyễn Văn Hưởng -> khô ráo (POS)
        c_trips = [([3, 4, 5], [8, 9], 'POS')]
    elif rec_num == 1325:
        # Ung Văn Khiêm -> nước đã rút (POS)
        c_trips = [([4, 5, 6], [8, 9, 10], 'POS')]
    elif rec_num == 1326:
        # Nguyễn Biểu -> đi lại bình thường (POS)
        c_trips = [([4, 5], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1327:
        # đường Đào Trí -> khô ráo (POS)
        c_trips = [([1, 2, 3], [6, 7], 'POS')]
    elif rec_num == 1328:
        # đường Lê Văn Việt -> lưu thông thuận lợi (POS)
        c_trips = [([1, 2, 3, 4], [7, 8, 9, 10], 'POS')]
    elif rec_num == 1329:
        # Bình Quới -> không bị ngập (POS)
        c_trips = [([3, 4], [9, 10, 11], 'POS')]
    elif rec_num == 1330:
        # Nguyễn Văn Khối -> nước đã rút (POS)
        c_trips = [([4, 5, 6], [8, 9, 10], 'POS')]

    # --- R1331 to R1340 ---
    elif rec_num == 1331:
        # Ung Văn Khiêm -> hết ngập hẳn (POS)
        c_trips = [([3, 4, 5], [6, 7, 8], 'POS')]
    elif rec_num == 1332:
        # đường Bến Phú Định -> khô ráo hoàn toàn (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1333:
        # Kinh Dương Vương -> hết ngập hẳn (POS)
        c_trips = [([9, 10, 11], [12, 13, 14], 'POS')]
    elif rec_num == 1334:
        # Nguyễn Duy -> nước đã rút sạch (POS)
        c_trips = [([3, 4], [5, 6, 7, 8], 'POS')]
    elif rec_num == 1335:
        # Đường Cây Trâm -> nước rút rất nhanh (POS)
        c_trips = [([0, 1, 2], [6, 7, 8, 9], 'POS')]
    elif rec_num == 1336:
        # Quốc lộ 13 -> hết ngập hoàn toàn (POS)
        c_trips = [([6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1337:
        # Đường Bạch Đằng -> nước rút rất nhanh (POS)
        c_trips = [([0, 1, 2], [6, 7, 8, 9], 'POS')]
    elif rec_num == 1338:
        # đường Nguyễn Biểu -> không còn ngập nữa (POS)
        c_trips = [([1, 2, 3], [6, 7, 8, 9], 'POS')]
    elif rec_num == 1339:
        # đường Phan Huy Ích -> khô ráo (POS)
        c_trips = [([1, 2, 3, 4], [7, 8], 'POS')]
    elif rec_num == 1340:
        # Mễ Cốc -> nước rút sạch (POS)
        c_trips = [([3, 4], [7, 8, 9], 'POS')]

    # --- R1341 to R1350 ---
    elif rec_num == 1341:
        # Lương Định Của -> thông xe (POS)
        c_trips = [([5, 6, 7], [15, 16], 'POS')]
    elif rec_num == 1342:
        # Hoàng Diệu -> khô queo (POS), đi lại dễ dàng (POS)
        c_trips = [
            ([3, 4], [9, 10], 'POS'),
            ([3, 4], [14, 15, 16, 17], 'POS')
        ]
    elif rec_num == 1343:
        # đường Quốc Hương -> đã khô ráo (POS)
        c_trips = [([6, 7, 8], [9, 10, 11], 'POS')]
    elif rec_num == 1344:
        # đường Tô Ngọc Vân -> ráo hoảnh (POS)
        c_trips = [([6, 7, 8, 9], [10, 11], 'POS')]
    elif rec_num == 1345:
        # An Dương Vương -> hết ngập (POS)
        c_trips = [([4, 5, 6], [8, 9], 'POS')]
    elif rec_num == 1346:
        # đường Nguyễn Biểu -> thông thoáng (POS)
        c_trips = [([6, 7, 8], [9, 10], 'POS')]
    elif rec_num == 1347:
        # Võ Văn Ngân -> khô rang (POS)
        c_trips = [([5, 6, 7], [15, 16], 'POS')]
    elif rec_num == 1348:
        # Phạm Văn Đồng -> không bị ngập (POS)
        c_trips = [([3, 4, 5], [10, 11, 12], 'POS')]
    elif rec_num == 1349:
        # Đỗ Xuân Hợp -> hết ngập (POS)
        c_trips = [([4, 5, 6], [8, 9], 'POS')]
    elif rec_num == 1350:
        # Đường Bến Phú Định -> lưu thông bình thường (POS)
        c_trips = [([0, 1, 2, 3], [7, 8, 9, 10], 'POS')]

    # --- R1351 to R1360 ---
    elif rec_num == 1351:
        # đường Trần Hưng Đạo -> không ngập (POS)
        c_trips = [([1, 2, 3, 4], [7, 8], 'POS')]
    elif rec_num == 1352:
        # Nguyễn Biểu -> hết ngập hẳn (POS)
        c_trips = [([9, 10], [11, 12, 13], 'POS')]
    elif rec_num == 1353:
        # Dương Văn Cam -> khô queo (POS)
        c_trips = [([9, 10, 11], [12, 13], 'POS')]
    elif rec_num == 1354:
        # Hoàng Diệu -> hết ngập hoàn toàn (POS)
        c_trips = [([6, 7], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1355:
        # Nguyễn Biểu -> khô ráo (POS)
        c_trips = [([6, 7], [8, 9], 'POS')]
    elif rec_num == 1356:
        # Trần Hưng Đạo -> nước đã rút (POS)
        c_trips = [([9, 10, 11], [12, 13, 14], 'POS')]
    elif rec_num == 1357:
        # đường Dương Văn Cam -> không còn ngập nước (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1358:
        # Hồ Học Lãm -> thông suốt (POS)
        c_trips = [([6, 7, 8], [9, 10], 'POS')]
    elif rec_num == 1359:
        # Nguyễn Hữu Cảnh -> đi lại bình thường (POS)
        c_trips = [([4, 5, 6], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1360:
        # Nguyễn Duy -> đã khô ráo (POS)
        c_trips = [([3, 4], [9, 10, 11], 'POS')]

    # --- R1361 to R1370 ---
    elif rec_num == 1361:
        # đường Đỗ Xuân Hợp -> khô ráo sạch sẽ (POS)
        c_trips = [([1, 2, 3, 4], [10, 11, 12, 13], 'POS')]
    elif rec_num == 1362:
        # đường Nguyễn Biểu -> lưu thông bình thường (POS)
        c_trips = [([5, 6, 7], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1363:
        # Calmette -> khô ráo sạch sẽ (POS)
        c_trips = [([7], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1364:
        # Lê Văn Lương -> thông thoáng (POS)
        c_trips = [([6, 7, 8], [11, 12], 'POS')]
    elif rec_num == 1365:
        # Cây Trâm -> đã khô ráo (POS)
        c_trips = [([5, 6], [14, 15, 16], 'POS')]
    elif rec_num == 1366:
        # đường Quốc Hương -> nước đã rút sạch sẽ (POS)
        c_trips = [([1, 2, 3], [9, 10, 11, 12, 13], 'POS')]
    elif rec_num == 1367:
        # đường Cây Trâm -> nước rút hết (POS)
        c_trips = [([1, 2, 3], [9, 10, 11], 'POS')]
    elif rec_num == 1368:
        # Bạch Đằng -> thông thoáng (POS)
        c_trips = [([6, 7], [10, 11], 'POS')]
    elif rec_num == 1369:
        # Đào Trí -> không bị ngập (POS)
        c_trips = [([3, 4], [9, 10, 11], 'POS')]
    elif rec_num == 1370:
        # đường Phạm Thế Hiển -> lưu thông thuận lợi (POS)
        c_trips = [([1, 2, 3, 4], [7, 8, 9, 10], 'POS')]

    # --- R1371 to R1380 ---
    elif rec_num == 1371:
        # đường Đinh Bộ Lĩnh -> nước rút sạch (POS)
        c_trips = [([1, 2, 3, 4], [7, 8, 9], 'POS')]
    elif rec_num == 1372:
        # đường Đoàn Văn Bơ -> không ngập (POS)
        c_trips = [([1, 2, 3, 4], [7, 8], 'POS')]
    elif rec_num == 1373:
        # đường Phạm Thế Hiển -> thông thoáng (POS)
        c_trips = [([1, 2, 3, 4], [12, 13], 'POS')]
    elif rec_num == 1374:
        # đường Thảo Điền -> thông thoáng (POS)
        c_trips = [([1, 2, 3], [11, 12], 'POS')]
    elif rec_num == 1375:
        # đường Bình Quới -> khô ráo hoàn toàn (POS)
        c_trips = [([5, 6, 7], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1376:
        # Bình Quới -> nước đã rút sạch (POS)
        c_trips = [([3, 4], [5, 6, 7, 8], 'POS')]
    elif rec_num == 1377:
        # Hồ Học Lãm -> nước đã rút (POS)
        c_trips = [([4, 5, 6], [8, 9, 10], 'POS')]
    elif rec_num == 1378:
        # Calmette -> khô ráo (POS)
        c_trips = [([6], [7, 8], 'POS')]
    elif rec_num == 1379:
        # Nguyễn Biểu -> khô ráo (POS)
        c_trips = [([3, 4], [7, 8], 'POS')]
    elif rec_num == 1380:
        # đường An Dương Vương -> không còn ngập nước (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]

    # --- R1381 to R1390 ---
    elif rec_num == 1381:
        # đường Bạch Đằng -> nước đã rút hết (POS)
        c_trips = [([6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1382:
        # Nguyễn Hữu Cảnh -> nước đã rút (POS)
        c_trips = [([9, 10, 11], [12, 13, 14], 'POS')]
    elif rec_num == 1383:
        # đường Trần Xuân Soạn -> nước đã rút (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11], 'POS')]
    elif rec_num == 1384:
        # đường Nguyễn Văn Khối -> khô ráo hoàn toàn (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]
    elif rec_num == 1385:
        # Nguyễn Duy -> thông thoáng trở lại (POS)
        c_trips = [([3, 4], [5, 6, 7, 8], 'POS')]
    elif rec_num == 1386:
        # đường Nguyễn Hữu Cảnh -> nước đã rút (POS)
        c_trips = [([5, 6, 7, 8], [9, 10, 11], 'POS')]
    elif rec_num == 1387:
        # Cây Trâm -> nước đã rút (POS)
        c_trips = [([5, 6], [14, 15, 16], 'POS')]
    elif rec_num == 1388:
        # Đoàn Văn Bơ -> hết ngập (POS)
        c_trips = [([3, 4, 5], [8, 9], 'POS')]
    elif rec_num == 1389:
        # đường Nguyễn Xí -> lưu thông thuận lợi (POS)
        c_trips = [([1, 2, 3], [6, 7, 8, 9], 'POS')]
    elif rec_num == 1390:
        # Đường Đào Trí -> lưu thông bình thường (POS)
        c_trips = [([0, 1, 2], [6, 7, 8, 9], 'POS')]

    # --- R1391 to R1400 ---
    elif rec_num == 1391:
        # đường Trần Hưng Đạo -> khô ráo sạch sẽ (POS)
        c_trips = [([6, 7, 8, 9], [10, 11, 12, 13], 'POS')]
    elif rec_num == 1392:
        # Bạch Đằng -> nước rút sạch (POS), đi lại dễ dàng (POS)
        c_trips = [
            ([3, 4], [9, 10, 11], 'POS'),
            ([3, 4], [14, 15, 16, 17], 'POS')
        ]
    elif rec_num == 1393:
        # Cây Trâm -> nước đã rút sạch (POS)
        c_trips = [([6, 7], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1394:
        # Lê Văn Việt -> nước đã rút (POS)
        c_trips = [([9, 10, 11], [12, 13, 14], 'POS')]
    elif rec_num == 1395:
        # đường Mễ Cốc -> không còn ngập nước (POS)
        c_trips = [([5, 6, 7], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1396:
        # đường Mễ Cốc -> đã khô ráo (POS)
        c_trips = [([6, 7, 8], [9, 10, 11], 'POS')]
    elif rec_num == 1397:
        # Bình Quới -> khô ráo (POS)
        c_trips = [([3, 4], [7, 8], 'POS')]
    elif rec_num == 1398:
        # Phạm Văn Đồng -> khô ráo (POS)
        c_trips = [([3, 4, 5], [7, 8], 'POS')]
    elif rec_num == 1399:
        # đường Bạch Đằng -> không còn ngập nước (POS)
        c_trips = [([5, 6, 7], [8, 9, 10, 11], 'POS')]
    elif rec_num == 1400:
        # Trần Hưng Đạo -> hết ngập hẳn (POS)
        c_trips = [([5, 6, 7], [15, 16, 17], 'POS')]

    curated_lines.append(f"{c_text}####{c_trips}")

assert len(curated_lines) == 100, f"Expected 100 lines, got {len(curated_lines)}"

# Read existing lines from phase3.txt
with open('data/validate_label/thuan/phase3.txt', 'r', encoding='utf-8') as f:
    existing_lines = [l.strip() for l in f if l.strip()]

existing_lines = existing_lines[:1300]
assert len(existing_lines) == 1300, f"Expected 1300 existing lines, got {len(existing_lines)}"

total_lines = existing_lines + curated_lines
assert len(total_lines) == 1400, f"Expected 1400 lines, got {len(total_lines)}"

with open('data/validate_label/thuan/phase3.txt', 'w', encoding='utf-8') as f:
    for line in total_lines:
        f.write(line + '\n')

print(f"Successfully updated phase3.txt with batch 14! Total records: {len(total_lines)}")
