"""
core/config.py - Cấu hình hệ thống Ingestion & Dashboard
Thu thập dữ liệu ngập lụt đô thị gần thời gian thực đa nền tảng:
1. TikTok Video: Video & Hashtag ngập lụt TP.HCM (Giữ nguyên ổn định).
2. Facebook: Tìm kiếm bài đăng ngập lụt thời gian thực qua Actor tối ưu chi phí & khớp điểm nóng.
"""

import os

# Apify API Token - Sử dụng token mới được cung cấp (Free tier có sẵn $5 credit)
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "apify_api_nALLiRCjYWDCWPUWwi3GDkmLG2po6L2Fy54o")

# ==========================================
# 1. Cấu hình Actor cào TikTok Video (Giữ nguyên ổn định)
# ==========================================
ACTOR_ID = "clockworks~free-tiktok-scraper"

DEFAULT_HASHTAGS = [
    "muangap",
    "ngaplut",
    "ngapsaigon",
    "ngaptphcm",
    "trieucuong",
    "ngapnuoc",
    "muasaigon",
    "trieucuongsaigon",
    "hongbienduongpho"
]

DEFAULT_SEARCH_QUERIES = [
    "ngập Tân Kỳ Tân Quý",
    "ngập Bình Tân",
    "mưa ngập Bình Tân",
    "ngập Kinh Dương Vương",
    "ngập Vĩnh Lộc",
    "ngập nước Sài Gòn",
    "mưa ngập TPHCM",
    "triều cường Sài Gòn",
    "ngập lụt TP.HCM",
    "ngập đường Phan Huy Ích",
    "ngập Ung Văn Khiêm",
    "ngập Nguyễn Văn Quá",
    "ngập Nguyễn Hữu Cảnh",
    "ngập Chợ Thủ Đức",
    "xe chết máy do ngập",
    "ngập lút bánh xe",
    "mưa ngập đường Sài Gòn",
    "ngập thất thủ Sài Gòn"
]

# ==========================================
# 2. Cấu hình Actor cào Facebook
# ==========================================
FB_SEARCH_PPR_ACTOR_ID = "danek~facebook-search-ppr"
FB_ACTOR_ID = FB_SEARCH_PPR_ACTOR_ID
FB_CRAWL_STRATEGY = os.environ.get("FB_CRAWL_STRATEGY", "search")

FB_SEARCH_QUERIES = [
    "mưa ngập Sài Gòn",
    "triều cường ngập Sài Gòn",
    "ngập xe chết máy Sài Gòn",
    "#ngapsaigon",
    "đường ngập bì bõm Sài Gòn"
]

FB_SEARCH_LOCATIONS = ["Ho Chi Minh City"]
FB_NEWER_THAN_DEFAULT = "48 hours"

# ==========================================
# Cấu hình Server & Cửa sổ thời gian
# ==========================================
DEFAULT_PORT = 8050
DEFAULT_WINDOW_MINUTES = 120
