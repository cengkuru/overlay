# OC4IDS Field-Level Mapping Report — Author Submission Checklist

**Version:** v1.0
**Audience:** Country teams preparing a field-level mapping report for CoST MSG / government review
**Purpose:** Confirm the report contains the minimum evidence a reviewer needs before submission. Items tagged `[GATE]` are enforced at the 30-minute reviewer gate check — missing any of them returns the report at triage. Items without the `[GATE]` tag are scored in the full rubric; weak performance on them does not block submission but costs points.

---

## How the checklist relates to the review

```
Submit with this checklist 100% ticked
        ↓
Reviewer runs the 10-item gate check (30 min)
        ↓ pass 10/10
Reviewer runs the full rubric (60–90 min)
        ↓
Review letter with score and revisions
```

Gate items (10 of 16) determine whether the report is reviewed at all. Full-rubric items (the other 6) determine how well it scores. Tick every box before submitting. If you cannot tick an item, explain in your cover note why it is absent.

---

## The 16 items (in report order)

### Section 1 — Executive summary and scope

- [ ] **1. Quantified headline `[GATE]`.** The executive summary states a percentage of required OC4IDS fields currently populated. Adjectives like *significant gaps* or *largely complete* do not satisfy this item.
- [ ] **2. Portal URLs and access dates `[GATE]`.** Every portal or system URL reviewed is listed with the date(s) it was accessed.
- [ ] **3. Sample defined `[GATE]`.** The project sample is characterised by count, aggregate value, sectors, time window, and sampling method.

### Section 2 — Methodology and legal anchoring

- [ ] **4. OC4IDS template version specified `[GATE]`.** The version used is stated explicitly (e.g. `0.9.5`, `0.9.6`). Mapping against a version more than one minor release behind current requires an explicit justification — otherwise it costs points in the full rubric (C3).
- [ ] **5. Procurement law and ATI/FOI law cited `[GATE]`.** Both frameworks named with section references. OGP commitments and sector rules added where relevant.

### Section 3 — Quantitative findings

- [ ] **6. Coverage percentages per lifecycle phase `[GATE]`.** Reported for identification, preparation, procurement, implementation, completion, maintenance, decommissioning.
- [ ] **7. Every required field has a status.** Each required OC4IDS field carries Populated / Partial / Missing / Not Applicable. NA entries are justified.
- [ ] **8. Source-field provenance `[GATE]`.** Every mapped OC4IDS field traces back to a named source-system field. Where no source field exists, the report states so explicitly.

### Section 4 — Diagnosis

- [ ] **9. Gap root causes `[GATE]`.** Every material gap classified by the 8-category typology: (1) no data exists, (2) outside reviewed system, (3) unstructured documents only, (4) poor quality, (5) cannot be linked, (6) collected but not disclosed, (7) blocked by workflow/legal, (8) country-context field not in template.
- [ ] **10. Data beyond OC4IDS examined.** Fields the country discloses that fall outside OC4IDS, with a recommendation on retention as extensions or upstream feedback to OCP. *Not a gate item — scored in the full rubric (C9). Skipping it costs points but does not block submission.*

### Section 5 — Data quality

- [ ] **11. Codelist alignment checked.** The report states which source-system codelists align with OC4IDS codelists directly and which need translation. *Scored in C7.*
- [ ] **12. Document URL health sampled.** A sample of document URLs tested; the percentage that resolve reported. Minimum sample: 20 documents or 10% of the set, whichever greater. *Scored in C7. If documents were explicitly out of scope, state so — C7 is then scored out of 8 rather than 10.*

### Section 6 — Action

- [ ] **13. Recommendations with named owners and timelines `[GATE]`.** Every recommendation names its owner (role plus person where possible) and gives a timeline. *"KADPPA should strengthen data collection"* fails. *"The KADPPA Director of IT will automate OC4IDS export from the e-GP system by Q3 2026"* passes.
- [ ] **14. Implementation roadmap with phasing.** Short-term (0–3 months), medium-term (3–12 months), long-term (12+ months) actions with owners and dependencies. *Scored in C11.*
- [ ] **15. Decision summary panel.** One page or boxed section classifying publishable elements as (a) can publish now, (b) can publish after light transformation, (c) requires system change, (d) requires legal or institutional action. *Scored in C11; omission costs 4 of C11's 11 points.*

### Section 7 — Evidence base

- [ ] **16. Completed mapping template attached as annex `[GATE]`.** The 6-sheet Excel workbook itself, not a summary of it.

---

## Writing discipline (applies to all sections)

A report with persistent writing-discipline failures is returned for copy-editing before review — scoring does not begin until the prose meets standard. This is an auto-return trigger, not a points deduction.

- Active voice wherever reasonable.
- No em dashes (use commas or full stops).
- Quantitative claims carry the evidence behind them.
- Adjective-only claims (*significant, notable, virtual, substantial*) are replaced with numbers or removed.
- Every finding cites a source: the template, a document, a legal reference, or an interview.

---

## What a reviewer does with a submitted report

1. **Gate check (30 min).** Work the 10 `[GATE]` items above (plus the gate-only check for the spot-sampled template rows).
   - 10 / 10 → proceed to full review.
   - 7–9 / 10 → revise and resubmit; no full scoring.
   - ≤6 / 10 → reject and rewrite.
2. **Full rubric (60–90 min).** Score 12 weighted dimensions summing to 100 points.
3. **Review letter.** Decision, section scores, top revisions, resubmission target date.

Gate score 2 / 10 is the published floor (Kaduna calibration). If you are below 6 / 10 on the gate items in this checklist before submitting, revise before you send.

---

## References

- OC4IDS 0.9.5 Field-Level Mapping Template — the Excel workbook this report translates.
- OCP OC4IDS documentation: `https://standard.open-contracting.org/infrastructure/latest/en/`
- CoST Infrastructure Data Standard (IDS) — overlay mapping on the template's `(CoST) IDS Elements` sheet.
- Overlay reviewer gate check (`reviewer-gate-check.md`) and full rubric (`full-rubric.md`).
