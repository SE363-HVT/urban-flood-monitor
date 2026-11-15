import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# Line 1601 (idx 1600): omit Quận 7
updates[1600] = (
    "Lâu lâu ghé qua Quận 7 mà ngập như sông luôn 😭 🌊 Huỳnh Tấn Phát 😅 📍 # quận7 # huynhtanphat # SàiGòn # ngậpmùa # trendtiktok 💦 🚤",
    [([13, 14, 15], [7, 8, 9], 'NEG')]
)

# Line 1604 (idx 1603): include prefix 'đường' -> đường Phạm Hữu Lầu [123, 124, 125, 126]
updates[1603] = (
    "Chiều tối 5 . 12 , triều cường đạt đỉnh trong đợt rằm tháng 10 âm lịch khiến nhiều tuyến đường ở khu nam TP. HCM ngập sâu , người dân đi lại khó khăn . Khoảng 16 giờ 30 , triều cường từ các con kênh , sông bắt đầu dâng cao và tràn vào nhiều tuyến đường ở khu nam TP. HCM . Đến khoảng 17 giờ , nhiều tuyến đường đã ngập sâu . Cụ thể các tuyến đường bị ảnh hưởng bởi triều cường tối nay gồm Phạm Hữu Lầu , Huỳnh Tấn Phát , Phú Thuận , Trần Xuân Soạn , Nguyễn Lương Bằng , Lê Văn Lương , Nguyễn Thị Thập … Lúc 18 giờ , đoạn đường Phạm Hữu Lầu ( phường Tân Mỹ ) ngập nặng , kéo dài gần hết tuyến đường như các đợt triều cường trước đây . Nhiều nơi nước ngập cao gần bánh xe máy , người dân di chuyển hết sức khó khăn . Đặc biệt , giao lộ đường 15B - Phạm Hữu Lầu bị ngập lênh láng . Trong khi đó , tại giao lộ Nguyễn Lương Bằng - Hoàng Quốc Việt cũng ngập diện rộng . Giao thông tại khu vực này bị ùn ứ vì nước ngập dù lực lượng CSGT đã túc trực , điều tiết phương tiện đi lại . Còn trên đường Phú Thuận và Trần Xuân Soạn , tình trạng ngập ít hơn những đợt triều cường trước . Bởi trên đường Trần Xuân Soạn , lực lượng chức năng đã đắp bao cát , ngăn nước từ Kênh Đôi nên chỉ ngập nhẹ . Đoạn ngập kéo dài không đáng kể .",
    [([123, 124, 125, 126], [132, 133], 'NEG'),
     ([253, 254, 255, 256], [274, 275], 'NEU')]
)

# Line 1615 (idx 1614): include tại TPHCM -> triều cường tại TPHCM [7, 8, 9, 10]
updates[1614] = (
    "23 tuyến đường bị ngập nặng do triều cường tại TPHCM # trieucuong # ngaplut # thuytrieu # fyp # trending",
    [([7, 8, 9, 10], [4, 5], 'NEG')]
)

# Line 1640 (idx 1639): omit Bình Thạnh (multi-level dup with Bình Quới)
updates[1639] = (
    "Đợt triều cường tháng 10 này lên cao quá , khu vực Nhà Bè , Quận 7 , 8 , Ql50 Bình Chánh , Bình Quới Bình Thạnh , . . ngập khá sâu , mọi người lưu thông bình an nha , hình ảnh này là tôi dính ngập ỏ quận 8 chiều tối hôm nay # triềucường # sàigòn # ngập # 2025 # dubaothoitiet",
    [([12, 13], [31, 32, 33], 'NEG'),
     ([15, 16], [31, 32, 33], 'NEG'),
     ([24, 25], [31, 32, 33], 'NEG')]
)

# Line 1654 (idx 1653): fix hallucination -> Triều cường ở TPHCM [13, 14, 15, 16] | dâng cao [17, 18], đường Trần Xuân Soạn [21, 22, 23, 24] | bị ngập sâu [31, 32, 33]
updates[1653] = (
    "Người dân TP. HCM vật lộn với triều cường giờ tan tầm 💦 Triều cường ở TPHCM dâng cao khiến đoạn đường Trần Xuân Soạn ( quận 7 , TPHCM ) bị ngập sâu . Nước từ miệng cống và kênh , rạch gần đó tràn lên đường vào giờ tan tầm khiến người dân di chuyển vất vả . Đến 18h30 , dòng nước vẫn đang tiếp tục dâng cao . Người dân sống tại các con hẻm trên đường Trần Xuân Soạn , Huỳnh Tấn Phát không còn lạ gì với cảnh nước triều từ kênh Tẻ dâng ngập lên mặt đường và tràn cả vào nhà … 👇 # Vietnamnet # Thờisự # PT",
    [([13, 14, 15, 16], [17, 18], 'NEG'),
     ([21, 22, 23, 24], [31, 32, 33], 'NEG')]
)

# Line 1675 (idx 1674): omit quận 12
updates[1674] = (
    "Cơn mưa lớn tối 27 - 5 khiến một số tuyến đường ở TP. HCM bị ngập , người dân bì bõm lội nước về nhà . Theo ghi nhận , trên đường Nguyễn Văn Quá quận 12 , mưa gây ngập hơn nửa bánh xe máy .",
    [([32, 33, 34, 35], [42, 43, 44, 45, 46], 'NEG')]
)

# Validate and apply updates
for idx, (new_text, new_trips) in updates.items():
    tokens = new_text.split()
    for asp, opi, pol in new_trips:
        for a in asp:
            assert a < len(tokens), f"Line {idx+1}: asp idx {a} out of range {len(tokens)}"
        for o in opi:
            assert o < len(tokens), f"Line {idx+1}: opi idx {o} out of range {len(tokens)}"
    lines[idx] = f"{new_text}####{new_trips}"

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print(f"Batch 17: Successfully updated {len(updates)} records!")
