import subprocess
import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

# Read current file
with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    cur_lines = [l.strip() for l in f if l.strip()]

# Read git HEAD file
git_head_bytes = subprocess.check_output(['git', 'show', 'HEAD:data/validate_label/thuan/phase2.txt'])
head_lines = [l.strip() for l in git_head_bytes.decode('utf-8').splitlines() if l.strip()]

print(f"Total lines: cur={len(cur_lines)}, head={len(head_lines)}")

# Compare lines 1630 to 2000
for i in range(1630, 2000):
    c_line = cur_lines[i]
    h_line = head_lines[i]
    if c_line != h_line:
        c_text, c_trip = c_line.split('####')
        h_text, h_trip = h_line.split('####')
        tokens = c_text.split()
        c_t = ast.literal_eval(c_trip)
        h_t = ast.literal_eval(h_trip)
        
        # Check if difference involves triều cường ở TPHCM or Bình Dương or rich opinion
        has_tc = 'triều cường ở tphcm' in c_text.lower()
        has_bd = any(k in c_text.lower() for k in ['bình dương', 'dĩ an', 'thuận an', 'thủ dầu một', '550', 'vũng tàu'])
        has_len_diff = len(c_trip) != len(h_trip)
        
        print(f"\nLine {i+1} (idx {i}):")
        print(f"  TEXT: {c_text}")
        print(f"  HEAD: {h_trip}")
        for t in h_t:
            print(f"    [HEAD] Asp: '{' '.join(tokens[x] for x in t[0])}' | Op: '{' '.join(tokens[x] for x in t[1])}' | {t[2]}")
        print(f"  CURR: {c_trip}")
        for t in c_t:
            print(f"    [CURR] Asp: '{' '.join(tokens[x] for x in t[0])}' | Op: '{' '.join(tokens[x] for x in t[1])}' | {t[2]}")
