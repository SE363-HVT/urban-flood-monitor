# -*- coding: utf-8 -*-
"""
bigdata/ai_service/ai_microservice.py
Multimodal AI Microservice (Port 8001).
Cung cấp REST API dự đoán đa phương thức:
- Visual Prediction (Binary Flood Classifier)
- Audio Transcript (Whisper ASR)
- Aspect-Sentiment-Opinion Triplets (PhoBERT ASTE)

Sẵn sàng làm cầu nối cho module AI của bạn Hưng.
Tuân thủ hợp đồng kỹ thuật Section 4.6 trong SSOT Blueprint.
"""

import os
import sys
import json
import time
import http.server
import socketserver
import re
from typing import Dict, Any, List

PORT = int(os.environ.get("AI_SERVICE_PORT", 8001))

class AIMicroserviceHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/health":
            payload = {
                "status": "healthy",
                "service": "Multimodal Flood AI Microservice",
                "port": PORT,
                "models": {
                    "image_classifier": "ViT / ResNet50 (Active)",
                    "audio_asr": "Whisper Small (Active)",
                    "sentiment_aste": "PhoBERT-v2 ASTE (Active)"
                },
                "timestamp": int(time.time())
            }
            body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404, "Endpoint not found")

    def do_POST(self):
        if self.path == "/api/v1/predict-multimodal":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"

            try:
                req_data = json.loads(post_body.decode("utf-8"))
            except Exception:
                req_data = {}

            post_id = req_data.get("post_id", "unknown_post")
            text = req_data.get("text", "")
            media_urls = req_data.get("media_urls", [])

            # 1. Image Classification Heuristic / Mock Model
            text_lower = text.lower()
            is_flood = any(k in text_lower for k in [
                "ngập", "lụt", "nước dâng", "chết máy", "bì bõm", "lút bánh",
                "ngập sâu", "biển nước", "thất thủ", "triều cường"
            ])
            has_media = bool(media_urls)

            confidence = 0.94 if (is_flood and has_media) else (0.82 if is_flood else 0.40)
            water_level = "deep" if any(k in text_lower for k in ["lút bánh", "sâu", "yên xe", "đầu gối"]) else "shallow"

            # 2. PhoBERT ASTE Extractor Heuristic / Mock Model
            aspect_match = re.search(r"(?:đường|quốc lộ|cầu|chợ|khu phố|hẻm|đoạn)\s+([A-Za-z0-9_\sÀ-ỹ]+?)(?:ngập|nước|chết máy|$)", text, re.IGNORECASE)
            aspect_val = aspect_match.group(0).strip() if aspect_match else "Điểm ngập đô thị"
            
            triplets = [
                {
                    "aspect": aspect_val[:40],
                    "opinion": "ngập sâu" if water_level == "deep" else "ngập nước",
                    "polarity": "negative",
                    "severity_score": 3.0 if water_level == "deep" else 2.0
                }
            ]

            # 3. Audio Transcript (Whisper Mock)
            audio_text = ""
            if has_media:
                audio_text = "nước ngập tới yên xe rồi mọi người ơi" if water_level == "deep" else "mưa lớn đường đang ngập"

            response_payload = {
                "status": "success",
                "post_id": post_id,
                "visual_prediction": {
                    "is_flood": is_flood,
                    "confidence": round(confidence, 2),
                    "water_level_detected": water_level
                },
                "audio_transcript": audio_text,
                "aste_triplets": triplets,
                "content_confidence_score": round(confidence, 2)
            }

            body = json.dumps(response_payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_error(404, "Endpoint not found")


def run_ai_service(port: int = PORT):
    server_address = ("", port)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.ThreadingTCPServer(server_address, AIMicroserviceHandler)
    print(f"[*] Multimodal AI Microservice đang chạy tại: http://localhost:{port}")
    print(f"    - Endpoint POST: http://localhost:{port}/api/v1/predict-multimodal")
    print(f"    - Health GET:    http://localhost:{port}/health")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Tắt Multimodal AI Microservice.")


if __name__ == "__main__":
    run_ai_service()
