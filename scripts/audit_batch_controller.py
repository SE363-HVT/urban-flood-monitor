import sys, ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase1.txt', 'r', encoding='utf-8') as f:
    thuan_lines = [l.strip() for l in f if l.strip()]

with open('data/validate_label/hung/phase1.txt', 'r', encoding='utf-8') as f:
    hung_lines = [l.strip() for l in f if l.strip()]

def show_batch(start_idx, end_idx):
    print(f"==================================================")
    print(f"           AUDITING BATCH {start_idx} TO {end_idx}")
    print(f"==================================================")
    for i in range(start_idx - 1, end_idx):
        rec_num = i + 1
        t_text, t_trips = thuan_lines[i].split('####')
        h_text, h_trips = hung_lines[i].split('####')
        t_parsed = ast.literal_eval(t_trips)
        h_parsed = ast.literal_eval(h_trips)
        
        t_tokens = t_text.split()
        h_tokens = h_text.split()
        
        # Check differences or potential issues
        is_diff = (t_parsed != h_parsed)
        has_comma_in_opi = any(',' in [t_tokens[j] for j in t[1]] for t in t_parsed)
        has_tc = any(' '.join([t_tokens[j] for j in t[0]]).lower() in ['triều cường', 'đỉnh triều'] for t in t_parsed)
        
        if is_diff or has_comma_in_opi or has_tc:
            print(f"\n[Rec {rec_num}]")
            print(f"TEXT: {t_text}")
            print(f"  THUAN ({len(t_parsed)}):")
            for a, o, p in t_parsed:
                asp_s = ' '.join([t_tokens[j] for j in a])
                opi_s = ' '.join([t_tokens[j] for j in o])
                print(f"    ({asp_s} {a}, {opi_s} {o}, {p})")
            print(f"  HUNG  ({len(h_parsed)}):")
            for a, o, p in h_parsed:
                asp_s = ' '.join([h_tokens[j] for j in a])
                opi_s = ' '.join([h_tokens[j] for j in o])
                print(f"    ({asp_s} {a}, {opi_s} {o}, {p})")

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        show_batch(int(sys.argv[1]), int(sys.argv[2]))
    else:
        show_batch(1, 50)
