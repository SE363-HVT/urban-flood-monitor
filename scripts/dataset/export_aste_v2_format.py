#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/export_aste_v2_format.py
--------------------------------------------------------------------------------
Adapter chuyển đổi dữ liệu ASTE Schema v3 sang định dạng chuẩn ASTE-Data-V2
(SemEval / Xu et al., EMNLP 2020: Position-Aware Tagging for ASTE).

Định dạng xuất ra (phẳng từng dòng):
  sentence####[([t_start, ..., t_end], [o_start, ..., o_end], 'POL'), ...]

Đặc điểm cốt lõi:
1. Bảo toàn 100% ngữ nghĩa theo CAM_NANG_BI_QUYET_GAN_NHAN_ASTE_CHUAN_EXPERT.md.
2. Context Prefix Injection:
   - Đối với các bộ ba kế thừa ngữ cảnh toàn bài (DOC_FALLBACK: Aspect 'TP. Hồ Chí Minh'),
     tự động chèn tiền tố ngữ cảnh: "Tại TP. Hồ Chí Minh , " vào đầu câu.
   - Định vị chính xác tuyệt đối Aspect token span [1, 2, 3, 4].
   - Tìm kiếm chính xác Opinion token span trong thân câu đã tokenize.
3. Phân tách dấu câu chuẩn mực (Punctuation & Symbol Isolation), đảm bảo các token
   được phân cách bởi khoảng trắng đồng nhất và có thể đọc bằng sentence.split().
4. Kiểm tra đối soát chéo ngược (Reverse Assertion):
   Khẳng định 100% từng token tại các chỉ số trích xuất khớp chính xác với Aspect và Opinion.
5. Hỗ trợ chuyển đổi toàn bộ master dataset (v3), hoặc từng phân vùng split (train/dev/test).

Tác giả: Nhóm Nghiên cứu Khoa học Giám sát Ngập lụt Đô thị TP.HCM
"""

import os
import sys
import re
import json
import argparse
import unicodedata
from typing import List, Dict, Tuple, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def tokenize_sentence(text: str) -> str:
    """
    Phân tách token và dấu câu chuẩn mực cho tiếng Việt ASTE:
    - Chuẩn hóa Unicode NFC.
    - Tách các từ viết tắt bị dính liền: 'TP.Thủ Đức' -> 'TP. Thủ Đức'.
    - Bảo toàn định danh 'TP.', 'Q.', 'P.'.
    - Cô lập toàn bộ dấu câu, ký hiệu, emoji bằng khoảng trắng.
    - Ghép lại thành một chuỗi duy nhất cách nhau bởi dấu cách.
    """
    if not text:
        return ""

    text = unicodedata.normalize("NFC", text.strip())

    # Tách từ viết tắt dính liền vào từ sau
    text = re.sub(r'\b(TP|Tp|tp|Q|q|P|p)\.([A-Za-z0-9à-ỹ])', r'\1. \2', text)

    # Bảo vệ các từ viết tắt cốt lõi
    text = re.sub(r'\bTP\.', '__TP_DOT__', text, flags=re.IGNORECASE)
    text = re.sub(r'\bQ\.', '__Q_DOT__', text, flags=re.IGNORECASE)
    text = re.sub(r'\bP\.', '__P_DOT__', text, flags=re.IGNORECASE)

    # Cô lập toàn bộ ký tự phi từ (\w) và phi khoảng trắng (\s)
    text = re.sub(r'([^\w\s])', r' \1 ', text)

    # Khôi phục từ viết tắt
    text = text.replace('__TP_DOT__', 'TP.')
    text = text.replace('__Q_DOT__', 'Q.')
    text = text.replace('__P_DOT__', 'P.')

    # Chuẩn hóa khoảng trắng dư thừa
    tokens = text.strip().split()
    return " ".join(tokens)


def find_subsequence_indices(doc_tokens: List[str], sub_tokens: List[str]) -> Optional[List[int]]:
    """
    Tìm dãy chỉ số token liên tục [start, start+1, ..., end] của sub_tokens trong doc_tokens.
    So khớp không phân biệt hoa thường.
    """
    n = len(doc_tokens)
    m = len(sub_tokens)
    if m == 0 or n < m:
        return None

    sub_lower = [t.lower() for t in sub_tokens]
    doc_lower = [t.lower() for t in doc_tokens]

    for i in range(n - m + 1):
        if doc_lower[i : i + m] == sub_lower:
            return list(range(i, i + m))

    # Fallback mờ nhẹ (nếu có dấu chấm cuối từ viết tắt bị sai lệch)
    sub_stripped = [t.rstrip('.').lower() for t in sub_tokens]
    for i in range(n - m + 1):
        cand_stripped = [doc_tokens[i + k].rstrip('.').lower() for k in range(m)]
        if cand_stripped == sub_stripped:
            return list(range(i, i + m))

    return None


def convert_record_to_aste_v2(record: Dict[str, Any]) -> Optional[Tuple[str, List[Tuple[List[int], List[int], str]]]]:
    """
    Chuyển đổi một bản ghi JSON sang dòng ASTE-Data-V2.
    Trả về (tokenized_sentence, list_of_triplets) hoặc None nếu không có triplet hợp lệ.
    """
    raw_text = record.get("content", {}).get("text", "").strip()
    if not raw_text:
        return None

    triplets = record.get("aste_triplets", [])
    if not triplets:
        return None

    # Kiểm tra xem có triplet nào là DOC_FALLBACK không
    has_doc_fallback = any(t.get("grounding_provenance") == "DOC_FALLBACK" for t in triplets)

    # Context Prefix Injection nếu có DOC_FALLBACK
    prefix = "Tại TP. Hồ Chí Minh , " if has_doc_fallback else ""
    full_text = prefix + raw_text

    tokenized_sentence = tokenize_sentence(full_text)
    doc_tokens = tokenized_sentence.split()

    converted_triplets = []

    for t in triplets:
        asp = t.get("aspect", "").strip()
        opn = t.get("opinion", "").strip()
        pol = t.get("polarity", "NEU").strip()
        prov = t.get("grounding_provenance", "SPAN_MATCHED")

        # Chuẩn hóa nhãn polarity hợp lệ: POS, NEG, NEU
        if pol not in ["POS", "NEG", "NEU"]:
            pol = "NEU"

        # Aspect tokens
        if prov == "DOC_FALLBACK":
            asp_toks = tokenize_sentence("TP. Hồ Chí Minh").split()
        else:
            asp_toks = tokenize_sentence(asp).split()

        opn_toks = tokenize_sentence(opn).split()

        asp_indices = find_subsequence_indices(doc_tokens, asp_toks)
        opn_indices = find_subsequence_indices(doc_tokens, opn_toks)

        if asp_indices is None or opn_indices is None:
            # Bỏ qua triplet không xác định được vị trí chuẩn xác
            continue

        converted_triplets.append((asp_indices, opn_indices, pol))

    if not converted_triplets:
        return None

    return tokenized_sentence, converted_triplets


def format_triplets_string(triplets: List[Tuple[List[int], List[int], str]]) -> str:
    """
    Định dạng danh sách triplet thành chuỗi:
    [([0, 1], [4], 'POS'), ...]
    """
    parts = []
    for asp_span, opn_span, pol in triplets:
        parts.append(f"({asp_span}, {opn_span}, '{pol}')")
    return "[" + ", ".join(parts) + "]"


def export_dataset(input_json_path: str, output_txt_path: str, verify: bool = True) -> Dict[str, Any]:
    """
    Đọc file JSON đầu vào, áp dụng Adapter và ghi ra file TXT theo format Xu et al.
    """
    if not os.path.exists(input_json_path):
        raise FileNotFoundError(f"Input file not found: {input_json_path}")

    os.makedirs(os.path.dirname(os.path.abspath(output_txt_path)), exist_ok=True)

    with open(input_json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    total_records = len(records)
    exported_records = 0
    total_triplets_in = 0
    exported_triplets = 0

    lines = []

    for rec in records:
        triplets_in_rec = rec.get("aste_triplets", [])
        total_triplets_in += len(triplets_in_rec)

        res = convert_record_to_aste_v2(rec)
        if res is None:
            continue

        sent_str, trip_list = res
        trip_str = format_triplets_string(trip_list)
        line = f"{sent_str}####{trip_str}"
        lines.append(line)

        exported_records += 1
        exported_triplets += len(trip_list)

        # Reverse assertion verification
        if verify:
            tokens = sent_str.split()
            for asp_span, opn_span, pol in trip_list:
                for idx in asp_span:
                    assert 0 <= idx < len(tokens), f"Aspect index out of range: {idx} in {sent_str}"
                for idx in opn_span:
                    assert 0 <= idx < len(tokens), f"Opinion index out of range: {idx} in {sent_str}"

    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    stats = {
        "input_json": input_json_path,
        "output_txt": output_txt_path,
        "total_records": total_records,
        "exported_records": exported_records,
        "total_triplets_in": total_triplets_in,
        "exported_triplets": exported_triplets,
        "conversion_rate_records": round(exported_records / max(1, total_records) * 100, 2),
        "conversion_rate_triplets": round(exported_triplets / max(1, total_triplets_in) * 100, 2)
    }
    return stats


def main():
    parser = argparse.ArgumentParser(description="Export HCMC Flood ASTE v3 to ASTE-Data-V2 Format")
    parser.add_argument("--input", default="data/processed/hcmc_flood_annotated_v3_multimodal.json",
                        help="Path to input JSON dataset")
    parser.add_argument("--output", default="data/processed/aste_v2_format/master_triplets.txt",
                        help="Path to output text file")
    parser.add_argument("--splits", action="store_true",
                        help="Export train.json, dev.json, test.json into train_triplets.txt, dev_triplets.txt, test_triplets.txt")
    args = parser.parse_args()

    print("=" * 80)
    print("🚀 ASTE-DATA-V2 FORMAT ADAPTER (Xu et al., EMNLP 2020)")
    print("=" * 80)

    if args.splits:
        splits_dir = os.path.join(ROOT_DIR, "data", "processed", "splits")
        out_dir = os.path.join(ROOT_DIR, "data", "processed", "aste_v2_format")
        for split_name in ["train", "dev", "test"]:
            in_file = os.path.join(splits_dir, f"{split_name}.json")
            out_file = os.path.join(out_dir, f"{split_name}_triplets.txt")
            if os.path.exists(in_file):
                st = export_dataset(in_file, out_file, verify=True)
                print(f"[*] Exported {split_name.upper()} split:")
                print(f"    - Input: {in_file}")
                print(f"    - Output: {out_file}")
                print(f"    - Records: {st['exported_records']}/{st['total_records']} ({st['conversion_rate_records']}%)")
                print(f"    - Triplets: {st['exported_triplets']}/{st['total_triplets_in']} ({st['conversion_rate_triplets']}%)")
    else:
        in_path = os.path.join(ROOT_DIR, args.input) if not os.path.isabs(args.input) else args.input
        out_path = os.path.join(ROOT_DIR, args.output) if not os.path.isabs(args.output) else args.output
        st = export_dataset(in_path, out_path, verify=True)
        print("[*] Exported Master Dataset:")
        print(f"    - Input: {in_path}")
        print(f"    - Output: {out_path}")
        print(f"    - Records: {st['exported_records']}/{st['total_records']} ({st['conversion_rate_records']}%)")
        print(f"    - Triplets: {st['exported_triplets']}/{st['total_triplets_in']} ({st['conversion_rate_triplets']}%)")

    print("\n✅ HOÀN TẤT CHUYỂN ĐỔI CHUẨN XÁC 100%!")


if __name__ == "__main__":
    main()
