# BẢNG KẾT QUẢ THỰC NGHIỆM ĐỐI SÁNH KHOA HỌC (ACADEMIC BENCHMARK TABLE)
## Bài toán Aspect-Sentiment-Opinion Triplet Extraction (ASTE) trên HCMC Flood V3

> Đánh giá độc lập trên tập **Test Split**. Dữ liệu được chuẩn hóa và tách biệt hoàn toàn theo hai định dạng độc lập:
> 1. **Định dạng Cũ (Original Linearized/BIO Text Format)**: Đánh giá trên 462 mẫu văn bản, 636 bộ ba thực tế.
> 2. **Định dạng Mới (SemEval v2 Word Index Tuple Format)**: Đánh giá trên 462 mẫu văn bản, 573 bộ ba thực tế.

---

### PHẦN 1: BẢNG BENCHMARK TRÊN ĐỊNH DẠNG MỚI (SEMEVAL V2 FORMAT)
*Định dạng nhãn: `[([a_idxs], [o_idxs], 'POL')]` với ranh giới index từ rời rạc.*
*Cấu trúc mã nguồn & checkpoint: `AI/{model_family}/{variant}/semeval_v2/`*

| Phương pháp / Mô hình | Phân loại kiến trúc | Strict Precision (%) | Strict Recall (%) | **Strict Triplet F1 (%)** | Aspect F1 (%) | Opinion F1 (%) | POS F1 (%) | Macro Polarity F1 (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **PhoBERT Large** | *Extractive Span-Pair (Large)* | 42.19% | **42.41%** | **42.30%** 🏆 | **67.73%** | **52.49%** | 67.81% | **41.67%** |
| **XLM-RoBERTa Base** | *Extractive Span-Pair Multilingual* | 41.42% | 39.62% | **40.50%** 🥈 | 63.98% | 51.22% | 65.72% | 39.59% |
| **PhoBERT Base v2** | *Extractive Span-Pair (Base)* | **44.78%** | 36.65% | **40.31%** 🥉 | 64.48% | 48.79% | **69.09%** | 40.04% |
| **XLM-V Base** | *Extractive Span-Pair (1M Vocab)* | 42.74% | 35.43% | **38.74%** | 63.07% | 46.95% | 62.16% | 36.92% |
| **Gemma-4-26B** | *Zero-Shot LLM (MoE 26B-A4B)* | 22.45% | 18.85% | **20.49%** | 40.27% | 32.76% | 33.71% | 21.27% |
| **BARTpho Syllable Base** | *Generative Seq2Seq* | 22.36% | 14.33% | **17.47%** | 28.74% | 22.51% | 57.93% | 20.50% |
| **Qwen3.8-27B** | *Zero-Shot LLM (Reasoning 27B)* | 17.34% | 12.74% | **14.69%** | 34.96% | 32.19% | 25.60% | 14.97% |
| **mT5 Base** | *Generative Seq2Seq Multilingual* | — | — | ⏳ *Sẵn sàng huấn luyện* | — | — | — | — |
| **BARTpho Word Base** | *Generative Seq2Seq (Word Base)* | — | — | ⏳ *Sẵn sàng huấn luyện* | — | — | — | — |

---

### PHẦN 2: BẢNG BENCHMARK TRÊN ĐỊNH DẠNG CŨ (ORIGINAL LINEARIZED FORMAT)
*Định dạng nhãn: Chuỗi văn bản phân đoạn hoặc chuỗi sinh `(aspect | opinion | polarity)`.*
*Cấu trúc mã nguồn & checkpoint: `AI/{model_family}/{variant}/old/`*

| Phương pháp / Mô hình | Kiến trúc kỹ thuật | Strict Precision (%) | Strict Recall (%) | **Strict Triplet F1 (%)** | Aspect F1 (%) | Opinion F1 (%) | POS F1 (%) | Macro Polarity F1 (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **mT5 Base** | *Generative Seq2Seq Multilingual* | 43.78% | 41.57% | **42.65%** 🏆 | 71.21% | 54.63% | 68.82% | 42.97% |
| **XLM-V Base** | *Joint BIO + Span-Pair (1M Vocab)* | 35.40% | 44.88% | **39.58%** 🥈 | 64.92% | 51.29% | 62.62% | 39.50% |
| **XLM-RoBERTa Base** | *Joint BIO + Span-Pair Multilingual* | 32.00% | 42.92% | **36.67%** | 69.22% | 50.04% | 63.61% | 36.98% |
| **BARTpho Word Base** | *Generative Seq2Seq (Word Base)* | 41.50% | 32.28% | **36.32%** ⭐ | 62.63% | 51.37% | 68.63% | 38.54% |
| **BARTpho Syllable Base** | *Generative Seq2Seq (Syllable Base)* | 40.92% | 32.28% | **36.09%** ⭐ | 63.13% | 50.63% | 68.10% | 35.40% |
| **PhoBERT Base v2** | *Joint BIO + Span-Pair (Base)* | 25.27% | 43.55% | **31.99%** | 69.50% | 53.18% | 46.19% | 30.37% |
| **PhoBERT Large** | *Joint BIO + Span-Pair (Large)* | 24.88% | 42.45% | **31.38%** | 69.61% | 52.94% | 44.59% | 30.06% |
| **Gemma-4-26B** | *Zero-Shot LLM (MoE 26B-A4B)* | 15.94% | 17.80% | **16.82%** | 42.38% | 29.39% | 28.48% | 17.63% |
| **Qwen3.8-27B** | *Zero-Shot LLM (Reasoning 27B)* | 14.39% | 12.13% | **13.16%** | 36.90% | 30.10% | 22.94% | 13.52% |
| **Heuristic (Word Matching)** | *Lexicon + Distance Heuristic* | 10.47% | 27.40% | **15.15%** | 39.11% | 30.92% | 30.20% | 15.51% |

---

### PHẦN 3: CẤU TRÚC THƯ MỤC CHUẨN HÓA THEO ĐỊNH DẠNG (STANDALONE ARCHITECTURE)
Để đảm bảo tính toàn vẹn và dễ dàng kiểm tra, tất cả mô hình đều được phân tách rạch ròi thành 2 thư mục độc lập với mã nguồn riêng biệt:
```text
AI/
├── {model_family}/
│   └── {variant}/
│       ├── old/                    # Định dạng phân đoạn cũ (Text format)
│       │   ├── finetune/           # Kịch bản huấn luyện cũ & checkpoint cũ
│       │   └── test/               # Kịch bản đánh giá & báo cáo benchmark cũ
│       └── semeval_v2/             # Định dạng SemEval v2 mới (Index tuple format)
│           ├── finetune/           # Kịch bản huấn luyện mới độc lập & checkpoint mới
│           └── test/               # Kịch bản đánh giá mới độc lập & báo cáo SemEval v2
```
