import sys, os, ast, re

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase1.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

print(f'=== TOTAL LINES: {len(lines)} ===')

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
    '#trieubds', '#nhabinhtan', '#kienthucnhadat', '#bds', '#xecongnghe'
]

bare_aspect_words = ['triều cường', 'đỉnh triều', 'triều cao', 'mặt đường', 'đoạn đường', 'con đường', 'dòng nước']

out_of_scope_list = []
commercial_list = []
bare_aspect_list = []
duplicate_opinion_list = []
fallback_with_street_list = []

for idx, line in enumerate(lines, 1):
    tokens_str, triplets_str = line.split('####')
    tokens = tokens_str.split()
    triplets = ast.literal_eval(triplets_str)
    text_lower = tokens_str.lower()
    
    # 1. Out of scope check
    for kw in out_of_scope_keywords:
        if kw in text_lower:
            if triplets:
                out_of_scope_list.append((idx, kw, tokens_str, triplets))
            break
            
    # 2. Commercial check
    for kw in commercial_keywords:
        if kw in text_lower and triplets:
            commercial_list.append((idx, kw, tokens_str, triplets))
            break
            
    # 3. Bare aspect check
    for asp, opi, pol in triplets:
        asp_text = ' '.join([tokens[i] for i in asp])
        if asp_text.lower() in bare_aspect_words:
            bare_aspect_list.append((idx, asp_text, asp, tokens_str, triplets))
            
    # 4. Multi-level duplication check (same opinion on street and city/ward)
    if len(triplets) > 1:
        opinions = [tuple(t[1]) for t in triplets]
        if len(opinions) != len(set(opinions)):
            duplicate_opinion_list.append((idx, tokens_str, triplets))

print(f'\n--- SUMMARY ---')
print(f'1. Out of Scope records with triplets: {len(out_of_scope_list)}')
for idx, kw, text, trips in out_of_scope_list:
    print(f'   Rec {idx} (kw: {kw}): {text[:70]}...')

print(f'\n2. Commercial records with triplets: {len(commercial_list)}')
for idx, kw, text, trips in commercial_list:
    print(f'   Rec {idx} (kw: {kw}): {text[:70]}...')

print(f'\n3. Bare Aspect records (triều cường / mặt đường / ...): {len(bare_aspect_list)}')
for idx, asp_text, asp, text, trips in bare_aspect_list:
    print(f'   Rec {idx} (asp: "{asp_text}"): {text[:70]}...')

print(f'\n4. Multi-level Duplication (identical opinion span assigned multiple times): {len(duplicate_opinion_list)}')
for idx, text, trips in duplicate_opinion_list:
    print(f'   Rec {idx}: {len(trips)} triplets | {text[:70]}...')
