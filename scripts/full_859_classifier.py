# -*- coding: utf-8 -*-
import ast, re
from analyze_all_859 import parse_859

recs = parse_859()

# Bộ lọc địa danh ngoài nghiêm ngặt (OUT-OF-SCOPE)
out_provinces_regex = [
    # Quốc tế
    r'\b(thái lan|thailand|bangkok|trung quốc|china|philippines|manila|nhật bản|tokyo)\b',
    # Miền Bắc
    r'\b(hà nội|hanoi|hà đông|cầu giấy|thanh xuân|hoàng mai|ba đình|hoàn kiếm|hai bà trưng|đống đa|tây hồ|long biên|gia lâm|đông anh|chương mỹ|văn phú|tứ liên|ihanoi)\b',
    r'\b(hải phòng|quảng ninh|hạ long|thái nguyên|bắc giang|bắc ninh|vĩnh phúc|phú thọ|thái bình|nam định|hà nam|hưng yên|hải dương|ninh bình)\b',
    r'\b(thanh hóa|nông cống|nghệ an|hà tĩnh|quảng bình|quảng trị|thừa thiên huế|tp huế)\b',
    # Miền Trung & Tây Nguyên
    r'\b(đà nẵng|quảng nam|hội an|tam kỳ|quảng ngãi|bình định|quy nhơn|phú yên|tuy hòa|khánh hòa|nha trang|ninh thuận|phan rang|bình thuận|phan thiết)\b',
    r'\b(kon tum|gia lai|pleiku|đắk lắk|buôn ma thuột|đắk nông|lâm đồng|đà lạt|bảo lộc)\b',
    # Miền Tây & ĐBSCL
    r'\b(cần thơ|cantho|ninh kiều|bình thủy|cái răng|ô môn|thốt nốt)\b',
    r'\b(long an|tân an|tiền giang|mỹ tho|gò công|bến tre|trà vinh|vĩnh long|đồng tháp|cao lãnh|sa đéc|an giang|long xuyên|châu đốc|kiên giang|rạch giá|phú quốc|hậu giang|vị thanh|sóc trăng|bạc liêu|cà mau|đbscl|đồng bằng sông cửu long|phụng hiệp|mỹ thuận)\b',
    # Đồng Nai & các huyện Đồng Nai
    r'\b(đồng nai|biên hòa|long khánh|mẹ bồng con|vĩnh thanh|dầu giây|trảng bom|định quán|tân phú đồng nai)\b',
    r'\b(tây ninh|bình phước|đồng xoài|chơn thành)\b'
]

# Quảng cáo thương mại & Dịch vụ ngoài lề
commercial_regex = [
    r'\b(otochutin|toantrung|thu mua xe|định giá xe|bán xe cũ|bán xe ngập|showroom ô tô)\b',
    r'\b(cửa chống ngập|bạt chắn nước|bạt chống ngập|tấm chắn nước)\b',
    r'\b(cho thuê phòng|phòng trọ|bán nhà|bán đất|bds|bất động sản|môi giới|chốt cọc)\b',
    r'\b(buffet|sushi|trà sữa|ẩm thực hải sản|chậu nhựa|chậu sành|chậu đất nung)\b',
    r'\b(ms hoa junior|học tiếng anh|lớp tiếng anh)\b'
]

# Meme / Phim hoạt hình / Giải trí thuần túy / Mẹo kỹ thuật xe
meme_tech_regex = [
    r'\b(thucung|thú cưng|chó cưng|mèo cưng|cún cưng)\b',
    r'\b(vùng đất linh hồn|anime|ghibli)\b',
    r'\b(hát live|trailer mv|mv ca nhạc|bài hát mới|album mới)\b',
    r'\b(quy trình xử lý khi xe bị ngập|thủy kích là gì|kỹ thuật chống thủy kích|bảo dưỡng xe)\b'
]

# Danh từ địa danh TP.HCM / Bình Dương / Vũng Tàu hợp lệ
valid_hcm_bd_vt = [
    'sài gòn', 'saigon', 'tphcm', 'tp. hcm', 'tp hcm', 'tp. hồ chí minh', 'thành phố hồ chí minh', 'hồ chí minh',
    'thủ đức', 'gò vấp', 'bình thạnh', 'tân bình', 'bình tân', 'quận 1', 'quận 2', 'quận 3', 'quận 4', 'quận 5',
    'quận 6', 'quận 7', 'quận 8', 'quận 9', 'quận 10', 'quận 11', 'quận 12', 'hóc môn', 'bình chánh', 'nhà bè',
    'củ chi', 'cần giờ', 'phú nhuận', 'tân phú',
    # Bình Dương
    'bình dương', 'thủ dầu một', 'thuận an', 'dĩ an', 'bến cát', 'tân uyên', 'bàu bàng', 'lái thiêu',
    'an phú', 'thuận giao', 'mỹ phước', 'đt743', 'đt744', 'đt748', 'kcn vsip', 'vsip',
    # Vũng Tàu
    'vũng tàu', 'bà rịa', 'bà rịa - vũng tàu', 'brvt', 'long điền', 'đất đỏ', 'thùy vân', 'bãi sau', 'bãi trước',
    'bến đình', 'thi sách'
]

hard_rejects = []
recover_candidates = []

for r in recs:
    text = r['p3_text']
    text_lower = text.lower()
    
    # 1. Kiểm tra Truly Out-of-scope
    out_matched = []
    for reg in out_provinces_regex:
        m = re.findall(reg, text_lower)
        if m:
            out_matched.extend(m)
            
    # Kiểm tra ngoại lệ (Ví dụ nhắc PouYuen Bình Tân, hoặc có đường SG mà hashtag quê quán)
    is_hard_out = False
    if out_matched:
        # Nếu có địa danh hợp lệ mạnh tại HCM/BD/VT
        has_strong_local = any(loc in text_lower for loc in [
            'trần xuân soạn', 'huỳnh tấn phát', 'lê văn lương', 'nguyễn văn hưởng', 'quốc lộ 13', 'ql13',
            'võ văn ngân', 'đặng thị rành', 'tô ngọc vân', 'phan huy ích', 'ung văn khiêm', 'thảo điền',
            'pouyuen', 'bến cát', 'thủ dầu một', 'thuận an', 'dĩ an', 'vũng tàu'
        ])
        if has_strong_local and all(x in ['bến tre', 'tiền giang', 'nghệ an', 'quảng nam', 'thanh hóa'] for x in out_matched):
            # Giữ lại vì là địa danh SG thực tế
            pass
        else:
            is_hard_out = True
            hard_rejects.append((r, 'OUT_OF_SCOPE', out_matched))
            continue
            
    # 2. Kiểm tra Commercial
    comm_matched = []
    for reg in commercial_regex:
        m = re.findall(reg, text_lower)
        if m:
            comm_matched.extend(m)
    if comm_matched:
        hard_rejects.append((r, 'COMMERCIAL', comm_matched))
        continue
        
    # 3. Kiểm tra Meme / Tech
    meme_matched = []
    for reg in meme_tech_regex:
        m = re.findall(reg, text_lower)
        if m:
            meme_matched.extend(m)
    if meme_matched:
        hard_rejects.append((r, 'MEME_OR_TECH', meme_matched))
        continue
        
    # 4. Kiểm tra độ dài câu
    if len(text.split()) < 5:
        hard_rejects.append((r, 'TOO_SHORT', len(text.split())))
        continue
        
    recover_candidates.append(r)

print(f"=== KẾT QUẢ PHÂN TÍCH TOÀN DIỆN 859 RECORDS REJECT ===")
print(f"Tổng số: 859 records")
print(f"  - Hard REJECT (loại bỏ chắc chắn theo quy tắc): {len(hard_rejects)}")
print(f"  - Phục hồi tiềm năng (IN-SCOPE cần rà soát & gán nhãn): {len(recover_candidates)}")

# Lưu kết quả ra file
with open('scratch_hard_rejects.txt', 'w', encoding='utf-8') as f:
    for r, reason, detail in hard_rejects:
        f.write(f"REC {r['rec_id']} | Reason: {reason} | Detail: {detail}\n  Text: {r['p3_text']}\n\n")

with open('scratch_recover_candidates.txt', 'w', encoding='utf-8') as f:
    for r in recover_candidates:
        f.write(f"REC {r['rec_id']} | P3: {r['p3_text']} | MA_TRIP: {r['master_triplets']}\n\n")

print("Đã lưu scratch_hard_rejects.txt và scratch_recover_candidates.txt")
