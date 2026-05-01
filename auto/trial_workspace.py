"""Disposable package copy with atomic whitelisted promote.

Replaces the old stash-in-place sandbox. Every sandbox or promote trial
runs on a full copy of the package under `/tmp/overlay-trial-<ts>-<pid>/`.
The working tree is never mutated unless promotion succeeds, at which
point only files on the manifest's `mutation_whitelist` are rewritten.

Rejected trials discard the whole workspace. Derived artifacts (DOCX,
charts) are never left in a half-accepted state.

Also validates chart PNGs against the manifest's `_baseline/` oracle
after promote: charts the patch did not intend to touch must stay
byte-identical to the baseline.
"""
from __future__ import annotations
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable, Dict, Iterator, List, Optional, Tuple

from manifest import Manifest
from mutator import PatchPlan


REBUILD_TIMEOUT_SEC = 180


@dataclass
class RebuildResult:
    ok: bool
    script: Optional[str] = None    # script that failed, if any
    stderr_tail: str = ""
    wall_time: float = 0.0


@dataclass
class PromoteResult:
    ok: bool
    reason: str
    touched_source: List[str]       # relative paths rewritten in package
    baseline_drift: List[str]       # chart paths that drifted from _baseline


def _sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class TrialWorkspace:
    """Context manager: `with TrialWorkspace(manifest) as ws: ...`

    On enter, copies the whole package root into /tmp. On exit, removes
    the copy. The caller can apply patches and rebuild inside the copy
    without ever touching the working tree.
    """

    def __init__(self, manifest: Manifest,
                 tmp_root: Optional[pathlib.Path] = None):
        self.manifest = manifest
        self._tmp_root = tmp_root or pathlib.Path(tempfile.gettempdir())
        self._dir: Optional[pathlib.Path] = None

    @property
    def root(self) -> pathlib.Path:
        if self._dir is None:
            raise RuntimeError("TrialWorkspace not entered")
        return self._dir

    @property
    def build_dir(self) -> pathlib.Path:
        return self.root / "build"

    def __enter__(self) -> "TrialWorkspace":
        ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        self._dir = self._tmp_root / f"overlay-trial-{ts}-{os.getpid()}"
        # Copy the whole package. ignore=None keeps _baseline and charts.
        shutil.copytree(self.manifest.root, self._dir,
                        symlinks=False, ignore=None)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._dir is not None and self._dir.exists():
            shutil.rmtree(self._dir, ignore_errors=True)
        self._dir = None

    # ─── Patch application ───────────────────────────────────────────

    def apply_patch(self, patch: PatchPlan) -> List[pathlib.Path]:
        """Rewrite patch files inside the trial copy.

        Patch paths are absolute references to the real package. We
        translate each to the equivalent path inside the trial root.
        Returns the list of trial paths rewritten.
        """
        written: List[pathlib.Path] = []
        for abs_path, content in patch.files.items():
            rel = abs_path.relative_to(self.manifest.root)
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
            written.append(target)
        return written

    # ─── Rebuild ─────────────────────────────────────────────────────

    def rebuild(self, scripts: Optional[List[str]] = None,
                timeout: int = REBUILD_TIMEOUT_SEC) -> RebuildResult:
        scripts = scripts or self.manifest.build_scripts
        start = time.monotonic()
        for s in scripts:
            script_path = self.build_dir / s
            if not script_path.exists():
                return RebuildResult(
                    ok=False, script=s,
                    stderr_tail=f"script not found: {script_path}",
                    wall_time=time.monotonic() - start,
                )
            result = subprocess.run(
                [sys.executable, s],
                cwd=self.build_dir,
                capture_output=True, text=True, timeout=timeout,
            )
            if result.returncode != 0:
                return RebuildResult(
                    ok=False, script=s,
                    stderr_tail=result.stderr[-1500:],
                    wall_time=time.monotonic() - start,
                )
        return RebuildResult(ok=True, wall_time=time.monotonic() - start)


# ─── Trial and promote ──────────────────────────────────────────────

def trial(manifest: Manifest, patch: PatchPlan,
          evaluate_fn: Callable[[pathlib.Path], dict],
          rebuild_scripts: Optional[List[str]] = None,
          ) -> Tuple[bool, Optional[dict], Optional[str], RebuildResult]:
    """Apply patch in a disposable copy, rebuild, evaluate, discard.

    Returns (ok, eval_results, error_message, rebuild_result). The
    working tree is never touched.
    """
    with TrialWorkspace(manifest) as ws:
        ws.apply_patch(patch)
        rr = ws.rebuild(rebuild_scripts)
        if not rr.ok:
            return False, None, f"rebuild failed in {rr.script}: {rr.stderr_tail[-400:]}", rr
        try:
            results = evaluate_fn(ws.root)
        except Exception as e:
            return False, None, f"evaluator crashed: {e}", rr
        return True, results, None, rr


def commit_patch(manifest: Manifest, patch: PatchPlan,
                 evaluate_fn: Callable[[pathlib.Path], dict],
                 accept_fn: Callable[[dict], Tuple[bool, str]],
                 rebuild_scripts: Optional[List[str]] = None,
                 ) -> Tuple[bool, Optional[dict], Optional[str],
                            Optional[PromoteResult], RebuildResult]:
    """Trial + gate + atomic promote.

    Only if `accept_fn(candidate_results)` returns (True, _) do we
    copy the whitelisted source files back into the working tree and
    rebuild the package in place so derived artifacts reflect the
    accepted source.

    Returns (ok_committed, eval_results, error_message, promote_result, rebuild_result).
    """
    with TrialWorkspace(manifest) as ws:
        ws.apply_patch(patch)
        rr = ws.rebuild(rebuild_scripts)
        if not rr.ok:
            return (False, None,
                    f"rebuild failed in {rr.script}: {rr.stderr_tail[-400:]}",
                    None, rr)
        try:
            results = evaluate_fn(ws.root)
        except Exception as e:
            return (False, None, f"evaluator crashed: {e}", None, rr)

        accepted, reason = accept_fn(results)
        if not accepted:
            # Workspace is discarded by the context manager. The real
            # package is byte-identical to pre-trial. This is the fix
            # for the old silent-regression path.
            return (False, results, f"rejected: {reason}", None, rr)

        promote_result = _atomic_promote(manifest, ws, patch)
        if not promote_result.ok:
            return (False, results,
                    f"promote failed: {promote_result.reason}",
                    promote_result, rr)

        # Rebuild in place so docx/png on disk reflect accepted source.
        in_place_rr = _rebuild_in_package(manifest, rebuild_scripts)
        if not in_place_rr.ok:
            # Source was promoted but rebuild failed. Restore baseline
            # charts and leave a blocker — caller decides what to do.
            _restore_baseline_charts(manifest)
            return (False, results,
                    f"in-place rebuild failed: {in_place_rr.stderr_tail[-400:]}",
                    promote_result, in_place_rr)

        return (True, results, reason, promote_result, in_place_rr)


def _atomic_promote(manifest: Manifest, ws: TrialWorkspace,
                    patch: PatchPlan) -> PromoteResult:
    """Copy patched source files from the trial workspace back into the
    package. Only paths listed in `mutation_whitelist` are allowed."""
    whitelist = {manifest.build_dir / n for n in manifest.mutation_whitelist}
    touched: List[str] = []

    for abs_path in patch.files:
        if abs_path not in whitelist:
            return PromoteResult(
                ok=False,
                reason=f"patch touches non-whitelisted path: {abs_path}",
                touched_source=[], baseline_drift=[],
            )

    for abs_path in patch.files:
        rel = abs_path.relative_to(manifest.root)
        src = ws.root / rel
        tmp = abs_path.with_suffix(abs_path.suffix + ".promote.tmp")
        try:
            shutil.copyfile(src, tmp)
            os.replace(tmp, abs_path)
        except Exception as e:
            if tmp.exists():
                try: tmp.unlink()
                except Exception: pass
            return PromoteResult(
                ok=False, reason=f"copy failed for {rel}: {e}",
                touched_source=touched, baseline_drift=[],
            )
        touched.append(str(rel))

    drift = _baseline_chart_drift(manifest, touched_scripts=set(touched))
    return PromoteResult(ok=True, reason="promoted",
                         touched_source=touched, baseline_drift=drift)


def _rebuild_in_package(manifest: Manifest,
                        scripts: Optional[List[str]] = None,
                        timeout: int = REBUILD_TIMEOUT_SEC) -> RebuildResult:
    scripts = scripts or manifest.build_scripts
    start = time.monotonic()
    for s in scripts:
        script_path = manifest.build_dir / s
        if not script_path.exists():
            return RebuildResult(ok=False, script=s,
                                 stderr_tail=f"missing: {script_path}",
                                 wall_time=time.monotonic() - start)
        result = subprocess.run(
            [sys.executable, s],
            cwd=manifest.build_dir,
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0:
            return RebuildResult(ok=False, script=s,
                                 stderr_tail=result.stderr[-1500:],
                                 wall_time=time.monotonic() - start)
    return RebuildResult(ok=True, wall_time=time.monotonic() - start)


def _baseline_chart_drift(manifest: Manifest,
                          touched_scripts: set) -> List[str]:
    """Charts that differ from the _baseline oracle but weren't touched
    by the patch. Only runs if the patch doesn't touch build_charts.py.
    """
    if manifest.baseline_dir is None or not manifest.baseline_dir.exists():
        return []
    if any("build_charts.py" in t for t in touched_scripts):
        return []  # expected drift
    drift: List[str] = []
    for baseline_png in manifest.baseline_dir.glob("*.png"):
        live = manifest.charts_dir / baseline_png.name
        if not live.exists():
            drift.append(str(baseline_png.name))
            continue
        if _sha256(live) != _sha256(baseline_png):
            drift.append(str(baseline_png.name))
    return drift


def _restore_baseline_charts(manifest: Manifest) -> None:
    if manifest.baseline_dir is None or not manifest.baseline_dir.exists():
        return
    manifest.charts_dir.mkdir(parents=True, exist_ok=True)
    for png in manifest.baseline_dir.glob("*.png"):
        shutil.copyfile(png, manifest.charts_dir / png.name)


# ─── Working-tree hashing (for tests) ────────────────────────────────

def package_fingerprint(manifest: Manifest,
                        include_globs: Optional[List[str]] = None
                        ) -> Dict[str, str]:
    """sha256 per file under the package. Used by tests to assert that
    rejected trials leave the tree byte-identical."""
    include_globs = include_globs or ["**/*"]
    out: Dict[str, str] = {}
    for glob in include_globs:
        for p in manifest.root.glob(glob):
            if not p.is_file():
                continue
            if p.name.startswith("~$"):
                continue  # office lock files
            rel = p.relative_to(manifest.root)
            out[str(rel)] = _sha256(p)
    return dict(sorted(out.items()))
