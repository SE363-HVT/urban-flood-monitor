import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# 1. REC 931 (idx 930): Tag both flood complaint 'Ngập quá nhiều' [16, 17, 18], NEG and coping measure 'kê lên hết' [12, 13, 14], POS
text_931 = lines[930].split('####')[0]
updates[930] = (
    text_931,
    [
        ([1], [12, 13, 14], 'POS'),
        ([1], [16, 17, 18], 'NEG')
    ]
)

# 2. REC 933 (idx 932): Expand bare word 'ngập' -> 'nước tràn vào nhà ngập hư hết tủ' [21..28], NEG
text_933 = lines[932].split('####')[0]
updates[932] = (
    text_933,
    [([1], list(range(21, 29)), 'NEG')]
)

# 3. REC 934 (idx 933): Expand 'ngập' -> 'nước ngập' [27, 28], NEG
text_934 = lines[933].split('####')[0]
updates[933] = (
    text_934,
    [([1], [27, 28], 'NEG')]
)

# 4. REC 935 (idx 934): Inverted polarity fix - water still inundated house because it could not recede -> NEG
text_935 = lines[934].split('####')[0]
updates[934] = (
    text_935,
    [([1], list(range(14, 26)), 'NEG')]
)

# 5. REC 938 (idx 937): Rhetorical public query 'khi nào thành phố mới hết ngập ?' -> NEU
text_938 = lines[937].split('####')[0]
updates[937] = (
    text_938,
    [([1, 2, 3, 4], [17, 18], 'NEU')]
)

# 6. REC 939 (idx 938): Anti-flood project funding 'chống ngập' [29, 30] -> POS
text_939 = lines[938].split('####')[0]
updates[938] = (
    text_939,
    [([1, 2, 3, 4], [29, 30], 'POS')]
)

# 7. REC 953 (idx 952): Expand opinion to include flood depth 'ngập gần 0 , 5m...' [11..37], NEG
text_953 = lines[952].split('####')[0]
updates[952] = (
    text_953,
    [([3, 4, 5], list(range(11, 38)), 'NEG')]
)

# 8. REC 961 (idx 960): 'chờ nước rút' [29, 30, 31] is waiting due to flood -> NEG (NOT POS)
text_961 = lines[960].split('####')[0]
updates[960] = (
    text_961,
    [
        ([2, 3, 4, 5], [7], 'NEG'),
        ([2, 3, 4, 5], [29, 30, 31], 'NEG')
    ]
)

# 9. REC 965 (idx 964): Clean double prefix and REJECT non-flood weather forecast
text_965 = "Tại TPHCM , Dự báo mưa giông còn kéo dài đến hết tuần sau ."
updates[964] = (
    text_965,
    []
)

# 10. REC 975 (idx 974): Anti-overtagging (remove TP. Thủ Đức, keep chợ Thủ Đức)
text_975 = lines[974].split('####')[0]
updates[974] = (
    text_975,
    [([16, 17, 18], [20, 21], 'NEG')]
)

# 11. REC 976 (idx 975): Landmark removal (remove chợ Thủ Đức, keep Lê Văn Ninh & Kha Vạn Cân)
text_976 = lines[975].split('####')[0]
updates[975] = (
    text_976,
    [
        ([13, 14, 15], list(range(21, 26)), 'NEG'),
        ([17, 18, 19], list(range(21, 26)), 'NEG')
    ]
)

# 12. REC 979 (idx 978): 'chờ nước rút' [15, 16, 17] is waiting due to flood -> NEG (NOT POS)
text_979 = lines[978].split('####')[0]
updates[978] = (
    text_979,
    [([1, 2, 3, 4], [15, 16, 17], 'NEG')]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 34 (931-980) successfully!")
