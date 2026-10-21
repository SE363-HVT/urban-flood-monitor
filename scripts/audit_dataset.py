import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

with open('data/processed/hcmc_flood_annotated_v3_multimodal.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total items: {len(data)}")

bad_aspect_not_in_text = []
bad_opinion_not_in_text = []
generic_aspects = {}
overlap_list = []
empty_list = []

GENERIC_WORDS = {
    'đường', 'nhiều tuyến đường', 'các tuyến đường', 'tuyến đường',
    'xe', 'phương tiện', 'khu vực', 'người dân', 'dòng xe',
    'các con đường', 'nhiều đoạn đường', 'một số tuyến đường',
    'nhiều đường', 'các đường', 'đoạn đường'
}

for i, item in enumerate(data):
    sid = item.get('seq_id', i)
    id_val = item.get('id', '')
    text = item.get('content', {}).get('text', '')
    triplets = item.get('aste_triplets', [])
    
    if not triplets:
        empty_list.append((i, sid, id_val, text[:60]))
        continue
        
    for t in triplets:
        asp = t.get('aspect', '')
        op = t.get('opinion', '')
        prov = t.get('grounding_provenance', '')
        
        if prov == 'SPAN_MATCHED' and asp not in text:
            bad_aspect_not_in_text.append((i, sid, id_val, asp, text[:60]))
            
        if op not in text:
            bad_opinion_not_in_text.append((i, sid, id_val, op, text[:60]))
            
        if asp.lower() in GENERIC_WORDS:
            generic_aspects[asp] = generic_aspects.get(asp, 0) + 1
            
        if asp.lower() in op.lower() or op.lower() in asp.lower():
            overlap_list.append((i, sid, id_val, asp, op))

print("--- Summary of Current Dataset ---")
print(f"Empty triplets records: {len(empty_list)}")
print(f"Bad aspect not in text: {len(bad_aspect_not_in_text)}")
if bad_aspect_not_in_text:
    print("Sample bad aspects not in text:")
    for x in bad_aspect_not_in_text[:5]:
        print(f"  idx {x[0]} (seq_id {x[1]}, id {x[2]}): asp='{x[3]}' | text='{x[4]}'")

print(f"Bad opinion not in text: {len(bad_opinion_not_in_text)}")
if bad_opinion_not_in_text:
    print("Sample bad opinions not in text:")
    for x in bad_opinion_not_in_text[:5]:
        print(f"  idx {x[0]} (seq_id {x[1]}, id {x[2]}): op='{x[3]}' | text='{x[4]}'")

print(f"Generic aspects count: {sum(generic_aspects.values())}")
for k, v in generic_aspects.items():
    print(f"  '{k}': {v}")

print(f"Aspect-Opinion Overlaps: {len(overlap_list)}")
if overlap_list:
    print("Sample overlaps:")
    for x in overlap_list[:5]:
        print(f"  idx {x[0]} (seq_id {x[1]}): asp='{x[3]}' | op='{x[4]}'")
