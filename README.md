# Overlay

**A reviewer's lens for OC4IDS field-level mapping reports.**

Overlay turns a completed OC4IDS Field-Level Mapping Template (the 6-sheet Excel workbook) into a draft review report, so members can publish mapping findings that stand up to evidence scrutiny instead of narrative bluff.

## Status

**Phase 1 — Rubric** *(current)*. The reviewer rubric ships first: a three-part framework (author checklist, reviewer gate check, full weighted rubric) that defines what a good mapping report must contain and how to grade it in 30 or 90 minutes.

**Phase 2 — Tool** *(planned)*. A CLI / web app that ingests the completed mapping template and emits a draft narrative report with rubric-compliant sections pre-filled from the template's evidence — coverage percentages, per-sheet gap tables, zero-coverage alerts, forward-mapping counts, codelist mismatches — leaving context-specific sections (legal alignment, institutional roles, recommendations) for the author to customise.

**Phase 3 — Calibration** *(planned)*. Score Zambia + Ghana/Uganda using the rubric, set the 100-point band cutoffs from the observed distribution, publish as v1.0.

## Why this exists

CoST members produce mapping reports without a shared quality standard. A report can read cleanly on the surface while the underlying template is under-filled. The Kaduna sample scores 2/10 on the gate check and ~19/100 on the full rubric — not because the prose is bad, but because the evidence layer was never forced into view.

Overlay's job is to force that layer into view automatically. The reviewer keeps judgment over legal interpretation, political feasibility, and narrative framing. The tool handles coverage counting, provenance tracing, zero-coverage detection, codelist conformance, document URL health, and the decision-summary classification.

## Contents

- `rubric/` — the three artefacts shipping now.
  - `author-checklist.md` — 16-item submission checklist for country teams (Part A, v1.0).
  - `reviewer-gate-check.md` — 10-item 30-minute triage card (Part B, v1.0).
  - `full-rubric.md` — weighted 100-point reviewer rubric (Part C, v0.9 pending calibration).

Later phases will add `cli/`, `samples/`, and `calibration/`.

## Governing philosophy

The report must not merely describe the standard. It must reveal the implementation reality.

A weak rubric asks: *"Did they talk about OC4IDS properly?"*
A strong rubric asks: *"Did this report surface what the country can actually publish, why it cannot publish the rest, and what must change next?"*

## Owner

CoST IS Open Data Specialist function. Revision cadence: after every third country application, or annually.
