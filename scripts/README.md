# 📦 Cấu Trúc Phân Loại Mô-đun Thư Mục Scripts (`scripts/`)

Thư mục `scripts/` đã được chuẩn hóa và tái cấu trúc toàn diện thành **6 gói chuyên biệt (subpackages)**. Thư mục gốc chỉ chứa các thư mục con tương ứng, không còn các tệp script rời rạc giúp cấu trúc dự án tinh gọn, chuyên nghiệp và dễ quản lý trên IDE (PyCharm / VS Code).

---

## 📁 1. `scripts/crawlers/` — Thu thập & Cào Dữ liệu
Các script chuyên trách cào dữ liệu từ mạng xã hội, diễn đàn và CSGT (cả online và offline):
* [`free_social_crawler.py`](./crawlers/free_social_crawler.py): Bộ cào đa nền tảng thời gian thực miễn phí (Facebook, Threads, TikTok, YouTube).
* [`crawl_threads_flood.py`](./crawlers/crawl_threads_flood.py): Cào dữ liệu chuyên sâu ngập lụt trên Meta Threads.
* [`crawl_targeted_pos.py`](./crawlers/crawl_targeted_pos.py): Cào bài đăng nhắm mục tiêu để bổ sung mẫu Positive.
* [`crawl_hcm_core_csgt.py`](./crawlers/crawl_hcm_core_csgt.py): Cào thông tin cảnh báo ngập lụt chính thống từ kênh CSGT TP.HCM.
* [`append_new_social_crawl.py`](./crawlers/append_new_social_crawl.py): Nối dữ liệu cào mới vào kho dữ liệu master.
* [`extract_tiktok_frames.py`](./crawlers/extract_tiktok_frames.py): Trích xuất video/khung hình ngập từ TikTok.
* [`organize_raw_episodes.py`](./crawlers/organize_raw_episodes.py): Phân loại và gán Episode ID cho các đợt ngập lịch sử.

---

## 📁 2. `scripts/dataset/` — Xử lý, Tinh lọc & Gán nhãn Dataset
Các script phục vụ tiền xử lý, chuẩn hóa địa danh và kiểm định chất lượng bộ dữ liệu ASTE 10K:
* [`cleanse_and_resolve_gazetteer.py`](./dataset/cleanse_and_resolve_gazetteer.py): Chuẩn hóa tên đường và tra cứu Phường/Quận theo Gazetteer TP.HCM.
* [`reannotate_expert_semantic_master.py`](./dataset/reannotate_expert_semantic_master.py): Tái gán nhãn ngữ nghĩa chuyên gia cho tập Master.
* [`reannotate_expert_batches.py`](./dataset/reannotate_expert_batches.py): Gán nhãn thủ công & bán tự động theo batch chuyên gia.
* [`augment_cda_pos.py`](./dataset/augment_cda_pos.py): Tăng cường dữ liệu ngữ cảnh (CDA) cho các mẫu Positive.
* [`build_dataset_v3.py`](./dataset/build_dataset_v3.py): Đóng gói và xây dựng bộ dữ liệu ASTE phiên bản v3.
* [`build_clean_dataset.py`](./dataset/build_clean_dataset.py): Lọc sạch và loại bỏ mẫu nhiễu/quảng cáo.
* [`clean_and_reindex_dataset_v4.py`](./dataset/clean_and_reindex_dataset_v4.py): Đánh chỉ mục và làm sạch phiên bản v4.
* [`enrich_master_v3_to_10k.py`](./dataset/enrich_master_v3_to_10k.py): Mở rộng bộ dữ liệu từ v3 lên mốc 10.000 mẫu chuẩn.
* [`finalize_master_10k_clean.py`](./dataset/finalize_master_10k_clean.py): Đóng gói tập dữ liệu 10K cuối cùng chuẩn sạch.
* [`create_splits.py`](./dataset/create_splits.py): Chia tập Train / Dev / Test theo tỷ lệ chuẩn.
* [`export_aste_v2_format.py`](./dataset/export_aste_v2_format.py): Xuất dữ liệu theo định dạng ASTE v2 chuẩn học máy.
* [`audit_10k_quality.py`](./dataset/audit_10k_quality.py): Đánh giá chất lượng toàn diện bộ dữ liệu 10K.
* [`audit_dataset_readiness.py`](./dataset/audit_dataset_readiness.py): Kiểm tra độ sẵn sàng của dataset trước khi huấn luyện.
* [`audit_dataset.py`](./dataset/audit_dataset.py): Báo cáo thống kê phân bổ nhãn và entity.
* [`apply_expert_curation.py`](./dataset/apply_expert_curation.py): Áp dụng các quy tắc biên tập chuyên gia vào dataset.
* [`inspect_aste_dataset.py`](./dataset/inspect_aste_dataset.py): Công cụ CLI kiểm tra nhanh nội dung mẫu dữ liệu.

---

## 📁 3. `scripts/training/` — Huấn luyện & Tinh chỉnh Mô hình AI
Các script huấn luyện trực tiếp hoặc tinh chỉnh siêu tham số cho các kiến trúc ASTE:
* [`train_phobert_aste.py`](./training/train_phobert_aste.py) & [`tune_and_train_phobert.py`](./training/tune_and_train_phobert.py): PhoBERT (Base v2 / Large).
* [`train_mt5_aste.py`](./training/train_mt5_aste.py) & [`tune_and_train_mt5.py`](./training/tune_and_train_mt5.py): mT5-base generative ASTE.
* [`train_xlm_roberta_aste.py`](./training/train_xlm_roberta_aste.py) & [`tune_and_train_xlm_roberta.py`](./training/tune_and_train_xlm_roberta.py): XLM-RoBERTa base.
* [`train_xlm_v_aste.py`](./training/train_xlm_v_aste.py) & [`tune_and_train_xlm_v.py`](./training/tune_and_train_xlm_v.py): XLM-V base.
* [`train_bartpho_aste.py`](./training/train_bartpho_aste.py) & [`tune_and_train_bartpho_word.py`](./training/tune_and_train_bartpho_word.py): BARTpho-word.
* [`train_bartpho_syllable_base.py`](./training/train_bartpho_syllable_base.py) & [`tune_and_train_bartpho_syllable.py`](./training/tune_and_train_bartpho_syllable.py): BARTpho-syllable.

---

## 📁 4. `scripts/benchmarks/` — Đánh giá & So sánh Hiệu năng
Các script đo đạc độ trễ, F1-score và so sánh giữa các phương pháp:
* [`benchmark_single_item_latency.py`](./benchmarks/benchmark_single_item_latency.py): Đo độ trễ suy luận đơn lẻ từng văn bản.
* [`benchmark_heuristic_baseline.py`](./benchmarks/benchmark_heuristic_baseline.py): Đánh giá baseline so khớp heuristic từ khóa.
* [`benchmark_llm_eval.py`](./benchmarks/benchmark_llm_eval.py): Đánh giá chất lượng ASTE bằng mô hình LLM.
* [`evaluate_mt5.py`](./benchmarks/evaluate_mt5.py): Đánh giá chi tiết mô hình mT5 trên tập Test.
* [`evaluate_xlm_v.py`](./benchmarks/evaluate_xlm_v.py): Đánh giá chi tiết mô hình XLM-V trên tập Test.

---

## 📁 5. `scripts/figures/` — Trực quan hóa & Đồ thị
Các script vẽ biểu đồ phân phối dữ liệu phục vụ báo cáo/khóa luận:
* [`generate_full_stats_v3.py`](./figures/generate_full_stats_v3.py): Sinh biểu đồ phân bổ nhãn và thống kê tổng hợp v3.
* [`generate_dataset_figures.py`](./figures/generate_dataset_figures.py): Vẽ biểu đồ các thuộc tính và tương quan dữ liệu.
* [`generate_split_figure.py`](./figures/generate_split_figure.py): Biểu đồ phân chia tập dữ liệu Train/Dev/Test.
* [`demo_clip_flood_query.py`](./figures/demo_clip_flood_query.py): Demo nhận diện hình ảnh ngập lụt qua Zero-shot CLIP.
* [`demo_extract_street_coordinates.py`](./figures/demo_extract_street_coordinates.py): Demo trích xuất tọa độ GPS tim đường.

---

## 📁 6. `scripts/pipeline/` — Điều phối & Vận hành Luồng Tích hợp
* [`orchestrator.py`](./pipeline/orchestrator.py): Điều phối tự động toàn bộ luồng xử lý dữ liệu.
* [`run_live_multimodal_pipeline.py`](./pipeline/run_live_multimodal_pipeline.py): Khởi chạy luồng pipeline thời gian thực tổng hợp.

---
> [!TIP]
> **Quy ước Import chuẩn**:
> Tất cả các câu lệnh import trong dự án sử dụng định dạng module phân cấp rõ ràng, ví dụ:
> ```python
> from scripts.crawlers.organize_raw_episodes import determine_episode_id
> from scripts.training.train_phobert_aste import PhoBertASTEPredictor
> from scripts.dataset.reannotate_expert_batches import extract_expert_triplets
> ```
