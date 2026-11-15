# reconcile_batch_49_50rec.py
# Batch 49: Records 1681 to 1730 (0-based indices 1680 to 1729)

TARGET_FILE = 'data/validate_label/thuan/phase2.txt'

with open(TARGET_FILE, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

assert len(lines) == 2000, f'Expected 2000 lines, got {len(lines)}'

updates = {
    # Rec 1681 (idx 1680): Strip passive 'bị' [49] and trim 39-token monster run-on to 'ngập sâu' [50, 51]
    1680: [([38, 39, 40, 41], [50, 51], 'NEG')],

    # Rec 1682 (idx 1681): Strip passive 'bị' [33] -> 'ngập nặng' [34, 35]
    1681: [
        ([43, 44, 45, 46], [34, 35], 'NEG'),
        ([53, 54, 55], [34, 35], 'NEG'),
        ([57, 58, 59], [34, 35], 'NEG')
    ],

    # Rec 1683 (idx 1682): Trim 14-token run-on to 'ngập sâu' [18, 19]
    1682: [([6, 7, 8, 9], [18, 19], 'NEG')],

    # Rec 1684 (idx 1683): OK
    1683: [
        ([19, 20], [24, 25], 'NEG'),
        ([31, 32, 33], [39, 40], 'NEG'),
        ([35, 36, 37], [39, 40], 'NEG')
    ],

    # Rec 1685 (idx 1684): Trim 16-token run-on to 'ngập như sông' [17, 18, 19]
    1684: [([11, 12], [17, 18, 19], 'NEG')],

    # Rec 1686 (idx 1685): OK
    1685: [([0, 1], [10, 11, 12, 13, 14, 15], 'NEG')],

    # Rec 1687 (idx 1686): OK
    1686: [([39, 40, 41, 42], [50, 51, 52, 53], 'NEG'), ([74, 75, 76], [67, 68, 69], 'NEG')],

    # Rec 1688 (idx 1687): Strip adverb and passive 'bất ngờ bị' -> 'ngập sâu' [45, 46]
    1687: [([34, 35, 36, 37], [45, 46], 'NEG')],

    # Rec 1689 (idx 1688): OK
    1688: [
        ([55, 56, 57, 58], [50, 51], 'NEG'),
        ([60, 61, 62], [50, 51], 'NEG'),
        ([64, 65, 66], [50, 51], 'NEG'),
        ([68, 69, 70], [50, 51], 'NEG')
    ],

    # Rec 1690 (idx 1689): Strip passive 'bị' [76] -> 'ngập nặng' [77, 78]
    1689: [
        ([59, 60, 61, 62], [77, 78], 'NEG'),
        ([64, 65, 66], [77, 78], 'NEG'),
        ([68, 69, 70], [77, 78], 'NEG'),
        ([72, 73, 74], [77, 78], 'NEG')
    ],

    # Rec 1691 (idx 1690): OK
    1690: [([25, 26, 27], [28, 29], 'NEG')],

    # Rec 1692 (idx 1691): OK
    1691: [([12, 13, 14, 15], [10, 11], 'POS')],

    # Rec 1693 (idx 1692): Trim 19-token run-on to 'thường xuyên ngập' [12, 13, 14]
    1692: [([8, 9, 10, 11], [12, 13, 14], 'NEG')],

    # Rec 1694 (idx 1693): OK
    1693: [([12, 13, 14, 15], [21, 22, 23], 'NEU')],

    # Rec 1695 (idx 1694): OK
    1694: [([1], [17, 18], 'POS')],

    # Rec 1696 (idx 1695): FIX GARBAGE ASPECT 'ngụ phường Tân' -> 'phường Tân Thuận' [6, 7, 8], opinion 'tràn vào nhà' [25, 26, 27]
    1695: [([6, 7, 8], [25, 26, 27], 'NEG')],

    # Rec 1697 (idx 1696): Fix 'ngập' -> 'ngập đã giảm' [17, 18, 19], POS
    1696: [([1, 2, 3, 4], [17, 18, 19], 'POS')],

    # Rec 1698 (idx 1697): OK
    1697: [([16, 17, 18], [34, 35, 36, 37], 'NEG')],

    # Rec 1699 (idx 1698): OK
    1698: [([10, 11, 12, 13], [15, 16, 17, 18, 19], 'NEG')],

    # Rec 1700 (idx 1699): OK
    1699: [([1], [18], 'NEG')],

    # Rec 1701 (idx 1700): OK
    1700: [([1], [18, 19], 'POS')],

    # Rec 1702 (idx 1701): OK
    1701: [([1, 2, 3, 4], [8, 9], 'POS')],

    # Rec 1703 (idx 1702): OK
    1702: [([1], [5, 6], 'POS')],

    # Rec 1704 (idx 1703): FIX POLARITY FLIP & TRUNCATION: 'giảm ngập' [29, 30] POS on TPHCM [41]
    1703: [([41], [29, 30], 'POS')],

    # Rec 1705 (idx 1704): OK
    1704: [([1], [14, 15, 16], 'NEG')],

    # Rec 1706 (idx 1705): Trim 10-token run-on to 'ngập sâu' [24, 25]
    1705: [([8, 9, 10, 11], [24, 25], 'NEG'), ([13, 14, 15], [24, 25], 'NEG')],

    # Rec 1707 (idx 1706): OK
    1706: [([1, 2, 3, 4], [9, 10], 'NEG')],

    # Rec 1708 (idx 1707): OK
    1707: [([16, 17, 18, 19], [26, 27], 'NEG')],

    # Rec 1709 (idx 1708): OK
    1708: [([1], [12, 13], 'NEG')],

    # Rec 1710 (idx 1709): FIX CHỜ NƯỚC RÚT TRAP: 'chờ nước rút' [22, 23, 24] NEG
    1709: [([1], [22, 23, 24], 'NEG')],

    # Rec 1711 (idx 1710): OK
    1710: [([5, 6, 7, 8], [9, 10], 'NEG')],

    # Rec 1712 (idx 1711): OK
    1711: [([1, 2, 3, 4], [22, 23], 'NEG')],

    # Rec 1713 (idx 1712): OK
    1712: [([1, 2, 3, 4], [30, 31], 'NEG')],

    # Rec 1714 (idx 1713): FIX CHỜ NƯỚC RÚT TRAP: 'chờ nước rút' [18, 19, 20] NEG
    1713: [([1], [18, 19, 20], 'NEG')],

    # Rec 1715 (idx 1714): OK
    1714: [([1], [16, 17], 'NEG')],

    # Rec 1716 (idx 1715): Trim 16-token run-on to 'ngập nước' [20, 21], conditional warning is NEU
    1715: [([1, 2, 3, 4], [20, 21], 'NEU')],

    # Rec 1717 (idx 1716): OK
    1716: [([12, 13], [20, 21], 'POS')],

    # Rec 1718 (idx 1717): OK
    1717: [([23, 24], [6, 7], 'NEG')],

    # Rec 1719 (idx 1718): OK
    1718: [([1], [12, 13], 'POS')],

    # Rec 1720 (idx 1719): OK
    1719: [([1, 2, 3, 4], [24, 25], 'POS')],

    # Rec 1721 (idx 1720): OK
    1720: [([8, 9], [4, 5], 'POS')],

    # Rec 1722 (idx 1721): OK
    1721: [([1, 2, 3, 4], [11, 12], 'POS')],

    # Rec 1723 (idx 1722): FIX NEGATION DROP: 'không ngập' [33, 34] POS
    1722: [([1, 2, 3, 4], [33, 34], 'POS')],

    # Rec 1724 (idx 1723): FIX NEGATION DROP: 'không xảy ra tình trạng ngập' [35, 36, 37, 38, 39, 40] POS
    1723: [([1, 2, 3, 4], [35, 36, 37, 38, 39, 40], 'POS')],

    # Rec 1725 (idx 1724): OK
    1724: [([1], [20], 'NEG')],

    # Rec 1726 (idx 1725): OK
    1725: [([11, 12], [33], 'NEG')],

    # Rec 1727 (idx 1726): OK
    1726: [([1, 2, 3, 4], [18, 19], 'POS')],

    # Rec 1728 (idx 1727): OK
    1727: [([1, 2, 3, 4], [17, 18], 'POS')],

    # Rec 1729 (idx 1728): FIX POLARITY FLIP & TRUNCATION: 'giảm ngập' [39, 40] POS
    1728: [([1], [39, 40], 'POS')],

    # Rec 1730 (idx 1729): Fix truncated opinion to 'ngập lũ' [8, 9] NEG
    1729: [([1, 2, 3, 4], [8, 9], 'NEG')]
}

print(f'Total updates in batch 49: {len(updates)}')

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
