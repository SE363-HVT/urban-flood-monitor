# -*- coding: utf-8 -*-
"""
scripts/augment_cda_pos.py
Triển khai phương pháp Nghịch đảo ngữ nghĩa có kiểm soát (Controlled Counterfactual Data Augmentation - CDA)
để tăng cường các mẫu POS chuẩn tắc cho tập dữ liệu ASTE v3, đạt mốc tỷ lệ ~15% POS phục vụ bài báo ICWSM 2027.

Nguyên tắc vàng:
1. 100% Verbatim Substring: Aspect và Opinion phải xuất hiện y nguyên từng ký tự trong văn bản câu.
2. 100% Thực thể thật tại TP.HCM theo NQ 1685 (0% rò rỉ cấp Quận).
3. Đánh dấu rõ metadata:
   - "is_counterfactual_augmented": True
   - "data_split_recommendation": "TRAIN_ONLY" (Đảm bảo tính liêm chính NCKH: chỉ train, không đưa vào test)
   - "crawl_batch": "batch_3_cda_augmented"
   - "polarity": "POS", "severity": "RECOVERED"
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import json
import random
from datetime import datetime, timezone

V3_PATH = "D:/SE363_RAWDATA/data/processed/hcmc_flood_annotated_v3_multimodal.json"

# Danh sách thực thể địa lý thật tại TP.HCM (Chuẩn NQ 1685, 0% Quận)
REAL_STREETS = [
    ("Trần Xuân Soạn", "csgt_tide_01", "Phường Tân Thuận"),
    ("Huỳnh Tấn Phát", "csgt_tide_02", "Phường Phú Thuận"),
    ("Phan Huy Ích", "csgt_rain_01", "Phường An Hội Tây"),
    ("Nguyễn Văn Khối", "csgt_rain_02", "Phường Thông Tây Hội"),
    ("Lê Đức Thọ", "csgt_rain_03", "Phường An Hội Đông"),
    ("Quốc lộ 13", "csgt_tide_03", "Phường Hiệp Bình"),
    ("Tô Ngọc Vân", "csgt_rain_04", "Phường Tam Bình"),
    ("Võ Văn Ngân", "csgt_rain_05", "Phường Linh Chiểu"),
    ("Kha Vạn Cân", "csgt_rain_06", "Phường Linh Đông"),
    ("Đặng Thị Rành", "csgt_rain_07", "Phường Linh Tây"),
    ("Ung Văn Khiêm", "csgt_tide_04", "Phường Thạnh Mỹ Tây"),
    ("Nguyễn Hữu Cảnh", "csgt_tide_05", "Phường Thạnh Mỹ Tây"),
    ("Bình Quới", "csgt_tide_06", "Phường Bình Quới"),
    ("Lương Định Của", "csgt_tide_07", "Phường An Khánh"),
    ("Thảo Điền", "csgt_tide_08", "Phường Thảo Điền"),
    ("Quốc Hương", "csgt_tide_09", "Phường Thảo Điền"),
    ("Nguyễn Văn Hưởng", "csgt_tide_10", "Phường Thảo Điền"),
    ("Hồ Học Lãm", "csgt_tide_11", "Phường An Lạc"),
    ("An Dương Vương", "csgt_tide_12", "Phường An Lạc"),
    ("Kinh Dương Vương", "csgt_rain_08", "Phường An Lạc"),
    ("Lê Văn Lương", "csgt_tide_13", "Phường Tân Phong"),
    ("Đào Trí", "csgt_tide_14", "Phường Phú Thuận"),
    ("Phạm Thế Hiển", "csgt_tide_15", "Phường Chánh Hưng"),
    ("Nguyễn Duy", "csgt_tide_16", "Phường Chánh Hưng"),
    ("Mễ Cốc", "csgt_tide_17", "Phường Phú Định"),
    ("Bến Phú Định", "csgt_tide_18", "Phường Phú Định"),
    ("Đỗ Xuân Hợp", "csgt_rain_09", "Phường Phước Long"),
    ("Dương Văn Cam", "csgt_rain_10", "Phường Linh Tây"),
    ("Nguyễn Xí", "csgt_tide_19", "Phường Bình Thạnh"),
    ("Bạch Đằng", "csgt_rain_11", "Phường Gia Định"),
    ("Đinh Bộ Lĩnh", "csgt_tide_20", "Phường Bình Hòa"),
    ("Phạm Văn Đồng", "csgt_rain_12", "Phường Hiệp Bình"),
    ("Cây Trâm", "csgt_rain_13", "Phường Thông Tây Hội"),
    ("Lê Văn Việt", "csgt_rain_14", "Phường Tăng Nhơn Phú"),
    ("Hoàng Diệu", "csgt_tide_21", "Phường Vĩnh Hội"),
    ("Đoàn Văn Bơ", "csgt_tide_22", "Phường Xóm Chiếu"),
    ("Calmette", "csgt_tide_23", "Phường Cầu Ông Lãnh"),
    ("Trần Hưng Đạo", "csgt_rain_15", "Phường Chợ Quán"),
    ("Nguyễn Biểu", "csgt_tide_24", "Phường Chợ Quán")
]

REAL_INFRASTRUCTURE = [
    ("cống ngăn triều Mương Chuối", "INFRASTRUCTURE_DRAINAGE", "Phường Nhà Bè"),
    ("cống ngăn triều Phú Xuân", "INFRASTRUCTURE_DRAINAGE", "Phường Phú Xuân"),
    ("cống ngăn triều Tân Thuận", "INFRASTRUCTURE_DRAINAGE", "Phường Tân Thuận"),
    ("cống ngăn triều Bến Nghé", "INFRASTRUCTURE_DRAINAGE", "Phường Bến Nghé"),
    ("cống ngăn triều Phú Định", "INFRASTRUCTURE_DRAINAGE", "Phường Phú Định"),
    ("trạm bơm Bình Lợi", "INFRASTRUCTURE_DRAINAGE", "Phường Bình Lợi Trung"),
    ("trạm bơm Nguyễn Hữu Cảnh", "INFRASTRUCTURE_DRAINAGE", "Phường Thạnh Mỹ Tây"),
    ("trạm bơm Nhiêu Lộc", "INFRASTRUCTURE_DRAINAGE", "Phường Nhiêu Lộc"),
    ("hệ thống cống thoát nước", "INFRASTRUCTURE_DRAINAGE", "TP. Hồ Chí Minh"),
    ("máy bơm công suất lớn", "INFRASTRUCTURE_DRAINAGE", "TP. Hồ Chí Minh"),
    ("dự án chống ngập", "INFRASTRUCTURE_DRAINAGE", "TP. Hồ Chí Minh"),
    ("bờ kè kênh", "INFRASTRUCTURE_DRAINAGE", "TP. Hồ Chí Minh")
]

REAL_HYDROLOGY = [
    ("triều cường", "HYDROLOGY", "TP. Hồ Chí Minh"),
    ("sông Sài Gòn", "HYDROLOGY", "TP. Hồ Chí Minh"),
    ("sông Đồng Nai", "HYDROLOGY", "TP. Hồ Chí Minh"),
    ("Kênh Nhiêu Lộc", "HYDROLOGY", "TP. Hồ Chí Minh"),
    ("kênh Tàu Hủ", "HYDROLOGY", "TP. Hồ Chí Minh"),
    ("kênh Tẻ", "HYDROLOGY", "TP. Hồ Chí Minh"),
    ("kênh Đôi", "HYDROLOGY", "TP. Hồ Chí Minh"),
    ("rạch Xuyên Tâm", "HYDROLOGY", "Phường Bình Thạnh"),
    ("trạm Phú An", "HYDROLOGY", "Phường Thạnh Mỹ Tây"),
    ("trạm Nhà Bè", "HYDROLOGY", "Phường Nhà Bè")
]

REAL_RESPONSE = [
    ("CSGT", "RESPONSE_ENTITY", "TP. Hồ Chí Minh"),
    ("lực lượng chức năng", "RESPONSE_ENTITY", "TP. Hồ Chí Minh"),
    ("công nhân thoát nước", "RESPONSE_ENTITY", "TP. Hồ Chí Minh"),
    ("đội cứu hộ", "RESPONSE_ENTITY", "TP. Hồ Chí Minh"),
    ("đội xung kích", "RESPONSE_ENTITY", "TP. Hồ Chí Minh"),
    ("chính quyền địa phương", "RESPONSE_ENTITY", "TP. Hồ Chí Minh")
]

# Các mẫu câu nghịch đảo (CDA Templates) đảm bảo tự nhiên, đa dạng ngữ cảnh
STREET_TEMPLATES = [
    ("Hiện tại tuyến {asp} {op}, các phương tiện đã có thể di chuyển thuận tiện.",
     ["nước đã rút hoàn toàn", "nước đã rút sạch", "mặt đường khô ráo", "thông thoáng trở lại", "hết ngập hẳn"]),
    ("Sau cơn mưa chiều, đường {asp} {op}, giao thông qua khu vực ổn định bình thường.",
     ["nước rút nhanh chóng", "nước đã rút", "khô ráo hoàn toàn", "không còn ngập nước", "lưu thông bình thường"]),
    ("Ghi nhận tại {asp} đến thời điểm này {op}, người dân đi lại dễ dàng không còn cảnh bì bõm.",
     ["nước rút sạch", "khô queo", "thông xe", "không bị ngập", "đã khô ráo"]),
    ("Đoạn đường {asp} sau khi triều cường hạ {op}, cuộc sống sinh hoạt của bà con đã ổn định trở lại.",
     ["nước đã rút sạch sẽ", "mặt đường thông thoáng", "nước rút hết", "khô ráo sạch sẽ", "thông suốt"]),
    ("Cập nhật giao thông {asp} hiện {op}, không còn tình trạng xe chết máy.",
     ["hết ngập", "khô ráo", "thông thoáng", "nước đã rút", "đi lại bình thường"]),
    ("Tuyến đường {asp} hôm nay {op}, các phương tiện di chuyển nhanh chóng.",
     ["không ngập", "khô ráo", "không còn ngập nữa", "nước rút sạch", "lưu thông thuận lợi"]),
    ("Bà con lưu thông qua {asp} an tâm nhé, khu vực này {op} rồi.",
     ["nước đã rút", "khô rang", "hết ngập hẳn", "đã khô ráo", "thông xe"]),
    ("Đường {asp} chiều tối nay {op}, người dân phấn khởi tan làm về nhà thuận tiện.",
     ["nước rút rất nhanh", "mặt đường khô ráo", "thông thoáng trở lại", "nước đã rút hoàn toàn", "lưu thông bình thường"]),
    ("Giao thông trục {asp} cơ bản {op}, không còn điểm nghẽn do nước tù đọng.",
     ["ổn định trở lại", "thông thoáng", "khô ráo", "hết ngập", "nước rút sạch"]),
    ("Nhờ thoát nước nhanh, mặt đường {asp} {op}, các cửa hàng bắt đầu mở cửa đón khách.",
     ["đã khô ráo", "khô ráo sạch sẽ", "nước đã rút hết", "ráo hoảnh", "thông thoáng"]),
    ("Thông tin khẩn: Điểm ngập {asp} {op}, các loại xe máy và ô tô lưu thông bình an.",
     ["nước đã rút sạch", "hết ngập hoàn toàn", "mặt đường thông thoáng", "thông suốt", "khô ráo"]),
    ("Sau khi mở van xả triều, khu vực {asp} {op}, người dân không còn phải bì bõm lội nước.",
     ["nước rút nhanh", "nước đã rút", "mặt đường khô ráo", "hết ngập hẳn", "khô queo"])
]

INFRA_TEMPLATES = [
    ("Khu vực này nhờ {asp} {op} nên đường phố không bị ngập úng sau mưa lớn.",
     ["vận hành hiệu quả", "hoạt động rất hiệu quả", "thoát nước rất nhanh", "thoát nước rất tốt", "phát huy hiệu quả"]),
    ("Hôm nay {asp} {op}, giúp mực nước trên tuyến đường hạ nhanh chóng.",
     ["hoạt động hết công suất", "vận hành liên tục", "thoát nước nhanh", "chống ngập tốt", "phát huy hiệu quả"]),
    ("Người dân đánh giá cao {asp} vì {op}, triều cường dâng cao nhưng không tràn vào nhà.",
     ["ngăn triều hiệu quả", "chống ngập hiệu quả", "hoạt động rất tốt", "phát huy hiệu quả", "thoát nước rất nhanh"]),
    ("Nhờ dự án nâng cấp, {asp} {op}, giảm thiểu tối đa tình trạng ngập cục bộ tại địa bàn.",
     ["phát huy hiệu quả", "thoát nước rất tốt", "hoạt động hiệu quả", "vận hành trơn tru"])
]

HYDRO_TEMPLATES = [
    ("Tại khu vực sông nước, ghi nhận {asp} {op}, triều đã qua đỉnh và dòng chảy hạ nhiệt.",
     ["rút dần", "bắt đầu rút", "nước rút dần", "xuống thấp"]),
    ("Mực nước tại {asp} chiều nay {op}, không gây áp lực ngập lên các tuyến đê bao lân cận.",
     ["đã hạ nhiệt", "giảm nhanh", "rút nhanh", "ở mức an toàn"]),
    ("Theo trạm quan trắc, {asp} {op}, dòng chảy thuận lợi không làm nước tràn vào khu dân cư.",
     ["rút dần", "hạ nhanh", "ở mức an toàn", "giảm nhanh"])
]

RESPONSE_TEMPLATES = [
    ("Trên đường ngập nước, các chiến sĩ {asp} {op}, hỗ trợ người dân an toàn qua vùng nước sâu.",
     ["kịp thời đẩy xe giúp dân", "kịp thời hỗ trợ", "ứng trực kịp thời", "giúp người dân vượt qua điểm ngập"]),
    ("Hình ảnh đẹp: lực lượng {asp} {op}, giúp phương tiện chết máy lưu thông an toàn.",
     ["nhiệt tình giúp đỡ người dân", "kịp thời hỗ trợ", "ứng trực kịp thời", "giúp người dân vượt qua điểm ngập"]),
    ("Được sự hướng dẫn của {asp} {op}, các phương tiện đã tránh được điểm ngập sâu và về nhà an toàn.",
     ["kịp thời hỗ trợ", "ứng trực kịp thời", "tận tình điều tiết giao thông"])
]


def generate_cda_samples(target_count=890):
    samples = []
    seen_texts = set()

    # 1. Mẫu đường phố (~70% = 620 mẫu)
    street_target = int(target_count * 0.70)
    attempts = 0
    while len(samples) < street_target and attempts < 10000:
        attempts += 1
        st_name, gid, ward = random.choice(REAL_STREETS)
        tpl, op_list = random.choice(STREET_TEMPLATES)
        op_choice = random.choice(op_list)

        text = tpl.format(asp=st_name, op=op_choice)
        if text in seen_texts: continue
        seen_texts.add(text)

        samples.append({
            "aspect": st_name,
            "opinion": op_choice,
            "aspect_category": "LOCATION_STREET",
            "gazetteer_id": gid,
            "ward": ward,
            "text": text,
            "severity": "RECOVERED"
        })

    # 2. Mẫu công trình hạ tầng (~15% = 135 mẫu)
    infra_target = len(samples) + int(target_count * 0.15)
    attempts = 0
    while len(samples) < infra_target and attempts < 10000:
        attempts += 1
        infra_name, cat, ward = random.choice(REAL_INFRASTRUCTURE)
        tpl, op_list = random.choice(INFRA_TEMPLATES)
        op_choice = random.choice(op_list)

        text = tpl.format(asp=infra_name, op=op_choice)
        if text in seen_texts: continue
        seen_texts.add(text)

        samples.append({
            "aspect": infra_name,
            "opinion": op_choice,
            "aspect_category": cat,
            "gazetteer_id": None,
            "ward": ward,
            "text": text,
            "severity": "RECOVERED"
        })

    # 3. Mẫu thủy văn hạ triều (~8% = 75 mẫu)
    hydro_target = len(samples) + int(target_count * 0.08)
    attempts = 0
    while len(samples) < hydro_target and attempts < 10000:
        attempts += 1
        hydro_name, cat, ward = random.choice(REAL_HYDROLOGY)
        tpl, op_list = random.choice(HYDRO_TEMPLATES)
        op_choice = random.choice(op_list)

        text = tpl.format(asp=hydro_name, op=op_choice)
        if text in seen_texts: continue
        seen_texts.add(text)

        samples.append({
            "aspect": hydro_name,
            "opinion": op_choice,
            "aspect_category": cat,
            "gazetteer_id": None,
            "ward": ward,
            "text": text,
            "severity": "RECOVERED"
        })

    # 4. Mẫu lực lượng hỗ trợ (~7% = 60 mẫu)
    attempts = 0
    while len(samples) < target_count and attempts < 10000:
        attempts += 1
        resp_name, cat, ward = random.choice(REAL_RESPONSE)
        tpl, op_list = random.choice(RESPONSE_TEMPLATES)
        op_choice = random.choice(op_list)

        text = tpl.format(asp=resp_name, op=op_choice)
        if text in seen_texts: continue
        seen_texts.add(text)

        samples.append({
            "aspect": resp_name,
            "opinion": op_choice,
            "aspect_category": cat,
            "gazetteer_id": None,
            "ward": ward,
            "text": text,
            "severity": "LOW"
        })

    return samples


def main():
    print("=" * 80)
    print("🚀 BẮT ĐẦU TẠO DỮ LIỆU NGHỊCH ĐẢO NGỮ NGHĨA CÓ KIỂM SOÁT (CDA TARGET ~15% POS)")
    print("=" * 80)

    if not os.path.exists(V3_PATH):
        print(f"❌ Không tìm thấy file: {V3_PATH}")
        return

    with open(V3_PATH, "r", encoding="utf-8") as f:
        v3_items = json.load(f)

    # Lấy các mẫu gốc thực tế thuần túy (không tính CDA cũ)
    real_items = [x for x in v3_items if not x.get("is_counterfactual_augmented")]
    print(f"[*] Số câu gốc thuần thực địa ngoài đời: {len(real_items)}")

    # Tính toán chính xác số mẫu CDA cần thiết để đạt ~15.0% POS:
    # Hiện có 171 POS thực địa, 5020 NEG, 991 NEU (Tổng non-POS = 6011).
    # Để POS đạt 15%: (171 + N) / (6011 + 171 + N) = 0.15 => N = 890.
    TARGET_CDA_COUNT = 890
    cda_data = generate_cda_samples(target_count=TARGET_CDA_COUNT)
    print(f"[*] Đã sinh thành công {len(cda_data)} mẫu POS nghịch đảo ngữ nghĩa độc bản không trùng lặp.")

    new_items = list(real_items)
    base_idx = len(new_items) + 1

    for i, s in enumerate(cda_data, start=base_idx):
        text = s["text"]
        asp = s["aspect"]
        op = s["opinion"]

        assert asp in text, f"Lỗi verbatim aspect: '{asp}' not in '{text}'"
        assert op in text, f"Lỗi verbatim opinion: '{op}' not in '{text}'"

        item_id = f"cda_pos_{i:05d}"
        pub_time = datetime.now(timezone.utc).isoformat()

        triplet = {
            "aspect": asp,
            "opinion": op,
            "polarity": "POS",
            "aspect_category": s["aspect_category"],
            "gazetteer_id": s["gazetteer_id"],
            "grounding_provenance": "SPAN_MATCHED",
            "severity": s["severity"]
        }

        entry = {
            "id": item_id,
            "parent_id": f"cda_root_{i:05d}",
            "episode_id": "cda_augmented_recovery",
            "episode_title": "Dữ liệu nghịch đảo ngữ nghĩa phục hồi (CDA Train Split)",
            "crawl_batch": "batch_3_cda_augmented",
            "is_new_crawl": False,
            "is_counterfactual_augmented": True,
            "data_split_recommendation": "TRAIN_ONLY",
            "source": {
                "platform": "cda_synthetic_inversion",
                "author": "CDA Generator Engine",
                "url": ""
            },
            "published_at": pub_time,
            "content": {
                "title": "Báo cáo phục hồi sau ngập (CDA Augmented)",
                "text": text
            },
            "location": {
                "locations": [s["ward"], "TP. Hồ Chí Minh"],
                "ward": s["ward"],
                "legacy_ward": s["ward"],
                "is_merged": False,
                "city": "Hồ Chí Minh",
                "legacy_district": "TP.HCM"
            },
            "media": {
                "has_media": False,
                "media_urls": []
            },
            "aste_triplets": [triplet],
            "seq_id": i
        }
        new_items.append(entry)

    # Ghi đè file v3
    with open(V3_PATH, "w", encoding="utf-8") as f:
        json.dump(new_items, f, ensure_ascii=False, indent=2)

    print(f"\n[+] ĐÃ LƯU THÀNH CÔNG TẬP DATASET V3 MỚI VÀO: {V3_PATH}")
    print(f"  - Tổng số mẫu câu mới: {len(new_items)} câu (gồm {len(real_items)} câu thực tế + {len(cda_data)} câu CDA)")

    # Thống kê nhanh
    all_triplets = [t for it in new_items for t in it.get("aste_triplets", [])]
    pols = {}
    for t in all_triplets:
        pols[t["polarity"]] = pols.get(t["polarity"], 0) + 1

    print("\n📊 PHÂN BỐ CỰC TÍNH MỚI:")
    for pol in ["NEG", "NEU", "POS"]:
        cnt = pols.get(pol, 0)
        print(f"  - {pol:6}: {cnt:5d} ({cnt/len(all_triplets)*100:5.2f}%)")
    print("=" * 80)


if __name__ == "__main__":
    main()
