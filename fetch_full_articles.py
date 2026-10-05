import json
import os
from googlenewsdecoder import gnewsdecoder
from newspaper import Article

RAW_FILE = os.path.join("data", "raw", "dataset_google_news.json")
OUTPUT_FILE = os.path.join("data", "raw", "dataset_google_news_full.json")

with open(RAW_FILE, "r", encoding="utf-8") as f:
    items = json.load(f)

full_articles = []
print(f"Bắt đầu bóc tách nội dung từ {len(items)} bài báo...")

# Bạn có thể bỏ [:30] để cào toàn bộ danh sách
for idx, item in enumerate(items, start=1):
    rss_link = item.get("link")

    if not rss_link:
        continue

    try:
        # 1. Giải mã link Google News sang link báo gốc
        decoded_res = gnewsdecoder(rss_link)
        decoded_url = (
            decoded_res.get("decoded_url")
            if isinstance(decoded_res, dict)
            else decoded_res
        )

        if not decoded_url:
            continue

        # 2. Tải và bóc tách nội dung trang báo
        article = Article(decoded_url, language="vi")
        article.download()
        article.parse()

        text = article.text.strip()
        if len(text) > 100:
            full_articles.append(
                {
                    "title": item.get("title"),
                    "url": decoded_url,
                    "published": item.get("published"),
                    "source": item.get("source"),
                    "text": text,
                }
            )
            print(f"[{idx}] Thành công: {item.get('title')[:45]}...")
    except Exception as e:
        print(f"[{idx}] Bỏ qua bài lỗi: {e}")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(full_articles, f, ensure_ascii=False, indent=2)

print(
    f"\nHoàn tất! Đã lưu {len(full_articles)} bài viết chi tiết vào {OUTPUT_FILE}"
)