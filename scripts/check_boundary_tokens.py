import sys, ast

sys.stdout.reconfigure(encoding='utf-8')
with open('data/validate_label/thuan/phase1.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

boundary_issues = []

unwanted_edge_words = {'nha', 'ạ', 'ơi', 'nè', 'nhé', 'với', 'và', 'của', 'ở', 'tại', 'trên', 'dưới', 'trong', 'ngoài', 'từ', 'đến', 'là'}

for idx, line in enumerate(lines, 1):
    text, trips_str = line.split('####')
    tokens = text.split()
    trips = ast.literal_eval(trips_str)
    
    for t_idx, (asp, opi, pol) in enumerate(trips):
        asp_toks = [tokens[i] for i in asp]
        opi_toks = [tokens[i] for i in opi]
        
        # Check aspect start/end
        if asp_toks and asp_toks[0].lower() in unwanted_edge_words:
            boundary_issues.append((idx, f"Aspect starts with '{asp_toks[0]}'", ' '.join(asp_toks)))
        if asp_toks and asp_toks[-1].lower() in unwanted_edge_words:
            boundary_issues.append((idx, f"Aspect ends with '{asp_toks[-1]}'", ' '.join(asp_toks)))
            
        # Check opinion start/end
        if opi_toks and opi_toks[0].lower() in {'nha', 'ạ', 'ơi', 'nè', 'nhé', 'và', 'với'}:
            boundary_issues.append((idx, f"Opinion starts with '{opi_toks[0]}'", ' '.join(opi_toks)))
        if opi_toks and opi_toks[-1].lower() in {'nha', 'ạ', 'ơi', 'nè', 'nhé', 'và', 'với', 'ở', 'tại', 'trong', 'trên'}:
            boundary_issues.append((idx, f"Opinion ends with '{opi_toks[-1]}'", ' '.join(opi_toks)))

print(f"Total boundary issues: {len(boundary_issues)}")
for iss in boundary_issues:
    print(f"Rec {iss[0]}: {iss[1]} -> '{iss[2]}'")
