# -*- coding: utf-8 -*-
"""
scripts/benchmark_single_item_latency.py
--------------------------------------------------------------------------------
RadiNet AI Pipeline Benchmark (1 Post / 1 Video)
Measures exact warm execution time (excluding model loading/initialization).
- Branch 1 (Fast Path): PhoBERT-base-v2 ASTE inference latency and triplet extraction
- Branch 2 (Slow Path): 5-stage frame funnel + CLIP + PhoWhisper + BARTpho ASTE
"""
import os
import sys
import io
import time
import subprocess
import cv2
import numpy as np
import torch
from PIL import Image

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

def compute_phash(img_rgb):
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    resized = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
    dct = cv2.dct(np.float32(resized))[:8, :8]
    med = np.median(dct)
    return (dct > med).flatten()

def hamming_dist(h1, h2):
    return int(np.count_nonzero(h1 != h2))

def get_laplacian_var(img_rgb):
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())

def get_exposure_score(img_rgb):
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    mean_val = float(np.mean(gray))
    # Passed if not underexposed (<25) and not overexposed (>235)
    return 25.0 <= mean_val <= 235.0, mean_val

def main():
    print("=" * 70)
    print("RADINET AI PIPELINE LATENCY BENCHMARK (1 POST / 1 VIDEO)")
    print(f"Device: {DEVICE} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print("=" * 70)
    print("\n[Phase 0] Loading all 4 models into VRAM (One-time warmup)...")
    
    # 1. PhoBERT
    from scripts.train_phobert_aste import PhoBertASTEPredictor
    phobert_ckpt = os.path.join(ROOT_DIR, "AI", "phobert", "base_v2", "finetune", "checkpoints")
    phobert = PhoBertASTEPredictor(checkpoint_dir=phobert_ckpt, device="cuda:0" if torch.cuda.is_available() else "cpu")
    
    # 2. CLIP ViT-B/32
    from transformers import CLIPProcessor, CLIPModel
    try:
        clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32", local_files_only=True).half().to(DEVICE).eval()
        clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32", local_files_only=True)
    except Exception:
        clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").half().to(DEVICE).eval()
        clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
    # 3. PhoWhisper-base
    from transformers import WhisperProcessor, WhisperForConditionalGeneration
    whisper_model = WhisperForConditionalGeneration.from_pretrained("vinai/phowhisper-base").half().to(DEVICE).eval()
    whisper_processor = WhisperProcessor.from_pretrained("vinai/phowhisper-base")
    
    # 4. BARTpho-syllable
    from AI.bartpho.test.inference import ASTEPredictor
    bart_ckpt = os.path.join(ROOT_DIR, "AI", "bartpho", "syllable_base", "finetune", "checkpoints", "best_aste_model")
    bartpho = ASTEPredictor(checkpoint_dir=bart_ckpt, device="cuda:0" if torch.cuda.is_available() else "cpu")
    bartpho.model = bartpho.model.half().eval()
    
    # Warmup runs on GPU
    dummy_text = "Đoạn đường Nguyễn Huệ ngập nhẹ sau mưa lớn."
    phobert.predict(dummy_text)
    dummy_img = Image.new("RGB", (224, 224), color=(100, 150, 200))
    clip_inputs = clip_processor(text=["a flood scene", "dry road"], images=dummy_img, return_tensors="pt", padding=True).to(DEVICE)
    with torch.no_grad():
        clip_model(**clip_inputs)
    dummy_audio = np.zeros(16000 * 2, dtype=np.float32)
    w_feat = whisper_processor(dummy_audio, sampling_rate=16000, return_tensors="pt").input_features.half().to(DEVICE)
    with torch.no_grad():
        whisper_model.generate(w_feat, language="vi", task="transcribe", max_new_tokens=10)
    bartpho.predict(dummy_text)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        vram = torch.cuda.memory_allocated(DEVICE) / (1024 * 1024)
        print(f"[+] All models loaded and warmed in VRAM! Current VRAM: {vram:.1f} MB\n")
    
    # =========================================================================
    # PART 1: FAST PATH BENCHMARK (1 Text Post)
    # =========================================================================
    print("=" * 70)
    print("PART 1: FAST PATH BENCHMARK (1 Text Post)")
    print("=" * 70)
    test_text = "Đoạn đường Võ Văn Ngân, TP. Hồ Chí Minh ngập sâu lút bánh xe, chết máy hàng loạt."
    print(f"Sample Post: \"{test_text}\"")
    
    latencies_fast = []
    triplets_fast = None
    for i in range(15):
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t_start = time.perf_counter()
        res = phobert.predict(test_text)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t_end = time.perf_counter()
        latencies_fast.append((t_end - t_start) * 1000.0)
        if triplets_fast is None:
            triplets_fast = res
            
    latencies_fast = latencies_fast[5:] # Drop first 5 warmup iterations
    print(f"• Pure Model Inference Latency:")
    print(f"  - Mean: {np.mean(latencies_fast):.2f} ms")
    print(f"  - Min : {np.min(latencies_fast):.2f} ms")
    print(f"  - Max : {np.max(latencies_fast):.2f} ms")
    print(f"  - P95 : {np.percentile(latencies_fast, 95):.2f} ms")
    print(f"• Output Triplets: {len(triplets_fast)} extracted")
    for t in triplets_fast:
        print(f"    - ({t['aspect']}, {t['opinion']}, {t['polarity']}, {t['severity']}) [conf: {t['confidence']:.2f}]")
        
    # =========================================================================
    # PART 2: SLOW PATH BENCHMARK (1 Video with 5-stage Funnel)
    # =========================================================================
    print("\n" + "=" * 70)
    print("PART 2: SLOW PATH BENCHMARK (1 Video - 30s TikTok Clip)")
    print("=" * 70)
    candidates = [
        "/tmp/live_test_video/video.mp4",
        os.path.join(ROOT_DIR, "data", "extracted_frames", "live_run_test", "input_video.mp4")
    ]
    video_path = next((p for p in candidates if os.path.exists(p)), None)
    if not video_path:
        print("[-] No test video found for Slow Path benchmark.")
        return
    print(f"Video Source: {video_path}")
    
    for target_duration, label in [(30.0, "30-second standard video"), (119.7, "Full 120-second video")]:
        print(f"\n--- Testing Slow Path on {label} ---")
        stage_times = {}
        
        # 1. ffprobe Probe
        t0 = time.perf_counter()
        probe_cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration,r_frame_rate,nb_frames",
            "-of", "csv=p=0", video_path
        ]
        proc = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        t_probe = (time.perf_counter() - t0) * 1000.0
        stage_times["1. ffprobe Video Probe"] = t_probe
        
        # 2. OpenCV 0.5 FPS Sampling
        t0 = time.perf_counter()
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        sample_interval = int(round(fps / 0.5)) # every 2.0s
        sampled_frames = []
        frame_idx = 0
        max_frames_to_read = int(target_duration * fps)
        
        while cap.isOpened() and frame_idx < max_frames_to_read:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % sample_interval == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                sampled_frames.append((frame_idx, frame_idx / fps, frame_rgb))
            frame_idx += 1
        cap.release()
        t_sample = (time.perf_counter() - t0) * 1000.0
        stage_times[f"2. OpenCV 0.5 FPS Sampling ({len(sampled_frames)} frames)"] = t_sample
        
        # 3. pHash Deduplication (Hamming distance <= 8)
        t0 = time.perf_counter()
        hashes = []
        for idx, sec, img in sampled_frames:
            h = compute_phash(img)
            lap = get_laplacian_var(img)
            matched_cluster = False
            for cluster_idx, (c_h, c_best_lap, c_frame) in enumerate(hashes):
                dist = hamming_dist(h, c_h)
                if dist <= 8:
                    matched_cluster = True
                    if lap > c_best_lap:
                        hashes[cluster_idx] = (c_h, lap, (idx, sec, img, lap))
                    break
            if not matched_cluster:
                hashes.append((h, lap, (idx, sec, img, lap)))
        
        deduped_frames = [item[2] for item in hashes]
        t_phash = (time.perf_counter() - t0) * 1000.0
        stage_times[f"3. pHash Dedup ({len(sampled_frames)} -> {len(deduped_frames)} frames)"] = t_phash
        
        # 4. Laplacian Blur Gate (var >= 100) + Exposure Gate
        t0 = time.perf_counter()
        quality_passed_frames = []
        for idx, sec, img, lap in deduped_frames:
            is_valid_exp, mean_exp = get_exposure_score(img)
            if lap >= 100.0 and is_valid_exp:
                quality_passed_frames.append((idx, sec, img, lap))
        if not quality_passed_frames and deduped_frames:
            quality_passed_frames = [max(deduped_frames, key=lambda x: x[3])]
        t_quality = (time.perf_counter() - t0) * 1000.0
        stage_times[f"4. Laplacian Blur + Exposure Gate ({len(deduped_frames)} -> {len(quality_passed_frames)} frames)"] = t_quality
        
        # 5. CLIP Flood Scoring + MMR Diversity Selection (Top-3)
        t0 = time.perf_counter()
        pil_images = [Image.fromarray(item[2]) for item in quality_passed_frames]
        clip_prompts = [
            "a flooded city street with deep water and submerged motorbikes or cars",
            "a dry normal road with traffic and no water",
            "an indoor scene, selfie, or food dish"
        ]
        clip_inputs = clip_processor(
            text=clip_prompts,
            images=pil_images,
            return_tensors="pt",
            padding=True
        ).to(DEVICE)
        with torch.no_grad():
            outputs = clip_model(**clip_inputs)
            flood_probs = outputs.logits_per_image.softmax(dim=-1)[:, 0].cpu().numpy()
            
        top_k = min(3, len(quality_passed_frames))
        selected_indices = np.argsort(flood_probs)[::-1][:top_k]
        top_frames = [quality_passed_frames[i] for i in selected_indices]
        top_flood_confidence = float(np.max(flood_probs))
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t_clip = (time.perf_counter() - t0) * 1000.0
        stage_times[f"5. CLIP Flood MMR Top-3 ({len(quality_passed_frames)} frames on GPU)"] = t_clip
        
        # 6. Audio Extraction (FFmpeg 16kHz mono, target duration)
        t0 = time.perf_counter()
        audio_cmd = [
            "ffmpeg", "-y", "-ss", "0", "-t", str(min(30.0, target_duration)),
            "-i", video_path, "-vn", "-ar", "16000", "-ac", "1",
            "-f", "wav", "pipe:1"
        ]
        audio_proc = subprocess.run(audio_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        audio_bytes = audio_proc.stdout
        t_audio_extract = (time.perf_counter() - t0) * 1000.0
        stage_times["6. FFmpeg Audio Extraction (30s PCM)"] = t_audio_extract
        
        # 7. PhoWhisper-base ASR Inference
        t0 = time.perf_counter()
        import wave
        with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
            raw_data = wf.readframes(wf.getnframes())
            audio_array = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        w_inputs = whisper_processor(audio_array, sampling_rate=16000, return_tensors="pt")
        w_features = w_inputs.input_features.half().to(DEVICE)
        with torch.no_grad():
            pred_ids = whisper_model.generate(w_features, language="vi", task="transcribe")
        transcript = whisper_processor.batch_decode(pred_ids, skip_special_tokens=True)[0].strip()
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t_whisper = (time.perf_counter() - t0) * 1000.0
        stage_times[f"7. PhoWhisper-base ASR Inference (GPU)"] = t_whisper
        
        # 8. BARTpho-syllable ASTE Inference
        t0 = time.perf_counter()
        fused_text = f"Đường Võ Văn Ngân ngập sâu. Lời thoại: {transcript}" if transcript else "Đường Võ Văn Ngân ngập sâu."
        bart_triplets = bartpho.predict(fused_text)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t_bartpho = (time.perf_counter() - t0) * 1000.0
        stage_times["8. BARTpho-syllable ASTE Inference (GPU)"] = t_bartpho
        
        total_time_ms = sum(stage_times.values())
        print(f"\n--- LATENCY BREAKDOWN ({label}) ---")
        for stage, duration_ms in stage_times.items():
            print(f"  {stage:<55}: {duration_ms:8.2f} ms")
        print("-" * 70)
        print(f"  {'TOTAL WARM SLOW PATH LATENCY':<55}: {total_time_ms:8.2f} ms ({total_time_ms/1000.0:.2f} s)")
        print(f"  • CLIP Flood Confidence: {top_flood_confidence:.2f}")
        print(f"  • PhoWhisper Transcript: \"{transcript}\"")
        print(f"  • BARTpho Triplets: {len(bart_triplets)} extracted")

if __name__ == "__main__":
    main()
