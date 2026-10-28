# 🚀 Hướng Dẫn Nhanh Khởi Chạy AI Microservice (Cổng 8001)

Tài liệu rút gọn 4 bước dành cho đồng đội tích hợp mô hình AI vào hệ thống RadiNet.

---

### Bước 1: Clone mã nguồn & chuyển sang nhánh `hung`
```bash
git clone https://github.com/SE363-HVT/urban-flood-monitor.git
cd urban-flood-monitor
git checkout hung
```

---

### Bước 2: Cài đặt môi trường
Chạy 2 lệnh dưới đây để cài các thư viện AI và công cụ xử lý video/âm thanh:

```bash
# 1. Cài thư viện Python cho AI & Microservice
pip install torch transformers fastapi uvicorn pillow opencv-python yt-dlp

# 2. Cài ffmpeg để bóc âm thanh từ video (trên Ubuntu / Debian)
sudo apt update && sudo apt install -y ffmpeg
```

---

### Bước 3: Copy 2 file Checkpoint vào đúng thư mục
Bạn chỉ cần nhận **2 file trọng số** từ Hưng và thả vào đúng 2 đường dẫn sau:

1. **Branch 1 (Fast Path — PhoBERT)**:
   * Thư mục: `AI/phobert/base_v2/finetune/checkpoints/`
   * File cần đặt: **`best_phobert_aste.pt`**

2. **Branch 2 (Slow Path — BARTpho)**:
   * Thư mục: `AI/bartpho/syllable_base/finetune/checkpoints/best_aste_model/`
   * File cần đặt: **`model.safetensors`** *(hoặc `pytorch_model.bin`)*

*(Lưu ý: Hai mô hình `CLIP ViT-B/32` và `PhoWhisper-base` sẽ **tự động tải** từ Hugging Face trong lần chạy đầu tiên, bạn không cần chép tay).*

---

### Bước 4: Khởi chạy AI Microservice
```bash
python bigdata/ai_service/ai_microservice.py --port 8001
```

Hoặc khởi chạy đồng bộ cùng pipeline streaming:
```bash
python bigdata/run_streaming_pipeline.py --enable_ai
```

---

### 🔍 Kiểm tra dịch vụ hoạt động

Mở một terminal khác và chạy lệnh test nhanh:

```bash
# 1. Kiểm tra trạng thái mô hình
curl http://localhost:8001/health

# 2. Chạy thử trích xuất Fast Path (< 35ms)
curl -X POST http://localhost:8001/api/v1/predict-fast \
     -H "Content-Type: application/json" \
     -d '{"text": "Đường Võ Văn Ngân ngập sâu lút bánh xe, chết máy hàng loạt"}'
```

> **Cơ chế An toàn (Zero Downtime):**  
> Nếu bạn chưa kịp copy file checkpoint, server vẫn sẽ khởi động bình thường ở chế độ `mock_fallback` để không làm đứt gãy luồng xử lý Kafka/PySpark. Khi bạn copy file vào và khởi động lại, hệ thống sẽ tự động kích hoạt Deep Learning thật $100\%$.
