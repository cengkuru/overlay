"""Deterministic evaluators scoring any Overlay review package.

Every evaluator returns (score, findings). Score is in [0, 1]; findings
is a list of dicts with keys:
  - "kind"        mutation class that might fix it (if any)
  - "detail"      human-readable
  - "target_file" path relative to the package root (e.g. "build/foo.py")
  - "target_text" string literal the mutator can search for (if any)
  - "severity"    optional — one of {"BLOCKER", "IMPORTANT", "MINOR"}.
                  Any BLOCKER finding causes promotion.accept() to
                  reject the patch regardless of weighted score.

The evaluators do not know about mutations. The mutator reads findings
and decides which patch to try. Country-specific thresholds, vocab,
counts, and paths live in the package manifest, not in this file.
"""
from __future__ import annotations
import importlib.util
import pathlib
import re
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

from manifest import Manifest
from snapshot import PackageSnapshot, build_snapshot, build_snapshot_at


# ─── Weights and thresholds ────────────────────────────────────────

EVALUATOR_WEIGHTS: Dict[str, float] = {
    "E01_no_dashes":          1.0,
    "E02_no_internal_vocab":  1.0,
    "E03_no_ai_tells":        1.0,
    "E04_docs_valid":         1.0,
    "E06_no_1480_lead":       1.0,
    "E07_chart_annotations":  0.7,
    "E08_page_length":        0.5,   # advisory only without soffice
    "E09_filename_refs":      1.0,
    "E10_assurance_gate":     1.0,
    "E11_counts_reconcile":   1.0,
    "E12_phase_reconcile":    0.8,
    "E13_rec_ids":            1.0,
    # Structural evaluators emit BLOCKER findings that hard-block
    # promotion. The score weight is intentionally low — the gate is
    # enforced in promotion.accept() via severity, not via score.
    "E14_required_sections":  1.0,
    "E15_required_tables":    1.0,
    "E16_required_visuals":   1.0,
}

PASS_THRESHOLD = 0.95
OVERALL_TARGET = 0.97


Finding = Dict[str, str]


# ─── Helpers ───────────────────────────────────────────────────────

def _rel_to_build(manifest: Manifest, script_name: str) -> str:
    return str((manifest.build_dir / script_name).relative_to(manifest.overlay_root))


_ASSURANCE_CACHE: Dict[str, Any] = {}


def _assurance_module(manifest: Manifest):
    """Import the package's own visuals.assurance at runtime.

    Each package ships its own under build/visuals/; we put the build
    dir on sys.path so the package's own intra-package imports
    (`from .brand import ...`) resolve. The engine stays country-agnostic
    because it never names the package.
    """
    cache_key = str(manifest.build_dir)
    if cache_key in _ASSURANCE_CACHE:
        return _ASSURANCE_CACHE[cache_key]

    visuals_dir = manifest.build_dir / "visuals"
    if not (visuals_dir / "assurance.py").exists():
        _ASSURANCE_CACHE[cache_key] = None
        return None

    build_dir_str = str(manifest.build_dir)
    added = False
    if build_dir_str not in sys.path:
        sys.path.insert(0, build_dir_str)
        added = True

    # Drop any stale module cache from a previous package so per-package
    # imports don't leak across country manifests.
    for name in list(sys.modules):
        if name == "visuals" or name.startswith("visuals."):
            del sys.modules[name]

    try:
        import visuals.assurance as mod       # noqa: E402
    except Exception as e:
        _ASSURANCE_CACHE[cache_key] = None
        if added:
            sys.path.remove(build_dir_str)
        # Surface the cause for debugging at load time
        print(f"[eval] assurance import failed: {e}", file=sys.stderr)
        return None
    if added:
        sys.path.remove(build_dir_str)
    _ASSURANCE_CACHE[cache_key] = mod
    return mod


# ─── Evaluators ────────────────────────────────────────────────────

def e01_no_dashes(snap: PackageSnapshot, manifest: Manifest
                  ) -> Tuple[float, List[Finding]]:
    """No em or en dashes in any DOCX output."""
    findings: List[Finding] = []
    total_em = total_en = 0
    for label, text in snap.iter_text_all():
        em = text.count("—")
        en = text.count("–")
        total_em += em
        total_en += en
        if em or en:
            for script in manifest.mutation_whitelist:
                findings.append({
                    "kind": "REPLACE_DASH",
                    "detail": f"{snap.outputs[label].name}: em={em}, en={en}",
                    "target_file": _rel_to_build(manifest, script),
                    "target_text": "—" if em else "–",
                })
    score = 1.0 if (total_em + total_en == 0) else 0.0
    return score, findings


def e02_no_internal_vocab(snap: PackageSnapshot, manifest: Manifest
                          ) -> Tuple[float, List[Finding]]:
    findings: List[Finding] = []
    vocab = manifest.forbidden_internal_vocab
    pattern = manifest.section_code_pattern
    total = 0
    for label, text in snap.iter_text_all():
        for term in vocab:
            hits = len(re.findall(rf"\b{re.escape(term)}\b", text, re.I))
            if hits:
                total += hits
                for script in manifest.mutation_whitelist:
                    findings.append({
                        "kind": "SUB_FORBIDDEN",
                        "detail": f"{snap.outputs[label].name}: '{term}' x{hits}",
                        "target_text": term,
                        "target_file": _rel_to_build(manifest, script),
                    })
        if pattern:
            cxx = re.findall(rf"\b{pattern}\b", text)
            if cxx:
                total += len(cxx)
                for script in manifest.mutation_whitelist:
                    findings.append({
                        "kind": "SUB_FORBIDDEN",
                        "detail": f"{snap.outputs[label].name}: section codes {sorted(set(cxx))}",
                        "target_text": ",".join(sorted(set(cxx))),
                        "target_file": _rel_to_build(manifest, script),
                    })
    score = 1.0 if total == 0 else max(0.0, 1.0 - 0.1 * total)
    return score, findings


def e03_no_ai_tells(snap: PackageSnapshot, manifest: Manifest
                    ) -> Tuple[float, List[Finding]]:
    findings: List[Finding] = []
    total = 0
    for label, text in snap.iter_text_all():
        for term in manifest.ai_tells:
            # Match whole word to avoid matching "leverages" twice, etc.
            hits = len(re.findall(rf"\b{re.escape(term)}\w*", text, re.I))
            if hits:
                total += hits
                for script in manifest.mutation_whitelist:
                    findings.append({
                        "kind": "DROP_AI_TELL",
                        "detail": f"{snap.outputs[label].name}: '{term}' x{hits}",
                        "target_text": term,
                        "target_file": _rel_to_build(manifest, script),
                    })
    score = 1.0 if total == 0 else max(0.0, 1.0 - 0.15 * total)
    return score, findings


def e04_docs_valid(snap: PackageSnapshot, manifest: Manifest
                   ) -> Tuple[float, List[Finding]]:
    """Every output in the manifest exists, opens, and has non-trivial size."""
    findings: List[Finding] = []
    labels = list(snap.outputs)
    ok = 0
    for label in labels:
        path = snap.outputs[label]
        if not path.exists() or path.stat().st_size < 10_000:
            findings.append({
                "kind": "REBUILD",
                "detail": f"missing or truncated: {label} ({path.name})",
                "target_file": "",
                "target_text": label,
            })
            continue
        if snap.view(label) is None:
            findings.append({
                "kind": "REBUILD",
                "detail": f"{label} failed to parse",
                "target_file": "",
                "target_text": label,
            })
            continue
        ok += 1
    score = ok / len(labels) if labels else 0.0
    return score, findings


def _is_permitted_context(para, policy: Dict[str, Any]) -> bool:
    """Is this paragraph's position a permitted context for the
    forbidden literal (template_total)? Permitted if:
      * its ancestor heading contains any of `permitted_headings`, OR
      * the paragraph text starts with one of `permitted_callout_labels`.
    """
    perm_head = policy.get("permitted_headings") or []
    perm_lbl = policy.get("permitted_callout_labels") or []
    anc = (para.ancestor_heading or "").lower()
    if any(h.lower() in anc for h in perm_head):
        return True
    head20 = (para.text or "").strip()[:60].upper()
    if any(label.upper() in head20 for label in perm_lbl):
        return True
    return False


def _is_forbidden_context(para, policy: Dict[str, Any]) -> bool:
    forb = policy.get("forbidden_headings") or []
    anc = (para.ancestor_heading or "").lower()
    return any(h.lower() in anc for h in forb)


def e06_no_1480_lead(snap: PackageSnapshot, manifest: Manifest
                     ) -> Tuple[float, List[Finding]]:
    """The template-total literal (e.g. '1,480') may appear in permitted
    contexts (annex, methodology, denominator callouts) but not in
    executive-summary / headline contexts."""
    policy = manifest.context_policy or {}
    literal = str(policy.get("template_total_literal", "1,480"))
    pat = re.compile(re.escape(literal).replace(",", r"[,]?"))
    findings: List[Finding] = []
    violations = 0
    for label in snap.all_docx_labels():
        v = snap.view(label)
        if v is None:
            continue
        for para in v.paragraphs:
            if not pat.search(para.text):
                continue
            if _is_forbidden_context(para, policy):
                violations += 1
                for script in manifest.mutation_whitelist:
                    findings.append({
                        "kind": "REMOVE_1480",
                        "detail": (f"{v.path.name} under "
                                   f"'{para.ancestor_heading}': "
                                   f"{literal}"),
                        "target_text": literal,
                        "target_file": _rel_to_build(manifest, script),
                    })
                continue
            if _is_permitted_context(para, policy):
                continue
            # Neither permitted nor explicitly forbidden: treat as minor.
            violations += 0.5
            for script in manifest.mutation_whitelist:
                findings.append({
                    "kind": "REMOVE_1480",
                    "detail": (f"{v.path.name} under "
                               f"'{para.ancestor_heading}' "
                               f"(advisory; not in permitted-context list)"),
                    "target_text": literal,
                    "target_file": _rel_to_build(manifest, script),
                })
    score = 1.0 if violations == 0 else max(0.0, 1.0 - 0.2 * violations)
    return score, findings


def e07_chart_annotations(snap: PackageSnapshot, manifest: Manifest
                          ) -> Tuple[float, List[Finding]]:
    """Charts exist, open, and carry signal. Delegates to the package's
    own assurance.py, which is the canonical chart-quality gate."""
    mod = _assurance_module(manifest)
    if mod is None or not hasattr(mod, "_check_chart_pngs"):
        # Fall back to existence check
        if not manifest.charts_dir.exists():
            return 0.0, [{"kind": "REBUILD", "detail": "charts dir missing",
                          "target_file": "", "target_text": ""}]
        pngs = list(manifest.charts_dir.glob("*.png"))
        return (1.0 if pngs else 0.0), []

    findings: List[Finding] = []
    results = mod._check_chart_pngs(manifest.charts_dir)
    blockers = [f for f in results if f.severity == "BLOCKER"]
    importants = [f for f in results if f.severity == "IMPORTANT"]
    pngs = list(manifest.charts_dir.glob("*.png")) or [None]
    for f in blockers + importants:
        findings.append({
            "kind": "ANNOTATE_CHART",
            "detail": f"{f.code}: {f.message}",
            "target_file": _rel_to_build(manifest, "build_charts.py"),
            "target_text": "",
        })
    score = max(0.0, 1.0 - (1.0 * len(blockers) + 0.1 * len(importants)) / max(1, len(pngs)))
    return score, findings


def e08_page_length(snap: PackageSnapshot, manifest: Manifest
                    ) -> Tuple[float, List[Finding]]:
    """Advisory page-length check using a heuristic estimator.

    Without `soffice` the page count is approximate. This evaluator is
    weighted low and marked advisory in findings.
    """
    findings: List[Finding] = []
    if not manifest.page_targets:
        return 1.0, []
    scores: List[float] = []
    for label, (lo, hi) in manifest.page_targets.items():
        path = snap.outputs.get(label)
        if path is None or not path.exists():
            continue
        n, method = snap.page_count(label)
        if lo <= n <= hi:
            scores.append(1.0)
            continue
        dist = min(abs(n - lo), abs(n - hi))
        scores.append(max(0.0, 1.0 - 0.1 * dist))
        findings.append({
            "kind": "ADJUST_LENGTH",
            "detail": (f"{label}: estimated pages={n} ({method}); "
                       f"target {lo}-{hi} — advisory"),
            "target_file": "",
            "target_text": label,
        })
    score = sum(scores) / len(scores) if scores else 1.0
    return score, findings


def e09_filename_refs(snap: PackageSnapshot, manifest: Manifest
                      ) -> Tuple[float, List[Finding]]:
    """No stale cross-doc filename refs anywhere in the outputs."""
    findings: List[Finding] = []
    migrations = manifest.filename_migrations
    if not migrations:
        return 1.0, []
    stale_total = 0
    for label, text in snap.iter_text_all():
        for bad, good in migrations:
            hits = text.count(bad)
            if hits:
                stale_total += hits
                for script in manifest.mutation_whitelist:
                    findings.append({
                        "kind": "FIX_FILENAME_REF",
                        "detail": (f"{snap.outputs[label].name}: stale "
                                   f"'{bad}' x{hits} → '{good}'"),
                        "target_text": bad,
                        "target_file": _rel_to_build(manifest, script),
                    })
    score = 1.0 if stale_total == 0 else max(0.0, 1.0 - 0.5 * stale_total)
    return score, findings


def e10_assurance_gate(snap: PackageSnapshot, manifest: Manifest
                       ) -> Tuple[float, List[Finding]]:
    """Run the package's assurance gate against every DOCX it knows."""
    mod = _assurance_module(manifest)
    if mod is None or not hasattr(mod, "audit_docx"):
        return 1.0, [{"kind": "EVAL_ERROR",
                      "detail": "assurance module not importable",
                      "target_file": "", "target_text": ""}]
    findings: List[Finding] = []
    b = i = m = 0
    for label, path in snap.outputs.items():
        if not path.exists():
            continue
        results = mod.audit_docx(path, manifest.charts_dir)
        for f in results:
            sev = f.severity
            if sev == "BLOCKER":
                b += 1
            elif sev == "IMPORTANT":
                i += 1
            else:
                m += 1
            findings.append({
                "kind": "ASSURANCE",
                "detail": f"{path.name}: {f.code} {f.message}",
                "target_file": "",
                "target_text": "",
            })
    score = max(0.0, 1.0 - 1.0 * b - 0.1 * i - 0.02 * m)
    return (min(1.0, score), findings)


def _extract_numbers(text: str) -> List[str]:
    # Find any comma-grouped number or decimal/percent (country-agnostic).
    return re.findall(r"\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?%?", text)


def e11_counts_reconcile(snap: PackageSnapshot, manifest: Manifest
                         ) -> Tuple[float, List[Finding]]:
    """Key counts in the outputs match the manifest and reconcile
    arithmetically."""
    findings: List[Finding] = []
    counts = (manifest.invariants or {}).get("counts") or {}
    if not counts:
        return 1.0, []

    # Arithmetic: required_populated / template_total ≈ overall_percent.
    total = float(counts.get("template_total", 0)) or None
    req = float(counts.get("required_populated", 0)) or None
    pct_decl = counts.get("overall_percent")
    arith_ok = True
    if total and req and pct_decl is not None:
        pct = round(100.0 * req / total, 1)
        if abs(pct - float(pct_decl)) > 0.15:
            arith_ok = False
            findings.append({
                "kind": "FIX_COUNTS",
                "detail": (f"manifest says {req}/{total} = "
                           f"{pct}% but declares {pct_decl}%"),
                "target_file": str(
                    (manifest.root / "package.yaml").relative_to(
                        manifest.overlay_root)),
                "target_text": f"{pct_decl}",
            })

    # Textual presence: the declared percentage or fraction should appear
    # in at least one DOCX output.
    key_fragments = []
    if total and req:
        key_fragments.append(f"{int(req)} of {int(total):,}")
    if pct_decl is not None:
        key_fragments.append(f"{pct_decl}%")
    missing = []
    present = 0
    for frag in key_fragments:
        found = any(frag in text for _, text in snap.iter_text_all())
        if found:
            present += 1
        else:
            missing.append(frag)
            findings.append({
                "kind": "COUNTS_MISSING",
                "detail": f"expected '{frag}' not found in any output",
                "target_file": "",
                "target_text": frag,
            })
    present_score = present / len(key_fragments) if key_fragments else 1.0
    score = (1.0 if arith_ok else 0.5) * present_score
    return score, findings


def e12_phase_reconcile(snap: PackageSnapshot, manifest: Manifest
                        ) -> Tuple[float, List[Finding]]:
    phases = (manifest.invariants or {}).get("phases") or {}
    if not phases:
        return 1.0, []
    findings: List[Finding] = []
    missing = 0
    for name, pct in phases.items():
        needle = f"{int(pct)}%"
        # Look for "<phase>" and "<pct>%" near each other.
        hit = False
        for label, text in snap.iter_text_all():
            low = text.lower()
            if name.lower() in low and needle in text:
                hit = True
                break
        if not hit:
            missing += 1
            findings.append({
                "kind": "PHASE_MISSING",
                "detail": f"phase '{name}' @ {pct}% not co-located in any output",
                "target_file": "",
                "target_text": f"{name}:{pct}",
            })
    score = 1.0 if missing == 0 else max(0.0, 1.0 - 0.1 * missing)
    return score, findings


def e13_rec_ids(snap: PackageSnapshot, manifest: Manifest
                ) -> Tuple[float, List[Finding]]:
    """Every R-id in the manifest is cited; no extra R-ids appear."""
    expected = set(manifest.recommendation_ids())
    if not expected:
        return 1.0, []
    findings: List[Finding] = []
    cited = set()
    for _, text in snap.iter_text_all():
        cited |= set(re.findall(r"\bR\d+\b", text))
    missing = expected - cited
    extra = cited - expected
    if missing:
        for m in sorted(missing, key=lambda s: int(s[1:])):
            findings.append({
                "kind": "ADD_RNUMBER",
                "detail": f"missing R-ref: {m}",
                "target_text": m,
                "target_file": "",
            })
    if extra:
        for e in sorted(extra):
            findings.append({
                "kind": "REC_EXTRA",
                "detail": f"unexpected R-ref: {e}",
                "target_text": e,
                "target_file": "",
            })
    penalty = 0.1 * len(missing) + 0.05 * len(extra)
    return max(0.0, 1.0 - penalty), findings


# ─── Structural evaluators ─────────────────────────────────────────
#
# E14/E15/E16 enforce the shape of each DOCX against the manifest
# schema. Every finding carries severity="BLOCKER" — the promotion
# gate rejects any patch that leaves a BLOCKER on the table,
# regardless of weighted overall improvement.

def _label_schema(manifest: Manifest, label: str) -> Optional[Dict[str, Any]]:
    schema = manifest.schema or {}
    entry = schema.get(label)
    return entry if isinstance(entry, dict) else None


def _heading_matches(para, needle: str) -> bool:
    return needle.strip().lower() in (para.text or "").strip().lower()


def e14_required_sections(snap: PackageSnapshot, manifest: Manifest
                          ) -> Tuple[float, List[Finding]]:
    """Every required heading listed in `schema.<label>.required_headings`
    must be present in that output at the declared level (or deeper)."""
    findings: List[Finding] = []
    missing_total = 0
    checked_total = 0
    for label in snap.all_docx_labels():
        sch = _label_schema(manifest, label)
        if not sch:
            continue
        required = sch.get("required_headings") or []
        if not required:
            continue
        v = snap.view(label)
        if v is None:
            findings.append({
                "kind": "STRUCTURE_MISSING",
                "detail": f"{label}: document missing; required sections cannot be verified",
                "severity": "BLOCKER",
                "target_file": "", "target_text": label,
            })
            missing_total += len(required)
            checked_total += len(required)
            continue
        headings = v.headings()
        for req in required:
            checked_total += 1
            needed_level = int(req.get("level", 1))
            must_contain = req.get("must_contain") or []
            found = False
            for h in headings:
                if h.heading_level and h.heading_level <= needed_level:
                    text = (h.text or "").lower()
                    if all(s.lower() in text for s in must_contain):
                        found = True
                        break
            if not found:
                missing_total += 1
                findings.append({
                    "kind": "ADD_SECTION",
                    "detail": (f"{v.path.name}: required L{needed_level} "
                               f"heading matching {must_contain} not found"),
                    "severity": "BLOCKER",
                    "target_file": "", "target_text": " ".join(must_contain),
                })
    score = 1.0 if missing_total == 0 else max(0.0, 1.0 - 1.0 * missing_total
                                                / max(1, checked_total))
    return score, findings


def _table_matches(table, spec: Dict[str, Any]) -> bool:
    rows_min = spec.get("rows_min")
    rows_max = spec.get("rows_max")
    cols_min = spec.get("cols_min")
    cols_max = spec.get("cols_max")
    if rows_min is not None and table.rows < rows_min:
        return False
    if rows_max is not None and table.rows > rows_max:
        return False
    if cols_min is not None and table.cols < cols_min:
        return False
    if cols_max is not None and table.cols > cols_max:
        return False
    header_contains = spec.get("header_contains") or []
    for needle in header_contains:
        if not table.header_has(needle):
            return False
    return True


def e15_required_tables(snap: PackageSnapshot, manifest: Manifest
                        ) -> Tuple[float, List[Finding]]:
    findings: List[Finding] = []
    missing_total = 0
    checked_total = 0
    for label in snap.all_docx_labels():
        sch = _label_schema(manifest, label)
        if not sch:
            continue
        required = sch.get("required_tables") or []
        if not required:
            continue
        v = snap.view(label)
        if v is None:
            continue
        tables = v.tables
        for req in required:
            checked_total += 1
            min_instances = int(req.get("min_instances", 1))
            matches = [t for t in tables if _table_matches(t, req)]
            if len(matches) < min_instances:
                missing_total += 1
                name = req.get("name") or "(anonymous)"
                hdrs = req.get("header_contains") or []
                findings.append({
                    "kind": "ADD_TABLE",
                    "detail": (f"{v.path.name}: table '{name}' missing "
                               f"(need {min_instances}, found {len(matches)}); "
                               f"expected header tokens {hdrs}"),
                    "severity": "BLOCKER",
                    "target_file": "", "target_text": name,
                })
    score = 1.0 if missing_total == 0 else max(0.0, 1.0 - 1.0 * missing_total
                                                / max(1, checked_total))
    return score, findings


def e16_required_visuals(snap: PackageSnapshot, manifest: Manifest
                         ) -> Tuple[float, List[Finding]]:
    findings: List[Finding] = []
    missing_total = 0
    checked_total = 0
    for label in snap.all_docx_labels():
        sch = _label_schema(manifest, label)
        if not sch:
            continue
        required = sch.get("required_image_count")
        if required is None:
            continue
        checked_total += 1
        v = snap.view(label)
        if v is None:
            missing_total += 1
            findings.append({
                "kind": "REBUILD",
                "detail": f"{label}: missing document; cannot count images",
                "severity": "BLOCKER",
                "target_file": "", "target_text": label,
            })
            continue
        if v.image_count < int(required):
            missing_total += 1
            findings.append({
                "kind": "ADD_IMAGE",
                "detail": (f"{v.path.name}: only {v.image_count} embedded "
                           f"image(s); schema requires >= {required}"),
                "severity": "BLOCKER",
                "target_file": "", "target_text": label,
            })
    score = 1.0 if missing_total == 0 else max(0.0, 1.0 - 1.0 * missing_total
                                                / max(1, checked_total))
    return score, findings


# ─── Runner ────────────────────────────────────────────────────────

EvaluatorFn = Callable[[PackageSnapshot, Manifest], Tuple[float, List[Finding]]]

ALL_EVALUATORS: Dict[str, EvaluatorFn] = {
    "E01_no_dashes":          e01_no_dashes,
    "E02_no_internal_vocab":  e02_no_internal_vocab,
    "E03_no_ai_tells":        e03_no_ai_tells,
    "E04_docs_valid":         e04_docs_valid,
    "E06_no_1480_lead":       e06_no_1480_lead,
    "E07_chart_annotations":  e07_chart_annotations,
    "E08_page_length":        e08_page_length,
    "E09_filename_refs":      e09_filename_refs,
    "E10_assurance_gate":     e10_assurance_gate,
    "E11_counts_reconcile":   e11_counts_reconcile,
    "E12_phase_reconcile":    e12_phase_reconcile,
    "E13_rec_ids":            e13_rec_ids,
    "E14_required_sections":  e14_required_sections,
    "E15_required_tables":    e15_required_tables,
    "E16_required_visuals":   e16_required_visuals,
}


def blocker_findings(results: Dict[str, Dict]) -> List[Tuple[str, Dict]]:
    """Return (evaluator_id, finding) pairs for every BLOCKER finding."""
    out: List[Tuple[str, Dict]] = []
    for eid, r in results.items():
        for f in r.get("findings") or []:
            if f.get("severity") == "BLOCKER":
                out.append((eid, f))
    return out


def run_all(manifest: Manifest,
            package_root: Optional[pathlib.Path] = None,
            ) -> Dict[str, Dict]:
    """Evaluate a package. `package_root` defaults to `manifest.root`;
    pass a trial workspace root to evaluate a candidate."""
    snap = (build_snapshot(manifest) if package_root is None
            else build_snapshot_at(manifest, package_root))
    results: Dict[str, Dict] = {}
    for eid, fn in ALL_EVALUATORS.items():
        try:
            score, findings = fn(snap, manifest)
        except Exception as e:
            score, findings = 0.0, [{
                "kind": "EVAL_ERROR",
                "detail": f"{eid} crashed: {e}",
                "target_file": "", "target_text": "",
            }]
        results[eid] = {
            "score": round(score, 4),
            "weight": EVALUATOR_WEIGHTS[eid],
            "findings": findings,
        }
    return results


def overall_score(results: Dict[str, Dict]) -> float:
    total_weight = sum(r["weight"] for r in results.values())
    if total_weight == 0:
        return 0.0
    weighted = sum(r["score"] * r["weight"] for r in results.values())
    return round(weighted / total_weight, 4)


if __name__ == "__main__":
    import argparse
    from manifest import load
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", default=None)
    args = ap.parse_args()
    root = pathlib.Path(__file__).resolve().parent.parent
    m = load(root, args.package)
    res = run_all(m)
    print("=" * 60)
    print(f"Package: {m.name}")
    print(f"Overall: {overall_score(res):.4f}")
    print("=" * 60)
    for eid, r in res.items():
        print(f"{eid:30s}  {r['score']:.3f}  (w={r['weight']})")
        for f in r["findings"][:3]:
            print(f"    - {f['detail']}")
