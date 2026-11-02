import sys
import ast
import re

sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\SE363_RAWDATA\data\validate_label\thuan\phase1.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f]

print(f'Total lines in phase1.txt: {len(lines)}')

locative_preps = {'ở', 'tại', 'trên', 'dưới', 'trong', 'ngoài', 'từ', 'đến', 'gần', 'cạnh', 'bên', 'phía', 'thuộc', 'của'}
vehicles = {'xe', 'xe máy', 'ô tô', 'xe buýt', 'xe tải', 'thuyền', 'ghe', 'ca nô', 'xe gắn máy', 'phương tiện', 'ô-tô', 'xe-máy'}
standalone_puncts = {'.', ',', ';', ':', '!', '?', '…', '...', '”', '\"', '\'', '(', ')', '[', ']', '-', '–', '|'}

flaws = []
pos_cases = []
neu_cases = []

for idx, line in enumerate(lines):
    rec_num = idx + 1
    if '####' not in line:
        flaws.append((rec_num, 'NO_TRIPLETS_SEPARATOR', line))
        continue
    text, trip_str = line.split('####')
    tokens = text.split()
    triplets = ast.literal_eval(trip_str)
    
    if not triplets:
        continue
        
    for t_idx, (asp, opi, pol) in enumerate(triplets):
        asp_words = [tokens[i] for i in asp]
        opi_words = [tokens[i] for i in opi]
        asp_str = ' '.join(asp_words)
        opi_str = ' '.join(opi_words)

        if pol == 'POS':
            pos_cases.append((rec_num, asp_str, opi_str, text))
        elif pol == 'NEU':
            neu_cases.append((rec_num, asp_str, opi_str, text))

        # Check for potential errors in POS
        if pol == 'POS' and not any(kw in opi_str.lower() for kw in ['rút', 'khô', 'thông', 'chống', 'giải quyết', 'nạo vét', 'thoát', 'hiệu quả', 'cải thiện']):
            flaws.append((rec_num, f'SUSPICIOUS_POS: opi="{opi_str}"', line))

        # Check for potential errors in NEU
        if pol == 'NEU' and any(kw in opi_str.lower() for kw in ['ngập sâu', 'ngập nặng', 'chết máy', 'chìm sâu', 'tê liệt']):
            flaws.append((rec_num, f'SUSPICIOUS_NEU (looks like active severe flood): opi="{opi_str}"', line))

print(f'\n--- STATS ---')
print(f'Total POS samples: {len(pos_cases)}')
for r, a, o, txt in pos_cases:
    print(f'  Line {r} [POS]: Aspect="{a}" | Opinion="{o}"')

print(f'\nTotal NEU samples: {len(neu_cases)}')
print(f'Potential semantic flaws: {len(flaws)}')
for r, msg, ln in flaws:
    print(f'  Line {r}: {msg}')
