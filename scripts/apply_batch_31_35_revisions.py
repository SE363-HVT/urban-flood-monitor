# -*- coding: utf-8 -*-
from span_helper import make_triplet
import json

batch_31_35_revisions = [
    # REC 3120: TP. Hồ Chí Minh ngập nặng
    (3120, "Tại TP. Hồ Chí Minh , Mưa kéo dài hơn 1 giờ khiến nước thoát không kịp gây ngập nặng",
     [("TP. Hồ Chí Minh", "ngập nặng", "NEG")]),

    # REC 3123: TP. HCM GIẢI PHÁP CHỐNG NGẬP
    (3123, "TP. HCM CHỦ ĐỘNG TRIỂN KHAI NHIỀU PHƯƠNG ÁN , GIẢI PHÁP CHỐNG NGẬP TPHCM và cả khu vực Nam bộ đã bước vào mùa mưa .",
     [("TP. HCM", "GIẢI PHÁP CHỐNG NGẬP", "POS")]),

    # REC 3125: QUẬN 12 HẺM NGẬP QUANH NĂM
    (3125, "Tại TP. Hồ Chí Minh , 🚨 QUẬN 12 : HẺM NGẬP QUANH NĂM DO NƯỚC THẢI CỦA CHUNG CƯ 👇 Nước thải sinh hoạt từ chung cư Thạnh Lộc phía trước hẻm xả thẳng xuống kênh , làm cho nước kênh tràn vào hẻm , có khi tràn vào nhà dân .",
     [("QUẬN 12", "HẺM NGẬP QUANH NĂM", "NEG")]),

    # REC 3137: TP. Hồ Chí Minh đợi nước rút
    (3137, "Tại TP. Hồ Chí Minh , Các xe đã dạt hết lên vỉa hè đứng đợi nước rút .",
     [("TP. Hồ Chí Minh", "đợi nước rút", "POS")]),

    # REC 3147: TP. Hồ Chí Minh chết máy
    (3147, "Tại TP. Hồ Chí Minh , phương tiện lưu thông chết máy , người dân chờ nước rút mới về nhà .",
     [("TP. Hồ Chí Minh", "chết máy", "NEG")]),

    # REC 3151: Thuận An, Thủ Dầu Một, sông SG đề phòng ngập
    (3151, "Tại TP. Hồ Chí Minh , Bà con hạ du Thuận An , Thủ Dầu Một ( Bình Dương cũ ) hay ven sông SG đề phòng ngập ❗",
     [("Thuận An", "đề phòng ngập", "NEU"),
      ("Thủ Dầu Một", "đề phòng ngập", "NEU"),
      ("sông SG", "đề phòng ngập", "NEU")]),

    # REC 3153: TP. Hồ Chí Minh ngập úng diễn ra thường xuyên
    (3153, "Tại TP. Hồ Chí Minh , Tình trạng ngập úng diễn ra thường xuyên , kéo dài nhiều ngày .",
     [("TP. Hồ Chí Minh", "ngập úng diễn ra thường xuyên", "NEG")]),

    # REC 3155: TP. Hồ Chí Minh Nước ngập dâng lên khá cao
    (3155, "Tại TP. Hồ Chí Minh , Nước ngập dâng lên khá cao .",
     [("TP. Hồ Chí Minh", "Nước ngập dâng lên khá cao", "NEG")]),

    # REC 3158: Thuận An, Thủ Dầu Một đề phòng ngập úng
    (3158, "Tại TP. Hồ Chí Minh , Bà con ven kênh , sông SG như Thuận An , Thủ Dầu Một đề phòng ngập úng , chủ động bảo vệ tài sản và con",
     [("Thuận An", "đề phòng ngập úng", "NEU"),
      ("Thủ Dầu Một", "đề phòng ngập úng", "NEU")]),

    # REC 3162: PHƯỜNG PHÚ HÒA ỨNG CỨU NGẬP CỤC BỘ
    (3162, "Tại TP. Hồ Chí Minh , 🌧 🌧 🌧 BAN CHQS PHƯỜNG PHÚ HÒA , TP THỦ DẦU MỘT , BÌNH DƯƠNG ỨNG CỨU NGẬP CỤC BỘ DO TRỜI MƯA BÃO \" 🌧 🌧 🌧 💯 Để chủ động , kịp thời ứng phó với diễn biến phức tạp của thiên tai , bão lũ , thời gian vừa qua Ban CHQS phường Phú Hoà đã ch",
     [("PHƯỜNG PHÚ HÒA", "ỨNG CỨU NGẬP CỤC BỘ", "POS")]),

    # REC 3169: THUẬN AN, THỦ DẦU MỘT, SÔNG SÀI GÒN NGUY CƠ NGẬP
    (3169, "THÔNG BÁO KHẨN : TỪ 7H SÁNG 25 / 11 ĐẾN 7H NGÀY 2 / 12 / 2025 , HỒ DẦU TIẾNG XẢ LŨ – NGƯỜI DÂN KHU VỰC HẠ DU THUẬN AN , THỦ DẦU MỘT VÀ VEN SÔNG SÀI GÒN CẦN CHỦ ĐỘNG ỨNG PHÓ NGUY CƠ NGẬP ⁉ ️",
     [("THUẬN AN", "NGUY CƠ NGẬP", "NEU"),
      ("THỦ DẦU MỘT", "NGUY CƠ NGẬP", "NEU"),
      ("SÔNG SÀI GÒN", "NGUY CƠ NGẬP", "NEU")]),

    # REC 3176: Quốc lộ 13 sẽ ngập
    (3176, "Trạm Thu Phí Suối Giữa ( Quốc lộ 13 ) ngay lúc này , mưa khá lớn , dự là sẽ ngập .",
     [("Quốc lộ 13", "sẽ ngập", "NEU")]),

    # REC 3180: Đường 30 tháng 4 Ngập
    (3180, "Tại TP. Hồ Chí Minh , Ngập ngập & ngập … Đường 30 tháng 4 hôm nay .",
     [("Đường 30 tháng 4", "Ngập", "NEG")]),

    # REC 3193: HỒ TRÀM, XUYÊN MỘC, BRVT NGẬP NẶNG
    (3193, "Tại TP. Hồ Chí Minh , HỒ TRÀM - XUYÊN MỘC - BRVT CŨ NGẬP NẶNG - NƯỚC CHẢY RA BIỂN KO KỊP",
     [("HỒ TRÀM", "NGẬP NẶNG", "NEG"),
      ("XUYÊN MỘC", "NGẬP NẶNG", "NEG"),
      ("BRVT", "NGẬP NẶNG", "NEG")]),

    # REC 3196: phường Mỹ Xuân xử lý tình trạng ngập
    (3196, "Tại TP. Hồ Chí Minh , Sớm xử lý tình trạng ngập tại phường Mỹ Xuân , thị xã Phú Mỹ",
     [("phường Mỹ Xuân", "xử lý tình trạng ngập", "POS")]),

    # REC 3419: TP. Hồ Chí Minh đường sẽ ngập
    (3419, "Tại TP. Hồ Chí Minh , Sau cơn mưa , đường sẽ ngập .",
     [("TP. Hồ Chí Minh", "ngập", "NEG")]),

    # REC 3429: TP. Hồ Chí Minh chết máy hết
    (3429, "Tại TP. Hồ Chí Minh , Xe khác ngta chết máy hết .",
     [("TP. Hồ Chí Minh", "chết máy hết", "NEG")]),

    # REC 3432: phường Bình Trị Đông A xe bị chết máy
    (3432, "Tại TP. Hồ Chí Minh , Chi đoàn Dân Quân phường Bình Trị Đông A đã cùng nhau hỗ trợ dắt phụ các xe bị chết máy .",
     [("phường Bình Trị Đông A", "xe bị chết máy", "NEG")]),

    # REC 3433: Bình Quới hạn chế ngập nước triều cường
    (3433, "Các vị trí xung yếu ở Bình Quới được khắc phục để hạn chế ngập nước triều cường",
     [("Bình Quới", "hạn chế ngập nước triều cường", "POS")]),

    # REC 3445: Bình Quới ngập
    (3445, "Nhật ký ngập Bình Quới . . .",
     [("Bình Quới", "ngập", "NEG")]),

    # REC 3447: TP. Hồ Chí Minh ngập
    (3447, "Tại TP. Hồ Chí Minh , Bữa đó trước nhà ngập xong ngập kế bên , tràn vòng phía sau nhà bếp lên .",
     [("TP. Hồ Chí Minh", "ngập", "NEG")]),

    # REC 3449: TP. Hồ Chí Minh xe chết máy
    (3449, "Tại TP. Hồ Chí Minh , Nhiều xe chết máy phải đẩy bộ , giao thông hỗn loạn .",
     [("TP. Hồ Chí Minh", "xe chết máy", "NEG")]),

    # REC 3465: quận Gò Gấp ngập
    (3465, "HCM phải cõng con qua đường ngập sau trận mưa xối xả chiều 24 / 6 Mưa lớn chiều 24 / 6 làm ngập nhiều tuyến đường ở quận Gò Gấp , TP. HCM .",
     [("quận Gò Gấp", "ngập", "NEG")]),

    # REC 3466: TP. Hồ Chí Minh đường ngập
    (3466, "Tại TP. Hồ Chí Minh , Nhiều người cõng con qua đường ngập .",
     [("TP. Hồ Chí Minh", "đường ngập", "NEG")]),

    # REC 3473: quận 2, quận 9 công trình chống ngập
    (3473, "CHUYÊN GIA HÀ LAN ĐỀ XUẤT GIẢI PHÁP CHỐNG NGẬP ĐỘC ĐÁO CHO TPHCM - - - - - - - - - - - - - - - - - - - - - - - - - - - - Các chuyên gia Hà Lan đề xuất xây dựng hệ thống công trình chống ngập cho quận 2 và quận 9 .",
     [("quận 2", "công trình chống ngập", "POS"),
      ("quận 9", "công trình chống ngập", "POS")]),

    # REC 3477: chợ Thủ Đức chống ngập
    (3477, "TPO - Theo cơ quan chức năng TP. Thủ Đức ( TPHCM ) , để giải quyết bài toán thoát nước , chống ngập cho khu vực “ lòng chảo ” chợ Thủ Đức cần phải thực hiện thêm các dự án trên các tuyến đường khác quanh chợ .",
     [("chợ Thủ Đức", "chống ngập", "POS")]),

    # REC 3489: Sài Gòn mưa ngập đường
    (3489, "Sài Gòn mưa ngập đường thế này , quả là một cơ hội tuyệt vời để OT 🥰",
     [("Sài Gòn", "mưa ngập đường", "NEG")]),

    # REC 3496: đường Trần Xuân Soạn ngăn được lượng nước lớn tràn vào
    (3496, "Người dân sống tại đường Trần Xuân Soạn cho biết nhờ các bao cát này nên chiều hôm nay đã ngăn được lượng nước lớn tràn vào trong .",
     [("đường Trần Xuân Soạn", "ngăn được lượng nước lớn tràn vào", "POS")]),

    # REC 3499: TP. HCM ngập do triều cường
    (3499, "Theo đó , từ đợt triều cường trong thời gian các ngày 20 - 25 . 10 ( từ 29 . 8 - 4 . 9 âm lịch ) , Phòng Hạ tầng kỹ thuật Sở Xây dựng TP. HCM cho biết trên địa bàn TP. HCM xảy ra các đợt ngập do triều cường tại nhiều khu vực .",
     [("TP. HCM", "ngập do triều cường", "NEG")]),

    # REC 3500: TP. Hồ Chí Minh Đoạn ngập kéo dài không đáng kể
    (3500, "Tại TP. Hồ Chí Minh , Đoạn ngập kéo dài không đáng kể .",
     [("TP. Hồ Chí Minh", "Đoạn ngập kéo dài không đáng kể", "NEG")])
]

def apply_revisions():
    with open('data/validate_label/thuan/phase3.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    print(f"Loaded {len(lines)} lines from phase3.txt")

    for rec_id, text, trips in batch_31_35_revisions:
        idx = rec_id - 1
        generated_triplets = []
        for asp_phrase, opi_phrase, pol in trips:
            t = make_triplet(text, asp_phrase, opi_phrase, pol)
            if t is None:
                print(f"ERROR: Cannot create triplet for REC {rec_id}: {asp_phrase} | {opi_phrase}")
                return False
            generated_triplets.append(t)
            
        new_line = f"{text}####{json.dumps(generated_triplets)}"
        lines[idx] = new_line
        print(f"Updated REC {rec_id}: {len(generated_triplets)} triplets")

    with open('data/validate_label/thuan/phase3.txt', 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

    print("Successfully wrote updates to phase3.txt")
    return True

if __name__ == '__main__':
    apply_revisions()
