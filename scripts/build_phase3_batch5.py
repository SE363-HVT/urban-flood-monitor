import ast, sys, re

sys.stdout.reconfigure(encoding='utf-8')

# Read raw batch 5
with open('scratch_batch5_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

assert len(blocks) == 100, f"Expected 100 blocks, got {len(blocks)}"

curated_lines = []

for idx, b in enumerate(blocks):
    rec_num = 401 + idx
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
    
    # --- R401 to R410 ---
    if rec_num == 401:
        # Satirical meme -> REJECT
        c_trips = []
    elif rec_num == 402:
        # Công viên Làng Hoa -> vẫn ngập nước (NEG)
        c_trips = [([7, 8, 9, 10], [16, 17, 18], 'NEG')]
    elif rec_num == 403:
        # khu dân cư Cityland Park Hills, Phan Văn Trị, Nguyễn Văn Lượng -> ngập nước (NEG)
        c_trips = [
            ([5, 6, 7, 8, 9, 10], [32, 33], 'NEG'),
            ([16, 17, 18], [32, 33], 'NEG'),
            ([20, 21, 22], [32, 33], 'NEG')
        ]
    elif rec_num == 404:
        # đường Nguyễn Văn Khối -> mênh mông nước (NEG)
        c_trips = [([30, 31, 32, 33], [47, 48, 49], 'NEG')]
    elif rec_num == 405:
        # hầm 1 chung cư -> nước ngập hơn 1m (NEG)
        c_trips = [([5, 6, 7, 8], [24, 25, 26, 27], 'NEG')]
    elif rec_num == 406:
        # Gò Vấp -> vẫn ngập sâu (NEG)
        c_trips = [([18, 19], [20, 21, 22], 'NEG')]
    elif rec_num == 407:
        # hầm 1 chung cư -> nước ngập hơn 1m (NEG)
        c_trips = [([5, 6, 7, 8], [24, 25, 26, 27], 'NEG')]
    elif rec_num == 408:
        # KDC Cityland Park Hills -> vẫn ngập 1 - 1 , 5m (NEG)
        c_trips = [([7, 8, 9, 10], [17, 18, 19, 20, 21, 22, 23], 'NEG')]
    elif rec_num == 409:
        # Video ca nhạc Quê Em Miền Nước Lũ -> REJECT
        c_trips = []
    elif rec_num == 410:
        # TP. HCM -> ngập sâu (NEG)
        c_trips = [([15, 16], [17, 18], 'NEG')]
        
    # --- R411 to R420 ---
    elif rec_num == 411:
        # TP HCM -> ngập sâu (NEG)
        c_trips = [([23, 24], [25, 26], 'NEG')]
    elif rec_num == 412:
        # TPHCM -> ngập gần nửa mét (NEG)
        c_trips = [([0], [4, 5, 6, 7], 'NEG')]
    elif rec_num == 413:
        # TP. Hồ Chí Minh -> có nguy cơ ngập (NEU)
        c_trips = [([1, 2, 3, 4], [9, 10, 11, 12], 'NEU')]
    elif rec_num == 414:
        # đường Phan Huy Ích -> ngập (NEG)
        c_trips = [([50, 51, 52, 53], [54], 'NEG')]
    elif rec_num == 415:
        # TP. Hồ Chí Minh -> có nguy cơ ngập (NEU)
        c_trips = [([15, 16, 17, 18], [4, 5, 6, 7], 'NEU')]
    elif rec_num == 416:
        # TP. HCM -> CẢNH BÁO 122 ĐIỂM NGẬP NƯỚC (NEU)
        c_trips = [([14, 15], [5, 6, 7, 8, 9, 10], 'NEU')]
    elif rec_num == 417:
        # Tips / How to use Google Maps -> REJECT
        c_trips = []
    elif rec_num == 418:
        # TP. HCM -> ngập ngang bánh xe (NEG)
        c_trips = [([6, 7], [8, 9, 10, 11], 'NEG')]
    elif rec_num == 419:
        # đường Đinh Bộ Lĩnh, Bạch Đằng -> ngập gần 5 tiếng (NEG)
        c_trips = [
            ([5, 6, 7, 8], [12, 13, 14, 15], 'NEG'),
            ([10, 11], [12, 13, 14, 15], 'NEG')
        ]
    elif rec_num == 420:
        # đường Đinh Bộ Lĩnh, Bạch Đằng -> ngập gần 5 tiếng (NEG)
        c_trips = [
            ([8, 9, 10, 11], [15, 16, 17, 18], 'NEG'),
            ([13, 14], [15, 16, 17, 18], 'NEG')
        ]
        
    # --- R421 to R430 ---
    elif rec_num == 421:
        # TP. HCM -> bị ngập nước (NEG)
        c_trips = [([15, 16], [27, 28, 29], 'NEG')]
    elif rec_num == 422:
        # TP. HCM -> ngập nước (NEG)
        c_trips = [([2, 3], [13, 14], 'NEG')]
    elif rec_num == 423:
        # Sài Gòn -> ngập ghê quá (NEG)
        c_trips = [([8, 9], [22, 23, 24], 'NEG')]
    elif rec_num == 424:
        # TP. Hồ Chí Minh -> xử lý 50 điểm ngập (POS)
        c_trips = [([0, 1, 2, 3], [10, 11, 12, 13, 14], 'POS')]
    elif rec_num == 425:
        # đường Phan Huy Ích, Thảo Điền -> ngập sâu (NEG)
        c_trips = [
            ([8, 9, 10, 11], [15, 16], 'NEG'),
            ([13, 14], [15, 16], 'NEG')
        ]
    elif rec_num == 426:
        # TP. Hồ Chí Minh -> ngập thêm nghiêm trọng (NEG)
        c_trips = [([4, 5, 6, 7], [36, 37, 38, 39], 'NEG')]
    elif rec_num == 427:
        # Đường Lê Quang Đạo, Đường Trần Văn Mười -> NGẬP (NEG)
        c_trips = [
            ([16, 17, 18, 19], [2], 'NEG'),
            ([47, 48, 49, 50], [2], 'NEG')
        ]
    elif rec_num == 428:
        # Phan Huy Ích, Phạm Văn Đồng, Tô Ngọc Vân, Lý Tế Xuyên -> nước dâng cao (NEG)
        c_trips = [
            ([37, 38, 39], [57, 58, 59], 'NEG'),
            ([41, 42, 43], [57, 58, 59], 'NEG'),
            ([45, 46, 47], [57, 58, 59], 'NEG'),
            ([49, 50, 51], [57, 58, 59], 'NEG')
        ]
    elif rec_num == 429:
        # Tìm phòng trọ -> REJECT
        c_trips = []
    elif rec_num == 430:
        # Tìm phòng trọ -> REJECT
        c_trips = []
        
    # --- R431 to R440 ---
    elif rec_num == 431:
        # Bất động sản quảng cáo mua bán nhà -> REJECT
        c_trips = []
    elif rec_num == 432:
        # đường Nguyễn Văn Khối -> vẫn còn ngập sâu (NEG)
        c_trips = [([1, 2, 3, 4], [18, 19, 20, 21], 'NEG')]
    elif rec_num == 433:
        # đường Nguyễn Văn Khối -> nước ngập mênh mông (NEG)
        c_trips = [([6, 7, 8, 9], [13, 14, 15, 16], 'NEG')]
    elif rec_num == 434:
        # đường Nguyễn Văn Khối -> nước ngập mênh mông (NEG)
        c_trips = [([14, 15, 16, 17], [24, 25, 26, 27], 'NEG')]
    elif rec_num == 435:
        # đường Nguyễn Văn Khối -> nước ngập mênh mông (NEG)
        c_trips = [([10, 11, 12, 13], [17, 18, 19, 20], 'NEG')]
    elif rec_num == 436:
        # NGUYỄN VĂN KHỐI -> Ngập (NEG)
        c_trips = [([5, 6, 7], [17], 'NEG')]
    elif rec_num == 437:
        # DJ Remix / Nhạc bài hát -> REJECT
        c_trips = []
    elif rec_num == 438:
        # Gò Vấp -> đã ngập (NEG)
        c_trips = [([0, 1], [2, 3], 'NEG')]
    elif rec_num == 439:
        # Meme caption chỉ có hashtag không vị ngữ -> REJECT
        c_trips = []
    elif rec_num == 440:
        # đường Nguyễn Văn Khối, Lê Văn Thọ -> vẫn ngập sâu (NEG)
        c_trips = [
            ([36, 37, 38, 39], [50, 51, 52], 'NEG'),
            ([41, 42, 43], [50, 51, 52], 'NEG')
        ]
        
    # --- R441 to R450 ---
    elif rec_num == 441:
        # đường Nguyễn Văn Khối -> mênh mông nước (NEG)
        c_trips = [([30, 31, 32, 33], [47, 48, 49], 'NEG')]
    elif rec_num == 442:
        # TP. HCM -> ngập từ chiều qua tới sáng nay (NEG)
        c_trips = [([9, 10], [1, 2, 3, 4, 5, 6, 7], 'NEG')]
    elif rec_num == 443:
        # đường Phạm Văn Chiêu -> ngập nặng (NEG)
        c_trips = [([36, 37, 38, 39], [24, 25], 'NEG')]
    elif rec_num == 444:
        # TPHCM -> Nguy cơ ngập (NEU)
        c_trips = [([2], [24, 25, 26], 'NEU')]
    elif rec_num == 445:
        # KDC Vĩnh Lộc -> nước ngập (NEG)
        c_trips = [([25, 26, 27], [19, 20], 'NEG')]
    elif rec_num == 446:
        # phường Tam Bình -> triển khai ứng dụng tiếp nhận thông tin (POS)
        c_trips = [([15, 16, 17], [23, 24, 25, 26, 27, 28, 29, 30], 'POS')]
    elif rec_num == 447:
        # phường Tam Bình -> chủ động chọn lộ trình an toàn (POS)
        c_trips = [([1, 2, 3], [58, 59, 60, 61, 62, 63, 64], 'POS')]
    elif rec_num == 448:
        # TPHCM -> ngập sâu (NEG)
        c_trips = [([11], [8, 9], 'NEG')]
    elif rec_num == 449:
        # TPHCM -> ngập nặng (NEG)
        c_trips = [([28], [40, 41], 'NEG')]
    elif rec_num == 450:
        # TPHCM -> bì bõm về nhà sau giờ làm (NEG)
        c_trips = [([12], [13, 14, 15, 16, 17, 18, 19], 'NEG')]
        
    # --- R451 to R460 ---
    elif rec_num == 451:
        # TP HCM -> ngập nước xe chết máy (NEG)
        c_trips = [([15, 16], [9, 10, 11, 12, 13], 'NEG')]
    elif rec_num == 452:
        # Nam bộ chung chung không có TPHCM -> REJECT
        c_trips = []
    elif rec_num == 453:
        # Sài Gòn -> lội nước (NEG)
        c_trips = [([10, 11], [5, 6], 'NEG')]
    elif rec_num == 454:
        # TP. HCM -> ngập (NEG)
        c_trips = [([4, 5], [6], 'NEG')]
    elif rec_num == 455:
        # TP. HCM -> ngập sâu (NEG)
        c_trips = [([12, 13], [14, 15], 'NEG')]
    elif rec_num == 456:
        # TP. HCM -> ngập sâu (NEG)
        c_trips = [([14, 15], [16, 17], 'NEG')]
    elif rec_num == 457:
        # TP. Hồ Chí Minh -> ngập sâu 40 - 60 cm (NEU)
        c_trips = [([3, 4, 5, 6], [38, 39, 40, 41, 42, 43], 'NEU')]
    elif rec_num == 458:
        # TP. HCM -> ngập sâu mênh mông (NEG)
        c_trips = [([25, 26], [41, 42, 43, 44], 'NEG')]
    elif rec_num == 459:
        # TP. HCM -> nguy cơ ngập sâu đến 60 cm (NEU)
        c_trips = [([2, 3], [7, 8, 9, 10, 11, 12, 13], 'NEU')]
    elif rec_num == 460:
        # đường Phạm Hữu Lầu -> nước dâng cao tràn vào nhà dân (NEG)
        c_trips = [([25, 26, 27, 28], [33, 34, 35, 36, 37, 38, 39], 'NEG')]
        
    # --- R461 to R470 ---
    elif rec_num == 461:
        # TP. Hồ Chí Minh -> có thể ngập sâu hơn nửa mét (NEU)
        c_trips = [([13, 14, 15, 16], [19, 20, 21, 22, 23, 24, 25], 'NEU')]
    elif rec_num == 462:
        # TPHCM -> triều cường đạt đỉnh (NEU)
        c_trips = [([2], [16, 17, 18, 19], 'NEU')]
    elif rec_num == 463:
        # TPHCM -> Triều cường đạt đỉnh (NEU)
        c_trips = [([7], [0, 1, 2, 3], 'NEU')]
    elif rec_num == 464:
        # sông Sài Gòn -> triều cường tràn bờ (NEG)
        c_trips = [([21, 22, 23], [7, 8, 9, 10], 'NEG')]
    elif rec_num == 465:
        # TPHCM -> kê đồ tránh ngập (NEG)
        c_trips = [([7], [11, 12, 13, 14], 'NEG')]
    elif rec_num == 466:
        # TPHCM -> bị ngập cục bộ (NEG)
        c_trips = [([27], [28, 29, 30, 31], 'NEG')]
    elif rec_num == 467:
        # Dĩ An Bình Dương (tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 468:
        # Sài Gòn -> ngập (NEG)
        c_trips = [([0, 1], [5], 'NEG')]
    elif rec_num == 469:
        # Triết lý quy hoạch thoát nước -> REJECT
        c_trips = []
    elif rec_num == 470:
        # Bài luận xã luận chung chung -> REJECT
        c_trips = []
        
    # --- R471 to R480 ---
    elif rec_num == 471:
        # Huỳnh Tấn Phát, Trần Xuân Soạn -> nguy cơ ngập sâu đến 60 cm (NEU)
        c_trips = [
            ([15, 16, 17], [30, 31, 32, 33, 34, 35, 36], 'NEU'),
            ([19, 20, 21], [30, 31, 32, 33, 34, 35, 36], 'NEU')
        ]
    elif rec_num == 472:
        # đường Trần Xuân Soạn -> ngập (NEG)
        c_trips = [([11, 12, 13, 14], [10], 'NEG')]
    elif rec_num == 473:
        # TP. HCM -> ngập nước (NEG)
        c_trips = [([49, 50], [40, 41], 'NEG')]
    elif rec_num == 474:
        # Chợ Thủ Đức -> thường xuyên ngập sâu (NEG)
        c_trips = [([2, 3, 4], [5, 6, 7, 8], 'NEG')]
    elif rec_num == 475:
        # TP Thủ Đức -> ngập đến nửa căn (NEG)
        c_trips = [([9, 10, 11], [12, 13, 14, 15], 'NEG')]
    elif rec_num == 476:
        # TP HCM -> chống ngập (POS)
        c_trips = [([0, 1], [4, 5], 'POS')]
    elif rec_num == 477:
        # Đường Sinco -> thường xuyên bị ngập nước (NEG)
        c_trips = [([2, 3], [28, 29, 30, 31, 32], 'NEG')]
    elif rec_num == 478:
        # Thanh Đa -> chìm trong biển triều cường lịch sử (NEG)
        c_trips = [([6, 7], [8, 9, 10, 11, 12, 13, 14], 'NEG')]
    elif rec_num == 479:
        # Sài Gòn -> ngập (NEG)
        c_trips = [([0, 1], [5], 'NEG')]
    elif rec_num == 480:
        # Cắt tiền tố Tại TP. Hồ Chí Minh , vì đã có Quận 7 cụ thể
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):]
        # Quận 7 -> ngập cỡ này (NEG)
        c_trips = [([0, 1], [2, 3, 4], 'NEG')]
        
    # --- R481 to R490 ---
    elif rec_num == 481:
        # đường Nguyễn Bình -> Triều cường ngập (NEG)
        c_trips = [([3, 4, 5], [0, 1, 2], 'NEG')]
    elif rec_num == 482:
        # Thanh Đa -> ngập nặng (NEG)
        c_trips = [([0, 1], [4, 5], 'NEG')]
    elif rec_num == 483:
        # TP. HCM -> triều cường đạt đỉnh (NEU)
        c_trips = [([6, 7], [21, 22, 23, 24], 'NEU')]
    elif rec_num == 484:
        # TP. HCM -> cảnh báo ngập (NEU)
        c_trips = [([0, 1], [2, 3, 4], 'NEU')]
    elif rec_num == 485:
        # Bình Dương (tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 486:
        # QL51 Long Bình Tân Đồng Nai (tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 487:
        # đường Trần Xuân Soạn -> Triều cường lên ngập (NEG)
        c_trips = [([4, 5, 6, 7], [0, 1, 2, 3], 'NEG')]
    elif rec_num == 488:
        # Trường THCS Nguyễn Thị Thập -> thi công chống ngập (POS)
        c_trips = [([26, 27, 28, 29, 30], [21, 22, 23, 24], 'POS')]
    elif rec_num == 489:
        # Phạm hùng -> nước ngập khủng lắm (NEG)
        c_trips = [([0, 1], [4, 5, 6, 7], 'NEG')]
    elif rec_num == 490:
        # Trần Xuân Soạn -> rốn ngập (NEG)
        c_trips = [([0, 1, 2], [3, 4], 'NEG')]
        
    # --- R491 to R500 ---
    elif rec_num == 491:
        # Meme than vãn ướt nhem chỉ có hashtag -> REJECT
        c_trips = []
    elif rec_num == 492:
        # TP HCM -> ngập (NEG)
        c_trips = [([10, 11], [6], 'NEG')]
    elif rec_num == 493:
        # Phường Bến Cát Bình Dương (tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 494:
        # TPHCM -> nguy cơ ngập nước (NEU)
        c_trips = [([4], [5, 6, 7, 8], 'NEU')]
    elif rec_num == 495:
        # TP. HCM -> mênh mông nước (NEG)
        c_trips = [([13, 14], [20, 21, 22], 'NEG')]
    elif rec_num == 496:
        # Sài Gòn -> ngập lênh láng nước (NEG)
        c_trips = [([10, 11], [12, 13, 14, 15], 'NEG')]
    elif rec_num == 497:
        # TPHCM -> thường xuyên ngập sâu (NEG)
        c_trips = [([0], [1, 2, 3, 4], 'NEG')]
    elif rec_num == 498:
        # TP. HCM -> lại ngập nặng (NEG)
        c_trips = [([14, 15], [18, 19, 20], 'NEG')]
    elif rec_num == 499:
        # TP. HCM -> ngập nhiều hơn (NEG)
        c_trips = [([22, 23], [39, 40, 41], 'NEG')]
    elif rec_num == 500:
        # sông Sài Gòn -> cảnh báo triều cường (NEU)
        c_trips = [([9, 10, 11], [4, 5, 6, 7], 'NEU')]

    curated_lines.append(f"{c_text}####{c_trips}")

assert len(curated_lines) == 100, f"Expected 100 lines, got {len(curated_lines)}"

# Read existing lines from phase3.txt
out_path = 'data/validate_label/thuan/phase3.txt'
with open(out_path, 'r', encoding='utf-8') as f:
    existing_lines = [l.strip() for l in f if l.strip()]

# Keep the first 400 lines (Batch 1 + 2 + 3 + 4)
batch1_to_4_lines = existing_lines[:400]
final_lines = batch1_to_4_lines + curated_lines

with open(out_path, 'w', encoding='utf-8') as out_f:
    for l in final_lines:
        out_f.write(l + '\n')

print(f"Successfully wrote 400 previous lines + 100 Batch 5 lines. Total lines in {out_path}: {len(final_lines)}")
