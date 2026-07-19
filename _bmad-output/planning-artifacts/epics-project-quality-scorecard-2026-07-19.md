# Project Quality Scorecard — Epic Breakdown (Epics Q1–Q3)

**Status:** `green-lit-with-amendments — pending operator ratification` (2026-07-19). Design party (Winston/Murat/John/Mary) + landscape survey authored it; the `bmad-party-mode` green-light (Winston/John/Murat/Amelia) returned **4/4 GO-WITH-AMENDMENTS** (see the BINDING `## Green-light amendments` section at the bottom — GL-1…GL-16). Per sprint governance: `bmad-code-review` precedes any story `done`. Class-S substrate (touches `production_runner` run-summary emission + a new `app/quality/` package). **Dev does not open until the operator ratifies.**

## Overview

A recurring, **project-specific** quality assessment scored on dimensions that matter for *this* project — not generic code metrics. Emitted into every production run's final report and refreshed regularly during development. The flagship + first dimension is **Dynamic Intelligence vs Determinism (DID)**; this pass ("everything") also stands up the full candidate set the survey surfaced.

**A strawman baseline exists** (branch `dev/quality-scorecard-epic-2026-07-19`, commit `4e8b9ed7`): `app/quality/scorecard.py` (fail-soft reader), `docs/quality/project-quality-scorecard.md` (prose + versioned machine block + `dimensions` container), `scripts/utilities/quality_scorecard.py` (CLI + `--check`), and a `run_summary.yaml` field. Its **bones are keepers** (fail-soft reader, versioned schema, dimensions container, CLI); the epic **reworks the content + integration** per the binding consensus below. The strawman's run-summary *stamp* and hand-transcribed judgment block are explicitly REPLACED.

> **⛔ BINDING DESIGN CONSENSUS (governs on conflict).** These are the ratified party rules; story bodies elaborate them but must not weaken them:
> 1. **Runs emit per-run mechanical FACTS, not the project grade.** `run_summary.yaml` carries a `fence_state` block derived from signals that already flow; the scorecard reference is a dated breadcrumb *pointer* labeled project-level-not-this-run. A run must never stamp a project score it cannot prove.
> 2. **The scorecard honors its own fence.** Each criterion = `{judged level + computed signal + evidence_ref}`. Humans author only genuine judgment (DID C1 neck-placement; calibration *magnitude*); C2/C3/C4/leak-count DERIVE from real signals (env gates on `--preset production`; a manifest bone-inventory; digest-bindings; `did_leak:`-tagged deferred-inventory entries). *Determinism-pretending-to-be-intelligence in the tool that scores it is a failure.*
> 3. **Anti-believed-green = machine-vs-prose honesty-pin TESTS** that FAIL when the doc disagrees with the code, reusing the Epic-43 RED-first ratchet pattern (`tests/marcus/cli/test_projector_coverage_ratchet_43_10.py`). Score *increases* must cite earned evidence; downgrades are free. `as_of` (prose edited) is split from `as_verified` (evidence re-checked). The CLI staleness `--check` is a secondary nag, not the guard.
> 4. **Report Band + ranked-leaks + trend arrow — NOT a false-precise `/100`.** Per-criterion 0–4 levels stay in the doc as the reasoning trace.
> 5. **Reproducibility:** each criterion needs an enumerated per-node checklist; DID C1 needs a re-checkable artifact; the mis-cited reading-path number is corrected (0.071 was the built-classifier dry-run — the **fresh naive holdout is OWED/unmeasured**, never implied measured); motion-tier "likely stale" → a verification TODO.

**Harmonization (do NOT duplicate existing reporting):** the scorecard doc `docs/quality/project-quality-scorecard.md` is the HOME. `docs/STATE-OF-THE-APP.md` §4 (BETA capability scorecard) and §11.5 (progress estimate) are COMPLEMENTARY — they answer "how far along?"; the scorecard answers "how healthy on load-bearing dimensions?" — **cross-reference, never merge.** Per-run views REUSE existing emitters (`run_summary.yaml`, the fence-enable flags, `economics.py` drift/`cost_posture`, HUD `HealthTile`) — no parallel plumbing.

**⚙️ TESTING DOCTRINE (operator-mandated — in EVERY story's AC; the measure must be VERY reliable):**
- **Component + run-segment level:** live-test every signal reader, honesty-pin ratchet, and the fail-soft reader in isolation (hermetic where possible; real live calls only where a signal genuinely needs them, per the no-mocks posture).
- **Full E2E:** run economically where cheap, otherwise **defer to the upcoming Operator/HIL R2 trial** — the quality reporting rides that trial as part of the shakedown (plan a witness capture of the run-summary `fence_state` + the final-report projection from R2).
- **Every dimension carries its own honesty-pin ratchet test** (its score cannot rise while the code contradicts it). Verify via shipped deps, not operator-only CLIs.

## Requirements Inventory

### FR Coverage Map

| Requirement | Epic / Story |
|---|---|
| FR1 — project quality scorecard, dimensions that matter for this project; in every run report + refreshed in dev | Q1.1, Q1.4, Q1.5 |
| FR2 — runs emit per-run `fence_state` FACTS (not the grade); scorecard ref = dated breadcrumb pointer | Q1.4 |
| FR3 — per-criterion `{level + signal + evidence_ref}`; judgment only where it earns; rest derived from signals | Q1.2 |
| FR4 — machine-vs-prose honesty-pin ratchets (fence-claim, leak-count, arithmetic); evidence-gated upgrades; `as_of`/`as_verified` split | Q1.3 |
| FR5 — report Band + ranked-leaks + trend arrow; per-criterion 0–4 as reasoning trace | Q1.5, Q1.4 |
| FR6 — DID dimension reauthored (enumerated checklists; corrected evidence incl. fresh-holdout OWED; re-checkable C1; motion TODO) | Q1.5 |
| FR7 — Cost-efficiency dimension (economics drift/`cost_posture`/budget-stop) | Q2.1 |
| FR8 — Coverage-honesty dimension (`CoverageReceipt` PASS/FAIL/vacuous) | Q2.2 |
| FR9 — Fidelity-trust dimension (Vera trace, `source_fidelity_audit`; WARN-only/OFF gap) | Q2.3 |
| FR10 — Capability-honesty dimension + auto-reconciliation (bundle tiers vs produced reality) | Q3.1 |
| FR11 — Governance/tracker-coherence dimension (progress_map, doc_drift, deferred-inventory) | Q3.2 |
| FR12 — Lane-discipline / scope-fidelity dimension (import-linter, lane-matrix — already enforced, unscored) | Q3.3 |
| FR13 — Calibration dimension, REPORT-ONLY (surfaces owed/unmeasured; does NOT build the holdout harness) | Q3.4 |
| NFR1 — fail-soft: a scorecard read NEVER raises into a production run | Q1.1, Q1.4 |
| NFR2 — reliability: heavy test mandate per the doctrine; honesty-pin ratchet per dimension | ALL |
| NFR3 — reuse existing emitters; no parallel plumbing; harmonize (cross-ref) with SOTA §4/§11.5 | Q1.4, Q1.5 |
| NFR4 — additive-within-schema; generalize the reader off the hard-coded DID key; `rubric_version` per dimension | Q1.1 |

## Epic List

- **Epic Q1 — Scorecard Engine + DID Reframe (FOUNDATION).** The shared machinery done right (schema v2, generalized reader, `{level+signal+evidence_ref}` criterion model, honesty-pin ratchet framework, per-run `fence_state`, final-report projector) + the flagship DID dimension reauthored honestly. **Hard dependency for Q2/Q3.**
- **Epic Q2 — Ready siblings.** Cost-efficiency, Coverage-honesty, Fidelity-trust — each already emits per-run signals; each = rubric + score + signal readers + honesty-pin, reusing the Q1 engine.
- **Epic Q3 — Partial + report-only siblings.** Capability-honesty (auto-reconciliation), Governance/tracker-coherence, Lane-discipline (score the already-enforced), Calibration (report-only honesty of the owed holdout).

**Cross-epic ordering:** **Q1 first and complete** (the engine + honesty-pin framework everything reuses) → Q2 ready siblings (parallelizable once Q1 lands) → Q3 partial/report-only. Any two stories touching `app/quality/scorecard.py`, the scorecard doc's machine block, or the `run_summary` payload serialize by rule. **Phasing flag:** if Q3's calibration or capability-honesty auto-reconciliation over-balloons, split it to a follow-on epic — the scorecard's job is to REPORT those honestly, not to build their underlying harnesses.

---

## Epic Q1: Scorecard Engine + DID Reframe (FOUNDATION)

### Story Q1.1: Scorecard schema v2 + generalized reader + versioning

**As** the quality-reporting substrate, **I need** a versioned, dimension-agnostic schema + a fail-soft generalized reader **so that** any dimension slots in without editing the reader and stale/incompatible rubrics can't be silently compared.

**Acceptance Criteria:**
- Machine block bumped to `quality-scorecard/v2`: each dimension carries `rubric_version`, `as_of` (prose last-edited), and `as_verified` (evidence last-re-checked); criteria carry `{level, signal, evidence_ref}` (signal nullable where genuinely judgment).
- `app/quality/scorecard.py` reader generalized off the hard-coded `_DID_KEY` → `dimension_ref(key)` + a `did_score_ref()` convenience wrapper; reader stays **fail-soft** (missing/malformed/non-mapping → `{"status":"unavailable"}`, NEVER raises) and stdlib+yaml-only (clean importable leaf).
- Prose owns meaning/basis; the machine block owns numbers; a check asserts one-prose-row-per-yaml-criterion and vice-versa (no silent drift).
- **Test (component):** parametrized reader fail-soft (missing file · bad yaml · non-mapping · marker-absent → unavailable, never raises); schema-round-trip; `rubric_version`/`as_verified` present. Hermetic.

### Story Q1.2: Per-criterion signal readers (judgment vs computed line)

**As** the DID dimension, **I need** the mechanically-checkable criteria backed by real signals **so that** a human cannot hand-score what the code already knows.

**Acceptance Criteria:**
- Signal readers implemented (fail-soft, read-only): **C3** — fences-enabled on `--preset production` from `narration_figure_fidelity_active()` / `coverage_gate_wiring` / `udac_wiring` (binary "wired into the production preset?"); **C2** — manifest bone-inventory (count `model_config_ref: null` render/assemble/publish nodes; assert no LLM ref in the compose/render/publish band, naming the roster); **C4** — digest-binding presence + `silent_bypass_events` (consumes Q1.4's real detector); **leak-count** — count of `did_leak:`-tagged open deferred-inventory entries.
- Rule enforced in design + test: **if a criterion has a signal, the human MUST NOT hand-assign its level** — the level is a function of the signal; the human authors only C1 (neck-placement, with a re-checkable artifact) and the calibration *magnitude*.
- **Test (component):** each signal reader against fixture + real repo state; monkeypatch each env gate on/off → asserted fences-enabled dict matches (signal can't drift from the flag).

### Story Q1.3: Honesty-pin ratchet framework (anti-believed-green)

**As** the project, **I need** tests that fail when the scorecard's claims contradict the code **so that** the score cannot quietly lie in either direction.

**Acceptance Criteria:**
- `tests/quality/test_scorecard_honesty_pins.py` (RED-first, reusing the 43-10 ratchet pattern): **(a) fence-claim consistency** — a criterion claiming a fence ON-by-default fails unless the env-gate default is truthy; **(b) leak-count reconciliation** — `open_leaks` must equal the count of `did_leak:`-tagged deferred entries; **(c) score-arithmetic pin** — band matches the boundary table; per-criterion levels are internally consistent.
- **Evidence-gated upgrade guard:** any score/level *increase* must cite a closed-leak / turned-on-fence `evidence_ref`; downgrades free. `trend` is a computed delta vs a small stored history, not free-text.
- CLI `--check` demoted to a secondary staleness nag (keep, but it is not the honesty guard).
- **Test (component):** the pins genuinely go RED under a seeded dishonest edit (bump C3 without flipping the flag → red; strike a `did_leak:` entry without updating count → red; fat-finger the band → red). This is the heart of the reliability mandate.

### Story Q1.4: Per-run `fence_state` in run_summary + fix `silent_bypass_events` + final-report projector

**As** the operator at a paid-run gate, **I need** this run's actual fence facts (not a project average) **so that** a regression shows up where it happened.

**Acceptance Criteria:**
- `run_summary.yaml` gains a `fence_state` block of per-run FACTS: `fences_enabled {fidelity, coverage, udac}`, `silent_bypass_events`, `hil_allowlist_empty`, `pack_hash_binding`/`conversation_chain_digest` refs, `cost_posture` (reused from economics). Emitted through `_emit_run_summary_yaml` (no parallel file).
- **`silent_bypass_events` fixed (precondition):** wired to a REAL detector, OR honestly emitted as `undetected` (never a dishonest `0`). An honest "we didn't check" beats a false clean.
- The stamped project score is REMOVED from `run_summary`; replaced by a dated breadcrumb `quality_scorecard: {source, as_of, note: project-level-not-this-run}`. Fail-soft preserved (`{"status":"unavailable"}` on any error; a run never fails over this).
- A deterministic **final-report projector** renders Band + ranked-leaks + trend + this-run `fence_state` (reusing Epic-43 tabular-projector discipline where it presents to the operator).
- **Test:** `test_run_summary_yaml_emit` extended (field present; unavailable-path carries the marker, never absent/raising); `fence_state` reflects env truth (monkeypatch); projector golden. **E2E:** witness the `fence_state` + projection on the R2 trial.

### Story Q1.5: DID dimension — reauthored honestly (band + leaks + trend)

**As** the flagship dimension, **I need** the DID assessment rebuilt to the consensus **so that** it is evidence-reproducible, not a well-argued vibe.

**Acceptance Criteria:**
- DID re-scored with each criterion carrying `{level, signal, evidence_ref}` + an **enumerated per-node checklist** (C2 bone roster; C3 binary preset-fenced); C1 cites a **re-checkable artifact** (e.g. the neck→digest-binding set), not a bare architectural assertion.
- Reported as **Band + ranked-leak-list + trend arrow** (no headline `/100`); per-criterion 0–4 kept as the reasoning trace.
- **Evidence corrections applied (Mary):** the reading-path number is fixed — 0.071 was the built-classifier dry-run; the **fresh naive holdout is OWED/unmeasured** (flagged as such, a single pinned metric+dataset+commit for what *was* run); motion capability-tier "likely stale" → an explicit verification TODO, not a claimed leak.
- The 5 DID leaks are tagged `did_leak:` in `deferred-inventory.md` so Q1.3's reconciliation pins them.
- **Test:** the honesty pins (Q1.3) pass by AGREEING WITH REALITY today (C3 "weak/OFF" matches the real default-OFF flags); a golden of the rendered DID section.

---

## Epic Q2: Ready siblings (reuse the Q1 engine)

*Each story: a new `##` dimension section in the scorecard doc + machine-block entry + signal readers over EXISTING emitters + its own honesty-pin ratchet + rubric. No new per-run plumbing beyond reading what already flows.*

### Story Q2.1: Cost-efficiency / paid-walk discipline dimension

**Acceptance Criteria:** rubric + criteria scored from `economics.py` signals (`cost_posture` exact/estimated/unavailable, per-agent `drift_alerts` vs rolling median, `MARCUS_TRIAL_BUDGET_USD` budget-stop posture); per-run `fence_state` gains a cost-posture fact if not already present; honesty-pin (a claimed "cost-fenced" level fails if the budget-stop is not wired). **Test:** signal readers hermetic; drift math pinned; E2E cost-posture witnessed on R2.

### Story Q2.2: Coverage-honesty dimension

**Acceptance Criteria:** rubric + criteria from `CoverageReceipt` (PASS/FAIL/PASS-vacuous, narration-obligation-unmet); scores the **default-OFF gap** honestly (coverage gate exists but off on the production preset = a leak, not a pass); honesty-pin ties the score to the real `coverage_gate_active()` default. **Test:** receipt-shape signal readers hermetic; the default-OFF pin goes red if someone claims coverage-fenced without the wiring.

### Story Q2.3: Fidelity-trust dimension (source→output faithfulness)

**Acceptance Criteria:** rubric + criteria from the Vera fidelity trace (Omissions/Inventions/Alterations) + `source_fidelity_audit` (`SEMANTIC_TRIPWIRE.gates_production`); the **WARN-only / default-OFF posture IS the measured gap** (a WARN that never gates = capped level); honesty-pin fails if the score claims "gating" while `gates_production: False`. **Test:** the `gates_production` boolean pin; trace-shape readers hermetic; fidelity witnessed on R2.

---

## Epic Q3: Partial + report-only siblings

### Story Q3.1: Capability-honesty dimension (declared vs produced) + auto-reconciliation

**Acceptance Criteria:** a dimension scoring whether front-door capability tiers (`bundle_catalog.py`) match produced reality; an **auto-reconciliation check** that flags a tier claiming `mechanism_only_never_produced` when a produced artifact exists (the DID Leak-5 pattern — workbook produced but tier stale); honesty-pin ties the score to the reconciliation result. **Test:** reconciliation against fixture tiers + a produced-artifact signal; red when a stale tier is seeded. **Phasing flag:** if full auto-reconciliation over-balloons, ship the scoring + a manual-reconciliation TODO and split the auto-check.

### Story Q3.2: Governance/tracker-coherence dimension

**Acceptance Criteria:** scores "believed-green in either direction" across trackers using `progress_map.py`, `doc_drift_monitor.py`, and deferred-inventory as signals; measures divergence between SOTA §11 / sprint-status / deferred-inventory. **Test:** divergence signal readers hermetic; a seeded three-tracker disagreement drops the score.

### Story Q3.3: Lane-discipline / scope-fidelity dimension (score the already-enforced)

**Acceptance Criteria:** a mostly-mechanical dimension scoring lane discipline from import-linter contract results + `governance-dimensions-taxonomy.md` / `lane-matrix.md` + scope_violation payloads (already enforced in CI — this story SCORES it, adds no new enforcement); honesty-pin ties the score to the live import-linter pass/fail count. **Test:** reads the real import-linter state; red if the score claims clean while contracts are broken.

### Story Q3.4: Calibration dimension — REPORT-ONLY

**Acceptance Criteria:** a dimension that HONESTLY REPORTS calibration posture (fresh-holdout vs resubstitution) — for reading-path it surfaces **"fresh naive holdout OWED / unmeasured"** and the single pinned resubstitution metric+dataset+commit; it does **NOT** build the holdout harness (that stays the separate owed epic `reading-path-fresh-naive-holdout-pre-trial`). Explicitly scores an owed/unmeasured neck as *uncalibrated*, not as passing. Honesty-pin fails if the dimension ever implies a fresh-holdout number was measured when it was not. **Test:** the "never imply measured" pin; the owed-flag renders. **Cross-link:** this is DID Leak 4's home; the two must not double-count.

---

## Green-light amendments

**Verdict: 4/4 GO-WITH-AMENDMENTS** (`bmad-party-mode` green-light, 2026-07-19 — Winston/architecture · John/scope · Murat/reliability · Amelia/dev-implementability). No NO-GO, no impasse. **These amendments are BINDING and govern on conflict** with the story bodies above. Binding unless marked (should) or (optional).

**Ordering & story split (all four voices flagged the Q1.2↔Q1.4 backward dependency):**
- **GL-1 — corrected Q1 topological order** (not the numeric order): **Q1.1 → Q1.4a → Q1.2 → Q1.3 → Q1.5 → Q1.4b**. Q1.2's C4 `silent_bypass_events` signal ships against the honest `undetected`/`null` state; Q1.4a's real detector lands with/before Q1.2's C4 (fail-soft tolerates an absent detector). Add this dependency note to Epic Q1 (the "serialize by rule" clause is concurrency, not ordering).
- **GL-2 — split Q1.4 into two stories.** **Q1.4a** = the `fence_state` block in `run_summary.yaml` + the honest `silent_bypass_events` detector fix (ships the operator job). **Q1.4b** = the deterministic final-report projector (reuse `hil_tabular_projector`), rendering Band + ranked-leaks + trend = Q1.5's output shape, so **sequence Q1.4b after Q1.5**. Q1.4b is a splittable tail.

**Seam-hardening (Winston):**
- **GL-3 (CRITICAL) — protect the clean leaf.** Signal readers must NOT module-import `app.*` from inside `app/quality` (import-linter names `app.quality` in zero contracts today, so this regression would pass CI while violating NFR4). Compute fence/env facts **at the `production_runner` seam** (which already imports `narration_figure_fidelity_active()`, `coverage_gate_active()`, etc.) and pass them into the scorecard layer **as plain data**, OR read via deferred local imports. Add a structural test asserting `app.quality` imports zero `app.*` at module scope — *that test is the leaf's honesty-pin.*
- **GL-4 — the run-summary breadcrumb stays a STATIC pointer.** `{source, note: project-level-not-this-run}`; `as_of` optional/omittable and must NOT force a governance-doc parse inside `_emit_run_summary_yaml` (would re-couple the runtime to the doc — forbidden by consensus rule #1). Per-run facts derive ONLY from run signals, never the doc.
- **GL-5 — wire `fence_state` into ALL FIVE emit call sites** (`production_runner.py` ~:2691/:4172/:4269/:4422/:5457 — the two-walks gotcha); a single-site wiring silently drops it on the other walk. Test presence across the start-walk AND resume-walk paths.

**Reliability meta-ratchets (Murat — binding unless noted):**
- **GL-6 (CRITICAL) — dimension-coverage meta-ratchet.** Reuse the 43-10 *structure*, not just its RED-first flavor: a named canonical dimension universe (`_EXPECTED_CANONICAL_KEYS`-style) + `test_every_dimension_has_a_honesty_pin` that FAILS unless every dimension in the v2 machine block has a registered honesty-pin. Prevents a future dimension shipping pin-less-and-green (the exact 42-1 believed-green class 43-10 kills). Add to Q1.3.
- **GL-7 — Q3.2 must not ship pin-less.** Its current test pins the signal→score function, not the machine-vs-prose contradiction. Either add the real pin (coherence-score can't rise while the three trackers actually diverge) OR declare Q3.2 fully-computed (no hand-authored level) + a test asserting no judgment field exists on it.
- **GL-8 — nail `silent_bypass_events` on all surfaces (Q1.4a):** (a) a component detection test (seed a synthetic bypass → detector reports it; no event → honest `undetected`/`0`); (b) a pin that `undetected` **caps C4** (cannot claim the clean level on an unchecked run).
- **GL-9 (should) — promote to doctrine-level:** "pins pass by AGREEING WITH REALITY today" and "goes RED under a seeded dishonest edit" become TESTING-DOCTRINE requirements for **every** dimension pin (Q2/Q3), not DID-only — so a sibling can't be authored green against a fictional target.
- **GL-10 (should) — the R2 witness is a checkable COMPARISON, not an observation:** capture this-run `fence_state` + projector output to a named evidence artifact and ASSERT equality with the independently-computed env truth for that run.
- **GL-11 (should) — close two hand-editable green surfaces:** a test pinning `trend == computed(history)` (no painted arrows); and tie any score/level INCREASE to an `as_verified` advance (a cited but stale `evidence_ref` must not suffice — that is the whole reason `as_of`/`as_verified` are split).

**Specification completeness (John + Amelia):**
- **GL-12 — name the `trend`-history substrate** (Q1.3, owner of `trend`): where it lives, its format, and the first-run "no history → no-trend" degrade.
- **GL-13 — ranked-leaks is CROSS-dimensional:** each dimension registers its leaks into the shared project ranked-leak list (else it silently stays DID-only). Add an AC to Q1.4b + a line to the Q2/Q3 story template.
- **GL-14 — Q1.3(b) leak-count pin runs against a fixture (or is intentionally RED-pending) until Q1.5 lands the 5 real `did_leak:` tags** (0 tags exist today) — so "working software each step" holds.
- **GL-15 — Q2.1 names the REAL seams** (not the non-existent `app/marcus/orchestrator/economics.py`): `app/runtime/economics.py::check_trial_budget`/`BudgetStatus` and the `cost_posture` Literal on `app/models/runtime/trial_economics_report.py`, consumed at `production_runner.py:382-389`.
- **GL-16 — Q3.3 reads the import-linter result via the shipped Python dep/API** (contracts in `pyproject.toml [tool.importlinter]`), NOT a CLI on PATH (per the verify-via-shipped-deps rule).

**Not blocking (confirmed sound):** fail-soft reader (Q1.1), reuse-existing-emitters harmonization, the E2E-deferral-to-R2 posture, and the Q3.1/Q3.4 report-only phasing flags. Amelia verified all named seams exist and are readable fail-soft.
