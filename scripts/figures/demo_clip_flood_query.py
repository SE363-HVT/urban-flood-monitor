#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/demo_clip_flood_query.py
--------------------------------------------------------------------------------
Demo script: Zero-shot visual flood verification with local frozen CLIP (ViT-B/32).
Runs 100% on CPU with low RAM footprint (~600MB).
Streams real post media in-memory from data/processed/hcmc_flood_annotated_v3_multimodal.json.
"""

import os
import sys
import io
import time
import json
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from pipeline.multimodal_streamer import stream_thumbnail_in_memory

DATASET_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "hcmc_flood_annotated_v3_multimodal.json")
MODEL_ID = "openai/clip-vit-base-patch32"

CANDIDATE_LABELS = [
    "a flooded street in a city with deep standing water and submerged vehicles",  # Index 0: Flood
    "a normal dry city road with clear traffic",                                   # Index 1: Dry/Normal
    "an indoor room, food dish, or personal selfie"                                # Index 2: Irrelevant
]


def load_clip_cpu():
    print(f"[*] Loading local CLIP model ({MODEL_ID}) on CPU...")
    start_t = time.time()
    model = CLIPModel.from_pretrained(MODEL_ID, use_safetensors=False, local_files_only=True).to("cpu")
    processor = CLIPProcessor.from_pretrained(MODEL_ID, local_files_only=True)
    model.eval()
    print(f"    Loaded in {time.time() - start_t:.2f}s! Memory footprint: ~600MB RAM\n")
    return model, processor


def evaluate_post(model, processor, post):
    post_id = post.get("id")
    content = post.get("content", {})
    text = content.get("text") if isinstance(content, dict) else str(content)
    source = post.get("source", {})
    video_url = source.get("url") if isinstance(source, dict) else None
    gold_triplets = post.get("aste_triplets", [])

    print("-" * 75)
    print(f"📌 Post ID: {post_id}")
    print(f"📝 Text: {text}")
    print(f"🔗 Video URL: {video_url}")
    print(f"🏷️  Gold ASTE: {gold_triplets}")

    if not video_url:
        print("⚠️  No canonical video URL available for in-memory streaming.\n")
        return

    # In-memory streaming (0 MB disk)
    t0 = time.time()
    img_bytes = stream_thumbnail_in_memory(video_url)
    if not img_bytes:
        print("❌ Could not stream keyframe from URL.\n")
        return

    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    stream_time = round((time.time() - t0) * 1000, 1)

    # CLIP Zero-shot classification
    t1 = time.time()
    inputs = processor(text=CANDIDATE_LABELS, images=image, return_tensors="pt", padding=True).to("cpu")
    with torch.no_grad():
        outputs = model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1).squeeze().tolist()
    infer_time = round((time.time() - t1) * 1000, 1)

    flood_prob = probs[0]
    is_flood = flood_prob >= 0.50

    print(f"⏱️  Stream Latency: {stream_time}ms | CLIP Inference (CPU): {infer_time}ms")
    print(f"📊 CLIP Probabilities:")
    print(f"    • [Flood]        {probs[0]*100:6.2f}% -> {CANDIDATE_LABELS[0]}")
    print(f"    • [Dry/Normal]   {probs[1]*100:6.2f}% -> {CANDIDATE_LABELS[1]}")
    print(f"    • [Irrelevant]   {probs[2]*100:6.2f}% -> {CANDIDATE_LABELS[2]}")
    print(f"🎯 Visual Flood Verification: {'✅ CONFIRMED FLOOD' if is_flood else '❌ NOT FLOODED'} (Confidence: {flood_prob:.2f})\n")


def main():
    if not os.path.exists(DATASET_FILE):
        print(f"Error: {DATASET_FILE} not found.")
        return

    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    model, processor = load_clip_cpu()

    # Select two contrasting examples: one severe flood (NEG) and one dry/recovery (POS)
    targets = ["tiktok_7683866511827684615", "tiktok_7688292338795400468"]
    selected = [item for item in data if item.get("id") in targets]

    print(f"[*] Running live query on {len(selected)} samples from {DATASET_FILE}:\n")
    for item in selected:
        evaluate_post(model, processor, item)


if __name__ == "__main__":
    main()
