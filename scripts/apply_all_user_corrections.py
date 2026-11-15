import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

fixes = {
    1227: [([15, 16, 17, 18], [10, 11], 'NEG')],
    1236: [([3, 4, 5, 6], [7, 8], 'NEG')],
    1321: [([0, 1, 2, 3], [4, 5, 6, 7], 'NEG')],
    1884: [([40, 41, 42, 43], [58, 59, 60, 61, 62, 63, 64], 'NEU'), ([44, 45, 46], [58, 59, 60, 61, 62, 63, 64], 'NEU')],
    1892: [([15, 16, 17, 18], [31, 32, 33, 34], 'NEG')],
    1921: [([3, 4, 5, 6], [1, 2], 'NEU'), ([9, 10, 11], [1, 2], 'NEU')],
    1947: [([0, 1], [2, 3, 4, 5], 'NEU'), ([11, 12, 13, 14], [2, 3, 4, 5], 'NEU')],
    1953: [([0, 1], [2, 3, 4], 'NEG')],
    1954: [([6, 7, 8], [18, 19, 20, 21, 22, 23, 24], 'NEG')],
    1959: [([5, 6, 7, 8], [9, 10], 'NEU')],
    1981: [([2, 3, 4, 5], [15, 16, 17], 'NEG')],
    1985: [([10, 11, 12, 13], [5, 6, 7, 8], 'NEG')],
    1987: [([5, 6, 7, 8], [9, 10], 'NEU')]
}

for idx, trips in fixes.items():
    text = lines[idx].split('####')[0].strip()
    lines[idx] = f"{text}####{trips}"

with open(filepath, 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print(f"Applied fixes successfully to {len(fixes)} records!")
