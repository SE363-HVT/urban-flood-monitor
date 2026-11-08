import sys, ast
sys.stdout.reconfigure(encoding='utf-8')
from scripts.categorize_diffs import categories, thuan_lines, hung_lines

print('=== POLARITY DIFF (Recs: 391, 439) ===')
for r in [391, 439]:
    t_text, t_trips = thuan_lines[r-1].split('####')
    h_text, h_trips = hung_lines[r-1].split('####')
    print(f'Rec {r}:')
    print(f'  Text: {t_text}')
    print(f'  Thuan: {t_trips}')
    print(f'  Hung:  {h_trips}')

print('\n=== SAMPLE OPINION SPAN DIFF (first 10) ===')
for r in categories['opinion_span_diff'][:10]:
    t_text, t_trips = thuan_lines[r-1].split('####')
    h_text, h_trips = hung_lines[r-1].split('####')
    t_toks = t_text.split()
    h_toks = h_text.split()
    print(f'\nRec {r}:')
    print(f'  Text: {t_text}')
    t_p = ast.literal_eval(t_trips)
    h_p = ast.literal_eval(h_trips)
    for a, o, p in t_p:
        asp_str = " ".join([t_toks[i] for i in a])
        opi_str = " ".join([t_toks[i] for i in o])
        print(f'    Thuan: ({asp_str}, {opi_str}, {p})')
    for a, o, p in h_p:
        asp_str = " ".join([h_toks[i] for i in a])
        opi_str = " ".join([h_toks[i] for i in o])
        print(f'    Hung:  ({asp_str}, {opi_str}, {p})')
