# OC4IDS Field-Level Mapping Report — Full Reviewer Rubric

**Version:** v0.9 (awaiting calibration across ≥3 reports before v1.0)
**Owner:** CoST IS Open Data Specialist function
**Revision cadence:** after every third country application, or annually — whichever comes first
**Applied:** only after the Reviewer Gate Check (Part B) passes 10 / 10

---

## Governing philosophy

The report must not merely describe the standard. It must reveal the implementation reality.

A weak rubric asks: *"Did they talk about OC4IDS properly?"*
A strong rubric asks: *"Did this report surface what the country can actually publish, why it cannot publish the rest, and what must change next?"*

Four reviewer questions the report must let a reader answer:

1. What does the source system publish today and where does each field originate?
2. What does OC4IDS require and what is the quantified gap?
3. Why do the gaps exist?
4. What changes, by when, and who owns each change?

---

## Audience discipline (standing)

The rubric has two audiences: the CoST IS reviewer (internal) and the country member team (external). The vocabulary does not cross.

**Member-facing outputs** (review letter, sample structural reference, covering email, any document a country team receives) must not contain:

- the name *Overlay*, or any rubric-part label (*Part A / B / C*), section code (*C0 through C11*), or gate scorecard language.
- pass/fail scores (*gate score 3 / 10*), procedural phrases (*reviewer gate check*, *full rubric*), or other tool-persona artefacts.
- resubmission dates set unilaterally by the reviewer. Any deadline is agreed through MSG consultation and appears in the covering email, not in the body of the review document.

Permitted credibility anchor: a single opening sentence of the form *"This review applies CoST IS's OC4IDS mapping review methodology."* No version numbers, no internal codes.

Internal language translates into plain operational terms for members:

| Internal | Member-facing |
|---|---|
| *Type-6 gap* | *This data already exists but is not yet publicly disclosed* |
| *Source-field provenance* | *Which system field each OC4IDS field comes from* |
| *Decision summary panel (C11)* | *What the country can publish now, and what needs to change* |
| *Lifecycle framework* | *Where the data sits across the project lifecycle* |
| *Overlay gate item 9 fails* | *No owner or timeline on any recommendation* |

**Reviewer voice.** First-person *"CoST IS"*, not *"Overlay"* or *"we the tool"*. Comparative praise without reference data (e.g. *"the strongest we have seen"*) is either quantified or removed.

**Member-facing date format.** Body prose uses natural English (*"23 April 2026"*). ISO (*"2026-04-23"*) is permitted only in metadata tables and source footers.

---

## Dual-output rule (standing)

Every Overlay review produces **two documents**, not one:

1. **Review and structural reference** (`01-review-and-reference.docx`). Portrait A4. Pairs CoST IS feedback with worked examples, section by section. Every finding (REVIEW NOTE, CoST Red) sits next to the pattern the revised section should follow (EXAMPLE, CoST Blue). The full list of priority revisions (R1 to R10) appears once, in the recommendations section. One document, one reading order.
2. **Sample final report** (`02-sample-final-report.docx`). Portrait A4. A fully-worked model report for the reviewed country. The structure, numbers, legal analysis, and recommendation logic are set at the level a CoST IS reviewer would accept on publication. Every stakeholder name appears in square brackets as a placeholder pending MSG consultation. The country team can adapt it directly.

A review without a worked model is half the deliverable. Country teams who only receive a list of problems interpret them inconsistently and resubmit with new problems; the revision loop becomes the bottleneck. A worked example of the target state shortens the loop by showing, not telling.

Both documents are CoST-branded Word documents produced with the `cost-document-design`, `communication-guide`, `cost-publication-assurance`, and `data-storytelling` skills. Both use the Activity Report archetype (Full Publication intensity, portrait A4).

Both documents must appear in `samples/<country>-<yyyy-mm>/` inside this repository as the audit trail.

---

## Scored dimensions (sum = 100)

Hard-gate items (already enforced by Part B) are listed where relevant but are not re-scored here.

### C0. Quantitative Mapping Backbone — 12 pts *(the chassis)*

The heaviest and most testable section. Without this section scoring at least **8 / 12**, the rest of the rubric is upholstery on a bad chassis.

**Denominator discipline.** The total OC4IDS template (approximately 1,480 slots across the four OC4IDS sheets) is a *universe*, not an obligation. OC4IDS contains required, recommended, optional, and sector-specific fields. A country doing everything right on every *relevant* field will still populate only 30–40% of the template universe because the rest legitimately does not apply. Leading a report with *"4.9% of 1,480 slots mapped"* sets a false deficit and misrepresents the publisher's standing. Use the denominators below instead.

**Required (the three denominators, in this order):**

1. **Required-fields gate.** Count of OC4IDS fields marked `required` in the v0.9.5 schema that the publisher populated. Report as a pass/fail line: *all required fields populated: yes / no*. This is the legal floor. The set is small (roughly 8–12 fields across all four sheets) and any strong publisher clears it trivially.
2. **Applicable-coverage rate.** Count of required + recommended fields applicable to the publisher's declared scope that are populated. The template's NA classifications produce this denominator directly: subtract NA-justified entries from the universe, then report the populated subset. This is the **scored denominator** — the one a reader sees first. It is what the OC4IDS Data Review Tool treats as the real floor.
3. **Absolute publishable-field count.** The count of fields currently publishable, decomposed into the decision-panel categories: *ready to publish* / *small format fixes* / *needs system work* / *needs policy action*. Drives the decision summary in C11.

**Supplementary (annex only):**

- Total-template figure (fields populated out of the ~1,480 universe) — permitted as a benchmarking datapoint for cross-country comparison, reported once in the annex, never in the executive summary or headline blocks.

**Also required in this section:**

- Per-sheet coverage across all four OC4IDS sheets: Projects, Contracting Processes, Linked Releases, Parties — expressed against the applicable denominator per sheet, not the total slot count.
- Zero-coverage sheets explicitly highlighted: silent zeros are a failure.
- Count of source data elements forward-mapped to OC4IDS (from `(Source) 2. Data elements`).
- Count of mapped fields validated with real example content (not placeholder).

| Score | Meaning |
|---:|---|
| 10–12 | All three denominators stated in order; per-sheet coverage; zero-sheets named; forward-map + validated counts present. |
| 6–9 | Two of three denominators + per-sheet coverage. Total-universe still used in headline: cap at 7. |
| 3–5 | One denominator only, or total-universe used as the lead figure. |
| 0–2 | Coverage numbers absent or unverifiable against the template. |

### C1. Executive summary clarity — 6 pts

Required: decision verdict, top 3–5 strengths, top 3–5 gaps, headline recommendation, plain-language summary, publisher named.

Red flags: generic summary; restates methodology instead of conclusions; no distinction between "can publish now" and "cannot publish now".

### C2. Scope and systems coverage — 6 pts

Required: legal mandate authorising disclosure, source systems enumerated (e-GP, PPDB, manual entry, parallel systems), back-office vs portal reviewed, stakeholders consulted, mapping team named, limitations stated.

### C3. Methodology and reproducibility — 7 pts

Required: evaluation criteria defined (Populated / Partial / Missing / NA), sample size and selection method, verification against actual records or API responses (not just schema), legal alignment test method, gap classification method.

Reproducibility standard: a second reviewer running the same template against the same system reaches the same results.

**Version-drift penalty:** reports mapped against an OC4IDS version more than one minor release behind current must include an explicit justification (e.g. *"chosen to align with existing in-country mapping work from 2024"*). Mapping against an older version without justification costs **−2 pts** in this section. The reviewer records the standard version used and flags any fields the publisher mapped against a deprecated path.

### C4. System landscape and data source inventory — 8 pts

Required minimum table:

| Source | Owner | Lifecycle stages covered | Format/access | Public? | Reliable? | Key issue |

Plus: source-of-truth explicitly identified when multiple systems hold overlapping data.

### C5. Field-level findings by lifecycle stage — 14 pts *(the heart)*

Seven stages covered: identification, preparation, procurement, implementation, completion, maintenance, decommissioning, plus cross-cutting sustainability.

For each stage:

- Fields available / partial / absent.
- Where data sits.
- Structured vs document-only.
- Public vs internal.
- Reliable for publication (yes / conditional / no).

**Report structure rule:**

- Phase-level summary tables in the **main body**: one row per phase with percentages, dominant gap type, 3 representative examples.
- Full field-level matrix in the **annex**. A complete matrix runs 200+ rows and cannot sit in the narrative body.

**Zero-coverage rule (phase level):** any phase with 0% coverage or only one field populated must be flagged explicitly with its own root-cause analysis. Such phases cannot be grouped with low-coverage phases under generic labels like *"other stages are weak"*. C0 requires this at sheet level; C5 re-states it at phase level so it cannot be buried. Kaduna's `Maintenance` and `Decommissioning` phases are the worked example — both at zero, both silently absorbed into the general "post-completion" narrative in the original report.

Reports that put everything in the body are penalised for readability; reports that omit the annex matrix fail C5 outright.

### C6. Gap typology and root cause — 8 pts

Each material gap classified using the 8-category typology:

1. No data exists.
2. Data exists but not in the reviewed system.
3. Data exists but only in unstructured documents.
4. Data exists but is poor quality.
5. Data exists but cannot yet be linked across systems.
6. Data exists but is not publicly disclosed.
7. Data cannot be captured because of workflow or legal constraints.
8. Field not in template/system but relevant for country context.

Plus each gap carries:

- Severity rating.
- Use-case impact: which oversight function or citizen query the gap blocks.

Gaps described only as schema non-compliance are penalised. *"This blocks single-bidder detection during implementation"* is what strong analysis looks like.

### C7. Data quality and usability — 10 pts

Must assess:

- Completeness.
- Consistency across records.
- Timeliness (freshness of the most recent record; age of the oldest).
- Uniqueness / duplication risk.
- Identifier schemes: OCID prefix registered with OCP, organisation identifier scheme, party identifier scheme.
- Referential integrity across project, contracting process, parties.
- Codelist conformity: which source codelists align with OC4IDS directly, which need translation.
- Date and amount formats.
- Document URL health: sample ≥20 or ≥10% of document set, whichever greater, report the resolve rate.
- Granularity for analysis and oversight.

### C8. Legal, policy and institutional alignment — 8 pts

Required:

- Procurement law with section references.
- FOI / ATI framework.
- OGP commitments relevant to infrastructure.
- Sector-specific rules where applicable.
- Institutional roles: who owns what data, who approves publication.
- Publication bottlenecks.
- Which OC4IDS fields the law already mandates vs which are voluntary.
- Conflicts between national law and OC4IDS flagged explicitly.

This is the single biggest blind spot across country reports and the strongest lever for implementation. Officials move faster when a legal obligation is documented.

### C9. Country-specific / non-template fields — 8 pts

Required:

- Fields currently disclosed that do not map to OC4IDS.
- Whether they should be retained as extensions.
- Whether they reflect local law, local practice, political priorities, or sector-specific needs.
- Recommendation on preserve / transform / propose as schema extension.

Upstream-feedback principle: country work feeds back to OCP and OC4IDS standard maintenance. A report that treats the standard as closed to input loses points here.

### C10. Recommendations — 12 pts

Stratified into four layers:

1. Immediate no-regret fixes (mapping clarifications, naming, document links, missing required fields already available).
2. System / configuration changes (new forms, new tables, API changes, workflow tweaks).
3. Institutional / process changes (ownership, data-entry SOPs, publication approvals).
4. Policy / legal changes (rules, mandates, inter-agency data sharing, formal publication requirements).

Each recommendation must carry:

- **Recommendation ID** (R1, R2, …) — stable identifier used for cross-referencing from C11's roadmap.
- Problem addressed (cross-referenced to a specific finding).
- Proposed fix.
- Named owner (role + person where possible).
- Effort level.
- Dependency.
- Priority.
- Timeline.
- Expected outcome.

### C11. Implementation roadmap and decision summary — 11 pts

**Roadmap** — short (0–3 mo), medium (3–12 mo), long (12+ mo) phasing with owners, dependencies, quick wins, risks, order-of-magnitude budgets.

Minimum table:

| Ref | Priority | Action | Owner | Dependency | Timeline | Output |

`Ref` points to the C10 recommendation ID (R1, R2, …) the roadmap action implements. Every roadmap row must reference at least one recommendation, or state the row as *emergent* with justification. This keeps the roadmap from drifting away from the diagnosis.

**Decision summary panel** *(mandatory; failure = −4 pts)* — one page or boxed section classifying publishable elements as:

| Bucket | What goes here |
|---|---|
| (a) Can publish now | Fields already mapped, with source, with data, legally clear |
| (b) Can publish after light transformation | Mapping clarifications, format conversions, naming fixes |
| (c) Requires system change | New tables, API extensions, workflow changes |
| (d) Requires legal or institutional action | Rule changes, mandates, inter-agency agreements |

This is the steering document for government and MSG audiences. It turns a 20-page review into a one-page decision.

---

## Review trail *(not separately scored; docked from C1 and C3 if missing)*

Each report lists: who reviewed, what version, what changed after review, unresolved disagreements, sign-off status. Report with no review trail loses up to 3 pts distributed across C1 and C3.

---

## Cross-cutting quality criteria

Failure on any one of these can dock **up to 3 pts** from the most relevant scored section:

- **Provenance.** Every OC4IDS field maps back to a named source-system field, or explicitly states none exists.
- **Evidence tiering.** Tier 1 claims (coverage, quality) cite quantitative evidence from the template or system. Tier 2 claims (process, workflow, legal) cite documentary or interview evidence. Tier 3 claims (synthesis) reference prior findings.
- **Reproducibility.** A second reviewer can re-derive C0's numbers from the template alone.
- **Use-case orientation.** Gaps described by the oversight function they block, not just schema compliance.

---

## Writing discipline *(auto-return trigger)*

Active voice, no em dashes, no filler. Enforced as a CoST publication-assurance standard separate from scoring.

A report that passes the gate but fails writing discipline is returned for copy-editing **before** full scoring. Writing is not a 1-point scorecard item — it is either publication-ready or it is not.

Specifically: persistent use of adjective-only claims (*significant, notable, virtual, substantial*) where numbers are available is a writing-discipline failure.

---

## Rating bands (v0.9 — provisional)

Band boundaries cannot be set from one data point. Sequence to set them:

1. Score Zambia using this rubric.
2. Score Ghana or Uganda using this rubric.
3. With three scored reports (Kaduna + 2 others) spanning weak / middling / strong, set bands from the observed distribution.
4. Mark this document as v1.0.

**Provisional bands** (the 55 cutoff is a guess until three reports are scored):

- **85–100** — strong decision document; ready for circulation with light edits.
- **70–84** — solid but incomplete; useful, missing implementation or evidence depth.
- **55–69** — technically informative, weak for decision-making.
- **Below 55** — not review-ready.

### Minimum inter-reviewer agreement

Two reviewers scoring the same report should fall within **10 points** of each other. Variance >15 points means the rubric is not ready for that context — clarify the disputed sections before continuing.

---

## Worked example — Kaduna (calibration floor; estimated scores)

The Kaduna report fails the gate at 2 / 10 and would not in production reach full scoring. The estimate below exists only to calibrate the 100-point scale.

| Section | Weight | Est. | Justification |
|---|---:|---:|---|
| C0. Quantitative backbone | 12 | 0 | No coverage numbers disclosed |
| C1. Exec summary | 6 | 2 | Narrative competent; no verdict |
| C2. Scope | 6 | 2 | Publisher named; no systems inventoried |
| C3. Methodology | 7 | 3 | Generic method; no reproducibility clause |
| C4. System landscape | 8 | 1 | Portal mentioned; no source systems |
| C5. Findings by stage | 14 | 4 | Phase table exists; no per-stage percentages |
| C6. Gap typology | 8 | 1 | No typology applied |
| C7. Data quality | 10 | 2 | Quality mentioned; no measures |
| C8. Legal alignment | 8 | 0 | Absent |
| C9. Non-template fields | 8 | 0 | Not examined |
| C10. Recommendations | 12 | 3 | Themes without owners |
| C11. Roadmap + decision summary | 11 | 1 | No roadmap; no decision panel |
| **Total** | **100** | **~19** | Below 55 |

Writing-discipline assessment: **partial**. Prose is clean but contains *"significant gaps exist"*, *"notable lack of completeness"*, *"virtual absence"* — the adjective-only claims the rubric penalises. Return for copy-editing before any future review.

---

## 60–90-minute full-review flow

| Time | Step |
|---:|---|
| 10 min | Re-open the template; re-verify C0 numbers against the report's claims. |
| 35–45 min | Score the 12 dimensions (C0–C11). Note evidence for each score. |
| 10 min | Write section-by-section comments. |
| 5–15 min | Compose the review letter: overall score, band, top three revisions requested. |
| Optional 15 min | Co-draft the decision summary panel with the author if the report is otherwise strong but C11's decision panel is weak. |

This is **review time**, not triage time. The 30-minute flow in the gate check is for go/no-go decisions — a full review needs its own hour.

---

## Review letter template

**Document ordering (member-facing).** Verdict → What is working → Priority revisions → Next step. Lead with what the country got right. This softens the critical middle without compromising diagnostic rigour and avoids the review reading as a demolition job.

**The covering email is the only member-facing communication that may contain a resubmission date.** The date is set after MSG consultation, not by the reviewer alone. Internal scoring (the 100-point rubric) is retained in reviewer records and never shown to members.

**Internal record template (reviewer's file, not sent to the member):**

```
Subject: OC4IDS Field-Level Mapping Report — Full Review: [country]

Internal record: not distributed to the country team.

Reviewer: [name]
Review date: [ISO]

Overall score: [X] / 100.
Band: [85–100 strong / 70–84 solid / 55–69 informative / <55 not review-ready].

Section scores:
- C0. Quantitative Mapping Backbone: [x / 12]
- C1. Executive summary: [x / 6]
- C2. Scope and systems: [x / 6]
- C3. Methodology: [x / 7]
- C4. System landscape: [x / 8]
- C5. Findings by stage: [x / 14]
- C6. Gap typology: [x / 8]
- C7. Data quality: [x / 10]
- C8. Legal alignment: [x / 8]
- C9. Non-template fields: [x / 8]
- C10. Recommendations: [x / 12]
- C11. Roadmap + decision summary: [x / 11]

Top three revisions requested:
1. [section]: [specific change]
2. [section]: [specific change]
3. [section]: [specific change]

Resubmission target: [date — typically 4 to 6 weeks from the date of this letter].

Detailed comments per section are attached.

Best,
[reviewer]
```

Setting an explicit resubmission target prevents revision cycles from drifting — CoST IS has seen enough programmes lose momentum at this step.

---

## What this rubric explicitly does not do

- Does not replace the completed mapping template.
- Does not score technical conformance to the OC4IDS JSON schema (that is the Data Review Tool's job).
- Does not evaluate political feasibility of recommendations.
- Does not substitute for direct engagement with the publishing authority during mapping.

---

## Related artefacts

- **Part A — Author Submission Checklist** (`author-checklist.md`) — distribute to country teams before submission.
- **Part B — Reviewer Gate Check** (`reviewer-gate-check.md`) — 30-minute triage that gates this full review.
- **Part D — Calibration Guide** (to be produced after three reports scored).
- **Part E — Feedback Template** (optional).
