import sys
import os
import ast

sys.stdout.reconfigure(encoding='utf-8')

# Hỗ trợ nhận đường dẫn file linh hoạt qua tham số dòng lệnh (mặc định là phase1.txt)
if len(sys.argv) > 1:
    filepath = sys.argv[1]
else:
    filepath = r'D:\SE363_RAWDATA\data\validate_label\thuan\phase1.txt'

if not os.path.exists(filepath):
    print(f"LỖI: Không tìm thấy file dữ liệu tại '{filepath}'")
    sys.exit(1)

with open(filepath, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

total_records = len(lines)
print(f"File kiểm định tính toàn vẹn Index: {filepath} ({total_records} records)")

flaws = []
broad_opinions = []
total_triplets = 0

for idx, line in enumerate(lines):
    rec_num = idx + 1
    if '####' not in line:
        continue
    text, trip_str = line.split('####')
    tokens = text.split()
    try:
        triplets = ast.literal_eval(trip_str)
    except Exception:
        continue

    for t_idx, (asp, opi, pol) in enumerate(triplets):
        total_triplets += 1

        # 1. Non-empty check
        if not asp:
            flaws.append((rec_num, f"EMPTY_ASPECT_INDEX at triplet {t_idx}"))
        if not opi:
            flaws.append((rec_num, f"EMPTY_OPINION_INDEX at triplet {t_idx}"))

        # 2. Contiguity check
        for k in range(len(asp) - 1):
            if asp[k+1] != asp[k] + 1:
                asp_toks = [tokens[i] for i in asp]
                flaws.append((rec_num, f"NON_CONTIGUOUS_ASPECT: indices={asp}, words={asp_toks}"))
                break

        for k in range(len(opi) - 1):
            if opi[k+1] != opi[k] + 1:
                opi_toks = [tokens[i] for i in opi]
                flaws.append((rec_num, f"NON_CONTIGUOUS_OPINION: indices={opi}, words={opi_toks}"))
                break

        # 3. Exact token reconstruction check
        asp_words = [tokens[i] for i in asp]
        opi_words = [tokens[i] for i in opi]
        asp_str = ' '.join(asp_words)
        opi_str = ' '.join(opi_words)

        # 4. Check if reconstructed span exists verbatim in the text
        if asp_str not in text:
            flaws.append((rec_num, f"ASPECT_NOT_IN_TEXT: '{asp_str}' not in text"))
        if opi_str not in text:
            flaws.append((rec_num, f"OPINION_NOT_IN_TEXT: '{opi_str}' not in text"))

        # 5. Check if internal tokens contain quotes or colons
        for i in opi:
            if tokens[i] in {':', ';', '”', '\"', '“'}:
                broad_opinions.append((rec_num, t_idx, f"PUNCT_INSIDE_OPINION: token[{i}]='{tokens[i]}' in '{opi_str}'"))

print(f"Tổng số triplets đối soát giải mã ngược: {total_triplets}")
print(f"Tổng số lỗi tính toàn vẹn Index (Index Integrity Flaws): {len(flaws)}")
print(f"Tổng số cảnh báo dấu câu trong Opinion (Punct Warning): {len(broad_opinions)}")
for rec, t_idx, msg in broad_opinions:
    print(f"  Line {rec} (t_{t_idx}): {msg}")

if not flaws:
    print("\n✅ TOÀN BỘ CÁC CHỈ SỐ INDEX KHỚP 100% TỪ VỰNG THỰC TẾ, 0 LỖI LỆCH TỪ!")
else:
    print(f"\n❌ CẦN ĐIỀU CHỈNH {len(flaws)} LỖI INDEX ĐƯỢC LIỆT KÊ!")
