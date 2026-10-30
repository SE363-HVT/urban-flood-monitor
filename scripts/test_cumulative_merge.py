# -*- coding: utf-8 -*-
import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Giả lập 3 nguồn dữ liệu theo đúng schema thực tế của hệ thống
now = int(time.time())

# Nguồn 1: Google RSS (3 bài)
google_events = [
    {
        "id": "g_1", "canonical_id": "news_tuoitre_1", "platform": "news",
        "title": "Đường Nguyễn Văn Quá ngập sâu sau mưa lớn", "text": "Đường Nguyễn Văn Quá ngập sâu sau mưa lớn",
        "create_time": now - 1800, "timestamp": now - 1800,
        "location": {"street": "Nguyễn Văn Quá", "ward": "Đông Hưng Thuận", "lat": 10.84, "lon": 106.62},
        "crawler_source": "live_free_social_crawler"
    },
    {
        "id": "g_2", "canonical_id": "news_thanhnien_2", "platform": "news",
        "title": "Kẹt xe bì bõm tại ngã tư Thủ Đức", "text": "Kẹt xe bì bõm tại ngã tư Thủ Đức",
        "create_time": now - 3600, "timestamp": now - 3600,
        "location": {"street": "Võ Văn Ngân", "ward": "Linh Chiểu", "lat": 10.85, "lon": 106.77},
        "crawler_source": "live_free_social_crawler"
    },
    {
        "id": "g_3", "canonical_id": "tiktok_vid_3", "platform": "tiktok",
        "title": "Bến Bình Đông ngập lút bánh xe", "text": "Bến Bình Đông ngập lút bánh xe",
        "create_time": now - 7200, "timestamp": now - 7200,
        "location": {"street": "Bến Bình Đông", "ward": "Phường 14", "lat": 10.74, "lon": 106.65},
        "crawler_source": "live_free_social_crawler"
    }
]

# Nguồn 2: Bing RSS (2 bài)
bing_events = [
    {
        "id": "b_1", "canonical_id": "news_bing_4", "platform": "news",
        "title": "Đường Ung Văn Khiêm ngập nửa mét chiều nay", "text": "Đường Ung Văn Khiêm ngập nửa mét chiều nay",
        "create_time": now - 9000, "timestamp": now - 9000,
        "location": {"street": "Ung Văn Khiêm", "ward": "Phường 25", "lat": 10.80, "lon": 106.71},
        "crawler_source": "live_free_social_crawler"
    },
    {
        "id": "b_2", "canonical_id": "facebook_bing_5", "platform": "facebook",
        "title": "Người dân dắt bộ xe chết máy ở Phan Huy Ích", "text": "Người dân dắt bộ xe chết máy ở Phan Huy Ích",
        "create_time": now - 18000, "timestamp": now - 18000,
        "location": {"street": "Phan Huy Ích", "ward": "Phường 14", "lat": 10.83, "lon": 106.63},
        "crawler_source": "live_free_social_crawler"
    }
]

# Nguồn 3: Apify Deep Crawl (3 bài)
apify_events = [
    {
        "id": "ap_1", "canonical_id": "apify_fb_6", "platform": "facebook",
        "title": "Trần Xuân Soạn nước ngập tràn bờ kè", "text": "Trần Xuân Soạn nước ngập tràn bờ kè",
        "create_time": now - 5000, "timestamp": now - 5000,
        "location": {"street": "Trần Xuân Soạn", "ward": "Tân Hưng", "lat": 10.75, "lon": 106.70},
        "crawler_source": "apify_facebook"
    },
    {
        "id": "ap_2", "canonical_id": "apify_tiktok_7", "platform": "tiktok",
        "title": "Kinh Dương Vương biến thành sông", "text": "Kinh Dương Vương biến thành sông",
        "create_time": now - 40000, "timestamp": now - 40000,
        "location": {"street": "Kinh Dương Vương", "ward": "An Lạc", "lat": 10.74, "lon": 106.61},
        "crawler_source": "apify_tiktok"
    },
    {
        "id": "ap_3", "canonical_id": "news_tuoitre_1", "platform": "news",  # Trùng ID với google_events[0]
        "title": "Đường Nguyễn Văn Quá ngập sâu sau mưa lớn", "text": "Đường Nguyễn Văn Quá ngập sâu sau mưa lớn",
        "create_time": now - 1800, "timestamp": now - 1800,
        "location": {"street": "Nguyễn Văn Quá", "ward": "Đông Hưng Thuận", "lat": 10.84, "lon": 106.62},
        "crawler_source": "apify_facebook"
    }
]

from dashboard.server import merge_and_deduplicate_events

# 1. Bước 1: Freecrawl nhận Google (3) + Bing (2) = 5 tin
step1 = merge_and_deduplicate_events(google_events, bing_events)
print(f"Bước 1 (Google + Bing): {len(step1)} tin (Kỳ vọng: 5)")
assert len(step1) == 5, f"Lỗi: Kỳ vọng 5 tin nhưng nhận được {len(step1)}"

# 2. Bước 2: User bấm Cào Apify -> Bắn thêm 3 tin (trong đó 1 tin trùng ID) -> Kỳ vọng: 5 + 2 = 7 tin
step2 = merge_and_deduplicate_events(step1, apify_events)
print(f"Bước 2 (Gộp thêm Apify): {len(step2)} tin (Kỳ vọng: 7)")
assert len(step2) == 7, f"Lỗi: Kỳ vọng 7 tin nhưng nhận được {len(step2)}"

# 3. Bước 3: Đợt cào Apify tiếp theo bị lỗi (0 tin mới) -> Kỳ vọng: vẫn giữ nguyên 7 tin, TUYỆT ĐỐI KHÔNG BỊ XÓA/RESET
step3 = merge_and_deduplicate_events(step2, [])
print(f"Bước 3 (Apify lần sau 0 tin): {len(step3)} tin (Kỳ vọng: vẫn đủ 7 tin)")
assert len(step3) == 7, f"Lỗi: Bị reset hoặc mất tin khi Apify cào được 0 bài!"

# 4. Kiểm tra phân loại 3 tầng độ tươi (Freshness 3-tier):
print("\nKiểm tra 3 tầng độ tươi:")
for ev in step2:
    print(f" - [{ev.get('status_tag', 'Chưa gắn')}] {ev.get('platform').upper()}: {ev.get('title')} ({ev.get('relative_time')})")

print("\n>>> TẤT CẢ KIỂM THỬ GỘP CỘNG DỒN ĐỀU VƯỢT QUA 100%! <<<")
