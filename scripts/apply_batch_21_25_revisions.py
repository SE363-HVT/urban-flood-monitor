# -*- coding: utf-8 -*-
from span_helper import make_triplet
import json

batch_21_25_revisions = [
    # REC 2116: Huỳnh Thúc Kháng, Tân Phú ngập
    (2116, "Dự đoán tình hình mưa Sài Gòn hôm nay : Huỳnh Thúc Kháng ngập tới háng , Trần Đình xu ngập tới khu , Tân Phú ngập tới dzú , Củ Chi ngập tới ti , Vân Đồn , Cát Lái ngập tới . . .",
     [("Huỳnh Thúc Kháng", "ngập tới háng", "NEG"),
      ("Tân Phú", "ngập tới dzú", "NEG"),
      ("Củ Chi", "ngập tới ti", "NEG")]),

    # REC 2142: Quốc lộ 13, Lái Thiêu HẾT NGẬP
    (2142, "CHỐNG NGẬP KIỂU MỚI , ĐƯA NƯỚC VÀO NHÀ DÂN LÀ MẶT ĐƯỜNG SẼ HẾT NGẬP Theo thông tin từ Báo Tiền Phong ngày 10 / 09 / 2026 , dự án nâng cấp Quốc lộ 13 qua phường Lái Thiêu và Bình Hòa tại TP. HCM đang tiến hành nâng nền đường cao hơ",
     [("Quốc lộ 13", "HẾT NGẬP", "POS"),
      ("Lái Thiêu", "HẾT NGẬP", "POS")]),

    # REC 2146: TP. HCM DỄ NGẬP NƯỚC
    (2146, "CHIỀU NAY NẾU MƯA LỚN , NGƯỜI DÂN TP. HCM CẦN LƯU Ý NHỮNG ĐOẠN ĐƯỜNG DỄ NGẬP NƯỚC NÀO ?",
     [("TP. HCM", "DỄ NGẬP NƯỚC", "NEU")]),

    # REC 2150: hẻm 290 Nguyễn Hữu Cảnh ngập úng
    (2150, "Ba thập kỷ qua , hơn 300 hộ dân tại hẻm 290 Nguyễn Hữu Cảnh , phường Rạch Dừa , TPHCM phải sống chung với cảnh ngập úng mỗi khi mùa mưa đến .",
     [("hẻm 290 Nguyễn Hữu Cảnh", "ngập úng", "NEG")]),

    # REC 2158: TPHCM tránh ngập
    (2158, "Anh em chọn hướng tránh ngập TPHCM # canhbaongaplut # canhbaoketxengaymua # ngapquan2 # ngapduongtrannao # canhbaogiaothong # giaothongantoan",
     [("TPHCM", "tránh ngập", "POS")]),

    # REC 2199: HCM ngập rồi
    (2199, "Tại TP. Hồ Chí Minh , Bãi giữa HCM ngập rồi ae ơi",
     [("HCM", "ngập rồi", "NEG")]),

    # REC 2311: Phú Mỹ Hưng ngập lụt
    (2311, "Tại TP. Hồ Chí Minh , “ Phú Mỹ Hưng là điển hình cho việc đô thị thích ứng với sụt lún , ngập lụt ” , ông Chơn nhận định .",
     [("Phú Mỹ Hưng", "ngập lụt", "NEU")]),

    # REC 2337: Trần Xuân Soạn, Hồ Học Lãm xuất hiện tình trạng ngập
    (2337, "Hồ Chí Minh như Trần Xuân Soạn và Hồ Học Lãm xuất hiện tình trạng ngập .",
     [("Trần Xuân Soạn", "xuất hiện tình trạng ngập", "NEG"),
      ("Hồ Học Lãm", "xuất hiện tình trạng ngập", "NEG")]),

    # REC 2341: phường Thuận An ngập sâu
    (2341, "Theo Chủ tịch UBND phường Thuận An Nguyễn Thanh Sơn , phường tiếp tục duy trì lực lượng và phương tiện ứng trực , thường xuyên kiểm tra các tuyến bờ bao , khu vực trũng thấp , cống thoát nước ; chủ động cảnh báo , xử lý những điểm có nguy cơ tràn bờ , sạt lở , ngập sâu , bảo đảm an toàn cho người dân .",
     [("phường Thuận An", "ngập sâu", "NEU")]),

    # REC 2352: Cống Phú Định chống ngập
    (2352, "Cống Phú Định trên Kênh Đôi có vai trò gì trong việc chống ngập ?",
     [("Cống Phú Định", "chống ngập", "POS")]),

    # REC 2354: TP. Hồ Chí Minh thời điểm ngập
    (2354, "Tại TP. Hồ Chí Minh , Đáng chú ý , thời điểm ngập thường trùng giờ cao điểm , ảnh hưởng trực tiếp đến việc đi lại của người dân , học sinh .",
     [("TP. Hồ Chí Minh", "thời điểm ngập", "NEG")]),

    # REC 2359: TP. Hồ Chí Minh ngập như gì
    (2359, "Tại TP. Hồ Chí Minh , Bình minh quê tôi ngập như gì .",
     [("TP. Hồ Chí Minh", "ngập như gì", "NEG")]),

    # REC 2361: TP. Hồ Chí Minh mưa tí là ngập
    (2361, "Tại TP. Hồ Chí Minh , Thế nhưng mưa tí là ngập",
     [("TP. Hồ Chí Minh", "mưa tí là ngập", "NEG")]),

    # REC 2362: phần huy ích nuic ngập
    (2362, "Tại TP. Hồ Chí Minh , ối đồi ôi , đây là video hồi tối e nói thấy có người live nuic ngập phần huy ích .",
     [("phần huy ích", "nuic ngập", "NEG")]),

    # REC 2373: Đường NA3, chánh phú hoà ngập hư hỏng hết đồ trong nhà
    (2373, "Tại TP. Hồ Chí Minh , em ở đây ngập hư hỏng hết đồ trong nhà rồi , 🥹 🥹 Đường NA3 , chánh phú hoà , BC BD mưa lớn tối 28 / 09 / 2026 # myphuoc3 # bencat # binhduong # myphuoc # ngaplut",
     [("Đường NA3", "ngập hư hỏng hết đồ trong nhà", "NEG"),
      ("chánh phú hoà", "ngập hư hỏng hết đồ trong nhà", "NEG")]),

    # REC 2386: sg mưa ngập
    (2386, "Tại TP. Hồ Chí Minh , sg sống nhanh quá , làm tí mưa ngập cho mn chậm lại 😶 ‍ 🌫 ️ 😶 ‍ 🌫 ️",
     [("sg", "mưa ngập", "NEG")]),

    # REC 2400: Sài Gòn chống ngập
    (2400, "Dự án chống ngập 10 . 000 tỷ của Sài Gòn chống ngập thế nào ?",
     [("Sài Gòn", "chống ngập", "POS")]),

    # REC 2452: Sài Gòn ngập nặng
    (2452, "Giới chức Trung Tâm Quản Lý Giao Thông Và Hạ Tầng Kỹ Thuật , xác nhận có ít nhất 12 con đường ở Sài Gòn ngập nặng ,",
     [("Sài Gòn", "ngập nặng", "NEG")]),

    # REC 2456: Sài Gòn mưa ngập
    (2456, "Dễ thương , Sài Gòn mưa ngập , anh Tây tranh thủ “ đu xe rác ” đi nhờ .",
     [("Sài Gòn", "mưa ngập", "NEG")]),

    # REC 2459: Phan Huy Ích ngập tới khoảng 1m
    (2459, "Riêng Phan Huy Ích có đoạn ngập tới khoảng 1m , nước tràn vào",
     [("Phan Huy Ích", "ngập tới khoảng 1m", "NEG")]),

    # REC 2481: TP. Hồ Chí Minh ngập lụt
    (2481, "Tại TP. Hồ Chí Minh , Mất tầm 30 ' chạy khắp ngõ ngách kiếm đường thoát nhưng đều bị dồn vào ngõ cụt vì bị chặn 2 đầu … trọn vẹn 3 , 5 tiếng đứng yên trong mưa và ngập lụt chờ nước rút nhưng ko làm được gì ,",
     [("TP. Hồ Chí Minh", "ngập lụt", "NEG")]),

    # REC 2496: đường 11, phường Trường Thọ ngập sâu trong nước
    (2496, "Tại TP. Hồ Chí Minh , Tủ lạnh , máy giặt , giường nệm ngập sâu trong nước Tối qua , người dân trên đường 11 ( phường Trường Thọ cũ ) thức trắng đêm Sau trận mưa chiều qua , nước ngập nhanh khiến tủ lạnh , máy giặt , nệm , nồi , xe … ngập trong nước Nhiều người",
     [("đường 11", "ngập sâu trong nước", "NEG"),
      ("phường Trường Thọ", "ngập nhanh", "NEG")]),

    # REC 2500: TP. Hồ Chí Minh Ngập
    (2500, "Tại TP. Hồ Chí Minh , Ngập thì ngập cứ đi thẳng về phía trước .",
     [("TP. Hồ Chí Minh", "Ngập", "NEG")])
]

def apply_revisions():
    with open('data/validate_label/thuan/phase3.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    print(f"Loaded {len(lines)} lines from phase3.txt")

    for rec_id, text, trips in batch_21_25_revisions:
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
