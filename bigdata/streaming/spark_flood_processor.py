# -*- coding: utf-8 -*-
"""
bigdata/streaming/spark_flood_processor.py
Kafka → PySpark micro-batch cho Hệ thống Giám sát Ngập lụt SE363.

Cải tiến toàn diện theo SSOT Blueprint (Section 4.1 & Section 4.3):
1. KAFKA CONSUMER & SPARK UDFs:
   - KafkaConsumer.poll() lấy bản ghi để ứng dụng tạo từng Spark DataFrame.
   - Spark UDFs (extract_gis_udf, extract_severity_udf) chạy song song qua master("local[*]").
2. PHỤC VỤ KHÔNG KHÓA FILE (IN-MEMORY REDIS SERVING STORE):
   - Hot Path ghi trực tiếp vào Redis GEO & Sorted Set (< 3ms)
   - Hỗ trợ Fallback file data/live_stream_state.json nếu Redis chưa bật.
3. GOM CỤM ĐA NGUỒN (SPATIO-TEMPORAL CLUSTERING):
   - Tích hợp SpatioTemporalClusterer hợp nhất các bài đăng trùng vị trí (<400m) và thời gian (<45p).
4. DEAD LETTER QUEUE (DLQ):
   - Topic: social.flood.dlq và fallback data/dlq_events.jsonl.
5. HỒ DỮ LIỆU ĐA TẦNG (MEDALLION LAKEHOUSE PARTITIONING):
   - Cold Path: data/lakehouse/flood_events/episode_id={id}/date={date}/
6. GIỚI HẠN TUYỆT ĐỐI 24 GIỜ:
   - Loại bỏ 100% bản ghi cũ hơn 24 giờ (86400s).
   - 3 nhãn phân loại: < 2h, 2-4h, <= 24h.
"""

import os
import sys
import warnings

warnings.filterwarnings("ignore")

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import json
import time
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from typing import Dict, Any, List, Optional

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.gazetteer import match_hotspot
from core.admin_resolver import RESOLVER
from pipeline.veracity_checker import VeracityChecker
from pipeline.event_processor import clean_stream_text, analyze_severity_heuristic, format_relative_time
from pipeline.spatio_temporal_clusterer import SpatioTemporalClusterer
from scripts.crawlers.organize_raw_episodes import determine_episode_id
from bigdata.streaming.stream_storage import write_json_atomic

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.functions import coalesce, col, udf
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, DoubleType
)

try:
    import redis
    from redis.backoff import NoBackoff
    from redis.retry import Retry
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

try:
    from kafka import KafkaProducer, KafkaConsumer
    from kafka.errors import KafkaConfigurationError
    from kafka.structs import OffsetAndMetadata
    KAFKA_AVAILABLE = True
except ImportError:
    KafkaProducer = None
    KafkaConsumer = None
    KAFKA_AVAILABLE = False

DATA_DIR = os.path.join(ROOT_DIR, "data")
LAKEHOUSE_DIR = os.path.join(DATA_DIR, "lakehouse", "flood_events")
CHECKPOINT_DIR = os.path.join(DATA_DIR, "lakehouse", "_checkpoints", "native_stream")
STREAM_STATE_FILE = os.path.join(DATA_DIR, "live_stream_state.json")
DLQ_FILE = os.path.join(DATA_DIR, "dlq_events.jsonl")

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

# Schema sự kiện đầu vào
EVENT_SCHEMA = StructType([
    StructField("id", StringType(), True),
    StructField("canonical_id", StringType(), True),
    StructField("url", StringType(), True),
    StructField("platform", StringType(), True),
    StructField("media_type", StringType(), True),
    StructField("author", StringType(), True),
    StructField("text", StringType(), True),
    StructField("title", StringType(), True),
    StructField("create_time", LongType(), True),
    StructField("created_at_iso", StringType(), True),
    StructField("timestamp", LongType(), True),
    StructField("historical_timestamp", LongType(), True),
    StructField("published_at", StringType(), True),
    StructField("relative_time", StringType(), True),
    StructField("freshness", StringType(), True),
    StructField("status_tag", StringType(), True),
    StructField("weight", DoubleType(), True),
    StructField("crawler_source", StringType(), True),
    StructField("_source_version", StringType(), True),
])

GIS_OUTPUT_SCHEMA = StructType([
    StructField("street", StringType(), True),
    StructField("ward", StringType(), True),
    StructField("district", StringType(), True),
    StructField("lat", DoubleType(), True),
    StructField("lon", DoubleType(), True),
    StructField("display_name", StringType(), True),
    StructField("precision", StringType(), True),
    StructField("coordinate_kind", StringType(), True),
    StructField("resolution_reason", StringType(), True),
    StructField("source", StringType(), True),
    StructField("cause", StringType(), True),
    StructField("cause_label", StringType(), True)
])

SEVERITY_OUTPUT_SCHEMA = StructType([
    StructField("opinion", StringType(), True),
    StructField("severity", StringType(), True),
    StructField("weight", DoubleType(), True)
])


@udf(returnType=GIS_OUTPUT_SCHEMA)
def extract_gis_udf(text):
    """Spark UDF: Phân tích GIS Street-First và ĐVHC chuẩn NQ 1685 phân tán trên các core."""
    default_res = {
        "street": "",
        "ward": "Toàn TP.HCM",
        "district": "TP.HCM",
        "lat": 10.7769,
        "lon": 106.7009,
        "display_name": "Toàn TP.HCM",
        "cause": "rain",
        "cause_label": "Mưa lớn, nước không thoát kịp"
    }
    try:
        if not text:
            return default_res

        cleaned = clean_stream_text(str(text)) or str(text)
        matched = match_hotspot(cleaned)
        if not matched:
            return default_res

        st = matched.get("street") or ""
        w = matched.get("ward", "")
        off_w = RESOLVER.resolve_to_official_ward(w, "") or w or "Toàn TP.HCM"

        return {
            "street": str(st or ""),
            "ward": str(off_w or "Toàn TP.HCM"),
            "district": str(matched.get("district", "TP.HCM") or "TP.HCM"),
            "lat": float(matched.get("lat") or 10.7769),
            "lon": float(matched.get("lon") or 106.7009),
            "display_name": str(matched.get("display_name") or st or "Điểm ngập TP.HCM"),
            "precision": matched.get("precision"),
            "coordinate_kind": matched.get("coordinate_kind"),
            "resolution_reason": matched.get("resolution_reason"),
            "source": matched.get("coordinate_source") or matched.get("source"),
            "cause": str(matched.get("cause", "rain") or "rain"),
            "cause_label": str(matched.get("cause_label", "Mưa lớn, nước không thoát kịp") or "Mưa lớn")
        }
    except Exception:
        return default_res


@udf(returnType=SEVERITY_OUTPUT_SCHEMA)
def extract_severity_udf(text):
    """Spark UDF: Phân loại mức độ nghiêm trọng và trọng số phân tán trên các core."""
    if not text:
        return {"opinion": "ngập nước", "severity": "medium", "weight": 2.0}
    info = analyze_severity_heuristic(text) or {}
    return {
        "opinion": info.get("opinion", "ngập nước"),
        "severity": info.get("severity_level", "medium"),
        "weight": float(info.get("weight", 2.0))
    }


class SparkFloodProcessor:
    def __init__(self, mode: str = "live", app_name: str = "SE363-Spark-Flood-Processor",
                 *, restore_serving: bool = True):
        self.mode = mode
        self.app_name = app_name
        self.veracity_checker = VeracityChecker(window_minutes=60, radius_meters=500.0)
        self.clusterer = SpatioTemporalClusterer(radius_meters=400.0, time_window_seconds=2700)
        self.spark = self._create_spark_session()
        if not restore_serving:
            return
        self.active_events_cache: List[Dict[str, Any]] = []
        self.redis_client = self._init_redis()
        self._hot_needs_retry = False
        self._hot_retry_at = 0.0
        self.dlq_producer = self._init_dlq_producer()
        self._warm_up_cache()
        self.recent_reports = {}
        now = datetime.now(timezone.utc)
        for day in (now - timedelta(days=1), now):
            files = Path(LAKEHOUSE_DIR).glob(f"episode_id=*/date={day:%Y-%m-%d}/report-{self.mode}-*.jsonl")
            for path in sorted(files, key=lambda item: item.stat().st_mtime_ns):
                with path.open(encoding="utf-8") as stream:
                    event = json.load(stream)
                if (event.get("create_time") or 0) >= now.timestamp() - 86400:
                    self.recent_reports[event["canonical_id"]] = event
        if self.recent_reports:
            self._publish_verified_batch([], batch_id=0)

    def _warm_up_cache(self):
        """Khởi động nạp trước các sự kiện còn hiệu lực trong 24 giờ từ Redis hoặc file đệm."""
        current_time = int(time.time())
        retention = 86400
        loaded = {}
        if self.redis_client:
            try:
                keys = self.redis_client.keys("flood:event:*")
                if keys:
                    pipe = self.redis_client.pipeline()
                    for k in keys:
                        pipe.get(k)
                    vals = pipe.execute()
                    for v in vals:
                        if v:
                            try:
                                ev = json.loads(v)
                                cid = ev.get("canonical_id") or ev.get("id")
                                ctime = ev.get("create_time", 0) or ev.get("timestamp", 0)
                                if cid and (current_time - ctime) <= retention:
                                    loaded[cid] = ev
                            except Exception:
                                pass
            except Exception as e:
                print(f"[Spark Engine] Cảnh báo warm up Redis: {e}")

        if not loaded and os.path.exists(STREAM_STATE_FILE):
            try:
                with open(STREAM_STATE_FILE, "r", encoding="utf-8") as sf:
                    data = json.load(sf)
                    for ev in data.get("events", []):
                        cid = ev.get("canonical_id") or ev.get("id")
                        ctime = ev.get("create_time", 0) or ev.get("timestamp", 0)
                        if cid and (current_time - ctime) <= retention:
                            loaded[cid] = ev
            except Exception:
                pass

        self.active_events_cache = list(loaded.values())
        if self.active_events_cache:
            print(f"[Spark Engine] Đã warm-up {len(self.active_events_cache)} sự kiện đang hoạt động từ storage.")

    def _create_spark_session(self) -> SparkSession:
        """Khởi tạo cụm Spark Session tối ưu phân tán đa lõi CPU."""
        spark = SparkSession.builder \
            .appName(self.app_name) \
            .master("local[*]") \
            .config("spark.driver.memory", "2g") \
            .config("spark.executor.memory", "2g") \
            .config("spark.sql.shuffle.partitions", "4") \
            .config("spark.default.parallelism", "4") \
            .config("spark.ui.showConsoleProgress", "false") \
            .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
            .getOrCreate()

        spark.sparkContext.setLogLevel("ERROR")
        return spark

    def _init_redis(self):
        if not REDIS_AVAILABLE:
            return None
        try:
            r = redis.Redis(
                host=REDIS_HOST, port=REDIS_PORT, db=0,
                socket_connect_timeout=0.4, socket_timeout=0.4,
                retry=Retry(NoBackoff(), 0), decode_responses=True
            )
            r.ping()
            print(f"[Spark Engine] Đã kết nối thành công tới Redis Serving Store ({REDIS_HOST}:{REDIS_PORT})")
            return r
        except Exception:
            print("[Spark Engine] Redis chưa bật -> Sẽ fallback ghi file đệm cục bộ.")
            return None

    def _init_dlq_producer(self):
        if not KAFKA_AVAILABLE:
            return None
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            res = sock.connect_ex(("localhost", 9092))
            sock.close()
            if res != 0:
                return None
            p = KafkaProducer(
                bootstrap_servers="localhost:9092",
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
                request_timeout_ms=1500,
                max_block_ms=1500,
            )
            return p
        except Exception:
            return None

    def send_dlq(self, error_type: str, message: str, payload: Any):
        dlq_event = {
            "failed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "source": "spark_streaming_processor",
            "error_type": error_type,
            "error_message": message,
            "raw_payload": payload,
            "retry_count": 0
        }
        if self.dlq_producer:
            try:
                self.dlq_producer.send("social.flood.dlq", value=dlq_event).get(timeout=3)
                return
            except Exception as error:
                print(f"[Spark Engine] DLQ Kafka chưa xác nhận: {error}")
        with open(DLQ_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(dlq_event, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def process_micro_batch(self, batch_df, batch_id: int, raw_records: Optional[List[Dict[str, Any]]] = None):
        """
        Xử lý micro-batch phân tán:
        Đã chuyển hoá dữ liệu GIS và Severity qua Spark UDFs trên các core.
        """
        # Áp dụng Spark UDFs song song
        transformed_df = batch_df \
            .withColumn("gis", extract_gis_udf(coalesce(col("text"), col("title")))) \
            .withColumn("sev", extract_severity_udf(coalesce(col("text"), col("title"))))

        rows = transformed_df.collect()
        if not rows:
            return
        print(f"\n[PySpark Stream] Micro-batch #{batch_id}: xử lý {len(rows)} báo cáo.")
        verified_batch = []
        raw_map = {self._fingerprint(r): r for r in (raw_records or [])}
        raw_by_id = {r.get("canonical_id") or str(r.get("id")): r for r in (raw_records or [])}

        payload_list = []
        for row in rows:
            if hasattr(row, "asDict"):
                record = row.asDict(recursive=True)
            elif isinstance(row, dict):
                record = row
            else:
                record = dict(row)

            gis = record.get("gis")
            if hasattr(gis, "asDict"):
                gis = gis.asDict(recursive=True)
            elif not isinstance(gis, dict):
                gis = {}

            sev = record.get("sev")
            if hasattr(sev, "asDict"):
                sev = sev.asDict(recursive=True)
            elif not isinstance(sev, dict):
                sev = {}

            raw_text = record.get("text") or record.get("title") or ""
            cleaned_txt = clean_stream_text(raw_text) or raw_text.strip()
            if len(cleaned_txt) < 8:
                self.send_dlq("CorruptedTextError", "Text length too short", record)
                continue

            orig = raw_map.get(record.get("_source_version"))
            if orig is None:
                orig = raw_by_id.get(record.get("canonical_id") or str(record.get("id")), {})
            spatial, lat, lon = self._select_location(orig, gis)
            st_name = spatial.get("street") or ""
            off_w = spatial.get("ward") or "Toàn TP.HCM"

            ctime = record.get("create_time") or record.get("timestamp") or int(time.time())
            hist_ts = record.get("historical_timestamp") or orig.get("historical_timestamp")

            event_payload = {
                "id": str(record.get("id")),
                "canonical_id": record.get("canonical_id") or f"{record.get('platform')}_{record.get('id')}",
                "platform": (record.get("platform") or ("social" if self.mode == "live" else "simulation")).lower(),
                "media_type": record.get("media_type") or "post",
                "author": record.get("author") or "Người dân TP.HCM",
                "text": cleaned_txt,
                "create_time": ctime,
                "created_at_iso": record.get("created_at_iso") or datetime.now(timezone.utc).isoformat(),
                "timestamp": ctime,
                "historical_timestamp": hist_ts,
                "relative_time": orig.get("relative_time") or format_relative_time(ctime),
                "freshness": orig.get("freshness") or "within_24h",
                "status_tag": orig.get("status_tag") or "🟡 CẢNH BÁO TRONG NGÀY (4-24 GIỜ)",
                "location": {
                    "street": st_name,
                    "display_name": spatial.get("display_name") or st_name or
                    (f"{off_w} (TP.HCM)" if off_w != "Toàn TP.HCM" else "Toàn TP. Hồ Chí Minh"),
                    "ward": off_w,
                    "administrative_unit": off_w,
                    "district": spatial.get("district") or "TP.HCM",
                    "lat": lat,
                    "lon": lon,
                    "heat_points": [[lat, lon]],
                    "cause": gis.get("cause", "rain"),
                    "cause_label": gis.get("cause_label", "Mưa lớn"),
                    "source": "pyspark_streaming_engine"
                },
                "aspect": st_name or off_w,
                "opinion": sev.get("opinion", "ngập nước"),
                "severity": sev.get("severity", "medium"),
                "weight": float(sev.get("weight") or 2.0),
                "url": record.get("url") or ""
            }
            self._preserve_source_fields(event_payload, orig, spatial)
            payload_list.append(event_payload)

        # Xử lý song song 8 luồng VeracityChecker để hoàn thành micro-batch trong < 0.3s
        from concurrent.futures import ThreadPoolExecutor
        def _verify_one(p):
            ref_t = p.get("historical_timestamp") or p.get("timestamp")
            return self.veracity_checker.verify_event(p, reference_time=ref_t)

        with ThreadPoolExecutor(max_workers=8) as pool:
            verified_batch = list(pool.map(_verify_one, payload_list))

        self._publish_verified_batch(verified_batch, batch_id)

    @staticmethod
    def _select_location(original, resolved):
        source = original.get("location")
        if isinstance(source, dict):
            try:
                lat, lon = float(source.get("lat")), float(source.get("lon"))
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return source, lat, lon
            except (TypeError, ValueError, OverflowError):
                pass
        return resolved, float(resolved.get("lat") or 10.7769), float(resolved.get("lon") or 106.7009)

    def _preserve_source_fields(self, event, original, resolved):
        for field in ("aspect", "opinion", "polarity", "sentiment", "triplets", "aste_triplets",
                      "media_urls", "video_url", "media", "historical_timestamp", "crawler_source",
                      "ingested_at_iso"):
            if original.get(field) is not None:
                event[field] = original[field]
        location = event["location"]
        if location.get("street"):
            level, kind = "street", "gazetteer_reference"
        elif str(location.get("ward") or "").lower().startswith(("phường", "xã", "đặc khu")):
            level, kind = "ward", "administrative_center"
        else:
            level, kind = "city", "administrative_center"
        location["precision"] = resolved.get("precision") or level
        location["coordinate_kind"] = resolved.get("coordinate_kind") or kind
        if resolved.get("resolution_reason"):
            location["resolution_reason"] = resolved["resolution_reason"]
        coordinate_source = resolved.get("coordinate_source") or resolved.get("source")
        if coordinate_source:
            location["coordinate_source"] = coordinate_source
        event["stream_mode"] = self.mode
        event["report_version"] = self._fingerprint(original or event)

    @staticmethod
    def _fingerprint(record):
        stable = {k: v for k, v in record.items() if k not in {
            "ingested_at_iso", "created_at_iso", "relative_time", "freshness", "status_tag",
        }}
        return sha256(json.dumps(stable, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

    def _publish_verified_batch(self, events, batch_id):
        self._append_cold_lakehouse(events)
        cutoff = int(time.time()) - 86400
        self.recent_reports = {
            cid: event for cid, event in self.recent_reports.items()
            if (event.get("create_time") or 0) >= cutoff
        }
        for event in events:
            if (event.get("create_time") or 0) >= cutoff:
                self.recent_reports[event["canonical_id"]] = event
        clustered = self.clusterer.cluster_events(list(self.recent_reports.values()))
        self._update_hot_dashboard_state(clustered)
        print(f"[PySpark Stream] Micro-batch #{batch_id}: {len(events)} báo cáo đã lưu, {len(clustered)} sự kiện đang phục vụ.")

    def _update_hot_dashboard_state(self, new_events: List[Dict[str, Any]]):
        """Cập nhật Hot Cache phục vụ Leaflet Dashboard tức thì (< 3ms) theo cơ chế cộng dồn (Cumulative Ingestion)."""
        current_time = int(time.time())
        retention_window = 86400  # Giữ lại toàn bộ tin tức trong vòng 24 giờ qua (3 tầng độ tươi)

        # 1. TẬP HỢP TẤT CẢ SỰ KIỆN HIỆN CÓ:
        # Nạp từ Redis và STREAM_STATE_FILE để đảm bảo PySpark KHÔNG BAO GIỜ ghi đè làm mất các tin do Apify cào sâu
        combined_map = {}

        # a. Từ Redis Serving Store
        if self.redis_client:
            try:
                keys = self.redis_client.keys("flood:event:*")
                if keys:
                    pipe = self.redis_client.pipeline()
                    for k in keys:
                        pipe.get(k)
                    vals = pipe.execute()
                    for v in vals:
                        if v:
                            try:
                                ev = json.loads(v)
                                cid = ev.get("canonical_id") or ev.get("id")
                                if cid:
                                    combined_map[cid] = ev
                            except Exception:
                                pass
            except Exception as e:
                print(f"[Spark Engine] Cảnh báo đọc Redis: {e}")

        # b. Từ file đệm cục bộ STREAM_STATE_FILE
        if os.path.exists(STREAM_STATE_FILE):
            try:
                with open(STREAM_STATE_FILE, "r", encoding="utf-8") as sf:
                    file_data = json.load(sf)
                    for ev in file_data.get("events", []):
                        cid = ev.get("canonical_id") or ev.get("id")
                        if cid and cid not in combined_map:
                            combined_map[cid] = ev
            except Exception:
                pass

        # c. Từ in-memory cache của Spark
        for ev in self.active_events_cache:
            cid = ev.get("canonical_id") or ev.get("id")
            if cid and cid not in combined_map:
                combined_map[cid] = ev

        report_ids = {report_id for ev in new_events for report_id in ev.get("report_ids", [])}
        if report_ids:
            combined_map = {
                cid: ev for cid, ev in combined_map.items()
                if cid not in report_ids and report_ids.isdisjoint(ev.get("report_ids", []))
            }

        # d. Thêm snapshot cụm đã cập nhật
        for ev in new_events:
            cid = ev.get("canonical_id") or ev.get("id")
            if cid:
                combined_map[cid] = ev

        # 2. LỌC VÀ KHỬ TRÙNG LẶP THEO CHỮ KÝ NGỮ NGHĨA
        # Áp dụng cơ chế cộng dồn (Cumulative Merge): Google RSS (M) + Bing (N) + Apify (K) = M + N + K
        deduped = []
        seen_ids = set()
        seen_semantics = set()

        all_candidate_events = list(combined_map.values())

        if self.mode == "live":
            # CHẾ ĐỘ LIVE: CHẶN 100% BẢN GHI SIMULATION!
            # Giữ lại TOÀN BỘ các tin trong vòng 24 giờ qua (<= 86400s) cho mọi nền tảng
            filtered_candidates = [
                ev for ev in all_candidate_events
                if ev.get("platform") not in ["simulation", "sim"]
                and not str(ev.get("canonical_id", "")).startswith("sim_")
                and ev.get("crawler_source") != "simulation_replayer"
                and (current_time - (ev.get("create_time", 0) or ev.get("timestamp", 0))) <= retention_window
            ]
        else:
            filtered_candidates = [
                ev for ev in all_candidate_events
                if ev.get("platform") in ["simulation", "sim"] or str(ev.get("canonical_id", "")).startswith("sim_")
            ]

        for ev in filtered_candidates:
            cid = str(ev.get("canonical_id") or ev.get("id") or "")
            loc = ev.get("location", {}) or {}
            street = str(loc.get("street") or "")
            opinion = str(ev.get("opinion") or "")
            txt = str(ev.get("text") or ev.get("title") or "")[:35].strip().lower()
            sem_sig = (street.lower(), opinion.lower(), txt)

            if cid and cid in seen_ids:
                continue
            if street and sem_sig in seen_semantics:
                continue

            if cid:
                seen_ids.add(cid)
            if street:
                seen_semantics.add(sem_sig)
            deduped.append(ev)

        # 3. TÍNH TOÁN LẠI 3 TẦNG ĐỘ TƯƠI CHO TOÀN BỘ DANH SÁCH
        for ev in deduped:
            ctime = ev.get("create_time", 0) or ev.get("timestamp", 0)
            age = max(0, current_time - ctime) if ctime > 0 else 0
            if age <= 7200:
                ev["freshness"] = "strict_2h"
                ev["status_tag"] = "🔴 ĐANG DIỄN RA (< 2 GIỜ)"
            elif age <= 14400:
                ev["freshness"] = "recent_4h"
                ev["status_tag"] = "🟠 ĐỢT MƯA VỪA DỨT (2-4 GIỜ)"
            else:
                ev["freshness"] = "within_24h"
                ev["status_tag"] = "🟡 CẢNH BÁO TRONG NGÀY (4-24 GIỜ)"

            ev["relative_time"] = format_relative_time(ctime, current_time)

        # Ưu tiên sắp xếp: Tin trong 2 giờ -> MXH (TikTok/Facebook/Threads/YouTube) -> Trọng số -> Thời gian
        deduped.sort(key=lambda x: (
            2 if x.get("freshness") == "strict_2h" or (current_time - (x.get("create_time", 0) or x.get("timestamp", 0))) <= 7200 else (
                1 if x.get("freshness") == "recent_4h" or (current_time - (x.get("create_time", 0) or x.get("timestamp", 0))) <= 14400 else 0
            ),
            1 if x.get("platform") in ["tiktok", "facebook", "threads", "youtube"] else 0,
            x.get("weight", 1.0),
            x.get("create_time", 0) or x.get("timestamp", 0)
        ), reverse=True)

        self.active_events_cache = deduped

        has_apify = any(ev.get("crawler_source") in ["apify_facebook", "apify_tiktok"] for ev in deduped)
        window_title = "Google RSS + Bing + Apify Deep Crawl (24h)" if has_apify else "Google RSS + Bing Streaming (24h)"

        out_data = {
            "mode": f"live_streaming_spark_{self.mode}",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "window": window_title,
            "events_count": len(deduped),
            "events": deduped
        }

        # 4. GHI REDIS THEO CƠ CHẾ UPSERT (< 3ms)
        self._hot_needs_retry = REDIS_AVAILABLE and self.redis_client is None
        if self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                pipe.delete("flood:geo:index", "flood:timeline:zset")
                for ev in deduped:
                    cid = ev.get("canonical_id") or ev.get("id")
                    if not cid:
                        continue
                    loc = ev.get("location", {}) or {}
                    lat = loc.get("lat") or ev.get("lat")
                    lon = loc.get("lon") or ev.get("lon")
                    ctime = ev.get("create_time") or ev.get("timestamp") or current_time

                    if lat and lon:
                        pipe.geoadd("flood:geo:index", (lon, lat, cid))
                    pipe.zadd("flood:timeline:zset", {cid: ctime})
                    pipe.set(f"flood:event:{cid}", json.dumps(ev, ensure_ascii=False), ex=86400)

                pipe.set("flood:serving:mode", self.mode)
                pipe.set("flood:serving:window", window_title)
                pipe.set("flood:serving:updated_at", current_time)
                pipe.execute()
            except Exception as e:
                self._hot_needs_retry = True
                print(f"[Spark Engine] Lỗi ghi Redis: {e}")

        # 5. GHI FILE ĐỆM CỤC BỘ NGUYÊN TỬ (Atomic Replace)
        try:
            write_json_atomic(STREAM_STATE_FILE, out_data)
        except Exception as e:
            self._hot_needs_retry = True
            print(f"[Spark Engine] Lỗi ghi file đệm: {e}")

    def _recover_hot_snapshot(self):
        if not getattr(self, "_hot_needs_retry", False) or time.monotonic() < self._hot_retry_at:
            return
        self._hot_retry_at = time.monotonic() + 10
        if self.redis_client is None:
            self.redis_client = self._init_redis()
        self._publish_verified_batch([], batch_id=0)

    def _append_cold_lakehouse(self, events: List[Dict[str, Any]]):
        """Lưu trữ sự kiện vào Medallion Lakehouse Cold Path theo phân vùng."""
        for ev in events:
            event_time = ev.get("create_time") or ev.get("timestamp") or int(time.time())
            target = self._normalized_path(event_time, ev["report_version"])
            if not target.exists():
                write_json_atomic(target, ev, durable=True)

    def _normalized_path(self, event_time, version):
        date = datetime.fromtimestamp(event_time, timezone.utc).strftime("%Y-%m-%d")
        episode = determine_episode_id(event_time)
        return Path(LAKEHOUSE_DIR) / f"episode_id={episode}" / f"date={date}" / f"report-{self.mode}-{version}.jsonl"

    def _process_ingress_batch(self, records, batch_id):
        distinct = {self._fingerprint(record): record for record in records}
        pending = {}
        recovered = []
        for version, record in distinct.items():
            target = Path(LAKEHOUSE_DIR).parent / "raw_reports" / self.mode / version[:2] / f"{version}.jsonl"
            if not target.exists():
                write_json_atomic(target, record, durable=True)
            event_time = record.get("create_time") or record.get("timestamp")
            if isinstance(event_time, (int, float)) and 0 < event_time < 4102444800:
                try:
                    with self._normalized_path(event_time, version).open(encoding="utf-8") as stream:
                        recovered.append(json.load(stream))
                    continue
                except FileNotFoundError:
                    pass
            pending[version] = record
        if recovered:
            self._publish_verified_batch(recovered, batch_id)
        if not pending:
            return
        try:
            spark_records = [dict(record, _source_version=version) for version, record in pending.items()]
            df = self._create_ingress_frame(spark_records)
            self.process_micro_batch(df, batch_id=batch_id, raw_records=list(pending.values()))
        except OSError:
            raise
        except Exception as error:
            print(f"[Spark Engine Warning] Lỗi micro-batch #{batch_id}: {error}")
            self._fallback_process_records(list(pending.values()), batch_id=batch_id)

    def _create_ingress_frame(self, records):
        return self.spark.createDataFrame(records, schema=EVENT_SCHEMA)

    def _decode_ingress_record(self, payload, topic, partition, offset):
        try:
            value = json.loads(payload.decode("utf-8")) if payload is not None else None
            if not isinstance(value, dict):
                raise ValueError("Expected a JSON object")
        except (ValueError, RecursionError) as error:
            self.send_dlq("KafkaPayloadError", str(error), {
                "topic": topic, "partition": partition, "offset": offset,
                "value": payload.decode("utf-8", errors="backslashreplace") if payload is not None else None,
            })
            return None
        if self.mode == "live" and (
            value.get("platform") in ("simulation", "sim")
            or str(value.get("canonical_id", "")).startswith("sim_")
        ):
            return None
        return value

    def start_kafka_streaming(self, bootstrap_servers: str = "localhost:9092", topics: Optional[List[str]] = None, batch_interval_sec: float = 1.0):
        """Lắng nghe sự kiện từ Kafka Topics và chạy xử lý phân tán qua Spark."""
        if topics is None:
            if self.mode == "live":
                # Chế độ LIVE: Chỉ lắng nghe topic thời gian thực, TUYỆT ĐỐI không nghe topic mô phỏng
                topics = ["social.live.raw"]
            else:
                # Chế độ SIMULATION: Lắng nghe topic mô phỏng
                topics = ["social.sim.raw"]

        if not KAFKA_AVAILABLE:
            print("[PySpark Stream Error] Thư viện kafka-python chưa được cài đặt!")
            self._start_buffer_watcher(topics, batch_interval_sec)
            return

        max_batch_size = 15
        print(f"\n[*] Đang kết nối tới Kafka Broker ({bootstrap_servers}) cho topics: {topics}...")
        batch_counter = 0
        while True:
            try:
                consumer = KafkaConsumer(
                    *topics,
                    bootstrap_servers=bootstrap_servers,
                    auto_offset_reset='earliest',
                    enable_auto_commit=False,
                    group_id=f'pyspark-flood-{self.mode}-streaming-group',
                    consumer_timeout_ms=1000,
                    max_poll_records=max_batch_size,
                )
                print(f"[*] Kafka → PySpark ({self.mode.upper()}) đang sẵn sàng xử lý các đợt ngập...")
                break
            except KafkaConfigurationError:
                raise
            except Exception as error:
                print(f"[PySpark Stream Warning] Đang dùng file đệm, sẽ kết nối lại Kafka: {error}")
                batch_counter = self._drain_buffer(topics, batch_counter, max_batch_size)
                self._recover_hot_snapshot()
                time.sleep(batch_interval_sec)

        try:
            while True:
                records = []
                msg_pack = consumer.poll(timeout_ms=1000)
                for messages in msg_pack.values():
                    for msg in messages:
                        value = self._decode_ingress_record(msg.value, msg.topic, msg.partition, msg.offset)
                        if value is not None:
                            records.append(value)

                for start in range(0, len(records), max_batch_size):
                    batch_counter += 1
                    self._process_ingress_batch(records[start:start + max_batch_size], batch_counter)
                if msg_pack:
                    consumer.commit({
                        partition: OffsetAndMetadata(messages[-1].offset + 1, "")
                        for partition, messages in msg_pack.items() if messages
                    })
                batch_counter = self._drain_buffer(topics, batch_counter, max_batch_size)
                self._recover_hot_snapshot()
        except KeyboardInterrupt:
            print("\n[*] Dừng luồng PySpark Streaming theo lệnh người dùng.")
        finally:
            consumer.close()

    def _start_buffer_watcher(self, topics: List[str], batch_interval_sec: float = 2.0):
        """Consume finished spool files while Kafka is unavailable."""
        batch_counter = 0
        while True:
            batch_counter = self._drain_buffer(topics, batch_counter, 15)
            self._recover_hot_snapshot()
            time.sleep(batch_interval_sec)

    def _drain_buffer(self, topics, batch_counter, batch_size):
        for topic in topics:
            folder = Path(DATA_DIR) / "lakehouse" / "_ingress_spool" / topic
            legacy = Path(DATA_DIR) / f"buffer_{topic}.jsonl"
            if legacy.exists():
                folder.mkdir(parents=True, exist_ok=True)
                legacy.replace(folder / f"legacy-{time.time_ns()}.jsonl")
            files = sorted(folder.glob("*.jsonl"))[:batch_size]
            records = []
            for path in files:
                with path.open(encoding="utf-8", errors="backslashreplace") as stream:
                    for line_number, line in enumerate(stream, start=1):
                        if not line.strip():
                            continue
                        try:
                            value = json.loads(line)
                            if not isinstance(value, dict):
                                raise ValueError("Expected a JSON object")
                        except (ValueError, RecursionError) as error:
                            self.send_dlq("LocalBufferPayloadError", str(error), {
                                "file": path.name, "line": line_number, "value": line.rstrip(),
                            })
                            continue
                        if self.mode == "live" and (
                            value.get("platform") in ("simulation", "sim")
                            or str(value.get("canonical_id", "")).startswith("sim_")
                        ):
                            continue
                        records.append(value)
                        if len(records) == batch_size:
                            batch_counter += 1
                            self._process_ingress_batch(records, batch_counter)
                            records = []
            if records:
                batch_counter += 1
                self._process_ingress_batch(records, batch_counter)
            for path in files:
                path.unlink()
        return batch_counter

    def _fallback_process_records(self, raw_records: List[Dict[str, Any]], batch_id: int):
        """Fallback an toàn xử lý trực tiếp bản ghi nếu Spark Session gặp lỗi môi trường."""
        verified_batch = []
        for record in raw_records:
            try:
                raw_text = record.get("text") or record.get("title") or ""
                cleaned_txt = clean_stream_text(raw_text) or raw_text.strip()
                if len(cleaned_txt) < 8:
                    self.send_dlq("CorruptedTextError", "Text length too short", record)
                    continue
                matched = match_hotspot(cleaned_txt) or {}
                spatial, lat, lon = self._select_location(record, matched)
                st_name = spatial.get("street") or ""
                off_w = spatial.get("ward") or "Toàn TP.HCM"

                ctime = record.get("create_time") or record.get("timestamp") or int(time.time())
                event_payload = {
                    "id": str(record.get("id")),
                    "canonical_id": record.get("canonical_id") or f"{record.get('platform')}_{record.get('id')}",
                    "platform": record.get("platform", "live_crawler" if self.mode == "live" else "simulation"),
                    "media_type": record.get("media_type", "post"),
                    "author": record.get("author", "Người dân TP.HCM"),
                    "text": cleaned_txt,
                    "create_time": ctime,
                    "created_at_iso": record.get("created_at_iso", datetime.now(timezone.utc).isoformat()),
                    "timestamp": ctime,
                    "relative_time": record.get("relative_time") or format_relative_time(ctime),
                    "freshness": record.get("freshness") or "within_24h",
                    "status_tag": record.get("status_tag") or "🟡 CẢNH BÁO TRONG NGÀY (4-24 GIỜ)",
                    "location": {
                        "street": st_name,
                        "display_name": spatial.get("display_name") or st_name or off_w,
                        "ward": off_w,
                        "administrative_unit": off_w,
                        "district": spatial.get("district") or "TP.HCM",
                        "lat": lat,
                        "lon": lon,
                        "heat_points": [[lat, lon]],
                        "cause": "rain",
                        "cause_label": "Mưa lớn",
                        "source": "fallback_streaming_engine"
                    },
                    "aspect": st_name or off_w,
                    "opinion": "ngập nước",
                    "severity": "medium",
                    "weight": 2.0,
                    "url": record.get("url", "")
                }
                self._preserve_source_fields(event_payload, record, spatial)
                reference_time = event_payload.get("historical_timestamp") or ctime
                verified_batch.append(self.veracity_checker.verify_event(event_payload, reference_time=reference_time))
            except (ValueError, TypeError, AttributeError, OverflowError) as error:
                self.send_dlq("RecordProcessingError", str(error), record)

        if verified_batch:
            self._publish_verified_batch(verified_batch, batch_id)

    def run_batch_simulation_job(self, input_records: List[Dict[str, Any]]):
        """Chạy một job xử lý lô hoàn chỉnh trên Spark (Dùng cho kiểm thử & benchmark)."""
        if not input_records:
            return
        self._process_ingress_batch(input_records, batch_id=1)

    def stop(self):
        if self.spark:
            self.spark.stop()


if __name__ == "__main__":
    from bigdata.streaming.structured_flood_stream import main

    main()
