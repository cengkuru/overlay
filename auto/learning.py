"""Append-only JSONL cycle log.

Records are rich enough to drive learning summaries: patch fingerprint,
touched files, timings, rebuild cost, assurance counts, rollback
outcome, and per-evaluator delta.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def patch_fingerprint(patch) -> str:
    h = hashlib.sha256()
    for path in sorted(patch.files):
        h.update(str(path).encode())
        h.update(b"\0")
        h.update(patch.files[path].encode())
        h.update(b"\0")
    return h.hexdigest()[:16]


def _delta(baseline: Dict[str, Dict],
           candidate: Optional[Dict[str, Dict]]) -> Dict[str, float]:
    if not candidate:
        return {}
    out: Dict[str, float] = {}
    for k, b in baseline.items():
        c = candidate.get(k, {"score": b["score"]})
        out[k] = round(c["score"] - b["score"], 4)
    return out


def _assurance_counts(results: Optional[Dict[str, Dict]]) -> Dict[str, int]:
    if not results or "E10_assurance_gate" not in results:
        return {"blocker": 0, "important": 0, "minor": 0}
    findings = results["E10_assurance_gate"].get("findings") or []
    b = i = m = 0
    for f in findings:
        detail = (f.get("detail") or "").upper()
        if "ASSURE-00" in detail or "ASSURE-01" in detail:
            # Severity is embedded in message prefix; fall back to none
            pass
        # Our evaluator reports severity-less detail; count all as
        # "findings" rather than split severities. A richer split would
        # need severity in the finding dict — left as a TODO when
        # evaluators evolve.
    return {"blocker": b, "important": i, "minor": m,
            "finding_count": len(findings)}


def log_cycle(runs_dir: pathlib.Path, *,
              cycle: int, mode: str,
              targeted_eval: Optional[str],
              mutation_class: Optional[str],
              accepted: bool, reason: str,
              baseline_overall: float, candidate_overall: float,
              baseline_results: Dict, candidate_results: Optional[Dict],
              patch_description: Optional[str],
              patch: Any = None,
              touched_files: Optional[List[str]] = None,
              timings: Optional[Dict[str, float]] = None,
              rebuild_cost: Optional[float] = None,
              rollback_outcome: str = "not_needed",
              baseline_drift: Optional[List[str]] = None,
              ) -> Dict:
    runs_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cycle": cycle,
        "mode": mode,
        "targeted_eval": targeted_eval,
        "mutation_class": mutation_class,
        "patch_description": patch_description,
        "patch_fingerprint": patch_fingerprint(patch) if patch else None,
        "touched_files": touched_files or [],
        "accepted": accepted,
        "reason": reason,
        "rollback_outcome": rollback_outcome,
        "baseline_overall": baseline_overall,
        "candidate_overall": candidate_overall,
        "score_delta": _delta(baseline_results, candidate_results),
        "baseline_scores": {
            k: v["score"] for k, v in baseline_results.items()
        },
        "candidate_scores": (
            {k: v["score"] for k, v in candidate_results.items()}
            if candidate_results else None
        ),
        "timings_sec": timings or {},
        "rebuild_cost_sec": rebuild_cost,
        "baseline_drift": baseline_drift or [],
        "assurance_counts": _assurance_counts(candidate_results),
    }
    with (runs_dir / "history.jsonl").open("a") as f:
        f.write(json.dumps(record) + "\n")
    return record
