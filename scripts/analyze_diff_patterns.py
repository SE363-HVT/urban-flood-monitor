import sys, ast

sys.stdout.reconfigure(encoding='utf-8')
from scripts.analyze_diff_recs import diff_recs
from scripts.generate_audited_phase1 import thuan_lines, hung_lines

tc_recs = []
multilevel_recs = []
text_diff_recs = []
other_diffs = []

for r in diff_recs:
    t_text, t_trips = thuan_lines[r-1].split('####')
    h_text, h_trips = hung_lines[r-1].split('####')
    t_p = ast.literal_eval(t_trips)
    h_p = ast.literal_eval(h_trips)
    t_toks = t_text.split()
    h_toks = h_text.split()
    
    if t_text != h_text:
        text_diff_recs.append(r)
    
    # check bare trieucuong in thuan
    has_bare_tc = any(' '.join([t_toks[j] for j in a]).lower() in ['triều cường', 'đỉnh triều'] for a, o, p in t_p)
    if has_bare_tc:
        tc_recs.append(r)
        
    # check multi-level dup in thuan
    t_opis = [tuple(t[1]) for t in t_p]
    if len(t_opis) != len(set(t_opis)):
        multilevel_recs.append(r)

print(f"Total diff recs: {len(diff_recs)}")
print(f"Text differs (e.g. in-place additions): {len(text_diff_recs)}")
print(f"Thuận has bare triều cường: {len(tc_recs)}")
print(f"Thuận has duplicate opinions (multi-level): {len(multilevel_recs)}")
