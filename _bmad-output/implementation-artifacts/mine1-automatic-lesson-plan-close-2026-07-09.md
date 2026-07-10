# Mine 1 CLOSE — Automatic Lesson_plan (2026-07-09 / 2026-07-10 UTC)

**Status:** CLOSED by party (John / Winston / Amelia / Murat) — CLOSE-with-named-fenced-residuals  
**Live run:** `runs/799db384-9b04-4436-9f34-e11608bf6385/`  
**Evidence:** `_bmad-output/implementation-artifacts/evidence/mine1-auto-selection-20260710T021943Z/automatic-lesson-plan/verdict.json`

## Claim MET

From Pass-1 `lesson_plan.collateral`, derive `ComponentSelection` without a manual intent file; fail-loud when collateral is absent/invalid; live `runs/<uuid>/` shows selection consumed by `compose_and_digest`.

## Delivered

| Piece | Path |
|---|---|
| Derive API | `app/marcus/lesson_plan/collateral_selection.py` (`derive_selection_from_lesson_plan`, `load_selection_from_lesson_plan_json`, source=`plan_collateral`) |
| Machine companion | `write_lesson_plan` → `irene-pass1.lesson-plan.json` |
| Trial CLI | `--lesson-plan-json` (precedence under ratified intent) |
| Unit | 4 new tests; suite 19 passed |
| Liveproof | `scripts/utilities/bank_mine1_auto_selection_liveproof.py` → pass |

## Fenced residuals (do not reopen Mine 1)

1. Winston: `write_lesson_plan` dual-write scope-note before multi-specialist reuse of the JSON companion.
2. Murat: field-value round-trip test before any schema-changing mine that alters lesson-plan JSON shape.
3. Explicit non-claims: Interactive REPL (Mine 2); Gamma; rewriting ratification library.

## Next

Mine 2 (Interactive SPOC) and Mine 4 (Canonical processed-source) in parallel per greenlight sequencing.
