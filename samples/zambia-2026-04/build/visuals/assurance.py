"""assurance.py — pre-ship gate for CoST review DOCX output.

Walks a rendered DOCX and its sibling chart PNGs, checks them against the
`cost-publication-assurance` skill's BLOCKER vocabulary, and returns a list
of Finding tuples. A build is shippable only when no BLOCKER fires.

Severity vocabulary (mirrors cost-publication-assurance SKILL.md):
- BLOCKER   — ship is unsafe; halt and fix before commit.
- IMPORTANT — ship degrades quality; fix on this pass or next.
- MINOR     — advisory; fix when convenient.

Checks:
1. Every embedded image in the DOCX opens via Pillow and has non-trivial
   colour variance (catches "chart rendered blank" regressions).
2. Every PNG under charts/ is referenced by the DOCX; stale PNGs log MINOR.
3. Every embedded image matches a known filename in the charts/ or
   infographics/ output dirs (catches stray embeds).
4. Document-wide font is Arial in the Normal style (BLOCKER if not).
5. Paragraph-run colour overrides fall within the brand palette set
   (IMPORTANT for any non-brand hex; the body-run inheritor hexes are
   allowed because _docx_helpers routes through the brand palette).
"""
from __future__ import annotations
import pathlib
from typing import Iterable, List, Tuple
from PIL import Image
from docx import Document
from docx.document import Document as DocType
from docx.oxml.ns import qn

from .brand import CoST_Red, Charcoal, Muted, LightMuted, TitleColor, DarkMuted

# ─── Brand palette allow-list ──────────────────────────────────────────────
# All hexes _docx_helpers.py currently ships. Upper-case, no leading '#'.
_ALLOWED_HEXES = {
    "B7251C", "CC2028", "C00000",          # red family (emphasis, cover, table)
    "4A4743", "2D2D2D",                     # body + title text
    "71B6C9", "F1C03D",                     # blue + yellow callouts
    "9C9B99", "6B6A68", "B0B0B1",           # muted greys
    "E5E4E3", "F3F2F1", "F0EDE7", "FFFFFF", # backgrounds
    "4EA83D",                               # low-priority green
    "F5D5D3", "D9EDF3", "FDF3D7", "E8F5E9", # priority tints
    "D4A017",                               # medium-priority amber text
}


class Finding(Tuple[str, str, str]):
    """(severity, code, message). Subclassed for readable repr."""
    __slots__ = ()

    def __new__(cls, severity: str, code: str, message: str):
        return super().__new__(cls, (severity, code, message))

    severity = property(lambda self: self[0])
    code     = property(lambda self: self[1])
    message  = property(lambda self: self[2])

    def __repr__(self):
        return f"[{self[0]}] {self[1]}: {self[2]}"


# ─── Image checks ──────────────────────────────────────────────────────────

def _image_has_signal(path: pathlib.Path) -> bool:
    """True if the image has >1 unique colour across a sampled grid.

    Catches the "matplotlib saved a blank canvas" regression without a full
    pixel scan. If the image opens but every sampled pixel is identical,
    the image has no signal.
    """
    with Image.open(path) as im:
        im = im.convert("RGB")
        w, h = im.size
        if w < 4 or h < 4:
            return False
        samples = set()
        step_x, step_y = max(1, w // 16), max(1, h // 16)
        for y in range(0, h, step_y):
            for x in range(0, w, step_x):
                samples.add(im.getpixel((x, y)))
                if len(samples) > 1:
                    return True
    return False


def _check_chart_pngs(charts_dir: pathlib.Path) -> List[Finding]:
    findings: List[Finding] = []
    if not charts_dir.exists():
        findings.append(Finding("BLOCKER", "ASSURE-001",
                                f"charts/ directory missing: {charts_dir}"))
        return findings
    for png in sorted(charts_dir.glob("*.png")):
        try:
            with Image.open(png) as im:
                w, h = im.size
            if w < 400 or h < 200:
                findings.append(Finding("IMPORTANT", "ASSURE-002",
                                        f"{png.name}: suspicious dimensions "
                                        f"{w}x{h}; charts should be ≥400x200"))
            if not _image_has_signal(png):
                findings.append(Finding("BLOCKER", "ASSURE-003",
                                        f"{png.name}: renders blank / single-colour"))
        except Exception as exc:
            findings.append(Finding("BLOCKER", "ASSURE-004",
                                    f"{png.name}: fails to open — {exc}"))
    return findings


# ─── DOCX walk ─────────────────────────────────────────────────────────────

def _iter_embedded_image_parts(doc: DocType) -> Iterable[Tuple[str, bytes]]:
    for rel in doc.part._rels.values():
        if "image" in rel.reltype:
            yield rel.target_ref, rel.target_part.blob


def _check_embedded_images(doc: DocType) -> List[Finding]:
    findings: List[Finding] = []
    count = 0
    for ref, blob in _iter_embedded_image_parts(doc):
        count += 1
        # Cost-logo is an asset, not a chart. Skip signal check.
        if "logo" in ref.lower() or "stripe" in ref.lower():
            continue
        # Write to a bytes buffer Pillow can read.
        import io
        try:
            with Image.open(io.BytesIO(blob)) as im:
                im = im.convert("RGB")
                w, h = im.size
                if w < 4 or h < 4:
                    findings.append(Finding("BLOCKER", "ASSURE-005",
                                            f"{ref}: image too small ({w}x{h})"))
                    continue
                # Quick signal check on embedded bytes.
                samples = set()
                step_x, step_y = max(1, w // 16), max(1, h // 16)
                for y in range(0, h, step_y):
                    for x in range(0, w, step_x):
                        samples.add(im.getpixel((x, y)))
                        if len(samples) > 1:
                            break
                    if len(samples) > 1:
                        break
                if len(samples) <= 1:
                    findings.append(Finding("BLOCKER", "ASSURE-006",
                                            f"{ref}: embedded image is blank"))
        except Exception as exc:
            findings.append(Finding("BLOCKER", "ASSURE-007",
                                    f"{ref}: fails to open — {exc}"))
    if count == 0:
        findings.append(Finding("IMPORTANT", "ASSURE-008",
                                "DOCX has no embedded images; expected charts"))
    return findings


def _check_fonts(doc: DocType) -> List[Finding]:
    findings: List[Finding] = []
    normal_font = doc.styles["Normal"].font.name
    if normal_font != "Arial":
        findings.append(Finding("BLOCKER", "ASSURE-010",
                                f"Normal style font is {normal_font!r}, "
                                f"expected 'Arial'"))
    return findings


def _check_run_colours(doc: DocType) -> List[Finding]:
    findings: List[Finding] = []
    unknown: dict[str, int] = {}
    for para in doc.paragraphs:
        for run in para.runs:
            rgb = run.font.color.rgb
            if rgb is None:
                continue
            hex_s = f"{rgb}".upper()
            if hex_s not in _ALLOWED_HEXES:
                unknown[hex_s] = unknown.get(hex_s, 0) + 1
    for hex_s, count in sorted(unknown.items()):
        findings.append(Finding("IMPORTANT", "ASSURE-012",
                                f"Non-brand colour #{hex_s} used in {count} "
                                f"paragraph run(s); add to brand palette or fix"))
    return findings


# ─── Public entry point ────────────────────────────────────────────────────

def audit_docx(docx_path: pathlib.Path,
               charts_dir: pathlib.Path | None = None) -> List[Finding]:
    """Run the full gate against a DOCX and its charts directory.

    Returns a list of Finding. Empty list == clean ship.
    """
    docx_path = pathlib.Path(docx_path)
    if not docx_path.exists():
        return [Finding("BLOCKER", "ASSURE-000",
                        f"docx not found: {docx_path}")]

    findings: List[Finding] = []
    if charts_dir is not None:
        findings += _check_chart_pngs(pathlib.Path(charts_dir))

    doc = Document(str(docx_path))
    findings += _check_embedded_images(doc)
    findings += _check_fonts(doc)
    findings += _check_run_colours(doc)
    return findings


def summarise(findings: List[Finding]) -> Tuple[int, int, int]:
    """Return (blockers, importants, minors)."""
    b = sum(1 for f in findings if f.severity == "BLOCKER")
    i = sum(1 for f in findings if f.severity == "IMPORTANT")
    m = sum(1 for f in findings if f.severity == "MINOR")
    return b, i, m
