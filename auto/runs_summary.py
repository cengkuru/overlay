"""Summarize history.jsonl into a learning report.

Usage:
    python3 auto/runs_summary.py                # write runs/summary.md
    python3 auto/runs_summary.py --last 50
"""
from __future__ import annotations
import argparse
import json
import pathlib
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List


def _load(runs_dir: pathlib.Path, last: int = 0) -> List[Dict[str, Any]]:
    p = runs_dir / "history.jsonl"
    if not p.exists():
        return []
    rows = [json.loads(ln) for ln in p.read_text().splitlines() if ln.strip()]
    return rows[-last:] if last else rows


def summarise(records: Iterable[Dict[str, Any]]) -> str:
    rows = list(records)
    if not rows:
        return "# Overlay learning summary\n\n_No runs logged yet._\n"

    total = len(rows)
    accepted = [r for r in rows if r.get("accepted")]
    rejected = [r for r in rows if not r.get("accepted")]

    by_class: Dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        cls = r.get("mutation_class") or "NONE"
        by_class[cls]["total"] += 1
        by_class[cls]["accepted" if r.get("accepted") else "rejected"] += 1

    # Gain per second where we have timing info
    gains_per_sec: Dict[str, List[float]] = defaultdict(list)
    for r in accepted:
        rt = (r.get("timings_sec") or {}).get("total") or r.get("rebuild_cost_sec")
        if not rt:
            continue
        gain = float(r.get("candidate_overall", 0)) - float(r.get("baseline_overall", 0))
        if rt > 0:
            gains_per_sec[r.get("mutation_class") or "NONE"].append(gain / rt)

    # Regression by evaluator (accepted cycle that nonetheless dropped
    # a non-targeted evaluator's score)
    regressions: Counter = Counter()
    for r in accepted:
        targeted = r.get("targeted_eval")
        for eid, delta in (r.get("score_delta") or {}).items():
            if eid == targeted:
                continue
            if delta < 0:
                regressions[eid] += 1

    # No-op rate: cycles where candidate_overall == baseline_overall
    noops = sum(1 for r in rows
                if r.get("candidate_overall") is not None
                and abs(float(r.get("candidate_overall", 0)) -
                        float(r.get("baseline_overall", 0))) < 1e-6)

    lines = [
        "# Overlay auto-researcher learning summary",
        "",
        f"- Cycles logged: **{total}**",
        f"- Accepted: **{len(accepted)}** "
        f"({100*len(accepted)/total:.0f}%)",
        f"- Rejected: **{len(rejected)}** "
        f"({100*len(rejected)/total:.0f}%)",
        f"- No-op cycles: **{noops}**",
        "",
        "## Acceptance by mutation class",
        "",
        "| Class | Total | Accepted | Rejected | Gain/sec (mean) |",
        "|---|---:|---:|---:|---:|",
    ]
    for cls in sorted(by_class, key=lambda c: -by_class[c]["total"]):
        c = by_class[cls]
        gps = gains_per_sec.get(cls) or []
        mean_gps = sum(gps) / len(gps) if gps else 0.0
        lines.append(f"| {cls} | {c['total']} | {c['accepted']} | "
                     f"{c['rejected']} | {mean_gps:.5f} |")

    lines.append("")
    lines.append("## Regressions in non-targeted evaluators")
    lines.append("")
    if not regressions:
        lines.append("_None — accepted cycles never dropped another score._")
    else:
        lines.append("| Evaluator | Accepted cycles that dropped this score |")
        lines.append("|---|---:|")
        for eid, n in regressions.most_common():
            lines.append(f"| {eid} | {n} |")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", default=None)
    ap.add_argument("--last", type=int, default=0)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    runs_dir = (pathlib.Path(args.runs_dir)
                if args.runs_dir
                else pathlib.Path(__file__).resolve().parent / "runs")
    out = pathlib.Path(args.out) if args.out else runs_dir / "summary.md"
    text = summarise(_load(runs_dir, args.last))
    out.write_text(text)
    print(f"wrote {out} ({len(text)} chars)")


if __name__ == "__main__":
    main()
