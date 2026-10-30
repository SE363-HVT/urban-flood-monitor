#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/tune_and_train_phobert.py
--------------------------------------------------------------------------------
Optuna Hyperparameter Tuning (3 Trials x 5 Epochs) followed by Full 30-Epoch
Fine-Tuning of PhoBERT ASTE Model on HCMC Urban Flood v3 Splits (GPU 3).

Workflow:
    Stage 1: Optuna Optimization
      - 3 Trials exploring: learning_rate, batch_size, dropout, weight_decay.
      - 5 Epochs per trial on train.json evaluated against dev.json.
      - Objective: Maximize composite validation ASTE score (Triplet F1 + Spans).
    Stage 2: Full Fine-Tuning
      - Retrain from scratch using the winning hyperparameter configuration.
      - 30 Epochs with FP16 mixed precision and linear warmup.
      - Save optimal checkpoint, tokenizer, and benchmark metrics to:
        AI/finetune/checkpoints/phobert_aste_best/

Author: RadiNet AI Research Team
Domain: Multimodal ASTE Urban Flood Monitoring
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

# Ensure current directory is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RANDOM_SEED = 42

def seed_everything(seed: int = RANDOM_SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def seed_worker(worker_id):
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)

seed_everything(RANDOM_SEED)

def get_file_md5(filepath: str) -> str:
    md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            md5.update(chunk)
    return md5.hexdigest()

def get_git_commit_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"

def audit_phobert_truncation(tokenizer, train_file: str, dev_file: str, test_file: str, max_len: int = 160) -> Dict[str, Any]:
    audit_results = {}
    splits = [("train", train_file), ("dev", dev_file), ("test", test_file)]
    print("\n" + "-" * 75)
    print("🔍 AUDIT ĐỘ DÀI TOKEN & TỶ LỆ TRUNCATION (PHOBERT)")
    print("-" * 75)
    for name, path in splits:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        lens = [len(tokenizer.tokenize(x.get("content", {}).get("text", ""))) + 2 for x in data]
        trunc_c = sum(1 for l in lens if l > max_len)
        trunc_pct = round(trunc_c / len(data) * 100, 2)
        audit_results[name] = {
            "total_samples": len(data),
            "max_len_setting": max_len,
            "max_observed": max(lens) if lens else 0,
            "truncated_count": trunc_c,
            "truncated_pct": trunc_pct
        }
        print(f"  • {name.upper():<5} (N={len(data):>4}) | Max Tokens={max(lens):>3}, >{max_len}: {trunc_c:>2} ({trunc_pct:>4.2f}%)")
    print("-" * 75)
    sys.stdout.flush()
    return audit_results

from scripts.training.train_phobert_aste import (
    ASTEJsonDataset,
    aste_collate_fn,
    PhoBertForASTE,
    evaluate_model,
    RANDOM_SEED
)

# Set optuna logging level
optuna.logging.set_verbosity(optuna.logging.INFO)


def run_training_cycle(
    model_name: str,
    train_ds: ASTEJsonDataset,
    dev_ds: ASTEJsonDataset,
    tokenizer,
    device: torch.device,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    weight_decay: float,
    dropout: float,
    fp16: bool = True,
    save_checkpoint_path: str = None,
    checkpoint_dir: str = None,
    trial_prefix: str = ""
) -> Dict[str, Any]:
    """Runs a complete training and validation cycle."""
    seed_everything(RANDOM_SEED)
    g = torch.Generator()
    g.manual_seed(RANDOM_SEED)

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=aste_collate_fn,
        generator=g,
        worker_init_fn=seed_worker
    )
    dev_loader = DataLoader(
        dev_ds,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=aste_collate_fn
    )

    model = PhoBertForASTE(model_name=model_name, dropout_rate=dropout).to(device)

    no_decay = ["bias", "LayerNorm.weight"]
    optimizer_grouped_parameters = [
        {"params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)], "weight_decay": weight_decay},
        {"params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)], "weight_decay": 0.0},
    ]
    optimizer = torch.optim.AdamW(optimizer_grouped_parameters, lr=learning_rate)

    total_steps = len(train_loader) * epochs
    warmup_steps = int(0.10 * total_steps)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps)
    scaler = torch.amp.GradScaler('cuda', enabled=fp16 and device.type == "cuda")

    best_score = -1.0
    best_metrics = None

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
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, bio_tags=bio_tags, raw_batch=raw_batch)
                loss = outputs["loss"]

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

        avg_loss = total_loss / len(train_loader)
        sec = time.time() - start_t

        dev_metrics = evaluate_model(model, dev_loader, tokenizer, device)
        dev_triplet_f1 = dev_metrics["Triplet_Strict_Match"]["F1"]
        dev_asp_f1 = dev_metrics["Aspect_Span"]["F1"]
        dev_opn_f1 = dev_metrics["Opinion_Span"]["F1"]
        dev_score = dev_triplet_f1 * 2.0 + dev_asp_f1 + dev_opn_f1

        print(f"  {trial_prefix}Epoch [{epoch:02d}/{epochs:02d}] ({sec:.1f}s) - Loss: {avg_loss:.4f} | Dev Triplet F1: {dev_triplet_f1:.2f}% (Asp F1: {dev_asp_f1:.2f}%, Opn F1: {dev_opn_f1:.2f}%)")

        if dev_score > best_score:
            best_score = dev_score
            best_metrics = dev_metrics
            if save_checkpoint_path and checkpoint_dir:
                torch.save({
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "dev_metrics": dev_metrics,
                    "params": {
                        "learning_rate": learning_rate,
                        "batch_size": batch_size,
                        "weight_decay": weight_decay,
                        "dropout": dropout
                    }
                }, save_checkpoint_path)
                tokenizer.save_pretrained(checkpoint_dir)

    # Free memory
    del model, optimizer, scheduler, scaler
    gc.collect()
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "best_score": best_score,
        "best_metrics": best_metrics
    }


def main():
    parser = argparse.ArgumentParser(description="Optuna Tuning & Full Fine-tuning for PhoBERT ASTE")
    parser.add_argument("--model_name", type=str, default="vinai/phobert-base-v2", help="Backbone model")
    parser.add_argument("--splits_dir", type=str, default="data/processed/splits", help="Directory of train, dev, test json")
    parser.add_argument("--output_dir", type=str, default="AI/finetune/checkpoints/phobert_aste_best", help="Checkpoint output folder")
    parser.add_argument("--report_dir", type=str, default=None, help="Directory to save benchmark report json")
    parser.add_argument("--n_trials", type=int, default=3, help="Number of Optuna trials")
    parser.add_argument("--trial_epochs", type=int, default=5, help="Epochs per Optuna trial")
    parser.add_argument("--final_epochs", type=int, default=30, help="Epochs for final fine-tuning")
    parser.add_argument("--device", type=str, default="cuda", help="Device (cuda or cpu)")
    parser.add_argument("--fp16", action="store_true", default=True, help="Mixed precision FP16")
    args = parser.parse_args()

    device = torch.device(args.device if torch.cuda.is_available() and args.device == "cuda" else "cpu")

    print("=" * 80)
    print("🌊 Optuna Hyperparameter Search (3 Trials x 5 Epochs) & PhoBERT ASTE Training")
    print("=" * 80)
    print(f"Device: {device} ({torch.cuda.get_device_name(0) if device.type == 'cuda' else 'CPU'})")
    print(f"Splits: {args.splits_dir}")
    print(f"Target Checkpoint Dir: {args.output_dir}\n")

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    train_path = os.path.join(args.splits_dir, "train.json")
    dev_path = os.path.join(args.splits_dir, "dev.json")
    test_path = os.path.join(args.splits_dir, "test.json")

    # Data Artifact Hashing & Truncation Audit
    train_md5 = get_file_md5(train_path)
    dev_md5 = get_file_md5(dev_path)
    test_md5 = get_file_md5(test_path)
    git_sha = get_git_commit_sha()
    truncation_audit = audit_phobert_truncation(tokenizer, train_path, dev_path, test_path, max_len=160)

    train_ds = ASTEJsonDataset(train_path, tokenizer, max_len=160, is_train=True)
    dev_ds = ASTEJsonDataset(dev_path, tokenizer, max_len=160, is_train=False)
    test_ds = ASTEJsonDataset(test_path, tokenizer, max_len=160, is_train=False)

    print(f"Dataset Loaded: Train={len(train_ds):,} | Dev={len(dev_ds):,} | Test={len(test_ds):,}\n")

    # ==============================================================================
    # STAGE 1: OPTUNA HYPERPARAMETER TUNING
    # ==============================================================================
    print("=" * 80)
    print(f"🔬 STAGE 1: RUNNING OPTUNA STUDY ({args.n_trials} Trials, {args.trial_epochs} Epochs each)")
    print("=" * 80)

    def objective(trial: optuna.Trial) -> float:
        lr = trial.suggest_float("learning_rate", 2.0e-5, 4.5e-5, log=True)
        batch_size = trial.suggest_categorical("batch_size", [16])  # 16 is optimal for RTX 2080 Ti
        dropout = trial.suggest_float("dropout", 0.10, 0.20, step=0.05)
        weight_decay = trial.suggest_float("weight_decay", 1e-4, 0.02, log=True)

        prefix = f"[Trial {trial.number + 1}/{args.n_trials}] (lr={lr:.2e}, bs={batch_size}, drop={dropout:.2f}, wd={weight_decay:.4f}) "
        print(f"\n{prefix}Starting {args.trial_epochs} epochs...")

        res = run_training_cycle(
            model_name=args.model_name,
            train_ds=train_ds,
            dev_ds=dev_ds,
            tokenizer=tokenizer,
            device=device,
            epochs=args.trial_epochs,
            batch_size=batch_size,
            learning_rate=lr,
            weight_decay=weight_decay,
            dropout=dropout,
            fp16=args.fp16,
            trial_prefix=f"[Trial {trial.number+1}] "
        )

        val_score = res["best_score"]
        dev_triplet_f1 = res["best_metrics"]["Triplet_Strict_Match"]["F1"]
        print(f"{prefix}--> Peak Dev Triplet F1: {dev_triplet_f1:.2f}% (Composite Score: {val_score:.2f})")
        return val_score

    study = optuna.create_study(
        study_name="phobert_aste_v3_tuning",
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=RANDOM_SEED)
    )
    study.optimize(objective, n_trials=args.n_trials)

    print("\n" + "=" * 80)
    print("🎯 OPTUNA TUNING COMPLETE!")
    print("=" * 80)
    print(f"Best Trial #{study.best_trial.number + 1} with Score: {study.best_value:.2f}")
    print("Best Hyperparameters:")
    for k, v in study.best_params.items():
        print(f"  • {k}: {v}")

    os.makedirs(args.output_dir, exist_ok=True)
    study_report = {
        "best_trial_number": study.best_trial.number + 1,
        "best_score": study.best_value,
        "best_params": study.best_params,
        "all_trials": [
            {
                "number": t.number + 1,
                "value": t.value,
                "params": t.params,
                "state": str(t.state)
            }
            for t in study.trials
        ]
    }
    with open(os.path.join(args.output_dir, "optuna_study.json"), "w", encoding="utf-8") as f:
        json.dump(study_report, f, indent=2)

    # ==============================================================================
    # STAGE 2: FINAL FULL FINE-TUNING (30 EPOCHS) WITH BEST PARAMETERS
    # ==============================================================================
    best_lr = study.best_params["learning_rate"]
    best_bs = study.best_params["batch_size"]
    best_drop = study.best_params["dropout"]
    best_wd = study.best_params["weight_decay"]

    print("\n" + "=" * 80)
    print(f"🚀 STAGE 2: FULL FINE-TUNING FOR {args.final_epochs} EPOCHS WITH OPTIMAL HYPERPARAMETERS")
    print(f"   Config: lr={best_lr:.2e}, batch_size={best_bs}, dropout={best_drop}, weight_decay={best_wd:.4f}")
    print("=" * 80)

    ckpt_path = os.path.join(args.output_dir, "best_phobert_aste.pt")
    final_res = run_training_cycle(
        model_name=args.model_name,
        train_ds=train_ds,
        dev_ds=dev_ds,
        tokenizer=tokenizer,
        device=device,
        epochs=args.final_epochs,
        batch_size=best_bs,
        learning_rate=best_lr,
        weight_decay=best_wd,
        dropout=best_drop,
        fp16=args.fp16,
        save_checkpoint_path=ckpt_path,
        checkpoint_dir=args.output_dir,
        trial_prefix="[Final 30ep] "
    )

    # ==============================================================================
    # FINAL INDEPENDENT TEST BENCHMARK
    # ==============================================================================
    print("\n" + "=" * 80)
    print("🏆 FINAL BENCHMARK EVALUATION ON INDEPENDENT TEST SET (test.json)")
    print("=" * 80)

    test_loader = DataLoader(test_ds, batch_size=best_bs, shuffle=False, collate_fn=aste_collate_fn)
    best_model = PhoBertForASTE(model_name=args.model_name, dropout_rate=best_drop).to(device)
    saved_ckpt = torch.load(ckpt_path, map_location=device)
    best_model.load_state_dict(saved_ckpt["model_state_dict"])

    test_metrics = evaluate_model(best_model, test_loader, tokenizer, device)

    report_path = os.path.join(args.output_dir, "benchmark_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(test_metrics, f, indent=2, ensure_ascii=False)

    training_meta = {
        "model_name": args.model_name,
        "random_seed": RANDOM_SEED,
        "selection_criterion": "composite_val_f1_grounded",
        "best_epoch": saved_ckpt.get("epoch", 0),
        "best_composite_score": final_res.get("best_score", 0.0),
        "params": {
            "learning_rate": best_lr,
            "batch_size": best_bs,
            "dropout": best_drop,
            "weight_decay": best_wd
        },
        "max_len": 160,
        "total_epochs": args.final_epochs,
        "git_commit_sha": git_sha,
        "dataset_md5": {
            "train": train_md5,
            "dev": dev_md5,
            "test": test_md5
        },
        "truncation_audit": truncation_audit,
        "hardware": {
            "device": str(device),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
            "torch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available()
        }
    }
    with open(os.path.join(args.output_dir, "training_meta.json"), "w", encoding="utf-8") as f:
        json.dump(training_meta, f, indent=2, ensure_ascii=False)

    print("\n✅ Final Academic Benchmark Results (ICWSM / KDD Standard):")
    print(f"  • Triplet Strict Match F1 : {test_metrics['Triplet_Strict_Match']['F1']:.2f}% (P: {test_metrics['Triplet_Strict_Match']['Precision']}%, R: {test_metrics['Triplet_Strict_Match']['Recall']}%)")
    print(f"  • Aspect Entity F1        : {test_metrics['Aspect_Span']['F1']:.2f}% (P: {test_metrics['Aspect_Span']['Precision']}%, R: {test_metrics['Aspect_Span']['Recall']}%)")
    print(f"  • Opinion Expression F1   : {test_metrics['Opinion_Span']['F1']:.2f}% (P: {test_metrics['Opinion_Span']['Precision']}%, R: {test_metrics['Opinion_Span']['Recall']}%)")
    print(f"  • Macro Polarity F1       : {test_metrics['Macro_Polarity_F1']:.2f}%")
    for pol in ["NEG", "POS", "NEU"]:
        p_info = test_metrics["Polarity_Per_Class"][pol]
        print(f"    - [{pol}] F1: {p_info['F1']:.2f}% (P: {p_info['Precision']}%, R: {p_info['Recall']}%, Gold: {p_info['Gold']})")

    print(f"\nSaved optimal model, study report, and benchmark metrics to: {args.output_dir}")

    if args.report_dir:
        os.makedirs(args.report_dir, exist_ok=True)
        report_file = os.path.join(args.report_dir, "test_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(test_metrics, f, indent=2, ensure_ascii=False)
        study_src = os.path.join(args.output_dir, "optuna_study.json")
        if os.path.exists(study_src):
            with open(os.path.join(args.report_dir, "optuna_study.json"), "w", encoding="utf-8") as f_dst:
                with open(study_src, "r", encoding="utf-8") as f_src:
                    f_dst.write(f_src.read())
        print(f"[+] Đã xuất báo cáo test tại: {report_file}")
        # Auto update master benchmark table
        update_script = os.path.join(PROJECT_ROOT, "scripts", "benchmark_heuristic_baseline.py")
        subprocess.run([sys.executable, "-u", update_script], env=os.environ)


if __name__ == "__main__":
    main()
