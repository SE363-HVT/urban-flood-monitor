import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# 1. REC 832 (idx 831): Expand truncated 'ngập' [21] to full depth measurement 'ngập hơn 1m' [21, 22, 23], NEG
text_832 = lines[831].split('####')[0]
updates[831] = (
    text_832,
    [([1], [21, 22, 23], 'NEG')]
)

# 2. REC 841 (idx 840): Anti-overtagging (remove district Q. 1, keep only Lê Thánh Tôn)
text_841 = lines[840].split('####')[0]
updates[840] = (
    text_841,
    [([21, 22, 23], [29, 30, 31, 32, 33], 'NEG')]
)

# 3. REC 848 (idx 847): Anti-overtagging (remove Q. Tân Bình & Q. Gò Vấp). Strip generic noun 'tuyến' -> đường Phan Huy Ích [67..70]
text_848 = lines[847].split('####')[0]
updates[847] = (
    text_848,
    [
        ([14, 15, 16, 17], [27, 28, 29], 'NEG'),
        ([67, 68, 69, 70], [95, 96, 97], 'NEG')
    ]
)

# 4. REC 851 (idx 850): Anti-overtagging (remove P. 15 & Q. Tân Bình, keep only đường Phan Huy Ích)
text_851 = lines[850].split('####')[0]
updates[850] = (
    text_851,
    [([20, 21, 22, 23], [36, 37], 'NEG')]
)

# 5. REC 859 (idx 858): 'chờ nước rút' [24, 25, 26] is traffic hardship -> NEG (NOT POS)
text_859 = lines[858].split('####')[0]
updates[858] = (
    text_859,
    [([1, 2, 3, 4], [24, 25, 26], 'NEG')]
)

# 6. REC 872 (idx 871): Anti-overtagging (remove P. 15 & Q. Tân Bình, keep only đường Phan Huy Ích)
text_872 = lines[871].split('####')[0]
updates[871] = (
    text_872,
    [([12, 13, 14, 15], list(range(27, 44)), 'NEG')]
)

# 7. REC 873 (idx 872): Anti-overtagging (remove P. 9 & Q. Gò Vấp, keep only đường Phạm Văn Chiêu)
text_873 = lines[872].split('####')[0]
updates[872] = (
    text_873,
    [([1, 2, 3, 4], [14, 15, 16, 17], 'NEG')]
)

# 8. REC 874 (idx 873): Anti-overtagging (remove P. 9 & Q. Gò Vấp, keep only đường Lê Văn Thọ)
text_874 = lines[873].split('####')[0]
updates[873] = (
    text_874,
    [([10, 11, 12, 13], [5], 'NEG')]
)

# 9. REC 879 (idx 878): Anti-overtagging (remove CV Làng Hoa, P. 8, Q. Gò Vấp, keep only đường Cây Trâm)
text_879 = lines[878].split('####')[0]
updates[878] = (
    text_879,
    [([9, 10, 11], [28, 29, 30, 31], 'NEG')]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 32 (831-880) successfully!")
