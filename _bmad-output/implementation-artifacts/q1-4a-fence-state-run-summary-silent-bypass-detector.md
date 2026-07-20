---
baseline_commit: dd2b2bb0
---

# Story Q1.4a: Per-run `fence_state` in run_summary + honest `silent_bypass_events` detector

Status: ready-for-dev

<!-- Epic Q1 (Scorecard Engine + DID Reframe, FOUNDATION). DISPATCH #2 of the binding GL-1 order: Q1.1 (done) → **Q1.4a** → Q1.2 → Q1.3 → Q1.5 → Q1.4b. Q1.4 was split per GL-2: Q1.4a = the run_summary fence_state block + honest silent_bypass detector (ships the operator job); Q1.4b = the final-report projector (sequenced AFTER Q1.5). Source epic: _bmad-output/planning-artifacts/epics-project-quality-scorecard-2026-07-19.md. -->

## Story

As **the operator at a paid-run gate**,
I want **this run's actual fence FACTS emitted into `run_summary.yaml` (not a project-average grade), with `silent_bypass_events` reporting an honest value instead of a hardcoded `0`**,
so that **a fence regression shows up in the run where it happened, and the report never claims a clean bypass count it did not actually check**.

## Scope fence (read FIRST)

This story emits **per-run mechanical FACTS** and fixes the `silent_bypass_events` honesty gap. It is bounded by binding consensus rule #1 ("runs emit facts, not the grade") and GL-2/GL-4/GL-5/GL-8/GL-15. It explicitly does **NOT**:

- **Build the final-report projector / Band+leaks+trend surface** — that is **Q1.4b** (sequenced after Q1.5). Q1.4a emits the raw `fence_state` data; it renders nothing operator-facing beyond the YAML.
- **Add the `app/quality` signal READERS (C2/C3/C4/leak-count)** — that is **Q1.2**. Q1.4a produces the honest run facts (esp. `silent_bypass_events`) that Q1.2's C4 reader later *consumes*; per GL-1, Q1.4a ships first and Q1.2's C4 rides the honest `undetected`/`null` state.
- **Add honesty-pin ratchet tests** (Q1.3) — including the GL-8(b) "`undetected` caps C4" pin. Q1.4a only *emits* the honest value that pin will key on.
- **Reauthor / re-score DID or edit the scorecard doc's assessment** (Q1.5). The only scorecard-doc-adjacent change here is a *code* change that STOPS the per-run doc-read (GL-4), not a doc edit.
- **Touch `app/quality/scorecard.py` or the doc machine block** — Q1.1 landed those; Q1.4a does not import `app.quality` on the hot path except to remove the existing doc-read stamp.

If you find yourself rendering an operator table, writing a signal reader under `app/quality/`, or editing §1.6 of the scorecard doc, **stop — that is a different story.**

## Acceptance Criteria

**AC1 — `fence_state` block emitted in `run_summary.yaml`, computed inside the shared emitter.** `app/marcus/orchestrator/production_runner.py::_emit_run_summary_yaml` (`:1417`) gains a `fence_state` block of **per-run FACTS**:
- `fences_enabled: {fidelity: bool, coverage: bool, udac: bool}` — from `narration_figure_fidelity_active()` (irene.graph, **deferred local import** — do not add a heavy module-level import), `coverage_gate_wiring.coverage_gate_active()`, `udac_wiring.udac_active()` (the latter two already imported by this module).
- `silent_bypass_events` — the **honest** value per AC2 (never a hardcoded `0`).
- `hil_allowlist_empty: bool` — from `len(hil_tabular_projector.KNOWN_UNRENDERED_ALLOWLIST) == 0` (deferred local import; the projector module is heavy).
- `pack_hash_binding` and `conversation_chain_digest` — **reference the values already computed in the payload** (`:1437`, `:1443`); do not recompute.
- `cost_posture` — reuse the existing economics read (`_operator_surface_cost_reading` @`:364`, or the same `TrialEconomicsReport` seam it uses); `exact` / `estimated` / `unavailable`. If not resolvable at the emit seam, emit `"unavailable"` (honest), never fabricate.

**AC2 — `silent_bypass_events` fixed (the precondition, GL-8).** Today `silent_bypass_events` is a param defaulting `0` that **no caller ever sets** (verified: zero `silent_bypass_events=` call sites), so every run stamps a dishonest `0`. Replace with an honest value:
- Wire it to a **real detector** where a signal already exists, OR emit the sentinel **`"undetected"`** (a string, not `0`) when no detection ran. An honest "we didn't check" beats a false clean.
- GL-8(a) — a **component detection test**: seed a synthetic bypass event → the detector reports it; no event → honest `undetected` (or a real `0` only if a detector genuinely ran and found none). Design note: Epic-41 made the *silent-specialist-skip* class **fail loud in both walks** (`SilentGateBypass`-style raise, `:258`), so that class is zero-by-construction on any run that *completed* to a run_summary; you may assert that honestly. Other bypass classes (e.g. the Path-Z §05/§05B skip, `:3999`) have no run-scoped counter today → `undetected` is the honest emission unless you wire a real ledger.
- Do **not** add the GL-8(b) "`undetected` caps C4" pin here — that lives in Q1.3; just emit the value it keys on.

**AC3 — Stamped project score REMOVED; static breadcrumb replaces it (GL-4, consensus rule #1).** The payload's `"quality_scorecard": _quality_scorecard_ref()` (`:1448`, which parses the governance doc every emit) is replaced by a **STATIC** breadcrumb dict literal: `{"source": "docs/quality/project-quality-scorecard.md", "note": "project-level-not-this-run"}` (an `as_of` key is optional and, if present, MUST be a static string — it must **not** trigger a doc parse inside `_emit_run_summary_yaml`). Per-run facts derive ONLY from run signals, never the doc. The `_quality_scorecard_ref()` doc-reading helper is removed from the emit path (the `app/quality` reader + CLI keep it for their own use; this only decouples the *runtime run-summary* from the doc).

**AC4 — Present across BOTH walks (GL-5).** Because `fence_state` is computed inside the single shared `_emit_run_summary_yaml`, all five call sites inherit it: start-walk (`_pause_at_gate` `:2691`, `run_production_trial` `:4172`) and resume/continue-walk (`_resume_prewalk_settings` `:4269`, `resume_production_trial` `:4422`, `_continue_production_walk` `:5457`). A test asserts `fence_state` is present in the emitted YAML from **both** a start-walk emit AND a resume-walk emit (a single-site wiring would silently drop it on the other walk — the two-walks gotcha).

**AC5 — `fence_state` reflects env truth.** Monkeypatch each of the three gate functions on/off → the emitted `fences_enabled` dict matches exactly (a fence fact can never drift from the flag it mirrors). Same for `hil_allowlist_empty` against a monkeypatched allowlist.

**AC6 — Fail-soft (NFR1).** The entire `fence_state` computation is wrapped so it **NEVER raises into a production run**: any error in a gate call / economics read / allowlist read degrades that field to an honest marker (`"unavailable"` / `"undetected"`) and the emit still writes a well-formed `run_summary.yaml`. A run must never fail over emitting its own fence facts. Test: force each sub-reader to raise (monkeypatch) → emit still succeeds, field carries the marker, never absent/raising.

**AC7 — Tests (component, hermetic).** Extend the existing **direct** emit test (`test_nonzero_silent_bypass_events_logs_debug_warning` and siblings that call `_emit_run_summary_yaml` directly — NOT the live-preflight `test_run_summary_yaml_emit` integration tests, which have a **pre-existing, unrelated** Epic-41 preflight-gate failure — stash-verified at baseline; do not attribute to this story or try to fix them here). New/extended hermetic tests cover: fence_state present + shape; the AC2 detector matrix; AC4 both-walks presence; AC5 env-truth; AC6 fail-soft; AC3 breadcrumb is static (assert no doc read occurs — e.g. monkeypatch the scorecard path to a sentinel and assert it is NOT opened during emit). **E2E (deferred to R2, GL-10):** the R2 operator-steered trial witnesses `fence_state`; capture it to a named evidence artifact and ASSERT equality with the independently-computed env truth for that run (a checkable comparison, not a mere observation). File the R2 witness obligation; do not run a live trial in this story.

## Tasks / Subtasks

- [x] **T1 — Readiness.** Re-read the scope fence + consensus rule #1 + GL-2/GL-4/GL-5/GL-8/GL-15/NFR1. **Pipeline-lockstep check: `production_runner.py` IS a `block_mode_trigger_paths` entry** (per `state/config/pipeline-manifest.yaml` / CLAUDE.md §Pipeline lockstep regime) — read `docs/dev-guide/pipeline-manifest-regime.md` at T1 before any code, and honor the block-mode discipline. Confirm no pack-version bump is implied (this is runtime emission, not a pack/step change → Tier-1 connective-tissue, dev-agent authority under the block-mode hook).
- [x] **T2 — `fence_state` builder** at the runner seam (GL-3: compute here, NOT in `app/quality`). A small `_build_fence_state(...)` helper in `production_runner.py` (or a runner-local module) returning the plain-data dict; fail-soft per AC6; deferred local imports for irene.graph + hil_tabular_projector. (AC1, AC6)
- [x] **T3 — Honest `silent_bypass_events` detector** (AC2). Decide real-detector-vs-`undetected` with the party's GL-8 guidance; wire it into the fence_state build. Keep the existing debug-log behavior compatible.
- [x] **T4 — Wire `fence_state` into the payload** inside `_emit_run_summary_yaml`; reference existing `pack_hash_binding`/`conversation_chain_digest`; add `cost_posture` via the economics seam. (AC1, AC4 — structural via shared emitter)
- [x] **T5 — GL-4 breadcrumb.** Replace `"quality_scorecard": _quality_scorecard_ref()` with the static pointer; remove the doc-read from the emit path. (AC3)
- [x] **T6 — Tests** (hermetic, direct-emit style). fence_state shape/presence, both-walks (AC4), env-truth (AC5), fail-soft (AC6), detector matrix (AC2), static-breadcrumb-no-doc-read (AC3). File the R2 witness obligation (GL-10) to `_bmad-output/maps/deferred-work.md` or the trial runbook. (AC7)
- [x] **T7 — Verify.** `pytest` the touched run_summary/emit tests + any two-walks resume test; `ruff`; `lint-imports` (import-linter). Confirm the 2 pre-existing preflight integration failures are unchanged (stash-verify if in doubt), not newly introduced.

## Dev Notes

### Current state of the seam (READ THESE before coding)

**`_emit_run_summary_yaml` (`app/marcus/orchestrator/production_runner.py:1417-1451`).** The single shared emitter. Current payload keys: `terminal_gate`, `silent_bypass_events` (param, default 0, debug-logs if ≠0), `specialist_roster_count`, `pack_hash_binding` (`:1437`), `component_selection`, `conversation_chain_digest` (`:1443`), `langsmith_trace_id`, `quality_scorecard` (`:1448` — the doc-reading stamp to replace). Writes `run_summary.yaml` under the run dir.

**The five call sites (two walks — GL-5).** Start-walk: `_pause_at_gate` (`:2691`, has composed `manifest`), `run_production_trial` (`:4172`, composed manifest). Resume/continue-walk: `_resume_prewalk_settings` (`:4269`, early-reject, no composed manifest), `resume_production_trial` (`:4422`, early-reject, no composed manifest), `_continue_production_walk` (`:5457`, composed manifest). Computing fence_state INSIDE the emitter covers all five with no per-call-site threading — the GL-5-safe design.

**Gate functions.** `narration_figure_fidelity_active()` (`app/specialists/irene/graph.py:180`) — **not currently imported** by production_runner; use a deferred local import inside the builder. `coverage_gate_wiring.coverage_gate_active()` (`:70`) and `udac_wiring.udac_active()` (`:50`) — already imported/used by production_runner (see `:307`, `:2906`, `:2919`). All three read env/config → calling them at emit time yields the run's actual fence posture.

**`silent_bypass_events` reality.** Param at `:1424`, stamped at `:1435`; **no caller sets it** → always `0`. The Epic-41 fail-loud on silent specialist skip (exception class `:258`; "fails loud in both walks", commit 81fdc495) means that bypass class halts the run rather than silently proceeding — so a *completed* run_summary honestly has zero of that class; other classes are `undetected` absent a real ledger. This is the honesty gap GL-8 closes.

**`hil_allowlist_empty`.** `hil_tabular_projector.KNOWN_UNRENDERED_ALLOWLIST` (`app/marcus/cli/hil_tabular_projector.py:1465`) is `frozenset()` today (drained at 43-9). `hil_allowlist_empty = (len(...) == 0)` → `True`. Deferred local import (heavy module).

**`cost_posture` (GL-15 / NFR3 — reuse, no parallel plumbing).** `_operator_surface_cost_reading` (`:364`) reads a `TrialEconomicsReport` (`app/models/runtime/trial_economics_report.py`; `cost_posture: Literal[...]` at `:74`; `check_trial_budget`/`BudgetStatus` at economics.py:347 / model :40) and returns `(cost, posture)`. Reuse that read for the fence_state `cost_posture`; do not build a second economics reader. Deep cost-efficiency scoring is **Q2.1**, not here.

### Binding constraints recap
- **Consensus #1:** runs emit FACTS, not the grade → fence_state is facts; the scorecard ref is a static breadcrumb pointer (GL-4).
- **GL-3:** compute fence/env facts at the `production_runner` seam and pass as plain data — do NOT push this into `app/quality` (Q1.1's clean-leaf guard, now recursive + module-scope, would catch a foreign import there anyway).
- **GL-5:** ALL FIVE emit sites — satisfied structurally by computing inside the shared emitter; test both walks.
- **GL-8:** honest `silent_bypass_events` (never dishonest `0`); detector matrix test.
- **NFR1/AC6:** fail-soft — the fence_state build never raises into a run.

### Q1.1 review learnings carried forward (previous-story intelligence)
- **Fail-soft must be per-field, not just top-level.** Q1.1's Edge finding showed a top-level guard let a malformed sub-structure crash downstream. Here: guard **each** gate/economics/allowlist read independently so one failure degrades one field, not the whole emit.
- **Mirror existing defensive idioms.** Q1.1's reader used `isinstance` guards before `.get`; match that style.
- **RED-first the honesty guards.** Prove the detector test goes RED on a seeded bypass, and that the static-breadcrumb test goes RED if a doc-read is reintroduced.
- **Don't over-reach across the story split** — Q1.1 held its scope fence exactly; do the same (no projector, no signal readers, no pins).

### Testing standards
- Use the **direct** `_emit_run_summary_yaml(...)` call style (hermetic, tmp run dir), like `test_nonzero_silent_bypass_events_logs_debug_warning`. Avoid the live-preflight integration path.
- The 2 pre-existing `test_run_summary_yaml_emit` integration failures (`PreflightGateFailed: hud-server-healthz/openai`) are **baseline, unrelated** — do not fix or attribute here.
- No live calls; no `--run-live`. E2E fence_state witness is deferred to the R2 trial (GL-10), filed as an obligation, not run here.

### Project structure notes
- `production_runner.py` is a pipeline-lockstep `block_mode_trigger_paths` entry → block-mode discipline applies (T1 reads the regime doc). This is Tier-1 connective-tissue (runtime emission; no pack/step/manifest schema change) → proceeds under dev-agent authority gated by the block-mode hook; **no pack version bump** and no party pre-consult required for Tier-1 (confirm no Tier-2/3 trigger).
- import-linter must stay green (18 contracts); the new deferred local imports keep the module-level graph unchanged.

### References
- [Source: epics-project-quality-scorecard-2026-07-19.md#Story Q1.4] + [#Green-light amendments GL-2/GL-4/GL-5/GL-8/GL-15/GL-10] + consensus rules #1.
- [Source: app/marcus/orchestrator/production_runner.py:1417-1451] — the emitter; [:2691,:4172,:4269,:4422,:5457] the five sites; [:1402] the doc-read stamp to remove; [:364] the economics read to reuse.
- [Source: app/specialists/irene/graph.py:180] · [app/marcus/orchestrator/coverage_gate_wiring.py:70] · [app/marcus/orchestrator/udac_wiring.py:50] — the three gate fns.
- [Source: app/marcus/cli/hil_tabular_projector.py:1465] — KNOWN_UNRENDERED_ALLOWLIST.
- [Source: app/models/runtime/trial_economics_report.py:40,74] · [app/runtime/economics.py:347] — cost_posture/BudgetStatus.
- [Source: docs/dev-guide/pipeline-manifest-regime.md] — block-mode discipline for the trigger path.
- [Prev story: q1-1-scorecard-schema-v2-generalized-reader-versioning.md] — done; the reader/schema this run-summary breadcrumb points at.

## Dev Agent Record

### Agent Model Used

Claude Opus 4.8 (1M context) — `claude-opus-4-8[1m]` (fresh BMAD dev agent, RED-first TDD).

### Debug Log References

- T1 block-mode/tier determination: `production_runner.py` confirmed at `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` line 106 (added by Epic 35 Story 35.0; the manifest comment itself states "No pack_version / schema_version bump: the rendered pack is byte-identical"). This change is runtime run-summary EMISSION only — no pack/step/manifest-schema change → **Tier-1 connective-tissue, dev-agent authority under the block-mode hook, NO pack version bump**. No Tier-2/3 trigger present.
- RED proof: all 23 new fence_state tests failed pre-implementation; critically `test_no_scorecard_doc_read_during_emit` failed `assert 1 == 0`, proving the OLD emit path read the governance doc (`_quality_scorecard_ref` → `did_score_ref` fired the spy). Post-fix it is GREEN (0 doc reads).
- Baseline stash-verify: the 2 `test_run_summary_yaml_emit` failures AND the 3 `test_front_door_selection_threading` failures are the SAME pre-existing Epic-41 `PreflightGateFailed: hud-server-healthz=fail, openai=fail` abort (upstream of the emit); identical with my production change stashed. Unchanged by this story.

### Completion Notes List

- **AC1** — `fence_state` block built inside the single shared `_emit_run_summary_yaml` (all 5 emit sites / both walks inherit structurally, GL-5). Fields: `fences_enabled {fidelity, coverage, udac}` (fidelity via deferred `from app.specialists.irene.graph import narration_figure_fidelity_active`; coverage/udac via already-imported wirings), `silent_bypass_events` (honest — see AC2), `hil_allowlist_empty` (deferred import of `hil_tabular_projector.KNOWN_UNRENDERED_ALLOWLIST`), `pack_hash_binding`/`conversation_chain_digest` (computed ONCE into locals and referenced, not recomputed), `cost_posture`.
- **AC2 / GL-8 — silent_bypass detector decision: SENTINEL `"undetected"` (not a real ledger).** Rationale: Epic-41's fail-loud (`GateBypassError`) makes the silent-specialist-skip class zero-by-construction on any *completed* run_summary, but that is only ONE class; the Path-Z §05/§05B skip and other classes have NO run-scoped counter today. A completed run therefore cannot honestly claim `0` across all classes → the honest *aggregate* emission is `"undetected"`. The param `silent_bypass_events: int = 0` was changed to `int | None = None` so it is now a detector SIGNAL: an explicit int is a real detected count (seed a synthetic bypass → reported verbatim; a genuine `0` only when a detector actually ran), `None` (no caller sets it) → `"undetected"`. The debug-log now fires only on a real non-zero detection (backwards-compatible; `test_nonzero_...` still passes). The dishonest hardcoded top-level `silent_bypass_events: 0` payload key was REMOVED (honest value lives only in `fence_state`).
- **AC3 / GL-4** — `"quality_scorecard": _quality_scorecard_ref()` replaced with a STATIC breadcrumb dict `{"source": "docs/quality/project-quality-scorecard.md", "note": "project-level-not-this-run"}`. The `_quality_scorecard_ref()` doc-reading helper was DELETED (Q1.4a owns it per Q1.1 T1 note); the runtime run-summary no longer parses the governance doc at all. NOTE (out-of-scope, cannot edit `app/quality/scorecard.py`): its `did_score_ref` docstring at `:115` still names `production_runner._quality_scorecard_ref` as a live consumer — now stale; flag for a future doc pass.
- **AC4** — Structural via the shared emitter; parametrized both-walks test (early-reject/no-composed-manifest + start-walk/with-selection) both emit `fence_state`.
- **AC5** — env-truth parametrized matrix (5 fence combos) + allowlist monkeypatch; `fences_enabled` mirrors the flags exactly.
- **AC6 / NFR1** — Fail-soft PER FIELD (Q1.1 learning): each gate/allowlist/economics read independently guarded → one failure degrades ONE field to an honest marker (`"unavailable"`/`"undetected"`) while neighbours stay truthful; plus a belt-and-suspenders outer guard on `_build_fence_state`. Five force-raise tests confirm the emit never raises and always writes well-formed YAML.
- **AC7** — 23 hermetic direct-emit test cases (16 functions) in `tests/integration/marcus/test_run_summary_fence_state.py`; updated the one direct-emit sibling assertion in `test_marcus_duality_boundary.py` (top-level `silent_bypass_events` → `fence_state.silent_bypass_events == "undetected"`). R2 fence_state witness obligation (GL-10) filed to `_bmad-output/maps/deferred-work.md` §"Q1.4a R2 fence_state witness obligation". No live trial run.
- **cost_posture spec vs reality:** the story approximated the vocabulary as `exact/estimated/unavailable`, but `TrialEconomicsReport.cost_posture` is actually `Literal["exact", "known-lower-bound-with-explicit-unavailable-attempts"]`. I surface the REAL field value verbatim (honesty over the approximate spec vocab), fail-soft to `"unavailable"` when the run's `cost-report.json` does not resolve — reusing the SAME persisted artifact + model `_operator_surface_cost_reading` reads (GL-15, no parallel economics plumbing; mirrors the seam's mid-write transaction guard).
- **Verification:** new+sibling tests 27 passed; ruff clean on all touched files; import-linter **18 kept, 0 broken** (deferred local imports kept the module graph unchanged); the 2 named + 3 sibling baseline preflight failures unchanged (stash-verified). Status left `ready-for-dev` and no commit per dispatch instruction.
- **Scope-fence temptations declined:** did not build the Q1.4b projector, did not add `app/quality` signal readers (Q1.2), did not add honesty-pin ratchets (Q1.3), did not touch the scorecard doc or DID score (Q1.5). No operator-facing rendering beyond the YAML. (One granted scope-fence EXCEPTION: FIX-D docstring-only wording fix at `app/quality/scorecard.py:115` — no code/logic change.)

### Code-review fixes (post 3-layer review, no BLOCKER; RED-first where testable)

- **FIX-C (MED, AC6 always-write):** wrapped the two compute-for-emit calls (`_pack_hash_binding`, `_conversation_chain_digest`) in the emitter in try/except → on raise (reject/resume paths force a LIVE compose / `directive.yaml` read that can fail) the value degrades to `"unavailable"` in BOTH the top-level key AND the fence_state reference, and the emit still writes a well-formed file. `_pack_hash_binding`'s own behavior unchanged. RED proof: `test_fail_soft_pack_hash_binding_still_writes` / `_conversation_chain_digest_still_writes` raised (aborting emit, no file) pre-fix → green after (file written, value `"unavailable"` both places).
- **FIX-B (LOW-MED, honesty):** `_fence_fences_enabled` now degrades a non-bool gate return to `"unavailable"` (`v if isinstance(v, bool) else "unavailable"`) instead of `bool()`-coercing (None→False would report a fence definitely-OFF when truth is unknown). RED proof: `test_fences_enabled_non_bool_return_is_unavailable[None/off/1/obj]` failed pre-fix (coerced) → green.
- **FIX-A (LOW, detector honesty):** negative int signal floored to `"undetected"`; debug-log guard made consistent (`int and not bool and > 0`) so a bool/negative signal is not logged as "expected 0, got …". RED proof: `test_silent_bypass_negative_floored_to_undetected` + `test_silent_bypass_bool_signal_is_undetected_and_not_logged` failed pre-fix → green.
- **FIX-F (LOW, GL-15):** extracted the mid-write transaction-guard filename to one shared module constant `_COST_REPORT_TRANSACTION_FILENAME`, used by both `_operator_surface_cost_reading` and `_fence_cost_posture` (rename can't desync them). Read logic not merged (minimal).
- **FIX-E (HIGH, stale assertion):** migrated `test_run_summary_yaml_emit.py:97` (`payload["silent_bypass_events"] == 0`) to the fence_state location, matching the sibling. NOTE: this assertion lives inside `test_clean_trial_run_summary_populated`, a pre-existing Epic-41 preflight-abort test — it aborts before reaching the assertion, so the migrated line does not execute today but is now correct for when the preflight issue is resolved. Did NOT fix the preflight failure.
- **FIX-D (LOW, doc-drift):** corrected the now-stale `app/quality/scorecard.py:115` docstring (removed `production_runner._quality_scorecard_ref` as a live consumer; the runtime run-summary is decoupled, only the CLI remains). Docstring-only.
- **FIX-G (operator docs):** updated the run_summary shape references in `docs/conversational-gates/g1-`, `g2c-`, `g3-`, `g4-operator-reference.md` (line 75 in each) — `silent_bypass_events` now under `fence_state` (honest `"undetected"`, not a hardcoded `0`); `quality_scorecard` now a static breadcrumb. (No `quality_scorecard` object was documented in that dir; only the 4 `silent_bypass_events` lines existed.)
- **DEFER filed:** added a `[Defer][Q1.4a-DETECTOR]` line to `deferred-work.md` — wire a REAL cross-walk silent-bypass detector (today `"undetected"` on 100% of real runs); distinct from the R2 witness entry.
- **Re-verify:** fence suite + duality **35 passed**; ruff clean on all touched files; import-linter **18 kept, 0 broken**; the 2 pre-existing preflight failures unchanged (`test_nonzero_...` still passes). Status left `ready-for-dev`; no commit.

### File List

- `app/marcus/orchestrator/production_runner.py` (modified) — deleted `_quality_scorecard_ref`; added `_QUALITY_SCORECARD_BREADCRUMB`, `_detect_silent_bypass_events`, `_fence_fences_enabled`, `_fence_hil_allowlist_empty`, `_fence_cost_posture`, `_build_fence_state`; rewired `_emit_run_summary_yaml` (param `silent_bypass_events: int | None`, fence_state wiring, static breadcrumb, top-level silent_bypass_events removed).
- `tests/integration/marcus/test_run_summary_fence_state.py` (new) — 23 hermetic direct-emit test cases / 16 functions (AC1–AC7).
- `tests/integration/marcus/test_marcus_duality_boundary.py` (modified) — updated the direct-emit sibling's silent_bypass assertion to the fence_state honest location.
- `_bmad-output/maps/deferred-work.md` (modified) — filed the R2 fence_state witness obligation (GL-10) + the real-detector DEFER (Q1.4a-DETECTOR).
- `app/quality/scorecard.py` (modified, docstring-only — FIX-D scope-fence exception) — corrected the stale `did_score_ref` consumer note.
- `tests/integration/marcus/test_run_summary_yaml_emit.py` (modified — FIX-E) — migrated the stale top-level `silent_bypass_events` assertion to the fence_state location.
- `docs/conversational-gates/g1-operator-reference.md`, `g2c-operator-reference.md`, `g3-operator-reference.md`, `g4-operator-reference.md` (modified — FIX-G) — updated run_summary shape references.
- `_bmad-output/implementation-artifacts/q1-4a-fence-state-run-summary-silent-bypass-detector.md` (modified) — task checkboxes + Dev Agent Record.
