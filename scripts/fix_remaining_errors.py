import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f]

# Line 456 (idx 455): Remove invalid aspect [nước]
text_456 = lines[455].split('####')[0]
lines[455] = f"{text_456}####[([11, 12, 13], [8, 9, 10], 'NEG')]"

# Line 463 (idx 462): No geo aspect, reject
text_463 = lines[462].split('####')[0]
lines[462] = f"{text_463}####[]"

# Line 590 (idx 589): Remove invalid aspect [nước]
text_590 = lines[589].split('####')[0]
# keep TP. Hồ Chí Minh | ngập hơn 0 , 5m
lines[589] = f"{text_590}####[([1, 2, 3, 4], [10, 11, 12, 13, 14], 'NEG')]"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print("Fixed lines 456, 463, 590!")
