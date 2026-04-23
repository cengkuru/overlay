#!/usr/bin/env python3
"""audit_docx.py — standalone CLI for the pre-ship assurance gate.

Usage:
    python scripts/audit_docx.py ../01-review-letter.docx
    python scripts/audit_docx.py ../01-review-letter.docx --charts ../charts
    python scripts/audit_docx.py ../01-review-letter.docx --strict

Exits non-zero if any BLOCKER fires. With --strict, also fails on IMPORTANT.
"""
from __future__ import annotations
import argparse
import pathlib
import sys

# Make the build/ parent importable so `visuals` resolves.
_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from visuals.assurance import audit_docx, summarise  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="CoST DOCX pre-ship gate.")
    ap.add_argument("docx", type=pathlib.Path, help="Path to the .docx file.")
    ap.add_argument("--charts", type=pathlib.Path, default=None,
                    help="Charts directory (defaults to <docx>/../charts).")
    ap.add_argument("--strict", action="store_true",
                    help="Fail on IMPORTANT as well as BLOCKER.")
    args = ap.parse_args()

    charts_dir = args.charts
    if charts_dir is None:
        charts_dir = args.docx.resolve().parent / "charts"

    findings = audit_docx(args.docx, charts_dir)
    blockers, importants, minors = summarise(findings)

    if not findings:
        print(f"PASS {args.docx.name} — 0 findings.")
        return 0

    for f in findings:
        print(f)
    print()
    print(f"Summary: {blockers} BLOCKER, {importants} IMPORTANT, {minors} MINOR.")

    if blockers or (args.strict and importants):
        print("FAIL — gate blocked.")
        return 1
    print("PASS (with advisory findings).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
