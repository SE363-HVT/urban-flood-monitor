# 🌊 Generative ASTE Fine-tuning Suite for Urban Flood Monitoring (TP.HCM)

> **Mục tiêu:** Cung cấp bộ công cụ huấn luyện, kiểm thử và tích hợp mô hình **Generative Aspect Sentiment Triplet Extraction (Text-to-Triplet)** trên tập dữ liệu ngập lụt đô thị TP.HCM phục vụ bài báo khoa học.

---

## 📁 Cấu trúc thư mục `finetune/`

```text
finetune/
├── data/
│   ├── train.json            # 2,283 mẫu huấn luyện (80%)
│   ├── val.json              # 285 mẫu kiểm định (10%)
│   └── test.json             # 286 mẫu kiểm thử độc lập (10%)
├── checkpoints/              # Thư mục lưu mô hình tốt nhất sau khi train
│   └── best_aste_model/      # Trọng số PyTorch + Tokenizer
├── prepare_dataset.py        # Tiền xử lý & phân tách dữ liệu từ data/processed/
├── train_generative_aste.py  # Script huấn luyện chính trên GPU (CUDA FP16)
├── inference.py              # Script suy luận thời gian thực & demo câu mới
├── evaluate_aste.py          # Đo Precision, Recall, F1 trên tập Test
└── README.md                 # Hướng dẫn chi tiết này
```

---

## 🚀 Hướng dẫn thực thi từng bước (Step-by-Step)

Sử dụng môi trường Python đã cài sẵn PyTorch CUDA:
```bash
PYTHON_BIN="/home/counting/anaconda3/envs/ryan_env/bin/python"
```

### Bước 1: Chuẩn bị dữ liệu
*(Đã được thực hiện sẵn, có thể chạy lại bất cứ lúc nào nếu cập nhật dataset)*
```bash
$PYTHON_BIN finetune/prepare_dataset.py
```

### Bước 2: Huấn luyện mô hình (Training)
Chạy huấn luyện trên GPU NVIDIA RTX 2080 Ti (sử dụng FP16 mixed precision):

```bash
$PYTHON_BIN finetune/train_generative_aste.py \
    --model_name "vinai/bartpho-syllable" \
    --epochs 6 \
    --batch_size 8 \
    --learning_rate 5e-5 \
    --output_dir "finetune/checkpoints/best_aste_model"
```

* Thời gian huấn luyện dự kiến: **~20 – 35 phút** trên card GPU RTX 2080 Ti.
* Checkpoint tối ưu (theo validation loss) sẽ tự động được lưu vào `finetune/checkpoints/best_aste_model/`.

### Bước 3: Thử nghiệm suy luận trên câu mới (Inference)
Sau khi train xong, kiểm thử khả năng bóc tách bộ ba trên các câu thực tế:

```bash
$PYTHON_BIN finetune/inference.py
```

Ví dụ kết quả sinh ra:
```text
Câu gốc : "Đường Võ Văn Ngân nước chảy như thác đổ, xe máy chết máy dắt bộ bì bõm."
Chuỗi sinh: "(Võ Văn Ngân | ngập lút bánh xe | NEG) ; (phương tiện giao thông | chết máy | NEG)"
Triplets  : [
  {"aspect": "Võ Văn Ngân", "opinion": "ngập lút bánh xe", "polarity": "NEG"},
  {"aspect": "phương tiện giao thông", "opinion": "chết máy", "polarity": "NEG"}
]
```

### Bước 4: Đo đạc chỉ số học thuật cho bài báo (Benchmark Evaluation)
Chạy script đánh giá trên 286 mẫu của tập Test:

```bash
$PYTHON_BIN finetune/evaluate_aste.py
```

Kết quả sẽ xuất ra bảng chuẩn để đưa vào Paper:
* **Triplet F1 (Exact Match):** Độ chính xác toàn diện của bộ ba.
* **Aspect F1:** Độ chính xác phát hiện tên đường/đối tượng ngập.
* **Opinion F1:** Độ chính xác nhận diện mức độ nghiêm trọng.

---

## 🧩 Tích hợp vào Pipeline RadiNet (`event_processor.py`)

Sau khi huấn luyện thành công, trong [`pipeline/event_processor.py`](../pipeline/event_processor.py), bạn chỉ cần thay hàm heuristic bằng `ASTEPredictor`:

```python
from finetune.inference import ASTEPredictor

# Khởi tạo mô hình một lần duy nhất lúc khởi động
ASTE_PREDICTOR = ASTEPredictor(checkpoint_dir="finetune/checkpoints/best_aste_model")

def analyze_severity_deep_learning(text: str):
    res = ASTE_PREDICTOR.predict(text)
    triplets = res.get("triplets", [])
    if not triplets:
        return None
    
    # Lấy bộ ba đầu tiên làm đại diện hoặc tổng hợp trọng số
    primary = triplets[0]
    return {
        "aspect": primary["aspect"],
        "opinion": primary["opinion"],
        "sentiment": primary["polarity"].lower(),
        "triplets": triplets
    }
```
