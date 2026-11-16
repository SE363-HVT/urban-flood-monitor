# -*- coding: utf-8 -*-
import ast, re

def parse_859():
    with open('scratch_all_859_rejected.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    entries = content.split('=== REC ')
    records = []
    for entry in entries[1:]:
        lines = entry.strip().split('\n')
        first_line = lines[0].strip()
        rec_id = int(first_line.split('===')[0].strip())
        
        p3_line = ""
        master_line = ""
        for line in lines[1:]:
            if line.startswith('P3_TEXT:'):
                p3_line = line[len('P3_TEXT:'):].strip()
            elif line.startswith('MASTER:'):
                master_line = line[len('MASTER:'):].strip()
                
        p3_parts = p3_line.split('####')
        p3_text = p3_parts[0].strip()
        
        master_parts = master_line.split('####')
        master_text = master_parts[0].strip()
        master_triplets = []
        if len(master_parts) > 1 and master_parts[1].strip():
            try:
                master_triplets = ast.literal_eval(master_parts[1].strip())
            except:
                pass
                
        records.append({
            'rec_id': rec_id,
            'p3_text': p3_text,
            'master_text': master_text,
            'master_triplets': master_triplets
        })
    return records

if __name__ == '__main__':
    recs = parse_859()
    print(f"Parsed {len(recs)} records.")
    
    with_master_triplets = [r for r in recs if len(r['master_triplets']) > 0]
    without_master_triplets = [r for r in recs if len(r['master_triplets']) == 0]
    print(f"Records with master triplets: {len(with_master_triplets)}")
    print(f"Records without master triplets: {len(without_master_triplets)}")
