import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('documents/BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md', 'r', encoding='utf-8') as f:
    text = f.read()

for term in ['hà nội', 'tỉnh ngoài', 'ngoài phạm vi', 'toàn quốc']:
    pos = 0
    print(f"=== SEARCH: {term} ===")
    while True:
        idx = text.lower().find(term, pos)
        if idx == -1: break
        start = max(0, idx - 150)
        end = min(len(text), idx + 250)
        print(text[start:end])
        print("-" * 50)
        pos = idx + len(term)
