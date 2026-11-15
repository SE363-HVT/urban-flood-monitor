import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

# Search for "đạt đỉnh" followed by numbers / meters
peak_records = []
for idx, line in enumerate(lines):
    rec_num = idx + 1
    t, tr = line.split('####')
    toks = t.split()
    triplets = ast.literal_eval(tr)
    
    # check if "đạt đỉnh" in text
    if re.search(r'đạt\s+đỉnh', t, re.IGNORECASE):
        # find where đạt đỉnh is
        for i in range(len(toks) - 1):
            if toks[i].lower() == 'đạt' and toks[i+1].lower() == 'đỉnh':
                # look at following tokens
                after_toks = toks[i+2:i+8]
                after_str = " ".join(after_toks)
                # check if contains number or meter
                if re.search(r'\d+(\s*,\s*\d+)?\s*(m|mét|cm)?', after_str):
                    peak_records.append((rec_num, i, t, triplets))

print(f"Tổng số records có 'đạt đỉnh' kèm số đo mực nước: {len(peak_records)}")
for r, i, t, tr in peak_records:
    toks = t.split()
    print(f"Rec {r}:")
    tok_window = " ".join(f"[{k}:{toks[k]}]" for k in range(max(0, i-2), min(len(toks), i+8)))
    print(f"  Window: {tok_window}")
    print(f"  Current triplets: {tr}\n")
