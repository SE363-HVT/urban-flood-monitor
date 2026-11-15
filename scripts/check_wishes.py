import sys
import ast
sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if idx >= 1880: break
        parts = line.strip().split('####')
        text = parts[0].strip()
        tokens = text.split()
        trips = ast.literal_eval(parts[1].strip()) if len(parts) > 1 else []
        if 'mong' in text.lower() or 'ước' in text.lower() or 'hy vọng' in text.lower():
            print(f"Line {idx+1}: {text} #### {trips}")
