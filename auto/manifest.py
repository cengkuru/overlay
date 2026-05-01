"""Package manifest loader.

The manifest is the single country-specific seam. Everything under auto/
reads country-specific paths, filenames, counts, and vocabulary through
a Manifest. No country name or country literal lives in engine code.

Discovery: `samples/<package>/package.yaml` (relative to overlay_root).
Selection: explicit argument, then OVERLAY_PACKAGE env var, then the
single package if exactly one exists.
"""
from __future__ import annotations
import os
import pathlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError as e:
    raise SystemExit(
        "PyYAML is required. Install with `pip install pyyaml`."
    ) from e


@dataclass
class Manifest:
    name: str
    root: pathlib.Path                       # samples/<package>/
    overlay_root: pathlib.Path
    build_dir: pathlib.Path
    build_scripts: List[str]
    outputs: Dict[str, str]                  # label -> relative filename
    read_only_outputs: List[str]             # labels not produced by build_scripts
    charts_dir: pathlib.Path
    baseline_dir: Optional[pathlib.Path]
    rebuild_cost_sec: Dict[str, float]
    mutation_whitelist: List[str]
    page_targets: Dict[str, Tuple[int, int]]
    invariants: Dict[str, Any]
    recommendations: List[Dict[str, str]]
    context_policy: Dict[str, Any]
    filename_migrations: List[Tuple[str, str]]
    forbidden_internal_vocab: Dict[str, str]
    section_code_pattern: str
    section_code_replacements: Dict[str, str]
    ai_tells: Dict[str, str]
    schema: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)

    def output_path(self, label: str) -> pathlib.Path:
        return self.root / self.outputs[label]

    def docx_labels(self) -> List[str]:
        return list(self.outputs.keys())

    def build_script_path(self, name: str) -> pathlib.Path:
        return self.build_dir / name

    def whitelisted_source_paths(self) -> List[pathlib.Path]:
        return [self.build_dir / n for n in self.mutation_whitelist]

    def recommendation_ids(self) -> List[str]:
        ids: List[str] = []
        for row in self.recommendations:
            rid = row.get("id") if isinstance(row, dict) else None
            if rid:
                ids.append(rid.rstrip(";").strip())
        return ids

    def rebuild_cost(self, script_names: List[str]) -> float:
        return sum(self.rebuild_cost_sec.get(s, 2.0) for s in script_names)


def _parse_recommendations(raw: Any) -> List[Dict[str, str]]:
    """Accept either a list of dicts or a list of 'id: R1; priority: X'
    strings (YAML flow sugar). Normalize to dicts."""
    out: List[Dict[str, str]] = []
    for item in raw or []:
        if isinstance(item, dict):
            out.append({k: str(v).strip().rstrip(";") for k, v in item.items()})
        elif isinstance(item, str):
            parts = [p.strip() for p in item.split(";") if p.strip()]
            d: Dict[str, str] = {}
            for p in parts:
                if ":" in p:
                    k, v = p.split(":", 1)
                    d[k.strip()] = v.strip()
            if d:
                out.append(d)
    return out


def load(overlay_root: pathlib.Path,
         package: Optional[str] = None) -> Manifest:
    overlay_root = pathlib.Path(overlay_root).resolve()
    samples = overlay_root / "samples"
    if not samples.is_dir():
        raise FileNotFoundError(f"no samples/ dir under {overlay_root}")

    package = package or os.environ.get("OVERLAY_PACKAGE")
    if not package:
        candidates = sorted(p.parent.name for p in samples.glob("*/package.yaml"))
        if len(candidates) == 1:
            package = candidates[0]
        elif not candidates:
            raise FileNotFoundError(
                f"no package.yaml found under {samples}. "
                f"Expected samples/<package>/package.yaml."
            )
        else:
            raise ValueError(
                f"multiple packages found ({candidates}); pass --package "
                f"or set OVERLAY_PACKAGE"
            )

    root = samples / package
    path = root / "package.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"manifest missing: {path}")

    raw = yaml.safe_load(path.read_text()) or {}

    def _require(key: str):
        if key not in raw:
            raise ValueError(f"{path}: missing required key '{key}'")
        return raw[key]

    outputs = _require("outputs") or {}
    if not isinstance(outputs, dict):
        raise ValueError(f"{path}: 'outputs' must be a mapping label->filename")

    page_targets_raw = raw.get("page_targets") or {}
    page_targets: Dict[str, Tuple[int, int]] = {}
    for label, bounds in page_targets_raw.items():
        if not (isinstance(bounds, (list, tuple)) and len(bounds) == 2):
            raise ValueError(
                f"{path}: page_targets['{label}'] must be [lo, hi]"
            )
        page_targets[label] = (int(bounds[0]), int(bounds[1]))

    migrations_raw = raw.get("filename_migrations") or []
    migrations: List[Tuple[str, str]] = []
    for pair in migrations_raw:
        if isinstance(pair, (list, tuple)) and len(pair) == 2:
            migrations.append((str(pair[0]), str(pair[1])))

    return Manifest(
        name=str(raw.get("name", package)),
        root=root,
        overlay_root=overlay_root,
        build_dir=root / "build",
        build_scripts=list(_require("build_scripts")),
        outputs={str(k): str(v) for k, v in outputs.items()},
        read_only_outputs=[str(x) for x in (raw.get("read_only_outputs") or [])],
        charts_dir=root / str(raw.get("charts_dir", "charts")),
        baseline_dir=(root / str(raw["baseline_dir"]))
                     if raw.get("baseline_dir") else None,
        rebuild_cost_sec={str(k): float(v)
                          for k, v in (raw.get("rebuild_cost_sec") or {}).items()},
        mutation_whitelist=list(raw.get("mutation_whitelist") or raw.get("build_scripts") or []),
        page_targets=page_targets,
        invariants=dict(raw.get("invariants") or {}),
        recommendations=_parse_recommendations(raw.get("recommendations")),
        context_policy=dict(raw.get("context_policy") or {}),
        filename_migrations=migrations,
        forbidden_internal_vocab={str(k): str(v)
                                   for k, v in (raw.get("forbidden_internal_vocab") or {}).items()},
        section_code_pattern=str(raw.get("section_code_pattern", r"C\d{1,2}")),
        section_code_replacements={str(k): str(v)
                                    for k, v in (raw.get("section_code_replacements") or {}).items()},
        ai_tells={str(k): str(v)
                  for k, v in (raw.get("ai_tells") or {}).items()},
        schema=dict(raw.get("schema") or {}),
        raw=raw,
    )
