# -*- coding: utf-8 -*-
from span_helper import make_triplet
import json

# Định nghĩa các bản ghi phục hồi cho Lô 1-4 (Recs 1 - 400)
# Format: (rec_id, text, [(asp_phrase, opi_phrase, pol), ...])
batch_1_4_revisions = [
    # REC 1: Trần Xuân Soạn ngập
    (1, "Chiều nay mưa 🌧 ️ 🌧 ️ 🌧 ️ Mưa thì mưa quán vẫn giao nước đến UFM như thường nha . Nổ đơn đùng đùng dù Trần Xuân Soạn có ngập quán cũng chèo xuồng đi giao 🌊 Zalo : 0368443756 mãi eoooo 🥰 Kafe Gần Nhà",
     [("Trần Xuân Soạn", "ngập", "NEG")]),

    # REC 73: thảo điền chống ngập
    (73, "bơm chìm . chống ngập gấp cho chủ nhà tại thảo điền quận 2 # maybomchim # bomchim # diennuoccuongthinh # bomchimchongngap # bomchimluuluong",
     [("thảo điền", "chống ngập gấp", "POS")]),

    # REC 75: Sài Gòn mưa ngập quá
    (75, "Sài Gòn dạo này mưa ngập quá , nay rảnh rỗi hát live một đoạn bài mới cho cả nhà nghe nhé 🌎 🫶 🏻 # MuonCaTraiDat # SOBE # nhachaymoingay",
     [("Sài Gòn", "mưa ngập quá", "NEG")]),

    # REC 113: Sài Gòn mưa ngập
    (113, "Hoàng Hôn Sài Gòn sau chuỗi mưa ngập 😍 📸 : Hoàng Châu , ST",
     [("Sài Gòn", "mưa ngập", "NEG")]),

    # REC 165: An Lạc, Bình Tân ngập
    (165, "2h chiều nay chưa mưa nhưng đã ngập . Ngập thì ngập cứ đi thẳng về phía trước . Lắp đặt bộ siêu trong Cubic 40 - An Lạc , Bình Tân .",
     [("Bình Tân", "đã ngập", "NEG"), ("An Lạc", "đã ngập", "NEG")]),

    # REC 195: Sài Gòn có mưa ngập không
    (195, "Nhẹ nhàng cùng bữa sáng tại Hà Nội rồi vào Sài Gòn kiếm tô Hủ Tiếu 🍜 🍜 🍜 . Sài Gòn có mưa ngập không anh em ? 👬 👬",
     [("Sài Gòn", "mưa ngập không", "NEU")]),

    # REC 216: Sài Gòn xe chết máy hàng loạt
    (216, "SAU TRẬN NGẬP TỐI 1 / 10 : CÓ NÊN MUA CHUNG CƯ ĐỂ TRÁNH NGẬP ? 3 CÂU HỎI TRƯỚC KHI MUA Tối 1 / 10 , Sài Gòn mưa lớn đúng giờ tan tầm , lại gặp triều cường . Nhiều tuyến đường ngập , có chỗ nước lên quá đầu gối , xe chết máy hàng loạt . Có con",
     [("Sài Gòn", "xe chết máy hàng loạt", "NEG")]),

    # REC 230: Phan Huy Ích ngập nước, rút nước
    (230, "Khu vực Phan Huy Ích - Tân Phú ngập nước có thể ghé em ngồi đợi rút nước rồi về nhé khách ơi",
     [("Phan Huy Ích", "ngập nước", "NEG"), ("Phan Huy Ích", "rút nước", "POS")]),

    # REC 243: TP HCM ngập thường xuyên
    (243, "Before \" chốt cọc \" : check ngay 159 điểm ngập thường xuyên của TP HCM 👇 👇 👇",
     [("TP HCM", "ngập thường xuyên", "NEG")]),

    # REC 262: Ung Văn Khiêm, đường Quốc Hương, Võ Văn Ngân, Nguyễn Duy Trinh ngập cả lối về
    (262, "Hà Bình Thuận . DJ . ILHAM · DIGIDI DIGIDI . TP. HCM SAU CƠN MƯA LỚN NGẬP CẢ LỐI VỀ Cơn mưa lúc hơn 16h chiều 1 / 10 / 2022 làm nhiều tuyến đường như Ung Văn Khiêm ( quận Bình Thạnh ) , đường Quốc Hương , Võ Văn Ngân , Nguyễn Duy Trinh , ( TP T",
     [("Ung Văn Khiêm", "NGẬP CẢ LỐI VỀ", "NEG"),
      ("đường Quốc Hương", "NGẬP CẢ LỐI VỀ", "NEG"),
      ("Võ Văn Ngân", "NGẬP CẢ LỐI VỀ", "NEG"),
      ("Nguyễn Duy Trinh", "NGẬP CẢ LỐI VỀ", "NEG")]),

    # REC 276: Sài Gòn mưa hoài
    (276, "💥 💥 Sài Gòn mưa gì mà mưa hoài vậy , ngày nào cũng mưa , chuỗi ngày “ Chiều nay trời Mưa ” 😎 😎 😎 # mưa # ngập # mưagióbãobùng # sàigòn # tphcm",
     [("Sài Gòn", "mưa hoài", "NEG")]),

    # REC 279: Sài Gòn lội nước
    (279, "💥 💥 Chiến thần lội nước bãi sau Sài Gòn chuỗi ngày “ Hồi chiều trời Mưa ” 😎 😎 😎 # mưa # ngập # mưagióbãobùng # viral # sàigòn",
     [("Sài Gòn", "lội nước", "NEG")]),

    # REC 280: Sài Gòn lội nước
    (280, "💥 💥 Cập nhật tình hình Sài Gòn Mưa Bão ngày 7 / 10 / 2026 của chuỗi ngày “ Hồi chiều trời Mưa ” chưa dứt . Dòng người lội nước giờ tan làm thật tội nghiệp 😎 😎 😎 # mưa # ngập # mưagióbãobùng # sàigòn # tphcm",
     [("Sài Gòn", "lội nước", "NEG")]),

    # REC 293: Gò Vấp combo Mưa - Ngập
    (293, "💥 💥 Gò Vấp Sài Gòn chuỗi ngày “ Hồi chiều trời Mưa ” và combo Mưa - Ngập giờ tan làm 😎 😎 😎 # mưa # ngập # mưagióbãobùng # sàigòn # tphcm",
     [("Gò Vấp", "Mưa - Ngập", "NEG")]),

    # REC 335: Sài Gòn mưa ngập lối
    (335, "Sài Gòn hôm nay mưa gì mà mưa ngập lối luôn á 🥹 🌧 ️ Ra đường thì sợ ướt , về nhà thì đường ngập , thôi mình … tìm chỗ trú mưa cho an toàn nha 😂 Mưa ngoài kia cứ rơi , còn ở Nhà Của Min thì bật máy lạnh , nằm chill , xem phim , nghỉ ngơi một xíu cho đời bớt",
     [("Sài Gòn", "mưa ngập lối", "NEG")]),

    # REC 380: Thành phố Hồ Chí Minh triều cường dâng cao
    (380, "PHÒNG CSGT CÔNG AN TPHCM CẢNH BÁO 122 ĐIỂM NGẬP NƯỚC TRÊN ĐỊA BÀN TP. KHU VỰC PHÍA ĐÔNG ( TỈNH BRVT CŨ ) , GỒM CÓ : Thành phố Hồ Chí Minh đang bước vào mùa mưa với những đợt mưa lớn , triều cường dâng cao , nhiều tuyến đườ",
     [("Thành phố Hồ Chí Minh", "triều cường dâng cao", "NEG")])
]

def apply_revisions():
    with open('data/validate_label/thuan/phase3.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    print(f"Loaded {len(lines)} lines from phase3.txt")

    for rec_id, text, trips in batch_1_4_revisions:
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
