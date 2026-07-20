---
baseline_commit: 10aff026
---

# Story Q3.3: Lane-discipline / scope-fidelity dimension (score the already-enforced)

Status: ready-for-dev

<!-- Epic Q3 (Partial + report-only siblings). DISPATCH #3 of Q3 (serial after Q3.2). Source epic: epics-project-quality-scorecard-2026-07-19.md. Follows the Q1 engine + ALL sibling learnings + the Q3.2 determinism lesson. ⚠️ GL-16 BINDING: read the import-linter result via the SHIPPED importlinter Python dep/API — NOT the lint-imports CLI on PATH (verify-via-shipped-deps). -->

## Story

As **the project quality scorecard**,
I want **a Lane-discipline dimension that SCORES the already-CI-enforced lane isolation from the live import-linter result (via the shipped dep), with an honesty pin tied to the real pass/fail count**,
so that **the operator sees an honest read of lane/scope discipline — and the score cannot claim clean while an import-linter contract is actually broken.**

## Scope fence (read FIRST)

Q3.3 adds ONE new dimension (`lane_discipline`). It SCORES the already-enforced; it adds **NO new enforcement**. It does **NOT**:

- **Touch the prior 6 dims** (all done) — read-only.
- **Add or change any import-linter contract** or lane-matrix/taxonomy doc — CONSUME them read-only (GL-15). The CI enforcement is unchanged; Q3.3 only scores it.
- **Use the `lint-imports` CLI** (GL-16) — use `importlinter.api` (the shipped Python dep). Read `[tool.importlinter]` from `pyproject.toml` via the API; run/read the contracts programmatically.
- **Touch Q3.4** — lane_discipline only.
- **Add module-scope `app.*` to `app/quality`** (GL-3 — importlinter is a third-party dep, not `app.*`, but keep module scope stdlib+yaml and use a deferred/local import for `importlinter.api`); **wire into production_runner** (E2E rides R2, GL-10).
- Extend the Q1 machinery **only additively**.

## Honest baseline (verified)

- **`importlinter` v2.11** ships `importlinter.api` (`read_configuration`, `use_cases`) — the GL-16 shipped-dep entrypoint (NOT the `lint-imports` CLI). `pyproject.toml [tool.importlinter]` declares **18 contracts** (root_packages=["app"]; Marcus M1/M2, Cora C1, lane-isolation D3/D4, etc.). Today: **18 kept / 0 broken** (verified every Q1/Q2/Q3 story) → lane discipline is genuinely **strong/clean**.
- `docs/lane-matrix.md` + `docs/governance-dimensions-taxonomy.md` are the governance maps (supporting evidence).
- **This is a legitimate persisted-level + honesty-pin (unlike Q3.2's volatile TC2):** import-linter changes only when the import GRAPH changes to break a contract — a REAL lane-discipline regression that SHOULD red the scorecard (the pin firing = the scorecard correctly refusing to claim clean while a contract is broken). Deterministic; not per-commit-volatile.

## Acceptance Criteria

**AC1 — New `## Dimension 7 — Lane-discipline / scope-fidelity` section + machine-block entry**, mirroring the prior dimensions (why-load-bearing → rubric → assessment table → ranked leaks → cadence). Machine block gains a `lane_discipline` dimension with the full field-set. Band+leaks+trend.

**AC2 — Signal reader over the LIVE import-linter (GL-16 shipped dep, fail-soft, read-only, clean-leaf):**
- **LD1 import-linter lane discipline (SIGNAL-DERIVED, mostly-mechanical):** via `importlinter.api` (deferred local import) — `read_configuration()` for the declared contracts + run/read the contracts for kept/broken. The level is a function of broken-count (0 broken → strong; broken > 0 → weak/lower). Apply the Q3.1/Q3.2 lesson: consult the REAL kept/broken result, not the mere contract count; **importlinter unavailable / config missing / the run errors → `unavailable`, never clean** (never report clean lane discipline from a linter that didn't actually run). Deterministic.
- **Performance/fail-soft note:** running the contracts builds the app/ import graph (seconds). Guard it (bounded + fail-soft: on any error/exception → `unavailable`). This is an assessment-cadence read, not a hot loop; note the cost in the §Cadence. (If a future render-time cost is a concern, a persisted-level + pin-re-runs split is the follow-on — but the epic wants the LIVE count, so LD1 reads it.)
- Optionally **LD2 lane-matrix coverage** (judgment-with-evidence): the lane-matrix / taxonomy governance maps exist (supporting evidence). Keep it honest (the maps existing ≠ perfect discipline).

**AC3 — The dimension's own honesty pin (GL-6 meta-ratchet REQUIRES it).** Register a `lane_discipline` pin in `_HONESTY_PIN_REGISTRY` + add `lane_discipline` to `_EXPECTED_CANONICAL_DIMENSION_KEYS` + LD1 to `_SIGNAL_DERIVED_READERS`. The pin is doc↔code: **the score FAILS if it claims clean lane discipline while import-linter reports broken > 0** (the epic's honesty-pin — "ties the score to the live import-linter pass/fail count"). RED-under-seeded (GL-9): a seeded broken-contract result → the LD1 level drops below clean; a block claiming strong while (seeded/fixture) broken > 0 → RED. Apply the isolating-pin lesson (Q2.3 FT2): the pin must consult the REAL kept/broken, not the contract-declared count.

**AC4 — GL-13 leak registration + cross-dimensional integration.** Today import-linter is clean (0 broken) → likely **`open_leaks: 0` + `leaks: []`** (the zero-leak path, now proven handled). IF a real lane-discipline gap exists (e.g. a documented lane-matrix hole, or a contract known-broken), register it (a SEVENTH `## Lane-Discipline Scorecard Leak Registry` / `lane_leak:` namespace, disjoint from the other six). `len(leaks) == open_leaks`; reconcile-by-identity if any leak; `ranked_project_leaks` aggregates all dims; `leak_coverage_gaps` clean (confirm the 0-leak path).

**AC5 — Mirror + trend + history.** Append a `lane_discipline` snapshot to `scorecard-history.jsonl` (mirror pin); trend baseline; projector NO code change.

**AC6 — Tests (hermetic + real) + honest Band.** LD1 against the REAL import-linter (18/0 today → strong) AND a seeded broken-contract fixture (broken > 0 → not clean); the pin RED-under-seeded; the isolating pin; importlinter-unavailable → unavailable; meta-ratchet green; mirror/arithmetic/leak-identity/coverage all green. **Band honesty:** the band_note states the score is the LIVE import-linter result (via the shipped dep, GL-16), deterministic, and reflects the real kept/broken count. **E2E:** deferred to R2 (GL-10 — file the obligation). Prior 6 dims pins + numbers unchanged.

## Tasks / Subtasks
- [x] **T1 — Readiness.** Re-read the scope fence + GL-16 (shipped dep not CLI) + honest baseline + ALL sibling review learnings (consult-real-result/nothing-checked→unavailable; isolating pin; determinism [Q3.2]; band honesty; the 0-leak path) + the 4 Q2-retro action items. Confirm no pipeline-lockstep trigger path edited; do NOT edit any import-linter contract.
- [x] **T2 — LD1 reader** (AC2) via `importlinter.api` (deferred import; kept/broken; fail-soft + bounded; unavailable on error). LD2 lane-matrix consulted as SUPPORTING evidence only (would-be coverage-verifier deferred as a named follow-on to keep the dimension honestly zero-leak).
- [x] **T3 — Rubric + assessment + machine block** (AC1); honest levels (strong today; 0 broken); signal-vs-judgment.
- [x] **T4 — Honesty pin + registry** (AC3); the broken-count pin; RED-under-seeded + isolating.
- [x] **T5 — GL-13 leaks** (AC4): open_leaks:0 + empty leaks (0-leak path confirmed — the SECOND dimension to use it); `lane_leak:` = the SEVENTH namespace, registry section added (zero-leak).
- [x] **T6 — History mirror** (AC5) + honest band_note.
- [x] **T7 — Tests + R2 obligation** (AC6).
- [x] **T8 — Verify.** `pytest tests/quality/ -q` (456 green); ruff clean; import-linter 18/0 (unchanged — did NOT edit contracts); clean-leaf green; prior 6 dims unchanged; ALL prior pins green.

## Dev Notes

### Verified import-linter seams (GL-16 — shipped dep, read-only)
- `importlinter.api` (v2.11): `read_configuration()` (reads `[tool.importlinter]` from pyproject.toml), `use_cases` (runs contracts → a report with kept/broken). Explore the exact API (e.g. `use_cases.create_report(...)` or the report object's kept/broken accessors) — use it programmatically; do NOT shell out to `lint-imports`.
- `pyproject.toml [tool.importlinter]` (:127): root_packages=["app"], 18 contracts.
- `docs/lane-matrix.md`, `docs/governance-dimensions-taxonomy.md` — governance maps.
- Deferred local import for `importlinter.api` (keep `app/quality` module scope stdlib+yaml; importlinter is third-party, not `app.*`, but the deferred pattern is consistent + keeps the import graph unchanged).

### The Q3.2 determinism lesson (relevant, but import-linter PASSES it)
Unlike Q3.2's volatile git-drift, import-linter is deterministic + a legitimate persisted-level signal: it breaks ONLY on a real import-graph regression (a forbidden import), which SHOULD red the scorecard. So LD1 reading the live result is honest + non-flapping (a break is a real lane-discipline regression, correctly red). Still: fail-soft (linter-unavailable → unavailable, never clean); bounded (guard the graph-build cost).

### The zero-leak path is now proven (Q3.2) — this dimension likely uses it
Import-linter is clean today (0 broken) → `open_leaks: 0` + `leaks: []`. The shared machinery handles this (Q3.2 confirmed: `leak_coverage_gaps` treats `open_leaks<=0` as no gap; count reader returns 0; identity reconciles empty). Confirm it holds for a 7th dimension.

### Sibling learnings + the 4 Q2 action items + Q3.1/Q3.2 learnings (BINDING)
consult-real-result (not the declared count); nothing-checked→unavailable; isolating pin; determinism; band honesty; GL-13 registration; reconcile-by-identity (7 namespaces if a leak); GL-9 RED-under-seeded; R2 witness. Equal-weight kept.

### References
- [Source: epics-project-quality-scorecard-2026-07-19.md#Story Q3.3] + [#GL-16 (import-linter via shipped dep) / GL-13 / GL-15 / GL-6 / GL-9 / GL-10] + FR12.
- [Source: importlinter.api (v2.11) · pyproject.toml [tool.importlinter]:127 (18 contracts)] — the GL-16 shipped-dep signal.
- [Source: docs/lane-matrix.md · docs/governance-dimensions-taxonomy.md] — the governance maps.
- [Source: q3-1 + q3-2 + q2.* stories (done) + their review remediations] — the sibling exemplars + ALL learnings (esp. Q3.2 determinism + the zero-leak path).
- [Source: app/quality/{signals,scorecard,history,report}.py · tests/quality/test_scorecard_honesty_pins.py] — the engine + registry to extend.

## Dev Agent Record

### Agent Model Used

Opus 4.8 (1M context) — fresh BMAD dev agent, RED-first, `bmad-dev-story`.

### Debug Log References

- GL-16 shipped-dep flow verified before any code: `importlinter.api.use_cases.read_user_options('pyproject.toml')` → `_register_contract_types(uo)` → `create_report(uo, cache_dir=None)` → `report.kept_count`/`report.broken_count` == **18 / 0**, ~0.4s, in-process (no `lint-imports` CLI, no subprocess). Determinism confirmed (two live reads identical).
- RED-first proofs (all fire): (1) broken-count pin — a seeded `broken>0` report derives `weak`, not the claimed clean level; (2) doc↔code — inflating LD1 to `uniform`/`partial` is caught by `_signal_derived_violations` (`machine-block level != reader-derived 'strong'`); (3) isolating pin — SAME declared total (18) but a broken RESULT drops the level to `weak` (proves consult-real-result, not declared count); (4) `importlinter`-unavailable / could_not_run / 0-0 / malformed → `unavailable`, never clean; (5) meta-ratchet reds if the `lane_discipline` pin registry entry is dropped.
- `subprocess.run` monkeypatched to raise AND `use_cases.lint_imports` monkeypatched to raise → the live reader is UNAFFECTED (proves GL-16: reads via the shipped `create_report`, not the CLI).

### Completion Notes List

- **New dimension 7 `lane_discipline`** — single SIGNAL-DERIVED criterion **LD1** (`import_linter_lane_signal`) over the LIVE import-linter via `importlinter.api` (GL-16, deferred local import; clean-leaf preserved — `app.quality` imports zero `app.*` at module scope, `importlinter` is third-party). Level = f(broken-count): **0 broken → strong** (18/0 today); **broken>0 → weak** (a real forbidden-import regression that SHOULD red the scorecard). Consults the REAL kept/broken RESULT, not the declared 18. Fail-soft + bounded: could_not_run / config-missing / run-error / nothing-checked (`kept+broken==0`) / malformed → `unavailable`, NEVER clean.
- **Honest posture:** Band **B** (LD1 strong = 3/4 = 75). Band ceiling B disclosed (a single signal-derived criterion caps at `strong`/3 — `level_from_signal` never awards uniform/4). **ZERO-LEAK** today (18/0 clean → `open_leaks: 0` + `leaks: []`) — the SECOND dimension to exercise the 0-leak path; cross-dimensional ranked-leak total stays **11** (unchanged). `lane_leak:` is the SEVENTH per-dimension namespace (registry section added to `deferred-inventory.md`, zero tags).
- **LD2 decision:** the lane-matrix / governance-dimensions-taxonomy maps are cited as SUPPORTING evidence only (their existence ≠ proof of exhaustive coverage — "maps existing ≠ perfect discipline"). A lane-matrix↔contract COVERAGE VERIFIER (the would-be LD2, a path toward A) is registered as a NAMED deferred follow-on (`lane-discipline-lane-matrix-contract-coverage-verifier`), NOT scored — keeping the dimension honestly zero-leak and avoiding an unverified-clean award.
- **Registries wired in lockstep:** `_EXPECTED_CANONICAL_DIMENSION_KEYS` += `lane_discipline`; `_SIGNAL_DERIVED_READERS` += `lane_discipline_import_linter`; `_HONESTY_PIN_REGISTRY[_LANE_KEY]` = {broken-count pin, isolating pin, lane leak-count, arithmetic}. Mirror snapshot appended to `scorecard-history.jsonl`; trend `baseline`; projector UNCHANGED (dimension-agnostic — renders the 7th dimension automatically; confirmed by a projector test).
- **Prior 6 dims UNCHANGED** (DID 65/B-, cost 62/B-, cov 58/C, fid 58/C, cap 50/C, tracker 38/D) — read-only; import-linter contracts UNTOUCHED (`pyproject.toml` not modified). **All prior pins green** (signal-derived, leak-count + slug-identity, arithmetic, meta-ratchet, mirror, computed-trend, evidence-gated-upgrade, leak-coverage incl. the 0-leak path).
- **R2 obligation:** LIVE run-end wiring into `production_runner` + a checkable-comparison witness ride the R2 operator-steered trial (GL-10) — the dimension ships the reader + machine block + projector + goldens; no `production_runner` edit here.
- **Verify (post code-review rework):** `pytest tests/quality/ -q` → **462 passed**; ruff clean; import-linter **18 kept / 0 broken** (unchanged, `pyproject.toml` not modified); clean-leaf green; scorecard-consumer integration (`test_run_summary_fence_state.py`) → 31 passed.

### Code-review rework (3-layer review — RED-first, no commit)

Applied all 8 findings:

- **FIX-B [MED, honesty] — coverage-completeness over-claim.** Reframed from 0-leak to **1 leak**: LD1 proves the 18 DECLARED contracts pass, but does NOT verify they COVER every documented lane (`docs/lane-matrix.md`) — a documented lane with no enforcing contract reads 18/0 clean while being a real hole. Registered the coverage-completeness-UNVERIFIED gap as ONE governance `lane_leak: lane-discipline-lane-matrix-contract-coverage-unverified` (DID Leak-4 owed-check precedent) → `open_leaks: 1`, `len(leaks)==open_leaks==count==1`. LD1 stays `strong` (18/0 declared-pass; the leak is a SEPARATE completeness gap), band stays **B**. §7.6 headline + band_note reframed to "declared contracts clean (18/0, live via shipped dep); lane↔contract coverage-completeness UNVERIFIED (1 open gap)". Cross-dimensional ranked total 11→**12**; the 6 sibling aggregate tests updated (prior dimensions' own leaks unchanged). The 0-leak PATH stays machinery-tested via synthetic-block tests.
- **FIX-A [MED] — console side-effects.** `create_report` renders a rich `console.status` + transient `Live` bar; wrapped the build in `redirect_stdout`/`redirect_stderr` sinks + `console.quiet=True` in the MAIN thread spanning the join → NOTHING reaches the terminal. RED/verify: `capsys` around the live read → empty.
- **FIX-E [MED] — hang.** The build now runs in a daemon worker thread joined with a watchdog `_IMPORTLINTER_TIMEOUT_S` (60s; portable — no POSIX `signal.alarm`); a stuck build → `unavailable` within the bound. RED-first: shrink the bound + sleep past it → `unavailable` in ~0.3s, no hang.
- **FIX-F [MED] — hostile report.** Wrapped the injected-report coercion in `try/except → None`; a report whose `.kept_count` property raises → `unavailable`, does not propagate.
- **FIX-C [MED] — private internal.** No public path registers contract types (`configure()` only sets settings; confirmed empirically), so `_register_contract_types` is genuinely required — added a LOUD anti-drift test (`test_importlinter_register_seam_available`) that reds if the seam moves in a future 2.x rather than silently degrading LD1.
- **FIX-D [MED] — brittle pin.** The registered claim pin now `pytest.skip`s (with reason) if the live reader is `unavailable` in this env, and asserts `block level == reader level` (doc↔reader consistency) rather than a hard `== "strong"` literal.
- **FIX-G [LOW] — honest invariant.** The real-repo pin asserts `broken_count == 0` (the honest invariant), not `kept_count == 18` (a 19th clean contract must not red it).
- **FIX-H [LOW] — isolating clarity + coercion.** The isolating pin now feeds a fake `Report` OBJECT (`.kept_count`/`.broken_count`) to the READER (proving the wiring, not just the level fn); the Mapping coercion uses explicit prefer-`kept`-else-`kept_count` (no eager double-`.get`).

### File List

- `app/quality/signals.py` — LD1 reader `import_linter_lane_signal` + `_read_import_linter_report` + `_coerce_count` + `lane_leak_count_signal` (7th `lane_leak:` namespace) + `_level_ld_import_linter` + `level_from_signal` wiring.
- `app/quality/scorecard.py` — `_LANE_KEY` + `_EXPECTED_CANONICAL_DIMENSION_KEYS` += `lane_discipline`.
- `docs/quality/project-quality-scorecard.md` — §Dimension 7 prose (§7.0/§7.5/§7.6/Cadence) + the `lane_discipline` machine-block entry (LD1, open_leaks:0, leaks:[], trend baseline).
- `docs/quality/scorecard-history.jsonl` — appended the `lane_discipline` baseline snapshot (75/B, LD1=3, open_leaks 0).
- `_bmad-output/planning-artifacts/deferred-inventory.md` — `## Lane-Discipline Scorecard Leak Registry` (zero-leak) + the named coverage-verifier follow-on.
- `tests/quality/test_scorecard_honesty_pins.py` — lane registry/readers wired; the 4 registered pins + RED-under-seeded proofs + the 7-namespace disjointness pin.
- `tests/quality/test_lane_discipline_dimension.py` — NEW: LD1 reader (real 18/0 + seeded fixtures + isolating + GL-16-not-CLI + determinism + unavailable), lane leak-count, the 0-leak-path lock-in, GL-13 interleave, projector-no-code-change.
- `tests/quality/test_scorecard_reader.py` — canonical-keys constant updated to 7 dimensions.
- `tests/quality/{test_cost_efficiency,test_coverage_honesty,test_capability_honesty,test_fidelity_trust,test_tracker_coherence}_dimension.py` + `tests/quality/test_scorecard_final_report.py` — cross-dimensional ranked-leak aggregate updated 11→12 + dims set gains `lane_discipline` (post-FIX-B; each prior dimension's OWN leaks unchanged).
