import sys
import ast

sys.stdout.reconfigure(encoding="utf-8")

with open("data/validate_label/thuan/phase2.txt", "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f]

start = int(sys.argv[1]) if len(sys.argv) > 1 else 1330
end = int(sys.argv[2]) if len(sys.argv) > 2 else 1380

for idx in range(start, end):
    parts = lines[idx].split("####")
    text = parts[0].strip()
    triplets = ast.literal_eval(parts[1]) if len(parts) > 1 else []
    toks = text.split()
    print(f"=== REC {idx+1} (idx {idx}) ===")
    print(" ".join(f"[{i}:{w}]" for i, w in enumerate(toks)))
    print("CURRENT:", triplets)
    for asp, opi, pol in triplets:
        asp_str = " ".join(toks[k] for k in asp)
        opi_str = " ".join(toks[k] for k in opi)
        print(f"   Asp: '{asp_str}' {asp} | Opi: '{opi_str}' {opi} | Pol: {pol}")
