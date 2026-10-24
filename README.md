# RadiNet: Multimodal Urban Flood Monitoring & Veracity Verification System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.5%2F4.2-E25A1C.svg)](https://spark.apache.org/)
[![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-Distributed%20Streaming-black.svg)](https://kafka.apache.org/)
[![Target Conference](https://img.shields.io/badge/Research-ICWSM%202027-success.svg)](https://www.icwsm.org/)
[![Dataset](https://img.shields.io/badge/Gold%20Dataset-ASTE%20v3%20Multimodal-orange.svg)](data/processed/hcmc_flood_annotated_v3_multimodal.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end Big Data & Multimodal Artificial Intelligence research framework designed for **real-time urban inundation detection, Aspect-Sentiment-Opinion Triplet Extraction (ASTE), and crowdsourced data veracity verification**. Engineered specifically for megacities facing complex tidal and pluvial flooding challenges, with empirical grounding in **Ho Chi Minh City, Vietnam**.

---

## 📌 Executive Summary & Research Motivation

Urban flooding driven by severe high tides (*triều cường*) and heavy tropical precipitation represents a critical vulnerability in coastal megacities. While social media platforms (TikTok, Facebook) and crowdsourced channels provide rapid citizen-sensor signals, harnessing this unstructured data stream faces severe scientific and engineering barriers:
1. **Severe Sentiment & Class Imbalance**: Disaster-related user posts are overwhelmingly negative (complaints, vehicle stalling), leaving positive flood recovery signals (*"water fully receded"*, *"roads dried"*) critically underrepresented ($< 1\%$).
2. **Noise, Misinformation & Re-shared Outdated Media**: Unverified videos from past years or unrelated regions routinely trigger false emergency alarms.
3. **Complex Administrative Dynamics**: Following major urban zoning reforms (such as Ho Chi Minh City's Resolution 1685/NQ-UBTVQH15 eliminating district-level administrative boundaries), legacy geospatial databases fail to correctly ground localized entities.

**RadiNet** addresses these challenges by uniting **Distributed Stream Processing (Kafka + PySpark)**, **Fine-Grained NLP (ASTE Schema v3)**, and **Multi-Tier Physical Grounding (Open-Meteo Satellite Weather + GIS Toponym Gazetteers)** into a unified, reproducible scientific pipeline.

---

## 🏛️ System Architecture

RadiNet operates as a decoupled, multi-tier streaming pipeline:

```
Crowdsourced Streams (TikTok, Facebook, News)
                    │
                    ▼
       [Live Social Stream Producer]
                    │
                    ▼
     [Distributed Broker: Apache Kafka]
           (Topic: social.live.raw)
                    │
                    ▼
    [Stream Engine: PySpark Structured Streaming]
                    │
    ┌───────────────┴────────────────────────────┐
    ▼                                            ▼
[Lakehouse Bronze/Silver Storage]     [Veracity & NLP Verification Engine]
   (Parquet / Snappy Compaction)         ├─ NLP: ASTE Triplet Extractor (PhoBERT)
                                         ├─ Vision: Keyframe In-Memory Streamer (yt-dlp)
                                         ├─ Physical: Open-Meteo Real-time Rain Check
                                         └─ Spatial: 168 Ward Gazetteer & CSGT Hotspots
                                                 │
                                                 ▼
                                     [Distributed In-Memory Cache]
                                             (Redis Key-Value)
                                                 │
                                                 ▼
                                 [Interactive Real-Time Leaflet Heatmap]
                                        (Web Server @ Port 8050)
```

---

## 🔬 Scientific Innovations & Contributions

### 1. Benchmark Dataset: HCMC Flood ASTE v3 (`Multimodal Gold Standard`)
Available at [`data/processed/hcmc_flood_annotated_v3_multimodal.json`](data/processed/hcmc_flood_annotated_v3_multimodal.json):
- **Scale**: **4,770 sentences**, **7,072 annotated Aspect-Sentiment-Opinion triplets** ($1.48$ triplets/sentence).
- **Targeted Class Rebalancing via Controlled Counterfactual Data Augmentation (CDA)**:
  - **Negative (`NEG`)**: $5,020$ triplets ($70.98\%$) — active inundation, traffic disruption.
  - **Positive (`POS`)**: $1,061$ triplets ($15.00\%$) — water receded, traffic resumed, pumping efficiency.
  - **Neutral (`NEU`)**: $991$ triplets ($14.01\%$) — technical water level gauge, hydrological forecasts.
- **Scientific Integrity Guarantee**:
  - $100\%$ Verbatim Substrings for both Aspect and Opinion spans.
  - Zero synthetic fabrication in evaluation splits: CDA augmented recovery samples ($890$ items) are explicitly flagged with `data_split_recommendation: "TRAIN_ONLY"`, ensuring the test benchmark represents $100\%$ authentic crowdsourced field posts.
  - Strictly compliant with Resolution 1685/NQ-UBTVQH15 (eliminated district tiers, mapped to 168 newly reformed wards).

### 2. Multi-tier Data Veracity Verification Engine
Evaluates every crowdsourced report through 4 orthogonal verification gates:
- **Gate 1 (Content & Visual Evidence)**: Multimodal inspection combining textual cues with keyframe extraction.
- **Gate 2 (Meteorological Cross-Check)**: Automated real-time API query to Open-Meteo at the exact latitude/longitude and posting timestamp.
- **Gate 3 (Spatio-Temporal Clustering)**: Density-based consensus check within a $500\text{ m}$ spatial radius and $60\text{ min}$ sliding window.
- **Gate 4 (Probabilistic Confidence)**: Reports scored from $0.0$ to $1.0$ and classified into `Confirmed` ($\ge 0.75$), `Suspect` ($0.50 - 0.74$), `Unverified`, and `Rejected` ($< 0.35$).

### 3. Lightweight Zero-Disk Multimodal Streaming
Located in [`pipeline/multimodal_streamer.py`](pipeline/multimodal_streamer.py):
- Streams video keyframes and mono 16kHz audio directly into RAM buffers (`io.BytesIO`).
- Completely bypasses CDN anti-hotlinking HTTP 403 errors using canonical URL token renewal.
- Consumes **0 MB persistent disk space** during live inference, eliminating gigabytes of video download overhead.

---

## 📊 Dataset Statistics Overview

| Dimension | Distribution / Value |
| :--- | :--- |
| **Total Corpus** | 4,770 sentences, 7,072 ASTE triplets |
| **Polarity Breakdown** | `NEG`: 70.98% (5,020) \| `POS`: 15.00% (1,061) \| `NEU`: 14.01% (991) |
| **Aspect Categories** | `LOCATION_ADMIN` (42.8%) \| `LOCATION_STREET` (29.9%) \| `HYDROLOGY` (18.7%) \| `INFRASTRUCTURE_DRAINAGE` (6.5%) \| `RESPONSE_ENTITY` (2.1%) |
| **Severity Levels** | `MEDIUM` (34.6%) \| `HIGH` (26.6%) \| `LOW` (24.7%) \| `RECOVERED` (14.1%) |
| **Multimodal Coverage** | 966 authentic post records with active video / high-resolution image links |
| **Geospatial Grounding**| Mapped across 122 Traffic Police (CSGT) flood hotspots and 168 administrative wards |

---

## 🚀 Quick Start & Reproducibility Guide

### 1. Environment Setup
Prerequisites: **Python 3.10+** (Tested on Python 3.10 and 3.14).

```bash
# Clone the repository
git clone https://github.com/SE363-HVT/urban-flood-monitor.git
cd urban-flood-monitor

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

### 2. Running Automated Verification Tests
Execute the built-in test suite to verify pipeline integrity:

```bash
# Run smoke tests on API endpoints and clusterers
python -m tests.smoke_test_pipeline

# Verify anti-spam filters and meteorological grounding
python -m tests.test_live_fixes
```

### 3. Launching Real-Time Monitoring & Heatmap

#### Option A: Simulation Mode (Recommended for Demos & Offline Evaluation)
Replays verified historical flood episodes (such as Typhoon No. 4 and late-September peak tides) with full meteorological verification:

```bash
python run_pipeline_test.py --mode simulation --window 120
```

#### Option B: Live Streaming Mode
Ingests live crowdsourced streams directly from TikTok and Facebook:

```bash
python run_pipeline_test.py --mode live --window 60
```

Access the interactive web dashboard at:
👉 **`http://localhost:8050`**

---

## 📂 Repository Structure

```text
urban-flood-monitor/
├── bigdata/                         # Distributed Streaming & Lakehouse Infrastructure
│   ├── ai_service/                  # Decoupled AI Microservice (Port 8001)
│   ├── lakehouse/                   # Parquet compaction & analytical storage jobs
│   ├── producers/                   # Distributed Kafka ingestion producers
│   ├── streaming/                   # PySpark Structured Streaming engines
│   └── docker-compose.yml           # Multi-container orchestration (Kafka, Spark, Redis)
├── core/                            # Foundational Domain Engines
│   ├── config.py                    # Global system and crawler configuration
│   └── gazetteer.py                 # Precision GIS Gazetteer (168 Wards & 122 CSGT Hotspots)
├── dashboard/                       # Web Presentation Tier
│   ├── index.html                   # Interactive Leaflet Heatmap & Veracity Panel
│   └── server.py                    # High-throughput asynchronous HTTP Server
├── data/                            # Processed Datasets & Ground Truth
│   ├── processed/
│   │   └── hcmc_flood_annotated_v3_multimodal.json  # Gold Standard ASTE v3 Dataset
│   ├── raw/episodes/                # Episode-based crowdsourced raw corpora
│   └── csgt_122_flood_hotspots.json # Verified coordinates for 122 flood hotspots
├── documents/                       # Comprehensive Scientific & Architectural Documentation
│   ├── HUONG_DAN_SUA_DATASET_ASTE_V3.md
│   ├── BIGDATA_DATA_ENGINEERING_ARCHITECTURE_AND_EVALUATION.md
│   └── RadiNet_Master_Notes.pdf
├── pipeline/                        # Feature Extraction & Verification Services
│   ├── event_processor.py           # Stream sanitization and spam rejection
│   ├── live_free_crawler.py         # Autonomous live crawler without paid APIs
│   ├── multimodal_streamer.py       # Zero-disk in-memory keyframe & audio streamer
│   ├── spatio_temporal_clusterer.py # Spatial consensus clustering engine
│   └── veracity_checker.py          # Multi-tier veracity verification against Open-Meteo
├── scripts/                         # Production Scripts & Benchmarking Tools
│   ├── augment_cda_pos.py           # Controlled counterfactual augmentation generator
│   ├── build_dataset_v3.py          # Gold standard dataset builder
│   ├── crawl_targeted_pos.py        # Targeted crawler for recovery signals
│   ├── generate_full_stats_v3.py    # 13-dimension dataset audit script
│   └── orchestrator.py              # Crawler workflow orchestrator
├── tests/                           # Automated Verification & Smoke Test Suite
│   ├── smoke_test_pipeline.py
│   └── test_live_fixes.py
├── run_pipeline_test.py             # System execution entrypoint
└── requirements.txt                 # Pinned Python package dependencies
```

---

## 🎯 Target Milestones & Paper Submission

This project serves as the core empirical and engineering foundation for academic publication:
- **Target Venue**: **ICWSM 2027** (*International AAAI Conference on Web and Social Media*)
- **Focus Areas**: Disaster Informatics, Multimodal Information Extraction, Data Veracity in Crowdsourcing Streams.
- **Compute Credit Application**: Google Cloud Research Credits / Google Ultra Program for large-scale PhoBERT fine-tuning and ViT inference.

---

## 👥 Authors & Acknowledgments

- **Research Team**: SE363 Research Group — University of Information Technology (VNU-HCM).
- **Core Maintainer**: Minh Thuan (`Tranminhthuan161@gmail.com`).
- **Organization**: [SE363 - HVT](https://github.com/SE363-HVT)
- **Repository**: [urban-flood-monitor](https://github.com/SE363-HVT/urban-flood-monitor)

---
*For inquiries, academic collaboration, or benchmark reproducibility questions, please open an Issue or contact the authors directly.*
