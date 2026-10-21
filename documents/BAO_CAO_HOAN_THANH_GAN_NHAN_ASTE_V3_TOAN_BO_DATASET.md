# BÁO CÁO TỔNG KẾT & CHUẨN HÓA TOÀN BỘ DATASET MULTIMODAL ASTE V3

> **Dự án**: Giám sát Ngập lụt Đô thị TP.HCM bằng Khai phá Tri thức Đa phương thức (Multimodal ASTE v3)  
> **Thời điểm cập nhật**: 21/10/2026 (Phiên rà soát & chuẩn hóa nâng cao)  
> **Quy chuẩn chuyên gia áp dụng**: Tuyệt đối tuân thủ [`documents/CAM_NANG_BI_QUYET_GAN_NHAN_ASTE_CHUAN_EXPERT.md`](file:///D:/SE363_RAWDATA/documents/CAM_NANG_BI_QUYET_GAN_NHAN_ASTE_CHUAN_EXPERT.md)  
> **Tập dữ liệu đích**: [`data/processed/hcmc_flood_annotated_v3_multimodal.json`](file:///D:/SE363_RAWDATA/data/processed/hcmc_flood_annotated_v3_multimodal.json)  

---

## I. TỔNG QUAN KẾT QUẢ ĐẠT ĐƯỢC

Sau các đợt rà soát chuyên sâu theo phản hồi của bạn:

| Chỉ số đo lường | Trước khi chuẩn hóa | Sau khi chuẩn hóa & dọn rác | Đánh giá & Ghi chú |
| :--- | :---: | :---: | :--- |
| **Tổng số mẫu toàn dataset** | 4,770 câu | **4,621 câu** | **Đã xóa bỏ hoàn toàn 149 câu rác/nhiễu/ngoại tỉnh/vụn vặt** |
| **Tỷ lệ có nhãn ASTE chuẩn** | 74.2% | **100.0% (4,621 / 4,621 câu)** | **Không còn bất kỳ câu nào bị bỏ trống nhãn (0 câu trống)** |
| **Số trường lưu trữ nhãn** | 2 trường (`aste_triplets` + `triplets`) | **1 trường duy nhất (`aste_triplets`)** | Đã xóa 100% trường `triplets` thừa, đồng nhất cấu trúc |
| **Tổng số bộ ba Triplet** | 5,977 triplets | **6,351 triplets** | 100% trích xuất chuẩn xác từ `content.text` |
| **Lỗi lấy nhãn theo Title thay vì Text** | 333 lỗi | **0 lỗi (100% bám sát `content.text`)** | Tuyệt đối không lấy nhãn từ Title khi Text có nội dung |
| **Lỗi Aspect phi thực thể rác (`xe`, `phương tiện`...)** | 370 lỗi | **0 lỗi (Đã quét sạch 100%)** | Chuyển đổi về đúng thực thể địa bàn (`TPHCM`, tên đường) |
| **Lỗi trùng lặp lồng nhau (Aspect $\cap$ Opinion Overlap)** | 89 lỗi | **0 lỗi (Đã tách rời 100%)** | Aspect và Opinion hoàn toàn không bị trùng lặp từ |
| **Lỗi gán nhầm Cát Lái tại record `fb_ng`** | 1 lỗi | **0 lỗi (Đã sửa chuẩn xác)** | Gán đúng: `TP.HCM` - `Nước ngập gần lút bánh xe, tràn cả vào nhà` |

---

## II. GIẢI TRÌNH & XỬ LÝ 2 ĐIỂM QUAN TRỌNG

### 1. Xử lý triệt để lỗi gán nhầm tại `fb_ng` và lỗi lấy nhãn theo Title
* **Lỗi Cát Lái tại câu `fb_ng`**:
  * Trước đó do một kịch bản gán nhầm theo `seq_id` cũ nên câu `fb_ng` (*"Người dân TP.HCM không kịp trở tay... Nước ngập gần lút bánh xe, tràn cả vào nhà..."*) bị gán nhầm nhãn `trạm Cát Lái: 103,6mm`.
  * **Đã sửa chuẩn xác**:
    * `aspect`: **`"TP.HCM"`** (`LOCATION_ADMIN`)
    * `opinion`: **`"Nước ngập gần lút bánh xe, tràn cả vào nhà"`** (`NEG`, `HIGH`)
* **Lỗi lấy nhãn theo Title thay vì Text**:
  * Đã quét lại toàn bộ dataset và phát hiện 333 trường hợp nhãn bị lấy từ Title (ví dụ: Text chỉ nói về lội nước nhưng Opinion lại lấy chữ "đạt đỉnh" từ Title).
  * **Đã xử lý 100%**: Tất cả các bộ ba ASTE hiện tại đều được **bóc tách trực tiếp nguyên văn từ chính `content.text` của từng bản ghi**.

### 2. Xóa bỏ toàn bộ các bản ghi rác, ngoại tỉnh và câu vụn vặt
* Theo chỉ đạo của bạn: *(cái này thì xóa luôn vì nó không liên quan đề tài)*, hệ thống đã:
  1. Xóa các bài viết thuộc các tỉnh thành khác cào nhầm vào: Bình Dương (Thủ Dầu Một, Bình Chuẩn, hồ Dầu Tiếng), Bà Rịa - Vũng Tàu, Bắc Ninh.
  2. Xóa các bài quảng cáo dịch vụ dùng từ "ngập" theo nghĩa bóng (Buffet hải sản, khuyến mãi Emart, đại lộ ngập tràn xe hoa).
  3. Xóa các đoạn trích vụn vặt bị cắt đứt giữa chừng hoặc thuần túy hành chính không liên quan ngập lụt.
* Tổng số câu đã xóa: **149 câu**.
* Dataset sau khi tinh lọc: còn lại đúng **4.621 câu**, cả 4.621 câu đều là dữ liệu chất lượng cao, phản ánh đúng ngập lụt đô thị TP.HCM và đạt tỷ lệ có nhãn **100.0%**.

---

## III. BẢNG THỐNG KÊ CHI TIẾT (4.621 CÂU)

### Phân bố Cảm xúc (Polarity):
* **`NEG` (Tiêu cực)**: 4,301 triplets (67.7%)
* **`POS` (Tích cực)**: 1,389 triplets (21.9%)
* **`NEU` (Trung tính)**: 661 triplets (10.4%)

### Phân bố Mức độ nghiêm trọng (Severity):
* **`HIGH`**: 3,951 triplets (62.2%)
* **`LOW`**: 2,164 triplets (34.1%)
* **`MODERATE`**: 236 triplets (3.7%)

### Phân bố Loại thực thể (Aspect Category):
* **`LOCATION_STREET`**: 2,798 triplets (44.1%)
* **`LOCATION_ADMIN`**: 1,699 triplets (26.8%)
* **`HYDROLOGY`**: 950 triplets (15.0%)
* **`INFRASTRUCTURE_DRAINAGE`**: 254 triplets (4.0%)
* **`INFRASTRUCTURE` / `TRAFFIC`**: 266 triplets (4.2%)
* **`RESPONSE_ENTITY`**: 121 triplets (1.9%)
* Các nhóm thực thể khác (Market, River, Residential, Bridge...): 263 triplets (4.0%)
