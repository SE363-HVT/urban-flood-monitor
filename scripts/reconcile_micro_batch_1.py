with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

# Rec 1 (idx 0):
lines[0] = "Tại TP. Hồ Chí Minh , Chiều tối 28 / 9 , triều cường ở TPHCM đạt đỉnh khiến nhiều tuyến đường phía Nam TP. HCM như Lê Văn Lương , Trần Xuân Soạn , Nguyễn Hữu Thọ … ngập sâu đúng giờ tan tầm , người dân chật vật đi lại .####[([27, 28, 29], [39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51], 'NEG'), ([31, 32, 33], [39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51], 'NEG'), ([35, 36, 37], [39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51], 'NEG'), ([12, 13, 14, 15], [16, 17], 'NEU')]"

# Rec 2 (idx 1):
lines[1] = "Tại TP. Hồ Chí Minh , Chiều tối nay TPHCM có thể mưa , triều cường ở TPHCM gây ngập # HTV # VOH # VOHTinTuc # RadioVOH # RadioHCM # RADIOTINg # TinTuc####[([9], [10, 11, 12], 'NEU'), ([14, 15, 16, 17], [19], 'NEU')]"

# Rec 4 (idx 3):
lines[3] = "Chiều nay , TPHCM và miền Tây đối mặt đợt triều cường ở TPHCM cao nhất từ đầu năm . Nhiều khu vực có nguy cơ ngập sâu , ảnh hưởng việc đi lại . Người dân nên theo dõi thông tin khí tượng và chủ động chọn lộ trình .####[([3], [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33], 'NEU'), ([10, 11, 12, 13], [14, 15, 16, 17, 18], 'NEU')]"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print("Micro-batch 1 (Rec 1 - 10) reconciled successfully!")
