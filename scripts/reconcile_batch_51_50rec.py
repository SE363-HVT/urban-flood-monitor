# reconcile_batch_51_50rec.py
# Batch 51: Records 1781 to 1830 (0-based indices 1780 to 1829)

TARGET_FILE = 'data/validate_label/thuan/phase2.txt'

with open(TARGET_FILE, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

assert len(lines) == 2000, f'Expected 2000 lines, got {len(lines)}'

updates = {
    # Rec 1781 (idx 1780): OK
    1780: [([6, 7, 8, 9], [15], 'NEG')],

    # Rec 1782 (idx 1781): OK
    1781: [([9, 10, 11, 12], [32, 33], 'NEG')],

    # Rec 1783 (idx 1782): OK
    1782: [([1, 2, 3, 4], [21, 22], 'NEG')],

    # Rec 1784 (idx 1783): OK
    1783: [([49, 50, 51], [43], 'NEG')],

    # Rec 1785 (idx 1784): OK
    1784: [([28, 29, 30], [19], 'NEG')],

    # Rec 1786 (idx 1785): OK
    1785: [
        ([4, 5, 6], [23, 24], 'NEG'),
        ([8, 9, 10], [23, 24], 'NEG'),
        ([12, 13, 14], [23, 24], 'NEG'),
        ([16, 17, 18], [23, 24], 'NEG'),
        ([20, 21, 22], [23, 24], 'NEG')
    ],

    # Rec 1787 (idx 1786): OK
    1786: [([1, 2, 3, 4], [13, 14], 'NEG')],

    # Rec 1788 (idx 1787): OK
    1787: [([1, 2, 3, 4], [8], 'NEG')],

    # Rec 1789 (idx 1788): OK
    1788: [([2, 3, 4], [21, 22, 23], 'NEG')],

    # Rec 1790 (idx 1789): OK
    1789: [([1], [42], 'NEG')],

    # Rec 1791 (idx 1790): OK
    1790: [([17, 18, 19], [12, 13], 'POS')],

    # Rec 1792 (idx 1791): OK
    1791: [([1], [10, 11], 'POS')],

    # Rec 1793 (idx 1792): OK
    1792: [([8, 9], [1, 2], 'POS')],

    # Rec 1794 (idx 1793): FIX POLARITY FLIP: 'xử lý căn cơ tình trạng ngập' [44, 45, 46, 47, 48, 49, 50] POS
    1793: [([8, 9], [44, 45, 46, 47, 48, 49, 50], 'POS')],

    # Rec 1795 (idx 1794): OK
    1794: [([20, 21, 22], [31, 32], 'NEG')],

    # Rec 1796 (idx 1795): Strip leading 'nước' [22] -> 'ngập cao hơn bánh xe máy' [23, 24, 25, 26, 27, 28]
    1795: [
        ([10, 11, 12, 13, 14, 15, 16], [23, 24, 25, 26, 27, 28], 'NEG'),
        ([18, 19, 20], [23, 24, 25, 26, 27, 28], 'NEG')
    ],

    # Rec 1797 (idx 1796): OK
    1796: [([1, 2, 3, 4], [11, 12], 'NEG')],

    # Rec 1798 (idx 1797): FIX CHỜ NƯỚC RÚT TRAP: 'chờ nước rút' [25, 26, 27] NEG
    1797: [([1], [25, 26, 27], 'NEG')],

    # Rec 1799 (idx 1798): OK
    1798: [([5, 6, 7], [12, 13], 'NEG')],

    # Rec 1800 (idx 1799): OK
    1799: [([13, 14, 15], [21, 22], 'NEG')],

    # Rec 1801 (idx 1800): OK
    1800: [([0, 1, 2, 3], [5, 6], 'NEG')],

    # Rec 1802 (idx 1801): Complete opinion to 'ngập gần nửa bánh xe máy' [9, 10, 11, 12, 13, 14] NEG
    1801: [([1, 2, 3, 4], [9, 10, 11, 12, 13, 14], 'NEG')],

    # Rec 1803 (idx 1802): OK
    1802: [
        ([4, 5, 6], [20, 21, 22, 23], 'NEG'),
        ([32, 33, 34, 35], [20, 21, 22, 23], 'NEG')
    ],

    # Rec 1804 (idx 1803): OK
    1803: [([1], [28, 29, 30], 'NEG')],

    # Rec 1805 (idx 1804): Split comma run-on to 'ngập sâu' [12, 13] and 'tràn vào nhà' [15, 16, 17]
    1804: [([1, 2, 3, 4], [12, 13], 'NEG'), ([1, 2, 3, 4], [15, 16, 17], 'NEG')],

    # Rec 1806 (idx 1805): OK
    1805: [([1, 2, 3, 4], [28, 29], 'POS')],

    # Rec 1807 (idx 1806): OK
    1806: [([1, 2, 3, 4], [24], 'NEG')],

    # Rec 1808 (idx 1807): OK
    1807: [([8, 9, 10], [11, 12, 13], 'POS')],

    # Rec 1809 (idx 1808): Trim 18-token run-on to 'ngập nặng' [27, 28]
    1808: [([18, 19], [27, 28], 'NEG')],

    # Rec 1810 (idx 1809): OK
    1809: [([21, 22, 23, 24], [26, 27], 'NEG')],

    # Rec 1811 (idx 1810): OK
    1810: [([10, 11], [7], 'NEG')],

    # Rec 1812 (idx 1811): OK
    1811: [([10, 11], [12, 13, 14, 15], 'NEG')],

    # Rec 1813 (idx 1812): OK
    1812: [([26, 27, 28, 29], [20], 'NEG')],

    # Rec 1814 (idx 1813): OK
    1813: [([15, 16, 17, 18], [12, 13], 'POS')],

    # Rec 1815 (idx 1814): FIX POLARITY FLIP: 'giảm đáng kể tình trạng ngập cục bộ' [17, 18, 19, 20, 21, 22, 23, 24] POS
    1814: [([1, 2, 3, 4], [17, 18, 19, 20, 21, 22, 23, 24], 'POS')],

    # Rec 1816 (idx 1815): FIX POLARITY FLIP: 'giải quyết triệt để ngập' [5, 6, 7, 8] POS
    1815: [([35, 36], [5, 6, 7, 8], 'POS')],

    # Rec 1817 (idx 1816): Strip leading 'nước' [21] -> 'ngập' [22] NEG
    1816: [([15, 16, 17, 18], [22], 'NEG')],

    # Rec 1818 (idx 1817): Conditional prediction 'có thể... ngập úng' -> NEU
    1817: [([25, 26, 27, 28], [29, 30], 'NEU')],

    # Rec 1819 (idx 1818): Complete opinion to 'ngập như sông' [8, 9, 10] NEG
    1818: [([1], [8, 9, 10], 'NEG')],

    # Rec 1820 (idx 1819): REJECT - personal ramblings, #hanoimua
    1819: [],

    # Rec 1821 (idx 1820): OK
    1820: [([2, 3, 4], [0], 'NEG')],

    # Rec 1822 (idx 1821): REJECT - Đồng Tháp (outside TP.HCM)
    1821: [],

    # Rec 1823 (idx 1822): OK
    1822: [
        ([3, 4, 5], [0, 1], 'NEG'),
        ([6, 7, 8, 9], [0, 1], 'NEG')
    ],

    # Rec 1824 (idx 1823): Remove out-of-scope Bình Dương [48, 49], trim 26-token run-on to 'ngập sâu' [16, 17]
    1823: [([12, 13, 14, 15], [16, 17], 'NEG')],

    # Rec 1825 (idx 1824): OK
    1824: [([1, 2, 3, 4], [18, 19], 'NEG')],

    # Rec 1826 (idx 1825): REJECT - Buôn Ma Thuột (outside TP.HCM)
    1825: [],

    # Rec 1827 (idx 1826): OK
    1826: [([17, 18], [14, 15], 'NEG')],

    # Rec 1828 (idx 1827): REJECT - Commercial product advertisement (vách ngăn chống ngập, tư vấn đo cửa)
    1827: [],

    # Rec 1829 (idx 1828): REJECT - Cà Mau (#povcamau #nuocngapcamau) (PASS 7)
    1828: [],

    # Rec 1830 (idx 1829): REJECT - Đường Bào, Phú Quốc, Kiên Giang (#phuquoc) (PASS 7)
    1829: []
}

print(f'Total updates in batch 51: {len(updates)}')

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
