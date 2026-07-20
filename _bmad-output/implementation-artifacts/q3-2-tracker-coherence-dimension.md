---
baseline_commit: 5e5ca1b1
---

# Story Q3.2: Governance / tracker-coherence dimension

Status: ready-for-dev

<!-- Epic Q3 (Partial + report-only siblings). DISPATCH #2 of Q3 (serial after Q3.1). Source epic: epics-project-quality-scorecard-2026-07-19.md. Follows the Q1 engine + all sibling learnings. ⚠️ GL-7 BINDING: Q3.2 must NOT ship pin-less — this story takes the FULLY-COMPUTED option (no hand-authored judgment level; the coherence level derives entirely from a real divergence signal) + a structural test asserting no judgment field + a seeded-divergence pin. -->

## Story

As **the project quality scorecard**,
I want **a Governance/tracker-coherence dimension that measures believed-green in EITHER direction across the project's status trackers (SOTA §11 / sprint-status / deferred-inventory), scored ENTIRELY from a real divergence signal**,
so that **the operator sees an honest, non-hand-waved read of whether the trackers agree — and the coherence score cannot rise while the trackers actually diverge.**

## Scope fence (read FIRST)

Q3.2 adds ONE new dimension (`tracker_coherence`) reusing the Q1 engine. It does **NOT**:

- **Touch DID / cost / coverage / fidelity / capability** (all done) — read-only.
- **Change the trackers or their tooling** — CONSUME `progress_map.qualify_sources()`, `doc_drift_monitor`, and read SOTA §11 / sprint-status / deferred-inventory read-only. NO parallel plumbing (GL-15).
- **Measure the scorecard's OWN internal coherence** (machine block ↔ history ↔ registry) — that is already pinned by Q1.3 (mirror, leak-identity). Q3.2 measures the EXTERNAL status-tracker coherence (avoid the self-referential recursion).
- **Touch Q3.3/Q3.4** — tracker_coherence only.
- **Add module-scope `app.*` to `app/quality`** (GL-3 — progress_map/doc_drift are `scripts.*`, not `app.*`, but keep module scope stdlib+yaml; deferred/local import if needed); **wire into production_runner** (E2E rides R2, GL-10).
- Extend the Q1 machinery **only additively**.

## GL-7 — the FULLY-COMPUTED declaration (binding)

Q3.2 is **fully-computed**: every criterion's level derives ENTIRELY from a real divergence signal — there is **NO hand-authored judgment level** on this dimension (all criteria `derivation: signal-derived`; none `judgment`/`judgment-with-evidence`). This is the honest choice for a *coherence* dimension (a hand-judged coherence score would be believed-green in the very dimension that scores believed-green). GL-7 requires either a real machine-vs-prose pin OR this fully-computed declaration + a test asserting no judgment field — **Q3.2 does BOTH** (fully-computed AND the seeded-divergence pin).

## Honest baseline (verified)

- **`progress_map.qualify_sources()`** (`scripts/utilities/progress_map.py:377`) already reconciles/qualifies the trackers (`_qualify_sprint_status`, `_qualify_markdown` against expected headings, epic/story parsing) and returns divergence findings — the divergence signal source.
- **`doc_drift_monitor.check_documentation_drift()`** (`scripts/utilities/doc_drift_monitor.py:19`) — git-based code-changed-without-doc drift check.
- The three trackers: `docs/STATE-OF-THE-APP.md` §11, `_bmad-output/implementation-artifacts/sprint-status.yaml`, `_bmad-output/planning-artifacts/deferred-inventory.md`. **NOTE:** the prior session's status-surface consolidation made these largely coherent (3 authored SSOTs + generated views) — so the tracker-coherence may be relatively HIGH today (few divergences). **That is fine:** a dimension may be honestly strong if reality is coherent; the GL-7 concern is that it be PINNED (not believed-green), NOT that it must carry a leak. Measure honestly; if `qualify_sources` surfaces real divergences today, those are the coherence leaks.

## Acceptance Criteria

**AC1 — New `## Dimension 6 — Governance / tracker-coherence` section + machine-block entry**, mirroring the prior dimensions (why-load-bearing → rubric → assessment table → ranked leaks → cadence). Machine block gains a `tracker_coherence` dimension with the full field-set. Band+leaks+trend. **Every criterion `derivation: signal-derived` (fully-computed; GL-7).**

**AC2 — Signal readers (fail-soft, read-only, clean-leaf) that produce a REAL divergence measurement:**
- **TC1 tracker-divergence (SIGNAL-DERIVED):** consume `progress_map.qualify_sources()` → the count/severity of divergence findings across SOTA §11 / sprint-status / deferred-inventory. The level is a function of the divergence (0 divergences → strong/coherent; divergences → lower, per a documented rubric). Apply the CV2/FT2/Q3.1 lesson: consult the REAL divergence findings, not mere tracker presence; nothing-actually-checked (qualify_sources unavailable) → `unavailable`, never coherent.
- **TC2 doc-drift (SIGNAL-DERIVED):** consume `doc_drift_monitor` (or an equivalent code↔doc drift signal) as a secondary coherence signal (fail-soft; a git-unavailable state → unavailable, not clean).
- Fully-computed: `level_from_signal` returns a real level for EVERY tracker_coherence criterion (no `None`/judgment).

**AC3 — GL-7 pins (BOTH the fully-computed test AND the divergence pin).** Register a `tracker_coherence` pin in `_HONESTY_PIN_REGISTRY` + add `tracker_coherence` to `_EXPECTED_CANONICAL_DIMENSION_KEYS` + the TC readers to `_SIGNAL_DERIVED_READERS`. Two pins:
- **(a) fully-computed structural pin** — assert NO tracker_coherence criterion carries a `judgment`/`judgment-with-evidence` derivation or a hand-authored level (every level == `level_from_signal(reader())`); a hand-edited coherence level that doesn't match the divergence signal → RED.
- **(b) seeded-divergence pin (the epic AC)** — a seeded THREE-tracker disagreement (fixture SOTA/sprint/inventory that disagree) drops the score: the coherence level computed from the seeded-divergent fixture is lower than the coherent-fixture level. RED-under-seeded: claim coherent while the (fixture) trackers diverge → RED.

**AC4 — GL-13 leak registration + cross-dimensional integration.** IF the real trackers diverge today (per `qualify_sources`), register the divergence as a `tracker_coherence` leak (a SIXTH `## Governance/Tracker-Coherence Scorecard Leak Registry` / `trk_leak:` namespace, disjoint from the other five); `len(leaks) == open_leaks`. IF the trackers are coherent today, `open_leaks: 0` + `leaks: []` (and `leak_coverage_gaps` must handle a dimension with `open_leaks: 0` cleanly — confirm no false gap). reconcile-by-identity if any leak. `ranked_project_leaks` aggregates all dims; `leak_coverage_gaps` clean.

**AC5 — Mirror + trend + history.** Append a `tracker_coherence` snapshot to `scorecard-history.jsonl` (mirror pin); trend baseline; projector NO code change.

**AC6 — Tests (hermetic + real) + honest Band.** Divergence signal readers against fixture trackers (coherent set → high; seeded three-tracker disagreement → lower) AND the real trackers; the GL-7 fully-computed pin + the seeded-divergence pin both RED-under-seeded; meta-ratchet green; mirror/arithmetic/leak-identity/coverage all green. **Band honesty:** the band_note states the coherence is FULLY-COMPUTED from the divergence signal (no human judgment) + what today's real divergence count is. **E2E:** deferred to R2 (GL-10 — file the obligation). All prior dims pins + numbers unchanged.

## Tasks / Subtasks
- [x] **T1 — Readiness.** Re-read the scope fence + the GL-7 fully-computed declaration + honest baseline + ALL sibling review learnings (consult-real-signal/nothing-checked→unavailable; isolating pin; band honesty; the `open_leaks: 0` / empty-leaks path — this is the FIRST dimension that may carry zero leaks, so verify leak_coverage_gaps + the leak-count pin handle 0 cleanly) + the 4 Q2-retro action items. Confirm no pipeline-lockstep trigger path edited.
- [x] **T2 — Divergence signal readers** (AC2): TC1 (progress_map.qualify_sources), TC2 (doc_drift); fully-computed; fail-soft; clean leaf.
- [x] **T3 — Rubric + assessment + machine block** (AC1); the divergence→level rubric; all signal-derived.
- [x] **T4 — GL-7 pins** (AC3): fully-computed structural pin + seeded-divergence pin; RED-under-seeded both.
- [x] **T5 — GL-13 leaks** (AC4): trk_leak: registry — 1 divergence exists today (qualify_sources DEGRADED); the 0-leak path is locked in additively (confirmed clean).
- [x] **T6 — History mirror** (AC5) + honest band_note.
- [x] **T7 — Tests + R2 obligation** (AC6).
- [x] **T8 — Verify.** `pytest tests/quality/ -q` (402 passed); ruff clean; import-linter 18/0; clean-leaf green; prior 5 dims unchanged; ALL prior pins green.

## Dev Notes

### Verified tracker seams (GL-15 — reuse read-only)
- `scripts/utilities/progress_map.py`: `qualify_sources()` (:377 — the qualification/divergence entrypoint), `_qualify_sprint_status()` (:205), `_qualify_markdown(filepath, expected_headings)` (:325), `_parse_epics`/`_story_counts`/`_classify_epic`/`_extract_section`/`_extract_last_updated`. Read its return shape to derive the divergence count/severity.
- `scripts/utilities/doc_drift_monitor.py`: `check_documentation_drift(changed_files)` (:19), `get_changed_files()` (:6).
- The three trackers: `docs/STATE-OF-THE-APP.md`, `sprint-status.yaml`, `deferred-inventory.md`.
- These are `scripts.*` (not `app.*`); still, keep `app/quality` module scope stdlib+yaml and use a deferred/local import for `scripts.utilities.progress_map` (the clean-leaf guard forbids module-scope `app.*` — `scripts.*` is not `app.*`, but a deferred import is the safe, consistent pattern and keeps the import graph unchanged).

### GL-7 is THE point of this story
Do not ship a hand-authored coherence level. Every tracker_coherence criterion is `signal-derived`; the fully-computed structural pin asserts no judgment field; the seeded-divergence pin proves the measurement is real. This is the honest resolution of "the coherence dimension must not itself be believed-green."

### The zero-leak case is new — verify the machinery handles it
This may be the FIRST dimension with `open_leaks: 0` (if the trackers are coherent today). Confirm: `leak_coverage_gaps` does NOT flag a dimension with `open_leaks: 0` + no `leaks:` list as a gap (a gap is `open_leaks > 0` AND no leaks list); the leak-count identity pin handles an empty set; `ranked_project_leaks` handles a dimension contributing zero leaks. If the real trackers DO diverge today, register the leak(s) normally.

### Sibling learnings + the 4 Q2 action items + Q3.1 learnings (BINDING)
consult-real-signal (not presence); nothing-checked→unavailable (Q3.1 FIX-3); isolating pin; band honesty; GL-13 registration; reconcile-by-identity; GL-9 RED-under-seeded; R2 witness. Equal-weight kept.

### References
- [Source: epics-project-quality-scorecard-2026-07-19.md#Story Q3.2] + [#GL-7 (binding: not pin-less) / GL-13 / GL-15 / GL-6 / GL-9 / GL-10] + FR11.
- [Source: scripts/utilities/progress_map.py:377 (qualify_sources) · doc_drift_monitor.py:19] — the divergence signals.
- [Source: docs/STATE-OF-THE-APP.md §11 · sprint-status.yaml · deferred-inventory.md] — the three trackers.
- [Source: q3-1 + q2.* stories (done) + their review remediations] — the sibling exemplars + ALL learnings.
- [Source: app/quality/{signals,scorecard,history,report}.py · tests/quality/test_scorecard_honesty_pins.py] — the engine + registry to extend.

## Dev Agent Record

### Agent Model Used

Opus 4.8 (1M context) — fresh BMAD dev agent, `bmad-dev-story` workflow, RED-first discipline.

### Debug Log References

- Baseline (HEAD 5e5ca1b1): `pytest tests/quality/ -q` → 346 passed; `lint-imports` → 18 kept / 0 broken.
- Honest measurement of the real trackers (live reads, no mocks):
  - `progress_map.qualify_sources()` → **verdict DEGRADED**, error_count 0, warning_count 1 (the `orphan_stories` warning: 269 `development_status` story keys in `sprint-status.yaml` match no `epic-*` prefix). → TC1 `partial`, `trackers_coherent=False`. A REAL divergence today → the dimension carries ONE leak (NOT the zero-leak case).
  - `doc_drift_monitor.get_changed_files()` over HEAD~1..HEAD → 0 in-scope code changes (docs-only commits) → `drift_detected=False` → TC2 `partial` (HEAD-only heuristic, capped conservative).
- Seeded proofs (all GREEN as RED-under-seeded pins): fully-computed structural pin reds on a judgment relabel + level lie; TC1 inflated-level reds; seeded three-tracker-disagreement (real `qualify_sources` over hermetic fixtures) drops `strong`→`partial`/`weak` and reds a coherent claim; slug-identity reds on a seeded typo; six-namespace disjointness.
- Final: `pytest tests/quality/ -q` → **402 passed**; `tests/integration/marcus/test_run_summary_fence_state.py` → 31 passed; ruff clean (app/quality + tests/quality); `lint-imports` → **18 kept / 0 broken**; clean-leaf green.

### Completion Notes List

- **GL-7 FULLY-COMPUTED (the point):** `tracker_coherence` is the ONLY dimension with NO hand-authored judgment level — BOTH criteria `derivation: signal-derived`, each `level == level_from_signal(reader())`. Shipped BOTH GL-7 pins: (a) the fully-computed structural pin (`test_tracker_coherence_is_fully_computed_no_judgment` + the de-mechanization RED proof — no criterion may carry a judgment derivation) and (a') the seeded-divergence pin (`test_tracker_seeded_divergence_lowers_score` — a seeded three-tracker disagreement, measured by the REAL `qualify_sources` over hermetic fixtures, lowers the computed level; a coherent claim while diverging → RED).
- **Honest measurement (AC2):** TC1 = `tracker_coherence_signal` over the REAL `qualify_sources` verdict (CLEAN→strong / DEGRADED→partial / FAIL→weak / unrunnable→unavailable; consult-real-signal, nothing-checked→unavailable per Q3.1 FIX-3). TC2 = `tracker_doc_drift_signal` over the REAL `get_changed_files` seam (active drift→weak / no-drift→partial capped / git-unavailable→unavailable). The `sys.exit`-ing `check_documentation_drift` is NOT called — only its read-only partition is reused (GL-15). Clean-leaf: both trackers reached via deferred local imports; module scope stays stdlib+yaml+re.
- **Today's honest verdict:** the trackers are DEGRADED (1 real divergence), so the dimension carries ONE governance leak (`open_leaks: 1`), NOT the zero-leak case. Band **C** (Σ 2+2 = 4/8 = 50). band_note states the coherence is FULLY-COMPUTED from the divergence signal (no human judgment) + today's real DEGRADED verdict + the reachable close-path.
- **⚠️ ZERO-LEAK PATH (new, verified):** confirmed the shared machinery ALREADY handles a 0-leak dimension — `leak_coverage_gaps` treats `open_leaks <= 0` as no gap; `ranked_project_leaks` skips an empty `leaks` list; the leak-count identity reconciles `0 == 0`. No machinery change needed; locked it in additively with `test_zero_leak_*` (coverage-gap / ranked / count / registry-empty).
- **GL-13 (AC4):** SIXTH `trk_leak:` namespace (disjoint from the five — `test_six_leak_namespaces_are_disjoint_and_dont_cross_count`); 1 registry entry; `len(leaks) == open_leaks == tracker_leak_count_signal() == 1`; the leak aggregates into the shared ranked list (now 6 dims, 10 leaks) sorting after paid-walk + learner-trust (governance lane).
- **AC5 mirror/trend:** appended the `tracker_coherence` snapshot to `scorecard-history.jsonl` (mirror pin green); `trend: baseline`; projector picks the dimension up with NO code change (`test_projector_renders_tracker_dimension_with_no_code_change`).
- **Scope fence honored:** prior 5 dimensions UNCHANGED (numbers + pins); the only edits to sibling test files were the cross-dimensional aggregate assertions (dimension set 5→6, ranked count 9→10, canonical-keys tuple) — the same additive update every prior sibling made. Did NOT touch the trackers/their tooling, `production_runner`, or Q3.3/Q3.4. Q1 machinery extended additively only.
- **Honesty judgment call (recorded):** the story's prose loosely describes `qualify_sources` as spanning "SOTA §11 / sprint-status / deferred-inventory," but the REAL qualifier spans sprint-status + SESSION-HANDOFF + next-session-start-here (incl. the cross-tracker `next_step_conflict` check). I measured the REAL signal honestly (consume-what-it-actually-checks) rather than forcing the illustrative tracker list; the prose/evidence names the real trackers. TC2 is capped at `partial` mechanically (a HEAD-only git heuristic checks doc-change PRESENCE not correctness — like the C2 proxy it can only downgrade), documented as fail-safe/conservative, not a hidden judgment.
- **R2 witness obligation (GL-10):** the live run-end wiring into `production_runner` + a checkable-comparison witness ride the R2 operator-steered trial (E2E deferred; no `production_runner` edit here — consistent with all prior siblings).

#### Code-review remediation (3-layer review; RED-first)

The reviewer accepted acceptance/GL-7/self-referential-trap but flagged TC2 as mis-designed (per-commit-volatile) + TC1 nondeterminism. Applied all five fixes; re-measured honestly; final numbers below.

- **FIX-A [HIGH — the design fix] — TC2 reframed from volatile per-commit drift → STABLE monitoring/gating POSTURE.** `tracker_doc_drift_signal` no longer runs `git HEAD~1..HEAD` at read time. It now reads the STABLE question every scorecard fence asks: is `doc_drift_monitor` WIRED, and does it GATE production or is it advisory? Honest today: the monitor EXISTS (wired) but is an ADVISORY pre-push hook that never gates a production run (no `gates_production` affordance) → **weak** (the fence-not-gating pattern, like coverage CV1 / fidelity FT1). This removes the read-time git call → no per-commit flapping, no git-unavailable false-clean, no subprocess-hang. Reachable close-path grounded in the real module: a truthy `gates_production` → strong. RED-first: `test_tc2_runs_no_git_at_read_time` monkeypatches `subprocess.run` to RAISE — the reader is unaffected (fails if any git runs); `test_tc2_gating_posture_close_path_is_strong` / `_advisory_posture_is_weak` / `_monitoring_not_wired_is_unavailable` seed the posture axis.
- **FIX-B [MED] — TC1 deterministic (staleness excluded).** TC1 now recomputes a STRUCTURAL verdict from qualify_sources' `findings`, EXCLUDING time-based `staleness`/`last_updated` (`_TIME_BASED_QUALIFY_CHECKS`). A structurally-coherent tracker set no longer flips CLEAN→DEGRADED because time passed. RED-first: `test_tc1_staleness_excluded_is_deterministic` (stale-only == coherent == strong; the raw all-findings verdict still surfaces staleness as evidence).
- **FIX-C [MED] — TC1 verdict↔count reconcile.** A supplied `verdict`/count that contradicts the `findings` tally (e.g. `{verdict: CLEAN, warning_count: 3}`) → `unavailable`, never coherent. RED-first: `test_tc1_verdict_count_contradiction_is_unavailable`.
- **FIX-D [MED] — Band ceiling disclosed + tautological test removed.** (a) With both criteria capping at `strong`(3) mechanically (`level_from_signal` never awards `uniform`/4), max = 6/8 = 75 → **Band B**; disclosed in §6.5/§6.6 + `test_band_ceiling_is_b_disclosed`. (b) Deleted the tautological prefix-mirror test (`test_tc2_prefixes_mirror_doc_drift_monitor`) and the mirrored prefix constants — the reframed TC2 does no partition, so nothing is mirrored.
- **FIX-E [LOW] — TC1 severity documented.** DEGRADED→partial is COARSE-by-design (the `divergence_count` is surfaced as evidence, not scaled into the level); documented in §6.5 + the machine-block note.
- **Re-measured honest state (deterministic):** TC1 = partial (structural DEGRADED — orphan stories; staleness excluded); TC2 = weak (drift monitoring wired but advisory/never-gates). Σ = 2+1 = 3/8 = **38 → Band D** (was C). **open_leaks: 2** (TC1 structural divergence + TC2 advisory-not-gating monitor, both governance); the shared ranked list is now **11**. History snapshot + band_note + deferred-inventory (2 `trk_leak:`) updated to the deterministic values. GL-7 kept (both criteria signal-derived, no judgment); both GL-7 pins + the zero-leak-path + six-namespace disjoint (trk=2) all green.
- **Final results:** `pytest tests/quality/ -q` → **407 passed**; integration fence-state → 31 passed; ruff clean; `lint-imports` → **18 kept / 0 broken**; clean-leaf green; prior 5 dims unchanged.

### File List

- `app/quality/signals.py` (M) — TC1 `tracker_coherence_signal`, TC2 `tracker_doc_drift_signal`, `tracker_leak_count_signal`, the `_level_tc_divergence`/`_level_tc_doc_drift` derivations + `level_from_signal` branches, `_TRACKER_LEAK_LINE_RE` / `_QUALIFY_VERDICTS` / `_DOC_DRIFT_*_PREFIXES`.
- `app/quality/scorecard.py` (M) — `_TRACKER_KEY` + `tracker_coherence` in `_EXPECTED_CANONICAL_DIMENSION_KEYS`.
- `docs/quality/project-quality-scorecard.md` (M) — §Dimension 6 prose (§6.0/§6.5/§6.6/Cadence) + the `tracker_coherence` machine-block entry.
- `docs/quality/scorecard-history.jsonl` (M) — appended the `tracker_coherence` baseline snapshot.
- `_bmad-output/planning-artifacts/deferred-inventory.md` (M) — the `## Governance/Tracker-Coherence Scorecard Leak Registry` + 1 `trk_leak:` entry.
- `tests/quality/test_scorecard_honesty_pins.py` (M) — the registered `tracker_coherence` pins (GL-7 fully-computed structural + seeded-divergence + de-mechanization RED, tracker leak-count + slug identity, six-namespace disjointness, arithmetic) + registry/reader wiring.
- `tests/quality/test_tracker_coherence_dimension.py` (A) — the readers vs fixtures + real repo, fail-soft/nothing-checked paths, level totals, GL-13 interleave, the ZERO-LEAK-PATH lock-in, projector-no-change.
- `tests/quality/test_scorecard_reader.py` · `test_scorecard_final_report.py` · `test_cost_efficiency_dimension.py` · `test_coverage_honesty_dimension.py` · `test_fidelity_trust_dimension.py` · `test_capability_honesty_dimension.py` (M) — cross-dimensional aggregate assertions updated 5→6 dims / 9→10 leaks (additive; prior dims' behavior unchanged).
- `_bmad-output/implementation-artifacts/q3-2-tracker-coherence-dimension.md` (M) — Tasks + Dev Agent Record.
