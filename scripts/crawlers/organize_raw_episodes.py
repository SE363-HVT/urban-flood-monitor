# -*- coding: utf-8 -*-
"""
scripts/organize_raw_episodes.py
Phân loại dữ liệu thô (Raw Data) theo các đợt ngập lụt thực tế (Incident / Episode Partitioning).
Chuẩn bị cấu trúc phân vùng cho Data Lakehouse (PySpark Partitioning) và tài liệu nghiên cứu (Paper Case Studies).

Cấu trúc phân vùng:
- 5 Episodes lớn trong năm 2026 (Hình thái thời tiết rõ ràng, độ đồng thuận cao).
- Historical Archive: Dữ liệu lịch sử 2018 - 2025.
- Sporadic Flood Events: Các tin ngập cục bộ nhỏ lẻ ngoài các đợt lớn.
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, Any, List, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(ROOT_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
EPISODES_DIR = os.path.join(RAW_DIR, "episodes")
os.makedirs(EPISODES_DIR, exist_ok=True)

# Định nghĩa các đợt ngập trọng điểm TP.HCM
EPISODE_DEFINITIONS = [
    {
        "id": "episode_01_2026-09-10_mua-giong-dau-thang-9",
        "name": "Đợt mưa giông diện rộng đầu tháng 9/2026",
        "description": "Mưa giông cực đoan đầu tháng 9 gây ngập sâu các trục đường trũng thấp (Ung Văn Khiêm, Phan Huy Ích, Nguyễn Hữu Cảnh).",
        "start_date": "2026-09-08",
        "end_date": "2026-09-13",
        "weather_type": "Mưa giông cực đoan diện rộng",
        "key_hotspots": ["Ung Văn Khiêm", "Phan Huy Ích", "Nguyễn Hữu Cảnh", "Tân Kỳ Tân Quý"]
    },
    {
        "id": "episode_02_2026-09-17_anh-huong-bao-so-4",
        "name": "Đợt mưa lớn do ảnh hưởng bão số 4 & dải hội tụ nhiệt đới",
        "description": "Hoàn lưu bão số 4 kết hợp dải hội tụ nhiệt đới gây mưa dầm diện rộng kéo dài nhiều ngày trên toàn địa bàn TP.HCM.",
        "start_date": "2026-09-17",
        "end_date": "2026-09-24",
        "weather_type": "Bão số 4 & Dải hội tụ nhiệt đới",
        "key_hotspots": ["Phạm Thế Hiển", "Võ Văn Ngân", "Nguyễn Văn Quá", "Quốc Lộ 13"]
    },
    {
        "id": "episode_03_2026-09-27_trieu-cuong-dinh-diem-cuoi-thang-9",
        "name": "Đợt triều cường đỉnh điểm kết hợp mưa lớn cuối tháng 9/2026",
        "description": "Đợt triều cường cuối tháng 9 kết hợp mưa to làm ngập nặng các tuyến đường ven sông (Trần Xuân Soạn, Huỳnh Tấn Phát, Quốc Hương, Thảo Điền).",
        "start_date": "2026-09-27",
        "end_date": "2026-09-30",
        "weather_type": "Triều cường kết hợp mưa lớn (Đỉnh triều > 1.65m)",
        "key_hotspots": ["Trần Xuân Soạn", "Huỳnh Tấn Phát", "Quốc Hương", "Nguyễn Thị Thập"]
    },
    {
        "id": "episode_04_2026-10-01_trieu-cuong-ram-thang-tam",
        "name": "Đợt triều cường Rằm tháng 8 Âm lịch đầu tháng 10/2026",
        "description": "Triều cường đạt đỉnh 1.70m tại trạm Phú An và Nhà Bè, nước tràn bờ kè gây ngập nặng diện rộng tại Quận 7, Quận 8, Nhà Bè.",
        "start_date": "2026-10-01",
        "end_date": "2026-10-05",
        "weather_type": "Đỉnh triều cường kỳ Rằm tháng 8 Âm lịch (1.70m)",
        "key_hotspots": ["Bến Bình Đông", "Phú Định", "Mễ Cốc", "Hiệp Phước", "Lê Văn Lương"]
    },
    {
        "id": "episode_05_2026-10-07_mua-giong-chieu-toi-cuc-bo",
        "name": "Đợt mưa giông chiều tối ngập cục bộ tháng 10/2026",
        "description": "Mưa rào và giông mạnh chiều tối gây ngập cục bộ tại khu vực trung tâm Quận 1 (Takashimaya), Gò Vấp, Thủ Đức.",
        "start_date": "2026-10-07",
        "end_date": "2026-10-12",
        "weather_type": "Mưa giông đối lưu cục bộ chiều tối",
        "key_hotspots": ["Lê Lợi - Pasteur", "Takashimaya", "Cây Trâm", "Đặng Thị Rành"]
    }
]

def extract_item_date(item: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """Trích xuất ngày YYYY-MM-DD và chuỗi thời gian chuẩn ISO."""
    t = (
        item.get("createTime") or
        item.get("createTimeISO") or
        item.get("time") or
        item.get("timestamp") or
        item.get("published") or
        item.get("date")
    )
    if not t:
        return None, None

    if isinstance(t, (int, float)):
        try:
            dt = datetime.fromtimestamp(t, timezone.utc)
            return dt.strftime("%Y-%m-%d"), dt.isoformat()
        except Exception:
            return None, None

    s = str(t).strip()
    if len(s) >= 10 and s[:4].isdigit() and s[4] == "-" and s[7] == "-":
        return s[:10], s

    if "GMT" in s or "," in s:
        try:
            dt = datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%d"), dt.isoformat()
        except Exception:
            pass

    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d"), dt.isoformat()
    except Exception:
        pass

    return None, None


def determine_episode_id(date_or_ts: Any) -> str:
    """Xác định episode id dựa trên ngày đăng tải (chuỗi YYYY-MM-DD hoặc Unix Timestamp)."""
    if not date_or_ts:
        return "sporadic_flood_events"

    if isinstance(date_or_ts, (int, float)):
        try:
            date_str = datetime.fromtimestamp(date_or_ts, timezone.utc).strftime("%Y-%m-%d")
        except Exception:
            return "sporadic_flood_events"
    elif isinstance(date_or_ts, str):
        if "T" in date_or_ts:
            date_str = date_or_ts.split("T")[0]
        else:
            date_str = date_or_ts[:10]
    else:
        return "sporadic_flood_events"

    # 1. Kiểm tra 5 Episodes năm 2026
    for ep in EPISODE_DEFINITIONS:
        if ep["start_date"] <= date_str <= ep["end_date"]:
            return ep["id"]

    # 2. Kiểm tra dữ liệu lịch sử (trước năm 2026)
    if date_str < "2026-01-01":
        return "historical_archive"

    # 3. Các ngày rải rác năm 2026 ngoài 5 đợt lớn
    return "sporadic_flood_events"


def get_item_identity(item: Dict[str, Any], platform: str) -> Tuple[str, str]:
    """Tạo khóa định danh duy nhất (URL và Content Hash) để khử trùng lặp tuyệt đối."""
    url = (
        item.get("webVideoUrl") or
        item.get("url") or
        item.get("link") or
        item.get("postUrl") or
        ""
    )
    text = (
        item.get("text") or
        item.get("caption") or
        item.get("desc") or
        item.get("title") or
        ""
    ).strip()
    c_hash = hashlib.md5(text.lower().encode("utf-8")).hexdigest()
    item_id = str(item.get("id") or item.get("postId") or c_hash[:12])
    return url or f"{platform}_{item_id}", c_hash


def organize_episodes():
    print("=" * 80)
    print("BẮT ĐẦU PHÂN LOẠI DỮ LIỆU THÔ THEO CÁC ĐỢT NGẬP (EPISODE PARTITIONING)")
    print("=" * 80)

    # Cấu trúc lưu trữ dữ liệu theo từng episode và nền tảng
    # partitioned_data[episode_id][platform] = list[dict]
    partitioned_data = defaultdict(lambda: defaultdict(list))
    seen_urls = set()
    seen_hashes = set()

    # Danh sách các file thô cần duyệt
    raw_files_to_scan = []

    # File trong data/raw/
    for fname in os.listdir(RAW_DIR):
        if fname.endswith(".json") and fname != "pipeline_state.json":
            raw_files_to_scan.append((os.path.join(RAW_DIR, fname), fname))

    # File last_crawled trong data/
    for special in ["last_crawled_tiktok.json", "last_crawled_facebook.json"]:
        sp_path = os.path.join(DATA_DIR, special)
        if os.path.exists(sp_path):
            raw_files_to_scan.append((sp_path, special))

    total_scanned = 0
    total_accepted = 0

    for file_path, fname in raw_files_to_scan:
        # Xác định nền tảng gốc từ tên file
        platform = "unknown"
        if "tiktok" in fname.lower():
            platform = "tiktok"
        elif "facebook" in fname.lower():
            platform = "facebook"
        elif "news" in fname.lower():
            platform = "news"

        try:
            with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as fp:
                data = json.load(fp)
            if not isinstance(data, list):
                continue
        except Exception as e:
            print(f"Bỏ qua file {fname} do lỗi đọc JSON: {e}")
            continue

        print(f"-> Đang quét file [{fname}] ({len(data)} items, platform: {platform})...")

        for item in data:
            if not isinstance(item, dict):
                continue
            total_scanned += 1

            # Khử trùng lặp
            item_url, item_hash = get_item_identity(item, platform)
            if item_url in seen_urls or (item_hash and item_hash in seen_hashes):
                continue
            seen_urls.add(item_url)
            if item_hash:
                seen_hashes.add(item_hash)

            # Xác định ngày và episode
            d_str, iso_str = extract_item_date(item)
            ep_id = determine_episode_id(d_str)

            # Chuẩn hóa gắn thêm metadata thời gian nếu chưa có
            if d_str and not item.get("extracted_date"):
                item["extracted_date"] = d_str
            if iso_str and not item.get("extracted_iso"):
                item["extracted_iso"] = iso_str

            partitioned_data[ep_id][platform].append(item)
            total_accepted += 1

    print("\n" + "=" * 80)
    print(f"KẾT QUẢ KHỬ TRÙNG LẶP: Quét {total_scanned} items -> Giữ lại {total_accepted} items duy nhất.")
    print("=" * 80)

    # Ghi dữ liệu vào từng thư mục Episode
    all_ep_ids = [ep["id"] for ep in EPISODE_DEFINITIONS] + ["historical_archive", "sporadic_flood_events"]

    for ep_id in all_ep_ids:
        ep_dir = os.path.join(EPISODES_DIR, ep_id)
        os.makedirs(ep_dir, exist_ok=True)

        ep_platforms = partitioned_data[ep_id]
        total_ep_items = sum(len(items) for items in ep_platforms.values())

        # Ghi các file theo platform
        for plat, items in ep_platforms.items():
            if items:
                out_name = f"{plat}_raw.json"
                out_path = os.path.join(ep_dir, out_name)
                with open(out_path, "w", encoding="utf-8") as out_fp:
                    json.dump(items, out_fp, ensure_ascii=False, indent=2)

        # Tạo metadata.json cho Episode
        ep_meta = {
            "episode_id": ep_id,
            "total_items": total_ep_items,
            "breakdown": {plat: len(items) for plat, items in ep_platforms.items()},
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        # Tìm thông tin định nghĩa nếu có
        found_def = next((ep for ep in EPISODE_DEFINITIONS if ep["id"] == ep_id), None)
        if found_def:
            ep_meta.update(found_def)
        elif ep_id == "historical_archive":
            ep_meta["name"] = "Dữ liệu lịch sử đối sánh (2018 - 2025)"
            ep_meta["description"] = "Tập hợp các đợt triều cường và mưa ngập mùa lũ các năm trước để phục vụ benchmark."
        elif ep_id == "sporadic_flood_events":
            ep_meta["name"] = "Các sự kiện ngập lụt cục bộ rải rác (Sporadic Events)"
            ep_meta["description"] = "Các trận mưa rào cục bộ ngắn hạn gây ngập 1-2 tuyến đường riêng lẻ ngoài các đợt triều cường/bão lớn."

        meta_path = os.path.join(ep_dir, "metadata.json")
        with open(meta_path, "w", encoding="utf-8") as meta_fp:
            json.dump(ep_meta, meta_fp, ensure_ascii=False, indent=2)

        print(f"✅ [{ep_id}]: {total_ep_items:4d} items | Breakdown: {dict(ep_meta['breakdown'])}")

    print("\nHoàn tất phân loại toàn bộ dữ liệu thô vào thư mục data/raw/episodes/ thành công!")

if __name__ == "__main__":
    organize_episodes()
