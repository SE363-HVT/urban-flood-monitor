import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# 1. REC 1081 (idx 1080): Remove landmark chợ Thủ Đức, keep 3 branch streets
text_1081 = lines[1080].split('####')[0]
updates[1080] = (
    text_1081,
    [
        ([21, 22, 23], [33, 34, 35], 'NEG'),
        ([25, 26, 27], [33, 34, 35], 'NEG'),
        ([29, 30, 31], [33, 34, 35], 'NEG')
    ]
)

# 2. REC 1082 (idx 1081): Separate long comma-joined opinion into clean discrete spans
text_1082 = lines[1081].split('####')[0]
updates[1081] = (
    text_1082,
    [
        ([1], [9, 10], 'NEG'),
        ([1], [12, 13, 14, 15], 'NEG')
    ]
)

# 3. REC 1084 (idx 1083): Clean comma-joined opinion -> 'ngập lút bánh xe máy' [13..17], NEG
text_1084 = lines[1083].split('####')[0]
updates[1083] = (
    text_1084,
    [
        ([3, 4, 5, 6], [13, 14, 15, 16, 17], 'NEG'),
        ([8, 9, 10], [13, 14, 15, 16, 17], 'NEG')
    ]
)

# 4. REC 1085 (idx 1084): Fix bare generic noun 'chợ' [56] -> Prepend 'Tại TPHCM , ' fallback prefix
raw_1085 = lines[1084].split('####')[0]
if not raw_1085.startswith('Tại TPHCM , '):
    text_1085 = 'Tại TPHCM , ' + raw_1085
else:
    text_1085 = raw_1085
updates[1084] = (
    text_1085,
    [([1], [54, 55, 56, 57], 'NEG')]
)

# 5. REC 1086 (idx 1085): Separate comma-joined opinion into discrete spans
text_1086 = lines[1085].split('####')[0]
updates[1085] = (
    text_1086,
    [
        ([1, 2, 3, 4], [20, 21], 'NEG'),
        ([1, 2, 3, 4], [23, 24, 25], 'NEG')
    ]
)

# 6. REC 1089 (idx 1088): Remove landmark chợ Thủ Đức, keep 7 branch streets
text_1089 = lines[1088].split('####')[0]
updates[1088] = (
    text_1089,
    [
        ([2, 3, 4], [38, 39, 40, 41], 'NEG'),
        ([6, 7, 8], [38, 39, 40, 41], 'NEG'),
        ([10, 11], [38, 39, 40, 41], 'NEG'),
        ([13, 14, 15], [38, 39, 40, 41], 'NEG'),
        ([25, 26, 27], [38, 39, 40, 41], 'NEG'),
        ([29, 30, 31], [38, 39, 40, 41], 'NEG'),
        ([33, 34, 35], [38, 39, 40, 41], 'NEG')
    ]
)

# 7. REC 1090 (idx 1089): Clean comma-joined opinion into discrete spans 'ngập sâu cả mét' [7..10] & 'chết máy' [17, 18]
text_1090 = lines[1089].split('####')[0]
updates[1089] = (
    text_1090,
    [
        ([1, 2, 3, 4], [7, 8, 9, 10], 'NEG'),
        ([1, 2, 3, 4], [17, 18], 'NEG')
    ]
)

# 8. REC 1093 (idx 1092): Clean comma-joined opinion into discrete spans
text_1093 = lines[1092].split('####')[0]
updates[1092] = (
    text_1093,
    [
        ([1, 2, 3, 4], [13, 14, 15, 16, 17, 18, 19], 'NEG'),
        ([1, 2, 3, 4], [30, 31], 'NEG')
    ]
)

# 9. REC 1094 (idx 1093): Out-of-scope province 'Bình Dương' tagged as aspect -> REJECT (####[])
text_1094 = lines[1093].split('####')[0]
updates[1093] = (
    text_1094,
    []
)

# 10. REC 1095 (idx 1094): Fix bare verb 'rút' POS -> 'Chờ nước rút' [3, 4, 5], NEG
text_1095 = lines[1094].split('####')[0]
updates[1094] = (
    text_1095,
    [([1], [3, 4, 5], 'NEG')]
)

# 11. REC 1096 (idx 1095): Anti-overtagging (remove ward phường Linh Xuân), shorten messy 31-token opinion -> 'ngập sâu' [2, 3], NEG
text_1096 = lines[1095].split('####')[0]
updates[1095] = (
    text_1096,
    [([33, 34, 35], [2, 3], 'NEG')]
)

# 12. REC 1097 (idx 1096): Anti-overtagging (remove wards phường Tam Bình & phường Bình Chiểu, keep tỉnh lộ 43)
text_1097 = lines[1096].split('####')[0]
updates[1096] = (
    text_1097,
    [([3, 4, 5], [31, 32], 'NEG')]
)

# 13. REC 1098 (idx 1097): Anti-overtagging (remove ward phường Tam Bình, keep tỉnh lộ 43)
text_1098 = lines[1097].split('####')[0]
updates[1097] = (
    text_1098,
    [([3, 4, 5], [17, 18, 19, 20, 21], 'NEG')]
)

# 14. REC 1101 (idx 1100): Expand bare noun 'ngập' -> 'ngập càng thêm trầm trọng' [27..31], NEG
text_1101 = lines[1100].split('####')[0]
updates[1100] = (
    text_1101,
    [([1], [27, 28, 29, 30, 31], 'NEG')]
)

# 15. REC 1102 (idx 1101): Remove duplicate aspect 'Hẻm 789', strip passive 'bị' -> 'ngập nặng' [11, 12], NEG
text_1102 = lines[1101].split('####')[0]
updates[1101] = (
    text_1102,
    [([3, 4, 5], [11, 12], 'NEG')]
)

# 16. REC 1103 (idx 1102): Expand bare 'ngập' -> 'ngập hết' [24, 25], NEG
text_1103 = lines[1102].split('####')[0]
updates[1102] = (
    text_1103,
    [([1], [24, 25], 'NEG')]
)

# 17. REC 1105 (idx 1104): Strip passive 'bị' -> 'nước tràn vào' [32, 33, 34], NEG
text_1105 = lines[1104].split('####')[0]
updates[1104] = (
    text_1105,
    [([3, 4, 5], [32, 33, 34], 'NEG')]
)

# 18. REC 1106 (idx 1105): Remove ward 'phường Tam Bình', tag 2 streets where pumps were deployed with 'giảm ngập' [47, 48], POS
text_1106 = lines[1105].split('####')[0]
updates[1105] = (
    text_1106,
    [
        ([26, 27, 28], [47, 48], 'POS'),
        ([37, 38, 39], [47, 48], 'POS')
    ]
)

# 19. REC 1107 (idx 1106): Strip passive 'bị' for all 7 streets -> 'ngập' [10], NEG
text_1107 = lines[1106].split('####')[0]
updates[1106] = (
    text_1107,
    [
        ([12, 13, 14, 15], [10], 'NEG'),
        ([17, 18, 19], [10], 'NEG'),
        ([21, 22, 23], [10], 'NEG'),
        ([25, 26], [10], 'NEG'),
        ([28, 29, 30], [10], 'NEG'),
        ([32, 33], [10], 'NEG'),
        ([35, 36, 37], [10], 'NEG')
    ]
)

# 20. REC 1112 (idx 1111): Expand bare 'ngập sâu' -> 'ngập sâu lút bánh xe' [16..20], NEG
text_1112 = lines[1111].split('####')[0]
updates[1111] = (
    text_1112,
    [([1], [16, 17, 18, 19, 20], 'NEG')]
)

# 21. REC 1114 (idx 1113): Clean long string into discrete spans
text_1114 = lines[1113].split('####')[0]
updates[1113] = (
    text_1114,
    [
        ([1, 2, 3, 4], [11, 12, 13, 14, 15], 'NEG'),
        ([1, 2, 3, 4], [22, 23, 24], 'NEG')
    ]
)

# 22. REC 1117 (idx 1116): Fix polarity inversion: bare 'ngập' NEG -> 'giảm ngập' [1, 2], POS
text_1117 = lines[1116].split('####')[0]
updates[1116] = (
    text_1117,
    [([9, 10], [1, 2], 'POS')]
)

# 23. REC 1119 (idx 1118): Fix polarity inversion: bare 'ngập' NEG -> 'chống ngập' [17, 18], POS
text_1119 = lines[1118].split('####')[0]
updates[1118] = (
    text_1119,
    [([8, 9], [17, 18], 'POS')]
)

# 24. REC 1120 (idx 1119): Strip passive 'bị' -> 'ngập dai dẳng' [11, 12, 13], NEG
text_1120 = lines[1119].split('####')[0]
updates[1119] = (
    text_1120,
    [([4, 5], [11, 12, 13], 'NEG')]
)

# 25. REC 1122 (idx 1121): Strip passive 'bị' -> 'ngập sâu' [20, 21], NEG for all 4 streets
text_1122 = lines[1121].split('####')[0]
updates[1121] = (
    text_1122,
    [
        ([32, 33, 34], [20, 21], 'NEG'),
        ([36, 37, 38], [20, 21], 'NEG'),
        ([40, 41, 42], [20, 21], 'NEG'),
        ([44, 45, 46], [20, 21], 'NEG')
    ]
)

# 26. REC 1123 (idx 1122): Strip passive 'bị' -> 'ngập sâu' [21, 22], NEG
text_1123 = lines[1122].split('####')[0]
updates[1122] = (
    text_1123,
    [([6, 7, 8], [21, 22], 'NEG')]
)

# 27. REC 1126 (idx 1125): Add 'chôn chân' [22, 23], NEG along with 'ngập' [32], NEG
text_1126 = lines[1125].split('####')[0]
updates[1125] = (
    text_1126,
    [
        ([1, 2, 3, 4], [22, 23], 'NEG'),
        ([1, 2, 3, 4], [32], 'NEG')
    ]
)

# 28. REC 1127 (idx 1126): Strip passive 'bị' and comma -> clean discrete 'chết máy' [11, 12], NEG
text_1127 = lines[1126].split('####')[0]
updates[1126] = (
    text_1127,
    [([1, 2, 3, 4], [11, 12], 'NEG')]
)

# 29. REC 1129 (idx 1128): Fix DOC_FALLBACK_MISUSE -> Tag explicit 'TP Thủ Đức' [14, 15, 16], 'ngập nước' [9, 10], NEG
text_1129 = lines[1128].split('####')[0]
updates[1128] = (
    text_1129,
    [([14, 15, 16], [9, 10], 'NEG')]
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

print(f"Successfully updated {count} records in Batch 37 (lines 1081-1130).")
