import sys
import ast

sys.stdout.reconfigure(encoding="utf-8")

file_path = "data/validate_label/thuan/phase2.txt"

with open(file_path, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f]

updates = {}

# 1480 (Rec 1481): keep current [([6, 7, 8, 9], [3, 4], 'NEG')]

# 1481 (Rec 1482): keep current [([31, 32, 33, 34], [36, 37], 'POS')]

# 1482 (Rec 1483): keep current [([1], [9], 'NEG')]

# 1483 (Rec 1484): keep current [([1], [9, 10], 'POS')]

# 1484 (Rec 1485): keep current [([1, 2, 3, 4], [12, 13], 'POS')]

# 1485 (Rec 1486): keep current [([1, 2, 3, 4], [34, 35], 'POS')]

# 1486 (Rec 1487): keep current [([1, 2, 3, 4], [16], 'NEG')]

# 1487 (Rec 1488): keep current [([25, 26], [20, 21], 'POS')]

# 1488 (Rec 1489): keep current [([1], [15, 16], 'POS')]

# 1489 (Rec 1490): keep current [([1], [31, 32, 33], 'NEG')]

# 1490 (Rec 1491): keep current [([1], [27], 'NEG')]

# 1491 (Rec 1492): keep current [([1], [25, 26], 'NEG')]

# 1492 (Rec 1493): keep current [([1], [32, 33], 'NEG')]

# 1493 (Rec 1494): keep current [([1], [7, 8, 9], 'NEG')]

# 1494 (Rec 1495): keep current [([15, 16, 17, 18], [22, 23], 'NEU')]

# 1495 (Rec 1496): [([1, 2, 3, 4], [14, 15], 'NEG')] (chết máy)
updates[1495] = [([1, 2, 3, 4], [14, 15], 'NEG')]

# 1496 (Rec 1497): keep current [([1], [24, 25], 'NEG')]

# 1497 (Rec 1498): keep current [([0, 1, 2, 3], [5, 6, 7], 'NEG')]

# 1498 (Rec 1499): [([24, 25, 26, 27], [32, 33], 'NEG')] (ngập lụt)
updates[1498] = [([24, 25, 26, 27], [32, 33], 'NEG')]

# 1499 (Rec 1500): [([8, 9, 10, 11], [26, 27], 'NEU')] (đề phòng ngập úng -> NEU)
updates[1499] = [([8, 9, 10, 11], [26, 27], 'NEU')]

# 1500 (Rec 1501): keep current [([19, 20, 21, 22], [42, 43], 'NEG')]

# 1501 (Rec 1502): [([11, 12, 13, 14], [21, 22], 'NEG')] (ngập nước)
updates[1501] = [([11, 12, 13, 14], [21, 22], 'NEG')]

# 1502 (Rec 1503): [([1], [11, 12, 13, 14, 15, 16], 'NEG')] (ngập 1 / 3 bánh xe)
updates[1502] = [([1], [11, 12, 13, 14, 15, 16], 'NEG')]

# 1503 (Rec 1504): keep current [([1, 2, 3, 4], [19, 20], 'NEG')]

# 1504 (Rec 1505): [([1], [32, 33, 34, 35, 36], 'NEG')] (nước tràn vào hàng quán)
updates[1504] = [([1], [32, 33, 34, 35, 36], 'NEG')]

# 1505 (Rec 1506): keep current [([1, 2, 3, 4], [31, 32], 'NEG')]

# 1506 (Rec 1507): keep current [([1, 2, 3, 4], [16], 'NEG')]

# 1507 (Rec 1508): keep current [([1, 2, 3, 4], [11, 12], 'NEG')]

# 1508 (Rec 1509): keep current [([11, 12, 13, 14], [37, 38, 39], 'NEG')]

# 1509 (Rec 1510): keep current [([1], [32], 'NEG')]

# 1510 (Rec 1511): [([12, 13], [27, 28], 'NEG'), ([15, 16], [27, 28], 'NEG'), ([18, 19, 20], [27, 28], 'NEG')] (ngập sâu, strip bị)
updates[1510] = [([12, 13], [27, 28], 'NEG'), ([15, 16], [27, 28], 'NEG'), ([18, 19, 20], [27, 28], 'NEG')]

# 1511 (Rec 1512): [([10, 11, 12, 13], [15, 16, 17, 18, 19], 'NEG')] (ngập quá nửa bánh xe)
updates[1511] = [([10, 11, 12, 13], [15, 16, 17, 18, 19], 'NEG')]

# 1512 (Rec 1513): [([1, 2, 3, 4], [32, 33], 'NEG')] (TP. Hồ Chí Minh, ngập nước)
updates[1512] = [([1, 2, 3, 4], [32, 33], 'NEG')]

# 1513 (Rec 1514): [([1, 2, 3, 4], [8, 9], 'NEG')] (chết máy)
updates[1513] = [([1, 2, 3, 4], [8, 9], 'NEG')]

# 1514 (Rec 1515): keep current [([1, 2, 3, 4], [31, 32], 'NEG')]

# 1515 (Rec 1516): [([1, 2, 3, 4], [16], 'NEG')] (ngập)
updates[1515] = [([1, 2, 3, 4], [16], 'NEG')]

# 1516 (Rec 1517): [([1, 2, 3, 4], [11, 12], 'NEG')] (chết máy)
updates[1516] = [([1, 2, 3, 4], [11, 12], 'NEG')]

# 1517 (Rec 1518): [([11, 12, 13, 14], [37, 38, 39], 'NEG')] (triều cao ở TPHCM, mênh mông nước)
updates[1517] = [([11, 12, 13, 14], [37, 38, 39], 'NEG')]

# 1518 (Rec 1519): keep current [([1], [32], 'NEG')]

# 1519 (Rec 1520): [([1], [17, 18], 'NEG')] (ngập nước)
updates[1519] = [([1], [17, 18], 'NEG')]

# 1520 (Rec 1521): keep current [([1, 2, 3, 4], [39, 40], 'NEG')]

# 1521 (Rec 1522): [] (REJECT - không chết máy, không ngập)
updates[1521] = []

# 1522 (Rec 1523): keep current [([1, 2, 3, 4], [14], 'NEG')]

# 1523 (Rec 1524): keep current [([1], [6], 'NEG')]

# 1524 (Rec 1525): [([1], [11, 12], 'POS')] (rút dần)
updates[1524] = [([1], [11, 12], 'POS')]

# 1525 (Rec 1526): [] (REJECT - Diên Khánh / Nha Trang)
updates[1525] = []

# 1526 (Rec 1527): [([9, 10], [18], 'NEG')] (Bình Tân, ngập)
updates[1526] = [([9, 10], [18], 'NEG')]

# 1527 (Rec 1528): keep current [([0, 1], [6], 'NEG')]

# 1528 (Rec 1529): [([29, 30, 31, 32], [33, 34], 'NEG')] (ngập nước)
updates[1528] = [([29, 30, 31, 32], [33, 34], 'NEG')]

# 1529 (Rec 1530): [([15], [16, 17, 18], 'NEG'), ([15], [23, 24], 'NEG')] (biến thành sông, chết máy)
updates[1529] = [([15], [16, 17, 18], 'NEG'), ([15], [23, 24], 'NEG')]

# Apply updates
for idx in range(1480, 1530):
    parts = lines[idx].split("####")
    text = parts[0].strip()
    if idx in updates:
        trips = updates[idx]
        lines[idx] = f"{text}####{trips}"

with open(file_path, "w", encoding="utf-8") as f:
    for line in lines:
        f.write(f"{line}\n")

print(f"Đã cập nhật thành công {len(updates)} records trong Lô 45 (1481 - 1530).")
