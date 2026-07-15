---
id: 39-1b
epic: 39
status: ready-for-dev
split_from: 39-1-glossary-downstream-render.md  # green-light 2026-07-15 — 4/4 unanimous split; Package B lifted verbatim
depends_on: 39-1  # MUST land first — strict serialization on shared files _act.py + workbook_producer.py
anchor_provenance: post-37-2b working tree  # line anchors (e.g. _act.py L859–882) verified against the post-37-2b working tree; re-verify against the post-39-1 landed tree at dev-open
---

# Story 39.1b: D2 MERGE exercise composition — collateral + enrichment merged, labeled, capped, never silently dropped

Status: ready-for-dev

## Story

As the learner,
I want my practice exercises composed from BOTH authorities (Irene practice collateral + course-check instruments from the enrichment overlay) with visible provenance,
so that exercises never silently drop either source and I can tell "Practice" from "Course Check — drawn from this course's own assessments" at a glance.

## Provenance & Dependencies (BINDING)

- **Split origin:** this story is Package B of the original `39-1-glossary-downstream-render.md` draft, lifted verbatim at the 2026-07-15 green-light round (4/4 GREEN-WITH-AMENDMENTS; split unanimous).
- **39-1 MUST land first — strict serialization.** Both stories edit `app/specialists/workbook_producer/_act.py` and `app/marcus/lesson_plan/workbook_producer.py`. 39-1b does NOT open dev until 39-1's diff is landed; every line anchor below is re-verified against the post-39-1 tree at dev-open.
- **Authorities:** the D2 party record — `_bmad-output/planning-artifacts/wave-3940-kickoff-party-record-2026-07-15.md` §D2 MERGE design items 1–7 (this story encodes them as ACs) — and the wave record §D3 Paid-Run Economy Protocol (same-diff deliverable bar with negative pins; batch attribution; `done-awaiting-live-witness` vocabulary).
- **Boarding rule (split rider):** this story boards governed **run A** on suite-green alone — **no probe of its own** (fully deterministic; no LLM surface). It carries a **separate per-story verdict line** on run A's evidence pack.
- **Pin-flip ownership (split rider):** the ~5 enumerated intentional pin flips (expectation updates in existing workbook-producer tests) land in THIS story's diff, never 39-1's. Each flip is enumerated in the dev diff, never drive-by.

## T1 Readiness (BINDING readings before any code)

1. **Wave party record (BINDING)** — `_bmad-output/planning-artifacts/wave-3940-kickoff-party-record-2026-07-15.md`: §D2 MERGE design items 1–7 and §D3 Paid-Run Economy Protocol.
2. **Answer-leak precedent** — commit `c0811817` + `tests/unit/marcus/lesson_plan/test_workbook_answer_leak_hygiene.py` (47 pins; the precedent for exercise-surface pins — re-runs green in this story).
3. **37-2b SPEC (37-2b-contract-bound)** — `37-2b-deep-dive-enrichment-cited.md` T1 item 2 (`project_enrichment_to_workbook_inputs` covered-LO/fact consumption) — verify against landed code at dev-open.
4. **Pipeline-lockstep regime doc** — `docs/dev-guide/pipeline-manifest-regime.md` checked against `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`: NO trigger path is touched (see Lockstep declaration). Mid-dev drift into a trigger row is a STOP, party-gate.
5. **Live shapes** — `runs/8b275e5b-ed8a-4720-8217-8ddaca4c6627` frozen inputs (the M-D2-2 replay-pin substrate), including the real 18-exercise shape (6 overlay + 12 collateral) used by the J-3 trim pin.
6. **Post-39-1 landed diff** — re-verify the `_act.py` attach seam and `workbook_producer.py` render/Answer-Key anchors against the tree 39-1 leaves behind (strict serialization).

## D2 MERGE exercise composition (RATIFIED design — lifted verbatim from 39-1 Package B)

Hard precondition **satisfied**: the answer-leak strip landed at `c0811817` (`_project_exercises` never emits `Correct Answer:` in prompts; `answer_keys` is the channel; 47-test module `tests/unit/marcus/lesson_plan/test_workbook_answer_leak_hygiene.py` is the precedent for exercise-surface pins and re-runs green in this story).

### Acceptance Criteria

1. **origin field (provenance is a field, not a position)** — `Exercise` (`app/marcus/lesson_plan/collateral_spec.py:202`, extra=forbid) gains `origin: Literal["collateral","enrichment"]` with back-compat default `"collateral"`; `_project_exercises` (`workbook_enrichment.py:470`) stamps `"enrichment"` on overlay-projected exercises. Existing serialized specs load unchanged (default applies).
2. **MERGE at the attach seam** — the attach loop in `app/specialists/workbook_producer/_act.py:859–882` stops REPLACING (`sec.model_copy(update={"exercises": list(overlay_ex)})` L880 discards collateral): composition becomes **collateral exercises first, overlay appended**, per section. `project_enrichment_to_workbook_inputs` (`workbook_enrichment.py:561`) stays a pure single-source projector — the merge lives at the attach seam only (Winston D2-1).
3. **Collision guard** — overlay exercise ids prefixed `g0-<component_id>` at attach; any residual cross-source `exercise_id` collision fails loud via `assert_unique_collateral_ids` (`workbook_producer.py:281`) — never silent-dropped. The existing first-section-only overlay dedup (L865–881) is preserved.
4. **Cap + visible loss** — target total ≤12 exercises per workbook; per-unit collateral cap 2; **overlay items are never trimmed**; ANY dropped/trimmed collateral is recorded in a visible `exercise_overlay_loss` structure mirroring `lo_overlay_loss` (visible-degrade idiom, `workbook_producer.py:639–643` — the "degrade-with-record; never a silent placeholder swap" note) — never silent.
5. **Labeled render groups + Answer Key labels** — the exercises block (`workbook_producer.py:716–725`) groups per unit as **"Practice"** (origin=collateral) → **"Course Check — drawn from this course's own assessments"** (origin=enrichment); the Answer Key block (L727–746) carries the same labels; grouping keys on the `origin` FIELD, never on list position.
6. **Authoring-time dedup is an INPUT contract, not machine dedup** — NO machine semantic dedup (ratified reject: non-deterministic). This story's obligation: the overlay's covered-LO/fact list reaches Irene-side collateral authoring as INPUT (**37-2b-contract-bound**: 37-2b T1 item 2 already consumes it for deep-dive authoring; the exercise-authoring leg cites the same projection `project_enrichment_to_workbook_inputs`), and the residual-duplication check is DECLARED as an operator spot-check at governed run A (John's seed pairs: admin-cost %, 73-day doubling, digital front door) — never claimed machine-caught.
7. **Five deterministic floors + replay pin (M-D2-1/M-D2-2)** — I/O matrix below, each row pinned; extend the real-run replay probe to `runs/8b275e5b-ed8a-4720-8217-8ddaca4c6627` pinning the CHOSEN composition (merged, labeled, capped) against the frozen inputs; the 47 answer-leak pins re-run green; intentional pin flips (~5 expectation updates in existing workbook-producer tests) are enumerated in the dev diff, never drive-by.
8. **(Murat fold — MUST) Deliverable-bar exercise clause in THE SAME DIFF (D3 plank 5) + negative pins** — extend `_assert_completed_workbook_deliverable` (`scripts/utilities/marcus_spoc_live_test_runner.py`; anchor re-verified against the post-39-1 tree, which lands the glossary clause first) with THIS story's own exercise-composition clause, asserted off structured artifacts first, then MD: (i) the per-unit provenance **labels are present** ("Practice" / "Course Check — drawn from this course's own assessments") whenever the corresponding origin class has items; (ii) any collateral trim is accompanied by a structured **`exercise_overlay_loss` record** (silent trim = REJECT); (iii) **overlay-never-trimmed** holds (any overlay item absent from the render = REJECT). **Negative-witness pins in the same diff** (fed mutated copies of frozen live shapes; each must REJECT): (a) origin-labeled group missing while items of that origin exist; (b) collateral trimmed with no `exercise_overlay_loss` record; (c) overlay item dropped from the render.
9. **(J-3 fold — MUST) Cross-unit collateral trim rule — round-robin, pinned** — when the ≤12 cap forces collateral trimming across units, the trim order is **round-robin by unit, then stable id**: every unit keeps ≥1 Practice item before any unit keeps 2; within a unit, retention follows stable-id order. Deterministic pin against the **real 18→12 shape** from the frozen 8b275e5b inputs (6 overlay + 12 collateral → 6 overlay kept untrimmed + 6 collateral kept round-robin, trimmed items recorded in `exercise_overlay_loss`). Byte-deterministic across runs (extends matrix rows b/c).

### I/O matrix (the five ratified floors + guards — every row a pinned deterministic test)

| # | Input condition | Verdict / outcome |
|---|---|---|
| a | collision identity: overlay id == collateral id pre-prefix | `g0-` prefix disambiguates; residual collision ⇒ assert_unique_collateral_ids FAILS loud |
| b | total ordering | unit → provenance class (collateral before enrichment) → stable id; byte-deterministic across runs |
| c | cap: >12 total / >2 collateral in a unit | collateral trimmed deterministically per the J-3 round-robin rule (by unit, then stable id; every unit keeps ≥1 Practice before any keeps 2), recorded in `exercise_overlay_loss`; overlay NEVER trimmed |
| c′ | real 18→12 shape (6 overlay + 12 collateral, frozen 8b275e5b inputs) | 6 overlay kept + 6 collateral kept round-robin; trimmed 6 recorded in `exercise_overlay_loss`; pin is byte-deterministic (J-3) |
| d | provenance labels | "Practice" / "Course Check — drawn from this course's own assessments" groups render per unit; Answer Key mirrors labels |
| e | answer-key mapping, mixed keyed/unkeyed | keyed exercises map to their `answer_keys` entry under the correct label; unkeyed render without invented answers; no prompt carries `Correct Answer:` (47-pin floor) |
| f | zero overlay exercises | pure-collateral render, no "Course Check" group, no loss record |
| g | zero collateral exercises | pure-overlay render under "Course Check", no phantom "Practice" group |

## Batch-run AC — governed run A (split riders)

- **No probe.** This story is fully deterministic (no LLM surface); the boarding rule ("only fixes independently greened offline join a batch") is satisfied by **suite-green alone** — deterministic suite + M-D2-2 replay pin + `bmad-code-review` green.
- On suite-green + review-green this story flips to `done-awaiting-live-witness  # deterministic+review green; no probe owed (fully deterministic); full-run witness owed by batch run A (after 37-2b + 39-1 + 39-1b)`.
- Run A's evidence pack carries **this story's own per-verdict line** (separate from 39-1's), keyed to the terminal `07W` render + the exercise deliverable-bar clause (AC 8): REACHED+PASS ⇒ flip to `done` citing the run id; NOT-REACHED ⇒ claim stays OPEN (never pass, never fail). This story never crosses two batch boundaries unwitnessed.
- The residual-duplication operator spot-check (AC 6) is DECLARED at run A — WARN taxonomy, never claimed machine-caught.

## Scope Fences (hard NO)

- NO machine semantic dedup of exercises (ratified reject: non-deterministic).
- NO glossary/encyclopedia work (39-1's); NO Ask-B / `07W.4` (38.2); NO References assemble/dedupe redesign (37.5); NO mode-parity (37.6); NO cover (40.1); NO trends/Door-Ajar (39.2).
- NO `app/specialists/irene_pass1/` changes (M-R2 fence).
- NO edits to `workbook_wiring.py`, `research_packet.py`, `production_runner.py`, `state/config/pipeline-manifest.yaml`, or any node/manifest/pack-version/learning-event surface (= undeclared lockstep expansion → STOP, party-gate).
- NO weakening of: the terminal `07W` model-free pin, G2 citation gate, VO↔on-screen protected invariants, the 47 answer-leak pins.
- NO pin flips outside this story's enumerated ~5 (and none of them land in 39-1's diff).

## Lockstep declaration

Checked every scoped file against `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`:

| Scoped file | Trigger-path entry? | Touched? |
|---|---|---|
| `app/specialists/workbook_producer/_act.py` | not listed | yes (attach-seam MERGE) |
| `app/marcus/lesson_plan/workbook_producer.py` | not listed | yes (labeled groups, `exercise_overlay_loss`, Answer Key labels) |
| `app/marcus/lesson_plan/workbook_enrichment.py` | not listed | yes (origin stamp) |
| `app/marcus/lesson_plan/collateral_spec.py` | not listed | yes (origin field) |
| `scripts/utilities/marcus_spoc_live_test_runner.py` | not listed | yes (deliverable-bar exercise clause, AC 8) |
| `app/marcus/orchestrator/workbook_wiring.py` | **trigger** | **NO** |
| `app/marcus/orchestrator/production_runner.py` | **trigger** | **NO** |
| `state/config/pipeline-manifest.yaml` | **trigger** | **NO** |

**Verdict: zero trigger paths touched — lockstep regime not triggered.** Any drift into a trigger row is a STOP.

## Dev Notes

- **Code map:** UPDATE `_act.py:859–882` (attach MERGE + `g0-` prefixing — anchors re-verified post-39-1); UPDATE `collateral_spec.py:202` (+`origin`); UPDATE `workbook_enrichment.py:470–558` (origin stamp); UPDATE `workbook_producer.py:716–746` (labeled exercise groups + Answer Key labels + `exercise_overlay_loss`); UPDATE `marcus_spoc_live_test_runner.py` (exercise deliverable-bar clause + 3 negative pins, same diff); tests under `tests/unit/marcus/lesson_plan/` + `tests/specialists/workbook_producer/`; replay-pin fixtures derived from the real 8b275e5b run (live-shape rule; digest-bound with bump tripwire).
- **Strict serialization discipline:** open dev only after 39-1 lands; first dev act is re-anchoring every line reference above against the post-39-1 tree.
- **Guardrails:** product work only (SPOC); terminal `07W` stays deterministic-consume; carrier robustness — additive-safe, fail-loud, no silent drops; the ~5 intentional pin flips are enumerated per-test in the diff description.

### References

- `_bmad-output/planning-artifacts/wave-3940-kickoff-party-record-2026-07-15.md` — §D2 MERGE design items 1–7 (the ratified design this story encodes), §D3 planks + amendments, wave run plan
- `_bmad-output/implementation-artifacts/39-1-glossary-downstream-render.md` — split parent (Package A; lands first)
- `_bmad-output/implementation-artifacts/37-2b-deep-dive-enrichment-cited.md` — `project_enrichment_to_workbook_inputs` consumption contract (AC 6)
- `runs/8b275e5b-ed8a-4720-8217-8ddaca4c6627` — frozen live inputs (replay pin M-D2-2; J-3 18→12 pin)
- `docs/dev-guide/pipeline-manifest-regime.md` · commit `c0811817` (answer-leak strip + 47-pin precedent)

## Green-Light Round Record (2026-07-15)

- **Verdict: 4/4 GREEN-WITH-AMENDMENTS** — Winston (architecture), John (PM), Amelia (dev), Murat (test architecture); two combined-lens reviews.
- **Split: unanimous.** Package A stays as `39-1-glossary-downstream-render.md`; Package B (this story) lifted verbatim into `39-1b-exercise-merge-composition.md`, strict-serialized after 39-1 on the shared files (`_act.py`, `workbook_producer.py`). Both seat on governed run A with separate per-story verdict lines; 39-1b boards on suite-green (no probe — fully deterministic).
- **Amendments folded into 39-1b per finding id:** Murat deliverable-bar exercise clause + negative pins in this story's diff (D3 plank 5) → AC 8; J-3 cross-unit round-robin collateral trim rule, pinned against the real 18→12 shape (6 overlay + 12 collateral) → AC 9 + matrix row c′; split riders (strict serialization after 39-1; suite-green boarding, no probe; separate run-A verdict line) → Provenance & Dependencies + Batch-run AC; pin-flip ownership (~5 flips land in 39-1b's diff, never 39-1's) → Provenance & Dependencies + Scope Fences.
- **Amendments folded into 39-1 per finding id (recorded there):** W1/A-2, W2/M1, J-1, W3, M2, M3, J-2, A-1, A-3.
- **Orchestrator concurred — party-consensus-=-approval** (solo-operator rule, CLAUDE.md): both stories flip to ready-for-dev without a redundant human hold; 39-1b sits `backlog` in `sprint-status.yaml` until 39-1 lands (strict serialization).

## Change Log

- 2026-07-15: Story created by party-ratified split from 39-1 at the green-light round (4/4 GREEN-WITH-AMENDMENTS; split unanimous). Package B (D2 MERGE composition: 7 ACs + 5-floor I/O matrix) lifted verbatim; folded per finding id: Murat deliverable-bar exercise clause + negative pins (AC 8), J-3 round-robin trim rule + 18→12 pin (AC 9, row c′), split riders (strict serialization after 39-1; suite-green boarding without probe; separate run-A verdict line; ~5 pin flips owned by this diff). Status: **ready-for-dev** (dev-open gated on 39-1 landing — strict serialization).
