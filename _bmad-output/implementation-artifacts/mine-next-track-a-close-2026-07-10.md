# Mine-next Track A — CLOSE (2026-07-10)

**Status:** Track A CLOSED 4/4 (John / Winston / Amelia / Murat) — HOLD B/C/D  
**Branch:** `dev/lesson-planning-2026-07-09`  
**Greenlight:** `mine-next-greenlight-2026-07-10.md`  
**Goal:** `goal-mine-next-completion-lanes-2026-07-10.txt`

---

## Operator ALERTS (still binding)

1. **Real HAI/PHS content required** before N1 / N4-complete / N5. Track B+C = **HOLD**.
2. **Batch LLM (N7)** — no silent GO; interactive operator dialogue after N5 E2E.
3. **Live E2E before Batch** — N5-class full SPOC terminal proof still ahead (after media).

---

## Track A results

| Lane | Claim | Evidence | Verdict |
|------|-------|----------|---------|
| **N6** | `run-envelope-corrupt-vs-absent-fail-loud` — corrupt raises `RunEnvelopeCorruptError`; absent → `None` | `mine-next-n6-corrupt-envelope-20260710T030017Z/` · run `aafed561…` | PASS |
| **N3** | Independent `deck-companion-quiz` projector (schema + enrichment + Markdown); empty refused | `mine-next-n3-quiz-projector-20260710T030020Z/` · run `7f61de61…` | PASS |
| **N2** | SPOC `--plan-dialogue` owns LO + workflow ratification (no 2B memory OS) | `mine-next-n2-spoc-plan-dialogue-20260710T030023Z/` · run `71dcecbb…` | PASS |

### Unit tests
`tests/marcus/lesson_plan/test_quiz_projector.py`  
`tests/marcus/lesson_plan/test_run_envelope_corrupt_fail_loud.py`  
`tests/unit/marcus/cli/test_marcus_spoc_plan_dialogue.py`  
→ **12 passed**

### Key paths
- `app/marcus/lesson_plan/workbook_enrichment.py` — `RunEnvelopeCorruptError`
- `app/marcus/lesson_plan/quiz_{spec,enrichment,producer}.py`
- `app/marcus/cli/marcus_spoc.py` — `run_plan_dialogue_preflight` + `--plan-dialogue`

---

## Explicit OUT / HOLD

- N6 residual trust slices (fidelity flag-ON, narration positive-carry, UDAC universality, bundle-carrier more, `reenter_at_node`, reading-path P2-4b)
- N3 siblings: job-aid / summary (later)
- N2 full 2B memory OS
- Track B: N1 ingest + N4 SME Gamma bind — **needs operator HAI/PHS media**
- Track C: N5 full SPOC terminal on real course content
- Track D: N7 Batch LLM — after N5 + live operator batching dialogue

---

## Party concurrence

| Seat | Verdict |
|------|---------|
| John | **CLOSE** Track A / HOLD B–D |
| Winston | **CLOSE** |
| Amelia | **CLOSE** (NIT only: optional hostile-input_fn pin) |
| Murat | **CLOSE** (stamps claim-envelope honest) |

**Orchestrator:** Track A CLOSED 4/4. Proceed only when operator delivers HAI/PHS media (Track B) or authorizes next trust slice / projector sibling within Track A residuals.
