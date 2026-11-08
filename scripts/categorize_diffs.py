import sys, ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase1.txt', 'r', encoding='utf-8') as f:
    thuan_lines = [l.strip() for l in f if l.strip()]

with open('data/validate_label/hung/phase1.txt', 'r', encoding='utf-8') as f:
    hung_lines = [l.strip() for l in f if l.strip()]

categories = {
    'hung_empty_thuan_labeled': [], # 25 records
    'thuan_empty_hung_labeled': [],
    'thuan_has_bare_trieucuong': [], # thuan tagged bare 'triều cường'
    'multi_level_duplication_in_thuan': [], # thuan tagged both street and ward/district/city
    'infrastructure_prefix_diff': [], # e.g. 'đường X' vs 'X'
    'opinion_span_diff': [], # e.g. rich context with comma vs short
    'polarity_diff': [],
    'other': []
}

for i in range(len(thuan_lines)):
    t_text, t_trips = thuan_lines[i].split('####')
    h_text, h_trips = hung_lines[i].split('####')
    t_parsed = ast.literal_eval(t_trips)
    h_parsed = ast.literal_eval(h_trips)
    
    if t_parsed == h_parsed:
        continue
        
    t_tokens = t_text.split()
    h_tokens = h_text.split()
    
    if t_parsed and not h_parsed:
        categories['hung_empty_thuan_labeled'].append(i + 1)
        continue
    if not t_parsed and h_parsed:
        categories['thuan_empty_hung_labeled'].append(i + 1)
        continue
        
    # Check if Thuan has bare 'triều cường' aspect
    has_bare_tc = False
    for asp, opi, pol in t_parsed:
        asp_w = ' '.join([t_tokens[j] for j in asp]).lower()
        if asp_w in ['triều cường', 'đỉnh triều']:
            has_bare_tc = True
            break
    if has_bare_tc:
        categories['thuan_has_bare_trieucuong'].append(i + 1)
        continue
        
    # Check multi-level duplication in Thuan
    if len(t_parsed) > len(h_parsed):
        t_opis = [tuple(t[1]) for t in t_parsed]
        if len(t_opis) != len(set(t_opis)):
            categories['multi_level_duplication_in_thuan'].append(i + 1)
            continue
            
    # Check infrastructure prefix differences (e.g. đường X vs X)
    t_asps = [' '.join([t_tokens[j] for j in t[0]]) for t in t_parsed]
    h_asps = [' '.join([h_tokens[j] for j in h[0]]) for h in h_parsed]
    if len(t_asps) == len(h_asps):
        prefix_diff = False
        for ta, ha in zip(t_asps, h_asps):
            if (ta.startswith('đường ') and ta[6:] == ha) or (ha.startswith('đường ') and ha[6:] == ta):
                prefix_diff = True
                break
        if prefix_diff:
            categories['infrastructure_prefix_diff'].append(i + 1)
            continue
            
    # Check opinion span difference
    t_opis_w = [' '.join([t_tokens[j] for j in t[1]]) for t in t_parsed]
    h_opis_w = [' '.join([h_tokens[j] for j in h[1]]) for h in h_parsed]
    if t_asps == h_asps and t_opis_w != h_opis_w:
        categories['opinion_span_diff'].append(i + 1)
        continue
        
    # Check polarity difference
    t_pols = [t[2] for t in t_parsed]
    h_pols = [h[2] for h in h_parsed]
    if t_asps == h_asps and t_opis_w == h_opis_w and t_pols != h_pols:
        categories['polarity_diff'].append(i + 1)
        continue
        
    categories['other'].append(i + 1)

print("=== CATEGORIZATION OF DIFFERENCES ===")
for cat, recs in categories.items():
    print(f"{cat}: count={len(recs)}, recs={recs[:20]}{'...' if len(recs)>20 else ''}")
