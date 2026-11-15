import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# REC 250 (idx 249):
# Change noun phrase opinion 'dòng nước ngập' [16, 17, 18] to core predicate 'ngập' [18]
text_250 = lines[249].split('####')[0]
updates[249] = (
    text_250,
    [([7, 8, 9, 10], [18], 'NEG')]
)

# REC 253 (idx 252):
# Aspect 'đường TPHCM' -> 'TPHCM' [24]
text_253 = lines[252].split('####')[0]
updates[252] = (
    text_253,
    [([24], [9, 10, 11, 12, 13, 14], 'NEG')]
)

# REC 255 (idx 254):
# Shorten 'cảnh ngập như cơm bữa' -> 'ngập như cơm bữa' [18, 19, 20, 21]
text_255 = lines[254].split('####')[0]
updates[254] = (
    text_255,
    [([5, 6, 7, 8], [18, 19, 20, 21], 'NEG')]
)

# REC 257 (idx 256):
# Clean vehicle breakdown opinion: 'chết máy' [5, 6] instead of 'Một chiếc xe ô tô chết máy'
text_257 = lines[256].split('####')[0]
updates[256] = (
    text_257,
    [
        ([14, 15, 16, 17], [5, 6], 'NEG'),
        ([14, 15, 16, 17], [11, 12], 'NEG')
    ]
)

# REC 260 (idx 259):
# Include prefix 'phường' -> 'phường Tân Hưng' [1, 2, 3]
text_260 = lines[259].split('####')[0]
updates[259] = (
    text_260,
    [([1, 2, 3], [12, 13], 'NEG')]
)

# REC 269 (idx 268):
# Include 'trường' -> 'trường THPT Ngô Quyền' [19, 20, 21, 22]
text_269 = lines[268].split('####')[0]
updates[268] = (
    text_269,
    [([19, 20, 21, 22], [24, 25, 26, 27], 'NEG')]
)

# REC 273 (idx 272):
# Advisory / warning -> Polarity NEU
text_273 = lines[272].split('####')[0]
updates[272] = (
    text_273,
    [([3, 4, 5, 6], [21, 22], 'NEU')]
)

# REC 280 (idx 279):
# Strip 'bị' -> 'ngập úng' [31, 32]
text_280 = lines[279].split('####')[0]
updates[279] = (
    text_280,
    [
        ([2], [31, 32], 'NEG'),
        ([2], [20, 21, 22, 23], 'POS')
    ]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 20 (231-280) successfully!")
