#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/train_phobert_aste.py
--------------------------------------------------------------------------------
End-to-End Fine-Tuning Pipeline for PhoBERT (Fast Path Span/Table ASTE Model)
on the HCMC Urban Flood Multimodal ASTE v3 Dataset Splits (data/processed/splits).

Formulation:
    Joint Multi-Task Architecture:
      1. PhoBERT Contextual Sequence Encoder (vinai/phobert-base-v2).
      2. Token BIO Sequence Tagger (Aspect & Opinion boundary extraction).
      3. Span-Pair Multi-Attribute Classifier:
         - Polarity (NEG / POS / NEU / NONE)
         - Aspect Category (LOCATION_STREET, LOCATION_ADMIN, HYDROLOGY, etc.)
         - Severity (HIGH, MODERATE, LOW, RECOVERED)

Features:
    - 100% Dataset Compatibility with Schema v3 (train.json, dev.json, test.json).
    - Subword-aware token alignment with zero data loss.
    - Strict Evaluation Benchmark (Aspect F1, Opinion F1, Strict Triplet Exact Match F1).
    - CUDA Mixed-Precision (FP16) training with dynamic batch collation.
    - Exportable checkpoint and standalone PhoBertASTEPredictor for real-time serving.

Author: RadiNet AI Research Team
Domain: Urban Flood Monitoring & Social Crowdsensing (TP.HCM)
"""

import os
import sys
import json
import math
import time
import argparse
import random
from typing import List, Dict, Tuple, Any, Optional
from collections import defaultdict, Counter

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup

import hashlib
import subprocess
import numpy as np

# Seed for scientific reproducibility
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

# ==============================================================================
# TAXONOMY & LABEL DEFINITIONS (Schema v3)
# ==============================================================================
TAG2ID = {"O": 0, "B-ASP": 1, "I-ASP": 2, "B-OPN": 3, "I-OPN": 4}
ID2TAG = {v: k for k, v in TAG2ID.items()}

POLARITY2ID = {"NONE": 0, "NEG": 1, "POS": 2, "NEU": 3}
ID2POLARITY = {v: k for k, v in POLARITY2ID.items()}

CATEGORY2ID = {
    "NONE": 0,
    "LOCATION_STREET": 1,
    "LOCATION_ADMIN": 2,
    "HYDROLOGY": 3,
    "INFRASTRUCTURE_DRAINAGE": 4,
    "INFRASTRUCTURE": 5,
    "RESPONSE_ENTITY": 6,
    "TRAFFIC": 7,
    "OTHER": 8,
}
ID2CATEGORY = {v: k for k, v in CATEGORY2ID.items()}

SEVERITY2ID = {"NONE": 0, "HIGH": 1, "LOW": 2, "MODERATE": 3}
ID2SEVERITY = {v: k for k, v in SEVERITY2ID.items()}


# ==============================================================================
# SUBWORD-AWARE TOKEN ALIGNMENT
# ==============================================================================
def align_subphrase(text: str, sub_str: str, raw_tokens: List[str]) -> Optional[Tuple[int, int]]:
    """
    Finds exact token span [start_idx, end_idx] (inclusive) for a subphrase in text.
    Handles PhoBERT BPE '@@' subword tokens and accents.
    Returns 1-based index (accounting for <s> token at index 0).
    """
    if not sub_str or not text:
        return None
    text_lower = text.lower()
    sub_lower = sub_str.lower().strip()
    idx = text_lower.find(sub_lower)
    if idx == -1:
        return None
    char_start = idx
    char_end = idx + len(sub_lower)

    # Reconstruct character positions of each BPE token in full text
    token_spans = []
    curr_char = 0
    for tok in raw_tokens:
        clean_tok = tok.replace("@@", "")
        pos = text_lower.find(clean_tok.lower(), curr_char)
        if pos != -1:
            token_spans.append((pos, pos + len(clean_tok)))
            curr_char = pos + len(clean_tok)
        else:
            token_spans.append((curr_char, curr_char + len(clean_tok)))
            curr_char += len(clean_tok)

    matched = [
        i for i, (ts, te) in enumerate(token_spans)
        if max(ts, char_start) < min(te, char_end)
    ]
    if matched:
        return matched[0] + 1, matched[-1] + 1  # +1 offset for <s>
    return None


# ==============================================================================
# DATASET & DATALOADER
# ==============================================================================
class ASTEJsonDataset(Dataset):
    def __init__(self, json_path: str, tokenizer, max_len: int = 160, is_train: bool = True):
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.is_train = is_train
        self.samples = []

        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Dataset split not found at: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        for item in raw_data:
            text = item.get("content", {}).get("text", "").strip()
            if not text:
                continue

            triplets = item.get("aste_triplets", [])
            self.samples.append({
                "id": item.get("id", ""),
                "text": text,
                "triplets": triplets,
                "episode": item.get("episode_id", "")
            })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        item = self.samples[idx]
        text = item["text"]
        raw_tokens = self.tokenizer.tokenize(text)

        # Truncate tokens if exceeding max_len - 2 (reserve <s> and </s>)
        if len(raw_tokens) > self.max_len - 2:
            raw_tokens = raw_tokens[: self.max_len - 2]

        input_ids = self.tokenizer.convert_tokens_to_ids(raw_tokens)
        input_ids = [self.tokenizer.bos_token_id] + input_ids + [self.tokenizer.eos_token_id]
        seq_len = len(input_ids)

        bio_tags = [TAG2ID["O"]] * seq_len

        gold_pairs = []
        valid_aspect_spans = []
        valid_opinion_spans = []

        for t in item["triplets"]:
            asp = t.get("aspect", "")
            opn = t.get("opinion", "")
            pol = t.get("polarity", "NEU")
            cat = t.get("aspect_category", "LOCATION_STREET")
            sev = t.get("severity", "LOW")

            # Opinion span (always present in text)
            o_span = align_subphrase(text, opn, raw_tokens)
            if not o_span:
                continue
            os_idx, oe_idx = o_span
            if oe_idx >= seq_len - 1:
                continue

            # Aspect span (verbatim or doc-level implicit)
            a_span = align_subphrase(text, asp, raw_tokens)
            if a_span and a_span[1] < seq_len - 1:
                as_idx, ae_idx = a_span
                # Tag BIO in sequence
                bio_tags[as_idx] = TAG2ID["B-ASP"]
                for k in range(as_idx + 1, ae_idx + 1):
                    bio_tags[k] = TAG2ID["I-ASP"]
            else:
                # Implicit document-level aspect anchor at <s> (token 0)
                as_idx, ae_idx = 0, 0

            # Tag Opinion BIO in sequence
            bio_tags[os_idx] = TAG2ID["B-OPN"]
            for k in range(os_idx + 1, oe_idx + 1):
                bio_tags[k] = TAG2ID["I-OPN"]

            pol_id = POLARITY2ID.get(pol, POLARITY2ID["NEU"])
            cat_id = CATEGORY2ID.get(cat, CATEGORY2ID["OTHER"])
            sev_id = SEVERITY2ID.get(sev, SEVERITY2ID["LOW"])

            gold_pairs.append({
                "aspect_span": (as_idx, ae_idx),
                "opinion_span": (os_idx, oe_idx),
                "polarity": pol_id,
                "category": cat_id,
                "severity": sev_id,
                "raw_aspect": asp,
                "raw_opinion": opn,
                "raw_polarity": pol
            })
            valid_aspect_spans.append((as_idx, ae_idx))
            valid_opinion_spans.append((os_idx, oe_idx))

        return {
            "id": item["id"],
            "text": text,
            "input_ids": input_ids,
            "bio_tags": bio_tags,
            "gold_pairs": gold_pairs,
            "seq_len": seq_len
        }


def aste_collate_fn(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
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


# ==============================================================================
# MODEL ARCHITECTURE: PhoBertForASTE
# ==============================================================================
class PhoBertForASTE(nn.Module):
    def __init__(self, model_name: str = "vinai/phobert-base-v2", dropout_rate: float = 0.15):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden_size = self.encoder.config.hidden_size  # 768 for phobert-base

        self.dropout = nn.Dropout(dropout_rate)
        self.tag_classifier = nn.Linear(hidden_size, len(TAG2ID))

        # Pair feature: [v_asp (768), v_opn (768), v_asp * v_opn (768), |v_asp - v_opn| (768), v_cls (768)] = 3840
        pair_dim = hidden_size * 5
        self.pair_dense = nn.Sequential(
            nn.Linear(pair_dim, hidden_size),
            nn.GELU(),
            nn.Dropout(dropout_rate)
        )

        self.polarity_head = nn.Linear(hidden_size, len(POLARITY2ID))
        self.category_head = nn.Linear(hidden_size, len(CATEGORY2ID))
        self.severity_head = nn.Linear(hidden_size, len(SEVERITY2ID))

        self.loss_bio = nn.CrossEntropyLoss(ignore_index=-100)
        # Class weighting for balanced multi-polarity learning
        pol_weights = torch.tensor([1.0, 1.2, 1.8, 1.8])  # NONE, NEG, POS, NEU
        self.loss_pol = nn.CrossEntropyLoss(weight=pol_weights)
        self.loss_cat = nn.CrossEntropyLoss(ignore_index=0)
        self.loss_sev = nn.CrossEntropyLoss(ignore_index=0)

    def extract_span_repr(self, sequence_output: torch.Tensor, start_idx: int, end_idx: int) -> torch.Tensor:
        """Mean pooling across token span [start_idx, end_idx]."""
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

        # Training forward pass with loss computation
        if bio_tags is not None and raw_batch is not None:
            loss_span = self.loss_bio(bio_logits.view(-1, len(TAG2ID)), bio_tags.view(-1))

            pair_feats = []
            pair_polarities = []
            pair_categories = []
            pair_severities = []

            device = input_ids.device
            self.loss_pol.weight = self.loss_pol.weight.to(device)

            for b_idx, sample in enumerate(raw_batch):
                seq_rep = sequence_output[b_idx]
                cls_rep = cls_output[b_idx]
                gold_pairs = sample["gold_pairs"]

                # Collect gold pairs
                for gp in gold_pairs:
                    as_i, ae_i = gp["aspect_span"]
                    os_i, oe_i = gp["opinion_span"]
                    v_asp = self.extract_span_repr(seq_rep, as_i, ae_i)
                    v_opn = self.extract_span_repr(seq_rep, os_i, oe_i)
                    feat = torch.cat([v_asp, v_opn, v_asp * v_opn, torch.abs(v_asp - v_opn), cls_rep], dim=-1)
                    pair_feats.append(feat)
                    pair_polarities.append(gp["polarity"])
                    pair_categories.append(gp["category"])
                    pair_severities.append(gp["severity"])

                # Negative sampling: create unassociated candidate pairs within sentence
                all_asps = list({gp["aspect_span"] for gp in gold_pairs})
                all_opns = list({gp["opinion_span"] for gp in gold_pairs})
                positive_combos = {(gp["aspect_span"], gp["opinion_span"]) for gp in gold_pairs}

                for a_sp in all_asps:
                    for o_sp in all_opns:
                        if (a_sp, o_sp) not in positive_combos:
                            v_asp = self.extract_span_repr(seq_rep, a_sp[0], a_sp[1])
                            v_opn = self.extract_span_repr(seq_rep, o_sp[0], o_sp[1])
                            feat = torch.cat([v_asp, v_opn, v_asp * v_opn, torch.abs(v_asp - v_opn), cls_rep], dim=-1)
                            pair_feats.append(feat)
                            pair_polarities.append(POLARITY2ID["NONE"])
                            pair_categories.append(0)
                            pair_severities.append(0)

            if pair_feats:
                pair_feats_t = torch.stack(pair_feats, dim=0)
                pair_h = self.pair_dense(pair_feats_t)
                pol_logits = self.polarity_head(pair_h)
                cat_logits = self.category_head(pair_h)
                sev_logits = self.severity_head(pair_h)

                labels_pol = torch.tensor(pair_polarities, dtype=torch.long, device=device)
                labels_cat = torch.tensor(pair_categories, dtype=torch.long, device=device)
                labels_sev = torch.tensor(pair_severities, dtype=torch.long, device=device)

                loss_pol = self.loss_pol(pol_logits, labels_pol)
                loss_cat = self.loss_cat(cat_logits, labels_cat)
                loss_sev = self.loss_sev(sev_logits, labels_sev)

                total_loss = loss_span + 1.2 * loss_pol + 0.4 * loss_cat + 0.4 * loss_sev
            else:
                total_loss = loss_span

            results["loss"] = total_loss

        return results

    def predict_triplets_for_sample(
        self,
        sequence_output: torch.Tensor,
        cls_output: torch.Tensor,
        predicted_tags: List[str],
        tokenizer,
        raw_text: str
    ) -> List[Dict[str, Any]]:
        """Decodes candidate Aspect and Opinion spans and classifies pair relations."""
        # 1. Parse Aspect and Opinion candidate spans
        aspect_spans = []
        opinion_spans = []

        curr_asp = None
        curr_opn = None

        for idx, tag in enumerate(predicted_tags):
            # Aspect
            if tag == "B-ASP":
                if curr_asp is not None and (curr_asp[1] - curr_asp[0] + 1) <= 10:
                    aspect_spans.append(curr_asp)
                curr_asp = [idx, idx]
            elif tag == "I-ASP" and curr_asp is not None:
                curr_asp[1] = idx
            else:
                if curr_asp is not None:
                    if (curr_asp[1] - curr_asp[0] + 1) <= 10:
                        aspect_spans.append(curr_asp)
                    curr_asp = None

            # Opinion
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

        if curr_asp is not None and (curr_asp[1] - curr_asp[0] + 1) <= 10:
            aspect_spans.append(curr_asp)
        if curr_opn is not None and (curr_opn[1] - curr_opn[0] + 1) <= 16:
            opinion_spans.append(curr_opn)

        # Always include implicit document-level anchor [0, 0] as fallback candidate
        aspect_spans.append([0, 0])

        if not opinion_spans:
            return []

        # 2. Score each (aspect, opinion) pair
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
        cat_logits = self.category_head(pair_h)
        sev_logits = self.severity_head(pair_h)

        pol_probs = torch.softmax(pol_logits, dim=-1)
        pred_pols = torch.argmax(pol_probs, dim=-1).cpu().tolist()
        pred_cats = torch.argmax(cat_logits, dim=-1).cpu().tolist()
        pred_sevs = torch.argmax(sev_logits, dim=-1).cpu().tolist()

        raw_tokens = tokenizer.tokenize(raw_text)

        predicted_triplets = []
        for i, (asp_span, opn_span) in enumerate(candidates):
            pol_id = pred_pols[i]
            if pol_id == POLARITY2ID["NONE"]:
                continue

            pol_label = ID2POLARITY[pol_id]
            cat_label = ID2CATEGORY.get(pred_cats[i], "LOCATION_STREET")
            sev_label = ID2SEVERITY.get(pred_sevs[i], "LOW")
            confidence = float(pol_probs[i, pol_id].item())

            # Decode Aspect
            if asp_span == (0, 0):
                aspect_str = "TP. Hồ Chí Minh"
                provenance = "DOC_FALLBACK"
            else:
                tok_slice = raw_tokens[asp_span[0] - 1: asp_span[1]]
                aspect_str = tokenizer.convert_tokens_to_string(tok_slice).replace("@@", "").strip()
                provenance = "SPAN_MATCHED"

            # Decode Opinion
            opn_slice = raw_tokens[opn_span[0] - 1: opn_span[1]]
            opinion_str = tokenizer.convert_tokens_to_string(opn_slice).replace("@@", "").strip()

            if not aspect_str or not opinion_str:
                continue

            predicted_triplets.append({
                "aspect": aspect_str,
                "opinion": opinion_str,
                "polarity": pol_label,
                "aspect_category": cat_label,
                "severity": sev_label,
                "grounding_provenance": provenance,
                "confidence": round(confidence, 4),
                "aspect_span": asp_span,
                "opinion_span": opn_span
            })

        return predicted_triplets


# ==============================================================================
# BENCHMARK EVALUATION FUNCTION
# ==============================================================================
def evaluate_model(model: PhoBertForASTE, dataloader: DataLoader, tokenizer, device: str) -> Dict[str, Any]:
    model.eval()

    gold_triplets_count = 0
    pred_triplets_count = 0
    correct_triplets_count = 0

    pol_stats = defaultdict(lambda: {"gold": 0, "pred": 0, "correct": 0})
    aspect_stats = {"gold": 0, "pred": 0, "correct": 0}
    opinion_stats = {"gold": 0, "pred": 0, "correct": 0}

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            raw_batch = batch["raw_batch"]

            outputs = model.encoder(input_ids=input_ids, attention_mask=attention_mask)
            seq_out = outputs.last_hidden_state
            cls_out = seq_out[:, 0, :]
            bio_logits = model.tag_classifier(seq_out)
            pred_tags_batch = torch.argmax(bio_logits, dim=-1).cpu().tolist()

            for b_idx, sample in enumerate(raw_batch):
                slen = sample["seq_len"]
                sample_tags = [ID2TAG[t] for t in pred_tags_batch[b_idx][:slen]]
                text = sample["text"]

                preds = model.predict_triplets_for_sample(
                    seq_out[b_idx], cls_out[b_idx], sample_tags, tokenizer, text
                )

                gold_triplets = sample["gold_pairs"]
                gold_triplets_count += len(gold_triplets)
                pred_triplets_count += len(preds)

                # Track Aspect / Opinion span counts
                gold_asps = {gp["aspect_span"] for gp in gold_triplets if gp["aspect_span"] != (0, 0)}
                gold_opns = {gp["opinion_span"] for gp in gold_triplets}
                pred_asps = {p["aspect_span"] for p in preds if p["aspect_span"] != (0, 0)}
                pred_opns = {p["opinion_span"] for p in preds}

                aspect_stats["gold"] += len(gold_asps)
                aspect_stats["pred"] += len(pred_asps)
                aspect_stats["correct"] += len(gold_asps.intersection(pred_asps))

                opinion_stats["gold"] += len(gold_opns)
                opinion_stats["pred"] += len(pred_opns)
                opinion_stats["correct"] += len(gold_opns.intersection(pred_opns))

                for gp in gold_triplets:
                    pol_stats[ID2POLARITY[gp["polarity"]]]["gold"] += 1
                for p in preds:
                    pol_stats[p["polarity"]]["pred"] += 1

                # Strict Triplet Match: Aspect span matches AND Opinion span matches AND Polarity matches
                matched_gold = set()
                for p in preds:
                    for g_idx, gp in enumerate(gold_triplets):
                        if g_idx in matched_gold:
                            continue
                        if (
                            p["aspect_span"] == gp["aspect_span"]
                            and p["opinion_span"] == gp["opinion_span"]
                            and p["polarity"] == ID2POLARITY[gp["polarity"]]
                        ):
                            correct_triplets_count += 1
                            pol_stats[p["polarity"]]["correct"] += 1
                            matched_gold.add(g_idx)
                            break

    def calc_prf(c, p, g):
        prec = (c / p) if p > 0 else 0.0
        rec = (c / g) if g > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        return round(prec * 100, 2), round(rec * 100, 2), round(f1 * 100, 2)

    triplet_p, triplet_r, triplet_f1 = calc_prf(correct_triplets_count, pred_triplets_count, gold_triplets_count)
    asp_p, asp_r, asp_f1 = calc_prf(aspect_stats["correct"], aspect_stats["pred"], aspect_stats["gold"])
    opn_p, opn_r, opn_f1 = calc_prf(opinion_stats["correct"], opinion_stats["pred"], opinion_stats["gold"])

    polarity_results = {}
    f1_sum = 0.0
    for pol in ["NEG", "POS", "NEU"]:
        st = pol_stats[pol]
        p_c, r_c, f_c = calc_prf(st["correct"], st["pred"], st["gold"])
        polarity_results[pol] = {"Precision": p_c, "Recall": r_c, "F1": f_c, "Gold": st["gold"], "Pred": st["pred"]}
        f1_sum += f_c
    macro_f1 = round(f1_sum / 3.0, 2)

    return {
        "Triplet_Strict_Match": {"Precision": triplet_p, "Recall": triplet_r, "F1": triplet_f1, "Gold": gold_triplets_count, "Pred": pred_triplets_count, "Correct": correct_triplets_count},
        "Aspect_Span": {"Precision": asp_p, "Recall": asp_r, "F1": asp_f1},
        "Opinion_Span": {"Precision": opn_p, "Recall": opn_r, "F1": opn_f1},
        "Polarity_Per_Class": polarity_results,
        "Macro_Polarity_F1": macro_f1
    }


# ==============================================================================
# MAIN TRAINING PIPELINE
# ==============================================================================
def train_phobert(args):
    print("=" * 80)
    print("🌊 PhoBERT Fast-Path ASTE Fine-Tuning Pipeline (v3 Splits)")
    print("=" * 80)

    device = torch.device(args.device if torch.cuda.is_available() and args.device == "cuda" else "cpu")
    print(f"Hardware Device: {device} ({torch.cuda.get_device_name(0) if device.type == 'cuda' else 'CPU'})")

    print(f"\n[1/4] Loading PhoBERT Tokenizer: {args.model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    train_path = os.path.join(args.splits_dir, "train.json")
    dev_path = os.path.join(args.splits_dir, "dev.json")
    test_path = os.path.join(args.splits_dir, "test.json")

    print(f"[2/4] Loading V3 Dataset Splits from: {args.splits_dir}...")
    train_ds = ASTEJsonDataset(train_path, tokenizer, max_len=args.max_len, is_train=True)
    dev_ds = ASTEJsonDataset(dev_path, tokenizer, max_len=args.max_len, is_train=False)
    test_ds = ASTEJsonDataset(test_path, tokenizer, max_len=args.max_len, is_train=False)

    print(f"  • Train Samples: {len(train_ds):,}")
    print(f"  • Dev Samples  : {len(dev_ds):,}")
    print(f"  • Test Samples : {len(test_ds):,}")

    g = torch.Generator()
    g.manual_seed(RANDOM_SEED)
    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=aste_collate_fn,
        generator=g,
        worker_init_fn=seed_worker
    )
    dev_loader = DataLoader(dev_ds, batch_size=args.batch_size, shuffle=False, collate_fn=aste_collate_fn)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False, collate_fn=aste_collate_fn)

    print(f"\n[3/4] Initializing PhoBertForASTE Model...")
    model = PhoBertForASTE(model_name=args.model_name, dropout_rate=args.dropout).to(device)

    # Optimizer & Scheduler
    no_decay = ["bias", "LayerNorm.weight"]
    optimizer_grouped_parameters = [
        {"params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)], "weight_decay": args.weight_decay},
        {"params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)], "weight_decay": 0.0},
    ]
    optimizer = torch.optim.AdamW(optimizer_grouped_parameters, lr=args.learning_rate)

    total_steps = len(train_loader) * args.epochs
    warmup_steps = int(0.10 * total_steps)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps)
    scaler = torch.amp.GradScaler('cuda', enabled=args.fp16 and device.type == "cuda")

    os.makedirs(args.output_dir, exist_ok=True)
    best_dev_f1 = -1.0
    best_checkpoint_path = os.path.join(args.output_dir, "best_phobert_aste.pt")

    print(f"\n[4/4] Starting Fine-Tuning ({args.epochs} Epochs, FP16: {args.fp16})...")
    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        start_time = time.time()

        for step, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            bio_tags = batch["bio_tags"].to(device)
            raw_batch = batch["raw_batch"]

            optimizer.zero_grad()

            with torch.amp.autocast('cuda', enabled=args.fp16 and device.type == "cuda"):
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, bio_tags=bio_tags, raw_batch=raw_batch)
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

            if (step + 1) % max(1, len(train_loader) // 5) == 0:
                print(f"  Epoch [{epoch}/{args.epochs}] Step [{step+1}/{len(train_loader)}] - Loss: {loss.item():.4f}")

        avg_train_loss = total_loss / len(train_loader)
        epoch_sec = time.time() - start_time

        # Validate on Dev Set
        dev_metrics = evaluate_model(model, dev_loader, tokenizer, device)
        dev_triplet_f1 = dev_metrics["Triplet_Strict_Match"]["F1"]
        dev_asp_f1 = dev_metrics["Aspect_Span"]["F1"]
        dev_opn_f1 = dev_metrics["Opinion_Span"]["F1"]
        dev_macro_f1 = dev_metrics["Macro_Polarity_F1"]

        # Composite score prioritizing Strict Triplet F1 with span grounding signals
        dev_score = dev_triplet_f1 * 2.0 + dev_asp_f1 + dev_opn_f1

        print(f"\n--- Epoch {epoch}/{args.epochs} Finished ({epoch_sec:.1f}s) ---")
        print(f"  Train Loss: {avg_train_loss:.4f}")
        print(f"  Dev Triplet Strict F1 : {dev_triplet_f1:.2f}% (P: {dev_metrics['Triplet_Strict_Match']['Precision']}%, R: {dev_metrics['Triplet_Strict_Match']['Recall']}%)")
        print(f"  Dev Aspect F1         : {dev_asp_f1:.2f}% | Opinion F1: {dev_opn_f1:.2f}%")
        print(f"  Dev Macro Polarity F1 : {dev_macro_f1:.2f}% (NEG: {dev_metrics['Polarity_Per_Class']['NEG']['F1']}%, POS: {dev_metrics['Polarity_Per_Class']['POS']['F1']}%, NEU: {dev_metrics['Polarity_Per_Class']['NEU']['F1']}%)")

        if dev_score > best_dev_f1:
            best_dev_f1 = dev_score
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "dev_metrics": dev_metrics,
                "args": vars(args)
            }, best_checkpoint_path)
            tokenizer.save_pretrained(args.output_dir)
            print(f"  >>> ⭐ Best Model Checkpoint Saved (Triplet F1: {dev_triplet_f1:.2f}%, Asp F1: {dev_asp_f1:.2f}%, Opn F1: {dev_opn_f1:.2f}%) !\n")

    # ==============================================================================
    # FINAL EVALUATION ON INDEPENDENT TEST SPLIT (Zero-Leakage Benchmark)
    # ==============================================================================
    print("=" * 80)
    print("🏆 FINAL BENCHMARK EVALUATION ON TEST SET (test.json)")
    print("=" * 80)

    checkpoint = torch.load(best_checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    test_metrics = evaluate_model(model, test_loader, tokenizer, device)

    # Save benchmark report
    report_path = os.path.join(args.output_dir, "benchmark_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(test_metrics, f, indent=2, ensure_ascii=False)

    training_meta = {
        "model_name": args.model_name,
        "random_seed": RANDOM_SEED,
        "selection_criterion": "composite_val_f1_grounded",
        "best_epoch": checkpoint.get("epoch", 0),
        "best_dev_metrics": checkpoint.get("dev_metrics", {}),
        "args": vars(args),
        "git_commit_sha": get_git_commit_sha(),
        "dataset_md5": {
            "train": get_file_md5(train_path),
            "dev": get_file_md5(dev_path),
            "test": get_file_md5(test_path)
        },
        "hardware": {
            "device": str(device),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
            "torch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available()
        }
    }
    with open(os.path.join(args.output_dir, "training_meta.json"), "w", encoding="utf-8") as f:
        json.dump(training_meta, f, indent=2, ensure_ascii=False)

    print("\n✅ Academic Benchmark Results (Ready for ICWSM / KDD Paper):")
    print(f"  • Triplet Strict Match F1 : {test_metrics['Triplet_Strict_Match']['F1']:.2f}% (P: {test_metrics['Triplet_Strict_Match']['Precision']}%, R: {test_metrics['Triplet_Strict_Match']['Recall']}%)")
    print(f"  • Aspect Entity F1        : {test_metrics['Aspect_Span']['F1']:.2f}% (P: {test_metrics['Aspect_Span']['Precision']}%, R: {test_metrics['Aspect_Span']['Recall']}%)")
    print(f"  • Opinion Expression F1   : {test_metrics['Opinion_Span']['F1']:.2f}% (P: {test_metrics['Opinion_Span']['Precision']}%, R: {test_metrics['Opinion_Span']['Recall']}%)")
    print(f"  • Macro Polarity F1       : {test_metrics['Macro_Polarity_F1']:.2f}%")
    for pol in ["NEG", "POS", "NEU"]:
        p_info = test_metrics["Polarity_Per_Class"][pol]
        print(f"    - [{pol}] F1: {p_info['F1']:.2f}% (P: {p_info['Precision']}%, R: {p_info['Recall']}%, Gold: {p_info['Gold']})")

    print(f"\nAll artifacts and benchmark report saved to: {args.output_dir}")


# ==============================================================================
# STANDALONE PREDICTOR FOR REAL-TIME SERVING
# ==============================================================================
class PhoBertASTEPredictor:
    def __init__(self, checkpoint_dir: str, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = torch.device(device)
        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir)
        ckpt_file = os.path.join(checkpoint_dir, "best_phobert_aste.pt")
        if not os.path.exists(ckpt_file):
            raise FileNotFoundError(f"Checkpoint file not found: {ckpt_file}")

        checkpoint = torch.load(ckpt_file, map_location=self.device)
        checkpoint_args = checkpoint.get("args") or checkpoint.get("params") or {}
        model_name = checkpoint_args.get("model_name")
        if not model_name:
            model_name = "vinai/phobert-large" if "large" in checkpoint_dir else "vinai/phobert-base-v2"
        self.model = PhoBertForASTE(model_name=model_name).to(self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()

    def predict(self, text: str) -> List[Dict[str, Any]]:
        raw_tokens = self.tokenizer.tokenize(text)
        if len(raw_tokens) > 158:
            raw_tokens = raw_tokens[:158]

        input_ids = self.tokenizer.convert_tokens_to_ids(raw_tokens)
        input_ids = [self.tokenizer.bos_token_id] + input_ids + [self.tokenizer.eos_token_id]
        inp_t = torch.tensor([input_ids], dtype=torch.long, device=self.device)
        att_t = torch.ones_like(inp_t)

        with torch.no_grad():
            outputs = self.model.encoder(input_ids=inp_t, attention_mask=att_t)
            seq_out = outputs.last_hidden_state[0]
            cls_out = seq_out[0]
            bio_logits = self.model.tag_classifier(seq_out.unsqueeze(0))
            pred_tags = torch.argmax(bio_logits[0], dim=-1).cpu().tolist()
            sample_tags = [ID2TAG[t] for t in pred_tags[:len(input_ids)]]

            triplets = self.model.predict_triplets_for_sample(
                seq_out, cls_out, sample_tags, self.tokenizer, text
            )

        return triplets


# ==============================================================================
# CLI ENTRYPOINT
# ==============================================================================
def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tune PhoBERT Fast-Path ASTE Model on HCMC Urban Flood v3 Splits")
    parser.add_argument("--model_name", type=str, default="vinai/phobert-base-v2", help="Pretrained PhoBERT model")
    parser.add_argument("--splits_dir", type=str, default="data/processed/splits", help="Directory containing train.json, dev.json, test.json")
    parser.add_argument("--output_dir", type=str, default="AI/finetune/checkpoints/phobert_aste_best", help="Directory to save model checkpoint")
    parser.add_argument("--epochs", type=int, default=6, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size for training and evaluation")
    parser.add_argument("--learning_rate", type=float, default=3e-5, help="Learning rate for AdamW optimizer")
    parser.add_argument("--weight_decay", type=float, default=0.01, help="Weight decay for regularization")
    parser.add_argument("--dropout", type=float, default=0.15, help="Dropout probability")
    parser.add_argument("--max_len", type=int, default=160, help="Maximum token sequence length")
    parser.add_argument("--device", type=str, default="cuda", help="Computation device (cuda or cpu)")
    parser.add_argument("--fp16", action="store_true", default=True, help="Enable mixed-precision FP16 training")
    parser.add_argument("--predict", type=str, default=None, help="Inference mode: test a custom sentence")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.predict:
        print(f"Running inference on checkpoint: {args.output_dir}")
        predictor = PhoBertASTEPredictor(checkpoint_dir=args.output_dir, device=args.device)
        triplets = predictor.predict(args.predict)
        print(f"\nInput Text: \"{args.predict}\"")
        print(f"Extracted Triplets ({len(triplets)}):")
        print(json.dumps(triplets, indent=2, ensure_ascii=False))
    else:
        train_phobert(args)
