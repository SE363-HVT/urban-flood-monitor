import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# 1. REC 882 (idx 881): Anti-overtagging (remove Q. Tân Phú & Q. Bình Tân)
text_882 = lines[881].split('####')[0]
updates[881] = (
    text_882,
    [
        ([19, 20], [7], 'NEG'),
        ([22, 23, 24], [7], 'NEG'),
        ([31, 32, 33], [7], 'NEG')
    ]
)

# 2. REC 885 (idx 884): Inverted polarity fix - pump success 'không sợ nước ngập' [60..63] is POS
text_885 = lines[884].split('####')[0]
updates[884] = (
    text_885,
    [([1], [60, 61, 62, 63], 'POS')]
)

# 3. REC 899 (idx 898): Strip passive 'bị' -> 'ngập , người dân đi lại khó khăn' [27..34], NEG
text_899 = lines[898].split('####')[0]
updates[898] = (
    text_899,
    [([11, 12], list(range(27, 35)), 'NEG')]
)

# 4. REC 902 (idx 901): Correct aspect to 'đường Cây Trâm' [1, 2, 3] and opinion to 'chống ngập' [31, 32], POS
text_902 = lines[901].split('####')[0]
updates[901] = (
    text_902,
    [([1, 2, 3], [31, 32], 'POS')]
)

# 5. REC 907 (idx 906): 'chờ nước rút' [25, 26, 27] is waiting due to flood -> NEG (NOT POS)
text_907 = lines[906].split('####')[0]
updates[906] = (
    text_907,
    [([1], [25, 26, 27], 'NEG')]
)

# 6. REC 911 (idx 910): Fix critical token shift: 'Thạnh ) ngập' -> 'ngập nặng nhất' [9, 10, 11], NEG
text_911 = lines[910].split('####')[0]
updates[910] = (
    text_911,
    [([0, 1, 2, 3], [9, 10, 11], 'NEG')]
)

# 7. REC 916 (idx 915): Anti-overtagging (remove Q. Bình Tân, keep only Đường Kinh Dương Vương)
text_916 = lines[915].split('####')[0]
updates[915] = (
    text_916,
    [([0, 1, 2, 3], [9, 10, 11], 'NEG')]
)

# 8. REC 918 (idx 917): Anti-overtagging (remove Q. Bình Tân, keep only đường Kinh Dương Vương)
text_918 = lines[917].split('####')[0]
updates[917] = (
    text_918,
    [([10, 11, 12, 13], list(range(1, 10)), 'NEG')]
)

# 9. REC 919 (idx 918): Anti-overtagging (remove Q. Bình Tân, keep only đường Kinh Dương Vương)
text_919 = lines[918].split('####')[0]
updates[918] = (
    text_919,
    [([21, 22, 23, 24], [7], 'NEG')]
)

# 10. REC 920 (idx 919): Landmark removal (remove bến xe miền Đông, keep only 4 flooded streets)
text_920 = lines[919].split('####')[0]
updates[919] = (
    text_920,
    [
        ([37, 38, 39], [19, 20, 21], 'NEG'),
        ([41, 42, 43, 44], [19, 20, 21], 'NEG'),
        ([46, 47, 48], [19, 20, 21], 'NEG'),
        ([50, 51, 52], [19, 20, 21], 'NEG')
    ]
)

# 11. REC 924 (idx 923): Landmark removal (remove cầu Rạch Chiếc, keep xa lộ Hà Nội)
text_924 = lines[923].split('####')[0]
updates[923] = (
    text_924,
    [
        ([5, 6, 7], [76, 77], 'NEG'),
        ([9, 10, 11], [76, 77], 'NEG'),
        ([13, 14], [76, 77], 'NEG'),
        ([21, 22, 23], [76, 77], 'NEG'),
        ([29, 30, 31, 32], [76, 77], 'NEG'),
        ([39, 40], [76, 77], 'NEG'),
        ([42, 43, 44, 45], [76, 77], 'NEG'),
        ([47, 48, 49], [76, 77], 'NEG'),
        ([51, 52, 53], [76, 77], 'NEG'),
        ([60, 61, 62, 63], [76, 77], 'NEG')
    ]
)

# 12. REC 928 (idx 927): Anti-overtagging (remove P. Phú Mỹ & Q. 7, keep only đường Huỳnh Tấn Phát)
text_928 = lines[927].split('####')[0]
updates[927] = (
    text_928,
    [([3, 4, 5, 6], [19, 20, 21, 22], 'NEG')]
)

# 13. REC 930 (idx 929): 'ngập nguyên một đêm không có rút được' [9..16] is NEG (not POS)
text_930 = lines[929].split('####')[0]
updates[929] = (
    text_930,
    [([1], list(range(9, 17)), 'NEG')]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 33 (881-930) successfully!")
