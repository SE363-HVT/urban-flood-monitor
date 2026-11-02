import sys
import ast
import re

sys.stdout.reconfigure(encoding='utf-8')

filepath = r'D:\SE363_RAWDATA\data\validate_label\thuan\phase1.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f]

assert len(lines) == 500, f"Expected 500 lines, found {len(lines)}"

locative_preps = {'ở', 'tại', 'trên', 'dưới', 'trong', 'ngoài', 'từ', 'đến', 'gần', 'cạnh', 'bên', 'phía', 'thuộc', 'của'}
vehicles = {'xe', 'xe máy', 'ô tô', 'xe buýt', 'xe tải', 'thuyền', 'ghe', 'ca nô', 'xe gắn máy', 'phương tiện', 'ô-tô', 'xe-máy', 'xe taxi', 'taxi', 'xe điện'}
people_roles = {'người dân', 'người', 'tài xế', 'bà con', 'chị oanh', 'cụ bà', 'phóng viên', 'admin', 'bác tài', 'mấy ní', 'chị', 'anh', 'em', 'chúng tôi'}
standalone_puncts = {'.', ',', ';', ':', '!', '?', '…', '...', '”', '\"', '\'', '(', ')', '[', ']', '-', '–', '|', '“', '‘', '’'}

provinces_regex = re.compile(
    r'(?<![a-zA-Z0-9_àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđĐ])'
    r'(cần\s*thơ|cantho|càmau|cà\s*mau|camau|sa\s*déc|sadec|đồng\s*tháp|dongthap|vĩnh\s*long|vinhlong|'
    r'đồng\s*nai|dongnai|long\s*khánh|hà\s*nội|hanoi|hanoimua|đà\s*nẵng|danang|hải\s*phòng|quảng\s*ninh|'
    r'thái\s*nguyên|yên\s*bái|lào\s*cai|yagi|thái\s*lan|bangkok|tiền\s*giang|mỹ\s*tho|bến\s*tre|trà\s*vinh|'
    r'sóc\s*trăng|bạc\s*liêu|kiên\s*giang|rạch\s*giá|an\s*giang|long\s*xuyên|châu\s*đốc|hậu\s*giang|'
    r'chương\s*mỹ|tứ\s*liên|bình\s*thủy|ninh\s*kiều)'
    r'(?![a-zA-Z0-9_àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđĐ])',
    re.IGNORECASE
)

print("================================================================================")
print("BẮT ĐẦU QUY TRÌNH KIỂM ĐỊNH LẶP ĐI LẶP LẠI 10 LẦN CHO 500 RECORDS (PHASE 1)")
print("================================================================================\n")

all_pass_success = True

for pass_num in range(1, 11):
    print(f">>> [PASS {pass_num}/10] Đang kiểm tra lần thứ {pass_num}...")
    pass_flaws = []

    for idx, line in enumerate(lines):
        rec_num = idx + 1
        if '####' not in line:
            pass_flaws.append((rec_num, "FORMAT_ERROR: Thiếu dấu phân cách ####"))
            continue
        text, trip_str = line.split('####')
        tokens = text.split()
        triplets = ast.literal_eval(trip_str)

        # 1. PASS 1: Kiểm tra biên Index Token
        if pass_num == 1:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                for k in asp + opi:
                    if k < 0 or k >= len(tokens):
                        pass_flaws.append((rec_num, f"INDEX_OUT_OF_BOUNDS: Token {k} ngoài dải [0, {len(tokens)-1}]"))

        # 2. PASS 2: Kiểm tra Overlap giữa Aspect và Opinion
        elif pass_num == 2:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                overlap = set(asp).intersection(set(opi))
                if overlap:
                    pass_flaws.append((rec_num, f"OVERLAP_ERROR: Trùng index {overlap} tại triplet {t_idx}"))

        # 3. PASS 3: Kiểm tra ranh giới Aspect (Giới từ, Dấu câu)
        elif pass_num == 3:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                asp_words = [tokens[k] for k in asp]
                if asp_words:
                    if asp_words[0].lower() in locative_preps and len(asp_words) > 1:
                        pass_flaws.append((rec_num, f"PREP_IN_ASPECT: Aspect dính giới từ '{asp_words[0]}'"))
                    if asp_words[0] in standalone_puncts or asp_words[-1] in standalone_puncts:
                        pass_flaws.append((rec_num, f"PUNCT_IN_ASPECT: Aspect dính dấu câu ở rìa: '{' '.join(asp_words)}'"))

        # 4. PASS 4: Kiểm tra ranh giới Opinion (Dấu câu, Cụm danh từ trơ trọi)
        elif pass_num == 4:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                opi_words = [tokens[k] for k in opi]
                if opi_words:
                    if opi_words[0] in standalone_puncts or opi_words[-1] in standalone_puncts:
                        pass_flaws.append((rec_num, f"PUNCT_IN_OPINION: Opinion dính dấu câu ở rìa: '{' '.join(opi_words)}'"))
                    opi_str = ' '.join(opi_words).lower()
                    if opi_str in ['đoạn ngập', 'những đoạn ngập', 'khu vực ngập', 'điểm ngập', 'vùng ngập']:
                        pass_flaws.append((rec_num, f"BARE_NOUN_OPINION: Opinion là cụm danh từ trơ trọi: '{opi_str}'"))

        # 5. PASS 5: Luật cấm Phương tiện giao thông (Vehicle Aspect Rule)
        elif pass_num == 5:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                asp_str = ' '.join(tokens[k] for k in asp).lower()
                if asp_str in vehicles:
                    pass_flaws.append((rec_num, f"VEHICLE_ASPECT_RULE: Aspect là phương tiện giao thông: '{asp_str}'"))

        # 6. PASS 6: Luật cấm Con người / Vai trò (Person / Role Aspect Rule)
        elif pass_num == 6:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                asp_str = ' '.join(tokens[k] for k in asp).lower()
                if asp_str in people_roles:
                    pass_flaws.append((rec_num, f"PERSON_ROLE_ASPECT: Aspect là con người/vai trò: '{asp_str}'"))

        # 7. PASS 7: Kiểm tra Phạm vi Địa lý TP.HCM (Geographic Scope)
        elif pass_num == 7:
            if triplets:  # Chỉ kiểm tra những mẫu CHƯA bị REJECT
                m = provinces_regex.search(text)
                if m:
                    pass_flaws.append((rec_num, f"OUT_OF_SCOPE_SUSPECT: Chứa từ khóa tỉnh ngoài '{m.group(0)}'"))

        # 8. PASS 8: Thẩm định Tính Nhất quán Sắc thái (Polarity Litmus Test)
        elif pass_num == 8:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                opi_str = ' '.join(tokens[k] for k in opi).lower()
                # Nếu nước rút/phục hồi rõ ràng mà mang nhãn NEG
                if pol == 'NEG' and any(kw in opi_str for kw in ['rút sạch', 'hết ngập', 'khô ráo', 'thông thoáng']):
                    pass_flaws.append((rec_num, f"POLARITY_MISMATCH: Nước rút nhưng mang nhãn NEG: '{opi_str}'"))
                # Nếu ngập sâu nghiêm trọng rõ ràng mà mang nhãn NEU
                if pol == 'NEU' and any(kw in opi_str for kw in ['ngập sâu lút', 'chết máy hàng loạt', 'chìm sâu trong biển nước']):
                    pass_flaws.append((rec_num, f"POLARITY_MISMATCH: Ngập sâu nghiêm trọng nhưng mang nhãn NEU: '{opi_str}'"))

        # 9. PASS 9: Kiểm tra DOC_FALLBACK vs Tên đường cụ thể
        elif pass_num == 9:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                asp_str = ' '.join(tokens[k] for k in asp)
                if asp_str == 'TP. Hồ Chí Minh':
                    # Kiểm tra xem câu có xuất hiện tên đường riêng viết hoa rõ ràng không
                    lower_t = text.lower()
                    for street_lead in ['đường nguyễn', 'đường lê', 'đường trần', 'đường huỳnh', 'đường võ', 'đường phạm']:
                        if street_lead in lower_t:
                            pass_flaws.append((rec_num, f"DOC_FALLBACK_MISUSE: Câu có '{street_lead}' nhưng aspect là TP. Hồ Chí Minh"))

        # 10. PASS 10: Hội tụ Cấu trúc, Format và Tính Toàn vẹn Tổng thể
        elif pass_num == 10:
            if not isinstance(triplets, list):
                pass_flaws.append((rec_num, "STRUCTURE_ERROR: Triplets không phải list"))
            for tr in triplets:
                if len(tr) != 3 or tr[2] not in ('POS', 'NEG', 'NEU'):
                    pass_flaws.append((rec_num, f"STRUCTURE_ERROR: Triplet {tr} sai định dạng chuẩn ASTE v2"))

    if pass_flaws:
        all_pass_success = False
        print(f"❌ PASS {pass_num} PHÁT HIỆN {len(pass_flaws)} LỖI:")
        for r, msg in pass_flaws[:10]:
            print(f"   - Record {r}: {msg}")
    else:
        print(f"✅ PASS {pass_num} HOÀN THÀNH: 0 LỖI (100% ĐẠT CHUẨN)")

print("\n================================================================================")
if all_pass_success:
    print("KẾT LUẬN: TOÀN BỘ 10 VÒNG KIỂM TRA ĐỀU ĐẠT 100% TUYỆT ĐỐI KHÔNG CÒN HẠT SẠN NÀO!")
else:
    print("KẾT LUẬN: CẦN TIẾP TỤC HIỆU CHỈNH CÁC LỖI TRÊN!")
print("================================================================================")
