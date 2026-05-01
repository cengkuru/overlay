"""Single-gate promotion.

A patch is accepted iff ALL of:
  1. No BLOCKER-severity finding remains in the candidate (hard gate:
     trumps every other criterion).
  2. Overall weighted score improves or holds.
  3. The targeted evaluator improves.
  4. No evaluator regresses below 0.9.

The BLOCKER gate means structural quality (E14/E15/E16) and assurance
BLOCKERs (E10) cannot be traded away for a higher score elsewhere.
"""
from __future__ import annotations
from typing import Dict, Tuple

from evaluators import overall_score, blocker_findings


def accept(baseline: Dict[str, Dict],
           candidate: Dict[str, Dict],
           targeted_eval: str) -> Tuple[bool, str]:
    # 1) Hard BLOCKER gate — any BLOCKER finding in candidate rejects.
    blockers = blocker_findings(candidate)
    if blockers:
        first_eid, first_f = blockers[0]
        return False, (f"BLOCKER in {first_eid}: "
                       f"{first_f.get('detail', '(no detail)')} "
                       f"(+{len(blockers)-1} more)"
                       if len(blockers) > 1
                       else f"BLOCKER in {first_eid}: "
                            f"{first_f.get('detail', '(no detail)')}")

    b_overall = overall_score(baseline)
    c_overall = overall_score(candidate)
    if c_overall < b_overall:
        return False, f"overall regressed {b_overall:.4f} → {c_overall:.4f}"

    b_score = baseline.get(targeted_eval, {}).get("score", 0.0)
    c_score = candidate.get(targeted_eval, {}).get("score", 0.0)
    if c_score <= b_score:
        return False, (f"{targeted_eval} did not improve "
                       f"({b_score:.3f} → {c_score:.3f})")

    for eid, cand in candidate.items():
        base = baseline.get(eid, {}).get("score", 0.0)
        if cand["score"] < 0.9 and cand["score"] < base:
            return False, (f"{eid} regressed below 0.9 "
                           f"({base:.3f} → {cand['score']:.3f})")

    return True, (f"overall {b_overall:.4f} → {c_overall:.4f}, "
                  f"{targeted_eval} {b_score:.3f} → {c_score:.3f}")
