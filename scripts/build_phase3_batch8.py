import ast, sys, re

sys.stdout.reconfigure(encoding='utf-8')

# Read raw batch 8
with open('scratch_batch8_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

assert len(blocks) == 100, f"Expected 100 blocks, got {len(blocks)}"

curated_lines = []

for idx, b in enumerate(blocks):
    rec_num = 701 + idx
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
    
    # --- R701 to R710 ---
    if rec_num == 701:
        # Lê Văn Lương - Tố Hữu (Hà Nội - tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 702:
        # TPHCM -> ngập lút (NEG)
        c_trips = [([11], [12, 13], 'NEG')]
    elif rec_num == 703:
        # đường Nguyễn Xí, Đinh Bộ Lĩnh -> ngập sâu (NEG)
        c_trips = [
            ([41, 42, 43], [22, 23], 'NEG'),
            ([45, 46, 47], [22, 23], 'NEG')
        ]
    elif rec_num == 704:
        # TPHCM -> LẠI NGẬP NHƯ SÔNG (NEG)
        c_trips = [([4], [5, 6, 7, 8], 'NEG')]
    elif rec_num == 705:
        # đường Lê Lai -> ngập nặng (NEG)
        c_trips = [([37, 38, 39], [26, 27], 'NEG')]
    elif rec_num == 706:
        # TPHCM -> ngập úng (NEG)
        c_trips = [([4], [5, 6], 'NEG')]
    elif rec_num == 707:
        # Cắt tiền tố thừa "Tại TP. Hồ Chí Minh , " vì câu đã có TP Dĩ An
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):].strip()
        # TP Dĩ An [14, 15, 16] -> ngập nặng [5, 6] (NEG)
        c_trips = [([14, 15, 16], [5, 6], 'NEG')]
    elif rec_num == 708:
        # quốc lộ 1K -> Ngập mênh mông (NEG)
        c_trips = [([7, 8, 9], [17, 18, 19], 'NEG')]
    elif rec_num == 709:
        # đường Nguyễn Tri Phương -> ngập sâu (NEG)
        c_trips = [([19, 20, 21, 22], [24, 25], 'NEG')]
    elif rec_num == 710:
        # đường Nguyễn Tri Phương -> ngập sâu (NEG)
        c_trips = [([12, 13, 14, 15], [17, 18], 'NEG')]

    # --- R711 to R720 ---
    elif rec_num == 711:
        # Cắt tiền tố thừa "Tại TP. Hồ Chí Minh , " vì câu đã có DĨ AN
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):].strip()
        # DĨ AN [1, 2] -> thất thủ [3, 4] (NEG)
        c_trips = [([1, 2], [3, 4], 'NEG')]
    elif rec_num == 712:
        # Ẩn dụ "ngập hoa bằng lăng tím" -> REJECT
        c_trips = []
    elif rec_num == 713:
        # Dĩ An, TP Thủ Đức -> ngập (NEG)
        c_trips = [
            ([12, 13], [7], 'NEG'),
            ([20, 21, 22], [7], 'NEG')
        ]
    elif rec_num == 714:
        # Ẩn dụ "ngập trong biển lửa" (cháy nổ) -> REJECT
        c_trips = []
    elif rec_num == 715:
        # Vũng Tàu (tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 716:
        # Bác bỏ tin đồn / sóng thần -> REJECT
        c_trips = []
    elif rec_num == 717:
        # Ẩn dụ ăn uống "ngập mặt" -> REJECT
        c_trips = []
    elif rec_num == 718:
        # CHỢ THỦ ĐỨC -> LẠI NGẬP NẶNG (NEG)
        c_trips = [([6, 7, 8], [9, 10, 11], 'NEG')]
    elif rec_num == 719:
        # Tản văn hài hước phân biệt tên đường -> REJECT
        c_trips = []
    elif rec_num == 720:
        # Tản văn hài hước phân biệt tên đường -> REJECT
        c_trips = []

    # --- R721 to R730 ---
    elif rec_num == 721:
        # TPHCM -> ngập sâu (NEG)
        c_trips = [([14], [11, 12], 'NEG')]
    elif rec_num == 722:
        # Ẩn dụ "ngập sắc cờ đỏ" -> REJECT
        c_trips = []
    elif rec_num == 723:
        # hầm chui Bến xe Miền Đông mới -> bị ngập (NEG)
        c_trips = [([11, 12, 13, 14, 15, 16, 17], [18, 19], 'NEG')]
    elif rec_num == 724:
        # phường Bình Lợi Trung -> ngập sâu (NEG)
        c_trips = [([9, 10, 11, 12], [16, 17], 'NEG')]
    elif rec_num == 725:
        # Video chém gió AI chống ngập TikTok -> REJECT
        c_trips = []
    elif rec_num == 726:
        # Quảng cáo bán xe ô tô Mitsubishi -> REJECT
        c_trips = []
    elif rec_num == 727:
        # Quảng cáo cứu hộ xe máy -> REJECT
        c_trips = []
    elif rec_num == 728:
        # đường Nguyễn Văn Khối -> ngập sâu (NEG)
        c_trips = [([9, 10, 11, 12], [14, 15], 'NEG')]
    elif rec_num == 729:
        # Đường Lê Đức Thọ -> ngập nặng (NEG)
        c_trips = [([0, 1, 2, 3], [7, 8], 'NEG')]
    elif rec_num == 730:
        # La Gi cũ (Bình Thuận - tỉnh ngoài) -> REJECT
        c_trips = []

    # --- R731 to R740 ---
    elif rec_num == 731:
        # Sài Gòn -> ngập nước (NEG)
        c_trips = [([0, 1], [2, 3], 'NEG')]
    elif rec_num == 732:
        # Cắt tiền tố thừa "Tại TP. Hồ Chí Minh , " vì câu đã có TP. HCM
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):].strip()
        # TP. HCM [3, 4] -> xóa tận gốc các điểm ngập [14, 15, 16, 17, 18, 19] (POS)
        c_trips = [([3, 4], [14, 15, 16, 17, 18, 19], 'POS')]
    elif rec_num == 733:
        # Đào Sư Tích -> Ngập (NEG)
        c_trips = [([0, 1, 2], [7], 'NEG')]
    elif rec_num == 734:
        # Nguyễn Bình -> Mưa ngập (NEG)
        c_trips = [([2, 3], [0, 1], 'NEG')]
    elif rec_num == 735:
        # Review xe máy mùa mưa ngập -> REJECT
        c_trips = []
    elif rec_num == 736:
        # Bến Phà Phú Định -> Nước Ngập (NEG)
        c_trips = [([4, 5, 6, 7], [0, 1], 'NEG')]
    elif rec_num == 737:
        # Ẩn dụ "ngập hoa và hương thơm" -> REJECT
        c_trips = []
    elif rec_num == 738:
        # chợ Thủ Đức -> cứ mưa là ngập (NEG)
        c_trips = [([4, 5, 6], [7, 8, 9, 10], 'NEG')]
    elif rec_num == 739:
        # Bãi sau Vũng Tàu (tỉnh ngoài) -> REJECT
        c_trips = []
    elif rec_num == 740:
        # Kỳ Văn, Hà Tĩnh (tỉnh ngoài) -> REJECT
        c_trips = []

    # --- R741 to R750 ---
    elif rec_num == 741:
        # TPHCM -> ngập lênh láng (NEG)
        c_trips = [([5], [6, 7, 8], 'NEG')]
    elif rec_num == 742:
        # chợ Thủ Đức -> giải cứu rốn ngập (POS)
        c_trips = [([17, 18, 19], [13, 14, 15, 16], 'POS')]
    elif rec_num == 743:
        # phường Phú Lợi, phường Vĩnh Tân -> ngập nặng (NEG)
        c_trips = [
            ([15, 16, 17], [40, 41], 'NEG'),
            ([19, 20, 21], [40, 41], 'NEG')
        ]
    elif rec_num == 744:
        # TPHCM -> ngập (NEU) (dự báo mưa to gây ngập)
        c_trips = [([11], [16], 'NEU')]
    elif rec_num == 745:
        # TP. HCM -> ngập vì triều cường dâng (NEG)
        c_trips = [([0, 1], [9, 10, 11, 12, 13], 'NEG')]
    elif rec_num == 746:
        # Sài Gòn -> ngập (NEG)
        c_trips = [([16, 17], [19], 'NEG')]
    elif rec_num == 747:
        # ĐƯỜNG LÊ LỢI, BÙI VIỆN -> NGẬP TRONG NƯỚC (NEG)
        c_trips = [
            ([10, 11, 12], [16, 17, 18], 'NEG'),
            ([14, 15], [16, 17, 18], 'NEG')
        ]
    elif rec_num == 748:
        # phường Sài Gòn -> ngập nước (NEG)
        c_trips = [([7, 8, 9], [18, 19], 'NEG')]
    elif rec_num == 749:
        # CẦU BA SON -> NGẬP (NEG), Thảo Điền -> ngập sâu (NEG)
        c_trips = [
            ([5, 6, 7], [3], 'NEG'),
            ([36, 37], [50, 51], 'NEG')
        ]
    elif rec_num == 750:
        # Câu chưa có địa điểm -> Fallback "Tại TPHCM , "
        c_text = "Tại TPHCM , " + c_text
        # TPHCM [1] -> Ngập sâu [4, 5] (NEG)
        c_trips = [([1], [4, 5], 'NEG')]

    # --- R751 to R760 ---
    elif rec_num == 751:
        # phường Tân Khánh -> ngập sâu (NEG)
        c_trips = [([13, 14, 15], [8, 9], 'NEG')]
    elif rec_num == 752:
        # TPHCM -> ngập sâu (NEG)
        c_trips = [([5], [8, 9], 'NEG')]
    elif rec_num == 753:
        # phường Tân Khánh -> chìm trong biển nước (NEG)
        c_trips = [([33, 34, 35], [38, 39, 40, 41], 'NEG')]
    elif rec_num == 754:
        # TPHCM -> bị ngập (NEG)
        c_trips = [([6], [7, 8], 'NEG')]
    elif rec_num == 755:
        # TPHCM -> chật vật di chuyển qua hàng loạt tuyến đường ngập (NEG)
        c_trips = [([2], [4, 5, 6, 7, 8, 9, 10, 11, 12, 13], 'NEG')]
    elif rec_num == 756:
        # Takashimaya -> ngập dữ (NEG)
        c_trips = [([5], [7, 8], 'NEG')]
    elif rec_num == 757:
        # TPHCM -> ngập thường xuyên (NEG)
        c_trips = [([8], [3, 4, 5], 'NEG')]
    elif rec_num == 758:
        # TPHCM -> có nguy cơ ngập (NEU)
        c_trips = [([7], [2, 3, 4, 5], 'NEU')]
    elif rec_num == 759:
        # Người đi đường hỏi thăm ngập nước -> REJECT
        c_trips = []
    elif rec_num == 760:
        # Đường Quốc Hương -> ngập như sông (NEG)
        c_trips = [([16, 17, 18], [24, 25, 26], 'NEG')]

    # --- R761 to R770 ---
    elif rec_num == 761:
        # Đường Quốc Hương -> ngập như sông (NEG)
        c_trips = [([22, 23, 24], [30, 31, 32], 'NEG')]
    elif rec_num == 762:
        # TPHCM -> NGẬP SÂU (NEG)
        c_trips = [([4], [9, 10], 'NEG')]
    elif rec_num == 763:
        # TP. HCM -> nguy cơ ngập úng (NEU)
        c_trips = [([0, 1], [4, 5, 6, 7], 'NEU')]
    elif rec_num == 764:
        # Thảo Điền -> ngập sâu (NEG)
        c_trips = [([3, 4], [5, 6], 'NEG')]
    elif rec_num == 765:
        # đường Quang Trung, Nguyễn Văn Quá -> bị ngập (NEG)
        c_trips = [
            ([4, 5, 6], [11, 12], 'NEG'),
            ([8, 9, 10], [11, 12], 'NEG')
        ]
    elif rec_num == 766:
        # Tổng hợp danh sách các điểm ngập -> REJECT
        c_trips = []
    elif rec_num == 767:
        # TPHCM -> nguy cơ ngập (NEU)
        c_trips = [([6], [17, 18, 19], 'NEU')]
    elif rec_num == 768:
        # phường Linh Xuân -> ngập sâu (NEG)
        c_trips = [([29, 30, 31], [36, 37], 'NEG')]
    elif rec_num == 769:
        # Thành phố Hồ Chí Minh -> bị ngập (NEG)
        c_trips = [([37, 38, 39, 40, 41], [42, 43], 'NEG')]
    elif rec_num == 770:
        # phường Thuận An -> bị ngập (NEG)
        c_trips = [([17, 18, 19], [30, 31], 'NEG')]

    # --- R771 to R780 ---
    elif rec_num == 771:
        # TPHCM -> NGẬP (NEG)
        c_trips = [([9], [3], 'NEG')]
    elif rec_num == 772:
        # Bình Chánh, quận Bình Tân -> ngập cục bộ (NEG)
        c_trips = [
            ([36, 37], [42, 43, 44], 'NEG'),
            ([39, 40, 41], [42, 43, 44], 'NEG')
        ]
    elif rec_num == 773:
        # Tin tức nới lỏng đồng phục học sinh -> REJECT
        c_trips = []
    elif rec_num == 774:
        # Bài viết fan ca sĩ cày view -> REJECT
        c_trips = []
    elif rec_num == 775:
        # TP. HCM -> ngập nước (NEG)
        c_trips = [([4, 5], [10, 11], 'NEG')]
    elif rec_num == 776:
        # Cắt tiền tố thừa "Tại TP. Hồ Chí Minh , " vì câu đã có TP HCM
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):].strip()
        # TP HCM [8, 9] -> NGẬP SÂU [10, 11] (NEG)
        c_trips = [([8, 9], [10, 11], 'NEG')]
    elif rec_num == 777:
        # TP. HCM -> ngập cục bộ (NEU) (cảnh báo)
        c_trips = [([10, 11], [16, 17, 18], 'NEU')]
    elif rec_num == 778:
        # Cắt tiền tố thừa "Tại TP. Hồ Chí Minh , " vì câu đã có TP. HCM
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):].strip()
        # TP. HCM [21, 22] -> nguy cơ ngập lụt [16, 17, 18, 19] (NEU)
        c_trips = [([21, 22], [16, 17, 18, 19], 'NEU')]
    elif rec_num == 779:
        # SÀI GÒN -> DỰ BÁO NGẬP NẶNG (NEU)
        c_trips = [([13, 14], [24, 25, 26, 27], 'NEU')]
    elif rec_num == 780:
        # TPHCM -> nguy cơ ngập cục bộ (NEU)
        c_trips = [([12], [19, 20, 21, 22, 23], 'NEU')]

    # --- R781 to R790 ---
    elif rec_num == 781:
        # TP. Hồ Chí Minh -> nguy cơ ngập úng (NEU)
        c_trips = [([5, 6, 7, 8], [11, 12, 13, 14], 'NEU')]
    elif rec_num == 782:
        # phường Tân Hiệp, Tân Khánh -> bị ngập (NEG)
        c_trips = [
            ([37, 38, 39], [43, 44], 'NEG'),
            ([41, 42], [43, 44], 'NEG')
        ]
    elif rec_num == 783:
        # TPHCM -> ngập nước (NEG)
        c_trips = [([3], [11, 12], 'NEG')]
    elif rec_num == 784:
        # Cò đất / bất động sản -> REJECT
        c_trips = []
    elif rec_num == 785:
        # đường Lê Văn Lương -> chống ngập (POS)
        c_trips = [([7, 8, 9, 10], [31, 32], 'POS')]
    elif rec_num == 786:
        # TP HỒ CHÍ MINH -> NGUY CƠ NGẬP (NEU)
        c_trips = [([11, 12, 13, 14], [7, 8, 9], 'NEU')]
    elif rec_num == 787:
        # Thành phố Hồ Chí Minh -> ngập sâu (NEG)
        c_trips = [([17, 18, 19, 20, 21], [42, 43], 'NEG')]
    elif rec_num == 788:
        # CHỢ THỦ ĐỨC -> CHỮA NGẬP NƯỚC (POS)
        c_trips = [([14, 15, 16], [10, 11, 12], 'POS')]
    elif rec_num == 789:
        # chợ Thủ Đức -> ngập sâu (NEG)
        c_trips = [([19, 20, 21], [22, 23], 'NEG')]
    elif rec_num == 790:
        # Chợ đầu mối thủ đức -> ngập sâu (NEG)
        c_trips = [([6, 7, 8, 9, 10], [11, 12], 'NEG')]

    # --- R791 to R800 ---
    elif rec_num == 791:
        # TPHCM -> THOÁT CẢNH RỐN NGẬP (POS)
        c_trips = [([4], [5, 6, 7, 8], 'POS')]
    elif rec_num == 792:
        # Cắt tiền tố thừa "Tại TP. Hồ Chí Minh , " vì câu đã có TP Hồ Chí Minh
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):].strip()
        # TP Hồ Chí Minh [2, 3, 4, 5] -> ngập lụt [13, 14] (NEG)
        c_trips = [([2, 3, 4, 5], [13, 14], 'NEG')]
    elif rec_num == 793:
        # TPHCM -> ngập đầy nhà (NEG)
        c_trips = [([15], [10, 11, 12], 'NEG')]
    elif rec_num == 794:
        # TPHCM -> ngập đầy nhà (NEG)
        c_trips = [([10], [5, 6, 7], 'NEG')]
    elif rec_num == 795:
        # đường Lê Lợi, Bùi Viện -> ngập trong nước (NEG)
        c_trips = [
            ([10, 11, 12], [16, 17, 18], 'NEG'),
            ([14, 15], [16, 17, 18], 'NEG')
        ]
    elif rec_num == 796:
        # TP. Hồ Chí Minh -> ngập úng cục bộ (NEG)
        c_trips = [([21, 22, 23, 24], [12, 13, 14, 15], 'NEG')]
    elif rec_num == 797:
        # THỦ ĐỨC -> NGẬP (NEG)
        c_trips = [([9, 10], [3], 'NEG')]
    elif rec_num == 798:
        # TP HCM -> Ngập ngang người (NEG)
        c_trips = [([7, 8], [0, 1, 2], 'NEG')]
    elif rec_num == 799:
        # Thảo Điền -> từng ngập , đang ngập và sẽ ngập (NEG)
        c_trips = [([21, 22], [23, 24, 25, 26, 27, 28, 29, 30], 'NEG')]
    elif rec_num == 800:
        # Xin review chọn trường học -> REJECT
        c_trips = []

    curated_lines.append(f"{c_text}####{c_trips}")

assert len(curated_lines) == 100, f"Expected 100 lines, got {len(curated_lines)}"

# Read existing lines from phase3.txt
out_path = 'data/validate_label/thuan/phase3.txt'
with open(out_path, 'r', encoding='utf-8') as f:
    existing_lines = [l.strip() for l in f if l.strip()]

# Keep the first 700 lines (Batch 1 to 7)
batch1_to_7_lines = existing_lines[:700]
final_lines = batch1_to_7_lines + curated_lines

with open(out_path, 'w', encoding='utf-8') as out_f:
    for l in final_lines:
        out_f.write(l + '\n')

print(f"Successfully wrote 700 previous lines + 100 Batch 8 lines. Total lines in {out_path}: {len(final_lines)}")
