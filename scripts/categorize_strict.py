# -*- coding: utf-8 -*-
import ast, re
from analyze_all_859 import parse_859

recs = parse_859()

# Danh sách từ khóa OUT-OF-SCOPE thực sự (Địa danh ngoài vùng HCM + BD + BRVT)
strict_out_provinces = [
    # Nước ngoài
    'bangkok', 'thái lan', 'thailand', 'trung quốc', 'china', 'philippines', 'manila', 'nhật bản',
    # Miền Bắc
    'hà nội', 'hanoi', 'hà đông', 'cầu giấy', 'nam từ liêm', 'bắc từ liêm', 'thanh xuân', 'hoàng mai',
    'ba đình', 'hoàn kiếm', 'hai bà trưng', 'đống đa', 'tây hồ', 'long biên', 'gia lâm', 'đông anh',
    'sóc sơn', 'chương mỹ', 'quốc oai', 'thạch thất', 'mê linh', 'văn phú', 'tứ liên', 'ihanoi',
    'hải phòng', 'quảng ninh', 'hạ long', 'thái nguyên', 'bắc giang', 'bắc ninh', 'vĩnh phúc',
    'phú thọ', 'thái bình', 'nam định', 'hà nam', 'hưng yên', 'hải dương', 'ninh bình',
    'thanh hóa', 'nông cống', 'nghệ an', 'tp vinh', 'hà tĩnh', 'quảng bình', 'quảng trị', 'thừa thiên huế', 'tp huế',
    # Miền Trung & Tây Nguyên
    'đà nẵng', 'quảng nam', 'hội an', 'tam kỳ', 'quảng ngãi', 'bình định', 'quy nhơn', 'phú yên', 'tuy hòa',
    'khánh hòa', 'nha trang', 'ninh thuận', 'phan rang', 'bình thuận', 'phan thiết',
    'kon tum', 'gia lai', 'pleiku', 'đắk lắk', 'buôn ma thuột', 'đắk nông', 'lâm đồng', 'đà lạt', 'bảo lộc',
    # Đồng Nai & lân cận ngoài scope
    'đồng nai', 'biên hòa', 'long khánh', 'mẹ bồng con', 'vĩnh thanh', 'dầu giây', 'trảng bom', 'định quán',
    'tây ninh', 'bình phước', 'đồng xoài', 'chơn thành',
    # Miền Tây / ĐBSCL
    'cần thơ', 'cantho', 'ninh kiều', 'bình thủy', 'cái răng', 'ô môn', 'thốt nốt',
    'long an', 'tân an', 'bến lức', 'tiền giang', 'mỹ tho', 'gò công', 'bến tre', 'trà vinh', 'vĩnh long',
    'đồng tháp', 'cao lãnh', 'sa đéc', 'an giang', 'long xuyên', 'châu đốc', 'kiên giang', 'rạch giá', 'phú quốc',
    'hậu giang', 'vị thanh', 'sóc trăng', 'bạc liêu', 'cà mau'
]

strict_commercial = [
    'otochutin', 'toantrung', 'bán xe', 'mua xe', 'thu mua xe', 'định giá xe', 'showroom',
    'cửa chống ngập', 'bạt chắn nước', 'bạt chống ngập', 'bán nhà', 'cho thuê phòng',
    'môi giới', 'bất động sản', 'trà sữa', 'ẩm thực', 'buffet', 'sushi'
]

strict_meme_tech = [
    'thucung', 'thú cưng', 'chó cưng', 'mèo cưng', 'cún cưng', 'vùng đất linh hồn', 'anime',
    'bảo dưỡng xe', 'quy trình xử lý khi xe bị ngập', 'thủy kích là gì', 'cách chống thủy kích'
]

# Kiểm tra từng record
confirmed_reject = []
potential_inscope = []

for r in recs:
    text_lower = (r['p3_text'] + ' ' + r['master_text']).lower()
    
    # 1. Kiểm tra địa danh ngoài
    found_out = []
    for p in strict_out_provinces:
        # Regex tìm từ nguyên vẹn
        pattern = r'(?<![a-zà-ỹ0-9_])' + re.escape(p) + r'(?![a-zà-ỹ0-9_])'
        if re.search(pattern, text_lower):
            found_out.append(p)
            
    # Kiểm tra xem có phải hashtag quê quán nhưng nội dung ở SG/BD/VT không
    # Ví dụ: PouYuen, hoặc có nhắc đường cụ thể ở TPHCM
    is_out = False
    if found_out:
        has_sg_street = any(st in text_lower for st in [
            'trần xuân soạn', 'nguyễn văn hưởng', 'huỳnh tấn phát', 'lê văn lương', 'quốc lộ 13', 'ql13',
            'võ văn ngân', 'đặng thị rành', 'tô ngọc vân', 'phần huy ích', 'phan huy ích', 'nguyễn xí',
            'thảo điền', 'phú mỹ hưng', 'bình thạnh', 'gò vấp', 'thủ đức', 'tân bình', 'bình tân', 'quận 7',
            'quận 8', 'quận 12', 'quận 2', 'quận 9', 'hóc môn', 'bình chánh', 'nhà bè', 'pouyuen', 'bến cát',
            'thuận an', 'dĩ an', 'thủ dầu một', 'tân uyên', 'bà rịa', 'vũng tàu'
        ])
        if has_sg_street and any(x in found_out for x in ['bến tre', 'tiền giang', 'nghệ an', 'quảng nam', 'thanh hóa', 'cần thơ', 'long an']):
            # Ưu tiên local street!
            is_out = False
        else:
            is_out = True
            confirmed_reject.append((r, 'OUT_OF_SCOPE_PROVINCE', found_out))
            continue

    # 2. Kiểm tra quảng cáo thương mại
    found_comm = [c for c in strict_commercial if c in text_lower]
    if found_comm:
        # Kiểm tra xem có phải nội dung ngập thực tế mà tình cờ dính chữ không
        # Ví dụ: "bán nhà" có thể là tin BĐS thuần túy
        confirmed_reject.append((r, 'COMMERCIAL', found_comm))
        continue
        
    # 3. Meme / Tech advice
    found_meme = [m for m in strict_meme_tech if m in text_lower]
    if found_meme:
        confirmed_reject.append((r, 'MEME_OR_TECH_ADVICE', found_meme))
        continue

    # 4. Kiểm tra câu quá ngắn / cụt ngủn
    words = r['p3_text'].split()
    if len(words) < 5:
        confirmed_reject.append((r, 'TOO_SHORT_OR_FRAGMENT', len(words)))
        continue
        
    potential_inscope.append(r)

print(f"Tổng số 859 records:")
print(f"  - Confirmed REJECT: {len(confirmed_reject)}")
print(f"  - Potential IN-SCOPE (cần phục hồi & gán nhãn): {len(potential_inscope)}")

# Thống kê chi tiết Confirmed REJECT
reason_counts = {}
for _, reason, _ in confirmed_reject:
    reason_counts[reason] = reason_counts.get(reason, 0) + 1
print(f"Phân loại Confirmed REJECT: {reason_counts}")
