import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import collections
import statistics

v3_path = "D:/SE363_RAWDATA/data/processed/hcmc_flood_annotated_v3_multimodal.json"
with open(v3_path, "r", encoding="utf-8") as f:
    data = json.load(f)

total_sentences = len(data)
all_triplets = [t for item in data for t in item.get("aste_triplets", [])]
total_triplets = len(all_triplets)

sent_lens_char = [len(x.get("content", {}).get("text", "")) for x in data]
sent_lens_word = [len(x.get("content", {}).get("text", "").split()) for x in data]
triplets_per_sent = [len(x.get("aste_triplets", [])) for x in data]

print("=== 1. QUY MÔ TỔNG THỂ ===")
print(f"Total Sentences: {total_sentences}")
print(f"Total Triplets: {total_triplets}")
print(f"Triplets/Sentence: Mean={statistics.mean(triplets_per_sent):.2f}, Median={statistics.median(triplets_per_sent)}, Max={max(triplets_per_sent)}")
print(f"Char length: Mean={statistics.mean(sent_lens_char):.1f}, Min={min(sent_lens_char)}, Max={max(sent_lens_char)}")
print(f"Word length: Mean={statistics.mean(sent_lens_word):.1f}, Min={min(sent_lens_word)}, Max={max(sent_lens_word)}")

print("\n=== 2. PHÂN BỐ SỐ LƯỢNG TRIPLET TRÊN MỖI CÂU ===")
triplet_counts = collections.Counter(triplets_per_sent)
for k in sorted(triplet_counts.keys()):
    print(f"  {k} triplets: {triplet_counts[k]} sentences ({triplet_counts[k]/total_sentences*100:.1f}%)")

print("\n=== 3. NỀN TẢNG (PLATFORM) ===")
plat_sents = collections.Counter(x.get("source", {}).get("platform", "unknown") for x in data)
plat_trips = collections.Counter(x.get("source", {}).get("platform", "unknown") for x in data for t in x.get("aste_triplets", []))
for p, c in plat_sents.most_common():
    print(f"  {p:10}: {c:5d} sentences ({c/total_sentences*100:5.1f}%) | {plat_trips[p]:5d} triplets ({plat_trips[p]/total_triplets*100:5.1f}%)")

print("\n=== 4. PHÂN BỐ CỰC TÍNH (POLARITY) ===")
pols = collections.Counter(t["polarity"] for t in all_triplets)
for pol, c in pols.most_common():
    print(f"  {pol:6}: {c:5d} ({c/total_triplets*100:5.2f}%)")

print("\n=== 5. PHÂN BỐ ASPECT CATEGORY ===")
cats = collections.Counter(t["aspect_category"] for t in all_triplets)
for cat, c in cats.most_common():
    print(f"  {cat:25}: {c:5d} ({c/total_triplets*100:5.2f}%)")

print("\n=== 6. MA TRẬN CATEGORY x POLARITY ===")
cat_pol = collections.defaultdict(lambda: collections.Counter())
for t in all_triplets:
    cat_pol[t["aspect_category"]][t["polarity"]] += 1
for cat, c in cats.most_common():
    print(f"  {cat:25} -> NEG: {cat_pol[cat]['NEG']:4d} ({cat_pol[cat]['NEG']/c*100:4.1f}%) | NEU: {cat_pol[cat]['NEU']:4d} ({cat_pol[cat]['NEU']/c*100:4.1f}%) | POS: {cat_pol[cat]['POS']:4d} ({cat_pol[cat]['POS']/c*100:4.1f}%)")

print("\n=== 7. PHÂN BỐ MỨC ĐỘ NGHIÊM TRỌNG (SEVERITY) ===")
sevs = collections.Counter(t.get("severity", "UNKNOWN") for t in all_triplets)
for s, c in sevs.most_common():
    print(f"  {s:12}: {c:5d} ({c/total_triplets*100:5.2f}%)")

print("\n=== 8. MA TRẬN CATEGORY x SEVERITY ===")
cat_sev = collections.defaultdict(lambda: collections.Counter())
for t in all_triplets:
    cat_sev[t["aspect_category"]][t.get("severity", "UNKNOWN")] += 1
for cat, c in cats.most_common():
    print(f"  {cat:25} -> HIGH: {cat_sev[cat]['HIGH']:4d} | MED: {cat_sev[cat]['MEDIUM']:4d} | LOW: {cat_sev[cat]['LOW']:4d} | REC: {cat_sev[cat]['RECOVERED']:4d}")

print("\n=== 9. ĐA PHƯƠNG TIỆN (MULTIMODAL) ===")
media_cnt = sum(1 for x in data if x.get("media", {}).get("has_media"))
print(f"  Has Media: {media_cnt} / {total_sentences} ({media_cnt/total_sentences*100:.1f}%)")

print("\n=== 10. PHÂN BỐ THEO EPISODE / ĐỢT TRIỀU ===")
ep_sents = collections.Counter(x.get("episode_id", "unknown") for x in data)
for ep, c in ep_sents.most_common(12):
    print(f"  {ep:35}: {c:5d} sents ({c/total_sentences*100:.1f}%)")

print("\n=== 11. TOP ASPECTS THEO TỪNG CATEGORY ===")
for cat, _ in cats.most_common():
    sub_asps = collections.Counter(t["aspect"] for t in all_triplets if t["aspect_category"] == cat)
    print(f"  [{cat}]")
    for asp, c in sub_asps.most_common(5):
        print(f"    - '{asp}': {c}")

print("\n=== 12. TOP OPINIONS THEO TỪNG CỰC TÍNH ===")
for pol in ["NEG", "NEU", "POS"]:
    sub_ops = collections.Counter(t["opinion"] for t in all_triplets if t["polarity"] == pol)
    print(f"  [{pol}]")
    for op, c in sub_ops.most_common(5):
        print(f"    - '{op}': {c}")

print("\n=== 13. KIỂM ĐỊNH CHẤT LƯỢNG (DATA QUALITY & INTEGRITY AUDIT) ===")
verbatim_errors = 0
for x in data:
    txt = x.get("content", {}).get("text", "")
    for t in x.get("aste_triplets", []):
        if t["aspect"] not in txt or t["opinion"] not in txt:
            verbatim_errors += 1
print(f"  - Verbatim substring errors: {verbatim_errors} (Target: 0)")

district_errors = 0
for t in all_triplets:
    if t["aspect"].lower().startswith("quận") or "quận " in t["aspect"].lower():
        district_errors += 1
print(f"  - District leakage errors (NQ 1685): {district_errors} (Target: 0)")

vehicle_keywords = ["xe máy", "ô tô", "xe buýt", "xe hơi", "phương tiện"]
vehicle_errors = sum(1 for t in all_triplets if t["aspect"].lower() in vehicle_keywords)
print(f"  - Vehicle aspect violations: {vehicle_errors} (Target: 0)")
