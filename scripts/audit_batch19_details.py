import sys
from ast import literal_eval
sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f]

batch = lines[1800:1900]

for idx, line in enumerate(batch, 1801):
    parts = line.split('####')
    text = parts[0]
    triplets = literal_eval(parts[1]) if len(parts) > 1 else []
    tokens = text.split()
    
    for a_idx, o_idx, pol in triplets:
        a_txt = ' '.join(tokens[i] for i in a_idx)
        o_txt = ' '.join(tokens[i] for i in o_idx)
        
        # Check if aspect is district but there's a street in text
        if a_txt in ['Quận 7', 'Bình Thạnh', 'Thủ Đức', 'Gò Vấp', 'Tân Bình', 'Bình Tân', 'Quận 8', 'TPHCM', 'TP.HCM']:
            for w in ['đường', 'cầu', 'hẻm']:
                if w in text.lower():
                    print(f"L{idx}: Broad aspect [{a_txt}] while '{w}' in text: {text[:90]}...")
                    break
