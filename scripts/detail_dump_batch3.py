import sys, ast, re

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch_batch3_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

for idx, b in enumerate(blocks):
    rec_num = 201 + idx
    header, line = b.split('\n', 1)
    
    if '#####' in line:
        text, trip_str = line.split('#####', 1)
    elif '####' in line:
        text, trip_str = line.split('####', 1)
    else:
        text, trip_str = line, "[]"
        
    trip_str = trip_str.lstrip('#').strip()
    try:
        trips = ast.literal_eval(trip_str)
    except Exception as e:
        trips = []
        
    tokens = text.split()
    print(f"[{rec_num}] Len={len(tokens)}")
    print(f"TEXT: {text}")
    print(f"RAW_TRIPS: {trips}")
    for a, o, s in trips:
        asp_str = ' '.join(tokens[i] for i in a if i < len(tokens))
        opi_str = ' '.join(tokens[i] for i in o if i < len(tokens))
        print(f"   Asp: [{asp_str}] | Opi: [{opi_str}] | {s}")
    print()
