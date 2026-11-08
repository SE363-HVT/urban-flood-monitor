import sys, os, ast, re

sys.stdout.reconfigure(encoding='utf-8')

def audit_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]

    print(f"Total lines: {len(lines)}")
    assert len(lines) == 500, f"Expected 500 lines, got {len(lines)}"

    # We will check each record
    total_triplets = 0
    issues = []

    for idx, line in enumerate(lines, 1):
        if '####' not in line:
            issues.append((idx, "FORMAT_ERROR", "Missing '####' separator"))
            continue
            
        text, trips_str = line.split('####')
        tokens = text.split()
        
        try:
            triplets = ast.literal_eval(trips_str)
        except Exception as e:
            issues.append((idx, "SYNTAX_ERROR", f"Cannot parse triplets: {e}"))
            continue
            
        total_triplets += len(triplets)
        
        for t_idx, trip in enumerate(triplets):
            if len(trip) != 3:
                issues.append((idx, "TUPLE_LEN", f"Triplet {t_idx} has length {len(trip)} != 3"))
                continue
                
            asp, opi, pol = trip
            
            # Check non-empty
            if not asp:
                issues.append((idx, "EMPTY_ASP", f"Triplet {t_idx} has empty aspect"))
            if not opi:
                issues.append((idx, "EMPTY_OPI", f"Triplet {t_idx} has empty opinion"))
                
            # Check bounds
            for i in asp:
                if i < 0 or i >= len(tokens):
                    issues.append((idx, "OUT_OF_BOUNDS_ASP", f"Index {i} out of bounds (len={len(tokens)})"))
            for i in opi:
                if i < 0 or i >= len(tokens):
                    issues.append((idx, "OUT_OF_BOUNDS_OPI", f"Index {i} out of bounds (len={len(tokens)})"))
                    
            # Check contiguous
            if asp and asp != list(range(asp[0], asp[-1] + 1)):
                issues.append((idx, "NON_CONTIGUOUS_ASP", f"Aspect {asp} is not contiguous"))
            if opi and opi != list(range(opi[0], opi[-1] + 1)):
                issues.append((idx, "NON_CONTIGUOUS_OPI", f"Opinion {opi} is not contiguous"))
                
            # Check overlap
            if set(asp) & set(opi):
                issues.append((idx, "OVERLAP", f"Aspect {asp} overlaps with Opinion {opi}"))
                
            # Decode words
            asp_words = ' '.join([tokens[i] for i in asp]) if all(0 <= i < len(tokens) for i in asp) else ""
            opi_words = ' '.join([tokens[i] for i in opi]) if all(0 <= i < len(tokens) for i in opi) else ""
            
            # Preposition leakage
            first_asp_tok = tokens[asp[0]].lower() if asp and 0 <= asp[0] < len(tokens) else ""
            if first_asp_tok in ['ở', 'tại', 'trên', 'dưới', 'trong', 'ngoài', 'từ', 'đến', 'gần', 'cạnh', 'bên', 'phía', 'thuộc', 'của']:
                issues.append((idx, "PREP_LEAKAGE", f"Aspect starts with prep '{first_asp_tok}': '{asp_words}'"))
                
            # Punct leakage in opinion
            if opi and 0 <= opi[0] < len(tokens):
                first_opi_tok = tokens[opi[0]]
                if first_opi_tok in [',', '.', ':', ';', '!', '?', '-', '–', '"', "'", '“', '”', '…']:
                    issues.append((idx, "EDGE_PUNCT_START", f"Opinion starts with punct '{first_opi_tok}': '{opi_words}'"))
            if opi and 0 <= opi[-1] < len(tokens):
                last_opi_tok = tokens[opi[-1]]
                if last_opi_tok in [',', '.', ':', ';', '!', '?', '-', '–', '"', "'", '“', '”', '…']:
                    issues.append((idx, "EDGE_PUNCT_END", f"Opinion ends with punct '{last_opi_tok}': '{opi_words}'"))
                    
            # Bare triều cường check
            if asp_words.lower() in ['triều cường', 'đỉnh triều', 'triều cao']:
                issues.append((idx, "BARE_TRIEU_CUONG", f"Aspect is bare '{asp_words}'"))
                
            # Vehicle check
            if asp_words.lower() in ['xe máy', 'ô tô', 'oto', 'xe buýt', 'xe tải', 'phương tiện']:
                issues.append((idx, "VEHICLE_ASPECT", f"Aspect is vehicle '{asp_words}'"))
                
            # Polarity check
            if pol not in ['POS', 'NEG', 'NEU']:
                issues.append((idx, "INVALID_POL", f"Polarity '{pol}' not in POS/NEG/NEU"))

    print(f"Total triplets audited: {total_triplets}")
    print(f"Total issues found: {len(issues)}")
    for iss in issues:
        print(f"  Line {iss[0]}: [{iss[1]}] {iss[2]}")
        
    return len(issues) == 0

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'data/validate_label/thuan/phase1.txt'
    audit_file(filepath)
