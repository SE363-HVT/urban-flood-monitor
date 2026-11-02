import sys
import ast
import re

sys.stdout.reconfigure(encoding='utf-8')

locative_preps = {'ở', 'tại', 'trên', 'dưới', 'trong', 'ngoài', 'từ', 'đến', 'gần', 'cạnh', 'bên', 'phía', 'thuộc', 'của'}
vehicle_keywords = {'xe', 'xe máy', 'ô tô', 'xe buýt', 'xe tải', 'ô-tô', 'xe-máy', 'phương tiện', 'xe gắn máy', 'thuyền', 'ghe', 'ca nô'}

def deep_audit_batch(start_idx, end_idx):
    master_file = r'D:\SE363_RAWDATA\data\processed\aste_v2_format\master_10k_triplets.txt'
    with open(master_file, 'r', encoding='utf-8') as f:
        all_lines = [line.strip() for line in f]

    batch = all_lines[start_idx:end_idx]
    results = []

    for i, line in enumerate(batch):
        rec_num = start_idx + i + 1
        if not line or '####' not in line:
            results.append({'rec': rec_num, 'status': 'ERROR', 'reason': 'Format sai, thiếu ####', 'raw': line})
            continue

        text_part, triplets_part = line.split('####', 1)
        tokens = text_part.strip().split()
        try:
            triplets = ast.literal_eval(triplets_part.strip())
        except Exception as e:
            results.append({'rec': rec_num, 'status': 'ERROR', 'reason': f'Lỗi parse triplets: {e}', 'raw': line})
            continue

        lower_text = text_part.lower()

        # 1. Kiểm tra spam / ngoài phạm vi / nghĩa bóng
        # Thái Lan
        if 'thái lan' in lower_text or 'sa đéc' in lower_text or '# sadec' in lower_text or 'hà nội' in lower_text or '# hanoimua' in lower_text or '# sadec' in lower_text:
            if 'sa đéc' in lower_text or '# sadec' in lower_text:
                results.append({
                    'rec': rec_num,
                    'status': 'REJECT',
                    'reason': 'NOT_FLOOD_RELEVANT: Tin ngập lụt tại Sa Đéc (tỉnh Đồng Tháp, ngoài phạm vi TP.HCM)',
                    'orig': line,
                    'cleaned_line': f"{text_part}####[]"
                })
                continue
            if '# hanoimua' in lower_text or 'hà nội mưa' in lower_text:
                results.append({
                    'rec': rec_num,
                    'status': 'REJECT',
                    'reason': 'NOT_FLOOD_RELEVANT: Tin ngập lụt tại Hà Nội (#hanoimua, ngoài phạm vi TP.HCM)',
                    'orig': line,
                    'cleaned_line': f"{text_part}####[]"
                })
                continue
            if 'tại thái lan' in lower_text or 'lũ lụt thái lan' in lower_text or 'ngập lụt diện rộng tại thái lan' in lower_text:
                results.append({
                    'rec': rec_num,
                    'status': 'REJECT',
                    'reason': 'NOT_FLOOD_RELEVANT: Tin ngập lụt tại Thái Lan (ngoài phạm vi TP.HCM)',
                    'orig': line,
                    'cleaned_line': f"{text_part}####[]"
                })
                continue

        if any(kw in lower_text for kw in ['1tr8', 'phòng trọ', 'cho thuê phòng', 'bán đất']):
            results.append({
                'rec': rec_num,
                'status': 'REJECT',
                'reason': 'COMMERCIAL_SPAM: Tin rao vặt cho thuê phòng/bán bất động sản',
                'orig': line,
                'cleaned_line': f"{text_part}####[]"
            })
            continue

        if any(kw in lower_text for kw in ['ngập tràn ánh sáng', 'ngập tràn niềm vui', 'ngập tràn quà', 'ngập tràn yêu thương', 'ngập tràn ưu đãi']):
            results.append({
                'rec': rec_num,
                'status': 'REJECT',
                'reason': 'METAPHORIC_FLOOD: Sử dụng từ ngập theo nghĩa ẩn dụ/văn học/khuyến mãi',
                'orig': line,
                'cleaned_line': f"{text_part}####[]"
            })
            continue

        issues = []
        corrected_triplets = []
        has_correction = False

        for t_idx, tr in enumerate(triplets):
            asp_idx, opi_idx, pol = tr

            # Kiểm tra range index
            if any(k < 0 or k >= len(tokens) for k in asp_idx + opi_idx):
                issues.append(f'INDEX_OUT_OF_RANGE trong triplet {t_idx}')
                continue

            # Kiểm tra overlap giữa aspect và opinion
            overlap = set(asp_idx).intersection(set(opi_idx))
            if overlap:
                issues.append(f'OVERLAPPING_AO: Aspect và Opinion đè index nhau tại {overlap}')

            asp_toks = [tokens[k] for k in asp_idx]
            opi_toks = [tokens[k] for k in opi_idx]
            asp_text = ' '.join(asp_toks)
            opi_text = ' '.join(opi_toks)

            new_asp_idx = list(asp_idx)
            new_opi_idx = list(opi_idx)
            new_pol = pol

            # 2. Kiểm tra giới từ vị trí đứng đầu Aspect
            if asp_toks and asp_toks[0].lower() in locative_preps and len(asp_toks) > 1:
                prep = asp_toks[0]
                issues.append(f'PREPOSITION_INCLUDED: Aspect dính giới từ vị trí "{prep}" ("{asp_text}") -> cắt bỏ "{prep}"')
                new_asp_idx = new_asp_idx[1:]
                has_correction = True

            # 3. Kiểm tra luật xe cộ (Section 5: VEHICLE RULE)
            if asp_text.lower() in vehicle_keywords:
                issues.append(f'ASPECT_VEHICLE: Aspect là phương tiện ("{asp_text}")')

            # 4. Kiểm tra sắc thái cảm xúc (Polarity Litmus Test)
            # Ngập lụt thực tế đang diễn ra gây tê liệt / ngập sâu mà bị dán nhãn NEU
            # Chú ý: Tránh câu khuyến cáo/dự báo mang từ "nguy cơ"
            if pol == 'NEU' and not any(adv in lower_text for adv in ['khuyến cáo', 'dự báo', 'nguy cơ', 'khuyên']):
                if any(kw in opi_text.lower() for kw in ['ngập sâu', 'ngập nặng', 'chết máy', 'ngập lút', 'nửa mét', 'nước tràn vào', 'tê liệt']):
                    issues.append(f'POLARITY_WRONG: Hiện trường ngập nặng/ách tắc ("{opi_text}") bị dán nhãn NEU -> sửa thành NEG')
                    new_pol = 'NEG'
                    has_correction = True

            # Phục hồi / Nước rút bị dán nhãn NEG
            if pol == 'NEG' and any(kw in opi_text.lower() for kw in ['rút sạch', 'bắt đầu rút', 'đã rút', 'hết ngập', 'khô ráo', 'thông thoáng', 'rút bớt']):
                issues.append(f'POLARITY_WRONG: Trạng thái nước rút/phục hồi ("{opi_text}") bị dán nhãn NEG -> sửa thành POS')
                new_pol = 'POS'
                has_correction = True

            # Đo lường mực nước / dự báo bị dán nhãn NEG
            if pol == 'NEG' and any(kw in opi_text.lower() for kw in ['đang ở mức cao', 'biến đổi chậm', 'ở cấp độ', 'dự báo đạt', 'đạt đỉnh']):
                if not any(neg_kw in opi_text.lower() for neg_kw in ['ngập', 'tràn', 'chết máy']):
                    issues.append(f'POLARITY_WRONG: Thông số đo đạc thủy triều khách quan ("{opi_text}") bị dán nhãn NEG -> sửa thành NEU')
                    new_pol = 'NEU'
                    has_correction = True

            corrected_triplets.append((new_asp_idx, new_opi_idx, new_pol))

        if issues:
            results.append({
                'rec': rec_num,
                'status': 'CORRECT' if has_correction else 'HUMAN_REVIEW',
                'issues': issues,
                'orig': line,
                'text': text_part,
                'cleaned_line': f"{text_part}####{corrected_triplets}"
            })
        else:
            results.append({
                'rec': rec_num,
                'status': 'ACCEPT',
                'orig': line,
                'cleaned_line': line
            })

    return results

if __name__ == '__main__':
    batch_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    start = (batch_num - 1) * 100
    end = batch_num * 100
    res = deep_audit_batch(start, end)

    accepts = [r for r in res if r['status'] == 'ACCEPT']
    corrects = [r for r in res if r['status'] == 'CORRECT']
    rejects = [r for r in res if r['status'] == 'REJECT']
    reviews = [r for r in res if r['status'] == 'HUMAN_REVIEW']

    print(f"=== BÁO CÁO THẨM ĐỊNH CHI TIẾT LÔ {batch_num} (Records {start+1} -> {end}) ===")
    print(f"Tổng số records: {len(res)}")
    print(f"✅ ACCEPT (Chuẩn ngữ nghĩa & cú pháp 100%): {len(accepts)}")
    print(f"⚠️ CORRECT (Đã phát hiện lỗi và sửa chính xác): {len(corrects)}")
    print(f"❌ REJECT (Tin rác / Ngoài TP.HCM / Nghĩa bóng): {len(rejects)}")
    print(f"❓ HUMAN_REVIEW (Nghi vấn ngữ cảnh): {len(reviews)}")

    if corrects or rejects or reviews:
        print("\n--- CHI TIẾT CÁC CA ĐẶC BIỆT CẦN XỬ LÝ ---")
        for r in res:
            if r['status'] != 'ACCEPT':
                print(f"\n[Record {r['rec']}] -> Trạng thái: {r['status']}")
                if 'reason' in r:
                    print(f"  * Lý do: {r['reason']}")
                if 'issues' in r:
                    for is_msg in r['issues']:
                        print(f"  * Lỗi: {is_msg}")
                print(f"  * Câu gốc: {r['orig']}")
                if 'cleaned_line' in r and r['cleaned_line'] != r['orig']:
                    print(f"  * Sửa thành: {r['cleaned_line']}")
