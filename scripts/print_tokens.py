import sys

sys.stdout.reconfigure(encoding='utf-8')
lines = open('data/validate_label/thuan/phase3.txt', encoding='utf-8').readlines()

for r in [154, 157, 164, 178]:
    text = lines[r-1].split('####')[0].strip()
    tokens = text.split()
    print(f'=== REC {r} ===')
    for i, tok in enumerate(tokens):
        print(f'{i}:{tok}', end=' ')
    print('\n')
