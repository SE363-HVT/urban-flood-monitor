# HCMC Multimodal ASTE v3 - Dataset Splits (80 / 10 / 10)

Thư mục này chứa 3 tập dữ liệu đã được phân chia theo chuẩn khoa học từ Master Dataset [`data/processed/hcmc_flood_annotated_v3_multimodal.json`](../hcmc_flood_annotated_v3_multimodal.json) phục vụ huấn luyện và đánh giá mô hình Multimodal ASTE.

## 1. Quy mô & Phân bổ (Tổng cộng 4,621 mẫu)

| Tập dữ liệu | File | Số lượng mẫu | Tỷ lệ (%) | Tổng số Triplets | Ghi chú vai trò |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Train** | [`train.json`](./train.json) | **3,697** | 80.00% | 5,029 | Dữ liệu huấn luyện chính cho mô hình học |
| **Dev / Val**| [`dev.json`](./dev.json) | **462** | 10.00% | 662 | Dữ liệu kiểm tra chéo (tuning hyperparameters & early stopping) |
| **Test** | [`test.json`](./test.json) | **462** | 10.00% | 636 | Đề thi độc lập để đánh giá và báo cáo F1-Score cuối cùng |
| **TỔNG** | **3 tập** | **4,621** | 100.00% | 6,327 | Không sót mẫu nào, không rò rỉ dữ liệu |

## 2. Các nguyên tắc kỹ thuật đã áp dụng

1. **Chống rò rỉ dữ liệu (No Data Leakage - Parent-grouped)**:
   - Tất cả các câu trích xuất từ cùng một bài báo hoặc cùng một bài đăng mạng xã hội (`parent_id`) đều nằm trọn vẹn trong cùng 1 tập. Tuyệt đối không có trường hợp một phần bài báo nằm ở Train và một phần nằm ở Dev/Test.
2. **Phân tầng cân bằng (Stratified Balance)**:
   - Tỷ lệ các nhãn cảm xúc (`NEG`, `POS`, `NEU`) và mức độ nghiêm trọng (`HIGH`, `LOW`, `MODERATE`) được duy trì cân đối ở cả 3 tập.
   - Tập `test.json` có **141 POS** và **71 NEU** (vượt xa điều kiện ràng buộc tối thiểu $\ge 30$ mẫu của hội thảo quốc tế ICWSM/KDD).
3. **Cân đối đa phương thức (Multimodal Representation)**:
   - Tỷ lệ mẫu có hình ảnh/video đính kèm đạt xấp xỉ ~20% ở cả 3 tập (Train: 20.2%, Dev: 20.8%, Test: 17.5%).
4. **Khả năng tái lập (Reproducibility)**:
   - Quá trình phân chia sử dụng hạt ngẫu nhiên cố định `RANDOM_SEED = 42`.
   - Toàn bộ metadata chi tiết được lưu trữ tại [`split_metadata.json`](./split_metadata.json).
