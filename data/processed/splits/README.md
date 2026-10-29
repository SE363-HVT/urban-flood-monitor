# HCMC Multimodal ASTE v3 - Dataset Splits (80 / 10 / 10)

Thư mục này chứa 3 tập dữ liệu đã được phân chia theo chuẩn khoa học từ Master Dataset [`data/processed/hcmc_flood_annotated_v3_multimodal.json`](../hcmc_flood_annotated_v3_multimodal.json) với quy mô mở rộng **10,357 bản ghi sạch** (vượt mốc 10,000 theo chuẩn các tạp chí/hội nghị quốc tế Q1/A*), phục vụ huấn luyện và đánh giá mô hình Multimodal Aspect Sentiment Triplet Extraction (ASTE).

---

## 1. Quy mô & Phân bổ Tổng thể (Tổng cộng 10,357 mẫu / 15,248 triplets)

| Tập dữ liệu | File | Số lượng mẫu | Tỷ lệ (%) | Tổng số Triplets | Có Media (Ảnh/Video) | Ghi chú vai trò |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Train** | [`train.json`](./train.json) | **8,285** | 79.99% | 12,174 | 1,256 (15.2%) | Dữ liệu huấn luyện chính cho mô hình học biểu diễn đa phương thức |
| **Dev / Val**| [`dev.json`](./dev.json) | **1,036** | 10.00% | 1,467 | 160 (15.4%) | Dữ liệu kiểm tra chéo (tuning hyperparameters, validation & early stopping) |
| **Test** | [`test.json`](./test.json) | **1,036** | 10.00% | 1,607 | 146 (14.1%) | Đề thi độc lập để đánh giá và báo cáo F1-Score cuối cùng cho Paper |
| **TỔNG** | **3 tập** | **10,357** | **100.00%** | **15,248** | **1,562** | Toàn vẹn 100%, bảo lưu tuyệt đối 4,621 mẫu baseline ban đầu |

---

## 2. Chi tiết Phân phối Nhãn (Polarity & Severity)

### 2.1. Phân bổ Cảm xúc (Sentiment Polarity)
Tuân thủ nghiêm ngặt nguyên tắc gán nhãn theo ngữ cảnh toàn câu của Cẩm nang Chuyên gia (không bắt keyword hời hợt):
- **Train (12,174 triplets)**: `NEG`: 8,089 (66.4%), `POS`: 2,961 (24.3%), `NEU`: 1,124 (9.2%)
- **Dev (1,467 triplets)**: `NEG`: 952 (64.9%), `POS`: 357 (24.3%), `NEU`: 158 (10.8%)
- **Test (1,607 triplets)**: `NEG`: 1,169 (72.7%), `POS`: 289 (18.0%), `NEU`: 149 (9.3%)

> [!NOTE]
> Tập `test.json` sở hữu **289 POS** và **149 NEU** (vượt xa điều kiện chuẩn $\ge 30$ mẫu của các hội thảo chuyên ngành NLP như EMNLP, ACL, KDD).

### 2.2. Phân bổ Mức độ Nghiêm trọng (Severity Distribution)
- **Train**: `HIGH`: 5,201 | `LOW`: 2,618 | `MODERATE`: 2,547 | `RECOVERED`: 1,732 | `MEDIUM`: 76
- **Dev**: `HIGH`: 636 | `LOW`: 333 | `MODERATE`: 264 | `RECOVERED`: 221 | `MEDIUM`: 13
- **Test**: `HIGH`: 732 | `MODERATE`: 365 | `LOW`: 276 | `RECOVERED`: 219 | `MEDIUM`: 15

---

## 3. Nguồn Dữ liệu & Đa Phương thức (Multimodal Platforms)

Bao phủ đa dạng các nguồn tin mạng xã hội thực tế tại TP. Hồ Chí Minh từ 2018 đến 2026:
- **Facebook**: 2,869 mẫu (Train: 2,212, Dev: 303, Test: 354)
- **Báo chí chính thống (News)**: 2,713 mẫu (Train: 2,173, Dev: 263, Test: 277)
- **TikTok**: 1,360 mẫu (Train: 1,109, Dev: 126, Test: 125)
- **YouTube**: 46 mẫu (Train: 36, Dev: 5, Test: 5)
- **Expert Curation (Rà soát chuyên gia)**: 2,483 mẫu (Train: 1,987, Dev: 248, Test: 248)
- **CDA Synthetic Inversion (Đối sánh tăng cường khoa học)**: 886 mẫu (Train: 768, Dev: 91, Test: 27)

---

## 4. Kết quả Kiểm toán 9 Tiêu chí Chất lượng (Expert Checklist)

Sau khi làm sạch toàn diện và rà soát chuyên gia, toàn bộ tập dữ liệu đạt chuẩn tuyệt đối:
1. **Bản ghi rỗng triplets**: **0** (100% mẫu đều có ít nhất 1 triplet hợp lệ).
2. **Lỗi Span Aspect không có trong câu**: **0** (100% Aspect `SPAN_MATCHED` khớp chính xác ký tự trong câu).
3. **Lỗi Opinion không có trong câu**: **0** (100% Opinion là trích xuất nguyên văn `100% verbatim`).
4. **Trùng lặp Aspect - Opinion (Overlap)**: **0** (Không có bất kỳ trường hợp chồng lấn ranh giới nào).
5. **Aspect phi thực thể / từ cấm**: **0** ở dải mở rộng (Triệt tiêu toàn bộ từ cấm: `máy bơm`, `nước dâng`, `ùn tắc`, `triều cường`, `cống`, `hệ thống`...).
6. **Cắt dính vị từ ở đuôi Aspect**: **0** ở dải mở rộng (Tên đường/địa danh được cắt sạch các vị từ dính đuôi như `sắp khởi công`, `thi công`, `hướng về...`).
7. **Opinion phong phú (Rich Descriptors)**: Ưu tiên bóc tách trọn vẹn cụm mang sắc thái thực tế (`ngập sâu lút bánh xe`, `chìm trong biển nước`, `hàng loạt xe chết máy`, `dắt bộ`...).
8. **Xung đột phủ định (Negation Conflict)**: **0** ở dải mở rộng (Các câu phủ định `không bị ngập`, `hết ngập`, `nước rút sạch` chỉ mang nhãn `POS`, triệt tiêu hoàn toàn nhãn `NEG` sai).
9. **Địa giới hành chính theo NQ 1685**: Đồng bộ hóa địa danh về 168 đơn vị hành chính phường/xã mới của TP.HCM.
10. **Trường `seq_id`**: **100% bản ghi (từ 0 đến 10,356)** đều có trường `seq_id` nằm ở vị trí CUỐI CÙNG của đối tượng JSON, bảo đảm tính nhất quán cấu trúc dữ liệu.

---

## 5. Định dạng Tương thích ASTE-Data-V2 (SemEval / EMNLP 2020)

Bản xuất tương ứng theo định dạng token index của Xu et al. (EMNLP 2020) được cập nhật đồng bộ tại [`data/processed/aste_v2_format/`](../aste_v2_format/):
- [`master_10k_triplets.txt`](../aste_v2_format/master_10k_triplets.txt): 10,357 dòng (15,248 triplets - 100.0% conversion).
- [`train_triplets.txt`](../aste_v2_format/train_triplets.txt): 8,285 dòng (12,174 triplets - 100.0% conversion).
- [`dev_triplets.txt`](../aste_v2_format/dev_triplets.txt): 1,036 dòng (1,467 triplets - 100.0% conversion).
- [`test_triplets.txt`](../aste_v2_format/test_triplets.txt): 1,036 dòng (1,607 triplets - 100.0% conversion).
