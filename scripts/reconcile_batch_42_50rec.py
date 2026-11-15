import sys
import ast

sys.stdout.reconfigure(encoding="utf-8")

file_path = "data/validate_label/thuan/phase2.txt"

with open(file_path, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f]

# Dictionary of adjustments for records 1330 to 1379 (0-based)
updates = {}

# 1330 (Rec 1331): [([1], [6, 7, 8, 9, 10, 11, 12], 'NEG')] (ngập lên đến hơn bánh xe máy)
updates[1330] = [([1], [6, 7, 8, 9, 10, 11, 12], 'NEG')]

# 1331 (Rec 1332): [([15, 16, 17], [2, 3], 'NEG')] (đường Quốc Hương, ngập sâu)
updates[1331] = [([15, 16, 17], [2, 3], 'NEG')]

# 1332 (Rec 1333): [([1, 2, 3, 4], [9, 10], 'NEG')] (strip 'bị' -> chết máy)
updates[1332] = [([1, 2, 3, 4], [9, 10], 'NEG')]

# 1333 (Rec 1334): [([1], [26, 27, 28], 'NEG')] (chờ nước rút, NEG)
updates[1333] = [([1], [26, 27, 28], 'NEG')]

# 1334 (Rec 1335): keep current [([1, 2, 3, 4], [12, 13], 'NEG')] (lội nước)

# 1335 (Rec 1336): [([1], [22, 23, 24, 25], 'NEG')] (nước tràn vào nhà)
updates[1335] = [([1], [22, 23, 24, 25], 'NEG')]

# 1336 (Rec 1337): keep current [([6, 7, 8], [9, 10, 11, 12, 13], 'NEG')] (đã ngập gần 3 tiếng)

# 1337 (Rec 1338): keep current [([8, 9, 10, 11], [19, 20, 21], 'POS')] (giải quyết ngập)

# 1338 (Rec 1339): keep current [([1], [39, 40], 'POS')] (chống ngập)

# 1339 (Rec 1340): keep current [([6, 7, 8, 9], [22, 23, 24], 'POS')] (giải quyết ngập)

# 1340 (Rec 1341): keep current [([21, 22], [16], 'NEG')] (ngập)

# 1341 (Rec 1342): keep current [([6, 7, 8, 9], [19, 20, 21, 22, 23, 24], 'NEG'), ([11, 12, 13, 14], [19, 20, 21, 22, 23, 24], 'NEG')]

# 1342 (Rec 1343): [([46, 47, 48, 49], [43, 44], 'POS')] (chống ngập do triều cường ở TPHCM -> POS)
updates[1342] = [([46, 47, 48, 49], [43, 44], 'POS')]

# 1343 (Rec 1344): [([0, 1], [2, 3], 'NEU')] (TP. HCM chống ngập do triều cường ở TPHCM thế nào ? -> NEU)
updates[1343] = [([0, 1], [2, 3], 'NEU')]

# 1344 (Rec 1345): [([31, 32], [22, 23, 24, 25, 26, 27], 'POS')] (giải quyết tình hình ngập nước)
updates[1344] = [([31, 32], [22, 23, 24, 25, 26, 27], 'POS')]

# 1345 (Rec 1346): [([30, 31, 32, 33], [25, 26], 'POS')] (giảm ngập -> POS)
updates[1345] = [([30, 31, 32, 33], [25, 26], 'POS')]

# 1346 (Rec 1347): [([44, 45], [12, 13, 14], 'POS'), ([49, 50, 51], [12, 13, 14], 'POS'), ([55, 56, 57], [12, 13, 14], 'POS')]
updates[1346] = [([44, 45], [12, 13, 14], 'POS'), ([49, 50, 51], [12, 13, 14], 'POS'), ([55, 56, 57], [12, 13, 14], 'POS')]

# 1347 (Rec 1348): [([24, 25, 26, 27], [33, 34, 35, 36, 37], 'POS')] (giải quyết triệt để ngập -> POS)
updates[1347] = [([24, 25, 26, 27], [33, 34, 35, 36, 37], 'POS')]

# 1348 (Rec 1349): [([13, 14], [7, 8, 9], 'POS'), ([19, 20], [7, 8, 9], 'POS'), ([22, 23, 24], [7, 8, 9], 'POS')]
updates[1348] = [([13, 14], [7, 8, 9], 'POS'), ([19, 20], [7, 8, 9], 'POS'), ([22, 23, 24], [7, 8, 9], 'POS')]

# 1349 (Rec 1350): [([7, 8], [3, 4, 5], 'POS')] (chống ngập nước -> POS)
updates[1349] = [([7, 8], [3, 4, 5], 'POS')]

# 1350 (Rec 1351): [([15, 16, 17, 18], [13], 'NEU')] (Ngập do triều cường ở TPHCM -> NEU)
updates[1350] = [([15, 16, 17, 18], [13], 'NEU')]

# 1351 (Rec 1352): [([12, 13, 14, 15], [9, 10], 'POS')] (chống ngập -> POS)
updates[1351] = [([12, 13, 14, 15], [9, 10], 'POS')]

# 1352 (Rec 1353): keep current [([19, 20, 21, 22], [29, 30, 31, 32, 33, 34, 35, 36], 'POS')]

# 1353 (Rec 1354): keep current [([1, 2, 3, 4], [16, 17], 'NEG')]

# 1354 (Rec 1355): keep current [([4, 5, 6, 7], [20, 21, 22], 'NEG')]

# 1355 (Rec 1356): keep current [([1, 2, 3, 4], [24, 25], 'NEG')]

# 1356 (Rec 1357): [([9], [28, 29], 'NEG')] (ngập sâu, strip bị & comma)
updates[1356] = [([9], [28, 29], 'NEG')]

# 1357 (Rec 1358): [([9, 10, 11, 12], [20, 21, 22, 23, 24], 'NEG'), ([9, 10, 11, 12], [31, 32], 'NEG')]
updates[1357] = [([9, 10, 11, 12], [20, 21, 22, 23, 24], 'NEG'), ([9, 10, 11, 12], [31, 32], 'NEG')]

# 1358 (Rec 1359): keep current [([1, 2, 3, 4], [14, 15], 'NEG')]

# 1359 (Rec 1360): [([28, 29, 30, 31], [9, 10], 'NEG')]
updates[1359] = [([28, 29, 30, 31], [9, 10], 'NEG')]

# 1360 (Rec 1361): keep current [([1], [23, 24, 25], 'NEG')]

# 1361 (Rec 1362): keep current [([1], [4, 5], 'NEG')]

# 1362 (Rec 1363): [([1], [9, 10], 'NEG'), ([1], [18, 19], 'NEG')] (chết máy, dắt bộ)
updates[1362] = [([1], [9, 10], 'NEG'), ([1], [18, 19], 'NEG')]

# 1363 (Rec 1364): [([1], [12, 13, 14], 'NEG')] (lội bì bõm)
updates[1363] = [([1], [12, 13, 14], 'NEG')]

# 1364 (Rec 1365): [([1], [9], 'NEG')] (ngập, strip comma and bị)
updates[1364] = [([1], [9], 'NEG')]

# 1365 (Rec 1366): keep current [([1], [28, 29, 30], 'NEG')]

# 1366 (Rec 1367): [([1], [11, 12, 13, 14], 'NEG')] (ngập nửa bánh xe)
updates[1366] = [([1], [11, 12, 13, 14], 'NEG')]

# 1367 (Rec 1368): keep current [([1, 2, 3, 4], [20, 21], 'NEG')]

# 1368 (Rec 1369): [([1, 2, 3, 4], [11, 12], 'POS')] (hết ngập -> POS)
updates[1368] = [([1, 2, 3, 4], [11, 12], 'POS')]

# 1369 (Rec 1370): keep current [([1], [5, 6], 'NEG')]

# 1370 (Rec 1371): keep current [([33, 34, 35, 36], [31, 32], 'POS')]

# 1371 (Rec 1372): keep current [([2, 3, 4, 5], [6, 7, 8], 'NEG')]

# 1372 (Rec 1373): keep current [([1], [14, 15], 'POS')]

# 1373 (Rec 1374): keep current [([24, 25, 26, 27], [19, 20], 'POS')]

# 1374 (Rec 1375): keep current [([23, 24, 25, 26], [20, 21], 'POS')]

# 1375 (Rec 1376): [([1, 2, 3, 4], [12, 13], 'NEG')] (ngập nặng, strip bị)
updates[1375] = [([1, 2, 3, 4], [12, 13], 'NEG')]

# 1376 (Rec 1377): keep current [([1], [4, 5], 'NEG')]

# 1377 (Rec 1378): [([26, 27], [29, 30, 31, 32], 'POS')] (kênh Tẻ, thoát cảnh ngập nước -> POS)
updates[1377] = [([26, 27], [29, 30, 31, 32], 'POS')]

# 1378 (Rec 1379): [([23, 24, 25, 26], [20, 21, 22], 'POS')] (chống ngập nước -> POS)
updates[1378] = [([23, 24, 25, 26], [20, 21, 22], 'POS')]

# 1379 (Rec 1380): keep current [([7, 8, 9, 10], [11, 12], 'NEG')]

# Apply updates
for idx in range(1330, 1380):
    parts = lines[idx].split("####")
    text = parts[0].strip()
    if idx in updates:
        trips = updates[idx]
        lines[idx] = f"{text}####{trips}"

with open(file_path, "w", encoding="utf-8") as f:
    for line in lines:
        f.write(f"{line}\n")

print(f"Đã cập nhật thành công {len(updates)} records trong Lô 42 (1331 - 1380).")
