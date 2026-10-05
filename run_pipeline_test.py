"""
run_pipeline_test.py - Script Thử Nghiệm Toàn Diện Pipeline Near Real-Time & Heatmap
SE363. Urban Drainage & Flooding Monitoring System (All-In-One Multi-Platform)

Chế độ LIVE cào TOÀN DIỆN đồng thời tất cả các nguồn:
1. Video TikTok ngập lụt, triều cường TP.HCM
2. Facebook Search: Bài đăng người dùng cá nhân & cộng đồng qua từ khóa
3. Facebook Targets: Bài viết từ các Fanpage & Group giao thông định sẵn

Cách dùng:
  # Chạy cào thật toàn diện trực tiếp từ tất cả các nguồn qua Apify:
  python run_pipeline_test.py --mode live --window 60

  # Chạy mô phỏng offline (không tốn quota Apify, dữ liệu bài đăng người dùng phong phú):
  python run_pipeline_test.py --mode simulation --window 120
"""

import sys
import os
import argparse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from dashboard.server import start_server
from core.config import APIFY_TOKEN, DEFAULT_WINDOW_MINUTES

def main():
    parser = argparse.ArgumentParser(
        description="SE363 - Pipeline Cào Toàn Diện Đa Nền Tảng (TikTok + FB Search Người Dùng + FB Fanpages & Groups)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ lệnh chạy:
  # Chế độ LIVE TOÀN DIỆN (cào đồng thời TikTok + Facebook bài đăng người dùng + Fanpages & Groups):
  python run_pipeline_test.py --mode live --window 60

  # Chế độ mô phỏng offline với dữ liệu có sẵn:
  python run_pipeline_test.py --mode simulation --window 120
        """
    )

    parser.add_argument(
        "--mode",
        choices=["simulation", "live"],
        default="live",
        help="Chế độ chạy: 'live' (cào toàn diện từ Apify) hoặc 'simulation' (dùng dữ liệu phong phú offline)"
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="Apify API Token (Mặc định tự động lấy từ core/config.py)"
    )
    parser.add_argument(
        "--window",
        type=int,
        default=DEFAULT_WINDOW_MINUTES,
        help="Kích thước cửa sổ thời gian lọc (phút) - Mặc định: 120 phút (2 giờ)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8050,
        help="Cổng mở giao diện Heatmap trên trình duyệt (Mặc định: 8050)"
    )

    args = parser.parse_args()
    token = args.token or APIFY_TOKEN

    if args.mode == "live" and not token:
        print("\n[!] LOI: Ban da chon --mode live nhung chua cung cap token.")
        print("Vui long them token vao core/config.py hoac truyen tham so --token apify_api_XXXX\n")
        sys.exit(1)

    start_server(port=args.port, mode=args.mode, apify_token=token, window_minutes=args.window)

if __name__ == "__main__":
    main()
