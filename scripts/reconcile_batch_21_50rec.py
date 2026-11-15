import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# REC 289 (idx 288):
# Advisory warning -> NEU
text_289 = lines[288].split('####')[0]
updates[288] = (
    text_289,
    [([16, 17, 18, 19], [20, 21], 'NEU')]
)

# REC 294 (idx 293):
# Add CSGT support -> POS
text_294 = lines[293].split('####')[0]
# 0:Tại 1:TPHCM 2:, ... 20:tổ 21:chức 22:điều 23:tiết 24:giao 25:thông 26:, 27:hỗ 28:trợ 29:người 30:và 31:phương 32:tiện 33:qua 34:điểm 35:ngập 36:.
updates[293] = (
    text_294,
    [([1], list(range(22, 36)), 'POS')]
)

# REC 296 (idx 295):
# Fix text corruption: 'ở TPHCM ở TPHCM ở TPHCM' -> 'ở TPHCM'
text_296 = "Đây là ngày thứ ba liên tiếp TPHCM bị ngập úng do triều cường ở TPHCM dâng cao ."
# 0:Đây 1:là 2:ngày 3:thứ 4:ba 5:liên 6:tiếp 7:TPHCM 8:bị 9:ngập 10:úng 11:do 12:triều 13:cường 14:ở 15:TPHCM 16:dâng 17:cao 18:.
updates[295] = (
    text_296,
    [
        ([7], [9, 10], 'NEG'),
        ([12, 13, 14, 15], [16, 17], 'NEU')
    ]
)

# REC 306 (idx 305):
# Strip 'bị' -> 'ngập sâu , giao thông tê liệt , người dân di chuyển vô cùng khó khăn' [23..38]
text_306 = lines[305].split('####')[0]
updates[305] = (
    text_306,
    [([6, 7, 8, 9], list(range(23, 39)), 'NEG')]
)

# REC 308 (idx 307):
# Clean 'người kẹt cứng' -> 'kẹt cứng' [18, 19]
text_308 = lines[307].split('####')[0]
updates[307] = (
    text_308,
    [
        ([1, 2, 3, 4], [12, 13, 14], 'NEG'),
        ([1, 2, 3, 4], [18, 19], 'NEG')
    ]
)

# REC 310 (idx 309):
# Strip bare noun 'tình trạng ngập nước' -> 'ngập nước' [15, 16]
text_310 = lines[309].split('####')[0]
updates[309] = (
    text_310,
    [([8], [15, 16], 'NEG')]
)

# REC 319 (idx 318):
# Flood risk prevention policy -> NEU
text_319 = lines[318].split('####')[0]
updates[318] = (
    text_319,
    [([37, 38, 39, 40], [56, 57], 'NEU')]
)

# REC 326 (idx 325):
# Strip 'bị' -> 'ngập sâu' [26, 27]
text_326 = lines[325].split('####')[0]
updates[325] = (
    text_326,
    [([15, 16], [26, 27], 'NEG')]
)

# REC 330 (idx 329):
# Scientific explanation of flooding -> NEU
text_330 = lines[329].split('####')[0]
updates[329] = (
    text_330,
    [([1], [14], 'NEU')]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 21 (281-330) successfully!")
