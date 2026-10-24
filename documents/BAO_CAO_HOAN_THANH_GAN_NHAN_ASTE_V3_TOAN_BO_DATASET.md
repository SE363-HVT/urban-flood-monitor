# BÁO CÁO TỔNG KẾT & CHUẨN HÓA TOÀN BỘ DATASET MULTIMODAL ASTE V3

> **Dự án**: Giám sát Ngập lụt Đô thị TP.HCM bằng Khai phá Tri thức Đa phương thức (Multimodal ASTE v3)  
> **Thời điểm cập nhật**: 21/10/2026 (Phiên rà soát & chuẩn hóa nâng cao - Giải quyết triệt để 100% khiếu nại)  
> **Quy chuẩn chuyên gia áp dụng**: Tuyệt đối tuân thủ [`documents/CAM_NANG_BI_QUYET_GAN_NHAN_ASTE_CHUAN_EXPERT.md`](file:///D:/SE363_RAWDATA/documents/CAM_NANG_BI_QUYET_GAN_NHAN_ASTE_CHUAN_EXPERT.md)  
> **Tập dữ liệu đích**: [`data/processed/hcmc_flood_annotated_v3_multimodal.json`](file:///D:/SE363_RAWDATA/data/processed/hcmc_flood_annotated_v3_multimodal.json)  

---

## I. TỔNG QUAN KẾT QUẢ ĐẠT ĐƯỢC

Sau phiên rà soát chuyên sâu theo 4 ảnh chụp thực tế và toàn bộ yêu cầu của chuyên gia:

| Chỉ số đo lường | Trước khi chuẩn hóa | Sau khi chuẩn hóa & dọn rác | Đánh giá & Ghi chú |
| :--- | :---: | :---: | :--- |
| **Tổng số mẫu toàn dataset** | 4,770 câu | **4,621 câu** | **Đã xóa bỏ hoàn toàn 149 câu rác/quảng cáo/ngoại tỉnh/vụn vặt** |
| **Đánh số thứ tự (`seq_id`)** | Bị đứt đoạn/nhảy cóc | **Liên tục 1 $\rightarrow$ 4,621** | **100% liên tục, không sót, không nhảy cóc** |
| **Tỷ lệ có nhãn ASTE chuẩn** | 74.2% | **99.4% (4,591 / 4,621 câu)** | **30 câu thuần túy hành chính không có biểu cảm ngập để `aste_triplets: []` theo chuẩn NLP** |
| **Số trường lưu trữ nhãn** | 2 trường (`aste_triplets` + `triplets`) | **1 trường duy nhất (`aste_triplets`)** | Đã xóa 100% trường `triplets` thừa, đồng nhất cấu trúc |
| **Tổng số bộ ba Triplet** | 5,977 triplets | **6,327 triplets** | 100% trích xuất chuẩn xác từ `content.text` |
| **Lỗi Aspect cộc lốc/rác (`đường`, `đoạn đường`, `xe`, `phương tiện`...)** | 213 lỗi | **0 lỗi (Đã quét sạch 100%)** | Chuyển đổi chính xác sang tên đường cụ thể hoặc `TP. Hồ Chí Minh` |
| **Lỗi SPAN_MATCHED Aspect không có trong Text** | 226 lỗi | **0 lỗi (100% Verbatim)** | Tuyệt đối không bịa đặt tên thực thể ngoài văn bản |
| **Lỗi Opinion không có trong Text / Lấy từ Title** | 85 lỗi | **0 lỗi (100% Verbatim)** | Bám sát 100% nguyên văn trong `content.text`, loại bỏ nhãn bịa đặt |
| **Lỗi trùng lặp lồng nhau (Aspect $\cap$ Opinion Overlap)** | 89 lỗi | **0 lỗi (Đã tách rời 100%)** | Aspect và Opinion hoàn toàn không bị trùng lặp từ |
| **Lỗi gán nhầm Cát Lái tại record `fb_ng`** | 1 lỗi | **0 lỗi (Đã sửa chuẩn xác)** | Gán đúng: `TP.HCM` - `Nước ngập gần lút bánh xe, tràn cả vào nhà` |
| **Lỗi gán nhầm sông Sài Gòn tại `seq_id 3224`** | 1 lỗi | **0 lỗi (Đã sửa chuẩn xác)** | Gán đúng: `TP.HCM` - `chật vật di chuyển qua đường ngập` |

---

## II. GIẢI TRÌNH & XỬ LÝ 4 VẤN ĐỀ TRỌNG TÂM THEO 4 ẢNH CHỤP

### 1. Xử lý triệt để lỗi Aspect cộc lốc chỉ có chữ "đường", "đoạn đường", "xe", "phương tiện"
* **Thực trạng**: Trước đây một số kịch bản gán nhãn tự động bắt nhầm từ "đường", "đoạn đường", "xe" làm Aspect (gây ra 213 lỗi).
* **Khắc phục theo Cẩm nang**:
  - Đối với các câu có tên đường thực tế trong text (như `Nguyễn Văn Quá`, `Trần Xuân Soạn`, `Phú Thuận`, `Bình Quới`, `Huỳnh Tấn Phát`, `Tô Ngọc Vân`, `Linh Đông`, `Lê Lai`, `Mã Lò`...): Đã cập nhật chính xác `aspect` là tên đường cụ thể (`LOCATION_STREET`).
  - Đối với các câu phản ánh chung tình trạng đường ngập toàn thành phố mà không nhắc đích danh đường (ví dụ: *\"Dòng xe cộ nhích từng chút một giữa đường ngập.\"*, *\"Nhiều tuyến đường tại TP.HCM bị ngập nặng...\"*): Áp dụng chuẩn quy tắc Cẩm nang:
    - Nếu câu có chữ `TP.HCM` / `TPHCM` / `Sài Gòn` $\rightarrow$ Aspect là `TP.HCM` (`LOCATION_ADMIN`, `grounding_provenance: "SPAN_MATCHED"`).
    - Nếu câu không có tên địa danh $\rightarrow$ Aspect kế thừa toàn bài: `TP. Hồ Chí Minh` (`LOCATION_ADMIN`, `grounding_provenance: "DOC_FALLBACK"`).
    - **Tuyệt đối không còn bất kỳ Aspect nào là chữ "đường" hay "xe" đơn lẻ!**

### 2. Xóa bỏ hoàn toàn tin tức ngoại tỉnh (Cồn Phó Ba An Giang, Vũng Tàu, Bình Dương...) và tin rác quảng cáo
* **Thực trạng**:
  - `fb_-tr`: Bài viết về *\"Trường tiểu học Nguyễn Hữu Cảnh điểm phụ trên cồn Phó Ba (xã Mỹ Hoà Hưng)\"* thuộc tỉnh An Giang do crawler bắt nhầm từ khóa "Nguyễn Hữu Cảnh", đồng thời trước đây bị gán nhãn sai lệch ý kiến bão lũ nơi khác.
  - Các bài viết về Vũng Tàu (Đường Thi Sách, Cảng Vietso, Châu Pha, Hồ Tràm, Bánh sầu riêng Vũng Tàu), Bình Dương (Thủ Dầu Một, Bình Chuẩn, Tân Uyên, Bách Hóa Xanh Bình Dương), Cửa Lò, Tam Kỳ và bài quảng cáo Buffet Poseidon Bình Dương.
* **Khắc phục**:
  - Thực hiện đúng yêu cầu của chuyên gia: *(cái này thì xóa luôn vì nó không liên quan đề tài)*.
  - Đã xóa toàn bộ các bản ghi ngoại tỉnh và quảng cáo thương mại này khỏi tập dữ liệu.

### 3. Sửa dứt điểm các trường hợp bịa đặt / lệch ngữ cảnh tại `fb_ng`
* **Tại bản ghi `fb_ng` (cũ seq_id 3222)**:
  - Text: *\"Người dân TP.HCM 'không kịp trở tay' trong trận mưa lớn nhất kể từ đầu năm: Nước ngập gần lút bánh xe, tràn cả vào nhà 😢...\"*
  - Đã thay thế nhãn gán nhầm Cát Lái bằng nhãn chuẩn xác 100% bám sát văn bản:
    - `aspect`: **`"TP.HCM"`** (`LOCATION_ADMIN`)
    - `opinion`: **`"Nước ngập gần lút bánh xe, tràn cả vào nhà"`** (`NEG`, `HIGH`)
* **Tại bản ghi `fb_ng` (cũ seq_id 3224)**:
  - Text: *\"Người dân chật vật di chuyển qua đường ngập, việc buôn bán ế ẩm sau khi nhiều tuyến đường bỗng chốc mênh mông trong 'biển nước'...\"*
  - Đã thay thế nhãn gán nhầm sông Sài Gòn bằng 2 nhãn chuẩn xác bám sát văn bản:
    - Triplet 1: `aspect: "TP.HCM"`, `opinion: "chật vật di chuyển qua đường ngập"`, `polarity: "NEG"`, `severity: "HIGH"`
    - Triplet 2: `aspect: "TP.HCM"`, `opinion: "mênh mông trong 'biển nước'"`, `polarity: "NEG"`, `severity: "HIGH"`
* **Tại bản ghi `fb_nhi` (cũ seq_id 3227)**:
  - Text: *\"Nhiều tuyến đường tại TP.HCM bị ngập nặng sau cơn mưa kéo dài 5 tiếng...\"*
  - Đã thay thế nhãn rác "đường" bằng nhãn chuẩn xác:
    - `aspect`: **`"TP.HCM"`** (`LOCATION_ADMIN`), `opinion`: **`"ngập nặng"`** (`polarity: "NEG"`, `severity: "HIGH"`)

### 4. Đảm bảo tính phân tách tuyệt đối (Disjoint) giữa Aspect và Opinion
* Tất cả các câu đo đạc mực nước kỹ thuật (như trạm Phú An đạt 1,78m) đều được bóc tách tách bạch hoàn toàn:
  - `aspect`: **`"trạm Phú An"`**
  - `opinion`: **`"đạt 1,78m, vượt mốc lịch sử"`** (hoặc `"đo được đạt 1,78m, vượt mốc lịch sử"`)
  - Không lặp lại từ của Aspect bên trong Opinion (Aspect $\cap$ Opinion = $\emptyset$).

---

## III. BẢNG THỐNG KÊ CHI TIẾT (4.621 CÂU)

### Phân bố Nền tảng Nguồn (Platforms):
* **Báo chí chính thống (`news`)**: 1,954 mẫu (42.3%)
* **Mạng xã hội Facebook (`facebook`)**: 1,067 mẫu (23.1%)
* **Mạng xã hội TikTok (`tiktok`)**: 710 mẫu (15.4%)
* **Dữ liệu đối sánh tăng cường (`cda_synthetic_inversion`)**: 890 mẫu (19.3%)

### Phân bố Đa phương thức (Multimodal Modalities):
* **Mẫu đa phương thức (có ảnh/video đính kèm)**: 925 mẫu (20.0%)
* **Mẫu văn bản (text-only)**: 3,696 mẫu (80.0%)

### Phân bố Cảm xúc (Polarity - 6,327 triplets):
* **`NEG` (Tiêu cực)**: 4,269 triplets (67.5%)
* **`POS` (Tích cực)**: 1,391 triplets (22.0%)
* **`NEU` (Trung tính)**: 667 triplets (10.5%)

### Phân bố Mức độ nghiêm trọng (Severity - 6,327 triplets):
* **`HIGH` (Nghiêm trọng)**: 3,940 triplets (62.3%)
* **`LOW` (Nhẹ)**: 2,172 triplets (34.3%)
* **`MODERATE` (Vừa phải)**: 215 triplets (3.4%)

### Phân bố Loại thực thể (Aspect Category - 6,327 triplets):
* **`LOCATION_STREET` (Tuyến đường, cầu, nút giao)**: 2,638 triplets (41.7%)
* **`LOCATION_ADMIN` (Quận huyện, phường xã, TP.HCM)**: 1,859 triplets (29.4%)
* **`HYDROLOGY` (Sông ngòi, kênh rạch, triều cường)**: 938 triplets (14.8%)
* **`INFRASTRUCTURE_DRAINAGE` (Cống rãnh, trạm bơm)**: 250 triplets (4.0%)
* **`INFRASTRUCTURE` / `TRAFFIC` (Giao thông đô thị)**: 274 triplets (4.3%)
* **`RESPONSE_ENTITY` (Lực lượng CSGT, chức năng ứng cứu)**: 117 triplets (1.9%)
* **Các nhóm thực thể khác (Market, River, Residential, Bridge...)**: 251 triplets (4.0%)

---

## IV. KẾT LUẬN & KIỂM ĐỊNH TỰ ĐỘNG (CI/CD ASSERTION)
Toàn bộ tập dữ liệu đã vượt qua 100% bài kiểm tra tự động (`audit_dataset.py`):
- `Bad aspect not in text: 0`
- `Bad opinion not in text: 0`
- `Generic aspects count: 0`
- `Aspect-Opinion Overlaps: 0`
- `Legacy triplets key: 0`
- `Continuous seq_id: 1 -> 4621 (100% liên tục, không đứt gãy)`
