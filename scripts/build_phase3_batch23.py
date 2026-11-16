# -*- coding: utf-8 -*-
"""
Build Phase 3 Batch 23 (Records 2201 - 2300).
Tuân thủ 100% BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md.
"""

batch23_data = [
    # 2201 (Tứ Liên thuộc Hà Nội tỉnh ngoài -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Hơn 3 ngày sống chung với ngập của người dân ở Tứ Liên",
        []
    ),
    # 2202
    (
        "Mưa lớn khiến nhiều tuyến đường TPHCM ngập nước chiều và tối 22 . 9 , phương tiện di chuyển khó khăn , nhiều người phải dắt xe qua đoạn ngập sâu .",
        [
            ([6], [7, 8], 'NEG'),
            ([6], [30, 31], 'NEG')
        ]
    ),
    # 2203 (Strip giới từ 'lên' theo Pass 5)
    (
        "Vì hồi chiều trời mưa nên đường dẫn lên cầu Ba Son ngập luôn !",
        [([9, 10, 11], [12, 13], 'NEG')]
    ),
    # 2204
    (
        "Sài Gòn hẻm ngập nước ngoằn ngoèo cỡ nào cũng không cản được đam mê tới tận nhà sửa máy .",
        [([0, 1], [3, 4], 'NEG')]
    ),
    # 2205 (Hồ Trị An thuộc Đồng Nai tỉnh ngoài -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , HỒ TRỊ AN BẮT ĐẦU XẢ NƯỚC , VEN SÔNG CÓ NGUY CƠ NGẬP SAU NHIỀU NGÀY MƯA LỚN !",
        []
    ),
    # 2206 (Tin tiến độ thi công hạ tầng, không nhắc ngập -> REJECT)
    (
        "Nút giao quốc lộ 50 - Nguyễn Văn Linh ở huyện Bình Chánh cũ ( TP. HCM ) đã thi công xong nhưng chưa thể khai thác , dự kiến chờ đến quý 4 / 2027 .",
        []
    ),
    # 2207
    (
        "TPHCM : Mưa lớn giờ tan tầm , đường Hồ Học Lãm ngập sâu",
        [([8, 9, 10, 11], [12, 13], 'NEG')]
    ),
    # 2208 (Dự báo nguy cơ ngập tương lai -> NEU)
    (
        "CẢNH BÁO GẤP 24 / 9 : ÁP THẤP MẠNH LÊN , TRÚT “ BOM NƯỚC ” – TPHCM NGUY CƠ NGẬP THÀNH SÔNG # thoitiet",
        [([18], [19, 20, 21, 22, 23], 'NEU')]
    ),
    # 2209
    (
        "THIÊN TAI : Người dân TPHCM đẩy xe giúp nhau qua dòng nước ngập xiết # vietan # tintuc # news",
        [([5], [13, 14], 'NEG')]
    ),
    # 2210 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Đường vào nhà ngập sâu , đợi nước rút thì lâu nên chờ mãi cuối cùng quyết định để xe lại đặt Grap đi về và lội nước vào .",
        [([1], [6, 7], 'NEG')]
    ),
    # 2211 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nước sâu tới gối , hầm xe thì nước tràn vào ngập 😔 😔",
        [([1], [11, 12, 13, 14], 'NEG')]
    ),
    # 2212 (Cắt bỏ tiền tố thừa vì thân bài có phường Tân Thới Hiệp, strip 'ở' theo Pass 5)
    (
        "Còn anh Dương Văn Hà , chủ tiệm sửa xe ở phường Tân Thới Hiệp , lại giúp bà con sau những trận ngập .",
        [([11, 12, 13, 14], [23], 'NEG')]
    ),
    # 2213 (Mẹo tư vấn sửa xe máy ngập nước -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Những xe bị chết máy nhẹ do nước vào , anh hỗ trợ vệ sinh , hong khô miễn phí và hướng dẫn mọi người cách tự xử lý , để không phải tốn thêm chi phí khi chưa thực sự cần sửa chữa .",
        []
    ),
    # 2214 (Tản văn triết lý cuộc sống -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Những điều không lớn lao , nhưng giữa lúc mưa gió , lại có thể giúp một người không phải chạy xe trong bộ quần áo ướt sũng , một chiếc xe được cứu kịp thời , và một ngày mưu sinh bớt nhọc nhằn hơn .",
        []
    ),
    # 2215
    (
        "Mấy ngày qua , mưa bão 🌧 ️ kết hợp triều cường dâng cao 🌊 đã biến nhiều tuyến đường TP. HCM thành \" sông \" , xe chết máy xếp hàng 🚗 💥 , cuộc sống người dân hoàn toàn đảo lộn .",
        [([20, 21], [28, 29], 'NEG')]
    ),
    # 2216 (Strip 'ở' theo Pass 5)
    (
        "Bơm nước giải cứu nhiều vườn bưởi bị ngập ở xã Tân Vĩnh Lộc , TP. HCM",
        [([10, 11, 12, 13], [7, 8], 'NEG')]
    ),
    # 2217 (Dự báo triều cường đề phòng ngập -> NEU)
    (
        "Triều cường TP. HCM lên đỉnh 1 , 65 m , đề phòng ngập trong những ngày tới",
        [([2, 3], [11, 12, 13], 'NEU')]
    ),
    # 2218 (Dự báo có thể gây ngập -> NEU)
    (
        "Tại TPHCM , Cơ quan khí tượng cảnh báo mưa lớn kết hợp triều cường có thể gây ngập tại các vùng trũng thấp , ven sông , ảnh hưởng giao thông và hoạt động kinh tế - xã hội .",
        [([1], [15, 16, 17, 18], 'NEU')]
    ),
    # 2219 (Rao bán bất động sản / nhà trọ -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Khu này cao ráo , an ninh , chưa bao giờ ngập .",
        []
    ),
    # 2220 (Cắt bỏ tiền tố thừa vì thân bài có Quận 7)
    (
        "Giữ sức khoẻ nhé Quận 7 của tôi ơi , hi vọng ngày gặp lại Quận 7 chưa chìm trong biển nước , bạn bè thì chưa cưới và mấy quán ngon vẫn chưa đóng cửa .",
        [([4, 5], [17, 18, 19, 20, 21], 'POS')]
    ),
    # 2221 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Mưa như trút nước , xe cộ kẹt cứng , nước mênh mông khắp nơi .",
        [([1], [13, 14, 15, 16, 17], 'NEG')]
    ),
    # 2222
    (
        "[ TP. HCM ] : Mưa xối xả đúng giờ cao điểm khiến hàng loạt cửa ngõ tê liệt hoàn toàn , nước dâng cuồn cuộn ngập lút bánh xe .",
        [([1, 2], [26, 27, 28, 29], 'NEG')]
    ),
    # 2223 (Chỉ ùn ứ kẹt xe, không nhắc ngập -> REJECT)
    (
        "Chiều 30 / 9 , cơn mưa như trút nước trút xuống đúng vào khung giờ tan tầm đã khiến tình hình giao thông tại nhiều khu vực trọng điểm của TP. HCM rơi vào tình trạng ùn ứ nghiêm trọng .",
        []
    ),
    # 2224
    (
        "Tại khu vực Thủ Đức , lượng mưa lớn chỉ sau ít phút đã khiến các tuyến đường Tô Ngọc Vân , Linh Đông và Nguyễn Văn Quá ngập sâu lút bánh , nước chảy xiết làm hàng loạt phương tiện chết máy .",
        [
            ([18, 19, 20], [28, 29, 30, 31], 'NEG'),
            ([22, 23], [28, 29, 30, 31], 'NEG'),
            ([25, 26, 27], [28, 29, 30, 31], 'NEG')
        ]
    ),
    # 2225 (Fallback - Khen ngợi người dân hỗ trợ -> POS)
    (
        "Tại TPHCM , Giữa muôn vàn khó khăn vì thời tiết bất lợi , hình ảnh những người dân hai bên đường chủ động túc trực cảnh báo điểm ngập nguy hiểm , tận tình hỗ trợ đẩy xe giúp người qua đường đã thắp lên nét đẹp nghĩa tình , tiếp thêm nguồn năng lượng tích cực và sự ấm áp trong cộng đồng giữa chiều mưa phố thị .",
        [([1], [33, 34, 35, 36, 37, 38, 39, 40, 41, 42], 'POS')]
    ),
    # 2226
    (
        "10 mấy năm vào sài gòn ở mà đay là lần đầu tiên thấy vĩnh lộc A bị ngập lụt",
        [([14, 15, 16], [17, 18, 19], 'NEG')]
    ),
    # 2227
    (
        "Nâng nền nhà 3 lần , khu dân cư tại TPHCM vẫn không thoát cảnh ngập 😓 Triều cường rạng sáng 28 / 9 khiến đường Rạch Cùng , TPHCM chìm trong nước .",
        [([25, 26, 27], [30, 31, 32], 'NEG')]
    ),
    # 2228 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Học sinh đi học , người dân đi làm phải chật vật qua đoạn đường ngập ; nhiều nhà vẫn bị nước tràn vào",
        [([1], [24, 25, 26], 'NEG')]
    ),
    # 2229 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Cận cảnh sau cơn mưa chiều nay nhiều tuyến đường ngập nặng 👇 Nguồn : tổng hợp # ducphantan # nghethuatvagiaitri",
        [([1], [13, 14], 'NEG')]
    ),
    # 2230
    (
        "Chiều nay Sài Gòn mưa lớn , nhiều tuyến đường ngập sâu , người dân chật vật di chuyển giữa dòng nước .",
        [([2, 3], [10, 11], 'NEG')]
    ),
    # 2231 (Không nói ngập -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Mưu sinh vốn đã nhiều vất vả , gặp thêm cơn mưa chiều lại càng thêm khó khăn .",
        []
    ),
    # 2232 (Câu hỏi nguyên nhân ngập -> NEU)
    (
        "Nguyên nhân khiến TP. HCM ngập ngày càng nặng ?",
        [([3, 4], [5, 6, 7, 8], 'NEU')]
    ),
    # 2233 (Công thức toán châm biếm không địa danh -> REJECT)
    (
        "Sụt lún + triều cường + mưa cực đoan + quy hoạch thiếu bài bản = Ngập úng ?",
        []
    ),
    # 2234 (Strip 'ở' theo Pass 5)
    (
        "Mưa lớn kết hợp triều cường khiến nhiều tuyến đường ở TPHCM ngập sâu đúng giờ tan tầm .",
        [([11], [12, 13], 'NEG')]
    ),
    # 2235 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Người dân chật vật dắt xe , bì bõm vượt dòng nước về nhà .",
        [([1], [10, 11, 12, 13, 14], 'NEG')]
    ),
    # 2236 (Dự báo cảnh báo ngập tương lai -> NEU)
    (
        "TPHCM : TRIỀU CƯỜNG VƯỢT BÁO ĐỘNG 3 , CẢNH BÁO NGẬP TỪ 28 - 30 / 9 Từ ngày 28 - 30 / 9 , TPHCM bước vào đợt triều cường cao , trong đó một số trạm dự báo vượt mức báo động 3 .",
        [([0], [9, 10, 11], 'NEU')]
    ),
    # 2237 (Strip 'ở' theo Pass 5)
    (
        "Bản đồ một số điểm thường xuyên ngập nặng do triều cường ở TPHCM .",
        [([13], [5, 6, 7, 8], 'NEG')]
    ),
    # 2238 (Cắt bỏ tiền tố thừa vì thân bài có Hồ Chí Minh)
    (
        "Hồ Chí Minh vào chiều 30 / 9 khiến nhiều tuyến phố ngập sâu .",
        [([0, 1, 2], [12, 13], 'NEG')]
    ),
    # 2239
    (
        "MƯA LỚN KHIẾN TP. HCM NGẬP VÀ KẸT XE NGHIÊM TRỌNG Mưa lớn sáng 30 / 9 khiến nhiều tuyến đường huyết mạch tại TP. HCM ngập nặng , giao thông rơi vào cảnh kẹt cứng giờ cao điểm .",
        [([24, 25], [26, 27], 'NEG')]
    ),
    # 2240 (Strip 'ở' theo Pass 5)
    (
        "Chiều nay 30 . 9 , mưa lớn đúng giờ tan tầm cùng triều cường khiến nhiều tuyến đường ở TP. HCM ngập sâu .",
        [([20, 21], [22, 23], 'NEG')]
    ),
    # 2241 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Có nơi người đi đường quay đầu vì sợ xe chết máy .",
        [([1], [11, 12, 13, 14], 'NEG')]
    ),
    # 2242 (Nước đã rút -> POS theo Pass 8)
    (
        "Sau trận ngập sâu , đến trưa 1 / 10 , nước tại khu dân cư quanh đường số 11 , phường Thủ Đức , TP. HCM đã rút .",
        [([17, 18, 19], [27, 28], 'POS')]
    ),
    # 2243 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Người dân đang khẩn trương dọn bùn đất , cọ rửa nhà cửa và đưa phương tiện bị ngập đi sửa chữa .",
        [([1], [20, 21], 'NEG')]
    ),
    # 2244
    (
        "Triều cường kết hợp mưa , đường Trần Xuân Soạn ngập đúng giờ tan tầm # TNN",
        [([6, 7, 8, 9], [10], 'NEG')]
    ),
    # 2245
    (
        "Nổ đơn đùng đùng dù Trần Xuân Soạn có ngập quán cũng chèo xuồng đi giao 🌊 Zalo : 0368443756 mãi eoooo 🥰 Kafe Gần Nhà",
        [([5, 6, 7], [8, 9], 'NEG')]
    ),
    # 2246
    (
        "Khoảng 16h , mưa lớn trút xuống khu vực Thủ Đức ( TP HCM ) khiến nhiều tuyến đường ngập sâu .",
        [([9, 10], [19, 20], 'NEG')]
    ),
    # 2247 (Strip 'Trên' theo Pass 5)
    (
        "Trên đường Tô Ngọc Vân , chỉ sau khoảng 10 phút mưa nặng hạt , nước đã dâng lút bánh xe , chảy xiết .",
        [([1, 2, 3, 4], [17, 18, 19, 20], 'NEG')]
    ),
    # 2248 (Cắt cụt lỡ dở -> REJECT)
    (
        "Khu vực giao với đường Linh Đông ngập nặng nhất , dòn",
        []
    ),
    # 2249 (Strip 'ở' theo Pass 5)
    (
        "ĐƯỜNG THÀNH SÔNG , NHÀ THÀNH ĐIỂM NGẬP TRONG NGÀY TRIỀU CƯỜNG Ở TPHCM Triều cường dâng cao chiều 28 / 9 khiến nhiều tuyến đường ở TPHCM ngập sâu , giao thông ùn ứ .",
        [([27], [28, 29], 'NEG')]
    ),
    # 2250 (Cắt cụt lỡ dở -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Nước tràn vào nhà , người dân chật vật kê dọn đồ đạc , xoay xở tro",
        []
    ),
    # 2251 (Strip 'trên tuyến' theo Pass 5)
    (
        "Sáng 28 - 9 , trên tuyến đường Rạch Cùng thuộc phường Bình Đông , TP. HCM triều cường lên cao , khiến nơi đây bị ngập .",
        [([7, 8, 9], [25, 26], 'NEG')]
    ),
    # 2252
    (
        "Mưa lớn chiều 30 / 9 khiến đường Phan Văn Hớn và Nguyễn Văn Quá ngập nặng , kẹt xe 3km .",
        [
            ([7, 8, 9, 10], [15, 16], 'NEG'),
            ([12, 13, 14], [15, 16], 'NEG')
        ]
    ),
    # 2253 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nhiều người dân phải tấp vào cây xăng đợi nước rút Video : Chinh Hoàng",
        [([1], [11, 12, 13], 'NEG')]
    ),
    # 2254
    (
        "Mưa lớn trút xuống TP. HCM , đường Phan Huy Ích và Nguyễn Văn Quá ngập sâu , xe cộ chật vật “ vượt ải 🥲 # Y1PN",
        [
            ([7, 8, 9, 10], [15, 16], 'NEG'),
            ([12, 13, 14], [15, 16], 'NEG')
        ]
    ),
    # 2255 (Cắt cụt lỡ dở ở cuối -> REJECT)
    (
        "Dự án cải thiện hệ thống thoát nước , nước thải lưu vực Tây thành phố với vốn đầu tư hơn 7 nghìn tỷ đồng vừa được phê duyệt , kỳ vọng sẽ giải bài toán ngập nước cho 8 phường tại TP.",
        []
    ),
    # 2256 (Strip 'ở' theo Pass 5)
    (
        "MƯA LỚN GIỜ TAN TẦM Ở TPHCM , NGƯỜI DÂN BÌ BÕM DẮT XE VỀ NHÀ Mưa lớn kết hợp triều cường khiến nhiều tuyến đường ở TPHCM ngập sâu đúng giờ tan tầm .",
        [([27], [28, 29], 'NEG')]
    ),
    # 2257
    (
        "Đường Ung Văn Khiêm sắp mở rộng 30 m , xóa sổ ' rốn ' kẹt xe , ngập nước Đường Ung Văn Khiêm ( phường Thạnh Mỹ Tây ) là một trong những tuyến đường thường xuyên ùn tắc vào giờ cao điểm .",
        [([0, 1, 2, 3], [18, 19], 'NEG')]
    ),
    # 2258 (Strip 'tại' theo Pass 5)
    (
        "Mưa lớn tại TP. HCM vào chiều 30 / 9 khiến nhiều tuyến phố ngập sâu .",
        [([3, 4], [14, 15], 'NEG')]
    ),
    # 2259
    (
        "Cô gái vừa đi du lịch về , tá hoả khi bước vào nhà Nhà ngập nước mênh mông , đồ đạc trôi lềnh bềnh Tại đường số 40 , Hiệp Bình , Thủ Đức 📸 Ngọc Linh",
        [([26, 27, 28], [15, 16, 17, 18], 'NEG')]
    ),
    # 2260 (Chống ngập -> POS)
    (
        "🌧 ️ Mưa đã tạnh nhưng nước vẫn chưa rút , người dân TP. HCM tất bật chống ngập , bảo vệ tài sản .",
        [([13, 14], [17, 18], 'POS')]
    ),
    # 2261 (Strip 'ở' theo Pass 5)
    (
        "Chấn động nước ngập cao vô xe buýt ở Sài Gòn khiến ai cũng rén",
        [([9, 10], [2, 3, 4, 5, 6, 7], 'NEG')]
    ),
    # 2262 (Cắt cụt lỡ dở -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , 🌧 ️ Cứ mưa lớn là nước tràn vào nhà , đó là chuyện đã quen của nhiều hộ dân phía Tây TP.",
        []
    ),
    # 2263 (Thủy văn: đỉnh triều sông Sài Gòn lên cao -> NEU)
    (
        "TP. HCM có nơi mưa to vào buổi tối , đỉnh triều khu vực sông Sài Gòn lên cao 1 , 85 m có khả năng xuất hiện ngày 28 - 30 / 9 .",
        [([14, 15, 16], [17, 18], 'NEU')]
    ),
    # 2264 (Dự báo đề phòng ngập úng tương lai -> NEU)
    (
        "Hồ Chí Minh dự báo có mưa vừa đến to từ 4 giờ chiều nay , người dân cần đề phòng ngập úng do triều cường ⛈ ⛈",
        [([0, 1, 2], [19, 20, 21, 22], 'NEU')]
    ),
    # 2265 (Strip 'tại' theo Pass 5)
    (
        "Chiều tối 30 / 9 , cơn mưa lớn kéo dài từ 16 giờ kèm dông , sét trên diện rộng tại TP. HCM khiến nhiều tuyến đường ngập sâu .",
        [([22, 23], [28, 29], 'NEG')]
    ),
    # 2266 (Cắt cụt lỡ dở -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Cơn mưa vào giờ cao điểm , dòng nước chảy xiết và ngập úng diện rộng khiến người dân phải chật vật di chuyển , giao thông tại nhiều",
        []
    ),
    # 2267 (Strip 'ở' theo Pass 5)
    (
        "MƯA LỚN Ở TP. HCM ĐƯỜNG PHỐ THÀNH “ SÔNG ” Mưa lớn bất ngờ ở TP. HCM : Đường phố , khu dân cư ngập thành “ sông ” TP. HCM mưa lớn chiều 29 / 9 : Bầu trời bất ngờ tối sầm , mưa trút xuống khiến nhiều tuyến đường và khu dân cư ngập nước .",
        [([16, 17], [57, 58], 'NEG')]
    ),
    # 2268 (Strip 'ở' theo Pass 5, chống ngập -> POS)
    (
        "Mưa đã tạnh nhiều nhưng nước chưa rút , bà con ở TPHCM đang phải chống ngập , bảo vệ tài sản .",
        [([12], [15, 16], 'POS')]
    ),
    # 2269 (Strip 'ở' theo Pass 5)
    (
        "Mưa lớn ngay lúc này ngập nhiều nơi ở sài gòn 🌨 ️ # đỗhoàithương # fanpageđỗhoàithương # tintuc",
        [([9, 10], [5, 6, 7], 'NEG')]
    ),
    # 2270
    (
        "Hơn 23h45 ngày 30 - 9 , đường số 11 , phường Thủ Đức , TP. HCM vẫn ngập sâu .",
        [([7, 8, 9], [18, 19], 'NEG')]
    ),
    # 2271 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nước tràn vào hàng trăm nhà dân , có nơi sâu hơn 1m , nhiều gia đình phải di dời chạy ngập trong đêm .",
        [([1], [23, 24, 25, 26], 'NEG')]
    ),
    # 2272
    (
        "Đường Phan Huy Ích lúc này , đoạn giáp ranh Tân Bình - Gò Vấp cũ , đang ngập nặng , nhiều chỗ qua thắt lưng .",
        [([0, 1, 2, 3], [17, 18, 19], 'NEG')]
    ),
    # 2273 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Xe ô tô , xe máy , cả xăng lẫn điện , chết máy la liệt .",
        [([1], [15, 16, 17, 18], 'NEG')]
    ),
    # 2274
    (
        "Mưa lớn giờ tan tầm , người dân TP. HCM bì bõm dắt xe giữa dòng nước ngập để về nhà 🌧 ️ # Y1PN",
        [([8, 9], [10, 11, 12, 13], 'NEG')]
    ),
    # 2275
    (
        "Chiều 29 . 9 , triều cường khiến đường Nguyễn Bình ( TP. HCM ) ngập khoảng 1 km , có nơi sâu gần nửa mét .",
        [([8, 9, 10], [15], 'NEG')]
    ),
    # 2276 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Hàng giờ liền , người dân phải canh con nước , chắn nước tràn vào nhà .",
        [([1], [14, 15, 16, 17, 18], 'NEG')]
    ),
    # 2277
    (
        "🔴 MƯA LỚN ĐÚNG GIỜ TAN TẦM , NHIỀU KHU VỰC Ở TPHCM BẮT ĐẦU NGẬP Mưa dông trút xuống nhiều khu vực TPHCM đúng giờ tan tầm chiều 30 . 9 , gây ngập cục bộ .",
        [([23], [33, 34, 35, 36], 'NEG')]
    ),
    # 2278 (Cắt bỏ tiền tố thừa vì thân bài có Linh Đông - Lý Tế Xuyên, strip 'tại khu vực' theo Pass 5)
    (
        "- - - - - - - - - - - 🎥 Nước ngập tại khu vực Linh Đông - Lý Tế Xuyên ( Nguồn : MXH )",
        [([17, 18, 19, 20, 21, 22], [12, 13], 'NEG')]
    ),
    # 2279
    (
        "Sài Gòn đặc sản mưa ngâu Phố phường ngập nước , người đâu đi về !",
        [([0, 1], [8, 9], 'NEG')]
    ),
    # 2280 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Xe nằm đường , đứng tái tê 😆 Chân bì bõm lội , não nề mưa rơi 😄 # Saigon # Mua # Quan9",
        [([1], [12, 13, 14], 'NEG')]
    ),
    # 2281 (Strip 'tại' theo Pass 5)
    (
        "Biển nước lúc nửa khuya tại đường Phan Huy Ích ( quận Tân Bình cũ ) # NguoiVietTre # tphcm # duongphanhuyich",
        [([6, 7, 8, 9], [0, 1], 'NEG')]
    ),
    # 2282 (Cắt bỏ tiền tố thừa vì thân bài có ngã tư Hàng Xanh, strip 'khu vực gần' theo Pass 5)
    (
        "khu vực gần ngã tư Hàng Xanh sáng nay 🥲 🥲 🥲 Ăn nguyên combo mưa ngập , kẹt xe . . .",
        [([3, 4, 5, 6], [15, 16], 'NEG')]
    ),
    # 2283
    (
        "🌊 TP. HCM : Triều cường dâng cao , một số tuyến đường ngập cục bộ 👇",
        [([1, 2], [13, 14, 15], 'NEG')]
    ),
    # 2284
    (
        "Đường khu Nam TP. HCM 3 ngày liên tiếp ngập vì triều cường Theo ghi nhận của Tri Thức - Znews chiều 29 / 9 , nước triều dâng cao khiến đường Nguyễn Bình ( xã Hiệp Phước , TP. HCM ) tiếp tục chìm trong nước .",
        [([31, 32, 33], [44, 45, 46], 'NEG')]
    ),
    # 2285 (Cắt cụt lỡ dở -> REJECT)
    (
        "Tại TP. Hồ Chí Minh , Có đoạn ngập khoảng nửa mét , lút bánh xe má",
        []
    ),
    # 2286 (Cắt cụt lỡ dở -> REJECT)
    (
        "🌊 DỰ BÁO MỰC NƯỚC VÀ NGẬP DO TRIỀU NGÀY 29 / 9 / 2026 TẠI KHU VỰC HIỆP PHƯỚC Theo kết quả dự báo thử nghiệm của Khoa Khí tượng Thủy văn và Tài nguyên nước – Trường Đại học Tài nguyên và Môi trường TP. HCM , ngày 29 / 9 / 2026 , mực nướ",
        []
    ),
    # 2287 (Strip 'Ở' theo Pass 5)
    (
        "BẢN ĐỒ MỘT SỐ ĐIỂM THƯỜNG XUYÊN NGẬP NẶNG DO TRIỀU CƯỜNG Ở TPHCM Bản đồ dưới đây cập nhật một số khu vực có thể bị ngập do triều cường , giúp người dân chủ động lựa chọn lộ trình di chuyển .",
        [([13], [5, 6, 7, 8], 'NEG')]
    ),
    # 2288
    (
        "Khoảng 16h chiều 30 - 9 , mưa lớn trút xuống khu vực Thủ Đức ( TP HCM ) khiến nhiều tuyến đường ngập sâu .",
        [([13, 14], [23, 24], 'NEG')]
    ),
    # 2289 (Cắt cụt lỡ dở -> REJECT)
    (
        "Khu vực giao với đường Linh Đông ngập nặn",
        []
    ),
    # 2290
    (
        "HCM : Đường lại biến thành sông , nước chảy mạnh Đường về nhà hôm nay xa quá Đây là lần ngập thứ 2 trong ngày cuối cùng của tháng 9 Địa điểm : Đường Phan Huy Ích Nguồn : Bùi Quang Phúc",
        [([34, 35, 36, 37], [4, 5, 6], 'NEG')]
    ),
    # 2291
    (
        "🌨 ️ mưa ngập sấm chớp liên hồi tân bình thành phố hồ chí minh 🙏 # đỗhoàithương # fanpageđỗhoàithương # tintuc",
        [([8, 9], [2, 3], 'NEG')]
    ),
    # 2292 (Strip 'ở' theo Pass 5)
    (
        "Nhiều tuyến đường ở TPHCM ngập sâu do triều cường",
        [([4], [5, 6], 'NEG')]
    ),
    # 2293
    (
        "💦 💦 Mưa lớn bất ngờ trút xuống TP. HCM vào chiều tối 30 - 9 , đúng giờ tan tầm , khiến nhiều tuyến đường ngập sâu , người dân tham gia giao thông di chuyển khó khăn .",
        [([8, 9], [26, 27], 'NEG')]
    ),
    # 2294
    (
        "TP. HCM hiện ghi nhận 159 điểm thường xuyên ngập .",
        [([0, 1], [7, 8, 9], 'NEG')]
    ),
    # 2295 (Strip 'ở' theo Pass 5)
    (
        "Bài toán thoát ngập ở TP. HCM : Nhận diện hơn 30 “ điểm đen ” ngập nước kinh niên , cứ mưa là ngập .",
        [([5, 6], [16, 17, 18, 19], 'NEG')]
    ),
    # 2296 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Mưa ngập từ ngoài đường đến vào trong nhà … .",
        [([1], [3, 4], 'NEG')]
    ),
    # 2297 (Strip 'Ở' theo Pass 5)
    (
        "🔰 BẢN ĐỒ MỘT SỐ ĐIỂM THƯỜNG XUYÊN NGẬP NẶNG DO TRIỀU CƯỜNG Ở TPHCM Bản đồ dưới đây cập nhật một số khu vực có thể bị ngập do triều cường , giúp người dân chủ động lựa chọn lộ trình di chuyển .",
        [([14], [6, 7, 8, 9], 'NEG')]
    ),
    # 2298
    (
        "Mỗi khi mưa lớn , đường Mã Lò ( đoạn từ Tỉnh lộ 10 đến Hương lộ 2 , phường Bình Trị Đông , TPHCM ) lại ngập sâu , ảnh hưởng nghiêm trọng đến việc đi lại và sinh hoạt của người dân .",
        [([5, 6, 7], [27, 28], 'NEG')]
    ),
    # 2299 (Tin rao bán nhà đất -> REJECT)
    (
        "💥 k ngập , k ngập , k ngập , 5ty1 đường MÃ Lò ( gần Tâ . n Kỳ Tâ . n Quý ) - 4 tầng BTCT , dt : 4 × 12m , 4 phòng - hẻm xe tăng đậu cửa , sát quận đội , an ninh , yên tĩnh Lh : 0869 . 777 . 944 - ( Duy ) # nhabinhtan , # nhabinhtangiare , # nhadep",
        []
    ),
    # 2300
    (
        "Mưa lớn gây ngập nhiều tuyến đường TPHCM , xe máy chết máy la liệt",
        [
            ([7], [2, 3], 'NEG'),
            ([7], [11, 12, 13, 14], 'NEG')
        ]
    ),
]

def format_line(text, triplets):
    formatted_triplets = []
    for asp, opn, pol in triplets:
        formatted_triplets.append(f"({asp}, {opn}, '{pol}')")
    triplets_str = "[" + ", ".join(formatted_triplets) + "]"
    return f"{text}####{triplets_str}\n"

if __name__ == '__main__':
    assert len(batch23_data) == 100, f"Expected 100 records, got {len(batch23_data)}"
    
    phase3_path = "data/validate_label/thuan/phase3.txt"
    with open(phase3_path, "r", encoding="utf-8") as f:
        lines = [l for l in f.readlines() if l.strip()]
    
    base_2200 = lines[:2200]
    assert len(base_2200) == 2200, f"Expected 2200 existing lines, found {len(base_2200)}"
    
    new_lines = [format_line(t, tr) for t, tr in batch23_data]
    
    all_lines = base_2200 + new_lines
    with open(phase3_path, "w", encoding="utf-8") as f:
        f.writelines(all_lines)
        
    print(f"Successfully updated {len(all_lines)} lines to {phase3_path}!")
