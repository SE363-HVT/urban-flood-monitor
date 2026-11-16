import ast, sys, re

sys.stdout.reconfigure(encoding='utf-8')

# Read raw batch 3
with open('scratch_batch3_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

assert len(blocks) == 100, f"Expected 100 blocks, got {len(blocks)}"

curated_lines = []

for idx, b in enumerate(blocks):
    rec_num = 201 + idx
    header, line = b.split('\n', 1)
    
    # Handle possible ##### or ####
    if '#####' in line:
        text, trip_str = line.split('#####', 1)
    elif '####' in line:
        text, trip_str = line.split('####', 1)
    else:
        text, trip_str = line, "[]"
        
    trip_str = trip_str.lstrip('#').strip()
    try:
        trips = ast.literal_eval(trip_str)
    except:
        trips = []
        
    c_text = text
    c_trips = trips
    
    # --- R201 to R210 ---
    if rec_num == 201:
        # Thủ Đức -> ngập lụt
        c_trips = [([10, 11], [7, 8], 'NEG')]
    elif rec_num == 202:
        # phường Thủ Đức -> chạy ngập
        c_trips = [([28, 29, 30], [35, 36], 'NEG')]
    elif rec_num == 203:
        # cầu Thủ Thiêm cũ -> ngập sâu
        c_trips = [([10, 11, 12, 13], [6, 7], 'NEG')]
    elif rec_num == 204:
        # Rule 9: Đinh Bộ Lĩnh, Nguyễn xí -> vẫn ngập sâu
        c_trips = [
            ([7, 8, 9], [22, 23, 24], 'NEG'),
            ([11, 12], [22, 23, 24], 'NEG')
        ]
    elif rec_num == 205:
        # đường Nguyễn Gia Trí -> ngập gần nửa bánh xe
        c_trips = [([6, 7, 8, 9], [19, 20, 21, 22, 23], 'NEG')]
    elif rec_num == 206:
        # Phan Huy Ích -> ngập nước sâu
        c_trips = [([0, 1, 2], [6, 7, 8], 'NEG')]
    elif rec_num == 207:
        # Gò Vấp, cổng bv 175 -> ngập
        c_trips = [
            ([5, 6], [15], 'NEG'),
            ([9, 10, 11], [15], 'NEG')
        ]
    elif rec_num == 208:
        # TPHCM -> ngập nước
        c_trips = [([19], [20, 21], 'NEG')]
    elif rec_num == 209:
        # ngã tư Hàng Xanh -> kẹt cứng
        c_trips = [([10, 11, 12, 13], [7, 8], 'NEG')]
    elif rec_num == 210:
        # Outside province Bình Dương, Vũng Tàu -> REJECT
        c_trips = []
        
    # --- R211 to R220 ---
    elif rec_num == 211:
        # Rule 9: đường Điện Biên Phủ, cầu Nguyễn Hữu Cảnh, cầu Sài Gòn -> bị ngập nặng
        c_trips = [
            ([5, 6, 7, 8], [20, 21, 22], 'NEG'),
            ([12, 13, 14, 15], [20, 21, 22], 'NEG'),
            ([17, 18, 19], [20, 21, 22], 'NEG')
        ]
    elif rec_num == 212:
        # TP. HCM -> bố trí máy bơm di động xử lý điểm ngập (POS)
        c_trips = [([0, 1], [8, 9, 10, 11], 'POS')]
    elif rec_num == 213:
        # Rule 9: Thảo Điền, chợ Thủ Đức, Tân Sơn Nhất -> ưu tiên xử lý ngập
        c_trips = [
            ([18, 19], [12, 13, 14, 15, 16], 'POS'),
            ([21, 22, 23], [12, 13, 14, 15, 16], 'POS'),
            ([25, 26, 27], [12, 13, 14, 15, 16], 'POS')
        ]
    elif rec_num == 214:
        # TP. HCM -> ĐẶT MỤC TIÊU HẾT NGẬP
        c_trips = [([0, 1], [2, 3, 4, 5, 6], 'POS')]
    elif rec_num == 215:
        # Rule 9: Thảo Điền, chợ Thủ Đức, Tân Sơn Nhất -> ưu tiên xử lý ngập
        c_trips = [
            ([8, 9], [2, 3, 4, 5, 6], 'POS'),
            ([11, 12, 13], [2, 3, 4, 5, 6], 'POS'),
            ([15, 16, 17], [2, 3, 4, 5, 6], 'POS')
        ]
    elif rec_num == 216:
        # Chung cư ad -> REJECT
        c_trips = []
    elif rec_num == 217:
        # Thảo Điền -> hóa hồ bơi
        c_trips = [([0, 1], [3, 4, 5], 'NEG')]
    elif rec_num == 218:
        # TP. HCM -> mưa lớn gây ngập
        c_trips = [([10, 11], [18, 19, 20, 21], 'NEG')]
    elif rec_num == 219:
        # đường Mã Lò -> ngập
        c_trips = [([5, 6, 7], [11], 'NEG')]
    elif rec_num == 220:
        # TP. HCM -> xuất hiện tình trạng ngập
        c_trips = [([19, 20], [38, 39, 40, 41], 'NEU')]
        
    # --- R221 to R230 ---
    elif rec_num == 221:
        # rạch Thủ Đức -> dâng nhanh rồi tràn qua bờ kè, đường số 11 -> ngập sâu hơn 1m
        c_trips = [
            ([10, 11, 12], [15, 16, 17, 18, 19, 20, 21], 'NEG'),
            ([30, 31, 32], [44, 45, 46, 47], 'NEG')
        ]
    elif rec_num == 222:
        # chợ Thủ Đức -> ngập đường
        c_trips = [([12, 13, 14], [9, 10], 'NEG')]
    elif rec_num == 223:
        # Cut prefix 'Tại TP. Hồ Chí Minh ,' because text already has 'Tuyến đường Tô Ngọc Vân'
        prefix = "Tại TP. Hồ Chí Minh , "
        if c_text.startswith(prefix):
            c_text = c_text[len(prefix):]
        # Text: Trận mưa rất lớn lúc 15h30 chiều nay kéo dài khoảng hơn 1h nhưng nước suối Tô Ngọc Vân dâng lên rất cao và chảy xiết . Tuyến đường Tô Ngọc Vân bị ngập cục bộ 1 số đoạn làm 2 oto phải gọi cứu hộ . Rất may là mưa đã hết nên nước đang rút dần .
        # Tokenizing c_text:
        # 27: Tuyến 28: đường 29: Tô 30: Ngọc 31: Vân -> bị ngập cục bộ (33..35)
        # 54: nước 55: đang 56: rút 57: dần (54..57 POS)
        toks_223 = c_text.split()
        asp_idx = []
        opi_idx_neg = []
        opi_idx_pos = []
        for i, t in enumerate(toks_223):
            if t == 'Tuyến' and i+3 < len(toks_223) and toks_223[i+1]=='đường' and toks_223[i+2]=='Tô':
                asp_idx = [i, i+1, i+2, i+3, i+4]
            if t == 'bị' and i+2 < len(toks_223) and toks_223[i+1]=='ngập' and toks_223[i+2]=='cục':
                opi_idx_neg = [i, i+1, i+2, i+3]
            if t == 'nước' and i+3 < len(toks_223) and toks_223[i+1]=='đang' and toks_223[i+2]=='rút':
                opi_idx_pos = [i, i+1, i+2, i+3]
        c_trips = [
            (asp_idx, opi_idx_neg, 'NEG'),
            (asp_idx, opi_idx_pos, 'POS')
        ]
    elif rec_num == 224:
        # đường Tô Ngọc Vân -> ngập cục bộ (NEG), nước đang rút (POS)
        c_trips = [
            ([15, 16, 17, 18], [10, 11, 12], 'NEG'),
            ([15, 16, 17, 18], [35, 36, 37], 'POS')
        ]
    elif rec_num == 225:
        # đường Tô Ngọc Vân -> nước đã dâng lút bánh xe , chảy xiết (NEG)
        # đường Linh Đông -> ngập nặng nhất (NEG)
        c_trips = [
            ([20, 21, 22, 23], [34, 35, 36, 37, 38, 39, 40, 41, 42], 'NEG'),
            ([48, 49, 50], [51, 52, 53], 'NEG')
        ]
    elif rec_num == 226:
        # đường Phan Huy Ích -> BIẾN THÀNH SÔNG
        c_trips = [([0, 1, 2, 3], [4, 5, 6], 'NEG')]
    elif rec_num == 227:
        # đường Phan Huy ích -> ngập lụt
        c_trips = [([5, 6, 7, 8], [2, 3], 'NEG')]
    elif rec_num == 228:
        # đường Phan Huy Ích -> ngập chấn động
        c_trips = [([13, 14, 15, 16], [9, 10, 11], 'NEG')]
    elif rec_num == 229:
        # đường Phan Huy Ích -> rốn ngập
        c_trips = [([5, 6, 7, 8], [11, 12], 'NEG')]
    elif rec_num == 230:
        # Ghé quán cafe -> REJECT
        c_trips = []
        
    # --- R231 to R240 ---
    elif rec_num == 231:
        # đường Phan Huy ích -> ngập lụt
        c_trips = [([8, 9, 10, 11], [5, 6], 'NEG')]
    elif rec_num == 232:
        # Đường Phan Huy Ích -> cứ mưa là ngập
        c_trips = [([4, 5, 6, 7], [9, 10, 11, 12], 'NEG')]
    elif rec_num == 233:
        # Đường Phan Huy Ích -> ngập sâu cả mét
        c_trips = [([0, 1, 2, 3], [4, 5, 6, 7], 'NEG')]
    elif rec_num == 234:
        # đường Phan Huy Ích -> rút nước (POS)
        c_trips = [([7, 8, 9, 10], [11, 12], 'POS')]
    elif rec_num == 235:
        # Đường Phan Huy Ích -> ngập sâu cả mét
        c_trips = [([6, 7, 8, 9], [14, 15, 16, 17], 'NEG')]
    elif rec_num == 236:
        # đường Phan Huy Ích -> đã rút bớt (POS)
        c_trips = [([17, 18, 19, 20], [29, 30, 31], 'POS')]
    elif rec_num == 237:
        # đường Phan Huy Ích -> ngập sâu hơn một mét
        c_trips = [([16, 17, 18, 19], [22, 23, 24, 25, 26], 'NEG')]
    elif rec_num == 238:
        # Phan Huy Ích -> vẫn ngập sâu
        c_trips = [([7, 8, 9], [3, 4, 5], 'NEG')]
    elif rec_num == 239:
        # đường Phan Huy ích -> ngập
        c_trips = [([3, 4, 5, 6], [9], 'NEG')]
    elif rec_num == 240:
        # Đường Nguyễn Văn Khối -> ngập như sông
        c_trips = [([6, 7, 8, 9], [10, 11, 12], 'NEG')]
        
    # --- R241 to R250 ---
    elif rec_num == 241:
        # Tân Hòa Đông, ngã tư bốn xã -> ngập rất sâu
        c_trips = [
            ([18, 19, 20], [51, 52, 53], 'NEG'),
            ([24, 25, 26, 27], [51, 52, 53], 'NEG')
        ]
    elif rec_num == 242:
        # Rule 9: Hồ Học Lãm, Mã Lò, Tên Lửa, Tỉnh Lộ 10, Tân Hòa Đông, Phan Anh, Quang Trung -> xảy ra ngập
        c_trips = [
            ([33, 34, 35], [27, 28, 29], 'NEG'),
            ([37, 38], [27, 28, 29], 'NEG'),
            ([42, 43], [27, 28, 29], 'NEG'),
            ([45, 46, 47], [27, 28, 29], 'NEG'),
            ([49, 50, 51], [27, 28, 29], 'NEG'),
            ([53, 54], [27, 28, 29], 'NEG'),
            ([56, 57], [27, 28, 29], 'NEG')
        ]
    elif rec_num == 243:
        # Bds chốt cọc -> REJECT
        c_trips = []
    elif rec_num == 244:
        # TP. Hồ Chí Minh -> xử lý ngập đô thị (POS)
        c_trips = [([14, 15, 16, 17], [23, 24, 25, 26, 27], 'POS')]
    elif rec_num == 245:
        # hầm vượt sông Sài Gòn -> kẹt cứng, đường Mai Chí Thọ -> ngập như sông
        c_trips = [
            ([9, 10, 11, 12, 13], [14, 15], 'NEG'),
            ([17, 18, 19, 20], [21, 22, 23], 'NEG')
        ]
    elif rec_num == 246:
        # TPHCM -> mưa to gây ngập (NEU forecast)
        c_trips = [([2], [26, 27, 28, 29], 'NEU')]
    elif rec_num == 247:
        # TPHCM -> mưa lớn gây ngập (NEU forecast)
        c_trips = [([5], [24, 25, 26, 27], 'NEU')]
    elif rec_num == 248:
        # Quán nhạc vàng meme -> REJECT
        c_trips = []
    elif rec_num == 249:
        # Quán nhạc vàng meme -> REJECT
        c_trips = []
    elif rec_num == 250:
        # Quán nhạc vàng meme -> REJECT
        c_trips = []
        
    # --- R251 to R260 ---
    elif rec_num == 251:
        # Sài Gòn -> ngập úng
        c_trips = [([0, 1], [11, 12], 'NEG')]
    elif rec_num == 252:
        # HẦM CHUI AN PHÚ -> HẾT NGẬP (POS)
        c_trips = [([0, 1, 2, 3], [5, 6], 'POS')]
    elif rec_num == 253:
        # tphcm -> ngập nước
        c_trips = [([14], [1, 2], 'NEG')]
    elif rec_num == 254:
        # TP. HCM -> ngập nước
        c_trips = [([10, 11], [12, 13], 'NEG')]
    elif rec_num == 255:
        # TP. HCM -> ngập nặng
        c_trips = [([0, 1], [13, 14], 'NEG')]
    elif rec_num == 256:
        # Outside province Bình Dương -> REJECT
        c_trips = []
    elif rec_num == 257:
        # Sài Gòn -> nước ngập
        c_trips = [([13, 14], [10, 11], 'NEG')]
    elif rec_num == 258:
        # TP. HCM -> chống ngập bằng dữ liệu và AI (POS)
        c_trips = [([0, 1], [4, 5, 6, 7, 8, 9, 10], 'POS')]
    elif rec_num == 259:
        # Sushi delivery ad -> REJECT
        c_trips = []
    elif rec_num == 260:
        # khu đô thị Sala -> nước ngập sâu
        c_trips = [([8, 9, 10, 11], [15, 16, 17], 'NEG')]
        
    # --- R261 to R270 ---
    elif rec_num == 261:
        # TP HCM -> điểm ngập thường xuyên (NEU)
        c_trips = [([8, 9], [3, 4, 5, 6], 'NEU')]
    elif rec_num == 262:
        # Remix DJ / Hà Bình Thuận -> REJECT
        c_trips = []
    elif rec_num == 263:
        # TP. HCM -> ngập nước
        c_trips = [([7, 8], [18, 19], 'NEG')]
    elif rec_num == 264:
        # TPHCM -> Nước ngập gần hết bánh xe
        c_trips = [([12], [0, 1, 2, 3, 4, 5], 'NEG')]
    elif rec_num == 265:
        # Khu dân cư Cityland Park Hills -> ngập sâu
        c_trips = [([0, 1, 2, 3, 4, 5], [9, 10], 'NEG')]
    elif rec_num == 266:
        # TPHCM -> nguy cơ ngập (NEU)
        c_trips = [([0], [6, 7, 8], 'NEU')]
    elif rec_num == 267:
        # TP. HCM -> CẢNH BÁO NGẬP (NEU)
        c_trips = [([2, 3], [9, 10, 11], 'NEU')]
    elif rec_num == 268:
        # TP. Hồ Chí Minh -> tăng giải pháp chống ngập (POS)
        c_trips = [([0, 1, 2, 3], [4, 5, 6, 7, 8], 'POS')]
    elif rec_num == 269:
        # TP. Hồ Chí Minh -> dự kiến hoàn thành 9 dự án chống ngập (POS)
        c_trips = [([11, 12, 13, 14], [15, 16, 17, 18, 19, 20, 21, 22, 23], 'POS')]
    elif rec_num == 270:
        # Sài Gòn -> hết ngập (POS)
        c_trips = [([2, 3], [5, 6], 'POS')]
        
    # --- R271 to R280 ---
    elif rec_num == 271:
        # Bds Củ Chi -> REJECT
        c_trips = []
    elif rec_num == 272:
        # TP. HCM -> Tăng cường ứng phó ngập (POS)
        c_trips = [([0, 1], [3, 4, 5, 6, 7], 'POS')]
    elif rec_num == 273:
        # TP. HCM -> chìm trong biển nước
        c_trips = [([13, 14], [15, 16, 17, 18], 'NEG')]
    elif rec_num == 274:
        # Sài Gòn -> đường sá ngập
        c_trips = [([4, 5], [15, 16, 17], 'NEG')]
    elif rec_num == 275:
        # Rule 9: SC vivocity, Lotte quận 7 -> xe ngập nửa bánh
        c_trips = [
            ([3, 4], [10, 11, 12, 13], 'NEG'),
            ([6, 7, 8], [10, 11, 12, 13], 'NEG')
        ]
    elif rec_num == 276:
        # Meme weather -> REJECT
        c_trips = []
    elif rec_num == 277:
        # Headline only windy miennam -> REJECT
        c_trips = []
    elif rec_num == 278:
        # Meme Cầu Ba Son -> REJECT
        c_trips = []
    elif rec_num == 279:
        # Meme Chiến thần lội nước -> REJECT
        c_trips = []
    elif rec_num == 280:
        # Meme Mưa bão -> REJECT
        c_trips = []
        
    # --- R281 to R290 ---
    elif rec_num == 281:
        # đường Phan Huy Ích -> mưa ngập
        c_trips = [([5, 6, 7, 8], [2, 3], 'NEG')]
    elif rec_num == 282:
        # Đường Phan Văn Trị -> bị ngập sâu
        c_trips = [([0, 1, 2, 3], [12, 13, 14], 'NEG')]
    elif rec_num == 283:
        # Rule 9: Sài Gòn, Quận Gò Vấp -> ngập
        c_trips = [
            ([5, 6], [3], 'NEG'),
            ([8, 9, 10], [3], 'NEG')
        ]
    elif rec_num == 284:
        # TPHCM -> lội nước
        c_trips = [([0], [8, 9], 'NEG')]
    elif rec_num == 285:
        # TP. HCM -> xử lý dứt điểm 50 điểm ngập úng trọng điểm (POS)
        c_trips = [([0, 1], [17, 18, 19, 20, 21, 22, 23, 24, 25, 26], 'POS')]
    elif rec_num == 286:
        # Đường -> hết ngập (POS), nhà -> lại ngập (NEG)
        c_trips = [
            ([36], [37, 38], 'POS'),
            ([40], [41, 42], 'NEG')
        ]
    elif rec_num == 287:
        # Rule 9: Gò Vấp, Bình Thạnh -> ngập nặng
        c_trips = [
            ([2, 3], [7, 8], 'NEG'),
            ([5, 6], [7, 8], 'NEG')
        ]
    elif rec_num == 288:
        # phường Tam Bình -> triển khai ứng dụng tiếp nhận thông tin (POS)
        c_trips = [([12, 13, 14], [20, 21, 22, 23, 24, 25, 26, 27], 'POS')]
    elif rec_num == 289:
        # Rule 9: đường Đinh Bộ Lĩnh, Bạch Đằng -> ngập gần 5 tiếng
        c_trips = [
            ([12, 13, 14, 15], [19, 20, 21, 22], 'NEG'),
            ([17, 18], [19, 20, 21, 22], 'NEG')
        ]
    elif rec_num == 290:
        # Nguyễn Văn Khối -> Ngập Tới Đ . ầu Gối
        c_trips = [([8, 9, 10], [13, 14, 15, 16, 17, 18], 'NEG')]
        
    # --- R291 to R300 ---
    elif rec_num == 291:
        # Đường Nguyễn Văn Khối -> hoá biển nước
        c_trips = [([0, 1, 2, 3], [8, 9, 10], 'NEG')]
    elif rec_num == 292:
        # Đường Phạm Hữu Lầu -> ngập rất sâu
        c_trips = [([0, 1, 2, 3], [8, 9, 10], 'NEG')]
    elif rec_num == 293:
        # Meme chuỗi ngày mưa -> REJECT
        c_trips = []
    elif rec_num == 294:
        # TP HCM -> ngập do triều cường
        c_trips = [([0, 1], [2, 3, 4, 5], 'NEG')]
    elif rec_num == 295:
        # Sài Gòn -> cứ mưa là ngập
        c_trips = [([0, 1], [2, 3, 4, 5], 'NEG')]
    elif rec_num == 296:
        # Triều cường tại TP. Hồ Chí Minh -> dự báo đạt đỉnh (NEU)
        c_trips = [([0, 1, 2, 3, 4, 5, 6], [7, 8, 9, 10], 'NEU')]
    elif rec_num == 297:
        # TPHCM -> có nguy cơ ngập (NEU)
        c_trips = [([4], [9, 10, 11, 12], 'NEU')]
    elif rec_num == 298:
        # trung tâm TPHCM -> ngập nặng
        c_trips = [([14, 15, 16], [6, 7], 'NEG')]
    elif rec_num == 299:
        # TPHCM -> kiểm tra đường ngập (POS)
        c_trips = [([3], [8, 9, 10, 11], 'POS')]
    elif rec_num == 300:
        # TPHCM -> có nguy cơ ngập (NEU)
        c_trips = [([4], [9, 10, 11, 12], 'NEU')]

    curated_lines.append(f"{c_text}####{c_trips}")

assert len(curated_lines) == 100, f"Expected 100 lines, got {len(curated_lines)}"

# Read existing lines from phase3.txt
out_path = 'data/validate_label/thuan/phase3.txt'
with open(out_path, 'r', encoding='utf-8') as f:
    existing_lines = [l.strip() for l in f if l.strip()]

# Keep the first 200 lines (Batch 1 + Batch 2)
batch1_2_lines = existing_lines[:200]
final_lines = batch1_2_lines + curated_lines

with open(out_path, 'w', encoding='utf-8') as out_f:
    for l in final_lines:
        out_f.write(l + '\n')

print(f"Successfully wrote 200 previous lines + 100 Batch 3 lines. Total lines in {out_path}: {len(final_lines)}")
