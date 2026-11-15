import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('documents/BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md', 'r', encoding='utf-8') as f:
    text = f.read()

print("TOTAL LENGTH:", len(text))
for section in text.split("## "):
    header = section.split("\n")[0]
    print(f"SECTION: {header}")
