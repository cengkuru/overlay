"""Auto-researcher loop.

Usage:
    python3 auto/loop.py                       # promote, 8 cycles, default pkg
    python3 auto/loop.py --mode propose        # eval + one candidate, no apply
    python3 auto/loop.py --mode sandbox        # apply in trial workspace only
    python3 auto/loop.py --package fixture-country
    OVERLAY_PACKAGE=zambia-2026-04 python3 auto/loop.py

Every trial runs in a disposable /tmp copy of the package. On accept,
the manifest's whitelisted source files are atomically promoted and the
package is rebuilt in place so derived artifacts reflect accepted source.
On reject, the workspace is discarded; the working tree is unchanged.
"""
from __future__ import annotations
import argparse
import os
import pathlib
import shutil
import sys
import time
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import evaluators as EV
import mutator as MU
from manifest import Manifest, load as load_manifest
from promotion import accept as acceptance_gate
from trial_workspace import trial, commit_patch
from weakness_detector import top_weakness
from learning import log_cycle


def evaluate(manifest: Manifest,
             package_root: pathlib.Path = None) -> dict:
    return EV.run_all(manifest, package_root)


def _format_score_table(results: dict) -> str:
    lines = ["| Eval | Score | Weight |", "|---|---:|---:|"]
    for eid, r in results.items():
        lines.append(f"| {eid} | {r['score']:.3f} | {r['weight']} |")
    return "\n".join(lines)


def _write_dashboard(run_dir: pathlib.Path, manifest: Manifest,
                     initial: dict, final: dict,
                     cycles: list) -> pathlib.Path:
    md = [
        "# Overlay auto-researcher run",
        "",
        f"**Package:** {manifest.name}",
        f"**When:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"**Cycles:** {len(cycles)}",
        f"**Overall score:** "
        f"{EV.overall_score(initial):.4f} → **{EV.overall_score(final):.4f}**",
        f"**Target:** {EV.OVERALL_TARGET}",
        "",
        "## Initial scores",
        "",
        _format_score_table(initial),
        "",
        "## Cycle log",
        "",
    ]
    if not cycles:
        md.append("_No cycles attempted — baseline already met target, "
                  "or no rule-driven mutation was available._")
    for i, c in enumerate(cycles, start=1):
        acc = "ACCEPTED" if c["accepted"] else "REJECTED"
        md.append(f"### Cycle {i} — {acc}")
        md.append("")
        md.append(f"- Targeted evaluator: `{c['targeted_eval']}`")
        md.append(f"- Mutation class: `{c['mutation_class']}`")
        md.append(f"- Patch: {c['patch_description']}")
        md.append(f"- Touched: {', '.join(c.get('touched_files') or []) or '—'}")
        md.append(f"- Result: {c['reason']}")
        md.append("")
    md += ["## Final scores", "", _format_score_table(final), ""]
    out = run_dir / "dashboard.md"
    out.write_text("\n".join(md))
    return out


def _set_latest_symlink(runs_dir: pathlib.Path, run_dir: pathlib.Path) -> None:
    """Replace runs/latest with a symlink to run_dir, tolerating any
    prior state (missing, symlink, file, or directory)."""
    latest = runs_dir / "latest"
    if latest.is_symlink() or latest.is_file():
        try:
            latest.unlink()
        except OSError:
            pass
    elif latest.is_dir():
        shutil.rmtree(latest)
    try:
        os.symlink(run_dir.name, latest)
    except OSError:
        # Fallback if symlinks unsupported (e.g. weird FS): copy instead.
        shutil.copytree(run_dir, latest)


def run(mode: str = "promote",
        max_cycles: int = 8,
        package: str = None) -> int:
    overlay_root = HERE.parent
    manifest = load_manifest(overlay_root, package)

    runs_dir = HERE / "runs"
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = runs_dir / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[auto] package: {manifest.name}")
    print(f"[auto] mode: {mode}, max {max_cycles} cycles")
    print(f"[auto] run directory: {run_dir}")

    t0 = time.monotonic()
    initial = evaluate(manifest)
    baseline_eval_time = time.monotonic() - t0
    print(f"[auto] baseline eval: {baseline_eval_time:.2f}s")

    current = initial
    current_overall = EV.overall_score(current)
    baseline_blockers = EV.blocker_findings(current)
    print(f"[auto] baseline overall: {current_overall:.4f}")
    if baseline_blockers:
        print(f"[auto] baseline BLOCKERS: {len(baseline_blockers)}")
        for eid, f in baseline_blockers[:5]:
            print(f"   BLOCKER {eid}: {f.get('detail')}")
        if len(baseline_blockers) > 5:
            print(f"   ...and {len(baseline_blockers) - 5} more")

    target_met = (
        not baseline_blockers
        and current_overall >= EV.OVERALL_TARGET
        and all(r["score"] >= EV.PASS_THRESHOLD for r in current.values())
    )
    if target_met:
        print("[auto] already at target; no cycles needed")
        dash = _write_dashboard(run_dir, manifest, initial, current, [])
        _set_latest_symlink(runs_dir, run_dir)
        print(f"[auto] dashboard: {dash}")
        return 0

    skip_evals: set = set()
    cycles: list = []

    for cycle in range(1, max_cycles + 1):
        print(f"\n[cycle {cycle}] ranking weaknesses…")
        tw = top_weakness(manifest, current, skip=skip_evals)
        if tw is None:
            print("[cycle] no remaining weakness with a mutation. Done.")
            break
        eval_id, result = tw
        print(f"[cycle {cycle}] weakest: {eval_id} "
              f"(score={result['score']:.3f})")

        patch = MU.propose(manifest, eval_id, result)
        if patch is None:
            print(f"[cycle {cycle}] no mutation available for {eval_id}; skip")
            skip_evals.add(eval_id)
            log_cycle(runs_dir, cycle=cycle, mode=mode,
                      targeted_eval=eval_id, mutation_class=None,
                      accepted=False, reason="no mutation available",
                      baseline_overall=current_overall,
                      candidate_overall=current_overall,
                      baseline_results=current, candidate_results=None,
                      patch_description=None)
            continue

        touched = patch.relative_files(manifest)
        print(f"[cycle {cycle}] mutation: {patch.mutation_class} — "
              f"{patch.description}")
        print(f"[cycle {cycle}] touches: {', '.join(touched)}")

        if mode == "propose":
            log_cycle(runs_dir, cycle=cycle, mode=mode,
                      targeted_eval=eval_id,
                      mutation_class=patch.mutation_class,
                      accepted=False, reason="propose mode; no apply",
                      baseline_overall=current_overall,
                      candidate_overall=current_overall,
                      baseline_results=current, candidate_results=None,
                      patch_description=patch.description,
                      patch=patch, touched_files=touched)
            cycles.append({
                "targeted_eval": eval_id,
                "mutation_class": patch.mutation_class,
                "patch_description": patch.description,
                "touched_files": touched,
                "accepted": False,
                "reason": "propose mode (dry run)",
            })
            break  # propose shows one candidate and exits

        t_cycle = time.monotonic()
        def _eval_at(root):
            return evaluate(manifest, root)

        if mode == "sandbox":
            ok, cand_results, err, rr = trial(manifest, patch, _eval_at)
            cycle_time = time.monotonic() - t_cycle
            if not ok:
                print(f"[cycle {cycle}] sandbox failed: {err}")
                log_cycle(runs_dir, cycle=cycle, mode=mode,
                          targeted_eval=eval_id,
                          mutation_class=patch.mutation_class,
                          accepted=False, reason=err,
                          baseline_overall=current_overall,
                          candidate_overall=current_overall,
                          baseline_results=current, candidate_results=None,
                          patch_description=patch.description,
                          patch=patch, touched_files=touched,
                          timings={"total": cycle_time,
                                   "rebuild": rr.wall_time})
                skip_evals.add(eval_id)
                continue
            new_overall = EV.overall_score(cand_results)
            print(f"[cycle {cycle}] sandbox overall: "
                  f"{current_overall:.4f} → {new_overall:.4f}  "
                  f"({cycle_time:.2f}s)")
            log_cycle(runs_dir, cycle=cycle, mode=mode,
                      targeted_eval=eval_id,
                      mutation_class=patch.mutation_class,
                      accepted=False, reason="sandbox mode; no commit",
                      baseline_overall=current_overall,
                      candidate_overall=new_overall,
                      baseline_results=current,
                      candidate_results=cand_results,
                      patch_description=patch.description,
                      patch=patch, touched_files=touched,
                      timings={"total": cycle_time, "rebuild": rr.wall_time},
                      rebuild_cost=manifest.rebuild_cost(manifest.build_scripts))
            cycles.append({
                "targeted_eval": eval_id,
                "mutation_class": patch.mutation_class,
                "patch_description": patch.description,
                "touched_files": touched,
                "accepted": False,
                "reason": f"sandbox: {current_overall:.4f} → {new_overall:.4f}",
            })
            skip_evals.add(eval_id)
            continue

        # promote mode
        def _gate(cand):
            return acceptance_gate(current, cand, eval_id)
        ok, cand_results, err, promote_result, rr = commit_patch(
            manifest, patch, _eval_at, _gate,
        )
        cycle_time = time.monotonic() - t_cycle
        if not ok:
            # Working tree is byte-identical because we never promoted.
            reason = err or "rejected before promote"
            print(f"[cycle {cycle}] {reason} ({cycle_time:.2f}s)")
            log_cycle(runs_dir, cycle=cycle, mode=mode,
                      targeted_eval=eval_id,
                      mutation_class=patch.mutation_class,
                      accepted=False, reason=reason,
                      baseline_overall=current_overall,
                      candidate_overall=(EV.overall_score(cand_results)
                                         if cand_results else current_overall),
                      baseline_results=current,
                      candidate_results=cand_results,
                      patch_description=patch.description,
                      patch=patch, touched_files=touched,
                      timings={"total": cycle_time, "rebuild": rr.wall_time},
                      rebuild_cost=manifest.rebuild_cost(manifest.build_scripts),
                      rollback_outcome="not_needed")
            skip_evals.add(eval_id)
            cycles.append({
                "targeted_eval": eval_id,
                "mutation_class": patch.mutation_class,
                "patch_description": patch.description,
                "touched_files": touched,
                "accepted": False,
                "reason": reason,
            })
            continue

        # Accepted
        drift = promote_result.baseline_drift if promote_result else []
        reason = err  # when ok, commit_patch uses err to carry the accept reason
        print(f"[cycle {cycle}] accepted: {reason} ({cycle_time:.2f}s)")
        if drift:
            print(f"[cycle {cycle}] baseline drift on unchanged charts: "
                  f"{drift}")
        log_cycle(runs_dir, cycle=cycle, mode=mode,
                  targeted_eval=eval_id,
                  mutation_class=patch.mutation_class,
                  accepted=True, reason=reason or "accepted",
                  baseline_overall=current_overall,
                  candidate_overall=EV.overall_score(cand_results),
                  baseline_results=current,
                  candidate_results=cand_results,
                  patch_description=patch.description,
                  patch=patch, touched_files=touched,
                  timings={"total": cycle_time, "rebuild": rr.wall_time},
                  rebuild_cost=manifest.rebuild_cost(manifest.build_scripts),
                  baseline_drift=drift)
        current = cand_results
        current_overall = EV.overall_score(current)
        cycles.append({
            "targeted_eval": eval_id,
            "mutation_class": patch.mutation_class,
            "patch_description": patch.description,
            "touched_files": touched,
            "accepted": True,
            "reason": reason or "accepted",
        })

        if (current_overall >= EV.OVERALL_TARGET
                and all(r["score"] >= EV.PASS_THRESHOLD
                        for r in current.values())):
            print(f"[auto] target reached after cycle {cycle}")
            break

    dash = _write_dashboard(run_dir, manifest, initial, current, cycles)
    _set_latest_symlink(runs_dir, run_dir)
    print(f"\n[auto] final overall: {current_overall:.4f}")
    final_blockers = EV.blocker_findings(current)
    if final_blockers:
        print(f"[auto] {len(final_blockers)} BLOCKER(s) still open — "
              f"package cannot ship")
    print(f"[auto] dashboard: {dash}")
    if final_blockers:
        return 2
    return 0 if current_overall >= EV.OVERALL_TARGET else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["propose", "sandbox", "promote"],
                    default="promote")
    ap.add_argument("--cycles", type=int, default=8)
    ap.add_argument("--package", default=None,
                    help="package name under samples/; defaults to "
                         "OVERLAY_PACKAGE or the single package on disk")
    args = ap.parse_args()
    sys.exit(run(mode=args.mode, max_cycles=args.cycles, package=args.package))


if __name__ == "__main__":
    main()
