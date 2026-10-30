#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/run_live_multimodal_pipeline.py
--------------------------------------------------------------------------------
Full End-to-End Live Multimodal AI Pipeline:
1. Video Ingestion: Live stream video from URL (yt-dlp)
2. Video Decoding: OpenCV extracts top-3 keyframes
3. Audio Demuxing: FFmpeg extracts 16kHz mono audio WAV
4. Vision AI: CLIP ViT-B/32 zero-shot flood verification + 512D embeddings
5. Audio AI: PhoWhisper-base speech-to-text transcript
6. ASTE AI: BARTpho-syllable generative triplet extraction on fused multimodal content
"""

import os
import sys
import time
import json
import subprocess
import torch
from PIL import Image
import cv2
import wave
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from transformers import (
    CLIPProcessor, CLIPModel,
    WhisperProcessor, WhisperForConditionalGeneration,
    AutoTokenizer, MBartForConditionalGeneration
)

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

def main():
    # 0. Select Target Post from Dataset
    target_post = {
        "id": "tiktok_7683908042328427792",
        "url": "https://www.tiktok.com/@dantri.com.vn/video/7683908042328427792",
        "caption": "Khu vực gần chợ Thủ Đức ngập sâu, xe chết máy hàng loạt #dantrinews #xuhuong #LearnOnTikTok"
    }

    print("=" * 80)
    print("🚀 LIVE MULTIMODAL INGESTION & AI INFERENCE BENCHMARK")
    print(f"📌 Post ID: {target_post['id']}")
    print(f"🔗 Video URL: {target_post['url']}")
    print(f"📝 Raw Caption: {target_post['caption']}")
    print(f"🖥️  Compute Device: {DEVICE} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print("=" * 80)

    work_dir = os.path.join(PROJECT_ROOT, "data", "extracted_frames", "live_run_test")
    os.makedirs(work_dir, exist_ok=True)
    video_path = os.path.join(work_dir, "input_video.mp4")
    audio_path = os.path.join(work_dir, "input_audio.wav")

    stage_timings = {}
    total_start = time.time()

    # -------------------------------------------------------------------------
    # STAGE 1: Live Video Ingestion (yt-dlp)
    # -------------------------------------------------------------------------
    print("\n[*] Stage 1: Ingesting video stream from live URL (yt-dlp)...")
    t0 = time.time()
    cmd_dl = [
        sys.executable, "-m", "yt_dlp",
        "-f", "best[ext=mp4]/best",
        "-o", video_path,
        "--no-playlist",
        "--quiet",
        target_post["url"]
    ]
    subprocess.run(cmd_dl, check=True)
    stage_timings["1_video_download_ms"] = round((time.time() - t0) * 1000, 2)
    vid_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"    -> Done in {stage_timings['1_video_download_ms']:.1f}ms! Downloaded {vid_size_mb:.2f} MB")

    # -------------------------------------------------------------------------
    # STAGE 2: Video Decoding & Keyframe Extraction (OpenCV)
    # -------------------------------------------------------------------------
    print("\n[*] Stage 2: Decoding video & extracting top-3 representative keyframes (OpenCV)...")
    t0 = time.time()
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    duration_s = total_frames / fps
    indices = [int(total_frames * 0.25), int(total_frames * 0.50), int(total_frames * 0.75)]
    
    extracted_frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frame_path = os.path.join(work_dir, f"frame_{idx:04d}.jpg")
            cv2.imwrite(frame_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            extracted_frames.append(frame_path)
    cap.release()
    stage_timings["2_opencv_keyframe_ms"] = round((time.time() - t0) * 1000, 2)
    print(f"    -> Done in {stage_timings['2_opencv_keyframe_ms']:.1f}ms! Extracted 3 frames (Duration: {duration_s:.1f}s)")

    # -------------------------------------------------------------------------
    # STAGE 3: Audio Demuxing & Resampling (FFmpeg -> 16kHz mono)
    # -------------------------------------------------------------------------
    print("\n[*] Stage 3: Demuxing audio track & resampling to 16kHz mono (FFmpeg)...")
    t0 = time.time()
    cmd_audio = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        audio_path
    ]
    subprocess.run(cmd_audio, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    stage_timings["3_ffmpeg_audio_ms"] = round((time.time() - t0) * 1000, 2)
    aud_size_kb = os.path.getsize(audio_path) / 1024
    print(f"    -> Done in {stage_timings['3_ffmpeg_audio_ms']:.1f}ms! Extracted audio: {aud_size_kb:.1f} KB")

    # -------------------------------------------------------------------------
    # STAGE 4: Vision AI - CLIP ViT-B/32 (Verification + 512D Embeddings)
    # -------------------------------------------------------------------------
    print("\n[*] Stage 4: Running Vision AI (CLIP ViT-B/32) on top-3 keyframes...")
    t0 = time.time()
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32", local_files_only=True).to(DEVICE)
    clip_proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32", local_files_only=True)
    clip_model.eval()

    labels = [
        "a flooded street in a city with deep standing water and submerged vehicles",
        "a normal dry city road with clear traffic",
        "an indoor room, food dish, or personal selfie"
    ]
    pil_images = [Image.open(fp).convert("RGB") for fp in extracted_frames]
    inputs_clip = clip_proc(text=labels, images=pil_images, return_tensors="pt", padding=True).to(DEVICE)

    with torch.no_grad():
        outputs_clip = clip_model(**inputs_clip)
        # Softmax over candidate labels for each frame
        probs_per_frame = outputs_clip.logits_per_image.softmax(dim=1).cpu().tolist()
        # Visual embeddings (batch_size, 512)
        visual_features = outputs_clip.image_embeds.cpu()

    # Average flood confidence across top-3 frames
    avg_flood_prob = sum(p[0] for p in probs_per_frame) / len(probs_per_frame)
    stage_timings["4_clip_vision_ms"] = round((time.time() - t0) * 1000, 2)
    print(f"    -> Done in {stage_timings['4_clip_vision_ms']:.1f}ms!")
    print(f"    • Visual Flood Confidence: {avg_flood_prob * 100:.2f}%")
    print(f"    • Visual Feature Shape: {list(visual_features.shape)} (512D embeddings)")

    # -------------------------------------------------------------------------
    # STAGE 5: Audio AI - PhoWhisper-base Speech-to-Text
    # -------------------------------------------------------------------------
    print("\n[*] Stage 5: Running Audio AI (PhoWhisper-base) speech-to-text on 16kHz audio...")
    t0 = time.time()
    asr_proc = WhisperProcessor.from_pretrained("vinai/phowhisper-base")
    asr_model = WhisperForConditionalGeneration.from_pretrained("vinai/phowhisper-base").to(DEVICE)
    asr_model.eval()

    # Read audio wav file using wave module (limit to first 30 seconds for speed)
    with wave.open(audio_path, "rb") as wf:
        n_frames = min(wf.getnframes(), 16000 * 30)
        audio_bytes = wf.readframes(n_frames)
        audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

    input_features = asr_proc(audio_data, sampling_rate=16000, return_tensors="pt").input_features.to(DEVICE)
    with torch.no_grad():
        predicted_ids = asr_model.generate(input_features, language="vi", task="transcribe")
    transcript = asr_proc.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()

    stage_timings["5_whisper_asr_ms"] = round((time.time() - t0) * 1000, 2)
    print(f"    -> Done in {stage_timings['5_whisper_asr_ms']:.1f}ms!")
    print(f"    • Spoken Audio Transcript: \"{transcript}\"")

    # -------------------------------------------------------------------------
    # STAGE 6: Triplet ASTE AI - BARTpho-syllable Multimodal Fusion
    # -------------------------------------------------------------------------
    print("\n[*] Stage 6: Running ASTE AI (BARTpho-syllable) on Fused Context (Caption + ASR)...")
    t0 = time.time()
    bart_dir = os.path.join(PROJECT_ROOT, "AI", "bartpho", "syllable_base", "finetune", "checkpoints", "best_aste_model")
    bart_tok = AutoTokenizer.from_pretrained(bart_dir)
    bart_model = MBartForConditionalGeneration.from_pretrained(bart_dir).to(DEVICE)
    bart_model.eval()

    # Fused input: Caption + Whisper speech transcript
    fused_input = f"{target_post['caption']} . Lời thoại: {transcript}" if transcript else target_post['caption']
    input_enc = bart_tok(fused_input, max_length=256, truncation=True, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        gen_tokens = bart_model.generate(
            input_ids=input_enc["input_ids"],
            attention_mask=input_enc["attention_mask"],
            num_beams=4,
            max_length=80
        )
    gen_text = bart_tok.decode(gen_tokens[0], skip_special_tokens=True).strip()
    stage_timings["6_bartpho_aste_ms"] = round((time.time() - t0) * 1000, 2)
    print(f"    -> Done in {stage_timings['6_bartpho_aste_ms']:.1f}ms!")
    print(f"    • Generated ASTE String: \"{gen_text}\"")

    total_pipeline_time_ms = round((time.time() - total_start) * 1000, 2)

    # -------------------------------------------------------------------------
    # FINAL REPORT & CONCRETE NUMBERS
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("📊 REAL-WORLD MEASURED RUNTIME REPORT (END-TO-END LIVE PIPELINE)")
    print("=" * 80)
    non_ai_ms = stage_timings["1_video_download_ms"] + stage_timings["2_opencv_keyframe_ms"] + stage_timings["3_ffmpeg_audio_ms"]
    pure_ai_ms = stage_timings["4_clip_vision_ms"] + stage_timings["5_whisper_asr_ms"] + stage_timings["6_bartpho_aste_ms"]

    print(f"1. Network Ingestion (yt-dlp MP4 stream) : {stage_timings['1_video_download_ms']:8.2f} ms ({stage_timings['1_video_download_ms']/total_pipeline_time_ms*100:5.1f}%)")
    print(f"2. Video Decoding (OpenCV top-3 frames)  : {stage_timings['2_opencv_keyframe_ms']:8.2f} ms ({stage_timings['2_opencv_keyframe_ms']/total_pipeline_time_ms*100:5.1f}%)")
    print(f"3. Audio Demuxing (FFmpeg 16kHz WAV)     : {stage_timings['3_ffmpeg_audio_ms']:8.2f} ms ({stage_timings['3_ffmpeg_audio_ms']/total_pipeline_time_ms*100:5.1f}%)")
    print(f"   [SUBTOTAL NON-AI I/O & PREPROCESSING] : {non_ai_ms:8.2f} ms ({non_ai_ms/total_pipeline_time_ms*100:5.1f}%)")
    print("-" * 80)
    print(f"4. Vision AI (CLIP ViT-B/32 on 3 frames) : {stage_timings['4_clip_vision_ms']:8.2f} ms ({stage_timings['4_clip_vision_ms']/total_pipeline_time_ms*100:5.1f}%)")
    print(f"5. Audio AI (PhoWhisper-base 30s ASR)    : {stage_timings['5_whisper_asr_ms']:8.2f} ms ({stage_timings['5_whisper_asr_ms']/total_pipeline_time_ms*100:5.1f}%)")
    print(f"6. Triplet AI (BARTpho Multimodal ASTE)  : {stage_timings['6_bartpho_aste_ms']:8.2f} ms ({stage_timings['6_bartpho_aste_ms']/total_pipeline_time_ms*100:5.1f}%)")
    print(f"   [SUBTOTAL PURE NEURAL AI INFERENCE]   : {pure_ai_ms:8.2f} ms ({pure_ai_ms/total_pipeline_time_ms*100:5.1f}%)")
    print("=" * 80)
    print(f"🏁 TOTAL END-TO-END PIPELINE LATENCY    : {total_pipeline_time_ms:8.2f} ms ({total_pipeline_time_ms/1000:.2f} seconds)")
    print("=" * 80)

if __name__ == "__main__":
    main()
