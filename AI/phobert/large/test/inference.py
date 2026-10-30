#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI/phobert/test/inference.py
--------------------------------------------------------------------------------
Real-time ASTE Inference Utility using fine-tuned PhoBERT checkpoints
(supports both phobert-base-v2 and phobert-large).
"""

import os
import sys
import json
import argparse
import torch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PHOBERT_DIR = os.path.dirname(SCRIPT_DIR)
AI_DIR = os.path.dirname(PHOBERT_DIR)
PROJECT_ROOT = os.path.dirname(AI_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.training.train_phobert_aste import PhoBertASTEPredictor

DEFAULT_CHECKPOINT = os.path.join(PHOBERT_DIR, "finetune", "checkpoints", "phobert_large")
if not os.path.exists(DEFAULT_CHECKPOINT):
    DEFAULT_CHECKPOINT = os.path.join(PHOBERT_DIR, "finetune", "checkpoints", "phobert_base_v2")
if not os.path.exists(DEFAULT_CHECKPOINT):
    DEFAULT_CHECKPOINT = os.path.join(AI_DIR, "finetune", "checkpoints", "phobert_aste_best")


def main():
    parser = argparse.ArgumentParser(description="PhoBERT ASTE Inference")
    parser.add_argument("--checkpoint_dir", type=str, default=DEFAULT_CHECKPOINT, help="Path to checkpoint directory")
    parser.add_argument("--text", type=str, default="Đoạn Thảo Điền nước rút nhanh, mặt đường khô ráo.", help="Text to extract triplets from")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu", help="Device")
    args = parser.parse_args()

    print(f"Loading checkpoint from: {args.checkpoint_dir}")
    predictor = PhoBertASTEPredictor(checkpoint_dir=args.checkpoint_dir, device=args.device)

    triplets = predictor.predict(args.text)
    print(f"\nInput: \"{args.text}\"")
    print(f"Extracted Triplets ({len(triplets)}):")
    print(json.dumps(triplets, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
