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

print("=" * 65)
print("🔍 KIỂM TRA TRẠNG THÁI KẾT NỐI GOOGLE NEWS RSS")
print("=" * 65)

# 1. Kiểm tra IP Public thực tế của máy
current_ip = "Không xác định"
try:
    with urllib.request.urlopen("https://api.ipify.org", timeout=5) as ip_resp:
        current_ip = ip_resp.read().decode('utf-8').strip()
except Exception:
    pass

print(f" • Địa chỉ IP Public hiện tại: {current_ip}")

TEST_URL = "https://news.google.com/rss/search?q=ng%E1%BA%ADp+TPHCM&hl=vi&gl=VN&ceid=VN:vi"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print(f" • Mục tiêu : {TEST_URL[:50]}...")
print(" • Đang gửi yêu cầu kiểm tra...")

req = urllib.request.Request(TEST_URL, headers=HEADERS)
t0 = time.time()

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        elapsed = time.time() - t0
        content = resp.read()
        print(f"\n✅ KẾT QUẢ: BÌNH THƯỜNG (HTTP {resp.status} OK)")
        print(f" • Thời gian phản hồi : {elapsed:.2f} giây")
        print(f" • Dung lượng nhận    : {len(content):,} bytes")
        print(f" • Tình trạng IP ({current_ip}): SẠCH, Google không chặn IP của bạn!")
        print(" • Khuyến cáo         : Có thể bật lại luồng cào Google RSS bình thường.")
except urllib.error.HTTPError as e:
    elapsed = time.time() - t0
    print(f"\n⚠️ KẾT QUẢ: BỊ GIỚI HẠN TẦN SUẤT (HTTP {e.code} {e.reason})")
    print(f" • Thời gian phản hồi : {elapsed:.2f} giây")
    if e.code == 503:
        print(f" • Tình trạng IP ({current_ip}): Google đang tạm phạt tần suất (503 Service Unavailable).")
        print(" • CÓ BỊ CHẶN VĨNH VIỄN KHÔNG?: TUYỆT ĐỐI KHÔNG!")
        print(" • NGUYÊN NHÂN VẪN BỊ TRÊN 4G: Nếu bật Hotspot điện thoại nhưng QUÊN TẮT WI-FI trên điện thoại,")
        print("   điện thoại sẽ tiếp tục lấy mạng Wi-Fi nhà chia sẻ cho máy tính -> IP Public vẫn là IP cũ!")
        print(" 👉 CÁCH XỬ LÝ: Vào Cài đặt điện thoại -> TẮT HẲN Wi-Fi -> Chỉ bật 4G/5G và Điểm phát sóng.")
    elif e.code == 429:
        print(" • Tình trạng IP      : Quá nhiều request (Too Many Requests). Chờ 15 phút.")
    else:
        print(f" • Mã lỗi chi tiết    : {e.code}")
except (TimeoutError, urllib.error.URLError) as e:
    elapsed = time.time() - t0
    print(f"\n⚠️ KẾT QUẢ: BỊ GOOGLE DROP KẾT NỐI (Timeout / Connection Dropped sau {elapsed:.2f}s)")
    print(f" • Tình trạng IP ({current_ip}): Google đang tạm thời từ chối xử lý kết nối từ IP này.")
    print(" • CÓ BỊ CHẶN VĨNH VIỄN KHÔNG?: TUYỆT ĐỐI KHÔNG!")
    print(" 👉 CÁCH XỬ LÝ NHANH:")
    print("   1. Tắt hẳn Wi-Fi trên điện thoại, chỉ bật Dữ liệu di động 4G/5G rồi phát Hotspot.")
    print("   2. Hoặc bật VPN 1.1.1.1 WARP trên máy tính để đổi IP ngay tức thì.")
    print("   3. Hệ thống SE363 đã tự động chuyển 100% sang Microsoft Bing News RSS.")
except Exception as e:
    print(f"\n❌ LỖI KHÁC: {e}")

print("=" * 65)
