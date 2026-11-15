import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f]

updates = {}

# 1. REC 1232 (idx 1231): Strip passive 'bị' -> 'ngập' [11], NEG
text_1232 = lines[1231].split('####')[0]
updates[1231] = (
    text_1232,
    [([1, 2, 3, 4], [11], 'NEG')]
)

# 2. REC 1233 (idx 1232): Strip passive 'bị' -> 'ngập' [20], NEG and add 'nước rút chậm' [25, 26, 27], NEG
text_1233 = lines[1232].split('####')[0]
updates[1232] = (
    text_1233,
    [
        ([15, 16, 17, 18], [20], 'NEG'),
        ([15, 16, 17, 18], [25, 26, 27], 'NEG')
    ]
)

# 3. REC 1237 (idx 1236): Fix aspect 'triều cường ở TPHCM' -> 'TPHCM' [6], opinion 'ngập' [8], NEG
text_1237 = lines[1236].split('####')[0]
updates[1236] = (
    text_1237,
    [([6], [8], 'NEG')]
)

# 4. REC 1238 (idx 1237): Clean opinion -> 'ngập' [26], NEG (avoid punctuation warning from quote mark)
text_1238 = lines[1237].split('####')[0]
updates[1237] = (
    text_1238,
    [([24, 25], [26], 'NEG')]
)

# 5. REC 1239 (idx 1238): Expand bare 'ngập' -> 'Nước ngập triền miên' [33, 34, 35], NEG
text_1239 = lines[1238].split('####')[0]
updates[1238] = (
    text_1239,
    [([1], [33, 34, 35], 'NEG')]
)

# 6. REC 1241 (idx 1240): Fix inverted 'rút' POS -> 'vẫn ngập sâu' [17, 18, 19], NEG (avoid token 20 comma)
text_1241 = lines[1240].split('####')[0]
updates[1240] = (
    text_1241,
    [([1], [17, 18, 19], 'NEG')]
)

# 7. REC 1242 (idx 1241): Fix negation inversion: bare 'ngập' NEG -> 'không có ngập' [19, 20, 21], POS
text_1242 = lines[1241].split('####')[0]
updates[1241] = (
    text_1242,
    [([1], [19, 20, 21], 'POS')]
)

# 8. REC 1243 (idx 1242): Expand bare 'ngập' -> 'thường xuyên ngập' [6, 7, 8], NEG
text_1243 = lines[1242].split('####')[0]
updates[1242] = (
    text_1243,
    [([1], [6, 7, 8], 'NEG')]
)

# 9. REC 1244 (idx 1243): Expand to 'giải quyết tình trạng ngập' [1, 2, 3, 4, 5], POS
text_1244 = lines[1243].split('####')[0]
updates[1243] = (
    text_1244,
    [([6, 7], [1, 2, 3, 4, 5], 'POS')]
)

# 10. REC 1245 (idx 1244): Construction schedule, non-flood 'rút ngắn thời gian', duplicate prefix -> REJECT (####[])
raw_1245 = lines[1244].split('####')[0]
if raw_1245.startswith('Tại TPHCM , Tại TP. Hồ Chí Minh , '):
    text_1245 = raw_1245.replace('Tại TPHCM , Tại TP. Hồ Chí Minh , ', 'Tại TPHCM , ')
else:
    text_1245 = raw_1245
updates[1244] = (
    text_1245,
    []
)

# 11. REC 1246 (idx 1245): Fix negation inversion & long string -> 'hết cảnh ngập lụt' [20, 21, 22, 23], POS
text_1246 = lines[1245].split('####')[0]
updates[1245] = (
    text_1246,
    [([1], [20, 21, 22, 23], 'POS')]
)

# 12. REC 1247 (idx 1246): Strip passive 'bị' -> 'ngập nặng' [39, 40], NEG
text_1247 = lines[1246].split('####')[0]
updates[1246] = (
    text_1247,
    [([5, 6, 7], [39, 40], 'NEG')]
)

# 13. REC 1248 (idx 1247): Strip passive 'bị' and long comma string -> 'ngập hơn 1m' [14, 15, 16], NEG
text_1248 = lines[1247].split('####')[0]
updates[1247] = (
    text_1248,
    [([4, 5, 6, 7, 8], [14, 15, 16], 'NEG')]
)

# 14. REC 1250 (idx 1249): Separate into 'nước tràn vào nhà' [5..8], NEG and 'ngập hơn 1m' [9, 10, 11], NEG
text_1250 = lines[1249].split('####')[0]
updates[1249] = (
    text_1250,
    [
        ([1], [5, 6, 7, 8], 'NEG'),
        ([1], [9, 10, 11], 'NEG')
    ]
)

# 15. REC 1251 (idx 1250): Expand bare 'ngập' -> 'ngập' [25], NEG
text_1251 = lines[1250].split('####')[0]
updates[1250] = (
    text_1251,
    [([1], [25], 'NEG')]
)

# 16. REC 1252 (idx 1251): Fix polarity flip: bare 'ngập' NEG -> 'giảm ngập' [24, 25], POS
text_1252 = lines[1251].split('####')[0]
updates[1251] = (
    text_1252,
    [([1], [24, 25], 'POS')]
)

# 17. REC 1253 (idx 1252): Fix aspect to 'hẻm 789' [58, 59] -> 'chống ngập tạm thời' [51, 52, 53, 54], POS
text_1253 = lines[1252].split('####')[0]
updates[1252] = (
    text_1253,
    [([58, 59], [51, 52, 53, 54], 'POS')]
)

# 18. REC 1255 (idx 1254): Strip passive 'bị' -> 'nhấn chìm' [26, 27], NEG
text_1255 = lines[1254].split('####')[0]
updates[1254] = (
    text_1255,
    [([14, 15, 16], [26, 27], 'NEG')]
)

# 19. REC 1256 (idx 1255): Fix DOC_FALLBACK_MISUSE -> 'Võ Văn Ngân' [14, 15, 16] -> 'chống ngập' [12, 13], POS
text_1256 = lines[1255].split('####')[0]
updates[1255] = (
    text_1256,
    [([14, 15, 16], [12, 13], 'POS')]
)

# 20. REC 1257 (idx 1256): Expand bare 'ngập' -> 'ngập trở nên nặng nề' [32, 33, 34, 35, 36], NEG
text_1257 = lines[1256].split('####')[0]
updates[1256] = (
    text_1257,
    [([1], [32, 33, 34, 35, 36], 'NEG')]
)

# 21. REC 1260 (idx 1259): Fix negation inversion: bare 'ngập' NEG -> 'không còn ngập' [34, 35, 36], POS
text_1260 = lines[1259].split('####')[0]
updates[1259] = (
    text_1260,
    [([1], [34, 35, 36], 'POS')]
)

# 22. REC 1262 (idx 1261): Shorten long comma-joined string [36..48] -> clean 'ngập sâu' [36, 37], NEG for all 4 entities
text_1262 = lines[1261].split('####')[0]
updates[1261] = (
    text_1262,
    [
        ([15, 16], [36, 37], 'NEG'),
        ([18, 19], [36, 37], 'NEG'),
        ([21, 22, 23], [36, 37], 'NEG'),
        ([25, 26, 27], [36, 37], 'NEG')
    ]
)

# 23. REC 1264 (idx 1263): Add 'chờ nước rút' [33, 34, 35], NEG along with 'chết máy' [9, 10], NEG
text_1264 = lines[1263].split('####')[0]
updates[1263] = (
    text_1264,
    [
        ([1, 2, 3, 4], [9, 10], 'NEG'),
        ([1, 2, 3, 4], [33, 34, 35], 'NEG')
    ]
)

# 24. REC 1266 (idx 1265): Add 'ngã nhào' [10, 11], NEG along with 'ngập' [28], NEG
text_1266 = lines[1265].split('####')[0]
updates[1265] = (
    text_1266,
    [
        ([1, 2, 3, 4], [10, 11], 'NEG'),
        ([1, 2, 3, 4], [28], 'NEG')
    ]
)

# 25. REC 1267 (idx 1266): Expand bare 'rút' -> 'rút nhanh hơn' [20, 21, 22], POS
text_1267 = lines[1266].split('####')[0]
updates[1266] = (
    text_1267,
    [([1], [20, 21, 22], 'POS')]
)

# 26. REC 1268 (idx 1267): Fix polarity flip: bare 'rút' POS -> 'ngập' [10], NEG and 'rút nhanh hơn' [29, 30, 31], POS
text_1268 = lines[1267].split('####')[0]
updates[1267] = (
    text_1268,
    [
        ([1], [10], 'NEG'),
        ([1], [29, 30, 31], 'POS')
    ]
)

# 27. REC 1271 (idx 1270): Add 'lưu thông bình thường trở lại' [24..28], POS along with 'ngập' [16], NEG
text_1271 = lines[1270].split('####')[0]
updates[1270] = (
    text_1271,
    [
        ([1], [16], 'NEG'),
        ([1], [24, 25, 26, 27, 28], 'POS')
    ]
)

# 28. REC 1275 (idx 1274): Add 'chết máy' [36, 37], NEG and 'chờ nước rút' [47, 48, 49], NEG along with 'ngập sâu' [22, 23], NEG
text_1275 = lines[1274].split('####')[0]
updates[1274] = (
    text_1275,
    [
        ([1, 2, 3, 4], [22, 23], 'NEG'),
        ([1, 2, 3, 4], [36, 37], 'NEG'),
        ([1, 2, 3, 4], [47, 48, 49], 'NEG')
    ]
)

# 29. REC 1276 (idx 1275): Clean long comma string to 'ngập diện rộng' [12, 13, 14], NEG
text_1276 = lines[1275].split('####')[0]
updates[1275] = (
    text_1276,
    [([2, 3, 4], [12, 13, 14], 'NEG')]
)

# 30. REC 1277 (idx 1276): Fix DOC_FALLBACK_MISUSE -> Aspect 'chợ Thủ Đức' [12, 13, 14], 'ngập hết' [36, 37], NEG
text_1277 = lines[1276].split('####')[0]
updates[1276] = (
    text_1277,
    [([12, 13, 14], [36, 37], 'NEG')]
)

# 31. REC 1279 (idx 1278): Fix polarity flip (flood suffering tagged POS) & clean 24-token comma string -> 'nước ngập' [4, 5], NEG and 'nước tràn vào' [28, 29, 30], NEG
text_1279 = lines[1278].split('####')[0]
updates[1278] = (
    text_1279,
    [
        ([1], [4, 5], 'NEG'),
        ([1], [28, 29, 30], 'NEG')
    ]
)

# Apply updates to lines
count = 0
for idx, (new_text, new_triplets) in updates.items():
    toks = new_text.split()
    # verify tokens
    for asp, opi, pol in new_triplets:
        asp_str = " ".join(toks[k] for k in asp)
        opi_str = " ".join(toks[k] for k in opi)
        assert all(0 <= k < len(toks) for k in asp), f"Asp index OOB in line {idx+1}: {asp}"
        assert all(0 <= k < len(toks) for k in opi), f"Opi index OOB in line {idx+1}: {opi}"
    lines[idx] = f"{new_text}####{new_triplets}"
    count += 1

with open('data/validate_label/thuan/phase2.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')

print(f"Successfully updated {count} records in Batch 40 (lines 1231-1280).")
