"""Rule-based patch generator.

Each mutation returns a PatchPlan whose `files` dict maps absolute
paths INSIDE the package root to the full replacement content. The
mutator honours `target_file` from findings — it never scans every
build script by default.

No LLM. Mutations listed in `MUTATION_DISPATCH` all resolve to real
functions; there are no ghost entries. Unsupported evaluators simply
return no patch and the loop logs "no mutation available".
"""
from __future__ import annotations
import pathlib
import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Set

from manifest import Manifest


@dataclass
class PatchPlan:
    files: Dict[pathlib.Path, str]
    description: str
    targeted_eval_id: str
    mutation_class: str

    def relative_files(self, manifest: Manifest) -> List[str]:
        out = []
        for p in self.files:
            try:
                out.append(str(p.relative_to(manifest.root)))
            except ValueError:
                out.append(str(p))
        return out


# ─── Helpers ────────────────────────────────────────────────────────

def _findings_target_paths(manifest: Manifest,
                           findings: List[Dict[str, str]]) -> List[pathlib.Path]:
    """Resolve `target_file` values to absolute paths under the package.

    Paths may be recorded relative to the overlay root (as the new
    evaluators emit) or bare filenames (legacy). Duplicates preserved-
    insertion-order removed. Non-whitelisted paths are dropped.
    """
    whitelist = {(manifest.build_dir / n).resolve()
                 for n in manifest.mutation_whitelist}
    resolved: List[pathlib.Path] = []
    seen: Set[pathlib.Path] = set()
    for f in findings:
        t = f.get("target_file") or ""
        if not t:
            continue
        p = pathlib.Path(t)
        if not p.is_absolute():
            # Try overlay-root-relative
            cand = (manifest.overlay_root / p).resolve()
            if cand.exists():
                p = cand
            else:
                # Try build-dir-relative (bare script name)
                cand = (manifest.build_dir / p).resolve()
                if cand.exists():
                    p = cand
                else:
                    continue
        else:
            p = p.resolve()
        if p not in whitelist:
            continue
        if p not in seen:
            resolved.append(p)
            seen.add(p)
    return resolved


def _fallback_whitelist_paths(manifest: Manifest) -> List[pathlib.Path]:
    return [(manifest.build_dir / n).resolve()
            for n in manifest.mutation_whitelist
            if (manifest.build_dir / n).exists()]


def _targets_from(manifest: Manifest,
                  findings: List[Dict[str, str]]) -> List[pathlib.Path]:
    resolved = _findings_target_paths(manifest, findings)
    return resolved or _fallback_whitelist_paths(manifest)


# ─── Mutations ──────────────────────────────────────────────────────

def mutate_replace_dash(manifest: Manifest, targeted_eval: str,
                        findings: List[Dict[str, str]]) -> Optional[PatchPlan]:
    files: Dict[pathlib.Path, str] = {}
    for path in _targets_from(manifest, findings):
        content = path.read_text()
        new = content.replace("—", ",").replace("–", "-")
        if new != content:
            files[path] = new
    if not files:
        return None
    return PatchPlan(files, f"Replace em/en dashes in {len(files)} script(s)",
                     targeted_eval, "REPLACE_DASH")


def mutate_sub_forbidden(manifest: Manifest, targeted_eval: str,
                         findings: List[Dict[str, str]]) -> Optional[PatchPlan]:
    vocab = manifest.forbidden_internal_vocab
    cxx_pattern = manifest.section_code_pattern
    cxx_map = manifest.section_code_replacements

    terms_needed: Set[str] = set()
    cxx_codes: Set[str] = set()
    for f in findings:
        t = (f.get("target_text") or "").strip()
        if not t:
            continue
        if t in vocab:
            terms_needed.add(t)
        elif cxx_pattern and re.fullmatch(cxx_pattern, t):
            cxx_codes.add(t)
        else:
            # May be a comma-joined section-code set
            for piece in t.split(","):
                piece = piece.strip()
                if cxx_pattern and re.fullmatch(cxx_pattern, piece):
                    cxx_codes.add(piece)
    if not terms_needed and not cxx_codes:
        return None

    files: Dict[pathlib.Path, str] = {}
    for path in _targets_from(manifest, findings):
        content = path.read_text()
        new = content
        for term in terms_needed:
            new = re.sub(rf"\b{re.escape(term)}\b", vocab[term], new)
        for code in cxx_codes:
            repl = cxx_map.get(code, "this section")
            new = re.sub(rf"\b{re.escape(code)}\b", repl, new)
        if new != content:
            files[path] = new
    if not files:
        return None
    return PatchPlan(files,
                     f"Substitute {len(terms_needed) + len(cxx_codes)} internal term(s)",
                     targeted_eval, "SUB_FORBIDDEN")


def mutate_drop_ai_tell(manifest: Manifest, targeted_eval: str,
                        findings: List[Dict[str, str]]) -> Optional[PatchPlan]:
    tells = manifest.ai_tells
    terms_needed: Set[str] = set()
    for f in findings:
        t = (f.get("target_text") or "").lower().strip()
        if t in tells:
            terms_needed.add(t)
    if not terms_needed:
        return None

    files: Dict[pathlib.Path, str] = {}
    for path in _targets_from(manifest, findings):
        content = path.read_text()
        new = content
        for term in terms_needed:
            new = re.sub(rf"\b{re.escape(term)}\b",
                         tells[term], new, flags=re.I)
        if new != content:
            files[path] = new
    if not files:
        return None
    return PatchPlan(files, f"Replace {len(terms_needed)} AI-tell phrase(s)",
                     targeted_eval, "DROP_AI_TELL")


def mutate_remove_1480(manifest: Manifest, targeted_eval: str,
                       findings: List[Dict[str, str]]) -> Optional[PatchPlan]:
    """Only mutate build scripts whose generated paragraphs will land
    in *forbidden* contexts. The evaluator already distinguishes
    forbidden vs advisory findings; we drop advisory ones here.
    """
    forbidden = [f for f in findings
                 if "advisory" not in f.get("detail", "").lower()
                 and f.get("kind") == "REMOVE_1480"]
    if not forbidden:
        return None

    literal = (manifest.context_policy or {}).get(
        "template_total_literal", "1,480")
    literal_re = re.escape(literal).replace(",", r"[,]?")
    patterns = [
        (re.compile(rf"(\d{{1,3}}(?:,\d{{3}})?|\d+)\s+of\s+{literal_re}\s+"
                    rf"(?:OC4IDS\s+)?(?:template\s+)?slots?"),
         lambda m: f"{m.group(1)} OC4IDS fields"),
        (re.compile(rf"{literal_re}\s+OC4IDS\s+template\s+slots?"),
         lambda m: "the OC4IDS universe"),
        (re.compile(rf"{literal_re}\s+slots?\b"),
         lambda m: "the OC4IDS universe"),
        (re.compile(rf"\b{literal_re}\b"),
         lambda m: "the OC4IDS universe"),
    ]
    files: Dict[pathlib.Path, str] = {}
    for path in _targets_from(manifest, forbidden):
        content = path.read_text()
        new = content
        for pat, repl in patterns:
            new = pat.sub(repl, new)
        if new != content:
            files[path] = new
    if not files:
        return None
    return PatchPlan(files, f"Remove forbidden-context '{literal}' references",
                     targeted_eval, "REMOVE_1480")


def mutate_fix_filename_ref(manifest: Manifest, targeted_eval: str,
                            findings: List[Dict[str, str]]) -> Optional[PatchPlan]:
    migrations = manifest.filename_migrations
    if not migrations:
        return None
    files: Dict[pathlib.Path, str] = {}
    for path in _targets_from(manifest, findings):
        content = path.read_text()
        new = content
        for bad, good in migrations:
            new = new.replace(bad, good)
        if new != content:
            files[path] = new
    if not files:
        return None
    return PatchPlan(files, f"Apply {len(migrations)} filename migration(s)",
                     targeted_eval, "FIX_FILENAME_REF")


# ─── Dispatch ──────────────────────────────────────────────────────

MUTATION_DISPATCH: Dict[str, Callable] = {
    "E01_no_dashes":         mutate_replace_dash,
    "E02_no_internal_vocab": mutate_sub_forbidden,
    "E03_no_ai_tells":       mutate_drop_ai_tell,
    "E06_no_1480_lead":      mutate_remove_1480,
    "E09_filename_refs":     mutate_fix_filename_ref,
    # E04 (docs valid): no mutation — rebuild is itself the fix.
    # E05 subsumed by E13; E13 requires editorial content not mutable by rule.
    # E07/E08 (chart annotations / page length): mutations intentionally
    # deferred. E08 is advisory; E07 blockers require human review today.
    # E10 composed of assurance findings — individual fixes land under
    # E01/E02/E07 etc.; no standalone mutation.
    # E11/E12/E13 require data/content edits, not rule-driven mutations.
}


def propose(manifest: Manifest, eval_id: str,
            result: Dict) -> Optional[PatchPlan]:
    """Propose a single patch for the given evaluator result, or None
    if no rule-driven mutation exists for this evaluator."""
    fn = MUTATION_DISPATCH.get(eval_id)
    if fn is None:
        return None
    findings = result.get("findings", []) or []
    return fn(manifest, eval_id, findings)


# ─── Bundling ──────────────────────────────────────────────────────

def bundle(patches: List[PatchPlan]) -> Optional[PatchPlan]:
    """Combine commutative patches that share overlapping file sets.

    Later mutations win on a per-file basis. The description lists the
    mutation classes folded together. Returns None if `patches` is empty.
    """
    if not patches:
        return None
    if len(patches) == 1:
        return patches[0]
    merged: Dict[pathlib.Path, str] = {}
    classes: List[str] = []
    evals: List[str] = []
    for p in patches:
        classes.append(p.mutation_class)
        evals.append(p.targeted_eval_id)
        # For each file, start from the original on disk so we can stack
        # replacements deterministically: the first patch's content, then
        # subsequent patches re-applied on top.
        for path, content in p.files.items():
            merged[path] = content
    return PatchPlan(
        files=merged,
        description=f"bundle({len(patches)}): " + ", ".join(classes),
        targeted_eval_id=evals[0],
        mutation_class="BUNDLE:" + "+".join(classes),
    )
