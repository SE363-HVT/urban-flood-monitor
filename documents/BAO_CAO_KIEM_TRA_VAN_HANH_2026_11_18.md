# Báo cáo kiểm tra vận hành thực tế ngày 18/11/2026

## 1. Phạm vi và cách kiểm tra

Đã khởi chạy hệ thống bằng entrypoint hiện có, lần lượt ở simulation và live, có bật AI. Đã kiểm tra Docker Kafka/Redis/Kafka UI, producer, Spark processor, AI service, dữ liệu Redis/file, cold storage, API dashboard và tương tác trên cả 7 panel bằng Chrome headless. Đã thử compaction trong thư mục tạm, các tình huống gom cụm có kiểm soát và fallback của dashboard khi Redis tạm ngưng.

Đây là phiên kiểm tra ngắn để xác nhận hành vi, không phải kiểm thử tải dài hạn, benchmark F1 hoặc nghiệm thu mọi nhánh lỗi. Không sửa mã nguồn vận hành, dependency, checkpoint mô hình hay dữ liệu gán nhãn. Không chạy huấn luyện và không kích hoạt cào sâu Apify tính phí.

Môi trường thực tế: Windows, Python 3.14.6, PySpark 4.2.0, kafka-python 3.0.11, redis Python client 8.1.0, Transformers 5.21.0, PyTorch 2.14.1+cpu. Máy có NVIDIA RTX 3050 Laptop 6 GB nhưng torch.cuda.is_available() là False do bản PyTorch hiện tại là CPU. Việc có GPU trên máy không đồng nghĩa service đang dùng GPU.

## 2. Những phần đã chạy thành công

| Thành phần | Kết quả quan sát |
| --- | --- |
| Kafka / Redis / Kafka UI | Container hoạt động; Kafka liệt kê được topic; Redis trả PONG |
| Simulation runner | Nạp được 3.818 sự kiện; warm-up 15 báo cáo thành 11 sự kiện sau gom cụm; producer tiếp tục gửi 10 tin mỗi chu kỳ thử |
| Spark processor | Kết nối Kafka/Redis, xử lý được nhiều batch và xuất dữ liệu serving/cold path; có log hoàn tất từng batch |
| Live end-to-end | Crawler phát hiện 4 tin 1022, gửi Kafka; Spark xử lý 4 tin; API heatmap trả 4 sự kiện mode live từ Redis |
| Kiểm chứng live | Cả 4 sự kiện có content_check từ AI service và kết quả đối soát thời tiết; lượng mưa bằng 0 vẫn có thể được giữ khi có bối cảnh triều cường/đọng nước |
| AI service | Nạp thành công PhoBERT, CLIP, PhoWhisper và BARTpho; health báo cả 4 active, device CPU |
| Fast Path | Trả HTTP 200 và triplet thực tế cho câu ngập, nước rút và dự báo |
| Slow Path | Một URL TikTok trả HTTP 200, visual prediction, transcript và triplet BARTpho; tổng thời gian khoảng 18,1 giây |
| Dashboard API | Heatmap, summary, admin-wards, time-series, throughput, system-health, live-feed và trạng thái pool có phản hồi |
| Dashboard UI | Cả 7 panel mở được ở cả simulation và live; Leaflet/ECharts tải được; có tile bản đồ, marker và canvas biểu đồ |
| Apify pool | Panel đọc được danh sách 9 tài khoản; không sửa tài khoản hay kích hoạt crawl sâu |
| Compaction Spark | Hai file JSONL thử được gộp thành Parquet Snappy; header file là PAR1 |
| Smoke test hiện có | tests/smoke_test_pipeline.py kết thúc thành công; các ca tọa độ và gom 20 báo cáo thành một cụm đều qua |

Tên 7 panel đã kiểm tra: Bản Đồ Nhiệt; Phường/Xã & Vùng; Diễn Biến Theo Giờ; Tốc Độ Thu Thập; Tin Báo Hiện Trường; Sức Khỏe Hệ Thống; Pool Key Apify. Đã tương tác chuyển panel, phím 1, thu gọn/mở sidebar và thay kích thước viewport. Đây chưa phải kiểm thử mọi nút nghiệp vụ.

## 3. Các vấn đề đã tái hiện hoặc có bằng chứng chạy thực tế

### 3.1. Biểu đồ theo giờ đang phân loại sai dữ liệu

Một snapshot simulation có 46 sự kiện: trường polarity gồm 39 NEG, 5 NEU và 2 POS. Trong summary tương ứng, tổng các cột NEG bằng 46, còn NEU và POS bằng 0.

Đối chiếu compute_time_series_metrics trong dashboard/server.py: hàm không ưu tiên polarity; chuyển sentiment/status_tag sang chữ hoa rồi tìm chuỗi chữ thường “pos” và “neu”. Đây là lỗi logic có thể ảnh hưởng trực tiếp panel Diễn Biến Theo Giờ. Ngoài ra, nhánh ngoài cửa sổ đang cộng vào NEG giờ hiện tại, cần kiểm tra riêng trước khi sửa.

Hướng ưu tiên: chuẩn hóa quy tắc phân loại và cửa sổ thời gian trên cùng snapshot, bảo đảm khớp giữa panel bản đồ, feed và biểu đồ; không đổi format API trong cùng lần sửa.

### 3.2. Panel sức khỏe chưa phản ánh tình trạng service thực tế

API system-health trả AI ONLINE, cổng 8000, latency 42 ms, trong khi AI thật hoạt động ở 8001. Sau khi dừng AI và Spark, chỉ khởi động dashboard để kiểm tra, API vẫn báo AI/Kafka/Redis/crawler ONLINE cùng các giá trị mặc định; uptime_seconds bằng 0.

Hướng ưu tiên: heartbeat có timeout, timestamp và trạng thái thực; phân biệt service không chạy với chạy heuristic. Không dùng tình trạng “ONLINE” mặc định làm bằng chứng hệ thống khỏe.

### 3.3. Lỗi canvas xuất hiện khi tương tác dashboard

Trong cả hai lượt UI simulation và live, trình duyệt ghi nhận IndexSizeError: getImageData có source width bằng 0. Stack đi qua leaflet-heat.js, invalidateSize và callback trong index.html khoảng dòng 3372 tại phiên kiểm tra.

Các panel vẫn mở và bản đồ vẫn tải tile, nhưng không thể coi cơ chế resize hiện tại đã loại bỏ hoàn toàn lỗi. Cần tái hiện đúng trạng thái panel ẩn/hiện và chỉ redraw heat layer khi container có kích thước hợp lệ. Giữ nguyên sidebar, router, phím tắt và bộ icon hiện có.

### 3.4. Slow Path vượt timeout bên gọi trong ca thử

Một ca media hoàn tất sau khoảng 18,1 giây, bao gồm lấy media và suy luận. VeracityChecker hiện dành 3,5 giây cho request có media. Ca này cho thấy service có thể trả kết quả sau khi bên gọi đã chuyển sang heuristic; không chứng minh mọi video đều cần 18 giây.

Snapshot simulation cũng có đồng thời 25 sự kiện lấy kết quả AI và 21 sự kiện dùng heuristic. Không quy toàn bộ fallback đó cho timeout vì warm-up ban đầu chạy trước khi AI được khởi động và media cũng có thể lỗi truy cập.

Hướng ưu tiên: đo riêng các giai đoạn, theo dõi lý do fallback, giới hạn đồng thời và cân nhắc xử lý bổ sung bất đồng bộ. Không chỉ tăng timeout đồng loạt làm nghẽn streaming. Chưa thay bản PyTorch hoặc cấu hình GPU khi chưa kiểm thử tương thích môi trường riêng.

### 3.5. Mô hình cũ còn sai ngữ nghĩa và boundary

Trong ba câu thử thủ công, câu nước rút cho kết quả POS; câu “Dự báo triều cường có thể gây ngập đường Huỳnh Tấn Phát.” lại sinh NEG. Câu ngập còn sinh aspect “nhiều xe”, fallback TP.HCM dù đã có tên đường và opinion có dấu chấm ở cuối.

Ba câu này là bằng chứng lỗi cụ thể, không đủ để suy ra F1. Giữ kế hoạch đối soát dataset và benchmark độc lập; không thay nhãn bằng heuristic hàng loạt để làm đẹp kết quả. Latency Fast Path lần đầu khoảng 82–106 ms, lượt sau khoảng 29–39 ms theo response của service; không dùng mẫu nhỏ này làm cam kết SLA.

### 3.6. Bộ gom cụm có ba lỗi thiết kế được tái hiện

- Ba điểm A–B–C cùng thời gian, mỗi cặp liền kề cách khoảng 334 m: thứ tự A,B,C tạo 2 cụm, B,A,C tạo 1 cụm.
- Hai bản ghi cùng ID vẫn tạo report_count bằng 2.
- Sau cluster_events, dữ liệu lồng trong input thay đổi. Điều này có thể ảnh hưởng báo cáo nguồn còn được dùng ở cold path.

Ca NEG và POS cùng vị trí cũng bị gộp, giữ polarity của đại diện và tăng confidence. Với dữ liệu ghim tim đường, đây là lý do phải bổ sung định danh địa danh, cấp định vị và cách cập nhật trạng thái; không chỉ đổi thuật toán theo khoảng cách GPS.

### 3.7. Fallback dashboard hoạt động nhưng còn chậm khi Redis treo

Khi tạm pause Redis trong lúc chỉ dashboard chạy, API heatmap trả HTTP 200 và đủ 4 sự kiện từ local_file_buffer, mất khoảng 6,9 giây. Sau khi unpause và qua thời hạn cache, API đọc Redis trở lại với đủ 4 sự kiện.

Đây là kiểm tra read fallback của dashboard khi Redis không phản hồi, không phải chứng minh producer/streaming không mất dữ liệu trong mọi loại lỗi Redis/Kafka. Hướng ưu tiên là giới hạn timeout và giảm phép thử kết nối lặp mà vẫn giữ fallback hiện có.

### 3.8. Lakehouse: Parquet chạy được; standalone vẫn là JSONL

Compaction Spark ghi được file Parquet thật trong thư mục thử, còn standalone tạo consolidated_events.jsonl. Vì thế cần giữ kế hoạch tách định dạng đầu ra và làm rõ trạng thái triển khai Delta. Không cần thay toàn bộ kho lưu trữ ngay khi đường Spark/Parquet hiện tại đã hoạt động.

## 4. Giới hạn kiểm tra cần giữ rõ

- Nguồn live trong phiên này chỉ thu được tin 1022. Đã chạy crawler đa nguồn nhưng kết quả rỗng của nguồn khác không chứng minh nguồn đó luôn lỗi hay luôn hoạt động; cần log riêng từng engine để phân biệt.
- Một số URL TikTok trong simulation yêu cầu đăng nhập. Không sử dụng cookie tài khoản cá nhân để vượt giới hạn truy cập.
- Cào sâu Apify chưa được chạy; panel/status hoạt động không chứng minh actor TikTok/Facebook đã crawl thành công.
- Smoke test chấp nhận heuristic khi AI offline. Kiểm tra DLQ hiện tại cũng chưa chứng minh đầy đủ message đã được broker lưu và consumer đọc được. “Smoke test qua” không thay thế kiểm tra tính đúng dữ liệu.
- Chưa thử crash giữa các sink, phục hồi offset sau lỗi, tải lớn, thời gian chạy dài hay thay đổi dependency. Việc dừng và khởi động lại simulation/live thành công không đồng nghĩa đã kiểm chứng exactly-once.
- Chưa xác minh độ đúng của transcript/visual prediction trên bộ media có gold label và chưa đo accuracy GIS toàn tập.

## 5. Thứ tự cải thiện sau khi chạy thử

1. Sửa số liệu và trạng thái giám sát: polarity/cửa sổ thời gian, health probe thật, throughput đo được; đồng thời xử lý lỗi redraw canvas có kiểm chứng trên cả 7 panel.
2. Củng cố gom cụm và bảo toàn ASTE: ID duy nhất, không mutate input, cấp định vị đại diện, quản lý tin phục hồi và bằng chứng nguồn.
3. Đo và điều phối AI: readiness thực, timeout/fallback minh bạch, xử lý media phù hợp với CPU/GPU và tài nguyên máy.
4. Củng cố nguồn và lưu trữ: ack/offset/buffer, idempotency, retry và đối chiếu cold/hot path.
5. Sau đó mới thử native Structured Streaming và Delta ở môi trường riêng nếu mang lại lợi ích đo được. Không đổi engine và dependency chỉ để khớp tên gọi trong tài liệu.

Giữ routing ngoài phạm vi theo quyết định của người dùng. Heatmap tiếp tục ghim địa danh đại diện, không biến vị trí tim đường thành GPS hiện trường.

## 6. Kết thúc phiên và dấu vết

Đã dừng các tiến trình runner, dashboard, AI, Spark và trình duyệt do phiên thử tạo. Kafka, Redis và Kafka UI được giữ chạy như lúc kiểm kê trước khi chạy runner. Redis đã được unpause; các key flood do phiên thử tạo đã dọn vì Redis ban đầu có DBSIZE bằng 0.

Đã khôi phục file serving state và gazetteer cache từ bản sao trước khi thử. Git không có thay đổi mã nguồn vận hành hoặc dữ liệu tracked sau khi khôi phục; chỉ có tài liệu. Log vận hành, offset/topic Kafka và các bản ghi cold path do chạy simulation/live vẫn là dấu vết của phiên thử, không tuyên bố đã hoàn tác toàn bộ trạng thái runtime.

Các JSON kết quả, ảnh dashboard, bản sao trước/sau và log được lưu cục bộ tại thư mục tạm C:/Users/USER/AppData/Local/Temp/SE363_runtime_audit_20261118_005317. Không đưa token hoặc thông tin tài khoản vào báo cáo này. Thư mục tạm có thể bị hệ điều hành dọn; những kết luận quan trọng đã được ghi lại trong tài liệu này.

## 7. Chạy đối chiếu và cải tiến dashboard sau khi bật Docker

Đã chạy entrypoint chuẩn ở simulation rồi live, có bật AI. Kafka, Redis và Kafka UI dùng các container đang chạy. Simulation phát lại dữ liệu đã lưu và xuất qua Spark sang Redis. Lượt live thu 8 tin, Spark ghi 6 sự kiện sau gom cụm và API đọc cả 6 từ Redis. Fast Path trả thành công một triplet cho câu kiểm tra. Spark compaction trên hai tệp thử trong thư mục tạm tạo Parquet Snappy có header PAR1. Nhánh standalone trả JSONL.

- Biểu đồ phân loại ưu tiên polarity của sự kiện. Sáu khung giờ gồm giờ hiện tại và năm giờ liền trước. Bản ghi thiếu thời gian, quá cũ hoặc ở tương lai nằm ngoài phép đếm. Trên cùng kịch bản 5 bản ghi, phiên bản cũ đếm 5 NEG, phiên bản sửa đếm 1 NEG, 1 NEU, 1 POS và bỏ 2 bản ghi ngoài khung.
- Dashboard health chạy kiểm tra nền. AI dùng HTTP health ở cổng cấu hình và đọc trạng thái các mô hình, Redis dùng PING, Kafka kiểm tra TCP bootstrap. AI chạy mô hình báo ONLINE tại cổng 8001 và chuyển STANDBY khi dừng. Trạng thái crawler riêng chưa có heartbeat.
- Panel tốc độ hiển thị số sự kiện trong phút qua theo thời gian của snapshot đang phục vụ. Tỷ lệ xác thực dùng trạng thái veracity dữ liệu. Tên trường và kiểu dữ liệu API được giữ.
- Leaflet chỉ cập nhật kích thước và gắn heat layer khi bản đồ có kích thước hợp lệ. Kiểm tra Chrome tái hiện lỗi canvas trước sửa và không thấy lỗi sau sửa qua cả 7 panel ở simulation lẫn live. Đã thử phím tắt, thu gọn sidebar và resize.
- Gom cụm bỏ bản ghi lặp ID trong cùng lần gọi và sao chép sâu trước tổng hợp. Ca 20 báo cáo vẫn gom thành một cụm. Ca bản ghi lặp và dữ liệu lồng xác nhận số báo cáo và bảo toàn input. Tính ổn định theo thứ tự và trạng thái cụm qua batch vẫn cần đối chiếu riêng.
- Khi Redis nhận kết nối nhưng im lặng, phép thử cô lập đọc được dữ liệu fallback sau khoảng 0,22 giây. Qua 4 test hồi quy và 6 ca smoke test hiện có. Smoke test DLQ kiểm tra fallback cục bộ.

Đã dừng các tiến trình test, khôi phục file serving và gazetteer cache, dọn key Redis phát sinh trong phiên. Container Kafka, Redis và Kafka UI tiếp tục chạy. Log, Kafka và cold storage giữ dấu vết runtime. Kiểm tra checksum xác nhận `phase3.txt` giữ nguyên. Phiên này chưa kiểm thử tải dài, phục hồi offset/replay qua lỗi hay chuyển sang Structured Streaming hoặc Delta.
