# -*- coding: utf-8 -*-
"""
Script áp dụng toàn bộ các bản ghi khôi phục & hiệu chỉnh cho Phase 3:
- Bình Dương & Vũng Tàu (Đô thị sáp nhập / giáp ranh)
- Từ ngữ Dân dã / Châm chọc về ngập lụt
- Lô 11 - 14 (Records 1001 đến 1400)
Sử dụng span_helper để tính toán và kiểm tra Span Index tự động 100% chuẩn xác.
"""

import sys, os, ast
sys.path.insert(0, os.path.abspath('.'))
from scripts.span_helper import make_triplet

raw_revisions = [
    # ==============================================================================
    # NHÓM 1: BÌNH DƯƠNG & VŨNG TÀU (KHÔI PHỤC VÀ GÁN NHÃN ĐÚNG QUY CHUẨN)
    # ==============================================================================
    (63, "Bãi sau Sài Gòn mùa mưa lũ nhé 😎 😎 😎 # tphcm # vungtau # mưa # mưagióbãobùng # ngập", [
        ("Sài Gòn", "mùa mưa lũ", "NEG")
    ]),

    (210, "159 điểm ngập thường xuyên tại TP. HCM ( gồm TP. HCM cũ , Bình Dương cũ , Bà Rịa - Vũng Tàu cũ ) · TP. HCM cũ : 76 điểm . Trung tâm : 39 điểm", [
        ("TP. HCM", "điểm ngập thường xuyên", "NEU"),
        ("Bình Dương", "điểm ngập thường xuyên", "NEU"),
        ("Bà Rịa - Vũng Tàu", "điểm ngập thường xuyên", "NEU")
    ]),

    (256, "Anh em Tphcm cũ và sau sáp nhập update khu vực nào ko ngập sau mấy trận mưa lớn ạ ! Em trc : 1 / Đông Hòa Quốc lộ 1k ( Dĩ An , Bình Dương ) : ngập nhẹ", [
        ("Quốc lộ 1k", "ngập nhẹ", "NEG"),
        ("Dĩ An", "ngập nhẹ", "NEG"),
        ("Bình Dương", "ngập nhẹ", "NEG")
    ]),

    (399, "Bình Dương tiếp tục giữ chuỗi \" hồi chiều trời mưa \" CSGT cảnh báo 122 điểm ngập ở TPHCM bao gồm khu vực Vũng Tàu", [
        ("Bình Dương", "122 điểm ngập", "NEU"),
        ("TPHCM", "122 điểm ngập", "NEU"),
        ("Vũng Tàu", "122 điểm ngập", "NEU")
    ]),

    (467, "Dĩ An mưa to quá nè bà con cập nhật tình hình ngập đi", [
        ("Dĩ An", "ngập", "NEU")
    ]),

    (485, "Bình Dương ngập sâu sau mưa lớn , lực lượng chức năng rất nhanh đã giải cứu nhiều người dân bị cô lập trong vùng ngập", [
        ("Bình Dương", "ngập sâu", "NEG")
    ]),

    (493, "Mưa lớn sáng 23 / 10 khiến nhiều khu dân cư ở phường Bến Cát ngập sâu , có nơi nước dâng gần 2 m , lực lượng chức năng phải dùng dây thừng hỗ trợ hơn 120 người đến nơi an toàn .", [
        ("phường Bến Cát", "ngập sâu", "NEG")
    ]),

    (502, "Tối 23 / 10 , nhiều tuyến đường gần sông Sài Gòn , thuộc phường Thủ Dầu Một ( TPHCM ) , bất ngờ bị ngập sâu , khiến phương tiện và người dân không thể lưu thông", [
        ("phường Thủ Dầu Một", "ngập sâu", "NEG")
    ]),

    (508, "Hiện mực nước sông Sài Gòn đang dâng cao , gây ngập 1 số nơi như Chánh Mỹ , chợ Thủ Dầu Một , bờ kè Bưng Cải , An Sơn , Quốc Lộ 13", [
        ("Chánh Mỹ", "ngập", "NEG"),
        ("chợ Thủ Dầu Một", "ngập", "NEG"),
        ("bờ kè Bưng Cải", "ngập", "NEG"),
        ("An Sơn", "ngập", "NEG"),
        ("Quốc Lộ 13", "ngập", "NEG")
    ]),

    (509, "Sáng sớm 18 / 9 , ở tỉnh Bình Dương đã có mưa kéo dài . Theo dự báo , mưa kết hợp với triều cường có thể gây ngập úng tại các vùng hạ du ven sông Sài Gòn .", [
        ("Bình Dương", "có thể gây ngập úng", "NEU"),
        ("sông Sài Gòn", "có thể gây ngập úng", "NEU")
    ]),

    (600, "Sau cơn mưa lớn nhiều nơi ở khu vực Bến Cát - Bàu Bàng ( Bình Dương cũ ) bị ngập sâu , lực lượng cứu hộ TP HCM kịp thời đưa 127 người đến nơi an toàn", [
        ("Bến Cát", "ngập sâu", "NEG"),
        ("Bàu Bàng", "ngập sâu", "NEG"),
        ("Bình Dương", "ngập sâu", "NEG")
    ]),

    (715, "NHIỀU TUYẾN ĐƯỜNG TRUNG TÂM KHU VỰC VŨNG TÀU NGẬP SAU MƯA ! Tối 2 / 9 , một cơn mưa lớn kéo dài khiến các tuyến đường khu vực trung tâm Vũng Tàu ngập nặng", [
        ("VŨNG TÀU", "NGẬP", "NEG"),
        ("Vũng Tàu", "ngập nặng", "NEG")
    ]),

    (921, "Sáng sớm 18 / 9 , ở tỉnh Bình Dương đã có mưa kéo dài . Theo dự báo , mưa kết hợp với triều cường có thể gây ngập úng tại các vùng hạ du ven sông Sài Gòn .", [
        ("Bình Dương", "có thể gây ngập úng", "NEU"),
        ("sông Sài Gòn", "có thể gây ngập úng", "NEU")
    ]),

    (2050, "Bình Dương cũ có nhiều điểm ngập", [
        ("Bình Dương", "nhiều điểm ngập", "NEG")
    ]),

    (2159, "Nâng nền Quốc lộ 13 , nhà dân thấp gần 1m , nắng bụi mưa ngập Đoạn Quốc lộ 13 từ trạm thu phí Lái Thiêu đến cầu Vĩnh Bình đang được thi công", [
        ("Quốc lộ 13", "mưa ngập", "NEG")
    ]),

    (2301, "Cảnh báo 🆘 Mưa lớn , đang ngập đoạn Cách Mạng Tháng Tám từ vòng xoay chợ Lái Thiêu ( tua 18 ) đến trạm thu phí cầu Phú Long", [
        ("Cách Mạng Tháng Tám", "đang ngập", "NEG"),
        ("chợ Lái Thiêu", "đang ngập", "NEG")
    ]),

    (2303, "Cảnh báo ngay lúc này 🆘 ĐANG MƯA lớn , và ngập đoạn Cách Mạng Tháng Tám từ vòng xoay chợ Lái Thiêu ( tua 18 ) đến trạm thu phí cầu Phú Long", [
        ("Cách Mạng Tháng Tám", "ngập", "NEG"),
        ("chợ Lái Thiêu", "ngập", "NEG")
    ]),

    (2417, "Bình Dương mưa ngập lối về", [
        ("Bình Dương", "mưa ngập", "NEG")
    ]),

    (2418, "trận mưa sáng sớm nay khiến đường tạo lực bắc tân uyên ngập sâu # xuhuongtiktok # bdsminhhung # xuhuong # xuhuong2026", [
        ("đường tạo lực bắc tân uyên", "ngập sâu", "NEG")
    ]),

    (2443, "Mưa lớn gây ngập nhiều tuyến đường tại phường Thủ Dầu Một ( TPHCM ) , giao thông bị ảnh hưởng nghiêm trọng .", [
        ("phường Thủ Dầu Một", "ngập", "NEG")
    ]),

    (2522, "159 điểm ngập thường xuyên tại TP. HCM ( gồm TP. HCM cũ , Bình Dương cũ , Bà Rịa - Vũng Tàu cũ ) · TP. HCM cũ : 76 điểm .", [
        ("TP. HCM", "điểm ngập thường xuyên", "NEU"),
        ("Bình Dương", "điểm ngập thường xuyên", "NEU"),
        ("Bà Rịa - Vũng Tàu", "điểm ngập thường xuyên", "NEU")
    ]),

    (2551, "🆘 Cảnh báo khẩn giữa đêm , nước cuồn cuồn tràn về đoạn cầu Khánh Vân ( Tân Uyên , Bình Dương cũ ) Nước từ đâu chưa rõ dồn dập đổ về", [
        ("cầu Khánh Vân", "nước cuồn cuồn tràn về", "NEG"),
        ("Tân Uyên", "nước cuồn cuồn tràn về", "NEG")
    ]),

    (2552, "Khẩn 🆘 Cảnh báo giữa đêm , nước cuồn cuồn tràn về đoạn cầu Khánh Vân ( Tân Uyên , Bình Dương cũ ) Nước từ đâu chưa rõ dồn dập đổ về", [
        ("cầu Khánh Vân", "nước cuồn cuồn tràn về", "NEG"),
        ("Tân Uyên", "nước cuồn cuồn tràn về", "NEG")
    ]),

    (2553, "Cập nhật ngay lúc này 🆘 2h sáng , lực lượng chức năng phường Tân Khánh ( Tân Uyên , Bình Dương cũ ) đã có mặt tại điểm ngập sâu cầu Khánh Vân", [
        ("cầu Khánh Vân", "ngập sâu", "NEG"),
        ("Tân Uyên", "ngập sâu", "NEG")
    ]),

    (2667, "mưa ngập kiểu này chỉ có dĩ an bình dương thôi kk 🤣 giờ làm mòi gì nhậu anh em 🤣", [
        ("dĩ an bình dương", "mưa ngập", "NEG")
    ]),

    (2770, "Mọi năm cứ triều cường lên rồi rút nhanh , còn năm nay thì lên ối giời ơi luôn . nào là chợ BD , nào là c ôbg đành , Ngô Quyền", [
        ("chợ BD", "triều cường lên", "NEG"),
        ("Ngô Quyền", "triều cường lên", "NEG")
    ]),

    (2771, "Bình Dương lại mưa ngập nữa rồi", [
        ("Bình Dương", "mưa ngập", "NEG")
    ]),

    (2778, "Đài KTTV Nam bộ dự báo triều cường có thể đạt 1 , 9 – 1 , 95m Thủ Dầu Một , vượt báo động 3 30 – 35cm , ngập .", [
        ("Thủ Dầu Một", "ngập", "NEU")
    ]),

    (2857, "kiếp nạn sinh nhật mùa mưa Thủ Dầu Một ngập lênh láng 🤣 🤣 # binhduongdidau # reviewbinhduong # binhduongangi", [
        ("Thủ Dầu Một", "ngập lênh láng", "NEG")
    ]),

    (2858, "Bình Dương sáng nay nhiều tuyến đường gần sông thuỷ triều dâng cao ngập cả mặt đường # reviewbinhduong # thu", [
        ("Bình Dương", "ngập cả mặt đường", "NEG")
    ]),

    (2967, "Tối nay ( 23 / 10 ) , nhiều tuyến đường gần sông Sài Gòn , thuộc phường Thủ Dầu Một ( TPHCM ) , bất ngờ bị ngập sâu , khiến phương tiện và người dân không thể lưu thông", [
        ("phường Thủ Dầu Một", "ngập sâu", "NEG")
    ]),

    (2988, "Hiện mực nước sông Sài Gòn đang dâng cao , gây ngập 1 số nơi như Chánh Mỹ , chợ Thủ Dầu Một , bờ kè Bưng Cải , An Sơn , Quốc Lộ 13", [
        ("Chánh Mỹ", "ngập", "NEG"),
        ("chợ Thủ Dầu Một", "ngập", "NEG"),
        ("bờ kè Bưng Cải", "ngập", "NEG"),
        ("An Sơn", "ngập", "NEG"),
        ("Quốc Lộ 13", "ngập", "NEG")
    ]),

    (3127, "Trung tâm Bình Dương ngay lúc này 😟 Triều cường dâng cao , loạt tuyến đường như Cách Mạng Tháng Tám ( cầu ông Đành ) , Ngô Quyền", [
        ("Bình Dương", "Triều cường dâng cao", "NEG"),
        ("Cách Mạng Tháng Tám", "Triều cường dâng cao", "NEG"),
        ("Ngô Quyền", "Triều cường dâng cao", "NEG")
    ]),

    (3132, "Nhiều nhà dân đã bị ngập nặng sau cơn mưa lớn sáng nay ở TP Dĩ An .", [
        ("TP Dĩ An", "ngập nặng", "NEG")
    ]),

    (3133, "quốc lộ 1K , khu vực Châu Thới tối nay Ngập mênh mông luôn , hiện CSGT đang điều tiết Tôi là dân Dĩ An TÔI L", [
        ("quốc lộ 1K", "Ngập mênh mông", "NEG"),
        ("Châu Thới", "Ngập mênh mông", "NEG"),
        ("Dĩ An", "Ngập mênh mông", "NEG")
    ]),

    (3134, "Bình Dương ❌ Khẩn trương đưa người dân ra khỏi nơi bị ngập sâu , nguy hiểm Sáng nay ngày 10 / 5 , trận mưa lớn kèm lốc xoáy quét qua", [
        ("Bình Dương", "ngập sâu", "NEG")
    ]),

    (3136, "‼ ️ DĨ AN - Nhiều tuyến đường đã ngập Hiện tại đường Nguyễn Tri Phương đang ngập sâu , có đoạn nước chảy như thác , bà con hạn chế", [
        ("DĨ AN", "ngập", "NEG"),
        ("đường Nguyễn Tri Phương", "ngập sâu", "NEG")
    ]),

    (3140, "BÌNH DƯƠNG : CÁC CHIẾN SĨ KHẨN TRƯƠNG DI DỜI NGƯỜI DÂN RA KHỎI NHỮNG NƠI NGẬP SÂU ‼ ️ Sáng nay ngày 10 / 5 , trận mưa lớn", [
        ("BÌNH DƯƠNG", "NGẬP SÂU", "NEG")
    ]),

    (3142, "Bình Dương : Mưa lớn cuốn trôi xe bán tải , nữ tài xế ra đi trong cống thoát nước 😥 😥 😥 Tối 13 / 9 , một phụ nữ điều khiển xe ô tô trên đường đang bị ngập nước trong cơn mưa lớn ở Bình Dương", [
        ("Bình Dương", "Mưa lớn", "NEG"),
        ("Bình Dương", "ngập nước", "NEG")
    ]),

    (3143, "Cơn mưa lớn đổ xuống cuối chiều nay khiến nhiều tuyến đường ở Bình Dương ngập sâu , xe máy bị nước cuốn , cây xanh gãy đổ . . .", [
        ("Bình Dương", "ngập sâu", "NEG")
    ]),

    (3146, "Cơn mưa lớn khiến nhiều tuyến đường tại Bình Dương ngập sâu .", [
        ("Bình Dương", "ngập sâu", "NEG")
    ]),

    (3148, "Tối 13 / 9 , một phụ nữ điều khiển xe ô tô trên đường đang bị ngập nước trong cơn mưa lớn ở Bình Dương và bị nước cuốn trôi", [
        ("Bình Dương", "ngập nước", "NEG")
    ]),

    (3149, "Thuận An , Bình Dương cứ tưởng Vũng Tàu 😟 😟 Ngay lúc này , đêm 7 / 11 , thuỷ triều dâng làm ngập 1 đoạn Cách Mạng Tháng Tám ( đoạn Cầu Ngang )", [
        ("Thuận An", "ngập", "NEG"),
        ("Bình Dương", "ngập", "NEG"),
        ("Cách Mạng Tháng Tám", "ngập", "NEG"),
        ("Cầu Ngang", "ngập", "NEG")
    ]),

    (3150, "Đoạn Lotte và Cầu Ông Bố ( QL13 , Thuận An , Bình Dương ) nước vẫn còn ngập khá cao , kẹt xe kéo dài .", [
        ("Cầu Ông Bố", "ngập khá cao", "NEG"),
        ("QL13", "ngập khá cao", "NEG"),
        ("Thuận An", "ngập khá cao", "NEG")
    ]),

    (3152, "Thuận An , Bình Dương , khổ sở với ngập úng kéo dài 4 năm .", [
        ("Thuận An", "ngập úng", "NEG"),
        ("Bình Dương", "ngập úng", "NEG")
    ]),

    (3154, "Ngay lúc này 🆘 Thuỷ triều dâng , làm nước ngập trên đường CMT8 , đoạn Cầu Ngang , Hưng định , Thuận An , Bình Dương cũ .", [
        ("đường CMT8", "nước ngập", "NEG"),
        ("Cầu Ngang", "nước ngập", "NEG"),
        ("Thuận An", "nước ngập", "NEG")
    ]),

    (3156, "Đường Trần Tử Bình x Lý Thường Kiệt , Thủ Dầu Một , Bình Dương ngay lúc này 😥 😥 😥 - - - - Đợt triều cường dâng vào giữa tháng 10 , nước ngập sâu", [
        ("Đường Trần Tử Bình", "nước ngập sâu", "NEG"),
        ("Lý Thường Kiệt", "nước ngập sâu", "NEG"),
        ("Thủ Dầu Một", "nước ngập sâu", "NEG")
    ]),

    (3157, "Cảnh người dân đi học , đi làm trễ sáng nay vì không qua được vùng ngập ở đoạn cầu Quan - Bến Cát , Bình Dương .", [
        ("cầu Quan", "ngập", "NEG"),
        ("Bến Cát", "ngập", "NEG")
    ]),

    (3159, "Ngập ở khu vực trung tâm Bình Dương ngay lúc này 😟 Triều cường dâng , loạt tuyến đường như Cách Mạng Tháng Tám ( cầu ông Đành ) , Thích Quảng Đức", [
        ("Bình Dương", "Ngập", "NEG"),
        ("Cách Mạng Tháng Tám", "Ngập", "NEG"),
        ("Thích Quảng Đức", "Ngập", "NEG")
    ]),

    (3163, "Thủ Dầu Một , Mưa ngập ngay lúc này ở ngã 3 Cống Thích Quảng Đức , Thủ Dầu Một , Bình Dương .", [
        ("ngã 3 Cống Thích Quảng Đức", "Mưa ngập", "NEG"),
        ("Thủ Dầu Một", "Mưa ngập", "NEG")
    ]),

    (3165, "Tối nay ⛔ Thủy Triều dâng cao gây ngập chợ Bình Dương và ngã 6 đến cầu Ông Đành .", [
        ("chợ Bình Dương", "ngập", "NEG"),
        ("ngã 6", "ngập", "NEG"),
        ("cầu Ông Đành", "ngập", "NEG")
    ]),

    (3166, "Mực nước đo được là 1 , 85m tại trạm Thủ Dầu Một , cao hơn báo động 3 .", [
        ("trạm Thủ Dầu Một", "cao hơn báo động 3", "NEU")
    ]),

    (3167, "Chợ Bình Dương tối nay và những ngày gần đây nước ngập khiến nhiều xe chết máy .", [
        ("Chợ Bình Dương", "nước ngập", "NEG")
    ]),

    (3171, "BÌNH DƯƠNG CHIỀU NAY PHỐ CŨNG NHƯ SÔNG 😢 Khoảng 17h chiều nay ( 13 / 10 ) , cơn mưa lớn bất ngờ đổ xuống nhiều nơi ở Bình Dương khiến đường Thích Quảng Đức ngập sâu", [
        ("BÌNH DƯƠNG", "PHỐ CŨNG NHƯ SÔNG", "NEG"),
        ("đường Thích Quảng Đức", "ngập sâu", "NEG")
    ]),

    (3172, "Thủ Dầu Một Đoạn Đường Huỳnh Văn lũy ngay lúc này , Sau trận mưa lớn nước đã dâng cao ngập nửa xe máy , nhiều người phải dắt bộ", [
        ("Đường Huỳnh Văn lũy", "ngập nửa xe máy", "NEG"),
        ("Thủ Dầu Một", "ngập nửa xe máy", "NEG")
    ]),

    (3173, "Mưa như trút , nước chảy như thác cuốn trôi xe máy ở Bình Dương TPO - Cơn mưa lớn kèm sấm sét chiều nay ( 24 / 5 ) khiến nhiều tuyến đường ở Bình Dương ngập sâu", [
        ("Bình Dương", "nước chảy như thác", "NEG"),
        ("Bình Dương", "ngập sâu", "NEG")
    ]),

    (3174, "Sau loạt ôtô trôi lềnh đềnh , thì xe máy đậu trên lề cũng bị ngập nặng trong cơn mưa ở Mỹ Phước 2 ( Bến Cát )", [
        ("Mỹ Phước 2", "ngập nặng", "NEG"),
        ("Bến Cát", "ngập nặng", "NEG")
    ]),

    (3175, "Bình Dương : Mưa ngập ở 2 thành phố , giao thông tắc nghẽn Đến 19 giờ ngày 1 . 9 . 2024 , nhiều điểm ngập ở TP Dĩ An và TP Thuận An", [
        ("Bình Dương", "Mưa ngập", "NEG"),
        ("TP Dĩ An", "nhiều điểm ngập", "NEG"),
        ("TP Thuận An", "nhiều điểm ngập", "NEG")
    ]),

    (3177, "Cơn mưa ngang qua VŨNG TÀU NGẬP BANH CHÀNH / BANH TA LÔNG Chỗ bạn sao rồi", [
        ("VŨNG TÀU", "NGẬP BANH CHÀNH", "NEG")
    ]),

    (3178, "Mưa lớn đầu mùa , nhiều tuyến đường Vũng Tàu ngập sâu Ảnh : Kha Lu", [
        ("Vũng Tàu", "ngập sâu", "NEG")
    ]),

    (3179, "Mưa lớn đầu mùa , nhiều tuyến đường Vũng Tàu ngập sâu", [
        ("Vũng Tàu", "ngập sâu", "NEG")
    ]),

    (3181, "Ngập nặng ở Thi Sách - Vũng Tàu Video : Trần Phúc Hậu", [
        ("Thi Sách", "Ngập nặng", "NEG"),
        ("Vũng Tàu", "Ngập nặng", "NEG")
    ]),

    (3182, "Hàng loạt phương tiện chết máy trong cơn mưa lớn ở Vũng Tàu tối 22 / 5 Tối 22 / 5 , cơn mưa lớn kéo dài khoảng 2 tiếng đồng hồ khiến các tuyến đường ở Vũng Tàu ngập sâu", [
        ("Vũng Tàu", "chết máy", "NEG"),
        ("Vũng Tàu", "ngập sâu", "NEG")
    ]),

    (3183, "Mưa lớn đầu mùa , nhiều tuyến đường Vũng Tàu ngập sâu Ngày 7 / 6 , trận mưa lớn kéo dài khoảng 3 giờ đồng hồ khiến nhiều tuyến đường ở trung tâm TP Vũng Tàu ngập nặng", [
        ("Vũng Tàu", "ngập sâu", "NEG"),
        ("TP Vũng Tàu", "ngập nặng", "NEG")
    ]),

    (3184, "💦 NHIỀU TUYẾN ĐƯỜNG TRUNG TÂM KHU VỰC VŨNG TÀU NGẬP SAU MƯA !", [
        ("VŨNG TÀU", "NGẬP", "NEG")
    ]),

    (3186, "📍 14 TUYẾN ĐƯỜNG NGẬP SÂU KHI MƯA LỚN TẠI VŨNG TÀU .", [
        ("VŨNG TÀU", "NGẬP SÂU", "NEG")
    ]),

    (3187, "TÌNH HÌNH NGẬP LỤT SẮP TỚI TẠI BÀ RỊA .", [
        ("BÀ RỊA", "NGẬP LỤT", "NEU")
    ]),

    (3191, "Đường ở chợ Bình Dương gần đây cứ như ' Vũng Tàu ' 🫣 Đường ngập bà con xin đừng cố chạy qua .", [
        ("chợ Bình Dương", "ngập", "NEG")
    ]),

    (3194, "Không ngờ có ngày Vũng Tàu gặp cảnh này . Ngập ngang bụng luôn 🥲 🥲 Note : đoạn ngã tư Vietso Petro đường 30 / 4", [
        ("Vũng Tàu", "Ngập ngang bụng", "NEG"),
        ("đường 30 / 4", "Ngập ngang bụng", "NEG")
    ]),

    (3195, "Đường 30 / 4 khu vực cảng Vietso ngập nặng , mọi người nên chọn hướng đi khác", [
        ("Đường 30 / 4", "ngập nặng", "NEG")
    ]),

    (3197, "Mưa lớn ngập sâu ở Bến Cát , Bình Dương Không cần đi chữa lành , ở đây vừa lành và lạnh luôn 🐧", [
        ("Bến Cát", "ngập sâu", "NEG"),
        ("Bình Dương", "ngập sâu", "NEG")
    ]),

    (3198, "Đường Bà Rịa – Châu Pha đoạn thi công cầu vượt km 49 + 900 ngập nước vì trời mưa", [
        ("Đường Bà Rịa – Châu Pha", "ngập nước", "NEG")
    ]),

    (3202, "Bình Dương : Mưa lớn gây ngập ở 2 thành phố , giao thông ùn tắc ⛈ ⛈ ⛈", [
        ("Bình Dương", "ngập", "NEG")
    ]),

    (3448, "Cơn mưa như trút từ trưa đến chiều nay 16 - 4 khiến tuyến đường Quốc lộ 13 , Tp Thuận An , Bình Dương ( giáp phường Hiệp Bình Phước ) ngập sâu trong biển nước", [
        ("Quốc lộ 13", "ngập sâu", "NEG"),
        ("Tp Thuận An", "ngập sâu", "NEG"),
        ("Bình Dương", "ngập sâu", "NEG")
    ]),

    (3450, "Quốc lộ 13 đoạn qua thị xã Thuận An ngập nặng , hàng ngàn phương tiện \" chìm sâu \" trong nước .", [
        ("Quốc lộ 13", "ngập nặng", "NEG"),
        ("thị xã Thuận An", "ngập nặng", "NEG")
    ]),

    (3451, "Trạm CSGT Quốc Lộ 13 phát hiện dùng xe thùng chở người dân qua vùng ngập nước ở cầu Quan , Bến Cát Bình Dương sáng nay .", [
        ("cầu Quan", "ngập nước", "NEG"),
        ("Bến Cát", "ngập nước", "NEG")
    ]),

    (3452, "Hiện tại QL13 hướng 2 chiều từ cây Xăng số 4 đến Lotte Bình Dương đang ùn tắc giao thông do ngập", [
        ("QL13", "ngập", "NEG"),
        ("Bình Dương", "ngập", "NEG")
    ]),

    (3472, "Bình Dương mưa lớn ngay lúc này ❌ ghi nhận mưa lớn khiến đường ngập nhiều nơi , đúng lúc mọi người tan ca về", [
        ("Bình Dương", "đường ngập", "NEG")
    ]),

    (3487, "🛑 Triều cường trên sông Sài Gòn vượt báo động III gây ngập nhiều tuyến đường ở Bình Dương tối nay 18 / 10", [
        ("sông Sài Gòn", "ngập", "NEG"),
        ("Bình Dương", "ngập", "NEG")
    ]),

    (3505, "Đỉnh triều cao nhất ngày ở mức xấp xỉ hoặc trên báo động 2 sẽ duy trì đến hết ngày 26 và 27 - 11 , riêng trạm Thủ Dầu Một ở mức cao", [
        ("trạm Thủ Dầu Một", "ở mức cao", "NEU")
    ]),

    (3657, "\" Tôi vừa tan ca làm trong công trình xây dựng dưới Bình Dương chạy về đến đây thì gặp nước ngập , xe tôi bị chết máy , phải dắt bộ hơn 2km rồi \"", [
        ("Bình Dương", "nước ngập", "NEG")
    ]),

    # ==============================================================================
    # NHÓM 2: TỪ NGỮ DÂN DÃ / CHÂM CHỌC / CHÂM BIẾM VỀ NGẬP LỤT ĐỜI THƯỜNG
    # ==============================================================================
    (42, "Sài Gòn đặc sản mưa ngâu Phố phường ngập nước , người đâu đi về ! Xe nằm đường , đứng tái tê Nhích từng chút một , dầm dề dưới mưa .", [
        ("Sài Gòn", "ngập nước", "NEG")
    ]),

    (317, "🌧 ️ MƯA LỚN , NGẬP SÂU NGƯỜI ĐI XE MÁY CẦN LƯU Ý GÌ ? 💦 Dạo này chiều nào Sài Gòn cũng đổ mưa lớn , phố xá biến thành sông , khiến bao chiến mã rơi vào cảnh chết máy", [
        ("Sài Gòn", "phố xá biến thành sông", "NEG"),
        ("Sài Gòn", "chết máy", "NEG")
    ]),

    (338, "SÀI GÒN MÙA NÀY … KHÔNG CẦN ĐI BIỂN ! Mưa xuống một trận , đường phố TP. HCM lập tức biến thành sông", [
        ("SÀI GÒN", "biến thành sông", "NEG"),
        ("TP. HCM", "biến thành sông", "NEG")
    ]),

    (374, "Sài Gòn thất thủ sau cơn mưa lớn , phương tiện trục trặc , nước tràn vào nhà dân", [
        ("Sài Gòn", "thất thủ", "NEG"),
        ("Sài Gòn", "nước tràn vào nhà", "NEG")
    ]),

    (401, "CV Làng Hoa Gò Vấp biến thành Công Viên Nước Gò Vấp , mùa ngập chơi nước mưa nước cống", [
        ("CV Làng Hoa Gò Vấp", "ngập", "NEG")
    ]),

    (437, "Bãi sau Gò Vấp - Ngã ➕ Lê Văn Thọ - Nguyễn Văn Khối Gò Vấp # mưa # ngập # bơi # hưxe # xuhuong # reels # đặcsản", [
        ("Lê Văn Thọ", "ngập", "NEG"),
        ("Nguyễn Văn Khối", "ngập", "NEG"),
        ("Gò Vấp", "ngập", "NEG")
    ]),

    (439, "Bãi sau Gò Vấp - Ngã ➕ Lê Văn Thọ - Nguyễn Văn Khối Gò Vấp # mưa # ngập # bơi # hưxe # xuhuong # reels # đặcsản", [
        ("Lê Văn Thọ", "ngập", "NEG"),
        ("Nguyễn Văn Khối", "ngập", "NEG"),
        ("Gò Vấp", "ngập", "NEG")
    ]),

    (606, "TP. HCM cứ mỗi khi mưa lại ngập , đường phố biến thành sông , nhà dân thì chìm trong biển nước .", [
        ("TP. HCM", "ngập", "NEG"),
        ("TP. HCM", "biến thành sông", "NEG"),
        ("TP. HCM", "chìm trong biển nước", "NEG")
    ]),

    (701, "Biển nước tại đoạn Lê Văn Lương - Tố Hữu .", [
        ("Lê Văn Lương", "Biển nước", "NEG"),
        ("Tố Hữu", "Biển nước", "NEG")
    ]),

    (739, "Bãi sau Sài Gòn quê tôi mùa nước lũ # mưa # ngập # mưagióbãobùng # vungtau # sàigòn", [
        ("Sài Gòn", "nước lũ", "NEG")
    ]),

    (774, "Sài Gòn thất thủ , nước ngập mênh mông mà anh Tăng Phúc bắt fan đặt báo thức", [
        ("Sài Gòn", "thất thủ", "NEG"),
        ("Sài Gòn", "nước ngập mênh mông", "NEG")
    ]),

    (2509, "Tại TPHCM , Có nơi lượng mưa lên tới 290 - 330 mm , khiến nước thoát chậm , nhiều tuyến đường ngập sâu", [
        ("TPHCM", "thoát chậm", "NEG"),
        ("TPHCM", "ngập sâu", "NEG")
    ]),

    # ==============================================================================
    # NHÓM 3: HIỆU CHỈNH CHUYÊN SÂU LÔ 11 - 14 (RECORDS 1001 ĐẾN 1400)
    # ==============================================================================
    (1011, "Siêu dự án chống ngập của TP. HCM khởi công năm 2016 theo hình thức BT , gồm 6 cống ngăn triều : Cây Khô , Mương Chuối , Phú Xuân , Bến Nghé , Tân Thuận và Phú Định .", [
        ("Cây Khô", "chống ngập", "POS"),
        ("Mương Chuối", "chống ngập", "POS"),
        ("Phú Xuân", "chống ngập", "POS"),
        ("Bến Nghé", "chống ngập", "POS"),
        ("Tân Thuận", "chống ngập", "POS"),
        ("Phú Định", "chống ngập", "POS")
    ]),

    (1035, "Dự án Giải quyết ngập do triều khu vực Thành phố Hồ Chí Minh gồm 6 cống ngăn triều : Bến Nghé , Cây Khô , Mương Chuối , Phú Định , Phú Xuân , Tân Thuận", [
        ("Bến Nghé", "Giải quyết ngập", "POS"),
        ("Cây Khô", "Giải quyết ngập", "POS"),
        ("Mương Chuối", "Giải quyết ngập", "POS"),
        ("Phú Định", "Giải quyết ngập", "POS"),
        ("Phú Xuân", "Giải quyết ngập", "POS"),
        ("Tân Thuận", "Giải quyết ngập", "POS")
    ]),

    (1041, "Bao giờ TPHCM hết ngập ?", [
        ("TPHCM", "hết ngập", "NEU")
    ]),

    (1046, "Tại TPHCM , Tuyến đường dẫn vào cống đã được chỉnh trang , thảm nhựa , cảnh quan thông thoáng hơn .", [
        ("TPHCM", "thông thoáng hơn", "POS")
    ]),

    (1054, "Tại TPHCM , Nay khô ráo , nước hết ngập rồi ạ 😜", [
        ("TPHCM", "khô ráo", "POS"),
        ("TPHCM", "nước hết ngập", "POS")
    ]),

    (1068, "Triều cường ở TPHCM đạt đỉnh , gây ngập nặng ở TP. HCM vào ngày nào ?", [
        ("triều cường ở TPHCM", "đạt đỉnh", "NEU"),
        ("TP. HCM", "ngập nặng", "NEU")
    ]),

    (1097, "Dân Sài Gòn than trời khi nào mới hết ngập ?", [
        ("Sài Gòn", "hết ngập", "NEU")
    ]),

    (1098, "TP. HCM : Đường Trần Xuân Soạn , bán đảo Thanh Đa sẽ hết ngập do triều cường ?", [
        ("Đường Trần Xuân Soạn", "hết ngập", "NEU"),
        ("bán đảo Thanh Đa", "hết ngập", "NEU")
    ]),

    (1119, "Tại TPHCM , Đây là lần thứ hai hầm chui này bị ngập kể từ khi thông xe hồi tháng 2 .", [
        ("TPHCM", "bị ngập", "NEG")
    ]),
]

def generate_and_apply_all():
    phase3_path = 'data/validate_label/thuan/phase3.txt'
    with open(phase3_path, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]
    assert len(lines) == 3875, f"Expected 3875 lines, got {len(lines)}"

    print(f"Bắt đầu biên dịch {len(raw_revisions)} bản ghi hiệu chỉnh...")
    compiled_revisions = {}
    
    for rec_id, text, triplet_specs in raw_revisions:
        triplets = []
        for asp_p, opi_p, pol in triplet_specs:
            t = make_triplet(text, asp_p, opi_p, pol)
            triplets.append(t)
        compiled_revisions[rec_id] = (text, triplets)
        
    print(f"✅ Đã biên dịch thành công 100% không lỗi {len(compiled_revisions)} bản ghi!")
    
    # Apply to lines
    updated_lines = list(lines)
    for rec_id, (new_text, new_triplets) in compiled_revisions.items():
        line_idx = rec_id - 1
        trip_strs = []
        for a, o, s in new_triplets:
            trip_strs.append(f"({a}, {o}, '{s}')")
        formatted = '[' + ', '.join(trip_strs) + ']'
        updated_lines[line_idx] = f"{new_text}####{formatted}"
        
    with open(phase3_path, 'w', encoding='utf-8') as f:
        for l in updated_lines:
            f.write(l + '\n')
            
    print(f"🎉 Đã cập nhật thành công toàn bộ vào {phase3_path}!")

if __name__ == '__main__':
    generate_and_apply_all()
