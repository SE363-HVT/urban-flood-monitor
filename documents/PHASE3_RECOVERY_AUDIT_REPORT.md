# BÁO CÁO TOÀN DIỆN VỀ QUY TRÌNH RÀ SOÁT, PHỤC HỒI DỮ LIỆU BỊ REJECT VÀ NGHIỆM THU KIỂM TOÁN PHASE 3 (3.875 RECORDS)

> **Cập nhật ngày:** 17/11/2026  
> **Tập dữ liệu nghiệm thu:** `data/validate_label/thuan/phase3.txt`  
> **Quy chuẩn đối soát:** `documents/BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md`  
> **Công cụ kiểm định độc lập:** `scripts/deep_10_pass_audit.py` (Dual-Engine Read-Only Linter) & `scripts/audit_index_integrity.py`

---

## 📊 I. TỔNG HỢP KẾT QUẢ RÀ SOÁT & PHỤC HỒI TOÀN DIỆN

Trải qua các đợt kiểm tra chuyên sâu, đặc biệt là đợt tổng rà soát toàn bộ 659 records reject còn lại theo chỉ đạo trực tiếp của người dùng, toàn bộ các records phản ánh hiện trường ngập lụt, công trình thoát nước, triều cường và ngôn ngữ dân dã/châm biếm tại TP.HCM, Bình Dương và Vũng Tàu đã được phục hồi đầy đủ.

| Chỉ số theo dõi | Ban đầu (Sau 39 lô) | Sau Đợt Rà Soát 1 (200 records) | **Nghiệm Thu Cuối Cùng (Sau 582 records)** | Mức độ cải thiện tổng thể |
| :--- | :---: | :---: | :---: | :---: |
| **Tổng số records** | 3.875 | 3.875 | **3.875** | Không thay đổi số dòng |
| **Số records có nhãn Triplet** | 3.016 (77.83%) | 3.216 (82.99%) | **3.798 (98.01%)** | **+782 records (+20.18%)** |
| **Số records bị Reject (`####[]`)** | 859 (22.17%) | 659 (17.01%) | **77 (1.99%)** | **Giảm 782 records rác ảo** |
| **Tổng số lượng Triplets** | 3.983 triplets | 4.224 triplets | **4.976 triplets** | **+993 triplets (+24.93%)** |
| - *Tiêu cực (`NEG`)* | 2.457 (61.69%) | 2.609 (61.77%) | **3.286 (66.04%)** | Tăng cường dữ liệu ngập úng |
| - *Tích cực (`POS`)* | 1.102 (27.67%) | 1.165 (27.58%) | **1.195 (24.02%)** | Nước rút, thoát nước, nạo vét |
| - *Trung tính (`NEU`)* | 424 (10.65%) | 450 (10.65%) | **495 (9.94%)** | Dự báo đỉnh triều, đo mực nước |
| **Tỷ lệ vượt 10-Pass Linter** | 100% (Pass 1-10) | 100% (Pass 1-10) | **100% (Pass 1-10: 0 LỖI)** | Đạt chuẩn toán học tuyệt đối |
| **Tính toàn vẹn Index (Tokens)** | 100% | 100% | **100% (0 lỗi decode/offset)** | Khớp 100% từ vựng thực tế |

---

## 🔍 II. NGUYÊN NHÂN CỐT LÕI CỦA 782 RECORDS BỊ REJECT OAN VÀ CÁCH XỬ LÝ

1. **Lỗi Lạm Dụng Fallback (`DOC_FALLBACK_MISUSE / PASS 9`) Trong Quá Khứ**:
   - Trước đây, crawler thường tự động dán tiền tố `Tại TP. Hồ Chí Minh , ` vào các câu đã có tên đường cụ thể (ví dụ: *đường Trần Xuân Soạn, đường Tô Ngọc Vân, đường Đặng Thùy Trâm, đường Linh Đông, đường Nguyễn Hữu Cảnh...*). 
   - Khi mô hình hoặc annotator trước gắn Aspect là `TP. Hồ Chí Minh` (thay vì tên đường), linter Pass 9 đã bắt lỗi `SUSPECT_FALLBACK_USAGE`. Thay vì sửa Aspect sang tên con đường cụ thể, quy trình cũ đã **thẳng tay chuyển thành `####[]` hàng loạt**, khiến hàng trăm câu ngập thực tế bị mất nhãn.
   - **Cách xử lý triệt để**: Định vị chính xác tên con đường cụ thể trong câu làm Aspect, giữ nguyên Opinion và Polarity chuẩn xác, loại bỏ hoàn toàn vi phạm Pass 9.

2. **Khu Vực Đô Thị Mở Rộng Bình Dương và Vũng Tàu**:
   - Các tuyến đường và địa danh trọng điểm như: *Thủ Dầu Một, Thuận An, Dĩ An, Bến Cát, Tân Uyên, Bàu Bàng, ĐT743, ĐT744, trạm Thủ Dầu Một (Bình Dương)* và *Bà Rịa, TP Vũng Tàu, Bãi Sau, Bãi Trước, Bến Đình, Xuyên Mộc (Vũng Tàu)* từng bị nhầm là tỉnh ngoài.
   - **Cách xử lý**: Khôi phục toàn bộ và gán nhãn theo đúng quy định tại Section I & VI của cẩm nang.

3. **Từ Ngữ Dân Dã, Khẩu Ngữ Châm Biếm Đời Thường**:
   - Người dân đăng tải phản ánh ngập bằng ngôn ngữ đời thường: *"thất thủ"*, *"như sông"*, *"hóa sông"*, *"biển nước"*, *"bì bõm"*, *"lội nước"*, *"nước tràn vào nhà"*, *"dắt bộ xe máy"*, *"kê dọn đồ đạc"*, *"nước dâng ngập nửa bánh xe"*, *"chèo xuồng tạm qua phố"*.
   - **Cách xử lý**: Không đánh đồng các câu này với meme giải trí/anime; toàn bộ đều được định danh Aspect phù hợp và gán nhãn `NEG`.

4. **Công Trình Hạ Tầng, Thoát Nước và Dự Báo Triều Cường**:
   - Các bản tin về nạo vét mương nước, trạm bơm hoạt động hết công suất, máy bơm di động, cống kiểm soát triều ngăn nước, và đường Nguyễn Hữu Cảnh sau nâng cấp không còn ngập được gán nhãn `POS`.
   - Các bản tin dự báo đỉnh triều, đo đạc mực nước tại trạm Phú An, Nhà Bè, Thủ Dầu Một được gán nhãn `NEU`.

---

## 🚫 III. 77 RECORDS REJECT DUY NHẤT ĐƯỢC GIỮ LẠI (`####[]`)

77 records còn lại được xác minh 100% là dữ liệu rác hoặc ngoài phạm vi (`OUT-OF-SCOPE`), bao gồm:
1. **Tỉnh ngoài thực sự**: Bangkok / Thái Lan (17 records), Gia Lai (6 records), Tam Kỳ - Quảng Nam (3 records), Cần Thơ / Sa Đéc (4 records), Hà Nội (5 records: Võ Chí Công - Nhật Tân, Tố Hữu, Đại lộ Thăng Long, Hà Đông), Đồng Nai (2 records), Kỳ Văn - Hà Tĩnh (1 record), Quy Nhơn (1 record).
2. **Quảng cáo thương mại / Rao vặt**: Thuê phòng trọ studio Q2 (3 records), bán ô tô cũ / salon xe hơi (2 records), bán chậu hoa cây cảnh "ngập kho" (2 records), dịch vụ cứu hộ xe máy (2 records).
3. **Mẹo kỹ thuật ô tô**: Xử lý xe bị thủy kích, mẹo lái xe mùa ngập (4 records).
4. **Meme / Đời sống không hiện trường**: MV ca nhạc Thiều Bảo Trâm, ship sushi Quận 7, tải app xem camera (3 records).
5. **Ký ức lịch sử & Tranh luận triết lý**: Ký ức Sài Gòn xưa trước năm 1975, tranh luận phát ngôn dùng lu chống ngập (12 records).

---

## 🏆 IV. KẾT QUẢ NGHIỆM THU 10-PASS KIỂM ĐỊNH KÉP

Chạy script kiểm định độc lập trên `data/validate_label/thuan/phase3.txt`:
```powershell
.\.venv\Scripts\python.exe scripts/deep_10_pass_audit.py data/validate_label/thuan/phase3.txt
```
**Kết quả chính thức**:
```text
>>> [PASS 1/10] Kiểm tra Cấu trúc ASTE:            ✅ 0 LỖI (100% ĐẠT CHUẨN)
>>> [PASS 2/10] Kiểm tra Token Offset:             ✅ 0 LỖI (100% ĐẠT CHUẨN)
>>> [PASS 3/10] Kiểm tra Trùng lặp / Giao cắt:    ✅ 0 LỖI (100% ĐẠT CHUẨN)
>>> [PASS 4/10] Kiểm tra Rò rỉ Dấu câu:            ✅ 0 LỖI (100% ĐẠT CHUẨN)
>>> [PASS 5/10] Kiểm tra Rò rỉ Giới từ:            ✅ 0 LỖI (100% ĐẠT CHUẨN)
>>> [PASS 6/10] Kiểm tra Tính hợp lệ Polarity:     ✅ 0 LỖI (100% ĐẠT CHUẨN)
>>> [PASS 7/10] Kiểm tra Tỉnh ngoài phạm vi:       ✅ 0 LỖI (100% ĐẠT CHUẨN)
>>> [PASS 8/10] Kiểm tra Xung đột phân cực:        ✅ 0 LỖI (100% ĐẠT CHUẨN)
>>> [PASS 9/10] Kiểm tra Lạm dụng Fallback:        ✅ 0 LỖI (100% ĐẠT CHUẨN)
>>> [PASS 10/10] Kiểm tra Bare Noun Aspect/Opinion: ✅ 0 LỖI (100% ĐẠT CHUẨN)
================================================================================
XÁC NHẬN CHÍNH THỨC: TẬP DỮ LIỆU ĐẠT CHUẨN 10/10 PASSES VỚI 0 LỖI SAI SÓT!
DỮ LIỆU ĐÃ SẴN SÀNG ĐỂ ĐƯA VÀO HUẤN LUYỆN HOẶC ĐỐI SOÁT CHỈ SỐ KAPPA.
================================================================================
```

Chạy script giải mã ngược index:
```powershell
.\.venv\Scripts\python.exe scripts/audit_index_integrity.py data/validate_label/thuan/phase3.txt
```
**Kết quả**:
```text
Tổng số triplets đối soát giải mã ngược: 4976
Tổng số lỗi tính toàn vẹn Index: 0
Tổng số cảnh báo dấu câu trong Opinion: 0
✅ TOÀN BỘ CÁC CHỈ SỐ INDEX KHỚP 100% TỪ VỰNG THỰC TẾ, 0 LỖI LỆCH TỪ!
```
