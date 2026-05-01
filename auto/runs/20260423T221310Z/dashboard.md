# Overlay auto-researcher run

**Package:** fixture-country
**When:** 2026-04-23T22:13:10+00:00
**Cycles:** 1
**Overall score:** 0.8682 → **0.8682**
**Target:** 0.97

## Initial scores

| Eval | Score | Weight |
|---|---:|---:|
| E01_no_dashes | 1.000 | 1.0 |
| E02_no_internal_vocab | 1.000 | 1.0 |
| E03_no_ai_tells | 0.850 | 1.0 |
| E04_docs_valid | 1.000 | 1.0 |
| E06_no_1480_lead | 0.900 | 1.0 |
| E07_chart_annotations | 0.000 | 0.7 |
| E08_page_length | 1.000 | 0.5 |
| E09_filename_refs | 1.000 | 1.0 |
| E10_assurance_gate | 1.000 | 1.0 |
| E11_counts_reconcile | 0.500 | 1.0 |
| E12_phase_reconcile | 1.000 | 0.8 |
| E13_rec_ids | 1.000 | 1.0 |

## Cycle log

### Cycle 1 — REJECTED

- Targeted evaluator: `E03_no_ai_tells`
- Mutation class: `DROP_AI_TELL`
- Patch: Replace 1 AI-tell phrase(s)
- Touched: build/build_fixture_doc.py
- Result: sandbox: 0.8682 → 0.8818

## Final scores

| Eval | Score | Weight |
|---|---:|---:|
| E01_no_dashes | 1.000 | 1.0 |
| E02_no_internal_vocab | 1.000 | 1.0 |
| E03_no_ai_tells | 0.850 | 1.0 |
| E04_docs_valid | 1.000 | 1.0 |
| E06_no_1480_lead | 0.900 | 1.0 |
| E07_chart_annotations | 0.000 | 0.7 |
| E08_page_length | 1.000 | 0.5 |
| E09_filename_refs | 1.000 | 1.0 |
| E10_assurance_gate | 1.000 | 1.0 |
| E11_counts_reconcile | 0.500 | 1.0 |
| E12_phase_reconcile | 1.000 | 0.8 |
| E13_rec_ids | 1.000 | 1.0 |
