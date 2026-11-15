with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

t, _ = lines[999].split('####')
lines[999] = f"{t}####[([6, 7], [17, 18, 19, 20, 21, 22, 23], 'NEG')]"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')
