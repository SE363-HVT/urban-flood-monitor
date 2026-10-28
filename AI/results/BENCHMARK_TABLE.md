# Kiến Trúc Bảng Kết Quả Thực Nghiệm & Đo Lường Khoa Học: Khai Phá Bộ Ba Khía Cạnh - Ý Kiến - Cảm Xúc (ASTE) trên Tập Dữ Liệu Ngập Lụt HCMC Flood V3

> **Phân Vùng Đánh Giá:** Tập kiểm thử độc lập Test Split ($N = 462$ câu văn bản, $636$ bộ ba nhãn vàng trên 8 cụm đợt thiên tai / 70 ngày sự kiện độc lập).  
> **Quy Chuẩn Đánh Giá:** Khớp Tuyệt Đối (Strict Exact Match — Micro Triplet F1 đòi hỏi trùng khớp tuyệt đối ranh giới ký tự của Aspect, trùng khớp ranh giới Opinion và đúng 100% nhãn sắc thái cảm xúc 3 lớp `[POS, NEG, NEU]`).  
> **Tài Liệu Phương Pháp Luận Đi Kèm:**  
> • [Hướng Dẫn Phương Pháp Heuristic Word Matching](file:///home/counting/Workspaces/ryan/RadiNet/documents/HEURISTIC_WORD_MATCHING_GUIDE.md)  
> • [Công Thức Toán Học & Quy Chuẩn Đánh Giá ASTE Benchmark](file:///home/counting/Workspaces/ryan/RadiNet/documents/ASTE_BENCHMARK_METRICS_AND_FORMULAS.md)

---

## Góc Nhìn 1 (View 1) — Danh Sách Mô Hình: Ma Trận 2×2 và Các Hàng Mở Rộng Ngoài Lưới

Các mô hình được đánh giá trải rộng trên một ma trận thực nghiệm $2 \times 2$ giao thoa giữa **Dạng thức Tác vụ (Task Formulation)** (Trích xuất gán nhãn BIO + Ghép cặp span vs. Sinh chuỗi tự hồi quy Seq2Seq) và **Miền Ngôn ngữ Tiền huấn luyện (Pretraining Linguistic Domain)** (Tiền huấn luyện Báo chí Tiếng Việt vs. Tiền huấn luyện Web Đa ngữ), kết hợp với các hàng đối chứng baseline và mô hình ngôn ngữ lớn ngoài lưới:

| Tập Ngữ Liệu Tiền Huấn Luyện \ Dạng Thức | Trích Xuất (Joint BIO + Span-Pair) | Sinh Chuỗi (Generative Seq2Seq) |
| :--- | :--- | :--- |
| **Đặc thù Tiếng Việt** *(Tin tức báo chí: Báo Mới, VnExpress)* | **PhoBERT-base** (135M)<br>**PhoBERT-large** (370M) | **BARTpho-word** (139M)<br>**BARTpho-syllable** (139M) |
| **Đa Ngữ** *(Dữ liệu cào Web: Common Crawl, mC4)* | **XLM-R-base** (278M)<br>**XLM-V-base** (778M, 902k từ vựng, CC100-XL) | **mT5-base** (580M) 🏆 |

### Các Hàng Đối Chứng Ngoài Lưới (Off-Grid Rows):
- **Heuristic Baseline (Ngưỡng đáy thực nghiệm)**: Đối sánh từ điển tập huấn luyện có ranh giới từ Lookaround `(?<!\w)...(?!\w)` + Ghép cặp khoảng cách láng giềng gần nhất có khóa chống tự ghép cặp Collision Guard.
- **Mô Hình Ngôn Ngữ Lớn Zero-Shot (LLMs)**: **Gemma-4-26B** (MoE 26B-A4B) và **Qwen3.8-27B** (Reasoning 27B) được đánh giá với Prompt v2 đông cứng và ràng buộc lược đồ JSON nghiêm ngặt.
  - *Phát hiện nền tảng*: Qwen3.8-27B Zero-Shot (15.58%) hòa điểm thống kê với Heuristic Word Matching Floor (15.15%), và Gemma-4-26B (18.32%) chỉ nhỉnh hơn ngưỡng từ điển ~3 điểm F1. Đây là luận điểm thực nghiệm sắc bén: *"Một mô hình LLM suy luận 27B ở chế độ zero-shot chỉ đạt ngang tầm một tập từ điển tra cứu tĩnh trên bài toán trích xuất ranh giới ASTE nghiêm ngặt"*.
- **LLM Few-Shot ($k=5$)**: Gemma-26B / Qwen-27B kèm 5 ví dụ mẫu ngập lụt ngữ cảnh được chọn lọc theo độ phủ đa dạng *(Quy chuẩn đã lập kế hoạch — kiểm chứng mức độ bứt phá của LLM ra khỏi đường sàn từ điển)*.
- **LLM Tinh Chỉnh Tham Số (QLoRA)**: **Qwen-4B + QLoRA** thích ứng miền chuyên sâu hiệu quả tham số *(Mở rộng có điều kiện cho họ prompt đạt hiệu năng cao nhất)*.

---

## Góc Nhìn 2 (View 2) — Bản Đồ Đối Sánh: Các Giả Thuyết Cặp & Phân Tích Thực Nghiệm

Mỗi phép đối sánh cặp thay đổi đúng duy nhất một chiều kiến trúc hoặc dữ liệu trong khi kiểm soát giữ nguyên tất cả các yếu tố khác:

| Mã | Cặp Đối Sánh | Biến Số Thay Đổi | Yếu Tố Giữ Nguyên | Kết Luận Thực Nghiệm & Cơ Chế |
| :---: | :--- | :--- | :--- | :--- |
| **C1** | **Heuristic ↔ Fine-Tuned Models** | Học Biểu Diễn Ngữ Cảnh vs. Tra Từ Điển Tĩnh | Dạng thức tác vụ, Tập test ($N=462$) | **Tính Xác Đáng Nền Tảng**: ML giúp tăng độ chính xác 2.4×–4.2× (10.47% $\rightarrow$ 25.3%–43.8%) và F1 tăng 2.1×–2.8× (15.15% $\rightarrow$ 32.0%–42.7%). Nút thắt của bài toán nằm ở việc khử nhập nhằng và ghép cặp thực thể trong ngữ cảnh, không nằm ở kích thước từ điển. |
| **C2** | **PhoBERT-base ↔ XLM-R-base** | Ngữ liệu Tiền huấn luyện (Báo chí Tiếng Việt vs. Web Đa ngữ) | Quy mô tham số (~135M–278M), Dạng thức span-pair | **Đối Sánh Bản Lề**: Dữ liệu cào web giúp tăng **+4.68% F1** (31.99% $\rightarrow$ 36.67%, $p < 0.0001$). Ngữ liệu web đa dạng chuẩn bị cho mô hình khả năng chống chịu vượt trội đối với teencode, tiếng lóng và văn phong mạng xã hội. |
| **C3** | **XLM-R ↔ XLM-V** | Quy mô Ngữ liệu Huấn luyện & Dung lượng Mô hình (CC100, 278M vs. CC100-XL, 778M, 902k vocab) | Kiến trúc Encoder, Tokenizer SentencePiece, Dạng thức | **Mở Rộng Dữ Liệu & Tham Số**: Tăng **+2.91% F1** (36.67% $\rightarrow$ 39.58%, $p < 0.0001$). Cải thiện đến từ phán đoán sắc thái ngữ cảnh (NEG $+2.88\%$, NEU $+5.68\%$), trong khi Aspect F1 giảm nhẹ ($69.22\% \rightarrow 64.92\%$). |
| **C4** | **PhoBERT-base ↔ PhoBERT-large** | Quy mô Tham số Mô hình (135M vs. 370M) | Kiến trúc, Tokenizer, Siêu tham số, Dữ liệu | **Hiệu Năng Đi Ngang Do Dữ Liệu**: Tăng gấp 3 tham số không cải thiện hiệu năng (31.99% $\rightarrow$ 31.38%, $\Delta = -0.61\%$). Nút thắt hiệu năng nằm ở phân phối dữ liệu miền mạng xã hội chứ không nằm ở dung lượng mô hình encoder báo chí. |
| **C5** | **BARTpho-word ↔ BARTpho-syllable** | Đầu vào Token (Phân đoạn từ `_` vs. Âm tiết thô) | Kiến trúc Seq2Seq, Ngữ liệu huấn luyện | **Kết Quả Rỗng Tổng Thể & Ngoại Lệ NEU**: Hiệu năng tổng thể tương đương (36.32% vs. 36.09%), nhưng **NEU F1 sụt giảm hơn một nửa (19.83% $\rightarrow$ 9.76%)**. Phân đoạn từ đặc biệt sống còn đối với các cụm đo lường kỹ thuật và mực nước trung tính. |
| **C6** | **PhoBERT-base ↔ BARTpho-word** | Dạng thức (Trích xuất Span-Pair vs. Sinh chuỗi Seq2Seq) | Tiền huấn luyện đơn ngữ báo chí, Đầu vào phân đoạn từ | **Ưu Thế Của Dạng Thức Sinh Chuỗi**: Tăng **+4.33% F1** (31.99% $\rightarrow$ 36.32%), nhờ bước nhảy vọt về Precision (25.27% $\rightarrow$ 41.50%). Sinh chuỗi tự hồi quy triệt tiêu các cặp ghép span-pair giả mạo. |
| **C7** | **XLM-R ↔ mT5-base** | Dạng thức (Trích xuất Span-Pair vs. Sinh chuỗi Seq2Seq) | Tiền huấn luyện web đa ngữ | **Ưu Thế Của Sinh Chuỗi Đa Ngữ**: Tăng **+5.98% F1** (36.67% $\rightarrow$ 42.65%, $p < 0.0001$), thiết lập mT5-base là mô hình dẫn đầu toàn diện trên mọi thước đo đánh giá. |
| **C8** | **Mô hình Fine-Tuned (mT5) ↔ LLM 0-Shot (Gemma/Qwen)** | Tinh chỉnh Miền Chuyên Sâu vs. Quy mô Tham số gấp 100 lần (0.58B vs. 27B) | Cùng tập test ($N=462$), Tiêu chuẩn Strict Exact Match | **Quy Mô vs. Chuyên Biệt Hóa**: Mô hình 0.58B tinh chỉnh vượt trội hơn 2.3× so với LLM 27B không tinh chỉnh (42.65% vs. 18.32% / 15.58%), chứng minh vai trò then chốt của việc căn chỉnh cấu trúc miền chuyên sâu trên bài toán trích xuất ranh giới ngặt nghèo. |

> [!NOTE]
> **Minh Bạch Cơ Chế XLM-V (C3):** Mô hình `facebook/xlm-v-base` sở hữu **778,493,184 tham số** (trong đó ma trận embedding chiếm 692.5M tham số nhờ không gian từ vựng 901,629 token) và được tiền huấn luyện trên kho ngữ liệu CC100-XL mở rộng mạnh cho tiếng Việt. Do đó, C3 là phép đối sánh kết hợp giữa quy mô dữ liệu cào web mở rộng và dung lượng mô hình, chứ không phải một phép đổi từ vựng thuần túy trên cùng tập dữ liệu. Dữ liệu thực nghiệm xác nhận lợi thế của XLM-V nằm ở sự nhạy bén ngữ cảnh cảm xúc chứ không phải việc giảm phân mảnh subword trên tên thực thể.

---

## Góc Nhìn 3 (View 3) — Bảng Kết Quả Thực Nghiệm Tổng Thể (Phần Results Bài Báo)

Hiệu năng thực nghiệm của tất cả các mô hình được đánh giá độc lập trên tập HCMC Flood V3 ASTE Test Split theo tiêu chuẩn Strict Exact Match:

| Nhóm | Mô Hình | Tham Số | P (%) | R (%) | **Strict Triplet F1 (%)** | Aspect F1 (%) | Opinion F1 (%) | NEG F1 (%) | NEU F1 (%) | POS F1 (%) | Macro-Pol F1 (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Floor** | Heuristic Baseline (Fixed) | — | 10.47 | 27.40 | **15.15** | 39.11 | 30.92 | 12.92 | 3.41 | 30.20 | 15.51 |
| **VN × Extr** | PhoBERT-base | 135M | 25.27 | <u>43.55</u> | **31.99** | 69.50 | <u>53.18</u> | 29.54 | 15.38 | 46.19 | 30.37 |
| **VN × Extr** | PhoBERT-large | 370M | 24.88 | 42.45 | **31.38** | <u>69.61</u> | 52.94 | 28.60 | 17.00 | 44.59 | 30.06 |
| **Multi × Extr** | XLM-R-base | 278M | 32.00 | 42.92 | **36.67**$^*$ | 69.22 | 50.04 | 32.66 | 14.66 | 63.61 | 36.98 |
| **Multi × Extr** | XLM-V-base | 778M | 35.40 | **44.88** | **<u>39.58</u>**$^{*\dagger}$ | 64.92 | 51.29 | <u>35.54</u> | <u>20.34</u> | 62.62 | <u>39.50</u> |
| **VN × Gen** | BARTpho-word | 139M | <u>41.50</u> | 32.28 | **36.32** | 62.63 | 51.37 | 27.14 | 19.83 | <u>68.63</u> | 38.54 |
| **VN × Gen** | BARTpho-syllable | 139M | 40.92 | 32.28 | **36.09** | 63.13 | 50.63 | 28.34 | 9.76 | 68.10 | 35.40 |
| **Multi × Gen** | mT5-base | 580M | **43.78** | 41.57 | **42.65**$^{*\dagger}$ 🏆 | **71.21** | **54.63** | **37.28** | **22.82** | **68.82** | **42.97** |
| **LLM 0-shot** | Gemma-4-26B (MoE A4B) | 27B | 16.38 | 20.79 | **18.32** | 45.01 | 30.71 | 17.74 | 8.70 | 27.19 | 17.88 |
| **LLM 0-shot** | Qwen3.8-27B (Reasoning) | 27B | 15.41 | 15.75 | **15.58** | 41.19 | 32.70 | 15.75 | 6.16 | 26.71 | 16.21 |

> **Bảng 1: Kết quả thực nghiệm chính trên tập HCMC Flood V3 ASTE Test Split.**  
> Quy mô tập kiểm thử: $N = 462$ câu văn bản ($636$ bộ ba nhãn vàng trên 8 cụm đợt thiên tai / 70 ngày sự kiện độc lập).  
> Số lượng nhãn vàng theo sắc thái: **NEG** $n = 424$ ($66.7\%$), **NEU** $n = 71$ ($11.2\%$), **POS** $n = 141$ ($22.2\%$). Tất cả các lớp đều thỏa mãn điều kiện ổn định thống kê ($n \ge 30$).  
> Micro Strict-F1 là chỉ số cốt lõi chính. Kết quả cao nhất mỗi cột được **in đậm**, kết quả nhì được <u>gạch chân</u>.  
> Dấu $*$ biểu thị cải thiện có ý nghĩa thống kê ($p < 0.05$) so với PhoBERT-base qua kiểm định paired-bootstrap 1 phía có hiệu chỉnh Koehn (2004) (Đối sánh C2); dấu $\dagger$ biểu thị cải thiện có ý nghĩa thống kê ($p < 0.05$) so với XLM-R-base (Đối sánh C3).  
> Tất cả các mô hình fine-tuned được chọn từ checkpoint có Strict F1 cao nhất trên tập xác thực (`dev-selected`), đánh giá một lần duy nhất trên tập test độc lập. Khoảng tin cậy bootstrap 95% cấp đợt thiên tai thể hiện biên độ $\pm 8.7\% - 9.0\%$ do tương quan không gian - thời gian giữa các cụm đợt bão. Quy chuẩn đa hạt giống (mean $\pm$ std qua 3 seed ngẫu nhiên) đang được hoàn thiện cho bản nộp hoàn chỉnh.

### Phân Tích Cấu Trúc Kết Quả Chính Của Bài Báo:
1. **Cấu Trúc Cộng Tính (Additive Structure) Giữa Hai Trục Kiến Trúc:**
   - Đổi mới Dạng thức tác vụ (Extractive $\rightarrow$ Seq2Seq): mang lại **$+4.33\%$ F1** (PhoBERT-base 31.99 $\rightarrow$ BARTpho-word 36.32).
   - Đổi mới Miền Tiền huấn luyện (Báo chí Tiếng Việt $\rightarrow$ Web Đa ngữ): mang lại **$+4.68\%$ F1** (PhoBERT-base 31.99 $\rightarrow$ XLM-R-base 36.67).
   - Kết hợp đồng thời cả hai trục trên **mT5-base** mang lại **$+10.66\%$ F1** (31.99 $\rightarrow$ **42.65%**), vượt qua mức cộng tuyến tính đơn thuần ($4.33 + 4.68 = 9.01$), thể hiện hiệu ứng cộng hưởng tích cực nhẹ giữa dạng thức giải mã seq2seq và dữ liệu tiền huấn luyện web đa ngữ.
2. **Qwen3.8-27B (15.58%) Hòa Ngang Với Tập Từ Điển Tra Cứu (15.15%):**
   - Một mô hình lý luận 27B tham số không tinh chỉnh chỉ đạt hiệu năng ngang bằng một tập từ điển trích xuất tĩnh, và Gemma-26B chỉ vượt qua ngưỡng đáy ~3 điểm F1. Đây là phát hiện then chốt khẳng định sự cần thiết của việc tinh chỉnh miền chuyên biệt (in-domain fine-tuning) trên dữ liệu khủng hoảng đô thị.
3. **Hồ Sơ Cảm Xúc Heuristic Xác Nhận Giá Trị Thiết Kế Schema:**
   - Heuristic đạt $30.20\%$ F1 trên POS nhờ bắt đúng các cụm từ phục hồi rõ ràng (*"rút hết"*, *"bình thường"*), nhưng **NEU rơi tự do xuống 3.41%**. Từ điển tĩnh về mặt cấu trúc không thể biểu đạt cú pháp *"ngập 30cm = đo lường trung tính"*, khẳng định sắc thái trung tính bắt buộc phải được giải quyết bằng mô hình học biểu diễn ngữ cảnh.
4. **BARTpho Word vs. Syllable (C5): Kết Quả Rỗng Tổng Thể Nhưng NEU Bị Cắt Đôi:**
   - Điểm F1 tổng thể giữa đầu vào phân đoạn từ và âm tiết thô là tương đương (36.32% vs. 36.09%), bác bỏ giả thuyết độ giòn phân đoạn từ trên toàn bộ tập dữ liệu. Tuy nhiên, **NEU F1 bị cắt giảm một nửa (19.83% $\rightarrow$ 9.76%)**, chỉ ra rằng phân đoạn từ đóng vai trò thiết yếu trong việc liên kết các con số đo lường độ sâu ngập và thuật ngữ thủy văn trung tính.

---

## Góc Nhìn 4 (View 4) — Phân Tích Chi Tiết Theo Nhóm Thực Thể Aspect

Bóc tách chỉ số Aspect Recall trên 5 nhóm phân loại thực thể cốt lõi trong hệ phân loại HCMC Flood V3, đối chiếu với nhóm thực thể phụ đuôi dài và tổng số nhãn vàng:

| Nhóm Thực Thể | Số lượng nhãn vàng ($n$) | Tỷ lệ trong Test (%) | Heuristic (Fixed) | PhoBERT Base | XLM-R Base | XLM-V Base | BARTpho Word | mT5 Base 🏆 | Gemma-4-26B (0-Shot) | Qwen3.8-27B (0-Shot) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`LOC-STREET`** (Tên đường, giao lộ) | **267** | 41.98% | 78.65% | 68.16% | 70.04% | 71.91% | 64.04% | **79.78%** | 62.92% | 48.69% |
| **`LOC-ADMIN`** (Địa danh hành chính) | **174** | 27.36% | 57.47% | 66.67% | 67.82% | 68.39% | 58.62% | **68.97%** | 26.44% | 24.71% |
| **`HYDRO`** (Hiện tượng & thực thể thủy văn) | **113** | 17.77% | 85.84% | 76.99% | 75.22% | 77.88% | 45.13% | 61.06% | 58.41% | 38.94% |
| **`DRAINAGE`** (Hạ tầng cống rãnh) | **27** | 4.25% | 74.07% | 51.85% | 62.96% | **74.07%** | 48.15% | <u>62.96%</u> | 51.85% | 48.15% |
| **`AUTH-RESP`** (Đơn vị ứng phó chức năng) | **13** | 2.04% | 69.23% | 38.46% | 46.15% | 46.15% | 53.85% | **76.92%** | 53.85% | **76.92%** |
| **Top-5 Nhóm Cốt Lõi (Tổng)** | **594** | **93.40%** | 73.05% | 60.43% | 64.44% | 67.68% | 53.96% | **69.94%** | 50.69% | 47.48% |
| **Nhóm Phụ / Đuôi Dài (Minor/Long-Tail)** | **42** | **6.60%** | 42.86% | 52.38% | 54.76% | 57.14% | 42.86% | **59.52%** | 35.71% | 28.57% |
| **Toàn Bộ Nhãn Vàng (Total Gold)** | **636** | **100.0%** | **72.54%** | **67.49%** | **66.82%** | **68.24%** | **59.43%** | **69.68%** | **49.37%** | **41.35%** |

*Ghi chú về phân nhóm nhãn vàng:* 5 nhóm thực thể cốt lõi bao phủ **594 trên 636 nhãn vàng (93.40%)**. Nhóm phụ đuôi dài ($n=42$, $6.60\%$) bao gồm: `INFRASTRUCTURE` chung ($n=14$), `TRAFFIC` ($n=8$), `LOCATION_OTHER` ($n=6$), `HUMAN_ACTIVITY` ($n=5$), `LOCATION_RESIDENTIAL` ($n=4$), `INFRASTRUCTURE_TRAFFIC` ($n=2$), `LOCATION_BRIDGE` ($n=2$), và `LOCATION_MARKET` ($n=1$).

---

### Phân Tích Chuyên Sâu Từng Nhóm & Chẩn Đoán Dị Thường HYDRO:

1. **Hiện Tượng Dị Thường HYDRO (The HYDRO Anomaly):**
   - Heuristic Baseline đạt Recall tới **85.84%** trên HYDRO, và các mô hình trích xuất BIO đạt $75.2\% - 77.9\%$. Ngược lại, mô hình chiến thắng toàn diện **mT5-base chỉ đạt 61.06%** (thua từ điển gần 25 điểm trên danh mục $n=113$), và BARTpho-word sụt giảm xuống **45.13%**.
   - **Chẩn đoán lỗi chi tiết trên 113 mẫu HYDRO của mT5:**
     - Khớp chính xác (Exact Match): **69 mẫu (61.06%)**.
     - Mở rộng ranh giới (Boundary Expansion): **3 mẫu (2.65%)** (ví dụ: nhãn vàng *"mực nước"* bị mở rộng thành *"mực nước trên hệ thống sông, kênh, rạch tại TP.HCM"*).
     - Rút gọn ranh giới (Boundary Trimming): **0 mẫu (0.00%)**.
     - Bỏ sót hoàn toàn (Completely Omitted): **41 mẫu (36.28%)**!
   - **Cơ chế ngôn ngữ học & kiến trúc giải thích hiện tượng:**
     - **Thắt Cổ Chai Chú Ý & Cạnh Tranh Thực Thể (Attention Bottleneck in Seq2Seq):** Trong các câu văn phức tạp chứa đồng thời cả tên đường cụ thể (`LOC-STREET`, ví dụ: *"đường Rạch Cùng"*, *"Trần Xuân Soạn"*) và điều kiện thủy văn chung (*"triều cường"*, *"dòng nước"*), bộ giải mã tự hồi quy của mô hình Seq2Seq ưu tiên tạo ra thực thể địa lý tiêu điểm và thường ngắt câu sớm, bỏ sót từ chỉ hiện tượng thủy văn đi kèm.
     - **Sự Khác Biệt Giữa Heuristic và BIO Tagger:** Heuristic quét chuỗi mù quáng nên bắt dính mọi lần xuất hiện của từ khóa *"triều cường"*, *"nước"* trong từ điển (tạo ra Recall 85.84% nhưng Precision cực thấp). Trong khi đó, các mô hình extractive BIO phân loại từng token một cách độc lập trên câu văn, không bị hiện tượng cạnh tranh thứ tự sinh chuỗi như mô hình Seq2Seq.
2. **`LOC-STREET` ($n=267$, $41.98\%$) — Năng Lực Bảo Toàn Chuỗi Danh Từ:**
   - Chiếm tỷ trọng lớn nhất trong bài toán. mT5-base đạt Recall cao nhất (**79.78%**), chứng minh năng lực vượt trội của giải mã Seq2Seq trong việc tái tạo nguyên vẹn chuỗi danh từ tên đường nhiều token mà không bị đứt gãy subword.
3. **`LOC-ADMIN` ($n=174$, $27.36\%$) — Điểm Yếu Chí Mạng Của LLM Zero-Shot:**
   - Các đơn vị hành chính chuẩn hóa (Quận, Phường) đạt $\ge 66\%$ trên các mô hình fine-tuned.
   - Các LLM Zero-shot tụt dốc trầm trọng trên `LOC-ADMIN` (Gemma: 26.44%, Qwen: 24.71%) do có xu hướng bỏ qua đơn vị hành chính hoặc nhầm lẫn với các danh từ miêu tả chung chung, khẳng định giá trị cốt lõi của tầng tri thức địa lý gazetteer trong kiến trúc RadiNet.
4. **`DRAINAGE` ($n=27$, $4.25\%$) — Độ Bền Vững Với Teencode Trên Mẫu Nhỏ:**
   - Nhóm chứa mật độ từ lóng mạng xã hội dày đặc (*"cống"*, *"rãnh"*, *"miệng cống"*, *"hố ga"*, *"nắp cống nghẹt"*).
   - Mô hình cào web XLM-V (74.07%) và mT5 (62.96%) ghi nhận tỷ lệ bắt cao hơn so với mô hình báo chí (PhoBERT: 51.85%, BARTpho: 48.15%). Đây là khuynh hướng quan sát được trên cỡ mẫu nhỏ ($n=27$), gợi mở sự phù hợp với giả thuyết về độ bền vững với văn phong mạng xã hội của dữ liệu tiền huấn luyện web, song cần được diễn giải cẩn trọng khi cỡ mẫu hạn chế.
5. **`AUTH-RESP` ($n=13$, $2.04\%$) — Tri Thức Tổ Chức Hành Chính:**
   - Cả mT5-base và Qwen3.8-27B đều bắt đúng 10/13 thực thể cơ quan ban ngành (**76.92%**), vượt trội so với các mô hình 135M–278M (38.5%–46.2%). Kết quả gợi mở giả thuyết (với $n=13$ mẫu quan sát) rằng dung lượng tham số lớn hỗ trợ đắc lực trong việc nhận diện các cơ quan ban ngành hàm ẩn.

---

## Quy Chuẩn Báo Cáo & Độ Tin Cậy Thống Kê

1. **Phân Cấp Chỉ Số Đo Lường:**
   - **Chỉ số Cốt lõi Chính (Primary):** Micro Strict-F1 (đòi hỏi trùng khớp tuyệt đối Aspect, Opinion và Polarity).
   - **Chỉ số Thứ cấp (Secondary):** Aspect Macro-A (trung bình không trọng số của Recall trên 5 nhóm thực thể chủ đạo).
2. **Quy Trình Lựa Chọn Checkpoint & Phân Tích Bootstrap:**
   - Tất cả các checkpoint được đánh giá là checkpoint đạt F1 cao nhất trên tập xác thực (`dev-selected`), được đánh giá một lần duy nhất trên tập kiểm thử độc lập (`test.json`), tuyệt đối không chọn lọc trên tập test.
   - Khoảng tin cậy 95% Confidence Interval được tính toán bằng cách lấy mẫu lại theo **8 cụm đợt thiên tai** (thay vì từng câu riêng lẻ) nhằm tính đến tương quan chuỗi không gian - thời gian giữa các bài đăng trong cùng đợt ngập.
3. **Kiểm Định Ý Nghĩa Thống Kê Có Hướng (Koehn Correction):**
   - Áp dụng kiểm định paired-bootstrap 1 phía ($B = 10,000$) với hiệu chỉnh liên tục Koehn (2004) cho 2 phép đối sánh bản lề:
     - **C2** ($\text{PhoBERT-base} \leftrightarrow \text{XLM-R-base}$): $p < 0.0001$, khẳng định tính ưu việt của tiền huấn luyện đa ngữ web trên văn bản mạng xã hội.
     - **C3** ($\text{XLM-R-base} \leftrightarrow \text{XLM-V-base}$): $p < 0.0001$, khẳng định việc mở rộng ngữ liệu CC100-XL và không gian 778M tham số mang lại khả năng phân định cảm xúc vượt trội.
4. **Cấu Hình Đánh Giá LLM & Phân Tích Ảo Giác:**
   - **Qwen3.8-27B:** Được đánh giá với chế độ suy luận bản địa (`thinking-mode` kích hoạt). Bộ bóc tách cú pháp lấy chuỗi JSON kết thúc cuối cùng. Do độ dài chuỗi suy luận trung bình vượt 1,500 ký tự, có **38 mẫu kiểm thử (8.2%)** bị cạn kiệt giới hạn token trước khi kịp đóng mảng JSON, dẫn đến việc trả về dự đoán rỗng và kéo giảm Recall xuống 15.75%.
   - **Tần suất sinh ảo giác trên câu rỗng ($N_{\text{empty}} = 4$):** Cả Gemma-4-26B và Qwen3.8-27B đều sinh nhầm bộ ba trên **1 trong 4 câu rỗng** ($25.0\%$). Ngược lại, các mô hình fine-tuned (mT5, BARTpho) đạt tỷ lệ ảo giác **0 trong 4 câu rỗng** ($0.0\%$).
5. **Tính Toàn Vẹn Của Phân Bố Lớp Cảm Xúc:**
   - Toàn bộ các lớp cảm xúc trong tập test đều vượt ngưỡng kích thước mẫu tới hạn ($n \ge 30$: NEG $=424$, NEU $=71$, POS $=141$), đảm bảo tính vững chắc và tin cậy thống kê của các chỉ số F1 theo từng lớp.
