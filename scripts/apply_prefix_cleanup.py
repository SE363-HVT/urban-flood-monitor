import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

new_lines = list(lines)

# 1. Rec 1616 (index 1615)
# Old: Triều cường ở TPHCM TPHCM 5 / 12 đạt đỉnh xấp xỉ 1 , 8m . Nguy cơ ngập úng đô thị diện rộng . # xuhuong # tintuc # trieucuongtphcm # tphcmngaymua
t1616 = lines[1615].split('####')[0]
t1616_new = t1616.replace('Triều cường ở TPHCM TPHCM 5 / 12', 'Triều cường ở TPHCM 5 / 12')
# Old trip: [([0, 1, 2, 3], [8, 9], 'NEU')]
# Old token [8, 9] was "đạt đỉnh", in new text it is at [7, 8]
tr1616_new = [([0, 1, 2, 3], [7, 8], 'NEU')]
new_lines[1615] = f"{t1616_new}####{tr1616_new}"

# 2. Rec 1669 (index 1668)
# Old: Hôm nay , ngày 6 / 12 triều cường ở TPHCM ở TPHCM đạt đỉnh 1 , 85m , nguy cơ ngập sâu nhiều nơi 🌊
t1669 = lines[1668].split('####')[0]
t1669_new = t1669.replace('triều cường ở TPHCM ở TPHCM đạt đỉnh', 'triều cường ở TPHCM đạt đỉnh')
# Old trip: [([7, 8, 9, 10], [13, 14], 'NEU')]
# In new text: [7, 8, 9, 10] = "triều cường ở TPHCM", [11, 12] = "đạt đỉnh"
tr1669_new = [([7, 8, 9, 10], [11, 12], 'NEU')]
new_lines[1668] = f"{t1669_new}####{tr1669_new}"

# 3. Rec 1892 (index 1891)
# Old: Tại TP. Hồ Chí Minh , TP. HỒ CHÍ MINH NGẬP SÂU DO TRIỀU CƯỜNG ĐẠT ĐỈNH Khoảng 17 - 18 giờ chiều tối nay ( 13 / 9 / 2026 ) , triều cường tại TP. Hồ Chí Minh đã đạt đỉnh của đợt đầu tháng 8 âm lịch . - Triều cường lên đúng vào giờ cao điểm buổi chiều lại kết hợp với mưa rào n
t1892 = lines[1891].split('####')[0]
t1892_new = t1892[len('Tại TP. Hồ Chí Minh , '):]
# Old trip: [([6, 7, 8, 9], [10, 11], 'NEG')]
# New trip shifted by -6: [([0, 1, 2, 3], [4, 5], 'NEG')]
tr1892_new = [([0, 1, 2, 3], [4, 5], 'NEG')]
new_lines[1891] = f"{t1892_new}####{tr1892_new}"

# 4. Rec 1961 (index 1960)
# Old: Tại TPHCM , TPHCM : Bất lực dắt bộ qua " biển nước " giờ tan làm vì xe c . h . ế . t m . á . y la liệt . Cơn mưa tầm tã trút xuống khiến hàng loạt tuyến đường ngập sâu kỷ lục , giao thông rối loạn tột độ . Chi tiết cảnh ngập lụt kinh hoàng và cảnh báo thời tiết đêm nay ở ngay dưới bình l
t1961 = lines[1960].split('####')[0]
t1961_new = t1961[len('Tại TPHCM , '):]
# Old trip: [([1], [45, 46], 'NEG')] -> token [1] was TPHCM in prefix, token [45, 46] was "ngập sâu"
# New trip shifted by -3: aspect [0] ("TPHCM"), opinion [42, 43] ("ngập sâu")
tr1961_new = [([0], [42, 43], 'NEG')]
new_lines[1960] = f"{t1961_new}####{tr1961_new}"

# 5. Rec 788 (index 787)
# Old: Tại TPHCM , Đoạn từ gần châu cầu Sài Gòn đến đến gần tòa nhà The Marnor khoảng 300 m có nhiều lô cốt công trình , mặt đường bị thu hẹp khiến người dân khó khăn hơn khi vượt qua " rốn ngập " .
t788 = lines[787].split('####')[0]
t788_new = t788[len('Tại TPHCM , '):]
toks788 = t788_new.split()
# Find "cầu Sài Gòn" in toks788
# "châu cầu Sài Gòn" -> [4, 5, 6] = "cầu Sài Gòn"
# opinion: "khó khăn hơn khi vượt qua \" rốn ngập \"" -> tokens 30..39
# or "rốn ngập" -> tokens [38, 39]
# Let's inspect tokens for 788
for i, tk in enumerate(toks788):
    if tk in ['cầu', 'Sài', 'Gòn', 'khó', 'khăn', 'rốn', 'ngập']:
        pass
tr788_new = [([4, 5, 6], [30, 31, 32, 33, 34, 35, 36, 37, 38, 39], 'NEG')]
new_lines[787] = f"{t788_new}####{tr788_new}"

# 6. Rec 1234 (index 1233)
# Old: Tại TPHCM , Qua kiểm tra toàn bộ nước của hẻm này đều thoát ra rạch Đĩa , đoạn cuối tuyến có khoảng 15m cống bị nghẹt nên dẫn đến tình trạng ngập .
t1234 = lines[1233].split('####')[0]
t1234_new = t1234[len('Tại TPHCM , '):]
# tokens: "rạch Đĩa" = [11, 12], "ngập" = [29]
tr1234_new = [([11, 12], [29], 'NEG')]
new_lines[1233] = f"{t1234_new}####{tr1234_new}"

# 7. Remaining 56 records from the 59 list (excluding 1892 which is already handled above)
recs_to_shift = [
    1, 2, 16, 27, 40, 41, 43, 46, 47, 49, 93, 99, 100, 124, 139, 144, 359, 375, 393, 460,
    513, 521, 851, 862, 880, 897, 917, 1000, 1017, 1019, 1040, 1099, 1109, 1129, 1150, 1160,
    1166, 1218, 1227, 1256, 1277, 1349, 1387, 1430, 1432, 1445, 1459, 1527, 1568, 1570, 1594,
    1626, 1648, 1812, 1851, 1889, 1944, 1966
]

for r in recs_to_shift:
    idx = r - 1
    t, tr = lines[idx].split('####')
    triplets = ast.literal_eval(tr)
    
    if t.startswith('Tại TP. Hồ Chí Minh , '):
        pfx = 'Tại TP. Hồ Chí Minh , '
        shift = 6
    elif t.startswith('Tại TPHCM , '):
        pfx = 'Tại TPHCM , '
        shift = 3
    else:
        continue
        
    t_new = t[len(pfx):]
    new_tr = []
    
    # Special handle for 1160 and 1218 (Aspect was "Thủ Đức là" due to 1 token offset)
    if r == 1160:
        # "chợ Thủ Đức" = [12, 13, 14], opinion = [5, 6, 7, 8] ("giải quyết giảm ngập")
        new_tr = [([12, 13, 14], [5, 6, 7, 8], 'POS')]
    elif r == 1218:
        # "chợ Thủ Đức" = [13, 14, 15], opinion = [6, 7, 8, 9] ("giải quyết giảm ngập")
        new_tr = [([13, 14, 15], [6, 7, 8, 9], 'POS')]
    elif r in [359, 375, 393, 513]:
        # Keep only the body triplet
        for asp, opi, pol in triplets:
            if not all(i < shift for i in asp):
                new_tr.append(([i - shift for i in asp], [i - shift for i in opi], pol))
    else:
        for asp, opi, pol in triplets:
            if all(i < shift for i in asp):
                continue
            new_tr.append(([i - shift for i in asp], [i - shift for i in opi], pol))
            
    new_lines[idx] = f"{t_new}####{new_tr}"

# Write to temp file for verification
with open('data/validate_label/thuan/phase2_test.txt', 'w', encoding='utf-8') as f:
    for l in new_lines:
        f.write(l + '\n')

print(f"Created phase2_test.txt with {len(new_lines)} lines.")
