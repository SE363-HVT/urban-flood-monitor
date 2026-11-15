# reconcile_batch_50_50rec.py
# Batch 50: Records 1731 to 1780 (0-based indices 1730 to 1779)

TARGET_FILE = 'data/validate_label/thuan/phase2.txt'

with open(TARGET_FILE, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

assert len(lines) == 2000, f'Expected 2000 lines, got {len(lines)}'

updates = {
    # Rec 1731 (idx 1730): OK
    1730: [([1, 2, 3, 4], [10, 11], 'POS')],

    # Rec 1732 (idx 1731): OK
    1731: [([19, 20], [5, 6], 'POS')],

    # Rec 1733 (idx 1732): FIX POLARITY FLIP & TRUNCATION: 'giảm ngập' [16, 17] POS on 'TPHCM' [14]
    1732: [([14], [16, 17], 'POS')],

    # Rec 1734 (idx 1733): OK
    1733: [([24], [19, 20], 'NEG')],

    # Rec 1735 (idx 1734): FIX ASPECT: 'thành phố' [15, 16] faces 'ngập úng' [22, 23] NEG
    1734: [([15, 16], [22, 23], 'NEG')],

    # Rec 1736 (idx 1735): OK
    1735: [([9, 10, 11, 12], [17, 18, 19], 'NEU')],

    # Rec 1737 (idx 1736): Conditional forecast 'có thể ngập' -> NEU
    1736: [([16, 17, 18, 19], [22], 'NEU')],

    # Rec 1738 (idx 1737): Trim 13-token run-on to 'ngập sâu' [37, 38]
    1737: [([23, 24], [37, 38], 'NEG')],

    # Rec 1739 (idx 1738): Trim 15-token run-on to 'ngập lênh láng' [25, 26, 27]
    1738: [([1], [25, 26, 27], 'NEG')],

    # Rec 1740 (idx 1739): Trim 24-token run-on to 'dâng cao phủ kín mặt đường' [15, 16, 17, 18, 19, 20]
    1739: [([4, 5, 6], [15, 16, 17, 18, 19, 20], 'NEG')],

    # Rec 1741 (idx 1740): FIX POLARITY FLIP & TRUNCATION: 'rút chậm' [29, 30] NEG
    1740: [([1], [29, 30], 'NEG')],

    # Rec 1742 (idx 1741): OK
    1741: [([1], [19], 'NEG')],

    # Rec 1743 (idx 1742): OK
    1742: [([23, 24, 25], [26, 27], 'NEG')],

    # Rec 1744 (idx 1743): OK
    1743: [([1], [4, 5, 6], 'NEG')],

    # Rec 1745 (idx 1744): FIX CHỜ NƯỚC RÚT TRAP: 'chờ nước rút' [12, 13, 14] NEG
    1744: [([1], [12, 13, 14], 'NEG')],

    # Rec 1746 (idx 1745): OK
    1745: [([1, 2, 3, 4], [21], 'NEG')],

    # Rec 1747 (idx 1746): Recommendation/advisory to avoid flood areas -> NEU
    1746: [([1, 2, 3, 4], [30, 31], 'NEU')],

    # Rec 1748 (idx 1747): Trim 21-token run-on to 'ngập sâu' [23, 24]
    1747: [([12, 13], [23, 24], 'NEG')],

    # Rec 1749 (idx 1748): OK
    1748: [([1, 2, 3, 4], [13, 14], 'NEG')],

    # Rec 1750 (idx 1749): OK
    1749: [([1, 2, 3, 4], [14, 15], 'NEG')],

    # Rec 1751 (idx 1750): OK
    1750: [([1, 2, 3, 4], [19], 'NEG')],

    # Rec 1752 (idx 1751): OK
    1751: [([16, 17, 18, 19, 20], [10, 11, 12, 13, 14], 'NEG')],

    # Rec 1753 (idx 1752): Trim comma run-on to 'ngập nặng' [27, 28]
    1752: [([13, 14, 15, 16, 17], [27, 28], 'NEG')],

    # Rec 1754 (idx 1753): Trim 10-token run-on to 'ngập sâu' [15, 16]
    1753: [([0, 1, 2, 3], [15, 16], 'NEG')],

    # Rec 1755 (idx 1754): Add 'ngập sâu' [14, 15] alongside 'chết máy' [19, 20]
    1754: [([1, 2, 3, 4], [14, 15], 'NEG'), ([1, 2, 3, 4], [19, 20], 'NEG')],

    # Rec 1756 (idx 1755): OK
    1755: [([4, 5], [8, 9], 'NEG')],

    # Rec 1757 (idx 1756): OK
    1756: [
        ([0, 1, 2], [13, 14, 15, 16], 'NEG'),
        ([4, 5, 6, 7], [13, 14, 15, 16], 'NEG')
    ],

    # Rec 1758 (idx 1757): Trim 15-token run-on to 'ngập nặng' [22, 23]
    1757: [([7, 8, 9, 10, 11], [22, 23], 'NEG')],

    # Rec 1759 (idx 1758): Trim 12-token run-on to 'ngập' [30]
    1758: [([18, 19, 20, 21, 22], [30], 'NEG')],

    # Rec 1760 (idx 1759): OK
    1759: [
        ([9, 10, 11, 12], [0, 1, 2], 'NEG'),
        ([15, 16, 17], [0, 1, 2], 'NEG')
    ],

    # Rec 1761 (idx 1760): OK
    1760: [([1], [36], 'NEG')],

    # Rec 1762 (idx 1761): OK
    1761: [([1, 2, 3, 4], [19], 'NEG')],

    # Rec 1763 (idx 1762): Trim 17-token opposite compound clauses to Clause 1: 'nước rút nhanh hơn' [14, 15, 16, 17] POS
    1762: [([3, 4, 5, 6], [14, 15, 16, 17], 'POS')],

    # Rec 1764 (idx 1763): OK
    1763: [
        ([28, 29], [23, 24, 25], 'NEG'),
        ([31, 32, 33], [23, 24, 25], 'NEG'),
        ([35, 36, 37], [23, 24, 25], 'NEG'),
        ([44, 45, 46], [23, 24, 25], 'NEG'),
        ([48, 49, 50], [23, 24, 25], 'NEG')
    ],

    # Rec 1765 (idx 1764): OK
    1764: [
        ([12, 13], [25, 26, 27, 28], 'NEG'),
        ([15, 16, 17], [25, 26, 27, 28], 'NEG'),
        ([19, 20, 21], [25, 26, 27, 28], 'NEG')
    ],

    # Rec 1766 (idx 1765): Trim 20-token run-on to 'ngập sâu' [7, 8]
    1765: [([1, 2, 3, 4], [7, 8], 'NEG')],

    # Rec 1767 (idx 1766): Strip leading 'nước' [10] -> 'ngập lên đến yên xe máy' [11, 12, 13, 14, 15, 16]
    1766: [([1, 2, 3, 4, 5, 6, 7, 8], [11, 12, 13, 14, 15, 16], 'NEG')],

    # Rec 1768 (idx 1767): OK
    1767: [([1], [28], 'NEG')],

    # Rec 1769 (idx 1768): Strip leading 'nước' [6] -> 'ngập kéo dài' [7, 8, 9]
    1768: [([1, 2, 3], [7, 8, 9], 'NEG')],

    # Rec 1770 (idx 1769): OK
    1769: [([1, 2, 3, 4], [22, 23], 'NEG')],

    # Rec 1771 (idx 1770): OK
    1770: [([1], [19, 20, 21], 'NEG')],

    # Rec 1772 (idx 1771): OK
    1771: [([1], [20, 21], 'NEG')],

    # Rec 1773 (idx 1772): Fix bare noun 'ngập' [8] to predicate 'chưa hết ngập' [21, 22, 23] NEG
    1772: [([1, 2, 3, 4], [21, 22, 23], 'NEG')],

    # Rec 1774 (idx 1773): Strip passive 'bị' [11] -> 'ngập sâu' [12, 13]
    1773: [
        ([2, 3, 4, 5], [12, 13], 'NEG'),
        ([7, 8, 9], [12, 13], 'NEG')
    ],

    # Rec 1775 (idx 1774): Complete 'rút' [11] to 'rút bớt' [11, 12] POS
    1774: [([1], [11, 12], 'POS')],

    # Rec 1776 (idx 1775): OK
    1775: [([1, 2, 3, 4], [12], 'NEG')],

    # Rec 1777 (idx 1776): OK
    1776: [([1], [33, 34, 35], 'NEG')],

    # Rec 1778 (idx 1777): OK
    1777: [
        ([19, 20, 21], [25, 26], 'NEG'),
        ([23, 24], [25, 26], 'NEG')
    ],

    # Rec 1779 (idx 1778): OK
    1778: [([21, 22, 23], [15], 'NEG')],

    # Rec 1780 (idx 1779): OK
    1779: [([1], [25], 'NEG')]
}

print(f'Total updates in batch 50: {len(updates)}')

# Verify each update against tokens
for idx, trip_list in updates.items():
    text = lines[idx].split('####')[0]
    toks = text.split()
    for trip in trip_list:
        asp_idx, opi_idx, pol = trip
        assert all(0 <= i < len(toks) for i in asp_idx), f'Bad asp index in {idx}'
        assert all(0 <= i < len(toks) for i in opi_idx), f'Bad opi index in {idx}'
        assert pol in ['POS', 'NEG', 'NEU'], f'Bad pol in {idx}'

# Apply updates and write back
for idx, trip_list in updates.items():
    text = lines[idx].split('####')[0]
    lines[idx] = f'{text}####{trip_list}'

with open(TARGET_FILE, 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print(f'Successfully updated {len(updates)} records in {TARGET_FILE}!')
