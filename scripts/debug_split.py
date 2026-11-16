import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch_batch3_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

for idx, b in enumerate(blocks):
    rec_num = 201 + idx
    if 270 <= rec_num <= 280:
        print(f"--- Block {rec_num} ---")
        print(b[:150])
        lines = b.split('\n')
        for l in lines[1:]:
            if '####' in l:
                text, trip_str = l.split('####', 1)
                print(f"  trip_str: {trip_str[:50]}")
            else:
                print(f"  NO ####: {l[:50]}")
