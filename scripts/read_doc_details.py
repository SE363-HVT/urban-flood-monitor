import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('documents/BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Let us print Section III, IV, VI
for sec_name in ["III.", "IV.", "VI."]:
    start = text.find(sec_name)
    end = text.find("## ", start + 1)
    if end == -1: end = len(text)
    print("="*40, sec_name, "="*40)
    print(text[start:end])
