import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = [line.rstrip('\r\n') for line in f]

corrections = {
    # 1931 (idx 1930): TP. Hồ Chí Minh ngập nước (rút gọn opinion bỏ comma)
    1930: [([12, 13, 14, 15], [16, 17], 'NEG')],

    # 1934 (idx 1933): hầm chui An Phú ngập
    1933: [([42, 43, 44, 45], [40], 'NEG')],

    # 1938 (idx 1937): TPHCM dễ ngập nước (cảnh báo lưu ý -> NEU)
    1937: [([1], [17, 18, 19], 'NEU')],

    # 1940 (idx 1939): TP. HCM ngập sâu (rút gọn opinion)
    1939: [([6, 7], [12, 13], 'NEG')],

    # 1941 (idx 1940): TP. HCM dễ ngập (khuyến cáo lưu ý -> NEU)
    1940: [([15, 16], [5, 6], 'NEU')],

    # 1943 (idx 1942): THE GLOBAL CITY KO NGẬP / TPHCM ngập nặng
    1942: [([4, 5, 6], [7, 8], 'POS'), ([26], [27, 28], 'NEG')],

    # 1944 (idx 1943): Thành phố biển Thủ Đức ngập nhất (tránh fallback)
    1943: [([6, 7], [14, 15], 'NEG')],

    # 1947 (idx 1946): đường Lương Định Của tiếp tục ngập (sửa tục ngập -> tiếp tục ngập)
    1946: [([10, 11, 12, 13], [17, 18, 19], 'NEG')],

    # 1948 (idx 1947): TP. HCM khả năng ngập nặng (dự báo -> NEU)
    1947: [([0, 1], [2, 3, 4, 5], 'NEU')],

    # 1950 (idx 1949): TPHCM chìm trong nước (chuẩn hóa entity)
    1949: [([9], [10, 11, 12], 'NEG')],

    # 1953 (idx 1952): TP. HCM ngập qua đầu gối (sửa lệch token 'HCM ,' -> 'TP. HCM')
    1952: [([20, 21], [27, 28, 29, 30], 'NEG')],

    # 1954 (idx 1953): Dĩ An, Bình Dương -> REJECT
    1953: [],

    # 1955 (idx 1954): Ngã tư 550, Dĩ An, Bình Dương -> REJECT
    1954: [],

    # 1956 (idx 1955): TP. HCM ngập nặng / ngã tư Hàng Xanh ùn ứ kéo dài
    1955: [([16, 17], [18, 19], 'NEG'), ([35, 36, 37, 38], [39, 40, 41, 42], 'NEG')],

    # 1960 (idx 1959): Hà Nội nắng nóng, triều cường ở TPHCM đạt đỉnh (sửa aspect TPHCM, triệt tiêu lỗi Pass 7)
    1959: [([8], [5, 6, 9, 10], 'NEU')],

    # 1965 (idx 1964): TP HCM ngập hơn một mét
    1964: [([10, 11], [1, 2, 3, 4], 'NEG')],

    # 1976 (idx 1975): TPHCM ngập sâu (chuẩn hóa entity)
    1975: [([27], [28, 29], 'NEG')],

    # 1978 (idx 1977): Sài Gòn ngập sâu (rút gọn opinion 12 tokens có comma)
    1977: [([6, 7], [14, 15], 'NEG')],

    # 1979 (idx 1978): đường Rạch Cùng / phường Bình Đông dâng khoảng nửa mét
    1978: [([24, 25, 26], [19, 20, 21, 22], 'NEG'), ([28, 29, 30], [19, 20, 21, 22], 'NEG')]
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

print(f"\n✅ ĐÃ HIỆU CHỈNH THÀNH CÔNG {count_updated} RECORDS TRONG LÔ 54!")
