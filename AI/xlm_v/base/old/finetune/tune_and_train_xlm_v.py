#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/tune_and_train_xlm_v.py
--------------------------------------------------------------------------------
Optuna Hyperparameter Tuning (3 Trials x 5 Epochs) followed by Full 30-Epoch
Fine-Tuning of XLM-V ASTE Model on HCMC Urban Flood v3 Splits.

Backbone: facebook/xlm-v-base (Liang et al., Meta AI, 2023)
  • One-Million token vocabulary
  • Joint BIO Sequence Tagging + Span-Pair Representation

Reviewer Compliance Checklist (V2 Standard):
  1. Checkpoint Selection: Validation Composite Grounded ASTE F1 (Triplet F1 + 0.5*Asp + 0.5*Opn)
  2. Deterministic Seeding: Seed 42 for PyTorch, NumPy, Python, CuDNN, DataLoader
  3. Truncation Audit: Max sequence length 256, verified target truncation 0.00%
  4. Artifact Pinning: Git commit SHA and dataset MD5 hashes persisted in training_meta.json
  5. AMP Scaler Guard: Unscale before clip, scale_before <= scale_after scheduler guard

Workflow:
  Stage 1: Optuna Optimization (3 Trials x 5 Epochs) maximizing Validation Composite ASTE F1
  Stage 2: Full Fine-Tuning (30 Epochs) with winning hyperparameters, saving best F1 checkpoint
  Stage 3: Independent Test Split Evaluation on test.json (462 samples)
  Stage 4: Master Comparison Table Update in AI/results/
"""

import os
import sys
import gc
import json
import time
import argparse
import random
import hashlib
import subprocess
from typing import Dict, Any

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, get_linear_schedule_with_warmup
import optuna

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.train_xlm_v_aste import (
    XLMVJsonDataset,
    aste_collate_fn,
    XLMVForASTE,
    evaluate_model,
    seed_everything,
    seed_worker,
    get_file_md5,
    get_git_commit_sha,
    RANDOM_SEED
)

optuna.logging.set_verbosity(optuna.logging.INFO)

GPU_UUID_MAP = {
    0: "GPU-402b1880-531f-0736-be2e-03a8a229590b",
    2: "GPU-40888ad5-fe5d-17c8-a236-4b0fd1d97e6f",
    3: "GPU-17220462-c4da-32ae-f317-0c0e97d6e63e"
}

DEFAULT_SPLITS_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "splits")
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "AI", "xlm_v", "base", "finetune", "checkpoints")
DEFAULT_REPORT_DIR = os.path.join(PROJECT_ROOT, "AI", "xlm_v", "base", "test", "benchmark_reports")


def audit_truncation(json_path: str, tokenizer, max_len: int = 256) -> Dict[str, Any]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    lengths = []
    for item in data:
        t = item.get("content", {}).get("text", "")
        if t:
            tokens = tokenizer.encode(t, truncation=False)
            lengths.append(len(tokens))
    arr = np.array(lengths) if lengths else np.array([0])
    truncated_count = int(np.sum(arr > max_len))
    return {
        "total_samples": len(data),
        "max_len_setting": max_len,
        "max_observed": int(np.max(arr)) if len(arr) > 0 else 0,
        "truncated_count": truncated_count,
        "truncated_pct": round(float(truncated_count / max(1, len(data)) * 100), 2)
    }


def train_epoch_loop(
    model_name: str,
    train_file: str,
    dev_file: str,
    learning_rate: float,
    batch_size: int,
    weight_decay: float,
    dropout: float,
    epochs: int,
    device: torch.device,
    fp16: bool = True,
    save_checkpoint_path: str = None,
    checkpoint_dir: str = None,
    trial_prefix: str = "",
    max_len: int = 256
) -> Dict[str, Any]:
    seed_everything(RANDOM_SEED)
    g = torch.Generator()
    g.manual_seed(RANDOM_SEED)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    train_dataset = XLMVJsonDataset(train_file, tokenizer, max_len=max_len, is_train=True)
    dev_dataset = XLMVJsonDataset(dev_file, tokenizer, max_len=max_len, is_train=False)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=aste_collate_fn,
        worker_init_fn=seed_worker,
        generator=g,
        num_workers=0,
        pin_memory=False
    )
    dev_loader = DataLoader(
        dev_dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=aste_collate_fn,
        num_workers=0,
        pin_memory=False
    )

    model = XLMVForASTE(model_name=model_name, dropout_rate=dropout).to(device)

    no_decay = ["bias", "LayerNorm.weight"]
    optimizer_grouped_parameters = [
        {"params": [p for n, p in model.named_parameters() if p.requires_grad and not any(nd in n for nd in no_decay)], "weight_decay": weight_decay},
        {"params": [p for n, p in model.named_parameters() if p.requires_grad and any(nd in n for nd in no_decay)], "weight_decay": 0.0},
    ]
    optimizer = torch.optim.AdamW(optimizer_grouped_parameters, lr=learning_rate)

    total_steps = len(train_loader) * epochs
    warmup_steps = int(0.10 * total_steps)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps)
    scaler = torch.amp.GradScaler('cuda', enabled=fp16 and device.type == "cuda")

    best_score = -1.0
    best_metrics = None
    epoch_histories = []

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        start_t = time.time()

        for step, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            bio_tags = batch["bio_tags"].to(device)
            raw_batch = batch["raw_batch"]

            optimizer.zero_grad()

            with torch.amp.autocast('cuda', enabled=fp16 and device.type == "cuda"):
                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    bio_tags=bio_tags,
                    raw_batch=raw_batch
                )
                loss = outputs.get("loss", torch.tensor(0.0, device=device))

            if loss.requires_grad:
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                scale_before = scaler.get_scale()
                scaler.step(optimizer)
                scaler.update()
                scale_after = scaler.get_scale()
                if scale_before <= scale_after:
                    scheduler.step()

            total_loss += loss.item()

        epoch_loss = total_loss / max(1, len(train_loader))
        epoch_dur = time.time() - start_t

        metrics = evaluate_model(model, dev_loader, device)
        t_f1 = metrics["Triplet_Strict_Match"]["F1"]
        a_f1 = metrics["Aspect_Span"]["F1"]
        o_f1 = metrics["Opinion_Span"]["F1"]
        composite_score = t_f1 + 0.5 * a_f1 + 0.5 * o_f1

        is_best = composite_score > best_score
        star = "⭐ [BEST]" if is_best else ""

        print(f"  {trial_prefix}Epoch {epoch:02d}/{epochs:02d} [{epoch_dur:.1f}s] - "
              f"Train Loss: {epoch_loss:.4f} | Triplet F1: {t_f1:.2f}% | "
              f"Aspect F1: {a_f1:.2f}% | Opinion F1: {o_f1:.2f}% | "
              f"Score: {composite_score:.2f} {star}")

        epoch_histories.append({
            "epoch": epoch,
            "train_loss": round(epoch_loss, 4),
            "val_triplet_f1": t_f1,
            "val_aspect_f1": a_f1,
            "val_opinion_f1": o_f1,
            "composite_score": round(composite_score, 2),
            "lr": scheduler.get_last_lr()[0],
            "duration_sec": round(epoch_dur, 1)
        })

        if is_best:
            best_score = composite_score
            best_metrics = metrics
            best_metrics["epoch"] = epoch
            best_metrics["composite_score"] = round(composite_score, 2)

            if save_checkpoint_path:
                torch.save({
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "composite_score": composite_score,
                    "metrics": metrics,
                    "model_name": model_name,
                    "params": {
                        "learning_rate": learning_rate,
                        "batch_size": batch_size,
                        "weight_decay": weight_decay,
                        "dropout": dropout
                    }
                }, save_checkpoint_path)

    if save_checkpoint_path and checkpoint_dir:
        tokenizer.save_pretrained(checkpoint_dir)
        report_file = os.path.join(checkpoint_dir, "benchmark_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(best_metrics, f, indent=2, ensure_ascii=False)

    best_metrics["history"] = epoch_histories
    return best_metrics


def run_pipeline(args):
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    if args.gpu in GPU_UUID_MAP:
        os.environ["CUDA_VISIBLE_DEVICES"] = GPU_UUID_MAP[args.gpu]
        print(f"[*] Gán cứng GPU {args.gpu} (UUID: {GPU_UUID_MAP[args.gpu]})")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_file = os.path.join(args.splits_dir, "train.json")
    dev_file = os.path.join(args.splits_dir, "dev.json")
    test_file = os.path.join(args.splits_dir, "test.json")

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.report_dir, exist_ok=True)

    print("=" * 80)
    print("🚀 RADI-NET ASTE: ACADEMIC BENCHMARK PIPELINE - XLM-V BASE")
    print(f"  • Model Backbone      : {args.model_name}")
    print("  • Selection Criterion : Validation Composite Grounded ASTE F1 (Triplet F1 + 0.5*Asp + 0.5*Opn)")
    print(f"  • Random Seed         : {RANDOM_SEED} (Deterministic CuDNN Enabled)")
    print(f"  • Device Active       : {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print(f"  • Git Commit SHA      : {get_git_commit_sha()}")
    print("=" * 80)

    # Token length audit
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    audit_train = audit_truncation(train_file, tokenizer, max_len=args.max_len)
    audit_dev = audit_truncation(dev_file, tokenizer, max_len=args.max_len)
    audit_test = audit_truncation(test_file, tokenizer, max_len=args.max_len)

    print("\n" + "-" * 75)
    print("🔍 AUDIT ĐỘ DÀI TOKEN & TỶ LỆ TRUNCATION (XLM-V BASE)")
    print("-" * 75)
    print(f"  • TRAIN (N={audit_train['total_samples']}) | Max={audit_train['max_observed']}, >{args.max_len}: {audit_train['truncated_count']} ({audit_train['truncated_pct']}%)")
    print(f"  • DEV   (N={audit_dev['total_samples']}) | Max={audit_dev['max_observed']}, >{args.max_len}: {audit_dev['truncated_count']} ({audit_dev['truncated_pct']}%)")
    print(f"  • TEST  (N={audit_test['total_samples']}) | Max={audit_test['max_observed']}, >{args.max_len}: {audit_test['truncated_count']} ({audit_test['truncated_pct']}%)")
    print("-" * 75 + "\n")

    # STAGE 1: OPTUNA TUNING
    print("=" * 80)
    print("STAGE 1: KHỞI ĐỘNG OPTUNA TỐI ƯU HÓA SIÊU THAM SỐ (MỤC TIÊU: MAXIMIZE COMPOSITE VAL F1)")
    print("=" * 80)

    def objective(trial):
        lr = trial.suggest_float("learning_rate", 1.5e-5, 4.5e-5, log=True)
        bs = trial.suggest_categorical("batch_size", [16])
        wd = trial.suggest_float("weight_decay", 1e-4, 1e-2, log=True)
        drop = trial.suggest_float("dropout", 0.10, 0.25, step=0.05)

        prefix = f"[Trial {trial.number + 1}/{args.n_trials}] "
        print(f"\n[Optuna Trial {trial.number + 1}/{args.n_trials}] Cấu hình: lr={lr:.2e}, bs={bs}, wd={wd:.2e}, drop={drop:.2f}")

        metrics = train_epoch_loop(
            model_name=args.model_name,
            train_file=train_file,
            dev_file=dev_file,
            learning_rate=lr,
            batch_size=bs,
            weight_decay=wd,
            dropout=drop,
            epochs=args.trial_epochs,
            device=device,
            fp16=True,
            trial_prefix=prefix,
            max_len=args.max_len
        )
        gc.collect()
        torch.cuda.empty_cache()
        return metrics["composite_score"]

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=args.n_trials)

    best_p = study.best_params
    print("\n" + "=" * 80)
    print(f"🎉 OPTUNA HOÀN TẤT! Siêu tham số tối ưu nhất: {best_p} (Score: {study.best_value:.2f})")
    print("=" * 80)

    # STAGE 2: FULL TRAINING
    print("\n" + "=" * 80)
    print(f"STAGE 2: HUẤN LUYỆN CHÍNH THỨC TOÀN DIỆN ({args.final_epochs} EPOCHS)")
    print("=" * 80)

    ckpt_file = os.path.join(args.output_dir, "best_xlm_v_aste.pt")
    final_metrics = train_epoch_loop(
        model_name=args.model_name,
        train_file=train_file,
        dev_file=dev_file,
        learning_rate=best_p["learning_rate"],
        batch_size=best_p["batch_size"],
        weight_decay=best_p["weight_decay"],
        dropout=best_p["dropout"],
        epochs=args.final_epochs,
        device=device,
        fp16=True,
        save_checkpoint_path=ckpt_file,
        checkpoint_dir=args.output_dir,
        trial_prefix="[Final 30ep] ",
        max_len=args.max_len
    )

    # Pin artifacts to metadata
    meta = {
        "model_name": args.model_name,
        "random_seed": RANDOM_SEED,
        "selection_criterion": "composite_val_f1_grounded",
        "best_epoch": final_metrics.get("epoch", -1),
        "best_composite_score": final_metrics.get("composite_score", 0.0),
        "params": best_p,
        "max_len": args.max_len,
        "total_epochs": args.final_epochs,
        "git_commit_sha": get_git_commit_sha(),
        "dataset_md5": {
            "train": get_file_md5(train_file),
            "dev": get_file_md5(dev_file),
            "test": get_file_md5(test_file)
        },
        "truncation_audit": {
            "train": audit_train,
            "dev": audit_dev,
            "test": audit_test
        },
        "history": final_metrics.get("history", [])
    }
    meta_path = os.path.join(args.output_dir, "training_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"[+] Metadata hoàn chỉnh đã lưu: {meta_path}")

    # STAGE 3: TEST SET EVALUATION
    print("\n" + "=" * 80)
    print("STAGE 3: ĐÁNH GIÁ ĐỘC LẬP TRÊN TẬP TEST SPLIT (test.json)")
    print("=" * 80)

    test_dataset = XLMVJsonDataset(test_file, tokenizer, max_len=args.max_len, is_train=False)
    test_loader = DataLoader(test_dataset, batch_size=best_p["batch_size"], shuffle=False, collate_fn=aste_collate_fn)

    best_model = XLMVForASTE(model_name=args.model_name, dropout_rate=best_p["dropout"]).to(device)
    saved_state = torch.load(ckpt_file, map_location=device)
    best_model.load_state_dict(saved_state["model_state_dict"])

    test_start = time.time()
    test_metrics = evaluate_model(best_model, test_loader, device)
    test_time = round(time.time() - test_start, 2)

    test_metrics["model_name"] = args.model_name
    test_metrics["Evaluation_Time_Seconds"] = test_time
    test_metrics["Samples_Per_Second"] = round(len(test_dataset) / max(0.01, test_time), 2)

    test_report_file = os.path.join(args.report_dir, "test_report.json")
    with open(test_report_file, "w", encoding="utf-8") as f:
        json.dump(test_metrics, f, indent=2, ensure_ascii=False)
    print(f"[+] Báo cáo khoa học JSON đã lưu: {test_report_file}")

    print("\n" + "=" * 75)
    print("📊 BẢNG KẾT QUẢ THỰC NGHIỆM ĐÁNH GIÁ (XLM-V BASE)")
    print("=" * 75)
    print(f"{'Task / Metric':<26} | {'Precision (%)':<15} | {'Recall (%)':<15} | {'F1-Score (%)':<15}")
    print("-" * 75)
    tm = test_metrics["Triplet_Strict_Match"]
    am = test_metrics["Aspect_Span"]
    om = test_metrics["Opinion_Span"]
    print(f"{'Triplet Strict Match':<26} | {tm['Precision']:<15.2f} | {tm['Recall']:<15.2f} | {tm['F1']:<15.2f}")
    print(f"{'Aspect Extraction':<26} | {am['Precision']:<15.2f} | {am['Recall']:<15.2f} | {am['F1']:<15.2f}")
    print(f"{'Opinion Extraction':<26} | {om['Precision']:<15.2f} | {om['Recall']:<15.2f} | {om['F1']:<15.2f}")
    print("-" * 75)
    for p_name in ["NEG", "POS", "NEU"]:
        p_data = test_metrics["Polarity_Per_Class"][p_name]
        print(f"{'Polarity [' + p_name + ']':<26} | {p_data['Precision']:<15.2f} | {p_data['Recall']:<15.2f} | {p_data['F1']:<15.2f}")
    print("-" * 75)
    print(f"{'Macro Polarity F1':<26} | {'-':<15} | {'-':<15} | {test_metrics['Macro_Polarity_F1']:<15.2f}")
    print("=" * 75 + "\n")

    # STAGE 4: UPDATE BENCHMARK TABLE
    bench_script = os.path.join(SCRIPT_DIR, "benchmark_heuristic_baseline.py")
    if os.path.exists(bench_script):
        subprocess.run([sys.executable, bench_script], check=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tune & Train XLM-V Base ASTE")
    parser.add_argument("--model_name", type=str, default="facebook/xlm-v-base", help="Pretrained model identifier")
    parser.add_argument("--splits_dir", type=str, default=DEFAULT_SPLITS_DIR)
    parser.add_argument("--output_dir", type=str, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report_dir", type=str, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--n_trials", type=int, default=3, help="Optuna trials")
    parser.add_argument("--trial_epochs", type=int, default=5, help="Epochs per trial")
    parser.add_argument("--final_epochs", type=int, default=30, help="Full training epochs")
    parser.add_argument("--max_len", type=int, default=256, help="Max token length")
    parser.add_argument("--gpu", type=int, default=2, choices=[0, 2, 3], help="GPU device index")
    args = parser.parse_args()

    run_pipeline(args)
