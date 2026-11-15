import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.rstrip('\r\n') for line in f]

for i in range(1880, 1930):
    line = lines[i]
    parts = line.split('####')
    text = parts[0].strip()
    trip_str = parts[1].strip() if len(parts) > 1 else '[]'
    triplets = ast.literal_eval(trip_str)
    tokens = text.split()
    
    # Check flags
    flaws = []
    for t in triplets:
        asp = " ".join(tokens[idx] for idx in t[0]) if t[0] else ""
        op = " ".join(tokens[idx] for idx in t[1]) if t[1] else ""
        pol = t[2]
        
        # Check bị
        if op.startswith("bị ") or op.startswith("lại bị "):
            flaws.append(f"Opinion starts with passive 'bị': '{op}'")
        # Check comma in op
        if "," in op:
            flaws.append(f"Opinion contains comma (run-on/leakage): '{op}'")
        # Check prep in asp
        if any(asp.startswith(p + " ") for p in ['ở', 'tại', 'trên', 'dưới', 'trong', 'từ', 'đến']):
            flaws.append(f"Aspect starts with prep: '{asp}'")
        # Check nonsense aspect
        if asp in ['vực ở', 'bộ đường Phạm Hữu', 'triều cường ở TPHCM']:
            flaws.append(f"Nonsense aspect: '{asp}'")
        # Check nonsense opinion
        if op in ['TPHCM ngập', 'máy dắt', 'vẫn còn', 'SÔNG CÓ NGUY CƠ', 'ngập cục']:
            flaws.append(f"Nonsense/truncated opinion: '{op}'")
            
    print(f"REC {i+1} (idx {i}):")
    print(f"  TEXT: {text}")
    print(f"  TRIPS: {triplets}")
    for t in triplets:
        print(f"    {' '.join(tokens[idx] for idx in t[0])} | {' '.join(tokens[idx] for idx in t[1])} | {t[2]}")
    if flaws:
        print(f"  ⚠️ FLAWS: {flaws}")
