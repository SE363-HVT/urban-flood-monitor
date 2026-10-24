"""
finetune/train_generative_aste.py
Kịch bản huấn luyện mô hình Generative ASTE (Text-to-Triplet) cho bài toán ngập lụt TP.HCM:
- Hỗ trợ các Backbone Pretrained SOTA tiếng Việt:
  + vinai/bartpho-syllable (Mặc định: Rất ổn định, tối ưu tiếng Việt)
  + VietAI/vit5-base (Kiến trúc Google T5)
- Tối ưu hóa GPU CUDA với Mixed Precision (FP16) trên RTX 2080 Ti.
- Tự động lưu checkpoint tốt nhất theo Validation Loss.
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

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")
DEFAULT_OUTPUT_DIR = os.path.join(CURRENT_DIR, "checkpoints", "best_aste_model")


class ASTEDataset(Dataset):
    """Dataset đọc dữ liệu trực tiếp từ các file JSON."""
    def __init__(
        self,
        json_path: str,
        tokenizer,
        max_source_len: int = 256,
        max_target_len: int = 128
    ):
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Không tìm thấy file: {json_path}")
            
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

        # Encode chuỗi đầu vào
        source_enc = self.tokenizer(
            input_text,
            max_length=self.max_source_len,
            padding=False,
            truncation=True,
            return_tensors=None
        )

        # Encode chuỗi mục tiêu
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


def collate_fn(batch, tokenizer, pad_token_id: int):
    """Đệm động (Dynamic Padding) theo độ dài dài nhất của từng batch."""
    input_ids = [torch.tensor(x["input_ids"], dtype=torch.long) for x in batch]
    attention_mask = [torch.tensor(x["attention_mask"], dtype=torch.long) for x in batch]
    labels = [torch.tensor(x["labels"], dtype=torch.long) for x in batch]

    # Pad inputs
    padded_inputs = torch.nn.utils.rnn.pad_sequence(
        input_ids, batch_first=True, padding_value=pad_token_id
    )
    padded_masks = torch.nn.utils.rnn.pad_sequence(
        attention_mask, batch_first=True, padding_value=0
    )

    # Pad labels (thay thế pad_token_id bằng -100 để bỏ qua trong CrossEntropyLoss)
    padded_labels = torch.nn.utils.rnn.pad_sequence(
        labels, batch_first=True, padding_value=-100
    )

    return {
        "input_ids": padded_inputs,
        "attention_mask": padded_masks,
        "labels": padded_labels
    }


def load_model_and_tokenizer(model_name: str):
    """Nạp Tokenizer và Mô hình Seq2Seq với khả năng tương thích cao."""
    print(f"[*] Đang tải mô hình & tokenizer: {model_name}...")
    
    if "vit5" in model_name.lower():
        # Đối với ViT5, sử dụng cơ chế nạp SentencePiece tùy chỉnh
        from transformers import T5Tokenizer
        import sentencepiece as spm
        from huggingface_hub import hf_hub_download
        
        spm_file = hf_hub_download(model_name, "spiece.model")
        sp = spm.SentencePieceProcessor()
        sp.load(spm_file)
        vocab = [(sp.id_to_piece(i), sp.get_score(i)) for i in range(sp.get_piece_size())]
        tokenizer = T5Tokenizer(vocab=vocab)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    else:
        # Đối với BARTpho hoặc các mô hình Seq2Seq chuẩn
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    return tokenizer, model


def evaluate(model, val_loader, device, use_amp: bool = True) -> float:
    """Đánh giá loss trên tập kiểm thử validation."""
    model.eval()
    total_loss = 0.0
    total_steps = 0

    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            with torch.cuda.amp.autocast(enabled=use_amp):
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
    parser = argparse.ArgumentParser(description="Huấn luyện mô hình Generative ASTE cho Ngập lụt TP.HCM")
    parser.add_argument("--model_name", type=str, default="vinai/bartpho-syllable", help="Mô hình Pretrained (vinai/bartpho-syllable hoặc VietAI/vit5-base)")
    parser.add_argument("--epochs", type=int, default=6, help="Số lượng epoch huấn luyện (Khuyên dùng: 6 - 10)")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size (Mặc định: 8)")
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="Learning rate (Mặc định: 5e-5)")
    parser.add_argument("--max_source_len", type=int, default=256, help="Độ dài tối đa câu đầu vào")
    parser.add_argument("--max_target_len", type=int, default=128, help="Độ dài tối đa chuỗi triplet sinh ra")
    parser.add_argument("--output_dir", type=str, default=DEFAULT_OUTPUT_DIR, help="Thư mục lưu checkpoint tốt nhất")
    parser.add_argument("--no_amp", action="store_true", help="Vô hiệu hóa Mixed Precision (FP16)")

    args = parser.parse_args()

    # Kiểm tra thiết bị tính toán
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_amp = (not args.no_amp) and torch.cuda.is_available()

    print("=" * 70)
    print("KHỞI CHẠY HUẤN LUYỆN GENERATIVE ASTE (TEXT-TO-TRIPLET)")
    print(f"  • Mô hình nền tảng  : {args.model_name}")
    print(f"  • Thiết bị phần cứng: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print(f"  • Mixed Precision   : {'BẬT (FP16)' if use_amp else 'TẮT (FP32)'}")
    print(f"  • Epochs            : {args.epochs}")
    print(f"  • Batch Size        : {args.batch_size}")
    print(f"  • Learning Rate     : {args.learning_rate}")
    print(f"  • Thư mục đích      : {args.output_dir}")
    print("=" * 70)

    # 1. Nạp Tokenizer và Mô hình
    tokenizer, model = load_model_and_tokenizer(args.model_name)
    model.to(device)

    pad_token_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0

    # 2. Chuẩn bị DataLoader
    train_file = os.path.join(DATA_DIR, "train.json")
    val_file = os.path.join(DATA_DIR, "val.json")

    if not os.path.exists(train_file):
        print(f"[!] Lỗi: Chưa tìm thấy {train_file}. Vui lòng chạy 'python finetune/prepare_dataset.py' trước!")
        sys.exit(1)

    train_dataset = ASTEDataset(train_file, tokenizer, args.max_source_len, args.max_target_len)
    val_dataset = ASTEDataset(val_file, tokenizer, args.max_source_len, args.max_target_len)

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=lambda b: collate_fn(b, tokenizer, pad_token_id)
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=lambda b: collate_fn(b, tokenizer, pad_token_id)
    )

    print(f"[*] Kích thước dữ liệu: {len(train_dataset)} mẫu Train ({len(train_loader)} bước/epoch) | {len(val_dataset)} mẫu Val")

    # 3. Cấu hình Optimizer và Scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=0.01)
    total_training_steps = len(train_loader) * args.epochs
    warmup_steps = int(total_training_steps * 0.1)  # 10% warmup
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_training_steps)
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)

    # 4. Vòng lặp Huấn luyện (Training Loop)
    best_val_loss = float("inf")
    os.makedirs(args.output_dir, exist_ok=True)

    print("\n[+] Bắt đầu quá trình tối ưu hóa trọng số...")
    start_train_time = time.time()

    for epoch in range(1, args.epochs + 1):
        model.train()
        epoch_loss = 0.0
        step_count = 0
        pbar = tqdm(train_loader, desc=f"Epoch {epoch}/{args.epochs}")

        for batch in pbar:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()

            with torch.cuda.amp.autocast(enabled=use_amp):
                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                loss = outputs.loss

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            scaler.step(optimizer)
            scaler.update()
            scheduler.step()

            epoch_loss += loss.item()
            step_count += 1
            pbar.set_postfix({"train_loss": f"{loss.item():.4f}", "lr": f"{scheduler.get_last_lr()[0]:.2e}"})

        avg_train_loss = epoch_loss / max(1, step_count)

        # Đánh giá trên tập Validation
        val_loss = evaluate(model, val_loader, device, use_amp=use_amp)

        print(f"\n>> [Tổng kết Epoch {epoch}/{args.epochs}]: Train Loss = {avg_train_loss:.4f} | Val Loss = {val_loss:.4f}")

        # Lưu Checkpoint tốt nhất
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            print(f"⭐ Val Loss cải thiện ({val_loss:.4f})! Đang lưu mô hình tốt nhất vào: {args.output_dir}...")
            model.save_pretrained(args.output_dir)
            tokenizer.save_pretrained(args.output_dir)

            # Lưu file thông tin metadata
            meta = {
                "base_model": args.model_name,
                "best_epoch": epoch,
                "best_val_loss": round(best_val_loss, 4),
                "timestamp": int(time.time())
            }
            with open(os.path.join(args.output_dir, "training_meta.json"), "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)

    total_time = time.time() - start_train_time
    print("\n" + "=" * 70)
    print(f"🎉 HUẤN LUYỆN HOÀN TẤT TRONG {total_time // 60:.0f} PHÚT {total_time % 60:.1f} GIÂY!")
    print(f"   • Val Loss thấp nhất: {best_val_loss:.4f}")
    print(f"   • Checkpoint tối ưu sẵn sàng tại: {args.output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    train()
