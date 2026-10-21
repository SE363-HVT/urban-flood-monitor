import sys
import os
import json
import random
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# Set fixed random seed for strict reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

MASTER_PATH = 'data/processed/hcmc_flood_annotated_v3_multimodal.json'
SPLITS_DIR = 'data/processed/splits'

os.makedirs(SPLITS_DIR, exist_ok=True)

# 1. Load Master Dataset (Read-only)
with open(MASTER_PATH, 'r', encoding='utf-8') as f:
    master_data = json.load(f)

total_count = len(master_data)
print(f"Loaded Master Dataset: {total_count} samples.")

# Target counts: 80% / 10% / 10%
target_test = 462
target_dev = 462
target_train = total_count - target_test - target_dev  # 3697

print(f"Target split counts -> Train: {target_train}, Dev: {target_dev}, Test: {target_test}")

# Group by parent_id to prevent data leakage (same article/post in same split)
grouped_by_parent = defaultdict(list)
for item in master_data:
    parent = item.get('parent_id') or item.get('id')
    grouped_by_parent[parent].append(item)

print(f"Total unique parent groups: {len(grouped_by_parent)}")

# Categorize each group by its primary characteristics for stratified allocation:
# (dominant_polarity, has_media, platform)
def get_group_signature(items):
    pols = defaultdict(int)
    has_media = False
    platform = items[0].get('source', {}).get('platform', 'unknown')
    
    for it in items:
        media = it.get('media', {})
        if media.get('has_media') or (media.get('media_urls') and len(media.get('media_urls')) > 0):
            has_media = True
        for t in it.get('aste_triplets', []):
            pols[t.get('polarity', 'NEU')] += 1
            
    dom_pol = 'NEU'
    if pols:
        # Prioritize rare classes (POS, then NEU, then NEG)
        if pols['POS'] > 0:
            dom_pol = 'POS'
        elif pols['NEU'] > 0:
            dom_pol = 'NEU'
        else:
            dom_pol = 'NEG'
            
    return (dom_pol, has_media, platform)

signature_groups = defaultdict(list)
for parent, items in grouped_by_parent.items():
    sig = get_group_signature(items)
    signature_groups[sig].append((parent, items))

train_items = []
dev_items = []
test_items = []

# Shuffle within each signature group deterministically
for sig, groups in signature_groups.items():
    random.shuffle(groups)
    for parent, items in groups:
        # Determine best allocation to maintain targets
        # Check current counts
        train_deficit = target_train - len(train_items)
        dev_deficit = target_dev - len(dev_items)
        test_deficit = target_test - len(test_items)
        
        # We need to fill test and dev up to target, remainder goes to train
        item_len = len(items)
        
        # Decide between test, dev, train based on deficit proportion
        if test_deficit >= item_len and (test_deficit / target_test) >= (dev_deficit / target_dev) and (test_deficit / target_test) >= (train_deficit / target_train):
            test_items.extend(items)
        elif dev_deficit >= item_len and (dev_deficit / target_dev) >= (train_deficit / target_train):
            dev_items.extend(items)
        else:
            if train_deficit > 0:
                train_items.extend(items)
            elif dev_deficit > 0:
                dev_items.extend(items)
            else:
                test_items.extend(items)

# Fine-adjust if sizes slightly exceed due to group boundaries
# If test or dev slightly differs from 462, move single-item groups between splits without breaking parents
def fine_tune_splits(train, dev, test, target_tr, target_dv, target_ts):
    # Map single items groups
    pass

print(f"\nInitial split sizes:")
print(f"  Train: {len(train_items)}")
print(f"  Dev:   {len(dev_items)}")
print(f"  Test:  {len(test_items)}")
print(f"  Total: {len(train_items) + len(dev_items) + len(test_items)}")

# Adjust so that Dev and Test are exactly 462 and Train is 3697, preserving parent groups
while len(dev_items) > target_dev:
    # Find a group in dev that can move to train
    # Find candidate
    moved = False
    for i in range(len(dev_items) - 1, -1, -1):
        pid = dev_items[i].get('parent_id') or dev_items[i].get('id')
        p_items = [it for it in dev_items if (it.get('parent_id') or it.get('id')) == pid]
        if len(dev_items) - len(p_items) >= target_dev:
            # Move p_items to train
            dev_items = [it for it in dev_items if (it.get('parent_id') or it.get('id')) != pid]
            train_items.extend(p_items)
            moved = True
            break
    if not moved:
        break

while len(test_items) > target_test:
    moved = False
    for i in range(len(test_items) - 1, -1, -1):
        pid = test_items[i].get('parent_id') or test_items[i].get('id')
        p_items = [it for it in test_items if (it.get('parent_id') or it.get('id')) == pid]
        if len(test_items) - len(p_items) >= target_test:
            test_items = [it for it in test_items if (it.get('parent_id') or it.get('id')) != pid]
            train_items.extend(p_items)
            moved = True
            break
    if not moved:
        break

while len(dev_items) < target_dev:
    moved = False
    for i in range(len(train_items) - 1, -1, -1):
        pid = train_items[i].get('parent_id') or train_items[i].get('id')
        p_items = [it for it in train_items if (it.get('parent_id') or it.get('id')) == pid]
        if len(dev_items) + len(p_items) <= target_dev:
            train_items = [it for it in train_items if (it.get('parent_id') or it.get('id')) != pid]
            dev_items.extend(p_items)
            moved = True
            break
    if not moved:
        break

while len(test_items) < target_test:
    moved = False
    for i in range(len(train_items) - 1, -1, -1):
        pid = train_items[i].get('parent_id') or train_items[i].get('id')
        p_items = [it for it in train_items if (it.get('parent_id') or it.get('id')) == pid]
        if len(test_items) + len(p_items) <= target_test:
            train_items = [it for it in train_items if (it.get('parent_id') or it.get('id')) != pid]
            test_items.extend(p_items)
            moved = True
            break
    if not moved:
        break

print(f"\nFinal exact split sizes:")
print(f"  Train: {len(train_items)} ({len(train_items)/total_count*100:.2f}%)")
print(f"  Dev:   {len(dev_items)} ({len(dev_items)/total_count*100:.2f}%)")
print(f"  Test:  {len(test_items)} ({len(test_items)/total_count*100:.2f}%)")
print(f"  Total: {len(train_items) + len(dev_items) + len(test_items)}")

# Helper to compute statistics for each split
def compute_stats(split_data):
    stats = {
        'total_samples': len(split_data),
        'total_triplets': 0,
        'polarity': defaultdict(int),
        'severity': defaultdict(int),
        'aspect_category': defaultdict(int),
        'platforms': defaultdict(int),
        'has_media': 0,
        'text_only': 0
    }
    for it in split_data:
        platform = it.get('source', {}).get('platform', 'unknown')
        stats['platforms'][platform] += 1
        
        media = it.get('media', {})
        if media.get('has_media') or (media.get('media_urls') and len(media.get('media_urls')) > 0):
            stats['has_media'] += 1
        else:
            stats['text_only'] += 1
            
        triplets = it.get('aste_triplets', [])
        stats['total_triplets'] += len(triplets)
        for t in triplets:
            stats['polarity'][t.get('polarity', 'UNKNOWN')] += 1
            stats['severity'][t.get('severity', 'UNKNOWN')] += 1
            stats['aspect_category'][t.get('aspect_category', 'UNKNOWN')] += 1
            
    # convert defaultdict to regular dict
    stats['polarity'] = dict(stats['polarity'])
    stats['severity'] = dict(stats['severity'])
    stats['aspect_category'] = dict(stats['aspect_category'])
    stats['platforms'] = dict(stats['platforms'])
    return stats

train_stats = compute_stats(train_items)
dev_stats = compute_stats(dev_items)
test_stats = compute_stats(test_items)

print("\n--- Split Statistics Check ---")
print("Train Polarity:", train_stats['polarity'])
print("Dev Polarity:  ", dev_stats['polarity'])
print("Test Polarity: ", test_stats['polarity'])

print("\nTrain Media:", train_stats['has_media'], "/", train_stats['total_samples'])
print("Dev Media:  ", dev_stats['has_media'], "/", dev_stats['total_samples'])
print("Test Media: ", test_stats['has_media'], "/", test_stats['total_samples'])

# Sort items by original seq_id for clean browsing
train_items.sort(key=lambda x: x.get('seq_id', 0))
dev_items.sort(key=lambda x: x.get('seq_id', 0))
test_items.sort(key=lambda x: x.get('seq_id', 0))

# Save split files
train_path = os.path.join(SPLITS_DIR, 'train.json')
dev_path = os.path.join(SPLITS_DIR, 'dev.json')
test_path = os.path.join(SPLITS_DIR, 'test.json')
meta_path = os.path.join(SPLITS_DIR, 'split_metadata.json')

with open(train_path, 'w', encoding='utf-8') as f:
    json.dump(train_items, f, ensure_ascii=False, indent=2)

with open(dev_path, 'w', encoding='utf-8') as f:
    json.dump(dev_items, f, ensure_ascii=False, indent=2)

with open(test_path, 'w', encoding='utf-8') as f:
    json.dump(test_items, f, ensure_ascii=False, indent=2)

metadata = {
    'dataset_name': 'HCMC Multimodal ASTE v3',
    'master_source_file': MASTER_PATH,
    'total_master_samples': total_count,
    'random_seed': RANDOM_SEED,
    'split_ratio': '80 / 10 / 10',
    'splits': {
        'train': {
            'file': 'train.json',
            'count': len(train_items),
            'stats': train_stats
        },
        'dev': {
            'file': 'dev.json',
            'count': len(dev_items),
            'stats': dev_stats
        },
        'test': {
            'file': 'test.json',
            'count': len(test_items),
            'stats': test_stats
        }
    }
}

with open(meta_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print(f"\nSUCCESS: Created all split files in {SPLITS_DIR}/ successfully!")
