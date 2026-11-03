import sys
import re
import ast

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Semantic boundary markers - where opinion description must stop
STOP_PATTERNS = [
    r'\b(cho biết|chia sẻ|nói|theo|phóng viên|báo|đài|ghi nhận|thông tin từ)\b',
    r'\b(các trường|nhà trường|chính quyền|lực lượng chức năng|cảnh sát|csgt|ubnd|khuyến cáo|đề nghị|yêu cầu)\b',
    r'\b(nhằm|để đảm bảo|để bảo đảm|được biết|dự báo|cảnh báo)\b',
    r'(\( ?ảnh|\( ?nguồn|ảnh :|nguồn :|video :|clip :)',
    r'["“”;:…]'
]

# Patterns for timestamp/date metadata at the tail
TAIL_METADATA_PATTERN = re.compile(
    r',?\s*(sau trận mưa|vào lúc|chiều tối|tối nay|sáng nay|chiều nay|ngày)?\s*\b\d{1,2}\s*/\s*\d{1,2}\b.*$', 
    re.IGNORECASE
)

# Semantic consequence patterns - must describe flood situation/impact
CONSEQUENCE_PATTERNS = [
    r'\b(chết máy|tắt máy|dắt bộ|hỏng xe|hư xe|lút bánh|lút cả bánh)\b',
    r'\b(chật vật|bì bõm|lội nước|lội giữa dòng|vật lộn|té ngã|khó khăn|vất vả|lao đao)\b',
    r'\b(chảy xiết|cuồn cuộn|tràn vào|tràn lên|như thác|biển nước|mênh mông|đen ngòm)\b',
    r'\b(ùn ứ|tê liệt|kẹt xe|ùn tắc|hỗn loạn|tắc nghẽn|nhích từng mét|ken đặc)\b',
    r'\b(ảnh hưởng lớn|ảnh hưởng nghiêm trọng|ảnh hưởng đến|ảnh hưởng việc|đảo lộn|hết sức vất vả)\b'
]

stop_regex = re.compile('|'.join(STOP_PATTERNS), re.IGNORECASE)
cons_regex = re.compile('|'.join(CONSEQUENCE_PATTERNS), re.IGNORECASE)

def process_file(filepath, dry_run=True):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]

    updated_count = 0
    updated_lines = []

    for idx, line in enumerate(lines, 1):
        text, trip_str = line.split('####')
        tokens = text.split()
        triplets = ast.literal_eval(trip_str)
        if not triplets:
            updated_lines.append(line)
            continue

        # Collect all aspect indices in the sentence to avoid any overlap
        all_aspect_indices = set()
        for asp, _, _ in triplets:
            all_aspect_indices.update(asp)

        line_modified = False
        new_triplets = []

        for t_idx, (asp, opi, pol) in enumerate(triplets):
            if not opi:
                new_triplets.append((asp, opi, pol))
                continue

            opi_end = opi[-1]
            # Check if immediately followed by comma
            if opi_end + 1 < len(tokens) and tokens[opi_end + 1] == ',':
                # Look ahead for clause boundary
                end_clause = len(tokens)
                for k in range(opi_end + 2, len(tokens)):
                    if tokens[k] in {'.', '!', '?', '#'} or tokens[k].startswith('#'):
                        end_clause = k
                        break

                clause_tokens = tokens[opi_end + 2 : end_clause]
                clause_text = ' '.join(clause_tokens)

                # Check if stop pattern appears in clause
                stop_m = stop_regex.search(clause_text)
                if stop_m:
                    match_char_start = stop_m.start()
                    sub_prefix = clause_text[:match_char_start].strip()
                    sub_tok_count = len(sub_prefix.split()) if sub_prefix else 0
                    end_clause = opi_end + 2 + sub_tok_count

                # Strip trailing timestamp/date metadata
                cur_extended_str = ' '.join(tokens[opi_end + 2 : end_clause])
                meta_m = TAIL_METADATA_PATTERN.search(cur_extended_str)
                if meta_m:
                    cut_char = meta_m.start()
                    prefix_str = cur_extended_str[:cut_char].strip()
                    end_clause = opi_end + 2 + len(prefix_str.split())

                # Prevent overlap with ANY aspect in the sentence
                for k in range(opi_end + 2, end_clause):
                    if k in all_aspect_indices:
                        end_clause = k
                        break

                # Strip trailing punctuation, symbols, and non-alphanumeric tokens (emojis, puncts)
                while end_clause > opi_end + 2:
                    last_tok = tokens[end_clause - 1]
                    if not any(c.isalnum() for c in last_tok) or last_tok in {',', '.', ';', ':', '!', '?', '”', '"', '-', '…'}:
                        end_clause -= 1
                    else:
                        break

                candidate_slice = tokens[opi_end + 2 : end_clause]
                candidate_str = ' '.join(candidate_slice)

                # Check if the candidate extension contains a genuine consequence/severity description
                if cons_regex.search(candidate_str) and len(candidate_slice) >= 2:
                    new_opi = list(range(opi[0], end_clause))
                    # Sanity check: must never overlap with aspect
                    if not (set(asp) & set(new_opi)):
                        new_triplets.append((asp, new_opi, pol))
                        line_modified = True
                    else:
                        new_triplets.append((asp, opi, pol))
                else:
                    new_triplets.append((asp, opi, pol))
            else:
                new_triplets.append((asp, opi, pol))

        if line_modified:
            updated_count += 1
            updated_lines.append(f"{text}####{new_triplets}")
        else:
            updated_lines.append(line)

    print(f"\n[{filepath}] Total modified lines: {updated_count} / {len(lines)}")
    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            for l in updated_lines:
                f.write(l + '\n')
        print(f"Successfully saved {filepath}!")

if __name__ == '__main__':
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--apply':
        dry_run = False
    
    target_files = ['data/validate_label/thuan/phase1.txt', 'data/validate_label/thuan/phase2.txt']
    if len(sys.argv) > 2:
        target_files = [sys.argv[2]]
        
    for tf in target_files:
        print(f"\n==========================================")
        print(f"PROCESSING: {tf} (dry_run={dry_run})")
        print(f"==========================================")
        process_file(tf, dry_run=dry_run)
