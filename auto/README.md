# Overlay Auto-Researcher

A bounded self-tuning loop for Overlay review packages. Same shape as the Notion Thinking Partner auto-improvement engine, scaled down to the surface Overlay actually has: a small number of deterministic Python builders and two docx outputs per country review.

```
  EVALUATE       DETECT           MUTATE          SANDBOX          PROMOTE          LEARN
  ┌──────┐      ┌──────┐         ┌──────┐        ┌──────┐         ┌──────┐        ┌──────┐
  │Score │─────>│Weakest│───────>│Bounded│──────>│Rebuild│────────>│Accept│───────>│Append│
  │docx  │      │ eval │         │patch │       │+score│  pass    │+log  │        │JSONL │
  └──────┘      └──────┘         └──────┘        └──┬───┘         └──────┘        └──────┘
                                                    │ fail
                                                    v
                                                 ┌──────┐
                                                 │Revert│
                                                 │+log  │
                                                 └──────┘
```

## Modules

| File | Role |
|---|---|
| `evaluators.py` | 9 deterministic evaluators, each returning a score in [0, 1] and a list of findings. |
| `weakness_detector.py` | Ranks evaluators by `(1 - score) * weight` and returns the top weakness. |
| `mutator.py` | Rule-based patch generator. Given a weakness category, proposes one bounded edit against a specific build script or rubric file. |
| `sandbox.py` | Applies a patch to a temp copy of the build tree, rebuilds the docx, re-runs evaluators. Returns the new score vector. |
| `promotion.py` | Single gate: overall score non-decreasing AND the targeted evaluator improves AND no evaluator regresses below 0.9. |
| `learning.py` | Appends every cycle to `runs/history.jsonl`. Summarises win/loss patterns. |
| `loop.py` | Orchestrator. Runs up to N cycles until all evaluators hit target OR budget exhausted. Emits `runs/latest/dashboard.md`. |

## Evaluators

All evaluators are deterministic, cheap to run, and graded 0.0 to 1.0.

| ID | What it checks | Target |
|---|---|---|
| E01 | No em or en dashes in either docx | 1.0 |
| E02 | No internal tool vocabulary (Overlay / Gate / Part A/B/C / Cxx / gate score) | 1.0 |
| E03 | No AI-tell phrases (delve, leverage, utilize, seamless, holistic, transformative...) | 1.0 |
| E04 | Both documents exist, non-empty, and open as valid docx | 1.0 |
| E05 | All R-numbers cited in the merged doc (R1 through R10) are present in the priority revisions table | 1.0 |
| E06 | No 1,480-slot denominator leads (the misleading headline) | 1.0 |
| E07 | Every chart embedded is also annotated (data-storytelling rule) | 0.9+ |
| E08 | Page count within target (merged doc 10 to 16 pages; final report 10 to 20 pages) | 0.9+ |
| E09 | Cross-doc filename references are consistent (merged mentions `02-sample-final-report.docx`) | 1.0 |

Overall score = weighted mean. Weights prioritise hard blockers (E01–E06 at 1.0, E07–E09 at 0.7).

## Mutations

The mutator only proposes patches it can safely apply without LLM calls. Each mutation is tagged with an evaluator ID and a file scope.

| Mutation class | Targets | Bounded action |
|---|---|---|
| `REPLACE_DASH` | E01 | Replace em/en dashes in source `.py` strings with commas or periods. |
| `SUB_FORBIDDEN` | E02 | Substitute internal vocabulary terms with safe alternatives from the rubric's translation table. |
| `DROP_AI_TELL` | E03 | Remove or rewrite AI-tell phrases with plainer verbs. |
| `ADD_RNUMBER` | E05 | Insert a missing R-ref citation into the priority revisions table source. |
| `REMOVE_1480` | E06 | Remove the 1,480 denominator from executive-summary strings. |
| `BUMP_PADDING` | layout | Increase cell padding constants in `_docx_helpers.py`. |
| `FIX_FILENAME_REF` | E09 | Correct filename references across build scripts. |

Every mutation is a single-file, single-hunk edit. No cross-file refactors. No API shape changes.

## Usage

```bash
cd auto
python3 loop.py                    # runs until convergence or max 8 cycles
python3 loop.py --cycles 3         # cap at 3 cycles
python3 loop.py --mode propose     # evaluate + propose, don't apply (dry run)
python3 loop.py --mode sandbox     # apply + rebuild + score, don't promote
python3 loop.py --mode promote     # full loop (default)
```

Output lives in `runs/<timestamp>/` with a copy of `dashboard.md` symlinked at `runs/latest/`.

## Philosophy

This is not a general self-healing engine. It is a narrow, bounded optimiser for a pipeline the rubric already defines success criteria for. The evaluators are the rubric in code. The mutator respects the scope contract. The sandbox never touches the real sample folder until the promotion gate passes.

If a patch cannot be generated from the rule set, the loop stops and logs the weakness for human review. No LLM call fabricates one.
