with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.rstrip('\r\n') for line in f]

text = lines[1959].split('####')[0].strip()
lines[1959] = text + "####[]"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print("Rejected line 1960:", lines[1959])
