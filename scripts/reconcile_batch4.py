import sys
import os
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

assert len(lines) == 2000

batch4 = lines[300:400]
audited_batch4 = []

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
    line = batch4[idx]
    rec_num = idx + 301
    parts = line.split('####')
    text = parts[0].strip()
    trips = ast.literal_eval(parts[1].strip())
    tokens = text.split()

    if rec_num == 301:
        # In-place 'ở TPHCM' for triều cường [23, 24]:
        toks = text.split()
        toks.insert(25, 'ở')
        toks.insert(26, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [23, 24, 25, 26] | lên cao [27, 28] NEU
        # TPHCM was [28] -> [30] | ngập úng was [39, 40] -> [41, 42] NEU
        new_trips = [
            ([30], [41, 42], 'NEU'),
            (list(range(23, 27)), [27, 28], 'NEU')
        ]
        audited_batch4.append(make_line(new_text, new_trips))

    elif rec_num == 302:
        # Fix hallucinated aspect [Sài Gòn đang] -> sông Sài Gòn [21, 22, 23] | ở cấp độ 2 [25..28] NEU
        # Remove bare triều cường
        new_trips = [
            ([21, 22, 23], list(range(25, 29)), 'NEU')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num == 303:
        # Risk warning -> NEU
        new_trips = [
            ([1], list(range(24, 43)), 'NEU')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num in (304, 305):
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 306:
        # Combine triều cường tại TPHCM [5, 6, 7, 8]
        # Remove redundant opinion 2
        new_trips = [
            ([5, 6, 7, 8], list(range(22, 39)), 'NEG')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num == 307:
        # Include 'đường' at token 1: đường Nguyễn Bình [1, 2, 3]
        # Remove Hiệp Phước, Nhà Bè (multi-level duplication in parens)
        new_trips = [
            ([1, 2, 3], list(range(34, 38)), 'NEG')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num == 308:
        # Include 'đường' at token 1: đường Huỳnh Tấn Phát [1..4]
        # Remove Quận 7
        new_trips = [
            ([1, 2, 3, 4], [12, 13, 14], 'NEG'),
            ([1, 2, 3, 4], [17, 18, 19], 'NEG')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num == 309:
        # Remove redundant opinion 2
        new_trips = [
            ([3, 4, 5], list(range(8, 25)), 'NEG')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num == 310:
        # Fix drifted opinion: tình trạng ngập nước [13..16]
        new_trips = [
            ([8], list(range(13, 17)), 'NEG')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num == 311:
        # Strip bare noun: ngập sâu [31, 32]
        new_trips = [
            (list(range(24, 28)), [31, 32], 'NEG')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num in range(312, 316):
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 316:
        # ngăn chặn triệt để tình trạng tràn đê ngập úng [45..54] POS
        new_trips = [
            ([1], list(range(45, 55)), 'POS')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num in range(317, 323):
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 323:
        # In-place 'ở TPHCM' for triều cường [1, 2]:
        toks = text.split()
        toks.insert(3, 'ở')
        toks.insert(4, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [1, 2, 3, 4] | dâng cao [12, 13] NEG
        # TPHCM was [23] -> [25] | ngập was [14] -> [16] NEG
        new_trips = [
            ([25], [16], 'NEG'),
            ([1, 2, 3, 4], [12, 13], 'NEG')
        ]
        audited_batch4.append(make_line(new_text, new_trips))

    elif rec_num == 324:
        # Include 'đường' at token 27: đường Bình Quới [27, 28, 29]
        # Remove Thanh Đa (multi-level duplication)
        new_trips = [
            ([27, 28, 29], list(range(30, 34)), 'NEG')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num in range(325, 331):
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 331:
        # Conditional forecast -> NEU
        new_trips = [
            ([1], [19], 'NEU')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num == 332:
        # Clean opinions
        new_trips = [
            ([14], [16, 17], 'NEG'),
            ([14], list(range(28, 32)), 'NEG')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num == 333:
        # Remove sông Sài Gòn (multi-level duplication)
        new_trips = [
            ([22, 23], list(range(43, 47)), 'NEU')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num == 334:
        # Conditional forecast hypothesis -> NEU
        new_trips = [
            (list(range(11, 15)), [26, 27, 28], 'NEU')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num in range(335, 340):
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 340:
        # Include 'đường' at token 21: đường Nguyễn Xuân Soạn [21..24]
        # Remove Tân Thuận (boundary marker)
        new_trips = [
            (list(range(21, 25)), list(range(39, 44)), 'NEG')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num in (341, 342):
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 343:
        # Include 'đường' at token 5: đường Huỳnh Tấn Phát [5..8]
        # Remove Phú Thuận in parens
        new_trips = [
            (list(range(5, 9)), list(range(20, 25)), 'NEG')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num == 344:
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 345:
        # Include 'đường' at token 7: đường Phú Thuận [7, 8, 9]
        new_trips = [
            ([7, 8, 9], [11, 12], 'NEG'),
            ([7, 8, 9], list(range(14, 19)), 'NEG')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num in range(346, 348):
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 348:
        # In-place 'ở TPHCM' for triều cường [5, 6]:
        toks = text.split()
        toks.insert(7, 'ở')
        toks.insert(8, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [5, 6, 7, 8] | dâng cao [9, 10] NEG
        # TPHCM was [24] -> [26] | bị ngập was [25, 26] -> [27, 28] NEG
        new_trips = [
            ([26], [27, 28], 'NEG'),
            ([5, 6, 7, 8], [9, 10], 'NEG')
        ]
        audited_batch4.append(make_line(new_text, new_trips))

    elif rec_num in range(349, 358):
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 358:
        # In-place 'ở TPHCM' for triều cường [5, 6]:
        toks = text.split()
        toks.insert(7, 'ở')
        toks.insert(8, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [5, 6, 7, 8] | dâng cao [18, 19] NEG
        # streets shifted by +2
        new_trips = [
            ([5, 6, 7, 8], [18, 19], 'NEG'),
            ([31, 32, 33], [28, 29], 'NEG'),
            ([35, 36, 37], [28, 29], 'NEG'),
            ([39, 40, 41], [28, 29], 'NEG'),
            ([43, 44, 45], [28, 29], 'NEG'),
            ([47, 48, 49], [28, 29], 'NEG')
        ]
        audited_batch4.append(make_line(new_text, new_trips))

    elif rec_num == 359:
        # Prepend fallback 'Tại TPHCM , '
        # text: Tại TPHCM , Khoảng 17 giờ 30 , khi triều cường ở TPHCM đạt đỉnh , đường phố mênh mông nước .
        new_text = "Tại TPHCM , Khoảng 17 giờ 30 , khi triều cường ở TPHCM đạt đỉnh , đường phố mênh mông nước ."
        # triều cường ở TPHCM [9, 10, 11, 12] | đạt đỉnh [13, 14] NEU
        # TPHCM [1] | mênh mông nước [18, 19, 20] NEG
        new_trips = [
            (list(range(9, 13)), [13, 14], 'NEU'),
            ([1], [18, 19, 20], 'NEG')
        ]
        audited_batch4.append(make_line(new_text, new_trips))

    elif rec_num in range(360, 364):
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 364:
        # In-place 'ở TPHCM' for Triều cường [0, 1]:
        toks = text.split()
        toks.insert(2, 'ở')
        toks.insert(3, 'TPHCM')
        new_text = ' '.join(toks)
        # Triều cường ở TPHCM is [0, 1, 2, 3] | lập đỉnh [4, 5] NEU
        new_trips = [
            ([0, 1, 2, 3], [4, 5], 'NEU')
        ]
        audited_batch4.append(make_line(new_text, new_trips))

    elif rec_num == 365:
        # In-place 'ở TPHCM' for triều cường [18, 19]:
        toks = text.split()
        toks.insert(20, 'ở')
        toks.insert(21, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [18..21] | ngập úng nghiêm trọng [24..27] NEG
        # Remove cross-clause TP. HCM
        new_trips = [
            (list(range(18, 22)), list(range(24, 28)), 'NEG')
        ]
        audited_batch4.append(make_line(new_text, new_trips))

    elif rec_num == 366:
        # Remove phường Tân Thuận (multi-level duplication)
        new_trips = [
            ([0, 1, 2, 3], list(range(8, 14)), 'NEG')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num == 367:
        # In-place 'ở TPHCM' for đỉnh triều [9, 10]:
        toks = text.split()
        toks.insert(11, 'ở')
        toks.insert(12, 'TPHCM')
        new_text = ' '.join(toks)
        # đỉnh triều ở TPHCM is [9, 10, 11, 12] | lên đến + 1 , 88m [17..22] NEU
        # streets shifted by +2
        new_trips = [
            (list(range(9, 13)), list(range(17, 23)), 'NEU'),
            ([31, 32, 33], [25, 26], 'NEG'),
            ([35, 36, 37], [25, 26], 'NEG'),
            ([39, 40, 41], [25, 26], 'NEG'),
            ([49, 50, 51], [25, 26], 'NEG')
        ]
        audited_batch4.append(make_line(new_text, new_trips))

    elif rec_num in range(368, 372):
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 372:
        # In-place 'ở TPHCM' for triều cường [3, 4]:
        toks = text.split()
        toks.insert(5, 'ở')
        toks.insert(6, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [3..6] | dâng cao [7, 8] NEG
        # TP. HCM was [8, 9] -> [10, 11] | ngập nặng was [16, 17] -> [18, 19] NEG
        new_trips = [
            ([10, 11], [18, 19], 'NEG'),
            (list(range(3, 7)), [7, 8], 'NEG')
        ]
        audited_batch4.append(make_line(new_text, new_trips))

    elif rec_num == 373:
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 374:
        # In-place 'ở TPHCM' for triều cường [9, 10]:
        toks = text.split()
        toks.insert(11, 'ở')
        toks.insert(12, 'TPHCM')
        new_text = ' '.join(toks)
        # đường Bình Quới [3, 4, 5] | ngập sâu [6, 7] NEG
        # triều cường ở TPHCM [9..12] | dâng cao [13, 14] NEG
        new_trips = [
            ([3, 4, 5], [6, 7], 'NEG'),
            (list(range(9, 13)), [13, 14], 'NEG')
        ]
        audited_batch4.append(make_line(new_text, new_trips))

    elif rec_num == 375:
        # In-place 'ở TPHCM' for Triều cường [6, 7]:
        toks = text.split()
        toks.insert(8, 'ở')
        toks.insert(9, 'TPHCM')
        new_text = ' '.join(toks)
        # Triều cường ở TPHCM is [6..9] | đạt đỉnh [10, 11] NEU
        # TP. Hồ Chí Minh [1..4] | ngập sâu was [14, 15] -> [16, 17] NEG
        new_trips = [
            (list(range(6, 10)), [10, 11], 'NEU'),
            ([1, 2, 3, 4], [16, 17], 'NEG')
        ]
        audited_batch4.append(make_line(new_text, new_trips))

    elif rec_num == 376:
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 377:
        # Remove phường Tân Hưng (multi-level duplication in parens)
        new_trips = [
            ([1, 2, 3, 4], list(range(11, 37)), 'NEG')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num in range(378, 380):
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 380:
        # Risk warning -> NEU
        new_trips = [
            ([1], [5], 'NEU')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num == 381:
        # Risk warning -> NEU
        new_trips = [
            ([1], [5, 6], 'NEU')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num in range(382, 386):
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 386:
        # In-place 'ở TPHCM' for triều cường [4, 5]:
        toks = text.split()
        toks.insert(6, 'ở')
        toks.insert(7, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [4..7] | dâng cao [8, 9] NEG
        # sông Sài Gòn was [11..13] -> [13..15] | tràn qua bờ đê was [14..17] -> [16..19] NEG
        # bán đảo Thanh Đa was [21..24] -> [23..26] | ngập sâu was [29, 30] -> [31, 32] NEG
        new_trips = [
            (list(range(4, 8)), [8, 9], 'NEG'),
            (list(range(13, 16)), list(range(16, 20)), 'NEG'),
            (list(range(23, 27)), [31, 32], 'NEG')
        ]
        audited_batch4.append(make_line(new_text, new_trips))

    elif rec_num in range(387, 390):
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 390:
        # Remove bare noun 'dòng nước'
        new_trips = [
            ([1, 2, 3, 4], list(range(8, 12)), 'NEG')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num == 391:
        # In-place 'ở TPHCM' for triều cường [6, 7]:
        toks = text.split()
        toks.insert(8, 'ở')
        toks.insert(9, 'TPHCM')
        new_text = ' '.join(toks)
        # triều cường ở TPHCM is [6..9] | đạt đỉnh [10, 11] NEU
        # bờ đê was [14, 15] -> [16, 17] | ngập sâu hơn was [17..19] -> [19..21] NEG
        new_trips = [
            (list(range(6, 10)), [10, 11], 'NEU'),
            ([16, 17], list(range(19, 22)), 'NEG')
        ]
        audited_batch4.append(make_line(new_text, new_trips))

    elif rec_num == 392:
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 393:
        # Prepend fallback 'Tại TPHCM , '
        # text: Tại TPHCM , Đến 16 giờ , triều cường ở TPHCM đạt đỉnh , cho nên trên mặt đường có nơi ngập lên đến bánh xe máy .
        new_text = "Tại TPHCM , Đến 16 giờ , triều cường ở TPHCM đạt đỉnh , cho nên trên mặt đường có nơi ngập lên đến bánh xe máy ."
        # triều cường ở TPHCM [7..10] | đạt đỉnh [11, 12] NEU
        # TPHCM [1] | ngập lên đến bánh xe máy [21..26] NEG
        new_trips = [
            (list(range(7, 11)), [11, 12], 'NEU'),
            ([1], list(range(21, 27)), 'NEG')
        ]
        audited_batch4.append(make_line(new_text, new_trips))

    elif rec_num in range(394, 396):
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 396:
        # Polarity POS for flood barrier mitigation
        new_trips = [
            ([6, 7], list(range(21, 26)), 'POS')
        ]
        audited_batch4.append(make_line(text, new_trips))

    elif rec_num == 397:
        audited_batch4.append(make_line(text, trips))

    elif rec_num == 398:
        # Prepend fallback 'Tại TPHCM , '
        new_text = "Tại TPHCM , " + text
        # TPHCM [1] | bắt đầu rút dần [12..15] POS
        new_trips = [
            ([1], list(range(12, 16)), 'POS')
        ]
        audited_batch4.append(make_line(new_text, new_trips))

    elif rec_num in (399, 400):
        audited_batch4.append(make_line(text, trips))

print(f"Audited batch 4 count: {len(audited_batch4)}")

# Update phase2.txt
updated_lines = lines[:300] + audited_batch4 + lines[400:]
assert len(updated_lines) == len(lines), f"Line count mismatch {len(updated_lines)} vs {len(lines)}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in updated_lines:
        f.write(l + '\n')

print("Successfully updated Batch 4 in data/validate_label/thuan/phase2.txt!")
