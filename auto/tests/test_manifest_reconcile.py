"""Zambia manifest arithmetic must reconcile."""
from __future__ import annotations
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from manifest import load as load_manifest


def test_zambia_counts_reconcile(overlay_root):
    m = load_manifest(overlay_root, "zambia-2026-04")
    c = m.invariants.get("counts", {})
    total = c["template_total"]
    req = c["required_populated"]
    pct_decl = c["overall_percent"]
    pct = round(100.0 * req / total, 1)
    assert abs(pct - pct_decl) < 0.15, (
        f"{req}/{total} = {pct}%, manifest says {pct_decl}%"
    )


def test_zambia_r_ids_are_complete(overlay_root):
    m = load_manifest(overlay_root, "zambia-2026-04")
    ids = m.recommendation_ids()
    assert ids == [f"R{i}" for i in range(1, 11)], ids


def test_fixture_phases_are_well_formed(overlay_root):
    m = load_manifest(overlay_root, "fixture-country")
    phases = m.invariants["phases"]
    # Every value is a non-negative integer in [0, 100].
    for name, pct in phases.items():
        assert isinstance(pct, (int, float))
        assert 0 <= pct <= 100
