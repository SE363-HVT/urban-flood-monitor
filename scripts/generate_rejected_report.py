import ast
import re

# Load master lines 501 to 2500 (indices 500 to 2499)
with open('data/processed/aste_v2_format/master_10k_triplets.txt', 'r', encoding='utf-8') as f:
    master_lines = [f.readline().strip() for _ in range(2500)][500:2500]

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    phase2_lines = [line.strip() for line in f]

provinces = [
    'hà nội', 'hải phòng', 'đà nẵng', 'cần thơ', 'bình dương', 'đồng nai', 'long an', 
    'tiền giang', 'bến tre', 'trà vinh', 'vĩnh long', 'đồng tháp', 'an giang', 'kiên giang', 
    'cà mau', 'bạc liêu', 'sóc trăng', 'hậu giang', 'bà rịa', 'vũng tàu', 'bình phước', 
    'tây ninh', 'bình thuận', 'ninh thuận', 'khánh hòa', 'nha trang', 'phú yên', 'bình định', 
    'quảng ngãi', 'quảng nam', 'thừa thiên', 'huế', 'quảng trị', 'quảng bình', 'hà tĩnh', 
    'nghệ an', 'thanh hóa', 'nam định', 'thái bình', 'hải dương', 'hưng yên', 'bắc ninh', 
    'bắc giang', 'vĩnh phúc', 'phú thọ', 'thái nguyên', 'tuyên quang', 'hà giang', 'cao bằng', 
    'bắc kạn', 'lạng sơn', 'lào cai', 'yên bái', 'sơn la', 'hòa bình', 'điện biên', 'lai châu', 
    'kon tum', 'gia lai', 'đắk lắk', 'đắk nông', 'lâm đồng', 'đà lạt', 'buôn ma thuột'
]
provinces_regex = re.compile(r'\b(' + '|'.join([re.escape(p) for p in provinces]) + r')\b', re.IGNORECASE)

rejected_entries = []

for idx, (p2_line, ms_line) in enumerate(zip(phase2_lines, master_lines)):
    rec_in_phase2 = idx + 1
    rec_in_master = idx + 501
    
    p2_tokens, p2_trip_str = p2_line.split('####')
    ms_tokens, ms_trip_str = ms_line.split('####')
    
    p2_triplets = ast.literal_eval(p2_trip_str)
    ms_triplets = ast.literal_eval(ms_trip_str)
    
    if len(p2_triplets) == 0:
        # Determine rejection reason
        reasons = []
        text_lower = p2_tokens.lower()
        
        # Check out of scope province
        m = provinces_regex.findall(p2_tokens)
        matched_provinces = [
            p for p in m 
            if not (p.lower() == 'hà nội' and 'xa lộ hà nội' in text_lower)
            and not (p.lower() == 'hậu giang' and ('sân bay' in text_lower or 'quận 6' in text_lower or 'đường hậu giang' in text_lower))
        ]
        if matched_provinces:
            reasons.append(f"Tỉnh ngoài phạm vi ({', '.join(set(matched_provinces))})")
            
        if any(kw in text_lower for kw in ['quảng cáo', 'bán đất', 'bất động sản', 'liên hệ', 'inbox', 'giá chỉ', 'bán nhà', 'honda', 'xe mới']):
            reasons.append("Tin thương mại/Quảng cáo/Bán hàng")
            
        if any(kw in text_lower for kw in ['hội thảo', 'nghiên cứu', 'luận án', 'khoa học', 'hội nghị', 'tọa đàm']):
            reasons.append("Hội thảo/Văn bản hành chính không phải tin cứu hộ ngập lụt hiện trường")
            
        if not reasons:
            if not ms_triplets:
                reasons.append("Mẫu vốn là rác/rỗng từ Master")
            else:
                reasons.append("Không chứa địa danh/tên đường cụ thể hoặc gán sai bản chất (xe cộ, con người, cảm thán câu like)")
                
        reason_str = " | ".join(reasons)
        rejected_entries.append({
            'phase2_id': rec_in_phase2,
            'master_id': rec_in_master,
            'tokens': p2_tokens,
            'master_triplets': ms_trip_str,
            'reason': reason_str
        })

output_path = 'data/validate_label/thuan/phase2_rejected_records.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(f"================================================================================\n")
    f.write(f"TỔNG HỢP CÁC CÂU BỊ LOẠI BỎ (REJECTED RECORDS) TRONG PHASE 2 (RECORDS 501 - 2500)\n")
    f.write(f"TỔNG CỘNG: {len(rejected_entries)} / 2000 RECORDS BỊ LOẠI (DÁN NHÃN ####[])\n")
    f.write(f"================================================================================\n\n")
    
    for item in rejected_entries:
        f.write(f"--- [Record Master #{item['master_id']} | Phase2 #{item['phase2_id']}] ---\n")
        f.write(f"LÝ DO LOẠI: {item['reason']}\n")
        f.write(f"TEXT: {item['tokens']}\n")
        f.write(f"NHÃN GỐC TỪ MASTER: {item['master_triplets']}\n\n")

print(f"Generated {len(rejected_entries)} rejected records in {output_path}")
