"""brand.py — single source of truth for visual tokens.

Every hex and every matplotlib style setting in this pipeline comes through
here. Other modules import these names; no module under visuals/ or build/
should define its own colours.

Rule: if cost_charts (from the user's cost-document-design skill) is importable,
delegate to it so palette drift is impossible. Otherwise fall back to the local
rcParams below so the build never fails on a missing skill install.
"""
from __future__ import annotations
import sys
import pathlib

# ─── Canonical CoST palette (matches _docx_helpers.py + cost_charts.py) ────
CoST_Red    = "#B7251C"
Charcoal    = "#4A4743"
Muted       = "#9C9B99"
LightMuted  = "#D7D4CF"
TitleColor  = "#2D2D2D"
DarkMuted   = "#6B6A68"

# ─── Layout tokens ─────────────────────────────────────────────────────────
# Landscape A4 at 20mm margins → 25.7 cm content
content_width_cm_landscape = 25.7
# Portrait A4 at 22mm margins → 16.6 cm content
content_width_cm_portrait = 16.6

# ─── Figure sizes by archetype (inches, matplotlib convention) ─────────────
# These carry the same proportions the current three PNGs use, so existing
# charts remain byte-stable when they migrate through this module.
figsize_vertical_bar   = (7.0, 3.8)
figsize_horizontal_bar = (7.5, 4.2)
figsize_compact_bar    = (7.0, 3.6)
figsize_slopegraph     = (7.5, 4.0)
figsize_small_multi    = (8.0, 4.5)

# ─── Skill delegate resolution ─────────────────────────────────────────────
_SKILL_ASSETS = pathlib.Path(
    "/Users/cengkurumichael/.claude/skills/cost-document-design/assets"
)


def _load_cost_charts():
    """Return the cost_charts module if available, else None."""
    if str(_SKILL_ASSETS) not in sys.path:
        sys.path.insert(0, str(_SKILL_ASSETS))
    try:
        import cost_charts  # type: ignore
        return cost_charts
    except ImportError:
        return None


def apply_matplotlib_style() -> None:
    """Apply CoST matplotlib style. Delegates to cost_charts.style() if present.

    Fallback rcParams are byte-compatible with the delegate's defaults so the
    three existing PNGs regenerate identically.
    """
    cc = _load_cost_charts()
    if cc is not None:
        cc.style()
        return

    # Fallback — mirrors cost_charts.style()
    import matplotlib as mpl
    mpl.rcParams.update({
        "font.family":      "Arial",
        "font.size":        10,
        "axes.edgecolor":   Muted,
        "axes.spines.top":  False,
        "axes.spines.right": False,
        "axes.labelcolor":  Charcoal,
        "xtick.color":      Charcoal,
        "ytick.color":      Charcoal,
    })


def cost_charts_module():
    """Expose the skill's cost_charts module for other visuals submodules.

    Returns None if the skill is not installed; callers must handle that
    (e.g., charts.py raises a clear ImportError with install guidance).
    """
    return _load_cost_charts()
