#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI/xlm_roberta/base/semeval_v2/finetune/tune_and_train_xlm_roberta_semeval_v2.py
--------------------------------------------------------------------------------
Stage 1: Optuna Hyperparameter Optimization (3 Trials x 5 Epochs)
Stage 2: Full Fine-Tuning with Winning Hyperparameters (Early Stopping Patience = 5)
Stage 3: Independent Evaluation on SemEval v2 Test Split

Backbone: xlm-roberta-base
Target: Maximize Validation Strict SemEval v2 Triplet F1
"""

import os
import sys
import gc
import json
import time
import argparse
import random
import subprocess
from typing import Dict, Any, List

try:
    import setproctitle
    setproctitle.setproctitle("python")
except Exception:
    pass

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, get_linear_schedule_with_warmup
from tqdm import tqdm
import optuna

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FINETUNE_DIR = SCRIPT_DIR
SEMEVAL_DIR = os.path.dirname(FINETUNE_DIR)

def get_project_root():
    curr = os.path.abspath(SCRIPT_DIR)
    while curr != os.path.dirname(curr):
        if os.path.exists(os.path.join(curr, ".git")) or os.path.exists(os.path.join(curr, "data")):
            return curr
        curr = os.path.dirname(curr)
    return "/home/counting/Workspaces/ryan/RadiNet"

PROJECT_ROOT = get_project_root()
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if FINETUNE_DIR not in sys.path:
    sys.path.insert(0, FINETUNE_DIR)

from train_xlm_roberta_semeval_v2 import (
    XLMRobertaForSemEvalASTE,
    SemEvalXLMRobertaASTEDataset,
    semeval_collate_fn,
    evaluate_val_triplet_f1,
    seed_everything,
    seed_worker,
    RANDOM_SEED
)

optuna.logging.set_verbosity(optuna.logging.INFO)


def train_single_epoch(model, loader, optimizer, scheduler, scaler, device):
    model.train()
    total_loss = 0.0
    steps = 0
    for batch in loader:
        in_ids = batch["input_ids"].to(device, non_blocking=True)
        att_m = batch["attention_mask"].to(device, non_blocking=True)
        bio_tags = batch["bio_tags"].to(device, non_blocking=True)
        raw_batch = batch["raw_batch"]

        optimizer.zero_grad()
        with torch.amp.autocast('cuda', enabled=device.type == "cuda"):
            outputs = model(input_ids=in_ids, attention_mask=att_m, bio_tags=bio_tags, raw_batch=raw_batch)
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
        steps += 1
    return total_loss / max(1, steps)


def run_training_cycle(
    model_name: str,
    train_ds: SemEvalXLMRobertaASTEDataset,
    val_ds: SemEvalXLMRobertaASTEDataset,
    device: torch.device,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    weight_decay: float,
    dropout: float,
    save_checkpoint_path: str = None,
    patience: int = 5,
    trial_prefix: str = ""
) -> Dict[str, Any]:
    seed_everything(RANDOM_SEED)
    g = torch.Generator()
    g.manual_seed(RANDOM_SEED)

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=semeval_collate_fn,
        generator=g,
        worker_init_fn=seed_worker,
        num_workers=2,
        pin_memory=True
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=semeval_collate_fn,
        num_workers=2,
        pin_memory=True
    )

    model = XLMRobertaForSemEvalASTE(model_name=model_name, dropout_rate=dropout).to(device)

    # Differential learning rate
    optimizer_grouped_parameters = [
        {"params": [p for n, p in model.encoder.named_parameters() if p.requires_grad], "lr": learning_rate, "weight_decay": weight_decay},
        {"params": [p for n, p in model.tag_classifier.named_parameters() if p.requires_grad], "lr": 1e-4, "weight_decay": weight_decay},
        {"params": [p for n, p in model.pair_dense.named_parameters() if p.requires_grad], "lr": 1e-4, "weight_decay": weight_decay},
        {"params": [p for n, p in model.polarity_head.named_parameters() if p.requires_grad], "lr": 1e-4, "weight_decay": weight_decay},
    ]

    optimizer = torch.optim.AdamW(optimizer_grouped_parameters)
    total_steps = len(train_loader) * epochs
    warmup_steps = int(total_steps * 0.1)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps)
    scaler = torch.amp.GradScaler('cuda', enabled=device.type == "cuda")

    best_val_f1 = -1.0
    best_val_loss = float("inf")
    best_epoch = 0
    patience_cnt = 0
    history = []

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        train_loss = train_single_epoch(model, train_loader, optimizer, scheduler, scaler, device)
        val_metrics = evaluate_val_triplet_f1(model, val_loader, device)
        dur = time.time() - t0

        val_f1 = val_metrics["val_f1"]
        val_loss = val_metrics["val_loss"]
        val_p = val_metrics["val_p"]
        val_r = val_metrics["val_r"]

        is_best = (val_f1 > best_val_f1) or (val_f1 == best_val_f1 and val_loss < best_val_loss)
        star = "⭐ [BEST]" if is_best else ""

        print(f"{trial_prefix}Epoch {epoch:02d}/{epochs:02d} [{dur:.1f}s] - Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val F1: {val_f1:.2f}% (P: {val_p:.2f}%, R: {val_r:.2f}%) {star}")
        sys.stdout.flush()

        history.append({
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "val_loss": val_loss,
            "val_f1": val_f1,
            "val_p": val_p,
            "val_r": val_r,
            "dur": round(dur, 1)
        })

        if is_best:
            best_val_f1 = val_f1
            best_val_loss = val_loss
            best_epoch = epoch
            patience_cnt = 0
            if save_checkpoint_path:
                os.makedirs(os.path.dirname(save_checkpoint_path), exist_ok=True)
                torch.save(model.state_dict(), save_checkpoint_path)
        else:
            patience_cnt += 1
            if patience_cnt >= patience:
                print(f"{trial_prefix}🛑 Early stopping kích hoạt tại Epoch {epoch}.")
                break

    del model, optimizer, scheduler, scaler
    torch.cuda.empty_cache()
    gc.collect()

    return {
        "best_epoch": best_epoch,
        "best_val_f1": best_val_f1,
        "best_val_loss": best_val_loss,
        "history": history
    }


def main():
    parser = argparse.ArgumentParser(description="Optuna Tuning & Full Fine-tuning for XLM-RoBERTa Base on SemEval v2")
    parser.add_argument("--model_name", type=str, default="xlm-roberta-base")
    parser.add_argument("--data_dir", type=str, default=os.path.join(PROJECT_ROOT, "data", "semeval_v2"))
    parser.add_argument("--checkpoints_dir", type=str, default=os.path.join(SEMEVAL_DIR, "finetune", "checkpoints"))
    parser.add_argument("--n_trials", type=int, default=3, help="Số trials Optuna (mặc định 3)")
    parser.add_argument("--trial_epochs", type=int, default=5, help="Số epochs mỗi trial Optuna (mặc định 5)")
    parser.add_argument("--final_epochs", type=int, default=25, help="Số epochs tối đa cho full training")
    parser.add_argument("--final_patience", type=int, default=5, help="Patience cho early stopping full training")
    parser.add_argument("--skip_optuna", action="store_true", help="Bỏ qua Optuna nếu đã có optuna_study.json và dùng best params đã tìm thấy")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("=" * 80)
    print("🚀 PIPELINE OPTUNA & HUẤN LUYỆN: XLM-ROBERTA BASE (SEMEVAL V2 FORMAT)")
    print(f"  • Device          : {device} ({torch.cuda.get_device_name(0) if device.type == 'cuda' else 'CPU'})")
    print(f"  • Data Directory  : {args.data_dir}")
    print(f"  • Checkpoints Dir : {args.checkpoints_dir}")
    print(f"  • Optuna Config   : {args.n_trials} trials x {args.trial_epochs} epochs")
    print(f"  • Full Train Ep   : {args.final_epochs} epochs (Early stopping patience = {args.final_patience})")
    print("=" * 80)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    train_path = os.path.join(args.data_dir, "train.json")
    dev_path = os.path.join(args.data_dir, "dev.json")
    test_path = os.path.join(args.data_dir, "test.json")

    print("\n⏳ Đang load datasets...")
    train_ds = SemEvalXLMRobertaASTEDataset(train_path, tokenizer, max_len=256)
    dev_ds = SemEvalXLMRobertaASTEDataset(dev_path, tokenizer, max_len=256)
    print(f"  ✓ Đã nạp: Train={len(train_ds):,} | Dev={len(dev_ds):,}\n")

    os.makedirs(args.checkpoints_dir, exist_ok=True)
    best_model_dir = os.path.join(args.checkpoints_dir, "best_model")
    os.makedirs(best_model_dir, exist_ok=True)

    optuna_path = os.path.join(args.checkpoints_dir, "optuna_study.json")
    if args.skip_optuna and os.path.exists(optuna_path):
        print("=" * 80)
        print(f"⏩ PHÁT HIỆN KẾT QUẢ OPTUNA CÓ SẴN TẠI: {optuna_path}")
        print("   BỎ QUA GIAI ĐOẠN 1 (OPTUNA) VÀ TIẾP TỤC HUẤN LUYỆN TOÀN DIỆN.")
        print("=" * 80)
        with open(optuna_path, "r", encoding="utf-8") as f:
            study_data = json.load(f)
        best_params = study_data["best_params"]
        best_score = study_data.get("best_score", 0.0)
        best_trial = study_data.get("best_trial_number", 1)
        print(f"  • Best Trial #    : {best_trial}")
        print(f"  • Best Val F1     : {best_score:.2f}%")
        print(f"  • Best Parameters : {json.dumps(best_params, indent=4)}")
        print("=" * 80 + "\n")
    else:
        # ==============================================================================
        # STAGE 1: OPTUNA HYPERPARAMETER TUNING (3 Trials x 5 Epochs)
        # ==============================================================================
        print("=" * 80)
        print(f"🔬 GIAI ĐOẠN 1: OPTUNA HYPERPARAMETER TUNING ({args.n_trials} Trials x {args.trial_epochs} Epochs)")
        print("=" * 80)

        def objective(trial: optuna.Trial) -> float:
            lr = trial.suggest_float("learning_rate", 1.5e-5, 4.5e-5, log=True)
            dropout = trial.suggest_float("dropout", 0.10, 0.25, step=0.05)
            weight_decay = trial.suggest_float("weight_decay", 1e-4, 1e-2, log=True)
            batch_size = trial.suggest_categorical("batch_size", [16])

            prefix = f"[Trial {trial.number + 1}/{args.n_trials} (lr={lr:.2e}, drop={dropout:.2f}, wd={weight_decay:.4f})] "
            print(f"\n{prefix}Bắt đầu huấn luyện {args.trial_epochs} epochs...")

            res = run_training_cycle(
                model_name=args.model_name,
                train_ds=train_ds,
                val_ds=dev_ds,
                device=device,
                epochs=args.trial_epochs,
                batch_size=batch_size,
                learning_rate=lr,
                weight_decay=weight_decay,
                dropout=dropout,
                save_checkpoint_path=None,
                patience=args.trial_epochs,
                trial_prefix=prefix
            )
            print(f"{prefix}Hoàn tất! Best Val Triplet F1: {res['best_val_f1']:.2f}% (Epoch {res['best_epoch']})")
            return res["best_val_f1"]

        study = optuna.create_study(direction="maximize", study_name="xlm_roberta_base_semeval_v2")
        study.optimize(objective, n_trials=args.n_trials)

        print("\n" + "=" * 80)
        print("🏆 KẾT QUẢ OPTUNA HYPERPARAMETER OPTIMIZATION:")
        print(f"  • Best Trial #    : {study.best_trial.number + 1}")
        print(f"  • Best Val F1     : {study.best_value:.2f}%")
        print(f"  • Best Parameters : {json.dumps(study.best_params, indent=4)}")
        print("=" * 80 + "\n")

        # Lưu kết quả Optuna
        optuna_results = {
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
        with open(optuna_path, "w", encoding="utf-8") as f:
            json.dump(optuna_results, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Đã lưu Optuna study tại: {optuna_path}\n")
        best_params = study.best_params

    # ==============================================================================
    # STAGE 2: FULL FINE-TUNING VỚI THAM SỐ CHIẾN THẮNG
    # ==============================================================================
    print("=" * 80)
    print("🔥 GIAI ĐOẠN 2: HUẤN LUYỆN TOÀN DIỆN (FULL FINE-TUNING) VỚI BEST HYPERPARAMETERS")
    print(f"  • Learning Rate   : {best_params['learning_rate']:.2e}")
    print(f"  • Dropout         : {best_params['dropout']:.2f}")
    print(f"  • Weight Decay    : {best_params['weight_decay']:.4e}")
    print(f"  • Batch Size      : {best_params['batch_size']}")
    print(f"  • Số Epochs tối đa: {args.final_epochs} (Patience: {args.final_patience})")
    print("=" * 80)

    final_model_path = os.path.join(best_model_dir, "xlm_roberta_aste_weights.pt")
    final_res = run_training_cycle(
        model_name=args.model_name,
        train_ds=train_ds,
        val_ds=dev_ds,
        device=device,
        epochs=args.final_epochs,
        batch_size=best_params["batch_size"],
        learning_rate=best_params["learning_rate"],
        weight_decay=best_params["weight_decay"],
        dropout=best_params["dropout"],
        save_checkpoint_path=final_model_path,
        patience=args.final_patience,
        trial_prefix="[Full Training] "
    )

    tokenizer.save_pretrained(best_model_dir)

    history_path = os.path.join(best_model_dir, "training_history.json")
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(final_res, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("✅ HOÀN TẤT GIAI ĐOẠN 2 HUẤN LUYỆN!")
    print(f"  • Best Checkpoint : {best_model_dir}")
    print(f"  • Best Epoch      : {final_res['best_epoch']}")
    print(f"  • Best Val F1     : {final_res['best_val_f1']:.2f}%")
    print("=" * 80 + "\n")

    # ==============================================================================
    # STAGE 3: TEST EVALUATION
    # ==============================================================================
    eval_script = os.path.join(SEMEVAL_DIR, "test", "evaluate_xlm_roberta_semeval_v2.py")
    if os.path.exists(eval_script):
        print("=" * 80)
        print("🎯 GIAI ĐOẠN 3: ĐÁNH GIÁ ĐỘC LẬP TRÊN TEST SET (data/semeval_v2/test.json)")
        print("=" * 80)
        cmd = [
            sys.executable, eval_script,
            "--checkpoint_dir", best_model_dir,
            "--test_file", test_path
        ]
        subprocess.run(cmd, check=True)
    else:
        print(f"⚠️ Không tìm thấy script đánh giá tại: {eval_script}")

    # ==============================================================================
    # STAGE 4: SYNC RESULTS TO BENCHMARK TABLE
    # ==============================================================================
    benchmark_table_path = os.path.join(PROJECT_ROOT, "AI", "results", "BENCHMARK_TABLE.md")
    report_file = os.path.join(SEMEVAL_DIR, "test", "benchmark_reports", "xlm_roberta_base_semeval_v2_report.json")
    if os.path.exists(benchmark_table_path) and os.path.exists(report_file):
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                rep = json.load(f)
            tm = rep.get("Triplet_Strict_Match", {})
            am = rep.get("Aspect_Span", {})
            om = rep.get("Opinion_Span", {})
            pos = rep.get("Polarity_Per_Class", {}).get("POS", {})
            macro = rep.get("Macro_Polarity_F1", 0.0)

            p_f1 = tm.get("F1", 0.0)
            p_prec = tm.get("Precision", 0.0)
            p_rec = tm.get("Recall", 0.0)
            a_f1 = am.get("F1", 0.0)
            o_f1 = om.get("F1", 0.0)
            pos_f1 = pos.get("F1", 0.0)

            with open(benchmark_table_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            new_lines = []
            in_part1 = False

            for line in lines:
                if "PHẦN 1: BẢNG BENCHMARK TRÊN ĐỊNH DẠNG MỚI" in line:
                    in_part1 = True
                elif "PHẦN 2:" in line:
                    in_part1 = False

                if in_part1 and "| **XLM-RoBERTa Base** |" in line:
                    new_line = f"| **XLM-RoBERTa Base** | *Extractive Span-Pair Multilingual* | {p_prec:.2f}% | {p_rec:.2f}% | **{p_f1:.2f}%** | {a_f1:.2f}% | {o_f1:.2f}% | {pos_f1:.2f}% | {macro:.2f}% |"
                    new_lines.append(new_line)
                else:
                    new_lines.append(line)

            with open(benchmark_table_path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines))
            print(f"  ✓ Đã tự động cập nhật kết quả vào {benchmark_table_path}!\n")
        except Exception as e:
            print(f"⚠️ Không thể cập nhật bảng benchmark: {e}")


if __name__ == "__main__":
    main()
