# -*- coding: utf-8 -*-
with open('scripts/build_phase3_batch34.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix Rec 3366
old_3366 = '''    # Rec 3366: Đã có TP. HCM, trạm điện quận Gò Vấp, đường Cây Trâm
    ("Tối 14 - 9 , trên địa bàn TP. HCM xuất hiện mưa lớn khiến nhiều tuyến đường ngập , trong đó trạm điện quận Gò Vấp trên đường Cây Trâm bị nước tràn vào , lực lượng PCCC đã ứng cứu khẩn cấp đến hút nước ra ngoài .", [
        ([8, 9], [18], 'NEG'),
        ([23, 24, 25, 26, 27], [32, 33, 34], 'NEG'),
        ([29, 30, 31], [32, 33, 34], 'NEG'),
    ]),'''

new_3366 = '''    # Rec 3366: Đã có trạm điện quận Gò Vấp, đường Cây Trâm
    ("Tối 14 - 9 , trên địa bàn TP. HCM xuất hiện mưa lớn khiến nhiều tuyến đường ngập , trong đó trạm điện quận Gò Vấp trên đường Cây Trâm bị nước tràn vào , lực lượng PCCC đã ứng cứu khẩn cấp đến hút nước ra ngoài .", [
        ([23, 24, 25, 26, 27], [32, 33, 34], 'NEG'),
        ([29, 30, 31], [32, 33, 34], 'NEG'),
    ]),'''

# Fix Rec 3380
old_3380 = '''    # Rec 3380: Đã có TP HCM, TP Thủ Đức, đường Phạm Văn Đồng
    ("Mưa lớn gây ngập đường , kẹt xe ở TP HCM Mưa lớn khiến nhiều nơi ở TP Thủ Đức ngập sâu , nắp hố ga trên đường Phạm Văn Đồng bị bung tạo thành cột nước cao , gây ùn tắc khoảng 4 km , chiều 6 / 9 .", [
        ([9, 10], [2, 3], 'NEG'),
        ([9, 10], [6, 7], 'NEG'),
        ([17, 18, 19], [20, 21], 'NEG'),
        ([27, 28, 29, 30], [39, 40, 41], 'NEG'),
    ]),'''

new_3380 = '''    # Rec 3380: Đã có TP Thủ Đức, đường Phạm Văn Đồng
    ("Mưa lớn gây ngập đường , kẹt xe ở TP HCM Mưa lớn khiến nhiều nơi ở TP Thủ Đức ngập sâu , nắp hố ga trên đường Phạm Văn Đồng bị bung tạo thành cột nước cao , gây ùn tắc khoảng 4 km , chiều 6 / 9 .", [
        ([17, 18, 19], [20, 21], 'NEG'),
        ([27, 28, 29, 30], [39, 40, 41], 'NEG'),
    ]),'''

c = c.replace(old_3366, new_3366)
c = c.replace(old_3380, new_3380)

with open('scripts/build_phase3_batch34.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('Patched build_phase3_batch34.py!')
