import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# REC 531 (idx 530):
# Advisory weather warning -> NEU
text_531 = lines[530].split('####')[0]
updates[530] = (
    text_531,
    [([1], [31, 32], 'NEU')]
)

# REC 532 (idx 531):
# Anti-overtagging: remove phường Bến Thành. Strip 'bị' -> 'ngập' [22]
text_532 = lines[531].split('####')[0]
updates[531] = (
    text_532,
    [
        ([10, 11], [22], 'NEG'),
        ([13, 14, 15], [22], 'NEG')
    ]
)

# REC 534 (idx 533):
# Anti-overtagging: remove phường Chợ Quán
text_534 = lines[533].split('####')[0]
updates[533] = (
    text_534,
    [
        ([2, 3, 4], [14, 15, 16], 'NEG'),
        ([6, 7], [14, 15, 16], 'NEG')
    ]
)

# REC 537 (idx 536):
# Anti-overtagging: remove phường Hòa Bình & phường Vườn Lài
text_537 = lines[536].split('####')[0]
updates[536] = (
    text_537,
    [
        ([4, 5, 6, 7], [39, 40], 'NEG'),
        ([9, 10, 11], [39, 40], 'NEG'),
        ([13, 14], [39, 40], 'NEG'),
        ([21, 22, 23], [39, 40], 'NEG')
    ]
)

# REC 538 (idx 537):
# Add fallback 'Tại TPHCM , ' to replace bare noun 'đường'
text_538 = f"Tại TPHCM , {lines[537].split('####')[0]}"
# 0:Tại 1:TPHCM 2:, 3:Nước 4:trên 5:đường 6:rút 7:dần 8:, 9:giao 10:thông 11:trở 12:lại 13:bình 14:thường 15:.
updates[537] = (
    text_538,
    [
        ([1], [6, 7], 'POS'),
        ([1], list(range(9, 15)), 'POS')
    ]
)

# REC 543 (idx 542):
# Rich single opinion
text_543 = lines[542].split('####')[0]
updates[542] = (
    text_543,
    [([1, 2, 3, 4], list(range(19, 30)), 'NEG')]
)

# REC 544 (idx 543):
# Strip 'bị' -> 'chết máy giữa đường' [11..14]
text_544 = lines[543].split('####')[0]
updates[543] = (
    text_544,
    [([1, 2, 3, 4], list(range(11, 15)), 'NEG')]
)

# REC 554 (idx 553):
# Advisory warning -> NEU
text_554 = lines[553].split('####')[0]
updates[553] = (
    text_554,
    [([3, 4, 5, 6], [21, 22], 'NEU')]
)

# REC 556 (idx 555):
# Remove redundant sub-span
text_556 = lines[555].split('####')[0]
updates[555] = (
    text_556,
    [([1, 2, 3, 4], list(range(10, 28)), 'NEG')]
)

# REC 563 (idx 562):
# Remove redundant sub-span
text_563 = lines[562].split('####')[0]
updates[562] = (
    text_563,
    [([1, 2, 3, 4], list(range(9, 25)), 'NEG')]
)

# REC 571 (idx 570):
# Strip 'bị' -> 'chia cắt cục bộ' [25..28]
text_571 = lines[570].split('####')[0]
updates[570] = (
    text_571,
    [
        ([12, 13, 14], list(range(25, 29)), 'NEG'),
        ([16, 17, 18], list(range(25, 29)), 'NEG'),
        ([20, 21, 22], list(range(25, 29)), 'NEG')
    ]
)

# REC 572 (idx 571):
# Mobilize traffic police to assist -> POS
text_572 = lines[571].split('####')[0]
updates[571] = (
    text_572,
    [([13, 14], list(range(27, 51)), 'POS')]
)

# REC 573 (idx 572):
# Add CSGT assistance -> POS
text_573 = lines[572].split('####')[0]
updates[572] = (
    text_573,
    [
        ([16, 17, 18], [11, 12], 'NEG'),
        ([20, 21], [11, 12], 'NEG'),
        ([16, 17, 18], list(range(31, 43)), 'POS')
    ]
)

# REC 575 (idx 574):
# Assist citizens escape flooding -> POS
text_575 = lines[574].split('####')[0]
updates[574] = (
    text_575,
    [([27, 28, 29], list(range(31, 40)), 'POS')]
)

# REC 577 (idx 576):
# CSGT assistance praised -> POS
text_577 = lines[576].split('####')[0]
updates[576] = (
    text_577,
    [([1], list(range(8, 17)), 'POS')]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 26 (531-580) successfully!")
