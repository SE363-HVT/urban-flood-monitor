import sys
from ast import literal_eval
sys.stdout.reconfigure(encoding='utf-8')

if len(sys.argv) < 2:
    print("Usage: python audit_micro_batch_10.py <start_idx_0_based> [count=10]")
    sys.exit(1)

start_idx = int(sys.argv[1])
count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
end_idx = min(start_idx + count, 2000)

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

batch = lines[start_idx:end_idx]
print(f"==================================================")
print(f"=== MICRO-BATCH AUDIT: Records {start_idx+1} to {end_idx} ===")
print(f"==================================================")

preps = {'ở', 'tại', 'trên', 'dưới', 'trong', 'ngoài', 'từ', 'đến', 'gần', 'cạnh', 'bên', 'phía', 'thuộc', 'của'}
vehicles = {'xe', 'xe máy', 'ô tô', 'xe buýt', 'xe tải', 'thuyền', 'ghe', 'ca nô', 'xe gắn máy', 'phương tiện'}

for i, line in enumerate(batch):
    rec_no = start_idx + i + 1
    parts = line.split('####')
    text = parts[0]
    trip_str = parts[1] if len(parts) > 1 else '[]'
    tokens = text.split()
    triplets = literal_eval(trip_str)
    
    print(f"\n--- RECORD {rec_no} ---")
    print(f"TEXT: {text}")
    print(f"TOKENS ({len(tokens)}):")
    # print tokens in lines of 10
    tok_line = []
    for t_i, t in enumerate(tokens):
        tok_line.append(f"{t_i}:{t}")
        if len(tok_line) >= 8:
            print("  " + " | ".join(tok_line))
            tok_line = []
    if tok_line:
        print("  " + " | ".join(tok_line))
        
    print(f"TRIPLETS: {triplets}")
    if not triplets:
        print("  -> REJECTED (####[])")
    else:
        for t_idx, (a_idx, o_idx, pol) in enumerate(triplets):
            a_words = [tokens[j] for j in a_idx]
            o_words = [tokens[j] for j in o_idx]
            print(f"  [{t_idx+1}] ASPECT {a_idx}: '{' '.join(a_words)}'")
            print(f"      OPINION {o_idx}: '{' '.join(o_words)}'")
            print(f"      POLARITY: {pol}")
            
            # Diagnostic checks
            # 1. Prep in aspect
            if a_words[0].lower() in preps:
                print(f"      ⚠️ PREP LEAKAGE: '{a_words[0]}'")
            # 2. Vehicle as aspect
            if ' '.join(a_words).lower() in vehicles:
                print(f"      ⚠️ VEHICLE AS ASPECT: '{' '.join(a_words)}'")
            # 3. Bare tidal
            if ' '.join(a_words).lower() in ['triều cường', 'đỉnh triều', 'triều cao', 'thủy triều']:
                print(f"      ⚠️ BARE TIDAL: '{' '.join(a_words)}'")
            # 4. Missed prefix
            min_a = min(a_idx)
            if min_a > 0:
                p_tok = tokens[min_a-1].lower()
                if p_tok in ['đường', 'cầu', 'hẻm', 'ngõ', 'phố', 'đại_lộ', 'xa_lộ', 'rạch', 'kênh'] and p_tok not in ' '.join(a_words).lower():
                    if not (p_tok == 'đường' and ' '.join(a_words) in ['Sài Gòn', 'TP.HCM', 'TPHCM']):
                        print(f"      ⚠️ MISSED PREFIX: '{tokens[min_a-1]}' before '{' '.join(a_words)}'")
            # 5. Edge punct in opinion
            if o_words[0] in ['.', ',', ';', ':', '!', '?', '…', '-', '–']:
                print(f"      ⚠️ EDGE PUNCT START: '{o_words[0]}'")
            if o_words[-1] in ['.', ',', ';', ':', '!', '?', '…', '-', '–']:
                print(f"      ⚠️ EDGE PUNCT END: '{o_words[-1]}'")
