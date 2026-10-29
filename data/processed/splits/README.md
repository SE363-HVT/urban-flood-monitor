# HCMC Multimodal ASTE v3 - Dataset Splits (80 / 10 / 10)

Thư mục này chứa 3 tập dữ liệu đã được phân chia theo chuẩn khoa học từ Master Dataset [`data/processed/hcmc_flood_annotated_v3_multimodal.json`](../hcmc_flood_annotated_v3_multimodal.json) với quy mô mở rộng **10,432 bản ghi** (vượt mốc 10k theo chuẩn các tạp chí / hội nghị quốc tế Q1/A*), phục vụ huấn luyện và đánh giá mô hình Multimodal Aspect Sentiment Triplet Extraction (ASTE).

---

## 1. Quy mô & Phân bổ Tổng thể (Tổng cộng 10,432 mẫu / 15,433 triplets)

| Tập dữ liệu | File | Số lượng mẫu | Tỷ lệ (%) | Tổng số Triplets | Có Media (Ảnh/Video) | Ghi chú vai trò |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Train** | [`train.json`](./train.json) | **8,346** | 80.00% | 12,329 | 1,290 (15.5%) | Dữ liệu huấn luyện chính cho mô hình học biểu diễn đa phương thức |
| **Dev / Val**| [`dev.json`](./dev.json) | **1,043** | 10.00% | 1,535 | 157 (15.1%) | Dữ liệu kiểm tra chéo (tuning hyperparameters, validation & early stopping) |
| **Test** | [`test.json`](./test.json) | **1,043** | 10.00% | 1,569 | 145 (13.9%) | Đề thi độc lập để đánh giá và báo cáo F1-Score cuối cùng cho Paper |
| **TỔNG** | **3 tập** | **10,432** | **100.00%** | **15,433** | **1,592** | Toàn vẹn 100%, bảo lưu tuyệt đối 4,621 mẫu baseline ban đầu |

---

## 2. Chi tiết Phân phối Nhãn (Polarity & Severity)

### 2.1. Phân bổ Cảm xúc (Sentiment Polarity)
Đảm bảo duy trì tỷ lệ tự nhiên của bài toán cảnh báo ngập lụt thực địa, đồng thời cung cấp đủ mẫu `POS` và `NEU` để mô hình học phân biệt sắc thái đối lập / phục hồi:
- **Train (12,329 triplets)**: `NEG`: 8,384 (68.0%), `POS`: 2,847 (23.1%), `NEU`: 1,098 (8.9%)
- **Dev (1,535 triplets)**: `NEG`: 1,000 (65.1%), `POS`: 337 (22.0%), `NEU`: 198 (12.9%)
- **Test (1,569 triplets)**: `NEG`: 1,077 (68.6%), `POS`: 368 (23.5%), `NEU`: 124 (7.9%)

> [!NOTE]
> Tập `test.json` sở hữu **368 POS** và **124 NEU** (vượt xa điều kiện chuẩn $\ge 30$ mẫu của các hội thảo chuyên ngành NLP/Data Mining như EMNLP, ACL, KDD).

### 2.2. Phân bổ Mức độ Nghiêm trọng (Severity Distribution)
- **Train**: `HIGH`: 5,250 | `MODERATE`: 2,752 | `LOW`: 2,499 | `RECOVERED`: 1,740 | `MEDIUM`: 88
- **Dev**: `HIGH`: 619 | `MODERATE`: 333 | `LOW`: 354 | `RECOVERED`: 216 | `MEDIUM`: 13
- **Test**: `HIGH`: 728 | `MODERATE`: 312 | `LOW`: 306 | `RECOVERED`: 220 | `MEDIUM`: 3

---

## 3. Nguồn Dữ liệu & Đa Phương thức (Multimodal Platforms)

Tập dữ liệu bao phủ đa dạng các nguồn tin mạng xã hội thực tế tại TP. Hồ Chí Minh từ 2018 đến 2026:
- **Facebook**: 2,911 mẫu (Train: 2,261, Dev: 319, Test: 331)
- **Báo chí chính thống (News)**: 2,716 mẫu (Train: 2,194, Dev: 277, Test: 245)
- **TikTok**: 1,390 mẫu (Train: 1,129, Dev: 134, Test: 127)
- **YouTube**: 46 mẫu (Train: 37, Dev: 5, Test: 4)
- **Expert Curation (Rà soát chuyên gia)**: 2,483 mẫu (Train: 1,987, Dev: 248, Test: 248)
- **CDA Synthetic Inversion (Đối sánh tăng cường khoa học)**: 886 mẫu (Train: 738, Dev: 60, Test: 88)

---

## 4. Các Nguyên tắc Kỹ thuật Đã Áp Dụng

1. **Chống rò rỉ dữ liệu (Strict Zero Data Leakage - Parent-grouped)**:
   - Các câu trích đoạn sinh ra từ cùng một bài viết gốc (`parent_id`) luôn được gom nhóm và nằm trọn vẹn trong cùng một tập (`Train`, `Dev` hoặc `Test`). Tuyệt đối không xuất hiện hiện tượng chồng lấn thông tin ngữ cảnh giữa tập huấn luyện và tập kiểm thử.
2. **Tuân thủ Cẩm nang Gán nhãn Chuyên gia**:
   - Tất cả bản ghi đều tuân thủ nghiêm ngặt theo hướng dẫn tại [`CAM_NANG_BI_QUYET_GAN_NHAN_ASTE_CHUAN_EXPERT.md`](../../documents/CAM_NANG_BI_QUYET_GAN_NHAN_ASTE_CHUAN_EXPERT.md): trích xuất cụm biểu đạt sắc thái nguyên văn (rich verbatim descriptors), loại bỏ hoàn toàn các thực thể cấm (`máy bơm`, `nước dâng`, `ùn tắc`, `đang`, `xuất hiện tình trạng`), triệt tiêu xung đột nhãn con (như *không bị ngập úng* luôn là nhãn `POS` độc nhất).
3. **Bảo tồn 100% Tập Baseline**:
   - Toàn bộ 4,621 mẫu gốc ban đầu (`seq_id: 0` đến `4620`) được giữ nguyên vẹn tuyệt đối vị trí và dữ liệu.
4. **Định dạng tương thích ASTE-Data-V2**:
   - Bản phân chia tương ứng theo chuẩn index vị trí SemEval / ASTE-Data-V2 đã được xuất tự động tại thư mục [`data/processed/aste_v2_format/`](../aste_v2_format/) gồm `train_triplets.txt`, `dev_triplets.txt`, `test_triplets.txt` và `master_10k_triplets.txt`.
5. **Khả năng tái lập khoa học (Reproducibility)**:
   - Sử dụng hạt ngẫu nhiên cố định `RANDOM_SEED = 42`.
   - Metadata chi tiết từng tiêu chí được đồng bộ tại [`split_metadata.json`](./split_metadata.json).
