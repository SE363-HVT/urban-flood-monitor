# -*- coding: utf-8 -*-
"""
Script chuẩn bị và rà soát các records cần khôi phục & chỉnh sửa trong Phase 3:
1. Khôi phục & gán nhãn cho các records Bình Dương & Vũng Tàu (hạ tầng, đường, phường, xã, thành phố).
2. Khôi phục & gán nhãn cho các records dùng từ ngữ dân dã / châm chọc / châm biếm về ngập lụt thực tế.
3. Rà soát & hiệu chỉnh Lô 11 - 14 (Records 1001 đến 1400).
4. Kiểm tra đối soát index và tokenization để đảm bảo 0 lỗi.
"""

import ast

phase3_path = 'data/validate_label/thuan/phase3.txt'
master_path = 'data/processed/aste_v2_format/master_10k_triplets.txt'

with open(phase3_path, 'r', encoding='utf-8') as f:
    p3_lines = [l.strip() for l in f if l.strip()]

with open(master_path, 'r', encoding='utf-8') as f:
    m_lines = [l.strip() for l in f if l.strip()]

p3_m = m_lines[2500:6375]
assert len(p3_lines) == 3875, f"Expected 3875 lines, got {len(p3_lines)}"
assert len(p3_m) == 3875, f"Expected 3875 master lines, got {len(p3_m)}"

# Dictionary to hold revisions: rec_id (1-indexed) -> (new_text, new_triplets, comment)
revisions = {}

print("Sẵn sàng xây dựng bộ sửa đổi chi tiết...")
