import sys, ast
sys.stdout.reconfigure(encoding='utf-8')
from scripts.categorize_diffs import categories, thuan_lines, hung_lines

print(f"=== OTHER CATEGORY: {len(categories['other'])} records ===")
for r in categories['other']:
    t_text, t_trips = thuan_lines[r-1].split('####')
    h_text, h_trips = hung_lines[r-1].split('####')
    t_toks = t_text.split()
    h_toks = h_text.split()
    t_p = ast.literal_eval(t_trips)
    h_p = ast.literal_eval(h_trips)
    print(f"\n--- Rec {r} ---")
    print(f"Text: {t_text}")
    print(f"  Thuan ({len(t_p)}):")
    for a, o, p in t_p:
        asp_str = " ".join([t_toks[i] for i in a])
        opi_str = " ".join([t_toks[i] for i in o])
        print(f"    ({asp_str} {a}, {opi_str} {o}, {p})")
    print(f"  Hung ({len(h_p)}):")
    for a, o, p in h_p:
        asp_str = " ".join([h_toks[i] for i in a])
        opi_str = " ".join([h_toks[i] for i in o])
        print(f"    ({asp_str} {a}, {opi_str} {o}, {p})")
