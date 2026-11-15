import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# 1. REC 1281 (idx 1280): Fix polarity flip: bare 'ngập' NEG -> 'chấm dứt tình trạng' [34, 35, 36, 37], POS
text_1281 = lines[1280].split('####')[0]
updates[1280] = (
    text_1281,
    [([11, 12, 13, 14], [34, 35, 36, 37], 'POS')]
)

# 2. REC 1283 (idx 1282): Separate comma-joined opinion into discrete spans
text_1283 = lines[1282].split('####')[0]
updates[1282] = (
    text_1283,
    [
        ([14, 15, 16], [17, 18, 19], 'NEG'),
        ([14, 15, 16], [21, 22, 23, 24], 'NEG')
    ]
)

# 3. REC 1285 (idx 1284): Expand bare 'ngập' -> 'tình trạng ngập' [23, 24, 25], NEG
text_1285 = lines[1284].split('####')[0]
updates[1284] = (
    text_1285,
    [([1, 2, 3, 4], [23, 24, 25], 'NEG')]
)

# 4. REC 1286 (idx 1285): Strip passive 'bị' -> 'ngập sâu' [27, 28], NEG for all 4 streets
text_1286 = lines[1285].split('####')[0]
updates[1285] = (
    text_1286,
    [
        ([10, 11, 12], [27, 28], 'NEG'),
        ([14, 15, 16], [27, 28], 'NEG'),
        ([18, 19, 20], [27, 28], 'NEG'),
        ([22, 23, 24], [27, 28], 'NEG')
    ]
)

# 5. REC 1287 (idx 1286): Separate 18-token comma string into discrete spans
text_1287 = lines[1286].split('####')[0]
updates[1286] = (
    text_1287,
    [
        ([9], [10, 11, 12], 'NEG'),
        ([9], [14, 15], 'NEG')
    ]
)

# 6. REC 1289 (idx 1288): Strip passive 'bị' -> 'chết máy' [10, 11], NEG
text_1289 = lines[1288].split('####')[0]
updates[1288] = (
    text_1289,
    [([1, 2, 3, 4], [10, 11], 'NEG')]
)

# 7. REC 1292 (idx 1291): Expand bare 'ngập' -> 'nước ngập' [17, 18], NEG
text_1292 = lines[1291].split('####')[0]
updates[1291] = (
    text_1292,
    [([1, 2, 3, 4], [17, 18], 'NEG')]
)

# 8. REC 1293 (idx 1292): Expand bare 'ngập úng' -> 'ngập úng cục bộ' [39, 40, 41, 42], NEG
text_1293 = lines[1292].split('####')[0]
updates[1292] = (
    text_1293,
    [([1, 2, 3, 4], [39, 40, 41, 42], 'NEG')]
)

# 9. REC 1296 (idx 1295): Add 'dâng lên đến đầu gối' [7..11], NEG on 'đường Nguyễn Tuyến' [43..45]
text_1296 = lines[1295].split('####')[0]
updates[1295] = (
    text_1296,
    [
        ([43, 44, 45], [18], 'NEG'),
        ([43, 44, 45], [7, 8, 9, 10, 11], 'NEG')
    ]
)

# 10. REC 1297 (idx 1296): Expand bare 'ngập' -> 'nước ngập' [4, 5], NEG
text_1297 = lines[1296].split('####')[0]
updates[1296] = (
    text_1297,
    [([1], [4, 5], 'NEG')]
)

# 11. REC 1298 (idx 1297): Clean duplicate prefix 'Tại TPHCM , Tại TP. Hồ Chí Minh ,' -> single 'Tại TPHCM ,', fix bare 'rút' -> 'chờ nước rút' [21, 22, 23], NEG
raw_1298 = lines[1297].split('####')[0]
if raw_1298.startswith('Tại TPHCM , Tại TP. Hồ Chí Minh , '):
    text_1298 = raw_1298.replace('Tại TPHCM , Tại TP. Hồ Chí Minh , ', 'Tại TPHCM , ')
else:
    text_1298 = raw_1298
updates[1297] = (
    text_1298,
    [([1], [21, 22, 23], 'NEG')]
)

# 12. REC 1300 (idx 1299): Fix polarity flip: bare 'rút' POS -> 'ngập sâu' [18, 19], NEG
text_1300 = lines[1299].split('####')[0]
updates[1299] = (
    text_1300,
    [([1], [18, 19], 'NEG')]
)

# 13. REC 1301 (idx 1300): Strip passive 'bị' -> 'ngập nặng' [68, 69], NEG for all 9 streets
text_1301 = lines[1300].split('####')[0]
updates[1300] = (
    text_1301,
    [
        ([11, 12, 13], [68, 69], 'NEG'),
        ([15, 16, 17], [68, 69], 'NEG'),
        ([19, 20, 21], [68, 69], 'NEG'),
        ([28, 29, 30], [68, 69], 'NEG'),
        ([32, 33, 34], [68, 69], 'NEG'),
        ([36, 37, 38], [68, 69], 'NEG'),
        ([40, 41, 42], [68, 69], 'NEG'),
        ([44, 45, 46], [68, 69], 'NEG'),
        ([53, 54, 55], [68, 69], 'NEG')
    ]
)

# 14. REC 1305 (idx 1304): Separate comma string into discrete spans
text_1305 = lines[1304].split('####')[0]
updates[1304] = (
    text_1305,
    [
        ([4, 5, 6], [9, 10], 'NEG'),
        ([4, 5, 6], [12, 13, 14, 15], 'NEG')
    ]
)

# 15. REC 1308 (idx 1307): Strip passive 'bị' -> 'ngập nước kéo dài' [22, 23, 24, 25], NEG
text_1308 = lines[1307].split('####')[0]
updates[1307] = (
    text_1308,
    [([14, 15], [22, 23, 24, 25], 'NEG')]
)

# 16. REC 1309 (idx 1308): Strip passive 'bị' -> 'ngập nước sâu' [28, 29, 30], NEG
text_1309 = lines[1308].split('####')[0]
updates[1308] = (
    text_1309,
    [([1, 2, 3, 4], [28, 29, 30], 'NEG')]
)

# 17. REC 1310 (idx 1309): Expand bare 'ngập' -> 'ngập lút bánh xe máy' [23, 24, 25, 26, 27], NEG
text_1310 = lines[1309].split('####')[0]
updates[1309] = (
    text_1310,
    [([1], [23, 24, 25, 26, 27], 'NEG')]
)

# 18. REC 1311 (idx 1310): Add 'chết máy' [16, 17], NEG along with 'ngập' [14], NEG
text_1311 = lines[1310].split('####')[0]
updates[1310] = (
    text_1311,
    [
        ([1], [14], 'NEG'),
        ([1], [16, 17], 'NEG')
    ]
)

# 19. REC 1314 (idx 1313): Clean duplicate prefix 'Tại TPHCM , Tại TP. Hồ Chí Minh ,' -> single 'Tại TPHCM ,', fix bare 'rút' -> 'chờ nước rút' [18, 19, 20], NEG
raw_1314 = lines[1313].split('####')[0]
if raw_1314.startswith('Tại TPHCM , Tại TP. Hồ Chí Minh , '):
    text_1314 = raw_1314.replace('Tại TPHCM , Tại TP. Hồ Chí Minh , ', 'Tại TPHCM , ')
else:
    text_1314 = raw_1314
updates[1313] = (
    text_1314,
    [([1], [18, 19, 20], 'NEG')]
)

# 20. REC 1315 (idx 1314): Expand bare 'ngập' -> 'nước ngập kéo dài' [21, 22, 23, 24], NEG
text_1315 = lines[1314].split('####')[0]
updates[1314] = (
    text_1315,
    [([1], [21, 22, 23, 24], 'NEG')]
)

# 21. REC 1318 (idx 1317): Strip passive 'bị' -> 'ngập nặng' [40, 41], NEG for all 6 streets
text_1318 = lines[1317].split('####')[0]
updates[1317] = (
    text_1318,
    [
        ([18, 19, 20], [40, 41], 'NEG'),
        ([22, 23, 24], [40, 41], 'NEG'),
        ([26, 27], [40, 41], 'NEG'),
        ([29, 30, 31], [40, 41], 'NEG'),
        ([33, 34, 35], [40, 41], 'NEG'),
        ([37, 38], [40, 41], 'NEG')
    ]
)

# 22. REC 1319 (idx 1318): Separate comma string into discrete spans
text_1319 = lines[1318].split('####')[0]
updates[1318] = (
    text_1319,
    [
        ([5, 6, 7], [8, 9], 'NEG'),
        ([5, 6, 7], [13, 14, 15, 16, 17], 'NEG')
    ]
)

# 23. REC 1320 (idx 1319): Expand bare 'ngập' -> 'ngập nghiêm trọng hơn' [29, 30, 31, 32], NEG
text_1320 = lines[1319].split('####')[0]
updates[1319] = (
    text_1320,
    [([1], [29, 30, 31, 32], 'NEG')]
)

# 24. REC 1321 (idx 1320): Separate comma string into discrete spans
text_1321 = lines[1320].split('####')[0]
updates[1320] = (
    text_1321,
    [
        ([10, 11, 12], [13, 14, 15], 'NEG'),
        ([10, 11, 12], [17, 18, 19, 20], 'NEG')
    ]
)

# 25. REC 1322 (idx 1321): Fix preposition leakage & non-geographic aspect: 'Triều cường ở TPHCM' -> 'TPHCM' [3], 'ngập sâu' [6, 7], NEG
text_1322 = lines[1321].split('####')[0]
updates[1321] = (
    text_1322,
    [([3], [6, 7], 'NEG')]
)

# 26. REC 1326 (idx 1325): Remove non-geographic aspect 'triều cường ở TP. HCM', keep 3 clean streets
text_1326 = lines[1325].split('####')[0]
updates[1325] = (
    text_1326,
    [
        ([29, 30, 31, 32], [19, 20, 21, 22], 'NEG'),
        ([39, 40, 41], [19, 20, 21, 22], 'NEG'),
        ([43, 44, 45], [19, 20, 21, 22], 'NEG')
    ]
)

# 27. REC 1328 (idx 1327): Add 'nước ngập sâu' [11, 12, 13], NEG along with 'chìm trong nước' [5, 6, 7], NEG
text_1328 = lines[1327].split('####')[0]
updates[1327] = (
    text_1328,
    [
        ([2, 3, 4], [5, 6, 7], 'NEG'),
        ([2, 3, 4], [11, 12, 13], 'NEG')
    ]
)

# 28. REC 1329 (idx 1328): Expand bare 'ngập' -> 'rốn ngập' [12, 13], NEG
text_1329 = lines[1328].split('####')[0]
updates[1328] = (
    text_1329,
    [([1], [12, 13], 'NEG')]
)

# Apply updates to lines
count = 0
for idx, (new_text, new_triplets) in updates.items():
    toks = new_text.split()
    # verify tokens
    for asp, opi, pol in new_triplets:
        asp_str = " ".join(toks[k] for k in asp)
        opi_str = " ".join(toks[k] for k in opi)
        assert all(0 <= k < len(toks) for k in asp), f"Asp index OOB in line {idx+1}: {asp}"
        assert all(0 <= k < len(toks) for k in opi), f"Opi index OOB in line {idx+1}: {opi}"
    lines[idx] = f"{new_text}####{new_triplets}"
    count += 1

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print(f"Successfully updated {count} records in Batch 41 (lines 1281-1330).")
