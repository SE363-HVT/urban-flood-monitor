# -*- coding: utf-8 -*-
"""
core/config.py - Cấu hình hệ thống Ingestion & Dashboard
Thu thập dữ liệu ngập lụt đô thị gần thời gian thực đa nền tảng:
1. TikTok Video: Video & Hashtag ngập lụt TP.HCM (Tối ưu truy vấn tốc độ cao chống timeout).
2. Facebook: Tìm kiếm bài đăng ngập lụt thời gian thực qua Actor tối ưu chi phí & lọc sạch rác.
"""

import os

# Apify API Token - Sử dụng token mới được cung cấp (Free tier có sẵn $5 credit)
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "apify_api_wTDd6uCOPAyo3sDLx864GjAmUflbBh1Ff9o0")

# ==========================================
# 1. Cấu hình Actor cào TikTok Video (Tối ưu tốc độ phản hồi < 45s, chống timeout 300s)
# ==========================================
ACTOR_ID = "clockworks~free-tiktok-scraper"

DEFAULT_HASHTAGS = [
    "ngapsaigon",
    "muangap",
    "trieucuong"
]

DEFAULT_SEARCH_QUERIES = [
    "ngập TPHCM",
    "ngập Sài Gòn",
    "mưa ngập TP.HCM",
    "triều cường Sài Gòn",
    "xe chết máy ngập"
]

# ==========================================
# 2. Cấu hình Actor cào Facebook (Chuyên sâu TP.HCM & Tiết kiệm tối đa)
# ==========================================
FB_ACTOR_ID = "scraper_one~facebook-posts-search"
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
    "mưa ngập TP.HCM",
    "ngập đường Sài Gòn",
    "triều cường ngập Sài Gòn",
    "ngập xe chết máy",
    "#ngapsaigon",
    "#muangap"
]

FB_SEARCH_LOCATIONS = ["Ho Chi Minh City"]
FB_NEWER_THAN_DEFAULT = "48 hours"

# ==========================================
# Cấu hình Server & Cửa sổ thời gian
# ==========================================
DEFAULT_PORT = 8050
DEFAULT_WINDOW_MINUTES = 120
