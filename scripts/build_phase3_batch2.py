import ast, sys

sys.stdout.reconfigure(encoding='utf-8')

# Read raw batch 2
with open('scratch_batch2_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

curated_lines = []

for idx, b in enumerate(blocks):
    rec_num = 101 + idx
    header, line = b.split('\n', 1)
    text, trip_str = line.split('####')
    trips = ast.literal_eval(trip_str)
    
    c_text = text
    c_trips = trips
    
    # R101: ok
    if rec_num == 101:
        c_trips = [([3, 4, 5, 6], [0, 1], 'NEG')]
    # R102: Rich opinion
    elif rec_num == 102:
        c_trips = [([7, 8], [4, 5, 6], 'NEG')]
    # R103: ok
    elif rec_num == 103:
        c_trips = [([2], [3, 4], 'NEG')]
    # R104: NEU
    elif rec_num == 104:
        c_trips = [([2], [32, 33, 34, 35, 36, 37, 38], 'NEU')]
    # R105: Clean aspect
    elif rec_num == 105:
        c_trips = [([19], [21, 22, 23, 24], 'NEG')]
    # R106: Clean aspect
    elif rec_num == 106:
        c_trips = [([0, 1], [13, 14], 'NEG')]
    # R107: ok
    elif rec_num == 107:
        c_trips = [([11], [6, 7], 'NEG')]
    # R108: ok
    elif rec_num == 108:
        c_trips = [([3, 4], [5, 6], 'NEG')]
    # R109: ok
    elif rec_num == 109:
        c_trips = [([5], [6, 7, 8], 'NEG')]
    # R110: ok
    elif rec_num == 110:
        c_trips = [([4, 5], [11], 'NEG')]
    # R111: Rich opinion
    elif rec_num == 111:
        c_trips = [([0], [15, 16, 17, 18], 'NEG')]
    # R112: ok
    elif rec_num == 112:
        c_trips = [([38], [39, 40], 'NEG')]
    # R113: Scenery sunset photo -> REJECT
    elif rec_num == 113:
        c_trips = []
    # R114: ok
    elif rec_num == 114:
        c_trips = [([41, 42, 43], [46, 47, 48, 49], 'NEG')]
    # R115: Clean aspect
    elif rec_num == 115:
        c_trips = [
            ([5, 6], [7, 8, 9], 'NEG'),
            ([44, 45], [28, 29, 30, 31, 32, 33, 34], 'NEG'),
            ([47, 48, 49], [28, 29, 30, 31, 32, 33, 34], 'NEG')
        ]
    # R116: Strip dòng nước & hashtag duplicates
    elif rec_num == 116:
        c_trips = [([8, 9, 10, 11], [17, 18, 19, 20], 'NEG')]
    # R117: ok
    elif rec_num == 117:
        c_trips = [([6, 7], [8, 9], 'NEG')]
    # R118: ok
    elif rec_num == 118:
        c_trips = [([6, 7], [8, 9], 'NEG')]
    # R119: ok
    elif rec_num == 119:
        c_trips = [([0, 1], [2, 3, 4, 5], 'NEG')]
    # R120: Car repair advice -> REJECT
    elif rec_num == 120:
        c_trips = []
    # R121: Rule 9
    elif rec_num == 121:
        c_trips = [
            ([11, 12], [19, 20, 21, 22], 'NEG'),
            ([14, 15], [19, 20, 21, 22], 'NEG'),
            ([16, 17], [19, 20, 21, 22], 'NEG')
        ]
    # R122: Project POS
    elif rec_num == 122:
        c_trips = [([0], [6, 7, 8, 9, 10, 11], 'POS')]
    # R123: ok
    elif rec_num == 123:
        c_trips = [([2], [6, 7, 8, 9], 'NEG')]
    # R124: POS
    elif rec_num == 124:
        c_trips = [([6], [13, 14], 'POS')]
    # R125: ok
    elif rec_num == 125:
        c_trips = [([31, 32, 33, 34], [48, 49], 'NEG')]
    # R126: ok
    elif rec_num == 126:
        c_trips = [([0, 1, 2, 3], [4, 5, 6, 7], 'NEG')]
    # R127: Recommendation NEU
    elif rec_num == 127:
        c_trips = [([0, 1], [9, 10], 'NEU')]
    # R128: Room rental ad -> REJECT
    elif rec_num == 128:
        c_trips = []
    # R129: Multi entity
    elif rec_num == 129:
        c_trips = [([0, 1], [10, 11], 'NEG'), ([3, 4], [10, 11], 'NEG')]
    # R130: Rule 9 with POS for non-flooded area
    elif rec_num == 130:
        c_trips = [
            ([0, 1], [17, 18], 'NEG'),
            ([3, 4], [17, 18], 'NEG'),
            ([23, 24], [28, 29, 30, 31, 32], 'POS')
        ]
    # R131: ok
    elif rec_num == 131:
        c_trips = [([0, 1, 2, 3, 4], [28, 29, 30, 31], 'NEG')]
    # R132: ok
    elif rec_num == 132:
        c_trips = [([5], [6, 7, 8, 9, 10], 'NEG')]
    # R133: ok
    elif rec_num == 133:
        c_trips = [([50, 51, 52], [31, 32], 'NEG')]
    # R134: Question NEU
    elif rec_num == 134:
        c_trips = [([0, 1], [5, 6, 7, 8], 'NEU')]
    # R135: Rule 9
    elif rec_num == 135:
        c_trips = [([10, 11, 12], [21, 22, 23], 'NEG'), ([14, 15], [21, 22, 23], 'NEG')]
    # R136: Rule 9
    elif rec_num == 136:
        c_trips = [([33, 34, 35, 36], [49, 50, 51], 'NEG'), ([38, 39, 40], [49, 50, 51], 'NEG')]
    # R137: Newspaper title tip without location -> REJECT
    elif rec_num == 137:
        c_trips = []
    # R138: Rule 9
    elif rec_num == 138:
        c_trips = [
            ([19, 20, 21], [23, 24, 25, 26, 27], 'NEG'),
            ([37, 38, 39], [41, 42, 43, 44, 45], 'NEG'),
            ([56, 57, 58], [60], 'NEG'),
            ([80, 81, 82], [84, 85, 86], 'NEG')
        ]
    # R139: ok
    elif rec_num == 139:
        c_trips = [([0], [1, 2], 'NEG')]
    # R140: Warning NEU
    elif rec_num == 140:
        c_trips = [([0, 1], [8, 9, 10], 'NEU')]
    # R141: ok
    elif rec_num == 141:
        c_trips = [([54, 55, 56, 57], [5, 6], 'NEG')]
    # R142: Rule 9
    elif rec_num == 142:
        c_trips = [
            ([39, 40, 41], [12, 13, 14, 15, 16], 'NEG'),
            ([43, 44, 45], [12, 13, 14, 15, 16], 'NEG'),
            ([47, 48, 49], [12, 13, 14, 15, 16], 'NEG'),
            ([51, 52], [12, 13, 14, 15, 16], 'NEG'),
            ([54, 55, 56], [12, 13, 14, 15, 16], 'NEG')
        ]
    # R143: ok
    elif rec_num == 143:
        c_trips = [([9, 10, 11], [53, 54], 'NEG')]
    # R144: ok
    elif rec_num == 144:
        c_trips = [([25, 26, 27, 28], [40, 41, 42, 43, 44, 45], 'NEG')]
    # R145: Project POS
    elif rec_num == 145:
        c_trips = [([6, 7, 8, 9], [10, 11, 12, 13, 14, 15, 16], 'POS')]
    # R146: Rule 9 (all 4 streets)
    elif rec_num == 146:
        c_trips = [
            ([5], [21, 22, 23, 24, 25], 'NEG'),
            ([6], [21, 22, 23, 24, 25], 'NEG'),
            ([7, 8, 9], [21, 22, 23, 24, 25], 'NEG'),
            ([10, 11, 12], [21, 22, 23, 24, 25], 'NEG')
        ]
    # R147: Rule 9 POS
    elif rec_num == 147:
        c_trips = [
            ([21, 22, 23, 24, 25], [19, 20], 'POS'),
            ([27, 28, 29], [19, 20], 'POS'),
            ([31, 32, 33], [19, 20], 'POS')
        ]
    # R148: ok
    elif rec_num == 148:
        c_trips = [([0, 1], [2, 3], 'NEG')]
    # R149: ok
    elif rec_num == 149:
        c_trips = [([18, 19], [52, 53, 54, 55, 56, 57], 'NEG')]
    # R150: ok
    elif rec_num == 150:
        c_trips = [([5, 6, 7, 8], [18, 19], 'NEG')]
    # R151: ok
    elif rec_num == 151:
        c_trips = [([18, 19, 20, 21], [25, 26, 27, 28, 29], 'NEG')]
    # R152: ok
    elif rec_num == 152:
        c_trips = [([11, 12], [13, 14], 'NEG')]
    # R153: ok
    elif rec_num == 153:
        c_trips = [([6], [12, 13, 14, 15], 'NEG')]
    # R154: Clean aspect
    elif rec_num == 154:
        c_trips = [([31, 32, 33], [35, 36], 'NEG')]
    # R155: ok
    elif rec_num == 155:
        c_trips = [([19, 20], [25, 26, 27], 'NEG')]
    # R156: POS
    elif rec_num == 156:
        c_trips = [([0, 1], [9, 10], 'POS')]
    # R157: ok
    elif rec_num == 157:
        c_trips = [([12, 13, 14], [8, 9, 10], 'NEG')]
    # R158: ok
    elif rec_num == 158:
        c_trips = [([20, 21], [11, 12], 'NEG')]
    # R159: ok
    elif rec_num == 159:
        c_trips = [([32, 33, 34], [48, 49], 'NEG')]
    # R160: ok
    elif rec_num == 160:
        c_trips = [([18, 19, 20], [33, 34], 'NEG')]
    # R161: ok
    elif rec_num == 161:
        c_trips = [([26, 27], [59, 60, 61], 'NEG')]
    # R162: Strip city duplicate
    elif rec_num == 162:
        c_trips = [([13, 14], [28, 29], 'NEG')]
    # R163: Strip city duplicate
    elif rec_num == 163:
        c_trips = [([17, 18], [24, 25], 'NEG')]
    # R164: Clean aspect
    elif rec_num == 164:
        c_trips = [([14, 15, 16], [11, 12], 'NEG')]
    # R165: Aquarium installation ad -> REJECT
    elif rec_num == 165:
        c_trips = []
    # R166: Rule 9
    elif rec_num == 166:
        c_trips = [
            ([8, 9], [20, 21, 22, 23, 24], 'NEG'),
            ([14, 15], [20, 21, 22, 23, 24], 'NEG')
        ]
    # R167: Rule 9
    elif rec_num == 167:
        c_trips = [([4, 5], [21, 22], 'NEG'), ([7, 8], [21, 22], 'NEG')]
    # R168: Rule 9
    elif rec_num == 168:
        c_trips = [
            ([2, 3], [14, 15], 'NEG'),
            ([5, 6], [14, 15], 'NEG'),
            ([8, 9], [14, 15], 'NEG')
        ]
    # R169: ok
    elif rec_num == 169:
        c_trips = [([6, 7, 8], [14, 15], 'NEG')]
    # R170: ok
    elif rec_num == 170:
        c_trips = [([1, 2], [15], 'NEG')]
    # R171: ok
    elif rec_num == 171:
        c_trips = [([6], [13, 14, 15], 'NEG')]
    # R172: Strip duplicate
    elif rec_num == 172:
        c_trips = [([13, 14], [28, 29], 'NEG')]
    # R173: ok
    elif rec_num == 173:
        c_trips = [([14, 15, 16], [29, 30, 31], 'NEG')]
    # R174: ok
    elif rec_num == 174:
        c_trips = [([2, 3], [4, 5, 6, 7, 8], 'NEG')]
    # R175: ok
    elif rec_num == 175:
        c_trips = [([15, 16], [17, 18, 19], 'NEG')]
    # R176: ok
    elif rec_num == 176:
        c_trips = [([14, 15, 16, 17], [18, 19, 20, 21], 'NEG')]
    # R177: ok
    elif rec_num == 177:
        c_trips = [([5, 6, 7, 8], [16, 17], 'NEG')]
    # R178: ok
    elif rec_num == 178:
        c_trips = [([11, 12], [6, 7, 8, 9], 'NEG')]
    # R179: ok
    elif rec_num == 179:
        c_trips = [([15, 16, 17], [30, 31], 'NEG')]
    # R180: NEU
    elif rec_num == 180:
        c_trips = [([0], [1, 2, 3, 4, 5], 'NEU')]
    # R181: NEU
    elif rec_num == 181:
        c_trips = [([5, 6], [7, 8, 9], 'NEU')]
    # R182: Strip duplicate
    elif rec_num == 182:
        c_trips = [([14, 15, 16, 17], [27, 28], 'NEG')]
    # R183: Forecast NEU
    elif rec_num == 183:
        c_trips = [([4], [17, 18], 'NEU')]
    # R184: Forecast NEU
    elif rec_num == 184:
        c_trips = [([5], [21, 22], 'NEU')]
    # R185: Forecast NEU
    elif rec_num == 185:
        c_trips = [([2, 3, 4, 5], [9, 10, 11], 'NEU')]
    # R186: Forecast NEU
    elif rec_num == 186:
        c_trips = [([2], [8, 9, 10], 'NEU')]
    # R187: ok
    elif rec_num == 187:
        c_trips = [([3, 4], [11, 12], 'NEG')]
    # R188: ok
    elif rec_num == 188:
        c_trips = [([0, 1], [24, 25, 26, 27, 28, 29], 'NEG')]
    # R189: Strip CSGT
    elif rec_num == 189:
        c_trips = [([1, 2, 3, 4], [17, 18], 'NEU')]
    # R190: POS
    elif rec_num == 190:
        c_trips = [([50, 51], [52, 53, 54], 'POS')]
    # R191: POS
    elif rec_num == 191:
        c_trips = [([1, 2], [3, 4], 'POS')]
    # R192: ok
    elif rec_num == 192:
        c_trips = [([3, 4, 5, 6], [10, 11, 12, 13], 'NEG')]
    # R193: Clean aspect
    elif rec_num == 193:
        c_trips = [([0, 1], [2, 3], 'NEG')]
    # R194: Province / song lyrics -> REJECT
    elif rec_num == 194:
        c_trips = []
    # R195: Hanoi travel status -> REJECT
    elif rec_num == 195:
        c_trips = []
    # R196: Rule 9
    elif rec_num == 196:
        c_trips = [
            ([47, 48], [40, 41, 42, 43, 44], 'NEG'),
            ([51, 52, 53], [40, 41, 42, 43, 44], 'NEG'),
            ([55, 56], [40, 41, 42, 43, 44], 'NEG')
        ]
    # R197: POS
    elif rec_num == 197:
        c_trips = [([0, 1], [9, 10, 11, 12, 13, 14], 'POS')]
    # R198: NEU
    elif rec_num == 198:
        c_trips = [([6, 7], [8, 9], 'NEU')]
    # R199: ok
    elif rec_num == 199:
        c_trips = [([2, 3], [4], 'NEG')]
    # R200: ok
    elif rec_num == 200:
        c_trips = [([17, 18, 19], [34, 35, 36, 37, 38, 39], 'NEG')]
        
    curated_lines.append(f"{c_text}####{c_trips}")

assert len(curated_lines) == 100

# Write 100 lines batch 1 + 100 lines batch 2 to phase3.txt
out_path = 'data/validate_label/thuan/phase3.txt'
with open(out_path, 'r', encoding='utf-8') as f:
    existing_lines = [l.strip() for l in f if l.strip()]

batch1_lines = existing_lines[:100]
final_lines = batch1_lines + curated_lines

with open(out_path, 'w', encoding='utf-8') as out_f:
    for l in final_lines:
        out_f.write(l + '\n')

print(f'Wrote 100 lines for Batch 1 + 100 lines for Batch 2. Total lines in {out_path}: {len(final_lines)}')
