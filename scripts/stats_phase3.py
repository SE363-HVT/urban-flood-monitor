# -*- coding: utf-8 -*-
import ast
from collections import Counter

phase3_path = 'data/validate_label/thuan/phase3.txt'
with open(phase3_path, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Total lines: {len(lines)}")

sent_counts = Counter()
aspect_counts = Counter()
reject_count = 0
valid_triplet_count = 0

for line in lines:
    text, trips_str = line.split('####')
    trips = ast.literal_eval(trips_str)
    if not trips:
        reject_count += 1
    else:
        tokens = text.split()
        for asp, opi, sent in trips:
            valid_triplet_count += 1
            sent_counts[sent] += 1
            asp_text = ' '.join(tokens[i] for i in asp)
            aspect_counts[asp_text] += 1

print(f"Reject records (####[]): {reject_count} ({reject_count/len(lines)*100:.2f}%)")
print(f"Records with triplets: {len(lines) - reject_count} ({(len(lines) - reject_count)/len(lines)*100:.2f}%)")
print(f"Total triplets: {valid_triplet_count}")
print(f"Polarity distribution: {dict(sent_counts)}")
print("Top 15 most frequent aspects:")
for asp, cnt in aspect_counts.most_common(15):
    print(f"  - \"{asp}\": {cnt}")
