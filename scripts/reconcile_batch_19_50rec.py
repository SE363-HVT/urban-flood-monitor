import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# REC 182 (idx 181):
# Tình trạng ngập cũng xảy ra tại đường Trần Xuân Soạn , Huỳnh Tấn Phát ( phường Tân Thuận ) , khu bán đảo Thanh Đa ( phường Bình Quới ) , đường Võ Nguyên Giáp ( phường Thủ Đức ) và quốc lộ 50 ( xã Bình Hưng ) …
# Change bare noun opinion 'Tình trạng ngập' [0, 1, 2] to core predicate 'ngập' [2]
# And ensure 'bán đảo Thanh Đa' is [22, 23, 24, 25]
updates[181] = (
    lines[181].split('####')[0],
    [
        ([7, 8, 9, 10], [2], 'NEG'),
        ([12, 13, 14], [2], 'NEG'),
        ([22, 23, 24, 25], [2], 'NEG'),
        ([32, 33, 34, 35], [2], 'NEG'),
        ([42, 43, 44], [2], 'NEG')
    ]
)

# REC 186 (idx 185):
# Remove invalid cause entity 'hồ Dầu Tiếng'
text_186 = lines[185].split('####')[0]
updates[185] = (
    text_186,
    [([74, 75], [34, 35, 36], 'NEU')]
)

# REC 192 (idx 191):
# Strip 'bị' from opinion: 'ngập nước nặng nhất' [4, 5, 6, 7]
text_192 = lines[191].split('####')[0]
updates[191] = (
    text_192,
    [
        ([21, 22, 23], [4, 5, 6, 7], 'NEG'),
        ([25, 26, 27], [4, 5, 6, 7], 'NEG'),
        ([29, 30, 31], [4, 5, 6, 7], 'NEG'),
        ([33, 34], [4, 5, 6, 7], 'NEG')
    ]
)

# REC 194 (idx 193):
# Remove redundant cầu Tân Thuận (anti over-tagging)
text_194 = lines[193].split('####')[0]
updates[193] = (
    text_194,
    [([1, 2, 3, 4], [8, 9, 10], 'NEG')]
)

# REC 195 (idx 194):
# Strip 'bị' -> 'ngập nước' [10, 11]
text_195 = lines[194].split('####')[0]
updates[194] = (
    text_195,
    [
        ([17, 18, 19, 20, 21], [10, 11], 'NEG'),
        ([23, 24, 25], [10, 11], 'NEG'),
        ([32, 33, 34, 35, 36], [10, 11], 'NEG'),
        ([38, 39, 40], [10, 11], 'NEG')
    ]
)

# REC 200 (idx 199):
# Strip 'bị' -> 'ngập lênh láng' [12, 13, 14]
text_200 = lines[199].split('####')[0]
updates[199] = (
    text_200,
    [
        ([5, 6], [12, 13, 14], 'NEG'),
        ([8, 9, 10], [12, 13, 14], 'NEG')
    ]
)

# REC 205 (idx 204):
# Fix repeated text corruption: 'ở TPHCM ở TPHCM ở TPHCM' -> 'ở TPHCM'
text_205 = "Chiều 6 / 11 , triều cường ở TPHCM dâng cao khiến nhiều con đường ở khu vực phía Nam TPHCM ngập mênh mông nước ."
# Tokens:
# 0:Chiều 1:6 2:/ 3:11 4:, 5:triều 6:cường 7:ở 8:TPHCM 9:dâng 10:cao 11:khiến 12:nhiều 13:con 14:đường 15:ở 16:khu 17:vực 18:phía 19:Nam 20:TPHCM 21:ngập 22:mênh 23:mông 24:nước 25:.
updates[204] = (
    text_205,
    [
        ([18, 19, 20], [21, 22, 23, 24], 'NEG'),
        ([5, 6, 7, 8], [9, 10], 'NEU')
    ]
)

# REC 206 (idx 205):
# Strip 'bị' -> 'ngập sâu' [43, 44]
text_206 = lines[205].split('####')[0]
updates[205] = (
    text_206,
    [
        ([20, 21, 22], [43, 44], 'NEG'),
        ([24, 25, 26], [43, 44], 'NEG'),
        ([28, 29, 30], [43, 44], 'NEG'),
        ([32, 33, 34], [43, 44], 'NEG'),
        ([36, 37, 38], [43, 44], 'NEG')
    ]
)

# REC 210 (idx 209):
# Strip 'bị' -> 'ngập sâu' [19, 20]
text_210 = lines[209].split('####')[0]
updates[209] = (
    text_210,
    [([1, 2, 3, 4], [19, 20], 'NEG')]
)

# REC 220 (idx 219):
# Fix repeated text corruption: 'ở TPHCM ở TPHCM ở TPHCM' -> 'ở TPHCM'
# and correct absurd aspect 'cư tại' and opinion 'bán đảo Thanh Đa'
text_220 = "Trước đó một ngày , triều cường ở TPHCM dâng cao khiến khu dân cư tại bán đảo Thanh Đa chìm trong biển nước ."
# Tokens:
# 0:Trước 1:đó 2:một 3:ngày 4:, 5:triều 6:cường 7:ở 8:TPHCM 9:dâng 10:cao 11:khiến 12:khu 13:dân 14:cư 15:tại 16:bán 17:đảo 18:Thanh 19:Đa 20:chìm 21:trong 22:biển 23:nước 24:.
updates[219] = (
    text_220,
    [
        ([16, 17, 18, 19], [20, 21, 22, 23], 'NEG'),
        ([5, 6, 7, 8], [9, 10], 'NEU')
    ]
)

# REC 228 (idx 227):
# Fix 'kẹt cứng' assigned to 'triều cường'
text_228 = lines[227].split('####')[0]
updates[227] = (
    text_228,
    [([5, 6, 7, 8], [9, 10], 'NEU')]
)

# REC 230 (idx 229):
# Aspect 'chân cầu Rạch Chiếc' -> 'cầu Rạch Chiếc' [15, 16, 17]
# Opinion: strip 'bị' -> 'ngập sâu , giao thông rơi vào cảnh ùn tắc kéo dài nhiều giờ' [19..32]
text_230 = lines[229].split('####')[0]
updates[229] = (
    text_230,
    [([15, 16, 17], list(range(19, 33)), 'NEG')]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 181-230 successfully!")
