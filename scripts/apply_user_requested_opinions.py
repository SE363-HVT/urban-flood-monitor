import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

# Dictionary of clean, selective triplets strictly adhering to user's guidelines:
updates = {
    # 27: user: "27 là ngập lũ"
    27: [([1, 2], [3, 4], 'NEG')],

    # 40: user: "40 là ngập"
    40: [([10, 11, 12, 13], [17], 'NEG')],

    # 41: user: "câu tà lao... đừng có mang vô opinion" -> "ngập"
    41: [([3, 4], [12], 'NEG')],

    # 46: user: "46 thì là ngập thôi"
    46: [([1, 2], [9], 'NEG')],

    # 49: user: "câu tà lao... đừng có mang vô opinion" -> "nước ngập"
    49: [([10, 11], [3, 4], 'NEG')],

    # 124: user: "124 là ngập"
    124: [
        ([4, 5], [17], 'NEG'),
        ([7, 8], [17], 'NEG'),
        ([10, 11], [17], 'NEG')
    ],

    # 788: "cầu Sài Gòn" -> "rốn ngập"
    788: [([4, 5, 6], [39, 40], 'NEG')],

    # 1000: user: "rec 1000 là ngập"
    1000: [([6, 7], [23], 'NEG')],

    # 1099: user: "1099 thì khô ráo"
    1099: [([20, 21, 22, 23], [31, 32], 'POS')],

    # 1234: "rạch Đĩa" -> "ngập"
    1234: [([12, 13], [29], 'NEG')],

    # 1277: user: "1277 thì là ngập hết cả đoạn đường từ đầu đến cuối chợ"
    1277: [([9, 10, 11], [33, 34, 35, 36, 37, 38, 39, 40, 41, 42], 'NEG')],

    # 1445: user: "rec 1445 thì để ngập sâu thôi"
    1445: [([43, 44, 45, 46], [58, 59], 'NEG')],

    # 1459: "TP Hồ Chí Minh" -> "bị ngập"
    1459: [([27, 28, 29, 30], [31, 32], 'NEG')],

    # 1527: "Bình Tân" -> "Bao ngập tắt máy xe" or "ngập"
    1527: [([6, 7], [15], 'NEG')],

    # 1570: user: "rec 1570 là ngập sâu thôi"
    1570: [([5, 6], [7, 8], 'NEG')],

    # 1594: "Sài gòn" -> "ngập lụt"
    1594: [([9, 10], [15, 16], 'NEU')],

    # 1616: "Triều cường ở TPHCM" -> "đạt đỉnh"
    1616: [([0, 1, 2, 3], [7, 8], 'NEU')],

    # 1648: "TP HCM" -> "ngập sâu"
    1648: [([18, 19], [20, 21], 'NEG')],

    # 1669: "triều cường ở TPHCM" -> "đạt đỉnh"
    1669: [([7, 8, 9, 10], [11, 12], 'NEU')],

    # 1892: user: "Ngập sâu do triều cường thì lấy ngập sâu là được"
    1892: [([0, 1, 2, 3], [4, 5], 'NEG')],

    # 1961: user: "Ngập sâu do triều cường thì lấy ngập sâu là được"
    1961: [([0], [42, 43], 'NEG')]
}

for rec_num, tr in updates.items():
    idx = rec_num - 1
    t, _ = lines[idx].split('####')
    toks = t.split()
    # verify
    for a, o, p in tr:
        a_txt = " ".join(toks[i] for i in a)
        o_txt = " ".join(toks[i] for i in o)
        print(f"Rec {rec_num}: Aspect='{a_txt}', Opinion='{o_txt}', Pol='{p}'")
    lines[idx] = f"{t}####{tr}"

with open(filepath, 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"\nApplied updates to {len(updates)} records!")
