with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

# Line 1084 (idx 1083)
text_1084 = lines[1083].split('####')[0]
lines[1083] = f"{text_1084}####[([3, 4, 5, 6], [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], 'NEG'), ([8, 9, 10], [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], 'NEG')]"

# Line 1089 (idx 1088)
text_1089 = lines[1088].split('####')[0]
lines[1088] = f"{text_1089}####[([2, 3, 4], [38, 39, 40, 41], 'NEG'), ([6, 7, 8], [38, 39, 40, 41], 'NEG'), ([10, 11], [38, 39, 40, 41], 'NEG'), ([13, 14, 15], [38, 39, 40, 41], 'NEG'), ([21, 22, 23], [38, 39, 40, 41], 'NEG'), ([25, 26, 27], [38, 39, 40, 41], 'NEG'), ([29, 30, 31], [38, 39, 40, 41], 'NEG'), ([33, 34, 35], [38, 39, 40, 41], 'NEG')]"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print("Lines 1084 and 1089 fixed successfully!")
