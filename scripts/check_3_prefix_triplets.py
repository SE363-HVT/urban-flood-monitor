import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

for r in [375, 393, 513]:
    idx = r - 1
    text, trip = lines[idx].split('####')
    print(f"Rec {r}:")
    print(f"  TEXT: {text}")
    print(f"  TRIP: {trip}\n")
