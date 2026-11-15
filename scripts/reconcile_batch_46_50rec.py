import sys
import ast

sys.stdout.reconfigure(encoding="utf-8")

file_path = "data/validate_label/thuan/phase2.txt"

with open(file_path, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f]

updates = {}

# 1530 (Rec 1531): [([12, 13], [2, 3], 'NEG')] (Sài Gòn, fix aspect token 13, 14 -> 12, 13)
updates[1530] = [([12, 13], [2, 3], 'NEG')]

# 1531 (Rec 1532): [([1], [8, 9, 10], 'NEG')] (ngập khủng khiếp)
updates[1531] = [([1], [8, 9, 10], 'NEG')]

# 1532 (Rec 1533): [([1], [8, 9], 'NEG')] (ngập nhà)
updates[1532] = [([1], [8, 9], 'NEG')]

# 1533 (Rec 1534): [] (REJECT - Đền Sòng Sơn / Cô Chín, Thanh Hóa)
updates[1533] = []

# 1534 (Rec 1535): keep current [([6, 7, 8, 9], [10, 11], 'NEU')]

# 1535 (Rec 1536): keep current [([12, 13, 14], [9, 10], 'NEG')]

# 1536 (Rec 1537): keep current [] (REJECT - Miền Trung)

# 1537 (Rec 1538): [] (REJECT - Sân Mỹ Đình, Hà Nội)
updates[1537] = []

# 1538 (Rec 1539): [] (REJECT - Đắk Lắk)
updates[1538] = []

# 1539 (Rec 1540): keep current [([3, 4], [14, 15], 'NEG')]

# 1540 (Rec 1541): keep current [([12, 13, 14], [9, 10], 'NEG')]

# 1541 (Rec 1542): [] (REJECT - Tân Kỳ, Nghệ An)
updates[1541] = []

# 1542 (Rec 1543): [] (REJECT - Tân Kỳ, Nghệ An)
updates[1542] = []

# 1543 (Rec 1544): keep current [([0, 1], [2], 'NEG')]

# 1544 (Rec 1545): keep current [([1, 2, 3, 4], [8, 9], 'NEG')]

# 1545 (Rec 1546): keep current [([8, 9, 10, 11], [12, 13], 'NEG')]

# 1546 (Rec 1547): keep current [([17, 18, 19], [13, 14, 15, 16], 'POS')]

# 1547 (Rec 1548): [] (REJECT - Huế)
updates[1547] = []

# 1548 (Rec 1549): [] (REJECT - Real Estate promotion)
updates[1548] = []

# 1549 (Rec 1550): keep current [([5, 6, 7, 8], [27, 28, 29], 'NEU')]

# 1550 (Rec 1551): [] (REJECT - Hướng dẫn kỹ thuật bảo dưỡng xe khi ngập)
updates[1550] = []

# 1551 (Rec 1552): keep current [([7], [8, 9, 10, 11], 'NEG')]

# 1552 (Rec 1553): keep current [([0, 1], [4, 5, 6, 7], 'NEU')]

# 1553 (Rec 1554): keep current [([10, 11], [7, 8], 'NEG')]

# 1554 (Rec 1555): [([13, 14, 15, 16], [51, 52], 'NEU')] (dự báo ngập úng tăng cao -> NEU)
updates[1554] = [([13, 14, 15, 16], [51, 52], 'NEU')]

# 1555 (Rec 1556): keep current [([0, 1, 2, 3], [5, 6], 'NEU')]

# 1556 (Rec 1557): keep current [] (REJECT - Quy Nhơn)

# 1557 (Rec 1558): keep current [] (REJECT - Hà Nội)

# 1558 (Rec 1559): keep current [([3, 4], [7], 'NEG')]

# 1559 (Rec 1560): keep current [] (REJECT - Tranh luận mua xe ô tô ngập nước)

# 1560 (Rec 1561): keep current [([7, 8, 9, 10, 11], [2, 3], 'NEU')]

# 1561 (Rec 1562): keep current [] (REJECT - Bán cửa chống ngập)

# 1562 (Rec 1563): keep current [([1, 2, 3, 4], [19, 20], 'NEG')]

# 1563 (Rec 1564): keep current [([34, 35], [37, 38], 'NEG')]

# 1564 (Rec 1565): keep current [] (REJECT - Gia Lai)

# 1565 (Rec 1566): [([1], [14, 15, 16], 'POS')] (giảm ngập lụt -> POS)
updates[1565] = [([1], [14, 15, 16], 'POS')]

# 1566 (Rec 1567): keep current [([12], [32], 'NEG'), ([14, 15, 16], [32], 'NEG'), ([18, 19, 20], [32], 'NEG'), ([22, 23], [32], 'NEG'), ([25, 26], [32], 'NEG')]

# 1567 (Rec 1568): keep current [([8, 9], [11, 12, 13], 'NEG')]

# 1568 (Rec 1569): keep current [([12, 13, 14, 15], [16, 17], 'NEU')]

# 1569 (Rec 1570): keep current [([11, 12], [13, 14], 'NEG')]

# 1570 (Rec 1571): keep current [([13, 14, 15], [18, 19, 20], 'NEG')]

# 1571 (Rec 1572): keep current [([1, 2, 3, 4], [14, 15], 'NEG')]

# 1572 (Rec 1573): keep current [([1, 2, 3, 4], [9], 'NEG')]

# 1573 (Rec 1574): keep current [([1], [7, 8], 'NEG')]

# 1574 (Rec 1575): keep current [([1], [23, 24], 'NEG')]

# 1575 (Rec 1576): keep current [] (REJECT - Hà Đông, Hà Nội)

# 1576 (Rec 1577): [] (REJECT - Trung Quốc)
updates[1576] = []

# 1577 (Rec 1578): keep current [] (REJECT - Gia Lai)

# 1578 (Rec 1579): [([1, 2, 3, 4], [29], 'NEG')] (ngập, strip 'bị')
updates[1578] = [([1, 2, 3, 4], [29], 'NEG')]

# 1579 (Rec 1580): keep current [([4], [8], 'NEG')]

# Apply updates
for idx in range(1530, 1580):
    parts = lines[idx].split("####")
    text = parts[0].strip()
    if idx in updates:
        trips = updates[idx]
        lines[idx] = f"{text}####{trips}"

with open(file_path, "w", encoding="utf-8") as f:
    for line in lines:
        f.write(f"{line}\n")

print(f"Đã cập nhật thành công {len(updates)} records trong Lô 46 (1531 - 1580).")
