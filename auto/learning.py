"""Append-only JSONL log of every cycle."""
from __future__ import annotations
import json
import pathlib
from datetime import datetime
from typing import Dict, Optional


def log_cycle(runs_dir: pathlib.Path, *, cycle: int, mode: str,
              targeted_eval: Optional[str], mutation_class: Optional[str],
              accepted: bool, reason: str,
              baseline_overall: float, candidate_overall: float,
              baseline_results: Dict, candidate_results: Optional[Dict],
              patch_description: Optional[str]):
    runs_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "cycle": cycle,
        "mode": mode,
        "targeted_eval": targeted_eval,
        "mutation_class": mutation_class,
        "patch_description": patch_description,
        "accepted": accepted,
        "reason": reason,
        "baseline_overall": baseline_overall,
        "candidate_overall": candidate_overall,
        "baseline_scores": {
            k: v["score"] for k, v in baseline_results.items()
        },
        "candidate_scores": (
            {k: v["score"] for k, v in candidate_results.items()}
            if candidate_results else None
        ),
    }
    with (runs_dir / "history.jsonl").open("a") as f:
        f.write(json.dumps(record) + "\n")
    return record
