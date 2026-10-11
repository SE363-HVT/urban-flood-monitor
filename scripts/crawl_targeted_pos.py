"""
scripts/crawl_targeted_pos.py
Kịch bản cào dữ liệu chuyên biệt cho nhãn POSITIVE (POS) về phục hồi ngập lụt tại TP.HCM:
- Rào 3 lớp bảo vệ nghiêm ngặt:
  1. Truy vấn 3 trục bắt buộc: [Địa danh TP.HCM] + [Ngập/Triều cường] + [Khẳng định phục hồi: đã rút/thông thoáng/bình thường].
  2. Bộ lọc loại trừ rác tuyệt đối: Chặn triệt để thể thao 'nước rút', công trình, bất động sản, ngoại tỉnh.
  3. Bộ lọc loại trừ cảm xúc tiêu cực: Chặn triệt để các câu 'chờ nước rút', 'đợi nước rút', 'tấp lên lề', 'chết máy'.
- Tự động gắn nhãn POS chuẩn mực và lưu bổ sung vào các phân vùng Episode tương ứng trong data/raw/episodes/.
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

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
EPISODES_DIR = os.path.join(DATA_DIR, "raw", "episodes")

from core.gazetteer import normalize_text, HOTSPOTS, OUT_OF_SCOPE_LOCATIONS
from pipeline.event_processor import clean_stream_text, contains_spam_or_noise
from scripts.organize_raw_episodes import determine_episode_id

# -----------------------------------------------------------------------------
# 1. RÀO CHẮN NGHIÊM NGẶT CÁC TÍN HIỆU TIÊU CỰC / ĐAU KHỔ / CHỜ ĐỢI
# -----------------------------------------------------------------------------
DISTRESS_NEGATIVE_CUES = [
    "chờ nước rút", "đợi nước rút", "đợi cho nước rút", "chờ cho nước rút",
    "đứng chờ nước", "ngồi chờ nước", "chờ mưa ngớt", "chờ mưa tạnh",
    "khi nào hết ngập", "bao giờ nước rút", "chưa rút", "chưa rút nước",
    "vẫn ngập", "ngập chưa rút", "rút chậm", "rút rất chậm", "không rút kịp",
    "ngập quá", "ngập sâu", "ngập nặng", "ngập lút bánh", "lút bánh", "nửa bánh",
    "chết máy", "tắt máy", "dắt bộ", "dắt xe", "dẫn bộ", "bì bõm",
    "tấp lên lề", "tấp vào lề", "lên lề", "ướt sũng", "không dám đi",
    "bất lực", "tràn vào nhà", "nước tràn", "nước cuốn", "biển nước", "mênh mông",
    "kẹt cứng", "tê liệt", "sóng đánh", "hên xui", "hỏi đã rút nước chưa",
    "trú mưa", "đứng chôn chân", "vất vả", "gian nan", "chật vật"
]

# -----------------------------------------------------------------------------
# 2. RÀO CHẮN NGHIÊM NGẶT RÁC THỂ THAO / CÔNG TRÌNH / PR / NGOẠI TỈNH
# -----------------------------------------------------------------------------
JUNK_OFFTOPIC_CUES = [
    "pha nước rút", "chạy nước rút", "giai đoạn nước rút", "nước rút thi công",
    "tay đua", "về đích", "cầu đi bộ", "nhựa duy tân", "duy tân", "cải tạo diện mạo",
    "deal hot", "ngập trời", "giải mật", "hồ sơ giải mật", "nhà sách", "khai trương",
    "độc quyền trên", "series tập", "cánh sóng âm", "khuyến mãi", "sale sập sàn",
    "mực tím", "truyện hạt lúa", "cia sài gòn", "bán nhà", "cho thuê", "phòng trọ",
    "căn hộ", "vinhomes", "bánh mì", "xe lướt", "odo", "thi hộ", "học hộ",
    "hà nội", "mcer", "marie curie", "đà lạt", "đà nẵng", "hải phòng", "thái nguyên"
]

# -----------------------------------------------------------------------------
# 3. TÍN HIỆU BẮT BUỘC KHẲNG ĐỊNH NƯỚC ĐÃ RÚT / ĐƯỜNG KHÔ / BÌNH THƯỜNG
# -----------------------------------------------------------------------------
AFFIRMATIVE_POS_CUES = [
    "nước đã rút", "nước đã rút hết", "nước rút hết", "nước rút hoàn toàn",
    "đã rút hẳn", "đã hết ngập", "hết ngập", "không còn ngập", "đường đã khô ráo",
    "đã khô ráo", "khô ráo hoàn toàn", "mặt đường khô ráo", "khô ráo sạch sẽ",
    "lưu thông bình thường", "di chuyển bình thường", "lưu thông thuận lợi",
    "giao thông ổn định trở lại", "đi lại dễ dàng", "thông thoáng trở lại",
    "mặt đường thông thoáng", "nước rút nhanh", "xe cộ qua lại bình thường"
]

# -----------------------------------------------------------------------------
# 4. DANH SÁCH TRUY VẤN 3 TRỤC BẮT BUỘC CHO NHÃN POS
# -----------------------------------------------------------------------------
POS_TARGETED_QUERIES = [
    # Nhóm Facebook Kênh Giao thông & Điểm nóng
    ('site:facebook.com "Trần Xuân Soạn" "triều cường" "đã rút"', "facebook"),
    ('site:facebook.com "Nguyễn Hữu Cảnh" "ngập" "đã rút hết"', "facebook"),
    ('site:facebook.com "Quốc Hương" "ngập" "lưu thông bình thường"', "facebook"),
    ('site:facebook.com "Thảo Điền" "ngập" "thông thoáng"', "facebook"),
    ('site:facebook.com "Ung Văn Khiêm" "ngập" "hết ngập"', "facebook"),
    ('site:facebook.com "Huỳnh Tấn Phát" "triều cường" "nước đã rút"', "facebook"),
    ('site:facebook.com "Lê Văn Lương" "triều cường" "đã rút hết"', "facebook"),
    ('site:facebook.com "Hầm chui An Phú" "hết ngập"', "facebook"),
    ('site:facebook.com "Phan Huy Ích" "ngập" "nước đã rút"', "facebook"),
    ('site:facebook.com "Nguyễn Văn Quá" "ngập" "đã rút hết"', "facebook"),
    ('site:facebook.com "Mễ Cốc" "triều cường" "nước đã rút"', "facebook"),
    ('site:facebook.com "Bến Bình Đông" "triều cường" "rút hết"', "facebook"),
    ('site:facebook.com "Tân Hòa Đông" "ngập" "lưu thông bình thường"', "facebook"),
    ('site:facebook.com "Kha Vạn Cân" "ngập" "đã hết ngập"', "facebook"),
    ('site:facebook.com "Võ Văn Ngân" "ngập" "thông thoáng"', "facebook"),
    ('site:facebook.com "VOV Giao thông" "triều cường" "nước đã rút"', "facebook"),
    ('site:facebook.com "VOV Giao thông" "ngập" "thông thoáng"', "facebook"),
    ('site:facebook.com "Giao thông TP.HCM" "ngập" "lưu thông bình thường"', "facebook"),
    ('site:facebook.com "Tôi là dân Quận 7" "triều cường" "đã rút"', "facebook"),
    ('site:facebook.com "Bình Thạnh" "ngập" "nước đã rút" "thông thoáng"', "facebook"),
    ('site:facebook.com "Thủ Đức" "ngập" "nước rút" "bình thường"', "facebook"),
    ('site:facebook.com "sau cơn mưa" "hết ngập" "Sài Gòn"', "facebook"),
    ('site:facebook.com "sau cơn mưa" "nước đã rút" "TPHCM"', "facebook"),
    ('site:facebook.com "triều cường" "lưu thông bình thường" "TPHCM"', "facebook"),

    # Nhóm TikTok
    ('site:tiktok.com "nước đã rút" "ngập" "TPHCM"', "tiktok"),
    ('site:tiktok.com "hết ngập" "thông thoáng" "Sài Gòn"', "tiktok"),
    ('site:tiktok.com "triều cường" "đã rút" "Sài Gòn"', "tiktok"),
    ('site:tiktok.com "sau cơn mưa" "hết ngập" "TPHCM"', "tiktok"),
    ('site:tiktok.com "Nguyễn Hữu Cảnh" "nước đã rút"', "tiktok"),
    ('site:tiktok.com "Trần Xuân Soạn" "nước đã rút"', "tiktok"),
    ('site:tiktok.com "Thảo Điền" "hết ngập"', "tiktok"),
    ('site:tiktok.com "Ung Văn Khiêm" "nước đã rút"', "tiktok"),
    ('site:tiktok.com "Huỳnh Tấn Phát" "triều cường" "rút"', "tiktok"),
    ('site:tiktok.com "nước rút hết" "giao thông bình thường" "TPHCM"', "tiktok")
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


def is_strictly_clean_pos_flood(text: str) -> bool:
    """Kiểm tra khắt khe: Bắt buộc là POS thật sự về ngập lụt TP.HCM, không lẫn rác."""
    if not text or len(text) < 15:
        return False
    clean = clean_stream_text(text)
    if not clean: return False
    t_low = clean.lower()

    # 1. Rào chắn tiêu cực / đau khổ (Nếu có thì loại ngay!)
    for cue in DISTRESS_NEGATIVE_CUES:
        if cue in t_low:
            return False

    # 2. Rào chắn rác thể thao / thi công / quảng cáo / ngoại tỉnh
    for junk in JUNK_OFFTOPIC_CUES:
        if junk in t_low:
            return False
    if contains_spam_or_noise(clean):
        return False

    # 3. Phải có từ khóa khẳng định nước đã rút / hết ngập / thông thoáng
    has_pos = any(cue in t_low for cue in AFFIRMATIVE_POS_CUES)
    if not has_pos:
        return False

    # 4. Phải có bối cảnh ngập lụt / triều cường / mưa
    has_flood_ctx = any(k in t_low for k in ["ngập", "triều cường", "mưa", "thoát nước", "nước ngập", "thủy triều"])
    if not has_flood_ctx:
        return False

    # 5. Phải có địa bàn TP.HCM hoặc điểm nóng TP.HCM
    has_hcmc = any(k in t_low for k in [
        "tphcm", "tp.hcm", "tp hcm", "sài gòn", "sai gon", "hồ chí minh",
        "quận 7", "thủ đức", "bình thạnh", "gò vấp", "nhà bè", "quận 8", "bình tân",
        "trần xuân soạn", "nguyễn hữu cảnh", "quốc hương", "thảo điền", "ung văn khiêm",
        "huỳnh tấn phát", "an phú", "nguyễn văn quá", "phan huy ích", "mễ cốc"
    ])
    if not has_hcmc:
        return False

    return True


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


def run_targeted_pos_crawler(max_per_query: int = 50):
    print("=" * 80)
    print("KHỞI ĐỘNG CÀO DỮ LIỆU CHUYÊN BIỆT NHÃN POSITIVE (POS) - RÀO 3 LỚP BẢO VỆ")
    print("=" * 80)

    seen_urls, seen_hashes = load_existing_identifiers()
    print(f"-> Đã nạp {len(seen_urls)} URLs và {len(seen_hashes)} content hashes hiện có để chống trùng lặp.")

    new_items_by_episode = defaultdict(lambda: defaultdict(list))
    total_found = 0
    total_added = 0
    rejected_distress = 0
    rejected_junk = 0
    rejected_duplicate = 0

    for q_idx, (query, platform) in enumerate(POS_TARGETED_QUERIES, start=1):
        print(f"\n[{q_idx}/{len(POS_TARGETED_QUERIES)}] Truy vấn POS: {query} ({platform.upper()})...")
        enc_q = urllib.parse.quote_plus(query)
        feed_url = f"https://news.google.com/rss/search?q={enc_q}&hl=vi&gl=VN&ceid=VN:vi"

        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"  Lỗi khi gọi RSS feed: {e}")
            continue

        entries = feed.entries[:max_per_query]
        print(f"  -> Nhận được {len(entries)} kết quả từ công cụ tìm kiếm.")

        for entry in entries:
            total_found += 1
            raw_title = getattr(entry, "title", "") or ""
            raw_summary = getattr(entry, "summary", "") or ""
            clean_title = re.sub(r'\s*-\s*(?:TikTok|Facebook)\s*$', '', raw_title, flags=re.IGNORECASE).strip()
            full_text = f"{clean_title}. {raw_summary}".strip()

            # 1. Kiểm tra rào chắn tiêu cực / đau khổ
            if any(cue in full_text.lower() for cue in DISTRESS_NEGATIVE_CUES):
                rejected_distress += 1
                continue

            # 2. Kiểm tra tính hợp lệ POS nghiêm ngặt
            if not is_strictly_clean_pos_flood(clean_title) and not is_strictly_clean_pos_flood(full_text):
                rejected_junk += 1
                continue

            # 3. Khử trùng lặp qua văn bản
            c_hash = hashlib.md5(clean_title.lower().encode("utf-8")).hexdigest()
            if c_hash in seen_hashes:
                rejected_duplicate += 1
                continue

            # 4. Giải mã URL
            rss_link = getattr(entry, "link", "")
            if not rss_link:
                continue

            try:
                decoded = gnewsdecoder(rss_link)
                decoded_url = decoded.get("decoded_url") if isinstance(decoded, dict) else decoded
            except Exception:
                decoded_url = ""

            if not decoded_url or not isinstance(decoded_url, str):
                continue

            if decoded_url in seen_urls:
                rejected_duplicate += 1
                continue

            if platform == "tiktok" and "tiktok.com" not in decoded_url.lower():
                continue
            if platform == "facebook" and "facebook.com" not in decoded_url.lower():
                continue

            seen_urls.add(decoded_url)
            seen_hashes.add(c_hash)

            # 5. Phân vùng Episode
            pub_date_raw = getattr(entry, "published", "")
            d_str, iso_str = parse_rfc822_date(pub_date_raw)
            if not d_str:
                d_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                iso_str = datetime.now(timezone.utc).isoformat()

            ep_id = determine_episode_id(d_str)
            author_name, post_id = extract_author_and_id(decoded_url, platform)

            raw_record = {
                "id": post_id,
                "url": decoded_url,
                "webVideoUrl": decoded_url if platform == "tiktok" else "",
                "mediaUrls": [decoded_url] if platform == "tiktok" else [],
                "text": clean_title,
                "title": clean_title,
                "author": author_name,
                "authorMeta": {"name": author_name},
                "createTimeISO": iso_str,
                "published": pub_date_raw,
                "extracted_date": d_str,
                "platform": platform,
                "crawled_at": datetime.now(timezone.utc).isoformat(),
                "crawler_source": "free_discovery_engine",
                "targeted_intent": "POS"
            }

            new_items_by_episode[ep_id][platform].append(raw_record)
            total_added += 1

        time.sleep(0.3)

    print("\n" + "=" * 80)
    print("HOÀN TẤT THU THẬP POS CHUYÊN BIỆT:")
    print(f"  * Tổng số ứng viên quét: {total_found}")
    print(f"  * Bị loại do chứa tín hiệu tiêu cực/đau khổ/chờ đợi: {rejected_distress}")
    print(f"  * Bị loại do rác thể thao/công trình/ngoại tỉnh/không đủ chuẩn POS: {rejected_junk}")
    print(f"  * Bị loại do trùng lặp: {rejected_duplicate}")
    print(f"  * SỐ BÀI POS CHUẨN XÁC 100% ĐƯỢC BỔ SUNG: {total_added}")
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
                uid = it.get("url") or it.get("id")
                if uid: merged_dict[uid] = it
            for it in items:
                uid = it.get("url") or it.get("id")
                if uid: merged_dict[uid] = it

            final_list = list(merged_dict.values())
            with open(target_path, "w", encoding="utf-8") as fp:
                json.dump(final_list, fp, ensure_ascii=False, indent=2)

            print(f"  + [{ep_id}] {platform.upper()}: Thêm {len(items)} bài POS -> Tổng: {len(final_list)} bài ({raw_fname})")

    print("\n-> Đã cập nhật toàn bộ bài POS vào các phân vùng Episode!")


if __name__ == "__main__":
    run_targeted_pos_crawler(max_per_query=50)
