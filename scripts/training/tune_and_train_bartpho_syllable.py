#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/tune_and_train_bartpho_syllable.py
--------------------------------------------------------------------------------
Rigorous Academic Benchmark Fine-Tuning Pipeline for BARTpho Syllable Base:
- Backbone: vinai/bartpho-syllable-base (131.5M parameters)
- Generative Seq2Seq ASTE on HCMC Flood V3 multimodal dataset
- Fully Seeded Reproducibility (Seed 42, deterministic CuDNN, seeded Generator)
- Truncation Audit & Safeguards (max_source_len=256, max_target_len=200; target truncation ~0%)
- Checkpoint Selection: Validation Triplet F1 (Strict Match, greedy decode)
- Artifact Pinning in Metadata: MD5 hashes of train/val/test splits, Git commit SHA
- Label Smoothing: 0.1 for enhanced Seq2Seq generalization

Workflow:
  Stage 1: Optuna Optimization (3 Trials x 5 Epochs) maximizing Validation Triplet F1
  Stage 2: Full Fine-Tuning (30 Epochs) with winning hyperparameters, saving best F1 checkpoint
  Stage 3: Independent Test Split Evaluation on test.json (462 samples)
  Stage 4: Inference Verification Demo
  Stage 5: Master Comparison Table Update in AI/results/
"""

import os
import sys
import gc
import json
import time
import random
import hashlib
import argparse
import subprocess
import unicodedata
import re
from typing import Dict, Any, List, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
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

PYTHON_EXE = "/home/counting/anaconda3/envs/ryan_env/bin/python"

GPU_UUID_MAP = {
    0: "GPU-402b1880-531f-0736-be2e-03a8a229590b",
    2: "GPU-40888ad5-fe5d-17c8-a236-4b0fd1d97e6f",
    3: "GPU-17220462-c4da-32ae-f317-0c0e97d6e63e"
}

DEFAULT_DATA_DIR = os.path.join(PROJECT_ROOT, "AI", "bartpho", "data")
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "AI", "bartpho", "syllable_base", "finetune", "checkpoints", "best_aste_model")
DEFAULT_REPORT_DIR = os.path.join(PROJECT_ROOT, "AI", "bartpho", "syllable_base", "test", "benchmark_reports")


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


def parse_triplets_from_string(text: str) -> List[Dict[str, str]]:
    """Linearized Seq2Seq output parser -> list of normalized aspect-opinion-polarity triplets."""
    if not text or text.strip().lower() in ["none", ""]:
        return []

    triplets = []
    items = re.findall(r'\((.*?)\)', text)
    if not items:
        items = text.split(";")

    seen = set()

    for item in items:
        parts = [p.strip() for p in item.split("|")]
        if len(parts) >= 3:
            asp = unicodedata.normalize('NFC', parts[0]).strip()
            opi = unicodedata.normalize('NFC', parts[1]).strip()
            pol = parts[2].strip().upper()
            if pol not in ["POS", "NEG", "NEU"]:
                pol = "NEG"
            key = (asp.lower(), opi.lower(), pol)
            if asp and opi and key not in seen:
                seen.add(key)
                triplets.append({"aspect": asp, "opinion": opi, "polarity": pol})
        elif len(parts) == 2:
            asp = unicodedata.normalize('NFC', parts[0]).strip()
            opi = unicodedata.normalize('NFC', parts[1]).strip()
            key = (asp.lower(), opi.lower(), "NEG")
            if asp and opi and key not in seen:
                seen.add(key)
                triplets.append({"aspect": asp, "opinion": opi, "polarity": "NEG"})

    return triplets


class ASTEDataset(Dataset):
    def __init__(self, json_path: str, tokenizer, max_source_len: int = 256, max_target_len: int = 200):
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Missing data file: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.tokenizer = tokenizer
        self.max_source_len = max_source_len
        self.max_target_len = max_target_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx: int):
        item = self.data[idx]
        s_enc = self.tokenizer(
            item["input_text"],
            max_length=self.max_source_len,
            padding=False,
            truncation=True,
            return_tensors=None
        )
        t_enc = self.tokenizer(
            item["target_text"],
            max_length=self.max_target_len,
            padding=False,
            truncation=True,
            return_tensors=None
        )
        return {
            "index": idx,
            "input_ids": s_enc["input_ids"],
            "attention_mask": s_enc["attention_mask"],
            "labels": t_enc["input_ids"]
        }


def collate_fn(batch: List[Dict[str, Any]], pad_token_id: int):
    indices = [x["index"] for x in batch]
    input_ids = [torch.tensor(x["input_ids"], dtype=torch.long) for x in batch]
    attention_mask = [torch.tensor(x["attention_mask"], dtype=torch.long) for x in batch]
    labels = [torch.tensor(x["labels"], dtype=torch.long) for x in batch]

    p_in = torch.nn.utils.rnn.pad_sequence(input_ids, batch_first=True, padding_value=pad_token_id)
    p_att = torch.nn.utils.rnn.pad_sequence(attention_mask, batch_first=True, padding_value=0)
    p_lab = torch.nn.utils.rnn.pad_sequence(labels, batch_first=True, padding_value=-100)

    return {
        "indices": indices,
        "input_ids": p_in,
        "attention_mask": p_att,
        "labels": p_lab
    }


def evaluate_val_f1_and_loss(
    model,
    val_loader,
    tokenizer,
    raw_val_samples: List[Dict[str, Any]],
    device: torch.device,
    max_target_len: int = 200,
    use_amp: bool = True
) -> Dict[str, float]:
    """Evaluates validation loss with teacher forcing AND validation triplet F1 via greedy decode."""
    model.eval()
    total_loss = 0.0
    total_steps = 0

    # 1. Validation Loss
    with torch.no_grad():
        for batch in val_loader:
            in_ids = batch["input_ids"].to(device, non_blocking=True)
            att_m = batch["attention_mask"].to(device, non_blocking=True)
            labs = batch["labels"].to(device, non_blocking=True)

            with torch.amp.autocast('cuda', enabled=use_amp):
                loss = model(input_ids=in_ids, attention_mask=att_m, labels=labs, label_smoothing=0.1).loss
            total_loss += loss.item()
            total_steps += 1

    avg_loss = total_loss / max(1, total_steps)

    # 2. Greedy Generation for Validation Triplet F1 (beam=1)
    n_gold, n_pred, n_correct = 0, 0, 0
    with torch.no_grad():
        for batch in val_loader:
            in_ids = batch["input_ids"].to(device, non_blocking=True)
            att_m = batch["attention_mask"].to(device, non_blocking=True)
            indices = batch["indices"]

            with torch.amp.autocast('cuda', enabled=use_amp):
                gen_ids = model.generate(
                    input_ids=in_ids,
                    attention_mask=att_m,
                    max_length=max_target_len,
                    num_beams=1,
                    no_repeat_ngram_size=3
                )

            decoded_texts = tokenizer.batch_decode(gen_ids, skip_special_tokens=True)

            for i, val_idx in enumerate(indices):
                gold_raw = raw_val_samples[val_idx].get("raw_triplets", [])
                gold_set = set(
                    (t["aspect"].strip().lower(), t["opinion"].strip().lower(), t["polarity"].strip().upper())
                    for t in gold_raw
                )
                pred_triplets = parse_triplets_from_string(decoded_texts[i])
                pred_set = set(
                    (t["aspect"].strip().lower(), t["opinion"].strip().lower(), t["polarity"].strip().upper())
                    for t in pred_triplets
                )

                n_gold += len(gold_set)
                n_pred += len(pred_set)
                n_correct += len(gold_set.intersection(pred_set))

    p = (n_correct / n_pred * 100) if n_pred > 0 else 0.0
    r = (n_correct / n_gold * 100) if n_gold > 0 else 0.0
    f1 = (2 * p * r / (p + r)) if (p + r) > 0 else 0.0

    return {
        "val_loss": round(avg_loss, 4),
        "val_p": round(p, 2),
        "val_r": round(r, 2),
        "val_f1": round(f1, 2),
        "n_gold": n_gold,
        "n_pred": n_pred,
        "n_correct": n_correct
    }


def audit_truncation(tokenizer, train_file: str, val_file: str, test_file: str, max_source_len: int, max_target_len: int) -> Dict[str, Any]:
    """Audits sequence lengths against thresholds to ensure supervision integrity."""
    audit_results = {}
    splits = [("train", train_file), ("val", val_file), ("test", test_file)]

    print("\n" + "-" * 75)
    print("🔍 AUDIT ĐỘ DÀI TOKEN & TỶ LỆ TRUNCATION (BẢO VỆ TÍNH TOÀN VẸN DỮ LIỆU)")
    print("-" * 75)

    for name, path in splits:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        s_lens = [len(tokenizer(x["input_text"]).input_ids) for x in data]
        t_lens = [len(tokenizer(x["target_text"]).input_ids) for x in data]

        s_trunc = sum(1 for l in s_lens if l > max_source_len)
        t_trunc = sum(1 for l in t_lens if l > max_target_len)

        s_pct = round(s_trunc / len(data) * 100, 2)
        t_pct = round(t_trunc / len(data) * 100, 2)

        audit_results[name] = {
            "total_samples": len(data),
            "max_source_len_setting": max_source_len,
            "max_target_len_setting": max_target_len,
            "source_max_observed": max(s_lens),
            "target_max_observed": max(t_lens),
            "source_truncated_count": s_trunc,
            "source_truncated_pct": s_pct,
            "target_truncated_count": t_trunc,
            "target_truncated_pct": t_pct
        }

        print(f"  • {name.upper():<5} (N={len(data):>4}) | "
              f"Source max={max(s_lens):>3}, >{max_source_len}: {s_trunc:>2} ({s_pct:>4.2f}%) | "
              f"Target max={max(t_lens):>3}, >{max_target_len}: {t_trunc:>2} ({t_pct:>4.2f}%)")

    print("-" * 75)
    sys.stdout.flush()
    return audit_results


def run_training_cycle(
    model_name: str,
    train_file: str,
    val_file: str,
    tokenizer,
    device: torch.device,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    weight_decay: float,
    max_source_len: int = 256,
    max_target_len: int = 200,
    save_output_dir: str = None,
    meta_extra: Dict[str, Any] = None,
    trial_prefix: str = ""
) -> Dict[str, Any]:
    seed_everything(RANDOM_SEED)

    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 1
    train_ds = ASTEDataset(train_file, tokenizer, max_source_len, max_target_len)
    val_ds = ASTEDataset(val_file, tokenizer, max_source_len, max_target_len)

    with open(val_file, "r", encoding="utf-8") as f:
        raw_val_samples = json.load(f)

    # Seeded DataLoaders
    g = torch.Generator()
    g.manual_seed(RANDOM_SEED)

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=2,
        pin_memory=True,
        generator=g,
        worker_init_fn=seed_worker,
        collate_fn=lambda b: collate_fn(b, pad_id)
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=2,
        pin_memory=True,
        collate_fn=lambda b: collate_fn(b, pad_id)
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    total_steps = len(train_loader) * epochs
    warmup_steps = int(0.10 * total_steps)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps)
    scaler = torch.amp.GradScaler('cuda', enabled=device.type == "cuda")

    best_val_f1 = -1.0
    best_val_loss = float("inf")
    best_epoch = 0
    history = []

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        model.train()
        train_loss = 0.0
        step_c = 0

        for batch in train_loader:
            in_ids = batch["input_ids"].to(device, non_blocking=True)
            att_m = batch["attention_mask"].to(device, non_blocking=True)
            labs = batch["labels"].to(device, non_blocking=True)

            optimizer.zero_grad()
            with torch.amp.autocast('cuda', enabled=device.type == "cuda"):
                loss = model(input_ids=in_ids, attention_mask=att_m, labels=labs, label_smoothing=0.1).loss

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            scale_before = scaler.get_scale()
            scaler.step(optimizer)
            scaler.update()
            scale_after = scaler.get_scale()

            if scale_before <= scale_after:
                scheduler.step()

            train_loss += loss.item()
            step_c += 1

        avg_train_loss = train_loss / max(1, step_c)

        # Validation evaluation: Loss + Strict Triplet F1
        val_metrics = evaluate_val_f1_and_loss(
            model=model,
            val_loader=val_loader,
            tokenizer=tokenizer,
            raw_val_samples=raw_val_samples,
            device=device,
            max_target_len=max_target_len,
            use_amp=device.type == "cuda"
        )
        dur = time.time() - t0

        val_loss = val_metrics["val_loss"]
        val_f1 = val_metrics["val_f1"]
        val_p = val_metrics["val_p"]
        val_r = val_metrics["val_r"]

        # Selection Criterion: Validation Triplet F1 (tie-break on val loss)
        is_best = (val_f1 > best_val_f1) or (val_f1 == best_val_f1 and val_loss < best_val_loss)
        star = "⭐ [BEST F1]" if is_best else ""

        print(f"  {trial_prefix}Epoch {epoch:02d}/{epochs:02d} [{dur:.1f}s] - "
              f"Train Loss: {avg_train_loss:.4f} | Val Loss: {val_loss:.4f} | "
              f"Val Triplet F1: {val_f1:.2f}% (P: {val_p:.2f}%, R: {val_r:.2f}%) | "
              f"LR: {scheduler.get_last_lr()[0]:.2e} {star}")
        sys.stdout.flush()

        history.append({
            "epoch": epoch,
            "train_loss": round(avg_train_loss, 4),
            "val_loss": val_loss,
            "val_triplet_f1": val_f1,
            "val_triplet_p": val_p,
            "val_triplet_r": val_r,
            "lr": scheduler.get_last_lr()[0],
            "duration_sec": round(dur, 1)
        })

        if is_best:
            best_val_f1 = val_f1
            best_val_loss = val_loss
            best_epoch = epoch
            if save_output_dir:
                os.makedirs(save_output_dir, exist_ok=True)
                model.save_pretrained(save_output_dir)
                tokenizer.save_pretrained(save_output_dir)

    if save_output_dir:
        meta = {
            "model_name": model_name,
            "random_seed": RANDOM_SEED,
            "selection_criterion": "validation_triplet_f1_strict",
            "best_epoch": best_epoch,
            "best_val_triplet_f1": best_val_f1,
            "best_val_loss": best_val_loss,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "weight_decay": weight_decay,
            "label_smoothing": 0.1,
            "max_source_len": max_source_len,
            "max_target_len": max_target_len,
            "total_epochs": epochs,
            "git_commit_sha": get_git_commit_sha(),
            "history": history
        }
        if meta_extra:
            meta.update(meta_extra)

        with open(os.path.join(save_output_dir, "training_meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

    del model, optimizer, scheduler, train_loader, val_loader
    torch.cuda.empty_cache()
    gc.collect()

    return {
        "best_epoch": best_epoch,
        "best_val_f1": best_val_f1,
        "best_val_loss": best_val_loss,
        "history": history
    }


def main():
    parser = argparse.ArgumentParser(description="Optuna Tuning and 30-Epoch Training for BARTpho Syllable Base")
    parser.add_argument("--model_name", type=str, default="vinai/bartpho-syllable-base")
    parser.add_argument("--data_dir", type=str, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output_dir", type=str, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report_dir", type=str, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--trials", type=int, default=3, help="Optuna trials count")
    parser.add_argument("--trial_epochs", type=int, default=5, help="Epochs per Optuna trial")
    parser.add_argument("--train_epochs", type=int, default=30, help="Full fine-tuning epochs")
    parser.add_argument("--max_source_len", type=int, default=256, help="Max source length")
    parser.add_argument("--max_target_len", type=int, default=200, help="Max target length")
    parser.add_argument("--gpu", type=int, default=0, choices=[0, 2, 3], help="GPU index (0, 2, or 3)")

    args = parser.parse_args()

    # Hardware configuration
    gpu_uuid = GPU_UUID_MAP[args.gpu]
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu_uuid
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_file = os.path.join(args.data_dir, "train.json")
    val_file = os.path.join(args.data_dir, "val.json")
    test_file = os.path.join(args.data_dir, "test.json")

    # Data artifact hashing
    train_md5 = get_file_md5(train_file)
    val_md5 = get_file_md5(val_file)
    test_md5 = get_file_md5(test_file)
    git_sha = get_git_commit_sha()

    print("=" * 80)
    print("🚀 RADI-NET ASTE: ACADEMIC BENCHMARK PIPELINE - BARTPHO-SYLLABLE-BASE")
    print(f"  • Model Backbone      : {args.model_name}")
    print(f"  • Selection Criterion : Validation Triplet F1 (Strict Match, Greedy Decode)")
    print(f"  • Random Seed         : {RANDOM_SEED} (Deterministic CuDNN Enabled)")
    print(f"  • GPU Target          : GPU {args.gpu} (UUID: {gpu_uuid})")
    print(f"  • Device Active       : {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print(f"  • Git Commit SHA      : {git_sha}")
    print(f"  • Data Split MD5s     : train={train_md5[:8]}, val={val_md5[:8]}, test={test_md5[:8]}")
    print(f"  • Optuna Config       : {args.trials} Trials × {args.trial_epochs} Epochs (Objective: Maximize Val Triplet F1)")
    print(f"  • Final Training      : {args.train_epochs} Epochs")
    print(f"  • Output Checkpoint   : {args.output_dir}")
    print("=" * 80)
    sys.stdout.flush()

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    # Truncation Audit
    truncation_audit = audit_truncation(
        tokenizer=tokenizer,
        train_file=train_file,
        val_file=val_file,
        test_file=test_file,
        max_source_len=args.max_source_len,
        max_target_len=args.max_target_len
    )

    meta_extra = {
        "git_commit_sha": git_sha,
        "dataset_md5": {
            "train": train_md5,
            "val": val_md5,
            "test": test_md5
        },
        "truncation_audit": truncation_audit,
        "hardware": {
            "gpu_index": args.gpu,
            "gpu_uuid": gpu_uuid,
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
            "torch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available()
        }
    }

    os.makedirs(os.path.dirname(args.output_dir), exist_ok=True)
    os.makedirs(args.report_dir, exist_ok=True)

    # 1. Stage 1: Optuna Hyperparameter Optimization
    print("\n" + "=" * 80)
    print("STAGE 1: KHỞI ĐỘNG OPTUNA TỐI ƯU HÓA SIÊU THAM SỐ (MỤC TIÊU: MAXIMIZE VALIDATION TRIPLET F1)")
    print("=" * 80)
    sys.stdout.flush()

    def objective(trial: optuna.Trial) -> float:
        lr = trial.suggest_float("learning_rate", 2.0e-5, 6.0e-5, log=True)
        bs = trial.suggest_categorical("batch_size", [16, 24])
        wd = trial.suggest_float("weight_decay", 1e-4, 1e-2, log=True)

        print(f"\n[Optuna Trial {trial.number + 1}/{args.trials}] Cấu hình: lr={lr:.2e}, bs={bs}, wd={wd:.2e}")
        sys.stdout.flush()

        res = run_training_cycle(
            model_name=args.model_name,
            train_file=train_file,
            val_file=val_file,
            tokenizer=tokenizer,
            device=device,
            epochs=args.trial_epochs,
            batch_size=bs,
            learning_rate=lr,
            weight_decay=wd,
            max_source_len=args.max_source_len,
            max_target_len=args.max_target_len,
            trial_prefix=f"[Trial {trial.number + 1}] "
        )
        val_f1 = res["best_val_f1"]
        print(f"==> Kết thúc Trial {trial.number + 1}: Best Val Triplet F1 = {val_f1:.2f}% (Loss: {res['best_val_loss']:.4f}, Epoch {res['best_epoch']})")
        sys.stdout.flush()
        return val_f1

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=RANDOM_SEED))
    study.optimize(objective, n_trials=args.trials)

    best_params = study.best_params
    best_f1 = study.best_value

    study_summary = {
        "best_trial_number": study.best_trial.number + 1,
        "best_val_triplet_f1": round(best_f1, 2),
        "best_params": best_params,
        "selection_criterion": "validation_triplet_f1_strict",
        "git_commit_sha": git_sha,
        "dataset_md5": {"train": train_md5, "val": val_md5, "test": test_md5},
        "all_trials": [
            {
                "trial": t.number + 1,
                "val_triplet_f1": round(t.value, 2) if t.value is not None else None,
                "params": t.params
            }
            for t in study.trials
        ]
    }
    study_file = os.path.join(args.report_dir, "optuna_study.json")
    with open(study_file, "w", encoding="utf-8") as f:
        json.dump(study_summary, f, indent=2)

    with open(os.path.join(os.path.dirname(args.output_dir), "optuna_study.json"), "w", encoding="utf-8") as f:
        json.dump(study_summary, f, indent=2)

    print("\n" + "=" * 80)
    print("🎉 KẾT QUẢ OPTUNA CHO BARTPHO SYLLABLE BASE:")
    print(f"  • Best Trial         : #{study.best_trial.number + 1}")
    print(f"  • Best Val Triplet F1: {best_f1:.2f}%")
    print(f"  • Best Params        : {best_params}")
    print("=" * 80)
    sys.stdout.flush()

    # 2. Stage 2: Full Fine-Tuning 30 Epochs
    print("\n" + "=" * 80)
    print(f"STAGE 2: HUẤN LUYỆN TOÀN DIỆN {args.train_epochs} EPOCHS (LƯU CHECKPOINT THEO VALIDATION TRIPLET F1 TỐI ƯU)")
    print(f"  • Learning Rate : {best_params['learning_rate']}")
    print(f"  • Batch Size    : {best_params['batch_size']}")
    print(f"  • Weight Decay  : {best_params['weight_decay']}")
    print("=" * 80)
    sys.stdout.flush()

    final_res = run_training_cycle(
        model_name=args.model_name,
        train_file=train_file,
        val_file=val_file,
        tokenizer=tokenizer,
        device=device,
        epochs=args.train_epochs,
        batch_size=best_params["batch_size"],
        learning_rate=best_params["learning_rate"],
        weight_decay=best_params["weight_decay"],
        max_source_len=args.max_source_len,
        max_target_len=args.max_target_len,
        save_output_dir=args.output_dir,
        meta_extra=meta_extra,
        trial_prefix="[Full Train] "
    )

    print("\n" + "=" * 80)
    print("✅ HUẤN LUYỆN 30 EPOCHS HOÀN TẤT THÀNH CÔNG!")
    print(f"  • Checkpoint Path      : {args.output_dir}")
    print(f"  • Best Epoch           : {final_res['best_epoch']}")
    print(f"  • Best Val Triplet F1  : {final_res['best_val_f1']:.2f}%")
    print(f"  • Associated Val Loss  : {final_res['best_val_loss']:.4f}")
    print("=" * 80)
    sys.stdout.flush()

    # 3. Stage 3: Independent Test Split Evaluation
    print("\n" + "=" * 80)
    print("STAGE 3: ĐÁNH GIÁ ĐỘC LẬP TRÊN TẬP TEST (462 MẪU)")
    print("=" * 80)
    sys.stdout.flush()

    eval_script = os.path.join(PROJECT_ROOT, "AI", "bartpho", "syllable_base", "test", "evaluate_aste.py")
    report_file = os.path.join(args.report_dir, "bartpho_syllable_test_report.json")
    cmd_eval = [
        PYTHON_EXE, "-u", eval_script,
        "--checkpoint_dir", args.output_dir,
        "--output_report", report_file
    ]
    subprocess.run(cmd_eval, check=True, env=os.environ)

    # 4. Stage 4: Inference Demo
    infer_script = os.path.join(PROJECT_ROOT, "AI", "bartpho", "syllable_base", "test", "inference.py")
    subprocess.run([PYTHON_EXE, "-u", infer_script], check=True, env=os.environ)

    # 5. Stage 5: Update Master Comparison Table in AI/results
    print("\n" + "=" * 80)
    print("📈 CẬP NHẬT BẢNG SO SÁNH TỔNG HỢP MASTER BENCHMARK TABLE TRONG AI/results/")
    print("=" * 80)
    update_script = os.path.join(PROJECT_ROOT, "scripts", "benchmark_heuristic_baseline.py")
    subprocess.run([PYTHON_EXE, "-u", update_script], check=True, env=os.environ)


if __name__ == "__main__":
    main()
