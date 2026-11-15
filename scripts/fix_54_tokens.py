import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.rstrip('\r\n') for line in f]

# Rec 1953 (idx 1952)
text_1953 = lines[1952].split('####')[0].strip()
tokens_1953 = text_1953.split()
lines[1952] = f"{text_1953}####[([21, 22], [26, 27, 28, 29], 'NEG')]"

# Rec 1956 (idx 1955)
text_1956 = lines[1955].split('####')[0].strip()
tokens_1956 = text_1956.split()
lines[1955] = f"{text_1956}####[([20, 21], [22, 23], 'NEG'), ([35, 36, 37, 38], [39, 40, 41, 42], 'NEG')]"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print("Rec 1953 Asp:", [tokens_1953[x] for x in [21, 22]], "Op:", [tokens_1953[x] for x in [26, 27, 28, 29]])
print("Rec 1956 Asp1:", [tokens_1956[x] for x in [20, 21]], "Op1:", [tokens_1956[x] for x in [22, 23]])
print("Rec 1956 Asp2:", [tokens_1956[x] for x in [35, 36, 37, 38]], "Op2:", [tokens_1956[x] for x in [39, 40, 41, 42]])
