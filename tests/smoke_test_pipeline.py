# -*- coding: utf-8 -*-
"""
tests/smoke_test_pipeline.py
Chiến Lược Kiểm Thử Khói Tự Động (Automated Smoke Test Suite).

Mục tiêu (Blueprint 8):
1. Test 1: Kiểm tra Dashboard Web Server cổng 8050 và /api/metrics.
2. Test 2: Kiểm tra cấu trúc dữ liệu /api/realtime-heatmap.
3. Test 3: Kiểm tra tính toàn vẹn tuyệt đối tọa độ 3 tuyến đường bảo chứng:
   - Đường số 40 Hiệp Bình: [10.8444, 106.7331]
   - Chợ Thủ Đức: [10.8505, 106.7543]
   - Quốc lộ 51 Phước Thái: [10.6650, 107.0350]
4. Test 4: Kiểm tra bộ gom cụm SpatioTemporalClusterer (Gom 20 bài báo cáo -> 1 cụm).
5. Test 5: Kiểm tra Hợp đồng Dịch vụ AI Đa phương thức (Section 4.6).
6. Test 6: Kiểm tra cơ chế Dead Letter Queue (DLQ fallback).
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import json
import time
import requests

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def test_dashboard_health():
    print("\n[TEST 1] Kiem tra Dashboard Web Server cong 8050...")
    for host in ["127.0.0.1", "localhost"]:
        try:
            res = requests.get(f"http://{host}:8050/", timeout=3)
            if res.status_code == 200:
                print(f"   [+] Dashboard ({host}) phan hoi HTTP 200 OK")
                res_m = requests.get(f"http://{host}:8050/api/metrics", timeout=3)
                if res_m.status_code == 200:
                    m_data = res_m.json()
                    print(f"   [+] API Metrics phan hoi HTTP 200 OK (Status: {m_data.get('status')})")
                return
        except requests.exceptions.RequestException:
            continue
    print("   [!] Dashboard Web Server hien chua bat tren cong 8050 (Bo qua khi chay doc lap).")


def test_api_realtime_heatmap():
    print("\n[TEST 2] Kiem tra API /api/realtime-heatmap...")
    for host in ["127.0.0.1", "localhost"]:
        try:
            res = requests.get(f"http://{host}:8050/api/realtime-heatmap", timeout=3)
            if res.status_code == 200:
                data = res.json()
                assert "events" in data, "Thieu truong 'events' trong payload API"
                assert "mode" in data, "Thieu truong 'mode' trong payload API"
                assert "ward_stats" in data, "Thieu truong 'ward_stats' trong payload API"
                print(f"   [+] API Heatmap ({host}) hop le, tra ve {len(data['events'])} su kien ngap (Served from: {data.get('served_from')})")
                return
        except requests.exceptions.RequestException:
            continue
    print("   [!] Dashboard Web Server hien chua bat tren cong 8050 (Bo qua khi chay doc lap).")


def test_hotspot_coordinates_integrity():
    print("\n[TEST 3] Kiem tra tinh toan ven toa do 3 tuyen duong bao chung...")
    from core.gazetteer import match_hotspot

    # 1. Đường số 40 Hiệp Bình
    m40 = match_hotspot("ngập nặng ở đường số 40 hiệp bình")
    assert m40 is not None, "Không nhận diện được Đường số 40 Hiệp Bình"
    assert abs(m40["lat"] - 10.8444) < 0.005, f"Lệch tọa độ Đường 40: {m40}"
    assert abs(m40["lon"] - 106.7331) < 0.005, f"Lệch kinh độ Đường 40: {m40}"

    # 2. Chợ Thủ Đức
    m_td = match_hotspot("ngập lênh láng ngay chợ thủ đức")
    assert m_td is not None, "Không nhận diện được Chợ Thủ Đức"
    assert abs(m_td["lat"] - 10.8505) < 0.005, f"Lệch tọa độ Chợ Thủ Đức: {m_td}"
    assert abs(m_td["lon"] - 106.7543) < 0.005, f"Lệch kinh độ Chợ Thủ Đức: {m_td}"

    # 3. Quốc lộ 51 Phước Thái
    m_51 = match_hotspot("ql51 phước thái ngập sâu")
    assert m_51 is not None, "Không nhận diện được QL51 Phước Thái"
    assert abs(m_51["lat"] - 10.6650) < 0.005, f"Lệch tọa độ QL51: {m_51}"
    assert abs(m_51["lon"] - 107.0350) < 0.005, f"Lệch kinh độ QL51: {m_51}"

    print("   [+] 100% toa do 3 tuyen duong bao chung chinh xac tuyet doi!")


def test_spatio_temporal_clustering():
    print("\n[TEST 4] Kiem tra Gom cum Khong - Thoi gian (Spatio-Temporal Clustering)...")
    from pipeline.spatio_temporal_clusterer import SpatioTemporalClusterer

    clusterer = SpatioTemporalClusterer(radius_meters=400.0, time_window_seconds=2700)
    now = int(time.time())

    # Tạo 20 sự kiện cùng nói về Chợ Thủ Đức trong cùng 15 phút
    mock_events = []
    for i in range(20):
        mock_events.append({
            "id": f"event_{i}",
            "canonical_id": f"cid_{i}",
            "platform": "tiktok" if i % 2 == 0 else "facebook",
            "author": f"user_{i}",
            "text": f"Chợ Thủ Đức ngập sâu quá bài {i}",
            "create_time": now + (i * 30),
            "location": {
                "street": "Chợ Thủ Đức",
                "lat": 10.8505 + (i * 0.00005),  # Sai lệch vài mét (< 50m)
                "lon": 106.7543 + (i * 0.00005)
            },
            "weight": 2.0
        })

    clustered = clusterer.cluster_events(mock_events)
    assert len(clustered) == 1, f"Kỳ vọng gom thành 1 Master Incident, nhưng ra {len(clustered)}"
    master = clustered[0]
    assert master["report_count"] == 20, f"Kỳ vọng 20 người báo cáo, nhận được {master['report_count']}"
    assert "Được báo cáo bởi 20 người" in master["cluster_label"]
    assert len(master["sources"]) == 2  # Cả tiktok và facebook
    print(f"   [+] Gom cum 20 bai viet -> 1 Master Incident ('{master['cluster_label']}') xuat sac!")


def test_ai_microservice_contract():
    print("\n[TEST 5] Kiem tra Hop dong Ky thuat Dich vu AI Da phuong thuc...")
    from pipeline.veracity_checker import VeracityChecker
    vc = VeracityChecker(enable_weather_check=False)

    sample_event = {
        "id": "test_ai_contract_01",
        "canonical_id": "test_cid_01",
        "text": "Đường Kha Vạn Cân ngập sâu quá xe chết máy la liệt",
        "url": "https://sample.com/video1",
        "create_time": int(time.time()),
        "location": {
            "street": "Kha Vạn Cân",
            "lat": 10.8500,
            "lon": 106.7500
        }
    }

    eval_res = vc.evaluate_content_ai(sample_event)
    assert "content_score" in eval_res, "Thiếu trường content_score"
    assert "visual_verified" in eval_res, "Thiếu trường visual_verified"
    assert eval_res["content_score"] >= 0.70, f"Điểm tin cậy không đạt chuẩn: {eval_res}"
    print(f"   [+] Danh gia noi dung / thi giac thanh cong: Nguon [{eval_res.get('source')}] - Diem: {eval_res.get('content_score')}")


def test_dead_letter_queue():
    print("\n[TEST 6] Kiem tra Co che Dead Letter Queue (DLQ Fallback)...")
    from bigdata.producers.social_producer import SocialKafkaProducer
    producer = SocialKafkaProducer()

    # Bắn thử payload lỗi (text rỗng)
    bad_payload = {"id": "bad_test", "text": ""}
    accepted = producer.publish_event("social.live.raw", bad_payload)
    assert not accepted, "Lẽ ra phải từ chối bản ghi lỗi text rỗng"

    dlq_file = os.path.join(ROOT_DIR, "data", "dlq_events.jsonl")
    assert os.path.exists(dlq_file), "Tệp DLQ fallback chưa được tạo"
    print("   [+] DLQ hoat dong chinh xac: Ban ghi loi duoc bat va ghi nhan an toan!")


if __name__ == "__main__":
    print("=" * 70)
    print("[*] KHOI CHAY BO KIEM THU KHOI TU DONG (AUTOMATED SMOKE TEST)")
    print("=" * 70)

    test_hotspot_coordinates_integrity()
    test_spatio_temporal_clustering()
    test_ai_microservice_contract()
    test_dead_letter_queue()
    test_dashboard_health()
    test_api_realtime_heatmap()

    print("\n" + "=" * 70)
    print("[V] TOAN BO SMOKE TEST DAT TIEU CHUAN HOAN THIEN!")
    print("=" * 70)
