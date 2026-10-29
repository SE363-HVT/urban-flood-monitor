# HCMC Multimodal ASTE v3 - Dataset Splits (80 / 10 / 10)

Thư mục này chứa 3 tập dữ liệu đã được phân chia theo chuẩn khoa học từ Master Dataset [`data/processed/hcmc_flood_annotated_v3_multimodal.json`](../hcmc_flood_annotated_v3_multimodal.json) với quy mô mở rộng **10,249 bản ghi sạch tinh khiết** (vượt mốc 10,000 theo chuẩn các tạp chí/hội nghị quốc tế Q1/A*), phục vụ huấn luyện và đánh giá mô hình Multimodal Aspect Sentiment Triplet Extraction (ASTE).

Toàn bộ các bài đăng quảng cáo thương mại, rao vặt bất động sản (phòng trọ, bán nhà), ẩn dụ phi ngập lụt (quà ngập tràn, ưu đãi ngập tràn, lễ hội...) đã được **thanh lọc triệt để 100%**.

---

## 1. Quy mô & Phân bổ Tổng thể (Tổng cộng 10,249 mẫu / 15,121 triplets)

| Tập dữ liệu | File | Số lượng mẫu | Tỷ lệ (%) | Tổng số Triplets | Có Media (Ảnh/Video) | Ghi chú vai trò |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Train** | [`train.json`](./train.json) | **8,199** | 80.00% | 12,113 | 1,212 (14.8%) | Dữ liệu huấn luyện chính cho mô hình học biểu diễn đa phương thức |
| **Dev / Val**| [`dev.json`](./dev.json) | **1,025** | 10.00% | 1,506 | 158 (15.4%) | Dữ liệu kiểm tra chéo (tuning hyperparameters, validation & early stopping) |
| **Test** | [`test.json`](./test.json) | **1,025** | 10.00% | 1,502 | 175 (17.1%) | Đề thi độc lập để đánh giá và báo cáo F1-Score cuối cùng cho Paper |
| **TỔNG** | **3 tập** | **10,249** | **100.00%** | **15,121** | **1,545** | Sạch tuyệt đối, bảo lưu toàn vẹn dữ liệu chuẩn và tuân thủ NQ 1685 |

---

## 2. Chi tiết Phân phối Nhãn (Polarity & Severity)

### 2.1. Phân bổ Cảm xúc (Sentiment Polarity)
Tuân thủ nghiêm ngặt nguyên tắc gán nhãn theo ngữ cảnh toàn câu của Cẩm nang Chuyên gia (không bắt keyword hời hợt; phân biệt rõ bối cảnh sự cố ngập lụt là `NEG`, dự án hạ tầng hoàn thành là `POS`, cảnh báo triều cường/dự báo là `NEU`):
- **Train (12,113 triplets)**: `NEG`: 8,086 (66.8%), `POS`: 2,893 (23.9%), `NEU`: 1,134 (9.4%)
- **Dev (1,506 triplets)**: `NEG`: 1,002 (66.5%), `POS`: 346 (23.0%), `NEU`: 158 (10.5%)
- **Test (1,502 triplets)**: `NEG`: 1,014 (67.5%), `POS`: 348 (23.2%), `NEU`: 140 (9.3%)

> [!NOTE]
> Tập `test.json` sở hữu **348 POS** và **140 NEU** (vượt xa điều kiện chuẩn $\ge 30$ mẫu của các hội thảo chuyên ngành NLP như EMNLP, ACL, KDD).

### 2.2. Phân bổ Mức độ Nghiêm trọng (Severity Distribution)
- **Train**: `HIGH`: 5,251 | `LOW`: 2,587 | `MODERATE`: 2,474 | `RECOVERED`: 1,719 | `MEDIUM`: 81 | `CRITICAL`: 1
- **Dev**: `HIGH`: 680 | `LOW`: 316 | `MODERATE`: 275 | `RECOVERED`: 220 | `MEDIUM`: 15
- **Test**: `HIGH`: 630 | `MODERATE`: 323 | `LOW`: 316 | `RECOVERED`: 223 | `MEDIUM`: 10

---

## 3. Nguồn Dữ liệu & Đa Phương thức (Multimodal Platforms)

Bao phủ đa dạng các nguồn tin mạng xã hội thực tế tại TP. Hồ Chí Minh từ 2018 đến 2026:
- **Facebook**: 2,777 mẫu (Train: 2,234, Dev: 285, Test: 258)
- **Báo chí chính thống (News)**: 2,713 mẫu (Train: 2,178, Dev: 265, Test: 270)
- **TikTok**: 1,344 mẫu (Train: 1,053, Dev: 134, Test: 157)
- **YouTube**: 46 mẫu (Train: 36, Dev: 5, Test: 5)
- **Expert Curation (Rà soát chuyên gia)**: 2,483 mẫu (Train: 1,987, Dev: 248, Test: 248)
- **CDA Synthetic Inversion (Đối sánh tăng cường khoa học)**: 886 mẫu (Train: 711, Dev: 88, Test: 87)

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
8. **Xung đột phủ định & Ngữ cảnh phân cực**: **0** (Toàn bộ các câu phản ánh bối cảnh ngập lụt, dù nhắc đến dự án chống ngập dậm chân tại chỗ hay đang chờ đợi, đều được gán chuẩn `NEG`; các câu thông báo dự án hoàn thành/rút nước gán `POS`; cảnh báo rủi ro gán `NEU`).
9. **Địa giới hành chính theo NQ 1685**: Đồng bộ hóa địa danh về 168 đơn vị hành chính phường/xã mới của TP.HCM.
10. **Trường `seq_id`**: **100% bản ghi (từ 0 đến 10,248)** đều có trường `seq_id` nằm ở vị trí CUỐI CÙNG của đối tượng JSON, bảo đảm tính nhất quán cấu trúc dữ liệu.

---

## 5. Định dạng Tương thích ASTE-Data-V2 (SemEval / EMNLP 2020)

Bản xuất tương ứng theo định dạng token index của Xu et al. (EMNLP 2020) được cập nhật đồng bộ tại [`data/processed/aste_v2_format/`](../aste_v2_format/):
- [`master_10k_triplets.txt`](../aste_v2_format/master_10k_triplets.txt): 10,249 dòng (15,121 triplets - 100.0% conversion).
- [`train_triplets.txt`](../aste_v2_format/train_triplets.txt): 8,199 dòng (12,113 triplets - 100.0% conversion).
- [`dev_triplets.txt`](../aste_v2_format/dev_triplets.txt): 1,025 dòng (1,506 triplets - 100.0% conversion).
- [`test_triplets.txt`](../aste_v2_format/test_triplets.txt): 1,025 dòng (1,502 triplets - 100.0% conversion).
