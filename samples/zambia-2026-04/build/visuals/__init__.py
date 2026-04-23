"""visuals — CoST review visuals package.

Single import surface for brand tokens, charts, infographics, imagery, and
the pre-ship assurance gate.
"""
from .brand import (
    apply_matplotlib_style,
    CoST_Red, Charcoal, Muted, LightMuted, TitleColor, DarkMuted,
    content_width_cm_landscape, content_width_cm_portrait,
)

__all__ = [
    "apply_matplotlib_style",
    "CoST_Red", "Charcoal", "Muted", "LightMuted", "TitleColor", "DarkMuted",
    "content_width_cm_landscape", "content_width_cm_portrait",
]
