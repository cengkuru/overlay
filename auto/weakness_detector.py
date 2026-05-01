"""Rank evaluators by expected gain per second of rebuild cost.

gain  = (1 - score) * weight
cost  = estimated rebuild cost of the mutation's target file set
       (falls back to the cheapest single build script if unknown)
rank  = gain / max(cost, 1e-3)
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

from manifest import Manifest
from mutator import MUTATION_DISPATCH


def _mutation_cost(manifest: Manifest, eval_id: str) -> float:
    """Pessimistic estimate: every script in the whitelist at its
    rebuild cost. Real per-patch cost is measured after a propose."""
    costs = manifest.rebuild_cost_sec or {}
    return sum(costs.get(s, 2.0) for s in manifest.mutation_whitelist) or 1.0


def rank_weaknesses(manifest: Manifest,
                    results: Dict[str, Dict],
                    pass_threshold: float = 0.95
                    ) -> List[Tuple[str, float]]:
    """Return (eval_id, priority) for every non-passing evaluator that
    has a mutation in MUTATION_DISPATCH, sorted by priority desc.
    Evaluators without a mutation are excluded so the loop never picks
    an unpatchable target."""
    ranked: List[Tuple[str, float]] = []
    for eid, r in results.items():
        if r["score"] >= pass_threshold:
            continue
        if eid not in MUTATION_DISPATCH:
            continue
        gain = (1.0 - r["score"]) * r["weight"]
        cost = _mutation_cost(manifest, eid)
        priority = gain / max(cost, 1e-3)
        ranked.append((eid, priority))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked


def top_weakness(manifest: Manifest,
                 results: Dict[str, Dict],
                 skip: Optional[set] = None,
                 ) -> Optional[Tuple[str, Dict]]:
    skip = skip or set()
    for eid, _ in rank_weaknesses(manifest, results):
        if eid in skip:
            continue
        return eid, results[eid]
    return None
