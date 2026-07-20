---
baseline_commit: 9a111f1e
---

# Story Q1.4b: Deterministic final-report projector (Band + ranked-leaks + trend + this-run fence_state)

Status: ready-for-dev

<!-- Epic Q1 (Scorecard Engine + DID Reframe, FOUNDATION). DISPATCH #6 (LAST) of the binding GL-1 order: Q1.1 → Q1.4a → Q1.2 → Q1.3 → Q1.5 (all done) → **Q1.4b**. The splittable tail (GL-2), sequenced AFTER Q1.5 because it renders Q1.5's output shape. Closing this story closes Epic Q1. Source epic: _bmad-output/planning-artifacts/epics-project-quality-scorecard-2026-07-19.md. -->

## Story

As **the operator at a run's final report**,
I want **a deterministic projection of the project quality posture — Band + ranked-leaks + trend — alongside THIS run's actual fence_state facts, rendered in the Epic-43 tabular discipline**,
so that **I see, at run end, both the project's health band and what THIS run actually fenced — a checkable, reproducible surface, not prose.**

## Scope fence (read FIRST)

Q1.4b builds the deterministic PROJECTOR (the render code) + the cross-dimensional ranked-leak aggregation (GL-13). It does **NOT**:

- **Reauthor DID content** (Q1.5 done) — it only adds a machine-readable `leaks` list to the DID machine block mirroring the §1.6 ranked list Q1.5 authored, and renders it. No prose re-judgment.
- **Change the signal readers (Q1.2) / fence_state emitter (Q1.4a) / pin framework (Q1.3)** — it CONSUMES them (reads the scorecard via `dimension_ref`/`history`, takes a run's `fence_state` as plain input).
- **Wire the projector into `production_runner`'s live operator surface** — the LIVE E2E is DEFERRED to the R2 trial (GL-10): capture the projector output on R2 + ASSERT it equals the independently-computed env truth for that run. Q1.4b ships the projector FUNCTION + a golden; it does not re-touch the pipeline-lockstep `production_runner` emit path (that live wiring rides R2). File the R2 witness obligation.
- **Add module-scope `app.*` to `app/quality`** (GL-3) — any reuse of `hil_tabular_projector` is a deferred local import, or the tiny deterministic table renderer is re-expressed stdlib-only; the recursive leaf-guard stays green.

If you find yourself re-judging DID, editing the fence_state emitter, or wiring `production_runner`, **stop — that is a different story.**

## Acceptance Criteria

**AC1 — Structured cross-dimensional ranked-leak source (GL-13).** Add a machine-readable `leaks:` list to the DID dimension's machine block, mirroring the §1.6 ranked list + the `## DID Scorecard Leak Registry` slugs: each entry `{rank, criterion, slug, lane}` (lane ∈ paid-walk / learner-trust / governance, per §1.6 prioritization). `len(leaks) == open_leaks == did_leak: tag count == 5` (a fuller reconciliation; extend the Q1.3 leak-count pin to also assert `len(leaks) == open_leaks` if cheap). A `ranked_project_leaks(block)` aggregator collects **every** dimension's `leaks` into ONE cross-dimensional ranked list (DID sole contributor today; Q2/Q3 dimensions register into the same list — this is the GL-13 shared list). Ranking: by lane priority (paid-walk → learner-trust → governance) then rank.

**AC2 — Deterministic final-report projector (reuse Epic-43 tabular discipline).** `render_scorecard_final_report(*, block, history, fence_state) -> str` in a clean-leaf module (`app/quality/report.py`): renders, as deterministic markdown tables (reuse `hil_tabular_projector`'s `_md_table` discipline via a deferred local import, OR re-express a small stdlib-only deterministic table renderer following that discipline — reviewer's call; the bar is deterministic + Epic-43-consistent + golden-stable):
- **Band** (per dimension: label + Band + band_note; DID = B−) — NOT a false-precise `/100` headline (the per-criterion 0–4 may appear as a compact trace column).
- **Ranked project leaks** (from `ranked_project_leaks`) — rank · criterion · lane · slug.
- **Trend** — the computed arrow from `trend_from_history` (▬ baseline today), never painted.
- **This-run fence_state** — the block Q1.4a emits into `run_summary.yaml` (`fences_enabled {fidelity/coverage/udac}`, `silent_bypass_events`, `hil_allowlist_empty`, `cost_posture`, pack/chain digests), passed in as plain data.

**AC3 — Fail-soft (NFR1).** The projector NEVER raises: a missing/unavailable scorecard, empty history, or an absent/`{"status":"unavailable"}` fence_state each degrade to an honest rendered marker (e.g. "quality scorecard unavailable", "this run: fence_state unavailable") — a run's final report must never fail over the projection. Deterministic on degraded inputs too.

**AC4 — Determinism + golden.** Same inputs → byte-identical output (sort keys/rows deterministically; no dict-iteration-order dependence, no timestamps). A golden test pins the rendered report for (a) the real scorecard + a representative `fence_state`, and (b) the degraded/unavailable paths. RED under a seeded content change (band flip, leak added, fence flip). Not auto-blessed.

**AC5 — GL-13 registration contract documented for Q2/Q3.** Document (in the epic's Q2/Q3 story-template area or a short dev-guide note) that every new dimension MUST add its `leaks:` list to the machine block so `ranked_project_leaks` picks it up — else it silently stays DID-only. A structural test asserts `ranked_project_leaks` covers every dimension that declares `open_leaks > 0` (a dimension with open leaks but no `leaks` list → red).

**AC6 — R2 witness obligation filed (GL-10).** File (deferred-work.md / the trial runbook) the R2 checkable comparison: on the R2 trial, capture `render_scorecard_final_report(...)` output to a named evidence artifact and ASSERT it equals the independently-computed env truth (Band from the doc, fence_state from that run's env). Do NOT run a live trial here.

## Tasks / Subtasks

- [x] **T1 — Readiness.** Re-read the scope fence + GL-2/GL-10/GL-13 + consensus rule #4 (Band not /100). Confirm no pipeline-lockstep trigger path is edited (projector + doc machine-block leaks list + tests; `production_runner` untouched → regime does not trigger).
- [x] **T2 — Structured leaks list + aggregator** (AC1): add `leaks:` to the DID machine block (5 ranked entries, slugs matching the registry); `ranked_project_leaks(block)`; extend the Q1.3 leak-count pin to also check `len(leaks)==open_leaks` (if clean).
- [x] **T3 — Projector** (AC2/AC3): `app/quality/report.py::render_scorecard_final_report` — deterministic, fail-soft, Epic-43 tabular; clean leaf (deferred import of `_md_table` or a stdlib re-express). Reads scorecard via `dimension_ref`/`history`; `fence_state` passed in.
- [x] **T4 — Golden + determinism tests** (AC4): golden for real + degraded inputs; byte-identical repeat; RED-under-seeded-change; GL-13 coverage test (AC5).
- [x] **T5 — GL-13 doc + R2 obligation** (AC5/AC6): the registration-contract note; the R2 witness entry.
- [x] **T6 — Verify.** `pytest tests/quality/ -q`; ruff; import-linter 18/0; clean-leaf green; DID numbers unchanged; all Q1.3 pins still green (the `leaks` addition is additive — mirror pin unaffected since it mirrors score/band/levels/open_leaks/as_of/as_verified, not `leaks`).

## Dev Notes

### What exists (consume, do not rebuild)
- `app/quality/scorecard.py` (`dimension_ref`, `read_scorecard_block`, `did_score_ref`), `history.py` (`trend_from_history`, `newest_snapshot`), `signals.py` — the data layer.
- `app/marcus/cli/hil_tabular_projector.py`: `_md_table(headers, rows)` (L130) is the deterministic markdown-table renderer; `_truncate_cell` (L275), `_paginate` (L145). Reuse `_md_table`'s discipline (deferred import if used from `app/quality`, since it's `app.marcus.*` — the clean-leaf guard forbids a module-scope import). Note `_md_table` is a private helper; if cross-package deferred-import of a private symbol feels wrong, re-express a ~15-line deterministic md-table in `report.py` following the same shape (headers → `| … |` + separator + rows) — deterministic + golden-stable is the real bar.
- Q1.4a `fence_state` shape (in `run_summary.yaml`): `{fences_enabled:{fidelity,coverage,udac}, silent_bypass_events, hil_allowlist_empty, pack_hash_binding, conversation_chain_digest, cost_posture}` — values may be `"unavailable"`/`"undetected"` (render them honestly, never coerce to clean).

### The report is FACTS + POSTURE side by side
Consensus rule #1: the run emits FACTS (fence_state), the scorecard is project POSTURE (Band/leaks/trend). The projector shows BOTH clearly labeled — "This run" (fence_state) vs "Project (not this run)" (Band/leaks/trend) — so the operator never reads a project grade as a per-run claim. Label the sections that way.

### Clean-leaf + fail-soft (carried learnings)
- Module scope stays stdlib (+ yaml if needed); `hil_tabular_projector` only via deferred local import (or re-expressed). The recursive `test_scorecard_clean_leaf` covers `report.py`.
- Per-field fail-soft (Q1.4a learning): a bad scorecard degrades the Band section only; a bad fence_state degrades the run section only; the report always renders.
- Deterministic: sort leaks by (lane-priority, rank); sort fence keys by a fixed order; no `dict` iteration-order or timestamp leakage (golden depends on it).

### GL-13 forward-compat
`ranked_project_leaks` iterates ALL dimensions' `leaks` lists — today only DID has one. When Q2/Q3 add cost-efficiency/coverage/fidelity/etc., each adds its `leaks` list and the shared ranked list grows automatically. AC5's coverage test makes a dimension with `open_leaks>0` but no `leaks` list fail — so a sibling can't silently stay off the shared list.

### Scope boundary vs R2 (GL-10)
Q1.4b = the projector FUNCTION + golden (offline, deterministic). The LIVE run-end wiring + the checkable-comparison witness ride the R2 operator-steered trial (do not re-touch `production_runner`'s emit path here — it is a pipeline-lockstep trigger path, and the epic defers this E2E to R2). File the obligation; don't run a trial.

### Testing standards
- Reuse `tests/quality/`. Hermetic goldens (real scorecard read + a fixture fence_state; degraded fixtures). No live calls, no `--run-live`.
- The golden is a real render↔golden check (RED under seeded change), token- or full-output-anchored deliberately (per the Q1.5 golden-robustness learning: prefer stable structure over brittle exact-spacing where a reformat is meaning-preserving).

### References
- [Source: epics-project-quality-scorecard-2026-07-19.md#Story Q1.4] (the projector bullet) + [#Green-light amendments GL-2/GL-10/GL-13] + consensus rules #1/#4.
- [Source: app/marcus/cli/hil_tabular_projector.py:130 `_md_table`] — the tabular discipline to reuse.
- [Source: app/quality/scorecard.py · history.py · signals.py] — the data layer consumed.
- [Source: docs/quality/project-quality-scorecard.md §1.6 + machine block + `## DID Scorecard Leak Registry`] — the Band/leaks/trend + the 5 leak slugs.
- [Source: app/marcus/orchestrator/production_runner.py:1526 `_build_fence_state`] — the fence_state shape the projector renders (read-only reference).
- [Prev stories: q1-1/q1-4a/q1-2/q1-3/q1-5 all done] — the full machinery Q1.4b renders.

## Dev Agent Record

### Agent Model Used

Opus 4.8 (1M context) — fresh BMAD dev agent, RED-first discipline, `bmad-dev-story` workflow.

### Debug Log References

- **RED-first #1 (golden non-vacuous).** Perturbed `report.py` trend arrow (`▬ baseline` → `= baseline`) → `test_fixture_render_matches_golden`, `test_render_is_deterministic_byte_identical`, `test_real_scorecard_render_golden` all FAILED (3 failed, 14 passed); reverted → 17 passed.
- **RED-first #2 (leak reconciliation).** Struck the 5th structured `leaks:` entry from the DID machine block while leaving `open_leaks: 5` → both `test_leak_count_reconciles_on_real_repo` (extended, `4 == 5` AssertionError) and `test_real_did_leaks_reconcile_with_open_leaks` FAILED; reverted → 2 passed.
- **RED-first #3 (seeded change on copies).** `test_golden_reds_under_seeded_band_flip` / `_leak_added` / `_fence_flip` (deep-copied fixture) and `test_real_scorecard_render_reds_under_seeded_band_flip` (deep-copied real block, band→A) assert `render != golden`; `test_leak_coverage_gap_reds_for_dimension_without_leaks` reds a synthetic dimension with `open_leaks>0` and no `leaks` list (AC5).
- **Verify.** `pytest tests/quality/ -q` → 154 passed; `ruff check app/quality tests/quality` clean; `lint-imports` → 18 kept / 0 broken; clean-leaf (`test_scorecard_clean_leaf`) green over `report.py`; DID golden green; `did_score_ref()` → score 65, band B− (UNCHANGED).

### Completion Notes List

- **`app/quality/report.py::render_scorecard_final_report(*, block, history, fence_state) -> str`** — deterministic (same inputs → byte-identical; dimensions/criteria/leaks sorted by fixed keys, fixed fence-row order, no dict-order/timestamp leakage), fail-soft (NEVER raises; per-field: bad scorecard degrades the Project section only → `_quality scorecard unavailable_`; absent/`{"status":"unavailable"}` fence_state degrades the This-run section only → `_this run: fence_state unavailable_`; outer `except` last-resort marker). Two clearly-labelled sections — **"This run (facts)"** (fence_state) vs **"Project (not this run)"** (Band/leaks/trend) — so a project grade is never read as a per-run claim (consensus rule #1). Band per dimension (NOT a `/100` headline — asserted `"/100" not in out`); per-criterion 0–4 as a compact trace sub-table; trend arrow COMPUTED from the ledger via `trend_from_history` (never painted; `▬ baseline` today).
- **Tabular discipline (Epic-43).** Re-expressed a ~12-line stdlib `_md_table` (header → separator → body; `None`→empty cell) rather than a cross-package deferred import of the private `hil_tabular_projector._md_table` — keeps `report.py` a pure leaf with no coupling to a private cross-package symbol (reviewer's-call option in AC2; deterministic + golden-stable is the bar).
- **Clean-leaf (GL-3).** Module scope is stdlib only; `trend_from_history` reached via a **relative** intra-package import (`from .history import ...`), which references no foreign `app.*` name → the recursive clean-leaf guard stays green. No module-scope `app.*` in `app/quality`.
- **GL-13.** Added a structured `leaks:` list (5 entries `{rank, criterion, slug, lane}`) to the DID machine block, mirroring §1.6's ranked list + the `## DID Scorecard Leak Registry` slugs; `len==open_leaks==5`. `ranked_project_leaks(block)` aggregates EVERY dimension's `leaks` into ONE cross-dimensional list ranked by lane priority (paid-walk → learner-trust → governance) then rank — proven cross-dimensional by a 2-dimension fixture that interleaves Alpha(paid-walk) → Beta(learner-trust) → Alpha(governance). `leak_coverage_gaps(block)` is the AC5 structural guard (a dimension with `open_leaks>0` but no `leaks` list → gap + silently absent from the ranked list).
- **Additive-safety.** The `leaks:` addition does NOT break Q1.3 pins: the mirror pin mirrors `{score,band,levels,open_leaks,as_of,as_verified}` (not `leaks`); the DID §1.6 golden `_did_projection` ignores `leaks`; arithmetic/fence/leak-count/mirror/golden pins all stay green. Extended the leak-count pin to additionally assert `len(leaks)==open_leaks` when present (additive — never spuriously reds a dimension without a `leaks` list yet). **DID numbers UNCHANGED (65/B−).**
- **Scope fence honored.** Did NOT reauthor DID prose (only added the machine-readable `leaks` list); did NOT touch signal readers (Q1.2) / `fence_state` emitter (Q1.4a) / pin framework (Q1.3) beyond the additive `leaks` list + the projector + the extended pin; did NOT wire the projector into `production_runner` (verified untouched — pipeline-lockstep trigger path; live E2E deferred to R2 per GL-10). No scope-fence temptation acted on.
- **R2 witness obligation (AC6/GL-10) FILED** to `_bmad-output/implementation-artifacts/deferred-work.md` (`q1-4b-r2-final-report-projector-witness`): on R2, capture `render_scorecard_final_report(...)` to a named run-dir artifact and ASSERT it equals the independently-computed env truth (Band from the doc; fence_state recomputed from that run's env). No live trial run here.
- **GL-13 registration contract documented** at `docs/dev-guide/quality-scorecard-dimension-authoring.md` (Q2/Q3 dimensions MUST add their own `leaks:` list to register on the shared list, else they stay DID-only; the coverage guard catches an omission).
- **Left Status `ready-for-dev` per operator instruction (not committed).** Awaiting `bmad-code-review` + party green-light before advancing. Recommend running code review with a different model.

#### Code-review fixes applied (5, RED-first) — no BLOCKER/HIGH

- **FIX-1 [MED] slug-set IDENTITY pin.** The count pins reconcile through the integer 5 (registry `did_leak:` count == `open_leaks` == `len(leaks)`) and never compare slug IDENTITIES — a typo'd machine-block slug or a renamed registry tag keeps all three at 5 and stays green. Added `test_machine_block_leak_slugs_match_registry_identity` (SET equality of machine-block leak slugs vs registry `did_leak:` slugs, extracted with the same fenced/HTML-comment/archived stripping as the count signal). **RED proof:** typo'd a real machine-block slug on the doc → identity pin RED (`1 failed`) while both count pins stayed GREEN (`2 passed`); reverted.
- **FIX-2 [LOW] per-section fail-soft isolation + mixed-key sort guard.** (a) Each section now renders under its own `_try_section` guard, so a Project-section failure no longer discards a good fence section. (b) Every dimension/criteria `sorted(...)` is total-order-safe (`key=str` / `key=lambda kv: str(kv[0])`) — a heterogeneous-key machine block no longer `TypeError`s. **RED proof:** reverting to a single combined guard → `test_section_isolation_fence_survives_project_failure` RED; restored GREEN. Plus `test_mixed_key_block_does_not_crash_and_fence_survives`.
- **FIX-3 [LOW] degraded fence marker aligned to the REAL emitter.** `production_runner._build_fence_state` emits NO `status` key on degradation — it fills per-field `"unavailable"`/`"undetected"` VALUES. `_fence_state_is_marker` now renders the single honest marker for an empty `{}` OR a fence_state whose every leaf value ∈ `{"unavailable","undetected"}` (legacy `{"status":"unavailable"}` still handled). **RED proof:** reverting to status-only → `test_all_unavailable_fence_state_renders_single_marker` + `test_empty_fence_state_renders_single_marker` RED; restored GREEN. A partially-degraded fence (one real fact) still renders rows.
- **FIX-4 [LOW] `_md_table` cell escaping.** `_cell` now escapes `|` → `\|` and collapses CR/LF to a space; all row cells (labels, slugs, band_note, criterion keys) route through `_cell`, so an operator-authored pipe/newline can't split a row or silently defeat a row-anchored golden. **RED proof:** neutralizing the escaping → `test_cell_escaping_keeps_pipe_and_newline_in_one_cell` RED; restored GREEN.
- **FIX-5 [NIT] read the history ledger once.** `_render_trend` now reads/parses the JSONL ONCE via new additive `history.all_history_entries()` and derives each dimension's arrow from the in-memory entries via new additive `history.trend_from_entries()` (both delegate to the shared pure `_trend_from_dim_entries`). `trend_from_history` was refactored to a thin wrapper over the same pure computation — **behaviour byte-identical**, all 13 Q1.3 trend/mirror/history pins green, trend still COMPUTED (never painted). No O(dimensions) re-reads as Q2/Q3 land.
- **Post-fix verification:** `pytest tests/quality/` → **162 passed**; Q1.3 trend/mirror/leak pins → 13 passed; fence_state integration → 31 passed; ruff clean; `lint-imports` 18/0; clean-leaf green over `report.py`; **DID 65/B− UNCHANGED**; determinism byte-identical repeat confirmed.

### File List

- `app/quality/report.py` (new) — the deterministic fail-soft projector + `ranked_project_leaks` + `leak_coverage_gaps` + stdlib `_md_table` (+ FIX-2 per-section guards / total-order sorts, FIX-3 degraded-fence marker, FIX-4 cell escaping, FIX-5 single-read trend).
- `app/quality/history.py` (modified) — additive `all_history_entries()` + `trend_from_entries()` + shared pure `_trend_from_dim_entries()`; `trend_from_history` refactored to a behaviour-identical thin wrapper (FIX-5, single read).
- `app/quality/__init__.py` (modified) — export the projector + aggregators (relative imports; clean-leaf preserved).
- `docs/quality/project-quality-scorecard.md` (modified) — additive structured `leaks:` list (5 entries) in the DID machine block; DID numbers unchanged.
- `docs/dev-guide/quality-scorecard-dimension-authoring.md` (new) — the GL-13 leak-registration contract for Q2/Q3.
- `tests/quality/test_scorecard_final_report.py` (new) — fixture full-string golden + real-scorecard row-anchored golden + degraded/determinism/trend-computed/coverage/ranked-order tests.
- `tests/quality/test_scorecard_honesty_pins.py` (modified) — extended the real-repo leak-count pin to also assert `len(leaks)==open_leaks`.
- `_bmad-output/implementation-artifacts/deferred-work.md` (modified) — R2 witness obligation.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified) — status comment (row left `ready-for-dev`).
