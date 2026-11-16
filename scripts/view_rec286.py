import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch_batch3_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

for b in blocks:
    if '286' in b[:30]:
        print(b)
