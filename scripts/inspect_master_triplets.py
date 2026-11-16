# -*- coding: utf-8 -*-
import ast, re
from categorize_strict import potential_inscope

print(f"Tổng số ứng viên phục hồi: {len(potential_inscope)}")

# Kiểm tra triplet trong master của 811 records
valid_master_triplets = 0
invalid_master_triplets = 0
empty_master = 0

sample_inspections = []

for r in potential_inscope:
    m_trips = r['master_triplets']
    m_text = r['master_text']
    m_toks = m_text.split()
    
    if not m_trips:
        empty_master += 1
        continue
        
    # Giải mã triplets
    decoded = []
    has_err = False
    for asp_idx, opi_idx, pol in m_trips:
        try:
            asp_str = " ".join([m_toks[i] for i in asp_idx])
            opi_str = " ".join([m_toks[i] for i in opi_idx])
            decoded.append((asp_str, opi_str, pol))
        except Exception as e:
            has_err = True
            
    if has_err:
        invalid_master_triplets += 1
    else:
        valid_master_triplets += 1
        if len(sample_inspections) < 30:
            sample_inspections.append((r['rec_id'], m_text, decoded))

print(f"Master có triplets hợp lệ giải mã được: {valid_master_triplets}")
print(f"Master triplets bị lỗi index: {invalid_master_triplets}")
print(f"Master rỗng: {empty_master}")

print("\n--- XEM 15 MẪU ĐẦU TIÊN GIẢI MÃ TỪ MASTER ---")
for rec_id, text, trips in sample_inspections[:15]:
    print(f"\nREC {rec_id}:")
    print(f"  TEXT: {text[:100]}...")
    for asp, opi, pol in trips:
        print(f"    -> Aspect: [{asp}] | Opinion: [{opi}] | Pol: {pol}")
