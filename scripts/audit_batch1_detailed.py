import sys
import os
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [f.readline().strip() for _ in range(100)]

issues = []
for idx, line in enumerate(lines, 1):
    parts = line.split('####')
    text = parts[0].strip()
    trips = ast.literal_eval(parts[1].strip())
    tokens = text.split()
    
    # 1. Check bare triều cường
    for asp_idx, opi_idx, pol in trips:
        asp_words = [tokens[i] for i in asp_idx]
        asp_text = ' '.join(asp_words).lower()
        if asp_text in ['triều cường', 'đỉnh triều', 'triều cao']:
            issues.append((idx, f'BARE_TIDAL: Aspect is bare "{asp_text}" at {asp_idx}'))
            
        # 2. Check causative verbs in opinion
        opi_words = [tokens[i] for i in opi_idx]
        if opi_words and opi_words[0].lower() in ['gây', 'làm']:
            issues.append((idx, f'CAUSATIVE_OPINION: Opinion starts with "{opi_words[0]}" at {opi_idx}'))
            
        # 3. Check bare noun opinion
        if ' '.join(opi_words).lower() in ['điểm ngập', 'đoạn ngập', 'khu vực ngập']:
            issues.append((idx, f'BARE_NOUN_OPINION: Opinion is bare noun at {opi_idx}'))

    # 4. Check multi-level duplication
    opi_map = {}
    for asp_idx, opi_idx, pol in trips:
        asp = ' '.join(tokens[i] for i in asp_idx)
        opi_key = tuple(opi_idx)
        if opi_key not in opi_map:
            opi_map[opi_key] = []
        opi_map[opi_key].append(asp)
    for opi_key, asps in opi_map.items():
        if len(asps) > 1:
            issues.append((idx, f'SHARED_OPINION: Same opinion {list(opi_key)} tagged for multiple aspects: {asps}'))

for rec_idx, desc in issues:
    print(f'Rec {rec_idx}: {desc}')
print(f'Total issues detected: {len(issues)}')
