import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'documents/BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Section III.2
old_sec3 = """7. 🚫 **Quy tắc Tránh Đa gán nhãn Trùng lặp (Anti Over-tagging / Multi-level Duplication)**:
   - Khi một câu xuất hiện cả tên đường cụ thể lẫn địa danh bao trùm (ví dụ: `đường Trần Xuân Soạn ( TPHCM )` hoặc `đường Phan Huy Ích ( phường Tân Sơn , TP. HCM )`):
     + **CHỈ gán Aspect duy nhất** cho thực thể cụ thể nhất (`đường Trần Xuân Soạn` hoặc `đường Phan Huy Ích`).
     + **KHÔNG** gán thêm `TPHCM` hay `phường Tân Sơn` cho cùng một vị ngữ trạng thái ngập lụt để tránh tạo ra các triplet trùng lặp làm méo mó trọng số mô hình."""

new_sec3 = """7. 🚫 **Quy tắc Tránh Đa gán nhãn Trùng lặp (Anti Over-tagging / Multi-level Duplication)**:
   - Khi một câu xuất hiện cả tên đường cụ thể lẫn địa danh bao trùm (ví dụ: `đường Trần Xuân Soạn ( TPHCM )` hoặc `đường Phan Huy Ích ( phường Tân Sơn , TP. HCM )`):
     + **CHỈ gán Aspect duy nhất** cho thực thể cụ thể nhất (`đường Trần Xuân Soạn` hoặc `đường Phan Huy Ích`).
     + **KHÔNG** gán thêm `TPHCM` hay `phường Tân Sơn` cho cùng một vị ngữ trạng thái ngập lụt để tránh tạo ra các triplet trùng lặp làm méo mó trọng số mô hình.
8. 🏷️ **Quy tắc "Nguyên văn trong Text" cho Tiền tố Hạ tầng (`đường`, `cầu`, `hầm`, `kênh`, `sông`)**:
   - **Chỉ lấy những gì có thật trong text gốc (`Verbatim in Text`)**:
     + Nếu trong câu có chữ `đường` ngay trước tên riêng (ví dụ: `đường Nguyễn Văn Hưởng`, `đường Tô Ngọc Vân`) $\\rightarrow$ Gán trọn vẹn cả cụm `đường Nguyễn Văn Hưởng`.
     + Nếu trong câu chỉ viết tên riêng (ví dụ: `Nguyễn Văn Hưởng ngập sâu`, `Phan Huy Ích ngập nửa mét`) $\\rightarrow$ Chỉ gán nhãn `Nguyễn Văn Hưởng` hoặc `Phan Huy Ích`, **tuyệt đối không tự ý thêm token `đường` vào**.
   - **Cắt sạch các từ cảm thán, trợ từ ở cuối tên hạ tầng** (như `nha`, `ạ`, `nè`). Ví dụ: `cầu Thị Nghè 2 nha` $\\rightarrow$ Cắt bỏ `nha`, chỉ lấy `cầu Thị Nghè 2`.
9. 📋 **Quy tắc Xử lý Danh sách Tuyến đường Liệt kê (Enumerated Street Lists)**:
   - Khi một bản tin liệt kê một chuỗi các tuyến đường/khu vực chịu chung một tình trạng ngập (ví dụ: `các điểm ngập trên đường ĐT748 , ĐT744 , Bùi Thị Xuân , Thuận Giao 19 . . . ngập nhẹ`):
     + **Bắt buộc trích xuất 1:1 đầy đủ từng thực thể độc lập** kết hợp với vị ngữ trạng thái chung:
       * `(đường ĐT748, ngập nhẹ, NEG)`
       * `(ĐT744, ngập nhẹ, NEG)`
       * `(Bùi Thị Xuân, ngập nhẹ, NEG)`
       * `(Thuận Giao 19, ngập nhẹ, NEG)`
     + **Tuyệt đối CẤM** gán gom cả chuỗi các con đường vào một Aspect dài duy nhất (`[13..33]`).
     + **Tuyệt đối CẤM** lười biếng chỉ gán 1-2 con đường đầu tiên và bỏ sót các tuyến đường phía sau."""

assert old_sec3 in content, "Section III.2 snippet not found in content"
content = content.replace(old_sec3, new_sec3)

# 2. Update Section V
old_sec5 = """| **`NEU`**<br>*(Trung tính / Dự báo / Đo lường)* | 1. **Đo đạc thủy văn**: Báo cáo mực nước sông, đỉnh triều kỹ thuật khách quan.<br>2. **Dự báo thời tiết & Khuyến cáo rủi ro**: Cảnh báo nguy cơ (chưa xảy ra thực tế).<br>3. **Câu hỏi thăm dò / Tu từ**: Hỏi tình hình, thắc mắc thông số. | Xuất hiện: *đang ở mức cao, dự báo đạt 1m70, có nguy cơ ngập sâu, khuyến cáo hạn chế di chuyển, triều cường chưa đạt đỉnh, mưa bao nhiêu mm thì ngập?*. | • *"triều cường ở TPHCM đang ở mức cao"* $\\rightarrow$ `NEU`<br>• *"dự báo biến đổi chậm"* $\\rightarrow$ `NEU`<br>• *"có nguy cơ ngập sâu"* $\\rightarrow$ `NEU`<br>• *"Đoạn này ngập chưa mọi người?"* $\\rightarrow$ `NEU` |"""

new_sec5 = """| **`NEU`**<br>*(Trung tính / Dự báo / Đo lường)* | 1. **Đo đạc thủy văn**: Báo cáo mực nước sông, đỉnh triều kỹ thuật khách quan.<br>2. **Dự báo thời tiết & Khuyến cáo rủi ro**: Cảnh báo nguy cơ, dự báo có điều kiện (chưa xảy ra thực tế).<br>3. **Câu hỏi thăm dò / Tu từ**: Hỏi tình hình, thắc mắc thông số. | Xuất hiện: *đang ở mức cao, dự báo đạt 1m70, có nguy cơ ngập sâu, khuyến cáo hạn chế di chuyển, triều cường chưa đạt đỉnh, nếu mưa xuất hiện cùng thời điểm nước sẽ thoát chậm hơn, mưa bao nhiêu mm thì ngập?, Ngập Thế Này Sao?*. | • *"triều cường ở TPHCM đang ở mức cao"* $\\rightarrow$ `NEU`<br>• *"dự báo biến đổi chậm"* $\\rightarrow$ `NEU`<br>• *"có nguy cơ ngập sâu"* $\\rightarrow$ `NEU`<br>• *"Đoạn này ngập chưa mọi người?"* $\\rightarrow$ `NEU`<br>• *"Phan Huy Ích Ngập Thế Này Sao ?"* $\\rightarrow$ `NEU`<br>• *"nước trên mặt đường sẽ thoát chậm hơn"* (dự báo điều kiện) $\\rightarrow$ `NEU` |"""

assert old_sec5 in content, "Section V snippet not found in content"
content = content.replace(old_sec5, new_sec5)

# 3. Update Section VI.1
old_sec6_1 = """* **CÁC TỈNH NGOÀI PHẠM VI (OUT-OF-SCOPE - Bắt buộc gán `REJECT (####[])`)**:
  - Tuyệt đối loại bỏ các bản tin từ tỉnh thành khác dù crawler có gán nhầm tiền tố TP.HCM:
    + **Hà Nội**: `#hanoi`, `#hanoimua`, `Chương Mỹ`, `Tứ Liên`, `Hoàng Mai`, `Thanh Xuân`, `Hà Đông`, `ngã 4 văn phú`, app `iHaNoi`.
    + **Cần Thơ**: `#cantho`, `#65cầnthơ`, `#chợbìnhthủy`, `đường Nguyễn Văn Cừ (NVC)`.
    + **Đồng Nai**: `đèo Mẹ Bồng Con`, `Vĩnh Thanh`, `#dongnai`, `#longkhanh`, `Dầu Giây`.
    + **Miền Tây & ĐBSCL**: `Cà Mau` (`#camau`), `Đồng Tháp` / `Sa Đéc` (`#sadec`), `Vĩnh Long`, `Bến Tre`, `Trà Vinh`, `An Giang`, `Kiên Giang`.
    + **Miền Trung & Tây Nguyên**: `Gia Lai`, `Quy Nhơn`, `Nha Trang`, `Đà Lạt`, `Lâm Đồng`, `Đà Nẵng`, `Huế`.
    + **Nước ngoài**: `Thái Lan`, `Bangkok`, `Trung Quốc`."""

new_sec6_1 = """* **CÁC TỈNH NGOÀI PHẠM VI (OUT-OF-SCOPE - Bắt buộc gán `REJECT (####[])`)**:
  - Tuyệt đối loại bỏ các bản tin từ tỉnh thành khác dù crawler có gán nhầm tiền tố TP.HCM:
    + **Hà Nội**: `#hanoi`, `#hanoimua`, `Chương Mỹ`, `Tứ Liên`, `Hoàng Mai`, `Thanh Xuân`, `Hà Đông`, `ngã 4 văn phú`, app `iHaNoi`.
    + **Cần Thơ**: `#cantho`, `#65cầnthơ`, `#chợbìnhthủy`, `đường Nguyễn Văn Cừ (NVC)`.
    + **Đồng Nai**: `đèo Mẹ Bồng Con`, `Vĩnh Thanh`, `#dongnai`, `#longkhanh`, `Dầu Giây`.
    + **Miền Tây & ĐBSCL**: `Cà Mau` (`#camau`), `Đồng Tháp` / `Sa Đéc` (`#sadec`), `Vĩnh Long`, `Bến Tre`, `Trà Vinh`, `An Giang`, `Kiên Giang`.
    + **Miền Trung & Tây Nguyên**: `Gia Lai`, `Quy Nhơn`, `Nha Trang`, `Đà Lạt`, `Lâm Đồng`, `Đà Nẵng`, `Huế`, `Nông Cống`, `Thanh Hóa`.
    + **Nước ngoài**: `Thái Lan`, `Bangkok`, `Trung Quốc`.
* 📌 **Phân biệt Hashtag Quê quán Người dùng vs Địa danh Xảy ra Ngập Thực tế**:
  - Khi cào bài từ mạng xã hội (TikTok, Facebook), nhiều người dùng gắn hashtag quê quán cá nhân (ví dụ: công nhân PouYuen Bình Tân gắn `#bentre`, `#bentre71` vì là người Bến Tre xa quê).
  - **Nguyên tắc ưu tiên Ngữ cảnh Nội dung trước Hashtag Cá nhân**:
    + Nếu nội dung bài viết nêu rõ địa danh cụ thể tại TP.HCM hoặc vùng giáp ranh hợp lệ (ví dụ: `PouYuen Bình Tân lại trong biển nước #PouYuen #congnhan #bentre`) $\\rightarrow$ Sự kiện ngập xảy ra ngay tại PouYuen Bình Tân, TP.HCM $\\rightarrow$ **Bắt buộc giữ lại và gán nhãn** cho `PouYuen Bình Tân`.
    + Chỉ gán `REJECT (####[])` khi bản thân sự kiện ngập hoặc toàn bộ bài viết diễn ra ở tỉnh ngoài (Hà Nội, Cần Thơ, Thanh Hóa, Cà Mau...)."""

assert old_sec6_1 in content, "Section VI.1 snippet not found in content"
content = content.replace(old_sec6_1, new_sec6_1)

# 4. Update Section VI.2
old_sec6_2 = """* **Nội dung đời sống giải trí / Ẩn dụ**:
  - Câu cá, giăng lưới mùa nước nổi (`#cathiennhien`, `#đammêcâucá`).
  - Tranh luận triết lý, chém gió không địa chỉ thực tế (*"lượng mưa lớn thì nước nào mà chẳng ngập"*).
  - Từ ngữ ẩn dụ: *ngập tràn xe mới, ngập tràn niềm vui, ngập tràn ưu đãi*."""

new_sec6_2 = """* **Nội dung đời sống giải trí / Ẩn dụ**:
  - Câu cá, giăng lưới mùa nước nổi (`#cathiennhien`, `#đammêcâucá`).
  - Tranh luận triết lý, chém gió không địa chỉ thực tế (*"lượng mưa lớn thì nước nào mà chẳng ngập"*).
  - Từ ngữ ẩn dụ: *ngập tràn xe mới, ngập tràn niềm vui, ngập tràn ưu đãi*.
* 🎭 **Làm sạch Video Clip Meme / Đời Sống Giải Trí Không Mang Giá Trị Cảnh Báo**:
  - Bắt buộc gán `REJECT (####[])` cho các clip bắt trend giải trí, hài hước, nghệ thuật mà từ ngữ ngập lụt chỉ đóng vai trò làm nền:
    + So sánh phim ảnh hoạt hình / anime (ví dụ: *đoạn video đạp xe giữa vùng ngập nước giống cảnh trong Vùng đất linh hồn #anime* $\\rightarrow$ `####[]`).
    + Đi xem concert ca nhạc (ví dụ: *đội mưa vượt ngập nước để nghe chị Chi hát live* $\\rightarrow$ `####[]`).
    + Clip thú cưng, cún cưng lội nước đùa giỡn (`#thucung`, `#dangyeu` $\\rightarrow$ `####[]`).
    + Clip trêu đùa hài hước (ví dụ: *anh cá đi khảo sát nước ngập đi tới cái chảo luôn* $\\rightarrow$ `####[]`).
    + Mẹo bảo dưỡng / kỹ thuật xe (ví dụ: *Quy trình xử lý khi xe bị ngập nước VF5 #xecongnghe* $\\rightarrow$ `####[]`)."""

assert old_sec6_2 in content, "Section VI.2 snippet not found in content"
content = content.replace(old_sec6_2, new_sec6_2)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Cẩm nang BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md updated successfully!")
