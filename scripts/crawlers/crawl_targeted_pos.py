"""
scripts/crawl_targeted_pos.py
Kịch bản cào dữ liệu chuyên biệt cho nhãn POSITIVE (POS) & NEUTRAL (NEU) theo chuẩn HUONG_DAN_SUA_DATASET_ASTE_V3.md:
- Rào 3 lớp bảo vệ ở CẤP ĐỘ CÂU (Sentence-Level Litmus Test):
  1. Truy vấn cụm ngắn tự nhiên (Natural Query Clusters) trên Facebook & TikTok để tăng độ phủ (Recall).
  2. Bóc tách từng câu độc lập: Không gạt bỏ bài viết chỉ vì câu trước nhắc đến 'ngập/chết máy' nếu câu sau có 'nước đã rút/khô ráo/thông xe'.
  3. Bộ lọc loại trừ nghiêm ngặt tại câu: Chặn triệt để trạng thái chưa rút ('chờ nước rút', 'chưa rút', 'rút rất chậm'), thể thao, BĐS, ngoại tỉnh.
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

from core.gazetteer import normalize_text, HOTSPOTS, OUT_OF_SCOPE_LOCATIONS
from pipeline.event_processor import clean_stream_text, contains_spam_or_noise
from scripts.crawlers.organize_raw_episodes import determine_episode_id

# -----------------------------------------------------------------------------
# 1. RÀO CHẮN TRẠNG THÁI CHƯA RÚT / BẾ TẮC (ÁP DỤNG TRÊN TỪNG CÂU)
# -----------------------------------------------------------------------------
SENTENCE_DISTRESS_CUES = [
    "chờ nước rút", "đợi nước rút", "đợi cho nước rút", "chờ cho nước rút",
    "đứng chờ nước", "ngồi chờ nước", "chờ mưa ngớt", "chờ mưa tạnh",
    "khi nào hết ngập", "bao giờ nước rút", "chưa rút", "chưa rút nước",
    "vẫn ngập", "ngập chưa rút", "rút chậm", "rút rất chậm", "không rút kịp",
    "khi nào nước rút", "tấp vào lề đứng chờ", "tấp lên lề đứng chờ", "chờ cứu hộ"
]

# -----------------------------------------------------------------------------
# 2. RÀO CHẮN RÁC THỂ THAO / BĐS / PR / NGOẠI TỈNH
# -----------------------------------------------------------------------------
JUNK_OFFTOPIC_CUES = [
    "pha nước rút", "chạy nước rút", "giai đoạn nước rút", "nước rút thi công",
    "tay đua", "về đích", "cầu đi bộ", "nhựa duy tân", "duy tân", "cải tạo diện mạo",
    "deal hot", "ngập trời", "giải mật", "hồ sơ giải mật", "nhà sách", "khai trương",
    "độc quyền trên", "series tập", "cánh sóng âm", "khuyến mãi", "sale sập sàn",
    "mực tím", "truyện hạt lúa", "cia sài gòn", "bán nhà", "cho thuê", "phòng trọ",
    "căn hộ", "vinhomes", "bánh mì", "xe lướt", "odo", "thi hộ", "học hộ",
    "thông cống nghẹt", "hút hầm cầu", "thông nghẹt", "sạc xanh", "bảo dưỡng xe",
    "hà nội", "mcer", "marie curie", "đà lạt", "đà nẵng", "hải phòng", "thái nguyên",
    "nông cống", "thanh hóa", "nghệ an", "quảng ninh", "lâm đồng", "cà mau",
    "đồng nai", "phước tân", "biên hòa", "biên hoà", "long thành", "nhơn trạch"
]

# -----------------------------------------------------------------------------
# 3. TÍN HIỆU PHỤC HỒI / KHẲNG ĐỊNH NƯỚC ĐÃ RÚT (POS)
# -----------------------------------------------------------------------------
AFFIRMATIVE_POS_CUES = [
    "nước đã rút", "nước đã rút hết", "nước rút hết", "nước rút hoàn toàn",
    "đã rút hẳn", "đã hết ngập", "hết ngập", "không còn ngập", "đường đã khô ráo",
    "đã khô ráo", "khô ráo hoàn toàn", "mặt đường khô ráo", "khô ráo sạch sẽ",
    "lưu thông bình thường", "di chuyển bình thường", "lưu thông thuận lợi",
    "giao thông ổn định trở lại", "đi lại dễ dàng", "thông thoáng trở lại",
    "mặt đường thông thoáng", "nước rút nhanh", "xe cộ qua lại bình thường",
    "phát huy hiệu quả", "hoạt động hiệu quả", "thoát nước nhanh", "chống ngập tốt",
    "ứng trực kịp thời", "kịp thời hỗ trợ", "bình yên sau mưa", "khô ráo", "khô rang",
    "rút sạch", "thông xe", "hết ngập hẳn"
]

# -----------------------------------------------------------------------------
# 4. TÍN HIỆU CÔNG TRÌNH / THỦY VĂN / ĐO ĐẠC (NEU)
# -----------------------------------------------------------------------------
AFFIRMATIVE_NEU_CUES = [
    "cống ngăn triều", "cống kiểm soát triều", "cống thoát nước", "trạm bơm",
    "máy bơm", "vận hành thử nghiệm", "vận hành hết công suất", "hoạt động hết công suất",
    "vận hành liên tục", "khánh thành", "khởi công", "triển khai thi công", "thi công",
    "nghiệm thu", "nạo vét", "khơi thông", "nâng nền", "đê bao", "bờ kè",
    "đỉnh triều", "mực nước triều", "mực nước sông", "dự báo triều cường",
    "cảnh báo triều cường", "dự báo đỉnh triều", "đo được", "đo đạc", "đạt mức", "ở mức cao"
]

# -----------------------------------------------------------------------------
# 5. MA TRẬN TRUY VẤN MỞ RỘNG CỤM NGẮN TỰ NHIÊN (HIGH-RECALL CLUSTERS)
# -----------------------------------------------------------------------------
TARGETED_QUERIES = [
    # === Cụm ngắn tự nhiên POS trên Facebook ===
    ('site:facebook.com "nước đã rút" "TPHCM"', "facebook", "POS"),
    ('site:facebook.com "nước đã rút" "Sài Gòn"', "facebook", "POS"),
    ('site:facebook.com "nước rút sạch" "TPHCM"', "facebook", "POS"),
    ('site:facebook.com "hết ngập" "thông thoáng" "TPHCM"', "facebook", "POS"),
    ('site:facebook.com "đường khô ráo" "sau mưa" "TPHCM"', "facebook", "POS"),
    ('site:facebook.com "lưu thông bình thường" "triều cường" "TPHCM"', "facebook", "POS"),
    ('site:facebook.com "xe cộ qua lại bình thường" "TPHCM"', "facebook", "POS"),
    ('site:facebook.com "nước rút hết rồi" "Sài Gòn"', "facebook", "POS"),
    ('site:facebook.com "không còn ngập" "TPHCM"', "facebook", "POS"),
    ('site:facebook.com "thông xe" "nước rút" "TPHCM"', "facebook", "POS"),
    ('site:facebook.com "Trần Xuân Soạn" "rút hết"', "facebook", "POS"),
    ('site:facebook.com "Thảo Điền" "nước rút"', "facebook", "POS"),
    ('site:facebook.com "Nguyễn Hữu Cảnh" "nước rút"', "facebook", "POS"),
    ('site:facebook.com "Quốc Hương" "thông thoáng"', "facebook", "POS"),
    ('site:facebook.com "Phan Huy Ích" "nước rút"', "facebook", "POS"),
    ('site:facebook.com "Lê Văn Lương" "nước rút"', "facebook", "POS"),
    ('site:facebook.com "công nhân thoát nước" "hỗ trợ dân"', "facebook", "POS"),
    ('site:facebook.com "CSGT" "đẩy xe giúp dân" "TPHCM"', "facebook", "POS"),

    # === Cụm ngắn tự nhiên POS trên TikTok ===
    ('site:tiktok.com "nước đã rút" "TPHCM"', "tiktok", "POS"),
    ('site:tiktok.com "nước đã rút" "Sài Gòn"', "tiktok", "POS"),
    ('site:tiktok.com "nước rút sạch" "Sài Gòn"', "tiktok", "POS"),
    ('site:tiktok.com "hết ngập" "Sài Gòn"', "tiktok", "POS"),
    ('site:tiktok.com "đường khô ráo" "Sài Gòn"', "tiktok", "POS"),
    ('site:tiktok.com "bình thường trở lại" "mưa" "TPHCM"', "tiktok", "POS"),
    ('site:tiktok.com "sau mưa" "nước rút" "TPHCM"', "tiktok", "POS"),
    ('site:tiktok.com "Thảo Điền" "hết ngập"', "tiktok", "POS"),
    ('site:tiktok.com "Trần Xuân Soạn" "nước rút"', "tiktok", "POS"),
    ('site:tiktok.com "Nguyễn Hữu Cảnh" "hết ngập"', "tiktok", "POS"),
    ('site:tiktok.com "Huỳnh Tấn Phát" "nước rút"', "tiktok", "POS"),
    ('site:tiktok.com "nước rút hết" "Sài Gòn"', "tiktok", "POS"),

    # === Cụm ngắn tự nhiên NEU trên Facebook & TikTok ===
    ('site:facebook.com "cống ngăn triều" "vận hành" "TPHCM"', "facebook", "NEU"),
    ('site:facebook.com "trạm bơm" "vận hành" "TPHCM"', "facebook", "NEU"),
    ('site:facebook.com "dự án chống ngập" "thi công" "TPHCM"', "facebook", "NEU"),
    ('site:facebook.com "nạo vét rạch" "TPHCM"', "facebook", "NEU"),
    ('site:facebook.com "đỉnh triều" "trạm Phú An" "mực nước"', "facebook", "NEU"),
    ('site:facebook.com "đỉnh triều" "trạm Nhà Bè" "mực nước"', "facebook", "NEU"),
    ('site:facebook.com "dự báo triều cường" "TPHCM"', "facebook", "NEU"),
    ('site:tiktok.com "cống ngăn triều" "TPHCM"', "tiktok", "NEU"),
    ('site:tiktok.com "trạm bơm chống ngập" "TPHCM"', "tiktok", "NEU"),
    ('site:tiktok.com "dự án chống ngập" "TPHCM"', "tiktok", "NEU"),
    ('site:tiktok.com "nạo vét kênh" "TPHCM"', "tiktok", "NEU"),
    ('site:tiktok.com "triều cường đạt đỉnh" "TPHCM"', "tiktok", "NEU")
]


def load_existing_identifiers() -> Tuple[Set[str], Set[str]]:
    """Tải toàn bộ URL và MD5 hash đã tồn tại để đảm bảo không trùng lặp."""
    seen_urls = set()
    seen_hashes = set()

    for root, _, files in os.walk(EPISODES_DIR):
        for f in files:
            if f.endswith("_raw.json"):
                fpath = os.path.join(root, f)
                try:
                    with open(fpath, "r", encoding="utf-8-sig") as fp:
                        items = json.load(fp)
                        if isinstance(items, list):
                            for it in items:
                                u = it.get("url") or it.get("webVideoUrl") or ""
                                if u: seen_urls.add(u)
                                t = it.get("text") or it.get("title") or ""
                                if t: seen_hashes.add(hashlib.md5(t.strip().lower().encode("utf-8")).hexdigest())
                except Exception:
                    pass

    return seen_urls, seen_hashes


def extract_clean_sentences_by_intent(text: str, intent: str) -> List[str]:
    """
    Quy Tắc Quyết Định Cực Tính 1 Câu (1-Sentence Litmus Test):
    Tách bài viết thành từng câu độc lập và kiểm tra tính hợp lệ trên TỪNG CÂU.
    """
    if not text or len(text) < 15:
        return []

    # Tách câu
    raw_sentences = re.split(r'(?:[\r\n]+|(?<=[.!?])\s+)', text)
    valid_sentences = []

    for s in raw_sentences:
        s_clean = s.strip()
        if len(s_clean) < 15 or len(s_clean) > 250:
            continue
        s_low = s_clean.lower()

        # 1. Rào chắn rác thể thao / BĐS / ngoại tỉnh
        if any(junk in s_low for junk in JUNK_OFFTOPIC_CUES):
            continue
        if contains_spam_or_noise(s_clean):
            continue

        # 2. Kiểm tra theo Intent
        if intent == "POS":
            # Chặn câu đang trong trạng thái bế tắc / chưa rút
            if any(cue in s_low for cue in SENTENCE_DISTRESS_CUES):
                continue
            # Phải có từ khẳng định nước rút / phục hồi
            if not any(cue in s_low for cue in AFFIRMATIVE_POS_CUES):
                continue
        elif intent == "NEU":
            # Phải có từ công trình / kỹ thuật / đo đạc
            if not any(cue in s_low for cue in AFFIRMATIVE_NEU_CUES):
                continue

        # 3. Phải có bối cảnh TP.HCM hoặc mưa ngập
        has_ctx = any(k in s_low for k in [
            "ngập", "triều cường", "mưa", "thoát nước", "nước ngập", "thủy triều",
            "cống", "trạm bơm", "rạch", "kênh", "đỉnh triều", "mực nước", "nạo vét",
            "tphcm", "tp.hcm", "sài gòn", "thủ đức", "bình thạnh", "gò vấp", "nhà bè",
            "trần xuân soạn", "nguyễn hữu cảnh", "quốc hương", "thảo điền", "ung văn khiêm",
            "huỳnh tấn phát", "phú an", "mương chuối", "bến nghé", "tân thuận"
        ])
        if not has_ctx:
            continue

        valid_sentences.append(s_clean)

    return valid_sentences


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
        if m_user: author = m_user.group(1)
        m_vid = re.search(r'/video/(\d+)', url)
        if m_vid: item_id = m_vid.group(1)
    elif platform == "facebook":
        m_page = re.search(r'facebook\.com/([^/?#]+)', url)
        if m_page and m_page.group(1) not in ["groups", "watch", "reel", "story.php", "permalink.php"]:
            author = m_page.group(1)
        m_post = re.search(r'/(?:posts|videos|reel)/([a-zA-Z0-9_.-]+)', url)
        if m_post: item_id = m_post.group(1)

    return author, item_id


def run_targeted_pos_neu_crawler(max_per_query: int = 50):
    print("=" * 80)
    print("🚀 KHỞI ĐỘNG CÀO DỮ LIỆU POS & NEU (SENTENCE-LEVEL PARSING & NATURAL CLUSTERS)")
    print("=" * 80)

    seen_urls, seen_hashes = load_existing_identifiers()
    print(f"-> Đã nạp {len(seen_urls)} URLs và {len(seen_hashes)} content hashes hiện có để chống trùng lặp.")

    new_items_by_episode = defaultdict(lambda: defaultdict(list))
    total_found = 0
    total_added = 0
    added_pos = 0
    added_neu = 0
    rejected_junk = 0
    rejected_duplicate = 0

    for q_idx, (query, platform, intent) in enumerate(TARGETED_QUERIES, start=1):
        print(f"\n[{q_idx}/{len(TARGETED_QUERIES)}] Truy vấn [{intent}]: {query} ({platform.upper()})...")
        enc_q = urllib.parse.quote_plus(query)
        feed_url = f"https://news.google.com/rss/search?q={enc_q}&hl=vi&gl=VN&ceid=VN:vi"

        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"  Lỗi khi gọi RSS feed: {e}")
            continue

        entries = feed.entries[:max_per_query]
        print(f"  -> Nhận được {len(entries)} kết quả từ RSS Discovery.")

        for entry in entries:
            total_found += 1
            raw_title = getattr(entry, "title", "") or ""
            raw_summary = getattr(entry, "summary", "") or ""
            clean_title = re.sub(r'\s*-\s*(?:TikTok|Facebook)\s*$', '', raw_title, flags=re.IGNORECASE).strip()
            full_text = f"{clean_title}. {raw_summary}".strip()

            # Bóc tách các câu thỏa mãn Litmus Test của Intent
            valid_sentences = extract_clean_sentences_by_intent(full_text, intent)
            if not valid_sentences:
                rejected_junk += 1
                continue

            # Giải mã URL gốc
            rss_link = getattr(entry, "link", "")
            if not rss_link: continue

            try:
                decoded = gnewsdecoder(rss_link)
                decoded_url = decoded.get("decoded_url") if isinstance(decoded, dict) else decoded
            except Exception:
                decoded_url = ""

            if not decoded_url or not isinstance(decoded_url, str): continue
            if platform == "tiktok" and "tiktok.com" not in decoded_url.lower(): continue
            if platform == "facebook" and "facebook.com" not in decoded_url.lower(): continue

            # Phân vùng Episode
            pub_date_raw = getattr(entry, "published", "")
            d_str, iso_str = parse_rfc822_date(pub_date_raw)
            if not d_str:
                d_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                iso_str = datetime.now(timezone.utc).isoformat()

            ep_id = determine_episode_id(d_str)
            author_name, post_id = extract_author_and_id(decoded_url, platform)

            # Lưu từng câu hợp lệ độc lập
            for s_idx, sent in enumerate(valid_sentences):
                c_hash = hashlib.md5(sent.lower().encode("utf-8")).hexdigest()
                if c_hash in seen_hashes:
                    rejected_duplicate += 1
                    continue
                seen_hashes.add(c_hash)

                raw_record = {
                    "id": f"{post_id}_s{s_idx:02d}",
                    "url": decoded_url,
                    "webVideoUrl": decoded_url if platform == "tiktok" else "",
                    "mediaUrls": [decoded_url] if platform == "tiktok" else [],
                    "text": sent,
                    "title": clean_title,
                    "author": author_name,
                    "authorMeta": {"name": author_name},
                    "createTimeISO": iso_str,
                    "published": pub_date_raw,
                    "extracted_date": d_str,
                    "platform": platform,
                    "crawled_at": datetime.now(timezone.utc).isoformat(),
                    "crawler_source": "sentence_litmus_engine",
                    "targeted_intent": intent
                }

                new_items_by_episode[ep_id][platform].append(raw_record)
                total_added += 1
                if intent == "POS":
                    added_pos += 1
                else:
                    added_neu += 1

        time.sleep(0.15)

    print("\n" + "=" * 80)
    print("✨ HOÀN TẤT THU THẬP POS & NEU CẢI TIẾN:")
    print(f"  * Tổng số bài viết quét: {total_found}")
    print(f"  * Số câu bị loại (rác/không đúng intent): {rejected_junk}")
    print(f"  * Số câu bị loại do trùng lặp: {rejected_duplicate}")
    print(f"  * SỐ CÂU POS THU HOẠCH MỚI: {added_pos}")
    print(f"  * SỐ CÂU NEU THU HOẠCH MỚI: {added_neu}")
    print(f"  * TỔNG SỐ CÂU HỢP LỆ BỔ SUNG: {total_added}")
    print("=" * 80)

    # Ghi vào các file tương ứng trong data/raw/episodes/
    for ep_id, platforms in new_items_by_episode.items():
        ep_dir = os.path.join(EPISODES_DIR, ep_id)
        os.makedirs(ep_dir, exist_ok=True)

        for platform, items in platforms.items():
            raw_fname = f"{platform}_raw.json"
            target_path = os.path.join(ep_dir, raw_fname)

            existing_items = []
            if os.path.exists(target_path):
                try:
                    with open(target_path, "r", encoding="utf-8-sig") as fp:
                        existing_items = json.load(fp)
                        if not isinstance(existing_items, list):
                            existing_items = []
                except Exception:
                    existing_items = []

            merged_dict = {}
            for it in existing_items:
                uid = it.get("text") or it.get("url") or it.get("id")
                if uid: merged_dict[uid] = it
            for it in items:
                uid = it.get("text") or it.get("url") or it.get("id")
                if uid: merged_dict[uid] = it

            final_list = list(merged_dict.values())
            with open(target_path, "w", encoding="utf-8") as fp:
                json.dump(final_list, fp, ensure_ascii=False, indent=2)

            print(f"  + [{ep_id}] {platform.upper()}: Thêm {len(items)} câu -> Tổng: {len(final_list)} ({raw_fname})")

    print("\n-> Đã cập nhật toàn bộ bài POS & NEU vào các phân vùng Episode!")


if __name__ == "__main__":
    run_targeted_pos_neu_crawler(max_per_query=50)
