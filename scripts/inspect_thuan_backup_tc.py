import sys, ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase1.txt.backup_before_audit', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

tc_records = []
for idx, line in enumerate(lines, 1):
    text, trips_str = line.split('####')
    toks = text.split()
    trips = ast.literal_eval(trips_str)
    for a, o, p in trips:
        asp_words = ' '.join([toks[i] for i in a]).lower()
        if 'triều' in asp_words:
            tc_records.append((idx, asp_words, a, o, p, text, trips))
            break

print(f'Total records with "triều" in aspect in Thuan backup: {len(tc_records)}')
for r, asp_w, a, o, p, text, trips in tc_records:
    print(f'Rec {r}: asp="{asp_w}" | trips={trips} | text="{text[:70]}..."')
