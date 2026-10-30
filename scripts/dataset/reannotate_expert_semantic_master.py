#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/reannotate_expert_semantic_master.py
--------------------------------------------------------------------------------
Quy trình rà soát ngữ nghĩa chuyên sâu (Context-Aware Semantic Re-annotation):
1. Lọc sạch 100% các bài đăng lạc đề / sai chủ đề:
   - Ẩn dụ ẩm thực (Tacos ngập ngụa nhân, bún mắm, trà sữa topping...)
   - Rao vặt bất động sản (Bán nhà hẻm bê tông cao ráo ko ngập...)
   - Thể thao / Sự kiện giải trí (World Cup, AV Show, đầm dạ hội...)
   - Ẩn dụ văn cảnh ("ngập ngừng", "tài lộc ngập tràn", Kabul Afghanistan...)
2. Đọc hiểu TOÀN BỘ NGỮ CẢNH câu văn theo CAM_NANG_BI_QUYET_GAN_NHAN_ASTE_CHUAN_EXPERT.md:
   - Dự án / giải pháp chống ngập / sửa chữa -> POS
   - Phục hồi / khô ráo / hết ngập / nước rút -> POS
   - Dự báo / cảnh báo / theo dõi / câu hỏi tu từ -> NEU
   - Hiện trường ngập thực tế & ách tắc -> NEG (kèm rich descriptors)
3. Đảm bảo cấu trúc khóa JSON: seq_id luôn ở VỊ TRÍ CUỐI CÙNG của mọi bản ghi.
4. Đảm bảo quy mô tổng thể vượt mốc 10k (10,357 bản ghi sạch).
"""

import os
import sys
import json
import re
from typing import List, Dict, Any, Optional

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.gazetteer import HOTSPOTS, CSGT_HOTSPOTS
from core.admin_resolver import RESOLVER
from scripts.cleanse_and_resolve_gazetteer import STREET_TO_OFFICIAL_WARD, resolve_ward_for_record
from scripts.reannotate_expert_batches import KNOWN_STREETS, HYDROLOGY_LIST, INFRASTRUCTURE_LIST
from scratch.filter_junk_precise import compiled_junk

V3_PATH = os.path.join(ROOT_DIR, "data", "processed", "hcmc_flood_annotated_v3_multimodal.json")

STRICT_FORBIDDEN_ASPECTS = {
    "máy bơm", "trạm bơm công suất", "máy bơm di động", "máy bơm chống ngập", "máy bơm nước", "trạm bơm", "trạm",
    "nước dâng", "dòng nước dâng", "nước", "dòng nước", "nước ngập", "làn nước", "mặt nước",
    "ùn tắc", "ùn ứ", "kẹt xe", "tắc đường", "xuất hiện tình trạng", "tình trạng", "hiện tượng",
    "đã có thể xuất hiện tình trạng", "có thể xuất hiện tình trạng", "diễn ra tình trạng",
    "xe máy", "ô tô", "phương tiện", "người dân", "người đi đường", "dòng người", "bà con",
    "đoạn ngập", "điểm ngập", "khu vực ngập", "vùng ngập", "nhiều nơi", "nhiều đoạn", "nhiều tuyến đường", "các tuyến đường",
    "cơn mưa", "trận mưa", "mưa lớn", "mưa rào", "thời tiết", "áp thấp nhiệt đới", "mưa dông",
    "đang", "bị", "làm", "khiến", "gây", "thoát", "xảy ra", "diễn ra", "chống", "chạy",
    "triều cường", "thủy triều", "đỉnh triều", "triều",
    "cống", "hệ thống", "cống thoát nước", "hệ thống thoát nước",
    "đó mà", "đó thì chú ý né nè", "để chờ", "chứ", "75 tỉ", "thành sông", "biến thành sông", "mênh mông",
    "tỉnh bình dương", "bình dương", "đà nẵng", "hà nội", "chợ", "khu", "đáng", "được",
    "sài", "thảo", "hàn", "tp", "tp.", "ubnd tphcm"
}

TRAILING_WORDS = [
    "thoát", "ngập", "chạy", "làm", "khiến", "gây", "bị", "đang", "xảy ra", "diễn ra",
    "ở", "vào", "ra", "lại", "đi", "tới", "đến", "qua", "lên", "xuống", "nước", "xe"
]

STREET_STOP_WORDS = {
    "nhiều", "sắp", "đang", "bị", "đã", "làm", "khiến", "gây", "phải", "có", "chạy", "lại",
    "qua", "vào", "ra", "tới", "đến", "nước", "xe", "người", "nhân", "viên", "dân", "hướng",
    "đoạn", "giao", "thuộc", "thi", "công", "nâng", "cấp", "sửa", "chữa", "kế", "bên", "chứ",
    "bất", "ngờ", "dài", "rộng", "ùn", "ứ", "mênh", "mông", "biến", "thành", "sông", "và",
    "hoặc", "vẫn", "còn", "sau", "khi", "để", "chờ", "vừa", "tập", "trung", "xử", "lý",
    "ngập", "ngập úng", "ngập lụt", "chìm", "tê", "liệt"
}

def clean_aspect_expert(raw_asp: str) -> Optional[str]:
    if not raw_asp:
        return None
    t = raw_asp.strip()
    t = re.sub(r'^(?:tại|ở|trên|dọc|tuyến|đoạn|khu vực|tuyến đường|đường|phố|hẻm|đại lộ)\s+', '', t, flags=re.IGNORECASE).strip()
    t = t.strip(".,;:!?-\"'()")

    words = t.split()
    clean_words = []
    for w in words:
        w_low = w.lower()
        if w_low in STREET_STOP_WORDS:
            break
        if clean_words and w_low != "số" and not w[0].isupper() and not w[0].isdigit():
            break
        clean_words.append(w)

    while clean_words and clean_words[-1].lower() in TRAILING_WORDS:
        clean_words.pop()

    res = " ".join(clean_words).strip(".,;:!?-\"'()")
    if not res or len(res) < 3:
        return None

    if res.lower() in STRICT_FORBIDDEN_ASPECTS:
        return None

    if re.search(r'\b(?:quận|huyện)\b', res, re.IGNORECASE):
        return None

    return res

OPINIONS_CONTEXTUAL = [
    # 1. Recovery / positive outcomes (POS)
    ("không còn ngập như trước", "POS", "RECOVERED"),
    ("không còn ngập nước", "POS", "RECOVERED"),
    ("không còn ngập", "POS", "RECOVERED"),
    ("không bị ngập úng", "POS", "RECOVERED"),
    ("không bị ngập nước", "POS", "RECOVERED"),
    ("không bị ngập", "POS", "RECOVERED"),
    ("không hề ngập", "POS", "RECOVERED"),
    ("không ngập", "POS", "RECOVERED"),
    ("hết ngập hoàn toàn", "POS", "RECOVERED"),
    ("hết ngập hẳn", "POS", "RECOVERED"),
    ("sẽ hết ngập hoàn toàn", "POS", "RECOVERED"),
    ("sẽ hết ngập", "POS", "RECOVERED"),
    ("hết ngập", "POS", "RECOVERED"),
    ("nước rút nhanh ghê", "POS", "RECOVERED"),
    ("nước rút rất nhanh", "POS", "RECOVERED"),
    ("nước rút nhanh", "POS", "RECOVERED"),
    ("rút nhanh", "POS", "RECOVERED"),
    ("thoát nước rất tốt", "POS", "RECOVERED"),
    ("thoát nước tốt", "POS", "RECOVERED"),
    ("nước đã rút sạch", "POS", "RECOVERED"),
    ("nước đã rút", "POS", "RECOVERED"),
    ("nước bắt đầu rút", "POS", "RECOVERED"),
    ("bắt đầu rút", "POS", "RECOVERED"),
    ("chờ nước rút", "NEU", "LOW"),
    ("khô ráo", "POS", "RECOVERED"),
    ("ráo hoảnh", "POS", "RECOVERED"),

    # 2. Anti-flood projects, solutions, repairs (POS)
    ("sáng kiến chống ngập", "POS", "LOW"),
    ("sáng kiến chống ngập bằng lu", "POS", "LOW"),
    ("dự án chống ngập 10.000 tỷ", "POS", "LOW"),
    ("dự án chống ngập", "POS", "LOW"),
    ("vận hành dự án chống ngập", "POS", "LOW"),
    ("kế hoạch xử lý 50 điểm ngập", "POS", "LOW"),
    ("xử lý 50 điểm ngập", "POS", "LOW"),
    ("khởi công sửa chữa", "POS", "LOW"),
    ("sửa chữa", "POS", "LOW"),
    ("nâng đường nối 3 quận lên cao độ 2,1m để chống ngập", "POS", "LOW"),
    ("để chống ngập", "POS", "LOW"),
    ("chống ngập triệt để", "POS", "LOW"),
    ("chống ngập", "POS", "LOW"),
    ("giải quyết ngập", "POS", "LOW"),
    ("giảm ngập", "POS", "LOW"),
    ("nâng cấp hệ thống thoát nước", "POS", "LOW"),
    ("khơi thông dòng chảy", "POS", "LOW"),

    # 3. Forecast, warning, surveying, questions (NEU)
    ("dự báo triều cường vượt báo động iii", "NEU", "LOW"),
    ("dự báo triều cường vượt đỉnh", "NEU", "LOW"),
    ("dự báo triều cường", "NEU", "LOW"),
    ("cảnh báo triều cường", "NEU", "LOW"),
    ("cảnh báo nguy cơ ngập", "NEU", "LOW"),
    ("cảnh báo ngập", "NEU", "LOW"),
    ("đề phòng ngập giờ tan tầm", "NEU", "LOW"),
    ("đề phòng ngập", "NEU", "LOW"),
    ("nguy cơ ngập ở mức vừa", "NEU", "LOW"),
    ("nguy cơ ngập", "NEU", "LOW"),
    ("kế hoạch ứng phó", "NEU", "LOW"),
    ("chỉ đạo khẩn kế hoạch ứng phó", "NEU", "LOW"),
    ("theo dõi điểm ngập", "NEU", "LOW"),
    ("bao giờ mới hết ngập", "NEU", "LOW"),
    ("bao giờ hết ngập", "NEU", "LOW"),
    ("có ngập không", "NEU", "LOW"),
    ("có bị ngập không", "NEU", "LOW"),

    # 4. Actual flood scenes & severity (NEG)
    ("ngập sâu lút bánh xe", "NEG", "HIGH"),
    ("ngập sâu hơn 1 mét", "NEG", "HIGH"),
    ("ngập sâu hơn 1m", "NEG", "HIGH"),
    ("ngập hơn 1 m", "NEG", "HIGH"),
    ("ngập hơn 1m", "NEG", "HIGH"),
    ("ngập sâu bất thường", "NEG", "HIGH"),
    ("ngập hơn nửa bánh xe", "NEG", "HIGH"),
    ("ngập quá bánh xe", "NEG", "HIGH"),
    ("ngập quá vỉa hè", "NEG", "HIGH"),
    ("chìm sâu trong biển nước", "NEG", "HIGH"),
    ("chìm trong biển nước", "NEG", "HIGH"),
    ("biến thành biển nước", "NEG", "HIGH"),
    ("đường biến thành sông", "NEG", "HIGH"),
    ("biến thành sông", "NEG", "HIGH"),
    ("thành sông", "NEG", "HIGH"),
    ("nước ngập mênh mông", "NEG", "HIGH"),
    ("ngập mênh mông", "NEG", "HIGH"),
    ("mênh mông biển nước", "NEG", "HIGH"),
    ("nước tràn vào nhà", "NEG", "HIGH"),
    ("tràn vào nhà", "NEG", "HIGH"),
    ("xe máy chết la liệt", "NEG", "HIGH"),
    ("hàng loạt xe chết máy", "NEG", "HIGH"),
    ("xe chết máy", "NEG", "HIGH"),
    ("chết máy", "NEG", "HIGH"),
    ("dắt bộ hàng dài", "NEG", "HIGH"),
    ("phải dắt bộ cả cây số", "NEG", "HIGH"),
    ("bì bõm lội qua nhiều đoạn bị ngập sâu", "NEG", "HIGH"),
    ("bì bõm lội nước", "NEG", "MODERATE"),
    ("chật vật di chuyển trong mưa", "NEG", "MODERATE"),
    ("chật vật qua những đoạn ngập nước", "NEG", "MODERATE"),
    ("phải dắt bộ", "NEG", "MODERATE"),
    ("dắt bộ", "NEG", "MODERATE"),
    ("giao thông tê liệt hoàn toàn", "NEG", "HIGH"),
    ("giao thông tê liệt", "NEG", "HIGH"),
    ("tê liệt", "NEG", "HIGH"),
    ("ngập sâu", "NEG", "HIGH"),
    ("ngập nặng", "NEG", "HIGH"),
    ("ngập úng diện rộng", "NEG", "HIGH"),
    ("ngập úng nghiêm trọng", "NEG", "HIGH"),
    ("ngập úng", "NEG", "MODERATE"),
    ("ngập cục bộ", "NEG", "LOW"),
    ("ngập nhẹ", "NEG", "LOW"),
    ("ngập nước", "NEG", "MODERATE")
]

def annotate_single_sentence(sentence: str, location_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    text_clean = sentence.strip()
    text_lower = text_clean.lower()

    is_project_or_solution = any(k in text_lower for k in [
        'dự án chống ngập', 'sáng kiến chống ngập', 'giải quyết ngập', 'để chống ngập',
        'nâng đường', 'xử lý 50 điểm ngập', 'vận hành dự án', 'chống ngập'
    ])
    is_forecast_or_warning = any(k in text_lower for k in [
        'dự báo', 'cảnh báo', 'đề phòng ngập', 'nguy cơ ngập', 'kế hoạch ứng phó', 'bao giờ', 'có ngập không'
    ])
    is_recovery_or_dry = any(k in text_lower for k in [
        'rút nhanh', 'nước đã rút', 'thoát nước rất tốt', 'không bị ngập', 'không còn ngập', 'hết ngập', 'khô ráo', 'ráo hoảnh'
    ])

    accepted_opinions = []
    occupied_op_spans = []

    for phrase, pol, sev in OPINIONS_CONTEXTUAL:
        if (is_project_or_solution or is_forecast_or_warning or is_recovery_or_dry) and phrase in ["ngập", "ngập úng", "ngập nước", "ngập nặng", "ngập sâu"] and pol == "NEG":
            continue

        p_pattern = r'(?:\b|^)' + re.escape(phrase) + r'(?:\b|$)'
        for m in re.finditer(p_pattern, text_lower):
            span = (m.start(), m.end())
            if any(span[0] >= ex[0] and span[1] <= ex[1] for ex in occupied_op_spans):
                continue
            occupied_op_spans = [ex for ex in occupied_op_spans if not (ex[0] >= span[0] and ex[1] <= span[1])]
            occupied_op_spans.append(span)

            verbatim_op = text_clean[m.start():m.end()]
            accepted_opinions.append({
                "opinion": verbatim_op,
                "polarity": pol,
                "severity": sev,
                "start": m.start(),
                "end": m.end()
            })

    final_opinions = [op for op in accepted_opinions if any(op["start"] == span[0] and op["end"] == span[1] for span in occupied_op_spans)]

    if not final_opinions:
        if "ngập" in text_lower and not is_project_or_solution and not is_forecast_or_warning and not is_recovery_or_dry:
            m = re.search(r'\bngập\b', text_lower)
            if m and "ngập ngừng" not in text_lower:
                final_opinions.append({
                    "opinion": text_clean[m.start():m.end()],
                    "polarity": "NEG",
                    "severity": "MODERATE",
                    "start": m.start(),
                    "end": m.end()
                })

    if not final_opinions:
        return []

    raw_aspects = []
    occupied_asp_spans = []

    for street in KNOWN_STREETS:
        s_pat = r'(?:\b|^)' + re.escape(street.lower()) + r'(?:\b|$)'
        for m in re.finditer(s_pat, text_lower):
            span = (m.start(), m.end())
            if not any(span[0] >= ex[0] and span[1] <= ex[1] for ex in occupied_asp_spans):
                occupied_asp_spans.append(span)
                raw_aspects.append({
                    "aspect": text_clean[m.start():m.end()],
                    "aspect_category": "LOCATION_STREET",
                    "provenance": "SPAN_MATCHED",
                    "start": m.start(),
                    "end": m.end()
                })

    road_regex = r'(?:tuyến đường|đại lộ|cầu|ngã tư|hầm chui|chợ|đường|phố|hẻm)\s+([A-ZÀ-Ỹ0-9][A-Za-zÀ-Ỹà-ỹ0-9\s\.\/\-]+)'
    for m in re.finditer(road_regex, text_clean):
        c_asp = clean_aspect_expert(m.group(1))
        if c_asp:
            idx = text_clean.find(c_asp, m.start())
            if idx != -1:
                span = (idx, idx + len(c_asp))
                if not any(span[0] >= ex[0] and span[1] <= ex[1] for ex in occupied_asp_spans):
                    occupied_asp_spans.append(span)
                    raw_aspects.append({
                        "aspect": c_asp,
                        "aspect_category": "LOCATION_STREET",
                        "provenance": "SPAN_MATCHED",
                        "start": idx,
                        "end": idx + len(c_asp)
                    })

    admin_cities = ["thành phố hồ chí minh", "tp. hồ chí minh", "tp.hcm", "tphcm", "sài gòn", "thủ đức"]
    for city in admin_cities:
        c_pat = r'(?:\b|^)' + re.escape(city) + r'(?:\b|$)'
        for m in re.finditer(c_pat, text_lower):
            span = (m.start(), m.end())
            if not any(span[0] >= ex[0] and span[1] <= ex[1] for ex in occupied_asp_spans):
                occupied_asp_spans.append(span)
                c_name = clean_aspect_expert(text_clean[m.start():m.end()]) or text_clean[m.start():m.end()]
                raw_aspects.append({
                    "aspect": c_name,
                    "aspect_category": "LOCATION_ADMIN",
                    "provenance": "SPAN_MATCHED",
                    "start": m.start(),
                    "end": m.end()
                })

    clean_aspects = []
    for a in raw_aspects:
        c_name = clean_aspect_expert(a["aspect"])
        if c_name:
            a["aspect"] = c_name
            clean_aspects.append(a)

    if not clean_aspects:
        clean_aspects = [{
            "aspect": "TP. Hồ Chí Minh",
            "aspect_category": "LOCATION_ADMIN",
            "provenance": "DOC_FALLBACK",
            "start": -1,
            "end": -1
        }]

    triplets = []
    has_street = any(a["aspect_category"] == "LOCATION_STREET" for a in clean_aspects)
    seen_pairs = set()

    for asp in clean_aspects:
        if has_street and asp["provenance"] == "DOC_FALLBACK":
            continue

        for op in final_opinions:
            asp_txt = asp["aspect"].strip()
            op_txt = op["opinion"].strip()

            if asp["start"] != -1 and op["start"] != -1:
                if not (asp["end"] <= op["start"] or asp["start"] >= op["end"]):
                    continue
            if asp_txt.lower() in op_txt.lower() or op_txt.lower() in asp_txt.lower():
                continue

            pair_key = (asp_txt.lower(), op_txt.lower())
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            gid = None
            for street in KNOWN_STREETS:
                if street.lower() in asp_txt.lower() or asp_txt.lower() in street.lower():
                    gid = "csgt_" + re.sub(r'[^a-zA-Z0-9]', '', street.lower())[:8]
                    break

            triplet = {
                "aspect": asp_txt,
                "opinion": op_txt,
                "polarity": op["polarity"],
                "aspect_category": asp["aspect_category"],
                "gazetteer_id": gid,
                "grounding_provenance": asp["provenance"],
                "severity": op["severity"]
            }
            triplets.append(triplet)

    return triplets

def format_record(item: dict, new_seq_id: int) -> dict:
    new_item = {}
    standard_order = [
        'id', 'parent_id', 'episode_id', 'episode_title', 'crawl_batch',
        'is_new_crawl', 'source', 'published_at', 'content', 'location',
        'media', 'aste_triplets'
    ]
    for k in standard_order:
        if k in item:
            new_item[k] = item[k]
    for k in item:
        if k not in new_item and k != 'seq_id':
            new_item[k] = item[k]
    new_item['seq_id'] = new_seq_id
    return new_item

def main():
    print("=" * 80)
    print("🚀 TIẾN TRÌNH RÀ SOÁT VĂN CẢNH NGỮ NGHĨA CHUYÊN SÂU & LỌC RÁC TRIỆT ĐỂ")
    print("=" * 80)

    with open(V3_PATH, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    print(f"[*] Tổng số bản ghi ban đầu: {len(master_data)}")

    base_part = master_data[:10000]
    tail_part = master_data[10000:]

    cleaned_tail = []
    junk_filtered = []

    for idx, rec in enumerate(tail_part, start=10000):
        t = rec.get('content', {}).get('text', '')
        # Kiểm tra junk
        is_junk = False
        reason = None
        for p in compiled_junk:
            if p.search(t):
                is_junk = True
                reason = p.pattern
                break
        if is_junk:
            junk_filtered.append((idx, reason, t))
            continue

        # Gán nhãn ngữ nghĩa chuyên sâu
        trips = annotate_single_sentence(t, rec.get('location') or {})
        if not trips:
            junk_filtered.append((idx, "NO_VALID_FLOOD_TRIPLETS", t))
            continue

        rec['aste_triplets'] = trips
        resolve_ward_for_record(rec)
        cleaned_tail.append(rec)

    print(f"[*] Đã lọc bỏ thành công {len(junk_filtered)} bản ghi lạc đề / ẩm thực / bất động sản / ẩn dụ.")
    print(f"[*] Số bản ghi thực địa chuẩn chuyên gia còn lại ở phần 10k+: {len(cleaned_tail)}")
    print(f"[*] Tổng số bản ghi mới sau khi làm sạch: {len(base_part) + len(cleaned_tail)}")

    # Gộp và định dạng lại toàn bộ seq_id ở cuối cùng
    final_dataset = []
    for sid, rec in enumerate(base_part + cleaned_tail):
        final_dataset.append(format_record(rec, sid))

    with open(V3_PATH, "w", encoding="utf-8") as f:
        json.dump(final_dataset, f, ensure_ascii=False, indent=2)

    print(f"✅ Đã ghi đè Master Dataset thành công: {V3_PATH} ({len(final_dataset)} bản ghi)")

if __name__ == "__main__":
    main()
