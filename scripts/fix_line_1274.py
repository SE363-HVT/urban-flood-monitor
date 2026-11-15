with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

text_1274 = lines[1273].split('####')[0]
lines[1273] = f"{text_1274}####[([86, 87, 88, 89], [109, 110], 'NEG'), ([91, 92, 93], [109, 110], 'NEG'), ([95, 96], [109, 110], 'NEG'), ([98, 99, 100], [109, 110], 'NEG'), ([102, 103, 104], [109, 110], 'NEG'), ([106, 107], [109, 110], 'NEG')]"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print("Line 1274 fixed successfully!")
