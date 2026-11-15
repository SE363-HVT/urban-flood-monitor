import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# 1. REC 1188 (idx 1187): Expand bare 'rút' POS -> 'chờ nước rút' [20, 21, 22], NEG
text_1188 = lines[1187].split('####')[0]
updates[1187] = (
    text_1188,
    [([1], [20, 21, 22], 'NEG')]
)

# 2. REC 1191 (idx 1190): Add 'chết máy' [19, 20], NEG along with 'ngập sâu' [29, 30], NEG
text_1191 = lines[1190].split('####')[0]
updates[1190] = (
    text_1191,
    [
        ([8, 9, 10, 11], [19, 20], 'NEG'),
        ([8, 9, 10, 11], [29, 30], 'NEG')
    ]
)

# 3. REC 1193 (idx 1192): Anti-overtagging (remove phường Linh Đông, keep chợ Thủ Đức)
text_1193 = lines[1192].split('####')[0]
updates[1192] = (
    text_1193,
    [([2, 3, 4], [22, 23, 24, 25, 26], 'NEG')]
)

# 4. REC 1194 (idx 1193): Separate comma-joined opinion into discrete spans
text_1194 = lines[1193].split('####')[0]
updates[1193] = (
    text_1194,
    [
        ([1, 2, 3, 4], [7, 8, 9, 10], 'NEG'),
        ([1, 2, 3, 4], [20, 21], 'NEG')
    ]
)

# 5. REC 1196 (idx 1195): Strip passive 'bị' for all 4 locations -> 'ngập rất sâu' [53, 54, 55], NEG
text_1196 = lines[1195].split('####')[0]
updates[1195] = (
    text_1196,
    [
        ([18, 19, 20], [53, 54, 55], 'NEG'),
        ([30, 31, 32], [53, 54, 55], 'NEG'),
        ([34, 35, 36], [53, 54, 55], 'NEG'),
        ([46, 47, 48, 49, 50], [53, 54, 55], 'NEG')
    ]
)

# 6. REC 1199 (idx 1198): Separate comma-joined opinion into discrete spans
text_1199 = lines[1198].split('####')[0]
updates[1198] = (
    text_1199,
    [
        ([1, 2, 3, 4], [10, 11], 'NEG'),
        ([1, 2, 3, 4], [14, 15], 'NEG')
    ]
)

# 7. REC 1200 (idx 1199): Strip passive 'bị' -> 'ngập sâu' [22, 23], NEG
text_1200 = lines[1199].split('####')[0]
updates[1199] = (
    text_1200,
    [([15, 16], [22, 23], 'NEG')]
)

# 8. REC 1201 (idx 1200): Strip passive 'bị' -> 'ngập nặng nề' [9, 10, 11], NEG
text_1201 = lines[1200].split('####')[0]
updates[1200] = (
    text_1201,
    [([5, 6, 7], [9, 10, 11], 'NEG')]
)

# 9. REC 1203 (idx 1202): Expand bare 'ngập' -> 'ngập lên hơn bánh xe máy' [7..12], NEG
text_1203 = lines[1202].split('####')[0]
updates[1202] = (
    text_1203,
    [([1], [7, 8, 9, 10, 11, 12], 'NEG')]
)

# 10. REC 1204 (idx 1203): Separate compound opinion into discrete spans
text_1204 = lines[1203].split('####')[0]
updates[1203] = (
    text_1204,
    [
        ([5, 6, 7], [10, 11, 12], 'NEG'),
        ([5, 6, 7], [14, 15, 16, 17, 18], 'NEG')
    ]
)

# 11. REC 1206 (idx 1205): Clean opinion span to 'ngập' [18], NEG
text_1206 = lines[1205].split('####')[0]
updates[1205] = (
    text_1206,
    [([1, 2, 3, 4], [18], 'NEG')]
)

# 12. REC 1207 (idx 1206): Separate comma-joined opinion into discrete spans
text_1207 = lines[1206].split('####')[0]
updates[1206] = (
    text_1207,
    [
        ([8, 9, 10, 11], [12, 13, 14, 15], 'NEG'),
        ([8, 9, 10, 11], [17, 18, 19, 20], 'NEG')
    ]
)

# 13. REC 1208 (idx 1207): Expand bare 'ngập' -> 'ngập hơn chục năm nay' [19..23], NEG
text_1208 = lines[1207].split('####')[0]
updates[1207] = (
    text_1208,
    [([1], [19, 20, 21, 22, 23], 'NEG')]
)

# 14. REC 1209 (idx 1208): Expand bare verb 'rút' -> 'rút hết' [21, 22], POS
text_1209 = lines[1208].split('####')[0]
updates[1208] = (
    text_1209,
    [([1], [21, 22], 'POS')]
)

# 15. REC 1213 (idx 1212): Fix missing verb -> 'ngập hơn nửa bánh xe máy' [9..14], NEG
text_1213 = lines[1212].split('####')[0]
updates[1212] = (
    text_1213,
    [([1], [9, 10, 11, 12, 13, 14], 'NEG')]
)

# 16. REC 1215 (idx 1214): Separate comma-joined opinion into discrete spans
text_1215 = lines[1214].split('####')[0]
updates[1214] = (
    text_1215,
    [
        ([1], [5], 'NEG'),
        ([1], [14, 15, 16], 'NEG')
    ]
)

# 17. REC 1217 (idx 1216): Expand bare 'ngập' -> 'ngập khắp nơi' [4, 5, 6], NEG
text_1217 = lines[1216].split('####')[0]
updates[1216] = (
    text_1217,
    [([1], [4, 5, 6], 'NEG')]
)

# 18. REC 1218 (idx 1217): Fix DOC_FALLBACK_MISUSE & polarity flip -> Aspect 'chợ Thủ Đức' [17, 18, 19], 'giải quyết giảm ngập' [9..12], POS
text_1218 = lines[1217].split('####')[0]
updates[1217] = (
    text_1218,
    [([17, 18, 19], [9, 10, 11, 12], 'POS')]
)

# 19. REC 1219 (idx 1218): Expand bare 'ngập' -> 'ngập cục bộ' [15, 16, 17], NEG
text_1219 = lines[1218].split('####')[0]
updates[1218] = (
    text_1219,
    [([1], [15, 16, 17], 'NEG')]
)

# 20. REC 1221 (idx 1220): Expand bare 'ngập' -> 'rốn ngập' [10, 11], NEG
text_1221 = lines[1220].split('####')[0]
updates[1220] = (
    text_1221,
    [([1], [10, 11], 'NEG')]
)

# 21. REC 1222 (idx 1221): Fix polarity flip: bare 'ngập' NEG -> 'giải quyết ngập cục bộ' [34..38], POS
text_1222 = lines[1221].split('####')[0]
updates[1221] = (
    text_1222,
    [([1], [34, 35, 36, 37, 38], 'POS')]
)

# 22. REC 1223 (idx 1222): Fix polarity flip: bare 'ngập' NEG -> 'chống ngập' [17, 18], POS
text_1223 = lines[1222].split('####')[0]
updates[1222] = (
    text_1223,
    [([1, 2, 3, 4], [17, 18], 'POS')]
)

# 23. REC 1224 (idx 1223): Fix polarity flip: bare 'ngập' NEG -> 'chống ngập' [26, 27], POS
text_1224 = lines[1223].split('####')[0]
updates[1223] = (
    text_1224,
    [([3, 4], [26, 27], 'POS')]
)

# 24. REC 1225 (idx 1224): Strip passive 'bị' -> 'ngập' [27], NEG
text_1225 = lines[1224].split('####')[0]
updates[1224] = (
    text_1225,
    [
        ([33, 34, 35, 36], [27], 'NEG'),
        ([41, 42, 43, 44], [45, 46, 47, 48, 49], 'NEG')
    ]
)

# 25. REC 1227 (idx 1226): Fix DOC_FALLBACK_MISUSE -> Aspect 'chợ Thủ Đức' [9, 10, 11], 'chống ngập' [4, 5], POS
text_1227 = lines[1226].split('####')[0]
updates[1226] = (
    text_1227,
    [([9, 10, 11], [4, 5], 'POS')]
)

# 26. REC 1228 (idx 1227): Fix preposition leakage & non-geographic aspect: 'triều cường ở TPHCM' -> 'TPHCM' [18], 'vẫn ngập' [10, 11], NEG
text_1228 = lines[1227].split('####')[0]
updates[1227] = (
    text_1228,
    [([18], [10, 11], 'NEG')]
)

# 27. REC 1229 (idx 1228): Fix polarity inversion: bare 'ngập' NEG -> 'không còn ngập' [33, 34, 35], POS
text_1229 = lines[1228].split('####')[0]
updates[1228] = (
    text_1229,
    [([1], [33, 34, 35], 'POS')]
)

# 28. REC 1230 (idx 1229): Expand bare 'ngập' -> 'nước ngập' [6, 7], NEG and 'bốc mùi' [17, 18], NEG
text_1230 = lines[1229].split('####')[0]
updates[1229] = (
    text_1230,
    [
        ([1], [6, 7], 'NEG'),
        ([1], [17, 18], 'NEG')
    ]
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

print(f"Successfully updated {count} records in Batch 39 (lines 1181-1230).")
