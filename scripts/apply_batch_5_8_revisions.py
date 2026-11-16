# -*- coding: utf-8 -*-
from span_helper import make_triplet
import json

batch_5_8_revisions = [
    # REC 409: Gò Vấp ngập nhanh
    (409, "Ngọc Minh Võ . Hạnh Nguyên · Quê Em Miền Nước Lũ . 🌧 ️ GÒ VẤP MƯA LỚN , HẦM XE NGẬP NƯỚC – NGOÀI ĐƯỜNG THÀNH “ SÔNG ” Cơn mưa lớn khiến nhiều khu vực ở Gò Vấp ngập nhanh . Nước tràn xuống cả HẦM XE , trong khi nhiều tuyến đường bê",
     [("Gò Vấp", "ngập nhanh", "NEG")]),

    # REC 511: Sài Gòn ngập
    (511, "💦 MÙA MƯA SÀI GÒN - MÙA CỦA NHỮNG CƠN MƯA BẤT CHỢT 💦 🌧 ️ Sài Gòn đã bất đầu những cơn mưa đầu mùa . Những cơn mưa bất chợt , ào đến rồi đi để lại những \" con sông \" ngập bất thình lình : ) : ) ⛈ ️ Để đối phó với những cơn mưa hãy : 🌩 ️ Luôn c",
     [("Sài Gòn", "ngập bất thình lình", "NEG")]),

    # REC 541: Quận 7, Nhà Bè có bị ngập kg
    (541, "Tại TP. Hồ Chí Minh , Tình hình Quận 7 , Nhà Bè có bị ngập kg mọi người",
     [("Quận 7", "có bị ngập kg", "NEU"),
      ("Nhà Bè", "có bị ngập kg", "NEU")]),

    # REC 553: ĐƯỜNG UNG VĂN KHIÊM ngập lụt
    (553, "ĐƯỜNG UNG VĂN KHIÊM Nói đến các cung đường quan trọng hay những con đường hội tụ những đặc điểm rất Bình Thạnh gồm : ăn , chơi , kẹt xe và ngập lụt , người ta có thể liệt kê ngay những cái tên đã đi vào huyền thoại như Xô Viết Nghệ Tĩnh thì một đoạ",
     [("ĐƯỜNG UNG VĂN KHIÊM", "ngập lụt", "NEG")]),

    # REC 570: TP. HCM ngập
    (570, "\" Điệp khúc \" ngập do mưa và triều cường là nỗi ám ảnh của người dân tại TP. HCM . Bỏ nghề , bỏ nhà là những gì người dân nghĩ đến khi liên tục chịu cảnh sống chung với ngập .",
     [("TP. HCM", "ngập do mưa và triều cường", "NEG")]),

    # REC 593: sông Sài Gòn đang lên theo triều
    (593, "Nam Bộ có nguy cơ ngập sâu do triều cường 👉 🏻 Trong những ngày tới , mực nước sông Cửu Long , sông Sài Gòn đang lên theo triều và có khả năng đạt mức cao nhất vào ngày 25 - 27 / 10 / 2018 . 👉 🏻 Thời gian xuất hiện đỉnh triều hằng ngày từ 5 đến 7 giờ và từ",
     [("sông Sài Gòn", "đang lên theo triều", "NEU")]),

    # REC 605: TP. HCM hết ngập ?
    (605, "Yeah1 TV . . Bao giờ TP. HCM hết ngập ? # TNN # YeaH1",
     [("TP. HCM", "hết ngập", "NEU")]),

    # REC 607: TPHCM chống ngập
    (607, "🔴 CẬN CẢNH SIÊU DỰ ÁN CHỐNG NGẬP 10 . 000 TỶ CH . Ế . T CHÌM Ở TP. HCM Siêu dự án chống ngập của TPHCM , khởi công từ năm 2016 với tổng mức đầu tư gần 10 . 000 tỷ đồng , dự kiến hoàn thành vào năm 2018 nhưng đến nay vẫn chưa thể về đích . D",
     [("TPHCM", "chống ngập", "POS")]),

    # REC 634: Gò Vấp ngập nặng
    (634, "Tại TP. Hồ Chí Minh , ⚠ ️ POST NÀY ĐỂ DÂN GÒ VẤP CẬP NHẬT CÁC ĐOẠN ĐƯỜNG ĐANG BỊ NGẬP NẶNG ĐỂ MỌI NGƯỜI BIẾT TRÁNH NHA",
     [("Gò Vấp", "ngập nặng", "NEG")]),

    # REC 639: TPHCM ngập nước
    (639, "Vietnamnet . vn . . Theo đại diện Sở Xây dựng TPHCM , hệ thống thoát nước của địa phương đang quá tải , tình trạng ngập nước có thể tiếp tục diễn ra khi xuất hiện mưa lớn trong thời gian tới . # Vietnamnet # Thờisự # NH",
     [("TPHCM", "ngập nước", "NEU")]),

    # REC 645: Lê Văn Lương nước còn ngập hong
    (645, "Anh chị nào ở Nhà Bè cho em hỏi buổi sáng tầm 6h30 thì đường ở Lê Văn Lương nước còn ngập hong ạ",
     [("Lê Văn Lương", "còn ngập hong", "NEU")]),

    # REC 647: đào sư tích mưa liên tục và ngập
    (647, "Tại TP. Hồ Chí Minh , cho em hỏi có đường nào tránh ngập 1 tí không ạ em đi học về đang kẹt ở đào sư tích đường thì cứ mưa liên tục và ngập , anh chị khoá trên có biết đường nào tránh ngập 1 ít để xe chạy qua hông chỉ em với",
     [("đào sư tích", "mưa liên tục và ngập", "NEG")]),

    # REC 648: KDC Đào Sư Tích bị ngập không
    (648, "Anh em cho hỏi Đường đi từ Lotte Quận 7 đến KDC Đào Sư Tích , Phước Kiêng có Đoạn nào bị ngập không ? Và khi ngập thì Ô tô 7 chỗ đi qua đoạn này có ảnh hưởng gì không nhỉ ?",
     [("KDC Đào Sư Tích", "bị ngập không", "NEU")]),

    # REC 650: TP. HCM có 66 điểm ngập
    (650, "Tại TP. Hồ Chí Minh , Những \" điểm ngập \" trên địa bàn TP. HCM bạn nên biết khi MÙA MƯA TỚI : ( Theo thống kê , TP. HCM có 66 điểm ngập được thống kê , nhưng chỉ là các điểm ngoài đường phố , còn các điểm ngập trong con hẻm và khu dân cư vẫn chưa được liệt kê . Số liệu cho",
     [("TP. HCM", "có 66 điểm ngập", "NEU")]),

    # REC 719: Lê Văn Thọ ngập nửa bánh xe, Lê Đức Thọ trôi luôn xe
    (719, "Để phân biệt 2 con đường này tốt nhất là vào mùa mưa : Nếu là Lê Văn Thọ thì bạn sẽ bị ngập nửa bánh xe , còn Lê Đức Thọ thì nguyên bánh hoặc trôi luôn xe 😇",
     [("Lê Văn Thọ", "ngập nửa bánh xe", "NEG"),
      ("Lê Đức Thọ", "trôi luôn xe", "NEG")]),

    # REC 725: Sài Gòn chống ngập bằng AI
    (725, "Sài Gòn sắp chống ngập bằng AI luôn rồi bà con ơi # saigontrend # sukien # fantasticnetwork # saigonnews # saigonangi # saigon",
     [("Sài Gòn", "chống ngập", "POS")]),

    # REC 759: đường bùi văn ba, huỳnh tấn phát ngập nước
    (759, "Mn ơi cho em hỏi đường bùi văn ba với huỳnh tấn phát quận 7 có hay ngập nước không .",
     [("đường bùi văn ba", "hay ngập nước không", "NEU"),
      ("huỳnh tấn phát", "hay ngập nước không", "NEU")]),

    # REC 766: TPHCM ngập do mưa lớn
    (766, "HƠN 100 ĐIỂM NGẬP 👇 📌 Lưu ý quan trọng : Hiện TPHCM có 116 – 122 điểm ( không chính xác 112 ) theo thông tin mới nhất từ Sở Xây dựng & PC08 ( cập nhật 06 / 10 / 2026 ) . Dưới đây là danh sách đầy đủ , phân nhóm : 🌧 ️ I . 83 điểm ngập do mưa lớn Khu vực tr",
     [("TPHCM", "ngập do mưa lớn", "NEG")]),

    # REC 773: TP. Hồ Chí Minh mưa ngập
    (773, "Tại TP. Hồ Chí Minh , Trong những ngày mưa ngập , trường THPT Bình Tân cho phép học sinh mặc quần tây , áo sơ mi hoặc đồ thể dục thay áo dài , khuyến khích học sinh mang dép có quai hậu hoặc giày chống trơn thay vì mang giày bata",
     [("TP. Hồ Chí Minh", "mưa ngập", "NEG")]),

    # REC 784: đường lê văn lương hay bị ngập khi triều cường
    (784, "Tớ có tầm 4 tỷ , muốn đầu tư căn 2 ngủ ở mạn quận 9 hoặc Nhà Bè . Thấy dự án bên khải hoàn xây cũng nhanh , nhưng tìm hiểu thì ạn đường lê văn lương hay bị ngập khi triều cường ? có bạn nào review giúp tớ vs .",
     [("đường lê văn lương", "hay bị ngập khi triều cường", "NEG")]),

    # REC 800: Thảo Điền có ngập
    (800, "Các ba mẹ ơi , cho mình xin review trường Huỳnh Văn Ngỡi , Thảo Điền cũ với ạ . Vào mùa mưa thì khu vực trường có ngập và kẹt xe nhiều không a ?",
     [("Thảo Điền", "có ngập", "NEU")])
]

def apply_revisions():
    with open('data/validate_label/thuan/phase3.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    print(f"Loaded {len(lines)} lines from phase3.txt")

    for rec_id, text, trips in batch_5_8_revisions:
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
