# Overlay

**A reviewer's lens for OC4IDS field-level mapping reports.**

Overlay is a framework — and, in a later phase, a tool — for reviewing the reports CoST members produce after completing the OC4IDS Field-Level Mapping Template. Its job is to make sure those reports reveal the implementation reality of a country's disclosure system, not just narrate compliance with the standard.

## How the pieces fit

```
Author checklist   →   Reviewer gate check   →   Full rubric   →   Review letter
(before submission)    (30-min triage)           (60–90 min)       (decision + revisions)
```

- **Author checklist** (Part A) — 16-item submission hygiene list country teams work through before submitting.
- **Reviewer gate check** (Part B) — 10 brutal go/no-go items; passing is the entry ticket to full review.
- **Full rubric** (Part C) — weighted 100-point evaluation applied only after the gate passes.
- **Review letter** — the reviewer's written decision with section scores and top revisions requested.

## Status

**Phase 1 — Rubric** *(current)*. The three artefacts above. The author checklist and gate check ship at v1.0; the full rubric ships at v0.9 and reaches v1.0 after calibration across three scored reports (Kaduna + Zambia + Ghana/Uganda).

**Phase 2 — Tool** *(planned, scope-limited)*. A deterministic generator that ingests the completed mapping template Excel and emits the *mechanical* sections of a draft report:

- C0 quantitative backbone (coverage counts, percentages, zero-coverage flags, forward-map counts).
- C5 phase-level summary tables.
- Annex matrix with field-level status.
- Codelist conformance checks against OC4IDS codelists.

The **interpretive** sections — executive summary verdict, gap root causes (C6), legal alignment (C8), recommendations (C10), decision summary panel (C11) — are left blank for the author to write. These require human judgment about institutional context and political feasibility; automating them would hollow out the exercise. The tool is a report-starter, not a report-writer.

**Phase 3 — Calibration** *(planned)*. Score Zambia, then Ghana or Uganda, using the rubric. Set the 100-point band cutoffs from the observed distribution. Publish as v1.0. Measure inter-reviewer variance on at least one report.

## Why this exists

CoST members produce mapping reports without a shared quality standard. A report can read cleanly on the surface while the underlying template is under-filled. The Kaduna sample scores 2/10 on the gate check and ~19/100 on the full rubric — not because the prose is bad, but because the evidence layer was never forced into view.

Overlay's job is to force that layer into view. Phase 1 does it through a rubric and a reviewer discipline. Phase 2 adds a tool that does the mechanical extraction automatically so reviewers and authors can focus on judgment.

## Governing philosophy

The report must not merely describe the standard. It must reveal the implementation reality.

A weak rubric asks: *"Did they talk about OC4IDS properly?"*
A strong rubric asks: *"Did this report surface what the country can actually publish, why it cannot publish the rest, and what must change next?"*

## Contents

```
overlay/
├── README.md
├── .gitignore
└── rubric/
    ├── author-checklist.md       # Part A — 16-item submission checklist (v1.0)
    ├── reviewer-gate-check.md    # Part B — 10-item 30-min triage (v1.0)
    └── full-rubric.md            # Part C — weighted 100-point rubric (v0.9)
```

Later phases add `cli/`, `samples/`, `calibration/`.

## Owner and cadence

CoST IS Open Data Specialist function. Revision cadence: after every third country application, or annually — whichever comes first.
