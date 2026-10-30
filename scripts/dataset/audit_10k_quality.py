import json
import re

with open('data/processed/hcmc_flood_annotated_v3_multimodal.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

total_records = len(data)
print(f"==================================================")
print(f"       10K MASTER DATASET QUALITY AUDIT REPORT     ")
print(f"==================================================")
print(f"Total Records: {total_records}")
assert total_records > 10000, f"Total records {total_records} is not > 10,000!"

# 1. Check seq_id order and key positioning
seq_id_not_last = 0
seq_id_gaps = 0
for i, item in enumerate(data):
    keys = list(item.keys())
    if keys[-1] != 'seq_id':
        seq_id_not_last += 1
    if item.get('seq_id') != i:
        seq_id_gaps += 1

print(f"1. seq_id key position at end of dict: {total_records - seq_id_not_last}/{total_records} (Violations: {seq_id_not_last})")
print(f"2. seq_id continuous sequence (0 to {total_records-1}): {total_records - seq_id_gaps}/{total_records} (Gaps: {seq_id_gaps})")

# 2. Check triplets
total_triplets = 0
empty_triplet_records = 0
span_matched_aspect_mismatches = 0
opinion_mismatches = 0
span_overlaps = 0
invalid_polarities = 0
polarity_dist = {'POS': 0, 'NEG': 0, 'NEU': 0}

for i, item in enumerate(data):
    text = (item.get('content', {}).get('text', '') or '') + ' ' + (item.get('content', {}).get('title', '') or '')
    text_lower = text.lower()
    triplets = item.get('aste_triplets', [])
    
    if not triplets:
        empty_triplet_records += 1
        
    for t in triplets:
        total_triplets += 1
        pol = t.get('polarity')
        if pol in polarity_dist:
            polarity_dist[pol] += 1
        else:
            invalid_polarities += 1
            
        asp = t.get('aspect', '')
        op = t.get('opinion', '')
        prov = t.get('grounding_provenance', 'SPAN_MATCHED')
        
        # Check verbatim in text for SPAN_MATCHED
        if prov == 'SPAN_MATCHED' and asp.lower() not in text_lower:
            span_matched_aspect_mismatches += 1
            if span_matched_aspect_mismatches <= 5:
                print(f"  [SPAN_MATCHED Aspect mismatch] idx {i}, seq_id {item.get('seq_id')}: '{asp}' not in text")
                
        if op.lower() not in text_lower:
            opinion_mismatches += 1
            if opinion_mismatches <= 5:
                print(f"  [Opinion mismatch] idx {i}, seq_id {item.get('seq_id')}: '{op}' not in text")
                
        # Check exact overlap
        if asp.lower() == op.lower() or asp.lower() in op.lower() or op.lower() in asp.lower():
            span_overlaps += 1
            if span_overlaps <= 5:
                print(f"  [Span overlap] idx {i}, seq_id {item.get('seq_id')}: asp='{asp}', op='{op}'")

print(f"3. Total ASTE Triplets: {total_triplets}")
print(f"   - Polarity Distribution: NEG={polarity_dist['NEG']} ({polarity_dist['NEG']/total_triplets*100:.1f}%), POS={polarity_dist['POS']} ({polarity_dist['POS']/total_triplets*100:.1f}%), NEU={polarity_dist['NEU']} ({polarity_dist['NEU']/total_triplets*100:.1f}%)")
print(f"4. Empty Triplet Records: {empty_triplet_records}")
print(f"5. SPAN_MATCHED Aspect Mismatches: {span_matched_aspect_mismatches}")
print(f"6. Opinion Span Mismatches: {opinion_mismatches}")
print(f"7. Span Overlaps: {span_overlaps}")
print(f"8. Invalid Polarities: {invalid_polarities}")

# 3. Check for specific ad/BDS keywords from user screenshots
bds_ad_check = re.compile(
    r'(1tr8 máy lạnh|2 căn Huỳnh Tấn Phát.*4,5 Tỉ|sắm sửa thả ga - nhận quà ngập tràn|'
    r'quà ngập tràn|ưu đãi ngập tràn|voucher ngập tràn|deal ngập tràn|LocknLock x Vincom|'
    r'The Pizza Company|GRAND OPENING VIKINGS|Duy nhất tại Sachi Garden|'
    r'CO\.OPMART HUỲNH TẤN PHÁT LÊN KỆ|Cần bán Chung Cư Thái An)', 
    re.IGNORECASE
)
found_junk = 0
for i, item in enumerate(data):
    text = (item.get('content', {}).get('text', '') or '') + ' ' + (item.get('content', {}).get('title', '') or '')
    if bds_ad_check.search(text):
        found_junk += 1
        print(f"  [Remaining Junk] idx {i}, seq_id {item.get('seq_id')}: {text[:80]}")

print(f"9. Residual Junk / BDS / Ads: {found_junk}")
print(f"==================================================")
if (seq_id_not_last == 0 and seq_id_gaps == 0 and empty_triplet_records == 0 
    and span_matched_aspect_mismatches == 0 and opinion_mismatches == 0 
    and span_overlaps == 0 and invalid_polarities == 0 and found_junk == 0):
    print("STATUS: AUDIT PASSED 100% PERFECTLY!")
else:
    print("STATUS: AUDIT FOUND ISSUES!")
print(f"==================================================")
