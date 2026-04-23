"""Build the charts for the Zambia review package (v0.11).

Run: python build_charts.py

v0.11 changes:
- Every chart carries one annotation explaining WHY the accent bar matters,
  per the data-storytelling skill rule "one annotation on the highest-value
  data point if it reduces interpretation effort".
- Annotation text is short (under 60 chars) and sits away from data labels.
- Charts are sized slightly larger so annotations do not crowd bars.
"""
import pathlib
from visuals.brand import apply_matplotlib_style, cost_charts_module

_cc = cost_charts_module()
if _cc is None:
    raise ImportError(
        "cost_charts skill asset not importable. Install cost-document-design "
        "skill at ~/.claude/skills/cost-document-design/ or vendor the helper."
    )
bar_chart_mode_a = _cc.bar_chart_mode_a
save = _cc.save

apply_matplotlib_style()
OUT = pathlib.Path(__file__).parent.parent / "charts"
OUT.mkdir(parents=True, exist_ok=True)
SRC_TEMPLATE = "Zambia OC4IDS field-level mapping template v0.9.5, accessed 23 April 2026."

for old in ["04-legal-crosswalk.png"]:
    p = OUT / old
    if p.exists():
        p.unlink()


def chart_1_oc4ids_sheet_coverage():
    """Red on the silent sheets; annotation flags the structural story."""
    labels = ["Linked\nReleases\n(0/6)", "Parties\n(18/968)",
              "Projects\n(35/353)", "Contracting\nProcesses\n(20/153)"]
    pct = [0.0, 1.9, 9.9, 13.1]
    fig, ax = bar_chart_mode_a(
        title="Two OC4IDS sheets carry almost no Zambia data",
        subtitle="Share of OC4IDS fields populated per template sheet",
        labels=labels,
        values=pct,
        accent_index=[0, 1],
        value_labels=[f"{v:.1f}%" for v in pct],
        orientation="vertical",
        source=SRC_TEMPLATE,
        annotation=("Silent sheets hide the\nhalf of the standard that\ntracks parties and releases",
                    0.3, 11.0),
        figsize=(7.0, 3.8),
    )
    save(fig, str(OUT / "01-sheet-coverage.png"))
    print("OK 01-sheet-coverage.png")


def chart_2_phase_coverage():
    """Red on Implementation; annotation names the NCC insight."""
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
        annotation=("NCC already collects this data\nunder s.53. It is not yet disclosed.",
                    18.0, 4.4),
        figsize=(7.5, 4.2),
    )
    save(fig, str(OUT / "02-phase-coverage.png"))
    print("OK 02-phase-coverage.png")


def chart_3_decision_buckets():
    """Red on 'Ready to publish'; annotation names the immediate win."""
    buckets = ["Ready to publish", "Small format fixes",
               "Needs system work", "Needs policy action"]
    counts = [35, 20, 73, 25]
    fig, ax = bar_chart_mode_a(
        title="35 fields can be published today. 20 more after small format fixes.",
        subtitle="OC4IDS fields by disclosure pathway, applicable to ZPPA's scope",
        labels=buckets,
        values=counts,
        accent_index=0,
        orientation="horizontal",
        source="CoST IS review of Zambia mapping template, 23 April 2026.",
        annotation=("Immediate win: no new\nsystem work, no new law.",
                    45.0, 0.0),
        figsize=(7.0, 3.6),
    )
    save(fig, str(OUT / "03-decision-buckets.png"))
    print("OK 03-decision-buckets.png")


def infographic_headline_stats():
    """Three-card glance anchor for the review letter §1 opening."""
    from visuals.infographics import stat_card_row
    stat_card_row([
        ("73",       "OC4IDS fields mapped",      "Across four template sheets"),
        ("2 of 4",   "Template sheets near zero", "Linked Releases and Parties"),
        ("47 of 48", "Source elements traced",    "From ZPPA e-GP into OC4IDS"),
    ], OUT / "04-headline-stats.png")
    print("OK 04-headline-stats.png")


def infographic_integration_pathway():
    """4-step process diagram for §6 , the 'disclosure gap, not data gap' thesis."""
    from visuals.infographics import process_diagram
    process_diagram([
        ("Data collected",  "NCC under s.53"),
        ("Held by NCC",     "Monitoring records"),
        ("Not disclosed",   "No OC4IDS path"),
        ("Integration fix", "ZPPA ↔ NCC bridge"),
    ], OUT / "05-integration-pathway.png",
       title="Most missing implementation data is already collected",
       source="CoST IS review of Zambia mapping template, 23 April 2026.")
    print("OK 05-integration-pathway.png")


if __name__ == "__main__":
    chart_1_oc4ids_sheet_coverage()
    chart_2_phase_coverage()
    chart_3_decision_buckets()
    infographic_headline_stats()
    infographic_integration_pathway()
