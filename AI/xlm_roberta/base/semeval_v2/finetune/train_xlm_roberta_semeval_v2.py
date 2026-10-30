#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI/xlm_roberta/base/semeval_v2/finetune/train_xlm_roberta_semeval_v2.py
--------------------------------------------------------------------------------
End-to-End Fine-Tuning Pipeline for XLM-RoBERTa Base on the SemEval v2 ASTE Format
(data/semeval_v2/{train.json, dev.json, test.json}).

Architecture:
  1. XLM-RoBERTa Contextual Sequence Encoder (xlm-roberta-base).
  2. Token BIO Sequence Tagger (Aspect & Opinion boundary extraction).
  3. Span-Pair Multi-Attribute Classifier (Polarity: NONE, NEG, POS, NEU).
  4. Direct SemEval v2 Span Alignment via Fast Tokenizer word_ids.

Features:
  - Process name masking (displays as 'python' in ps/top for user privacy).
  - Early stopping based on Validation Strict SemEval v2 Triplet F1.
  - Generates evaluations in exact SemEval v2 index format: [([a_idxs], [o_idxs], 'POL')].
"""

import os
import sys
import json
import math
import time
import argparse
import random
from typing import List, Dict, Tuple, Any, Optional

try:
    import setproctitle
    setproctitle.setproctitle("python")
except Exception:
    pass

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup
from tqdm import tqdm

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
DEFAULT_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "semeval_v2")
DEFAULT_OUTPUT_DIR = os.path.join(SEMEVAL_DIR, "finetune", "checkpoints", "best_model")

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

TAG2ID = {"O": 0, "B-ASP": 1, "I-ASP": 2, "B-OPN": 3, "I-OPN": 4}
ID2TAG = {v: k for k, v in TAG2ID.items()}

POLARITY2ID = {"NONE": 0, "NEG": 1, "POS": 2, "NEU": 3}
ID2POLARITY = {v: k for k, v in POLARITY2ID.items()}


class SemEvalXLMRobertaASTEDataset(Dataset):
    """Dataset reading SemEval v2 format and producing token-aligned spans for XLM-RoBERTa."""
    def __init__(self, data_path: str, tokenizer, max_len: int = 256):
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.samples = []

        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Missing dataset at: {data_path}")

        if data_path.endswith(".json"):
            with open(data_path, "r", encoding="utf-8") as f:
                raw_items = json.load(f)
        else:
            raw_items = []
            with open(data_path, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split("####")
                    sent = parts[0].strip()
                    tgt = parts[1].strip() if len(parts) > 1 else "[]"
                    import ast
                    raw_items.append({
                        "id": f"sample_{idx}",
                        "tokens": sent.split(),
                        "semeval_triplets": ast.literal_eval(tgt)
                    })

        for item in raw_items:
            words = item.get("tokens") or item.get("sentence", "").split()
            if not words:
                continue

            encoding = self.tokenizer(
                words,
                is_split_into_words=True,
                max_length=self.max_len,
                padding=False,
                truncation=True,
                return_tensors=None
            )

            input_ids = encoding["input_ids"]
            attention_mask = encoding["attention_mask"]
            word_ids = encoding.word_ids()

            # Map word index -> [subtoken start, subtoken end)
            w2tok = {}
            tok2word = {}
            for tok_idx, w_idx in enumerate(word_ids):
                if w_idx is not None:
                    tok2word[tok_idx] = w_idx
                    if w_idx not in w2tok:
                        w2tok[w_idx] = []
                    w2tok[w_idx].append(tok_idx)

            # Build token-level BIO tags
            bio_tags = [TAG2ID["O"]] * len(input_ids)
            gold_pairs = []

            for triplet in item.get("semeval_triplets", []):
                aspect_word_indices, opinion_word_indices, pol = triplet
                pol_str = pol.upper() if isinstance(pol, str) else "NEG"

                asp_tok_indices = [t for w in aspect_word_indices for t in w2tok.get(w, [])]
                opn_tok_indices = [t for w in opinion_word_indices for t in w2tok.get(w, [])]

                if not asp_tok_indices or not opn_tok_indices:
                    continue

                # BIO tagging for Aspect
                bio_tags[asp_tok_indices[0]] = TAG2ID["B-ASP"]
                for t in asp_tok_indices[1:]:
                    bio_tags[t] = TAG2ID["I-ASP"]

                # BIO tagging for Opinion
                bio_tags[opn_tok_indices[0]] = TAG2ID["B-OPN"]
                for t in opn_tok_indices[1:]:
                    bio_tags[t] = TAG2ID["I-OPN"]

                gold_pairs.append({
                    "aspect_tok_span": (min(asp_tok_indices), max(asp_tok_indices) + 1),
                    "opinion_tok_span": (min(opn_tok_indices), max(opn_tok_indices) + 1),
                    "polarity": POLARITY2ID.get(pol_str, POLARITY2ID["NEG"]),
                    "aspect_word_indices": aspect_word_indices,
                    "opinion_word_indices": opinion_word_indices,
                    "polarity_str": pol_str
                })

            self.samples.append({
                "id": item.get("id", ""),
                "words": words,
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "bio_tags": bio_tags,
                "gold_pairs": gold_pairs,
                "w2tok": w2tok,
                "tok2word": tok2word,
                "semeval_triplets": item.get("semeval_triplets", [])
            })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


def semeval_collate_fn(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    max_len = max(len(s["input_ids"]) for s in batch)
    B = len(batch)

    input_ids = torch.zeros((B, max_len), dtype=torch.long)
    attention_mask = torch.zeros((B, max_len), dtype=torch.long)
    bio_tags = torch.full((B, max_len), fill_value=TAG2ID["O"], dtype=torch.long)

    for i, s in enumerate(batch):
        L = len(s["input_ids"])
        input_ids[i, :L] = torch.tensor(s["input_ids"], dtype=torch.long)
        attention_mask[i, :L] = torch.tensor(s["attention_mask"], dtype=torch.long)
        bio_tags[i, :L] = torch.tensor(s["bio_tags"], dtype=torch.long)

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "bio_tags": bio_tags,
        "raw_batch": batch
    }


class XLMRobertaForSemEvalASTE(nn.Module):
    """Joint Token Tagger + Span-Pair Representation for XLM-RoBERTa ASTE."""
    def __init__(self, model_name: str = "xlm-roberta-base", dropout_rate: float = 0.15):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden_size = self.encoder.config.hidden_size

        self.dropout = nn.Dropout(dropout_rate)
        self.tag_classifier = nn.Linear(hidden_size, len(TAG2ID))

        # Span-pair representation: [v_asp, v_opn, v_asp * v_opn, |v_asp - v_opn|, v_cls] -> 5 * hidden_size
        pair_feature_dim = 5 * hidden_size
        self.pair_dense = nn.Sequential(
            nn.Linear(pair_feature_dim, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout_rate)
        )
        self.polarity_head = nn.Linear(hidden_size, len(POLARITY2ID))

        # Loss functions with class weighting for imbalanced polarities
        self.loss_bio = nn.CrossEntropyLoss()
        weight_pol = torch.tensor([0.2, 1.0, 1.2, 1.8], dtype=torch.float)
        self.loss_pol = nn.CrossEntropyLoss(weight=weight_pol)

    def extract_span_repr(self, sequence_rep: torch.Tensor, start_idx: int, end_idx: int) -> torch.Tensor:
        start_idx = max(0, min(start_idx, sequence_rep.size(0) - 1))
        end_idx = max(start_idx + 1, min(end_idx, sequence_rep.size(0)))
        span_slice = sequence_rep[start_idx:end_idx]
        return span_slice.mean(dim=0)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        bio_tags: Optional[torch.Tensor] = None,
        raw_batch: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, torch.Tensor]:
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        sequence_output = outputs.last_hidden_state  # [B, L, H]
        cls_output = sequence_output[:, 0, :]        # [B, H]

        bio_logits = self.tag_classifier(self.dropout(sequence_output))
        results = {"bio_logits": bio_logits}

        if bio_tags is not None and raw_batch is not None:
            loss_span = self.loss_bio(bio_logits.view(-1, len(TAG2ID)), bio_tags.view(-1))

            pair_feats = []
            pair_polarities = []
            device = input_ids.device
            self.loss_pol.weight = self.loss_pol.weight.to(device)

            for b_idx, sample in enumerate(raw_batch):
                seq_rep = sequence_output[b_idx]
                cls_rep = cls_output[b_idx]
                gold_pairs = sample["gold_pairs"]

                # Positive gold pairs
                for gp in gold_pairs:
                    as_i, ae_i = gp["aspect_tok_span"]
                    os_i, oe_i = gp["opinion_tok_span"]
                    v_asp = self.extract_span_repr(seq_rep, as_i, ae_i)
                    v_opn = self.extract_span_repr(seq_rep, os_i, oe_i)
                    feat = torch.cat([v_asp, v_opn, v_asp * v_opn, torch.abs(v_asp - v_opn), cls_rep], dim=-1)
                    pair_feats.append(feat)
                    pair_polarities.append(gp["polarity"])

                # Negative candidate pairs (cross-combinations of non-paired spans)
                all_asps = list({gp["aspect_tok_span"] for gp in gold_pairs})
                all_opns = list({gp["opinion_tok_span"] for gp in gold_pairs})
                positive_combos = {(gp["aspect_tok_span"], gp["opinion_tok_span"]) for gp in gold_pairs}

                for a_sp in all_asps:
                    for o_sp in all_opns:
                        if (a_sp, o_sp) not in positive_combos:
                            v_asp = self.extract_span_repr(seq_rep, a_sp[0], a_sp[1])
                            v_opn = self.extract_span_repr(seq_rep, o_sp[0], o_sp[1])
                            feat = torch.cat([v_asp, v_opn, v_asp * v_opn, torch.abs(v_asp - v_opn), cls_rep], dim=-1)
                            pair_feats.append(feat)
                            pair_polarities.append(POLARITY2ID["NONE"])

            if pair_feats:
                pair_feats_t = torch.stack(pair_feats, dim=0)
                pair_h = self.pair_dense(pair_feats_t)
                pol_logits = self.polarity_head(pair_h)
                labels_pol = torch.tensor(pair_polarities, dtype=torch.long, device=device)
                loss_pol = self.loss_pol(pol_logits, labels_pol)
                results["loss"] = loss_span + 1.5 * loss_pol
            else:
                results["loss"] = loss_span

        return results

    def predict_semeval_triplets(
        self,
        sequence_output: torch.Tensor,
        cls_output: torch.Tensor,
        predicted_tags: List[str],
        tok2word: Dict[int, int]
    ) -> List[Tuple[Tuple[int, ...], Tuple[int, ...], str]]:
        # Extract token spans from BIO
        asp_spans = []
        opn_spans = []

        curr_asp = []
        curr_opn = []

        for idx, tag in enumerate(predicted_tags):
            if tag == "B-ASP":
                if curr_asp:
                    asp_spans.append((curr_asp[0], curr_asp[-1] + 1))
                curr_asp = [idx]
            elif tag == "I-ASP" and curr_asp:
                curr_asp.append(idx)
            else:
                if curr_asp:
                    asp_spans.append((curr_asp[0], curr_asp[-1] + 1))
                    curr_asp = []

            if tag == "B-OPN":
                if curr_opn:
                    opn_spans.append((curr_opn[0], curr_opn[-1] + 1))
                curr_opn = [idx]
            elif tag == "I-OPN" and curr_opn:
                curr_opn.append(idx)
            else:
                if curr_opn:
                    opn_spans.append((curr_opn[0], curr_opn[-1] + 1))
                    curr_opn = []

        if curr_asp:
            asp_spans.append((curr_asp[0], curr_asp[-1] + 1))
        if curr_opn:
            opn_spans.append((curr_opn[0], curr_opn[-1] + 1))

        if not asp_spans or not opn_spans:
            return []

        # Candidate span pairs
        pair_feats = []
        pair_meta = []

        for a_s, a_e in asp_spans:
            v_asp = self.extract_span_repr(sequence_output, a_s, a_e)
            a_w_idxs = sorted(list({tok2word[t] for t in range(a_s, a_e) if t in tok2word}))
            if not a_w_idxs:
                continue

            for o_s, o_e in opn_spans:
                v_opn = self.extract_span_repr(sequence_output, o_s, o_e)
                o_w_idxs = sorted(list({tok2word[t] for t in range(o_s, o_e) if t in tok2word}))
                if not o_w_idxs:
                    continue

                feat = torch.cat([v_asp, v_opn, v_asp * v_opn, torch.abs(v_asp - v_opn), cls_output], dim=-1)
                pair_feats.append(feat)
                pair_meta.append((tuple(a_w_idxs), tuple(o_w_idxs)))

        if not pair_feats:
            return []

        pair_feats_t = torch.stack(pair_feats, dim=0)
        with torch.no_grad():
            pair_h = self.pair_dense(pair_feats_t)
            logits = self.polarity_head(pair_h)
            probs = torch.softmax(logits, dim=-1)
            preds = torch.argmax(probs, dim=-1).cpu().tolist()

        predicted_triplets = []
        for (a_w_tuple, o_w_tuple), pred_id in zip(pair_meta, preds):
            pol_label = ID2POLARITY[pred_id]
            if pol_label != "NONE":
                predicted_triplets.append((a_w_tuple, o_w_tuple, pol_label))

        return predicted_triplets


def evaluate_val_triplet_f1(model, val_loader, device: torch.device) -> Dict[str, float]:
    model.eval()
    n_gold = 0
    n_pred = 0
    n_correct = 0
    total_val_loss = 0.0
    steps = 0

    with torch.no_grad():
        for batch in val_loader:
            in_ids = batch["input_ids"].to(device, non_blocking=True)
            att_m = batch["attention_mask"].to(device, non_blocking=True)
            bio_tags = batch["bio_tags"].to(device, non_blocking=True)
            raw_batch = batch["raw_batch"]

            with torch.amp.autocast('cuda', enabled=device.type == "cuda"):
                outputs = model(input_ids=in_ids, attention_mask=att_m, bio_tags=bio_tags, raw_batch=raw_batch)
                loss = outputs["loss"]
            total_val_loss += loss.item()
            steps += 1

            bio_logits = outputs["bio_logits"]
            pred_tags_batch = torch.argmax(bio_logits, dim=-1).cpu().tolist()

            encoder_out = model.encoder(input_ids=in_ids, attention_mask=att_m).last_hidden_state
            cls_out = encoder_out[:, 0, :]

            for b_idx, sample in enumerate(raw_batch):
                seq_len = len(sample["input_ids"])
                predicted_tags = [ID2TAG[t] for t in pred_tags_batch[b_idx][:seq_len]]
                pred_triplets = model.predict_semeval_triplets(
                    sequence_output=encoder_out[b_idx],
                    cls_output=cls_out[b_idx],
                    predicted_tags=predicted_tags,
                    tok2word=sample["tok2word"]
                )

                gold_triplets = [
                    (tuple(sorted(t[0])), tuple(sorted(t[1])), t[2].upper())
                    for t in sample.get("semeval_triplets", [])
                ]

                gold_set = set(gold_triplets)
                pred_set = set(pred_triplets)

                n_gold += len(gold_set)
                n_pred += len(pred_set)
                n_correct += len(gold_set.intersection(pred_set))

    p = (n_correct / n_pred * 100) if n_pred > 0 else 0.0
    r = (n_correct / n_gold * 100) if n_gold > 0 else 0.0
    f1 = (2 * p * r / (p + r)) if (p + r) > 0 else 0.0
    avg_loss = total_val_loss / max(1, steps)

    return {
        "val_loss": round(avg_loss, 4),
        "val_p": round(p, 2),
        "val_r": round(r, 2),
        "val_f1": round(f1, 2)
    }


def train(args):
    seed_everything(RANDOM_SEED)

    device = torch.device(args.device if (torch.cuda.is_available() and "cuda" in args.device) else ("cuda" if torch.cuda.is_available() else "cpu"))
    gpu_name = torch.cuda.get_device_name(device) if device.type == "cuda" else "CPU"

    print("=" * 80)
    print("🚀 HUẤN LUYỆN XLM-ROBERTA BASE TRÊN ĐỊNH DẠNG SEMEVAL V2")
    print(f"  • Model Backbone  : {args.model_name}")
    print(f"  • Thiết bị        : {device} ({gpu_name})")
    print(f"  • Data Directory  : {args.data_dir}")
    print(f"  • Checkpoint Dir  : {args.output_dir}")
    print(f"  • Batch Size      : {args.batch_size}")
    print(f"  • Learning Rate   : {args.learning_rate}")
    print(f"  • Weight Decay    : {args.weight_decay}")
    print(f"  • Số Epochs tối đa: {args.epochs}")
    print(f"  • Early Stopping  : Patience = {args.patience} epochs")
    print("=" * 80)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    train_path = os.path.join(args.data_dir, "train.json")
    val_path = os.path.join(args.data_dir, "dev.json")

    print("\n⏳ Đang tải và tiền xử lý datasets...")
    train_ds = SemEvalXLMRobertaASTEDataset(train_path, tokenizer, max_len=args.max_len)
    val_ds = SemEvalXLMRobertaASTEDataset(val_path, tokenizer, max_len=args.max_len)
    print(f"  ✓ Train Set: {len(train_ds):,} mẫu")
    print(f"  ✓ Dev Set  : {len(val_ds):,} mẫu\n")

    g = torch.Generator()
    g.manual_seed(RANDOM_SEED)

    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        shuffle=True,
        generator=g,
        worker_init_fn=seed_worker,
        num_workers=2,
        pin_memory=True,
        collate_fn=semeval_collate_fn
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=2,
        pin_memory=True,
        collate_fn=semeval_collate_fn
    )

    model = XLMRobertaForSemEvalASTE(model_name=args.model_name, dropout_rate=args.dropout).to(device)

    # Differential learning rate
    optimizer_grouped_parameters = [
        {"params": [p for n, p in model.encoder.named_parameters() if p.requires_grad], "lr": args.learning_rate},
        {"params": [p for n, p in model.tag_classifier.named_parameters() if p.requires_grad], "lr": 1e-4},
        {"params": [p for n, p in model.pair_dense.named_parameters() if p.requires_grad], "lr": 1e-4},
        {"params": [p for n, p in model.polarity_head.named_parameters() if p.requires_grad], "lr": 1e-4},
    ]

    optimizer = torch.optim.AdamW(optimizer_grouped_parameters, weight_decay=args.weight_decay)
    total_steps = len(train_loader) * args.epochs
    warmup_steps = int(total_steps * args.warmup_ratio)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps)

    scaler = torch.amp.GradScaler('cuda', enabled=device.type == "cuda")

    best_val_f1 = -1.0
    best_val_loss = float("inf")
    best_epoch = 0
    patience_counter = 0
    history = []

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        model.train()
        train_loss = 0.0
        step_c = 0

        pbar = tqdm(train_loader, desc=f"Epoch {epoch}/{args.epochs}", leave=False)
        for batch in pbar:
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

            train_loss += loss.item()
            step_c += 1

        avg_train_loss = train_loss / max(1, step_c)
        val_metrics = evaluate_val_triplet_f1(model=model, val_loader=val_loader, device=device)
        dur = time.time() - t0

        val_loss = val_metrics["val_loss"]
        val_f1 = val_metrics["val_f1"]
        val_p = val_metrics["val_p"]
        val_r = val_metrics["val_r"]

        is_best = (val_f1 > best_val_f1) or (val_f1 == best_val_f1 and val_loss < best_val_loss)
        star = "⭐ [BEST F1]" if is_best else ""

        print(f"Epoch {epoch:02d}/{args.epochs:02d} [{dur:.1f}s] - "
              f"Train Loss: {avg_train_loss:.4f} | Val Loss: {val_loss:.4f} | "
              f"Val Triplet F1: {val_f1:.2f}% (P: {val_p:.2f}%, R: {val_r:.2f}%) {star}")
        sys.stdout.flush()

        history.append({
            "epoch": epoch,
            "train_loss": round(avg_train_loss, 4),
            "val_loss": val_loss,
            "val_triplet_f1": val_f1,
            "val_triplet_p": val_p,
            "val_triplet_r": val_r,
            "duration_sec": round(dur, 1)
        })

        if is_best:
            best_val_f1 = val_f1
            best_val_loss = val_loss
            best_epoch = epoch
            patience_counter = 0
            os.makedirs(args.output_dir, exist_ok=True)
            torch.save(model.state_dict(), os.path.join(args.output_dir, "xlm_roberta_aste_weights.pt"))
            tokenizer.save_pretrained(args.output_dir)
        else:
            patience_counter += 1
            if patience_counter >= args.patience:
                print(f"\n" + "=" * 80)
                print(f"🛑 EARLY STOPPING KÍCH HOẠT: Không có cải thiện Val F1 trong {args.patience} epochs liên tiếp.")
                print(f"  • Huấn luyện dừng lại sớm tại Epoch {epoch}/{args.epochs}.")
                print(f"  • Checkpoint tốt nhất đã được lưu tại Epoch {best_epoch} (Val F1: {best_val_f1:.2f}%).")
                print("=" * 80)
                break

    # Save training history
    with open(os.path.join(args.output_dir, "training_history.json"), "w", encoding="utf-8") as f:
        json.dump({
            "model_name": args.model_name,
            "best_epoch": best_epoch,
            "best_val_triplet_f1": best_val_f1,
            "best_val_loss": best_val_loss,
            "history": history
        }, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("✅ HOÀN TẤT HUẤN LUYỆN XLM-ROBERTA BASE SEMEVAL V2!")
    print(f"  • Best Checkpoint : {args.output_dir}")
    print(f"  • Best Epoch      : {best_epoch}")
    print(f"  • Best Val F1     : {best_val_f1:.2f}%")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Fine-tune XLM-RoBERTa Base on SemEval v2 ASTE")
    parser.add_argument("--model_name", type=str, default="xlm-roberta-base")
    parser.add_argument("--data_dir", type=str, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output_dir", type=str, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max_len", type=int, default=256)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--learning_rate", type=float, default=2.5e-5)
    parser.add_argument("--weight_decay", type=float, default=0.01)
    parser.add_argument("--dropout", type=float, default=0.15)
    parser.add_argument("--warmup_ratio", type=float, default=0.1)
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--device", type=str, default="cuda")
    args = parser.parse_args()

    train(args)


if __name__ == "__main__":
    main()
