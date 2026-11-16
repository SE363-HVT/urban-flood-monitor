import ast, sys, re

sys.stdout.reconfigure(encoding='utf-8')

# Read raw batch 6
with open('scratch_batch6_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

assert len(blocks) == 100, f"Expected 100 blocks, got {len(blocks)}"

curated_lines = []

for idx, b in enumerate(blocks):
    rec_num = 501 + idx
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
    
    # --- R501 to R510 ---
    if rec_num == 501:
        # TP. HCM -> bị ngập nước (NEG)
        c_trips = [([21, 22], [14, 15, 16], 'NEG')]
    elif rec_num == 502:
        # Thủ Dầu Một Bình Dương (tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 503:
        # Thanh Đa -> ngập sâu (NEG), sông Sài Gòn -> tràn qua bờ kè (NEG)
        c_trips = [
            ([17, 18], [28, 29], 'NEG'),
            ([2, 3, 4], [5, 6, 7, 8], 'NEG')
        ]
    elif rec_num == 504:
        # sông Sài Gòn -> ngập sâu (NEG)
        c_trips = [([20, 21, 22], [45, 46], 'NEG')]
    elif rec_num == 505:
        # TP. HCM -> vượt báo động 3 gây ngập nước (NEU)
        c_trips = [([2, 3], [27, 28, 29, 30, 31, 32, 33], 'NEU')]
    elif rec_num == 506:
        # TP. HCM -> có thể đạt đỉnh (NEU)
        c_trips = [([6, 7], [8, 9, 10, 11], 'NEU')]
    elif rec_num == 507:
        # Quận 7 -> biến đường thành sông (NEG)
        c_trips = [([9, 10], [3, 4, 5, 6], 'NEG')]
    elif rec_num == 508:
        # Bình Dương (tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 509:
        # Bình Dương (tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 510:
        # TPHCM -> ngập nặng (NEG)
        c_trips = [([4], [5, 6], 'NEG')]
        
    # --- R511 to R520 ---
    elif rec_num == 511:
        # Thơ / mẹo đối phó mùa mưa -> REJECT
        c_trips = []
    elif rec_num == 512:
        # TPHCM -> ngập nặng (NEG)
        c_trips = [([4], [5, 6], 'NEG')]
    elif rec_num == 513:
        # Gò Vấp, Tân Bình -> chìm trong biển nước (NEG)
        c_trips = [
            ([48, 49], [59, 60, 61, 62], 'NEG'),
            ([53, 54], [59, 60, 61, 62], 'NEG')
        ]
    elif rec_num == 514:
        # 10 bí kíp sinh tồn -> REJECT
        c_trips = []
    elif rec_num == 515:
        # Sài Gòn -> ngập sâu (NEG)
        c_trips = [([22, 23], [24, 25], 'NEG')]
    elif rec_num == 516:
        # TP. HCM -> ngập sâu (NEG)
        c_trips = [([23, 24], [25, 26], 'NEG')]
    elif rec_num == 517:
        # đường Nguyễn Duy Trinh -> bị ngập nước hơn 1 m suốt 2 tiếng (NEG)
        c_trips = [([25, 26, 27, 28], [33, 34, 35, 36, 37, 38, 39, 40, 41], 'NEG')]
    elif rec_num == 518:
        # TPHCM -> ngập sâu (NEG)
        c_trips = [([22], [31, 32], 'NEG')]
    elif rec_num == 519:
        # đường Văn Tiến Dũng, Nguyễn Văn Linh -> ngập sâu (NEG)
        c_trips = [
            ([14, 15, 16, 17], [26, 27], 'NEG'),
            ([19, 20, 21], [26, 27], 'NEG')
        ]
    elif rec_num == 520:
        # Sài Gòn -> ngập trong nước (NEG)
        c_trips = [([6, 7], [14, 15, 16], 'NEG')]
        
    # --- R521 to R530 ---
    elif rec_num == 521:
        # TP. HCM -> MƯA NGẬP (NEG)
        c_trips = [([0, 1], [5, 6], 'NEG')]
    elif rec_num == 522:
        # TPHCM -> ngập nặng (NEG)
        c_trips = [([2], [8, 9], 'NEG')]
    elif rec_num == 523:
        # TPHCM -> ngập sâu (NEG)
        c_trips = [([9], [10, 11], 'NEG')]
    elif rec_num == 524:
        # ĐƯỜNG TRẦN XUÂN SOẠN -> CHỐNG NGẬP (POS)
        c_trips = [([1, 2, 3, 4], [11, 12], 'POS')]
    elif rec_num == 525:
        # đường Trần Xuân Soạn -> mực nước lên tới 20 – 25 cm (NEG)
        c_trips = [([28, 29, 30, 31], [41, 42, 43, 44, 45, 46, 47, 48], 'NEG')]
    elif rec_num == 526:
        # TP. HCM -> lại ngập (NEG)
        c_trips = [([13, 14], [15, 16], 'NEG')]
    elif rec_num == 527:
        # đường Trần Xuân Soạn -> nước ngập (NEG)
        c_trips = [([10, 11, 12, 13], [8, 9], 'NEG')]
    elif rec_num == 528:
        # đường Trần Xuân Soạn -> biển nước (NEG)
        c_trips = [([5, 6, 7, 8], [22, 23], 'NEG')]
    elif rec_num == 529:
        # Trần Xuân Soạn, Huỳnh Tấn Phát, Nguyễn Lương Bằng, Phạm Hữu Lầu, 15B -> bị ngập (NEG)
        c_trips = [
            ([40, 41, 42], [61, 62], 'NEG'),
            ([44, 45, 46], [61, 62], 'NEG'),
            ([48, 49, 50], [61, 62], 'NEG'),
            ([52, 53, 54], [61, 62], 'NEG'),
            ([56], [61, 62], 'NEG')
        ]
    elif rec_num == 530:
        # đường Trần Xuân Soạn -> giải quyết vấn đề ngập nước (POS)
        c_trips = [([9, 10, 11, 12], [14, 15, 16, 17, 18, 19], 'POS')]
        
    # --- R531 to R540 ---
    elif rec_num == 531:
        # đường Trần Xuân Soạn -> thường xuyên chịu cảnh ngập nặng (NEG)
        c_trips = [([18, 19, 20, 21], [30, 31, 32, 33, 34, 35], 'NEG')]
    elif rec_num == 532:
        # Trần Xuân Soạn, Huỳnh Tấn Phát -> ngập do triều cường (NEG)
        c_trips = [
            ([2, 3, 4], [20, 21, 22, 23], 'NEG'),
            ([6, 7, 8], [20, 21, 22, 23], 'NEG')
        ]
    elif rec_num == 533:
        # đường Lê Văn Lương -> ngập sâu (NEG)
        c_trips = [([10, 11, 12, 13], [14, 15], 'NEG')]
    elif rec_num == 534:
        # TP. HCM -> thường xuyên chìm trong nước (NEG)
        c_trips = [([12, 13], [14, 15, 16, 17, 18], 'NEG')]
    elif rec_num == 535:
        # đường Bình Quới -> ngập nặng kéo dài (NEG)
        c_trips = [([33, 34, 35], [55, 56, 57, 58], 'NEG')]
    elif rec_num == 536:
        # TP. HCM -> ĐẠT ĐỈNH TRIỀU CỰC ĐẠI (NEU)
        c_trips = [([0, 1], [2, 3, 4, 5, 6], 'NEU')]
    elif rec_num == 537:
        # TPHCM -> chống ngập (POS)
        c_trips = [([4], [13, 14], 'POS')]
    elif rec_num == 538:
        # Quận 7 -> lội nước về nhà (NEG)
        c_trips = [([7, 8], [10, 11, 12, 13], 'NEG')]
    elif rec_num == 539:
        # HUỲNH TẤN PHÁT -> VỪA NGẬP VỪA KẸT (NEG)
        c_trips = [([1, 2, 3], [12, 13, 14, 15], 'NEG')]
    elif rec_num == 540:
        # Huỳnh Tấn Phát -> nước ngập lai láng nhiều ngày (NEG)
        c_trips = [([13, 14, 15], [2, 3, 4, 5, 6, 7], 'NEG')]
        
    # --- R541 to R550 ---
    elif rec_num == 541:
        # Câu hỏi thăm dò không có sự kiện ngập -> REJECT
        c_trips = []
    elif rec_num == 542:
        # đường Nguyễn Văn Hưởng, Quốc Hương, đường Thảo Điền -> đang ngập dữ (NEG)
        c_trips = [
            ([32, 33, 34, 35], [22, 23, 24], 'NEG'),
            ([37, 38], [22, 23, 24], 'NEG'),
            ([40, 41, 42], [22, 23, 24], 'NEG')
        ]
    elif rec_num == 543:
        # Đường Thảo Điền, Quốc Hương, Nguyễn Văn Hưởng -> ngập do mưa (NEG)
        c_trips = [
            ([29, 30, 31], [21, 22, 23], 'NEG'),
            ([33, 34], [21, 22, 23], 'NEG'),
            ([36, 37, 38], [21, 22, 23], 'NEG')
        ]
    elif rec_num == 544:
        # Quốc Hương, Tống Hữu Định, Thái Ly, Thảo Điền -> ngập nặng (NEG)
        c_trips = [
            ([49, 50], [64, 65], 'NEG'),
            ([52, 53, 54], [64, 65], 'NEG'),
            ([56, 57], [64, 65], 'NEG'),
            ([59, 60], [64, 65], 'NEG')
        ]
    elif rec_num == 545:
        # TP. HCM -> NGẬP SÂU (NEG)
        c_trips = [([0, 1], [11, 12], 'NEG')]
    elif rec_num == 546:
        # TP. HCM -> ngập sâu (NEG)
        c_trips = [([9, 10], [11, 12], 'NEG')]
    elif rec_num == 547:
        # TP Thủ Đức -> hay bị ngập nước (NEG)
        c_trips = [([14, 15, 16], [6, 7, 8, 9], 'NEG')]
    elif rec_num == 548:
        # Nguyễn Văn Quá -> bị ngập tới đầu gối (NEG)
        c_trips = [([18, 19, 20], [34, 35, 36, 37, 38], 'NEG')]
    elif rec_num == 549:
        # Lê Văn Khương -> ngập nhẹ (NEG)
        c_trips = [([3, 4, 5], [6, 7], 'NEG')]
    elif rec_num == 550:
        # TPHCM -> CHẬT VẬT ĐI LÀM (NEG)
        c_trips = [([12], [13, 14, 15, 16], 'NEG')]
        
    # --- R551 to R560 ---
    elif rec_num == 551:
        # TPHCM -> ngập nghiêm trọng (NEG)
        c_trips = [([23], [38, 39, 40], 'NEG')]
    elif rec_num == 552:
        # Cắt tiền tố Tại TP. Hồ Chí Minh , vì trong thân bài đã có TPHCM cụ thể
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):]
        # TPHCM -> ngập sâu (NEG)
        c_trips = [([29], [30, 31], 'NEG')]
    elif rec_num == 553:
        # Giới thiệu ẩm thực / tản văn đường phố -> REJECT
        c_trips = []
    elif rec_num == 554:
        # TP. HCM -> bì bõm lội nước về nhà (NEG)
        c_trips = [([11, 12], [13, 14, 15, 16, 17, 18], 'NEG')]
    elif rec_num == 555:
        # TP. HCM -> ngập nặng (NEG)
        c_trips = [([13, 14], [15, 16], 'NEG')]
    elif rec_num == 556:
        # đường Chu Văn An -> ngâm mình trong dòng nước ngập (NEG)
        c_trips = [([12, 13, 14, 15], [26, 27, 28, 29, 30, 31], 'NEG')]
    elif rec_num == 557:
        # TP Thủ Đức, Bình Thạnh -> ngập sâu (NEG)
        c_trips = [
            ([17, 18, 19], [26, 27], 'NEG'),
            ([21, 22], [26, 27], 'NEG')
        ]
    elif rec_num == 558:
        # Bình Thạnh -> ngập sâu đến thắt lưng (NEG)
        c_trips = [([1, 2], [12, 13, 14, 15, 16], 'NEG')]
    elif rec_num == 559:
        # Cắt tiền tố Tại TP. Hồ Chí Minh , vì đã có BÌNH THẠNH CŨ
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):]
        # BÌNH THẠNH -> NGẬP TỚI 1 MÉT (NEG)
        c_trips = [([0, 1], [7, 8, 9, 10], 'NEG')]
    elif rec_num == 560:
        # TP HCM -> ngập nặng (NEG)
        c_trips = [([4, 5], [6, 7], 'NEG')]
        
    # --- R561 to R570 ---
    elif rec_num == 561:
        # Tô Ngọc Vân, Phạm Văn Đồng, Dương Văn Cam, chợ Thủ Đức -> NGẬP SÂU (NEG)
        c_trips = [
            ([40, 41, 42], [5, 6], 'NEG'),
            ([44, 45, 46], [5, 6], 'NEG'),
            ([48, 49, 50], [5, 6], 'NEG'),
            ([55, 56, 57], [5, 6], 'NEG')
        ]
    elif rec_num == 562:
        # quận Bình Thạnh, TP Thủ Đức -> ngập ngang người (NEG)
        c_trips = [
            ([19, 20, 21], [26, 27, 28], 'NEG'),
            ([23, 24, 25], [26, 27, 28], 'NEG')
        ]
    elif rec_num == 563:
        # Bình Thạnh, Thủ Đức -> ngập nặng (NEG)
        c_trips = [
            ([12, 13], [18, 19], 'NEG'),
            ([15, 16], [18, 19], 'NEG')
        ]
    elif rec_num == 564:
        # quận Bình Thạnh, TP Thủ Đức -> ngập ngang người (NEG)
        c_trips = [
            ([26, 27, 28], [33, 34, 35], 'NEG'),
            ([30, 31, 32], [33, 34, 35], 'NEG')
        ]
    elif rec_num == 565:
        # TP. HCM -> ngập sâu (NEG)
        c_trips = [([34, 35], [36, 37], 'NEG')]
    elif rec_num == 566:
        # đường Chu Văn An -> ngâm mình trong dòng nước ngập (NEG)
        c_trips = [([17, 18, 19, 20], [31, 32, 33, 34, 35, 36], 'NEG')]
    elif rec_num == 567:
        # Đinh Bộ Lĩnh, Chu Văn An -> ngập gần một mét (NEG)
        c_trips = [
            ([55, 56, 57], [7, 8, 9, 10], 'NEG'),
            ([59, 60, 61], [7, 8, 9, 10], 'NEG')
        ]
    elif rec_num == 568:
        # Đường Phạm Văn Đồng -> ngập sâu hơn một mét (NEG)
        c_trips = [([48, 49, 50, 51], [27, 28, 29, 30, 31], 'NEG')]
    elif rec_num == 569:
        # TP. HCM -> NGẬP (NEG)
        c_trips = [([1, 2], [3], 'NEG')]
    elif rec_num == 570:
        # Bài bình luận xã hội chung chung -> REJECT
        c_trips = []
        
    # --- R571 to R580 ---
    elif rec_num == 571:
        # TP. HCM -> bị ngập nước do triều cường (NEU)
        c_trips = [([13, 14], [7, 8, 9, 10, 11, 12], 'NEU')]
    elif rec_num == 572:
        # đường Bùi Văn Ba -> ngập nặng (NEG)
        c_trips = [([6, 7, 8, 9], [13, 14], 'NEG')]
    elif rec_num == 573:
        # Giới thiệu ứng dụng camera -> REJECT
        c_trips = []
    elif rec_num == 574:
        # Quận 7 -> Nước Thủy Triều Lên Ngập (NEG)
        c_trips = [([15, 16], [4, 5, 6, 7, 8], 'NEG')]
    elif rec_num == 575:
        # TP. HỒ CHÍ MINH -> NGUY CƠ NGẬP NẶNG (NEU)
        c_trips = [([0, 1, 2, 3], [4, 5, 6, 7], 'NEU')]
    elif rec_num == 576:
        # TP Thủ Đức -> ngập sâu (NEG)
        c_trips = [([14, 15, 16], [17, 18], 'NEG')]
    elif rec_num == 577:
        # TP THỦ ĐỨC -> NGẬP NẶNG (NEG)
        c_trips = [([0, 1, 2], [3, 4], 'NEG')]
    elif rec_num == 578:
        # TP THỦ ĐỨC -> NGẬP NẶNG (NEG)
        c_trips = [([0, 1, 2], [3, 4], 'NEG')]
    elif rec_num == 579:
        # chợ Thủ Đức -> bị ngập sâu hơn trước (NEG)
        c_trips = [([3, 4, 5], [28, 29, 30, 31, 32], 'NEG')]
    elif rec_num == 580:
        # đường Tô Ngọc Vân -> ngập sâu (NEG)
        c_trips = [([7, 8, 9, 10], [16, 17], 'NEG')]
        
    # --- R581 to R590 ---
    elif rec_num == 581:
        # TP Thủ Đức -> ngập sâu (NEG)
        c_trips = [([2, 3, 4], [9, 10], 'NEG')]
    elif rec_num == 582:
        # chợ Thủ Đức -> ngập lênh láng (NEG)
        c_trips = [([34, 35, 36], [52, 53, 54], 'NEG')]
    elif rec_num == 583:
        # TP Thủ Đức, quận Gò Vấp, quận Tân Bình, Tân Phú -> bị ngập nặng (NEG)
        c_trips = [
            ([34, 35, 36], [51, 52, 53], 'NEG'),
            ([38, 39, 40], [51, 52, 53], 'NEG'),
            ([42, 43, 44], [51, 52, 53], 'NEG'),
            ([46, 47], [51, 52, 53], 'NEG')
        ]
    elif rec_num == 584:
        # đường Võ Văn Ngân -> chống ngập (POS)
        c_trips = [([8, 9, 10, 11], [2, 3], 'POS')]
    elif rec_num == 585:
        # Cắt tiền tố Tại TP. Hồ Chí Minh , vì đã có THỦ ĐỨC cụ thể
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):]
        # THỦ ĐỨC -> NGẬP NƯỚC (NEG)
        c_trips = [([0, 1], [9, 10], 'NEG')]
    elif rec_num == 586:
        # chợ Thủ Đức -> ngập lênh láng (NEG)
        c_trips = [([45, 46, 47], [58, 59, 60], 'NEG')]
    elif rec_num == 587:
        # quận Bình Tân -> vẫn ngập sâu hơn nửa mét (NEG)
        c_trips = [([31, 32, 33], [34, 35, 36, 37, 38, 39], 'NEG')]
    elif rec_num == 588:
        # TPHCM -> ngập nặng (NEG)
        c_trips = [([0], [5, 6], 'NEG')]
    elif rec_num == 589:
        # TP HCM -> Ngập lút xe máy (NEG)
        c_trips = [([10, 11], [2, 3, 4, 5], 'NEG')]
    elif rec_num == 590:
        # Sài Gòn -> ngập lụt tới mọi ngóc ngách (NEG)
        c_trips = [([0, 1], [6, 7, 8, 9, 10, 11], 'NEG')]
        
    # --- R591 to R600 ---
    elif rec_num == 591:
        # Quốc lộ 50 -> nước ngập lút (NEG)
        c_trips = [([0, 1, 2], [10, 11, 12], 'NEG')]
    elif rec_num == 592:
        # đường Tô Ngọc Vân -> ngập sâu (NEG)
        c_trips = [([12, 13, 14, 15], [21, 22], 'NEG')]
    elif rec_num == 593:
        # Nam Bộ / sông Cửu Long (tỉnh ngoài / vùng rộng) -> REJECT
        c_trips = []
    elif rec_num == 594:
        # Thủ Thiêm, hầm Sông Sài Gòn -> Nước lên ngập (NEG)
        c_trips = [
            ([4, 5], [0, 1, 2], 'NEG'),
            ([8, 9, 10, 11], [0, 1, 2], 'NEG')
        ]
    elif rec_num == 595:
        # TPHCM -> ngập nặng (NEG)
        c_trips = [([41], [49, 50], 'NEG')]
    elif rec_num == 596:
        # SÔNG SÀI GÒN -> NGUY CƠ NGẬP (NEU)
        c_trips = [([16, 17, 18], [11, 12, 13], 'NEU')]
    elif rec_num == 597:
        # sông Sài Gòn -> cảnh báo ngập (NEU)
        c_trips = [([16, 17, 18], [10, 11, 12], 'NEU')]
    elif rec_num == 598:
        # TP HCM -> nguy cơ sẽ xảy ra ngập úng (NEU)
        c_trips = [([0, 1], [7, 8, 9, 10, 11, 12], 'NEU')]
    elif rec_num == 599:
        # TPHCM -> nguy cơ ngập nước rất cao (NEU)
        c_trips = [([24], [31, 32, 33, 34, 35], 'NEU')]
    elif rec_num == 600:
        # Bến Cát - Bàu Bàng Bình Dương (tỉnh ngoài) -> REJECT
        c_trips = []

    curated_lines.append(f"{c_text}####{c_trips}")

assert len(curated_lines) == 100, f"Expected 100 lines, got {len(curated_lines)}"

# Read existing lines from phase3.txt
out_path = 'data/validate_label/thuan/phase3.txt'
with open(out_path, 'r', encoding='utf-8') as f:
    existing_lines = [l.strip() for l in f if l.strip()]

# Keep the first 500 lines (Batch 1 to 5)
batch1_to_5_lines = existing_lines[:500]
final_lines = batch1_to_5_lines + curated_lines

with open(out_path, 'w', encoding='utf-8') as out_f:
    for l in final_lines:
        out_f.write(l + '\n')

print(f"Successfully wrote 500 previous lines + 100 Batch 6 lines. Total lines in {out_path}: {len(final_lines)}")
