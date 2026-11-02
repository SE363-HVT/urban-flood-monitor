# CẨM NANG BÍ QUYẾT GÁN NHÃN & KIỂM ĐỊNH DATASET ASTE CHUẨN NCKH QUỐC TẾ
> **Dự án**: Giám sát Ngập lụt Đô thị Thời gian thực TP.HCM (SE363 - Capstone & NCKH)  
> **Chuẩn dữ liệu**: SemEval ASTE-Data-V2 (Xu et al., EMNLP 2020)  
> **Mục tiêu**: Đạt độ chính xác tuyệt đối (Strict F1 $\ge 70\%$, Cohen's Kappa $\kappa \ge 0.70$) phục vụ công bố bài báo khoa học quốc tế.

---

## 🌟 I. TÔN CHỈ TỐI THƯỢNG CỦA CHUYÊN GIA

> ⚠️ **NGUYÊN TẮC BẤT DI BẤT DỊCH**:  
> *"ĐỌC HIỂU TRỌN VẸN TOÀN BỘ NGỮ CẢNH CÂU VĂN + TỪNG TỪ + TỪNG DẤU CÂU + TỪNG HASHTAG.  
> TUYỆT ĐỐI KHÔNG BẮT KEYWORD HỜI HỢT MÀ BỎ QUA NGỮ NGHĨA THỰC TẾ!"*

Khi đưa dữ liệu cho AI (Agent / LLM) hoặc người làm:
1. **Tuyệt đối không chạy ẩu hàng trăm mẫu cùng lúc**: Luôn chia nhỏ thành các lô **50 records / lần** để bộ nhớ ngữ cảnh (Context Window) luôn tập trung cao nhất, tránh ảo giác (hallucination) và bỏ sót lỗi.
2. **Luôn kiểm định lặp lại 10 vòng (10-Pass Audit)** trước khi chốt dữ liệu vào tập huấn luyện.

---

## 📐 II. CẤU TRÚC ĐỊNH DẠNG CHUẨN SEMEVAL ASTE-DATA-V2

Mỗi dòng dữ liệu phải tuân thủ nghiêm ngặt định dạng:
```text
token_0 token_1 ... token_n####[([aspect_indices], [opinion_indices], 'POLARITY'), ...]
```
* **Phân tách từ**: Tách chính xác bằng khoảng trắng đơn (`split()`).
* **Đánh số Index**: Bắt đầu từ `0`.
* **Cặp Triplet**: Bộ 3 phần tử gồm:
  - `aspect_indices`: Danh sách số nguyên tăng dần liên tục biểu thị vị trí của thực thể.
  - `opinion_indices`: Danh sách số nguyên tăng dần liên tục biểu thị vị trí của trạng thái.
  - `'POLARITY'`: Sắc thái cảm xúc, nhận một trong 3 giá trị: `'POS'`, `'NEG'`, hoặc `'NEU'`.
* **Mẫu bị loại bỏ (REJECT)**: Giữ nguyên câu văn bản gốc và gán triplet rỗng:
  ```text
  câu_văn_bản_gốc####[]
  ```
  *(Việc này bắt buộc để giữ số thứ tự dòng khớp 1:1 giữa hai người gán nhãn khi chạy script tính Cohen's Kappa).*

---

## 🎯 III. QUY CHUẨN VÀNG VỀ ASPECT (TARGET ENTITY)

Aspect là **Thực thể không gian, địa lý hoặc hạ tầng** chịu tác động của ngập lụt.

### 1. Các Aspect Hợp Lệ
* **Tên đường, tuyến hẻm**: `đường Nguyễn Văn Hưởng`, `Huỳnh Tấn Phát`, `Quốc lộ 50`, `Lê Văn Lương`.
* **Công trình giao thông & thủy lợi**: `cầu Bình Triệu`, `hầm chui An Phú`, `ngã tư Hàng Xanh`, `trạm bơm Thảo Điền`, `cống ngăn triều Mương Chuối`.
* **Thủy văn & nguồn nước**: `sông Sài Gòn`, `rạch Thủ Đức`, `kênh Nhiêu Lộc`, `nước`, `triều cường`, `mưa`.
* **Đơn vị hành chính**: `phường An Khánh`, `Bình Trị Đông`, `TP.HCM`, `Sài Gòn`.
* **Document Fallback**: Nếu bài viết phản ánh ngập tại TP.HCM nhưng không nhắc tên đường cụ thể, sử dụng tiền tố được bơm sẵn `Tại TP. Hồ Chí Minh ,` $\rightarrow$ Aspect là `TP. Hồ Chí Minh` (tokens `[1, 2, 3, 4]`).

### 2. Các Điều Cấm Kỵ Tuyệt Đối Về Aspect
1. ❌ **CẤM gán Phương tiện giao thông làm Aspect (`VEHICLE RULE`)**:
   - `xe máy`, `ô tô`, `xe buýt`, `xe tải` chỉ là **nạn nhân**, không phải hạ tầng bị ngập.
   - **Cách xử lý**: Bắt buộc chuyển Aspect sang tên con đường nơi phương tiện chết máy (Ví dụ: *"Đường Nguyễn Hữu Cảnh xe máy chết máy hàng loạt"* $\rightarrow$ Aspect là `Nguyễn Hữu Cảnh`, Opinion là `xe máy chết máy hàng loạt`).
2. ❌ **CẤM gán Con người / Vai trò làm Aspect**:
   - `người dân`, `tài xế`, `bà con`, `cụ bà`, `chị Oanh` không bao giờ là Aspect ngập lụt.
3. ❌ **CẤM dính giới từ vị trí ở đầu Aspect**:
   - Phải cắt sạch: *ở, tại, trên, dưới, trong, ngoài, từ, đến, gần, cạnh, bên, phía, thuộc, của*.
   - Ví dụ: `trên đường Lê Văn Việt` $\rightarrow$ Cắt bỏ `trên`, chỉ lấy `đường Lê Văn Việt`.
4. ❌ **CẤM lạm dụng DOC_FALLBACK khi câu có tên đường cụ thể (`DOC_FALLBACK_MISUSE`)**:
   - Nếu trong câu có nhắc tên đường riêng (ví dụ: `đường Huỳnh Tấn Phát`), tuyệt đối không được gán Aspect là `TP. Hồ Chí Minh`, mà phải gán trực tiếp vào tên đường.

---

## 💬 IV. QUY CHUẨN VÀNG VỀ OPINION (STATE / SENTIMENT EXPRESSION)

Opinion là **Cụm từ biểu đạt trạng thái vật lý, mức độ ngập lụt, hoặc hành vi ứng phó**.

### 1. Các Yêu Cầu Bắt Buộc
1. **Giữ trọn vẹn mức độ mô tả (Rich Descriptors & Severity)**:
   - Lấy đủ chiều sâu: `ngập sâu khoảng nửa mét`, `ngập lút bánh xe`, `nước tràn vào nhà`, `chết máy hàng loạt`.
   - Giữ lại từ phủ định (*không, chưa, vẫn chưa*), từ trạng thái (*đã, đang, bắt đầu*) và từ tăng tiến (*sml, kinh khủng, mênh mông*).
2. **Tuyệt đối cấm lấy cụm danh từ trơ trọi làm Opinion**:
   - ❌ Sai: `opinion: "điểm ngập"`, `opinion: "đoạn ngập"`, `opinion: "khu vực ngập"`.  
     *(Đây là danh từ chỉ vị trí, không phải vị ngữ trạng thái!)*
   -  Đúng: `opinion: "giải quyết điểm ngập"` hoặc `opinion: "ngập sâu"`.
3. **Cắt sạch dấu câu đứng độc lập ở rìa (Edge Punctuation Sanitation)**:
   - Nếu ở đầu hoặc cuối Opinion có dấu câu đứng lẻ (`?`, `!`, `,`, `.`, `:`), bắt buộc phải loại bỏ token dấu câu đó ra khỏi `opinion_indices`.
   - Ví dụ: `"Ngập Thế Này Sao ?"` $\rightarrow$ Cắt bỏ dấu `?`, chỉ lấy `"Ngập Thế Này Sao"`.
4. **Không ôm dấu ngoặc kép hoặc dấu giải thích**:
   - Rút gọn về cụm trạng thái cốt lõi: Thay vì lấy cả câu `ngập nặng , trở thành " biển nước " đen ngòm`, chỉ cần lấy chính xác `ngập nặng`.

---

## ⚖️ V. BỘ QUY TẮC PHÂN ĐỊNH POLARITY (THE LITMUS TEST)

Tuyệt đối không thấy chữ *"ngập"* là vội vàng đánh `NEG`! Phải đọc hiểu bản chất phát ngôn:

| Nhãn Polarity | Bản chất Ngữ nghĩa | Tiêu chí nhận diện thực tế | Ví dụ điển hình |
| :---: | :--- | :--- | :--- |
| **`POS`**<br>*(Tích cực / Phục hồi / Giải pháp)* | 1. **Nước rút, phục hồi**: Đường khô ráo, giao thông thông thoáng.<br>2. **Dự án / Công trình chống ngập**: Nạo vét, xây kè, khơi thông cống rãnh, giải quyết dứt điểm ngập.<br>3. **Khen ngợi**: Trạm bơm chạy tốt, CSGT giúp dân vượt ngập. | Xuất hiện: *nước bắt đầu rút, rút sạch, hết ngập, khô ráo, thông thoáng, giải quyết ngập, chống ngập triệt để, nạo vét, tăng năng lực thoát nước, bờ bao gia cố*. | • *"khi nước bắt đầu rút"* $\rightarrow$ `POS`<br>• *"đường Trần Xuân Soạn không còn bị ngập"* $\rightarrow$ `POS`<br>• *"giải quyết căn cơ tình trạng ngập"* $\rightarrow$ `POS`<br>• *"hỗ trợ người dân đưa xe qua đoạn ngập"* $\rightarrow$ `POS` |
| **`NEU`**<br>*(Trung tính / Dự báo / Đo lường)* | 1. **Đo đạc thủy văn**: Báo cáo mực nước sông, đỉnh triều kỹ thuật khách quan.<br>2. **Dự báo thời tiết & Khuyến cáo rủi ro**: Cảnh báo nguy cơ (chưa xảy ra thực tế).<br>3. **Câu hỏi thăm dò / Tu từ**: Hỏi tình hình, thắc mắc thông số. | Xuất hiện: *đang ở mức cao, dự báo đạt 1m70, có nguy cơ ngập sâu, khuyến cáo hạn chế di chuyển, triều cường chưa đạt đỉnh, mưa bao nhiêu mm thì ngập?*. | • *"triều cường trên sông Sài Gòn đang ở mức cao"* $\rightarrow$ `NEU`<br>• *"dự báo biến đổi chậm"* $\rightarrow$ `NEU`<br>• *"có nguy cơ ngập sâu"* $\rightarrow$ `NEU`<br>• *"Đoạn này ngập chưa mọi người?"* $\rightarrow$ `NEU` |
| **`NEG`**<br>*(Tiêu cực / Tê liệt / Ngập úng)* | 1. **Hiện trường ngập lụt thực tế**: Nước ngập đường, ngập vào nhà dân.<br>2. **Ách tắc & Hư hại**: Xe chết máy, dắt bộ, tê liệt giao thông, sinh hoạt đảo lộn. | Xuất hiện: *ngập sâu khoảng nửa mét, nước dâng ngập mặt đường, xe chết máy, bì bõm, nước tràn vào nhà, ngập lênh láng, kẹt xe*. | • *"ngập sâu khoảng nửa mét"* $\rightarrow$ `NEG`<br>• *"nước tràn vào nhà"* $\rightarrow$ `NEG`<br>• *"dòng xe bì bõm nhích từng mét"* $\rightarrow$ `NEG`<br>• *"hàng loạt xe chết máy"* $\rightarrow$ `NEG` |

---

## 🚫 VI. BỘ LỌC THANH LỌC DỮ LIỆU RÁC & NGOÀI TP.HCM (`REJECT`)

Khi cào dữ liệu từ mạng xã hội (TikTok / Facebook), crawler thường tìm theo hashtag chung (`#ngaplut`, `#trieucuong`) rồi tự động dán tiền tố `"Tại TP. Hồ Chí Minh ,"`. Phải đọc kỹ nội dung và hashtag để phát hiện và gán **`####[]`**:

1. **Ngập lụt ở các Tỉnh/Thành khác**:
   * Cần Thơ: `#cantho`, `#65cầnthơ`, `#chợbìnhthủy`, `đường Nguyễn Văn Cừ (NVC)`.
   * Hà Nội: `#hanoi`, `#hanoimua`, `Chương Mỹ`, `Tứ Liên`, app `iHaNoi`.
   * Cà Mau: `#camau`, `#càmau`, `#reviewcamau`.
   * Đồng Nai: `Đèo Mẹ Bồng Con`, `Vĩnh Thanh`, `#dongnai`, `#longkhanh`.
   * Sa Đéc - Đồng Tháp: `#sadec`, `#sadectv`.
   * Vĩnh Long, Miền Tây: `#vinhlong`, `#mientay`.
   * Nước ngoài: `Thái Lan`, `Bangkok`.
2. **Nội dung Phi Ngập lụt Đô thị / Ẩn dụ / Thương mại**:
   * Câu cá, bắt cá đồng mùa nước nổi (`#cathiennhien`, `#đammêcâucá`).
   * Tranh luận triết lý, chính trị vô thưởng vô phạt (*"lượng mưa lớn thì nước nào mà chẳng ngập"*).
   * Rao vặt thương mại, cho thuê phòng trọ có giá tiền (`Huỳnh Tấn Phát 1tr8 phòng trọ...`).
   * Dùng từ ngập theo nghĩa bóng (*ngập tràn ánh sáng, ngập tràn niềm vui, ngập tràn ưu đãi*).

---

## 🛠️ VII. BỘ CÔNG CỤ SCRIPT KIỂM ĐỊNH TỰ ĐỘNG CÓ SẴN TRONG REPO

Để phục vụ cho Phase 2 và Phase 3, các script sau đã được đóng gói hoàn chỉnh:

1. [`scripts/deep_10_pass_audit.py`](file:///D:/SE363_RAWDATA/scripts/deep_10_pass_audit.py):
   * Chạy **10 vòng kiểm định lặp đi lặp lại** quét toàn bộ các lỗi: Range Index, Overlap, Giới từ, Dấu câu, Phương tiện, Con người, Tỉnh ngoài, Polarity, DOC_FALLBACK, Cấu trúc cú pháp.
2. [`scripts/audit_index_integrity.py`](file:///D:/SE363_RAWDATA/scripts/audit_index_integrity.py):
   * Tự động giải mã ngược (Reverse-reconstruction) toàn bộ các cặp số index ra chuỗi từ vựng thực tế để bảo đảm **độ chính xác 100% từng chữ và từng ký tự**.
3. [`scripts/verify_batch_50.py`](file:///D:/SE363_RAWDATA/scripts/verify_batch_50.py):
   * Công cụ chia nhỏ dữ liệu thành các lô **50 records / lần** để kiểm định cuốn chiếu.

---

## 🚀 VIII. HƯỚNG DẪN TRIỂN KHAI CHO CÁC PHASE TIẾP THEO

* **Phase 2 (Overlap 2.000 records: 501 ➔ 2.500)**:
  - Cả bạn (Thuận) và bạn Hùng làm **độc lập 100%** không trao đổi.
  - Sử dụng cẩm nang này và chạy các script trên để đảm bảo tập nhãn của bạn chuẩn xác tuyệt đối.
  - Sau khi nộp, chạy script tính Cohen's Kappa để lấy số liệu $\ge 0.70$ đưa vào bài báo.
* **Phase 3 (Về đích: Thuận làm từ 6.251 ➔ 10.249)**:
  - Chia nhỏ thành từng lô 50 mẫu, áp dụng triệt để bộ lọc rác tỉnh ngoài và cẩm nang này để hoàn tất toàn bộ Master Dataset.
