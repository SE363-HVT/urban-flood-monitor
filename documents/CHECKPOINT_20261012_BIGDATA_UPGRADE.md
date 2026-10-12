# 📌 BÁO CÁO CHECKPOINT TIẾN ĐỘ DỰ ÁN (12/10/2026)
## ĐỀ TÀI: NÂNG CẤP HỆ THỐNG GIÁM SÁT NGẬP LỤT ĐÔ THỊ THỜI GIAN THỰC LÊN KIẾN TRÚC BIG DATA (KAFKA KRaft + PYSPARK + LAKEHOUSE)
**Môn học**: SE363 - Xử lý Dữ liệu Lớn  
**Nhánh Git**: `feat/bigdata-kafka-pyspark` (Base tag: `v1.0-monolith-clean`)  
**Môi trường**: Windows 11, OpenJDK 17, Python 3.14 (.venv), Docker Desktop  

---

## 1. TỔNG KẾT CÁC CÔNG VIỆC ĐÃ HOÀN THÀNH HÔM NAY

### A. Sao lưu & Bảo toàn Hệ thống Baseline (100% An toàn)
* Tạo Git Tag `v1.0-monolith-clean` và đẩy lên GitHub làm mốc phục hồi an toàn.
* Tạo nhánh phát triển mới `feat/bigdata-kafka-pyspark`.
* Tạo bản sao lưu vật lý `backup_data_snapshot_20261012.zip` (~5 MB) chứa toàn bộ dữ liệu sạch và các module cốt lõi trước khi nâng cấp.

### B. Tách biệt Hai Bộ Crawler (Dataset Enrichment vs Live Streaming)
* **Crawler 1 (Làm giàu Dataset tĩnh)**: Giữ nguyên `scripts/free_social_crawler.py` chuyên trách cào sâu theo batch, mở rộng tập mẫu lịch sử.
* **Crawler 2 (Luồng trực tiếp thời gian thực)**: Xây dựng mới `pipeline/live_free_crawler.py` hoàn toàn miễn phí qua Google Discovery RSS + `googlenewsdecoder`, cửa sổ trượt linh hoạt 60–120 phút, sinh mã `canonical_id` chuẩn hóa.

### C. Thiết lập Cụm Apache Kafka 4.3.1 KRaft & Kafka-UI
* Viết cấu hình `bigdata/docker-compose.yml`:
  * Sử dụng phiên bản mới nhất **Apache Kafka 4.3.1** chạy ở chế độ **Pure KRaft** (không phụ thuộc Zookeeper, tối ưu RAM < 1.5GB).
  * Tích hợp **Kafka-UI** (`provectuslabs/kafka-ui:latest`) trên cổng web `8080`.
* Giải quyết triệt để vấn đề biến môi trường Docker CLI trên Windows và kiến trúc Dual Listeners:
  * `PLAINTEXT://0.0.0.0:9092` (Advertised: `localhost:9092`) cho máy Windows host và PySpark.
  * `PLAINTEXT_INTERNAL://0.0.0.0:29092` (Advertised: `kafka:29092`) cho mạng nội bộ Docker container của Kafka-UI.
* Đã kiểm thử cụm chạy xanh (*Healthy*) và nhận tin nhắn ổn định.

### D. Xây dựng Multi-Source Kafka Producer
* Xây dựng `bigdata/producers/social_producer.py`:
  * Hỗ trợ đồng thời **Live Mode** (Free Crawler + Apify Deep Poller theo nhu cầu demo) và **Simulation Mode** (phát lại từ 3.818 mẫu sạch).
  * Chống trùng lặp Tầng 1: Gán `canonical_id` làm khóa Kafka Message Key.
  * Cơ chế chịu lỗi (Fault-Tolerance): Tự động nhận diện Broker và bảo vệ luồng.

### E. PySpark Structured Streaming Engine & Lakehouse Partitioning
* Cài đặt `pyspark==4.2.0` và `kafka-python==3.0.11`.
* Xây dựng `bigdata/streaming/spark_flood_processor.py`:
  * Cấu hình tương thích Windows (`PYSPARK_PYTHON` trỏ đúng vào `.venv`).
  * Kế thừa 100% logic cốt lõi: Định vị Street-First (122 điểm CSGT + tim đường OSM), 168 ĐVHC sau sáp nhập (NQ 1685), Đối soát khí tượng Open-Meteo (Veracity Checker).
  * Output 2 đường độc lập:
    * **Hot Path**: Cập nhật `data/live_stream_state.json` (< 3s) phục vụ Leaflet Dashboard.
    * **Cold Path**: Lưu trữ phân vùng chuẩn Lakehouse đa tầng `episode_id={id}/date={date}/`.
* Tách biệt rõ ràng `data/pipeline_state.json` (chỉ dùng cho Crawler Watermark) và `data/live_stream_state.json` (dùng cho Dashboard).

### F. Backfill Dữ liệu Lịch sử vào Data Lakehouse (Silver Layer)
* Xây dựng và thực thi thành công `bigdata/lakehouse/backfill_episodes.py`:
  * Đã chuẩn hóa và phân vùng **3.818 sự kiện ngập lịch sử** (gồm 1.548 điểm ngập cụ thể tuyến đường) vào **274 partitions** trong Lakehouse chỉ mất **2.95 giây**.
  * Đồng bộ `metadata.json` mô tả đặc trưng thời tiết cho toàn bộ 5 đợt ngập lớn.

---

## 2. TRẠNG THÁI HIỆN TẠI & CÓ BỊ BLOCK GÌ KHÔNG?
* **Trạng thái**: ✅ **HOÀN TOÀN THÔNG SUỐT, KHÔNG CÓ BẤT KỲ BLOCKER NÀO.**
* **Các vấn đề đã được gỡ bỏ hoàn toàn trong buổi hôm nay**:
  1. Đã tìm ra đường dẫn Docker Desktop CLI và kiểm tra PATH trên Windows.
  2. Đã fix lỗi xoay vô tận của Kafka-UI do cấu hình mạng listener nội bộ.
  3. Đã fix lỗi Unicode mã hóa cp1252 trên PowerShell Windows.
  4. Đã khôi phục và bảo toàn nguyên trạng file `pipeline_state.json`.

---

## 3. CẦN KIỂM THỬ VÀ NÂNG CẤP GÌ Ở BUỔI TIẾP THEO?

1. **Kiểm thử End-to-End Live Stream (End-to-End Integration Test)**:
   * Chạy song song: Kafka Broker $\rightarrow$ Producer (Live Free Crawler) $\rightarrow$ PySpark Streaming Engine $\rightarrow$ Leaflet Dashboard (`dashboard/index.html`).
   * Kiểm tra độ trễ hiển thị điểm ngập mới lên bản đồ nhiệt dưới 3 giây.
2. **Kịch bản Demo Giảng viên (Dual-Engine Ingestion Demo)**:
   * Kiểm thử bật đồng thời cả **Free Crawler** và **Apify Poller** trong lúc demo để chứng minh cơ chế chống trùng lặp đa nguồn (Two-Tier Deduplication) không bị dẫm chân.
3. **Viết Script Khởi chạy Tự động (One-Click Runner)**:
   * Tạo file `bigdata/run_streaming_pipeline.py` (hoặc PowerShell script) để 1 lệnh khởi động trơn tru toàn bộ luồng mà không phải gõ nhiều terminal thủ công.
4. **Xây dựng AI Microservice Skeleton**:
   * Thiết lập `bigdata/ai_service/app.py` (FastAPI cổng 8001) với cơ chế Mock Heuristic Fallback, sẵn sàng để bạn Hưng tích hợp mô hình PhoBERT ASTE, ViT Image Classifier và Whisper ASR.

---

## 4. HƯỚNG DẪN KHI NGHỈ / TIẾP TỤC

### Khi nghỉ hôm nay (Tắt Docker để tiết kiệm RAM/CPU máy):
Mở terminal PowerShell và chạy:
```powershell
cd D:\SE363_RAWDATA\bigdata
docker compose down
```
*(Hoặc mở ứng dụng Docker Desktop và nhấn nút Stop ở container group `bigdata`). Dữ liệu và cấu hình đều được lưu an toàn trên ổ đĩa.*

### Khi tiếp tục buổi sau:
Chỉ cần bật lại Docker bằng 1 lệnh:
```powershell
cd D:\SE363_RAWDATA\bigdata
docker compose up -d
```
Cụm Kafka KRaft và Kafka-UI sẽ sẵn sàng hoạt động ngay lập tức!
