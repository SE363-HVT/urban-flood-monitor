# 📂 Giải Thích Chi Tiết Thư Mục `RadiNet/data` (Dễ Hiểu Nhất)
## Hướng Dẫn Toàn Diện Về Dữ Liệu Ngập Lụt Đô Thị TP.HCM

> **Mục tiêu tài liệu**: Giải thích rõ ràng, trực quan chức năng, nguồn gốc và cách sử dụng của **từng file và thư mục con** bên trong [`RadiNet/data`](file:///home/counting/Workspaces/ryan/RadiNet/data) dành cho cả nhà nghiên cứu AI lẫn lập trình viên hệ thống.

---

## 🗺️ Bản Đồ Cấu Trúc Tổng Thể

Thư mục `RadiNet/data` được chia làm **5 nhóm dữ liệu chính**:

```text
RadiNet/data/
├── 🏛️ 1. CƠ SỞ DỮ LIỆU ĐỊA LÝ & TỌA ĐỘ GPS (GIS Knowledge Base)
│   ├── csgt_122_flood_hotspots.json        # 122 điểm ngập chuẩn của CSGT TP.HCM (Tọa độ thật 100%)
│   ├── hcmc_168_administrative_units.json  # 168 Phường/Xã mới theo Nghị quyết 1685 (UBTVQH)
│   ├── osm_geocoded_csgt.json              # Tọa độ tim đường OpenStreetMap đối soát 122 điểm CSGT
│   └── gazetteer_dynamic_cache.json        # Bộ nhớ tự học tọa độ các đường mới từ OpenStreetMap
│
├── 🧠 2. DỮ LIỆU HUẤN LUYỆN AI ĐÃ GÁN NHÃN (Processed ASTE Benchmark)
│   └── processed/
│       ├── hcmc_flood_annotated_v2_multimodal.json # BỘ DỮ LIỆU CHÍNH: 3.922 mẫu & 5.483 bộ ba ASTE
│       ├── hcmc_flood_annotated_v1.json            # Bản v1 cơ sở ban đầu (dùng cho huấn luyện cũ)
│       ├── aste_dataset_metrics.json               # Số liệu thống kê phân phối nhãn học thuật
│       ├── ASTE_DATASET_REPORT.md                  # Báo cáo tổng hợp chất lượng dữ liệu
│       └── DATASET_GUIDE.md                        # Hướng dẫn chi tiết cấu trúc JSON & Metadata
│
├── ⚡ 3. BỘ ĐỆM DỮ LIỆU REAL-TIME & TRẠNG THÁI PIPELINE
│   ├── last_crawled_tiktok.json            # 249 video TikTok mới nhất cào về gần đây
│   ├── last_crawled_facebook.json          # 12 bài đăng Facebook mới nhất cào về gần đây
│   ├── real_facebook_flood_pool.json       # 29 bài đăng Facebook thực tế chọn lọc (phục vụ mô phỏng)
│   ├── crawl_csgt_audit.json               # 1.183 bản ghi nhật ký kiểm định dữ liệu cào
│   └── pipeline_state.json                 # Trạng thái chống trùng lặp bài viết (seen_ids, watermark)
│
├── 📦 4. DỮ LIỆU NGUYÊN BẢN CHƯA QUA XỬ LÝ (Raw Crawled Data)
│   └── raw/
│       ├── dataset_google_news_full.json   # Dữ liệu thô cào từ Google News (báo chí)
│       ├── dataset_free-tiktok-scraper_*.json # Các file thô cào từ TikTok
│       ├── dataset_facebook-search-scraper_*.json # Các file thô cào từ Facebook Search
│       └── episodes/                       # Phân loại dữ liệu thô theo 7 đợt ngập lịch sử
│
└── 🎥 5. TÀI NGUYÊN MULTIMODAL (Video & Audio)
    ├── audio_sample/                       # Các file video/audio mẫu (.mp4, .wav)
    └── extracted_frames/                   # Frame hình ảnh & audio 16kHz đã bóc tách phục vụ AI
```

---

## 🏛️ NHÓM 1: Cơ Sở Dữ Liệu Địa Lý & Tọa Độ GPS (GIS Knowledge Base)

Nhóm này chứa toàn bộ tri thức về bản đồ, tên đường và tọa độ kinh/vĩ độ (`lat`, `lon`) của TP.HCM. **Hệ thống không bao giờ gieo tọa độ ngẫu nhiên**, mà lấy trực tiếp từ các file này:

### 1. `csgt_122_flood_hotspots.json` (109 KB - 122 bản ghi)
- **Đây là gì?**: Danh mục 122 "điểm đen" ngập nước do **Phòng Cảnh sát Giao thông Công an TP.HCM (PC08)** công bố chính thức (gồm 83 điểm do mưa và 39 điểm do triều cường).
- **Nội dung bên trong**: Tên đường, đoạn đường chính xác (ví dụ: *"Từ Huỳnh Tấn Phát đến Lâm Văn Bền"*), Phường, Quận, và **tọa độ GPS tim đường chuẩn 5 chữ số thập phân** (độ chính xác $\approx 1.1\text{m}$).
- **Hệ thống dùng làm gì?**: Khi người dân đăng *"Đường Trần Xuân Soạn ngập lút bánh"*, hệ thống tìm thấy ngay tọa độ `lat: 10.75105, lon: 106.71451` để cắm cờ đỏ cảnh báo lên bản đồ.

### 2. `hcmc_168_administrative_units.json` (148 KB - 168 bản ghi)
- **Đây là gì?**: Danh mục 168 Đơn vị hành chính (Phường/Xã/Thị trấn) của TP.HCM đã được cập nhật **chuẩn hóa theo Nghị quyết số 1685/NQ-UBTVQH15** (mô hình sáp nhập mới nhất).
- **Nội dung bên trong**: Tên phường mới, thuộc cụm quận nào, từ khóa nhận diện và tọa độ trung tâm (centroid) của phường.
- **Hệ thống dùng làm gì?**: Khi bài viết chỉ nói chung chung *"Phường Thảo Điền ngập nặng"* mà không nói tên đường cụ thể, hệ thống dùng file này để định vị vị trí phường trên bản đồ.

### 3. `osm_geocoded_csgt.json` (27 KB - 122 bản ghi)
- **Đây là gì?**: File đối soát chéo tọa độ của 122 điểm CSGT được truy vấn tự động từ máy chủ bản đồ toàn cầu **OpenStreetMap (OSM)**.
- **Nội dung bên trong**: Mã định danh CSGT gắn với tên đối tượng đường chuẩn trong OpenStreetMap.
- **Hệ thống dùng làm gì?**: Đảm bảo marker luôn rơi đúng vào tim đường nhựa (highway centerline), không bao giờ bị lệch sang nóc nhà dân hay bờ sông.

### 4. `gazetteer_dynamic_cache.json` (44 KB - 110 bản ghi)
- **Đây là gì?**: **Bộ nhớ đệm tự học (Self-Learning Cache)** của hệ thống.
- **Cơ chế hoạt động**: Khi người dân nhắc đến một tuyến đường mới toanh chưa có trong danh mục 122 điểm (ví dụ: *"Đường Lê Văn Quới"*, *"Đường Mã Lò"*), hệ thống tự động gọi API OpenStreetMap để lấy tọa độ, sau đó lưu ngay vào file này. Lần sau gặp lại đường đó, hệ thống đọc từ cache ra ngay trong 0.001 giây mà không cần lên mạng hỏi lại.

---

## 🧠 NHÓM 2: Dữ Liệu Huấn Luyện AI Đã Gán Nhãn (`processed/`)

Đây là "trái tim" dữ liệu phục vụ huấn luyện mô hình Trích xuất bộ ba khía cạnh cảm xúc ngập lụt (Generative ASTE):

### 1. `hcmc_flood_annotated_v2_multimodal.json` (5.9 MB - 3.922 bản ghi)
- **ĐÂY LÀ FILE QUAN TRỌNG NHẤT CỦA DỰ ÁN**.
- **Nội dung**: Gồm 3.922 câu văn thực tế từ báo chí, Facebook và TikTok, đi kèm **5.483 bộ ba nhãn ASTE**:
  - `aspect`: Đối tượng bị ngập (Tên đường, phương tiện giao thông, khu vực ngập...).
  - `opinion`: Biểu hiện ngập (ngập sâu cản trở giao thông, xe chết máy dắt bộ, triều cường dâng cao...).
  - `polarity`: Thái độ cảm xúc (`NEGATIVE` - bức xúc/nguy hiểm; `NEUTRAL` - đo đạc thông báo; `POSITIVE` - nước đã rút hết/khen).
- **Metadata đi kèm**: Gắn cờ có video/ảnh hay không (`media.has_media`), thuộc đợt ngập nào (`episode_id`), nền tảng nào (`news`, `facebook`, `tiktok`).

### 2. `hcmc_flood_annotated_v1.json` (5.9 MB)
- **Đây là gì?**: Phiên bản sơ khởi tiền đề (v1) trước khi được làm giàu thêm các trường multimodal của v2. Hiện tại đã được nâng cấp đồng bộ với v2.

### 3. `aste_dataset_metrics.json` & `ASTE_DATASET_REPORT.md`
- **Đây là gì?**: File số liệu tổng hợp (JSON) và Báo cáo tóm tắt (Markdown) về các chỉ số học thuật: độ dài câu trung bình, tỷ lệ mất cân bằng nhãn (`NEG`: 94.2%, `NEU`: 5.5%, `POS`: 0.3%), mật độ bộ ba trên mỗi câu.

### 4. `DATASET_GUIDE.md`
- **Đây là gì?**: Bản hướng dẫn chi tiết quy ước định dạng từng trường trong file JSON (`content`, `location`, `aste_triplets`, `source`).

---

## ⚡ NHÓM 3: Bộ Đệm Dữ Liệu Real-Time & Trạng Thái Pipeline

Nhóm này phục vụ luồng vận hành trực tiếp (live streaming pipeline) và giao diện Web Dashboard:

### 1. `last_crawled_tiktok.json` (1.3 MB - 249 bài)
- **Đây là gì?**: Bản chụp dữ liệu các video TikTok ngập lụt TP.HCM mới nhất do crawler cào về.
- **Chứa gì?**: Caption bài đăng, ID tác giả, link video gốc, lượt xem, lượt tim, danh sách hashtag `#ngaptphcm`, `#trieucuong`.

### 2. `last_crawled_facebook.json` (36 KB - 12 bài)
- **Đây là gì?**: Các bài đăng giao thông mới nhất cào từ các Fanpage/Group Facebook về tình hình ngập lụt.

### 3. `real_facebook_flood_pool.json` (159 KB - 29 bài)
- **Đây là gì?**: Tập hợp 29 bài viết Facebook thực tế tiêu biểu đã được lọc sạch spam BĐS.
- **Hệ thống dùng làm gì?**: Dùng cho chế độ **chạy mô phỏng (Simulation Mode)** khi bạn chạy `python run_pipeline_test.py --mode simulation`. Chế độ này giúp bạn kiểm thử bản đồ nhiệt mà không tốn tiền mua gói cào mạng xã hội.

### 4. `pipeline_state.json` (1.2 KB)
- **Đây là gì?**: File "sổ nhớ" ghi lại trạng thái của hệ thống streaming.
- **Nội dung**: Lưu danh sách các bài viết đã xử lý (`seen_ids`) và mốc thời gian gần nhất (`watermark`). Nhờ file này, hệ thống không bao giờ xử lý lại một bài viết 2 lần, tránh tạo ra cảnh báo giả trùng lặp.

### 5. `crawl_csgt_audit.json` (446 KB - 1.183 bản ghi)
- **Đây là gì?**: Nhật ký đối soát dữ liệu cào: ghi lại những bài viết nào đã được gắn đúng điểm CSGT, bài nào bị loại do rác hoặc ngoài địa bàn TP.HCM.

---

## 📦 NHÓM 4: Dữ Liệu Thô Chưa Qua Xử Lý (`raw/`)

Thư mục này chứa dữ liệu gốc "như lúc vừa tải về từ Internet", chưa được làm sạch hay gán nhãn:

### 1. Các file thô ở gốc `raw/`:
- `dataset_google_news_full.json` (818 KB): Dữ liệu bài báo thô từ Google News RSS.
- `dataset_free-tiktok-scraper_*.json`: Các gói dữ liệu thô cào từ TikTok qua công cụ Apify.
- `dataset_facebook-search-scraper_*.json`: Các gói dữ liệu thô cào từ Facebook qua từ khóa tìm kiếm.

### 2. Thư mục `raw/episodes/` (Phân chia theo 7 đợt ngập thực tế):
Dữ liệu thô được gom nhóm khoa học vào 7 thư mục con đại diện cho các đợt mưa bão và triều cường lớn tại TP.HCM:
1. `episode_01_2026-09-10_mua-giong-dau-thang-9/`: Đợt mưa lớn đầu tháng 9.
2. `episode_02_2026-09-17_anh-huong-bao-so-4/`: Đợt hoàn lưu bão số 4 (Soulik).
3. `episode_03_2026-09-27_trieu-cuong-dinh-diem-cuoi-thang-9/`: Đợt triều cường đỉnh điểm cuối tháng 9.
4. `episode_04_2026-10-01_trieu-cuong-ram-thang-tam/`: Đợt triều cường Rằm tháng Tám.
5. `episode_05_2026-10-07_mua-giong-chieu-toi-cuc-bo/`: Đợt mưa giông chiều tối đầu tháng 10.
6. `historical_archive/`: Kho bài báo lưu trữ từ các năm trước (2018–2025).
7. `sporadic_flood_events/`: Các đợt ngập cục bộ rải rác.

---

## 🎥 NHÓM 5: Tài Nguyên Multimodal (Video & Audio)

Nhóm dữ liệu phục vụ nghiên cứu đa phương thức (Vision-Language & Audio ASR):

### 1. `audio_sample/`
- Chứa các file mẫu video và audio thực tế: `sample_0.mp4`, `sample_0.wav`, `sample_1.mp4`, `sample_1.wav`, `sample_2.mp4`, `sample_2.wav`.
- Dùng để kiểm thử nhanh mô hình nhận diện giọng nói (Whisper) hoặc kiểm tra luồng phân tách âm thanh.

### 2. `extracted_frames/`
- Thư mục đầu ra của công cụ [`RadiNet/scripts/extract_tiktok_frames.py`](file:///home/counting/Workspaces/ryan/RadiNet/scripts/extract_tiktok_frames.py).
- Chứa các ảnh trích xuất (keyframe) với tần suất 1 ảnh / 2 giây và audio chuẩn 16kHz mono phục vụ đưa vào mạng nơ-ron tích chập (CNN) hoặc Vision Transformer (ViT).

---

## 💡 Bảng Tra Cứu Nhanh: "Khi Cần Làm Gì Thì Dùng File Nào?"

| Nhu Cầu Của Bạn | File Cần Dùng | Ghi Chú |
| :--- | :--- | :--- |
| **Huấn luyện mô hình AI (ASTE)** | [`data/processed/hcmc_flood_annotated_v2_multimodal.json`](file:///home/counting/Workspaces/ryan/RadiNet/data/processed/hcmc_flood_annotated_v2_multimodal.json) hoặc các file trong `finetune/data/` | Đã gán nhãn chuẩn 100% |
| **Tra cứu tọa độ GPS của 1 tuyến đường** | [`data/csgt_122_flood_hotspots.json`](file:///home/counting/Workspaces/ryan/RadiNet/data/csgt_122_flood_hotspots.json) & [`data/gazetteer_dynamic_cache.json`](file:///home/counting/Workspaces/ryan/RadiNet/data/gazetteer_dynamic_cache.json) | Tọa độ chuẩn 5 chữ số thập phân |
| **Tra cứu danh sách Phường/Xã mới** | [`data/hcmc_168_administrative_units.json`](file:///home/counting/Workspaces/ryan/RadiNet/data/hcmc_168_administrative_units.json) | Cập nhật theo NQ 1685 |
| **Chạy thử giao diện bản đồ nhiệt (offline)** | [`data/real_facebook_flood_pool.json`](file:///home/counting/Workspaces/ryan/RadiNet/data/real_facebook_flood_pool.json) | Chạy qua lệnh `python run_pipeline_test.py --mode simulation` |
| **Xem dữ liệu cào mới nhất từ mạng xã hội** | [`data/last_crawled_tiktok.json`](file:///home/counting/Workspaces/ryan/RadiNet/data/last_crawled_tiktok.json) & [`data/last_crawled_facebook.json`](file:///home/counting/Workspaces/ryan/RadiNet/data/last_crawled_facebook.json) | Dữ liệu thô cập nhật theo phiên cào |
| **Bóc tách video thành hình ảnh để đưa vào AI** | Chạy script [`scripts/extract_tiktok_frames.py`](file:///home/counting/Workspaces/ryan/RadiNet/scripts/extract_tiktok_frames.py) | Xuất kết quả vào `data/extracted_frames/` |
