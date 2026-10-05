"""
core/state_manager.py - Quản lý Trạng thái Ingestion (Watermark & Khử trùng lặp)
Đảm bảo luồng Real-Time không bị trùng bài và luôn bám sát mốc thời gian mới nhất.
"""

import json
import os
import time
from typing import Set, Dict, Any

STATE_FILE = os.path.join("data", "pipeline_state.json")

class StateManager:
    def __init__(self, state_path: str = STATE_FILE):
        self.state_path = state_path
        self.watermark: int = 0
        self.seen_ids: Set[str] = set()
        self.load()

    def load(self):
        """Đọc trạng thái đã lưu từ file disk (nếu có)"""
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.watermark = data.get("watermark", 0)
                    self.seen_ids = set(data.get("seen_ids", []))
            except Exception as e:
                print(f"[State] Không thể đọc state file ({e}), khởi tạo mới.")

    def save(self):
        """Lưu trạng thái xuống disk"""
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        # Giữ tối đa 5000 IDs gần nhất để tránh file phình to
        trimmed_ids = list(self.seen_ids)[-5000:]
        payload = {
            "watermark": self.watermark,
            "last_saved_time": int(time.time()),
            "seen_ids_count": len(trimmed_ids),
            "seen_ids": trimmed_ids
        }
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def is_new(self, video_id: str, create_time: int) -> bool:
        """Kiểm tra video có mới hơn watermark và chưa từng gặp hay không"""
        if video_id in self.seen_ids:
            return False
        if self.watermark > 0 and create_time <= self.watermark:
            return False
        return True

    def mark_seen(self, video_id: str, create_time: int):
        """Ghi nhận video mới và cập nhật watermark trượt về phía trước"""
        self.seen_ids.add(video_id)
        if create_time > self.watermark:
            self.watermark = create_time

    def reset(self, new_watermark: int = 0):
        """Reset state phục vụ mục đích test thử nghiệm"""
        self.watermark = new_watermark
        self.seen_ids.clear()
        self.save()
