#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI/xlm_v/base/semeval_v2/finetune/train_xlm_v_semeval_v2.py
--------------------------------------------------------------------------------
End-to-End Fine-Tuning Pipeline for XLM-V Base on the SemEval v2 ASTE Format
(data/semeval_v2/{train.json, dev.json, test.json}).

Architecture:
  1. XLM-V Contextual Sequence Encoder (facebook/xlm-v-base, 1M Vocab).
  2. Token BIO Sequence Tagger (Aspect & Opinion boundary extraction).
  3. Span-Pair Multi-Attribute Classifier (Polarity: NONE, NEG, POS, NEU).
  4. Direct SemEval v2 Span Alignment via Fast Tokenizer word_ids.

Features:
  - Process name masking (displays as 'python' in ps/top for privacy).
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


class SemEvalXLMVASTEDataset(Dataset):
    """Dataset reading SemEval v2 format and producing token-aligned spans for XLM-V."""
    def __init__(self, data_path: str, tokenizer, max_len: int = 160):
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
                        "sentence": sent,
                        "semeval_triplets": ast.literal_eval(tgt) if tgt != "[]" else []
                    })

        for item in raw_items:
            tokens = item.get("tokens", item.get("sentence", "").split())
            if not tokens:
                continue

            semeval_triplets = item.get("semeval_triplets", [])
            self.samples.append({
                "id": item.get("id", ""),
                "tokens": tokens,
                "sentence": item.get("sentence", " ".join(tokens)),
                "semeval_triplets": semeval_triplets
            })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        item = self.samples[idx]
        words = item["tokens"]

        encoding = self.tokenizer(
            words,
            is_split_into_words=True,
            truncation=True,
            max_length=self.max_len,
            padding=False,
            return_attention_mask=True
        )

        input_ids = encoding["input_ids"]
        word_ids = encoding.word_ids()
        seq_len = len(input_ids)

        word2tok = {}
        tok2word = {}
        for t_idx, w_id in enumerate(word_ids):
            if w_id is not None:
                word2tok.setdefault(w_id, []).append(t_idx)
                tok2word[t_idx] = w_id

        bio_tags = [TAG2ID["O"]] * seq_len
        gold_pairs = []

        for (a_idxs, o_idxs, pol) in item["semeval_triplets"]:
            if not a_idxs or not o_idxs:
                continue

            # Map word indices to token spans
            a_toks = [t for w in a_idxs if w in word2tok for t in word2tok[w]]
            o_toks = [t for w in o_idxs if w in word2tok for t in word2tok[w]]

            if not a_toks or not o_toks:
                continue

            as_tok, ae_tok = min(a_toks), max(a_toks)
            os_tok, oe_tok = min(o_toks), max(o_toks)

            # Assign BIO tags
            bio_tags[as_tok] = TAG2ID["B-ASP"]
            for k in range(as_tok + 1, ae_tok + 1):
                bio_tags[k] = TAG2ID["I-ASP"]

            bio_tags[os_tok] = TAG2ID["B-OPN"]
            for k in range(os_tok + 1, oe_tok + 1):
                bio_tags[k] = TAG2ID["I-OPN"]

            pol_id = POLARITY2ID.get(pol.upper(), POLARITY2ID["NEU"])
            gold_pairs.append({
                "aspect_tok_span": (as_tok, ae_tok),
                "opinion_tok_span": (os_tok, oe_tok),
                "polarity": pol_id,
                "gold_semeval_triplet": (tuple(sorted(a_idxs)), tuple(sorted(o_idxs)), pol.upper())
            })

        return {
            "id": item["id"],
            "tokens": words,
            "semeval_triplets": item.get("semeval_triplets", []),
            "word2tok": word2tok,
            "tok2word": tok2word,
            "input_ids": input_ids,
            "bio_tags": bio_tags,
            "gold_pairs": gold_pairs,
            "seq_len": seq_len
        }


def semeval_collate_fn(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    max_len = max(b["seq_len"] for b in batch)
    batch_size = len(batch)

    input_ids = torch.zeros((batch_size, max_len), dtype=torch.long)
    attention_mask = torch.zeros((batch_size, max_len), dtype=torch.long)
    bio_tags = torch.full((batch_size, max_len), -100, dtype=torch.long)

    for i, b in enumerate(batch):
        slen = b["seq_len"]
        input_ids[i, :slen] = torch.tensor(b["input_ids"], dtype=torch.long)
        attention_mask[i, :slen] = 1
        bio_tags[i, :slen] = torch.tensor(b["bio_tags"], dtype=torch.long)

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "bio_tags": bio_tags,
        "raw_batch": batch
    }


class XLMVForSemEvalASTE(nn.Module):
    """Joint Token Tagger + Span-Pair Polarity Classifier for XLM-V ASTE."""
    def __init__(self, model_name: str = "facebook/xlm-v-base", dropout_rate: float = 0.15, freeze_embeddings: bool = True):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        if freeze_embeddings:
            # XLM-V has 1-Million token vocabulary (~2.77GB embedding tensor).
            # Freezing word embeddings avoids 6GB+ AdamW state allocation, fitting cleanly in 11GB VRAM.
            if hasattr(self.encoder, "embeddings") and hasattr(self.encoder.embeddings, "word_embeddings"):
                self.encoder.embeddings.word_embeddings.weight.requires_grad = False

        hidden_size = self.encoder.config.hidden_size  # 768

        self.dropout = nn.Dropout(dropout_rate)
        self.tag_classifier = nn.Linear(hidden_size, len(TAG2ID))

        pair_dim = hidden_size * 5
        self.pair_dense = nn.Sequential(
            nn.Linear(pair_dim, hidden_size),
            nn.GELU(),
            nn.Dropout(dropout_rate)
        )
        self.polarity_head = nn.Linear(hidden_size, len(POLARITY2ID))

        self.loss_bio = nn.CrossEntropyLoss(ignore_index=-100)
        pol_weights = torch.tensor([1.0, 1.2, 1.8, 1.8])  # NONE, NEG, POS, NEU
        self.loss_pol = nn.CrossEntropyLoss(weight=pol_weights)

    def extract_span_repr(self, sequence_output: torch.Tensor, start_idx: int, end_idx: int) -> torch.Tensor:
        if start_idx == end_idx:
            return sequence_output[start_idx]
        return sequence_output[start_idx: end_idx + 1].mean(dim=0)

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

                # Negative candidate pairs
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
        """Predicts aspect & opinion spans and maps tokens back to word indices."""
        aspect_spans = []
        opinion_spans = []

        curr_asp = None
        curr_opn = None

        for idx, tag in enumerate(predicted_tags):
            if tag == "B-ASP":
                if curr_asp is not None and (curr_asp[1] - curr_asp[0] + 1) <= 12:
                    aspect_spans.append(curr_asp)
                curr_asp = [idx, idx]
            elif tag == "I-ASP" and curr_asp is not None:
                curr_asp[1] = idx
            else:
                if curr_asp is not None:
                    if (curr_asp[1] - curr_asp[0] + 1) <= 12:
                        aspect_spans.append(curr_asp)
                    curr_asp = None

            if tag == "B-OPN":
                if curr_opn is not None and (curr_opn[1] - curr_opn[0] + 1) <= 16:
                    opinion_spans.append(curr_opn)
                curr_opn = [idx, idx]
            elif tag == "I-OPN" and curr_opn is not None:
                curr_opn[1] = idx
            else:
                if curr_opn is not None:
                    if (curr_opn[1] - curr_opn[0] + 1) <= 16:
                        opinion_spans.append(curr_opn)
                    curr_opn = None

        if curr_asp is not None and (curr_asp[1] - curr_asp[0] + 1) <= 12:
            aspect_spans.append(curr_asp)
        if curr_opn is not None and (curr_opn[1] - curr_opn[0] + 1) <= 16:
            opinion_spans.append(curr_opn)

        if not aspect_spans or not opinion_spans:
            return []

        candidates = []
        pair_feats = []
        for as_i, ae_i in aspect_spans:
            v_asp = self.extract_span_repr(sequence_output, as_i, ae_i)
            for os_i, oe_i in opinion_spans:
                v_opn = self.extract_span_repr(sequence_output, os_i, oe_i)
                feat = torch.cat([v_asp, v_opn, v_asp * v_opn, torch.abs(v_asp - v_opn), cls_output], dim=-1)
                pair_feats.append(feat)
                candidates.append(((as_i, ae_i), (os_i, oe_i)))

        pair_feats_t = torch.stack(pair_feats, dim=0)
        pair_h = self.pair_dense(pair_feats_t)
        pol_logits = self.polarity_head(pair_h)
        pred_pols = torch.argmax(pol_logits, dim=-1).cpu().tolist()

        predicted_triplets = []
        for i, (asp_span, opn_span) in enumerate(candidates):
            pol_id = pred_pols[i]
            if pol_id == POLARITY2ID["NONE"]:
                continue
            pol_str = ID2POLARITY[pol_id]

            # Map token spans to word indices
            a_words = sorted(list({tok2word[t] for t in range(asp_span[0], asp_span[1] + 1) if t in tok2word}))
            o_words = sorted(list({tok2word[t] for t in range(opn_span[0], opn_span[1] + 1) if t in tok2word}))

            if a_words and o_words:
                predicted_triplets.append((tuple(a_words), tuple(o_words), pol_str))

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
                seq_len = sample["seq_len"]
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
    print("🚀 HUẤN LUYỆN XLM-V BASE TRÊN ĐỊNH DẠNG SEMEVAL V2")
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

    train_file = os.path.join(args.data_dir, "train.json")
    val_file = os.path.join(args.data_dir, "dev.json") if os.path.exists(os.path.join(args.data_dir, "dev.json")) else os.path.join(args.data_dir, "val.json")

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    train_ds = SemEvalXLMVASTEDataset(train_file, tokenizer, max_len=args.max_len)
    val_ds = SemEvalXLMVASTEDataset(val_file, tokenizer, max_len=args.max_len)

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

    model = XLMVForSemEvalASTE(model_name=args.model_name, dropout_rate=args.dropout).to(device)

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
            torch.save(model.state_dict(), os.path.join(args.output_dir, "xlm_v_aste_weights.pt"))
            tokenizer.save_pretrained(args.output_dir)
        else:
            patience_counter += 1
            if args.patience > 0 and patience_counter >= args.patience:
                print("\n" + "=" * 80)
                print(f"🛑 EARLY STOPPING KÍCH HOẠT: Không có cải thiện Val F1 trong {args.patience} epochs liên tiếp.")
                print(f"  • Huấn luyện dừng lại sớm tại Epoch {epoch:02d}/{args.epochs:02d}.")
                print(f"  • Checkpoint tốt nhất đã được lưu tại Epoch {best_epoch:02d} (Val F1: {best_val_f1:.2f}%).")
                print("=" * 80)
                sys.stdout.flush()
                break

    meta = {
        "model_name": args.model_name,
        "format": "semeval_v2",
        "random_seed": RANDOM_SEED,
        "selection_criterion": "validation_strict_semeval_triplet_f1",
        "best_epoch": best_epoch,
        "best_val_triplet_f1": best_val_f1,
        "best_val_loss": best_val_loss,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "total_epochs": args.epochs,
        "early_stopping_patience": args.patience,
        "history": history
    }
    with open(os.path.join(args.output_dir, "training_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("✅ HOÀN TẤT HUẤN LUYỆN XLM-V BASE SEMEVAL V2!")
    print(f"  • Best Checkpoint : {args.output_dir}")
    print(f"  • Best Epoch      : {best_epoch}")
    print(f"  • Best Val F1     : {best_val_f1:.2f}%")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="facebook/xlm-v-base")
    parser.add_argument("--data_dir", type=str, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output_dir", type=str, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--learning_rate", type=float, default=2e-5)
    parser.add_argument("--weight_decay", type=float, default=0.01)
    parser.add_argument("--dropout", type=float, default=0.15)
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--patience", type=int, default=5, help="Early stopping patience")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--warmup_ratio", type=float, default=0.1)
    parser.add_argument("--max_len", type=int, default=160)

    args = parser.parse_args()
    train(args)
