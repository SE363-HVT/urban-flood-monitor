import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = [line.rstrip('\r\n') for line in f]

corrections = {
    # 1982 (idx 1981): TPHCM bì bõm lội (chuẩn hóa entity)
    1981: [([5], [15, 16, 17], 'NEG')],

    # 1985 (idx 1984): TPHCM CẢNH BÁO NGẬP (bổ sung token CẢNH)
    1984: [([0], [9, 10, 11], 'NEU')],

    # 1986 (idx 1985): TPHCM thường xuyên ngập nặng (chuẩn hóa entity)
    1985: [([13], [5, 6, 7, 8], 'NEG')],

    # 1988 (idx 1987): Hà Nội nắng nóng, triều cường ở TPHCM đạt đỉnh -> REJECT theo quy tắc 9 NON_HCM_PROVINCE
    1987: [],

    # 1990 (idx 1989): Sài Gòn ngập sâu (rút gọn opinion 12 tokens có comma)
    1989: [([2, 3], [10, 11], 'NEG')],

    # 1992 (idx 1991): TP. HCM ngập nặng / Mai Chí Thọ, Nguyễn Cơ Thạch nhích từng mét
    1991: [
        ([24, 25], [26, 27], 'NEG'),
        ([46, 47, 48], [42, 43, 44], 'NEG'),
        ([50, 51, 52], [42, 43, 44], 'NEG')
    ]
}

count_updated = 0
for idx, new_triplets in corrections.items():
    old_line = lines[idx]
    text = old_line.split('####')[0].strip()
    new_line = f"{text}####{new_triplets}"
    if new_line != old_line:
        lines[idx] = new_line
        count_updated += 1
        tokens = text.split()
        print(f"Update Rec {idx+1} (idx {idx}):")
        print(f"  Old: {old_line.split('####')[1]}")
        print(f"  New: {new_triplets}")
        for t in new_triplets:
            print(f"    Asp: '{' '.join(tokens[x] for x in t[0])}' | Op: '{' '.join(tokens[x] for x in t[1])}' | Pol: {t[2]}")

with open(filepath, 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print(f"\n✅ ĐÃ HIỆU CHỈNH THÀNH CÔNG {count_updated} RECORDS TRONG LÔ 55 (HOÀN TẤT PHASE 2)!")
