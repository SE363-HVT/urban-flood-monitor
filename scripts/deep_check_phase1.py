import sys, ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase1.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Total lines: {len(lines)}")

all_asps = {}
causative_found = []
quotes_found = []
unusual_asps = []

for idx, line in enumerate(lines, 1):
    text, trips_str = line.split('####')
    tokens = text.split()
    trips = ast.literal_eval(trips_str)
    for a, o, p in trips:
        a_w = ' '.join([tokens[i] for i in a])
        o_w = ' '.join([tokens[i] for i in o])
        all_asps.setdefault(a_w, []).append(idx)
        
        # Check causative verbs
        if any(o_w.startswith(cv) for cv in ['gây ngập', 'làm ngập', 'gây ra ngập', 'làm tăng nguy cơ']):
            causative_found.append((idx, a_w, o_w))
            
        # Check quotes in opinion
        if any(q in o_w for q in ['"', '”', '“']):
            quotes_found.append((idx, a_w, o_w))

print(f"\n1. Distinct aspect entities: {len(all_asps)}")
# Sort aspects alphabetically to inspect all entities
for a_w in sorted(all_asps.keys()):
    count = len(all_asps[a_w])
    recs = all_asps[a_w]
    # Check if aspect looks like a verb, adjective, or project phrase
    if a_w.startswith('dự án') or a_w.startswith('Dự án') or a_w in ['nước', 'Nước'] or count <= 1:
        print(f"   [{count:2d} times] Aspect: '{a_w}' | Recs: {recs[:5]}")

print(f"\n2. Causative verbs in opinion: {len(causative_found)}")
for c in causative_found:
    print(f"   Rec {c[0]}: Asp='{c[1]}' | Opi='{c[2]}'")

print(f"\n3. Quotes in opinion: {len(quotes_found)}")
for q in quotes_found:
    print(f"   Rec {q[0]}: Asp='{q[1]}' | Opi='{q[2]}'")
