import sys

sys.stdout.reconfigure(encoding="utf-8")
with open("data/validate_label/thuan/phase2.txt", "r", encoding="utf-8") as f:
    for i, l in enumerate(f):
        if "ngụ " in l:
            p = l.strip().split("####")
            print(f"Line {i+1}: {p[0][:80]}... #### {p[1] if len(p)>1 else ''}")
