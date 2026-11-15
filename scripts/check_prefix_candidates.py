import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

# Let us identify all records starting with prefix
# We want to know: which ones have an actual location in the text?
# 1. Road, street, bridge, tunnel, alley, highway, circle, intersection, market, bus station, canal, river, landmark
# 2. Districts: 1..12, Binh Thanh, Thu Duc, Go Vap, Tan Binh, Tan Phu, Phu Nhuan, Binh Tan, Nha Be, Hoc Mon, Cu Chi, Can Gio, Binh Chanh, Di An, Thuan An, Thu Dau Mot, Ben Cat, Tan Uyen, Vung Tau, Ba Ria
# 3. Famous landmarks: Thao Dien, Thanh Da, An Phu, Phu My Hung, Hang Xanh, Bay Hien, Ba Son, Bui Vien, Phan Huy Ich...

# Notice: In the 55 records where triplets target ONLY body entities, or 4 where triplets target both,
# the triplets ALREADY target the specific location in the body!
# What about other records where the text mentions a district/ward/street?
# Let us inspect ALL records starting with "Tại TP. Hồ Chí Minh , " or "Tại TPHCM , "

prefix_candidates = []
for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip_str = line.split('####')
    triplets = ast.literal_eval(trip_str)
    
    prefix = None
    body = text
    pfx_len = 0
    if text.startswith('Tại TP. Hồ Chí Minh , '):
        prefix = 'Tại TP. Hồ Chí Minh , '
        body = text[len('Tại TP. Hồ Chí Minh , '):]
        pfx_len = 6 # tokens: 'Tại', 'TP.', 'Hồ', 'Chí', 'Minh', ','
    elif text.startswith('Tại TPHCM , '):
        prefix = 'Tại TPHCM , '
        body = text[len('Tại TPHCM , '):]
        pfx_len = 3 # tokens: 'Tại', 'TPHCM', ','
    elif text.startswith('Tại TP.HCM , '):
        prefix = 'Tại TP.HCM , '
        body = text[len('Tại TP.HCM , '):]
        pfx_len = 4 # tokens: 'Tại', 'TP.HCM', ','
        
    if not prefix:
        continue
        
    prefix_candidates.append({
        'rec_num': rec_num,
        'prefix': prefix,
        'pfx_len': pfx_len,
        'text': text,
        'body': body,
        'triplets': triplets
    })

print(f"Total records with prefix: {len(prefix_candidates)}")

# Now let us check each candidate to see if body contains a specific location
# Let's write a comprehensive checker
