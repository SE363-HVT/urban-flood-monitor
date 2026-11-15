with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

# Line 1606 (idx 1605): aspect is TP. HCM [10, 11], not trung tâm [8, 9]
text_1606 = lines[1605].split('####')[0]
lines[1605] = f"{text_1606}####[([10, 11], [12, 13], 'NEG')]"

# Line 1657 (idx 1656): aspect is TPHCM [6], not ở [5]
text_1657 = lines[1656].split('####')[0]
lines[1656] = f"{text_1657}####[([6], [10, 11, 12, 13, 14, 15, 16], 'NEG')]"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print("Lines 1606 and 1657 fixed successfully!")
