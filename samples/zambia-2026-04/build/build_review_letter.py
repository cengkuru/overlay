"""Build Doc 1: CoST IS review of the Zambia OC4IDS field-level mapping report.

Layout: Landscape A4, Professional Report intensity.
Voice: CoST IS to Zambia Technical Team. No internal tool vocabulary.

v0.10 changes:
- All Overlay / gate-score / rubric-code / Part A/B/C references removed.
- Resubmission date removed (routed to covering email).
- 'Findings' renamed to 'Priority revisions'; F1-F10 renamed to R1-R10.
- 'Gate scorecard' section deleted entirely.
- 'What is working' (former 'Strengths') moved up to sit right after the verdict.
- Comparative praise without reference data removed.
- Body dates use '23 April 2026' form; metadata retains ISO.
- Table widths set explicitly to landscape content width so tables span the page.
- Source-path samples rendered in Courier New (no backticks).
"""
import pathlib
from docx import Document
from docx.shared import Cm, Mm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ─── CoST palette ───────────────────────────────────────────────────────────
RED = RGBColor(0xB7, 0x25, 0x1C)
COVER_RED = RGBColor(0xCC, 0x20, 0x28)
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

CRITICAL_BG = RGBColor(0xF5, 0xD5, 0xD3)
HIGH_BG = RGBColor(0xD9, 0xED, 0xF3)
MEDIUM_BG = RGBColor(0xFD, 0xF3, 0xD7)
LOW_BG = RGBColor(0xE8, 0xF5, 0xE9)
MEDIUM_TEXT = RGBColor(0xD4, 0xA0, 0x17)
LOW_TEXT = RGBColor(0x4E, 0xA8, 0x3D)

ASSETS = pathlib.Path("/Users/cengkurumichael/.claude/skills/cost-document-design/assets")
CHARTS = pathlib.Path(__file__).parent.parent / "charts"
OUT = pathlib.Path(__file__).parent.parent / "01-review-letter.docx"

# Landscape A4: 297mm x 210mm, margins 18mm => content width ~26.1 cm = 26100 emu-ish
# In Cm the usable width is 297 - 36 = 261 mm = 26.1 cm
CONTENT_W_CM = 26.1


def hex_of(c):
    if isinstance(c, str):
        return c.upper().lstrip("#")
    return "".join(f"{b:02X}" for b in c)


def set_cell_shading(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_of(hex_color))
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


def set_table_full_width(table, content_cm=CONTENT_W_CM):
    """Force a table to span the section's content width."""
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False
    tbl_pr = table._tbl.tblPr
    # Remove any existing tblW
    for existing in tbl_pr.findall(qn('w:tblW')):
        tbl_pr.remove(existing)
    tblW = OxmlElement('w:tblW')
    tblW.set(qn('w:w'), str(int(content_cm * 567)))  # 567 dxa per cm
    tblW.set(qn('w:type'), 'dxa')
    tbl_pr.append(tblW)


def apply_col_widths(table, widths_cm):
    """Set column widths via both XML grid and cell-level width, so Word honours them."""
    tbl = table._tbl
    # Remove existing grid
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


def accent_bar(doc, color=RED, width_cm=6):
    """A thin coloured rule under a heading."""
    t = doc.add_table(rows=1, cols=1)
    t.autofit = False
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl_pr = t._tbl.tblPr
    for existing in tbl_pr.findall(qn('w:tblW')):
        tbl_pr.remove(existing)
    tblW = OxmlElement('w:tblW')
    tblW.set(qn('w:w'), str(int(width_cm * 567)))
    tblW.set(qn('w:type'), 'dxa')
    tbl_pr.append(tblW)
    cell = t.cell(0, 0)
    cell.text = ""
    cell.paragraphs[0].paragraph_format.space_after = Pt(0)
    set_cell_borders(cell, bottom="single", color=hex_of(color), sz="24")
    return t


# ─── Document setup ─────────────────────────────────────────────────────────

doc = Document()
section = doc.sections[0]
section.orientation = WD_ORIENT.LANDSCAPE
section.page_width = Mm(297)
section.page_height = Mm(210)
section.top_margin = Mm(18)
section.bottom_margin = Mm(18)
section.left_margin = Mm(18)
section.right_margin = Mm(18)

style = doc.styles['Normal']
style.font.name = 'Arial'
style.font.size = Pt(10.5)
style.font.color.rgb = CHARCOAL

# Header: logo top-right
header = section.header
hp = header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hp.paragraph_format.space_after = Pt(0)
hp.add_run().add_picture(str(ASSETS / "cost-logo-real.jpeg"), width=Cm(4.2))

# Footer: stripe + page number
footer = section.footer
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

# ─── Title block ────────────────────────────────────────────────────────────
para(doc, "CoST IS REVIEW", size_pt=11, bold=True, color=RED, space_after=2)
para(doc, "OC4IDS Field-Level Mapping Report", size_pt=22, bold=True, color=CHARCOAL, space_after=4)
para(doc, "Zambia: ZPPA, NCC, CoST Zambia   •   Draft of 3 March 2026",
     size_pt=13, color=DMUTED, space_after=10)
accent_bar(doc, RED, width_cm=20)
para(doc, "", space_after=6)

# Metadata block (no internal vocabulary)
meta_t = doc.add_table(rows=3, cols=2)
set_table_full_width(meta_t)
apply_col_widths(meta_t, [5.5, 20.5])
meta_rows = [
    ("Reviewed by:",
     "CoST International Secretariat. This review applies CoST IS's OC4IDS mapping review methodology."),
    ("Review date:", "23 April 2026."),
    ("Companion document:",
     "02-structural-reference.docx, a short illustrative extract showing one way a revised report could be structured."),
]
for i, (k, v) in enumerate(meta_rows):
    kc, vc = meta_t.rows[i].cells
    add_run(kc.paragraphs[0], k, bold=True, size_pt=10, color=DMUTED)
    add_run(vc.paragraphs[0], v, size_pt=10.5, color=CHARCOAL)
    for c in (kc, vc):
        set_cell_borders(c)
para(doc, "", space_after=12)

# ─── Verdict ────────────────────────────────────────────────────────────────
vb = doc.add_table(rows=1, cols=1)
set_table_full_width(vb)
apply_col_widths(vb, [CONTENT_W_CM])
vc = vb.cell(0, 0)
set_cell_shading(vc, LGRAY)
set_cell_borders(vc, top="single", bottom="single", color=hex_of(RED), sz="24")
vcp = vc.paragraphs[0]
add_run(vcp, "VERDICT   ", bold=True, size_pt=10, color=RED)
add_run(vcp, "The Zambia mapping template is substantively strong: 73 OC4IDS fields mapped, every mapped field backed by a real source path, and 47 of 48 source elements traced forward into OC4IDS. ",
        size_pt=10.5, color=CHARCOAL)
add_run(vcp, "The narrative report does not yet reflect the strength of the underlying work. ",
        bold=True, size_pt=10.5, color=CHARCOAL)
add_run(vcp, "The executive summary leads with adjectives rather than numbers, the lifecycle findings are described but not quantified, and most recommendations have no named owner. The legal framework analysis in Annex 8.1 is publication-quality and should anchor the report's front page, not sit at the back.",
        size_pt=10.5, color=CHARCOAL)
para(doc, "", space_after=14)

# ─── What is working (moved up: strengths first) ────────────────────────────
p = doc.add_paragraph()
add_run(p, "1.  What is working", bold=True, size_pt=13, color=CHARCOAL)
accent_bar(doc, LOW_TEXT, width_cm=8)
para(doc, "", space_after=4)

para(doc, "These elements of the current draft are already at the level a reader needs. Keep them on revision.",
     size_pt=10.5, space_after=8)

strengths = [
    ("Legal framework analysis in Annex 8.1.",
     "The citations to the Access to Information Act 2023 (s.6, s.8, s.9, s.17), the ZPPA Act 2020 (s.67, s.70), and the NCC Act 2020 (s.5, s.31, s.33, s.53) are precise and directly tied to disclosure obligations. This is the report's strongest asset. Move the substance forward into the executive summary; keep the full text in the annex."),
    ("The NCC insight.",
     "The observation in section 4.1 that most implementation-stage data is already collected by NCC under its statutory monitoring mandate is the single most actionable finding in the report. It reframes the question from 'how do we collect this data?' to 'how do we integrate and disclose what is already collected?' Make this the headline of the recommendations section."),
    ("Source element forward-mapping.",
     "The template maps 47 of the 48 source data elements from the ZPPA e-GP system into OC4IDS paths. That coverage is excellent. Report the number in the methodology section."),
    ("Lifecycle framework in section 8.2.",
     "The five-row data-source-by-stage table is a foundation for the decision summary this review asks for (section 2, revision R4 below). Expand it into the four-bucket classification: ready to publish, small format fixes, needs system work, needs policy action."),
    ("Mapping quality.",
     "Every OC4IDS path the template lists as mapped contains real source content. No placeholders. A reviewer sampling the mapping sheets can verify every line back to the ZPPA e-GP schema."),
]
for title, body in strengths:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    add_run(p, "+  ", bold=True, size_pt=10.5, color=LOW_TEXT)
    add_run(p, title + "  ", bold=True, size_pt=10.5, color=CHARCOAL)
    add_run(p, body, size_pt=10.5, color=CHARCOAL)

para(doc, "", space_after=14)

# ─── Headline numbers chart ─────────────────────────────────────────────────
p = doc.add_paragraph()
add_run(p, "2.  The mapping evidence", bold=True, size_pt=13, color=CHARCOAL)
accent_bar(doc, RED, width_cm=8)
para(doc, "", space_after=4)

para(doc, "The report's strongest asset is the template itself. It maps 73 OC4IDS fields across four sheets, all backed by real source paths from the ZPPA e-GP system. The headline does not yet say this. Section 4 below sets out specific changes to bring the narrative in line with the evidence.",
     size_pt=10.5, space_after=8)

para(doc, "Two of the four OC4IDS template sheets carry almost no Zambia data. That is the first story the executive summary should lead with.",
     size_pt=10.5, space_after=6)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(str(CHARTS / "01-sheet-coverage.png"), width=Cm(22))
para(doc, "", space_after=14)

# Page break for section 3
doc.add_page_break()

# ─── Phase coverage ─────────────────────────────────────────────────────────
p = doc.add_paragraph()
add_run(p, "3.  Where the gaps sit across the project lifecycle", bold=True, size_pt=13, color=CHARCOAL)
accent_bar(doc, RED, width_cm=8)
para(doc, "", space_after=4)

para(doc, "Disclosure is strong at identification and procurement. It thins out sharply across implementation and collapses entirely at maintenance and decommissioning. The report describes this in words; the revision should add the percentages.",
     size_pt=10.5, space_after=8)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(str(CHARTS / "02-phase-coverage.png"), width=Cm(22))
para(doc, "", space_after=6)

para(doc, "The report already points to the single most useful reading of this pattern: most of the missing implementation-stage data is already collected by the National Council for Construction under its statutory monitoring mandate (NCC Act 2020, s.53). In other words, this is a disclosure gap, not a data gap. Remediation is integration, not new collection. That framing should carry the report.",
     size_pt=10.5, space_after=14)

# ─── Priority revisions table ───────────────────────────────────────────────
p = doc.add_paragraph()
add_run(p, "4.  Priority revisions requested", bold=True, size_pt=13, color=CHARCOAL)
accent_bar(doc, RED, width_cm=8)
para(doc, "", space_after=4)

para(doc, "Ten changes, ranked by priority. Each carries an issue, the evidence behind it, the specific revision requested, and a proposed owner. Dates are not set here; a resubmission schedule will be agreed through the MSG in the covering note.",
     size_pt=10.5, space_after=10)

revs = [
    ("R1", "Critical", "The executive summary carries no number.",
     'The opening currently reads "significant data gaps exist". The template itself supports a stronger statement: 73 OC4IDS fields mapped, two of four template sheets near zero (Linked Releases 0/6, Parties 18/968).',
     "Rewrite the first paragraph of the executive summary to lead with the headline numbers and the two silent sheets.",
     "Zambia Technical Team"),
    ("R2", "Critical", "Phase-level percentages are discussed but not reported.",
     "Section 4 describes each phase qualitatively. A quantitative line per phase is recoverable directly from the template: identification 28%, preparation 12%, procurement 21%, implementation 2%, completion 8%, maintenance 0%, decommissioning 0%.",
     "Add a phase coverage table to section 4: one row per phase, with percentage, dominant reason for the gap, and a short example.",
     "Zambia Technical Team"),
    ("R3", "Critical", "Source-field provenance is in the template but not in the report.",
     "Every mapped OC4IDS path in the template is already traced to a ZPPA e-GP source path (for example, the OC4IDS project id comes from zppa_egp.project.project.id).",
     "Add a source column to the section 5 phase tables: the OC4IDS path, the ZPPA e-GP source path, and the current status.",
     "Zambia Technical Team"),
    ("R4", "Critical", "Recommendations carry no owner or timeline.",
     "Sections 6.1 to 6.6 list six recommendation groups. All are directional. None names an institution, a person, or a quarter.",
     "Assign each recommendation to a specific institution (NCC, ZPPA, CoST Zambia, or the relevant ministry) with a proposed quarter. Cite the legal provision each recommendation operationalises. Timelines will be confirmed by the MSG.",
     "CoST Zambia with NCC and ZPPA"),
    ("R5", "High", "Gaps are listed by phase but not classified by cause.",
     "The strongest implicit finding in the report is that most of the missing implementation data is already collected by NCC but is not publicly disclosed. That is a different problem from data that does not exist at all, and it takes a different fix.",
     "Classify each material gap as one of: not collected, collected but not disclosed, collected only in unstructured documents, collected inconsistently, restricted by law or workflow. Label the NCC insight explicitly as 'collected but not yet disclosed'.",
     "Zambia Technical Team"),
    ("R6", "High", "Data published beyond OC4IDS is not examined.",
     "The report does not discuss which fields the ZPPA e-GP or NCC publish today that fall outside OC4IDS. That is useful country context for both the Zambia audience and for OCP's future OC4IDS revisions.",
     "Add a short section listing non-OC4IDS fields the country publishes, with a recommendation on whether to preserve them as extensions or to propose them for the standard.",
     "Zambia Technical Team with CoST IS"),
    ("R7", "High", "The conclusion does not classify what can be published now.",
     "Section 8.2 is a first pass at who holds data at which stage, but it does not separate fields that can be published today from those requiring new workflows or new law.",
     "Add a decision summary at the end of the report: four groups (ready to publish, small format fixes, needs system work, needs policy action), with a short example in each. This is the table a Permanent Secretary reads first.",
     "Zambia Technical Team"),
    ("R8", "Medium", "The portal URL and access dates are missing from the body.",
     "The ZPPA e-GP URL (eprocure.zppa.org.zm/epps/home.d) is in the attached mapping template but not in the report itself.",
     "Add the URL and the dates the system was accessed to section 3.1.",
     "Zambia Technical Team"),
    ("R9", "Medium", "The sample is not quantified.",
     "Section 3 says 'the ZPPA e-GP system was analysed' without specifying what was analysed.",
     "State the count of procurement records reviewed, the aggregate value, the sectors covered, the time window, and how records were selected.",
     "Zambia Technical Team"),
    ("R10", "Low", "Some unmapped rows in the template lack a reason.",
     "A spot-check of five unmapped rows in the OC4IDS sheets found no note explaining why the field was left blank.",
     "Before resubmission, add a short Notes entry to every unmapped row in the (OC4IDS) sheets. One line per row is sufficient.",
     "Zambia Technical Team"),
]

rt = doc.add_table(rows=len(revs) + 1, cols=6)
set_table_full_width(rt)
apply_col_widths(rt, [1.1, 2.1, 5.0, 7.6, 6.4, 3.9])

headers = ["Ref", "Priority", "Issue", "Evidence", "Revision requested", "Proposed owner"]
for i, h in enumerate(headers):
    c = rt.rows[0].cells[i]
    set_cell_shading(c, "2D2D2D")
    set_cell_borders(c, top="single", bottom="single", left="single", right="single", color="2D2D2D")
    add_run(c.paragraphs[0], h, bold=True, size_pt=10, color=WHITE)

prio_map = {
    "Critical": (RED, CRITICAL_BG),
    "High": (BLUE, HIGH_BG),
    "Medium": (MEDIUM_TEXT, MEDIUM_BG),
    "Low": (LOW_TEXT, LOW_BG),
}
for ri, (ref, prio, issue, ev, rec, owner) in enumerate(revs, start=1):
    cells = rt.rows[ri].cells
    bg = LGRAY if ri % 2 == 0 else WHITE
    for c in cells:
        set_cell_shading(c, bg)
        set_cell_borders(c)
    add_run(cells[0].paragraphs[0], ref, bold=True, size_pt=9.5, color=CHARCOAL)
    pc_text_color, pc_bg = prio_map[prio]
    set_cell_shading(cells[1], pc_bg)
    add_run(cells[1].paragraphs[0], prio, bold=True, size_pt=9.5, color=pc_text_color)
    add_run(cells[2].paragraphs[0], issue, bold=True, size_pt=9.5, color=CHARCOAL)
    add_run(cells[3].paragraphs[0], ev, size_pt=9.5, color=CHARCOAL)
    add_run(cells[4].paragraphs[0], rec, size_pt=9.5, color=CHARCOAL)
    add_run(cells[5].paragraphs[0], owner, size_pt=9.5, color=CHARCOAL)

para(doc, "", space_after=12)

# ─── Decision summary preview ───────────────────────────────────────────────
doc.add_page_break()
p = doc.add_paragraph()
add_run(p, "5.  What Zambia can publish now", bold=True, size_pt=13, color=CHARCOAL)
accent_bar(doc, RED, width_cm=8)
para(doc, "", space_after=4)

para(doc, "This is the reading this review asks for in R7 above. It is also the single table the report's primary audience (MSG members, permanent secretaries, senior officials) will read first. An indicative version, drawn from the current mapping template, appears below. The revision should produce a version reviewed by the Zambia team before publication.",
     size_pt=10.5, space_after=8)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(str(CHARTS / "03-decision-buckets.png"), width=Cm(22))
para(doc, "", space_after=14)

# ─── Law already permits most of it ────────────────────────────────────────
p = doc.add_paragraph()
add_run(p, "6.  The law already permits most of what is missing", bold=True, size_pt=13, color=CHARCOAL)
accent_bar(doc, RED, width_cm=8)
para(doc, "", space_after=4)

para(doc, "This is the point the legal framework analysis in Annex 8.1 already makes. It is worth pulling forward into the body of the report:",
     size_pt=10.5, space_after=8)

# Simple, labelled table instead of a misleading 4-bar chart
lt = doc.add_table(rows=4, cols=3)
set_table_full_width(lt)
apply_col_widths(lt, [7.0, 11.5, 7.6])
headers = ["Legal authority", "What it authorises", "Relevance to OC4IDS publication"]
for i, h in enumerate(headers):
    c = lt.rows[0].cells[i]
    set_cell_shading(c, "2D2D2D")
    set_cell_borders(c, top="single", bottom="single", left="single", right="single", color="2D2D2D")
    add_run(c.paragraphs[0], h, bold=True, size_pt=10, color=WHITE)

legal_rows = [
    ("Access to Information Act 2023, s.8",
     "Proactive publication by every information holder of contracts signed, suppliers, amounts, and periods for completion.",
     "Broad: covers most procurement-stage and contract-stage OC4IDS fields."),
    ("NCC Act 2020, s.53",
     "Regular project monitoring and evaluation by the National Council for Construction, with the right to request records and to share information across authorities.",
     "Depth: covers implementation-stage fields (progress, quality, variations) that ZPPA does not currently publish."),
    ("ZPPA Act 2020, s.67 and s.70",
     "Transparency of procurement records subject to confidentiality provisions.",
     "Procurement-specific: already supports the fields the e-GP system publishes today."),
]
for ri, r in enumerate(legal_rows, start=1):
    cells = lt.rows[ri].cells
    bg = LGRAY if ri % 2 == 0 else WHITE
    for c in cells:
        set_cell_shading(c, bg)
        set_cell_borders(c)
    add_run(cells[0].paragraphs[0], r[0], bold=True, size_pt=9.5, color=CHARCOAL)
    add_run(cells[1].paragraphs[0], r[1], size_pt=9.5, color=CHARCOAL)
    add_run(cells[2].paragraphs[0], r[2], size_pt=9.5, color=CHARCOAL)

para(doc, "", space_after=12)

# Callout box with the core legal implication
cb = doc.add_table(rows=1, cols=1)
set_table_full_width(cb)
apply_col_widths(cb, [CONTENT_W_CM])
cc = cb.cell(0, 0)
set_cell_shading(cc, LGRAY)
set_cell_borders(cc, left="single", color=hex_of(BLUE), sz="32")
ccp = cc.paragraphs[0]
add_run(ccp, "IMPLICATION  ", bold=True, size_pt=10, color=BLUE)
add_run(ccp, "Publishing most of the missing implementation data does not require new law. It requires an integration layer between ZPPA and NCC, and a short statutory instrument clarifying that the two systems share publication-relevant records. The revision should make this case in the recommendations section.",
        size_pt=10.5, color=CHARCOAL)
para(doc, "", space_after=14)

# ─── Next step ──────────────────────────────────────────────────────────────
p = doc.add_paragraph()
add_run(p, "7.  Next step", bold=True, size_pt=13, color=CHARCOAL)
accent_bar(doc, RED, width_cm=8)
para(doc, "", space_after=4)

para(doc, "This review is a working document between CoST IS and the Zambia Technical Team. The covering note proposes a short call to walk through the ten revisions and agree a resubmission schedule with the MSG. A companion document (02-structural-reference.docx) is attached: it is a short illustrative extract, not a rewrite of the report. Use it as a reference for the kind of specificity a strong report carries, not as content to adopt.",
     size_pt=10.5, space_after=12)

# Source footer
para(doc, "Source: Zambia OC4IDS field-level mapping template v0.9.5, accessed 2026-04-23. Zambia OC4IDS field-level mapping report (draft), 3 March 2026.",
     size_pt=9, italic=True, color=MUTED, space_after=0)

doc.save(str(OUT))
print(f"OK {OUT}")
