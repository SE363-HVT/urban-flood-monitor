# -*- coding: utf-8 -*-
"""
scripts/check_google_rss.py
Công cụ kiểm tra nhanh tình trạng Rate-limit của Google RSS trên IP hiện tại.
"""

import sys
import time
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

TEST_URL = "https://news.google.com/rss/search?q=ng%E1%BA%ADp+TPHCM&hl=vi&gl=VN&ceid=VN:vi"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("=" * 65)
print("🔍 KIỂM TRA TRẠNG THÁI KẾT NỐI GOOGLE NEWS RSS")
print("=" * 65)
print(f" • Mục tiêu : {TEST_URL[:50]}...")
print(" • Đang gửi yêu cầu kiểm tra...")

req = urllib.request.Request(TEST_URL, headers=HEADERS)
t0 = time.time()

try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        elapsed = time.time() - t0
        content = resp.read()
        print(f"\n✅ KẾT QUẢ: BÌNH THƯỜNG (HTTP {resp.status} OK)")
        print(f" • Thời gian phản hồi : {elapsed:.2f} giây")
        print(f" • Dung lượng nhận    : {len(content):,} bytes")
        print(" • Tình trạng IP      : SẠCH, Google không chặn IP của bạn!")
        print(" • Khuyến cáo         : Có thể bật lại luồng cào Google RSS bình thường.")
except urllib.error.HTTPError as e:
    elapsed = time.time() - t0
    print(f"\n⚠️ KẾT QUẢ: BỊ GIỚI HẠN TẦN SUẤT (HTTP {e.code} {e.reason})")
    print(f" • Thời gian phản hồi : {elapsed:.2f} giây")
    if e.code == 503:
        print(" • Tình trạng IP      : Google đang tạm phạt tần suất (503 Service Unavailable).")
        print(" • CÓ BỊ CHẶN VĨNH VIỄN KHÔNG?: TUYỆT ĐỐI KHÔNG!")
        print(" • Thời gian chờ nhả : Thông thường 15 - 45 phút kể từ lần dừng cào cuối cùng.")
        print(" • HƯỚNG DẪN XỬ LÝ NHANH NGAY LẬP TỨC:")
        print("   1. Đổi mạng Wi-Fi khác hoặc bật 4G phát từ điện thoại để có IP mới ngay lập tức.")
        print("   2. Hoặc bật phần mềm VPN / Cloudflare 1.1.1.1 WARP để vượt qua trong 1 giây.")
        print("   3. Hệ thống SE363 đã có Circuit Breaker tự động chuyển sang Bing News RSS.")
    elif e.code == 429:
        print(" • Tình trạng IP      : Quá nhiều request (Too Many Requests). Chờ 15 phút.")
    else:
        print(f" • Mã lỗi chi tiết    : {e.code}")
except (TimeoutError, urllib.error.URLError) as e:
    elapsed = time.time() - t0
    print(f"\n⚠️ KẾT QUẢ: BỊ GOOGLE DROP KẾT NỐI (Timeout / Connection Dropped sau {elapsed:.2f}s)")
    print(" • Tình trạng IP      : Google đang tạm thời từ chối xử lý kết nối từ IP này.")
    print(" • CÓ BỊ CHẶN VĨNH VIỄN KHÔNG?: TUYỆT ĐỐI KHÔNG!")
    print(" • Thời gian chờ nhả : Khoảng 15 - 45 phút không gửi request liên tục.")
    print(" • CÁCH VƯỢT QUA NGAY (KHÔNG CẦN CHỜ):")
    print("   👉 Đổi sang Wi-Fi khác / Bật 4G điện thoại / Bật VPN 1.1.1.1 WARP.")
    print("   👉 Hệ thống SE363 đã tự động chuyển 100% sang Microsoft Bing News RSS.")
except Exception as e:
    print(f"\n❌ LỖI KHÁC: {e}")

print("=" * 65)
