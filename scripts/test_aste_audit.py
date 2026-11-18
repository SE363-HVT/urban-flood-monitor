"""Regression tests for read-only validation and reviewed-span cross-checks.

Run: .venv/Scripts/python.exe -B -m unittest scripts.test_aste_audit -v
"""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.aste_audit_core import (LOCATIVE_PREPS, audit_file, compare_expected,
                                     inspect_line, summarize)
from scripts.span_helper import make_triplet, sanitize_span
from scripts.verify_batch_50 import inspect_sub_batch

ROOT = Path(__file__).resolve().parents[1]


def codes(record, level='ERROR'):
    return {i['code'] for i in record['issues'] if i['level'] == level}


def record(text, trips):
    return inspect_line(text + '####' + repr(trips), 1)


class AuditTests(unittest.TestCase):
    def test_one_token_locations_and_hydrology(self):
        for aspect in ['TPHCM', 'TP.HCM', 'ĐT743', 'nước', 'mưa']:
            with self.subTest(aspect=aspect):
                self.assertFalse(codes(record(aspect + ' ngập', [([0], [1], 'NEG')])))

    def test_all_locatives_single_and_multiple_tokens(self):
        for prep in LOCATIVE_PREPS:
            for indices in [[0], [0, 1]]:
                with self.subTest(prep=prep, indices=indices):
                    self.assertIn('PREP_LEAKAGE', codes(record(prep + ' TPHCM ngập', [(indices, [2], 'NEG')])))

    def test_malformed_inputs_are_reported(self):
        cases = [('', 'BLANK_LINE'), ('text', 'FORMAT_ERROR'), ('text####[]####[]', 'FORMAT_ERROR'),
                 ('text####[', 'SYNTAX_ERROR'), ('text####None', 'TRIPLETS_TYPE'),
                 ('text####{}', 'TRIPLETS_TYPE'), ('####[]', 'EMPTY_TEXT'),
                 ('text####[[[0], [0], "NEG"]]', 'TRIPLET_CONTAINER'),
                 ('text####[(1,)]', 'TRIPLET_SHAPE')]
        for text, code in cases:
            with self.subTest(text=text):
                self.assertIn(code, codes(inspect_line(text, 1)))

    def test_invalid_span_types_bounds_order(self):
        for span, code in [(None, 'SPAN_TYPE'), ((0,), 'SPAN_TYPE'), ([], 'EMPTY_SPAN'),
                           ([True], 'INDEX_TYPE'), ([0.0], 'INDEX_TYPE'), (['0'], 'INDEX_TYPE'),
                           ([-1], 'OUT_OF_BOUNDS'), ([99], 'OUT_OF_BOUNDS'),
                           ([0, 2], 'NON_CONTIGUOUS'), ([1, 0], 'NON_CONTIGUOUS'),
                           ([0, 0], 'NON_CONTIGUOUS')]:
            with self.subTest(span=span):
                self.assertIn(code, codes(record('TPHCM đang ngập', [(span, [2], 'NEG')])))

    def test_polarity_overlap_duplicate(self):
        for pol in ['BAD', None, [], {}]:
            self.assertIn('INVALID_POLARITY', codes(record('TPHCM ngập', [([0], [1], pol)])))
        self.assertIn('OVERLAP_INDEX', codes(record('Bình Tân ngập', [([0, 1], [1], 'NEG')])))
        trip = ([0], [1], 'NEG')
        self.assertIn('DUPLICATE_TRIPLET', codes(record('TPHCM ngập', [trip, trip])))

    def test_edge_symbols_and_internal_comma(self):
        for token in ['?', '…', '😰', '⚠️', '👩‍🚒', '1️⃣', '#️⃣', '\ufe0f', '\u200d']:
            self.assertIn('PUNCT_LEAKAGE', codes(record('TPHCM ngập ' + token, [([0], [1, 2], 'NEG')])))
        self.assertFalse(codes(record('TP.HCM ngập sâu , nước chảy xiết', [([0], list(range(1, 7)), 'NEG')])))

    def test_numeric_and_named_tokens_are_not_punctuation(self):
        from scripts.aste_audit_core import is_edge_punctuation
        for token in ['1', '12', '1m70', '30/4', '0,2', 'TP.HCM', 'ĐT743']:
            with self.subTest(token=token):
                self.assertFalse(is_edge_punctuation(token))

    def test_summary_counts_findings_and_distinct_lines_separately(self):
        rows = [record('ở ngập', [([0], [0], 'BAD')]), record('TPHCM ngập', [([0], [1], 'NEG')])]
        summary = summarize(rows)
        self.assertEqual(summary['error_records'], 1)
        self.assertGreater(summary['errors'], summary['error_records'])

    def test_explicit_policy(self):
        for asp, code in [('CSGT', 'PEOPLE_ASPECT'), ('xe máy', 'VEHICLE_ASPECT'),
                           ('con đường', 'GENERIC_ASPECT'), ('triều cường', 'BARE_TIDE_ASPECT')]:
            words = asp.split()
            self.assertIn(code, codes(record(asp + ' ngập', [(list(range(len(words))), [len(words)], 'NEG')])))
        self.assertIn('CAUSATIVE_VERB', codes(record('TPHCM gây ngập', [([0], [1, 2], 'NEG')])))
        self.assertIn('BARE_NOUN_AS_OPINION', codes(record('TPHCM điểm ngập', [([0], [1, 2], 'NEG')])))

    def test_context_never_auto_rejects(self):
        for text, trips in [
            ('Dĩ An ngập', [([0, 1], [2], 'NEG')]),
            ('Vũng Tàu ngập', [([0, 1], [2], 'NEG')]),
            ('Bình Tân ngập #bentre', [([0, 1], [2], 'NEG')]),
            ('TPHCM ngập còn Hà Nội khô', [([0], [1], 'NEG')]),
            ('TPHCM ngập như sông', [([0], [1, 2, 3], 'NEG')]),
            ('TPHCM sẽ nạo vét', [([0], [1, 2, 3], 'POS')]),
        ]:
            with self.subTest(text=text):
                r = record(text, trips)
                self.assertFalse(codes(r))
                self.assertFalse(r['rejected'])
                self.assertEqual(len(r['triplets']), len(trips))
        rejected = record('TPHCM dự báo ngập', [])
        self.assertIn('REJECT_DECISION', codes(rejected, 'REVIEW'))
        self.assertFalse(codes(rejected))

    def test_physical_lines_bom_ranges_read_only(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'data.txt'
            p.write_text('TPHCM ngập####[([0], [1], "NEG")]\r\n\r\nx####[]\r\n', encoding='utf-8-sig', newline='')
            original = p.read_bytes()
            rows = audit_file(p)
            self.assertEqual([r['rec'] for r in rows], [1, 2, 3])
            self.assertIn('BLANK_LINE', codes(rows[1]))
            self.assertEqual(inspect_sub_batch(p, 2, 100)[0]['rec'], 3)
            for start, end in [(-1, 2), (1, 1), (4, 5)]:
                with self.assertRaises(ValueError):
                    audit_file(p, start, end)
            self.assertEqual(p.read_bytes(), original)

    def test_later_records_survive_bad_input(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'data.txt'
            p.write_text('x####[([99], [0], "NEG")]\nx####[\nx y####[([0], [1], "POS")]\n', encoding='utf-8')
            rows = audit_file(p)
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[2]['triplets'][0]['opi'], 'y')

    def test_legacy_list_triplets_still_checked(self):
        r = record('ở TPHCM ngập', [[[0], [2], 'NEG']])
        self.assertIn('TRIPLET_CONTAINER', codes(r))
        self.assertIn('PREP_LEAKAGE', codes(r))
        self.assertEqual(r['triplets'][0]['asp'], 'ở')

    def test_generic_road_is_not_a_specific_road_warning(self):
        r = record('TPHCM nhiều tuyến đường ngập', [([0], [4], 'NEG')])
        self.assertNotIn('FALLBACK_CONTEXT', codes(r, 'REVIEW'))
        r = record('TPHCM đường Tam Bình ngập', [([0], [4], 'NEG')])
        self.assertIn('FALLBACK_CONTEXT', codes(r, 'REVIEW'))


class HelperAndExpectedTests(unittest.TestCase):
    def test_invalid_phrase_types_raise_clear_errors(self):
        for text, aspect, opinion in [(None, 'x', 'y'), ('x y', None, 'y'), ('x y', 'x', ['y'])]:
            with self.assertRaises(ValueError):
                make_triplet(text, aspect, opinion, 'NEG')

    def test_explicit_opinion_occurrence_and_exact_indices(self):
        text = 'TPHCM ngập rồi ngập sâu'
        with self.assertRaises(ValueError):
            make_triplet(text, 'TPHCM', 'ngập', 'NEG')
        self.assertEqual(make_triplet(text, 'TPHCM', 'ngập', 'NEG', opi_occurrence=1), ([0], [3], 'NEG'))
        text = 'đường Nguyễn Văn Hưởng đang ngập sâu khoảng nửa mét'
        self.assertEqual(make_triplet(text, 'đường Nguyễn Văn Hưởng', 'đang ngập sâu khoảng nửa mét', 'NEG'),
                         ([0, 1, 2, 3], [4, 5, 6, 7, 8, 9], 'NEG'))

    def test_repeated_phrases_require_explicit_occurrence(self):
        text = 'TPHCM ngập , TPHCM hết ngập'
        with self.assertRaises(ValueError):
            make_triplet(text, 'TPHCM', 'hết ngập', 'POS')
        self.assertEqual(make_triplet(text, 'TPHCM', 'hết ngập', 'POS', asp_occurrence=1), ([3], [4, 5], 'POS'))
        self.assertEqual(make_triplet(text, 'TPHCM', 'hết ngập', 'POS', asp_start=3)[0], [3])
        for kw in [{'asp_start': -1}, {'asp_occurrence': True}, {'asp_start': 0, 'asp_occurrence': 0}]:
            with self.assertRaises(ValueError):
                make_triplet(text, 'TPHCM', 'hết ngập', 'POS', **kw)

    def test_no_silent_trimming_or_case_substitution(self):
        for asp, opi in [('ở TPHCM', 'ngập'), ('TPHCM', 'ngập !'), ('tphcm', 'ngập')]:
            with self.assertRaises(ValueError):
                make_triplet('ở TPHCM ngập !', asp, opi, 'NEG')
        self.assertEqual(make_triplet('khu dân cư ngập', 'khu dân cư', 'ngập', 'NEG')[0], [0, 1, 2])
        self.assertEqual(sanitize_span('ở TPHCM ngập'.split(), [0, 1]), [1])
        with self.assertRaises(ValueError):
            make_triplet('TPHCM ngập', 'TPHCM', 'TPHCM ngập', 'NEG')

    def test_expected_catches_wrong_words_and_occurrences(self):
        text = 'TPHCM ngập , TPHCM hết ngập'
        expected = {'1': {'text': text, 'triplets': [
            {'asp': 'TPHCM', 'asp_start': 3, 'opi': 'hết ngập', 'opi_start': 4, 'pol': 'POS'}]}}
        wrong = record(text, [([0], [4, 5], 'POS')])
        self.assertFalse(codes(wrong))  # Valid indices do not prove correct binding.
        compare_expected([wrong], expected)
        self.assertIn('EXPECTED_MISMATCH', codes(wrong))
        correct = record(text, [([3], [4, 5], 'POS')])
        compare_expected([correct], expected)
        self.assertFalse(codes(correct))
        changed = record('Tại ' + text, [([4], [5, 6], 'POS')])
        compare_expected([changed], expected)
        self.assertIn('EXPECTED_TEXT', codes(changed))
        missing = record(text, [])
        compare_expected([missing], expected)
        self.assertIn('EXPECTED_MISMATCH', codes(missing))

    def test_expected_schema_and_missing_coverage(self):
        for expected in [{}, {'1': {}}, {'1': {'text': 'x y', 'triplets': None}},
                         {'1': {'text': 'x y', 'triplets': [{'asp': 'x', 'asp_start': True,
                           'opi': 'y', 'opi_start': 1, 'pol': 'NEG'}]}}]:
            r = record('x y', [([0], [1], 'NEG')])
            compare_expected([r], expected)
            self.assertIn('EXPECTED_SCHEMA', codes(r))


class CliTests(unittest.TestCase):
    def test_duplicate_expected_decisions_and_fields_are_rejected(self):
        from scripts.aste_audit_cli import main
        payloads = ['{"1": {}, "1": {"text": "x", "triplets": []}}',
                    '{"1": {"text": "wrong", "text": "x", "triplets": []}}']
        with tempfile.TemporaryDirectory() as td, contextlib.redirect_stdout(io.StringIO()):
            path = Path(td) / 'data.txt'
            expected = Path(td) / 'expected.json'
            path.write_text('x####[]', encoding='utf-8')
            for payload in payloads:
                expected.write_text(payload, encoding='utf-8')
                self.assertEqual(main([str(path), '--expected', str(expected), '--json']), 2)

    def test_entry_points_exit_json_and_source_unchanged(self):
        cases = [
            ('valid', 'TPHCM ngập####[([0], [1], "NEG")]', 0),
            ('bounds', 'TPHCM ngập####[([0], [99], "NEG")]', 1),
            ('single_prep', 'ở TPHCM ngập####[([0], [2], "NEG")]', 1),
            ('overlap', 'TPHCM ngập####[([0], [0, 1], "NEG")]', 1),
            ('bad_pol', 'TPHCM ngập####[([0], [1], "BAD")]', 1),
            ('syntax', 'x####[\nx y####[([0], [1], "NEG")]', 1),
        ]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'data.txt'
            for case, body, code in cases:
                path.write_text(body, encoding='utf-8')
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                for script in ['deep_10_pass_audit.py', 'audit_index_integrity.py', 'verify_batch_50.py']:
                    with self.subTest(case=case, script=script):
                        cmd = [sys.executable, '-B', str(ROOT / 'scripts' / script), str(path)]
                        if script.startswith('verify'):
                            cmd += ['0', '50']
                        result = subprocess.run(cmd + ['--json'], capture_output=True, encoding='utf-8', cwd=td)
                        self.assertEqual(result.returncode, code, result.stderr)
                        output = json.loads(result.stdout)
                        self.assertEqual(output['exit_code'], code)
                        self.assertEqual(output['summary']['semantic_status'], 'NOT_CERTIFIED')
                        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)

    def test_input_errors_reviews_and_expected_cli(self):
        from scripts.aste_audit_cli import main
        with tempfile.TemporaryDirectory() as td, contextlib.redirect_stdout(io.StringIO()):
            p = Path(td) / 'data.txt'
            self.assertEqual(main([str(p), '--json']), 2)
            p.write_text('', encoding='utf-8')
            self.assertEqual(main([str(p), '--json']), 2)
            p.write_text('x####[]', encoding='utf-8')
            self.assertEqual(main([str(p), '--json']), 0)
            self.assertEqual(main([str(p), '--json', '--fail-on-review']), 1)
            exp = Path(td) / 'expected.json'
            exp.write_text(json.dumps({'1': {'text': 'x', 'triplets': []}}), encoding='utf-8')
            self.assertEqual(main([str(p), '--json', '--expected', str(exp)]), 0)


if __name__ == '__main__':
    unittest.main()
