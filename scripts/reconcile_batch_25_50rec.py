import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# REC 484 (idx 483):
# Strip 'bị' -> 'chết máy' [14, 15]
text_484 = lines[483].split('####')[0]
updates[483] = (
    text_484,
    [
        ([0, 1, 2, 3], [5], 'NEG'),
        ([0, 1, 2, 3], [14, 15], 'NEG')
    ]
)

# REC 488 (idx 487):
# Anti-overtagging: remove khu Thanh Đa
text_488 = lines[487].split('####')[0]
updates[487] = (
    text_488,
    [([13, 14], list(range(3, 9)), 'NEG')]
)

# REC 500 (idx 499):
# Fix truncated opinion 'hơn nửa bánh xe' -> 'nước ngập hơn nửa bánh xe' [8..13]
text_500 = lines[499].split('####')[0]
updates[499] = (
    text_500,
    [([1], list(range(8, 14)), 'NEG')]
)

# REC 504 (idx 503):
# Anti-overtagging: remove phường Bình Đông
text_504 = lines[503].split('####')[0]
updates[503] = (
    text_504,
    [([3, 4, 5, 6, 7], [20, 21], 'NEG')]
)

# REC 506 (idx 505):
# Add CSGT POS action
text_506 = lines[505].split('####')[0]
# 0:Giao 1:lộ 2:Huỳnh 3:Tấn 4:Phát 5:- 6:Phú 7:Thuận 8:ngập 9:rất 10:sâu 11:, 12:CSGT 13:trạm 14:Đa 15:Phước 16:điều 17:tiết 18:giao 19:thông 20:và 21:hỗ 22:trợ 23:người 24:dân 25:.
updates[505] = (
    text_506,
    [
        ([2, 3, 4], [8, 9, 10], 'NEG'),
        ([6, 7], [8, 9, 10], 'NEG'),
        ([2, 3, 4], list(range(16, 25)), 'POS')
    ]
)

# REC 513 (idx 512):
# Add fallback 'Tại TPHCM , ' to replace bare noun 'mặt đường'
# Text original: Từ khoảng 16 giờ ngày 22_10 . 2025 , sau trận mưa lớn , nước từ kênh Đôi bắt đầu dâng cao , chỉ sau nửa giờ , mặt đường đã ngập sâu hơn nửa bánh xe .
# Clean text: Tại TPHCM , Từ khoảng 16 giờ ngày 22_10 . 2025 , sau trận mưa lớn , nước từ kênh Đôi bắt đầu dâng cao , chỉ sau nửa giờ , mặt đường đã ngập sâu hơn nửa bánh xe .
text_513 = f"Tại TPHCM , {lines[512].split('####')[0]}"
# Tokens of text_513:
# 0:Tại 1:TPHCM 2:, 3:Từ 4:khoảng 5:16 6:giờ 7:ngày 8:22_10 9:. 10:2025 11:, 12:sau 13:trận 14:mưa 15:lớn 16:, 17:nước 18:từ 19:kênh 20:Đôi 21:bắt 22:đầu 23:dâng 24:cao 25:, 26:chỉ 27:sau 28:nửa 29:giờ 30:, 31:mặt 32:đường 33:đã 34:ngập 35:sâu 36:hơn 37:nửa 38:bánh 39:xe 40:.
updates[512] = (
    text_513,
    [
        ([19, 20], [21, 22, 23, 24], 'NEG'),
        ([1], list(range(34, 40)), 'NEG')
    ]
)

# REC 514 (idx 513):
# Remove redundant sub-span
text_514 = lines[513].split('####')[0]
updates[513] = (
    text_514,
    [([1, 2, 3, 4], list(range(7, 27)), 'NEG')]
)

# REC 522 (idx 521):
# Add fallback 'Tại TPHCM , ' to replace bare noun 'đường sá'
text_522 = f"Tại TPHCM , {lines[521].split('####')[0]}"
# 0:Tại 1:TPHCM 2:, 3:Hơn 4:18 5:giờ 6:, 7:mưa 8:đã 9:tạnh 10:dần 11:nhưng 12:đường 13:sá 14:vẫn 15:ngập 16:.
updates[521] = (
    text_522,
    [([1], [14, 15], 'NEG')]
)

# REC 523 (idx 522):
# Anti-overtagging: remove phường Cầu Ông Lãnh
text_523 = lines[522].split('####')[0]
updates[522] = (
    text_523,
    [
        ([3, 4, 5], [31, 32], 'NEG'),
        ([7, 8, 9, 10], [31, 32], 'NEG')
    ]
)

# REC 525 (idx 524):
# Rich single opinion
text_525 = lines[524].split('####')[0]
updates[524] = (
    text_525,
    [([1, 2, 3, 4], list(range(10, 30)), 'NEG')]
)

# REC 527 (idx 526):
# Strip generic prefix 'tuyến' -> 'đường Trần Hưng Đạo' [2, 3, 4, 5]
text_527 = lines[526].split('####')[0]
updates[526] = (
    text_527,
    [
        ([2, 3, 4, 5], [7, 8, 9, 10], 'NEG'),
        ([2, 3, 4, 5], list(range(12, 24)), 'NEG')
    ]
)

for idx, (t, tr) in updates.items():
    lines[idx] = f"{t}####{tr}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"Reconciled {len(updates)} records in Batch 25 (481-530) successfully!")
