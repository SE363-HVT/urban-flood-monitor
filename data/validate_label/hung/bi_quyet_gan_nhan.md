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
* **Thủy văn & nguồn nước**: `sông Sài Gòn`, `rạch Thủ Đức`, `kênh Nhiêu Lộc`, `nước`, `triều cường ở TPHCM`, `mưa`.
* **Đơn vị hành chính**: `phường An Khánh`, `Bình Trị Đông`, `TP.HCM`, `Sài Gòn`, bao gồm cả các khu vực đô thị mở rộng/giáp ranh như Bình Dương (`Thủ Dầu Một`, `Thuận An`, `Dĩ An`, `Bến Cát`) và Vũng Tàu (`Bà Rịa - Vũng Tàu`).
* **Document Fallback**: Nếu bài viết phản ánh ngập tại TP.HCM nhưng không nhắc tên đường cụ thể, sử dụng tiền tố được bơm sẵn `Tại TP. Hồ Chí Minh ,` $\rightarrow$ Aspect là `TP. Hồ Chí Minh` (tokens `[1, 2, 3, 4]`) hoặc `Tại TPHCM ,` $\rightarrow$ Aspect là `TPHCM` (token `[1]`).

### 2. Các Điều Cấm Kỵ & Quy Tắc Chuẩn Hóa Aspect Mới Nhất
1. ❌ **CẤM gán Phương tiện giao thông làm Aspect (`VEHICLE RULE`)**:
   - `xe máy`, `ô tô`, `xe buýt`, `xe tải`, `phương tiện` chỉ là **nạn nhân / đối tượng lưu thông**, không phải hạ tầng bị ngập.
   - **Cách xử lý**: Bắt buộc chuyển Aspect sang tên con đường nơi phương tiện chết máy, hoặc fallback về `TPHCM`.
2. ❌ **CẤM gán Con người / Vai trò làm Aspect (`PEOPLE ROLE`)**:
   - `người dân`, `tài xế`, `bà con`, `cụ bà`, `chị Oanh`, `lực lượng chức năng`, `CSGT` không bao giờ là Aspect ngập lụt.
3. ❌ **CẤM dính giới từ vị trí ở đầu Aspect (`PREPOSITION LEAKAGE`)**:
   - Phải cắt sạch: *ở, tại, trên, dưới, trong, ngoài, từ, đến, gần, cạnh, bên, phía, thuộc, của*.
   - Ví dụ: `trên đường Lê Văn Việt` $\rightarrow$ Cắt bỏ `trên`, chỉ lấy `đường Lê Văn Việt`.
4. ❌ **CẤM lạm dụng DOC_FALLBACK khi câu có tên đường cụ thể (`DOC_FALLBACK_MISUSE / PASS 9`)**:
   - Nếu trong câu có nhắc tên đường riêng (ví dụ: `đường Huỳnh Tấn Phát`, `đường Võ Văn Ngân`, `đường Trần Xuân Soạn`, `đường Tam Bình`), tuyệt đối KHÔNG ĐƯỢC dùng Fallback `TPHCM`, mà bắt buộc phải gán trực tiếp vào tên đường.
5. ❌ **CẤM gán các danh từ chỉ hạ tầng chung chung làm Aspect**:
   - `mặt đường`, `đoạn đường`, `con đường`, `chân cầu`, `cư xá`, `làn nước ngập`, `nâng nền`, `dòng nước` **KHÔNG ĐƯỢC** làm Aspect trơ trọi.
   - **Cách xử lý cho tin POS, NEG thiếu địa danh cụ thể**:
     + Bổ sung tiền tố `Tại TPHCM , ` vào ngay đầu câu văn bản gốc.
     + Gán Aspect là `TPHCM` (token `[1]`).
     + Toàn bộ chỉ số Opinion phía sau sẽ tịnh tiến tương ứng `+3` tokens.
6. 🌊 **Quy tắc vàng Aspect Triều cường / Đỉnh triều (Tin `NEU` / `NEG`)**:
   - Tuyệt đối không để chữ `triều cường` hoặc `đỉnh triều` hoặc `triều cao` trơ trọi một mình làm Aspect (vì vi phạm bản chất địa lý không gian của ASTE).
   - **Cách xử lý**: Bổ sung trực tiếp tại chỗ (in-place) vào text thành `triều cường ở TPHCM` (hoặc `đỉnh triều ở TPHCM`, `triều cao ở TPHCM`).
   - Sau đó gán trọn vẹn cụm 4 token này làm Aspect: `aspect_indices: [i, i+1, i+2, i+3]`.
7. 🚫 **Quy tắc Tránh Đa gán nhãn Trùng lặp (Anti Over-tagging / Multi-level Duplication)**:
   - Khi một câu xuất hiện cả tên đường cụ thể lẫn địa danh bao trùm (ví dụ: `đường Trần Xuân Soạn ( TPHCM )` hoặc `đường Phan Huy Ích ( phường Tân Sơn , TP. HCM )`):
     + **CHỈ gán Aspect duy nhất** cho thực thể cụ thể nhất (`đường Trần Xuân Soạn` hoặc `đường Phan Huy Ích`).
     + **KHÔNG** gán thêm `TPHCM` hay `phường Tân Sơn` cho cùng một vị ngữ trạng thái ngập lụt để tránh tạo ra các triplet trùng lặp làm méo mó trọng số mô hình.

---

## 💬 IV. QUY CHUẨN VÀNG VỀ OPINION (STATE / SENTIMENT EXPRESSION)

Opinion là **Cụm từ biểu đạt trạng thái vật lý, mức độ ngập lụt, hoặc hành vi ứng phó**.

### 1. Các Yêu Cầu Bắt Buộc
1. **Giữ trọn vẹn mức độ mô tả (Rich Descriptors & Severity)**:
   - Lấy đủ chiều sâu: `ngập sâu khoảng nửa mét`, `ngập lút bánh xe`, `nước tràn vào nhà`, `chết máy hàng loạt`.
   - Giữ lại từ phủ định (*không, chưa, vẫn chưa*), từ trạng thái (*đã, đang, bắt đầu*) và từ tăng tiến (*sml, kinh khủng, mênh mông*).
2. **Tuyệt đối cấm lấy cụm danh từ trơ trọi làm Opinion (`BARE_NOUN_AS_OPINION / PASS 10`)**:
   - ❌ Sai: `opinion: "điểm ngập"`, `opinion: "đoạn ngập"`, `opinion: "khu vực ngập"`.  
     *(Đây là danh từ chỉ vị trí, không phải vị ngữ trạng thái!)*
   -  Đúng: `opinion: "giải quyết điểm ngập"` hoặc `opinion: "ngập sâu"`.
3. **Cắt sạch dấu câu đứng độc lập ở rìa (Edge Punctuation Sanitation / PASS 4)**:
   - Nếu ở đầu hoặc cuối Opinion có dấu câu đứng lẻ (`?`, `!`, `,`, `.`, `:`), bắt buộc phải loại bỏ token dấu câu đó ra khỏi `opinion_indices`.
   - Ví dụ: `"Ngập Thế Này Sao ?"` $\rightarrow$ Cắt bỏ dấu `?`, chỉ lấy `"Ngập Thế Này Sao"`.
4. **Không ôm dấu ngoặc kép hoặc dấu giải thích**:
   - Rút gọn về cụm trạng thái cốt lõi: Thay vì lấy cả câu `ngập nặng , trở thành " biển nước " đen ngòm`, chỉ cần lấy chính xác `ngập nặng`.
5. **Cắt bỏ động từ nguyên nhân đứng trước trạng thái ngập (`CAUSATIVE_VERB_STRIPPING`)**:
   - Khi câu xuất hiện các từ chỉ nguyên nhân như `gây`, `làm`, `gây ra` đứng ngay trước `ngập` / `ngập úng` / `tăng nguy cơ ngập`:
     + `gây ngập` $\rightarrow$ rút gọn thành `ngập`.
     + `làm ngập 0,2 - 1m` $\rightarrow$ rút gọn thành `ngập 0,2 - 1m`.
     + `gây ngập sâu` $\rightarrow$ rút gọn thành `ngập sâu`.
     + `gây ra ngập úng` $\rightarrow$ rút gọn thành `ngập úng`.
     + `làm tăng nguy cơ ngập` $\rightarrow$ rút gọn thành `tăng nguy cơ ngập`.
   - Giúp Opinion thể hiện trực diện tình trạng ngập lụt thực tế, ngắn gọn, súc tích và dễ hiểu cho mô hình ASTE.
6. 🌊 **Quy chuẩn về Dấu Phẩy `,` trong Opinion (Liên kết Ngữ cảnh & Mức độ mô tả)**:
   - **Được phép giữ dấu phẩy `,` ở GIỮA Opinion**: Khi dấu phẩy nối liền các vế câu mô tả liên tục tính chất, mức độ nghiêm trọng và hậu quả thực tế của sự việc (ví dụ: `ngập sâu , người dân chật vật di chuyển`, `nước đã dâng lút bánh xe , chảy xiết`, `ngập sâu , hàng loạt xe tắt máy , người dân bì bõm lội nước về nhà`). Việc giữ trọn vẹn ngữ cảnh này giúp mô hình nắm bắt đầy đủ độ sâu mô tả (Rich Context & Severity).
   - **Tuyệt đối CẤM dính dấu câu thừa ở ĐẦU hoặc CUỐI Opinion (Edge Punctuation Sanitation / Pass 4)**: Dấu phẩy `,`, dấu chấm `.`, dấu hai chấm `:`, dấu chấm than `!`, dấu hỏi `?`, emoji đứng độc lập ở rìa span (đầu hoặc cuối) bắt buộc phải cắt bỏ sạch sẽ để tránh làm span bị cụt hoặc rò rỉ cú pháp.
   - 🛑 **Quy tắc Điểm Dừng Ngữ Nghĩa (Semantic Boundary Guards)**: Khi mở rộng vị ngữ qua dấu phẩy, **bắt buộc phải dừng lại** trước các trường hợp sau để tránh gom nhầm thông tin:
     + **Dừng trước lời dẫn trích dẫn nhân vật**: `... cho biết`, `... chia sẻ`, `theo ông...`.
     + **Dừng trước dấu ngoặc kép `"`, hai chấm `:`, ba chấm `…`**.
     + **Dừng trước khuyến cáo/chính sách hành chính**: `các trường chủ động cho học sinh nghỉ`, `lực lượng chức năng phong tỏa...`.
     + **Dừng trước metadata ảnh/nguồn/mốc thời gian ở đuôi**: `( Ảnh : ...)`, `( Nguồn : ...)`, `, tối 22 / 9`.
     + **Tuyệt đối không bao trùm Aspect (Anti-Overlap)**: Opinion mở rộng không bao giờ được chạm hoặc lấn vào vị trí index của Aspect trong câu.
---

## ⚖️ V. BỘ QUY TẮC PHÂN ĐỊNH POLARITY (THE LITMUS TEST)

Tuyệt đối không thấy chữ *"ngập"* là vội vàng đánh `NEG`! Phải đọc hiểu bản chất phát ngôn:

| Nhãn Polarity | Bản chất Ngữ nghĩa | Tiêu chí nhận diện thực tế | Ví dụ điển hình |
| :---: | :--- | :--- | :--- |
| **`POS`**<br>*(Tích cực / Phục hồi / Giải pháp)* | 1. **Nước rút, phục hồi**: Đường khô ráo, giao thông thông thoáng.<br>2. **Dự án / Công trình chống ngập**: Nạo vét, xây kè, khơi thông cống rãnh, giải quyết dứt điểm ngập.<br>3. **Khen ngợi**: Trạm bơm chạy tốt, CSGT giúp dân vượt ngập. | Xuất hiện: *nước bắt đầu rút, rút sạch, hết ngập, khô ráo, thông thoáng, giải quyết ngập, chống ngập triệt để, nạo vét, tăng năng lực thoát nước, bờ bao gia cố*. | • *"khi nước bắt đầu rút"* $\rightarrow$ `POS`<br>• *"đường Trần Xuân Soạn không còn bị ngập"* $\rightarrow$ `POS`<br>• *"giải quyết căn cơ tình trạng ngập"* $\rightarrow$ `POS`<br>• *"hỗ trợ người dân đưa xe qua đoạn ngập"* $\rightarrow$ `POS` |
| **`NEU`**<br>*(Trung tính / Dự báo / Đo lường)* | 1. **Đo đạc thủy văn**: Báo cáo mực nước sông, đỉnh triều kỹ thuật khách quan.<br>2. **Dự báo thời tiết & Khuyến cáo rủi ro**: Cảnh báo nguy cơ (chưa xảy ra thực tế).<br>3. **Câu hỏi thăm dò / Tu từ**: Hỏi tình hình, thắc mắc thông số. | Xuất hiện: *đang ở mức cao, dự báo đạt 1m70, có nguy cơ ngập sâu, khuyến cáo hạn chế di chuyển, triều cường chưa đạt đỉnh, mưa bao nhiêu mm thì ngập?*. | • *"triều cường ở TPHCM đang ở mức cao"* $\rightarrow$ `NEU`<br>• *"dự báo biến đổi chậm"* $\rightarrow$ `NEU`<br>• *"có nguy cơ ngập sâu"* $\rightarrow$ `NEU`<br>• *"Đoạn này ngập chưa mọi người?"* $\rightarrow$ `NEU` |
| **`NEG`**<br>*(Tiêu cực / Tê liệt / Ngập úng)* | 1. **Hiện trường ngập lụt thực tế**: Nước ngập đường, ngập vào nhà dân.<br>2. **Ách tắc & Hư hại**: Xe chết máy, dắt bộ, tê liệt giao thông, sinh hoạt đảo lộn. | Xuất hiện: *ngập sâu khoảng nửa mét, nước dâng ngập mặt đường, xe chết máy, bì bõm, nước tràn vào nhà, ngập lênh láng, kẹt xe*. | • *"ngập sâu khoảng nửa mét"* $\rightarrow$ `NEG`<br>• *"nước tràn vào nhà"* $\rightarrow$ `NEG`<br>• *"dòng xe bì bõm nhích từng mét"* $\rightarrow$ `NEG`<br>• *"hàng loạt xe chết máy"* $\rightarrow$ `NEG` |

---

## 🚫 VI. BỘ LỌC THANH LỌC DỮ LIỆU RÁC & NGOÀI PHẠM VI (`REJECT`)

Khi cào dữ liệu từ mạng xã hội (TikTok / Facebook), crawler thường tìm theo hashtag chung (`#ngaplut`, `#trieucuong`) rồi tự động dán tiền tố `"Tại TP. Hồ Chí Minh ,"`. Annotator và Agent bắt buộc phải đọc kỹ toàn bộ ngữ cảnh, văn bản và hashtag để phân loại chuẩn xác:

### 1. Phân định Ranh giới Địa lý (Geographic Scope)
* **KHU VỰC HỢP LỆ (IN-SCOPE - Bắt buộc giữ lại và gán nhãn)**:
  - Toàn bộ các quận, huyện, thành phố thuộc TP.HCM (Quận 1 - 12, TP. Thủ Đức, Gò Vấp, Bình Thạnh, Tân Bình, Bình Tân, Hóc Môn, Bình Chánh, Nhà Bè, Củ Chi, Cần Giờ).
  - Các khu vực thuộc vùng đô thị liên kết / sáp nhập kinh tế - không gian:
    + **Bình Dương**: *Thủ Dầu Một, Thuận An, Dĩ An, Bến Cát, Tân Uyên, KCN VSIP*.
    + **Vũng Tàu**: *Thành phố Vũng Tàu, Bà Rịa - Vũng Tàu*.
* **CÁC TỈNH NGOÀI PHẠM VI (OUT-OF-SCOPE - Bắt buộc gán `REJECT (####[])`)**:
  - Tuyệt đối loại bỏ các bản tin từ tỉnh thành khác dù crawler có gán nhầm tiền tố TP.HCM:
    + **Hà Nội**: `#hanoi`, `#hanoimua`, `Chương Mỹ`, `Tứ Liên`, `Hoàng Mai`, `Thanh Xuân`, `Hà Đông`, `ngã 4 văn phú`, app `iHaNoi`.
    + **Cần Thơ**: `#cantho`, `#65cầnthơ`, `#chợbìnhthủy`, `đường Nguyễn Văn Cừ (NVC)`.
    + **Đồng Nai**: `đèo Mẹ Bồng Con`, `Vĩnh Thanh`, `#dongnai`, `#longkhanh`, `Dầu Giây`.
    + **Miền Tây & ĐBSCL**: `Cà Mau` (`#camau`), `Đồng Tháp` / `Sa Đéc` (`#sadec`), `Vĩnh Long`, `Bến Tre`, `Trà Vinh`, `An Giang`, `Kiên Giang`.
    + **Miền Trung & Tây Nguyên**: `Gia Lai`, `Quy Nhơn`, `Nha Trang`, `Đà Lạt`, `Lâm Đồng`, `Đà Nẵng`, `Huế`.
    + **Nước ngoài**: `Thái Lan`, `Bangkok`, `Trung Quốc`.

### 2. Nội dung Phi Ngập lụt Đô thị / Quảng cáo Thương mại (Bắt buộc `####[]`)
* **Quảng cáo thương mại / Rao vặt**:
  - Showroom mua bán ô tô cũ/mới (ví dụ: *#otochutin, #toantrung, tranh luận ngập nước định giá xe*).
  - Bán cửa chống ngập, bán bạt chắn nước (*"Khách nhà em mãi đỉnh"*).
  - Môi giới bất động sản, rao thuê phòng trọ (*"Nhà hẻm Nguyễn Xí có ngập như lời đồn #bds"*).
* **Nội dung đời sống giải trí / Ẩn dụ**:
  - Câu cá, giăng lưới mùa nước nổi (`#cathiennhien`, `#đammêcâucá`).
  - Tranh luận triết lý, chém gió không địa chỉ thực tế (*"lượng mưa lớn thì nước nào mà chẳng ngập"*).
  - Từ ngữ ẩn dụ: *ngập tràn xe mới, ngập tràn niềm vui, ngập tràn ưu đãi*.

---

## 🛠️ VII. KIẾN TRÚC KIỂM ĐỊNH KÉP (DUAL-ENGINE AUDIT) & BỘ CÔNG CỤ SCRIPT TỰ ĐỘNG

Nhằm giải quyết triệt để mối lo ngại về việc script tự động có thể hiểu sai ngữ cảnh gây lệch lạc dữ liệu, hệ thống áp dụng **Kiến trúc Kiểm định Kép (Dual-Engine)** phân định ranh giới trách nhiệm rõ ràng:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   KIẾN TRÚC KIỂM ĐỊNH KÉP (DUAL-ENGINE)                │
└────────────────────────────────────────────────────────────────────────┘
          │                                              │
          ▼                                              ▼
┌──────────────────────────────────┐   ┌──────────────────────────────────┐
│   ENGINE 1: CHUYÊN GIA / AGENT   │   │     ENGINE 2: SCRIPT AUDITOR     │
│   (Semantic Reasoning Engine)    │   │  (Mathematical & Linting Engine) │
├──────────────────────────────────┤   ├──────────────────────────────────┤
│ • Đọc hiểu trọn vẹn ngữ cảnh.    │   │ • 100% READ-ONLY (Không sửa file)│
│ • Phân định POS / NEG / NEU.     │   │ • Đối soát toán học Span Index.  │
│ • Nhận diện địa danh TP.HCM.     │   │ • Phát hiện rò rỉ giới từ/dấu câu│
│ • Đánh giá mẫu giáp ranh/ẩn dụ.  │   │ • Giải mã ngược (Reconstruction) │
└──────────────────────────────────┘   └──────────────────────────────────┘
```

### 1. Cam Kết An Toàn Tuyệt Đối: "Strictly Read-Only Auditor"
* **Không bao giờ tự ý sửa file nhãn**: Các script kiểm định tuyệt đối **KHÔNG có bất kỳ hàm `write()` hay `dump()` nào** lên file dataset gốc.
* **Vai trò là một Compiler / Linter**: Script chỉ đọc file, phát hiện lỗi vi phạm quy chuẩn, in ra chính xác số thứ tự dòng, token vi phạm, lý do lỗi và dừng lại.
* **Con người / Agent quyết định sửa chữa**: Mọi chỉnh sửa đều phải do Chuyên gia / Agent đọc lại dòng đó, hiểu nguyên nhân ngữ nghĩa và chủ động cập nhật.

### 2. Danh Mục 10 Nhóm Lỗi Được Tự Động Quét Sâu (10-Pass Linter)
Bộ công cụ tự động kiểm định 10 chiều độc lập:
1. `FORMAT_ERROR`: Thiếu dấu phân cách `####` hoặc cấu trúc dòng sai lệch.
2. `SYNTAX_ERROR`: Cú pháp Python tuple/list không hợp lệ (`ast.literal_eval` thất bại).
3. `OUT_OF_BOUNDS`: Index của Aspect/Opinion vượt quá tổng số tokens của câu (`idx >= len(tokens)`).
4. `NON_CONTIGUOUS`: Dãy index không tăng dần liên tục từng đơn vị (ví dụ: `[1, 3]` thay vì `[1, 2, 3]`).
5. `OVERLAP_INDEX`: Trùng lặp vị trí giữa Aspect và Opinion trong cùng một triplet ($Span_{asp} \cap Span_{opi} \neq \emptyset$).
6. `PREP_LEAKAGE`: Aspect bị dính giới từ vị trí ở token đầu tiên (*ở, tại, trên, dưới, trong, ngoài, từ, đến, gần, cạnh, bên, phía, thuộc, của*).
7. `PUNCT_LEAKAGE`: Opinion bị dính dấu câu đứng độc lập ở đầu hoặc cuối (*.,;:!?…”"'()[]-–|*).
8. `VEHICLE_ASPECT`: Gán nhầm phương tiện giao thông làm Aspect (*xe máy, ô tô, xe buýt, xe tải...*).
9. `NON_HCM_PROVINCE`: Câu có nhắc tên tỉnh ngoài (*Cần Thơ, Hà Nội, Cà Mau, Sa Đéc, Đồng Nai...*) mà không bị loại bỏ (`REJECT`).
10. `DOC_FALLBACK_MISUSE`: Dùng tiền tố `TP. Hồ Chí Minh` làm Aspect trong khi câu văn có nhắc tên đường hoặc địa danh cụ thể.

### 3. Bộ 3 Script Kiểm Định Chuẩn Hóa và Cú Pháp CLI

Tất cả 3 script đều hỗ trợ truyền đường dẫn file linh hoạt qua tham số dòng lệnh (CLI parameter) trên cả Windows PowerShell và Linux/macOS:

#### 🔹 Script 1: Kiểm tra cuốn chiếu từng lô 50 mẫu [`scripts/verify_batch_50.py`](file:///D:/SE363_RAWDATA/scripts/verify_batch_50.py)
* **Mục đích**: Chạy kiểm tra tức thì ngay sau khi gán nhãn xong mỗi block 50 mẫu, khoanh vùng lỗi trong phạm vi hẹp để sửa ngay lập tức.
* **Cú pháp lệnh**:
  ```powershell
  # Kiểm tra block từ record 1 đến 50:
  .\.venv\Scripts\python.exe scripts/verify_batch_50.py <đường_dẫn_file> 0 50

  # Kiểm tra block từ record 51 đến 100:
  .\.venv\Scripts\python.exe scripts/verify_batch_50.py <đường_dẫn_file> 50 100

  # Ví dụ chạy kiểm tra Phase 2:
  .\.venv\Scripts\python.exe scripts/verify_batch_50.py data/validate_label/thuan/phase2.txt 0 50
  ```

#### 🔹 Script 2: Kiểm định chuyên sâu 10 vòng lặp [`scripts/deep_10_pass_audit.py`](file:///D:/SE363_RAWDATA/scripts/deep_10_pass_audit.py)
* **Mục đích**: Quét toàn bộ file qua **10 vòng độc lập** để bắt trọn vẹn 10 nhóm lỗi nêu trên. Đảm bảo toàn bộ dataset đạt 100% 0 lỗi trước khi bàn giao.
* **Cú pháp lệnh**:
  ```powershell
  # Chạy kiểm định 10 vòng cho toàn bộ file:
  .\.venv\Scripts\python.exe scripts/deep_10_pass_audit.py <đường_dẫn_file>

  # Ví dụ kiểm định Phase 1 (500 records):
  .\.venv\Scripts\python.exe scripts/deep_10_pass_audit.py data/validate_label/thuan/phase1.txt

  # Ví dụ kiểm định Phase 2 (2.000 records):
  .\.venv\Scripts\python.exe scripts/deep_10_pass_audit.py data/validate_label/thuan/phase2.txt
  ```

#### 🔹 Script 3: Giải mã ngược kiểm tra tính toàn vẹn Index [`scripts/audit_index_integrity.py`](file:///D:/SE363_RAWDATA/scripts/audit_index_integrity.py)
* **Mục đích**: Tự động lấy các số nguyên trong `aspect_indices` và `opinion_indices` để trích xuất ngược lại từng từ vựng trong câu văn gốc (`tokens[i]`), đối soát trực tiếp xem có bị lệch chữ, rỗng nhãn, hay dính dấu câu hay không.
* **Cú pháp lệnh**:
  ```powershell
  # Chạy đối soát giải mã ngược toàn bộ file:
  .\.venv\Scripts\python.exe scripts/audit_index_integrity.py <đường_dẫn_file>

  # Ví dụ đối soát Phase 2:
  .\.venv\Scripts\python.exe scripts/audit_index_integrity.py data/validate_label/thuan/phase2.txt
  ```

---

## 🚀 VIII. QUY TRÌNH TRIỂN KHAI THỰC CHIẾN (STEP-BY-STEP WORKFLOW)

Quy trình chuẩn hóa 4 bước khép kín (The 4-Step Agile Labeling & Verification Loop) áp dụng cho mọi annotator và agent:

```
┌────────────────────────────────────────────────────────────────────────┐
│             QUY TRÌNH 4 BƯỚC THỰC CHIẾN (AGILE LABELING LOOP)          │
└────────────────────────────────────────────────────────────────────────┘
  [Bước 1] Gán nhãn 50 mẫu cuốn chiếu (Đọc trọn vẹn ngữ cảnh + hashtag)
     │
     ▼
  [Bước 2] Chạy `verify_batch_50.py` kiểm tra tức thì block 50 vừa gán
     │       ├── Có lỗi ➔ Mở file sửa tay ngay tại chỗ ➔ Chạy lại Bước 2
     │       └── 0 lỗi  ➔ Tiến hành lô 50 tiếp theo
     ▼
  [Bước 3] Nghiệm thu toàn file với `deep_10_pass_audit.py` (10 vòng độc lập)
     │       └── Phát hiện bất kỳ cảnh báo nào ➔ Hiệu chỉnh triệt để
     ▼
  [Bước 4] Đối soát giải mã ngược với `audit_index_integrity.py`
             └── Nghiệm thu 100% khớp từ vựng ➔ Commit dữ liệu an toàn
```

### 1. Triển khai Phase 2: Tập Overlap 2.000 Records (Từ dòng 501 ➔ 2.500)
* **Quy tắc Mù Đôi (Double-Blind Independent Annotation)**:
  - Cả bạn Thuận và bạn Hùng thực hiện hoàn toàn độc lập, không xem nhãn của nhau để bảo đảm tính khách quan khoa học.
  - Mỗi người tuân thủ cẩm nang này và sử dụng bộ script trên để tự audit tập nhãn của mình đạt **0 lỗi hình thức và toán học**.
* **Đo lường Độ Tin Cậy Liên Đánh Giá (Inter-Annotator Agreement)**:
  - Sau khi cả 2 hoàn tất, chạy script tính chỉ số **Cohen's Kappa ($\kappa$)** trên các nhãn Triplet.
  - Mục tiêu bài báo: $\kappa \ge 0.70$ (Mức độ đồng thuận cao - Substantial Agreement).

### 2. Triển khai Phase 3: Tập Về Đích 4.000 Records (Từ dòng 6.251 ➔ 10.249)
* **Hoàn tất Master Dataset**:
  - Áp dụng triệt để bộ lọc rác tỉnh ngoài (`REJECT`) và cẩm nang này để hoàn tất toàn bộ 10.249 dòng của đề tài.
  - Duy trì kiểm tra từng block 50 records để loại bỏ triệt để ảo giác suy luận.

---

## 📚 IX. TÀI LIỆU THAM KHẢO CỐT LÕI (CORE REFERENCE DOCUMENTS)

Để thực hiện gán nhãn và kiểm định chính xác tuyệt đối cho các giai đoạn tiếp theo (Phase 2 & Phase 3), Agent / Annotator bắt buộc phải đọc kết hợp đầy đủ **3 tài liệu nền tảng** sau:

1. **Cẩm nang chuyên gia gốc tiếng Việt**:
   * [`documents/CAM_NANG_BI_QUYET_GAN_NHAN_ASTE_CHUAN_EXPERT.md`](file:///D:/SE363_RAWDATA/documents/CAM_NANG_BI_QUYET_GAN_NHAN_ASTE_CHUAN_EXPERT.md)
   * *Nội dung*: Cẩm nang chi tiết bằng tiếng Việt đúc kết từ 110 mẫu vàng thực tế tại TP.HCM. Giải thích cặn kẽ về bản chất ngữ nghĩa tiếng Việt, cách bóc tách thực thể không dính từ rác, Opinion không lấy danh từ trơ trọi, và bảng phân định sắc thái `POS` / `NEG` / `NEU` theo ngữ cảnh đời thực.

2. **Hệ thống quy chuẩn tiếng Anh của nhóm**:
   * [`documents/UNIFIED_SYSTEM_GUIDE.md`](file:///D:/SE363_RAWDATA/documents/UNIFIED_SYSTEM_GUIDE.md)
   * *Nội dung*: Bản đặc tả kiến trúc Single Source of Truth (SSOT) chuẩn hóa theo định dạng quốc tế SemEval ASTE-Data-V2 (Xu et al., EMNLP 2020), định nghĩa mô hình học sâu Dual-Branch và 4 tầng đối soát thực địa GIS.

3. **System Prompt Kiểm định & Thẩm định chuyên dụng**:
   * [`label_prompt.txt`](file:///D:/SE363_RAWDATA/label_prompt.txt)
   * *Nội dung*: Bộ system prompt 211 dòng bằng tiếng Anh quy định các mã lỗi chuẩn (`FORMAT_ERROR`, `SPAN_BOUNDARY`, `ASPECT_VEHICLE`, `POLARITY_WRONG`, `DOC_FALLBACK_MISUSE`, `NOT_FLOOD_RELEVANT`) và nguyên tắc ưu tiên quyết định (`ERROR` $\rightarrow$ `REJECT` $\rightarrow$ `HUMAN_REVIEW` $\rightarrow$ `CORRECT` $\rightarrow$ `ACCEPT`).
