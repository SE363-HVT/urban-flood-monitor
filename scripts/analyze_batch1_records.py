import sys, ast
sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [f.readline().strip() for _ in range(100)]

def inspect_range(start, end):
    print(f"=== RECORDS {start} to {end} ===")
    for i in range(start - 1, end):
        parts = lines[i].split('####')
        text = parts[0].strip()
        trips = ast.literal_eval(parts[1].strip())
        tokens = text.split()
        print(f"[{i+1}] {text}")
        if not trips:
            print("    -> REJECT")
        for a, o, p in trips:
            asp = " ".join(tokens[j] for j in a)
            opi = " ".join(tokens[j] for j in o)
            print(f"    -> [{asp}] ({a}) | [{opi}] ({o}) | {p}")

if __name__ == '__main__':
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    inspect_range(start, end)
