# -*- coding: utf-8 -*-
"""
bigdata/producers/social_producer.py
Kafka Ingestion Producer Adapter cho Hệ thống Giám sát Ngập lụt SE363.
Hỗ trợ Kiến trúc Thu nạp Đa nguồn (Multi-Source Ingestion & Dual-Engine):
1. LIVE MODE:
   - Engine 1 (Chủ lực): LiveFreeSocialCrawler (100% miễn phí, Google RSS Discovery).
   - Engine 2 (Tùy chọn): Apify TikTok/Facebook Poller (Kích hoạt khi demo/cào sâu).
2. SIMULATION MODE:
   - Tái sử dụng SimulationReplayer từ tập 3.922 mẫu sạch để phát lại luồng mô phỏng.
3. CƠ CHẾ CHỐNG TRÙNG LẶP TẦNG 1 (PRODUCER DEDUPLICATION):
   - Băm định danh duy nhất (canonical_id) làm Kafka Message Key.
4. CƠ CHẾ CHỊU LỖI (FAULT-TOLERANCE):
   - Tự động phát hiện Kafka Broker (localhost:9092).
   - Nếu Kafka chưa bật, tự động chuyển sang chế độ Local Buffer để không làm đứt luồng.
"""

import os
import sys
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from pipeline.live_free_crawler import LiveFreeSocialCrawler
from pipeline.simulation_replayer import SimulationReplayer
from pipeline.tiktok_poller import TikTokPoller
from pipeline.facebook_poller import FacebookPoller

try:
    from kafka import KafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    KafkaProducer = None
    KAFKA_AVAILABLE = False


KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_LIVE_RAW = "social.live.raw"
TOPIC_SIM_RAW = "social.sim.raw"


class SocialKafkaProducer:
    def __init__(self, bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVERS):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.seen_canonical_ids = set()
        self.free_crawler = LiveFreeSocialCrawler()
        self.tiktok_poller = TikTokPoller()
        self.facebook_poller = FacebookPoller()
        self._init_kafka()

    def _init_kafka(self):
        if not KAFKA_AVAILABLE:
            print("[Producer Warning] Thư viện kafka-python chưa sẵn sàng. Chạy ở chế độ Local Buffer.")
            return

        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks=1,
                retries=3,
                request_timeout_ms=5000
            )
            print(f"[Producer Info] Đã kết nối thành công tới Kafka Broker tại {self.bootstrap_servers}")
        except Exception as e:
            print(f"[Producer Warning] Không thể kết nối tới Kafka Broker ({e}). Sẽ sử dụng Local Buffer fallback.")
            self.producer = None

    def publish_event(self, topic: str, event: Dict[str, Any]) -> bool:
        """
        Bắn sự kiện vào Kafka Topic với khóa là canonical_id để chống trùng lặp.
        """
        canonical_id = event.get("canonical_id") or f"{event.get('platform')}_{event.get('id')}"
        if canonical_id in self.seen_canonical_ids:
            return False  # Chống trùng lặp tầng 1

        self.seen_canonical_ids.add(canonical_id)
        event["ingested_at_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        if self.producer:
            try:
                self.producer.send(topic, key=canonical_id, value=event)
                return True
            except Exception as e:
                print(f"[Producer Error] Lỗi khi gửi message vào topic {topic}: {e}")
                return False
        else:
            # Local fallback: Ghi vào buffer file để Spark hoặc hệ thống đọc
            buffer_file = os.path.join(ROOT_DIR, "data", f"buffer_{topic}.jsonl")
            try:
                with open(buffer_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(event, ensure_ascii=False) + "\n")
                return True
            except Exception:
                return False

    def run_live_cycle(
        self,
        enable_free_crawler: bool = True,
        enable_apify_deep: bool = False,
        window_minutes: int = 120
    ) -> Dict[str, Any]:
        """
        Một chu kỳ thu nạp Live Mode:
        - Free Crawler quét nhanh ma trận điểm nóng.
        - Apify cào sâu (nếu được kích hoạt bằng nút demo).
        """
        published_count = 0
        total_discovered = 0

        # 1. Thu thập từ Free Crawler (Engine 1)
        if enable_free_crawler:
            events, stats = self.free_crawler.poll_live_stream(window_minutes=window_minutes)
            total_discovered += len(events)
            for ev in events:
                if self.publish_event(TOPIC_LIVE_RAW, ev):
                    published_count += 1

        # 2. Thu thập từ Apify Deep Poller (Engine 2 - Khi bấm demo)
        if enable_apify_deep:
            try:
                tt_events, _ = self.tiktok_poller.poll_live_apify(window_minutes=window_minutes, max_items=15)
                fb_events, _ = self.facebook_poller.poll_live_apify(window_minutes=window_minutes, max_items=15)
                for ev in (tt_events + fb_events):
                    total_discovered += 1
                    if self.publish_event(TOPIC_LIVE_RAW, ev):
                        published_count += 1
            except Exception as e:
                print(f"[Producer Apify Error] Không thể cào sâu qua Apify: {e}")

        if self.producer:
            self.producer.flush()

        return {
            "mode": "live",
            "total_discovered": total_discovered,
            "published_to_kafka": published_count,
            "topic": TOPIC_LIVE_RAW,
            "kafka_connected": self.producer is not None
        }

    def run_simulation_cycle(self, batch_size: int = 15) -> Dict[str, Any]:
        """
        Một chu kỳ phát lại Simulation Mode:
        - Đọc các batch sự kiện mô phỏng từ SimulationReplayer và bắn vào topic social.sim.raw.
        """
        replayer = SimulationReplayer.get_instance()
        events, stats = replayer.poll(batch_size=batch_size)
        published_count = 0

        for ev in events:
            # Gán canonical_id chuẩn hóa
            ev["canonical_id"] = f"sim_{ev.get('id')}"
            if self.publish_event(TOPIC_SIM_RAW, ev):
                published_count += 1

        if self.producer:
            self.producer.flush()

        return {
            "mode": "simulation",
            "batch_size": batch_size,
            "published_to_kafka": published_count,
            "topic": TOPIC_SIM_RAW,
            "kafka_connected": self.producer is not None
        }


if __name__ == "__main__":
    producer = SocialKafkaProducer()
    print("[*] Đang kiểm tra chạy thử Producer ở chế độ Simulation Mode...")
    res = producer.run_simulation_cycle(batch_size=5)
    print(f"[+] Kết quả Ingestion: {res}")

    print("\n[*] Đang kiểm tra chạy thử Producer ở chế độ Live Mode (Free Crawler)...")
    res_live = producer.run_live_cycle(enable_free_crawler=True, enable_apify_deep=False)
    print(f"[+] Kết quả Live Ingestion: {res_live}")
