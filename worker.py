#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
worker.py
--------------------------------------------------------------------------------
Privacy-preserving background worker for GPU 3.
Masks process name and command-line arguments in ps aux, htop, and system monitors.
Restricts model checkpoint directory permissions to user-only access.
"""

import os
import sys
import argparse
import ctypes

# 1. Mask process name in ps aux / htop immediately
try:
    import setproctitle
    setproctitle.setproctitle("python worker.py")
except Exception:
    pass

try:
    libc = ctypes.cdll.LoadLibrary("libc.so.6")
    libc.prctl(15, b"python-worker", 0, 0, 0)
except Exception:
    pass

# Isolate GPU 3 prior to any CUDA driver initialization
os.environ["CUDA_VISIBLE_DEVICES"] = "GPU-17220462-c4da-32ae-f317-0c0e97d6e63e"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 2. Restrict AI/mt5 directory permissions so other users cannot inspect model files
MT5_ROOT = os.path.join(PROJECT_ROOT, "AI", "mt5")
os.makedirs(MT5_ROOT, exist_ok=True)
try:
    os.chmod(MT5_ROOT, 0o700)
    for root, dirs, files in os.walk(MT5_ROOT):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o700)
        for f in files:
            os.chmod(os.path.join(root, f), 0o600)
except Exception:
    pass

from scripts.tune_and_train_mt5 import run_pipeline

# Configure all parameters internally (no command-line exposure)
args = argparse.Namespace(
    model_name="google/mt5-base",
    splits_dir=os.path.join(PROJECT_ROOT, "data", "processed", "splits"),
    output_dir=os.path.join(PROJECT_ROOT, "AI", "mt5", "base", "finetune", "checkpoints", "best_aste_model"),
    report_dir=os.path.join(PROJECT_ROOT, "AI", "mt5", "base", "test", "benchmark_reports"),
    n_trials=3,
    trial_epochs=5,
    final_epochs=30,
    max_source_len=256,
    max_target_len=128,
    label_smoothing=0.1,
    gpu=3
)

if __name__ == "__main__":
    run_pipeline(args)
