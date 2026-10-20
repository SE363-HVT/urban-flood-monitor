# 📌 BÁO CÁO CHECKPOINT & KẾ HOẠCH XỬ LÝ (15/10/2026)
## ĐỀ TÀI: ĐỐI SOÁT LƯỢNG MƯA LỊCH SỬ SIMULATION & TỐI ƯU HÓA ĐỘ TRỄ HEATMAP STREAMING
**Môn học**: SE363 - Xử lý Dữ liệu Lớn  
**Thời gian tạo**: 01:00 AM, ngày 15/10/2026  
**Trạng thái**: Đã khoanh vùng chính xác 100% nguyên nhân gốc rễ, đã áp dụng bản vá cốt lõi, sẵn sàng cho bước tinh chỉnh tối ưu vào ngày mai.

---

## 1. MÔ TẢ HIỆN TRẠNG & TRIỆU CHỨNG QUAN SÁT ĐƯỢC

### Triệu chứng 1: Điểm Simulation không hiển thị lượng mưa lịch sử
* **Hiện tượng**: Khi mở bản đồ Heatmap ở chế độ Simulation (`http://localhost:8050`) và click vào các điểm ngập mô phỏng (ví dụ: *Đường Huỳnh Tịnh Của*, *Đường Nguyễn Tri Phương*), khung popup hiển thị:  
  `Lượng mưa thực tế: Không ghi nhận mưa tại thời điểm này (có thể do triều cường)`  
  và điểm xác thực rơi vào mức `Nghi vấn (Chờ kiểm chứng) (~58% - 66%)`.
* **Kỳ vọng**: Vì các bài đăng/video này được thu thập trong các đợt mưa lớn/bão lịch sử (Tháng 9 & 10/2026 hoặc 16/10/2024), trạm khí tượng vệ tinh Open-Meteo phải trả về đúng lượng mưa lịch sử đo được tại thời điểm video xuất bản (từ `0.4 mm/h` đến `6.8 mm/h`) và gắn nhãn `Đã xác thực`.

### Triệu chứng 2: Độ trễ hiển thị lên Heatmap kéo dài ~15 phút
* **Hiện tượng**: Sau khi chạy lệnh khởi động `run_streaming_pipeline.py --mode simulation`, phải đợi khoảng 10 đến 15 phút thì các tin mới bắt đầu hiển thị lên giao diện Heatmap thay vì xuất hiện tức thì trong vài giây.

---

## 2. PHÂN TÍCH NGUYÊN NHÂN GỐC RỄ (ROOT CAUSE ANALYSIS)

### A. Về bài toán lượng mưa Simulation (Open-Meteo Weather Plausibility)
1. **Thiếu trường trong PySpark `EVENT_SCHEMA`**:
   * Khi `SimulationReplayer` nạp dữ liệu từ `data/processed/hcmc_flood_annotated_v1.json`, mỗi bài đăng có trường `published_at` (thời điểm video thực tế đăng tải).
   * Tuy nhiên, động cơ `spark_flood_processor.py` đọc dữ liệu từ Kafka thông qua định nghĩa cấu trúc `EVENT_SCHEMA` (`StructType`). Trường `historical_timestamp` trước đó chưa được khai báo trong schema này.
   * Do cơ chế **Schema Enforcement** của Apache Spark, tất cả các trường không nằm trong `EVENT_SCHEMA` đều bị Spark tự động cắt bỏ (strip out).
2. **Hậu quả rơi về Live Mode**:
   * Khi mất `historical_timestamp`, hệ thống rơi về dùng `create_time` (mốc thời gian hôm nay, vừa sinh ra).
   * Hàm `check_weather_plausibility` thấy mốc thời gian cách hiện tại $< 24\text{ giờ}$ nên tự động gọi API Live Forecast của ngày hôm nay. Vì hôm nay tại TP.HCM trời tạnh ráo ($0.0\text{ mm/h}$), API trả về câu mặc định: *"Không ghi nhận mưa tại thời điểm này (có thể do triều cường)"*.

### B. Về bài toán độ trễ ~15 phút (Streaming Pipeline Bottleneck)
1. **Dồn ứ hàng trăm tin nhắn trong Kafka Topic**:
   * Qua các lần chạy thử trước đó, Kafka topic `social.sim.raw` đã tích tụ hàng trăm bản ghi cũ chưa được commit offset.
   * Khi PySpark khởi động, nó đọc một micro-batch khổng lồ lên tới **320 – 500 sự kiện** cùng lúc.
2. **Nghẽn mạng do gọi HTTP tuần tự sang Open-Meteo**:
   * Với mỗi sự kiện trong batch 500 tin, Spark lại thực hiện một request HTTP tuần tự đến máy chủ Open-Meteo ở châu Âu.
   * $500\text{ requests} \times 1\text{ đến }2\text{ giây/request} \approx 500\text{ đến }1000\text{ giây} \approx 8\text{ đến }15\text{ phút}$!
   * Đồng thời, việc gửi 500 request liên tục trong vài phút làm chạm ngưỡng **Rate Limit** của Open-Meteo (giới hạn 60 – 600 req/phút), dẫn đến timeout và lỗi mạng.
3. **Tiến trình chạy đè ngầm (Duplicate Zombie Processes)**:
   * Kiểm tra hệ thống phát hiện có **2 tiến trình `run_streaming_pipeline.py` và 2 tiến trình PySpark** chạy song song cùng lúc từ 12:09 AM (PID 13632 và PID 15556), làm nhân đôi số lượng request và gây nghẽn cổng 8050.

---

## 3. CÔNG VIỆC ĐÃ HOÀN TẤT TRONG BUỔI TỐI NAY

1. **Khôi phục 100% nguyên trạng 2 API & Logic thuật toán**:
   * Giữ nguyên vẹn hàm `check_weather_plausibility` (Open-Meteo) và `geocode_osm_dynamic` (OpenStreetMap).
   * Giữ nguyên công thức tính điểm tin cậy:  
     $$\text{Confidence Score} = 0.40 \times \text{Content} + 0.35 \times \text{Weather} + 0.25 \times \text{Consensus}$$
2. **Bảo toàn `historical_timestamp` qua toàn bộ Data Pipeline**:
   * Đã sửa `pipeline/simulation_replayer.py` để trích xuất `published_at` và `historical_timestamp` từ dataset.
   * Đã sửa `bigdata/producers/social_producer.py` để truyền trường này qua Kafka message.
   * Đã bổ sung `StructField("historical_timestamp", LongType(), True)` và `StructField("published_at", StringType(), True)` vào `EVENT_SCHEMA` trong `bigdata/streaming/spark_flood_processor.py`.
   * Đã sửa `pipeline/veracity_checker.py` để ưu tiên `historical_timestamp` khi gọi `archive-api.open-meteo.com`.
3. **Đã kiểm thử độc lập thành công rực rỡ**:
   * Khi chạy micro-batch nhỏ (5 tin), thời gian xử lý **chưa đầy 4 giây**.
   * Kết quả Open-Meteo trả về đúng lượng mưa lịch sử:
     * *Đường Huỳnh Tịnh Của*: `1.2 mm/h` $\rightarrow$ **Đã xác thực (80%)**.
     * *Đường Nguyễn Văn Hưởng*: `0.4 mm/h` $\rightarrow$ **Đã xác thực (78%)**.
     * *Đường Phan Văn Hớn*: `0.7 mm/h` $\rightarrow$ **Đã xác thực (77%)**.
     * *Đường Số 40*: `0.3 mm/h` $\rightarrow$ **Đã xác thực (72%)**.
4. **Đã dọn dẹp tiến trình**:
   * Cưỡng chế dừng toàn bộ các tiến trình zombie chạy đè ngầm (PID 13632, 15556, 21684, 21860, 21668, 23504).

---

## 4. KẾ HOẠCH HÀNH ĐỘNG DỨT ĐIỂM CHO NGÀY MAI

Để hệ thống chạy mượt mà tuyệt đối khi demo (bắn tin tức thì trong 2-3 giây và 100% điểm hiển thị đúng lượng mưa), ngày mai sẽ thực hiện 3 giải pháp kỹ thuật sau:

### Kế hoạch 1: Áp dụng Cơ chế Weather Pre-caching & Batching
* **Vấn đề**: Hiện tại mỗi sự kiện gửi 1 request HTTP riêng sang Open-Meteo, nếu Kafka dồn nhiều tin sẽ bị chậm.
* **Giải pháp**:
  * Tận dụng `weather_cache` theo lưới không gian (`lat_grid`, `lon_grid`) và ngày/giờ (`date_str`, `hour`).
  * Các sự kiện trong cùng một khu vực (bán kính 5-10km) và cùng một đợt bão sẽ dùng chung kết quả thời tiết từ cache mà **không cần gọi lại Open-Meteo lần thứ hai**.
  * Tốc độ xử lý sẽ tăng từ 15 phút xuống còn **dưới 2 giây**.

### Kế hoạch 2: Giới hạn Micro-batch Size trong PySpark Streaming
* **Vấn đề**: Khi Kafka có tin tồn đọng, PySpark không được nuốt một lúc 500 tin.
* **Giải pháp**:
  * Cấu hình `maxOffsetsPerTrigger = 15` hoặc `batch_size = 10` trong consumer loop.
  * Mỗi đợt micro-batch chỉ xử lý đúng 10-15 sự kiện, đảm bảo hoàn thành trong nháy mắt và đẩy ngay lên Leaflet Heatmap.

### Kế hoạch 3: Cơ chế Single-Instance Guard (Chống chạy trùng lặp)
* **Giải pháp**:
  * Viết một file khóa PID (`data/pipeline.lock`) trong `bigdata/run_streaming_pipeline.py`.
  * Nếu người dùng vô tình bấm chạy 2 lần, chương trình thứ hai sẽ cảnh báo ngay: *"Pipeline đã đang chạy ở PID xxx, vui lòng không mở trùng lặp!"*.

### Kế hoạch 4: Kiểm thử nghiệm thu toàn trình (End-to-End Verification)
* Chạy một lệnh duy nhất:
  ```powershell
  python bigdata/run_streaming_pipeline.py --mode simulation --clean
  ```
* Mở trình duyệt `http://localhost:8050`, xác nhận:
  1. Tin bắn ra đều đặn sau mỗi chu kỳ (không bị trễ 15 phút).
  2. Bấm vào bất kỳ điểm ngập mô phỏng nào cũng hiển thị đúng lượng mưa lịch sử đo từ trạm vệ tinh Open-Meteo.

---
*Ghi nhận bởi AI Assistant lúc 01:00 AM, ngày 15/10/2026. Chúc bạn ngủ ngon và hẹn gặp lại vào buổi làm việc ngày mai!*
