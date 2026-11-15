import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# Line 1061 (idx 1060): include prefix 'sông' -> sông Sài Gòn [48, 49, 50], opinion 'kiểm soát ngập' [4, 5, 6] is POS
updates[1060] = (
    "Đây là công trình kiểm soát ngập có quy mô lớn nhất miền Nam , bao gồm 6 cống kiểm soát triều khổng lồ tại Bến Nghé , Tân Thuận , Phú Xuân , Mương Chuối , Cây Khô , Phú Định ; gần 8km đê kè ven sông Sài Gòn và hàng chục cống nhỏ .",
    [([48, 49, 50], [4, 5, 6], 'POS')]
)

# Line 1084 (idx 1083): remove invalid non-geographic aspect 'giao thông', keep Dương Văn Cam and Tô Ngọc Vân
updates[1083] = (
    "Trên các tuyến đường Dương Văn Cam , Tô Ngọc Vân , nước ngập lút bánh xe máy , giao thông tê liệt nhiều giờ .",
    [([4, 5, 6], [13, 14, 15, 16, 17], 'NEG'),
     ([8, 9, 10], [13, 14, 15, 16, 17], 'NEG')]
)

# Line 1099 (idx 1098): include prefix 'cầu' -> cầu vượt Gò Dưa [26, 27, 28, 29]
updates[1098] = (
    "Tại TP. Hồ Chí Minh , Trong làn nước đục ngầu , người dân tất bật di chuyển tài sản , xe cộ lên khu vực cầu vượt Gò Dưa - nơi cao hơn và tạm thời khô ráo .",
    [([26, 27, 28, 29], [37, 38], 'POS')]
)

# Validate and apply updates
for idx, (new_text, new_trips) in updates.items():
    tokens = new_text.split()
    for asp, opi, pol in new_trips:
        for a in asp:
            assert a < len(tokens), f"Line {idx+1}: asp idx {a} out of range {len(tokens)}"
        for o in opi:
            assert o < len(tokens), f"Line {idx+1}: opi idx {o} out of range {len(tokens)}"
    lines[idx] = f"{new_text}####{new_trips}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print(f"Batch 11: Successfully updated {len(updates)} records!")
