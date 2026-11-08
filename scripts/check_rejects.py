import sys, ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase1.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

out_of_scope_keywords = [
    'hà nội', 'hanoi', 'chương mỹ', 'tứ liên', 'hoàng mai', 'thanh xuân', 'hà đông', 'ihanoi', 'hoài đức',
    'cần thơ', 'cantho', '65cầnthơ', 'chợ bình thủy', 'nguyễn văn cừ',
    'mẹ bồng con', 'vĩnh thanh', 'long khánh', 'dầu giây',
    'cà mau', 'camau', 'sa đéc', 'sadec', 'vĩnh long', 'bến tre', 'trà vinh', 'an giang', 'kiên giang',
    'nông cống', 'nongcong', 'thanh hóa', 'thanhhoa', 'đbscl', 'đồng bằng sông cửu long',
    'gia lai', 'quy nhơn', 'nha trang', 'đà lạt', 'lâm đồng', 'đà nẵng', 'huế', 'thái lan', 'bangkok', 'trung quốc'
]

commercial_keywords = [
    '#huynguyencar', '#chothuexetulaibinhtan', '#otochutin', '#toantrung',
    '#trieubds', '#nhabinhtan', '#kienthucnhadat', '#bds', '#xecongnghe',
    'giải pháp thích ứng', 'bài toán chống ngập không chỉ nằm ở việc',
    'theo dõi diễn biến sụt lún'
]

print("=== OUT OF SCOPE / COMMERCIAL / ABSTRACT CONFERENCE INSPECTION ===")
for idx, line in enumerate(lines, 1):
    tokens_str, triplets_str = line.split('####')
    triplets = ast.literal_eval(triplets_str)
    text_lower = tokens_str.lower()
    
    # Check out of scope
    for kw in out_of_scope_keywords:
        if kw in text_lower and triplets:
            print(f"[REJECT_OUT_OF_SCOPE] Rec {idx} (kw: '{kw}'):")
            print(f"  TEXT: {tokens_str}")
            print(f"  TRIPLETS: {triplets}")
            break
            
    # Check commercial / abstract
    for kw in commercial_keywords:
        if kw in text_lower and triplets:
            print(f"[REJECT_COMMERCIAL_OR_ABSTRACT] Rec {idx} (kw: '{kw}'):")
            print(f"  TEXT: {tokens_str}")
            print(f"  TRIPLETS: {triplets}")
            break
