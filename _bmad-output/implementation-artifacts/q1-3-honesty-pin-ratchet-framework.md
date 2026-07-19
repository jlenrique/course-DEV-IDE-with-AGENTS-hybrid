---
baseline_commit: f717fba6
---

# Story Q1.3: Honesty-pin ratchet framework (anti-believed-green)

Status: ready-for-dev

<!-- Epic Q1 (Scorecard Engine + DID Reframe, FOUNDATION). DISPATCH #4 of the binding GL-1 order: Q1.1 (done) → Q1.4a (done) → Q1.2 (done) → **Q1.3** → Q1.5 → Q1.4b. Source epic: _bmad-output/planning-artifacts/epics-project-quality-scorecard-2026-07-19.md. -->

## Story

As **the project**,
I want **tests that FAIL when the scorecard's claims contradict the code**,
so that **the score cannot quietly lie in either direction — a level can only rise on earned, cited evidence, and no dimension can ship without a pin**.

## Scope fence (read FIRST)

Q1.3 builds the **anti-believed-green machinery**: the honesty pins, the dimension-coverage meta-ratchet, the evidence-gated upgrade guard, and the trend-history substrate. It does **NOT**:

- **Reauthor DID prose / enumerated checklists / the C1 re-checkable artifact / the 0.071 correction / the Band+leaks+trend REPORTING reshape** — that is **Q1.5**. Q1.3 pins the CURRENT v2 shape; Q1.5 reshapes it (and updates the pins in lockstep).
- **Tag the 5 `did_leak:` entries** — that is **Q1.5**. Per **GL-14**, 0 tags exist today (`open_leaks: 5` is hand-carried), so the leak-count reconciliation pin is proven against a **fixture** and is **intentionally RED-pending** on the real repo (a self-clearing `xfail(strict=True)`) until Q1.5 lands the tags.
- **Change any signal reader / the fence_state emitter / the machine-block numbers** — Q1.1/Q1.2/Q1.4a own those; Q1.3 CONSUMES them (the pins call `app.quality.signals` + `dimension_ref`). DID stays 65/B-.
- **Build the final-report projector** (Q1.4b).
- **Import `app.*` at module scope in `app/quality`** (GL-3) — any new `app/quality` helper stays stdlib+json/yaml; the leaf-guard must stay green.

If you find yourself rewriting §1.6, tagging a `did_leak:`, or moving a number, **stop — that is a different story.**

## Acceptance Criteria

**AC1 — `tests/quality/test_scorecard_honesty_pins.py` (RED-first, reusing the 43-10 ratchet form).** Three pins that go RED when the doc disagrees with the code:
- **(a) Fence-claim consistency** — for every criterion whose `derivation: signal-derived`, the machine-block `level`/`score` MUST equal the reader's live output (`level_from_signal(reader())`). Concretely today: C3's `level` must equal `level_from_signal(fences_enabled_signal())` (== `weak`). A criterion claiming a fence ON-by-default fails unless the real env-gate default is truthy. RED under a seeded dishonest edit: bump C3 to `strong`/`partial` without the env-gate default flipping → red.
- **(b) Leak-count reconciliation** — `open_leaks` MUST equal the count of `did_leak:`-tagged **open** entries (via `open_leak_count_signal()`). **GL-14:** proven GREEN against a **fixture** deferred-inventory (seeded N tags ↔ `open_leaks: N`); on the REAL repo it is an **`@pytest.mark.xfail(strict=True, reason="GL-14: open_leaks=5 hand-carried until Q1.5 tags the 5 did_leak entries")`** so it is honestly RED-pending now and **auto-fires** (xpass→failure forcing the marker's removal) the moment Q1.5 makes 5==5. RED under: strike a `did_leak:` entry (in the fixture) without updating the count → red.
- **(c) Score-arithmetic** — the per-criterion `score`/`level` mapping is internally consistent (score↔level per §1.5: 4=strong/uniform · 3=strong · 2=partial · 1=weak · 0=absent), the sum of criterion scores /20 normalized to /100 equals the headline `score` (4+3+1+3+2=13/20=65), and `band` matches the §1.5 boundary table (65→`B-`). RED under: fat-finger the band, a criterion score, or the headline.

**AC2 — GL-6 (CRITICAL) dimension-coverage meta-ratchet.** Reuse the 43-10 *structure*: a NAMED canonical dimension universe (extend Q1.1's `_EXPECTED_CANONICAL_DIMENSION_KEYS`) + a pin registry mapping each dimension → its registered honesty-pins, and `test_every_dimension_has_a_honesty_pin` that FAILS unless **every** dimension present in the v2 machine block has ≥1 registered pin. Today: 1 dimension (DID) with pins (a)/(b)/(c). A future dimension added to the machine block without a registered pin → red (the exact 42-1 believed-green class the ratchet kills). Also assert the named universe ⊆/== the machine-block dimension keys (no typo, no orphan).

**AC3 — GL-11 evidence-gated upgrade guard + GL-12 trend-history substrate.**
- **Trend-history substrate (GL-12 — name it):** an append-only JSON-lines file at **`docs/quality/scorecard-history.jsonl`** (co-located with the doc, git-tracked). One object per assessment snapshot: `{"as_of", "dimension", "score", "band", "levels": {criterion: score}, "open_leaks", "as_verified"}`. A fail-soft reader (stdlib+json, clean leaf) `history_entries(dimension)` returns them oldest→newest. **First-run degrade:** absent/empty history → no trend / `baseline`. Q1.3 SEEDS the first (2026-07-19 baseline) entry.
- **`trend` is computed, not painted (GL-11):** a pin asserts the machine-block `trend` equals `trend_from_history(dimension)` (delta vs the latest *prior* snapshot; `baseline` when none). Today both = `baseline`. RED under: hand-paint `trend: rising` with no supporting history.
- **Evidence-gated upgrade (GL-11):** a pin that, comparing the current machine block against the latest prior history snapshot, asserts any criterion/headline **INCREASE** cites (i) an `evidence_ref` that advanced (a closed-leak / turned-on-fence reference, not the same stale string) AND (ii) an `as_verified` advance (a stale `evidence_ref` must NOT suffice — this is why `as_of`/`as_verified` are split). **Downgrades are free** (no evidence required). With only the baseline entry present, the guard is a no-op today and activates on the next assessment (honest first-run).

**AC4 — CLI `--check` demoted to a secondary staleness nag.** Keep `scripts/utilities/quality_scorecard.py --check` (the `as_of` age warning) but document (module docstring + the scorecard doc §Cadence "Staleness ratchet" line) that it is a SECONDARY nag, NOT the honesty guard — the honesty guard is `tests/quality/test_scorecard_honesty_pins.py`. No behavior change to `--check`.

**AC5 — The pins pass TODAY by AGREEING WITH REALITY, and go RED on a seeded dishonest edit (GL-9 doctrine).** Every pin: (1) green now because the doc matches the code (C3 weak matches default-OFF fences; band matches score; trend baseline matches empty history); (2) a companion test proves it goes RED under a seeded dishonest edit (via a fixture/parametrized mutation — do NOT mutate the real doc). This RED-under-seeded-edit proof is the heart of the reliability mandate.

## Tasks / Subtasks

- [x] **T1 — Readiness.** Re-read the scope fence + consensus rule #3 (anti-believed-green; `as_of` vs `as_verified` split) + GL-6/GL-9/GL-11/GL-12/GL-14 + the 43-10 ratchet reference. No pipeline-lockstep trigger path touched (tests + a docs/-local history file + optional clean-leaf helper) → regime does not trigger.
- [x] **T2 — History substrate** (AC3, GL-12): `docs/quality/scorecard-history.jsonl` seeded with the baseline; a fail-soft `history_entries()` + `trend_from_history()` reader in `app/quality/` (stdlib+json, clean leaf) — or extend `scorecard.py`. Deferred imports if any app touch (there is none — pure file read).
- [x] **T3 — The 3 pins** (AC1): fence-claim (consume `signals.level_from_signal`/`fences_enabled_signal`), leak-count reconciliation (fixture green + real-repo xfail-strict per GL-14), score-arithmetic (score↔level↔band↔sum).
- [x] **T4 — GL-6 meta-ratchet** (AC2): named dimension universe + pin registry + `test_every_dimension_has_a_honesty_pin` + no-typo/no-orphan.
- [x] **T5 — Evidence-gated upgrade + computed-trend pins** (AC3, GL-11).
- [x] **T6 — `--check` demotion doc** (AC4): docstring + §Cadence line; no behavior change.
- [x] **T7 — RED-under-seeded-edit proofs** (AC5) for each pin; verify. `pytest tests/quality/ -q`; ruff; import-linter 18/0; clean-leaf green; DID numbers unchanged.

## Dev Notes

### What already exists (consume, do not rebuild)
- **`app/quality/scorecard.py`** (Q1.1): `read_scorecard_block`, `dimension_ref(key)`, `_EXPECTED_CANONICAL_DIMENSION_KEYS`. Fail-soft, clean leaf.
- **`app/quality/signals.py`** (Q1.2): `fences_enabled_signal`, `bone_inventory_signal`, `lock_contract_signal`, `open_leak_count_signal`, `level_from_signal`. Deferred-import discipline; the fence signal is env-INDEPENDENT.
- **Machine block v2 shape** (post-Q1.2): dimension `{rubric_version, as_of, as_verified, score, max, band, band_note, criteria, open_leaks, trend}`; each criterion `{level, derivation, signal, evidence_ref, score, max}` where `derivation ∈ {signal-derived, judgment-with-evidence, judgment}`. Current DID: score 65 / B- / criteria 4·3·1·3·2 (neck·bone·fence·lock·honesty) / open_leaks 5 / trend baseline.
- **43-10 ratchet** (`tests/marcus/cli/test_projector_coverage_ratchet_43_10.py`): the structural form to reuse — a NAMED `_EXPECTED_*` frozenset + coverage/disjoint/no-orphan assertions, pure (no IO/live spend). Mirror it for the dimension-coverage meta-ratchet.
- **§1.5 rubric** (bands A≥90 · B75-89 · B−60-74 · C40-59 · D<40; levels 0 absent/1 weak/2 partial/3 strong/4 uniform) — the score-arithmetic pin's source of truth. Read it in the doc.

### The pins pin DOC↔CODE, not doc↔doc
The whole point (consensus rule #3): each pin compares the machine-block CLAIM against a CODE-COMPUTED reality. Fence-claim → `signals`; leak-count → `open_leak_count_signal`; arithmetic → the §1.5 rule. A pin that only checks the doc against itself is worthless — make every pin cite a code source.

### GL-14 leak-count is RED-pending BY DESIGN
`open_leaks: 5` is hand-carried; 0 `did_leak:` tags exist today. The reconciliation pin is GREEN on a seeded fixture (logic proven) and `xfail(strict=True)` on the real repo — so it is honestly red-pending and CANNOT be forgotten: when Q1.5 tags the 5 leaks (5==5), the xfail becomes an xpass and pytest-strict FAILS, forcing the dev to delete the marker and promote it to a hard pin. This is "working software each step" + a self-clearing obligation.

### Trend-history first-run honesty (GL-12)
With only the baseline snapshot, `trend_from_history` returns `baseline` and the evidence-gated guard has nothing prior to compare → no-op. This is the correct first-run degrade; the guard activates on the SECOND assessment. Do not fabricate a prior entry.

### Q1.1/Q1.2/Q1.4a learnings carried forward
- **Per-field fail-soft**; `"unavailable"`/`"undetected"` are first-class and can never satisfy a "clean" pin.
- **RED-first the pins** — a pin that was never seen RED is not trustworthy; prove each goes red under a seeded edit (fixture/parametrized, never mutate the real doc).
- **Hold the Q1.5 boundary** — pins assert the CURRENT shape; Q1.5 reshapes + updates them.
- **Clean leaf** — any `app/quality` history helper stays stdlib+json.

### Testing standards
- Reuse `tests/quality/`. Pure-structural where possible (like 43-10). Hermetic fixtures for the seeded-RED proofs (copy the block to tmp, mutate, assert the pin fails). No live calls, no `--run-live`.

### References
- [Source: epics-project-quality-scorecard-2026-07-19.md#Story Q1.3] + [#Green-light amendments GL-6/GL-9/GL-11/GL-12/GL-14] + consensus rule #3.
- [Source: tests/marcus/cli/test_projector_coverage_ratchet_43_10.py] — the ratchet form to reuse.
- [Source: app/quality/scorecard.py · app/quality/signals.py] — the code the pins consume.
- [Source: docs/quality/project-quality-scorecard.md §1.5/§1.6 + machine block] — the claims the pins verify.
- [Prev stories: q1-1 (reader/leaf) · q1-2 (signals/derivation) · q1-4a (fence_state)] — all done.

## Dev Agent Record

### Agent Model Used

claude-opus-4-8[1m] (fresh BMAD dev agent, RED-first TDD).

### Debug Log References

- Baseline before changes: `pytest tests/quality/ -q` → 94 passed; ruff clean; import-linter 18/0.
- Final: `pytest tests/quality/ -q -rx` → **119 passed, 1 xfailed** (the intentional GL-14 `xfail(strict=True)`); ruff `All checks passed!`; import-linter **18 kept / 0 broken**; clean-leaf guard green (scans `app/quality/history.py`).
- Two ruff findings fixed mid-flight (UP035 `Callable` from `collections.abc`; SIM102 collapsed nested `if` in the headline-increase branch).
- One RED-proof fixture bug fixed: `textwrap.dedent` yields column-0 lines, so the `.replace()` needle for the strike-a-tag proof had to drop its 4-space indent.

### Completion Notes List

**All 5 ACs satisfied. DID numbers UNCHANGED (65/B-; 4·3·1·3·2; open_leaks 5; trend baseline) — doc diff is a single §Cadence prose line; the machine block is byte-identical.**

- **AC1 — 3 pins, each doc↔code (never doc↔doc):**
  - (a) **fence-claim** — `_signal_derived_violations` compares every `derivation: signal-derived` criterion's machine-block `level` to `level_from_signal(reader())`; C3 == `level_from_signal(fences_enabled_signal())` == `weak` (env-INDEPENDENT default-OFF posture). Code source = `app.quality.signals`.
  - (b) **leak-count reconciliation** — `open_leaks` vs `open_leak_count_signal()["open_leak_count"]`. GREEN on a seeded fixture (3 tags ↔ `_reconcile(3, 3)`); on the REAL repo it is `@pytest.mark.xfail(strict=True, reason="GL-14: open_leaks=5 hand-carried until Q1.5 tags the 5 did_leak entries")` (5 vs 0 today). Self-clearing: when Q1.5 makes 5==5 the assert passes → XPASS → strict FAIL → the marker must be deleted.
  - (c) **score-arithmetic** — `_arithmetic_violations`: score↔level per §1.5 (`_SCORE_TO_LEVELS`), Σ13/20→65/100 == headline, band == `_band_for_score(65)` == B-. Code source = the §1.5 rubric encoded in-test.
- **AC2 — GL-6 meta-ratchet:** consumes Q1.1's `_EXPECTED_CANONICAL_DIMENSION_KEYS` + a `_HONESTY_PIN_REGISTRY` (DID → the three AC1 pin names). `test_every_dimension_has_a_honesty_pin` fails unless every machine-block dimension has ≥1 pin; `test_canonical_universe_matches_machine_block` (no-orphan/no-typo, universe == block keys); `test_pin_registry_keys_are_canonical_no_orphans` (registry ⊆ canonical + every named pin is a real test in-module). Mirrors the 43-10 structural form.
- **AC3 — GL-11/GL-12:**
  - **Trend-history substrate** at `docs/quality/scorecard-history.jsonl` (append-only JSONL, git-tracked), seeded with the 2026-07-19 baseline snapshot `{as_of, dimension, score, band, levels, open_leaks, as_verified}`. Reader `app/quality/history.py` (`history_entries`, `latest_prior_snapshot`, `trend_from_history`) — stdlib+json, **clean leaf, zero module-scope `app.*`**. First-run degrade: absent/empty/malformed-line → `baseline`.
  - **Computed trend** — `test_trend_is_computed_not_painted`: machine-block `trend` == `trend_from_history(DID)` (both `baseline`; RED under a painted `rising`).
  - **Evidence-gated upgrade guard** — `evidence_gated_upgrade_violations(block, prior)`: any criterion/headline INCREASE vs the latest *strictly-prior* snapshot must (i) cite a non-empty `evidence_ref` AND (ii) advance `as_verified` (a bumped `as_of` alone — prose edited, evidence not re-checked — fails). Downgrades free. No-op today (baseline `as_of` == block `as_of` → `latest_prior_snapshot` is `None`); activates on the 2nd assessment.
- **AC4 — `--check` demoted** to a documented SECONDARY staleness nag (CLI module docstring + doc §Cadence "Staleness ratchet" line both now name `tests/quality/test_scorecard_honesty_pins.py` as the honesty guard). **No behavior change** to `--check`.
- **AC5 / GL-9 doctrine** — every pin (1) green today by agreeing with reality, and (2) has a companion proof it goes RED under a **seeded** dishonest edit via fixture / in-memory `deepcopy` mutation — the real doc/inventory is NEVER mutated: `test_fence_claim_pin_reds_on_dishonest_level` (+ parametrized strong/partial/uniform), `test_leak_count_pin_reds_when_fixture_tag_struck`, `test_score_arithmetic_pin_reds_on_seeded_edit` (band/headline/criterion-score/level-mismatch), `test_trend_pin_reds_on_hand_painted_arrow`, `test_upgrade_guard_reds_on_increase_without_as_verified_advance`, `test_upgrade_guard_reds_on_increase_without_evidence_ref`; the meta-ratchet's `test_meta_ratchet_reds_on_pinless_dimension` seeds a pin-less `cost_efficiency` dimension.

**Scope fence held:** did NOT reauthor §1.6 / enumerated checklists / C1 artifact / 0.071 correction / Band+leaks+trend reshape (Q1.5); did NOT tag any `did_leak:` entry; did NOT change any signal reader / fence_state emitter / machine-block number; did NOT build the projector (Q1.4b); no module-scope `app.*` added to `app/quality`. No scope-fence temptation arose that required declining — the leak-count RED-pending is handled exactly as GL-14 prescribes (fixture + xfail-strict), so no urge to tag the real leaks.

---

### Code-review response batch (3-layer review — HIGH + 4 MED + 2 LOW), RED-first, no commit

The anti-believed-green machinery had its own believed-green holes. All closed; DID stays 65/B-; final suite **131 passed, 1 xfailed**; ruff clean; import-linter 18/0.

- **R1 [HIGH] — closed the upgrade-guard bypass.** Two additions: (i) a STANDING `test_newest_history_mirrors_current_block` — the newest ledger entry per dimension must content-match the block `{dimension, score, band, levels{criterion:score}, open_leaks, as_of, as_verified}`, so inflating the doc without appending to `scorecard-history.jsonl` goes RED (`_mirror_violations`); (ii) the evidence-gated guard now runs as a STANDING pin over the real block + each dimension's real newest-strictly-prior snapshot. Together they make the guard's no-op self-terminating: the mirror pin forces a real prior to appear on the next re-score, activating the guard automatically. RED-first proven: `test_mirror_pin_reds_on_doc_inflation_without_history_append`; inline demo showed a real-ledger inflation → mirror RED, and an inflation with a real prior + stale `as_verified` → guard RED.
- **R2 [MED] — parametrized coverage over ALL dimensions.** `_signal_derived_violations`, `_mechanical_criteria_violations`, `_arithmetic_violations` (per-dim, iterated in the pin), the real-repo leak reconciliation, and the evidence guard now iterate every machine-block dimension — a future `cost_efficiency` can't pass vacuously on a DID-only assertion. `test_arithmetic_pin_covers_every_dimension_not_just_did` seeds a 2nd inconsistent dimension → RED.
- **R3 [MED] — anti-de-mechanization of pin (a).** `_SIGNAL_DERIVED_READERS` (CODE) — not the doc's self-declared `derivation` — is the authority on which criteria are mechanical. New `test_code_known_mechanical_criteria_not_de_mechanized` asserts each code-known mechanical criterion still declares `signal-derived` AND matches its reader. `test_de_mechanization_is_caught` proves the OLD doc-driven half SKIPS a relabeled C3 (the hole) while the code-driven half catches it.
- **R4 [MED] — history.py date hardening.** (a) `_valid_iso` gate before any date compare; a malformed `as_of` on the newest-appended entry → `baseline`. (b) `newest_snapshot`/`latest_prior_snapshot`/`trend_from_history` select by max-BY-VALIDATED-DATE, not `entries[-1]`. (c) deterministic file-index tie-break on equal `as_of`. Tests: `test_trend_degrades_on_malformed_newest_as_of`, `test_trend_uses_max_by_date_not_file_order`, `test_trend_same_date_tiebreak_is_later_in_file`.
- **R5 [MED, Edge Hunter] — pin robustness.** (a) missing `criteria` → clean violation not KeyError (`test_arithmetic_pin_handles_missing_criteria_without_keyerror`). (b) `_int_score` bool-guard: `score: true` is malformed, never coerced to 1 (`test_arithmetic_pin_rejects_bool_score_not_coerced_to_one`). (c) evidence guard treats missing/non-numeric prior levels conservatively — a real increase can't slip (`test_upgrade_guard_conservative_on_malformed_prior_levels`). (d) `_coverage_violations` fails a 0-dimension block (`test_meta_ratchet_rejects_zero_dimension_block`).
- **R6 [LOW]** — GL-14 xfail docstring now notes the auto-fire also triggers on a dishonest `open_leaks: 0` (0==0) — acceptable (forces attention); the true clearing event stays "Q1.5 tags the 5 leaks".
- **R7 [LOW]** — dropped the brittle `[4,3,1,3,2]` insertion-order literal; the arithmetic pin is the `_arithmetic_violations` computation (robust to YAML key reorder) + a non-brittle `score==65 / band==B-` witness.
- **Documented residual** — added to the test-module docstring, `app/quality/history.py` docstring, AND doc §Cadence: the trend/history axis is a *judgment-history ledger*, not observed state; the pins enforce doc↔ledger mirror + mandatory append + evidence-gated increases but CANNOT mechanically detect a *coordinated* fabrication of both doc and ledger — a review/governance residual, stated plainly.

### File List

- `app/quality/history.py` — NEW. Trend-history substrate reader (GL-12): `history_entries`, `newest_snapshot`, `latest_prior_snapshot`, `trend_from_history` + `_valid_iso` date-hardening (R4: ISO-validate before compare, max-by-validated-date selection, file-index tie-break). Fail-soft, stdlib+json, clean leaf.
- `docs/quality/scorecard-history.jsonl` — NEW. Append-only JSONL history log; seeded 2026-07-19 DID baseline snapshot.
- `tests/quality/test_scorecard_honesty_pins.py` — NEW. The 3 honesty pins (a/b/c) + GL-6 meta-ratchet + GL-11 computed-trend & evidence-gated upgrade guard + R1 doc↔ledger mirror pin + R3 anti-de-mechanization pin + R4/R5 robustness tests + all AC5 RED-under-seeded-edit companion proofs. All block-level pins iterate every dimension (R2).
- `scripts/utilities/quality_scorecard.py` — MODIFIED (docstring only). `--check` documented as a SECONDARY staleness nag, not the honesty guard. No behavior change.
- `docs/quality/project-quality-scorecard.md` — MODIFIED (§Cadence prose only — two lines: `--check` demotion + the honest-residual ledger note). Machine block byte-identical.
