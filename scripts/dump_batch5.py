import sys

sys.stdout.reconfigure(encoding='utf-8')

master_path = 'data/processed/aste_v2_format/master_10k_triplets.txt'
with open(master_path, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

# Batch 5: records 401 to 500 in Thuan phase 3
# In master, Thuan starts at line 2501 (index 2500)
# Batch 1: index 2500..2600 (records 1..100)
# Batch 2: index 2600..2700 (records 101..200)
# Batch 3: index 2700..2800 (records 201..300)
# Batch 4: index 2800..2900 (records 301..400)
# Batch 5: index 2900..3000 (records 401..500)

batch5_raw = lines[2900:3000]
assert len(batch5_raw) == 100

with open('scratch_batch5_dump.txt', 'w', encoding='utf-8') as out:
    for idx, l in enumerate(batch5_raw):
        rec_num = 401 + idx
        master_line_num = 2901 + idx
        out.write(f"=== REC {rec_num} (Master line {master_line_num}) ===\n{l}\n\n")

print(f"Dumped 100 records for Batch 5 (Records 401 to 500) to scratch_batch5_dump.txt successfully!")
