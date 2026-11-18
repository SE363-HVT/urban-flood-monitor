"""Read-only batch validation; CLI ranges retain original [start, end) syntax."""
if __package__:
    from .aste_audit_core import audit_file
    from .aste_audit_cli import main
else:
    from aste_audit_core import audit_file
    from aste_audit_cli import main


def inspect_sub_batch(filepath, start_idx, end_idx):
    records = audit_file(filepath, start_idx, end_idx)
    for rec in records:
        rec['flaws'] = [f"{i['code']}: {i['message']}" for i in rec['issues'] if i['level'] == 'ERROR']
        rec['status'] = ('FLAWED' if rec['flaws'] else
                         'REJECTED_UNREVIEWED' if rec['rejected'] else 'STRUCTURE_OK')
    return records


if __name__ == '__main__':
    raise SystemExit(main(mode='batch'))
