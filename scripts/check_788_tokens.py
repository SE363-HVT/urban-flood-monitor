import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/validate_label/thuan/phase2_test.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

t, tr = lines[787].split('####')
print("Line 788:")
toks = t.split()
for i, tk in enumerate(toks):
    print(f"{i}: {tk}")
