"""Build Doc 2: structural reference for a revised Zambia report.

Portrait A4, illustrative excerpt only. Target length 4-6 pages.

v0.11 changes:
- Uses _docx_helpers for shared table/padding/image logic.
- Generous table inner padding (labels no longer hug cell edges).
- Cover strip images sized consistently.
- Row heights set so tables don't collapse in Word.
"""
import pathlib
from docx import Document
from docx.shared import Cm, Mm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import _docx_helpers as H

CHARTS = pathlib.Path(__file__).parent.parent / "charts"
OUT = pathlib.Path(__file__).parent.parent / "02-structural-reference.docx"

# Portrait A4, 22mm margins => 16.6cm content width
CONTENT_W = 16.6

# ─── Document setup ─────────────────────────────────────────────────────────
doc = Document()
H.setup_portrait(doc.sections[0], margin_mm=22)
H.setup_base_style(doc)
H.add_logo_header(doc.sections[0])
H.add_stripe_footer(doc.sections[0])

# ─── Cover block ────────────────────────────────────────────────────────────
# Africa-contextual image strip
strip = doc.add_table(rows=1, cols=3)
H.set_table_full_width(strip, CONTENT_W)
col_w = CONTENT_W / 3
H.apply_col_widths(strip, [col_w, col_w, col_w])

stocks = [
    H.ASSETS / "stock-africa-rural-road.jpeg",
    H.ASSETS / "stock-africa-highway-aerial.jpeg",
    H.ASSETS / "stock-africa-scaffolding.jpeg",
]
for i in range(3):
    cell = strip.rows[0].cells[i]
    H.set_cell_borders(cell)
    H.set_cell_margins(cell, top=0, bottom=0, left=0, right=0)
    cp = cell.paragraphs[0]
    cp.paragraph_format.space_after = Pt(0)
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.add_run().add_picture(str(stocks[i]), width=Cm(col_w - 0.05), height=Mm(42))

# Red title block
red = doc.add_table(rows=1, cols=1)
H.set_table_full_width(red, CONTENT_W)
H.apply_col_widths(red, [CONTENT_W])
rcell = red.rows[0].cells[0]
H.set_cell_shading(rcell, H.COVER_RED)
H.set_cell_margins(rcell, top=480, bottom=480, left=460, right=460)
H.set_cell_borders(rcell)
rcp = rcell.paragraphs[0]
rcp.paragraph_format.space_after = Pt(4)
H.add_run(rcp, "STRUCTURAL REFERENCE", bold=True, size_pt=11, color=H.WHITE)
rcp2 = rcell.add_paragraph()
rcp2.paragraph_format.space_after = Pt(8)
H.add_run(rcp2, "What a revised OC4IDS field-level mapping report can look like",
          bold=True, size_pt=18, color=H.WHITE)
rcp3 = rcell.add_paragraph()
rcp3.paragraph_format.space_after = Pt(0)
H.add_run(rcp3, "A short illustrative extract.  Zambia context.  23 April 2026.",
          size_pt=10, color=H.WHITE)

H.para(doc, "", space_after=10)

# Non-commitment disclaimer
H.callout_box(
    doc, CONTENT_W,
    label="HOW TO READ THIS DOCUMENT",
    label_color=H.DMUTED,
    body="This is a structural reference. It is not a commitment document, and it is not a rewrite of the Zambia team's report. Every figure, owner, timeline and legal instrument shown below is a placeholder, included to show the kind of specificity a strong report carries. Any actual assignment of owners, timelines, or legal actions should follow consultation through the CoST Zambia MSG, NCC, ZPPA, and the relevant line ministry.",
)
H.para(doc, "", space_after=12)

# ─── Section 1: Executive summary excerpt ──────────────────────────────────
H.heading(doc, "1.  Executive summary: the kind of opening this report needs", level=1)

H.verdict_box(
    doc, CONTENT_W,
    label="VERDICT",
    headline="Zambia's procurement system can publish roughly 35 OC4IDS fields today with no new work, and another 20 after small format fixes. Most of the information that is missing (including contract variations, progress reports, and payment records) is already collected by the National Council for Construction under its statutory monitoring mandate. It is a disclosure gap, not a data gap.",
    tail="The Access to Information Act 2023 section 8 already requires proactive publication of most of the missing information. The proposed Information Platform for Public Infrastructure (IPPI-Zambia) is the integration layer this analysis calls for.",
)
H.para(doc, "", space_after=14)

H.heading(doc, "The three numbers a revised report should lead with", level=2)

stats = doc.add_table(rows=1, cols=3)
H.set_table_full_width(stats, CONTENT_W)
col = CONTENT_W / 3
H.apply_col_widths(stats, [col, col, col])
H.set_row_height(stats.rows[0], 4.8)

stat_data = [
    ("35",
     "OC4IDS fields the ZPPA e-GP system can publish today. Placeholder figure from current mapping, to be confirmed through MSG review.",
     H.LOW_TEXT),
    ("55",
     "OC4IDS fields publishable after small format fixes (35 today plus 20 light transformation).",
     H.BLUE),
    ("Yes",
     "Does Zambia's existing law (ATI Act 2023 s.8, NCC Act 2020 s.53) already permit publication of most currently missing fields? The answer determines whether this is a disclosure problem or a legal problem.",
     H.RED),
]
for i, (val, label, col_color) in enumerate(stat_data):
    cell = stats.rows[0].cells[i]
    H.set_cell_shading(cell, H.LGRAY)
    H.set_cell_margins(cell, top=260, bottom=260, left=280, right=280)
    H.set_cell_borders(cell, top="single", color=H.hex_of(col_color), sz="40")
    p1 = cell.paragraphs[0]
    H.add_run(p1, val, bold=True, size_pt=28, color=col_color)
    p2 = cell.add_paragraph()
    p2.paragraph_format.space_before = Pt(4)
    H.add_run(p2, label, size_pt=9, color=H.DMUTED)

H.para(doc, "", space_after=12)

H.para(doc, "A revised executive summary should pair each of these numbers with a one-sentence explanation and a plain-language reading: the first is the immediate win, the second is a near-term win with light integration work, the third reframes the rest of the report from 'we lack data' to 'we lack disclosure mechanics'.",
       size_pt=10.5, italic=True, color=H.DMUTED, space_after=14)

# ─── Section 2: One phase row ──────────────────────────────────────────────
doc.add_page_break()
H.heading(doc, "2.  Findings by lifecycle phase: what one row should look like", level=1)

H.para(doc, "The current draft's section 4 describes each phase in prose. A single table row, quantified, with a named reason for the gap, carries far more for a reader. One row is shown here to illustrate the format; the revised report should carry one row for each of the seven lifecycle phases.",
       size_pt=10.5, space_after=10)

ph = doc.add_table(rows=2, cols=4)
H.set_table_full_width(ph, CONTENT_W)
H.apply_col_widths(ph, [2.8, 2.0, 4.2, CONTENT_W - 9.0])
H.apply_default_padding(ph)
H.styled_table_header(ph.rows[0],
                      ["Phase", "Coverage", "Dominant reason for the gap", "Example"])

H.set_row_height(ph.rows[1], 2.6)
row = ph.rows[1].cells
for c in row:
    H.set_cell_borders(c)
    H.set_cell_shading(c, H.WHITE)
H.add_run(row[0].paragraphs[0], "Implementation", bold=True, size_pt=10, color=H.CHARCOAL)
H.add_run(row[1].paragraphs[0], "2%", bold=True, size_pt=12, color=H.RED)
H.add_run(row[2].paragraphs[0],
          "Collected but not yet publicly disclosed. Data sits in NCC inspection records.",
          size_pt=10, color=H.CHARCOAL)
H.add_run(row[3].paragraphs[0],
          "Contract variations, progress updates, payment certificates, and quality-assurance reports are captured by NCC under NCC Act 2020 s.53 and shared with ZPPA only on request. Integration, not new collection, is the remediation.",
          size_pt=10, color=H.CHARCOAL)

H.para(doc, "", space_after=16)

# ─── Section 3: One provenance row ────────────────────────────────────────
H.heading(doc, "3.  Source-field provenance: what one row should look like", level=1)

H.para(doc, "Every mapped OC4IDS field in the Zambia template is already traced to a specific ZPPA e-GP source path. The report should surface this in the annex. An example of the target format:",
       size_pt=10.5, space_after=10)

pv = doc.add_table(rows=2, cols=4)
H.set_table_full_width(pv, CONTENT_W)
H.apply_col_widths(pv, [3.8, 5.4, 2.6, CONTENT_W - 11.8])
H.apply_default_padding(pv)
H.styled_table_header(pv.rows[0],
                      ["OC4IDS path", "ZPPA e-GP source path",
                       "Status", "Disclosure pathway"])

H.set_row_height(pv.rows[1], 1.6)
row = pv.rows[1].cells
for c in row:
    H.set_cell_borders(c)
    H.set_cell_shading(c, H.WHITE)
H.add_run(row[0].paragraphs[0], "/publicAuthority/name",
          size_pt=9.5, color=H.CHARCOAL, font="Courier New")
H.add_run(row[1].paragraphs[0], "zppa_egp.project.publicAuthority.name",
          size_pt=9.5, color=H.CHARCOAL, font="Courier New")
H.add_run(row[2].paragraphs[0], "Populated", bold=True, size_pt=10, color=H.LOW_TEXT)
H.add_run(row[3].paragraphs[0], "Ready to publish", size_pt=10, color=H.CHARCOAL)

H.para(doc, "", space_after=16)

# ─── Section 4: Gap typology ───────────────────────────────────────────────
H.heading(doc, "4.  Gap typology: every gap should be named by its cause", level=1)

H.para(doc, "A review of the current draft classifies every material gap into one of the categories below. Different causes take different fixes. Naming them explicitly reframes 'recommendations' from a shopping list into a sequenced programme.",
       size_pt=10.5, space_after=10)

typology = [
    ("Not collected", "Data does not exist in any reviewed system.",
     "Maintenance schedules; decommissioning plans.",
     "New capture workflow plus budget line."),
    ("Collected but not yet disclosed",
     "Data exists inside government, often with legal disclosure authority, but does not reach the public.",
     "Contract variations and payment certificates held by NCC.",
     "Integration between systems. A short statutory instrument may be sufficient."),
    ("Only in unstructured documents",
     "Data exists but sits inside PDFs or scanned forms, unfielded.",
     "Project briefs and ESIA narratives.",
     "Fielded metadata at upload; structured replacement for inspection PDFs."),
    ("Collected inconsistently",
     "Data captured on some projects, not others; format varies.",
     "Some tender-evaluation free-text fields.",
     "Standardisation before publication."),
    ("Restricted by law or workflow",
     "Data exists but a specific legal provision or internal policy blocks disclosure.",
     "Beneficial ownership of contracting firms.",
     "Regulation or policy change, not a technical fix."),
]

tt = doc.add_table(rows=len(typology) + 1, cols=4)
H.set_table_full_width(tt, CONTENT_W)
col_w = (CONTENT_W - 3.4) / 3
H.apply_col_widths(tt, [3.4, col_w, col_w, col_w])
H.apply_default_padding(tt)
H.styled_table_header(tt.rows[0],
                      ["Cause", "What it means",
                       "Example in Zambia", "What fixes it"])

for ri, row in enumerate(typology, start=1):
    cells = tt.rows[ri].cells
    H.set_row_height(tt.rows[ri], 1.5)
    bg = H.LGRAY if ri % 2 == 0 else H.WHITE
    accent = ri == 2  # "Collected but not yet disclosed" is the Zambia story
    for c in cells:
        H.set_cell_borders(c)
        H.set_cell_shading(c, bg)
    for ci, v in enumerate(row):
        H.add_run(cells[ci].paragraphs[0], v,
                  bold=(ci == 0 and accent),
                  size_pt=9.5,
                  color=(H.RED if ci == 0 and accent else H.CHARCOAL))

H.para(doc, "", space_after=10)
H.para(doc, "The dominant cause in Zambia is the second one: data already collected by NCC that is not yet publicly disclosed. Naming that out loud changes the whole recommendations section.",
       size_pt=10.5, italic=True, color=H.DMUTED, space_after=16)

# ─── Section 5: One recommendation row ─────────────────────────────────────
doc.add_page_break()
H.heading(doc, "5.  Recommendations: what one row should look like", level=1)

H.para(doc, "The current draft's section 6 lists six recommendations. All are directional. Below is an example of the format a strong recommendation takes. Owners and timelines shown here are placeholders pending MSG consultation.",
       size_pt=10.5, space_after=10)

rec_t = doc.add_table(rows=2, cols=7)
H.set_table_full_width(rec_t, CONTENT_W)
H.apply_col_widths(rec_t, [0.9, 2.4, 3.6, 2.9, 2.6, 1.5, 2.7])
H.apply_default_padding(rec_t)
H.styled_table_header(rec_t.rows[0],
                      ["Ref", "Type", "Action", "Proposed owner",
                       "Legal basis", "Quarter", "Effort"],
                      size_pt=9.5)

H.set_row_height(rec_t.rows[1], 2.6)
row = rec_t.rows[1].cells
for c in row:
    H.set_cell_borders(c)
    H.set_cell_shading(c, H.WHITE)
H.add_run(row[0].paragraphs[0], "R1", bold=True, size_pt=10, color=H.CHARCOAL)
H.add_run(row[1].paragraphs[0], "Immediate no-regret fix",
          bold=True, size_pt=9, color=H.LOW_TEXT)
p_act = row[2].paragraphs[0]
H.add_run(p_act, "Publish the 35 'ready to publish' fields through an OC4IDS-compliant feed on the ZPPA e-GP portal.",
          bold=True, size_pt=9.5, color=H.CHARCOAL)
p_act2 = row[2].add_paragraph()
p_act2.paragraph_format.space_before = Pt(2)
H.add_run(p_act2, "Uses existing source paths. No new data collection. CC BY 4.0 licence.",
          size_pt=9, color=H.DMUTED, italic=True)
H.add_run(row[3].paragraphs[0],
          "[Proposed: ZPPA Director of IT. Confirm through MSG.]",
          size_pt=9, color=H.CHARCOAL, italic=True)
H.add_run(row[4].paragraphs[0], "ATI Act 2023 s.8; ZPPA Act 2020 s.67",
          size_pt=9, color=H.CHARCOAL)
H.add_run(row[5].paragraphs[0], "[Placeholder]",
          bold=True, size_pt=9.5, color=H.RED, italic=True)
H.add_run(row[6].paragraphs[0], "Low", size_pt=9, color=H.CHARCOAL)

H.para(doc, "", space_after=12)

H.para(doc, "A revised recommendations section would carry eight to ten rows in this format, grouped into four types: immediate no-regret fixes, system or configuration changes, institutional or process changes, and policy or legal changes.",
       size_pt=10.5, italic=True, color=H.DMUTED, space_after=16)

# ─── Section 6: Decision panel ─────────────────────────────────────────────
H.heading(doc, "6.  Decision summary: what the Permanent Secretary reads first", level=1)

H.para(doc, "This is the single table the revised report needs most. It classifies every publishable element into one of four pathways, matched to who can act and under which law. Numbers below are placeholders drawn from the current mapping template; the revised report should produce a version reviewed by the Zambia team before publication.",
       size_pt=10.5, space_after=10)

H.centered_image(doc, CHARTS / "03-decision-buckets.png", width_cm=CONTENT_W - 1.5,
                 space_before=6, space_after=12)

buckets = [
    ("Ready to publish",
     "Fields the ZPPA e-GP system already holds with clean source paths and clear legal authority.",
     "≈ 35 fields. Project IDs, titles, sectors, procurement method, tender values.",
     H.LOW_TEXT),
    ("Small format fixes",
     "Fields present but needing date-format conversion, codelist alignment, or free-text standardisation.",
     "≈ 20 fields. Descriptions, sector codes, date harmonisation.",
     H.BLUE),
    ("Needs system work",
     "Fields NCC already collects under NCC Act 2020 s.53 but that need an integration layer to reach the public.",
     "≈ 73 fields. Contract variations, progress, quality and safety, payments, final costs.",
     H.YELLOW),
    ("Needs policy action",
     "Fields blocked by absence of a regulation, statutory instrument, or internal approval workflow.",
     "≈ 25 fields. Beneficial ownership; maintenance and decommissioning capture.",
     H.RED),
]

bt = doc.add_table(rows=len(buckets), cols=3)
H.set_table_full_width(bt, CONTENT_W)
H.apply_col_widths(bt, [4.2, 6.2, CONTENT_W - 10.4])
for ri, (label, what, example, col) in enumerate(buckets):
    cells = bt.rows[ri].cells
    H.set_row_height(bt.rows[ri], 1.8)
    H.set_cell_borders(cells[0], left="single", color=H.hex_of(col), sz="40")
    for c in cells:
        H.set_cell_shading(c, H.LGRAY)
        H.set_cell_margins(c, top=220, bottom=220, left=260, right=260)
    H.add_run(cells[0].paragraphs[0], label, bold=True, size_pt=11, color=col)
    H.add_run(cells[1].paragraphs[0], what, size_pt=10, color=H.CHARCOAL)
    H.add_run(cells[2].paragraphs[0], example, size_pt=10, color=H.CHARCOAL)

H.para(doc, "", space_after=14)

# ─── Section 7: How to use ─────────────────────────────────────────────────
H.heading(doc, "7.  Using this reference", level=1)

H.para(doc, "This document is structural guidance. It shows the shape and specificity a strong report carries; it does not prescribe Zambia's final content. The revised report should preserve what the Zambia team already did well (the legal framework analysis in Annex 8.1, the NCC insight, the 97.9% source forward-mapping) and apply the formats above to the sections CoST IS has flagged for revision.",
       size_pt=10.5, space_after=10)

H.para(doc, "A companion document (03-sample-final-report.docx) carries the same structure filled out in full, as a worked model the Zambia team can adapt directly.",
       size_pt=10.5, italic=True, color=H.DMUTED, space_after=14)

H.para(doc, "CoST, the Infrastructure Transparency Initiative  •  www.infrastructuretransparency.org  •  Published under CC BY 4.0",
       size_pt=8, italic=True, color=H.LMUTED,
       align=WD_ALIGN_PARAGRAPH.CENTER, space_after=0)

doc.save(str(OUT))
print(f"OK {OUT}")
