import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("data/validate_label/thuan/phase2.txt", "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f]

idx = int(sys.argv[1]) if len(sys.argv) > 1 else 1042
text = lines[idx].split("####")[0]
toks = text.split()
for i, t in enumerate(toks):
    print(f"{i}:{t}", end=" ")
print()
