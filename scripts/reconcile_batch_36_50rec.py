import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# 1. REC 1035 (idx 1034): Multi-level duplication (remove landmark chợ Thủ Đức, keep 2 streets with clean 'ngập sâu' [28, 29])
text_1035 = lines[1034].split('####')[0]
updates[1034] = (
    text_1035,
    [
        ([16, 17, 18], [28, 29], 'NEG'),
        ([20, 21, 22], [28, 29], 'NEG')
    ]
)

# 2. REC 1036 (idx 1035): Expand bare verb 'rút' POS -> 'chờ nước rút' [15, 16, 17], NEG
text_1036 = lines[1035].split('####')[0]
updates[1035] = (
    text_1036,
    [([1], [15, 16, 17], 'NEG')]
)

# 3. REC 1038 (idx 1037): Expand bare verb 'rút' POS -> 'chờ nước rút' [13, 14, 15], NEG
text_1038 = lines[1037].split('####')[0]
updates[1037] = (
    text_1038,
    [([1], [13, 14, 15], 'NEG')]
)

# 4. REC 1039 (idx 1038): Landmark removal (remove chợ Thủ Đức, keep 3 branch streets)
text_1039 = lines[1038].split('####')[0]
updates[1038] = (
    text_1039,
    [
        ([17, 18, 19], [35, 36], 'NEG'),
        ([21, 22, 23], [35, 36], 'NEG'),
        ([25, 26, 27], [35, 36], 'NEG')
    ]
)

# 5. REC 1040 (idx 1039): Aspect is 'TP. Thủ Đức' [17, 18, 19], opinion 'ngập' [25], NEG (avoid bare noun 'điểm ngập' per Pass 10)
text_1040 = lines[1039].split('####')[0]
updates[1039] = (
    text_1040,
    [([17, 18, 19], [25], 'NEG')]
)

# 6. REC 1042 (idx 1041): Expand compound 'ngập' -> 'ngập cục bộ' [16, 17, 18], NEG
text_1042 = lines[1041].split('####')[0]
updates[1041] = (
    text_1042,
    [([1], [16, 17, 18], 'NEG')]
)

# 7. REC 1043 (idx 1042): Fix distorted long cross-sentence link -> Clean aspects: 'TP. Thủ Đức' [4, 5, 6] -> 'rốn ngập' [2, 3], NEG; 'TP. Thủ Đức' [79, 80, 81] -> 'ngập nước' [74, 75], NEG
text_1043 = lines[1042].split('####')[0]
updates[1042] = (
    text_1043,
    [
        ([4, 5, 6], [2, 3], 'NEG'),
        ([79, 80, 81], [74, 75], 'NEG')
    ]
)

# 8. REC 1046 (idx 1045): Connect 'ngập' [39] to nearest explicit target 'chợ Thủ Đức' [32, 33, 34]
text_1046 = lines[1045].split('####')[0]
updates[1045] = (
    text_1046,
    [([32, 33, 34], [39], 'NEG')]
)

# 9. REC 1047 (idx 1046): Add all 5 parallel street targets for 'giải quyết ngập' [14, 15, 16], POS
text_1047 = lines[1046].split('####')[0]
updates[1046] = (
    text_1047,
    [
        ([24, 25, 26, 27], [14, 15, 16], 'POS'),
        ([29, 30, 31, 32], [14, 15, 16], 'POS'),
        ([34, 35, 36, 37], [14, 15, 16], 'POS'),
        ([39, 40, 41, 42], [14, 15, 16], 'POS'),
        ([44, 45, 46, 47], [14, 15, 16], 'POS')
    ]
)

# 10. REC 1048 (idx 1047): 'Ngoài đường Võ Văn Ngân thì 4 tuyến đường còn lại ngập sâu...': 
# The only named street is excluded, flooded roads are anonymous generic entities -> REJECT (####[])
raw_text_1048 = lines[1047].split('####')[0]
if raw_text_1048.startswith('Tại TPHCM , '):
    text_1048 = raw_text_1048[len('Tại TPHCM , '):]
else:
    text_1048 = raw_text_1048
updates[1047] = (
    text_1048,
    []
)

# 11. REC 1052 (idx 1051): Anti-overtagging (remove wards P. Thảo Điền & P. Phước Long B, keep 4 streets)
text_1052 = lines[1051].split('####')[0]
updates[1051] = (
    text_1052,
    [
        ([40, 41, 42], [35, 36], 'NEG'),
        ([49, 50, 51, 52], [35, 36], 'NEG'),
        ([54, 55, 56, 57], [35, 36], 'NEG'),
        ([65, 66, 67], [35, 36], 'NEG')
    ]
)

# 12. REC 1056 (idx 1055): Add direct flood descriptor 'ngập sâu' [26, 27] to 'TP. Hồ Chí Minh' [1, 2, 3, 4]
text_1056 = lines[1055].split('####')[0]
updates[1055] = (
    text_1056,
    [
        ([1, 2, 3, 4], [21, 22], 'NEG'),
        ([1, 2, 3, 4], [26, 27], 'NEG')
    ]
)

# 13. REC 1060 (idx 1059): Fix inverted polarity ('ngập' NEG -> 'Giải quyết ngập' [8, 9, 10], POS)
text_1060 = lines[1059].split('####')[0]
updates[1059] = (
    text_1060,
    [([16, 17], [8, 9, 10], 'POS')]
)

# 14. REC 1062 (idx 1061): Aspect preposition leakage & clean entity ('triều cường ở TPHCM' -> 'TPHCM' [22], opinion 'tình trạng ngập' [52, 53, 54], NEG)
text_1062 = lines[1061].split('####')[0]
updates[1061] = (
    text_1062,
    [([22], [52, 53, 54], 'NEG')]
)

# 15. REC 1063 (idx 1062): Expand bare 'rút' -> 'rút nhanh' [33, 34], POS
text_1063 = lines[1062].split('####')[0]
updates[1062] = (
    text_1063,
    [([1], [33, 34], 'POS')]
)

# 16. REC 1065 (idx 1064): Fix polarity flip ('ngập' NEG -> 'chống ngập' [23, 24], POS)
text_1065 = lines[1064].split('####')[0]
updates[1064] = (
    text_1065,
    [([13, 14], [23, 24], 'POS')]
)

# 17. REC 1070 (idx 1069): Clean duplicate prefix 'Tại TPHCM , Tại TP. Hồ Chí Minh ,' -> single 'Tại TPHCM ,'
raw_1070 = lines[1069].split('####')[0]
if raw_1070.startswith('Tại TPHCM , Tại TP. Hồ Chí Minh , '):
    text_1070 = raw_1070.replace('Tại TPHCM , Tại TP. Hồ Chí Minh , ', 'Tại TPHCM , ')
else:
    text_1070 = raw_1070
updates[1069] = (
    text_1070,
    [([1], [9, 10, 11], 'NEG')]
)

# 18. REC 1072 (idx 1071): Anti-overtagging (remove TP Thủ Đức, keep 4 streets with discrete opinions 'ngập sâu' [37, 38], 'chết máy' [43, 44])
text_1072 = lines[1071].split('####')[0]
updates[1071] = (
    text_1072,
    [
        ([17, 18, 19], [37, 38], 'NEG'),
        ([17, 18, 19], [43, 44], 'NEG'),
        ([21, 22, 23], [37, 38], 'NEG'),
        ([21, 22, 23], [43, 44], 'NEG'),
        ([25, 26, 27], [37, 38], 'NEG'),
        ([25, 26, 27], [43, 44], 'NEG'),
        ([29, 30, 31], [37, 38], 'NEG'),
        ([29, 30, 31], [43, 44], 'NEG')
    ]
)

# 19. REC 1074 (idx 1073): Fix truncated ungrammatical opinion 'ra ngập' -> 'xảy ra ngập' [23, 24, 25], NEG
text_1074 = lines[1073].split('####')[0]
updates[1073] = (
    text_1074,
    [([10, 11, 12, 13], [23, 24, 25], 'NEG')]
)

# 20. REC 1077 (idx 1076): Fix polarity flip ('ngập' NEG -> 'chống ngập' [16, 17], POS)
text_1077 = lines[1076].split('####')[0]
updates[1076] = (
    text_1077,
    [([1, 2, 3, 4], [16, 17], 'POS')]
)

# 21. REC 1078 (idx 1077): Expand 'ngập úng' -> 'ngập úng cục bộ' [35, 36, 37, 38], NEG
text_1078 = lines[1077].split('####')[0]
updates[1078] = (
    text_1078,
    [([1, 2, 3, 4], [35, 36, 37, 38], 'NEG')]
)

# Apply updates to lines
count = 0
for idx, (new_text, new_triplets) in updates.items():
    toks = new_text.split()
    # verify tokens
    for asp, opi, pol in new_triplets:
        asp_str = " ".join(toks[k] for k in asp)
        opi_str = " ".join(toks[k] for k in opi)
        # verify no index out of bounds
        assert all(0 <= k < len(toks) for k in asp), f"Asp index OOB in line {idx+1}: {asp}"
        assert all(0 <= k < len(toks) for k in opi), f"Opi index OOB in line {idx+1}: {opi}"
    lines[idx] = f"{new_text}####{new_triplets}"
    count += 1

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print(f"Successfully updated {count} records in Batch 36 (lines 1031-1080).")
