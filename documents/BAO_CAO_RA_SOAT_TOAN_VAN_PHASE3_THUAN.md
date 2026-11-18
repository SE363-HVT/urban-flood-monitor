# Rà soát nhãn ASTE của Thuận trong Phase 3

Đối tượng rà soát là [phase3.txt](../data/validate_label/thuan/phase3.txt), gồm 3.875 bản ghi. Quy tắc áp dụng là [cẩm nang ASTE của dự án](BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md), trong đó Bình Dương và Bà Rịa – Vũng Tàu thuộc phạm vi nghiên cứu. Phần kiểm định ghi lại kết quả trên bản trước khi sửa. Phần cuối ghi các chỉnh sửa đã áp dụng và thống kê của bản hiện hành.

## Kết quả index và định dạng

| Nội dung | Kết quả |
| --- | ---: |
| Bản ghi kiểm định toàn file | 3.875 |
| Triplet giải mã và đối chiếu manifest | 4.474 |
| Phân bố polarity | 2.503 NEG, 1.199 POS, 772 NEU |
| Bản ghi `[]` | 243 |
| Aspect một token | 812 triplet |
| Index ngoài phạm vi, span rỗng hoặc đứt đoạn, overlap trong triplet | 0 |
| Khác nội dung, cụm từ, vị trí bắt đầu, polarity hoặc số triplet so với manifest | 0 |
| Dòng có khoảng trắng thừa ngay trước `####` | 3 |
| Cờ `REVIEW` do công cụ phát sinh | 727 trên 670 dòng |

Cả `deep_10_pass_audit.py` và `audit_index_integrity.py` chạy với manifest hiện hành. Một lượt giải mã riêng dùng `split()` và `tokens[i]` cho từng triplet rồi đối chiếu cụm từ, vị trí bắt đầu và polarity. Cả hai phép đối chiếu đồng ý với manifest trước đó. Vì manifest phản ánh các quyết định gán cũ, một cụm từ đã được chọn sai từ trước vẫn có thể khớp hoàn toàn khi kiểm tra bằng công cụ.

Dòng [286](../data/validate_label/thuan/phase3.txt#L286), [488](../data/validate_label/thuan/phase3.txt#L488) và [564](../data/validate_label/thuan/phase3.txt#L564) có một khoảng trắng dư cuối phần text. `split()` bỏ khoảng trắng này nên các index không dịch chuyển. Việc này chỉ cần chuẩn hóa nếu pipeline yêu cầu phần text phải đúng dạng `" ".join(text.split())`.

Có 214 triplet có cụm aspect lặp nguyên dạng trong câu và 15 triplet có cụm opinion lặp. Việc một cụm xuất hiện nhiều lần tự thân không phải lỗi. Hai trường hợp chọn nhầm lần xuất hiện được mô tả bên dưới. Dòng 227, từng có lỗi vượt biên, hiện giải mã triplet thứ hai thành `đường Phan Huy ích` với index 5–8 và `Xe buýt ch * t máy` với index 10–15, nhãn NEG. [Dòng 227](../data/validate_label/thuan/phase3.txt#L227)

## Sai lệch có căn cứ trực tiếp

Các khoảng index trong bảng tính từ 0 và gồm cả hai đầu. Những trường hợp có thể dựng span từ văn bản hiện tại được đối chiếu theo cụm nguyên văn.

| Dòng | Hiện trạng | Phân tích và đề xuất |
| --- | --- | --- |
| [355](../data/validate_label/thuan/phase3.txt#L355) | Opinion 18–26, NEU | Giữ `vừa` ở token 17 vì bổ nghĩa trực tiếp cho hành động phát cảnh báo. Opinion đề xuất là `vừa cảnh báo 122 điểm có nguy cơ ngập nước`, 17–26, NEU. |
| [675](../data/validate_label/thuan/phase3.txt#L675) | `Lê Văn Thọ` 13–15, `đang ngập như thế nào` 16–20, NEU | Cả câu cho biết nhìn hiện trường là đã thấy Lê Văn Thọ đang ngập. `Như thế nào rồi hen` nằm trong nhận xét `Nhìn vậy cũng đủ hiểu`. Ngữ cảnh xác nhận ngập hiện tại. Giữ aspect, đề xuất opinion 16–21 và NEG. |
| [788](../data/validate_label/thuan/phase3.txt#L788) | Cả POS lẫn NEU dùng `chợ Thủ Đức` 46–48 | Opinion NEU `LIỆU CÓ ĐỦ` 18–20 đặt câu hỏi về ngân sách trong tiêu đề, nơi có `CHỢ THỦ ĐỨC` 14–16. Dùng 14–16 cho NEU. Triplet POS vẫn dùng 46–48 vì gắn với mục tiêu cải tạo trong thân bài. |
| [2076](../data/validate_label/thuan/phase3.txt#L2076) | Chỉ gán `đường Tô Ngọc Vân` 33–36 với `thành sông` 47–48, NEG | Cả tuyến đường và khu vực chợ đều được nêu trực tiếp là nơi thành sông. Bổ sung `chợ Thủ Đức` 40–42 với cùng opinion 47–48, NEG. |
| [2091](../data/validate_label/thuan/phase3.txt#L2091), [2215](../data/validate_label/thuan/phase3.txt#L2215) | Gán NEG cho cảnh xe chết máy ở TP.HCM | Văn bản nguồn cho thấy đây là đoạn dẫn của bài quảng bá bất động sản The Global City. Khi áp dụng quy tắc loại quảng cáo theo toàn bài, cả hai đoạn trích nên để `[]`, nhất quán với 2090 và 2092–2094. |
| [3040](../data/validate_label/thuan/phase3.txt#L3040), [3067](../data/validate_label/thuan/phase3.txt#L3067) | `bị ngập nước do triều cường`, NEG | Nguồn nói danh sách tuyến **sẽ** ngập khi triều vượt báo động. Dòng 571 giữ được ngữ cảnh đầy đủ và đã là NEU. Giữ index đã chọn ở 3040 và 3067, đổi polarity sang NEU. Ở 3040, aspect 13–14 đã trỏ đúng TP.HCM trong tiêu đề, trước tên cơ quan. |
| [3090](../data/validate_label/thuan/phase3.txt#L3090) | Cả hai triplet dùng `TPHCM` 39 | Với opinion tiêu đề `Mất chỗ ngủ , đi ủng cả ngày trong nhà` 0–9, địa danh trong cùng tiêu đề ở token 14. Đổi aspect của riêng triplet này từ 39 sang 14. Token 39 vẫn phù hợp với opinion ở thân bài. |
| [3507](../data/validate_label/thuan/phase3.txt#L3507) | Chỉ gán `ngập sâu đến vậy` 33–36, NEG | Giữ trạng thái lặp `lại` ở token 32. Văn bản còn nêu thông tin thủy văn `triều cường ở TPHCM` 20–23 với `dâng cao` 24–25, phù hợp thêm NEU nếu giữ cả phát ngôn thủy văn được dẫn lại trong câu. |
| [3633](../data/validate_label/thuan/phase3.txt#L3633) | Opinion NEG bắt đầu ở token 30 | Lấy từ token 29 để giữ đúng `lại dính nước ngập , xe chết máy`, 29–36. |
| [3674](../data/validate_label/thuan/phase3.txt#L3674) | `Mong cải thiện ... không có ngập`, POS | Đây là mong muốn của người dân về đường 38. Bài gốc có dự án đã được duyệt ở một đoạn riêng, và dòng 3675 đã để NEU cho lời mong tương tự. Nên dùng NEU cho câu nói này và dùng POS cho thông tin dự án cụ thể. |

Nguồn tại chỗ cho dòng 2091/2215 nằm trong [Facebook thô của đợt 02](../data/raw/episodes/episode_02_2026-09-17_anh-huong-bao-so-4/facebook_raw.json#L982). Nguồn cho dòng 3040/3067 là [Facebook thô lưu trữ](../data/raw/episodes/historical_archive/facebook_raw.json#L7086). Nguồn cho dòng 3674 là [bài về đường 38 của VOV Giao thông](https://vovgiaothong.vn/newsaudio/ron-ngap-lau-nam-tai-tp-thu-duc-d44125.html), có bản sao trong [kho tin gốc](../data/raw/episodes/historical_archive/news_raw.json#L1078).

## Địa danh trong bài gốc và ranh giới của dòng trích

| Dòng | Đối chiếu | Nhận định |
| --- | --- | --- |
| [3554](../data/validate_label/thuan/phase3.txt#L3554) | Bài gốc xác định xe buýt kẹt cứng trên **đường Võ Văn Ngân**, đoạn chợ Thủ Đức. | Triplet NEG mô tả đúng hậu quả. Fallback TP.HCM hợp lệ trên đoạn text hiện tại, nhưng kém cụ thể hơn bài gốc. |
| [3558](../data/validate_label/thuan/phase3.txt#L3558) | Câu `Đoạn ngập nặng khoảng nửa mét` đứng ngay sau câu nói về **đường Lê Văn Việt**, cũng xuất hiện ở dòng 3557. | NEG đúng. Nếu muốn aspect cấp đường, cần phục hồi câu định vị có thật trong nguồn rồi tính index từ text mới. |
| [3559](../data/validate_label/thuan/phase3.txt#L3559) | Bài gốc đặt cảnh dắt xe tại **đường Dương Văn Cam** do xe chết máy khi vượt ngập. Thủ Đức và quận 10 trong câu chỉ điểm đi và điểm đến. | `[]` đang làm mất dấu một hậu quả đã xác nhận. Nếu giữ nguyên cách tách đoạn, có thể dùng tiền tố `Tại TPHCM , ` và NEG cho `Vừa hì hục dắt xe máy lên vỉa hỉa`. Nếu phục hồi câu định vị từ bài gốc, dùng đường Dương Văn Cam. |
| [3560](../data/validate_label/thuan/phase3.txt#L3560), [3674–3675](../data/validate_label/thuan/phase3.txt#L3674) | Bài gốc lần lượt xác định **đường Dương Văn Cam** và **đường 38**. | Triplet hiện dùng thành phố vì đoạn trích thiếu tên đường. Để nâng độ cụ thể cần phục hồi đoạn nguồn hoặc lưu liên kết ngữ cảnh. Việc đổi index chỉ hợp lệ sau khi cụm địa danh thực sự có trong text. |

Các nguồn tương ứng là [Tuổi Trẻ về ngập phía tây TP.HCM](https://tuoitre.vn/mua-lon-gan-2-tieng-nhieu-tuyen-duong-tay-tp-hcm-ngap-sau-xe-chet-may-hang-loat-20250918183303942.htm), [Tin tức 24h về Lê Văn Việt và Dương Văn Cam](https://www.24h.com.vn/tin-tuc-trong-ngay/sai-gon-mua-tam-ta-xe-may-ngap-gan-toi-yen-o-to-chet-may-bong-benh-trong-nuoc-c46a1254916.html), và [VOV Giao thông về đường 38](https://vovgiaothong.vn/newsaudio/ron-ngap-lau-nam-tai-tp-thu-duc-d44125.html). Các bản sao tương ứng được đối chiếu trong [kho tin gốc](../data/raw/episodes/historical_archive/news_raw.json#L475).

## Các trường hợp cần thống nhất cách gán

- **Danh sách tuyến và giao lộ**. Dòng 427 nêu hai đường và có một mục riêng `Giao lộ Lê Quang Đạo - Trần Văn Mười`, index 36–44. Hai giao lộ còn lại đóng vai trò mốc giới hạn của một đoạn. Nếu giao lộ được công bố thành mục ngập độc lập, thêm một triplet NEG cho 36–44 với opinion 2–10. Dòng 3250 là ví dụ đúng, gán đủ cả bảy tuyến cùng một vị ngữ dự báo. [Dòng 427](../data/validate_label/thuan/phase3.txt#L427) · [Dòng 3250](../data/validate_label/thuan/phase3.txt#L3250)
- **Hai cách cắt cùng địa danh**. Dòng 2985 dùng `Thanh Đa` 17–18 và dòng 3848 dùng `khu vực Thanh Đa` 15–18. Hai câu chỉ khác dấu câu cuối và cùng ý nghĩa. Nên thống nhất `Thanh Đa` để hai mẫu có cùng span địa danh. Ngoài trường hợp này, 35 nhóm văn bản trùng sau khi chuẩn hóa chữ hoa và dấu câu có cùng chữ và polarity đã gán. [Dòng 2985](../data/validate_label/thuan/phase3.txt#L2985) · [Dòng 3848](../data/validate_label/thuan/phase3.txt#L3848)
- **Opinion dạng danh từ**. Dòng 257 và 2555 gán cả cụm `dòng nước ngập`, đi sau giới từ `giữa`. Đây là cụm chỉ bối cảnh. Cần rà lại ranh giới theo IV.1.2. Phương án giữ hiện trường là lấy lõi `nước ngập` tại 10–11 và 8–9, vì câu vẫn định vị nước ngập tối qua ở Sài Gòn. [Dòng 257](../data/validate_label/thuan/phase3.txt#L257) · [Dòng 2555](../data/validate_label/thuan/phase3.txt#L2555)
- **Tiêu đề danh sách chưa nêu tên tuyến**. Dòng 88 đang là `[]`, còn dòng 2622 gán NEG ở cấp Sài Gòn. Cả hai cùng nhắc năm tuyến thường ngập nhưng không cung cấp tên tuyến. Cần dùng một tiêu chí cho cả hai, dựa vào việc lời văn có tự xác nhận ngập tái diễn hay chỉ giới thiệu danh sách. [Dòng 88](../data/validate_label/thuan/phase3.txt#L88) · [Dòng 2622](../data/validate_label/thuan/phase3.txt#L2622)
- **Câu giả định hoặc nhận xét chung**. Dòng 610 nói về khả năng tình trạng ngập giảm nếu người dân thay đổi hành vi. Có thể lấy `Sài Gòn` 13–14 và `có lẽ sẽ giảm đi rất nhiều` 15–21, NEU, nếu cẩm nang được áp dụng để giữ giả định địa phương. Nếu xếp bài vào bình luận xã hội không có dữ kiện hiện trường, giữ `[]`. Dòng 719, 720 và 3204 dùng cấu trúc giả định nhưng mô tả các tuyến cụ thể thường ngập với độ sâu cụ thể, có cơ sở để giữ NEG theo nhóm hiện trạng lặp lại. [Dòng 610](../data/validate_label/thuan/phase3.txt#L610) · [Dòng 719](../data/validate_label/thuan/phase3.txt#L719)
- **Đoạn cắt cụt và địa lý**. Dòng 3 vẫn có đủ hai cặp aspect–opinion hoàn chỉnh trước phần bị cắt. Dòng 3394 giữ `nước ngập` vì phần độ sâu kết thúc ở `từ 30 -`. Dòng 2180 có tiền tố TPHCM, nhưng hai câu trước định vị hiện trường tại đèo Mẹ Bồng Con, Đồng Nai, nên `[]` phù hợp. Dòng 173 giữ `phường Tân Khánh`, Bình Dương cũ, bởi cầu Khánh Vân chỉ là mốc. [Dòng 3](../data/validate_label/thuan/phase3.txt#L3) · [Dòng 173](../data/validate_label/thuan/phase3.txt#L173) · [Dòng 2180](../data/validate_label/thuan/phase3.txt#L2180) · [Dòng 3394](../data/validate_label/thuan/phase3.txt#L3394)

Còn 12 trường hợp thiếu căn cứ nguồn từ lần rà trước, gồm 63, 692, 1909, 1913, 1915, 1931, 1935, 1939, 1945, 2359, 2827 và 3240. Bảy dòng sông Đồng Nai thiếu đoạn sông hoặc trạm đo. Năm dòng còn lại thiếu địa bàn hoặc hiện trường đủ rõ để chốt. [Danh sách và lý do theo từng dòng](../scripts/scratch/phase3_source_followup_pending.json)

## Phạm vi và khả năng tái kiểm định

- Kiểm tra máy gồm toàn bộ 3.875 dòng, kể cả dòng không có cờ. Cờ gồm 243 quyết định loại, 215 opinion dùng chung, 168 tín hiệu polarity, 72 tín hiệu tiền tố hạ tầng, 15 dấu hiệu địa lý, 9 văn bản trùng và 5 dấu hiệu fallback. Cờ có thể là nhãn đúng, chẳng hạn nhiều tuyến cùng ngập.
- Đối chiếu ngữ cảnh tập trung vào dòng có dấu hiệu nhầm lần xuất hiện, thiếu mức độ hoặc trạng thái, dự báo và sự kiện đã xảy ra, tiền tố địa danh, danh sách tuyến, câu bị cắt và nguồn của các đoạn trích. Quét nhất quán 888 câu trong đoạn có nhiều câu cùng mẫu, thu được 208 mẫu sau khi chuẩn hóa địa danh và con số. Các câu cùng mẫu có cùng opinion đã chuẩn hóa và polarity. Sự nhất quán giữa các câu cùng mẫu chưa đủ để xác nhận từng câu đúng với nguồn.
- Đây là lượt giải mã toàn file và thẩm định ngữ cảnh trên các ca đã đọc lại, dựa thêm vào manifest và quyết định từ lần rà trước. Chưa có bộ nhãn độc lập mới cho từng dòng trong lượt này. Vì đã thấy sai lệch ngữ nghĩa và sai lần xuất hiện, chưa thể kết luận 3.875 dòng đúng hết hoặc nêu tỷ lệ chính xác ngữ nghĩa.
- SHA-256 dataset là `af7fed3569613eb384a1103e7a422a4423606166cbbb7fd3cb335c1598c6b1aa`. SHA-256 cẩm nang là `e139e6598ce0446137fb909ca890b5c7d4c018933ea78344c8b48bbc84a05506`.
- Dữ liệu kiểm định chi tiết nằm trong [bảng giải mã 3.875 dòng](../scripts/scratch/phase3_current_review_rows.tsv), [báo cáo kiểm định toàn file](../scripts/scratch/deep_10_pass_audit.phase3_current_full.json) và [báo cáo đối chiếu index](../scripts/scratch/audit_index_integrity.phase3_current_full.json).

## Kết quả sau khi áp dụng chỉnh sửa

Đã sửa trực tiếp 21 dòng trong `phase3.txt`, gồm 18 dòng đổi nhãn và 3 dòng chuẩn hóa khoảng trắng. Giữ đủ 3.875 dòng và giữ thứ tự. Dòng 3559 là dòng duy nhất được thêm từ vào văn bản. Tiền tố `Tại TPHCM , ` phù hợp với phạm vi đã xác nhận trong nguồn và với cách tách đoạn hiện có.

- Sửa lần xuất hiện của aspect ở 788, 3090 và 3309. Ở 675, lấy lõi hiện trường `đang ngập` với NEG. Ở 3040, 3067 và 3674, đổi polarity sang NEU theo ngữ cảnh nguồn.
- Bổ sung thực thể độc lập ở 427 và 2076, tách thông tin quan trắc triều khỏi ngập thực tế ở 3507. Bỏ hai đoạn dẫn của bài quảng bá bất động sản ở 2091 và 2215 bằng nhãn `[]`.
- Sửa ranh giới opinion ở 257, 355, 2555, 3507 và 3633. Đồng nhất aspect `Thanh Đa` ở 3848 với 2985. Cắt khoảng trắng thừa ở 286, 488 và 564.
- Dòng 3559 bổ sung NEG cho hậu quả dắt xe khi ngập. Nguồn xác nhận sự kiện trên đường Dương Văn Cam. Dòng trích không chứa tên đường nên dùng `TPHCM` [1] và opinion [3–11].
- Giữ 88 ở `[]` vì câu chỉ dẫn vào danh sách. Dòng 2622 có tính từ và cụm từ mô tả ngập lặp lại nên giữ NEG. Giữ 610 ở `[]` vì đây là nhận xét giả định chung về ý thức, thiếu một hiện trường hoặc biện pháp được triển khai. Các đoạn 3554, 3558, 3560 và 3675 vẫn dùng địa danh cấp thành phố theo phần text có sẵn. Tên tuyến chỉ có ở đoạn nguồn khác.
- Hai trình kiểm định chạy toàn file với manifest mới và báo 0 lỗi. Các triplet được dựng lại bằng `span_helper.py` và khớp cả cụm từ lẫn vị trí. Bản tại mốc áp dụng có 4.476 triplet (2.503 NEG, 1.198 POS, 775 NEU), 244 dòng `[]` và 727 cờ REVIEW trên 670 dòng. 12 trường hợp thiếu nguồn đã liệt kê phía trên vẫn cần dữ kiện.
- SHA-256 tại mốc này là `cba22c33c3345fa930e7f8cc5f6b31b3c66960738a87e095c4babf5b6589a780`. [Quyết định trước và sau theo dòng](../scripts/scratch/phase3_reaudit_applied_decisions.json) · [Manifest](../scripts/scratch/phase3_reaudit_applied.expected.json) · [Thống kê](../scripts/scratch/phase3_reaudit_applied_stats.json)

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

## Đối soát ngữ nghĩa từng bản ghi

Đã rà đủ **3.875 dòng** theo cẩm nang ASTE. Mỗi quyết định dựa trên nội dung của chính dòng, kể cả dấu câu, hashtag và phần bị cắt có thể đọc được. Với 888 dòng theo mẫu lặp, bản đối chiếu hiển thị đầy đủ văn bản chung và liệt kê từng số dòng cùng địa danh và vị trí span tương ứng trong 208 nhóm. Các dòng còn lại được đọc dưới dạng nguyên dòng kèm triplet đã giải mã. Tỷ lệ được tính trên toàn bộ file.

| Kết quả | Số dòng | Tỷ lệ |
| --- | ---: | ---: |
| Chấp nhận toàn bộ nhãn ban đầu của dòng | 3.714 | 95,85% |
| Có ít nhất một điểm cần sửa và đã cập nhật | 161 | 4,15% |
| Tổng số bản ghi | 3.875 | 100% |

Một dòng chỉ đạt khi mọi aspect, opinion, polarity, lần xuất hiện của từng cụm và quyết định để `[]` đều phù hợp trong lượt đọc. Tỷ lệ trên đo bản trước khi sửa theo đánh giá của một lượt rà soát. Cần bộ nhãn độc lập để tính Strict F1 hoặc Cohen’s Kappa.

- Dòng **677** giữ hai tuyến đã ngập với NEG và bổ sung NEU cho tình trạng chưa biết của Dương Quảng Hàm.
- Dòng **135** giữ Nguyễn Văn Quá. Song Hành đóng vai trò mốc nối đoạn trong câu nên bỏ hai nhãn gán sự kiện riêng cho tuyến này.
- Dòng **3796** có mô tả ngập và nêu kênh Đôi là nguồn triều. Thêm `Tại TPHCM , `, dùng aspect `TPHCM` ở index `[1]` và opinion bắt đầu ở index 4.
- Dòng **3431** chuyển thành `[]` vì chỉ xác nhận ùn tắc. Dòng **3854** bổ sung NEG cho từng tuyến và khu Chợ Lớn vì câu tự xác nhận cả bốn địa điểm chìm trong nước.

Trong 161 dòng sửa có 36 dòng thay đổi text theo hai quy ước của cẩm nang, gồm 9 tiền tố fallback và 27 lần bổ sung địa danh cho cụm thủy văn. Các span liên quan được dựng lại từ token của text cuối. Đủ 3.875 dòng và giữ thứ tự. Bản hiện hành có 4.540 triplet, gồm 2.468 NEG, 876 NEU, 1.196 POS và 279 dòng ghi `[]`.

Hai trình kiểm định dùng chung bộ quy tắc và đều báo **0 ERROR** sau khi đối chiếu với manifest. Cả 4.540 triplet khớp cụm chữ, vị trí bắt đầu và polarity trong manifest. Còn 765 cờ REVIEW trên 707 dòng, gồm 279 quyết định `[]`, 212 cờ opinion dùng chung, 170 cờ polarity, 71 cờ tiền tố hạ tầng, 15 cờ địa lý, 9 cờ text trùng, 8 cờ fallback và 1 cờ ranh giới. Chẳng hạn, dòng 3070 có dấu hai chấm bên trong cách viết cách điệu `t : ê l : iệt`. Đây là một phần của từ mô tả hậu quả giao thông nên span giữ nguyên dạng chữ của câu.

SHA-256 của bản đã sửa là `a6e69889fae6885ea33c6a17277a3bfd394953e388678ee9903bfc599e31be0f`. [Phase 3 đã cập nhật](../data/validate_label/thuan/phase3.txt) · [Kết quả theo dòng](../scripts/scratch/phase3_exhaustive_records.csv) · [Nhãn trước và sau, kèm lý do](../scripts/scratch/phase3_exhaustive_decisions.json) · [Manifest](../scripts/scratch/phase3_exhaustive.expected.json) · [Kiểm định 10 nhóm](../scripts/scratch/deep_10_pass_audit.phase3_exhaustive.json) · [Kiểm định index](../scripts/scratch/audit_index_integrity.phase3_exhaustive.json)

## Kết luận từng cờ REVIEW của Phase 3

Đã đọc lại ngữ cảnh của cả 707 dòng mang 765 cờ, áp dụng cẩm nang theo văn bản trong từng dòng. **765/765 cờ ban đầu đã có kết luận**. Có 26 cờ mà cụm hoặc quyết định liên quan đã được sửa trực tiếp. 739 cờ được xác nhận giữ kết luận, trong đó có những dòng được sửa ở phần nhãn khác. Tổng cộng **34/707 dòng** cần sửa nhãn hoặc chuẩn hóa text. [Kết luận từng cờ ban đầu](../scripts/scratch/phase3_review765_ban_dau.csv) · [34 dòng đã sửa và lý do](../scripts/scratch/phase3_review765_decisions.json)

- Dòng 37 và 2278 dùng một aspect cho khu vực Linh Đông - Lý Tế Xuyên vì câu nêu một khu vực chung. Những câu liệt kê các tuyến ngập độc lập vẫn giữ mỗi tuyến một triplet.
- Dòng 709 và 710 bổ sung NEU cho khuyến cáo hạn chế đi vào đường Nguyễn Tri Phương và giữ NEG cho hiện trường ngập.
- Dòng 929 có cả ngập đã xảy ra và nước đã rút, nên nhận lần lượt NEG và POS. Dòng 3855 xác nhận ngập tái diễn và dùng fallback `TPHCM` ở index `[1]`.

Bản sau sửa có **3.875 bản ghi, 4.555 triplet, 270 dòng `[]` và 0 lỗi kỹ thuật**. Trình kiểm định phát lại 760 cờ trên 694 dòng theo tiêu chí của công cụ. Bảng đối chiếu bản sau sửa ghi kết luận cho 760 cờ này, kể cả các trường hợp mới xuất hiện do đổi triplet. Kết quả của lượt này chỉ tính cho nhóm 707 dòng mang cờ. [Bảng xác nhận các cờ trên bản sau sửa](../scripts/scratch/phase3_review765_ban_da_sua.csv) · [Manifest hiện hành](../scripts/scratch/phase3_review765.expected.json)

SHA-256 của bản sau sửa là `4aa89ce44bd3006cbb18bc5302c08c659866afdbc113123cff7d2582025487f4`.

## Đối chiếu trước khi chốt Phase 3

Đã quét cả **3.875 dòng** để tìm nhãn thiếu nhất quán ở câu gần trùng, câu lịch sử, hai sắc thái trong cùng bản ghi, câu bị cắt và các dấu hiệu nhầm giữa hiện trạng với dự báo. Đọc lại nguyên văn các trường hợp được tìm ra và quyết định dựa trên nội dung có trong từng dòng. Không đối chiếu bài nguồn hoặc lấy nội dung dòng khác để suy ra nhãn. Đây là lượt rà soát đối chiếu toàn file trên bản sau mốc xử lý 765 cờ.

Đã sửa trực tiếp **22 dòng**. Tám dòng hồi ức hoặc tranh luận về Sài Gòn xưa chuyển về `[]` theo cẩm nang. Ở dòng 3855, hoàn nguyên phần văn bản trước khi thêm fallback ở lượt trước. Dòng 503 giữ Thanh Đa vì sông Sài Gòn được nhắc như nguồn nước. Dòng 886 và 2109 giữ đầy đủ dấu hiệu rủi ro trong opinion NEU. Dòng 720 và 3204 giữ triplet hoàn chỉnh của Lê Văn Thọ và bỏ span dừng ở cụm bị cắt `thì nguyên bán`. [Nhãn trước và sau theo dòng](../scripts/scratch/phase3_prechot_decisions.json)

Hai trình kiểm định đối chiếu toàn bộ **4.540 triplet** với manifest và báo **0 lỗi kỹ thuật**. Bản hiện hành có 2.454 NEG, 886 NEU, 1.200 POS và 279 dòng `[]`. Số lượng và thứ tự 3.875 dòng được giữ nguyên. Lượt đối chiếu bổ sung này không tạo bộ nhãn ngữ nghĩa độc lập cho toàn file.

SHA-256 tại mốc đó là `a9e550b6cee641d2462d10ac9e62613738fc035b115679abbdc78d127363f1e1`. [Dataset](../data/validate_label/thuan/phase3.txt) · [Manifest](../scripts/scratch/phase3_prechot.expected.json) · [Kiểm định 10 nhóm](../scripts/scratch/deep_10_pass_audit.phase3_prechot.json) · [Kiểm định index](../scripts/scratch/audit_index_integrity.phase3_prechot.json)

## Đo lại tỷ lệ đúng ngữ nghĩa bằng mẫu ngẫu nhiên

Một dòng đạt khi toàn bộ aspect, opinion, polarity, index và quyết định `[]` phù hợp với nội dung trong chính dòng. Chọn ngẫu nhiên 150 dòng từ bản đầu lượt rà (seed 38752223) và 60 dòng khác để kiểm tra bản sau đợt sửa đầu (seed 38752224). Đọc toàn văn của từng dòng đã chọn. Hai mẫu không trùng dòng và đo hai phiên bản khác nhau.

| Mốc | Số dòng đạt | Tỷ lệ | Khoảng Wilson 95% |
| --- | ---: | ---: | ---: |
| Bản đầu lượt rà | 140/150 | 93,33% | 88,16–96,34% |
| Bản sau 46 chỉnh sửa đầu tiên, trước các sửa đổi bổ sung | 54/60 | 90,00% | 79,85–95,34% |

Đã sửa 54 dòng, gồm 16 dòng tìm thấy qua hai mẫu và 38 dòng phát hiện khi đối chiếu ngữ cảnh tương tự. Ví dụ, dòng 802 tách POS cho hoạt động dọn dẹp khỏi NEG cho ngập sâu. Dòng 638 bổ sung NEU cho khuyến cáo chọn tuyến khác. Dòng 1624 chuyển về `[]` vì chỉ nêu giao thông thuận lợi. Sau sửa, 210/210 dòng thuộc hai mẫu đều khớp kết luận của lượt rà này. Kết quả 210/210 là kiểm tra trên chính các dòng đã đọc và sửa. Chưa có tỷ lệ đúng ngữ nghĩa chính xác cho toàn bộ bản mới sau cả 54 chỉnh sửa.

Bản hiện hành có **3.875 dòng**, **4.503 triplet**, **320 dòng `[]`** và **0 lỗi kỹ thuật**. SHA-256 là `c024db29d50d9749f7b4ac46609c9fd1ea774902d28ca0cbba902cdb0bdd0e3b`.

[Mẫu 150 dòng](../scripts/scratch/phase3_quality_sample.csv) · [Mẫu kiểm tra 60 dòng](../scripts/scratch/phase3_quality_holdout.csv) · [54 quyết định sửa](../scripts/scratch/phase3_quality_decisions.json) · [Manifest hiện hành](../scripts/scratch/phase3_quality.expected.json)

## Đối chiếu toàn bộ 3.875 bản ghi

Bản đầu lượt rà có SHA-256 `c024db29d50d9749f7b4ac46609c9fd1ea774902d28ca0cbba902cdb0bdd0e3b`. Đã đối chiếu từng số dòng với nhật ký của lượt đọc toàn văn, các lần sửa sau đó và bản giải mã triplet hiện tại. Trong lượt này đọc lại trực tiếp 230 dòng từng thay đổi hoặc có dấu hiệu sai ngữ cảnh. 3.645 dòng còn lại được đối chiếu với kết luận của lượt đọc trước và kiểm định kỹ thuật hiện tại. Tiêu chí theo từng câu, không tra nguồn hoặc dựa vào câu kế bên để gán aspect hay polarity.

- **3.866/3.875 dòng (99,77%)** được chấp nhận ở bản đầu lượt rà. **9/3.875 dòng (0,23%)** phát hiện nhãn sai hoặc thiếu. Đây là tỷ lệ theo kết quả đối chiếu các lượt, chưa phải thước đo dựa trên một lần gán nhãn độc lập lại toàn bộ file.
- Bản Phase 3 đầy đủ đã sửa nhãn ở 9 dòng, giữ đủ 3.875 dòng theo thứ tự cũ, với 4.507 triplet, 320 dòng `[]` và 0 lỗi kỹ thuật. Hai dòng dùng thêm fallback cho vị trí ngập chưa có tên. SHA-256 `a0e4652665063f313920032e0f44c9f8239f7d59c380fc6366fff2aafd828894`.

[Phase 3 đã sửa](../data/validate_label/thuan/phase3.txt) · [Bảng 3.875 dòng](../scripts/scratch/phase3_fullfinal_doi_chieu.csv) · [Nhãn trước và sau của 9 dòng](../scripts/scratch/phase3_fullfinal_decisions.json)

## Kiểm tra lại span và ngữ cảnh trước khi bàn giao

Đối chiếu lại toàn bộ 3.875 dòng với kết quả rà toàn văn và bản giải mã, sau đó đọc trực tiếp các trường hợp tìm được khi kiểm tra span ngắn, lần xuất hiện của địa danh, ranh giới opinion và tiền tố hạ tầng. Các quyết định dựa trên chính văn bản từng dòng.

Đã sửa 14 dòng trực tiếp trong `phase3.txt`. Ví dụ, dòng 2147 và 2707 chuyển sang NEG vì thống kê xác nhận các điểm ngập hiện hữu. Dòng 419 gán đoạn Đinh Bộ Lĩnh - Bạch Đằng cho cả hiện trường và hoạt động hút nước. Không thay đổi văn bản, số dòng hoặc thứ tự.

Hai trình kiểm định đối chiếu toàn bộ 4.504 triplet, với **0 lỗi định dạng hoặc index**. Có 321 dòng `[]` hợp lệ. SHA-256 bản hiện hành là `590d911e3e3bf0e48f2d8fdc9f29baf4652db42a5df8ed0745ebd69bee6c1702`. [Nhãn trước và sau của 14 dòng](../scripts/scratch/phase3_labelcheck_decisions.json) · [Manifest hiện hành](../scripts/scratch/phase3_labelcheck.expected.json)
