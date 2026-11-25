# -*- coding: utf-8 -*-
"""
core/config.py - Cấu hình hệ thống Ingestion & Dashboard
Thu thập dữ liệu ngập lụt đô thị gần thời gian thực đa nền tảng:
1. TikTok Video: Video & Hashtag ngập lụt TP.HCM (Tối ưu tốc độ phản hồi ~60s, chống timeout).
2. Facebook: Tìm kiếm bài đăng ngập lụt thời gian thực qua Actor tối ưu chi phí & lọc sạch rác.
"""

import os
from pathlib import Path


def _load_local_env() -> None:
    """Nạp biến môi trường từ file .env ở thư mục gốc (đã được .gitignore) nếu tồn tại."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.is_file():
        return
    try:
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value:
                os.environ.setdefault(key, value)
    except Exception:
        pass


_load_local_env()

# Apify API Token fallback (ưu tiên lấy từ biến môi trường / .env hoặc Dashboard Apify Pool)
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "").strip()

# ==========================================
# 1. Cấu hình Actor cào TikTok Video (Tối ưu phản hồi < 90s, an toàn dưới timeout 300s)
# ==========================================
ACTOR_ID = "clockworks~free-tiktok-scraper"

DEFAULT_HASHTAGS = [
    "ngapsaigon",
    "muangap",
    "trieucuong",
    "saigonngap",
    "trieucuongsaigon",
    "ngaptphcm"
]

DEFAULT_SEARCH_QUERIES = [
    "ngập TPHCM",
    "ngập Sài Gòn",
    "mưa ngập TP.HCM",
    "triều cường Sài Gòn",
    "triều cường TPHCM"
]

# ==========================================
# 2. Cấu hình Actor cào Facebook (Chuyên sâu TP.HCM & Tiết kiệm tối đa)
# ==========================================
FB_ACTOR_ID = "danek~facebook-search-ppr"
FB_SEARCH_PPR_ACTOR_ID = FB_ACTOR_ID
FB_CRAWL_STRATEGY = os.environ.get("FB_CRAWL_STRATEGY", "search")

# 5 Fanpage trọng điểm uy tín tại TP.HCM được chọn lọc
FB_TARGET_PAGES = [
    "https://www.facebook.com/phapluattp.vn",       # Báo Pháp Luật TP.HCM
    "https://www.facebook.com/thanhnien",           # Báo Thanh Niên
    "https://www.facebook.com/nguoilaodong",        # Báo Người Lao Động
    "https://www.facebook.com/congdongvnexpress",   # VnExpress
    "https://www.facebook.com/SGCT1"               # Sài Gòn Của Tôi
]

FB_TARGET_PAGE_IDENTIFIERS = [
    "phapluattp.vn", "thanhnien", "nguoilaodong", "congdongvnexpress", "sgct1",
    "pháp luật tp.hcm", "thanh niên", "người lao động", "vnexpress", "sài gòn của tôi"
]

FB_SEARCH_QUERIES = [
    "triều cường ngập Sài Gòn",
    "mưa ngập TP.HCM",
    "ngập đường Sài Gòn",
    "ngập xe chết máy TPHCM",
    "#ngapsaigon"
]

FB_SEARCH_LOCATIONS = ["Ho Chi Minh City"]
FB_NEWER_THAN_DEFAULT = "48 hours"

# ==========================================
# Cấu hình Server & Cửa sổ thời gian
# ==========================================
DEFAULT_PORT = 8050
DEFAULT_WINDOW_MINUTES = 120
