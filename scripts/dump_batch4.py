import sys

sys.stdout.reconfigure(encoding='utf-8')

master_path = 'data/processed/aste_v2_format/master_10k_triplets.txt'
with open(master_path, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

# Batch 4: records 301 to 400 in Thuan phase 3
# In master, Thuan starts at line 2501 (index 2500)
# Batch 1: index 2500..2600 (records 1..100)
# Batch 2: index 2600..2700 (records 101..200)
# Batch 3: index 2700..2800 (records 201..300)
# Batch 4: index 2800..2900 (records 301..400)

batch4_raw = lines[2800:2900]
assert len(batch4_raw) == 100

with open('scratch_batch4_dump.txt', 'w', encoding='utf-8') as out:
    for idx, l in enumerate(batch4_raw):
        rec_num = 301 + idx
        master_line_num = 2801 + idx
        out.write(f"=== REC {rec_num} (Master line {master_line_num}) ===\n{l}\n\n")

print(f"Dumped 100 records for Batch 4 (Records 301 to 400) to scratch_batch4_dump.txt successfully!")
