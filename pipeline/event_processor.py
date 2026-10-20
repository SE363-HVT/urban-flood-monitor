"""
pipeline/event_processor.py - Xử lý Sự kiện Ngập Lụt Đô thị Chuẩn Hóa
Làm sạch văn bản, phát hiện biểu hiện ngập lụt, phân loại mức độ nghiêm trọng
và định dạng sự kiện chuẩn hóa cho toàn hệ thống.
"""

import re
import json
import unicodedata
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from core.gazetteer import match_hotspot, normalize_text

BDS_SPAM_KEYWORDS = [
  "bán nhà",
  "nhà bán",
  "cần bán",
  "bán gấp",
  "gấp bán",
  "chính chủ gửi",
  "chính chủ bán",
  "hạ giá bán",
  "cắt lỗ",
  "chủ kẹt tiền",
  "chủ cần tiền",
  "chốt gấp",
  "chủ ngộp",
  "ngộp thở",
  "giảm sâu",
  "giá mới chỉ",
  "còn tl",
  "thương lượng",
  "giá bán:",
  "giá chỉ",
  "tỷ tl",
  "tỉ tl",
  "t.ỷ",
  "tỷ t.l",
  "triệu/m2",
  "triệu/m²",
  "triệu/tháng",
  "chdv",
  "căn hộ dịch vụ",
  "tòa nhà",
  "nhà 2 mt",
  "nhà mt",
  "mặt tiền kinh doanh",
  "hẻm xe hơi",
  "hxh",
  "hxt",
  "hẻm thông",
  "sổ hồng",
  "sổ đỏ",
  "sổ riêng",
  "hoàn công",
  "pháp lý chuẩn",
  "công chứng ngay",
  "thổ cư",
  "đất nền",
  "biệt thự",
  "villa",
  "shophouse",
  "diện tích:",
  "dt:",
  "cn:",
  "kết cấu:",
  "ngang x dài",
  "kdc cao cấp",
  "cho thuê phòng",
  "phòng trọ",
  "tìm bạn ở ghép",
  "căn hộ for rent",
  "apartment",
  "môi giới",
  "hoa hồng",
  "liên hệ xem nhà",
  "zalo xem nhà",
  "pass phòng",
  "pass phòng",
  "nhượng phòng",
  "studio",
  "tách bếp",
  "ban công",
  "full nội thất",
  "xách vali",
  "máy giặt",
  "tủ lạnh",
  "nước nóng",
  "4k/kwh",
  "kwh",
  "điện:",
  "nước:",
  "hotline",
  "zalo",
  "cọc",
  "cho thuê",
  "ở ghép",
  "giá rẻ",
  "phòng trọ bình thạnh",
  "nhà trọ",
  "tiện ích:",
  "chi phí hàng tháng"
]

BDS_NEGATION_PHRASES = [
  "không ngập",
  "không bị ngập",
  "k ngập",
  "k bị ngập",
  "chưa bao giờ ngập",
  "cao ráo không ngập",
  "cam kết không ngập",
  "đoạn không ngập",
  "khu vực không ngập",
  "không lo ngập",
  "sạch sẽ không ngập",
  "đường cao không ngập",
  "vị trí cao không ngập"
]

ADS_METAPHOR_PATTERNS = [
  "ưu đãi ngập tràn",
  "ngập tràn ưu đãi",
  "ngập tràn niềm vui",
  "ngập tràn quà tặng",
  "quà tặng ngập tràn",
  "ngập tràn tiếng cười",
  "ngập tràn sắc hoa",
  "ngập tràn hạnh phúc",
  "ngập tràn sắc xuân",
  "deal ngập tràn",
  "sale ngập tràn",
  "ngập tràn voucher",
  "ngập tràn khuyến mãi",
  "ngập thịt",
  "ngập topping",
  "ngập phô mai",
  "sense city",
  "gigamall",
  "aeon mall",
  "tô tượng",
  "tranh cát",
  "đêm hội trung thu",
  "rước đèn",
  "trống hội",
  "minigame",
  "giveaway",
  "mua 1 tặng 1",
  "voucher giảm",
  "workshop",
  "khai trương rộn ràng",
  "ngập tràn ánh sáng",
  "ngập tràn niềm vui",
  "ngập tràn hạnh phúc",
  "ngập tràn tiếng cười",
  "ngập tràn yêu thương",
  "cửa sổ ngập tràn",
  "ban công siêu thoáng"
]

EDUCATION_SPAM_KEYWORDS = [
  "học từ vựng",
  "từ vựng tiếng anh",
  "trung tâm tiếng anh",
  "anh ngữ",
  "học tiếng anh",
  "thầy altaf",
  "khóa học",
  "lớp học",
  "tuyển sinh",
  "ielts",
  "toeic",
  "toefl",
  "gia sư",
  "du học",
  "học bổng",
  "trường học online",
  "buổi học",
  "học thử",
  "học viên",
  "giáo viên bản xứ",
  "trung tâm ngoại ngữ",
  "tiếng anh giao tiếp",
  "luyện thi",
  "đăng ký khóa học",
  "bài giảng",
  "giáo trình",
  "tieng anh",
  "english"
]

REPAIR_SHOP_KEYWORDS = [
  "tiệm sửa xe",
  "sửa xe",
  "sửa chữa xe",
  "thợ sửa xe",
  "chuyên sửa xe",
  "dịch vụ sửa xe",
  "sửa xe máy",
  "sửa xe lưu động",
  "vá xe lưu động",
  "vá xe",
  "vá vỏ",
  "thay ruột xe",
  "thay bugi",
  "cứu hộ sửa xe",
  "tiệm rửa xe",
  "rửa xe",
  "chăm sóc xe",
  "thay nhớt",
  "gara sửa xe",
  "garage sửa xe",
  "sửa khóa",
  "dịch vụ sửa chữa"
]

SPORTS_AND_LEISURE_KEYWORDS = [
  "sân cầu lông",
  "sân the b",
  "sân bóng",
  "kèo cầu lông",
  "đánh cầu",
  "vợt cầu lông",
  "trình độ: tby-tb",
  "trình độ:",
  "yếu+",
  "sẵn nữ",
  "tuyển mem",
  "vãng lai",
  "tìm bạn chơi",
  "giao lưu thể thao",
  "pickleball",
  "bida club"
]

PROJECT_AND_MACRO_KEYWORDS = [
  "phương án thiết kế cho dự án quỹ đất",
  "dự án quỹ đất",
  "nghiên cứu dự án hơn",
  "dự án hơn 10.000 tỉ",
  "chuẩn bị mở rộng đường",
  "giải phóng mặt bằng",
  "chuyên gia hiến kế chống ngập",
  "solutions for urban flood",
  "chi hơn 142.340 tỷ",
  "mệnh lệnh",
  "mệnh lệnh không được thay đổi",
  "bộ đội cụ hồ",
  "thủ tướng",
  "thủ tướng chính phủ",
  "phó thủ tướng",
  "chính trị",
  "tin nội chính",
  "ctvn",
  "chinhtrivietnam",
  "tinnoichinh",
  "duanchongngaptphcm",
  "thutuongleminhhung",
  "kênh tham lương",
  "hồ điều tiết ngầm",
  "vì sao phải sống chung",
  "dự án chống ngập",
  "công trình về đích",
  "bàn giao",
  "6,5 triệu người dân"
]

NOISE_KEYWORDS = [
  "bangkok",
  "thái lan",
  "thailand",
  "australia",
  "vaycuoi",
  "cinnamon",
  "nutella",
  "cookie",
  "toán 4",
  "ronaldo",
  "asiancup"
]

FOREIGN_NOISE_WORDS = [
  "harga",
  "spesifikasi",
  "absen",
  "ngapake",
  "rika",
  "izle",
  "leyla",
  "cheesecake",
  "tarifi",
  "resep",
  "recipe",
  "baking",
  "ano pa",
  "inaantay",
  "fırında",
  "yaşanacaksa",
  "ayrılıklarr",
  "kesfet",
  "malzemeler"
]

HIGH_SEVERITY_KEYWORDS = [
  "ngập sâu",
  "lút bánh",
  "ngập lút",
  "chết máy",
  "tràn vào nhà",
  "ngập tràn vào nhà",
  "cuốn trôi",
  "tê liệt",
  "nước xiết",
  "chảy xiết",
  "ngập nửa xe",
  "bơi thuyền",
  "thất thủ",
  "thành sông",
  "hóa sông",
  "như sông",
  "biển nước",
  "trong biển nước",
  "thành biển",
  "chìm trong biển",
  "chèo xuồng",
  "bơi xuồng",
  "lênh láng nước",
  "mênh mông nước",
  "ngập tới háng",
  "ngập tới bụng",
  "ngập nửa người",
  "ngập lút đầu",
  "chết máy hàng loạt",
  "dắt bộ xe",
  "xe chết máy",
  "cháy bugi",
  "nước vào pô",
  "nước vô bô",
  "ngập nửa mét",
  "ngập 1 mét",
  "ngập tới đầu gối",
  "ngập đến đầu gối",
  "ngập tới gối",
  "nước ngập tới gối",
  "ngập hơn nửa bánh xe",
  "ngập lút máy",
  "sóng đánh té xe",
  "sóng nước đánh mạnh"
]

MEDIUM_SEVERITY_KEYWORDS = [
  "ngập úng",
  "ngập nặng",
  "ngập đường",
  "ngập nước",
  "nước ngập",
  "mưa ngập",
  "ngập lụt",
  "triều cường dâng",
  "triều cường ngập",
  "nước tràn",
  "bì bõm",
  "lội nước",
  "dắt bộ",
  "nước dâng cao",
  "ngập nhẹ",
  "rút chậm",
  "đọng nước",
  "khó đi lại do ngập",
  "ngập bánh xe",
  "ngập xe",
  "xe ngập",
  "nước dâng ngập",
  "ngập lối đi",
  "ngập nửa bánh xe",
  "nửa bánh xe",
  "ngập bánh",
  "đường ngập",
  "nước tràn qua đường"
]

VIETNAMESE_DIACRITICS = set(["ó", "ư", "ữ", "ê", "ứ", "ế", "ự", "é", "ớ", "ồ", "ũ", "ỉ", "ĩ", "ằ", "ọ", "ử", "ổ", "ể", "ắ", "ẵ", "ẫ", "ủ", "ụ", "í", "ầ", "ỏ", "ỷ", "ờ", "ô", "ỵ", "ú", "ộ", "ở", "â", "ỡ", "ạ", "ề", "đ", "ẳ", "á", "ệ", "õ", "ả", "à", "ò", "ố", "ặ", "ù", "ợ", "ẻ", "ẩ", "ý", "ỳ", "ã", "è", "ă", "ấ", "ỗ", "ậ", "ễ", "ì", "ỹ", "ị", "ẽ", "ừ", "ơ", "ẹ"])

def is_valid_vietnamese_content(text: str) -> bool:
    text_lower = text.lower()
    if any(fw in text_lower for fw in FOREIGN_NOISE_WORDS):
        return False
    return any(ch in VIETNAMESE_DIACRITICS for ch in text_lower)


def contains_spam_or_noise(text: str) -> bool:
    text_lower = text.lower()
    if any(k in text_lower for k in BDS_SPAM_KEYWORDS):
        return True
    if any(k in text_lower for k in BDS_NEGATION_PHRASES):
        return True
    if any(k in text_lower for k in ADS_METAPHOR_PATTERNS):
        return True
    if any(k in text_lower for k in EDUCATION_SPAM_KEYWORDS):
        return True
    if any(k in text_lower for k in REPAIR_SHOP_KEYWORDS):
        return True
    if any(k in text_lower for k in SPORTS_AND_LEISURE_KEYWORDS):
        return True
    if any(k in text_lower for k in PROJECT_AND_MACRO_KEYWORDS):
        return True
    if any(k in text_lower for k in NOISE_KEYWORDS):
        return True
    return False


def clean_stream_text(raw_text: str) -> Optional[str]:
    """Làm sạch văn bản đầu vào và loại bỏ mọi nguồn tin rác / BĐS."""
    if not raw_text:
        return None
    text = unicodedata.normalize('NFC', raw_text).strip()
    if len(text) < 12:
        return None
    if not is_valid_vietnamese_content(text):
        return None
    if contains_spam_or_noise(text):
        return None
    text = re.sub(r'\s+', ' ', text)
    return text


def analyze_severity_heuristic(text: str) -> Optional[Dict[str, Any]]:
    """
    Phân tích mức độ nghiêm trọng và trích xuất thực thể biểu hiện ngập lụt.
    QUAN TRỌNG: Nếu văn bản KHÔNG chứa bất kỳ từ khóa ngập lụt thực tế nào,
    hàm sẽ trả về None (TUYỆT ĐỐI KHÔNG mặc định gán 'có ngập nước').
    """
    clean_text = normalize_text(text)

    for kw in HIGH_SEVERITY_KEYWORDS:
        if kw in clean_text:
            return {
                "opinion": kw,
                "sentiment": "negative",
                "severity_level": "high",
                "weight": 3.0
            }

    for kw in MEDIUM_SEVERITY_KEYWORDS:
        if kw in clean_text:
            return {
                "opinion": kw,
                "sentiment": "negative",
                "severity_level": "medium",
                "weight": 2.0
            }

    has_rain = any(rk in clean_text for rk in ("mưa lớn", "mưa to", "mưa giông", "triều cường", "mưa kéo dài"))
    has_flood = "ngập" in clean_text

    if has_flood:
        return {
            "opinion": "mưa ngập",
            "sentiment": "negative",
            "severity_level": "low",
            "weight": 1.2
        }

    return None


def format_relative_time(create_timestamp: Optional[int], reference_timestamp: Optional[int] = None) -> str:
    """Định dạng thời gian tương đối."""
    if not create_timestamp:
        return "Gần đây"
    ref = reference_timestamp or int(datetime.now().timestamp())
    diff_sec = max(0, ref - create_timestamp)
    if diff_sec < 60:
        return "vừa xong"
    elif diff_sec < 3600:
        return f"{diff_sec // 60} phút trước"
    elif diff_sec < 86400:
        h = diff_sec // 3600
        m = (diff_sec % 3600) // 60
        return f"{h} giờ {m} phút trước" if m > 0 else f"{h} giờ trước"
    else:
        return f"{diff_sec // 86400} ngày trước"


def process_tiktok_item(item: Dict[str, Any], reference_time: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Chuẩn hóa bài đăng TikTok, lọc spam và kiểm tra ngập lụt nghiêm ngặt."""
    raw_text = item.get("text", "") or item.get("desc", "") or item.get("title", "")

    cleaned_text = clean_stream_text(raw_text)
    if not cleaned_text:
        return None

    # BẮT BUỘC: Phải có biểu hiện ngập lụt thực tế
    analysis = analyze_severity_heuristic(cleaned_text)
    if not analysis:
        return None

    hotspot = match_hotspot(cleaned_text)
    if not hotspot:
        return None

    create_time = item.get("createTime") or item.get("create_time", 0)
    author_info = item.get("authorMeta", {})
    author_name = author_info.get("name") or author_info.get("nickName") or item.get("author", "Người dùng TikTok")

    video_url = item.get("webVideoUrl", "")
    if not video_url:
        video_url = f"https://www.tiktok.com/@{author_name}/video/{item.get('id')}"

    event = {
        "id": str(item.get("id")),
        "platform": item.get("platform", "tiktok"),
        "media_type": "video",
        "author": author_name,
        "text": cleaned_text,
        "create_time": create_time,
        "created_at_iso": item.get("createTimeISO") or (datetime.fromtimestamp(create_time, timezone.utc).isoformat() if create_time else ""),
        "relative_time": format_relative_time(create_time, reference_time),
        "location": {
            "street": hotspot.get("street") or (hotspot["display_name"] if hotspot.get("priority", 3) >= 3 else ""),
            "display_name": hotspot.get("display_name", ""),
            "ward": hotspot["ward"],
            "administrative_unit": hotspot.get("ward", ""),
            "district": hotspot.get("district", ""),
            "region": hotspot.get("region", "TPHCM"),
            "lat": hotspot["lat"],
            "lon": hotspot["lon"],
            "heat_points": hotspot.get("heat_points", [[hotspot["lat"], hotspot["lon"]]]),
            "priority": hotspot.get("priority", 3),
            "type": hotspot["type"],
            "cause": hotspot.get("cause", "rain"),
            "cause_label": hotspot.get("cause_label", "Mưa lớn, nước không thoát kịp"),
            "source": hotspot.get("source", "seed")
        },
        "aspect": hotspot["display_name"],
        "opinion": analysis["opinion"],
        "sentiment": analysis["sentiment"],
        "severity": analysis["severity_level"],
        "weight": analysis["weight"],
        "url": video_url
    }

    return event
