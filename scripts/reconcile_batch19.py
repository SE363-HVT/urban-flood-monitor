import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f]

print(f"Total lines before reconcile: {len(lines)}")

# 1. Line 1809 (idx 1808):
# Shorten verbose opinion and remove multi-level duplicate
text_1809 = lines[1808].split('####')[0]
lines[1808] = f"{text_1809}####[([18, 19], [27, 28], 'NEG')]"

# 2. Line 1812 (idx 1811):
# canal kênh Tẻ overflows
text_1812 = lines[1811].split('####')[0]
lines[1811] = f"{text_1812}####[([10, 11], [12, 13, 14, 15], 'NEG')]"

# 3. Line 1819 (idx 1818):
# Add fallback Tại TPHCM , and label TPHCM | ngập
orig_text_1819 = lines[1818].split('####')[0]
if not orig_text_1819.startswith("Tại TPHCM ,"):
    text_1819 = f"Tại TPHCM , {orig_text_1819}"
else:
    text_1819 = orig_text_1819
lines[1818] = f"{text_1819}####[([1], [8], 'NEG')]"

# 4. Line 1824 (idx 1823):
# Shorten verbose opinion
text_1824 = lines[1823].split('####')[0]
lines[1823] = f"{text_1824}####[([12, 13, 14, 15], [16, 17], 'NEG'), ([48, 49], [56, 57], 'NEG')]"

# 5. Line 1826 (idx 1825):
# Clean misplaced fallback prefix on out-of-province line
lines[1825] = "Buôn Ma Thuột hôm nay mưa to quá ngập lụt nước khu vực từ Thiện Hạnh đến km3 # bmt # reviewbuonmathuot # 47daklak # lulut # ngaplut####[]"

# 6. Line 1868 (idx 1867):
# Restore TP. HCM | ngập sâu
text_1868 = lines[1867].split('####')[0]
lines[1867] = f"{text_1868}####[([8, 9], [11, 12], 'NEG')]"

# 7. Line 1878 (idx 1877):
# Shorten verbose opinion
text_1878 = lines[1877].split('####')[0]
lines[1877] = f"{text_1878}####[([5], [6, 7], 'NEG')]"

# 8. Line 1879 (idx 1878):
# Shorten verbose opinion
text_1879 = lines[1878].split('####')[0]
lines[1878] = f"{text_1879}####[([4, 5], [14, 15], 'NEG')]"

# 9. Line 1882 (idx 1881):
# Remove multi-level duplicate Bình Thạnh
text_1882 = lines[1881].split('####')[0]
lines[1881] = f"{text_1882}####[([12, 13], [19], 'NEG')]"

# 10. Line 1897 (idx 1896):
# Shorten verbose opinion
text_1897 = lines[1896].split('####')[0]
lines[1896] = f"{text_1897}####[([3, 4, 5, 6], [31, 32], 'NEG')]"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print(f"Total lines after reconcile: {len(lines)}")
print("Batch 19 reconciled successfully!")
