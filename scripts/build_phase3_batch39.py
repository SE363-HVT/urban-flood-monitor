# -*- coding: utf-8 -*-
"""
Script xây dựng và gán nhãn chuẩn hóa cho Phase 3 - Batch 39 (Records 3801 - 3875).
75 records cuối cùng để hoàn tất 100% Phase 3 (3.875 records).
Tuân thủ 100% tài liệu BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md.
"""

batch39_data = [
    # Rec 3801: Cắt prefix nhân tạo -> rạch Văn Thánh
    ("Ngập triều từ rạch Văn Thánh dâng vào .", [
        ([3, 4, 5], [0], 'NEG'),
    ]),

    # Rec 3802: Bullet fragment không có địa danh -> REJECT
    ("→ Ngập sâu – bán đảo thấp , nhận triều trực tiếp .", []),

    # Rec 3803: Cắt prefix -> sông Sài Gòn
    ("→ Ngập khi triều từ sông Sài Gòn dâng .", [
        ([5, 6, 7], [1], 'NEG'),
    ]),

    # Rec 3804: Bullet fragment -> REJECT
    ("→ Một số đoạn ngập triều .", []),

    # Rec 3805: Ghi chú admin group ("ad loại") -> REJECT
    ("Linh Trung – Đường số 6 → chủ yếu ngập mưa , không phải ngập triều → ad loại .", []),

    # Rec 3806: List header ("CHỈ NGẬP KHI MƯA...") -> REJECT
    ("📍 QUẬN BÌNH TÂN – CHỈ NGẬP KHI MƯA + TRIỀU ( KHÔNG NGẬP TRIỀU ĐƠN LẺ )", []),

    # Rec 3807: Admin note ("❌ Bình Long...") -> REJECT
    ("❌ Bình Long – ngập mưa là chính", []),

    # Rec 3808: Admin note ("❌ Hương Lộ 2...") -> REJECT
    ("❌ Hương Lộ 2 – ngập mưa là chính", []),

    # Rec 3809: Admin note ("❌ Mã Lò...") -> REJECT
    ("❌ Mã Lò – kênh Tân Hóa – ngập mưa – KHÔNG phải ngập triều", []),

    # Rec 3810: Admin note ("→ Ad loại...") -> REJECT
    ("→ Ad loại toàn bộ khỏi danh sách “ ngập triều ” .", []),

    # Rec 3811: List header ("📍 BÌNH CHÁNH...") -> REJECT
    ("📍 BÌNH CHÁNH – CHỈ MỘT SỐ ĐOẠN NGẬP TRIỀU , Ít ngập khi mưa nhỏ", []),

    # Rec 3812: Admin note ("ad loại") -> REJECT
    ("→ Ngập mưa → KHÔNG phải ngập triều , ad loại .", []),

    # Rec 3813: List header ("📍 NHÀ BÈ...") -> REJECT
    ("📍 NHÀ BÈ – NGẬP TRIỀU RẤT NẶNG", []),

    # Rec 3814: Bullet fragment -> REJECT
    ("→ Ngập triều sâu nhất khu Nam .", []),

    # Rec 3815: Bullet fragment -> REJECT
    ("→ Ngập triều tại đoạn gần rạch .", []),

    # Rec 3816: Bullet fragment -> REJECT
    ("→ Triều lên mạnh là ngập dù không mưa .", []),

    # Rec 3817: Bullet fragment -> REJECT
    ("→ Ngập do triều từ rạch Nhà Bè dâng .", []),

    # Rec 3818: Bullet fragment -> REJECT
    ("Khu sát bờ kênh / rạch ngập sớm hơn 20 – 40 phút", []),

    # Rec 3819: Bullet fragment -> REJECT
    ("Khi mưa trùng triều → ngập tăng 2 – 3 lần", []),

    # Rec 3820: Dự báo xả lũ thượng lưu -> REJECT
    ("Vì khả năng mưa giai đoạn tới vẫn còn lớn khi kết hợp xả lũ do thượng lưu vẫn đang cao khi dồn về hạ du thì tình trạng ngập úng sẽ tăng cao vào buổi chiều tối đến rạng sáng .", []),

    # Rec 3821: Hashtag TikTok -> REJECT
    ("Nhiều tuyến đường dễ ngập người dân nên lưu ý ! # TVPL # ThuVienPhapLuat # LearnOnTikTok # Hoccungtiktok", []),

    # Rec 3822: Tỉnh ngoài (Quy Nhơn, Bình Định) -> REJECT
    ("Quy Nhơn ngay lúc này cần nhờ mọi người chia sẻ để người dân và tài xế có hướng đi khác để tránh đi qua đập tràn đường Điện Biên Phủ hướng ra QL19 đang bị chặn xe do ngập nha !", []),

    # Rec 3823: Kỹ thuật xe / lời khuyên chung chung -> REJECT
    ("Cùng save lại những điều cần nhớ khi xe chết máy khi ngập nước mùa mưa bão nha ⛈ ️", []),

    # Rec 3824: Chung cư Thủ Đức (cắt 'Ở')
    ("Ở chung cư thủ đức mà còn ngập cỡ này , ở ngoài đường ngập hơn nửa xe oto luôn các bạn ạ .", [
        ([1, 2, 3, 4], [7], 'NEG'),
    ]),

    # Rec 3825: Meme video TikTok hashtag -> REJECT
    ("Các bạn xem cuối video m quay chiếc oto để dưới lòng đường kìa , nó ngập mún đến nóc chiếc xe luôn # muangaplut # ngaplut # thuduc", []),

    # Rec 3826: Quy tắc 6 mở rộng triều cường in-place
    ("Ngập nước do mưa to hay triều cường ở TPHCM giờ chỉ còn là cái tên !", [
        ([6, 7, 8, 9], [0, 1], 'NEG'),
    ]),

    # Rec 3827: Đã có TP HCM, triều cường
    ("Cuộc sống người dân TP HCM bị đảo lộn khi nhiều tuyến đường ngập sâu trong đợt triều cường cao 1 , 78 m , đặc biệt tại các khu vực ven sông , chiều 5 / 11 .", [
        ([4, 5], [13, 14], 'NEG'),
        ([17, 18], [19, 20, 21, 22, 23], 'NEG'),
    ]),

    # Rec 3828: Quy tắc 6 mở rộng triều cường in-place
    ("Trời không mưa mà triều cường ở TPHCM lên ngập to quá .", [
        ([4, 5, 6, 7], [9, 10], 'NEG'),
    ]),

    # Rec 3829: Tỉnh ngoài (Gia Lai) -> REJECT
    ("Tại Gia Lai , mưa lớn những ngày qua đã làm ngập lụt trên diện rộng và sạt lở một số tuyến giao thông trọng điểm .", []),

    # Rec 3830: Tỉnh ngoài (Gia Lai) -> REJECT
    ("Sáng nay ( 19 / 11 ) , do nước lớn , Quốc lộ 1 qua Gia Lai đã bị chia cắt , giao thông tê liệt .", []),

    # Rec 3831: Hoạt động thanh niên tình nguyện -> REJECT
    ("Các thanh niên trẻ tình nguyện dọn dẹp miệng cống để giảm ngập lụt trên đường phố ❤ ️ ❤ ️ ❤ ️", []),

    # Rec 3832: quận 1 (cắt 'thuộc' và 'cũ')
    ("Theo ghi nhận của Dân trí , đợt triều cường chiều 8 / 11 đã gây ngập nặng tại nhiều tuyến đường thuộc quận 1 cũ .", [
        ([23, 24], [16, 17], 'NEG'),
    ]),

    # Rec 3833: Hậu quả người đi xe té ngã -> REJECT
    ("Người đi xe máy chao đảo tay lái , nhiều người bị nước văng ướt sũng .", []),

    # Rec 3834: TPHCM
    ("Mặc dù TPHCM vừa trải qua đợt triều cường được xem là lịch sử , nhưng theo người dân địa phương , đây là lần đầu tiên khu vực trung tâm bị ngập sâu đến vậy .", [
        ([2], [32, 33], 'NEG'),
    ]),

    # Rec 3835: Bản tin cắt cụt chung chung không địa danh cụ thể -> REJECT
    ("Đến 20h , nước tại các tuyến đường trung tâm rút chậm .", []),

    # Rec 3836: TikTok hashtag spam -> REJECT
    ("# Lan167 # Triều cường tp HCM ngập sâu do mực nước dâng cao kỷ lục # xuhuongtiktok2025 ❤ ️ 💕 🇻 🇳 🌹", []),

    # Rec 3837: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Hơn ba giờ sáng mở cửa giật mình nước đã vào trong nhà , đê chưa tràn mà nhà đã ngập nước , lần đầu tiên nhà mình bị ngập kiểu này . vừa cõng con vừa chạy lụt , ớn thật sự", [
        ([1], [23, 24], 'NEG'),
    ]),

    # Rec 3838: Tỉnh ngoài (Hà Đông, Hà Nội) -> REJECT
    ("Ngập lụt ngã tư đường phố , ngã 4 văn phú hà đông", []),

    # Rec 3839: Tỉnh ngoài (Gia Lai) -> REJECT
    ("Ngập lụt bủa vây nhiều khu vực ở Gia Lai", []),

    # Rec 3840: Tỉnh ngoài (Gia Lai) -> REJECT
    ("TPO - Do ảnh hưởng của các đợt mưa lớn những ngày qua , trên địa bàn phía Đông tỉnh Gia Lai đã bắt đầu xảy ra ngập lụt tại một số khu vực .", []),

    # Rec 3841: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhiều phương tiện \" chạy mưa \" chưa kịp về đến nhà đã phải bì bõm lội nước do nhiều tuyến đường bị ngập sau mưa lớn .", [
        ([1], [26], 'NEG'),
    ]),

    # Rec 3842: Hoạt động tình nguyện -> REJECT
    ("Người đàn ông tình nguyện dọn miệng cống thoát nước khi đang ngập lụt đường phố ❤ ️ ❤ ️ ❤ ️", []),

    # Rec 3843: Dự án đầu tư ngăn triều -> REJECT
    ("Với tổng vốn đầu tư 10 . 000 tỷ đồng , dự án cống ngăn triều được kỳ vọng hoàn thành năm 2018 để bảo vệ 6 , 5 triệu dân thuộc khu vực bờ hữu khỏi ngập do triều và biến đổi khí hậu .", []),

    # Rec 3844: Phản ánh dự án đình trệ -> REJECT
    ("Nhưng sau nhiều năm , công trình vẫn đình trệ , còn ngập lụt diễn ra ngày càng nặng nề , đặc biệt ở khu vực quận 7 cũ .", []),

    # Rec 3845: Tản mạn cá nhân than phiền dự án bỏ hoang -> REJECT
    ("Sống cạnh công trường cống Phú Định , ông Nguyễn Văn Tiệm ( 70 tuổi ) cho biết : \" Công trình bỏ hoang mấy năm nay , chúng tôi chỉ mong dự án sớm khởi động lại và có giải pháp thoát nước để không còn chịu cảnh sống chung với ngập \" .", []),

    # Rec 3846: Sài Gòn
    ("Sài Gòn ơi nắng bụi , mưa ngập .", [
        ([0, 1], [6, 7], 'NEG'),
    ]),

    # Rec 3847: Nguyễn Thị Thập (cắt 'q7')
    ("Nguyễn Thị Thập q7 ngập trong biển nước .", [
        ([0, 1, 2], [4, 5, 6, 7], 'NEG'),
    ]),

    # Rec 3848: Thanh Đa, phường Bình Quới
    ("Nước từ sông Sài Gòn tràn qua bờ kè , chảy vào các con hẻm khu vực Thanh Đa , phường Bình Quới , hàng chục hộ dân ngập sâu , đồ đạc hư hỏng , tối 24 / 10", [
        ([20, 21, 22], [28, 29], 'NEG'),
        ([17, 18], [28, 29], 'NEG'),
    ]),

    # Rec 3849: Tỉnh ngoài (Gia Lai) -> REJECT
    ("MƯA LỚN GÂY NGẬP LỤT Ở GIA LAI", []),

    # Rec 3850: Tỉnh ngoài (Gia Lai) -> REJECT
    ("TPO - Từ đêm qua đến sáng 18 / 11 , khu vực phía Đông tỉnh Gia Lai mưa lớn kéo dài gây ngập lụt cục bộ tại một số địa phương .", []),

    # Rec 3851: Sài Gòn (cắt 'ở')
    ("Nước ngập ngang bụng sau mưa lớn ở Sài Gòn 🌧 ️ ⛈ ️", [
        ([8, 9], [1, 2, 3], 'NEG'),
    ]),

    # Rec 3852: Ký ức Sài Gòn trước 1975 -> REJECT
    ("Sài Gòn Xưa Và Những Mùa Nước Ngập : Ký Ức Không Thể Quên Trước 1975", []),

    # Rec 3853: Ký ức Sài Gòn trước 1975 -> REJECT
    ("Sài Gòn trước 1975 không chỉ được nhớ đến bởi những hàng me già , những con đường thanh bình và dòng người hối hả … mà còn bởi những trận ngập lụt bất ngờ đã trở thành một phần ký ức khó quên của người dân nơi đây .", []),

    # Rec 3854: Tuyến đường Trần Hưng Đạo, Nguyễn Huệ, Hàm Nghi, khu Chợ Lớn
    ("Những cơn mưa lớn trút xuống khiến nhiều tuyến đường như Trần Hưng Đạo , Nguyễn Huệ , Hàm Nghi , hay khu Chợ Lớn chìm trong biển nước .", [
        ([11, 12, 13], [25, 26, 27, 28], 'NEG'),
        ([15, 16], [25, 26, 27, 28], 'NEG'),
        ([18, 19], [25, 26, 27, 28], 'NEG'),
        ([22, 23, 24], [25, 26, 27, 28], 'NEG'),
    ]),

    # Rec 3855: Hoài niệm thời ấy -> REJECT
    ("Hệ thống thoát nước thời ấy còn hạn chế , khiến việc ngập trở thành điều quen thuộc mỗi mùa mưa về .", []),

    # Rec 3856: Hoài niệm văn nghệ xưa -> REJECT
    ("Nhưng chính trong cảnh nước dâng , trẻ con lại tung tăng bì bõm , người lớn chèo xuồng tạm qua phố , và Sài Gòn vẫn giữ được vẻ bình yên , mộc mạc đến lạ .", []),

    # Rec 3857: Video ký ức xưa -> REJECT
    ("Video này tái hiện lại hình ảnh những ngày ngập lụt của Sài Gòn xưa – một góc ký ức dung dị mà đầy cảm xúc .", []),

    # Rec 3858: Tin đồn dự báo năm 2025 -> REJECT
    ("Tin nóng ngày 06 / 11 / 2025 , Sài gòn có nguy cơ sắp ngập lụt nhiều khu vực . . . bà con mình cẩn thận . . .", []),

    # Rec 3859: Tản mạn cảm thán người dân thức trắng đêm -> REJECT
    ("Người dân thức trắng đêm giữa biển nước .", []),

    # Rec 3860: TP. HCM dự báo ("có thể ngập" -> NEU theo Pass 8)
    ("Triều cường hôm nay , hơn 20 tuyến đường TP. HCM có thể ngập .", [
        ([9, 10], [11, 12, 13], 'NEU'),
    ]),

    # Rec 3861: Chuyện gia đình tát nước -> REJECT
    ("Tối hôm qua mưa lớn quá nước ngập khắp nhà , tui con phụ mẹ tát nước mệt mún chít lun , giờ tụi con nhủ bù lấy sức đây . . .", []),

    # Rec 3862: Dự đoán vu vơ -> REJECT
    ("bít đâu tối nay Sì Gòn ngập nữa . . . .", []),

    # Rec 3863: Cần Giờ sinh thái rừng ngập mặn -> REJECT
    ("Cách trung tâm TPHCM chỉ khoảng 1 tiếng 30 phút chạy xe máy là bạn đã đến Cần Giờ - nơi có những cánh rừng đước bạt ngàn và hệ sinh thái rừng ngập mặn đa dạng .", []),

    # Rec 3864: Đường Trần Hưng Đạo (CẤM gán CSGT làm Aspect)
    ("Đường Trần Hưng Đạo , CSGT phải hỗ trợ dân di chuyển trong cảnh ngập . . .", [
        ([0, 1, 2, 3], [14], 'NEG'),
    ]),

    # Rec 3865: Than thở mạng xã hội -> REJECT
    ("Lâu lâu ghé qua Quận 7 mà ngập như sông luôn 😭 🌊", []),

    # Rec 3866: Cắt tiền tố nhân tạo -> Hồ Chí Minh
    ("Hồ Chí Minh bị ngập sâu , lượng mưa lên tới 200mm .", [
        ([0, 1, 2], [4, 5], 'NEG'),
    ]),

    # Rec 3867: Hashtag TikTok spam -> REJECT
    ("Mưa to ngập cả đường lớn # sàigòn # mùam # ngập_hết_đường", []),

    # Rec 3868: TP. HCM, triều cường
    ("Khoảng 16 giờ 30 , triều cường từ các con kênh , sông bắt đầu dâng cao và tràn vào nhiều tuyến đường ở khu nam TP. HCM .", [
        ([26, 27], [18, 19], 'NEG'),
        ([5, 6], [15, 16], 'NEG'),
    ]),

    # Rec 3869: đoạn đường Phạm Hữu Lầu
    ("Lúc 18 giờ , đoạn đường Phạm Hữu Lầu ( phường Tân Mỹ ) ngập nặng , kéo dài gần hết tuyến đường như các đợt triều cường trước đây .", [
        ([4, 5, 6, 7, 8], [14, 15], 'NEG'),
    ]),

    # Rec 3870: Fallback 'Tại TPHCM , '
    ("Tại TPHCM , Nhiều nơi nước ngập cao gần bánh xe máy , người dân di chuyển hết sức khó khăn .", [
        ([1], [6, 7, 8, 9, 10, 11], 'NEG'),
        ([1], [19, 20], 'NEG'),
    ]),

    # Rec 3871: Bullet fragment hậu quả chung chung -> REJECT
    ("• Nhiều tuyến đường bị ngập sâu chỉ trong khoảng 30 phút , khiến giao thông bị tê liệt : xe chết máy , người dân phải dắt bộ hoặc tìm đường khác .", []),

    # Rec 3872: Cắt tiền tố nhân tạo -> Hồ Chí Minh
    ("Hồ Chí Minh chiều 24 / 10 vượt mức báo động 3 tới 17 cm , nhiều nơi trong Thành phố , nước dâng nhanh , ngập sâu .", [
        ([0, 1, 2], [23, 24], 'NEG'),
        ([0, 1, 2], [26, 27], 'NEG'),
    ]),

    # Rec 3873: Hồ Chí Minh, triều cường
    ("Hồ Chí Minh , triều cường khiến nước ngập dâng cao , mọi người di chuyển cẩn thận nhé !", [
        ([0, 1, 2], [8], 'NEG'),
        ([4, 5], [9, 10], 'NEG'),
    ]),

    # Rec 3874: Đoạn cắt cụt chung chung -> REJECT
    ("Nhiều nơi trong thành phố nước đã dâng nhanh , ngập sâu , và thậm chí ở cả những khu vực chưa từng ngập .", []),

    # Rec 3875: Làm sạch hashtag -> đường Cây Bàng, bờ Thủ Thiêm
    ("Nước lên ngập đường Cây Bàng bờ Thủ Thiêm , đầu hầm Sông Sài Gòn", [
        ([3, 4, 5], [2], 'NEG'),
        ([6, 7, 8], [2], 'NEG'),
    ]),
]

def test_triplets():
    print(f"Tổng số records kiểm tra trong Batch 39: {len(batch39_data)}")
    assert len(batch39_data) == 75, f"Batch 39 phải có đúng 75 records, hiện tại có {len(batch39_data)}"
    
    flaws = 0
    for idx, (text, triplets) in enumerate(batch39_data, start=3801):
        tokens = text.split()
        for asp_idx, op_idx, sent in triplets:
            try:
                asp_tokens = [tokens[i] for i in asp_idx]
                op_tokens = [tokens[i] for i in op_idx]
                asp_str = " ".join(asp_tokens)
                op_str = " ".join(op_tokens)
                
                # Check sentiment
                if sent not in ['POS', 'NEG', 'NEU']:
                    print(f"LỖI SENTIMENT Rec {idx}: {sent}")
                    flaws += 1
                    
                # Check punctuation at edges
                bad_puncts = [',', '.', '!', '?', ';', ':', '(', ')', '"', '“', '”', '…', '-', '–', '→', '•']
                if asp_tokens[0] in bad_puncts or asp_tokens[-1] in bad_puncts:
                    print(f"LỖI DẤU CÂU ASPECT Rec {idx}: \"{asp_str}\"")
                    flaws += 1
                if op_tokens[0] in bad_puncts or op_tokens[-1] in bad_puncts:
                    print(f"LỖI DẤU CÂU OPINION Rec {idx}: \"{op_str}\"")
                    flaws += 1
                    
                # Check prepositions
                bad_preps = ['ở', 'tại', 'trên', 'trong', 'tới', 'vào', 'bởi', 'do', 'đến', 'thuộc', 'gần', 'của', 'dọc']
                if asp_tokens[0].lower() in bad_preps:
                    print(f"LỖI GIỚI TỪ ĐẦU ASPECT Rec {idx}: \"{asp_str}\"")
                    flaws += 1
            except Exception as e:
                print(f"LỖI INDEX NGOÀI RANGE Rec {idx}: {e}")
                flaws += 1
    if flaws == 0:
        print("TẤT CẢ CÁC TRIPLETS CỦA BATCH 39 ĐỀU HỢP LỆ VÀ KHỚP TOKEN!")
    else:
        print(f"TỔNG CỘNG PHÁT HIỆN {flaws} LỖI!")
    return flaws

if __name__ == '__main__':
    flaws = test_triplets()
    if flaws == 0:
        phase3_path = 'data/validate_label/thuan/phase3.txt'
        with open(phase3_path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        base_lines = lines[:3800]
        
        new_batch_lines = []
        for text, triplets in batch39_data:
            trip_strs = []
            for a, o, s in triplets:
                trip_strs.append(f"({a}, {o}, '{s}')")
            formatted_trips = '[' + ', '.join(trip_strs) + ']'
            clean_text = text.rstrip("# "); new_batch_lines.append(f"{clean_text}####{formatted_trips}")
            
        full_lines = base_lines + new_batch_lines
        with open(phase3_path, 'w', encoding='utf-8') as f:
            for l in full_lines:
                f.write(l + '\n')
        print(f"Successfully updated {len(full_lines)} lines to {phase3_path}!")
