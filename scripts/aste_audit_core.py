"""Read-only ASTE rules. ERROR = explicit violation; REVIEW = contextual evidence.

Policy: documents/BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md.
No automatic relabel/reject and no claim of semantic certification.
"""
from collections import Counter
from pathlib import Path
import ast
import re
import unicodedata

POLARITIES = frozenset({'POS', 'NEG', 'NEU'})
LOCATIVE_PREPS = frozenset('ở tại trên dưới trong ngoài từ đến gần cạnh bên phía thuộc của'.split())
VEHICLES = frozenset({'xe', 'xe máy', 'ô tô', 'xe buýt', 'xe tải', 'phương tiện',
                      'thuyền', 'ghe', 'ca nô', 'xe gắn máy', 'ô-tô', 'xe-máy'})
PEOPLE = frozenset({'người dân', 'tài xế', 'bà con', 'cụ bà', 'chị oanh', 'lực lượng chức năng', 'csgt'})
GENERIC_ASPECTS = frozenset({'mặt đường', 'đoạn đường', 'con đường', 'chân cầu',
                            'cư xá', 'làn nước ngập', 'nâng nền', 'dòng nước'})
BARE_OPINIONS = frozenset({'điểm ngập', 'đoạn ngập', 'vùng ngập', 'tuyến ngập', 'khu vực ngập', 'mực nước'})
BARE_TIDES = frozenset({'triều cường', 'đỉnh triều', 'triều cao'})
CITY_ASPECTS = frozenset({'tp. hồ chí minh', 'tp. hcm', 'tphcm', 'tp.hcm',
                         'tp hồ chí minh', 'tp hcm', 'sài gòn', 'thành phố'})
INFRA_PREFIXES = frozenset({'đường', 'cầu', 'hầm', 'kênh', 'sông'})
GENERIC_ROAD_FOLLOWERS = frozenset('này đó kia nào vừa qua lớn tp tp. tphcm tp.hcm hcm sài hồ ngập phố xá hóa thành biến hỗ về nhớ ở tại chìm lại nước như trong ngoài bị đã đang sẽ trũng thấp thủy bộ'.split())
CAUSATIVE = re.compile(r'^(?:gây ra|gây|làm)\s+(?:ngập\b|tăng nguy cơ ngập\b)')
OUTSIDE_CUES = re.compile(r'\b(?:hà nội|cần thơ|cà mau|đồng nai|sa đéc|bangkok|thái lan)\b|#(?:hanoi|cantho|bentre)\b')
GROUPS = {
    1: 'Format / syntax / schema', 2: 'Index type / empty / bounds / continuity',
    3: 'Aspect-opinion overlap', 4: 'Edge punctuation / emoji', 5: 'Aspect prepositions',
    6: 'Polarity / duplicate triplets', 7: 'Explicit aspect and opinion rules',
    8: 'Contextual semantic review', 9: 'Fallback / geography / reject / duplication review',
    10: 'Agent expectations / exact occurrence cross-check',
}


def is_edge_punctuation(token):
    """Standalone symbols, punctuation, emoji incl. variation selectors and ZWJ.

    Attached punctuation in TP.HCM, 30/4, etc. is not a separate token.
    """
    cats = [unicodedata.category(c) for c in token]
    # Emoji keycaps contain a digit (Nd), so category P/S alone misses them.
    if token and token[0] in '0123456789#*' and token[1:] in ('\u20e3', '\ufe0f\u20e3'):
        return True
    # Detached variation selectors/combining marks/ZWJ are not meaningful words.
    if cats and all(c[0] == 'M' or c == 'Cf' for c in cats):
        return True
    return bool(cats) and any(c[0] in 'PS' for c in cats) and all(
        c[0] in 'PSM' or c == 'Cf' for c in cats)


def span_problem(tokens, span):
    if not isinstance(span, list):
        return 'SPAN_TYPE', 'Span must be a list of integers.'
    if not span:
        return 'EMPTY_SPAN', 'Span cannot be empty inside a triplet.'
    if any(type(i) is not int for i in span):
        return 'INDEX_TYPE', 'Index must be int; bool/float/string are invalid.'
    if any(i < 0 or i >= len(tokens) for i in span):
        return 'OUT_OF_BOUNDS', f'Expected 0 <= index < {len(tokens)}; got {span!r}.'
    if span != list(range(span[0], span[-1] + 1)):
        return 'NON_CONTIGUOUS', f'Indices must increase consecutively: {span!r}.'
    return None


def inspect_line(line, line_number):
    item = {'rec': line_number, 'text': '', 'tokens': [], 'triplets': [], 'issues': [], 'rejected': False}

    def add(level, code, message, group, triplet=None):
        item['issues'].append({'level': level, 'code': code, 'message': message,
                               'group': group, 'triplet': triplet})

    if not line.strip():
        add('ERROR', 'BLANK_LINE', 'Blank physical line; do not drop/renumber records.', 1)
        return item
    if line.count('####') != 1:
        add('ERROR', 'FORMAT_ERROR', 'Expected exactly one #### separator.', 1)
        return item
    text, literal = line.split('####')
    item.update(text=text, tokens=text.split())
    tokens = item['tokens']
    if not tokens:
        add('ERROR', 'EMPTY_TEXT', 'Text cannot be empty, including rejected records.', 1)
    try:
        triplets = ast.literal_eval(literal.strip())
    except (SyntaxError, ValueError, TypeError, RecursionError) as exc:
        add('ERROR', 'SYNTAX_ERROR', str(exc), 1)
        return item
    if not isinstance(triplets, list):
        add('ERROR', 'TRIPLETS_TYPE', 'Annotation must be a list, including [].', 1)
        return item
    item['rejected'] = triplets == []
    if item['rejected']:
        add('REVIEW', 'REJECT_DECISION', 'Read the whole text: [] does not prove rejection is appropriate.', 9)
    seen = set()
    for number, trip in enumerate(triplets, 1):
        if not isinstance(trip, (tuple, list)) or len(trip) != 3:
            add('ERROR', 'TRIPLET_SHAPE', 'Expected ([aspect indices], [opinion indices], polarity) tuple.', 1, number)
            continue
        if isinstance(trip, list):
            # Legacy JSON-like triplets are decoded too, so format errors never
            # hide bad indices. Canonical output remains tuple per section II.
            add('ERROR', 'TRIPLET_CONTAINER', 'Legacy list triplet: canonical cẩm nang format requires a tuple; indices still checked.', 1, number)
        aspect, opinion, polarity = trip
        if not isinstance(polarity, str) or polarity not in POLARITIES:
            add('ERROR', 'INVALID_POLARITY', f'Expected POS/NEG/NEU, got {polarity!r}.', 6, number)
        valid_spans = True
        for name, span in [('Aspect', aspect), ('Opinion', opinion)]:
            problem = span_problem(tokens, span)
            if problem:
                add('ERROR', problem[0], name + ': ' + problem[1], 2, number)
                valid_spans = False
        if not valid_spans:
            continue  # Never dereference malformed spans; continue with later data.
        asp = ' '.join(tokens[i] for i in aspect)
        opi = ' '.join(tokens[i] for i in opinion)
        al, ol = asp.casefold(), opi.casefold()
        item['triplets'].append({'asp': asp, 'asp_idx': aspect, 'opi': opi,
                                 'opi_idx': opinion, 'pol': polarity, 'number': number})
        if set(aspect) & set(opinion):
            add('ERROR', 'OVERLAP_INDEX', f'Aspect/opinion overlap: {sorted(set(aspect) & set(opinion))}.', 3, number)
        for name, span in [('Aspect', aspect), ('Opinion', opinion)]:
            if is_edge_punctuation(tokens[span[0]]) or is_edge_punctuation(tokens[span[-1]]):
                add('ERROR', 'PUNCT_LEAKAGE', f'{name} has standalone punctuation/emoji at an edge.', 4, number)
        if tokens[aspect[0]].casefold() in LOCATIVE_PREPS:
            add('ERROR', 'PREP_LEAKAGE', f'Aspect starts with {tokens[aspect[0]]!r}; one-token locations remain valid.', 5, number)
        key = (tuple(aspect), tuple(opinion), repr(polarity))
        if key in seen:
            add('ERROR', 'DUPLICATE_TRIPLET', 'Identical triplet repeated.', 6, number)
        seen.add(key)
        for invalid, code in [(VEHICLES, 'VEHICLE_ASPECT'), (PEOPLE, 'PEOPLE_ASPECT'), (GENERIC_ASPECTS, 'GENERIC_ASPECT')]:
            if al in invalid:
                add('ERROR', code, f'Explicitly disallowed standalone aspect: {asp!r}.', 7, number)
        if al in BARE_TIDES and polarity in ('NEU', 'NEG'):
            add('ERROR', 'BARE_TIDE_ASPECT', 'Apply III.2.6 manually; after approved text insertion, recalculate indices.', 7, number)
        if ol in BARE_OPINIONS:
            add('ERROR', 'BARE_NOUN_AS_OPINION', f'Bare nominal opinion: {opi!r}.', 7, number)
        if CAUSATIVE.match(ol):
            add('ERROR', 'CAUSATIVE_VERB', 'Opinion includes a leading causal verb; see IV.1.5.', 7, number)
        if tokens[aspect[-1]].casefold() in {'nha', 'ạ', 'nè'}:
            add('REVIEW', 'ASPECT_PARTICLE', 'Check a trailing particle after the infrastructure name.', 8, number)
        if aspect[0] and tokens[aspect[0] - 1].casefold() in INFRA_PREFIXES:
            add('REVIEW', 'INFRA_PREFIX', 'Check whether the preceding infrastructure prefix belongs to this name (III.2.8).', 8, number)
        if any(t in {'"', '“', '”', ':', '…', '...'} for t in tokens[opinion[0]:opinion[-1]+1]):
            add('REVIEW', 'SEMANTIC_BOUNDARY', 'Check quotes, explanations, metadata and semantic stopping rules (IV.1.6).', 8, number)
        if opinion[0] and tokens[opinion[0] - 1].casefold() in {'không', 'chưa', 'đã', 'đang', 'vẫn', 'bắt', 'sẽ'}:
            add('REVIEW', 'OPINION_LEFT_CONTEXT', 'Check omitted negation, tense or state before the opinion.', 8, number)
        if polarity == 'NEG' and re.search(r'\b(?:dự báo|nguy cơ|có thể|sẽ|rút|khô ráo|hết ngập)\b', text.casefold()):
            add('REVIEW', 'POLARITY_CONTEXT', 'NEG with forecast/recovery cues: read the full clause; no automatic change.', 8, number)
        road_candidate = any(
            word.casefold() == 'đường' and tokens[i+1].casefold() not in GENERIC_ROAD_FOLLOWERS
            and (tokens[i+1][0].isupper() or tokens[i+1][0].isdigit())
            for i, word in enumerate(tokens[:-1]))
        if al in CITY_ASPECTS and road_candidate:
            add('REVIEW', 'FALLBACK_CONTEXT', 'Check for a specific road/locality; never reject to bypass this warning.', 9, number)
    if triplets and OUTSIDE_CUES.search(text.casefold()):
        add('REVIEW', 'GEOGRAPHY_CONTEXT', 'Check event location vs hometown hashtags; never auto-reject by keywords.', 9)
    by_opinion = Counter(tuple(t['opi_idx']) for t in item['triplets'])
    if any(count > 1 for count in by_opinion.values()):
        add('REVIEW', 'SHARED_OPINION', 'Check complete street enumeration vs city/ward/road over-tagging.', 8)
    return item


def audit_file(filepath, start=0, end=None):
    """Range [start, end) counts physical lines; preserve blank lines and IDs."""
    # splitlines() would also split U+2028/U+2029 inside a social-media record.
    # Read actual file lines so record numbers stay aligned with annotators.
    with Path(filepath).open(encoding='utf-8-sig') as stream:
        lines = [line.rstrip('\r\n') for line in stream]
    if type(start) is not int or start < 0 or (end is not None and (type(end) is not int or end <= start)):
        raise ValueError('Expected 0 <= start < end (end exclusive).')
    if not lines:
        raise ValueError('Dataset is empty.')
    if start >= len(lines):
        raise ValueError(f'Start {start} is outside the {len(lines)} physical lines.')
    stop = min(end if end is not None else len(lines), len(lines))
    records = [inspect_line(lines[i], i + 1) for i in range(start, stop)]
    seen_text = {}
    for rec in records:
        text = rec['text']
        if text and text in seen_text:
            rec['issues'].append({'level': 'REVIEW', 'code': 'DUPLICATE_TEXT',
                                  'message': f'Same text as line {seen_text[text]}; preserve alignment, review split leakage.',
                                  'group': 9, 'triplet': None})
        seen_text.setdefault(text, rec['rec'])
    return records


def compare_expected(records, expected):
    """Compare independently chosen phrases AND starts, bound to exact final text.

    JSON: {"1": {"text": "...", "triplets": [{"asp": "TPHCM", "asp_start": 0,
      "opi": "ngập", "opi_start": 1, "pol": "NEG"}]}}
    Requires expectations for all selected records, allows entries outside range.
    """
    if not isinstance(expected, dict):
        raise ValueError('Expected manifest must be a JSON object keyed by physical line number.')
    for rec in records:
        def error(code, message):
            rec['issues'].append({'level': 'ERROR', 'code': code, 'message': message, 'group': 10, 'triplet': None})
        entry = expected.get(str(rec['rec']))
        if not isinstance(entry, dict) or set(entry) != {'text', 'triplets'}:
            error('EXPECTED_SCHEMA', 'Require text and triplets for every selected line.')
            continue
        if entry['text'] != rec['text']:
            error('EXPECTED_TEXT', 'Final text differs from reviewed text; recalculate indices after text changes.')
            continue
        if not isinstance(entry['triplets'], list):
            error('EXPECTED_SCHEMA', 'Expected triplets must be a list.')
            continue
        signatures, valid = [], True
        for chosen in entry['triplets']:
            if (not isinstance(chosen, dict) or set(chosen) != {'asp', 'asp_start', 'opi', 'opi_start', 'pol'}
                    or not isinstance(chosen['pol'], str) or chosen['pol'] not in POLARITIES):
                valid = False
                break
            spans = []
            for field in ('asp', 'opi'):
                phrase, first = chosen[field], chosen[field + '_start']
                if not isinstance(phrase, str) or not phrase.split() or type(first) is not int:
                    valid = False
                    break
                words = phrase.split()
                span = list(range(first, first + len(words)))
                if span_problem(rec['tokens'], span) or rec['tokens'][first:first + len(words)] != words:
                    valid = False
                    break
                spans.append(tuple(span))
            if not valid:
                break
            signatures.append((*spans, chosen['pol']))
        if not valid or len(set(signatures)) != len(signatures):
            error('EXPECTED_SCHEMA', 'Expected phrase/start/polarity invalid or duplicated; check independent review.')
            continue
        actual = [(tuple(t['asp_idx']), tuple(t['opi_idx']), t['pol']) for t in rec['triplets']]
        if sorted(map(repr, actual)) != sorted(map(repr, signatures)):
            error('EXPECTED_MISMATCH', 'Mismatch with reviewed phrases/occurrences/polarities, including missing/extra triplets or reject.')


def summarize(records):
    issues = [i for r in records for i in r['issues']]
    return {'records': len(records), 'decoded_triplets': sum(len(r['triplets']) for r in records),
            'rejected_records': sum(r['rejected'] for r in records),
            'errors': sum(i['level'] == 'ERROR' for i in issues),
            'reviews': sum(i['level'] == 'REVIEW' for i in issues),
            'error_records': sum(any(i['level'] == 'ERROR' for i in r['issues']) for r in records),
            'review_records': sum(any(i['level'] == 'REVIEW' for i in r['issues']) for r in records),
            'by_code': dict(Counter(i['code'] for i in issues)), 'semantic_status': 'NOT_CERTIFIED'}
