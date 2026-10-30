# -*- coding: utf-8 -*-
"""
scripts/crawl_hcm_core_csgt.py
Thu thập dữ liệu mạng xã hội (TikTok & Facebook) tập trung chuyên sâu vào
100+ Điểm nóng ngập lụt trung tâm TP.HCM theo danh mục CSGT PC08 (csgt_122_flood_hotspots.json).
- Tận dụng cả Title và Summary để nhận diện đầy đủ ngữ cảnh địa bàn TP.HCM.
- Lọc rác tuyệt đối: Chặn BĐS, F&B ẩm thực, xe cũ, dịch vụ hút hầm cầu.
- Ghi log audit liên tục từng mẫu.
"""

import os
import sys
import json
import re
import time
import hashlib
import urllib.parse
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, Any, List, Set, Optional, Tuple

import feedparser
from googlenewsdecoder import gnewsdecoder

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

DATA_DIR = os.path.join(ROOT_DIR, "data")
EPISODES_DIR = os.path.join(DATA_DIR, "raw", "episodes")
AUDIT_LOG_FILE = os.path.join(DATA_DIR, "crawl_csgt_audit.json")

from pipeline.event_processor import clean_stream_text, contains_spam_or_noise
from scripts.crawlers.organize_raw_episodes import determine_episode_id

FLOOD_INTENT_KEYWORDS = [
    "ngập", "ngap", "triều cường", "trieu cuong", "chết máy", "chet may",
    "bì bõm", "bi bom", "lội nước", "loi nuoc", "lút bánh", "lut banh",
    "nước dâng", "nuoc dang", "ngập sâu", "ngap sau", "biển nước", "bien nuoc",
    "thất thủ", "that thu", "ngập lụt", "ngap lut", "tràn vào nhà", "tran vao nha",
    "mênh mông nước", "sóng đánh", "ngập đường", "ngap duong", "dắt bộ", "dắt xe",
    "dẫn bộ", "xe chết máy", "ùn tắc do ngập", "ngập nặng", "ngap nang",
    "dự báo triều cường", "cảnh báo ngập", "đỉnh triều", "thủy kích"
]

HCM_ONLY_AFFIRMATIONS = [
    "tphcm", "tp.hcm", "tp hcm", "sài gòn", "sai gon", "hồ chí minh", "ho chi minh",
    "thủ đức", "thu duc", "bình thạnh", "quận 7", "bình tân", "tân bình", "quận 8",
    "gò vấp", "nhà bè", "hóc môn", "bình chánh", "quận 12", "quận 4", "quận 6", "tân phú",
    "quận 1", "quận 3", "quận 5", "quận 10", "quận 11", "phú nhuận"
]

OUT_OF_SCOPE_REGIONS = [
    "bình dương", "binh duong", "thủ dầu một", "dĩ an", "thuận an", "bến cát", "tân uyên",
    "vũng tàu", "vung tau", "bà rịa", "ba ria", "phú mỹ", "côn đảo", "long điền",
    "đồng nai", "dong nai", "biên hòa", "phước tân", "long thành", "nhơn trạch", "trảng bom",
    "hà nội", "đà nẵng", "hải phòng", "cần thơ", "cà mau", "nghệ an", "tuyên quang",
    "thái nguyên", "quảng ninh", "đà lạt", "bảo lộc", "nha trang", "lâm đồng"
]

JUNK_KEYWORDS = [
    "bán nhà", "bán đất", "cho thuê", "pass phòng", "cần sang nhượng", "sổ hồng riêng", "sổ đỏ",
    "chính chủ cần bán", "căn duplex", "chung cư mini", "studio ban công", "pax sky",
    "căn góc cực thoáng", "1pn", "2pn", "ban công tách bếp", "vách kính lùa", "sát vách quận 1",
    "xe lướt", "thu mua xe cũ", "thông cống nghẹt", "hút hầm cầu", "thông nghẹt giá rẻ",
    "vệ sinh môi trường", "gọi là tới phục vụ 24/24",
    "ngập tràn deal", "ngập tràn may mắn", "ngập tràn ưu đãi", "ngập tràn quà",
    "ngập tràn ánh sáng", "ngập tràn niềm vui", "ngập tràn tiếng cười", "ngập tràn hạnh phúc",
    "ngập tràn hy vọng", "ngập tràn năng lượng", "ngập tràn tết",
    "ngập ánh sáng", "ngập năng lượng", "ngập dầu", "ngập bơ", "ngập mỡ", "ngập dâu sữa", "ngập ngụa",
    "địa điểm ăn uống", "cháo nấm rơm", "bánh khọt", "quán chay", "mì cay", "cellphones",
    "sắm tết", "shin-chan", "đặt vé gặp cậu bé bút chì", "shop bí", "lục bình bãi tắm", "trung nam group", "thanh toán dự án", "giao 3 khu đất", "khu đất vàng", "kfc", "starbucks", "highlands coffee", "the pizza company", "tacos station", "familymart", "co.opmart", "deal 8/3",
    "ngô xương ngập", "thế kỉ", "lịch sử việt nam"
]

TOP_CSGT_HOTSPOTS = [
    ("Trần Xuân Soạn", "Quận 7"),
    ("Huỳnh Tấn Phát", "Quận 7"),
    ("Lê Văn Lương", "Nhà Bè"),
    ("Đào Sư Tích", "Nhà Bè"),
    ("Quốc Hương", "TP. Thủ Đức"),
    ("Thảo Điền", "TP. Thủ Đức"),
    ("Tô Ngọc Vân", "TP. Thủ Đức"),
    ("Linh Đông", "TP. Thủ Đức"),
    ("Võ Văn Ngân", "TP. Thủ Đức"),
    ("Kha Vạn Cân", "TP. Thủ Đức"),
    ("Đỗ Xuân Hợp", "TP. Thủ Đức"),
    ("Ung Văn Khiêm", "Bình Thạnh"),
    ("Nguyễn Xí", "Bình Thạnh"),
    ("Đinh Bộ Lĩnh", "Bình Thạnh"),
    ("Nguyễn Hữu Cảnh", "Bình Thạnh"),
    ("Phan Huy Ích", "Gò Vấp"),
    ("Lê Đức Thọ", "Gò Vấp"),
    ("Phạm Văn Chiêu", "Gò Vấp"),
    ("Nguyễn Văn Quá", "Quận 12"),
    ("Mễ Cốc", "Quận 8"),
    ("Bến Bình Đông", "Quận 8"),
    ("Bến Phú Định", "Quận 8"),
    ("Hồ Học Lãm", "Bình Tân"),
    ("Kinh Dương Vương", "Bình Tân"),
    ("Tân Hòa Đông", "Quận 6"),
]


def load_existing_identifiers() -> Tuple[Set[str], Set[str]]:
    seen_urls = set()
    seen_hashes = set()

    if os.path.exists(EPISODES_DIR):
        for root, _, files in os.walk(EPISODES_DIR):
            for f in files:
                if f.endswith("_raw.json"):
                    try:
                        with open(os.path.join(root, f), "r", encoding="utf-8-sig") as fp:
                            items = json.load(fp)
                            if isinstance(items, list):
                                for it in items:
                                    u = it.get("url") or it.get("webVideoUrl") or it.get("link") or ""
                                    if u:
                                        seen_urls.add(u)
                                    t = it.get("text") or it.get("caption") or it.get("title") or ""
                                    if t:
                                        seen_hashes.add(hashlib.md5(t.strip().lower().encode("utf-8")).hexdigest())
                    except Exception:
                        pass

    for vf in ["hcmc_flood_annotated_v1.json", "hcmc_flood_annotated_v2_multimodal.json"]:
        v_file = os.path.join(DATA_DIR, "processed", vf)
        if os.path.exists(v_file):
            try:
                with open(v_file, "r", encoding="utf-8") as fp:
                    v_items = json.load(fp)
                    for it in v_items:
                        src_url = it.get("source", {}).get("url") or ""
                        if src_url:
                            seen_urls.add(src_url)
                        txt = it.get("content", {}).get("text") or ""
                        if txt:
                            seen_hashes.add(hashlib.md5(txt.strip().lower().encode("utf-8")).hexdigest())
            except Exception:
                pass

    return seen_urls, seen_hashes


def evaluate_content(text: str, street_name: str) -> Tuple[bool, str]:
    clean = clean_stream_text(text)
    if not clean or len(clean) < 15:
        return False, "Văn bản quá ngắn"

    clean_low = clean.lower()

    for jw in JUNK_KEYWORDS:
        if jw in clean_low:
            return False, f"Chứa từ khóa rác: {jw}"

    if re.search(r'\bodo\s*(?::\s*)?\d+', clean_low):
        return False, "Quảng cáo xe ODO"

    for out_reg in OUT_OF_SCOPE_REGIONS:
        if out_reg in clean_low:
            if "xa lộ hà nội" not in clean_low and not any(hcm in clean_low for hcm in ["tphcm", "sài gòn", "thủ đức", "quận 7", "bình thạnh"]):
                return False, f"Ngoại phạm vi: {out_reg}"

    if not any(fk in clean_low for fk in FLOOD_INTENT_KEYWORDS):
        return False, "Không chứa hành vi ngập lụt thực tế"

    has_hcm = any(h in clean_low for h in HCM_ONLY_AFFIRMATIONS)
    has_target_street = (street_name.lower() in clean_low)
    has_csgt_spot = any(st.lower() in clean_low for st, _ in TOP_CSGT_HOTSPOTS)

    if not (has_hcm or has_target_street or has_csgt_spot):
        return False, "Không xác định được vị trí thuộc TP.HCM"

    return True, "Hợp lệ"


def parse_rfc822_date(date_str: str) -> Tuple[Optional[str], Optional[str]]:
    if not date_str:
        return None, None
    try:
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%d"), dt.isoformat()
    except Exception:
        pass
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d"), dt.isoformat()
    except Exception:
        return None, None


def extract_author_and_id(url: str, platform: str) -> Tuple[str, str]:
    author = f"{platform.capitalize()} Creator"
    item_id = hashlib.md5(url.encode("utf-8")).hexdigest()[:16]

    if platform == "tiktok":
        m_user = re.search(r'@([a-zA-Z0-9_.-]+)', url)
        if m_user:
            author = m_user.group(1)
        m_vid = re.search(r'/video/(\d+)', url)
        if m_vid:
            item_id = m_vid.group(1)
    elif platform == "facebook":
        m_page = re.search(r'facebook\.com/([^/?#]+)', url)
        if m_page and m_page.group(1) not in ["groups", "watch", "reel", "story.php", "permalink.php"]:
            author = m_page.group(1)
        m_post = re.search(r'/(?:posts|videos|reel)/([a-zA-Z0-9_.-]+)', url)
        if m_post:
            item_id = m_post.group(1)

    return author, item_id


def run_csgt_crawler(max_per_query: int = 25):
    print("=" * 80)
    print("BẮT ĐẦU CRAWL CSGT TRUNG TÂM TP.HCM (KÈM AUDIT CHI TIẾT)")
    print("=" * 80)

    seen_urls, seen_hashes = load_existing_identifiers()
    print(f"[*] Đã tải {len(seen_urls)} URLs và {len(seen_hashes)} content hashes.")

    queries = []
    for st, dist in TOP_CSGT_HOTSPOTS:
        queries.append((f'site:tiktok.com "{st}" "ngập"', "tiktok", st, dist))
        queries.append((f'site:facebook.com "{st}" "ngập"', "facebook", st, dist))

    audit_records = []
    new_items_by_episode = defaultdict(lambda: defaultdict(list))

    total_scanned = 0
    total_accepted = 0
    total_duplicates = 0
    total_rejected = 0

    for idx, (query, platform, street, district) in enumerate(queries, 1):
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=vi&gl=VN&ceid=VN:vi"

        try:
            feed = feedparser.parse(rss_url)
        except Exception:
            continue

        entries = feed.entries[:max_per_query]
        print(f"[{idx}/{len(queries)}] {platform.upper()}: '{street}' ({district}) -> {len(entries)} RSS entries.")

        for entry in entries:
            total_scanned += 1
            raw_title = getattr(entry, "title", "")
            raw_summary = getattr(entry, "summary", "")
            raw_link = getattr(entry, "link", "")
            pub_date = getattr(entry, "published", "")

            clean_title = re.sub(r'\s*-\s*(?:TikTok|Facebook)\s*$', '', raw_title, flags=re.IGNORECASE).strip()
            full_text = f"{clean_title}. {raw_summary}".strip()

            # Đánh giá nội dung
            is_valid, reason = evaluate_content(full_text, street)
            if not is_valid:
                total_rejected += 1
                audit_records.append({
                    "title": clean_title,
                    "platform": platform,
                    "street": street,
                    "status": "REJECTED",
                    "reason": reason
                })
                continue

            # Kiểm tra trùng lặp hash
            t_hash = hashlib.md5(clean_title.lower().encode("utf-8")).hexdigest()
            if t_hash in seen_hashes:
                total_duplicates += 1
                audit_records.append({
                    "title": clean_title,
                    "platform": platform,
                    "street": street,
                    "status": "DUPLICATE",
                    "reason": "Trùng lặp nội dung văn bản"
                })
                continue

            # Decode URL
            real_url = raw_link
            try:
                dec = gnewsdecoder(raw_link)
                if dec.get("status") and dec.get("decoded_url"):
                    real_url = dec["decoded_url"]
            except Exception:
                pass

            if platform == "tiktok" and "tiktok.com" not in real_url.lower():
                # Nếu decoder không trả về tiktok direct URL, thử giữ raw nếu link là news article
                pass
            if platform == "facebook" and "facebook.com" not in real_url.lower():
                pass

            if real_url in seen_urls:
                total_duplicates += 1
                audit_records.append({
                    "url": real_url,
                    "title": clean_title,
                    "platform": platform,
                    "street": street,
                    "status": "DUPLICATE",
                    "reason": "Trùng lặp URL"
                })
                continue

            seen_urls.add(real_url)
            seen_hashes.add(t_hash)

            date_str, iso_str = parse_rfc822_date(pub_date)
            ep_id = determine_episode_id(date_str)
            author, item_id = extract_author_and_id(real_url, platform)

            record = {
                "id": item_id,
                "url": real_url,
                "text": clean_title,
                "author": author,
                "published_at": iso_str or datetime.now(timezone.utc).isoformat(),
                "created_time": date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "crawler_source": "free_discovery_engine",
                "csgt_matched_street": street
            }

            if platform == "tiktok":
                record["webVideoUrl"] = real_url
                record["videoMeta"] = {"coverUrl": "", "downloadAddr": ""}
            elif platform == "facebook":
                record["post_url"] = real_url
                record["media_urls"] = []

            new_items_by_episode[ep_id][platform].append(record)
            total_accepted += 1

            audit_records.append({
                "url": real_url,
                "title": clean_title,
                "platform": platform,
                "street": street,
                "status": "ACCEPTED",
                "reason": f"Khớp CSGT: {street} - {district} (Episode: {ep_id})"
            })

    with open(AUDIT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(audit_records, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print(f"KẾT QUẢ TỔNG KẾT:")
    print(f"  * Tổng số ứng viên quét: {total_scanned}")
    print(f"  * Trùng lặp (URL hoặc Text): {total_duplicates}")
    print(f"  * Bị loại bỏ (Rác, ngoại tỉnh, không liên quan): {total_rejected}")
    print(f"  * MẪU MỚI ĐẠT CHUẨN: {total_accepted}")
    print("=" * 80)

    for ep_id, platforms in new_items_by_episode.items():
        ep_dir = os.path.join(EPISODES_DIR, ep_id)
        os.makedirs(ep_dir, exist_ok=True)
        for plat, items in platforms.items():
            if not items:
                continue
            raw_f = os.path.join(ep_dir, f"{plat}_raw.json")
            existing = []
            if os.path.exists(raw_f):
                try:
                    with open(raw_f, "r", encoding="utf-8") as rf:
                        existing = json.load(rf)
                except Exception:
                    existing = []
            existing.extend(items)
            with open(raw_f, "w", encoding="utf-8") as rf:
                json.dump(existing, rf, ensure_ascii=False, indent=2)
            print(f"  + [{ep_id}] {plat.upper()}: Thêm {len(items)} bài -> Tổng: {len(existing)}")

    return total_accepted, total_rejected, total_duplicates


if __name__ == "__main__":
    run_csgt_crawler()
