# 🌊 RadiNet: HCMC Urban Flood ASTE Dataset Inspection Report

> **Generated at:** `2026-10-13 18:59:17`  
> **Dataset File:** `hcmc_flood_annotated_v2_multimodal.json`  
> **Core Task:** Multimodal Aspect Sentiment Triplet Extraction (M-ABSA / ASTE) for Urban Hydrology & Flooding

---

## 1. Executive Summary

| Metric / Dimension | Value | Technical Context |
| :--- | :---: | :--- |
| **Total Annotated Samples** | **3,922** | Sentence-level news & social media posts |
| **Total ASTE Triplets** | **5,483** | 100% annotated coverage |
| **Average Triplet Density** | **1.40** | Triplets per sample |
| **Unique Aspect Entities** | **516** | Roads, rivers, vehicles, infrastructure |
| **Unique Opinion Expressions** | **19** | Flood depth, disruption, traffic status |
| **Multimodal Samples with Media** | **1,011 (25.8%)** | TikTok video CDN / social image links |
| **Active Direct Media CDN URLs** | **1,114** | Direct video / image endpoints |
| **Administrative Wards Covered** | **58** | Aligned with NQ 1278 administrative boundaries |

---

## 2. Sentiment Polarity Breakdown (ASTE Target Labels)

| Polarity | Triplets | Share (%) | Definition & Domain Meaning |
| :--- | :---: | :---: | :--- |
| **NEG** | 5,163 | 94.2% | Severe flood, submerged engine, paralyzed traffic, water intrusion |
| **NEU** | 303 | 5.5% | Tide forecast, flood advisory, monitoring warning |
| **POS** | 17 | 0.3% | Receded water, dry roadway, smooth traffic flow |

*Class Imbalance Ratio:* NEG to POS = `303.7 : 1`


---

## 3. Top Recurring ASTE Triplets

| Rank | Aspect Entity | Opinion Phrase | Polarity | Frequency | Share (%) |
| :---: | :--- | :--- | :---: | :---: | :---: |
| #1 | `khu vực ngập` | ngập nước cục bộ | **NEG** | 309 | 5.6% |
| #2 | `phương tiện giao thông` | nước ngập làm xe chết máy, phải dắt bộ bì bõm | **NEG** | 263 | 4.8% |
| #3 | `Thủ Đức` | ngập nước cục bộ | **NEG** | 128 | 2.3% |
| #4 | `tuyến đường ngập` | ngập nước cục bộ | **NEG** | 122 | 2.2% |
| #5 | `sài gòn` | ngập nước cục bộ | **NEG** | 116 | 2.1% |
| #6 | `tphcm` | ngập sâu gây cản trở và đảo lộn giao thông | **NEG** | 103 | 1.9% |
| #7 | `khu vực ngập` | ngập sâu gây cản trở và đảo lộn giao thông | **NEG** | 99 | 1.8% |
| #8 | `tp.hcm` | ngập nước cục bộ | **NEG** | 99 | 1.8% |
| #9 | `tp.hcm` | ngập sâu gây cản trở và đảo lộn giao thông | **NEG** | 94 | 1.7% |
| #10 | `Thủ Đức` | ngập sâu gây cản trở và đảo lộn giao thông | **NEG** | 85 | 1.6% |
| #11 | `tphcm` | ngập nước cục bộ | **NEG** | 78 | 1.4% |
| #12 | `tuyến đường ngập` | ngập sâu gây cản trở và đảo lộn giao thông | **NEG** | 74 | 1.3% |

---

## 4. Text Grounding Audit

| Grounding Type | Count | Rate (%) | Description |
| :--- | :---: | :---: | :--- |
| **Exact Substring Span** | 3,985 | 72.7% | Target entity appears verbatim in sentence |
| **Accent-Normalized Span** | 0 | 0.0% | Minor diacritic / capitalization variation |
| **Implicit Domain Aspects** | 1,498 | 27.3% | Canonical concepts (`khu vực ngập`, `phương tiện`) |

---

## 5. Dataset Quality Linter Audit

| Validation Criterion | Status | Diagnostic Finding |
| :--- | :---: | :--- |
| Schema Required Keys | PASS | 0 missing keys |
| Text Content Uniqueness | PASS | 0 duplicate texts (100% unique textual entries) |
| Sample Identifier Uniqueness | WARN | 66 duplicate ID collisions in social batches |
| Zero-length Sentences | PASS | 0 empty sentences |
| Zero-triplet Samples | PASS | 0 unannotated samples |
| Triplet Label Validity | PASS | 100% valid polarity labels (NEG, NEU, POS) |

