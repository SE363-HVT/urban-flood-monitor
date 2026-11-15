import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# 1. REC 632 (idx 631): Strip passive 'bị' -> 'ngập rất nặng' [23, 24, 25]
text_632 = lines[631].split('####')[0]
updates[631] = (
    text_632,
    [([3, 4, 5, 6], [23, 24, 25], 'NEG')]
)

# 2. REC 633 (idx 632): Sub-span deduplication -> keep single richest span [6..25], remove duplicate [21..23]
text_633 = lines[632].split('####')[0]
updates[632] = (
    text_633,
    [([1, 2, 3, 4], list(range(6, 26)), 'NEG')]
)

# 3. REC 652 (idx 651): Anti-overtagging (remove boundary landmarks đường 65 & đường Tống Hữu Định). Strip 'bị' -> 'ngập nặng' [16, 17]
text_652 = lines[651].split('####')[0]
updates[651] = (
    text_652,
    [([3, 4, 5], [16, 17], 'NEG')]
)

# 4. REC 653 (idx 652): Strip 'bị' -> 'ngập nặng' [17, 18]
text_653 = lines[652].split('####')[0]
updates[652] = (
    text_653,
    [([1, 2, 3, 4], [17, 18], 'NEG')]
)

# 5. REC 654 (idx 653): Replace weather cause 'mưa lớn' with flood predicate 'ngập' [10]
text_654 = lines[653].split('####')[0]
updates[653] = (
    text_654,
    [([1, 2, 3, 4], [10], 'NEG')]
)

# 6. REC 657 (idx 656): Strip 'bị' -> 'ngập nặng' [10, 11]
text_657 = lines[656].split('####')[0]
updates[656] = (
    text_657,
    [
        ([13, 14, 15], [10, 11], 'NEG'),
        ([17, 18, 19, 20], [10, 11], 'NEG'),
        ([22, 23], [10, 11], 'NEG'),
        ([25, 26, 27], [10, 11], 'NEG'),
        ([29, 30, 31], [10, 11], 'NEG'),
        ([33, 34, 35], [10, 11], 'NEG')
    ]
)

# 7. REC 660 (idx 659): Strip preposition 'do' -> 'ngập nước' [10, 11]
text_660 = lines[659].split('####')[0]
updates[659] = (
    text_660,
    [([1, 2, 3, 4], [10, 11], 'NEG')]
)

# 8. REC 661 (idx 660): Clean vehicle opinion -> 'chết máy' [8, 9]
text_661 = lines[660].split('####')[0]
updates[660] = (
    text_661,
    [([11, 12, 13, 14], [8, 9], 'NEG')]
)

# 9. REC 662 (idx 661): Full descriptive flood span -> [3..15] ('Nước dâng cao lút nửa bánh xe máy , kéo dài như sông'), polarity calibrated to NEG
text_662 = lines[661].split('####')[0]
updates[661] = (
    text_662,
    [([1], list(range(3, 16)), 'NEG')]
)

# 10. REC 666 (idx 665): Anti-overtagging (remove landmark bridges cầu Thủ Thiêm & cầu Sài Gòn). Rich flood opinion [26..40]
text_666 = lines[665].split('####')[0]
updates[665] = (
    text_666,
    [([8, 9, 10, 11], list(range(26, 41)), 'NEG')]
)

# 11. REC 679 (idx 678): Strip generic noun 'tuyến' -> Aspect is 'QL1' [9]
text_679 = lines[678].split('####')[0]
updates[678] = (
    text_679,
    [([9], list(range(20, 24)), 'NEG')]
)

# 12. REC 680 (idx 679): Complete flood clause -> 'nước ngập vẫn chưa rút' [8, 9, 10, 11, 12]
text_680 = lines[679].split('####')[0]
updates[679] = (
    text_680,
    [([1], [8, 9, 10, 11, 12], 'NEG')]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 28 (631-680) successfully!")
