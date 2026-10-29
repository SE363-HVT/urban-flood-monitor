# CẨM NANG BÍ QUYẾT GÁN NHÃN ASTE CHUYÊN SÂU (EXPERT ANNOTATION MANUAL)
> **Dự án**: Nghiên cứu Khoa học - Giám sát Ngập lụt Đô thị TP.HCM bằng Khai phá Tri thức Đa phương thức (Multimodal ASTE v3)  
> **Nguồn tri thức**: Đúc kết từ thực nghiệm tinh chỉnh thủ công 110 mẫu vàng (Gold Standards: `seq_id 1 -> 110`) của Chuyên gia gán nhãn.  
> 
> 🔥 **TÔN CHỈ TỐI THƯỢNG CỦA CHUYÊN GIA**:  
> *"ĐỌC HẾT CÂU + HIỂU TRỌN VẸN NGỮ CẢNH + TUYỆT ĐỐI KHÔNG BẮT KEYWORD MỘT CÁCH HỜI HỢT MÀ BỎ ĐI CÁC YẾU TỐ NGỮ CẢNH KHÁC!"*

---

## I. NGUYÊN TẮC VÀNG VỀ ASPECT (TARGET ENTITY)

Aspect là **Thực thể mục tiêu** mà câu văn hướng tới để mô tả hoặc đánh giá. Khi bóc tách Aspect, bắt buộc tuân thủ 5 điều sau:

### 1. Bóc tách tinh gọn – Cắt sạch từ rác ở đầu và đuôi
* **Sai lầm thường gặp**: Cắt dính cả trạng từ, liên từ hoặc vị từ vào tên đường.
* **Quy chuẩn sửa đổi**:
  - ❌ `Trần Xuân Soạn thường xuyên xảy ra tình trạng` $\rightarrow$  **`Trần Xuân Soạn`**
  - ❌ `51 vào để xử lý điểm` $\rightarrow$  **`quốc lộ 51`**
  - ❌ `D5 thường xuyên diễn ra tình trạng` $\rightarrow$  **`đường D5`**
  - ❌ `Thị Nghè 2 nha` $\rightarrow$  **`Thị Nghè 2`**

### 2. Tách riêng các tuyến đường bị ghép (Compound Aspects)
* Khi tác giả liệt kê nhiều con đường trong một cụm câu, **phải tách thành các bộ triplet độc lập**:
  - ❌ Gộp chung: `Lã Xuân Oai và Nguyễn Duy Trinh`
  -  Tách riêng:
    - Triplet 1: Aspect = **`Lã Xuân Oai`**
    - Triplet 2: Aspect = **`Nguyễn Duy Trinh`**

### 3. Bảo toàn tiền tố nhận diện hạ tầng và địa vật trọng điểm
* Khi câu văn nhấn mạnh công trình, chợ, cầu, ngã tư hoặc dự án, phải lấy đủ tiền tố định danh để mô hình học đúng kiểu thực thể:
  -  **`cầu Bình Triệu`** (không cắt trơ trọi `Bình Triệu`)
  -  **`cầu Ba Son`** (không cắt cụt `Ba Son`)
  -  **`chợ Thủ Đức`** (không nhầm với địa danh phường)
  -  **`dự án nạo vét các tuyến rạch thoát nước`**
  -  **`Dự án Giải quyết ngập do triều giai đoạn 1`** (không cắt cụt `Dự án Giải quyết`)

### 4. Bóc tách không gian đa cấp độ (Multi-Level Spatial Grounding)
* Nếu câu có cả tên đường và tên phường/xã, phải tạo các triplet tương ứng để phục vụ bản đồ GIS:
  - Ví dụ: *"Tại đường Hồ Học Lãm (phường An Lạc)... ngập sâu"*
    - Triplet 1: Aspect = **`Hồ Học Lãm`** (`LOCATION_STREET`)
    - Triplet 2: Aspect = **`An Lạc`** (`LOCATION_ADMIN`)

### 5. Tuyệt đối không gán Aspect rác / Phi thực thể
* ❌ CẤM gán các từ như: `ùn tắc`, `nước dâng` làm Aspect.
* Nếu câu mô tả hiện tượng chung toàn thành phố mà không nhắc tên đường cụ thể:
  - Nếu trong câu có chữ `TPHCM` / `Sài Gòn` $\rightarrow$ Aspect là **`TPHCM`** / **`Sài Gòn`** (`grounding_provenance: "SPAN_MATCHED"`).
  - Nếu câu trích ra từ bài báo nói về TPHCM nhưng câu đó không có tên địa danh $\rightarrow$ Kích hoạt kế thừa toàn bài: Aspect là **`TP. Hồ Chí Minh`** (`grounding_provenance: "DOC_FALLBACK"`).

---

## II. NGUYÊN TẮC VÀNG VỀ OPINION (SENTIMENT / STATE EXPRESSION)

Opinion là **cụm từ mô tả tính chất, mức độ ngập lụt, cảm xúc hoặc hành động ứng phó**.

### 1. Giữ trọn vẹn mức độ mô tả (Rich Descriptors & Severity)
Tuyệt đối **KHÔNG** chỉ cắt trơ trọi một chữ `\"ngập\"` khi câu có mô tả chi tiết! Phải lấy toàn vẹn cụm từ biểu đạt mức độ và tác động thực tế có trong văn bản:
* **Mức độ ngập sâu**:
  - `Ngập gần cả mét` (thay vì chỉ `Ngập`)
  - `ngập hơn nửa bánh xe` (thay vì chỉ `ngập`)
  - `ngập sâu lút bánh xe` (thay vì chỉ `ngập sâu`)
  - `ngập lênh láng`, `chìm sâu trong biển nước`, `ngập như sông`, `nước ngập mênh mông`
  - `vẫn còn ngập sâu, có nơi trên 0,5m`
* **Hành vi ứng phó & Hậu quả giao thông**:
  - `hàng loạt xe chết máy`
  - `dắt bộ xe do xe chết máy`
  - `phải dắt bộ cả cây số`
  - `bì bõm lội qua nhiều đoạn bị ngập sâu`
  - `chật vật qua những đoạn ngập nước`
  - `nhích từng chút một trong làn nước ngập`
  - `nước tràn vào`

### 2. Gán đúng vị từ cho từng đối tượng chủ thể
* **Đối với cống rãnh, hệ thống thoát nước**:
  - Ý kiến mô tả phải là: `quá tải`, `chưa đáp ứng khả năng tiêu thoát`, `tê liệt` (không gán là "ngập úng").
* **Đối với dòng nước / thủy văn**:
  - `dâng sâu`, `cuồn cuộn như lũ`, `vẫn chưa rút`, `nước rút rất chậm`.

### 3. Cấm tuyệt đối gán Opinion là cụm danh từ chỉ vị trí như "đoạn ngập"
* ❌ **Sai lầm nghiêm trọng**: Gán `opinion: "đoạn ngập"`. "Đoạn ngập" là một cụm danh từ chỉ phân đoạn đường hoặc vị trí không gian (ví dụ: *"xe di chuyển qua đoạn ngập"*), hoàn toàn **không phải là vị từ hoặc ý kiến** mô tả trạng thái! Gán như vậy câu văn sẽ tối nghĩa và mô hình không thể học được sắc thái biểu cảm.
* ✅ **Quy chuẩn chuẩn xác**:
  - Trong câu: *"Các phương tiện di chuyển qua đoạn ngập trên đường Trần Xuân Soạn"* $\rightarrow$ Aspect là `đường Trần Xuân Soạn`, Opinion phải là **`ngập`** (hoặc `di chuyển qua đoạn ngập` nếu muốn nhấn mạnh sự di chuyển khó khăn), tuyệt đối không để cộc lốc `"đoạn ngập"`.
  - Trong câu: *"nghiêng xe tháo nước khi đi qua đoạn ngập"* $\rightarrow$ Opinion là `nghiêng xe tháo nước` hoặc `ngập`.

---

## III. NGUYÊN TẮC VÀNG VỀ POLARITY (SẮC THÁI CẢM XÚC & NGỮ CẢNH)

Không được thấy chữ `\"ngập\"` là vội vàng đánh nhãn `NEG`! Phải đọc hiểu trọn vẹn mục đích phát ngôn của câu văn:

| Nhãn Polarity | Ngữ cảnh ứng dụng | Ví dụ thực tế từ dữ liệu vàng |
| :---: | :--- | :--- |
| **`POS`**<br>*(Tích cực)* | 1. **Dự án, giải pháp chống ngập**: Dự án, công trình đầu tư, khơi thông kênh rạch, giải quyết dứt điểm ngập.<br>2. **Ý khen ngợi & Đánh giá tích cực của người dân**: Nước rút nhanh, thoát nước tốt, công trình phát huy hiệu quả, đô thị ít ngập hơn.<br>3. **Trạng thái phục hồi**: Nước bắt đầu rút, đường xá thông thoáng trở lại. | - *\"nước rút nhanh ghê\"* / *\"nước rút lẹ\"*<br>- *\"thoát nước tốt\"* / *\"không còn ngập như trước\"*<br>- *\"tình trạng ngập ít xảy ra hơn\"*<br>- *\"hạn chế sụp lún, ngập lụt\"*<br>- *\"chống ngập triệt để\"*<br>- *\"tiêu thoát nước và giảm ngập trực tiếp\"*<br>- *\"tăng năng lực thoát nước\"*<br>- *\"giải quyết căn cơ tình trạng ngập\"*<br>- *\"cải thiện hệ thống thoát nước\"*<br>- *\"nước bắt đầu rút\"* / *\"có dấu hiệu rút bớt\"* |
| **`NEU`**<br>*(Trung tính)* | 1. **Dự báo khí tượng & Khuyến cáo**: Tin thời tiết cảnh báo đề phòng ngập, đỉnh triều ở mức cao.<br>2. **Đánh giá quy chuẩn**: Nguy cơ ngập mức độ vừa/nhẹ theo kỹ thuật.<br>3. **Hoạt động theo dõi**: Quan trắc điểm ngập, kế hoạch đưa vào.<br>4. **Câu hỏi thắc mắc / Tu từ**: Câu hỏi thăm tình hình, thắc mắc của người dân. | - *\"đề phòng ngập úng\"*<br>- *\"tiếp tục ở mức cao, có thể đạt đỉnh và vượt mức báo động 3\"*<br>- *\"cảnh báo nguy cơ ngập lụt\"*<br>- *\"nguy cơ ngập ở mức vừa\"*<br>- *\"tiếp tục theo dõi điểm ngập\"*<br>- *\"Bao giờ mới giải quyết được hết tình trạng ngập\"*<br>- *\"Hôm nay đường này có ngập không?\"*<br>- *\"MƯA NGẬP CHƯA ĐỦ KHỔ HAY SAO?\"* |
| **`NEG`**<br>*(Tiêu cực)* | 1. **Hiện trường ngập úng thực tế**: Gây ngập đường, ngập nhà cửa, đồ đạc hư hỏng.<br>2. **Hậu quả giao thông**: Xe chết máy, người dân phải dắt bộ, bì bõm lội nước.<br>3. **Ách tắc & Đình trệ**: Ùn tắc, hỗn loạn, cản trở đời sống sinh hoạt. | - *\"ngập sâu lút bánh xe\"*<br>- *\"nước tràn vào nhà\"*<br>- *\"hàng loạt xe chết máy\"*<br>- *\"ngập hơn nửa bánh xe\"*<br>- *\"chật vật qua những đoạn ngập nước\"*<br>- *\"quá tải\"* (hệ thống thoát nước) |

---

## IV. NGUYÊN TẮC VỀ ASPECT CATEGORY (PHÂN LOẠI THỰC THỂ)

* **`LOCATION_STREET`**: Tên đường, tuyến hẻm, cây cầu, ngã tư, hầm chui (`Lê Lai`, `Mã Lò`, `cầu Ba Son`, `cầu Bình Triệu`).
* **`LOCATION_ADMIN`**: Cấp Tỉnh/Thành phố (`TPHCM`, `TP. Hồ Chí Minh`, `Sài Gòn`) và cấp Phường/Xã (`An Lạc`, `Bình Trị Đông`, `Dĩ An`).  
  ⚠️ *Cấm kỵ*: Tuyệt đối không để `TPHCM` mang nhãn `LOCATION_STREET`!
* **`HYDROLOGY`**: Sông ngòi, kênh rạch, dòng nước (`sông Sài Gòn`, `rạch Thủ Đức`, `nước`, `triều cường`, `đỉnh triều`).
* **`INFRASTRUCTURE_DRAINAGE`**: Cống thoát nước, trạm bơm, dự án nạo vét, hệ thống thoát nước đô thị (`hệ thống thoát nước`, `Dự án chống ngập`).

---

## V. BẢNG MẪU ĐỐI SOÁT THỰC CHIẾN (CASE STUDY)

```json
// Mẫu 1: Ý khen ngợi / Nước rút nhanh (POS)
{
  "sentence": "Cơn mưa lớn vừa dứt thì nước rút nhanh ghê, đường Huỳnh Tấn Phát ráo hoảnh.",
  "aste_triplets": [
    {"aspect": "Huỳnh Tấn Phát", "opinion": "nước rút nhanh ghê", "polarity": "POS", "aspect_category": "LOCATION_STREET"}
  ]
}

// Mẫu 2: Đánh giá nguy cơ theo dõi (NEU) - Tách riêng từng đường
{
  "sentence": "Các tuyến Bình Quới, Lã Xuân Oai cũng được đánh giá có nguy cơ ngập ở mức vừa.",
  "aste_triplets": [
    {"aspect": "Bình Quới", "opinion": "nguy cơ ngập ở mức vừa", "polarity": "NEU", "aspect_category": "LOCATION_STREET"},
    {"aspect": "Lã Xuân Oai", "opinion": "nguy cơ ngập ở mức vừa", "polarity": "NEU", "aspect_category": "LOCATION_STREET"}
  ]
}

// Mẫu 3: Dự án công trình chống ngập (POS)
{
  "sentence": "Công trình giúp giải quyết tình trạng ô nhiễm và chống ngập triệt để cho khu vực.",
  "aste_triplets": [
    {"aspect": "Công trình", "opinion": "chống ngập triệt để", "polarity": "POS", "aspect_category": "INFRASTRUCTURE_DRAINAGE"}
  ]
}

// Mẫu 4: Hiện trường ngập thực tế chi tiết mức độ (NEG)
{
  "sentence": "Đường Mã Lò (phường Bình Trị Đông) nước ngập sâu lút bánh xe khiến hàng loạt xe chết máy.",
  "aste_triplets": [
    {"aspect": "Mã Lò", "opinion": "ngập sâu lút bánh xe", "polarity": "NEG", "aspect_category": "LOCATION_STREET"},
    {"aspect": "Bình Trị Đông", "opinion": "ngập sâu lút bánh xe", "polarity": "NEG", "aspect_category": "LOCATION_ADMIN"}
  ]
}

// Mẫu 5: Câu hỏi tu từ / Thắc mắc (NEU)
{
  "sentence": "Bao giờ mới giải quyết được hết tình trạng ngập ở HCM đây?",
  "aste_triplets": [
    {"aspect": "TP. Hồ Chí Minh", "opinion": "Bao giờ mới giải quyết được hết tình trạng ngập", "polarity": "NEU", "aspect_category": "LOCATION_ADMIN"}
  ]
}
```

---

## VI. CHECKLIST BẮT BUỘC TRƯỚC KHI LƯU RECORD
1. [ ] **100% Verbatim**: Tất cả Aspect (`SPAN_MATCHED`) và Opinion bắt buộc phải là chuỗi con nguyên văn xuất hiện trong câu.
2. [ ] **Không sót thực thể**: Đã kiểm tra xem có tên đường, cây cầu hay tên phường nào trong câu bị bỏ sót không.
3. [ ] **Không dính từ rác**: Đã cắt bỏ sạch sẽ các từ nối thừa ở đầu/đuôi Aspect chưa?
4. [ ] **Đầy đủ mức độ**: Opinion đã giữ lại đầy đủ cụm từ chỉ chiều sâu, mức độ ngập chưa? (Tuyệt đối không lấy danh từ "đoạn ngập").
5. [ ] **Đúng ngữ cảnh Polarity**: Nếu là dự án giải quyết ngập hoặc khen nước rút nhanh / ít ngập $\rightarrow$ `POS`; nếu là dự báo/cảnh báo/câu hỏi $\rightarrow$ `NEU`; nếu là ngập thực tế $\rightarrow$ `NEG`.

---

## VII. QUY CHUẨN ADAPTER CHUYỂN ĐỔI SANG ĐỊNH DẠNG ASTE-V2 (SEMEVAL / EMNLP 2020 INDEX FORMAT)

### 1. Tôn chỉ cốt lõi: Bảo toàn 100% ngữ nghĩa & Phương pháp gán nhãn
* **Nguyên tắc bất biến**: Phương pháp gán nhãn của nhóm **hoàn toàn giữ nguyên** theo đúng Mục I đến Mục VI trong Cẩm nang này.
* **Vai trò của Adapter**: Adapter chỉ là tầng chuyển đổi hình thức biểu diễn (**Representation Format Adapter**), chuyển đổi từ định dạng lưu trữ ngữ nghĩa JSON của nhóm (`hcmc_flood_annotated_v3_multimodal.json`) sang định dạng tệp phẳng đánh chỉ số token (`aste_data_v2/test_triplets.txt`) để phục vụ so sánh (benchmark) trực tiếp với các mô hình baseline quốc tế trong bài báo khoa học.
* **Hai tập dữ liệu song hành**:
  1. `hcmc_flood_annotated_v3_multimodal.json`: Bộ Master 10,000 records chuẩn của nhóm, lưu trữ đầy đủ thuộc tính đa phương thức, toạ độ GIS, thông tin phường xã NQ 1685, xuất xứ gán nhãn (`grounding_provenance`), và mức độ ngập (`severity`).
  2. `data/processed/aste_v2_emnlp2020/*.txt`: Bộ file sau Adapter theo đúng chuẩn Xu et al. (EMNLP 2020), cấu trúc:
     ```text
     tokenized_sentence####[([t_start, ..., t_end], [o_start, ..., o_end], 'POL'), ...]
     ```

### 2. Cơ chế Tiền tố hóa Ngữ cảnh (Context Prefix Injection) cho DOC_FALLBACK
* **Thách thức bài toán**: Format chuẩn của Xu et al. bắt buộc mọi từ của Aspect và Opinion phải có mặt trong câu để đánh chỉ số token index `[start, ..., end]`. Tuy nhiên, với các câu thuộc dạng `DOC_FALLBACK` (ngữ cảnh toàn bài báo nói về ngập lụt tại TP. Hồ Chí Minh nhưng tác giả không lặp lại tên thành phố trong câu con đó), trong câu không xuất hiện trực tiếp cụm từ `"TP. Hồ Chí Minh"`.
* **Giải pháp quy chuẩn**:
  - Đối với các triplet có `grounding_provenance == "DOC_FALLBACK"`, Adapter sẽ tự động bổ sung tiền tố ngữ cảnh:
    `Tại TP. Hồ Chí Minh , <câu_gốc>`
  - Sau khi chèn tiền tố, câu được phân đoạn token rõ ràng (tách biệt các dấu câu `,`, `.`, `!`, `?`, `"` bằng khoảng trắng).
  - Vị trí của Aspect `TP. Hồ Chí Minh` luôn được định vị chính xác tuyệt đối tại: **`[1, 2, 3, 4]`** (với token 0 là `"Tại"`, token 5 là dấu phẩy `","`).
  - Vị trí của Opinion được tìm kiếm chính xác tuyệt đối theo chuỗi token trong phần thân câu (từ token 6 trở đi).

### 3. Bảng Minh họa Xác định Chỉ số Token Chính xác Tuyệt đối
Xét câu văn ví dụ:
* *Câu gốc*: `"Sáng 11/9, khi nước bắt đầu rút, chị tranh thủ dọn bùn đất."`
* *Aspect*: `TP. Hồ Chí Minh` (`DOC_FALLBACK`)
* *Opinion*: `nước bắt đầu rút`
* *Polarity*: `POS`

Sau khi Adapter áp dụng Context Prefix Injection và phân tách dấu câu chuẩn mực:
```text
Tại TP. Hồ Chí Minh , Sáng 11/9 , khi nước bắt đầu rút , chị tranh thủ dọn bùn đất .
```

Bảng phân rã token 0-indexed:
| Token Index | Giá trị Token | Chú giải vai trò |
| :---: | :--- | :--- |
| `0` | `Tại` | Từ nối tiền tố ngữ cảnh |
| `1` | `TP.` | **Aspect Token 1** |
| `2` | `Hồ` | **Aspect Token 2** |
| `3` | `Chí` | **Aspect Token 3** |
| `4` | `Minh` | **Aspect Token 4** |
| `5` | `,` | Dấu phẩy ngăn cách tiền tố |
| `6` | `Sáng` | Thân câu gốc |
| `7` | `11/9` | Thân câu gốc |
| `8` | `,` | Dấu phẩy câu gốc |
| `9` | `khi` | Liên từ |
| `10` | `nước` | **Opinion Token 1** |
| `11` | `bắt` | **Opinion Token 2** |
| `12` | `đầu` | **Opinion Token 3** |
| `13` | `rút` | **Opinion Token 4** |
| `14` | `,` | Dấu phẩy câu gốc |
| `15` | `chị` | Đại từ |
| `16` | `tranh` | Thân câu gốc |
| `17` | `thủ` | Thân câu gốc |
| `18` | `dọn` | Thân câu gốc |
| `19` | `bùn` | Thân câu gốc |
| `20` | `đất` | Thân câu gốc |
| `21` | `.` | Dấu chấm kết câu |

* Dòng xuất ra chuẩn ASTE-Data-V2:
```text
Tại TP. Hồ Chí Minh , Sáng 11/9 , khi nước bắt đầu rút , chị tranh thủ dọn bùn đất .####[([1, 2, 3, 4], [10, 11, 12, 13], 'POS')]
```

⚠️ **Lưu ý kiểm soát chất lượng (QA)**:
1. Tuyệt đối không tính nhầm token ranh giới. Opinion `"nước bắt đầu rút"` bắt đầu tại token `10` và kết thúc tại token `13` $\rightarrow$ dãy chỉ số là `[10, 11, 12, 13]`.
2. Tokenizer trong Adapter phải xử lý tách dấu câu đồng nhất (`Punctuation Isolation`) để đảm bảo không dính dấu phẩy hay dấu chấm vào từ (ví dụ `rút ,` thay vì `rút,`).
3. Adapter tự động kiểm tra đối soát chéo (Reverse Assertion): Lấy các token tại vị trí `[start, ..., end]` ghép lại phải trùng khớp 100% từng ký tự với Aspect và Opinion gốc. Nếu phát hiện bất kỳ sai lệch nào, Adapter sẽ lập tức báo lỗi và dừng để chuyên gia thẩm tra.
