import sys
import ast

sys.stdout.reconfigure(encoding="utf-8")

file_path = "data/validate_label/thuan/phase2.txt"

with open(file_path, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f]

updates = {}

# 1430 (Rec 1431): [([1], [24, 25], 'NEU')] (hệ thống cảnh báo sớm ngập lụt -> NEU)
updates[1430] = [([1], [24, 25], 'NEU')]

# 1431 (Rec 1432): [([31, 32, 33], [24, 25, 26, 27], 'NEG')] (chợ Thủ Đức, ngập nước dai dẳng)
updates[1431] = [([31, 32, 33], [24, 25, 26, 27], 'NEG')]

# 1432 (Rec 1433): [([42, 43, 44, 45], [38, 39], 'POS'), ([42, 43, 44, 45], [57, 58], 'NEG')]
updates[1432] = [([42, 43, 44, 45], [38, 39], 'POS'), ([42, 43, 44, 45], [57, 58], 'NEG')]

# 1433 (Rec 1434): keep current [([13, 14, 15, 16], [10, 11], 'POS')]

# 1434 (Rec 1435): keep current [([1], [24, 25], 'NEG')]

# 1435 (Rec 1436): keep current [([16, 17, 18, 19], [38, 39], 'POS')]

# 1436 (Rec 1437): keep current [([8, 9, 10, 11], [6], 'NEG')]

# 1437 (Rec 1438): [([13, 14, 15, 16], [20, 21, 22, 23, 24], 'POS')] (giảm tình trạng ngập úng -> POS)
updates[1437] = [([13, 14, 15, 16], [20, 21, 22, 23, 24], 'POS')]

# 1438 (Rec 1439): [([2, 3, 4, 5], [50, 51, 52, 53], 'NEG')] (ngập ngang ống pô)
updates[1438] = [([2, 3, 4, 5], [50, 51, 52, 53], 'NEG')]

# 1439 (Rec 1440): keep current [([1], [11, 12], 'NEG')]

# 1440 (Rec 1441): keep current [([5, 6], [15, 16, 17, 18], 'NEG')]

# 1441 (Rec 1442): keep current [([1, 2, 3, 4], [17, 18], 'NEG')]

# 1442 (Rec 1443): keep current [([24, 25, 26, 27], [22], 'NEG')]

# 1443 (Rec 1444): [([11], [26, 27], 'NEG')] (TPHCM, ngập sâu, fix aspect token 10 -> 11, strip bị)
updates[1443] = [([11], [26, 27], 'NEG')]

# 1444 (Rec 1445): [([49, 50, 51, 52], [64, 65], 'NEG')] (đường Tô Ngọc Vân, ngập sâu, strip bị)
updates[1444] = [([49, 50, 51, 52], [64, 65], 'NEG')]

# 1445 (Rec 1446): [([3, 4, 5, 6], [14, 15], 'NEG')] (đường Tô Ngọc Vân, ngập sâu)
updates[1445] = [([3, 4, 5, 6], [14, 15], 'NEG')]

# 1446 (Rec 1447): [([18, 19, 20, 21], [23], 'NEG')] (ngập, strip bị)
updates[1446] = [([18, 19, 20, 21], [23], 'NEG')]

# 1447 (Rec 1448): keep current [([20, 21, 22, 23], [31, 32], 'POS')]

# 1448 (Rec 1449): keep current [([1, 2, 3, 4], [23], 'NEG')]

# 1449 (Rec 1450): keep current [([1], [16], 'NEG')]

# 1450 (Rec 1451): keep current [([1], [9], 'NEG')]

# 1451 (Rec 1452): keep current [([18, 19, 20, 21], [15, 16], 'POS')]

# 1452 (Rec 1453): [([23, 24, 25, 26], [16], 'NEG')] (ngập, strip bare noun rốn ngập)
updates[1452] = [([23, 24, 25, 26], [16], 'NEG')]

# 1453 (Rec 1454): keep current [([9, 10, 11, 12], [7, 8], 'POS')]

# 1454 (Rec 1455): keep current [([1, 2, 3, 4], [17, 18], 'POS')]

# 1455 (Rec 1456): keep current [([15, 16, 17, 18], [13, 14], 'POS')]

# 1456 (Rec 1457): keep current [([3, 4, 5, 6], [8, 9, 10], 'NEG')]

# 1457 (Rec 1458): keep current [([1, 2, 3, 4], [30, 31], 'POS')]

# 1458 (Rec 1459): [([33, 34, 35, 36], [38], 'NEG')] (TP Hồ Chí Minh, ngập, fix aspect & opinion)
updates[1458] = [([33, 34, 35, 36], [38], 'NEG')]

# 1459 (Rec 1460): [([4, 5, 6], [23, 24], 'NEG'), ([8, 9, 10], [23, 24], 'NEG'), ([12, 13], [23, 24], 'NEG'), ([15, 16, 17], [23, 24], 'NEG')]
updates[1459] = [([4, 5, 6], [23, 24], 'NEG'), ([8, 9, 10], [23, 24], 'NEG'), ([12, 13], [23, 24], 'NEG'), ([15, 16, 17], [23, 24], 'NEG')]

# 1460 (Rec 1461): [([1], [8, 9, 10, 11], 'NEG')] (tràn vào nhà dân)
updates[1460] = [([1], [8, 9, 10, 11], 'NEG')]

# 1461 (Rec 1462): keep current [([25, 26], [34, 35, 36, 37], 'NEG'), ([28, 29, 30], [34, 35, 36, 37], 'NEG')]

# 1462 (Rec 1463): keep current [([1], [12, 13], 'NEG')]

# 1463 (Rec 1464): [([8, 9, 10, 11], [0, 1], 'NEU')] (dự báo ngập úng -> NEU)
updates[1463] = [([8, 9, 10, 11], [0, 1], 'NEU')]

# 1464 (Rec 1465): keep current [([14, 15], [25, 26], 'NEG')]

# 1465 (Rec 1466): [([14, 15, 16], [11], 'NEG'), ([18, 19], [11], 'NEG'), ([21, 22, 23], [11], 'NEG'), ([25, 26, 27], [11], 'NEG'), ([49, 50, 51], [53, 54], 'NEG')]
updates[1465] = [([14, 15, 16], [11], 'NEG'), ([18, 19], [11], 'NEG'), ([21, 22, 23], [11], 'NEG'), ([25, 26, 27], [11], 'NEG'), ([49, 50, 51], [53, 54], 'NEG')]

# 1466 (Rec 1467): [([3, 4, 5], [12, 13], 'NEG')] (ngập sâu, strip bị)
updates[1466] = [([3, 4, 5], [12, 13], 'NEG')]

# 1467 (Rec 1468): [([1], [10, 11, 12, 13, 14], 'NEG')] (ngập lên đến đầu gối)
updates[1467] = [([1], [10, 11, 12, 13, 14], 'NEG')]

# 1468 (Rec 1469): keep current [([1], [14], 'NEG')]

# 1469 (Rec 1470): [([17, 18, 19], [15], 'NEG')] (fix cross-sentence token 4 -> 15)
updates[1469] = [([17, 18, 19], [15], 'NEG')]

# 1470 (Rec 1471): [([14, 15, 16, 17, 18, 19], [4, 5], 'NEG')] (Trường ĐH Văn hóa TP. HCM)
updates[1470] = [([14, 15, 16, 17, 18, 19], [4, 5], 'NEG')]

# 1471 (Rec 1472): [([1], [18, 19], 'NEG')] (chết máy)
updates[1471] = [([1], [18, 19], 'NEG')]

# 1472 (Rec 1473): keep current [([1], [22], 'NEG')]

# 1473 (Rec 1474): keep current [([1, 2, 3, 4], [23, 24], 'NEG')]

# 1474 (Rec 1475): keep current [([1], [19], 'NEG')]

# 1475 (Rec 1476): [([1], [24, 25, 26], 'NEG')] (chờ nước rút -> NEG)
updates[1475] = [([1], [24, 25, 26], 'NEG')]

# 1476 (Rec 1477): keep current [([5, 6, 7], [22, 23], 'NEG')]

# 1477 (Rec 1478): [([22, 23, 24, 25], [32, 33, 34, 35], 'NEG')] (chìm trong biển nước)
updates[1477] = [([22, 23, 24, 25], [32, 33, 34, 35], 'NEG')]

# 1478 (Rec 1479): keep current [([1], [11, 12], 'POS')]

# 1479 (Rec 1480): [([1, 2, 3, 4], [13], 'NEG')] (ngập, strip bare noun rốn ngập)
updates[1479] = [([1, 2, 3, 4], [13], 'NEG')]

# Apply updates
for idx in range(1430, 1480):
    parts = lines[idx].split("####")
    text = parts[0].strip()
    if idx in updates:
        trips = updates[idx]
        lines[idx] = f"{text}####{trips}"

with open(file_path, "w", encoding="utf-8") as f:
    for line in lines:
        f.write(f"{line}\n")

print(f"Đã cập nhật thành công {len(updates)} records trong Lô 44 (1431 - 1480).")
