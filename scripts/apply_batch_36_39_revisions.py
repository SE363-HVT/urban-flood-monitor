# -*- coding: utf-8 -*-
from span_helper import make_triplet
import json

batch_36_39_revisions = [
    # REC 3647: rạch Cầu Ngang chống ngập
    (3647, "Các dự án chống ngập gần hoàn thiện gồm : dự án xây hệ thống thoát nước dọc đường ray xe lửa ( hoàn thành tháng 7 . 2025 ) ; dự án cải tạo rạch Cầu Ngang ( hoàn thành tháng 7 . 2025 ) .",
     [("rạch Cầu Ngang", "chống ngập", "POS")]),

    # REC 3649: TP. Hồ Chí Minh chết máy
    (3649, "Tại TP. Hồ Chí Minh , “ Con cháu mà đi học là nó hay bị chết máy rồi té xe ngã xe đồ , sụp vào cống thì cũng rất là nguy hiểm . ”",
     [("TP. Hồ Chí Minh", "chết máy", "NEG")]),

    # REC 3650: TP. Hồ Chí Minh ngập
    (3650, "Tại TP. Hồ Chí Minh , “ Đường thì nhỏ mà nước nó lên ngập như thế này thì quá khủng khiếp ”",
     [("TP. Hồ Chí Minh", "ngập", "NEG")]),

    # REC 3651: TP. Hồ Chí Minh ngăn triều
    (3651, "Tại TP. Hồ Chí Minh , Khi hoàn thành , hệ thống này sẽ như một tấm lá chắn khổng lồ , ngăn triều từ các con sông lớn tràn vào nội đô , bảo vệ diện tích 570km² với khoảng 6 , 5 triệu dân .",
     [("TP. Hồ Chí Minh", "ngăn triều", "POS")]),

    # REC 3653: thành phố giảm ngập
    (3653, "Tại TP. Hồ Chí Minh , Mực nước ngoài sông lớn có thể cao nhưng trong kênh rạch của mình ở mức thấp , lúc này chúng như những cái hồ chứa nước , nước sẽ rút nhanh từ đó làm giảm ngập cho thành phố . ”",
     [("thành phố", "giảm ngập", "POS")]),

    # REC 3654: TP. HCM chống ngập
    (3654, "Giờ đây , với sự vào cuộc quyết liệt của Chính phủ và TP. HCM , hy vọng về một ngày công trình chống ngập 10 . 000 tỷ đồng về đích đang lớn hơn bao giờ hết .",
     [("TP. HCM", "chống ngập", "POS")]),

    # REC 3656: TP. Hồ Chí Minh mưa ngập
    (3656, "Tại TP. Hồ Chí Minh , “ Tôi mong các ngành chức năng sớm có biện pháp khắc phục chứ mưa ngập từ năm này sang năm khác , rất khổ ” , ông Mạnh nói .",
     [("TP. Hồ Chí Minh", "mưa ngập", "NEG")]),

    # REC 3659: TP. HCM giảm ngập
    (3659, "Để giảm ngập trước mắt , Sở Xây dựng TP. HCM yêu cầu đơn vị thuộc thẩm quyền nhanh chóng nạo vét các tuyến cống , cửa xả , kênh rạch bị bồi lắng , đặc biệt ưu tiên các nơi thường xuyên bị ngập và sửa chữa cống bị tắc nghẽn . . .",
     [("TP. HCM", "giảm ngập", "POS")]),

    # REC 3666: TP. Hồ Chí Minh sẽ ngập
    (3666, "Tại TP. Hồ Chí Minh , \" Tôi ở đây cả mấy chục năm rồi , khu vực này cứ mưa là sẽ ngập .",
     [("TP. Hồ Chí Minh", "sẽ ngập", "NEG")]),

    # REC 3667: TP. Hồ Chí Minh xe chết máy, nước rút
    (3667, "Tại TP. Hồ Chí Minh , \" Tôi chở hàng ở trong hẻm ra thì không may xe chết máy , bây giờ phải đợi nước rút mới kiểm tra được \" , tài xế xe tải chia sẻ .",
     [("TP. Hồ Chí Minh", "xe chết máy", "NEG"),
      ("TP. Hồ Chí Minh", "nước rút", "POS")]),

    # REC 3670: TP. Hồ Chí Minh nước vẫn tràn vào nhà
    (3670, "Tại TP. Hồ Chí Minh , Mặc dù bà đã dùng tấm gỗ che lại nhưng vẫn \" không ăn thua \" , nước vẫn tràn vào nhà .",
     [("TP. Hồ Chí Minh", "nước vẫn tràn vào nhà", "NEG")]),

    # REC 3671: hồ Gò Dưa kế hoạch chống ngập
    (3671, "Thực tế , TP HCM từng đặt mục tiêu xây bảy hồ điều tiết ( một hồ hở , sáu hồ ngầm ) thuộc kế hoạch chống ngập từ năm 2021 , trong đó dự án hồ Gò Dưa rộng 20 ha tại Thủ Đức với tổng vốn hơn 1 . 000 tỷ đồng .",
     [("hồ Gò Dưa", "kế hoạch chống ngập", "POS")]),

    # REC 3673: TP. Hồ Chí Minh chết máy
    (3673, "Tại TP. Hồ Chí Minh , “ Nhiều phương tiện bị chết máy phải đẩy bộ về nhà ” , ông Thành , ngụ tại con hẻm trên nói .",
     [("TP. Hồ Chí Minh", "chết máy", "NEG")]),

    # REC 3674: TP. Hồ Chí Minh không có ngập
    (3674, "Tại TP. Hồ Chí Minh , \" Mong cải thiện , đường được nâng lên cho người dân đi được thoải mái , không có ngập \"",
     [("TP. Hồ Chí Minh", "không có ngập", "POS")]),

    # REC 3677: Thủ Đức thoát cảnh bì bõm
    (3677, "Thủ Đức đã phê duyệt dự án nâng cấp đường và hệ thống thoát nước , giúp người dân thoát cảnh bì bõm mỗi khi trời mưa .",
     [("Thủ Đức", "thoát cảnh bì bõm", "POS")]),

    # REC 3684: TP. Hồ Chí Minh nước ngập
    (3684, "Tại TP. Hồ Chí Minh , “ Mỗi lần nước ngập là tôi và vợ phải bỏ hết công việc buôn bán để dựng ván che chắn , hôm nay mưa lớn khiến nước tràn vào , chúng tôi phải liên tục tát nước gần cả tiếng đồng hồ .",
     [("TP. Hồ Chí Minh", "nước ngập", "NEG")]),

    # REC 3694: TP. HCM chống ngập do triều cường
    (3694, "Trong cuộc họp báo kinh tế - xã hội định kỳ do Sở VH - TT cùng Ban Tuyên giáo và Dân vận Thành ủy TP. HCM tổ chức chiều 30 . 10 , đại diện Sở Xây dựng thông tin về các dự án chống ngập do triều cường trên địa bàn .",
     [("TP. HCM", "chống ngập do triều cường", "POS")]),

    # REC 3696: Gò Vấp, Thảo Điền, chợ Thủ Đức giải quyết ngập
    (3696, "\" Một số dự án giải quyết ngập trên địa bàn Gò Vấp , Thảo Điền - Quốc Hương và chợ Thủ Đức đang và sẽ triển khai cũng sẽ góp phần giảm ngập cho các khu vực \" nóng \" hiện nay trên địa bàn \" , ông Hoàng Phúc Dũng nói .",
     [("Gò Vấp", "giải quyết ngập", "POS"),
      ("Thảo Điền", "giải quyết ngập", "POS"),
      ("chợ Thủ Đức", "giải quyết ngập", "POS")]),

    # REC 3813: NHÀ BÈ NGẬP TRIỀU RẤT NẶNG
    (3813, "📍 NHÀ BÈ – NGẬP TRIỀU RẤT NẶNG",
     [("NHÀ BÈ", "NGẬP TRIỀU RẤT NẶNG", "NEG")]),

    # REC 3814: khu Nam Ngập triều sâu nhất
    (3814, "→ Ngập triều sâu nhất khu Nam .",
     [("khu Nam", "Ngập triều sâu nhất", "NEG")]),

    # REC 3817: rạch Nhà Bè Ngập do triều
    (3817, "→ Ngập do triều từ rạch Nhà Bè dâng .",
     [("rạch Nhà Bè", "Ngập do triều", "NEG")]),

    # REC 3820: TP. Hồ Chí Minh ngập úng
    (3820, "Tại TP. Hồ Chí Minh , Vì khả năng mưa giai đoạn tới vẫn còn lớn khi kết hợp xả lũ do thượng lưu vẫn đang cao khi dồn về hạ du thì tình trạng ngập úng sẽ tăng cao vào buổi chiều tối đến rạng sáng .",
     [("TP. Hồ Chí Minh", "ngập úng", "NEU")]),

    # REC 3821: TP. Hồ Chí Minh dễ ngập
    (3821, "Tại TP. Hồ Chí Minh , Nhiều tuyến đường dễ ngập người dân nên lưu ý ! # TVPL # ThuVienPhapLuat # LearnOnTikTok # Hoccungtiktok",
     [("TP. Hồ Chí Minh", "dễ ngập", "NEU")]),

    # REC 3825: thuduc ngập mún đến nóc
    (3825, "Các bạn xem cuối video m quay chiếc oto để dưới lòng đường kìa , nó ngập mún đến nóc chiếc xe luôn # muangaplut # ngaplut # thuduc",
     [("thuduc", "ngập mún đến nóc", "NEG")]),

    # REC 3831: TP. Hồ Chí Minh giảm ngập lụt
    (3831, "Tại TP. Hồ Chí Minh , Các thanh niên trẻ tình nguyện dọn dẹp miệng cống để giảm ngập lụt trên đường phố ❤ ️ ❤ ️ ❤ ️",
     [("TP. Hồ Chí Minh", "giảm ngập lụt", "POS")]),

    # REC 3835: TP. Hồ Chí Minh rút chậm
    (3835, "Tại TP. Hồ Chí Minh , Đến 20h , nước tại các tuyến đường trung tâm rút chậm .",
     [("TP. Hồ Chí Minh", "rút chậm", "NEG")]),

    # REC 3836: tp HCM ngập sâu
    (3836, "# Lan167 # Triều cường tp HCM ngập sâu do mực nước dâng cao kỷ lục # xuhuongtiktok2025 ❤ ️ 💕 🇻 🇳 🌹",
     [("tp HCM", "ngập sâu", "NEG")]),

    # REC 3842: TP. Hồ Chí Minh ngập lụt
    (3842, "Tại TP. Hồ Chí Minh , Người đàn ông tình nguyện dọn miệng cống thoát nước khi đang ngập lụt đường phố ❤ ️ ❤ ️ ❤ ️",
     [("TP. Hồ Chí Minh", "ngập lụt", "NEG")]),

    # REC 3843: cống ngăn triều khỏi ngập do triều
    (3843, "Với tổng vốn đầu tư 10 . 000 tỷ đồng , dự án cống ngăn triều được kỳ vọng hoàn thành năm 2018 để bảo vệ 6 , 5 triệu dân thuộc khu vực bờ hữu khỏi ngập do triều và biến đổi khí hậu .",
     [("cống ngăn triều", "khỏi ngập do triều", "POS")]),

    # REC 3844: quận 7 ngập lụt diễn ra ngày càng nặng nề
    (3844, "Nhưng sau nhiều năm , công trình vẫn đình trệ , còn ngập lụt diễn ra ngày càng nặng nề , đặc biệt ở khu vực quận 7 cũ .",
     [("quận 7", "ngập lụt diễn ra ngày càng nặng nề", "NEG")]),

    # REC 3845: cống Phú Định thoát nước
    (3845, "Sống cạnh công trường cống Phú Định , ông Nguyễn Văn Tiệm ( 70 tuổi ) cho biết : \" Công trình bỏ hoang mấy năm nay , chúng tôi chỉ mong dự án sớm khởi động lại và có giải pháp thoát nước để không còn chịu cảnh sống chung với ngập \" .",
     [("cống Phú Định", "thoát nước", "POS")]),

    # REC 3858: Sài gòn sắp ngập lụt
    (3858, "Tin nóng ngày 06 / 11 / 2025 , Sài gòn có nguy cơ sắp ngập lụt nhiều khu vực . . . bà con mình cẩn thận . . .",
     [("Sài gòn", "sắp ngập lụt", "NEU")]),

    # REC 3859: TP. Hồ Chí Minh biển nước
    (3859, "Tại TP. Hồ Chí Minh , Người dân thức trắng đêm giữa biển nước .",
     [("TP. Hồ Chí Minh", "biển nước", "NEG")]),

    # REC 3861: TP. Hồ Chí Minh nước ngập khắp nhà
    (3861, "Tại TP. Hồ Chí Minh , Tối hôm qua mưa lớn quá nước ngập khắp nhà , tui con phụ mẹ tát nước mệt mún chít lun , giờ tụi con nhủ bù lấy sức đây . . .",
     [("TP. Hồ Chí Minh", "nước ngập khắp nhà", "NEG")]),

    # REC 3862: Sì Gòn ngập nữa
    (3862, "bít đâu tối nay Sì Gòn ngập nữa . . . .",
     [("Sì Gòn", "ngập nữa", "NEU")]),

    # REC 3865: Quận 7 ngập như sông
    (3865, "Lâu lâu ghé qua Quận 7 mà ngập như sông luôn 😭 🌊",
     [("Quận 7", "ngập như sông", "NEG")]),

    # REC 3867: sàigòn ngập cả đường lớn
    (3867, "Mưa to ngập cả đường lớn # sàigòn # mùam # ngập_hết_đường",
     [("sàigòn", "ngập cả đường lớn", "NEG")]),

    # REC 3871: TP. Hồ Chí Minh ngập sâu
    (3871, "Tại TP. Hồ Chí Minh , • Nhiều tuyến đường bị ngập sâu chỉ trong khoảng 30 phút , khiến giao thông bị tê liệt : xe chết máy , người dân phải dắt bộ hoặc tìm đường khác .",
     [("TP. Hồ Chí Minh", "ngập sâu", "NEG")]),

    # REC 3874: thành phố ngập sâu
    (3874, "Nhiều nơi trong thành phố nước đã dâng nhanh , ngập sâu , và thậm chí ở cả những khu vực chưa từng ngập .",
     [("thành phố", "ngập sâu", "NEG")])
]

def apply_revisions():
    with open('data/validate_label/thuan/phase3.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    print(f"Loaded {len(lines)} lines from phase3.txt")

    for rec_id, text, trips in batch_36_39_revisions:
        idx = rec_id - 1
        generated_triplets = []
        for asp_phrase, opi_phrase, pol in trips:
            t = make_triplet(text, asp_phrase, opi_phrase, pol)
            if t is None:
                print(f"ERROR: Cannot create triplet for REC {rec_id}: {asp_phrase} | {opi_phrase}")
                return False
            generated_triplets.append(t)
            
        new_line = f"{text}####{json.dumps(generated_triplets)}"
        lines[idx] = new_line
        print(f"Updated REC {rec_id}: {len(generated_triplets)} triplets")

    with open('data/validate_label/thuan/phase3.txt', 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

    print("Successfully wrote updates to phase3.txt")
    return True

if __name__ == '__main__':
    apply_revisions()
