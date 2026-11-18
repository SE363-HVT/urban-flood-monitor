"""Ten validation groups; shared read-only rules, not ten semantic approvals."""
if __package__:
    from .aste_audit_cli import main
else:
    from aste_audit_cli import main

if __name__ == '__main__':
    raise SystemExit(main(mode='deep'))
