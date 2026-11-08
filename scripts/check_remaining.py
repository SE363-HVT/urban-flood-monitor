import sys, ast

sys.stdout.reconfigure(encoding='utf-8')
from scripts.analyze_diff_patterns import diff_recs, tc_recs, multilevel_recs, text_diff_recs
from scripts.generate_audited_phase1 import thuan_lines, hung_lines

remaining = set(diff_recs) - set(tc_recs) - set(multilevel_recs) - set(text_diff_recs)
print(f"Remaining records: {len(remaining)}")
for r in sorted(list(remaining)):
    t_text, t_trips = thuan_lines[r-1].split('####')
    h_text, h_trips = hung_lines[r-1].split('####')
    t_p = ast.literal_eval(t_trips)
    h_p = ast.literal_eval(h_trips)
    t_toks = t_text.split()
    h_toks = h_text.split()
    print(f"\nRec {r}:")
    print(f"  Text: {t_text}")
    print(f"  Thuan: {t_p}")
    for a, o, p in t_p:
        a_s = " ".join([t_toks[j] for j in a])
        o_s = " ".join([t_toks[j] for j in o])
        print(f"    ({a_s}, {o_s}, {p})")
    print(f"  Hung:  {h_p}")
    for a, o, p in h_p:
        a_s = " ".join([h_toks[j] for j in a])
        o_s = " ".join([h_toks[j] for j in o])
        print(f"    ({a_s}, {o_s}, {p})")
