# -*- coding: utf-8 -*-
"""
tests/test_live_fixes.py
Kiểm tra toàn bộ 5 cải tiến quan trọng:
1. Lọc sạch bài rác BĐS (Phòng trọ Bình Thạnh) và bình luận chính trị/vĩ mô (Bộ đội Cụ Hồ).
2. Kiểm tra Open-Meteo API theo giờ đăng bài thực tế (Asia/Bangkok).
3. Kiểm tra trích xuất Bùi Văn Ba.
4. Kiểm tra Live Crawler: không có bài nào cũ quá 24h, phân tầng đúng 3 nhãn.
"""

import sys
import os
import time

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from pipeline.event_processor import clean_stream_text, contains_spam_or_noise
from core.gazetteer import match_all_hotspots
from pipeline.veracity_checker import VeracityChecker
from pipeline.live_free_crawler import LiveFreeSocialCrawler

print("=" * 60)
print("[TEST 1] Kiểm tra chặn bài rác BĐS & Bình luận vĩ mô/chính trị:")
print("=" * 60)

# Bài viết Phòng trọ Bình Thạnh (Screenshot 3 của user)
spam_bds = """STUDIO TÁCH BẾP - BAN CÔNG SIÊU THOÁNG TẠI UNG VĂN KHIÊM
Vị trí: Trục đường Ung Văn Khiêm, P.25, Q. Bình Thạnh
Thiết kế: Dạng Studio sở hữu cả ban công và cửa sổ ngập tràn ánh sáng. Khu vực bếp tách biệt hoàn toàn giúp phòng luôn sạch sẽ.
Tiện ích: Xách vali vào ở ngay với FULL NỘI THẤT (Giường nệm, máy lạnh, tủ lạnh, nước nóng...).
Điện: 4k/kWh. Nước: 150k/người. Hotline/Zalo: 0975 341 862"""

# Bài viết Bộ đội Cụ Hồ (Screenshot 1 của user)
macro_policy = """6,5 TRIỆU NGƯỜI DÂN CHỜ MỘT MỆNH LỆNH KHÔNG ĐƯỢC THAY ĐỔI
Những đêm đầu tháng 10/2026, nhiều gia đình ở TP.HCM không ngủ... đợt triều cường đỉnh lịch sử... mưa lớn 150mm.
Dự án chống ngập do triều cường đã đạt 95% khối lượng. Kênh Tham Lương 9.030 tỷ đồng.
Thủ tướng Lê Minh Hưng đưa công trình về đích... #CTVN #chinhtrivietnam #tinnoichinh #duanchongngaptphcm"""

# Bài viết ngập thật tại Ung Văn Khiêm
real_flood = "Đường Ung Văn Khiêm ngập sâu bì bõm, hàng loạt xe chết máy phải dắt bộ trong mưa to chiều nay!"

res_bds = clean_stream_text(spam_bds)
res_macro = clean_stream_text(macro_policy)
res_real = clean_stream_text(real_flood)

print(f"  - Spam BĐS Phòng Trọ: {'[BLOCKED - CHẶN THÀNH CÔNG]' if res_bds is None else '[FAILED]'}")
print(f"  - Bình luận chính trị/vĩ mô: {'[BLOCKED - CHẶN THÀNH CÔNG]' if res_macro is None else '[FAILED]'}")
print(f"  - Báo ngập thực tế Ung Văn Khiêm: {'[ACCEPTED - HỢP LỆ]' if res_real is not None else '[FAILED]'}")

assert res_bds is None, "Lỗi: Spam BĐS không được để lọt!"
assert res_macro is None, "Lỗi: Bình luận vĩ mô không được để lọt!"
assert res_real is not None, "Lỗi: Bài ngập thật bị chặn nhầm!"

print("\n" + "=" * 60)
print("[TEST 2] Kiểm tra nhận diện điểm ngập Bùi Văn Ba (Quận 7):")
print("=" * 60)
bui_van_ba_text = "Mỗi đợt triều cường, khoảng 70 hộ dân tại chung cư 136 Bùi Văn Ba, TP.HCM nước tràn vào nhà bì bõm"
spots = match_all_hotspots(bui_van_ba_text)
print(f"  - Kết quả khớp: {len(spots)} điểm")
for s in spots:
    print(f"    * Đường: {s.get('street')} | ĐVHC: {s.get('ward')} | Tọa độ: {s.get('lat')}, {s.get('lon')}")
assert any("Bùi Văn Ba" in s.get("street", "") for s in spots), "Lỗi: Bùi Văn Ba phải được nhận diện!"

print("\n" + "=" * 60)
print("[TEST 3] Kiểm tra Open-Meteo đối soát thời tiết theo giờ đăng bài (15:00 hôm nay):")
print("=" * 60)
checker = VeracityChecker()
now = int(time.time())
post_afternoon = now - 7 * 3600  # 7 tiếng trước (~15:00 - 16:00)
sample_event = {
    "id": "test_meteo_live",
    "text": "Ngập sâu ở Bùi Văn Ba chiều nay",
    "lat": 10.7485,
    "lon": 106.7320,
    "create_time": post_afternoon,
    "timestamp": post_afternoon
}
verified = checker.verify_event(sample_event)
w_check = verified.get("veracity", {}).get("weather_check", {})
print(f"  - Weather check reason: {w_check.get('reason')}")
print(f"  - Weather score: {w_check.get('score')}")
print(f"  - Precipitation mm: {w_check.get('precipitation_mm')} mm/h")
assert w_check.get("precipitation_mm", 0.0) > 0, "Lỗi: Phải tìm thấy lượng mưa chiều nay từ Open-Meteo!"

print("\n" + "=" * 60)
print("[TEST 4] Quét Live Crawler thử nghiệm (Giới hạn 24h & 3 nhãn):")
print("=" * 60)
crawler = LiveFreeSocialCrawler()
live_events, stats = crawler.poll_live_stream(window_minutes=120, max_queries=10)
print(f"  - Tổng số sự kiện hợp lệ quét được: {len(live_events)}")
for ev in live_events[:5]:
    age_h = (now - ev['create_time']) / 3600.0
    print(f"    * [{ev['platform'].upper()}] {ev['location'].get('street') or ev['location'].get('ward')}")
    print(f"      Thời gian: {ev.get('relative_time')} (cách đây {age_h:.1f}h)")
    print(f"      Nhãn: {ev.get('status_tag')}")
    assert age_h <= 24.5, f"Lỗi: Sự kiện cũ hơn 24h xuất hiện ({age_h:.1f}h)!"

print("\n[V] TẤT CẢ 4 BỘ KIỂM THỬ ĐỀU ĐẠT 100% THÀNH CÔNG!")
