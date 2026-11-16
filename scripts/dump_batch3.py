import sys

sys.stdout.reconfigure(encoding='utf-8')

master_path = 'data/processed/aste_v2_format/master_10k_triplets.txt'
with open(master_path, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

# Batch 3: records 201 to 300 in Thuan phase 3
# In master, Thuan starts at line 2501 (index 2500)
# Batch 1: index 2500..2600 (records 1..100)
# Batch 2: index 2600..2700 (records 101..200)
# Batch 3: index 2700..2800 (records 201..300)

batch3_raw = lines[2700:2800]
assert len(batch3_raw) == 100

with open('scratch_batch3_dump.txt', 'w', encoding='utf-8') as out:
    for idx, l in enumerate(batch3_raw):
        rec_num = 201 + idx
        master_line_num = 2701 + idx
        out.write(f"=== REC {rec_num} (Master line {master_line_num}) ===\n{l}\n\n")

print(f"Dumped 100 records for Batch 3 (Records 201 to 300) to scratch_batch3_dump.txt successfully!")
