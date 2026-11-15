import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# 1. REC 785 (idx 784): Trim trailing timestamp metadata ', chiều 16 / 5' -> span [14..32]
text_785 = lines[784].split('####')[0]
updates[784] = (
    text_785,
    [([1, 2, 3, 4], list(range(14, 33)), 'NEG')]
)

# 2. REC 788 (idx 787): Boundary description without street name -> inject 'Tại TPHCM , ' fallback prefix
text_788_orig = lines[787].split('####')[0]
text_788 = f"Tại TPHCM , {text_788_orig}"
updates[787] = (
    text_788,
    [([1], [42, 43], 'NEG')]
)

# 3. REC 792 (idx 791): 'chờ nước rút' [18, 19, 20] is waiting due to flooded road -> NEG
text_792 = lines[791].split('####')[0]
updates[791] = (
    text_792,
    [([1], [18, 19, 20], 'NEG')]
)

# 4. REC 810 (idx 809): Expand truncated bare verb 'rút' to full predicate 'bắt đầu rút dần' [8, 9, 10, 11], POS
text_810 = lines[809].split('####')[0]
updates[809] = (
    text_810,
    [([1], [8, 9, 10, 11], 'POS')]
)

# 5. REC 813 (idx 812): 'hết ngập' [12, 13] is flood recovery -> POS
text_813 = lines[812].split('####')[0]
updates[812] = (
    text_813,
    [([1], [12, 13], 'POS')]
)

# 6. REC 823 (idx 822): Anti-overtagging (remove district Q. 7, keep only đường Huỳnh Tấn Phát)
text_823 = lines[822].split('####')[0]
updates[822] = (
    text_823,
    [([1, 2, 3, 4], list(range(9, 43)), 'NEG')]
)

# 7. REC 824 (idx 823): Anti-overtagging (remove district Q. 12, keep only đường Nguyễn Văn Quá)
text_824 = lines[823].split('####')[0]
updates[823] = (
    text_824,
    [([3, 4, 5, 6], list(range(13, 35)), 'NEG')]
)

# 8. REC 826 (idx 825): Anti-overtagging (remove Q. 9 & Q. Bình Thành, keep only 6 specific streets)
text_826 = lines[825].split('####')[0]
updates[825] = (
    text_826,
    [
        ([1, 2, 3, 4], [32, 33, 34], 'NEG'),
        ([6, 7, 8], [32, 33, 34], 'NEG'),
        ([10, 11, 12], [32, 33, 34], 'NEG'),
        ([14, 15, 16], [32, 33, 34], 'NEG'),
        ([21, 22, 23], [32, 33, 34], 'NEG'),
        ([25, 26, 27], [32, 33, 34], 'NEG')
    ]
)

# 9. REC 830 (idx 829): Add flooded homes triplet 'ngập úng' [15, 16], NEG
text_830 = lines[829].split('####')[0]
updates[829] = (
    text_830,
    [
        ([1, 2, 3, 4], [9, 10], 'NEG'),
        ([1, 2, 3, 4], [15, 16], 'NEG')
    ]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 31 (781-830) successfully!")
