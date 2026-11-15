# reconcile_batch_52_50rec.py
# Batch 52: Records 1831 to 1880 (0-based indices 1830 to 1879)

TARGET_FILE = 'data/validate_label/thuan/phase2.txt'

with open(TARGET_FILE, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

assert len(lines) == 2000, f'Expected 2000 lines, got {len(lines)}'

updates = {
    # Rec 1831 (idx 1830): OK
    1830: [([1, 2, 3, 4], [10], 'NEG')],

    # Rec 1832 (idx 1831): OK
    1831: [([1, 2, 3, 4], [6, 7], 'NEG')],

    # Rec 1833 (idx 1832): REJECT - Nha Trang (outside TP.HCM)
    1832: [],

    # Rec 1834 (idx 1833): REJECT - Meme / humor clip ('Cách qua chỗ ngập nước nhanh nhất 😂')
    1833: [],

    # Rec 1835 (idx 1834): REJECT - Cần Thơ (outside TP.HCM)
    1834: [],

    # Rec 1836 (idx 1835): REJECT - Agricultural sticky rice farming in Mekong Delta ('100 công nếp #duylamnong')
    1835: [],

    # Rec 1837 (idx 1836): REJECT - Commercial product ad for Kawasan WA01 flood sensor
    1836: [],

    # Rec 1838 (idx 1837): REJECT - Đồng Tháp (outside TP.HCM)
    1837: [],

    # Rec 1839 (idx 1838): REJECT - ĐBSCL (outside TP.HCM)
    1838: [],

    # Rec 1840 (idx 1839): OK
    1839: [([1], [6], 'NEG')],

    # Rec 1841 (idx 1840): OK
    1840: [([1], [4], 'NEG')],

    # Rec 1842 (idx 1841): OK
    1841: [([10, 11], [3, 4], 'POS')],

    # Rec 1843 (idx 1842): REJECT - Commercial installation ad for flood barriers ('vách chống ngập bảo hành 36 tháng')
    1842: [],

    # Rec 1844 (idx 1843): REJECT - Tân Uyên, Bình Dương (#tanuyenbinhduong) (PASS 7)
    1843: [],

    # Rec 1845 (idx 1844): OK
    1844: [([0, 1, 2], [3, 4], 'NEG')],

    # Rec 1846 (idx 1845): OK
    1845: [([0, 1], [4], 'NEG')],

    # Rec 1847 (idx 1846): OK
    1846: [([1, 2, 3, 4], [10], 'NEG')],

    # Rec 1848 (idx 1847): Rhetorical question 'Đây là ở đâu mà ngập vậy ạ ?' -> NEU
    1847: [([1, 2, 3, 4], [11], 'NEU')],

    # Rec 1849 (idx 1848): OK
    1848: [([2, 3], [11, 12], 'POS')],

    # Rec 1850 (idx 1849): REJECT - Real estate marketing (#bds #bdsbinhthanh)
    1849: [],

    # Rec 1851 (idx 1850): OK
    1850: [([7, 8], [6], 'NEG')],

    # Rec 1852 (idx 1851): OK
    1851: [([0, 1], [2, 3], 'NEG')],

    # Rec 1853 (idx 1852): OK
    1852: [
        ([2, 3, 4, 5], [22, 23, 24, 25], 'NEG'),
        ([9, 10], [22, 23, 24, 25], 'NEG'),
        ([12, 13], [22, 23, 24, 25], 'NEG')
    ],

    # Rec 1854 (idx 1853): OK
    1853: [([7, 8], [0, 1], 'NEG')],

    # Rec 1855 (idx 1854): FIX POLARITY FLIP & ASPECTS: 'Q1' [25, 26] and 'Q4' [28, 29] with 'ko còn ngập' [31, 32, 33, 34] POS
    1854: [
        ([25, 26], [31, 32, 33, 34], 'POS'),
        ([28, 29], [31, 32, 33, 34], 'POS')
    ],

    # Rec 1856 (idx 1855): OK
    1855: [
        ([7, 8], [15, 16], 'NEG'),
        ([10, 11, 12], [15, 16], 'NEG')
    ],

    # Rec 1857 (idx 1856): OK
    1856: [([4, 5], [6, 7], 'NEG')],

    # Rec 1858 (idx 1857): OK
    1857: [([1, 2, 3, 4], [128, 129], 'NEG')],

    # Rec 1859 (idx 1858): REJECT - Long Hải (BR-VT) with hashtag #ngập tagged as opinion
    1858: [],

    # Rec 1860 (idx 1859): OK
    1859: [([4, 5], [6, 7, 8, 9], 'NEG')],

    # Rec 1861 (idx 1860): OK
    1860: [([13, 14, 15, 16], [18, 19], 'POS')],

    # Rec 1862 (idx 1861): OK
    1861: [([3, 4], [5, 6, 7, 8], 'NEG')],

    # Rec 1863 (idx 1862): Complete opinion to 'ngập hơn nửa bánh xe' [12, 13, 14, 15, 16] NEG
    1862: [([1, 2, 3, 4], [12, 13, 14, 15, 16], 'NEG')],

    # Rec 1864 (idx 1863): OK
    1863: [([1], [20, 21], 'NEG')],

    # Rec 1865 (idx 1864): OK
    1864: [([15, 16, 17], [9], 'NEG')],

    # Rec 1866 (idx 1865): OK
    1865: [([0, 1, 2, 3, 4], [11], 'NEG')],

    # Rec 1867 (idx 1866): OK
    1866: [
        ([15, 16], [27, 28], 'NEG'),
        ([18, 19], [27, 28], 'NEG'),
        ([21, 22], [27, 28], 'NEG')
    ],

    # Rec 1868 (idx 1867): OK
    1867: [([8, 9], [11, 12], 'NEG')],

    # Rec 1869 (idx 1868): Prediction of risk 'nguy cơ ngập' [27, 28, 29] -> NEU
    1868: [([11, 12, 13, 14], [27, 28, 29], 'NEU')],

    # Rec 1870 (idx 1869): OK
    1869: [([6, 7, 8, 9, 10, 11], [12, 13], 'NEG')],

    # Rec 1871 (idx 1870): OK
    1870: [([13, 14, 15, 16], [96, 97], 'NEU')],

    # Rec 1872 (idx 1871): OK
    1871: [([26, 27, 28, 29], [65], 'NEG')],

    # Rec 1873 (idx 1872): OK
    1872: [([17, 18, 19, 20, 21, 22, 23], [12, 13, 14, 15], 'NEG')],

    # Rec 1874 (idx 1873): Complete alleviation opinion to 'hạn chế ngập cục bộ' [17, 18, 19, 20, 21] POS
    1873: [([2, 3, 4], [17, 18, 19, 20, 21], 'POS')],

    # Rec 1875 (idx 1874): Strip passive 'bị' [30] -> 'ngập' [31] NEG
    1874: [([24, 25, 26], [31], 'NEG')],

    # Rec 1876 (idx 1875): OK
    1875: [
        ([3, 4, 5, 6], [11, 12], 'NEG'),
        ([8, 9, 10], [11, 12], 'NEG')
    ],

    # Rec 1877 (idx 1876): OK
    1876: [([10, 11], [12, 13], 'NEG')],

    # Rec 1878 (idx 1877): Trim 32-token monster run-on to 'ngập sâu' [6, 7] NEG
    1877: [([5], [6, 7], 'NEG')],

    # Rec 1879 (idx 1878): Trim 18-token run-on to 'ngập nặng' [14, 15] NEG
    1878: [([4, 5], [14, 15], 'NEG')],

    # Rec 1880 (idx 1879): Trim comma relief clause -> 'ngập quá' [45, 46] NEG
    1879: [([42, 43, 44], [45, 46], 'NEG')]
}

print(f'Total updates in batch 52: {len(updates)}')

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
