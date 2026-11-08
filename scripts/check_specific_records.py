import sys, ast

sys.stdout.reconfigure(encoding='utf-8')
with open('data/validate_label/thuan/phase1.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

for r in [122, 123, 138, 227, 457, 471]:
    line = lines[r-1]
    text, trips_str = line.split('####')
    tokens = text.split()
    trips = ast.literal_eval(trips_str)
    print(f"\n=== Rec {r} ===")
    print("TEXT:", text)
    for a, o, p in trips:
        a_str = " ".join([tokens[i] for i in a])
        o_str = " ".join([tokens[i] for i in o])
        print(f"  Aspect: '{a_str}' {a} | Opinion: '{o_str}' {o} | {p}")
