import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# 1. REC 982 (idx 981): Expand bare verb 'rút' -> 'nước đã rút hết' [8, 9, 10, 11], POS
text_982 = lines[981].split('####')[0]
updates[981] = (
    text_982,
    [([1], [8, 9, 10, 11], 'POS')]
)

# 2. REC 983 (idx 982): Landmark removal (remove chợ Thủ Đức, keep 3 branch streets)
text_983 = lines[982].split('####')[0]
updates[982] = (
    text_983,
    [
        ([15, 16, 17], list(range(31, 36)), 'NEG'),
        ([19, 20, 21], list(range(31, 36)), 'NEG'),
        ([23, 24, 25], list(range(31, 36)), 'NEG')
    ]
)

# 3. REC 984 (idx 983): Expand bare verb 'rút' -> 'nước đã rút hết' [13, 14, 15, 16], POS
text_984 = lines[983].split('####')[0]
updates[983] = (
    text_984,
    [([1], [13, 14, 15, 16], 'POS')]
)

# 4. REC 998 (idx 997): Anti-overtagging (remove phường Hiệp Bình Chánh, keep đường 38)
text_998 = lines[997].split('####')[0]
updates[997] = (
    text_998,
    [([12, 13], [5, 6], 'NEG')]
)

# 5. REC 1004 (idx 1003): Anti-overtagging (remove P. Linh Xuân & TP. Thủ Đức, keep chợ Linh Xuân & đường số 8)
text_1004 = lines[1003].split('####')[0]
updates[1003] = (
    text_1004,
    [
        ([16, 17, 18], list(range(34, 40)), 'NEG'),
        ([20, 21, 22], list(range(34, 40)), 'NEG')
    ]
)

# 6. REC 1010 (idx 1009): Fix aspect prefix - include token 32 'giao' -> 'giao lộ Kha Vạn Cân - Phạm Văn Đồng' [32..40]
text_1010 = lines[1009].split('####')[0]
updates[1009] = (
    text_1010,
    [
        ([5, 6, 7, 8], [15, 16, 17, 18], 'NEG'),
        (list(range(32, 41)), [57, 58], 'NEG')
    ]
)

# 7. REC 1013 (idx 1012): Anti-overtagging (remove thành phố Thủ Đức, keep đường Tô Ngọc Vân & Gò Dưa)
text_1013 = lines[1012].split('####')[0]
updates[1012] = (
    text_1013,
    [
        ([7, 8, 9, 10], list(range(23, 48)), 'NEG'),
        ([12, 13], list(range(23, 48)), 'NEG')
    ]
)

# 8. REC 1021 (idx 1020): Strip passive 'bị' -> 'gián đoạn' [15, 16], NEG
text_1021 = lines[1020].split('####')[0]
updates[1020] = (
    text_1021,
    [([11, 12, 13], [15, 16], 'NEG')]
)

# 9. REC 1030 (idx 1029): Include 'TP.' in aspect -> 'TP. Thủ Đức' [13, 14, 15], NEG
text_1030 = lines[1029].split('####')[0]
updates[1029] = (
    text_1030,
    [([13, 14, 15], [3, 4], 'NEG')]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 35 (981-1030) successfully!")
