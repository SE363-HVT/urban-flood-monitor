import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# REC 436 (idx 435):
# Anti-overtagging: cầu Phước Long & đường Huỳnh Tấn Phát are boundary markers
text_436 = lines[435].split('####')[0]
updates[435] = (
    text_436,
    [([1, 2, 3, 4], [37, 38, 39, 40], 'NEG')]
)

# REC 444 (idx 443):
# Remove redundant sub-span
text_444 = lines[443].split('####')[0]
updates[443] = (
    text_444,
    [([5, 6, 7, 8], list(range(12, 45)), 'NEG')]
)

# REC 457 (idx 456):
# Strip 'bị' -> 'ngập' [21]
text_457 = lines[456].split('####')[0]
updates[456] = (
    text_457,
    [
        ([4, 5, 6, 7], list(range(8, 13)), 'NEU'),
        ([18, 19], [21], 'NEG')
    ]
)

# REC 458 (idx 457):
# Remove redundant sub-span
text_458 = lines[457].split('####')[0]
updates[457] = (
    text_458,
    [([1, 2, 3, 4], list(range(9, 19)), 'NEG')]
)

# REC 462 (idx 461):
# Strip bare noun 'tình trạng' -> 'ngập' [26]
text_462 = lines[461].split('####')[0]
updates[461] = (
    text_462,
    [
        ([5, 6, 7], [26], 'NEG'),
        ([9, 10], [26], 'NEG')
    ]
)

# REC 466 (idx 465):
# Anti-overtagging: Remove P. Tân Thuận Tây & Q. 7. Strip 'bị' -> 'ngập sâu' [17, 18]
text_466 = lines[465].split('####')[0]
updates[465] = (
    text_466,
    [([1, 2, 3, 4], [17, 18], 'NEG')]
)

# REC 473 (idx 472):
# Strip 'bị' -> 'chết máy' [17, 18]
text_473 = lines[472].split('####')[0]
updates[472] = (
    text_473,
    [([1, 2, 3, 4], [17, 18], 'NEG')]
)

# REC 477 (idx 476):
# Strip generic prefix 'tuyến' -> 'đường Trần Xuân Soạn' [15, 16, 17, 18]
text_477 = lines[476].split('####')[0]
updates[476] = (
    text_477,
    [
        ([5, 6], [7, 8, 9, 10], 'NEG'),
        ([15, 16, 17, 18], [22, 23, 24], 'NEG')
    ]
)

# REC 480 (idx 479):
# Fix broken aspect 'do triều cường ở' -> 'triều cường ở TPHCM' [5, 6, 7, 8]
text_480 = lines[479].split('####')[0]
updates[479] = (
    text_480,
    [([5, 6, 7, 8], [2, 3], 'NEG')]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 24 (431-480) successfully!")
