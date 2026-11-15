import sys
import os
import ast

sys.stdout.reconfigure(encoding='utf-8')

# Read current phase2.txt
with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Total lines in phase2.txt: {len(lines)}")

# We will construct audited_batch1 (records 1 to 100)
audited_batch1 = []

# Helper to verify a reconstructed line
def make_line(text, triplets):
    tokens = text.split()
    for a, o, p in triplets:
        assert p in ('POS', 'NEU', 'NEG'), f"Bad pol {p}"
        assert a == list(range(a[0], a[-1] + 1)), f"Non-contig aspect {a}"
        assert o == list(range(o[0], o[-1] + 1)), f"Non-contig opinion {o}"
        assert a[-1] < len(tokens) and a[0] >= 0, f"Aspect OOB {a} len {len(tokens)}"
        assert o[-1] < len(tokens) and o[0] >= 0, f"Opinion OOB {o} len {len(tokens)}"
    return f"{text}####{triplets}"

# Let's inspect each line 0..99
for idx in range(100):
    line = lines[idx]
    rec_num = idx + 1
    parts = line.split('####')
    text = parts[0].strip()
    trips = ast.literal_eval(parts[1].strip())
    tokens = text.split()

    if rec_num == 1:
        # In-place "ở TPHCM" for triều cường:
        # text: Tại TP. Hồ Chí Minh , Chiều tối 28 / 9 , triều cường đạt đỉnh ...
        # tokens: [12, 13] is triều cường. Insert 'ở', 'TPHCM' after token 13.
        toks = text.split()
        toks.insert(14, 'ở')
        toks.insert(15, 'TPHCM')
        new_text = ' '.join(toks)
        # [12, 13, 14, 15] is triều cường ở TPHCM
        # đạt đỉnh is [16, 17]
        # Lê Văn Lương was [25, 26, 27] -> [27, 28, 29]
        # Trần Xuân Soạn was [29, 30, 31] -> [31, 32, 33]
        # Nguyễn Hữu Thọ was [33, 34, 35] -> [35, 36, 37]
        # opinion was [37..49] -> [39..51]
        new_trips = [
            ([27, 28, 29], list(range(39, 52)), 'NEG'),
            ([31, 32, 33], list(range(39, 52)), 'NEG'),
            ([35, 36, 37], list(range(39, 52)), 'NEG'),
            ([12, 13, 14, 15], [16, 17], 'NEU')
        ]
        audited_batch1.append(make_line(new_text, new_trips))

    elif rec_num == 2:
        # In-place "ở TPHCM" for triều cường:
        # text: Tại TP. Hồ Chí Minh , Chiều tối nay TPHCM có thể mưa , triều cường gây ngập ...
        # TPHCM [9] | có thể mưa [10, 11, 12]
        # triều cường was [14, 15]. Insert 'ở', 'TPHCM'
        toks = text.split()
        toks.insert(16, 'ở')
        toks.insert(17, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [14, 15, 16, 17]
        # gây ngập: causative 'gây' at 18 stripped, 'ngập' at 19
        new_trips = [
            ([9], [10, 11, 12], 'NEU'),
            ([14, 15, 16, 17], [19], 'NEU')
        ]
        audited_batch1.append(make_line(new_text, new_trips))

    elif rec_num == 3:
        # Saigon có những chiều mưa xe giăng ngập lối , k phải đứng yên mà chậm lại giữa dòng hối hả cuộc đời # quatangcuocsong
        # Philosophical meme / metaphorical -> REJECT
        audited_batch1.append(f"{text}####[]")

    elif rec_num == 4:
        # In-place "ở TPHCM" for triều cường:
        # Chiều nay , TPHCM và miền Tây đối mặt đợt triều cường cao nhất từ đầu năm . Nhiều khu vực có nguy cơ ngập sâu , ảnh hưởng việc đi lại . ...
        toks = text.split()
        toks.insert(12, 'ở')
        toks.insert(13, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [10, 11, 12, 13]
        # cao nhất từ đầu năm is [14, 15, 16, 17, 18]
        # TPHCM is [3] | có nguy cơ ngập sâu , ảnh hưởng việc đi lại was [21..31] -> [23..33]
        new_trips = [
            ([3], list(range(23, 34)), 'NEU'),
            ([10, 11, 12, 13], list(range(14, 19)), 'NEU')
        ]
        audited_batch1.append(make_line(new_text, new_trips))

    elif rec_num == 5:
        # REJECT
        audited_batch1.append(f"{text}####[]")

    elif rec_num == 6:
        # Sáng 28 - 9 , trên tuyến đường Rạch Cùng thuộc phường Bình Đông , TP. HCM triều cường lên cao , khiến nơi đây bị ngập . Bên cạnh đó tại đường Đặng Thùy Trâm thuộc phường Bình Thạnh , nước tràn lên mặt đường , ảnh hưởng đến việc đi lại của người dân . # tuoitre # tiktok # baotuoitre # tiktoktuoitre
        # Remove multi-level duplication: phường Bình Đông, phường Bình Thạnh
        # Remove bare triều cường
        new_trips = [
            ([7, 8, 9], [25, 26], 'NEG'),
            ([32, 33, 34, 35], list(range(41, 56)), 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 7:
        # Đợt triều cường rằm tháng Tám ...
        # Remove xã Hiệp Phước (qualifier in parens of Nguyễn Bình)
        new_trips = [
            ([64, 65, 66, 67], list(range(51, 55)), 'NEG'),  # đường Lê Văn Lương | tràn qua mặt đường
            ([69, 70], list(range(51, 55)), 'NEG'),          # Nguyễn Bình | tràn qua mặt đường
            ([77, 78, 79], list(range(51, 55)), 'NEG'),      # Phạm Hữu Lầu | tràn qua mặt đường
            ([184, 185], list(range(189, 200)), 'NEU'),      # Phú An | dự báo đạt từ 1 , 6 đến 1 , 65m
            ([187, 188], list(range(189, 200)), 'NEU'),      # Nhà Bè | dự báo đạt từ 1 , 6 đến 1 , 65m
            ([213, 214, 215], list(range(216, 224)), 'NEU')  # Thủ Dầu Một | có thể vượt báo động 3 tới 25cm
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 8:
        # REJECT
        audited_batch1.append(f"{text}####[]")

    elif rec_num == 9:
        # Triều cường ở TPHCM tiếp tục lên , nhiều nơi có thể ngập sâu trên 30 cm | VTVWDB
        new_trips = [
            ([0, 1, 2, 3], list(range(12, 17)), 'NEU')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 10:
        # Triều cường ở TPHCM lên cao ngập lụt ở Nam Bộ ...
        # Combine contiguous opinion: lên cao ngập lụt [4, 5, 6, 7]
        new_trips = [
            ([0, 1, 2, 3], [4, 5, 6, 7], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 11:
        # Tại TP. Hồ Chí Minh , Chiều tối 30 / 09 , ngập khắp nơi ! !
        new_trips = [
            ([1, 2, 3, 4], [12, 13, 14], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 12:
        # Đường Phan Huy Ích Gò Vấp . Anh em nhớ né lúc trời mưa to tránh ngập nha AE 👌 👌
        # Remove Gò Vấp (multi-level duplication)
        new_trips = [
            ([0, 1, 2, 3], [15, 16], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 13:
        # Nhiều xe tắt máy , nước dâng lên hơn nửa bánh xe . Ghi nhận tại đường Nguyễn Văn Quá , Phường Đông Hưng Thuận , TP. HCM .
        # Remove Phường Đông Hưng Thuận (multi-level duplication)
        new_trips = [
            ([16, 17, 18, 19], list(range(5, 12)), 'NEG'),
            ([16, 17, 18, 19], [0, 1, 2, 3], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 14:
        # Mưa lớn tại TP. Hồ Chí Minh vào chiều 30 / 9 khiến nhiều tuyến phố ngập sâu . Nước dâng cao , chảy cuồn cuộn khiến người dân di chuyển vô cùng khó khăn . Địa điểm : Đường Nguyễn Văn Quá
        # Remove redundant [23, 24, 25] (chảy cuồn cuộn)
        new_trips = [
            ([39, 40, 41, 42], [16, 17], 'NEG'),
            ([39, 40, 41, 42], list(range(19, 35)), 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 15:
        # Vấn nạn triều cường khu Nam Sài Gòn ... Liệu rằng tuyến đường Lê Văn Lương có ngập không ?
        # Text has: tuyến đường Lê Văn Lương [25..28]
        new_trips = [
            ([25, 26, 27, 28], [29, 30, 31], 'NEU'),
            ([4, 5, 6, 7], [0, 1, 2, 3], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 16:
        # Tại TP. Hồ Chí Minh , Cập nhật tình hình ngập bà con Thủ Đức ơi 😢
        new_trips = [
            ([13, 14], [8, 9, 10], 'NEU')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 17:
        # thành phố Hồ Chí Minh
        new_trips = [
            ([11, 12, 13, 14, 15], list(range(16, 22)), 'NEG'),
            ([11, 12, 13, 14, 15], [26, 27, 28], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 18:
        # Mưa Sài Gòn chiều nay . Đường vào nhà ngập sâu , đợi nước rút thì lâu nên chờ mãi cuối cùng quyết định để xe lại đặt Grap đi về và lội nước vào . Nước sâu tới gối , hầm xe thì nước tràn vào ngập 😔 😔
        # Stop narrative at comma: ngập sâu [9, 10]
        # Opinion 2: Nước sâu tới gối , hầm xe thì nước tràn vào ngập [36..47]
        # Remove redundant [44..47]
        new_trips = [
            ([1, 2], [9, 10], 'NEG'),
            ([1, 2], list(range(36, 48)), 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 19:
        # Bơm nước giải cứu nhiều vườn bưởi bị ngập ở xã Tân Vĩnh Lộc , TP. HCM 👇
        # Remove TP. HCM (multi-level duplication)
        new_trips = [
            ([10, 11, 12, 13], [7, 8], 'NEG'),
            ([10, 11, 12, 13], [0, 1, 2, 3], 'POS')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 20:
        # Triều cường TP. HCM lên đỉnh 1 , 65 m ...
        # Combine Triều cường TP. HCM [0, 1, 2, 3] | lên đỉnh 1 , 65 m [4..9] NEU
        new_trips = [
            ([0, 1, 2, 3], list(range(4, 10)), 'NEU'),
            ([60, 61, 62, 63], list(range(65, 78)), 'NEU')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 21:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 22:
        # Verbatim prefix:
        # đường Trường Chinh [95, 96, 97]
        # đường Tô Ngọc Vân [146, 147, 148, 149]
        new_trips = [
            ([95, 96, 97], list(range(114, 128)), 'NEG'),
            ([99, 100, 101], list(range(114, 128)), 'NEG'),
            ([103, 104, 105, 106, 107], list(range(114, 128)), 'NEG'),
            ([109, 110, 111, 112], list(range(114, 128)), 'NEG'),
            ([146, 147, 148, 149], list(range(157, 172)), 'NEG'),
            ([151, 152], list(range(157, 172)), 'NEG'),
            ([154, 155, 156], list(range(157, 172)), 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 23:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 24:
        # Bình tân tên lửa ngập quá ta 😂 # lulu # xuhuong # bìnhtantphcm
        # Remove Bình tân (multi-level duplication)
        new_trips = [
            ([2, 3], [4, 5], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 25:
        # Cập nhật tình hình đường Liên Khu 4 - 5 Bình Tân trưa 13h40 … vẫn ngập chưa rút nước ...
        # Remove Bình Tân (multi-level duplication)
        new_trips = [
            ([4, 5, 6, 7, 8, 9], list(range(15, 20)), 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 26:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 27:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 28:
        # In-place "ở TPHCM" for triều cường:
        # Trước nguy cơ mưa lớn , triều cường gây ngập đường , ảnh hưởng việc đi lại và an toàn của học sinh , các trường tại TP. Hồ Chí Minh có thể chủ động tổ chức học trực tuyến . ...
        toks = text.split()
        toks.insert(8, 'ở')
        toks.insert(9, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [6, 7, 8, 9]
        # gây ngập đường... : causative 'gây' at 10 stripped, 'ngập đường , ảnh hưởng việc đi lại và an toàn của học sinh' is [11..24]
        # Remove cross-sentence TP. Hồ Chí Minh
        new_trips = [
            ([6, 7, 8, 9], list(range(11, 25)), 'NEU')
        ]
        audited_batch1.append(make_line(new_text, new_trips))

    elif rec_num == 29:
        # Remove Thành Phố Hồ Chí Minh (multi-level duplication)
        new_trips = [
            ([7, 8, 9], [28, 29], 'NEG'),
            ([39, 40, 41], list(range(51, 58)), 'NEG'),
            ([45, 46], list(range(51, 58)), 'NEG'),
            ([48, 49, 50], list(range(51, 58)), 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 30:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 31:
        # Remove TP. Hồ Chí Minh (multi-level duplication with dự án)
        new_trips = [
            ([6, 7, 8, 9, 10, 11, 12], list(range(24, 32)), 'POS')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 32:
        # Remove Sài Gòn (multi-level duplication)
        new_trips = [
            ([3, 4, 5], [0, 1], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 33:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 34:
        # Remove TP. HCM (multi-level duplication)
        new_trips = [
            ([9, 10, 11, 12], [21, 22, 23], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 35:
        # Triều cường nước lên Xã Vĩnh Lộc . TPHCM ...
        # In-place "ở TPHCM" for Triều cường:
        toks = text.split()
        toks.insert(2, 'ở')
        toks.insert(3, 'TPHCM')
        new_text = ' '.join(toks)
        # Triều cường ở TPHCM is [0, 1, 2, 3] | nước lên is [4, 5] | NEG
        # Xã Vĩnh Lộc was [4, 5, 6] -> [6, 7, 8]
        # Remove TPHCM (multi-level duplication)
        # opinion was [26..37] -> [28..39]
        new_trips = [
            ([6, 7, 8], list(range(28, 40)), 'NEG'),
            ([0, 1, 2, 3], [4, 5], 'NEG')
        ]
        audited_batch1.append(make_line(new_text, new_trips))

    elif rec_num == 36:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 37:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 38:
        # Remove Tân Bình, TP. HCM (multi-level duplication)
        new_trips = [
            ([12, 13, 14], [10], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 39:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 40:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 41:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 42:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 43:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 44:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 45:
        # Remove Bình Thạnh (multi-level duplication)
        new_trips = [
            ([18], [15, 16], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 46:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 47:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 48:
        # Một đêm không ngủ của người dân vùng ngập ở TPHCM
        # Title of news: Một đêm không ngủ [0, 1, 2, 3, 4] | NEG
        new_trips = [
            ([10], [0, 1, 2, 3, 4], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 49:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 50:
        # Remove duplicate ùn tắc
        new_trips = [
            ([69], list(range(20, 24)), 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 51:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 52:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 53:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 54:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 55 or rec_num == 56 or rec_num == 57:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 58:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 59:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 60:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 61:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 62:
        # Rooftop home gardening clip (#Lamvuon #trongrausach #trongrausanthuong) -> REJECT
        audited_batch1.append(f"{text}####[]")

    elif rec_num == 63:
        # Remove Sài Gòn (multi-level duplication)
        new_trips = [
            ([14, 15], [16, 17], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 64:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 65:
        # Verbatim prefix: đường Tam Bình [19, 20, 21]
        new_trips = [
            ([19, 20, 21], [28, 29], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 66:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 67:
        # TP. HCM hứng đợt mưa lớn kéo dài 6 ngày , có nơi được dự báo trên 250 mm , cảnh báo ngập nhiều khu vực # tiktoknews # saigonbiz
        # Token 20 is cảnh, 21 is báo, 22 is ngập
        # opinion: cảnh báo ngập [20, 21, 22] | NEU
        new_trips = [
            ([0, 1], [20, 21, 22], 'NEU')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 68:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 69:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 70:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 71:
        # Remove Gò Vấp (multi-level duplication)
        new_trips = [
            ([0, 1, 2], list(range(6, 10)), 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 72:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 73:
        # đường Phan Huy Ích [26, 27, 28, 29]
        # phường Thủ Đức [31, 32, 33]
        new_trips = [
            ([26, 27, 28, 29], list(range(37, 54)), 'NEG'),
            ([31, 32, 33], list(range(37, 54)), 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 74:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 75:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 76:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 77:
        # phường Thủ Đức [11, 12, 13]
        new_trips = [
            ([11, 12, 13], [3, 4], 'NEG'),
            ([11, 12, 13], [20, 21, 22], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 78:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 79:
        # Remove Bình thạnh (multi-level duplication)
        new_trips = [
            ([0, 1, 2, 3], list(range(8, 12)), 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 80:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 81:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 82:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 83:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 84:
        # Remove TPHCM (multi-level duplication)
        new_trips = [
            (list(range(7, 16)), [0, 1], 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 85:
        # đường Phan Huy Ích [7, 8, 9, 10]
        # Remove redundant [17, 18, 19]
        new_trips = [
            ([7, 8, 9, 10], list(range(14, 40)), 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 86:
        audited_batch1.append(f"{text}####[]")

    elif rec_num == 87:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 88:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 89:
        # Rooftop home gardening clip (#Lamvuon #trongrausach #trongrausanthuong) -> REJECT
        audited_batch1.append(f"{text}####[]")

    elif rec_num == 90:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 91:
        # Prepend fallback: Tại TPHCM ,
        new_text = "Tại TPHCM , " + text
        # Tokens: Tại (0), TPHCM (1), , (2)
        # aspect: TPHCM [1]
        # ngập nước was [7, 8] -> [10, 11]
        new_trips = [
            ([1], [10, 11], 'NEG')
        ]
        audited_batch1.append(make_line(new_text, new_trips))

    elif rec_num == 92:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 93:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 94:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 95:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 96:
        # Clean opinion:
        # [3, 4, 5] Đường Mã Lò | ngập sau mưa lớn , nhiều xe chết máy [9..17] NEG
        # [22, 23, 24] đường Mã Lò | ngập nước sau mưa lớn [31..35] NEG
        new_trips = [
            ([3, 4, 5], list(range(9, 18)), 'NEG'),
            ([22, 23, 24], list(range(31, 36)), 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 97:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 98:
        # Remove phường Thủ Đức, TP. HCM (multi-level duplication)
        new_trips = [
            ([7, 8, 9], [18, 19], 'NEG'),
            ([7, 8, 9], list(range(21, 28)), 'NEG')
        ]
        audited_batch1.append(make_line(text, new_trips))

    elif rec_num == 99:
        audited_batch1.append(make_line(text, trips))

    elif rec_num == 100:
        audited_batch1.append(make_line(text, trips))

print(f"Audited batch 1 count: {len(audited_batch1)}")

# Save updated phase2.txt with audited_batch1 replacing first 100 lines
updated_lines = audited_batch1 + lines[100:]
assert len(updated_lines) == len(lines), f"Line count mismatch {len(updated_lines)} vs {len(lines)}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in updated_lines:
        f.write(l + '\n')

print("Successfully written audited Batch 1 to data/validate_label/thuan/phase2.txt!")
