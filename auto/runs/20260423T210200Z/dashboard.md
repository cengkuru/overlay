# Overlay Auto-Researcher Run

**When:** 2026-04-23T21:02:09Z
**Cycles:** 2
**Overall score:** 0.8810 → **1.0000**
**Target:** 0.97

## Initial scores

| Eval | Score | Weight |
|---|---:|---:|
| E01_no_dashes | 0.000 | 1.0 |
| E02_no_internal_vocab | 1.000 | 1.0 |
| E03_no_ai_tells | 1.000 | 1.0 |
| E04_docs_valid | 1.000 | 1.0 |
| E05_r_ref_integrity | 1.000 | 1.0 |
| E06_no_1480_lead | 1.000 | 1.0 |
| E07_chart_annotations | 1.000 | 0.7 |
| E08_page_length | 1.000 | 0.7 |
| E09_filename_refs | 1.000 | 1.0 |

## Cycle log

### Cycle 1 — REJECTED

- Targeted evaluator: `E01_no_dashes`
- Mutation class: `REPLACE_DASH`
- Patch: Replace em/en dashes in 2 script(s)
- Result: E06_no_1480_lead regressed below 0.9 (1.000 → 0.400)

### Cycle 2 — ACCEPTED

- Targeted evaluator: `E06_no_1480_lead`
- Mutation class: `REMOVE_1480`
- Patch: Remove '1,480' denominator from build strings
- Result: overall 0.9286 → 1.0000, E06_no_1480_lead 0.400 → 1.000

## Final scores

| Eval | Score | Weight |
|---|---:|---:|
| E01_no_dashes | 1.000 | 1.0 |
| E02_no_internal_vocab | 1.000 | 1.0 |
| E03_no_ai_tells | 1.000 | 1.0 |
| E04_docs_valid | 1.000 | 1.0 |
| E05_r_ref_integrity | 1.000 | 1.0 |
| E06_no_1480_lead | 1.000 | 1.0 |
| E07_chart_annotations | 1.000 | 0.7 |
| E08_page_length | 1.000 | 0.7 |
| E09_filename_refs | 1.000 | 1.0 |
