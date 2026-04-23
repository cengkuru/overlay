"""infographics.py — programmatic, deterministic infographic patterns.

Rule: no AI. Every infographic in a CoST review contains numbers, comparisons,
or structural relationships. Those fail silently under AI image generation.
These functions compose matplotlib primitives and return PNG paths.

Public API:
    stat_card_row(cards, out_path, figsize=None) -> Path
    process_diagram(steps, out_path, title=None, source=None) -> Path
    decision_bucket_strip(buckets, out_path) -> Path  [reserved for next doc]
    cover_photo_strip(photo_paths, out_path, target_width_cm) -> Path
"""
from __future__ import annotations
import pathlib
from typing import Sequence, Tuple, Optional

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from PIL import Image

from .brand import (
    CoST_Red, Charcoal, Muted, LightMuted, TitleColor, DarkMuted,
    apply_matplotlib_style,
)


# ─── Stat-card row ─────────────────────────────────────────────────────────

def stat_card_row(
    cards: Sequence[Tuple[str, str]] | Sequence[Tuple[str, str, str]],
    out_path: str | pathlib.Path,
    *,
    figsize: Tuple[float, float] = (12.0, 3.0),
    accent: str = CoST_Red,
    dpi: int = 300,
) -> pathlib.Path:
    """Render a horizontal row of headline stat cards.

    `cards` is a sequence of (value, label) or (value, label, sublabel) tuples.
    The first card gets the red accent top rule; the rest use the muted grey.

    Example:
        stat_card_row([
            ("73",  "OC4IDS fields mapped", "Across four template sheets"),
            ("2 of 4", "Template sheets near zero", "Linked Releases and Parties"),
            ("47 of 48", "Source elements traced", "From ZPPA e-GP into OC4IDS"),
        ], "../charts/04-headline-stats.png")
    """
    apply_matplotlib_style()
    out_path = pathlib.Path(out_path)
    n = len(cards)
    assert 2 <= n <= 5, "stat_card_row expects 2–5 cards"

    fig, axes = plt.subplots(1, n, figsize=figsize)
    fig.patch.set_facecolor("white")

    for i, ax in enumerate(axes):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        card = cards[i]
        value = card[0]
        label = card[1]
        sub = card[2] if len(card) > 2 else None

        rule_color = accent if i == 0 else Muted
        # Top accent rule
        ax.add_patch(patches.Rectangle(
            (0.05, 0.86), 0.90, 0.04,
            facecolor=rule_color, edgecolor="none",
        ))
        # Value
        ax.text(0.5, 0.55, value,
                ha="center", va="center",
                fontsize=36, fontweight="bold",
                color=TitleColor, family="Arial")
        # Label
        ax.text(0.5, 0.25, label,
                ha="center", va="center",
                fontsize=11, fontweight="bold",
                color=Charcoal, family="Arial",
                wrap=True)
        # Sublabel
        if sub:
            ax.text(0.5, 0.10, sub,
                    ha="center", va="center",
                    fontsize=9, color=DarkMuted, family="Arial",
                    wrap=True)

    plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.05, wspace=0.08)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    return out_path


# ─── Process diagram ───────────────────────────────────────────────────────

def process_diagram(
    steps: Sequence[Tuple[str, str]],
    out_path: str | pathlib.Path,
    *,
    title: Optional[str] = None,
    source: Optional[str] = None,
    accent_index: int = -1,
    figsize: Tuple[float, float] = (12.0, 3.2),
    dpi: int = 300,
) -> pathlib.Path:
    """Render a horizontal boxes-and-arrows process diagram.

    `steps` is a sequence of (heading, detail) pairs. `accent_index` points to
    the box that carries the insight — -1 means the last box (the fix).

    Example:
        process_diagram([
            ("Data collected",  "NCC under s.53"),
            ("Held by NCC",     "Monitoring records"),
            ("Not disclosed",   "No OC4IDS path"),
            ("Integration fix", "ZPPA ↔ NCC bridge"),
        ], "../charts/05-integration-pathway.png",
           title="Zambia's implementation gap is a disclosure gap",
           source="CoST IS review of Zambia mapping template, 23 April 2026.")
    """
    apply_matplotlib_style()
    out_path = pathlib.Path(out_path)
    n = len(steps)
    assert 3 <= n <= 6, "process_diagram expects 3–6 steps"
    if accent_index < 0:
        accent_index = n + accent_index

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Title (insight title convention)
    if title:
        fig.text(0.02, 0.93, title,
                 ha="left", va="top",
                 fontsize=13, fontweight="bold",
                 color=TitleColor, family="Arial")

    # Geometry
    box_w = 0.86 / n - 0.015
    box_h = 0.50
    y_bottom = 0.18
    y_top = y_bottom + box_h
    y_mid = (y_bottom + y_top) / 2
    left_pad = 0.07

    arrow_gap = 0.008

    for i, (heading, detail) in enumerate(steps):
        x_left = left_pad + i * (box_w + 0.015)
        x_right = x_left + box_w
        is_accent = (i == accent_index)
        face = CoST_Red if is_accent else "white"
        edge = CoST_Red if is_accent else Muted
        heading_color = "white" if is_accent else TitleColor
        detail_color = "white" if is_accent else Charcoal

        box = FancyBboxPatch(
            (x_left, y_bottom), box_w, box_h,
            boxstyle="round,pad=0.005,rounding_size=0.015",
            facecolor=face, edgecolor=edge, linewidth=1.5,
        )
        ax.add_patch(box)

        # Heading
        ax.text(x_left + box_w / 2, y_bottom + box_h * 0.68, heading,
                ha="center", va="center",
                fontsize=11, fontweight="bold",
                color=heading_color, family="Arial",
                wrap=True)
        # Detail
        ax.text(x_left + box_w / 2, y_bottom + box_h * 0.32, detail,
                ha="center", va="center",
                fontsize=9,
                color=detail_color, family="Arial",
                wrap=True)

        # Arrow to next box
        if i < n - 1:
            x_arrow_start = x_right + arrow_gap
            x_arrow_end = x_right + 0.015 - arrow_gap
            arrow = FancyArrowPatch(
                (x_arrow_start, y_mid), (x_arrow_end, y_mid),
                arrowstyle="-|>", mutation_scale=14,
                color=Muted, linewidth=1.5,
            )
            ax.add_patch(arrow)

    # Source footer
    if source:
        fig.text(0.02, 0.04, f"Source: {source}",
                 ha="left", va="bottom",
                 fontsize=8, style="italic",
                 color=DarkMuted, family="Arial")

    fig.savefig(out_path, dpi=dpi, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    return out_path


# ─── Cover photo strip (fixes alignment with red title block) ─────────────

def cover_photo_strip(
    photo_paths: Sequence[str | pathlib.Path],
    out_path: str | pathlib.Path,
    *,
    target_width_cm: float,
    strip_height_mm: float = 50.0,
    gutter_px: int = 8,
    dpi: int = 300,
) -> pathlib.Path:
    """Compose photos into a single PNG at the target content width.

    Solves the cover-page misalignment problem: when three photos are embedded
    in a 3-column Word table, Word's cell margins and borders push them past
    the red title block below. Rendering one PNG at `target_width_cm` and
    embedding a single centered image guarantees the photo strip ends at
    exactly the same position as the red block.

    Inputs:
        photo_paths: 2-4 photo paths (typically the stock-africa-* jpegs).
        out_path: where to write the composed PNG.
        target_width_cm: the document's content width in cm (16.6 portrait,
            25.7 landscape). The output PNG is rendered at this width * dpi
            pixels so it embeds at exactly that cm width with no scaling.
        strip_height_mm: vertical size of the strip at render.
        gutter_px: small white gap between photos, in pixels at render dpi.

    Returns the out_path.
    """
    out_path = pathlib.Path(out_path)
    n = len(photo_paths)
    assert 2 <= n <= 4, "cover_photo_strip expects 2-4 photos"

    # Convert cm/mm to pixels at the target dpi.
    # 1 cm = 0.3937 inches → px = cm * (dpi / 2.54)
    target_w_px = int(round(target_width_cm * dpi / 2.54))
    strip_h_px  = int(round(strip_height_mm / 10 * dpi / 2.54))

    # Each sub-photo is (target_w_px - (n-1)*gutter_px) / n wide.
    photo_w_px = (target_w_px - (n - 1) * gutter_px) // n
    # Distribute rounding so total equals target_w_px exactly.
    widths = [photo_w_px] * n
    drift = target_w_px - (sum(widths) + (n - 1) * gutter_px)
    widths[-1] += drift  # absorb drift on the last tile

    canvas = Image.new("RGB", (target_w_px, strip_h_px), color=(255, 255, 255))
    x = 0
    for i, p in enumerate(photo_paths):
        with Image.open(p) as src:
            src = src.convert("RGB")
            # Center-crop to the tile aspect ratio, then resize.
            tile_w, tile_h = widths[i], strip_h_px
            src_w, src_h = src.size
            target_aspect = tile_w / tile_h
            src_aspect = src_w / src_h
            if src_aspect > target_aspect:
                # source is wider; crop horizontally
                new_src_w = int(round(src_h * target_aspect))
                x0 = (src_w - new_src_w) // 2
                src_crop = src.crop((x0, 0, x0 + new_src_w, src_h))
            else:
                # source is taller; crop vertically
                new_src_h = int(round(src_w / target_aspect))
                y0 = (src_h - new_src_h) // 2
                src_crop = src.crop((0, y0, src_w, y0 + new_src_h))
            src_resized = src_crop.resize((tile_w, tile_h), Image.LANCZOS)
            canvas.paste(src_resized, (x, 0))
        x += widths[i]
        if i < n - 1:
            x += gutter_px

    canvas.save(out_path, "PNG", dpi=(dpi, dpi))
    return out_path


# ─── Decision bucket strip (reserved, not used in Zambia letter) ───────────

def decision_bucket_strip(
    buckets: Sequence[Tuple[str, int, str]],
    out_path: str | pathlib.Path,
    *,
    figsize: Tuple[float, float] = (12.0, 3.5),
    source: Optional[str] = None,
    dpi: int = 300,
) -> pathlib.Path:
    """Render a horizontal decision-bucket strip. Reserved for next country.

    `buckets` is a sequence of (label, count, status) where status is one of
    {"ready", "fixes", "system", "policy"}.
    """
    apply_matplotlib_style()
    out_path = pathlib.Path(out_path)
    colors = {
        "ready":  CoST_Red,
        "fixes":  "#71B6C9",  # BLUE from brand palette
        "system": "#F1C03D",  # YELLOW
        "policy": DarkMuted,
    }

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    n = len(buckets)
    box_w = 0.90 / n - 0.02
    left_pad = 0.05

    for i, (label, count, status) in enumerate(buckets):
        x_left = left_pad + i * (box_w + 0.02)
        color = colors.get(status, Muted)

        ax.add_patch(patches.Rectangle(
            (x_left, 0.78), box_w, 0.04,
            facecolor=color, edgecolor="none",
        ))
        ax.text(x_left + box_w / 2, 0.50, str(count),
                ha="center", va="center",
                fontsize=32, fontweight="bold",
                color=TitleColor, family="Arial")
        ax.text(x_left + box_w / 2, 0.20, label,
                ha="center", va="center",
                fontsize=10, fontweight="bold",
                color=Charcoal, family="Arial", wrap=True)

    if source:
        fig.text(0.05, 0.03, f"Source: {source}",
                 fontsize=8, style="italic", color=DarkMuted, family="Arial")

    fig.savefig(out_path, dpi=dpi, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    return out_path
