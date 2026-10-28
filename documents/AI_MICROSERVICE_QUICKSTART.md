# 🚀 Hướng Dẫn Khởi Chạy AI Microservice (Windows — Cổng 8001)

Tài liệu rút gọn 4 bước dành cho đồng đội tích hợp mô hình AI vào hệ thống RadiNet trên hệ điều hành **Windows**.

> [!IMPORTANT]
> **LUÔN BẬT MÔI TRƯỜNG ẢO `.venv` TRƯỚC KHI THỰC HIỆN BẤT KỲ THAO TÁC NÀO!**

---

### Bước 1: Clone mã nguồn & chuyển sang nhánh `hung`
Mở **Windows Terminal** (PowerShell hoặc CMD):
```powershell
git clone https://github.com/SE363-HVT/urban-flood-monitor.git
cd urban-flood-monitor
git checkout hung
```

---

### Bước 2: Bật `.venv` & Cài đặt môi trường

#### 2.1. Kích hoạt môi trường ảo `.venv` (Bắt buộc)
```powershell
# Nếu chưa có thư mục .venv thì tạo mới:
python -m venv .venv

# Trên PowerShell (bật .venv):
.\.venv\Scripts\Activate.ps1

# (Nếu PowerShell báo lỗi Script Execution Policy, chạy lệnh này 1 lần:
#  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass rồi chạy lại lệnh Activate.ps1)

# Hoặc nếu dùng CMD (Command Prompt):
.venv\Scripts\activate.bat
```
*(Khi terminal hiện tiền tố `(.venv)` ở đầu dòng là đã kích hoạt thành công!)*

#### 2.2. Cài đặt các thư viện AI
```powershell
# Cài đặt thư viện Python trong .venv:
pip install torch transformers fastapi uvicorn pillow opencv-python yt-dlp

# Cài đặt ffmpeg trên Windows để tách âm thanh video (chọn 1 trong 2):
winget install Gyan.FFmpeg
# Hoặc nếu máy có Chocolatey: choco install ffmpeg
```

---

### Bước 3: Copy 2 file Checkpoint vào đúng thư mục
Bạn chỉ cần nhận **2 file trọng số** từ Hưng và thả vào đúng 2 thư mục sau:

1. **Branch 1 (Fast Path — PhoBERT)**:
   * Thư mục: `AI\phobert\base_v2\finetune\checkpoints\`
   * File cần đặt: **`best_phobert_aste.pt`**

2. **Branch 2 (Slow Path — BARTpho)**:
   * Thư mục: `AI\bartpho\syllable_base\finetune\checkpoints\best_aste_model\`
   * File cần đặt: **`model.safetensors`** *(hoặc `pytorch_model.bin`)*

*(Lưu ý: Hai mô hình `CLIP ViT-B/32` và `PhoWhisper-base` sẽ **tự động tải** từ Hugging Face trong lần chạy đầu tiên, bạn không cần chép tay).*

---

### Bước 4: Khởi chạy AI Microservice
Đảm bảo đang ở trong `(.venv)`, gõ lệnh:
```powershell
python bigdata\ai_service\ai_microservice.py --port 8001
```

Hoặc khởi chạy đồng bộ cùng pipeline:
```powershell
python bigdata\run_streaming_pipeline.py --enable_ai
```

---

### 🔍 Kiểm tra dịch vụ hoạt động

Mở một cửa sổ PowerShell khác (hoặc trình duyệt web):

```powershell
# 1. Kiểm tra trạng thái mô hình (trên trình duyệt: http://localhost:8001/health)
curl.exe http://localhost:8001/health

# 2. Chạy thử trích xuất Fast Path (< 35ms)
curl.exe -X POST http://localhost:8001/api/v1/predict-fast `
     -H "Content-Type: application/json" `
     -d "{\"text\": \"Đường Võ Văn Ngân ngập sâu lút bánh xe, chết máy hàng loạt\"}"
```

> **Cơ chế An toàn (Zero Downtime):**  
> Nếu bạn chưa kịp copy file checkpoint, server vẫn sẽ khởi động bình thường ở chế độ `mock_fallback` để không làm đứt gãy luồng xử lý Kafka/PySpark. Khi bạn copy file vào và khởi động lại, hệ thống sẽ tự động kích hoạt Deep Learning thật $100\%$.
