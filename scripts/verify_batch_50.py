#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/verify_batch_50.py
Strictly Read-Only Auditor for rolling 50-record batches (ASTE-Data-V2 format).
Usage:
    python3 scripts/verify_batch_50.py <file_path> [start_idx] [end_idx]
"""

import ast
import sys

LOC_PREPS = {
    "ở", "tại", "trên", "dưới", "trong", "ngoài",
    "từ", "đến", "gần", "cạnh", "bên", "phía", "thuộc", "của"
}
EDGE_PUNCT = set(".,;:!?…”\"'()[]-–|“")
FORBIDDEN_ASPECTS = {
    "mặt đường", "đoạn đường", "con đường", "chân cầu", "cư xá",
    "làn nước ngập", "nâng nền", "dòng nước", "miệng cống",
    "mực nước", "triều cường", "đỉnh triều", "mực nước triều",
    "nước triều", "nước triều cường", "xe", "xe máy", "ô tô",
    "xe buýt", "xe tải", "xe cộ", "phương tiện", "người dân"
}
BARE_OPINIONS = {"điểm ngập", "đoạn ngập", "khu vực ngập", "vùng ngập", "chỗ ngập"}


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/verify_batch_50.py <file_path> [start_idx] [end_idx]")
        return 1

    file_path = sys.argv[1]
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\r\n") for line in f]

    start_idx = int(sys.argv[2]) if len(sys.argv) >= 3 else 0
    end_idx = int(sys.argv[3]) if len(sys.argv) >= 4 else len(lines)
    batch = lines[start_idx:end_idx]

    print(f"=== VERIFY BATCH [{start_idx + 1} .. {min(end_idx, len(lines))}] ({len(batch)} records) ===")
    errors = []
    valid_count = 0
    reject_count = 0

    for offset, line in enumerate(batch):
        line_num = start_idx + offset + 1
        if "####" not in line:
            errors.append((line_num, "FORMAT_ERROR", "Missing '####' delimiter"))
            continue
        text, trip_str = line.split("####", 1)
        tokens = text.split()
        try:
            triplets = ast.literal_eval(trip_str)
        except Exception as e:
            errors.append((line_num, "SYNTAX_ERROR", str(e)))
            continue

        if not triplets:
            reject_count += 1
            continue
        valid_count += 1

        for a, o, pol in triplets:
            if pol not in {"POS", "NEG", "NEU"}:
                errors.append((line_num, "POLARITY_INVALID", pol))
            if not a or not o:
                errors.append((line_num, "EMPTY_SPAN", f"a={a}, o={o}"))
                continue
            if any(i < 0 or i >= len(tokens) for i in a + o):
                errors.append((line_num, "OUT_OF_BOUNDS", f"a={a}, o={o}, len={len(tokens)}"))
                continue
            if a != list(range(a[0], a[-1] + 1)):
                errors.append((line_num, "NON_CONTIGUOUS_ASPECT", str(a)))
            if o != list(range(o[0], o[-1] + 1)):
                errors.append((line_num, "NON_CONTIGUOUS_OPINION", str(o)))
            if set(a) & set(o):
                errors.append((line_num, "OVERLAP_INDEX", f"a={a}, o={o}"))

            a_tokens = [tokens[i] for i in a]
            o_tokens = [tokens[i] for i in o]
            a_str = " ".join(a_tokens)
            o_str = " ".join(o_tokens)

            if a_tokens[0].lower() in LOC_PREPS:
                errors.append((line_num, "PREP_LEAKAGE", f"a='{a_str}'"))
            if a_tokens[0] in EDGE_PUNCT or a_tokens[-1] in EDGE_PUNCT:
                errors.append((line_num, "PUNCT_LEAKAGE_ASPECT", f"a='{a_str}'"))
            if o_tokens[0] in EDGE_PUNCT or o_tokens[-1] in EDGE_PUNCT:
                errors.append((line_num, "PUNCT_LEAKAGE_OPINION", f"o='{o_str}'"))
            if a_str.lower() in FORBIDDEN_ASPECTS:
                errors.append((line_num, "FORBIDDEN_ASPECT", f"a='{a_str}'"))
            if o_str.lower() in BARE_OPINIONS:
                errors.append((line_num, "BARE_OPINION", f"o='{o_str}'"))
            if o_tokens[0].lower() in {"gây", "làm"} and len(o_tokens) > 1 and o_tokens[1].lower().startswith("ngập"):
                errors.append((line_num, "CAUSATIVE_VERB_UNSTRIPPED", f"o='{o_str}'"))

    print(f"Summary: {valid_count} valid | {reject_count} rejected ([]) | {len(errors)} errors")
    for ln, code, detail in errors:
        print(f"  [Line {ln}] {code}: {detail}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

