# Rà soát nhãn ASTE Phase 3 của Thuận

File xử lý là `data/validate_label/thuan/phase3.txt`, gồm 3.875 dòng. Dùng [cẩm nang Phase 3](BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md), SHA-256 `E139E6598CE0446137FB909CA890B5C7D4C018933EA78344C8B48BBC84A05506`. Giữ cùng phiên bản quy tắc khi nối lô. Khi ví dụ trong hai tài liệu nền khác quy tắc Phase 3, áp dụng cẩm nang Phase 3, đặc biệt với aspect đa cấp, triều trơ và emoji ở rìa.

Đọc toàn bộ từng dòng, kể cả hashtag và phần bị cắt. Gán theo từng block 50, báo mỗi 100. Gán cụm nguyên văn và lần xuất hiện sau khi xác định ngữ cảnh. Dùng `span_helper.py` tính index, chạy `verify_batch_50.py --expected` từng block. Giữ thứ tự dòng. Ghi lại các quyết định ranh giới để tái kiểm tra. Sau khi hoàn tất toàn file, chạy cả hai công cụ audit cuối theo cẩm nang.

## Lô 001 · Dòng 1–100

- Đã đọc và gán cả 100 dòng. Đã ghi cập nhật 72 dòng, giữ nguyên văn bản và thứ tự dòng. Giải mã 122 triplet, có 7 quyết định `[]`.
- Hai block 50 đều đạt 0 `ERROR` cả kiểm tra kỹ thuật và `--expected`. 32 `REVIEW` là các dấu hiệu đã xuất ra để đối chiếu, gồm quyết định `[]`, vị ngữ dùng chung, tiền tố hạ tầng và tín hiệu polarity.
- Các quyết định theo từng dòng và cụm đã duyệt nằm trong `scripts/scratch/phase3_001_100.review.txt` và `scripts/scratch/phase3_001_100.expected.json`.
- Dòng 1 là quảng cáo quán, 68 chỉ có hashtag ngập và 75, 78 dùng ngập làm nền cho nội dung âm nhạc. Dòng 94 bàn về ngập thời Pháp thuộc.
- Những ca nên đối soát thêm theo ngữ cảnh nguồn gồm 56 (tiêu đề ngắn), 58 (mốc thời gian quá khứ lẫn tương lai nên gán NEU theo ngữ cảnh thời tiết), 63 (ví von Bãi Sau, chưa có mô tả rõ hiện trường), 73 (ứng phó bơm chìm tại nhà, cần phân biệt với quảng cáo), 88 (tiêu đề giới thiệu danh sách, đoạn trích chưa nêu sự kiện hoặc địa điểm cụ thể). Dòng 57 gán NEG cho đánh giá hiệu quả hạn chế của khoản đầu tư.
- SHA-256 sau khi ghi là `BF636F2308247684C293F8F97DF71B6EC65CA1C71F1925839769A8107A616BD0`.

## Lô 002 · Dòng 101–200

- Đã đọc và gán cả 100 dòng. Đã ghi cập nhật 78 dòng, giữ nguyên văn bản và thứ tự dòng. Giải mã 154 triplet, có 6 quyết định `[]`.
- Hai block 50 đều đạt 0 `ERROR` khi chạy `verify_batch_50.py --expected`. Có 54 lượt `REVIEW`.
- Quyết định từng dòng và vị trí đã duyệt nằm trong `scripts/scratch/phase3_101_200.review.txt` và `scripts/scratch/phase3_101_200.expected.json`.
- Dòng 124 hỏi bao giờ hết ngập nên gán NEU. Dòng 128 là tin rao phòng. Dòng 129 giữ cả TP.HCM và Bình Dương vì bài nêu hai địa bàn riêng cùng bị ngập. Dòng 195 chọn lần xuất hiện thứ hai của `Sài Gòn`, nơi phát ngôn đặt câu hỏi về mưa ngập.
- Các ca cần đối soát thêm nếu có văn bản gốc gồm 133 (địa chỉ cuối bài có thể là thông tin kênh), 136 (đuôi cụt, giữ `vẫn chìm` theo tiêu đề và mệnh đề trước), 137 (khuyến cáo chung, không có địa điểm xảy ra trong nội dung), 149 (bài giới thiệu dự án, địa danh công trình chưa xuất hiện trong đoạn), 165 (lắp đặt sản phẩm kèm lời kể ngập), 173 (nhà dân gần cầu, cầu dùng để định vị), 194 (tiêu đề đề xuất giải pháp và thân bài bị cắt sau đoạn trích dẫn).
- SHA-256 sau khi ghi là `C776F4AC987D6DC245F29D63B0969C3BA183D2F2560F4A87C2E02890BAA502FD`.

## Lô 003 · Dòng 201–300

- Đã đọc và gán cả 100 dòng. Ghi cập nhật 74 dòng. Hai block 50 đạt 0 `ERROR` khi đối chiếu với `--expected`. Sau gán có 135 triplet, 10 quyết định `[]` và 27 lượt `REVIEW`.
- Dòng 204 nói về một ngã tư mang tên hai đường. Dòng 211 nêu hai cây cầu để định vị đoạn ngập trên đường Điện Biên Phủ. Dòng 230 là lời mời khách ghé quán và chưa xác nhận nước đã rút. Dòng 234 xác nhận nước rút sau trận ngập nên gán POS. Dòng 262 mô tả một sự kiện có ngày cụ thể năm 2022 và đủ tên đường nên giữ. Các dòng 276–278 thiếu phát ngôn về hiện trường hoặc cảnh báo ngập trong nội dung chính. Dòng 279 có hành vi lội nước nên giữ.
- Quyết định và vị trí đã duyệt ở `scripts/scratch/phase3_201_300.review.txt` và `scripts/scratch/phase3_201_300.expected.json`.
- SHA-256 sau khi ghi là `3D44C967AAAFC65BBD7985AAED314FA03859CE63C006DD1F4CC076E05918BA99`.

## Lô 004 · Dòng 301–400

- Đã đọc và gán cả 100 dòng. Có 84 dòng thay đổi so với bản ban đầu, 140 triplet, 3 quyết định `[]` và 27 lượt `REVIEW`. Cả hai block đạt 0 `ERROR` khi đối chiếu với `--expected`.
- Dòng 305 tách dự án sắp hoạt động (POS) khỏi câu hỏi khu vực nào hết ngập (NEU). Dòng 335 dùng ngập để giới thiệu chỗ nghỉ nên loại. Dòng 338 ví đường thành sông để tả hiện trường nên giữ. Dòng 384 là khuyến cáo theo điều kiện, gán NEU cho từng địa bàn được nêu. Dòng 387 gán riêng số đo cho từng trạm và cảnh báo ngập cho TP.HCM.
- Quyết định và vị trí đã duyệt ở `scripts/scratch/phase3_301_400.review.txt` và `scripts/scratch/phase3_301_400.expected.json`.

## Đối soát các ca giáp ranh ở lô trước

- Đã đọc lại các ca nêu ở lô 001 và 002 dựa trên toàn văn sẵn có và chốt nhãn theo cẩm nang. Dòng 56 giữ NEG theo mô tả lội/trôi trong nước ngập. Dòng 58 giữ NEU theo khung dự báo chưa tách được hiện trường riêng. Dòng 63, 88, 137 và 165 giữ `[]` vì đoạn văn lần lượt thiếu trạng thái ngập rõ, không cung cấp hiện trường trong danh sách, chỉ là hướng dẫn chung, hoặc có ngữ cảnh lắp đặt sản phẩm. Dòng 73 giữ POS vì mô tả bơm chìm để ứng phó tại nhà cụ thể. Dòng 133 dùng TP.HCM vì địa chỉ cuối bài chưa được gắn với hiện trường. Dòng 136 giữ hai đường theo mệnh đề trọn ý trước từ bị cắt. Dòng 149 và 194 giữ POS vì tiêu đề nêu dự án hoặc giải pháp cụ thể về mục đích chống ngập.
- Sửa dòng 173 sang `phường Tân Khánh`. Chủ thể bị ngập là nhà dân trong phường. Cầu Khánh Vân là mốc gần đó. Lô 002 có 79 dòng thay đổi so với bản ban đầu sau lần sửa này.
- Sau khi ghi, chạy lại đối chiếu bốn lô trên file thật. Tất cả đạt 0 `ERROR`. Đối chiếu Git giữ đủ 3.875 dòng, phần văn bản trước `####` giống bản ban đầu và các dòng sau 400 giữ nguyên.
- SHA-256 hiện tại là `1496E1325AC3BD4E9F49C93EEF8AE41458FDC3E0BB2207661F9552F26FE727BA`.

## Lô 005 · Dòng 401–500

- Đã đọc và gán 100 dòng. Cập nhật 71 dòng. Có 125 triplet và 8 quyết định `[]`. Hai block 50 đều đạt 0 `ERROR` với `--expected`.
- Dòng 403 chỉ gán Cityland Park Hills vì hai tuyến đường dùng để định vị khu dân cư. Dòng 423 tách câu hỏi hiện tại (NEU) và việc đã ngập ngày hôm qua (NEG). Dòng 452 không lấy địa danh từ tên báo. Dòng 486 theo địa điểm nêu trong thân bài thay vì tiền tố do crawler thêm, nên loại. Dòng 485 và 493 giữ hiện trường Bình Dương và tách hành động cứu hộ.
- Cụm từ và vị trí đã duyệt ở `scripts/scratch/phase3_401_500.review.txt` và `scripts/scratch/phase3_401_500.expected.json`.

## Lô 006 · Dòng 501–600

- Đã đọc và gán 100 dòng. Cập nhật 80 dòng. Có 155 triplet và 2 quyết định `[]`. Hai block 50 đều đạt 0 `ERROR` với `--expected`.
- Dòng 508 gán năm địa điểm được liệt kê cho ngập thực tế và giữ thêm trạng thái đo đạc của sông Sài Gòn. Dòng 530 là câu hỏi về hệ quả của nâng đường nên gán NEU. Dòng 552 nhắc Hà Nội để so sánh và mô tả hiện trường tại TP.HCM. Dòng 571 là cảnh báo ngập theo điều kiện mực triều. Dòng 584 tách năng lực thoát nước còn hạn chế (NEG) và cải thiện so với trước (POS).
- Cụm từ và vị trí đã duyệt ở `scripts/scratch/phase3_501_600.review.txt` và `scripts/scratch/phase3_501_600.expected.json`.
- SHA-256 sau lô 006 là `EF0EFB ECD95BD024C9381ED216BE9BE5E53FAD945682A1728558F115424797D2` (bỏ khoảng trắng).

## Lô 007 · Dòng 601–700

- Đã đọc và gán 100 dòng. Cập nhật 80 dòng. Có 134 triplet và 9 quyết định `[]`. Hai block 50 đều đạt 0 `ERROR` với `--expected`.
- Dòng 605 là câu hỏi về thời điểm hết ngập. Dòng 639 có hai trạng thái riêng: hệ thống thoát nước đang quá tải (NEG) và dự báo ngập nếu có mưa lớn (NEU). Dòng 663 mô tả người dân chờ rút nước, chưa xác nhận phục hồi. Dòng 676 dùng ngập với nghĩa hàng hóa đầy kho. Dòng 692 được loại vì đoạn trích chưa định vị sự kiện trong phạm vi. Dòng 693 ghi rõ tuyến tại khu vực cầu Nhật Tân.
- Cụm từ và vị trí đã duyệt ở `scripts/scratch/phase3_601_700.review.txt` và `scripts/scratch/phase3_601_700.expected.json`.
- SHA-256 hiện tại là `0F93512D79AAC1DAA0506DC17895D034EFFB58785D06AC1360D088A9E32AE8AD`.

Mốc của đợt trên là dòng 700. Bảng cuối tài liệu ghi kết quả của toàn bộ 39 lô.

- Đối soát lại dòng 227. Tách hai hậu quả giao thông thành `Xe buýt ch * t máy` (10–15) và `xe máy dắt bộ` (17–20). Đã cập nhật manifest và chạy lại lô 201–300 với 0 `ERROR`. SHA-256 tại mốc sửa dòng 227 là `E84D3425A1E2A8311D1F655CE527A2285E50AD1F94F0F1003E07B0B04E854C01`.

## Kết quả toàn bộ Phase 3 trước đợt đối soát chất lượng

Đã rà 3.875/3.875 dòng. Số dòng đổi nhãn tính theo bản trong Git trước khi rà. Phần văn bản trước `####` và thứ tự dòng khớp với bản đó.

| Lô | Dòng | Dòng đổi nhãn | Triplet | Dòng `[]` |
| --- | --- | ---: | ---: | ---: |
| 1 | 1–100 | 72 | 122 | 7 |
| 2 | 101–200 | 79 | 154 | 6 |
| 3 | 201–300 | 74 | 136 | 10 |
| 4 | 301–400 | 84 | 140 | 3 |
| 5 | 401–500 | 71 | 125 | 8 |
| 6 | 501–600 | 80 | 155 | 2 |
| 7 | 601–700 | 80 | 134 | 9 |
| 8 | 701–800 | 86 | 115 | 16 |
| 9 | 801–900 | 90 | 123 | 7 |
| 10 | 901–1000 | 87 | 121 | 5 |
| 11 | 1001–1100 | 94 | 99 | 6 |
| 12 | 1101–1200 | 97 | 102 | 5 |
| 13 | 1201–1300 | 100 | 100 | 0 |
| 14 | 1301–1400 | 100 | 100 | 0 |
| 15 | 1401–1500 | 100 | 100 | 0 |
| 16 | 1501–1600 | 100 | 100 | 0 |
| 17 | 1601–1700 | 100 | 100 | 0 |
| 18 | 1701–1800 | 100 | 100 | 0 |
| 19 | 1801–1900 | 100 | 100 | 0 |
| 20 | 1901–2000 | 100 | 100 | 0 |
| 21 | 2001–2100 | 85 | 95 | 11 |
| 22 | 2101–2200 | 88 | 116 | 8 |
| 23 | 2201–2300 | 78 | 98 | 11 |
| 24 | 2301–2400 | 81 | 81 | 23 |
| 25 | 2401–2500 | 93 | 105 | 12 |
| 26 | 2501–2600 | 95 | 110 | 6 |
| 27 | 2601–2700 | 93 | 108 | 5 |
| 28 | 2701–2800 | 91 | 112 | 8 |
| 29 | 2801–2900 | 93 | 114 | 8 |
| 30 | 2901–3000 | 91 | 124 | 3 |
| 31 | 3001–3100 | 91 | 115 | 11 |
| 32 | 3101–3200 | 91 | 104 | 11 |
| 33 | 3201–3300 | 94 | 118 | 4 |
| 34 | 3301–3400 | 89 | 135 | 4 |
| 35 | 3401–3500 | 89 | 105 | 6 |
| 36 | 3501–3600 | 94 | 106 | 9 |
| 37 | 3601–3700 | 94 | 112 | 6 |
| 38 | 3701–3800 | 98 | 84 | 18 |
| 39 | 3801–3875 | 61 | 62 | 18 |
| **Tổng** | **1–3875** | **3483** | **4330** | **266** |

Triplet gồm 2.445 NEG, 1.151 POS và 734 NEU. Đợt cuối từ dòng 3001 đến 3875 có 801 dòng đổi nhãn, 941 triplet và 87 dòng `[]`.

SHA-256 bản cuối là `c6f5dc2b548b6a0ac05706ce491c88420e1b02c82748c642fc927f2655d15e5a`.

### Đối chiếu cuối

- `deep_10_pass_audit.py` trả mã 0. `audit_index_integrity.py --expected scripts/scratch/phase3_all.expected.json` trả mã 0 và đối chiếu toàn bộ 4.330 triplet theo cụm từ, vị trí bắt đầu và polarity trong manifest. Cả hai báo 0 lỗi kỹ thuật.
- Công cụ đánh dấu 752 lượt `REVIEW` trên 695 dòng, gồm 266 quyết định `[]`, 219 vị ngữ dùng chung, 162 tín hiệu polarity, 70 tiền tố hạ tầng, 15 tín hiệu địa lý, 9 văn bản trùng, 5 cảnh báo ngữ cảnh bên trái, 4 cảnh báo fallback và 2 cảnh báo ranh giới ngữ nghĩa. Đây là các cờ gợi ý đối soát. Kết quả kỹ thuật chưa xác lập độ chính xác ngữ nghĩa hoặc độ đồng thuận giữa hai người gán.
- Dòng 3250 tách đủ bảy tuyến trong danh sách cảnh báo, mỗi tuyến có một triplet NEU. Dòng 3393 lấy hầm chui ở đầu TP.HCM làm aspect vì Biên Hòa chỉ là hướng đi. Các dòng 3852–3857 thuộc chuỗi kể lại ngập trước 1975, nên giữ văn bản và để `[]` theo tiêu chí lịch sử.
- Với bản ghi thiếu ngữ cảnh, dùng địa danh hoặc tiền tố có sẵn khi văn bản đủ căn cứ. Giữ nguyên văn bản cho phép đối chiếu 1:1 với bản gốc và tránh bổ sung địa danh do suy đoán.
- Dấu vết từng lô nằm tại `scripts/scratch/phase3_<dòng đầu>_<dòng cuối>.review.txt` và `*.expected.json`. Báo cáo toàn file và thống kê nằm tại `scripts/scratch/deep_10_pass_audit.phase3.json`, `scripts/scratch/audit_index_integrity.phase3.json` và `scripts/scratch/phase3_final_stats.json`.

## Đối soát chất lượng và fallback

Kiểm tra lại bằng công cụ trên cả 3.875 dòng. Đọc lại 266 dòng từng để `[]`, đối chiếu chín cặp văn bản trùng và ưu tiên đọc lại toàn văn các ca có nghi vấn về phạm vi, polarity, thiếu địa danh, tiền tố hạ tầng hoặc ranh giới opinion. Lượt này kiểm tra kỹ thuật toàn file và tái thẩm định ngữ nghĩa có trọng điểm. Kết quả chưa phải một lượt gán độc lập từ đầu trên cả 3.875 dòng.

Đã sửa 41 dòng. Có 24 dòng được phục hồi từ `[]`. Trong số 23 dòng đổi văn bản, 21 dòng được thêm tiền tố `Tại TPHCM , ` và hai dòng (1027, 3497) được bổ sung `ở TPHCM` ngay sau aspect triều cường theo mục III.2.6. Cả 3.875 dòng giữ nguyên thứ tự. Span được dựng lại theo văn bản cuối bằng `span_helper.py`.

- Dòng 3041 và 3068 nối tiếp bản tin về 23 tuyến đường ở TP.HCM. Thêm fallback `TPHCM` ở index `[1]` và chọn `sẽ bị ngập` với nhãn NEU.
- Chỉ thêm fallback khi có căn cứ về địa bàn nghiên cứu và dòng thiếu địa danh cụ thể của sự kiện. Các token gốc dịch sang phải ba vị trí. Căn cứ có thể nằm trong đoạn nối tiếp rõ ràng, như câu bắt đầu bằng `Tức là` sau bản tin 23 tuyến đường. Tin ngoài phạm vi, quảng cáo, mẹo kỹ thuật chung và đoạn thiếu căn cứ tiếp tục dùng `[]`.
- Dòng 720 bỏ opinion bị cắt `nguyên bán` và giữ triplet đủ nghĩa. Dòng 2669 dừng opinion ở `Ngập Lụt Hôm Nay`, trước dấu hai chấm. Dòng 2960 lấy cả dấu hiệu trạng thái `đã` trong `đã huy động`. Dòng 3108 ghi riêng ngập quanh chợ Thủ Đức và khó khăn lưu thông trên đường Phạm Văn Đồng.
- Chín cặp văn bản trùng khớp nhãn và được giữ tại vị trí gốc. Các danh sách tuyến độc lập được tách thành nhiều triplet, như bảy tuyến của dòng 3250.

Bản tại mốc đối soát này có 4.356 triplet và 242 dòng `[]`. Hai bộ kiểm định báo 0 lỗi kỹ thuật. Công cụ phát 717 lượt `REVIEW` trên 664 dòng, gồm 242 quyết định `[]`, 218 vị ngữ dùng chung, 160 tín hiệu polarity, 69 tiền tố hạ tầng, 15 tín hiệu địa lý, 9 văn bản trùng và 4 tín hiệu fallback. Số cờ phản ánh các điều kiện được bộ kiểm tra nhận diện. Độ chính xác ngữ nghĩa tuyệt đối vẫn chưa được xác lập.

SHA-256 tại mốc này là `a7ed7c079df0f27d1924bd8f85895893de8cb03de3aa114ec45c33d9e527f651`. Quyết định sửa từng dòng nằm trong `scripts/scratch/phase3_quality_decisions.json`. Manifest tại mốc này là `scripts/scratch/phase3_quality.expected.json`. Báo cáo mới nằm trong `scripts/scratch/deep_10_pass_audit.phase3_quality.json` và `scripts/scratch/audit_index_integrity.phase3_quality.json`. Bản trước đợt đối soát được lưu tại `scripts/scratch/phase3_before_quality.txt`.

## Rà soát toàn văn và đối chiếu nguồn bổ sung

Đã rà lại aspect, opinion và polarity của 3.875 dòng theo cẩm nang Phase 3. Các câu lặp cùng khuôn được đối chiếu theo khuôn và các trường hợp ngoại lệ. Đã chỉnh **277 dòng** so với bản trước lượt rà này, gồm 275 dòng trong lượt rà toàn văn và hai dòng sau khi đối chiếu nguồn. Thứ tự và số lượng dòng được giữ nguyên. Trong những dòng đổi văn bản, 10 dòng được thêm tiền tố `Tại TPHCM , `, 13 dòng được bổ sung `ở TPHCM` cho cụm thủy văn theo cẩm nang và dòng 2781 được hoàn chỉnh tên thành phố từ bản tin gốc.

- **717 lượt REVIEW của bản trước**. Giữ nhãn cho 661 lượt sau khi đối chiếu, 44 lượt thuộc các dòng đã sửa và 12 lượt còn thiếu dữ kiện để chốt.
- **Bản tại mốc đối chiếu nguồn** có 4.474 triplet và 243 dòng `[]`. Công cụ phát 727 lượt REVIEW trên 670 dòng. Đã đối chiếu 715 lượt theo quyết định giữ hoặc sửa và còn 12 lượt thiếu dữ kiện nguồn. Các cờ kỹ thuật có thể tiếp tục xuất hiện ở các nhãn đã được xem lại.
- **Kiểm định index**. Cả 78 block tối đa 50 dòng đạt 0 `ERROR` với manifest. Cả hai lượt kiểm định toàn file cũng đạt 0 `ERROR` và đối chiếu aspect, opinion, vị trí bắt đầu và polarity của cả 4.474 triplet. Con số này đo kết quả kiểm định theo các quy tắc đã triển khai. Chưa có lượt gán độc lập thứ hai để đo độ đồng thuận.
- Dòng 2781 khôi phục `Hồ Chí Minh` từ văn bản VTV10 gốc. Gán `TP. Hồ Chí Minh` [15, 16, 17, 18] và `CẢNH BÁO NGẬP NHIỀU KHU VỰC` [8, 9, 10, 11, 12, 13] với NEU.
- Dòng 3657 thêm fallback `TPHCM` [1] và gán `gặp nước ngập` [22, 23, 24] với NEG. Nguồn đặt hiện trường trên Quốc lộ 1K tại đoạn giáp Linh Xuân và Bình Dương, cả hai thuộc phạm vi theo cẩm nang. Bình Dương trong câu chỉ nơi làm việc. Chi tiết dắt bộ hơn 2 km trong trích đoạn thiếu xác nhận từ nguồn nên nằm ngoài opinion. [Bài Tuổi Trẻ gốc](https://tuoitre.vn/cho-thu-duc-day-song-sau-con-mua-lon-20240901185434356.htm)
- Giữ nhãn sau đối chiếu nguồn cho 701, 2622, 3246, 3752 và 3768. Dòng 2622 giữ NEG ở cấp Sài Gòn vì caption chỉ xác định tình trạng ngập thường xuyên và thiếu tên năm đường. Các dòng còn lại được đối chiếu với địa bàn ngoài phạm vi. [Ghi nhận của VOV tại Hà Nội](https://vov.gov.vn/ha-noi-mua-ngot-nhieu-duong-van-ngap-sau-toi-1m-o-to-va-xe-may-chet-may-la-liet-dtnew-1117975), [Ghi nhận hiện trường của Báo Hà Tĩnh](https://baohatinh.vn/het-mua-roi-thanh-pho-ha-tinh-van-con-song-post122496.html)
- **12 dòng cần nguồn** gồm 63, 692, 1909, 1913, 1915, 1931, 1935, 1939, 1945, 2359, 2827 và 3240. Bảy dòng sông Đồng Nai giữ NEU tạm thời vì văn bản là số liệu hoặc quan trắc thủy văn và thiếu đoạn sông hoặc trạm. Năm dòng còn lại giữ `[]` do chưa đủ căn cứ về hiện trường hoặc địa bàn.
- SHA-256 của dataset tại mốc đối chiếu nguồn là `af7fed3569613eb384a1103e7a422a4423606166cbbb7fd3cb335c1598c6b1aa`.

### Checkpoint 39 lô tại mốc đối chiếu nguồn

Số dòng chỉnh được tính so với bản có 717 lượt REVIEW. Lô 39 có 75 dòng.

| Lô | Dòng | Dòng chỉnh | Triplet | Dòng `[]` | ERROR |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | 1–100 | 12 | 128 | 7 | 0 |
| 2 | 101–200 | 10 | 165 | 6 | 0 |
| 3 | 201–300 | 9 | 139 | 10 | 0 |
| 4 | 301–400 | 9 | 146 | 3 | 0 |
| 5 | 401–500 | 8 | 130 | 8 | 0 |
| 6 | 501–600 | 10 | 159 | 2 | 0 |
| 7 | 601–700 | 8 | 140 | 9 | 0 |
| 8 | 701–800 | 5 | 118 | 15 | 0 |
| 9 | 801–900 | 8 | 127 | 5 | 0 |
| 10 | 901–1000 | 12 | 123 | 5 | 0 |
| 11 | 1001–1100 | 6 | 102 | 4 | 0 |
| 12 | 1101–1200 | 3 | 104 | 4 | 0 |
| 13 | 1201–1300 | 0 | 100 | 0 | 0 |
| 14 | 1301–1400 | 0 | 100 | 0 | 0 |
| 15 | 1401–1500 | 0 | 100 | 0 | 0 |
| 16 | 1501–1600 | 0 | 100 | 0 | 0 |
| 17 | 1601–1700 | 0 | 100 | 0 | 0 |
| 18 | 1701–1800 | 13 | 100 | 0 | 0 |
| 19 | 1801–1900 | 31 | 100 | 0 | 0 |
| 20 | 1901–2000 | 0 | 100 | 0 | 0 |
| 21 | 2001–2100 | 8 | 96 | 11 | 0 |
| 22 | 2101–2200 | 6 | 115 | 10 | 0 |
| 23 | 2201–2300 | 8 | 102 | 11 | 0 |
| 24 | 2301–2400 | 4 | 82 | 23 | 0 |
| 25 | 2401–2500 | 4 | 105 | 13 | 0 |
| 26 | 2501–2600 | 4 | 115 | 5 | 0 |
| 27 | 2601–2700 | 7 | 109 | 6 | 0 |
| 28 | 2701–2800 | 6 | 114 | 7 | 0 |
| 29 | 2801–2900 | 6 | 118 | 7 | 0 |
| 30 | 2901–3000 | 9 | 130 | 2 | 0 |
| 31 | 3001–3100 | 11 | 125 | 8 | 0 |
| 32 | 3101–3200 | 6 | 109 | 11 | 0 |
| 33 | 3201–3300 | 8 | 122 | 4 | 0 |
| 34 | 3301–3400 | 8 | 144 | 4 | 0 |
| 35 | 3401–3500 | 10 | 113 | 5 | 0 |
| 36 | 3501–3600 | 5 | 114 | 6 | 0 |
| 37 | 3601–3700 | 8 | 122 | 0 | 0 |
| 38 | 3701–3800 | 9 | 90 | 15 | 0 |
| 39 | 3801–3875 | 6 | 68 | 17 | 0 |
| **Tổng** | **1–3875** | **277** | **4474** | **243** | **0** |

Các tệp đối chiếu nằm trong `scripts/scratch/`. Manifest tại mốc này là `phase3_source_followup.expected.json`. Hai sổ cờ là `phase3_source_followup_reviews_baseline.csv` và `phase3_source_followup_reviews_final.csv`. Lý do theo từng ca tra nguồn nằm trong `phase3_source_followup_decisions.json` và `phase3_source_followup_pending.json`. Báo cáo kiểm định là `deep_10_pass_audit.phase3_source_followup.json` và `audit_index_integrity.phase3_source_followup.json`.

## Áp dụng các chỉnh sửa từ lần rà soát tiếp theo

Đã cập nhật 18 dòng nhãn và chuẩn hóa khoảng trắng ở 3 dòng. Bản tại mốc áp dụng gồm 3.875 dòng, 4.476 triplet, 244 dòng `[]` và 727 cờ REVIEW trên 670 dòng. Cả hai trình kiểm định toàn file với manifest hiện hành báo 0 lỗi kỹ thuật. Dataset giữ nguyên thứ tự. 12 trường hợp thiếu nguồn của mốc trước còn mở.

SHA-256 của dataset tại mốc này là `cba22c33c3345fa930e7f8cc5f6b31b3c66960738a87e095c4babf5b6589a780`. Manifest tại mốc này nằm tại `scripts/scratch/phase3_reaudit_applied.expected.json`. Các thay đổi từng dòng và căn cứ nằm trong [báo cáo rà soát](BAO_CAO_RA_SOAT_TOAN_VAN_PHASE3_THUAN.md) và `scripts/scratch/phase3_reaudit_applied_decisions.json`.

## Mốc gán nhãn từ văn bản của chính dòng trước khi bật lại fallback

Mỗi bản ghi là một mẫu độc lập. Aspect, opinion và polarity được quyết định từ văn bản trước `####` và cẩm nang ASTE. Tiền tố địa danh đã có trong dataset được đọc cùng câu. Địa danh ngoài phạm vi nêu trong thân câu vẫn được ưu tiên hơn tiền tố. Bước chuẩn hóa fallback hoặc triều cường chỉ áp dụng khi có đủ căn cứ địa lý trong chính dòng.

- Đã chỉnh 48 bản ghi. Trong số đó, 35 bản ghi được khôi phục phần text trước các lần thêm địa danh. Các bản ghi khác thay đổi nhãn trên text hiện có.
- Dòng 2091 và 2215 trở lại NEG vì dòng tự mô tả hiện trường và xe chết máy ở TP.HCM. Dòng 3040 và 3067 trở lại NEG vì phần text chỉ nói các tuyến bị ngập, thiếu phát ngôn dự báo hay điều kiện.
- Dòng 2781 khôi phục nguyên đoạn kết bị cắt ở `TP.` và để `[]`. Dòng 3559 chỉ nêu dắt xe và gặp mưa, còn dòng 3657 nêu nơi làm việc và nơi gặp ngập bằng đại từ chỉ định. Cả hai được bỏ tiền tố thêm sau lượt đọc nguồn và gán `[]`.
- Dòng 2180 và 2499 có tiền tố địa bàn trong text trước đợt rà và xác nhận ngập nên được gán NEG. Dòng 3554 chỉ nêu xe buýt bị kẹt và được gán `[]`.
- Các trường hợp từng chờ nguồn được xử lý từ nội dung hiện có. Bảy dòng sông Đồng Nai giữ NEU cho quan trắc thủy văn. Dòng 2359 gán NEG vì có tiền tố địa bàn và phát ngôn ngập. Các dòng 63, 692, 2827 và 3240 giữ `[]` theo mức độ căn cứ trong từng text.

Bản tại mốc này có 3.875 dòng, 4.449 triplet và 268 dòng `[]`. Cả hai lượt kiểm định toàn file với manifest mới báo 0 lỗi kỹ thuật. Công cụ phát 751 cờ REVIEW trên 694 dòng. SHA-256 là `730cc9f922d4af74523934d3fb0037e6b852dbb5817e06f1de4210b3c79aecf3`. Manifest ở `scripts/scratch/phase3_row_text.expected.json` và [các quyết định theo dòng](../scripts/scratch/phase3_row_text_decisions.json).

## Mốc áp dụng fallback theo cẩm nang và polarity theo từng câu

Đọc từng bản ghi độc lập để chọn aspect, opinion và polarity. Khi câu mô tả hiện trường, nguy cơ hoặc biện pháp chống ngập đủ rõ và thiếu địa danh của sự kiện, vẫn được thêm tiền tố `Tại TPHCM , ` theo cẩm nang. Aspect khi đó là `TPHCM` tại index [1]. Tính lại toàn bộ index trên text sau chuẩn hóa. Quy tắc riêng cho cụm triều cường và đỉnh triều tiếp tục áp dụng. POS, NEG và NEU được quyết định bằng phát ngôn có trong dòng.

- Cập nhật 32 dòng từ mốc trước, gồm 30 dòng thêm tiền tố fallback và hai dòng chuẩn hóa cụm thủy văn theo mục III.2.6.
- Dòng 3657 dùng fallback cho nơi gặp ngập chưa có tên và giữ toàn bộ hậu quả nêu trong câu với NEG. Bình Dương chỉ là nơi người kể làm việc. Dòng 3041 và 3068 dùng fallback với NEU vì câu tự nêu điều kiện triều vượt báo động và kết quả dự kiến.
- Dòng 3559 giữ `[]` vì chỉ mô tả dắt xe và gặp mưa. Dòng 2781 giữ `[]` vì phần hiện có ghi Nam Bộ và địa danh cụ thể bị cắt ở `TP.`.
- Kiểm định toàn bộ 3.875 dòng trên bản cập nhật thu được 4.483 triplet, 236 dòng `[]` và 0 lỗi kỹ thuật. Có 720 cờ REVIEW trên 663 dòng.
- SHA-256 tại mốc này là `70fc45bc84f0e95faea797df87069769a6ab045f69168be753d6c494fe353ec4`. Manifest tại mốc này là `scripts/scratch/phase3_text_fallback.expected.json`. [Lý do và nhãn theo từng dòng](../scripts/scratch/phase3_text_fallback_decisions.json)

## Rà soát tổng thể trước khi chốt Phase 3

File kiểm tra có **3.875 dòng**, nhiều hơn 10 dòng so với số nêu trong yêu cầu. Phạm vi kiểm tra bao phủ toàn bộ file. Áp dụng cẩm nang ASTE, chỉ đọc ngữ cảnh có trong từng dòng và dùng fallback/chuẩn hóa thủy văn ở những chỗ cẩm nang cho phép.

| Phép đo | Bản được đo | Số mẫu đạt | Tỷ lệ | Khoảng Wilson 95% |
| --- | --- | ---: | ---: | ---: |
| Mẫu ngẫu nhiên thứ nhất | Bản đầu lượt rà | 117/120 | 97,5% | 92,9–99,1% |
| Mẫu ngẫu nhiên thứ hai, không trùng mẫu đầu | Bản sau khi sửa 50 dòng, trước bốn chỉnh sửa cuối | 76/80 | 95,0% | 87,8–98,0% |
| Kiểm định kỹ thuật toàn file | Bản đã sửa | 3.875/3.875 | 100% trong phạm vi phép kiểm | — |

Một dòng đạt nếu mọi aspect, opinion, polarity, vị trí xuất hiện và quyết định `[]` trong dòng đều được chấp nhận khi đọc nguyên văn. Mẫu đầu được rút bằng seed 3633875. Mẫu sau dùng seed 3634483 và loại các dòng đã xuất hiện trong mẫu đầu. Hai tỷ lệ đo ở hai bản khác nhau. Bốn lỗi của mẫu thứ hai đã được sửa. Chưa có điểm ngữ nghĩa độc lập mới cho bản sau bốn chỉnh sửa đó. Không dùng điểm kỹ thuật để suy ra tỷ lệ đúng ngữ nghĩa. Đợt này kiểm định kỹ thuật tất cả dòng và đọc lại 200 dòng ngẫu nhiên cùng các nhóm nghi vấn trên toàn file. Chưa thực hiện một vòng gán nhãn độc lập từng dòng cho cả 3.875 bản ghi trong đợt này.

Đã sửa **54 dòng**, gồm 50 dòng ở lượt đối chiếu các kiểu phát ngôn tương tự và 4 dòng từ mẫu kiểm tra kế tiếp. Trong số đó có 43 dòng chuẩn hóa cụm thủy văn và hai dòng thêm tiền tố fallback. Số lượng và thứ tự dòng được giữ nguyên.

- Dòng 911 khôi phục nhãn NEU cho trạng thái triều đạt đỉnh đã nói rõ trước phần câu bị cắt. Dòng 1078 và 2818 bổ sung NEU cho trạng thái triều, đồng thời giữ NEG cho hậu quả ngập.
- Dòng 373 bổ sung rạch Thủ Đức làm aspect cho hoạt động cải tạo. Dòng 1003 giữ `biến thành hầm` làm opinion của phát ngôn lo ngại. Dòng 3420 gán theo cụm địa bàn được mô tả là có nhiều đường ngập. Dòng 3453 chuyển thành `[]` vì text chỉ có ùn tắc giao thông.
- Bản đã sửa có **4.533 triplet**, gồm 2.510 NEG, 825 NEU, 1.198 POS và 231 dòng `[]`. Hai trình kiểm định và phép dựng span toàn file với manifest hiện hành báo 0 lỗi kỹ thuật. Bộ kiểm tra phát 715 cờ REVIEW trên 658 dòng.
- SHA-256 tại mốc rà soát mẫu là `00a4850ea5852d457d4cb70b4e9e7dd7273f13a00e80718105438bccabbdba15`. Manifest ở `scripts/scratch/phase3_final_verify.expected.json`. [Mẫu 120](../scripts/scratch/phase3_final_review_sample.csv) · [Mẫu 80](../scripts/scratch/phase3_final_verify_sample.csv) · [50 dòng sửa đầu](../scripts/scratch/phase3_final_review_decisions.json) · [4 dòng sửa sau](../scripts/scratch/phase3_final_verify_decisions.json)

## Mốc đọc lại toàn bộ 3.875 dòng

- Hoàn thành lượt rà soát theo nội dung từng dòng. Bản đầu lượt rà có 3.714/3.875 dòng được chấp nhận (95,85%). Đã sửa đủ 161 dòng phát hiện cần đổi nhãn hoặc chuẩn hóa text.
- Bản hiện hành có 3.875 dòng, 4.540 triplet, 279 dòng `[]`, 0 ERROR và 765 cờ REVIEW trên 707 dòng. SHA-256 `a6e69889fae6885ea33c6a17277a3bfd394953e388678ee9903bfc599e31be0f`.
- [Báo cáo tổng thể](BAO_CAO_RA_SOAT_TOAN_VAN_PHASE3_THUAN.md) · [Bản đầu lượt rà](../scripts/scratch/phase3_exhaustive_snapshot.txt) · [Nhật ký chỉnh sửa](../scripts/scratch/phase3_exhaustive_decisions.json) · [Kết quả theo dòng](../scripts/scratch/phase3_exhaustive_records.csv)

## Mốc xử lý 765 cờ REVIEW

Đã có kết luận cho 765/765 cờ ban đầu trên 707 dòng. Đã sửa 34 dòng, giữ đủ 3.875 dòng và kiểm định 4.555 triplet với 0 lỗi kỹ thuật. SHA-256 tại mốc đó là `4aa89ce44bd3006cbb18bc5302c08c659866afdbc113123cff7d2582025487f4`. [Cờ ban đầu](../scripts/scratch/phase3_review765_ban_dau.csv) · [Cờ trên bản sau sửa](../scripts/scratch/phase3_review765_ban_da_sua.csv) · [Bản sao trước đợt xử lý](../scripts/scratch/phase3_review765_before.txt)

## Mốc đối chiếu trước khi chốt

Đã đối chiếu toàn file và sửa thêm 22 dòng. Bản hiện hành có 3.875 dòng, 4.540 triplet, 279 dòng `[]` và 0 lỗi kỹ thuật. SHA-256 `a9e550b6cee641d2462d10ac9e62613738fc035b115679abbdc78d127363f1e1`. [Báo cáo](BAO_CAO_RA_SOAT_TOAN_VAN_PHASE3_THUAN.md) · [Nhãn trước và sau](../scripts/scratch/phase3_prechot_decisions.json) · [Bản sao trước lượt đối chiếu](../scripts/scratch/phase3_prechot_before.txt)

## Mốc đo lại tỷ lệ đúng ngữ nghĩa

Mẫu đầu đạt 140/150 dòng trước sửa. Mẫu khác đạt 54/60 dòng sau đợt sửa đầu. Đã sửa 54 dòng phát hiện trong và ngoài mẫu. Bản hiện hành có 3.875 dòng và 4.503 triplet, với 0 lỗi kỹ thuật. SHA-256 `c024db29d50d9749f7b4ac46609c9fd1ea774902d28ca0cbba902cdb0bdd0e3b`. [Thống kê](../scripts/scratch/phase3_quality_stats.json) · [Bản sao đầu lượt rà](../scripts/scratch/phase3_quality_before.txt)

## Mốc đối chiếu toàn file và sửa nhãn sai

Bản đầu lượt rà có 3.866/3.875 dòng được chấp nhận (99,77%). Đã sửa 9 dòng trực tiếp trong Phase 3. File có 4.507 triplet, 320 dòng `[]` và 0 lỗi kỹ thuật. SHA-256 `a0e4652665063f313920032e0f44c9f8239f7d59c380fc6366fff2aafd828894`. [Bảng đối chiếu](../scripts/scratch/phase3_fullfinal_doi_chieu.csv)

## Mốc kiểm tra lại span và ngữ cảnh

Sửa 14 dòng trong `phase3.txt`. Bản hiện hành có 3.875 dòng, 4.504 triplet, 321 dòng `[]` và 0 lỗi định dạng hoặc index. SHA-256 `590d911e3e3bf0e48f2d8fdc9f29baf4652db42a5df8ed0745ebd69bee6c1702`. [Nhật ký chỉnh sửa](../scripts/scratch/phase3_labelcheck_decisions.json)
