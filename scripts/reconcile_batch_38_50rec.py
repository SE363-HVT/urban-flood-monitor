import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# 1. REC 1143 (idx 1142): Separate comma-joined opinion into discrete spans
text_1143 = lines[1142].split('####')[0]
updates[1142] = (
    text_1143,
    [
        ([0, 1, 2], [15, 16, 17], 'NEG'),
        ([0, 1, 2], [19, 20, 21, 22], 'NEG')
    ]
)

# 2. REC 1144 (idx 1143): Fix catastrophic polarity flip: bare 'rút' POS -> 'ngập sâu' [14, 15], NEG
text_1144 = lines[1143].split('####')[0]
updates[1143] = (
    text_1144,
    [([1], [14, 15], 'NEG')]
)

# 3. REC 1148 (idx 1147): Expand bare 'ngập' -> 'nguy cơ ngập cao' [22, 23, 24, 25], NEG
text_1148 = lines[1147].split('####')[0]
updates[1147] = (
    text_1148,
    [([1], [22, 23, 24, 25], 'NEG')]
)

# 4. REC 1157 (idx 1156): Expand bare 'ngập' -> 'ngập kéo dài' [11, 12, 13], NEG
text_1157 = lines[1156].split('####')[0]
updates[1156] = (
    text_1157,
    [([1, 2, 3, 4], [11, 12, 13], 'NEG')]
)

# 5. REC 1160 (idx 1159): Fix DOC_FALLBACK_MISUSE & polarity inversion: bare 'ngập' NEG -> 'giải quyết giảm ngập' [8, 9, 10, 11], POS on 'chợ Thủ Đức' [16, 17, 18]
text_1160 = lines[1159].split('####')[0]
updates[1159] = (
    text_1160,
    [([16, 17, 18], [8, 9, 10, 11], 'POS')]
)

# 6. REC 1161 (idx 1160): Fix polarity inversion: bare 'ngập' NEG -> 'kiểm soát ngập' [16, 17, 18], POS on 'TPHCM' [1]
text_1161 = lines[1160].split('####')[0]
updates[1160] = (
    text_1161,
    [([1], [16, 17, 18], 'POS')]
)

# 7. REC 1162 (idx 1161): Expand bare 'ngập' -> 'ngập cục bộ' [32, 33, 34], NEG
text_1162 = lines[1161].split('####')[0]
updates[1161] = (
    text_1162,
    [([1], [32, 33, 34], 'NEG')]
)

# 8. REC 1163 (idx 1162): Strip passive 'bị' and comma -> clean 'ngập sâu' [22, 23], NEG
text_1163 = lines[1162].split('####')[0]
updates[1162] = (
    text_1163,
    [([8], [22, 23], 'NEG')]
)

# 9. REC 1165 (idx 1164): Expand bare 'ngập úng' -> 'ngập úng cục bộ' [32, 33, 34, 35], NEG
text_1165 = lines[1164].split('####')[0]
updates[1164] = (
    text_1165,
    [([1, 2, 3, 4], [32, 33, 34, 35], 'NEG')]
)

# 10. REC 1166 (idx 1165): Shorten long comma-joined string [35..45] -> clean 'ngập sâu' [35, 36], NEG for all 3 entities
text_1166 = lines[1165].split('####')[0]
updates[1165] = (
    text_1166,
    [
        ([26, 27], [35, 36], 'NEG'),
        ([29, 30], [35, 36], 'NEG'),
        ([32, 33, 34], [35, 36], 'NEG')
    ]
)

# 11. REC 1172 (idx 1171): Add 'ngập sâu' [26, 27], NEG along with 'chết máy' [19, 20], NEG
text_1172 = lines[1171].split('####')[0]
updates[1171] = (
    text_1172,
    [
        ([1, 2, 3, 4], [19, 20], 'NEG'),
        ([1, 2, 3, 4], [26, 27], 'NEG')
    ]
)

# 12. REC 1174 (idx 1173): Add 'nằm bất động' [8, 9, 10], NEG along with 'ngập' [13], NEG
text_1174 = lines[1173].split('####')[0]
updates[1173] = (
    text_1174,
    [
        ([1], [8, 9, 10], 'NEG'),
        ([1], [13], 'NEG')
    ]
)

# 13. REC 1175 (idx 1174): Add 'đợi nước rút' [23, 24, 25], NEG along with 'chết máy' [17, 18], NEG
text_1175 = lines[1174].split('####')[0]
updates[1174] = (
    text_1175,
    [
        ([1, 2, 3, 4], [17, 18], 'NEG'),
        ([1, 2, 3, 4], [23, 24, 25], 'NEG')
    ]
)

# 14. REC 1178 (idx 1177): Expand bare 'ngập' -> 'ngập thường xuyên' [10, 11, 12], NEG
text_1178 = lines[1177].split('####')[0]
updates[1177] = (
    text_1178,
    [([1, 2, 3, 4], [10, 11, 12], 'NEG')]
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

print(f"Successfully updated {count} records in Batch 38 (lines 1131-1180).")
