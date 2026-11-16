import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    with open('scratch_batch5_tokens.txt', 'r', encoding='utf-16') as f:
        content = f.read()
except:
    with open('scratch_batch5_tokens.txt', 'r', encoding='utf-8') as f:
        content = f.read()

recs = content.split('=== REC ')
def show_recs(start, end):
    for r in recs:
        if not r.strip():
            continue
        num_str = r.split(' ===')[0]
        try:
            num = int(num_str)
            if start <= num <= end:
                print(f"=== REC {r.strip()}\n" + "="*80)
        except:
            pass

start = int(sys.argv[1]) if len(sys.argv) > 1 else 401
end = int(sys.argv[2]) if len(sys.argv) > 2 else 425
show_recs(start, end)
