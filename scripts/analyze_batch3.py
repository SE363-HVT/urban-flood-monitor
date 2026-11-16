import sys, ast, re

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch_batch3_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

outside_provinces = [
    'hà nội', 'hải phòng', 'đà nẵng', 'cần thơ', 'nha trang', 'đà lạt',
    'huế', 'quảng ninh', 'bình dương', 'đồng nai', 'vũng tàu', 'long an',
    'tiền giang', 'bến tre', 'vĩnh long', 'trà vinh', 'hậu giang', 'sóc trăng',
    'bạc liêu', 'cà mau', 'an giang', 'kiên giang', 'đồng tháp', 'bắc ninh',
    'nghệ an', 'thanh hóa', 'quảng bình', 'quảng trị', 'quảng nam', 'quảng ngãi',
    'bình định', 'phú yên', 'khánh hòa', 'ninh thuận', 'bình thuận', 'kon tum',
    'gia lai', 'đắk lắk', 'đắk nông', 'lâm đồng', 'bình phước', 'tây ninh',
    'sa đéc', 'hạ long', 'thái nguyên', 'nam định', 'thái bình', 'hải dương'
]

print(f"Tổng số blocks đọc được: {len(blocks)}")
for idx, b in enumerate(blocks):
    rec_num = 201 + idx
    header, line = b.split('\n', 1)
    text, trip_str = line.split('####')
    trips = ast.literal_eval(trip_str)
    
    text_lower = text.lower()
    
    # Check outside provinces
    out_prov = [p for p in outside_provinces if p in text_lower]
    
    # Check ads / contact
    has_contact = bool(re.search(r'(0\d{8,10}|hotline|liên hệ|inbox|giá bán|giá chỉ|zalo)', text_lower))
    
    # Check triage indicators
    notes = []
    if out_prov:
        notes.append(f"Tỉnh ngoài: {out_prov}")
    if has_contact:
        notes.append("Có liên hệ/quảng cáo")
    if 'triều cường' in text_lower or 'đỉnh triều' in text_lower:
        notes.append("Có triều cường/đỉnh triều")
    if text.startswith('Tại TP. Hồ Chí Minh ,') or text.startswith('Tại TPHCM ,'):
        notes.append("Có tiền tố nhân tạo đầu câu")
        
    if notes or len(trips) == 0:
        print(f"REC {rec_num}: {' | '.join(notes)} | Raw trips: {len(trips)}")
