---
id: 39-1b
epic: 39
status: done-awaiting-live-witness
split_from: 39-1-glossary-downstream-render.md  # green-light 2026-07-15 — 4/4 unanimous split; Package B lifted verbatim
depends_on: 39-1  # MUST land first — strict serialization on shared files _act.py + workbook_producer.py
anchor_provenance: post-37-2b working tree  # line anchors (e.g. _act.py L859–882) verified against the post-37-2b working tree; re-verify against the post-39-1 landed tree at dev-open
baseline_commit: 6edf563e7131b246a6357d90b4f7c83d0cde594b
---

# Story 39.1b: D2 MERGE exercise composition — collateral + enrichment merged, labeled, capped, never silently dropped

Status: done-awaiting-live-witness  # deterministic+review green; no probe owed (fully deterministic); full-run witness owed by batch run A (after 37-2b + 39-1)

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

## Dev Agent Record

### Implementation Plan (T1 anchor re-verification, post-39-1 tree at `6edf563e`)

- Attach seam re-anchored: `_act.py:902–925` (was L859–882 in the spec); the REPLACE `sec.model_copy(update={"exercises": list(overlay_ex)})` sat at L923. Visible-degrade idiom re-anchored to `workbook_producer.py:681–685` (lo_overlay_loss_note render). `assert_unique_collateral_ids` at `workbook_producer.py:281` unchanged.
- Lockstep re-verified at dev-open against the live `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`: zero scoped files are trigger rows (matches the story's Lockstep declaration verbatim).
- Data flow implemented as the mirror of `lo_overlay_loss`: merge+prefix+cap in `_act.py` (attach seam only, Winston D2-1) → `WorkbookInputs.exercise_overlay_loss` → `produce(exercise_overlay_loss=…)` → `WorkbookSidecar.{exercise_composition, exercise_overlay_loss}` → `_sidecar_refs` → run.json 07W contribution → runner bar clause.
- The composition receipt (`exercise_composition`) is NEW beyond the spec letter: the bar's structured-first assertion needs a persisted per-section origin-grouping witness; it derives in `produce()` from the SAME composed spec the render walks, so structure cannot diverge from the deliverable.

### Debug Log

- **Frozen-shape discrepancy (recorded, not blocking):** the spec's row c′ claims the real 8b275e5b shape is "18 exercises (6 overlay + 12 collateral)". The frozen run's ACTUAL attachable shape (verified by running the real intake against `runs/8b275e5b…`) is **6 overlay + 8 collateral = 14 → capped to 12** (trim `ex-u03-2`, `ex-u05-2` — round-robin: the second items of the only two 2-collateral units). Per the live-shape rule the pin follows the real substrate (committed fixture `tests/fixtures/exercise_merge_39_1b/composition-8b275e5b.json` + skip-if-absent full replay probe); the ratified 18→12 arithmetic (6+12 → 6+6, trim 6) is pinned separately as a synthetic row-c case so the D2/J-3 letter is also witnessed.
- Answer-key channel: overlay worked answers are keyed by component id at projection; the `g0-` prefix at attach re-keys them in lockstep (row-e keyed lookups resolve on the RENDERED id). The 47-pin answer-leak floor is projection-level and unaffected (re-run green).
- `WITNESS_REPLAY_STRICT=1` suite 22/22 green post-change — the glossary-render witness family's digest surface is glossary-scoped and untouched by the Exercises/Answer Key render change.
- G1 on the frozen run post-merge: numeric audit AUDIT (pass), G2 unsourced 0 — the loss-callout counts are bare integers (symbol-only gate is a non-event) and exercise/answer numerals ride the existing `_authored_prose_figure_supplements` declaration.
- **Full-suite attribution (2026-07-16):** the repo-wide default suite (`-n auto`) reported 199 failed / 9866 passed; serial re-run + a clean **baseline worktree at `6edf563e`** proved **325 inherited reds failing identically with the 39-1b diff absent** (manifest G0R fold/schema pins, `tests/test_progress_map.py`, production-runner/Gary integration fixtures with Pass-1 authority-receipt drift, the known `test_health_tiles_prefer_persisted_cost_report`, etc. — pre-existing full-tree condition, surfaced to the operator as wave debt, NOT this story's scope), plus 1 uncommitted-diff tripwire (`test_audit_tw_7c_4_no_live_dispatch_scope_creep` scans `git diff HEAD`; clears at commit). **Zero failures attributable to this diff**; every my-surface module (answer-leak 47 pins, band wiring, schema parity, collateral emission, deep-dive wiring, bar modules, matrix module) green serially.

### Intentional pin flips (enumerated — the ~5 owned by this diff)

1. `tests/marcus/lesson_plan/test_collateral_spec_shape_stable.py` — `EXERCISE_EXPECTED_FIELDS` allowlist gains `origin` (AC 1).
2. `tests/specialists/workbook_producer/test_workbook_enriched_consumption.py` — 4 rendered-id assertions (T1, T3, T6-false, T6-true) flip from `Exercise \`src-001-c021\`` to the `g0-`-prefixed rendered id via new `RENDERED_QUIZ_EXERCISE_ID` (AC 3 collision guard).
3. `app/marcus/lesson_plan/schema/collateral_spec.v1.schema.json` — emitted JSON-Schema witness regenerated from the live model (byte-current pin `test_emitted_schema_is_byte_current_vs_live`; regen discipline).

No other expectation changed; 39-1's diff carries zero flips from this story (pin-flip ownership rider held).

### Completion Notes

- AC 1 ✅ `origin: Literal["collateral","enrichment"]` (back-compat default) on `Exercise`; `_project_exercises` stamps `"enrichment"`. Existing serialized specs load unchanged (default applies; shape-pin + invariants green).
- AC 2 ✅ attach loop MERGEs (collateral first, overlay appended); projector stays pure single-source.
- AC 3 ✅ `g0-<component_id>` prefix at attach + answer-key re-key; residual collision fails loud via `assert_unique_collateral_ids` (row-a negative test); first-section-only overlay dedup preserved.
- AC 4 ✅ `_apply_exercise_composition_cap`: total ≤12, per-unit collateral cap 2, overlay never trimmed, `exercise_overlay_loss` record mirrors `lo_overlay_loss` + visible MD callout — never silent.
- AC 5 ✅ per-unit origin-keyed groups "Practice" / "Course Check — drawn from this course's own assessments" in Exercises AND Answer Key (labels are module constants; the runner bar imports them — no drift).
- AC 6 ✅ DECLARED (contract-bound verified against landed 37-2b code): `deep_dive_enrichment.py:1055–1075` consumes `project_enrichment_to_workbook_inputs` (covered LOs/sections) as authoring input; the exercise-authoring leg cites the same projection. NO machine semantic dedup anywhere in this diff; residual-duplication check is an **operator spot-check at governed run A** (John's seed pairs: admin-cost %, 73-day doubling, digital front door) — WARN taxonomy, never claimed machine-caught.
- AC 7 ✅ `tests/specialists/workbook_producer/test_exercise_merge_composition_39_1b.py` — 15 deterministic tests: rows a (identity + residual-collision), b (class-then-stable-id order; byte-deterministic), c (per-unit cap, ratified 18→12 round-robin, overlay-beyond-cap, partial-second-round), c′ (committed live-shape fixture pin + full 8b275e5b replay probe M-D2-2, skip-if-absent), d (labels + Answer Key mirror + receipt), e (mixed keyed/unkeyed + no `Correct Answer:` on the rendered surface), f/g (no phantom groups, no loss record), visible-callout test.
- AC 8 ✅ `_assert_exercise_composition_conformant` wired into `_assert_completed_workbook_deliverable` (same diff, plank 5): structured receipt first (well-formedness; trim⇔loss consistency), MD floor second (label presence per origin class; overlay-never-trimmed; callout⇔record desync both directions). `tests/unit/scripts/test_workbook_deliverable_bar_39_1b.py` — 12 tests incl. the 3 named negative pins (a/b/c) + desync/malformed/tally-mismatch pins + pre-39.1b tolerance; existing 37-2b/39-1 bar modules re-run green (46/46 combined).
- AC 9 ✅ J-3 round-robin (by unit in section order, then stable id; every unit keeps ≥1 Practice before any keeps 2) pinned against the real frozen shape AND the ratified synthetic 18→12 shape; byte-deterministic across runs.
- Scope fences held: no irene_pass1/ wiring/manifest/pack edits; terminal 07W stays deterministic-consume; 07W model-free pin, G2 gate, VO↔on-screen invariants untouched; 47 answer-leak pins green.

## Senior Developer Review (AI) — T4 Blind+Edge+Auditor, 2026-07-16

**Outcome: APPROVED WITH REMEDIATION APPLIED (same session).** Three parallel layers on `git diff 6edf563e..179ccdd9`: Blind Hunter (adversarial), Edge Case Hunter, Acceptance Auditor. Auditor verdict: **9/9 ACs satisfied, 0 violated** (frozen-shape deviation ruled conforming-in-intent under the live-shape rule; scope fences + protected invariants held; negative pins genuinely mutated frozen shapes per M-D3-2b). 14 normalized findings after blind+edge dedup → 4 dismissed, 10 patched, 0 deferred, 0 decision-needed.

### Action Items (all resolved this session)

- [x] [Review][Patch] **F4 (MED): schema-versioning contract skipped** — `SCHEMA_VERSION` bumped `1.1 → 1.2` + `SCHEMA_CHANGELOG.md` "CollateralSpec v1.2" entry (minor/additive per the repo's semver-for-schemas) + emitted witness regenerated + shape-stable pin updated in lockstep (same enumerated flip surface). [`collateral_spec.py:68`]
- [x] [Review][Patch] **F2 (MED): silent-trim check was tautological** (receipt tally copies the loss record) — bar gains the **independent blueprint cross-check**: kept Practice ∪ trimmed ids must EQUAL Irene's authored collateral ids off run.json (disjointness enforced; tolerant only when the blueprint is absent). The REAL silent-trim mutant (trims, records nothing, internally consistent) now REJECTS. [`marcus_spoc_live_test_runner.py`; pins `test_blueprint_cross_check_*`]
- [x] [Review][Patch] **F9 (LOW): label check satisfiable by the Answer Key mirror alone** — heading presence is now `count >= 2` (Exercises block + Answer Key mirror both required); bar-test MD builder emits the mirror. [pin `test_label_missing_from_one_block_rejects`]
- [x] [Review][Patch] **F10 (LOW): bar never verified Practice ids / trimmed ids against the render** — kept Practice ids must render; recorded-trimmed ids must NOT render. [pins `test_practice_id_dropped_from_render_rejects`, `test_trimmed_id_still_rendering_rejects`]
- [x] [Review][Patch] **F8 (LOW): note-less/empty-note loss record rendered a literal "None" callout / suppressed the callout while the record persisted** — callout now renders whenever the record exists, with an honest generic fallback text. [pin `test_noteless_loss_record_renders_fallback_callout_never_none`]
- [x] [Review][Patch] **F11 (LOW): receipt laundered a malformed `trimmed_count` to 0** — tally now copied VERBATIM; the runner's well-formedness check refuses garbage instead of trusting a producer-cleaned claim.
- [x] [Review][Patch] **F6 (LOW): overlay overflow past the total cap was unrecorded** — explicit warning when `overlay_total > 12` (overlay is never trimmed by ratified design; the receipt's `course_check_total` carries the number).
- [x] [Review][Patch] **F7 (LOW): answer-key re-key collision / double-prefix were silent** — both anomalies now warn loudly (mirrors the answer-leak routing warnings); behavior stays deterministic.
- [x] [Review][Patch] **F1b (LOW): "stable id" ambiguity on numeric suffixes** — docstring states plainly: LEXICOGRAPHIC order (`ex-10` < `ex-2`); zero-pad for numeric retention priority. Natural-sort was not adopted (unratified behavior change; current corpus shapes single-digit).

### Dismissed (4, with reasons)

- **Authored exercise order "destroyed"** — the re-sort IS the ratified row-b total ordering (unit → provenance class → stable id; M-D2-1 determinism floor).
- **Cap reshapes card-less legacy runs** — D2-5 is an unconditional workbook cap by design (matrix rows f/g assume it); any legacy trim is recorded + callout-visible, never silent.
- **All-texts semantics on multi-deliverable runs** — matches the deep-dive sibling clause's every-MD idiom; the producer emits exactly one MD+DOCX pair per run today; revisit only if multi-workbook runs ever ship.
- **Duplicate `section_id` heading ambiguity** — duplicate section ids cannot ship: `assert_unique_collateral_ids` rejects them at `produce()`.

**Post-remediation verification:** changed-files ruff clean; matrix module 16/16; bar modules 24 + siblings = 73 combined green; `tests/marcus/lesson_plan/` + contract version pins 395 green; scoped workbook battery 1,556 green; STRICT witness replay 22/22.

## File List

- `app/marcus/lesson_plan/collateral_spec.py` — `Exercise.origin` field (AC 1)
- `app/marcus/lesson_plan/workbook_enrichment.py` — origin stamp in `_project_exercises` (AC 1)
- `app/specialists/workbook_producer/_act.py` — attach-seam MERGE + `g0-` prefix + answer-key re-key + `_apply_exercise_composition_cap` + `WorkbookInputs.exercise_overlay_loss` + produce pass-through + `_sidecar_refs` keys (ACs 2/3/4/9)
- `app/marcus/lesson_plan/workbook_producer.py` — group-label constants + `_exercise_origin_groups` + `_exercise_composition_receipt` + labeled Exercises/Answer Key blocks + loss callout + `compose_workbook`/`produce` params + `WorkbookSidecar` fields (ACs 4/5/8-structured)
- `app/marcus/lesson_plan/schema/collateral_spec.v1.schema.json` — regenerated emitted-schema witness (pin flip 3)
- `scripts/utilities/marcus_spoc_live_test_runner.py` — `_assert_exercise_composition_conformant` + wiring into `_assert_completed_workbook_deliverable` (AC 8)
- `tests/specialists/workbook_producer/test_exercise_merge_composition_39_1b.py` — NEW: I/O matrix rows a–g + c′ + replay probe (AC 7/9)
- `tests/unit/scripts/test_workbook_deliverable_bar_39_1b.py` — NEW: bar clause positive floors + negative pins (AC 8)
- `tests/fixtures/exercise_merge_39_1b/composition-8b275e5b.json` — NEW: committed live-shape composition fixture (row c′; schema_version bump tripwire)
- `tests/marcus/lesson_plan/test_collateral_spec_shape_stable.py` — pin flip 1 (origin in allowlist) + T4 F4 version-pin update (1.1→1.2, same enumerated surface)
- `tests/specialists/workbook_producer/test_workbook_enriched_consumption.py` — pin flip 2 (rendered `g0-` id)
- `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` — T4 F4: CollateralSpec v1.2 entry (additive `Exercise.origin`)

## Change Log

- 2026-07-16 (T4): **Review APPROVED + remediation applied same session** — schema v1.2 bump + changelog (F4); bar hardened with the independent blueprint cross-check (F2), both-blocks label check (F9), Practice-id/trimmed-id render checks (F10); producer callout/receipt robustness (F8/F11); overflow + re-key warnings (F6/F7); lexicographic-order docstring (F1b). 4 findings dismissed with recorded reasons. Status → **done-awaiting-live-witness** (deterministic+review green; no probe owed — fully deterministic; full-run witness owed by batch run A).
- 2026-07-16: **Story 39.1b implemented** (dev agent, baseline `6edf563e`). D2 MERGE composition landed end-to-end: origin field + enrichment stamp; attach-seam MERGE with `g0-` collision prefix + answer-key re-key; ≤12/per-unit-2 cap with J-3 round-robin trim + `exercise_overlay_loss` (structured record + visible callout, mirror of `lo_overlay_loss`); per-unit "Practice"/"Course Check" origin-keyed render groups mirrored in the Answer Key; `exercise_composition` receipt persisted to run.json; runner deliverable-bar exercise clause + negative pins in the same diff (plank 5). 15 new matrix tests + 12 new bar tests; 3 enumerated pin-flip surfaces (allowlist, rendered id ×4, emitted schema regen); 47 answer-leak pins + STRICT witness replay 22/22 + existing bar modules re-run green. Frozen-shape discrepancy recorded: real 8b275e5b composition is 6 overlay + 8 collateral (14→12, trim 2), not the spec's estimated 6+12; both the real shape and the ratified 18→12 arithmetic are pinned.
- 2026-07-15: Story created by party-ratified split from 39-1 at the green-light round (4/4 GREEN-WITH-AMENDMENTS; split unanimous). Package B (D2 MERGE composition: 7 ACs + 5-floor I/O matrix) lifted verbatim; folded per finding id: Murat deliverable-bar exercise clause + negative pins (AC 8), J-3 round-robin trim rule + 18→12 pin (AC 9, row c′), split riders (strict serialization after 39-1; suite-green boarding without probe; separate run-A verdict line; ~5 pin flips owned by this diff). Status: **ready-for-dev** (dev-open gated on 39-1 landing — strict serialization).
