"""Derive a structural schema from a golden DOCX.

Given the current sample outputs as the quality bar, this tool reads
each DOCX and emits a YAML fragment describing the structural features
that every future country package must also have. The output is pasted
under the `schema` key in the package's `package.yaml`.

Usage:
    python3 auto/tools/derive_schema.py \\
        --docx samples/zambia-2026-04/01-review-and-reference.docx \\
        --docx samples/zambia-2026-04/02-sample-final-report.docx
"""
from __future__ import annotations
import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List

HERE = pathlib.Path(__file__).resolve().parent
AUTO = HERE.parent
if str(AUTO) not in sys.path:
    sys.path.insert(0, str(AUTO))

try:
    import yaml
except ImportError:
    yaml = None

from docx import Document

from snapshot import _flatten_body


def _table_signatures(doc) -> List[Dict[str, Any]]:
    sigs: List[Dict[str, Any]] = []
    for i, t in enumerate(doc.tables):
        rows = len(t.rows)
        cols = len(t.columns)
        header = [c.text.strip() for c in t.rows[0].cells] if rows else []
        # Short header (first 3 words of first cell) — used as a stable
        # identifier for this table across countries where the full
        # content may vary.
        first_cell_head = (header[0] if header else "").split()[:4]
        sigs.append({
            "index": i,
            "rows": rows,
            "cols": cols,
            "header": header,
            "first_cell_starts_with": " ".join(first_cell_head),
        })
    return sigs


def _required_headings(paragraphs) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for p in paragraphs:
        if not p.heading_level:
            continue
        out.append({
            "level": p.heading_level,
            "text": p.text.strip(),
        })
    return out


def derive_one(docx_path: pathlib.Path) -> Dict[str, Any]:
    d = Document(str(docx_path))
    paras, breaks, rows = _flatten_body(d)
    n_images = sum(1 for r in d.part._rels.values()
                   if "image" in r.reltype)
    return {
        "file": docx_path.name,
        "required_headings": _required_headings(paras),
        "required_tables": _table_signatures(d),
        "required_image_count": n_images,
        "page_break_count": breaks,
        "table_row_total": rows,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docx", action="append", required=True,
                    help="repeat for each output DOCX")
    ap.add_argument("--format", choices=["yaml", "json"], default="yaml")
    args = ap.parse_args()

    out = {"schema": {}}
    for path_str in args.docx:
        path = pathlib.Path(path_str)
        if not path.exists():
            print(f"missing: {path}", file=sys.stderr)
            sys.exit(2)
        out["schema"][path.stem] = derive_one(path)

    if args.format == "json" or yaml is None:
        print(json.dumps(out, indent=2))
    else:
        print(yaml.safe_dump(out, sort_keys=False, width=120,
                             allow_unicode=True, default_flow_style=False))


if __name__ == "__main__":
    main()
