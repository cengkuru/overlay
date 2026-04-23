"""Rule-based patch generator.

Each mutation is a single-file, single-hunk edit. No LLM. No cross-file
refactors. If a weakness has no known mutation, the mutator returns None
and the loop halts with a human-review note.
"""
from __future__ import annotations
import pathlib
import re
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PatchPlan:
    files: Dict[pathlib.Path, str]
    description: str
    targeted_eval_id: str
    mutation_class: str


BUILD_SCRIPTS = [
    "samples/zambia-2026-04/build/build_review_and_reference.py",
    "samples/zambia-2026-04/build/build_final_report.py",
    "samples/zambia-2026-04/build/build_charts.py",
]


def mutate_replace_dash(root, targeted_eval):
    files = {}
    for rel in BUILD_SCRIPTS:
        path = root / rel
        if not path.exists():
            continue
        content = path.read_text()
        if "—" not in content and "–" not in content:
            continue
        new = content.replace("—", ",").replace("–", "-")
        if new != content:
            files[path] = new
    if not files:
        return None
    return PatchPlan(files, f"Replace em/en dashes in {len(files)} script(s)",
                     targeted_eval, "REPLACE_DASH")


SAFE_SUBSTITUTIONS = {
    "Overlay": "this review",
    "Gate score": "review score (internal)",
    "gate item": "review item (internal)",
    "Reviewer Gate Check": "review methodology",
    "Full Rubric": "review methodology",
    "Part A": "the author checklist",
    "Part B": "the triage step",
    "Part C": "the full review",
}


def mutate_sub_forbidden(root, targeted_eval, findings):
    files = {}
    terms_needed = set()
    for f in findings:
        t = f.get("target_text", "")
        if t and t in SAFE_SUBSTITUTIONS:
            terms_needed.add(t)
        elif t:
            for piece in t.split(","):
                if re.match(r"C\d{1,2}", piece):
                    terms_needed.add(piece)
    if not terms_needed:
        return None

    for rel in BUILD_SCRIPTS:
        path = root / rel
        if not path.exists():
            continue
        content = path.read_text()
        new = content
        for term in terms_needed:
            if term in SAFE_SUBSTITUTIONS:
                new = re.sub(rf"\b{re.escape(term)}\b",
                             SAFE_SUBSTITUTIONS[term], new)
            elif re.match(r"C\d{1,2}", term):
                replacement = {
                    "C0": "the quantitative backbone",
                    "C5": "the lifecycle findings section",
                    "C6": "the gap typology section",
                    "C8": "the legal alignment section",
                    "C9": "the non-template fields section",
                    "C10": "the recommendations section",
                    "C11": "the roadmap section",
                }.get(term, "this section")
                new = re.sub(rf"\b{re.escape(term)}\b", replacement, new)
        if new != content:
            files[path] = new
    if not files:
        return None
    return PatchPlan(files, f"Substitute {len(terms_needed)} internal term(s)",
                     targeted_eval, "SUB_FORBIDDEN")


AI_TELL_REPLACEMENTS = {
    "delve": "examine",
    "leverage": "use",
    "utilize": "use",
    "utilizes": "uses",
    "utilized": "used",
    "seamless": "smooth",
    "seamlessly": "smoothly",
    "cutting-edge": "new",
    "groundbreaking": "significant",
    "paradigm shift": "change",
    "synergy": "cooperation",
    "holistic": "complete",
    "transformative": "significant",
    "fostering": "building",
}


def mutate_drop_ai_tell(root, targeted_eval, findings):
    files = {}
    terms_needed = set()
    for f in findings:
        t = f.get("target_text", "").lower()
        if t in AI_TELL_REPLACEMENTS:
            terms_needed.add(t)
    if not terms_needed:
        return None

    for rel in BUILD_SCRIPTS:
        path = root / rel
        if not path.exists():
            continue
        content = path.read_text()
        new = content
        for term in terms_needed:
            new = re.sub(rf"\b{re.escape(term)}\b",
                         AI_TELL_REPLACEMENTS[term], new, flags=re.I)
        if new != content:
            files[path] = new
    if not files:
        return None
    return PatchPlan(files, f"Replace {len(terms_needed)} AI-tell phrase(s)",
                     targeted_eval, "DROP_AI_TELL")


def mutate_remove_1480(root, targeted_eval, findings):
    files = {}
    patterns = [
        (re.compile(r"(\d{1,3}(?:,\d{3})?|\d+)\s+of\s+1[,]?480\s+(?:OC4IDS\s+)?(?:template\s+)?slots?"),
         lambda m: f"{m.group(1)} OC4IDS fields"),
        (re.compile(r"1[,]?480\s+OC4IDS\s+template\s+slots?"),
         lambda m: "the OC4IDS universe"),
        (re.compile(r"1[,]?480\s+slots?\b"),
         lambda m: "the OC4IDS universe"),
        (re.compile(r"\b1[,]?480\b"),
         lambda m: "the OC4IDS universe"),
    ]
    for rel in BUILD_SCRIPTS:
        path = root / rel
        if not path.exists():
            continue
        content = path.read_text()
        new = content
        for pat, repl in patterns:
            new = pat.sub(repl, new)
        if new != content:
            files[path] = new
    if not files:
        return None
    return PatchPlan(files, "Remove '1,480' denominator from build strings",
                     targeted_eval, "REMOVE_1480")


def mutate_fix_filename_ref(root, targeted_eval, findings):
    files = {}
    for rel in BUILD_SCRIPTS:
        path = root / rel
        if not path.exists():
            continue
        content = path.read_text()
        new = content.replace("03-sample-final-report.docx",
                              "02-sample-final-report.docx")
        if new != content:
            files[path] = new
    if not files:
        return None
    return PatchPlan(files, "Update stale filename reference 03-* → 02-*",
                     targeted_eval, "FIX_FILENAME_REF")


def propose(root, eval_id, result):
    findings = result.get("findings", [])
    classes = {f.get("kind") for f in findings}

    if eval_id == "E01_no_dashes" or "REPLACE_DASH" in classes:
        return mutate_replace_dash(root, eval_id)
    if eval_id == "E02_no_internal_vocab" or "SUB_FORBIDDEN" in classes:
        return mutate_sub_forbidden(root, eval_id, findings)
    if eval_id == "E03_no_ai_tells" or "DROP_AI_TELL" in classes:
        return mutate_drop_ai_tell(root, eval_id, findings)
    if eval_id == "E06_no_1480_lead" or "REMOVE_1480" in classes:
        return mutate_remove_1480(root, eval_id, findings)
    if eval_id == "E09_filename_refs" or "FIX_FILENAME_REF" in classes:
        return mutate_fix_filename_ref(root, eval_id, findings)
    return None
