#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI/phobert/large/semeval_v2/finetune/train_phobert_large_semeval_v2.py
--------------------------------------------------------------------------------
End-to-End Fine-Tuning Pipeline for PhoBERT Large on the SemEval v2 ASTE Format
(data/semeval_v2/{train.json, dev.json, test.json}).

Architecture:
  1. PhoBERT Large Contextual Sequence Encoder (vinai/phobert-large, Hidden=1024, 24 Layers).
  2. Token BIO Sequence Tagger (Aspect & Opinion boundary extraction).
  3. Span-Pair Multi-Attribute Classifier (Polarity: NONE, NEG, POS, NEU).
  4. Direct SemEval v2 Span Alignment (Zero-loss word-to-BPE token mapping).
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


def align_words_to_bpe(words: List[str], tokenizer) -> Tuple[List[str], List[List[int]], Dict[int, int]]:
    bpe_tokens = []
    word2bpe = []
    bpe2word = {}
    for w_idx, w in enumerate(words):
        sub_toks = tokenizer.tokenize(w)
        if not sub_toks:
            sub_toks = [tokenizer.unk_token]
        start_bpe = len(bpe_tokens)
        for i in range(len(sub_toks)):
            bpe2word[start_bpe + i] = w_idx
        bpe_tokens.extend(sub_toks)
        end_bpe = len(bpe_tokens)
        word2bpe.append(list(range(start_bpe, end_bpe)))
    return bpe_tokens, word2bpe, bpe2word


class SemEvalASTEDataset(Dataset):
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
                        "semeval_triplets": ast.literal_eval(tgt)
                    })

        for item in raw_items:
            words = item.get("tokens") or item.get("sentence", "").split()
            if not words:
                continue

            bpe_tokens, word2bpe, bpe2word = align_words_to_bpe(words, self.tokenizer)

            # Prepend <s> and append </s>
            all_bpe_tokens = [self.tokenizer.cls_token] + bpe_tokens + [self.tokenizer.sep_token]
            if len(all_bpe_tokens) > self.max_len:
                all_bpe_tokens = all_bpe_tokens[:self.max_len - 1] + [self.tokenizer.sep_token]

            input_ids = self.tokenizer.convert_tokens_to_ids(all_bpe_tokens)
            attention_mask = [1] * len(input_ids)

            # Offset by 1 for <s>
            bpe2word_shifted = {bpe_idx + 1: w_idx for bpe_idx, w_idx in bpe2word.items() if bpe_idx + 1 < len(input_ids) - 1}
            word2bpe_shifted = []
            for bpe_list in word2bpe:
                shifted = [b + 1 for b in bpe_list if b + 1 < len(input_ids) - 1]
                word2bpe_shifted.append(shifted)

            bio_tags = [TAG2ID["O"]] * len(input_ids)
            gold_pairs = []

            for triplet in item.get("semeval_triplets", []):
                aspect_word_indices, opinion_word_indices, pol = triplet
                pol_str = pol.upper() if isinstance(pol, str) else "NEG"

                asp_bpe_indices = []
                for w in aspect_word_indices:
                    if w < len(word2bpe_shifted):
                        asp_bpe_indices.extend(word2bpe_shifted[w])

                opn_bpe_indices = []
                for w in opinion_word_indices:
                    if w < len(word2bpe_shifted):
                        opn_bpe_indices.extend(word2bpe_shifted[w])

                if not asp_bpe_indices or not opn_bpe_indices:
                    continue

                bio_tags[asp_bpe_indices[0]] = TAG2ID["B-ASP"]
                for b in asp_bpe_indices[1:]:
                    bio_tags[b] = TAG2ID["I-ASP"]

                bio_tags[opn_bpe_indices[0]] = TAG2ID["B-OPN"]
                for b in opn_bpe_indices[1:]:
                    bio_tags[b] = TAG2ID["I-OPN"]

                gold_pairs.append({
                    "aspect_tok_span": (min(asp_bpe_indices), max(asp_bpe_indices) + 1),
                    "opinion_tok_span": (min(opn_bpe_indices), max(opn_bpe_indices) + 1),
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
                "bpe2word": bpe2word_shifted,
                "word2bpe": word2bpe_shifted,
                "seq_len": len(input_ids),
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


class PhoBertLargeForSemEvalASTE(nn.Module):
    def __init__(self, model_name: str = "vinai/phobert-large", dropout_rate: float = 0.15):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden_size = self.encoder.config.hidden_size  # 1024

        self.dropout = nn.Dropout(dropout_rate)
        self.tag_classifier = nn.Linear(hidden_size, len(TAG2ID))

        # Span-pair feature representation: 5 * 1024 = 5120
        pair_feature_dim = 5 * hidden_size
        self.pair_dense = nn.Sequential(
            nn.Linear(pair_feature_dim, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout_rate)
        )
        self.polarity_head = nn.Linear(hidden_size, len(POLARITY2ID))

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
        sequence_output = outputs.last_hidden_state  # [B, L, 1024]
        cls_output = sequence_output[:, 0, :]        # [B, 1024]

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

                for gp in gold_pairs:
                    as_i, ae_i = gp["aspect_tok_span"]
                    os_i, oe_i = gp["opinion_tok_span"]
                    v_asp = self.extract_span_repr(seq_rep, as_i, ae_i)
                    v_opn = self.extract_span_repr(seq_rep, os_i, oe_i)
                    feat = torch.cat([v_asp, v_opn, v_asp * v_opn, torch.abs(v_asp - v_opn), cls_rep], dim=-1)
                    pair_feats.append(feat)
                    pair_polarities.append(gp["polarity"])

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
        bpe2word: Dict[int, int]
    ) -> List[Tuple[Tuple[int, ...], Tuple[int, ...], str]]:
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

        pair_feats = []
        pair_meta = []

        for a_s, a_e in asp_spans:
            v_asp = self.extract_span_repr(sequence_output, a_s, a_e)
            a_w_idxs = sorted(list({bpe2word[b] for b in range(a_s, a_e) if b in bpe2word}))
            if not a_w_idxs:
                continue

            for o_s, o_e in opn_spans:
                v_opn = self.extract_span_repr(sequence_output, o_s, o_e)
                o_w_idxs = sorted(list({bpe2word[b] for b in range(o_s, o_e) if b in bpe2word}))
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
                seq_len = sample["seq_len"]
                predicted_tags = [ID2TAG[t] for t in pred_tags_batch[b_idx][:seq_len]]
                pred_triplets = model.predict_semeval_triplets(
                    sequence_output=encoder_out[b_idx],
                    cls_output=cls_out[b_idx],
                    predicted_tags=predicted_tags,
                    bpe2word=sample["bpe2word"]
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
