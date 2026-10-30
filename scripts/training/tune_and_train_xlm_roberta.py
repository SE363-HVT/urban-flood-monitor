#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/tune_and_train_xlm_roberta.py
--------------------------------------------------------------------------------
Optuna Hyperparameter Tuning (3 Trials x 5 Epochs) followed by Full 30-Epoch
Fine-Tuning of XLM-RoBERTa ASTE Model on HCMC Urban Flood v3 Splits.

Workflow:
    Stage 1: Optuna Optimization
      - 3 Trials exploring: learning_rate, batch_size, dropout, weight_decay.
      - 5 Epochs per trial on train.json evaluated against dev.json.
      - Objective: Maximize composite validation ASTE score (Triplet F1 + Spans).
    Stage 2: Full Fine-Tuning
      - Retrain from scratch using the winning hyperparameter configuration.
      - 30 Epochs with FP16 mixed precision and linear warmup.
      - Save optimal checkpoint, tokenizer, and benchmark metrics to:
        AI/xlm_roberta/base/finetune/checkpoints/
    Stage 3: Independent Test Split Evaluation
      - Evaluates on test.json (462 test samples).
      - Saves benchmark report to AI/xlm_roberta/base/test/benchmark_reports/test_report.json.
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

from scripts.training.train_xlm_roberta_aste import (
    XLMRobertaJsonDataset,
    aste_collate_fn,
    XLMRobertaForASTE,
    evaluate_model,
    RANDOM_SEED
)

optuna.logging.set_verbosity(optuna.logging.INFO)

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

def audit_xlm_roberta_truncation(tokenizer, train_file: str, dev_file: str, test_file: str, max_len: int = 160) -> Dict[str, Any]:
    audit_results = {}
    splits = [("train", train_file), ("dev", dev_file), ("test", test_file)]
    print("\n" + "-" * 75)
    print("🔍 AUDIT ĐỘ DÀI TOKEN & TỶ LỆ TRUNCATION (XLM-ROBERTA)")
    print("-" * 75)
    for name, path in splits:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        lens = [len(tokenizer(x.get("content", {}).get("text", "")).input_ids) for x in data]
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

GPU_UUID_MAP = {
    0: "GPU-402b1880-531f-0736-be2e-03a8a229590b",
    2: "GPU-40888ad5-fe5d-17c8-a236-4b0fd1d97e6f",
    3: "GPU-17220462-c4da-32ae-f317-0c0e97d6e63e"
}


def run_training_cycle(
    model_name: str,
    train_ds: XLMRobertaJsonDataset,
    dev_ds: XLMRobertaJsonDataset,
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

    model = XLMRobertaForASTE(model_name=model_name, dropout_rate=dropout).to(device)

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

    del model, optimizer, scheduler, train_loader, dev_loader
    torch.cuda.empty_cache()
    gc.collect()

    return best_metrics


def main():
    parser = argparse.ArgumentParser(description="Optuna Tuning and Training for XLM-RoBERTa ASTE")
    parser.add_argument("--model_name", type=str, default="xlm-roberta-base", help="Pretrained model identifier")
    parser.add_argument("--train_file", type=str, default="data/processed/splits/train.json")
    parser.add_argument("--dev_file", type=str, default="data/processed/splits/dev.json")
    parser.add_argument("--test_file", type=str, default="data/processed/splits/test.json")
    parser.add_argument("--trials", type=int, default=3, help="Optuna trials count")
    parser.add_argument("--trial_epochs", type=int, default=5, help="Epochs per Optuna trial")
    parser.add_argument("--train_epochs", type=int, default=30, help="Full fine-tuning epochs")
    parser.add_argument("--gpu", type=int, default=2, choices=[0, 2, 3], help="GPU index (0, 2, or 3)")
    parser.add_argument("--checkpoint_dir", type=str, default="AI/xlm_roberta/base/finetune/checkpoints")
    parser.add_argument("--report_dir", type=str, default="AI/xlm_roberta/base/test/benchmark_reports")
    parser.add_argument("--skip_tune", action="store_true", help="Skip Optuna and train with default hyperparams")

    args = parser.parse_args()

    gpu_uuid = GPU_UUID_MAP[args.gpu]
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu_uuid
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("=" * 80)
    print("🚀 RADI-NET ASTE: OPTUNA TUNING & FINE-TUNING XLM-ROBERTA-BASE")
    print(f"  • Model Backbone : {args.model_name}")
    print(f"  • GPU Target     : GPU {args.gpu} (UUID: {gpu_uuid})")
    print(f"  • Device Active  : {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print(f"  • Optuna Config  : {args.trials} Trials × {args.trial_epochs} Epochs")
    print(f"  • Final Training : {args.train_epochs} Epochs")
    print(f"  • Output Path    : {args.checkpoint_dir}")
    print("=" * 80)

    # 1. Load Tokenizer & Datasets
    print(f"\n[*] Đang nạp tokenizer: {args.model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    train_path = os.path.join(PROJECT_ROOT, args.train_file)
    dev_path = os.path.join(PROJECT_ROOT, args.dev_file)
    test_path = os.path.join(PROJECT_ROOT, args.test_file)

    train_md5 = get_file_md5(train_path)
    dev_md5 = get_file_md5(dev_path)
    test_md5 = get_file_md5(test_path)
    git_sha = get_git_commit_sha()
    truncation_audit = audit_xlm_roberta_truncation(tokenizer, train_path, dev_path, test_path, max_len=160)

    train_ds = XLMRobertaJsonDataset(train_path, tokenizer, max_len=160, is_train=True)
    dev_ds = XLMRobertaJsonDataset(dev_path, tokenizer, max_len=160, is_train=False)
    test_ds = XLMRobertaJsonDataset(test_path, tokenizer, max_len=160, is_train=False)

    print(f"[*] Kích thước dữ liệu: Train={len(train_ds):,} | Dev={len(dev_ds):,} | Test={len(test_ds):,}")

    os.makedirs(args.checkpoint_dir, exist_ok=True)
    os.makedirs(args.report_dir, exist_ok=True)

    # 2. Stage 1: Optuna Hyperparameter Tuning
    best_params = {
        "learning_rate": 3.0e-5,
        "batch_size": 16,
        "dropout": 0.15,
        "weight_decay": 0.001
    }

    if not args.skip_tune and args.trials > 0:
        print("\n" + "=" * 80)
        print("STAGE 1: KHỞI ĐỘNG OPTUNA TÌM SIÊU THAM SỐ TỐI ƯU")
        print("=" * 80)

        def objective(trial: optuna.Trial) -> float:
            lr = trial.suggest_float("learning_rate", 1.5e-5, 4.5e-5, log=True)
            bs = trial.suggest_categorical("batch_size", [16, 24])
            drop = trial.suggest_float("dropout", 0.10, 0.20, step=0.05)
            wd = trial.suggest_float("weight_decay", 1e-4, 1e-2, log=True)

            print(f"\n[Optuna Trial {trial.number + 1}/{args.trials}] Cấu hình: lr={lr:.2e}, bs={bs}, drop={drop:.2f}, wd={wd:.2e}")

            metrics = run_training_cycle(
                model_name=args.model_name,
                train_ds=train_ds,
                dev_ds=dev_ds,
                tokenizer=tokenizer,
                device=device,
                epochs=args.trial_epochs,
                batch_size=bs,
                learning_rate=lr,
                weight_decay=wd,
                dropout=drop,
                trial_prefix=f"[Trial {trial.number + 1}] "
            )
            score = metrics["composite_score"]
            print(f"==> Kết thúc Trial {trial.number + 1}: Composite Score = {score:.2f} (Triplet F1 = {metrics['Triplet_Strict_Match']['F1']:.2f}%)")
            return score

        study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=RANDOM_SEED))
        study.optimize(objective, n_trials=args.trials)

        best_params = study.best_params
        best_score = study.best_value

        study_summary = {
            "best_trial_number": study.best_trial.number + 1,
            "best_value": round(best_score, 2),
            "best_params": best_params,
            "all_trials": [
                {
                    "trial": t.number + 1,
                    "value": round(t.value, 2) if t.value is not None else None,
                    "params": t.params
                }
                for t in study.trials
            ]
        }
        study_file = os.path.join(args.checkpoint_dir, "optuna_study.json")
        with open(study_file, "w", encoding="utf-8") as f:
            json.dump(study_summary, f, indent=2)

        print("\n" + "=" * 80)
        print("🎉 KẾT QUẢ OPTUNA:")
        print(f"  • Best Trial  : #{study.best_trial.number + 1}")
        print(f"  • Best Score  : {best_score:.2f}")
        print(f"  • Best Params : {best_params}")
        print(f"  • Đã lưu kết quả tại: {study_file}")
        print("=" * 80)

    # 3. Stage 2: Full Fine-Tuning 30 Epochs
    print("\n" + "=" * 80)
    print(f"STAGE 2: BẮT ĐẦU FINE-TUNING TOÀN DIỆN {args.train_epochs} EPOCHS VỚI THAM SỐ THẮNG CUỘC")
    print(f"  • Learning Rate : {best_params['learning_rate']}")
    print(f"  • Batch Size    : {best_params['batch_size']}")
    print(f"  • Dropout       : {best_params['dropout']}")
    print(f"  • Weight Decay  : {best_params['weight_decay']}")
    print("=" * 80)

    checkpoint_file = os.path.join(args.checkpoint_dir, "best_xlm_roberta_aste.pt")

    final_metrics = run_training_cycle(
        model_name=args.model_name,
        train_ds=train_ds,
        dev_ds=dev_ds,
        tokenizer=tokenizer,
        device=device,
        epochs=args.train_epochs,
        batch_size=best_params["batch_size"],
        learning_rate=best_params["learning_rate"],
        weight_decay=best_params["weight_decay"],
        dropout=best_params["dropout"],
        save_checkpoint_path=checkpoint_file,
        checkpoint_dir=args.checkpoint_dir,
        trial_prefix="[Full Train] "
    )

    print("\n" + "=" * 80)
    print("✅ HUẤN LUYỆN TOÀN DIỆN HOÀN TẤT!")
    print(f"  • Checkpoint tối ưu : {checkpoint_file}")
    print(f"  • Epoch tốt nhất    : {final_metrics['epoch']}")
    print(f"  • Dev Triplet F1    : {final_metrics['Triplet_Strict_Match']['F1']:.2f}%")
    print("=" * 80)

    # 4. Stage 3: Independent Test Evaluation
    print("\n" + "=" * 80)
    print(f"STAGE 3: ĐÁNH GIÁ ĐỘC LẬP TRÊN TẬP TEST ({len(test_ds)} MẪU)")
    print("=" * 80)

    best_ckpt = torch.load(checkpoint_file, map_location=device, weights_only=False)
    eval_model = XLMRobertaForASTE(model_name=args.model_name, dropout_rate=best_params["dropout"]).to(device)
    eval_model.load_state_dict(best_ckpt["model_state_dict"])

    test_loader = DataLoader(test_ds, batch_size=best_params["batch_size"], shuffle=False, collate_fn=aste_collate_fn)
    test_metrics = evaluate_model(eval_model, test_loader, device)

    test_report_file = os.path.join(args.report_dir, "test_report.json")
    with open(test_report_file, "w", encoding="utf-8") as f:
        json.dump(test_metrics, f, indent=2, ensure_ascii=False)

    training_meta = {
        "model_name": args.model_name,
        "random_seed": RANDOM_SEED,
        "selection_criterion": "composite_val_f1_grounded",
        "best_epoch": final_metrics.get("epoch", 0),
        "best_composite_score": final_metrics.get("composite_score", 0.0),
        "params": best_params,
        "max_len": 160,
        "total_epochs": args.train_epochs,
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
    with open(os.path.join(args.checkpoint_dir, "training_meta.json"), "w", encoding="utf-8") as f:
        json.dump(training_meta, f, indent=2, ensure_ascii=False)

    # Also mirror optuna study into test benchmark reports
    study_source = os.path.join(args.checkpoint_dir, "optuna_study.json")
    if os.path.exists(study_source):
        with open(os.path.join(args.report_dir, "optuna_study.json"), "w", encoding="utf-8") as f:
            with open(study_source, "r", encoding="utf-8") as sf:
                f.write(sf.read())

    print("\n" + "=" * 80)
    print("📊 BẢNG KẾT QUẢ THỰC NGHIỆM ĐÁNH GIÁ TRÊN TẬP TEST (XLM-ROBERTA-BASE)")
    print("=" * 80)
    tm = test_metrics["Triplet_Strict_Match"]
    am = test_metrics["Aspect_Span"]
    om = test_metrics["Opinion_Span"]
    print(f"{'Metric / Task':<25} | {'Precision (%)':<14} | {'Recall (%)':<14} | {'F1-Score (%)':<14}")
    print("-" * 75)
    print(f"{'Triplet Strict Match':<25} | {tm['Precision']:<14.2f} | {tm['Recall']:<14.2f} | {tm['F1']:<14.2f}")
    print(f"{'Aspect Extraction':<25} | {am['Precision']:<14.2f} | {am['Recall']:<14.2f} | {am['F1']:<14.2f}")
    print(f"{'Opinion Extraction':<25} | {om['Precision']:<14.2f} | {om['Recall']:<14.2f} | {om['F1']:<14.2f}")
    print("-" * 75)
    for p_name in ["NEG", "POS", "NEU"]:
        pm = test_metrics["Polarity_Per_Class"][p_name]
        print(f"{f'Polarity [{p_name}]':<25} | {pm['Precision']:<14.2f} | {pm['Recall']:<14.2f} | {pm['F1']:<14.2f}")
    print("-" * 75)
    print(f"{'Macro Polarity F1':<25} | {'-':<14} | {'-':<14} | {test_metrics['Macro_Polarity_F1']:<14.2f}")
    print("=" * 80)
    print(f"[+] Báo cáo đã lưu vào: {test_report_file}")


if __name__ == "__main__":
    main()
