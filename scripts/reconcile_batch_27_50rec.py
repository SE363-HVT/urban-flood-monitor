import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# REC 587 (idx 586):
# Strip 'bị' -> 'ngập nước' [11, 12]
text_587 = lines[586].split('####')[0]
updates[586] = (
    text_587,
    [([8, 9], [11, 12], 'NEG')]
)

# REC 588 (idx 587):
# Strip 'bị' -> 'ngập nặng' [39, 40]
text_588 = lines[587].split('####')[0]
updates[587] = (
    text_588,
    [
        ([25, 26, 27], [39, 40], 'NEG'),
        ([29, 30], [39, 40], 'NEG'),
        ([32, 33], [39, 40], 'NEG'),
        ([35, 36], [39, 40], 'NEG')
    ]
)

# REC 589 (idx 588):
# Strip 'bị' -> 'ngập sâu' [27, 28]
text_589 = lines[588].split('####')[0]
updates[588] = (
    text_589,
    [
        ([9, 10, 11], [27, 28], 'NEG'),
        ([13, 14, 15], [27, 28], 'NEG'),
        ([17, 18, 19], [27, 28], 'NEG'),
        ([21, 22, 23], [27, 28], 'NEG')
    ]
)

# REC 591 (idx 590):
# Strip 'bị' -> 'ngập sâu' [18, 19]
text_591 = lines[590].split('####')[0]
updates[590] = (
    text_591,
    [([1, 2, 3, 4], [18, 19], 'NEG')]
)

# REC 598 (idx 597):
# Strip 'bị' -> 'chết máy' [20, 21]
text_598 = lines[597].split('####')[0]
updates[597] = (
    text_598,
    [
        ([1, 2, 3, 4], list(range(8, 14)), 'NEG'),
        ([1, 2, 3, 4], [20, 21], 'NEG')
    ]
)

# REC 602 (idx 601):
# Anti-overtagging: remove phường Tăng Nhơn Phú & TP Thủ Đức
text_602 = lines[601].split('####')[0]
updates[601] = (
    text_602,
    [([12, 13, 14, 15], list(range(26, 33)), 'NEG')]
)

# REC 603 (idx 602):
# Strip 'bị' -> 'chết máy' [19, 20]
text_603 = lines[602].split('####')[0]
updates[602] = (
    text_603,
    [([1, 2, 3, 4], [19, 20], 'NEG')]
)

# REC 604 (idx 603):
# Strip 'bị' -> 'chết máy' [19, 20]
text_604 = lines[603].split('####')[0]
updates[603] = (
    text_604,
    [([13, 14, 15, 16], [19, 20], 'NEG')]
)

# REC 605 (idx 604):
# Remove redundant sub-span
text_605 = lines[604].split('####')[0]
updates[604] = (
    text_605,
    [([2, 3, 4, 5], list(range(6, 13)), 'NEG')]
)

# REC 608 (idx 607):
# Strip 'bị' -> 'chết máy bồng bềnh' [9..12]
text_608 = lines[607].split('####')[0]
updates[607] = (
    text_608,
    [([1, 2, 3, 4], list(range(9, 13)), 'NEG')]
)

# REC 612 (idx 611):
# Anti-overtagging: remove phường Thảo Điền. Strip 'bị' -> 'ngập nặng' [13, 14]
text_612 = lines[611].split('####')[0]
updates[611] = (
    text_612,
    [([1, 2, 3], [13, 14], 'NEG')]
)

# REC 613 (idx 612):
# Strip 'bị' -> 'chết máy' [17, 18]
text_613 = lines[612].split('####')[0]
updates[612] = (
    text_613,
    [([9, 10, 11, 12, 13, 14], [17, 18], 'NEG')]
)

# REC 618 (idx 617):
# Strip 'bị' and remove sub-span
text_618 = lines[617].split('####')[0]
updates[617] = (
    text_618,
    [([1, 2, 3, 4], list(range(22, 39)), 'NEG')]
)

# REC 623 (idx 622):
# Strip 'bị' -> 'té ngã' [16, 17]
text_623 = lines[622].split('####')[0]
updates[622] = (
    text_623,
    [([1, 2, 3, 4], [16, 17], 'NEG')]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 27 (581-630) successfully!")
