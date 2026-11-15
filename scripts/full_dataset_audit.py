import sys
import os
from ast import literal_eval
sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'

if not os.path.exists(filepath):
    print(f"Error: {filepath} does not exist.")
    sys.exit(1)

with open(filepath, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f]

total_lines = len(lines)
print(f"==================================================")
print(f"=== FULL DATASET AUDIT REPORT: phase2.txt ===")
print(f"Total lines: {total_lines}")
print(f"==================================================")

errors = []
warnings = []
total_triplets = 0
verified_lines = 0
rejected_lines = 0

out_of_province_kws = ['hà nội', 'đà nẵng', 'hải phòng', 'cần thơ', 'nha trang', 'huế', 'quảng ninh', 'vinh', 'thanh hóa', 'nghệ an', 'quảng bình', 'quảng trị', 'quảng nam', 'quảng ngãi', 'bình định', 'phú yên', 'khánh hòa', 'ninh thuận', 'bình thuận', 'lâm đồng', 'đà lạt', 'buôn ma thuột', 'đắk lắk', 'gia lai', 'pleiku', 'kon tum', 'hà tĩnh', 'nam định', 'thái bình', 'hải dương', 'bắc ninh', 'vĩnh phúc', 'phú thọ', 'thái nguyên', 'tuyên quang', 'lào cai', 'yên bái', 'hà giang', 'cao bằng', 'lạng sơn', 'bắc kạn', 'hòa bình', 'sơn la', 'điện biên', 'lai châu']

for idx, line in enumerate(lines, 1):
    if '####' not in line:
        errors.append(f"Line {idx}: Missing delimiter '####'")
        continue
    
    parts = line.split('####')
    text = parts[0]
    trip_str = parts[1] if len(parts) > 1 else '[]'
    tokens = text.split()
    
    try:
        triplets = literal_eval(trip_str)
    except Exception as e:
        errors.append(f"Line {idx}: Syntax error in triplets: {e}")
        continue
        
    if not triplets:
        rejected_lines += 1
    else:
        verified_lines += 1
        total_triplets += len(triplets)

    # 1. Index bounds & integrity
    for t_idx, (a_idx, o_idx, pol) in enumerate(triplets):
        if not a_idx:
            errors.append(f"Line {idx}: Empty aspect index in triplet {t_idx}")
        if not o_idx:
            errors.append(f"Line {idx}: Empty opinion index in triplet {t_idx}")
        for i in a_idx:
            if i < 0 or i >= len(tokens):
                errors.append(f"Line {idx}: Aspect index {i} out of bounds (len={len(tokens)})")
        for i in o_idx:
            if i < 0 or i >= len(tokens):
                errors.append(f"Line {idx}: Opinion index {i} out of bounds (len={len(tokens)})")

        a_words = ' '.join(tokens[i] for i in a_idx).lower()
        o_words = ' '.join(tokens[i] for i in o_idx).lower()

        # 2. Bare tidal aspect
        if a_words in ['triều cường', 'đỉnh triều', 'triều cao', 'thủy triều']:
            errors.append(f"Line {idx}: Standalone bare tidal aspect [{a_words}] without location!")

        # 3. Invalid non-geo aspects
        if a_words in ['xe cộ', 'giao thông', 'ô tô', 'xe máy', 'mực nước', 'nước']:
            errors.append(f"Line {idx}: Invalid non-geographic aspect [{a_words}]!")

        # 4. Opinion contains aspect name or triều cường
        if 'triều cường' in o_words:
            warnings.append(f"Line {idx}: Opinion contains 'triều cường': [{o_words}]")

    # 5. Out of province with positive labels
    t_lower = text.lower()
    for kw in out_of_province_kws:
        if kw in t_lower and kw not in ['xa lộ hà nội'] and triplets:
            # Check if there is also HCMC/Bình Dương
            if not any(h in t_lower for h in ['tphcm', 'tp. hcm', 'tp.hcm', 'sài gòn', 'bình dương', 'thủ đức']):
                warnings.append(f"Line {idx}: Out of province kw '{kw}' has triplets: {triplets}")

print(f"Checked records: {total_lines}")
print(f"Verified (informative flood) records: {verified_lines}")
print(f"Rejected (non-flood/out-of-province) records: {rejected_lines}")
print(f"Total valid triplets extracted: {total_triplets}")
print(f"Errors detected: {len(errors)}")
print(f"Warnings detected: {len(warnings)}")

if errors:
    print("\n--- ERRORS ---")
    for e in errors[:20]:
        print(e)

if warnings:
    print("\n--- WARNINGS ---")
    for w in warnings[:20]:
        print(w)

if not errors and not warnings:
    print("\n🎉 HOÀN TẤT 100%: TẤT CẢ 2,000 RECORDS PHASE 2 ĐẠT CHUẨN HOÀN TOÀN!")
