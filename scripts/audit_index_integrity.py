#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/audit_index_integrity.py
Strictly Read-Only Reverse-Reconstruction Index Auditor for ASTE-Data-V2 files.
Usage:
    python3 scripts/audit_index_integrity.py <file_path> [start_idx] [end_idx]
"""

import ast
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/audit_index_integrity.py <file_path> [start_idx] [end_idx]")
        return 1

    file_path = sys.argv[1]
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\r\n") for line in f]

    start_idx = int(sys.argv[2]) if len(sys.argv) >= 3 else 0
    end_idx = int(sys.argv[3]) if len(sys.argv) >= 4 else len(lines)
    subset = lines[start_idx:end_idx]

    print(f"============================================================")
    print(f" REVERSE INDEX INTEGRITY AUDIT: {file_path} [{start_idx + 1}..{min(end_idx, len(lines))}]")
    print(f"============================================================")

    total_triplets = 0
    errors = []

    for offset, line in enumerate(subset):
        line_num = start_idx + offset + 1
        if "####" not in line:
            errors.append((line_num, "Missing '####' delimiter"))
            continue
        text, trip_str = line.split("####", 1)
        tokens = text.split()
        try:
            triplets = ast.literal_eval(trip_str)
        except Exception as e:
            errors.append((line_num, f"Syntax error: {e}"))
            continue

        if not triplets:
            continue

        reconstructed = []
        for a, o, pol in triplets:
            total_triplets += 1
            if not a or not o or any(i < 0 or i >= len(tokens) for i in a + o):
                errors.append((line_num, f"Index out of bounds: a={a}, o={o}"))
                continue
            a_text = " ".join(tokens[i] for i in a)
            o_text = " ".join(tokens[i] for i in o)
            if not a_text.strip() or not o_text.strip():
                errors.append((line_num, f"Empty reconstructed token string: a='{a_text}', o='{o_text}'"))
            reconstructed.append(f"({a} -> '{a_text}' | {o} -> '{o_text}' | {pol})")

        if len(subset) <= 60:
            print(f"L{line_num:03d}: " + " ; ".join(reconstructed))

    print(f"------------------------------------------------------------")
    print(f"Verified {len(subset)} lines | {total_triplets} triplets reconstructed | {len(errors)} index errors")
    for ln, msg in errors:
        print(f"  [ERROR Line {ln}]: {msg}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

