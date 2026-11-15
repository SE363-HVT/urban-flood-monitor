import sys
import os
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

assert len(lines) == 2000

batch2 = lines[100:200]
audited_batch2 = []

def make_line(text, triplets):
    tokens = text.split()
    for a, o, p in triplets:
        assert p in ('POS', 'NEU', 'NEG'), f"Bad pol {p}"
        assert a == list(range(a[0], a[-1] + 1)), f"Non-contig aspect {a}"
        assert o == list(range(o[0], o[-1] + 1)), f"Non-contig opinion {o}"
        assert a[-1] < len(tokens) and a[0] >= 0, f"Aspect OOB {a} len {len(tokens)}"
        assert o[-1] < len(tokens) and o[0] >= 0, f"Opinion OOB {o} len {len(tokens)}"
    return f"{text}####{triplets}"

for idx in range(100):
    line = batch2[idx]
    rec_num = idx + 101
    parts = line.split('####')
    text = parts[0].strip()
    trips = ast.literal_eval(parts[1].strip())
    tokens = text.split()

    if rec_num == 101:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 102:
        # Remove redundant [14..19]
        new_trips = [
            ([0, 1], [2, 3], 'NEG'),
            ([0, 1], list(range(8, 22)), 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 103:
        # Remove redundant [19..23]
        new_trips = [
            ([8, 9], list(range(13, 24)), 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 104:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 105:
        # Verbatim prefix: đường Phan Huy Ích [31, 32, 33, 34]
        new_trips = [
            ([31, 32, 33, 34], list(range(37, 54)), 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 106 or rec_num == 107:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 108:
        # Remove Bình Thạnh (multi-level duplication)
        new_trips = [
            ([4, 5, 6], [2, 3], 'NEG'),
            ([10, 11, 12], [8, 9], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 109 or rec_num == 110 or rec_num == 111 or rec_num == 112 or rec_num == 113 or rec_num == 114:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 115:
        # Verbatim prefix: đường Phan Huy Ích [5, 6, 7, 8]
        new_trips = [
            ([5, 6, 7, 8], list(range(9, 13)), 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 116:
        # Fix hallucinated aspect [cảnh này cho] -> SG [8] | đường hay là sông [4..7] NEU
        new_trips = [
            ([8], list(range(4, 8)), 'NEU')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 117:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 118:
        # Fix grammar boundary: nước ngập vô nhà [14..17]
        new_trips = [
            ([1, 2, 3, 4], list(range(14, 18)), 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 119:
        # Remove xã Vĩnh Lộc (multi-level duplication)
        new_trips = [
            ([18, 19, 20], [10, 11], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 120:
        # Fix truncated opinions and add stations
        new_trips = [
            ([1, 2], list(range(4, 8)), 'NEU')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 121 or rec_num == 122:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 123:
        # Include 'dự' in aspect: dự án chống ngập này [10..14]
        new_trips = [
            (list(range(10, 15)), list(range(0, 9)), 'POS')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 124:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 125:
        # Remove Ga Đại Học Quốc Gia (redundant)
        new_trips = [
            ([10, 11], [12, 13], 'POS')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 126:
        audited_batch2.append(f"{text}####[]")

    elif rec_num == 127:
        # Remove Bình Tân (multi-level duplication)
        new_trips = [
            ([15, 16, 17], [11, 12], 'NEG'),
            ([19, 20], [11, 12], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 128:
        # Remove Xã Vĩnh Lộc (multi-level duplication)
        new_trips = [
            (list(range(8, 12)), list(range(16, 31)), 'NEG'),
            (list(range(13, 16)), list(range(16, 31)), 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 129:
        # Remove Phường 25, Bình Thạnh (multi-level duplication)
        # Verbatim prefix: đường Ung Văn Khiêm [8..11]
        new_trips = [
            (list(range(8, 12)), [16, 17], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 130:
        # Include 'Đường' at token 0: Đường Phan Huy Ích [0, 1, 2, 3]
        new_trips = [
            ([0, 1, 2, 3], [5, 6, 7], 'NEG'),
            ([0, 1, 2, 3], list(range(14, 19)), 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 131:
        # Include 'đường' at token 6: đường Trần Xuân Soạn [6..9]
        # Remove Quận 7, remove bare Triều cường
        new_trips = [
            (list(range(6, 10)), list(range(13, 26)), 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 132:
        # Remove Sài Gòn (multi-level duplication)
        new_trips = [
            ([8], [11, 12, 13], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num in range(133, 143):
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 143:
        # Remove bình tân (multi-level duplication)
        new_trips = [
            ([2, 3], [11, 12], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 144:
        # Strip bare noun 'Điểm' [6], keep 'ngập nặng nhất' [7, 8, 9]
        new_trips = [
            ([13], [7, 8, 9], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 145 or rec_num == 146 or rec_num == 147 or rec_num == 148 or rec_num == 149:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 150:
        # Strip prep leak 'ở' [15]
        new_trips = [
            ([16, 17], list(range(2, 6)), 'NEG'),
            ([16, 17], list(range(7, 12)), 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 151:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 152:
        # In-place 'ở TPHCM' for Triều cường [7, 8]:
        toks = text.split()
        toks.insert(9, 'ở')
        toks.insert(10, 'TPHCM')
        new_text = ' '.join(toks)
        # Triều cường ở TPHCM is [7, 8, 9, 10]
        # đang dân cao was [9, 10, 11] -> [11, 12, 13]
        # SÀI GÒN [0, 1] | kẹt xe was [19, 20] -> [21, 22] | nước ngập was [21, 22] -> [23, 24]
        new_trips = [
            ([0, 1], [21, 22], 'NEG'),
            ([0, 1], [23, 24], 'NEG'),
            ([7, 8, 9, 10], [11, 12, 13], 'NEG')
        ]
        audited_batch2.append(make_line(new_text, new_trips))

    elif rec_num == 153:
        # In-place 'ở TPHCM' for triều cường [20, 21]:
        toks = text.split()
        toks.insert(22, 'ở')
        toks.insert(23, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [20, 21, 22, 23]
        # đạt đỉnh vượt báo động 3 was [22..27] -> [24..29]
        # TP. HCM [0, 1] | mưa lớn kéo dài [2..5]
        new_trips = [
            ([0, 1], list(range(2, 6)), 'NEU'),
            (list(range(20, 24)), list(range(24, 30)), 'NEU')
        ]
        audited_batch2.append(make_line(new_text, new_trips))

    elif rec_num == 154:
        # Remove bare triều cường [17, 18], keep TP. HCM [25, 26] | lên cao [19, 20] NEU
        new_trips = [
            ([25, 26], [19, 20], 'NEU')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 155:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 156:
        audited_batch2.append(f"{text}####[]")

    elif rec_num == 157 or rec_num == 158:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 159:
        # Include 'đường' at token 16: đường Cây Trâm [16, 17, 18]
        # Remove Gò Vấp (multi-level duplication)
        new_trips = [
            ([16, 17, 18], [13, 14], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 160 or rec_num == 161:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 162:
        # Include 'Đường' at token 0: Đường Nguyễn Văn Khối [0, 1, 2, 3]
        # Remove Thông Tây Hội (multi-level duplication)
        new_trips = [
            ([0, 1, 2, 3], list(range(11, 16)), 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 163:
        # Remove Quận Thủ Đức (multi-level duplication)
        new_trips = [
            ([0, 1, 2], list(range(16, 23)), 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 164:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 165:
        audited_batch2.append(f"{text}####[]")

    elif rec_num == 166:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 167:
        # In-place 'ở TPHCM' for triều cường [6, 7]:
        toks = text.split()
        toks.insert(8, 'ở')
        toks.insert(9, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [6, 7, 8, 9]
        # bắt đầu đạt đỉnh was [8..11] -> [10..13]
        new_trips = [
            ([6, 7, 8, 9], list(range(10, 14)), 'NEU')
        ]
        audited_batch2.append(make_line(new_text, new_trips))

    elif rec_num == 168 or rec_num == 169:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 170:
        # Include 'đường' at token 1: đường Trần Xuân Soạn [1, 2, 3, 4]
        new_trips = [
            ([1, 2, 3, 4], list(range(15, 19)), 'POS')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num in range(171, 175):
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 175:
        # Include 'đường' at token 2: đường Phạm Hữu Lầu [2, 3, 4, 5]
        new_trips = [
            ([2, 3, 4, 5], [11, 12], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 176:
        # Include 'đường' at token 1: đường Huỳnh Tấn Phát [1, 2, 3, 4]
        new_trips = [
            ([1, 2, 3, 4], [10, 11, 12], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num in range(177, 180):
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 180:
        # Combine triều cường tại TPHCM [5, 6, 7, 8]
        new_trips = [
            ([5, 6, 7, 8], list(range(9, 14)), 'NEU'),
            ([5, 6, 7, 8], [20, 21], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 181:
        # Include 'đường' at token 5: đường Nguyễn Văn Linh [5..8]
        # Remove Tân Thuận in parens
        new_trips = [
            (list(range(5, 9)), list(range(23, 29)), 'NEG'),
            ([14, 15, 16], list(range(23, 29)), 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 182:
        # Include 'đường' at token 7: đường Trần Xuân Soạn [7..10]
        # Include 'đường' at token 32: đường Võ Nguyên Giáp [32..35]
        new_trips = [
            (list(range(7, 11)), [0, 1, 2], 'NEG'),
            ([12, 13, 14], [0, 1, 2], 'NEG'),
            ([24, 25], [0, 1, 2], 'NEG'),
            (list(range(32, 36)), [0, 1, 2], 'NEG'),
            ([42, 43, 44], [0, 1, 2], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 183:
        # Strip 'đạt đỉnh , ' at start of warning opinion:
        # 'cần đề phòng ngập ở các vùng trũng thấp , ven sông , ảnh hưởng đến giao thông và hoạt động kinh tế - xã hội' [10..36]
        new_trips = [
            ([2, 3, 4, 5], list(range(10, 37)), 'NEU')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 184:
        # In-place 'ở TPHCM' for triều cường [9, 10]:
        toks = text.split()
        toks.insert(11, 'ở')
        toks.insert(12, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [9, 10, 11, 12]
        # đang lên nhanh và đạt đỉnh was [17..21] -> [19..23]
        new_trips = [
            (list(range(9, 13)), list(range(19, 24)), 'NEU')
        ]
        audited_batch2.append(make_line(new_text, new_trips))

    elif rec_num in range(185, 187):
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 187:
        # Remove bare triều cường [7, 8]
        new_trips = [
            ([13, 14, 15], list(range(16, 20)), 'NEU')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 188:
        # Include 'nặng' [30]: từng ngập nặng [28, 29, 30]
        new_trips = [
            ([1], [28, 29, 30], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num in range(189, 191):
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 191:
        # Include 'đường' prefixes:
        # đường Phú Thuận [37, 38, 39]
        # đường Nguyễn Văn Quỳ [52, 53, 54, 55]
        # đường Nguyễn Lương Bằng [57, 58, 59, 60]
        # đường Hoàng Quốc Việt [68, 69, 70, 71]
        # đường Nguyễn Thị Thập [73, 74, 75, 76]
        # đường 15B [78, 79]
        # đường D1 [81, 82]
        new_trips = [
            ([37, 38, 39], [31, 32], 'NEG'),
            (list(range(52, 56)), [31, 32], 'NEG'),
            (list(range(57, 61)), [31, 32], 'NEG'),
            (list(range(68, 72)), [31, 32], 'NEG'),
            (list(range(73, 77)), [31, 32], 'NEG'),
            ([78, 79], [31, 32], 'NEG'),
            ([81, 82], [31, 32], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 192:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 193:
        # Include 'đường' at token 1: đường Phạm Hữu Lầu [1, 2, 3, 4]
        new_trips = [
            ([1, 2, 3, 4], list(range(6, 13)), 'NEG'),
            ([1, 2, 3, 4], list(range(14, 21)), 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 194:
        # Include 'đường' at token 1: đường Trần Xuân Soạn [1, 2, 3, 4]
        new_trips = [
            ([1, 2, 3, 4], [8, 9, 10], 'NEG'),
            ([18, 19, 20], [8, 9, 10], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 195:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 196:
        # In-place 'ở TPHCM' for triều cường [5, 6]:
        toks = text.split()
        toks.insert(7, 'ở')
        toks.insert(8, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [5, 6, 7, 8]
        # dâng cao và tràn vào was [15..19] -> [17..21]
        new_trips = [
            ([5, 6, 7, 8], list(range(17, 22)), 'NEG')
        ]
        audited_batch2.append(make_line(new_text, new_trips))

    elif rec_num == 197:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 198:
        # Include 'đường' at token 11: đường Phạm Hữu Lầu [11..14]
        # Remove Tân Mỹ (multi-level duplication)
        new_trips = [
            (list(range(11, 15)), [20, 21], 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

    elif rec_num == 199:
        audited_batch2.append(make_line(text, trips))

    elif rec_num == 200:
        # Include 'đường' at token 5: đường 15B [5, 6]
        new_trips = [
            ([5, 6], list(range(11, 15)), 'NEG'),
            ([8, 9, 10], list(range(11, 15)), 'NEG')
        ]
        audited_batch2.append(make_line(text, new_trips))

print(f"Audited batch 2 count: {len(audited_batch2)}")

# Update phase2.txt
updated_lines = lines[:100] + audited_batch2 + lines[200:]
assert len(updated_lines) == len(lines), f"Line count mismatch {len(updated_lines)} vs {len(lines)}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in updated_lines:
        f.write(l + '\n')

print("Successfully updated Batch 2 in data/validate_label/thuan/phase2.txt!")
