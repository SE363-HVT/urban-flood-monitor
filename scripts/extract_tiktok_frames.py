#!/usr/bin/env python3
"""
RadiNet/scripts/extract_tiktok_frames.py
Utility to download, decode, and extract representative keyframes and audio tracks
from TikTok/Facebook flood videos for Multimodal Vision-Language AI models (CLIP, ViT, Whisper).
"""

import os
import sys
import argparse
import subprocess
import cv2
from typing import List, Dict, Any, Optional

def extract_keyframes_from_video(
    video_path: str,
    output_dir: str,
    fps_sample: float = 0.5,
    max_frames: int = 12
) -> List[str]:
    """
    Extracts representative visual keyframes from a video using OpenCV.
    - fps_sample: 0.5 means 1 frame every 2 seconds.
    - max_frames: Maximum frames to prevent memory bloat.
    """
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"[!] Error: Could not open video file: {video_path}")
        return []

    video_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_sec = total_frames / video_fps if video_fps > 0 else 0
    frame_interval = max(1, int(video_fps / fps_sample))

    saved_frames = []
    frame_idx = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_interval == 0 and saved_count < max_frames:
            timestamp_sec = frame_idx / video_fps
            frame_filename = f"frame_{saved_count:03d}_{timestamp_sec:.1f}s.jpg"
            frame_filepath = os.path.join(output_dir, frame_filename)
            
            # Save frame at high JPEG quality
            cv2.imwrite(frame_filepath, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
            saved_frames.append(frame_filepath)
            saved_count += 1

        frame_idx += 1

    cap.release()
    print(f"[+] Extracted {len(saved_frames)} keyframes (Duration: {duration_sec:.1f}s) to: {output_dir}")
    return saved_frames


def extract_audio_track(video_path: str, output_wav_path: str) -> Optional[str]:
    """
    Extracts 16kHz mono audio track from video using FFmpeg for Whisper ASR.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        output_wav_path
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"[+] Extracted 16kHz audio track for Whisper: {output_wav_path}")
        return output_wav_path
    except Exception as e:
        print(f"[-] Warning: Failed to extract audio track: {e}")
        return None


def process_video_asset(
    video_path: str,
    target_dir: str,
    fps_sample: float = 0.5,
    max_frames: int = 10
) -> Dict[str, Any]:
    """
    Complete multimodal extraction: frames + audio.
    """
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    out_dir = os.path.join(target_dir, base_name)
    os.makedirs(out_dir, exist_ok=True)

    frames_dir = os.path.join(out_dir, "frames")
    frames = extract_keyframes_from_video(video_path, frames_dir, fps_sample=fps_sample, max_frames=max_frames)
    
    wav_path = os.path.join(out_dir, f"{base_name}.wav")
    audio = extract_audio_track(video_path, wav_path)

    return {
        "video_path": video_path,
        "base_name": base_name,
        "frames_extracted": len(frames),
        "frame_paths": frames,
        "audio_path": audio
    }


def main():
    parser = argparse.ArgumentParser(description="RadiNet - TikTok/Facebook Video Frame & Audio Extractor")
    parser.add_argument("--video", type=str, default="RadiNet/data/audio_sample/sample_0.mp4", help="Path to .mp4 video file")
    parser.add_argument("--output_dir", type=str, default="RadiNet/data/extracted_frames", help="Output directory")
    parser.add_argument("--fps", type=float, default=0.5, help="Sampling rate (frames per second, default=0.5: 1 frame/2s)")
    parser.add_argument("--max_frames", type=int, default=10, help="Max keyframes to extract")
    args = parser.parse_args()

    if not os.path.exists(args.video):
        print(f"[!] Error: Video file does not exist: {args.video}")
        sys.exit(1)

    print("=" * 70)
    print("        RADINET MULTIMODAL VIDEO ASSET DECOMPOSITION TOOL             ")
    print("=" * 70)
    print(f"[*] Input Video : {args.video}")
    print(f"[*] Target Dir  : {args.output_dir}")
    print(f"[*] Sampling    : {args.fps} FPS (max {args.max_frames} frames)")
    print("-" * 70)

    result = process_video_asset(args.video, args.output_dir, fps_sample=args.fps, max_frames=args.max_frames)
    print("-" * 70)
    print(f"[✓] Decomposition Completed Successfully:")
    print(f"    • Frames: {result['frames_extracted']} image files saved in {os.path.join(args.output_dir, result['base_name'], 'frames')}")
    print(f"    • Audio : {result['audio_path']}")
    print("=" * 70)


if __name__ == "__main__":
    main()
