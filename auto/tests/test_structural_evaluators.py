"""Structural quality bar — the Zambia outputs are the golden oracle.

These tests prove:
  1. The current Zambia DOCX pass every structural evaluator cleanly.
  2. Synthetic mutations to the Zambia DOCX (remove a required section,
     remove a required table, drop an image) produce BLOCKER findings.
  3. The fixture-country package passes its own (simpler) schema.
  4. The BLOCKER gate in promotion.accept() rejects a candidate even
     when its weighted overall score improved.
"""
from __future__ import annotations
import copy
import pathlib
import shutil
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from manifest import load as load_manifest
from snapshot import (Paragraph, TableView, DocView, PackageSnapshot,
                      build_snapshot)
import evaluators as EV
from promotion import accept as accept_gate


# ─── Happy path: current Zambia outputs satisfy the quality bar ────

def test_zambia_baseline_passes_structural_evaluators(overlay_root):
    m = load_manifest(overlay_root, "zambia-2026-04")
    snap = build_snapshot(m)

    for evid in ("E14_required_sections", "E15_required_tables",
                 "E16_required_visuals"):
        fn = EV.ALL_EVALUATORS[evid]
        score, findings = fn(snap, m)
        assert score == 1.0, f"{evid} failed on baseline: {findings}"
        blockers = [f for f in findings if f.get("severity") == "BLOCKER"]
        assert not blockers, f"{evid} emitted BLOCKERs on baseline: {blockers}"


def test_zambia_baseline_has_no_blockers_overall(overlay_root):
    m = load_manifest(overlay_root, "zambia-2026-04")
    results = EV.run_all(m)
    blockers = EV.blocker_findings(results)
    assert not blockers, (
        "Zambia baseline has BLOCKERs — quality bar not self-consistent:\n"
        + "\n".join(f"  {eid}: {f['detail']}" for eid, f in blockers)
    )


# ─── Mutation path: missing section / table / image all block ──────

@pytest.fixture
def zambia_snapshot(overlay_root):
    m = load_manifest(overlay_root, "zambia-2026-04")
    return m, build_snapshot(m)


def test_missing_required_section_blocks(zambia_snapshot):
    m, snap = zambia_snapshot
    label = "sample_final_report"
    v = snap.view(label)
    filtered = [p for p in v.paragraphs
                if not ("conclusion" in (p.text or "").lower()
                        and p.heading_level)]
    mutated = DocView(
        path=v.path, paragraphs=filtered,
        raw_text=v.raw_text, page_break_count=v.page_break_count,
        table_row_count=v.table_row_count,
        image_count=v.image_count, tables=v.tables,
    )
    snap._views[label] = mutated
    score, findings = EV.e14_required_sections(snap, m)
    assert score < 1.0
    blockers = [f for f in findings if f.get("severity") == "BLOCKER"]
    assert any("conclusion" in f["detail"].lower() for f in blockers), (
        f"expected Conclusion BLOCKER, got: {blockers}"
    )


def test_missing_required_table_blocks(zambia_snapshot):
    m, snap = zambia_snapshot
    label = "sample_final_report"
    v = snap.view(label)
    kept = [t for t in v.tables
            if not (t.header_has("Phase") and t.header_has("Coverage")
                    and t.cols >= 3)]
    mutated = DocView(
        path=v.path, paragraphs=v.paragraphs,
        raw_text=v.raw_text, page_break_count=v.page_break_count,
        table_row_count=v.table_row_count, image_count=v.image_count,
        tables=kept,
    )
    snap._views[label] = mutated
    score, findings = EV.e15_required_tables(snap, m)
    assert score < 1.0
    blockers = [f for f in findings if f.get("severity") == "BLOCKER"]
    assert any("phase_coverage_table" in f["detail"] for f in blockers), (
        f"expected phase_coverage_table BLOCKER, got: {blockers}"
    )


def test_insufficient_images_blocks(zambia_snapshot):
    m, snap = zambia_snapshot
    label = "sample_final_report"
    v = snap.view(label)
    mutated = DocView(
        path=v.path, paragraphs=v.paragraphs,
        raw_text=v.raw_text, page_break_count=v.page_break_count,
        table_row_count=v.table_row_count,
        image_count=0,
        tables=v.tables,
    )
    snap._views[label] = mutated
    score, findings = EV.e16_required_visuals(snap, m)
    assert score < 1.0
    blockers = [f for f in findings if f.get("severity") == "BLOCKER"]
    assert blockers, "expected image-count BLOCKER"


# ─── Gate: BLOCKER rejects even when weighted score improves ────────

def _mk_result(score, findings=None, weight=1.0):
    return {"score": score, "weight": weight, "findings": findings or []}


def test_blocker_gate_rejects_despite_score_improvement():
    baseline = {
        "E14_required_sections": _mk_result(0.8,
            [{"kind": "ADD_SECTION", "severity": "BLOCKER",
              "detail": "missing Conclusion", "target_file": "",
              "target_text": ""}],
        ),
        "E03_no_ai_tells": _mk_result(0.8, []),
    }
    candidate = {
        "E14_required_sections": _mk_result(0.9,
            [{"kind": "ADD_SECTION", "severity": "BLOCKER",
              "detail": "missing Conclusion", "target_file": "",
              "target_text": ""}],
        ),
        "E03_no_ai_tells": _mk_result(1.0, []),
    }
    accepted, reason = accept_gate(baseline, candidate, "E03_no_ai_tells")
    assert not accepted, f"gate wrongly accepted: {reason}"
    assert "BLOCKER" in reason


def test_no_blockers_allows_promotion():
    baseline = {
        "E03_no_ai_tells": _mk_result(0.8, []),
        "E14_required_sections": _mk_result(1.0, []),
    }
    candidate = {
        "E03_no_ai_tells": _mk_result(1.0, []),
        "E14_required_sections": _mk_result(1.0, []),
    }
    accepted, reason = accept_gate(baseline, candidate, "E03_no_ai_tells")
    assert accepted, reason


# ─── Country-agnostic: fixture package passes its own schema ───────

def test_fixture_country_passes_its_schema(overlay_root):
    m = load_manifest(overlay_root, "fixture-country")
    snap = build_snapshot(m)
    for evid in ("E14_required_sections", "E15_required_tables",
                 "E16_required_visuals"):
        fn = EV.ALL_EVALUATORS[evid]
        score, findings = fn(snap, m)
        assert score == 1.0, f"{evid} fixture failed: {findings}"
