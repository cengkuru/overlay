"""Build the charts for the Zambia review package (v0.10).

Run: python build_charts.py

Patches applied in v0.10:
- Chart 01: red accent flipped to Linked Releases + Parties (zero/near-zero).
  The story is the silence, not the strength.
- Chart 02: unchanged; red on Implementation 2%, this one works.
- Chart 03: plain-language labels (Ready to publish / Small format fixes /
  Needs system work / Needs policy action). Denominator framing revised.
- Chart 04 REMOVED: the legal-crosswalk bar chart was misleading (overlapping
  counts, split NCC bars, contradictory editorial emphasis). The legal story
  is told in a table in the docs now.
"""
import sys, pathlib

ASSETS = pathlib.Path("/Users/cengkurumichael/.claude/skills/cost-document-design/assets")
sys.path.insert(0, str(ASSETS))

from cost_charts import style, bar_chart_mode_a, save  # noqa: E402

style()
OUT = pathlib.Path(__file__).parent.parent / "charts"
OUT.mkdir(parents=True, exist_ok=True)
SRC_TEMPLATE = "Zambia OC4IDS field-level mapping template v0.9.5, accessed 23 April 2026."

# Remove the retired chart if present on re-run.
old = OUT / "04-legal-crosswalk.png"
if old.exists():
    old.unlink()


def chart_1_oc4ids_sheet_coverage():
    """Per-sheet coverage. Red on the silent sheets, not the strongest."""
    labels = ["Linked\nReleases\n(0/6)", "Parties\n(18/968)", "Projects\n(35/353)",
              "Contracting\nProcesses\n(20/153)"]
    pct = [0.0, 1.9, 9.9, 13.1]
    fig, ax = bar_chart_mode_a(
        title="Two OC4IDS sheets carry almost no Zambia data: Linked Releases and Parties",
        subtitle="Share of OC4IDS fields populated per template sheet",
        labels=labels,
        values=pct,
        accent_index=[0, 1],
        value_labels=[f"{v:.1f}%" for v in pct],
        orientation="vertical",
        source=SRC_TEMPLATE,
    )
    save(fig, str(OUT / "01-sheet-coverage.png"))
    print("OK 01-sheet-coverage.png")


def chart_2_phase_coverage():
    """Lifecycle coverage. Red on Implementation, which is the critical gap."""
    phases = ["Identification", "Preparation", "Procurement",
              "Implementation", "Completion", "Maintenance", "Decommissioning"]
    pct = [28, 12, 21, 2, 8, 0, 0]
    fig, ax = bar_chart_mode_a(
        title="Implementation, Maintenance and Decommissioning disclose almost nothing",
        subtitle="Estimated share of applicable OC4IDS fields populated per lifecycle phase",
        labels=phases,
        values=pct,
        accent_index=3,
        value_labels=[f"{v}%" for v in pct],
        orientation="horizontal",
        source=SRC_TEMPLATE + " Phase estimates derived from mapped-path counts.",
        figsize=(6.0, 3.6),
    )
    save(fig, str(OUT / "02-phase-coverage.png"))
    print("OK 02-phase-coverage.png")


def chart_3_decision_buckets():
    """Plain-language disclosure pathways. Red on Ready to publish (the win)."""
    buckets = ["Ready to publish", "Small format fixes",
               "Needs system work", "Needs policy action"]
    counts = [35, 20, 73, 25]
    fig, ax = bar_chart_mode_a(
        title="Zambia can publish 35 fields today, 55 after small fixes",
        subtitle="OC4IDS fields by disclosure pathway, applicable to ZPPA's scope",
        labels=buckets,
        values=counts,
        accent_index=0,
        orientation="horizontal",
        source="CoST IS review of Zambia mapping template, 23 April 2026.",
        figsize=(6.0, 3.2),
    )
    save(fig, str(OUT / "03-decision-buckets.png"))
    print("OK 03-decision-buckets.png")


if __name__ == "__main__":
    chart_1_oc4ids_sheet_coverage()
    chart_2_phase_coverage()
    chart_3_decision_buckets()
