# -*- coding: utf-8 -*-
from span_helper import make_triplet
import json

batch_26_30_revisions = [
    # REC 2514: TP. HCM VÙNG NGẬP SÂU
    (2514, "KHẨN CẤP : TP. HCM YÊU CẦU SƠ TÁN KHI VÙNG NGẬP SÂU UBND TP. HCM vừa ban hành công văn khẩn , yêu cầu các sở , ngành và địa phương theo dõi chặt diễn biến thời tiết , trực ban 24 / 24h và bố trí lực lượng cảnh báo , hướng dẫn giao thông .",
     [("TP. HCM", "VÙNG NGẬP SÂU", "NEG")]),

    # REC 2523: TP. HCM xử lý điểm ngập
    (2523, "TP. HCM bố trí máy bơm di động xử lý điểm ngập .",
     [("TP. HCM", "xử lý điểm ngập", "POS")]),

    # REC 2546: TP. HCM xử lý các điểm ngập
    (2546, "Sau những ngày nhiều tuyến đường tiếp tục biến thành sông , TP. HCM lại bước vào một đợt rà soát lớn để tìm nguyên nhân và xếp thứ tự ưu tiên xử lý các điểm ngập .",
     [("TP. HCM", "xử lý các điểm ngập", "POS")]),

    # REC 2558: Ung Văn Khiêm, đường Quốc Hương, Võ Văn Ngân, Nguyễn Duy Trinh NGẬP CẢ LỐI VỀ
    (2558, "TP. HCM SAU CƠN MƯA LỚN NGẬP CẢ LỐI VỀ Cơn mưa lúc hơn 16h chiều 1 / 10 / 2022 làm nhiều tuyến đường như Ung Văn Khiêm ( quận Bình Thạnh ) , đường Quốc Hương , Võ Văn Ngân , Nguyễn Duy Trinh , ( TP T",
     [("Ung Văn Khiêm", "NGẬP CẢ LỐI VỀ", "NEG"),
      ("đường Quốc Hương", "NGẬP CẢ LỐI VỀ", "NEG"),
      ("Võ Văn Ngân", "NGẬP CẢ LỐI VỀ", "NEG"),
      ("Nguyễn Duy Trinh", "NGẬP CẢ LỐI VỀ", "NEG")]),

    # REC 2561: Quốc lộ 13 ngập
    (2561, "Nâng nền Quốc lộ 13 ở TP. HCM , chủ đầu tư lý giải và lên phương án hỗ trợ các hộ dân bị ảnh hưởng # VOVTPHCM # Quốclộ13 # nângnền # ngập # bụi",
     [("Quốc lộ 13", "ngập", "NEG")]),

    # REC 2564: đường Ung Văn Khiêm ngập nước
    (2564, "TP. HCM chuẩn bị mở rộng đường Ung Văn Khiêm và nghiên cứu dự án hơn 10 . 000 tỉ đồng với đường trên cao , nút giao đa tầng Hàng Xanh để giảm kẹt xe , ngập nước .",
     [("đường Ung Văn Khiêm", "ngập nước", "POS")]),

    # REC 2576: TP. HCM giải quyết 50 điểm ngập nặng
    (2576, "TP. HCM lên kế hoạch giải quyết 50 điểm ngập nặng",
     [("TP. HCM", "giải quyết 50 điểm ngập nặng", "POS")]),

    # REC 2596: xã Tân Vĩnh Lộc ngập úng
    (2596, "Tại TP. Hồ Chí Minh , Hơn 7 ngày qua , nhiều hộ dân ở xã Tân Vĩnh Lộc phải sống chung với cảnh ngập úng",
     [("xã Tân Vĩnh Lộc", "ngập úng", "NEG")]),

    # REC 2611: TP. Hồ Chí Minh chống ngập
    (2611, "Tại TP. Hồ Chí Minh , Vậy có cách nào chống ngập không ?",
     [("TP. Hồ Chí Minh", "chống ngập", "NEU")]),

    # REC 2612: Bến Nghé, Tân Thuận, Phú Xuân, Mương Chuối, Cây Khô, Phú Định chống ngập
    (2612, "Dự án chống ngập 10 . 000 tỷ đồng với 6 cống ngăn triều : Bến Nghé , Tân Thuận , Phú Xuân , Mương Chuối , Cây Khô , Phú Định , vận hành thông minh bằng SCADA .",
     [("Bến Nghé", "chống ngập", "POS"),
      ("Tân Thuận", "chống ngập", "POS"),
      ("Phú Xuân", "chống ngập", "POS"),
      ("Mương Chuối", "chống ngập", "POS"),
      ("Cây Khô", "chống ngập", "POS"),
      ("Phú Định", "chống ngập", "POS")]),

    # REC 2613: Khu Nam ngập
    (2613, "Tại TP. Hồ Chí Minh , Anh chị ở Khu Nam thấy tình hình ngập dạo này thế nào ?",
     [("Khu Nam", "ngập", "NEU")]),

    # REC 2622: Sài Gòn ngập lụt
    (2622, "5 CON ĐƯỜNG HUYỀN THOẠI chuyên gia ngập lụt mùa mưa bão mà con dân Sài Gòn nào nghe tới cũng thấy sợ 🤣 🤣 🤣",
     [("Sài Gòn", "ngập lụt", "NEG")]),

    # REC 2647: đường Phan Huy Ích ngập hơn 1 mét
    (2647, "Đã tìm ra nguyên nhân đường Phan Huy Ích ngập hơn 1 mét tối qua",
     [("đường Phan Huy Ích", "ngập hơn 1 mét", "NEG")]),

    # REC 2654: TP. HCM chống ngập
    (2654, "Dự án chống ngập quy mô lớn nhất TP. HCM sẽ vận hành chính thức vào tháng 11 - 2026 .",
     [("TP. HCM", "chống ngập", "POS")]),

    # REC 2655: TP. HCM chống ngập
    (2655, "TP. HCM chi hơn 142 . 000 tỷ đồng cho bài toán chống ngập , đặt mục tiêu đến năm 2030 cơ bản xử lý ngập do mưa .",
     [("TP. HCM", "chống ngập", "POS")]),

    # REC 2660: Hồ Chí Minh xử lý 50 vị trí ngập nặng
    (2660, "Tại TP. Hồ Chí Minh , Hồ Chí Minh dự kiến chi hơn 142 . 000 tỷ đồng cho các dự án giao thông , thủy lợi , thoát nước và chỉnh trang đô thị , tập trung xử lý 50 vị trí ngập nặng .",
     [("Hồ Chí Minh", "xử lý 50 vị trí ngập nặng", "POS")]),

    # REC 2662: TP. HCM chống ngập
    (2662, "Đầu tư hơn 7 . 000 tỷ cho các dự án chống ngập nhưng TP. HCM chỉ mới giải quyết được 3 / 50 điểm ngập .",
     [("TP. HCM", "chống ngập", "POS")]),

    # REC 2696: TP. HCM ngập lâu
    (2696, "Vì sao nhiều điểm ngập ở TP. HCM nay ngập lâu , nước rút chậm ?",
     [("TP. HCM", "ngập lâu", "NEG")]),

    # REC 2699: Hồ Chí Minh thường xuyên ngập nặng
    (2699, "Tại TP. Hồ Chí Minh , Hồ Chí Minh hiện ghi nhận 159 điểm ngập , trong đó có 24 tuyến đường thường xuyên ngập nặng .",
     [("Hồ Chí Minh", "thường xuyên ngập nặng", "NEG")]),

    # REC 2746: TP. HCM NGẬP NGỤA VÌ MƯA VÀ TRIỀU
    (2746, "NGẬP NGỤA VÌ MƯA VÀ TRIỀU , TP. HCM RÚT NGẮN THỜI GIAN GIẢI QUYẾT Sở Xây dựng TP. HCM cho biết trận mưa cuối tháng 9 và đầu tháng 10 vượt tần suất thiết kế của hệ thống thoát nước , khiến nhiều kênh rạch dâng cao và rút chậm .",
     [("TP. HCM", "NGẬP NGỤA VÌ MƯA VÀ TRIỀU", "NEG")]),

    # REC 2747: Hồ Chí Minh xử lý 50 điểm ngập
    (2747, "Tại TP. Hồ Chí Minh , Hồ Chí Minh dành 142 . 000 tỷ đồng xử lý 50 điểm ngập",
     [("Hồ Chí Minh", "xử lý 50 điểm ngập", "POS")]),

    # REC 2782: TP. HCM chống ngập
    (2782, "Nâng nền nhà 3 lần , tốn hơn 100 triệu đồng vẫn loay hoay chống ngập ở TP. HCM",
     [("TP. HCM", "chống ngập", "NEG")]),

    # REC 2784: Thành phố Hồ Chí Minh đỉnh triều cường
    (2784, "🌧 ️ HƯỚNG DẪN ĐẢM BẢO AN TOÀN KHI CÓ NGẬP LỤT TẠI ĐÔ THỊ Theo Đài Khí tượng Thủy văn Nam Bộ , đỉnh triều cường tại Thành phố Hồ Chí Minh dự báo vượt báo động 3 từ ngày 28 / 9 đến 30 / 9 / 2026 .",
     [("Thành phố Hồ Chí Minh", "đỉnh triều cường", "NEU")]),

    # REC 2800: TP. HCM đường ngập sâu
    (2800, "TP. HCM liên tục có mưa lớn , đường ngập sâu : Vì sao thời tiết ngày càng bất thường ?",
     [("TP. HCM", "đường ngập sâu", "NEG")]),

    # REC 2810: Gò Vấp ngập sâu hơn 1 m
    (2810, "🔴 KHOẢNH KHẮC NƯỚC TRÀN VÀO NHÀ DÂN Ở KHU BIỆT THỰ TP HCM Sáng 8 / 10 , nhiều tầng hầm tại khu dân cư Cityland Park Hills ( phường Gò Vấp , TPHCM ) vẫn ngập sâu hơn 1 m sau trận mưa lớn chiều tối 7 / 10 , khiến nhiều xe máy , máy móc và thiết",
     [("Gò Vấp", "ngập sâu hơn 1 m", "NEG")]),

    # REC 2819: đường Mã Lò chống ngập
    (2819, "TP. HCM khởi công dự án chống ngập đường Mã Lò trong tháng 11 - Báo Thanh Niên",
     [("đường Mã Lò", "chống ngập", "POS")]),

    # REC 2821: Quận 1 ngập
    (2821, "Tại TP. Hồ Chí Minh , Quận 1 mưa lớn còn ngập thì đừng hỏi sao mưa lớn đường thành sông , 5 lý do vì sao đường ngập có thể gây bất ngờ ?",
     [("Quận 1", "ngập", "NEG")]),

    # REC 2823: Sài Gòn ngập lụt
    (2823, "🧐 Vì sao năm nào cũng mưa , nhưng năm nay Sài Gòn lại ngập lụt tới vậy ?",
     [("Sài Gòn", "ngập lụt", "NEU")]),

    # REC 2830: TP. HCM CẢNH BÁO 122 ĐIỂM NGẬP LỤT
    (2830, "TP. HCM PHÁT CẢNH BÁO 122 ĐIỂM NGẬP LỤT SAU NHỮNG CƠN MUA NẶNG HẠT KÉO DÀI CHIỀU 7 / 10",
     [("TP. HCM", "CẢNH BÁO 122 ĐIỂM NGẬP LỤT", "NEU")]),

    # REC 2845: TP. Hồ Chí Minh NGẬP XUYÊN ĐÊM
    (2845, "Tại TP. Hồ Chí Minh , ĐÀ GÒ RỒI CŨNG NGẬP XUYÊN ĐÊM .",
     [("TP. Hồ Chí Minh", "NGẬP XUYÊN ĐÊM", "NEG")]),

    # REC 2848: Hồ Chí Minh chống ngập
    (2848, "Hồ Chí Minh dự kiến hoàn thành 9 dự án chống ngập ngay trong năm nay .",
     [("Hồ Chí Minh", "chống ngập", "POS")]),

    # REC 2850: TP. HCM ứng phó ngập do mưa lớn kết hợp triều cường
    (2850, "TP. HCM : Tăng cường ứng phó ngập do mưa lớn kết hợp triều cường .",
     [("TP. HCM", "ứng phó ngập do mưa lớn kết hợp triều cường", "POS")]),

    # REC 2861: Quận 7, Nhà Bè ngập
    (2861, "Tại sao đỉnh triều cường 10 / 10 chỉ ngập Quận 7 và Nhà Bè ?",
     [("Quận 7", "ngập", "NEG"),
      ("Nhà Bè", "ngập", "NEG")]),

    # REC 2862: Quận 7, Nhà Bè hết ngập
    (2862, "Tại TP. Hồ Chí Minh , Xem ngay câu trả lời từ tiến độ dự án 10 . 000 tỷ chống ngập ở Quận 7 và Nhà Bè đạt 80 % . Sang năm khu vực này mới hết ngập Chỗ của anh em hôm nay có bị ngập không ?",
     [("Quận 7", "hết ngập", "POS"),
      ("Nhà Bè", "hết ngập", "POS")]),

    # REC 2863: TP HCM triều cường đạt đỉnh
    (2863, "Nhiều trường ở TP HCM cho học sinh về sớm , tránh triều cường đạt đỉnh 12 / 10 - 13 / 10 # trieucuong # xuhuong ( theo socmedia , vnexpress )",
     [("TP HCM", "triều cường đạt đỉnh", "NEU")]),

    # REC 2876: quận 7 ngập do mưa và triều cường
    (2876, "Đây là hy vọng cho người dân quận 7 sẽ không còn phải khổ sở vì ngập do mưa và triều cường .",
     [("quận 7", "ngập do mưa và triều cường", "NEG")]),

    # REC 2921: TP. Hồ Chí Minh bì bõm lội qua những vũng nước
    (2921, "Tại TP. Hồ Chí Minh , Như thông lệ , cư dân của thành phố sôi động nhất cả nước phải hứng chịu cảnh bì bõm lội qua những vũng nước giữa đô thị giờ tan tầm .",
     [("TP. Hồ Chí Minh", "bì bõm lội qua những vũng nước", "NEG")]),

    # REC 2945: HCM bị ngập sâu
    (2945, "Tại TP. Hồ Chí Minh , HCM ) bị ngập sâu , khiến nhiều người tham gia giao thông gặp nhiều khó khăn , một số người té ngã sõng soài xuống nước , một số người phải phải dắt bộ vì xe chết máy giữa đường .",
     [("HCM", "bị ngập sâu", "NEG")]),

    # REC 2960: TP. HCM vùng ngập sâu gần 2m
    (2960, "Ngay sau khi nhận tin , Phòng Cảnh sát PCCC & CNCH – Công an TP. HCM đã huy động hàng chục cán bộ , chiến sĩ chia nhiều hướng vào vùng ngập sâu gần 2m để cứu người trong đêm tối .",
     [("TP. HCM", "vùng ngập sâu gần 2m", "NEG")]),

    # REC 2963: hầm chui chống ngập
    (2963, "Nực cười ở chỗ , cả một công trình hầm chui 75 tỷ , nhưng đầu tư cả camera giám sát , lực lượng túc trực và máy bơm chỉ để . . . chống ngập .",
     [("hầm chui", "chống ngập", "POS")]),

    # REC 2981: đường Nguyễn Hữu Cảnh máy bơm chống ngập
    (2981, "Cần đàm phán , trường hợp dừng thuê máy bơm chống ngập đường Nguyễn Hữu Cảnh trước thời hạn , TP. HCM sẽ phải bồi thường thiệt hại hợp đồng cho Công ty cổ phần tập đoàn công nghiệp Quang Trung .",
     [("đường Nguyễn Hữu Cảnh", "máy bơm chống ngập", "POS")]),

    # REC 2992: TP. Hồ Chí Minh chìm trong biển nước
    (2992, "Tại TP. Hồ Chí Minh , đã chìm trong biển nước .",
     [("TP. Hồ Chí Minh", "chìm trong biển nước", "NEG")])
]

def apply_revisions():
    with open('data/validate_label/thuan/phase3.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    print(f"Loaded {len(lines)} lines from phase3.txt")

    for rec_id, text, trips in batch_26_30_revisions:
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
