with open('data/validate_label/thuan/phase2_test.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

t, _ = lines[787].split('####')
lines[787] = f"{t}####[([4, 5, 6], [39, 40], 'NEG')]"

with open('data/validate_label/thuan/phase2_test.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')
