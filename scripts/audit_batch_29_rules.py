import sys
import ast
import re

sys.stdout.reconfigure(encoding="utf-8")

with open("data/validate_label/thuan/phase2.txt", "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f]

for idx in range(680, 730):
    parts = lines[idx].split("####")
    text = parts[0]
    triplets = ast.literal_eval(parts[1]) if len(parts) > 1 else []
    toks = text.split()
    
    for asp, opi, pol in triplets:
        asp_s = " ".join(toks[k] for k in asp)
        opi_s = " ".join(toks[k] for k in opi)
        
        # 1. Prep in aspect
        if toks[asp[0]].lower() in ['ở', 'tại', 'trên', 'dưới', 'trong', 'từ', 'đến', 'đoạn', 'tuyến']:
            print(f"REC {idx+1}: PREP/GENERIC IN ASPECT: '{asp_s}'")
            
        # 2. Passive/causative in opinion
        if toks[opi[0]].lower() in ['bị', 'gây', 'làm', 'do']:
            print(f"REC {idx+1}: PASSIVE/CAUSATIVE IN OPINION: '{opi_s}'")
            
        # 3. Edge punct
        if toks[opi[-1]] in ['.', ',', ';', ':', '!', '?', '"', '”', '…']:
            print(f"REC {idx+1}: EDGE PUNCT END OPINION: '{opi_s}'")
        if toks[opi[0]] in ['.', ',', ';', ':', '!', '?', '"', '“', '…']:
            print(f"REC {idx+1}: EDGE PUNCT START OPINION: '{opi_s}'")
            
        # 4. Bare noun
        if opi_s.lower() in ['điểm ngập', 'đoạn ngập', 'khu vực ngập', 'mặt đường', 'tuyến đường']:
            print(f"REC {idx+1}: BARE NOUN OPINION: '{opi_s}'")
            
        # 5. Fallback misuse
        if asp_s.lower() in ['tp. hồ chí minh', 'tphcm', 'tp. hcm']:
            for wi, w in enumerate(toks):
                if w.lower() == 'đường' and wi + 1 < len(toks):
                    nxt = toks[wi+1]
                    if nxt[0].isupper() and nxt.lower() not in ['này', 'đó', 'kia', 'tp', 'tp.', 'tphcm', 'hcm']:
                        print(f"REC {idx+1}: SUSPECT FALLBACK: Has street '{w} {nxt}' but aspect is '{asp_s}'")
                        break
                        
        # 6. Polarity warnings
        if 'đề phòng' in opi_s.lower() or 'cảnh báo' in opi_s.lower():
            if pol == 'NEG':
                print(f"REC {idx+1}: ADVISORY POLARITY: '{opi_s}' is NEG, should be NEU?")
        if 'chống ngập' in opi_s.lower() and pol != 'POS':
            print(f"REC {idx+1}: CHONG NGAP POLARITY: '{opi_s}' is {pol}, should be POS?")
