# -*- coding: utf-8 -*-
"""
bigdata/ai_service/ai_microservice.py
--------------------------------------------------------------------------------
RadiNet Multimodal AI Microservice (Port 8001) - v2.0
Implements the 2-Branch AI Architecture defined in ARCHITECTURE_V2_AND_AI_IMPLEMENTATION_GUIDE.md:

1. Branch 1 (Fast Path):
   - Model: vinai/phobert-base-v2 (Span / Table-filling ASTE)
   - Input: Text (Title, Caption, Post content)
   - Latency: <= 10ms on GPU (strict SLA <= 35ms)
   - Zero hallucination, extracts verbatim spans for GIS Grounding

2. Branch 2 (Slow Path):
   - Models: CLIP ViT-B/32 (Vision) + PhoWhisper-base (Audio ASR) + BARTpho-syllable (Generative ASTE)
   - Input: Video URL / Media attachments + Caption
   - Latency: ~1.5s - 5.0s (SLA <= 10.0s)
   - Verifies visual flood scene, transcribes spoken speech, fuses cross-modal features

3. Unified Endpoint:
   - POST /api/v1/predict-multimodal: Auto-routes to Fast Path or Slow Path based on media presence
   - Maintains 100% backward compatibility with pipeline/veracity_checker.py
"""

import os
import sys
import io
import time
import wave
import argparse
import unicodedata
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

import numpy as np
from PIL import Image
import torch
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Setup Project Path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from pipeline.multimodal_streamer import stream_thumbnail_in_memory, stream_audio_in_memory

PORT = int(os.environ.get("AI_SERVICE_PORT", 8001))
DEVICE_STR = "cuda:0" if torch.cuda.is_available() else "cpu"
DEVICE = torch.device(DEVICE_STR)

# Global Model Registry
MODELS = {
    "phobert_fast": None,
    "clip_model": None,
    "clip_processor": None,
    "whisper_model": None,
    "whisper_processor": None,
    "bartpho_predictor": None,
    "device": DEVICE_STR,
    "is_ready": False
}

CLIP_CANDIDATE_LABELS = [
    "a flooded street in a city with deep standing water and submerged vehicles",
    "a normal dry city road with clear traffic",
    "an indoor room, food dish, or personal selfie"
]


# =============================================================================
# MODEL INITIALIZATION & WARMING
# =============================================================================
def load_all_models():
    """Loads all AI models into GPU memory in FP16 to minimize VRAM footprint."""
    print(f"\n[*] Initializing RadiNet AI Models on device: {DEVICE_STR}...")
    t0 = time.time()

    # 1. Fast Path: PhoBERT-base-v2 ASTE
    try:
        from scripts.train_phobert_aste import PhoBertASTEPredictor
        phobert_ckpt = os.path.join(ROOT_DIR, "AI", "phobert", "base_v2", "finetune", "checkpoints")
        if os.path.exists(os.path.join(phobert_ckpt, "best_phobert_aste.pt")):
            MODELS["phobert_fast"] = PhoBertASTEPredictor(checkpoint_dir=phobert_ckpt, device=DEVICE_STR)
            print("    [+] Branch 1 (Fast Path): PhoBERT-base-v2 loaded successfully.")
    except Exception as e:
        print(f"    [-] Warning: Could not load PhoBERT Fast Path: {e}")

    # 2. Slow Path: CLIP ViT-B/32
    try:
        from transformers import CLIPProcessor, CLIPModel
        MODELS["clip_model"] = CLIPModel.from_pretrained("openai/clip-vit-base-patch32", local_files_only=True).half().to(DEVICE)
        MODELS["clip_processor"] = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32", local_files_only=True)
        MODELS["clip_model"].eval()
        print("    [+] Branch 2 (Vision): CLIP ViT-B/32 (FP16) loaded successfully.")
    except Exception as e:
        print(f"    [-] Warning: Could not load CLIP Vision model: {e}")

    # 3. Slow Path: PhoWhisper-base ASR
    try:
        from transformers import WhisperProcessor, WhisperForConditionalGeneration
        MODELS["whisper_model"] = WhisperForConditionalGeneration.from_pretrained("vinai/phowhisper-base").half().to(DEVICE)
        MODELS["whisper_processor"] = WhisperProcessor.from_pretrained("vinai/phowhisper-base")
        MODELS["whisper_model"].eval()
        print("    [+] Branch 2 (Audio): PhoWhisper-base ASR (FP16) loaded successfully.")
    except Exception as e:
        print(f"    [-] Warning: Could not load PhoWhisper model: {e}")

    # 4. Slow Path: BARTpho-syllable Generative ASTE
    try:
        from AI.bartpho.test.inference import ASTEPredictor
        bart_ckpt = os.path.join(ROOT_DIR, "AI", "bartpho", "syllable_base", "finetune", "checkpoints", "best_aste_model")
        if os.path.exists(bart_ckpt):
            pred = ASTEPredictor(checkpoint_dir=bart_ckpt, device=DEVICE_STR)
            pred.model = pred.model.half()
            MODELS["bartpho_predictor"] = pred
            print("    [+] Branch 2 (ASTE Fusion): BARTpho-syllable (FP16) loaded successfully.")
    except Exception as e:
        print(f"    [-] Warning: Could not load BARTpho model: {e}")

    MODELS["is_ready"] = True
    vram_mb = torch.cuda.memory_allocated(DEVICE) / (1024 * 1024) if torch.cuda.is_available() else 0
    print(f"[*] All models initialized in {time.time() - t0:.2f}s! VRAM allocated: {vram_mb:.1f} MB\n")


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_all_models()
    yield
    print("[*] Shutting down AI Microservice.")


# =============================================================================
# FASTAPI APP & SCHEMAS
# =============================================================================
app = FastAPI(
    title="RadiNet Multimodal Flood AI Microservice",
    version="2.0",
    description="Dual-branch AI Service: Fast Path (PhoBERT ASTE) & Slow Path (CLIP + PhoWhisper + BARTpho)",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FastPredictionRequest(BaseModel):
    post_id: Optional[str] = "post_raw"
    text: str = Field(..., description="Sentence or post caption text to extract triplets from")


class SlowPredictionRequest(BaseModel):
    post_id: Optional[str] = "post_raw"
    text: Optional[str] = ""
    media_urls: Optional[List[str]] = []
    video_url: Optional[str] = None


class UnifiedPredictionRequest(BaseModel):
    post_id: Optional[str] = "post_raw"
    text: Optional[str] = ""
    media_urls: Optional[List[str]] = []
    video_url: Optional[str] = None


# =============================================================================
# CORE PREDICTION LOGIC
# =============================================================================
def execute_fast_path(text: str) -> List[Dict[str, Any]]:
    """Runs PhoBERT Fast Path (<=10ms). Falls back to heuristic if model not loaded."""
    if not text:
        return []

    phobert = MODELS.get("phobert_fast")
    if phobert is not None:
        try:
            return phobert.predict(text)
        except Exception as e:
            print(f"[FastPath] PhoBERT error: {e}")

    # Graceful fallback heuristic if PhoBERT is unavailable
    text_lower = text.lower()
    if any(k in text_lower for k in ["ngập", "lụt", "chết máy", "nước dâng", "triều cường"]):
        return [{
            "aspect": "Điểm ngập đô thị",
            "opinion": "ngập sâu",
            "polarity": "NEG",
            "confidence": 0.75
        }]
    return []


def execute_slow_path(text: str, video_url: Optional[str]) -> Dict[str, Any]:
    """Runs Multimodal Slow Path (CLIP + PhoWhisper + BARTpho)."""
    visual_result = {"is_flood": False, "confidence": 0.50, "water_level_detected": "normal"}
    audio_transcript = ""
    triplets = []

    # 1. Vision Verification via CLIP
    if video_url and MODELS.get("clip_model") is not None:
        try:
            thumb_bytes = stream_thumbnail_in_memory(video_url)
            if thumb_bytes:
                img = Image.open(io.BytesIO(thumb_bytes)).convert("RGB")
                inputs = MODELS["clip_processor"](
                    text=CLIP_CANDIDATE_LABELS,
                    images=img,
                    return_tensors="pt",
                    padding=True
                ).to(DEVICE)
                with torch.no_grad():
                    outputs = MODELS["clip_model"](**inputs)
                    probs = outputs.logits_per_image.softmax(dim=1).squeeze().tolist()
                
                flood_prob = probs[0]
                visual_result = {
                    "is_flood": bool(flood_prob >= 0.50),
                    "confidence": round(float(flood_prob), 2),
                    "water_level_detected": "deep" if flood_prob >= 0.85 else "shallow"
                }
        except Exception as e:
            print(f"[SlowPath] CLIP Vision error: {e}")

    # 2. Speech-to-Text via PhoWhisper
    if video_url and MODELS.get("whisper_model") is not None:
        try:
            audio_bytes = stream_audio_in_memory(video_url)
            if audio_bytes and len(audio_bytes) > 2048:
                with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
                    n_frames = min(wf.getnframes(), 16000 * 30) # 30s limit
                    raw_audio = np.frombuffer(wf.readframes(n_frames), dtype=np.int16).astype(np.float32) / 32768.0

                inputs = MODELS["whisper_processor"](raw_audio, sampling_rate=16000, return_tensors="pt")
                feat = inputs.input_features.half().to(DEVICE)
                with torch.no_grad():
                    pred_ids = MODELS["whisper_model"].generate(feat, language="vi", task="transcribe")
                audio_transcript = MODELS["whisper_processor"].batch_decode(pred_ids, skip_special_tokens=True)[0].strip()
        except Exception as e:
            print(f"[SlowPath] PhoWhisper ASR error: {e}")

    # 3. Triplet ASTE Extraction via BARTpho
    fused_text = f"{text} . Lời thoại: {audio_transcript}" if audio_transcript else text
    if fused_text and MODELS.get("bartpho_predictor") is not None:
        try:
            res = MODELS["bartpho_predictor"].predict(fused_text)
            triplets = res.get("triplets", [])
        except Exception as e:
            print(f"[SlowPath] BARTpho ASTE error: {e}")

    # Fallback to Fast Path if BARTpho produced empty results
    if not triplets and text:
        triplets = execute_fast_path(text)

    # Compute overall content score
    vis_score = visual_result["confidence"] if visual_result.get("is_flood") else 0.50
    content_score = round(0.5 * vis_score + 0.5 * (0.90 if triplets else 0.50), 2)

    return {
        "visual_prediction": visual_result,
        "audio_transcript": audio_transcript,
        "aste_triplets": triplets,
        "content_confidence_score": content_score
    }


# =============================================================================
# API ENDPOINTS
# =============================================================================
@app.get("/")
@app.get("/health")
def health_check():
    """Health check reporting active status of all 4 models."""
    vram_mb = torch.cuda.memory_allocated(DEVICE) / (1024 * 1024) if torch.cuda.is_available() else 0
    return {
        "status": "healthy",
        "service": "RadiNet Multimodal AI Microservice v2.0",
        "port": PORT,
        "device": DEVICE_STR,
        "vram_allocated_mb": round(vram_mb, 1),
        "models": {
            "branch_1_phobert_fast": "active" if MODELS["phobert_fast"] else "mock_fallback",
            "branch_2_clip_vision": "active" if MODELS["clip_model"] else "mock_fallback",
            "branch_2_whisper_asr": "active" if MODELS["whisper_model"] else "mock_fallback",
            "branch_2_bartpho_aste": "active" if MODELS["bartpho_predictor"] else "mock_fallback"
        },
        "timestamp": int(time.time())
    }


@app.post("/api/v1/predict-fast")
def predict_fast(req: FastPredictionRequest):
    """
    Branch 1: Fast Path Endpoint (Text-Only).
    Strict SLA: <= 35ms. Zero-hallucination verbatim span extraction via PhoBERT.
    """
    t0 = time.time()
    triplets = execute_fast_path(req.text)
    latency_ms = round((time.time() - t0) * 1000, 2)

    return {
        "status": "success",
        "branch": "fast_path",
        "post_id": req.post_id,
        "latency_ms": latency_ms,
        "triplets": triplets,
        "visual_verified": False,
        "content_confidence_score": 0.85 if triplets else 0.40
    }


@app.post("/api/v1/predict-slow")
def predict_slow(req: SlowPredictionRequest):
    """
    Branch 2: Slow Path Endpoint (Multimodal Video/Audio).
    SLA: <= 10.0s. Runs CLIP keyframe verification + PhoWhisper ASR + BARTpho fusion.
    """
    t0 = time.time()
    canonical_url = req.video_url or (req.media_urls[0] if req.media_urls else None)
    res = execute_slow_path(req.text or "", canonical_url)
    latency_ms = round((time.time() - t0) * 1000, 2)

    return {
        "status": "success",
        "branch": "slow_path",
        "post_id": req.post_id,
        "latency_ms": latency_ms,
        **res
    }


@app.post("/api/v1/predict-multimodal")
def predict_multimodal(req: UnifiedPredictionRequest):
    """
    Canonical Endpoint: Auto-routes to Fast Path or Slow Path.
    Maintains 100% backward compatibility with pipeline/veracity_checker.py.
    """
    t0 = time.time()
    canonical_url = req.video_url or (req.media_urls[0] if req.media_urls else None)
    has_media = bool(canonical_url or req.media_urls)

    if has_media:
        # Route to Branch 2: Slow Path
        slow_res = execute_slow_path(req.text or "", canonical_url)
        latency_ms = round((time.time() - t0) * 1000, 2)
        return {
            "status": "success",
            "branch": "slow_path",
            "post_id": req.post_id,
            "latency_ms": latency_ms,
            **slow_res
        }
    else:
        # Route to Branch 1: Fast Path (<=10ms response)
        triplets = execute_fast_path(req.text or "")
        latency_ms = round((time.time() - t0) * 1000, 2)
        return {
            "status": "success",
            "branch": "fast_path",
            "post_id": req.post_id,
            "latency_ms": latency_ms,
            "visual_prediction": {
                "is_flood": False,
                "confidence": 0.50,
                "water_level_detected": "normal"
            },
            "audio_transcript": "",
            "aste_triplets": triplets,
            "content_confidence_score": 0.85 if triplets else 0.40
        }


# =============================================================================
# CLI RUNNER
# =============================================================================
def run_ai_service(host: str = "0.0.0.0", port: int = PORT):
    print(f"[*] Starting RadiNet AI Microservice on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RadiNet Multimodal AI Microservice v2.0")
    parser.add_argument("--port", type=int, default=PORT, help="Port to listen on (default: 8001)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface (default: 0.0.0.0)")
    args = parser.parse_args()
    run_ai_service(host=args.host, port=args.port)
