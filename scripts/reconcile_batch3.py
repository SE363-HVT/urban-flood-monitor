import sys
import os
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

assert len(lines) == 2000

batch3 = lines[200:300]
audited_batch3 = []

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
    line = batch3[idx]
    rec_num = idx + 201
    parts = line.split('####')
    text = parts[0].strip()
    trips = ast.literal_eval(parts[1].strip())
    tokens = text.split()

    if rec_num in (201, 202):
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 203:
        # Include 'đường' at token 2: đường Phú Thuận [2, 3, 4]
        new_trips = [
            ([2, 3, 4], [12, 13, 14], 'POS'),
            ([6, 7, 8], [12, 13, 14], 'POS')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 204:
        # Include 'đường' at token 2: đường Trần Xuân Soạn [2, 3, 4, 5]
        new_trips = [
            ([2, 3, 4, 5], [12, 13, 14], 'POS'),
            ([2, 3, 4, 5], [23, 24], 'POS'),
            ([19, 20], [16, 17], 'POS')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 205:
        # In-place 'ở TPHCM' for triều cường [5, 6]:
        toks = text.split()
        toks.insert(7, 'ở')
        toks.insert(8, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [5, 6, 7, 8] | dâng cao [9, 10] NEG
        # TPHCM was [18] -> [20] | ngập mênh mông nước was [19..22] -> [21..24] NEG
        new_trips = [
            ([20], list(range(21, 25)), 'NEG'),
            ([5, 6, 7, 8], [9, 10], 'NEG')
        ]
        audited_batch3.append(make_line(new_text, new_trips))

    elif rec_num == 206:
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 207:
        # Remove redundant [17..22]
        new_trips = [
            ([1, 2, 3, 4], list(range(6, 36)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 208:
        # Include 'đường' at token 5: đường Phạm Hữu Lầu [5..8]
        # Strip bare noun 'Điểm' [0], keep 'ngập sâu nhất' [1, 2, 3]
        # Remove 15B, D1
        new_trips = [
            (list(range(5, 9)), [1, 2, 3], 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num in range(209, 213):
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 213:
        # Fix drifted opinion [30, 31] -> ngập úng [29, 30] NEU
        new_trips = [
            (list(range(9, 13)), [29, 30], 'NEU')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 214:
        # Include 'đường' at token 26: đường Phạm Hữu Lầu [26..29]
        new_trips = [
            (list(range(26, 30)), list(range(9, 13)), 'POS')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num in range(215, 218):
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 218:
        audited_batch3.append(f"{text}####[]")

    elif rec_num == 219:
        # Remove Bình Quới (multi-level duplication with hẻm 558)
        new_trips = [
            ([20, 21], list(range(28, 48)), 'POS')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 220:
        # In-place 'ở TPHCM' for triều cường [5, 6]:
        toks = text.split()
        toks.insert(7, 'ở')
        toks.insert(8, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [5, 6, 7, 8] | dâng cao [9, 10] NEG
        # Thanh Đa was [16, 17] -> [18, 19] | chìm trong biển nước was [18..21] -> [20..23] NEG
        new_trips = [
            ([18, 19], list(range(20, 24)), 'NEG'),
            ([5, 6, 7, 8], [9, 10], 'NEG')
        ]
        audited_batch3.append(make_line(new_text, new_trips))

    elif rec_num == 221:
        # Remove Bình Quới (multi-level duplication in parens)
        new_trips = [
            ([1, 2, 3, 4], list(range(19, 23)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num in range(222, 227):
        audited_batch3.append(make_line(text, trips))

    elif rec_num in (227, 229):
        audited_batch3.append(f"{text}####[]")

    elif rec_num == 228:
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 230:
        # Remove redundant [24..30]
        new_trips = [
            (list(range(14, 18)), list(range(18, 33)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 231:
        # Include 'duy' at token 24: duy trì ở mức cao [24..28]
        new_trips = [
            ([18, 19, 20], list(range(24, 29)), 'NEU')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num in range(232, 236):
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 236:
        # Fix truncated opinion: tràn lên mặt đường [10..13]
        new_trips = [
            ([1], list(range(10, 14)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 237:
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 238:
        # Include 'đường' at token 12: đường Phạm Hữu Lầu [12..15]
        new_trips = [
            (list(range(12, 16)), list(range(16, 21)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 239:
        # Remove TPHCM (broad area)
        # [35, 36, 37] is '1 , 85m'
        new_trips = [
            ([29, 30], list(range(22, 27)), 'NEU'),
            ([32, 33], list(range(22, 27)), 'NEU'),
            (list(range(40, 43)), [35, 36, 37], 'NEU')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 240:
        # Include 'Đường' at token 0: Đường Phạm Hữu Lầu [0..3]
        new_trips = [
            ([0, 1, 2, 3], list(range(10, 15)), 'NEG'),
            ([0, 1, 2, 3], list(range(16, 24)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 241:
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 242:
        # bì bõm lội nước về nhà is [19..24] (token 25 is period '.')
        new_trips = [
            ([0, 1, 2, 3], [4, 5], 'NEG'),
            ([0, 1, 2, 3], list(range(19, 25)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num in range(243, 246):
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 246:
        # Include 'đường' at token 4: đường Phạm Hữu Lầu [4..7]
        new_trips = [
            ([4, 5, 6, 7], [10, 11], 'NEG'),
            ([4, 5, 6, 7], list(range(13, 19)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 247:
        # Remove TPHCM and bare triều cường
        new_trips = [
            ([19, 20], list(range(25, 30)), 'NEG'),
            ([22, 23], list(range(25, 30)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 248:
        # Remove Bình Quới (multi-level duplication in parens)
        new_trips = [
            ([3, 4], [14, 15, 16], 'NEG'),
            ([3, 4], [20, 21], 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 249:
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 250:
        # Include 'hẻm' at token 7: hẻm 92 Thanh Đa [7..10]
        new_trips = [
            (list(range(7, 11)), [16, 17, 18], 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 251:
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 252:
        # Include 'phường' at token 8: phường Xóm Chiếu [8, 9, 10]
        # Remove TPHCM (multi-level duplication)
        new_trips = [
            ([8, 9, 10], list(range(18, 23)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num in range(253, 255):
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 255:
        # Include 'đường' at token 5: đường Đặng Thùy Trâm [5..8]
        # Remove Bình Lợi Trung in parens
        new_trips = [
            (list(range(5, 9)), list(range(17, 22)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 256:
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 257:
        # Include 'đường' at token 14: đường Trần Xuân Soạn [14..17]
        new_trips = [
            (list(range(14, 18)), list(range(0, 7)), 'NEG'),
            (list(range(14, 18)), [11, 12], 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num in range(258, 261):
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 261:
        # nước ngập vào tận cửa hàng is [9..14]
        new_trips = [
            (list(range(3, 7)), list(range(9, 15)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 262:
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 263:
        # Split clean opinions
        new_trips = [
            ([2, 3, 4, 5], list(range(6, 10)), 'NEG'),
            ([2, 3, 4, 5], list(range(11, 16)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num in range(264, 268):
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 268:
        # Include 'Đường' at token 0: Đường Phạm Hữu Lầu [0..3]
        # Remove Huỳnh Tấn Phát (boundary marker)
        new_trips = [
            ([0, 1, 2, 3], list(range(16, 20)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num in range(269, 274):
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 274:
        # Combine triều cường tại TP. HCM [10..14]
        new_trips = [
            (list(range(10, 15)), [15, 16], 'NEU'),
            (list(range(10, 15)), list(range(18, 35)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 275:
        # Include 'đường' at token 10: đường Bình Quới [10, 11, 12]
        # Remove phường Bình Quới in parens
        new_trips = [
            ([10, 11, 12], list(range(22, 27)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num in range(276, 282):
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 282:
        # Remove Bình Quới (multi-level duplication)
        new_trips = [
            ([3, 4], [31, 32, 33], 'NEG'),
            ([12, 13, 14], list(range(15, 19)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 283:
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 284:
        # Include 'phường' at token 7: phường Bình Quới [7, 8, 9]
        # Opinion: nước dâng ngập hết cả nhà is [37..42]
        new_trips = [
            ([7, 8, 9], list(range(37, 43)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 285:
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 286:
        # Include 'hẻm' at token 7: hẻm 140 Bình Quới [7..10]
        new_trips = [
            (list(range(7, 11)), list(range(17, 22)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num in range(287, 291):
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 291:
        # Include 'đường' at token 1: đường Trần Xuân Soạn [1..4]
        # Fix opinion boundary [hàng loạt xe chết máy] [20..24]
        new_trips = [
            ([1, 2, 3, 4], [17, 18], 'NEG'),
            ([1, 2, 3, 4], list(range(20, 25)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num == 292:
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 293:
        # Remove Tân Mỹ in parens
        new_trips = [
            ([4, 5, 6], list(range(18, 23)), 'NEG'),
            ([8, 9, 10], list(range(18, 23)), 'NEG')
        ]
        audited_batch3.append(make_line(text, new_trips))

    elif rec_num in range(294, 296):
        audited_batch3.append(make_line(text, trips))

    elif rec_num == 296:
        # In-place 'ở TPHCM' for triều cường [12, 13]:
        toks = text.split()
        toks.insert(14, 'ở')
        toks.insert(15, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [12, 13, 14, 15] | dâng cao [16, 17] NEG
        # TPHCM [7] | ngập úng [9, 10] NEG
        new_trips = [
            ([7], [9, 10], 'NEG'),
            (list(range(12, 16)), [16, 17], 'NEG')
        ]
        audited_batch3.append(make_line(new_text, new_trips))

    elif rec_num in range(297, 301):
        audited_batch3.append(make_line(text, trips))

print(f"Audited batch 3 count: {len(audited_batch3)}")

# Update phase2.txt
updated_lines = lines[:200] + audited_batch3 + lines[300:]
assert len(updated_lines) == len(lines), f"Line count mismatch {len(updated_lines)} vs {len(lines)}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in updated_lines:
        f.write(l + '\n')

print("Successfully updated Batch 3 in data/validate_label/thuan/phase2.txt!")
