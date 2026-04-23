"""Build Doc 1 (v0.12): CoST IS review + structural reference, merged.

Replaces the separate review letter and structural reference documents.
Pairs REVIEW NOTE callouts (CoST Red) with EXAMPLE callouts (CoST Blue),
section by section, so the country team reads each problem alongside the
pattern the revised report should follow.

Layout: Portrait A4, 22mm margins. Target length 12 to 14 pages.
"""
import pathlib
from docx import Document
from docx.shared import Cm, Mm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import _docx_helpers as H
from visuals.infographics import cover_photo_strip

CHARTS = pathlib.Path(__file__).parent.parent / "charts"
OUT = pathlib.Path(__file__).parent.parent / "01-review-and-reference.docx"
CONTENT_W = 16.6

# Build the cover photo strip as one PNG at exact content width so it aligns
# flush with the red title block below.
_COVER_STRIP = CHARTS / "cover-strip-review-and-reference.png"
cover_photo_strip(
    [
        H.ASSETS / "stock-africa-rural-road.jpeg",
        H.ASSETS / "stock-africa-highway-aerial.jpeg",
        H.ASSETS / "stock-africa-scaffolding.jpeg",
    ],
    _COVER_STRIP,
    target_width_cm=CONTENT_W,
    strip_height_mm=46,
)


# ─── Document setup ─────────────────────────────────────────────────────────
doc = Document()
H.setup_portrait(doc.sections[0], margin_mm=22)
H.setup_base_style(doc)
H.add_logo_header(doc.sections[0])
H.add_stripe_footer(doc.sections[0])


# ─── Cover ──────────────────────────────────────────────────────────────────
# Single composed PNG anchored inside a 1x1 table at EXACTLY CONTENT_W — the
# same anchoring the red block uses, so the two edges are byte-identical.
strip_tbl = doc.add_table(rows=1, cols=1)
H.set_table_full_width(strip_tbl, CONTENT_W)
H.apply_col_widths(strip_tbl, [CONTENT_W])
scell = strip_tbl.rows[0].cells[0]
H.set_cell_margins(scell, top=0, bottom=0, left=0, right=0)
H.set_cell_borders(scell)
scp = scell.paragraphs[0]
scp.paragraph_format.space_before = Pt(0)
scp.paragraph_format.space_after = Pt(0)
scp.add_run().add_picture(str(_COVER_STRIP), width=Cm(CONTENT_W))

# Red title block
red = doc.add_table(rows=1, cols=1)
H.set_table_full_width(red, CONTENT_W)
H.apply_col_widths(red, [CONTENT_W])
rcell = red.rows[0].cells[0]
H.set_cell_shading(rcell, H.COVER_RED)
H.set_cell_margins(rcell, top=500, bottom=500, left=480, right=480)
H.set_cell_borders(rcell)
rcp = rcell.paragraphs[0]
rcp.paragraph_format.space_after = Pt(4)
H.add_run(rcp, "CoST IS REVIEW AND STRUCTURAL REFERENCE",
          bold=True, size_pt=11, color=H.WHITE)
rcp2 = rcell.add_paragraph()
rcp2.paragraph_format.space_after = Pt(8)
H.add_run(rcp2, "Feedback on the Zambia OC4IDS field-level mapping report, paired with worked examples of what a revised section should look like.",
          bold=True, size_pt=16, color=H.WHITE)
rcp3 = rcell.add_paragraph()
rcp3.paragraph_format.space_after = Pt(0)
H.add_run(rcp3, "Zambia: ZPPA, NCC, CoST Zambia.  Draft of 3 March 2026 reviewed on 23 April 2026.",
          size_pt=10, color=H.WHITE)

H.para(doc, "", space_after=10)

# Non-commitment disclaimer
H.callout_box(
    doc, CONTENT_W,
    label="HOW TO READ THIS DOCUMENT",
    label_color=H.DMUTED,
    body="This document pairs the CoST IS review with worked examples. Each major section carries up to three blocks: a QUOTED FROM DRAFT block (the passage from the current report, in grey) so you can see exactly what the review note targets, a REVIEW NOTE (what is wrong and why, in red), and an EXAMPLE (what the revised section should look like, in blue). QUOTED blocks marked [QUOTE] are placeholders for the Zambia team to replace with verbatim text from the current draft. The full list of priority revisions sits once, in section 8. A companion document, 02-sample-final-report.docx, carries a fully-worked model report the Zambia team can adapt directly. Every stakeholder name, number, and date in the EXAMPLE blocks and the companion model is a placeholder pending MSG consultation.",
)
H.para(doc, "", space_after=10)

# Metadata
meta = doc.add_table(rows=3, cols=2)
H.set_table_full_width(meta, CONTENT_W)
H.apply_col_widths(meta, [5.0, CONTENT_W - 5.0])
for i, (k, v) in enumerate([
    ("Reviewed by:",
     "CoST International Secretariat. This review applies CoST IS's OC4IDS mapping review methodology."),
    ("Review date:", "23 April 2026."),
    ("Companion:",
     "02-sample-final-report.docx. A fully-worked model report for Zambia. Structure and format are illustrative; stakeholder names are placeholders."),
]):
    kc = meta.rows[i].cells[0]
    vc = meta.rows[i].cells[1]
    for c in (kc, vc):
        H.set_cell_borders(c)
        H.set_cell_margins(c, top=140, bottom=140, left=180, right=180)
    H.add_run(kc.paragraphs[0], k, bold=True, size_pt=9.5, color=H.DMUTED)
    H.add_run(vc.paragraphs[0], v, size_pt=9.5, color=H.CHARCOAL)


# ─── Page 2: Verdict + What is working ─────────────────────────────────────
doc.add_page_break()
H.heading(doc, "Verdict", level=1)

# Glance anchor , three headline numbers before the verdict.
H.centered_image(doc, CHARTS / "04-headline-stats.png", width_cm=CONTENT_W,
                 space_before=0, space_after=12)

H.verdict_box(
    doc, CONTENT_W,
    label="VERDICT",
    headline="The Zambia mapping template is substantively strong: 73 OC4IDS fields mapped, every mapped field backed by a real source path, and 47 of 48 source elements traced forward into OC4IDS.",
    tail="The narrative report does not yet reflect the strength of the underlying work. The executive summary leads with adjectives rather than numbers, the lifecycle findings are described but not quantified, and most recommendations have no named owner. The legal framework analysis in Annex 8.1 is publication-quality and should anchor the report's front page, not sit at the back.",
)
H.para(doc, "", space_after=14)

H.heading(doc, "1.  What is working", level=1)

H.para(doc, "These elements of the current draft are already at the level a reader needs. Keep them on revision.",
       size_pt=10.5, space_after=8)

strengths = [
    ("Legal framework analysis in Annex 8.1.",
     "The citations to the Access to Information Act 2023 (s.6, s.8, s.9, s.17), the ZPPA Act 2020 (s.67, s.70), and the NCC Act 2020 (s.5, s.31, s.33, s.53) are precise and directly tied to disclosure obligations. This is the report's strongest asset. Move the substance forward into the executive summary; keep the full text in the annex."),
    ("The NCC insight.",
     "The observation in section 4.1 that most implementation-stage data is already collected by NCC under its statutory monitoring mandate is the single most actionable finding in the report. It reframes the question from 'how do we collect this data' to 'how do we integrate and disclose what is already collected'. Make this the headline of the recommendations section."),
    ("Source element forward-mapping.",
     "The template maps 47 of the 48 source data elements from the ZPPA e-GP system into OC4IDS paths. That coverage is excellent. Report the number in the methodology section."),
    ("Lifecycle framework in section 8.2.",
     "The five-row data-source-by-stage table is a foundation for the decision summary this review asks for. Expand it into the four-bucket classification shown in section 9 below."),
    ("Mapping quality.",
     "Every OC4IDS path the template lists as mapped contains real source content. No placeholders. A reviewer sampling the mapping sheets can verify every line back to the ZPPA e-GP schema."),
]
for title, body in strengths:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    H.add_run(p, "+  ", bold=True, size_pt=11, color=H.LOW_TEXT)
    H.add_run(p, title + "  ", bold=True, size_pt=10.5, color=H.CHARCOAL)
    H.add_run(p, body, size_pt=10.5, color=H.CHARCOAL)


# ─── Section 2: How to read this ───────────────────────────────────────────
doc.add_page_break()
H.heading(doc, "2.  How to read this document", level=1)

H.para(doc, "The rest of this document walks through the revised report section by section. Each of the seven sections below (3 through 9) carries the same two-part format:",
       size_pt=10.5, space_after=8)

H.para(doc, "•   A REVIEW NOTE block in red, naming what the current draft does and which revision identifier in section 8 addresses it.",
       size_pt=10.5, space_after=4)
H.para(doc, "•   An EXAMPLE block in blue, showing what the revised section should look like, with a representative row, table, or chart.",
       size_pt=10.5, space_after=10)

H.para(doc, "The full list of priority revisions, R1 through R10, sits in section 8. Section 10 covers the legal lever (what the law already permits) and section 11 sets out the next step. The companion document 02-sample-final-report.docx carries every section filled out as a worked model, with placeholder stakeholder names pending MSG consultation.",
       size_pt=10.5, space_after=10)


# ─── Section 3: Executive summary ──────────────────────────────────────────
doc.add_page_break()
H.heading(doc, "3.  Executive summary", level=1)

H.quoted_passage(
    doc, CONTENT_W,
    source_hint="Executive summary, para 1 (draft of 3 March 2026)",
    body="[QUOTE , Zambia team to paste opening sentence of the current executive summary verbatim. The current draft's opening reads, approximately: 'Significant data gaps exist in Zambia's disclosure of infrastructure procurement and implementation data across the OC4IDS standard.']",
)
H.para(doc, "", space_after=6)

H.review_note(
    doc, CONTENT_W,
    ref_ids=["R1"],
    body="The current opening reads 'significant data gaps exist'. Adjectives do not travel. The template supports a much stronger statement: 73 OC4IDS fields mapped, two of four template sheets near zero (Linked Releases 0 of 6, Parties 18 of 968). Lead with those numbers and the structural reading becomes visible from the first paragraph.",
)
H.para(doc, "", space_after=10)


def _exec_summary_content(cell):
    p = cell.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    H.add_run(p, "The revised opening should lead with three numbers, not three adjectives:",
              size_pt=10.5, color=H.CHARCOAL, italic=True)

    inner = cell.add_table(rows=1, cols=3)
    H.set_table_full_width(inner, CONTENT_W - 1.2)
    col = (CONTENT_W - 1.2) / 3
    H.apply_col_widths(inner, [col, col, col])
    H.set_row_height(inner.rows[0], 4.5)

    for i, (val, label, col_color) in enumerate([
        ("35",
         "OC4IDS fields the ZPPA e-GP system can publish today, with no new work.",
         H.LOW_TEXT),
        ("55",
         "Publishable within 12 months (35 today plus 20 after format fixes).",
         H.BLUE),
        ("Yes",
         "Zambia's existing law (ATI Act s.8, NCC Act s.53) already permits publication of most currently-missing fields.",
         H.RED),
    ]):
        c = inner.rows[0].cells[i]
        H.set_cell_shading(c, H.LGRAY)
        H.set_cell_margins(c, top=220, bottom=220, left=240, right=240)
        H.set_cell_borders(c, top="single", color=H.hex_of(col_color), sz="40")
        p1 = c.paragraphs[0]
        H.add_run(p1, val, bold=True, size_pt=24, color=col_color)
        p2 = c.add_paragraph()
        p2.paragraph_format.space_before = Pt(2)
        H.add_run(p2, label, size_pt=8.5, color=H.DMUTED)


H.example_block(doc, CONTENT_W,
                label_detail="Target opening for section 1 of the revised report",
                content_fn=_exec_summary_content)


# ─── Section 4: Phase coverage ─────────────────────────────────────────────
doc.add_page_break()
H.heading(doc, "4.  Findings by lifecycle phase", level=1)

H.quoted_passage(
    doc, CONTENT_W,
    source_hint="Section 4, opening paragraph (draft of 3 March 2026)",
    body="[QUOTE , Zambia team to paste one or two sentences from the current section 4 that describe implementation-stage coverage without a number. The draft currently reads, approximately: 'Implementation-stage disclosure is thin, with most fields unpopulated or populated only in narrative form. Maintenance and decommissioning remain largely unaddressed by the current template submission.']",
)
H.para(doc, "", space_after=6)

H.review_note(
    doc, CONTENT_W,
    ref_ids=["R2"],
    body="The current section 4 describes each phase qualitatively and never states a percentage. The template allows a quantified line for every phase: identification 28%, preparation 12%, procurement 21%, implementation 2%, completion 8%, maintenance 0%, decommissioning 0%. The chart below reads in five seconds. The revised report should carry a full phase coverage table in addition.",
)
H.para(doc, "", space_after=10)

H.centered_image(doc, CHARTS / "02-phase-coverage.png", width_cm=CONTENT_W - 0.4,
                 space_before=4, space_after=10)


def _phase_row_content(cell):
    p = cell.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(6)
    H.add_run(p, "One row from the full phase table, illustrated:",
              size_pt=10.5, color=H.CHARCOAL, italic=True)

    ph = cell.add_table(rows=2, cols=4)
    H.set_table_full_width(ph, CONTENT_W - 1.2)
    H.apply_col_widths(ph, [2.6, 1.9, 4.0, CONTENT_W - 1.2 - 8.5])
    H.apply_default_padding(ph)
    H.styled_table_header(ph.rows[0],
                          ["Phase", "Coverage", "Dominant cause", "Example"])

    H.set_row_height(ph.rows[1], 2.6)
    row = ph.rows[1].cells
    for c in row:
        H.set_cell_borders(c)
        H.set_cell_shading(c, H.WHITE)
    H.add_run(row[0].paragraphs[0], "Implementation", bold=True, size_pt=10, color=H.CHARCOAL)
    H.add_run(row[1].paragraphs[0], "2%", bold=True, size_pt=12, color=H.RED)
    H.add_run(row[2].paragraphs[0],
              "Collected but not yet publicly disclosed. Data sits in NCC inspection records.",
              size_pt=9.5, color=H.CHARCOAL)
    H.add_run(row[3].paragraphs[0],
              "Contract variations, progress updates, payment certificates, and quality-assurance reports are captured by NCC under NCC Act 2020 s.53 and shared with ZPPA only on request. Integration, not new collection, is the remediation.",
              size_pt=9.5, color=H.CHARCOAL)


H.example_block(doc, CONTENT_W,
                label_detail="Target format for one row of the phase coverage table",
                content_fn=_phase_row_content)


# ─── Section 5: Source provenance ──────────────────────────────────────────
doc.add_page_break()
H.heading(doc, "5.  Source-field provenance", level=1)

H.review_note(
    doc, CONTENT_W,
    ref_ids=["R3"],
    body="The template already traces every mapped OC4IDS path to a specific ZPPA e-GP source path. The report does not surface this. A reader of the narrative cannot see what system each field comes from. Add a source column to the phase findings table, or include a provenance annex. One row of the target format appears below.",
)
H.para(doc, "", space_after=10)


def _prov_row_content(cell):
    p = cell.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(6)
    H.add_run(p, "One row from the full provenance table, illustrated:",
              size_pt=10.5, color=H.CHARCOAL, italic=True)

    pv = cell.add_table(rows=2, cols=4)
    H.set_table_full_width(pv, CONTENT_W - 1.2)
    H.apply_col_widths(pv, [3.6, 5.0, 2.4, CONTENT_W - 1.2 - 11.0])
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
    H.add_run(row[2].paragraphs[0], "Populated",
              bold=True, size_pt=10, color=H.LOW_TEXT)
    H.add_run(row[3].paragraphs[0], "Ready to publish",
              size_pt=10, color=H.CHARCOAL)


H.example_block(doc, CONTENT_W,
                label_detail="Target format for one row of the provenance annex",
                content_fn=_prov_row_content)


# ─── Section 6: Why the gaps exist ─────────────────────────────────────────
doc.add_page_break()
H.heading(doc, "6.  Why the gaps exist", level=1)

H.quoted_passage(
    doc, CONTENT_W,
    source_hint="Section 4.1 or equivalent, on implementation data (draft of 3 March 2026)",
    body="[QUOTE , Zambia team to paste the draft's description of the NCC monitoring role verbatim. The draft currently refers to NCC's statutory role without naming it as a 'collected but not yet disclosed' gap; typically something like: 'The National Council for Construction maintains inspection and project monitoring records under its statutory mandate, although these are not currently integrated with ZPPA's disclosure channels.']",
)
H.para(doc, "", space_after=6)

H.review_note(
    doc, CONTENT_W,
    ref_ids=["R5"],
    body="The current draft lists gaps by phase but not by cause. This matters because different causes take different fixes: 'not collected' needs a new workflow, 'collected but not disclosed' needs integration, 'restricted by law' needs regulation. The strongest implicit finding in the current draft (NCC already collects implementation data) is a 'collected but not disclosed' gap; labelling it out loud reframes the whole recommendations section.",
)
H.para(doc, "", space_after=8)

# Integration-pathway visual , the thesis of the whole document.
H.centered_image(doc, CHARTS / "05-integration-pathway.png", width_cm=CONTENT_W,
                 space_before=0, space_after=12)


def _typology_content(cell):
    p = cell.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(6)
    H.add_run(p, "Classify every material gap against the five causes below. The Zambia-dominant cause is the second row, highlighted in red.",
              size_pt=10.5, color=H.CHARCOAL, italic=True)

    typology = [
        ("Not collected", "Data does not exist in any reviewed system.",
         "Maintenance schedules.", "New workflow plus budget."),
        ("Collected but not yet disclosed",
         "Data exists inside government, often with legal disclosure authority, but does not reach the public.",
         "Contract variations and payment certificates held by NCC.",
         "Integration between systems. A short statutory instrument may be enough."),
        ("Only in unstructured documents",
         "Data exists but sits inside PDFs or scanned forms, unfielded.",
         "Project briefs, ESIA narratives.",
         "Fielded metadata at upload."),
        ("Collected inconsistently",
         "Captured on some projects, not others; format varies.",
         "Tender-evaluation free-text fields.",
         "Standardisation before publication."),
        ("Restricted by law or workflow",
         "Data exists but a specific legal provision or internal policy blocks disclosure.",
         "Beneficial ownership of contracting firms.",
         "Regulation or policy change, not a technical fix."),
    ]

    tt = cell.add_table(rows=len(typology) + 1, cols=4)
    H.set_table_full_width(tt, CONTENT_W - 1.2)
    col_w = (CONTENT_W - 1.2 - 3.4) / 3
    H.apply_col_widths(tt, [3.4, col_w, col_w, col_w])
    H.apply_default_padding(tt)
    H.styled_table_header(tt.rows[0],
                          ["Cause", "What it means",
                           "Zambia example", "What fixes it"])

    for ri, r in enumerate(typology, start=1):
        cells = tt.rows[ri].cells
        H.set_row_height(tt.rows[ri], 1.6)
        accent = ri == 2
        bg = H.LGRAY if ri % 2 == 0 else H.WHITE
        for c in cells:
            H.set_cell_borders(c)
            H.set_cell_shading(c, bg)
        for ci, v in enumerate(r):
            H.add_run(cells[ci].paragraphs[0], v,
                      bold=(ci == 0 and accent),
                      size_pt=9.5,
                      color=(H.RED if ci == 0 and accent else H.CHARCOAL))


H.example_block(doc, CONTENT_W,
                label_detail="Five-cause typology for gap classification",
                content_fn=_typology_content)


# ─── Section 7: Non-template fields ────────────────────────────────────────
doc.add_page_break()
H.heading(doc, "7.  Data beyond OC4IDS", level=1)

H.review_note(
    doc, CONTENT_W,
    ref_ids=["R6"],
    body="The current draft does not examine what the ZPPA e-GP or NCC systems publish that falls outside OC4IDS. Country-specific disclosure that could feed upstream to OCP is invisible. Preserving useful local fields as extensions (rather than dropping them) is part of a mature mapping report. Three candidate extensions identified from the template appear below.",
)
H.para(doc, "", space_after=10)


def _extensions_content(cell):
    p = cell.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(6)
    H.add_run(p, "Country-specific fields worth preserving as OC4IDS extensions:",
              size_pt=10.5, color=H.CHARCOAL, italic=True)

    ext = cell.add_table(rows=4, cols=2)
    H.set_table_full_width(ext, CONTENT_W - 1.2)
    H.apply_col_widths(ext, [5.2, CONTENT_W - 1.2 - 5.2])
    H.apply_default_padding(ext)
    H.styled_table_header(ext.rows[0],
                          ["Zambia-specific field",
                           "Why preserve it as an OC4IDS extension"])

    rows = [
        ("Local project-reference scheme",
         "A 14-character code combining sector, ministry, and year of approval. Used as internal cross-reference by the Ministry of Finance. Candidate for an extension field (zambia:projectReference)."),
        ("NCC contractor grade",
         "A capability grade (1 to 6) assigned by NCC to registered contractors. Informs cross-country comparisons of contractor capacity. Candidate for the Parties sheet (zambia:contractorGrade)."),
        ("Force-account flag",
         "A flag indicating whether implementation is by direct government labour. Currently invisible in OC4IDS. Worth proposing to OCP for inclusion in the procurement-method codelist."),
    ]
    for ri, r in enumerate(rows, start=1):
        cells = ext.rows[ri].cells
        H.set_row_height(ext.rows[ri], 1.5)
        bg = H.LGRAY if ri % 2 == 0 else H.WHITE
        for c in cells:
            H.set_cell_shading(c, bg)
            H.set_cell_borders(c)
        H.add_run(cells[0].paragraphs[0], r[0], bold=True, size_pt=10, color=H.CHARCOAL)
        H.add_run(cells[1].paragraphs[0], r[1], size_pt=10, color=H.CHARCOAL)


H.example_block(doc, CONTENT_W,
                label_detail="Target content for the non-template-fields section",
                content_fn=_extensions_content)


# ─── Section 8: Priority revisions (the full table) ────────────────────────
doc.add_page_break()
H.heading(doc, "8.  Priority revisions requested", level=1)

H.review_note(
    doc, CONTENT_W,
    ref_ids=["R4"],
    body="Recommendations 6.1 to 6.6 in the current draft are directional. None names an institution, a person, or a quarter. The table below lists the ten revisions this review asks for, each with a proposed owner. Timelines are placeholders; the MSG sets them. Sections 3 through 9 above each cite one of these identifiers.",
)
H.para(doc, "", space_after=10)

revs = [
    ("R1", "Critical", "Executive summary carries no number.",
     "Rewrite the opening paragraph to lead with the headline numbers and the two silent sheets.",
     "Zambia Technical Team"),
    ("R2", "Critical", "Phase-level percentages not reported.",
     "Add a phase coverage table to section 4: one row per phase with percentage, cause, and example.",
     "Zambia Technical Team"),
    ("R3", "Critical", "Source-field provenance not surfaced.",
     "Add a source column to the section 5 phase tables, or include a provenance annex. One row per mapped field.",
     "Zambia Technical Team"),
    ("R4", "Critical", "Recommendations carry no owner or timeline.",
     "Assign each recommendation to a specific institution with a proposed quarter. Cite the legal provision it operationalises.",
     "CoST Zambia with NCC and ZPPA"),
    ("R5", "High", "Gaps not classified by cause.",
     "Apply the five-cause typology in section 6 to every material gap. Label the NCC insight as 'collected but not yet disclosed'.",
     "Zambia Technical Team"),
    ("R6", "High", "Data beyond OC4IDS not examined.",
     "Add a short section listing non-OC4IDS fields the country publishes. Recommend which to preserve as extensions.",
     "Zambia Technical Team with CoST IS"),
    ("R7", "High", "Conclusion does not classify what can be published now.",
     "Add a decision summary at the end: ready to publish, small format fixes, needs system work, needs policy action.",
     "Zambia Technical Team"),
    ("R8", "Medium", "Portal URL and access dates missing from the body.",
     "Add the ZPPA e-GP URL and the dates accessed to section 3.1.",
     "Zambia Technical Team"),
    ("R9", "Medium", "Sample not quantified.",
     "State count, aggregate value, sectors, time window, and selection method in section 3.",
     "Zambia Technical Team"),
    ("R10", "Low", "Unmapped template rows lack reasons.",
     "Before resubmission, add a short Notes entry to every unmapped row in the OC4IDS sheets.",
     "Zambia Technical Team"),
]

rt = doc.add_table(rows=len(revs) + 1, cols=5)
H.set_table_full_width(rt, CONTENT_W)
H.apply_col_widths(rt, [0.9, 1.8, 4.2, 6.1, CONTENT_W - 13.0])
H.apply_default_padding(rt)
H.styled_table_header(rt.rows[0],
                      ["Ref", "Priority", "Issue", "Revision requested",
                       "Proposed owner"],
                      size_pt=9.5)

prio_map = {
    "Critical": (H.RED, H.CRITICAL_BG),
    "High": (H.BLUE, H.HIGH_BG),
    "Medium": (H.MEDIUM_TEXT, H.MEDIUM_BG),
    "Low": (H.LOW_TEXT, H.LOW_BG),
}
for ri, (ref, prio, issue, rec, owner) in enumerate(revs, start=1):
    cells = rt.rows[ri].cells
    H.set_row_height(rt.rows[ri], 1.6)
    bg = H.LGRAY if ri % 2 == 0 else H.WHITE
    for c in cells:
        H.set_cell_shading(c, bg)
        H.set_cell_borders(c)
    H.add_run(cells[0].paragraphs[0], ref, bold=True, size_pt=9.5, color=H.CHARCOAL)
    pc_text, pc_bg = prio_map[prio]
    H.set_cell_shading(cells[1], pc_bg)
    H.add_run(cells[1].paragraphs[0], prio, bold=True, size_pt=9, color=pc_text)
    H.add_run(cells[2].paragraphs[0], issue, bold=True, size_pt=9, color=H.CHARCOAL)
    H.add_run(cells[3].paragraphs[0], rec, size_pt=9, color=H.CHARCOAL)
    H.add_run(cells[4].paragraphs[0], owner, size_pt=9, color=H.CHARCOAL)


# ─── Section 9: Decision summary ───────────────────────────────────────────
doc.add_page_break()
H.heading(doc, "9.  Decision summary", level=1)

H.quoted_passage(
    doc, CONTENT_W,
    source_hint="Section 8.2 (draft of 3 March 2026) , data-holder lifecycle table",
    body="[QUOTE , Zambia team to paste one or two rows of the current section 8.2 lifecycle table. Currently the table names the holder and the stage, but does not say which fields can go public today. Example row from the draft: 'Implementation , NCC , Project monitoring records, inspection forms, progress reports.']",
)
H.para(doc, "", space_after=6)

H.review_note(
    doc, CONTENT_W,
    ref_ids=["R7"],
    body="The current section 8.2 lists who holds data at each stage but does not separate fields that can be published today from those requiring new workflows or new law. This is the single table the report's primary audience (MSG members, permanent secretaries) will read first. Build it from the four buckets below.",
)
H.para(doc, "", space_after=10)

H.centered_image(doc, CHARTS / "03-decision-buckets.png", width_cm=CONTENT_W - 0.6,
                 space_before=4, space_after=10)


def _decision_panel_content(cell):
    p = cell.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(6)
    H.add_run(p, "Classify every publishable element into one of the four pathways below.",
              size_pt=10.5, color=H.CHARCOAL, italic=True)

    buckets = [
        ("Ready to publish",
         "Fields already held with clean source paths and clear legal authority.",
         "Approximately 35 fields. Project IDs, titles, sectors, procurement method, tender values.",
         H.LOW_TEXT),
        ("Small format fixes",
         "Fields present but needing date-format conversion, codelist alignment, or free-text standardisation.",
         "Approximately 20 fields. Descriptions, sector codes, date harmonisation.",
         H.BLUE),
        ("Needs system work",
         "Fields NCC already collects under NCC Act s.53 but that need an integration layer to reach the public.",
         "Approximately 73 fields. Contract variations, progress, quality and safety, payments, final costs.",
         H.YELLOW),
        ("Needs policy action",
         "Fields blocked by absence of a regulation, statutory instrument, or internal approval workflow.",
         "Approximately 25 fields. Beneficial ownership; maintenance and decommissioning capture.",
         H.RED),
    ]
    bt = cell.add_table(rows=len(buckets), cols=3)
    H.set_table_full_width(bt, CONTENT_W - 1.2)
    H.apply_col_widths(bt, [4.0, 5.8, CONTENT_W - 1.2 - 9.8])
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


H.example_block(doc, CONTENT_W,
                label_detail="Target format for the decision summary panel",
                content_fn=_decision_panel_content)


# ─── Section 10: Legal lever ───────────────────────────────────────────────
doc.add_page_break()
H.heading(doc, "10.  The law already permits most of what is missing", level=1)

H.para(doc, "This is the point Annex 8.1 of the current draft already makes. It is worth pulling forward into the body of the report:",
       size_pt=10.5, space_after=10)

lt = doc.add_table(rows=4, cols=3)
H.set_table_full_width(lt, CONTENT_W)
H.apply_col_widths(lt, [5.6, 6.5, CONTENT_W - 12.1])
H.apply_default_padding(lt)
H.styled_table_header(lt.rows[0],
                      ["Legal authority", "What it authorises",
                       "Relevance to OC4IDS publication"])

legal_rows = [
    ("Access to Information Act 2023, s.8",
     "Proactive publication by every information holder of contracts signed, suppliers, amounts, and periods for completion.",
     "Broad: covers most procurement-stage and contract-stage fields."),
    ("NCC Act 2020, s.53",
     "Regular project monitoring and evaluation by the National Council for Construction, with the right to request records and to share information across authorities.",
     "Depth: covers implementation-stage fields that ZPPA does not currently publish."),
    ("ZPPA Act 2020, s.67 and s.70",
     "Transparency of procurement records subject to confidentiality provisions.",
     "Procurement-specific: supports the fields the e-GP system publishes today."),
]
for ri, r in enumerate(legal_rows, start=1):
    cells = lt.rows[ri].cells
    H.set_row_height(lt.rows[ri], 1.6)
    bg = H.LGRAY if ri % 2 == 0 else H.WHITE
    for c in cells:
        H.set_cell_shading(c, bg)
        H.set_cell_borders(c)
    H.add_run(cells[0].paragraphs[0], r[0], bold=True, size_pt=10, color=H.CHARCOAL)
    H.add_run(cells[1].paragraphs[0], r[1], size_pt=10, color=H.CHARCOAL)
    H.add_run(cells[2].paragraphs[0], r[2], size_pt=10, color=H.CHARCOAL)

H.para(doc, "", space_after=12)

H.callout_box(
    doc, CONTENT_W,
    label="IMPLICATION",
    label_color=H.BLUE,
    body="Publishing most of the missing implementation data does not require new law. It requires an integration layer between ZPPA and NCC, and a short statutory instrument clarifying that the two systems share publication-relevant records. The revision should make this case in the recommendations section.",
)


# ─── Section 11: Next step ─────────────────────────────────────────────────
doc.add_page_break()
H.heading(doc, "11.  Next step", level=1)

H.para(doc, "This review is a working document between CoST IS and the Zambia Technical Team. The covering note proposes a short call to walk through the ten revisions and agree a resubmission schedule with the MSG.",
       size_pt=10.5, space_after=10)

H.para(doc, "One companion document accompanies this review:",
       size_pt=10.5, space_after=6)

H.para(doc, "•   02-sample-final-report.docx. A fully-worked model report for Zambia at the target standard. The structure, numbers, legal analysis, and recommendation logic are set at the level a CoST IS reviewer would accept on publication. Every stakeholder name is shown in square brackets as a placeholder; confirm all assignments through the MSG before the report is finalised. The Zambia team can adapt it directly.",
       size_pt=10.5, space_after=14)

H.para(doc, "Source: Zambia OC4IDS field-level mapping template v0.9.5, accessed 2026-04-23. Zambia OC4IDS field-level mapping report (draft), 3 March 2026.",
       size_pt=9, italic=True, color=H.MUTED, space_after=0)

doc.save(str(OUT))
print(f"OK {OUT}")
