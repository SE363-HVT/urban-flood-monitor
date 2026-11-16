# -*- coding: utf-8 -*-
import ast, re

with open('scratch_all_859_rejected.txt', 'r', encoding='utf-8') as f:
    text = f.read()

entries = text.split('=== REC ')
print(f"Total entries: {len(entries) - 1}")

truly_out_provinces = [
    r'\bhà nội\b', r'\bhà đông\b', r'\bcần thơ\b', r'\bgia lai\b', r'\bđà nẵng\b',
    r'\bnha trang\b', r'\bquy nhơn\b', r'\bđà lạt\b', r'\blâm đồng\b', r'\bthanh hóa\b',
    r'\bnghệ an\b', r'\bhuế\b', r'\bquảng nam\b', r'\bquảng bình\b', r'\bquảng trị\b',
    r'\bhà tĩnh\b', r'\bnam định\b', r'\bthái bình\b', r'\bhải phòng\b', r'\bbắc giang\b',
    r'\bthái nguyên\b', r'\bvĩnh phúc\b', r'\bphú thọ\b', r'\bcà mau\b', r'\bbến tre\b',
    r'\ban giang\b', r'\bkiên giang\b', r'\bđồng tháp\b', r'\bsa đéc\b', r'\bvĩnh long\b',
    r'\btrà vinh\b', r'\bsóc trăng\b', r'\bbạc liêu\b', r'\bhậu giang\b', r'\btiền giang\b',
    r'\bmỹ tho\b', r'\bđồng nai\b', r'\bbiên hòa\b', r'\blong khánh\b', r'\btây ninh\b',
    r'\bbình phước\b', r'\bbình thuận\b', r'\bphan thiết\b', r'\bninh thuận\b', r'\bphan rang\b',
    r'\bkhánh hòa\b', r'\bkon tum\b', r'\bđắk lắk\b', r'\bđắk nông\b', r'\bbuôn ma thuột\b',
    r'\btrung quốc\b', r'\bthái lan\b', r'\bbangkok\b', r'\bhạ long\b'
]

commercial_patterns = [
    r'\botochutin\b', r'\btoantrung\b', r'\bbán xe\b', r'\bmua xe\b', r'\bthu mua\b',
    r'\bđịnh giá xe\b', r'\bshowroom\b', r'\bcửa chống ngập\b', r'\bbạt chắn\b',
    r'\bphòng trọ\b', r'\bbán nhà\b', r'\bmôi giới\b', r'\bcho thuê\b', r'\btrà sữa\b',
    r'\bquán ăn\b', r'\bẩm thực\b', r'\bsushi\b'
]

non_flood_patterns = [
    r'\bngập hoa\b', r'\bbiển lửa\b', r'\bhải sản ngập\b', r'\bvùng đất linh hồn\b',
    r'\banime\b', r'\bthú cưng\b', r'\bcâu cá\b', r'\bcá thiên nhiên\b', r'\bchủ nghĩa xã hội\b'
]

out_province = []
commercial = []
non_flood = []
remaining_candidates = []

for e in entries[1:]:
    lines = e.strip().split('\n')
    rec_id = int(lines[0].split(' ')[0])
    p3_line = lines[1][len('P3_TEXT: '):]
    m_line = lines[2][len('MASTER:  '):]
    
    combined = (p3_line + ' ' + m_line).lower()
    
    # Check if truly out-province
    if any(re.search(pat, combined) for pat in truly_out_provinces):
        # Exclude cases that are in TP.HCM / BD / VT but mention out province casually
        # like "công nhân PouYuen quê Bến Tre"
        if not any(k in combined for k in ['pouyuen', 'bình tân', 'thủ đức', 'gò vấp', 'quận ', 'bình dương', 'vũng tàu']):
            out_province.append((rec_id, p3_line, m_line))
            continue
            
    # Check commercial
    if any(re.search(pat, combined) for pat in commercial_patterns):
        commercial.append((rec_id, p3_line, m_line))
        continue
        
    # Check non flood
    if any(re.search(pat, combined) for pat in non_flood_patterns):
        non_flood.append((rec_id, p3_line, m_line))
        continue
        
    remaining_candidates.append((rec_id, p3_line, m_line))

print(f"1. Truly Out-Province: {len(out_province)}")
print(f"2. Commercial Ads: {len(commercial)}")
print(f"3. Non-Flood Entertainment: {len(non_flood)}")
print(f"4. Remaining Candidates to Carefully Audit: {len(remaining_candidates)}")

with open('scratch_candidates_to_audit.txt', 'w', encoding='utf-8') as f:
    for idx, p3, m in remaining_candidates:
        f.write(f"=== REC {idx} ===\nP3: {p3}\nMS: {m}\n\n")

print("Wrote scratch_candidates_to_audit.txt")
