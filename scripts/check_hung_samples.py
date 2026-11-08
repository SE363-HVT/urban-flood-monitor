import sys, ast
sys.stdout.reconfigure(encoding='utf-8')
from scripts.generate_audited_phase1 import thuan_lines, hung_lines

sample_recs = [52, 54, 70, 160, 163, 214, 281, 282, 284, 305, 327, 356, 359, 360, 377, 379, 411, 416, 417, 425]
for r in sample_recs:
    h_text, h_trips_str = hung_lines[r-1].split('####')
    h_toks = h_text.split()
    h_trips = ast.literal_eval(h_trips_str)
    print(f'Rec {r}:')
    print(f'  Hung text:  {h_text[:80]}...')
    print(f'  Hung trips: {h_trips}')
    for a, o, p in h_trips:
        a_str = " ".join([h_toks[j] for j in a])
        o_str = " ".join([h_toks[j] for j in o])
        print(f'     ({a_str}, {o_str}, {p})')
