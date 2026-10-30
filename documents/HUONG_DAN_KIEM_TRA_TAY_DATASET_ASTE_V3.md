# 📘 CẨM NANG HƯỚNG DẪN KIỂM TRA TAY DATASET ASTE V3 (MANUAL AUDIT GUIDE)
## Dành riêng cho Thành viên Dự án SE363 / RadiNet — Chuẩn Bị Bài Báo ICWSM 2027

> **Tệp dữ liệu mục tiêu**: [`data/processed/hcmc_flood_annotated_v3_multimodal.json`](file:///d:/SE363_RAWDATA/data/processed/hcmc_flood_annotated_v3_multimodal.json)  
> **Quy mô tập dữ liệu**: **4.770 mẫu câu / 7.072 bộ ba gán nhãn**  
> **Mục đích**: Hướng dẫn từng bước cách mở file, bôi đen văn bản, đối chiếu 5 tiêu chí học thuật và phát hiện lỗi gán nhãn thủ công trước khi nộp nghiệm thu.

---

## 🎯 1. Cấu Trúc Một Mẫu Gán Nhãn Chuẩn (Schema v3)

Khi bạn mở file JSON lên, mỗi mẫu câu sẽ có cấu trúc như sau:

```json
{
  "id": "ep03_fb_post_0012_s01",
  "content": {
    "title": "Ngập đường Trần Xuân Soạn chiều nay",
    "text": "Đường Trần Xuân Soạn triều cường dâng cao ngập lút bánh xe, nhiều phương tiện chết máy bì bõm."
  },
  "location": {
    "ward": "Phường Tân Thuận",
    "city": "Hồ Chí Minh",
    "legacy_district": "TP.HCM"
  },
  "aste_triplets": [
    {
      "aspect": "Trần Xuân Soạn",
      "opinion": "ngập lút bánh xe",
      "polarity": "NEG",
      "aspect_category": "LOCATION_STREET",
      "severity": "HIGH",
      "grounding_provenance": "SPAN_MATCHED",
      "gazetteer_id": "csgt_tide_01"
    }
  ]
}
```

---

## 🔍 2. Quy Trình 4 Bước Kiểm Tra Nhanh Một Mẫu Câu (The 4-Step Checklist)

Khi nhìn vào một dòng trong file JSON, bạn chỉ cần thực hiện đúng **4 bước**:

```
[Bước 1: Soi Aspect] ──► [Bước 2: Soi Opinion] ──► [Bước 3: Soi Polarity] ──► [Bước 4: Soi Category]
  - Có trong câu?         - Có trong câu?           - Có từ phủ định?         - Đúng nhóm thực thể?
  - Bỏ râu ria chưa?       - Bỏ từ nối chưa?         - NEG, POS hay NEU?       - Tuyệt đối không Quận!
```

### Bước 1: Kiểm tra `aspect` (Khía cạnh)
1. **Bôi đen text**: Dùng chuột bôi đen chữ trong trường `"aspect"`, bấm `Ctrl + F` tìm xem chữ đó **có xuất hiện y nguyên 100% trong `content.text` không**.
2. **Cắt tỉa râu ria**:
   - Gặp: *"ở đường Trần Xuân Soạn"*, *"tại khu vực Thảo Điền"*.
   - ✅ **Đúng**: Cắt bỏ chữ *"ở", "tại", "khu vực"*, chỉ lấy `Trần Xuân Soạn` hoặc `Thảo Điền`.
3. **Kiểm tra chữ "Quận" (Lỗi cấm kỵ theo NQ 1685)**:
   - ❌ Tuyệt đối **KHÔNG ĐƯỢC CÓ** `Quận 7`, `Quận 8`, `Quận Bình Thạnh`.
   - ✅ Nếu bài viết nhắc đến Quận, hệ thống phải map về tên đường hoặc Phường mới (*Phường Tân Thuận, Phường Hiệp Bình*).
4. **Kiểm tra phương tiện giao thông (Lỗi nhầm nạn nhân)**:
   - ❌ Thấy `xe máy`, `ô tô`, `xe buýt` làm Aspect $\longrightarrow$ **Bắt lỗi ngay!** Xe cộ là nạn nhân, Aspect phải là con đường nơi xe bị chết máy.

### Bước 2: Kiểm tra `opinion` (Ý kiến / Trạng thái)
1. **Kiểm tra Verbatim**: Tương tự như Aspect, `opinion` bắt buộc phải là cụm từ **có thật từng chữ trong câu**.
2. **Giữ trọn vẹn hạt nhân chỉ mức độ**:
   - Người ta viết *"ngập lút bánh xe"* thì lấy trọn vẹn `ngập lút bánh xe`. Đừng cắt cụt ngủn còn mỗi chữ `ngập`.
   - Người ta viết *"chết máy hàng loạt"* thì lấy trọn vẹn `chết máy hàng loạt`.

### Bước 3: Kiểm tra `polarity` (Cực tính: NEG / POS / NEU)
Cực tính là **thái độ đối với Aspect**, kiểm tra theo **Quy tắc 1 Câu**:
* **`NEG` (Tiêu cực)**: Tả ngập lụt đang diễn ra, kẹt xe, chết máy, nước tràn vào nhà, nước rút chậm.
  - *Từ khóa*: `ngập sâu`, `ngập nặng`, `chết máy`, `bì bõm`, `chưa rút`, `kẹt xe`.
* **`POS` (Tích cực - Rất quan trọng)**:
  - **Phục hồi**: Nước đã rút, khô ráo, hết ngập, đường thông thoáng, xe đi lại bình thường.
  - **Khen ngợi**: Công trình ngăn triều phát huy hiệu quả, CSGT đẩy xe giúp dân.
  - ⚠️ **LỖI CẦN BẮT**: Nếu câu ghi *"đường đã hết ngập"* hoặc *"nước đã rút sạch"* mà nhãn ghi là `NEG` $\longrightarrow$ **Bắt sửa thành `POS` ngay!**
* **`NEU` (Trung tính)**:
  - Số liệu đo đạc kỹ thuật: *"ngập sâu khoảng 20-30cm"*, *"đỉnh triều đạt 1m70"*.
  - Dự báo khí tượng: *"dự báo triều cường"*, *"nguy cơ ngập"*.
  - Tin công trình: *"khánh thành cống"*, *"vận hành thử nghiệm trạm bơm"*.
  - Câu hỏi thăm: *"đường có ngập không mọi người?"*.

### Bước 4: Kiểm tra `aspect_category` (5 Nhóm chuẩn)
Đối chiếu xem Aspect đó thuộc nhóm nào:
1. **`LOCATION_STREET`**: Tên đường, cầu, ngã tư, hẻm (*Trần Xuân Soạn, cầu Bình Triệu, hầm Thủ Thiêm*).
2. **`LOCATION_ADMIN`**: Thành phố hoặc 168 Phường/Xã mới (*TP. Hồ Chí Minh, Sài Gòn, Phường Tân Thuận*).
3. **`HYDROLOGY`**: Sông, ngòi, kênh, rạch, đỉnh triều (*triều cường, sông Sài Gòn, Kênh Nhiêu Lộc, trạm Phú An*).
4. **`INFRASTRUCTURE_DRAINAGE`**: Cống, máy bơm, đê kè (*cống ngăn triều Mương Chuối, trạm bơm Bình Lợi, miệng cống*).
5. **`RESPONSE_ENTITY`**: Lực lượng ứng trực (*CSGT, công nhân thoát nước, lực lượng chức năng*).

---

##  bảng 3. BẢNG TRA CỨU NHANH CÁC LỖI THƯỜNG GẶP (CHEAT-SHEET)

| Câu văn mẫu trong bài | Gán nhãn SAI (Cần bắt lỗi) | Gán nhãn ĐÚNG (Chuẩn ICWSM) | Giải thích lý do |
| :--- | :--- | :--- | :--- |
| *"Nhiều xe máy chết máy la liệt trên đường Huỳnh Tấn Phát."* | Aspect: `xe máy`<br>Opinion: `chết máy` | Aspect: `Huỳnh Tấn Phát`<br>Opinion: `chết máy la liệt` | Xe máy là nạn nhân, không phải thực thể địa lý. |
| *"Đường Trần Xuân Soạn Quận 7 ngập sâu nửa mét."* | Aspect: `Quận 7`<br>Category: `LOCATION_ADMIN` | Aspect: `Trần Xuân Soạn`<br>Category: `LOCATION_STREET` | Bỏ hoàn toàn cấp Quận theo Nghị quyết 1685. |
| *"Đến 20h tối nước đã rút sạch, đường khô ráo xe đi bình thường."* | Polarity: `NEG`<br>Opinion: `nước` | Polarity: `POS`<br>Opinion: `nước đã rút sạch, đường khô ráo` | Câu tả trạng thái phục hồi hoàn tất, bắt buộc là POS. |
| *"Triều cường sông Sài Gòn dâng cao làm ngập mép đường."* | Aspect: `Sài Gòn`<br>Category: `LOCATION_ADMIN` | Aspect: `sông Sài Gòn`<br>Category: `HYDROLOGY` | Lỗi Shadowing: không được cắt vụn tên sông thành tên thành phố. |
| *"Đoạn qua ngã tư Nguyễn Văn Cừ nước ngập sâu khoảng 30cm."* | Polarity: `NEG` | Polarity: `NEU`<br>Severity: `MEDIUM` | Đo đạc trắc quan khách quan mang tính chất kỹ thuật $\rightarrow$ NEU. |

---

## 📋 4. Lưu Ý Quan Trọng Về Các Mẫu Tăng Cường (CDA - 890 Mẫu Cuối File)

Khi bạn cuộn xuống cuối file JSON (các mẫu có ID bắt đầu bằng `cda_pos_...`):
- Đây là các mẫu được tạo bằng phương pháp **Nghịch đảo ngữ nghĩa có kiểm soát (Counterfactual Data Augmentation)** để cân bằng tỷ lệ POS đạt đúng 15.00%.
- **Cách nhận biết**:
  ```json
  {
    "is_counterfactual_augmented": true,
    "data_split_recommendation": "TRAIN_ONLY"
  }
  ```
- **Nguyên tắc thẩm định**:
  - Kiểm tra xem tên đường có phải là đường thật tại TP.HCM không (*Trần Xuân Soạn, Phan Huy Ích, Tô Ngọc Vân...*).
  - Kiểm tra xem vị ngữ có đúng là vị ngữ phục hồi không (*nước đã rút, khô ráo, hết ngập*).
  - Đảm bảo các câu này đều có cờ `"TRAIN_ONLY"` để không bị đưa nhầm vào tập Test khi đánh giá bài báo.

---

## 🛠️ 5. Script Hỗ Trợ Kiểm Tra Tự Động Trước Khi Kiểm Tra Tay

Nếu bạn muốn kiểm tra quét nhanh toàn bộ file bằng máy tính trước khi soi từng dòng bằng mắt, chỉ cần mở terminal và chạy script đã chuẩn bị sẵn:

```bash
python scripts/figures/generate_full_stats_v3.py
```

Nếu màn hình hiển thị:
- `Loi Verbatim Opinion: 0`
- `Loi ro ri cap Quan: 0`
- `Loi gan xe co lam Aspect: 0`
- `Cuc tinh: NEG ~71% | POS 15% | NEU ~14%`

$\Longrightarrow$ **Tập dữ liệu hoàn toàn sạch sẽ và đạt chuẩn vàng (Gold Standard) để gửi đi nghiệm thu!**
