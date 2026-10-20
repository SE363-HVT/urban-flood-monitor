# CẨM NANG BÍ QUYẾT GÁN NHÃN ASTE CHUYÊN SÂU (EXPERT ANNOTATION MANUAL)
> **Dự án**: Nghiên cứu Khoa học - Giám sát Ngập lụt Đô thị TP.HCM bằng Khai phá Tri thức Đa phương thức (Multimodal ASTE v3)  
> **Nguồn tri thức**: Đúc kết từ thực nghiệm tinh chỉnh thủ công 110 mẫu vàng (Gold Standards: `seq_id 1 -> 110`) của Chuyên gia gán nhãn.  
> **Tôn chỉ tối thượng**: *"Đọc kỹ từng câu, thấu hiểu ngữ cảnh trọn vẹn, không bắt keyword hời hợt, không đọc lướt!"*

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
Tuyệt đối **KHÔNG** chỉ cắt trơ trọi một chữ `"ngập"`! Phải lấy toàn vẹn cụm từ biểu đạt mức độ và tác động thực tế có trong văn bản:
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

---

## III. NGUYÊN TẮC VÀNG VỀ POLARITY (SẮC THÁI CẢM XÚC & NGỮ CẢNH)

Không được thấy chữ `"ngập"` là vội vàng đánh nhãn `NEG`! Phải đọc hiểu trọn vẹn mục đích phát ngôn của câu văn:

| Nhãn Polarity | Ngữ cảnh ứng dụng | Ví dụ thực tế từ dữ liệu vàng |
| :---: | :--- | :--- |
| **`POS`**<br>*(Tích cực)* | 1. Dự án, công trình đầu tư chống ngập, tiêu thoát nước.<br>2. Biện pháp cải tạo, khơi thông kênh rạch, giải quyết dứt điểm ngập.<br>3. Tình trạng nước rút, giao thông phục hồi bình thường. | - *"giải quyết ngập"*<br>- *"chống ngập triệt để"*<br>- *"tiêu thoát nước và giảm ngập trực tiếp"*<br>- *"tăng năng lực thoát nước"*<br>- *"giải quyết căn cơ tình trạng ngập"*<br>- *"cải thiện hệ thống thoát nước"*<br>- *"nước bắt đầu rút"* |
| **`NEU`**<br>*(Trung tính)* | 1. Dự báo khí tượng, tin thời tiết cảnh báo đề phòng.<br>2. Đánh giá nguy cơ ngập mức độ theo quy chuẩn kỹ thuật.<br>3. Hoạt động theo dõi, quan trắc điểm ngập.<br>4. Câu hỏi thắc mắc, câu hỏi tu từ của người dân. | - *"đề phòng ngập úng"*<br>- *"nguy cơ ngập ở mức vừa"*<br>- *"tiếp tục theo dõi điểm ngập"*<br>- *"Bao giờ mới giải quyết được hết tình trạng ngập"*<br>- *"Hôm nay đường này có ngập không?"*<br>- *"MƯA NGẬP CHƯA ĐỦ KHỔ HAY SAO?"* |
| **`NEG`**<br>*(Tiêu cực)* | 1. Hiện trường ngập úng thực tế gây ngập đường, ngập nhà.<br>2. Xe chết máy, người dân phải dắt bộ, bì bõm lội nước.<br>3. Ùn tắc, hỗn loạn, cản trở đời sống sinh hoạt. | - *"ngập sâu lút bánh xe"*<br>- *"nước tràn vào nhà"*<br>- *"hàng loạt xe chết máy"*<br>- *"ngập hơn nửa bánh xe"*<br>- *"chật vật qua những đoạn ngập nước"*<br>- *"quá tải"* (hệ thống thoát nước) |

---

## IV. NGUYÊN TẮC VỀ ASPECT CATEGORY (PHÂN LOẠI THỰC THỂ)

* **`LOCATION_STREET`**: Tên đường, tuyến hẻm, cây cầu, ngã tư, hầm chui (`Lê Lai`, `Mã Lò`, `cầu Ba Son`, `cầu Bình Triệu`).
* **`LOCATION_ADMIN`**: Cấp Tỉnh/Thành phố (`TPHCM`, `TP. Hồ Chí Minh`, `Sài Gòn`) và cấp Phường/Xã (`An Lạc`, `Bình Trị Đông`, `Dĩ An`).  
  ⚠️ *Cấm kỵ*: Tuyệt đối không để `TPHCM` mang nhãn `LOCATION_STREET`!
* **`HYDROLOGY`**: Sông ngòi, kênh rạch, dòng nước (`sông Sài Gòn`, `rạch Thủ Đức`, `nước`).
* **`INFRASTRUCTURE_DRAINAGE`**: Cống thoát nước, trạm bơm, dự án nạo vét, hệ thống thoát nước đô thị (`hệ thống thoát nước`, `Dự án chống ngập`).

---

## V. BẢNG MẪU ĐỐI SOÁT THỰC CHIẾN (CASE STUDY)

Dưới đây là một số mẫu điển hình đã được chuyên gia chuẩn hóa để làm khuôn mẫu đối chiếu:

```json
// Mẫu 1: Đánh giá nguy cơ theo dõi (NEU) - Tách riêng từng đường
{
  "sentence": "Các tuyến Bình Quới, Lã Xuân Oai cũng được đánh giá có nguy cơ ngập ở mức vừa.",
  "aste_triplets": [
    {"aspect": "Bình Quới", "opinion": "nguy cơ ngập ở mức vừa", "polarity": "NEU", "aspect_category": "LOCATION_STREET"},
    {"aspect": "Lã Xuân Oai", "opinion": "nguy cơ ngập ở mức vừa", "polarity": "NEU", "aspect_category": "LOCATION_STREET"}
  ]
}

// Mẫu 2: Dự án công trình chống ngập (POS)
{
  "sentence": "Công trình giúp giải quyết tình trạng ô nhiễm và chống ngập triệt để cho khu vực.",
  "aste_triplets": [
    {"aspect": "Công trình", "opinion": "chống ngập triệt để", "polarity": "POS", "aspect_category": "INFRASTRUCTURE_DRAINAGE"}
  ]
}

// Mẫu 3: Hiện trường ngập thực tế chi tiết mức độ (NEG)
{
  "sentence": "Đường Mã Lò (phường Bình Trị Đông) nước ngập sâu lút bánh xe khiến hàng loạt xe chết máy.",
  "aste_triplets": [
    {"aspect": "Mã Lò", "opinion": "ngập sâu lút bánh xe", "polarity": "NEG", "aspect_category": "LOCATION_STREET"},
    {"aspect": "Bình Trị Đông", "opinion": "ngập sâu lút bánh xe", "polarity": "NEG", "aspect_category": "LOCATION_ADMIN"}
  ]
}

// Mẫu 4: Câu hỏi tu từ / Thắc mắc (NEU)
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
4. [ ] **Đầy đủ mức độ**: Opinion đã giữ lại đầy đủ cụm từ chỉ chiều sâu, mức độ ngập chưa?
5. [ ] **Đúng ngữ cảnh Polarity**: Nếu là dự án giải quyết ngập $\rightarrow$ `POS`; nếu là dự báo/câu hỏi $\rightarrow$ `NEU`; nếu là ngập thực tế $\rightarrow$ `NEG`.
