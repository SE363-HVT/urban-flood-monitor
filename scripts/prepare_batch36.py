# -*- coding: utf-8 -*-
with open('scratch_batch36_dump.txt', 'r', encoding='utf-8') as f:
    dump_lines = [l.strip() for l in f if l.strip()]

with open('scratch_batch36_tokens.txt', 'r', encoding='utf-8') as f:
    token_lines = [l.strip() for l in f if l.strip()]

with open('scratch_batch36_review.txt', 'w', encoding='utf-8') as f:
    for i, (d, t) in enumerate(zip(dump_lines, token_lines)):
        f.write(f"=== Record {3501 + i} ===\n")
        f.write(f"Dump: {d}\n")
        f.write(f"Tokens: {t}\n\n")

print("Saved scratch_batch36_review.txt")
