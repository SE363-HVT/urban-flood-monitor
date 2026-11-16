import ast, sys, re

sys.stdout.reconfigure(encoding='utf-8')

# Read raw batch 4
with open('scratch_batch4_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

assert len(blocks) == 100, f"Expected 100 blocks, got {len(blocks)}"

curated_lines = []

for idx, b in enumerate(blocks):
    rec_num = 301 + idx
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
    
    # --- R301 to R310 ---
    if rec_num == 301:
        # THÀNH PHỐ HỒ CHÍ MINH -> NGUY CƠ NGẬP (NEU)
        c_trips = [([2, 3, 4, 5, 6], [11, 12, 13], 'NEU')]
    elif rec_num == 302:
        # TPHCM -> hàng loạt điểm ngập (NEG)
        c_trips = [([3], [7, 8, 9, 10], 'NEG')]
    elif rec_num == 303:
        # TPHCM -> nguy cơ ngập sâu (NEU)
        c_trips = [([11], [14, 15, 16, 17], 'NEU')]
    elif rec_num == 304:
        # TP. HCM -> lội nước (NEG)
        c_trips = [([38, 39], [51, 52], 'NEG')]
    elif rec_num == 305:
        # TPHCM -> sắp hết ngập (POS)
        c_trips = [([15], [16, 17, 18], 'POS')]
    elif rec_num == 306:
        # TPHCM -> ngập sâu hơn 1m (NEG)
        c_trips = [([10], [2, 3, 4, 5], 'NEG')]
    elif rec_num == 307:
        # TP. HCM -> ngập nặng (NEG)
        c_trips = [([14, 15], [16, 17], 'NEG')]
    elif rec_num == 308:
        # TPHCM -> nguy cơ ngập nước (NEU)
        c_trips = [([9], [41, 42, 43, 44], 'NEU')]
    elif rec_num == 309:
        # TPHCM -> xử lý ngập úng (POS)
        c_trips = [([4], [33, 34, 35, 36], 'POS')]
    elif rec_num == 310:
        # TP. HCM -> nguy cơ ngập trên diện rộng (NEU)
        c_trips = [([24, 25], [30, 31, 32, 33, 34, 35], 'NEU')]
        
    # --- R311 to R320 ---
    elif rec_num == 311:
        # TPHCM -> đề phòng ngập (NEU)
        c_trips = [([7], [16, 17, 18], 'NEU')]
    elif rec_num == 312:
        # TP HCM -> NGẬP SÂU (NEG)
        c_trips = [([3, 4], [5, 6], 'NEG')]
    elif rec_num == 313:
        # Sài Gòn -> ngập lụt nhất (NEG)
        c_trips = [([7, 8], [4, 5, 6], 'NEG')]
    elif rec_num == 314:
        # TP. HỒ CHÍ MINH -> CÓ THỂ NGẬP SÂU HƠN NỬA MÉT (NEU)
        c_trips = [([5, 6, 7, 8], [9, 10, 11, 12, 13, 14, 15], 'NEU')]
    elif rec_num == 315:
        # Sài Gòn -> càng chống càng ngập (NEG)
        c_trips = [([7, 8], [33, 34, 35, 36], 'NEG')]
    elif rec_num == 316:
        # TP. HCM -> ngập gần lút bánh xe (NEG)
        c_trips = [([9, 10], [11, 12, 13, 14, 15], 'NEG')]
    elif rec_num == 317:
        # Driving tips -> REJECT
        c_trips = []
    elif rec_num == 318:
        # Thành phố Hồ Chí Minh -> bị ngập sâu (NEG)
        c_trips = [([16, 17, 18, 19, 20], [40, 41, 42], 'NEG')]
    elif rec_num == 319:
        # TP. HCM -> nguy cơ ngập sâu đến 60 cm (NEU)
        c_trips = [([2, 3], [7, 8, 9, 10, 11, 12, 13], 'NEU')]
    elif rec_num == 320:
        # TPHCM -> vẫn ngập nặng (NEG)
        c_trips = [([7], [13, 14, 15], 'NEG')]
        
    # --- R321 to R330 ---
    elif rec_num == 321:
        # TP. HCM -> ngập sâu (NEG)
        c_trips = [([4, 5], [10, 11], 'NEG')]
    elif rec_num == 322:
        # TPHCM -> đề phòng ngập (NEU)
        c_trips = [([3], [27, 28, 29], 'NEU')]
    elif rec_num == 323:
        # TPHCM -> ngập sâu (NEG)
        c_trips = [([6], [3, 4], 'NEG')]
    elif rec_num == 324:
        # TPHCM -> bì bõm lội nước (NEG)
        c_trips = [([3], [9, 10, 11, 12], 'NEG')]
    elif rec_num == 325:
        # TPHCM -> có thể gây ngập úng (NEU)
        c_trips = [([31], [41, 42, 43, 44, 45], 'NEU')]
    elif rec_num == 326:
        # TP HCM -> ngập (NEG)
        c_trips = [([10, 11], [9], 'NEG')]
    elif rec_num == 327:
        # TP HCM -> NGẬP SÂU (NEG)
        c_trips = [([24, 25], [26, 27], 'NEG')]
    elif rec_num == 328:
        # TPHCM -> triều cường gây áp lực ngập (NEU)
        c_trips = [([2], [17, 18, 19, 20, 21, 22], 'NEU')]
    elif rec_num == 329:
        # SÔNG SÀI GÒN -> TRIỀU CƯỜNG (NEU)
        c_trips = [([10, 11, 12], [4, 5], 'NEU')]
    elif rec_num == 330:
        # SÔNG SÀI GÒN -> lên nhanh và ở mức cao (NEU)
        c_trips = [([6, 7, 8], [50, 51, 52, 53, 54, 55], 'NEU')]
        
    # --- R331 to R340 ---
    elif rec_num == 331:
        # TP. HCM -> ngập nặng (NEG)
        c_trips = [([3, 4], [15, 16], 'NEG')]
    elif rec_num == 332:
        # TP. HCM -> ngập nặng (NEG)
        c_trips = [([3, 4], [15, 16], 'NEG')]
    elif rec_num == 333:
        # TP. HCM -> ngập (NEG)
        c_trips = [([17, 18], [11], 'NEG')]
    elif rec_num == 334:
        # TP. HCM -> ngập nặng (NEG)
        c_trips = [([13, 14], [15, 16], 'NEG')]
    elif rec_num == 335:
        # Min homestay ad -> REJECT
        c_trips = []
    elif rec_num == 336:
        # TP HCM -> đường ngập (NEG)
        c_trips = [([10, 11], [8, 9], 'NEG')]
    elif rec_num == 337:
        # TP HCM -> đường ngập (NEG)
        c_trips = [([10, 11], [8, 9], 'NEG')]
    elif rec_num == 338:
        # Poem meme -> REJECT
        c_trips = []
    elif rec_num == 339:
        # TP HCM -> đường ngập (NEG)
        c_trips = [([10, 11], [8, 9], 'NEG')]
    elif rec_num == 340:
        # TPHCM -> Mưa ngập (NEG)
        c_trips = [([6], [0, 1], 'NEG')]
        
    # --- R341 to R350 ---
    elif rec_num == 341:
        # TPHCM -> ngập sâu (NEG)
        c_trips = [([5], [6, 7], 'NEG')]
    elif rec_num == 342:
        # TPHCM -> ngập sâu (NEG)
        c_trips = [([7], [2, 3], 'NEG')]
    elif rec_num == 343:
        # TPHCM -> đường ngập sâu (NEG)
        c_trips = [([2], [9, 10, 11], 'NEG')]
    elif rec_num == 344:
        # TPHCM -> ngập sâu (NEG)
        c_trips = [([6], [7, 8], 'NEG')]
    elif rec_num == 345:
        # TPHCM -> đường ngập sâu (NEG)
        c_trips = [([2], [9, 10, 11], 'NEG')]
    elif rec_num == 346:
        # TPHCM -> NGẬP SÂU (NEG), NƯỚC RÚT CHẬM (NEG)
        c_trips = [
            ([6], [7, 8], 'NEG'),
            ([6], [10, 11, 12], 'NEG')
        ]
    elif rec_num == 347:
        # TPHCM -> ngập sâu (NEG)
        c_trips = [([7], [10, 11], 'NEG')]
    elif rec_num == 348:
        # TPHCM -> ngập sâu (NEG)
        c_trips = [([0], [1, 2], 'NEG')]
    elif rec_num == 349:
        # đường Trần Xuân Soạn -> ngập (NEG)
        c_trips = [([6, 7, 8, 9], [5], 'NEG')]
    elif rec_num == 350:
        # đường Trần Xuân Soạn -> ngập (NEG)
        c_trips = [([6, 7, 8, 9], [5], 'NEG')]
        
    # --- R351 to R360 ---
    elif rec_num == 351:
        # đường Trần Xuân Soạn -> ngập (NEG)
        c_trips = [([6, 7, 8, 9], [5], 'NEG')]
    elif rec_num == 352:
        # TP HCM -> ngập sâu (NEG)
        c_trips = [([2, 3], [4, 5], 'NEG')]
    elif rec_num == 353:
        # Sài Gòn -> hễ mưa là ngập (NEG)
        c_trips = [([10, 11], [5, 6, 7, 8], 'NEG')]
    elif rec_num == 354:
        # TP. HCM -> ngập (NEG)
        c_trips = [([17, 18], [11], 'NEG')]
    elif rec_num == 355:
        # TP. Hồ Chí Minh -> có nguy cơ ngập nước (NEU)
        c_trips = [([13, 14, 15, 16], [22, 23, 24, 25, 26], 'NEU')]
    elif rec_num == 356:
        # TP. HCM -> 122 điểm ngập (NEG)
        c_trips = [([12, 13], [2, 3, 4], 'NEG')]
    elif rec_num == 357:
        # TP. HỒ CHÍ MINH -> CÓ NGUY CƠ NGẬP (NEU)
        c_trips = [([16, 17, 18, 19], [5, 6, 7, 8], 'NEU')]
    elif rec_num == 358:
        # TP. HCM -> liên tục ngập sâu (NEG)
        c_trips = [([0, 1], [6, 7, 8, 9], 'NEG')]
    elif rec_num == 359:
        # TP. HCM -> nước rút chậm (NEG)
        c_trips = [([6, 7], [12, 13, 14], 'NEG')]
    elif rec_num == 360:
        # TP. HCM -> đã ngập ngang bánh xe (NEG)
        c_trips = [([9, 10], [11, 12, 13, 14, 15], 'NEG')]
        
    # --- R361 to R370 ---
    elif rec_num == 361:
        # TP. HCM -> ngập sâu (NEG)
        c_trips = [([0, 1], [9, 10], 'NEG')]
    elif rec_num == 362:
        # TP. Thủ Đức -> thường xuyên ngập nặng (NEG)
        c_trips = [([31, 32, 33], [17, 18, 19, 20], 'NEG')]
    elif rec_num == 363:
        # TP. HCM -> mưa ngập (NEG)
        c_trips = [([3, 4], [15, 16], 'NEG')]
    elif rec_num == 364:
        # TP. HCM -> ngâm chân giữa nước ngập (NEG)
        c_trips = [([6, 7], [17, 18, 19, 20, 21], 'NEG')]
    elif rec_num == 365:
        # TP. HCM -> mưa ngập (NEG)
        c_trips = [([0, 1], [3, 4], 'NEG')]
    elif rec_num == 366:
        # Rule 9: Nguyễn Văn Khối, Lê Văn Thọ -> ngập nặng
        c_trips = [
            ([49, 50, 51], [45, 46], 'NEG'),
            ([53, 54, 55], [45, 46], 'NEG')
        ]
    elif rec_num == 367:
        # TP. HCM -> ngập nặng sau mưa lớn (NEG), xóa 50 điểm ngập (POS)
        c_trips = [
            ([2, 3], [4, 5, 6, 7, 8], 'NEG'),
            ([2, 3], [64, 65, 66, 67], 'POS')
        ]
    elif rec_num == 368:
        # TP. Thủ Đức -> ngập sâu (NEG)
        c_trips = [([39, 40, 41], [28, 29], 'NEG')]
    elif rec_num == 369:
        # TP HCM -> mưa diện rộng và ngập nước (NEU)
        c_trips = [([25, 26], [29, 30, 31, 32, 33, 34], 'NEU')]
    elif rec_num == 370:
        # thành phố Thủ Đức -> ngập nặng (NEG)
        c_trips = [([37, 38, 39, 40], [23, 24], 'NEG')]
        
    # --- R371 to R380 ---
    elif rec_num == 371:
        # phường Thủ Đức -> nước ngập do mưa lớn (NEG)
        c_trips = [([29, 30, 31], [19, 20, 21, 22, 23], 'NEG')]
    elif rec_num == 372:
        # đường số 11 -> gây ngập nước (NEG)
        c_trips = [([36, 37, 38], [49, 50, 51], 'NEG')]
    elif rec_num == 373:
        # Rule 9: chợ Thủ Đức, Tô Ngọc Vân -> giải quyết tình trạng ngập (POS)
        c_trips = [
            ([36, 37, 38], [28, 29, 30, 31, 32], 'POS'),
            ([46, 47, 48], [28, 29, 30, 31, 32], 'POS')
        ]
    elif rec_num == 374:
        # POPS TV Dong Thap reup -> REJECT
        c_trips = []
    elif rec_num == 375:
        # Đường Đặng Thùy Trâm -> nâng nền hơn 1m để chống ngập (POS)
        c_trips = [([13, 14, 15, 16], [21, 22, 23, 24, 25, 26, 27], 'POS')]
    elif rec_num == 376:
        # TPHCM -> ngập nước (NEG)
        c_trips = [([15], [12, 13], 'NEG')]
    elif rec_num == 377:
        # Đường Đặng Thùy Trâm -> nâng nền gần 2 mét để chống ngập (POS)
        c_trips = [([14, 15, 16, 17], [23, 24, 25, 26, 27, 28, 29, 30], 'POS')]
    elif rec_num == 378:
        # TPHCM -> triều cường đạt đỉnh (NEU)
        c_trips = [([13], [24, 25, 26, 27], 'NEU')]
    elif rec_num == 379:
        # TPHCM -> đạt đỉnh (NEU)
        c_trips = [([9], [10, 11], 'NEU')]
    elif rec_num == 380:
        # Outside province BRVT -> REJECT
        c_trips = []
        
    # --- R381 to R390 ---
    elif rec_num == 381:
        # TP. Hồ Chí Minh -> có thể ngập sâu hơn nửa mét (NEU)
        c_trips = [([5, 6, 7, 8], [9, 10, 11, 12, 13, 14, 15], 'NEU')]
    elif rec_num == 382:
        # TP. HCM -> triều cường đạt đỉnh (NEU)
        c_trips = [([3, 4], [14, 15, 16, 17], 'NEU')]
    elif rec_num == 383:
        # TP. HCM -> đề phòng ngập (NEU)
        c_trips = [([2, 3], [27, 28, 29], 'NEU')]
    elif rec_num == 384:
        # Cut prefix 'Tại TP. Hồ Chí Minh , '
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):]
        # Text starts: Dự kiến tiếp tục mưa lớn vào chiều nay 08 . 10 ! Khách hàng lưu thông về phía Nhà Bè cũ , quận 7 , 4 , 8 cũ hết sức cẩn trọng , nếu nước ngập cao thì đừng cố di chuyển...
        # Look for Nhà Bè (or quận 7, 4, 8) and nước ngập cao
        toks = c_text.split()
        asp_idx = []
        opi_idx = []
        for i, t in enumerate(toks):
            if t == 'Nhà' and i+1 < len(toks) and toks[i+1] == 'Bè':
                asp_idx = [i, i+1]
            if t == 'nước' and i+2 < len(toks) and toks[i+1] == 'ngập' and toks[i+2] == 'cao':
                opi_idx = [i, i+1, i+2]
        c_trips = [(asp_idx, opi_idx, 'NEG')] if (asp_idx and opi_idx) else []
    elif rec_num == 385:
        # TP HCM -> triều cường đạt đỉnh (NEU)
        c_trips = [([6, 7], [15, 16, 17, 18], 'NEU')]
    elif rec_num == 386:
        # TP. Hồ Chí Minh -> ngập nhanh (NEG)
        c_trips = [([7, 8, 9, 10], [11, 12], 'NEG')]
    elif rec_num == 387:
        # TP. HCM -> Cảnh báo tiếp tục ngập sâu (NEU)
        c_trips = [([2, 3], [34, 35, 36, 37, 38, 39], 'NEU')]
    elif rec_num == 388:
        # Sài Gòn -> cẩn thận các khu vực khi nước Ngập (NEU)
        c_trips = [([1, 2], [3, 4, 5, 6, 7, 8, 9, 10], 'NEU')]
    elif rec_num == 389:
        # TPHCM -> Nguy cơ ngập (NEU)
        c_trips = [([2], [24, 25, 26], 'NEU')]
    elif rec_num == 390:
        # TP. HCM -> ngập nặng (NEG)
        c_trips = [([0, 1], [5, 6], 'NEG')]
        
    # --- R391 to R400 ---
    elif rec_num == 391:
        # TP. HCM -> NGẬP NƯỚC (NEG)
        c_trips = [([10, 11], [5, 6], 'NEG')]
    elif rec_num == 392:
        # TP. HCM -> triều cường được dự báo đạt đỉnh (NEU)
        c_trips = [([0, 1], [29, 30, 31, 32, 33, 34, 35], 'NEU')]
    elif rec_num == 393:
        # TP. Hồ Chí Minh -> ngập sâu (NEG)
        c_trips = [([1, 2, 3, 4], [16, 17], 'NEG')]
    elif rec_num == 394:
        # đường Nguyễn Bình -> ngập khoảng 1 km (NEG)
        c_trips = [([27, 28, 29], [34, 35, 36, 37], 'NEG')]
    elif rec_num == 395:
        # Thành phố Hồ Chí Minh -> bị ngập sâu (NEG)
        c_trips = [([12, 13, 14, 15, 16], [32, 33, 34], 'NEG')]
    elif rec_num == 396:
        # TP. HCM -> CHẬT VẬT LỘI NƯỚC (NEG)
        c_trips = [([3, 4], [10, 11, 12, 13], 'NEG')]
    elif rec_num == 397:
        # TP. Hồ Chí Minh -> ngập (NEG)
        c_trips = [([0, 1, 2, 3], [4], 'NEG')]
    elif rec_num == 398:
        # Thành phố Hồ Chí Minh -> bị ngập sâu (NEG)
        c_trips = [([10, 11, 12, 13, 14], [30, 31, 32], 'NEG')]
    elif rec_num == 399:
        # Outside province Bình Dương, Vũng Tàu -> REJECT
        c_trips = []
    elif rec_num == 400:
        # khu dân cư Cityland Park Hills -> bị ngập hơn 1 mét (NEG)
        c_trips = [([13, 14, 15, 16, 17, 18], [28, 29, 30, 31, 32], 'NEG')]

    curated_lines.append(f"{c_text}####{c_trips}")

assert len(curated_lines) == 100, f"Expected 100 lines, got {len(curated_lines)}"

# Read existing lines from phase3.txt
out_path = 'data/validate_label/thuan/phase3.txt'
with open(out_path, 'r', encoding='utf-8') as f:
    existing_lines = [l.strip() for l in f if l.strip()]

# Keep the first 300 lines (Batch 1 + Batch 2 + Batch 3)
batch1_2_3_lines = existing_lines[:300]
final_lines = batch1_2_3_lines + curated_lines

with open(out_path, 'w', encoding='utf-8') as out_f:
    for l in final_lines:
        out_f.write(l + '\n')

print(f"Successfully wrote 300 previous lines + 100 Batch 4 lines. Total lines in {out_path}: {len(final_lines)}")
