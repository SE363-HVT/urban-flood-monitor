import sys, ast

sys.stdout.reconfigure(encoding='utf-8')
from scripts.generate_audited_phase1 import thuan_lines, hung_lines, REJECT_RECORDS

diff_recs = []
for i in range(len(thuan_lines)):
    rec_num = i + 1
    if rec_num in REJECT_RECORDS:
        continue
    t_text, t_trips = thuan_lines[i].split('####')
    h_text, h_trips = hung_lines[i].split('####')
    t_p = ast.literal_eval(t_trips)
    h_p = ast.literal_eval(h_trips)
    if t_p != h_p or t_text != h_text:
        diff_recs.append(rec_num)

print(f"Total diff recs: {len(diff_recs)}")
