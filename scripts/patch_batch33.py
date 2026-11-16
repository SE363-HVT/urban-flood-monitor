# -*- coding: utf-8 -*-
with open('scripts/build_phase3_batch33.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Rec 3208
old_3208 = '''    # Rec 3208: Đã có đường Trần Xuân Soạn, quận 7
    ("Chiều 18 - 10 , triều cường dâng cao và đạt đỉnh , tuyến đường Trần Xuân Soạn , quận 7 , TP. HCM ngập nặng gây khó khăn cho người dân qua lại .", [
        ([13, 14, 15, 16], [24, 25], 'NEG'),
        ([13, 14, 15, 16], [26, 27], 'NEG'),
        ([18, 19], [24, 25], 'NEG'),
    ]),'''

new_3208 = '''    # Rec 3208: Đã có đường Trần Xuân Soạn, quận 7
    ("Chiều 18 - 10 , triều cường dâng cao và đạt đỉnh , tuyến đường Trần Xuân Soạn , quận 7 , TP. HCM ngập nặng gây khó khăn cho người dân qua lại .", [
        ([13, 14, 15, 16, 17], [24, 25], 'NEG'),
        ([13, 14, 15, 16, 17], [26, 27, 28], 'NEG'),
        ([19, 20], [24, 25], 'NEG'),
    ]),'''

# Fix Rec 3209
old_3209 = '''    # Rec 3209: Đã có TP. HCM
    ("Đây là 1 trong 8 tuyến đường thường xuyên ngập nặng do triều cường ở TP. HCM .", [
        ([16, 17], [8, 9, 10, 11], 'NEG'),
    ]),'''

new_3209 = '''    # Rec 3209: Đã có TP. HCM
    ("Đây là 1 trong 8 tuyến đường thường xuyên ngập nặng do triều cường ở TP. HCM .", [
        ([15, 16], [9, 10], 'NEG'),
    ]),'''

# Fix Rec 3213
old_3213 = '''    # Rec 3213: Đã có QUẬN 7, đường Trần Xuân Soạn, quận 7
    ("QUẬN 7 QUÁ QUEN : TRIỀU CƯỜNG LÊN ĐỈNH , NGƯỜI DÂN CHẬT VẬT LỘI NƯỚC VỀ NHÀ Chiều nay ( 18 / 10 ) , triều cường xuất hiện gây ngập đường Trần Xuân Soạn ( quận 7 ) đã khiến việc đi lại của người dân gặp nhiều trở ngại .", [
        ([0, 1], [11, 12, 13, 14], 'NEG'),
        ([33, 34, 35, 36], [31, 32], 'NEG'),
        ([38, 39], [31, 32], 'NEG'),
    ]),'''

new_3213 = '''    # Rec 3213: Đã có QUẬN 7, đường Trần Xuân Soạn, quận 7
    ("QUẬN 7 QUÁ QUEN : TRIỀU CƯỜNG LÊN ĐỈNH , NGƯỜI DÂN CHẬT VẬT LỘI NƯỚC VỀ NHÀ Chiều nay ( 18 / 10 ) , triều cường xuất hiện gây ngập đường Trần Xuân Soạn ( quận 7 ) đã khiến việc đi lại của người dân gặp nhiều trở ngại .", [
        ([0, 1], [12, 13, 14, 15], 'NEG'),
        ([32, 33, 34, 35], [31], 'NEG'),
        ([37, 38], [31], 'NEG'),
    ]),'''

# Fix Rec 3216
old_3216 = '''    # Rec 3216: Đã có TP. HCM
    ("Chiều 24 - 10 , triều cường tiếp tục dâng cao , khiến nhiều khu vực ở TP. HCM bị ngập .", [
        ([18, 19], [20, 21], 'NEG'),
    ]),'''

new_3216 = '''    # Rec 3216: Đã có TP. HCM
    ("Chiều 24 - 10 , triều cường tiếp tục dâng cao , khiến nhiều khu vực ở TP. HCM bị ngập .", [
        ([17, 18], [20], 'NEG'),
    ]),'''

# Fix Rec 3227
old_3227 = '''    # Rec 3227: Đã có Trần Xuân Soạn, Trần Trọng Cung, Nguyễn Thị Thập, Phạm Hữu Lầu, Quận 7
    ("Trần Xuân Soạn , Trần Trọng Cung , Nguyễn Thị Thập , Phạm Hữu Lầu . . . nói chung Quận 7 ngập ' từa lưa hột dưa ' ae lưu ý !", [
        ([0, 1, 2], [23], 'NEG'),
        ([4, 5, 6], [23], 'NEG'),
        ([8, 9, 10], [23], 'NEG'),
        ([12, 13, 14], [23], 'NEG'),
        ([21, 22], [23], 'NEG'),
    ]),'''

new_3227 = '''    # Rec 3227: Đã có Trần Xuân Soạn, Trần Trọng Cung, Nguyễn Thị Thập, Phạm Hữu Lầu, Quận 7
    ("Trần Xuân Soạn , Trần Trọng Cung , Nguyễn Thị Thập , Phạm Hữu Lầu . . . nói chung Quận 7 ngập ' từa lưa hột dưa ' ae lưu ý !", [
        ([0, 1, 2], [22], 'NEG'),
        ([4, 5, 6], [22], 'NEG'),
        ([8, 9, 10], [22], 'NEG'),
        ([12, 13, 14], [22], 'NEG'),
        ([20, 21], [22], 'NEG'),
    ]),'''

# Fix Rec 3230
old_3230 = '''    # Rec 3230: Đã có TP. HCM
    ("ĐƯỜNG PHỐ TP. HCM NGẬP LÊNH LÁNG SAU MƯA LỚN , NHIỀU XE CHẾT MÁY TRONG BIỂN NƯỚC Chiều tối 6 / 10 , cơn mưa lớn trút xuống một số nơi tại TP. HCM khiến nhiều tuyến đường ngập sâu .", [
        ([2, 3], [4, 5, 6], 'NEG'),
        ([2, 3], [12, 13], 'NEG'),
        ([35, 36], [40, 41], 'NEG'),
    ]),'''

new_3230 = '''    # Rec 3230: Đã có TP. HCM
    ("ĐƯỜNG PHỐ TP. HCM NGẬP LÊNH LÁNG SAU MƯA LỚN , NHIỀU XE CHẾT MÁY TRONG BIỂN NƯỚC Chiều tối 6 / 10 , cơn mưa lớn trút xuống một số nơi tại TP. HCM khiến nhiều tuyến đường ngập sâu .", [
        ([2, 3], [4, 5, 6], 'NEG'),
        ([2, 3], [13, 14], 'NEG'),
        ([33, 34], [39, 40], 'NEG'),
    ]),'''

# Fix Rec 3243
old_3243 = '''    # Rec 3243: Đã có TP. HCM, quận Bình Thạnh
    ("Người dân TP. HCM dắt bộ xe máy đi làm trong mưa lớn Sáng 25 / 5 , mưa lớn khiến nhiều khu vực tại quận Bình Thạnh ( TP. HCM ) ngập nặng .", [
        ([2, 3], [4, 5, 6, 7], 'NEG'),
        ([24, 25, 26], [32, 33], 'NEG'),
    ]),'''

new_3243 = '''    # Rec 3243: Đã có TP. HCM, quận Bình Thạnh
    ("Người dân TP. HCM dắt bộ xe máy đi làm trong mưa lớn Sáng 25 / 5 , mưa lớn khiến nhiều khu vực tại quận Bình Thạnh ( TP. HCM ) ngập nặng .", [
        ([2, 3], [4, 5, 6, 7], 'NEG'),
        ([25, 26, 27], [32, 33], 'NEG'),
    ]),'''

# Fix Rec 3248
old_3248 = '''    # Rec 3248: Dự báo đỉnh triều tương lai -> NEU (Pass 8)
    ("TP. HCM sắp đón đỉnh triều cường cao nhất năm Dự báo đỉnh triều cường đợt rằm tháng 10 âm lịch tại TP. HCM có khả năng cao nhất năm , xuất hiện vào ngày 27 - 29 / 11 ở mức từ 1 , 7 - 1 , 75m gây ngập úng vùng trũng thấp , ven sông .", [
        ([0, 1], [50, 51], 'NEU'),
        ([21, 22], [50, 51], 'NEU'),
    ]),'''

new_3248 = '''    # Rec 3248: Dự báo đỉnh triều tương lai -> NEU (Pass 8)
    ("TP. HCM sắp đón đỉnh triều cường cao nhất năm Dự báo đỉnh triều cường đợt rằm tháng 10 âm lịch tại TP. HCM có khả năng cao nhất năm , xuất hiện vào ngày 27 - 29 / 11 ở mức từ 1 , 7 - 1 , 75m gây ngập úng vùng trũng thấp , ven sông .", [
        ([0, 1], [50, 51, 52], 'NEU'),
        ([22, 23], [50, 51, 52], 'NEU'),
    ]),'''

# Fix Rec 3249
old_3249 = '''    # Rec 3249: Khuyên đề phòng ngập úng, Fallback 'Tại TPHCM , ' -> NEU (Pass 8)
    ("Tại TPHCM , “ Đây là kỳ triều cường cao , cần đề phòng ngập úng những vùng trũng thấp và ven sông .", [
        ([1], [10, 11, 12, 13], 'NEU'),
    ]),'''

new_3249 = '''    # Rec 3249: Khuyên đề phòng ngập úng, Fallback 'Tại TPHCM , ' -> NEU (Pass 8)
    ("Tại TPHCM , “ Đây là kỳ triều cường cao , cần đề phòng ngập úng những vùng trũng thấp và ven sông .", [
        ([1], [11, 12, 13, 14, 15], 'NEU'),
    ]),'''

# Fix Rec 3250
old_3250 = '''    # Rec 3250: Dự báo các tuyến đường có khả năng bị ngập -> NEU (Pass 8)
    ("Một vài tuyến đường có khả năng bị ngập , như : đường Trần Xuân Soạn , Đào Sư Tích , Huỳnh Tấn Phát , Nguyễn Bình , Lê Văn Lương , Quốc lộ 50 , Phạm Hữu Lầu .", [
        ([11, 12, 13, 14], [4, 5, 6, 7, 8], 'NEU'),
        ([16, 17, 18], [4, 5, 6, 7, 8], 'NEU'),
        ([20, 21, 22], [4, 5, 6, 7, 8], 'NEU'),
        ([24, 25], [4, 5, 6, 7, 8], 'NEU'),
        ([27, 28, 29], [4, 5, 6, 7, 8], 'NEU'),
        ([31, 32, 33], [4, 5, 6, 7, 8], 'NEU'),
        ([35, 36, 37], [4, 5, 6, 7, 8], 'NEU'),
    ]),'''

new_3250 = '''    # Rec 3250: Dự báo các tuyến đường có khả năng bị ngập -> NEU (Pass 8)
    ("Một vài tuyến đường có khả năng bị ngập , như : đường Trần Xuân Soạn , Đào Sư Tích , Huỳnh Tấn Phát , Nguyễn Bình , Lê Văn Lương , Quốc lộ 50 , Phạm Hữu Lầu .", [
        ([12, 13, 14, 15], [4, 5, 6, 7, 8], 'NEU'),
        ([17, 18, 19], [4, 5, 6, 7, 8], 'NEU'),
        ([21, 22, 23], [4, 5, 6, 7, 8], 'NEU'),
        ([25, 26], [4, 5, 6, 7, 8], 'NEU'),
        ([28, 29, 30], [4, 5, 6, 7, 8], 'NEU'),
        ([32, 33, 34], [4, 5, 6, 7, 8], 'NEU'),
        ([36, 37, 38], [4, 5, 6, 7, 8], 'NEU'),
    ]),'''

# Fix Rec 3256
old_3256 = '''    # Rec 3256: Đã có THỦ ĐỨC, Thủ Đức
    ("NHỮNG TUYẾN ĐƯỜNG CẦN TRÁNH Ở THỦ ĐỨC KHI MƯA LỚN 🌧 Vào mùa mưa , tình trạng ngập nước ở Thủ Đức là điều không thể tránh khỏi .", [
        ([6, 7], [15, 16], 'NEG'),
        ([18, 19], [15, 16], 'NEG'),
    ]),'''

new_3256 = '''    # Rec 3256: Đã có THỦ ĐỨC, Thủ Đức
    ("NHỮNG TUYẾN ĐƯỜNG CẦN TRÁNH Ở THỦ ĐỨC KHI MƯA LỚN 🌧 Vào mùa mưa , tình trạng ngập nước ở Thủ Đức là điều không thể tránh khỏi .", [
        ([6, 7], [16, 17, 18, 19], 'NEG'),
        ([21, 22], [16, 17, 18, 19], 'NEG'),
    ]),'''

# Fix Rec 3264
old_3264 = '''    # Rec 3264: Đã có TPHCM
    ("‼ ️ TPHCM : ĐƯỜNG LẠI BIẾN THÀNH SÔNG SAU MƯA 🌧 Trưa 12 / 5 , tại một số quận , huyện của TPHCM tiếp tục có mưa to , nhiều điểm ngập do nước không rút kịp , gây ách tắc giao thông .", [
        ([2], [4, 5, 6, 7, 8], 'NEG'),
        ([21], [35, 36, 37, 38], 'NEG'),
    ]),'''

new_3264 = '''    # Rec 3264: Đã có TPHCM
    ("‼ ️ TPHCM : ĐƯỜNG LẠI BIẾN THÀNH SÔNG SAU MƯA 🌧 Trưa 12 / 5 , tại một số quận , huyện của TPHCM tiếp tục có mưa to , nhiều điểm ngập do nước không rút kịp , gây ách tắc giao thông .", [
        ([2], [4, 5, 6, 7, 8], 'NEG'),
        ([24], [40, 41, 42, 43, 44], 'NEG'),
    ]),'''

# Fix Rec 3273
old_3273 = '''    # Rec 3273: Đã có TP Thủ Đức, quận Bình Thạnh
    ("Đường TP HCM ngập nửa mét sau mưa lớn Cơn mưa kéo dài khiến nhiều đường ở TP Thủ Đức , quận Bình Thạnh , ngập sâu nửa mét , người dân bì bõm đẩy , dắt xe chết máy về nhà , chiều 1 / 10 .", [
        ([18, 19, 20], [26, 27, 28, 29], 'NEG'),
        ([18, 19, 20], [38, 39], 'NEG'),
        ([22, 23, 24], [26, 27, 28, 29], 'NEG'),
    ]),'''

new_3273 = '''    # Rec 3273: Đã có TP Thủ Đức, quận Bình Thạnh
    ("Đường TP HCM ngập nửa mét sau mưa lớn Cơn mưa kéo dài khiến nhiều đường ở TP Thủ Đức , quận Bình Thạnh , ngập sâu nửa mét , người dân bì bõm đẩy , dắt xe chết máy về nhà , chiều 1 / 10 .", [
        ([17, 18, 19], [25, 26, 27, 28], 'NEG'),
        ([17, 18, 19], [38, 39], 'NEG'),
        ([21, 22, 23], [25, 26, 27, 28], 'NEG'),
    ]),'''

# Fix Rec 3276
old_3276 = '''    # Rec 3276: Đã có đường Bùi Bằng Đoàn, Phú Mỹ Hưng, quận 7
    ("Cơn mưa lớn chiều tối ngày 27 / 5 tại TPHCM đã gây ra tình trạng ngập úng trên tuyến đường Bùi Bằng Đoàn , khu đô thị Phú Mỹ Hưng , quận 7 .", [
        ([20, 21, 22, 23], [15, 16], 'NEG'),
        ([27, 28, 29], [15, 16], 'NEG'),
        ([31, 32], [15, 16], 'NEG'),
    ]),'''

new_3276 = '''    # Rec 3276: Đã có đường Bùi Bằng Đoàn, Phú Mỹ Hưng, quận 7
    ("Cơn mưa lớn chiều tối ngày 27 / 5 tại TPHCM đã gây ra tình trạng ngập úng trên tuyến đường Bùi Bằng Đoàn , khu đô thị Phú Mỹ Hưng , quận 7 .", [
        ([20, 21, 22, 23], [14, 15, 16, 17], 'NEG'),
        ([25, 26, 27, 28, 29, 30], [14, 15, 16, 17], 'NEG'),
        ([32, 33], [14, 15, 16, 17], 'NEG'),
    ]),'''

# Fix Rec 3279
old_3279 = '''    # Rec 3279: Đã có Nguyễn Hữu Cảnh, Q. Bình Thạnh
    ("Rốn ngập ” Nguyễn Hữu Cảnh ở Q. Bình Thạnh ( TP. HCM ) đã được đầu tư máy bơm , triển khai dự án nâng đường nhưng mưa xuống vẫn ngập sâu .", [
        ([3, 4, 5], [31, 32], 'NEG'),
        ([8, 9, 10], [31, 32], 'NEG'),
    ]),'''

new_3279 = '''    # Rec 3279: Đã có Nguyễn Hữu Cảnh, Q. Bình Thạnh
    ("Rốn ngập ” Nguyễn Hữu Cảnh ở Q. Bình Thạnh ( TP. HCM ) đã được đầu tư máy bơm , triển khai dự án nâng đường nhưng mưa xuống vẫn ngập sâu .", [
        ([3, 4, 5], [31, 32], 'NEG'),
        ([7, 8, 9], [31, 32], 'NEG'),
    ]),'''

for o, n in [
    (old_3208, new_3208), (old_3209, new_3209), (old_3213, new_3213),
    (old_3216, new_3216), (old_3227, new_3227), (old_3230, new_3230),
    (old_3243, new_3243), (old_3248, new_3248), (old_3249, new_3249),
    (old_3250, new_3250), (old_3256, new_3256), (old_3264, new_3264),
    (old_3273, new_3273), (old_3276, new_3276), (old_3279, new_3279)
]:
    if o in content:
        content = content.replace(o, n)
    else:
        print('FAILED TO FIND PATTERN:', o[:40])

with open('scripts/build_phase3_batch33.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated build_phase3_batch33.py!')
