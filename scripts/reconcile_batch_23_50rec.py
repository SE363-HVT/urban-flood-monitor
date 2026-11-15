import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# REC 385 (idx 384):
# Strip 'bị' -> 'ngập nặng' [39, 40]
text_385 = lines[384].split('####')[0]
updates[384] = (
    text_385,
    [
        ([44, 45], [39, 40], 'NEG'),
        ([47, 48], [39, 40], 'NEG'),
        ([50, 51], [39, 40], 'NEG'),
        ([53, 54], [39, 40], 'NEG'),
        ([56, 57], [39, 40], 'NEG')
    ]
)

# REC 389 (idx 388):
# Remove redundant sub-span overlap
text_389 = lines[388].split('####')[0]
updates[388] = (
    text_389,
    [([1, 2, 3, 4], list(range(8, 21)), 'NEG')]
)

# REC 395 (idx 394):
# Remove redundant sub-span overlap
text_395 = lines[394].split('####')[0]
updates[394] = (
    text_395,
    [([1, 2, 3, 4], list(range(17, 26)), 'NEG')]
)

# REC 399 (idx 398):
# Strip bare noun 'tình trạng' -> 'ngập do triều cường' [6, 7, 8, 9]
text_399 = lines[398].split('####')[0]
updates[398] = (
    text_399,
    [([11, 12, 13, 14], [6, 7, 8, 9], 'NEG')]
)

# REC 409 (idx 408):
# Strip causative 'gây' -> 'ngập' [18]
text_409 = lines[408].split('####')[0]
updates[408] = (
    text_409,
    [
        ([19, 20, 21, 22], [18], 'NEG'),
        ([31, 32, 33, 34], [18], 'NEG'),
        ([31, 32, 33, 34], list(range(41, 50)), 'NEG')
    ]
)

# REC 423 (idx 422):
# Strip 'bị' -> 'chết máy' [16, 17]
text_423 = lines[422].split('####')[0]
updates[422] = (
    text_423,
    [([1, 2, 3, 4], [16, 17], 'NEG')]
)

# REC 427 (idx 426):
# Preventative directive -> NEU
text_427 = lines[426].split('####')[0]
updates[426] = (
    text_427,
    [([1, 2, 3, 4], [34, 35], 'NEU')]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 23 (381-430) successfully!")
