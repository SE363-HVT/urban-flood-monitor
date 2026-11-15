import subprocess
import sys
sys.stdout.reconfigure(encoding='utf-8')

cmd = ['git', 'diff', 'data/validate_label/thuan/phase2.txt']
diff_out = subprocess.check_output(cmd, text=True, encoding='utf-8')

# Let us find lines where triều cường ở TPHCM was changed
lines = diff_out.splitlines()
for i, l in enumerate(lines):
    if l.startswith('-') and 'triều cường ở TPHCM' in l and '####' in l:
        print(f"OLD: {l}")
        if i + 1 < len(lines):
            print(f"NEW: {lines[i+1]}")
        print("-" * 50)
