import sys
from ast import literal_eval
sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    current = [l.strip() for l in f]
with open('data/validate_label/thuan/phase2.txt.backup_v2', 'r', encoding='utf-8') as f:
    backup = [l.strip() for l in f]

shortened_cases = []
for idx in range(2000):
    c = current[idx]
    b = backup[idx]
    c_parts = c.split('####')
    b_parts = b.split('####')
    c_trips = literal_eval(c_parts[1]) if len(c_parts) > 1 else []
    b_trips = literal_eval(b_parts[1]) if len(b_parts) > 1 else []
    c_tokens = c_parts[0].split()
    b_tokens = b_parts[0].split()
    
    for (ca, co, cp) in c_trips:
        for (ba, bo, bp) in b_trips:
            # Match same aspect
            if ca == ba and len(co) < len(bo):
                b_text = ' '.join(b_tokens[i] for i in bo)
                c_text = ' '.join(c_tokens[i] for i in co)
                asp_text = ' '.join(c_tokens[i] for i in ca)
                shortened_cases.append({
                    'line': idx + 1,
                    'aspect': asp_text,
                    'asp_idx': ca,
                    'current_opi': c_text,
                    'curr_idx': co,
                    'backup_opi': b_text,
                    'back_idx': bo
                })

print(f"Total shortened cases found: {len(shortened_cases)}")
for sc in shortened_cases:
    print(f"L{sc['line']}: asp=[{sc['aspect']}] | curr=[{sc['current_opi']}] | back=[{sc['backup_opi']}]")
