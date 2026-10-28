#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generate_split_figure.py
--------------------------------------------------------------------------------
Publication-grade scientific figure illustrating the HCMC Urban Flood ASTE
Dataset Partitioning & Multi-Stratification Analysis (Train 80% / Dev 10% / Test 10%).

Conforms to Swiss Modernism 2.0 / Academic Precision standards (IEEE/CVPR/ACL).
Generates:
  - figure/fig6_dataset_split_partition_diagnostics.png
  - figure/fig6_dataset_split_partition_diagnostics.pdf
"""

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Patch

# Matplotlib global typography & styling
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Liberation Sans', 'Arial', 'sans-serif']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#475569'
plt.rcParams['axes.linewidth'] = 0.85
plt.rcParams['grid.color'] = '#E2E8F0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.linewidth'] = 0.65
plt.rcParams['grid.alpha'] = 0.8
plt.rcParams['xtick.color'] = '#334155'
plt.rcParams['ytick.color'] = '#334155'
plt.rcParams['xtick.labelsize'] = 8.5
plt.rcParams['ytick.labelsize'] = 8.5

# Design Tokens (Academic Precision Palette)
C_NAVY_DARK   = "#0F172A"
C_NAVY_MAIN   = "#1E3A5F"
C_BLUE_NEWS   = "#2563EB"
C_PURPLE_TT   = "#7C3AED"
C_SKY_FB      = "#0284C7"
C_AMBER_CDA   = "#D97706"
C_EMERALD_POS = "#059669"
C_AMBER_NEU   = "#F59E0B"
C_ROSE_NEG    = "#DC2626"
C_SLATE_MUTED = "#64748B"
C_PANEL_BG    = "#F8FAFC"
C_WHITE       = "#FFFFFF"
C_BORDER      = "#CBD5E1"

C_TRAIN       = "#1E3A5F"
C_DEV         = "#0284C7"
C_TEST        = "#059669"

HALO = [pe.withStroke(linewidth=2.8, foreground="white")]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SPLIT_META_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "splits", "split_metadata.json")
OUT_DIR = os.path.join(PROJECT_ROOT, "figure")
os.makedirs(OUT_DIR, exist_ok=True)


def load_split_metadata():
    if not os.path.exists(SPLIT_META_PATH):
        raise FileNotFoundError(f"Missing split metadata: {SPLIT_META_PATH}")
    with open(SPLIT_META_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_figure(meta):
    splits = meta["splits"]
    train_st = splits["train"]["stats"]
    dev_st = splits["dev"]["stats"]
    test_st = splits["test"]["stats"]

    fig = plt.figure(figsize=(15.2, 5.2), dpi=300, facecolor=C_WHITE)
    gs = fig.add_gridspec(1, 4, width_ratios=[1.15, 1.25, 1.15, 1.45], wspace=0.32, left=0.05, right=0.97, top=0.85, bottom=0.14)

    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])
    ax_c = fig.add_subplot(gs[2])
    ax_d = fig.add_subplot(gs[3])

    for ax in [ax_a, ax_b, ax_c, ax_d]:
        ax.set_facecolor(C_PANEL_BG)
        ax.set_axisbelow(True)

    # --------------------------------------------------------------------------
    # Panel (a): Partition Scale & Modality Composition
    # --------------------------------------------------------------------------
    split_names = ["Train\n(80%)", "Dev / Val\n(10%)", "Test\n(10%)"]
    text_only = [train_st["text_only"], dev_st["text_only"], test_st["text_only"]]
    multimodal = [train_st["has_media"], dev_st["has_media"], test_st["has_media"]]
    total_triplets = [train_st["total_triplets"], dev_st["total_triplets"], test_st["total_triplets"]]

    x = np.arange(len(split_names))
    width = 0.52

    p1 = ax_a.bar(x, text_only, width, label="Text-only", color="#94A3B8", edgecolor=C_BORDER, linewidth=0.8)
    p2 = ax_a.bar(x, multimodal, width, bottom=text_only, label="Multimodal (Img/Vid)", color=C_BLUE_NEWS, edgecolor=C_NAVY_DARK, linewidth=0.8)

    # Annotations
    for i in range(len(x)):
        tot = text_only[i] + multimodal[i]
        trips = total_triplets[i]
        pct_mm = (multimodal[i] / tot) * 100
        ax_a.text(x[i], tot + 65, f"N={tot:,}\n({trips:,} trips)", ha="center", va="bottom", fontsize=8.2, fontweight="bold", color=C_NAVY_DARK, path_effects=HALO)
        ax_a.text(x[i], text_only[i] / 2, f"{text_only[i]:,}", ha="center", va="center", fontsize=7.8, color="white", fontweight="bold")
        ax_a.text(x[i], text_only[i] + (multimodal[i] / 2), f"{multimodal[i]:,}\n({pct_mm:.1f}%)", ha="center", va="center", fontsize=7.5, color="white", fontweight="bold")

    ax_a.set_xticks(x)
    ax_a.set_xticklabels(split_names, fontweight="semibold")
    ax_a.set_ylabel("Number of Samples", fontweight="semibold", color=C_NAVY_DARK)
    ax_a.set_ylim(0, 4400)
    ax_a.yaxis.grid(True)
    ax_a.legend(loc="upper right", frameon=True, facecolor=C_WHITE, framealpha=0.9, edgecolor=C_BORDER, fontsize=7.6)
    ax_a.set_title("(a) Split Scale & Modality Mix", fontweight="bold", fontsize=10.5, pad=12, color=C_NAVY_DARK)

    # --------------------------------------------------------------------------
    # Panel (b): Platform Ingestion Stratification
    # --------------------------------------------------------------------------
    platforms = ["news", "facebook", "tiktok", "cda_synthetic_inversion"]
    plat_labels = ["Google News", "Facebook", "TikTok", "CDA Synthetic"]
    colors_plat = [C_BLUE_NEWS, C_SKY_FB, C_PURPLE_TT, C_AMBER_CDA]

    # Normalize by split total to show exact percentage consistency
    train_pcts = [train_st["platforms"][p] / train_st["total_samples"] * 100 for p in platforms]
    dev_pcts = [dev_st["platforms"][p] / dev_st["total_samples"] * 100 for p in platforms]
    test_pcts = [test_st["platforms"][p] / test_st["total_samples"] * 100 for p in platforms]

    y_p = np.arange(len(platforms))
    bar_h = 0.24

    ax_b.barh(y_p - bar_h, train_pcts, height=bar_h, label="Train", color=C_TRAIN, edgecolor="white", linewidth=0.5)
    ax_b.barh(y_p, dev_pcts, height=bar_h, label="Dev / Val", color=C_DEV, edgecolor="white", linewidth=0.5)
    ax_b.barh(y_p + bar_h, test_pcts, height=bar_h, label="Test", color=C_TEST, edgecolor="white", linewidth=0.5)

    for i in range(len(platforms)):
        ax_b.text(train_pcts[i] + 0.8, y_p[i] - bar_h, f"{train_pcts[i]:.1f}%", va="center", fontsize=7.2, color=C_TRAIN, fontweight="bold")
        ax_b.text(test_pcts[i] + 0.8, y_p[i] + bar_h, f"{test_pcts[i]:.1f}%", va="center", fontsize=7.2, color=C_TEST, fontweight="bold")

    ax_b.set_yticks(y_p)
    ax_b.set_yticklabels(plat_labels, fontweight="semibold")
    ax_b.set_xlabel("Platform Ingestion Proportion (%)", fontweight="semibold", color=C_NAVY_DARK)
    ax_b.set_xlim(0, 52)
    ax_b.xaxis.grid(True)
    ax_b.legend(loc="lower right", frameon=True, facecolor=C_WHITE, framealpha=0.9, edgecolor=C_BORDER, fontsize=7.6)
    ax_b.set_title("(b) Ingestion Source Stratification", fontweight="bold", fontsize=10.5, pad=12, color=C_NAVY_DARK)

    # --------------------------------------------------------------------------
    # Panel (c): Polarity & Severity Conservation
    # --------------------------------------------------------------------------
    # Stacked 100% bars for Polarity across splits
    cols_pol = [C_ROSE_NEG, C_EMERALD_POS, C_AMBER_NEU]
    pol_labels = ["Negative", "Positive", "Neutral"]
    pol_keys = ["NEG", "POS", "NEU"]

    splits_data = [train_st, dev_st, test_st]
    x_c = np.arange(len(splits_data))
    w_c = 0.48

    bottom_p = np.zeros(len(splits_data))
    for k_idx, k in enumerate(pol_keys):
        vals = [s["polarity"][k] / s["total_triplets"] * 100 for s in splits_data]
        bars = ax_c.bar(x_c, vals, w_c, bottom=bottom_p, label=pol_labels[k_idx], color=cols_pol[k_idx], edgecolor=C_BORDER, linewidth=0.6)
        for i in range(len(splits_data)):
            if vals[i] > 6.0:
                ax_c.text(x_c[i], bottom_p[i] + vals[i] / 2, f"{vals[i]:.1f}%", ha="center", va="center", color="white", fontsize=7.5, fontweight="bold")
        bottom_p += np.array(vals)

    ax_c.set_xticks(x_c)
    ax_c.set_xticklabels(["Train", "Dev / Val", "Test"], fontweight="semibold")
    ax_c.set_ylabel("Triplet Polarity Proportion (%)", fontweight="semibold", color=C_NAVY_DARK)
    ax_c.set_ylim(0, 100)
    ax_c.yaxis.grid(True)
    ax_c.legend(loc="upper right", frameon=True, facecolor=C_WHITE, framealpha=0.9, edgecolor=C_BORDER, fontsize=7.6)
    ax_c.set_title("(c) Polarity Conservation", fontweight="bold", fontsize=10.5, pad=12, color=C_NAVY_DARK)

    # --------------------------------------------------------------------------
    # Panel (d): Top Semantic Aspect Categories Stratification
    # --------------------------------------------------------------------------
    top_aspects = [
        ("LOCATION_STREET", "Street Location"),
        ("LOCATION_ADMIN", "Admin / District"),
        ("HYDROLOGY", "Hydrology / Tide"),
        ("INFRASTRUCTURE_DRAINAGE", "Drainage Infra"),
        ("INFRASTRUCTURE", "General Infra"),
        ("TRAFFIC", "Traffic Obstruction"),
        ("RESPONSE_ENTITY", "Response Entity")
    ]

    y_d = np.arange(len(top_aspects))
    h_d = 0.24

    train_asp_pct = [train_st["aspect_category"].get(k, 0) / train_st["total_triplets"] * 100 for k, _ in top_aspects]
    dev_asp_pct = [dev_st["aspect_category"].get(k, 0) / dev_st["total_triplets"] * 100 for k, _ in top_aspects]
    test_asp_pct = [test_st["aspect_category"].get(k, 0) / test_st["total_triplets"] * 100 for k, _ in top_aspects]

    ax_d.barh(y_d - h_d, train_asp_pct, height=h_d, label="Train", color=C_TRAIN, edgecolor="white", linewidth=0.5)
    ax_d.barh(y_d, dev_asp_pct, height=h_d, label="Dev / Val", color=C_DEV, edgecolor="white", linewidth=0.5)
    ax_d.barh(y_d + h_d, test_asp_pct, height=h_d, label="Test", color=C_TEST, edgecolor="white", linewidth=0.5)

    for i in range(len(top_aspects)):
        ax_d.text(train_asp_pct[i] + 0.6, y_d[i] - h_d, f"{train_asp_pct[i]:.1f}%", va="center", fontsize=7.0, color=C_TRAIN, fontweight="bold")
        ax_d.text(test_asp_pct[i] + 0.6, y_d[i] + h_d, f"{test_asp_pct[i]:.1f}%", va="center", fontsize=7.0, color=C_TEST, fontweight="bold")

    ax_d.set_yticks(y_d)
    ax_d.set_yticklabels([name for _, name in top_aspects], fontweight="semibold")
    ax_d.set_xlabel("Aspect Category Proportion (%)", fontweight="semibold", color=C_NAVY_DARK)
    ax_d.set_xlim(0, 48)
    ax_d.xaxis.grid(True)
    ax_d.legend(loc="lower right", frameon=True, facecolor=C_WHITE, framealpha=0.9, edgecolor=C_BORDER, fontsize=7.6)
    ax_d.set_title("(d) Semantic Aspect Stratification", fontweight="bold", fontsize=10.5, pad=12, color=C_NAVY_DARK)

    # Figure Global Title
    fig.suptitle(
        "Figure 6: HCMC Urban Flood ASTE Dataset Partitioning & Cross-Split Multi-Stratification Analysis (80/10/10)",
        fontsize=12.2,
        fontweight="bold",
        color=C_NAVY_DARK,
        y=0.97
    )

    out_png = os.path.join(OUT_DIR, "fig6_dataset_split_partition_diagnostics.png")
    out_pdf = os.path.join(OUT_DIR, "fig6_dataset_split_partition_diagnostics.pdf")

    plt.savefig(out_png, dpi=300, facecolor=C_WHITE, bbox_inches='tight')
    plt.savefig(out_pdf, format="pdf", facecolor=C_WHITE, bbox_inches='tight')
    plt.close()

    print(f"[+] Successfully exported Figure 6 to:")
    print(f"    • PNG: {out_png}")
    print(f"    • PDF: {out_pdf}")


if __name__ == "__main__":
    meta = load_split_metadata()
    generate_figure(meta)
