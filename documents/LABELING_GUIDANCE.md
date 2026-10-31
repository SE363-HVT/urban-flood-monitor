# HƯỚNG DẪN THỰC THI GÁN NHÃN DỮ LIỆU ASTE (10.000 RECORDS - NHÓM 2 NGƯỜI)

> **Mục tiêu:** Trích xuất các bộ ba Triplet = `(Aspect, Opinion, Polarity)` từ 10.000 câu đánh giá.

---

## 1. TỔNG QUAN BÀI TOÁN ASTE

Mỗi mẫu cần gán nhãn bao gồm 3 thành phần:
* **Aspect Term ($a$):** Đối tượng / khía cạnh được nhắc tới 
* **Opinion Term ($o$):** Cụm từ thể hiện ý kiến / cảm nhận 
* **Sentiment Polarity ($s$):** Cảm xúc gắn với khía cạnh đó

---

## 2. KẾ HOẠCH PHÂN BỔ 10.000 RECORDS (3 GIAI ĐOẠN)

```text
[ 10.000 Records ]
   │
   ├── Phase 1: Pilot & Hiệu chỉnh Guideline (500 records)
   │     └── Cả 2 cùng gán nhãn -> Họp chốt quy tắc chung
   │
   ├── Phase 2: Gán nhãn kép Overlap để tính IAA (2.000 records - 20%)
   │     └── Cả 2 làm ĐỘC LẬP 100% -> Tính Cohen's Kappa & F1 đưa vào bài báo
   │
   └── Phase 3: Chia đôi làm độc lập (7.500 records còn lại)
         ├── Bạn A: 3.750 records
         └── Bạn B: 3.750 records
```

---

## 3. QUY TRÌNH THỰC HIỆN 4 BƯỚC (BẮT TAY LÀM NGAY)

### Bước 1: Setup
Chuẩn bị system prompt

---

### Bước 2: Chạy Phase 1 - Pilot (500 records đầu)
* Cả 2 bạn cùng xem 500 records đầu tiên.
* Họp lại và thống nhất các trường hợp gây tranh cãi.

---

### Bước 3: Chạy Phase 2 - Overlap (2.000 records tính chỉ số bài báo)
* **Quy tắc vàng:** **Tuyệt đối không trao đổi** trong suốt quá trình làm 2.000 records này.
* Sau khi cả 2 bạn nạp kết quả xong, chạy script Python để xuất ra bảng điểm:

```python
# Script tính Cohen's Kappa cho Polarity giữa 2 annotator
from sklearn.metrics import cohen_kappa_score

# label_1 và label_2 là danh sách nhãn Polarity (0: Negative, 1: Neutral, 2: Positive)
# trên các cặp (Aspect, Opinion) mà cả 2 bạn cùng bôi trùng khớp
kappa = cohen_kappa_score(labels_annotator_1, labels_annotator_2)
print(f"Cohen's Kappa (Polarity): {kappa:.3f}")
```

* **Ngưỡng đạt chuẩn bài báo:**
  * Strict F1 (Trùng 100% ranh giới từ & Polarity): $\ge 70\%$
  * Cohen's Kappa $\kappa$ (cho nhãn cảm xúc): $\ge 0.70$ (Substantial Agreement)
* **Xử lý bất đồng:** Những mẫu hai bạn gán lệch nhau sẽ nhờ **người thứ 3 (GVHD / Leader)** chọn nhãn cuối cùng.

---

### Bước 4: Chạy Phase 3 - Về đích (7.500 records còn lại)
* Chia đôi danh sách: Bạn A nhận từ record 2.501 đến 6.250; Bạn B nhận từ 6.251 đến 10.000.
* Mỗi người tự rà soát và sửa nhãn độc lập.
* Ghép toàn bộ dữ liệu lại để bắt đầu huấn luyện mô hình (Model Training).
