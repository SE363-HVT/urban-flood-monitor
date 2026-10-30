#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/train_xlm_v_aste.py
--------------------------------------------------------------------------------
Joint Sequence Tagging and Multi-Task Span-Pair Representation for ASTE
using XLM-V (facebook/xlm-v-base).

XLM-V Architecture Highlights (Liang et al., Meta AI, 2023):
  • 1-Million token multilingual vocabulary (One-Million Vocab)
  • Eliminates subword fragmentation for Vietnamese named entities and slang
  • Encoder-only architecture with 768 hidden dimensions

Academic ASTE Formulation:
  • Input: Raw Vietnamese social flood text
  • Backbone: AutoModel.from_pretrained("facebook/xlm-v-base")
  • Head 1: BIO Token-level Tagger for Aspect (B-ASP, I-ASP) and Opinion (B-OPN, I-OPN)
  • Head 2: Span-Pair Representation: [v_asp, v_opn, v_asp * v_opn, |v_asp - v_opn|, v_cls]
  • Head 3: Multi-Task Classification: Polarity (NEG, POS, NEU), Category, Severity
"""

import os
import sys
import gc
import json
import time
import random
import argparse
from typing import List, Dict, Tuple, Optional, Any

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup
import hashlib
import subprocess
import numpy as np
from tqdm import tqdm

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

TAG2ID = {"O": 0, "B-ASP": 1, "I-ASP": 2, "B-OPN": 3, "I-OPN": 4}
ID2TAG = {v: k for k, v in TAG2ID.items()}

POLARITY2ID = {"NONE": 0, "NEG": 1, "POS": 2, "NEU": 3}
ID2POLARITY = {v: k for k, v in POLARITY2ID.items()}

CATEGORY2ID = {
    "OTHER": 0,
    "LOCATION_STREET": 1,
    "LOCATION_ADMIN": 2,
    "HYDROLOGY": 3,
    "INFRASTRUCTURE_DRAINAGE": 4,
    "INFRASTRUCTURE": 5,
    "TRAFFIC": 6,
    "RESPONSE_ENTITY": 7,
    "HUMAN_ACTIVITY": 8
}
ID2CATEGORY = {v: k for k, v in CATEGORY2ID.items()}

SEVERITY2ID = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
ID2SEVERITY = {v: k for k, v in SEVERITY2ID.items()}


def align_subphrase_offsets(text: str, sub_str: str, encoding) -> Optional[Tuple[int, int]]:
    """Align subphrase characters to token indices using tokenizer offset_mapping."""
    if not sub_str or not text:
        return None
    text_lower = text.lower()
    sub_lower = sub_str.lower().strip()
    idx = text_lower.find(sub_lower)
    if idx == -1:
        return None
    char_start = idx
    char_end = idx + len(sub_lower)

    offsets = encoding["offset_mapping"]
    matched = []
    for i, (ts, te) in enumerate(offsets):
        if ts == te:
            continue  # special token <s>, </s>
        if max(ts, char_start) < min(te, char_end):
            matched.append(i)

    if matched:
        return matched[0], matched[-1]
    return None


class XLMVJsonDataset(Dataset):
    def __init__(self, json_path: str, tokenizer, max_len: int = 256, is_train: bool = True):
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.is_train = is_train
        self.samples = []

        with open(json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        for item in raw_data:
            text = item.get("content", {}).get("text", "")
            if not text:
                continue

            triplets = item.get("aste_triplets", [])
            self.samples.append({
                "id": item.get("id", ""),
                "text": text,
                "triplets": triplets
            })

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        sample = self.samples[idx]
        text = sample["text"]

        encoding = self.tokenizer(
            text,
            max_length=self.max_len,
            padding=False,
            truncation=True,
            return_offsets_mapping=True,
            return_tensors=None
        )

        input_ids = encoding["input_ids"]
        seq_len = len(input_ids)
        bio_tags = [TAG2ID["O"]] * seq_len

        gold_pairs = []

        for trip in sample["triplets"]:
            asp_str = trip.get("aspect", "")
            opn_str = trip.get("opinion", "")
            pol_str = trip.get("polarity", "NONE").upper()
            cat_str = trip.get("aspect_category", "OTHER")
            sev_str = trip.get("severity", "LOW")

            asp_span = align_subphrase_offsets(text, asp_str, encoding)
            opn_span = align_subphrase_offsets(text, opn_str, encoding)

            if asp_span:
                bio_tags[asp_span[0]] = TAG2ID["B-ASP"]
                for i in range(asp_span[0] + 1, asp_span[1] + 1):
                    bio_tags[i] = TAG2ID["I-ASP"]
            else:
                asp_span = (0, 0)  # implicit/unaligned aspect

            if opn_span:
                bio_tags[opn_span[0]] = TAG2ID["B-OPN"]
                for i in range(opn_span[0] + 1, opn_span[1] + 1):
                    bio_tags[i] = TAG2ID["I-OPN"]

                gold_pairs.append({
                    "aspect_span": asp_span,
                    "opinion_span": opn_span,
                    "polarity": POLARITY2ID.get(pol_str, POLARITY2ID["NONE"]),
                    "category": CATEGORY2ID.get(cat_str, 0),
                    "severity": SEVERITY2ID.get(sev_str, 1),
                    "aspect_text": asp_str,
                    "opinion_text": opn_str,
                    "gold_polarity": pol_str
                })

        return {
            "id": sample["id"],
            "text": text,
            "input_ids": input_ids,
            "attention_mask": [1] * seq_len,
            "bio_tags": bio_tags,
            "gold_pairs": gold_pairs,
            "gold_triplets_raw": sample["triplets"]
        }


def aste_collate_fn(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    max_len = max(len(x["input_ids"]) for x in batch)
    batch_size = len(batch)

    input_ids = torch.zeros((batch_size, max_len), dtype=torch.long)
    attention_mask = torch.zeros((batch_size, max_len), dtype=torch.long)
    bio_tags = torch.full((batch_size, max_len), -100, dtype=torch.long)

    for i, x in enumerate(batch):
        l = len(x["input_ids"])
        input_ids[i, :l] = torch.tensor(x["input_ids"], dtype=torch.long)
        attention_mask[i, :l] = torch.tensor(x["attention_mask"], dtype=torch.long)
        bio_tags[i, :l] = torch.tensor(x["bio_tags"], dtype=torch.long)

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "bio_tags": bio_tags,
        "raw_batch": batch
    }


class XLMVForASTE(nn.Module):
    def __init__(self, model_name: str = "facebook/xlm-v-base", dropout_rate: float = 0.15, freeze_embeddings: bool = True):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        if freeze_embeddings:
            # XLM-V has 1-Million token vocabulary (~2.77GB embedding tensor).
            # Freezing word embeddings avoids 6GB+ AdamW state allocation, fitting cleanly in 11GB VRAM.
            if hasattr(self.encoder, "embeddings") and hasattr(self.encoder.embeddings, "word_embeddings"):
                self.encoder.embeddings.word_embeddings.weight.requires_grad = False

        hidden_size = self.encoder.config.hidden_size  # 768 for base

        self.dropout = nn.Dropout(dropout_rate)
        self.tag_classifier = nn.Linear(hidden_size, len(TAG2ID))

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
        pol_weights = torch.tensor([1.0, 1.2, 1.8, 1.8])  # NONE, NEG, POS, NEU
        self.loss_pol = nn.CrossEntropyLoss(weight=pol_weights)
        self.loss_cat = nn.CrossEntropyLoss(ignore_index=0)
        self.loss_sev = nn.CrossEntropyLoss(ignore_index=0)

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
        sequence_output = outputs.last_hidden_state
        cls_output = sequence_output[:, 0, :]

        bio_logits = self.tag_classifier(self.dropout(sequence_output))
        results = {"bio_logits": bio_logits}

        total_loss = 0.0
        if bio_tags is not None:
            active_loss = attention_mask.view(-1) == 1
            active_logits = bio_logits.view(-1, len(TAG2ID))
            active_labels = torch.where(
                active_loss,
                bio_tags.view(-1),
                torch.tensor(self.loss_bio.ignore_index).type_as(bio_tags)
            )
            loss_bio_val = self.loss_bio(active_logits, active_labels)
            total_loss = total_loss + 1.5 * loss_bio_val
            results["loss_bio"] = loss_bio_val

        pair_reps = []
        target_pol = []
        target_cat = []
        target_sev = []

        if raw_batch is not None and self.training:
            for b_idx, sample in enumerate(raw_batch):
                seq_repr = sequence_output[b_idx]
                cls_repr = cls_output[b_idx]
                gold_pairs = sample["gold_pairs"]
                gold_set = {(p["aspect_span"], p["opinion_span"]): p for p in gold_pairs}

                all_asp_spans = list(set([p["aspect_span"] for p in gold_pairs] + [(0, 0)]))
                all_opn_spans = list(set([p["opinion_span"] for p in gold_pairs]))

                for a_span in all_asp_spans:
                    v_asp = self.extract_span_repr(seq_repr, a_span[0], a_span[1])
                    for o_span in all_opn_spans:
                        v_opn = self.extract_span_repr(seq_repr, o_span[0], o_span[1])
                        feat = torch.cat([
                            v_asp,
                            v_opn,
                            v_asp * v_opn,
                            torch.abs(v_asp - v_opn),
                            cls_repr
                        ], dim=-1)
                        pair_reps.append(feat)

                        if (a_span, o_span) in gold_set:
                            gp = gold_set[(a_span, o_span)]
                            target_pol.append(gp["polarity"])
                            target_cat.append(gp["category"])
                            target_sev.append(gp["severity"])
                        else:
                            target_pol.append(POLARITY2ID["NONE"])
                            target_cat.append(0)
                            target_sev.append(0)

            if len(pair_reps) > 0:
                pair_tensor = torch.stack(pair_reps, dim=0)
                pair_dense = self.pair_dense(pair_tensor)
                pol_logits = self.polarity_head(pair_dense)
                cat_logits = self.category_head(pair_dense)
                sev_logits = self.severity_head(pair_dense)

                dev = input_ids.device
                l_pol = self.loss_pol(pol_logits, torch.tensor(target_pol, device=dev))
                l_cat = self.loss_cat(cat_logits, torch.tensor(target_cat, device=dev))
                l_sev = self.loss_sev(sev_logits, torch.tensor(target_sev, device=dev))

                total_loss = total_loss + 2.0 * l_pol + 0.5 * l_cat + 0.5 * l_sev
                results["loss_pair"] = l_pol

            results["loss"] = total_loss

        return results

    def predict_spans_and_pairs(
        self,
        sequence_output: torch.Tensor,
        cls_output: torch.Tensor,
        candidate_aspects: List[Tuple[int, int]],
        candidate_opinions: List[Tuple[int, int]]
    ) -> List[Dict[str, Any]]:
        """Inference head to pair candidate spans and classify sentiment."""
        predicted_triplets = []
        if not candidate_opinions:
            return predicted_triplets

        asp_candidates = list(candidate_aspects)
        if (0, 0) not in asp_candidates:
            asp_candidates.append((0, 0))

        pair_feats = []
        pair_keys = []

        for a_span in asp_candidates:
            v_asp = self.extract_span_repr(sequence_output, a_span[0], a_span[1])
            for o_span in candidate_opinions:
                v_opn = self.extract_span_repr(sequence_output, o_span[0], o_span[1])
                feat = torch.cat([
                    v_asp,
                    v_opn,
                    v_asp * v_opn,
                    torch.abs(v_asp - v_opn),
                    cls_output
                ], dim=-1)
                pair_feats.append(feat)
                pair_keys.append((a_span, o_span))

        if not pair_feats:
            return predicted_triplets

        pair_tensor = torch.stack(pair_feats, dim=0)
        pair_dense = self.pair_dense(pair_tensor)
        pol_logits = self.polarity_head(pair_dense)
        pol_preds = torch.argmax(pol_logits, dim=-1).cpu().tolist()

        for (a_span, o_span), pol_id in zip(pair_keys, pol_preds):
            if pol_id != POLARITY2ID["NONE"]:
                predicted_triplets.append({
                    "aspect_span": a_span,
                    "opinion_span": o_span,
                    "polarity": ID2POLARITY[pol_id]
                })

        return predicted_triplets


def extract_spans_from_bio(tags: List[int]) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Decodes sequence of BIO tag IDs into Aspect and Opinion token span tuples."""
    aspects = []
    opinions = []
    cur_asp_start = None
    cur_opn_start = None

    for i, tag_id in enumerate(tags):
        tag_str = ID2TAG.get(tag_id, "O")

        if tag_str == "B-ASP":
            if cur_asp_start is not None:
                aspects.append((cur_asp_start, i - 1))
            cur_asp_start = i
        elif tag_str == "I-ASP":
            if cur_asp_start is None:
                cur_asp_start = i
        else:
            if cur_asp_start is not None:
                aspects.append((cur_asp_start, i - 1))
                cur_asp_start = None

        if tag_str == "B-OPN":
            if cur_opn_start is not None:
                opinions.append((cur_opn_start, i - 1))
            cur_opn_start = i
        elif tag_str == "I-OPN":
            if cur_opn_start is None:
                cur_opn_start = i
        else:
            if cur_opn_start is not None:
                opinions.append((cur_opn_start, i - 1))
                cur_opn_start = None

    if cur_asp_start is not None:
        aspects.append((cur_asp_start, len(tags) - 1))
    if cur_opn_start is not None:
        opinions.append((cur_opn_start, len(tags) - 1))

    return aspects, opinions


def evaluate_model(model: XLMVForASTE, dataloader: DataLoader, device: torch.device) -> Dict[str, Any]:
    model.eval()

    n_gold_triplets = 0
    n_pred_triplets = 0
    n_correct_triplets = 0

    n_gold_aspects = 0
    n_pred_aspects = 0
    n_correct_aspects = 0

    n_gold_opinions = 0
    n_pred_opinions = 0
    n_correct_opinions = 0

    pol_stats = {
        "NEG": {"gold": 0, "pred": 0, "correct": 0},
        "POS": {"gold": 0, "pred": 0, "correct": 0},
        "NEU": {"gold": 0, "pred": 0, "correct": 0}
    }

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            raw_batch = batch["raw_batch"]

            outputs = model.encoder(input_ids=input_ids, attention_mask=attention_mask)
            seq_out = outputs.last_hidden_state
            cls_out = seq_out[:, 0, :]
            bio_logits = model.tag_classifier(seq_out)
            bio_preds = torch.argmax(bio_logits, dim=-1).cpu().tolist()

            for b_idx, sample in enumerate(raw_batch):
                seq_len = len(sample["input_ids"])
                pred_tags = bio_preds[b_idx][:seq_len]

                cand_asp, cand_opn = extract_spans_from_bio(pred_tags)

                pred_trips = model.predict_spans_and_pairs(
                    seq_out[b_idx],
                    cls_out[b_idx],
                    cand_asp,
                    cand_opn
                )

                gold_triplets_set = set()
                gold_asp_set = set()
                gold_opn_set = set()

                for gp in sample["gold_pairs"]:
                    gold_triplets_set.add((gp["aspect_span"], gp["opinion_span"], gp["gold_polarity"]))
                    gold_asp_set.add(gp["aspect_span"])
                    gold_opn_set.add(gp["opinion_span"])
                    if gp["gold_polarity"] in pol_stats:
                        pol_stats[gp["gold_polarity"]]["gold"] += 1

                pred_triplets_set = set()
                pred_asp_set = set(cand_asp)
                pred_opn_set = set(cand_opn)

                for pt in pred_trips:
                    pred_triplets_set.add((pt["aspect_span"], pt["opinion_span"], pt["polarity"]))
                    if pt["polarity"] in pol_stats:
                        pol_stats[pt["polarity"]]["pred"] += 1

                correct_triplets = gold_triplets_set.intersection(pred_triplets_set)
                for ct in correct_triplets:
                    if ct[2] in pol_stats:
                        pol_stats[ct[2]]["correct"] += 1

                n_gold_triplets += len(gold_triplets_set)
                n_pred_triplets += len(pred_triplets_set)
                n_correct_triplets += len(correct_triplets)

                n_gold_aspects += len(gold_asp_set)
                n_pred_aspects += len(pred_asp_set)
                n_correct_aspects += len(gold_asp_set.intersection(pred_asp_set))

                n_gold_opinions += len(gold_opn_set)
                n_pred_opinions += len(pred_opn_set)
                n_correct_opinions += len(gold_opn_set.intersection(pred_opn_set))

    def prf(gold, pred, corr):
        p = corr / pred if pred > 0 else 0.0
        r = corr / gold if gold > 0 else 0.0
        f = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        return round(p * 100, 2), round(r * 100, 2), round(f * 100, 2)

    tp, tr, tf1 = prf(n_gold_triplets, n_pred_triplets, n_correct_triplets)
    ap, ar, af1 = prf(n_gold_aspects, n_pred_aspects, n_correct_aspects)
    op, opr, of1 = prf(n_gold_opinions, n_pred_opinions, n_correct_opinions)

    polarity_results = {}
    macro_f1_sum = 0.0
    for p_name, counts in pol_stats.items():
        p, r, f = prf(counts["gold"], counts["pred"], counts["correct"])
        polarity_results[p_name] = {
            "Precision": p,
            "Recall": r,
            "F1": f,
            "Gold": counts["gold"],
            "Pred": counts["pred"],
            "Correct": counts["correct"]
        }
        macro_f1_sum += f

    macro_pol_f1 = round(macro_f1_sum / len(pol_stats), 2)

    return {
        "Triplet_Strict_Match": {
            "Precision": tp,
            "Recall": tr,
            "F1": tf1,
            "Gold": n_gold_triplets,
            "Pred": n_pred_triplets,
            "Correct": n_correct_triplets
        },
        "Aspect_Span": {
            "Precision": ap,
            "Recall": ar,
            "F1": af1
        },
        "Opinion_Span": {
            "Precision": op,
            "Recall": opr,
            "F1": of1
        },
        "Polarity_Per_Class": polarity_results,
        "Macro_Polarity_F1": macro_pol_f1
    }
