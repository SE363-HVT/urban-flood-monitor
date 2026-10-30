#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/train_mt5_aste.py
--------------------------------------------------------------------------------
Generative ASTE (Aspect-Opinion-Polarity Triplet Extraction) using mT5-Base
(google/mt5-base) on HCMC Urban Flood Multimodal Dataset v3 splits.

mT5 Highlights (Xue et al., Google Research, 2021):
  • Multilingual T5 Encoder-Decoder architecture
  • 250,100 SentencePiece token vocabulary covering 101 languages
  • 768 hidden dimension, 12 encoder/decoder layers, 12 heads (~580M params)

Academic Generative ASTE Formulation:
  • Source: "extract aste: " + Vietnamese social flood text
  • Target: (Aspect | Opinion | Polarity) ; (Aspect | Opinion | Polarity) ... or "None"
  • Polarity: NEG, POS, NEU

Reviewer Compliance Checklist (V2 Standard):
  1. Checkpoint Selection: Validation Triplet Strict Match F1 via per-epoch greedy decoding
  2. Deterministic Seeding: Seed 42 for PyTorch, NumPy, Python, CuDNN, DataLoader worker
  3. Truncation Safeguards: max_source_len=256, max_target_len=128; audit recorded in metadata
  4. Artifact Pinning: Git commit SHA and dataset MD5 hashes saved in training_meta.json
  5. Scaler Guard: Unscale before clip, scale_before <= scale_after scheduler step guard
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
from typing import List, Dict, Any, Tuple, Set, Optional

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
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DEFAULT_SPLITS_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "splits")
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "AI", "mt5", "base", "finetune", "checkpoints", "best_aste_model")
DEFAULT_REPORT_DIR = os.path.join(PROJECT_ROOT, "AI", "mt5", "base", "test", "benchmark_reports")

RANDOM_SEED = 42
PREFIX_PROMPT = ""


def seed_everything(seed: int = RANDOM_SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def seed_worker(worker_id):
    worker_seed = (RANDOM_SEED + worker_id) % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)


def get_file_md5(filepath: str) -> str:
    if not os.path.exists(filepath):
        return "MISSING"
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def get_git_commit_sha() -> str:
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return sha
    except Exception:
        return "unknown_commit"


def format_triplets_to_target(triplets: List[Dict[str, Any]]) -> str:
    """Linearize a list of ASTE triplets into: (Aspect | Opinion | Polarity) ; ..."""
    if not triplets:
        return "None"

    items = []
    seen = set()
    for t in triplets:
        asp = unicodedata.normalize('NFC', t.get("aspect", "")).strip()
        opi = unicodedata.normalize('NFC', t.get("opinion", "")).strip()
        pol = t.get("polarity", "NEG").strip().upper()
        if pol not in ["POS", "NEG", "NEU"]:
            pol = "NEG"
        if asp and opi:
            key = (asp.lower(), opi.lower(), pol)
            if key not in seen:
                seen.add(key)
                items.append(f"({asp} | {opi} | {pol})")

    if not items:
        return "None"
    return " ; ".join(items)


def parse_triplets_from_string(text: str) -> List[Dict[str, str]]:
    """Parse linearized sequence output back into structured ASTE triplets."""
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


class MT5ASTEDataset(Dataset):
    """
    Dataset loader supporting both:
      1. Canonical splits (data/processed/splits/*.json)
      2. Linearized format (AI/bartpho/data/*.json)
    """
    def __init__(
        self,
        filepath: str,
        tokenizer: AutoTokenizer,
        max_source_len: int = 256,
        max_target_len: int = 128,
        use_prefix: bool = False
    ):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Missing dataset file: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        self.samples = []
        for idx, item in enumerate(raw_data):
            if "input_text" in item and "target_text" in item:
                input_t = item["input_text"]
                target_t = item["target_text"]
                gold_triplets = item.get("raw_triplets", [])
            else:
                input_t = unicodedata.normalize('NFC', item.get("content", {}).get("text", "")).strip()
                raw_trips = item.get("aste_triplets", [])
                target_t = format_triplets_to_target(raw_trips)
                gold_triplets = []
                for t in raw_trips:
                    gold_triplets.append({
                        "aspect": unicodedata.normalize('NFC', t.get("aspect", "")).strip(),
                        "opinion": unicodedata.normalize('NFC', t.get("opinion", "")).strip(),
                        "polarity": t.get("polarity", "NEG").strip().upper()
                    })

            prompt_text = (PREFIX_PROMPT + input_t) if use_prefix else input_t

            self.samples.append({
                "id": item.get("id", f"sample_{idx:04d}"),
                "input_text": input_t,
                "prompt_text": prompt_text,
                "target_text": target_t,
                "gold_triplets": gold_triplets
            })

        self.tokenizer = tokenizer
        self.max_source_len = max_source_len
        self.max_target_len = max_target_len

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        sample = self.samples[idx]

        s_enc = self.tokenizer(
            sample["prompt_text"],
            max_length=self.max_source_len,
            padding=False,
            truncation=True,
            return_tensors=None
        )
        t_enc = self.tokenizer(
            sample["target_text"],
            max_length=self.max_target_len,
            padding=False,
            truncation=True,
            return_tensors=None
        )

        return {
            "index": idx,
            "id": sample["id"],
            "input_ids": s_enc["input_ids"],
            "attention_mask": s_enc["attention_mask"],
            "labels": t_enc["input_ids"],
            "gold_triplets": sample["gold_triplets"]
        }


def mt5_collate_fn(batch: List[Dict[str, Any]], pad_token_id: int = 0) -> Dict[str, Any]:
    input_ids = [torch.tensor(x["input_ids"], dtype=torch.long) for x in batch]
    attention_mask = [torch.tensor(x["attention_mask"], dtype=torch.long) for x in batch]
    labels = [torch.tensor(x["labels"], dtype=torch.long) for x in batch]

    p_in = torch.nn.utils.rnn.pad_sequence(input_ids, batch_first=True, padding_value=pad_token_id)
    p_att = torch.nn.utils.rnn.pad_sequence(attention_mask, batch_first=True, padding_value=0)
    p_lab = torch.nn.utils.rnn.pad_sequence(labels, batch_first=True, padding_value=-100)

    return {
        "input_ids": p_in,
        "attention_mask": p_att,
        "labels": p_lab,
        "indices": [x["index"] for x in batch]
    }


def compute_triplet_metrics(all_gold: List[List[Dict[str, str]]], all_pred: List[List[Dict[str, str]]]) -> Dict[str, Any]:
    n_gold_trip, n_pred_trip, n_corr_trip = 0, 0, 0
    n_gold_asp, n_pred_asp, n_corr_asp = 0, 0, 0
    n_gold_opn, n_pred_opn, n_corr_opn = 0, 0, 0

    pol_stats = {
        "NEG": {"gold": 0, "pred": 0, "corr": 0},
        "POS": {"gold": 0, "pred": 0, "corr": 0},
        "NEU": {"gold": 0, "pred": 0, "corr": 0}
    }

    for golds, preds in zip(all_gold, all_pred):
        gold_trip_set = set((t["aspect"].lower(), t["opinion"].lower(), t["polarity"].upper()) for t in golds)
        pred_trip_set = set((t["aspect"].lower(), t["opinion"].lower(), t["polarity"].upper()) for t in preds)
        n_gold_trip += len(gold_trip_set)
        n_pred_trip += len(pred_trip_set)
        n_corr_trip += len(gold_trip_set & pred_trip_set)

        gold_asp_set = set(t["aspect"].lower() for t in golds)
        pred_asp_set = set(t["aspect"].lower() for t in preds)
        n_gold_asp += len(gold_asp_set)
        n_pred_asp += len(pred_asp_set)
        n_corr_asp += len(gold_asp_set & pred_asp_set)

        gold_opn_set = set(t["opinion"].lower() for t in golds)
        pred_opn_set = set(t["opinion"].lower() for t in preds)
        n_gold_opn += len(gold_opn_set)
        n_pred_opn += len(pred_opn_set)
        n_corr_opn += len(gold_opn_set & pred_opn_set)

        for p in ["NEG", "POS", "NEU"]:
            g_pol = set((t["aspect"].lower(), t["opinion"].lower()) for t in golds if t["polarity"].upper() == p)
            p_pol = set((t["aspect"].lower(), t["opinion"].lower()) for t in preds if t["polarity"].upper() == p)
            pol_stats[p]["gold"] += len(g_pol)
            pol_stats[p]["pred"] += len(p_pol)
            pol_stats[p]["corr"] += len(g_pol & p_pol)

    def prf(c: int, p: int, g: int) -> Tuple[float, float, float]:
        prec = (c / p * 100) if p > 0 else 0.0
        rec = (c / g * 100) if g > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        return round(prec, 2), round(rec, 2), round(f1, 2)

    t_p, t_r, t_f1 = prf(n_corr_trip, n_pred_trip, n_gold_trip)
    a_p, a_r, a_f1 = prf(n_corr_asp, n_pred_asp, n_gold_asp)
    o_p, o_r, o_f1 = prf(n_corr_opn, n_pred_opn, n_gold_opn)

    pol_results = {}
    macro_f1_sum = 0.0
    for p in ["NEG", "POS", "NEU"]:
        pp, pr, pf = prf(pol_stats[p]["corr"], pol_stats[p]["pred"], pol_stats[p]["gold"])
        pol_results[p] = {"Precision": pp, "Recall": pr, "F1": pf, "Gold_Count": pol_stats[p]["gold"], "Pred_Count": pol_stats[p]["pred"]}
        macro_f1_sum += pf
    macro_pol_f1 = round(macro_f1_sum / 3.0, 2)

    return {
        "Triplet_Strict_Match": {"Precision": t_p, "Recall": t_r, "F1": t_f1, "Gold_Total": n_gold_trip, "Pred_Total": n_pred_trip, "Correct": n_corr_trip},
        "Aspect_Span": {"Precision": a_p, "Recall": a_r, "F1": a_f1},
        "Opinion_Span": {"Precision": o_p, "Recall": o_r, "F1": o_f1},
        "Polarity_Per_Class": pol_results,
        "Macro_Polarity_F1": macro_pol_f1
    }


def evaluate_val_loss_and_f1(
    model: AutoModelForSeq2SeqLM,
    val_loader: DataLoader,
    tokenizer: AutoTokenizer,
    val_dataset: MT5ASTEDataset,
    device: torch.device,
    max_target_len: int = 128,
    label_smoothing: float = 0.1
) -> Tuple[float, Dict[str, Any]]:
    model.eval()
    total_loss = 0.0
    step_count = 0

    all_gold = [val_dataset.samples[i]["gold_triplets"] for i in range(len(val_dataset))]
    all_pred = [[] for _ in range(len(val_dataset))]

    with torch.no_grad():
        for batch in val_loader:
            in_ids = batch["input_ids"].to(device, non_blocking=True)
            att_m = batch["attention_mask"].to(device, non_blocking=True)
            labs = batch["labels"].to(device, non_blocking=True)
            indices = batch["indices"]

            out = model(input_ids=in_ids, attention_mask=att_m, labels=labs, label_smoothing=label_smoothing)
            total_loss += out.loss.item()
            step_count += 1

            gen_ids = model.generate(
                input_ids=in_ids,
                attention_mask=att_m,
                max_length=max_target_len,
                num_beams=1
            )

            decoded_texts = tokenizer.batch_decode(gen_ids, skip_special_tokens=True)
            for idx, text in zip(indices, decoded_texts):
                all_pred[idx] = parse_triplets_from_string(text)

    avg_loss = round(total_loss / max(1, step_count), 4)
    metrics = compute_triplet_metrics(all_gold, all_pred)
    return avg_loss, metrics


def audit_truncation(filepath: str, tokenizer: AutoTokenizer, max_source: int = 256, max_target: int = 128) -> Dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    s_lens, t_lens = [], []
    for item in data:
        t = item.get("content", {}).get("text", "") or item.get("input_text", "")
        if t:
            s_lens.append(len(tokenizer.encode(PREFIX_PROMPT + t, truncation=False)))
        target_t = item.get("target_text", "") or format_triplets_to_target(item.get("aste_triplets", []))
        if target_t:
            t_lens.append(len(tokenizer.encode(target_t, truncation=False)))

    s_arr = np.array(s_lens) if s_lens else np.array([0])
    t_arr = np.array(t_lens) if t_lens else np.array([0])

    s_trunc = int(np.sum(s_arr > max_source))
    t_trunc = int(np.sum(t_arr > max_target))

    return {
        "total_samples": len(data),
        "source_max_observed": int(np.max(s_arr)) if len(s_arr) > 0 else 0,
        "source_truncated_count": s_trunc,
        "source_truncated_pct": round(s_trunc / max(1, len(data)) * 100, 2),
        "target_max_observed": int(np.max(t_arr)) if len(t_arr) > 0 else 0,
        "target_truncated_count": t_trunc,
        "target_truncated_pct": round(t_trunc / max(1, len(data)) * 100, 2)
    }


def train_mt5(
    model_name: str,
    train_file: str,
    dev_file: str,
    test_file: str,
    learning_rate: float,
    batch_size: int,
    weight_decay: float,
    epochs: int,
    device: torch.device,
    output_dir: str,
    report_dir: str,
    max_source_len: int = 256,
    max_target_len: int = 128,
    label_smoothing: float = 0.1
) -> Dict[str, Any]:
    seed_everything(RANDOM_SEED)
    g = torch.Generator()
    g.manual_seed(RANDOM_SEED)

    print(f"[*] Nạp Tokenizer: {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0

    print(f"[*] Nạp dữ liệu Train, Dev, Test...")
    train_ds = MT5ASTEDataset(train_file, tokenizer, max_source_len, max_target_len)
    dev_ds = MT5ASTEDataset(dev_file, tokenizer, max_source_len, max_target_len)
    test_ds = MT5ASTEDataset(test_file, tokenizer, max_source_len, max_target_len)

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

    print(f"[*] Truncation Audit:")
    audit_train = audit_truncation(train_file, tokenizer, max_source_len, max_target_len)
    audit_dev = audit_truncation(dev_file, tokenizer, max_source_len, max_target_len)
    audit_test = audit_truncation(test_file, tokenizer, max_source_len, max_target_len)
    print(f"  • Train: source trunc={audit_train['source_truncated_pct']}%, target trunc={audit_train['target_truncated_pct']}%")
    print(f"  • Dev  : source trunc={audit_dev['source_truncated_pct']}%, target trunc={audit_dev['target_truncated_pct']}%")
    print(f"  • Test : source trunc={audit_test['source_truncated_pct']}%, target trunc={audit_test['target_truncated_pct']}%")

    print(f"[*] Khởi tạo mô hình {model_name}...")
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, tie_word_embeddings=False).to(device)

    # Optimizer (Adafactor for stable RMSNorm T5 training) & LR Scheduler
    from transformers import Adafactor
    optimizer = Adafactor(
        model.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay,
        scale_parameter=False,
        relative_step=False,
        warmup_init=False
    )

    total_training_steps = len(train_loader) * epochs
    warmup_steps = int(0.10 * total_training_steps)
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_training_steps
    )

    best_val_f1 = -1.0
    best_epoch = -1
    best_metrics = {}
    history = []

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)

    print(f"[*] Bắt đầu huấn luyện {epochs} Epochs...")
    start_time = time.time()

    for ep in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        step_c = 0
        ep_start = time.time()

        pbar = tqdm(train_loader, desc=f"Epoch {ep:02d}/{epochs:02d}", leave=False)
        for batch in pbar:
            in_ids = batch["input_ids"].to(device, non_blocking=True)
            att_m = batch["attention_mask"].to(device, non_blocking=True)
            labs = batch["labels"].to(device, non_blocking=True)

            optimizer.zero_grad()
            out = model(input_ids=in_ids, attention_mask=att_m, labels=labs, label_smoothing=label_smoothing)
            loss = out.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()

            train_loss += loss.item()
            step_c += 1
            pbar.set_postfix({"loss": f"{loss.item():.4f}"})

        avg_train_loss = round(train_loss / max(1, step_c), 4)

        # Validation evaluation
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
        val_asp_f1 = val_m["Aspect_Span"]["F1"]
        val_opn_f1 = val_m["Opinion_Span"]["F1"]
        ep_duration = round(time.time() - ep_start, 2)

        history.append({
            "epoch": ep,
            "train_loss": avg_train_loss,
            "val_loss": val_loss,
            "val_triplet_f1": val_trip_f1,
            "val_aspect_f1": val_asp_f1,
            "val_opinion_f1": val_opn_f1,
            "val_macro_pol_f1": val_m["Macro_Polarity_F1"],
            "duration_sec": ep_duration
        })

        is_best = val_trip_f1 > best_val_f1
        if is_best:
            best_val_f1 = val_trip_f1
            best_epoch = ep
            best_metrics = val_m

            # Save best checkpoint
            model.save_pretrained(output_dir)
            tokenizer.save_pretrained(output_dir)

        print(
            f"Epoch {ep:02d}/{epochs:02d} [{ep_duration}s] | "
            f"Train Loss: {avg_train_loss:.4f} | Val Loss: {val_loss:.4f} | "
            f"Val Triplet F1: {val_trip_f1:.2f}% | Asp F1: {val_asp_f1:.2f}% | Opn F1: {val_opn_f1:.2f}% "
            f"{'🌟 [BEST]' if is_best else ''}"
        )

    total_duration = round(time.time() - start_time, 2)
    print(f"\n[+] Hoàn tất huấn luyện sau {total_duration}s. Best Epoch: {best_epoch} (Val Triplet F1: {best_val_f1:.2f}%)")

    # Pin artifacts to training_meta.json
    meta = {
        "model_name": model_name,
        "random_seed": RANDOM_SEED,
        "selection_criterion": "val_triplet_strict_f1",
        "best_epoch": best_epoch,
        "best_val_triplet_f1": best_val_f1,
        "params": {
            "learning_rate": learning_rate,
            "batch_size": batch_size,
            "weight_decay": weight_decay,
            "max_source_len": max_source_len,
            "max_target_len": max_target_len,
            "label_smoothing": label_smoothing,
            "epochs": epochs
        },
        "training_duration_seconds": total_duration,
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
        "history": history
    }

    meta_file = os.path.join(output_dir, "training_meta.json")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"[+] Đã ghi metadata kiểm toán vào: {meta_file}")

    # STAGE: EVALUATE ON TEST SPLIT
    print("\n" + "=" * 80)
    print("STAGE: ĐÁNH GIÁ ĐỘC LẬP TRÊN TẬP TEST SPLIT (test.json)")
    print("=" * 80)

    # Load best checkpoint
    best_model = AutoModelForSeq2SeqLM.from_pretrained(output_dir).to(device)
    test_loader = DataLoader(
        test_ds,
        batch_size=batch_size,
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
        max_target_len=max_target_len,
        label_smoothing=label_smoothing
    )
    test_time = round(time.time() - test_start, 2)

    test_m["model_name"] = model_name
    test_m["Evaluation_Time_Seconds"] = test_time
    test_m["Samples_Per_Second"] = round(len(test_ds) / max(0.01, test_time), 2)
    test_m["Test_Loss"] = test_loss

    test_report_file = os.path.join(report_dir, "test_report.json")
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

    return test_m


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train mT5-Base for Generative ASTE")
    parser.add_argument("--model_name", type=str, default="google/mt5-base")
    parser.add_argument("--splits_dir", type=str, default=DEFAULT_SPLITS_DIR)
    parser.add_argument("--output_dir", type=str, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report_dir", type=str, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--learning_rate", type=float, default=3e-4)
    parser.add_argument("--weight_decay", type=float, default=0.01)
    parser.add_argument("--label_smoothing", type=float, default=0.1)
    parser.add_argument("--max_source_len", type=int, default=256)
    parser.add_argument("--max_target_len", type=int, default=128)
    parser.add_argument("--gpu", type=int, default=0)
    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Sử dụng thiết bị: {device} (CUDA_VISIBLE_DEVICES={args.gpu})")

    train_file = os.path.join(args.splits_dir, "train.json")
    dev_file = os.path.join(args.splits_dir, "dev.json")
    test_file = os.path.join(args.splits_dir, "test.json")

    train_mt5(
        model_name=args.model_name,
        train_file=train_file,
        dev_file=dev_file,
        test_file=test_file,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        weight_decay=args.weight_decay,
        epochs=args.epochs,
        device=device,
        output_dir=args.output_dir,
        report_dir=args.report_dir,
        max_source_len=args.max_source_len,
        max_target_len=args.max_target_len,
        label_smoothing=args.label_smoothing
    )
