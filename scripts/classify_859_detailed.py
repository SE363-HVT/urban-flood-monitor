# -*- coding: utf-8 -*-
import ast, re
from analyze_all_859 import parse_859

recs = parse_859()

# 1. Các từ khóa địa phương OUT-OF-SCOPE thực sự
truly_out_keywords = [
    # Hà Nội & Miền Bắc
    'hà nội', 'hanoi', 'hà đông', 'cầu giấy', 'nam từ liêm', 'bắc từ liêm', 'thanh xuân', 'hoàng mai',
    'ba đình', 'hoàn kiếm', 'hai bà trưng', 'đống đa', 'tây hồ', 'long biên', 'gia lâm', 'đông anh',
    'sóc sơn', 'chương mỹ', 'quốc oai', 'thạch thất', 'mê linh', 'văn phú', 'tứ liên', 'ihanoi',
    'hải phòng', 'quảng ninh', 'hạ long', 'thái nguyên', 'bắc giang', 'bắc ninh', 'vĩnh phúc',
    'phú thọ', 'thái bình', 'nam định', 'hà nam', 'hưng yên', 'hải dương', 'ninh bình',
    'thanh hóa', 'nông cống', 'nghệ an', 'vinh', 'hà tĩnh', 'quảng bình', 'quảng trị', 'huế',
    # Miền Trung & Tây Nguyên
    'đà nẵng', 'quảng nam', 'hội an', 'quảng ngãi', 'bình định', 'quy nhơn', 'phú yên', 'tuy hòa',
    'khánh hòa', 'nha trang', 'ninh thuận', 'phan rang', 'bình thuận', 'phan thiết',
    'kon tum', 'gia lai', 'pleiku', 'đắk lắk', 'buôn ma thuột', 'đắk nông', 'lâm đồng', 'đà lạt', 'bảo lộc',
    # Đồng Nai & Bình Phước & Tây Ninh
    'đồng nai', 'biên hòa', 'long khánh', 'mẹ bồng con', 'vĩnh thanh', 'dầu giây', 'trảng bom',
    'tây ninh', 'bình phước', 'đồng xoài',
    # Miền Tây / ĐBSCL
    'cần thơ', 'cantho', 'ninh kiều', 'bình thủy', 'cái răng', 'ô môn', 'thốt nốt',
    'long an', 'tân an', 'tiền giang', 'mỹ tho', 'bến tre', 'trà vinh', 'vĩnh long',
    'đồng tháp', 'cao lãnh', 'sa đéc', 'an giang', 'long xuyên', 'châu đốc', 'kiên giang', 'rạch giá', 'phú quốc',
    'hậu giang', 'vị thanh', 'sóc trăng', 'bạc liêu', 'cà mau',
    # Nước ngoài
    'thái lan', 'thailand', 'bangkok', 'trung quốc', 'china', 'philippines', 'manila', 'nhật bản', 'tokyo'
]

# 2. Quảng cáo thương mại & Phi ngập lụt
commercial_keywords = [
    'otochutin', 'toantrung', 'bán xe', 'mua xe', 'thu mua xe', 'định giá xe', 'showroom',
    'cửa chống ngập', 'bạt chắn nước', 'bạt chống ngập', 'bán nhà', 'cho thuê phòng',
    'môi giới', 'bất động sản', 'trà sữa', 'ẩm thực', 'buffet', 'sushi'
]

# 3. Meme / Thú cưng / Anime / Kỹ thuật xe
meme_keywords = [
    'thucung', 'thú cưng', 'chó cưng', 'mèo cưng', 'cún cưng', 'vùng đất linh hồn', 'anime',
    'bảo dưỡng xe', 'quy trình xử lý khi xe bị ngập', 'thủy kích là gì', 'cách chống thủy kích'
]

# Phân loại
out_of_scope_recs = []
commercial_recs = []
meme_recs = []
candidate_recs = []

for r in recs:
    text_lower = (r['p3_text'] + ' ' + r['master_text']).lower()
    
    # Kiểm tra Truly out
    matched_out = [kw for kw in truly_out_keywords if kw in text_lower]
    # Ngoại lệ: Nếu có PouYuen / Bình Dương / Vũng Tàu / Sài Gòn / TPHCM mà chỉ có hashtag quê quán
    is_out = False
    if matched_out:
        # Kiểm tra xem có phải hashtag quê quán nhưng nội dung ở SG/BD/VT không
        has_local = any(loc in text_lower for loc in ['sài gòn', 'saigon', 'tphcm', 'tp.hcm', 'bình dương', 'vũng tàu', 'thủ đức', 'gò vấp', 'bình thạnh', 'tân bình', 'bình tân', 'quận ', 'q.', 'hóc môn', 'bình chánh', 'nhà bè', 'phú nhuận'])
        # Nếu có local nhưng matched_out là gì?
        if has_local and any(kw in matched_out for kw in ['bến tre', 'tiền giang', 'nghệ an', 'thanh hóa', 'quảng nam']):
            # Cần xem xét kỹ, có thể là hashtag người dùng
            pass
        else:
            is_out = True
            out_of_scope_recs.append((r, matched_out))
            continue
            
    # Kiểm tra Commercial
    matched_comm = [kw for kw in commercial_keywords if kw in text_lower]
    if matched_comm:
        commercial_recs.append((r, matched_comm))
        continue
        
    # Kiểm tra Meme / Tech
    matched_meme = [kw for kw in meme_keywords if kw in text_lower]
    if matched_meme:
        meme_recs.append((r, matched_meme))
        continue
        
    candidate_recs.append(r)

print(f"Total rejected records: {len(recs)}")
print(f"Truly out-of-scope records: {len(out_of_scope_recs)}")
print(f"Commercial records: {len(commercial_recs)}")
print(f"Meme/Tech advice records: {len(meme_recs)}")
print(f"Potential candidates for RECOVERY: {len(candidate_recs)}")
