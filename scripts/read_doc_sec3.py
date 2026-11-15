import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('documents/BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md', 'r', encoding='utf-8') as f:
    text = f.read()

s = text.find("## 🎯 III. QUY CHUẨN VÀNG VỀ ASPECT")
e = text.find("## 💬 IV.")
print(text[s:e])
