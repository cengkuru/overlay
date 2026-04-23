"""Build Doc 2: a short structural reference for a revised Zambia report.

Layout: Portrait A4. Length target: 4 to 6 pages.

v0.10 changes from the previous 22-page parallel rewrite:
- Relabelled as "Structural reference" with an explicit non-commitment disclaimer.
- Named owners replaced with placeholders (actual names require MSG consultation).
- Trimmed to: cover, executive summary excerpt, one phase row, one provenance
  row, gap typology table, one recommendation row, decision panel.
- Full recommendation list, full roadmap, risks table, review trail, conclusion
  are all removed. Those belong in the real report after MSG consultation.
- Denominators revised: no more "4.9% of 1,480 template slots" headline; coverage
  expressed against applicable-scope denominators.
- Cover strip uses stock-africa-* assets only.
- Table widths set explicitly to content width so no table collapses to ~70%.
"""
import pathlib
from docx import Document
from docx.shared import Cm, Mm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ─── CoST palette ───────────────────────────────────────────────────────────
RED = RGBColor(0xB7, 0x25, 0x1C)
COVER_RED = RGBColor(0xCC, 0x20, 0x28)
TABLE_RED = RGBColor(0xC0, 0x00, 0x00)
CHARCOAL = RGBColor(0x4A, 0x47, 0x43)
BLUE = RGBColor(0x71, 0xB6, 0xC9)
YELLOW = RGBColor(0xF1, 0xC0, 0x3D)
MUTED = RGBColor(0x9C, 0x9B, 0x99)
DMUTED = RGBColor(0x6B, 0x6A, 0x68)
LMUTED = RGBColor(0xB0, 0xB0, 0xB1)
MGRAY = RGBColor(0xE5, 0xE4, 0xE3)
LGRAY = RGBColor(0xF3, 0xF2, 0xF1)
LIGHT_NEUTRAL = RGBColor(0xF0, 0xED, 0xE7)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LOW_TEXT = RGBColor(0x4E, 0xA8, 0x3D)

ASSETS = pathlib.Path("/Users/cengkurumichael/.claude/skills/cost-document-design/assets")
CHARTS = pathlib.Path(__file__).parent.parent / "charts"
OUT = pathlib.Path(__file__).parent.parent / "02-structural-reference.docx"

# Portrait A4, 20mm margins: 210 - 40 = 170 mm content width = 17 cm
CONTENT_W_CM = 17.0


def hex_of(c):
    if isinstance(c, str):
        return c.upper().lstrip("#")
    return "".join(f"{b:02X}" for b in c)


def set_cell_shading(cell, color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_of(color))
    tc_pr.append(shd)


def set_cell_borders(cell, top=None, bottom=None, left=None, right=None, color="E5E4E3", sz="4"):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_borders = OxmlElement('w:tcBorders')
    for side, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        border = OxmlElement(f'w:{side}')
        border.set(qn('w:val'), val if val else 'nil')
        if val:
            border.set(qn('w:sz'), sz)
            border.set(qn('w:color'), color)
        tc_borders.append(border)
    tc_pr.append(tc_borders)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tc_pr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for k, v in (('top', top), ('bottom', bottom), ('left', left), ('right', right)):
        el = OxmlElement(f'w:{k}')
        el.set(qn('w:w'), str(v))
        el.set(qn('w:type'), 'dxa')
        tcMar.append(el)
    tc_pr.append(tcMar)


def set_table_full_width(table, content_cm=CONTENT_W_CM):
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False
    tbl_pr = table._tbl.tblPr
    for existing in tbl_pr.findall(qn('w:tblW')):
        tbl_pr.remove(existing)
    tblW = OxmlElement('w:tblW')
    tblW.set(qn('w:w'), str(int(content_cm * 567)))
    tblW.set(qn('w:type'), 'dxa')
    tbl_pr.append(tblW)


def apply_col_widths(table, widths_cm):
    tbl = table._tbl
    for grid in tbl.findall(qn('w:tblGrid')):
        tbl.remove(grid)
    grid = OxmlElement('w:tblGrid')
    for w in widths_cm:
        gc = OxmlElement('w:gridCol')
        gc.set(qn('w:w'), str(int(w * 567)))
        grid.append(gc)
    tbl.insert(list(tbl).index(tbl.find(qn('w:tblPr'))) + 1, grid)
    for row in table.rows:
        for cell, w in zip(row.cells, widths_cm):
            cell.width = Cm(w)


def add_run(p, text, *, bold=False, italic=False, size_pt=10.5, color=CHARCOAL, font="Arial"):
    run = p.add_run(text)
    run.font.name = font
    run.font.size = Pt(size_pt)
    run.font.color.rgb = color
    run.bold = bold
    run.italic = italic
    return run


def para(doc, text, *, size_pt=10.5, color=CHARCOAL, bold=False, italic=False,
         space_after=6, align=None, font="Arial"):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(0)
    if text:
        add_run(p, text, bold=bold, italic=italic, size_pt=size_pt, color=color, font=font)
    return p


def heading(doc, text, *, level=1):
    sizes = {1: 15, 2: 12, 3: 11}
    space_before = {1: 14, 2: 10, 3: 6}
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before[level])
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    add_run(p, text, bold=True, size_pt=sizes[level], color=CHARCOAL if level > 1 else RED)


# ─── Build document ─────────────────────────────────────────────────────────

doc = Document()
sec = doc.sections[0]
sec.page_width = Mm(210)
sec.page_height = Mm(297)
sec.top_margin = Mm(20)
sec.bottom_margin = Mm(20)
sec.left_margin = Mm(20)
sec.right_margin = Mm(20)

style = doc.styles['Normal']
style.font.name = 'Arial'
style.font.size = Pt(10.5)
style.font.color.rgb = CHARCOAL

# Header: logo
header = sec.header
hp = header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hp.paragraph_format.space_after = Pt(0)
hp.add_run().add_picture(str(ASSETS / "cost-logo-real.jpeg"), width=Cm(4.2))

# Footer: stripe + page number
footer = sec.footer
fp = footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
fp.paragraph_format.space_after = Pt(0)
fp.add_run().add_picture(str(ASSETS / "cost-stripe-real.png"), width=Cm(17))
fp2 = footer.add_paragraph()
fp2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
fp2.paragraph_format.space_before = Pt(4)
fr = fp2.add_run()
fr.font.name = 'Arial'; fr.font.size = Pt(8.5); fr.font.color.rgb = MUTED
fld = OxmlElement('w:fldSimple')
fld.set(qn('w:instr'), 'PAGE')
fr._element.append(fld)

# ─── Cover block ────────────────────────────────────────────────────────────
# Africa-contextual image strip (stock-africa-* assets only)
strip = doc.add_table(rows=1, cols=3)
set_table_full_width(strip)
apply_col_widths(strip, [CONTENT_W_CM / 3, CONTENT_W_CM / 3, CONTENT_W_CM / 3])

stocks = [
    ASSETS / "stock-africa-rural-road.jpeg",
    ASSETS / "stock-africa-highway-aerial.jpeg",
    ASSETS / "stock-africa-scaffolding.jpeg",
]
for i in range(3):
    set_cell_borders(strip.rows[0].cells[i])
    cp = strip.rows[0].cells[i].paragraphs[0]
    cp.paragraph_format.space_after = Pt(0)
    cp.add_run().add_picture(str(stocks[i]),
                             width=Cm(CONTENT_W_CM / 3), height=Mm(40))

# Red title block spans full content width
red = doc.add_table(rows=1, cols=1)
set_table_full_width(red)
apply_col_widths(red, [CONTENT_W_CM])
rcell = red.rows[0].cells[0]
set_cell_shading(rcell, COVER_RED)
set_cell_margins(rcell, top=420, bottom=420, left=420, right=420)
set_cell_borders(rcell)
rcp = rcell.paragraphs[0]
rcp.paragraph_format.space_after = Pt(4)
add_run(rcp, "STRUCTURAL REFERENCE", bold=True, size_pt=11, color=WHITE)
rcp2 = rcell.add_paragraph()
rcp2.paragraph_format.space_after = Pt(6)
add_run(rcp2, "What a revised OC4IDS field-level mapping report can look like",
        bold=True, size_pt=18, color=WHITE)
rcp3 = rcell.add_paragraph()
rcp3.paragraph_format.space_after = Pt(0)
add_run(rcp3, "A short illustrative extract.  Zambia context.  23 April 2026.",
        size_pt=10, color=WHITE)

para(doc, "", space_after=6)

# Non-commitment disclaimer
db = doc.add_table(rows=1, cols=1)
set_table_full_width(db)
apply_col_widths(db, [CONTENT_W_CM])
dc = db.cell(0, 0)
set_cell_shading(dc, LIGHT_NEUTRAL)
set_cell_borders(dc, left="single", color=hex_of(YELLOW), sz="32")
set_cell_margins(dc, top=200, bottom=200, left=240, right=240)
dcp = dc.paragraphs[0]
add_run(dcp, "HOW TO READ THIS DOCUMENT  ", bold=True, size_pt=10, color=DMUTED)
add_run(dcp, "This is a structural reference. It is not a commitment document, and it is not a rewrite of the Zambia team's report. Every figure, owner, timeline and legal instrument shown below is a ",
        size_pt=10, color=CHARCOAL)
add_run(dcp, "placeholder",
        bold=True, italic=True, size_pt=10, color=CHARCOAL)
add_run(dcp, ", included to show the kind of specificity a strong report carries. Any actual assignment of owners, timelines, or legal actions should follow consultation through the CoST Zambia MSG, NCC, ZPPA, and the relevant line ministry.",
        size_pt=10, color=CHARCOAL)

para(doc, "", space_after=10)

# ─── Executive summary excerpt ──────────────────────────────────────────────
heading(doc, "1.  Executive summary: the kind of opening this report needs", level=1)

vb = doc.add_table(rows=1, cols=1)
set_table_full_width(vb)
apply_col_widths(vb, [CONTENT_W_CM])
vc = vb.cell(0, 0)
set_cell_shading(vc, LGRAY)
set_cell_borders(vc, top="single", bottom="single", color=hex_of(RED), sz="24")
set_cell_margins(vc, top=200, bottom=200, left=240, right=240)
vp = vc.paragraphs[0]
add_run(vp, "VERDICT  ", bold=True, size_pt=10, color=RED)
add_run(vp, "Zambia's procurement system can publish roughly 35 OC4IDS fields today with no new work, and another 20 after small format fixes. Most of the information that is missing, including contract variations, progress reports, and payment records, is already collected by the National Council for Construction under its statutory monitoring mandate. It is a disclosure gap, not a data gap.",
        bold=True, size_pt=11, color=CHARCOAL)
vp2 = vc.add_paragraph()
vp2.paragraph_format.space_before = Pt(4)
add_run(vp2, "The Access to Information Act 2023 section 8 already requires proactive publication of most of the missing information. The proposed Information Platform for Public Infrastructure (IPPI-Zambia) is the integration layer this analysis calls for.",
        size_pt=10.5, color=CHARCOAL)

para(doc, "", space_after=10)

heading(doc, "The three numbers a revised report should lead with", level=2)

stats = doc.add_table(rows=1, cols=3)
set_table_full_width(stats)
apply_col_widths(stats, [CONTENT_W_CM / 3, CONTENT_W_CM / 3, CONTENT_W_CM / 3])

stat_data = [
    ("35",
     "OC4IDS fields the ZPPA e-GP system can publish today. [Placeholder figure from current mapping, to be confirmed through MSG review.]",
     LOW_TEXT),
    ("55",
     "OC4IDS fields publishable after small format fixes (35 today plus 20 light transformation).",
     BLUE),
    ("Yes",
     "Does Zambia's existing law (ATI Act 2023 s.8, NCC Act 2020 s.53) already permit publication of most currently missing fields? The answer determines whether this is a disclosure problem or a legal problem.",
     RED),
]
for i, (val, label, col) in enumerate(stat_data):
    cell = stats.rows[0].cells[i]
    set_cell_shading(cell, LGRAY)
    set_cell_margins(cell, top=200, bottom=200, left=200, right=200)
    set_cell_borders(cell, top="single", color=hex_of(col), sz="32")
    p1 = cell.paragraphs[0]
    add_run(p1, val, bold=True, size_pt=28, color=col)
    p2 = cell.add_paragraph()
    p2.paragraph_format.space_before = Pt(2)
    add_run(p2, label, size_pt=9, color=DMUTED)

para(doc, "", space_after=10)

para(doc, "A revised executive summary should pair each of these numbers with a one-sentence explanation and a plain-language reading: the first is the immediate win, the second is a near-term win with light integration work, the third reframes the rest of the report from 'we lack data' to 'we lack disclosure mechanics'.",
     size_pt=10.5, italic=True, color=DMUTED, space_after=12)

# ─── One phase row as an example ───────────────────────────────────────────
doc.add_page_break()
heading(doc, "2.  Findings by lifecycle phase: what one row should look like", level=1)

para(doc, "The current draft's section 4 describes each phase in prose. A single table row, quantified, with a named reason for the gap, carries far more for a reader. One row is shown here to illustrate the format; the revised report should carry one row for each of the seven lifecycle phases.",
     size_pt=10.5, space_after=8)

ph = doc.add_table(rows=2, cols=4)
set_table_full_width(ph)
apply_col_widths(ph, [3.0, 2.2, 4.0, 7.8])
for i, h in enumerate(["Phase", "Coverage", "Dominant reason for the gap", "Example"]):
    c = ph.rows[0].cells[i]
    set_cell_shading(c, TABLE_RED)
    add_run(c.paragraphs[0], h, bold=True, size_pt=10, color=WHITE)
row = ph.rows[1].cells
for c in row:
    set_cell_borders(c)
    set_cell_shading(c, WHITE)
add_run(row[0].paragraphs[0], "Implementation", bold=True, size_pt=10, color=CHARCOAL)
add_run(row[1].paragraphs[0], "2%", bold=True, size_pt=12, color=RED)
add_run(row[2].paragraphs[0], "Collected but not yet publicly disclosed. Data sits in NCC inspection records.",
        size_pt=10, color=CHARCOAL)
add_run(row[3].paragraphs[0], "Contract variations, progress updates, payment certificates, and quality-assurance reports are captured by NCC under NCC Act 2020 s.53 and shared with ZPPA only on request. Integration, not new collection, is the remediation.",
        size_pt=10, color=CHARCOAL)

para(doc, "", space_after=14)

# ─── One provenance row ─────────────────────────────────────────────────────
heading(doc, "3.  Source-field provenance: what one row should look like", level=1)

para(doc, "Every mapped OC4IDS field in the Zambia template is already traced to a specific ZPPA e-GP source path. The report should surface this in the annex. An example of the target format:",
     size_pt=10.5, space_after=8)

pv = doc.add_table(rows=2, cols=4)
set_table_full_width(pv)
apply_col_widths(pv, [4.0, 5.8, 2.5, 4.7])
for i, h in enumerate(["OC4IDS path", "ZPPA e-GP source path", "Status", "Disclosure pathway"]):
    c = pv.rows[0].cells[i]
    set_cell_shading(c, TABLE_RED)
    add_run(c.paragraphs[0], h, bold=True, size_pt=10, color=WHITE)
row = pv.rows[1].cells
for c in row:
    set_cell_borders(c)
    set_cell_shading(c, WHITE)
add_run(row[0].paragraphs[0], "/publicAuthority/name", size_pt=9.5, color=CHARCOAL, font="Courier New")
add_run(row[1].paragraphs[0], "zppa_egp.project.publicAuthority.name",
        size_pt=9.5, color=CHARCOAL, font="Courier New")
add_run(row[2].paragraphs[0], "Populated", bold=True, size_pt=10, color=LOW_TEXT)
add_run(row[3].paragraphs[0], "Ready to publish", size_pt=10, color=CHARCOAL)

para(doc, "", space_after=14)

# ─── Gap typology table (full, because it generalises) ─────────────────────
heading(doc, "4.  Gap typology: every gap should be named by its cause", level=1)

para(doc, "A review of the current draft classifies every material gap into one of the categories below. Different causes take different fixes. Naming them explicitly reframes 'recommendations' from a shopping list into a sequenced programme.",
     size_pt=10.5, space_after=8)

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
set_table_full_width(tt)
apply_col_widths(tt, [3.6, 4.6, 4.4, 4.4])
for i, h in enumerate(["Cause", "What it means", "Example in Zambia", "What fixes it"]):
    c = tt.rows[0].cells[i]
    set_cell_shading(c, TABLE_RED)
    add_run(c.paragraphs[0], h, bold=True, size_pt=10, color=WHITE)
for ri, row in enumerate(typology, start=1):
    cells = tt.rows[ri].cells
    bg = LGRAY if ri % 2 == 0 else WHITE
    accent = ri == 2  # "Collected but not yet disclosed" is the dominant Zambia cause
    for c in cells:
        set_cell_borders(c)
        set_cell_shading(c, bg)
    for ci, v in enumerate(row):
        add_run(cells[ci].paragraphs[0], v,
                bold=(ci == 0 and accent),
                size_pt=9.5,
                color=(RED if ci == 0 and accent else CHARCOAL))

para(doc, "", space_after=8)
para(doc, "The dominant cause in Zambia is the second one: data already collected by NCC that is not yet publicly disclosed. Naming that out loud changes the whole recommendations section.",
     size_pt=10.5, italic=True, color=DMUTED, space_after=14)

# ─── One recommendation row ────────────────────────────────────────────────
doc.add_page_break()
heading(doc, "5.  Recommendations: what one row should look like", level=1)

para(doc, "The current draft's section 6 lists six recommendations. All are directional. Below is an example of the format a strong recommendation takes. Owners and timelines shown here are placeholders pending MSG consultation.",
     size_pt=10.5, space_after=8)

rec_t = doc.add_table(rows=2, cols=7)
set_table_full_width(rec_t)
apply_col_widths(rec_t, [0.9, 2.6, 3.8, 2.8, 2.8, 1.6, 2.5])
for i, h in enumerate(["Ref", "Type", "Action", "Proposed owner", "Legal basis", "Quarter", "Effort"]):
    c = rec_t.rows[0].cells[i]
    set_cell_shading(c, TABLE_RED)
    add_run(c.paragraphs[0], h, bold=True, size_pt=9.5, color=WHITE)
row = rec_t.rows[1].cells
for c in row:
    set_cell_borders(c)
    set_cell_shading(c, WHITE)
add_run(row[0].paragraphs[0], "R1", bold=True, size_pt=10, color=CHARCOAL)
add_run(row[1].paragraphs[0], "Immediate no-regret fix", bold=True, size_pt=9, color=LOW_TEXT)
p_act = row[2].paragraphs[0]
add_run(p_act, "Publish the 35 'ready to publish' fields through an OC4IDS-compliant feed on the ZPPA e-GP portal.",
        bold=True, size_pt=9.5, color=CHARCOAL)
p_act2 = row[2].add_paragraph()
p_act2.paragraph_format.space_before = Pt(2)
add_run(p_act2, "Uses existing source paths. No new data collection. CC BY 4.0 licence.",
        size_pt=9, color=DMUTED, italic=True)
add_run(row[3].paragraphs[0],
        "[Proposed: ZPPA Director of IT. To be confirmed through MSG.]",
        size_pt=9, color=CHARCOAL, italic=True)
add_run(row[4].paragraphs[0], "ATI Act 2023 s.8; ZPPA Act 2020 s.67",
        size_pt=9, color=CHARCOAL)
add_run(row[5].paragraphs[0], "[Placeholder]", bold=True, size_pt=9.5, color=RED, italic=True)
add_run(row[6].paragraphs[0], "Low", size_pt=9, color=CHARCOAL)

para(doc, "", space_after=10)

para(doc, "A revised recommendations section would carry eight to ten rows in this format, grouped into four types: immediate no-regret fixes, system or configuration changes, institutional or process changes, and policy or legal changes.",
     size_pt=10.5, italic=True, color=DMUTED, space_after=14)

# ─── Decision panel (the steering view) ────────────────────────────────────
heading(doc, "6.  Decision summary: what the Permanent Secretary reads first", level=1)

para(doc, "This is the single table the revised report needs most. It classifies every publishable element into one of four pathways, matched to who can act and under which law. Numbers below are placeholders drawn from the current mapping template; the revised report should produce a version reviewed by the Zambia team before publication.",
     size_pt=10.5, space_after=8)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(str(CHARTS / "03-decision-buckets.png"), width=Cm(CONTENT_W_CM - 1))
para(doc, "", space_after=6)

buckets = [
    ("Ready to publish",
     "Fields the ZPPA e-GP system already holds with clean source paths and clear legal authority.",
     "≈ 35 fields. Project IDs, titles, sectors, procurement method, tender values.",
     LOW_TEXT),
    ("Small format fixes",
     "Fields present but needing date-format conversion, codelist alignment, or free-text standardisation.",
     "≈ 20 fields. Descriptions, sector codes, date harmonisation.",
     BLUE),
    ("Needs system work",
     "Fields NCC already collects under NCC Act 2020 s.53 but that need an integration layer to reach the public.",
     "≈ 73 fields. Contract variations, progress, quality and safety, payments, final costs.",
     YELLOW),
    ("Needs policy action",
     "Fields blocked by absence of a regulation, statutory instrument, or internal approval workflow.",
     "≈ 25 fields. Beneficial ownership; maintenance and decommissioning capture.",
     RED),
]

bt = doc.add_table(rows=len(buckets), cols=3)
set_table_full_width(bt)
apply_col_widths(bt, [4.5, 6.5, 6.0])
for ri, (label, what, example, col) in enumerate(buckets):
    cells = bt.rows[ri].cells
    set_cell_borders(cells[0], left="single", color=hex_of(col), sz="32")
    for c in cells:
        set_cell_shading(c, LGRAY)
        set_cell_margins(c, top=140, bottom=140, left=180, right=180)
    add_run(cells[0].paragraphs[0], label, bold=True, size_pt=11, color=col)
    add_run(cells[1].paragraphs[0], what, size_pt=10, color=CHARCOAL)
    add_run(cells[2].paragraphs[0], example, size_pt=10, color=CHARCOAL)

para(doc, "", space_after=12)

# ─── Closing note ───────────────────────────────────────────────────────────
heading(doc, "7.  Using this reference", level=1)

para(doc, "This document is structural guidance. It shows the shape and specificity a strong report carries; it does not prescribe Zambia's final content. The revised report should preserve what the Zambia team already did well (the legal framework analysis in Annex 8.1, the NCC insight, the 97.9% source forward-mapping) and apply the formats above to the sections CoST IS has flagged for revision.",
     size_pt=10.5, space_after=10)

# Legal footer
para(doc, "CoST, the Infrastructure Transparency Initiative  •  www.infrastructuretransparency.org  •  Published under CC BY 4.0",
     size_pt=8, italic=True, color=LMUTED, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=0)

doc.save(str(OUT))
print(f"OK {OUT}")
