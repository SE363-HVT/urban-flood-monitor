#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generate_dataset_figures.py
--------------------------------------------------------------------------------
Publication-grade scientific figures for the HCMC Urban Flood Multimodal ASTE Dataset.
Conforms to Swiss Modernism 2.0 / Academic Precision standards (CVPR/ICCV/IEEE).

Outputs:
    RadiNet/figure/fig1_dataset_architecture_overview.png / .pdf
    RadiNet/figure/fig2_aste_triplet_diagnostics.png / .pdf
    RadiNet/figure/fig3_semantic_aspect_opinion_matrix.png / .pdf
    RadiNet/figure/fig4_geospatial_flood_hotspots.png / .pdf

Author: RadiNet Research Team
Domain: Multimodal Aspect Sentiment Triplet Extraction (M-ABSA / ASTE) for Urban Flooding
"""

import os
import sys
import json
from collections import Counter, defaultdict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Patch

# Set font family and rendering parameters
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']
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
C_EMERALD_POS = "#059669"
C_AMBER_NEU   = "#D97706"
C_ROSE_NEG    = "#DC2626"
C_SLATE_MUTED = "#64748B"
C_PANEL_BG    = "#F8FAFC"
C_WHITE       = "#FFFFFF"
C_BORDER      = "#CBD5E1"

HALO = [pe.withStroke(linewidth=2.8, foreground="white")]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "hcmc_flood_annotated_v2_multimodal.json")
OUT_DIR = os.path.join(PROJECT_ROOT, "figure")
os.makedirs(OUT_DIR, exist_ok=True)


def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================================================================
# FIGURE 1: Dataset Composition & Architecture Overview
# ==============================================================================
def generate_figure1_overview(data):
    """
    3-Panel Panoramic Overview:
    (a) Source Platform & Modality Composition (Text-only vs. Multimodal)
    (b) Temporal & Flood Episode Ingestion Breakdown
    (c) Sentence Length Distributions across Ingestion Streams
    """
    fig = plt.figure(figsize=(13.2, 4.4), dpi=300, facecolor=C_WHITE)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.25, 1.0], wspace=0.32, left=0.06, right=0.96, top=0.86, bottom=0.14)
    
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])
    ax_c = fig.add_subplot(gs[2])

    # --- Panel (a): Platform & Media Breakdown ---
    platforms = ["Google News", "Facebook", "TikTok"]
    text_only = [2085, 822, 4]
    multimodal = [0, 256, 755]
    totals = [2085, 1078, 759]
    y_pos = np.arange(len(platforms))
    bar_h = 0.52

    p1 = ax_a.barh(y_pos, text_only, height=bar_h, color="#94A3B8", edgecolor="#64748B", linewidth=0.8, label="Text-only")
    p2 = ax_a.barh(y_pos, multimodal, height=bar_h, left=text_only, color="#3B82F6", edgecolor="#1D4ED8", linewidth=0.8, label="Multimodal (Video/Image)")

    for idx, (t, m, tot) in enumerate(zip(text_only, multimodal, totals)):
        pct = tot / len(data) * 100
        ax_a.text(tot + 45, idx, f"{tot:,}\n({pct:.1f}%)", va="center", ha="left", fontsize=8.2, fontweight="bold", color=C_NAVY_DARK)

    ax_a.set_yticks(y_pos)
    ax_a.set_yticklabels(platforms, fontweight="bold", fontsize=9.0)
    ax_a.set_xlim(0, 2750)
    ax_a.set_xlabel("Number of Samples", fontsize=8.8, fontweight="bold", color=C_NAVY_DARK)
    ax_a.set_title("(a) Platform & Modality Composition", loc="left", fontsize=10.0, fontweight="bold", color=C_NAVY_DARK, pad=8)
    ax_a.legend(loc="upper right", fontsize=8.0, framealpha=0.95, edgecolor=C_BORDER)
    ax_a.grid(axis="x", alpha=0.6)

    # --- Panel (b): Episode Breakdown ---
    episodes_data = [
        ("Hist. Archive\n(2018-2025)", 2096, "#475569"),
        ("Ep.03: Peak\nHigh Tide", 498, "#0284C7"),
        ("Ep.04: Lunar\nMid-Autumn Tide", 364, "#0369A1"),
        ("Sporadic Flood\nEvents", 345, "#64748B"),
        ("Ep.05: Localized\nDownpours", 287, "#0D9488"),
        ("Ep.02: Typhoon\nSoulik Rainband", 209, "#2563EB"),
        ("Ep.01: Early Sept\nConvective Storm", 123, "#4F46E5"),
    ]
    ep_names = [x[0] for x in episodes_data]
    ep_counts = [x[1] for x in episodes_data]
    ep_colors = [x[2] for x in episodes_data]
    x_b = np.arange(len(episodes_data))

    bars_b = ax_b.bar(x_b, ep_counts, width=0.62, color=ep_colors, edgecolor="#1E293B", linewidth=0.7)
    for bar in bars_b:
        h = bar.get_height()
        ax_b.text(bar.get_x() + bar.get_width() / 2.0, h + 35, f"{h:,}", ha="center", va="bottom", fontsize=7.8, fontweight="bold", color=C_NAVY_DARK)

    ax_b.set_xticks(x_b)
    ax_b.set_xticklabels(ep_names, rotation=35, ha="right", fontsize=7.8)
    ax_b.set_ylim(0, 2450)
    ax_b.set_ylabel("Number of Samples", fontsize=8.8, fontweight="bold", color=C_NAVY_DARK)
    ax_b.set_title("(b) Ingestion by Flood & Tide Episode", loc="left", fontsize=10.0, fontweight="bold", color=C_NAVY_DARK, pad=8)
    ax_b.grid(axis="y", alpha=0.6)

    # --- Panel (c): Sequence Word Lengths Boxplot/KDE ---
    news_words = [len(it["content"]["text"].split()) for it in data if it["source"]["platform"] == "news"]
    fb_words = [len(it["content"]["text"].split()) for it in data if it["source"]["platform"] == "facebook"]
    tt_words = [len(it["content"]["text"].split()) for it in data if it["source"]["platform"] == "tiktok"]

    # Filter outliers > 120 words for clean visualization
    news_filt = [min(w, 120) for w in news_words]
    fb_filt = [min(w, 120) for w in fb_words]
    tt_filt = [min(w, 120) for w in tt_words]

    box_data = [news_filt, fb_filt, tt_filt]
    box = ax_c.boxplot(box_data, vert=True, patch_artist=True, widths=0.48,
                       medianprops=dict(color=C_NAVY_DARK, linewidth=1.6),
                       whiskerprops=dict(color="#64748B", linewidth=1.0),
                       capprops=dict(color="#64748B", linewidth=1.0),
                       flierprops=dict(marker='o', markersize=2.5, alpha=0.3, color="#94A3B8"))

    box_colors = ["#93C5FD", "#67E8F9", "#C4B5FD"]
    for patch, col in zip(box['boxes'], box_colors):
        patch.set_facecolor(col)
        patch.set_edgecolor("#334155")
        patch.set_linewidth(1.1)

    medians = [np.median(news_words), np.median(fb_words), np.median(tt_words)]
    means = [np.mean(news_words), np.mean(fb_words), np.mean(tt_words)]
    for idx, (med, mn) in enumerate(zip(medians, means)):
        ax_c.text(idx + 1, 105, f"Med: {med:.0f}\nAvg: {mn:.1f}", ha="center", va="center", fontsize=7.6, fontweight="bold",
                  bbox=dict(boxstyle="round,pad=0.22", facecolor=C_WHITE, edgecolor=C_BORDER, alpha=0.9))

    ax_c.set_xticks([1, 2, 3])
    ax_c.set_xticklabels(["News\n(Sentences)", "Facebook\n(Posts)", "TikTok\n(Captions)"], fontweight="bold", fontsize=8.6)
    ax_c.set_ylim(0, 125)
    ax_c.set_ylabel("Words per Sample", fontsize=8.8, fontweight="bold", color=C_NAVY_DARK)
    ax_c.set_title("(c) Sequence Length Distribution", loc="left", fontsize=10.0, fontweight="bold", color=C_NAVY_DARK, pad=8)
    ax_c.grid(axis="y", alpha=0.6)

    for ax in [ax_a, ax_b, ax_c]:
        ax.set_facecolor(C_PANEL_BG)

    plt.savefig(os.path.join(OUT_DIR, "fig1_dataset_architecture_overview.png"), dpi=300, bbox_inches="tight")
    plt.savefig(os.path.join(OUT_DIR, "fig1_dataset_architecture_overview.pdf"), bbox_inches="tight")
    plt.close()
    print("Generated: RadiNet/figure/fig1_dataset_architecture_overview.png & .pdf")


# ==============================================================================
# FIGURE 2: ASTE Triplet Telemetry & Diagnostics
# ==============================================================================
def generate_figure2_aste_diagnostics(data):
    """
    4-Panel ASTE Triplet Diagnostic Figure:
    (a) Extreme Sentiment Polarity Distribution (NEG vs. NEU vs. POS)
    (b) Triplet Density per Sentence (1 vs 2 triplets)
    (c) Aspect Text-Grounding Breakdown (Verbatim vs Implicit)
    (d) Aspect and Opinion Span Word Length Distributions
    """
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 8.4), dpi=300, facecolor=C_WHITE)
    plt.subplots_adjust(wspace=0.28, hspace=0.38, left=0.08, right=0.95, top=0.92, bottom=0.08)

    ax_pol = axes[0, 0]
    ax_den = axes[0, 1]
    ax_grd = axes[1, 0]
    ax_len = axes[1, 1]

    # --- Panel (a): Polarity Distribution (Log scale + Direct Counts) ---
    pols = ["NEGATIVE\n(Severe Flood)", "NEUTRAL\n(Advisory / Tide)", "POSITIVE\n(Water Receded)"]
    counts = [5163, 303, 17]
    pcts = [5163 / 5483 * 100, 303 / 5483 * 100, 17 / 5483 * 100]
    cols = [C_ROSE_NEG, C_AMBER_NEU, C_EMERALD_POS]
    x_a = np.arange(len(pols))

    bars_a = ax_pol.bar(x_a, counts, color=cols, width=0.55, edgecolor="#1E293B", linewidth=1.0)
    for bar, c, p in zip(bars_a, counts, pcts):
        ax_pol.text(bar.get_x() + bar.get_width() / 2.0, c * 1.18, f"{c:,}\n({p:.1f}%)",
                    ha="center", va="bottom", fontsize=8.6, fontweight="bold", color=C_NAVY_DARK)

    ax_pol.set_yscale("log")
    ax_pol.set_ylim(5, 18000)
    ax_pol.set_xticks(x_a)
    ax_pol.set_xticklabels(pols, fontweight="bold", fontsize=8.6)
    ax_pol.set_ylabel("Triplets (Logarithmic Scale)", fontsize=8.8, fontweight="bold", color=C_NAVY_DARK)
    ax_pol.set_title("(a) Aspect Sentiment Polarity Distribution", loc="left", fontsize=9.8, fontweight="bold", color=C_NAVY_DARK, pad=6)
    ax_pol.grid(axis="y", which="both", alpha=0.5)

    # Imbalance annotation box
    ax_pol.text(0.95, 0.92, "Extreme Imbalance:\nNEG : POS = 303.7 : 1", transform=ax_pol.transAxes,
                ha="right", va="top", fontsize=8.0, fontweight="bold", color=C_ROSE_NEG,
                bbox=dict(boxstyle="round,pad=0.28", facecolor="#FEE2E2", edgecolor="#FCA5A5"))

    # --- Panel (b): Triplet Density Distribution ---
    densities = ["1 Triplet", "2 Triplets"]
    dens_counts = [2361, 1561]
    dens_pcts = [2361 / 3922 * 100, 1561 / 3922 * 100]
    colors_den = ["#3B82F6", "#8B5CF6"]

    wedges, texts, autotexts = ax_den.pie(
        dens_counts, labels=densities, autopct="%1.1f%%", startangle=90,
        colors=colors_den, explode=(0.04, 0.04), pctdistance=0.78,
        wedgeprops=dict(width=0.45, edgecolor="#FFFFFF", linewidth=2.0),
        textprops=dict(fontsize=8.8, fontweight="bold", color=C_NAVY_DARK)
    )
    for at in autotexts:
        at.set_fontsize(9.2)
        at.set_fontweight("bold")
        at.set_color(C_WHITE)

    ax_den.text(0, 0, f"Total\n3,922\nSamples", ha="center", va="center", fontsize=8.8, fontweight="bold", color=C_NAVY_DARK)
    ax_den.set_title("(b) Triplet Multiplicity Density", loc="left", fontsize=9.8, fontweight="bold", color=C_NAVY_DARK, pad=6)

    # --- Panel (c): Text-Grounding Breakdown ---
    categories_grd = ["Verbatim Substring\n(Grounded in text)", "Canonical Entity\n(Implicit domain entity)"]
    grd_counts = [3985, 1498]
    grd_pcts = [3985 / 5483 * 100, 1498 / 5483 * 100]
    grd_colors = ["#10B981", "#F59E0B"]

    bars_c = ax_grd.barh(np.arange(len(categories_grd)), grd_counts, height=0.50, color=grd_colors, edgecolor="#1E293B", linewidth=0.8)
    for bar, c, p in zip(bars_c, grd_counts, grd_pcts):
        ax_grd.text(c + 80, bar.get_y() + bar.get_height() / 2.0, f"{c:,} ({p:.1f}%)",
                    va="center", ha="left", fontsize=8.6, fontweight="bold", color=C_NAVY_DARK)

    ax_grd.set_yticks(np.arange(len(categories_grd)))
    ax_grd.set_yticklabels(categories_grd, fontweight="bold", fontsize=8.6)
    ax_grd.set_xlim(0, 5600)
    ax_grd.set_xlabel("Number of Triplets", fontsize=8.8, fontweight="bold", color=C_NAVY_DARK)
    ax_grd.set_title("(c) Aspect Text-Grounding Status", loc="left", fontsize=9.8, fontweight="bold", color=C_NAVY_DARK, pad=6)
    ax_grd.grid(axis="x", alpha=0.6)

    # --- Panel (d): Span Length Distributions ---
    aspect_lens = []
    opinion_lens = []
    for it in data:
        for t in it.get("aste_triplets", []):
            aspect_lens.append(len(t["aspect"].split()))
            opinion_lens.append(len(t["opinion"].split()))

    x_spans = np.arange(1, 15)
    asp_freq = Counter(aspect_lens)
    opn_freq = Counter(opinion_lens)
    asp_dist = [asp_freq.get(x, 0) / len(aspect_lens) * 100 for x in x_spans]
    opn_dist = [opn_freq.get(x, 0) / len(opinion_lens) * 100 for x in x_spans]

    w_bar = 0.38
    ax_len.bar(x_spans - w_bar / 2, asp_dist, width=w_bar, color="#06B6D4", edgecolor="#0891B2", label="Aspect Term (Avg: 2.6 words)")
    ax_len.bar(x_spans + w_bar / 2, opn_dist, width=w_bar, color="#F97316", edgecolor="#EA580C", label="Opinion Phrase (Avg: 7.4 words)")

    ax_len.set_xticks(x_spans)
    ax_len.set_xlim(0.2, 14.8)
    ax_len.set_xlabel("Span Length (Words / Tokens)", fontsize=8.8, fontweight="bold", color=C_NAVY_DARK)
    ax_len.set_ylabel("Share of Spans (%)", fontsize=8.8, fontweight="bold", color=C_NAVY_DARK)
    ax_len.set_title("(d) Span Token Length Distributions", loc="left", fontsize=9.8, fontweight="bold", color=C_NAVY_DARK, pad=6)
    ax_len.legend(loc="upper right", fontsize=8.0, framealpha=0.95, edgecolor=C_BORDER)
    ax_len.grid(axis="y", alpha=0.6)

    for ax in [ax_pol, ax_grd, ax_len]:
        ax.set_facecolor(C_PANEL_BG)

    plt.savefig(os.path.join(OUT_DIR, "fig2_aste_triplet_diagnostics.png"), dpi=300, bbox_inches="tight")
    plt.savefig(os.path.join(OUT_DIR, "fig2_aste_triplet_diagnostics.pdf"), bbox_inches="tight")
    plt.close()
    print("Generated: RadiNet/figure/fig2_aste_triplet_diagnostics.png & .pdf")


# ==============================================================================
# FIGURE 3: Semantic Aspect-Opinion Co-occurrence Matrix
# ==============================================================================
def generate_figure3_cooccurrence_matrix(data):
    """
    Publication-grade Co-occurrence Heatmap Matrix:
    Cross-tabulates Top 8 Aspect Categories/Entities against Top 7 Canonical Opinion Expressions.
    """
    top_aspects = [
        "Khu vực ngập",
        "Phương tiện giao thông",
        "TP. Hồ Chí Minh",
        "TP. Thủ Đức",
        "Tuyến đường ngập",
        "Sài Gòn",
        "Đường Trần Xuân Soạn",
        "Sông Sài Gòn",
    ]
    
    top_opinions = [
        "ngập nước cục bộ",
        "ngập sâu gây cản trở giao thông",
        "xe chết máy, dắt bộ",
        "triều cường dâng cao",
        "nước tràn vào nhà dân",
        "nước rút chậm",
        "dự báo / theo dõi (NEU)"
    ]

    def norm_aspect(asp_str):
        al = asp_str.strip().lower()
        if al in ["tp.hcm", "tphcm", "tp. hồ chí minh", "tp hcm", "tp hồ chí minh", "hồ chí minh"]:
            return "TP. Hồ Chí Minh"
        elif al in ["thủ đức", "tp. thủ đức", "tp thủ đức"]:
            return "TP. Thủ Đức"
        elif al in ["trần xuân soạn", "đường trần xuân soạn"]:
            return "Đường Trần Xuân Soạn"
        elif al in ["sông sài gòn"]:
            return "Sông Sài Gòn"
        elif al in ["sài gòn"]:
            return "Sài Gòn"
        elif al in ["khu vực ngập"]:
            return "Khu vực ngập"
        elif al in ["phương tiện giao thông", "xe cộ"]:
            return "Phương tiện giao thông"
        elif al in ["tuyến đường ngập", "đường ngập"]:
            return "Tuyến đường ngập"
        return None

    def match_opinion(opn):
        ol = opn.lower()
        if "cục bộ" in ol:
            return "ngập nước cục bộ"
        elif "cản trở" in ol or "tê liệt" in ol:
            return "ngập sâu gây cản trở giao thông"
        elif "chết máy" in ol or "dắt bộ" in ol or "lút bánh" in ol:
            return "xe chết máy, dắt bộ"
        elif "triều cường dâng" in ol or "dâng cao gây ngập" in ol:
            return "triều cường dâng cao"
        elif "nhà dân" in ol:
            return "nước tràn vào nhà dân"
        elif "rút chậm" in ol:
            return "nước rút chậm"
        elif "dự báo" in ol or "theo dõi" in ol or "đang lên" in ol:
            return "dự báo / theo dõi (NEU)"
        return None

    matrix = np.zeros((len(top_aspects), len(top_opinions)))
    
    for it in data:
        for t in it.get("aste_triplets", []):
            asp = norm_aspect(t["aspect"])
            opn = match_opinion(t["opinion"])
            if asp and opn:
                r = top_aspects.index(asp)
                c = top_opinions.index(opn)
                matrix[r, c] += 1

    fig, ax = plt.subplots(figsize=(11.2, 6.6), dpi=300, facecolor=C_WHITE)
    
    cmap = plt.cm.Blues
    norm_matrix = np.sqrt(matrix)
    im = ax.imshow(norm_matrix, cmap=cmap, aspect="auto", vmin=0)

    # Ticks & Labels
    ax.set_xticks(np.arange(len(top_opinions)))
    ax.set_yticks(np.arange(len(top_aspects)))
    
    opn_labels = [
        "1. Ngập nước\ncục bộ (NEG)",
        "2. Cản trở /\ntắc đường (NEG)",
        "3. Chết máy,\ndắt bộ (NEG)",
        "4. Triều cường\ndâng cao (NEG)",
        "5. Nước tràn\nvào nhà (NEG)",
        "6. Nước rút\nchậm (NEG)",
        "7. Dự báo /\ntheo dõi (NEU)"
    ]
    asp_labels = [
        "Khu vực ngập (Domain)",
        "Phương tiện giao thông (Vehicle)",
        "TP. Hồ Chí Minh (City-wide)",
        "TP. Thủ Đức (District)",
        "Tuyến đường ngập (Roadway)",
        "Sài Gòn (Urban Macro)",
        "Đường Trần Xuân Soạn (Hotspot)",
        "Sông Sài Gòn (Hydrology)"
    ]

    ax.set_xticklabels(opn_labels, fontsize=8.6, fontweight="bold", color=C_NAVY_DARK)
    ax.set_yticklabels(asp_labels, fontsize=8.8, fontweight="bold", color=C_NAVY_DARK)

    # In-cell numerical text
    max_val = matrix.max()
    for i in range(len(top_aspects)):
        for j in range(len(top_opinions)):
            val = int(matrix[i, j])
            text_color = C_WHITE if matrix[i, j] > max_val * 0.38 else C_NAVY_DARK
            ax.text(j, i, f"{val:,}" if val > 0 else "-", ha="center", va="center",
                    color=text_color, fontsize=8.8, fontweight="bold")

    # Titles & Styling
    ax.set_title("Semantic Aspect-Opinion Co-occurrence & Sentiment Interaction Matrix",
                 fontsize=10.6, fontweight="bold", color=C_NAVY_DARK, pad=12)
    ax.set_xlabel("Canonical Opinion Expressions & Polarity Classes", fontsize=9.2, fontweight="bold", color=C_NAVY_DARK, labelpad=8)
    ax.set_ylabel("High-Frequency Aspect Entities", fontsize=9.2, fontweight="bold", color=C_NAVY_DARK, labelpad=8)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
    cbar.ax.set_ylabel("Intensity (Square-Root Scaled Frequency)", fontsize=8.0, fontweight="bold", color=C_NAVY_DARK)
    cbar.ax.tick_params(labelsize=7.6)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "fig3_semantic_aspect_opinion_matrix.png"), dpi=300, bbox_inches="tight")
    plt.savefig(os.path.join(OUT_DIR, "fig3_semantic_aspect_opinion_matrix.pdf"), bbox_inches="tight")
    plt.close()
    print("Generated: RadiNet/figure/fig3_semantic_aspect_opinion_matrix.png & .pdf")


# ==============================================================================
# FIGURE 4: Geospatial Urban Flood Hotspots
# ==============================================================================
def generate_figure4_hotspots(data):
    """
    2-Panel Geospatial Distribution Figure:
    (a) Top 12 Specific Urban Flood Hotspots / Vulnerable Corridors in HCMC
    (b) Administrative Ward Representation & Regional Vulnerability Clusters
    """
    fig, (ax_roads, ax_wards) = plt.subplots(1, 2, figsize=(12.8, 5.4), dpi=300, facecolor=C_WHITE)
    plt.subplots_adjust(wspace=0.34, left=0.21, right=0.96, top=0.88, bottom=0.12)

    # --- Panel (a): Top Specific Roadways ---
    hotspots = [
        ("Trần Xuân Soạn (Quận 7 - Triều cường)", 123, "#DC2626"),
        ("Chợ Thủ Đức / Dương Văn Cam (Trũng)", 112, "#EA580C"),
        ("Phan Huy Ích (Gò Vấp / Tân Bình)", 70, "#D97706"),
        ("Bán đảo Bình Quới (Bình Thạnh)", 64, "#2563EB"),
        ("Quốc Hương (Thảo Điền)", 42, "#0284C7"),
        ("Nguyễn Hữu Cảnh (Bình Thạnh)", 40, "#0D9488"),
        ("Tô Ngọc Vân (Thủ Đức)", 38, "#059669"),
        ("Kinh Dương Vương (Bình Tân)", 27, "#4F46E5"),
        ("Ung Văn Khiêm (Bình Thạnh)", 26, "#7C3AED"),
        ("Hầm chui An Phú (Nút giao Thủ Đức)", 25, "#9333EA"),
        ("Đỗ Xuân Hợp (TP. Thủ Đức)", 22, "#64748B"),
        ("Võ Văn Ngân (Dốc Thủ Đức)", 21, "#475569"),
    ]
    road_names = [x[0] for x in hotspots][::-1]
    road_counts = [x[1] for x in hotspots][::-1]
    road_colors = [x[2] for x in hotspots][::-1]
    y_r = np.arange(len(hotspots))

    bars_r = ax_roads.barh(y_r, road_counts, height=0.62, color=road_colors, edgecolor="#1E293B", linewidth=0.7)
    for bar in bars_r:
        w = bar.get_width()
        ax_roads.text(w + 2.5, bar.get_y() + bar.get_height() / 2.0, f"{int(w)}",
                      va="center", ha="left", fontsize=8.2, fontweight="bold", color=C_NAVY_DARK)

    ax_roads.set_yticks(y_r)
    ax_roads.set_yticklabels(road_names, fontsize=8.4, fontweight="bold", color=C_NAVY_DARK)
    ax_roads.set_xlim(0, 145)
    ax_roads.set_xlabel("Mentions in Flood Dataset", fontsize=8.8, fontweight="bold", color=C_NAVY_DARK)
    ax_roads.set_title("(a) Top Specific Urban Flood Corridors", loc="left", fontsize=10.0, fontweight="bold", color=C_NAVY_DARK, pad=8)
    ax_roads.grid(axis="x", alpha=0.6)

    # --- Panel (b): Administrative Region Cluster Share ---
    region_clusters = [
        ("TP. Thủ Đức\n(Linh Đông, Thảo Điền, Linh Chiểu)", 468, "#2563EB"),
        ("Quận 7 & Nhà Bè\n(Tân Hưng, Phú Thuận, Phước Kiển)", 294, "#DC2626"),
        ("Bình Thạnh\n(Bình Quới, P.19, P.21, P.25)", 245, "#0284C7"),
        ("Gò Vấp & Tân Bình\n(P.14, P.15, Phan Huy Ích)", 182, "#EA580C"),
        ("Bình Tân & Quận 8\n(An Lạc, Mễ Cốc, Bến Phú Định)", 126, "#7C3AED"),
        ("Bình Dương Border\n(Thuận An, Dĩ An, Lái Thiêu)", 88, "#059669"),
        ("City-wide / Area Macro\n(Chưa gắn tuyến đường lẻ)", 2519, "#94A3B8"),
    ]
    reg_names = [x[0] for x in region_clusters][::-1]
    reg_counts = [x[1] for x in region_clusters][::-1]
    reg_colors = [x[2] for x in region_clusters][::-1]
    y_w = np.arange(len(region_clusters))

    bars_w = ax_wards.barh(y_w, reg_counts, height=0.62, color=reg_colors, edgecolor="#1E293B", linewidth=0.7)
    for bar in bars_w:
        w = bar.get_width()
        pct = w / len(data) * 100
        ax_wards.text(w + 35, bar.get_y() + bar.get_height() / 2.0, f"{int(w):,} ({pct:.1f}%)",
                      va="center", ha="left", fontsize=8.2, fontweight="bold", color=C_NAVY_DARK)

    ax_wards.set_yticks(y_w)
    ax_wards.set_yticklabels(reg_names, fontsize=8.2, fontweight="bold", color=C_NAVY_DARK)
    ax_wards.set_xlim(0, 2950)
    ax_wards.set_xlabel("Number of Samples", fontsize=8.8, fontweight="bold", color=C_NAVY_DARK)
    ax_wards.set_title("(b) Administrative Regional Clusters (NQ 1278)", loc="left", fontsize=10.0, fontweight="bold", color=C_NAVY_DARK, pad=8)
    ax_wards.grid(axis="x", alpha=0.6)

    for ax in [ax_roads, ax_wards]:
        ax.set_facecolor(C_PANEL_BG)

    plt.savefig(os.path.join(OUT_DIR, "fig4_geospatial_flood_hotspots.png"), dpi=300, bbox_inches="tight")
    plt.savefig(os.path.join(OUT_DIR, "fig4_geospatial_flood_hotspots.pdf"), bbox_inches="tight")
    plt.close()
    print("Generated: RadiNet/figure/fig4_geospatial_flood_hotspots.png & .pdf")


def main():
    print(f"Loading dataset: {DATA_PATH}...")
    data = load_data()
    print(f"Loaded {len(data):,} items successfully.")
    
    print("\n--- Generating Scientific Figures ---")
    generate_figure1_overview(data)
    generate_figure2_aste_diagnostics(data)
    generate_figure3_cooccurrence_matrix(data)
    generate_figure4_hotspots(data)
    print("\nAll 4 figures generated successfully in RadiNet/figure/")


if __name__ == "__main__":
    main()
