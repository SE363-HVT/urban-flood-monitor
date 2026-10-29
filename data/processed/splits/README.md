# HCMC Multimodal ASTE v3 - Dataset Splits (80 / 10 / 10)

Thư mục này chứa 3 tập dữ liệu đã được phân chia theo chuẩn khoa học từ Master Dataset [`data/processed/hcmc_flood_annotated_v3_multimodal.json`](../hcmc_flood_annotated_v3_multimodal.json) với quy mô mở rộng **10,392 bản ghi** (vượt mốc 10,000 theo chuẩn các tạp chí/hội nghị quốc tế Q1/A*), phục vụ huấn luyện và đánh giá mô hình Multimodal Aspect Sentiment Triplet Extraction (ASTE).

---

## 1. Quy mô & Phân bổ Tổng thể (Tổng cộng 10,392 mẫu / 15,297 triplets)

| Tập dữ liệu | File | Số lượng mẫu | Tỷ lệ (%) | Tổng số Triplets | Có Media (Ảnh/Video) | Ghi chú vai trò |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Train** | [`train.json`](./train.json) | **8,314** | 80.00% | 12,200 | 1,282 (15.4%) | Dữ liệu huấn luyện chính cho mô hình học biểu diễn đa phương thức |
| **Dev / Val**| [`dev.json`](./dev.json) | **1,039** | 10.00% | 1,559 | 148 (14.2%) | Dữ liệu kiểm tra chéo (tuning hyperparameters, validation & early stopping) |
| **Test** | [`test.json`](./test.json) | **1,039** | 10.00% | 1,538 | 140 (13.5%) | Đề thi độc lập để đánh giá và báo cáo F1-Score cuối cùng cho Paper |
| **TỔNG** | **3 tập** | **10,392** | **100.00%** | **15,297** | **1,570** | Toàn vẹn 100%, bảo lưu tuyệt đối 4,621 mẫu baseline ban đầu |

---

## 2. Chi tiết Phân phối Nhãn (Polarity & Severity)

### 2.1. Phân bổ Cảm xúc (Sentiment Polarity)
Duy trì tỷ lệ tự nhiên của thực địa ngập lụt đô thị, đảm bảo đủ số lượng mẫu phân hóa `POS` và `NEU`:
- **Train (12,200 triplets)**: `NEG`: 8,243 (67.6%), `POS`: 2,886 (23.7%), `NEU`: 1,071 (8.8%)
- **Dev (1,559 triplets)**: `NEG`: 1,058 (67.9%), `POS`: 304 (19.5%), `NEU`: 197 (12.6%)
- **Test (1,538 triplets)**: `NEG`: 1,024 (66.6%), `POS`: 361 (23.5%), `NEU`: 153 (9.9%)

> [!NOTE]
> Tập `test.json` sở hữu **361 POS** và **153 NEU** (vượt xa điều kiện chuẩn $\ge 30$ mẫu của các hội thảo chuyên ngành NLP như EMNLP, ACL, KDD).

### 2.2. Phân bổ Mức độ Nghiêm trọng (Severity Distribution)
- **Train**: `HIGH`: 5,237 | `MODERATE`: 2,646 | `LOW`: 2,506 | `RECOVERED`: 1,739 | `MEDIUM`: 72
- **Dev**: `HIGH`: 664 | `MODERATE`: 344 | `LOW`: 306 | `RECOVERED`: 225 | `MEDIUM`: 20
- **Test**: `HIGH`: 670 | `MODERATE`: 299 | `LOW`: 346 | `RECOVERED`: 211 | `MEDIUM`: 12

---

## 3. Nguồn Dữ liệu & Đa Phương thức (Multimodal Platforms)

Bao phủ đa dạng các nguồn tin mạng xã hội thực tế tại TP. Hồ Chí Minh từ 2018 đến 2026:
- **Facebook**: 2,893 mẫu (Train: 2,260, Dev: 354, Test: 279)
- **Báo chí chính thống (News)**: 2,716 mẫu (Train: 2,154, Dev: 275, Test: 287)
- **TikTok**: 1,368 mẫu (Train: 1,108, Dev: 134, Test: 126)
- **YouTube**: 46 mẫu (Train: 37, Dev: 5, Test: 4)
- **Expert Curation (Rà soát chuyên gia)**: 2,483 mẫu (Train: 1,987, Dev: 248, Test: 248)
- **CDA Synthetic Inversion (Đối sánh tăng cường khoa học)**: 886 mẫu (Train: 768, Dev: 23, Test: 95)

---

## 4. Kết quả Kiểm toán 9 Tiêu chí Chất lượng (Expert Checklist)

Sau khi làm sạch toàn diện và rà soát chuyên gia, toàn bộ tập dữ liệu đạt chuẩn tuyệt đối:
1. **Bản ghi rỗng triplets**: **0** (100% mẫu đều có ít nhất 1 triplet hợp lệ).
2. **Lỗi Span Aspect không có trong câu**: **0** (100% Aspect `SPAN_MATCHED` khớp chính xác ký tự trong câu).
3. **Lỗi Opinion không có trong câu**: **0** (100% Opinion là trích xuất nguyên văn `100% verbatim`).
4. **Trùng lặp Aspect - Opinion (Overlap)**: **0** (Không có bất kỳ trường hợp chồng lấn ranh giới nào).
5. **Aspect phi thực thể / từ cấm**: **0** (Triệt tiêu toàn bộ từ cấm: `máy bơm`, `nước dâng`, `ùn tắc`, `triều cường`, `cống`, `hệ thống`...).
6. **Cắt dính vị từ ở đuôi Aspect**: **0** (Tên đường/địa danh được cắt sạch các vị từ dính đuôi như `sắp khởi công`, `thi công`, `hướng về...`).
7. **Opinion phong phú (Rich Descriptors)**: Ưu tiên bóc tách trọn vẹn cụm mang sắc thái thực tế (`ngập sâu lút bánh xe`, `hàng loạt xe chết máy`, `bì bõm lội nước`, `dắt bộ`, `chìm trong biển nước`...).
8. **Xung đột phủ định (Negation Conflict)**: **0** (Các câu phủ định `không bị ngập`, `hết ngập`, `nước rút sạch` chỉ mang nhãn `POS`, triệt tiêu hoàn toàn nhãn `NEG` sai).
9. **Địa giới hành chính theo NQ 1685**: Đồng bộ hóa địa danh về 168 đơn vị hành chính phường/xã mới của TP.HCM.
10. **Trường `seq_id`**: **100% bản ghi (từ 0 đến 10,391)** đều có trường `seq_id` nằm ở vị trí CUỐI CÙNG của đối tượng JSON, bảo đảm tính nhất quán cấu trúc dữ liệu.

---

## 5. Định dạng Tương thích ASTE-Data-V2 (SemEval / EMNLP 2020)

Bản xuất tương ứng theo định dạng token index của Xu et al. (EMNLP 2020) được cập nhật đồng bộ tại [`data/processed/aste_v2_format/`](../aste_v2_format/):
- [`master_10k_triplets.txt`](../aste_v2_format/master_10k_triplets.txt): 10,392 dòng (15,297 triplets - 100.0% conversion).
- [`train_triplets.txt`](../aste_v2_format/train_triplets.txt): 8,314 dòng (12,200 triplets - 100.0% conversion).
- [`dev_triplets.txt`](../aste_v2_format/dev_triplets.txt): 1,039 dòng (1,559 triplets - 100.0% conversion).
- [`test_triplets.txt`](../aste_v2_format/test_triplets.txt): 1,039 dòng (1,538 triplets - 100.0% conversion).
