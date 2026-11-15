import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f]

print(f"Total lines before reconcile: {len(lines)}")

# 1. Line 1917 (idx 1916): Shorten verbose opinion
text_1917 = lines[1916].split('####')[0]
lines[1916] = f"{text_1917}####[([20], [21, 22], 'NEG')]"

# 2. Line 1920 (idx 1919): Shorten verbose opinion
text_1920 = lines[1919].split('####')[0]
lines[1919] = f"{text_1920}####[([13], [14, 15], 'NEG')]"

# 3. Line 1926 (idx 1925): Shorten verbose opinion
text_1926 = lines[1925].split('####')[0]
lines[1925] = f"{text_1926}####[([33], [38, 39], 'NEG')]"

# 4. Line 1927 (idx 1926): Shorten verbose opinion
text_1927 = lines[1926].split('####')[0]
lines[1926] = f"{text_1927}####[([26], [27, 28], 'NEG')]"

# 5. Line 1931 (idx 1930): Shorten verbose opinion
text_1931 = lines[1930].split('####')[0]
lines[1930] = f"{text_1931}####[([12, 13, 14, 15], [16, 17], 'NEG')]"

# 6. Line 1937 (idx 1936): Fix generic aspect to TP. HCM, shorten opinion
text_1937 = lines[1936].split('####')[0]
lines[1936] = f"{text_1937}####[([0, 1], [9, 10], 'NEG')]"

# 7. Line 1940 (idx 1939): Shorten verbose opinion
text_1940 = lines[1939].split('####')[0]
lines[1939] = f"{text_1940}####[([6, 7], [12, 13], 'NEG')]"

# 8. Line 1960 (idx 1959): Transform TPHCM triều cường -> triều cường ở TPHCM đạt đỉnh
lines[1959] = "Hà Nội nắng nóng , triều cường ở TPHCM đạt đỉnh # sggpnews # saigongiaiphong # sggp # dubaothoitiet # thoitiet####[([5, 6, 7, 8], [9, 10], 'NEU')]"

# 9. Line 1978 (idx 1977): Shorten verbose opinion
text_1978 = lines[1977].split('####')[0]
lines[1977] = f"{text_1978}####[([6, 7], [14, 15], 'NEG')]"

# 10. Line 1979 (idx 1978): Remove triều cường from opinion of đường Rạch Cùng
text_1979 = lines[1978].split('####')[0]
lines[1978] = f"{text_1979}####[([24, 25, 26], [19, 20, 21, 22], 'NEG')]"

# 11. Line 1988 (idx 1987): Transform TPHCM triều cường -> triều cường ở TPHCM đạt đỉnh
lines[1987] = "Hà Nội nắng nóng , triều cường ở TPHCM đạt đỉnh # SGGP####[([5, 6, 7, 8], [9, 10], 'NEU')]"

# 12. Line 1990 (idx 1989): Shorten verbose opinion
text_1990 = lines[1989].split('####')[0]
lines[1989] = f"{text_1990}####[([2, 3], [10, 11], 'NEG')]"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print(f"Total lines after reconcile: {len(lines)}")
print("Batch 20 reconciled successfully!")
