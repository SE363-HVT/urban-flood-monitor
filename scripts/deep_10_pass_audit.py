#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/deep_10_pass_audit.py
Strictly Read-Only 10-Pass Independent Linter for ASTE-Data-V2 files.
Usage:
    python3 scripts/deep_10_pass_audit.py <file_path>
"""

import ast
import re
import sys

LOC_PREPS = {
    "ở", "tại", "trên", "dưới", "trong", "ngoài",
    "từ", "đến", "gần", "cạnh", "bên", "phía", "thuộc", "của"
}
EDGE_PUNCT = set(".,;:!?…”\"'()[]-–|“")
VEHICLES = {
    "xe", "xe máy", "ô tô", "xe buýt", "xe tải",
    "xe cộ", "phương tiện", "xe con", "xe ben"
}
FORBIDDEN_ASPECTS = {
    "mặt đường", "đoạn đường", "con đường", "chân cầu", "cư xá",
    "làn nước ngập", "nâng nền", "dòng nước", "miệng cống",
    "mực nước", "triều cường", "đỉnh triều", "mực nước triều",
    "nước triều", "nước triều cường", "người dân"
}
NON_HCM_PROVINCES = [
    "hà nội", "cần thơ", "cà mau", "sa đéc", "đồng nai", "biên hòa", "vĩnh long",
    "tiền giang", "bến tre", "an giang", "kiên giang", "hậu giang", "sóc trăng",
    "bạc liêu", "trà vinh", "đồng tháp", "long an", "tây ninh", "bình phước",
    "đà nẵng", "huế", "nha trang", "lâm đồng", "đà lạt", "hải phòng", "quảng ninh",
    "nghệ an", "tp vinh", "thanh hóa", "nông cống", "tứ liên", "chương mỹ"
]


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/deep_10_pass_audit.py <file_path>")
        return 1

    file_path = sys.argv[1]
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\r\n") for line in f]

    pass_errors = {i: [] for i in range(1, 11)}
    parsed_records = []

    # Pass 1: FORMAT_ERROR & Pass 2: SYNTAX_ERROR
    for idx, line in enumerate(lines, 1):
        if "####" not in line:
            pass_errors[1].append((idx, "Missing '####' delimiter"))
            continue
        text, trip_str = line.split("####", 1)
        tokens = text.split()
        if not tokens:
            pass_errors[1].append((idx, "Empty sentence left of '####'"))
            continue
        try:
            triplets = ast.literal_eval(trip_str)
            if not isinstance(triplets, list):
                pass_errors[2].append((idx, "Triplets payload is not a list"))
                continue
        except Exception as e:
            pass_errors[2].append((idx, f"ast.literal_eval failed: {e}"))
            continue
        parsed_records.append((idx, text, tokens, triplets))

    # Passes 3 to 10
    for idx, text, tokens, triplets in parsed_records:
        text_lower = text.lower()
        if triplets:
            for prov in NON_HCM_PROVINCES:
                if re.search(r"\b" + re.escape(prov) + r"\b", text_lower):
                    pass_errors[9].append((idx, f"Out-of-scope province '{prov}' not rejected"))

        for a, o, pol in triplets:
            if pol not in {"POS", "NEG", "NEU"}:
                pass_errors[1].append((idx, f"Invalid polarity '{pol}'"))
            # Pass 3: OUT_OF_BOUNDS
            if not a or not o or any(i < 0 or i >= len(tokens) for i in a + o):
                pass_errors[3].append((idx, f"Index out of bounds: a={a}, o={o}, len={len(tokens)}"))
                continue
            # Pass 4: NON_CONTIGUOUS
            if a != list(range(a[0], a[-1] + 1)) or o != list(range(o[0], o[-1] + 1)):
                pass_errors[4].append((idx, f"Non-contiguous span: a={a}, o={o}"))
            # Pass 5: OVERLAP_INDEX
            if set(a) & set(o):
                pass_errors[5].append((idx, f"Overlapping aspect/opinion indices: a={a}, o={o}"))

            a_tokens = [tokens[i] for i in a]
            o_tokens = [tokens[i] for i in o]
            a_str = " ".join(a_tokens)
            o_str = " ".join(o_tokens)

            # Pass 6: PREP_LEAKAGE
            if a_tokens[0].lower() in LOC_PREPS:
                pass_errors[6].append((idx, f"Leading preposition in aspect: '{a_str}'"))
            # Pass 7: PUNCT_LEAKAGE
            if a_tokens[0] in EDGE_PUNCT or a_tokens[-1] in EDGE_PUNCT:
                pass_errors[7].append((idx, f"Edge punctuation in aspect: '{a_str}'"))
            if o_tokens[0] in EDGE_PUNCT or o_tokens[-1] in EDGE_PUNCT:
                pass_errors[7].append((idx, f"Edge punctuation in opinion: '{o_str}'"))
            # Pass 8: VEHICLE_ASPECT & FORBIDDEN_ASPECT
            if a_str.lower() in VEHICLES or a_str.lower() in FORBIDDEN_ASPECTS:
                pass_errors[8].append((idx, f"Forbidden/vehicle aspect: '{a_str}'"))
            # Pass 10: DOC_FALLBACK_MISUSE
            if a == [1, 2, 3, 4] and tokens[:5] == ["Tại", "TP.", "Hồ", "Chí", "Minh"]:
                body = " ".join(tokens[6:])
                m = re.search(
                    r"\b(đường|phố|hẻm|quốc lộ|tỉnh lộ|đại lộ|xa lộ|cầu|hầm|kênh|rạch|sông|suối|phường|quận|huyện|xã|khu dân cư|khu đô thị)\s+[A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ0-9]",
                    body,
                )
                if m:
                    pass_errors[10].append((idx, f"DOC_FALLBACK_MISUSE when '{m.group(0)}' exists"))

    pass_names = {
        1: "FORMAT_ERROR",
        2: "SYNTAX_ERROR",
        3: "OUT_OF_BOUNDS",
        4: "NON_CONTIGUOUS",
        5: "OVERLAP_INDEX",
        6: "PREP_LEAKAGE",
        7: "PUNCT_LEAKAGE",
        8: "VEHICLE_OR_FORBIDDEN_ASPECT",
        9: "NON_HCM_PROVINCE",
        10: "DOC_FALLBACK_MISUSE",
    }

    print(f"============================================================")
    print(f" DEEP 10-PASS AUDIT REPORT: {file_path} ({len(lines)} lines)")
    print(f"============================================================")
    total_err = 0
    for p in range(1, 11):
        errs = pass_errors[p]
        total_err += len(errs)
        status = "PASS (0 errors)" if not errs else f"FAIL ({len(errs)} errors)"
        print(f"  Pass {p:2d} [{pass_names[p]:<27}]: {status}")
        for ln, msg in errs:
            print(f"      -> Line {ln}: {msg}")
    print(f"------------------------------------------------------------")
    print(f"TOTAL ERRORS: {total_err}")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())

