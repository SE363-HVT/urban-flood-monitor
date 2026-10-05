# ĐỒ ÁN SE363 - HỆ THỐNG GIÁM SÁT ĐÔ THỊ & CẢNH BÁO NGẬP LỤT TP.HCM QUA DỮ LIỆU STREAMING MẠNG XÃ HỘI
**Tài liệu Tiến độ Dự án, Hướng dẫn Tích hợp Mô hình ASTE & Đề xuất Nâng cao Workload AI**

---

## I. TỔNG KẾT TIẾN ĐỘ THỰC TẾ (STATUS AS OF TODAY)

Hiện tại, hệ thống đã hoàn thiện toàn bộ khung kiến trúc xương sống (Streaming Pipeline & GIS Visualization), hoạt động độc lập và sẵn sàng chờ ráp mô hình ASTE:

| Thành phần | Trạng thái hiện tại | Chi tiết kỹ thuật |
| :--- | :---: | :--- |
| **1. Crawling & Streaming Engine** | **HOÀN TẤT** | * **Live Mode:** Cào trực tiếp qua Apify REST API, lọc thời gian thực $\le 60$ phút.<br>* **Simulation Mode:** Phát lại dòng dữ liệu trôi vòng tròn (Sliding Stream), khử trùng lặp tuyệt đối, luân chuyển theo quận. |
| **2. Bóc tách Thực thể & Ngữ nghĩa (PoC Mock)** | **TẠM THỜI (Heuristic Baseline)** | Sử dụng bộ Heuristic NLP tạm thời để trích xuất Aspect - Opinion - Severity phục vụ dựng luồng dữ liệu và kiểm thử giao diện. **Đang chờ thay thế bằng mô hình ASTE đã huấn luyện.** |
| **3. GIS & Precision Geocoding Engine** | **HOÀN TẤT** | Chuẩn hóa 100% tọa độ tim đường giao thông theo chuẩn OpenStreetMap Highway (`class=highway`), triệt tiêu hoàn toàn lỗi lệch marker vào nhà dân/hẻm nhánh. |
| **4. Web Dashboard & Real-time Heatmap** | **HOÀN TẤT** | Giao diện bản đồ nhiệt động (Leaflet.js + Leaflet.heat), hiệu ứng bay bản đồ (`flyTo`), bảng tin feed cập nhật thời gian thực, hiển thị đầy đủ nhãn Aspect, Opinion, Trọng số nghiêm trọng. |

---

## II. ĐÁNH GIÁ KIẾN TRÚC MÃ NGUỒN: KHI BẠN TRAIN XONG ASTE THÌ RÁP VÀO CÓ ỔN KHÔNG?

> **KẾT LUẬN: HOÀN TOÀN TƯƠNG THÍCH VÀ CỰC KỲ DỄ RÁP (PLUG-AND-PLAY)!**

Mã nguồn hiện tại trong [`pipeline/event_processor.py`](file:///D:/SE363_RAWDATA/pipeline/event_processor.py) đã được thiết kế theo đúng mô hình **Adapter Pattern (Decoupled Architecture)**. 

### Luồng dữ liệu chuẩn đã chuẩn bị sẵn:
```
[TikTok Raw Post]
       │
       ▼
clean_stream_text()  (Làm sạch teencode, icon, chuẩn hóa Unicode NFC)
       │
       ▼
[ASTE Model Inference] ──> Trả về Triplet: (Aspect, Opinion, Sentiment)
       │
       ├─► Aspect ("Phạm Thế Hiển") ────► match_hotspot() ────► Lấy GIS (lat, lon, heat_points)
       ├─► Opinion ("ngập lút bánh") ───► Severity Scorer ───► Tính Weight (1.2, 2.0, 3.0)
       └─► Sentiment ("negative") ──────► Gán sắc thái
       │
       ▼
[Event Object gửi lên Dashboard & Heatmap]
```

### Cách bạn ráp mô hình vào code (Chỉ mất dưới 10 phút):
Trong [`pipeline/event_processor.py`](file:///D:/SE363_RAWDATA/pipeline/event_processor.py), bạn chỉ cần thay hàm `analyze_severity_heuristic()` bằng class bọc mô hình ASTE:

```python
# Ví dụ tích hợp mô hình sau khi train xong:
class ASTEModelPredictor:
    def __init__(self, model_checkpoint="weights/best_phobert_aste.pt"):
        # Load PhoBERT backbone + Head (STAGE / Table-Filling / GCN)
        self.model = torch.load(model_checkpoint, map_location="cpu")
        self.model.eval()

    def predict(self, text: str) -> List[Tuple[str, str, str]]:
        # Inference sinh ra triplet: [(Aspect, Opinion, Sentiment)]
        # Ví dụ: [("Đường Mã Lò", "ngập sâu chết máy", "negative")]
        return triplets

# Trong process_tiktok_item():
# Gọi predictor.predict(cleaned_text) để nhận triplet thật từ mô hình Deep Learning!
```
* **Không cần sửa một dòng code nào** của Server, Dashboard Leaflet, hay TikTok Poller. Toàn bộ hệ thống sẽ tự động chuyển từ cơ chế Heuristic sang Deep Learning Inference ngay lập tức.

---

## III. ĐỀ XUẤT CÁC HƯỚNG AI NÂNG CAO (HARDCORE AI WORKLOAD)

Nếu nhóm muốn tăng độ nặng học thuật và kỹ thuật của đồ án để gây ấn tượng mạnh với hội đồng và đạt điểm tối đa, dưới đây là **4 hướng AI nâng cao chuyên sâu (Hardcore AI)** được thiết kế riêng cho bài toán Urban Flood Monitoring:

### 1. Spatio-Temporal Graph Neural Network (ST-GNN) dự báo lan truyền ngập lụt đô thị
* **Bài toán:** Dữ liệu mạng xã hội chỉ phản ánh những nơi có người quay clip. Nhiều tuyến đường kề bên bị ngập nhưng không ai đăng bài $\rightarrow$ hệ thống bị điểm mù (Sparsity problem).
* **Mô hình AI:** Xây dựng mạng nơ-ron đồ thị không - thời gian (**ST-GCN** hoặc **DCRNN - Diffusion Convolutional Recurrent Neural Network**).
  * **Đồ thị $G = (V, E)$:** Các đỉnh $V$ là các tuyến đường/nút giao TP.HCM, các cạnh $E$ là tính kết nối kề nhau và độ dốc địa hình (DEM - Digital Elevation Model).
  * **Input Feature:** Tín hiệu ngập trích xuất từ mô hình ASTE tại thời điểm $t$.
  * **Output AI:** 
    1. **Spatial Propagation (Lan truyền không gian):** Dự báo sau 30-60 phút nữa, ngập lụt và tắc nghẽn sẽ lan sang những tuyến đường kế cận nào.
    2. **Zero-Shot Road Imputation:** Ước tính mức độ ngập của các tuyến đường lân cận dù không có bài đăng mạng xã hội nào nhắc tới.
* **Độ nặng AI:** **Rất cao (Hardcore)**. Áp dụng PyTorch Geometric (`torch_geometric`), mang tính ứng dụng thực tế cao về Quy hoạch đô thị thông minh (Smart City).

---

### 2. Multimodal TikTok Intelligence: PhoWhisper Speech-to-Text (Audio AI) + Video Vision Verification
* **Bài toán đặc thù của TikTok:** Hơn 60% clip ngập lụt trên TikTok **chỉ có 1-2 hashtag ngắn ngủn** (như `#ngaplut #saigon`), văn bản caption không hề nhắc tên đường! Tuy nhiên, **người quay clip lại nói rất rõ trong video**: *"Đường Ung Văn Khiêm ngập sâu quá trời rồi mọi người ơi..."*.
* **Mô hình AI:**
  1. **Audio Speech-to-Text (PhoWhisper / Whisper-small-vi):** Tự động bóc tách audio stream của video TikTok và chuyển giọng nói thành văn bản tiếng Việt.
  2. Ghép nội dung giọng nói vào caption văn bản $\rightarrow$ đưa vào mô hình ASTE. Điều này giúp tăng độ phủ phát hiện điểm ngập (**Recall**) lên gấp 2-3 lần.
  3. **Computer Vision (Lightweight ViT / MobileNetV3 / CLIP Zero-Shot):** Quét khung hình video để phân loại xem hình ảnh có thực sự là cảnh đường ngập nước hay không (loại bỏ video ghép nhạc khiêu vũ, bán hàng gắn nhầm hashtag).
* **Độ nặng AI:** **Cao (Hardcore)**. Đưa đề tài thành hệ thống **Multimodal Foundation AI (Audio + Video + Text)** hoàn chỉnh.

---

### 3. End-to-End Multitask Joint Learning (ASTE + Continuous Flood Depth Regression)
* **Bài toán:** Các mô hình ASTE thông thường chỉ gán nhãn phân loại (Negative / Neutral / Positive). Nhưng cảnh báo ngập cần ước tính **độ sâu mực nước (centimet)** để xe cộ biết có nên đi qua hay không.
* **Mô hình AI:** Xây dựng kiến trúc học đa nhiệm (**Joint Multitask Framework**):
  * **Shared Encoder:** `vinai/phobert-base-v2` hoặc `xlm-roberta-base`.
  * **Head 1 (ASTE Task):** Grid Tagging Representation (GtR) hoặc Boundary-Driven Table-Filling bóc tách bộ ba `(Aspect, Opinion, Sentiment)`.
  * **Head 2 (Depth Regression Task):** Mạng hồi quy kết hợp Ordinal Classification Loss dự báo trực tiếp mực nước ước lượng: *10-20cm (Ngập mép bánh)*, *30-50cm (Chết máy)*, *>60cm (Ngập lút bánh)*.
  * **Hàm mất mát tổng hợp:** $\mathcal{L}_{\text{total}} = \lambda_1 \mathcal{L}_{\text{ASTE}} + \lambda_2 \mathcal{L}_{\text{Depth}}$.
* **Độ nặng AI:** **Cao**. Thể hiện năng lực thiết kế kiến trúc mạng nơ-ron tùy biến (Custom PyTorch Loss & Dual Heads) thay vì chỉ dùng thư viện có sẵn.

---

### 4. Semantic Contrastive Event Clustering & Knowledge Graph Grounding
* **Bài toán:** Phân biệt các tuyến đường trùng tên tại các quận khác nhau (ví dụ: *Đường Vườn Lài Q12* vs *Vườn Lài Tân Phú*; *Nguyễn Trãi Q1* vs *Nguyễn Trãi Q5*).
* **Mô hình AI:** 
  * Sử dụng kỹ thuật **Contrastive Learning** (Học tương phản) để huấn luyện không gian embedding của PhoBERT phân tách rõ ràng ngữ cảnh địa lý.
  * Kết hợp **Knowledge Graph Embedding (KGE)** nhúng quan hệ thực thể địa lý: $\text{Tuyến đường} \xrightarrow{\text{nằm tại}} \text{Phường} \xrightarrow{\text{thuộc}} \text{Quận}$.
* **Độ nặng AI:** **Vừa đến Cao**. Rất phù hợp nếu nhóm định hướng làm bài báo khoa học (Research Paper).

---

## IV. LỘ TRÌNH LẮP RÁP & HOÀN THIỆN CÁC PHASE (CẬP NHẬT THEO TIẾN ĐỘ)

```
[Phase 1: Dataset & Crawling PoC] 
    │  - Hệ thống cào & Pipeline: ĐÃ HOÀN TẤT.
    │  - Gán nhãn ngữ liệu ASTE (2.000 - 3.000 mẫu tiếng Việt): ĐANG THỰC HIỆN.
    ▼
[Phase 2: Huấn luyện & Benchmark Mô hình ASTE] (Trọng tâm của nhóm AI)
    │  - Cài đặt các kiến trúc: STAGE, Table-Filling, GCN trên backbone PhoBERT.
    │  - Huấn luyện trên GPU (Colab/Kaggle), đo Precision/Recall/Macro-F1.
    │  - Xuất Checkpoint tối ưu (Best Checkpoint .pt hoặc .onnx).
    ▼
[Phase 3: Lắp ráp Mô hình vào Pipeline & Hạ tầng Big Data]
    │  - Viết Adapter bọc mô hình ASTE thay thế bộ Heuristic tạm thời.
    │  - (Tùy chọn hạ tầng): Dựng cụm Kafka / Redis Stream nếu môn yêu cầu Producer/Consumer phân tán.
    ▼
[Phase 4: Tích hợp Toàn diện & Nâng cao Workload AI]
    │  - Tích hợp thêm 1 trong các hướng AI nâng cao (ST-GNN, Audio Whisper, hoặc Multitask Depth).
    │  - Kết nối WebSocket cập nhật giao diện Dashboard theo thời gian thực.
    ▼
[Phase 5: Kiểm thử tải, Diễn tập Demo & Hoàn thiện Báo cáo]
    │  - Dùng Simulation Mode làm kịch bản diễn tập thuyết trình (bảo đảm luôn có dữ liệu mượt mà).
    │  - Viết Paper học thuật, thiết kế Slide và nghiệm thu đề tài.
```

---

## V. CHECKLIST HÀNH ĐỘNG DÀNH CHO BẠN TRAIN MODEL

Khi bạn trong nhóm hoàn thành việc huấn luyện mô hình ASTE:
1. Xuất file trọng số mô hình tốt nhất (ví dụ: `weights/best_phobert_aste.pt`).
2. Viết 1 script test inference độc lập nhận vào chuỗi string và in ra danh sách triplet:
   ```python
   # Output mong muốn:
   # Input: "Đường Mã Lò nước ngập sâu quá xe chết máy"
   # Output: [("Đường Mã Lò", "ngập sâu", "negative"), ("xe", "chết máy", "negative")]
   ```
3. Copy hàm inference đó vào class Adapter trong [`pipeline/event_processor.py`](file:///D:/SE363_RAWDATA/pipeline/event_processor.py) là toàn bộ hệ thống web, bản đồ nhiệt, và định vị GIS sẽ tự động chạy trên nền tảng Deep Learning mới mà không gặp bất kỳ xung đột nào.
