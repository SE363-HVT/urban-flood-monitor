import json
import os
import urllib.parse
import feedparser

# Thư mục đích theo cấu trúc của project
OUTPUT_DIR = os.path.join("data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "dataset_google_news.json")

queries = [
    '"ngập" "TPHCM"',
    '"triều cường đạt đỉnh" "TPHCM"',
    '"xe chết máy" "ngập" "Sài Gòn"',
    '"ngập sâu" ("Thủ Đức" OR "Quận 7" OR "Bình Thạnh")',
    '"Trần Xuân Soạn" OR "Quốc Hương" OR "Tô Ngọc Vân" ngập',
]

results = []

for q in queries:
    print(f"Đang cào: {q}...")
    encoded_q = urllib.parse.quote(q)
    rss_url = (
        f"https://news.google.com/rss/search?q={encoded_q}&hl=vi&gl=VN&ceid=VN:vi"
    )
    feed = feedparser.parse(rss_url)

    for entry in feed.entries:
        results.append(
            {
                "query": q,
                "title": getattr(entry, "title", ""),
                "link": getattr(entry, "link", ""),
                "published": getattr(entry, "published", ""),
                "summary": getattr(entry, "summary", ""),
                "source": entry.source.title if hasattr(entry, "source") else "",
            }
        )

# Khử trùng lặp theo URL bài viết
unique_results = list({item["link"]: item for item in results if item["link"]}.values())

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(unique_results, f, ensure_ascii=False, indent=2)

print(f"\n Hoàn tất! Đã lưu {len(unique_results)} tin tức vào: {OUTPUT_FILE}")