# BÀI TOÁN XÁC THỰC DỮ LIỆU & PHÒNG CHỐNG TIN GIẢ TRÊN MẠNG XÃ HỘI
**Đề tài SE363: Giám sát Đô thị & Cảnh báo Ngập lụt qua Dữ liệu TikTok Streaming**

---

## I. ĐẶT VẤN ĐỀ (PROBLEM STATEMENT)

Dữ liệu mạng xã hội (Social Sensing / Crowd-sourced Data) có ưu điểm vượt trội về tính tức thời và độ phủ rộng khắp đô thị. Tuy nhiên, nó mang bản chất tự do, không kiểm duyệt, dẫn đến nguy cơ xuất hiện các nội dung sai lệch, gây nhiễu loạn cho hệ thống cảnh báo giao thông.

### 4 Kịch bản "Nói xạo / Tin giả" điển hình:
1. **Cố tình tung tin thất thiệt (Trolling / Prank):** Người dùng đăng status hoặc video cố tình khẳng định một tuyến đường nào đó đang ngập sâu, kẹt xe vào một ngày nắng ráo nhằm đùa cợt hoặc câu tương tác.
2. **Tái sử dụng video cũ (Recycled / Stale Videos):** Lấy lại các clip ngập lụt kinh hoàng từ những năm trước (2022, 2023) đăng lại vào ngày hôm nay để "câu view", trong khi hiện tại ngoài đường khô ráo.
3. **Nói mỉa mai, châm biếm (Sarcasm / Irony / Humor):** Người dùng dùng từ ngữ tích cực/phóng đại để trêu đùa: *"Nắng đẹp quá, chuẩn bị đem xuồng ra bơi trên đường Nguyễn Huệ thôi mọi người"*.
4. **Gắn thẻ rác (Spam Hashtags):** Video nội dung nhảy nhót, bán hàng rong nhưng lại gắn hàng loạt hashtag hot `#ngaplut #muasaigon` để ké đề xuất.

> **Hạn chế nếu chỉ dùng NLP câu chữ thuần túy:** 
> Mô hình NLP (kể cả ASTE hay PhoBERT) chỉ đọc hiểu câu chữ trong văn bản. Nếu bài đăng viết: *"Đường Nguyễn Huệ đang ngập lụt xe chết máy"*, mô hình vẫn sẽ bóc tách đúng bộ ba *(Nguyễn Huệ, ngập lụt, Negative)*. Do đó, **nếu chỉ tin vào 1 câu text đơn lẻ, hệ thống chắc chắn sẽ bị đánh lừa.**

---

## II. KIẾN TRÚC PHÒNG VỆ ĐA TẦNG (MULTI-TIER VERIFICATION ARCHITECTURE)

Để giải quyết triệt để vấn đề này trong các buổi làm việc tiếp theo, nhóm sẽ nghiên cứu và tích hợp mô hình **Xác thực Đa tầng (Multi-tier Defense)**:

```
[TikTok Post Input]
         │
         ▼
[Tầng 1: NLP Sarcasm & Spam Filter] ────(Loại bỏ câu châm biếm, hashtag rác)
         │
         ▼
[Tầng 2: Đối soát Khí tượng Thời gian thực] ──(Lượng mưa trạm đo & Đỉnh triều cường)
         │
         ▼
[Tầng 3: Đồng thuận Không - Thời gian] ───(Gom cụm nhiều người đăng cùng lúc)
         │
         ▼
[Tính Điểm Tin Cậy (Confidence Score)]
  ├── C < 50%: Bỏ qua / Gắn cờ Unverified (Mờ nhạt trên bản đồ)
  ├── 50% <= C < 80%: Điểm nóng Nghi vấn (Cảnh báo thăm dò)
  └── C >= 80%: Điểm nóng Xác thực (Confirmed Flood Alert - Đỏ rực)
```

---

### 1. Tầng 1: Thuật toán Đồng thuận Đa nguồn Không - Thời gian (Spatio-Temporal Consensus)
* **Nguyên lý cốt lõi:** Ngập lụt là hiện tượng tự nhiên cục bộ nhưng diện rộng. Một điểm ngập thật sự không bao giờ chỉ có duy nhất 1 người quay clip.
* **Cơ chế hoạt động:**
  * Gom cụm bài đăng trong cùng khung thời gian $\Delta t = 30\text{ phút}$ và bán kính không gian $R = 500\text{m}$.
  * **Công thức tính điểm đồng thuận ($S_{\text{consensus}}$):**
    $$S_{\text{consensus}} = 1 - e^{-\alpha \cdot (N - 1)}$$
    *(với $N$ là số lượng tài khoản độc lập cùng báo cáo điểm ngập, $\alpha \approx 0.5$)*
  * **Quy tắc phân loại:**
    * **$N = 1$ bài đăng:** $S_{\text{consensus}} = 0$. Gán trạng thái `🟡 Nghi vấn / Chưa kiểm chứng` (chỉ hiển thị chấm nhỏ mờ hoặc icon dấu `?`, không kích hoạt quầng nhiệt cảnh báo diện rộng).
    * **$N \ge 3$ bài đăng:** $S_{\text{consensus}} \ge 0.63$. Gộp thành **Cụm sự kiện (Incident Cluster)** $\rightarrow$ kích hoạt cảnh báo đỏ rực `🔴 Đã xác thực (Confirmed)`.
* **Kết quả:** Nếu 1 kẻ cố tình đăng clip giả mạo, tin đó sẽ nằm cô lập một mình ở mức nghi vấn và tự động hết hạn, biến mất khỏi bản đồ sau 60 phút mà không gây hoang mang.

---

### 2. Tầng 2: Đối soát Dữ liệu Khí tượng Khách quan (Weather & Tidal Ground-Truth Cross-Check)
* **Nguyên lý:** Lấy dữ liệu trạm quan trắc khách quan để kiểm chứng điều kiện cần (Physical Feasibility).
* **Nguồn dữ liệu:** API thời tiết mở miễn phí (Open-Meteo hoặc OpenWeatherMap) theo tọa độ TP.HCM và Lịch thủy triều trạm Phú An / Nhà Bè.
* **Ma trận đối soát logic:**
  | Tình trạng Khí quyển thực tế | Dữ liệu Mạng xã hội | Kết luận của Hệ thống |
  | :--- | :--- | :--- |
  | Trời nắng ráo 6h qua, Lượng mưa = 0mm, Không triều cường | Video báo "Ngập sâu 50cm" | **GẮN CỜ TIN GIẢ / CLIP CŨ (99% Fake)** $\rightarrow$ Chặn không đưa lên bản đồ. |
  | Mưa giông to $\ge 30\text{ mm/h}$ | Video báo "Ngập sâu chết máy" | **HỢP LÝ CAO (+30% Confidence)** $\rightarrow$ Đẩy nhanh tiến độ kích hoạt. |
  | Đang giờ đỉnh triều cường ($> 1.6\text{m}$) | Video báo "Nước tràn bờ kè Q7, Q8" | **HỢP LÝ CAO (+35% Confidence)** $\rightarrow$ Xác nhận triều ngập. |

---

### 3. Tầng 3: Computer Vision & Metadata Verification (Ảnh/Video)
* **Phát hiện clip cũ:**
  * Phân tích ánh sáng khung hình (Scene Lighting): Nếu người đăng nói ngập lúc 19h tối mà hình ảnh thumbnail lại là trời trưa nắng chói chang $\rightarrow$ Phát hiện mâu thuẫn thời gian.
  * So khớp hàm băm ảnh (Perceptual Hashing / Image Hash): Lưu hash các clip ngập nổi tiếng trên mạng; nếu một clip xuất hiện lại sau nhiều tháng với nội dung giống hệt $\rightarrow$ Gắn nhãn `Recycled Video`.

---

### 4. Tầng 4: Bộ lọc Châm biếm (Sarcasm & Irony Detection)
* Xây dựng bộ quy tắc hoặc nhãn phụ trong PhoBERT để phát hiện các mẫu câu đùa cợt:
  * Từ khóa tương phản tiêu cực - tích cực: *"nắng vỡ đầu mà bơi"*, *"trời đẹp ghê... ngập tới nóc"*, *"chèo thuyền đi làm"*.
  * Tự động hạ trọng số nghiêm trọng về `0` cho các câu nói giỡn mang tính giải trí.

---

## III. KẾ HOẠCH HÀNH ĐỘNG CHO BUỔI LÀM VIỆC TIẾP THEO

Khi quay lại giải quyết bài toán này, nhóm sẽ thực hiện các bước sau:

1. [ ] **Thêm trường `confidence` vào mô hình dữ liệu sự kiện:**
   * Mỗi sự kiện trong `event_processor.py` sẽ có thêm trường:
     ```json
     "confidence": 0.85,
     "verification_status": "confirmed", // "unverified" | "suspect" | "confirmed"
     "evidence_count": 3
     ```
2. [ ] **Viết module `weather_validator.py`:**
   * Tích hợp gọi API Open-Meteo để lấy `hourly.precipitation` tại TP.HCM.
   * Viết hàm kiểm tra: `is_weather_plausible(timestamp, location)`.
3. [ ] **Nâng cấp Dashboard hiển thị trực quan:**
   * Điểm chưa xác thực: Icon màu vàng cam kèm nhãn `[Chờ xác minh]`.
   * Điểm đã đồng thuận: Quầng nhiệt đỏ rực kèm số lượng bài đăng đồng thuận (ví dụ: `Đã có 4 video xác nhận`).
4. [ ] **Soạn sẵn kịch bản trả lời Hội đồng Bảo vệ (Defense Talking Points):**
   * Tận dụng tài liệu này để đưa vào mục *"Giới hạn và Giải pháp kiểm soát chất lượng dữ liệu"* trong Báo cáo cuối kỳ.
