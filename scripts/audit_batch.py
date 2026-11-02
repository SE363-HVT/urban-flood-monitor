import sys
import json
import ast
import re

sys.stdout.reconfigure(encoding='utf-8')

def audit_range(start_idx, end_idx):
    master_file = r'D:\SE363_RAWDATA\data\processed\aste_v2_format\master_10k_triplets.txt'
    with open(master_file, 'r', encoding='utf-8') as f:
        all_lines = [line.strip() for line in f]

    batch = all_lines[start_idx:end_idx]
    locative_preps = {'ở', 'tại', 'trên', 'dưới', 'trong', 'ngoài', 'từ', 'đến', 'gần', 'cạnh', 'bên', 'phía', 'thuộc', 'của'}
    vehicle_keywords = {'xe', 'xe máy', 'ô tô', 'xe buýt', 'xe tải', 'ô-tô', 'xe-máy', 'phương tiện', 'xe gắn máy'}

    results = []

    for i, line in enumerate(batch):
        rec_num = start_idx + i + 1
        if not line or '####' not in line:
            results.append({'rec': rec_num, 'status': 'ERROR', 'reason': 'Malformatted line', 'raw': line})
            continue

        text_part, triplets_part = line.split('####', 1)
        tokens = text_part.strip().split()
        try:
            triplets = ast.literal_eval(triplets_part.strip())
        except Exception as e:
            results.append({'rec': rec_num, 'status': 'ERROR', 'reason': f'Cannot parse triplets: {e}', 'raw': line})
            continue

        lower_text = text_part.lower()

        # Check spam or out of scope
        if 'thái lan' in lower_text:
            results.append({'rec': rec_num, 'status': 'REJECT', 'reason': 'Tin ngập lụt tại Thái Lan (ngoài phạm vi TP.HCM)', 'line': line})
            continue
        if any(kw in lower_text for kw in ['1tr8', 'phòng trọ', 'cho thuê phòng', 'bán đất']):
            results.append({'rec': rec_num, 'status': 'REJECT', 'reason': 'Quảng cáo thương mại / thuê phòng trọ', 'line': line})
            continue
        if 'ngập tràn ánh sáng' in lower_text or 'ngập tràn niềm vui' in lower_text or 'ngập tràn quà' in lower_text:
            results.append({'rec': rec_num, 'status': 'REJECT', 'reason': 'Nghĩa bóng / ẩn dụ phi ngập lụt', 'line': line})
            continue

        issues = []
        corrected_triplets = []
        has_correction = False

        for t_idx, tr in enumerate(triplets):
            asp_idx, opi_idx, pol = tr
            # Range check
            if any(k < 0 or k >= len(tokens) for k in asp_idx + opi_idx):
                issues.append(f'INDEX_OUT_OF_RANGE in triplet {t_idx}')
                continue

            asp_toks = [tokens[k] for k in asp_idx]
            opi_toks = [tokens[k] for k in opi_idx]
            asp_text = ' '.join(asp_toks)
            opi_text = ' '.join(opi_toks)

            new_asp_idx = list(asp_idx)
            new_opi_idx = list(opi_idx)
            new_pol = pol

            # 1. Preposition check in aspect
            if asp_toks and asp_toks[0].lower() in locative_preps and len(asp_toks) > 1:
                issues.append(f'PREPOSITION_INCLUDED: aspect dính từ "{asp_toks[0]}" ({asp_text}) -> cắt bỏ')
                new_asp_idx = new_asp_idx[1:]
                has_correction = True

            # 2. Vehicle check
            if asp_text.lower() in vehicle_keywords:
                issues.append(f'ASPECT_VEHICLE: aspect là phương tiện ({asp_text})')

            # 3. Polarity check: Active flood labeled NEU -> should be NEG
            if pol == 'NEU' and any(kw in opi_text.lower() for kw in ['ngập sâu', 'ngập nặng', 'chết máy', 'ngập lút', 'nửa mét', 'nước tràn vào', 'tê liệt', 'ngập đến']):
                issues.append(f'POLARITY_WRONG: ngập nặng/ách tắc dán nhãn NEU ("{opi_text}") -> sửa thành NEG')
                new_pol = 'NEG'
                has_correction = True

            # 4. Polarity check: Recovery labeled NEG -> should be POS
            if pol == 'NEG' and any(kw in opi_text.lower() for kw in ['rút sạch', 'bắt đầu rút', 'đã rút', 'hết ngập', 'khô ráo', 'thông thoáng']):
                issues.append(f'POLARITY_WRONG: phục hồi/nước rút dán nhãn NEG ("{opi_text}") -> sửa thành POS')
                new_pol = 'POS'
                has_correction = True

            corrected_triplets.append((new_asp_idx, new_opi_idx, new_pol))

        if issues:
            results.append({
                'rec': rec_num,
                'status': 'CORRECT' if has_correction else 'HUMAN_REVIEW',
                'issues': issues,
                'orig': line,
                'text': text_part,
                'corrected_line': f"{text_part}####{corrected_triplets}"
            })
        else:
            results.append({'rec': rec_num, 'status': 'ACCEPT', 'orig': line})

    return results

if __name__ == '__main__':
    res = audit_range(0, 100)
    accepts = [r for r in res if r['status'] == 'ACCEPT']
    corrects = [r for r in res if r['status'] == 'CORRECT']
    rejects = [r for r in res if r['status'] == 'REJECT']
    reviews = [r for r in res if r['status'] == 'HUMAN_REVIEW']

    print(f"=== BÁO CÁO AUDIT LÔ 1 (Records 1 -> 100) ===")
    print(f"Tổng số records: {len(res)}")
    print(f"ACCEPT (Chuẩn 100%, giữ nguyên): {len(accepts)}")
    print(f"CORRECT (Cần hiệu chỉnh cú pháp/nhãn/giới từ): {len(corrects)}")
    print(f"REJECT (Rác / Ngoài phạm vi / Ẩn dụ): {len(rejects)}")
    print(f"HUMAN_REVIEW (Cần người quyết định): {len(reviews)}")

    # Check distribution of polarity in batch 1
    pos_samples = []
    neu_samples = []
    for r in res:
        line = r.get('orig') or r.get('line')
        if not line: continue
        txt, trips = line.split('####')
        toks = txt.split()
        for tr in ast.literal_eval(trips):
            if tr[2] == 'POS':
                pos_samples.append((r['rec'], " ".join(toks[k] for k in tr[0]), " ".join(toks[k] for k in tr[1])))
            elif tr[2] == 'NEU':
                neu_samples.append((r['rec'], " ".join(toks[k] for k in tr[0]), " ".join(toks[k] for k in tr[1])))

    print(f"\n[PHÂN BỐ ĐẶC BIỆT]:")
    print(f"- Số mẫu POS (Phục hồi/khen ngợi): {len(pos_samples)}")
    for rec_id, asp, opi in pos_samples[:5]:
        print(f"   + Record {rec_id}: Aspect='{asp}', Opinion='{opi}'")
    print(f"- Số mẫu NEU (Dự báo/thủy văn/hành chính): {len(neu_samples)}")
    for rec_id, asp, opi in neu_samples[:5]:
        print(f"   + Record {rec_id}: Aspect='{asp}', Opinion='{opi}'")

    print("\nChi tiết các ca CORRECT / Cần chỉnh sửa:")
    for r in res:
        if r['status'] != 'ACCEPT':
            print(f"\n[Record {r['rec']}] Trạng thái: {r['status']}")
            if 'reason' in r:
                print(f"  Lý do: {r['reason']}")
            if 'issues' in r:
                for is_msg in r['issues']:
                    print(f"  Vấn đề: {is_msg}")
            if 'orig' in r:
                print(f"  Văn bản gốc: {r['orig']}")
            if 'corrected_line' in r:
                print(f"  Đã sửa thành: {r['corrected_line']}")
