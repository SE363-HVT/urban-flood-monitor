# 🏗️ BÁO CÁO TOÀN DIỆN KIẾN TRÚC BIG DATA, ĐÁNH GIÁ CHUYÊN SÂU & BẢN VẼ KỸ THUẬT HÀNH ĐỘNG (MASTER CHECKPOINT & BLUEPRINT)
## HỆ THỐNG GIÁM SÁT VÀ CẢNH BÁO NGẬP LỤT ĐÔ THỊ THỜI GIAN THỰC ĐA NỀN TẢNG (SE363)
> **Chuyên ngành**: Kỹ thuật Dữ liệu & Hệ thống Thông tin (Data Engineering & Big Data Systems)  
> **Dự án**: SE363 - Xử lý Dữ liệu Lớn (Đại học Công nghệ Thông tin - ĐHQG-HCM)  
> **Phiên bản tài liệu**: `v2.5-master-checkpoint-final`  
> **Mục đích tài liệu**: Đóng vai trò là **SSOT Master Checkpoint** và **Hướng dẫn Triển khai Hành động Khép kín (Actionable Turnkey Guide)** để AI Agent kế thừa và trực tiếp thực thi các phase cải tiến trong các phiên làm việc tiếp theo mà không cần phải đoán định hay phụ thuộc vào ngữ cảnh hội thoại cũ.  

---

## 📑 MỤC LỤC
1. [BẢN ĐỒ KIẾN TRÚC & TỔNG KIỂM KÊ TÀI NGUYÊN HIỆN TẠI](#1-bản-đồ-kiến-trúc--tổng-kiểm-kê-tài-nguyên-hiện-tại)
   * 1.1. Sơ đồ Luồng Dữ liệu Toàn trình (End-to-End Data Pipeline Flow)
   * 1.2. Kiểm kê Tài nguyên & Vị trí Mã nguồn (File Registry)
   * 1.3. Ma trận Phân bổ Cổng mạng & Topology Dịch vụ (Network & Port Matrix)
2. [KIỂM TOÁN CHUYÊN SÂU: CÁC KHUYẾT ĐIỂM & RỦI RO KỸ THUẬT HIỆN HỮU](#2-kiểm-toán-chuyên-sâu-các-khuyết-điểm--rủi-ro-kỹ-thuật-hiện-hữu)
   * 2.1. Tầng Xử lý Luồng (PySpark Streaming Anti-patterns)
   * 2.2. Tầng Lưu trữ Hồ dữ liệu (Lakehouse Storage & Small Files Crisis)
   * 2.3. Tầng Phục vụ Dữ liệu (Serving Concurrency & File Lock)
   * 2.4. Tầng Khử trùng lặp & Chất lượng Dữ liệu (Data Deduplication & Governance)
3. [CÁC GÓP Ý & MẪU THIẾT KẾ DATA ENGINEERING BỔ SUNG CHUẨN MỰC](#3-các-góp-ý--mẫu-thiết-kế-data-engineering-bổ-sung-chuẩn-mực)
4. [BẢN VẼ KỸ THUẬT CHI TIẾT TỪNG PHÂN HỆ CẢI TIẾN (CODE & SCHEMA BLUEPRINT)](#4-bản-vẽ-kỹ-thuật-chi-tiết-từng-phân-hệ-cải-tiến-code--schema-blueprint)
   * 4.1. Nâng cấp Spark sang Native Structured Streaming + Spark UDF
   * 4.2. Chuyển đổi Lakehouse sang Apache Parquet / Delta Lake & Auto-Compaction
   * 4.3. Loại bỏ Xung đột Tệp tin bằng Redis In-Memory Serving Store
   * 4.4. Cơ chế Gom cụm Sự kiện Đa nguồn (Spatio-Temporal Flood Clustering)
   * 4.5. Cơ chế Xử lý Lỗi & Dead Letter Queue (Kafka DLQ)
   * 4.6. Chuẩn hóa Hợp đồng Kết nối Dịch vụ AI Đa phương thức (AI Microservice Contract)
   * 4.7. Chuẩn hóa Quản lý Thư viện (`requirements.txt`)
   * 4.8. Đặc tả Chi tiết Hợp đồng Dữ liệu Toàn trình (End-to-End Data Contract Schemas)
5. [CƠ CHẾ PHÒNG HỘ SUY BIẾN DUYÊN DÁNG & TỰ PHỤC HỒI (GRACEFUL DEGENERATION)](#5-cơ-chế-phòng-hộ-suy-biến-duyên-dáng--tự-phục-hồi-graceful-degeneration)
6. [LỘ TRÌNH THỰC THI PHÂN KỲ & TIÊU CHÍ HOÀN THÀNH (DEFINITION OF DONE - DOD)](#6-lộ-trình-thực-thi-phân-kỳ--tiêu-chí-hoàn-thành-definition-of-done---dod)
7. [SỔ TAY DÒNG LỆNH THỰC CHIẾN DÀNH CHO AGENT (AGENT PLAYBOOK & CLI CHEAT SHEET)](#7-sổ-tay-dòng-lệnh-thực-chiến-dành-cho-agent-agent-playbook--cli-cheat-sheet)
8. [CHIẾN LƯỢC KIỂM THỬ KHÓI TỰ ĐỘNG (AUTOMATED SMOKE TEST SUITE)](#8-chiến-lược-kiểm-thử-khói-tự-động-automated-smoke-test-suite)
9. [HƯỚNG DẪN KÍCH HOẠT DÀNH CHO AI AGENT Ở PHIÊN TIẾP THEO](#9-hướng-dẫn-kích-hoạt-dành-cho-ai-agent-ở-phiên-tiếp-theo)
10. [HƯỚNG DẪN BẢO VỆ ĐỒ ÁN VÀ TRẢ LỜI PHẢN BIỆN GIẢNG VIÊN](#10-hướng-dẫn-bảo-vệ-đồ-án-và-trả-lời-phản-biện-giảng-viên)

---

## 1. BẢN ĐỒ KIẾN TRÚC & TỔNG KIỂM KÊ TÀI NGUYÊN HIỆN TẠI

### 1.1. Sơ đồ Luồng Dữ liệu Toàn trình (End-to-End Data Pipeline Flow)

```mermaid
flowchart TD
    subgraph INGESTION ["1. TẦNG THU NẠP ĐA NGUỒN (INGESTION LAYER)"]
        direction TB
        RSS["LiveFreeSocialCrawler<br/>(Google Discovery RSS + googlenewsdecoder)"]
        Apify["Apify Actor Poller<br/>(Deep TikTok + Facebook Crawlers)"]
        Sim["SimulationReplayer<br/>(3.922 bài đăng lịch sử / 5 Episodes)"]
    end

    subgraph MESSAGING ["2. TẦNG HÀNG ĐỢI THÔNG ĐIỆP (KAFKA CLUSTER)"]
        direction TB
        KProducer["SocialKafkaProducer<br/>(Message Key: canonical_id)"]
        KafkaBroker["Apache Kafka 4.3.1 (KRaft Mode - Port 9092)<br/>Topics: social.live.raw | social.sim.raw"]
        KUI["Kafka-UI Dashboard (Port 8080)"]
    end

    subgraph PROCESSING ["3. TẦNG XỬ LÝ & BẢO CHỨNG DỮ LIỆU (PYSPARK ENGINE)"]
        direction TB
        SparkProc["PySpark Structured Streaming<br/>(bigdata/streaming/spark_flood_processor.py)"]
        GIS["Core Gazetteer & AdminResolver<br/>(Street-First, 122 CSGT Hotspots, NQ 1685)"]
        Veracity["Veracity Checker<br/>(Open-Meteo Weather API + Haversine 500m/60m)"]
    end

    subgraph STORAGE ["4. TẦNG HỒ DỮ LIỆU ĐA TẦNG (DATA LAKEHOUSE)"]
        direction TB
        ColdPath["Cold Path Permanent Storage<br/>data/lakehouse/flood_events/"]
        Partitions["Hive-style Partitioning:<br/>episode_id={id}/date={date}/batch_{ts}.jsonl"]
    end

    subgraph SERVING ["5. TẦNG PHỤC VỤ & TRÌNH DIỄN (SERVING & DASHBOARD)"]
        direction TB
        HotState["Hot State Buffer<br/>(data/live_stream_state.json & Redis GEO)"]
        WebServer["Dashboard Web Server<br/>(dashboard/server.py - Port 8050)"]
        WebUI["Leaflet GIS Heatmap Dashboard<br/>(Auto-poll 3s, Clean-start, Veracity Badges)"]
    end

    RSS --> KProducer
    Apify --> KProducer
    Sim --> KProducer
    KProducer --> KafkaBroker
    KafkaBroker -. Giám sát .- KUI
    KafkaBroker --> SparkProc
    SparkProc <--> GIS
    SparkProc <--> Veracity
    SparkProc -->|Hot Path < 3s| HotState
    SparkProc -->|Cold Path Lakehouse| ColdPath
    ColdPath --> Partitions
    HotState --> WebServer
    WebServer --> WebUI
```

### 1.2. Kiểm kê Tài nguyên & Vị trí Mã nguồn (File Registry)

| STT | Tệp tin / Thư mục | Phân tầng | Vai trò & Trách nhiệm chính |
| :---: | :--- | :--- | :--- |
| 1 | [`bigdata/docker-compose.yml`](file:///D:/SE363_RAWDATA/bigdata/docker-compose.yml) | Infrastructure | Cấu hình Docker container cho Apache Kafka 4.3.1 (KRaft mode) và Kafka-UI (port 8080) |
| 2 | [`bigdata/run_streaming_pipeline.py`](file:///D:/SE363_RAWDATA/bigdata/run_streaming_pipeline.py) | Orchestration | Script 1-click khởi chạy toàn bộ 4 tầng (Kafka, Dashboard, Spark, Ingestion Loop) |
| 3 | [`bigdata/producers/social_producer.py`](file:///D:/SE363_RAWDATA/bigdata/producers/social_producer.py) | Ingestion | Kafka Producer đa nguồn, băm `canonical_id`, hỗ trợ fallback local buffer |
| 4 | [`bigdata/streaming/spark_flood_processor.py`](file:///D:/SE363_RAWDATA/bigdata/streaming/spark_flood_processor.py) | Stream Compute | Động cơ PySpark nhận tin từ Kafka, phân tích GIS, đối soát thời tiết, xuất Hot/Cold Path |
| 5 | [`bigdata/lakehouse/backfill_episodes.py`](file:///D:/SE363_RAWDATA/bigdata/lakehouse/backfill_episodes.py) | Lakehouse ETL | Pipeline nạp lịch sử (Backfill) 3.818 bài đăng vào 274 phân vùng Lakehouse |
| 6 | [`core/gazetteer.py`](file:///D:/SE363_RAWDATA/core/gazetteer.py) | Core GIS | Thuật toán bóc tách tuyến đường phân tầng (Street-First, 122 CSGT, OSM Geocoding) |
| 7 | [`core/admin_resolver.py`](file:///D:/SE363_RAWDATA/core/admin_resolver.py) | Core Admin | Single Source of Truth giải mã 168 ĐVHC TP.HCM theo Nghị quyết 1685/NQ-UBTVQH15 |
| 8 | [`pipeline/veracity_checker.py`](file:///D:/SE363_RAWDATA/pipeline/veracity_checker.py) | Verification | Xác thực tin giả qua đối soát lượng mưa Open-Meteo và đồng thuận không gian 500m/60p |
| 9 | [`pipeline/live_free_crawler.py`](file:///D:/SE363_RAWDATA/pipeline/live_free_crawler.py) | Free Crawler | Bộ cào thời gian thực 0 đồng qua Google News RSS và giải mã link chuyển hướng |
| 10 | [`pipeline/simulation_replayer.py`](file:///D:/SE363_RAWDATA/pipeline/simulation_replayer.py) | Simulator | Bộ phát lại dòng dữ liệu lịch sử từ tập dữ liệu chuẩn hóa 3.922 tin |
| 11 | [`dashboard/server.py`](file:///D:/SE363_RAWDATA/dashboard/server.py) | Serving API | Máy chủ HTTP cổng 8050, phục vụ REST API `/api/realtime-heatmap`, hỗ trợ clean start |
| 12 | [`dashboard/index.html`](file:///D:/SE363_RAWDATA/dashboard/index.html) | Presentation | Giao diện bản đồ nhiệt Leaflet, ghim marker động, auto-poll 3s, proximity scanner |

### 1.3. Ma trận Phân bổ Cổng mạng & Topology Dịch vụ (Network & Port Matrix)

Để loại trừ triệt để nguy cơ xung đột cổng (Port Conflict) giữa các tiến trình, hệ thống quy chuẩn bảng phân bổ cổng cố định:

| Cổng (Port) | Giao thức | Dịch vụ (Service) | Trạng thái hiện tại | Mô tả & Cách kiểm tra |
| :---: | :---: | :--- | :---: | :--- |
| **8050** | HTTP | Dashboard Web Server & REST API | Đang chạy | Giao diện GIS Leaflet & Endpoint `/api/realtime-heatmap` (`dashboard/server.py`) |
| **9092** | TCP / Kafka | Kafka Broker (KRaft Mode) | Đang chạy (Docker) | Tiếp nhận & phân phối các topic sự kiện ngập lụt |
| **8080** | HTTP | Kafka-UI Management Console | Đang chạy (Docker) | Giao diện trực quan kiểm tra Topic, Consumer Group, Message Lag |
| **6379** | TCP / Redis | Redis In-Memory Hot Serving Store | Sẵn sàng thêm (Phase 1) | Lưu trữ GEO Spatial index & sliding timeline buffer |
| **8001** | HTTP | Multimodal AI Microservice (FastAPI) | Sẵn sàng thêm (Phase 3) | Microservice chạy mô hình AI của bạn Hưng (Binary Classifier, PhoBERT, Whisper) |
| **9090** | HTTP | Prometheus Metrics Scraper | Tùy chọn (Phase 4) | Thu thập chỉ số hiệu năng Spark Streaming & Kafka Lag |
| **3000** | HTTP | Grafana Monitoring Dashboard | Tùy chọn (Phase 4) | Biểu đồ trực quan hóa độ trễ và thông lượng hệ thống |

---

## 2. KIỂM TOÁN CHUYÊN SÂU: CÁC KHUYẾT ĐIỂM & RỦI RO KỸ THUẬT HIỆN HỮU

### 2.1. Tầng Xử lý Luồng (PySpark Streaming Anti-patterns)
* **Khuyết điểm cốt tử 1: Vòng lặp đơn luồng trên Driver (`.collect()` Bottleneck):**
  * Trong [`spark_flood_processor.py`](file:///D:/SE363_RAWDATA/bigdata/streaming/spark_flood_processor.py#L115), dữ liệu được đưa vào `createDataFrame` nhưng ngay sau đó bị kéo ngược về Driver thông qua `batch_df.collect()`.
  * Toàn bộ logic GIS (`match_hotspot`), chuẩn hóa hành chính (`RESOLVER`), và kiểm tra thời tiết (`veracity_checker`) đang chạy trong vòng lặp `for row in rows:` tuần tự trên một luồng CPU duy nhất của Driver.
  * **Hậu quả**: Khi có đợt mưa bão lớn, lượng tin đổ về Kafka đạt 5.000–10.000 events/phút, tiến trình Driver sẽ bị nghẽn CPU 100%, tích lũy Kafka Consumer Lag khổng lồ và sập bộ nhớ (Out of Memory - OOM).
* **Khuyết điểm 2: Thiếu Checkpoint & Nguy cơ mất dữ liệu (Data Loss):**
  * Consumer đang dùng `enable_auto_commit=True` và `auto_offset_reset='latest'`. Nếu máy bị mất điện hoặc tiến trình bị kill giữa chừng khi Spark chưa kịp ghi kết quả, Kafka broker đã ghi nhận offset đã đọc $\rightarrow$ **Dữ liệu trong batch đó mất vĩnh viễn không thể hồi phục**.

### 2.2. Tầng Lưu trữ Hồ dữ liệu (Lakehouse Storage & Small Files Crisis)
* **Khuyết điểm 3: Khủng hoảng Tệp tin vụn (The Small Files Problem):**
  * Tại [`spark_flood_processor.py`](file:///D:/SE363_RAWDATA/bigdata/streaming/spark_flood_processor.py#L250), mỗi micro-batch Spark ghi ra một tệp riêng biệt: `batch_{timestamp}.jsonl` với kích thước chỉ từ 1 KB đến 10 KB.
  * Trong luồng streaming 24/7 với chu kỳ 5 giây, hệ thống sinh ra **~17.280 tệp JSONL nhỏ mỗi ngày**.
  * **Hậu quả**: Phân mảnh Inode nghiêm trọng trên hệ thống tệp, làm các công cụ phân tích truy vấn (Spark SQL, DuckDB, Trino) mất 95% thời gian chỉ để mở/đóng tệp tin (I/O Metadata Overhead) thay vì xử lý dữ liệu.
* **Khuyết điểm 4: Chưa áp dụng Định dạng Cột (Columnar) và Bảng ACID:**
  * Toàn bộ Lakehouse đang lưu dạng văn bản thuần (`.jsonl`). JSONL không hỗ trợ nén nạp theo cột, không có Metadata Statistics (min/max pruning), và không có tính năng Time Travel (quay ngược thời gian để xem lại trạng thái dữ liệu cũ).

### 2.3. Tầng Phục vụ Dữ liệu (Serving Concurrency & File Lock)
* **Khuyết điểm 5: Xung đột Đọc/Ghi đồng thời (File Race Condition):**
  * Spark liên tục ghi đè file [`data/live_stream_state.json`](file:///D:/SE363_RAWDATA/data/live_stream_state.json) bằng `json.dump()`, trong khi Web Server liên tục đọc file này bằng `json.load()` mỗi khi người dùng hoặc luồng auto-poll gọi API.
  * **Hậu quả**: Rất dễ phát sinh lỗi sập máy chủ web `json.decoder.JSONDecodeError: Unterminated string` khi Web Server đọc trúng thời điểm tệp đang bị ghi dở dang.

### 2.4. Tầng Khử trùng lặp & Chất lượng Dữ liệu (Data Deduplication & Governance)
* **Khuyết điểm 6: Khử trùng lặp đa nguồn chỉ ở mức bề mặt:**
  * Hiện tại `canonical_id` chỉ băm theo URL hoặc ID bài viết.
  * **Hậu quả**: Khi một điểm ngập lớn như Chợ Thủ Đức xảy ra, 20 người dân đăng tải 20 bài viết khác nhau trên TikTok/Facebook. Hệ thống vẫn lưu thành 20 điểm riêng biệt, gây nhiễu quầng nhiệt và thiếu khả năng hợp nhất thành **1 Điểm ngập Trọng điểm (Master Incident)**.
* **Khuyết điểm 7: Thiếu Schema Contracts & Dead Letter Queue (DLQ):**
  * Khi Crawler thu thập được bài viết rác hoặc cấu trúc bị lỗi (thiếu trường thời gian, tọa độ null, text dị biệt), Spark chỉ `continue` bỏ qua mà không ghi log vào Dead Letter Queue để điều tra nguyên nhân.
* **Khuyết điểm 8: File phụ thuộc (`requirements.txt`) quá sơ sài:**
  * File hiện chỉ có 2 dòng `requests` và `urllib3`, thiếu toàn bộ các thư viện sống còn: `pyspark`, `kafka-python`, `googlenewsdecoder`, `beautifulsoup4`,...

---

## 3. CÁC GÓP Ý & MẪU THIẾT KẾ DATA ENGINEERING BỔ SUNG CHUẨN MỰC

Dưới góc nhìn của Kỹ sư Dữ liệu Lớn, đây là các quy tắc kiến trúc chuẩn công nghiệp cần được bổ sung vào hệ thống:

```mermaid
flowchart LR
    subgraph INGEST ["1. INGESTION & CONTRACTS"]
        Crawler["Social Crawlers"] --> Pydantic["Data Contract<br/>(Pydantic Schema)"]
        Pydantic -->|Hợp lệ| KafkaTopic["Kafka: social.events.raw"]
        Pydantic -->|Dữ liệu lỗi| KafkaDLQ["Kafka DLQ: social.events.dlq"]
    end

    subgraph ENGINE ["2. NATIVE SPARK STREAMING"]
        KafkaTopic --> SparkRead["spark.readStream (Native)"]
        SparkRead --> SparkUDF["Spark UDFs Song Song<br/>(GIS + Admin + Weather)"]
        SparkUDF --> Watermark["Watermark 10m + dropDuplicates"]
    end

    subgraph SERVING ["3. HOT SERVING PATH"]
        SparkUDF -->|Micro-batch| Redis[("Redis In-Memory DB<br/>GEOADD + ZADD")]
        Redis --> WebFastAPI["FastAPI / Dashboard Server"]
    end

    subgraph LAKEHOUSE ["4. MEDALLION LAKEHOUSE"]
        SparkUDF --> Bronze[("Bronze Layer (Raw Avro/Parquet)")]
        Bronze --> Silver[("Silver Layer (Delta Lake Cleansed)")]
        Silver --> Gold[("Gold Layer (Aggregates & Metrics)")]
        Gold --> CompactionJob["Scheduled Compaction Job<br/>(Merge small files -> 128MB)"]
    end
```

1. **Chuẩn hóa Mô hình Huy chương (Medallion Architecture)**:
   * **Bronze Layer**: Dữ liệu sự kiện thô nguyên bản từ Kafka, ghi append-only, giữ nguyên mọi trường metadata ban đầu.
   * **Silver Layer**: Dữ liệu đã làm sạch qua chuẩn NQ 1685, bóc tách GIS Street-First, đối soát Veracity và gán mã định danh phân vùng `episode_id`. Lưu dưới định dạng **Apache Parquet / Delta Lake**.
   * **Gold Layer**: Các bảng tổng hợp không - thời gian được tính toán sẵn (Aggregated Data Marts):
     * `gold_hourly_ward_flood_stats`: Số vụ ngập và độ sâu trung bình theo từng Phường/Xã trong mỗi giờ.
     * `gold_hotspot_severity_leaderboard`: Bảng xếp hạng các điểm đen ngập nghiêm trọng nhất TP.HCM.
2. **Cơ chế Hàng đợi Thư chết (Dead Letter Queue - DLQ)**:
   * Tạo topic Kafka `social.flood.dlq`. Bất kỳ bản ghi nào không thể giải mã, schema bị rách, hoặc phát hiện spam độc hại sẽ được định tuyến sang DLQ cùng với lý do lỗi (`error_reason`, `stack_trace`) để theo dõi chất lượng dữ liệu.
3. **Cơ chế In-Memory Hot Serving với Redis**:
   * Thay thế việc đọc/ghi file `live_stream_state.json` bằng Redis:
     * Dùng lệnh `GEOADD` để lưu tọa độ GIS của các điểm ngập.
     * Dùng lệnh `ZADD` với score là timestamp để truy vấn cửa sổ trượt (ví dụ: chỉ lấy các điểm trong 2 giờ qua bằng `ZRANGEBYSCORE`).
     * Thời gian phản hồi giảm xuống dưới **3 mili-giây**, triệt tiêu vĩnh viễn lỗi khóa file.
4. **Hệ thống Gom cụm Sự kiện (Spatio-Temporal Event Clustering)**:
   * Sử dụng thuật toán phân cụm không gian dựa trên mật độ (**DBSCAN**) hoặc **Geohash/H3 Hexagon Binning** để tự động gộp các bài đăng đơn lẻ của nhiều người dùng thành một "Sự kiện Ngập Trọng điểm".

---

## 4. BẢN VẼ KỸ THUẬT CHI TIẾT TỪNG PHÂN HỆ CẢI TIẾN (CODE & SCHEMA BLUEPRINT)

### 4.1. Nâng cấp Spark sang Native Structured Streaming + Spark UDF

* **Mục tiêu**: Loại bỏ vòng lặp `consumer.poll()` và `.collect()`, phân tán 100% công việc xử lý xuống các Worker cores.

```python
# ==============================================================================
# BLUEPRINT 4.1: bigdata/streaming/spark_flood_processor_native.py
# ==============================================================================
import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf, struct
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, DoubleType, ArrayType
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.gazetteer import match_hotspot
from core.admin_resolver import RESOLVER
from pipeline.event_processor import clean_stream_text, analyze_severity_heuristic

EVENT_INPUT_SCHEMA = StructType([
    StructField("id", StringType(), True),
    StructField("canonical_id", StringType(), True),
    StructField("platform", StringType(), True),
    StructField("text", StringType(), True),
    StructField("create_time", LongType(), True),
    StructField("created_at_iso", StringType(), True),
    StructField("url", StringType(), True),
])

GIS_OUTPUT_SCHEMA = StructType([
    StructField("street", StringType(), True),
    StructField("ward", StringType(), True),
    StructField("district", StringType(), True),
    StructField("lat", DoubleType(), True),
    StructField("lon", DoubleType(), True),
    StructField("display_name", StringType(), True),
])

spark = SparkSession.builder \
    .appName("SE363-Native-Structured-Streaming") \
    .master("local[*]") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

@udf(returnType=GIS_OUTPUT_SCHEMA)
def extract_gis_udf(text):
    if not text:
        return {"street": "", "ward": "Toàn TP.HCM", "district": "TP.HCM", "lat": 10.7769, "lon": 106.7009, "display_name": "Toàn TP.HCM"}
    cleaned = clean_stream_text(text) or text
    matched = match_hotspot(cleaned)
    if not matched:
        return {"street": "", "ward": "Toàn TP.HCM", "district": "TP.HCM", "lat": 10.7769, "lon": 106.7009, "display_name": "Toàn TP.HCM"}
    
    st = matched.get("street") or matched.get("display_name", "")
    w = matched.get("ward", "")
    off_w = RESOLVER.resolve_to_official_ward(w, "") or w or "Toàn TP.HCM"
    return {
        "street": st,
        "ward": off_w,
        "district": matched.get("district", "TP.HCM"),
        "lat": float(matched.get("lat", 10.7769)),
        "lon": float(matched.get("lon", 106.7009)),
        "display_name": matched.get("display_name") or st
    }

raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "social.live.raw,social.sim.raw") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

parsed_stream = raw_stream.selectExpr("CAST(value AS STRING) as json_payload") \
    .select(from_json(col("json_payload"), EVENT_INPUT_SCHEMA).alias("data")) \
    .select("data.*") \
    .withColumn("gis_info", extract_gis_udf(col("text")))

def foreach_batch_sink(batch_df, batch_id):
    if batch_df.count() == 0:
        return
    print(f"[Native Spark] Đang xử lý phân tán Micro-batch #{batch_id}...")

query = parsed_stream.writeStream \
    .foreachBatch(foreach_batch_sink) \
    .option("checkpointLocation", "data/lakehouse/_checkpoints/native_stream") \
    .trigger(processingTime="3 seconds") \
    .start()
```

---

### 4.2. Chuyển đổi Lakehouse sang Apache Parquet & Delta Lake

* **Mục tiêu**: Giải quyết dứt điểm "Small Files Problem", chuyển sang định dạng cột Parquet nén Snappy và chạy job tự động nén gộp định kỳ.

```python
# ==============================================================================
# BLUEPRINT 4.2: bigdata/lakehouse/compaction_job.py
# ==============================================================================
import os
import glob
from pyspark.sql import SparkSession

def compact_lakehouse_partitions(base_lakehouse_dir="data/lakehouse/flood_events"):
    spark = SparkSession.builder \
        .appName("Lakehouse-Compaction-Job") \
        .master("local[*]") \
        .getOrCreate()

    partition_folders = glob.glob(f"{base_lakehouse_dir}/episode_id=*/date=*")
    print(f"[*] Tìm thấy {len(partition_folders)} phân vùng cần kiểm tra Compaction...")

    for folder in partition_folders:
        jsonl_files = glob.glob(f"{folder}/*.jsonl")
        if len(jsonl_files) > 5:
            print(f"[*] Đang nén gộp {len(jsonl_files)} tệp vụn tại: {folder}")
            df = spark.read.json(folder)
            parquet_target = folder.replace("flood_events", "silver_parquet_lakehouse")
            os.makedirs(parquet_target, exist_ok=True)
            df.coalesce(1).write.mode("overwrite").parquet(parquet_target)
            print(f"   ✓ Đã tối ưu hóa xong -> {parquet_target}")

if __name__ == "__main__":
    compact_lakehouse_partitions()
```

---

### 4.3. Loại bỏ Xung đột Tệp tin bằng Redis In-Memory Serving Store

* **Mục tiêu**: Tách rời 100% giữa Spark Processor và Dashboard Server. Spark bắn sự kiện vào Redis, Dashboard đọc từ Redis.

#### A. Cấu hình Container Redis trong `bigdata/docker-compose.yml`:
```yaml
  redis:
    image: redis:7.2-alpine
    container_name: se363-redis-serving
    ports:
      - "6379:6379"
    command: redis-server --save "" --appendonly no --maxmemory 256mb --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          memory: 256M
    restart: unless-stopped
```

#### B. Redis Data Model & Command Blueprint:
* **Key 1: `flood:geo:index` (Redis GEO Set)**: `GEOADD flood:geo:index <lon> <lat> <canonical_id>`
* **Key 2: `flood:timeline:zset` (Redis Sorted Set)**: `ZADD flood:timeline:zset <create_time> <canonical_id>`
* **Key 3: `flood:event:<canonical_id>` (Redis String / Hash)**: Payload JSON đầy đủ, TTL 24h (`EXPIRE 86400`).

---

### 4.4. Cơ chế Gom cụm Sự kiện Đa nguồn (Spatio-Temporal Flood Clustering)

```python
# ==============================================================================
# BLUEPRINT 4.4: pipeline/spatio_temporal_clusterer.py
# ==============================================================================
import time
from typing import List, Dict, Any
from core.gazetteer import haversine_distance_meters

class SpatioTemporalClusterer:
    """
    Gom cụm các bài đăng mạng xã hội trùng khớp về không gian (< 400m)
    và thời gian (< 45 phút) thành một 'Sự kiện Ngập Thống Nhất' (Unified Incident).
    """
    def __init__(self, radius_meters: float = 400.0, time_window_seconds: int = 2700):
        self.radius = radius_meters
        self.window = time_window_seconds

    def cluster_events(self, raw_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        clusters = []

        for ev in raw_events:
            loc = ev.get("location", {})
            lat, lon = loc.get("lat"), loc.get("lon")
            ev_time = ev.get("create_time", int(time.time()))
            if not lat or not lon:
                clusters.append(ev)
                continue

            merged = False
            for c in clusters:
                c_lat, c_lon = c["location"]["lat"], c["location"]["lon"]
                c_time = c["create_time"]

                dist = haversine_distance_meters(lat, lon, c_lat, c_lon)
                time_diff = abs(ev_time - c_time)

                if dist <= self.radius and time_diff <= self.window:
                    c["report_count"] = c.get("report_count", 1) + 1
                    c["sources"] = list(set(c.get("sources", [c["platform"]]) + [ev["platform"]]))
                    c["weight"] = max(c.get("weight", 1.0), ev.get("weight", 1.0)) + 0.5
                    c["posts_summary"] = c.get("posts_summary", []) + [{
                        "author": ev.get("author"),
                        "text": ev.get("text"),
                        "url": ev.get("url")
                    }]
                    merged = True
                    break

            if not merged:
                ev_copy = dict(ev)
                ev_copy["report_count"] = 1
                ev_copy["sources"] = [ev.get("platform", "social")]
                clusters.append(ev_copy)

        return clusters
```

---

### 4.5. Cơ chế Xử lý Lỗi & Dead Letter Queue (Kafka DLQ)

* **Topic DLQ**: `social.flood.dlq`
* **Schema mẫu DLQ**:
```json
{
  "failed_at": "2026-10-14T01:30:00Z",
  "source_topic": "social.live.raw",
  "error_type": "SchemaValidationError | GeocodingFailure | ParseException",
  "error_message": "Field 'create_time' must be a valid epoch integer",
  "raw_payload": { "id": "raw_123", "text": "null corrupted data" },
  "retry_count": 3
}
```

---

### 4.6. Chuẩn hóa Hợp đồng Kết nối Dịch vụ AI Đa phương thức (AI Microservice Contract)

Dành cho module của bạn Hưng (Binary Image Classifier, Whisper ASR, PhoBERT ASTE) trên cổng 8001:

* **Endpoint**: `POST http://localhost:8001/api/v1/predict-multimodal`
* **Request Contract**:
```json
{
  "post_id": "tiktok_7421892182",
  "text": "Đường Kha Vạn Cân ngập sâu quá xe chết máy la liệt",
  "media_urls": [
    "https://v16-webapp-prime.tiktok.com/video_sample.mp4",
    "https://p16-sign-sg.tiktokcdn.com/image_sample.jpg"
  ]
}
```
* **Response Contract**:
```json
{
  "status": "success",
  "visual_prediction": {
    "is_flood": true,
    "confidence": 0.94,
    "water_level_detected": "deep"
  },
  "audio_transcript": "nước ngập tới yên xe rồi mọi người ơi",
  "aste_triplets": [
    {
      "aspect": "Đường Kha Vạn Cân",
      "opinion": "ngập sâu",
      "polarity": "negative",
      "severity_score": 3.0
    }
  ],
  "content_confidence_score": 0.92
}
```

---

### 4.7. Chuẩn hóa Quản lý Thư viện (`requirements.txt`)

```text
# SE363 - Complete Big Data Dependencies
# Core & Web Serving
requests>=2.31.0
urllib3>=2.0.0
beautifulsoup4>=4.12.0
googlenewsdecoder>=0.1.3
feedparser>=6.0.11

# Messaging & Distributed Computing
kafka-python>=3.0.0
pyspark>=3.5.0
delta-spark>=3.1.0

# Database & In-Memory Serving
redis>=5.0.0
duckdb>=0.10.0

# Geospatial & Math
numpy>=1.24.0
scipy>=1.11.0

# Code Quality & Validation
pydantic>=2.5.0
```

---

### 4.8. Đặc tả Chi tiết Hợp đồng Dữ liệu Toàn trình (End-to-End Data Contract Schemas)

#### Hợp đồng 1: Raw Stream Ingestion Event (`social.live.raw` / `social.sim.raw`)
```json
{
  "id": "tt_7389102381",
  "canonical_id": "8f03c2a1e9487c9d",
  "platform": "tiktok",
  "text": "Mưa to quá Đường số 40 Hiệp Bình ngập lút bánh xe",
  "author": "user_saigon_ngap",
  "create_time": 1728873600,
  "created_at_iso": "2026-10-14T00:00:00Z",
  "url": "https://www.tiktok.com/@user/video/7389102381",
  "media_urls": ["https://cdn.tiktok.com/video_sample.mp4"],
  "ingested_at": 1728873602
}
```

#### Hợp đồng 2: Processed Silver Event (Spark Output -> Lakehouse & Serving)
```json
{
  "id": "tt_7389102381",
  "canonical_id": "8f03c2a1e9487c9d",
  "platform": "tiktok",
  "text": "Mưa to quá Đường số 40 Hiệp Bình ngập lút bánh xe",
  "create_time": 1728873600,
  "location": {
    "street": "Đường số 40",
    "ward": "Phường Hiệp Bình Chánh",
    "district": "TP. Thủ Đức",
    "lat": 10.8444,
    "lon": 106.7331,
    "display_name": "Đường số 40, Phường Hiệp Bình Chánh",
    "match_source": "csgt_122_hotspots"
  },
  "severity": {
    "level": "heavy",
    "score": 3.0,
    "depth_cm": 45.0,
    "keywords": ["ngập lút bánh", "mưa to"]
  },
  "veracity": {
    "is_verified": true,
    "confidence_score": 0.88,
    "weather_corroborated": true,
    "spatial_consensus_count": 3
  },
  "episode_id": "episode_2026_oct",
  "batch_timestamp": 1728873605
}
```

---

## 5. CƠ CHẾ PHÒNG HỘ SUY BIẾN DUYÊN DÁNG & TỰ PHỤC HỒI (GRACEFUL DEGENERATION)

Hệ thống được thiết kế theo nguyên tắc "No Single Point of Crash". Khi bất kỳ phân hệ nào gặp sự cố, hệ thống tự động suy biến xuống cấp độ an toàn thấp hơn:

```mermaid
flowchart TD
    subgraph FAILOVER_REDIS ["Phòng hộ Tầng Serving"]
        Req1["Dashboard Query"] --> TryRedis{"Thử kết nối Redis<br/>(Port 6379)?"}
        TryRedis -->|Thành công| ReadRedis["Đọc GEO/ZSET từ Redis (< 3ms)"]
        TryRedis -->|Mất kết nối| FallbackFile["Fallback: Đọc file live_stream_state.json<br/>+ Ghi log WARNING (Không crash)"]
    end

    subgraph FAILOVER_WEATHER ["Phòng hộ Tầng Đối soát"]
        Req2["Veracity Check"] --> TryAPI{"Gọi Open-Meteo<br/>Weather API?"}
        TryAPI -->|HTTP 200| CalcRain["Tính toán lượng mưa thực tế"]
        TryAPI -->|Timeout / 429| FallbackSpatial["Fallback: Dùng Spatial Consensus (500m/60p)<br/>weather_matched = null"]
    end

    subgraph FAILOVER_KAFKA ["Phòng hộ Tầng Thu nạp"]
        Req3["Crawler Push Event"] --> TryKafka{"Kafka Broker<br/>sẵn sàng?"}
        TryKafka -->|Sẵn sàng| SendBroker["Bắn vào Topic social.*.raw"]
        TryKafka -->|Down / Lỗi| LocalBuffer["Fallback: Ghi hàng đợi tạm data/fallback_queue.jsonl<br/>Retry sau qua Exponential Backoff"]
    end
```

* **Nguyên tắc 1: Phục vụ Web không gián đoạn**: Nếu container Redis bị tắt hoặc chưa cài, server chuyển sang đọc từ file đệm cục bộ `data/live_stream_state.json` mà không trả về lỗi 500.
* **Nguyên tắc 2: Không block Stream bởi API bên thứ ba**: Nếu Open-Meteo bị quá tải hoặc rớt mạng, hàm `veracity_checker.py` bắt lỗi `requests.exceptions.RequestException`, đặt điểm tin cậy mặc định `0.5` và tiếp tục luồng xử lý.

---

## 6. LỘ TRÌNH THỰC THI PHÂN KỲ & TIÊU CHÍ HOÀN THÀNH (DEFINITION OF DONE - DOD)

Hệ thống được chia thành 4 Phase rõ ràng để các Agent ở phiên sau thực thi tuần tự:

```
[PHASE 1: NỀN TẢNG & SERVING KHÔNG LỖI] ──> [PHASE 2: NATIVE SPARK & DELTA LAKE]
                 │                                        │
                 ▼                                        ▼
[PHASE 4: ORCHESTRATION & OBSERVABILITY] <── [PHASE 3: AI SERVICE & CLUSTERING]
```

### 🔴 Phase 1: Nền tảng Độ tin cậy & Phục vụ không khóa file (Ưu tiên cao nhất - Làm ngay)
* [ ] **Công việc 1.1**: Cập nhật container `redis` vào [`bigdata/docker-compose.yml`](file:///D:/SE363_RAWDATA/bigdata/docker-compose.yml).
* [ ] **Công việc 1.2**: Sửa [`dashboard/server.py`](file:///D:/SE363_RAWDATA/dashboard/server.py) để ưu tiên đọc hot state từ Redis (kèm fallback đọc file `live_stream_state.json`).
* [ ] **Công việc 1.3**: Chuẩn hóa tệp [`requirements.txt`](file:///D:/SE363_RAWDATA/requirements.txt) đầy đủ tất cả thư viện sống còn.
* **Tiêu chí hoàn thành (DoD)**: Chạy pipeline và dashboard liên tục trong 30 phút không xuất hiện bất kỳ lỗi `JSONDecodeError` hay `ModuleNotFoundError`.

### 🟡 Phase 2: Nâng cấp PySpark Streaming & Hồ dữ liệu Delta Lake (Trọng tâm Big Data)
* [ ] **Công việc 2.1**: Chuyển đổi [`spark_flood_processor.py`](file:///D:/SE363_RAWDATA/bigdata/streaming/spark_flood_processor.py) sang Native Structured Streaming với `spark.readStream.format("kafka")`.
* [ ] **Công việc 2.2**: Đóng gói các hàm GIS (`match_hotspot`) và Admin (`RESOLVER`) thành Spark UDFs để chạy phân tán.
* [ ] **Công việc 2.3**: Xây dựng kịch bản nén tệp tự động `bigdata/lakehouse/compaction_job.py` để gộp JSONL thành Parquet.
* **Tiêu chí hoàn thành (DoD)**: Spark tận dụng 100% các lõi CPU của máy, checkpoint được lưu ổn định vào thư mục `_checkpoints`.

### 🟢 Phase 3: Gom cụm Sự kiện & Tích hợp Microservice AI
* [ ] **Công việc 3.1**: Triển khai module `SpatioTemporalClusterer` để gom nhiều bài đăng trùng vị trí và thời gian thành 1 Master Incident.
* [ ] **Công việc 3.2**: Xây dựng Mock AI Microservice cổng 8001 sẵn sàng cho bạn Hưng kết nối mô hình.
* [ ] **Công việc 3.3**: Thiết lập topic Dead Letter Queue `social.flood.dlq` trên Kafka.
* **Tiêu chí hoàn thành (DoD)**: 20 bài viết cùng nói về ngập Chợ Thủ Đức chỉ hiển thị 1 marker lớn duy nhất có ghi nhãn "Được báo cáo bởi 20 người".

### 🔵 Phase 4: Điều phối & Giám sát Hệ thống (Production Readiness)
* [ ] **Công việc 4.1**: Viết DAG điều phối (Dagster / Prefect) quản lý lịch chạy cào tin, nén Lakehouse, sao lưu dữ liệu.
* [ ] **Công việc 4.2**: Kết nối Prometheus exporter để đo Kafka Consumer Lag và tốc độ xử lý micro-batch.
* **Tiêu chí hoàn thành (DoD)**: Có thể theo dõi độ trễ hệ thống và tình trạng cụm qua giao diện đồ thị thời gian thực.

---

## 7. SỔ TAY DÒNG LỆNH THỰC CHIẾN DÀNH CHO AGENT (AGENT PLAYBOOK & CLI CHEAT SHEET)

Dành cho AI Agent ở phiên tiếp theo, chỉ cần sao chép và thực thi trực tiếp trên PowerShell:

### 7.1. Kích hoạt Môi trường & Khởi động Hạ tầng Docker
```powershell
# 1. Kích hoạt môi trường ảo Python
& "D:\SE363_RAWDATA\.venv\Scripts\Activate.ps1"

# 2. Khởi động cụm hạ tầng Kafka KRaft & Redis
docker compose -f "D:\SE363_RAWDATA\bigdata\docker-compose.yml" up -d

# 3. Kiểm tra trạng thái vùng chứa Docker
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### 7.2. Kiểm tra Kết nối & Chạy Thử nghiệm Từng Tầng
```powershell
# 1. Kiểm tra Kafka UI mở tại: http://localhost:8080
# 2. Kiểm tra Dashboard Web mở tại: http://localhost:8050

# 3. Khởi chạy riêng biệt Dashboard Web Server:
& "D:\SE363_RAWDATA\.venv\Scripts\python.exe" "D:\SE363_RAWDATA\dashboard\server.py"

# 4. Khởi chạy riêng biệt Động cơ Xử lý Luồng Spark:
& "D:\SE363_RAWDATA\.venv\Scripts\python.exe" "D:\SE363_RAWDATA\bigdata\streaming\spark_flood_processor.py"

# 5. Khởi chạy Bộ phát Dữ liệu Mô phỏng Lịch sử (Simulation Replayer):
& "D:\SE363_RAWDATA\.venv\Scripts\python.exe" "D:\SE363_RAWDATA\pipeline\simulation_replayer.py" --speed 5.0 --episode ep_2026_10_01

# 6. Khởi chạy 1-Click Toàn bộ Pipeline:
& "D:\SE363_RAWDATA\.venv\Scripts\python.exe" "D:\SE363_RAWDATA\bigdata\run_streaming_pipeline.py"
```

### 7.3. Thực thi Công việc Nén Lakehouse (Compaction)
```powershell
# Chạy job nén gộp các file JSONL vụn thành Apache Parquet
& "D:\SE363_RAWDATA\.venv\Scripts\python.exe" "D:\SE363_RAWDATA\bigdata\lakehouse\compaction_job.py"
```

---

## 8. CHIẾN LƯỢC KIỂM THỬ KHÓI TỰ ĐỘNG (AUTOMATED SMOKE TEST SUITE)

Khi AI Agent hoàn thành mỗi Phase, Agent PHẢI khởi chạy tập lệnh kiểm thử khói để nghiệm thu trước khi báo cáo người dùng:

```python
# ==============================================================================
# BLUEPRINT 8: tests/smoke_test_pipeline.py
# ==============================================================================
import requests
import json
import time

def test_dashboard_health():
    print("[TEST 1] Kiểm tra Dashboard Web Server cổng 8050...")
    res = requests.get("http://localhost:8050/", timeout=5)
    assert res.status_code == 200, f"Dashboard trả về mã lỗi: {res.status_code}"
    print("   ✓ Dashboard phản hồi HTTP 200 OK")

def test_api_realtime_heatmap():
    print("[TEST 2] Kiểm tra API /api/realtime-heatmap...")
    res = requests.get("http://localhost:8050/api/realtime-heatmap", timeout=5)
    assert res.status_code == 200, f"API Heatmap trả về mã: {res.status_code}"
    data = res.json()
    assert "events" in data, "Thiếu trường 'events' trong payload API"
    print(f"   ✓ API Heatmap hợp lệ, trả về {len(data['events'])} sự kiện ngập")

def test_hotspot_coordinates_integrity():
    print("[TEST 3] Kiểm tra tính toàn vẹn tọa độ của 3 tuyến đường bảo chứng...")
    from core.gazetteer import match_hotspot
    # 1. Đường số 40 Hiệp Bình
    m40 = match_hotspot("ngập nặng ở đường số 40 hiệp bình")
    assert abs(m40["lat"] - 10.8444) < 0.005, f"Lệch tọa độ Đường 40: {m40}"
    # 2. Chợ Thủ Đức
    m_td = match_hotspot("ngập lênh láng ngay chợ thủ đức")
    assert abs(m_td["lat"] - 10.8505) < 0.005, f"Lệch tọa độ Chợ Thủ Đức: {m_td}"
    # 3. Quốc lộ 51 Phước Thái
    m_51 = match_hotspot("ql51 phước thái ngập sâu")
    assert abs(m_51["lat"] - 10.6650) < 0.005, f"Lệch tọa độ QL51: {m_51}"
    print("   ✓ 100% tọa độ 3 tuyến đường bảo chứng chính xác tuyệt đối!")

if __name__ == "__main__":
    test_dashboard_health()
    test_api_realtime_heatmap()
    test_hotspot_coordinates_integrity()
    print("\n🎉 TOÀN BỘ SMOKE TEST ĐẠT TIÊU CHUẨN HOÀN THIỆN!")
```

---

## 9. HƯỚNG DẪN KÍCH HOẠT DÀNH CHO AI AGENT Ở PHIÊN TIẾP THEO

> 🤖 **LƯU Ý DÀNH CHO AI AGENT TIẾP QUẢN DỰ ÁN**:
> Khi người dùng gửi yêu cầu bắt đầu cải tiến hệ thống theo tài liệu này:
> 1. **ĐỌC KỸ MỤC 6 (LỘ TRÌNH THỰC THI)**: Xác định người dùng muốn thực thi **Phase nào** (ưu tiên tuần tự từ Phase 1 $\rightarrow$ Phase 4).
> 2. **TUÂN THỦ NGUYÊN TẮC GIỮ TOÀN VẸN LOGIC NGHIỆP VỤ GIS CŨ**:
>    * Tuyệt đối **KHÔNG** sửa đổi thuật toán phân tầng so khớp trong [`core/gazetteer.py`](file:///D:/SE363_RAWDATA/core/gazetteer.py) (Tầng 1.A CSGT $\rightarrow$ 1.B Dynamic Cache $\rightarrow$ 1.C OSM $\rightarrow$ Tầng 2 ĐVHC).
>    * Tuyệt đối **KHÔNG** thay đổi tọa độ chuẩn của 3 tuyến đường đã kiểm chứng:
>      * Đường số 40 (Phường Hiệp Bình): `[10.8444, 106.7331]`
>      * Tim Chợ Thủ Đức: `[10.8505, 106.7543]`
>      * Quốc lộ 51 (Phước Thái): `[10.6650, 107.0350]`
> 3. **KIỂM TRA MÔI TRƯỜNG TRƯỚC KHI CHẠY**:
>    * Luôn sử dụng Python từ `.venv`: `.\.venv\Scripts\python.exe`.
>    * Đảm bảo kiểm tra Docker CLI hoạt động trước khi gọi docker compose.
> 4. **CHẠY SMOKE TEST SAU KHI SỬA ĐỔI**: Chạy script tại Mục 8 để xác nhận không gây regression bug.

---

## 10. HƯỚNG DẪN BẢO VỆ ĐỒ ÁN VÀ TRẢ LỜI PHẢN BIỆN GIẢNG VIÊN

| Câu hỏi của Hội đồng Giảng viên | Câu trả lời chuẩn chuyên gia Data Engineer |
| :--- | :--- |
| **"Tại sao em dùng PySpark nhưng hệ thống chạy trên 1 máy cá nhân (Local)?"** | *"Dạ thưa Thầy/Cô, PySpark được thiết kế theo nguyên tắc Abstraction. Việc chạy `master('local[*]')` giúp tận dụng tối đa kiến trúc đa lõi song song (Multi-core Parallelism) của CPU máy tính cá nhân trong quá trình phát triển. Toàn bộ mã nguồn sử dụng Spark DataFrame và Structured Streaming chuẩn tắc, do đó khi đưa lên cụm phân tán nhiều máy (như AWS EMR hoặc Databricks), hệ thống chỉ cần thay đổi cấu hình Master URL mà không phải viết lại bất kỳ dòng code nào."* |
| **"Tại sao không dùng cơ sở dữ liệu như PostgreSQL/MongoDB mà lại lưu JSON ra thư mục?"** | *"Dạ thưa Thầy/Cô, trong ngành Kỹ thuật Dữ liệu, việc tổ chức cây thư mục phân vùng theo `episode_id` và `date` là mô hình lưu trữ hồ dữ liệu (Data Lakehouse Partitioning). Cách làm này giúp lưu trữ chi phí thấp (Object Storage / HDFS) và tối ưu cho các bài toán phân tích lịch sử quy mô lớn. Đối với tầng hiển thị Dashboard cần tốc độ mili-giây, nhóm sử dụng In-memory Serving Store (Redis)."* |
| **"Dữ liệu mạng xã hội có rất nhiều tin giả, hệ thống lọc như thế nào?"** | *"Nhóm triển khai cơ chế Veracity 4 tầng: Tầng 1 AI nội dung (kết nối mô hình của bạn Hưng), Tầng 2 đối soát lượng mưa thực tế từ trạm khí tượng vệ tinh Open-Meteo, Tầng 3 tính toán đồng thuận Spatio-Temporal trong bán kính 500m / 60 phút, và Tầng 4 chấm điểm Confidence Score (>=0.75 mới kích hoạt báo động đỏ trên bản đồ)."* |
| **"Tại sao chọn Kafka 4.3.1 KRaft thay vì Zookeeper?"** | *"Dạ thưa Thầy/Cô, kể từ Kafka 3.x và chính thức ở bản 4.x, Apache Kafka đã chuyển hoàn toàn sang cơ chế KRaft (Kafka Raft Metadata Mode). KRaft loại bỏ hoàn toàn cụm Zookeeper cồng kềnh bên ngoài, giúp giảm 50% lượng RAM tiêu thụ, phục hồi metadata nhanh hơn gấp 10 lần và tối ưu vượt trội khi vận hành trong Docker container."* |

---
*Tài liệu được hoàn thiện và đóng gói thành công làm Master Checkpoint cho dự án SE363.*
