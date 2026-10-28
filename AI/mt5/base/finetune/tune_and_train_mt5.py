#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/tune_and_train_mt5.py
--------------------------------------------------------------------------------
Optuna Hyperparameter Tuning (3 Trials x 5 Epochs) followed by Full 30-Epoch
Fine-Tuning of mT5-Base (google/mt5-base) on HCMC Flood V3 Splits.

Workflow:
  Stage 1: Optuna Optimization (3 Trials x 5 Epochs)
    - Search Space: learning_rate (1e-4 - 5e-4), batch_size (4, 8), weight_decay (0.01 - 0.1)
    - Objective: Maximize Validation Triplet Strict Match F1
  Stage 2: Full Fine-Tuning (30 Epochs)
    - Full training from scratch with winning configuration
    - Evaluates each epoch on dev.json; saves best Triplet F1 checkpoint
    - Persists audit metadata, commit SHA, and dataset MD5 hashes to training_meta.json
  Stage 3: Independent Test Split Evaluation
    - Evaluates on test.json (462 samples)
    - Saves JSON benchmark report to AI/mt5/base/test/benchmark_reports/test_report.json
  Stage 4: Master Benchmark Table Update
    - Triggers scripts/benchmark_heuristic_baseline.py to sync AI/results/
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
from torch.utils.data import DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    get_linear_schedule_with_warmup
)
import optuna

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.train_mt5_aste import (
    MT5ASTEDataset,
    mt5_collate_fn,
    evaluate_val_loss_and_f1,
    audit_truncation,
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
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "AI", "mt5", "base", "finetune", "checkpoints", "best_aste_model")
DEFAULT_REPORT_DIR = os.path.join(PROJECT_ROOT, "AI", "mt5", "base", "test", "benchmark_reports")


def run_mt5_epoch_loop(
    model_name: str,
    train_file: str,
    dev_file: str,
    learning_rate: float,
    batch_size: int,
    weight_decay: float,
    epochs: int,
    device: torch.device,
    save_checkpoint_path: str = None,
    trial_prefix: str = "",
    max_source_len: int = 256,
    max_target_len: int = 128,
    label_smoothing: float = 0.1,
    accum_steps: int = 2
) -> Dict[str, Any]:
    seed_everything(RANDOM_SEED)
    g = torch.Generator()
    g.manual_seed(RANDOM_SEED)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0

    train_ds = MT5ASTEDataset(train_file, tokenizer, max_source_len, max_target_len)
    dev_ds = MT5ASTEDataset(dev_file, tokenizer, max_source_len, max_target_len)

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=lambda b: mt5_collate_fn(b, pad_id),
        worker_init_fn=seed_worker,
        generator=g,
        num_workers=0
    )
    dev_loader = DataLoader(
        dev_ds,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=lambda b: mt5_collate_fn(b, pad_id),
        num_workers=0
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, tie_word_embeddings=False).to(device)

    from transformers import Adafactor
    optimizer = Adafactor(
        model.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay,
        scale_parameter=False,
        relative_step=False,
        warmup_init=False
    )

    total_optimizer_steps = (len(train_loader) // accum_steps) * epochs
    warmup_steps = int(0.10 * total_optimizer_steps)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_optimizer_steps)

    best_val_f1 = -1.0
    best_epoch = -1
    best_metrics = {}
    history = []

    for ep in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        step_c = 0
        ep_start = time.time()

        optimizer.zero_grad()
        for step, batch in enumerate(train_loader):
            in_ids = batch["input_ids"].to(device, non_blocking=True)
            att_m = batch["attention_mask"].to(device, non_blocking=True)
            labs = batch["labels"].to(device, non_blocking=True)

            out = model(input_ids=in_ids, attention_mask=att_m, labels=labs, label_smoothing=label_smoothing)
            loss = out.loss / accum_steps
            loss.backward()

            if (step + 1) % accum_steps == 0 or (step + 1) == len(train_loader):
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                optimizer.zero_grad()
                scheduler.step()

            train_loss += (loss * accum_steps).item()
            step_c += 1

        avg_train_loss = round(train_loss / max(1, step_c), 4)

        val_loss, val_m = evaluate_val_loss_and_f1(
            model=model,
            val_loader=dev_loader,
            tokenizer=tokenizer,
            val_dataset=dev_ds,
            device=device,
            max_target_len=max_target_len,
            label_smoothing=label_smoothing
        )

        val_trip_f1 = val_m["Triplet_Strict_Match"]["F1"]
        ep_duration = round(time.time() - ep_start, 2)

        history.append({
            "epoch": ep,
            "train_loss": avg_train_loss,
            "val_loss": val_loss,
            "val_triplet_f1": val_trip_f1,
            "val_aspect_f1": val_m["Aspect_Span"]["F1"],
            "val_opinion_f1": val_m["Opinion_Span"]["F1"],
            "val_macro_pol_f1": val_m["Macro_Polarity_F1"],
            "duration_sec": ep_duration
        })

        is_best = val_trip_f1 > best_val_f1
        if is_best:
            best_val_f1 = val_trip_f1
            best_epoch = ep
            best_metrics = val_m
            if save_checkpoint_path is not None:
                os.makedirs(save_checkpoint_path, exist_ok=True)
                model.save_pretrained(save_checkpoint_path)
                tokenizer.save_pretrained(save_checkpoint_path)

        print(
            f"{trial_prefix}Epoch {ep:02d}/{epochs:02d} [{ep_duration}s] | "
            f"Train Loss: {avg_train_loss:.4f} | Val Loss: {val_loss:.4f} | "
            f"Val Triplet F1: {val_trip_f1:.2f}% | Asp F1: {val_m['Aspect_Span']['F1']:.2f}% | "
            f"Opn F1: {val_m['Opinion_Span']['F1']:.2f}% {'⭐' if is_best else ''}"
        )

    # Cleanup
    del model, optimizer, scheduler
    gc.collect()
    torch.cuda.empty_cache()

    return {
        "best_epoch": best_epoch,
        "best_val_f1": best_val_f1,
        "best_metrics": best_metrics,
        "history": history
    }


def run_pipeline(args):
    print("=" * 80)
    print("🚀 PIPELINE TỐI ƯU HÓA VÀ HUẤN LUYỆN mT5-BASE (google/mt5-base)")
    print(f"  • Model Backbone : {args.model_name}")
    print(f"  • GPU Device     : GPU {args.gpu}")
    print(f"  • Optuna Trials  : {args.n_trials} Trials x {args.trial_epochs} Epochs")
    print(f"  • Final Training : {args.final_epochs} Epochs")
    print(f"  • Checkpoint Out : {args.output_dir}")
    print(f"  • Report Out     : {args.report_dir}")
    print("=" * 80)

    # Set GPU
    if args.gpu in GPU_UUID_MAP:
        os.environ["CUDA_VISIBLE_DEVICES"] = GPU_UUID_MAP[args.gpu]
    else:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[+] Device khởi tạo: {device}")

    train_file = os.path.join(args.splits_dir, "train.json")
    dev_file = os.path.join(args.splits_dir, "dev.json")
    test_file = os.path.join(args.splits_dir, "test.json")

    # Sequence Length and Truncation Audit
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    audit_train = audit_truncation(train_file, tokenizer, args.max_source_len, args.max_target_len)
    audit_dev = audit_truncation(dev_file, tokenizer, args.max_source_len, args.max_target_len)
    audit_test = audit_truncation(test_file, tokenizer, args.max_source_len, args.max_target_len)

    print(f"[+] Truncation Audit:")
    print(f"    Train: {audit_train['total_samples']} samples | max_src: {audit_train['source_max_observed']} (trunc {audit_train['source_truncated_pct']}%) | max_tgt: {audit_train['target_max_observed']} (trunc {audit_train['target_truncated_pct']}%)")
    print(f"    Dev  : {audit_dev['total_samples']} samples | max_src: {audit_dev['source_max_observed']} (trunc {audit_dev['source_truncated_pct']}%) | max_tgt: {audit_dev['target_max_observed']} (trunc {audit_dev['target_truncated_pct']}%)")
    print(f"    Test : {audit_test['total_samples']} samples | max_src: {audit_test['source_max_observed']} (trunc {audit_test['source_truncated_pct']}%) | max_tgt: {audit_test['target_max_observed']} (trunc {audit_test['target_truncated_pct']}%)")

    # STAGE 1: OPTUNA HYPERPARAMETER TUNING
    print("\n" + "=" * 80)
    print(f"STAGE 1: OPTUNA HYPERPARAMETER OPTIMIZATION ({args.n_trials} Trials x {args.trial_epochs} Epochs)")
    print("=" * 80)

    def objective(trial: optuna.Trial) -> float:
        lr = trial.suggest_float("learning_rate", 2e-4, 1e-3, log=True)
        bs = trial.suggest_categorical("batch_size", [2])
        wd = trial.suggest_float("weight_decay", 0.01, 0.1)

        print(f"\n--- [Optuna Trial {trial.number + 1}/{args.n_trials}] LR: {lr:.2e} | BS: {bs} | WD: {wd:.4f} ---")
        res = run_mt5_epoch_loop(
            model_name=args.model_name,
            train_file=train_file,
            dev_file=dev_file,
            learning_rate=lr,
            batch_size=bs,
            weight_decay=wd,
            epochs=args.trial_epochs,
            device=device,
            trial_prefix=f"[Trial {trial.number+1}] ",
            max_source_len=args.max_source_len,
            max_target_len=args.max_target_len,
            label_smoothing=args.label_smoothing
        )
        return res["best_val_f1"]

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=RANDOM_SEED))
    study.optimize(objective, n_trials=args.n_trials)

    best_trial = study.best_trial
    best_p = best_trial.params
    print("\n" + "=" * 80)
    print(f"🏆 CẤU HÌNH THẮNG CUỘC TỪ OPTUNA (Trial {best_trial.number + 1}):")
    print(f"  • Learning Rate : {best_p['learning_rate']:.2e}")
    print(f"  • Batch Size    : {best_p['batch_size']}")
    print(f"  • Weight Decay  : {best_p['weight_decay']:.4f}")
    print(f"  • Best Val F1   : {best_trial.value:.2f}%")
    print("=" * 80)

    # STAGE 2: FULL FINE-TUNING (30 EPOCHS)
    print("\n" + "=" * 80)
    print(f"STAGE 2: HUẤN LUYỆN TOÀN DIỆN ({args.final_epochs} EPOCHS) VỚI HYPERPARAMETERS TỐI ƯU")
    print("=" * 80)

    final_res = run_mt5_epoch_loop(
        model_name=args.model_name,
        train_file=train_file,
        dev_file=dev_file,
        learning_rate=best_p["learning_rate"],
        batch_size=best_p["batch_size"],
        weight_decay=best_p["weight_decay"],
        epochs=args.final_epochs,
        device=device,
        save_checkpoint_path=args.output_dir,
        trial_prefix="[Final 30ep] ",
        max_source_len=args.max_source_len,
        max_target_len=args.max_target_len,
        label_smoothing=args.label_smoothing
    )

    # Save metadata
    meta = {
        "model_name": args.model_name,
        "random_seed": RANDOM_SEED,
        "selection_criterion": "val_triplet_strict_f1",
        "best_epoch": final_res.get("best_epoch", -1),
        "best_val_triplet_f1": final_res.get("best_val_f1", 0.0),
        "params": best_p,
        "max_source_len": args.max_source_len,
        "max_target_len": args.max_target_len,
        "label_smoothing": args.label_smoothing,
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
        "history": final_res.get("history", [])
    }
    meta_path = os.path.join(args.output_dir, "training_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"[+] Đã ghi metadata kiểm toán vào: {meta_path}")

    # STAGE 3: TEST SET EVALUATION
    print("\n" + "=" * 80)
    print("STAGE 3: ĐÁNH GIÁ ĐỘC LẬP TRÊN TẬP TEST SPLIT (test.json)")
    print("=" * 80)

    best_model = AutoModelForSeq2SeqLM.from_pretrained(args.output_dir).to(device)
    test_ds = MT5ASTEDataset(test_file, tokenizer, args.max_source_len, args.max_target_len)
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0
    test_loader = DataLoader(
        test_ds,
        batch_size=best_p["batch_size"],
        shuffle=False,
        collate_fn=lambda b: mt5_collate_fn(b, pad_id),
        num_workers=0
    )

    test_start = time.time()
    test_loss, test_m = evaluate_val_loss_and_f1(
        model=best_model,
        val_loader=test_loader,
        tokenizer=tokenizer,
        val_dataset=test_ds,
        device=device,
        max_target_len=args.max_target_len,
        label_smoothing=args.label_smoothing
    )
    test_time = round(time.time() - test_start, 2)

    test_m["model_name"] = args.model_name
    test_m["Evaluation_Time_Seconds"] = test_time
    test_m["Samples_Per_Second"] = round(len(test_ds) / max(0.01, test_time), 2)
    test_m["Test_Loss"] = test_loss

    os.makedirs(args.report_dir, exist_ok=True)
    test_report_file = os.path.join(args.report_dir, "test_report.json")
    with open(test_report_file, "w", encoding="utf-8") as f:
        json.dump(test_m, f, indent=2, ensure_ascii=False)
    print(f"[+] Báo cáo kết quả kiểm thử JSON đã lưu: {test_report_file}")

    print("\n" + "=" * 75)
    print("📊 BẢNG KẾT QUẢ THỰC NGHIỆM ĐÁNH GIÁ (mT5 BASE)")
    print("=" * 75)
    print(f"{'Task / Metric':<26} | {'Precision (%)':<15} | {'Recall (%)':<15} | {'F1-Score (%)':<15}")
    print("-" * 75)
    tm = test_m["Triplet_Strict_Match"]
    am = test_m["Aspect_Span"]
    om = test_m["Opinion_Span"]
    print(f"{'Triplet Strict Match':<26} | {tm['Precision']:<15.2f} | {tm['Recall']:<15.2f} | {tm['F1']:<15.2f}")
    print(f"{'Aspect Extraction':<26} | {am['Precision']:<15.2f} | {am['Recall']:<15.2f} | {am['F1']:<15.2f}")
    print(f"{'Opinion Extraction':<26} | {om['Precision']:<15.2f} | {om['Recall']:<15.2f} | {om['F1']:<15.2f}")
    print("-" * 75)
    for p_name in ["NEG", "POS", "NEU"]:
        p_data = test_m["Polarity_Per_Class"][p_name]
        print(f"{'Polarity [' + p_name + ']':<26} | {p_data['Precision']:<15.2f} | {p_data['Recall']:<15.2f} | {p_data['F1']:<15.2f}")
    print("-" * 75)
    print(f"{'Macro Polarity F1':<26} | {'-':<15} | {'-':<15} | {test_m['Macro_Polarity_F1']:<15.2f}")
    print("=" * 75 + "\n")

    # STAGE 4: UPDATE BENCHMARK TABLE
    bench_script = os.path.join(SCRIPT_DIR, "benchmark_heuristic_baseline.py")
    if os.path.exists(bench_script):
        subprocess.run([sys.executable, bench_script], check=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tune & Train mT5-Base ASTE")
    parser.add_argument("--model_name", type=str, default="google/mt5-base")
    parser.add_argument("--splits_dir", type=str, default=DEFAULT_SPLITS_DIR)
    parser.add_argument("--output_dir", type=str, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report_dir", type=str, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--n_trials", type=int, default=3, help="Optuna trials")
    parser.add_argument("--trial_epochs", type=int, default=5, help="Epochs per trial")
    parser.add_argument("--final_epochs", type=int, default=30, help="Full training epochs")
    parser.add_argument("--max_source_len", type=int, default=256)
    parser.add_argument("--max_target_len", type=int, default=128)
    parser.add_argument("--label_smoothing", type=float, default=0.1)
    parser.add_argument("--gpu", type=int, default=0, choices=[0, 2, 3], help="GPU device index")
    args = parser.parse_args()

    run_pipeline(args)
