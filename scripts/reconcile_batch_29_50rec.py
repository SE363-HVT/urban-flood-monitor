import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# 1. REC 689 (idx 688): Replace 'là ngập' [23, 24] with rich descriptive flood predicate 'ngập vào nhà luôn' [26, 27, 28, 29]
text_689 = lines[688].split('####')[0]
updates[688] = (
    text_689,
    [([14, 15, 16, 17], [26, 27, 28, 29], 'NEG')]
)

# 2. REC 697 (idx 696): Strip passive 'bị' -> 'chết máy' [12, 13]
text_697 = lines[696].split('####')[0]
updates[696] = (
    text_697,
    [([16, 17, 18, 19], [12, 13], 'NEG')]
)

# 3. REC 711 (idx 710): Fix fatal semantic error - [17, 18] was inside 'Trung tâm chống ngập nước TP'.
# Tag actual flood predicate on street: 'đã ngập thế này' [8, 9, 10, 11]
text_711 = lines[710].split('####')[0]
updates[710] = (
    text_711,
    [([32, 33, 34], [8, 9, 10, 11], 'NEG')]
)

# 4. REC 714 (idx 713): Expand to full predicate 'chống ngập hiệu quả' [5, 6, 7, 8], POS
text_714 = lines[713].split('####')[0]
updates[713] = (
    text_714,
    [([1], [5, 6, 7, 8], 'POS')]
)

# 5. REC 717 (idx 716): Tag all 3 measuring stations objectively (NEU)
text_717 = lines[716].split('####')[0]
updates[716] = (
    text_717,
    [
        ([29, 30, 31, 32], [34, 35, 36], 'NEU'),
        ([38, 39, 40, 41], [42, 43, 44], 'NEU'),
        ([46, 47, 48], [50], 'NEU')
    ]
)

# 6. REC 722 (idx 721): Strip passive 'bị' -> 'ngập' [31]
text_722 = lines[721].split('####')[0]
updates[721] = (
    text_722,
    [
        ([3, 4, 5, 6], [10, 11], 'NEG'),
        ([15, 16, 17, 18, 19, 20], [31], 'NEG')
    ]
)

# 7. REC 724 (idx 723): Weather/flood advisory 'Đề phòng ngập cục bộ' [3..7] must be NEU, not NEG
text_724 = lines[723].split('####')[0]
updates[723] = (
    text_724,
    [([1], [3, 4, 5, 6, 7], 'NEU')]
)

# 8. REC 725 (idx 724): Strip passive 'bị' -> 'ngập' [9]
text_725 = lines[724].split('####')[0]
updates[724] = (
    text_725,
    [([4, 5, 6], [9], 'NEG')]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 29 (681-730) successfully!")
