#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/train_bartpho_syllable_base.py
--------------------------------------------------------------------------------
Automated Pipeline to Fine-tune BARTpho-syllable-base on HCMC Flood ASTE V3 Splits:
1. Verifies dataset splits in AI/bartpho/data/.
2. Fine-tunes vinai/bartpho-syllable-base on specified GPU with FP16 AMP.
3. Automatically evaluates the best checkpoint on the independent test set.
4. Outputs benchmark report and runs inference test cases.
5. Updates master comparison table in AI/results/.
"""

import os
import sys
import json
import time
import argparse
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PYTHON_EXE = "/home/counting/anaconda3/envs/ryan_env/bin/python"

GPU_UUID_MAP = {
    0: "GPU-402b1880-531f-0736-be2e-03a8a229590b",
    2: "GPU-40888ad5-fe5d-17c8-a236-4b0fd1d97e6f",
    3: "GPU-17220462-c4da-32ae-f317-0c0e97d6e63e"
}


def main():
    parser = argparse.ArgumentParser(description="Train and Evaluate BARTpho-syllable-base for ASTE")
    parser.add_argument("--gpu", type=int, default=0, choices=[0, 2, 3], help="GPU index (0, 2, or 3)")
    parser.add_argument("--epochs", type=int, default=20, help="Number of epochs (default: 20)")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size (default: 16)")
    parser.add_argument("--learning_rate", type=float, default=4e-5, help="Learning rate (default: 4e-5)")
    parser.add_argument("--patience", type=int, default=6, help="Early stopping patience")
    parser.add_argument("--evaluate_after", action="store_true", default=True, help="Run evaluation after training")

    args = parser.parse_args()

    gpu_uuid = GPU_UUID_MAP[args.gpu]
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu_uuid

    print("=" * 80)
    print("🚀 RADI-NET GENERATIVE ASTE: HUẤN LUYỆN VÀ ĐÁNH GIÁ BARTPHO-SYLLABLE-BASE")
    print(f"  • GPU Target    : GPU {args.gpu} (UUID: {gpu_uuid})")
    print(f"  • Epochs        : {args.epochs}")
    print(f"  • Batch Size    : {args.batch_size}")
    print(f"  • Learning Rate : {args.learning_rate}")
    print(f"  • Python Env    : {PYTHON_EXE}")
    print("=" * 80)

    # 1. Check data preparation
    data_train = os.path.join(PROJECT_ROOT, "AI", "bartpho", "data", "train.json")
    if not os.path.exists(data_train):
        prep_script = os.path.join(PROJECT_ROOT, "AI", "bartpho", "finetune", "prepare_dataset.py")
        print("[*] Đang chuẩn bị dữ liệu từ data/processed/splits/...")
        subprocess.run([PYTHON_EXE, prep_script], check=True)

    # 2. Run Fine-Tuning
    train_script = os.path.join(PROJECT_ROOT, "AI", "bartpho", "syllable_base", "finetune", "train_generative_aste.py")
    output_dir = os.path.join(PROJECT_ROOT, "AI", "bartpho", "syllable_base", "finetune", "checkpoints", "best_aste_model")
    log_dir = os.path.join(PROJECT_ROOT, "AI", "bartpho", "syllable_base", "finetune")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "training.log")

    cmd_train = [
        PYTHON_EXE, "-u", train_script,
        "--model_name", "vinai/bartpho-syllable-base",
        "--epochs", str(args.epochs),
        "--batch_size", str(args.batch_size),
        "--learning_rate", str(args.learning_rate),
        "--patience", str(args.patience),
        "--output_dir", output_dir
    ]

    print(f"\n[*] Bắt đầu huấn luyện... Ghi log vào: {log_file}")
    with open(log_file, "w", encoding="utf-8") as f_log:
        proc = subprocess.Popen(
            cmd_train,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=os.environ
        )
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            f_log.write(line)
            f_log.flush()

        proc.wait()
        if proc.returncode != 0:
            print(f"[!] Lỗi khi huấn luyện (Return code: {proc.returncode}). Xem chi tiết tại: {log_file}")
            sys.exit(proc.returncode)

    print("\n✅ Huấn luyện hoàn tất thành công!")

    # 3. Evaluate Model on Test Split
    if args.evaluate_after:
        print("\n" + "=" * 80)
        print("📊 BẮT ĐẦU ĐÁNH GIÁ MÔ HÌNH TRÊN TẬP TEST ĐỘC LẬP")
        print("=" * 80)
        eval_script = os.path.join(PROJECT_ROOT, "AI", "bartpho", "syllable_base", "test", "evaluate_aste.py")
        report_file = os.path.join(PROJECT_ROOT, "AI", "bartpho", "syllable_base", "test", "benchmark_reports", "bartpho_syllable_test_report.json")
        cmd_eval = [
            PYTHON_EXE, "-u", eval_script,
            "--checkpoint_dir", output_dir,
            "--output_report", report_file
        ]
        subprocess.run(cmd_eval, check=True, env=os.environ)

        # 4. Quick Inference Demo
        infer_script = os.path.join(PROJECT_ROOT, "AI", "bartpho", "syllable_base", "test", "inference.py")
        cmd_infer = [PYTHON_EXE, "-u", infer_script]
        subprocess.run(cmd_infer, check=True, env=os.environ)

        # 5. Update Master Benchmark Table in AI/results
        print("\n" + "=" * 80)
        print("📈 CẬP NHẬT BẢNG SO SÁNH TỔNG HỢP TRONG AI/results/")
        print("=" * 80)
        update_script = os.path.join(PROJECT_ROOT, "scripts", "benchmark_heuristic_baseline.py")
        subprocess.run([PYTHON_EXE, "-u", update_script], check=True, env=os.environ)


if __name__ == "__main__":
    main()
