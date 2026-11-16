# -*- coding: utf-8 -*-
"""
Bộ xử lý chuẩn hóa chuyên sâu cho các records cần khôi phục & hiệu chỉnh trong Phase 3:
- Nhóm 1: Bình Dương & Vũng Tàu (Đô thị sáp nhập / giáp ranh)
- Nhóm 2: Từ ngữ Dân dã / Châm biếm về ngập lụt
- Nhóm 3: Hiệu chỉnh chuyên sâu Lô 11 - 14 (Records 1001 đến 1400)
"""

# Dictionary: rec_id -> (text, triplets, note)
REVISED_RECORDS = {}

def add_rev(rec_id, text, triplets, note=""):
    REVISED_RECORDS[rec_id] = (text, triplets, note)

# ==============================================================================
# NHÓM 1: BÌNH DƯƠNG & VŨNG TÀU (KHÔI PHỤC VÀ GÁN NHÃN ĐÚNG QUY CHUẨN)
# ==============================================================================

# Rec 63: Bãi sau Sài Gòn mùa mưa lũ -> Sài Gòn ngập
add_rev(63, "Bãi sau Sài Gòn mùa mưa lũ nhé 😎 😎 😎 # tphcm # vungtau # mưa # mưagióbãobùng # ngập", [
    ([2, 3], [4, 5], 'NEG'),
], "Sài Gòn mùa mưa lũ")

# Rec 210: 159 điểm ngập thường xuyên tại TP. HCM ( gồm TP. HCM cũ , Bình Dương cũ , Bà Rịa - Vũng Tàu cũ )
add_rev(210, "159 điểm ngập thường xuyên tại TP. HCM ( gồm TP. HCM cũ , Bình Dương cũ , Bà Rịa - Vũng Tàu cũ ) · TP. HCM cũ : 76 điểm . Trung tâm : 39 điểm", [
    ([7, 8], [2], 'NEU'),
    ([14, 15], [2], 'NEU'),
    ([18, 19], [2], 'NEU'),
    ([22, 23, 24, 25], [2], 'NEU'),
], "Bình Dương, Bà Rịa - Vũng Tàu điểm ngập thường xuyên")

# Rec 256: Đông Hòa Quốc lộ 1k ( Dĩ An , Bình Dương )
add_rev(256, "Anh em Tphcm cũ và sau sáp nhập update khu vực nào ko ngập sau mấy trận mưa lớn ạ ! Em trc : 1 / Đông Hòa Quốc lộ 1k ( Dĩ An , Bình Dương ) : ngập nhẹ", [
    ([24, 25, 26], [35, 36], 'NEG'),
    ([28, 29], [35, 36], 'NEG'),
    ([31, 32], [35, 36], 'NEG'),
], "Quốc lộ 1k Dĩ An Bình Dương ngập nhẹ")

# Rec 399: Bình Dương tiếp tục giữ chuỗi " hồi chiều trời mưa " CSGT cảnh báo 122 điểm ngập ở TPHCM
add_rev(399, "Bình Dương tiếp tục giữ chuỗi \" hồi chiều trời mưa \" CSGT cảnh báo 122 điểm ngập ở TPHCM bao gồm khu vực Vũng Tàu", [
    ([0, 1], [15], 'NEU'),
    ([17], [15], 'NEU'),
    ([22, 23], [15], 'NEU'),
], "Bình Dương, Vũng Tàu 122 điểm ngập")

# Rec 467: Dĩ An mưa to quá nè bà con cập nhật tình hình ngập đi
add_rev(467, "Dĩ An mưa to quá nè bà con cập nhật tình hình ngập đi", [
    ([0, 1], [10], 'NEU'),
], "Dĩ An ngập")

# Rec 485: Bình Dương ngập sâu sau mưa lớn
add_rev(485, "Bình Dương ngập sâu sau mưa lớn , lực lượng chức năng rất nhanh đã giải cứu nhiều người dân bị cô lập trong vùng ngập", [
    ([0, 1], [2, 3], 'NEG'),
], "Bình Dương ngập sâu")

# Rec 493: phường Bến Cát ngập sâu
add_rev(493, "Mưa lớn sáng 23 / 10 khiến nhiều khu dân cư ở phường Bến Cát ngập sâu , có nơi nước dâng gần 2 m , lực lượng chức năng phải dùng dây thừng hỗ trợ hơn 120 người đến nơi an toàn .", [
    ([11, 12, 13], [14, 15], 'NEG'),
], "phường Bến Cát ngập sâu")

# Rec 502: phường Thủ Dầu Một ( TPHCM ) ngập sâu
add_rev(502, "Tối 23 / 10 , nhiều tuyến đường gần sông Sài Gòn , thuộc phường Thủ Dầu Một ( TPHCM ) , bất ngờ bị ngập sâu , khiến phương tiện và người dân không thể lưu thông", [
    ([13, 14, 15, 16], [22, 23], 'NEG'),
], "phường Thủ Dầu Một ngập sâu")

# Rec 508: gây ngập 1 số nơi như Chánh Mỹ , chợ Thủ Dầu Một , bờ kè Bưng Cải , An Sơn , Quốc Lộ 13
add_rev(508, "Hiện mực nước sông Sài Gòn đang dâng cao , gây ngập 1 số nơi như Chánh Mỹ , chợ Thủ Dầu Một , bờ kè Bưng Cải , An Sơn , Quốc Lộ 13", [
    ([14, 15], [9], 'NEG'),
    ([17, 18, 19, 20], [9], 'NEG'),
    ([22, 23, 24, 25], [9], 'NEG'),
    ([27, 28], [9], 'NEG'),
    ([30, 31, 32], [9], 'NEG'),
], "Chánh Mỹ, chợ Thủ Dầu Một, Quốc Lộ 13 ngập")

# Rec 509: Bình Dương mưa kết hợp với triều cường có thể gây ngập úng
add_rev(509, "Sáng sớm 18 / 9 , ở tỉnh Bình Dương đã có mưa kéo dài . Theo dự báo , mưa kết hợp với triều cường có thể gây ngập úng tại các vùng hạ du ven sông Sài Gòn .", [
    ([6, 7], [22, 23, 24, 25], 'NEU'),
    ([32, 33, 34], [22, 23, 24, 25], 'NEU'),
], "Bình Dương, sông Sài Gòn có thể gây ngập úng")

# Rec 600: khu vực Bến Cát - Bàu Bàng bị ngập sâu
add_rev(600, "Sau cơn mưa lớn nhiều nơi ở khu vực Bến Cát - Bàu Bàng ( Bình Dương cũ ) bị ngập sâu , lực lượng cứu hộ TP HCM kịp thời đưa 127 người đến nơi an toàn", [
    ([9, 10], [18, 19], 'NEG'),
    ([12, 13], [18, 19], 'NEG'),
    ([15, 16], [18, 19], 'NEG'),
], "Bến Cát, Bàu Bàng, Bình Dương ngập sâu")

# Rec 715: NHIỀU TUYẾN ĐƯỜNG TRUNG TÂM KHU VỰC VŨNG TÀU NGẬP SAU MƯA !
add_rev(715, "NHIỀU TUYẾN ĐƯỜNG TRUNG TÂM KHU VỰC VŨNG TÀU NGẬP SAU MƯA ! Tối 2 / 9 , một cơn mưa lớn kéo dài khiến các tuyến đường khu vực trung tâm Vũng Tàu ngập nặng", [
    ([5, 6], [7], 'NEG'),
    ([24, 25], [26, 27], 'NEG'),
], "VŨNG TÀU NGẬP, Vũng Tàu ngập nặng")

# Rec 921: Cảnh báo triều cường vượt báo động 3 ở Bình Dương
add_rev(921, "Sáng sớm 18 / 9 , ở tỉnh Bình Dương đã có mưa kéo dài . Theo dự báo , mưa kết hợp với triều cường có thể gây ngập úng tại các vùng hạ du ven sông Sài Gòn .", [
    ([6, 7], [22, 23, 24, 25], 'NEU'),
    ([32, 33, 34], [22, 23, 24, 25], 'NEU'),
], "Bình Dương có thể gây ngập úng")

# Rec 2050: Bình Dương cũ có nhiều điểm ngập
add_rev(2050, "Bình Dương cũ có nhiều điểm ngập", [
    ([0, 1], [4, 5, 6], 'NEG'),
], "Bình Dương có nhiều điểm ngập")

# Rec 2159: Quốc lộ 13 từ trạm thu phí Lái Thiêu mưa ngập
add_rev(2159, "Nâng nền Quốc lộ 13 , nhà dân thấp gần 1m , nắng bụi mưa ngập Đoạn Quốc lộ 13 từ trạm thu phí Lái Thiêu đến cầu Vĩnh Bình đang được thi công", [
    ([2, 3, 4], [13, 14], 'NEG'),
    ([16, 17, 18], [13, 14], 'NEG'),
], "Quốc lộ 13 mưa ngập")

# Rec 2301: Cách Mạng Tháng Tám từ vòng xoay chợ Lái Thiêu đang ngập
add_rev(2301, "Cảnh báo 🆘 Mưa lớn , đang ngập đoạn Cách Mạng Tháng Tám từ vòng xoay chợ Lái Thiêu ( tua 18 ) đến trạm thu phí cầu Phú Long", [
    ([8, 9, 10, 11], [5, 6], 'NEG'),
    ([15, 16, 17], [5, 6], 'NEG'),
], "Cách Mạng Tháng Tám, chợ Lái Thiêu đang ngập")

# Rec 2303: Cách Mạng Tháng Tám ngập
add_rev(2303, "Cảnh báo ngay lúc này 🆘 ĐANG MƯA lớn , và ngập đoạn Cách Mạng Tháng Tám từ vòng xoay chợ Lái Thiêu ( tua 18 ) đến trạm thu phí cầu Phú Long", [
    ([11, 12, 13, 14], [8], 'NEG'),
    ([18, 19, 20], [8], 'NEG'),
], "Cách Mạng Tháng Tám, chợ Lái Thiêu ngập")

# Rec 2417: Bình Dương mưa ngập lối về
add_rev(2417, "Bình Dương mưa ngập lối về", [
    ([0, 1], [2, 3], 'NEG'),
], "Bình Dương mưa ngập")

# Rec 2418: đường tạo lực bắc tân uyên ngập sâu
add_rev(2418, "trận mưa sáng sớm nay khiến đường tạo lực bắc tân uyên ngập sâu # xuhuongtiktok # bdsminhhung # xuhuong # xuhuong2026", [
    ([5, 6, 7, 8, 9, 10], [11, 12], 'NEG'),
], "đường tạo lực bắc tân uyên ngập sâu")

# Rec 2443: phường Thủ Dầu Một ( TPHCM ) mưa lớn gây ngập
add_rev(2443, "Mưa lớn gây ngập nhiều tuyến đường tại phường Thủ Dầu Một ( TPHCM ) , giao thông bị ảnh hưởng nghiêm trọng .", [
    ([9, 10, 11, 12], [2], 'NEG'),
], "phường Thủ Dầu Một ngập")

# Rec 2522: 159 điểm ngập thường xuyên tại TP. HCM ( gồm TP. HCM cũ , Bình Dương cũ , Bà Rịa - Vũng Tàu cũ )
add_rev(2522, "159 điểm ngập thường xuyên tại TP. HCM ( gồm TP. HCM cũ , Bình Dương cũ , Bà Rịa - Vũng Tàu cũ ) · TP. HCM cũ : 76 điểm .", [
    ([7, 8], [2], 'NEU'),
    ([14, 15], [2], 'NEU'),
    ([18, 19], [2], 'NEU'),
    ([22, 23, 24, 25], [2], 'NEU'),
], "Bình Dương, Bà Rịa - Vũng Tàu điểm ngập")

# Rec 2551: đoạn cầu Khánh Vân ( Tân Uyên , Bình Dương cũ ) nước cuồn cuồn tràn về
add_rev(2551, "🆘 Cảnh báo khẩn giữa đêm , nước cuồn cuồn tràn về đoạn cầu Khánh Vân ( Tân Uyên , Bình Dương cũ ) Nước từ đâu chưa rõ dồn dập đổ về", [
    ([12, 13, 14], [7, 8, 9, 10], 'NEG'),
    ([16, 17], [7, 8, 9, 10], 'NEG'),
], "cầu Khánh Vân, Tân Uyên nước tràn về")

# Rec 2552: cầu Khánh Vân ( Tân Uyên , Bình Dương cũ ) nước cuồn cuồn tràn về
add_rev(2552, "Khẩn 🆘 Cảnh báo giữa đêm , nước cuồn cuồn tràn về đoạn cầu Khánh Vân ( Tân Uyên , Bình Dương cũ ) Nước từ đâu chưa rõ dồn dập đổ về", [
    ([11, 12, 13], [6, 7, 8, 9], 'NEG'),
    ([15, 16], [6, 7, 8, 9], 'NEG'),
], "cầu Khánh Vân tràn về")

# Rec 2553: điểm ngập sâu cầu Khánh Vân ( Tân Uyên , Bình Dương cũ )
add_rev(2553, "Cập nhật ngay lúc này 🆘 2h sáng , lực lượng chức năng phường Tân Khánh ( Tân Uyên , Bình Dương cũ ) đã có mặt tại điểm ngập sâu cầu Khánh Vân", [
    ([24, 25, 26], [22, 23], 'NEG'),
    ([14, 15], [22, 23], 'NEG'),
], "cầu Khánh Vân ngập sâu")

# Rec 2667: dĩ an bình dương mưa ngập
add_rev(2667, "mưa ngập kiểu này chỉ có dĩ an bình dương thôi kk 🤣 giờ làm mòi gì nhậu anh em 🤣", [
    ([6, 7, 8, 9], [0, 1], 'NEG'),
], "dĩ an bình dương mưa ngập")

# Rec 2770: triều cường lên chợ BD , c ôbg đành , Ngô Quyền
add_rev(2770, "Mọi năm cứ triều cường lên rồi rút nhanh , còn năm nay thì lên ối giời ơi luôn . nào là chợ BD , nào là c ôbg đành , Ngô Quyền", [
    ([21, 22], [3, 4], 'NEG'),
    ([29, 30], [3, 4], 'NEG'),
], "chợ BD, Ngô Quyền triều cường lên")

# Rec 2771: Bình Dương lại mưa ngập nữa rồi
add_rev(2771, "Bình Dương lại mưa ngập nữa rồi", [
    ([0, 1], [3, 4], 'NEG'),
], "Bình Dương mưa ngập")

# Rec 2778: triều cường có thể đạt 1 , 9 – 1 , 95m Thủ Dầu Một , ngập
add_rev(2778, "Đài KTTV Nam bộ dự báo triều cường có thể đạt 1 , 9 – 1 , 95m Thủ Dầu Một , vượt báo động 3 30 – 35cm , ngập .", [
    ([14, 15, 16], [25], 'NEU'),
], "Thủ Dầu Một ngập dự báo")

# Rec 2857: Thủ Dầu Một ngập lênh láng
add_rev(2857, "kiếp nạn sinh nhật mùa mưa Thủ Dầu Một ngập lênh láng 🤣 🤣 # binhduongdidau # reviewbinhduong # binhduongangi", [
    ([5, 6, 7], [8, 9], 'NEG'),
], "Thủ Dầu Một ngập lênh láng")

# Rec 2858: Bình Dương nhiều tuyến đường gần sông thuỷ triều dâng cao ngập cả mặt đường
add_rev(2858, "Bình Dương sáng nay nhiều tuyến đường gần sông thuỷ triều dâng cao ngập cả mặt đường # reviewbinhduong # thu", [
    ([0, 1], [13], 'NEG'),
], "Bình Dương ngập")

# Rec 2967: phường Thủ Dầu Một ( TPHCM ) bất ngờ bị ngập sâu
add_rev(2967, "Tối nay ( 23 / 10 ) , nhiều tuyến đường gần sông Sài Gòn , thuộc phường Thủ Dầu Một ( TPHCM ) , bất ngờ bị ngập sâu , khiến phương tiện và người dân không thể lưu thông", [
    ([17, 18, 19, 20], [26, 27], 'NEG'),
], "phường Thủ Dầu Một ngập sâu")

# Rec 2988: Chánh Mỹ , chợ Thủ Dầu Một , bờ kè Bưng Cải , An Sơn , Quốc Lộ 13 ngập
add_rev(2988, "Hiện mực nước sông Sài Gòn đang dâng cao , gây ngập 1 số nơi như Chánh Mỹ , chợ Thủ Dầu Một , bờ kè Bưng Cải , An Sơn , Quốc Lộ 13", [
    ([14, 15], [9], 'NEG'),
    ([17, 18, 19, 20], [9], 'NEG'),
    ([22, 23, 24, 25], [9], 'NEG'),
    ([27, 28], [9], 'NEG'),
    ([30, 31, 32], [9], 'NEG'),
], "chợ Thủ Dầu Một, Quốc Lộ 13 ngập")

# Rec 3127: Cách Mạng Tháng Tám ( cầu ông Đành ) , Ngô Quyền triều cường dâng cao
add_rev(3127, "Trung tâm Bình Dương ngay lúc này 😟 Triều cường dâng cao , loạt tuyến đường như Cách Mạng Tháng Tám ( cầu ông Đành ) , Ngô Quyền (", [
    ([2, 3], [7, 8, 9], 'NEG'),
    ([15, 16, 17, 18], [7, 8, 9], 'NEG'),
    ([24, 25], [7, 8, 9], 'NEG'),
], "Bình Dương, Cách Mạng Tháng Tám Triều cường dâng cao")

# Rec 3132: TP Dĩ An nhiều nhà dân bị ngập nặng
add_rev(3132, "Nhiều nhà dân đã bị ngập nặng sau cơn mưa lớn sáng nay ở TP Dĩ An .", [
    ([13, 14, 15], [4, 5], 'NEG'),
], "TP Dĩ An ngập nặng")

# Rec 3133: quốc lộ 1K , khu vực Châu Thới Ngập mênh mông
add_rev(3133, "quốc lộ 1K , khu vực Châu Thới tối nay Ngập mênh mông luôn , hiện CSGT đang điều tiết Tôi là dân Dĩ An TÔI L", [
    ([0, 1, 2], [8, 9], 'NEG'),
    ([5, 6], [8, 9], 'NEG'),
    ([20, 21], [8, 9], 'NEG'),
], "quốc lộ 1K, Châu Thới, Dĩ An Ngập mênh mông")

# Rec 3134: Bình Dương bị ngập sâu
add_rev(3134, "Bình Dương ❌ Khẩn trương đưa người dân ra khỏi nơi bị ngập sâu , nguy hiểm Sáng nay ngày 10 / 5 , trận mưa lớn kèm lốc xoáy quét qua", [
    ([0, 1], [11, 12], 'NEG'),
], "Bình Dương ngập sâu")

# Rec 3136: đường Nguyễn Tri Phương Dĩ An đang ngập sâu
add_rev(3136, "‼ ️ DĨ AN - Nhiều tuyến đường đã ngập Hiện tại đường Nguyễn Tri Phương đang ngập sâu , có đoạn nước chảy như thác , bà con hạn chế", [
    ([2, 3], [7], 'NEG'),
    ([11, 12, 13, 14], [16, 17], 'NEG'),
], "DĨ AN ngập, đường Nguyễn Tri Phương ngập sâu")

# Rec 3140: BÌNH DƯƠNG NGẬP SÂU
add_rev(3140, "BÌNH DƯƠNG : CÁC CHIẾN SĨ KHẨN TRƯƠNG DI DỜI NGƯỜI DÂN RA KHỎI NHỮNG NƠI NGẬP SÂU ‼ ️ Sáng nay ngày 10 / 5 , trận mưa lớn", [
    ([0, 1], [15, 16], 'NEG'),
], "BÌNH DƯƠNG NGẬP SÂU")

# Rec 3142: Bình Dương Mưa lớn cuốn trôi xe
add_rev(3142, "Bình Dương : Mưa lớn cuốn trôi xe bán tải , nữ tài xế ra đi trong cống thoát nước 😥 😥 😥 Tối 13 / 9 , một phụ nữ điều khiển xe ô tô trên đường đang bị ngập nước trong cơn mưa lớn ở Bình Dương", [
    ([0, 1], [3, 4], 'NEG'),
    ([0, 1], [35, 36], 'NEG'),
], "Bình Dương ngập nước")

# Rec 3143: Bình Dương nhiều tuyến đường ngập sâu
add_rev(3143, "Cơn mưa lớn đổ xuống cuối chiều nay khiến nhiều tuyến đường ở Bình Dương ngập sâu , xe máy bị nước cuốn , cây xanh gãy đổ . . .", [
    ([12, 13], [14, 15], 'NEG'),
], "Bình Dương ngập sâu")

# Rec 3146: nhiều tuyến đường tại Bình Dương ngập sâu
add_rev(3146, "Cơn mưa lớn khiến nhiều tuyến đường tại Bình Dương ngập sâu .", [
    ([6, 7], [8, 9], 'NEG'),
], "Bình Dương ngập sâu")

# Rec 3148: ngập nước trong cơn mưa lớn ở Bình Dương
add_rev(3148, "Tối 13 / 9 , một phụ nữ điều khiển xe ô tô trên đường đang bị ngập nước trong cơn mưa lớn ở Bình Dương và bị nước cuốn trôi", [
    ([14, 15], [22, 23], 'NEG'),
], "Bình Dương ngập nước")

# Rec 3149: Thuận An , Bình Dương Cách Mạng Tháng Tám ngập
add_rev(3149, "Thuận An , Bình Dương cứ tưởng Vũng Tàu 😟 😟 Ngay lúc này , đêm 7 / 11 , thuỷ triều dâng làm ngập 1 đoạn Cách Mạng Tháng Tám ( đoạn Cầu Ngang )", [
    ([0, 1], [17], 'NEG'),
    ([3, 4], [17], 'NEG'),
    ([21, 22, 23, 24], [17], 'NEG'),
    ([27, 28], [17], 'NEG'),
], "Thuận An, Bình Dương, Cách Mạng Tháng Tám ngập")

# Rec 3150: Cầu Ông Bố ( QL13 , Thuận An , Bình Dương ) nước vẫn còn ngập khá cao
add_rev(3150, "Đoạn Lotte và Cầu Ông Bố ( QL13 , Thuận An , Bình Dương ) nước vẫn còn ngập khá cao , kẹt xe kéo dài .", [
    ([3, 4, 5], [15, 16, 17, 18], 'NEG'),
    ([7], [15, 16, 17, 18], 'NEG'),
    ([9, 10], [15, 16, 17, 18], 'NEG'),
    ([12, 13], [15, 16, 17, 18], 'NEG'),
], "Cầu Ông Bố, QL13, Thuận An ngập khá cao")

# Rec 3152: Thuận An , Bình Dương ngập úng kéo dài
add_rev(3152, "Thuận An , Bình Dương , khổ sở với ngập úng kéo dài 4 năm .", [
    ([0, 1], [6, 7], 'NEG'),
    ([3, 4], [6, 7], 'NEG'),
], "Thuận An, Bình Dương ngập úng")

# Rec 3154: đường CMT8 , đoạn Cầu Ngang , Thuận An nước ngập
add_rev(3154, "Ngay lúc này 🆘 Thuỷ triều dâng , làm nước ngập trên đường CMT8 , đoạn Cầu Ngang , Hưng định , Thuận An , Bình Dương cũ .", [
    ([10, 11], [6, 7], 'NEG'),
    ([14, 15], [6, 7], 'NEG'),
    ([19, 20], [6, 7], 'NEG'),
    ([22, 23], [6, 7], 'NEG'),
], "đường CMT8, Cầu Ngang ngập")

# Rec 3156: Đường Trần Tử Bình x Lý Thường Kiệt , Thủ Dầu Một , Bình Dương triều cường gây ngập nặng
add_rev(3156, "Đường Trần Tử Bình x Lý Thường Kiệt , Thủ Dầu Một , Bình Dương ngay lúc này 😥 😥 😥 - - - - Đợt triều cường dâng vào giữa tháng 10 , nước ngập sâu", [
    ([0, 1, 2, 3], [32, 33], 'NEG'),
    ([5, 6, 7], [32, 33], 'NEG'),
    ([9, 10, 11], [32, 33], 'NEG'),
    ([13, 14], [32, 33], 'NEG'),
], "Đường Trần Tử Bình, Thủ Dầu Một ngập sâu")

# Rec 3157: vùng ngập ở đoạn cầu Quan - Bến Cát , Bình Dương
add_rev(3157, "Cảnh người dân đi học , đi làm trễ sáng nay vì không qua được vùng ngập ở đoạn cầu Quan - Bến Cát , Bình Dương .", [
    ([18, 19], [15], 'NEG'),
    ([21, 22], [15], 'NEG'),
    ([24, 25], [15], 'NEG'),
], "cầu Quan, Bến Cát, Bình Dương ngập")

# Rec 3159: Ngập ở khu vực trung tâm Bình Dương Cách Mạng Tháng Tám ( cầu ông Đành ) , Thích Quảng Đức
add_rev(3159, "Ngập ở khu vực trung tâm Bình Dương ngay lúc này 😟 Triều cường dâng , loạt tuyến đường như Cách Mạng Tháng Tám ( cầu ông Đành ) , Thích Quảng Đức (", [
    ([5, 6], [0], 'NEG'),
    ([15, 16, 17, 18], [0], 'NEG'),
    ([20, 21, 22], [0], 'NEG'),
    ([25, 26, 27], [0], 'NEG'),
], "Bình Dương, Cách Mạng Tháng Tám, Thích Quảng Đức Ngập")

# Rec 3163: ngã 3 Cống Thích Quảng Đức , Thủ Dầu Một Mưa ngập
add_rev(3163, "Thủ Dầu Một , Mưa ngập ngay lúc này ở ngã 3 Cống Thích Quảng Đức , Thủ Dầu Một , Bình Dương .", [
    ([0, 1, 2], [4, 5], 'NEG'),
    ([10, 11, 12, 13, 14, 15], [4, 5], 'NEG'),
    ([17, 18, 19], [4, 5], 'NEG'),
    ([21, 22], [4, 5], 'NEG'),
], "ngã 3 Cống Thích Quảng Đức Mưa ngập")

# Rec 3165: gây ngập chợ Bình Dương và ngã 6 đến cầu Ông Đành
add_rev(3165, "Tối nay ⛔ Thủy Triều dâng cao gây ngập chợ Bình Dương và ngã 6 đến cầu Ông Đành .", [
    ([8, 9, 10], [6], 'NEG'),
    ([12, 13], [6], 'NEG'),
    ([15, 16, 17], [6], 'NEG'),
], "chợ Bình Dương, ngã 6, cầu Ông Đành ngập")

# Rec 3166: Mực nước đo được là 1 , 85m tại trạm Thủ Dầu Một , cao hơn báo động 3
add_rev(3166, "Mực nước đo được là 1 , 85m tại trạm Thủ Dầu Một , cao hơn báo động 3 .", [
    ([10, 11, 12, 13], [15, 16, 17, 18], 'NEU'),
], "trạm Thủ Dầu Một cao hơn báo động 3")

# Rec 3167: Chợ Bình Dương nước ngập khiến nhiều xe chết máy
add_rev(3167, "Chợ Bình Dương tối nay và những ngày gần đây nước ngập khiến nhiều xe chết máy .", [
    ([0, 1, 2], [9], 'NEG'),
    ([0, 1, 2], [13, 14], 'NEG'),
], "Chợ Bình Dương nước ngập, chết máy")

# Rec 3171: BÌNH DƯƠNG CHIỀU NAY PHỐ CŨNG NHƯ SÔNG đường Thích Quảng Đức ngập sâu
add_rev(3171, "BÌNH DƯƠNG CHIỀU NAY PHỐ CŨNG NHƯ SÔNG 😢 Khoảng 17h chiều nay ( 13 / 10 ) , cơn mưa lớn bất ngờ đổ xuống nhiều nơi ở Bình Dương khiến đường Thích Quảng Đức ngập sâu", [
    ([0, 1], [4, 5, 6, 7], 'NEG'),
    ([26, 27], [32, 33], 'NEG'),
    ([30, 31, 32], [32, 33], 'NEG'),
], "BÌNH DƯƠNG PHỐ NHƯ SÔNG, đường Thích Quảng Đức ngập sâu")

# Rec 3172: Thủ Dầu Một Đường Huỳnh Văn Lũy nước dâng cao ngập nửa xe
add_rev(3172, "Thủ Dầu Một Đoạn Đường Huỳnh Văn lũy ngay lúc này , Sau trận mưa lớn nước đã dâng cao ngập nửa xe máy , nhiều người phải dắt bộ", [
    ([0, 1, 2], [15, 16, 17], 'NEG'),
    ([4, 5, 6, 7], [15, 16, 17], 'NEG'),
], "Thủ Dầu Một, Đường Huỳnh Văn Lũy ngập nửa xe")

# Rec 3173: nước chảy như thác cuốn trôi xe máy ở Bình Dương
add_rev(3173, "Mưa như trút , nước chảy như thác cuốn trôi xe máy ở Bình Dương TPO - Cơn mưa lớn kèm sấm sét chiều nay ( 24 / 5 ) khiến nhiều tuyến đường ở Bình Dương ngập sâu", [
    ([11, 12], [4, 5, 6, 7], 'NEG'),
    ([28, 29], [30, 31], 'NEG'),
], "Bình Dương nước chảy như thác, ngập sâu")

# Rec 3174: xe máy đậu trên lề cũng bị ngập nặng ở Mỹ Phước 2 ( Bến Cát )
add_rev(3174, "Sau loạt ôtô trôi lềnh đềnh , thì xe máy đậu trên lề cũng bị ngập nặng trong cơn mưa ở Mỹ Phước 2 ( Bến Cát )", [
    ([20, 21, 22], [12, 13], 'NEG'),
    ([24, 25], [12, 13], 'NEG'),
], "Mỹ Phước 2, Bến Cát ngập nặng")

# Rec 3175: Bình Dương : Mưa ngập ở 2 thành phố
add_rev(3175, "Bình Dương : Mưa ngập ở 2 thành phố , giao thông tắc nghẽn Đến 19 giờ ngày 1 . 9 . 2024 , nhiều điểm ngập ở TP Dĩ An và TP Thuận An", [
    ([0, 1], [3, 4], 'NEG'),
    ([27, 28, 29], [24, 25], 'NEG'),
    ([31, 32, 33], [24, 25], 'NEG'),
], "Bình Dương Mưa ngập, TP Dĩ An, TP Thuận An ngập")

# Rec 3177: VŨNG TÀU NGẬP BANH CHÀNH
add_rev(3177, "Cơn mưa ngang qua VŨNG TÀU NGẬP BANH CHÀNH / BANH TA LÔNG Chỗ bạn sao rồi", [
    ([4, 5], [6, 7, 8], 'NEG'),
], "VŨNG TÀU NGẬP BANH CHÀNH")

# Rec 3178: nhiều tuyến đường Vũng Tàu ngập sâu
add_rev(3178, "Mưa lớn đầu mùa , nhiều tuyến đường Vũng Tàu ngập sâu Ảnh : Kha Lu", [
    ([8, 9], [10, 11], 'NEG'),
], "Vũng Tàu ngập sâu")

# Rec 3179: nhiều tuyến đường Vũng Tàu ngập sâu
add_rev(3179, "Mưa lớn đầu mùa , nhiều tuyến đường Vũng Tàu ngập sâu", [
    ([8, 9], [10, 11], 'NEG'),
], "Vũng Tàu ngập sâu")

# Rec 3181: Ngập nặng ở Thi Sách - Vũng Tàu
add_rev(3181, "Ngập nặng ở Thi Sách - Vũng Tàu Video : Trần Phúc Hậu", [
    ([4, 5], [0, 1], 'NEG'),
    ([7, 8], [0, 1], 'NEG'),
], "Thi Sách, Vũng Tàu Ngập nặng")

# Rec 3182: nhiều tuyến đường ở Vũng Tàu ngập sâu
add_rev(3182, "Hàng loạt phương tiện chết máy trong cơn mưa lớn ở Vũng Tàu tối 22 / 5 Tối 22 / 5 , cơn mưa lớn kéo dài khoảng 2 tiếng đồng hồ khiến các tuyến đường ở Vũng Tàu ngập sâu", [
    ([11, 12], [2, 3], 'NEG'),
    ([32, 33], [34, 35], 'NEG'),
], "Vũng Tàu chết máy, ngập sâu")

# Rec 3183: nhiều tuyến đường Vũng Tàu ngập sâu
add_rev(3183, "Mưa lớn đầu mùa , nhiều tuyến đường Vũng Tàu ngập sâu Ngày 7 / 6 , trận mưa lớn kéo dài khoảng 3 giờ đồng hồ khiến nhiều tuyến đường ở trung tâm TP Vũng Tàu ngập nặng", [
    ([8, 9], [10, 11], 'NEG'),
    ([32, 33, 34], [35, 36], 'NEG'),
], "Vũng Tàu ngập sâu, ngập nặng")

# Rec 3184: NHIỀU TUYẾN ĐƯỜNG TRUNG TÂM KHU VỰC VŨNG TÀU NGẬP SAU MƯA !
add_rev(3184, "💦 NHIỀU TUYẾN ĐƯỜNG TRUNG TÂM KHU VỰC VŨNG TÀU NGẬP SAU MƯA !", [
    ([6, 7], [8], 'NEG'),
], "VŨNG TÀU NGẬP")

# Rec 3186: 14 TUYẾN ĐƯỜNG NGẬP SÂU KHI MƯA LỚN TẠI VŨNG TÀU .
add_rev(3186, "📍 14 TUYẾN ĐƯỜNG NGẬP SÂU KHI MƯA LỚN TẠI VŨNG TÀU .", [
    ([10, 11], [4, 5], 'NEG'),
], "VŨNG TÀU NGẬP SÂU")

# Rec 3187: TÌNH HÌNH NGẬP LỤT SẮP TỚI TẠI BÀ RỊA
add_rev(3187, "TÌNH HÌNH NGẬP LỤT SẮP TỚI TẠI BÀ RỊA .", [
    ([6, 7], [2, 3], 'NEU'),
], "BÀ RỊA NGẬP LỤT dự báo")

# Rec 3191: chợ Bình Dương Đường ngập bà con xin đừng cố chạy qua
add_rev(3191, "Đường ở chợ Bình Dương gần đây cứ như ' Vũng Tàu ' 🫣 Đường ngập bà con xin đừng cố chạy qua .", [
    ([3, 4, 5], [13], 'NEG'),
], "chợ Bình Dương ngập")

# Rec 3194: Vũng Tàu Ngập ngang bụng đường 30 / 4
add_rev(3194, "Không ngờ có ngày Vũng Tàu gặp cảnh này . Ngập ngang bụng luôn 🥲 🥲 Note : đoạn ngã tư Vietso Petro đường 30 / 4", [
    ([4, 5], [10, 11, 12], 'NEG'),
    ([21, 22, 23, 24], [10, 11, 12], 'NEG'),
], "Vũng Tàu, đường 30 / 4 Ngập ngang bụng")

# Rec 3195: Đường 30 / 4 khu vực cảng Vietso ngập nặng
add_rev(3195, "Đường 30 / 4 khu vực cảng Vietso ngập nặng , mọi người nên chọn hướng đi khác", [
    ([0, 1, 2, 3], [8, 9], 'NEG'),
], "Đường 30 / 4 ngập nặng")

# Rec 3197: Bến Cát , Bình Dương Mưa lớn ngập sâu
add_rev(3197, "Mưa lớn ngập sâu ở Bến Cát , Bình Dương Không cần đi chữa lành , ở đây vừa lành và lạnh luôn 🐧", [
    ([5, 6], [2, 3], 'NEG'),
    ([8, 9], [2, 3], 'NEG'),
], "Bến Cát, Bình Dương ngập sâu")

# Rec 3198: Đường Bà Rịa – Châu Pha ngập nước
add_rev(3198, "Đường Bà Rịa – Châu Pha đoạn thi công cầu vượt km 49 + 900 ngập nước vì trời mưa", [
    ([0, 1, 2, 3, 4], [13, 14], 'NEG'),
], "Đường Bà Rịa – Châu Pha ngập nước")

# Rec 3202: Bình Dương : Mưa lớn gây ngập ở 2 thành phố
add_rev(3202, "Bình Dương : Mưa lớn gây ngập ở 2 thành phố , giao thông ùn tắc ⛈ ⛈ ⛈", [
    ([0, 1], [5], 'NEG'),
], "Bình Dương ngập")

# Rec 3448: Quốc lộ 13 , Tp Thuận An , Bình Dương ngập sâu
add_rev(3448, "Cơn mưa như trút từ trưa đến chiều nay 16 - 4 khiến tuyến đường Quốc lộ 13 , Tp Thuận An , Bình Dương ( giáp phường Hiệp Bình Phước ) ngập sâu trong biển nước", [
    ([16, 17, 18], [30, 31], 'NEG'),
    ([20, 21, 22], [30, 31], 'NEG'),
    ([24, 25], [30, 31], 'NEG'),
], "Quốc lộ 13, Tp Thuận An, Bình Dương ngập sâu")

# Rec 3450: Quốc lộ 13 đoạn qua thị xã Thuận An ngập nặng
add_rev(3450, "Quốc lộ 13 đoạn qua thị xã Thuận An ngập nặng , hàng ngàn phương tiện \" chìm sâu \" trong nước .", [
    ([0, 1, 2], [7, 8], 'NEG'),
    ([5, 6, 7], [7, 8], 'NEG'),
], "Quốc lộ 13 ngập nặng")

# Rec 3451: vùng ngập nước ở cầu Quan , Bến Cát Bình Dương
add_rev(3451, "Trạm CSGT Quốc Lộ 13 phát hiện dùng xe thùng chở người dân qua vùng ngập nước ở cầu Quan , Bến Cát Bình Dương sáng nay .", [
    ([17, 18], [14, 15], 'NEG'),
    ([20, 21], [14, 15], 'NEG'),
    ([22, 23], [14, 15], 'NEG'),
], "cầu Quan, Bến Cát, Bình Dương ngập nước")

# Rec 3452: QL13 hướng 2 chiều từ cây Xăng số 4 đến Lotte Bình Dương đang ùn tắc giao thông do ngập
add_rev(3452, "Hiện tại QL13 hướng 2 chiều từ cây Xăng số 4 đến Lotte Bình Dương đang ùn tắc giao thông do ngập", [
    ([2], [18], 'NEG'),
    ([12, 13], [18], 'NEG'),
], "QL13, Bình Dương ngập")

# Rec 3472: Bình Dương mưa lớn khiến đường ngập nhiều nơi
add_rev(3472, "Bình Dương mưa lớn ngay lúc này ❌ ghi nhận mưa lớn khiến đường ngập nhiều nơi , đúng lúc mọi người tan ca về", [
    ([0, 1], [11], 'NEG'),
], "Bình Dương đường ngập")

# Rec 3487: Triều cường trên sông Sài Gòn vượt báo động III gây ngập nhiều tuyến đường ở Bình Dương
add_rev(3487, "🛑 Triều cường trên sông Sài Gòn vượt báo động III gây ngập nhiều tuyến đường ở Bình Dương tối nay 18 / 10", [
    ([17, 18], [9], 'NEG'),
    ([4, 5, 6], [9], 'NEG'),
], "Bình Dương, sông Sài Gòn ngập")

# Rec 3505: trạm Thủ Dầu Một ở mức cao
add_rev(3505, "Đỉnh triều cao nhất ngày ở mức xấp xỉ hoặc trên báo động 2 sẽ duy trì đến hết ngày 26 và 27 - 11 , riêng trạm Thủ Dầu Một ở mức cao", [
    ([27, 28, 29, 30], [32, 33], 'NEU'),
], "trạm Thủ Dầu Một ở mức cao")

# Rec 3657: Bình Dương gặp nước ngập
add_rev(3657, "\" Tôi vừa tan ca làm trong công trình xây dựng dưới Bình Dương chạy về đến đây thì gặp nước ngập , xe tôi bị chết máy , phải dắt bộ hơn 2km rồi \"", [
    ([12, 13], [20, 21], 'NEG'),
], "Bình Dương nước ngập")

# ==============================================================================
# NHÓM 2: TỪ NGỮ DÂN DÃ / CHÂM CHỌC / CHÂM BIẾM VỀ NGẬP LỤT ĐỜI THƯỜNG
# ==============================================================================

# Rec 42: Sài Gòn đặc sản mưa ngâu Phố phường ngập nước
add_rev(42, "Sài Gòn đặc sản mưa ngâu Phố phường ngập nước , người đâu đi về ! Xe nằm đường , đứng tái tê Nhích từng chút một , dầm dề dưới mưa .", [
    ([0, 1], [6, 7], 'NEG'),
], "Sài Gòn ngập nước")

# Rec 317: Dạo này chiều nào Sài Gòn cũng đổ mưa lớn , phố xá biến thành sông , khiến bao chiến mã rơi vào cảnh chết máy
add_rev(317, "🌧 ️ MƯA LỚN , NGẬP SÂU NGƯỜI ĐI XE MÁY CẦN LƯU Ý GÌ ? 💦 Dạo này chiều nào Sài Gòn cũng đổ mưa lớn , phố xá biến thành sông , khiến bao chiến mã rơi vào cảnh chết máy", [
    ([21, 22], [28, 29, 30, 31], 'NEG'),
    ([21, 22], [40, 41], 'NEG'),
], "Sài Gòn phố xá biến thành sông, chết máy")

# Rec 338: SÀI GÒN MÙA NÀY … KHÔNG CẦN ĐI BIỂN ! Mưa xuống một trận , đường phố TP. HCM lập tức biến thành sông
add_rev(338, "SÀI GÒN MÙA NÀY … KHÔNG CẦN ĐI BIỂN ! Mưa xuống một trận , đường phố TP. HCM lập tức biến thành sông", [
    ([0, 1], [21, 22, 23], 'NEG'),
    ([16, 17], [21, 22, 23], 'NEG'),
], "SÀI GÒN, TP. HCM biến thành sông")

# Rec 374: Sài Gòn " thất thủ " sau cơn mưa lớn , phương tiện trục trặc , nước tràn vào nhà dân
add_rev(374, "Sài Gòn \" thất thủ \" sau cơn mưa lớn , phương tiện trục trặc , nước tràn vào nhà dân", [
    ([0, 1], [2, 3], 'NEG'),
    ([0, 1], [14, 15, 16, 17], 'NEG'),
], "Sài Gòn thất thủ, nước tràn vào nhà")

# Rec 401: CV Làng Hoa Gò Vấp Công Viên Nước Gò Vấp mùa ngập chơi nước mưa
add_rev(401, "CV Làng Hoa Gò Vấp biến thành Công Viên Nước Gò Vấp , mùa ngập chơi nước mưa nước cống", [
    ([0, 1, 2, 3, 4], [11], 'NEG'),
], "CV Làng Hoa Gò Vấp ngập")

# Rec 437: Bãi sau Gò Vấp - Ngã ➕ Lê Văn Thọ - Nguyễn Văn Khối Gò Vấp
add_rev(437, "Bãi sau Gò Vấp - Ngã ➕ Lê Văn Thọ - Nguyễn Văn Khối Gò Vấp # mưa # ngập # bơi # hưxe # xuhuong # reels # đặcsản", [
    ([6, 7, 8], [15], 'NEG'),
    ([10, 11, 12], [15], 'NEG'),
    ([13, 14], [15], 'NEG'),
], "Lê Văn Thọ, Nguyễn Văn Khối, Gò Vấp ngập")

# Rec 439: Bãi sau Gò Vấp - Ngã ➕ Lê Văn Thọ - Nguyễn Văn Khối Gò Vấp
add_rev(439, "Bãi sau Gò Vấp - Ngã ➕ Lê Văn Thọ - Nguyễn Văn Khối Gò Vấp # mưa # ngập # bơi # hưxe # xuhuong # reels # đặcsản", [
    ([6, 7, 8], [15], 'NEG'),
    ([10, 11, 12], [15], 'NEG'),
    ([13, 14], [15], 'NEG'),
], "Lê Văn Thọ, Nguyễn Văn Khối, Gò Vấp ngập")

# Rec 606: TP. HCM cứ mỗi khi mưa lại ngập , đường phố biến thành sông , nhà dân thì chìm trong biển nước
add_rev(606, "TP. HCM cứ mỗi khi mưa lại ngập , đường phố biến thành sông , nhà dân thì chìm trong biển nước .", [
    ([0, 1], [6], 'NEG'),
    ([0, 1], [10, 11, 12], 'NEG'),
    ([0, 1], [17, 18, 19, 20], 'NEG'),
], "TP. HCM ngập, biến thành sông, chìm trong biển nước")

# Rec 701: Biển nước tại đoạn Lê Văn Lương - Tố Hữu .
add_rev(701, "Biển nước tại đoạn Lê Văn Lương - Tố Hữu .", [
    ([4, 5, 6], [0, 1], 'NEG'),
    ([8, 9], [0, 1], 'NEG'),
], "Lê Văn Lương, Tố Hữu Biển nước")

# Rec 739: Bãi sau Sài Gòn quê tôi mùa nước lũ
add_rev(739, "Bãi sau Sài Gòn quê tôi mùa nước lũ # mưa # ngập # mưagióbãobùng # vungtau # sàigòn", [
    ([2, 3], [6, 7], 'NEG'),
], "Sài Gòn nước lũ")

# Rec 774: Sài Gòn thất thủ , nước ngập mênh mông
add_rev(774, "Sài Gòn thất thủ , nước ngập mênh mông mà anh Tăng Phúc bắt fan đặt báo thức", [
    ([0, 1], [2], 'NEG'),
    ([0, 1], [5, 6], 'NEG'),
], "Sài Gòn thất thủ, nước ngập mênh mông")

# Rec 2509: Tại TPHCM , Có nơi lượng mưa lên tới 290 - 330 mm , khiến nước thoát chậm , nhiều tuyến đường ngập sâu
add_rev(2509, "Tại TPHCM , Có nơi lượng mưa lên tới 290 - 330 mm , khiến nước thoát chậm , nhiều tuyến đường ngập sâu", [
    ([1], [14, 15], 'NEG'),
    ([1], [20, 21], 'NEG'),
], "TPHCM thoát chậm, ngập sâu")

# ==============================================================================
# NHÓM 3: HIỆU CHỈNH CHUYÊN SÂU LÔ 11 - 14 (RECORDS 1001 ĐẾN 1400)
# ==============================================================================

# Rec 1011: Siêu dự án chống ngập của TP. HCM ... gồm 6 cống ngăn triều : Cây Khô , Mương Chuối , Phú Xuân , Bến Nghé , Tân Thuận và Phú Định .
add_rev(1011, "Siêu dự án chống ngập của TP. HCM khởi công năm 2016 theo hình thức BT , gồm 6 cống ngăn triều : Cây Khô , Mương Chuối , Phú Xuân , Bến Nghé , Tân Thuận và Phú Định .", [
    ([24, 25], [2, 3], 'POS'),
    ([27, 28], [2, 3], 'POS'),
    ([30, 31], [2, 3], 'POS'),
    ([33, 34], [2, 3], 'POS'),
    ([36, 37], [2, 3], 'POS'),
    ([39, 40], [2, 3], 'POS'),
], "6 cống ngăn triều chống ngập POS")

# Rec 1035: Dự án Giải quyết ngập do triều khu vực Thành phố Hồ Chí Minh ... gồm 6 cống ngăn triều : Bến Nghé , Cây Khô , Mương Chuối , Phú Định , Phú Xuân , Tân Thuận
add_rev(1035, "Dự án Giải quyết ngập do triều khu vực Thành phố Hồ Chí Minh gồm 6 cống ngăn triều : Bến Nghé , Cây Khô , Mương Chuối , Phú Định , Phú Xuân , Tân Thuận", [
    ([19, 20], [2, 3], 'POS'),
    ([22, 23], [2, 3], 'POS'),
    ([25, 26], [2, 3], 'POS'),
    ([28, 29], [2, 3], 'POS'),
    ([31, 32], [2, 3], 'POS'),
    ([34, 35], [2, 3], 'POS'),
], "6 cống ngăn triều giải quyết ngập POS")

# Rec 1041: Bao giờ TPHCM hết ngập ?
add_rev(1041, "Bao giờ TPHCM hết ngập ?", [
    ([2], [3, 4], 'NEU'),
], "TPHCM hết ngập hỏi thăm dò NEU")

# Rec 1046: tuyến đường được thảm nhựa , cảnh quan thông thoáng hơn .
add_rev(1046, "Tại TPHCM , Tuyến đường dẫn vào cống đã được chỉnh trang , thảm nhựa , cảnh quan thông thoáng hơn .", [
    ([1], [15, 16], 'POS'),
], "TPHCM thông thoáng hơn POS")

# Rec 1054: Tại TPHCM , Nay khô ráo , nước hết ngập rồi ạ
add_rev(1054, "Tại TPHCM , Nay khô ráo , nước hết ngập rồi ạ 😜", [
    ([1], [4, 5], 'POS'),
    ([1], [8, 9], 'POS'),
], "TPHCM khô ráo, hết ngập POS")

# Rec 1068: Triều cường đạt đỉnh , gây ngập nặng ở TP. HCM
add_rev(1068, "Triều cường ở TPHCM đạt đỉnh , gây ngập nặng ở TP. HCM vào ngày nào ?", [
    ([0, 1, 2, 3], [4, 5], 'NEU'),
    ([10, 11], [7, 8], 'NEU'),
], "triều cường ở TPHCM đạt đỉnh, TP. HCM ngập nặng NEU")

# Rec 1097: Dân Sài Gòn than trời khi nào mới hết ngập ?
add_rev(1097, "Dân Sài Gòn than trời khi nào mới hết ngập ?", [
    ([1, 2], [6, 7], 'NEU'),
], "Sài Gòn hết ngập hỏi thăm dò NEU")

# Rec 1098: TP. HCM : Đường Trần Xuân Soạn , bán đảo Thanh Đa sẽ hết ngập do triều cường ?
add_rev(1098, "TP. HCM : Đường Trần Xuân Soạn , bán đảo Thanh Đa sẽ hết ngập do triều cường ?", [
    ([3, 4, 5, 6], [12, 13], 'NEU'),
    ([8, 9, 10, 11], [12, 13], 'NEU'),
], "Đường Trần Xuân Soạn, bán đảo Thanh Đa hết ngập NEU")

# Rec 1119: hầm chui này bị ngập
add_rev(1119, "Tại TPHCM , Đây là lần thứ hai hầm chui này bị ngập kể từ khi thông xe hồi tháng 2 .", [
    ([1], [11], 'NEG'),
], "TPHCM hầm chui ngập NEG")

print(f"Tổng số revisions đã định nghĩa: {len(REVISED_RECORDS)}")
