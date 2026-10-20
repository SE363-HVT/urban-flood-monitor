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
   - Tự động phát hiện Kafka Broker (localhost:9092) qua fast socket check.
   - Nếu Kafka chưa bật, tự động chuyển sang chế độ Local Buffer để không làm đứt luồng.
5. DEAD LETTER QUEUE (DLQ) & DATA CONTRACT (Section 4.5 & 4.8):
   - Topic DLQ: social.flood.dlq
   - Phân loại lỗi và định tuyến các payload rác / hỏng sang DLQ.
"""

import os
import sys
import json
import time
import socket
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from pipeline.live_free_crawler import LiveFreeSocialCrawler
from pipeline.simulation_replayer import SimulationReplayer
from pipeline.tiktok_poller import TikTokPoller
from pipeline.facebook_poller import FacebookPoller

try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True

    class IngestionEventModel(BaseModel):
        id: str
        canonical_id: Optional[str] = None
        platform: str = "social"
        text: str
        create_time: int
        created_at_iso: Optional[str] = None
        url: Optional[str] = ""
except ImportError:
    PYDANTIC_AVAILABLE = False

try:
    from kafka import KafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    KafkaProducer = None
    KAFKA_AVAILABLE = False


KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_LIVE_RAW = "social.live.raw"
TOPIC_SIM_RAW = "social.sim.raw"
TOPIC_FLOOD_DLQ = "social.flood.dlq"


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
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.4)
            parts = self.bootstrap_servers.split(":")
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 9092
            res = sock.connect_ex((host, port))
            sock.close()
            if res != 0:
                print(f"[Producer Warning] Kafka Broker ({self.bootstrap_servers}) chưa sẵn sàng. Sẽ sử dụng Local Buffer fallback.")
                self.producer = None
                return
        except Exception:
            self.producer = None
            return

        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks=1,
                retries=3,
                request_timeout_ms=3000
            )
            print(f"[Producer Info] Đã kết nối thành công tới Kafka Broker tại {self.bootstrap_servers}")
        except Exception as e:
            print(f"[Producer Warning] Không thể kết nối tới Kafka Broker ({e}). Sẽ sử dụng Local Buffer fallback.")
            self.producer = None

    def send_to_dlq(self, source_topic: str, error_type: str, error_message: str, raw_payload: Any) -> bool:
        """
        Định tuyến bản ghi lỗi sang Dead Letter Queue (DLQ): social.flood.dlq (Blueprint 4.5).
        """
        dlq_event = {
            "failed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "source_topic": source_topic,
            "error_type": error_type,
            "error_message": error_message,
            "raw_payload": raw_payload,
            "retry_count": 0
        }

        if self.producer:
            try:
                self.producer.send(TOPIC_FLOOD_DLQ, value=dlq_event)
                return True
            except Exception as e:
                print(f"[DLQ Error] Không thể gửi DLQ qua Kafka: {e}")

        # Fallback local DLQ file
        dlq_file = os.path.join(ROOT_DIR, "data", "dlq_events.jsonl")
        try:
            with open(dlq_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(dlq_event, ensure_ascii=False) + "\n")
            return True
        except Exception:
            return False

    def validate_event(self, event: Dict[str, Any], source_topic: str) -> bool:
        """Kiểm tra hợp đồng dữ liệu đầu vào (Data Contract Validation)."""
        raw_text = event.get("text") or event.get("title") or ""
        if not raw_text or len(str(raw_text).strip()) < 5:
            self.send_to_dlq(source_topic, "SchemaValidationError", "Field 'text' is missing or too short (< 5 chars)", event)
            return False

        if not event.get("id"):
            self.send_to_dlq(source_topic, "SchemaValidationError", "Field 'id' is required but missing", event)
            return False

        return True

    def publish_event(self, topic: str, event: Dict[str, Any]) -> bool:
        """
        Bắn sự kiện vào Kafka Topic với khóa là canonical_id để chống trùng lặp.
        Kiểm tra hợp đồng dữ liệu, gửi sang DLQ nếu phát hiện bản ghi lỗi.
        """
        if not self.validate_event(event, topic):
            return False

        canonical_id = event.get("canonical_id") or f"{event.get('platform', 'mxh')}_{event.get('id')}"
        if canonical_id in self.seen_canonical_ids:
            return False  # Chống trùng lặp tầng 1

        self.seen_canonical_ids.add(canonical_id)
        event["canonical_id"] = canonical_id
        event["ingested_at_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        if self.producer:
            try:
                self.producer.send(topic, key=canonical_id, value=event)
                return True
            except Exception as e:
                print(f"[Producer Error] Lỗi khi gửi message vào topic {topic}: {e}")
                self.send_to_dlq(topic, "KafkaProducerException", str(e), event)
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
        - Cập nhật timestamp hiện tại để các sự kiện được hiển thị tức thì trên Live Heatmap.
        """
        replayer = SimulationReplayer.get_instance()
        events, stats = replayer.poll(batch_size=batch_size)
        published_count = 0
        now_ts = int(time.time())

        for ev in events:
            # Bảo tồn 100% mốc thời gian đăng tải video gốc để đối soát lượng mưa lịch sử với Open-Meteo
            video_time = ev.get("create_time") or ev.get("timestamp") or now_ts
            hist_time = ev.get("historical_timestamp") or video_time
            pub_at = ev.get("published_at") or datetime.fromtimestamp(hist_time, timezone.utc).isoformat()
            ev["canonical_id"] = f"sim_{ev.get('id')}_{now_ts}"
            ev["create_time"] = video_time
            ev["timestamp"] = video_time
            ev["historical_timestamp"] = hist_time
            ev["published_at"] = pub_at
            ev["crawler_source"] = "simulation_replayer"
            ev["platform"] = "simulation"
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
