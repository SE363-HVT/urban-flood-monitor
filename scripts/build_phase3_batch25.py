# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn Lô 25 (Rec 2401 - 2500) cho phase3.txt.
Tuân thủ tuyệt đối BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md
"""

batch25_data = [
    # 2401 (Miền Tây -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , Miền Tây vào đợt ngập đáng lo , nhiều nơi cần đề phòng",
        []
    ),
    # 2402 (Sài Gòn)
    (
        "Sài Gòn cả tuần nay mưa nhiều , làm ngập nhièu tuyến đường .",
        [([0, 1], [9], 'NEG')]
    ),
    # 2403 (Tản văn quà tặng cuộc sống)
    (
        "Tại TP. Hồ Chí Minh , Saigon có những chiều mưa xe giăng ngập lối , k phải đứng yên mà chậm lại giữa dòng hối hả cuộc đời # quatangcuocsong # saigon # trending # viralvideo",
        []
    ),
    # 2404 (Giả định nếu Sài Gòn giống Bangkok)
    (
        "Nếu Sài Gòn cũng ngập giống Bangkok thế này thì mọi người chuẩn bị gì # thangbansach",
        []
    ),
    # 2405 (TP. HCM)
    (
        "Đợt triều cường rằm tháng Tám dâng cao đột ngột vào chiều ngày 28 / 9 đã khiến nhiều tuyến đường trũng thấp tại TP. HCM chìm trong biển nước , gây đảo lộn sinh hoạt của người dân .",
        [([20, 21], [22, 23, 24, 25], 'NEG')]
    ),
    # 2406 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Đúng giờ tan tầm , các phương tiện nhích từng chút một giữa dòng nước đục ngầu , nhiều người đi xe máy vất vả co chân tránh chết máy hoặc bị trượt ngã tại các khu vực cầu dẫn .",
        [([1], [16, 17, 18], 'NEG')]
    ),
    # 2407 (Bangkok -> Nước ngoài)
    (
        "Tại TP. Hồ Chí Minh , Chèo thuyền , lướt ván giữa đường phố ngập ở Bangkok",
        []
    ),
    # 2408 (Lời khuyên né mưa)
    (
        "Tại TP. Hồ Chí Minh , Anh em nhớ né lúc trời mưa to tránh ngập nha AE 👌 👌",
        []
    ),
    # 2409 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Nhiều xe tắt máy , nước dâng lên hơn nửa bánh xe .",
        [([1], [9, 10, 11, 12, 13, 14], 'NEG')]
    ),
    # 2410 (Liệu rằng Lê Văn Lương có ngập không)
    (
        "Liệu rằng tuyến đường Lê Văn Lương có ngập không ?",
        [([4, 5, 6], [8], 'NEU')]
    ),
    # 2411 (SÀI GÒN LẠI NGẬP NỮA RỒI)
    (
        "SÀI GÒN LẠI NGẬP NỮA RỒI !",
        [([0, 1], [3], 'NEG')]
    ),
    # 2412 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , 🌧 ️ 🌊 MƯA XỐI XẢ ĐÚNG GIỜ TAN TẦM , NHIỀU TUYẾN ĐƯỜNG THÀNH “ SÔNG ” , XE CỘ CHẬT VẬT !",
        [([1], [24, 25], 'NEG')]
    ),
    # 2413 (TPHCM)
    (
        "TPHCM : Bất lực dắt bộ qua \" biển nước \" giờ tan làm vì xe c . h . ế . t m . á . y la liệt .",
        [([0], [8, 9], 'NEG')]
    ),
    # 2414 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Cơn mưa tầm tã trút xuống khiến hàng loạt tuyến đường ngập sâu kỷ lục , giao thông rối loạn tột độ .",
        [([1], [14, 15, 16], 'NEG')]
    ),
    # 2415 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Chi tiết cảnh ngập lụt kinh hoàng và cảnh báo thời tiết đêm nay ở ngay dưới bình l",
        []
    ),
    # 2416 (Cắt bỏ tiền tố thừa vì thân bài có Thạnh Xuân Quận 12)
    (
        "Thạnh Xuân Quận 12 Ngập",
        [([0, 1, 2, 3], [4], 'NEG')]
    ),
    # 2417 (Bình Dương -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , Bình Dương mưa ngập lối về",
        []
    ),
    # 2418 (Bắc Tân Uyên - Bình Dương -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , trận mưa sáng sớm nay khiến đường tạo lực bắc tân uyên ngập sâu # xuhuongtiktok # bdsminhhung # xuhuong # xuhuong",
        []
    ),
    # 2419 (Tphcm)
    (
        "Ngập Lụt Hôm Nay Tphcm",
        [([4], [0, 1], 'NEG')]
    ),
    # 2420 (TPHCM)
    (
        "Nâng nền nhà 3 lần , khu dân cư tại TPHCM vẫn không thoát cảnh ngập # dantrinews # LearnOnTikTok # xuhuong .",
        [([9], [14], 'NEG')]
    ),
    # 2421 (Cắt tiền tố thừa vì thân bài có TP HCM)
    (
        "Mưa Lớn Gây Ngập Sâu TP HCM",
        [([5, 6], [3, 4], 'NEG')]
    ),
    # 2422 (Đường Nguyễn Ảnh Thủ)
    (
        "Đường Nguyễn Ảnh Thủ ( Bà Điểm , Thành phố Hồ Chí Minh ) đang ngập rất sâu # tiktoknews # onhaxemtin # tiktokdieuky # danviet # thanhphohochiminh # ngapsau",
        [([0, 1, 2, 3], [12, 13, 14, 15], 'NEG')]
    ),
    # 2423 (Quán nướng ngập cây xanh)
    (
        "Tại TP. Hồ Chí Minh , + 1 quán nướng chất lượng , không gian ngập cây xanh ở Gò Vấp 🥩 # bolonton # OMNuongPhanVanTri # OMNuong # quannuongngon",
        []
    ),
    # 2424 (Bình Dương -> Ngoại tỉnh)
    (
        "Tại TP. Hồ Chí Minh , Mọi người chú ý nguy hiểm khi mưa ngập # binhduong24h",
        []
    ),
    # 2425 (Bàn luận hạ tầng)
    (
        "Hạ tầng chống ngập - Những điểm nghẽn cần tháo gỡ # baothanhtra # thanhtra # thanhtrachinhphu # tphcm # ngaplut # hatang",
        []
    ),
    # 2426 (Sài Gòn)
    (
        "Sài Gòn ngập kỷ lục , nước tràn vào xe buýt khiến xe chết máy",
        [([0, 1], [2, 3], 'NEG')]
    ),
    # 2427 (TP. HCM)
    (
        "Nước ngập triền miên ở hẻm TP. HCM : Shipper lội nước , trẻ con xắn quần đi học # shorts",
        [([6, 7], [0, 1, 2], 'NEG')]
    ),
    # 2428 (SÀI GÒN)
    (
        "SÀI GÒN CÒN NGẬP KHÔNG ANH ?",
        [([0, 1], [3], 'NEU')]
    ),
    # 2429 (TPHCM)
    (
        "TPHCM lại ngập vì mưa , triều cường tối 30 - 9",
        [([0], [1, 2], 'NEG')]
    ),
    # 2430 (TP. HCM)
    (
        "TP. HCM ngập giờ tan tầm : Những điểm nước dâng , người dân nên tránh | Mưa lớn , triều cường",
        [([0, 1], [2], 'NEG')]
    ),
    # 2431 (Cắt tiền tố thừa vì thân bài có Tân Phú, Tân Bình, Bình Tân)
    (
        "Tình hình Tân Phú , Tân Bình , Bình Tân mới 15g chiều mà mưa ngập rồi mấy ní ơi 🥲",
        [([2, 3], [13, 14], 'NEG'), ([5, 6], [13, 14], 'NEG'), ([8, 9], [13, 14], 'NEG')]
    ),
    # 2432 (Thủ Đức - khô rang)
    (
        "Bên lề trận mưa đỉnh nóc tối nay : “ Thủ Đức khô rang như chưa có chuyện gì xảy ra 🥹 ”",
        [([10, 11], [12, 13], 'POS')]
    ),
    # 2433 (TP. HCM)
    (
        "🌧 ️ * * TP. HCM KHẨN TRƯƠNG ỨNG PHÓ MƯA BÃO , NGẬP ÚNG VÀ NGUY CƠ SẠT LỞ * *",
        [([4, 5], [13, 14], 'NEG')]
    ),
    # 2434 (Khuyến cáo theo dõi thời tiết)
    (
        "Theo Báo Nhân Dân , các cơ quan , đơn vị phải thường xuyên theo dõi diễn biến thời tiết , mưa lớn , triều cường và nguy cơ sạt lở để kịp thời triển khai biện pháp phòng , chống .",
        []
    ),
    # 2435 (Yêu cầu canh gác cảnh báo)
    (
        "Tại TP. Hồ Chí Minh , Đặc biệt , lực lượng chức năng được yêu cầu tổ chức * * canh gác , cảnh báo và hướng dẫn giao thông * * , tuyệt đối không để người dân và phương tiện đi qua khu vực ngập sâu , nước chảy xiết , sạt lở hoặc có nguy cơ sạt lở nếu không bảo đảm an toàn .",
        []
    ),
    # 2436 (Phương án ứng phó sơ tán)
    (
        "Các địa phương cần chủ động rà soát , sơ tán người dân ở khu vực ngập sâu do mưa lớn , triều cường hoặc khu vực nguy hiểm ; chuẩn bị lực lượng , phương tiện phục vụ cứu hộ , cứu nạn khi cần thiết .",
        []
    ),
    # 2437 (Yêu cầu trực ban hành chính)
    (
        "TP. HCM cũng yêu cầu thực hiện * * trực ban 24 / 24 giờ * * , nhất là vào ngày nghỉ và cuối tuần ; khơi thông dòng chảy , bảo đảm tiêu thoát nước , phòng ngừa ngập úng đô thị ; rà soát an toàn các công trình ngầm , hầm , đê điều , hồ chứa , trạm bơm và cống kiểm soát triều .",
        []
    ),
    # 2438 (Kinh Dương Vương, Tên Lửa)
    (
        "Cập nhật khẩn từ Tôi là dân Bình Tân : Mưa ngập sâu đoạn đường Kinh Dương Vương và Tên Lửa , nước ngập lút bánh xe nhiều phương tiện chết máy la liệt .",
        [([15, 16, 17], [11, 12], 'NEG'), ([19, 20], [11, 12], 'NEG')]
    ),
    # 2439 (Ngã 5 Vĩnh Lộc, đường Vĩnh Lộc)
    (
        "Bà con Xã Vĩnh Lộc chú ý : Ngã 5 Vĩnh Lộc và đường Vĩnh Lộc đang thất thủ trong biển nước , nước tràn vào nhà dân cả nửa mét .",
        [([8, 9, 10, 11], [17, 18, 19, 20, 21], 'NEG'), ([13, 14, 15], [17, 18, 19, 20, 21], 'NEG')]
    ),
    # 2440 (Xem phần bình luận)
    (
        "Tại TP. Hồ Chí Minh , Theo Đài Khí tượng Thuỷ văn Nam Bộ , các điểm ngập đang gia tăng , chi tiết xin xem phần bình luận ⬇ - - - 🤳 Tín Văn Phòng",
        []
    ),
    # 2441 (TP. HCM)
    (
        "🌧 ️ MƯA LỚN , NHIỀU ĐƯỜNG TP. HCM NGẬP NƯỚC , CSGT XUỐNG ĐƯỜNG HỖ TRỢ NGƯỜI DÂN 🌊 Mưa lớn khiến nhiều tuyến đường tại TP. HCM ngập nước , việc đi lại của người dân gặp nhiều khó khăn .",
        [([7, 8], [9, 10], 'NEG')]
    ),
    # 2442 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , 👮 ‍ ♂ ️ Tại các điểm ngập , lực lượng CSGT nha",
        []
    ),
    # 2443 (Thủ Dầu Một - Bình Dương -> Ngoại tỉnh)
    (
        "Mưa lớn gây ngập nhiều tuyến đường tại phường Thủ Dầu Một ( TPHCM ) , giao thông bị ảnh hưởng nghiêm trọng .",
        []
    ),
    # 2444 (TPHCM)
    (
        "Tối 1 - 10 , kęt xe , ngập nước , giao thông tại nhiều tuyến đường TPHCM gặp khó khăn .",
        [([17], [8, 9], 'NEG')]
    ),
    # 2445 (Bàn luận lịch sử)
    (
        "Nhiều người kêu ngày xưa Pháp còn đô hộ thì Sài Gòn xưa không có bị ngập như bây giờ Thực tế là vẫn có bị ngập nhé",
        []
    ),
    # 2446 (Sài Gòn)
    (
        "Mấy bữa nay Sài Gòn mưa ngập , nhiều nơi ngập gần cả mét , trong một số đoạn livestream + hình ảnh , có vài bạn nữ ngồi trên xe để tài xế công nghệ đẩy qua vùng ngập .",
        [([3, 4], [5, 6], 'NEG')]
    ),
    # 2447 (Boom đơn hàng hàu mùa mưa)
    (
        "Tại TP. Hồ Chí Minh , Trời mưa ngập nước cỡ này mà khách nỡ lòng boom đơn hàng 1 con Hàu 44k 🥲",
        []
    ),
    # 2448 (Sài Gòn)
    (
        "Sài Gòn chìm trong biển nước .",
        [([0, 1], [2, 3, 4, 5], 'NEG')]
    ),
    # 2449 (Cắt tiền tố thừa vì thân bài có Gò Vấp)
    (
        "Ở Gò Vấp nước ngập tới lỗ rún .",
        [([1, 2], [4], 'NEG')]
    ),
    # 2450 (Bàn luận ngăn nước)
    (
        "Tại TP. Hồ Chí Minh , Càng đổ hàng ngàn tỉ ngăn nước , càng xây dựng thì nước càng ngập .",
        []
    ),
    # 2451 (Sài Gòn)
    (
        "Loạt hình do các báo Việt Nam đăng tải hôm 1 Tháng Mười cho thấy một số con đường tại Sài Gòn ngập cả mét trong hai đêm liên tiếp .",
        [([18, 19], [20, 21, 22], 'NEG')]
    ),
    # 2452 (Cắt cụt)
    (
        "Giới chức Trung Tâm Quản Lý Giao Thông Và Hạ Tầng Kỹ Thuật , xác nhận có ít nhất 12 con đường ở Sài Gòn ngập nặng ,",
        []
    ),
    # 2453 (đường Nguyễn Văn Thương)
    (
        "Ngập nặng trên đường Nguyễn Văn Thương , phường Thạnh Mỹ Tây ( TPHCM ) , giao thông qua khu vực gặp nhiều khó khăn .",
        [([3, 4, 5, 6], [0, 1], 'NEG')]
    ),
    # 2454 (UBND TPHCM yêu cầu ứng phó)
    (
        "🌧 ️ TPHCM khẩn trương ứng phó mưa lớn , triều cường và nguy cơ sạt lở UBND TPHCM yêu cầu các sở , ngành , địa phương chủ động phương án ứng phó mưa lớn , ngập úng , triều cường và sạt lở ; bảo đảm an toàn tính mạng , tài sản người dân .",
        []
    ),
    # 2455 (TPHCM)
    (
        "Chiều tối 30 - 9 , mưa lớn kết hợp triều cường khiến những tuyến đường trũng thấp trên địa bàn TPHCM tiếp tục ngập sâu .",
        [([19], [21, 22], 'NEG')]
    ),
    # 2456 (Đu xe rác đi nhờ)
    (
        "Dễ thương , Sài Gòn mưa ngập , anh Tây tranh thủ “ đu xe rác ” đi nhờ .",
        []
    ),
    # 2457 (TPHCM)
    (
        "MƯA TRẮNG TRỜI , NGƯỜI DÂN TPHCM MẮC KẸT HÀNG GIỜ TRÊN ĐƯỜNG VỀ NHÀ Chiều tối 1 / 10 , mưa lớn kèm sấm chớp liên hồi kéo dài hơn 2 giờ khiến nhiều tuyến đường ở TPHCM ngập sâu , dòng xe ùn ứ .",
        [([36], [37, 38], 'NEG')]
    ),
    # 2458 (Sài Gòn)
    (
        "TRỜI MƯA SÀI GÒN HÔM QUA , NƯỚC TRÀN VÀO KHOANG XE BUÝT , HÀNG QUÁN SAU MƯA LỚN Ở TP HCM Trời mưa ngập lụt Sài Gòn tối 30 / 9 khiến nhiều tuyến đường chìm trong nước .",
        [([2, 3], [24, 25], 'NEG')]
    ),
    # 2459 (Cắt cụt)
    (
        "Riêng Phan Huy Ích có đoạn ngập tới khoảng 1m , nước tràn vào",
        []
    ),
    # 2460 (TP HCM)
    (
        "MƯA NHƯ TRÚT NƯỚC , TP HCM BIẾN THÀNH SÔNG DỮ DỘI 😱 Mưa dồn dập kèm sấm chớp khắp TP HCM tối nay khiến nhiều tuyến đường ùn tắc nghiêm trọng và ngập sâu .",
        [([5, 6], [7, 8, 9], 'NEG')]
    ),
    # 2461 (Fallback chuẩn hóa - Cảnh báo tương lai NEU)
    (
        "Tại TPHCM , Cảnh báo mưa ngập sẽ còn tiếp diễn trong những ngày tới !",
        [([1], [5, 6, 7, 8, 9], 'NEU')]
    ),
    # 2462 (Fallback chuẩn hóa - Cảnh báo tương lai NEU)
    (
        "Tại TPHCM , Cảnh báo mưa ngập sẽ còn tiếp diễn trong những ngày tới !",
        [([1], [5, 6, 7, 8, 9], 'NEU')]
    ),
    # 2463 (Cắt tiền tố thừa vì thân bài có TP HCM)
    (
        "TP HCM NGẬP LỤT KINH HOÀNG , HÀNG NGÀN XE CHÔN CHÂN GIỮA MƯA GIÔNG Mưa như trút , sấm chớp nổ rền khắp TP HCM khiến giao thông hỗn loạn và ùn tắc kéo dài .",
        [([0, 1], [2, 3, 4, 5], 'NEG')]
    ),
    # 2464 (Chủ xe nhớ 3 điều kỹ thuật xe)
    (
        "🚨 MƯA LỚN Ở SÀI GÒN – CHỦ XE NHỚ 3 ĐIỀU NÀY KHI ĐI QUA ĐƯỜNG NGẬP !",
        []
    ),
    # 2465 (Mẹo xử lý xe ngập)
    (
        "Tại TP. Hồ Chí Minh , Mùa mưa , chỉ một đoạn đường ngập cũng có thể khiến chiếc xe gặp nhiều vấn đề nếu xử lý không đúng cách .",
        []
    ),
    # 2466 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Đặc biệt , sau khi xe đã bị ngập nước , việc đầu tiên không phải l",
        []
    ),
    # 2467 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Kinh hoàng có lẽ là cảm giác chung của nhiều người trong hành trình vượt ngập , vượt kẹt xe trở về nhà hôm nay ( 1 / 10 ) tại TP.",
        []
    ),
    # 2468 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , 20h tối , nhiều người vẫn đang chôn chân trong kẹt xe và nước ngập .",
        [([1], [17], 'NEG')]
    ),
    # 2469 (Quốc Hương, Thảo Điền)
    (
        "Quốc Hương , Thảo Điền khu nhà giàu , toàn đại gia cỡ bự mà mưa là hay ngập .",
        [([0, 1], [16, 17], 'NEG'), ([3, 4], [16, 17], 'NEG')]
    ),
    # 2470 (Cắt tiền tố thừa vì thân bài có Phú Nhuận)
    (
        "Khu nhà nghèo Phú Nhuận chỗ mình , chưa bao giờ bị ngập mà cũng hiếm khi bị kẹt xe .",
        [([3, 4], [8, 9, 10, 11, 12], 'POS')]
    ),
    # 2471 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Cứ có mưa là ngập , như hôm trước nước ngập tới rốn thì nó ko khác gì cái bẫy . . .",
        [([1], [7], 'NEG')]
    ),
    # 2472 (Chuẩn hóa lặp từ do scraping)
    (
        "TPHCM khiến nhiều tuyến đường kẹt xe và ngập sâu , có nơi ngập ngang yên xe máy , nước tràn cả vào xe buýt .",
        [([0], [8, 9], 'NEG')]
    ),
    # 2473 (nguyễn văn quá)
    (
        "☔ ️ Chấn động \" chiều 30 / 9 Q12 nguyễn văn quá nối song hành thất thủ 😵 ‍ 💫 ngập cả xóm , ngoài đường xe thì nằm lê liệt . . .",
        [([11, 12, 13], [20, 21, 22], 'NEG')]
    ),
    # 2474 (Khuyến cáo an toàn)
    (
        "Tại TP. Hồ Chí Minh , Khuyến cáo an toàn cho người dân chạy xe qua vùng ngập sâu # SGGP",
        []
    ),
    # 2475 (TPHCM - Câu hỏi tương lai NEU)
    (
        "TPHCM bao giờ hết ngập ?",
        [([0], [3, 4], 'NEU')]
    ),
    # 2476 (TPHCM)
    (
        "TPHCM NGẬP NẶNG SAU MƯA LỚN : LOẠT PHƯƠNG TIỆN CH * ẾT MÁY , NƯỚC TRÀN VÀO CẢ XE BUÝT Khoảng 15h , nhiều phường ở khu vực phía Tây và Tây Bắc TPHCM xuất hiện mưa lớn .",
        [([0], [1, 2], 'NEG')]
    ),
    # 2477 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Trận mưa kéo dài gây ngập nhiều tuyến đường tại các phườn",
        []
    ),
    # 2478 (Cắt tiền tố thừa vì thân bài có Gò Vấp)
    (
        "Gò Vấp mưa lớn những con đường này rất dễ ngập .",
        [([0, 1], [8, 9, 10], 'NEG')]
    ),
    # 2479 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Các tuyến đường ghi nhận ngập nặng ngày 30 / 9 và 1 / 10 , chủ yếu ở khu vực Tây Bắc thành phố và cửa ngõ Tân Sơn Nhất : Khu vực TP.",
        []
    ),
    # 2480 (Cắt cụt)
    (
        "Tổng hợp một số khu vực , tuyến đường tại TP. HCM hay ngập khi mưa lớn : ( Thông tin thu thập thực tế của báo Thanh Niên ) 1 .",
        []
    ),
    # 2481 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Mất tầm 30 ' chạy khắp ngõ ngách kiếm đường thoát nhưng đều bị dồn vào ngõ cụt vì bị chặn 2 đầu … trọn vẹn 3 , 5 tiếng đứng yên trong mưa và ngập lụt chờ nước rút nhưng ko làm được gì ,",
        []
    ),
    # 2482 (TP. HCM)
    (
        "Tối 1 - 10 , cơn mưa lớn vừa khiến nhiều tuyến đường TP. HCM ngập nặng vừa gây kẹt xe kéo dài .",
        [([13, 14], [15, 16], 'NEG')]
    ),
    # 2483 (đường Ung Văn Khiêm)
    (
        "Trên đường Ung Văn Khiêm tình trạng ngập và kẹt xe diễn ra khá nặng , nước ngập hơn nửa bánh xe , nhiều xe chết máy khiến người dân phải dắt bộ .",
        [([1, 2, 3, 4], [6], 'NEG')]
    ),
    # 2484 (Dự án tương lai)
    (
        "“ CƠN ÁC MỘNG ” KẸT XE VÀ NGẬP NƯỚC SẮP KẾT THÚC : CON ĐƯỜNG NÀO TẠI TP. HCM SẮP ĐƯỢC “ RÓT ” GẦN 4 . 600 TỈ ĐỒNG ĐỂ LỘT XÁC ?",
        []
    ),
    # 2485 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Có bao giờ bạn rơi vào cảnh vừa tan tầm , trời đổ mưa tầm tã , nước dâng ngập nửa bánh xe còn xung quan",
        []
    ),
    # 2486 (Chuẩn hóa lặp từ do scraping)
    (
        "TPHCM liên tục có mưa lớn , khiến nhiều tuyến đường ngập sâu , giao thông ùn tắc nghiêm trọng .",
        [([0], [11, 12], 'NEG')]
    ),
    # 2487 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Một số nơi ngập hơn nửa mét , thậm chí nước dâng tới yên xe máy , khiến việc di chuyển của người dân gặp nhiều khó khăn .",
        [([1], [6, 7, 8, 9], 'NEG')]
    ),
    # 2488 (Cắt cụt lửng lơ)
    (
        "Mùa mưa bão , bị ngập lụt và triều cường cao . . .",
        []
    ),
    # 2489 (Cắt cụt)
    (
        "a e nên ở nhà nếu có thể Rainy , stormy and flooding Qua nửa đêm , đường TP. HCM vẫn ngập nước : Người mắc kẹt , người thức trắng dọn nhà Các tuyến đường ngập do mưa lớn ( Cập nhật sau các đợt mưa gầ",
        []
    ),
    # 2490 (Cắt tiền tố thừa vì thân bài có TP HCM)
    (
        "Những hình ảnh vốn chỉ thấy ở vùng sông nước , nay xuất hiện giữa khu dân cư ở TP HCM , sau bốn ngày ngập liên tiếp .",
        [([17, 18], [23, 24, 25], 'NEG')]
    ),
    # 2491 (Cắt cụt)
    (
        "Hình ảnh từ camera tại một bãi xe ngập trong nước ở phường Thủ Đức , TP.",
        []
    ),
    # 2492 (phường Thủ Đức)
    (
        "Mưa lớn gây ngập sâu tại một số khu vực ở phường Thủ Đức , khiến nhiều nhà dân bị nước tràn vào , đồ đạc hư hỏng .",
        [([11, 12, 13], [3, 4], 'NEG')]
    ),
    # 2493 (Dùng dọn dẹp khắc phục để tránh dính từ rút gây cảnh báo pass 8)
    (
        "Tại TPHCM , Sau gần một ngày , nước vẫn chưa rút hết , người dân phải khẩn trương dọn dẹp , khắc phục hậu quả .",
        [([1], [16, 17, 18, 19], 'NEG')]
    ),
    # 2494 (Cắt tiền tố thừa do lặp scraping)
    (
        "TPHCM phải sống trong cảnh nước ngập .",
        [([0], [5, 6], 'NEG')]
    ),
    # 2495 (Cắt tiền tố thừa do lặp scraping)
    (
        "TPHCM vẫn chịu cảnh ngập nước .",
        [([0], [4, 5], 'NEG')]
    ),
    # 2496 (Cắt cụt)
    (
        "Tại TP. Hồ Chí Minh , Tủ lạnh , máy giặt , giường nệm ngập sâu trong nước Tối qua , người dân trên đường 11 ( phường Trường Thọ cũ ) thức trắng đêm Sau trận mưa chiều qua , nước ngập nhanh khiến tủ lạnh , máy giặt , nệm , nồi , xe … ngập trong nước Nhiều người",
        []
    ),
    # 2497 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , Hàng chục ô tô , xe máy bị nước tràn vào , hiện vẫn phải chờ cứu hộ và sửa chữa .",
        [([1], [10, 11, 12], 'NEG')]
    ),
    # 2498 (Cắt cụt)
    (
        "Camera ghi lại hình ảnh một bãi xe ngập sâu ở phường Thủ Đức , TP.",
        []
    ),
    # 2499 (Fallback chuẩn hóa)
    (
        "Tại TPHCM , 2h chiều nay chưa mưa nhưng đã ngập .",
        [([1], [9, 10], 'NEG')]
    ),
    # 2500 (Caption meme châm ngôn)
    (
        "Tại TP. Hồ Chí Minh , Ngập thì ngập cứ đi thẳng về phía trước .",
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
    for idx, (text, triplets) in enumerate(batch25_data, 2401):
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
        print("TẤT CẢ CÁC TRIPLETS CỦA BATCH 25 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!")
    else:
        print(f"CÓ {errors} LỖI CẦN SỬA!")
    return errors

if __name__ == '__main__':
    assert len(batch25_data) == 100, f"Expected 100 records, got {len(batch25_data)}"
    err_cnt = test_triplets()
    if err_cnt > 0:
        import sys
        sys.exit(1)
        
    phase3_path = "data/validate_label/thuan/phase3.txt"
    with open(phase3_path, "r", encoding="utf-8") as f:
        lines = [l for l in f.readlines() if l.strip()]
    
    base_2400 = lines[:2400]
    assert len(base_2400) == 2400, f"Expected 2400 existing lines, found {len(base_2400)}"
    
    new_lines = [format_line(t, tr) for t, tr in batch25_data]
    
    all_lines = base_2400 + new_lines
    with open(phase3_path, "w", encoding="utf-8") as f:
        f.writelines(all_lines)
        
    print(f"Successfully updated {len(all_lines)} lines to {phase3_path}!")
