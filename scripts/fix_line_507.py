with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

text_507 = lines[506].split('####')[0]
lines[506] = f"{text_507}####[([4, 5, 6, 7], [8, 9], 'NEU'), ([24], [25, 26], 'NEG')]"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print("Line 507 fixed successfully!")
