"""Thin re-exports from trial_workspace for backwards-compatibility.

The old stash-in-place sandbox has been removed. All trial and promote
work goes through `trial_workspace.TrialWorkspace`, which operates on a
disposable `/tmp` copy of the package.
"""
from __future__ import annotations

from trial_workspace import (                                        # noqa: F401
    TrialWorkspace,
    trial,
    commit_patch,
    package_fingerprint,
)
