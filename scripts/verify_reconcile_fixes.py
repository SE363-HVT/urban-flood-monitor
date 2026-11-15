import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

fixes = {
    # Line 1228 (idx 1227): "Do vậy , về tổng thể thì khu vực này vẫn ngập khi mưa và triều cường ở TPHCM ."
    # Aspect: triều cường ở TPHCM [14, 15, 16, 17]
    # Opinion: vẫn ngập [10, 11]
    1227: [([14, 15, 16, 17], [10, 11], 'NEG')],

    # Line 1237 (idx 1236): "Mưa ngập , triều cường ở TPHCM cũng ngập và thậm chí ngập nhiều ngày nước vẫn ch..."
    # Aspect: triều cường ở TPHCM [2, 3, 4, 5]
    # Opinion: cũng ngập [6, 7] or ngập [7]
    1236: [([2, 3, 4, 5], [7], 'NEG')],

    # Line 1322 (idx 1321): "Triều cường ở TPHCM dâng cao ngập sâu tại nhiều khu vực thấp trũng ."
    # Aspect: Triều cường ở TPHCM [0, 1, 2, 3]
    # Opinion: dâng cao ngập sâu [4, 5, 6, 7]
    1321: [([0, 1, 2, 3], [4, 5, 6, 7], 'NEG')],

    # Line 1885 (idx 1884): "Cùng lúc , đỉnh triều ở TPHCM sông Sài Gòn được dự báo đạt mức cao nhất trong hôm nay , làm gia tăng nguy cơ ngập úng..."
    # Aspect: đỉnh triều ở TPHCM [40, 41, 42, 43], sông Sài Gòn [44, 45, 46]
    # Opinion: làm gia tăng nguy cơ ngập úng [58, 59, 60, 61, 62, 63, 64]
    1884: [([40, 41, 42, 43], [58, 59, 60, 61, 62, 63, 64], 'NEU'), ([44, 45, 46], [58, 59, 60, 61, 62, 63, 64], 'NEU')],

    # Line 1893 (idx 1892): "Ở Sài Gòn có 2 thứ không bao giờ trễ hẹn : kẹt xe và triều cường ở TPHCM . Tối nay triều cường lên , mưa không lớn mà đường vẫn ngập lênh láng như này đây 🥹..."
    # Aspect: triều cường ở TPHCM [15, 16, 17, 18]
    # Opinion: vẫn ngập lênh láng [31, 32, 33, 34]
    1892: [([15, 16, 17, 18], [31, 32, 33, 34], 'NEG')],

    # Line 1922 (idx 1921): "🌊 CẢNH BÁO TRIỀU CƯỜNG ở TPHCM KHU VỰC SÔNG SÀI GÒN"
    # Aspect: TRIỀU CƯỜNG ở TPHCM [3, 4, 5, 6], SÔNG SÀI GÒN [9, 10, 11]
    # Opinion: CẢNH BÁO [1, 2]
    1921: [([3, 4, 5, 6], [1, 2], 'NEU'), ([9, 10, 11], [1, 2], 'NEU')],

    # Line 1948 (idx 1947): "TP. HCM khả năng ngập nặng vì mưa lớn kết hợp triều cường ở TPHCM cao"
    # Aspect: TP. HCM [0, 1], triều cường ở TPHCM [11, 12, 13, 14]
    # Opinion: khả năng ngập nặng [2, 3, 4, 5]
    1947: [([0, 1], [2, 3, 4, 5], 'NEU'), ([11, 12, 13, 14], [2, 3, 4, 5], 'NEU')],

    # Line 1954 (idx 1953): "Dĩ An ngập hết rồi 🌧 Clip : Hồng Tâm" (Bình Dương - in scope)
    # Aspect: Dĩ An [0, 1]
    # Opinion: ngập hết rồi [2, 3, 4]
    1953: [([0, 1], [2, 3, 4], 'NEG')],

    # Line 1955 (idx 1954): "🆘 Trước nhà hàng Phố Đôi Ngã Tư 550 ngay lúc này . Sau trận mưa lớn , nước ngập , xe di chuyển chậm lúc tan tầm . Mọi người lưu ý ." (Dĩ An, Bình Dương - in scope)
    # Aspect: Ngã Tư 550 [6, 7, 8]
    # Opinion: nước ngập , xe di chuyển chậm [17, 18, 19, 20, 21, 22, 23]
    1954: [([6, 7, 8], [17, 18, 19, 20, 21, 22, 23], 'NEG')],

    # Line 1960 (idx 1959): "Hà Nội nắng nóng , triều cường ở TPHCM đạt đỉnh # sggpnews # saigongiaiphong # sggp # dubaothoitiet # thoitiet"
    # Aspect: triều cường ở TPHCM [5, 6, 7, 8]
    # Opinion: đạt đỉnh [9, 10]
    1959: [([5, 6, 7, 8], [9, 10], 'NEU')],

    # Line 1982 (idx 1981): "Mưa kèm triều cường ở TPHCM : Sáng đi làm ướt sũng , tối về bì bõm lội"
    # Aspect: triều cường ở TPHCM [2, 3, 4, 5]
    # Opinion: bì bõm lội [15, 16, 17]
    1981: [([2, 3, 4, 5], [15, 16, 17], 'NEG')],

    # Line 1986 (idx 1985): "Bản đồ một số điểm thường xuyên ngập nặng do triều cường ở TPHCM . - - - - - - - - - - Link xem : ..."
    # Aspect: triều cường ở TPHCM [10, 11, 12, 13]
    # Opinion: thường xuyên ngập nặng [5, 6, 7, 8]
    1985: [([10, 11, 12, 13], [5, 6, 7, 8], 'NEG')],

    # Line 1988 (idx 1987): "Hà Nội nắng nóng , triều cường ở TPHCM đạt đỉnh # SGGP"
    # Aspect: triều cường ở TPHCM [5, 6, 7, 8]
    # Opinion: đạt đỉnh [9, 10]
    1987: [([5, 6, 7, 8], [9, 10], 'NEU')]
}

for idx, trips in fixes.items():
    text = lines[idx].split('####')[0].strip()
    tokens = text.split()
    print(f"\nLine {idx+1}:")
    for t in trips:
        asp = " ".join(tokens[x] for x in t[0])
        op = " ".join(tokens[x] for x in t[1])
        print(f"  Asp [{t[0]}]: '{asp}' | Op [{t[1]}]: '{op}' | Pol: {t[2]}")
