import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.rstrip('\r\n') for line in f]

text = lines[1905].split('####')[0].strip()
tokens = text.split()
lines[1905] = text + "####[([9, 10, 11], [12], 'NEG')]"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print("Fixed Rec 1906:", lines[1905])
print("Asp:", [tokens[x] for x in [9, 10, 11]], "Op:", [tokens[x] for x in [12]])
