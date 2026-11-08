import sys, ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase1.txt', 'r', encoding='utf-8') as f:
    thuan_lines = [l.strip() for l in f if l.strip()]

with open('data/validate_label/hung/phase1.txt', 'r', encoding='utf-8') as f:
    hung_lines = [l.strip() for l in f if l.strip()]

def get_text_trips(line):
    parts = line.split('####')
    tokens = parts[0].split()
    trips = ast.literal_eval(parts[1])
    return tokens, trips

print(f"Loaded {len(thuan_lines)} lines.")
