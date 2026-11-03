import sys
import os
import ast
import re

sys.stdout.reconfigure(encoding='utf-8')

locative_preps = {'ở', 'tại', 'trên', 'dưới', 'trong', 'ngoài', 'từ', 'đến', 'gần', 'cạnh', 'bên', 'phía', 'thuộc', 'của'}
vehicles = {'xe', 'xe máy', 'ô tô', 'xe buýt', 'xe tải', 'thuyền', 'ghe', 'ca nô', 'xe gắn máy', 'phương tiện', 'ô-tô', 'xe-máy'}
standalone_puncts = {'.', ',', ';', ':', '!', '?', '…', '...', '”', '\"', '\'', '(', ')', '[', ']', '-', '–', '|'}

def inspect_sub_batch(filepath, start_idx, end_idx):
    if not os.path.exists(filepath):
        print(f"LỖI: Không tìm thấy file dữ liệu tại '{filepath}'")
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        all_lines = [line.strip() for line in f if line.strip()]

    total_records = len(all_lines)
    end_idx = min(end_idx, total_records)
    batch = all_lines[start_idx:end_idx]
    report = []

    for i, line in enumerate(batch):
        rec_num = start_idx + i + 1
        if '####' not in line:
            report.append({
                'rec': rec_num,
                'status': 'FORMAT_ERROR',
                'text': line,
                'triplets': [],
                'flaws': ['Thiếu phân cách ####']
            })
            continue

        text, trip_str = line.split('####')
        tokens = text.split()
        try:
            triplets = ast.literal_eval(trip_str)
        except Exception as e:
            report.append({
                'rec': rec_num,
                'status': 'SYNTAX_ERROR',
                'text': text,
                'triplets': [],
                'flaws': [f'Không thể parse triplets: {e}']
            })
            continue

        # Empty triplet = rejected
        if not triplets:
            report.append({
                'rec': rec_num,
                'status': 'REJECTED_CLEAN',
                'text': text,
                'triplets': [],
                'flaws': []
            })
            continue

        item_triplets = []
        flaws = []
        for t_idx, (asp, opi, pol) in enumerate(triplets):
            asp_words = [tokens[k] for k in asp]
            opi_words = [tokens[k] for k in opi]
            asp_str = ' '.join(asp_words)
            opi_str = ' '.join(opi_words)

            # Check index bounds
            if any(k < 0 or k >= len(tokens) for k in asp + opi):
                flaws.append(f'BOUNDS_ERROR in triplet {t_idx}')
            # Check overlap
            if set(asp).intersection(set(opi)):
                flaws.append(f'OVERLAP in triplet {t_idx}')
            # Check preposition in aspect
            if asp_words and asp_words[0].lower() in locative_preps and len(asp_words) > 1:
                flaws.append(f'PREP in aspect: "{asp_words[0]}"')
            # Check vehicle
            if asp_str.lower() in vehicles:
                flaws.append(f'VEHICLE aspect: "{asp_str}"')
            # Check trailing/leading puncts
            if asp_words and (asp_words[0] in standalone_puncts or asp_words[-1] in standalone_puncts):
                flaws.append(f'PUNCT in aspect: "{asp_str}"')
            if opi_words and (opi_words[0] in standalone_puncts or opi_words[-1] in standalone_puncts):
                flaws.append(f'PUNCT in opinion: "{opi_str}"')

            item_triplets.append({
                'asp': asp_str,
                'asp_idx': asp,
                'opi': opi_str,
                'opi_idx': opi,
                'pol': pol
            })

        report.append({
            'rec': rec_num,
            'status': 'VERIFIED' if not flaws else 'FLAWED',
            'text': text,
            'triplets': item_triplets,
            'flaws': flaws
        })

    return report

if __name__ == '__main__':
    # Hỗ trợ cả 2 dạng:
    # 1. python verify_batch_50.py <start> <end>
    # 2. python verify_batch_50.py <filepath> <start> <end>
    default_fp = r'D:\SE363_RAWDATA\data\validate_label\thuan\phase1.txt'

    if len(sys.argv) == 3:
        fp = default_fp
        start = int(sys.argv[1])
        end = int(sys.argv[2])
    elif len(sys.argv) >= 4:
        fp = sys.argv[1]
        start = int(sys.argv[2])
        end = int(sys.argv[3])
    else:
        print("Sử dụng: python verify_batch_50.py [filepath] <start_idx> <end_idx>")
        sys.exit(1)

    data = inspect_sub_batch(fp, start, end)
    print(f"Kiểm tra File: {fp}")
    print(f"Kiểm tra từ dòng {start+1} đến {end} (Tổng {len(data)} items):")
    flawed_items = [d for d in data if d['status'] in ('FLAWED', 'FORMAT_ERROR', 'SYNTAX_ERROR')]
    reject_items = [d for d in data if d['status'] == 'REJECTED_CLEAN']
    verified_items = [d for d in data if d['status'] == 'VERIFIED']

    print(f"  + Hợp lệ chuẩn xác: {len(verified_items)}")
    print(f"  + Rác/Tỉnh ngoài đã loại (Reject): {len(reject_items)}")
    print(f"  + Có sai sót cần sửa: {len(flawed_items)}")

    if flawed_items:
        print("\nCHI TIẾT SAI SÓT CẦN HIỆU CHỈNH:")
        for it in flawed_items:
            print(f"Dòng {it['rec']}: {it['flaws']}")
            print(f"  Văn bản: {it['text'][:85]}...")
            print(f"  Triplets: {it['triplets']}")
    else:
        print("\n✅ TOÀN BỘ LÔ NÀY HOÀN TOÀN ĐẠT CHUẨN, 0 SAI SÓT!")
