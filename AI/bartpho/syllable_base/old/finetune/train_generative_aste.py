"""
AI/bartpho/syllable_base/finetune/train_generative_aste.py
--------------------------------------------------------------------------------
Standalone Fine-tuning Script for Generative ASTE using BARTpho-syllable-base
(vinai/bartpho-syllable-base) on HCMC Flood Multimodal Dataset V3 splits.

Key features:
- Backbone: vinai/bartpho-syllable-base (Syllable-level Seq2Seq Transformer)
- Full Random Seeding (Seed 42, deterministic CuDNN, seeded Generator)
- Truncation Audit & Safeguards (max_source_len=256, max_target_len=200; target truncation ~0%)
- Checkpoint Selection: Validation Triplet F1 (Strict Match via per-epoch greedy decode)
- Artifact Pinning in Metadata: Git commit SHA, dataset MD5 hashes, selection criterion
- Label Smoothing: 0.1 for enhanced generalization
- Dynamic padding & GPU batching with FP16 Automatic Mixed Precision
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
from typing import List, Dict, Any, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    get_linear_schedule_with_warmup
)
from tqdm import tqdm

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYLLABLE_BASE_DIR = os.path.dirname(SCRIPT_DIR)
BARTPHO_DIR = os.path.dirname(SYLLABLE_BASE_DIR)
AI_DIR = os.path.dirname(BARTPHO_DIR)
PROJECT_ROOT = os.path.dirname(AI_DIR)

DEFAULT_DATA_DIR = os.path.join(BARTPHO_DIR, "data")
DEFAULT_OUTPUT_DIR = os.path.join(SYLLABLE_BASE_DIR, "finetune", "checkpoints", "best_aste_model")

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
    model.eval()
    total_loss = 0.0
    total_steps = 0

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
        "val_f1": round(f1, 2)
    }


def audit_truncation(tokenizer, train_file: str, val_file: str, test_file: str, max_source_len: int, max_target_len: int) -> Dict[str, Any]:
    audit_results = {}
    splits = [("train", train_file), ("val", val_file), ("test", test_file)]

    print("\n" + "-" * 75)
    print("🔍 AUDIT ĐỘ DÀI TOKEN & TỶ LỆ TRUNCATION")
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


def train(args):
    seed_everything(RANDOM_SEED)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("=" * 80)
    print("🚀 HUẤN LUYỆN BARTPHO-SYLLABLE-BASE GENERATIVE ASTE")
    print(f"  • Thiết bị        : {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print(f"  • Random Seed     : {RANDOM_SEED} (CuDNN Deterministic)")
    print(f"  • Tiêu chí lưu    : Validation Triplet F1 (Strict Match, Greedy Decode)")
    print(f"  • Batch Size      : {args.batch_size}")
    print(f"  • Learning Rate   : {args.learning_rate}")
    print(f"  • Weight Decay    : {args.weight_decay}")
    print(f"  • Label Smoothing : {args.label_smoothing}")
    print(f"  • Số Epochs       : {args.epochs}")
    print("=" * 80)

    train_file = os.path.join(args.data_dir, "train.json")
    val_file = os.path.join(args.data_dir, "val.json")
    test_file = os.path.join(args.data_dir, "test.json")

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 1

    # Truncation audit
    truncation_audit = audit_truncation(tokenizer, train_file, val_file, test_file, args.max_source_len, args.max_target_len)

    train_ds = ASTEDataset(train_file, tokenizer, args.max_source_len, args.max_target_len)
    val_ds = ASTEDataset(val_file, tokenizer, args.max_source_len, args.max_target_len)

    with open(val_file, "r", encoding="utf-8") as f:
        raw_val_samples = json.load(f)

    g = torch.Generator()
    g.manual_seed(RANDOM_SEED)

    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=2,
        pin_memory=True,
        generator=g,
        worker_init_fn=seed_worker,
        collate_fn=lambda b: collate_fn(b, pad_id)
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=2,
        pin_memory=True,
        collate_fn=lambda b: collate_fn(b, pad_id)
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    total_steps = len(train_loader) * args.epochs
    warmup_steps = int(args.warmup_ratio * total_steps)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps)
    scaler = torch.amp.GradScaler('cuda', enabled=device.type == "cuda")

    best_val_f1 = -1.0
    best_val_loss = float("inf")
    best_epoch = 0
    history = []

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        model.train()
        train_loss = 0.0
        step_c = 0

        for batch in tqdm(train_loader, desc=f"Epoch {epoch}/{args.epochs}"):
            in_ids = batch["input_ids"].to(device, non_blocking=True)
            att_m = batch["attention_mask"].to(device, non_blocking=True)
            labs = batch["labels"].to(device, non_blocking=True)

            optimizer.zero_grad()
            with torch.amp.autocast('cuda', enabled=device.type == "cuda"):
                loss = model(input_ids=in_ids, attention_mask=att_m, labels=labs, label_smoothing=args.label_smoothing).loss

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

        val_metrics = evaluate_val_f1_and_loss(
            model=model,
            val_loader=val_loader,
            tokenizer=tokenizer,
            raw_val_samples=raw_val_samples,
            device=device,
            max_target_len=args.max_target_len,
            use_amp=device.type == "cuda"
        )
        dur = time.time() - t0

        val_loss = val_metrics["val_loss"]
        val_f1 = val_metrics["val_f1"]
        val_p = val_metrics["val_p"]
        val_r = val_metrics["val_r"]

        is_best = (val_f1 > best_val_f1) or (val_f1 == best_val_f1 and val_loss < best_val_loss)
        star = "⭐ [BEST F1]" if is_best else ""

        print(f"Epoch {epoch:02d}/{args.epochs:02d} [{dur:.1f}s] - "
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
            os.makedirs(args.output_dir, exist_ok=True)
            model.save_pretrained(args.output_dir)
            tokenizer.save_pretrained(args.output_dir)

    # Pin artifacts to metadata
    git_sha = get_git_commit_sha()
    meta = {
        "model_name": args.model_name,
        "random_seed": RANDOM_SEED,
        "selection_criterion": "validation_triplet_f1_strict",
        "best_epoch": best_epoch,
        "best_val_triplet_f1": best_val_f1,
        "best_val_loss": best_val_loss,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "label_smoothing": args.label_smoothing,
        "max_source_len": args.max_source_len,
        "max_target_len": args.max_target_len,
        "total_epochs": args.epochs,
        "git_commit_sha": git_sha,
        "dataset_md5": {
            "train": get_file_md5(train_file),
            "val": get_file_md5(val_file),
            "test": get_file_md5(test_file)
        },
        "truncation_audit": truncation_audit,
        "hardware": {
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
            "torch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available()
        },
        "history": history
    }

    with open(os.path.join(args.output_dir, "training_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("✅ HOÀN TẤT HUẤN LUYỆN!")
    print(f"  • Best Checkpoint : {args.output_dir}")
    print(f"  • Best Epoch      : {best_epoch}")
    print(f"  • Best Val F1     : {best_val_f1:.2f}% (Val Loss: {best_val_loss:.4f})")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="vinai/bartpho-syllable-base")
    parser.add_argument("--data_dir", type=str, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output_dir", type=str, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--learning_rate", type=float, default=4e-5)
    parser.add_argument("--weight_decay", type=float, default=0.01)
    parser.add_argument("--label_smoothing", type=float, default=0.1)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--warmup_ratio", type=float, default=0.1)
    parser.add_argument("--max_source_len", type=int, default=256)
    parser.add_argument("--max_target_len", type=int, default=200)

    args = parser.parse_args()
    train(args)
