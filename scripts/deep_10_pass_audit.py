import sys
import os
import re
import ast

# Đặt mã hóa UTF-8 cho console output
sys.stdout.reconfigure(encoding='utf-8')

file_path = sys.argv[1] if len(sys.argv) > 1 else 'data/validate_label/thuan/phase3.txt'

if not os.path.exists(file_path):
    print(f"File không tồn tại: {file_path}")
    sys.exit(1)

with open(file_path, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

total_records = len(lines)
print(f"File kiểm định: {file_path} (Tổng số records: {total_records})")
print("=" * 80)
print(f"BẮT ĐẦU QUY TRÌNH KIỂM ĐỊNH LẶP ĐI LẶP LẠI 10 LẦN CHO {total_records} RECORDS")
print("NGUYÊN TẮC: READ-ONLY AUDITOR (CHỈ KIỂM ĐỊNH - TUYỆT ĐỐI KHÔNG TỰ SỬA DỮ LIỆU)")
print("=" * 80)

all_pass_success = True

for pass_num in range(1, 11):
    print(f"\n>>> [PASS {pass_num}/10] Đang kiểm tra lần thứ {pass_num}...")
    pass_flaws = []

    for idx, line in enumerate(lines):
        rec_num = idx + 1
        
        # 1. PASS 1: Kiểm tra cấu trúc phân tách ####
        if pass_num == 1:
            if '####' not in line:
                pass_flaws.append((rec_num, "SYNTAX_ERROR: Thiếu dấu phân tách '####'"))
                continue
            parts = line.split('####')
            if len(parts) != 2:
                pass_flaws.append((rec_num, f"SYNTAX_ERROR: Xuất hiện {len(parts)} phần phân tách bởi '####' (yêu cầu đúng 2 phần)"))
                continue
            text, trips_str = parts[0].strip(), parts[1].strip()
            try:
                triplets = ast.literal_eval(trips_str)
                if not isinstance(triplets, list):
                    pass_flaws.append((rec_num, "FORMAT_ERROR: Phần triplet không phải là dạng list []"))
            except Exception as e:
                pass_flaws.append((rec_num, f"PARSE_ERROR: Không parse được chuỗi triplet: {e}"))
            continue

        # Dành cho các Pass từ 2 đến 10:
        parts = line.split('####')
        text, trips_str = parts[0].strip(), parts[1].strip()
        tokens = text.split()
        triplets = ast.literal_eval(trips_str)

        # 2. PASS 2: Kiểm tra tính liên tục của Span (Contiguous Indexing)
        if pass_num == 2:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                for name, sp in [("Aspect", asp), ("Opinion", opi)]:
                    if not sp:
                        continue
                    # Phải là danh sách số nguyên liên tục: sp[k] == sp[0] + k
                    for k in range(len(sp)):
                        if sp[k] != sp[0] + k:
                            pass_flaws.append((rec_num, f"NON_CONTIGUOUS: {name} span không liên tục: {sp}"))
                            break

        # 3. PASS 3: Kiểm tra Span Out of Bounds & Empty Span
        elif pass_num == 3:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                for name, sp in [("Aspect", asp), ("Opinion", opi)]:
                    if not sp:
                        pass_flaws.append((rec_num, f"EMPTY_SPAN: {name} span rỗng trong triplet {t_idx+1}"))
                    for index in sp:
                        if index < 0 or index >= len(tokens):
                            pass_flaws.append((rec_num, f"INDEX_OUT_OF_BOUNDS: {name} index {index} vượt quá độ dài câu ({len(tokens)} tokens)"))

        # 4. PASS 4: Kiểm tra dấu câu dính ở rìa Span (Punctuation Contamination)
        elif pass_num == 4:
            punct_chars = {'.', ',', '!', '?', ';', ':', '...', '"', "'", '“', '”', '(', ')', '[', ']', '{', '}'}
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                # Kiểm tra Aspect
                if asp:
                    first_w = tokens[asp[0]]
                    last_w = tokens[asp[-1]]
                    if first_w in punct_chars or last_w in punct_chars:
                        pass_flaws.append((rec_num, f"PUNCT_IN_ASPECT: Aspect dính dấu câu ở rìa: '{' '.join(tokens[k] for k in asp)}'"))
                # Kiểm tra Opinion
                if opi:
                    first_w = tokens[opi[0]]
                    last_w = tokens[opi[-1]]
                    if first_w in punct_chars or last_w in punct_chars:
                        pass_flaws.append((rec_num, f"PUNCT_IN_OPINION: Opinion dính dấu câu ở rìa: '{' '.join(tokens[k] for k in opi)}'"))

        # 5. PASS 5: Kiểm tra Giới từ / Mạo từ thừa ở đầu Aspect (Preposition Stripping)
        elif pass_num == 5:
            prepositions = {'ở', 'tại', 'đến', 'qua', 'từ', 'trong', 'về', 'khu', 'phía'}
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                if asp:
                    first_w = tokens[asp[0]].lower()
                    if first_w in prepositions and len(asp) > 1:
                        # Ngoại trừ 'khu đô thị', 'khu dân cư' có thể giữ, nhưng 'ở', 'tại', 'từ' tuyệt đối cấm
                        if first_w in {'ở', 'tại', 'từ', 'đến'}:
                            pass_flaws.append((rec_num, f"PREPOSITION_IN_ASPECT: Aspect bắt đầu bằng giới từ: '{first_w}'"))

        # 6. PASS 6: Kiểm tra Polarity Hợp lệ & Nhãn REJECT
        elif pass_num == 6:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                if pol not in {'POS', 'NEG', 'NEU'}:
                    pass_flaws.append((rec_num, f"INVALID_POLARITY: Nhãn cảm xúc '{pol}' không hợp lệ (phải là POS/NEG/NEU)"))

        # 7. PASS 7: Kiểm tra Triplet Trùng lặp hoàn toàn
        elif pass_num == 7:
            seen_triplets = set()
            for t in triplets:
                t_key = (tuple(t[0]), tuple(t[1]), t[2])
                if t_key in seen_triplets:
                    pass_flaws.append((rec_num, f"DUPLICATE_TRIPLET: Trùng lặp hoàn toàn triplet {t}"))
                seen_triplets.add(t_key)

        # 8. PASS 8: Kiểm tra Mâu thuẫn Polarity (Nước rút / Giảm ngập mà gán NEG)
        elif pass_num == 8:
            for t_idx, (asp, opi, pol) in enumerate(triplets):
                opi_str = ' '.join(tokens[k] for k in opi).lower()
                is_recovery = (
                    ('rút' in opi_str and 'không rút' not in opi_str and 'chậm rút' not in opi_str and 'chưa rút' not in opi_str and 'chờ' not in opi_str and 'nước rút' not in opi_str)
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
                                'ngập', 'phố', 'xá', 'hóa', 'thành', 'biến', 'hỗ', 'về', 'nhớ',
                                'ở', 'tại', 'chìm', 'lại', 'nước'
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
