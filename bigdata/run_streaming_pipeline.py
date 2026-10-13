# -*- coding: utf-8 -*-
"""
bigdata/run_streaming_pipeline.py
Trình Khởi Chạy Tự Động Toàn Trình (End-to-End One-Click Streaming Runner)
cho Hệ Thống Giám Sát Ngập Lụt Đô Thị SE363.

Điều phối 4 tầng kiến trúc:
1. Cụm Apache Kafka 4.3.1 (KRaft Mode) & Kafka-UI (Port 8080).
2. Leaflet Heatmap Dashboard Web Server (Port 8050).
3. PySpark Structured Streaming Engine (Parallel Micro-batches, Hot State, Lakehouse).
4. Multi-Source Kafka Producer (Live Free Crawler hoặc Simulation Replayer).
"""

import os
import sys
import time
import subprocess
import argparse
import signal

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

PYTHON_EXE = sys.executable


def check_docker_kafka() -> bool:
    """Kiểm tra cụm Kafka container có đang chạy không."""
    print("[1/4] Kiểm tra Cụm Apache Kafka 4.3.1 KRaft...")
    try:
        res = subprocess.run(["docker", "ps", "--filter", "name=se363-kafka-kraft", "--format", "{{.Status}}"],
                             capture_stdout=True, text=True, check=False)
        if "Up" in res.stdout:
            print("   ✅ Cụm Kafka KRaft đang hoạt động (localhost:9092, UI: http://localhost:8080)")
            return True
        else:
            print("   ⚠️ Container se363-kafka-kraft chưa bật.")
            return False
    except Exception:
        print("   ⚠️ Không thể kết nối tới Docker CLI. Hãy đảm bảo Docker Desktop đã mở.")
        return False


def start_docker_kafka():
    """Khởi động Kafka qua docker compose."""
    compose_file = os.path.join(ROOT_DIR, "bigdata", "docker-compose.yml")
    print(f"[*] Đang khởi động Kafka & Kafka-UI từ {compose_file}...")
    try:
        subprocess.run(["docker", "compose", "-f", compose_file, "up", "-d"], check=True)
        print("   ✅ Đã gửi lệnh khởi động Kafka. Đang chờ Broker sẵn sàng (5s)...")
        time.sleep(5)
    except Exception as e:
        print(f"   ❌ Lỗi khi khởi động docker compose: {e}")


def main():
    parser = argparse.ArgumentParser(description="SE363 - End-to-End Big Data Streaming Pipeline Runner")
    parser.add_argument("--mode", choices=["live", "simulation"], default="live",
                        help="Chế độ thu nạp: 'live' (Free Crawler) hoặc 'simulation' (3.818 mẫu lịch sử)")
    parser.add_argument("--enable-apify", action="store_true",
                        help="Bật thêm cào sâu Apify trong Live Mode (chỉ bật khi demo giảng viên)")
    parser.add_argument("--interval", type=int, default=60,
                        help="Chu kỳ cào / phát lại (giây). Mặc định 60 giây")
    parser.add_argument("--skip-dashboard", action="store_true",
                        help="Bỏ qua không chạy Dashboard Web Server")

    args = parser.parse_args()

    print("=" * 75)
    print("🌊 SE363: URBAN FLOOD MONITORING - END-TO-END STREAMING PIPELINE")
    print("=" * 75)
    print(f" • Chế độ thu nạp (Mode) : {args.mode.upper()}")
    print(f" • Cào sâu Apify        : {'BẬT (Demo)' if args.enable_apify else 'TẮT (Tiết kiệm chi phí)'}")
    print(f" • Chu kỳ chuỗi sự kiện  : {args.interval} giây")
    print(f" • Python Runtime       : {PYTHON_EXE}")
    print("=" * 75)

    # 1. Kiểm tra Kafka
    if not check_docker_kafka():
        start_docker_kafka()

    processes = []

    try:
        # 2. Khởi động Dashboard Server nếu không skip
        if not args.skip_dashboard:
            print("\n[2/4] Khởi động Leaflet Heatmap Dashboard Web Server (Port 8050)...")
            server_script = os.path.join(ROOT_DIR, "dashboard", "server.py")
            p_dash = subprocess.Popen([PYTHON_EXE, server_script, "--port", "8050"])
            processes.append(("Dashboard Server", p_dash))
            time.sleep(1.5)
            print("   ✅ Dashboard đang chạy tại: http://localhost:8050")

        # 3. Khởi động PySpark Structured Streaming Processor
        print("\n[3/4] Khởi động PySpark Structured Streaming Engine...")
        spark_script = os.path.join(ROOT_DIR, "bigdata", "streaming", "spark_flood_processor.py")
        p_spark = subprocess.Popen([PYTHON_EXE, spark_script])
        processes.append(("PySpark Engine", p_spark))
        time.sleep(3)
        print("   ✅ PySpark Streaming Processor đã sẵn sàng xử lý micro-batch!")

        # 4. Khởi động Kafka Producer Ingestion Loop
        print(f"\n[4/4] Khởi chạy Producer Ingestion Loop ({args.mode.upper()})...")
        from bigdata.producers.social_producer import SocialKafkaProducer
        producer = SocialKafkaProducer()

        cycle = 0
        while True:
            cycle += 1
            print(f"\n--- [Cycle #{cycle}] Thu nạp sự kiện ngập lụt lúc {time.strftime('%H:%M:%S')} ---")
            if args.mode == "live":
                stats = producer.run_live_cycle(enable_free_crawler=True, enable_apify_deep=args.enable_apify)
                print(f"   📡 [Live Free Ingestion] Phát hiện: {stats['total_discovered']} tin | Đã bắn vào Kafka: {stats['published_to_kafka']} tin")
            else:
                stats = producer.run_simulation_cycle(batch_size=10)
                print(f"   📡 [Simulation Replayer] Đã bắn: {stats['published_to_kafka']} tin vào Kafka topic {stats['topic']}")

            print(f"   ⏱️ Đang chờ {args.interval} giây cho chu kỳ tiếp theo... (Nhấn Ctrl+C để dừng)")
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n\n[*] Đang dừng toàn bộ các tiến trình streaming an toàn...")
    finally:
        for name, p in processes:
            print(f"[*] Tắt {name} (PID: {p.pid})...")
            p.terminate()
            try:
                p.wait(timeout=3)
            except Exception:
                p.kill()
        print("[*] Đã tắt toàn bộ hệ thống streaming thành công!")


if __name__ == "__main__":
    main()
