import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

t, tr = lines[999].split('####')
print("Rec 1000:")
print("Text:", t)
print("Triplets:", tr)
for i, tk in enumerate(t.split()):
    print(f"[{i}:{tk}]", end=" ")
print()
