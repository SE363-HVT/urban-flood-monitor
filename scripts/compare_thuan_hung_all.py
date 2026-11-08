import sys, ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase1.txt', 'r', encoding='utf-8') as f:
    thuan_lines = [l.strip() for l in f if l.strip()]

with open('data/validate_label/hung/phase1.txt', 'r', encoding='utf-8') as f:
    hung_lines = [l.strip() for l in f if l.strip()]

print(f'Thuan lines: {len(thuan_lines)}, Hung lines: {len(hung_lines)}')

diff_count = 0
for idx in range(min(len(thuan_lines), len(hung_lines))):
    t_text, t_trips = thuan_lines[idx].split('####')
    h_text, h_trips = hung_lines[idx].split('####')
    t_parsed = ast.literal_eval(t_trips)
    h_parsed = ast.literal_eval(h_trips)
    
    if t_parsed != h_parsed:
        diff_count += 1
        t_tokens = t_text.split()
        h_tokens = h_text.split()
        print(f"\n==================== RECORD {idx + 1} ====================")
        print(f"TEXT THUAN: {t_text}")
        print(f"TRIPS THUAN: {t_parsed}")
        for asp, opi, pol in t_parsed:
            a_w = ' '.join([t_tokens[i] for i in asp])
            o_w = ' '.join([t_tokens[i] for i in opi])
            print(f"   Thuan -> ({a_w}, {o_w}, {pol})")
        print(f"TEXT HUNG:  {h_text}")
        print(f"TRIPS HUNG:  {h_parsed}")
        for asp, opi, pol in h_parsed:
            a_w = ' '.join([h_tokens[i] for i in asp])
            o_w = ' '.join([h_tokens[i] for i in opi])
            print(f"   Hung  -> ({a_w}, {o_w}, {pol})")

print(f"\nTotal differences: {diff_count} / {len(thuan_lines)}")
