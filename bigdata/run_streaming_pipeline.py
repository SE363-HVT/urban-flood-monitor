# -*- coding: utf-8 -*-
"""
bigdata/run_streaming_pipeline.py
Trình Khởi Chạy Tự Động Toàn Trình (End-to-End One-Click Streaming Runner)
cho Hệ Thống Giám Sát Ngập Lụt Đô Thị SE363.

Điều phối các tầng kiến trúc:
1. Cụm Apache Kafka 4.3.1 (KRaft Mode) & Kafka-UI (Port 8080) & Redis (Port 6379).
2. Leaflet Heatmap Dashboard Web Server (Port 8050).
3. PySpark Native Structured Streaming Engine (Parallel UDFs, Hot State Redis, Lakehouse Parquet).
4. Multi-Source Kafka Producer (Live Free Crawler hoặc Simulation Replayer) & Dead Letter Queue.
5. Multimodal AI Microservice (Port 8001 - Tùy chọn).
"""

import os
import sys
import time
import subprocess
import argparse
import json

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


def check_docker_services() -> bool:
    """Kiểm tra cụm Kafka & Redis container có đang chạy không."""
    print("[1/5] Kiểm tra Cụm Docker (Kafka 4.3.1 KRaft & Redis 7.2)...")
    try:
        res = subprocess.run(
            ["docker", "ps", "--filter", "name=se363-kafka-kraft", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
            check=False
        )
        if "Up" in res.stdout:
            print("   ✅ Cụm Kafka KRaft đang hoạt động (localhost:9092, UI: http://localhost:8080)")
            return True
        else:
            print("   ⚠️  Container se363-kafka-kraft chưa bật.")
            return False
    except Exception:
        print("   ⚠️  Không thể kết nối tới Docker CLI. Hệ thống sẽ tự động fallback sang Local Buffer.")
        return False


def start_docker_services():
    """Khởi động Kafka & Redis qua docker compose."""
    compose_file = os.path.join(ROOT_DIR, "bigdata", "docker-compose.yml")
    print(f"[*] Đang khởi động Kafka, Kafka-UI & Redis từ {compose_file}...")
    try:
        subprocess.run(["docker", "compose", "-f", compose_file, "up", "-d"], check=True)
        print("   Đang chờ 5 giây để Kafka KRaft broker hoàn tất khởi tạo...")
        time.sleep(5)
        print("   ✅ Docker containers đã sẵn sàng!")
    except Exception as e:
        print(f"   ❌ Lỗi khi khởi động Docker Compose: {e}")
        print("   Hệ thống sẽ chạy với Local Buffer fallback.")


def main():
    parser = argparse.ArgumentParser(description="SE363 - End-to-End Big Data Streaming Pipeline Runner")
    parser.add_argument("--mode", choices=["live", "simulation"], default="live",
                        help="Chế độ thu nạp: 'live' (Free Crawler) hoặc 'simulation' (3.818 mẫu lịch sử)")
    parser.add_argument("--enable-apify", action="store_true",
                        help="Bật thêm cào sâu Apify trong Live Mode (chỉ bật khi demo giảng viên)")
    parser.add_argument("--enable-ai", action="store_true",
                        help="Khởi chạy Multimodal AI Microservice trên cổng 8001")
    parser.add_argument("--interval", type=int, default=None,
                        help="Chu kỳ cào / phát lại (giây). Mặc định 60 giây")
    parser.add_argument("--skip-dashboard", action="store_true",
                        help="Bỏ qua không chạy Dashboard Web Server")

    args = parser.parse_args()
    if args.interval is None:
        args.interval = 5 if args.mode == "simulation" else 60

    print("=" * 75)
    print("🚀 SE363: URBAN FLOOD MONITORING - END-TO-END STREAMING PIPELINE")
    print("=" * 75)
    print(f" • Chế độ thu nạp (Mode) : {args.mode.upper()}")
    print(f" • Cào sâu Apify        : {'BẬT (Demo)' if args.enable_apify else 'TẮT (Tiết kiệm chi phí)'}")
    print(f" • AI Microservice (8001): {'BẬT' if args.enable_ai else 'TẮT'}")
    print(f" • Chu kỳ chuỗi sự kiện  : {args.interval} giây")
    print(f" • Python Runtime       : {PYTHON_EXE}")
    print("=" * 75)

    # 1. Kiểm tra Kafka & Redis Docker
    if not check_docker_services():
        start_docker_services()

    processes = []
    log_files = []

    try:
        # Dọn dẹp và khởi tạo state ban đầu
        state_file = os.path.join(ROOT_DIR, "data", "live_stream_state.json")
        try:
            import redis
            r = redis.Redis(host="localhost", port=6379, db=0, socket_connect_timeout=0.2, decode_responses=True)
            if r.ping():
                # Dọn dẹp sạch sẽ các key cũ để chống nhiễm chéo giữa Live và Simulation
                keys = r.keys("flood:event:*")
                if keys:
                    r.delete(*keys)
                r.delete("flood:timeline:zset", "flood:geo:index")
                r.set("flood:serving:mode", args.mode)
                r.set("flood:serving:window", "120 phút")
        except Exception:
            r = None

        if args.mode == "live":
            # CHẾ ĐỘ LIVE: TUYỆT ĐỐI KHÔNG DÙNG SIMULATION REPLAYER!
            # Khởi tạo trạng thái hoàn toàn sạch để chờ luồng tin tức Near Real-Time thật
            with open(state_file, "w", encoding="utf-8") as sf:
                json.dump({
                    "mode": "live",
                    "window": "120 phút",
                    "events_count": 0,
                    "events": []
                }, sf, ensure_ascii=False, indent=2)
            print("   ✓ [Live Mode Clean Init] Đã dọn sạch bộ nhớ cache. Sẵn sàng thu nạp Near Real-Time thực tế.")
        else:
            # CHẾ ĐỘ SIMULATION: Nạp tập sự kiện kiểm thử từ SimulationReplayer
            try:
                from pipeline.simulation_replayer import SimulationReplayer
                from pipeline.veracity_checker import VeracityChecker
                from pipeline.spatio_temporal_clusterer import SpatioTemporalClusterer
                
                replayer = SimulationReplayer.get_instance()
                warmup_raw, stats = replayer.poll(batch_size=15)
                vc = VeracityChecker()
                cl = SpatioTemporalClusterer()
                verified_warmup = []
                for ev in warmup_raw:
                    ref_t = ev.get("historical_timestamp") or ev.get("create_time")
                    verified_warmup.append(vc.verify_event(ev, reference_time=ref_t))
                clustered_warmup = cl.cluster_events(verified_warmup)
                
                with open(state_file, "w", encoding="utf-8") as sf:
                    json.dump({
                        "mode": args.mode,
                        "window": "120 phút",
                        "events_count": len(clustered_warmup),
                        "events": clustered_warmup
                    }, sf, ensure_ascii=False, indent=2)
                print(f"   ✓ [Simulation Ingestion] Đã nạp trước {len(clustered_warmup)} sự kiện mô phỏng vào Heatmap.")
                
                if r and r.ping():
                    pipe = r.pipeline()
                    for ev in clustered_warmup:
                        cid = ev.get("canonical_id") or ev.get("id")
                        loc = ev.get("location", {})
                        lat = loc.get("lat") or ev.get("lat")
                        lon = loc.get("lon") or ev.get("lon")
                        ctime = ev.get("create_time", int(time.time()))
                        if lat and lon:
                            pipe.geoadd("flood:geo:index", (lon, lat, cid))
                        pipe.zadd("flood:timeline:zset", {cid: ctime})
                        pipe.set(f"flood:event:{cid}", json.dumps(ev, ensure_ascii=False), ex=86400)
                    pipe.execute()
                    print(f"   ✓ [Redis Store] Đã đồng bộ {len(clustered_warmup)} sự kiện vào In-Memory Redis Hot Store.")
            except Exception as e:
                print(f"   ! Lỗi khởi tạo mô phỏng: {e}")

        # 2. Khởi động AI Microservice nếu được yêu cầu
        if args.enable_ai:
            print("\n[2/5] Khởi động Multimodal AI Microservice (Port 8001)...")
            ai_script = os.path.join(ROOT_DIR, "bigdata", "ai_service", "ai_microservice.py")
            p_ai = subprocess.Popen([PYTHON_EXE, ai_script], cwd=ROOT_DIR)
            processes.append(("AI Microservice", p_ai))
            time.sleep(1.5)
            print("   ✅ AI Microservice đang chạy tại: http://localhost:8001")
        else:
            print("\n[2/5] Multimodal AI Microservice: TẮT (Tiết kiệm RAM & CPU, dùng Heuristic Baseline)")

        # 3. Khởi động Dashboard Server nếu không skip
        if not args.skip_dashboard:
            print("\n[3/5] Khởi động Leaflet Heatmap Dashboard Web Server (Port 8050)...")
            server_script = os.path.join(ROOT_DIR, "dashboard", "server.py")
            p_dash = subprocess.Popen([PYTHON_EXE, server_script, "--port", "8050", "--mode", args.mode], cwd=ROOT_DIR)
            processes.append(("Dashboard Server", p_dash))
            time.sleep(1.5)
            print("   ✅ Dashboard đang chạy tại: http://localhost:8050")

        # 4. Khởi động PySpark Structured Streaming Processor
        print("\n[4/5] Khởi động PySpark Structured Streaming Engine...")
        spark_script = os.path.join(ROOT_DIR, "bigdata", "streaming", "spark_flood_processor.py")
        spark_log_path = os.path.join(ROOT_DIR, "data", "spark_engine.log")
        spark_log = open(spark_log_path, "a", encoding="utf-8")
        log_files.append(spark_log)
        p_spark = subprocess.Popen([PYTHON_EXE, "-u", spark_script, "--mode", args.mode], stdout=spark_log, stderr=spark_log, cwd=ROOT_DIR)
        processes.append(("PySpark Engine", p_spark))
        print("   Đang đợi 8 giây để PySpark khởi tạo và kết nối Kafka & Redis...")
        time.sleep(8)
        print("   ✅ PySpark Streaming Processor đã sẵn sàng xử lý micro-batch!")
        print(f"   ℹ️  Chi tiết log động cơ PySpark được ghi vào: data/spark_engine.log")

        # 5. Khởi chạy Producer Ingestion Loop
        print(f"\n[5/5] Khởi chạy Producer Ingestion Loop ({args.mode.upper()})...")
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
        for f in log_files:
            try:
                f.close()
            except Exception:
                pass
        print("[*] Đã tắt toàn bộ hệ thống streaming thành công!")


if __name__ == "__main__":
    main()
