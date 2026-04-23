"""Build the 4 charts for the Zambia review package.

Run: python build_charts.py
"""
import sys, pathlib

ASSETS = pathlib.Path("/Users/cengkurumichael/.claude/skills/cost-document-design/assets")
sys.path.insert(0, str(ASSETS))

from cost_charts import style, bar_chart_mode_a, save  # noqa: E402

style()
OUT = pathlib.Path(__file__).parent.parent / "charts"
OUT.mkdir(parents=True, exist_ok=True)
SRC_TEMPLATE = "Zambia OC4IDS Field-Level Mapping Template v0.9.5, accessed 2026-04-23. n=1,480 template slots."


def chart_1_oc4ids_sheet_coverage():
    labels = ["Contracting\nProcesses\n(20/153)", "Projects\n(35/353)", "Parties\n(18/968)", "Linked\nReleases\n(0/6)"]
    pct = [13.1, 9.9, 1.9, 0.0]
    fig, ax = bar_chart_mode_a(
        title="Zambia mapped 73 of 1,480 OC4IDS fields; two sheets sit near zero",
        subtitle="Share of OC4IDS fields mapped per sheet in Zambia's template",
        labels=labels,
        values=pct,
        accent_index=0,
        value_labels=[f"{v:.1f}%" for v in pct],
        orientation="vertical",
        source=SRC_TEMPLATE,
    )
    save(fig, str(OUT / "01-sheet-coverage.png"))
    print("OK 01-sheet-coverage.png")


def chart_2_phase_coverage():
    phases = ["Identification", "Preparation", "Procurement",
              "Implementation", "Completion", "Maintenance", "Decommissioning"]
    pct = [28, 12, 21, 2, 8, 0, 0]
    fig, ax = bar_chart_mode_a(
        title="Implementation, Maintenance and Decommissioning disclose almost nothing",
        subtitle="Estimated share of OC4IDS fields populated per lifecycle phase (Zambia)",
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
    buckets = ["(a) Publish now", "(b) Light transformation",
               "(c) System change", "(d) Legal/institutional"]
    counts = [35, 20, 73, 25]
    fig, ax = bar_chart_mode_a(
        title="Zambia can publish 35 OC4IDS fields immediately from the e-GP system",
        subtitle="Estimated count of OC4IDS fields by disclosure pathway",
        labels=buckets,
        values=counts,
        accent_index=0,
        orientation="horizontal",
        source="Overlay classification applied to Zambia mapping template, 2026-04-23.",
        figsize=(6.0, 3.2),
    )
    save(fig, str(OUT / "03-decision-buckets.png"))
    print("OK 03-decision-buckets.png")


def chart_4_legal_crosswalk():
    laws = ["ATI Act 2023\n(s.8 proactive)",
            "NCC Act 2020\n(s.53 monitoring)",
            "ZPPA Act 2020\n(s.67, s.70)",
            "NCC Act 2020\n(s.33 register)"]
    counts = [46, 55, 20, 18]
    fig, ax = bar_chart_mode_a(
        title="Zambia's existing law already authorises publication of 46 OC4IDS fields",
        subtitle="OC4IDS fields each legal instrument authorises for proactive disclosure",
        labels=laws,
        values=counts,
        accent_index=0,
        orientation="vertical",
        source="Overlay legal crosswalk: Zambia ATI Act 2023, NCC Act No.10/2020, ZPPA Act No.3/2020.",
        figsize=(6.0, 3.4),
    )
    save(fig, str(OUT / "04-legal-crosswalk.png"))
    print("OK 04-legal-crosswalk.png")


if __name__ == "__main__":
    chart_1_oc4ids_sheet_coverage()
    chart_2_phase_coverage()
    chart_3_decision_buckets()
    chart_4_legal_crosswalk()
