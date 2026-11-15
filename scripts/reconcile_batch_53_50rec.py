import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = [line.rstrip('\r\n') for line in f]

corrections = {
    # 1881 (idx 1880): Nhiều đường TP HCM ngập sâu
    1880: [([2, 3], [4, 5], 'NEG')],

    # 1884 (idx 1883): Tại TPHCM , Mong 1 ngày nào đó Việt Nam mình sẽ không còn ngập khi mưa to nữa
    1883: [([1], [12, 13, 14], 'POS')],

    # 1885 (idx 1884): đỉnh triều ở TPHCM sông Sài Gòn... làm gia tăng nguy cơ ngập úng
    1884: [([43], [61, 62, 63, 64], 'NEU'), ([44, 45, 46], [61, 62, 63, 64], 'NEU')],

    # 1889 (idx 1888): Bình Thạnh hay ngập (tránh lạm dụng fallback TPHCM)
    1888: [([24, 25], [26, 27], 'NEG')],

    # 1893 (idx 1892): Sài Gòn... đường vẫn ngập lênh láng
    1892: [([1, 2], [32, 33, 34], 'NEG')],

    # 1897 (idx 1896): đường Tô Ngọc Vân bị ngập... (bỏ bị, bỏ comma)
    1896: [([3, 4, 5, 6], [32], 'NEG')],

    # 1902 (idx 1901): đường TPHCM ngập cục bộ (sửa ngập cục -> ngập cục bộ)
    1901: [([11], [12, 13, 14], 'NEG')],

    # 1903 (idx 1902): đường TPHCM ngập nước (chuẩn hóa entity TPHCM)
    1902: [([6], [7, 8], 'NEG')],

    # 1904 (idx 1903): đường TPHCM kẹt xe , ngập nước
    1903: [([6], [10, 11], 'NEG')],

    # 1905 (idx 1904): nhiều khu vực ở TPHCM ngập sâu (sửa lệch token 'vực ở' | 'TPHCM ngập')
    1904: [([26], [27, 28], 'NEG')],

    # 1906 (idx 1905): cầu Ba Son ngập luôn (sửa lệch token 'Ba Son ngập' | 'luôn')
    1905: [([8, 9, 10], [11], 'NEG')],

    # 1908 (idx 1907): Quảng cáo thương mại sửa chữa pin iPhone 11 -> REJECT
    1907: [],

    # 1909 (idx 1908): NÓNG ! BÀ CON TP. HCM CHÚ Ý ! ... CÓ NGUY CƠ NGẬP (sửa 'SÔNG CÓ NGUY CƠ' -> 'CÓ NGUY CƠ NGẬP')
    1908: [([4, 5], [19, 20, 21, 22], 'NEU')],

    # 1910 (idx 1909): TP. HCM... nguy cơ ngập úng tăng cao (sửa NEG -> NEU cảnh báo dự báo)
    1909: [([7, 8], [20, 21, 22, 23, 24, 25], 'NEU')],

    # 1911 (idx 1910): xe máy dắt bộ đường Phạm Hữu Lầu (sửa lệch index 'bộ đường Phạm Hữu' | 'máy dắt')
    1910: [([10, 11, 12, 13], [8, 9], 'NEG')],

    # 1912 (idx 1911): đường Hồ Học Lãm ( phường An Lạc , TPHCM ) vẫn còn ngập sâu (sửa 'vẫn còn' -> 'ngập sâu')
    1911: [([21, 22, 23, 24], [34, 35], 'NEG'), ([26, 27, 28], [34, 35], 'NEG')],

    # 1917 (idx 1916): TPHCM bị ngập , gây khó khăn... (bỏ bị, bỏ câu phụ)
    1916: [([20], [22], 'NEG')],

    # 1920 (idx 1919): TPHCM bị ngập , gây khó khăn...
    1919: [([13], [15], 'NEG')],

    # 1921 (idx 1920): Dự đoán mưa vần vè meme hài hước -> REJECT
    1920: [],

    # 1922 (idx 1921): CẢNH BÁO TRIỀU CƯỜNG ở TPHCM KHU VỰC SÔNG SÀI GÒN (bỏ giới từ 'ở' trong aspect)
    1921: [([6], [1, 2, 3, 4], 'NEU'), ([9, 10, 11], [1, 2, 3, 4], 'NEU')],

    # 1924 (idx 1923): 'chết máy... đặc sản Sài Gòn' (không có thông tin ngập lụt) -> REJECT
    1923: [],

    # 1925 (idx 1924): Lê Văn Việt, Nguyễn Văn Hưởng... bị ngập (bỏ 'bị')
    1924: [
        ([36, 37, 38], [67], 'NEG'),
        ([40, 41, 42], [67], 'NEG'),
        ([44, 45], [67], 'NEG'),
        ([47, 48, 49], [67], 'NEG'),
        ([51, 52, 53], [67], 'NEG')
    ],

    # 1926 (idx 1925): TPHCM ngập sâu (rút gọn opinion nhiều mệnh đề)
    1925: [([33], [38, 39], 'NEG')],

    # 1927 (idx 1926): TPHCM ngập sâu (rút gọn opinion)
    1926: [([26], [27, 28], 'NEG')],

    # 1930 (idx 1929): TP. HCM... người dân chú ý ngập lụt (khuyến cáo dự báo -> NEU)
    1929: [([0, 1], [30, 31, 32, 33], 'NEU')]
}

count_updated = 0
for idx, new_triplets in corrections.items():
    old_line = lines[idx]
    text = old_line.split('####')[0].strip()
    new_line = f"{text}####{new_triplets}"
    if new_line != old_line:
        lines[idx] = new_line
        count_updated += 1
        tokens = text.split()
        print(f"Update Rec {idx+1} (idx {idx}):")
        print(f"  Old: {old_line.split('####')[1]}")
        print(f"  New: {new_triplets}")
        for t in new_triplets:
            print(f"    Asp: '{' '.join(tokens[x] for x in t[0])}' | Op: '{' '.join(tokens[x] for x in t[1])}' | Pol: {t[2]}")

with open(filepath, 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print(f"\n✅ ĐÃ HIỆU CHỈNH THÀNH CÔNG {count_updated} RECORDS TRONG LÔ 53!")
