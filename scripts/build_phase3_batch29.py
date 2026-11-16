# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn Lô 29 (Rec 2801 - 2900) cho phase3.txt.
Tuân thủ tuyệt đối BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md
"""

batch29_data = [
    # 2801 (đường Rạch Cùng)
    (
        "TP. HCM của tôi đó , triều cường ngập nửa mét , người lớn lo lắng còn đám trẻ vui đùa , bắt cá trên đường Chiều 11 / 10 , triều cường dâng cao khiến đường Rạch Cùng , phường Bình Đông , TP. HCM , chìm trong nước .",
        [([31, 32, 33], [42, 43, 44], 'NEG')]
    ),
    # 2802 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Nhiều đoạn ngập khoảng 0 , 5 m , có nơi nướ",
        []
    ),
    # 2803 (TPHCM)
    (
        "🌊 🌧 Hầm xe khu biệt thự ở TPHCM ngập hơn 1 mét",
        [([7], [8, 9, 10, 11], 'NEG')]
    ),
    # 2804 (TPHCM)
    (
        "Sau trận mưa lớn , nhiều khu vực ở TPHCM ngập suốt 20 giờ .",
        [([8], [9], 'NEG')]
    ),
    # 2805 (TPHCM)
    (
        "😢 Nhiều tầng hầm biệt thự , ngân hàng ở TPHCM ngập sâu , nhiều giấy tờ - tài sản ngâm trong nước dù mưa đã tạnh từ tối qua .",
        [([10], [11, 12], 'NEG')]
    ),
    # 2806 (TPHCM)
    (
        "Tầng hầm biệt thự , ngân hàng ở TPHCM ngập sâu sau mưa lớn ngày 7 / 10 .",
        [([8], [9, 10], 'NEG')]
    ),
    # 2807 (KDC Cityland Park Hills , Gò Vấp)
    (
        "Ghi nhận sáng 8 / 10 tại KDC Cityland Park Hills , Gò Vấp : nhiều hầm vẫn ngập 1 - 1 , 5m .",
        [([7, 8, 9, 10], [17], 'NEG'), ([12, 13], [17], 'NEG')]
    ),
    # 2808 (Hồ Chí Minh)
    (
        "Hồ Chí Minh đang phải lội nước trở về nhà .",
        [([0, 1, 2], [5, 6], 'NEG')]
    ),
    # 2809 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Triều cường chiều tối nay vẫn xấp xỉnh đỉnh của đợt chiều qua , khiến nhiều tuyến đường ngập sâu , có nơi quá nửa bánh xe , nhiều xe chết máy .",
        [([1], [18, 19], 'NEG')]
    ),
    # 2810 (Cắt cụt)
    (
        "🔴 KHOẢNH KHẮC NƯỚC TRÀN VÀO NHÀ DÂN Ở KHU BIỆT THỰ TP HCM Sáng 8 / 10 , nhiều tầng hầm tại khu dân cư Cityland Park Hills ( phường Gò Vấp , TPHCM ) vẫn ngập sâu hơn 1 m sau trận mưa lớn chiều tối 7 / 10 , khiến nhiều xe máy , máy móc và thiết",
        []
    ),
    # 2811 (Tranh luận đạo đức dịch vụ)
    (
        "Tấm hình được chụp tại 1 điểm ngập ở Sài Gòn đang gây tranh cãi - Người ta bỏ tiền ra xài dịch vụ thì có quyền được hưởng chứ sao .",
        []
    ),
    # 2812 (Bình luận mạng)
    (
        "Tại TP. Hồ Chí Minh , - Trời ơi , đường ngập thì xuống phụ nhau qua cho lẹ , đàn ông mà ngồi z được cũng thua , tội anh Grab quá trời .",
        []
    ),
    # 2813 (TPHCM)
    (
        "Gian nan giải bài toán chống ngập Sau mỗi trận mưa lớn , nhiều gia đình TPHCM lại thức trắng kê đồ , tát nước , chứng kiến xe chết máy , nhà cửa hư hỏng và buôn bán đình trệ .",
        [([14], [23, 24], 'NEG')]
    ),
    # 2814 (khu Nam TPHCM)
    (
        "Triều cường đạt đỉnh , những đêm dài không ngủ ở khu Nam TPHCM",
        [([11, 12, 13], [2, 3], 'NEG')]
    ),
    # 2815 (Cắt cụt)
    (
        "🌊 Triều cường đạt đỉnh , TP.",
        []
    ),
    # 2816 (TP. HCM)
    (
        "Chiều nay 11 . 10 triều cường đạt đỉnh : Đường ở TP. HCM ngập sâu , nước tràn vào nhà dân - Báo Thanh Niên",
        [([12, 13], [14, 15], 'NEG')]
    ),
    # 2817 (TP. HCM)
    (
        "Nhiều tuyến đường ở TP. HCM ngập vì triều cường đạt đỉnh - Tuổi Trẻ",
        [([4, 5], [6], 'NEG')]
    ),
    # 2818 (khu nam TP. HCM)
    (
        "Triều cường đạt đỉnh chiều 10 . 10 : Đường khu nam TP. HCM ngập sâu , người dân chật vật - Báo Thanh Niên",
        [([10, 11, 12, 13], [14, 15], 'NEG')]
    ),
    # 2819 (Khởi công dự án tương lai)
    (
        "TP. HCM khởi công dự án chống ngập đường Mã Lò trong tháng 11 - Báo Thanh Niên",
        []
    ),
    # 2820 (Takashimaya)
    (
        "Con cưng Sài Gòn khu vực xung quanh Takashimaya mưa vẫn ngập như thường .",
        [([7], [10], 'NEG')]
    ),
    # 2821 (Bài phân tích lý do)
    (
        "Tại TP. Hồ Chí Minh , Quận 1 mưa lớn còn ngập thì đừng hỏi sao mưa lớn đường thành sông , 5 lý do vì sao đường ngập có thể gây bất ngờ ?",
        []
    ),
    # 2822 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nhiều tuyến đường ngập lênh láng , người dân gặp khó khăn khi di chuyển .",
        [([1], [6, 7], 'NEG')]
    ),
    # 2823 (Tiêu đề bài xã luận)
    (
        "🧐 Vì sao năm nào cũng mưa , nhưng năm nay Sài Gòn lại ngập lụt tới vậy ?",
        []
    ),
    # 2824 (Câu hỏi kỹ thuật)
    (
        "Tại TP. Hồ Chí Minh , Cùng một cơn mưa vì sao 1 hầm ngập mưa hầm còn lại thì không ?",
        []
    ),
    # 2825 (Sài Gòn)
    (
        "Sốc nặng với quả mưa và ngập lụt ở Sài Gòn luôn !",
        [([9, 10], [6, 7], 'NEG')]
    ),
    # 2826 (mã lò , bình tân)
    (
        "# xuhuong mã lò , bình tân , rần 1h sáng lại ngập",
        [([2, 3], [12], 'NEG'), ([5, 6], [12], 'NEG')]
    ),
    # 2827 (khu vực BT)
    (
        "Điểm ngập nặng nhất ở khu vực BT",
        [([5, 6], [1, 2, 3], 'NEG')]
    ),
    # 2828 (khu biệt thự TP HCM)
    (
        "Khoảnh khắc nước tràn vào hầm nhà dân ở khu biệt thự TP HCM",
        [([9, 10, 11, 12], [2, 3], 'NEG')]
    ),
    # 2829 (TP. HCM)
    (
        "Hầm biệt thự TP. HCM ngập 1 , 5m sau trận mưa lớn",
        [([3, 4], [5], 'NEG')]
    ),
    # 2830 (Cảnh báo chung)
    (
        "TP. HCM PHÁT CẢNH BÁO 122 ĐIỂM NGẬP LỤT SAU NHỮNG CƠN MUA NẶNG HẠT KÉO DÀI CHIỀU 7 / 10",
        []
    ),
    # 2831 (TP. HCM)
    (
        "Mưa hơn 2 giờ đúng giờ tan tầm , nhiều đường TP. HCM ngập sâu , xe chết máy hàng loạt",
        [([10, 11], [12, 13], 'NEG')]
    ),
    # 2832 (TP. HCM)
    (
        "Chiều tối 7 / 10 , mưa lớn trút xuống TP. HCM khiến nhiều tuyến đường ngập sâu ; nhiều xe tắt máy , người dân chật vật di chuyển giữa dòng nước # tiktoknews # amm",
        [([8, 9], [14, 15], 'NEG')]
    ),
    # 2833 (SÀI GÒN)
    (
        "SÀI GÒN 08 / 10 / 2026 Triều cường đang dân cao , Đi làm sao mà cực quá kẹt xe nước ngập .",
        [([0, 1], [19, 20], 'NEG')]
    ),
    # 2834 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Ủa trời mưa ngập đường mà sao bọt như biển zậy 🌊",
        [([1], [6], 'NEG')]
    ),
    # 2835 (TÂN MAI)
    (
        "CƠN MƯA LỚN CHIỀU NAY 8 / 10 , TÂN MAI NGẬP NẶNG ! !",
        [([9, 10], [11, 12], 'NEG')]
    ),
    # 2836 (Cảnh báo chung)
    (
        "Tại TP. Hồ Chí Minh , Hồ Chí Minh cảnh báo 122 điểm ngập mùa mưa 😭 🌧 ️",
        []
    ),
    # 2837 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Mưa to liên tục và ngập nhiều nơi",
        [([1], [7], 'NEG')]
    ),
    # 2838 (Câu hỏi đường đi)
    (
        "Vậy đường đi đến TT Genesis có ngập không ?",
        []
    ),
    # 2839 (đường Cây Trâm)
    (
        "Lại ngập tại đường Cây Trâm sau cơn mưa lớn chiều tối nay .",
        [([3, 4, 5], [1], 'NEG')]
    ),
    # 2840 (Tam kỳ -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , Tam kỳ sau 3 ngày mưa hi sinh đt để quay video cho anh xem ngập lút bánh xe r tình hình mưa to nữa là thất thủ đừng mưa nữa ông trời ơi 🥲 🥲 # xuhuong # tamky92",
        []
    ),
    # 2841 (Đường Nguyễn Văn Khối)
    (
        "Đường Nguyễn Văn Khối ở Thông Tây Hội , TP. HCM nước ngập nửa bánh xe sau mưa lớn đêm qua",
        [([0, 1, 2, 3], [10, 11, 12, 13], 'NEG')]
    ),
    # 2842 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Ngập nước lên gần hết bánh xe roài 🥹",
        [([1], [3, 4], 'NEG')]
    ),
    # 2843 (Lời khuyên an toàn)
    (
        "Tại TP. Hồ Chí Minh , Người dân được khuyến cáo chủ động đổi lộ trình , không cố đi qua nơi nước sâu , chảy xiết và đặc biệt tránh xa hố ga mất nắp , dây điện , trụ điện , cột đèn khi khu vực bị ngập .",
        []
    ),
    # 2844 (chợ bình thủy - Cần Thơ -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , chợ bình thủy quê tôi ngập quá ngập rồi chỗ mọi người có ngập không ?",
        []
    ),
    # 2845 (Khẩu hiệu mơ hồ)
    (
        "Tại TP. Hồ Chí Minh , ĐÀ GÒ RỒI CŨNG NGẬP XUYÊN ĐÊM .",
        []
    ),
    # 2846 (Bản tin chính sách)
    (
        "Hồ Chí Minh tăng giải pháp chống ngập # htv # htvnewz # htvtintuc # tphcm",
        []
    ),
    # 2847 (Cắt cụt)
    (
        "Trước áp lực ngập do mưa lớn và triều cường , TP.",
        []
    ),
    # 2848 (Kế hoạch dự án)
    (
        "Hồ Chí Minh dự kiến hoàn thành 9 dự án chống ngập ngay trong năm nay .",
        []
    ),
    # 2849 (Cắt cụt)
    (
        "Thành phố đã lên phương án xử lý 50 điểm ngập từ nay đến năm 2030 . # chuyendong24h # tiktoknews # chongngap # tphcm # diemn",
        []
    ),
    # 2850 (Chỉ đạo hành chính)
    (
        "TP. HCM : Tăng cường ứng phó ngập do mưa lớn kết hợp triều cường .",
        []
    ),
    # 2851 (TP. HCM)
    (
        "Triều cường dâng cao lúc rạng sáng , hàng loạt ô tô ở TP. HCM chìm trong biển nước .",
        [([11, 12], [13, 14, 15, 16], 'NEG')]
    ),
    # 2852 (Sài Gòn)
    (
        "10 ngày nay , Sài Gòn mưa liên tục , lại thêm triều cường nên đường sá ngập , kẹt xe khắp nơi .",
        [([4, 5], [14], 'NEG')]
    ),
    # 2853 (Cắt tiền tố thừa vì có Quận 1)
    (
        "Con tui đi học trên Quận 1 , ngày nào về tới nhà cũng ướt sũng .",
        [([5, 6], [14, 15], 'NEG')]
    ),
    # 2854 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Dòng người lội nước giờ tan làm thật tội nghiệp 😎 😎 😎 # mưa # ngập # mưagióbãobùng # sàigòn # tphcm",
        [([1], [5, 6], 'NEG')]
    ),
    # 2855 (Đường Nguyễn Văn Khối)
    (
        "Đường Nguyễn Văn Khối ( Gò Vấp ) hoá biển nước sau cơn mưa chiều 7 . 10 !",
        [([0, 1, 2, 3], [8, 9, 10], 'NEG')]
    ),
    # 2856 (Thủ Đức)
    (
        "Nước Ngập Thủ Đức Hôm Nay 2026",
        [([2, 3], [0, 1], 'NEG')]
    ),
    # 2857 (Thủ Dầu Một - Bình Dương -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , kiếp nạn sinh nhật mùa mưa Thủ Dầu Một ngập lênh láng 🤣 🤣 # binhduongdidau # reviewbinhduong # binhduongangi # reviewanngon # anngonmoingay",
        []
    ),
    # 2858 (Bình Dương -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , Bình Dương sáng nay nhiều tuyến đường gần sông thuỷ triều dâng cao ngập cả mặt đường # reviewbinhduong # thuytrieu",
        []
    ),
    # 2859 (TP. HCM)
    (
        "Triều cường TP. HCM dâng 1 , 86 m : đường ngập nặng , xe chết máy",
        [([2, 3], [11, 12], 'NEG')]
    ),
    # 2860 (quận 7 , Nhà Bè)
    (
        "Cảnh báo top 7 con đường ngập sâu nguy hiểm ở quận 7 và Nhà Bè dịp triều cường từ 10 / 10 - 12 / 10 / 26 Anh em qua khu này nhớ né nha ☠ ️ 😭 😭 # trieucuong # ngapnuoc # nhabe # q7 # CapCut",
        [([9, 10], [6, 7], 'NEG'), ([12, 13], [6, 7], 'NEG')]
    ),
    # 2861 (Tiêu đề giải thích nguyên nhân)
    (
        "Tại sao đỉnh triều cường 10 / 10 chỉ ngập Quận 7 và Nhà Bè ?",
        []
    ),
    # 2862 (Giải thích dự án)
    (
        "Tại TP. Hồ Chí Minh , Xem ngay câu trả lời từ tiến độ dự án 10 . 000 tỷ chống ngập ở Quận 7 và Nhà Bè đạt 80 % . Sang năm khu vực này mới hết ngập Chỗ của anh em hôm nay có bị ngập không ?",
        []
    ),
    # 2863 (Phương án nhà trường)
    (
        "Nhiều trường ở TP HCM cho học sinh về sớm , tránh triều cường đạt đỉnh 12 / 10 - 13 / 10 # trieucuong # xuhuong ( theo socmedia , vnexpress )",
        []
    ),
    # 2864 (TP. HCM)
    (
        "Nhiều hầm xe tại khu biệt thự ở TP. HCM ngập sâu hơn 1 m sau mưa lớn , khiến hàng loạt xe máy , máy móc và tài sản của người dân bị ngâm trong nước , hư hỏng Ảnh & Clip : Di Anh # news # amm # FCGN",
        [([8, 9], [10, 11], 'NEG')]
    ),
    # 2865 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , ngập lụt 😭 😭 # creatorsearchinsights # cáchlàmchovideoxuhướng # nanathodia # xuhuong # ngap",
        []
    ),
    # 2866 (TPHCM)
    (
        "Tầng hầm ngập sâu , cư dân khu biệt thự hạng sang ở TPHCM ' còng lưng ' bơm tát nước",
        [([11], [2, 3], 'NEG')]
    ),
    # 2867 (TPHCM)
    (
        "Người dân TPHCM lội nước ăn cơm tối trong mùa triều cường # dantrinews # LearnOnTikTok # xuhuong",
        [([2], [3, 4], 'NEG')]
    ),
    # 2868 (sông Sài Gòn)
    (
        "Nước tràn vào hàng quán ven sông Sài Gòn trong ngày triều cường # vnexpress # vnego # tphcm",
        [([6, 7, 8], [1, 2], 'NEG')]
    ),
    # 2869 (Cắt cụt)
    (
        "Triều cường gây ngập sâu tại TP. HCM , sinh hoạt và giao thông đảo lộn Tình trạng ngập do triều cường tại phía Nam TP. HCM đang diễn biến phức tạp , khiến hàng loạt tuyến đường thấp ven sông ngập sâu mênh mông , giao thông nghẽn mạng đúng giờ tan t",
        []
    ),
    # 2870 (TP. HCM)
    (
        "Triều cường gây ngập gần nửa mét ở TP. HCM , phụ huynh lội nước cõng con đến trường # shorts",
        [([8, 9], [3], 'NEG')]
    ),
    # 2871 (Sài Gòn)
    (
        "Sài Gòn ngập ngày cuối tuần .",
        [([0, 1], [2], 'NEG')]
    ),
    # 2872 (TPHCM)
    (
        "Chiều 12 - 10 , triều cường tiếp tục dâng tại TPHCM , người chật vật tát nước , người thích thú bắt lươn",
        [([9], [7, 8], 'NEG')]
    ),
    # 2873 (sông Sài Gòn)
    (
        "Nước tràn vào hàng quán ven sông Sài Gòn trong ngày triều cường # vietan # tintuc # news # tphcm",
        [([6, 7, 8], [1, 2], 'NEG')]
    ),
    # 2874 (Tư duy chống ngập)
    (
        "Tại TP. Hồ Chí Minh , TP HCM thay đổi tư duy chống ngập",
        []
    ),
    # 2875 (Sài Gòn)
    (
        "Trời ơi Sài Gòn lại ngập nữa rồi",
        [([2, 3], [4, 5], 'NEG')]
    ),
    # 2876 (Hy vọng tương lai)
    (
        "Đây là hy vọng cho người dân quận 7 sẽ không còn phải khổ sở vì ngập do mưa và triều cường .",
        []
    ),
    # 2877 (TPHCM)
    (
        "⛈ ️ 🌫 ️ TPHCM : Ngập khủng khiếp nhiều tuyến đường , khu vực sau cơn mưa lúc sáng sớm",
        [([4], [6, 7], 'NEG')]
    ),
    # 2878 (thành phố Hồ Chí Minh)
    (
        "Cơn mưa kéo dài nhiều tiếng đồng hồ trên diện rộng vào sáng sớm 10 / 5 khiến nhiều tuyến đường , khu vực tại thành phố Hồ Chí Minh ngập trong biển nước , ô tô , xe máy chết máy hàng loạt , giao thông ùn tắc nghiêm trọng .",
        [([25, 26, 27, 28, 29], [30, 31, 32, 33], 'NEG')]
    ),
    # 2879 (đường Phạm Văn Đồng)
    (
        "Tại TPHCM , do ảnh hưởng của mưa lớn nhiều đoạn trên đường Phạm Văn Đồng bị ngập nặng .",
        [([12, 13, 14, 15], [17, 18], 'NEG')]
    ),
    # 2880 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Đoạn này có địa hình khá thấp nên nước mưa từ các chỗ cao dồn về khiến đoạn ngã ba trên bị ngập nghiêm trọng , nhiều chỗ ngập quá đầu gối , xe cộ chết máy hàng loạt , giao thông ùn tắc dài gần cây số .",
        [([1], [25, 26, 27], 'NEG')]
    ),
    # 2881 (chợ Thủ Đức)
    (
        "Cách đó không xa , các tuyến đường xung quanh chợ Thủ Đức cũng bị ngập nặng , người dân phải xuống xe dắt bộ .",
        [([10, 11, 12], [15, 16], 'NEG')]
    ),
    # 2882 (đường Đặng Thùy Trâm)
    (
        "Tại quận Bình Thạnh , mưa lớn kéo dài khiến đường Đặng Thùy Trâm ngập hơn nửa bánh xe .",
        [([10, 11, 12, 13], [14, 15, 16, 17, 18], 'NEG')]
    ),
    # 2883 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nhiều xe bị chết máy , người dân phải dắt bộ .",
        [([1], [5, 6], 'NEG')]
    ),
    # 2884 (TP Hồ Chí Minh)
    (
        "Trận mưa kéo dài đã khiến nhiều tuyến đường ở TP Hồ Chí Minh bị ngập sâu .",
        [([10, 11, 12, 13], [15, 16], 'NEG')]
    ),
    # 2885 (đường Dương Văn Cam , Đặng Thị Rành , Kha Vạn Cân , Hồ Văn Tư)
    (
        "Tại đường Dương Văn Cam , Đặng Thị Rành , Kha Vạn Cân , Hồ Văn Tư ( TP Thủ Đức ) , đường Nguyễn Văn Khối , Phạm Văn Chiêu ( quận Gò Vấp ) , Nguyễn Văn Quá ( quận 12 ) nước ngập lút bánh khiến hàng loạt xe chết máy , nhiều người ướt sũng đồ đạc .",
        [([2, 3, 4], [45, 46, 47], 'NEG'), ([6, 7, 8], [45, 46, 47], 'NEG'), ([10, 11, 12], [45, 46, 47], 'NEG'), ([14, 15, 16], [45, 46, 47], 'NEG')]
    ),
    # 2886 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nhiều hộ dân dùng tấm gỗ , sắt chắn trước cửa nhưng nước vẫn tràn vào bên trong .",
        [([1], [17, 18], 'NEG')]
    ),
    # 2887 (Đo lượng mưa)
    (
        "Lượng mưa đo được tại Gò Vấp , TP Thủ Đức đạt khoảng 30 - 50 mm .",
        []
    ),
    # 2888 (TPHCM)
    (
        "TPHCM - Liên tiếp trong 2 ngày 16 - 17 . 10 , triều cường trên hệ thống sông Sài Gòn dâng cao , vượt mức báo động 3 , khiến nhiều khu vực ở TPHCM bị ngập sâu , việc đi lại , buôn bán của người dân gặp nhiều khó khăn .",
        [([0], [37, 38], 'NEG')]
    ),
    # 2889 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Ông em đồng nghiệp bì bõm vượt 10km phố ngập nước qua cafe .",
        [([1], [12, 13], 'NEG')]
    ),
    # 2890 (TP. HCM)
    (
        "MƯA LỚN GIỜ TAN TẦM , NGƯỜI DÂN TP. HCM LỘI BIỂN NƯỚC TRỞ VỀ NHÀ",
        [([8, 9], [11, 12], 'NEG')]
    ),
    # 2891 (TP. HCM)
    (
        "Trận mưa lớn vào khoảng 17h00 ngày hôm nay ( 27 / 5 ) và kéo dài 30 phút đã khiến nhiều tuyến đường ở TP. HCM bị ngập , người dân phải bì bõm lội nước về nhà , một số xe bị chết máy .",
        [([25, 26], [28], 'NEG')]
    ),
    # 2892 (đoạn đường Trần Xuân Soạn)
    (
        "Triều cường dâng cao khiến đoạn đường Trần Xuân Soạn ( quận 7 , TPHCM ) bị ngập sâu .",
        [([6, 7, 8, 9], [17, 18], 'NEG')]
    ),
    # 2893 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nước từ miệng cống và kênh , rạch gần đó tràn lên đường vào giờ tan tầm khiến người dân di chuyển vất vả .",
        [([1], [14, 15, 16], 'NEG')]
    ),
    # 2894 (đường Trần Xuân Soạn , Huỳnh Tấn Phát)
    (
        "Người dân sống tại các con hẻm trên đường Trần Xuân Soạn , Huỳnh Tấn Phát không còn lạ gì với cảnh nước triều từ kênh Tẻ dâng ngập lên mặt đường và tràn cả vào nhà … 👇",
        [([8, 9, 10, 11], [27, 28], 'NEG'), ([13, 14, 15], [27, 28], 'NEG')]
    ),
    # 2895 (đỉnh triều ở TPHCM - Mở rộng Quy tắc 6 - NEU)
    (
        "Ngày 30 . 10 , đỉnh triều ở TPHCM duy trì ở mức cao khi đạt 1 , 66m lúc 5h và 1 , 69m lúc 17h30 .",
        [([5, 6, 7, 8], [9, 10, 11, 12], 'NEU')]
    ),
    # 2896 (Trần Xuân Soạn , Đào Sư Tích , Lê Văn Lương , Huỳnh Tấn Phát , Nguyễn Bình)
    (
        "Theo Sở Xây dựng TPHCM , hiện thành phố có 7 tuyến đường trục chính bị ngập do triều cường , gồm : Trần Xuân Soạn , Đào Sư Tích , Lê Văn Lương , Quốc lộ 50 , Phạm Hữu Lầu , Huỳnh Tấn Phát , Nguyễn Bình .",
        [([23, 24, 25], [16], 'NEG'), ([27, 28, 29], [16], 'NEG'), ([31, 32, 33], [16], 'NEG'), ([43, 44, 45], [16], 'NEG'), ([47, 48], [16], 'NEG')]
    ),
    # 2897 (Fallback chuẩn hóa - Cảnh báo tương lai NEU)
    (
        "Tại TPHCM , Người dân cần đề phòng ngập úng ở vùng trũng thấp .",
        [([1], [5, 6, 7, 8], 'NEU')]
    ),
    # 2898 (TP Hồ Chí Minh)
    (
        "Nhiều tuyến đường ở TP Hồ Chí Minh ngập sâu sau cơn mưa kéo dài",
        [([4, 5, 6, 7], [8, 9], 'NEG')]
    ),
    # 2899 (đường Thảo Điền)
    (
        "Theo quan sát của phóng viên , ngay từ lối vào đường Thảo Điền , nhiều xe máy của người dân bị chết máy , nước ngập hơn nửa bánh xe , buộc phải đẩy bộ .",
        [([11, 12, 13], [26, 27, 28, 29, 30], 'NEG')]
    ),
    # 2900 (đường Nguyễn Hữu Cảnh)
    (
        "Cơn mưa cũng khiến một số đoạn thuộc đường Nguyễn Hữu Cảnh ngập cục bộ , người dân di chuyển khó khăn .",
        [([8, 9, 10, 11], [12, 13, 14], 'NEG')]
    )
]

def format_line(text, triplets):
    formatted_triplets = []
    for asp, opn, pol in triplets:
        formatted_triplets.append(f"({asp}, {opn}, '{pol}')")
    triplets_str = "[" + ", ".join(formatted_triplets) + "]"
    return f"{text}####{triplets_str}\n"

def test_triplets():
    errors = 0
    punct = set(".,;:!?\"'“”‘’()[]{}#~-_/\\")
    for idx, (text, triplets) in enumerate(batch29_data, 2801):
        tokens = text.split()
        for asp, opn, pol in triplets:
            # Check aspect bounds
            for a in asp:
                if a < 0 or a >= len(tokens):
                    print(f"LỖI REC {idx}: Aspect index {a} out of range (len {len(tokens)})")
                    errors += 1
            # Check opinion bounds
            for o in opn:
                if o < 0 or o >= len(tokens):
                    print(f"LỖI REC {idx}: Opinion index {o} out of range (len {len(tokens)})")
                    errors += 1
            asp_str = " ".join([tokens[a] for a in asp])
            opn_str = " ".join([tokens[o] for o in opn])
            # Check punctuation edge
            if tokens[opn[0]] in punct or tokens[opn[-1]] in punct:
                print(f"CẢNH BÁO REC {idx}: Opinion dính dấu câu: '{opn_str}'")
                errors += 1
            if tokens[asp[0]] in punct or tokens[asp[-1]] in punct:
                print(f"CẢNH BÁO REC {idx}: Aspect dính dấu câu: '{asp_str}'")
                errors += 1
            # Check empty
            if not asp_str.strip() or not opn_str.strip():
                print(f"LỖI REC {idx}: Aspect hoặc Opinion rỗng")
                errors += 1
    if errors == 0:
        print("TẤT CẢ CÁC TRIPLETS CỦA BATCH 29 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!")
    else:
        print(f"CÓ {errors} LỖI CẦN SỬA!")
    return errors

if __name__ == '__main__':
    assert len(batch29_data) == 100, f"Expected 100 records, got {len(batch29_data)}"
    err_cnt = test_triplets()
    if err_cnt > 0:
        import sys
        sys.exit(1)
        
    phase3_path = "data/validate_label/thuan/phase3.txt"
    with open(phase3_path, "r", encoding="utf-8") as f:
        lines = [l for l in f.readlines() if l.strip()]
    
    base_2800 = lines[:2800]
    assert len(base_2800) == 2800, f"Expected 2800 existing lines, found {len(base_2800)}"
    
    new_lines = [format_line(t, tr) for t, tr in batch29_data]
    
    all_lines = base_2800 + new_lines
    with open(phase3_path, "w", encoding="utf-8") as f:
        f.writelines(all_lines)
        
    print(f"Successfully updated {len(all_lines)} lines to {phase3_path}!")
