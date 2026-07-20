---
baseline_commit: 4167e912
---

# Story Q2.2: Coverage-honesty dimension

Status: ready-for-dev

<!-- Epic Q2 (Ready siblings). DISPATCH #2 of Q2 (serial after Q2.1; touches the machine block + pin registry → serialize by rule). Source epic: _bmad-output/planning-artifacts/epics-project-quality-scorecard-2026-07-19.md. Follows the Q2.1 cost-efficiency EXEMPLAR (the second sibling) + all Q2.1 review learnings. Honors the GL-13 authoring contract + the 5 Q1-retro action items. -->

## Story

As **the project quality scorecard**,
I want **a Coverage-honesty dimension scored from the EXISTING `CoverageReceipt` machinery + the real `coverage_gate_active()` default, with its own honesty pin**,
so that **the operator sees an honest read of whether source-coverage is enforced — and the default-OFF coverage gate is scored as a LEAK, not silently as a pass.**

## Scope fence (read FIRST)

Q2.2 adds ONE new dimension (`coverage_honesty`) reusing the Q1 engine + the Q2.1 pattern. It does **NOT**:

- **Touch DID or cost_efficiency** (Q1/Q2.1 done) — their numbers + prose + machine blocks are read-only.
- **Change the coverage runtime / gate / fence_state emitter / production_runner** — CONSUME `coverage_gate_active()`, `CoverageReceipt`, `evaluate_vacuous_receipt` etc. read-only; NO parallel plumbing (GL-15/NFR3).
- **Touch Q2.3/Q3** — coverage_honesty only.
- **Add module-scope `app.*` to `app/quality`** (GL-3) — coverage types via deferred local import, or read a run's coverage receipt as plain data.
- **Wire into production_runner's live emit** — E2E rides R2 (GL-10).
- Extend the Q1 machinery **only additively** (new readers, a new registered pin, a `coverage_honesty` machine-block + history + leaks entry).

## Honest baseline (verified — the assessment must match this)

- **The coverage gate EXISTS but is DEFAULT-OFF.** `coverage_gate_active()` (`coverage_gate_wiring.py:70`) reads `MARCUS_COVERAGE_GATE_ACTIVE`, default OFF; the production preset does not set it → **on a paid production walk, source-coverage is NOT enforced by default.** Per the epic AC: *the default-OFF gap IS the measured gap — a leak, not a pass.* This is the DID-C3 / cost-CE1 pattern.
- **The receipt distinguishes PASS / FAIL / PASS-vacuous.** `coverage_gate.py`: fail = `must_cover ∧ ((coverage_status==missing ∧ no_planned_surface) ∨ verbatim_absent ∨ narration_obligation_unmet)`; `evaluate_vacuous_receipt` + `COVERAGE_VACUOUS_TAG` = "marcus.coverage.vacuous-receipt" flags a receipt that passed only because it asserted nothing (a vacuous PASS is NOT a real pass — honesty machinery that already exists).

## Acceptance Criteria

**AC1 — New `## Dimension 3 — Coverage-honesty` section + machine-block entry**, mirroring the DID §1 / cost §2 structure (why-load-bearing → rubric → assessment table `{level, derivation, signal, evidence_ref, score, max}` → ranked leaks → cadence). Machine block gains a `coverage_honesty` dimension with the full field-set (`rubric_version/as_of/as_verified/score/max/band/band_note/criteria/open_leaks/leaks/trend`). Band+leaks+trend reporting.

**AC2 — Signal readers over the EXISTING coverage emitters** (fail-soft, read-only, clean-leaf; deferred imports / plain receipt read). Criteria (adapt to the honest reality; follow the signal-vs-judgment partition — retro AI-Q4):
- **coverage-fence enforcement (SIGNAL-DERIVED, the leak):** is the coverage gate enforced by default on the production preset? Via `coverage_gate_active()`'s default state. Honest today: default-OFF → **weak** (the leak). **Build this reader RIGHT per the Q2.1 CE1 remediation:** reachable close-path (if the gate is genuinely wired-on-by-default, the reader reports enforced=True → the criterion can earn strong — the pin must NOT block the honest upgrade), **read-only + env-independent** (no `os.environ` mutation; use an injectable env mapping / consult the real source, NOT a self-clearing constant).
- **receipt honesty (vacuous distinction):** does the machinery honestly flag PASS-vacuous (`evaluate_vacuous_receipt` / `COVERAGE_VACUOUS_TAG`) rather than counting a vacuous receipt as a real PASS? (judgment-with-evidence — the mechanism exists + is honest).
- **narration-obligation coverage:** `narration_obligation_unmet` detection wired (FIX-2 in coverage_gate). (judgment-with-evidence).
- Do NOT let an unverified/unknown/vacuous signal award a clean level (the anti-believed-green invariant).

**AC3 — The dimension's own honesty pin (GL-6 meta-ratchet REQUIRES it).** Register a `coverage_honesty` pin in `_HONESTY_PIN_REGISTRY` + add `coverage_honesty` to `_EXPECTED_CANONICAL_DIMENSION_KEYS`. The fence-claim pin is doc↔code: **a claimed "coverage-fenced" level FAILS unless `coverage_gate_active()` is truthy by default** (mirror DID-C3 / cost-CE1). RED-under-seeded (GL-9): bump the coverage-fence level to strong without the gate default-on → RED. Add the fence-enforcement reader to `_SIGNAL_DERIVED_READERS`.

**AC4 — GL-13 leak registration + cross-dimensional integration.**
- `coverage_honesty` `leaks:` list (`{rank, criterion, slug, lane}`; `len == open_leaks`); ≥1 = the default-OFF coverage-gate leak (lane `learner-trust` — coverage protects source-faithfulness; use your judgment on lane per §rubric prioritization). Slug → a `## Coverage-Honesty Scorecard Leak Registry` (a THIRD namespace, e.g. `cov_leak:`, disjoint from `did_leak:`/`cost_leak:` — verify the three readers don't cross-count).
- reconcile-by-identity (retro AI-Q2) covers coverage.
- `ranked_project_leaks` now aggregates DID + cost + coverage; `leak_coverage_gaps` stays clean (add coverage_honesty to the real-repo coverage assertion).

**AC5 — Mirror + trend + history.** Append a `coverage_honesty` snapshot to `scorecard-history.jsonl` (mirror pin, per-dimension); trend baseline; projector picks it up NO code change.

**AC6 — Tests (hermetic + real) + honest Band.** Receipt-shape signal readers against fixture `CoverageReceipt`s (PASS / FAIL / PASS-vacuous / narration-obligation-unmet) AND real state; the default-OFF fence pin RED-under-seeded (GL-9 — claims coverage-fenced without the wiring → red); meta-ratchet green; mirror/arithmetic/leak-identity/coverage all green. **Band honesty (Q2.1 FIX-2 learning):** if the coverage-fence (the thesis criterion) is weak while receipt-honesty criteria are strong, the `band_note` must state the headline is lifted by receipt-machinery honesty while the ENFORCEMENT (the thesis) is off-by-default — do not let the Band read as "coverage is enforced." **E2E:** deferred to R2 (GL-10 — file the obligation). DID + cost pins/numbers unchanged.

## Tasks / Subtasks
- [x] **T1 — Readiness.** Re-read the scope fence + honest baseline + the Q2.1 exemplar + its review learnings (CE1 close-path reachable/read-only; band honesty; non-empty guards; status consistency; regex IGNORECASE) + GL-13/GL-6/GL-9 + the 5 retro action items. Confirm no pipeline-lockstep trigger path edited.
- [x] **T2 — Signal readers** (AC2) — coverage-fence-default (built per the Q2.1 CE1 remediation from the start), receipt-honesty/vacuous, narration-obligation; fail-soft per-field; clean leaf.
- [x] **T3 — Rubric + assessment + machine block** (AC1) — honest levels; the default-OFF leak; signal-vs-judgment partition.
- [x] **T4 — Honesty pin + registry** (AC3); RED-under-seeded.
- [x] **T5 — GL-13 leaks + cov_leak registry + identity + ranked/coverage** (AC4).
- [x] **T6 — History mirror** (AC5) + honest band_note.
- [x] **T7 — Tests + R2 obligation** (AC6).
- [x] **T8 — Verify.** `pytest tests/quality/ -q`; ruff; import-linter 18/0; clean-leaf green; DID + cost unchanged; ALL prior pins green.

## Dev Notes

### Verified coverage seams (GL-15 — reuse, do NOT rebuild)
- `app/marcus/orchestrator/coverage_gate_wiring.py`: `coverage_gate_active()` (:70, default-OFF via `MARCUS_COVERAGE_GATE_ACTIVE`), `write_coverage_receipt`/`load_coverage_receipt_from_disk` (:114/:132), imports `CoverageReceipt`.
- `app/marcus/lesson_plan/coverage_gate.py`: the fail predicate (`coverage_status==missing ∧ no_planned_surface ∨ verbatim_absent ∨ narration_obligation_unmet`), `evaluate_vacuous_receipt`, `COVERAGE_VACUOUS_TAG`, `CoverageAssuranceError`.
- `app/marcus/lesson_plan/coverage_receipt.py`: the `CoverageReceipt` / `CoverageReceiptRow` model.
- Read a run's coverage receipt as plain data or deferred-import the model — NO module-scope `app.*` in `app/quality`.

### Follow the Q2.1 cost-efficiency EXEMPLAR + its review learnings (do NOT repeat its bugs)
Q2.1 is the sibling pattern (`app/quality/signals.py` cost readers, the `cost_efficiency` machine-block + `## Cost-Efficiency Scorecard Leak Registry` + the registered pin). Mirror it. Critically, apply Q2.1's REVIEW-FIX learnings up front:
- **The fence reader's close-path MUST be reachable + read-only** (Q2.1 FIX-1/FIX-6): do NOT write a self-clearing env constant that can never report strong and mutates global env. Use the read-only injectable-env pattern the remediated `budget_stop_default_signal` established.
- **Band honesty** (Q2.1 FIX-2): the band_note must not let telemetry/receipt-honesty mask a weak enforcement thesis.
- **Non-empty guards** (Q2.1 FIX-3): a present-but-empty structure is not "covered".
- **Status consistency** (Q2.1 FIX-4): return `unavailable` when a monitor/import is missing, not `ok`.
- **Regex IGNORECASE** (Q2.1 FIX-5) where any hex/tag matching applies.
- Equal-weight scoring kept (consistent with DID/cost); honest reading via band_note.

### The 5 Q1-retro action items (BINDING)
GL-13 registration (leaks + registered pin); reconcile-by-IDENTITY not count (coverage slug set-compare); GL-9 (green-by-reality + RED-under-seeded); signal-vs-judgment honesty; R2 checkable-comparison witness filed.

### Honesty is the bar
The coverage gate is real but default-OFF → on a paid walk, coverage is not enforced by default. Say so plainly (a real gate, opt-in) → the default-OFF gap is the leak. A PASS-vacuous receipt is honestly NOT a pass. Do not overclaim "coverage-fenced"; do not understate the gate/receipt machinery as absent.

### Testing standards
Reuse `tests/quality/`. Hermetic fixture `CoverageReceipt`s + real reads; monkeypatch `MARCUS_COVERAGE_GATE_ACTIVE` on/off → the fence signal matches (anti-drift, env-independent). No live calls; no `--run-live`.

### References
- [Source: epics-project-quality-scorecard-2026-07-19.md#Story Q2.2] + [#GL-13/GL-15/GL-6/GL-9/GL-10] + FR8.
- [Source: docs/dev-guide/quality-scorecard-dimension-authoring.md] — the GL-13 contract.
- [Source: app/marcus/orchestrator/coverage_gate_wiring.py:70 · app/marcus/lesson_plan/coverage_gate.py · coverage_receipt.py] — the coverage seams.
- [Source: q2-1-cost-efficiency-dimension.md (done) + its review remediation] — the sibling exemplar + the fence-reader/band-honesty learnings.
- [Source: docs/quality/project-quality-scorecard.md §1 (DID) + §2 (cost) + machine block] — the exemplars to mirror.
- [Source: app/quality/{signals,scorecard,history,report}.py · tests/quality/test_scorecard_honesty_pins.py] — the engine + registry to extend.

## Dev Agent Record

### Agent Model Used

Opus 4.8 (1M context) — fresh BMAD dev agent, `bmad-dev-story` workflow. RED-first discipline.

### Debug Log References

- `pytest tests/quality/ -q` → **243 passed** (7.95s, xdist).
- `ruff check` (all changed files) → **All checks passed!**
- `lint-imports` → **Contracts: 18 kept, 0 broken.**
- Clean-leaf guard `tests/quality/test_scorecard_clean_leaf.py::test_app_quality_is_a_clean_leaf` → green (all new coverage readers reach `app.marcus.*` ONLY via deferred local imports; zero module-scope `app.*`).
- `scripts/utilities/quality_scorecard.py --check` → `OK: scorecard as_of 2026-07-19`.
- **RED-first proof (live doc-seed, then reverted):** bumped machine-block CV1 `coverage_fence_default_on` level weak→strong (score 1→3) in the real doc; the fence-claim pin went RED (`coverage_honesty.coverage_fence_default_on: machine-block level 'strong' != reader-derived 'weak'`) AND the arithmetic pin went RED (`Σscore 9/12 normalizes to 75 != headline 58`); reverted. (Committed in-memory-seeded RED proofs also cover: any inflated level, slug-typo-while-count-green, three-namespace disjointness.)

### Completion Notes List

- **Honest baseline matched.** Coverage gate `coverage_gate_active()` is DEFAULT-OFF (`MARCUS_COVERAGE_GATE_ACTIVE` unset; production preset sets no default) → CV1 `default_coverage_enforced=False` → level **weak** (the leak, DID-C3 / cost-CE1 pattern). Receipt machinery honestly distinguishes PASS / FAIL / PASS-vacuous (`evaluate_vacuous_receipt` + `COVERAGE_VACUOUS_TAG`) and detects `narration_obligation_unmet` → CV2/CV3 **strong** (judgment-with-evidence). Band **C** (Σ 7/12=58); band_note states the C is receipt-honesty-lifted while ENFORCEMENT is off-by-default (and CV2/CV3 run only when the gate is woken).
- **AC2 fence reader built RIGHT (Q2.1 CE1 remediation, not the bug):** `coverage_fence_default_signal(env=None)` delegates to the REAL `coverage_gate_active()` when live (reachable close-path — a wired-on gate → enforced=True → strong) and resolves an injectable env mapping for the preset-default posture; **read-only** (zero `os.environ` mutation, proven by test) and **env-independent**; registered in `_SIGNAL_DERIVED_READERS`. FIX-4 (`status:unavailable` on import failure), FIX-3 (non-empty guards: empty-when-content receipt is not a clean pass), applied.
- **AC3 pin (GL-6 meta-ratchet + GL-9):** `coverage_fence_default_on` pin is doc↔code (a claimed coverage-fenced level FAILS unless `coverage_gate_active()` is truthy-by-default); registered in `_HONESTY_PIN_REGISTRY[coverage_honesty]`; `coverage_honesty` added to `_EXPECTED_CANONICAL_DIMENSION_KEYS`.
- **AC4 GL-13:** `leaks` list `{rank,criterion,slug,lane}` (len==open_leaks==1; the default-OFF leak, lane learner-trust — coverage protects source-faithfulness); THIRD `cov_leak:` namespace in `## Coverage-Honesty Scorecard Leak Registry`; three-namespace disjointness proven (did=5/cost=1/cov=1, pairwise disjoint, readers don't cross-count); identity-reconcile covers coverage; `ranked_project_leaks` aggregates DID+cost+coverage (7); `leak_coverage_gaps` clean.
- **AC5 mirror/trend:** appended a `coverage_honesty` snapshot to `scorecard-history.jsonl` (mirror pin green); trend baseline; projector picks it up with **no code change** (verified).
- **DID + cost_efficiency UNCHANGED** — numbers/prose/machine-blocks read-only (DID 65/B-, cost 62/B-); all prior pins green. Coverage runtime (`coverage_gate_wiring.py`, `coverage_gate.py`, `coverage_receipt.py`, `production_runner.py`) UNTOUCHED (no parallel plumbing, GL-15; no pipeline-lockstep trigger path edited).
- **Cross-dimensional sibling-test updates (mandated by AC4 — a third contributor legitimately changes these totals/universe assertions, not the dimensions' numbers):** `test_scorecard_reader.py` canonical tuple (+coverage_honesty); `test_cost_efficiency_dimension.py::test_cost_leak_is_lane_grouped...` overall `set(dims)` (+_COVERAGE_KEY); `test_scorecard_final_report.py::test_real_did_leaks_reconcile...` total 6→7.
- **E2E deferred to R2 (GL-10):** filed `q2-2-r2-coverage-honesty-witness` in `deferred-work.md`.
- **Honesty judgment call — lane.** Coverage is one of the three DID-C3 fences (fidelity/coverage/UDAC); DID frames that fence bundle as paid-walk. To avoid double-framing and per the spec steer, the coverage_honesty leak is laned **learner-trust** (coverage's distinctive value is source-faithfulness), so it sorts after the paid-walk block on the shared ranked list. Defensible either way; documented.
- Per dispatch instruction: Status left **ready-for-dev**; not committed.

### File List

- `app/quality/signals.py` (M) — coverage-honesty readers (`coverage_fence_default_signal`, `coverage_receipt_honesty_signal`, `coverage_narration_obligation_signal`, `coverage_leak_count_signal`, `_load_coverage_receipt_obj`) + `_level_cv_coverage_fence` + `level_from_signal` branch + `cov_leak:` regex.
- `app/quality/scorecard.py` (M) — `_COVERAGE_KEY` + added to `_EXPECTED_CANONICAL_DIMENSION_KEYS`.
- `docs/quality/project-quality-scorecard.md` (M) — Dimensions list item 3; §Dimension 3 prose (rubric/assessment/leaks/cadence); `coverage_honesty` machine-block entry.
- `docs/quality/scorecard-history.jsonl` (M) — appended `coverage_honesty` baseline snapshot.
- `_bmad-output/planning-artifacts/deferred-inventory.md` (M) — `## Coverage-Honesty Scorecard Leak Registry` + `cov_leak:` tag.
- `_bmad-output/implementation-artifacts/deferred-work.md` (M) — R2 coverage-honesty witness obligation.
- `tests/quality/test_coverage_honesty_dimension.py` (A) — signal readers vs fixture `CoverageReceipt`s (PASS/FAIL/vacuous/narration-unmet/empty/all-excluded) + real reads + monkeypatch on/off + GL-13 + projector pickup.
- `tests/quality/test_scorecard_honesty_pins.py` (M) — coverage pins (fence-claim, leak-count, arithmetic) + RED-under-seeded proofs + slug identity + three-namespace disjointness + derivation split; registry + `_SIGNAL_DERIVED_READERS` + imports.
- `tests/quality/test_scorecard_reader.py` (M) — canonical tuple +coverage_honesty.
- `tests/quality/test_cost_efficiency_dimension.py` (M) — cross-dimensional `set(dims)` +_COVERAGE_KEY.
- `tests/quality/test_scorecard_final_report.py` (M) — cross-dimensional ranked total 6→7.

### Review remediation (code review — 3 layers, 2026-07-19)

CE1 fence-reader bug did NOT recur (all three layers confirmed). Applied 5 fixes (RED-first for FIX-1/2, monkeypatch-proof for FIX-3):
- **FIX-1 [top] — CV2 `is_clean_pass` was dishonest on a real FAIL.** It derived solely from `evaluate_vacuous_receipt`, so a must-cover blocking FAIL with one covered row (`joined==1`, vacuous-silent) read `is_clean_pass=True`. Now consults the gate: `is_clean_pass = reason is None AND not evaluate_coverage_gate(rec) AND (joined>0 or all_excluded)`; added a `gate_blocks` field. Strengthened the toothless `test_receipt_honesty_fail_receipt_is_not_clean` to assert `gate_blocks is True` + `is_clean_pass is False`. RED proof: with the guard reverted, that test FAILED (wrongly-True).
- **FIX-2 [MED] — fence reader injectable-env branch now fail-soft.** `env=[...]` (`.get` AttributeError) and `env={KEY:1}` (`'int'.strip` AttributeError) escaped, contradicting the never-raises contract. Now: non-Mapping env or non-str value → `status:"unavailable"` (never a false-clean posture). RED proof: reverted branch raised `AttributeError: 'int' object has no attribute 'strip'` — the exact escape flagged.
- **FIX-3 [LOW] — CV3 `narration_obligation_gate_wired` now EXERCISES the real `_is_blocking` predicate** (a probe whose only blocking reason is the narration term must block; a control must not), not mere model-field presence. Proof: monkeypatching `_is_blocking` to drop the term flips `gate_wired` False (`test_narration_obligation_gate_wired_checks_real_predicate`).
- **FIX-4 [LOW] — `_load_coverage_receipt_obj` tries JSON-content THEN path** for a `str` source (a receipt-as-text is no longer silently misread as "no receipt"). Test: `test_receipt_honesty_reads_json_content_string`.
- **FIX-5 [NIT] — anti-drift pin** over the full truthy vocab (`1/true/yes/on` + case variants) asserting the injectable-env resolution agrees with the real `coverage_gate_wiring._env_true`.

Post-fix: `pytest tests/quality/ -q` → **254 passed**; ruff clean; import-linter 18/0; DID (65/B-) + cost (62/B-) unchanged; all prior pins green (meta-ratchet, mirror, arithmetic, leak-identity across 3 disjoint namespaces, coverage); clean-leaf green. Status left ready-for-dev; not committed.

### Change Log

- 2026-07-19 — Q2.2 review remediation: 5 fixes (CV2 gate-consulting is_clean_pass [FIX-1, RED-first], injectable-env fail-soft [FIX-2, RED-first], CV3 real-predicate wiring check [FIX-3], JSON-content str load [FIX-4], truthy-vocab anti-drift pin [FIX-5]). 254 quality tests pass; ruff/import-linter clean; DID+cost unchanged.
- 2026-07-19 — Q2.2 Coverage-honesty dimension implemented (all 6 ACs). New `coverage_honesty` dimension (Band C, 58) scored from existing coverage emitters; CV1 fence-enforcement signal-derived (weak/default-OFF leak), CV2/CV3 judgment-with-evidence (strong). Honesty pin + GL-6 meta-ratchet + GL-9 RED-under-seeded; GL-13 `cov_leak:` third namespace + cross-dimensional aggregation; mirror/trend/history. DID + cost unchanged. 243 quality tests pass; ruff clean; import-linter 18/0.
