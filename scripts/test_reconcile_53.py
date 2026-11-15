import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.rstrip('\r\n') for line in f]

# Let's inspect each line from 1880 to 1929
corrections = {}

# 1881 (idx 1880): Nhiều đường TP HCM ngập sâu...
# tokens[2, 3] = TP HCM, tokens[4, 5] = ngập sâu
corrections[1880] = [([2, 3], [4, 5], 'NEG')]

# 1884 (idx 1883): Tại TPHCM , Mong 1 ngày nào đó Việt Nam mình sẽ không còn ngập khi mưa to nữa
# tokens[1] = TPHCM, tokens[12, 13, 14] = không còn ngập -> POS!
corrections[1883] = [([1], [12, 13, 14], 'POS')]

# 1885 (idx 1884): đỉnh triều ở TPHCM sông Sài Gòn... làm gia tăng nguy cơ ngập úng
# tokens[43] = TPHCM, tokens[44, 45, 46] = sông Sài Gòn, tokens[61, 62, 63, 64] = nguy cơ ngập úng -> NEU
corrections[1884] = [([43], [61, 62, 63, 64], 'NEU'), ([44, 45, 46], [61, 62, 63, 64], 'NEU')]

# 1889 (idx 1888): Bình Thạnh hay ngập...
# tokens[24, 25] = Bình Thạnh, tokens[26, 27] = hay ngập -> NEG
corrections[1888] = [([24, 25], [26, 27], 'NEG')]

# 1893 (idx 1892): Sài Gòn... triều cường ở TPHCM... đường vẫn ngập lênh láng
# tokens[1, 2] = Sài Gòn, tokens[32, 33, 34] = ngập lênh láng -> NEG
corrections[1892] = [([1, 2], [32, 33, 34], 'NEG')]

# 1902 (idx 1901): đường TPHCM ngập cục bộ
# tokens[11] = TPHCM, tokens[12, 13, 14] = ngập cục bộ -> NEG
corrections[1901] = [([11], [12, 13, 14], 'NEG')]

# 1903 (idx 1902): đường TPHCM ngập nước
# tokens[6] = TPHCM, tokens[7, 8] = ngập nước -> NEG
corrections[1902] = [([6], [7, 8], 'NEG')]

# 1904 (idx 1903): đường TPHCM kẹt xe , ngập nước
# tokens[6] = TPHCM, tokens[10, 11] = ngập nước -> NEG
corrections[1903] = [([6], [10, 11], 'NEG')]

# 1905 (idx 1904): nhiều khu vực ở TPHCM ngập sâu
# tokens[26] = TPHCM, tokens[27, 28] = ngập sâu -> NEG
corrections[1904] = [([26], [27, 28], 'NEG')]

# 1906 (idx 1905): cầu Ba Son ngập luôn
# tokens[8, 9, 10] = cầu Ba Son, tokens[11] = ngập -> NEG
corrections[1905] = [([8, 9, 10], [11], 'NEG')]

# 1908 (idx 1907): Quảng cáo thay pin iPhone 11 -> REJECT
corrections[1907] = []

# 1909 (idx 1908): NÓNG ! BÀ CON TP. HCM CHÚ Ý ! ... VEN SÔNG CÓ NGUY CƠ NGẬP
# tokens[4, 5] = TP. HCM, tokens[19, 20, 21, 22] = CÓ NGUY CƠ NGẬP -> NEU
corrections[1908] = [([4, 5], [19, 20, 21, 22], 'NEU')]

# 1910 (idx 1909): TP. HCM... nguy cơ ngập úng tăng cao
# tokens[7, 8] = TP. HCM, tokens[20, 21, 22, 23, 24, 25] = nguy cơ ngập úng tăng cao -> NEU
corrections[1909] = [([7, 8], [20, 21, 22, 23, 24, 25], 'NEU')]

# 1911 (idx 1910): xe máy dắt bộ đường Phạm Hữu Lầu
# tokens[10, 11, 12, 13] = đường Phạm Hữu Lầu, tokens[8, 9] = dắt bộ -> NEG
corrections[1910] = [([10, 11, 12, 13], [8, 9], 'NEG')]

# 1912 (idx 1911): đường Hồ Học Lãm ( phường An Lạc , TPHCM ) vẫn còn ngập sâu
# tokens[21, 22, 23, 24] = đường Hồ Học Lãm, tokens[34, 35] = ngập sâu -> NEG
# tokens[26, 27, 28] = phường An Lạc, tokens[34, 35] = ngập sâu -> NEG
corrections[1911] = [([21, 22, 23, 24], [34, 35], 'NEG'), ([26, 27, 28], [34, 35], 'NEG')]

# 1897 (idx 1896): đường Tô Ngọc Vân bị ngập...
# tokens[3, 4, 5, 6] = đường Tô Ngọc Vân, tokens[32] = ngập -> NEG
corrections[1896] = [([3, 4, 5, 6], [32], 'NEG')]

# 1917 (idx 1916): TPHCM bị ngập , gây khó khăn cho việc đi lại
# tokens[20] = TPHCM, tokens[22] = ngập -> NEG
corrections[1916] = [([20], [22], 'NEG')]

# 1920 (idx 1919): TPHCM bị ngập , gây khó khăn cho việc đi lại
# tokens[13] = TPHCM, tokens[15] = ngập -> NEG
corrections[1919] = [([13], [15], 'NEG')]

# 1921 (idx 1920): Dự đoán tình hình mưa Sài Gòn... meme vần vè -> REJECT
corrections[1920] = []

# 1922 (idx 1921): CẢNH BÁO TRIỀU CƯỜNG ở TPHCM KHU VỰC SÔNG SÀI GÒN
# tokens[6] = TPHCM, tokens[1, 2, 3, 4] = CẢNH BÁO TRIỀU CƯỜNG -> NEU
# tokens[9, 10, 11] = SÔNG SÀI GÒN, tokens[1, 2, 3, 4] = CẢNH BÁO TRIỀU CƯỜNG -> NEU
corrections[1921] = [([6], [1, 2, 3, 4], 'NEU'), ([9, 10, 11], [1, 2, 3, 4], 'NEU')]

# 1924 (idx 1923): Con chiến mã của tui cũng phải chết máy... đặc sản Sài Gòn -> Không có thông tin ngập -> REJECT
corrections[1923] = []

# 1925 (idx 1924): Lê Văn Việt, Nguyễn Văn Hưởng... bị ngập -> bỏ bị
corrections[1924] = [
    ([36, 37, 38], [67], 'NEG'),
    ([40, 41, 42], [67], 'NEG'),
    ([44, 45], [67], 'NEG'),
    ([47, 48, 49], [67], 'NEG'),
    ([51, 52, 53], [67], 'NEG')
]

# 1926 (idx 1925): TPHCM ngập sâu
corrections[1925] = [([33], [38, 39], 'NEG')]

# 1927 (idx 1926): TPHCM ngập sâu
corrections[1926] = [([26], [27, 28], 'NEG')]

# 1930 (idx 1929): TP. HCM... người dân chú ý ngập lụt -> NEU
corrections[1929] = [([0, 1], [30, 31, 32, 33], 'NEU')]

print(f"Tổng số records được hiệu chỉnh: {len(corrections)} / 50")
