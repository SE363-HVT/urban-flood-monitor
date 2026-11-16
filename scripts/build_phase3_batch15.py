# -*- coding: utf-8 -*-
"""
Build Phase 3 Batch 15 (Records 1401 - 1500).
Tuân thủ 100% BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md.
"""

import sys

# Dữ liệu 100 records của Lô 15 (1401 - 1500)
# (text, [(aspect_span, opinion_span, polarity)])

batch15_data = [
    # 1401
    (
        "Sau cơn mưa chiều , đường Hoàng Diệu khô ráo hoàn toàn , giao thông qua khu vực ổn định bình thường .",
        [([5, 6, 7], [8, 9, 10, 11], 'POS')]
    ),
    # 1402
    (
        "Tuyến đường Bình Quới hôm nay khô ráo , các phương tiện di chuyển nhanh chóng .",
        [([1, 2, 3], [6, 7], 'POS')]
    ),
    # 1403
    (
        "Nhờ thoát nước nhanh , mặt đường Trần Xuân Soạn đã khô ráo , các cửa hàng bắt đầu mở cửa đón khách .",
        [([6, 7, 8, 9], [10, 11, 12], 'POS')]
    ),
    # 1404
    (
        "Bà con lưu thông qua Kha Vạn Cân an tâm nhé , khu vực này nước đã rút rồi .",
        [([5, 6, 7], [15, 16, 17], 'POS')]
    ),
    # 1405
    (
        "Tuyến đường Dương Văn Cam hôm nay không ngập , các phương tiện di chuyển nhanh chóng .",
        [([1, 2, 3, 4], [7, 8], 'POS')]
    ),
    # 1406
    (
        "Cập nhật giao thông Đinh Bộ Lĩnh hiện đi lại bình thường , không còn tình trạng xe chết máy .",
        [([4, 5, 6], [8, 9, 10, 11], 'POS')]
    ),
    # 1407
    (
        "Bà con qua Đặng Thị Rành chú ý nhé , hiện tại nước rút sạch rồi .",
        [([3, 4, 5], [10, 11, 12], 'POS')]
    ),
    # 1408
    (
        "Đến thời điểm này Phan Huy Ích đã thông thoáng , xe cộ di chuyển rất thuận lợi .",
        [([4, 5, 6], [8, 9], 'POS')]
    ),
    # 1409
    (
        "Bà con lưu thông qua Quốc Hương an tâm nhé , khu vực này nước đã rút rồi .",
        [([5, 6], [14, 15, 16], 'POS')]
    ),
    # 1410
    (
        "Tuyến đường Lê Đức Thọ hôm nay thông suốt , các phương tiện di chuyển nhanh chóng .",
        [([1, 2, 3, 4], [7, 8], 'POS')]
    ),
    # 1411
    (
        "Nhờ thoát nước nhanh , mặt đường An Dương Vương đã khô ráo , các cửa hàng bắt đầu mở cửa đón khách .",
        [([6, 7, 8, 9], [10, 11, 12], 'POS')]
    ),
    # 1412
    (
        "Mặt đường khu vực Kha Vạn Cân nước đã rút sạch , người dân phấn khởi đi lại .",
        [([4, 5, 6], [7, 8, 9, 10], 'POS')]
    ),
    # 1413
    (
        "Ghi nhận tại Quốc Hương đến thời điểm này khô queo , người dân đi lại dễ dàng không còn cảnh bì bõm .",
        [([3, 4], [9, 10], 'POS'), ([3, 4], [14, 15, 16, 17], 'POS')]
    ),
    # 1414
    (
        "Đoạn đường Quốc Hương sau khi triều cường hạ nước rút hết , cuộc sống sinh hoạt của bà con đã ổn định trở lại .",
        [([1, 2, 3], [9, 10, 11], 'POS')]
    ),
    # 1415
    (
        "Bà con lưu thông qua Hoàng Diệu an tâm nhé , khu vực này hết ngập hẳn rồi .",
        [([5, 6], [14, 15, 16], 'POS')]
    ),
    # 1416
    (
        "Đường Lê Đức Thọ chiều tối nay nước rút rất nhanh , người dân phấn khởi tan làm về nhà thuận tiện .",
        [([0, 1, 2, 3], [7, 8, 9, 10], 'POS')]
    ),
    # 1417
    (
        "Đến thời điểm này Bến Phú Định đã khô ráo , xe cộ di chuyển rất thuận lợi .",
        [([4, 5, 6], [8, 9], 'POS')]
    ),
    # 1418
    (
        "Bà con lưu thông qua Trần Xuân Soạn an tâm nhé , khu vực này khô rang rồi .",
        [([5, 6, 7], [15, 16], 'POS')]
    ),
    # 1419
    (
        "Sau khi mở van xả triều , khu vực Đào Trí nước rút nhanh , người dân không còn phải bì bõm lội nước .",
        [([9, 10], [11, 12, 13], 'POS')]
    ),
    # 1420
    (
        "Cập nhật giao thông Dương Văn Cam hiện hết ngập , không còn tình trạng xe chết máy .",
        [([4, 5, 6], [8, 9], 'POS')]
    ),
    # 1421
    (
        "Tuyến đường Tô Ngọc Vân hôm nay không ngập , các phương tiện di chuyển nhanh chóng .",
        [([1, 2, 3, 4], [7, 8], 'POS')]
    ),
    # 1422
    (
        "Nhờ thoát nước nhanh , mặt đường Quốc Hương ráo hoảnh , các cửa hàng bắt đầu mở cửa đón khách .",
        [([6, 7, 8], [9, 10], 'POS')]
    ),
    # 1423
    (
        "Nhờ thoát nước nhanh , mặt đường Đặng Thị Rành nước đã rút hết , các cửa hàng bắt đầu mở cửa đón khách .",
        [([6, 7, 8, 9], [10, 11, 12, 13], 'POS')]
    ),
    # 1424
    (
        "Bà con lưu thông qua Phạm Văn Đồng an tâm nhé , khu vực này thông xe rồi .",
        [([5, 6, 7], [15, 16], 'POS')]
    ),
    # 1425
    (
        "Sau cơn mưa chiều , đường Phạm Văn Đồng nước đã rút , giao thông qua khu vực ổn định bình thường .",
        [([5, 6, 7, 8], [9, 10, 11], 'POS')]
    ),
    # 1426
    (
        "Tuyến đường Calmette hôm nay thông suốt , các phương tiện di chuyển nhanh chóng .",
        [([1, 2], [5, 6], 'POS')]
    ),
    # 1427
    (
        "Nhờ thoát nước nhanh , mặt đường Quốc lộ 13 nước đã rút sạch , các cửa hàng bắt đầu mở cửa đón khách .",
        [([6, 7, 8, 9], [10, 11, 12, 13], 'POS')]
    ),
    # 1428
    (
        "Ghi nhận tại Bình Quới đến thời điểm này thông xe , người dân đi lại dễ dàng không còn cảnh bì bõm .",
        [([3, 4], [9, 10], 'POS'), ([3, 4], [14, 15, 16, 17], 'POS')]
    ),
    # 1429
    (
        "Bà con lưu thông qua Trần Xuân Soạn an tâm nhé , khu vực này hết ngập hẳn rồi .",
        [([5, 6, 7], [15, 16, 17], 'POS')]
    ),
    # 1430
    (
        "Đến thời điểm này Lương Định Của đã khô ráo , xe cộ di chuyển rất thuận lợi .",
        [([4, 5, 6], [8, 9], 'POS')]
    ),
    # 1431
    (
        "Tuyến đường Bạch Đằng hôm nay lưu thông thuận lợi , các phương tiện di chuyển nhanh chóng .",
        [([1, 2, 3], [6, 7, 8, 9], 'POS')]
    ),
    # 1432
    (
        "Đường Nguyễn Văn Hưởng chiều tối nay khô ráo , người dân phấn khởi tan làm về nhà thuận tiện .",
        [([0, 1, 2, 3], [7, 8], 'POS')]
    ),
    # 1433
    (
        "Bà con qua Nguyễn Xí chú ý nhé , hiện tại hết ngập rồi .",
        [([3, 4], [9, 10], 'POS')]
    ),
    # 1434
    (
        "Sau cơn mưa chiều , đường Huỳnh Tấn Phát lưu thông bình thường , giao thông qua khu vực ổn định bình thường .",
        [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]
    ),
    # 1435
    (
        "Tuyến đường Dương Văn Cam hôm nay thông suốt , các phương tiện di chuyển nhanh chóng .",
        [([1, 2, 3, 4], [7, 8], 'POS')]
    ),
    # 1436
    (
        "Sau khi mở van xả triều , khu vực Nguyễn Văn Hưởng hết ngập hẳn , người dân không còn phải bì bõm lội nước .",
        [([9, 10, 11], [12, 13, 14], 'POS')]
    ),
    # 1437
    (
        "Cập nhật giao thông Tô Ngọc Vân hiện nước đã rút , không còn tình trạng xe chết máy .",
        [([4, 5, 6], [8, 9, 10], 'POS')]
    ),
    # 1438
    (
        "Nhờ thoát nước nhanh , mặt đường Nguyễn Văn Hưởng ráo hoảnh , các cửa hàng bắt đầu mở cửa đón khách .",
        [([6, 7, 8, 9], [10, 11], 'POS')]
    ),
    # 1439
    (
        "Bà con qua Đặng Thị Rành chú ý nhé , hiện tại hết ngập rồi .",
        [([3, 4, 5], [10, 11], 'POS')]
    ),
    # 1440
    (
        "Đường An Dương Vương chiều tối nay thông thoáng trở lại , người dân phấn khởi tan làm về nhà thuận tiện .",
        [([0, 1, 2, 3], [7, 8, 9, 10], 'POS')]
    ),
    # 1441
    (
        "Cập nhật giao thông Mễ Cốc hiện hết ngập , không còn tình trạng xe chết máy .",
        [([4, 5], [7, 8], 'POS')]
    ),
    # 1442
    (
        "Hiện tại tuyến Thảo Điền nước đã rút sạch , các phương tiện đã có thể di chuyển thuận tiện .",
        [([3, 4], [5, 6, 7, 8], 'POS')]
    ),
    # 1443
    (
        "Đường Trần Hưng Đạo chiều tối nay nước đã rút hoàn toàn , người dân phấn khởi tan làm về nhà thuận tiện .",
        [([0, 1, 2, 3], [7, 8, 9, 10, 11], 'POS')]
    ),
    # 1444
    (
        "Cập nhật giao thông Đặng Thị Rành hiện hết ngập , không còn tình trạng xe chết máy .",
        [([4, 5, 6], [8, 9], 'POS')]
    ),
    # 1445
    (
        "Cập nhật giao thông Bến Phú Định hiện đi lại bình thường , không còn tình trạng xe chết máy .",
        [([4, 5, 6], [8, 9, 10, 11], 'POS')]
    ),
    # 1446
    (
        "Sau cơn mưa chiều , đường Phạm Văn Đồng lưu thông bình thường , giao thông qua khu vực ổn định bình thường .",
        [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]
    ),
    # 1447
    (
        "Bà con lưu thông qua Phạm Văn Đồng an tâm nhé , khu vực này nước đã rút rồi .",
        [([5, 6, 7], [15, 16, 17], 'POS')]
    ),
    # 1448
    (
        "Sau cơn mưa chiều , đường Bến Phú Định nước rút nhanh chóng , giao thông qua khu vực ổn định bình thường .",
        [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]
    ),
    # 1449
    (
        "Hiện tại tuyến Phạm Văn Đồng nước đã rút sạch , các phương tiện đã có thể di chuyển thuận tiện .",
        [([3, 4, 5], [6, 7, 8, 9], 'POS')]
    ),
    # 1450
    (
        "Đoạn đường Dương Văn Cam sau khi triều cường hạ nước đã rút sạch sẽ , cuộc sống sinh hoạt của bà con đã ổn định trở lại .",
        [([1, 2, 3, 4], [10, 11, 12, 13, 14], 'POS')]
    ),
    # 1451
    (
        "Sau cơn mưa chiều , đường Mễ Cốc nước rút nhanh chóng , giao thông qua khu vực ổn định bình thường .",
        [([5, 6, 7], [8, 9, 10, 11], 'POS')]
    ),
    # 1452
    (
        "Tuyến đường Kha Vạn Cân hôm nay khô ráo , các phương tiện di chuyển nhanh chóng .",
        [([1, 2, 3, 4], [7, 8], 'POS')]
    ),
    # 1453
    (
        "Đoạn đường Đỗ Xuân Hợp sau khi triều cường hạ nước rút hết , cuộc sống sinh hoạt của bà con đã ổn định trở lại .",
        [([1, 2, 3, 4], [10, 11, 12], 'POS')]
    ),
    # 1454
    (
        "Tuyến đường Tô Ngọc Vân hôm nay lưu thông thuận lợi , các phương tiện di chuyển nhanh chóng .",
        [([1, 2, 3, 4], [7, 8, 9, 10], 'POS')]
    ),
    # 1455
    (
        "Bà con lưu thông qua Nguyễn Duy an tâm nhé , khu vực này nước đã rút rồi .",
        [([5, 6], [14, 15, 16], 'POS')]
    ),
    # 1456
    (
        "Tuyến đường Quốc Hương hôm nay không còn ngập nữa , các phương tiện di chuyển nhanh chóng .",
        [([1, 2, 3], [6, 7, 8, 9], 'POS')]
    ),
    # 1457
    (
        "Sau khi mở van xả triều , khu vực Phạm Thế Hiển khô queo , người dân không còn phải bì bõm lội nước .",
        [([9, 10, 11], [12, 13], 'POS')]
    ),
    # 1458
    (
        "Mặt đường khu vực Quốc Hương nước đã rút sạch , người dân phấn khởi đi lại .",
        [([4, 5], [6, 7, 8, 9], 'POS')]
    ),
    # 1459
    (
        "Sau cơn mưa chiều , đường Trần Xuân Soạn khô ráo hoàn toàn , giao thông qua khu vực ổn định bình thường .",
        [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]
    ),
    # 1460
    (
        "Đến thời điểm này Nguyễn Văn Hưởng đã hết ngập , xe cộ di chuyển rất thuận lợi .",
        [([4, 5, 6], [8, 9], 'POS')]
    ),
    # 1461
    (
        "Sau khi mở van xả triều , khu vực Quốc Hương nước đã rút , người dân không còn phải bì bõm lội nước .",
        [([9, 10], [11, 12, 13], 'POS')]
    ),
    # 1462
    (
        "Mặt đường khu vực Quốc Hương thông suốt , người dân phấn khởi đi lại .",
        [([4, 5], [6, 7], 'POS')]
    ),
    # 1463
    (
        "Hiện tại tuyến Kinh Dương Vương nước đã rút sạch , các phương tiện đã có thể di chuyển thuận tiện .",
        [([3, 4, 5], [6, 7, 8, 9], 'POS')]
    ),
    # 1464
    (
        "Hiện tại tuyến Lê Đức Thọ hết ngập hẳn , các phương tiện đã có thể di chuyển thuận tiện .",
        [([3, 4, 5], [6, 7, 8], 'POS')]
    ),
    # 1465
    (
        "Nhờ thoát nước nhanh , mặt đường Trần Hưng Đạo ráo hoảnh , các cửa hàng bắt đầu mở cửa đón khách .",
        [([6, 7, 8, 9], [10, 11], 'POS')]
    ),
    # 1466
    (
        "Mặt đường khu vực Bạch Đằng thông suốt , người dân phấn khởi đi lại .",
        [([4, 5], [6, 7], 'POS')]
    ),
    # 1467
    (
        "Bà con qua Đinh Bộ Lĩnh chú ý nhé , hiện tại nước rút sạch rồi .",
        [([3, 4, 5], [10, 11, 12], 'POS')]
    ),
    # 1468
    (
        "Hiện tại tuyến Quốc lộ 13 thông thoáng trở lại , các phương tiện đã có thể di chuyển thuận tiện .",
        [([3, 4, 5], [6, 7, 8, 9], 'POS')]
    ),
    # 1469
    (
        "Bà con qua Đặng Thị Rành chú ý nhé , hiện tại khô ráo rồi .",
        [([3, 4, 5], [10, 11], 'POS')]
    ),
    # 1470
    (
        "Tuyến đường Nguyễn Văn Khối chiều nay sau khi mưa ngớt đã thông thoáng , xe cộ đi lại dễ dàng .",
        [([1, 2, 3, 4], [11, 12], 'POS'), ([1, 2, 3, 4], [17, 18, 19, 20], 'POS')]
    ),
    # 1471
    (
        "Bà con lưu thông qua Hoàng Diệu an tâm nhé , khu vực này đã khô ráo rồi .",
        [([5, 6], [14, 15, 16], 'POS')]
    ),
    # 1472
    (
        "Sau cơn mưa chiều , đường Nguyễn Biểu nước rút nhanh chóng , giao thông qua khu vực ổn định bình thường .",
        [([5, 6, 7], [8, 9, 10, 11], 'POS')]
    ),
    # 1473
    (
        "Sau cơn mưa chiều , đường Đào Trí nước rút nhanh chóng , giao thông qua khu vực ổn định bình thường .",
        [([5, 6, 7], [8, 9, 10, 11], 'POS')]
    ),
    # 1474
    (
        "Tuyến đường Huỳnh Tấn Phát hôm nay khô ráo , các phương tiện di chuyển nhanh chóng .",
        [([1, 2, 3, 4], [7, 8], 'POS')]
    ),
    # 1475
    (
        "Sau khi mở van xả triều , khu vực Nguyễn Duy hết ngập hẳn , người dân không còn phải bì bõm lội nước .",
        [([9, 10], [11, 12, 13], 'POS')]
    ),
    # 1476
    (
        "Sau cơn mưa chiều , đường Ung Văn Khiêm không còn ngập nước , giao thông qua khu vực ổn định bình thường .",
        [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]
    ),
    # 1477
    (
        "Sau cơn mưa chiều , đường Trần Hưng Đạo nước đã rút , giao thông qua khu vực ổn định bình thường .",
        [([5, 6, 7, 8], [9, 10, 11], 'POS')]
    ),
    # 1478
    (
        "Tuyến đường Quốc lộ 13 hôm nay lưu thông thuận lợi , các phương tiện di chuyển nhanh chóng .",
        [([1, 2, 3, 4], [7, 8, 9, 10], 'POS')]
    ),
    # 1479
    (
        "Mặt đường khu vực Dương Văn Cam khô ráo , người dân phấn khởi đi lại .",
        [([4, 5, 6], [7, 8], 'POS')]
    ),
    # 1480
    (
        "Nhờ thoát nước nhanh , mặt đường Lê Văn Lương đã khô ráo , các cửa hàng bắt đầu mở cửa đón khách .",
        [([6, 7, 8, 9], [10, 11, 12], 'POS')]
    ),
    # 1481
    (
        "Đoạn đường Nguyễn Văn Hưởng sau khi triều cường hạ mặt đường thông thoáng , cuộc sống sinh hoạt của bà con đã ổn định trở lại .",
        [([1, 2, 3, 4], [12, 13], 'POS')]
    ),
    # 1482
    (
        "Đoạn đường Lê Văn Việt sau khi triều cường hạ thông suốt , cuộc sống sinh hoạt của bà con đã ổn định trở lại .",
        [([1, 2, 3, 4], [10, 11], 'POS')]
    ),
    # 1483
    (
        "Sau khi mở van xả triều , khu vực Nguyễn Hữu Cảnh khô queo , người dân không còn phải bì bõm lội nước .",
        [([9, 10, 11], [12, 13], 'POS')]
    ),
    # 1484
    (
        "Sau cơn mưa chiều , đường Đặng Thị Rành lưu thông bình thường , giao thông qua khu vực ổn định bình thường .",
        [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]
    ),
    # 1485
    (
        "Tuyến đường Dương Văn Cam hôm nay lưu thông thuận lợi , các phương tiện di chuyển nhanh chóng .",
        [([1, 2, 3, 4], [7, 8, 9, 10], 'POS')]
    ),
    # 1486
    (
        "Ghi nhận tại Đào Trí đến thời điểm này thông xe , người dân đi lại dễ dàng không còn cảnh bì bõm .",
        [([3, 4], [9, 10], 'POS'), ([3, 4], [14, 15, 16, 17], 'POS')]
    ),
    # 1487
    (
        "Đoạn đường Hồ Học Lãm sau khi triều cường hạ khô ráo sạch sẽ , cuộc sống sinh hoạt của bà con đã ổn định trở lại .",
        [([1, 2, 3, 4], [10, 11, 12, 13], 'POS')]
    ),
    # 1488
    (
        "Nhờ thoát nước nhanh , mặt đường Quốc lộ 13 đã khô ráo , các cửa hàng bắt đầu mở cửa đón khách .",
        [([6, 7, 8, 9], [10, 11, 12], 'POS')]
    ),
    # 1489
    (
        "Cập nhật giao thông Lương Định Của hiện khô ráo , không còn tình trạng xe chết máy .",
        [([4, 5, 6], [8, 9], 'POS')]
    ),
    # 1490
    (
        "Cập nhật giao thông Phạm Văn Đồng hiện khô ráo , không còn tình trạng xe chết máy .",
        [([4, 5, 6], [8, 9], 'POS')]
    ),
    # 1491
    (
        "Nhờ thoát nước nhanh , mặt đường Quốc Hương khô ráo sạch sẽ , các cửa hàng bắt đầu mở cửa đón khách .",
        [([6, 7, 8], [9, 10, 11, 12], 'POS')]
    ),
    # 1492
    (
        "Đường Nguyễn Duy chiều tối nay lưu thông bình thường , người dân phấn khởi tan làm về nhà thuận tiện .",
        [([0, 1, 2], [6, 7, 8, 9], 'POS')]
    ),
    # 1493
    (
        "Ghi nhận tại An Dương Vương đến thời điểm này thông xe , người dân đi lại dễ dàng không còn cảnh bì bõm .",
        [([3, 4, 5], [10, 11], 'POS'), ([3, 4, 5], [15, 16, 17, 18], 'POS')]
    ),
    # 1494
    (
        "Sau khi mở van xả triều , khu vực Mễ Cốc hết ngập hẳn , người dân không còn phải bì bõm lội nước .",
        [([9, 10], [11, 12, 13], 'POS')]
    ),
    # 1495
    (
        "Sau cơn mưa chiều , đường Trần Xuân Soạn lưu thông bình thường , giao thông qua khu vực ổn định bình thường .",
        [([5, 6, 7, 8], [9, 10, 11, 12], 'POS')]
    ),
    # 1496
    (
        "Bà con lưu thông qua Hoàng Diệu an tâm nhé , khu vực này khô rang rồi .",
        [([5, 6], [14, 15], 'POS')]
    ),
    # 1497
    (
        "Nhờ thoát nước nhanh , mặt đường Ung Văn Khiêm đã khô ráo , các cửa hàng bắt đầu mở cửa đón khách .",
        [([6, 7, 8, 9], [10, 11, 12], 'POS')]
    ),
    # 1498
    (
        "Giao thông trục Lê Đức Thọ cơ bản khô ráo , không còn điểm nghẽn do nước tù đọng .",
        [([3, 4, 5], [8, 9], 'POS')]
    ),
    # 1499
    (
        "Tuyến đường Dương Văn Cam hôm nay nước rút sạch , các phương tiện di chuyển nhanh chóng .",
        [([1, 2, 3, 4], [7, 8, 9], 'POS')]
    ),
    # 1500
    (
        "Thông tin khẩn : Điểm ngập Quốc lộ 13 thông suốt , các loại xe máy và ô tô lưu thông bình an .",
        [([6, 7, 8], [9, 10], 'POS')]
    ),
]

def format_line(text, triplets):
    formatted_triplets = []
    for asp, opn, pol in triplets:
        formatted_triplets.append(f"({asp}, {opn}, '{pol}')")
    triplets_str = "[" + ", ".join(formatted_triplets) + "]"
    return f"{text}####{triplets_str}\n"

if __name__ == '__main__':
    assert len(batch15_data) == 100, f"Expected 100 records, got {len(batch15_data)}"
    
    # Đọc 1400 dòng đã có trong phase3.txt
    phase3_path = "data/validate_label/thuan/phase3.txt"
    with open(phase3_path, "r", encoding="utf-8") as f:
        existing_lines = [l for l in f.readlines() if l.strip()]
    
    print(f"Existing lines in phase3.txt: {len(existing_lines)}")
    assert len(existing_lines) == 1400, f"Expected 1400 existing lines, found {len(existing_lines)}"
    
    # Format 100 dòng mới
    new_lines = [format_line(t, tr) for t, tr in batch15_data]
    
    # Ghi toàn bộ 1500 dòng vào phase3.txt
    all_lines = existing_lines + new_lines
    with open(phase3_path, "w", encoding="utf-8") as f:
        f.writelines(all_lines)
        
    print(f"Successfully wrote {len(all_lines)} lines to {phase3_path}!")
