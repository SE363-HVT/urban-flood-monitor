import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

# 1. Rec 16: Aspect [7, 8] ("Thủ Đức"), Opinion [0, 1, 2, 3, 4] ("Cập nhật tình hình ngập")
t16, _ = lines[15].split('####')
toks16 = t16.split()
a16_txt = " ".join(toks16[i] for i in [7, 8])
o16_txt = " ".join(toks16[i] for i in [0, 1, 2, 3, 4])
print(f"Rec 16: Aspect='{a16_txt}' | Opinion='{o16_txt}'")
lines[15] = f"{t16}####[([7, 8], [0, 1, 2, 3, 4], 'NEU')]"

# 2. Rec 43: Aspect [7, 8] ("TP. HCM"), Opinion [0, 1] ("Ngập nước")
t43, _ = lines[42].split('####')
toks43 = t43.split()
a43_txt = " ".join(toks43[i] for i in [7, 8])
o43_txt = " ".join(toks43[i] for i in [0, 1])
print(f"Rec 43: Aspect='{a43_txt}' | Opinion='{o43_txt}'")
lines[42] = f"{t43}####[([7, 8], [0, 1], 'NEU')]"

with open(filepath, 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print("Successfully updated Rec 16 and Rec 43!")
