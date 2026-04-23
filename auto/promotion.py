"""Single-gate promotion: patch is accepted iff overall improves AND targeted
evaluator improves AND no evaluator regresses below 0.9."""
from __future__ import annotations
from typing import Dict, Tuple

from evaluators import overall_score


def accept(baseline: Dict[str, Dict],
           candidate: Dict[str, Dict],
           targeted_eval: str) -> Tuple[bool, str]:
    """Return (accepted, reason)."""
    b_overall = overall_score(baseline)
    c_overall = overall_score(candidate)
    if c_overall < b_overall:
        return False, f"overall regressed {b_overall:.4f} → {c_overall:.4f}"

    b_score = baseline.get(targeted_eval, {}).get("score", 0.0)
    c_score = candidate.get(targeted_eval, {}).get("score", 0.0)
    if c_score <= b_score:
        return False, f"{targeted_eval} did not improve ({b_score:.3f} → {c_score:.3f})"

    for eid, cand in candidate.items():
        base = baseline.get(eid, {}).get("score", 0.0)
        if cand["score"] < 0.9 and cand["score"] < base:
            return False, f"{eid} regressed below 0.9 ({base:.3f} → {cand['score']:.3f})"

    return True, (f"overall {b_overall:.4f} → {c_overall:.4f}, "
                  f"{targeted_eval} {b_score:.3f} → {c_score:.3f}")
