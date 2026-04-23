"""Rank evaluators by weakness and return the top candidate for mutation."""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple


def rank_weaknesses(results: Dict[str, Dict]) -> List[Tuple[str, float]]:
    """Rank evaluators by (1 - score) * weight, descending.

    Already-passing evaluators (score >= 0.95) are excluded.
    """
    ranked = []
    for eid, r in results.items():
        score, weight = r["score"], r["weight"]
        if score >= 0.95:
            continue
        gap = (1.0 - score) * weight
        ranked.append((eid, gap))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked


def top_weakness(results: Dict[str, Dict],
                 skip: Optional[set] = None) -> Optional[Tuple[str, Dict]]:
    """Return (evaluator_id, result_dict) for the worst non-skipped evaluator."""
    skip = skip or set()
    for eid, gap in rank_weaknesses(results):
        if eid in skip:
            continue
        return eid, results[eid]
    return None
