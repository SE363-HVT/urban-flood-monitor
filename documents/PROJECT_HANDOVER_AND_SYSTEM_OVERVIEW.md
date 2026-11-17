# 📘 BÀN GIAO TOÀN DIỆN DỰ ÁN & CẨM NANG HỆ THỐNG (PROJECT HANDOVER & SYSTEM OVERVIEW)
## Real-Time Multimodal Urban Flood Monitoring & Veracity Verification System (TP. Hồ Chí Minh & Vùng Đô Thị Mở Rộng)

> **Dự án**: Đồ án Chuyên ngành Dữ liệu lớn (SE363) - Trường ĐH Công nghệ Thông tin (UIT - VNU-HCM) & Mục tiêu Công bố Quốc tế (ICWSM / EMNLP).  
> **Người thực hiện**: Nhóm nghiên cứu SE363 (Thuận - Primary Annotator / System Lead & Hùng - Independent Peer Annotator).  
> **Mục đích tài liệu**: Cung cấp bức tranh toàn cảnh 100% về kiến trúc hệ thống, toàn bộ mã nguồn (source code), kho ngữ liệu ASTE (10.249 records), tiến độ thực tế, các kinh nghiệm thực chiến xương máu và quy trình thao tác chuẩn xác để **bất kỳ AI Agent / Chuyên gia mới nào tiếp nhận dự án đều có thể đọc hiểu và tiếp tục công việc ngay lập tức mà không gặp bất kỳ trở ngại nào**.

---

## 📑 MỤC LỤC CHI TIẾT
1. [TỔNG QUAN DỰ ÁN & MỤC TIÊU NGHIÊN CỨU](#1-tổng-quan-dự-án--mục-tiêu-nghiên-cứu)
2. [BẢN ĐỒ KIẾN TRÚC & MÔ TẢ CHI TIẾT TOÀN BỘ SOURCE CODE](#2-bản-đồ-kiến-trúc--mô-tả-chi-tiết-toàn-bộ-source-code)
3. [KHO NGỮ LIỆU ASTE MASTER 10.249 RECORDS & HIỆN TRẠNG 3 PHASES](#3-kho-ngữ-liệu-aste-master-10249-records--hiện-trạng-3-phases)
4. [BỘ KINH NGHIỆM THỰC CHIẾN XƯƠNG MÁU & NGUYÊN TẮC CỐT TỬ CỦA USER](#4-bộ-kinh-nghiệm-thực-chiến-xương-máu--nguyên-tắc-cốt-tử-của-user)
5. [CÔNG CỤ KIỂM ĐỊNH KÉP & BỘ HELPER TOÁN HỌC](#5-công-cụ-kiểm-định-kép--bộ-helper-toán-học)
6. [CÔNG VIỆC ĐANG LÀM VÀ HƯỚNG DẪN BẮT TAY LÀM TIẾP (NEXT STEPS RUNBOOK)](#6-công-việc-đang-làm-và-hướng-dẫn-bắt-tay-làm-tiếp-next-steps-runbook)
7. [BẢNG TRA CỨU LỆNH NHANH (CHEATSHEET)](#7-bảng-tra-cứu-lệnh-nhanh-cheatsheet)

---

## 1. TỔNG QUAN DỰ ÁN & MỤC TIÊU NGHIÊN CỨU

### 1.1. Bối cảnh & Bài toán
TP. Hồ Chí Minh chịu ảnh hưởng nặng nề bởi triều cường và mưa lớn cực đoan. Tuy nhiên:
- **Cảm biến thủy văn vật lý quá thưa thớt**: Chỉ được lắp tại một số kênh rạch lớn, hàng nghìn tuyến đường đô thị hoàn toàn không có cảm biến.
- **Dữ liệu mạng xã hội (TikTok, Facebook, VOV, Báo chí) cực kỳ phong phú và tức thời**, nhưng chứa đầy **nhiễu**:
  + Quảng cáo thương mại / rao vặt bất động sản (*"phòng trọ Huỳnh Tấn Phát ngập tràn ánh sáng"*, *"chậu hoa ngập kho"*).
  + Video câu like tái sử dụng (recycled clips) từ mùa mưa các năm trước đăng lại khi trời đang nắng ráo.
  + Mất cân bằng dữ liệu nghiêm trọng: Người dân chỉ kêu ca khi ngập (`NEG`), hầu như không ai đăng bài khi nước đã rút (`POS`), khiến hệ thống cảnh báo bị treo vĩnh viễn nếu không có cơ chế phát hiện nước rút.
  + Người dân quen than phiền về phương tiện (*"xe chết máy"*, *"hỏng bugi"*) thay vì nói thẳng tên tuyến đường.

### 1.2. Giải pháp Cốt lõi của Dự án
Xây dựng một hệ thống **Big Data Streaming kết hợp AI Đa phương thức (Multimodal AI) toàn trình**:
1. **Thu nạp đa nguồn thời gian thực (Multi-Engine Ingestion)**: Cào song song từ Cổng 1022 TP.HCM, VOV Giao thông, YouTube Shorts, Báo chí (VnExpress, Tuổi Trẻ, Thanh Niên), TikTok Video và Facebook Posts.
2. **Trích xuất thông tin cấu trúc bằng AI (ASTE - Aspect Sentiment Triplet Extraction)**: Trích xuất bộ 3 `(Aspect, Opinion, Polarity)` theo chuẩn quốc tế SemEval ASTE-Data-V2.
3. **Xác thực đa nguồn chống tin giả (Veracity Verification Engine)**: Kiểm chứng chéo với API thời tiết vật lý Open-Meteo và cơ chế đồng thuận không gian - thời gian bán kính 500m.
4. **Bản đồ Giám sát & Điều hướng Thời gian thực (Live Actionable GIS Dashboard)**: Hiển thị bản đồ nhiệt (Heatmap), cảnh báo điểm ngập, trạng thái nước rút và lộ trình tránh điểm ngập trên nền Leaflet.

---

## 2. BẢN ĐỒ KIẾN TRÚC & MÔ TẢ CHI TIẾT TOÀN BỘ SOURCE CODE

Thư mục gốc của dự án: `D:\SE363_RAWDATA`

```
SE363_RAWDATA/
├── core/                  # Thư viện nền tảng & cấu hình hệ thống
├── pipeline/              # Động cơ thu thập đa nguồn, clusterer, veracity checker
├── bigdata/               # Kiến trúc luồng phân tán (Kafka, PySpark, Lakehouse)
├── dashboard/             # Giao diện bản đồ nhiệt Leaflet & Web Server
├── AI/                    # Các mô hình ASTE Benchmark (PhoBERT, BARTpho, mT5, LLMs)
├── data/                  # Kho dữ liệu raw, processed, splits & validate_label
├── documents/             # Toàn bộ tài liệu quy chuẩn, cẩm nang và báo cáo
├── scripts/               # Bộ công cụ kiểm định kép (Linter), helper toán học & crawlers
└── tests/                 # Unit tests & smoke tests kiểm thử hệ thống
```

### 2.1. Thư mục `core/` (Cấu hình & Xử lý Địa danh)
- `core/config.py`: Cấu hình chung toàn hệ thống (Apify tokens, hashtag TikTok, danh sách Fanpage Facebook uy tín, tham số crawler).
- `core/admin_resolver.py`: Bộ phân giải đơn vị hành chính TP.HCM theo Nghị quyết mới 1685/NQ-UBTVQH15 (168 phường/xã/thị trấn mới, tọa độ 122 điểm ngập trọng điểm của PC08).
- `core/gazetteer.py`: Từ điển không gian địa lý (GIS Gazetteer) ánh xạ tên đường, cầu, nút giao về tọa độ kinh độ/vĩ độ (Lat/Lon).
- `core/apify_pool.py`: Bộ quản lý xoay vòng API Key Apify tự động (Key Pool Manager với cơ chế tự động chuyển key khi gặp HTTP 401/402 hết tiền).
- `core/state_manager.py`: Quản lý trạng thái luồng thu thập.

### 2.2. Thư mục `pipeline/` (Động cơ Thu thập & Lọc Dữ liệu)
- `pipeline/live_free_crawler.py`: Động cơ thu thập 100% miễn phí chạy đa luồng (16 workers):
  + Cổng thông tin 1022 TP.HCM (API JSON chính thức).
  + VOV Giao thông Ticker (Tin nóng tắc đường, ngập lụt).
  + YouTube Shorts & Videos qua `yt-dlp` (bộ lọc 24h).
  + RSS Báo chí chính thống (VnExpress, Tuổi Trẻ, Thanh Niên).
  + Google Discovery & Bing RSS làm fallback.
- `pipeline/tiktok_poller.py`: Cào video TikTok theo hashtag ngập lụt sử dụng Apify Actor `clockworks~free-tiktok-scraper`.
- `pipeline/facebook_poller.py`: Cào bài đăng Facebook sử dụng Apify Actor `danek~facebook-search-ppr`.
- `pipeline/simulation_replayer.py`: Động cơ phát lại (replay) 3.818 mẫu lịch sử sạch để demo hoặc chạy offline không cần mạng.
- `pipeline/veracity_checker.py`: Bộ kiểm định tin giả đa tầng:
  + Tầng 1: Heuristic lọc từ khóa rao vặt bất động sản/bán xe.
  + Tầng 2: Đối soát khí tượng thực tế Open-Meteo (nếu bài đăng bảo ngập sâu mà thời tiết 72h qua lượng mưa = 0mm $\rightarrow$ gắn cờ Recycled Video).
  + Tầng 3: Đồng thuận không gian - thời gian (Spatio-Temporal Consensus trong bán kính 500m).
- `pipeline/spatio_temporal_clusterer.py`: Gom cụm các cảnh báo ngập lụt theo thuật toán DBSCAN không gian - thời gian.
- `pipeline/multimodal_streamer.py`: Điều phối luồng xử lý đa phương thức (Text + Video frames).

### 2.3. Thư mục `bigdata/` (Tầng Xử lý Dữ liệu Lớn Phân tán)
- `bigdata/docker-compose.yml`: Triển khai hạ tầng hạ tầng gồm Apache Kafka 4.3.1 (KRaft mode, Port 9092) và Redis 7.2 In-Memory Hot Store (Port 6379).
- `bigdata/run_streaming_pipeline.py`: Khởi chạy PySpark Structured Streaming với micro-batch 5 giây.
- `bigdata/streaming/`: Mã nguồn PySpark streaming, xử lý JSON từ Kafka topic `social.live.raw`, giải nén và làm giàu dữ liệu qua Gazetteer.
- `bigdata/lakehouse/`: Tầng lưu trữ Delta Parquet (Bronze $\rightarrow$ Silver $\rightarrow$ Gold) phục vụ phân tích lịch sử ngập.

### 2.4. Thư mục `dashboard/` (Giao diện Bản đồ Điều hành)
- `dashboard/server.py`: HTTP Server viết bằng Python (Port 8050) phục vụ API dữ liệu ngập thời gian thực từ Redis hot store.
- `dashboard/index.html`: Giao diện Dashboard chuyên nghiệp:
  + Bản đồ Leaflet Heatmap hiển thị cường độ ngập theo thời gian thực.
  + Pin Jitter Algorithm: Thuật toán làm lệch nhẹ tọa độ marker để chống hiện tượng đè chồng lấp khi nhiều tin cùng báo một con đường.
  + Lucide Vector SVG Icons phân loại trực quan (Đỏ: Ngập sâu/Chết máy, Vàng: Ứ nước nhẹ, Xanh lá: Nước đã rút).
  + Lộ trình điều hướng tránh điểm ngập cho phương tiện giao thông.

### 2.5. Thư mục `AI/` (Nghiên cứu Mô hình Học sâu ASTE)
Gồm các kiến trúc mô hình được huấn luyện và đánh giá trên bộ dữ liệu của đề tài:
- `AI/phobert/`: Mô hình PhoBERT (base_v2 và large).
- `AI/bartpho/`: Mô hình BARTpho (syllable_base và word_base) theo hướng Generative ASTE.
- `AI/mt5/`: Mô hình đa ngôn ngữ mT5 base.
- `AI/xlm_roberta/` & `AI/xlm_v/`: Các backbone Transformer đa ngôn ngữ.
- `AI/llm/`: Đánh giá Zero-shot / Few-shot với LLM mã nguồn mở (Gemma 26B, Qwen 27B).
- `AI/results/`: Kết quả bảng so sánh Benchmark F1-score (`BENCHMARK_TABLE.md`, `benchmark_comparison.csv`).

### 2.6. Thư mục `scripts/` (Bộ Công cụ Kiểm định & Thao tác Dữ liệu Cốt lõi)
- **`scripts/deep_10_pass_audit.py`**: **LINTER KIỂM ĐỊNH TỐI CAO CỦA DỰ ÁN**. Bộ kiểm tra 10 chiều độc lập hoàn toàn Read-only (không tự ý sửa file), phát hiện mọi lỗi cú pháp, rò rỉ ranh giới, token offset và vi phạm quy chuẩn.
- **`scripts/audit_index_integrity.py`**: Bộ kiểm toán giải mã ngược (De-tokenization), lấy danh sách số thứ tự `[start...end]` đối soát ngược lại với văn bản gốc để chứng minh 100% khớp từ vựng, không có hiện tượng lệch token.
- **`scripts/span_helper.py`**: **BỘ HELPER TOÁN HỌC SINH TRIPLET AN TOÀN**. Chứa hàm `make_triplet(text, asp_phrase, opi_phrase, polarity)` giúp tự động định vị token span, tự động gọt sạch dấu câu ở biên (Pass 4) và giới từ ở đầu (Pass 5).
- **`scripts/stats_phase3.py`**: Xuất thống kê chi tiết tỷ lệ nhãn, số triplet, phân bố `NEG`/`POS`/`NEU` và top các thực thể xuất hiện nhiều nhất.

---

## 3. KHO NGỮ LIỆU ASTE MASTER 10.249 RECORDS & HIỆN TRẠNG 3 PHASES

Toàn bộ kho ngữ liệu gốc được chuẩn hóa theo chuẩn quốc tế SemEval ASTE-Data-V2 lưu tại [master_10k_triplets.txt](file:///D:/SE363_RAWDATA/data/processed/aste_v2_format/master_10k_triplets.txt) với đúng **10.249 dòng văn bản**:
$$\text{Cấu trúc: } \text{token}_0 \text{ token}_1 \dots \text{ token}_n \text{ #### } [([\text{asp}], [\text{opi}], '\text{POL}')]$$

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        CẤU TRÚC PHÂN CHIA 3 PHASES CỦA DỰ ÁN                           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • PHASE 1 (Dòng 1 ➔ 500: 500 records):                                                 │
│   Tập Benchmark Vàng sơ khởi do Thuận gán nhãn & đã audit chuẩn mực.                   │
│   Tệp lưu: data/validate_label/thuan/phase1.txt                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • PHASE 2 (Dòng 501 ➔ 2.500: 2.000 records):                                           │
│   Tập Đánh giá Mù Đôi (Double-Blind) giữa Thuận & Hùng để tính Cohen's Kappa.          │
│   Độ đồng thuận cảm xúc đạt κ = 0.88 (Substantial / Almost Perfect Agreement).         │
│   Tệp lưu: data/validate_label/thuan/phase2.txt & data/validate_label/hung/phase2.txt │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • PHASE 3 (Dòng 2.501 ➔ 10.249: 7.749 records còn lại): Chia đôi khối lượng:          │
│   1. PHẦN THUẬN (Dòng 2.501 ➔ 6.375: 3.875 records):                                   │
│      👉 TRẠNG THÁI: ĐÃ HOÀN TẤT 100%, ĐÃ AUDIT 10/10 PASSES ĐẠT 0 LỖI!                │
│      Tệp lưu: data/validate_label/thuan/phase3.txt                                     │
│   2. PHẦN HÙNG (Dòng 6.376 ➔ 10.249: 3.874 records):                                  │
│      👉 TRẠNG THÁI: ĐANG CHỜ TRIỂN KHAI (Hiện file đang trống 0 dòng).                │
│      Tệp lưu: data/validate_label/hung/phase3.txt                                      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Thống kê Nghiệm thu Chi tiết Phase 3 (Phần Thuận - 3.875 records vừa hoàn thành):
- **Số records có nhãn Triplet**: **3.798 records (98.01%)**.
- **Số records bị Reject thực sự (`####[]`)**: **Đúng 77 records (1.99%)** (chỉ gồm tỉnh ngoài như Bangkok, Hà Nội, Gia Lai và quảng cáo mua bán xe/phòng trọ).
- **Tổng số Triplets**: **4.976 triplets** (`NEG`: 3.286 | `POS`: 1.195 | `NEU`: 495).
- **Kiểm định kép 10-Pass Linter**: **10/10 PASSES: 0 LỖI (100% ĐẠT CHUẨN TOÁN HỌC)**.
- **Tính toàn vẹn Index**: **100% khớp từ vựng, 0 lỗi lệch token offset**.

---

## 4. BỘ KINH NGHIỆM THỰC CHIẾN XƯƠNG MÁU & NGUYÊN TẮC CỐT TỬ CỦA USER

> [!IMPORTANT]
> Đây là những nguyên tắc tối cao đã được kiểm chứng và chấn chỉnh qua hàng chục phiên làm việc với User. **Agent mới tuyệt đối không được vi phạm hay tự ý thay đổi bất kỳ quy tắc nào!**

### 1. 🚨 BẮT BUỘC LƯU Ý: Bình Dương & Vũng Tàu LÀ IN-SCOPE (TUYỆT ĐỐI CẤM REJECT)
- **Căn cứ**: Đề tài nghiên cứu áp dụng cho **Vùng Đại đô thị TP.HCM mở rộng (Greater HCMC Metropolitan Area)**. Về kinh tế, chuỗi cung ứng, luồng di chuyển lao động hàng ngày và lưu vực thủy văn (sông Sài Gòn - Đồng Nai), **Bình Dương** và **Vũng Tàu** là hai địa bàn đã sáp nhập kinh tế - không gian chặt chẽ với TP.HCM.
- **Khu vực Bình Dương**: *Thủ Dầu Một, Thuận An, Dĩ An, Bến Cát, Tân Uyên, Bàu Bàng, Lái Thiêu, ĐT743, ĐT744, ĐT748, QL13, KCN Sóng Thần, VSIP...* $\rightarrow$ **Bắt buộc giữ lại và gán nhãn** trực tiếp cho địa danh đó.
- **Khu vực Vũng Tàu**: *TP Vũng Tàu, TP Bà Rịa, TX Phú Mỹ, Đất Đỏ, Long Điền, Xuyên Mộc, Hồ Tràm, Đường 30/4, Thùy Vân, Hạ Long, Bãi Sau, Bãi Trước, Bến Đình...* $\rightarrow$ **Bắt buộc giữ lại và gán nhãn**.
- **Chỉ gán `REJECT (####[])` khi**: Sự kiện ngập diễn ra ở tỉnh ngoài thực sự (*Hà Nội, Cần Thơ, Cà Mau, Gia Lai, Tam Kỳ, Thái Lan/Bangkok, Trung Quốc...*).

### 2. ⚠️ Lỗi Lạm Dụng Fallback (`DOC_FALLBACK_MISUSE / PASS 9`)
- **Nguyên nhân sai lầm cũ**: Crawler tự động dán tiền tố `Tại TP. Hồ Chí Minh , ` vào câu. Khi trong câu **đã có tên đường cụ thể** (*đường Trần Xuân Soạn, đường Tô Ngọc Vân, đường Đặng Thùy Trâm, đường Linh Đông...*), annotator cũ gán Aspect là `TP. Hồ Chí Minh` khiến linter Pass 9 báo lỗi `SUSPECT_FALLBACK_USAGE`. Thay vì sửa Aspect thành tên đường, annotator cũ lại **thẳng tay gắn `####[]` để lách linter**, làm mất hàng trăm bản tin ngập lụt quý giá!
- **Quy tắc chuẩn**:
  + **Ưu tiên số 1**: Khi câu đã có tên đường / địa danh cụ thể $\rightarrow$ **BẮT BUỘC gán Aspect là tên đường / địa danh đó**, CẤM dùng Fallback `TP. Hồ Chí Minh`.
  + **Chỉ dùng Fallback khi**: Câu hoàn toàn không nhắc tới bất kỳ một tên đường cụ thể nào mà chỉ nói về hiện trường ngập chung chung (ví dụ: *"Tại TP. Hồ Chí Minh , Mưa lớn khiến hàng loạt xe chết máy"* $\rightarrow$ Aspect `TP. Hồ Chí Minh` `[1, 2, 3, 4]`).
  + **TUYỆT ĐỐI CẤM REJECT câu chỉ vì vi phạm Pass 9**: Phải sửa Aspect về đúng tên đường.

### 3. 🎭 Phân Biệt Khẩu Ngữ Châm Biếm Đời Thường (Slang/Satire) vs. Meme Giải Trí
- **Giữ lại và gán `NEG`**: Người dân dùng ngôn ngữ bình dân, ví von đời thực để kêu than ngập: *"thất thủ"*, *"như sông"*, *"hóa sông"*, *"biển nước"*, *"bì bõm"*, *"lội nước"*, *"dắt bộ xe máy"*, *"kê dọn đồ đạc"*, *"nước lút bánh xe"*, *"chèo xuồng tạm"*, *"mưa tí là ngập"*, *"nhà biến thành hầm"*. Đây là phản ánh hiện trường chân thực của bài toán đô thị!
- **Chỉ gán `REJECT (####[])` khi**: Yếu tố ngập lụt chỉ làm nền phụ cho nội dung giải trí khác:
  + So sánh phim hoạt hình/anime (*Vùng đất linh hồn*).
  + Clip đi xem ca nhạc concert (*chị Chi hát live*).
  + Clip thú cưng nô đùa dưới nước (`#thucung`, `#dangyeu`).
  + Mẹo kỹ thuật xử lý xe bị thủy kích chung chung.
  + Rao vặt phòng trọ studio, bán xe ô tô cũ, chậu hoa cây cảnh ngập kho.
  + Ký ức Sài Gòn trước năm 1975, tranh luận triết lý dùng lu chống ngập.

### 4. ✂️ Xử Lý Câu Bị Cắt Cụt Do Buffer Crawler
- Các bài viết từ TikTok/Facebook do giới hạn buffer (~250 ký tự) thường bị cắt ngang ở từ cuối (ví dụ: *"Khu vực giao với đường Linh Đông ngập nặng nhất , dòn..."*).
- **Quy tắc**: Nếu ở vế trước đã có đầy đủ địa danh (`đường Linh Đông`) và tình trạng ngập (`ngập nặng nhất`) $\rightarrow$ **Bắt buộc trích xuất Triplet**, không được vội vã đánh đồng là câu cụt để reject!

### 5. 🏗️ Phân Định Công Trình Hạ Tầng (`POS`) & Dự Báo Đỉnh Triều (`NEU`)
- Trạm bơm vận hành hết công suất, máy bơm di động, nạo vét kênh mương, cống kiểm soát triều, nước rút bớt, đường sau nâng cấp không còn ngập $\rightarrow$ Gán nhãn **`POS`**.
- Dự báo đỉnh triều, đo đạc mực nước tại các trạm Phú An, Nhà Bè, Thủ Dầu Một, Vũng Tàu $\rightarrow$ Gán nhãn **`NEU`**.

### 6. 🔄 Nguyên Tắc Nhất Quán Tuyệt Đối & Micro-Batching
- **User đặc biệt lưu ý**: Không được đổi quy tắc gán nhãn giữa chừng sau vài chục lô. Mọi lô từ đầu đến cuối phải tuân thủ nghiêm ngặt [BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md](file:///D:/SE363_RAWDATA/documents/BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md).
- **Micro-Batching**: Luôn chia nhỏ dữ liệu thành từng lô 50 – 100 records để đọc hiểu toàn bộ ngữ cảnh câu, không chạy ẩu hàng loạt bằng script heuristic thay thế việc đọc hiểu.

---

## 5. CÔNG CỤ KIỂM ĐỊNH KÉP & BỘ HELPER TOÁN HỌC

Kiến trúc kiểm định của dự án áp dụng mô hình **Dual-Engine Audit**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   KIẾN TRÚC KIỂM ĐỊNH KÉP (DUAL-ENGINE)                │
└────────────────────────────────────────────────────────────────────────┘
          │                                              │
          ▼                                              ▼
┌──────────────────────────────────┐   ┌──────────────────────────────────┐
│   ENGINE 1: CHUYÊN GIA / AGENT   │   │     ENGINE 2: SCRIPT AUDITOR     │
│   (Semantic Reasoning Engine)    │   │  (Mathematical & Linting Engine) │
├──────────────────────────────────┤   ├──────────────────────────────────┤
│ • Đọc hiểu trọn vẹn ngữ cảnh câu.│   │ • 100% READ-ONLY (Không sửa file)│
│ • Phân định POS / NEG / NEU.     │   │ • Đối soát toán học Span Index.  │
│ • Nhận diện địa danh In-Scope.   │   │ • Phát hiện rò rỉ giới từ/dấu câu│
│ • Quyết định trích xuất / reject.│   │ • Giải mã ngược (Reconstruction) │
└──────────────────────────────────┘   └──────────────────────────────────┘
```

### 5.1. Danh mục 10 Nhóm Lỗi Được Quét Bởi `deep_10_pass_audit.py`
1. **Pass 1: Syntax Format**: Kiểm tra cú pháp phân cách `####` và cấu trúc danh sách Python `[([a], [o], 's')]`.
2. **Pass 2: Token Offset**: Kiểm tra chỉ số token có vượt quá số từ trong câu không.
3. **Pass 3: Overlap**: Kiểm tra xem Aspect và Opinion có bị trùng đè vị trí lên nhau không.
4. **Pass 4: Border Punctuation**: Kiểm tra rò rỉ dấu câu (`"`, `'`, `,`, `.`, `!`, `?`) ở rìa Aspect/Opinion.
5. **Pass 5: Preposition Leakage**: Kiểm tra giới từ thừa ở đầu Aspect (`ở`, `tại`, `trên`, `trong`, `tới`...).
6. **Pass 6: Polarity Validity**: Chỉ chấp nhận 3 giá trị `POS`, `NEG`, `NEU`.
7. **Pass 7: Out-of-Scope Provinces**: Phát hiện các tỉnh ngoài phạm vi chưa được reject.
8. **Pass 8: Polarity Mismatch**: Kiểm tra các từ mang nghĩa phục hồi (*"nước rút"*, *"khô ráo"*) bị gán nhầm `NEG`.
9. **Pass 9: Fallback Misuse**: Phát hiện câu đã có tên đường cụ thể nhưng lại dùng Fallback `TP. Hồ Chí Minh`.
10. **Pass 10: Bare Noun as Opinion**: Bắt lỗi các danh từ hiện tượng trơ trọi không có tính từ/vị ngữ (*"điểm ngập"*, *"vùng ngập"*, *"mực nước"*).

### 5.2. Công Cụ Sinh Triplet Chuẩn Xác `span_helper.py`
Khi cần tạo hoặc sửa Triplet, **bắt buộc gọi qua `span_helper.py`**:
```python
from scripts.span_helper import make_triplet

# Đầu vào: câu text gốc, cụm Aspect bằng chữ, cụm Opinion bằng chữ, Polarity
trip = make_triplet(
    text="Tại TP. Hồ Chí Minh , đường Nguyễn Văn Quá ngập sâu khiến xe chết máy .",
    asp_phrase="đường Nguyễn Văn Quá",
    opi_phrase="ngập sâu",
    polarity="NEG"
)
# Kết quả trả về triplet số chuẩn xác 100%: ([6, 7, 8, 9], [10, 11], 'NEG')
```
*Tác dụng*: Tự động dò tìm token index, tự động cắt bỏ giới từ thừa, tự động gọt sạch dấu câu ở biên, đảm bảo không bao giờ bị lệch vị trí số từ.

---

## 6. CÔNG VIỆC ĐANG LÀM VÀ HƯỚNG DẪN BẮT TAY LÀM TIẾP (NEXT STEPS RUNBOOK)

### 6.1. Mục tiêu trước mắt: Triển khai Gán nhãn Phase 3 Phần của Hùng
- **Nhiệm vụ tiếp theo**: Thực hiện gán nhãn cho **3.874 records** thuộc Phase 3 của bạn Hùng (tương ứng từ **dòng 6.376 đến dòng 10.249** trong file `data/processed/aste_v2_format/master_10k_triplets.txt`).
- **Tệp đích cần ghi**: `data/validate_label/hung/phase3.txt`.

### 6.2. Quy trình 4 Bước Bắt Buộc Khi Làm Từng Lô
```
[Bước 1: Đọc & Trích xuất]
   ├── Lấy lô 50 - 100 records từ dòng 6.376 trở đi trong master_10k_triplets.txt
   ├── Đọc kỹ toàn bộ ngữ cảnh từng câu văn bản
   └── Xác định Aspect (tên đường/Bình Dương/Vũng Tàu), Opinion, Polarity theo Section V
        ▼
[Bước 2: Chuẩn hóa Span qua span_helper.py]
   └── Sử dụng make_triplet() để tính toán index chính xác, chống rò rỉ dấu câu/giới từ
        ▼
[Bước 3: Chạy Linter Kiểm định deep_10_pass_audit.py]
   └── Chạy kiểm tra tệp đích: Bắt buộc đạt 10/10 PASSES: 0 LỖI
        ▼
[Bước 4: Giải mã ngược audit_index_integrity.py]
   └── Xác nhận 100% token offset khớp chuẩn từ vựng thực tế trước khi chuyển sang lô tiếp theo
```

### 6.3. Sau khi Hoàn tất Toàn bộ Phase 3
1. Ghép nối Master Dataset hoàn chỉnh 10.249 records:
   $$\text{Master 10K} = \text{Phase 1 (Thuận)} + \text{Phase 2 (Thuận)} + \text{Phase 3 (Thuận)} + \text{Phase 3 (Hùng)}$$
2. Chạy tái huấn luyện (Retrain) và đánh giá Benchmark các mô hình ASTE (`PhoBERT`, `BARTpho`, `mT5`) trong thư mục `AI/`.
3. Tích hợp mô hình ASTE tốt nhất vào luồng PySpark streaming thời gian thực (`bigdata/run_streaming_pipeline.py`).

---

## 7. BẢNG TRA CỨU LỆNH NHANH (CHEATSHEET)

Mọi thao tác chạy lệnh trên Windows PowerShell, sử dụng môi trường ảo: `.\.venv\Scripts\python.exe`.

### 7.1. Kiểm định Dữ liệu ASTE
```powershell
# 1. Kiểm định kép 10 vòng độc lập (Bắt buộc đạt 10/10 PASSES: 0 LỖI)
.\.venv\Scripts\python.exe scripts/deep_10_pass_audit.py data/validate_label/thuan/phase3.txt

# 2. Đối soát giải mã ngược token (Bắt buộc 0 lỗi lệch từ)
.\.venv\Scripts\python.exe scripts/audit_index_integrity.py data/validate_label/thuan/phase3.txt

# 3. Xem thống kê nhanh phân bố nhãn
.\.venv\Scripts\python.exe scripts/stats_phase3.py
```

### 7.2. Khởi động Toàn Trình Hệ Thống (End-to-End System)
```powershell
# 1. Khởi động hạ tầng Kafka KRaft & Redis 7.2 (Docker)
docker-compose -f bigdata/docker-compose.yml up -d

# 2. Khởi động Dashboard Web Server (Port 8050)
.\.venv\Scripts\python.exe dashboard/server.py

# 3. Khởi động PySpark Streaming Pipeline (Xử lý micro-batch 5s)
.\.venv\Scripts\python.exe bigdata/run_streaming_pipeline.py

# 4. Khởi động Crawler thu nạp đa nguồn miễn phí
.\.venv\Scripts\python.exe pipeline/live_free_crawler.py
```

### 7.3. Thao tác Git An Toàn
```powershell
# Kiểm tra trạng thái
git status

# Commit và Push lên main
git add -A
git commit -m "feat: <mô tả công việc cụ thể>"
git push origin main
```

---

## 📌 DANH SÁCH TÀI LIỆU QUY CHUẨN ĐỌC THÊM
1. [BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md](file:///D:/SE363_RAWDATA/documents/BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md): **KIM CHỈ NAM QUY TẮC GÁN NHÃN VÀ AUDIT (ĐỌC KỸ TỪ MỤC I ĐẾN MỤC X)**.
2. [PHASE3_RECOVERY_AUDIT_REPORT.md](file:///D:/SE363_RAWDATA/documents/PHASE3_RECOVERY_AUDIT_REPORT.md): Báo cáo chi tiết quá trình rà soát và phục hồi 782 records reject Phase 3 của Thuận.
3. [PHASE2_EVALUATION_COHEN_KAPPA_AND_PHASE3_ALLOCATION.md](file:///D:/SE363_RAWDATA/documents/PHASE2_EVALUATION_COHEN_KAPPA_AND_PHASE3_ALLOCATION.md): Báo cáo đánh giá Cohen's Kappa Phase 2 ($\kappa = 0.88$) và kế hoạch phân công Phase 3.
4. [SYSTEM_ARCHITECTURE_AND_RUNBOOK.md](file:///D:/SE363_RAWDATA/documents/SYSTEM_ARCHITECTURE_AND_RUNBOOK.md): Cẩm nang chi tiết vận hành toàn trình Crawling - Streaming - Dashboard.
5. [UNIFIED_SYSTEM_GUIDE.md](file:///D:/SE363_RAWDATA/documents/UNIFIED_SYSTEM_GUIDE.md): Bản đặc tả kiến trúc học thuật phục vụ bài báo quốc tế (ICWSM/EMNLP).
