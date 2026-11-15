import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

for r in [1234, 1277]:
    t, tr = lines[r - 1].split('####')
    toks = t.split()
    print(f"Rec {r}:")
    for i, tk in enumerate(toks):
        print(f"[{i}:{tk}]", end=" ")
    print("\n")
