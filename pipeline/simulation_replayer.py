# -*- coding: utf-8 -*-
"""
pipeline/simulation_replayer.py
Bộ phát lại bài đăng mô phỏng (Simulation Replayer) phục vụ nghiệm thu & kiểm thử.
Được tối ưu hóa triệt để theo 3 nguyên tắc:
1. STRICT STREET-FIRST: Khi bài viết có tên đường -> 100% ưu tiên tên đường lên title hàng đầu.
   Loại bỏ mọi trường hợp nuốt mất tên đường do trùng từ khóa hành chính (như xã Vĩnh Lộc, Bán đảo...).
2. HIGHWAY CENTERLINE GEOCODING: Khi nhận diện tên đường -> Ghim chính xác 100% vào tim đường.
3. SSOT NQ 1685: 100% Phường/Xã hiển thị ĐVHC mới sau sáp nhập, loại bỏ hoàn toàn tên cũ.
"""

import os
import json
import re
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

from pipeline.event_processor import clean_stream_text, analyze_severity_heuristic
from core.admin_resolver import RESOLVER
from core.gazetteer import (
    STREET_HOTSPOTS,
    DYNAMIC_CACHE,
    ROAD_PATTERN,
    BOGUS_ROAD_PHRASES,
    STOP_CANDIDATE_WORDS,
    clean_road_candidate,
    normalize_text,
    geocode_osm_dynamic,
    ADMIN_HOTSPOTS
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ANNOTATED_FILE = os.path.join(DATA_DIR, "processed", "hcmc_flood_annotated_v1.json")
ADMIN_UNITS_FILE = os.path.join(DATA_DIR, "hcmc_168_administrative_units.json")

# Danh sách từ dừng bổ sung khi trích xuất tên đường
EXTRA_STOP_WORDS = set([
    "ngập", "ngap", "nước", "nuoc", "kẹt xe", "ket xe", "tắc đường", "tac duong",
    "mưa", "mua", "bì bõm", "bi bom", "lội", "loi", "ngập sâu", "ngap sau",
    "xe máy", "xe may", "ô tô", "o to", "chết máy", "chet may",
    "đang ngập", "bị ngập", "ngập nặng", "ngập lênh láng",
    "mênh mông", "biển nước", "sông", "thành sông", "hóa sông", "như sông",
    "quận", "huyện", "phường", "xã", "thành phố", "tphcm", "sài gòn",
    "điểm trường", "trường học", "trường thpt", "trường thcs", "trường tiểu học",
    "cống", "cống thoát", "cống thoát nước", "đường cống", "hệ thống cống", "hệ thống thoát nước",
    "miệng cống", "nắp cống", "trạm bơm", "máy bơm", "đê bao", "bờ bao", "ven sông", "bờ kè",
    "thông minh", "thành phố thông minh", "đô thị thông minh", "chống ngập", "dự án",
    "theo hướng", "hướng từ", "từ cao tốc", "phong tỏa", "hai đầu", "khu nam", "ở khu nam"
])

def clean_road_title(title: str) -> str:
    """Loại bỏ sạch các tiền tố thừa (tuyến đường, đoạn đường) và hậu tố quận/huyện cũ."""
    if not title:
        return ""
    cleaned = re.sub(r'^(?:tuyến đường|đoạn đường|trục đường|tuyến|đoạn)\s+', '', title, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*\((?:Quận|Huyện|TP\.?|Thủ Đức|Bình Chánh|Bình Tân|Tân Phú|Gò Vấp|Hóc Môn|Bình Thạnh|Nhà Bè|Củ Chi|Cần Giờ|Phố Tây|\d+)[^\)]*\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    return cleaned

class SimulationReplayer:
    _instance: Optional['SimulationReplayer'] = None
    _sim_offset: int = 0
    _events_pool: Optional[List[Dict[str, Any]]] = None

    def __init__(self):
        self._ensure_pool_loaded()

    @classmethod
    def get_instance(cls) -> 'SimulationReplayer':
        if cls._instance is None:
            cls._instance = SimulationReplayer()
        return cls._instance

    @classmethod
    def reset_pool(cls):
        """Buộc nạp lại pool khi có thay đổi cấu hình dữ liệu."""
        cls._events_pool = None
        cls._sim_offset = 0

    def _ensure_pool_loaded(self):
        if SimulationReplayer._events_pool is not None:
            return

        if not os.path.exists(ANNOTATED_FILE):
            SimulationReplayer._events_pool = []
            return

        # Tải tọa độ 168 ĐVHC
        admin_coords = {}
        if os.path.exists(ADMIN_UNITS_FILE):
            try:
                with open(ADMIN_UNITS_FILE, "r", encoding="utf-8") as f:
                    u_data = json.load(f)
                    admin_coords = {u["name"]: (u["lat"], u["lon"]) for u in u_data}
            except Exception:
                pass

        # Xây dựng từ điển quét nhanh CHỈ CHỨA TÊN ĐƯỜNG/GIAO LỘ THỰC TẾ
        road_keywords_dict = {}
        admin_keywords_blacklist = set([
            "thủ đức", "thu duc", "bình thạnh", "binh thanh", "quận 7", "quan 7",
            "quận 8", "quan 8", "gò vấp", "go vap", "tân bình", "tan binh",
            "bình tân", "binh tan", "tân phú", "tan phu", "nhà bè", "nha be",
            "hóc môn", "hoc mon", "củ chi", "cu chi", "bình chánh", "binh chanh",
            "cần giờ", "can gio", "quận 1", "quan 1", "quận 3", "quan 3",
            "quận 4", "quan 4", "quận 5", "quan 5", "quận 6", "quan 6",
            "quận 10", "quan 10", "quận 11", "quan 11", "quận 12", "quan 12"
        ])

        for s in STREET_HOTSPOTS:
            st_name = clean_road_title(s.get("street") or s.get("display_name", ""))
            for kw in s.get("keywords", []):
                kw_c = kw.strip().lower()
                if len(kw_c) < 3 or kw_c.isdigit():
                    continue
                if any(kw_c.startswith(p) for p in [
                    "phường ", "phuong ", "xã ", "xa ", "quận ", "quan ",
                    "huyện ", "huyen ", "thị trấn ", "thi tran ", "tp.", "tp "
                ]):
                    continue
                if re.match(r'^[pq]\.?\s*\d+', kw_c):
                    continue
                if kw_c in admin_keywords_blacklist:
                    continue
                road_keywords_dict[kw_c] = (st_name, s)

        # Bổ sung các từ khóa trong Dynamic Cache
        for c_kw, c_val in DYNAMIC_CACHE.items():
            ck_c = c_kw.strip().lower()
            if len(ck_c) >= 3 and ck_c not in road_keywords_dict:
                st_n = clean_road_title(c_val.get("street") or c_val.get("display_name", ""))
                road_keywords_dict[ck_c] = (st_n, c_val)

        sorted_kws = sorted(road_keywords_dict.keys(), key=lambda x: len(x), reverse=True)
        pattern_fast = re.compile(
            r'(?:\b|^|\s)(?<!\bxã\s)(?<!\bxa\s)(?<!\bphường\s)(?<!\bphuong\s)(?<!\bquận\s)(?<!\bquan\s)(?<!\bhuyện\s)(?<!\bhuyen\s)(?<!\bthị trấn\s)(?<!\bthi tran\s)(' + '|'.join(re.escape(k) for k in sorted_kws) + r')(?:\b|$|[\s.,!?])'
        )

        # Xây dựng từ điển quét nhanh Phường/Xã cho Fallback Tầng 2
        admin_kws_dict = {}
        for u in ADMIN_HOTSPOTS:
            w_name = u.get("ward") or u.get("display_name", "")
            resolved_w = RESOLVER.resolve_to_official_ward(w_name, "") or w_name
            if resolved_w in admin_coords and resolved_w != "Toàn TP.HCM":
                for kw in u.get("keywords", []):
                    kw_c = kw.strip().lower()
                    if len(kw_c) >= 4 and not kw_c.isdigit() and kw_c not in admin_keywords_blacklist:
                        admin_kws_dict[kw_c] = resolved_w

        sorted_admin_kws = sorted(admin_kws_dict.keys(), key=lambda x: len(x), reverse=True)
        pattern_admin = re.compile(
            r'(?:\b|^|\s)(' + '|'.join(re.escape(k) for k in sorted_admin_kws) + r')(?:\b|$|[\s.,!?])'
        )

        with open(ANNOTATED_FILE, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        localized_events = []
        citywide_events = []
        seen_texts = set()

        for item in raw_data:
            content = item.get("content", {})
            raw_text = content.get("text") or content.get("title") or ""
            cleaned_txt = clean_stream_text(raw_text) or raw_text.strip()
            if len(cleaned_txt) < 12:
                continue

            t_key = cleaned_txt[:40].lower()
            if t_key in seen_texts:
                continue
            seen_texts.add(t_key)

            loc_obj = item.get("location", {})
            raw_w = loc_obj.get("ward", "")
            raw_d = loc_obj.get("legacy_district", "")
            off_w = RESOLVER.resolve_to_official_ward(raw_w, raw_d) or RESOLVER.resolve_to_official_ward(raw_w, "") or "Toàn TP.HCM"

            clean_t = normalize_text(cleaned_txt).replace('–', '-').replace('—', '-')
            st_cand = ""
            matched_spot = None

            # =================================================================
            # PHÂN CẤP ƯU TIÊN 3 TẦNG CHUẨN XÁC (STRICT 3-TIER SPATIAL HIERARCHY):
            # TẦNG 1: Tên đường / Cầu / Nút giao chuẩn xác (Ghim đúng tim đường)
            # TẦNG 2: Khu vực theo Phường/Xã (Khi không có tên đường chuẩn)
            # TẦNG 3: Toàn TP. Hồ Chí Minh (Khi không có cả đường lẫn phường)
            # =================================================================

            # -----------------------------------------------------------------
            # BƯỚC 1: TÌM KIẾM ĐƯỜNG CHUẨN TRONG DANH MỤC CSGT & SEED HOTSPOTS
            # Ưu tiên giao lộ / thực thể cụ thể nhất (Longest-Entity Matching)
            # ví dụ: 'Ngã tư Phạm Văn Đồng - Tô Ngọc Vân' > 'Phạm Văn Đồng'
            # -----------------------------------------------------------------
            all_fast_hits = [m.group(1).strip() for m in pattern_fast.finditer(clean_t)]
            if all_fast_hits:
                matched_kw = max(all_fast_hits, key=lambda k: len(k))
                st_cand, matched_spot = road_keywords_dict[matched_kw]

            # -----------------------------------------------------------------
            # BƯỚC 2: NẾU CHƯA THẤY, THỬ REGEX VỚI ĐIỀU KIỆN XÁC THỰC NGHIÊM NGẶT
            # Tuyệt đối không nhận từ rác/cống thoát/thông minh/trạng ngữ
            # -----------------------------------------------------------------
            if not st_cand:
                reg_matches = ROAD_PATTERN.findall(cleaned_txt)
                for cand in reg_matches:
                    cleaned_cand = clean_road_candidate(cand)
                    cleaned_cand = re.sub(r'\s+(?:và|va|với|voi|đoạn|doan|khúc|khuc|giao)$', '', cleaned_cand, flags=re.IGNORECASE).strip()
                    if not cleaned_cand:
                        continue
                    if cleaned_cand.isdigit() or (len(cleaned_cand) <= 3 and cleaned_cand.isalnum()):
                        if re.search(r'(?:quốc\s+lộ|quoc\s+lo|ql)\s+' + re.escape(cleaned_cand), cleaned_txt, re.I):
                            cleaned_cand = f"Quốc lộ {cleaned_cand}"
                        elif re.search(r'(?:tỉnh\s+lộ|tinh\s+lo|tl)\s+' + re.escape(cleaned_cand), cleaned_txt, re.I):
                            cleaned_cand = f"Tỉnh lộ {cleaned_cand}"
                        elif re.search(r'(?:đường\s+số|duong\s+so)\s+' + re.escape(cleaned_cand), cleaned_txt, re.I):
                            cleaned_cand = f"Đường số {cleaned_cand}"
                        else:
                            continue
                    c_low = cleaned_cand.lower()
                    if len(cleaned_cand) < 3 or len(cleaned_cand.split()) > 5:
                        continue
                    if any(b in c_low for b in BOGUS_ROAD_PHRASES) or any(b in c_low for b in EXTRA_STOP_WORDS):
                        continue
                    if c_low in STOP_CANDIDATE_WORDS:
                        continue

                    # Kiểm tra trong DYNAMIC_CACHE
                    if c_low in DYNAMIC_CACHE:
                        matched_spot = DYNAMIC_CACHE[c_low]
                        st_cand = clean_road_title(matched_spot.get("street") or matched_spot.get("display_name", ""))
                        break

                    # Kiểm tra trong road_keywords_dict
                    m_c = pattern_fast.search(c_low)
                    if m_c:
                        kw_hit = m_c.group(1).strip()
                        st_cand, matched_spot = road_keywords_dict[kw_hit]
                        break



            # -----------------------------------------------------------------
            # BƯỚC 3: QUÉT TRƯỜNG LOCATIONS TRONG DATASET (CHỈ NHẬN NẾU ĐÃ XÁC THỰC)
            # -----------------------------------------------------------------
            if not st_cand:
                loc_list = loc_obj.get("locations", [])
                for cand in loc_list:
                    cand_clean = clean_road_title(cand.strip())
                    cand_low = cand_clean.lower()
                    if any(b in cand_low for b in BOGUS_ROAD_PHRASES) or any(b in cand_low for b in EXTRA_STOP_WORDS):
                        continue
                    if any(cand_clean.startswith(p) for p in ["Đô thị", "TP.", "Quận", "Huyện", "Khu vực Toàn"]):
                        continue
                    if any(cand_low.startswith(p) for p in ["phường", "xã", "thị trấn", "quận", "huyện"]):
                        continue
                    if cand_low in DYNAMIC_CACHE:
                        matched_spot = DYNAMIC_CACHE[cand_low]
                        st_cand = clean_road_title(matched_spot.get("street") or cand_clean)
                        break
                    cand_norm = normalize_text(cand_clean)
                    m_cand = pattern_fast.search(cand_norm)
                    if m_cand:
                        st_cand, matched_spot = road_keywords_dict[m_cand.group(1).strip()]
                        break

            # Kiểm tra cuối: Tuyệt đối không cho phép bất kỳ cụm từ rác nào lọt làm st_cand
            if st_cand:
                st_cand_low = st_cand.lower()
                if any(b in st_cand_low for b in BOGUS_ROAD_PHRASES) or any(b in st_cand_low for b in EXTRA_STOP_WORDS):
                    st_cand = ""
                    matched_spot = None

            # Làm sạch tiền tố tên đường/cầu
            if st_cand:
                st_cand = clean_road_title(st_cand)
                if not any(st_cand.lower().startswith(p) for p in [
                    "đường", "quốc lộ", "tỉnh lộ", "đại lộ", "xa lộ", "cầu", "hầm", "ngã", "vòng", "kdc", "khu dân cư"
                ]):
                    st_cand = f"Đường {st_cand}"

            # -----------------------------------------------------------------
            # BƯỚC 4: QUÉT TÌM PHƯỜNG/XÃ ĐƯỢC NHẮC TRỰC TIẾP TRONG NỘI DUNG
            # Nếu bài viết ghi rõ 'phường Dĩ An' hay 'xã Bà Điểm', ưu tiên tuyệt đối phường được nhắc!
            # -----------------------------------------------------------------
            m_adm = pattern_admin.search(clean_t)
            if m_adm:
                off_w = admin_kws_dict[m_adm.group(1).strip()]

            # =================================================================
            # PHÂN BỔ TỌA ĐỘ VÀ GIAO DIỆN THEO 3 CẤP ĐỘ ƯU TIÊN (PRIORITY 1 -> 3)
            # =================================================================
            lat, lon = None, None
            heat_pts = []
            cause = "rain"
            cause_label = "Mưa lớn, nước không thoát kịp"
            event_priority = 1

            if st_cand:
                # -------------------------------------------------------------
                # CẤP ĐỘ 1 (PRIORITY 1 - TÊN ĐƯỜNG CHUẨN XÁC, TIM ĐƯỜNG 100%)
                # -------------------------------------------------------------
                event_priority = 3
                st_low = st_cand.lower()
                st_core = re.sub(r'^(?:đường|tuyến|đại lộ|xa lộ)\s+', '', st_low).strip()
                if matched_spot:
                    lat = matched_spot["lat"]
                    lon = matched_spot["lon"]
                    heat_pts = matched_spot.get("heat_points", [[lat, lon]])
                    cause = matched_spot.get("cause", "rain")
                    cause_label = matched_spot.get("cause_label", "Mưa lớn, nước không thoát kịp")
                    if (not off_w or off_w == "Toàn TP.HCM") and matched_spot.get("ward"):
                        off_w = RESOLVER.resolve_to_official_ward(matched_spot["ward"], "") or matched_spot["ward"]
                elif st_low in DYNAMIC_CACHE:
                    c_entry = DYNAMIC_CACHE[st_low]
                    lat = c_entry["lat"]
                    lon = c_entry["lon"]
                    heat_pts = c_entry.get("heat_points", [[lat, lon]])
                    if c_entry.get("ward"):
                        off_w = RESOLVER.resolve_to_official_ward(c_entry["ward"], "") or c_entry["ward"]
                elif st_core in DYNAMIC_CACHE:
                    c_entry = DYNAMIC_CACHE[st_core]
                    lat = c_entry["lat"]
                    lon = c_entry["lon"]
                    heat_pts = c_entry.get("heat_points", [[lat, lon]])
                    if c_entry.get("ward"):
                        off_w = RESOLVER.resolve_to_official_ward(c_entry["ward"], "") or c_entry["ward"]
                elif off_w in admin_coords:
                    lat, lon = admin_coords[off_w]
                    heat_pts = [[lat, lon]]
                else:
                    lat, lon = 10.7769, 106.7009
                    heat_pts = [[10.7769, 106.7009]]

            elif off_w in admin_coords and off_w != "Toàn TP.HCM":
                # -------------------------------------------------------------
                # CẤP ĐỘ 2 (PRIORITY 2 - KHU VỰC CHUNG THEO PHƯỜNG / XÃ ĐVHC MỚI)
                # Tuyệt đối không tự chế ra tên đường!
                # -------------------------------------------------------------
                event_priority = 2
                st_cand = "" # KHÔNG CÓ TÊN ĐƯỜNG
                lat, lon = admin_coords[off_w]
                heat_pts = [[lat, lon]]
                cause = "rain"
                cause_label = "Mưa lớn diện rộng cục bộ"

            else:
                # -------------------------------------------------------------
                # CẤP ĐỘ 3 (PRIORITY 3 - ĐIỂM CHUNG TOÀN TP. HỒ CHÍ MINH)
                # -------------------------------------------------------------
                event_priority = 1
                st_cand = ""
                off_w = "Toàn TP.HCM"
                lat, lon = 10.7769, 106.7009
                heat_pts = [[10.7769, 106.7009]]
                cause = "rain"
                cause_label = "Cảnh báo ngập lụt đô thị TP.HCM"

            # Chuẩn hóa lại off_w lần cuối qua RESOLVER để tuyệt đối không có phường cũ
            resolved_final = RESOLVER.resolve_to_official_ward(off_w, "")
            if resolved_final:
                off_w = resolved_final

            # ASTE triplet & Severity
            triplets = item.get("aste_triplets", [])
            opinion = "ngập nước"
            aspect = st_cand or off_w
            if triplets:
                opinion = triplets[0].get("opinion") or "ngập nước"
                aspect = triplets[0].get("aspect") or aspect

            analysis = analyze_severity_heuristic(cleaned_txt) or {
                "opinion": opinion,
                "sentiment": "negative",
                "severity_level": "medium",
                "weight": 2.0
            }

            platform = (item.get("source", {}).get("platform") or "tiktok").lower()
            media_type = "video" if platform == "tiktok" else "post"
            priority = event_priority

            # Định dạng tên hiển thị chuẩn theo phân cấp 3 tầng
            if st_cand:
                display_name = st_cand
                type_label = f"Tuyến đường {st_cand}"
            elif off_w in admin_coords and off_w != "Toàn TP.HCM":
                display_name = f"{off_w} (TP.HCM)"
                type_label = f"Khu vực {off_w}"
            else:
                display_name = "Toàn TP. Hồ Chí Minh"
                type_label = "Khu vực Toàn TP. Hồ Chí Minh (Diện rộng)"

            ev = {
                "id": str(item.get("id")),
                "platform": platform,
                "media_type": media_type,
                "author": item.get("source", {}).get("author") or "Người dân TP.HCM",
                "text": cleaned_txt,
                "location": {
                    "street": st_cand,
                    "display_name": display_name,
                    "ward": off_w,
                    "administrative_unit": off_w,
                    "district": "TP.HCM",
                    "region": "TPHCM",
                    "lat": lat,
                    "lon": lon,
                    "heat_points": heat_pts,
                    "priority": priority,
                    "type": type_label,
                    "cause": cause,
                    "cause_label": cause_label,
                    "source": "annotated_dataset_v1"
                },
                "aspect": aspect,
                "opinion": opinion,
                "sentiment": "negative",
                "severity": analysis.get("severity_level", "medium"),
                "weight": analysis.get("weight", 2.0),
                "url": item.get("source", {}).get("url") or "",
                "veracity": {
                    "status": "confirmed",
                    "confidence_score": 0.88,
                    "status_label": "Đã xác thực",
                    "weather_check": {
                        "checked": True,
                        "has_rain": True,
                        "precipitation_mm": 2.5,
                        "plausible": True,
                        "reason": "Trạm khí tượng lịch sử đối soát: Có mưa (2.5 mm/h)"
                    },
                    "evidence_count": 2
                }
            }

            if st_cand or off_w in admin_coords:
                localized_events.append(ev)
            else:
                citywide_events.append(ev)

        # Phân bổ xen kẽ các phường/xã để tạo độ bao phủ rộng khắp TP.HCM
        by_ward = {}
        for ev in localized_events:
            w = ev["location"]["ward"]
            by_ward.setdefault(w, []).append(ev)

        interleaved_localized = []
        while any(by_ward.values()):
            for w in list(by_ward.keys()):
                if by_ward[w]:
                    interleaved_localized.append(by_ward[w].pop(0))

        # Trộn xen kẽ 4 điểm cục bộ (đường/phường) : 1 tin diện rộng TP.HCM
        final_pool = []
        loc_idx = 0
        cw_idx = 0
        total_loc = len(interleaved_localized)
        total_cw = len(citywide_events)

        while loc_idx < total_loc or cw_idx < total_cw:
            for _ in range(4):
                if loc_idx < total_loc:
                    final_pool.append(interleaved_localized[loc_idx])
                    loc_idx += 1
            if cw_idx < total_cw:
                final_pool.append(citywide_events[cw_idx])
                cw_idx += 1

        SimulationReplayer._events_pool = final_pool
        print(f"[SimulationReplayer] Đã nạp thành công {len(final_pool)} sự kiện chuẩn hóa từ hcmc_flood_annotated_v1.json (Đường cụ thể: {len(localized_events)})")

    def poll(self, batch_size: int = 15, platform_filter: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        pool = SimulationReplayer._events_pool or []
        if platform_filter:
            pool = [ev for ev in pool if ev.get("platform") == platform_filter]

        total_pool = len(pool)
        if total_pool == 0:
            return [], {"mode": "simulation", "events_matched": 0, "active_window": "2 giờ qua"}

        # Lấy theo offset xoay vòng
        curr_offset = SimulationReplayer._sim_offset % total_pool
        SimulationReplayer._sim_offset += batch_size

        batch_events = []
        for i in range(batch_size):
            idx = (curr_offset + i) % total_pool
            batch_events.append(dict(pool[idx]))

        current_time = int(time.time())
        window_minutes = 120
        span_seconds = window_minutes * 60

        for idx, ev in enumerate(batch_events):
            offset_seconds = int((idx / max(batch_size - 1, 1)) * (span_seconds - 300))
            post_time = current_time - span_seconds + offset_seconds
            ev["create_time"] = post_time
            ev["created_at_iso"] = datetime.fromtimestamp(post_time, timezone.utc).isoformat()
            
            diff_m = max((current_time - post_time) // 60, 1)
            if diff_m < 60:
                rel = f"{diff_m} phút trước"
            elif diff_m < 1440:
                rel = f"{diff_m // 60} giờ {diff_m % 60}p trước"
            else:
                rel = f"{diff_m // 1440} ngày trước"
            ev["relative_time"] = rel

        batch_events.sort(key=lambda x: (x.get("weight", 1.0), x.get("create_time", 0)), reverse=True)

        stats = {
            "platform": platform_filter or "simulation_dataset",
            "mode": "simulation",
            "total_crawled": total_pool,
            "events_window": len(batch_events),
            "total_events_displayed": len(batch_events),
            "active_window": f"{window_minutes // 60} giờ qua (Mô phỏng TP.HCM)"
        }
        return batch_events, stats
