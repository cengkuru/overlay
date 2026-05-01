"""Performance gates for the auto-researcher.

Current measured ceilings on macOS laptop baseline:
  baseline evaluate()      ~1.0s (parses 2 DOCX + runs assurance chart check)
  one deterministic cycle  ~4.0s (eval + 3-script rebuild + eval)

Gates are deliberately loose: tighten later if/when the chart signal
check moves to a cheaper sampling strategy. Goal here is to catch
regressions that blow through these, not to police small drift.
"""
from __future__ import annotations
import pathlib
import sys
import time

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from manifest import load as load_manifest
import evaluators as EV


PERF_EVAL_CEILING_SEC = 1.5     # eval cold; measured ~1.0
PERF_CYCLE_CEILING_SEC = 6.0    # deterministic cycle; measured ~4.0


def test_baseline_eval_within_gate(overlay_root):
    m = load_manifest(overlay_root, "zambia-2026-04")
    # Warm: assurance module import is cached after first call.
    EV.run_all(m)
    t0 = time.monotonic()
    EV.run_all(m)
    elapsed = time.monotonic() - t0
    assert elapsed <= PERF_EVAL_CEILING_SEC, (
        f"baseline evaluate() took {elapsed:.2f}s "
        f"(gate: {PERF_EVAL_CEILING_SEC:.2f}s)"
    )


def test_fixture_eval_is_fast(overlay_root):
    """The fixture-country package is tiny; eval should be under 300ms
    cold. This guards against accidentally adding evaluator work that
    scales with the engine rather than the package."""
    m = load_manifest(overlay_root, "fixture-country")
    t0 = time.monotonic()
    EV.run_all(m)
    elapsed = time.monotonic() - t0
    assert elapsed <= 0.5, f"fixture eval took {elapsed:.2f}s (gate: 0.5s)"
