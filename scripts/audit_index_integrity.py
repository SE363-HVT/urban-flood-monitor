"""Decode spans; use --expected to verify independently selected occurrences."""
if __package__:
    from .aste_audit_cli import main
else:
    from aste_audit_cli import main

if __name__ == '__main__':
    raise SystemExit(main(mode='index'))
