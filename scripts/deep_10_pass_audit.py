import sys
import re
import ast

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

if len(sys.argv) < 2:
    print("Sử dụng: python deep_10_pass_audit.py <path_to_data_file.txt>")
    sys.exit(1)

file_path = sys.argv[1]

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
except Exception as e:
    print(f"Lỗi đọc file: {e}")
    sys.exit(1)

total_records = len(lines)
print(f"File kiểm định: {file_path} (Tổng số records: {total_records})")
print("=" * 80)
print(f"BẮT ĐẦU QUY TRÌNH KIỂM ĐỊNH LẶP ĐI LẶP LẠI 10 LẦN CHO {total_records} RECORDS")
print("NGUYÊN TẮC: READ-ONLY AUDITOR (CHỈ KIỂM ĐỊNH - TUYỆT ĐỐI KHÔNG TỰ SỬA DỮ LIỆU)")
print("=" * 80)

# Danh sách từ khóa cấm/nguy cơ
standalone_puncts = {'.', ',', ';', ':', '!', '?', '…', '"', "'", '(', ')', '[', ']', '-', '–', '|', '“', '”'}
locative_preps = {'ở', 'tại', 'trên', 'dưới', 'trong', 'ngoài', 'từ', 'đến', 'gần', 'cạnh', 'bên', 'phía', 'thuộc', 'của'}
vehicles = {
    'xe máy', 'ô tô', 'xe buýt', 'xe tải', 'phương tiện', 'xe hơi', 'xe con', 
    'xe khách', 'xe ben', 'xe đạp', 'xe đầu kéo', 'xe ba gác', 'xe cộ', 'xe'
}
people_roles = {
    'người dân', 'người đi đường', 'tài xế', 'bà con', 'chị oanh', 'cụ bà', 
    'người', 'lực lượng chức năng', 'csgt', 'chú bảo vệ', 'công an', 'thợ sửa xe'
}

# Regex nhận diện tỉnh ngoài phạm vi hợp lệ
provinces_regex = re.compile(
    r'\b(hà nội|can tho|cần thơ|ninh kiều|cái răng|bình thủy|ô môn|thốt nốt|hưng phú|cà mau|đồng nai|sa đéc|'
    r'vĩnh long|bến tre|trà vinh|an giang|kiên giang|long xuyên|châu đốc|tiền giang|mỹ tho|hậu giang|vị thanh|'
    r'sóc trăng|bạc liêu|đà nẵng|huế|thừa thiên|quảng nam|quảng ngãi|bình định|quy nhơn|phú yên|tuy hòa|khánh hòa|'
    r'nha trang|ninh thuận|phan rang|bình thuận|phan thiết|lâm đồng|đà lạt|bảo lộc|gia lai|pleiku|kon tum|đắk lắk|'
    r'buôn ma thuột|đắk nông|gia nghĩa|bình phước|đồng xoài|tây ninh|hải phòng|quảng ninh|hạ long|thái nguyên|'
    r'bắc ninh|bắc giang|nam định|thái bình|hà nam|ninh bình|thanh hóa|nghệ an|vinh|hà tĩnh|chương mỹ|hoàng mai|'
    r'thanh xuân|cầu giấy|đống đa|ba đình|hoàn kiếm|hai bà trưng|tây hồ|long biên|hà đông|nam từ liêm|bắc từ liêm|'
    r'mê linh|đông anh|sóc sơn|gia lâm|thanh trì|thường tín|phú xuyên|quốc oai|thạch thất|đan phượng|hoài đức|'
    r'ba vì|phúc thọ|sơn tây|ứng hòa|mỹ đức|thanh oai)\b',
    re.IGNORECASE
)

all_pass_success = True

for pass_num in range(1, 11):
    print(f"\n>>> [PASS {pass_num}/10] Đang kiểm tra lần thứ {pass_num}...")
    pass_flaws = []
    
    for idx, line in enumerate(lines):
        rec_num = idx + 1
        if "####" not in line:
            pass_flaws.append((rec_num, "FORMAT_ERROR: Thiếu dấu phân cách ####"))
            continue
            
        text, labels_str = line.split("####", 1)
        tokens = text.split()
        
        try:
            triplets = ast.literal_eval(labels_str)
        except Exception as e:
            pass_flaws.append((rec_num, f"SYNTAX_ERROR: Không parse được nhãn {e}"))
            continue

        # 1. PASS 1: Kiểm tra Biên giới Index (Bounds Check)
        if pass_num == 1:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                for i in asp:
                    if i < 0 or i >= len(tokens):
                        pass_flaws.append((rec_num, f"OUT_OF_BOUNDS: Aspect index {i} ngoài phạm vi (len={len(tokens)})"))
                for j in opi:
                    if j < 0 or j >= len(tokens):
                        pass_flaws.append((rec_num, f"OUT_OF_BOUNDS: Opinion index {j} ngoài phạm vi (len={len(tokens)})"))

        # 2. PASS 2: Kiểm tra Tính Liên tục (Contiguity Check)
        elif pass_num == 2:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                if asp and asp != list(range(asp[0], asp[-1] + 1)):
                    pass_flaws.append((rec_num, f"NON_CONTIGUOUS: Aspect span không liên tục: {asp}"))
                if opi and opi != list(range(opi[0], opi[-1] + 1)):
                    pass_flaws.append((rec_num, f"NON_CONTIGUOUS: Opinion span không liên tục: {opi}"))

        # 3. PASS 3: Kiểm tra Trùng lặp Span giữa Aspect và Opinion (Overlap Check)
        elif pass_num == 3:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                overlap = set(asp) & set(opi)
                if overlap:
                    pass_flaws.append((rec_num, f"OVERLAP_ERROR: Aspect và Opinion giao nhau tại index {overlap}"))

        # 4. PASS 4: Kiểm tra Rò rỉ Dấu câu (Punctuation Leakage)
        elif pass_num == 4:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                asp_words = [tokens[k] for k in asp]
                opi_words = [tokens[k] for k in opi]
                if asp_words and (asp_words[0] in standalone_puncts or asp_words[-1] in standalone_puncts):
                    pass_flaws.append((rec_num, f"PUNCT_IN_ASPECT: Aspect dính dấu câu ở rìa: '{' '.join(asp_words)}'"))
                if opi_words and (opi_words[0] in standalone_puncts or opi_words[-1] in standalone_puncts):
                    pass_flaws.append((rec_num, f"PUNCT_IN_OPINION: Opinion dính dấu câu ở rìa: '{' '.join(opi_words)}'"))

        # 5. PASS 5: Kiểm tra Giới từ chỉ vị trí (Locative Prepositions) ở đầu Aspect
        elif pass_num == 5:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                asp_words = [tokens[k] for k in asp]
                if asp_words and asp_words[0].lower() in locative_preps and len(asp_words) > 1:
                    pass_flaws.append((rec_num, f"PREPOSITION_IN_ASPECT: Aspect bắt đầu bằng giới từ: '{asp_words[0]}'"))

        # 6. PASS 6: Kiểm tra Phương tiện giao thông & Con người làm Aspect (Entity Leakage)
        elif pass_num == 6:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                asp_str = ' '.join(tokens[k] for k in asp).lower()
                if asp_str in vehicles:
                    pass_flaws.append((rec_num, f"VEHICLE_AS_ASPECT: Phương tiện bị gán nhầm làm aspect: '{asp_str}'"))
                if asp_str in people_roles:
                    pass_flaws.append((rec_num, f"PEOPLE_AS_ASPECT: Con người/vai vế bị gán nhầm làm aspect: '{asp_str}'"))

        # 7. PASS 7: Kiểm tra Phạm vi Địa lý TP.HCM (Geographic Scope)
        elif pass_num == 7:
            if triplets:  # Chỉ kiểm tra những mẫu CHƯA bị REJECT
                m = provinces_regex.search(text)
                if m:
                    text_lower = text.lower()
                    other_matches = [
                        match.group(0) for match in provinces_regex.finditer(text)
                        if not (match.group(0).lower() == 'hà nội' and ('xa lộ hà nội' in text_lower or 'triều cường ở tphcm' in text_lower))
                        and not (match.group(0).lower() == 'hậu giang' and ('sân bay' in text_lower or 'quận 6' in text_lower or 'đường hậu giang' in text_lower or 'đường cửu long' in text_lower))
                        and not (match.group(0).lower() == 'bình phước' and 'hiệp bình phước' in text_lower)
                        and not (match.group(0).lower() == 'thái bình' and 'nguyễn thái bình' in text_lower)
                    ]
                    if other_matches:
                        pass_flaws.append((rec_num, f"OUT_OF_SCOPE_SUSPECT: Chứa từ khóa tỉnh ngoài '{other_matches[0]}'"))

        # 8. PASS 8: Thẩm định Tính Nhất quán Sắc thái (Polarity Litmus Test)
        elif pass_num == 8:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                opi_str = ' '.join(tokens[k] for k in opi).lower()
                is_recovery = (
                    'không ngập' in opi_str 
                    or ('hết ngập' in opi_str and 'chưa' not in opi_str and 'không' not in opi_str) 
                    or ('thông thoáng' in opi_str and 'không thông thoáng' not in opi_str)
                    or (('đã rút' in opi_str or 'bắt đầu rút' in opi_str) and 'chưa' not in opi_str and 'không' not in opi_str)
                    or (re.search(r'(?<![t\w])rút nước\b', opi_str) and 'chưa' not in opi_str and 'không' not in opi_str)
                )
                if is_recovery and pol == 'NEG':
                    pass_flaws.append((rec_num, f"POLARITY_MISMATCH: Opinion mang nghĩa phục hồi '{opi_str}' nhưng nhãn là NEG"))

        # 9. PASS 9: Kiểm tra lạm dụng Fallback (Có tên đường cụ thể nhưng lại dùng Fallback TPHCM)
        elif pass_num == 9:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                asp_str = ' '.join(tokens[k] for k in asp).lower()
                # Nếu gán Fallback TP.HCM nhưng trong câu có tên đường cụ thể với từ 'đường'
                if asp_str in {'tp. hồ chí minh', 'tp. hcm', 'tphcm', 'tp hồ chí minh', 'tp hcm', 'thành phố'}:
                    # Tìm xem câu có xuất hiện tên đường không
                    for w_i, w in enumerate(tokens):
                        if w.lower() == 'đường' and w_i + 1 < len(tokens):
                            next_w = tokens[w_i + 1]
                            # Nếu từ sau 'đường' viết hoa chữ cái đầu và không phải từ chung / tên thành phố
                            if next_w[0].isupper() and next_w.lower() not in {
                                'này', 'đó', 'kia', 'nào', 'vừa', 'qua', 'lớn', 
                                'tp', 'tp.', 'tphcm', 'tp.hcm', 'hcm', 'sài', 'hồ',
                                'ngập', 'phố', 'xá', 'hóa', 'thành', 'biến'
                            }:
                                # Có tên đường cụ thể nhưng lại dùng Fallback
                                pass_flaws.append((rec_num, f"SUSPECT_FALLBACK_USAGE: Có tên đường cụ thể '{w} {next_w}...' nhưng dùng Fallback '{asp_str}'"))
                                break

        # 10. PASS 10: Kiểm tra Bare Noun trong Opinion (Pass 4 danh từ trần trụi)
        elif pass_num == 10:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                opi_str = ' '.join(tokens[k] for k in opi).lower()
                if opi_str in {'điểm ngập', 'đoạn ngập', 'vùng ngập', 'tuyến ngập', 'khu vực ngập', 'mực nước'}:
                    pass_flaws.append((rec_num, f"BARE_NOUN_AS_OPINION: Danh từ hiện tượng trần trụi không có tính từ/vị ngữ: '{opi_str}'"))

    if pass_flaws:
        all_pass_success = False
        print(f"❌ PASS {pass_num} PHÁT HIỆN {len(pass_flaws)} LỖI:")
        for r_num, msg in pass_flaws[:10]:
            print(f"   - Record {r_num}: {msg}")
        if len(pass_flaws) > 10:
            print(f"   ... và {len(pass_flaws) - 10} lỗi khác.")
    else:
        print(f"✅ PASS {pass_num} HOÀN THÀNH: 0 LỖI (100% ĐẠT CHUẨN)")

print("\n================================================================================")
if all_pass_success:
    print("XÁC NHẬN CHÍNH THỨC: TẬP DỮ LIỆU ĐẠT CHUẨN 10/10 PASSES VỚI 0 LỖI SAI SÓT!")
    print("DỮ LIỆU ĐÃ SẴN SÀNG ĐỂ ĐƯA VÀO HUẤN LUYỆN HOẶC ĐỐI SOÁT CHỈ SỐ KAPPA.")
else:
    print("KẾT LUẬN: CẦN TIẾP TỤC HIỆU CHỈNH CÁC DÒNG ĐƯỢC CHỈ RA Ở TRÊN!")
print("================================================================================")
