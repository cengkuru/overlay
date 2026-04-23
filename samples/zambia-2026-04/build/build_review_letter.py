"""Build Doc 1: CoST IS review letter for the Zambia OC4IDS mapping report.

v0.11 changes:
- Uses _docx_helpers for shared table/padding/image logic.
- Generous table inner padding (titles no longer hug cell edges).
- Charts embedded with consistent centered margins.
- Row heights set so content never collapses.
"""
import pathlib
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import _docx_helpers as H

CHARTS = pathlib.Path(__file__).parent.parent / "charts"
OUT = pathlib.Path(__file__).parent.parent / "01-review-letter.docx"

# Landscape A4, 20mm margins => 25.7cm content width
CONTENT_W = 25.7

# ─── Document setup ─────────────────────────────────────────────────────────
doc = Document()
H.setup_landscape(doc.sections[0], margin_mm=20)
H.setup_base_style(doc)
H.add_logo_header(doc.sections[0])
H.add_stripe_footer(doc.sections[0])

# ─── Title block ────────────────────────────────────────────────────────────
H.para(doc, "CoST IS REVIEW", size_pt=11, bold=True, color=H.RED, space_after=2)
H.para(doc, "OC4IDS Field-Level Mapping Report", size_pt=22, bold=True,
       color=H.CHARCOAL, space_after=4)
H.para(doc, "Zambia: ZPPA, NCC, CoST Zambia   •   Draft of 3 March 2026",
       size_pt=13, color=H.DMUTED, space_after=12)
H.accent_bar(doc, H.RED, width_cm=20)
H.para(doc, "", space_after=10)

# Metadata block
meta = doc.add_table(rows=3, cols=2)
H.set_table_full_width(meta, CONTENT_W)
H.apply_col_widths(meta, [5.8, CONTENT_W - 5.8])
H.apply_default_padding(meta, header_row=-1)
meta_rows = [
    ("Reviewed by:",
     "CoST International Secretariat. This review applies CoST IS's OC4IDS mapping review methodology."),
    ("Review date:", "23 April 2026."),
    ("Companion documents:",
     "02-structural-reference.docx (short illustrative extract) and 03-sample-final-report.docx (a fully-worked model report the Zambia team can adapt)."),
]
for i, (k, v) in enumerate(meta_rows):
    kc, vc = meta.rows[i].cells
    H.add_run(kc.paragraphs[0], k, bold=True, size_pt=10, color=H.DMUTED)
    H.add_run(vc.paragraphs[0], v, size_pt=10.5, color=H.CHARCOAL)
    for c in (kc, vc):
        H.set_cell_borders(c)

H.para(doc, "", space_after=14)

# ─── Verdict ────────────────────────────────────────────────────────────────
H.verdict_box(
    doc, CONTENT_W,
    label="VERDICT",
    headline="The Zambia mapping template is substantively strong: 73 OC4IDS fields mapped, every mapped field backed by a real source path, and 47 of 48 source elements traced forward into OC4IDS.",
    tail="The narrative report does not yet reflect the strength of the underlying work. The executive summary leads with adjectives rather than numbers, the lifecycle findings are described but not quantified, and most recommendations have no named owner. The legal framework analysis in Annex 8.1 is publication-quality and should anchor the report's front page, not sit at the back.",
)
H.para(doc, "", space_after=16)

# ─── Section 1: What is working ────────────────────────────────────────────
p = doc.add_paragraph()
H.add_run(p, "1.  What is working", bold=True, size_pt=14, color=H.CHARCOAL)
H.accent_bar(doc, H.LOW_TEXT, width_cm=9)
H.para(doc, "", space_after=6)

H.para(doc, "These elements of the current draft are already at the level a reader needs. Keep them on revision.",
       size_pt=10.5, space_after=10)

strengths = [
    ("Legal framework analysis in Annex 8.1.",
     "The citations to the Access to Information Act 2023 (s.6, s.8, s.9, s.17), the ZPPA Act 2020 (s.67, s.70), and the NCC Act 2020 (s.5, s.31, s.33, s.53) are precise and directly tied to disclosure obligations. This is the report's strongest asset. Move the substance forward into the executive summary; keep the full text in the annex."),
    ("The NCC insight.",
     "The observation in section 4.1 that most implementation-stage data is already collected by NCC under its statutory monitoring mandate is the single most actionable finding in the report. It reframes the question from 'how do we collect this data' to 'how do we integrate and disclose what is already collected'. Make this the headline of the recommendations section."),
    ("Source element forward-mapping.",
     "The template maps 47 of the 48 source data elements from the ZPPA e-GP system into OC4IDS paths. That coverage is excellent. Report the number in the methodology section."),
    ("Lifecycle framework in section 8.2.",
     "The five-row data-source-by-stage table is a foundation for the decision summary this review asks for (section 2, revision R4 below). Expand it into the four-bucket classification: ready to publish, small format fixes, needs system work, needs policy action."),
    ("Mapping quality.",
     "Every OC4IDS path the template lists as mapped contains real source content. No placeholders. A reviewer sampling the mapping sheets can verify every line back to the ZPPA e-GP schema."),
]
for title, body in strengths:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    H.add_run(p, "+  ", bold=True, size_pt=11, color=H.LOW_TEXT)
    H.add_run(p, title + "  ", bold=True, size_pt=10.5, color=H.CHARCOAL)
    H.add_run(p, body, size_pt=10.5, color=H.CHARCOAL)

H.para(doc, "", space_after=14)

# ─── Section 2: Mapping evidence ───────────────────────────────────────────
p = doc.add_paragraph()
H.add_run(p, "2.  The mapping evidence", bold=True, size_pt=14, color=H.CHARCOAL)
H.accent_bar(doc, H.RED, width_cm=9)
H.para(doc, "", space_after=6)

H.para(doc, "The report's strongest asset is the template itself. It maps 73 OC4IDS fields across four sheets, all backed by real source paths from the ZPPA e-GP system. The headline does not yet say this. Section 4 below sets out specific changes to bring the narrative in line with the evidence.",
       size_pt=10.5, space_after=6)

H.para(doc, "Two of the four OC4IDS template sheets carry almost no Zambia data. That is the first story the executive summary should lead with.",
       size_pt=10.5, space_after=8)

H.centered_image(doc, CHARTS / "01-sheet-coverage.png", width_cm=22,
                 space_before=8, space_after=14)

# Page break for section 3
doc.add_page_break()

# ─── Section 3: Phase coverage ─────────────────────────────────────────────
p = doc.add_paragraph()
H.add_run(p, "3.  Where the gaps sit across the project lifecycle",
          bold=True, size_pt=14, color=H.CHARCOAL)
H.accent_bar(doc, H.RED, width_cm=9)
H.para(doc, "", space_after=6)

H.para(doc, "Disclosure is strong at identification and procurement. It thins out sharply across implementation and collapses entirely at maintenance and decommissioning. The report describes this in words; the revision should add the percentages.",
       size_pt=10.5, space_after=8)

H.centered_image(doc, CHARTS / "02-phase-coverage.png", width_cm=22,
                 space_before=8, space_after=10)

H.para(doc, "The report already points to the single most useful reading of this pattern: most of the missing implementation-stage data is already collected by the National Council for Construction under its statutory monitoring mandate (NCC Act 2020, s.53). In other words, this is a disclosure gap, not a data gap. Remediation is integration, not new collection. That framing should carry the report.",
       size_pt=10.5, space_after=16)

# ─── Section 4: Priority revisions ─────────────────────────────────────────
p = doc.add_paragraph()
H.add_run(p, "4.  Priority revisions requested", bold=True, size_pt=14, color=H.CHARCOAL)
H.accent_bar(doc, H.RED, width_cm=9)
H.para(doc, "", space_after=6)

H.para(doc, "Ten changes, ranked by priority. Each carries an issue, the evidence behind it, the specific revision requested, and a proposed owner. Dates are not set here; a resubmission schedule will be agreed through the MSG in the covering note.",
       size_pt=10.5, space_after=12)

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
H.set_table_full_width(rt, CONTENT_W)
H.apply_col_widths(rt, [1.2, 2.3, 5.0, 7.4, 6.2, 3.6])
H.apply_default_padding(rt)
H.styled_table_header(rt.rows[0],
                      ["Ref", "Priority", "Issue", "Evidence",
                       "Revision requested", "Proposed owner"],
                      bg="2D2D2D")

prio_map = {
    "Critical": (H.RED, H.CRITICAL_BG),
    "High": (H.BLUE, H.HIGH_BG),
    "Medium": (H.MEDIUM_TEXT, H.MEDIUM_BG),
    "Low": (H.LOW_TEXT, H.LOW_BG),
}
for ri, (ref, prio, issue, ev, rec, owner) in enumerate(revs, start=1):
    cells = rt.rows[ri].cells
    H.set_row_height(rt.rows[ri], 1.8)
    bg = H.LGRAY if ri % 2 == 0 else H.WHITE
    for c in cells:
        H.set_cell_shading(c, bg)
        H.set_cell_borders(c)
    H.add_run(cells[0].paragraphs[0], ref, bold=True, size_pt=9.5, color=H.CHARCOAL)
    pc_text, pc_bg = prio_map[prio]
    H.set_cell_shading(cells[1], pc_bg)
    H.add_run(cells[1].paragraphs[0], prio, bold=True, size_pt=9.5, color=pc_text)
    H.add_run(cells[2].paragraphs[0], issue, bold=True, size_pt=9.5, color=H.CHARCOAL)
    H.add_run(cells[3].paragraphs[0], ev, size_pt=9.5, color=H.CHARCOAL)
    H.add_run(cells[4].paragraphs[0], rec, size_pt=9.5, color=H.CHARCOAL)
    H.add_run(cells[5].paragraphs[0], owner, size_pt=9.5, color=H.CHARCOAL)

H.para(doc, "", space_after=14)

# Page break for section 5
doc.add_page_break()

# ─── Section 5: Decision summary preview ───────────────────────────────────
p = doc.add_paragraph()
H.add_run(p, "5.  What Zambia can publish now", bold=True, size_pt=14, color=H.CHARCOAL)
H.accent_bar(doc, H.RED, width_cm=9)
H.para(doc, "", space_after=6)

H.para(doc, "This is the reading this review asks for in R7 above. It is also the single table the report's primary audience (MSG members, permanent secretaries, senior officials) will read first. An indicative version, drawn from the current mapping template, appears below. The revision should produce a version reviewed by the Zambia team before publication.",
       size_pt=10.5, space_after=8)

H.centered_image(doc, CHARTS / "03-decision-buckets.png", width_cm=22,
                 space_before=8, space_after=16)

# ─── Section 6: Legal lever ────────────────────────────────────────────────
p = doc.add_paragraph()
H.add_run(p, "6.  The law already permits most of what is missing",
          bold=True, size_pt=14, color=H.CHARCOAL)
H.accent_bar(doc, H.RED, width_cm=9)
H.para(doc, "", space_after=6)

H.para(doc, "This is the point the legal framework analysis in Annex 8.1 already makes. It is worth pulling forward into the body of the report:",
       size_pt=10.5, space_after=10)

lt = doc.add_table(rows=4, cols=3)
H.set_table_full_width(lt, CONTENT_W)
H.apply_col_widths(lt, [7.0, 11.5, CONTENT_W - 18.5])
H.apply_default_padding(lt)
H.styled_table_header(lt.rows[0],
                      ["Legal authority", "What it authorises",
                       "Relevance to OC4IDS publication"],
                      bg="2D2D2D")

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
    H.set_row_height(lt.rows[ri], 1.5)
    bg = H.LGRAY if ri % 2 == 0 else H.WHITE
    for c in cells:
        H.set_cell_shading(c, bg)
        H.set_cell_borders(c)
    H.add_run(cells[0].paragraphs[0], r[0], bold=True, size_pt=10, color=H.CHARCOAL)
    H.add_run(cells[1].paragraphs[0], r[1], size_pt=10, color=H.CHARCOAL)
    H.add_run(cells[2].paragraphs[0], r[2], size_pt=10, color=H.CHARCOAL)

H.para(doc, "", space_after=14)

H.callout_box(
    doc, CONTENT_W,
    label="IMPLICATION",
    label_color=H.BLUE,
    body="Publishing most of the missing implementation data does not require new law. It requires an integration layer between ZPPA and NCC, and a short statutory instrument clarifying that the two systems share publication-relevant records. The revision should make this case in the recommendations section.",
)
H.para(doc, "", space_after=16)

# ─── Section 7: Next step ──────────────────────────────────────────────────
p = doc.add_paragraph()
H.add_run(p, "7.  Next step", bold=True, size_pt=14, color=H.CHARCOAL)
H.accent_bar(doc, H.RED, width_cm=9)
H.para(doc, "", space_after=6)

H.para(doc, "This review is a working document between CoST IS and the Zambia Technical Team. The covering note proposes a short call to walk through the ten revisions and agree a resubmission schedule with the MSG.",
       size_pt=10.5, space_after=6)

H.para(doc, "Two companion documents are attached:",
       size_pt=10.5, space_after=4)

H.para(doc, "•   02-structural-reference.docx: a short illustrative extract showing the shape and specificity a strong report carries. Use it as a pattern reference.",
       size_pt=10.5, space_after=4)

H.para(doc, "•   03-sample-final-report.docx: a fully-worked model report for Zambia. Every stakeholder name is a placeholder pending MSG consultation, but the structure, numbers, legal analysis, and recommendation logic are at the target standard. The Zambia team can adapt it directly if useful.",
       size_pt=10.5, space_after=14)

H.para(doc, "Source: Zambia OC4IDS field-level mapping template v0.9.5, accessed 2026-04-23. Zambia OC4IDS field-level mapping report (draft), 3 March 2026.",
       size_pt=9, italic=True, color=H.MUTED, space_after=0)

doc.save(str(OUT))
print(f"OK {OUT}")
