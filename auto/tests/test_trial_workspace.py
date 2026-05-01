"""Trial workspace guarantees: rejected trials leave the working tree
byte-identical; accepted promotes touch only whitelisted source files."""
from __future__ import annotations
import os
import pathlib
import shutil
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from manifest import load as load_manifest
from mutator import PatchPlan
from trial_workspace import (TrialWorkspace, trial, commit_patch,
                              package_fingerprint)


def _dummy_evaluate(_root):
    return {"E01_no_dashes": {"score": 1.0, "weight": 1.0, "findings": []}}


def _always_accept(_cand):
    return True, "test-accept"


def _always_reject(_cand):
    return False, "test-reject"


def test_rejected_trial_leaves_tree_byte_identical(fixture_package):
    m = load_manifest(fixture_package, "fixture-country")
    before = package_fingerprint(m)

    # Build a harmless patch that rewrites the fixture's build script
    # with an added newline. Any promote that is rejected must not land.
    target = m.build_dir / "build_fixture_doc.py"
    patch = PatchPlan(
        files={target: target.read_text() + "\n# trial marker\n"},
        description="add trial marker",
        targeted_eval_id="E03_no_ai_tells",
        mutation_class="TEST_NOOP",
    )
    ok, results, err, promote, rr = commit_patch(
        m, patch, lambda r: _dummy_evaluate(r), _always_reject,
    )
    assert not ok
    after = package_fingerprint(m)
    assert before == after, "working tree changed after rejected promote"


def test_accepted_promote_touches_only_whitelisted(fixture_package):
    m = load_manifest(fixture_package, "fixture-country")
    before = package_fingerprint(m)

    target = m.build_dir / "build_fixture_doc.py"
    new_content = target.read_text().replace(
        "leverage this review", "use this review"
    )
    patch = PatchPlan(
        files={target: new_content},
        description="rename leverage",
        targeted_eval_id="E03_no_ai_tells",
        mutation_class="DROP_AI_TELL",
    )
    ok, results, reason, promote, rr = commit_patch(
        m, patch, lambda r: _dummy_evaluate(r), _always_accept,
    )
    assert ok, reason
    after = package_fingerprint(m)

    changed = {k for k in before if before[k] != after.get(k)}
    new_paths = set(after) - set(before)
    dropped = set(before) - set(after)
    # Only the patched source and its derived docx may change.
    # package.yaml and unrelated files must be byte-identical.
    assert "build/build_fixture_doc.py" in changed
    for k in changed:
        assert k in ("build/build_fixture_doc.py", "fixture-report.docx"), \
            f"unexpected change: {k}"
    assert not dropped, f"files disappeared: {dropped}"


def test_sandbox_does_not_modify_tree(fixture_package):
    m = load_manifest(fixture_package, "fixture-country")
    before = package_fingerprint(m)

    target = m.build_dir / "build_fixture_doc.py"
    patch = PatchPlan(
        files={target: target.read_text() + "\n# sandbox marker\n"},
        description="sandbox marker",
        targeted_eval_id="E03_no_ai_tells",
        mutation_class="TEST_NOOP",
    )
    ok, results, err, rr = trial(m, patch, lambda r: _dummy_evaluate(r))
    # rebuild succeeds because the marker is harmless
    assert ok, err
    after = package_fingerprint(m)
    assert before == after, "sandbox modified working tree"


def test_non_whitelisted_patch_refused(fixture_package):
    m = load_manifest(fixture_package, "fixture-country")
    # Try to patch a file outside mutation_whitelist
    off_limits = m.build_dir / "visuals" / "assurance.py"
    patch = PatchPlan(
        files={off_limits: "# tampered\n"},
        description="out of scope",
        targeted_eval_id="E07_chart_annotations",
        mutation_class="BAD",
    )
    ok, results, err, promote, rr = commit_patch(
        m, patch, lambda r: _dummy_evaluate(r), _always_accept,
    )
    assert not ok
    assert "non-whitelisted" in (err or "").lower()
