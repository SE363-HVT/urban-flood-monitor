import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    with open('scratch_batch3_analysis.txt', 'r', encoding='utf-16') as f:
        text = f.read()
except:
    with open('scratch_batch3_analysis.txt', 'r', encoding='utf-8') as f:
        text = f.read()

records = text.split('[')

def view_range(start, end):
    for r in records:
        if not r.strip():
            continue
        num_str = r.split(']')[0]
        try:
            num = int(num_str)
            if start <= num <= end:
                print(f"[{r.strip()}\n" + "-"*60)
        except:
            pass

start = int(sys.argv[1]) if len(sys.argv) > 1 else 201
end = int(sys.argv[2]) if len(sys.argv) > 2 else 220
view_range(start, end)
