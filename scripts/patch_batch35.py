# -*- coding: utf-8 -*-
with open('scripts/build_phase3_batch35.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix Rec 3414
old_3414 = '''    # Rec 3414: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhất là một số tuyến đường ven sông bị ngập sâu khiến nhiều người tham gia giao thông gặp nhiều khó khăn .", [
        ([1], [12, 13, 14], 'NEG'),
        ([1], [23, 24, 25, 26], 'NEG'),
    ]),'''

new_3414 = '''    # Rec 3414: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhất là một số tuyến đường ven sông bị ngập sâu khiến nhiều người tham gia giao thông gặp nhiều khó khăn .", [
        ([1], [12, 13], 'NEG'),
        ([1], [21, 22, 23, 24], 'NEG'),
    ]),'''

# Fix Rec 3426
old_3426 = '''    # Rec 3426: Đã có quốc lộ 50, xã Bình Hưng, huyện Bình Chánh
    ("Người dân TP. HCM than trời vì triều cường ngập nhà hơn 10 năm Những tháng cuối năm , hàng chục hộ dân sống trên quốc lộ 50 , đoạn qua xã Bình Hưng , huyện Bình Chánh ( TP. HCM ) , phải khốn khổ trăm bề vì ngập nước do triều cường .", [
        ([25, 26, 27], [44, 45, 46, 47], 'NEG'),
        ([25, 26, 27], [49, 50], 'NEG'),
        ([32, 33, 34], [49, 50], 'NEG'),
        ([36, 37, 38], [49, 50], 'NEG'),
    ]),'''

new_3426 = '''    # Rec 3426: Đã có quốc lộ 50, xã Bình Hưng, huyện Bình Chánh
    ("Người dân TP. HCM than trời vì triều cường ngập nhà hơn 10 năm Những tháng cuối năm , hàng chục hộ dân sống trên quốc lộ 50 , đoạn qua xã Bình Hưng , huyện Bình Chánh ( TP. HCM ) , phải khốn khổ trăm bề vì ngập nước do triều cường .", [
        ([25, 26, 27], [44, 45, 46, 47], 'NEG'),
        ([25, 26, 27], [49, 50], 'NEG'),
        ([31, 32, 33], [49, 50], 'NEG'),
        ([35, 36, 37], [49, 50], 'NEG'),
    ]),'''

# Fix Rec 3430
old_3430 = '''    # Rec 3430: Đã có đường Mã Lò
    ("Trận mưa to khiến trước cổng UBND phường và đoạn đường Mã Lò ngập nặng .", [
        ([11, 12, 13], [14, 15], 'NEG'),
    ]),'''

new_3430 = '''    # Rec 3430: Đã có đường Mã Lò
    ("Trận mưa to khiến trước cổng UBND phường và đoạn đường Mã Lò ngập nặng .", [
        ([10, 11, 12], [13, 14], 'NEG'),
    ]),'''

# Fix Rec 3434
old_3434 = '''    # Rec 3434: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , 👉 Hàng chục hộ dân bị ngập sâu , nhiều tài sản hư hỏng nặng .", [
        ([1], [9, 10, 11], 'NEG'),
        ([1], [15, 16, 17], 'NEG'),
    ]),'''

new_3434 = '''    # Rec 3434: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , 👉 Hàng chục hộ dân bị ngập sâu , nhiều tài sản hư hỏng nặng .", [
        ([1], [9, 10], 'NEG'),
        ([1], [15, 16, 17], 'NEG'),
    ]),'''

# Fix Rec 3438
old_3438 = '''    # Rec 3438: Đã có Bình Quới, phường Bình Quới
    ("Người dân rốn ngập Bình Quới ( TP. HCM ) vẫn còn khổ với con nước Đến chiều 25 / 10 , nhiều nơi tại phường Bình Quới , TP. HCM vẫn còn đang ngập sâu , ảnh hưởng đến sinh hoạt .", [
        ([4, 5], [33, 34, 35], 'NEG'),
        ([26, 27, 28], [33, 34, 35], 'NEG'),
        ([26, 27, 28], [37, 38, 39, 40, 41], 'NEG'),
    ]),'''

new_3438 = '''    # Rec 3438: Đã có Bình Quới, phường Bình Quới
    ("Người dân rốn ngập Bình Quới ( TP. HCM ) vẫn còn khổ với con nước Đến chiều 25 / 10 , nhiều nơi tại phường Bình Quới , TP. HCM vẫn còn đang ngập sâu , ảnh hưởng đến sinh hoạt .", [
        ([4, 5], [33, 34, 35], 'NEG'),
        ([25, 26, 27], [33, 34, 35], 'NEG'),
        ([25, 26, 27], [37, 38, 39, 40, 41], 'NEG'),
    ]),'''

# Fix Rec 3484
old_3484 = '''    # Rec 3484: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Người dân oằn mình đón đêm Trung thu trong cảnh kẹt xe , tắc đường , mưa ngập .", [
        ([1], [15, 16], 'NEG'),
        ([1], [18, 19], 'NEG'),
        ([1], [21, 22], 'NEG'),
    ]),'''

new_3484 = '''    # Rec 3484: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Người dân oằn mình đón đêm Trung thu trong cảnh kẹt xe , tắc đường , mưa ngập .", [
        ([1], [13, 14], 'NEG'),
        ([1], [16, 17], 'NEG'),
        ([1], [19, 20], 'NEG'),
    ]),'''

for o, n in [(old_3414, new_3414), (old_3426, new_3426), (old_3430, new_3430),
             (old_3434, new_3434), (old_3438, new_3438), (old_3484, new_3484)]:
    if o in c:
        c = c.replace(o, n)
    else:
        print('FAILED TO FIND PATTERN:', o[:40])

with open('scripts/build_phase3_batch35.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('Patched build_phase3_batch35.py!')
