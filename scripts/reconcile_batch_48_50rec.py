# reconcile_batch_48_50rec.py
# Batch 48: Records 1631 to 1680 (0-based indices 1630 to 1679)
import json

TARGET_FILE = 'data/validate_label/thuan/phase2.txt'

with open(TARGET_FILE, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

assert len(lines) == 2000, f'Expected 2000 lines, got {len(lines)}'

updates = {
    # Rec 1631 (idx 1630): Strip passive 'bị' [94], keep 'ngập sâu' [95, 96]
    1630: [([103, 104], [95, 96], 'NEG')],

    # Rec 1632 (idx 1631): OK
    1631: [([0, 1, 2, 3], [4, 5], 'NEU')],

    # Rec 1633 (idx 1632): OK
    1632: [([30, 31], [67, 68, 69], 'NEG')],

    # Rec 1634 (idx 1633): OK
    1633: [([1], [19, 20], 'NEG')],

    # Rec 1635 (idx 1634): OK
    1634: [([0, 1, 2], [23, 24, 25, 26, 27], 'NEG')],

    # Rec 1636 (idx 1635): OK
    1635: [([6, 7, 8, 9], [10, 11], 'NEU')],

    # Rec 1637 (idx 1636): Remove parenthetical locator 'Nhà bè' [10, 11]
    1636: [([5, 6, 7], [0, 1], 'NEG')],

    # Rec 1638 (idx 1637): Split sprawling run-on [10..20] into discrete opinions 'ngập' [10] and 'chết máy' [13, 14]
    1637: [([5, 6], [10], 'NEG'), ([5, 6], [13, 14], 'NEG')],

    # Rec 1639 (idx 1638): Keep NEU forecast warning
    1638: [([2, 3, 4, 5], [6, 7], 'NEU')],

    # Rec 1640 (idx 1639): OK
    1639: [([12, 13], [31, 32, 33], 'NEG'), ([15, 16], [31, 32, 33], 'NEG'), ([24, 25], [31, 32, 33], 'NEG')],

    # Rec 1641 (idx 1640): OK
    1640: [([6, 7, 8], [17, 18, 19, 20, 21, 22], 'NEG')],

    # Rec 1642 (idx 1641): OK
    1641: [([0, 1], [2, 3], 'NEG')],

    # Rec 1643 (idx 1642): REJECT - Motorcycle maintenance/repair advice guide (PASS 10)
    1642: [],

    # Rec 1644 (idx 1643): OK
    1643: [([1], [7], 'NEG')],

    # Rec 1645 (idx 1644): OK
    1644: [([25, 26, 27, 28], [32, 33, 34, 35, 36, 37, 38], 'POS'), ([48, 49, 50, 51], [53, 54], 'POS')],

    # Rec 1646 (idx 1645): Strip passive 'bị' [155], [260] and trim run-on comma clause
    1645: [
        ([151, 152, 153, 154], [156, 157], 'NEG'),
        ([256, 257, 258], [261, 262], 'NEG'),
        ([311, 312, 313, 314], [315, 316, 317, 318, 319], 'NEG')
    ],

    # Rec 1647 (idx 1646): Refine opinion to 'ngập lút bánh' [84, 85, 86]
    1646: [
        ([40, 41, 42, 43], [84, 85, 86], 'NEG'),
        ([45, 46, 47], [84, 85, 86], 'NEG'),
        ([49, 50, 51], [84, 85, 86], 'NEG'),
        ([53, 54, 55], [84, 85, 86], 'NEG'),
        ([62, 63, 64, 65], [84, 85, 86], 'NEG'),
        ([67, 68, 69], [84, 85, 86], 'NEG'),
        ([76, 77, 78], [84, 85, 86], 'NEG')
    ],

    # Rec 1648 (idx 1647): Split sprawling run-on [26..38] into 'ngập sâu' [26, 27] and 'chết máy' [31, 32]
    1647: [([24, 25], [26, 27], 'NEG'), ([24, 25], [31, 32], 'NEG')],

    # Rec 1649 (idx 1648): OK
    1648: [([2, 3], [5, 6, 7, 8], 'NEG')],

    # Rec 1650 (idx 1649): REJECT - personal rambling about Đà Lạt aunts
    1649: [],

    # Rec 1651 (idx 1650): Strip passive 'bị' [50] and trim 17-token run-on to 'ngập sâu' [51, 52]
    1650: [([49], [51, 52], 'NEG')],

    # Rec 1652 (idx 1651): Strip passive 'bị' and split 19-token run-on to 'ngập' [44] and 'chết máy' [60, 61]
    1651: [([41, 42], [44], 'NEG'), ([41, 42], [60, 61], 'NEG')],

    # Rec 1653 (idx 1652): OK
    1652: [([27, 28, 29, 30], [16, 17], 'POS')],

    # Rec 1654 (idx 1653): Strip passive 'bị' [31], keep 'ngập sâu' [32, 33]
    1653: [([13, 14, 15, 16], [17, 18], 'NEG'), ([21, 22, 23, 24], [32, 33], 'NEG')],

    # Rec 1655 (idx 1654): Strip passive 'bị' [147], opinion is 'ngập' [148]
    1654: [
        ([155, 156, 157], [148], 'NEG'),
        ([159, 160, 161], [148], 'NEG'),
        ([163, 164, 165], [148], 'NEG'),
        ([167, 168, 169], [148], 'NEG'),
        ([171, 172, 173], [148], 'NEG'),
        ([175, 176, 177], [148], 'NEG'),
        ([179, 180], [148], 'NEG')
    ],

    # Rec 1656 (idx 1655): REJECT - Real estate promotion for T&T City Millennia in Cần Giuộc, Long An (PASS 7 & PASS 10)
    1655: [],

    # Rec 1657 (idx 1656): Trim run-on comma clause to 'ngập nước' [10, 11]
    1656: [([6], [10, 11], 'NEG')],

    # Rec 1658 (idx 1657): Fix polarity: weather precaution / risk advisory is NEU
    1657: [([2, 3, 4, 5], [31, 32], 'NEU')],

    # Rec 1659 (idx 1658): OK
    1658: [([4, 5, 6, 7], [8, 9], 'NEU')],

    # Rec 1660 (idx 1659): Trim run-on to 'ngập cục bộ' [64, 65, 66] and add Gò Vấp [80, 81, 82], Q12 [84, 85] with 'ngập sâu' [91, 92]
    1659: [
        ([26, 27, 28], [41, 42, 43, 44, 45], 'NEG'),
        ([60, 61, 62, 63], [64, 65, 66], 'NEG'),
        ([80, 81, 82], [91, 92], 'NEG'),
        ([84, 85], [91, 92], 'NEG')
    ],

    # Rec 1661 (idx 1660): Trim 14-token run-on to 'ngập như sông' [33, 34, 35]
    1660: [
        ([20, 21, 22], [33, 34, 35], 'NEG'),
        ([24, 25], [33, 34, 35], 'NEG'),
        ([27, 28], [33, 34, 35], 'NEG')
    ],

    # Rec 1662 (idx 1661): OK
    1661: [([44, 45, 46, 47], [57], 'NEG'), ([49, 50, 51], [57], 'NEG')],

    # Rec 1663 (idx 1662): Strip passive 'bị' [18], keep 'ngập nặng' [19, 20]
    1662: [([5], [19, 20], 'NEG')],

    # Rec 1664 (idx 1663): Split 19-token run-on to 'ngập lênh láng' [22, 23, 24] and 'chết máy' [30, 31]
    1663: [([5, 6], [22, 23, 24], 'NEG'), ([5, 6], [30, 31], 'NEG')],

    # Rec 1665 (idx 1664): FIX TOKENS: Aspect is 'TPHCM' [39], opinion is 'ngập lênh láng' [44, 45, 46]
    1664: [([39], [44, 45, 46], 'NEG')],

    # Rec 1666 (idx 1665): FIX TOKENS: Aspect is 'TP HCM' [22, 23], opinion is 'ngập sâu' [24, 25] and 'chết máy' [29, 30]
    1665: [([22, 23], [24, 25], 'NEG'), ([22, 23], [29, 30], 'NEG')],

    # Rec 1667 (idx 1666): REJECT - Joke / meme about bus conductors ('ngập không sợ chết máy', 'Đại gia tiền lẻ')
    1666: [],

    # Rec 1668 (idx 1667): OK
    1667: [([0, 1, 2, 3], [4, 5], 'NEG')],

    # Rec 1669 (idx 1668): OK
    1668: [([7, 8, 9, 10], [13, 14], 'NEU')],

    # Rec 1670 (idx 1669): OK
    1669: [([4, 5, 6, 7], [9, 10], 'NEU')],

    # Rec 1671 (idx 1670): OK
    1670: [([9, 10, 11, 12], [13, 14, 15], 'NEU')],

    # Rec 1672 (idx 1671): Fix aspect/polarity: forecast warning for 'TP. HCM' [17, 18], opinion 'ngập sâu' [14, 15], NEU
    1671: [([17, 18], [14, 15], 'NEU')],

    # Rec 1673 (idx 1672): OK
    1672: [([0, 1], [18, 19], 'NEG')],

    # Rec 1674 (idx 1673): Set accurate predicate for 'quốc lộ 50' [8, 9, 10] -> 'bì bõm lội nước' [13, 14, 15, 16]
    1673: [([0, 1], [2, 3], 'NEG'), ([8, 9, 10], [13, 14, 15, 16], 'NEG')],

    # Rec 1675 (idx 1674): FIX MISSING 'ngập' [41] -> 'ngập hơn nửa bánh xe máy' [41, 42, 43, 44, 45, 46]
    1674: [([32, 33, 34, 35], [41, 42, 43, 44, 45, 46], 'NEG')],

    # Rec 1676 (idx 1675): OK
    1675: [([1], [36, 37], 'NEG')],

    # Rec 1677 (idx 1676): Clean aspect to named entity 'TP. HCM' [6, 7]
    1676: [([6, 7], [8, 9], 'NEG')],

    # Rec 1678 (idx 1677): Fix dangling opinion: strip 'nước' [10] and complete to 'ngập lên đến xe buýt' [11, 12, 13, 14, 15]
    1677: [([2, 3], [11, 12, 13, 14, 15], 'NEG')],

    # Rec 1679 (idx 1678): OK
    1678: [([107, 108, 109, 110], [138, 139, 140], 'NEG')],

    # Rec 1680 (idx 1679): OK
    1679: [([50, 51, 52], [48, 49], 'NEG')]
}

print(f'Total updates in batch 48: {len(updates)}')

# Verify each update against tokens
for idx, trip_list in updates.items():
    text = lines[idx].split('####')[0]
    toks = text.split()
    for trip in trip_list:
        asp_idx, opi_idx, pol = trip
        assert all(0 <= i < len(toks) for i in asp_idx), f'Bad asp index in {idx}'
        assert all(0 <= i < len(toks) for i in opi_idx), f'Bad opi index in {idx}'
        assert pol in ['POS', 'NEG', 'NEU'], f'Bad pol in {idx}'

print('All 50 updates verified against tokens successfully!')

# Apply updates and write back
for idx, trip_list in updates.items():
    text = lines[idx].split('####')[0]
    lines[idx] = f'{text}####{trip_list}'

with open(TARGET_FILE, 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print(f'Successfully updated {len(updates)} records in {TARGET_FILE}!')
