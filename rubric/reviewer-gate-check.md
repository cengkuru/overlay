# OC4IDS Field-Level Mapping Report — Reviewer Gate Check

**Version:** v1.0
**Audience:** CoST IS reviewer, MSG focal point
**Purpose:** 30-minute go/no-go triage on an incoming mapping report. Only reports that pass this gate receive a full weighted review.

---

## 30-minute flow

| Time | Step |
|---:|---|
| 5 min | Open the mapping template Excel first. Compute per-sheet percentages and the forward-map count. These are ground truth. |
| 15 min | Work the 10-item gate check against the narrative. Score each pass/fail — no partial credit. |
| 5 min | Spot-sample 5 random mapped rows (is the Mapping + Example substantive?) and 5 random unmapped rows (is the omission justified in Notes?). |
| 5 min | Write the gate-decision email. |

The point of opening the template first: the template is the x-ray, the report is the skin. Skin reads can fool you.

---

## The 10 gate items

Score each **1** (clearly present and adequate) or **0** (missing, placeholder, or inadequate). No partial credit.

| # | Gate item | Where to look | Pass if… |
|---|---|---|---|
| 1 | Quantified headline finding | Executive summary | A percentage of required OC4IDS fields populated is stated. Adjectives alone (*significant, mostly*) fail. |
| 2 | Portal/system URLs and access dates | Scope section | Every URL reviewed is listed with the date accessed. |
| 3 | OC4IDS template version | Methodology | Version number stated (e.g. `0.9.5`). |
| 4 | Sample defined | Scope / methodology | Project count, aggregate value, sectors, time window, sampling method all present. |
| 5 | Coverage percentages by phase | Findings | Percentages reported per lifecycle phase (identification → decommissioning). |
| 6 | Source-field provenance | Findings / annex | Every mapped field is traced to a named source-system field, or stated as having no source. |
| 7 | Gap root causes (typology applied) | Gap analysis | Each material gap classified by the 8-category typology — not just labelled "missing". |
| 8 | Procurement law and FOI both cited with section refs | Legal alignment | Both frameworks named with section numbers. OGP / sector rules where relevant. |
| 9 | Recommendations with named owners and timelines | Recommendations | Every recommendation carries an owner (role + person where possible) and a timeline. |
| 10 | Completed mapping template attached | Annexes | The 6-sheet Excel workbook is attached. Not a summary — the workbook. |

---

## Spot-sample (teeth of the gate)

Use 5 minutes to randomly sample from the `(OC4IDS) Projects`, `(OC4IDS) Contracting Processes`, `(OC4IDS) Linked Releases`, and `(OC4IDS) Parties` sheets.

- **5 mapped rows (rows with content in the `Mapping` column):** do the `Mapping` and `Example` cells contain substantive content, or placeholders, URLs-with-no-field-names, or copy-pasted template text?
- **5 unmapped rows:** is the omission justified in `Notes`? An empty `Notes` on an unmapped row is a silent gap.

**Spot-sample rule:** if ≥2 of 5 mapped rows are placeholders, the report drops one grade band on the full rubric. If ≥2 of 5 unmapped rows have no justification, flag as a writing-discipline failure.

---

## Gate decision

| Score | Decision | Action |
|---:|---|---|
| 10 / 10 | **Pass** | Proceed to Part C full review (60–90 min). |
| 7–9 / 10 | **Revise and resubmit** | Write a comment letter listing the failed items. Do not score the full rubric until the gate is passed. |
| ≤6 / 10 | **Reject and rewrite** | Report is not review-ready. Return with the gate scoresheet. |

### Scope-of-authority disclaimer

These decisions apply to **member programmes** where CoST IS has assurance authority. In **advisory or non-member contexts**, substitute *"strongly recommend revision"* for *"reject"*, and route the decision through the COO. Do not write a rejection letter your organisation cannot back.

---

## Gate-decision email template

Copy this into your reply:

```
Subject: OC4IDS Field-Level Mapping Report — Gate check result: [PASS / REVISE / REJECT]

Dear [author],

I have completed a 30-minute gate-check review of the [country] OC4IDS
field-level mapping report submitted on [date].

Gate score: [X] / 10.

Decision: [PASS / REVISE AND RESUBMIT / REJECT AND REWRITE].

Items requiring attention before resubmission:
- Gate [N]: [one-line description of what is missing and where in the
  report/annex it should appear]
- Gate [N]: [...]

[Optional — one paragraph on spot-sample findings.]

Reference: CoST Reviewer Gate Check v1.0.

Best,
[reviewer]
```

---

## Worked example — Kaduna (calibration floor)

| # | Item | Kaduna | Note |
|---|---|---|---|
| 1 | Quantified headline | ✗ | *"Significant gaps exist"* |
| 2 | Portal URL + dates | ✗ | Absent |
| 3 | Template version | ✓ | *"0.9.5"* stated |
| 4 | Sample defined | ✗ | No project count |
| 5 | Coverage % by phase | ✗ | Phase annex is qualitative only |
| 6 | Source-field provenance | ✗ | 17 of 201 source elements forward-mapped, undisclosed |
| 7 | Gap root causes | ✗ | Described as *"missing"* only |
| 8 | Procurement law + FOI | ✗ | Neither cited |
| 9 | Recommendations with owners/timelines | ✗ | All directional themes |
| 10 | Template annexed | ✓ | Attached but severely under-filled |

**Gate score: 2 / 10 → Reject and rewrite.**

Use this as the calibration floor. Anything scoring at or below 2 is unambiguously not review-ready regardless of prose quality.

---

## Related artefacts

- **Part A — Author Submission Checklist** (`author-checklist.md`) — send this to country teams before they submit. Reduces gate failures at source.
- **Part C — Full Reviewer Rubric** (`full-rubric.md`) — applied only after the gate passes.
