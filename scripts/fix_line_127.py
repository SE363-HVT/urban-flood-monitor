with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

text = lines[126].split('####')[0]
lines[126] = f"{text}####[([14, 15, 16, 17], [11, 12], 'NEG'), ([19, 20], [11, 12], 'NEG')]"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')
print('Fixed Line 127 successfully!')
