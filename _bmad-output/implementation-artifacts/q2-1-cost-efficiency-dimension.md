---
baseline_commit: 817e4f21
---

# Story Q2.1: Cost-efficiency / paid-walk discipline dimension

Status: ready-for-dev

<!-- Epic Q2 (Ready siblings — reuse the Q1 engine). DISPATCH #1 of Q2 (serial: Q2.1 → Q2.2 → Q2.3, all touch the machine block + pin registry → serialize by rule). Source epic: _bmad-output/planning-artifacts/epics-project-quality-scorecard-2026-07-19.md. FIRST full sibling dimension — sets the pattern Q2.2/Q2.3 follow. Honors the GL-13 authoring contract (docs/dev-guide/quality-scorecard-dimension-authoring.md) + the 5 Q1-retro action items. -->

## Story

As **the project quality scorecard**,
I want **a Cost-efficiency / paid-walk-discipline dimension scored from the EXISTING economics emitters, with its own honesty pin**,
so that **the operator sees an honest, evidence-grounded read of whether paid walks are cost-disciplined — and the score cannot claim a cost fence that is not actually wired.**

## Scope fence (read FIRST)

Q2.1 adds ONE new dimension (`cost_efficiency`) reusing the Q1 engine. It does **NOT**:

- **Touch the DID dimension** (Q1 done) — DID numbers stay 65/B-; DID §1 prose + machine block are read-only.
- **Change the signal-reader / fence_state / pin-framework / projector CODE** except **additively**: new cost signal readers, a new registered honesty pin, a `cost_efficiency` machine-block entry + history entry + leaks list. The Q1 machinery (`scorecard.py`, `history.py`, `report.py`, the pin framework) is CONSUMED; extend it only where the GL-13 contract requires (register leaks; register the pin).
- **Build new economics plumbing** (GL-15 / NFR3 "reuse, no parallel plumbing") — read the EXISTING `TrialEconomicsReport` + `check_trial_budget` + `compute_per_agent_drift` + `MARCUS_TRIAL_BUDGET_USD`. No second cost reader.
- **Touch Q2.2/Q2.3/Q3** — cost_efficiency only.
- **Add module-scope `app.*` to `app/quality`** (GL-3) — economics types via deferred local import or read the run's `cost-report.json` as plain data.
- **Wire into production_runner's live emit** (Q1.4a already emits `cost_posture` into `fence_state`; the E2E rides R2 per GL-10).

## Honest baseline (verified — do NOT re-derive; the assessment must match this)

- **Budget-stop is a REAL enforced brake but OPT-IN.** `check_trial_budget(total, budget)` returns `state="no-cap"` when `budget is None`; the budget resolves from `MARCUS_TRIAL_BUDGET_USD`, **unset by default → no-cap**. Epic-41 made it a real economic brake WHEN SET (`production_runner.py:3611/4208/5494`), but the production preset does **not** set a default budget → **default = no cap**. This is the DID-C3 pattern (mechanism exists, default-off) → a **cost-efficiency leak** (the budget fence is opt-in on paid walks).
- **`cost_posture`** ∈ `{exact, known-lower-bound-with-explicit-unavailable-attempts}` (`trial_economics_report.py`), with `unavailable_attempt_count`; a lower-bound posture = the reported cost is a floor, not exact (an honesty gap when it occurs).
- **Per-agent drift** = `compute_per_agent_drift` (rolling-median deviation → `DriftAlert`s), consumed at `production_runner.py:382-389` region and emitted in the report.

## Acceptance Criteria

**AC1 — New `## Dimension 2 — Cost-efficiency (paid-walk discipline)` section + machine-block entry**, mirroring the DID §1 structure: a why-load-bearing intro, a rubric (§2.x criteria 0–4 + bands), an assessment table with per-criterion `{level, signal, evidence_ref}` + basis, a ranked open-leak list, and a §Cadence. Machine block gains a `cost_efficiency` dimension: `rubric_version`, `as_of`, `as_verified`, `score`, `max`, `band`, `band_note`, `criteria`, `open_leaks`, `leaks:` (GL-13), `trend`. Per the Band+leaks+trend reporting (consensus rule #4); per-criterion 0–4 as the reasoning trace.

**AC2 — Signal readers over the EXISTING economics emitters** (fail-soft, read-only, clean-leaf; deferred local import for economics types, or plain `cost-report.json` read). Concretely:
- **budget-stop posture** — is a default budget cap wired/enforced on the production preset? (reads `MARCUS_TRIAL_BUDGET_USD` default-state + that `check_trial_budget` → `no-cap` absent it). Honest today: opt-in / default no-cap.
- **cost_posture** — `exact` vs `known-lower-bound-...` + `unavailable_attempt_count`.
- **drift** — drift monitoring wired (`compute_per_agent_drift`) + alert presence/severity vs rolling median.
- **cost transparency** — the report carries `per_agent_breakdown` + `per_model_breakdown` + `cascade_config_digest`/`pricing_table_digest` (reproducible cost attestation).
- **Signal-vs-judgment honesty (retro AI-Q4):** wire a criterion `signal-derived` ONLY where the code unambiguously computes the level (the budget-stop-default is binary like DID-C3 → signal-derived); use `judgment-with-evidence` (honestly-named signal) where the level needs judgment. NEVER let an unverified/unknown/lower-bound signal award a clean level (the anti-believed-green invariant).

**AC3 — The dimension's own honesty pin (GL-6 meta-ratchet REQUIRES it).** Register a `cost_efficiency` pin in the Q1.3 registry (`_HONESTY_PIN_REGISTRY`) — else `test_every_dimension_has_a_honesty_pin` goes RED. The pin is doc↔code: **a claimed "cost-fenced"/budget-enforced level FAILS unless the production-preset default actually enforces a budget** (mirror the DID-C3 fence-claim pin: the signal-derived criterion's level == the reader's live output; today that's the opt-in/weak state). RED-under-seeded-edit (GL-9): bump the budget-fence level to "strong" without a default budget wired → RED.

**AC4 — GL-13 leak registration + cross-dimensional integration.**
- Add the `cost_efficiency` `leaks:` list (`{rank, criterion, slug, lane}`; `len == open_leaks`); at minimum the budget-stop-opt-in leak (lane `paid-walk`). Slugs point to a cost-efficiency leak entry in the deferred inventory (mirror the `## DID Scorecard Leak Registry` decoupling — file a cost leak entry/registry so archival can't drop the count).
- **reconcile-by-identity (retro AI-Q2):** the leak-count pin's identity check (`{machine-block leak slugs} == {registry slugs}`) must cover `cost_efficiency` too — a count-only reconciliation is insufficient.
- `ranked_project_leaks` now aggregates DID + cost_efficiency (verify the cross-dimensional interleave by lane priority); `leak_coverage_gaps` stays clean (add cost_efficiency to the real-repo coverage assertion).

**AC5 — Mirror + trend + history (Q1.3/Q1.4b).** Append a `cost_efficiency` snapshot to `docs/quality/scorecard-history.jsonl` so the mirror pin (`test_newest_history_mirrors_current_block`, per-dimension) stays green; `trend` = `baseline` (first snapshot). The projector (`render_scorecard_final_report`) picks up the new dimension with NO projector change (Band + trace + ranked leaks + trend).

**AC6 — Tests (hermetic + real).** Signal readers against a fixture `TrialEconomicsReport` (exact + lower-bound + drift-alert + no-cap/under-budget/over-budget) AND real repo/env state; drift math pinned; the budget-stop-not-wired pin RED-under-seeded (GL-9); the GL-6 meta-ratchet green (cost_efficiency now has a registered pin); mirror/arithmetic/leak-identity/coverage all green. **E2E:** the per-run `cost_posture` fact already rides Q1.4a's `fence_state`; witness on R2 (deferred, GL-10 — file the obligation, don't run). DID pins all stay green; DID numbers unchanged.

## Tasks / Subtasks

- [x] **T1 — Readiness.** Re-read the scope fence + the honest baseline + GL-13 contract + GL-15/GL-6/GL-9 + the 5 Q1-retro action items. Confirmed no pipeline-lockstep trigger path is edited (doc + `app/quality` + tests + deferred-inventory; `production_runner`/`economics.py` untouched → regime does not trigger).
- [x] **T2 — Signal readers** (AC2) in `app/quality/signals.py` (extend) — budget-stop-default, cost_posture, drift, transparency; fail-soft per-field; clean leaf (deferred local imports only; `import json` added for the plain cost-report read).
- [x] **T3 — Rubric + assessment + machine block** (AC1) — authored `## Dimension 2` honestly; CE1 signal-derived (weak); CE2/CE3/CE4 judgment-with-evidence (strong); the budget-opt-in leak; machine-block cost_efficiency entry (62/B-).
- [x] **T4 — Honesty pin + registry** (AC3) — registered the cost_efficiency pins in `_HONESTY_PIN_REGISTRY`; CE1 reader in `_SIGNAL_DERIVED_READERS`; cost_efficiency added to `_EXPECTED_CANONICAL_DIMENSION_KEYS`; budget-fence-claim pin + RED-under-seeded proof (seen RED on the real doc, restored).
- [x] **T5 — GL-13 leak registration + cross-dim** (AC4) — leaks list (1, paid-walk); `## Cost-Efficiency Scorecard Leak Registry` (`cost_leak:` namespace) in deferred-inventory; count + slug-IDENTITY reconcile; ranked_project_leaks interleave verified; coverage clean.
- [x] **T6 — History mirror** (AC5) — appended the cost_efficiency baseline snapshot; mirror pin green; projector picks it up with no projector change.
- [x] **T7 — Tests + R2 obligation** (AC6) — hermetic fixtures + real reads; drift math pinned; RED-first pins; filed the R2 cost-posture witness to deferred-work.md.
- [x] **T8 — Verify.** `pytest tests/quality/ -q` 199 passed; ruff clean; import-linter 18/0; clean-leaf green; DID unchanged (65/B-, 5 leaks); ALL Q1 pins green (meta-ratchet, mirror, arithmetic, leak-identity, coverage).

## Dev Notes

### Verified economics seams (GL-15 — reuse, do NOT rebuild)
- `app/models/runtime/trial_economics_report.py`: `TrialEconomicsReport` (`cost_posture` Literal, `budget_status: BudgetStatus{state,over_by_usd}`, `drift_alerts: list[DriftAlert]`, `per_agent_breakdown`, `per_model_breakdown`, `cascade_config_digest`/`pricing_table_digest`, `unavailable_attempt_count`).
- `app/runtime/economics.py`: `check_trial_budget` (:347 — `no-cap` when budget None), `compute_per_agent_drift` (:362 — rolling median, deviation_pct → DriftAlert), budget resolution from `MARCUS_TRIAL_BUDGET_USD` (:550).
- `app/marcus/orchestrator/production_runner.py`: the run's `cost-report.json` seam (the `_operator_surface_cost_reading` @:364 Q1.4a already reuses) + `MARCUS_TRIAL_BUDGET_USD` as the enforced brake (:3536/:3611/:4208/:5494).
- Read a run's cost report as plain JSON, or deferred-import the model — NO module-scope `app.*` in `app/quality`.

### Follow the DID exemplar + the GL-13 contract
- Mirror the DID §1 doc structure (why-load-bearing → rubric → assessment table → ranked leaks → cadence) and the machine-block criterion shape (`{level, derivation, signal, evidence_ref, score, max}`).
- `docs/dev-guide/quality-scorecard-dimension-authoring.md` is the SSOT for the leaks-list + coverage-guard contract. Add cost_efficiency to `_EXPECTED_CANONICAL_DIMENSION_KEYS` (scorecard.py) so the meta-ratchet's universe covers it.

### The 5 Q1-retro action items (BINDING on this story)
1. GL-13 registration contract — leaks list + registered pin, or the meta-ratchet + coverage red it.
2. Reconcile by IDENTITY not count — the leak-slug set check must cover cost_efficiency.
3. GL-9 — every new pin green-by-reality-today AND RED-under-seeded-dishonest-edit.
4. Signal-vs-judgment honesty — signal-derived only where the code unambiguously computes it; else judgment-with-evidence with an honestly-named signal; no unverified/lower-bound signal awards a clean level.
5. R2 checkable-comparison witness — file the cost-posture witness obligation.

### Honesty is the bar (this dimension will be scrutinized like Q1.5)
The budget-stop is a real Epic-41 win — but it is OPT-IN (default no-cap). The assessment MUST say so plainly (a real enforced brake that is not default-on) — do not overclaim "cost-fenced" when the default is no-cap, and do not understate the Epic-41 brake as absent. Cost_posture lower-bound (when it occurs) is an honest floor, not exact. Every claim cites a code/report referent.

### Testing standards
- Reuse `tests/quality/`. Hermetic fixture `TrialEconomicsReport`s (build via the model) + real repo/env reads. Monkeypatch `MARCUS_TRIAL_BUDGET_USD` on/off → the budget-fence signal matches (anti-drift). No live calls; no `--run-live`.

### References
- [Source: epics-project-quality-scorecard-2026-07-19.md#Story Q2.1] + [#Green-light amendments GL-13/GL-15/GL-6/GL-9/GL-10] + FR7.
- [Source: docs/dev-guide/quality-scorecard-dimension-authoring.md] — the GL-13 authoring contract.
- [Source: app/models/runtime/trial_economics_report.py · app/runtime/economics.py:347,362,550 · production_runner.py:3536/3611] — the economics seams.
- [Source: docs/quality/project-quality-scorecard.md §1 + machine block] — the DID exemplar to mirror.
- [Source: app/quality/{scorecard,signals,history,report}.py · tests/quality/test_scorecard_honesty_pins.py] — the Q1 engine + pin registry to extend.
- [Prev: epic-q1-retro-2026-07-19.md] — the 5 binding action items.

## Dev Agent Record

### Agent Model Used

claude-opus-4-8[1m] (fresh BMAD dev agent, RED-first discipline).

### Debug Log References

- RED proof (GL-9), real doc: seeded CE1 `weak`→`strong` (no default budget wired) → `test_cost_budget_fence_claim_matches_reader` AND `test_cost_score_arithmetic_is_internally_consistent` both FAILED (`"budget_stop_default_on: score 1 ↔ level 'strong' violates §1.5"` + reader-derived mismatch); restored → green. Encoded permanently as in-memory seeded-RED tests (`test_cost_budget_fence_claim_reds_on_dishonest_level`, `test_cost_slug_identity_reds_on_seeded_typo_while_count_stays_green`).
- Smoke: `budget_stop_default_signal()` env-independent → `default_budget_enforced=False`/`no-cap` → `weak`; seeded cap 5.0/0.5 → `strong`. `cost_leak_count_signal()`==1, `open_leak_count_signal()` (DID)==5 unchanged.
- `pytest tests/quality/ -q` → 199 passed. ruff clean. `lint-imports` → 18 kept / 0 broken. CLI `--check` → OK.

### Completion Notes List

- **New dimension `cost_efficiency` (Dimension 2), Band B− (62/100), scored from the EXISTING economics emitters (GL-15 — no parallel plumbing).** Four criteria: CE1 budget-stop default (weak/1, **signal-derived**), CE2 cost_posture honesty (strong/3), CE3 drift monitoring (strong/3), CE4 cost transparency (strong/3). Σ = 10/16 → 62 → B-.
- **Honest baseline matched exactly:** the Epic-41 dollar brake (`MARCUS_TRIAL_BUDGET_USD`→`check_trial_budget`, enforced at both walks by 41-4) is a REAL enforced stop WHEN SET but OPT-IN by default (preset sets no default budget → `check_trial_budget(total, None)`==`no-cap`). Stated plainly as the DID-C3 pattern → the one paid-walk cost leak. Not overclaimed as "cost-fenced"; not understated as absent.
- **Signal-vs-judgment honesty (retro AI-Q4):** CE1 is `signal-derived` (the reader unambiguously computes weak, env-INDEPENDENT); CE2/CE3/CE4 are `judgment-with-evidence` with honestly-named signal blocks + `level_from_signal` returning `None` (no clean auto-award). No unverified/lower-bound signal awards a clean level.
- **Honesty pin (AC3/GL-6):** registered 3 cost_efficiency pins in `_HONESTY_PIN_REGISTRY`; CE1 reader in `_SIGNAL_DERIVED_READERS`; `cost_efficiency` added to `_EXPECTED_CANONICAL_DIMENSION_KEYS`. The meta-ratchet now covers cost_efficiency (a pin-less add would RED).
- **GL-13 (AC4):** cost_efficiency `leaks:` list (1, paid-walk) == open_leaks; `## Cost-Efficiency Scorecard Leak Registry` filed with a SEPARATE `cost_leak:` namespace (decoupled from archival, never collides with DID `did_leak:`); leak-count + slug-IDENTITY reconcile (retro AI-Q2); `ranked_project_leaks` aggregates DID(5)+cost(1)=6, interleaved by lane (cost paid-walk sorts among DID paid-walk); `leak_coverage_gaps` clean.
- **Mirror + trend (AC5):** appended the cost_efficiency baseline snapshot to `scorecard-history.jsonl` (trend=baseline); the projector renders the new dimension (Band/trace/ranked-leak/trend) with NO projector code change.
- **Scope fence honored:** DID dimension untouched (65/B-, 5 leaks, §1 read-only); `fence_state` emitter / `production_runner` / `economics.py` untouched; Q2.2/Q2.3/Q3 untouched; Q1 machinery extended additively only.
- **R2 witness (GL-10):** cost-posture checkable-comparison obligation filed to `deferred-work.md` (`q2-1-r2-cost-posture-witness`); not run live.
- **Q1 pins all green** (named): `test_signal_derived_levels_match_readers`, `test_leak_count_reconciles_on_real_repo`, `test_score_arithmetic_is_internally_consistent`, `test_machine_block_leak_slugs_match_registry_identity`, `test_every_dimension_has_a_honesty_pin`, `test_canonical_universe_matches_machine_block`, `test_newest_history_mirrors_current_block`, `test_trend_is_computed_not_painted`, `test_leak_coverage_gaps_clean_on_real_repo`, `test_did_machine_block_projection_matches_golden` (DID numbers unchanged).
- Two DID-only Q1 test expectations updated additively (legitimate cross-dimensional extension, not DID rescoring): `test_canonical_dimension_keys_constant` (now names both dimensions), `test_real_did_leaks_reconcile_with_open_leaks` (ranked total now 6), `test_meta_ratchet_reds_on_pinless_dimension` (hypothetical key changed since cost_efficiency is now registered).
- **Status left `ready-for-dev` and NOT committed per the dispatch instruction** (fresh dev agent; sprint-status not advanced).

**Code-review follow-ups applied (3-layer review; RED-first; DID stays 65/B-):**
- **FIX-1 [MED] — CE1 close-path made reader-reachable + env-mutation removed.** Investigated: the runtime has NO non-env preset-default budget source — `MARCUS_TRIAL_BUDGET_USD` (read live by `production_runner._resolve_trial_budget_usd`) is the only budget knob; the production preset sets/setdefaults nothing. Restructured `budget_stop_default_signal` to delegate to a new `_resolve_runtime_default_budget(env)` that reads the runtime's OWN budget source read-only (no `os.environ` pop/restore — FIX-6) via an injectable `env` mapping. It is no longer a self-clearing constant: a clean env → `None` → weak (the preset default today); an env carrying a wired default cap → `strong`. Docstring corrected (removed the false "mirrors …clears" claim; now honestly delegates and reads live). §2.6 + the machine-block CE1 comment state the honest close-path: **closing needs runtime substrate (a preset-default budget source the resolver returns)** — the reader detects it when present; the seeded-override test proves the level logic reaches strong on a real cap. New tests: `test_budget_stop_close_path_is_reader_reachable`, `test_budget_stop_reader_is_read_only_no_env_mutation`.
- **FIX-2 [LOW-MED] — Band honesty.** `band_note` now states B− is lifted by post-spend telemetry while the pre-spend brake (CE1, the thesis) is weak/opt-in; §2.6 opens with a prominent ⚠️ headline caveat elevating the outcome-weighted reading (equal-weight scoring kept, consistent with DID — only the READING made honest).
- **FIX-3 [LOW-MED] — transparency requires non-empty data.** `cost_transparency_signal` now requires `isinstance(dict) and len>0` for the breakdowns; RED-proven (`test_cost_transparency_reds_on_empty_breakdown` FAILS under the reverted guard, passes after — demonstrated ephemerally).
- **FIX-4 [LOW] — drift status consistency.** `cost_drift_signal` returns `status:"unavailable"` when `compute_per_agent_drift` is unimportable (was always `ok`); RED-proven via `test_cost_drift_status_unavailable_when_monitor_unimportable` (blocks the import).
- **FIX-5 [LOW] — digest regex.** `_SHA256_RE` gained `re.IGNORECASE` (uppercase hex no longer false-"absent"); `test_cost_transparency_accepts_uppercase_digest`.
- **FIX-7 [NIT] — CE1 weak-vs-partial rationale stated** explicitly in §2.6 (deliberate DID-C3-consistent conservative call — brake fully enforced when set, but the default is off → weak(1), mirroring `fence_enforcement_default_on`).
- **FIX-8 [NIT] — interleave test sharpened** to assert the paid-walk leaks are a contiguous front block spanning BOTH dimensions (lane grouping), not mere membership.
- Post-fix: `pytest tests/quality/ -q` → **203 passed**; ruff clean; import-linter 18/0; clean-leaf green; DID unchanged; all Q1 pins green.

### File List

- `app/quality/signals.py` (M) — cost readers (`budget_stop_default_signal`, `cost_posture_signal`, `cost_drift_signal`, `cost_transparency_signal`, `cost_leak_count_signal`), `_level_ce_budget` + `level_from_signal` wiring, `import json`.
- `app/quality/scorecard.py` (M) — `_COST_KEY` + `cost_efficiency` added to `_EXPECTED_CANONICAL_DIMENSION_KEYS`.
- `docs/quality/project-quality-scorecard.md` (M) — Dimensions list; `## Dimension 2` prose (§2.0/2.5/2.6 + cadence); machine-block `cost_efficiency` entry.
- `docs/quality/scorecard-history.jsonl` (M) — appended the cost_efficiency baseline snapshot.
- `_bmad-output/planning-artifacts/deferred-inventory.md` (M) — `## Cost-Efficiency Scorecard Leak Registry` (`cost_leak:` namespace, 1 leak).
- `_bmad-output/implementation-artifacts/deferred-work.md` (M) — R2 cost-posture witness obligation.
- `tests/quality/test_cost_efficiency_dimension.py` (A) — reader/drift-math/fixture/cross-dim/projector tests.
- `tests/quality/test_scorecard_honesty_pins.py` (M) — cost imports/reader/registry + registered cost pins + RED proofs + pinless-hypothetical fix.
- `tests/quality/test_scorecard_reader.py` (M) — canonical-keys constant updated to both dimensions.
- `tests/quality/test_scorecard_final_report.py` (M) — ranked-leaks total updated to cross-dimensional 6.
