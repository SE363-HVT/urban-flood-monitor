import sys
import re
import ast

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'data/validate_label/thuan/phase2.txt'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

prefixes = ['Tại TP. Hồ Chí Minh , ', 'Tại TPHCM , ', 'Tại TP.HCM , ']

# Let's inspect all prefix records
# 1. First, any record where existing triplets target body (59 records) -> clearly has location!
# 2. What about the other prefix records? Let's check which ones have actual place names!

candidates = []
for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip_str = line.split('####')
    triplets = ast.literal_eval(trip_str)
    
    pfx = None
    shift = 0
    if text.startswith('Tại TP. Hồ Chí Minh , '):
        pfx = 'Tại TP. Hồ Chí Minh , '
        shift = 6
    elif text.startswith('Tại TPHCM , '):
        pfx = 'Tại TPHCM , '
        shift = 3
    elif text.startswith('Tại TP.HCM , '):
        pfx = 'Tại TP.HCM , '
        shift = 4
        
    if not pfx:
        continue
        
    body = text[len(pfx):]
    
    # Check if existing triplets target body
    triplet_targets_body = any(any(i >= shift for i in asp) for asp, opi, pol in triplets)
    
    candidates.append({
        'rec_num': rec_num,
        'pfx': pfx,
        'shift': shift,
        'text': text,
        'body': body,
        'triplets': triplets,
        'triplet_targets_body': triplet_targets_body
    })

print(f"Total prefix records: {len(candidates)}")
print(f"Prefix records with triplets targeting body: {len([c for c in candidates if c['triplet_targets_body']])}")

# Now let's check the remaining prefix records (where triplets only targeted prefix [1] or [1,2,3,4]):
# Do any of them actually contain a specific road or district?
