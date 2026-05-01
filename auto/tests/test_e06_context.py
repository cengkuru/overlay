"""E06 distinguishes forbidden contexts from permitted ones.

Creates synthetic paragraphs with the fixture manifest's forbidden
literal ("100") and asserts that the evaluator scores them according
to the manifest's policy rather than flagging every hit.
"""
from __future__ import annotations
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from manifest import load as load_manifest
from snapshot import Paragraph, DocView, PackageSnapshot
import evaluators as EV


def _make_snapshot_with_paragraphs(manifest, paragraphs):
    """Build a PackageSnapshot whose single output is synthetic."""
    label = next(iter(manifest.outputs))
    fake_path = manifest.output_path(label)
    view = DocView(
        path=fake_path,
        paragraphs=paragraphs,
        raw_text="\n".join(p.text for p in paragraphs),
        page_break_count=0,
        table_row_count=0,
    )
    snap = PackageSnapshot(
        package_root=manifest.root,
        outputs={label: fake_path},
        charts_dir=manifest.charts_dir,
    )
    snap._views[label] = view
    return snap


@pytest.fixture
def fixture_manifest(overlay_root):
    return load_manifest(overlay_root, "fixture-country")


def test_e06_permits_callout_label(fixture_manifest):
    snap = _make_snapshot_with_paragraphs(fixture_manifest, [
        Paragraph(text="NOTE: the total of 100 fields is the universe.",
                  style="Normal", heading_level=None,
                  ancestor_heading="Findings"),
    ])
    score, findings = EV.e06_no_1480_lead(snap, fixture_manifest)
    assert score == 1.0, f"callout label not permitted: findings={findings}"


def test_e06_permits_annex_heading(fixture_manifest):
    snap = _make_snapshot_with_paragraphs(fixture_manifest, [
        Paragraph(text="The universe total is 100 fields.",
                  style="Normal", heading_level=None,
                  ancestor_heading="Annex A. Denominators"),
    ])
    score, _ = EV.e06_no_1480_lead(snap, fixture_manifest)
    assert score == 1.0


def test_e06_penalises_headline_heading(fixture_manifest):
    snap = _make_snapshot_with_paragraphs(fixture_manifest, [
        Paragraph(text="Only 25 of 100 fields are published.",
                  style="Normal", heading_level=None,
                  ancestor_heading="Headline"),
    ])
    score, findings = EV.e06_no_1480_lead(snap, fixture_manifest)
    assert score < 1.0, "forbidden heading context should score < 1.0"
    assert findings, "should emit a REMOVE_1480 finding"


def test_e06_advisory_for_neutral_heading(fixture_manifest):
    snap = _make_snapshot_with_paragraphs(fixture_manifest, [
        Paragraph(text="Coverage is 25 of 100 fields overall.",
                  style="Normal", heading_level=None,
                  ancestor_heading="Findings"),
    ])
    score, findings = EV.e06_no_1480_lead(snap, fixture_manifest)
    # Neutral: neither permitted nor forbidden — advisory, not a full
    # violation. Score should sit strictly between 0.0 and 1.0.
    assert 0.0 < score < 1.0
    assert findings and any("advisory" in f["detail"].lower() for f in findings)
