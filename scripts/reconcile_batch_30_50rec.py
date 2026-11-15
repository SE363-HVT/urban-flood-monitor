import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# 1. REC 741 (idx 740): Tag both flood event 'ngập tầng hầm' (NEG) and rescue 'bơm nước ra ngoài' (POS)
text_741 = lines[740].split('####')[0]
updates[740] = (
    text_741,
    [
        ([1], [4, 5, 6], 'NEG'),
        ([1], [18, 19, 20, 21], 'POS')
    ]
)

# 2. REC 743 (idx 742): Prediction/forecast 'dự đoán sẽ ngập lụt' [13..17] calibrated to NEU
text_743 = lines[742].split('####')[0]
updates[742] = (
    text_743,
    [([1, 2, 3, 4], [13, 14, 15, 16, 17], 'NEU')]
)

# 3. REC 750 (idx 749): Rich flood predicate 'ngập lênh láng' [11, 12, 13], NEG
text_750 = lines[749].split('####')[0]
updates[749] = (
    text_750,
    [([4, 5, 6, 7], [11, 12, 13], 'NEG')]
)

# 4. REC 755 (idx 754): 'chờ nước rút' [13, 14, 15] is traffic disruption (NEG), NOT active recovery (POS)
text_755 = lines[754].split('####')[0]
updates[754] = (
    text_755,
    [([1], [13, 14, 15], 'NEG')]
)

# 5. REC 760 (idx 759): Anti-overtagging (remove overarching wards phường Thủ Đức & phường Gò Vấp, keep only specific streets)
text_760 = lines[759].split('####')[0]
updates[759] = (
    text_760,
    [
        ([12, 13, 14], [42, 43, 44], 'NEG'),
        ([16, 17, 18], [42, 43, 44], 'NEG'),
        ([25, 26, 27], [42, 43, 44], 'NEG'),
        ([29, 30, 31], [42, 43, 44], 'NEG')
    ]
)

# 6. REC 768 (idx 767): Direct flood inundation predicate 'biến thành sông' [10, 11, 12], NEG
text_768 = lines[767].split('####')[0]
updates[767] = (
    text_768,
    [([1], [10, 11, 12], 'NEG')]
)

# 7. REC 770 (idx 769): Anti-overtagging (remove overarching TP Thủ Đức, keep only 4 specific streets)
text_770 = lines[769].split('####')[0]
updates[769] = (
    text_770,
    [
        ([11, 12], [31, 32, 33], 'NEG'),
        ([14, 15], [31, 32, 33], 'NEG'),
        ([17, 18, 19], [31, 32, 33], 'NEG'),
        ([21, 22, 23], [31, 32, 33], 'NEG')
    ]
)

# 8. REC 771 (idx 770): Anti-overtagging (remove phường Thảo Điền, keep only specific street Đường Quốc Hương)
text_771 = lines[770].split('####')[0]
updates[770] = (
    text_771,
    [([0, 1, 2], [8, 9, 10, 11, 12, 13], 'NEG')]
)

# 9. REC 777 (idx 776): 'chờ nước rút' [20, 21, 22] calibrated to NEG
text_777 = lines[776].split('####')[0]
updates[776] = (
    text_777,
    [
        ([1, 2, 3, 4], [12, 13], 'NEG'),
        ([1, 2, 3, 4], [20, 21, 22], 'NEG')
    ]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 30 (731-780) successfully!")
