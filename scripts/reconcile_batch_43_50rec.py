import sys
import ast

sys.stdout.reconfigure(encoding="utf-8")

file_path = "data/validate_label/thuan/phase2.txt"

with open(file_path, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f]

updates = {}

# 1380 (Rec 1381): keep current [([32, 33, 34, 35], [26, 27], 'POS')]

# 1381 (Rec 1382): [([0, 1, 2, 3], [11, 12, 13], 'NEG')] (ngập vào nhà)
updates[1381] = [([0, 1, 2, 3], [11, 12, 13], 'NEG')]

# 1382 (Rec 1383): [([5, 6, 7, 8], [35], 'NEG')] (ngập, strip 'bị')
updates[1382] = [([5, 6, 7, 8], [35], 'NEG')]

# 1383 (Rec 1384): keep current [([23, 24], [20, 21], 'NEG'), ([26, 27, 28, 29], [20, 21], 'NEG')]

# 1384 (Rec 1385): keep current [([1], [26, 27], 'NEG')]

# 1385 (Rec 1386): keep current [([10, 11, 12, 13], [8, 9], 'POS')]

# 1386 (Rec 1387): [([20, 21, 22], [26, 27], 'NEG')] (P. Thảo Điền, dâng cao)
updates[1386] = [([20, 21, 22], [26, 27], 'NEG')]

# 1387 (Rec 1388): [([16, 17, 18], [14], 'NEG')] (đoạn ngập trên đường Quốc Hương -> [16, 17, 18], [14])
updates[1387] = [([16, 17, 18], [14], 'NEG')]

# 1388 (Rec 1389): keep current [([1], [7, 8], 'NEG')]

# 1389 (Rec 1390): [([17, 18, 19, 20, 21, 22], [4, 5], 'NEG')] (Trường ĐH Văn hóa TP. HCM)
updates[1389] = [([17, 18, 19, 20, 21, 22], [4, 5], 'NEG')]

# 1390 (Rec 1391): keep current [([1, 2, 3, 4], [8], 'NEG')]

# 1391 (Rec 1392): [([1, 2, 3, 4], [24, 25], 'NEG')] (chết máy)
updates[1391] = [([1, 2, 3, 4], [24, 25], 'NEG')]

# 1392 (Rec 1393): keep current [([1], [23], 'NEG')]

# 1393 (Rec 1394): [([4, 5, 6], [30, 31], 'NEG')] (nước ngập)
updates[1393] = [([4, 5, 6], [30, 31], 'NEG')]

# 1394 (Rec 1395): keep current [([1], [14], 'NEG')]

# 1395 (Rec 1396): keep current [([1, 2, 3, 4], [37], 'NEG')]

# 1396 (Rec 1397): keep current [([1], [9, 10], 'NEG')]

# 1397 (Rec 1398): [([11, 12, 13], [28, 29], 'NEG')] (ngập nhẹ)
updates[1397] = [([11, 12, 13], [28, 29], 'NEG')]

# 1398 (Rec 1399): [([1], [19, 20, 21, 22, 23, 24, 25], 'NEG')] (ngập sâu quá nửa bánh xe máy)
updates[1398] = [([1], [19, 20, 21, 22, 23, 24, 25], 'NEG')]

# 1399 (Rec 1400): keep current [([1], [22], 'NEG')]

# 1400 (Rec 1401): keep current [([4, 5, 6, 7], [8, 9, 10, 11], 'POS')]

# 1401 (Rec 1402): keep current [([1], [9], 'NEG')]

# 1402 (Rec 1403): keep current [([29, 30, 31, 32], [26, 27], 'POS')]

# 1403 (Rec 1404): [([8, 9, 10, 11], [39], 'NEG')] (ngập, strip 'bị')
updates[1403] = [([8, 9, 10, 11], [39], 'NEG')]

# 1404 (Rec 1405): keep current [([1], [18, 19], 'NEG')]

# 1405 (Rec 1406): keep current [([22, 23, 24, 25], [34, 35], 'POS')]

# 1406 (Rec 1407): [([10, 11, 12], [28, 29], 'NEG'), ([19, 20], [28, 29], 'NEG')] (ngập nước, strip 'lại bị')
updates[1406] = [([10, 11, 12], [28, 29], 'NEG'), ([19, 20], [28, 29], 'NEG')]

# 1407 (Rec 1408): [([5, 6, 7], [33], 'NEG')] (ngập, strip 'đã bị')
updates[1407] = [([5, 6, 7], [33], 'NEG')]

# 1408 (Rec 1409): [([8, 9, 10], [12, 13, 14], 'NEG')] (ngập như sông)
updates[1408] = [([8, 9, 10], [12, 13, 14], 'NEG')]

# 1409 (Rec 1410): keep current [([15, 16, 17], [3], 'NEG')]

# 1410 (Rec 1411): keep current [([14, 15, 16], [1, 2], 'NEG')]

# 1411 (Rec 1412): keep current [([1], [5, 6], 'NEG')]

# 1412 (Rec 1413): keep current [([1, 2, 3, 4], [16, 17], 'NEG')]

# 1413 (Rec 1414): keep current [([5, 6, 7], [20, 21], 'NEG')]

# 1414 (Rec 1415): [([6, 7, 8], [14, 15], 'NEG')] (ngập nặng, strip 'bị')
updates[1414] = [([6, 7, 8], [14, 15], 'NEG')]

# 1415 (Rec 1416): [([1], [19, 20, 21], 'NEG')] (ngập suốt tuyến)
updates[1415] = [([1], [19, 20, 21], 'NEG')]

# 1416 (Rec 1417): [([14, 15, 16, 17, 18, 19], [1, 2], 'NEG')] (Trường ĐH Văn hóa TP. HCM)
updates[1416] = [([14, 15, 16, 17, 18, 19], [1, 2], 'NEG')]

# 1417 (Rec 1418): keep current [([1, 2, 3, 4], [8], 'NEG')]

# 1418 (Rec 1419): keep current [([1, 2, 3, 4], [8], 'NEG')]

# 1419 (Rec 1420): keep current [([1], [19, 20, 21], 'NEG')]

# 1420 (Rec 1421): [([11, 12, 13], [24], 'NEG')] (ngập, strip bare noun 'điểm')
updates[1420] = [([11, 12, 13], [24], 'NEG')]

# 1421 (Rec 1422): keep current [([1, 2, 3, 4], [8], 'NEG')]

# 1422 (Rec 1423): [([1, 2, 3, 4], [17, 18, 19], 'NEG')] (ngập lênh láng)
updates[1422] = [([1, 2, 3, 4], [17, 18, 19], 'NEG')]

# 1423 (Rec 1424): [([1, 2, 3, 4], [20, 21], 'NEG')] (chết máy)
updates[1423] = [([1, 2, 3, 4], [20, 21], 'NEG')]

# 1424 (Rec 1425): keep current [([1, 2, 3, 4], [17, 18], 'NEG')]

# 1425 (Rec 1426): keep current [([1, 2, 3, 4], [27], 'NEG')]

# 1426 (Rec 1427): keep current [([12, 13, 14], [15, 16, 17], 'NEG')]

# 1427 (Rec 1428): keep current [([17, 18, 19], [42, 43, 44, 45, 46], 'NEG'), ([21, 22, 23, 24], [42, 43, 44, 45, 46], 'NEG')]

# 1428 (Rec 1429): keep current [([1, 2, 3, 4], [22, 23], 'POS')]

# 1429 (Rec 1430): [([17, 18, 19], [40, 41], 'POS'), ([45, 46, 47], [40, 41], 'POS')] (giảm ngập, POS)
updates[1429] = [([17, 18, 19], [40, 41], 'POS'), ([45, 46, 47], [40, 41], 'POS')]

# Apply updates
for idx in range(1380, 1430):
    parts = lines[idx].split("####")
    text = parts[0].strip()
    if idx in updates:
        trips = updates[idx]
        lines[idx] = f"{text}####{trips}"

with open(file_path, "w", encoding="utf-8") as f:
    for line in lines:
        f.write(f"{line}\n")

print(f"Đã cập nhật thành công {len(updates)} records trong Lô 43 (1381 - 1430).")
