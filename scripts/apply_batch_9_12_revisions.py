# -*- coding: utf-8 -*-
from span_helper import make_triplet
import json

batch_9_12_revisions = [
    # REC 814: TP. HCM ngập nước
    (814, "Danh sách 122 điểm ngập nước ở TP. HCM , người đi đường cần lưu ý",
     [("TP. HCM", "ngập nước", "NEU")]),

    # REC 829: TP. Hồ Chí Minh hết ngập
    (829, "Tại TP. Hồ Chí Minh , Bao giờ thành phố mới hết ngập ?",
     [("TP. Hồ Chí Minh", "hết ngập", "NEU")]),

    # REC 830: TP. Hồ Chí Minh HẾT NGẬP
    (830, "Tại TP. Hồ Chí Minh , BAO LÂU NỮA SẼ HẾT NGẬP ĐÂY NHÀ NƯỚC ƠI !",
     [("TP. Hồ Chí Minh", "HẾT NGẬP", "NEU")]),

    # REC 832: TP. Hồ Chí Minh nước ngập
    (832, "Tại TP. Hồ Chí Minh , Triều cường vừa đi qua , người dân chưa kịp quên cảnh nước ngập thì những con hẻm lại tất bật thi công .",
     [("TP. Hồ Chí Minh", "nước ngập", "NEG")]),

    # REC 844: Phú Mỹ Hưng nguy cơ ngập
    (844, "\" Xu hướng sụt lún và mực nước triều cường ngày một cao khiến trong tương lai không xa , một số nơi ở khu Phú Mỹ Hưng cũng sẽ đối mặt với nguy cơ ngập \" , TS Thiềm Quốc Tuấn nhận định .",
     [("Phú Mỹ Hưng", "đối mặt với nguy cơ ngập", "NEU")]),

    # REC 859: TP. Hồ Chí Minh có một số nơi bị ngập
    (859, "Tại TP. Hồ Chí Minh , Hôm qua mưa lớn , nhưng điều ấn tượng nhất là dù mưa trên toàn thành phố nhưng chỉ có một số nơi bị ngập , rất nhiều nơi không hề ngập .",
     [("TP. Hồ Chí Minh", "có một số nơi bị ngập", "NEG")]),

    # REC 860: TP. Hồ Chí Minh nước rút hết
    (860, "Tại TP. Hồ Chí Minh , Những nơi bị ngập thì chỉ trong vòng 1 tiếng là nước rút hết .",
     [("TP. Hồ Chí Minh", "nước rút hết", "POS")]),

    # REC 863: TP. Hồ Chí Minh nước đang rút dần
    (863, "Tại TP. Hồ Chí Minh , Rất may là mưa đã hết nên nước đang rút dần .",
     [("TP. Hồ Chí Minh", "nước đang rút dần", "POS")]),

    # REC 865: TP. HCM HẾT NGẬP
    (865, "“ VẬN NƯỚC ” ĐANG LÊN SIÊU DỰ ÁN 10 . 000 TỶ , TP. HCM CÓ HẾT NGẬP ?",
     [("TP. HCM", "HẾT NGẬP", "NEU")]),

    # REC 868: sài gòn ngập nước
    (868, "Tại TP. Hồ Chí Minh , sài gòn ngập nước , tình người không ngập ❤ ️",
     [("sài gòn", "ngập nước", "NEG")]),

    # REC 878: TP. HCM hết ngập
    (878, "⁉ Khi nào TP. HCM hết ngập ?",
     [("TP. HCM", "hết ngập", "NEU")]),

    # REC 900: TP. HCM hết ngập
    (900, "⁉ Khi nào TP. HCM hết ngập ? .",
     [("TP. HCM", "hết ngập", "NEU")]),

    # REC 905: Sài Gòn hết ngập
    (905, "Khi nào Sài Gòn mới hết ngập . . .",
     [("Sài Gòn", "hết ngập", "NEU")]),

    # REC 906: Hồ Chí Minh Đường hết ngập, nhà lại ngập
    (906, "Hồ Chí Minh được nâng cao để chống ngập , nhưng nước lại dồn sang các khu dân cư lân cận , khiến người dân rơi vào vòng luẩn quẩn : Đường hết ngập , nhà lại ngập .",
     [("Hồ Chí Minh", "chống ngập", "POS"),
      ("Hồ Chí Minh", "nhà lại ngập", "NEG")]),

    # REC 914: TP. Hồ Chí Minh chống ngập
    (914, "Tại TP. Hồ Chí Minh , Tình trạng này xuất hiện 2 - 3 năm qua nhưng đến nay càng nặng hơn khi công trình chống ngập tại đây đang ì ạch thi công chưa biết thời gian hoàn thiện .",
     [("TP. Hồ Chí Minh", "chống ngập", "POS")]),

    # REC 916: TP. Hồ Chí Minh đường ngập, khô ráo
    (916, "Tại TP. Hồ Chí Minh , Bình thường tôi còn bán thêm viên chiên từ lúc 16h chiều nhưng nay biết đường ngập nên đợi đến khi khô ráo mới đẩy xe ra bán .",
     [("TP. Hồ Chí Minh", "đường ngập", "NEG"),
      ("TP. Hồ Chí Minh", "khô ráo", "POS")]),

    # REC 926: sông Sài Gòn đang lên theo triều
    (926, "Nam Bộ có nguy cơ ngập sâu do triều cường 👉 🏻 Trong những ngày tới , mực nước sông Cửu Long , sông Sài Gòn đang lên theo triều và có khả năng đạt mức cao nhất vào ngày 25 - 27 / 10 / 2018 .",
     [("sông Sài Gòn", "đang lên theo triều", "NEU")]),

    # REC 930: TPHCM chống ngập
    (930, "🔴 CẬN CẢNH SIÊU DỰ ÁN CHỐNG NGẬP 10 . 000 TỶ CH . Ế . T CHÌM Ở TP. HCM Siêu dự án chống ngập của TPHCM , khởi công từ năm 2016 với tổng mức đầu tư gần 10 . 000 tỷ đồng , dự kiến hoàn thành vào năm 2018 nhưng đến nay vẫn chưa thể về đích .",
     [("TPHCM", "chống ngập", "POS")]),

    # REC 932: Thủ Đức chống ngập
    (932, "4 . 000 tỷ chống ngập ở Thủ Đức : Đừng để phải chờ ông trời nghiệm thu !",
     [("Thủ Đức", "chống ngập", "POS")]),

    # REC 949: Thành Hồ hết ngập lụt
    (949, "Bao giờ thì Thành Hồ hết ngập lụt ?",
     [("Thành Hồ", "hết ngập lụt", "NEU")]),

    # REC 969: TP. Hồ Chí Minh hết ngập
    (969, "Tại TP. Hồ Chí Minh , thì câu hỏi \" khi nào hết ngập ? \" vẫn chưa bao giờ có câu trả lời rõ ràng .",
     [("TP. Hồ Chí Minh", "hết ngập", "NEU")]),

    # REC 979: TP. Hồ Chí Minh chống ngập hiệu quả
    (979, "Tại TP. Hồ Chí Minh , Giải pháp nào chống ngập hiệu quả ?",
     [("TP. Hồ Chí Minh", "chống ngập hiệu quả", "POS")]),

    # REC 988: TP. Hồ Chí Minh nước mới rút hết
    (988, "Tại TP. Hồ Chí Minh , \" Tôi nâng nền hai lần rồi mà không ăn thua , phải mấy tiếng sau mưa nước mới rút hết \" , ông Liêm nói .",
     [("TP. Hồ Chí Minh", "nước mới rút hết", "POS")]),

    # REC 998: thành phố chống ngập
    (998, "Người dân vùng trũng thấp hy vọng công trình chống ngập do triều cường trị giá 10 . 000 tỷ đồng của thành phố sớm giải quyết được vướng mắc , đi vào hoạt động hiệu quả .",
     [("thành phố", "chống ngập", "POS")]),

    # REC 999: TP. Hồ Chí Minh sớm hết ngập
    (999, "Tại TP. Hồ Chí Minh , \" Tôi chỉ mong đường sớm hết ngập để các cháu đi học và người dân di chuyển qua lại được an toàn \" , bà Lĩnh mong ước .",
     [("TP. Hồ Chí Minh", "sớm hết ngập", "POS")]),

    # REC 1026: TP. Hồ Chí Minh nguy cơ ngập sâu khi mưa lớn
    (1026, "Tại TP. Hồ Chí Minh , ⚠ ️ Người dân nên theo dõi cảnh báo thời tiết , chủ động lựa chọn lộ trình và hạn chế đi qua các tuyến đường có nguy cơ ngập sâu khi mưa lớn .",
     [("TP. Hồ Chí Minh", "nguy cơ ngập sâu khi mưa lớn", "NEU")]),

    # REC 1031: TP Hồ Chí Minh nguy cơ ngập nước
    (1031, "📍 Phòng CSGT Công an TP Hồ Chí Minh thông tin 122 điểm có nguy cơ ngập nước , gồm 83 điểm ngập do mưa lớn , nước không thoát kịp và 39 điểm ng",
     [("TP Hồ Chí Minh", "nguy cơ ngập nước", "NEU")]),

    # REC 1042: Bến Nghé, Cây Khô, Mương Chuối, Phú Định, Phú Xuân Giải quyết ngập
    (1042, "Tháng 06 tới đây là tròn 10 năm kể từ thời điểm Trung Nam Group khởi công Dự án Giải quyết ngập do triều khu vực Thành phố Hồ Chí Minh với 8 hạng mục chính , trong đó gồm 6 cống ngăn triều : Bến Nghé , Cây Khô , Mương Chuối , Phú Định , Phú Xuân , Tân .",
     [("Bến Nghé", "Giải quyết ngập", "POS"),
      ("Cây Khô", "Giải quyết ngập", "POS"),
      ("Mương Chuối", "Giải quyết ngập", "POS"),
      ("Phú Định", "Giải quyết ngập", "POS"),
      ("Phú Xuân", "Giải quyết ngập", "POS")]),

    # REC 1116: TP. Hồ Chí Minh khu vực ngập sâu
    (1116, "Tại TP. Hồ Chí Minh , Người dân cần theo dõi dự báo , chủ động bảo vệ tài sản và hạn chế di chuyển qua khu vực ngập sâu .",
     [("TP. Hồ Chí Minh", "ngập sâu", "NEU")]),

    # REC 1121: TP. HCM Triều cường dự báo đạt đỉnh
    (1121, "TP. HCM và Nam Bộ 26 / 9 / 2026 Triều cường dự báo đạt đỉnh : 28 – 30 / 9 # NhipSong24H # ThoiTiet # TPHCM # MuaDong # TrieuCuong # NgapNuoc \"",
     [("TP. HCM", "Triều cường dự báo đạt đỉnh", "NEU")])
]

def apply_revisions():
    with open('data/validate_label/thuan/phase3.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    print(f"Loaded {len(lines)} lines from phase3.txt")

    for rec_id, text, trips in batch_9_12_revisions:
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
