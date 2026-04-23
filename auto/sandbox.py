"""Apply a patch to a copy of the build tree, rebuild, and re-score.

Original build files are never mutated in place. A stash-and-apply pattern
is used so either the patch promotes cleanly or the originals return.
"""
from __future__ import annotations
import pathlib
import shutil
import subprocess
import sys
from typing import Dict, Optional

from mutator import PatchPlan


class StashedFiles:
    """Context manager that stashes files, lets the caller write new content,
    and restores originals on exit unless commit() is called first."""

    def __init__(self, patch: PatchPlan):
        self.patch = patch
        self.stashed: Dict[pathlib.Path, str] = {}
        self.committed = False

    def __enter__(self):
        for path in self.patch.files:
            self.stashed[path] = path.read_text()
        for path, content in self.patch.files.items():
            path.write_text(content)
        return self

    def commit(self):
        self.committed = True

    def __exit__(self, exc_type, exc, tb):
        if not self.committed:
            for path, content in self.stashed.items():
                path.write_text(content)


def rebuild(build_dir: pathlib.Path) -> bool:
    """Rebuild both docs and charts. Returns True on success."""
    scripts = ["build_charts.py",
               "build_review_and_reference.py",
               "build_final_report.py"]
    for s in scripts:
        result = subprocess.run(
            [sys.executable, s],
            cwd=build_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            print(f"[sandbox] rebuild failed at {s}:")
            print(result.stderr[-1200:])
            return False
    return True


def trial(patch: PatchPlan, build_dir: pathlib.Path, evaluate_fn):
    """Apply patch in a stash, rebuild, evaluate. Never commits.

    Returns (success, results, error_message).
    """
    with StashedFiles(patch):
        ok = rebuild(build_dir)
        if not ok:
            return False, None, "rebuild failed"
        try:
            results = evaluate_fn()
        except Exception as e:
            return False, None, f"evaluator crashed: {e}"
    return True, results, None


def commit_patch(patch: PatchPlan, build_dir: pathlib.Path, evaluate_fn):
    """Apply patch, rebuild, evaluate, and KEEP the changes if rebuild passed."""
    stash = StashedFiles(patch)
    stash.__enter__()
    try:
        ok = rebuild(build_dir)
        if not ok:
            stash.__exit__(None, None, None)
            return False, None, "rebuild failed"
        try:
            results = evaluate_fn()
        except Exception as e:
            stash.__exit__(None, None, None)
            return False, None, f"evaluator crashed: {e}"
        stash.commit()
        stash.__exit__(None, None, None)
        return True, results, None
    except Exception as e:
        stash.__exit__(None, None, None)
        return False, None, f"sandbox error: {e}"
