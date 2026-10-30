# 📂 CẨM NANG ĐIỀU HƯỚNG THƯ MỤC SCRIPTS (SE363 - RADINET)

Thư mục `scripts/` đã được phân loại thành các thư mục con chuyên biệt để dễ dàng quản trị, theo dõi và mở rộng:

---

## 📁 1. `scripts/crawlers/` — Thu thập Dữ liệu Đa nguồn (Online & Offline)
Chứa toàn bộ các công cụ quét dữ liệu mạng xã hội, báo chí và cảnh báo CSGT:
* [`crawl_threads_flood.py`](./crawlers/crawl_threads_flood.py): Thu thập bài đăng Threads theo 4 trụ cột (Topics, Spoken queries, Targeted Account Radar).
* [`free_social_crawler.py`](./crawlers/free_social_crawler.py): Thu thập dữ liệu miễn phí đa nền tảng (TikTok, Facebook, News) bằng Discovery Search.
* [`crawl_hcm_core_csgt.py`](./crawlers/crawl_hcm_core_csgt.py): Thu thập dữ liệu 122 điểm đen cảnh báo ngập lụt PC08 CSGT TP.HCM.
* [`crawl_targeted_pos.py`](./crawlers/crawl_targeted_pos.py): Thu thập bổ sung các tin tích cực POS (dự án chống ngập, thoát nước nhanh).
* [`append_new_social_crawl.py`](./crawlers/append_new_social_crawl.py): Hợp nhất các đợt cào mới vào Master Dataset.
* [`extract_tiktok_frames.py`](./crawlers/extract_tiktok_frames.py): Trích xuất keyframes video TikTok phục vụ CLIP Vision.
* [`organize_raw_episodes.py`](./crawlers/organize_raw_episodes.py): Phân loại dữ liệu thô vào các thư mục episode tương ứng.

---

## 📁 2. `scripts/dataset/` — Làm sạch, Kiểm toán, Gán nhãn & Splits Master 10K
Chứa các kịch bản kiểm soát chất lượng dữ liệu ASTE và phục vụ huấn luyện:
* [`audit_10k_quality.py`](./dataset/audit_10k_quality.py): Kiểm toán 9 tiêu chí chuyên gia cho Master Dataset 10,249 mẫu.
* [`audit_dataset.py`](./dataset/audit_dataset.py) & [`audit_dataset_readiness.py`](./dataset/audit_dataset_readiness.py): Kiểm tra độ sẵn sàng huấn luyện.
* [`apply_expert_curation.py`](./dataset/apply_expert_curation.py): Thanh lọc triệt để 100% tin rác BĐS, F&B, ẩm thực và ẩn dụ.
* [`reannotate_expert_batches.py`](./dataset/reannotate_expert_batches.py): Gán nhãn ngữ cảnh chuyên sâu theo từng lô.
* [`reannotate_expert_semantic_master.py`](./dataset/reannotate_expert_semantic_master.py): Hiệu chỉnh cực tính ngữ nghĩa (NEG/POS/NEU).
* [`build_clean_dataset.py`](./dataset/build_clean_dataset.py) & [`build_dataset_v3.py`](./dataset/build_dataset_v3.py): Xây dựng và hợp nhất dataset.
* [`clean_and_reindex_dataset_v4.py`](./dataset/clean_and_reindex_dataset_v4.py): Làm sạch và re-index trường seq_id về cuối đối tượng JSON.
* [`cleanse_and_resolve_gazetteer.py`](./dataset/cleanse_and_resolve_gazetteer.py): Chuẩn hóa địa giới hành chính NQ 1685 (168 phường mới).
* [`enrich_master_v3_to_10k.py`](./dataset/enrich_master_v3_to_10k.py) & [`finalize_master_10k_clean.py`](./dataset/finalize_master_10k_clean.py): Chốt Master Dataset 10K.
* [`augment_cda_pos.py`](./dataset/augment_cda_pos.py): Tăng cường dữ liệu CDA cho nhãn POS.
* [`create_splits.py`](./dataset/create_splits.py): Phân chia tập Train/Dev/Test (80/10/10) chống rò rỉ dữ liệu (Parent-grouped).
* [`export_aste_v2_format.py`](./dataset/export_aste_v2_format.py): Xuất tệp định dạng chuẩn ASTE-Data-V2 (Xu et al., EMNLP 2020).
* [`inspect_aste_dataset.py`](./dataset/inspect_aste_dataset.py): Thanh tra tổng thể phân bổ triplets và nhãn.

---

## 📁 3. `scripts/training/` — Huấn luyện & Tinh chỉnh Mô hình AI (Deep Learning)
Chứa mã nguồn huấn luyện các mô hình ASTE:
* [`train_phobert_aste.py`](./training/train_phobert_aste.py) & [`tune_and_train_phobert.py`](./training/tune_and_train_phobert.py): Fast Path PhoBERT-base-v2 (GPU <= 10ms, Macro-F1 > 93%).
* [`train_bartpho_aste.py`](./training/train_bartpho_aste.py) & [`train_bartpho_syllable_base.py`](./training/train_bartpho_syllable_base.py): Mô hình sinh seq2seq BARTpho.
* [`tune_and_train_bartpho_syllable.py`](./training/tune_and_train_bartpho_syllable.py) & [`tune_and_train_bartpho_word.py`](./training/tune_and_train_bartpho_word.py): Tinh chỉnh siêu tham số BARTpho.
* [`train_mt5_aste.py`](./training/train_mt5_aste.py) & [`tune_and_train_mt5.py`](./training/tune_and_train_mt5.py): Mô hình Google mT5.
* [`train_xlm_roberta_aste.py`](./training/train_xlm_roberta_aste.py) & [`tune_and_train_xlm_roberta.py`](./training/tune_and_train_xlm_roberta.py): Huấn luyện XLM-RoBERTa.
* [`train_xlm_v_aste.py`](./training/train_xlm_v_aste.py) & [`tune_and_train_xlm_v.py`](./training/tune_and_train_xlm_v.py): Huấn luyện XLM-V (1M vocab).

---

## 📁 4. `scripts/benchmarks/` — Đánh giá Benchmark, F1-Score & Đo Độ Trễ (Latency)
* [`benchmark_heuristic_baseline.py`](./benchmarks/benchmark_heuristic_baseline.py): Đánh giá so sánh hiệu năng với Heuristic Baseline.
* [`benchmark_llm_eval.py`](./benchmarks/benchmark_llm_eval.py): Đánh giá chéo chất lượng nhãn với LLM SOTA.
* [`benchmark_single_item_latency.py`](./benchmarks/benchmark_single_item_latency.py): Kiểm định độ trễ nghiêm ngặt SLA <= 35ms.
* [`evaluate_mt5.py`](./benchmarks/evaluate_mt5.py) & [`evaluate_xlm_v.py`](./benchmarks/evaluate_xlm_v.py): Đánh giá F1 trên tập kiểm thử độc lập.

---

## 📁 5. `scripts/figures/` — Xuất Biểu đồ Khoa học & Demos
* [`generate_dataset_figures.py`](./figures/generate_dataset_figures.py): Xuất các biểu đồ phân bổ phục vụ công bố quốc tế (ACL, EMNLP, KDD).
* [`generate_full_stats_v3.py`](./figures/generate_full_stats_v3.py): Tổng hợp thống kê dataset.
* [`generate_split_figure.py`](./figures/generate_split_figure.py): Trực quan hóa tỷ lệ Train/Dev/Test.
* [`demo_clip_flood_query.py`](./figures/demo_clip_flood_query.py): Demo nhận diện hình ảnh ngập lụt qua Zero-shot CLIP.
* [`demo_extract_street_coordinates.py`](./figures/demo_extract_street_coordinates.py): Demo trích xuất tọa độ GPS tim đường.

---

## 📁 6. `scripts/pipeline/` — Điều phối & Vận hành Luồng Tích hợp
* [`orchestrator.py`](./pipeline/orchestrator.py): Điều phối tự động toàn bộ luồng xử lý dữ liệu.
* [`run_live_multimodal_pipeline.py`](./pipeline/run_live_multimodal_pipeline.py): Khởi chạy luồng pipeline thời gian thực tổng hợp.

---
> [!NOTE]
> **Tính tương thích ngược 100% (Backward Compatibility)**:
> Tất cả các file tại thư mục gốc `scripts/*.py` được trang bị cơ chế Forwarding Shims tự động. Các lệnh gọi cũ `from scripts.train_phobert_aste import ...` hoặc chạy dòng lệnh `python scripts/train_phobert_aste.py` vẫn hoạt động trơn tru 100% không bị ảnh hưởng.
