import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

new_assignments = {
    # 1. Rec 16: "REC 16 gán opinion là ngập"
    16: [([7, 8], [4], 'NEU')],
    
    # 2. Rec 43: "rec 43 gán là Ngập"
    43: [([7, 8], [0], 'NEU')],
    
    # 3. Rec 93: "93 gán là ngập"
    93: [([0, 1], [2], 'NEG')],
    
    # 4. Rec 897: "897 là ngập"
    897: [([3, 4], [12], 'NEG')],
    
    # 5. Rec 1040: "1040 là ngập"
    1040: [([14, 15, 16], [22], 'NEG')],
    
    # 6. Rec 1616: đạt đỉnh xấp xỉ 1 , 8m
    1616: [([0, 1, 2, 3], [7, 8, 9, 10, 11, 12, 13], 'NEU')],
    
    # 7. Rec 1659: đạt đỉnh xấp xỉ 1 , 8m
    1659: [([4, 5, 6, 7], [8, 9, 10, 11, 12, 13, 14], 'NEU')],
    
    # 8. Rec 1669: đạt đỉnh 1 , 85m
    1669: [([7, 8, 9, 10], [11, 12, 13, 14, 15], 'NEU')],
    
    # 9. Rec 1671: sẽ đạt đỉnh xấp xỉ 1 , 8m
    1671: [([9, 10, 11, 12], [13, 14, 15, 16, 17, 18, 19, 20], 'NEU')]
}

for rec_num, tr in new_assignments.items():
    idx = rec_num - 1
    t, _ = lines[idx].split('####')
    toks = t.split()
    print(f"Rec {rec_num}:")
    for a, o, p in tr:
        a_txt = " ".join(toks[i] for i in a)
        o_txt = " ".join(toks[i] for i in o)
        print(f"  Aspect='{a_txt}' ({a}) | Opinion='{o_txt}' ({o}) | Polarity='{p}'")
    lines[idx] = f"{t}####{tr}"

with open(filepath, 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print(f"\nĐã cập nhật chuẩn xác {len(new_assignments)} records!")
