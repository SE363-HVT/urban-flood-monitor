"""Shared CLI presentation for the three historical auditor entry points."""
import argparse
import json
from pathlib import Path
import sys

if __package__:
    from .aste_audit_core import GROUPS, audit_file, compare_expected, summarize
else:
    from aste_audit_core import GROUPS, audit_file, compare_expected, summarize

ROOT = Path(__file__).resolve().parents[1]


def unique_json_object(pairs):
    """Reject duplicate decisions/fields rather than silently taking the last."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key in expected manifest: {key!r}.')
        result[key] = value
    return result


def main(argv=None, *, mode='deep'):
    # Windows redirected stdout defaults to a legacy code page. Keep reports UTF-8
    # without changing global streams merely by importing the module.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description='Read-only ASTE audit; semantic correctness requires full-context review.')
    parser.add_argument('paths', nargs='*', help='[file] for full audit; [file] start end for batch ([start,end), zero based).')
    parser.add_argument('--expected', type=Path, help='Reviewed phrase/start manifest bound to final text (JSON).')
    parser.add_argument('--json', action='store_true', help='Complete JSON on stdout; never writes dataset.')
    parser.add_argument('--show-tokens', action='store_true', help='Print token indices and decoded triplets for all selected lines.')
    parser.add_argument('--fail-on-review', action='store_true', help='Return 1 for review warnings as well as errors.')
    parser.add_argument('--max-details', type=int, default=30, help='Human-readable limit; --json includes all issues.')
    args = parser.parse_args(argv)
    if args.max_details < 0:
        parser.error('--max-details must be >= 0.')
    default = ROOT / 'data/validate_label/thuan' / ('phase3.txt' if mode == 'deep' else 'phase1.txt')
    paths = args.paths
    start, end = 0, None
    try:
        if mode == 'batch':
            if len(paths) not in (2, 3):
                parser.error('Batch syntax: [file] start end.')
            filepath = Path(paths[0]) if len(paths) == 3 else default
            start, end = map(int, paths[-2:])
        else:
            if len(paths) > 1:
                parser.error('Expected at most one dataset file.')
            filepath = Path(paths[0]) if paths else default
        records = audit_file(filepath, start, end)
        if args.expected:
            compare_expected(records, json.loads(args.expected.read_text(encoding='utf-8-sig'),
                                                 object_pairs_hook=unique_json_object))
    except (OSError, UnicodeError, ValueError) as exc:
        if args.json:
            print(json.dumps({'input_error': str(exc), 'exit_code': 2}, ensure_ascii=False))
        else:
            print(f'INPUT_ERROR: {exc}', file=sys.stderr)
        return 2
    summary = summarize(records)
    exit_code = int(bool(summary['errors'] or (args.fail_on_review and summary['reviews'])))
    report = {'file': str(filepath), 'summary': summary, 'expectations_checked': bool(args.expected),
              'exit_code': exit_code, 'records': records}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return exit_code
    print(f'ASTE READ-ONLY AUDIT: {filepath}')
    print(f"Physical lines {records[0]['rec']}..{records[-1]['rec']}; records={summary['records']}; "
          f"decoded triplets={summary['decoded_triplets']}; []={summary['rejected_records']}")
    if mode == 'deep':
        for group, label in GROUPS.items():
            issues = [i for r in records for i in r['issues'] if i['group'] == group]
            errors = sum(i['level'] == 'ERROR' for i in issues)
            print(f'GROUP {group:02d}: {label}: errors={errors}, reviews={len(issues)-errors}')
    print(f"ERROR={summary['errors']}; REVIEW={summary['reviews']}; exit={exit_code}")
    print(f"Distinct lines: with ERROR={summary['error_records']}, with REVIEW={summary['review_records']} (may overlap).")
    print('Codes: ' + json.dumps(summary['by_code'], ensure_ascii=False, sort_keys=True))
    shown = 0
    for rec in records:
        if args.show_tokens:
            print(f"LINE {rec['rec']}: " + ' | '.join(f'{i}:{t}' for i, t in enumerate(rec['tokens'])))
            print('  Triplets: ' + repr(rec['triplets']))
        for issue in rec['issues']:
            if shown < args.max_details:
                print(f"LINE {rec['rec']} triplet={issue['triplet']}: {issue['level']} {issue['code']}: {issue['message']}")
                print('  TEXT: ' + rec['text'])
                print('  DECODED: ' + repr(rec['triplets']))
                shown += 1
    total_issues = summary['errors'] + summary['reviews']
    if total_issues > shown:
        print(f'{total_issues-shown} further issues; use --json or increase --max-details.')
    print('Expectations: ' + ('CHECKED against provided reviewed phrases/starts.' if args.expected else
                              'NOT PROVIDED; decoding is not proof of the intended phrase/occurrence.'))
    print('No automatic relabel/reject. ERROR=0 only means implemented checks found no errors.')
    print('Full-context semantic review is required for EVERY record, even without REVIEW warnings.')
    print('Entry points share one validator; they are not independent semantic reviewers.')
    return exit_code
