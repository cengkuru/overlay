"""Shared fixtures for the auto-researcher test suite."""
from __future__ import annotations
import pathlib
import shutil
import subprocess
import sys

import pytest


HERE = pathlib.Path(__file__).resolve().parent
AUTO = HERE.parent
OVERLAY_ROOT = AUTO.parent

if str(AUTO) not in sys.path:
    sys.path.insert(0, str(AUTO))


@pytest.fixture
def overlay_root() -> pathlib.Path:
    return OVERLAY_ROOT


@pytest.fixture
def fixture_package(tmp_path) -> pathlib.Path:
    """Copy the fixture-country package into a tmp dir and build it.
    Returns the path to a *new* overlay root containing that single
    package. Tests that mutate the package should use this fixture to
    avoid touching the real `samples/fixture-country/`.
    """
    src = OVERLAY_ROOT / "samples" / "fixture-country"
    if not src.exists():
        pytest.skip("fixture-country package not present")
    dst_overlay = tmp_path / "overlay"
    dst = dst_overlay / "samples" / "fixture-country"
    dst.mkdir(parents=True)
    # Copy source files only; skip already-built docx so the build step
    # is exercised by the test.
    shutil.copytree(src / "build", dst / "build")
    shutil.copyfile(src / "package.yaml", dst / "package.yaml")
    (dst / "charts").mkdir(exist_ok=True)
    (dst / "_baseline").mkdir(exist_ok=True)
    # Run the build once to seed outputs.
    r = subprocess.run(
        [sys.executable, "build_fixture_doc.py"],
        cwd=dst / "build", capture_output=True, text=True, timeout=60,
    )
    if r.returncode != 0:
        pytest.fail(f"fixture build failed: {r.stderr}")
    return dst_overlay
