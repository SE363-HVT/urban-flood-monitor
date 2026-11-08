import sys, os, ast, re

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase1.txt', 'r', encoding='utf-8') as f:
    thuan_lines = [l.strip() for l in f if l.strip()]

with open('data/validate_label/hung/phase1.txt', 'r', encoding='utf-8') as f:
    hung_lines = [l.strip() for l in f if l.strip()]

assert len(thuan_lines) == 500
assert len(hung_lines) == 500

REJECT_RECORDS = {
    68, 145, 148, 150, 155, 157, 172, 178, 179, 184, 187, 194, 203,
    215, 229, 315, 316, 326, 393, 452, 481, 482, 486, 490, 491
}
for i, line in enumerate(thuan_lines, 1):
    _, trips_str = line.split('####')
    if trips_str == '[]':
        REJECT_RECORDS.add(i)

print(f"Total reject records: {len(REJECT_RECORDS)}")

# Records where Thuan has the preferred rich descriptive opinion with comma
rich_opi_recs = {58, 59, 80, 97, 98, 103, 117, 119, 131, 177, 270, 274, 296, 302, 363, 448, 462, 465, 468}

master_lines = []

for i in range(500):
    rec_num = i + 1
    t_text, t_trips_str = thuan_lines[i].split('####')
    h_text, h_trips_str = hung_lines[i].split('####')
    t_trips = ast.literal_eval(t_trips_str)
    h_trips = ast.literal_eval(h_trips_str)
    
    # 1. REJECT records
    if rec_num in REJECT_RECORDS:
        master_lines.append(f"{t_text}####[]")
        continue

    # 2. Text determination: use hung text if hung added in-place/fallback, else thuan text
    text = h_text if h_text != t_text else t_text
    
    # 3. Base triplets: default to hung triplets (which resolved bare trieucuong, multi-level dups, lists of streets)
    trips = [t for t in h_trips]
    
    # Targeted corrections:
    # Rec 127: Pass 9 fix - remove fallback [20] because specific streets exist
    if rec_num == 127:
        trips = [t for t in trips if t[0] != [20]]
        
    # Rec 66: Remove preposition 'dưới' from bridge aspect
    if rec_num == 66:
        trips = [([5, 6, 7, 8], [13, 14, 15, 16, 17], 'NEG')]
        
    # Rec 439: Question polarity -> NEU per Section V
    if rec_num == 439:
        trips = [([9, 10, 11], [12, 13, 14, 15], 'NEU')]
        
    # Rec 391: Condition / Forecast -> NEU
    if rec_num == 391:
        trips = [([14], [19, 20, 21], 'NEU'), ([1, 2, 3, 4], [42, 43, 44, 45, 46], 'NEU')]

    # Enrich with Thuan's rich descriptive opinion if applicable
    if rec_num in rich_opi_recs and t_text == text:
        trips = t_trips

    # Format the line and validate bounds
    tokens = text.split()
    for asp, opi, pol in trips:
        for idx in asp:
            assert idx < len(tokens), f"Rec {rec_num}: asp idx {idx} out of bounds (len={len(tokens)}) in '{tokens}'"
        for idx in opi:
            assert idx < len(tokens), f"Rec {rec_num}: opi idx {idx} out of bounds (len={len(tokens)}) in '{tokens}'"
            
    master_lines.append(f"{text}####{repr(trips)}")

print(f"Generated {len(master_lines)} master lines.")
with open('data/validate_label/thuan/phase1_master.txt', 'w', encoding='utf-8') as f:
    for line in master_lines:
        f.write(line + '\n')
print("Saved to data/validate_label/thuan/phase1_master.txt")
