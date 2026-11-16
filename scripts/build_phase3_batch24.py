# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn Lô 24 (Rec 2301 - 2400) cho phase3.txt.
Tuân thủ tuyệt đối BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md
"""

batch24_data = [
    # 2301 (Chợ Lái Thiêu - Bình Dương -> Ngoại tỉnh)
    (
        "Cảnh báo 🆘 Mưa lớn , đang ngập đoạn Cách Mạng Tháng Tám từ vòng xoay chợ Lái Thiêu ( tua 18 ) đến trạm thu phí cầu Phú Long ( Quốc Lộ 13 ) .",
        []
    ),
    # 2302 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Đã nhiều xe chết máy khi cố qua đoạn ngập .",
        [([1], [12], 'NEG')]
    ),
    # 2303 (Chợ Lái Thiêu - Bình Dương -> Ngoại tỉnh)
    (
        "Cảnh báo ngay lúc này 🆘 ĐANG MƯA lớn , và ngập đoạn Cách Mạng Tháng Tám từ vòng xoay chợ Lái Thiêu ( tua 18 ) đến trạm thu phí cầu Phú Long ( Quốc Lộ 13 ) .",
        []
    ),
    # 2304 (Đồng Nai -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , Đồng Nai : Đường ngập , nước tràn vào nhà sau cơn mưa sáng 30 - 9 # SGGP",
        []
    ),
    # 2305 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , ngập trong và sau cơn mưa .",
        []
    ),
    # 2306 (Tên hội thảo khoa học, không có sự kiện ngập thời sự)
    (
        "Đó là nhận định của các chuyên gia tại hội thảo khoa học \" Sụt lún và ngập lụt tại TP. HCM và các giải pháp thích ứng \" , do Trường ĐH Tài nguyên và Môi trường TP. HCM ( HCMUNRE ) tổ chức ngày 29 . 9 .",
        []
    ),
    # 2307 (Lý thuyết tôn nền chống ngập)
    (
        "Tại TP. Hồ Chí Minh , \" Chúng ta biết rằng việc tôn nền chống ngập nơi này , nước sẽ tràn sang nơi khác và gây ngập cục bộ .",
        []
    ),
    # 2308 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Sụt lún và ngập lụt gắn chặt",
        []
    ),
    # 2309 (Mô hình khoa học sụt lún)
    (
        "Tại TP. Hồ Chí Minh , Theo đánh giá của PGS . TS Lê Trung Chơn , nếu chỉ tính toán mưa và triều nhưng không cập nhật sự thay đổi cao độ mặt đất do sụt lún , các mô hình ngập có thể ngày càng xa rời điều kiện thực tế .",
        []
    ),
    # 2310 (Cắt bỏ tiền tố thừa vì thân bài có Phú Mỹ Hưng)
    (
        "Phú Mỹ Hưng ít ngập nhờ đâu ?",
        [([0, 1, 2], [3, 4], 'POS')]
    ),
    # 2311 (Đô thị thích ứng)
    (
        "Tại TP. Hồ Chí Minh , “ Phú Mỹ Hưng là điển hình cho việc đô thị thích ứng với sụt lún , ngập lụt ” , ông Chơn nhận định .",
        []
    ),
    # 2312 (Đường Phan Huy Ích ngập sâu 1 mét)
    (
        "Tối 30 . 9 , một video livestream trên một tài khoản TikTok ( thu hút lúc cao điểm lên tới 25 . 000 lượt xem cùng lúc ) cho thấy tuyến đường Phan Huy Ích ( phường Tân Sơn , TP. HCM ) ngập sâu 1 mét sau mưa lớn .",
        [([33, 34, 35], [44, 45, 46, 47], 'NEG')]
    ),
    # 2313 (đường Phan Huy Ích)
    (
        "Theo lời chủ tài khoản TikTok , nước đã tràn vào đường Phan Huy Ích sau cơn mưa lớn chiều 30 . 9 .",
        [([13, 14, 15], [8, 9, 10, 11], 'NEG')]
    ),
    # 2314 (Ùn tắc kẹt xe không ngập)
    (
        "Tại TP. Hồ Chí Minh , Ùn tắc xảy ra do mưa lớn từ khoảng 7h , đúng giờ người dân đi làm , học sinh đến trường .",
        []
    ),
    # 2315 (Vòng xoay Điện Biên Phủ ùn tắc)
    (
        "Cách cầu Ba Son khoảng 2 km , vòng xoay Điện Biên Phủ cũng ùn tắc .",
        []
    ),
    # 2316 (Đường ven kênh ùn tắc)
    (
        "Tại TP. Hồ Chí Minh , Đường ven kênh ít đèn đỏ , hiếm khi ùn tắc nên thường được người dân chọn đi khi khu trung tâm đông xe .",
        []
    ),
    # 2317 (Cắt Tại thừa)
    (
        "Đường Phạm Văn Đồng , một đoạn nằm gần ngã tư Phạm Văn Đồng – Tô Ngọc Vân ngập rất nặng .",
        [([0, 1, 2, 3], [15, 16, 17], 'NEG')]
    ),
    # 2318 (đường Phạm Văn Đồng)
    (
        "Đoạn ngập ở cả 2 chiều trên đường Phạm Văn Đồng này chỉ dài khoảng 200 m nhưng khiến tình hình giao thông tại đây gần như tê liệt .",
        [([7, 8, 9, 10], [1], 'NEG')]
    ),
    # 2319 (Ùn tắc kẹt xe không ngập)
    (
        "Tại TP. Hồ Chí Minh , Cũng theo ghi nhận lúc 18 giờ 30 , các xe đi qua đây bị ùn tắc cục bộ , kéo dài gần 3 km .",
        []
    ),
    # 2320 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , \" Khu vực này trước đây thường xuyên xảy ra ngập nặng .",
        [([1], [13, 14], 'NEG')]
    ),
    # 2321 (Giao thông nước chảy mạnh dắt xe máy)
    (
        "Nhiều người không thể điều khiển xe qua dòng nước chảy mạnh , phải xuống dắt xe máy .",
        []
    ),
    # 2322 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Một số xe bị ngập nước , chết máy .",
        [([1], [7, 8], 'NEG')]
    ),
    # 2323 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nước ngập sâu khiến hàng loạt xe chết máy , người dân đi lại hết sức vất vả ” , chị Na chia sẻ .",
        [([1], [4, 5], 'NEG')]
    ),
    # 2324 (Giao thông vất vả không ngập)
    (
        "Tại TP. Hồ Chí Minh , Dòng phương tiện lưu thông qua tuyến đường này vô cùng vất vả .",
        []
    ),
    # 2325 (TPHCM duy trì ở mức cao)
    (
        "Theo Đài Khí tượng Thủy văn Nam Bộ , mực nước tại hầu hết các trạm trên sông , kênh , rạch khu vực TPHCM biến đổi chậm và duy trì ở mức cao trong 1 - 2 ngày đầu , sau đó có xu hướng giảm .",
        [([19], [25, 26, 27, 28], 'NEU')]
    ),
    # 2326 (Thời tiết mưa dông lốc sét không ngập)
    (
        "Tại TP. Hồ Chí Minh , Người dân khi di chuyển trong thời gian mưa dông cần theo dõi diễn biến thời tiết , đồng thời đề phòng lốc , sét và gió giật mạnh , nhất là tại những khu vực đang có mưa lớn .",
        []
    ),
    # 2327 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , nhiều đoạn đường bị ngập nặng , trở thành \" biển nước \" đen ngòm .",
        [([1], [7, 8], 'NEG')]
    ),
    # 2328 (Mưa rào không ngập)
    (
        "Tại TP. Hồ Chí Minh , Riêng ngày 1 - 10 , một số khu vực , nhất là ven biển , có khả năng xuất hiện mưa rào vào buổi sáng .",
        []
    ),
    # 2329 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , \" Như hôm nay nước bắt đầu dâng từ lúc 15 giờ 30 mà tới hơn 18 giờ nhưng vẫn chưa rút nữa .",
        [([1], [8, 9, 10], 'NEG')]
    ),
    # 2330 (Trần Xuân Soạn, Huỳnh Tấn Phát)
    (
        "Dẫn chứng thực tế , PGS . TS Lê Trung Chơn cho biết tại khu vực quận 7 trước đây , các tuyến đường Trần Xuân Soạn , Huỳnh Tấn Phát và vùng lân cận thường xuyên xảy ra ngập khi mưa lớn hoặc triều cường .",
        [([24, 25, 26], [39], 'NEG'), ([28, 29, 30], [39], 'NEG')]
    ),
    # 2331 (Lý thuyết quy hoạch sụt lún)
    (
        "Những khu vực có tốc độ sụt lún cao , thường xuyên ngập hoặc có nguy cơ chịu tác động đồng thời của sụt lún , triều cường , mưa cực đoan và nước biển dâng cần được xác định là vùng rủi ro để có phương án phát triển phù hợp .",
        []
    ),
    # 2332 (Cảm thán không ngập)
    (
        "Tại TP. Hồ Chí Minh , Lần nào cũng vậy , rất vất vả và mệt mỏi ” .",
        []
    ),
    # 2333 (TPHCM - giải quyết triệt để điểm ngập)
    (
        "\" Chính quyền phường và người dân địa phương đang rất mong chờ Sở Xây dựng TPHCM sớm thẩm định , phê duyệt dự án , để giúp giải quyết triệt để điểm ngập , góp phần ổn định đời sống cho người dân ” , ông Nguyễn Phước Bình , Trưởng Phòng Hạ tầng , UBND phường Bình Trị Đông cho biết .",
        [([16], [29, 30, 31, 32, 33], 'POS')]
    ),
    # 2334 (Đường Phạm Hữu Lầu, đường 15B)
    (
        "Đường Phạm Hữu Lầu đoạn giao với đường 15B ngập sâu , giao thông ùn ứ lúc 18h .",
        [([0, 1, 2, 3], [9, 10], 'NEG'), ([7, 8], [9, 10], 'NEG')]
    ),
    # 2335 (phường Bình Quới)
    (
        "Ghi nhận tại phường Bình Quới trong chiều 28 / 9 , một số tuyến đường xuất hiện ngập khi mưa kết hợp với thời điểm triều lên , khiến việc đi lại của người dân gặp khó khăn .",
        [([3, 4, 5], [17, 18], 'NEG')]
    ),
    # 2336 (Phỏng vấn triều không phải lúc nào cũng ngập)
    (
        "Tại TP. Hồ Chí Minh , \" Như thời điểm hiện tại thì triều đã lên trễ hơn và cũng không phải lúc nào khu vực này cũng ngập \" , chị chia sẻ .",
        []
    ),
    # 2337 (Cắt cụt đầu câu)
    (
        "Hồ Chí Minh như Trần Xuân Soạn và Hồ Học Lãm xuất hiện tình trạng ngập .",
        []
    ),
    # 2338 (Khuyến cáo chung không có địa danh)
    (
        "Cơ quan khí tượng lưu ý các địa phương và người dân chủ động theo dõi thông tin dự báo diễn biến mưa , triều cường , nhất là tại những khu vực thường xảy ra ngập ; đồng thời chủ động các biện pháp phòng ngừa nhằm hạn chế ảnh hưởng đến đời sống , sinh hoạt và việc đi lại .",
        []
    ),
    # 2339 (Đường Trần Xuân Soạn)
    (
        "Đường Trần Xuân Soạn ngập do triều cường chiều 27 / 9 .",
        [([0, 1, 2, 3], [4], 'NEG')]
    ),
    # 2340 (Kỹ thuật nâng đê)
    (
        "Tại TP. Hồ Chí Minh , Tuyến 1 nâng cao khoảng 40cm so với mặt đê hiện hữu , dài hơn 480m .",
        []
    ),
    # 2341 (Phường Thuận An - Bình Dương -> Ngoại tỉnh)
    (
        "Theo Chủ tịch UBND phường Thuận An Nguyễn Thanh Sơn , phường tiếp tục duy trì lực lượng và phương tiện ứng trực , thường xuyên kiểm tra các tuyến bờ bao , khu vực trũng thấp , cống thoát nước ; chủ động cảnh báo , xử lý những điểm có nguy cơ tràn bờ , sạt lở , ngập sâu , bảo đảm an toàn cho người dân .",
        []
    ),
    # 2342 (đường Trần Xuân Soạn, phường Tân Thuận)
    (
        "Chiều 27 . 9 . 2026 , đúng vào giờ tan tầm , đường Trần Xuân Soạn , phường Tân Thuận , TP. HCM xuất hiện ngập do triều cường .",
        [([13, 14, 15, 16], [26], 'NEG'), ([18, 19, 20], [26], 'NEG')]
    ),
    # 2343 (TP. HCM xuất hiện ngập)
    (
        "Khoảng 16 giờ chiều 28 . 9 . 2026 , khi nước triều bắt đầu dâng , nhiều tuyến đường ở TP. HCM đồng loạt xuất hiện ngập .",
        [([21, 22], [27], 'NEG')]
    ),
    # 2344 (Cắt tiền tố thừa vì thân bài có Bình Tân)
    (
        "Con gái e nói : ” có thể nhìn thấy biển tại Bình Tân , HCM . ” 🤣 Mưa đã tạnh đc 3 tiếng rồi mà còn ngập cỡ đó .",
        [([12, 13], [28, 29, 30], 'NEG')]
    ),
    # 2345 (PouYuen Bình Tân)
    (
        "PouYuen Bình Tân lại trong biển nước",
        [([0, 1, 2], [4, 5, 6], 'NEG')]
    ),
    # 2346 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Hôm nay ngập nhiều hơn rồi , mọi người đi đường chú ý nha .",
        [([1], [5, 6, 7], 'NEG')]
    ),
    # 2347 (Cắt tiền tố thừa vì thân bài có TP HCM)
    (
        "Người dân TP HCM chật vật đi làm giữa mưa ngập , ùn tắc",
        [([2, 3], [9, 10], 'NEG')]
    ),
    # 2348 (Đường Phan Huy Ích)
    (
        "Đường Phan Huy Ích ngập sâu cả mét , nhiều người mắc kẹt tới nửa đêm sau cơn mưa lớn chiều 30 . 9 .",
        [([0, 1, 2, 3], [4, 5, 6, 7], 'NEG')]
    ),
    # 2349 (Phan Huy Ích)
    (
        "30 / 9 Tối Nay Ở Tân Bình | Phan Huy Ích Ngập Thế Này Sao ?",
        [([9, 10, 11], [12], 'NEG')]
    ),
    # 2350 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nước ngập tràn đường phố # ketxe",
        [([1], [4, 5], 'NEG')]
    ),
    # 2351 (Cắt tiền tố thừa vì thân bài có TP HCM)
    (
        "Nước ngập sân trường ở TP HCM , học sinh bì bõm vào lớp",
        [([5, 6], [1], 'NEG')]
    ),
    # 2352 (Hỏi vai trò cống)
    (
        "Cống Phú Định trên Kênh Đôi có vai trò gì trong việc chống ngập ?",
        []
    ),
    # 2353 (Chuẩn hóa lặp từ do scraping)
    (
        "TPHCM ngập 20 - 30 cm , phương tiện di chuyển khó khăn , nhiều xe máy chết máy .",
        [([0], [1, 2, 3, 4, 5], 'NEG')]
    ),
    # 2354 (Nhận xét chung không có địa danh)
    (
        "Tại TP. Hồ Chí Minh , Đáng chú ý , thời điểm ngập thường trùng giờ cao điểm , ảnh hưởng trực tiếp đến việc đi lại của người dân , học sinh .",
        []
    ),
    # 2355 (Chuẩn hóa lặp từ do scraping)
    (
        "TPHCM khiến nhiều tuyến đường kẹt xe và ngập sâu , có nơi ngập ngang yên xe máy .",
        [([0], [8, 9], 'NEG')]
    ),
    # 2356 (đường Linh Đông)
    (
        "Khu vực giao với đường Linh Đông ngập nặng nhất , dòng nước cuồn cuộn gây khó khăn cho người đi đường .",
        [([4, 5, 6], [7, 8, 9], 'NEG')]
    ),
    # 2357 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Cũng là ngập nhưng mỗi người đón",
        []
    ),
    # 2358 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , cái ngập khác nhau , chị gái lội nước đi",
        []
    ),
    # 2359 (Tản văn quê tôi)
    (
        "Tại TP. Hồ Chí Minh , Bình minh quê tôi ngập như gì .",
        []
    ),
    # 2360 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Cứ mưa là lại ngập ở nhiều nơi !",
        [([1], [7], 'NEG')]
    ),
    # 2361 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Thế nhưng mưa tí là ngập",
        []
    ),
    # 2362 (Sai chính tả teencode)
    (
        "Tại TP. Hồ Chí Minh , ối đồi ôi , đây là video hồi tối e nói thấy có người live nuic ngập phần huy ích .",
        []
    ),
    # 2363 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Ngập gì mà nửa người thấy ớn ăn trời !",
        [([1], [3], 'NEG')]
    ),
    # 2364 (Bangkok -> Nước ngoài)
    (
        "Tại TP. Hồ Chí Minh , Bangkok ngập nước 29 / 9 # jackduky # bangkokngapnuoc",
        []
    ),
    # 2365 (Chợ đầu mối thủ đức)
    (
        "Chợ đầu mối thủ đức ngập luôn rồi anh chị ơi , chạy xe cẩn thận nha anh chị # LIVEIncentiveProgram # LIVEIsEasy # PaidPartnership",
        [([0, 1, 2, 3, 4], [5], 'NEG')]
    ),
    # 2366 (đường Linh Đông)
    (
        "Khu vực giao với đường Linh Đông ngập nặng nhất , dòng nước cuồn cuộn gây khó khăn cho người đi đường",
        [([4, 5, 6], [7, 8, 9], 'NEG')]
    ),
    # 2367 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Đường ngập nước nguy hiểm , xe dễ tắt máy .",
        [([1], [4, 5], 'NEG')]
    ),
    # 2368 (đường Linh Đông)
    (
        "Khu vực giao với đường Linh Đông ngập nặng nhất , dòng nước cuồn cuộn gây khó khăn cho người đi đường # xuhuong",
        [([4, 5, 6], [7, 8, 9], 'NEG')]
    ),
    # 2369 (TPHCM)
    (
        "Mưa lớn vào chiều 30 / 9 đúng giờ tan tầm khiến nhiều tuyến đường TPHCM ngập sâu , hàng loạt xe tắt máy , người dân bì bõm lội nước về nhà # tiktoknews # amm",
        [([15], [16, 17], 'NEG')]
    ),
    # 2370 (Cắt tiền tố thừa vì thân bài có Bình Tân)
    (
        "Bình Thành Bình Tân ngập sâu",
        [([2, 3], [4, 5], 'NEG')]
    ),
    # 2371 (Cắt tiền tố thừa vì thân bài có HCM)
    (
        "Cập nhật tin tức 29 / 9 , HCM ngập nhiều ngày",
        [([8], [9, 10, 11], 'NEG')]
    ),
    # 2372 (Bangkok -> Nước ngoài)
    (
        "Tại TP. Hồ Chí Minh , # xuhuonlgtiktok BANGKOK Ngập lụt lịch sử # ngaplut # bangkok",
        []
    ),
    # 2373 (Bình Dương -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , em ở đây ngập hư hỏng hết đồ trong nhà rồi , 🥹 🥹 Đường NA3 , chánh phú hoà , BC BD mưa lớn tối 28 / 09 / 2026 # myphuoc3 # bencat # binhduong # myphuoc # ngaplut",
        []
    ),
    # 2374 (Thái Lan -> Nước ngoài)
    (
        "Tại TP. Hồ Chí Minh , CEO Thái Lan lãnh án tù vì drift bằng mô tô nước giữa đường ngập lụt",
        []
    ),
    # 2375 (Bangkok -> Nước ngoài)
    (
        "Tại TP. Hồ Chí Minh , Bangkok ngập thì cứ ngập , còn có ván thì cứ đem ra chèo # topcomments # bangkok # thailan # ngaplut # vanluotsong",
        []
    ),
    # 2376 (Bangkok -> Nước ngoài)
    (
        "Tại TP. Hồ Chí Minh , Bangkok ngập nặng , người dân biến đường phố thành ' chợ nổi '",
        []
    ),
    # 2377 (Bangkok -> Nước ngoài)
    (
        "Tại TP. Hồ Chí Minh , Người dân Bangkok biến phố ngập thành ' chợ nổi '",
        []
    ),
    # 2378 (Thái Lan -> Nước ngoài)
    (
        "Tại TP. Hồ Chí Minh , Điều người ta sợ nhất khi mưa lớn và ngập nước ở Thái Lan : | # topcomments # casau # xongchuong # thailan # ngaplut",
        []
    ),
    # 2379 (Bangkok -> Nước ngoài)
    (
        "Tại TP. Hồ Chí Minh , Mưa lớn kéo dài đã khiến thủ đô Bangkok của Thái Lan phải tuyên bố tình trạng thảm họa do ngập lụt nghiêm trọng tại nhiều khu vực .",
        []
    ),
    # 2380 (Sài Gòn)
    (
        "Sài Gòn mùa nước ngập .",
        [([0, 1], [3, 4], 'NEG')]
    ),
    # 2381 (Rạch Cùng)
    (
        "Triều cường dâng , người dân Rạch Cùng lội nước từ sáng sớm",
        [([6, 7], [8, 9], 'NEG')]
    ),
    # 2382 (Cần Thơ -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , Combo nước ngập + kẹt xe + cúp điện # cantho # trieucuong",
        []
    ),
    # 2383 (Khuyến cáo chung)
    (
        "Tại TP. Hồ Chí Minh , Người dân chủ động theo dõi tình hình , hạn chế đi qua khu vực ngập sâu .",
        []
    ),
    # 2384 (Bangkok -> Nước ngoài)
    (
        "Tại TP. Hồ Chí Minh , nước ngập bangkok # jackduky # bangkok",
        []
    ),
    # 2385 (Bangkok -> Nước ngoài)
    (
        "Tại TP. Hồ Chí Minh , Bangkok ngập sâu sau trận mưa lớn , người dân cầu cứu : ' Nước ngập tới cổ tôi rồi ' # znews # tiktoknews",
        []
    ),
    # 2386 (Caption meme vui)
    (
        "Tại TP. Hồ Chí Minh , sg sống nhanh quá , làm tí mưa ngập cho mn chậm lại 😶 ‍ 🌫 ️ 😶 ‍ 🌫 ️",
        []
    ),
    # 2387 (Sài Gòn - ngập nước)
    (
        "Sài Gòn đang chạy đua với ngập nước : 10 . 000 tỷ đồng cho dự án ngăn triều và thêm 7 . 688 tỷ đồng cho các dự án chống ngập mới .",
        [([0, 1], [5, 6], 'NEG')]
    ),
    # 2388 (Cắt cụt đầu câu)
    (
        "của thành phố Hồ Chí Minh ( cũ ) bị ngập nặng .",
        []
    ),
    # 2389 (Kỹ thuật xe thủy kích)
    (
        "Tại TP. Hồ Chí Minh , Đã làm rất nhiều phương tiện tham gia giao thông vào khu vực ngập bị thủy kích .",
        []
    ),
    # 2390 (Hướng dẫn kỹ thuật xe thủy kích)
    (
        "Tại TP. Hồ Chí Minh , Nếu các Bác tài lỡ đi vào khu vực ngập mà xe bị thủy kích , bị tắt máy thì :",
        []
    ),
    # 2391 (Mở rộng Triều cường ở TPHCM)
    (
        "Triều cường ở TPHCM vượt báo động 3 , giáo viên dùng xe chở cơm đưa học sinh qua vùng ngập",
        [([0, 1, 2, 3], [17, 18], 'NEG')]
    ),
    # 2392 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Mưa lớn - triều cường lên cao - hẻm ngập trắng xóa - nước chảy như sông !",
        [([1], [12, 13, 14], 'NEG')]
    ),
    # 2393 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Xe máy trong sân ngập nửa bánh - khách trong quán trú mưa - ly cà phê đá vẫn nóng !",
        [([1], [7, 8, 9], 'NEG')]
    ),
    # 2394 (Khuyên can chung chung)
    (
        "Tại TP. Hồ Chí Minh , Anh em ra đường nhớ cẩn thận - đi chậm - tránh chỗ ngập sâu nha !",
        []
    ),
    # 2395 (Bangkok Thái Lan -> Nước ngoài)
    (
        "Tại TP. Hồ Chí Minh , Thái Lan : Áp dụng tình trạng khẩn cấp do Bangkok ngập nặng",
        []
    ),
    # 2396 (48 tỉnh Thái Lan -> Nước ngoài)
    (
        "Tại TP. Hồ Chí Minh , 48 tỉnh Thái Lan ngập lụt , thiệt hại hàng chục nghìn tỷ baht",
        []
    ),
    # 2397 (Bangkok Thái Lan -> Nước ngoài)
    (
        "Tại TP. Hồ Chí Minh , Ngày 26 / 9 , Thống đốc Bangkok Chadchart Sittipunt ký quyết định đưa toàn bộ 50 quận của thủ đô Thái Lan vào diện chịu ảnh hưởng bởi thiên tai , sau gần 48 giờ mưa lớn gây ngập diện rộng , ảnh hưởng sinh hoạt và giao thông .",
        []
    ),
    # 2398 (Bangkok Thái Lan -> Nước ngoài)
    (
        "Tại TP. Hồ Chí Minh , CEO Thái Lan lĩnh án tù vì cưỡi môtô nước giữa Bangkok ngập lụt # ceothailan # cuoimotonuoc # ceothailanlinhantu # bangkokngaplut # danviet # tintuc # danvietviral",
        []
    ),
    # 2399 (Kỹ thuật bảo dưỡng xe điện)
    (
        "Tại TP. Hồ Chí Minh , Quy trình xử lý khi xe bị ngập nước VF5 # tranbathien # xecongnghe",
        []
    ),
    # 2400 (Câu hỏi bàn luận)
    (
        "Dự án chống ngập 10 . 000 tỷ của Sài Gòn chống ngập thế nào ?",
        []
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
    for idx, (text, triplets) in enumerate(batch24_data, 2301):
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
        print("TẤT CẢ CÁC TRIPLETS CỦA BATCH 24 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!")
    else:
        print(f"CÓ {errors} LỖI CẦN SỬA!")
    return errors

if __name__ == '__main__':
    assert len(batch24_data) == 100, f"Expected 100 records, got {len(batch24_data)}"
    err_cnt = test_triplets()
    if err_cnt > 0:
        import sys
        sys.exit(1)
        
    phase3_path = "data/validate_label/thuan/phase3.txt"
    with open(phase3_path, "r", encoding="utf-8") as f:
        lines = [l for l in f.readlines() if l.strip()]
    
    base_2300 = lines[:2300]
    assert len(base_2300) == 2300, f"Expected 2300 existing lines, found {len(base_2300)}"
    
    new_lines = [format_line(t, tr) for t, tr in batch24_data]
    
    all_lines = base_2300 + new_lines
    with open(phase3_path, "w", encoding="utf-8") as f:
        f.writelines(all_lines)
        
    print(f"Successfully updated {len(all_lines)} lines to {phase3_path}!")
