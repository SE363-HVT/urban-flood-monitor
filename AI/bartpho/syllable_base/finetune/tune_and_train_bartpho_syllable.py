#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/tune_and_train_bartpho_syllable.py
--------------------------------------------------------------------------------
Optuna Hyperparameter Tuning (3 Trials x 5 Epochs) followed by Full 30-Epoch
Fine-Tuning of BARTpho Syllable Base (vinai/bartpho-syllable-base) on HCMC Flood V3 Splits.

Workflow:
    Stage 1: Optuna Optimization
      - 3 Trials exploring: learning_rate, batch_size, weight_decay.
      - 5 Epochs per trial on train.json evaluated against val.json.
      - Objective: Minimize Seq2Seq Validation Cross-Entropy Loss.
    Stage 2: Full Fine-Tuning (30 Epochs)
      - Retrain from scratch using the winning hyperparameter configuration.
      - 30 Epochs with FP16 mixed precision and linear warmup.
      - Save optimal checkpoint to:
        AI/bartpho/syllable_base/finetune/checkpoints/best_aste_model/
    Stage 3: Independent Test Split Evaluation
      - Evaluates on test.json (462 test samples).
      - Saves benchmark report to AI/bartpho/syllable_base/test/benchmark_reports/bartpho_syllable_test_report.json.
      - Updates master benchmark table in AI/results/.
"""

import os
import sys
import gc
import json
import time
import random
import argparse
from typing import Dict, Any, List

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    get_linear_schedule_with_warmup
)
from tqdm import tqdm
import optuna

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

optuna.logging.set_verbosity(optuna.logging.INFO)

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(RANDOM_SEED)

PYTHON_EXE = "/home/counting/anaconda3/envs/ryan_env/bin/python"

GPU_UUID_MAP = {
    0: "GPU-402b1880-531f-0736-be2e-03a8a229590b",
    2: "GPU-40888ad5-fe5d-17c8-a236-4b0fd1d97e6f",
    3: "GPU-17220462-c4da-32ae-f317-0c0e97d6e63e"
}

DEFAULT_DATA_DIR = os.path.join(PROJECT_ROOT, "AI", "bartpho", "data")
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "AI", "bartpho", "syllable_base", "finetune", "checkpoints", "best_aste_model")
DEFAULT_REPORT_DIR = os.path.join(PROJECT_ROOT, "AI", "bartpho", "syllable_base", "test", "benchmark_reports")


class ASTEDataset(Dataset):
    def __init__(self, json_path: str, tokenizer, max_source_len: int = 160, max_target_len: int = 80):
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
        s_enc = self.tokenizer(item["input_text"], max_length=self.max_source_len, padding=False, truncation=True, return_tensors=None)
        t_enc = self.tokenizer(item["target_text"], max_length=self.max_target_len, padding=False, truncation=True, return_tensors=None)
        return {
            "input_ids": s_enc["input_ids"],
            "attention_mask": s_enc["attention_mask"],
            "labels": t_enc["input_ids"]
        }


def collate_fn(batch: List[Dict[str, Any]], pad_token_id: int):
    input_ids = [torch.tensor(x["input_ids"], dtype=torch.long) for x in batch]
    attention_mask = [torch.tensor(x["attention_mask"], dtype=torch.long) for x in batch]
    labels = [torch.tensor(x["labels"], dtype=torch.long) for x in batch]

    p_in = torch.nn.utils.rnn.pad_sequence(input_ids, batch_first=True, padding_value=pad_token_id)
    p_att = torch.nn.utils.rnn.pad_sequence(attention_mask, batch_first=True, padding_value=0)
    p_lab = torch.nn.utils.rnn.pad_sequence(labels, batch_first=True, padding_value=-100)

    return {"input_ids": p_in, "attention_mask": p_att, "labels": p_lab}


def evaluate_loss(model, val_loader, device, use_amp: bool = True) -> float:
    model.eval()
    total_loss = 0.0
    total_steps = 0
    with torch.no_grad():
        for batch in val_loader:
            in_ids = batch["input_ids"].to(device, non_blocking=True)
            att_m = batch["attention_mask"].to(device, non_blocking=True)
            labs = batch["labels"].to(device, non_blocking=True)

            with torch.amp.autocast('cuda', enabled=use_amp):
                loss = model(input_ids=in_ids, attention_mask=att_m, labels=labs).loss
            total_loss += loss.item()
            total_steps += 1
    return total_loss / max(1, total_steps)


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
    max_source_len: int = 160,
    max_target_len: int = 80,
    save_output_dir: str = None,
    trial_prefix: str = ""
) -> Dict[str, Any]:
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 1
    train_ds = ASTEDataset(train_file, tokenizer, max_source_len, max_target_len)
    val_ds = ASTEDataset(val_file, tokenizer, max_source_len, max_target_len)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=2, pin_memory=True, collate_fn=lambda b: collate_fn(b, pad_id))
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True, collate_fn=lambda b: collate_fn(b, pad_id))

    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    total_steps = len(train_loader) * epochs
    warmup_steps = int(0.10 * total_steps)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps)
    scaler = torch.amp.GradScaler('cuda', enabled=device.type == "cuda")

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
                loss = model(input_ids=in_ids, attention_mask=att_m, labels=labs).loss

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()

            train_loss += loss.item()
            step_c += 1

        avg_train_loss = train_loss / max(1, step_c)
        val_loss = evaluate_loss(model, val_loader, device, use_amp=device.type == "cuda")
        dur = time.time() - t0

        is_best = val_loss < best_val_loss
        star = "⭐ [BEST]" if is_best else ""

        print(f"  {trial_prefix}Epoch {epoch:02d}/{epochs:02d} [{dur:.1f}s] - "
              f"Train Loss: {avg_train_loss:.4f} | Val Loss: {val_loss:.4f} | "
              f"LR: {scheduler.get_last_lr()[0]:.2e} {star}")
        sys.stdout.flush()

        history.append({
            "epoch": epoch,
            "train_loss": round(avg_train_loss, 4),
            "val_loss": round(val_loss, 4),
            "lr": scheduler.get_last_lr()[0],
            "duration_sec": round(dur, 1)
        })

        if is_best:
            best_val_loss = val_loss
            best_epoch = epoch
            if save_output_dir:
                os.makedirs(save_output_dir, exist_ok=True)
                model.save_pretrained(save_output_dir)
                tokenizer.save_pretrained(save_output_dir)

    if save_output_dir:
        meta = {
            "model_name": model_name,
            "best_epoch": best_epoch,
            "best_val_loss": round(best_val_loss, 4),
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "weight_decay": weight_decay,
            "total_epochs": epochs,
            "history": history
        }
        with open(os.path.join(save_output_dir, "training_meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

    del model, optimizer, scheduler, train_loader, val_loader
    torch.cuda.empty_cache()
    gc.collect()

    return {
        "best_epoch": best_epoch,
        "best_val_loss": round(best_val_loss, 4),
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
    parser.add_argument("--gpu", type=int, default=0, choices=[0, 2, 3], help="GPU index (0, 2, or 3)")

    args = parser.parse_args()

    gpu_uuid = GPU_UUID_MAP[args.gpu]
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu_uuid
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("=" * 80)
    print("🚀 RADI-NET ASTE: OPTUNA TUNING & 30-EPOCH TRAINING - BARTPHO-SYLLABLE-BASE")
    print(f"  • Model Backbone : {args.model_name}")
    print(f"  • GPU Target     : GPU {args.gpu} (UUID: {gpu_uuid})")
    print(f"  • Device Active  : {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print(f"  • Optuna Config  : {args.trials} Trials × {args.trial_epochs} Epochs")
    print(f"  • Final Training : {args.train_epochs} Epochs")
    print(f"  • Output Path    : {args.output_dir}")
    print("=" * 80)
    sys.stdout.flush()

    train_file = os.path.join(args.data_dir, "train.json")
    val_file = os.path.join(args.data_dir, "val.json")
    test_file = os.path.join(args.data_dir, "test.json")

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    os.makedirs(os.path.dirname(args.output_dir), exist_ok=True)
    os.makedirs(args.report_dir, exist_ok=True)

    # 1. Stage 1: Optuna Optimization
    print("\n" + "=" * 80)
    print("STAGE 1: KHỞI ĐỘNG OPTUNA TÌM SIÊU THAM SỐ TỐI ƯU CHO BARTPHO SYLLABLE")
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
            trial_prefix=f"[Trial {trial.number + 1}] "
        )
        val_loss = res["best_val_loss"]
        print(f"==> Kết thúc Trial {trial.number + 1}: Best Val Loss = {val_loss:.4f} (Epoch {res['best_epoch']})")
        sys.stdout.flush()
        return val_loss

    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=RANDOM_SEED))
    study.optimize(objective, n_trials=args.trials)

    best_params = study.best_params
    best_loss = study.best_value

    study_summary = {
        "best_trial_number": study.best_trial.number + 1,
        "best_val_loss": round(best_loss, 4),
        "best_params": best_params,
        "all_trials": [
            {
                "trial": t.number + 1,
                "val_loss": round(t.value, 4) if t.value is not None else None,
                "params": t.params
            }
            for t in study.trials
        ]
    }
    study_file = os.path.join(args.report_dir, "optuna_study.json")
    with open(study_file, "w", encoding="utf-8") as f:
        json.dump(study_summary, f, indent=2)

    # Also mirror into checkpoints dir
    with open(os.path.join(os.path.dirname(args.output_dir), "optuna_study.json"), "w", encoding="utf-8") as f:
        json.dump(study_summary, f, indent=2)

    print("\n" + "=" * 80)
    print("🎉 KẾT QUẢ OPTUNA CHO BARTPHO SYLLABLE BASE:")
    print(f"  • Best Trial   : #{study.best_trial.number + 1}")
    print(f"  • Best Val Loss: {best_loss:.4f}")
    print(f"  • Best Params  : {best_params}")
    print("=" * 80)
    sys.stdout.flush()

    # 2. Stage 2: Full Fine-Tuning 30 Epochs
    print("\n" + "=" * 80)
    print(f"STAGE 2: BẮT ĐẦU HUẤN LUYỆN TOÀN DIỆN {args.train_epochs} EPOCHS VỚI THAM SỐ THẮNG CUỘC")
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
        save_output_dir=args.output_dir,
        trial_prefix="[Full Train] "
    )

    print("\n" + "=" * 80)
    print("✅ HUẤN LUYỆN 30 EPOCHS HOÀN TẤT THÀNH CÔNG!")
    print(f"  • Checkpoint Path : {args.output_dir}")
    print(f"  • Best Epoch      : {final_res['best_epoch']}")
    print(f"  • Lowest Val Loss : {final_res['best_val_loss']:.4f}")
    print("=" * 80)
    sys.stdout.flush()

    # 3. Stage 3: Independent Test Split Evaluation
    print("\n" + "=" * 80)
    print("STAGE 3: ĐÁNH GIÁ ĐỘC LẬP TRÊN TẬP TEST (462 MẪU)")
    print("=" * 80)
    sys.stdout.flush()

    eval_script = os.path.join(PROJECT_ROOT, "AI", "bartpho", "syllable_base", "test", "evaluate_aste.py")
    report_file = os.path.join(args.report_dir, "bartpho_syllable_test_report.json")
    import subprocess
    cmd_eval = [
        PYTHON_EXE, "-u", eval_script,
        "--checkpoint_dir", args.output_dir,
        "--output_report", report_file
    ]
    subprocess.run(cmd_eval, check=True, env=os.environ)

    # 4. Inference Demo
    infer_script = os.path.join(PROJECT_ROOT, "AI", "bartpho", "syllable_base", "test", "inference.py")
    subprocess.run([PYTHON_EXE, "-u", infer_script], check=True, env=os.environ)

    # 5. Update Master Comparison Table in AI/results
    print("\n" + "=" * 80)
    print("📈 CẬP NHẬT BẢNG SO SÁNH TỔNG HỢP TRONG AI/results/")
    print("=" * 80)
    update_script = os.path.join(PROJECT_ROOT, "scripts", "benchmark_heuristic_baseline.py")
    subprocess.run([PYTHON_EXE, "-u", update_script], check=True, env=os.environ)


if __name__ == "__main__":
    main()
