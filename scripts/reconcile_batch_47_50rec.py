import sys
import ast

sys.stdout.reconfigure(encoding="utf-8")

file_path = "data/validate_label/thuan/phase2.txt"

with open(file_path, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f]

updates = {}

# 1580 (Rec 1581): keep current [([1], [15, 16], 'NEG')]

# 1581 (Rec 1582): keep current [([120, 121], [106, 107], 'NEG')]

# 1582 (Rec 1583): [([1], [7, 8], 'POS')] (hết ngập -> POS)
updates[1582] = [([1], [7, 8], 'POS')]

# 1583 (Rec 1584): keep current [([0, 1], [6, 7], 'NEG')]

# 1584 (Rec 1585): keep current [([0, 1, 2], [4, 5, 6, 7], 'NEG')]

# 1585 (Rec 1586): keep current [([1, 2, 3, 4], [7], 'NEG')]

# 1586 (Rec 1587): keep current [([15, 16], [17, 18], 'NEG')]

# 1587 (Rec 1588): keep current [([2, 3], [4, 5, 6, 7, 8, 9], 'NEG')]

# 1588 (Rec 1589): keep current [([2, 3, 4], [5, 6, 7, 8], 'NEG'), ([17, 18], [28, 29], 'NEG')]

# 1589 (Rec 1590): keep current [([5, 6, 7, 8], [31, 32], 'NEG')]

# 1590 (Rec 1591): keep current [] (REJECT - Gia Lai)

# 1591 (Rec 1592): keep current [([8, 9], [1, 2, 3], 'NEG')]

# 1592 (Rec 1593): keep current [([77, 78, 79], [91, 92, 93, 94], 'NEG'), ([81, 82], [91, 92, 93, 94], 'NEG'), ([84, 85], [91, 92, 93, 94], 'NEG'), ([88, 89, 90], [91, 92, 93, 94], 'NEG')]

# 1593 (Rec 1594): [([12, 13], [18, 19], 'NEU')] (Sài gòn, nguy cơ sắp ngập lụt -> NEU)
updates[1593] = [([12, 13], [18, 19], 'NEU')]

# 1594 (Rec 1595): keep current [([7, 8, 9, 10], [11, 12], 'NEG')]

# 1595 (Rec 1596): keep current [([4, 5, 6, 7], [0], 'NEG')]

# 1596 (Rec 1597): [([0, 1, 2, 3], [15], 'NEU')] (có thể ngập -> NEU)
updates[1596] = [([0, 1, 2, 3], [15], 'NEU')]

# 1597 (Rec 1598): [] (REJECT - Clip hài hước thú cưng lũ cún)
updates[1597] = []

# 1598 (Rec 1599): [] (REJECT - Du lịch sinh thái rừng ngập mặn Cần Giờ)
updates[1598] = []

# 1599 (Rec 1600): keep current [([0, 1, 2, 3], [14], 'NEG')]

# 1600 (Rec 1601): keep current [([13, 14, 15], [7, 8, 9], 'NEG')]

# 1601 (Rec 1602): [([23, 24, 25, 26], [28, 29], 'NEG')] (ngập sâu, strip 'bị')
updates[1601] = [([23, 24, 25, 26], [28, 29], 'NEG')]

# 1602 (Rec 1603): keep current [([1, 2, 3, 4], [8, 9, 10, 11], 'NEG')]

# 1603 (Rec 1604): keep current [([123, 124, 125, 126], [132, 133], 'NEG'), ([253, 254, 255, 256], [274, 275], 'NEU')]

# 1604 (Rec 1605): keep current [([0, 1], [3, 4], 'NEG')]

# 1605 (Rec 1606): [([34, 35, 36], [12, 13], 'NEG')] (đường Đề Thám, ngập nặng)
updates[1605] = [([34, 35, 36], [12, 13], 'NEG')]

# 1606 (Rec 1607): keep current [([3, 4, 5, 6], [30, 31], 'NEG')]

# 1607 (Rec 1608): keep current [([3, 4, 5, 6], [7, 8], 'NEU')]

# 1608 (Rec 1609): keep current [([1, 2, 3, 4], [10, 11, 12], 'NEG')]

# 1609 (Rec 1610): keep current [([3, 4, 5, 6], [31, 32], 'NEG')]

# 1610 (Rec 1611): keep current [([0, 1, 2, 3], [5, 6], 'NEU')]

# 1611 (Rec 1612): keep current [([3, 4], [0, 1], 'NEG')]

# 1612 (Rec 1613): [([3, 4, 5], [0, 1], 'NEG')] (Phố Bùi Viện, Ngập nặng, remove over-tagged TP. Thủ Đức)
updates[1612] = [([3, 4, 5], [0, 1], 'NEG')]

# 1613 (Rec 1614): keep current [([3, 4, 5], [2], 'NEG')]

# 1614 (Rec 1615): keep current [([7, 8, 9, 10], [4, 5], 'NEG')]

# 1615 (Rec 1616): keep current [([0, 1, 2, 3], [8, 9], 'NEU')]

# 1616 (Rec 1617): keep current [([4, 5, 6, 7], [9, 10, 11, 12], 'NEG')]

# 1617 (Rec 1618): keep current [([1, 2, 3, 4], [5], 'NEG')]

# 1618 (Rec 1619): keep current [([1], [14, 15], 'NEG')]

# 1619 (Rec 1620): keep current [([7, 8, 9, 10], [13, 14], 'NEU')]

# 1620 (Rec 1621): [([2, 3, 4, 5], [9, 10], 'NEU')] (Vì sao TP. Hồ Chí Minh lại dễ bị ngập sâu...? -> NEU)
updates[1620] = [([2, 3, 4, 5], [9, 10], 'NEU')]

# 1621 (Rec 1622): keep current [([6, 7, 8, 9], [17, 18], 'NEG')]

# 1622 (Rec 1623): [([6], [14], 'NEG')] (TPHCM, ngập)
updates[1622] = [([6], [14], 'NEG')]

# 1623 (Rec 1624): keep current [([4, 5], [7, 8, 9], 'NEG')]

# 1624 (Rec 1625): keep current [([33, 34, 35, 36], [31], 'NEG')]

# 1625 (Rec 1626): [([3, 4], [19], 'NEG')] (Tân Quy, ngập)
updates[1625] = [([3, 4], [19], 'NEG')]

# 1626 (Rec 1627): [] (REJECT - Top 7 tuyến đường ngập quảng cáo BĐS)
updates[1626] = []

# 1627 (Rec 1628): [([1, 2, 3, 4], [15], 'NEG')] (ngập, strip 'bị')
updates[1627] = [([1, 2, 3, 4], [15], 'NEG')]

# 1628 (Rec 1629): [([0, 1, 2, 3], [22], 'NEG')] (ngập, strip 'bị')
updates[1628] = [([0, 1, 2, 3], [22], 'NEG')]

# 1629 (Rec 1630): [([8, 9, 10], [30], 'NEG')] (phường Bình Quới, ngập)
updates[1629] = [([8, 9, 10], [30], 'NEG')]

# Apply updates
for idx in range(1580, 1630):
    parts = lines[idx].split("####")
    text = parts[0].strip()
    if idx in updates:
        trips = updates[idx]
        lines[idx] = f"{text}####{trips}"

with open(file_path, "w", encoding="utf-8") as f:
    for line in lines:
        f.write(f"{line}\n")

print(f"Đã cập nhật thành công {len(updates)} records trong Lô 47 (1581 - 1630).")
