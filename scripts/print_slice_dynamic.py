# -*- coding: utf-8 -*-
with open('scratch_audit_batch_1_12.txt', 'r', encoding='utf-8') as f:
    text = f.read()

entries = text.split('=== REC ')
print(f"Tổng số entries: {len(entries)-1}")

def print_range(start_idx, end_idx):
    for i in range(start_idx, min(end_idx + 1, len(entries))):
        print(f"=== {entries[i].strip()}\n")

if __name__ == '__main__':
    import sys
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 31
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    print_range(start, end)
