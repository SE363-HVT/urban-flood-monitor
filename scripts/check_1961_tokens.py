import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

text, trip_str = lines[1960].split('####')
old_tokens = text.split()
print("Rec 1961 old token [1]:", old_tokens[1])
print("Rec 1961 old token [45, 46]:", old_tokens[45], old_tokens[46])

new_text = text[len('Tại TPHCM , '):]
new_tokens = new_text.split()
print("Rec 1961 new token [0]:", new_tokens[0])
print("Rec 1961 new token [42, 43]:", new_tokens[42], new_tokens[43])
