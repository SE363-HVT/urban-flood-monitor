"""
AI/bartpho/word_base/finetune/train_generative_aste.py
--------------------------------------------------------------------------------
Fine-tuning Script for Generative ASTE using BARTpho-word-base (vinai/bartpho-word-base)
on HCMC Flood Multimodal Dataset V3 splits.

Key features:
- Backbone: vinai/bartpho-word-base (Word-level Seq2Seq Transformer)
- Dynamic padding & GPU batching with FP16 Automatic Mixed Precision
- Linear warmup schedule with weight decay (AdamW)
- Saves best checkpoint based on validation loss
- Saves metadata and training history logs
"""

import os
import sys
import json
import time
import argparse
from typing import List, Dict, Any, Optional

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    get_linear_schedule_with_warmup
)
from tqdm import tqdm

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Navigate paths
WORD_BASE_DIR = os.path.dirname(SCRIPT_DIR)
BARTPHO_DIR = os.path.dirname(WORD_BASE_DIR)
AI_DIR = os.path.dirname(BARTPHO_DIR)
PROJECT_ROOT = os.path.dirname(AI_DIR)

DEFAULT_DATA_DIR = os.path.join(BARTPHO_DIR, "data")
DEFAULT_OUTPUT_DIR = os.path.join(WORD_BASE_DIR, "finetune", "checkpoints", "best_aste_model")


class ASTEDataset(Dataset):
    """Dataset loading paired text-to-triplet sequence examples."""
    def __init__(
        self,
        json_path: str,
        tokenizer,
        max_source_len: int = 160,
        max_target_len: int = 80
    ):
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
        input_text = item["input_text"]
        target_text = item["target_text"]

        source_enc = self.tokenizer(
            input_text,
            max_length=self.max_source_len,
            padding=False,
            truncation=True,
            return_tensors=None
        )

        target_enc = self.tokenizer(
            target_text,
            max_length=self.max_target_len,
            padding=False,
            truncation=True,
            return_tensors=None
        )

        return {
            "input_ids": source_enc["input_ids"],
            "attention_mask": source_enc["attention_mask"],
            "labels": target_enc["input_ids"]
        }


def collate_fn(batch, pad_token_id: int):
    """Dynamic padding for input sequences and target labels."""
    input_ids = [torch.tensor(x["input_ids"], dtype=torch.long) for x in batch]
    attention_mask = [torch.tensor(x["attention_mask"], dtype=torch.long) for x in batch]
    labels = [torch.tensor(x["labels"], dtype=torch.long) for x in batch]

    padded_inputs = torch.nn.utils.rnn.pad_sequence(
        input_ids, batch_first=True, padding_value=pad_token_id
    )
    padded_masks = torch.nn.utils.rnn.pad_sequence(
        attention_mask, batch_first=True, padding_value=0
    )
    # Mask pad tokens in labels with -100 for CrossEntropyLoss
    padded_labels = torch.nn.utils.rnn.pad_sequence(
        labels, batch_first=True, padding_value=-100
    )

    return {
        "input_ids": padded_inputs,
        "attention_mask": padded_masks,
        "labels": padded_labels
    }


def evaluate(model, val_loader, device, use_amp: bool = True) -> float:
    """Evaluate cross-entropy loss on validation split."""
    model.eval()
    total_loss = 0.0
    total_steps = 0

    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch["input_ids"].to(device, non_blocking=True)
            attention_mask = batch["attention_mask"].to(device, non_blocking=True)
            labels = batch["labels"].to(device, non_blocking=True)

            with torch.amp.autocast('cuda', enabled=use_amp):
                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                loss = outputs.loss

            total_loss += loss.item()
            total_steps += 1

    return total_loss / max(1, total_steps)


def train():
    parser = argparse.ArgumentParser(description="Fine-tune BARTpho for Generative ASTE")
    parser.add_argument("--model_name", type=str, default="vinai/bartpho-word-base", help="Pretrained model identifier")
    parser.add_argument("--epochs", type=int, default=25, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=16, help="Training batch size")
    parser.add_argument("--learning_rate", type=float, default=4e-5, help="Peak learning rate")
    parser.add_argument("--weight_decay", type=float, default=0.01, help="Weight decay for AdamW")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=1, help="Gradient accumulation steps")
    parser.add_argument("--max_source_len", type=int, default=160, help="Max source sequence length")
    parser.add_argument("--max_target_len", type=int, default=80, help="Max target sequence length")
    parser.add_argument("--data_dir", type=str, default=DEFAULT_DATA_DIR, help="Path to data directory with train.json and val.json")
    parser.add_argument("--output_dir", type=str, default=DEFAULT_OUTPUT_DIR, help="Output directory for best model checkpoint")
    parser.add_argument("--patience", type=int, default=7, help="Early stopping patience (epochs without validation loss improvement)")
    parser.add_argument("--no_amp", action="store_true", help="Disable FP16 automatic mixed precision")

    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_amp = (not args.no_amp) and torch.cuda.is_available()

    print("=" * 75)
    print("KHỞI CHẠY HUẤN LUYỆN GENERATIVE ASTE (TEXT-TO-TRIPLET) - BARTPHO-WORD-BASE")
    print(f"  • Backbone Model    : {args.model_name}")
    print(f"  • Compute Device    : {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print(f"  • Mixed Precision   : {'ENABLED (FP16 AMP)' if use_amp else 'DISABLED (FP32)'}")
    print(f"  • Epochs            : {args.epochs}")
    print(f"  • Batch Size        : {args.batch_size} (Grad Accum: {args.gradient_accumulation_steps})")
    print(f"  • Learning Rate     : {args.learning_rate}")
    print(f"  • Weight Decay      : {args.weight_decay}")
    print(f"  • Max Source / Target: {args.max_source_len} / {args.max_target_len}")
    print(f"  • Data Directory    : {args.data_dir}")
    print(f"  • Checkpoint Dest   : {args.output_dir}")
    print("=" * 75)

    # 1. Load Tokenizer & Model
    print(f"[*] Đang nạp mô hình & tokenizer {args.model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name)
    model.to(device)

    pad_token_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 1

    # 2. Prepare DataLoaders
    train_file = os.path.join(args.data_dir, "train.json")
    val_file = os.path.join(args.data_dir, "val.json")

    if not os.path.exists(train_file) or not os.path.exists(val_file):
        raise FileNotFoundError(f"Missing train or val dataset in {args.data_dir}. Run prepare_dataset.py first!")

    train_dataset = ASTEDataset(train_file, tokenizer, args.max_source_len, args.max_target_len)
    val_dataset = ASTEDataset(val_file, tokenizer, args.max_source_len, args.max_target_len)

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=2,
        pin_memory=True if torch.cuda.is_available() else False,
        collate_fn=lambda b: collate_fn(b, pad_token_id)
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=2,
        pin_memory=True if torch.cuda.is_available() else False,
        collate_fn=lambda b: collate_fn(b, pad_token_id)
    )

    print(f"[*] Dữ liệu huấn luyện: {len(train_dataset):,} mẫu ({len(train_loader)} bước/epoch) | Val: {len(val_dataset):,} mẫu")

    # 3. Optimizer & Scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    total_training_steps = (len(train_loader) // args.gradient_accumulation_steps) * args.epochs
    warmup_steps = int(total_training_steps * 0.10)
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_training_steps
    )
    scaler = torch.amp.GradScaler('cuda', enabled=use_amp)

    # 4. Training Loop
    best_val_loss = float("inf")
    best_epoch = 0
    epochs_no_improve = 0
    os.makedirs(args.output_dir, exist_ok=True)
    history = []

    print("\n[+] Bắt đầu tối ưu hóa mạng nơ-ron qua các epoch...")
    start_train_time = time.time()

    for epoch in range(1, args.epochs + 1):
        epoch_start_time = time.time()
        model.train()
        epoch_loss = 0.0
        step_count = 0

        pbar = tqdm(train_loader, desc=f"Epoch {epoch:02d}/{args.epochs:02d}", leave=False)
        optimizer.zero_grad()

        for step, batch in enumerate(pbar, 1):
            input_ids = batch["input_ids"].to(device, non_blocking=True)
            attention_mask = batch["attention_mask"].to(device, non_blocking=True)
            labels = batch["labels"].to(device, non_blocking=True)

            with torch.amp.autocast('cuda', enabled=use_amp):
                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                loss = outputs.loss / args.gradient_accumulation_steps

            scaler.scale(loss).backward()

            if step % args.gradient_accumulation_steps == 0 or step == len(train_loader):
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                scale_before = scaler.get_scale()
                scaler.step(optimizer)
                scaler.update()
                scale_after = scaler.get_scale()
                if scale_before <= scale_after:
                    scheduler.step()
                optimizer.zero_grad()

            loss_val = loss.item() * args.gradient_accumulation_steps
            epoch_loss += loss_val
            step_count += 1
            pbar.set_postfix({
                "loss": f"{loss_val:.4f}",
                "lr": f"{scheduler.get_last_lr()[0]:.2e}"
            })

        avg_train_loss = epoch_loss / max(1, step_count)
        val_loss = evaluate(model, val_loader, device, use_amp=use_amp)
        epoch_duration = time.time() - epoch_start_time

        is_best = val_loss < best_val_loss
        star = "⭐ [BEST]" if is_best else ""

        print(f"Epoch {epoch:02d}/{args.epochs:02d} [{epoch_duration:.1f}s] - "
              f"Train Loss: {avg_train_loss:.4f} | Val Loss: {val_loss:.4f} | "
              f"LR: {scheduler.get_last_lr()[0]:.2e} {star}")

        history.append({
            "epoch": epoch,
            "train_loss": round(avg_train_loss, 4),
            "val_loss": round(val_loss, 4),
            "lr": scheduler.get_last_lr()[0],
            "duration_sec": round(epoch_duration, 1)
        })

        if is_best:
            best_val_loss = val_loss
            best_epoch = epoch
            epochs_no_improve = 0
            # Save checkpoint
            model.save_pretrained(args.output_dir)
            tokenizer.save_pretrained(args.output_dir)

            meta = {
                "model_name": args.model_name,
                "best_epoch": best_epoch,
                "best_val_loss": round(best_val_loss, 4),
                "batch_size": args.batch_size,
                "learning_rate": args.learning_rate,
                "max_source_len": args.max_source_len,
                "max_target_len": args.max_target_len,
                "total_epochs": args.epochs,
                "timestamp": int(time.time()),
                "history": history
            }
            with open(os.path.join(args.output_dir, "training_meta.json"), "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= args.patience:
                print(f"\n[!] Early Stopping kích hoạt sau {args.patience} epoch không cải thiện validation loss!")
                break

    total_time = time.time() - start_train_time
    print("\n" + "=" * 75)
    print(f"🎉 HUẤN LUYỆN HOÀN TẤT TRONG {total_time // 60:.0f} PHÚT {total_time % 60:.1f} GIÂY!")
    print(f"   • Best Epoch       : {best_epoch}")
    print(f"   • Lowest Val Loss  : {best_val_loss:.4f}")
    print(f"   • Checkpoint Path  : {args.output_dir}")
    print("=" * 75)


if __name__ == "__main__":
    train()
