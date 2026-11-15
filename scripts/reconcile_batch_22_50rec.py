import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# REC 348 (idx 347):
# Strip 'bị' -> 'ngập' [28]
text_348 = lines[347].split('####')[0]
updates[347] = (
    text_348,
    [
        ([26], [28], 'NEG'),
        ([5, 6, 7, 8], [9, 10], 'NEG')
    ]
)

# REC 353 (idx 352):
# Add POS flood prevention action: 'ngăn nước tràn vào' [28, 29, 30, 31]
text_353 = lines[352].split('####')[0]
updates[352] = (
    text_353,
    [([1], [28, 29, 30, 31], 'POS')]
)

# REC 354 (idx 353):
# Add POS embankment reinforcement: 'gia cố bờ bao' [14, 15, 16, 17] alongside 'ngập tới đầu gối' [26..29]
text_354 = lines[353].split('####')[0]
updates[353] = (
    text_354,
    [
        ([1, 2, 3, 4], [26, 27, 28, 29], 'NEG'),
        ([1, 2, 3, 4], [14, 15, 16, 17], 'POS')
    ]
)

# REC 360 (idx 359):
# Opinion 'nước ngập' [15, 16] instead of single word 'ngập'
text_360 = lines[359].split('####')[0]
updates[359] = (
    text_360,
    [([1], [15, 16], 'NEG')]
)

# REC 370 (idx 369):
# Flood early warning technology application -> POS
text_370 = lines[369].split('####')[0]
updates[369] = (
    text_370,
    [([1], [9, 10, 11, 12], 'POS')]
)

# REC 380 (idx 379):
# Risk warning -> 'Nguy cơ ngập kéo dài' [3, 4, 5, 6, 7] -> NEU
text_380 = lines[379].split('####')[0]
updates[379] = (
    text_380,
    [([1], [3, 4, 5, 6, 7], 'NEU')]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 22 (331-380) successfully!")
