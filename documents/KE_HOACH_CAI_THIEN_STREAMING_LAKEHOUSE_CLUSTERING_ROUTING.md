# Kế hoạch cải thiện Streaming, Lakehouse, gom cụm và Heatmap ASTE

Ngày lập: 18/11/2026.

## Trạng thái triển khai

`main` đã tích hợp các bản sửa dashboard và gom cụm (`02fa140`) cùng bản sửa tiếp nhận Kafka → Spark (`a3488ba`). Entrypoint `bigdata/run_streaming_pipeline.py` tự dùng các bản sửa này khi khởi động ở chế độ live hoặc simulation. Hai chế độ chọn nguồn dữ liệu, cùng dùng mã dashboard và Spark processor hiện hành.

Đường chạy Kafka → PySpark đã bổ sung xác nhận gửi từ Kafka, xác nhận offset theo partition sau khi lưu đầu ra bền vững, và đọc lại file đệm nguyên tử. Báo cáo nguồn mới nằm trong `data/lakehouse/raw_reports/`. Báo cáo đã xác thực được lưu thành JSONL theo phân vùng trong `flood_events/` để có thể dựng lại sự kiện đang phục vụ. Compaction đọc được JSONL cũ và mới, xuất Parquet và đưa đầu ra JSONL dự phòng vào thư mục riêng.

Các báo cáo về cùng sự cố được gom xuyên lô. Heatmap phân biệt ghim đại diện cho đường, phường/xã và thành phố, đồng thời giữ nội dung ASTE nguồn. Dashboard và API chỉ số dùng chung snapshot, có trạng thái theo chu kỳ của crawler. Veracity tiếp tục dùng Open-Meteo Forecast và Archive, phân biệt 0 mm với thiếu dữ liệu, dùng chung lần gọi theo ô tọa độ và giới hạn luồng AI xử lý media.

### Structured Streaming và Delta Lake

Đường chạy chuẩn dùng Kafka Structured Streaming qua `readStream` và `writeStream`. Bộ phiên bản được ghim ở PySpark 4.2.0 và Delta Lake 4.4.1. JVM tải connector từ Maven Central khi chạy lần đầu. Spark lưu checkpoint riêng cho live và simulation trong `data/lakehouse/_checkpoints/structured_flood/`. Lúc chuyển lần đầu, chương trình lấy offset tiếp theo mà consumer group cũ đã xác nhận cho từng partition. Partition chưa có offset bắt đầu từ đầu phần dữ liệu còn trong Kafka. Các lần khởi động lại dùng checkpoint đã lưu. Nếu offset cần đọc đã hết hạn trong Kafka, truy vấn báo lỗi để đối soát.

Bảng lịch sử báo cáo đã xác thực nằm trong `data/lakehouse/delta/verified_reports/{mode}`. Bảng giữ thông tin địa danh, giờ sự kiện, lượng mưa và nội dung báo cáo đầy đủ. Khóa `report_version` cho phép phát lại cùng một phiên bản mà không thêm dòng. JSONL nguồn và JSONL phục hồi tiếp tục được lưu. Redis vẫn phục vụ snapshot dashboard. Khi ghi Delta lỗi, Spark giữ lô để đọc lại, còn dashboard phục vụ snapshot gần nhất đang có.

Khi pipeline cùng chế độ đã dừng, có thể nhập lịch sử JSONL đã xác thực bằng lệnh `python bigdata/streaming/structured_flood_stream.py --mode live --backfill-delta` hoặc `--mode simulation --backfill-delta`. Nhập lại cùng dữ liệu dùng lại khóa phiên bản.

### Watermark và kiểm thử tải

- Ngày 19/11/2026, 12 bản ghi còn lưu trong `social.live.raw` có cả giờ đăng và giờ nhập từ producer. Độ trễ trung vị là 412,1 phút và lớn nhất là 813,5 phút. Đây là mẫu nhỏ qua hai ngày. Chọn **24 giờ** làm khoảng chờ bảo thủ cho thống kê, tương ứng với phạm vi báo cáo trong ngày của dự án.
- Truy vấn thống kê đọc các phiên bản mới từ Delta sau khi được kích hoạt, tổng hợp theo **giờ đăng UTC** và ghi các khung giờ đã chốt vào `data/lakehouse/delta/hourly_report_counts/{mode}`. Nó có checkpoint riêng, dùng giờ mô phỏng trong chế độ simulation, và loại mốc đăng sau giờ nhận khỏi phép tính để bảo vệ watermark. Cửa sổ chỉ chốt khi giờ sự kiện trong luồng tiến đủ xa. Khi không có tin mới, watermark có thể đứng yên.
- Kho báo cáo gốc, bảng Delta đã xác thực, checkpoint Kafka và ba nhóm thời gian trên dashboard vẫn theo hợp đồng hiện có. Tin đến quá muộn có thể nằm ngoài số đếm theo giờ và vẫn đọc được trong `verified_reports`. JSON vận hành ở `data/lakehouse/_operations/structured_{mode}.json` ghi tốc độ, thời gian xử lý, watermark và số dòng bị loại khỏi phép tổng hợp trong lô gần nhất.
- Ca tải 5 phút trên máy Windows dùng 5 tin/giây, thêm một đợt 30 tin và bản sao 9.973 phiên bản Delta simulation. Cả 1.530 tin mới đi qua checkpoint và xuất hiện đúng một lần trong Delta qua 20 micro-batch. P95 từ lúc gửi đến khi hoàn tất lô là 35,75 giây. Sau tin cuối, luồng xử lý hết hàng chờ trong 25,69 giây. Trung vị micro-batch là 15.872 ms.
- Tái lập bằng `python scripts/pipeline/benchmark_structured_stream.py --seconds 300 --rate 5 --burst 30 --with-history`. Phép thử dùng topic ba partition riêng và thư mục tạm, chạy Kafka, Spark, Delta và truy vấn watermark thật. AI, Open-Meteo và Redis dùng điều kiện giả lập hoặc dự phòng. Kết quả đo áp dụng cho luồng xử lý và lưu trữ trên máy thử.

### Nghiệm thu phục hồi ngày 21/11/2026

Phép thử dùng Kafka hai partition, Spark Structured Streaming, Delta, Redis riêng và endpoint `/api/realtime-heatmap` thật. Dữ liệu đầu vào gồm ba tin kiểm thử cùng một tuyến đường. AI và Open-Meteo dùng đường dự phòng để kết quả phục hồi không phụ thuộc mạng ngoài.

- Dừng cưỡng bức tiến trình sau ghi JSONL và trước Delta, rồi dừng lần nữa sau ghi Delta và Redis nhưng trước file phục vụ. Checkpoint chưa xác nhận lô ở cả hai lần. Tiến trình khởi động lại bằng cùng checkpoint và đọc lại bản ghi.
- Gửi lại bản ghi đã xử lý sang partition khác và gửi thêm một tin mới. Dashboard trả đúng hai ID báo cáo trong một cụm. Khi tắt Redis rồi gửi tin thứ ba, dashboard đọc đủ ba ID từ file. Sau khi bật lại Redis, dashboard trả cùng ba ID từ Redis dù không gửi thêm tin.
- Đầu ra cuối có đúng ba báo cáo duy nhất trong JSONL nguồn, JSONL đã xử lý và Delta. Spark dùng timeout Redis hiện có và giao việc thử lại cho cơ chế phục hồi snapshot của ứng dụng, tránh mất thời gian dựng file dự phòng trong lúc Redis ngắt.

Tái lập với Kafka cục bộ và một Redis thử mới, rỗng, ánh xạ `127.0.0.1:16389`. Lệnh kiểm tra sẽ dừng và bật lại container Redis được chỉ định.

```powershell
docker run -d --name se363-recovery-redis -p 127.0.0.1:16389:6379 redis:7.2-alpine
.\.venv\Scripts\python.exe scripts\pipeline\verify_stream_recovery.py --redis-port 16389 --redis-container se363-recovery-redis
docker rm -f -v se363-recovery-redis
```

### Đo độ trễ qua ba chu kỳ live

Ba chu kỳ crawler miễn phí liên tiếp mất 46,30 giây, 38,84 giây và 49,86 giây, thu và gửi lần lượt 9, 1 và 1 tin. Kafka, Spark, Delta, Redis, AI và Open-Meteo đều chạy thật. Topic, checkpoint, bảng Delta và Redis DB của phép thử được cô lập. Cả 11 tin có trong Delta và được API heatmap đọc từ Redis. Độ trễ trung vị từ Kafka xác nhận đến API lần đầu trả tin là 19,05 giây, tối đa 19,07 giây, đo bằng polling 0,5 giây. Trung vị thời gian gọi API là 3,30 ms.

Runner tính `--interval` live theo khoảng cách mục tiêu giữa hai lần bắt đầu quét, với khoảng nghỉ tối thiểu 30 giây ở cấu hình mặc định 60 giây. Hai khoảng cách bắt đầu đo được là 76,30 và 68,84 giây. Theo công thức cũ và cùng thời gian quét, hai khoảng cách tương ứng là 106,30 và 98,84 giây. Simulation giữ lịch chờ sau mỗi lô. Phép đo này tập trung vào nhịp thu thập và xử lý các tin tìm được, chưa đo tải video cao hoặc độ trễ kéo dài nhiều giờ.

### Lịch Google RSS và nguồn trực tiếp

Runner mặc định nhắm chu kỳ live 30 giây. Các lượt chạy nối tiếp với khoảng nghỉ tối thiểu 5 giây. Google News RSS có lịch riêng 150 giây, mỗi lượt xoay vòng tối đa 8 truy vấn gồm 4 Facebook, 3 TikTok và 1 báo chí, với tối đa 2 worker. Khi Google trả HTTP 429 hoặc 503, crawler tạm dừng ít nhất 3 phút và tôn trọng `Retry-After` dài hơn. HTTP 403 dùng khoảng nghỉ tối thiểu 15 phút. Báo chí, VOV và 1022 vẫn được gọi khi Google đang nghỉ, YouTube có lịch riêng 120 giây.

Nhánh YouTube Data API dùng biến môi trường `YOUTUBE_DATA_API_KEY` tùy chọn. API tìm kiếm khoảng mỗi 5 phút và có thể tìm sớm theo địa điểm từ phản ánh mới của VOV hoặc Cổng 1022, với khoảng cách tối thiểu 2 phút giữa các lượt gọi. FreeCrawl lưu số lượt gọi trong SQLite trên máy để các tiến trình dùng cùng thư mục dự án chia sẻ giới hạn 90 lượt trong cửa sổ 25 giờ. Nhánh yt-dlp quét khoảng mỗi 2 phút. Hai nhánh tìm đồng thời khi cùng đến hạn và mỗi vòng đưa kết quả đạt lọc vào luồng live trong chính vòng đó. Cả hai ưu tiên video ngắn công khai, còn nhãn Shorts dựa trên URL Shorts đã xác nhận.

RSS báo chí đọc trực tiếp các mục thời sự, giao thông và xã hội với timeout, chọn tin mới nhất sau khi kiểm tra nội dung, khu vực và giờ đăng. Thiếu giờ đăng hợp lệ thì tin không đi vào heatmap.

Phép thử một lượt chỉ dùng nguồn trực tiếp trả 1 tin YouTube và 3 tin từ 1022 trong 41,62 giây, không gửi truy vấn Google RSS. RSS báo chí phản hồi nhưng không có tin đạt bộ lọc trong lượt thử. Nhánh Data API được kiểm tra bằng phản hồi giả lập do máy chưa cấu hình khóa.

Mục 2 trở đi ghi lại hiện trạng và các hướng phát triển tại thời điểm lập kế hoạch.

## 1. Mục tiêu và nguyên tắc bảo toàn hệ thống

Mục tiêu là cải thiện tính đúng đắn, khả năng phục hồi và chất lượng kết quả của hệ thống đang có. Tài liệu này không yêu cầu thay toàn bộ kiến trúc hoặc nâng cấp đồng loạt thư viện. Các phần dưới đây có mức hoàn thiện khác nhau: Spark đã xử lý batch, kho dữ liệu đã lưu JSONL/Parquet, bộ gom cụm đã hoạt động theo khoảng cách và thời gian, dashboard đã tìm điểm ngập lân cận. Những phần còn thiếu cần được bổ sung có kiểm soát.

Yêu cầu “không làm hư hệ thống” phải được cụ thể hóa thành cơ chế cô lập, kiểm chứng và quay lại phiên bản cũ. Chỉ đọc code không thể bảo đảm tuyệt đối mọi thay đổi sau này sẽ không phát sinh lỗi. Vì vậy, chỉ chuyển luồng phục vụ khi đã có bằng chứng đáp ứng các tiêu chí trong tài liệu này.

Các nguyên tắc bắt buộc khi triển khai:

1. Tích hợp bản sửa đã kiểm chứng trực tiếp vào đường chạy chính. Khi thử thay engine hoặc đổi định dạng lưu trữ, thực hiện đối chiếu trong môi trường riêng và chuẩn bị phương án phục hồi dữ liệu, offset trước khi chuyển luồng phục vụ.
2. Chạy đối chiếu bằng bản sao dữ liệu hoặc môi trường thử riêng. Với Kafka, dùng consumer group riêng; với Redis, dùng namespace riêng; với file, Delta và checkpoint, dùng thư mục riêng. Bản thử không được ghi vào trạng thái dashboard đang phục vụ.
3. Không đổi tên, xóa hoặc thay kiểu các trường API hiện có. Nếu bổ sung metadata, thêm trường tùy chọn và giữ lớp chuyển đổi về cấu trúc cũ.
4. Không sửa nhãn ASTE, master dataset, các phase audit hay checkpoint AI để phục vụ việc nâng cấp hạ tầng. Không khởi chạy crawler tính phí khi kiểm thử có thể dùng dữ liệu đã lưu.
5. Tách rõ live và simulation ở nguồn, trạng thái xử lý, checkpoint và đầu ra. Giữ nguyên phạm vi nghiên cứu gồm TP.HCM, Bình Dương và Bà Rịa - Vũng Tàu theo quy ước dự án.
6. Không thay đổi đồng loạt các thành phần trong một lần. Mỗi đợt có thay đổi nhỏ, kết quả đối chiếu, điểm dừng và cách rollback rõ ràng.

## 2. Tóm tắt hiện trạng

| Thành phần | Phần đã có trong code | Khoảng cách cần khắc phục | Hướng cải thiện |
| --- | --- | --- | --- |
| Streaming | KafkaConsumer đọc Kafka; tạo Spark DataFrame; GIS, heuristic, veracity và ghi đầu ra theo batch | Chưa dùng native Structured Streaming; checkpoint chưa phục hồi truy vấn; chưa có watermark | Củng cố tính bền vững trước, sau đó bổ sung engine Structured Streaming chạy đối chiếu |
| Lakehouse | JSONL phân vùng theo episode/ngày; Spark compaction xuất Parquet | Chưa có Delta table/transaction log; fallback JSONL dùng chung vùng mang tên Parquet | Giữ kho cũ, thêm bảng Delta ở đường dẫn riêng, kiểm chứng rồi mới dùng cho truy vấn |
| Gom cụm | Ghép báo cáo theo khoảng cách và thời gian, tổng hợp nguồn và số báo cáo | Thuật toán tham lam, phụ thuộc thứ tự; chưa quản lý đầy đủ trạng thái cụm qua batch và tin phục hồi | Làm kết quả ổn định, quản lý thành viên duy nhất, tách sự kiện và diễn biến trạng thái |
| Heatmap ASTE | Leaflet, ghim đại diện địa danh và tìm sự kiện gần người dùng | Cần phân biệt tọa độ đại diện với GPS hiện trường, tránh gom cụm/consensus sai ý nghĩa | Giữ ghim tim đường; bổ sung cấp định vị và tổng hợp theo địa danh; bỏ routing khỏi kế hoạch |

## 3. Streaming: từ batch hiện tại đến xử lý luồng có phục hồi

### 3.1. Căn cứ và điểm còn hạn chế

Mã liên quan: [spark_flood_processor.py](../bigdata/streaming/spark_flood_processor.py), [social_producer.py](../bigdata/producers/social_producer.py), [run_streaming_pipeline.py](../bigdata/run_streaming_pipeline.py).

Luồng hiện tại dùng KafkaConsumer.poll(), tạo DataFrame, xử lý rồi collect về driver để chạy veracity và cập nhật đầu ra. Đây là xử lý Kafka kết hợp Spark theo batch do ứng dụng điều phối. Chưa có truy vấn readStream/writeStream, watermark hay checkpoint hoạt động theo cơ chế Structured Streaming.

Một số điểm cần củng cố trước khi đổi engine:

- Kafka consumer bật tự động commit offset. Offset có thể được xác nhận trước khi các đầu ra đã ghi thành công; khi tiến trình lỗi, việc phục hồi chưa gắn chặt với kết quả lưu trữ.
- Vòng lặp lấy tối đa 15 bản ghi để xử lý rồi xóa current_batch trong finally. Nếu batch tích lũy vượt giới hạn này, phần dư có nguy cơ bị xóa. Cần kiểm tra tình huống nhiều partition cùng trả dữ liệu.
- Local buffer watcher đọc rồi làm rỗng file trước khi hoàn tất xử lý. Cần bảo vệ cả lỗi giữa chừng và trường hợp producer đang ghi đồng thời.
- Producer gửi Kafka bất đồng bộ; kết quả trả về chưa chứng minh broker đã nhận. Định danh bị đánh dấu đã thấy trước xác nhận gửi thành công có thể làm bỏ qua lần gửi lại.
- Gọi AI và thời tiết trên driver là bước chậm, có tác động mạng và có thể chạy lại khi retry. Đổi sang Structured Streaming không tự giải quyết điểm nghẽn này.

### 3.2. Cách cải thiện theo hai bước

**Bước A — củng cố đường chạy hiện có:** quản lý trạng thái xử lý thành công/thất bại rõ ràng; chỉ xác nhận nguồn sau khi đầu ra bền vững đã được ghi hoặc bản ghi đã được đưa vào nơi chờ retry/DLQ bền vững. Dùng khóa định danh ổn định để xử lý lại không tăng số sự kiện hay số người báo cáo. Không chỉ đổi auto-commit thành manual commit rồi xem là hoàn tất: cần quy định cách phục hồi khi một sink thành công nhưng sink còn lại thất bại.

Với buffer file, chuyển sang các đoạn file đã đóng và bàn giao bằng thao tác nguyên tử hoặc hàng đợi bền vững tương đương. Chỉ một bên sở hữu từng đoạn đang xử lý; không xóa file producer đang ghi. Bản ghi JSON lỗi được tách ra cùng lý do, các dòng hợp lệ còn lại vẫn được giữ.

**Bước B — bổ sung engine Structured Streaming:** đọc Kafka bằng nguồn streaming, parse bằng schema tường minh, giới hạn lượng đầu vào mỗi trigger và lưu checkpoint riêng. Giai đoạn đầu có thể dùng foreachBatch làm điểm nối với xử lý hiện có để giảm phạm vi thay đổi. Tuy nhiên, batch callback có thể chạy lại; các thao tác ghi, gọi AI và tổng hợp phải được thiết kế chịu retry.

Đầu ra bền vững nên là mốc phục hồi chính; Redis/dashboard là lớp phục vụ có thể dựng lại. Khi Redis lỗi nhưng dữ liệu bền vững đã lưu, cần hàng đợi hoặc tác vụ sửa đồng bộ sau, tránh mất bản ghi hoặc chặn vô hạn toàn pipeline. Cache kết quả AI/thời tiết phải có khóa gồm dữ liệu và phiên bản xử lý phù hợp; không dùng kết quả cũ cho nội dung đã thay đổi.

### 3.3. Thiết kế thời gian và watermark

Giữ create_time và historical_timestamp để tương thích, đồng thời quy định rõ các khái niệm nội bộ:

- Thời gian đăng gốc: phục vụ truy vết và đối soát thời tiết lịch sử.
- Thời gian tiếp nhận: phục vụ độ trễ và giám sát vận hành.
- Thời gian sự kiện dùng cho cửa sổ xử lý: lấy theo chính sách riêng cho live hoặc replay.

Simulation đang tái phát dữ liệu lịch sử bằng thời gian hiển thị mới. Không đưa historical_timestamp trực tiếp vào watermark của một luồng đồng hồ hiện tại vì có thể làm dữ liệu replay bị xem là quá muộn. Replay phải có đồng hồ/chính sách riêng và checkpoint riêng. Thời gian sai, thiếu hoặc nằm quá xa tương lai phải được cách ly trước khi có thể làm watermark tiến quá mức.

Watermark dùng cho các phép xử lý có trạng thái theo event time; chỉ khai báo watermark không tự lọc mọi bản ghi muộn hoặc thay thế chính sách giữ tin 24 giờ trên dashboard. Chọn độ trễ cho phép dựa trên phân bố độ trễ dữ liệu thật, chưa chốt cứng một con số khi chưa đo. Bản ghi quá muộn vẫn cần lưu lịch sử và ghi lý do xử lý; không âm thầm mất khỏi kho nguồn.

Theo [hướng dẫn Structured Streaming của Apache Spark](https://spark.apache.org/docs/latest/streaming/apis-on-dataframes-and-datasets.html), nguồn streaming, checkpoint và hành vi của từng sink cần được cấu hình phù hợp. Đặc biệt, foreachBatch mặc định có thể ghi lại batch; cần idempotency để tránh trùng. Không công bố “exactly-once toàn hệ thống” chỉ vì đã bật checkpoint.

### 3.4. Tương thích và nghiệm thu

- Giữ nguyên topics, cấu trúc event, API dashboard và nhánh local buffer hiện có khi thêm engine mới.
- Engine thử dùng consumer group và đầu ra riêng. Khi chuyển engine, phải xác định ranh giới offset đã xử lý; checkpoint mới không tự kế thừa offset của consumer cũ. Không dùng latest tùy tiện làm bỏ qua backlog.
- Đối chiếu các ca: bản ghi lặp, batch nhiều partition, lỗi giữa các sink, restart, Kafka/Redis/AI offline, JSON lỗi, tin đến muộn, thời gian tương lai và replay lịch sử.
- Đạt yêu cầu khi tập ID hợp lệ được bảo toàn, xử lý lại không nhân đôi hiệu ứng, lỗi có thể truy vết và khôi phục, độ trễ/bộ nhớ nằm trong mức đã đo phù hợp máy hiện tại.

Rollback: dừng engine mới, khôi phục writer cũ từ ranh giới nguồn đã ghi nhận, phát lại phần cần thiết qua cơ chế khử trùng lặp. Chỉ một writer được cập nhật vùng serving chính tại một thời điểm.

## 4. Lakehouse: bổ sung Delta mà giữ nguyên kho hiện có

### 4.1. Căn cứ và điểm còn hạn chế

Mã liên quan: [compaction_job.py](../bigdata/lakehouse/compaction_job.py), [backfill_episodes.py](../bigdata/lakehouse/backfill_episodes.py), hàm ghi cold path trong spark_flood_processor.py.

Hiện hệ thống ghi JSONL phân vùng; compaction dùng Spark để ghi Parquet. Chưa có ghi bảng Delta và transaction log tương ứng. Cài dependency delta-spark trong requirements không đồng nghĩa dữ liệu đang được quản lý bằng Delta.

Nhánh standalone ghi consolidated_events.jsonl vào vùng silver_parquet_lakehouse. Vì vậy, consumer có thể gặp dữ liệu khác định dạng trong vùng được hiểu là Parquet. Việc bắt lỗi theo cả file còn có thể bỏ sót các dòng phía sau một dòng JSON hỏng. coalesce(1) tiện cho phân vùng nhỏ nhưng sẽ thành nút thắt khi dữ liệu tăng. Ghi overwrite trực tiếp vào phân vùng đích cần được đánh giá cùng hoạt động của reader và writer khác.

### 4.2. Cách cải thiện

1. Lập danh mục dữ liệu và các reader hiện đang dùng từng đường dẫn trước khi di chuyển. Giữ nguyên kho JSONL làm nguồn truy vết; thêm vùng Delta riêng, không trộn hai định dạng trong cùng gốc bảng.
2. Chuẩn hóa schema Silver có phiên bản, quy tắc null, kiểu thời gian và đơn vị tọa độ rõ ràng. Giữ thông tin nguồn, ID, nội dung gốc và phiên bản AI/heuristic để tái xử lý được.
3. Thiết kế Bronze lưu báo cáo nguồn, Silver lưu báo cáo đã chuẩn hóa, Gold lưu tổng hợp. Nếu hiện chỉ có payload đã qua xác minh, không gọi bản sao của nó là raw Bronze; muốn có Bronze đúng nghĩa phải lưu cả đầu vào trước biến đổi.
4. Chốt khóa theo loại dữ liệu: một báo cáo nguồn có định danh ổn định; lịch sử sửa đổi cần thêm phiên bản hoặc dấu vết nguồn; incident có định danh riêng. Không áp dụng một canonical_id duy nhất để vô tình ghi đè lịch sử.
5. Nạp dữ liệu cũ vào bảng mới, kiểm tra số lượng, tập ID, null, lỗi parse và checksum/nội dung tương đương. Phần lỗi vào khu cách ly, không loại bỏ im lặng.
6. Compaction chỉ xử lý dữ liệu đã bàn giao hoặc có snapshot rõ ràng. Chọn số lượng/kích thước file theo lượng dữ liệu đo được; không ép một file cho mọi phân vùng. Nhánh không có Spark phải ghi vào vùng JSONL riêng và báo đúng định dạng.
7. Giữ Redis làm hot store. Bổ sung Delta không buộc dashboard đổi cách đọc hay tăng thời gian phản hồi của bản đồ.

Phân vùng theo ngày sự kiện hay ngày tiếp nhận phải được quyết định rõ và lưu cả hai mốc. Tránh phân vùng quá nhỏ theo mọi tổ hợp episode/ngày nếu tạo nhiều file vụn. Không chạy tác vụ xóa dữ liệu cũ/VACUUM trong giai đoạn chuyển đổi ban đầu.

Trước khi cài đặt, kiểm kê phiên bản Spark, Delta, Java, Scala và Kafka connector thực tế của môi trường. Chọn và khóa một bộ tương thích trong môi trường thử riêng, theo [bảng tương thích chính thức của Delta Lake](https://docs.delta.io/releases/). Các ràng buộc >= trong requirements hiện tại chưa đủ để bảo đảm một tổ hợp cài đặt tương thích.

### 4.3. Tương thích và nghiệm thu

Chạy nhập lại cùng dữ liệu phải cho kết quả đúng theo chính sách khóa; restart giữa lần ghi không làm lộ bảng dở dang; schema lạ được cách ly hoặc chuyển đổi có kiểm soát. Mọi chênh lệch số lượng phải giải thích được bằng danh sách bản ghi cụ thể, không chỉ so tổng số.

Chỉ chuyển các tác vụ phân tích sang bảng mới sau khi truy vấn đối chiếu khớp. Kho cũ và reader cũ vẫn hoạt động khi tắt tính năng Delta. Rollback bằng cấu hình reader/writer cũ; không cần chuyển đổi ngược bảng Delta hay xóa dữ liệu mới để hệ thống phục vụ lại.

## 5. Gom cụm: ổn định kết quả và bảo toàn diễn biến ngập

### 5.1. Căn cứ và điểm còn hạn chế

Mã liên quan: [spatio_temporal_clusterer.py](../pipeline/spatio_temporal_clusterer.py), [veracity_checker.py](../pipeline/veracity_checker.py), các điểm gọi clusterer trong streaming, runner và dashboard.

cluster_events hiện duyệt lần lượt, ghép báo cáo vào cụm đầu tiên thỏa bán kính 400 m và chênh thời gian 45 phút so với đại diện. Đây là cách gom cụm tham lam, chưa phải DBSCAN.

Các hạn chế đáng chú ý:

- Đổi thứ tự đầu vào có thể đổi kết quả; vị trí đại diện không được tính lại từ toàn bộ thành viên.
- Mỗi lần gọi tạo danh sách cụm mới. Việc cộng dồn các cụm qua hot store chưa tương đương quản lý một incident bền vững qua nhiều batch.
- report_count tăng theo lần ghép, chưa bảo đảm số báo cáo duy nhất hoặc số tác giả độc lập. Bài đăng lại có thể làm tăng bằng chứng.
- Sao chép event còn nông; thay đổi location/heat_points/veracity lồng bên trong có thể tác động dữ liệu đầu vào được dùng tiếp cho cold path.
- Chưa tách ngập đang diễn ra với tin phục hồi, dự báo hoặc khen ứng phó. Gom gần nhau rồi nâng confidence không đủ để kết luận trạng thái thực địa.
- Các điểm tọa độ fallback chung của thành phố có thể bị hiểu nhầm thành đồng thuận địa lý thực sự.

### 5.2. Cách cải thiện đề xuất

**Giai đoạn đầu, cải thiện bộ gom hiện có trước khi đổi thuật toán:** chuẩn hóa đầu vào, tách dữ liệu live/simulation, loại trùng theo ID và sắp xếp bằng khóa ổn định. Chọn cụm theo điểm phù hợp rõ ràng thay vì cụm đầu tiên. Không sửa đối tượng lồng của bản ghi gốc khi tổng hợp.

Thiết kế một incident có ID ổn định, tập report ID duy nhất, thời điểm bắt đầu/cập nhật, danh sách nguồn và lịch sử trạng thái. Định nghĩa riêng “số báo cáo”, “số tác giả xác định được” và “số nền tảng”; không gọi tất cả là số người. Bổ sung giới hạn thời gian, số thành viên và độ lan rộng để một chuỗi báo cáo nối tiếp không kéo thành cụm quá dài.

Vị trí phải đi kèm độ chính xác: điểm đã xác định tuyến đường, tâm phường hay fallback thành phố. Chỉ dùng bằng chứng địa lý đủ chính xác cho gom cụm theo mét; báo cáo diện rộng được hiển thị và lưu nhưng không tự tạo đồng thuận tại tâm thành phố. Các đường song song, cầu vượt và hầm gần nhau cần xét định danh đường hoặc bối cảnh để tránh ghép chỉ vì gần GPS.

Tách liên kết với incident khỏi quyết định trạng thái của incident. Tin “nước đã rút” vẫn có thể thuộc cùng sự cố lịch sử với tin “ngập sâu”, nhưng phải trở thành cập nhật trạng thái, không cộng như bằng chứng ngập đang diễn ra. POS khen cứu hộ không tự đồng nghĩa mặt đường đã hết ngập. Trường hợp xung đột cần giữ cả bằng chứng và hiển thị trạng thái chưa thống nhất; không tự xóa cảnh báo chỉ từ một nhãn POS.

Giữ hai cơ chế khác mục đích: consensus 500 m/60 phút của VeracityChecker đánh giá bằng chứng; clustering 400 m/45 phút hợp nhất incident. Đưa tham số về nơi cấu hình thống nhất, nhưng không ép hai cơ chế dùng cùng ngưỡng. Khi tính confidence, tránh đếm lại cùng nguồn ở cả hai bước. Vì veracity đang được gọi nhiều luồng, trạng thái recent_events cần được cập nhật an toàn và có thứ tự xác định hoặc được tính từ snapshot riêng.

**Giai đoạn sau mới so sánh thuật toán:** thử gom theo điều kiện không gian–thời gian trên cửa sổ hữu hạn, có chỉ mục không gian khi quy mô cần thiết. Nếu thử DBSCAN, dùng khoảng cách địa lý đúng đơn vị và thêm ràng buộc thời gian thực sự; không chạy DBSCAN chỉ theo GPS rồi gọi đó là gom cụm không gian–thời gian. Chỉ thay khi tập tình huống đã đánh giá cho thấy kết quả tốt hơn. DBSCAN cũng cần cơ chế giữ ID và nối cụm qua các cửa sổ.

### 5.3. Tương thích và nghiệm thu

Giữ các trường dashboard đang dùng: location, weight, report_count, sources, posts_summary, is_cluster, cluster_label và veracity. Metadata incident mới là trường bổ sung. Cold path giữ nguyên các báo cáo nguồn; bảng incident là dữ liệu dẫn xuất riêng.

Các ca bắt buộc: đảo thứ tự đầu vào; cùng bài xuất hiện lại; cùng sự cố trải qua nhiều batch; hai đường gần nhau; điểm fallback thành phố; tin ngập rồi nước rút; POS khen cứu hộ; hai tin trái ngược cùng thời điểm; restart và replay. Kiểm tra cả dữ liệu đầu vào không bị biến đổi sau khi gom.

Rollback bằng cách tắt bộ gom mới và dùng đầu ra cũ. Khi chuyển đổi, ghi serving vào namespace mới rồi chuyển reader có kiểm soát; không để cụm cũ và cụm mới cùng xuất hiện gây đếm đôi. Báo cáo nguồn phải đủ để dựng lại incident nếu bỏ trạng thái thử.

## 6. Heatmap đại diện địa danh và bảo toàn kết quả ASTE

### 6.1. Mục tiêu thực tế đã được làm rõ

Hệ thống phục vụ phát hiện thông tin ngập lụt tại TP.HCM và phân tích ASTE từ social/báo chí. Bài viết thường chỉ nêu tên đường, phường/xã hoặc thành phố, không cung cấp GPS hiện trường. Tọa độ tim đường dùng để ghim đại diện cho tuyến đường có tin báo ngập; đó không phải tọa độ đo được của vị trí ngập, và cũng không chứng minh toàn bộ tuyến đường đang ngập.

Theo yêu cầu cập nhật của người dùng, bỏ đề xuất tính tuyến thay thế khỏi kế hoạch triển khai. Đích đến của người dùng chưa được thu thập, trong khi dữ liệu hiện có cũng chưa xác định đủ đoạn ngập để hỗ trợ định tuyến đáng tin cậy. Không cần bổ sung routing để đạt mục tiêu hiện tại của đề tài. Các chức năng bản đồ và tìm điểm ngập lân cận đang có vẫn được giữ nguyên.

### 6.2. Cách cải thiện phù hợp với dữ liệu đang có

1. Giữ nguyên Aspect và Opinion nguyên văn trong kết quả ASTE. Tên địa danh chuẩn hóa, mã đường/phường và tọa độ đại diện thuộc lớp GIS bổ sung; không ghi đè span ASTE bằng tên chuẩn hóa.
2. Phân biệt ít nhất ba cấp định vị: tuyến đường, phường/xã, toàn thành phố. Nếu có đoạn đường hoặc giao lộ được nêu rõ và định vị được, lưu thêm mức cụ thể đó; không suy diễn đoạn ngập khi bài chỉ nhắc tên đường.
3. Lưu nguồn và kiểu định vị bằng metadata tùy chọn: vị trí đại diện từ gazetteer, tâm đơn vị hành chính, hay tọa độ trực tiếp nếu sau này có nguồn cung cấp. Không dùng confidence của AI nội dung để thay cho độ chính xác không gian.
4. Ưu tiên địa danh cụ thể đã có trong văn bản, dùng bối cảnh phường/xã để phân biệt tên đường trùng nhau. Khi chưa phân giải được, giữ trạng thái chưa xác định hoặc hiển thị ở cấp rộng phù hợp; không tự ghim một vị trí chính xác giả.
5. Popup/legend giải thích ngắn: “Vị trí đại diện tuyến đường có tin báo ngập”. Tin chỉ nêu phường/xã hoặc TP.HCM cần cách hiển thị phân biệt, tránh tạo cảm giác ngập tập trung tại tâm hành chính.
6. Tiếp tục dùng heatmap làm trực quan thông tin báo ngập. Không diễn giải bán kính/gradient quanh marker thành ranh giới ngập đo đạc. Pin jitter chỉ là dịch chuyển khi hiển thị; không dùng tọa độ jitter để gom cụm, đối soát thời tiết hoặc lưu vị trí gốc.

### 6.3. Điều chỉnh gom cụm và consensus theo ý nghĩa tọa độ

Khi các báo cáo dùng cùng tọa độ tim đường, khoảng cách bằng không có thể chỉ do cùng phép tra gazetteer. Đây là dấu hiệu cùng nhắc một tuyến đường, chưa đủ khẳng định cùng một điểm ngập. Vì vậy, gom báo cáo theo định danh địa danh đã phân giải, bối cảnh thời gian và trạng thái ngập; dùng khoảng cách như tín hiệu bổ trợ theo cấp định vị.

Nếu hai bài nói cùng đường nhưng khác đoạn rõ ràng, cần giữ thông tin đoạn và tránh gộp mất chi tiết. Nếu không có thông tin đoạn, có thể tổng hợp ở cấp tuyến đường với nhãn “nhiều báo cáo trên cùng tuyến”, không gọi là cùng vị trí hiện trường. Hai đường khác nhau dù gần GPS cũng không tự động bị gom chung. Các báo cáo cấp phường/thành phố không được đóng vai trò bằng chứng trong bán kính 500 m chỉ vì có chung tọa độ tâm.

Đếm báo cáo duy nhất và nguồn độc lập vẫn hữu ích. Tuy nhiên, không nâng confidence chỉ vì nhiều bản ghi được gán cùng tim đường hoặc cùng tâm phường. Tin phục hồi, dự báo và khen cứu hộ vẫn cần được phân biệt theo ngữ nghĩa như mục 5.

### 6.4. Tương thích và nghiệm thu

Giữ location.lat/lon, heat_points và cấu trúc API hiện tại cho dashboard. Metadata về cấp định vị là trường thêm tùy chọn; bản ghi cũ chưa có metadata vẫn phải đọc được. Không tự ý đổi toàn bộ tọa độ đang được gazetteer quản lý trong đợt cải thiện này.

Nghiệm thu bằng các trường hợp: bài chỉ nêu tên đường; bài nêu đường kèm phường; đường trùng tên; bài nêu giao lộ; bài chỉ nêu phường hoặc thành phố; hai tin cùng đường khác đoạn; và nhiều báo cáo trùng tim đường. Kiểm tra span ASTE không đổi, ghim vẫn đúng địa danh đại diện, thống kê không đếm đôi và không tạo đồng thuận GPS giả.

Rollback bằng cách tắt phần hiển thị/metadata mới và quay về lớp bản đồ hiện tại; không cần sửa ngược nội dung ASTE hay kho nguồn.

## 7. Hợp đồng tương thích cần giữ

| Ranh giới | Phần phải bảo toàn | Cách bổ sung an toàn |
| --- | --- | --- |
| Producer → xử lý | Topic live/sim, ID, text, platform, URL, media và các mốc thời gian | Bổ sung metadata có phiên bản; xử lý được bản ghi cũ thiếu trường mới |
| Xử lý → dashboard | Các endpoint và kiểu dữ liệu đang được JavaScript sử dụng | Adapter từ event/incident mới về payload hiện có |
| Redis/file fallback | Hành vi reader và định danh sự kiện đang phục vụ | Namespace thử riêng; một writer chính; file tạm riêng và thay thế nguyên tử |
| Cold storage → phân tích | Kho nguồn còn đọc được và truy vết được | Delta ở đường dẫn mới; reader chọn bằng cấu hình |
| AI → veracity | Hợp đồng response, timeout và fallback hiện có | Không thay checkpoint hoặc quy tắc nhãn trong cùng đợt nâng hạ tầng |
| Live ↔ simulation | Phân biệt nguồn, đồng hồ, bộ nhớ trạng thái và đầu ra | Không chia sẻ checkpoint hay tập consensus/incident giữa hai mode |

Các API và trường phụ thuộc cần được liệt kê từ cả server và JavaScript trước khi sửa. Ngoài streaming, dashboard và runner cũng có đường ghi serving; nếu chỉ cải thiện một writer mà để các writer còn lại ghi cùng file hoặc cùng trạng thái không phối hợp, hệ thống vẫn có thể mất cập nhật.

### 7.1. Dashboard là hệ thống 7 panel dùng chung dữ liệu

Heatmap là một trong 7 panel của dashboard, không phải toàn bộ giao diện. Danh sách dưới đây lấy đúng nhãn sidebar và data-panel trong dashboard/index.html, đã đối chiếu với hình người dùng cung cấp. Hình là phiên bản icon cũ; khi triển khai phải giữ bộ icon SVG/thư viện chuẩn đang có trong code, không phục hồi emoji từ hình. Mọi cải thiện ở nguồn dữ liệu, gom cụm, lưu trữ hoặc API phải được đánh giá theo tác động đến cả 7 panel. Không thiết kế lại dashboard thành một màn hình heatmap độc lập hoặc làm mất cách điều hướng giữa các panel đang có.

| Phím / thứ tự | Tên panel đúng trên menu | Định danh trong code | Nhóm sidebar |
| --- | --- | --- | --- |
| 1 | Bản Đồ Nhiệt | panel-heatmap | Bản Đồ Không Gian |
| 2 | Phường/Xã & Vùng | panel-wards | Thống Kê Địa Giới |
| 3 | Diễn Biến Theo Giờ | panel-trends | Phân Tích Dữ Liệu |
| 4 | Tốc Độ Thu Thập | panel-throughput | Phân Tích Dữ Liệu |
| 5 | Tin Báo Hiện Trường | panel-feed | Hiện Trường & Hạ Tầng |
| 6 | Sức Khỏe Hệ Thống | panel-health | Hiện Trường & Hạ Tầng |
| 7 | Pool Key Apify | panel-apify-pool | Quản Trị API Cloud |

| Panel | Yêu cầu khi cải thiện hệ thống |
| --- | --- |
| 1. Bản Đồ Nhiệt | Giữ ghim đại diện địa danh, marker/popup, lớp bản đồ và các thao tác hiện có; phân biệt cấp định vị mà không suy diễn vùng ngập chính xác |
| 2. Phường/Xã & Vùng | Giữ ánh xạ hành chính, phân vùng đô thị và kiểm tra lại cách tổng hợp khi báo cáo được gom thành incident; không để một sự cố bị đếm lặp do nhiều marker |
| 3. Diễn Biến Theo Giờ | Quy định rõ đang đếm báo cáo hay incident, dùng mốc thời gian nào và phân biệt live/simulation; thay thuật toán gom cụm không được âm thầm đổi ý nghĩa biểu đồ |
| 4. Tốc Độ Thu Thập | Tách số bản ghi tiếp nhận, hợp lệ, loại trùng, đã xác minh và số incident; không coi giảm marker sau gom cụm là giảm thông lượng hoặc tăng tỷ lệ loại tin rác |
| 5. Tin Báo Hiện Trường | Giữ truy cập các bài nguồn, thời gian, kết quả ASTE và liên kết; gom thành incident không làm mất bài gốc hoặc che khuất cập nhật nước rút |
| 6. Sức Khỏe Hệ Thống | Phản ánh trạng thái và độ trễ đo được của các thành phần; phân biệt engine phục vụ chính với engine đang chạy thử, tránh báo khỏe dựa vào giá trị mặc định |
| 7. Pool Key Apify | Giữ các thao tác và thông tin pool hiện có; kiểm thử cải thiện hạ tầng bằng dữ liệu lưu sẵn không được vô tình kích hoạt crawl, tiêu quota hay thay cấu hình tài khoản |

Trước khi sửa phải lập bảng phụ thuộc panel → endpoint → trường dữ liệu → nguồn tính toán. Với các chỉ số dùng chung, chốt riêng đơn vị “báo cáo nguồn”, “incident ngập” và “địa danh có tin báo”; các panel có thể dùng đơn vị khác nhau nếu được đặt tên rõ, không ép mọi panel dùng cùng một số đếm.

Giữ nhịp cập nhật và cơ chế điều hướng hiện tại làm baseline. Tránh để mỗi panel tự gọi lại AI, quét toàn bộ kho dữ liệu hoặc mở một vòng polling trùng lặp. Ưu tiên tái sử dụng snapshot/tổng hợp chung có thời điểm và phiên bản rõ ràng, sau đó đo hiệu quả trước khi thay cơ chế refresh. Nếu một API phụ hoặc panel lỗi, các panel còn lại vẫn phải sử dụng được dữ liệu hợp lệ gần nhất hoặc hiển thị trạng thái thiếu dữ liệu rõ ràng.

Nghiệm thu giao diện phải đi qua cả 7 panel: chuyển panel, phím tắt, sidebar, resize bản đồ/biểu đồ, refresh dữ liệu và đổi live/simulation. Đối chiếu số liệu với cùng snapshot nguồn, kiểm tra tin mới và tin phục hồi xuất hiện đúng, bảo đảm panel không hiển thị lẫn dữ liệu khác mode. Các tính năng thử nghiệm không được làm thay đổi cấu trúc 7 panel hiện có.

### 7.2. Tương thích toàn hệ thống là điều kiện chuyển đổi

Kiểm tra đủ 7 panel là một phần của nghiệm thu, chưa đủ để kết luận toàn hệ thống tương thích. Mỗi cải tiến phải có bảng tác động tới crawler/poller, producer, Kafka và local buffer, xử lý Spark, GIS/admin resolver, AI/veracity, clustering, Redis/file fallback, cold storage/compaction/backfill, dashboard API và các script khởi động. Thành phần không chịu tác động trực tiếp vẫn cần được kiểm tra tại ranh giới dùng chung dữ liệu hoặc dependency.

Trước khi bật luồng mới phải đối chiếu đầu vào/đầu ra trên dữ liệu lưu sẵn, thử khởi động bằng entrypoint hiện có, thử lỗi/restart và xác nhận rollback. Giữ nguyên tên trường, kiểu dữ liệu, đơn vị, định danh và ý nghĩa thời gian mà consumer cũ đang dùng; mọi thay đổi ý nghĩa cần adapter hoặc phiên bản mới rõ ràng. Đối chiếu cả dữ liệu thô lẫn các phép tổng hợp để tránh trường hợp API vẫn trả HTTP 200 nhưng số liệu đã sai.

Không nâng cấp dependency trong môi trường ổn định chỉ để thử một tính năng. Thử bộ phiên bản mới ở môi trường riêng; nếu chưa chứng minh được đường chạy cũ vẫn hoạt động hoặc chưa có cách phục hồi dữ liệu/offset tương ứng, giữ tính năng mới ở chế độ thử và chưa chuyển phục vụ. Mục tiêu là nâng chất lượng từng phần mà giữ toàn bộ chuỗi hiện có sử dụng được.

## 8. Thứ tự triển khai đề xuất

1. **Chốt baseline:** ghi phiên bản code và môi trường, cách khởi động hiện tại, snapshot dữ liệu thử, tập ID đầu ra, độ trễ và bộ nhớ. Đọc test trước khi chạy vì smoke test hiện có có thể gọi mạng và ghi DLQ; test live còn phụ thuộc thời tiết thực tế.
2. **Củng cố tính bền vững:** xác nhận gửi Kafka, quản lý offset, buffer không mất dữ liệu, idempotency và phối hợp writer. Đây là nền móng cho mọi bước sau.
3. **Cải thiện gom cụm trên dữ liệu đã lưu:** kiểm tra thứ tự, bản ghi lặp, trạng thái phục hồi, chất lượng tọa độ và bảo toàn báo cáo nguồn.
4. **Thử Structured Streaming riêng:** giữ adapter đầu ra, kiểm tra restart và ranh giới chuyển offset trước khi thay engine chính.
5. **Thử Delta riêng:** khóa dependency tương thích, nhập đối chiếu và chuyển các truy vấn phân tích từng phần. Delta và engine streaming không bắt buộc phải được chuyển cùng một đợt.
6. **Hoàn thiện Heatmap ASTE:** giữ ghim tim đường đại diện, phân biệt cấp đường/phường/thành phố, bảo toàn span ASTE và kiểm tra consensus không bị tăng giả do tọa độ quy ước. Không bổ sung routing trong kế hoạch này.

Đây là thứ tự theo quan hệ phụ thuộc, không phải cam kết hoàn thành tất cả trong một ngày. Mỗi bước phải có một phiên bản có thể review và quay lại độc lập.

## 9. Điều kiện chuyển sang phục vụ và điều kiện dừng

Trước mỗi lần bật cho luồng chính phải xác nhận: hợp đồng API cũ vẫn đọc được; live/sim không trộn; bản ghi hợp lệ được bảo toàn; retry không nhân đôi hiệu ứng; fallback cũ còn hoạt động; số liệu hiệu năng được đo trên máy thực tế; và quy trình rollback đã được thử trong môi trường riêng.

Chưa nên chốt ngưỡng hiệu năng bằng số quảng cáo trong comment. Đặt ngân sách độ trễ/bộ nhớ từ baseline và mục tiêu đã thống nhất trước khi chuyển đổi. Đo riêng thời gian nhận nguồn, xử lý Spark, AI/thời tiết, ghi kho và phục vụ dashboard để biết phần nào gây chậm.

Dừng chuyển đổi nếu xuất hiện ID bị mất chưa giải thích được, tăng report_count khi replay, sai trường/kiểu API, lẫn live/sim, nhãn phục hồi làm xóa nhầm cảnh báo, dữ liệu thử ghi vào serving chính, hoặc dependency mới làm đường chạy cũ không khởi động. Giữ bằng chứng lỗi và quay về writer/reader cũ theo ranh giới nguồn đã ghi nhận.

Tài liệu này chỉ đề xuất cách làm. Việc triển khai sau cần bám từng bước, kiểm chứng bằng dữ liệu hiện có và cập nhật tài liệu bàn giao theo đúng mức tính năng đã chạy thành công.

## 10. Điều chỉnh ưu tiên sau phiên vận hành thực tế 18/11/2026

Đã chạy simulation và live end-to-end, duyệt cả 7 panel, thử Fast/Slow Path, compaction và read fallback Redis/file. Chi tiết bằng chứng và giới hạn nằm trong [báo cáo kiểm tra vận hành](BAO_CAO_KIEM_TRA_VAN_HANH_2026_11_18.md).

Ưu tiên triển khai trước mắt là sửa các vấn đề đã tái hiện: biểu đồ theo giờ phân loại sai POS/NEU, health báo ONLINE mặc định và sai cổng AI, lỗi redraw canvas khi chuyển trạng thái panel, gom cụm đếm trùng/thay đổi input, và timeout media chưa phù hợp thời gian xử lý. Những việc này sát mục tiêu ASTE + phát hiện ngập và ít mở rộng phạm vi hơn thay engine ngay.

Native Structured Streaming và Delta vẫn là hướng cải thiện có điều kiện, sau khi củng cố ack/offset/buffer và idempotency. Phiên thử cho thấy Spark/Parquet hiện có chạy được trên môi trường thực tế; không nên nâng dependency hoặc thay toàn bộ đường chạy chỉ để khớp mô tả kiến trúc. Giữ các yêu cầu tương thích và rollback ở các mục trước cho từng thay đổi.
