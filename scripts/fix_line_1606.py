with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

text_1606 = lines[1605].split('####')[0]
lines[1605] = f"{text_1606}####[([28, 29, 30], [12, 13], 'NEG')]"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print("Updated 1606 to đường Đề Thám!")
