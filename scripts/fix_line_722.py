with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

text_722 = lines[721].split('####')[0]
lines[721] = f"{text_722}####[([3, 4, 5, 6], [10, 11], 'NEG'), ([15, 16, 17, 18, 19, 20], [30, 31], 'NEG')]"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print("Line 722 fixed successfully!")
