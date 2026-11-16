import ast, sys

sys.stdout.reconfigure(encoding='utf-8')

# Read raw batch 1
with open('scratch_batch1_dump.txt', 'r', encoding='utf-8') as f:
    blocks = [b.strip() for b in f.read().split('=== REC ') if b.strip()]

curated_lines = []

for idx, b in enumerate(blocks):
    rec_num = idx + 1
    header, line = b.split('\n', 1)
    text, trip_str = line.split('####')
    trips = ast.literal_eval(trip_str)
    
    # Defaults
    c_text = text
    c_trips = trips
    
    # 1. R1: Commercial sales post
    if rec_num == 1:
        c_trips = []
    # 2. R2: Rich opinion
    elif rec_num == 2:
        c_trips = [([16], [5, 6, 7, 8, 9, 10], 'NEG')]
    # 3. R3: ok
    elif rec_num == 3:
        c_trips = [([23, 24, 25, 26], [37, 38, 39, 40, 41, 42, 43, 44, 45], 'NEG'), ([51, 52, 53], [54, 55, 56], 'NEG')]
    # 4. R4: Fix invalid aspect in headline
    elif rec_num == 4:
        c_trips = [([27], [28, 29], 'NEG')]
    # 5. R5: ok
    elif rec_num == 5:
        c_trips = [([7, 8, 9], [25, 26], 'NEG'), ([32, 33, 34, 35], [41, 42, 43, 44, 45], 'NEG')]
    # 6. R6: ok
    elif rec_num == 6:
        c_trips = [([6, 7], [24, 25], 'NEG')]
    # 7. R7: ok
    elif rec_num == 7:
        c_trips = [([12, 13, 14, 15], [6, 7], 'NEG'), ([17, 18, 19], [6, 7], 'NEG'), ([21, 22, 23], [6, 7], 'NEG')]
    # 8. R8: ok
    elif rec_num == 8:
        c_trips = [([26, 27, 28, 29], [34, 35], 'NEG'), ([31, 32, 33], [34, 35], 'NEG')]
    # 9. R9: Clean duplicate aspect
    elif rec_num == 9:
        c_trips = [([31, 32], [36, 37, 38, 39], 'NEU')]
    # 10. R10: POS
    elif rec_num == 10:
        c_trips = [([19, 20, 21, 22, 23], [10, 11, 12, 13, 14, 15], 'POS')]
    # 11. R11: Clean multi invalid
    elif rec_num == 11:
        c_trips = [([27], [28, 29], 'NEG')]
    # 12. R12: ok
    elif rec_num == 12:
        c_trips = [([0, 1, 2, 3], [18, 19], 'NEG')]
    # 13. R13: Clean aspect
    elif rec_num == 13:
        c_trips = [([8, 9], [4], 'NEG')]
    # 14. R14: Rich opinion without edge punct
    elif rec_num == 14:
        c_trips = [([20, 21, 22, 23], [29, 30, 31, 32, 33, 34, 35], 'NEG')]
    # 15. R15: Rule 9 exact token bounds
    elif rec_num == 15:
        c_trips = [([20, 21], [15], 'NEG'), ([23, 24], [15], 'NEG')]
    # 16. R16: ok
    elif rec_num == 16:
        c_trips = [([5, 6], [7, 8], 'NEG')]
    # 17. R17: Clean opinion
    elif rec_num == 17:
        c_trips = [([33, 34, 35], [22, 23, 24, 25], 'NEG')]
    # 18. R18: ok
    elif rec_num == 18:
        c_trips = [([13, 14], [6, 7, 8, 9], 'NEG')]
    # 19. R19: ok
    elif rec_num == 19:
        c_trips = [([11, 12], [13, 14], 'NEG')]
    # 20. R20: Strip prep
    elif rec_num == 20:
        c_trips = [([14, 15], [7, 8, 9, 10, 11, 12], 'NEG')]
    # 21. R21: POS
    elif rec_num == 21:
        c_trips = [([59, 60, 61, 62, 63], [50, 51, 52, 53, 54, 55], 'POS')]
    # 22. R22: Rich opinion
    elif rec_num == 22:
        c_trips = [([0], [2, 3, 4, 5, 6], 'NEG')]
    # 23. R23: Strip prep
    elif rec_num == 23:
        c_trips = [([3, 4], [8, 9, 10, 11, 12, 13], 'NEU')]
    # 24. R24: Forecast NEU
    elif rec_num == 24:
        c_trips = [([0, 1, 2, 3], [20, 21, 22, 23], 'NEU')]
    # 25. R25: Strip prep tại
    elif rec_num == 25:
        c_trips = [([22, 23], [28, 29], 'NEG')]
    # 26. R26: in-place bare trieucuong
    elif rec_num == 26:
        c_text = text.replace('triều cường đang', 'triều cường ở TPHCM đang')
        c_trips = [([48, 49, 50, 51], [52, 53, 54, 55], 'NEU')]
    # 27. R27: ok
    elif rec_num == 27:
        c_trips = [([3, 4], [25], 'NEG')]
    # 28. R28: ok
    elif rec_num == 28:
        c_trips = [([0, 1, 2, 3], [4, 5], 'NEG')]
    # 29. R29: ok
    elif rec_num == 29:
        c_trips = [([12], [5, 6, 7], 'NEG')]
    # 30. R30: ok
    elif rec_num == 30:
        c_trips = [([15, 16], [11, 12, 13], 'NEG')]
    # 31. R31: ok
    elif rec_num == 31:
        c_trips = [([11, 12, 13], [21, 22, 23], 'NEG')]
    # 32. R32: Anti over-tagging
    elif rec_num == 32:
        c_trips = [([0, 1], [5, 6], 'NEG')]
    # 33. R33: ok
    elif rec_num == 33:
        c_trips = [([5, 6, 7, 8], [22, 23, 24], 'NEG')]
    # 34. R34: Clean aspect
    elif rec_num == 34:
        c_trips = [([11, 12], [7], 'NEG')]
    # 35. R35: ok
    elif rec_num == 35:
        c_trips = [([8, 9, 10], [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25], 'NEG')]
    # 36. R36: Strip prep Tại
    elif rec_num == 36:
        c_trips = [([3, 4, 5, 6], [22, 23], 'NEG')]
    # 37. R37: ok
    elif rec_num == 37:
        c_trips = [([55, 56], [50, 51], 'NEG'), ([58, 59, 60], [50, 51], 'NEG')]
    # 38. R38: ok
    elif rec_num == 38:
        c_trips = [([7, 8], [20, 21], 'NEG')]
    # 39. R39: Rich opinion
    elif rec_num == 39:
        c_trips = [([10, 11], [0, 1, 2, 3, 4, 5, 6, 7], 'NEG')]
    # 40. R40: ok
    elif rec_num == 40:
        c_trips = [([0, 1, 2, 3], [4, 5], 'NEG')]
    # 41. R41: ok
    elif rec_num == 41:
        c_trips = [([10, 11, 12], [18, 19], 'NEG')]
    # 42. R42: Joke poem -> REJECT
    elif rec_num == 42:
        c_trips = []
    # 43. R43: ok
    elif rec_num == 43:
        c_trips = [([14, 15, 16, 17], [8, 9], 'NEG')]
    # 44. R44: ok
    elif rec_num == 44:
        c_trips = [([2, 3], [9, 10, 11, 12], 'NEG')]
    # 45. R45: Rule 9
    elif rec_num == 45:
        c_trips = [
            ([0, 1, 2, 3], [30, 31], 'NEG'),
            ([5, 6, 7], [30, 31], 'NEG'),
            ([9, 10, 11], [30, 31], 'NEG'),
            ([18, 19, 20, 21], [30, 31], 'NEG')
        ]
    # 46. R46: Opinion ngập
    elif rec_num == 46:
        c_trips = [([13], [5], 'NEG')]
    # 47. R47: POS
    elif rec_num == 47:
        c_trips = [([9], [13, 14], 'POS')]
    # 48. R48: Forecast NEU
    elif rec_num == 48:
        c_trips = [([11], [12, 13, 14], 'NEU')]
    # 49. R49: ok
    elif rec_num == 49:
        c_trips = [([6], [12, 13, 14, 15], 'NEG')]
    # 50. R50: ok
    elif rec_num == 50:
        c_trips = [([2], [9], 'NEG')]
    # 51. R51: ok
    elif rec_num == 51:
        c_trips = [([12], [9, 10], 'NEG')]
    # 52. R52: Forecast NEU
    elif rec_num == 52:
        c_trips = [([0], [10, 11, 12], 'NEU')]
    # 53. R53: ok
    elif rec_num == 53:
        c_trips = [([26, 27, 28], [42, 43], 'NEG')]
    # 54. R54: Project POS
    elif rec_num == 54:
        c_trips = [([7, 8], [2, 3], 'POS')]
    # 55. R55: ok
    elif rec_num == 55:
        c_trips = [([18], [7, 8], 'NEG')]
    # 56. R56: Clean entity
    elif rec_num == 56:
        c_trips = [([10, 11], [6, 7], 'NEG')]
    # 57. R57: Clean hashtag entity
    elif rec_num == 57:
        c_trips = [([10, 11], [24, 25], 'NEG')]
    # 58. R58: ok
    elif rec_num == 58:
        c_trips = [([12, 13], [2, 3], 'NEG')]
    # 59. R59: Rule 9 clean overlap
    elif rec_num == 59:
        c_trips = [([9, 10, 11], [4, 5], 'NEG'), ([13, 14], [4, 5], 'NEG')]
    # 60. R60: Forecast NEU
    elif rec_num == 60:
        c_trips = [([0, 1], [22, 23, 24, 25], 'NEU')]
    # 61. R61: POS
    elif rec_num == 61:
        c_trips = [([0, 1], [9, 10], 'POS')]
    # 62. R62: ok
    elif rec_num == 62:
        c_trips = [([10, 11, 12, 13], [21, 22, 23, 24, 25], 'NEG')]
    # 63. R63: Troll/meme -> REJECT
    elif rec_num == 63:
        c_trips = []
    # 64. R64: Clean duplicate
    elif rec_num == 64:
        c_trips = [([0, 1], [2, 3], 'NEG')]
    # 65. R65: ok
    elif rec_num == 65:
        c_trips = [([1, 2, 3], [0], 'NEG')]
    # 66. R66: POS
    elif rec_num == 66:
        c_trips = [([6, 7, 8, 9], [40, 41, 42, 43, 44, 45], 'POS')]
    # 67. R67: POS
    elif rec_num == 67:
        c_trips = [([0, 1], [7, 8], 'POS')]
    # 68. R68: Multi-level
    elif rec_num == 68:
        c_trips = [([3, 4], [28], 'NEG')]
    # 69. R69: Rich opinion
    elif rec_num == 69:
        c_trips = [([3], [0, 1, 2], 'NEG')]
    # 70. R70: Clean entity
    elif rec_num == 70:
        c_trips = [([13, 14], [34, 35], 'NEG')]
    # 71. R71: ok
    elif rec_num == 71:
        c_trips = [([9, 10], [26, 27], 'NEG')]
    # 72. R72: ok
    elif rec_num == 72:
        c_trips = [([0, 1], [8, 9, 10], 'NEG')]
    # 73. R73: Pump sales ad -> REJECT
    elif rec_num == 73:
        c_trips = []
    # 74. R74: Clean adverb
    elif rec_num == 74:
        c_trips = [([8], [9, 10, 11], 'NEG')]
    # 75. R75: Singer live -> REJECT
    elif rec_num == 75:
        c_trips = []
    # 76. R76: Remove redundant prefix
    elif rec_num == 76:
        c_text = 'Lý Phục Man Quận 7 Có Ngập Không'
        c_trips = [([0, 1, 2], [5, 6, 7], 'NEU')]
    # 77. R77: Clean hashtag duplicate
    elif rec_num == 77:
        c_trips = [([8, 9], [4, 5, 6, 7], 'NEG')]
    # 78. R78: Singer trailer -> REJECT
    elif rec_num == 78:
        c_trips = []
    # 79. R79: ok
    elif rec_num == 79:
        c_trips = [([0, 1, 2, 3], [8], 'NEG')]
    # 80. R80: ok
    elif rec_num == 80:
        c_trips = [([2], [10, 11], 'NEG')]
    # 81. R81: POS
    elif rec_num == 81:
        c_trips = [([0, 1], [3, 4, 5, 6, 7], 'POS')]
    # 82. R82: Clean adverb
    elif rec_num == 82:
        c_trips = [([9], [11, 12], 'NEG')]
    # 83. R83: ok
    elif rec_num == 83:
        c_trips = [([5], [31, 32, 33, 34], 'NEG')]
    # 84. R84: Strip CSGT
    elif rec_num == 84:
        c_trips = [([7, 8], [9, 10], 'NEG')]
    # 85. R85: ok
    elif rec_num == 85:
        c_trips = [([4], [5], 'NEG')]
    # 86. R86: Forecast NEU
    elif rec_num == 86:
        c_trips = [([2], [12, 13, 14, 15], 'NEU')]
    # 87. R87: Strip duplicate city
    elif rec_num == 87:
        c_trips = [([9, 10, 11], [3], 'NEG')]
    # 88. R88: ok
    elif rec_num == 88:
        c_trips = [([10, 11], [5, 6], 'NEG')]
    # 89. R89: ok
    elif rec_num == 89:
        c_trips = [([31, 32], [5, 6], 'NEG')]
    # 90. R90: POS
    elif rec_num == 90:
        c_trips = [([1, 2], [10, 11], 'POS')]
    # 91. R91: Opinion ngập
    elif rec_num == 91:
        c_trips = [([13], [5], 'NEG')]
    # 92. R92: Clean aspect & strip comma
    elif rec_num == 92:
        c_trips = [([17], [8, 9], 'NEG')]
    # 93. R93: ok
    elif rec_num == 93:
        c_trips = [([6, 7], [32, 33], 'NEG')]
    # 94. R94: ok
    elif rec_num == 94:
        c_trips = [([19, 20], [31, 32], 'NEG')]
    # 95. R95: ok
    elif rec_num == 95:
        c_trips = [([3, 4], [5, 6], 'NEG')]
    # 96. R96: ok
    elif rec_num == 96:
        c_trips = [([6, 7, 8, 9, 10], [11, 12], 'NEG'), ([14, 15, 16, 17], [18, 19, 20], 'NEG')]
    # 97. R97: ok
    elif rec_num == 97:
        c_trips = [([4, 5], [11, 12], 'NEG')]
    # 98. R98: Rule 9 clean prepositions and trailing punct
    elif rec_num == 98:
        c_trips = [
            ([3, 4], [5, 6, 7, 8], 'NEG'),
            ([11, 12], [13, 14, 15, 16, 17], 'NEG'),
            ([20, 21, 22], [23, 24, 25, 26, 27, 28], 'NEG')
        ]
    # 99. R99: ok
    elif rec_num == 99:
        c_trips = [([20, 21], [56, 57], 'NEG')]
    # 100. R100: Strip duplicate city
    elif rec_num == 100:
        c_trips = [([10, 11], [13, 14], 'NEG')]
        
    curated_lines.append(f"{c_text}####{c_trips}")

out_path = 'data/validate_label/thuan/phase3.txt'
with open(out_path, 'w', encoding='utf-8') as out_f:
    for l in curated_lines:
        out_f.write(l + '\n')

print(f'Wrote {len(curated_lines)} lines to {out_path}')
