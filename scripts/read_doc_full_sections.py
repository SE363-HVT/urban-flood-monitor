import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('documents/BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md', 'r', encoding='utf-8') as f:
    text = f.read()

def show_section(title, next_title):
    s = text.find(title)
    e = text.find(next_title, s) if next_title else len(text)
    print(text[s:e])

print(">>> SECTION III:")
show_section("## 🎯 III. QUY CHUẨN VÀNG VỀ ASPECT", "## 💬 IV.")

print(">>> SECTION IV:")
show_section("## 💬 IV. QUY CHUẨN VÀNG VỀ OPINION", "## ⚖️ V.")

print(">>> SECTION VI:")
show_section("## 🚫 VI. BỘ LỌC THANH LỌC DỮ LIỆU RÁC", "## 🛠️ VII.")
